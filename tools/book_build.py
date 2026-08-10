#!/usr/bin/env python3
"""
Build clean, learner-oriented EPUBs for the Hanyu Library from public-domain
Chinese texts.

Why we re-typeset instead of rehosting source EPUBs
---------------------------------------------------
Project Gutenberg's Chinese "EPUB3" files are just the plain text wrapped in a
handful of XHTML pages -- there is no real chapter structure to inherit, and the
files carry PG's boilerplate and trademark. So we take the *public-domain text*
(which PG's own licence explicitly frees once its branding is stripped), remove
every trace of that boilerplate, convert scripts, split it into real chapters,
and package our own clean EPUB 3 with our own metadata.

Each book ships BOTH scripts (OEBPS/s/ = simplified, OEBPS/t/ = traditional) so
the reader's 简/繁 toggle is a directory swap rather than a lossy client-side
conversion. A non-standard OEBPS/hanyu.json carries the app's extra metadata
(chapter index, difficulty, tier, provenance); standard readers ignore it.

Usage
-----
    python3 tools/book_build.py                # build every book in the spec
    python3 tools/book_build.py luxun-nahan    # build one book by slug
    python3 tools/book_build.py --catalog      # rebuild books.json only
    python3 tools/book_build.py --qa           # build + print a QA report

Dependencies: opencc-python-reimplemented  (pip3 install --user it)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOOKS_DIR = os.path.join(ROOT, "books")
COVERS_DIR = os.path.join(ROOT, "images", "books")
CACHE_DIR = os.path.join(HERE, ".cache")
SPEC_PATH = os.path.join(HERE, "books_sources.json")
CATALOG_PATH = os.path.join(ROOT, "books.json")

RAW_BASE = "https://raw.githubusercontent.com/TeamDzX/hanyu-packs/main"
UA = {"User-Agent": "HanyuLibraryBuilder/1.0 (educational; public-domain texts)"}

# --------------------------------------------------------------------------
# Script conversion
# --------------------------------------------------------------------------

_cc = {}


def convert(text, config):
    """Convert between Chinese scripts via OpenCC ('t2s' or 's2t')."""
    if config not in _cc:
        import opencc
        _cc[config] = opencc.OpenCC(config)
    return _cc[config].convert(text)


# --------------------------------------------------------------------------
# Sourcing
# --------------------------------------------------------------------------

def _cached(name, fetch):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, name)
    if os.path.exists(path):
        return open(path, encoding="utf-8").read()
    data = fetch()
    open(path, "w", encoding="utf-8").write(data)
    time.sleep(1.0)          # be polite to the source
    return data


# Everything between these markers is the public-domain work itself; everything
# outside is Project Gutenberg's own licence text and branding, which we drop.
PG_START = re.compile(r"\*\*\*\s*START OF TH(?:E|IS) PROJECT GUTENBERG[^*]*\*\*\*")
PG_END = re.compile(r"\*\*\*\s*END OF TH(?:E|IS) PROJECT GUTENBERG[^*]*\*\*\*")


def fetch_gutenberg(book_id):
    def go():
        url = "https://www.gutenberg.org/ebooks/%d.txt.utf-8" % book_id
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=90) as f:
            return f.read().decode("utf-8", "replace")

    text = _cached("gutenberg-%d.txt" % book_id, go)
    start, end = PG_START.search(text), PG_END.search(text)
    if not (start and end):
        raise RuntimeError("Gutenberg #%d: boilerplate markers not found" % book_id)
    body = text[start.end():end.start()]

    # Belt and braces: refuse to ship anything still carrying PG branding.
    leftover = re.findall(r"(?i)project gutenberg|gutenberg-tm", body)
    if leftover:
        body = "\n".join(
            l for l in body.split("\n")
            if not re.search(r"(?i)project gutenberg|gutenberg-tm", l)
        )
    return body


def fetch_wikisource(title, host="zh.wikisource.org"):
    """Fetch a Wikisource page as wikitext-derived plain text."""
    def go():
        params = {"action": "parse", "page": title, "prop": "wikitext", "format": "json"}
        url = "https://%s/w/api.php?%s" % (host, urllib.parse.urlencode(params))
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as f:
            doc = json.load(f)
        return doc["parse"]["wikitext"]["*"]

    wt = _cached("wikisource-%s.txt" % re.sub(r"\W+", "_", title), go)
    return strip_wikitext(wt)


def strip_wikitext(wt):
    wt = re.sub(r"<ref[^>]*>.*?</ref>", "", wt, flags=re.S)
    wt = re.sub(r"<ref[^>]*/>", "", wt)
    wt = re.sub(r"\{\{[^{}]*\}\}", "", wt)
    wt = re.sub(r"\{\{[^{}]*\}\}", "", wt)          # nested templates, second pass
    wt = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]|]*)\]\]", r"\1", wt)
    wt = re.sub(r"</?[a-zA-Z][^>]*>", "", wt)
    wt = re.sub(r"^[*#:;]+\s*", "", wt, flags=re.M)
    wt = wt.replace("'''", "").replace("''", "")
    return wt


# --------------------------------------------------------------------------
# Chapter splitting
# --------------------------------------------------------------------------

TERMINAL = "。！？；：，、"


def _is_isolated(lines, i):
    prev_blank = i == 0 or not lines[i - 1].strip()
    next_blank = i + 1 >= len(lines) or not lines[i + 1].strip()
    return prev_blank and next_blank


def chunk_chapters(text, spec):
    """
    Fallback for texts with no structure of their own (some source editions are
    one continuous stream). Split into roughly equal reading sections on
    paragraph boundaries so the reader still has somewhere to stop.
    """
    target = spec.get("chunkChars", 6000)
    label = spec.get("chunkLabel", "第%s部分")
    paras = paragraphs(text)
    chapters, buf, size, n = [], [], 0, 0
    for p in paras:
        buf.append(p)
        size += len(p)
        if size >= target:
            n += 1
            chapters.append((label % _cn_num(n), "\n\n".join(buf)))
            buf, size = [], 0
    if buf:
        n += 1
        chapters.append((label % _cn_num(n), "\n\n".join(buf)))
    return chapters


_CN_DIGITS = "零一二三四五六七八九"


def _cn_num(n):
    """Small-integer Chinese numeral, enough for section labels."""
    if n < 10:
        return _CN_DIGITS[n]
    if n < 20:
        return "十" + (_CN_DIGITS[n % 10] if n % 10 else "")
    if n < 100:
        return _CN_DIGITS[n // 10] + "十" + (_CN_DIGITS[n % 10] if n % 10 else "")
    return str(n)


def split_chapters(text, spec):
    """Return [(title, body_text), ...] using the spec's chapter strategy."""
    lines = text.split("\n")
    stripped = [l.strip() for l in lines]
    mode = spec.get("chapterMode", "auto")

    if mode == "chunk":
        return chunk_chapters(text, spec)

    if mode == "regex":
        rx = re.compile(spec["chapterRegex"])
        marks = [i for i, l in enumerate(stripped) if l and rx.match(l)]
    elif mode == "flush":
        # Headings sit flush left while body lines are indented — the layout
        # several source editions use instead of blank-line separation.
        limit = spec.get("maxHeadingLen", 16)
        marks = [i for i, l in enumerate(stripped)
                 if l and len(l) <= limit and lines[i][:1] not in (" ", "\t", "　")]
    elif mode == "verse":
        # Poetry: verse lines have a fixed metre (5 or 7 characters plus its
        # punctuation), so anything else that follows one starts a new poem.
        lens = set(spec.get("verseLens", [6, 8]))

        def is_verse(l):
            return len(l) in lens and l[-1:] in "。，？！；"

        marks = []
        for i, l in enumerate(stripped):
            if not l or is_verse(l):
                continue
            if not marks or (stripped[i - 1] and is_verse(stripped[i - 1])):
                marks.append(i)
    elif mode == "titles":
        marks = []
        for title in spec["chapterTitles"]:
            names = title if isinstance(title, list) else [title]
            for name in names:
                exact = [i for i, l in enumerate(stripped) if l == name]
                # Prefer a blank-line-isolated heading, but some editions run
                # headings straight into the body with no blank lines at all —
                # there, a whole line equal to the title is signal enough.
                hit = [i for i in exact if _is_isolated(stripped, i)] or exact
                if hit:
                    marks.append(hit[0])
                    break
        marks.sort()          # source order, NOT the order listed in the spec
    else:
        marks = [
            i for i, l in enumerate(stripped)
            if l and len(l) <= 14
            and not any(c in l for c in TERMINAL)
            and _is_isolated(stripped, i)
        ]

    if not marks:
        return chunk_chapters(text, spec) if len(text) > 8000 else [(spec["title"], text)]

    chapters = []
    for n, start in enumerate(marks):
        end = marks[n + 1] if n + 1 < len(marks) else len(lines)
        title = stripped[start]
        body = "\n".join(lines[start + 1:end])
        if body.strip():
            chapters.append((title, body))
    return chapters


