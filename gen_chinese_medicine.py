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
   # Take 1 drew the black half with NO white dot and a malformed S-curve
   # (QC, 8 Sep) — a factual error on the card that teaches the symbol. Flux
   # will not count dots from "in each", so both are spelled out separately.
   ("a round polished stone plaque standing upright on raked pale sand, carved "
    "and painted with a taijitu: one perfect circle divided by a single smooth "
    "S-curve into one solid black half and one solid white half, with exactly "
    "two small round dots in the whole design — one single white dot centred "
    "in the black half, and one single black dot centred in the white half, "
    "clean and symmetrical, no cracks", "object"),
   # 3 五行
   ("five small natural objects arranged in a circle on dark slate: a green "
    "sprig of wood, a lit candle flame, a mound of yellow earth, a polished "
    "metal ingot and a shallow bowl of clear water, seen from above", "object"),
   # 4 经络
   ("a classic bronze acupuncture teaching figure, a standing human statue "
    "with fine engraved lines running along its arms and legs and tiny holes "
    "marking points, on a wooden stand", "object"),
   # 5 穴位
   # Take 1 grew a third hand and lost the finger count (QC, 8 Sep). Same
   # guard that fixed 按摩: say how many hands belong in the frame.
   # Round 2 still produced a third hand. Crop tighter and make the count the
   # first thing in the prompt rather than a trailing qualifier.
   ("extreme close up of exactly two hands and nothing else: a patient's hand "
    "resting palm down and flat on a white towel, and one Chinese "
    "practitioner's hand above it pressing a single extended index fingertip "
    "into the webbing between the patient's thumb and index finger, two hands "
    "only in the whole picture, five fingers on each, no other fingers, thumbs "
    "or arms anywhere, clear even skin, soft light", "people"),
   # 6 把脉
   # Take 1 laid a whole palm flat on the cushion (wrong technique — it is
   # three fingers on the radial artery) and grew extra digits (QC, 8 Sep).
   # Round 2 laid the whole palm flat across the wrist again. Lift the palm
   # explicitly, and put the hand count first.
   # Take 3 lifted the palm but turned it into a two-finger pinch. Name the
   # three fingers individually — "three fingertips" alone reads as a pinch.
   ("a Chinese doctor of about sixty in a white coat sitting at a wooden desk "
    "in a Chinese medicine clinic, leaning slightly forward to take the pulse "
    "of a patient sitting opposite her, the patient's bare forearm resting on "
    "a small silk pulse cushion between them and the doctor's fingers resting "
    "along the inside of the wrist, both people from the chest up and fully in "
    "frame, a wall of small wooden herb drawers behind, warm lamplight", "people"),
   # 7 舌头
   # Take 1 put the white coat on the person sticking their tongue out, so the
   # doctor appeared to be the patient, and cast both as Western (QC, 8 Sep).
   ("a young Chinese adult patient in an ordinary casual t-shirt sitting "
    "upright with their mouth open and tongue out to be examined, while a "
    "Chinese doctor — the only person wearing a white coat — leans in holding "
    "a small penlight a clear distance away from the mouth, the tongue a "
    "healthy normal pink, side view, calm clinic", "people"),
   # 8 上火
   # Take 1 drew steam rising off an iced drink, and the fried food read as
   # fried larvae (QC, 8 Sep).
   ("a tall glass of cool pale golden chrysanthemum tea on a kitchen table "
    "beside a plate of crisp fried chicken pieces and fresh red chillies, the "
    "drink still and clear with no steam, warm kitchen light", "object"),
   # 9 养生
   ("a serene older Chinese man in loose clothing practising slow tai chi in a "
    "misty park at sunrise, arms extended, trees behind", "scene"),
   # 10 中医师
   ("a friendly middle-aged Chinese doctor in a white coat seated at a wooden "
    "desk with a wall of herb drawers behind, hands folded, smiling", "people"),
   # 11 体质
   # Take 1 filled the tablet with garbled micro-text and little figures, and
   # cast the patient as Western (QC, 8 Sep). Give the screen nothing to
   # garble: plain bars only.
   ("a Chinese doctor in a white coat turning a tablet towards a Chinese "
    "patient in a consulting room, the tablet screen showing only three plain "
    "coloured rounded bars and nothing else, both looking at the screen and "
    "smiling, no icons, no figures, no symbols, no writing of any kind", "people"),
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
   # Take 1 read unmistakably as a lit CIGAR burning bare skin (QC, 8 Sep) —
   # self-inflicted: the prompt itself said "cigar-shaped". Never use that
   # word here. Describe the paper wrap, kill the flame, and state the gap.
   # Round 2: the object finally read as moxa, but Flux put it against a bare
   # BELLY with an angry red glow on the skin, so it read as a burn. Name the
   # body part, and forbid marks on the skin as explicitly as the gap.
   ("a Chinese practitioner holding a moxibustion stick above the bare upper "
    "back of a Chinese patient lying face down on a treatment couch: a "
    "straight matte cylinder of compressed dried mugwort wrapped in plain pale "
    "beige paper, its far end capped with soft grey ash over a faint dark "
    "ember, one thin wisp of pale smoke, no flame and no fire, held upright a "
    "full hand's width clear of the back with an obvious gap of air between "
    "the stick and the skin, the skin an even natural tone with no redness, no "
    "glow, no marks and no shine on it, not tobacco, not a cigar, calm clinic "
    "room", "people"),
   # 4 拔罐 — take 1 was gruesome (bruised, bloodshot rings); take 2 fixed the
   # skin but drew the cups as shallow glass LIDS lying on the back, so the
   # card no longer read as cupping (Alex, 7 Sep). Flux needs the cup described
   # as an object rather than named — a closed bell with its open rim pressed
   # down. Same lesson as the needles-drift-into-syringes note above.
   # Take 3 (QC, 8 Sep): the cups finally read as cups, but the client's head
   # was rotated as if facing up while the body lay prone. Say where the head
   # goes, the way the hand count is said.
   ("a Chinese therapist treating a relaxed Chinese person lying face down on "
    "a treatment couch, the person's head turned to one side with the cheek "
    "resting flat on the couch cushion and the neck straight and natural, "
    "never facing upwards, a white towel across the lower back, four cupping "
    "glasses standing in a row along the upper back, each one a thick rounded "
    "glass bell the size of a teacup, completely empty and dry inside with "
    "clear colourless glass and no liquid of any kind in it, not a glass of "
    "drink, closed and domed on top, its open rim "
    "pressed against the skin so the skin is drawn gently up inside the glass, "
    "not a lid and not a shallow dish, the skin smooth and natural in tone "
    "with only a faint pink ring under each cup, the therapist's two hands "
    "steadying one cup, only one therapist and exactly two hands visible, "
    "a calm warm treatment room", "people"),
   # 5 刮痧
   # Take 1: a hand with no arm entered frame holding a paddle the size of a
   # cheese slicer, over blotchy skin (QC, 8 Sep).
   # Round 2 fixed the floating hand but grew a second rod alongside the
   # scraper. Describe the one object concretely and forbid any other.
   ("a Chinese practitioner's hand holding one small flat pale jade scraping "
    "plate — a smooth rounded rectangle about the size of a matchbox, gripped "
    "flat between the thumb and fingers — and drawing it downwards along the "
    "oiled shoulder of a seated Chinese client, that single plate the only "
    "object in the whole picture with no stick, rod or second tool anywhere, "
    "the practitioner's whole hand and wrist in view, faint light pink streaks "
    "on the skin where it has passed, close up, calm treatment room", "people"),
   # 6 推拿
   # Take 1 cast a Western clinician in a lab coat and framed it almost
   # identically to 按摩 (QC, 8 Sep). Keep tuina prone and side-on so the two
   # cards read as different treatments.
   ("a Chinese tuina practitioner in a loose plain cotton uniform pressing "
    "both thumbs firmly along the spine of a Chinese patient lying face down "
    "on a treatment couch, the patient's head turned to one side on the "
    "cushion, seen from the side at couch height, only one practitioner and "
    "exactly two hands visible, warm wood-panelled treatment room", "people"),
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
   # Take 1: eight Western figures with melted faces and hands, arms flung
   # overhead so it read as a star-jump class, not taiji (QC, 8 Sep). Fewer
   # people means fewer faces to garble, and the arms are pinned below
   # shoulder height.
   ("three older Chinese people in loose dark silk exercise clothes practising "
    "tai chi together on a stone terrace in a park in the early morning, all "
    "three in the same slow posture with the weight settled onto one bent leg "
    "and both arms curved softly in front of the chest at shoulder height, "
    "arms never raised above the head, calm and unhurried, mist and trees "
    "behind", "scene"),
   # 9 气功
   # Take 1 was a young Western hiker in a puffer jacket, hands pressed
   # together in a namaste on a Californian ridge — nothing to do with qigong
   # (QC, 8 Sep). Name the cast, the clothing, the place and the hand shape.
   ("an older Chinese man in loose dark cotton exercise clothes standing alone "
    "in a quiet Chinese park courtyard at dawn, feet shoulder-width apart, "
    "knees softly bent, both hands empty and open with the palms turned "
    "upwards, held well apart at waist height with nothing at all in them and "
    "no object between them, no ball, eyes closed, breathing calmly, his hands "
    "not touching and never pressed together, no prayer gesture, willow trees "
    "and a stone balustrade behind", "scene"),
   # 10 药方 — first take wrote pseudo-Latin scribbles across the page. Hide
   # the writing under the hand and let the red seal and herb packets carry it.
   # Take 2 hid the page writing as intended but moved the garbling onto the
   # brush: gold pseudo-hanzi down the shaft, a pencil tip instead of bristles,
   # and a stray (R) trademark glyph by the seal (QC, 8 Sep).
   ("a Chinese doctor's hand holding a calligraphy brush with a plain unmarked "
    "dark wooden handle and a soft black tapered bristle tip, writing on a "
    "sheet of cream paper that is mostly covered by the hand and sleeve, a "
    "single red square seal stamp in the corner, three small folded paper "
    "packets of dried herbs beside the page, seen from directly above, no "
    "visible writing, no lettering or decoration on the brush handle, no "
    "logos, no symbols, no trademark marks", "object"),
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
   # "long forked branching rootlets" invited a twelve-legged spider (QC,
   # 8 Sep). Ginseng is stout with two or three short legs — cap the count.
   # Take 1 was a twelve-legged spider; capping the legs overcorrected into a
   # smooth grub (QC round 2). Ginseng needs its ringed neck to read at all.
   # Three takes: a twelve-legged spider, then a smooth grub, then a turnip
   # with a green shoot. Each correction pulled it toward a fresh vegetable.
   # Naming it DRIED and WOODY, and showing several rather than one hero
   # object, is what stops the vegetable reading.
   ("three dried ginseng roots lying side by side on a wooden board, each a "
    "slender pale brown woody root about the length of a little finger, deeply "
    "wrinkled and hard and dry like a twig, with a long tapering body, two "
    "thin leg-like roots and fine whiskers, no green stem, no leaves, no fresh "
    "vegetable, not a turnip, not a radish, not round, not bulbous", "object"),
   # 3 枸杞
   # Take 1 drew plump almond-sized fruit — effectively the 红枣 card twice
   # over, wrong ingredient on a vocabulary card (QC, 8 Sep). Give the size.
   # Two takes now have come back almond-shaped and plump. A size in words is
   # not landing — compare it to a familiar object of the right size instead.
   # Takes 1-3 all came back almond-sized and plump, whether the prompt said
   # "grain of rice" or "small raisin". A size in words does not land — put an
   # object of KNOWN size in the frame and let the berries be measured against
   # it. This is the general fix for any small ingredient.
   ("a small white ceramic spoon heaped with dried goji berries resting on a "
    "white saucer, the berries so small that fifty of them fill the spoon, "
    "each one a thin shrivelled orange-red sliver like a tiny wrinkled raisin, "
    "a scattering of them around the saucer, nothing in the picture bigger "
    "than a lentil, not almonds, not nuts, not dates, close up from above", "object"),
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
   # "dried red dates" pulled Flux to glossy Middle-Eastern medjool dates
   # with a bolt-head at each end (QC, 8 Sep). Lead with jujube and the size.
   ("a small white bowl of dried Chinese jujubes: small oval fruit about the "
    "size of an olive, deep brownish red with finely wrinkled matte skin and "
    "a tiny stem scar at one end, a few spilled beside the bowl, not large "
    "glossy medjool dates, close up", "object"),
   # 8 甘草
   ("thin diagonal slices of dried liquorice root, pale yellow with a "
    "fibrous grain and a thin brown bark edge, on cream linen", "object"),
   # 9 凉茶
   # Take 1 started the stream in mid-air with no spout above it (QC, 8 Sep).
   # Line the three things up explicitly: tap, stream, bowl.
   ("a traditional Cantonese herbal tea shop counter with several large brass "
    "and copper urns, dark herbal tea running in one continuous stream from "
    "the clearly visible curved brass tap of the nearest urn straight down "
    "into a small white bowl standing directly beneath it, the tap and the "
    "stream and the bowl all lined up vertically, warm evening light", "scene"),
   # 10 汤药
   ("a dark clay pot of simmering herbal decoction on a gas ring, dark brown "
    "liquid, dried herbs visible in the pot, steam rising, a ladle beside", "object"),
   # 11 药膳
   ("a steaming clay bowl of clear chicken soup with red dates, goji berries "
    "and a slice of ginseng floating in it, chopsticks and a ceramic spoon", "object"),
 ],
}

