"""Rise & Fall — compositor core.
All shot code is written in REFERENCE pixels (2880x2160). init(scale) sets the render size;
helpers multiply by S internally. Images are float32 RGB in [0,1] display space.
"""
import cv2, numpy as np, json, math, functools, os
from PIL import Image, ImageDraw, ImageFont

cv2.setNumThreads(2)
ROOT = '/Users/user/Documents/Claude Opp./10_October/rise_fall'
FPS = 24000 / 1001
REF_W, REF_H = 2880, 2160
NF = 492
FONT = f'{ROOT}/assets/fonts/outfit.ttf'

S = 1.0; W = REF_W; H = REF_H

# palette (scene space; finish() lifts blacks / rolls whites)
INK = np.array([0.13, 0.08, 0.06], np.float32)
RED = np.array([0.88, 0.03, 0.03], np.float32)
OCHRE = np.array([0.66, 0.16, 0.08], np.float32)
WHITE = np.array([0.97, 0.96, 0.95], np.float32)
CYAN = np.array([0.30, 0.90, 0.92], np.float32)


def init(scale):
    global S, W, H
    S = scale; W = int(round(REF_W * scale)); H = int(round(REF_H * scale))
    for f in (paper_tex, dark_tex, sprite, sprite_up, thermal_plate, photo_plate, _font):
        f.cache_clear()


def P(v):
    return v * S


def ease_out(x, p=3):
    x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** p


def ease_in(x, p=3):
    x = min(max(x, 0.0), 1.0); return x ** p


def ease_io(x):
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def clamp01(x):
    return min(max(x, 0.0), 1.0)


def prog(t, a, b):
    return clamp01((t - a) / (b - a)) if b > a else float(t >= a)


# ---------------------------------------------------------------- backgrounds
def _noise(rng, sx, sy, w, h):
    return cv2.resize(rng.standard_normal((sy, sx)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)


@functools.lru_cache(maxsize=4)
def paper_tex(variant=0):
    rng = np.random.default_rng(11 + variant)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W * 0.5) / (W * 0.62)) ** 2 + ((yy - H * 0.48) / (H * 0.62)) ** 2)
    base = 0.905 - 0.115 * r ** 2
    lf = _noise(rng, 10, 8, W, H) * 0.010 + _noise(rng, 60, 45, W, H) * 0.006
    fine = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), max(0.6, 0.9 * S)) * 0.012
    v = base + lf + fine
    # paper fibres
    fib = np.zeros((H, W), np.float32)
    for _ in range(int(900 * S * S) + 40):
        x, y = rng.uniform(0, W), rng.uniform(0, H); a = rng.uniform(0, math.pi); L = rng.uniform(8, 40) * S
        cv2.line(fib, (int(x), int(y)), (int(x + math.cos(a) * L), int(y + math.sin(a) * L)), float(rng.uniform(0.3, 1)), 1, cv2.LINE_AA)
    v -= cv2.GaussianBlur(fib, (0, 0), 0.6) * 0.018
    img = np.dstack([v * 0.992, v * 0.988, v * 1.0]).astype(np.float32)
    return img


@functools.lru_cache(maxsize=2)
def dark_tex(variant=0):
    rng = np.random.default_rng(31 + variant)
    v = np.abs(_noise(rng, 14, 10, W, H)) * 0.010 + _noise(rng, 90, 68, W, H) * 0.004 + 0.004
    v = np.clip(v, 0, 1)
    return np.dstack([v * 1.02, v, v * 0.98]).astype(np.float32)


def paper():
    return paper_tex(0).copy()


def dark():
    return dark_tex(0).copy()


def solid(rgb):
    img = np.empty((H, W, 3), np.float32); img[:] = rgb
    rng = np.random.default_rng(5)
    img *= (1 + _noise(rng, 12, 9, W, H)[..., None] * 0.02)
    return img


# ---------------------------------------------------------------- compositing
def over_pm(canvas, pm_rgb, a, x0, y0):
    """premultiplied rgb + alpha patch, top-left at integer render coords"""
    h, w = a.shape
    cx0, cy0 = max(0, x0), max(0, y0); cx1, cy1 = min(W, x0 + w), min(H, y0 + h)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    sx0, sy0 = cx0 - x0, cy0 - y0
    aa = a[sy0:sy0 + cy1 - cy0, sx0:sx0 + cx1 - cx0][..., None]
    cr = canvas[cy0:cy1, cx0:cx1]
    cr *= (1 - aa); cr += pm_rgb[sy0:sy0 + cy1 - cy0, sx0:sx0 + cx1 - cx0]