def paragraphs(body):
    """Collapse hard-wrapped source lines into real paragraphs."""
    out, buf = [], []
    for line in body.split("\n"):
        s = line.strip()
        if not s:
            if buf:
                out.append("".join(buf))
                buf = []
            continue
        indented = line[:1] in (" ", "\t", "　")
        if indented and buf:
            out.append("".join(buf))
            buf = []
        buf.append(s)
    if buf:
        out.append("".join(buf))
    return [p for p in out if p]


# --------------------------------------------------------------------------
# EPUB writing
# --------------------------------------------------------------------------

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


CSS = """\
body { font-family: "Songti SC", "Source Han Serif SC", serif; line-height: 1.9;
       margin: 1.2em; color: #1a1a1a; }
h1 { font-size: 1.35em; font-weight: 600; margin: 0 0 1.2em; text-align: center; }
p { margin: 0 0 0.95em; text-indent: 2em; }
"""


def chapter_xhtml(title, paras):
    body = "\n".join("  <p>%s</p>" % esc(p) for p in paras)
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh" lang="zh">\n'
            '<head><meta charset="utf-8"/><title>%s</title>'
            '<link rel="stylesheet" type="text/css" href="../style.css"/></head>\n'
            '<body>\n  <h1>%s</h1>\n%s\n</body>\n</html>\n'
            % (esc(title), esc(title), body))


