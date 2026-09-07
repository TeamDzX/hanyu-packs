#!/usr/bin/env python3
"""Generate every image for the Chinese Medicine & Acupuncture pack.

  images/flashcards/<deck>/<idx>.jpg   640x640 card photos (card 0 doubles as the
                                       deck cover, cropped 'center 20%' by the
                                       app — so card 0 is a wide scene with its
                                       subject in the upper middle and NO sky)
  images/pack_tcm_story_<id>.jpg       760x520 story cards

Lessons carried over from the earlier packs: living things and people need a
real, softly blurred background (the plain-studio look turns them into
specimens or mannequins); shapes Flux confuses get PHYSICAL descriptions —
"acupuncture needles" alone drifts into syringes, so every needle prompt says
"hair-thin, filiform, with a coiled metal handle". Hanzi never go in an image:
Flux garbles them, and the card shows the characters as text anyway.

    python3 gen_chinese_medicine.py                 # everything
    python3 gen_chinese_medicine.py tcm-herbs       # one deck, or 'stories'
    python3 gen_chinese_medicine.py covers          # just the three deck covers
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/.claude/scripts/imagegen"))
from comfy_gen import generate

# Inanimate objects: herbs, jars, needles, cups.
CARD_STYLE = (", clean modern photograph, single subject centered, soft plain "
              "studio background, bright even lighting, shallow depth of field, "
              "crisp and colourful, no text, no letters, no writing, no watermark")

# Hands, bodies, faces: needs a real room behind them.
PEOPLE_STYLE = (", photorealistic photograph, natural soft window light, "
                "calm modern clinic interior softly blurred behind, shallow "
                "depth of field, warm and reassuring, no text, no letters, "
                "no writing, no watermark")

# Wide establishing shots (clinic, pharmacy drawers, tai chi in a park).
SCENE_STYLE = (", clean modern photograph, real location, natural daylight, "
               "sharp focus, wide establishing view, no text, no letters, "
               "no writing, no watermark")

STYLES = {"object": CARD_STYLE, "people": PEOPLE_STYLE, "scene": SCENE_STYLE}

# Story cards leave the left third clear for the title overlay.
STORY_STYLE = (", photorealistic photograph, natural realistic lighting, shallow "
               "depth of field, candid documentary style, contemporary China, "
               "main subject placed on the RIGHT side of the frame, simple "
               "uncluttered out-of-focus space on the LEFT third, "
               "no text, no letters, no writing, no watermark")

NEEDLE = ("hair-thin filiform acupuncture needles, each with a tightly coiled "
          "silver metal handle, no syringe, no plastic")

DECKS = {
 "tcm-foundations": [
   # 0 中医 — cover: consulting room packed into the upper middle, no sky.
   ("the interior of a traditional Chinese medicine consulting room seen from "
    "the doorway, a wooden desk with a small pulse cushion, a wall of small "
    "wooden herb drawers behind, a doctor in a white coat seated in the upper "
    "middle of the frame, warm lamplight, the room filling the frame edge to "
    "edge, no windows, no sky", "scene"),
   # 1 气 — energy, abstract but photographic
   ("soft golden light and gentle wisps of warm mist flowing in a slow spiral "
    "over dark water at dawn, calm and luminous, abstract and serene", "scene"),
   # 2 阴阳
   ("a smooth round stone carved with a taijitu yin-yang symbol, one half "
    "polished black and one half polished white with a small dot of the "
    "opposite colour in each, resting on raked pale sand", "object"),
   # 3 五行
   ("five small natural objects arranged in a circle on dark slate: a green "
    "sprig of wood, a lit candle flame, a mound of yellow earth, a polished "
    "metal ingot and a shallow bowl of clear water, seen from above", "object"),
   # 4 经络
   ("a classic bronze acupuncture teaching figure, a standing human statue "
    "with fine engraved lines running along its arms and legs and tiny holes "
    "marking points, on a wooden stand", "object"),
   # 5 穴位
   ("close up of a practitioner's fingertip pressing a precise point on the "
    "back of a patient's hand between thumb and forefinger, soft light", "people"),
   # 6 把脉
   ("close up of a doctor's three fingers resting lightly on a patient's wrist "
    "on a small silk cushion on a wooden desk, taking the pulse", "people"),
   # 7 舌头
   ("a young adult with mouth open showing their tongue to a doctor who holds "
    "a small light, side view, neutral expression, clinic setting", "people"),
   # 8 上火
   ("a person's hand holding a glass of iced chrysanthemum tea next to a plate "
    "of red chillies and fried food pushed away, a cooling gesture, warm "
    "kitchen light", "object"),
   # 9 养生
   ("a serene older Chinese man in loose clothing practising slow tai chi in a "
    "misty park at sunrise, arms extended, trees behind", "scene"),
   # 10 中医师
   ("a friendly middle-aged Chinese doctor in a white coat seated at a wooden "
    "desk with a wall of herb drawers behind, hands folded, smiling", "people"),
   # 11 体质
   ("a doctor showing a patient a simple chart of body-type icons on a tablet "
    "in a consulting room, both looking at the screen, no readable text", "people"),
 ],
 "tcm-treatments": [
   # 0 针灸 — cover: back with needles filling the frame, no sky.
   ("a person lying face down on a treatment couch seen from above, several "
    + NEEDLE + " placed neatly along their upper back, a practitioner's hands "
    "at the edge of the frame, the couch and back filling the frame edge to "
    "edge, soft warm light", "people"),
   # 1 针
   ("a neat row of " + NEEDLE + " laid on a folded white cloth, extreme close "
    "up, the coiled handles catching the light", "object"),
   # 2 扎针
   ("close up of a practitioner's fingers holding one " + NEEDLE + " upright "
    "and placing it into the skin of a forearm resting on a towel", "people"),
   # 3 艾灸
   ("a smouldering moxa stick, a rolled cigar-shaped stick of dried mugwort "
    "glowing orange at its tip with a thin wisp of smoke, held a few "
    "centimetres above the skin of a person's lower back", "people"),
   # 4 拔罐
   ("a person's bare back with six round glass suction cups attached in two "
    "rows, the skin inside each cup drawn up and reddened, treatment room", "people"),
   # 5 刮痧
   ("a smooth flat pale jade scraping tool being drawn along a person's oiled "
    "shoulder by a practitioner's hand, close up", "people"),
   # 6 推拿
   ("a practitioner in a white uniform pressing both thumbs firmly into a "
    "patient's upper back, the patient lying face down on a treatment couch", "people"),
   # 7 按摩
   ("hands kneading a person's neck and shoulders, the person seated with "
    "eyes closed and relaxed, soft spa lighting", "people"),
   # 8 太极
   ("a group of people in loose white clothing practising tai chi together in "
    "a park in the early morning, arms raised in the same slow pose", "scene"),
   # 9 气功
   ("a person standing alone on a hilltop at dawn with feet apart and palms "
    "facing each other in front of the chest, eyes closed, breathing calmly", "scene"),
   # 10 药方 — first take wrote pseudo-Latin scribbles across the page. Hide
   # the writing under the hand and let the red seal and herb packets carry it.
   ("a Chinese doctor's hand holding a calligraphy brush, writing on a sheet "
    "of cream paper that is mostly covered by the hand and sleeve, a red "
    "square seal stamp in the corner, three small folded paper packets of "
    "dried herbs beside the page, seen from directly above, no visible "
    "writing", "object"),
   # 11 中药房
   ("the counter of a traditional Chinese pharmacy, a wall of hundreds of "
    "small wooden drawers with brass handles behind, a brass hand scale and "
    "paper packets on the counter, warm light", "scene"),
 ],
 "tcm-herbs": [
   # 0 中药 — cover: the drawers and herb piles fill the frame, no sky.
   ("a traditional Chinese pharmacy seen from the counter, a wall of small "
    "wooden herb drawers filling the whole frame edge to edge, open paper "
    "packets of dried roots, dried flowers and red berries heaped on the "
    "counter in the upper middle of the frame, a brass hand scale, warm "
    "lamplight, no windows", "scene"),
   # 1 草药
   ("an assortment of dried medicinal herbs in small shallow bamboo trays: "
    "dried roots, bark slices, seeds and dried flowers, seen from above", "object"),
   # 2 人参
   ("a whole dried ginseng root with a thick pale body and long forked "
    "branching rootlets shaped like a tiny human figure, on dark wood", "object"),
   # 3 枸杞
   ("a heap of bright red dried goji berries, small oval wrinkled berries "
    "spilling from a small glass jar, close up", "object"),
   # 4 当归
   ("slices of dried dang gui angelica root, pale cream rounds with a "
    "brownish rim and a fibrous texture, fanned out on a wooden board", "object"),
   # 5 菊花茶
   ("a clear glass teapot of pale golden chrysanthemum tea with whole white "
    "and yellow dried chrysanthemum flowers floating and unfurling in it, "
    "steam rising", "object"),
   # 6 生姜
   ("a knobbly fresh ginger root with pale golden skin, one end sliced to "
    "show the yellow fibrous flesh, on a wooden board", "object"),
   # 7 红枣
   ("a bowl of dried red dates, glossy wrinkled dark red jujubes, a few "
    "spilled beside the bowl, close up", "object"),
   # 8 甘草
   ("thin diagonal slices of dried liquorice root, pale yellow with a "
    "fibrous grain and a thin brown bark edge, on cream linen", "object"),
   # 9 凉茶
   ("a traditional Cantonese herbal tea shop counter with several large "
    "brass and copper urns, a small bowl of dark herbal tea being poured, "
    "warm evening light", "scene"),
   # 10 汤药
   ("a dark clay pot of simmering herbal decoction on a gas ring, dark brown "
    "liquid, dried herbs visible in the pot, steam rising, a ladle beside", "object"),
   # 11 药膳
   ("a steaming clay bowl of clear chicken soup with red dates, goji berries "
    "and a slice of ginseng floating in it, chopsticks and a ceramic spoon", "object"),
 ],
}

STORIES = {
 "pack_tcm_story_pulse":       ("a teenage boy seated at a wooden desk in a Chinese medicine clinic, his wrist "
                                "on a small cushion while an older doctor in a white coat takes his pulse, "
                                "the boy's mother standing beside him, warm lamplight, herb drawers behind"),
 "pack_tcm_story_acupuncture": ("a middle-aged Chinese man lying face down on a treatment couch, relaxed, with "
                                + NEEDLE + " placed along his lower back, a practitioner holding a smouldering "
                                "moxa stick above the skin, calm clinic room"),
 "pack_tcm_story_liangcha":    ("a smiling Chinese grandmother in a bright kitchen ladling dark herbal tea from a "
                                "clay pot into a bowl for a teenage grandchild who is pulling a face at the "
                                "bitter taste, dried chrysanthemum flowers and herbs on the table"),
}

SEED = 94000          # fresh block; prepare-for-china used 93000+
SEED_OVERRIDES = {"tcm-treatments/10": 94777}   # redo: pseudo-Latin scribbles on the first take
here = os.path.dirname(os.path.abspath(__file__))


def run(label, out, prompt, seed, w, h, mx):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        print(f"  skip {label} (exists)", flush=True)
        return True
    t0 = time.time()
    try:
        generate(out, prompt, seed, w, h, max_px=mx)
        print(f"  OK   {label} ({int(time.time() - t0)}s)", flush=True)
        return True
    except Exception as e:
        print(f"  FAIL {label}: {e}", flush=True)
        return False


def main():
    want = sys.argv[1:] or list(DECKS) + ["stories"]
    covers_only = want == ["covers"]
    jobs = []
    n = 0
    for deck, prompts in DECKS.items():
        for i, p in enumerate(prompts):
            prompt, style = p if isinstance(p, tuple) else (p, "object")
            label = f"{deck}/{i}"
            if deck in want or (covers_only and i == 0):
                jobs.append((label,
                             os.path.join(here, "images", "flashcards", deck, f"{i}.jpg"),
                             prompt + STYLES[style],
                             SEED_OVERRIDES.get(label, SEED + n * 13), 1024, 1024, 640))
            n += 1
    for sid, p in STORIES.items():
        if "stories" in want:
            jobs.append((sid, os.path.join(here, "images", sid + ".jpg"),
                         p + STORY_STYLE, SEED + n * 13, 1216, 832, 760))
        n += 1

    print(f"Generating {len(jobs)} images…", flush=True)
    ok = 0
    fail = []
    for i, (label, out, prompt, seed, w, h, mx) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}]", flush=True)
        if run(label, out, prompt, seed, w, h, mx):
            ok += 1
        else:
            fail.append(label)
    print(f"\nDONE: {ok} ok, {len(fail)} failed: {fail}", flush=True)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
