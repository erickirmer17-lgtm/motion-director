"""mix.py — sound design for "The AI editing era has begun…" (900 f @ 60 fps → 15.0 s).
Every cue is placed on the exact picture frame of its event; transients are aligned by each
sound's measured peak. Music bed = ElevenLabs track re-cut on its own bar grid so the groove
stops on the frame the final line exits."""
import os, subprocess, math, numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
FF = '/Users/user/Library/Python/3.9/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
SR, FPS, NF = 48000, 60, 900
LIB = '/Users/user/Documents/Claude Opp./System/Audio/SFX'
PRO = f'{LIB}/Ieditvrs SFX/Pro Sfx'
UI = f'{LIB}/Ieditvrs SFX/UI Sfx'
WH = f'{LIB}/Ieditvrs SFX/Sfs(whoosh)'
G = f'{HERE}/gen'
T = lambda f: f / FPS

_cache = {}
def load(p, rate=1.0):
    key = (p, rate)
    if key in _cache: return _cache[key]
    r = subprocess.run([FF, '-v', 'error', '-i', p, '-ac', '2', '-ar', str(int(SR / rate)), '-f', 'f32le', '-'], capture_output=True)
    x = np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()   # resampled to SR/rate, played at SR → pitch*rate
    pk = np.max(np.abs(x)) + 1e-9
    x /= pk                                                         # peak-normalise every source
    env = np.sqrt(np.convolve((x ** 2).mean(1), np.ones(256) / 256, 'same'))
    _cache[key] = (x, int(np.argmax(env)))
    return _cache[key]

N = int(SR * NF / FPS) + SR * 2
sfx = np.zeros((N, 2), np.float32); verb_send = np.zeros((N, 2), np.float32)
CUES = []
def cue(path, frame, db=-12, pan=0.0, rate=1.0, align='peak', verb=0.15, fade_out=None, length=None, start=0.0):
    """place a sound so its peak (or start) lands on `frame`."""
    x, pk = load(path, rate)
    if start: x = x[int(start * SR):]; pk = max(0, pk - int(start * SR))
    if length: x = x[:int(length * SR)].copy()
    if fade_out: n = min(len(x), int(fade_out * SR)); x = x.copy(); x[-n:] *= np.linspace(1, 0, n)[:, None]
    at = int(T(frame) * SR) - (pk if align == 'peak' else 0)
    g = 10 ** (db / 20)
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    y = x * g * np.array([l * 1.414, r * 1.414], np.float32)
    s0 = max(0, at); s1 = min(N, at + len(y))
    if s1 <= s0: return
    sfx[s0:s1] += y[s0 - at:s1 - at]
    verb_send[s0:s1] += y[s0 - at:s1 - at] * verb
    CUES.append((frame, os.path.basename(path), db))

# ------------------------------------------------------------------ picture-derived timings (mirror the JS)
def kf(t, keys, ease=None):
    if t <= keys[0][0]: return keys[0][1]
    for i in range(1, len(keys)):
        if t <= keys[i][0]:
            f0, v0 = keys[i - 1][:2]; f1, v1 = keys[i][:2]; u = (t - f0) / (f1 - f0)
            u = 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2      # ioC
            return v0 + (v1 - v0) * u
    return keys[-1][1]
def phX(t): return kf(t, [[400, -11.5], [440, -7.0], [502, 7.5], [540, 10]])
def first_frame(fn, target, a, b):
    t = a
    while t < b and fn(t) < target: t += 0.25
    return t
LAYOUT_CUTS = [(-1.3, 2.2, .5), (-4.6, 2.6, .4), (0.0, 2.8, .55), (-3.0, 2.8, .45), (-1.4, 2.4, .5)]
CUT_FRAMES = sorted(first_frame(phX, x0 + L * c, 400, 540) for x0, L, c in LAYOUT_CUTS)
def spring(f, freq=2.4, damp=0.58):
    if f <= 0: return 0
    t = f / FPS; w = 2 * math.pi * freq; wd = w * math.sqrt(1 - damp ** 2)
    return 1 - math.exp(-damp * w * t) * (math.cos(wd * t) + damp * w / wd * math.sin(wd * t))