def build_epub(spec, chapters_s, chapters_t, out_path, cover_bytes=None):
    """Write an EPUB 3 carrying both scripts plus our hanyu.json sidecar."""
    uid = "urn:hanyu:book:" + spec["slug"]
    today = date.today().isoformat()
    n = len(chapters_s)

    manifest, spine, nav_items = [], [], []
    manifest.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
    manifest.append('<item id="css" href="style.css" media-type="text/css"/>')
    manifest.append('<item id="hanyu" href="hanyu.json" media-type="application/json"/>')
    if cover_bytes:
        manifest.append('<item id="cover" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>')

    for i in range(n):
        cid = "c%03d" % (i + 1)
        manifest.append('<item id="s%s" href="s/%s.xhtml" media-type="application/xhtml+xml"/>' % (cid, cid))
        manifest.append('<item id="t%s" href="t/%s.xhtml" media-type="application/xhtml+xml"/>' % (cid, cid))
        spine.append('<itemref idref="s%s"/>' % cid)
        spine.append('<itemref idref="t%s" linear="no"/>' % cid)
        nav_items.append('    <li><a href="s/%s.xhtml">%s</a></li>' % (cid, esc(chapters_s[i][0])))

    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="zh">\n'
           '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
           '    <dc:identifier id="bookid">%s</dc:identifier>\n'
           '    <dc:title>%s</dc:title>\n'
           '    <dc:creator>%s</dc:creator>\n'
           '    <dc:language>zh-Hans</dc:language>\n'
           '    <dc:date>%s</dc:date>\n'
           '    <dc:rights>Public domain text. %s</dc:rights>\n'
           '    <dc:source>%s</dc:source>\n'
           '    <meta property="dcterms:modified">%sT00:00:00Z</meta>\n'
           '  </metadata>\n'
           '  <manifest>\n    %s\n  </manifest>\n'
           '  <spine>\n    %s\n  </spine>\n'
           '</package>\n'
           % (uid, esc(spec["title"]), esc(spec.get("author", "佚名")), today,
              esc(spec.get("pdBasis", "")), esc(spec.get("sourceNote", "")), today,
              "\n    ".join(manifest), "\n    ".join(spine)))

    nav = ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
           '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh">\n'
           '<head><meta charset="utf-8"/><title>%s</title></head>\n<body>\n'
           '<nav epub:type="toc" id="toc"><h1>目录</h1>\n  <ol>\n%s\n  </ol></nav>\n'
           '</body></html>\n' % (esc(spec["title"]), "\n".join(nav_items)))

    sidecar = {
        "slug": spec["slug"],
        "title": spec["title"],
        "titleTraditional": spec.get("titleTraditional", ""),
        "titlePinyin": spec.get("titlePinyin", ""),
        "titleEnglish": spec.get("titleEnglish", ""),
        "author": spec.get("author", ""),
        "authorPinyin": spec.get("authorPinyin", ""),
        "authorEnglish": spec.get("authorEnglish", ""),
        "era": spec.get("era", ""),
        "genre": spec.get("genre", ""),
        "tier": spec.get("tier", ""),
        "difficulty": spec.get("difficulty", 3),
        "classical": bool(spec.get("classical")),
        "free": bool(spec.get("free")),
        # Individual chapters readable without an unlock, as a taster inside an
        # otherwise premium book. Titles are matched after script conversion.
        "freeChapters": [convert(t, "t2s") for t in spec.get("freeChapters", [])],
        "blurb": spec.get("blurb", ""),
        "pdBasis": spec.get("pdBasis", ""),
        "sourceNote": spec.get("sourceNote", ""),
        "scripts": ["s", "t"],
        "chapters": [
            {"id": "c%03d" % (i + 1),
             "title": chapters_s[i][0],
             "titleTraditional": chapters_t[i][0],
             "chars": len("".join(chapters_s[i][1]))}
            for i in range(n)
        ],
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if os.path.exists(out_path):
        os.remove(out_path)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        # The mimetype entry must be first and STORED, per the EPUB spec.
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0" encoding="utf-8"?>\n'
                   '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                   '  <rootfiles><rootfile full-path="OEBPS/content.opf" '
                   'media-type="application/oebps-package+xml"/></rootfiles>\n</container>\n')
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/nav.xhtml", nav)
        z.writestr("OEBPS/style.css", CSS)
        z.writestr("OEBPS/hanyu.json", json.dumps(sidecar, ensure_ascii=False, indent=1))
        if cover_bytes:
            z.writestr("OEBPS/cover.jpg", cover_bytes)
        for i in range(n):
            cid = "c%03d" % (i + 1)
            z.writestr("OEBPS/s/%s.xhtml" % cid, chapter_xhtml(*chapters_s[i]))
            z.writestr("OEBPS/t/%s.xhtml" % cid, chapter_xhtml(*chapters_t[i]))
    return sidecar


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def load_source(spec):
    src = spec["source"]
    if src["type"] == "gutenberg":
        return fetch_gutenberg(src["id"])
    if src["type"] == "wikisource":
        return fetch_wikisource(src["page"])
    raise RuntimeError("unknown source type: %s" % src["type"])


