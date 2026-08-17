#!/usr/bin/env python3
"""Generate every image for the Back to School pack.

  images/flashcards/<deck>/<idx>.jpg   640x640 card photos (card 0 is also the
                                       deck cover, cropped 'center 20%' by the
                                       app — so keep card 0 a scene, not a face)
  images/pack_bts_story_<id>.jpg       760x520 story cards

Abstract words (school subjects, "revise", "term starts") are prompted as
PHYSICAL scenes — naming the concept alone gives Flux nothing to draw. Same
lesson as the erhu-renders-as-a-guitar problem in the music deck.

    python3 gen_back_to_school.py            # everything
    python3 gen_back_to_school.py subjects   # one deck, or 'stories'
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/.claude/scripts/imagegen"))
from comfy_gen import generate

# House flashcard look — matches vols 1-5 and hearts-feelings.
CARD_STYLE = (", clean modern photograph, single subject centered, soft plain "
              "studio background, bright even lighting, shallow depth of field, "
              "crisp and colourful, no text, no letters, no watermark")

# Two variants of the card look, both needed by this pack:
#   scene  — "soft plain studio background" makes Flux render a wide location as
#            a tiny isometric MODEL floating on white (it did exactly that to
#            the sports field). Real locations need a real setting instead.
#   people — without an explicit nationality Flux casts Western faces, which
#            looks wrong next to the rest of the app. The story prompts only
#            got this right because their style string says "contemporary China".
SCENE_STYLE = (", clean modern photograph, real location, contemporary China, "
               "natural daylight, sharp focus, wide establishing view, "
               "no text, no letters, no watermark")
PEOPLE_STYLE = (", clean modern photograph, contemporary China, Chinese people, "
                "natural light, shallow depth of field, warm and friendly, "
                "no text, no letters, no watermark")

STYLES = {"object": CARD_STYLE, "scene": SCENE_STYLE, "people": PEOPLE_STYLE}

# Story cards leave the left third clear for the title overlay.
STORY_STYLE = (", photorealistic photograph, natural realistic lighting, shallow "
               "depth of field, candid documentary style, contemporary China, "
               "main subject placed on the RIGHT side of the frame, simple "
               "uncluttered out-of-focus space on the LEFT third, "
               "no text, no letters, no watermark")

DECKS = {
 "classroom": [
   "a bright modern school classroom with neat rows of wooden desks facing a whiteboard, sunlight through tall windows",
   "a large dark green chalkboard filling a classroom wall, faint chalk dust, a wooden chalk ledge below",
   "a handful of colourful chalk sticks in an open wooden box beside a felt chalkboard eraser",
   "a wooden teacher's lectern standing on a low platform at the front of an empty classroom",
   "a single small wooden school desk with an attached chair, standing alone in an empty classroom",
   "a neat stack of hardback school textbooks piled on a desk beside a pen",
   "a Chinese school uniform tracksuit in blue and white hanging on a wooden hanger, zip jacket and matching trousers",
   "a bright yellow school bus parked at the kerb outside a school building on a sunny morning",
   ("a school sports field with a red running track around a green football pitch, "
    "students playing in the distance, sunny day", "scene"),
   "a school canteen with long tables and a stainless steel serving counter of hot food trays",
   "a tidy student dormitory room with wooden bunk beds, folded bedding and two small study desks",
   "a school science laboratory with long black benches, sinks, gas taps and glass beakers",
   ("two smiling Chinese teenage classmates in school uniform sitting side by side at a shared desk, books open", "people"),
   ("a friendly middle-aged Chinese head teacher in a smart suit standing in a bright school corridor, arms relaxed", "people"),
   "a long row of tall metal school lockers in a corridor, one door slightly open",
 ],
 "subjects": [
   "a wooden geometry set on graph paper - metal compass, protractor, set squares and a pencil",
   "a traditional calligraphy brush resting on a stone brush rest beside a black inkstone and blank rice paper",
   "a language classroom desk with over-ear headphones, a large world map on the wall behind",
   "an old folded map, a brass pocket watch, a bronze vessel and a rolled scroll on a dark wooden table",
   "a raised relief globe and a folded topographic map with a brass compass and coloured map pins",
   "a Newton's cradle with swinging steel balls beside a horseshoe magnet on a laboratory bench",
   "glass beakers and test tubes in a wooden rack filled with bright blue, green and orange liquids",
   "a silver laboratory microscope beside a green leafy potted plant and a glass specimen slide",
   "an orange basketball, a pair of running shoes and a coach's whistle on a polished gym floor",
   "an artist's wooden palette smeared with bright paint, brushes in a jar and a small easel",
   "a wooden upright piano with the lid open and sheet music standing on the music rest",
   "a row of desktop computers with keyboards on long desks in a school computer lab",
 ],
 "exams": [
   "an open school exercise book on a wooden desk with a pen resting on the page, warm desk lamp light",
   "rows of single desks spaced out in a large exam hall, students seated and writing",
   "a teacher's hands marking a stack of test papers with a red pen, ticks and scores in the margin",
   ("a Chinese student studying late at a desk surrounded by open books, highlighters and handwritten notes, lamp glowing", "people"),
   # "weekly timetable grid" alone came back as a month calendar full of dates —
   # coloured subject blocks are what separates a timetable from a calendar.
   ("a weekly class schedule chart taped to a classroom wall, a grid of brightly "
    "coloured subject blocks in rows and columns", "scene"),
   "a thick hardback dictionary lying open on a desk with a magnifying glass resting on the page",
   ("a happy Chinese graduate in a black cap and gown throwing the mortarboard high into the air outdoors", "people"),
   "a shining gold trophy standing beside a rolled certificate tied with a red ribbon rosette",
   ("a Chinese teacher standing at the front of a classroom teaching a room of attentive seated Chinese students", "people"),
   ("Chinese students streaming cheerfully out of a classroom doorway into a bright corridor at the end of a lesson", "people"),
   ("one empty chair and empty desk in the middle of a classroom full of seated Chinese students", "people"),
   ("Chinese students with backpacks walking in through a school gate on the first bright morning of term", "people"),
 ],
}

STORIES = {
 "pack_bts_story_first":  "a young student in school uniform with a backpack arriving at an open school gate on a bright first morning of term, other students walking in behind",
 "pack_bts_story_exam":   "a teenage student revising alone at a desk in an empty classroom in the late afternoon, textbooks and handwritten notes spread out",
 "pack_bts_story_sports": "a school sports day on an outdoor running track, a student running the final lap with classmates cheering from the side",
}

SEED = 91000          # fresh block; hearts-feelings used 90100+
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
            # A prompt is either a bare string (object style) or (prompt, style)
            prompt, style = p if isinstance(p, tuple) else (p, "object")
            if deck in want:
                jobs.append((f"{deck}/{i}",
                             os.path.join(here, "images", "flashcards", deck, f"{i}.jpg"),
                             prompt + STYLES[style], SEED + n * 13, 1024, 1024, 640))
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
