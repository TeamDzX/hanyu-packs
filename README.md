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