def build_book(spec, qa=False):
    text = load_source(spec)
    if spec.get("trimBefore"):
        m = re.search(spec["trimBefore"], text)
        if m:
            text = text[m.start():]
    if spec.get("trimAfter"):
        m = re.search(spec["trimAfter"], text)
        if m:
            text = text[:m.start()]

    raw_chapters = split_chapters(text, spec)
    if spec.get("dropChapters"):
        drop = set(spec["dropChapters"])
        raw_chapters = [c for c in raw_chapters if c[0] not in drop]
    if spec.get("minChapterChars"):
        floor = spec["minChapterChars"]
        raw_chapters = [c for c in raw_chapters if len(c[1]) >= floor]

    # Normalise both scripts from whichever the source happens to be.
    chapters_s, chapters_t = [], []
    for title, body in raw_chapters:
        paras = paragraphs(body)
        s_title, s_paras = convert(title, "t2s"), [convert(p, "t2s") for p in paras]
        t_title, t_paras = convert(title, "s2t"), [convert(p, "s2t") for p in paras]
        chapters_s.append((s_title, s_paras))
        chapters_t.append((t_title, t_paras))

    cover_bytes = None
    cover_path = os.path.join(COVERS_DIR, spec["slug"] + ".jpg")
    if os.path.exists(cover_path):
        cover_bytes = open(cover_path, "rb").read()

    out = os.path.join(BOOKS_DIR, spec["slug"] + ".epub")
    sidecar = build_epub(spec, chapters_s, chapters_t, out, cover_bytes)

    size = os.path.getsize(out)
    total = sum(c["chars"] for c in sidecar["chapters"])
    if qa:
        lens = [c["chars"] for c in sidecar["chapters"]]
        print("  chapters=%d chars=%d min=%d max=%d median=%d"
              % (len(lens), total, min(lens), max(lens), sorted(lens)[len(lens) // 2]))
        expected = spec.get("expectChapters")
        if expected and len(lens) != expected:
            print("  !! expected %d chapters, produced %d" % (expected, len(lens)))
    return sidecar, out, size, total


def catalog_entry(spec, sidecar, size, total, epub_path):
    digest = hashlib.sha256(open(epub_path, "rb").read()).hexdigest()[:16]
    return {
        "bookId": spec["slug"],
        "revision": spec.get("revision", 1),
        "title": sidecar["title"],
        "titleTraditional": sidecar["titleTraditional"],
        "titlePinyin": sidecar["titlePinyin"],
        "titleEnglish": sidecar["titleEnglish"],
        "author": sidecar["author"],
        "authorPinyin": sidecar["authorPinyin"],
        "authorEnglish": sidecar["authorEnglish"],
        "era": sidecar["era"],
        "genre": sidecar["genre"],
        "tier": sidecar["tier"],
        "difficulty": sidecar["difficulty"],
        "classical": sidecar["classical"],
        "free": sidecar["free"],
        "freeChapters": sidecar.get("freeChapters", []),
        "blurb": sidecar["blurb"],
        "chapters": len(sidecar["chapters"]),
        "chars": total,
        "bytes": size,
        "sha256": digest,
        "minApp": spec.get("minApp", "3.2"),
        "cover": "%s/images/books/%s.jpg" % (RAW_BASE, spec["slug"]),
        "url": "%s/books/%s.epub" % (RAW_BASE, spec["slug"]),
        "pdBasis": sidecar["pdBasis"],
        "sourceNote": sidecar["sourceNote"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*", help="build only these slugs")
    ap.add_argument("--catalog", action="store_true", help="rebuild books.json from existing epubs")
    ap.add_argument("--qa", action="store_true", help="print a per-book QA report")
    args = ap.parse_args()

    specs = json.load(open(SPEC_PATH, encoding="utf-8"))["books"]
    if args.slugs:
        specs = [s for s in specs if s["slug"] in args.slugs]
        if not specs:
            sys.exit("no matching slugs")

    entries, failures = [], []
    for spec in specs:
        print("· %s (%s)" % (spec["slug"], spec["title"]))
        try:
            sidecar, path, size, total = build_book(spec, qa=args.qa)
            entries.append(catalog_entry(spec, sidecar, size, total, path))
            print("  → %s  %.0f KB  %d chapters" % (os.path.basename(path), size / 1024.0,
                                                    len(sidecar["chapters"])))
        except Exception as exc:                       # noqa: BLE001 - report and carry on
            failures.append((spec["slug"], str(exc)))
            print("  !! FAILED: %s" % exc)

    if entries and not args.slugs:
        catalog = {"catalogRevision": 1, "generated": date.today().isoformat(), "books": entries}
        json.dump(catalog, open(CATALOG_PATH, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("\nWrote %s with %d books." % (os.path.basename(CATALOG_PATH), len(entries)))

    if failures:
        print("\n%d book(s) failed:" % len(failures))
        for slug, err in failures:
            print("  %s: %s" % (slug, err))
        sys.exit(1)


if __name__ == "__main__":
    main()