CLIPS3D = [(0, -9.4, 2.6), (0, -6.6, 1.8), (0, -4.6, 3.1), (0, -1.3, 2.2), (0, 1.1, 2.6), (0, 3.9, 2.0), (0, 6.1, 3.0),
           (1, -10.2, 3.0), (1, -7.0, 2.2), (1, -4.6, 2.6), (1, -1.8, 1.6), (1, 0.0, 2.8), (1, 3.0, 2.4), (1, 5.6, 2.8),
           (2, -9.6, 2.0), (2, -7.4, 2.8), (2, -4.4, 2.2), (2, -2.0, 3.2), (2, 1.4, 2.0), (2, 3.6, 2.6), (2, 6.4, 2.2),
           (3, -10.4, 2.4), (3, -7.8, 2.6), (3, -5.0, 1.8), (3, -3.0, 2.8), (3, 0.0, 2.2), (3, 2.4, 3.0), (3, 5.6, 2.4),
           (4, -9.8, 3.2), (4, -6.4, 2.0), (4, -4.2, 2.6), (4, -1.4, 2.4), (4, 1.2, 2.8), (4, 4.2, 2.0), (4, 6.4, 2.6)]
def settle_frame(tr, x0, L):
    x = x0 + L / 2
    ti = 384 + tr * 2.5 + ((12 - x) if tr % 2 else (x + 12)) * 0.75
    f = ti
    while spring(f - ti) < 1.0 and f < ti + 120: f += 0.5
    return f
def scrub(t): return kf(t, [[236, 0], [252, 10], [262, 4], [280, 22], [296, 30]])

# ------------------------------------------------------------------ CUE SHEET
P = lambda n: f'{PRO}/{n}.wav'
# BEAT 1 — cut
cue(f'{UI}/App Click 11.wav', 1, -16)
cue(f'{G}/blade.mp3', 9, -5, pan=-0.2)
cue(P('Sparkle Whoosh (3)'), 9, -17, pan=0.2)
cue(f'{G}/spark.mp3', 15, -16, rate=1.2, pan=0.5)
cue(P('Impact, Sub, Drop'), 22, -7, align='start', verb=0.05)
cue(P('Granular, Transform, Move, Splash (2)'), 24, -9, verb=0.2)
# BEAT 2 — crop over history (projector flutter underneath)
cue(f'{G}/projector.mp3', 24, -24, align='start', fade_out=0.25, length=2.15, verb=0.05)
for f in (54, 70, 86, 122): cue(P('Granular, Button, Select (17)'), f, -15)
for f in (64, 80, 96, 132): cue(P('Granular, Transform, Move, Splash (9)'), f, -13, verb=0.1)
for i, f in enumerate((64, 80, 96, 104, 108, 112, 116, 120, 124, 128)):
    cue(f'{G}/shutter_{"ab"[i % 2]}.mp3', f, -13 if f in (64, 80, 96) else -17, pan=(-0.25 if i % 2 else 0.25))
cue(P('Granular, Button, Select (2)'), 136, -13)
cue(f'{WH}/Magic Whoosh.mp3', 140, -19)
# BEAT 3 — type "past", modern "e", roll to sans, paste
for i, f in enumerate((150, 154, 158, 162)): cue(f'{G}/type_old_{"ab"[i % 2]}.mp3', f, -7, rate=(1.0, 1.04, 0.97, 1.02)[i], verb=0.08)
for i, f in enumerate((168, 173, 178, 183)): cue(f'{G}/pop.mp3', f, -17, rate=(1.0, 1.12, 1.26, 1.33)[i], pan=(-0.5, 0.5, 0.5, -0.5)[i])
cue(f'{LIB}/sfx/typing/keyboard-tap-modern.mp3', 196, -9)
cue(f'{UI}/App Click 2.wav', 196, -15)
cue(f'{UI}/small_whoosh_chimes_1.wav', 203, -18)
for f in (201, 204, 207, 210): cue(P('Granular, Button, Select (22)'), f + 3, -19)
PENTA = [1.0, 1.122, 1.26, 1.498, 1.682, 2.0, 2.245, 2.52, 2.997, 3.364, 4.0, 4.49]
for k in range(12): cue(f'{G}/pop.mp3', 216 + k * 1.2, -18, rate=PENTA[k] * 0.75, pan=((k % 3) - 1) * 0.5)
cue(P('Granular, Transform, Move, Splash (30)'), 230, -14)
# BEAT 4 — phenakistoscope scrub: one click per stepped frame
cue(f'{LIB}/Ieditvrs SFX/Sfx(IRL)/Turntable.wav', 240, -17)
last = 0
for f in range(236, 297):
    s = int(math.floor(scrub(f)))
    if s != last: cue(P('Granular, Button, Select (34)'), f, -24, rate=1.3 + 0.02 * (s % 5), pan=0.3); last = s
