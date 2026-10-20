"""mixer.py — frame-locked sound-design mixer (cue sheet → mix.wav).

Import it from a project's audio/mix.py:

    import sys; sys.path.insert(0, '<skill>/scripts/tools'); from mixer import Mixer
    m = Mixer(fps=60, frames=900)
    m.music('gen/music.mp3', first_kick_src=0.58, first_kick_frame=22, bpm=112.35,
            bars=[(0, 3), (1, 3), (3, None)], db=-7, fade=(766, 782))   # optional bar re-cut
    m.cue(PATH, frame, db=-12, pan=0, rate=1.0, align='peak'|'start', verb=0.15)
    m.render('mix.wav', lufs_proxy=-15.5, ceiling=-1.0)          # also writes mix.cues.json for earshot

Why it works:
- every source is peak-normalised, then placed so its *transient peak* lands on the event frame
  (align='peak') — ticks feel glued to the cut instead of late;
- `rate` = varispeed pitch (resample) for pitched families (rising pops, scrub clicks);
- one synthetic plate reverb send glues library sounds from different origins;
- gentle bus compression + look-ahead limiter → consistent, social-ready loudness.
"""
import os, math, json, subprocess, wave
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

FF = os.environ.get('FFMPEG', '/Users/user/Library/Python/3.9/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1')


