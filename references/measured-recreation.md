# Measured recreation — rebuilding a reference by numbers, and writing specs that do

Use this when the user wants a reference film rebuilt shot for shot with *their* content (their product, their
landing page, their brand), or pastes a "replicate prompt": a long XML-tagged spec full of frame numbers,
hex codes and keyframe tables. It also covers the reverse: turning a reference video into such a spec.
The default skill path (analyse → design something of your own) still applies when the reference is someone
else's work and the user hasn't asked for a 1:1 rebuild.

Two worked specs are kept privately in `10_October/motion_refs/_research/specs/` (a 15 s product film rebuilt
to <3.5/255 error, and a 14.5 s WebGL landing-page fly-over). Read one before writing your first spec.

## 1. The spec format (six tags)
| Tag | What goes in it |
|---|---|
| `<inputs>` | What to ask the user for, and the default for each if they skip it. Brand words and colours are kept exactly. |
| `<direction>` | Canvas (W×H, fps, frame count, *exact* rate: 30 vs 29.97), the story in one paragraph, palette in hex per surface, type with weights/axes/tracking, the **motion law** in one line, the **banned** list. |
| `<structure>` | Scene by scene, in frames or seconds: what is where, measured values at key frames, settle constants, hard-cut frames. Named coordinate spaces where layers have their own camera. |
| `<build>` | Numbered steps: engine contract, how assets are extracted, how values are measured, calibration, special fits, sound, render + verification targets. |
| `<gotchas>` | Traps hit while building (each one cost a re-render). |
| `<start>` | What to do first: ask the inputs, then show N stills at named frames before the full render. |

When you write a spec for the user (from a reference, or as a brief for a new film), use these six tags, put
numbers wherever an adjective would go, and end `<start>` with a stills gate. The same skeleton drives the
famous one-shape UI-morph prompts: `<structure>` is a state chain on a beat grid, `<direction>` says
"one shape, never cut; a cursor drives every change".

## 2. Engine contract for recreations
- One page, `seek(n)` a pure function of the frame number. No CSS transitions, timers, `Math.random`.
- **Every animated value comes from a table** `[[f, v], …]` with linear interpolation (`tbl()` in core.js) or a
  stated formula. Never put an easing curve on a measured move and never smooth a measured table: the
  curve is already in the numbers. Scan every table for one-frame outliers and patch them by interpolating
  the neighbours (a homography fit that grabbed the wrong plane = a one-frame glitch).
- **Settles are decaying approaches**, not CSS eases: `p(n) = 1 − rⁿ`, r ≈ 0.78–0.89 per frame
  (`approach(n, r)`). Fast start, soft landing: selection bars, panel edges, progress fills, dollies, headline scale.
- Scenes are absolutely positioned layers shown/hidden by frame. **Namespace class names per scene**
  (a headline `.w` silently overrode a terminal `.w`).
- Build all parameter tables in **one script run**. Importing one builder from another re-ran its side effects
  and wiped tables.
- Hard cuts are frame numbers in one list, checked exactly after render.

## 3. Measuring a reference (never eyeball)
- **Frame rate:** read the pts. Multiples of 1/30 = 30 fps, not 29.97; encoding at the wrong one drifts audio.
- **Every frame out:** `analyze_reference.py` (sheets, cuts, onsets) plus full-res grabs around each move.
- **Text by ink box.** Measure each word's ink bounding box (x0–x1, y0–y1) per key frame; place your text by
  its ink (`measureText().actualBoundingBox*`), so the same ink lands on the same pixels whatever the font metrics.
  Calibrate weight with an ink-ratio test against the source (terminal text that looked like 400 was 600) and
  letter-spacing from the measured advance (+1.2 % = +0.1 px at 14 px).
- **Sprites/illustrations:** extract by colour-to-alpha against the paper colour; per frame fit
  scale, translation and blur (template matching or phase correlation), stored as tables.
- **Planes in 3D** (a laptop lid, a phone, a page): a per-frame homography [a…h] from plane space to the frame,
  applied as `matrix3d(a,d,0,g, b,e,0,h, 0,0,1,0, c,f,0,1)` (or a canvas/WebGL quad). Lid and base are separate
  planes with separate fits.
- **Named spaces.** Give each camera its own space (stage px, terminal T, laptop L) with a fixed affine between
  them (T→L = x·0.731+565). Rectify frames into the inner space and calibrate glyph offsets by phase correlation
  until the residual is < 0.3 px.
- **Rotating parts** (rotors, dials): fit the angle over the full 360° when parts differ in colour (a 120° fit is
  ambiguous), regress one line through the per-frame argmins (slope °/frame), use Viterbi only to unwrap.
- **Cursor:** track with a rotation-aware template matcher at 2×; the click squash is hand-interpolated;
  opacity gets its own fade table (cursors fade, not cut). Arrow = one SVG polygon from the tip, white
  round-join outline under a black fill, no viewBox offset.