cue(P('Deep Whoosh   (1)'), 298, -10, verb=0.2)
# BEAT 5 — hands
cue(f'{G}/swing.mp3', 306, -15)
cue(f'{G}/spark.mp3', 320, -9, verb=0.35)
cue(P('Impact, Sub, Drop'), 320, -15, align='start', verb=0.05)
for i, f in enumerate(range(330, 394, 8)):
    cue(P('Granular, Button, Select (13)'), f, -15, rate=1 + 0.06 * (i % 4))
    if i % 2 == 0: cue(f'{G}/spark.mp3', f, -21, rate=1.0 + 0.1 * i, pan=0.3)
cue(f'{G}/ripple.mp3', 393, -7, verb=0.3)
cue(P('Power Up (1 sec)'), 398, -19)
# BEAT 6 — 3D timeline: magnetic snaps as each clip lands, swing, razor cuts, dive
for k, (tr, x0, L) in enumerate(CLIPS3D):
    f = settle_frame(tr, x0, L)
    if 392 <= f <= 470: cue(f'{G}/snap.mp3', f, -22, rate=0.9 + 0.25 * ((k * 7) % 5) / 4, pan=(tr - 2) * 0.3, verb=0.05)
cue(P('Deep Whoosh   (4)'), 452, -12, verb=0.25)
cue(f'{G}/swing.mp3', 455, -14)
for i, f in enumerate(CUT_FRAMES):
    cue(f'{G}/blade.mp3', f, -11, rate=1.0 + 0.05 * i, pan=-0.3 + 0.15 * i)
    cue(P('Granular, Button, Select (13)'), f, -17)
cue(P('Deep Whoosh   (1)'), 528, -8, verb=0.2)
cue(f'{G}/dive.mp3', 532, -12, align='peak')
# BEAT 7 — eye → lens: a shutter on every cut
for i, f in enumerate((540, 548, 556, 564, 572, 580, 588)):
    cue(f'{G}/shutter_{"ba"[i % 2]}.mp3', f, -11, rate=1.0 + 0.03 * i, pan=(-0.2, 0.2)[i % 2])
cue(f'{WH}/Dreamy Whoosh.wav', 600, -15)
cue(f'{WH}/Magic Whoosh.mp3', 608, -18)
cue(P('Enter'), 608, -15)
# BEAT 8 — camera → era → the line
cue(P('Granular, Button, Select (33)'), 627, -14)
cue(f'{UI}/small_whoosh_chimes_1.wav', 630, -20)
cue(f'{G}/blade.mp3', 639, -8)
cue(P('4 type & delete'), 645, -11)
cue(P('Granular, Transform, Move, Splash  (38)'), 651, -14)
for f in (674, 678, 682): cue(P('Granular, Transform, Move, Splash  (71)'), f, -21)
for i, f in enumerate((694, 698, 702)): cue(f'{G}/pop.mp3', f + 1, -14, rate=(1.5, 1.68, 1.89)[i], verb=0.2)
cue(P('Granular, Button, Select (2)'), 706, -17)
cue(f'{G}/pop.mp3', 786, -15, rate=0.8, verb=0.3)
# BEAT 9 — the spark → logo
cue(f'{G}/logo_chord_a.mp3', 789, -3, verb=0.35, align='start')
cue(f'{G}/spark.mp3', 790, -11, verb=0.5)
cue(P('Sparkle Whoosh (3)'), 796, -18, verb=0.3)
cue(P('Granular, Transform, Move, Splash (52)'), 812, -21, verb=0.3)

