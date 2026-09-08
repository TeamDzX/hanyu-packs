#!/usr/bin/env python3
"""Generate every image for the Chinese Medicine & Acupuncture pack.

  images/flashcards/<deck>/<idx>.jpg   640x640 card photos (card 0 doubles as the
                                       deck cover, cropped 'center 20%' by the
                                       app — so card 0 is a wide scene with its
                                       subject in the upper middle and NO sky)
  images/pack_tcm_story_<id>.jpg       760x520 story cards
  images/pack_tcm_story_<id>_s<n>.jpg  760x520 per-sentence scenes; the reader
                                       derives the name from the cover, so the
                                       file existing is the whole wiring

Lessons carried over from the earlier packs: living things and people need a
real, softly blurred background (the plain-studio look turns them into
specimens or mannequins); shapes Flux confuses get PHYSICAL descriptions —
"acupuncture needles" alone drifts into syringes, so every needle prompt says
"hair-thin, filiform, with a coiled metal handle". Hanzi never go in an image:
Flux garbles them, and the card shows the characters as text anyway.

    python3 gen_chinese_medicine.py                 # everything
    python3 gen_chinese_medicine.py tcm-herbs       # one deck, or 'stories'
    python3 gen_chinese_medicine.py covers          # just the three deck covers
    python3 gen_chinese_medicine.py scenes          # just the per-sentence scenes
    python3 gen_chinese_medicine.py --force tcm-treatments/4 tcm-treatments/7
                                                   # redo two cards by label

Existing files are skipped, so a changed prompt or seed needs --force (or the
old file deleted) before it takes effect.
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

# Per-sentence scenes fill the reader's hero header, which is cropped
# centre/cover, so they stay centred - unlike the story CARD below.
SCENE_IMG_STYLE = (", photorealistic photograph, natural realistic lighting, "
                   "shallow depth of field, candid documentary style, "
                   "contemporary China, subject centred in the frame, "
                   "no text, no letters, no writing, no watermark")

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
   # 4 拔罐 — take 1 was gruesome (bruised, bloodshot rings); take 2 fixed the
   # skin but drew the cups as shallow glass LIDS lying on the back, so the
   # card no longer read as cupping (Alex, 7 Sep). Flux needs the cup described
   # as an object rather than named — a closed bell with its open rim pressed
   # down. Same lesson as the needles-drift-into-syringes note above.
   ("a Chinese therapist treating a relaxed person lying face down on a "
    "treatment couch with a white towel across the lower back, four cupping "
    "glasses standing in a row along the upper back, each one a thick rounded "
    "glass bell the size of a teacup, closed and domed on top, its open rim "
    "pressed against the skin so the skin is drawn gently up inside the glass, "
    "not a lid and not a shallow dish, the skin smooth and natural in tone "
    "with only a faint pink ring under each cup, the therapist's two hands "
    "steadying one cup, a calm warm treatment room", "people"),
   # 5 刮痧
   ("a smooth flat pale jade scraping tool being drawn along a person's oiled "
    "shoulder by a practitioner's hand, close up", "people"),
   # 6 推拿
   ("a practitioner in a white uniform pressing both thumbs firmly into a "
    "patient's upper back, the patient lying face down on a treatment couch", "people"),
   # 7 按摩 — take 1 grew a third hand; take 2 fixed the anatomy but landed on
   # a Western physio in navy scrubs at an office chair, which reads as a
   # workplace back rub rather than 按摩 (Alex, 7 Sep). Keep the hand guard
   # that worked — whole therapist in frame, "exactly two hands", the client's
   # own hands given somewhere to be — and move the room to China.
   ("one Chinese massage therapist in a loose plain cotton uniform standing "
    "behind a seated Chinese client and kneading the client's shoulders with "
    "both hands, the client sitting upright on a low wooden stool with eyes "
    "closed and a calm relaxed face, the client's own hands resting on their "
    "own thighs, a warm wood-panelled massage room with folded towels and a "
    "soft lamp behind, seen from the front at chest height, only one therapist "
    "and exactly two hands visible", "people"),
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

# Per-sentence story illustrations. The reader builds the path from the cover
# URL — .../pack_tcm_story_x.jpg becomes .../pack_tcm_story_x_s<idx>.jpg
# (sentenceImageFor() in index.html) — so nothing in the pack JSON changes; the
# files simply have to exist. They did not, so every sentence fell back to the
# cover and the story looked like one picture repeated (Alex, 7 Sep). The index
# is 0-based and matches the sentence order in packs/chinese-medicine.json.
#
# Dr Pauline appears in two of the three stories, so she is described the same
# way every time — otherwise each frame casts a different doctor.
TEEN = ("a Chinese teenager about fifteen years old, tall and slim, in a "
        "plain t-shirt and jeans")
DOCTOR = ("Doctor Pauline, a warm middle-aged Chinese woman doctor with her "
          "hair tied back, in a white coat")

SCENES = dict(

 pack_tcm_story_pulse = [
   # 0 headache, sore throat, sleeping badly
   ("a teenage Chinese boy sitting on the edge of his bed late at night in a "
    "dim bedroom, one hand pressed to his forehead, tired and unwell, a glass "
    "of water on the bedside table"),
   # 1 Mum: let us go and see Dr Pauline
   ("a Chinese mother in the hallway of a flat holding a coat out to her son, "
    + TEEN + ", and gesturing towards the front door, both mid-conversation, "
    "warm daylight"),
   # 2 taking the pulse
   (DOCTOR + " seated at a wooden desk in a Chinese medicine clinic, three "
    "fingertips resting on the wrist of a teenage boy whose forearm lies on a "
    "small silk pulse cushion, a wall of small wooden herb drawers behind, "
    "warm lamplight"),
   # 3 looking at the tongue
   (DOCTOR + ", her own face calm and neutral with her mouth closed, leaning "
    "forward with a small examination light to look at the tongue of " + TEEN +
    " sitting opposite her with his mouth open, consulting room"),
   # 4 the prescription and the chrysanthemum tea
   (DOCTOR + " writing on a sheet of cream prescription paper at her desk "
    "while a teenage boy watches, a clear glass of pale golden chrysanthemum "
    "tea with whole white flowers floating in it beside her, the page mostly "
    "covered by her hand, no visible writing"),
   # 5 three days later, sleeping well
   ("a teenage Chinese boy waking rested in a sunlit bedroom, sitting up and "
    "stretching with a relaxed smile, bright morning light through the window"),
 ],

 pack_tcm_story_acupuncture = [
   # 0 desk job, sore lower back
   ("a middle-aged Chinese man hunched at a desk in front of a computer "
    "monitor in a home office, one hand pressed to his lower back, wincing, "
    "late afternoon light"),
   # 1 arriving at the clinic
   ("a middle-aged Chinese man stepping in through the glass door of a small "
    "Chinese medicine clinic from the street, a reception desk and a wall of "
    "wooden herb drawers visible inside, daylight"),
   # 2 finding the points, inserting the needles
   (DOCTOR + " gently inserting " + NEEDLE + " into the lower back of a "
    "middle-aged Chinese man lying face down on a treatment couch, a neat row "
    "of needles already standing along his back, calm clinic room"),
   # 3 nervous, but only a tingle
   ("close up of a middle-aged Chinese man's face resting sideways on a "
    "treatment couch pillow, eyes closed, apprehensive but calm, a folded "
    "towel under his cheek, soft clinic light"),
   # 4 moxibustion on the back
   (DOCTOR + " holding a smouldering moxa stick, a rolled cigar-shaped stick "
    "of dried mugwort glowing orange at the tip with a thin wisp of smoke, a "
    "few centimetres above the back of a man lying face down on a treatment "
    "couch, warm light"),
   # 5 standing up, back much lighter
   ("a middle-aged Chinese man standing beside a treatment couch in a clinic, "
    "stretching his back with a relieved smile, " + DOCTOR + " standing beside "
    "him smiling"),
 ],

 pack_tcm_story_liangcha = [
   # 0 arriving in the Guangzhou heat
   ("a teenage Chinese visitor with a backpack arriving at an old Guangzhou "
    "apartment block on a hot humid summer day, wiping sweat from their "
    "forehead, hazy heat, potted plants and washing on the balconies above"),
   # 1 Grandma: that is damp heat
   ("a smiling elderly Chinese grandmother in a light cotton blouse holding up "
    "an empty bowl as she explains something to " + TEEN + ", who stands a "
    "head taller than her in a small kitchen, warm daylight"),
   # 2 simmering the herbs
   ("an elderly Chinese grandmother dropping dried chrysanthemum flowers and "
    "pale slices of liquorice root into a dark clay pot simmering on a gas "
    "ring, steam rising, an open wooden cupboard of herb jars behind, small "
    "kitchen"),
   # 3 the tea is bitter
   (TEEN + " screwing up their face after a sip of dark bitter herbal tea from "
    "a small bowl at a kitchen table, an elderly Chinese grandmother laughing "
    "warmly beside them"),
   # 4 clear the heat when it is hot, keep warm when it is cold
   ("an elderly Chinese grandmother sitting at a kitchen table talking "
    "earnestly to her grandchild, " + TEEN + ", and gesturing with one hand, "
    "two bowls of dark herbal tea and a clay pot on the table between them, "
    "warm evening light"),
   # 5 making it themselves the next day
   (TEEN + " standing at a stove ladling dark herbal tea from a clay pot into "
    "a bowl, bright and energetic, morning light in a small kitchen"),
 ],
)

SEED = 94000          # fresh block; prepare-for-china used 93000+
SEED_OVERRIDES = {"tcm-treatments/10": 94777,   # redo: pseudo-Latin scribbles on the first take
                  "tcm-treatments/4": 94833,     # redo 8 Sep: cups drawn as flat lids
                  "tcm-treatments/7": 94834}     # redo 7 Sep: three hands
here = os.path.dirname(os.path.abspath(__file__))


def run(label, out, prompt, seed, w, h, mx, force=False):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out) and not force:
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
    args = sys.argv[1:]
    force = "--force" in args          # redo images that already exist, e.g.
    args = [a for a in args if a != "--force"]   # after changing a prompt/seed
    want = args or list(DECKS) + ["stories", "scenes"]
    covers_only = want == ["covers"]
    jobs = []
    n = 0
    for deck, prompts in DECKS.items():
        for i, p in enumerate(prompts):
            prompt, style = p if isinstance(p, tuple) else (p, "object")
            label = f"{deck}/{i}"
            if deck in want or label in want or (covers_only and i == 0):
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
    for sid, prompts in SCENES.items():
        for i, p in enumerate(prompts):
            name = sid + "_s" + str(i)
            # 'scenes', a story id, or a single frame name (for a redo)
            if "scenes" in want or sid in want or name in want:
                jobs.append((name, os.path.join(here, "images", name + ".jpg"),
                             p + SCENE_IMG_STYLE, SEED + n * 13, 1216, 832, 760))
            n += 1

    print(f"Generating {len(jobs)} images…", flush=True)
    ok = 0
    fail = []
    for i, (label, out, prompt, seed, w, h, mx) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}]", flush=True)
        if run(label, out, prompt, seed, w, h, mx, force):
            ok += 1
        else:
            fail.append(label)
    print(f"\nDONE: {ok} ok, {len(fail)} failed: {fail}", flush=True)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