class Mixer:
    def __init__(self, fps=60, frames=900, sr=48000, tail=2.0):
        self.fps, self.frames, self.sr = fps, frames, sr
        self.N = int(sr * frames / fps) + int(sr * tail)
        self.sfx = np.zeros((self.N, 2), np.float32)
        self.send = np.zeros((self.N, 2), np.float32)
        self.bed = np.zeros((self.N, 2), np.float32)
        self.cues = []
        self._cache = {}

    def T(self, f):
        return f / self.fps

    def load(self, path, rate=1.0):
        key = (path, rate)
        if key not in self._cache:
            r = subprocess.run([FF, '-v', 'error', '-i', path, '-ac', '2', '-ar', str(int(self.sr / rate)), '-f', 'f32le', '-'],
                               capture_output=True)
            x = np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()
            if not len(x): raise FileNotFoundError(path)
            x /= (np.abs(x).max() + 1e-9)
            env = np.sqrt(np.convolve((x ** 2).mean(1), np.ones(256) / 256, 'same'))
            self._cache[key] = (x, int(np.argmax(env)))
        return self._cache[key]

    def cue(self, path, frame, db=-12, pan=0.0, rate=1.0, align='peak', verb=0.15, length=None, fade_out=None, start=0.0):
        x, pk = self.load(path, rate)
        if start: x = x[int(start * self.sr):]; pk = max(0, pk - int(start * self.sr))
        if length: x = x[:int(length * self.sr)].copy()
        if fade_out:
            n = min(len(x), int(fade_out * self.sr)); x = x.copy(); x[-n:] *= np.linspace(1, 0, n)[:, None]
        at = int(self.T(frame) * self.sr) - (pk if align == 'peak' else 0)
        g = 10 ** (db / 20)
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        y = x * g * np.array([l * 1.414, r * 1.414], np.float32)
        s0, s1 = max(0, at), min(self.N, at + len(y))
        if s1 <= s0: return
        self.sfx[s0:s1] += y[s0 - at:s1 - at]
        self.send[s0:s1] += y[s0 - at:s1 - at] * verb
        self.cues.append((frame, os.path.basename(path), db))

    def music(self, path, first_kick_src, first_kick_frame, bpm=None, bars=None, db=-7, fade=None, beats_per_bar=4, xfade=0.006):
        """Place a music bed so its first downbeat lands on `first_kick_frame`.
        bars: optional list of (bar_from, bar_to) in SOURCE bars (0 = bar starting at first_kick_src; None = to end)
        to re-order/extend the track on its own grid (e.g. repeat the peak bars so the groove ends where the picture needs).
        fade: (frame_a, frame_b) fade the bed to silence (leave air before a logo hit)."""
        x, _ = self.load(path)
        sr = self.sr
        pre = first_kick_src - self.T(first_kick_frame)
        if bars and bpm:
            bar = beats_per_bar * 60 / bpm
            seg = lambda a, b: x[int(a * sr):(int(b * sr) if b is not None else len(x))]
            parts = []
            for i, (b0, b1) in enumerate(bars):
                a = first_kick_src + b0 * bar if not (i == 0 and b0 == 0) else pre
                b = first_kick_src + b1 * bar if b1 is not None else None
                parts.append(seg(a, b))
            n = int(xfade * sr); out = parts[0]
            for p in parts[1:]:
                out = np.concatenate([out[:-n], out[-n:] * np.linspace(1, 0, n)[:, None] + p[:n] * np.linspace(0, 1, n)[:, None], p[n:]])
        else:
            out = x[int(max(0, pre) * sr):]
            if pre < 0: out = np.concatenate([np.zeros((int(-pre * sr), 2), np.float32), out])
        out = out[:self.N]; out = np.pad(out, ((0, self.N - len(out)), (0, 0)))
        g = np.ones(self.N, np.float32)
        if fade:
            a, b = int(self.T(fade[0]) * sr), int(self.T(fade[1]) * sr)
            g[a:b] = np.linspace(1, 0, b - a) ** 1.6; g[b:] = 0
        self.bed += out * g[:, None] * 10 ** (db / 20)

    @staticmethod
    def _plate(sr, sec=1.6, pre=0.012):
        n = int(sec * sr); t = np.arange(n) / sr
        ir = np.random.default_rng(7).standard_normal((n, 2)).astype(np.float32) * np.exp(-t / (sec / 6.9))[:, None]
        ir = sosfilt(butter(2, [300, 7000], 'bandpass', fs=sr, output='sos'), ir, axis=0)
        ir = np.concatenate([np.zeros((int(pre * sr), 2), np.float32), ir])
        return ir / np.sqrt((ir ** 2).sum(0))

    def render(self, out, lufs_proxy=-15.5, ceiling=-1.0, wet=0.55, end_fade=0.25):
        sr = self.sr
        ir = self._plate(sr)
        verb = np.stack([fftconvolve(self.send[:, c], ir[:, c])[:self.N] for c in range(2)], 1).astype(np.float32)
        mix = self.bed + self.sfx + verb * wet
        mix = sosfilt(butter(2, 28, 'highpass', fs=sr, output='sos'), mix, axis=0)
        mix = self._compress(mix)
        L = int(self.T(self.frames) * sr)
        rms = np.sqrt(np.mean(mix[:L] ** 2))
        mix *= 10 ** ((lufs_proxy - 20 * np.log10(rms + 1e-9)) / 20)
        mix = self._limit(mix, ceiling)[:L]
        n = int(end_fade * sr); mix[-n:] *= np.linspace(1, 0, n)[:, None]
        with wave.open(out, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
        print(f'{len(self.cues)} cues  peak {20 * np.log10(np.abs(mix).max()):.2f} dB  rms {20 * np.log10(np.sqrt(np.mean(mix ** 2))):.2f} dB -> {out}')
        self.write_cues(os.path.splitext(out)[0] + '.cues.json')
        return out

    def write_cues(self, path, merge=1.5):
        """earshot cue sheet ({fps, events:[{f, kind, id}]}) for `earshot timeline/sheet --cues`; layered cues
        within `merge` frames count as one event (the earliest, then loudest, names it)"""
        ev, seen = [], []
        for f, name, db in sorted(self.cues, key=lambda c: (c[0], -c[2])):
            if any(abs(f - s) < merge for s in seen): continue
            seen.append(f); ev.append({'f': round(float(f), 2), 'kind': 'cue', 'id': f'{name}@{f:g}'})
        with open(path, 'w') as fh: json.dump({'fps': self.fps, 'events': ev}, fh, indent=1)
        return path

    def _compress(self, x, thr_db=-18, ratio=2.2, att=0.004, rel=0.12):
        lvl = np.abs(x).max(1); env = np.zeros_like(lvl)
        a, r = math.exp(-1 / (att * self.sr)), math.exp(-1 / (rel * self.sr)); e = 0.0
        for i, v in enumerate(lvl):
            e = a * e + (1 - a) * v if v > e else r * e + (1 - r) * v; env[i] = e
        over = np.maximum(0, 20 * np.log10(env + 1e-9) - thr_db)
        return x * (10 ** (-(over - over / ratio) / 20))[:, None]

    def _limit(self, x, ceiling_db=-1.0, look=0.003, rel=0.06):
        c = 10 ** (ceiling_db / 20); lvl = np.abs(x).max(1); n = int(look * self.sr)
        win = np.lib.stride_tricks.sliding_window_view(np.pad(lvl, (0, n)), n + 1).max(1)
        need = np.minimum(1, c / (win + 1e-9)); g = np.ones_like(need); r = math.exp(-1 / (rel * self.sr)); cur = 1.0
        for i, v in enumerate(need):
            cur = v if v < cur else r * cur + (1 - r) * v; g[i] = cur
        return x * g[:, None]
