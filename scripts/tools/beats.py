"""beats.py — measure a music track before animating to it.

  "/Users/user/Documents/Claude Opp./System/tools/earshot/.venv/bin/python" beats.py song.wav [--fps 60] [-o beats.json]

Needs librosa (the earshot venv has it; the system python3 doesn't). Writes beats.json:
  bpm, offset (first beat), beats, downbeats + bar_phase_scores, hits (strong onsets: z, bar, beat_in_bar),
  kick / snare / hat onsets by band, dropouts, grid_fit (half/double-time check), and every time also as frames.
Use: state changes on beats, big moments on downbeats, clicks and whooshes on hits, the biggest change after a dropout.
The beat grid is phase-refined against kick transients (an unrefined librosa grid was 64 ms early). librosa can
report half or double tempo: read grid_fit, and trust the grid the kicks sit on.
"""
import sys, json, argparse
import numpy as np
import librosa

ap = argparse.ArgumentParser()
ap.add_argument('src')
ap.add_argument('--fps', type=float, default=60)
ap.add_argument('-o', '--out')
ap.add_argument('--hits', type=int, default=24, help='strongest onsets to keep')
a = ap.parse_args()

SR, HOP = 22050, 256
y, sr = librosa.load(a.src, sr=SR, mono=True)
dur = len(y) / sr
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
tempo, beats = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=HOP, units='time', trim=False)
bpm = float(np.atleast_1d(tempo)[0])
beats = np.asarray(beats, float)

S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
fq = librosa.fft_frequencies(sr=sr, n_fft=2048)
ft = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=HOP)


def band(lo, hi):
    """positive spectral flux in a band, normalised 0..1, and its onsets (time, strength)"""
    lb = np.log1p(S[(fq >= lo) & (fq < hi)] * 100)
    fl = np.maximum(0, np.diff(lb, axis=1, prepend=lb[:, :1])).sum(0)
    fl = fl / (fl.max() + 1e-9)
    on = librosa.onset.onset_detect(onset_envelope=fl, sr=sr, hop_length=HOP, units='frames',
                                    wait=int(.09 * sr / HOP), pre_max=3, post_max=3, pre_avg=10, post_avg=10, delta=.08)
    return fl, [(round(float(ft[i]), 4), round(float(fl[i]), 3)) for i in on]


kick_env, kick = band(30, 150)
_, snare = band(150, 2500)
_, hat = band(6000, 11000)
kt = np.array([t for t, _ in kick])

# phase-refine the grid on kick transients: median offset of kicks that sit within ±70 ms of a beat
if len(kt) and len(beats):
    d = np.array([kt[np.argmin(np.abs(kt - b))] - b for b in beats])
    near = np.abs(d) < .07
    shift = float(np.median(d[near])) if near.sum() >= 4 else 0.0
    beats = beats + shift
else:
    shift = 0.0


def grid_fit(period):
    """kick strength within ±50 ms of a grid with this period (anchored on the first beat), as a share of all kick strength"""
    if not len(kt) or not len(beats):
        return 0.0
    ks = np.array([s for _, s in kick])
    ph = ((kt - beats[0]) / period) % 1.0
    return round(float((ks * (np.minimum(ph, 1 - ph) * period < .05)).sum() / ks.sum()), 3)


per = 60 / bpm
fit = {'bpm': grid_fit(per), 'double': grid_fit(per / 2), 'half': grid_fit(per * 2)}

# downbeats: the bar phase (0–3) whose beats carry the most kick strength (±70 ms)
def kick_at(t):
    m = np.abs(ft - t) <= .07
    return float(kick_env[m].max()) if m.any() else 0.0

scores = [round(sum(kick_at(b) for b in beats[p::4]), 3) for p in range(4)]
ph = int(np.argmax(scores))
down = beats[ph::4]

# hits: z-scored onset strength, local maxima ±2 hops, z > 2.5, the strongest N
z = (env - env.mean()) / (env.std() + 1e-9)
pk = [i for i in range(2, len(z) - 2) if z[i] > 2.5 and z[i] == z[i - 2:i + 3].max()]
pk = sorted(sorted(pk, key=lambda i: -z[i])[:a.hits])
attack = librosa.onset.onset_backtrack(np.array(pk, int), env) if pk else []   # peak → start of its rise
hits = []
for i, i0 in zip(pk, attack):
    t = float(ft[i0])
    bi = int(np.argmin(np.abs(beats - t))) if len(beats) else 0
    hits.append({'t': round(t, 4), 'z': round(float(z[i]), 2), 'bar': (bi - ph) // 4, 'beat_in_bar': (bi - ph) % 4,
                 'off_beat_ms': round((t - beats[bi]) * 1000) if len(beats) else None})

# dropouts: ≥ 0.4 s below 15 % of the median RMS (drops land on bar lines; the return is the big moment)
rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=HOP)[0]
quiet = rms < .15 * np.median(rms)
drops, i = [], 0
while i < len(quiet):
    if quiet[i]:
        j = i
        while j < len(quiet) and quiet[j]:
            j += 1
        if ft[min(j, len(ft) - 1)] - ft[i] >= .4:
            drops.append({'t0': round(float(ft[i]), 3), 't1': round(float(ft[min(j, len(ft) - 1)]), 3)})
        i = j
    else:
        i += 1

F = lambda ts: [int(round(t * a.fps)) for t in ts]
out = {
    'src': a.src, 'duration': round(dur, 3), 'fps': a.fps,
    'bpm': round(bpm, 2), 'frames_per_beat': round(a.fps * 60 / bpm, 2), 'grid_shift_ms': round(shift * 1000, 1),
    'grid_fit': fit, 'offset': round(float(beats[0]), 4) if len(beats) else None,
    'beats': [round(float(b), 4) for b in beats], 'downbeats': [round(float(b), 4) for b in down],
    'bar_phase': ph, 'bar_phase_scores': scores, 'hits': hits,
    'kick': kick, 'snare': snare, 'hat': hat, 'dropouts': drops,
    'frames': {'beats': F(beats), 'downbeats': F(down), 'hits': F([h['t'] for h in hits])},
}
dst = a.out or a.src.rsplit('.', 1)[0] + '.beats.json'
with open(dst, 'w') as f:
    json.dump(out, f, indent=1)
print(f"{bpm:.2f} BPM ({out['frames_per_beat']} f/beat @ {a.fps:g} fps), grid shifted {shift * 1000:+.0f} ms on kicks, "
      f"kick fit {fit['bpm']:.0%} (double {fit['double']:.0%}, half {fit['half']:.0%})")
print(f"{len(beats)} beats, {len(down)} downbeats (phase {ph}, scores {scores}), {len(hits)} hits, "
      f"{len(kick)} kicks, {len(drops)} dropouts → {dst}")
if fit['double'] > fit['bpm'] + .15:
    print('  note: many kicks fall between beats; check whether the track is double this tempo')
if bpm > 135 and fit['half'] > .9 * fit['bpm']:
    print('  note: kicks land only on every other beat; the felt tempo may be half this')
