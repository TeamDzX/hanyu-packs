#!/usr/bin/env python3
"""Generate every image for the Prepare for China pack.

  images/flashcards/<deck>/<idx>.jpg   640x640 card photos (card 0 doubles as the
                                       deck cover, cropped 'center 20%' by the app
                                       — keep its subject in the UPPER MIDDLE and
                                       keep open sky out of the frame)
  images/pack_pfc_story_<id>.jpg       760x520 story cards

App cards are prompted as the ACT the app performs (scanning a code, a car
pulling up, a delivery rider) — never as a logo or a UI screenshot. The house
"no text, no letters" clause does the rest: it keeps invented brand marks and
garbled Latin/Chinese UI text off the cards, which is what we want here anyway
since these are real third-party trademarks.

    python3 gen_prepare_china.py            # everything
    python3 gen_prepare_china.py travel-apps   # one deck, or 'stories'
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/.claude/scripts/imagegen"))
from comfy_gen import generate

CARD_STYLE = (", clean modern photograph, single subject centered, soft plain "
              "studio background, bright even lighting, shallow depth of field, "
              "crisp and colourful, no text, no letters, no watermark")

# Wide real locations — a studio background turns these into floating dioramas.
SCENE_STYLE = (", clean modern photograph, real location, contemporary China, "
               "natural daylight, sharp focus, no text, no letters, no watermark")

# Anything with a person in it: without the nationality anchor Flux casts Western
# faces, which reads wrong beside the rest of the app.
PEOPLE_STYLE = (", clean modern photograph, contemporary China, Chinese people, "
                "natural light, shallow depth of field, warm and friendly, "
                "no text, no letters, no watermark")

STYLES = {"object": CARD_STYLE, "scene": SCENE_STYLE, "people": PEOPLE_STYLE}

STORY_STYLE = (", photorealistic photograph, natural realistic lighting, shallow "
               "depth of field, candid documentary style, contemporary China, "
               "main subject placed on the RIGHT side of the frame, simple "
               "uncluttered out-of-focus space on the LEFT third, "
               "no text, no letters, no watermark")

DECKS = {
 "travel-apps": [
   # Cover: subject in the upper middle, no sky.
   ("a customer holding up a smartphone to scan a plain black and white square code "
    "displayed on a small stand on a market stall counter, the phone and the code in "
    "the upper middle of the frame, busy Chinese street market behind, no sky", "people"),
   ("a hand holding a smartphone showing a plain green messaging app chat screen of "
    "empty speech bubbles, blurred warm café interior behind", "people"),
   ("a customer holding out a smartphone with a plain blue payment screen towards a "
    "card reader on a shop counter", "people"),
   # 扫码 is the ACT of scanning. "camera held over a code" gave a phone merely
   # displaying a code, which collided with 付款码 on the next card — the phone has
   # to be pointed AT an external code with that code visible on screen.
   ("two hands holding a smartphone angled down towards a small square code sticker "
    "stuck on a restaurant tabletop, the code clearly on the table below the phone and "
    "the phone screen showing the camera view framing it, mid-scan", "object"),
   ("a smartphone held out at a supermarket till, its screen showing a plain barcode "
    "being read by the checkout scanner", "people"),
   ("a passport lying open on a desk beside a smartphone showing a blank form screen, "
    "warm desk lamp light", "object"),
   ("a smartphone mounted on a car dashboard showing a colourful navigation map with "
    "a bright route line, a city street ahead through the windscreen", "scene"),
   ("a person standing at the kerb holding up a phone as a small car pulls up beside "
    "them on a Chinese city street at dusk", "people"),
   ("a young Chinese woman sitting in a busy restaurant looking at her phone showing "
    "a grid of food photographs and star ratings", "people"),
   ("a food delivery rider in a bright uniform and helmet on a scooter with a large "
    "square insulated delivery box on the back, Chinese city street", "people"),
   ("a smartphone propped on a desk showing a grid of hotel room photographs, a "
    "passport and a small wheeled suitcase beside it", "object"),
   ("a smartphone showing a grid of product photographs on a shopping app, surrounded "
    "by small brown cardboard parcels on a table", "object"),
   ("a young Chinese woman photographing a styled cup of coffee and a dessert with her "
    "phone in a bright modern café, lifestyle photo being taken", "people"),
   ("a hand holding a smartphone showing a walking route map with a blue line, a busy "
    "pedestrian street softly blurred behind", "people"),
 ],
 "trip-prep": [
   # Cover: a flat lay fills the frame, so nothing is lost to the crop.
   ("a dark red passport lying open in the very centre of a wooden table and filling "
    "much of the frame, a boarding pass tucked between its pages, sunglasses and a "
    "folded map arranged around it, seen from directly above, no sky", "object"),
   ("a hand holding a plain paper boarding pass in front of an airport departure gate "
    "window with a plane outside", "people"),
   ("a hard-shell wheeled cabin suitcase standing upright, handle extended", "object"),
   ("an airport immigration hall with orderly queues of travellers waiting at passport "
    "control booths, bright modern terminal", "scene"),
   ("an airport customs inspection area, an open suitcase on a stainless steel "
    "inspection bench with a uniformed officer looking through it, a baggage x-ray "
    "machine behind, modern airport interior", "scene"),
   ("a hand holding a small SIM card above a smartphone with its SIM tray open on a "
    "desk", "object"),
   ("a person walking on a busy Chinese city street looking at their phone, a mobile "
    "network mast on a rooftop in the background", "people"),
   ("a white universal travel adapter plug with several different pin configurations "
    "folded out", "object"),
   ("a bank teller behind a currency exchange counter handing a small stack of red "
    "banknotes across to a customer", "people"),
   ("stacks of red banknotes beside foreign banknotes and a small desk calculator on a "
    "counter", "object"),
   # A two-person handover gave the guest two hands on one arm. One person
   # holding the card up, with both hands placed explicitly, is reliable.
   ("a smiling hotel receptionist standing alone behind a bright modern reception "
    "desk, holding up a single plain plastic key card in her right hand at chest "
    "height, her left hand resting flat on the desk, both hands clearly visible "
    "with five fingers each, tidy hotel lobby behind her, no other people in the "
    "frame", "people"),
   ("a guest wheeling a suitcase away from a hotel reception desk towards bright glass "
    "exit doors", "people"),
 ],
}

STORIES = {
 "pack_pfc_story_before": "a cheerful young traveller packing a modern open suitcase on a bed in a bright tidy modern bedroom, folding clothes into it, a passport and a smartphone resting on the bed beside the case, warm daylight through a large window",
 "pack_pfc_story_arrive": "a traveller with a wheeled suitcase walking through a bright modern airport arrivals hall, looking at their phone",
 "pack_pfc_story_around": "a traveller sitting in the back of a car looking out of the window at a Chinese city street going past, phone in hand",
}

SEED = 93000          # fresh block; bugs-butterflies used 92000+

# Cards re-rolled after a bad draw: the formula seed is not the one that shipped.
SEED_OVERRIDES = {"trip-prep/10": 93777}
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
    jobs = []
    n = 0
    for deck, prompts in DECKS.items():
        for i, p in enumerate(prompts):
            prompt, style = p if isinstance(p, tuple) else (p, "object")
            if deck in want:
                label = f"{deck}/{i}"
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
    ok, fail = 0, []
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
