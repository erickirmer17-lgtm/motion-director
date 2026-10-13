# motion-director

A Claude skill that turns an idea into a finished, edited motion-graphic video.
Claude plays creative director, copywriter, art director, sound designer and editor.
It researches, pitches concepts, sources and generates assets, builds the edit in code,
designs frame-locked sound, QA's every morph and delivers an MP4.

**Example output:** *The AI editing era has begun…* is a 15 s, 9:16, 60 fps spec ad for Claude. It mixes
public-domain engravings with a lime "edit layer", match-cuts on the Claude spark, uses a Three.js timeline,
and ends on the logo. The full source is in `scripts/engine/examples/ai_editing_era/`.

## How it works
| Stage | Claude delivers | You choose |
|---|---|---|
| 0 Intake | brief restated, format, **budget question** + cost sheet | budget, format |
| 1 Research | reference breakdown, brand study, asset pool | — |
| 2 Concept | 2–3 concepts (logline, copy, look, beats, sound) | one |
| 3 Storyboard | beat table + style frames rendered in the real engine | go / changes |
| 4 Assets | sourced + generated images, music candidates; **asks before any video generation** | picks |
| 5 Rough cut | full-length preview + temp mix | notes |
| 6 Final | motion-blurred master + share copy, QA report | approve |

Money rules: it asks your budget first and asks before every paid video generation. Everything else
runs on its own, and you pick at each stage gate.

## What's inside
```
SKILL.md                     workflow, roles, tool choice
references/                  pipeline · morph-cookbook · sound-design · assets · engine · style-library · lessons
scripts/engine/              deterministic browser-canvas + Three.js engine (60 fps, sub-frame motion blur)
  core.js index.html capture.js scene_template.js  examples/ai_editing_era/
scripts/engine_py/           numpy/cv2 compositors (film-grade, voxel sprites, thermal plates)
scripts/tools/               new_project.sh · analyze_reference.py · prep_assets.py · commons_search.py
                             sfx_scan.py · mixer.py · elevenlabs.py · pop_detect.py · sheet.py · encode.sh
assets/brand_claude/         official Claude lockup paths (spark + wordmark)
```

## Install
- **Claude Code:** copy the folder to `~/.claude/skills/motion-director/` (or `<project>/.claude/skills/`).
- **Claude.ai / desktop:** zip the folder and upload it as a skill.

Requirements: Node 18+, Python 3.9+ (numpy, scipy, opencv-python, Pillow), Google Chrome, and an ffmpeg
binary. Optional: Magnific MCP (GPT-Image-2 / Nano Banana / bg removal), ElevenLabs API key,
Topview / fal for video, Blender.

Environment overrides (defaults point at the author's workspace):
`FFMPEG`, `CHROME_PATH`, `ELEVENLABS_API_KEY` (or `MD_API_KEYS_FILE`). The SFX paths in
`references/sound-design.md` refer to a local library; swap them for your own.

## Quick start
```bash
bash scripts/tools/new_project.sh ~/videos/my_ad      # scaffold + npm install
cd ~/videos/my_ad/engine
node capture.js --from 0 --to 239 --scale 0.4 --jpg --workers 6   # preview frames of the starter scene
```
Then ask Claude: *"make a fast 15 second ad for … ending on the logo"*.

Trademarks and logos belong to their owners. Archival images used in examples are public domain.
