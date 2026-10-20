# Motion vocabulary — named moves, templates, camera, effects → seek(t) recipes

Naming a style works better than describing one. Use these names in concepts, beat tables and notes to the user,
and build them with the recipes. p ∈ [0,1] is local progress, e = ease(p). Durations at 60 fps.
Raw data (all 662 Animista keyframe blocks, template parameters, Swishy's Remotion sources) is private in
`10_October/motion_refs/_research/tool_extracts/`.

## Named entrances, exits and text moves
| Name | Source | Recipe | Dur |
|---|---|---|---|
| tracking-in-expand | Animista | letter-spacing −.5em→0 (re-centre the line), opacity 0→.6 by p=.4 →1; CubicOut | 42 f |
| tracking-in-contract-bck | Animista | spacing 1em→0, z 400→0 (scale P/(P−z), P≈1000), opacity as above | 60 f |
| text-focus-in | Animista | `filter: blur(12·(1−e)px)`, opacity e | 60 f |
| focus-in-contract | Animista | spacing 1em→0 + blur 12→0 + opacity; QuadOut | 42 f |
| text-blur-out | Animista | blur 0→12, opacity 1→0; QuadIn | 72 f |
| text-pop-up-top | Animista | y 0→−50, stacked 1–9 px light copies, drop shadow (0, 50e, 30e) | 30 f |
| text-shadow-pop | Animista | 8 hard copies offset k·e px, type moves −8e | 36 f |
| text-flicker-in-glow | Animista | on/off opacity table, white glow built in 3 blur passes (30/60/110 px) | 240 f |
| puff-in-center | Animista | scale 2→1, blur 4→0, opacity 0→1; SineIn | 42 f |
| slit-in-vertical | Animista | z −800→−160→0, rotY 90°→87°→0, opacity on by p=.54 | 27 f |
| slide-in-blurred-top | Animista | y −1000→0, scaleY 2.5→1, scaleX .2→1, blur 40→0; QuintOut | 36 f |
| swing-in-top-fwd | Animista | rotX −100°→0 about the top edge; BackOut | 30 f |
| roll-in-blurred-left | Animista | x −1000→0, rot −720°→0, blur 50→0; QuintOut | 39 f |
| bounce-in-top | Animista | y −500/0/−65/0/−28/0/−8/0 at 0/.38/.55/.72/.81/.9/.95/1, ease-in falls, ease-out rises | 66 f |
| jello / heartbeat / shake | Animista | scale or x tables per keyframe (attention moves; use once, on a landing) | 48–90 f |
| kenburns | Animista | scale 1→1.25, drift 15 px, origin near the subject; ease-out | 300 f |
| SplitText char rise | GSAP | per glyph y 100 %→0 inside a line clip, delay = amount·ease(nᵢ) from centre; expo.out | 36–60 f + spread |
| word-by-word title | spec | one word every 0.05–0.06 s, each rising 16 px out of a 12 px blur in 0.34 s | — |
| Rack-focus in | Raylight | blur 40→0 while scale 1.04→1; 600 ms ease-out (Raylight's default "In") | 36 f |
| Shimmer | Raylight | a Gaussian glint (width 0.18 of the word) sweeps across the type | 40–60 f |
| Spill word | Swishy | letters leave last-first 17 f apart: 35 f anticipation (rise 18 px, counter-rotate 3°), then fall 750 px, ±24°, blur 16 with a 0.45 trail | 110 f/letter |
| Scramble | Swishy | each glyph shows `hash(i, floor(f/3))` symbols for 8 cycles, then locks; 6 f per letter | — |
| Word wheel | Swishy | words on a left-bending arc (offset −\|d\|^1.2); hold to 30 % of the cycle, blur out by 50 %, in by 70 % | — |
| Extend / stretch | Swishy | rows skewX along a 15° diagonal: settle 0–30, stretch 30–75, reset, stretch back 105–150 | 150 f |
| Terminal typing | Swishy/spec | 4 f per character (30 fps), block cursor while typing → thin bar when idle | — |
| Goo text | Swishy | blur the type, alpha threshold (×19, −9), crisp type on top | — |
| DrawSVG draw-on | GSAP | `setLineDash([L·e, L+1])`; power2.inOut | 60–120 f |
| MorphSVG | GSAP | equalise point counts (split longest segments), pick the rotation k minimising Σ\|Aᵢ−Bᵢ₊ₖ\|², lerp; or flubber | 36–72 f |
| Flip expand | GSAP | rect = lerp(first, last, e) in the parent's space; expo.inOut | 30–48 f |
| CustomWiggle | GSAP | x = base + A·(1−p)·sin(2π·10p) | 30–60 f |

## Continuity transitions (no cut, no fade)
- **Black flood:** a shape overscales past the frame corners in ~0.3 s, then contracts into the next scene's shape.
- **Iris:** a 6-blade polygon opens onto the next image.
- **Goo merge:** blur + alpha threshold between two shapes.
- **Liquid glass:** a lens samples the scene behind it through a displacement map at three slightly different
  scales (one per channel) for chromatic edges; letters as signed-distance glass.
- **Edge-on swap:** split-flap, Rolodex, coin flip, venetian slats. Swap the texture when |cos θ| ≈ 0 or under full cover.
- **One shape, never cut:** a single container morphs size, radius and colour through UI states, a cursor drives
  every change with real clicks, the last frame matches the first (velocity included) so the clip loops.
- **Stair-step pixel mask:** the next section reveals through a stepped pixel edge (1minus1 showcase).

## Template families (arqe, animos): showcase layouts for images and screens
| Name | What it does | Build |
|---|---|---|
| Stack slide | next card rises onto a stack (2°→0°), cards behind shrink 0.95 per level | per segment y = lerp(H, y₀, e(local/.55)) |
| Carousel flow | belt of cards, centre 1.0, sides 0.82 scale / 0.55 opacity; steps of 1.67 s, 2/30 s stagger | offset = (i − idx − e)·pitch, wrapped |
| Cover flow | centre flat, neighbours turned 40° | rotY = clamp(d)·40°, z by \|d\| |
| Ticker tilt / stepped marquee | opposed rows on a plane tilted 30°; stepped lanes with 35 % hold | x = (t·v + laneOffset) mod W |
| Card globe | 30–40 cards on a Fibonacci sphere, facing camera, back faded; stepped stops with 2.8× zoom | opacity by z |
| Orbit | 7 planes on a ring; big in front, small behind | angle = 2π(i/n + t) |
| Spiral stream | cards wind down a 3.75-turn helix | y = h·frac(u − t) |
| Field / tunnel | fly through 12 planes scattered in depth 2.6k–10k, depth fog | z = near + (far − near)·frac(seed + t) |
| Proximity | 500 tiny tiles; a roaming focus magnifies nearby ones 5→60 | scale = lerp(max, min, smoothstep(d/dmax)) |
| Flicker | full-frame image strobe with a slow 30 % scale/drift | idx = floor(pace(t)·n) |
| Zoom parallax | Ken Burns 12 % push, alternating pan | scale = 1 + .12·e(local) |
| Wheel | big wheel ticks with 20 % anticipation, 10 % overshoot, 33 % hold | stepped angle via impulse curve |
| Page curl | lit pages bending, 2 s flips | subdivided plane wrapped on a cylinder |
| Gravity toss | cards thrown up, hang, fall and bounce (bounce .2, friction .4, tilt 18°, stagger .18 s) | closed-form arc + damped bounce |
Loop rule (animos): each card gets one segment; motion fills the first 45–55 % of it, then holds.

## Device mockups and still camera presets
Devices worth having as 3D plates: iPhone 17 Pro / Air, iPad Pro, MacBook Pro 14", Studio Display. Light presets: photo
studio, softbox, soft glow. Still-shot camera presets (tilt X/Y/Z°, zoom, aperture): straight-on 0/0/0 ×1.15 ·
hero left/right 6/∓24/∓2 ×1.35 f.45 · low angle −16/−8/0 ×1.5 · top-down 26/0/0 · isometric 18/32/0 ·
macro tilt 3/−13/−1 ×2.3 f.8 · flat lay 34/0/−10. Grain .04–.18, vignette 0–.3.
**Screenshot trick (Raylight):** duplicate and crop one element of a flat screenshot, float it forward, then dolly
toward it with focus on it. Lean a flat screen back for depth with a 3D tilt.

## Camera moves → code (aicameramovements.com families)
| Family | Moves | Code |
|---|---|---|
| Pan/tilt | static, pan, whip pan, tilt | yaw/pitch only, no parallax. Whip = yaw 60–120° in 8–12 f, expo.inOut, blur ∝ angular speed, cut at the blur peak |
| Zoom/lens | slow/fast/crash zoom | focal length only (log space), all layers scale equally. Crash = 24→85 mm in 4–8 f, expo.out + 2–3 f decaying shake |
| Dolly/track | dolly, tracking, follow, reverse tracking, side, low, vehicle, chase | position along view axis / subject + offset, `lookAt(subject)`. Layer at depth z shifts Δ/z. Chase = spring lag + noise |
| Physical | truck, pedestal, slider, push past, arc, orbit | x/y with the target moving too; push past = dolly through a near layer; arc 15–45°, orbit 90–360°: pos = target + (R sinθ, h, R cosθ) |
| Human | handheld, snorricam | seeded multi-octave noise 0.5–3 Hz, ±0.3–1° rotation; snorricam = subject fixed, world moves |
| Drone/crane | crane up/down, drone push/pull, helicopter | y on an arc with pitch compensation; Catmull-Rom path, ±3–5° roll on turns |
| Specials | first-person, tilt-shift, infinite zoom, earth zoom-out, time-lapse, pass-through | head-bob ~2 Hz at 1.6 m; band blur; scale = base^(kt) with nested scenes; h = h₀(h₁/h₀)^e; swap scene crossing a portal plane |
Not in that library: **dutch** (roll ±10–25°), **rack focus** (animate focus depth, or blur each 2D layer by k·\|z − focus\|),
**dolly zoom** (distance d(t) with fov = 2·atan(W/2d) so the subject keeps its size).
Craft: dolly gives parallax, zoom gives none. Every move has a subject with a start and an end. Raylight's
camera = two framings (centre, zoom, roll, orbit, tilt, pivot depth) with dolly / zoom / dolly-zoom between them,
zoom interpolated in log space. Shake presets: handheld, loose handheld, walk, run, car window, rumble, jitter (amount ~0.3).

## Scene effects (Raylight defaults; 1–2 subtle ones per shot)
Depth of field (focus range 5, bokeh 3) · bloom (1, threshold .8) · vignette .5 · motion blur 180°, 16 samples ·
film grain .06 / size 1.5 · ghost (opacity .08, offset 6, blur 3) · colour split · gradient map · edge fade ·
atmosphere. Our equivalents: per-pixel DOF (`measured-recreation.md` §5), `--sub N` blur, the ffmpeg finishing pass.

## Libraries in a seek(t) engine
- **GSAP** (free incl. SplitText/MorphSVG/DrawSVG; cdnjs `gsap/3.13.0`): build `gsap.timeline({paused: true})`,
  then `seek = t => tl.totalTime(t)`. No `random()`, ScrollTrigger, `delayedCall` or `onUpdate` side effects;
  detach from rAF with `gsap.ticker.remove(gsap.updateRoot)`.
- **Lottie** (LottieFiles free animations: Lottie Simple License, commercial use OK, credit optional):
  lottie-web 5.13.0 canvas renderer, one **offscreen canvas per animation** (it rewrites the canvas size on
  load), `autoplay: false`, wait for `DOMLoaded`, then per frame
  `anim.goToAndStop(clamp((t − t0)·anim.frameRate, 0, anim.totalFrames − 1e−3), true)` and `drawImage` it.
  `goToAndStop(v, false)` takes **milliseconds**. JSON basics: `fr` fps, `ip`/`op` in/out frames, `w`/`h`, `layers`.
  Avoid files whose expressions use random/wiggle (render a frame twice and compare).
- **Showcase sites worth studying** (gsap.com/showcase): almost all are scroll-scrubbed timelines; in a film,
  replace scroll progress with p(t). Ideas: films as tilted 3D discs rolling on an arc (A24), a page that is a
  music workstation whose playhead is the scroll (sonicdesk), logo glyphs as windows onto footage (Filmbot),
  thermal-gradient type with a band-wipe portrait and an orbit ellipse (Kelvin).