- **First frames** of a piece are often blurred and over-scaled on purpose (a "landed" first frame). Keep them.

## 4. Verification targets
- Difference against the source every 5th frame. Mean absolute error ≤ 3.5/255 overall; plain-type scenes ≈ 1;
  illustrated scenes ≈ 3.7; UI ≈ 4. Plot the per-frame error; spikes are bugs.
- Confirm the cut frames and the frame count (e.g. 451 frames, f0–f450), and mux audio **without** `-shortest`.
- Two critic agents with a default stance of *reject*: one on motion (contact sheet + error plot), one on design.
  Fix what they find before showing the user.
- Show the `<start>` stills (4–7 named frames) before the full render.

## 5. Recipe: 3D fly-over of a web page (one camera, never a cut)
For product/landing pages, a WebGL alternative to screen-recording:
1. **Capture.** Playwright at 1440 px wide, device scale 2. Scroll to the bottom once so lazy images and scroll
   animations finish. Mark the lift pieces (cards, mockups, chips, feature photos, testimonial, CTA) with
   `data-layer`; screenshot the full page with them hidden, then each piece alone on transparent with 28 px
   padding, and write each piece's page rect to JSON. **Lock the page before timing anything**: a section that
   changes height shifts every later beat.
2. **Scene.** The page is a textured quad on a studio floor (#f9fbfb centre → #f2f3f6 corners, soft wide shadow,
   24 px corners). Each piece is its own quad at its height, drawn lowest first, no depth buffer.
   **Mipmaps + 16× anisotropic filtering** or distant text shimmers.
3. **Camera from one speed curve**, never from position keys every half second. Focal length ~1880 px, tilt 56°
   from straight down, distance easing out 1360 → 1700 px and never back in, no yaw. Speed as a share of
   cruise (~770 page-px/s): 0 at 0 s, 0.5 by 0.6 s, hold, 1.0 by 1.6 s, 0.94–1.1 to 7.3 s, ease to 0.12 by 8.3 s.
   Integrate it (`travel()` in core.js).
4. **Per-pixel depth of field:** blur radius = 75·(focus − depth)/depth in front of focus, 6·(depth − focus)/depth
   behind, capped at 120 px; 40 golden-angle taps, each read from the mip level matching its blur. Focus follows
   whatever crosses the frame centre. Razor-thin in front, almost none behind.
5. **Lifts.** A piece stands up by rotating about its own middle, top edge toward the lens. Shadow = the same
   picture flat #1a2133, offset (0.10z, 4 + 0.36z), blur 7 + 0.5z, 26 % opacity. Most lifts are tiny (20–40 px);
   heroes 100–200 px. Brand tiles (32 → 140–200 px) lift beside the CTA and travel with the film to the end card.
6. **Rise and dive.** Rise = zoom out in log space (`lmix`) with a trapezoid speed (accelerate, even, decelerate)
   while the tilt flattens, handing the glide to a camera that pins the page's bottom edge 42 px above frame
   bottom. Overhead = the whole page as one strip, creeping 3.5 % closer. Dive = log scale on a quadratic
   ease-in-out, look-at solved from the pinned top edge; a rounded-rect mask morphs page → hero (24 → 38 px
   corners) and the hero lands as a card under the title.
7. **Title card.** Pill badge fades in; line 1 one word every 0.06 s; italic tail (grey #8b8b92) one word every
   0.05 s, each word rising 16 px out of a 12 px blur in 0.34 s; hold with a 2 % creep.
8. **Render** on the real GPU (`--enable-gpu --ignore-gpu-blocklist`, ANGLE backend: `metal` on this Mac,
   `d3d11` on Windows), 60 fps, 16 sub-frames across 0.7 of a frame. Hit on the card landing, whooshes on
   the rise and the dive.
9. **Gotchas.** A card fading with transparency shows what's behind it: fade it into the haze colour first and
   cut to transparent at the very end. Before the final, render a 30 fps preview and run
   `scripts/tools/flow_check.py --glide a:b` (optical flow): speed down the page must never dip and the zoom
   must never reverse during the flight.
Banned in this style: cuts, crossfades, stops or surges in the glide, yaw or sideways swing, zoom in-then-out,
glows, text over the page before the end card.

## 6. Recipe: product film with a terminal/UI inside a device (paper → laptop → UI → type → paper)
The other worked spec, as a pattern: illustrated sprites on paper, each on its own camera, pop in under a serif
headline; a laptop rises as a tilted 3D lid (keep the 3-frame rise: a laptop that just appears reads as a pop);
the camera dives into the screen while the wallpaper darkens under an overlay (opacity table, or the dive reads
too light); inside, a picker's selection bar slides down with a ×0.84 decay; rows dim as the bar passes
(`alpha = 1 − 0.55·smoothstep((barY − rowY − 6)/55)`); hard cuts to plain dark type; an install panel grows
downward by decaying approach; a download counter holds values per frame; hard cut to paper for the pay-off;
end mark. Every layer rides its own camera; hard cuts only, no crossfades.
