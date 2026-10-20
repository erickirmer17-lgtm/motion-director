# Pipeline — stage by stage

## Stage 0 — Intake (one message, then go)

Restate the brief in one paragraph: the idea, the line or message, the audience, the mood words the user
used ("historic-futuristic, clean, fast"), and the format. Defaults are 9:16, 1080×1920, 60 fps, 15 s,
ending on the brand. Ask only what changes the work:
- **Budget** (always): "How much do you want to spend on generation for this? Rough costs: GPT-Image-2 is about
  600–700 Magnific credits per image, background removal 3 cr, ElevenLabs music/SFX is cheap, video
  generation is the big one and I'll ask before each batch." Check `account_balance` first and quote it.
- Format only if it isn't implied. Brand/logo only if it's not obvious.
Mention reusable things you'll draw on: last week's assets (e.g. the robot-hand renders), the SFX library, fonts.

Then write the **Brief** block of `DIRECTION.md` (the template has it) before any creative work:
- **Remember:** the one sentence the viewer should leave with. Every beat is judged against it.
- **Facts vs choices.** Facts are locked and must be real: logo file, product screens, names, numbers,
  claims. Choices are yours: camera, motion, transitions, copy rhythm, sound. You may propose a stronger
  opening; you may not redraw the logo, mock a dashboard or invent a metric.
- **Unacceptable:** what would sink it (invented UI, a GPT-redrawn logo, unreadable copy, the default demo look).
- **A missing fact is a blocker, not an invitation.** If the film needs a real asset you don't have, ask for
  it or capture it from the real product (built-in browser screenshots of the live site); never paint a
  convincing stand-in. An unclear reference gets a question or one small test frame, not a full render.
- **Pasted spec?** A long `<inputs> <direction> <structure> <build> <gotchas> <start>` prompt is a measured
  recreation brief: follow `references/measured-recreation.md`, ask its inputs, honour its `<start>` stills gate.
- **Vibe brief?** A one-liner ("go all out", "insane product video") leaves every decision to the safest default,
  and hundreds of people get sibling films from it. Turn it into a production brief first: one sentence to
  remember, audience, formats, real assets, hard lines, deliverables. A product URL + "use the real screens,
  logo and assets" + "must have music" is the minimum that changes the result.

## Stage 1 — Research (no gate, report briefly)

- **Reference video given?** Run `scripts/tools/analyze_reference.py ref.mp4 research/ref/` and read every
  sheet. Write `research/ANALYSIS.md` covering spec, shot list with frame ranges, the continuity element,
  type, palette, how each morph is built, and the audio structure (onsets, silences, the logo chord). Use
  `scripts/engine/examples/x_recreate_ANALYSIS.md` as a model. Study it, then design something of your own:
  borrow techniques, never the exact design.
- **Style guide** (into `DIRECTION.md`, from the reference or the brand): sampled hex values (not "premium"),
  type family/width/weight/scale, where the eye goes first, **pacing as a number** (mean frames between
  meaningful changes; from `cuts.txt` when there's a reference), the motion vocabulary (snap, glide,
  overshoot, cut, hold), texture, and a **don't copy** list (subjects, logos, copy, product imagery).
- **Product films:** capture the exact screens you intend to animate from the real product into `assets/raw/`
  and show them as a contact sheet. The user approves that asset list before production.
- **No reference given?** Pull one: the analysed pro library in `10_October/motion_refs/` (each folder has
  `ANALYSIS.md` with shot list, transitions, palette, motion laws and engine recipes; `INDEX.md` lists them),
  whatships.com (launch videos posted on X), prompt-motion.com / promptsmotion.com (Claude-made pieces with their
  prompts), gsap.com/showcase, Dribbble motion, competitors' launch films. Name the style (`references/motion-vocabulary.md`)
  rather than describing it. Take the grammar, never the subjects, logos or copy.
- **Launch-film numbers** (measured on top launch films; use as defaults, not rules): median shot 1.46 s, the
  picture changes every ~0.7 s, first visible change by 0.1 s, product on screen by 2.8 s, a 1–4 s lull at ~65 %
  of runtime, the biggest peak at ~82 %, end card ~2.2 s. Launch videos on X: median 50 s, 72 % are 16:9; 11 s
  teasers do well too.
- **Brand study.** Colours, logo SVG (Wikimedia often has it), type, prior campaigns (web search). For
  Claude the lockup is in `assets/brand_claude/` (Crail `#D97757`, ink `#0f0f0d`).
- **Asset pool.** Brainstorm 20–40 candidate subjects that fit the idea, search the archives
  (`commons_search.py`), make contact sheets, pick, then download at standard thumb sizes (`references/assets.md`).

## Stage 2 — Concept (gate: user picks one)

Give 2–3 genuinely different concepts. Each gets:
- logline (1 sentence) and the **organising idea** (what every transition means)
- the copy: key words or line, plus any letter-level morphs (e.g. past→paste, camera→era)
- the look: ground, ink and accents in hex, two typefaces, image treatment
- a 5–9 beat outline with rough seconds
- the sound idea (tempo, textures, the ending)
Find concepts through three lenses: the product's verb made literal, the viewer's pain made visible, a formal
device (one shape that never cuts, the film staged inside a fake editor/UI, a caret that travels through every scene).
Arc: hook → turn → proof → promise → lockup. Test each concept before pitching it:
- **Deletion:** remove the demo beats; does the value still read?
- **Specificity:** would the film be just as true of a simpler product? Then it's generic.
- **Feature word:** would a stranger watching muted use the brief's word for the feature?
Recommend one and say why. Use AskUserQuestion; put the concept texts in the message above it.
Each concept has to beat the default AI demo (centred big text on a gradient, everything fading in, logo at
the end); say in one line what yours does instead.

