# Hanyu Content Packs

Free, over-the-air content packs for the **Hanyu** iOS app. Each pack is pure
data (characters, compound words, sentences, bespoke lessons) that the app
merges into its built-in content — **no App Store submission required.**

## How it's structured

```
packs/<slug>.json   ← edit these (one file per pack, easy to read)
packs.json          ← the MONOLITHIC catalog the app downloads (built from the above)
build.sh            ← regenerates packs.json from packs/*.json
radio.json          ← standalone: live radio stations (app v2.9+)
creators.json       ← standalone: "Creators to Follow" directory (app v3.0+ ONLY)
books.json          ← standalone: the Library catalog (app v3.2+ ONLY)
books/*.epub        ← the books themselves, built by tools/book_build.py
tools/books_sources.json  ← the source spec every book is built from
```

**Standalone catalogs** (`radio.json`, `creators.json`) are NOT built into
`packs.json` — each is fetched directly by the feature that uses it, and only by
app versions that have that feature. `creators.json` is consumed **only by
v3.0+** (the Creators to Follow directory); older versions, including v2.9.x,
have no code path that requests it, so pushing it is inert for them. Both are
bare JSON arrays, refreshed at runtime with strict UTF-8 validation.

The app downloads **`packs.json`** (a single file: `{ catalogRevision, packs: [...] }`),
finds the pack it needs by `packId`, checks its `revision`, and installs it.
Because the app fetches natively (not in a browser), CORS and host quirks don't
apply — `packs.json` can be served from GitHub raw, GitHub Pages, or mirrored to
the Wix site.

## Publishing an update

1. Edit a file in `packs/` (add entries to `content`, update `whatsNew`).
2. **Bump that pack's `revision`** (integer). The app only installs packs whose
   remote `revision` is higher than what the user already has.
3. Run `./build.sh` to regenerate `packs.json`.
4. Commit and push. Done — users get it next time they check for packs.

## Pack schema

| field | notes |
|---|---|
| `revision` | integer; bump on every change |
| `packId` | stable slug; **must match the file name and the landing-page card slug** |
| `name`, `icon`, `releaseDate`, `whatsNew` | shown in the in-app Packs tab |
| `minApp` | minimum app version that may install this pack |
| `content.characters` | `{ character, pinyin, meaning, strokes, hsk }` |
| `content.compoundWords` | `{ char1, char2, compound, pinyin, meaning, hint }` |
| `content.sentencesDatabase` | `{ chinese: [...], pinyin, english, difficulty }` |
| `content.bespokeLessons` | `{ id, title, titleChinese, titlePinyin, icon, color, colorEnd, level, difficulty, vocabulary: [{char, pinyin, meaning}] }` |

Content must stay **data only** (Apple App Store Review Guideline 2.5.2).

## The Library (`books.json`)

Books are built from `tools/books_sources.json` — never edited by hand:

```
python3 tools/book_build.py            # build every book + rewrite books.json
python3 tools/book_build.py zhuangzi   # just one (does NOT rewrite books.json)
python3 tools/book_validate.py         # structural check on every epub
python3 tools/gen_book_covers.py       # cover art for anything missing one
```

Sources are Project Gutenberg (`{"type":"gutenberg","id":N}`, or `"ids":[N,M]` to
assemble one book from several volumes) or Wikisource. Wikisource works spread
over many pages use `wikisource-multi`, which fetches each page's **rendered
HTML** rather than its wikitext — collections transclude their content and verse
sits in `<poem>` blocks, so wikitext comes back nearly empty. Give it either an
explicit ordered `pages` list, or `indexPage` + `prefix` to take the order from
the index and the set from the subpages that actually exist.

Chapter splitting has one mode per shape of source: `regex`, `titles`, `flush`,
`verse`, `separator` (a divider line, title on the next line), `chunk`, `auto`.
`stripLines`, `substitutions` and `titleSub` clean up editorial apparatus —
several editions interleave concordance numbering or inline variant readings
(`一作「X」`) that are noise to a learner.

### Cross-links (`links`)

A book can name the culture-section cards it belongs with, and the app wires
both directions from it — chips on the book's detail sheet, and a "Read … in the
Library" button on the matching card. Catalog-driven, so a new book arrives
already connected with no app update:

```json
"links": [
  { "type": "figure",     "id": "fig-confucius",     "label": "Confucius" },
  { "type": "philosophy", "id": "phil-taoism",       "label": "Taoism" },
  { "type": "dynasty",    "id": "tang",              "label": "Tang Dynasty" },
  { "type": "lesson",     "id": "fest-dragonboat",   "label": "Dragon Boat Festival" },
  { "type": "story",      "id": "tp_jingyesi",       "label": "静夜思" },
  { "type": "section",    "id": "history",           "label": "History" }
]
```

`figure`/`philosophy`/`dynasty` are always present (bundled into the History
section, or added by a content pack). `lesson`/`story`/`section` targets may not
exist for a given user — the app hides those chips rather than showing one that
goes nowhere, so it is safe to reference pack content.

The IDs are whatever the card carries as `data-hist-id` in the app, which for
pack-supplied cards is the entry's own `id` in `content.history`.
