#!/usr/bin/env python3
"""Generate every image for the Bugs & Butterflies pack.

  images/flashcards/<deck>/<idx>.jpg   640x640 card photos (card 0 doubles as the
                                       deck cover, cropped 'center 20%' by the
                                       app — so card 0 is always a wide scene)
  images/pack_bug_story_<id>.jpg       760x520 story cards

New lesson for this pack: the house CARD_STYLE's "soft plain studio background"
turns a live insect into a pinned SPECIMEN on white card. Living creatures need
a macro style with a real, softly-blurred natural background instead — the same
family of mistake as the isometric-model sports field in the back-to-school pack.
Second lesson: a card-0 cover must have NO open sky — the 'center 20%' crop is a
band near the top of the frame, so a wide landscape covers the deck in blank blue.

    python3 gen_insects.py            # everything
    python3 gen_insects.py insects    # one deck, or 'stories'
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/.claude/scripts/imagegen"))
from comfy_gen import generate

# House flashcard look — for inanimate OBJECTS only (mosquito coil, honey jar).
CARD_STYLE = (", clean modern photograph, single subject centered, soft plain "
              "studio background, bright even lighting, shallow depth of field, "
              "crisp and colourful, no text, no letters, no watermark")

# Live creatures: a studio background renders them as dead specimens on white.
# Macro photography with a real blurred background keeps them alive and still
# isolates the subject the way the house style wants.
MACRO_STYLE = (", extreme macro nature photograph, single creature sharply in "
               "focus filling the frame, softly blurred natural green "
               "background, bright natural daylight, vivid detail, "
               "no text, no letters, no watermark")

# Wide establishing shots (meadow, anthill) — "studio background" would shrink
# these to a floating diorama.
SCENE_STYLE = (", clean modern nature photograph, real outdoor location, "
               "natural daylight, sharp focus, wide establishing view, "
               "no text, no letters, no watermark")

STYLES = {"object": CARD_STYLE, "macro": MACRO_STYLE, "scene": SCENE_STYLE}

# Story cards leave the left third clear for the title overlay.
STORY_STYLE = (", photorealistic photograph, natural realistic lighting, shallow "
               "depth of field, candid documentary style, contemporary China, "
               "main subject placed on the RIGHT side of the frame, simple "
               "uncluttered out-of-focus space on the LEFT third, "
               "no text, no letters, no watermark")

# Species Flux can confuse are given PHYSICAL descriptions (the erhu lesson):
# cicada vs grasshopper vs cricket all collapse into "generic bug" by name alone.
DECKS = {
 "insects": [
   # Cover card. A wide meadow put all the insects in the SKY, and the app's
   # 'center 20%' cover crop is a horizontal band near the top — i.e. bald blue.
   # Covers need their subject packed into the upper-middle, no open sky.
   ("a close sunlit view of a flower meadow, colourful blooms filling the whole "
    "frame edge to edge with no sky, a large orange and black butterfly resting "
    "with open wings on a flower in the upper middle of the frame, a fat bumblebee "
    "on a bloom beside it, a ladybird and a dragonfly among the flowers", "scene"),
   "a brilliant blue and orange butterfly with wide open patterned wings resting on a pink flower",
   "a fuzzy yellow and black honeybee covered in pollen landing on a purple flower",
   "a single black ant with a narrow waist and long legs walking along a green leaf",
   "a dragonfly with a long slender turquoise body and four transparent veined wings perched on a reed",
   "a round red ladybird beetle with black spots and a glossy domed shell on a bright green leaf",
   "a large glossy iridescent green beetle with hard wing cases and thick legs on tree bark",
   ("a large cicada with a broad blunt head, bulging eyes set wide apart, a stout "
    "dark body and long transparent wings folded in a roof shape over its back, "
    "clinging head-up to the trunk of a tree in bright summer sunlight", "macro"),
   ("a green grasshopper with very long powerful folded back legs and a slender "
    "body sitting on a blade of tall grass", "macro"),
   ("a glossy brown cricket with long thread-like antennae and short wings "
    "standing on dark soil at night", "macro"),
   ("fireflies glowing yellow-green in the warm darkness of a summer field at "
    "dusk, small floating points of light, trees silhouetted behind", "scene"),
   ("a large moth with broad dusty grey-brown patterned wings spread flat, "
    "resting on a wooden wall beside a lamp at night", "macro"),
   "a mosquito with a long thin proboscis and delicate striped legs resting on a green leaf",
   "a common housefly with large red compound eyes and translucent wings standing on a white surface",
   "a shiny reddish-brown cockroach with long antennae and flat oval body on a kitchen tile floor",
 ],
 "minibeasts": [
   ("a large garden orb-weaver spider with a round patterned body and long banded "
    "legs sitting in the exact centre of its round web, the spider large and sharp "
    "in the middle of the frame, green leafy garden softly blurred behind, no sky", "macro"),
   ("a spider web covered in tiny dew drops stretched between two branches, "
    "backlit by early morning sun", "macro"),
   "a garden snail with a spiral brown shell and extended eye stalks gliding across a wet green leaf",
   ("a long thin reddish-pink earthworm with a smooth ringed body stretched out "
    "across dark damp soil, its body slender and string-like, not fat", "macro"),
   ("a plump soft green caterpillar with a ringed segmented body, many small stubby "
    "legs and a small rounded head, chewing a hole in the edge of a green leaf", "macro"),
   ("several white silkworm caterpillars with long soft ringed segmented bodies and "
    "tiny legs, crawling over fresh green mulberry leaves in a shallow round bamboo "
    "tray, seen from above", "macro"),
   "a long reddish-brown centipede with many pairs of legs crawling over a rotting log",
   "a yellow scorpion with raised curved tail and large pincers standing on sand",
   "a bright green praying mantis with triangular head and folded raised front legs on a stem",
   "a wasp with a smooth bright yellow and black striped body and narrow waist on a wooden fence",
   ("pale termites swarming over a piece of rotten wood, close up", "macro"),
   ("dozens of small black tadpoles with round heads and flicking tails swimming "
    "in shallow clear pond water over pebbles", "macro"),
 ],
 "bug-life": [
   ("the wide open wings of a butterfly filling the frame, intricate scales and "
    "veins, iridescent blue and black pattern", "macro"),
   ("close up of an insect's head showing two long thin segmented antennae and "
    "large compound eyes", "macro"),
   ("a golden honeycomb of perfect hexagonal wax cells covered in honeybees, "
    "close up", "macro"),
   "a glass jar of golden honey with a wooden honey dipper resting across the rim",
   ("close up of bright yellow pollen grains coating the yellow stamens at the "
    "centre of an open flower", "macro"),
   ("a silky pale cocoon hanging from a thin twig among green leaves", "macro"),
   ("small white grub-like larvae with soft segmented bodies curled on dark "
    "soil, close up", "macro"),
   ("a cone-shaped anthill of loose earth on the ground with ants swarming over "
    "it, garden soil around", "scene"),
   ("extreme close up of a mosquito perched on the skin of a human forearm, "
    "fine hairs visible", "macro"),
   ("a long line of black ants crawling one behind another along a tree branch", "macro"),
   # Third attempt. "flat spiral ... on a stand" kept standing the coil on its EDGE
   # in the holder. Forcing the camera directly overhead and describing the shape as
   # concentric circles is what finally lays it flat.
   ("a green mosquito repellent incense coil photographed from directly overhead, "
    "the whole spiral lying flat on the surface and seen face-on as flat concentric "
    "green circles winding into the centre, one small metal stand clipped underneath, "
    "the outer tip glowing orange with a thin wisp of smoke, nothing else in the "
    "frame, no sticks, no bowl", "object"),
   ("a white mosquito net hanging over a neatly made bed in a bright bedroom, "
    "net draped from the ceiling", "scene"),
 ],
}

STORIES = {
 "pack_bug_story_firefly":  "two children crouching in tall grass in a dark summer field at dusk watching fireflies glow around them, warm points of light in the air",
 "pack_bug_story_bee":      "a bee flying near an open classroom window while students at their desks turn to look, sunlight streaming in",
 "pack_bug_story_silkworm": "a child at a desk carefully feeding fresh mulberry leaves to white silkworms in a shallow bamboo tray, close and warm",
}

SEED = 92000          # fresh block; back-to-school used 91000+
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
            # A prompt is either a bare string (macro style) or (prompt, style)
            prompt, style = p if isinstance(p, tuple) else (p, "macro")
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
