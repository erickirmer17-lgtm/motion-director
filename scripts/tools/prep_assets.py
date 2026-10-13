"""prep.py — turn raw downloads / generations into engine-ready images + manifest.json.

kinds:
  ink   engraving/line art on paper -> RGBA, ink colour, alpha = darkness (paper becomes transparent)
  photo B&W photo kept rectangular (used with cover-fit inside frames)
  cut   RGBA cut-out (bg removed upstream) -> desaturated, cropped to content
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW, GEN, OUT = [os.path.join(HERE, d) for d in ('raw', 'gen', 'img')]
os.makedirs(OUT, exist_ok=True)
INK = np.array([16, 16, 16], np.float32)
MAXD = 2200

# SPEC lives in the project: assets/prep_spec.json → {"key": ["raw/file.jpg", "ink|photo|cut", {options}], …}
# (example from ai_editing_era: references/assets.md → "prep_spec example")
_spec_file = os.path.join(HERE, 'prep_spec.json')
SPEC = {k: tuple(v) for k, v in json.load(open(_spec_file)).items()} if os.path.exists(_spec_file) else {}


def resolve(p):
    full = os.path.join(HERE, p)
    if os.path.exists(full): return full
    stem = os.path.splitext(full)[0]
    for ext in ('.jpg', '.png', '.gif', '.jpeg'):
        if os.path.exists(stem + ext): return stem + ext
    return None


def load(p):
    im = Image.open(resolve(p))
    if getattr(im, 'n_frames', 1) > 1: im.seek(0)
    return im


def fit(im, maxd):
    s = maxd / max(im.size)
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS) if s < 1 else im


def crop_alpha(rgba, thr=0.04, margin=12):
    a = rgba[..., 3]
    ys, xs = np.where(a > thr * 255)
    if not len(ys): return rgba
    y0, y1 = max(ys.min() - margin, 0), min(ys.max() + margin + 1, a.shape[0])
    x0, x1 = max(xs.min() - margin, 0), min(xs.max() + margin + 1, a.shape[1])
    return rgba[y0:y1, x0:x1]


def do_ink(im, o):
    g = np.asarray(im.convert('L'), np.float32) / 255
    # paper level: robust high percentile of a blurred copy (local paper tone handles stains/vignettes)
    bl = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(g.shape) / 40)), np.float32) / 255
    paper = np.maximum(bl, np.percentile(g, 92))
    paper = np.maximum(paper, g)  # never darker than the pixel itself
    ink = np.percentile(g, 1.5)
    a = np.clip((paper - g) / np.maximum(paper - ink - 0.05, 0.15), 0, 1)
    a = np.clip((a - 0.06) / 0.94, 0, 1) ** o.get('gamma', 0.9)
    rgba = np.dstack([np.broadcast_to(INK, g.shape + (3,)), a * 255]).astype(np.uint8)
    return crop_alpha(rgba, 0.12, 16)


def do_photo(im, o):
    g = np.asarray(im.convert('L'), np.float32)
    lo, hi = np.percentile(g, 0.5), np.percentile(g, 99.6)
    g = np.clip((g - lo) / max(hi - lo, 1), 0, 1)
    g = g ** o.get('gamma', 1.0)
    return np.dstack([g * 255] * 3 + [np.full(g.shape, 255)]).astype(np.uint8)


def do_cut(im, o):
    im = im.convert('RGBA'); a = np.asarray(im, np.float32)
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    sat = o.get('sat', 0.0)
    rgb = a[..., :3] * sat + lum[..., None] * (1 - sat)
    out = np.dstack([rgb, a[..., 3]]).astype(np.uint8)
    return crop_alpha(out, 0.02, 6)


def main(keys=None):
    if not SPEC: sys.exit('no assets/prep_spec.json yet — list your sources there (see references/assets.md)')
    man = {}
    mf = os.path.join(HERE, 'manifest.json')
    if os.path.exists(mf): man = json.load(open(mf))
    for k, (src, kind, o) in SPEC.items():
        if keys and k not in keys:
            continue
        if not resolve(src):
            print('missing', k, src); continue
        im = fit(load(src), o.get('max', MAXD))
        arr = {'ink': do_ink, 'photo': do_photo, 'cut': do_cut}[kind](im, o)
        fn = f'{k}.png' if kind != 'photo' else f'{k}.jpg'
        pim = Image.fromarray(arr, 'RGBA')
        if kind == 'photo': pim.convert('RGB').save(os.path.join(OUT, fn), quality=93)
        else: pim.save(os.path.join(OUT, fn), optimize=False)
        man[k] = {'src': f'../assets/img/{fn}', 'kind': kind, 'w': pim.width, 'h': pim.height}
        print(k, kind, pim.size)
    json.dump(man, open(mf, 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
