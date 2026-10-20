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
- A letter built from several separately filled shapes shows faint anti-aliased seams that pop when you swap to the
  real glyph (EMBER dry run: 228 px changed). Fill the parts as ONE path (single beginPath, many subpaths) so the edges match.
- Typing/flip morphs: flipping letters (scaleY through 0) looks like a glitch. A masked vertical roll looks designed.
- Converging many same-size copies into one = mush. Absorb copies (shrink to the centre) and grow the hero.
- Zooming an archival scan past ~3× pixelates; hand over to vector type at the scan's size, then grow.
- The animated logo spark must be the logo's own path, ending on its exact centroid/scale, or the switch to the vector lockup pops.
- The GPU 2D canvas made renders depend on draw history: the same frame came out differently (thin-line
  thumbnails and discs, up to 123/255) depending on which frames the worker had drawn before, and the 3D init
  changed it too. A normal ascending render hid it; an out-of-order `--list` re-render would have shimmered.
  Fixed by a software 2D canvas in capture.js plus a warm-up of every clip's first frame in index.html.
  `seek_check.py` found it in the finished AI EDITING ERA film, so run it on every project.
- Motion blur by 8-bit running average (globalAlpha 1/(k+1)) is ≤1 level off at 4 samples but posterises at more;
  index.html now sums in float when `--sub` > 4. Sub-frames must stay inside the act (choose content with `FR`), or a
  hard cut double-exposes.
- Bounce everywhere reads as generated. `spring(f, 3.2, .55)` overshoots 13 %: use the `SP` presets (critical by
  default), overshoot only on ≤ 2 real landings, never on type.
- Chromium: `will-change` with an animated blur gives ghost frames; blur radii below ~0.75 px render fully sharp
  (a fade-from-blur pops at the end); `preserve-3d` with opacity or filter flattens the element (fade a wrapper);
  `backdrop-filter: url()` misreads displacement maps; `will-change` on anything the camera scales blurs its text.
- Footage in the browser: Python's `http.server` can't range-seek video. Load it as a blob URL and wait for `seeked`,
  re-encode all-intra (`-g 1`), or use JPEG sequences.
- Lottie: `goToAndStop(v, true)` = frames (relative to `ip`), `goToAndStop(v, false)` = **milliseconds**. The canvas
  renderer rewrites its canvas size on load: give each animation its own offscreen canvas and `drawImage` it.
- Hard flashes (white-outs, negatives) land on the music onset or 1–2 f before it; *pulses* (scale/brightness) peak
  ~2 f after their sound. Two conventions; pick per event.
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

**Tooling**
- `sheet.py` and `pop_detect.py` read frame numbers from file names; use `--crop` to measure a single morph region.
- `capture.js` hides 404s (favicon, optional logo/fonts json); add `--verbose` when debugging asset loading.
- Disk: `analyze_reference.py` writes every frame as PNG (≈ 30–90 MB per minute of reference) and full-res grabs are
  3–6 MB each. Check `df -h` before analysing many references; delete `analysis/frames/` once the sheets exist and take
  hi-res grabs as JPG (`-q:v 3`). The machine ran out of space mid-session on 2026-10-20.
- Subagents can't write report files (the harness refuses). Ask them to return the document as a fenced markdown
  block, then save it yourself.

**Process**
- Facts are not choices: never redraw a logo, mock a product screen or invent a number to fill a gap. A missing real
  asset is a question for the user. Redrawn logos and mocked UI read as fake on screen and break brand trust.
- Show the user the first real render early (style frames from the engine, not mock-ups).
- Your own frame-by-frame QA of every transition comes before the user sees a cut.
- Don't clone someone's piece 1:1 when it isn't the user's. Analyse it, then make an original in a related language.