# QC, 8 Sep: "middle-aged, hair tied back" was too loose an anchor — the
# final frame of the acupuncture story cast a visibly younger woman, and
# grandma's age and blouse changed between the liangcha cover and s2/s3. Each
# recurring character now carries one hard-to-drift feature (the glasses, the
# white hair, the greying crop) and is described identically every time.
TEEN = ("a Chinese teenager about fifteen years old, tall and slim, in a "
        "plain t-shirt and jeans")
# Kept deliberately short: an anchor is only worth what it costs the rest of
# the prompt, and "the same woman in every picture" is an instruction Flux
# cannot act on — the concrete features (the glasses, the white hair, the
# greying crop) are what actually hold a character steady between frames.
DOCTOR = ("Doctor Pauline, a Chinese woman doctor of about fifty with a round "
          "face, gold-rimmed glasses and black hair in a low bun, in a white "
          "coat")
GRANDMA = ("Grandma Chen, a small cheerful Chinese grandmother of about "
           "seventy-five with short white hair, in a blue floral cotton blouse")
MAN = ("a sturdily built Chinese man of about fifty with a short greying crop")

STORIES = {
 # QC 8 Sep: take 1 put two white-coated doctors in the frame and muddled the
 # fingers where the hands met at the cushion. One doctor, hands accounted for.
 # Round 2 cropped the boy out entirely — the patient was a disembodied
 # forearm at the frame edge — and drew the mother as an elderly woman.
 "pack_tcm_story_pulse":       ("exactly two people in the picture and nobody else: " + TEEN + " sitting on "
                                "the right of the frame in a Chinese medicine clinic with his whole face and "
                                "upper body clearly visible and his bare forearm resting on a small silk pulse "
                                "cushion on a wooden desk, and " + DOCTOR + " sitting opposite him with her "
                                "fingers resting along the inside of his wrist, no other person and no second "
                                "white coat, a wall of small wooden herb drawers behind, warm lamplight"),
 # QC 8 Sep: take 1 drove the needles through his t-shirt and shorts and stood
 # one in the treatment couch, and the moxa stick came out as a lit cigar. The
 # back is bare here and the moxa moves to scene 4, where it belongs.
 "pack_tcm_story_acupuncture": ("" + MAN + ", lying face down on a treatment couch, calm and relaxed, his shirt "
                                "removed so his whole back is bare skin with a white towel folded across his "
                                "hips, a neat row of " + NEEDLE + " standing in the bare skin of his lower back "
                                "only, no needles in any fabric or clothing and none in the couch, his head "
                                "turned to one side on the cushion, " + DOCTOR + " standing beside the couch, "
                                "calm clinic room"),
 # QC 8 Sep: take 1 poured the tea out of the pot's body with the spout facing
 # away, and the grandchild appeared to be eating a handful of herbs.
 "pack_tcm_story_liangcha":    ("" + GRANDMA + " in a bright kitchen, tilting a dark clay teapot so a thin "
                                "continuous stream of dark herbal tea runs from its clearly visible spout "
                                "straight down into a ceramic bowl standing on the table, the spout directly "
                                "above the bowl, and " + TEEN + " sitting beside her as her grandson, "
                                "pulling a face at the bitter smell with both hands flat on the table, only "
                                "two people and exactly four hands in the frame"),
}

