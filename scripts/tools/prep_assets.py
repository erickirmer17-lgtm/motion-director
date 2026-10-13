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

SPEC = {
    # ---- ink (engravings / line drawings)
    'ecr_canif':    ('raw/ecriture_00.jpg', 'ink', {}),
    'ecr_alpha':    ('raw/ecriture_02.jpg', 'ink', {}),
    'turk':         ('raw/turk_08.jpg', 'ink', {}),
    'turk_col':     ('raw/turk_00.jpg', 'ink', {'gamma': 0.8}),
    'jd_profile':   ('raw/jaquetdroz_05.jpg', 'ink', {}),
    'jd_dog':       ('raw/jaquetdroz_07.jpg', 'ink', {}),
    'durer_hands':  ('raw/durer_hands_07.jpg', 'ink', {}),
    'durer_book':   ('raw/durer_hands_12.jpg', 'ink', {}),
    'durer_pray':   ('raw/durer_hands_13.jpg', 'ink', {'gamma': 0.75}),
    'vaucanson':    ('raw/vaucanson_01.jpg', 'ink', {}),
    'jacquard':     ('raw/jacquard_01.jpg', 'ink', {}),
    'jacquard_card':('raw/jacquard_07.jpg', 'ink', {}),
    'jacquard_m':   ('raw/jacquard_03.png', 'ink', {}),
    'typecase':     ('raw/imprimerie_00.jpg', 'ink', {}),
    'imprimerie':   ('raw/imprimerie_01.jpg', 'ink', {}),
    'composition':  ('raw/imprimerie_02.jpg', 'ink', {}),
    'cam_obscura':  ('raw/camera_obscura_00.jpg', 'ink', {}),
    'optics':       ('raw/camera_obscura_01.jpg', 'ink', {}),
    'typewriter':   ('raw/typewriter_00.jpg', 'ink', {}),
    'praxi_proj':   ('raw/praxinoscope_07.jpg', 'ink', {}),
    'praxi':        ('raw/praxinoscope_04.jpg', 'ink', {}),
    'kin_camera':   ('raw/kinetoscope_01.jpg', 'ink', {}),
    'kin_tripod':   ('raw/kinetoscope_02.jpg', 'ink', {}),
    'kin_proj':     ('raw/kinetoscope_04.jpg', 'ink', {}),
    'marey_hurdle': ('raw/marey_07.png', 'ink', {}),
    'marey_disc':   ('raw/marey_06.jpg', 'ink', {}),
    'steamman':     ('raw/steamman_00.jpg', 'ink', {'gamma': 0.8}),
    'vesalius':     ('raw/vesalius_hand_01.png', 'ink', {}),
    'robot_engr':   ('gen/engraving_robot_arm.png', 'ink', {}),
    # ---- photos (rectangular, B&W)
    'adam':         ('raw/adam_00.jpg', 'photo', {}),
    'adam_hands':   ('raw/adam_01.jpg', 'photo', {}),
    'melies':       ('raw/melies_moon_05.jpg', 'photo', {}),
    'melies_cannon':('raw/melies_moon_10.jpg', 'photo', {}),
    'melies_draw':  ('raw/melies_moon_02.jpg', 'photo', {}),
    'metro_scene':  ('raw/metropolis_01.jpg', 'photo', {}),
    'praxi_photo':  ('raw/praxinoscope_01.jpg', 'photo', {}),
    'moviola_b':    ('raw/film_editor_05.jpg', 'photo', {}),
    'jd_writer_b':  ('raw/jaquetdroz_10.jpg', 'photo', {}),
    'phen_rats':    ('raw/phenakistoscope_00.jpg', 'photo', {}),
    'phen_cats':    ('raw/phenakistoscope_09.jpg', 'photo', {}),
    'phen_stampfer':('raw/phenakistoscope_04.gif', 'photo', {}),
    'phen_couple':  ('raw/phenakistoscope_03.gif', 'photo', {}),
    'muybridge':    ('raw/muybridge_horse_04.jpg', 'photo', {'max': 3840}),
    # ---- cut-outs (generated, bg removed)
    'r_point':      ('gen/robot_point_cut.png', 'cut', {}),
    'r_film':       ('gen/robot_film_cut.png', 'cut', {}),
    'r_scissors':   ('gen/robot_scissors_cut.png', 'cut', {}),
    'r_pinch':      ('gen/robot_pinch_cut.png', 'cut', {}),
    'android':      ('gen/marble_android_cut.png', 'cut', {}),
    'head_front':   ('gen/head_front_cut.png', 'cut', {}),
    'head_r':       ('gen/head_r_cut.png', 'cut', {}),
    'head_l':       ('gen/head_l_cut.png', 'cut', {}),
    'head_b':       ('gen/head_b_cut.png', 'cut', {}),
    'moviola_c':    ('gen/moviola_c_cut.png', 'cut', {}),
    'moviola':      ('gen/moviola_a_cut.png', 'cut', {}),
    'metro_robot':  ('gen/metro_robot_cut.png', 'cut', {}),
    'jd_writer':    ('gen/jd_writer_cut.png', 'cut', {}),
    'adam_hand':    ('gen/adam_hand_cut.png', 'cut', {}),
    'god_hand':     ('gen/god_hand_cut.png', 'cut', {}),
}


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
