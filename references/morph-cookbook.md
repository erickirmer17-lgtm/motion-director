# Morph & transition cookbook (all proven in renders)

Code for each lives in `scripts/engine/examples/ai_editing_era/scene.js` (search the beat name).
Principle: a fast hard cut feels smooth when **something persists**, such as a shape, a position, a colour or
a word. A morph is "perfect" when the frame-difference QA (`pop_detect.py`) doesn't flag it.

## Continuity anchors (hard cuts that feel like one shot)
- **Match-cut on a point.** Pin each new image so its meaningful point (fingertip, quill nib, scissor pivot,
  eye, lens) lands on the same screen point: `pin(ctx, name, px, py, CX, CY, {h})`. Get the points
  automatically where you can (`prep` alpha extremes: leftmost opaque pixel = fingertip), otherwise from a
  20-step coordinate grid image. Beat 5 hands (spark at contact) and beat 7 eye → lens chain.
- **Persistent ring / box / cursor** drawn above the cutting images (lime lens ring, crop box with handles,
  Claude-spark cursor dragging handles). The anchor keeps moving smoothly while the content steps.
- Cut decisions use the integer frame `FR`; motion uses sub-frame `t`. Otherwise motion blur blends two shots on a cut frame.

## Cuts that are the message
- **Razor split.** A lime line draws across a word (the spark is the blade), then the frame splits along the
  line and the two half-planes slide apart along the normal, revealing the next scene in the gap
  (half-plane clip + white fill per half). BEAT 1.
- **Crop edit.** An image is shown ghosted (13 %) outside a lime crop box and full inside; the cursor drags
  handles, the box snaps between aspect ratios (`E.snap`), and content swaps on the snap. BEAT 2.
- **Box → caret.** The crop box collapses (w→12 px, h→cap height) into the text caret that types the next word.

## Type morphs
- **Typing**: letters pop (`outBack` 6 f) at 4 f intervals; the caret follows with `outC` 3 f; it blinks only on holds.
- **Font-swap roll** (historic→modern): per letter, a masked vertical roll. The serif glyph slides up out
  of a clip rect while the sans glyph rises into place. Glyph *centres* interpolate between the two layouts. Stagger 3 f.
  Run a lime highlight block behind the word during the swap so it reads as "selected → replaced".
- **Ripple delete**: select ("cam" highlight grows), razor line drops at the boundary, deleted letters fall
  and shrink with `inBack`, and the survivor slides into the centre with `E.snap`.
- **Title-to-word**: zoom into a word printed *inside* an archival image (the engraving's title
  "The Camera Obscura"). Stop zooming once the printed word is about 380 px wide, crossfade (4 f) to your typeset word
  at the same size and position, then scale the typeset word up to full size. Don't zoom an archival scan past ~3×.
- **Mask rise / sink**: lines enter by rising from a baseline clip and exit by sinking back (staggered 2–4 f).
- **"Claude is typing…"**: the line's ellipsis is three terracotta dots. They wave, then merge into one dot
  that becomes the spark. A literal UI gesture that lands the brand.

## Shape morphs
- **Dot → logo spark**: sample the *logo's own* spark path (`initSpark(LOGO.sparkD)`), store it as polar
  points around the area centroid, and interpolate the radius from the dot radius to the real radius with ray tips lagging
  (`spread`). End it exactly on `logoGeom` (centroid × k, size = 2·rmax·k, rotation 0), then switch
  to the vector lockup; the switch is pixel-identical. Reveal the wordmark with `clipX` = the sliding spark's right edge.
- **Stroboscopic disc**: phenakistoscope / zoetrope images rotate in steps of exactly 360°/N per frame-step,
  so the figures animate in place. Detect N with an angular FFT and the centre with Hough circles. The scrub knob moves smoothly while
  the disc steps (`floor(scrub(FR))`).
- **Paste burst**: copies pop into a grid (`outBack`, 1.2 f stagger, pitched SFX). Then they're absorbed:
  copies shrink to the centre while the main disc grows from its slot into the hero disc.
  Don't converge everything at the same size, which turns to mush.
- Guard every `outBack(prog())` with `if (t <= start) return;`. Float error makes outBack(0) ≈ 2e-16 > 0,
  which draws invisible-but-stroked shapes (stray lime dots).

## 2D ↔ 3D hand-offs (Three.js in the same engine)
- **In**: the previous beat opens a hole (evenodd clip, a click-ripple circle) through which the 3D scene shows.
- **3D to 2D, exact**: dive the camera onto a textured face while `lookAt` keeps the target point centred
  (bezier path with a raised control point, up-vector blending from +Y to −Z). End straight above the point at
  distance D = imgHeightUnits / (targetPx / H) / (2·tan(fov/2)). Over the last 12 f, project the image
  rectangle's corners (`Vector3.project`), affine-map the crisp 2D image onto them, crossfade, and settle onto
  the next beat's exact framing. Verify with feature matching (estimateAffine2D ≈ identity).
- Face-plane height = group y + local y. Forgetting the group offset produced a 1.19× scale error (see lessons.md).

## Camera language
- 2D "camera" = transform around a pivot: push-ins `lerp(1.06,1)` on reveals, zooms with `E.inE` into centres.
- 3D: start top-down so it reads as flat UI, swing (`ioQuint`, ~1 s, with an arc) into a low angle down the
  tracks, push, then dive. Clips slide in along their tracks with springs (`spring(f, 2.4, 0.58)`) and never
  dip below the floor (clamp y).

