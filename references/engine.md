# Engine — browser canvas + Three.js, deterministic, 60 fps

## Files (`scripts/engine/`, copied into `<project>/engine/` by new_project.sh)
- `index.html`: sizes the canvas from `?w=&h=&fps=` (capture.js passes them). It loads fonts from `assets/fonts/fonts.json`
  (`[[family, file | 'local(Futura)', {weight}], …]`, falling back to the bundled Instrument Serif + Inter Display) and images from `../assets/manifest.json`, the logo from
  `../assets/brand/logo.json` (optional) and Three.js via an import map. It exposes `renderFrame(f, sub)`,
  which renders `sub` sub-frames over a 180° shutter and running-averages them (motion blur). Edit the font list here.
- `core.js`: helpers.
  - maths: `clamp lerp prog mix kf(t, [[f,v,ease],…]) spring(f, freq, damp)`, easing `E.*` incl. `E.snap`, `E.cam`, `E.bez(...)`
  - motion (`references/motion-math.md`): spring presets `SP.*` (critical by default), `track(t, v0, steps, SP.x)`
    stacked springs, `approach(n, r)` decaying settle, `tbl(t, rows)` measured tables, `travel(t, speedKeys)`
    speed-curve glides, `lmix` log-space zoom, `hitPulse`, `boil`
  - effects: `asciify(ctx, src, cell, ramp, {x,y,w,h,tint,bg,blend,aspect})` glyph mosaic of any image/canvas
  - images: `img(ctx,name,{x,y,w|h|s,r,a,ax,ay,blur,comp,shadow})`, `cover(ctx,name,cx,cy,w,h,{fx,fy,z})`,
    `pin()` (scene) = img anchored on a normalised point, `discImg()` (scene) = circular clip by manifest cx/cy/cr
  - type: `layout()` (kerned glyph positions via prefix measurement), `word(ctx,str,fam,size,x,y,{glyph:(i)=>({dx,dy,s,a,r,blur,color,fam})})`
  - brand: `spark(ctx,x,y,size,{grow,r,dotR,spread})` (polar morph), `logoGeom/logoWord/logoSpark` (official lockup, per-letter reveal, `clipX`)
  - `line dot rrect`; palette `C` (bg, ink, lime, terra …); `FONTS` keys
- `capture.js`: headless system Chrome (puppeteer-core), static server on the project root, N workers.
  The 2D canvas runs in software (`--disable-accelerated-2d-canvas`, about 25 % slower) because the GPU canvas
  resampled images differently depending on what was drawn before; WebGL stays on the GPU.
  Flags: `--from --to --step | --list a,b,c`, `--scale 0.4 --jpg` for previews, `--sub 4` for final, `--workers 6`.
  Speed: 900 frames at 0.4 scale ≈ 10 s; full res with `--sub 4` ≈ 30 s including Three.js.
- `scene_template.js`: starter (razor split → crop box → dot→spark→logo). `three_scene.js` stub.
- `examples/ai_editing_era/`: the full 900-frame film (`scene.js`, `three_scene.js`, `mix.py`, `DIRECTION.md`).

## Scene structure
```js
clip(startFrame, endFrame, (ctx, t, f) => { … }, z)   // z-sorted layers; t = sub-frame time, FR = integer frame
```
- Write absolute frame numbers. Put shared timing in constants (`T_TYPE=[150,154,…]`) so audio can mirror them.
- Hard-cut selection: `FR`. Motion: `t`. Overlapping clips = layering (e.g. the next beat drawn under the split halves).
- Keep each beat's drawing in a function so the transition clip can call it (split reveal draws beat 2 under beat 1).

## Determinism: every frame is `render(f)`
Frame 600 must render the same whether it's drawn first, after frame 599 or after frame 20. Workers render
interleaved frames, and re-rendering one section relies on it.
- Randomness: `hash(n)` from core.js, seeded by the frame, index or clip; never `Math.random`.
- No clocks (`Date`, `performance.now`, `requestAnimationFrame` time). Everything comes from `t` / `FR`.
- No state carried between frames (velocities, particle arrays advanced per call, "last position"). Compute
  positions in closed form from `t`; for simulated motion, precompute the whole run once at init and index it by frame.
