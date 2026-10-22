#!/usr/bin/env python3
"""
Pack Library banners for HSK 5 Core vols 2-4 and HSK 6 Core vols 2-8.

Until 2026-10-22 every volume of a level shared its vol-1 banner (byte-identical
copies), so the Library showed four identical HSK 5 cards and eight identical
HSK 6 ones. Vol 1 of each level keeps its image; each later volume gets its own
scene, climbing in sophistication with the volume like hsk4-foundations-1..3.

Banners are 1000x362 (the existing packbanners size): generated at 1536x560
(same ~2.75:1 ratio, multiples of 16) and resized down.

    python3 gen_hsk_banners.py                 # all ten
    python3 gen_hsk_banners.py hsk5-core-2 hsk6-core-2   # just these
"""
import os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images", "packbanners")
GEN = os.path.expanduser("~/.claude/scripts/imagegen/comfy_gen.py")

# Matches the existing banners: warm natural light, a single learner (or two)
# in a real Chinese setting. Any visible writing comes out as pseudo-hanzi, so
# pages, screens and signs are kept turned away or out of focus.
STYLE = (", photorealistic photograph, warm natural light, shallow depth of field, "
         "contemporary China, wide cinematic composition with the subject left of centre, "
         "no text, no readable writing, no logos")

SEED = 98000          # fresh block; story scenes used 96000+
SEED_OVERRIDES = {}   # slug -> seed, for one-off redos

SCENES = {
    # r2: the first take looked like the vol-1 woman (long hair, beige jumper)
    "hsk5-core-2": "a young Chinese woman with a short bob haircut and a denim jacket reading a thick novel on a cafe window seat, a glass cup of green tea beside her, autumn leaves and a city street softly blurred outside",
    "hsk5-core-3": "a young Chinese man at a wooden desk in the evening wearing over-ear headphones, listening intently, an open notebook and pen, warm desk lamp glow",
    "hsk5-core-4": "two Chinese friends in their twenties laughing in conversation at a traditional teahouse table, gaiwan tea cups and a clay teapot, carved wooden lattice windows",
    # r2: "seen from the side" still drew rows of pseudo-hanzi on the paper
    "hsk6-core-2": "a Chinese woman about to practise calligraphy, holding a brush poised just above a completely blank sheet of white rice paper, nothing written on it yet, ink stone and brush rest on a long wooden table",
    "hsk6-core-3": "a Chinese man reading a folded newspaper by the window of a high-speed train, green countryside and terraced hills streaking past outside",
    "hsk6-core-4": "a confident Chinese businesswoman presenting to colleagues in a modern glass meeting room, gesturing mid-sentence, the screen out of frame",
    "hsk6-core-5": "a Chinese university student surrounded by stacked books in a grand library reading room with tall arched windows and green desk lamps",
    "hsk6-core-6": "an elderly Chinese man and a young learner playing xiangqi Chinese chess on a stone table in a leafy park, round wooden pieces seen from a low angle",
    "hsk6-core-7": "a Chinese woman in a museum gallery studying an ancient bronze ding vessel in a softly lit glass case",
    "hsk6-core-8": "a young Chinese learner on a high balcony at golden hour holding a closed book, looking out over a sprawling Chinese city skyline with distant mountains",
}

def main(ids):
    for slug in ids:
        i = list(SCENES).index(slug)
        tmp = os.path.join(OUT, f".{slug}.png")
        dst = os.path.join(OUT, f"{slug}.jpg")
        seed = SEED_OVERRIDES.get(slug, SEED + 100 + i * 7)   # +100: r2 seeds
        if os.environ.get("SEED"): seed = int(os.environ["SEED"])
        subprocess.run([sys.executable, GEN, tmp, SCENES[slug] + STYLE, str(seed),
                        "--size", "1536x560"], check=True)
        Image.open(tmp).convert("RGB").resize((1000, 362), Image.LANCZOS).save(dst, quality=86)
        os.remove(tmp)
        print("wrote", dst)

if __name__ == "__main__":
    main(sys.argv[1:] or list(SCENES))
