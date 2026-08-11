#!/usr/bin/env python3
"""
Generate cover art for the Hanyu Library books.

Art direction: one cohesive set — classical Chinese ink-wash / literati painting,
portrait book-cover composition, tuned per book's era and mood. Deliberately NO
text in the generated image: Flux garbles hanzi, so titles are overlaid as real
glyphs in the app and on the landing page.

Runs with cooldowns between images and skips anything already on disk, because
long unbroken batches have crashed this server before.

    python3 tools/gen_book_covers.py            # only missing covers
    python3 tools/gen_book_covers.py --force    # regenerate everything
    python3 tools/gen_book_covers.py daodejing  # just these slugs
"""

import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "images", "books")
GEN = os.path.expanduser("~/.claude/scripts/imagegen/comfy_gen.py")

STYLE = ("classical Chinese ink wash painting, literati brushwork, subtle paper "
         "texture, muted natural pigments, portrait book cover composition, "
         "elegant negative space, no text, no letters, no writing, no signature")

COVERS = [
    ("luxun-nahan", 101,
     "a lone figure in a long scholar's gown crossing a stone bridge in a 1920s "
     "Chinese river town at dusk, shuttered shopfronts, overcast sky, quiet unease"),
    ("luxun-zhaohua", 102,
     "an old Chinese garden courtyard at early morning, plum blossom branches over "
     "a weathered whitewashed wall, moss on flagstones, warm nostalgic light"),
    ("yudafu-chenlun", 103,
     "a solitary young man standing on a misty coastal cliff at twilight, wind in his "
     "coat, cold grey-blue sea below, deep melancholy"),
    ("zhuziqing-ouyou", 104,
     "a 1930s European city street seen by a traveller, cobblestones wet with rain, "
     "distant cathedral spire, soft muted watercolour, gentle vintage travel mood"),
    ("tangshi-sanbai", 105,
     "a moonlit Tang dynasty mountain landscape, twisted pines on a cliff, a distant "
     "pagoda above cloud, full moon, faint gold accents, serene and classical"),
    ("shijing", 106,
     "an ancient Zhou dynasty countryside, millet fields and river reeds, herons rising, "
     "bronze age China, archaic and pastoral"),
    ("libai-ji", 107,
     "a Tang dynasty poet raising a wine cup to the full moon beside a river, flowing "
     "robes, drifting clouds, romantic and expansive"),
    ("lunyu", 108,
     "an ancient Chinese teacher seated beneath a spreading apricot tree instructing "
     "seated disciples, calm dignity, early morning light"),
    ("daodejing", 109,
     "a misty mountain valley with a winding stream vanishing into cloud, a single "
     "gnarled pine, vast emptiness, profound stillness, minimal composition"),
    ("sunzi-bingfa", 110,
     "ancient Chinese army banners on a misty ridge at dawn, silhouetted spears, "
     "distant fortified pass, cold disciplined atmosphere"),
    ("mengzi", 111,
     "a Warring States philosopher in spirited debate before a seated lord in an "
     "ancient hall, bronze vessels, oil lamps, animated gestures"),
    ("liaozhai", 112,
     "a moonlit abandoned temple courtyard, a fox silhouette on a broken wall, drifting "
     "mist through bare branches, eerie and beautiful, ghostly pale palette"),
    ("guwen-guanzhi", 113,
     "a scholar's desk by candlelight with stacked bamboo scrolls, an inkstone and a "
     "resting brush, quiet study at night"),
    ("sanzijing", 114,
     "children seated at low desks reciting in an old Chinese village schoolroom, "
     "wooden beams, morning light through paper windows, warm and simple"),

    # v3.3 — the philosophers and poets who already have a card in the culture
    # sections. Each cover leans on that figure's best-known image so the book
    # and the card read as the same subject.
    ("zhuangzi", 115,
     "a sleeping philosopher beneath a gourd vine with a single large butterfly "
     "drifting above him, a giant fish becoming a bird in the clouds beyond, "
     "dreamlike and playful, soft dawn colours"),
    ("mozi", 116,
     "ancient Chinese artisans and defenders on a city wall at dusk raising a "
     "wooden siege-defence engine, rope and timber, plain workmen's dress, "
     "practical and unheroic, working light"),
    ("hanfeizi", 117,
     "an austere Qin dynasty hall of state, a bronze measuring vessel and stacked "
     "legal bamboo slips on a stone dais, long cold shadows, severe symmetry, "
     "no people, disciplined and forbidding"),
    # Seeds re-rolled off 118/119: both landed a hanging scroll or plaque in
    # frame and Flux fills those with garbled pseudo-hanzi, which is the one
    # thing a Chinese-learning app cannot ship. Prompts now keep every
    # writing surface out of shot rather than relying on "no text" alone.
    ("xiaojing", 218,
     "a grown son kneeling to offer a bowl of tea to his elderly parents in a bare "
     "ancient Chinese room, plain undecorated walls, a single oil lamp, warm "
     "lamplight, tender and reverent, no scrolls, no plaques, no banners"),
    ("daxue-zhongyong", 219,
     "a scholar's low table by a moonlit lattice window with an inkstone, a resting "
     "brush and a stack of blank bamboo slips, plain undecorated walls, still and "
     "balanced composition, no scrolls, no plaques, no banners, no open book"),
    ("shiji", 120,
     "a Han dynasty historian writing by lamplight surrounded by towering stacks of "
     "bamboo scrolls, a barred window behind him, resolve in the face of disgrace, "
     "deep shadows, monumental"),
    ("dufu-shiji", 121,
     "a careworn Tang poet in a wind-torn thatched cottage above an autumn river, "
     "bare trees, distant war smoke on the horizon, grey and moving, compassionate "
     "melancholy"),
    ("chuci", 122,
     "a robed southern poet wandering a misty river marsh at dusk among orchids and "
     "reeds, shamanic banners and dragon motifs half-seen in the fog, strange and "
     "otherworldly, deep indigo and jade"),
    ("gushi-shijiu", 123,
     "a Han dynasty traveller looking back along an empty road under a bright moon, "
     "wild grass, distant city wall, plain and spare composition, ache of separation"),
    ("shuyuci", 124,
     "a Song dynasty woman poet alone at a window with a wine cup, plum blossom "
     "branches outside, scattered books and a scroll behind her, refined and "
     "sorrowful, delicate palette"),
]

