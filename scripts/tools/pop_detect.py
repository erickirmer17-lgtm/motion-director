"""pop_detect.py — find every frame-to-frame jump in a rendered PNG/JPG sequence.

  python3 pop_detect.py render/v2 [--top 60] [--cuts 64,80,96,...]

Lists the largest mean-abs-difference spikes. Every spike must be an intended cut or a fast move;
anything else is a pop (a morph that doesn't land, a layer that appears a frame early, a hand-off
mismatch). A perfect morph / hand-off does NOT show up in this list at all.
"""
import sys, glob
import numpy as np
from PIL import Image

d0 = sys.argv[1]
top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 60
cuts = set(int(v) for v in sys.argv[sys.argv.index('--cuts') + 1].split(',')) if '--cuts' in sys.argv else set()
fs = sorted(glob.glob(f'{d0}/*.png') + glob.glob(f'{d0}/*.jpg'))
prev, d = None, []
for f in fs:
    a = np.asarray(Image.open(f).convert('L').resize((270, 480)), np.float32)
    d.append(0 if prev is None else float(np.mean(np.abs(a - prev)))); prev = a
d = np.array(d)
for i in sorted(np.argsort(d)[::-1][:top]):
    tag = 'cut' if i in cuts else ''
    print(f'f{i:4d}  {d[i]:6.1f}  {tag}')
