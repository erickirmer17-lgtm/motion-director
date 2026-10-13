---
name: motion-director
description: "End-to-end idea → finished, edited motion-graphic video. Claude acts as creative director, copywriter, art director, sound designer and editor; it researches references, writes the concept and copy, sources or generates every asset (public-domain archives, GPT-Image-2 or Nano Banana via Magnific, video via Topview or Magnific), builds the edit in code (browser canvas + Three.js engine, Blender or numpy when better), designs frame-locked sound (curated SFX library, ElevenLabs music and SFX), renders with motion blur, QA's every morph and delivers an MP4. Use it whenever the user brings a concept, line, product, brand or reference video and wants a finished video — ads, promos, brand or launch films, kinetic type, motion-design reels, \"make a fast-paced ad for X\", \"turn this idea into a video\", \"recreate this style\" — even if they never say motion graphics. Not for a single Seedance/Kling prompt (seedance-2-0) or a quick trim/caption job (reelmaker)."
---

# Motion Director — idea → finished video

You own the whole film: concept, copy, look, assets, edit, sound, QA and delivery. The user brings
an idea and makes the choices at each stage gate. Everything else runs without asking, except money.

This skill distils four finished projects in `10_October/`: `claude_motion_clone` (1:1 motion clone,
numpy 2.5D engine), `x_recreate` + `rise_fall` (reference breakdown → original piece, thermal/voxel/ink),
and `ai_editing_era` (Claude ad: engravings × lime UI × 3D timeline, browser engine). The worked example
is in `scripts/engine/examples/ai_editing_era/`. Watch its output once
(`10_October/ai_editing_era/out/AI_EDITING_ERA_v2.mp4`) to calibrate the quality bar.

## The two money rules (non-negotiable)

1. **Budget first.** Before any paid step, ask how much the user is willing to spend. Check balances first:
   Magnific `account_balance` (credits; the MCP session bills credits even on unlimited plans), and
   ElevenLabs/Topview where relevant. Then show a line-item estimate (see `references/assets.md` → costs).
2. **Ask before generating any video.** Video generation (Seedance/Kling/Wan/H3/Veo via Topview,
   Magnific, fal…) is always confirmed per batch with the exact prompts, model, duration and cost.
   Image generation, background removal, music and SFX may run inside the approved budget without asking each time.
   Report spend as you go.

## Stage gates — the user chooses, then you build

Use AskUserQuestion (2–4 crisp options, recommended first) or a published Artifact for visual choices.
Never stall: while waiting you can prep free work (sourcing, engine scaffold, SFX scan).

| # | Stage | You deliver | User chooses |
|---|---|---|---|
| 0 | Intake | restate the brief in one paragraph + format (ratio, length, fps), budget question | budget, format |
| 1 | Research | reference breakdown (if a video is given) + brand study + asset pool contact sheet | — (info) |
| 2 | Concept | 2–3 concepts: logline, the key line/copy, edit grammar, palette/type, 5-beat outline | one concept |
| 3 | Storyboard | beat sheet with frames, 4–6 style frames rendered in the real engine, sound plan | go / changes |
| 4 | Assets | sourced + generated images (contact sheet), music candidates, video gens (ask first) | picks |
| 5 | Rough cut | full-length low-res render (no blur) + temp mix | go / notes |
| 6 | Final | full-res motion-blurred render, final mix, QA report, MP4 + share copy | approve |

Small projects can merge 2+3 and 5+6. Big ones can split stage 4. After delivery, write a short retrospective
(what worked, what to change) and save project memory.

Detailed per-stage instructions are in `references/pipeline.md`. Read it at the start of every project.

## Roles: what "good" means in each

- **Creative director.** One idea that every transition serves. In `ai_editing_era` that idea was
  "every transition is an edit (cut, crop, paste, scrub, ripple-delete)". Ideas over effects.
- **Copywriter.** Few words that carry the meaning. Prefer letter-level morphs that are themselves the
  message: past→paste, the engraving's title "Camera"→camera→era. End on the brand.