# Per-sentence story illustrations. The reader builds the path from the cover
# URL — .../pack_tcm_story_x.jpg becomes .../pack_tcm_story_x_s<idx>.jpg
# (sentenceImageFor() in index.html) — so nothing in the pack JSON changes; the
# files simply have to exist. They did not, so every sentence fell back to the
# cover and the story looked like one picture repeated (Alex, 7 Sep). The index
# is 0-based and matches the sentence order in packs/chinese-medicine.json.
#
# Dr Pauline appears in two of the three stories, so she is described the same
# way every time — otherwise each frame casts a different doctor. The character
# anchors themselves now live above STORIES, since the covers need them too.

SCENES = dict(

 pack_tcm_story_pulse = [
   # 0 headache, sore throat, sleeping badly
   ("a teenage Chinese boy sitting on the edge of his bed late at night in a "
    "dim bedroom, one hand pressed to his forehead, tired and unwell, a glass "
    "of water on the bedside table"),
   # 1 Mum: let us go and see Dr Pauline
   ("a Chinese mother in her forties, clearly a generation older than her son, "
    "with shoulder-length hair and a plain blouse, standing in the hallway of "
    "a flat holding a jacket out to him, " + TEEN + ", and gesturing towards "
    "the front door, both mid-conversation, warm daylight"),
   # 2 taking the pulse
   (DOCTOR + " seated at a wooden desk in a Chinese medicine clinic, three "
    "fingertips laid in a neat row across the wrist of " + TEEN + " whose bare "
    "forearm lies on a small silk pulse cushion, only two hands anywhere near "
    "the cushion, a wall of small wooden herb drawers behind, warm lamplight"),
   # 3 looking at the tongue
   # QC 8 Sep: take 1 pressed the light onto the tongue and rendered the
   # tongue as a slab of raw meat.
   (DOCTOR + ", her own face calm with her mouth closed, holding a small "
    "penlight a clear distance away from the open mouth of " + TEEN + " who "
    "sits opposite her, his tongue a healthy normal pink, the light never "
    "touching him, consulting room"),
   # 4 the prescription and the chrysanthemum tea
   # Round 2 ignored "no visible writing" and filled the page with garbled
   # hanzi, and drew the teenager as a child of about eight. Turn the page away
   # from the camera rather than asking for an empty page.
   (DOCTOR + " at her desk resting the tip of her pen on a sheet of cream "
    "prescription paper that is tilted away from the camera and mostly hidden "
    "under her hand and sleeve so the page reads as blank, no lettering or "
    "characters anywhere, while " + TEEN + ", clearly a tall teenager of about "
    "fifteen and not a small child, stands watching, a clear glass of pale "
    "golden chrysanthemum tea with whole white flowers floating in it beside "
    "her"),
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
   # QC 8 Sep: take 1 put twenty needles through his t-shirt fabric.
   # Round 2 fixed the needles-through-fabric but duplicated the patient's
   # head into the bottom corner. State the body count, not just the hands.
   ("exactly two people in the picture and no one else — " + DOCTOR + " and one "
    "patient, one head each — she is gently inserting " + NEEDLE + " into the "
    "bare skin of the lower back of " + MAN + ", who lies face down on a "
    "treatment couch with his shirt removed and a white towel across his hips, "
    "his one head turned to the side at the far end of the couch, a neat row "
    "of needles already standing in the bare skin, no needles in any fabric, "
    "calm clinic room"),
   # 3 nervous, but only a tingle
   ("close up of the face of " + MAN + " resting sideways on a treatment couch "
    "pillow, eyes closed, apprehensive but calm, a folded towel under his "
    "cheek, his skin clear and even, soft clinic light"),
   # 4 moxibustion on the back
   # QC 8 Sep: take 1 grew a second lit stick hanging unsupported in mid-air,
   # and "cigar-shaped" again produced a cigar.
   (DOCTOR + " holding exactly one moxibustion stick — a straight matte "
    "cylinder of compressed dried mugwort wrapped in plain pale beige paper, "
    "its far end glowing a dull ember red with one thin wisp of pale smoke, no "
    "flame, not tobacco and not a cigar — held a clear hand's width above the "
    "bare back of " + MAN + " lying face down on a treatment couch, only one "
    "stick anywhere in the frame and nothing floating in the air, warm light"),
   # 5 standing up, back much lighter
   # Round 2 grew a third forearm across the doctor's shoulder. Give both
   # people's arms somewhere definite to be.
   ("exactly two people and exactly four arms in the picture: " + MAN + ", "
    "standing beside a treatment couch in a clinic with both of his own arms "
    "hanging relaxed at his sides and a relieved smile, and " + DOCTOR + " "
    "standing next to him smiling with her hands clasped in front of her, "
    "nobody touching anybody, both of them fully in frame"),
 ],

 pack_tcm_story_liangcha = [
   # 0 arriving in the Guangzhou heat
   ("a teenage Chinese visitor with a backpack arriving at an old Guangzhou "
    "apartment block on a hot humid summer day, wiping sweat from their "
    "forehead, hazy heat, potted plants and washing on the balconies above"),
   # 1 Grandma: that is damp heat
   (GRANDMA + " holding up an empty ceramic bowl as she explains something to "
    + TEEN + ", who stands a head taller than her in a small kitchen, warm "
    "daylight"),
   # 2 simmering the herbs
   (GRANDMA + " dropping dried chrysanthemum flowers and pale slices of "
    "liquorice root into a dark clay pot simmering on a gas ring, the flowers "
    "dried and papery rather than fresh cut blooms, steam rising, one hand "
    "above the pot and one hand resting on the pot handle, an open wooden "
    "cupboard of herb jars behind, small kitchen"),
   # 3 the tea is bitter
   (TEEN + " screwing up their face after a sip of dark bitter herbal tea from "
    "a small bowl at a kitchen table, " + GRANDMA + " laughing warmly beside "
    "them, one bowl each on the table"),
   # 4 clear the heat when it is hot, keep warm when it is cold
   (GRANDMA + " sitting at a kitchen table talking earnestly to her "
    "grandchild, " + TEEN + ", and gesturing with one open hand, two bowls of "
    "dark herbal tea and a clay pot on the table between them, warm evening "
    "light"),
   # 5 making it themselves the next day
   # Round 2 built a cascade: a pot pouring into a second pot pouring into a
   # bowl. Say how many vessels exist.
   (TEEN + " standing at a stove in a small kitchen holding one dark clay pot "
    "by its handle in both hands and tipping it so a single stream of dark "
    "herbal tea pours from its spout into one ceramic bowl on the worktop "
    "below, exactly one pot and exactly one bowl in the whole picture and no "
    "other pot, pan or vessel being poured, bright and energetic, morning "
    "light"),
 ],
)

