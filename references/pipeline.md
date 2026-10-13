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

## Stage 1 — Research (no gate, report briefly)

- **Reference video given?** Run `scripts/tools/analyze_reference.py ref.mp4 research/ref/` and read every
  sheet. Write `research/ANALYSIS.md` covering spec, shot list with frame ranges, the continuity element,
  type, palette, how each morph is built, and the audio structure (onsets, silences, the logo chord). Use
  `scripts/engine/examples/x_recreate_ANALYSIS.md` as a model. Study it, then design something of your own:
  borrow techniques, never the exact design.
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
Recommend one and say why. Use AskUserQuestion; put the concept texts in the message above it.

## Stage 3 — Storyboard + style frames (gate: go / changes)

- Write `DIRECTION.md` with the beat table in **frames** (60 fps; a 112.5 BPM grid = 32 f per beat, 8 f per 16th).
- Scaffold the project (`new_project.sh`), build 4–6 key frames *in the real engine*, not as mock-ups, so
  what the user approves is what renders. Send a contact sheet (SendUserFile) or a small Artifact.
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

Full-length render at 0.4 scale with no motion blur (about 10 s), encoded with the temp mix. Send it. Ask for notes on pacing,
copy and any beat they'd swap. Also run your own frame-by-frame review of every transition first. The
user should never be the one to find a broken morph.

## Stage 6 — Final

- Full-res `--sub 4` render (about 30 s for 900 frames, 3D included), `pop_detect.py`, look at the spikes.
- Final mix: levels, breath before the logo, loudness about -15.5 RMS proxy and -1 dBFS ceiling.
- `encode.sh` gives the master (CRF 14) and the `_share` copy. Check the duration and that the last frame is the logo.
- Deliver with SendUserFile (render), plus 2–4 lines: what's in it, length/format, what you'd try next.
- Save project memory (what was made, where, reusable bits) and a feedback memory for any user correction.
