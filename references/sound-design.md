# Sound design — sleek, smooth, frame-locked

## The shape of a good 15 s ad mix
1. **Spine**: a music bed on the edit's tempo (112–120 BPM works for 60 fps: 112.5 BPM = 32 frames per beat).
   The first downbeat lands on the first big visual hit, not at 0.0 s.
2. **Event layer**: one sound per visible event (cut, snap, type, pop, scrub step, landing), each placed on
   its exact frame with its *transient peak* aligned (`align='peak'`). Most are -14…-24 dB, so they're felt more than heard.
3. **Gestures**: whooshes and swishes under big moves (camera swings, dives, splits). Align the whoosh peak to the
   moment of fastest motion.
4. **Breath**: 10–20 frames of near-silence before the logo. Fade the bed over 16 f and drop everything else.
5. **Resolve**: a warm chord/bloom that starts on the logo's first frame (`align='start'`) and peaks into the
   lockup, with a tiny sparkle on the spark.
Avoid harsh glitch packs, comedic pops and loud risers unless the brief wants energy over elegance.

## Curated library (`System/Audio/SFX/Ieditvrs SFX/`; `System/sfx` is a symlink to the same folder)
Profiled with `scripts/tools/sfx_scan.py` (duration · peak time · brightness):

| Role | File (Pro Sfx unless noted) | Notes |
|---|---|---|
| tiny tick / cut | `Granular, Button, Select (22).wav` 0.17 s, `(34)` 0.27 s | stack per montage cut; pitch with `rate` |
| grab / select | `Granular, Button, Select (17).wav`, `(13)`, `(33)` | handle grabs, selections |
| UI snap / settle | `Granular, Transform, Move, Splash (9).wav` 0.53 s, peak at 0 | box resize lands |
| move swish | `Granular, Transform, Move, Splash (2)` 1.7 s, `(30)`, `(38)`, `(52)`, `(71)` | note: `(38)`/`(71)` have TWO spaces before "(" |
| sparkle | `Sparkle Whoosh (3).wav` | spark moments, logo |
| deep whoosh | `Deep Whoosh   (1).wav` peak 0.97 s (three spaces) | swings, dives, zooms |
| sub hit | `Impact, Sub, Drop.wav` (align start) | the first split, ignition |
| riser | `Glass Riser.wav`, `Sfx (RISER)/Riser Reverb.mp3` | sparingly |
| delete | `4 type & delete.wav` | ripple delete |
| enter | `Enter.wav` | a word lands |
| UI clicks | `UI Sfx/App Click 2.wav`, `App Click 11.wav`, `small_whoosh_chimes_1.wav` | modern keys, highlight sweeps |
| whooshes | `Sfs(whoosh)/Dreamy Whoosh.wav`, `Magic Whoosh.mp3`, `Short Whoosh.wav` | soft transitions |
| real foley | `Sfx(IRL)/Scissors.wav`, `Turntable.wav`, `Old Book Page.wav`, `Mouse Click.wav` | historic touches |
| typing | `System/Audio/SFX/sfx/typing/typewriter-click.mp3`, `keyboard-tap-modern.mp3` (very quiet → normalised by mixer) | |
Also numbered folders: `09_Cinematic_Design` (whooshes, risers), `11_Communications_UI`.

## ElevenLabs sound-generation prompts that came back right (0.5 s minimum)
- shutter: "single crisp vintage mechanical camera shutter click, close, dry, short" (0.5 s, pi 0.6)
- projector: "vintage 16mm film projector running, soft rhythmic clatter of film sprockets and motor whir, close, clean, steady" (4 s)
- blade: "sleek fast blade slicing through air, bright metallic shing, clean and sharp, very short" (0.6 s)
- typewriter: "single heavy antique typewriter key strike, crisp metallic clack, close mic, dry"
- pop: "tiny soft glossy bubble pop, gentle UI sound" (pitch it into a pentatonic run with `rate`)
- spark: "tiny bright crystalline sparkle tink, like a spark igniting, delicate and clean" (0.8 s)
- ripple: "soft deep digital water-drop click with a round ripple, modern UI, clean"
- swing: "long smooth cinematic whoosh sweeping past, airy, wide stereo, elegant, no impact" (2 s)
- logo chord: "a warm, wide, glossy major synth chord swell with soft shimmering bells and a gentle reverb tail, elegant premium tech brand logo sting, clean, calm, no drums" (4 s, peak ≈ 0.6 s)
Batch with `scripts/tools/elevenlabs.py sfx jobs.json audio/gen/` (4 in parallel).

## Music
- Prompt with the exact BPM, key, instruments and "no vocals", e.g. "Sleek minimal futuristic electronic
  instrumental … exactly 112 BPM, 4/4 … clean deep sub kick on every beat, tight crisp clap on 2 and 4,
  glassy plucked synth arpeggio in A major, warm analog pad …". ElevenLabs honours tempo
  well (112.35 BPM measured), but free prompts tend to stop the groove at ~9 s and fade.
- `composition_plan` (sections with durations) holds the structure but can come back thin (kick-only).
- **Best method**: take the rich free-prompt track and **re-cut it on its own bar grid** so the groove ends
  exactly where the picture needs it. `Mixer.music(path, first_kick_src, first_kick_frame, bpm, bars=[(0,3),(1,3),(3,None)], fade=(a,b))`
  plays bars 0–3, repeats bars 1–3, then the original ending, with 6 ms crossfades on the kicks.
- Analyse candidates first: low-band onset detection gives the kick times and BPM; RMS per 0.5 s and a
  spectrogram (`showspectrumpic`) show where the energy drops.

## Mixer (`scripts/tools/mixer.py`)
`Mixer(fps, frames)` → `.music(...)`, `.cue(path, frame, db, pan, rate, align, verb)` → `.render('mix.wav')`.
It peak-normalises sources, uses a synthetic plate reverb send (~0.15), a gentle bus compressor, an RMS-proxy loudness of
-15.5 dB and a look-ahead limiter at -1 dBFS. Derive cue frames from the same maths as the picture (e.g. 3D clip settle
times from the spring function, scrub steps from `floor(scrub(f))`) so sound and picture can't drift.
Check the result with a 0.2 s RMS ladder plus a spectrogram: the breath before the logo must be visibly quiet.