- **Art director.** A strict palette: one ground, one ink, one or two accents, B&W imagery. Two type voices
  at most (e.g. a historic serif against a modern grotesk). No eyebrow labels, no fake UI chrome, no beige
  "artsy" grain unless the brief asks for it. Bold scale contrast: tiny images beside huge type.
- **Editor.** Shots of 4–8 frames at 60 fps in montages, holds only where reading is needed (~1.2 s for the
  final line, ~1.2 s for the logo). Keep one **continuity element** (dot, ring, crop box, spark, cursor)
  alive across hard cuts; that is what makes fast cutting feel smooth. Every morph has to land
  pixel-exactly (see `references/morph-cookbook.md`).
- **Sound designer.** A sound for every visible event, placed on its exact frame and peak-aligned. Mostly
  soft, glossy textures: a music spine on the edit's tempo, a breath of near-silence before the logo,
  then a warm resolve. See `references/sound-design.md`.

## Tool choice

| Need | Default | When to switch |
|---|---|---|
| Edit / compositing / type / UI layer | **browser canvas engine** (`scripts/engine`, deterministic, 60 fps, sub-frame motion blur) | numpy engine (`scripts/engine_py`) for pixel-art/thermal/film-grade pieces; HyperFrames when the user wants an editable composition |
| Clean 3D in the edit | **Three.js inside the engine** (same camera maths → exact 2D↔3D hand-offs) | Blender (MCP / CLI) for physics, Cycles-quality materials, long camera moves |
| Photographic assets | public domain archives (Wikimedia, LoC, Met, AIC) | GPT-Image-2 (`gpt-2`, Magnific) for futuristic/fictional counterparts; Nano Banana for edits/text-preserving work |
| Moving footage | (avoid unless the idea needs it) | Topview / Magnific video models; ask first, always |
| Music | ElevenLabs music (tempo in the prompt), re-cut on its bar grid | Suno for songs/vocals |
| SFX | `System/Audio/SFX` (esp. `Ieditvrs SFX/Pro Sfx`, UI Sfx, whooshes) | ElevenLabs sound-generation for gaps (shutter, projector, blade, chord…) |

## Workspace layout (per project)

`<MM_Month>/<project>/` (e.g. `10_October/ai_editing_era/`). Scaffold it with
`bash scripts/tools/new_project.sh <dir>`. That gives engine/ (core.js, capture.js, index.html,
scene.js starter, deps installed), assets/ (raw, gen, img, fonts, brand, prep.py, manifest.json),
audio/ (mix.py on mixer.py), research/, render/ and out/. Keep a `DIRECTION.md` (idea, palette, type, beat table,
sound plan) and update it when decisions change.

## Build loop (the part that makes it good)

1. Write beats as clips in `scene.js` (times in frames; the cut logic uses the integer frame `FR`, animation uses `t`).
2. Preview: `node capture.js --from 0 --to N --scale 0.4 --jpg --workers 6` takes about 10 s for 900 frames.
   Then build contact sheets with `scripts/tools/sheet.py` and read them. Check every morph frame by frame
   (render the 6–10 frames around it).
3. Fix, then re-render only the affected range. Repeat until nothing jumps unintentionally.
4. Final: `--sub 4` (180° shutter motion blur), full res PNG, then `scripts/tools/pop_detect.py`: every spike must be a planned cut.
5. Mix (`audio/mix.py`), then encode (`scripts/tools/encode.sh`), then send the MP4 with SendUserFile.

`references/engine.md` documents the engine API, 3D and the QA tools. `references/lessons.md` lists the
traps that already cost hours, so read it before building.

## References (read when relevant)

- `references/pipeline.md`: stage-by-stage instructions, deliverables, gate questions
- `references/morph-cookbook.md`: proven transitions and morphs with code pointers
- `references/sound-design.md`: SFX library map, music strategy, mixer usage, loudness
- `references/assets.md`: sourcing, prep, generation, video routing, costs
- `references/engine.md`: canvas engine API, 3D, Python engines, render and QA
- `references/style-library.md`: visual languages from past projects and promptsmotion.com
- `references/lessons.md`: gotchas and fixes, read before building
