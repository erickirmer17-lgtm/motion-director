"""pop_detect.py — find every frame-to-frame jump in a rendered PNG/JPG sequence.

  python3 pop_detect.py <dir> [--top 60] [--cuts 64,80,96] [--crop x0,y0,x1,y1] [--from A --to B]

Frame numbers come from the file names (works on partial / --list re-renders; gaps are skipped, not
diffed across). --crop measures one region only (e.g. the logo spark) so a tiny pop isn't drowned by
the rest of the frame. Every spike must be an intended cut or a fast move; a perfect morph or 3D→2D
hand-off does not appear in the list at all.
"""
import sys, glob, re, os
import numpy as np
from PIL import Image


def arg(name, default=None, cast=str):
    return cast(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


d0 = sys.argv[1]
top = arg('--top', 60, int)
cuts = set(int(v) for v in arg('--cuts', '').split(',') if v)
crop = tuple(int(v) for v in arg('--crop').split(',')) if arg('--crop') else None
a, b = arg('--from', 0, int), arg('--to', 10 ** 9, int)
files = {}
for f in glob.glob(f'{d0}/*.png') + glob.glob(f'{d0}/*.jpg'):
    m = re.search(r'(\d+)\.(png|jpg)$', os.path.basename(f))
    if m and a <= int(m.group(1)) <= b: files[int(m.group(1))] = f
prev_k, prev, res = None, None, []
for k in sorted(files):
    im = Image.open(files[k]).convert('L')
    if crop: im = im.crop(crop)
    w = 270 if not crop else min(540, im.width)
    arr = np.asarray(im.resize((w, max(1, int(im.height * w / im.width)))), np.float32)
    if prev is not None and k == prev_k + 1:
        diff = np.abs(arr - prev)
        res.append((k, float(diff.mean()), float((diff > 40).mean() * 100)))
    prev_k, prev = k, arr
if not res: sys.exit('need at least two consecutive frames')
res.sort(key=lambda r: -r[1])
print(' frame   meanΔ   %px>40')
for k, m, p in sorted(res[:top]):
    print(f'f{k:5d}  {m:6.1f}  {p:6.2f}  {"cut" if k in cuts else ""}')
