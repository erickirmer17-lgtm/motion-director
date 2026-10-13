# Lessons — traps that already cost hours

**Rendering / engine**
- Three.js `examples/jsm` imports bare `"three"`: you need an import map in index.html.
- Classic scripts run before module scripts: never touch `THREE` at a script's top level; lazy-init.
- A clip group sits at y = THICK/2 and its face plane at local y = THICK/2+0.003. World height = sum.
  Using only the local value gave a 1.19× mismatch in the 3D→2D hand-off. Measure, don't assume:
  compare renders with `estimateAffine2D`.
- `E.outBack(0)` is ≈2e-16, not 0. `if (u <= 0) return` doesn't catch it, so stroked rings got drawn at
  radius 6 and left stray lime dots. Guard on time (`if (t <= start) return`) and skip tiny sizes.
- Motion blur across hard cuts: choose content with `FR` (integer frame), not `t`.
- Lime (#C6F432) thin lines disappear on white. Use ≥6 px strokes, lime fills (highlight blocks behind
  black text read beautifully), or put the lime over imagery. Handles: lime fill + 2.5 px ink outline.
- Spring overshoot can push objects through the floor and they vanish: clamp the offset (`max(0, 1-s)`).
- Typing/flip morphs: flipping letters (scaleY through 0) looks like a glitch. A masked vertical roll looks designed.
- Converging many same-size copies into one = mush. Absorb copies (shrink to the centre) and grow the hero.
- Zooming an archival scan past ~3× pixelates; hand over to vector type at the scan's size, then grow.
- The animated logo spark must be the logo's own path, ending on its exact centroid/scale, or the switch to the vector lockup pops.
- Puppeteer: use system Chrome (`/Applications/Google Chrome.app/...`), headless 'new'. Screenshots aren't needed;
  `canvas.toDataURL` per frame is fast enough (≈30 ms/frame full res with 6 workers).

**Assets**
- Wikimedia 429s: descriptive UA, slow down, standard thumb widths only (1920/3840).
- Magnific bg removal can silently return the original on drawings on tinted paper. Check the alpha coverage.
- GPT-Image-2 robot hands: reference the previous render as `type:image` to keep identity; ask for a pure white background.
- Phenakistoscope figure count: angular FFT of a ring sample gives the dominant period (rats = 16, couple = 13).

**Audio**
- File names in the editor pack contain double/triple spaces (`Splash  (38)`, `Deep Whoosh   (1)`). Copy the names exactly.
- Align long whooshes by their peak; align chords/booms by their start.
- A music bed with a natural fade-out at ~9 s is common. Re-cut bars instead of regenerating.

**Process**
- Show the user the first real render early (style frames from the engine, not mock-ups).
- Your own frame-by-frame QA of every transition comes before the user sees a cut.
- Don't clone someone's piece 1:1 when it isn't the user's. Analyse it, then make an original in a related language.
