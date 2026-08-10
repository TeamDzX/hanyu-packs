#!/usr/bin/env python3
"""
Structural validation for the Hanyu Library EPUBs.

Checks the things that would actually break a reader (ours or a third party's):
mimetype placement, container/OPF wiring, every manifest href resolving, both
script directories present and complete, well-formed XHTML, and — because these
are re-typeset public-domain texts — that no source-provider branding survived.

    python3 tools/book_validate.py
"""

import json
import os
import re
import sys
import zipfile
from xml.etree import ElementTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_DIR = os.path.join(ROOT, "books")
CATALOG = os.path.join(ROOT, "books.json")

BRANDING = re.compile(r"(?i)project gutenberg|gutenberg-tm|www\.gutenberg")


def validate(path):
    errors, warnings = [], []
    z = zipfile.ZipFile(path)
    names = z.namelist()

    # 1. mimetype must be the first entry, stored uncompressed.
    if names[0] != "mimetype":
        errors.append("mimetype is not the first zip entry")
    else:
        info = z.getinfo("mimetype")
        if info.compress_type != zipfile.ZIP_STORED:
            errors.append("mimetype is compressed (must be stored)")
        if z.read("mimetype") != b"application/epub+zip":
            errors.append("mimetype content is wrong")

    # 2. container.xml -> OPF
    if "META-INF/container.xml" not in names:
        errors.append("missing META-INF/container.xml")
        return errors, warnings
    container = ElementTree.fromstring(z.read("META-INF/container.xml"))
    rootfile = container.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
    opf_path = rootfile.get("full-path")
    if opf_path not in names:
        errors.append("OPF referenced by container.xml is missing: %s" % opf_path)
        return errors, warnings

    # 3. OPF manifest + spine
    opf = ElementTree.fromstring(z.read(opf_path))
    ns = {"opf": "http://www.idpf.org/2007/opf"}
    base = os.path.dirname(opf_path)
    manifest = {}
    for item in opf.findall(".//opf:manifest/opf:item", ns):
        manifest[item.get("id")] = item.get("href")
        target = os.path.normpath(os.path.join(base, item.get("href")))
        if target not in names:
            errors.append("manifest item not in archive: %s" % item.get("href"))

    spine = [ref.get("idref") for ref in opf.findall(".//opf:spine/opf:itemref", ns)]
    if not spine:
        errors.append("empty spine")
    for idref in spine:
        if idref not in manifest:
            errors.append("spine references unknown id: %s" % idref)

    # 4. Both script variants must be complete and matched.
    s_ch = sorted(n for n in names if n.endswith(".xhtml") and "/s/" in n)
    t_ch = sorted(n for n in names if n.endswith(".xhtml") and "/t/" in n)
    if not s_ch:
        errors.append("no simplified chapters")
    if len(s_ch) != len(t_ch):
        errors.append("script mismatch: %d simplified vs %d traditional" % (len(s_ch), len(t_ch)))

    # 5. Sidecar metadata agrees with what is actually in the archive.
    side_path = os.path.join(base, "hanyu.json").replace("\\", "/")
    if side_path not in names:
        errors.append("missing hanyu.json sidecar")
    else:
        side = json.loads(z.read(side_path))
        if len(side["chapters"]) != len(s_ch):
            errors.append("sidecar lists %d chapters, archive has %d"
                          % (len(side["chapters"]), len(s_ch)))
        if not side.get("pdBasis"):
            warnings.append("sidecar has no pdBasis recorded")

    # 6. Every XHTML page must parse, and carry no source-provider branding.
    empty = 0
    for name in s_ch + t_ch:
        raw = z.read(name)
        try:
            ElementTree.fromstring(raw)
        except ElementTree.ParseError as exc:
            errors.append("XHTML does not parse: %s (%s)" % (name, exc))
            continue
        text = raw.decode("utf-8", "replace")
        if BRANDING.search(text):
            errors.append("source branding survived into %s" % name)
        if len(re.findall(r"<p>", text)) == 0:
            empty += 1
    if empty:
        warnings.append("%d chapter page(s) have no paragraphs" % empty)

    return errors, warnings


def main():
    catalog = json.load(open(CATALOG, encoding="utf-8"))
    total_err = 0
    print("Validating %d books\n" % len(catalog["books"]))
    for entry in catalog["books"]:
        path = os.path.join(BOOKS_DIR, entry["bookId"] + ".epub")
        if not os.path.exists(path):
            print("✗ %-18s MISSING FILE" % entry["bookId"])
            total_err += 1
            continue
        errors, warnings = validate(path)
        total_err += len(errors)
        mark = "✓" if not errors else "✗"
        print("%s %-18s %3d ch  %6.0f KB  %s"
              % (mark, entry["bookId"], entry["chapters"], entry["bytes"] / 1024.0,
                 "ok" if not errors else "%d ERROR(S)" % len(errors)))
        for e in errors:
            print("      ERROR: %s" % e)
        for w in warnings:
            print("      warn:  %s" % w)

    print("\n%s" % ("All books valid." if not total_err else "%d error(s) found." % total_err))
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
