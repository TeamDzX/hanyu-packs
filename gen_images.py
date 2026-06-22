#!/usr/bin/env python3
"""Generate card images for all pack stories -> images/<story-id>.jpg (web-sized)."""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/.claude/scripts/imagegen"))
from comfy_gen import generate

STYLE = (", photorealistic photograph, natural realistic lighting, shallow depth of field, "
         "candid documentary style, contemporary China, main subject placed on the RIGHT side "
         "of the frame, simple uncluttered out-of-focus space on the LEFT third, "
         "no text, no letters, no watermark")

STORIES = {
 # stories-vol-1
 "pack_story_hsk1":        "a sunny city park with people strolling and relaxing on a beautiful day, green trees and a lake",
 "pack_story_hsk2":        "a young person packing a suitcase excitedly planning a weekend trip, travel mood",
 "pack_story_hsk3":        "a traveler running along a railway station platform, train about to depart, hurried motion",
 # stories-vol-2
 "pack2_story_seasons":    "a beautiful landscape blending the four seasons, blossoms and snow and autumn leaves",
 "pack2_story_weather":    "a person with an umbrella walking in soft rain on a glistening city street",
 "pack2_story_holiday":    "Chinese New Year celebration with red lanterns, festive decorations and a family dinner",
 "pack2_story_school":     "a big beautiful school campus with students walking to class on a bright morning",
 "pack2_story_work":       "a young professional working at a desk in a modern company office",
 # stories-vol-3
 "pack3_story_hobbies":    "a cozy corner with hobby items - a guitar, paint brushes, books and a camera, warm light",
 "pack3_story_cooking":    "a person cooking dinner at home in a warm kitchen, steam rising from a wok",
 "pack3_story_doctor":     "a caring doctor consulting a patient in a bright modern clinic",
 "pack3_story_phone":      "a person absorbed in their smartphone in everyday life, screen softly glowing",
 "pack3_story_flight":     "an excited traveler at an airport gate watching an airplane through large windows",
 # stories-vol-4
 "pack4_story_pet":        "an adorable little cat being petted at home, cozy living room, affectionate moment",
 "pack4_story_directions": "a visitor asking a friendly local for directions on a city street, pointing the way",
 "pack4_story_bank":       "a modern bank interior with a person being helped at a service counter",
 "pack4_story_midautumn":  "Mid-Autumn Festival scene with mooncakes, tea and glowing lanterns under a full moon",
 "pack4_story_interview":  "a confident young person in business attire at a job interview, modern office meeting room",
 # stories-vol-5
 "pack5_story_clothes":    "a person browsing colourful clothes on racks in a bright fashion store, holding up a red shirt",
 "pack5_story_post":       "a person handing a letter across the counter at a post office, parcels and pigeonholes behind",
 "pack5_story_movie":      "friends watching a film in a darkened cinema, glowing screen light and a tub of popcorn",
 "pack5_story_haircut":    "a customer getting a fresh haircut in a modern barbershop, barber with scissors and comb",
 "pack5_story_rent":       "a happy young person holding keys in the doorway of a new empty apartment, moving boxes nearby",
 # stories-vol-6
 "pack6_story_coffee":     "a cozy coffee shop with a person enjoying a hot coffee by a sunny window, latte art and warm tones",
 "pack6_story_subway":     "a modern subway train arriving at a clean bright station platform, commuters waiting",
 "pack6_story_library":    "a bright library interior with tall bookshelves and a person reading at a desk",
 "pack6_story_beach":      "a beautiful sunny beach with blue sea and golden sand, a family playing by the water",
 "pack6_story_drive":      "a learner driver behind the wheel of a car with an instructor beside, driving school lesson",
}

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    items = list(STORIES.items()); ok=0; fail=[]
    for i,(sid,p) in enumerate(items):
        out = os.path.join(here, "images", sid + ".jpg")
        t0=time.time()
        try:
            generate(out, p+STYLE, 95000+i*7, 1216, 832, max_px=520); ok+=1
            print(f"[{i+1}/{len(items)}] OK {sid} ({int(time.time()-t0)}s)", flush=True)
        except Exception as e:
            fail.append(sid); print(f"[{i+1}/{len(items)}] FAIL {sid}: {e}", flush=True)
    print(f"\nDONE: {ok} ok, {len(fail)} failed: {fail}", flush=True)

if __name__=="__main__": main()
