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
