#!/usr/bin/env bash
# Regenerate the monolithic packs.json catalog from packs/*.json.
# Order here controls the order the app/landing page see the packs in.
set -euo pipefail
cd "$(dirname "$0")"

ORDER=(
  new-hanzi-100
  hsk4-foundations-1
  hsk4-foundations-2
  hsk4-foundations-3
  hsk5-starter
  stories-vol-1
  stories-vol-2
  stories-vol-3
  stories-vol-4
  stories-vol-5
  stories-vol-6
  stories-vol-7
  flashcards-vol-1
  flashcards-vol-2
  flashcards-vol-3
  flashcards-vol-4
  flashcards-vol-5
  hearts-feelings
  street-smart
  tone-master
  parrot-talk
  meet-the-tutor
  business-chinese
  brushstroke
  story-time
  hsk-sprint
  game-on
  internet-slang
  across-china
  sentence-lab
  inventions-innovations
  sages-strategists
  dynasties-landmarks
  great-figures
  treasure-ship-era
  philosophy
  festivals-traditions
  chengyu-idioms
  tang-poetry
  modern-music
  food-everyday-classics
  food-dumplings-dimsum
  food-sichuan
  food-street-breakfast
  food-noodles
  food-plant-based
  manga-everyday-essentials
  manga-out-and-about
  manga-travel
  manga-friends
  manga-doctor
)

FILES=()
for slug in "${ORDER[@]}"; do
  FILES+=("packs/${slug}.json")
done

# Validate every pack first.
for f in "${FILES[@]}"; do
  python3 -c "import json,sys; json.load(open('$f'))" || { echo "Invalid JSON: $f"; exit 1; }
done

GENERATED="$(date +%Y-%m-%d)"
jq -s --arg gen "$GENERATED" '{catalogRevision: 1, generated: $gen, packs: .}' "${FILES[@]}" > packs.json

echo "Built packs.json with $(jq '.packs | length' packs.json) packs."
