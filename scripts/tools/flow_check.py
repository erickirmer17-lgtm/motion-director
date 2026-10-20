"""flow_check.py — optical-flow check of the motion in a render (a 30 fps preview is enough).

  python3 flow_check.py render.mp4|frames_dir [--glide 0:246] [--glide 300:420] [--fps 30] [--width 360] [-o flow.csv]

Per frame pair: speed (median flow magnitude on textured pixels, px/frame at --width), direction, zoom
(radial expansion per frame: + = things grow = zoom in / dolly in, − = zoom out) and frame difference.
Flags:
  DIP      inside a --glide window (frames), speed falls > --dip (15 %) below the window's running median:
           a stop or surge in what should be one steady glide
  REVERSE  inside a --glide window, zoom flips sign against the window's majority (a pull-back that turns into a push-in)
  STALL    ≥ --stall seconds (1.2) with nothing moving (speed < 0.15 px/f and no frame change), outside holds you planned
  POP      frame difference > 3× both neighbours: a pop, or a cut (every one must be planned)
Writes flow.csv (frame, speed, dx, dy, zoom, diff) and flow.png (speed and zoom curves, flags marked).
Glide windows: frames at the render's fps, e.g. a fly-over cruise 1.6–7.3 s at 30 fps → --glide 48:219.
"""
import sys, os, glob, argparse
import numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument('src')
ap.add_argument('--glide', action='append', default=[], help='a:b frame window that must glide steadily (repeatable)')
ap.add_argument('--fps', type=float, default=0, help='frame rate (read from the video when omitted)')
ap.add_argument('--width', type=int, default=360)
ap.add_argument('--dip', type=float, default=.15)
ap.add_argument('--stall', type=float, default=1.2, help='seconds')
ap.add_argument('-o', '--out', default='')
a = ap.parse_args()


def frames():
    if os.path.isdir(a.src):
        for f in sorted(glob.glob(os.path.join(a.src, '*.png')) + glob.glob(os.path.join(a.src, '*.jpg'))):
            yield cv2.imread(f)
    else:
        cap = cv2.VideoCapture(a.src)
        while True:
            ok, im = cap.read()
            if not ok:
                break
            yield im


fps = a.fps
if not fps and not os.path.isdir(a.src):
    fps = cv2.VideoCapture(a.src).get(cv2.CAP_PROP_FPS) or 30
fps = fps or 30

rows, prev = [], None
for n, im in enumerate(frames()):
    h = int(im.shape[0] * a.width / im.shape[1]) // 2 * 2
    g = cv2.cvtColor(cv2.resize(im, (a.width, h), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    if prev is None:
        prev = g
        rows.append((0, 0., 0., 0., 0., 0.))
        continue
    fl = cv2.calcOpticalFlowFarneback(prev, g, None, .5, 4, 21, 3, 5, 1.1, 0)
    gx, gy = cv2.Sobel(prev, cv2.CV_32F, 1, 0), cv2.Sobel(prev, cv2.CV_32F, 0, 1)
    tex = np.hypot(gx, gy) > 20                     # flow is only meaningful where there is texture
    if tex.sum() < 200:
        tex[:] = True
    u, v = fl[..., 0][tex], fl[..., 1][tex]
    mag = np.hypot(u, v)
    yy, xx = np.nonzero(tex)
    cx, cy = a.width / 2, h / 2
    rx, ry = xx - cx, yy - cy
    uu, vv = u - u.mean(), v - v.mean()              # remove the pan, keep the radial part
    zoom = float((rx * uu + ry * vv).sum() / ((rx * rx + ry * ry).sum() + 1e-9))
    diff = float(np.abs(g.astype(np.float32) - prev).mean())
    rows.append((n, float(np.median(mag)), float(np.median(u)), float(np.median(v)), zoom * 100, diff))
    prev = g

R = np.array(rows)
N = len(R)
spd, zm, df = R[:, 1], R[:, 4], R[:, 5]
flags = []

for w in a.glide:
    s, e = (int(x) for x in w.split(':'))
    s, e = max(1, s), min(N - 1, e)
    seg = spd[s:e + 1]
    for i in range(s, e + 1):
        ref = np.median(spd[max(s, i - 15):min(e, i + 15) + 1])
        if ref > .3 and spd[i] < (1 - a.dip) * ref:
            flags.append((i, 'DIP', f'speed {spd[i]:.2f} vs {ref:.2f} px/f in glide {w}'))
    sg = np.sign(np.median(zm[s:e + 1])) or 1
    for i in range(s, e + 1):
        if np.sign(zm[i]) == -sg and abs(zm[i]) > .05:
            flags.append((i, 'REVERSE', f'zoom {zm[i]:+.3f}%/f against the glide ({"in" if sg > 0 else "out"})'))

still = (spd < .15) & (df < .3)
run = 0
for i in range(1, N):
    run = run + 1 if still[i] else 0
    if run == int(a.stall * fps):
        flags.append((i - run + 1, 'STALL', f'nothing moves for ≥ {a.stall:g} s from here'))

for i in range(1, N):
    ref = np.median(np.r_[df[max(1, i - 6):i], df[i + 1:i + 7]])
    if df[i] > 3 * max(ref, .5):                     # a cut = one spike; a one-frame flash = two in a row
        flags.append((i, 'POP', f'frame diff {df[i]:.1f} vs local {ref:.1f}'))

out = a.out or (os.path.splitext(a.src.rstrip('/'))[0] + '_flow')
np.savetxt(out + '.csv', R, delimiter=',', fmt=['%d', '%.3f', '%.3f', '%.3f', '%.4f', '%.2f'],
           header='frame,speed_px_f,dx,dy,zoom_pct_f,diff', comments='')
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(14, 5), sharex=True)
    ax[0].plot(R[:, 0], spd, lw=1); ax[0].set_ylabel('speed px/f')
    ax[1].plot(R[:, 0], zm, lw=1, color='C1'); ax[1].axhline(0, color='k', lw=.5); ax[1].set_ylabel('zoom %/f')
    for w in a.glide:
        s, e = (int(x) for x in w.split(':'))
        for x in ax:
            x.axvspan(s, e, color='C2', alpha=.08)
    for i, k, _ in flags:
        ax[0 if k in ('DIP', 'STALL', 'POP') else 1].axvline(i, color='r', lw=.6, alpha=.6)
    ax[1].set_xlabel(f'frame @ {fps:g} fps')
    fig.tight_layout(); fig.savefig(out + '.png', dpi=90)
except ImportError:
    pass

print(f'{N} frames @ {fps:g} fps, median speed {np.median(spd[1:]):.2f} px/f at {a.width}px wide → {out}.csv / .png')
runs = []                                            # merge consecutive frames with the same flag
for i, k, msg in sorted(flags, key=lambda x: (x[1], x[0])):
    if runs and runs[-1][1] == k and i == runs[-1][2] + 1:
        runs[-1][2] = i
    else:
        runs.append([i, k, i, msg])
for i0, k, i1, msg in sorted(runs)[:60]:
    span = f'f{i0}' if i0 == i1 else f'f{i0}–{i1}'
    print(f'  {k:<7} {span:<11} {i0 / fps:6.2f}s  {msg}')
if not flags:
    print('  clean: no dips, reversals, stalls or pops')