# ------------------------------------------------------------------ music bed: re-cut ElevenLabs track on its bar grid
mx, _ = load(f'{G}/music_a.mp3')
BEAT0, BEAT = 0.58, 60 / 112.347                     # first kick + beat length in the source
def src(a, b): return mx[int(a * SR):int(b * SR)]
bar = 4 * BEAT
b1, b3, b4 = BEAT0, BEAT0 + 2 * bar, BEAT0 + 3 * bar   # bar starts
pre = BEAT0 - T(22)                                  # first kick lands on frame 22
parts = [src(pre, b4), src(BEAT0 + bar, b4), src(b4, len(mx) / SR)]
XF = int(0.006 * SR)
music = parts[0]
for p in parts[1:]:
    a, b = music[-XF:].copy(), p[:XF].copy()
    music = np.concatenate([music[:-XF], a * np.linspace(1, 0, XF)[:, None] + b * np.linspace(0, 1, XF)[:, None], p[XF:]])
music = music[:N]
music = np.pad(music, ((0, N - len(music)), (0, 0)))
# the groove ends on the exit (~f770): fade the tail out fast, leave air before the logo chord
g = np.ones(N, np.float32)
f0, f1 = int(T(766) * SR), int(T(782) * SR)
g[f0:f1] = np.linspace(1, 0.0, f1 - f0) ** 1.6; g[f1:] = 0
music *= g[:, None] * 10 ** (-7 / 20)

# ------------------------------------------------------------------ reverb (synthetic plate) + bus
def plate(sec=1.6, pre=0.012):
    n = int(sec * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    ir = rng.standard_normal((n, 2)).astype(np.float32) * np.exp(-t / (sec / 6.9))[:, None]
    sos = butter(2, [300, 7000], 'bandpass', fs=SR, output='sos'); ir = sosfilt(sos, ir, axis=0)
    ir = np.concatenate([np.zeros((int(pre * SR), 2), np.float32), ir]); return ir / np.sqrt((ir ** 2).sum(0))
ir = plate()
wet = np.stack([fftconvolve(verb_send[:, c], ir[:, c])[:N] for c in range(2)], 1).astype(np.float32)
mix = music + sfx + wet * 0.55
# gentle glue: high-pass rumble, soft-knee compression on the sum, then a peak limiter
mix = sosfilt(butter(2, 28, 'highpass', fs=SR, output='sos'), mix, axis=0)
def compress(x, thr_db=-18, ratio=2.2, att=0.004, rel=0.12):
    lvl = np.abs(x).max(1); env = np.zeros_like(lvl); a, r = math.exp(-1 / (att * SR)), math.exp(-1 / (rel * SR)); e = 0.0
    for i, v in enumerate(lvl):
        e = a * e + (1 - a) * v if v > e else r * e + (1 - r) * v; env[i] = e
    edb = 20 * np.log10(env + 1e-9); over = np.maximum(0, edb - thr_db)
    gain = 10 ** (-(over - over / ratio) / 20); return x * gain[:, None]
mix = compress(mix)
def limiter(x, ceiling_db=-1.0, look=0.003, rel=0.06):
    c = 10 ** (ceiling_db / 20); lvl = np.abs(x).max(1); n = int(look * SR)
    need = np.minimum(1, c / (np.maximum.accumulate(np.lib.stride_tricks.sliding_window_view(np.pad(lvl, (0, n)), n + 1).max(1)) + 1e-9))
    g = np.ones_like(need); r = math.exp(-1 / (rel * SR)); cur = 1.0
    for i, v in enumerate(need):
        cur = v if v < cur else r * cur + (1 - r) * v; g[i] = cur
    return x * g[:, None]
# loudness target ≈ -14 LUFS-ish (RMS proxy), then limit
rms = np.sqrt(np.mean(mix[:int(T(NF) * SR)] ** 2)); mix *= 10 ** ((-15.5 - 20 * np.log10(rms + 1e-9)) / 20)
mix = limiter(mix)
mix = mix[:int(T(NF) * SR) + int(0.0 * SR)]
fade = int(0.25 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
out = f'{HERE}/mix.wav'
import wave
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print('cuts3D', [round(c, 1) for c in CUT_FRAMES])
print(len(CUES), 'cues  peak', round(20 * np.log10(np.abs(mix).max()), 2), 'dB  rms', round(20 * np.log10(np.sqrt(np.mean(mix ** 2))), 2), 'dB  ->', out)
