"""Tiny 2.5D layer engine: premultiplied float32 RGBA, bbox-limited affine warps,
mip-mapped sprites, per-layer gaussian DOF, over-compositing."""
import math
import numpy as np, cv2
from PIL import Image

W, H = 1080, 1920


def ease(name, x):
    x = min(max(x, 0.0), 1.0)
    if name == 'lin':
        return x
    if name == 'in':
        return x * x * x
    if name == 'out':
        return 1 - (1 - x) ** 3
    if name == 'inout':
        return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
    if name == 'in2':
        return x * x
    if name == 'out2':
        return 1 - (1 - x) ** 2
    if name == 'expo':
        return 1 - 2 ** (-10 * x) if x < 1 else 1
    if name == 'back':
        c1, c3 = 1.4, 2.4
        return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
    if name == 'hold':
        return 0.0
    return x


def kf(t, keys, default_ease='inout'):
    """keys: [(frame, value, ease_into_this_key?), ...]; value may be tuple."""
    if t <= keys[0][0]:
        return keys[0][1]
    for i in range(1, len(keys)):
        f1 = keys[i][0]
        if t <= f1:
            f0, v0 = keys[i - 1][0], keys[i - 1][1]
            v1 = keys[i][1]
            e = keys[i][2] if len(keys[i]) > 2 else default_ease
            u = ease(e, (t - f0) / (f1 - f0) if f1 > f0 else 1)
            if isinstance(v0, (tuple, list)):
                return tuple(a + (b - a) * u for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * u
    return keys[-1][1]


class Sprite:
    def __init__(self, rgba, anchor=None):
        """rgba: straight-alpha float32 (h,w,4) 0..1"""
        a = rgba[..., 3:4]
        pm = np.dstack([rgba[..., :3] * a, a]).astype(np.float32)
        self.mips = [pm]
        while min(self.mips[-1].shape[:2]) > 16:
            self.mips.append(cv2.pyrDown(self.mips[-1]))
        h, w = pm.shape[:2]
        self.w, self.h = w, h
        self.anchor = anchor if anchor is not None else (w / 2, h / 2)

    @staticmethod
    def load(path, anchor=None):
        im = np.asarray(Image.open(path).convert('RGBA')).astype(np.float32) / 255
        return Sprite(im, anchor)


def over(buf, patch, x0, y0):
    """composite premultiplied patch onto buf at integer offset (clipped)."""
    ph, pw = patch.shape[:2]
    bx0, by0 = max(x0, 0), max(y0, 0)
    bx1, by1 = min(x0 + pw, buf.shape[1]), min(y0 + ph, buf.shape[0])
    if bx1 <= bx0 or by1 <= by0:
        return
    p = patch[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0]
    r = buf[by0:by1, bx0:bx1]
    r *= (1 - p[..., 3:4])
    r += p


def affine(x, y, sx, sy, rot_deg, ax, ay):
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    # p_screen = T(x,y) R S (p - a)
    return np.array([[c * sx, -s * sy, x - (c * sx * ax - s * sy * ay)],
                     [s * sx, c * sy, y - (s * sx * ax + c * sy * ay)]], np.float64)


def draw(buf, spr, x, y, scale=1.0, rot=0.0, opacity=1.0, blur=0.0, color=None,
         sx=None, sy=None, anchor=None, tint=None):
    if opacity <= 0.003 or scale <= 1e-3:
        return
    sx = scale if sx is None else sx
    sy = scale if sy is None else sy
    ax, ay = anchor if anchor is not None else spr.anchor
    # mip choice
    m = max(abs(sx), abs(sy))
    lvl = 0
    while m * (2 ** (lvl + 1)) <= 1.0 and lvl + 1 < len(spr.mips):
        lvl += 1
    src = spr.mips[lvl]
    f = 2 ** lvl
    sxl, syl = sx * f, sy * f
    axl, ayl = ax / f, ay / f
    M = affine(x, y, sxl, syl, rot, axl, ayl)
    h, w = src.shape[:2]
    corners = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], np.float64).T
    pts = M @ corners
    pad = int(3 * blur + 3)
    x0, y0 = int(math.floor(pts[0].min())) - pad, int(math.floor(pts[1].min())) - pad
    x1, y1 = int(math.ceil(pts[0].max())) + pad, int(math.ceil(pts[1].max())) + pad
    cx0, cy0 = max(x0, -pad), max(y0, -pad)
    cx1, cy1 = min(x1, buf.shape[1] + pad), min(y1, buf.shape[0] + pad)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    M2 = M.copy()
    M2[0, 2] -= cx0
    M2[1, 2] -= cy0
    patch = cv2.warpAffine(src, M2, (cx1 - cx0, cy1 - cy0), flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if color is not None:
        a = patch[..., 3:4]
        patch = np.dstack([np.asarray(color, np.float32)[None, None, :] * a, a])
    if tint is not None:
        col, amt = tint
        a = patch[..., 3:4]
        patch[..., :3] = patch[..., :3] * (1 - amt) + np.asarray(col, np.float32) * a * amt
    if blur > 0.35:
        patch = cv2.GaussianBlur(patch, (0, 0), blur)
    if opacity < 1:
        patch *= opacity
    over(buf, patch, cx0, cy0)


def blank():
    return np.zeros((H, W, 4), np.float32)