- Lazy caches are fine only for pure layout (text measurement, glyph sets). index.html's warm-up renders the first
  frame of every clip once at load, so lazy inits (3D included) happen before any captured frame.
- Prove it: `python3 scripts/tools/seek_check.py <project>/engine` (ORDER = hidden state, NOISE = async loading).

## Three.js inside the canvas (`examples/ai_editing_era/three_scene.js`)
- Separate WebGL canvas (preserveDrawingBuffer), drawn with `ctx.drawImage(glc,0,0)` each sub-frame.
- Clean look: `NoToneMapping`, `MeshBasicMaterial` for image faces (full contrast), white clearcoat
  `MeshPhysicalMaterial` bodies, `ShadowMaterial` floor (opacity 0.13), RoomEnvironment PMREM at low intensity,
  Hemisphere + Directional light, `PCFShadowMap` (PCFSoft is gone in r186).
- Image textures: draw into a canvas with the *same aspect as the face plane* (contain for ink/cut-outs, cover
  for photos). Use 1500 px per unit for the hero face you'll dive into and 320 for the rest.
- Animate everything from `t` (no clocks). Lazy-init inside `draw3D` (module scripts load after classic scripts).

## Formats: one story, a composition per format
`W`, `H` and `FPS` are globals (from the page URL). Keep frame numbers, states and assets shared, and switch
layout per format instead of cropping one master:
```js
const FMT = H / W > 1.5 ? 'tall' : W / H > 1.5 ? 'wide' : 'square';
const LY = { tall:   { type: 172, cols: 1, cam: 'vertical dolly' },
             wide:   { type: 128, cols: 3, cam: 'lateral track'  },
             square: { type: 140, cols: 2, cam: 'push-in'        } }[FMT];
```
9:16 gets fewer simultaneous elements and larger type; 16:9 gets more spatial context; 1:1 tighter type and
shorter holds. Render each into its own folder (`--w 1920 --h 1080 --out ../render/wide`), mix once
(same frame grid), encode each, and give each its own `beats.jpg` + `safe.jpg`.

## Python engines (`scripts/engine_py/`)
- `rise_fall_core.py`: numpy/cv2 2.5D with paper/dark textures, voxel slab extrusion of sprites, thermal plates,
  stroke draw-on (boiled on twos), ink blobs, 4-point stars, speed lines and a `finish()` film grade (grain, weave,
  chroma, halation, vignette). Better for gritty/analog/pixel looks and 4:3 film pieces.
- `motion_clone_engine.py`: sprite affine/blur/DOF compositor used for the 1:1 AE clone.

## QA tools (`scripts/tools/`)
- `sheet.py dir out.jpg [--from --to --step --cols --crop x0,y0,x1,y1] [--safe]`: labelled contact sheets. Read them
  after every change. `--safe` shades everything outside the safe area for the frame's aspect (9:16 = rough union
  of TikTok/Reels/Shorts overlays) in red; `--width 390 --cols 4` = phone-in-hand size for readability.
- `seek_check.py <project>/engine`: renders sample frames ascending, shuffled and ascending again; PASS = seekable
  and deterministic. Run after the first beats and before the final.
- Zoomed crops around a morph: render the 6–10 frames around it at full res, crop and upscale (NEAREST) side by side.
- `pop_detect.py frames/ [--crop …] [--cuts …]`: largest frame-to-frame differences; anything that isn't a planned cut or fast move is a bug.
- `flow_check.py render.mp4 [--glide a:b …]`: optical flow per frame (speed, zoom direction): flags speed dips and
  zoom reversals inside glide windows, stalls and pops; writes `_flow.csv` + `_flow.png`. Run it on a 30 fps preview
  before any final with a long camera move.
- `beats.py track.mp3 --fps 60` (run with the earshot venv python): `beats.json` for cutting to a supplied track.
- Hand-off verification: render the last 3D frame (overlay alpha 0) and the next beat's first frame, then
  `cv2.estimateAffine2D` on ORB matches should be ≈ identity.
- `encode.sh frames mix.wav out.mp4 [fps] [poster_frame]` gives the master, the share copy and `_poster.png`.
- The critic loop that uses all of these is in `references/review.md`.
