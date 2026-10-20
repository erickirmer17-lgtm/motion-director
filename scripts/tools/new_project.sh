#!/bin/bash
# new_project.sh <project_dir> [--brand claude] [--w 1080 --h 1920 --fps 60 --seconds 15]
# Scaffolds a motion-director project:
#   engine/   core.js index.html capture.js package.json scene.js (starter) three_scene.js (stub) — npm deps installed
#   assets/   raw/ gen/ img/ fonts/ (bundled OFL fonts) brand/ (only with --brand claude) prep.py prep_spec.json manifest.json
#   audio/    gen/ + mix.py (Mixer, frames from --seconds × --fps)
#   research/ render/ reviews/ out/  DIRECTION.md (template: brief, style guide, beats, formats, sound, gate)
set -e
SK="$(cd "$(dirname "$0")/.." && pwd)"
P="$1"; shift || true
[ -z "$P" ] && { echo "usage: new_project.sh <project_dir> [--brand claude] [--w W --h H --fps F --seconds S]"; exit 1; }
BRAND=""; W=1080; H=1920; FPS=60; SEC=15
while [ $# -gt 0 ]; do case "$1" in
  --brand) BRAND="$2"; shift 2;; --w) W="$2"; shift 2;; --h) H="$2"; shift 2;;
  --fps) FPS="$2"; shift 2;; --seconds) SEC="$2"; shift 2;; *) echo "unknown arg $1"; exit 1;; esac; done
FRAMES=$(python3 -c "print(int(round($SEC*$FPS)))")
mkdir -p "$P"/{engine,assets/{raw,gen,img,fonts,brand},audio/gen,research,render,reviews,out}
cp "$SK/engine/core.js" "$SK/engine/capture.js" "$SK/engine/index.html" "$SK/engine/package.json" "$P/engine/"
[ -f "$P/engine/scene.js" ] || cp "$SK/engine/scene_template.js" "$P/engine/scene.js"
[ -f "$P/engine/three_scene.js" ] || echo "// optional 3D beat — see examples/ai_editing_era/three_scene.js" > "$P/engine/three_scene.js"
cp -n "$SK/../assets/fonts/"*.ttf "$P/assets/fonts/" 2>/dev/null || true
if [ "$BRAND" = "claude" ]; then cp -n "$SK/../assets/brand_claude/"* "$P/assets/brand/"; fi
cp "$SK/tools/prep_assets.py" "$P/assets/prep.py"
[ -f "$P/assets/prep_spec.json" ] || echo "{}" > "$P/assets/prep_spec.json"
[ -f "$P/assets/manifest.json" ] || echo "{}" > "$P/assets/manifest.json"
cat > "$P/engine/FORMAT" <<EOF
--w $W --h $H --fps $FPS   # pass these to capture.js; frames 0..$((FRAMES-1))
EOF
[ -f "$P/audio/mix.py" ] || cat > "$P/audio/mix.py" <<EOF
"""mix.py — frame-locked cue sheet (see motion-director references/sound-design.md)."""
import sys; sys.path.insert(0, '$SK/tools')
from mixer import Mixer
LIB = '/Users/user/Documents/Claude Opp./System/Audio/SFX'      # = System/sfx (symlink)
PRO = f'{LIB}/Ieditvrs SFX/Pro Sfx'
FPS, FRAMES = $FPS, $FRAMES
m = Mixer(fps=FPS, frames=FRAMES)
# m.music('gen/music.mp3', first_kick_src=0.58, first_kick_frame=22, bpm=112.35, bars=[(0, 3), (1, 3), (3, None)], db=-7, fade=(FRAMES-134, FRAMES-118))
# m.cue(f'{PRO}/Granular, Button, Select (17).wav', 54, -15)
m.render('mix.wav')
EOF
[ -f "$P/DIRECTION.md" ] || cat > "$P/DIRECTION.md" <<EOF
# <TITLE> — direction v1
**Gate:** 0 intake   <!-- update as each gate passes: 2 concept ✓ · 3 storyboard ✓ · 5 rough r01 … -->
**Format:** ${W}×${H} · ${FPS} fps · ${SEC} s (${FRAMES} f) · ends on <brand>
**Remember:** <the one sentence the viewer should leave with>
**Line:** <the copy>
**Idea:** <the organising idea — what every transition means>

## Brief
- audience · where it plays (feed / site / pitch) · variants (9:16 / 16:9 / 1:1)
- **Facts (locked, real only):** logo <path> · product screens <paths> · names, numbers, claims <source>
- **Choices (ours):** camera, motion, transitions, copy rhythm, sound
- **Unacceptable:** <e.g. invented UI or metrics, redrawn logo, centred-text-on-gradient look, unreadable copy>

## Style guide
- ground · ink · accent(s) (hex) · image treatment · texture (grain / paper / none)
- typefaces (2 max), sizes at 1080 w
- composition: where the eye goes first in each beat
- pacing: mean frames between meaningful changes (measured from the reference if one exists)
- motion by class: micro UI <snap, ≤3 f settle> · panels <settle> · camera <slow, near-invisible> · headlines <fast in, long hold> · hero/brand <…>
- banned defaults: <list>
- from the reference: keep <traits> · don't copy <subjects, logos, copy>

## Beats (frames @${FPS})
| f | beat | viewer now knows | entry → exit state | technique / morph | sound |
|---|---|---|---|---|---|

## Formats
<per variant: what changes (type scale, element count, camera path, holds); same story and states>

## Sound
tempo · music approach · signature sounds · where the breath goes · the ending
EOF
cd "$P/engine" && if npm install --silent; then echo "engine deps installed"; else echo "!! npm install failed — run it manually in $P/engine"; exit 1; fi
echo "scaffolded $P  (${W}x${H} @${FPS}, ${FRAMES} frames${BRAND:+, brand $BRAND})"
