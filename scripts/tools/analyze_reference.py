"""analyze_reference.py — break a reference video down before designing anything.

  python3 analyze_reference.py ref.mp4 outdir/ [--fps-sheet 15]

Writes:
  outdir/frames/NNNN.png        every frame at 270 px wide (for frame-exact study)
  outdir/sheet_XX.jpg           labelled contact sheets (frame # + seconds) — read these, all of them
  outdir/cuts.txt               frame-difference spikes (cut / fast-move candidates)
  outdir/audio_onsets.txt       spectral-flux onsets + 0.25 s loudness ladder
  outdir/spectrogram.png        log-frequency spectrogram (music vs SFX structure, silences, risers, logo chord)
Study list: shot durations (frames), what persists across cuts (the continuity element), type sizes/fonts,
palette, how each morph is built, where the audio breathes. Write it up as ANALYSIS.md (see x_recreate/ANALYSIS.md).
"""
import sys, os, glob, subprocess
import numpy as np, cv2
import scipy.io.wavfile as wav, scipy.signal as ss

FF = os.environ.get('FFMPEG', '/Users/user/Library/Python/3.9/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1')
src, out = sys.argv[1], sys.argv[2]
step_fps = int(sys.argv[sys.argv.index('--fps-sheet') + 1]) if '--fps-sheet' in sys.argv else 15
os.makedirs(f'{out}/frames', exist_ok=True)
info = subprocess.run([FF, '-i', src], capture_output=True, text=True).stderr
fps = float([l for l in info.split('\n') if ' fps' in l][0].split(' fps')[0].split(',')[-1])
subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-vf', 'scale=270:-2', f'{out}/frames/%04d.png'])
subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', '22050', f'{out}/audio.wav'])
subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-lavfi', 'showspectrumpic=s=1800x400:legend=1:scale=log:fscale=log', f'{out}/spectrogram.png'])
fs = sorted(glob.glob(f'{out}/frames/*.png'))
# cuts
prev, d = None, []
for f in fs:
    im = cv2.imread(f, 0).astype(np.float32); d.append(0 if prev is None else float(np.mean(np.abs(im - prev)))); prev = im
d = np.array(d)
with open(f'{out}/cuts.txt', 'w') as fo:
    thr = max(6.0, np.percentile(d, 90))
    for i, v in enumerate(d):
        if v > thr: fo.write(f'{i}\t{i / fps:.3f}s\t{v:.1f}\n')
# contact sheets
step = max(1, round(fps / step_fps)); idx = list(range(0, len(fs), step)); per = 40
for s in range(0, len(idx), per):
    tiles = []
    for i in idx[s:s + per]:
        im = cv2.resize(cv2.imread(fs[i]), (180, int(180 * cv2.imread(fs[i]).shape[0] / cv2.imread(fs[i]).shape[1])))
        cv2.putText(im, f'{i} {i / fps:.2f}', (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1); tiles.append(im)
    while len(tiles) % 10: tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(f'{out}/sheet_{s // per:02d}.jpg', np.vstack([np.hstack(tiles[r:r + 10]) for r in range(0, len(tiles), 10)]))
# audio
sr, x = wav.read(f'{out}/audio.wav'); x = x.astype(np.float32) / 32768
hop = int(sr * 0.01); f_, t_, Z = ss.stft(x, sr, nperseg=1024, noverlap=1024 - hop); S = np.abs(Z)
flux = np.maximum(0, np.diff(np.log1p(S * 100), axis=1)).sum(0); flux = (flux - flux.mean()) / (flux.std() + 1e-9)
pk, _ = ss.find_peaks(flux, height=1.5, distance=8)
with open(f'{out}/audio_onsets.txt', 'w') as fo:
    fo.write('onsets (s): ' + ' '.join(f'{t_[p + 1]:.2f}' for p in pk) + '\n')
    for i in range(0, len(x) // (sr // 4)):
        seg = x[i * sr // 4:(i + 1) * sr // 4]; db = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)
        fo.write(f'{i / 4:5.2f}s {db:6.1f} ' + '#' * int(max(0, (db + 60) / 1.5)) + '\n')
print(f'{len(fs)} frames @ {fps} fps → {out}  (read every sheet_*.jpg, cuts.txt, audio_onsets.txt, spectrogram.png)')
