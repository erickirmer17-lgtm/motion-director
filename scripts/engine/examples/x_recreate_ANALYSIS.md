# Breakdown — @jordanarchivess "i'd love to see AI try and recreate this"

Source: `source.mp4` (downloaded 2026-10-07 from x.com/jordanarchivess/status/2107536262894915762)

## 1. Technical spec

| | |
|---|---|
| Duration | 20.46 s · 488 frames |
| Frame rate | 23.976 fps (true 24p film cadence) |
| Resolution | 2880×2160 · **4:3** · H.264 High · ~25.8 Mb/s |
| Audio | AAC stereo 48 kHz · voiceover + dense SFX bed, no obvious music bed |
| Loudness | very hot: peaks hit 0 dBFS, sections sit at −8…−15 dB RMS; tail 17.7–20.4 s drops to −28…−33 dB |

## 2. Voiceover (Whisper, word-timed — `analysis/audio_stereo.json`)

| t | line |
|---|---|
| 0.00–2.52 | question line (≈10 words) |
| 3.42–4.32 | 2-word answer |
| 5.18–6.50 | 3-word line |
| 8.10–11.26 | "through" + three single-word nouns |
| 13.50–16.16 | closing 6-word line ending on the payoff word |

Every on-screen word is **typed in sync with the VO** — the text never leads the voice.

## 3. Shot list (frame-accurate)

| # | Frames | Time | Ground | What happens |
|---|---|---|---|---|
| 1 | 0 | 0.00 | **red flash** #D2181A | 1-frame stretched-type flash frame (vertical squash of the first word) |
| 2 | 1–13 | 0.04–0.54 | paper | HUGE bold lowercase sans, baseline/x-height **dashed red guide lines**, words slide L with per-frame jumps; a **black redaction bar** wipes a word; hand-drawn brown ink underline + tick |
| 3 | 14–17 | 0.58–0.71 | paper | text dissolves into **morse-like dash glyphs** (pixel-sorted / bitmap font), vertical dash column at right |
| 4 | 18–46 | 0.75–1.92 | paper | line shrinks to small (~1.3% H) caption, typed word-by-word; **cursive signature scribbles** draw on with heavy motion-blurred ghost copies, a red-brown loop circles a word, a vertical ink stroke drops in |
| 5 | 47 | 1.96 | **yellow flash** | 1-frame overexposed yellow version of next shot |
| 6 | 48–87 | 2.00–3.63 | paper → vignette | **cyan→blue 4-point star** blooms from left edge; red marker slashes + grey pencil strokes explode outward; 4 tiny pixel icons float; vignette closes from black edges over ~1.5 s; the word "you" turns white (inverted highlight) |
| 7 | 88–90 | 3.67–3.75 | dark | orange/red **glow hole** opens, red + black scribble loop over the type — burn transition |
| 8 | 91–150 | 3.79–6.26 | near-black #121212 | **thermal silhouette** of a profile head (depth-map → orange/yellow/white gradient map) resolves out of a blurred purple/red blob; thin white orbit ellipse whips around the head; caption typed with block cursor; bg cross-fades to grey wall |
| 9 | 143–150 | 5.96–6.26 | grey wall | silhouette transitions to a real photo of the profile; ink-burn mask eats the head |
| 10 | 151–152 | 6.30–6.34 | **light-leak frame** | black→red→orange→yellow horizon gradient (film burn) |
| 11 | 153–155 | 6.38–6.47 | grey | pixel blocks/depth slices mid-transition (3D extrude of sprites) |
| 12 | 156–198 | 6.51–8.26 | paper | **ring of ~14 pixel-art sprites** rotating clockwise; a black **ink ball** bounces around inside with smeared motion trail; each hit **ignites** the sprite (orange glow + spark ticks); ring slowly zooms in |
| 13 | 199–218 | 8.30–9.09 | dark | single sprite **extruded to 3D**, tumbling with a red 4-point sparkle; word typed with white block cursor → thin bar cursor |
| 14 | 219–235 | 9.13–9.80 | paper | tight track along the ring (horizontal pan), red speed dashes |
| 15 | 236–251 | 9.84–10.47 | dark + red beam | 3D sprite on a **red light beam** (projector cone); word typed |
| 16 | 252–263 | 10.51–10.97 | paper | pan along ring continued |
| 17 | 264–283 | 11.01–11.80 | dark | sprite spinning, red pixel **music notes** pop in, white speed lines; red ring flash on first frame |
| 18 | 284 | 11.84 | **inverted/greyscale** | 1-frame negative of the ring |
| 19 | 285–329 | 11.89–13.72 | paper + vignette | ring pulls back, then **explodes** into scattered sprites; ink blots **devour** sprites one by one (sprites become black silhouettes); typed word gets redacted |
| 20 | 330–380 | 13.76–15.85 | dark | **thermal hand** reaching up, enters as blurred red/purple smear with white whip arcs; caption split L/R of the hand, typed |
| 21 | 381–387 | 15.89–16.14 | paper | big pixel heart + first letter, top-left |
| 22 | 388–396 | 16.18–16.52 | dark | 3D sprite + 2 letters |
| 23 | 397–401 | 16.56–16.72 | **solid red** | 3D sprite + 3 letters (letters turn cyan on red) |
| 24 | 402–411 | 16.77–17.14 | dark | spinning 3D sprite + 4 letters spaced wide |
| 25 | 412–487 | 17.18–20.46 | paper | huge blurred ink swirl → resolves to the 4 letters **scattered and drifting/rotating** like floating debris, black dots; **red thread scribbles** loop around each letter; holds to end |