SEED = 94000          # fresh block; prepare-for-china used 93000+

# Every entry below is a QC redo from 8 Sep — the review that followed the
# 7 Sep publish. A changed prompt alone would re-roll the image, but a fresh
# seed keeps it from landing back in the same bad basin.
SEED_OVERRIDES = {
    "tcm-foundations/2":             95000,  # taijitu had no white dot in the black half
    "tcm-foundations/5":             95007,  # three converging hands
    "tcm-foundations/6":             95014,  # extra digits, palm-flat instead of three fingers
    "tcm-foundations/7":             95021,  # the patient wore the white coat
    "tcm-foundations/8":             95028,  # steam rising off an iced drink
    "tcm-foundations/11":            95035,  # garbled micro-text on the tablet
    "tcm-treatments/3":              95042,  # read as a lit cigar on bare skin
    "tcm-treatments/4":              95049,  # head rotated wrongly for a prone body
    "tcm-treatments/5":              95056,  # disembodied hand, cheese-slicer paddle
    "tcm-treatments/6":              95063,  # Western clinician, near-duplicate of 按摩
    "tcm-treatments/8":              95070,  # star-jumps, melted faces
    "tcm-treatments/9":              95077,  # Western hiker doing a namaste
    "tcm-treatments/10":             95084,  # garbled gold hanzi on the brush, stray (R)
    "tcm-herbs/2":                   95091,  # twelve-legged spider root
    "tcm-herbs/3":                   95098,  # goji drawn as plump dates
    "tcm-herbs/7":                   95105,  # jujube drawn as medjool dates
    "tcm-herbs/9":                   95112,  # the pour started in mid-air
    "pack_tcm_story_pulse":          95119,  # two doctors, muddled hands
    "pack_tcm_story_acupuncture":    95126,  # needles through clothing and into the couch
    "pack_tcm_story_liangcha":       95133,  # poured from the pot's body, not the spout
    "pack_tcm_story_pulse_s1":       95140,  # the mother looked like a teenage peer
    "pack_tcm_story_pulse_s2":       95147,  # recast for the tightened Dr Pauline anchor
    "pack_tcm_story_pulse_s3":       95154,  # penlight on the tongue, tongue as raw meat
    "pack_tcm_story_pulse_s4":       95161,  # recast for the tightened Dr Pauline anchor
    "pack_tcm_story_acupuncture_s2": 95168,  # needles through the t-shirt
    "pack_tcm_story_acupuncture_s3": 95175,  # heavy facial mottling
    "pack_tcm_story_acupuncture_s4": 95182,  # a second moxa stick floating in mid-air
    "pack_tcm_story_acupuncture_s5": 95189,  # Dr Pauline recast as a younger woman
    "pack_tcm_story_liangcha_s1":    95196,  # one grandmother across the story
    "pack_tcm_story_liangcha_s2":    95203,  # one grandmother; flowers were fresh, not dried
    "pack_tcm_story_liangcha_s3":    95210,  # one grandmother across the story
    "pack_tcm_story_liangcha_s4":    95217,  # one grandmother across the story
    "pack_tcm_story_liangcha_s5":    95224,  # one grandmother; ladle pour was vague
}