## Stage 3 — Storyboard + style frames (gate: go / changes)

- With a supplied track, measure it first: `beats.py song.wav --fps 60` → `beats.json` (BPM, phase-refined beats,
  downbeats, hits, dropouts, all as frames). State changes on beats, big moments on downbeats, clicks and whooshes on
  hits, the biggest change on the return after a dropout. With generated music, pick a BPM where a beat is a whole
  number of frames (100 BPM = 36 f, 112.5 = 32 f, 120 = 30 f at 60 fps).
- **Write the reads:** list everything the viewer must understand with its start and end frame; no two important
  reads overlap. Copy in fragments of 1–4 words, each held ≥ max(60, 42 + 8 per word) frames at 60 fps; copy on
  ≤ 65 % of frames and ≥ 1.5 s without text in every 10 s; no stretch longer than ~72 f without an event.
- Write `DIRECTION.md` with the beat table in **frames** (60 fps; a 112.5 BPM grid = 32 f per beat, 8 f per 16th).
  Every beat states **what the viewer now knows** and its **entry → exit state**. A beat whose purpose you
  can't state in a few words doesn't go in the render. A list of effects is not a storyboard.
- UI / product films: write the state chain first (e.g. SEARCH → RESULT → DETAIL → ACTION → CONFIRMATION)
  and carry one component through every state, changing size, colour, content and position while staying
  recognisably the same object. Design transitions between known states, not "make the UI dynamic".
- 3D beats built in Blender: block the set with Scenario **Blockout** (paid, quoted) or by hand, build the camera
  with `camera_path`, and check it with `capture_views` before any real render (`references/scenario-blender.md`).
- Fill the style guide's **motion by class** line: micro UI snaps (≤3 f settle, little overshoot), panels
  settle, the camera moves slowly enough to keep orientation, headlines arrive fast then hold. Springs for
  some classes, never all; if everything overshoots, nothing feels precise.
- Scaffold the project (`new_project.sh`), build 4–6 key frames *in the real engine*, not as mock-ups, so
  what the user approves is what renders. Send a contact sheet (SendUserFile) or a small Artifact.
  Run `scripts/tools/seek_check.py engine/` once these render, so hidden state is caught while the scene is small.
- Sound plan: the tempo, the music approach, the 6–10 signature sounds, where the silence goes.

## Stage 4 — Assets (gate: picks; ask before video)

- Sourced: download, then `prep.py` (ink extraction for engravings, B&W photos, cut-outs), then contact sheet.
- Generated stills: write prompts tightly (reference image for identity, "pure seamless white background",
  same lighting). Generate in parallel and show the results. Re-roll only what's off.
- Cut-outs: Magnific `images_remove_background` (3 cr). Check the result: it can fail on painted
  paper (Dürer praying hands came back unchanged).
- Music: 2 ElevenLabs candidates (`elevenlabs.py music`), analyse tempo/structure (see sound-design.md), recommend one.
- Video clips (only if the concept needs footage): list prompts, model, seconds and cost, **ask**, then generate.

## Stage 5 — Rough cut (gate: notes)

Full-length render at 0.4 scale with no motion blur (about 10 s), encoded with the temp mix. Before sending,
run the critic loop in `references/review.md` (evidence pack in `reviews/r01/`, checklist, scorecard, fix the
three largest defects, re-render only those ranges). The user should never be the one to find a broken
morph. Send the cut with the scorecard line and ask for notes on pacing, copy and any beat they'd swap.

## Stage 6 — Final

- Full-res `--sub 4` render (about 30 s for 900 frames, 3D included), `pop_detect.py`, look at the spikes,
  `seek_check.py`, and a final `review.md` pass (`reviews/final/`).
- **Variants are compositions, not crops.** Same story, assets and states; per format the layout changes
  (9:16 fewer elements and a stronger vertical hierarchy, 16:9 more spatial context, 1:1 tighter type and
  shorter holds). Render each with its own `--w --h` and give each its own `beats.jpg` + `safe.jpg`
  (`references/engine.md` → Formats).
- Final mix: levels, breath before the logo, loudness about -15.5 RMS proxy and -1 dBFS ceiling.
- `encode.sh` gives the master (CRF 14), the `_share` copy and `_poster.png` (the last frame, or pass a frame
  number). Check the duration and that the last frame is the logo.
- Deliver with SendUserFile (render): MP4 per variant, poster, and the delivery note from `review.md` (what's
  in it, length/format, **what still needs a human eye**, what you'd try next).
- Save project memory (what was made, where, reusable bits) and a feedback memory for any user correction.

## Long films (music videos, > 60 s)
Build inline under ~45 s; parallel building costs more than it saves there, so keep subagents for critique.
Over ~60 s, split into chapters (one file each, `chapter(name, start, end, shots)`) and brief one builder agent per
chapter, launched together. The lead writes the guide first: a **seams table** (exact framing, world coordinates and
pose at every chapter boundary) and a **world-state table** (the state of every motif per chapter). Builders edit
only their own file and report bugs in shared files instead of fixing them; only the lead edits shared code and
tells running builders when it changes. Check every seam at −2…+2 frames. Budget ~0.5–0.7 M tokens per builder.
Subagents can't write report files: have them return text and save it yourself.

## Resuming
The record of the film lives in files, not in the chat. Update the `**Gate:**` line of `DIRECTION.md` each time a
gate passes. On resume, read `DIRECTION.md`, the newest `reviews/rNN/REVIEW.md` and `out/`, say which gate the
project is at and which artifact is missing, and continue from there.