## Easing palette (core.js `E`)
`snap` (UI resize/settle), `outE`/`outQuint` (entrances), `inE` (zoom-through), `ioQuint` (camera),
`outBack`/`outBackS` (pops), `spring()` (physical settle). One family per gesture type, used consistently.
Springs now come as presets (`SP.firm`, `SP.calm`…, critical by default) and stack with `track()`; GSAP, Penner,
arqe and animos curves are in `references/motion-math.md`, named moves in `references/motion-vocabulary.md`.

## From the pro reference library (`10_October/motion_refs/*/ANALYSIS.md`, full recipes there)
- **Caret as the continuity element** (ADiitYA/SKOOP): every scene is a query typed somewhere (headline, caption on
  footage, URL bar, app sheet, pill); the caret holds screen-centre while the context changes around it.
- **Accent = unresolved, real = found:** products appear as flat accent silhouettes (`source-in` fill), then the real
  photo wipes in through a 20 %-feather gradient mask over 8–12 f. Reverse it to "un-find".
- **Cooling letters:** each typed glyph spawns in the accent and lerps to ink over ~10–12 f, so the trailing letters
  carry a gradient (hot-edge typing: an orange tail ~10 chars that cools to white, Jaxx). Typing at 2–3 f/char.
- **Word-colour karaoke:** each spoken word enters saturated (royal blue #2F5AE8) and dries to white over ~10 f; no
  box or underline needed. Words land within ±2 f of their Whisper onset, never ahead of the voice.
- **Three-tier caption lockup:** small lead-in top-left, one hero word at 25–30 % of H (tight tracking, often behind a
  matte of the head/hand/phone), small right-aligned tail under the hero's last letters. Red bar strikes negations.
- **Jump-scale cut:** the same word, same centre, at ¼ size on the next frame; no tween.
- **Images as glyphs:** cutouts pop between typed parentheses or as accent chips inside a sentence; contents swap every 4–8 f.
- **Processing wash:** luminance → a cycling 3-stop gradient map with a visible dot screen, crossfading back to true
  colour over 20–40 f ("the AI is thinking").
- **Invert-strobe whip:** across a cut, 2-frame pairs of normal / inverted-greyscale / smeared (diagonal ~30°), ~10 f,
  placed in the voice's breath gap. An invert cut is just 2 inverted frames on the cut.
- **B&W → colour bloom:** outgoing shot desaturates over 2 f, incoming starts B&W with grain, saturation back in 3 f.
- **Window match-cut:** a full-frame macro shrinks into a box that lands on (and tracks) the same detail in the wider shot.
- **Glyph mosaic boot-up:** `asciify()` with the cell size stepped 40 → 20 → 10 on beats; tall columns for a different
  texture; blend 40–70 % over the source so the photo still reads.
- **Type zoom-through:** a giant glyph scales past the lens around a point inside a counter; the counter becomes the
  matte for the next shot (`lmix(1, 40, E.inE(p))`).
- **Stepped builds:** grids double and resolutions halve on beats instead of tweening; reads as "machine".
- **White-out / negative flash:** full white on the cut frame (no ramp), or one inverted frame of the incoming shot.
- **Card shrink-to-hands:** the shot barrel-warps into a rounded card and scales into the presenter's hands on the anchor shot.
- **Panel push triptych:** new footage panels push in from the right and compress the others (1 → 2 → 3 columns, ~1.4 s apart).
- **Dots → logo:** three loading dots hop, collide and burst into the mark; then the wordmark types.
- **Pixel-mosaic wave** (Base44 "prompt becomes picture"): a fixed lattice of round dots (pitch 25.7 px, Ø 0.9·pitch)
  that never moves; each dot's colour is its **age since an elliptical front passed** (d = √((dx/960)²+(dy/540)²),
  0.02/frame, ±6 f hash jitter, 0.6–2× per-cell duration for freckles): white → cyan sprinkle ahead → orange → rust →
  red → peach → blush → image (4/4/8/6/8 f). Grid zooms out 9 % during the wave. Reveal: a 1-px glint line at mid-height
  opens at ~33 px/f; inside it the dots shrink and the photo starts pixelated at exactly the dot pitch, so dots become
  pixels, then blocks halve every 1.2 f. Finish by shrinking the frame into a 0.689 card, 40 px radius, over 29 f.
  Full pseudo-code in `aditya_tried_base_44…/ANALYSIS.md`.
- **Placeholder block → UI:** an accent block the size of the *next* word marks where it will land, then widens into a
  bar and becomes the input pill (one object carries three beats).
- **Zoom-cut ladder:** on each hard cut the background colour changes and the same pill returns 1.15–1.23× bigger with
  more pills around it; escalation without a camera move.
- **Brand-colour iris:** a 6-frame accent fill with a soft expanding hole onto the next shot (peak coverage ~30 % mid-flash).
- **Duotone strobe:** alternate 1–2 frames of a posterised gradient-map + dither version of the shot for 0.5–1 s to
  introduce footage inside the brand palette.
- **Hard speed-ramp pan:** 16 → 340 → 4 px/f over 40 f, peak at ~42 % of the move, on a stepped ~18 fps cadence.
- **Staggered 2×2 mosaic:** four independent timelines, cuts never on the same frame (≥ 2 f apart), ~1.8 cuts/s overall.
- **N-up teaser:** any finished caption film → a 2×2 grid of its four consecutive quarters (`xstack`), 1/4 the length,
  zero re-edit. Only hero words survive at quarter size.
