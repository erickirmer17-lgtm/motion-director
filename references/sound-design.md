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
- Analyse candidates first: `scripts/tools/beats.py track.mp3 --fps 60` (run with the earshot venv python, which has
  librosa) writes `beats.json`: BPM, a beat grid phase-refined on kick transients (librosa's raw grid was 46–64 ms early),
  downbeats from kick strength per bar phase, the strongest hits snapped to their attack, kick/snare/hat onsets,
  dropouts, and all of it as frame numbers. Read `grid_fit` for half/double-time mistakes. RMS per 0.5 s and a
  spectrogram (`showspectrumpic`) still show where the energy drops.
- Place sounds from the motion curves, not by hand (`references/motion-math.md` → Sound placement): whoosh apex on peak
  velocity, impact on contact, pop-in at 50 % travel, lock at 97 %. Hand-typed sync points land 8–11 f off.
- Pro references dip the bed before every turn (−20…−28 dB for 0.3–1.5 s) and save exact hits for interactions
  (clicks, pops, the logo forming) rather than every cut (`10_October/motion_refs/*/ANALYSIS.md`).

## Mixer (`scripts/tools/mixer.py`)
`Mixer(fps, frames)` → `.music(...)`, `.cue(path, frame, db, pan, rate, align, verb)` → `.render('mix.wav')`.
It peak-normalises sources, uses a synthetic plate reverb send (~0.15), a gentle bus compressor, an RMS-proxy loudness of
-15.5 dB and a look-ahead limiter at -1 dBFS. Derive cue frames from the same maths as the picture (e.g. 3D clip settle
times from the spring function, scrub steps from `floor(scrub(f))`) so sound and picture can't drift.
Check the result with a 0.2 s RMS ladder plus a spectrogram: the breath before the logo must be visibly quiet.

## Listening QA (earshot)
You cannot hear the mix; earshot can (local CPU, `earshot` skill; install at `System/tools/earshot`, MCP `earshot`).
Run it on the encoded MP4 before delivery; the whole pass takes ~35 s for a 15 s film.
1. `mixer.render('mix.wav')` also writes `mix.cues.json` (every cue frame, layered cues merged).
2. `earshot timeline out/film.mp4 --cues audio/mix.cues.json --detail high`: loudness, beat grid, events, and sync
   per cut and per cue (offset = sound minus picture). Read the 'chance' figures: only above-chance sync means anything.
3. `earshot sheet out/film.mp4 -o render/sheet.png --cues audio/mix.cues.json`: OPEN the PNG. Red marker = a cue
   with no sound under it (masked or missing): fix it. Violet = only a level peak (fine for whooshes/swells).
   Amber (within 100 ms) is expected for `align='peak'` cues: the mixer lands the *peak* on the frame, earshot
   marks the *onset*, which comes a few ms earlier for soft-attack sounds. A hit that is amber and *late* is wrong.
4. `earshot critique out/film.mp4`: scorecard vs 7 launch films; fix any critical/major row, consider the tips.
5. Choosing sounds: `earshot rank "<source + material + action>" "<…>/System/sfx/<folder>" --top 8` searches
   the library by sound (embeddings are cached), then `find` the clean trim. For a real-world gap,
   `python3 System/tools/freeassets/freeassets.py sfx "<keywords>" --max-dur 6 --rank "<source + material + action>"`
   pulls up to 10 Openverse/Freesound candidates (CC0/BY only, ~128 kbps MP3 previews, 200 searches/day) into
   `System/Audio/_OPENVERSE_INBOX/` and ranks them; `freeassets keep <file> <folder>` files a winner into the library;
   `freeassets credits <files>` prints the attribution lines CC BY needs. For a synthetic gap, `earshot sfx render <id>
   --dur <s> --apex <s>` makes a code-synthesized whoosh/hit/click aimed at the move, free and instant
   (`earshot sfx list --kind whoosh`); ElevenLabs when neither has it.
Baseline: AI EDITING ERA v2 scored launch-grade (23/23 in range), -15.2 LUFS, 97% of cuts with an onset within 100 ms,
0 red cues; only tip was a stop-down (0.2-1 s drop-out) before the biggest visual change.
