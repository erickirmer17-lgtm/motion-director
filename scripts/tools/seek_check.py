"""seek_check.py — prove every frame is a pure function of its frame number (seekable + deterministic).

  python3 seek_check.py <project>/engine [--frames 12] [--to LAST] [--scale 0.4] [--tol 16]

Renders the same sample frames on ONE worker three times: ascending, shuffled, ascending again.
ORDER (ascending vs shuffled): any difference means hidden state, i.e. a value carried between renderFrame
calls, a clock, an un-seeded Math.random, or a lazy cache that depends on what was drawn first. Such a
scene renders differently with different --workers and can't re-render one section on its own.
NOISE (ascending vs ascending): a frame that changes between identical runs points at async loading or a
renderer that isn't deterministic.
--tol is the per-pixel difference (0-255) ignored as anti-alias jitter; --tol 0 is bit-exact.
Run it once the first beats exist and again before the final render. Format comes from engine/FORMAT
(written by new_project.sh). Frames go to a temp dir that is deleted afterwards. Exit code 1 on failure.
"""
import sys, os, re, random, shutil, subprocess, tempfile
import numpy as np
from PIL import Image


def arg(name, default=None, cast=str):
    return cast(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


eng = os.path.abspath(sys.argv[1])
fmt = open(f'{eng}/FORMAT').read() if os.path.exists(f'{eng}/FORMAT') else ''
fa = dict(re.findall(r'--(w|h|fps) (\d+)', fmt))
m = re.search(r'frames 0\.\.(\d+)', fmt)
last = arg('--to', int(m.group(1)) if m else 899, int)
n, scale, tol = arg('--frames', 12, int), arg('--scale', 0.4, float), arg('--tol', 16, int)
step = max(1, last // n)
frames = list(range(0, last + 1, step))[:n]
shuffled = frames[:]; random.Random(7).shuffle(shuffled)
fmt_args = sum([[f'--{k}', v] for k, v in fa.items()], [])

tmp = tempfile.mkdtemp(prefix='seek_check_')
try:
    for name, order in (('asc', frames), ('shuf', shuffled), ('asc2', frames)):
        cmd = ['node', 'capture.js', '--list', ','.join(map(str, order)), '--out', f'{tmp}/{name}',
               '--scale', str(scale), '--workers', '1', *fmt_args]
        r = subprocess.run(cmd, cwd=eng, capture_output=True, text=True)
        if r.returncode: sys.exit(f'capture failed ({name}):\n{r.stdout}\n{r.stderr}')
    load = lambda d, f: np.asarray(Image.open(f'{tmp}/{d}/f{f:04d}.png').convert('RGB'), dtype=np.int16)
    bad = []
    for f in frames:
        a = load('asc', f)
        for kind, other in (('ORDER', 'shuf'), ('NOISE', 'asc2')):
            d = np.abs(a - load(other, f)).max(axis=2)
            frac = (d > tol).mean()
            if frac > 0: bad.append((kind, f, int(d.max()), frac))
    print(f'checked {len(frames)} frames {frames[0]}..{frames[-1]} (1 worker, tol {tol})')
    if bad:
        for kind, f, mx, frac in bad: print(f'  {kind} f{f}: max diff {mx}, {frac * 100:.3f}% px')
        if any(b[0] == 'ORDER' for b in bad):
            print('ORDER = hidden state: values kept between frames, Math.random, Date/performance.now, lazy caches.')
        if any(b[0] == 'NOISE' for b in bad):
            print('NOISE = differs between identical runs: an image/font still loading after READY, or GPU raster.')
        sys.exit(1)
    print('PASS: every sampled frame is independent of render order and stable between runs')
finally:
    shutil.rmtree(tmp, ignore_errors=True)
