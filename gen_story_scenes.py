#!/usr/bin/env python3
"""Per-sentence story illustrations for every pack that shipped without them.

  images/<cover>_s<n>.jpg   760x520, one per sentence, 0-based

The reader derives the path from the story's cover URL - sentenceImageFor() in
index.html turns .../foo.jpg into .../foo_s<n>.jpg and falls back to the cover
when the file 404s - so nothing in the pack JSON changes: the files simply have
to exist. They never did for the packs below, so all 22 of these stories showed
one picture repeated for every sentence (Alex, 7 Sep). stories-vol-1..7 already
have theirs; chinese-medicine has its own in gen_chinese_medicine.py.

    python3 gen_story_scenes.py                     # everything missing (118)
    python3 gen_story_scenes.py chengyu-idioms      # one pack
    python3 gen_story_scenes.py pack_bts_story_exam # one story
    python3 gen_story_scenes.py --force poem_minnong_s2   # redo one frame

Existing files are skipped, so a changed prompt or seed needs --force.

House rules carried over from the pack generators:
  - no hanzi, ever: Flux garbles them and the sentence is shown as text anyway;
    the same clause keeps invented Latin scribble off notebooks and shop signs
  - recurring people are described identically in every frame of a story,
    otherwise each sentence casts a different actor
  - things Flux mis-draws get a PHYSICAL description, not their name: a guqin
    becomes "a long flat narrow zither with seven silk strings, not a guitar",
    the same way the acupuncture needles had to stop being called needles
  - scenes are CENTRED. The story CARD leaves its left third clear for the title
    overlay, but a scene fills the reader's hero header, which is cropped
    centre/cover, and the older stories-vol scenes are all centre-weighted.
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/.claude/scripts/imagegen"))
from comfy_gen import generate

# Contemporary photo look - matches the story cards of these packs.
PHOTO = (", photorealistic photograph, natural realistic lighting, shallow "
         "depth of field, candid documentary style, contemporary China, "
         "subject centred in the frame, no text, no letters, no writing, "
         "no watermark")

# Night variant: the plain photo style washes fireflies out to nothing.
NIGHT = (", photorealistic night photograph, long exposure, deep blue darkness "
         "with small warm glowing lights, natural moonlight, subject centred "
         "in the frame, no text, no letters, no writing, no watermark")

# Macro variant for small living things: a studio background would turn them
# into pinned specimens (the lesson from the Bugs & Butterflies cards).
MACRO = (", extreme macro photograph, sharp focus on the creature, real "
         "softly blurred natural background, natural daylight, subject centred "
         "in the frame, no text, no letters, no writing, no watermark")

# The fables and the poems are painted, not photographed - their story cards
# are ink-and-wash, so their scenes have to be as well.
INK = (", traditional Chinese ink and wash painting, xieyi brushwork on rice "
       "paper, soft grey washes with muted earth tones, delicate line work, "
       "ancient China, paper texture, no text, no letters, no calligraphy, "
       "no seal, no signature, no watermark")

# ---------------------------------------------------------------- characters
# Described the same way in every frame they appear in.
BTS_GIRL = ("a Chinese primary school girl about ten years old with a short "
            "bob and a red neckerchief, in a blue and white tracksuit school "
            "uniform")
BTS_BOY = ("a Chinese teenage boy about fifteen with short black hair, in a "
           "navy and white tracksuit school uniform")
BUG_TEACHER = ("a friendly middle-aged Chinese male teacher in a pale blue "
               "shirt")
HF_MAN = ("a young Chinese man in his early twenties with short black hair, in "
          "a plain grey t-shirt")
HF_BARISTA = ("a young Chinese woman with her hair in a low ponytail, wearing "
              "a dark green barista apron")
HF_DATER = "a young Chinese man in his twenties in a new light blue shirt"
HF_DATE = ("a young Chinese woman in her twenties with long wavy hair, in a "
           "floral summer dress")
HF_STUDENT = ("a Chinese male university student in a grey hoodie with a "
              "backpack")
HF_XIAOMEI = ("a Chinese female university student with straight "
              "shoulder-length hair, in a beige cardigan")
PFC_TRAVELLER = ("a Western traveller in their twenties with short brown hair, "
                 "a grey backpack and a light jacket")
SILKWORM = ("plump cream-white silkworm caterpillars with smooth soft "
            "segmented skin and a small pale horn at the tail, completely "
            "hairless, no bristles, no spines, no hairs, no eye spots")
GUQIN = ("a long flat narrow wooden zither lying across a low table, seven "
         "silk strings running its length, played with both hands, not a "
         "guitar and not a harp")

# ------------------------------------------------------------------- scenes
# key = story cover basename, value = (default style, [prompt per sentence]).
# A frame that needs a different look is written as (prompt, style).
SCENES = {

 # ---------------------------------------------------------- back-to-school
 "pack_bts_story_first": (PHOTO, [
   # 0 today is the first day of the new term
   ("children in blue and white tracksuit uniforms walking in through the open "
    "railings of a Chinese primary school on a bright September morning, seen "
    "from behind at close range, backpacks on their shoulders, parents waving "
    "them off, green trees and a plain painted wall, no signboard, no banner, "
    "no notice board"),
   # 1 new uniform, backpack on
   (BTS_GIRL + " standing in the hallway of a flat, shrugging a new backpack "
    "onto her shoulders and checking herself in a mirror, morning light"),
   # 2 the school bus arrives at eight
   ("a school bus pulled up at the kerb outside a Chinese apartment block, its "
    "door open, " + BTS_GIRL + " stepping up onto the first step, other "
    "children already at the windows"),
   # 3 lots of new classmates in the classroom
   ("a bright primary school classroom full of Chinese children chatting at "
    "wooden desks before the lesson, backpacks on the chair backs, " +
    BTS_GIRL + " sitting down among them"),
   # 4 the teacher writes on the board and the lesson begins
   ("a Chinese teacher standing at a green chalkboard with her back half "
    "turned, chalk in hand, the board out of focus with no readable writing, "
    "rows of pupils watching from their desks"),
 ]),

 "pack_bts_story_exam": (PHOTO, [
   # 0 a maths exam tomorrow morning
   ("a school desk by a classroom window in the late afternoon with an open "
    "maths textbook of geometry diagrams, a ruler, a pair of compasses and a "
    "pencil case, no readable writing, low golden light"),
   # 1 stayed behind after class to revise
   (BTS_BOY + " alone at a desk in an otherwise empty classroom, bent over his "
    "books revising, rows of empty chairs behind him, late afternoon sun "
    "through the windows"),
   # 2 messy notes, written out again
   ("close up of a teenage boy's hands and pen over a fresh exercise book at a "
    "school desk, seen from a low angle so the page is turned away and almost "
    "edge on, a crumpled ball of paper pushed aside, no visible writing"),
   # 3 explaining a question to a classmate, three times over
   (BTS_BOY + " leaning over his exercise book and pointing at a diagram while "
    "another Chinese teenage boy beside him frowns in concentration, two desks "
    "pushed together in a classroom"),
   # 4 explaining it is what made him understand it
   (BTS_BOY + " sitting back in his chair with a sudden delighted look of "
    "understanding, pencil still in hand, his classmate beside him nodding, "
    "warm classroom light"),
   # 5 top of the class the next day
   ("a Chinese teacher handing a marked exam paper back to " + BTS_BOY +
    " at his desk, a single large red tick on the page and no readable "
    "writing, classmates turning round to look, bright morning classroom"),
 ]),

 "pack_bts_story_sports": (PHOTO, [
   # 0 every autumn the school holds a sports day
   ("a Chinese school sports ground on an autumn morning seen from the stand, "
    "a red running track around a green field, students gathering in class "
    "groups, yellow leaves on the trees behind"),
   # 1 no lessons, and the field is packed
   ("a school field packed with Chinese students sitting in class blocks on "
    "small stools along the edge of a red running track, seen low from the "
    "trackside, bright day, no banners, no signboards, no bunting"),
   # 2 signing up for the eight hundred metres
   (BTS_BOY + " standing at a registration table beside the track while a "
    "teacher writes on a clipboard, a plain paper race bib with no writing "
    "lying on the table"),
   # 3 not the fastest, but he never stopped
   (BTS_BOY + " running on the red track in the middle of a race, two runners "
    "a little ahead of him, his face set and determined, motion blur in the "
    "background"),
   # 4 the whole class shouting his name on the last lap
   ("Chinese students crowded at the trackside cheering, hands cupped round "
    "their mouths and arms in the air, a runner passing in motion blur in "
    "front of them"),
   # 5 third place, and the head teacher hands over the certificate
   ("a grey-haired middle-aged Chinese head teacher in a dark jacket handing a "
    "plain cream certificate with no writing to " + BTS_BOY + " beside the "
    "running track, the boy smiling and out of breath, classmates applauding "
    "behind"),
 ]),

 # -------------------------------------------------------- bugs-butterflies
 "pack_bug_story_firefly": (NIGHT, [
   # 0 a summer evening, walking out to the fields
   ("two Chinese children, a girl of about twelve and her younger sister, "
    "walking along a narrow path beside paddy fields at dusk, warm summer "
    "haze, distant hills", PHOTO),
   # 1 lots of tiny lights in the grass
   ("tall grass at the edge of a field at night with dozens of tiny warm "
    "yellow-green lights glowing among the stems"),
   # 2 they are fireflies
   ("a single firefly beetle clinging to a blade of grass at night, its small "
    "dark brown body, six legs and folded wing cases clearly visible, the tip "
    "of its abdomen glowing yellow-green, everything else in soft darkness"),
   # 3 flying up like stars in the sky
   ("dozens of fireflies rising over a dark field on a summer night, their "
    "glowing trails scattered like stars, a starry sky and the silhouette of "
    "trees behind"),
   # 4 they watched a long time and did not catch them
   ("a Chinese girl of about twelve and her younger sister sitting together on "
    "the grass at night in summer clothes, both smiling in wonder, their faces "
    "lit softly by drifting fireflies, hands resting in their laps"),
 ]),

 "pack_bug_story_bee": (PHOTO, [
   # 0 a bee flies in through the window
   ("a honeybee in flight just inside an open classroom window, sunlight "
    "behind it, rows of Chinese pupils at desks blurred in the background"),
   # 1 everyone nervous, afraid of being stung
   ("Chinese schoolchildren at their desks leaning back and away, hands raised "
    "to shield their heads, worried and giggling faces, a classroom"),
   # 2 the teacher: do not move, it is only looking for flowers
   (BUG_TEACHER + " standing calmly at the front of a classroom with one palm "
    "raised in a steadying gesture, speaking to the class, chalkboard behind "
    "with no readable writing"),
   # 3 he slowly opens another window
   (BUG_TEACHER + " reaching up to push open a tall classroom window, seen "
    "from the side with both hands on the frame, bright green trees and "
    "sunlight outside, the room dim around the opening"),
   # 4 the bee flies one lap and then out
   ("a honeybee in flight heading out through an open classroom window, wings "
    "blurred with motion, the sunlit garden beyond in soft focus"),
   # 5 it wants the lesson to end even more than you do
   (BUG_TEACHER + " laughing warmly at the front of the classroom, Chinese "
    "pupils at their desks laughing with him, relaxed bright room"),
 ]),

 "pack_bug_story_silkworm": (MACRO, [
   # 0 the science teacher gives everyone a few silkworms
   ("a Chinese science teacher handing a small open cardboard box holding a "
    "few tiny smooth pale silkworms to a schoolchild, other children crowding "
    "round to look, school science room", PHOTO),
   # 1 a paper box, fresh mulberry leaves every day
   ("a child's hands laying fresh green mulberry leaves into a shallow "
    "cardboard box where several " + SILKWORM + " are feeding, seen from "
    "above, daylight on a desk"),
   # 2 growing bigger, white and soft
   ("three or four " + SILKWORM + " feeding side by side on a green mulberry "
    "leaf, close macro, natural light"),
   # 3 they stop eating and begin to spin cocoons
   ("one of the " + SILKWORM + " half hidden inside a loose oval cocoon of "
    "pale yellow silk it has spun in the corner of a cardboard box, a few "
    "silk threads anchoring the cocoon to the cardboard, no spider web"),
   # 4 two weeks later, white moths come out
   ("one furry white silk moth with feathery antennae and folded wings resting "
    "on the cardboard beside the empty papery cocoon it has left, close macro, "
    "soft daylight"),
   # 5 back onto the mulberry tree in the yard
   ("a child's open hand lifting a white silk moth onto a mulberry branch in a "
    "sunlit courtyard, green leaves all round", PHOTO),
 ]),

 # ----------------------------------------------------------- chengyu idioms
 "chengyu_huashe": (INK, [
   # 0 a contest to draw a snake
   ("several men in loose ancient Chinese robes kneeling around low tables in "
    "a courtyard, each holding a brush over a sheet of paper, a large "
    "earthenware wine jar standing between them"),
   # 1 whoever finishes first drinks the wine
   ("a large earthenware wine jar with a wooden ladle resting on a mat in a "
    "courtyard, two men in ancient robes glancing towards it as they paint"),
   # 2 one man finished very quickly
   ("a man in ancient Chinese robes lifting his brush away from a finished "
    "painting of a long snake on paper, sitting back pleased with himself"),
   # 3 bored, he added legs to his snake
   ("a painted sheet of paper on a low table seen from above, a long inked "
    "snake on it with four small clumsy legs added along its body, a brush in "
    "a hand in a wide ancient sleeve at the edge of the frame"),
   # 4 snakes have no legs, you lose
   ("men in ancient Chinese robes pointing and laughing at a sheet of paper "
    "held up between them, the painting on it a plain long snake with four "
    "small clumsy legs added to it and no wings and no horns, one of them "
    "lifting the earthenware wine jar away"),
   # 5 doing too much ruins things
   ("a man in ancient Chinese robes sitting alone and empty-handed on a mat in "
    "a courtyard beside his painting of a legged snake, the others behind him "
    "drinking from small earthenware cups around the wine jar, no glassware "
    "and no table, evening"),
 ]),

 "chengyu_shouzhu": (INK, [
   # 0 a farmer working in his field
   ("an old Chinese farmer in a coarse robe and cloth head wrap hoeing a green "
    "field, a broad tree stump at the field edge, low mountains in the mist "
    "behind"),
   # 1 a rabbit runs into the stump and dies
   ("a brown hare lying still at the foot of a broad tree stump at the edge of "
    "a field, the grass bent around it"),
   # 2 delighted with a free rabbit
   ("an old Chinese farmer in a coarse robe holding up a brown hare by the "
    "ears with a delighted grin, his hoe tucked under his arm, field behind"),
   # 3 he stopped farming and waited by the stump every day
   ("an old Chinese farmer sitting with his back against a tree stump, his hoe "
    "lying idle in the grass beside him, watching the empty field, long "
    "afternoon shadows"),
   # 4 no more rabbits came and the field went to waste
   ("a neglected field overgrown with tall weeds, an old Chinese farmer "
    "slumped against the tree stump at its edge, thin and disheartened, grey "
    "washes"),
   # 5 luck is no substitute for effort
   ("an empty tree stump in a field of tall weeds at dusk, nobody there, a "
    "hoe abandoned in the grass, mist over the distant hills"),
 ]),

 "chengyu_jingwa": (INK, [
   # 0 a frog lived at the bottom of a well
   ("a small green frog sitting on wet mossy stones at the bottom of an old "
    "stone well, dim light falling on the water"),
   # 1 the sky looked only as big as the mouth of the well
   ("the view straight up from the bottom of a stone well, the round mouth of "
    "the well a small pale circle of sky far above, dark stone walls all "
    "round"),
   # 2 it thought its world was the biggest and best
   ("a green frog puffed up proudly on a stone at the bottom of a well, its "
    "throat swelled as it croaks, ripples in the shallow water"),
   # 3 a sea turtle told it the ocean is boundless
   ("a large old sea turtle resting at the stone rim of a well, its head "
    "lowered towards a small green frog far below in the shaft"),
   # 4 only then did the frog see how little it had seen
   ("a small green frog perched on the stone rim of a well, looking out and "
    "up, the land opening away below it, wide misty washes"),
   # 5 a narrow outlook
   ("a tiny frog on a rock in the foreground facing an immense misty ocean "
    "with rolling waves stretching to the horizon, vast empty washes"),
 ]),

 "chengyu_wangyang": (INK, [
   # 0 a herdsman kept many sheep
   ("a Chinese herdsman in a coarse robe standing beside a rough wooden pen "
    "full of sheep on a grassy slope, low hills behind"),
   # 1 a hole in the pen, and one sheep escapes
   ("a broken gap in a rough wooden sheep pen with one sheep slipping out "
    "through it into the grass, the rest of the flock behind the fence"),
   # 2 a neighbour urged him to mend it; he would not listen
   ("a neighbour in ancient Chinese dress gesturing urgently at a broken fence "
    "while the herdsman turns away with a dismissive wave of his hand"),
   # 3 the next day another sheep was gone
   ("a Chinese herdsman standing in his pen counting his sheep with a worried "
    "face, a gap in the flock, the broken fence behind him"),
   # 4 he hurried to mend the pen
   ("a Chinese herdsman kneeling to mend a broken wooden sheep pen, weaving "
    "branches and driving a stake into the ground, the sheep watching him"),
   # 5 never too late to put it right
   ("a mended wooden sheep pen at dusk with the whole flock safe inside, the "
    "herdsman sitting on a rock nearby at rest, soft evening washes"),
 ]),

 "chengyu_duiniu": (INK, [
   # 0 a musician who played beautifully
   ("a scholar musician in flowing ancient Chinese robes seated at " + GUQIN +
    ", playing in a garden pavilion, listeners seated on mats nearby"),
   # 1 one day he played facing a cow
   ("a scholar musician in ancient robes seated at " + GUQIN + " set on a low "
    "table in a green field, facing a large water buffalo standing a few paces "
    "away"),
   # 2 he played his most beautiful piece
   ("a scholar musician in ancient robes with his eyes closed and both hands "
    "on the silk strings of " + GUQIN + ", absorbed in playing, blossom petals "
    "drifting past"),
   # 3 the cow just kept eating grass
   ("a large water buffalo with its head down grazing steadily on grass, tail "
    "flicking, the seated musician and his long zither small and ignored in "
    "the background"),
   # 4 however good the music, the cow could not understand it
   ("a scholar musician in ancient robes seated at " + GUQIN + ", his hands "
    "lifted from the strings, looking at a water buffalo that has turned its "
    "head away and is still chewing"),
   # 5 effort wasted on the wrong audience
   ("a scholar musician in ancient robes walking away along a field path at "
    "dusk, carrying a long flat narrow zither wrapped in plain cloth "
    "horizontally under one arm, the water buffalo grazing on behind him, "
    "quiet grey washes"),
 ]),

 # ---------------------------------------------------------- hearts-feelings
 "pack_hf_story_cafe": (PHOTO, [
   # 0 I buy coffee at the cafe every day
   (HF_MAN + " walking in through the glass door of a small modern coffee shop "
    "in a Chinese city, morning light, a wooden counter beyond"),
   # 1 there is a girl in the cafe
   (HF_BARISTA + " working behind the counter of a small coffee shop, steaming "
    "milk at an espresso machine, warm interior"),
   # 2 her smile is very pretty
   ("a warm close portrait of " + HF_BARISTA + " smiling as she looks up from "
    "the counter, soft window light on her face"),
   # 3 I look at her and she looks at me
   (HF_MAN + " standing at the counter of a coffee shop while " + HF_BARISTA +
    " hands him a cup, the two of them catching each other's eye"),
   # 4 today she smiled at me and I am very happy
   (HF_MAN + " stepping out onto a sunny street with a takeaway coffee cup, "
    "grinning to himself, the cafe window behind him"),
 ]),

 "pack_hf_story_date": (PHOTO, [
   # 0 tonight I have a date and I am very nervous
   (HF_DATER + " sitting on the edge of his bed in a small flat, dressed up "
    "and ready far too early, hands clasped, nervous, evening light"),
   # 1 new clothes, and a rose
   (HF_DATER + " checking himself in a hallway mirror, a single red rose held "
    "in one hand, a jacket over his arm"),
   # 2 when she arrived my heart was beating fast
   (HF_DATE + " arriving at the doorway of a small warm restaurant while " +
    HF_DATER + " rises from the table to greet her, evening"),
   # 3 we ate together and talked a lot
   (HF_DATE + " and " + HF_DATER + " eating together at a small restaurant "
    "table with several shared dishes between them, both mid-conversation, "
    "warm light, other diners blurred behind"),
   # 4 when she laughed I forgot my nerves
   (HF_DATE + " laughing with her head tilted back at a restaurant table while "
    + HF_DATER + " laughs with her, a candle between them"),
   # 5 I hope there is a second date
   (HF_DATE + " and " + HF_DATER + " saying goodbye on a lit city street in "
    "the evening, half turned away from each other and both still smiling, "
    "warm shopfront lights behind"),
 ]),

 "pack_hf_story_confess": (PHOTO, [
   # 0 university classmates for two years
   (HF_STUDENT + " and " + HF_XIAOMEI + " walking out of a lecture hall among "
    "other Chinese students, campus corridor, daylight"),
   # 1 I always want to speak but never dare
   (HF_STUDENT + " standing a few steps away in a university corridor watching "
    + HF_XIAOMEI + " talk to friends, his mouth half open, hesitating"),
   # 2 my friend: she is leaving for Beijing
   ("two Chinese male university students sitting on a campus bench under "
    "trees, one talking earnestly to the other who stares at the ground, "
    "autumn afternoon"),
   # 3 last night I waited at the library entrance
   (HF_STUDENT + " standing alone under the lit entrance of a university "
    "library at night, hands in his hoodie pocket, cold air"),
   # 4 a deep breath: I like you, and have for a long time
   (HF_STUDENT + " standing a polite step apart from " + HF_XIAOMEI +
    " outside a library at night and speaking to her, one hand pressed flat "
    "against his own chest, not touching her, warm lamplight, both serious"),
   # 5 she blushed and said quietly: me too
   ("a close warm portrait of " + HF_XIAOMEI + " smiling shyly and looking "
    "down, cheeks flushed, night lamplight behind her"),
 ]),

 # -------------------------------------------------------- prepare-for-china
 "pack_pfc_story_before": (PHOTO, [
   # 0 next month I am travelling to China
   (PFC_TRAVELLER + " at a table at home with an open empty suitcase, a "
    "guidebook and folded clothes around it, planning the trip, daylight"),
   # 1 check the passport, buy insurance
   ("close view of a traveller's hands holding a dark passport above a laptop "
    "on a kitchen table, the screen a soft glare with nothing readable"),
   # 2 a friend: your phone matters more than your wallet in China
   ("two friends talking in a kitchen, one holding a smartphone up in one hand "
    "while a closed leather wallet lies forgotten on the table, warm daylight"),
   # 3 so I download the payment apps first
   ("close view of a thumb tapping the screen of a smartphone showing a grid "
    "of plain colourful blank app squares, no logos and no readable text, held "
    "over a kitchen table"),
   # 4 and I pack an adapter plug
   ("a white travel adapter plug and a coiled phone charger tucked into the "
    "corner of a packed open suitcase, seen from above"),
 ]),

 "pack_pfc_story_arrive": (PHOTO, [
   # 0 the plane lands, immigration first
   (PFC_TRAVELLER + " walking down a wide bright airport arrivals corridor "
    "towards a row of immigration booths, other passengers ahead, no "
    "signboards and no hanging signs"),
   # 1 the officer looks at my passport and asks where I am staying
   ("a uniformed Chinese immigration officer behind a glass booth checking a "
    "passport and speaking, a traveller seen from behind at the counter"),
   # 2 through customs, a SIM card at the airport
   ("a Chinese assistant at a small airport phone counter handing a tiny SIM "
    "card in a plastic holder across to " + PFC_TRAVELLER),
   # 3 only with a mobile number can I pay by phone
   (PFC_TRAVELLER + " sitting on a bench in an airport arrivals hall setting "
    "up a smartphone, backpack beside them, luggage trolleys passing behind"),
   # 4 buying water and scanning the code
   ("a traveller's hand holding a smartphone up to a small square black and "
    "white scan code on the counter of a Chinese convenience store, a bottle "
    "of water beside it, shelves behind"),
   # 5 paid in one second, so convenient
   (PFC_TRAVELLER + " smiling with the phone still in one hand as a shop "
    "assistant hands over a bottle of water, bright convenience store"),
 ]),

 "pack_pfc_story_around": (PHOTO, [
   # 0 a time-honoured old restaurant for breakfast
   ("the frontage of a traditional old Chinese breakfast restaurant early in "
    "the morning, stacked bamboo steamer baskets releasing steam by the door, "
    "a plain red shopfront, no signboard and no banner, a few customers on "
    "stools"),
   # 1 finding the best-rated place nearby
   (PFC_TRAVELLER + " sitting at a small table over a bowl of noodles looking "
    "at a smartphone, the screen a soft glare, a busy breakfast place around "
    "them"),
   # 2 opening the map to see how to get there
   (PFC_TRAVELLER + " standing on a city street corner holding a smartphone up "
    "and glancing along the road, traffic and shopfronts behind, daylight"),
   # 3 a bit far, so I call a car
   ("a small car pulling up at the kerb of a Chinese city street beside " +
    PFC_TRAVELLER + " who is stepping forward with a phone in hand"),
   # 4 three minutes later, watching the city go by
   ("the view from the back seat of a car, a traveller looking out of the side "
    "window at Chinese city streets sliding past, the driver's shoulder and "
    "the mirror in the foreground"),
   # 5 out all day and never used cash
   (PFC_TRAVELLER + " on a busy lit street food lane in the evening holding a "
    "phone up to pay at a stall, neon glow and steam, a closed wallet still in "
    "their jacket pocket"),
 ]),

 # ------------------------------------------------------------- tang poetry
 "poem_jingyesi": (INK, [
   # 0 before my bed, the bright moonlight
   ("the inside of a simple ancient Chinese bedchamber at night, a low wooden "
    "bed and a lattice window, a bright patch of moonlight lying across the "
    "floor"),
   # 1 I wonder if it is frost on the ground
   ("close view of a pale silvery patch of moonlight on a stone floor beside "
    "the edge of a wooden bed, so cold and white it might be frost"),
   # 2 I raise my head and gaze at the bright moon
   ("a figure in long ancient Chinese robes standing at an open lattice window "
    "with head tilted back, a large full moon high in the night sky"),
   # 3 I lower my head and think of home
   ("a figure in long ancient Chinese robes standing with head bowed in a dim "
    "room, a distant village and mountains suggested in mist beyond the "
    "window"),
 ]),

 "poem_chunxiao": (INK, [
   # 0 in spring I sleep, unaware of the dawn
   ("a sleeping figure under a quilt on a low wooden bed in a small ancient "
    "Chinese room, pale dawn light coming through a lattice window"),
   # 1 everywhere I hear the birds singing
   ("small birds perched and singing on a flowering branch just outside a "
    "wooden lattice window, soft morning light"),
   # 2 last night came the sound of wind and rain
   ("blossoming branches bent by wind and slanting rain in the dark, loose wet "
    "ink washes, a dim courtyard wall behind"),
   # 3 how many blossoms have fallen, who knows
   ("a courtyard floor of grey flagstones scattered with fallen pink blossom "
    "petals after rain, shallow puddles, the emptied branch above"),
 ]),

 "poem_dengguanque": (INK, [
   # 0 the white sun sinks behind the mountains
   ("a pale white sun sinking behind layered ridges of mountains, wide misty "
    "washes, a vast quiet landscape"),
   # 1 the Yellow River flows on into the sea
   ("a broad ochre river winding away across a wide plain towards a distant "
    "sea, seen from high above, misty horizon"),
   # 2 to take in a view of a thousand miles
   ("a scholar in ancient Chinese robes standing at the wooden railing of a "
    "tower balcony, seen from behind, gazing out over an immense river "
    "landscape"),
   # 3 climb one more storey higher
   ("a scholar in ancient Chinese robes climbing a narrow wooden staircase "
    "inside a multi-storey ancient tower, bright light coming from the storey "
    "above"),
 ]),

 "poem_minnong": (INK, [
   # 0 hoeing the grain in the noonday sun
   ("a Chinese farmer in a coarse robe and a wide straw hat bent over a hoe in "
    "a green millet field under a high white midday sun"),
   # 1 sweat drips on the soil beneath the crop
   ("a Chinese farmer in a wide straw hat bent low over his hoe among green "
    "stalks, seen from the side, beads of sweat running down his temple and "
    "falling towards the dark soil below him"),
   # 2 who realises that the food on the plate
   ("a plain bowl heaped with steamed white rice and a pair of chopsticks on a "
    "simple wooden table, a quiet still life"),
   # 3 grain by grain, is all hard toil
   ("a weathered open hand cupping a small heap of husked grain, a hoed field "
    "and a bent working figure suggested in the mist behind"),
 ]),

 "poem_xiangsi": (INK, [
   # 0 red beans grow in the southern land
   ("a slender branch of a red bean tree hung with small bright scarlet seeds, "
    "a misty southern Chinese landscape of low hills behind, a single touch of "
    "red in a grey wash"),
   # 1 when spring comes they put out new shoots
   ("fresh green shoots opening along a thin bare branch in spring mist, small "
    "red seeds still clinging further along it"),
   # 2 I wish you would gather many
   ("a hand in a wide ancient sleeve picking bright red seeds from a branch "
    "into a small cloth pouch"),
   # 3 for this thing most embodies longing
   ("a few bright red beans resting in an open palm beside a window, a figure "
    "in ancient robes looking out at distant misty hills"),
 ]),
}

# Which pack each story belongs to, so a pack name can be given on the command
# line. Taken from packs/*.json when this was written.
PACKS = {
 "back-to-school":    ["pack_bts_story_first", "pack_bts_story_exam",
                       "pack_bts_story_sports"],
 "bugs-butterflies":  ["pack_bug_story_firefly", "pack_bug_story_bee",
                       "pack_bug_story_silkworm"],
 "chengyu-idioms":    ["chengyu_huashe", "chengyu_shouzhu", "chengyu_jingwa",
                       "chengyu_wangyang", "chengyu_duiniu"],
 "hearts-feelings":   ["pack_hf_story_cafe", "pack_hf_story_date",
                       "pack_hf_story_confess"],
 "prepare-for-china": ["pack_pfc_story_before", "pack_pfc_story_arrive",
                       "pack_pfc_story_around"],
 "tang-poetry":       ["poem_jingyesi", "poem_chunxiao", "poem_dengguanque",
                       "poem_minnong", "poem_xiangsi"],
}

SEED = 96000          # fresh block; chinese-medicine used 94000+
here = os.path.dirname(os.path.abspath(__file__))


def run(label, out, prompt, seed, force=False):
    if os.path.exists(out) and not force:
        print(f"  skip {label} (exists)", flush=True)
        return True
    t0 = time.time()
    try:
        generate(out, prompt, seed, 1216, 832, max_px=760)
        print(f"  OK   {label} ({int(time.time() - t0)}s)", flush=True)
        return True
    except Exception as e:
        print(f"  FAIL {label}: {e}", flush=True)
        return False


def main():
    args = sys.argv[1:]
    force = "--force" in args
    args = [a for a in args if a != "--force"]

    wanted = set()
    for a in args:
        wanted.update(PACKS.get(a, [a]))       # a pack, a story, or one frame

    jobs = []
    n = 0
    for story, (style, prompts) in SCENES.items():
        for i, p in enumerate(prompts):
            prompt, st = p if isinstance(p, tuple) else (p, style)
            name = f"{story}_s{i}"
            if not wanted or story in wanted or name in wanted:
                jobs.append((name, os.path.join(here, "images", name + ".jpg"),
                             prompt + st, SEED + n * 13))
            n += 1

    print(f"Generating {len(jobs)} images...", flush=True)
    ok, fail = 0, []
    for i, (label, out, prompt, seed) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}]", flush=True)
        if run(label, out, prompt, seed, force):
            ok += 1
        else:
            fail.append(label)
    print(f"\nDONE: {ok} ok, {len(fail)} failed: {fail}", flush=True)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