# Round 2, same day: the redo itself needed a redo on these fourteen. Each
# note says what the FIRST redo produced, so a future pass does not repeat it.
SEED_OVERRIDES.update({
    "tcm-treatments/3":              96000,  # r2: moxa was held to a bare belly with a red burn glow
    "tcm-treatments/4":              96011,  # r2: cupping glasses came back full of coloured liquid
    "tcm-treatments/5":              96022,  # r2: a second rod appeared alongside the jade scraper
    "tcm-treatments/9":              96033,  # r2: 'invisible ball' produced a real leather ball
    "tcm-foundations/5":             96044,  # r2: still a third hand
    "tcm-foundations/6":             96055,  # r2: palm still laid flat across the wrist
    "tcm-herbs/2":                   96066,  # r2: overcorrected from spider root into a smooth grub
    "tcm-herbs/3":                   96077,  # r2: still almond-shaped and plump
    "pack_tcm_story_pulse":          96088,  # r2: the boy was cropped to a disembodied forearm
    "pack_tcm_story_liangcha":       96099,  # r2: the grandchild was drawn as a small Western boy
    "pack_tcm_story_acupuncture_s2": 96110,  # r2: the patient's head was duplicated
    "pack_tcm_story_acupuncture_s5": 96121,  # r2: a third forearm across the doctor's shoulder
    "pack_tcm_story_pulse_s4":       96132,  # r2: garbled hanzi on the page, boy drawn as a child
    "pack_tcm_story_liangcha_s5":    96143,  # r2: a pot pouring into a pot pouring into a bowl
})