def add_patch(canvas, rgb, x0, y0):
    h, w = rgb.shape[:2]
    cx0, cy0 = max(0, x0), max(0, y0); cx1, cy1 = min(W, x0 + w), min(H, y0 + h)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    canvas[cy0:cy1, cx0:cx1] += rgb[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]


def to_pm(rgba):
    a = rgba[..., 3:4]
    return np.dstack([rgba[..., :3] * a, rgba[..., 3:4]])


def place(canvas, pm, cx, cy, scale=1.0, rot=0.0, alpha=1.0, anchor=(0.5, 0.5), interp=cv2.INTER_LINEAR,
          tint=None, tint_amt=0.0, sx=None, sy=None):
    """pm: premultiplied float32 RGBA. cx,cy in RENDER px. scale: render px per source px. rot in degrees."""
    if alpha <= 0.001:
        return
    h, w = pm.shape[:2]
    sx = scale if sx is None else sx; sy = scale if sy is None else sy
    th = math.radians(rot); c, s = math.cos(th), math.sin(th)
    ax, ay = anchor[0] * w, anchor[1] * h
    M = np.array([[c * sx, -s * sy, 0], [s * sx, c * sy, 0]], np.float64)
    M[:, 2] = [cx, cy] - M[:, :2] @ [ax, ay]
    pts = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], np.float64) @ M.T
    x0, y0 = np.floor(pts.min(0)).astype(int) - 1; x1, y1 = np.ceil(pts.max(0)).astype(int) + 1
    x0c, y0c = max(x0, 0), max(y0, 0); x1c, y1c = min(x1, W), min(y1, H)
    if x1c <= x0c or y1c <= y0c:
        return
    M2 = M.copy(); M2[:, 2] -= [x0c, y0c]
    out = cv2.warpAffine(pm, M2, (x1c - x0c, y1c - y0c), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if tint is not None and tint_amt > 0:
        out[..., :3] = out[..., :3] * (1 - tint_amt) + np.asarray(tint, np.float32) * out[..., 3:4] * tint_amt
    if alpha < 1:
        out *= alpha
    over_pm(canvas, out[..., :3], out[..., 3], x0c, y0c)


# ---------------------------------------------------------------- sprites
@functools.lru_cache(maxsize=64)
def sprite(name):
    im = cv2.imread(f'{ROOT}/assets/sprites/px_{name}.png', cv2.IMREAD_UNCHANGED)
    rgba = np.dstack([im[..., 2], im[..., 1], im[..., 0], im[..., 3]]).astype(np.float32) / 255
    return to_pm(rgba)


@functools.lru_cache(maxsize=256)
def sprite_up(name, k):
    s = sprite(name)
    return cv2.resize(s, (s.shape[1] * k, s.shape[0] * k), interpolation=cv2.INTER_NEAREST)


def put_sprite(canvas, name, x, y, height, rot=0.0, alpha=1.0, tint=None, tint_amt=0.0, squash=1.0):
    """x,y,height in REF px; sprite centred."""
    s = sprite(name); h = s.shape[0]
    scale = P(height) / h
    k = max(1, int(scale))
    up = sprite_up(name, k)
    place(canvas, up, P(x), P(y), scale / k, rot, alpha, tint=tint, tint_amt=tint_amt,
          sx=scale / k / squash ** 0.5, sy=scale / k * squash)


def silhouette(pm, color):
    out = pm.copy(); out[..., :3] = np.asarray(color, np.float32) * pm[..., 3:4]
    return out


# ---------------------------------------------------------------- voxel / 3D slab
def _rot(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def voxel(canvas, name, x, y, height, rx=0, ry=0, rz=0, thick=0.16, side=0.42, alpha=1.0, persp=2.6, blur=0.0):
    """Extruded pixel-sprite slab. thick = fraction of sprite height. x,y,height in REF px."""
    s = sprite(name); h, w = s.shape[:2]
    scale = P(height) / h; k = max(1, int(scale)); up = sprite_up(name, k)
    u = scale / k  # render px per upscaled px
    hu, wu = up.shape[:2]
    R = _rot(rx, ry, rz)
    D = P(height) * persp
    T = P(height) * thick
    cx, cy = P(x), P(y)
    n = R @ np.array([0, 0, -1.0])  # front-face normal (towards camera = -z)
    corners = np.array([[-wu / 2, -hu / 2], [wu / 2, -hu / 2], [wu / 2, hu / 2], [-wu / 2, hu / 2]]) * u
    src = np.array([[0, 0], [wu, 0], [wu, hu], [0, hu]], np.float32)

    def proj(dz):
        P3 = np.column_stack([corners, np.full(4, dz)]) @ R.T
        f = D / (D + P3[:, 2])
        return np.column_stack([cx + P3[:, 0] * f, cy + P3[:, 1] * f]).astype(np.float32)

    allp = np.vstack([proj(-T / 2), proj(T / 2)])
    x0, y0 = np.floor(allp.min(0)).astype(int) - 2; x1, y1 = np.ceil(allp.max(0)).astype(int) + 2
    x0c, y0c = max(x0, 0), max(y0, 0); x1c, y1c = min(x1, W), min(y1, H)
    if x1c <= x0c or y1c <= y0c:
        return
    bw, bh = x1c - x0c, y1c - y0c
    acc = np.zeros((bh, bw, 4), np.float32)
    front_visible = n[2] < 0
    nl = max(6, int(T / max(1.0, P(2.0))))
    zs = np.linspace(T / 2, -T / 2, nl) if front_visible else np.linspace(-T / 2, T / 2, nl)
    edge = s.copy()
    sidecol = up.copy(); sidecol[..., :3] *= side
    light = 0.78 + 0.22 * abs(n[2])
    for i, dz in enumerate(zs):
        dst = (proj(dz) - np.array([x0c, y0c], np.float32)).astype(np.float32)
        Hm = cv2.getPerspectiveTransform(src, dst)
        last = i == nl - 1
        img = up if last else sidecol
        layer = cv2.warpPerspective(img, Hm, (bw, bh), flags=cv2.INTER_LINEAR, borderValue=0)
        if last:
            layer[..., :3] *= light
        a = layer[..., 3:4]
        acc[..., :3] = acc[..., :3] * (1 - a) + layer[..., :3]
        acc[..., 3:4] = acc[..., 3:4] * (1 - a) + a
    if blur > 0:
        acc = cv2.GaussianBlur(acc, (0, 0), P(blur))
    if alpha < 1:
        acc *= alpha
    over_pm(canvas, acc[..., :3], acc[..., 3], x0c, y0c)


# ---------------------------------------------------------------- text
@functools.lru_cache(maxsize=32)
def _font(size, weight):
    f = ImageFont.truetype(FONT, size); f.set_variation_by_axes([weight]); return f


@functools.lru_cache(maxsize=2048)
def text_pm(s, size, weight=700, color=(0, 0, 0), tracking=0.0):
    """returns (pm RGBA float, ascent_px) rendered at RENDER size; size in REF px"""
    px = max(4, int(round(P(size))))
    f = _font(px, weight)
    asc, desc = f.getmetrics()
    tr = tracking * px
    widths = [f.getlength(ch) for ch in s] if s else [0]
    tw = int(sum(widths) + tr * max(0, len(s) - 1) + px * 0.4) + 4
    img = Image.new('L', (max(tw, 4), asc + desc + 8), 0)
    d = ImageDraw.Draw(img)
    if tracking == 0:
        d.text((2, 4), s, font=f, fill=255)
    else:
        xx = 2
        for ch, wch in zip(s, widths):
            d.text((xx, 4), ch, font=f, fill=255); xx += wch + tr
    a = np.asarray(img, np.float32) / 255
    col = np.asarray(color, np.float32)
    pm = np.dstack([a * col[0], a * col[1], a * col[2], a])
    return pm, asc + 4


def text_width(s, size, weight=700, tracking=0.0):
    px = max(4, int(round(P(size)))); f = _font(px, weight)
    if not s:
        return 0.0
    return (f.getlength(s) + tracking * px * max(0, len(s) - 1)) / S


def draw_text(canvas, s, x, y, size, weight=700, color=(0, 0, 0), alpha=1.0, anchor='l', tracking=0.0, rot=0.0, blur=0.0):
    """x,y REF px; y = baseline. anchor l/c/r horizontal."""
    if not s:
        return
    pm, asc = text_pm(s, size, weight, tuple(float(c) for c in color), tracking)
    if blur > 0:
        pm = cv2.GaussianBlur(pm, (0, 0), P(blur))
    w_ = text_width(s, size, weight, tracking)
    ox = {'l': 0, 'c': w_ / 2, 'r': w_}[anchor]
    h, w = pm.shape[:2]
    ax = (2 + P(ox)) / w; ay = asc / h
    place(canvas, pm, P(x), P(y), 1.0, rot, alpha, anchor=(ax, ay))


def cursor(canvas, x, y, size, mode='bar', color=WHITE, alpha=1.0):
    """block while typing, thin bar when idle. y = baseline"""
    if mode == 'block':
        w_, h_ = size * 0.55, size * 0.72
    else:
        w_, h_ = size * 0.075, size * 0.95
    x0, y0 = int(P(x)), int(P(y - h_ + size * 0.08))
    x1, y1 = int(P(x + w_)) + 1, int(P(y + size * 0.1)) + 1
    canvas[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = canvas[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] * (1 - alpha) + np.asarray(color) * alpha


# ---------------------------------------------------------------- strokes / ink
def stroke_mask(pts, width, progress=1.0, taper=True, mask=None, jitter=0.0, seed=0):
    """pts: list of (x,y) REF px. Draws progressive polyline into a float mask (render res)."""
    if mask is None:
        mask = np.zeros((H, W), np.float32)
    pts = np.asarray(pts, np.float64)
    if len(pts) < 2:
        return mask
    if jitter > 0:
        rng = np.random.default_rng(seed)
        pts = pts + rng.normal(0, jitter, pts.shape)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); L = seg.sum()
    if L <= 0:
        return mask
    target = L * clamp01(progress); acc = 0.0
    n = len(pts) - 1
    for i in range(n):
        if acc >= target:
            break
        a, b = pts[i], pts[i + 1]
        if acc + seg[i] > target:
            b = a + (b - a) * (target - acc) / seg[i]
        u = (acc + seg[i] * 0.5) / L
        wmul = (0.35 + 0.65 * math.sin(math.pi * min(max(u, 0.02), 0.98)) ** 0.6) if taper else 1.0
        th = max(1, int(round(P(width * wmul))))
        cv2.line(mask, (int(P(a[0]) * 4), int(P(a[1]) * 4)), (int(P(b[0]) * 4), int(P(b[1]) * 4)), 1.0, th, cv2.LINE_AA, shift=2)
        acc += seg[i]
    return mask


def ink(canvas, mask, color=INK, alpha=1.0):
    m = np.clip(mask, 0, 1)[..., None] * alpha
    canvas *= (1 - m); canvas += np.asarray(color, np.float32) * m


def catmull(pts, n=8):
    pts = np.asarray(pts, np.float64)
    if len(pts) < 3:
        return pts
    P_ = np.vstack([pts[0], pts, pts[-1]]); out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return np.array(out)


def blob_mask(cx, cy, r, seed, lobes=7, rough=0.22, mask=None, spatter=0):
    """organic ink blot. REF px."""
    if mask is None:
        mask = np.zeros((H, W), np.float32)
    rng = np.random.default_rng(seed)
    ang = np.linspace(0, 2 * math.pi, 64, endpoint=False)
    rr = np.ones_like(ang)
    for k in range(2, lobes + 2):
        rr += rng.normal(0, rough / k ** 0.7) * np.cos(k * ang + rng.uniform(0, 6.28))
    pts = np.column_stack([cx + np.cos(ang) * r * rr, cy + np.sin(ang) * r * rr])
    cv2.fillPoly(mask, [(pts * S * 4).astype(np.int32)], 1.0, cv2.LINE_AA, shift=2)
    for _ in range(spatter):
        a = rng.uniform(0, 6.28); d = r * rng.uniform(1.05, 1.9); sr = r * rng.uniform(0.03, 0.10)
        cv2.circle(mask, (int(P(cx + math.cos(a) * d) * 4), int(P(cy + math.sin(a) * d) * 4)), max(1, int(P(sr) * 4)), 1.0, -1, cv2.LINE_AA, shift=2)
    return mask


# ---------------------------------------------------------------- light / fx
def star4_mask(cx, cy, r, rot=0.0, pinch=3.0, rx=1.0, ry=1.0):
    """4-point astroid star mask (REF px)."""
    m = np.zeros((H, W), np.float32)
    t = np.linspace(0, 2 * math.pi, 240)
    x = np.sign(np.cos(t)) * np.abs(np.cos(t)) ** pinch * r * rx
    y = np.sign(np.sin(t)) * np.abs(np.sin(t)) ** pinch * r * ry
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = np.column_stack([cx + x * c - y * s, cy + x * s + y * c])
    cv2.fillPoly(m, [(pts * S * 4).astype(np.int32)], 1.0, cv2.LINE_AA, shift=2)
    return m


def glow_from(mask_or_img, sigma, strength, color=None):
    src = mask_or_img if mask_or_img.ndim == 3 else mask_or_img[..., None] * np.asarray(color, np.float32)
    small = cv2.resize(src, (max(1, W // 4), max(1, H // 4)), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), max(0.5, P(sigma) / 4))
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR) * strength


def radial(cx, cy, rx, ry=None):
    ry = rx if ry is None else ry
    yy, xx = np.ogrid[0:H, 0:W]
    return np.sqrt(((xx - P(cx)) / P(rx)) ** 2 + ((yy - P(cy)) / P(ry)) ** 2).astype(np.float32)


def vignette_mul(img, strength=0.35, radius=0.9, color=(0, 0, 0), soft=0.55):
    r = radial(REF_W / 2, REF_H / 2, REF_W * 0.5 * radius / 0.72, REF_H * 0.5 * radius / 0.72)
    v = np.clip((r - (1 - soft)) / soft, 0, 1) ** 1.6 * strength
    img *= (1 - v[..., None]); img += np.asarray(color, np.float32) * v[..., None]
    return img


def speed_lines(canvas, seed, n, cx, cy, rmin, rmax, length, width, color=WHITE, alpha=1.0, ang_range=(0, 360)):
    rng = np.random.default_rng(seed)
    m = np.zeros((H, W), np.float32)
    for _ in range(n):
        a = math.radians(rng.uniform(*ang_range)); r0 = rng.uniform(rmin, rmax); L = length * rng.uniform(0.5, 1.2)
        p0 = (cx + math.cos(a) * r0, cy + math.sin(a) * r0); p1 = (cx + math.cos(a) * (r0 + L), cy + math.sin(a) * (r0 + L))
        stroke_mask([p0, p1], width * rng.uniform(0.6, 1.2), mask=m)
    ink(canvas, m, color, alpha)


# ---------------------------------------------------------------- thermal / photos
@functools.lru_cache(maxsize=6)
def thermal_plate(name):
    im = np.asarray(Image.open(f'{ROOT}/assets/thermal/{name}_thermal.png').convert('RGBA'), np.float32) / 255
    return to_pm(im)


@functools.lru_cache(maxsize=4)
def photo_plate(name):
    im = np.asarray(Image.open(f'{ROOT}/assets/photos/{name}.png').convert('RGB'), np.float32) / 255
    return im


def put_plate(canvas, pm, x, y, height, alpha=1.0, blur=0.0, hue=None, hue_amt=0.0, rot=0.0):
    """centre x,y REF; height REF px"""
    scale = P(height) / pm.shape[0]
    src = pm
    if blur > 0:
        small = cv2.resize(pm, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), P(blur) / scale * 0.25)
        src = cv2.resize(small, (pm.shape[1], pm.shape[0]), interpolation=cv2.INTER_LINEAR)
    if hue is not None and hue_amt > 0:
        src = src.copy(); a = src[..., 3:4]
        src[..., :3] = src[..., :3] * (1 - hue_amt) + np.asarray(hue, np.float32) * a * hue_amt
    place(canvas, src, P(x), P(y), scale, rot, alpha)


# ---------------------------------------------------------------- finishing
def finish(img, f, vig=0.30, grain=1.0, weave=1.0, chroma=1.0, halation=0.18, soft=0.6, seed_extra=0):
    rng = np.random.default_rng(1000 + f * 7 + seed_extra)
    # halation: bloom of highlights, warm
    hl = np.clip(img - 0.78, 0, None)
    if halation > 0:
        img = img + glow_from(hl * np.array([1.0, 0.45, 0.30], np.float32), 22, halation * 2.2)
    # chromatic fringe (radial)
    if chroma > 0:
        k = 0.0016 * chroma
        for ch, sc in ((0, 1 + k), (2, 1 - k)):
            M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, sc)
            img[..., ch] = cv2.warpAffine(img[..., ch], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # gate weave
    if weave > 0:
        dx, dy = rng.normal(0, 0.9 * weave) * S * 2, rng.normal(0, 1.1 * weave) * S * 2
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if vig > 0:
        img = vignette_mul(img, vig, 0.95)
    # tone: lift blacks, roll off whites
    x = np.clip(img, 0, None)
    x = np.where(x > 0.85, 0.85 + 0.15 * np.tanh((x - 0.85) / 0.15), x)
    img = 0.062 + 0.885 * x
    # grain: coarse + fine, stronger in mids
    if grain > 0:
        g1 = cv2.resize(rng.standard_normal((H // 2, W // 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        g2 = rng.standard_normal((H, W)).astype(np.float32)
        lum = img.mean(2)
        amp = (0.028 + 0.036 * (4 * lum * (1 - lum))) * grain
        g = (g1 * 0.7 + g2 * 0.45) * amp
        img = img + g[..., None] * np.array([1.0, 0.95, 1.05], np.float32)
    if soft > 0:
        img = cv2.GaussianBlur(img, (0, 0), max(0.3, soft * S * 2))
    return np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
