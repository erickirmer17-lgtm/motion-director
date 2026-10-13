"""sheet.py — labelled contact sheet from any rendered frame folder (PNG or JPG, full range or --list renders).

  python3 sheet.py <dir> <out.jpg> [--from A] [--to B] [--step N] [--cols 10] [--width 216] [--crop x0,y0,x1,y1]

Frame numbers come from the file names (f0067.png → 67), so partial / --list renders work. --crop zooms
into a region (full-res pixel coords) — use it to inspect a morph up close.
"""
import sys, glob, re, os
from PIL import Image, ImageDraw, ImageFont


def arg(name, default=None, cast=str):
    return cast(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


d, out = sys.argv[1], sys.argv[2]
a, b, step = arg('--from', 0, int), arg('--to', 10 ** 9, int), arg('--step', 1, int)
cols, tw = arg('--cols', 10, int), arg('--width', 216, int)
crop = tuple(int(v) for v in arg('--crop').split(',')) if arg('--crop') else None
files = {}
for f in glob.glob(f'{d}/*.png') + glob.glob(f'{d}/*.jpg'):
    m = re.search(r'(\d+)\.(png|jpg)$', os.path.basename(f))
    if m: files.setdefault(int(m.group(1)), f)
frames = [k for k in sorted(files) if a <= k <= b][::step]
if not frames: sys.exit(f'no frames in {d} for {a}..{b}')
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14) if os.path.exists('/System/Library/Fonts/Helvetica.ttc') else ImageFont.load_default()
tiles = []
for k in frames:
    im = Image.open(files[k]).convert('RGB')
    if crop:
        sx = im.width / max(crop[2], im.width) if False else 1
        im = im.crop(crop)
    th = int(im.height * tw / im.width)
    t = im.resize((tw, th)); dr = ImageDraw.Draw(t)
    dr.text((3, 3), str(k), fill=(255, 0, 0), font=font); dr.rectangle([0, 0, tw - 1, th - 1], outline=(200, 200, 200))
    tiles.append(t)
th = max(t.height for t in tiles); rows = (len(tiles) + cols - 1) // cols
s = Image.new('RGB', (cols * tw, rows * th), 'white')
for i, t in enumerate(tiles): s.paste(t, ((i % cols) * tw, (i // cols) * th))
s.save(out, quality=88)
print(f'{len(tiles)} frames → {out}')
