# Motion math — springs, settles, speed curves, eases, sync

Everything here is a pure function of time, so `seek(t)` stays deterministic. The helpers are in `core.js`.

## Springs
- Step response (ω₀ = 2π·freq, ζ = damping ratio, τ = seconds since the change):
  - ζ < 1: `1 − e^(−ζω₀τ)·(cos ω_dτ + ζω₀/ω_d·sin ω_dτ)`, with ω_d = ω₀√(1−ζ²)
  - ζ = 1: `1 − e^(−ω₀τ)(1 + ω₀τ)`
  - ζ > 1: `1 − (r₂e^(r₁τ) − r₁e^(r₂τ))/(r₂ − r₁)`, with r₁,₂ = −ζω₀ ± ω₀√(ζ²−1)
- From stiffness/damping/mass (Remotion, Framer, Raylight): ω₀ = √(k/m), ζ = c/(2√(km)), freq = ω₀/2π.
  Swishy's house entrance (damping 20, stiffness 90) = freq 1.51, ζ 1.05: a 22–25 px rise plus fade, 8–10 f stagger.
- **Stacked springs** for a value that changes target several times (a cursor, a container's width, a slider):
  `track(t) = v₀ + Σ (vᵢ − vᵢ₋₁)·S(t − tᵢ)`. A linear spring is exact under this sum: velocity carries through each
  retarget. `track(t, v0, [[f, v], …], SP.firm)` in core.js. Frame 812 renders without simulating 0–811.
- **Two-edge stretch:** a tab indicator or toggle knob gets its leading edge on a faster spring than its trailing
  edge, so it stretches toward the target and contracts on arrival.
- **Drags:** while held, the value follows the cursor; on release it springs back from wherever it was (a new
  `track` step starting at the release value).
- **Initial velocity** (a throw handed into a settle), with x₀ = from − to:
  ζ<1 `x = e^(−ζω₀τ)(x₀cos ω_dτ + (v₀ + ζω₀x₀)/ω_d·sin ω_dτ)`; ζ=1 `x = (x₀ + (v₀ + ω₀x₀)τ)e^(−ω₀τ)`; position = to + x.
- **Landing on a beat:** start the spring at cue − (frames to first reach 100 %, or 92 % for soft snaps).

### Presets (`SP` in core.js), settle = stays within 3 % at 60 fps
| Class | Preset | freq, ζ | Overshoot | Settle |
|---|---|---|---|---|
| UI chip / toggle | micro | 4.6, .87 | 0.4 % | 9 f |
| Picker / detent | detent | 4.0, .79 | 1.7 % | 9 f |
| Lock-in snap | snap | 3.1, .67 | 6 % | 18 f |
| UI arrival | firm | 1.9, 1 | 0 | 27 f |
| Panel / card | soft | 1.75, 1.19 | 0 | 39 f |
| Full-frame surface | heavy | 1.3, 1.34 | 0 | 62 f |
| Headline land (the only spring for type) | calm | 1.27, 1 | 0 | 41 f |
| Mascot / hero landing (≤ 2 per film) | land / pop | 2.25, .51 / 2.76, .53 | 15 % / 14 % | 24 / 20 f |
**Overshoot policy:** critical damping by default. Bounce everywhere is the top tell of generated motion. Overshoot
only on ≤ 2 true landings per film, never on type. The old defaults `spring(f, 3.2, .55)` (13 % overshoot) and
`(2.4, .58)` (11 %) are for deliberate pops only.
Other tools' presets, for reference: Raylight gentle 120/15, quick 220/16, bouncy 260/11, slow 80/26 (k/c, m = 1).

## Settles, tables, speed curves
- **Decaying approach** `approach(n, r) = 1 − rⁿ`, r 0.78–0.89/frame: the settle measured in pro UI recreations
  (selection bars ×0.84, panel edges, progress fills, dollies). Fast start, soft landing, no overshoot.
- **Measured tables** `tbl(t, [[f, v], …])`: linear, held at the ends, never eased or smoothed.
- **Speed curves for glides** `travel(t, [[f, speed], …])`: integrate one speed curve into distance instead of keying
  positions; position keys every few frames surge and stall. Verify with `flow_check.py` (speed never dips).
- **Zoom/scale/distance in log space** `lmix(a, b, u)`: equal ratios per unit time. A linear scale lerp reads as braking.
  Rise/pull-back moves: log-scale zoom with a **trapezoid speed** (accelerate, even, decelerate to a stop).
- **Hit pulse** `hitPulse(t, f0, 2, 5)`: 2 f attack, τ 5 f decay, for scale/brightness punches. The pulse peaks 2 f
  after its sound.
- **Hand-drawn boil:** `boil(t, 2)` = a new drawing every 2 frames (12/s at 24). Seed each element's noise with a hash of
  its own key plus the boil frame (`hash(key*7919 + boil(t))`), so one moving element doesn't re-jitter everything
  drawn after it.
- **Avoid twinning:** two arms, two eyes or a crowd never move in sync; offset phases by hash.

## Motion laws (measured on launch films; cinetic study)
- Duration ≈ 0.5 s + 1.6 ms per px travelled. Camera moves 0.9–3.0 s (`E.cam` = bezier .48,.1,0,.9).
- A secondary move starts at 55–75 % of the leading move (follow-through), not with it.
- Contact squash 1.08 / 0.90 over 8 f. Ordinary moves ≤ 25 px/f; ceiling 60–80 px/f; above that, redesign rather
  than add blur samples.
- Exits accelerate ~×1.14 per frame into the cut. A repeated reveal runs ~40 % faster the second time.
- Hold still at both ends of a camera move and go slower than feels right (Raylight academy).
- **Write the reads:** list everything the viewer must understand, with its start and end time; no two important
  reads overlap. (A first version with 7 reads in 1.3 s was unreadable.)

## Eases
- GSAP (v3 source): `in` is the base curve, `out(p) = 1 − in(1−p)`, `inOut = p<.5 ? in(2p)/2 : 1 − in(2(1−p))/2`.
  power1–4 = p²…p⁵; sine.in = 1 − cos(pπ/2); circ.in = 1 − √(1−p²); expo.in = 2^(10(p−1));
  back.out(s=1.70158) = (p−1)²((s+1)(p−1)+s)+1; elastic.out(a=1, P=.3) = a·2^(−10p)·sin((p−S)2π/P)+1,
  S = P/2π·asin(1/a); bounce.out = the 4-parabola Penner curve (n 7.5625, c 2.75); steps(n) = floor((n+1)p)/n.
- Penner cubic-bezier approximations (Animista):

| | In | Out | InOut |
|---|---|---|---|
| Quad | .55,.085,.68,.53 | .25,.46,.45,.94 | .455,.03,.515,.955 |
| Cubic | .55,.055,.675,.19 | .215,.61,.355,1 | .645,.045,.355,1 |
| Quart | .895,.03,.685,.22 | .165,.84,.44,1 | .77,0,.175,1 |
| Quint | .755,.05,.855,.06 | .23,1,.32,1 | .86,0,.07,1 |
| Sine | .47,0,.745,.715 | .39,.575,.565,1 | .445,.05,.55,.95 |
| Expo | .95,.05,.795,.035 | .19,1,.22,1 | 1,0,0,1 |
| Circ | .6,.04,.98,.335 | .075,.82,.165,1 | .785,.135,.15,.86 |
| Back | .6,−.28,.735,.045 | .175,.885,.32,1.275 | .68,−.55,.265,1.55 |
- Named curves from template tools (use as `E.bez(...)`): arqe Flow .86,.14,.14,.86 · Sweep .7,.1,.3,.9 ·
  Settle .8,.27,.2,.75 · Glide .33,0,0,1 · Smooth .76,0,.24,1 · Snap 1,0,0,1; animos Natural .4,0,.2,1 ·
  Slow-down 0,0,.35,1 · Impulse .5,−.6,.3,1 (anticipation) · Overshoot 1 + 3.2(t−1)³ + 2.2(t−1)².
- **Keyframed CSS animations** (Animista, `@keyframes`): the ease applies per segment, per property. Find the two
  keyframes around p that set the property, u = (p − kᵢ)/(kᵢ₊₁ − kᵢ), v = lerp(vᵢ, vᵢ₊₁, easeᵢ(u)). A property missing
  from a middle keyframe spans the whole outer segment. Use one `kf()` per property; note that CSS puts the timing
  function on the keyframe a segment *leaves*, while `kf()` takes it on the key the segment *arrives* at, so shift it one key later.

## Staggers (GSAP `distribute`)
Distance dᵢ of each item from the origin (`start`, `center`, `edges`, `end`, an index, or a grid point with
hypot(dx, dy)), normalised nᵢ = (dᵢ − min)/(max − min), delayᵢ = ease(nᵢ)·amount (or each·(count−1)); `edges` reverses.
"Random" = a seeded hash permutation. Then local progress pᵢ = clamp((t − t₀ − delayᵢ)/dur).

## Sound placement computed from the motion (not typed)
Hand-typed sync points landed 8–11 f off. Derive cue frames from the same curves that draw the picture:
| Picture event | Sound lands on |
|---|---|
| whoosh | its apex on the frame of **peak velocity** of the move |
| impact | the spring's **contact** frame (first reach of 100 %) |
| pop-in | **50 %** of travel |
| settle / lock | the **97 %** frame |
| beat pulse | the pulse peaks 2 f after the sound |
Align each SFX by its **measured peak**, not its file start (`Mixer.cue(align='peak')`). Audio more than ~45 ms
ahead of the picture reads as early; slightly late reads as natural.