COOLDOWN = 12          # seconds between images — this server dislikes long unbroken runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    jobs = [c for c in COVERS if not args.slugs or c[0] in args.slugs]

    done, skipped, failed = 0, 0, []
    for i, (slug, seed, subject) in enumerate(jobs, 1):
        out = os.path.join(OUT_DIR, slug + ".jpg")
        if os.path.exists(out) and not args.force:
            print("[%2d/%d] %-18s already present, skipping" % (i, len(jobs), slug))
            skipped += 1
            continue

        prompt = "%s, %s" % (subject, STYLE)
        print("[%2d/%d] %-18s generating..." % (i, len(jobs), slug), flush=True)
        cmd = [sys.executable, GEN, out, prompt, str(seed), "--size", "768x1152", "--max", "900"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=420)
            if res.returncode != 0 or not os.path.exists(out):
                failed.append((slug, (res.stderr or res.stdout or "").strip()[-200:]))
                print("        FAILED")
            else:
                done += 1
                print("        ok  %.0f KB" % (os.path.getsize(out) / 1024.0))
        except subprocess.TimeoutExpired:
            failed.append((slug, "timed out"))
            print("        TIMED OUT")

        if i < len(jobs):
            time.sleep(COOLDOWN)

    print("\ngenerated=%d skipped=%d failed=%d" % (done, skipped, len(failed)))
    for slug, err in failed:
        print("  %s: %s" % (slug, err))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