# Round 3: the two herb cards and the pulse technique needed a third pass.
SEED_OVERRIDES.update({
    "tcm-herbs/3":              97001,  # r3: almond-sized in all three earlier takes
    "tcm-herbs/2":              97002,  # r3: spider -> grub -> turnip
    "tcm-foundations/6":        97003,  # r3: palm lifted but became a two-finger pinch
    "pack_tcm_story_pulse":     97004,  # r3: the mother kept reading as a second clinician
})

# Round 4: two frames that four re-rolls could not fix were re-STAGED rather
# than re-rolled — 把脉 pulled back from a hand close-up to the wider two-person
# framing that worked first time in the pulse story, and the pulse cover lost
# the third person the white coat kept attaching itself to.
SEED_OVERRIDES.update({
    "tcm-foundations/6":    98001,
    "pack_tcm_story_pulse": 98002,
})

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
        if "stories" in want or sid in want:
            jobs.append((sid, os.path.join(here, "images", sid + ".jpg"),
                         p + STORY_STYLE,
                         SEED_OVERRIDES.get(sid, SEED + n * 13), 1216, 832, 760))
        n += 1
    for sid, prompts in SCENES.items():
        for i, p in enumerate(prompts):
            name = sid + "_s" + str(i)
            # 'scenes', a story id, or a single frame name (for a redo)
            if "scenes" in want or sid in want or name in want:
                jobs.append((name, os.path.join(here, "images", name + ".jpg"),
                             p + SCENE_IMG_STYLE,
                             SEED_OVERRIDES.get(name, SEED + n * 13), 1216, 832, 760))
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