**Rhythm:** cuts land on VO syllables / SFX onsets (onset list in `analysis/audio.py` output). Average shot ≈ 0.8 s, with 1-frame flash frames (f0, f47, f151, f284) as punctuation.

## 4. Visual system

**Palette (sampled)**
- Paper: #C1BFC0 → #DCDADC (centre-hot, cool grey, never pure white)
- Dark ground: #121212–#131313 (lifted black, never 0)
- Accent red: #D2181A / #D01916
- Ink: warm near-black brown #2A1A14; marker red #C8141A
- Thermal ramp: deep red #8E1A15 → orange #F0661C → amber #FFB347 → white-hot #FFF4E0
- Star glow: cyan #5EF2F0 → blue #1A3FD8

**Typography:** geometric grotesk, bold, lowercase, tight tracking. Close free matches: *Gilroy ExtraBold*, *Sora*, *Outfit*, *Plus Jakarta Sans*. Opener at ~30% frame height; captions at ~1.3–2% frame height. Cursor: a **solid white block** while typing that collapses to a **thin bar** when idle.

**Iconography:** 32×32-ish pixel-art sprites with 1-px black outlines, nearest-neighbour upscaled, slight 2-px drop shadow on paper. In the dark shots the same sprites are **voxel-extruded** into thin 3D slabs and tumble.

**Thermal figures:** depth map (or luminance) run through a gradient map, with the edge softly feathered and a faint bloom. Entry is a heavy-blur purple/red blob that sharpens over ~4 frames.

**Hand-drawn layer:** frame-by-frame ink lines (boiled, ~12 fps on twos) with a 3–5-copy motion-blur trail on fast strokes.

**Finishing (applied to everything):**
- film grain (fine, ~1.5% luma noise, animated per frame)
- paper fibre texture multiplied on light grounds
- strong vignette (lighter on paper, heavy in shot 6 and shot 19)
- red/cyan chromatic fringe on high-contrast edges
- gate weave: ±1–2 px per-frame jitter
- halation/bloom on whites and on the red sparkle
- motion blur on all fast moves (shutter ~180°)

## 5. Audio design

- **0–2.5 s:** close, dry VO; clicks/ticks for the typing; whoosh-in on the big type.
- **2.5–3.4 s:** almost silent (−33 dB) under the vignette close — the gap before the answer.
- **3.5–6.5 s:** low airy hum under the thermal head plus a soft riser; a big transient hit on the light-leak frame (6.5 s, −7 dB).
- **6.5–8.2 s:** each ink-ball bounce gets a ping/hit; ignition gets a crackle.
- **8.2–11.9 s:** each noun opens with a punchy impact (−10…−13 dB) plus a keyboard clack, a glitch tick on every flash frame, and riser swells between the nouns.
- **13.5–17.3 s:** the build. Impacts accelerate (16.25 → 16.6 → 16.8 → 17.04 → 17.28), one per letter.
- **17.7–20.4 s:** the release. Soft room tone with the scribble sounds at −28…−33 dB; it ends quiet.

## 6. How each technique maps to our stack

| Technique | Tool |
|---|---|
| Kinetic type, typing cursor, redaction bars, guide lines | HyperFrames (GSAP), 2880×2160 @ 23.976 |
| Pixel sprites | drawn as pixel grids in code → PNG (crisp, nearest-neighbour) |
| 3D extruded sprites | Three.js voxel extrude, or Blender (MCP connected) |
| Thermal silhouettes | GPT-Image-2 photo → Magnific `images_depth_map` → gradient map (ffmpeg / numpy) |
| Ink scribbles / signatures | SVG stroke-dashoffset draw-on, boiled on twos, trail copies |
| Ink-ball bounce + ignite | GSAP physics path + canvas particles |
| Light leaks / flash frames | generated gradient plates |
| Grain / paper / vignette / chroma / weave / halation | final ffmpeg grade pass (one filter graph) |
| VO | ElevenLabs |
| SFX | `System/sfx` library (typing, whoosh, impact, glitch), ElevenLabs sound-gen for gaps |
