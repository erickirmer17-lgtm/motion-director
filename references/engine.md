# Engine — browser canvas + Three.js, deterministic, 60 fps

## Files (`scripts/engine/`, copied into `<project>/engine/` by new_project.sh)
- `index.html`: sizes the canvas from `?w=&h=&fps=` (capture.js passes them). It loads fonts from `assets/fonts/fonts.json`
  (`[[family, file | 'local(Futura)', {weight}], …]`, falling back to the bundled Instrument Serif + Inter Display) and images from `../assets/manifest.json`, the logo from
  `../assets/brand/logo.json` (optional) and Three.js via an import map. It exposes `renderFrame(f, sub)`,
  which renders `sub` sub-frames over a 180° shutter and running-averages them (motion blur). Edit the font list here.
- `core.js`: helpers.
  - maths: `clamp lerp prog mix kf(t, [[f,v,ease],…]) spring(f, freq, damp)`, easing `E.*` incl. `E.snap`, `E.bez(...)`
  - images: `img(ctx,name,{x,y,w|h|s,r,a,ax,ay,blur,comp,shadow})`, `cover(ctx,name,cx,cy,w,h,{fx,fy,z})`,
    `pin()` (scene) = img anchored on a normalised point, `discImg()` (scene) = circular clip by manifest cx/cy/cr
  - type: `layout()` (kerned glyph positions via prefix measurement), `word(ctx,str,fam,size,x,y,{glyph:(i)=>({dx,dy,s,a,r,blur,color,fam})})`
  - brand: `spark(ctx,x,y,size,{grow,r,dotR,spread})` (polar morph), `logoGeom/logoWord/logoSpark` (official lockup, per-letter reveal, `clipX`)
  - `line dot rrect`; palette `C` (bg, ink, lime, terra …); `FONTS` keys
- `capture.js`: headless system Chrome (puppeteer-core), static server on the project root, N workers.
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

## Three.js inside the canvas (`examples/ai_editing_era/three_scene.js`)
- Separate WebGL canvas (preserveDrawingBuffer), drawn with `ctx.drawImage(glc,0,0)` each sub-frame.
- Clean look: `NoToneMapping`, `MeshBasicMaterial` for image faces (full contrast), white clearcoat
  `MeshPhysicalMaterial` bodies, `ShadowMaterial` floor (opacity 0.13), RoomEnvironment PMREM at low intensity,
  Hemisphere + Directional light, `PCFShadowMap` (PCFSoft is gone in r186).
- Image textures: draw into a canvas with the *same aspect as the face plane* (contain for ink/cut-outs, cover
  for photos). Use 1500 px per unit for the hero face you'll dive into and 320 for the rest.
- Animate everything from `t` (no clocks). Lazy-init inside `draw3D` (module scripts load after classic scripts).

## Python engines (`scripts/engine_py/`)
- `rise_fall_core.py`: numpy/cv2 2.5D with paper/dark textures, voxel slab extrusion of sprites, thermal plates,
  stroke draw-on (boiled on twos), ink blobs, 4-point stars, speed lines and a `finish()` film grade (grain, weave,
  chroma, halation, vignette). Better for gritty/analog/pixel looks and 4:3 film pieces.
- `motion_clone_engine.py`: sprite affine/blur/DOF compositor used for the 1:1 AE clone.

## QA tools (`scripts/tools/`)
- `sheet.py dir out.jpg [--from --to --step --cols --crop x0,y0,x1,y1]`: labelled contact sheets. Read them after every change.
- Zoomed crops around a morph: render the 6–10 frames around it at full res, crop and upscale (NEAREST) side by side.
- `pop_detect.py frames/ [--crop …] [--cuts …]`: largest frame-to-frame differences; anything that isn't a planned cut or fast move is a bug.
- Hand-off verification: render the last 3D frame (overlay alpha 0) and the next beat's first frame, then
  `cv2.estimateAffine2D` on ORB matches should be ≈ identity.
- `encode.sh frames mix.wav out.mp4` gives the master + share copy.
