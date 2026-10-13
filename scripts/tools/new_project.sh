#!/bin/bash
# new_project.sh <project_dir> — scaffold a motion-director project from the skill templates.
#   <project_dir>/engine   canvas engine (core.js, index.html, capture.js, scene.js starter, three_scene.js stub)
#   <project_dir>/assets   raw/ gen/ img/ fonts/ brand/ + prep.py + manifest.json
#   <project_dir>/audio    gen/ + mix.py starter (uses mixer.py)
#   <project_dir>/research, render/, out/
set -e
SK="$(cd "$(dirname "$0")/.." && pwd)"
P="$1"; [ -z "$P" ] && { echo "usage: new_project.sh <project_dir>"; exit 1; }
mkdir -p "$P"/{engine,assets/{raw,gen,img,fonts,brand},audio/gen,research,render,out}
cp "$SK/engine/core.js" "$SK/engine/capture.js" "$SK/engine/index.html" "$SK/engine/package.json" "$P/engine/"
cp "$SK/engine/scene_template.js" "$P/engine/scene.js"
[ -f "$P/engine/three_scene.js" ] || echo "// optional 3D beat — see examples/ai_editing_era/three_scene.js" > "$P/engine/three_scene.js"
cp "$SK/tools/prep_assets.py" "$P/assets/prep.py"
# official Claude lockup (spark + wordmark paths). Replace assets/brand/logo.json for other brands (same keys: spark, word).
cp -n "$SK/../assets/brand_claude/"* "$P/assets/brand/" 2>/dev/null || true
[ -f "$P/assets/manifest.json" ] || echo "{}" > "$P/assets/manifest.json"
# default fonts (Instrument Serif + Inter Display instances) and the official Claude logo, if present in a sibling project
SRC="/Users/user/Documents/Claude Opp./10_October/ai_editing_era/assets"
[ -d "$SRC/fonts" ] && cp -n "$SRC/fonts/"*.ttf "$P/assets/fonts/" 2>/dev/null || true
cat > "$P/audio/mix.py" <<EOF
"""mix.py — frame-locked cue sheet (see $SK/../references/sound-design.md)."""
import sys; sys.path.insert(0, '$SK/tools')
from mixer import Mixer
LIB = '/Users/user/Documents/Claude Opp./System/Audio/SFX'
PRO = f'{LIB}/Ieditvrs SFX/Pro Sfx'
m = Mixer(fps=60, frames=900)
# m.music('gen/music.mp3', first_kick_src=0.58, first_kick_frame=22, bpm=112.35, bars=[(0, 3), (1, 3), (3, None)], db=-7, fade=(766, 782))
# m.cue(f'{PRO}/Granular, Button, Select (17).wav', 54, -15)
m.render('mix.wav')
EOF
cd "$P/engine" && npm install --silent >/dev/null 2>&1 && echo "engine deps installed"
echo "scaffolded $P"
