// scene.js — "The AI editing era has begun…"  (900 frames @ 60 fps, 1080x1920)
'use strict';
const SHUTTER = 0.5;                       // 180° shutter, in frames
const Q = new URLSearchParams(location.search);
const SUB_DEFAULT = +(Q.get('sub') || 1);
function subsamples(f) { return SUB_DEFAULT; }
const has = n => !!IMG[n];
const CX = 540, CY = 960;

// ------------------------------------------------------------ clip registry
const CLIPS = [];
function clip(a, b, draw, z = 0) { CLIPS.push({ a, b, draw, z }); CLIPS.sort((p, q) => p.z - q.z); }
let FR = 0;                                // integer frame — hard-cut decisions use this, never the sub-frame time
function drawScene(ctx, t, f) {
  FR = f;
  for (const c of CLIPS) if (f >= c.a && f < c.b) { ctx.save(); c.draw(ctx, t, f); ctx.restore(); }
}

// ------------------------------------------------------------ shared UI pieces
function selBox(ctx, x, y, w, h, o = {}) {
  const a = o.a == null ? 1 : o.a; if (a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a;
  ctx.translate(x, y); if (o.r) ctx.rotate(o.r);
  const lw = o.lw || 6;
  if (w <= lw * 2.2) {            // collapsed → solid caret bar
    ctx.fillStyle = C.lime; ctx.fillRect(-Math.max(w, lw) / 2, -h / 2, Math.max(w, lw), h);
  } else {
    ctx.strokeStyle = C.lime; ctx.lineWidth = lw; ctx.lineJoin = 'miter';
    ctx.strokeRect(-w / 2, -h / 2, w, h);
  }
  const ha = o.handles == null ? 1 : o.handles;
  if (ha > 0.01) {
    const hs = (o.hs || 28) * ha;
    [[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]].forEach(([px, py], i) => {
      const s = hs * (o.grab === i ? 1.3 : 1);
      ctx.fillStyle = C.lime; ctx.fillRect(px - s / 2, py - s / 2, s, s);
      ctx.lineWidth = 2.5; ctx.strokeStyle = C.ink; ctx.strokeRect(px - s / 2, py - s / 2, s, s);
    });
  }
  ctx.restore();
}
function cursor(ctx, x, y, o = {}) {
  const a = o.a == null ? 1 : o.a; if (a <= 0) return;
  ctx.save();
  ctx.shadowColor = 'rgba(0,0,0,0.25)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 8;
  spark(ctx, x, y, o.size || 84, { r: o.r || 0, a, grow: o.grow, blur: o.blur });
  ctx.restore();
}
function caret(ctx, x, yTop, h, a = 1, w = 12) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = C.lime; ctx.fillRect(x - w / 2, yTop, w, h); ctx.restore();
}
function highlight(ctx, x0, x1, yTop, h, a = 1) {
  if (a <= 0 || x1 <= x0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = C.lime; ctx.fillRect(x0, yTop, x1 - x0, h); ctx.restore();
}
// draw an image so its normalised point (px,py) lands at (x,y); size via h or w
function pin(ctx, name, px, py, x, y, o = {}) {
  img(ctx, name, Object.assign({}, o, { x, y, ax: px, ay: py }));
}
function discImg(ctx, name, x, y, d, rot = 0, a = 1) {
  const m = META[name] || {}; const im = IMG[name];
  const cx = (m.cx || 0.5) * im.width, cy = (m.cy || 0.5) * im.height, cr = (m.cr || 0.48) * im.width;
  const k = (d / 2) / cr;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.rotate(rot);
  ctx.beginPath(); ctx.arc(0, 0, d / 2, 0, TAU); ctx.clip();
  ctx.drawImage(im, -cx * k, -cy * k, im.width * k, im.height * k);
  ctx.restore();
}

// ============================================================ BEAT 1 — CUT (0–46)
const CUT = { cy: 930, ang: -0.50, t0: 4, t1: 14, split0: 22, split1: 44 };
function cutWord(ctx, t) {
  const u = E.outE(prog(t, -6, 12));
  const s = lerp(1.08, 1.0, u), bl = lerp(10, 0, u);
  ctx.save(); ctx.translate(CX, CUT.cy); ctx.scale(s, s); ctx.translate(-CX, -CUT.cy);
  word(ctx, 'cut', FONTS.serif, 500, CX, CUT.cy + 120, { glyph: () => ({ blur: bl, a: clamp(0.35 + u) }) });
  ctx.restore();
}
function cutLine(ctx, t, lw) {
  const dx = Math.cos(CUT.ang), dy = Math.sin(CUT.ang), L = 1400;
  const p = E.ioQ(prog(t, CUT.t0, CUT.t1));
  if (p <= 0) return;
  const x0 = CX - dx * L, y0 = CUT.cy - dy * L;
  line(ctx, x0, y0, lerp(x0, CX + dx * L, p), lerp(y0, CUT.cy + dy * L, p), lw, C.lime, 1, 'butt');
}
clip(0, 46, (ctx, t) => {
  if (FR < CUT.split0) {
    // micro-anticipation: the halves part by a hair just before the split
    cutWord(ctx, t);
    cutLine(ctx, t, 9 + 4 * Math.exp(-Math.max(0, t - CUT.t1) / 3));
  } else {
    drawCropBeat(ctx, t);
    const d = kf(t, [[CUT.split0, 0], [CUT.split1, 1300, E.ioE]]);
    const nx = -Math.sin(CUT.ang), ny = Math.cos(CUT.ang), tx = Math.cos(CUT.ang), ty = Math.sin(CUT.ang);
    for (const side of [-1, 1]) {
      ctx.save();
      ctx.translate(nx * d * side + tx * d * 0.22 * side, ny * d * side + ty * d * 0.22 * side);
      ctx.beginPath();
      const big = 4000, ax = CX - tx * big, ay = CUT.cy - ty * big, bx = CX + tx * big, by = CUT.cy + ty * big;
      ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.lineTo(bx + nx * big * side, by + ny * big * side); ctx.lineTo(ax + nx * big * side, ay + ny * big * side);
      ctx.closePath(); ctx.clip();
      ctx.fillStyle = C.bg; ctx.fillRect(-3000, -3000, W + 6000, H + 6000);
      cutWord(ctx, 30);
      line(ctx, ax, ay, bx, by, 10, C.lime, 1, 'butt');
      ctx.restore();
    }
  }
  // the spark is the blade
  const p = prog(t, CUT.t0 - 1, CUT.t1 + 2);
  if (p > 0 && p < 1) {
    const e = E.ioQ(prog(t, CUT.t0, CUT.t1)), L = 1400;
    cursor(ctx, CX + Math.cos(CUT.ang) * lerp(-L, L, e), CUT.cy + Math.sin(CUT.ang) * lerp(-L, L, e), { size: 96, r: t * 0.3 });
  }
}, 10);

// ============================================================ BEAT 2 — CROP (22–150)
// [start, image, drawW, cx, cy]  (image drawn at width drawW centred at cx,cy; the crop box reveals it)
const CROP_SEQ = [
  [22, 'horse', 1300, 540, 900],
  [64, 'marey_hurdle', 1500, 560, 900],
  [80, 'metro_robot', 900, 540, 900],
  [96, 'melies', 1500, 540, 900],
  [104, 'kin_camera', 1300, 540, 900],
  [108, 'moviola_c', 760, 540, 900],
  [112, 'praxi_photo', 1500, 540, 900],
  [116, 'turk', 1150, 540, 900],
  [120, 'jacquard', 1400, 540, 900],
  [124, 'typewriter', 900, 540, 900],
  [128, 'vaucanson', 820, 540, 900],
];
function cropIdx(t) { let i = 0; CROP_SEQ.forEach((s, k) => { if (t >= s[0]) i = k; }); return i; }
const BOX = [
  [22, [540, 900, 860, 600]],
  [56, [540, 900, 860, 600]],
  [64, [540, 900, 640, 640], E.snap],
  [72, [540, 900, 640, 640]],
  [80, [540, 880, 560, 980], E.snap],
  [88, [540, 880, 560, 980]],
  [96, [540, 900, 880, 560], E.snap],
  [124, [540, 900, 880, 560]],
  [132, [540, 900, 420, 420], E.snap],
  [138, [540, 900, 420, 420]],
];
function cropBox(t) { return kf(t, BOX); }
function drawCropImage(ctx, name, dw, ix, iy, t, ghost) {
  if (name === 'horse') {
    const n = Math.floor((FR - 22) / 3) % 11, nm = 'mh' + n, m = META[nm];
    const im = IMG[nm], h = dw * im.height / im.width;
    // register the horse (half-strength) so it gallops in place
    const fx = 0.5 + (m.fx - 0.53) * 0.6, fy = 0.5 + (m.fy - 0.48) * 0.6;
    img(ctx, nm, { x: ix, y: iy, w: dw, ax: fx, ay: fy, a: ghost });
    return;
  }
  img(ctx, name, { x: ix, y: iy, w: dw, a: ghost });
}
function drawCropBeat(ctx, t) {
  const [cx, cy, w, h] = cropBox(t);
  const [, name, dw, ix, iy] = CROP_SEQ[cropIdx(FR)];
  const z = lerp(1.06, 1, E.outC(prog(t, 22, 48)));
  ctx.save(); ctx.translate(540, 900); ctx.scale(z, z); ctx.translate(-540, -900);
  // ghost (outside the crop) + full (inside)
  drawCropImage(ctx, name, dw, ix, iy, t, 0.13);
  ctx.save(); ctx.beginPath(); ctx.rect(cx - w / 2, cy - h / 2, w, h); ctx.clip();
  ctx.fillStyle = C.bg; ctx.fillRect(cx - w / 2, cy - h / 2, w, h);
  drawCropImage(ctx, name, dw, ix, iy, t, 1);
  ctx.restore();
  const grab = (t >= 54 && t < 66) ? 2 : (t >= 70 && t < 82) ? 1 : (t >= 86 && t < 98) ? 2 : (t >= 122 && t < 134) ? 2 : -1;
  const ha = 1 - prog(t, 136, 142);
  selBox(ctx, cx, cy, w, h, { grab, handles: ha });
  ctx.restore();
  filmstrip(ctx, t);
}
// timeline strip under the crop
function filmstrip(ctx, t) {
  const a = E.outC(prog(t, 30, 42)) * (1 - E.inC(prog(t, 132, 142)));
  if (a <= 0) return;
  const y = 1600 + (1 - a) * 80, th = 118, tw = 158, gap = 14;
  // continuous strip position follows the content index with a snap
  let pos = 0;
  CROP_SEQ.forEach((s, k) => { if (k > 0) pos += E.snap(prog(t, s[0] - 3, s[0] + 3)); });
  ctx.save(); ctx.globalAlpha *= a;
  CROP_SEQ.forEach((s, k) => {
    const x = CX + (k - pos) * (tw + gap);
    if (x < -tw || x > W + tw) return;
    ctx.save(); ctx.beginPath(); ctx.rect(x - tw / 2, y - th / 2, tw, th); ctx.clip();
    ctx.fillStyle = '#F2F2F2'; ctx.fillRect(x - tw / 2, y - th / 2, tw, th);
    const nm = s[1] === 'horse' ? 'mh2' : s[1], im = IMG[nm];
    if (im) { const sc = Math.max(tw / im.width, th / im.height) * (META[nm].kind === 'ink' ? 0.75 : 1); ctx.drawImage(im, x - im.width * sc / 2, y - im.height * sc / 2, im.width * sc, im.height * sc); }
    ctx.restore();
  });
  playhead(ctx, CX, y - th / 2 - 16, y + th / 2 + 16, {});
  ctx.restore();
}
function playhead(ctx, x, y0, y1) {
  line(ctx, x, y0, x, y1, 5, C.lime, 1, 'butt');
  ctx.save(); ctx.fillStyle = C.lime; ctx.strokeStyle = C.ink; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(x - 16, y0 - 26); ctx.lineTo(x + 16, y0 - 26); ctx.lineTo(x + 16, y0 - 8); ctx.lineTo(x, y0 + 6); ctx.lineTo(x - 16, y0 - 8); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.restore();
}
function cropCursor(t) {
  const [cx, cy, w, h] = cropBox(t);
  const br = [cx + w / 2, cy + h / 2], tr = [cx + w / 2, cy - h / 2];
  const park = [cx + w / 2 + 110, cy + h / 2 + 150];
  if (t < 54) return kf(t, [[42, [1200, 1450]], [54, br, E.outE]]);
  if (t < 66) return br;
  if (t < 70) return kf(t, [[66, br], [70, tr, E.ioC]]);
  if (t < 82) return tr;
  if (t < 86) return kf(t, [[82, tr], [86, br, E.ioC]]);
  if (t < 98) return br;
  if (t < 104) return kf(t, [[98, br], [104, park, E.ioC]]);
  if (t < 118) return park;
  if (t < 122) return kf(t, [[118, park], [122, br, E.ioC]]);
  return br;
}
clip(46, 150, (ctx, t) => {
  if (FR < 136) drawCropBeat(ctx, t);
  else drawCaretMorph(ctx, t);
  if (t < 140) { const [x, y] = cropCursor(t); cursor(ctx, x + 22, y + 22, { r: t * 0.04 }); }
});

// ============================================================ BEAT 3 — past → paste (136–240)
const PST = { y: 1050, serif: 380, sans: 300 };
const CARET_H = 300;
function letterSets(ctx) {
  // A: "past" serif + "e" sans ; B: "paste" all sans  — centred layouts
  const L = (chars) => {
    let w = 0; const xs = [];
    chars.forEach(([ch, fam, size]) => { ctx.font = `${size}px "${fam}"`; const a = ctx.measureText(ch).width; xs.push([w, a]); w += a; });
    return xs.map(([x, a]) => ({ x: CX - w / 2 + x, w: a, total: w }));
  };
  const S = [FONTS.serif, PST.serif], N = [FONTS.sans, PST.sans];
  return {
    A4: L([['p', ...S], ['a', ...S], ['s', ...S], ['t', ...S]]),
    A5: L([['p', ...S], ['a', ...S], ['s', ...S], ['t', ...S], ['e', ...N]]),
    B5: L([['p', ...N], ['a', ...N], ['s', ...N], ['t', ...N], ['e', ...N]]),
  };
}
let _LS = null;
const T_TYPE = [150, 154, 158, 162];
const T_E = 196, T_FLIP = [201, 204, 207, 210];
function drawCaretMorph(ctx, t) {
  // crop box collapses into the caret at the start of the word
  _LS = _LS || letterSets(ctx);
  const x0 = _LS.A4[0].x - 10, yTop = PST.y - CARET_H * 0.78;
  const u = E.snap(prog(t, 134, 146));
  const [cx, cy, w, h] = cropBox(134);
  const bx = lerp(cx, x0, u), by = lerp(cy, yTop + CARET_H / 2, u), bw = lerp(w, 12, u), bh = lerp(h, CARET_H, u);
  selBox(ctx, bx, by, bw, bh, { handles: 1 - prog(t, 134, 140), lw: lerp(6, 12, u) });
}
function pasteWord(ctx, t, alpha = 1, scale = 1) {
  _LS = _LS || letterSets(ctx);
  const chars = 'paste';
  const eIn = t >= T_E;
  const recentre = E.snap(prog(t, T_E, T_E + 8));
  ctx.save(); ctx.globalAlpha *= alpha;
  ctx.translate(CX, PST.y - 100); ctx.scale(scale, scale); ctx.translate(-CX, -(PST.y - 100));
  // lime selection sweep while the letters convert
  const hs = E.ioC(prog(t, T_FLIP[0] - 2, T_FLIP[0] + 6)), he = E.ioC(prog(t, T_FLIP[3] + 6, T_FLIP[3] + 14));
  const B = _LS.B5, wl = B[0].x - 14, wr = B[4].x + B[4].w + 14;
  if (hs > 0 && he < 1) highlight(ctx, lerp(wl, wr, he), lerp(wl, wr, hs), PST.y - 232, 300, 1);
  for (let i = 0; i < 5; i++) {
    if (i < 4 && t < T_TYPE[i]) continue;
    if (i === 4 && !eIn) continue;
    // position: A4 → A5 (recentre on e) → B5 (flip)
    const fp = i < 4 ? prog(t, T_FLIP[i], T_FLIP[i] + 7) : 0;
    const wA = i < 4 ? _LS.A5[i].w : _LS.A5[4].w, wB = _LS.B5[i].w;
    // glyph centre: A4 → A5 (recentre when the e arrives) → B5 (after the font swap)
    let cx;
    if (i < 4) cx = lerp(lerp(_LS.A4[i].x, _LS.A5[i].x, recentre) + wA / 2, _LS.B5[i].x + wB / 2, E.ioC(fp));
    else cx = lerp(_LS.A5[4].x, _LS.B5[4].x, E.ioC(prog(t, T_FLIP[0], T_FLIP[3] + 7))) + wB / 2;
    const ti = i < 4 ? T_TYPE[i] : T_E;
    const pop = E.outBack(prog(t, ti, ti + 6));
    const alpha = clamp((t - ti) / 2 + 0.3);
    const drawG = (fam, size, ww, dy, sc) => {
      ctx.save(); ctx.font = `${size}px "${fam}"`; ctx.fillStyle = C.ink; ctx.textBaseline = 'alphabetic';
      ctx.globalAlpha *= alpha;
      ctx.translate(cx, PST.y - size * 0.3 + dy); ctx.scale(sc, sc); ctx.translate(-ww / 2, size * 0.3);
      ctx.fillText(chars[i], 0, 0); ctx.restore();
    };
    const sc = lerp(0.6, 1, pop);
    if (fp <= 0 || i === 4) drawG(i < 4 ? FONTS.serif : FONTS.sans, i < 4 ? PST.serif : PST.sans, i < 4 ? wA : _LS.B5[4].w, 0, sc);
    else if (fp >= 1) drawG(FONTS.sans, PST.sans, _LS.B5[i].w, 0, 1);
    else {
      // masked roll: the serif letter rolls up and out, the sans letter rolls up into place
      const e = E.ioC(fp), D = 330;
      ctx.save(); ctx.beginPath(); ctx.rect(cx - 160, PST.y - 300, 320, 380); ctx.clip();
      drawG(FONTS.serif, PST.serif, wA, -e * D, 1);
      drawG(FONTS.sans, PST.sans, _LS.B5[i].w, (1 - e) * D, 1);
      ctx.restore();
    }
  }
  // caret
  let cxp;
  const typed = T_TYPE.filter(v => t >= v).length;
  if (t < T_E) {
    const xs = [_LS.A4[0].x - 10, ...[0, 1, 2, 3].map(i => _LS.A4[i].x + _LS.A4[i].w + 8)];
    cxp = xs[typed];
    if (typed > 0) { const tp = T_TYPE[typed - 1]; cxp = lerp(xs[typed - 1], xs[typed], E.outC(prog(t, tp, tp + 3))); }
  } else cxp = lerp(_LS.A5[4].x + _LS.A5[4].w + 8, _LS.B5[4].x + _LS.B5[4].w + 8, recentre);
  const blink = (t > 166 && t < 194) ? ((Math.floor((t - 166) / 14) % 2) ? 0 : 1) : 1;
  const ca = (1 - prog(t, T_FLIP[3] + 4, T_FLIP[3] + 8)) * blink;
  caret(ctx, cxp, PST.y - CARET_H * 0.78, CARET_H, ca);
  ctx.restore();
}
// "the past" — small history around the word
const PAST_IMGS = [
  { n: 'turk', x: 250, y: 560, w: 330, r: -0.06, t: 168 },
  { n: 'head_front', x: 860, y: 590, h: 360, r: 0.04, t: 173 },
  { n: 'jd_dog', x: 830, y: 1390, w: 360, r: 0.05, t: 178 },
  { n: 'vaucanson', x: 240, y: 1380, w: 280, r: -0.04, t: 183 },
];
const DISCS = ['phen_rats', 'phen_couple', 'phen_stampfer', 'phen_cats'];
function discGrid(t) {
  // 3 x 4 pasted copies, then converge into one
  const out = [];
  for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) {
    const k = r * 3 + c;
    out.push({ k, n: DISCS[(k + r) % 4], x: 200 + c * 340, y: 470 + r * 330, t: 216 + k * 1.2 });
  }
  return out;
}
clip(150, 240, (ctx, t) => {
  // small past images (behind)
  const away = E.inBack(prog(t, 212, 222));
  PAST_IMGS.forEach((p, i) => {
    const u = E.outBack(prog(t, p.t, p.t + 9));
    if (u <= 0) return;
    const s = lerp(0.4, 1, u) * (1 - away), bob = Math.sin((t - p.t) * 0.05 + i) * 6;
    img(ctx, p.n, { x: p.x, y: p.y + bob, w: p.w ? p.w * s : null, h: p.h ? p.h * s : null, r: p.r * (2 - u), a: clamp(u * 2) });
  });
  // pasted discs — copies land in a grid, then fly home one after another and stack into the main disc
  const grid = discGrid(t);
  const order = grid.slice().sort((p, q) => (p.k === 4) - (q.k === 4) || p.k - q.k);
  order.forEach((d, j) => {
    if (t <= d.t) return;
    const u = E.outBack(prog(t, d.t, d.t + 7));
    const main = d.k === 4;
    // copies are absorbed into the centre; the main disc grows from its slot into the hero disc
    const c0 = main ? 226 : 222 + j * 0.8, conv = E.ioE(prog(t, c0, c0 + (main ? 12 : 9)));
    const x = lerp(d.x, CX, conv), y = lerp(d.y, CY, conv);
    const dia = main ? lerp(250 * u, 880, conv) : 250 * u * (1 - conv);
    if (dia < 2) return;
    const n = main ? 'phen_rats' : d.n;
    discImg(ctx, n, x, y, dia, (t - d.t) * 0.03 * (d.k % 2 ? 1 : -1) * (1 - conv), 1);
    const ra = (1 - prog(t, d.t + 4, d.t + 12)) * clamp(u * 3);
    if (ra > 0 && dia > 40) { ctx.save(); ctx.strokeStyle = C.lime; ctx.lineWidth = 5; ctx.globalAlpha = ra; ctx.beginPath(); ctx.arc(x, y, dia / 2 + 6, 0, TAU); ctx.stroke(); ctx.restore(); }
  });
  // the word
  const wa = 1 - E.inC(prog(t, 223, 230)), ws = 1 - 0.3 * E.inC(prog(t, 223, 230));
  pasteWord(ctx, t, wa, ws);
}, 5);

// ============================================================ BEAT 4 — phenakistoscope scrub (236–300)
const PH = [{ n: 'phen_rats', N: 16, from: 236 }, { n: 'phen_couple', N: 13, from: 268 }];
function scrubPos(t) {   // in steps
  return kf(t, [[236, 0], [252, 10, E.ioC], [262, 4, E.ioC], [280, 22, E.ioC], [296, 30, E.inC]]);
}
clip(236, 300, (ctx, t) => {
  const ph = FR < 268 ? PH[0] : PH[1];
  const P = scrubPos(t);
  const step = Math.floor(scrubPos(FR));
  const rot = -step * TAU / ph.N;
  const zoom = 1 + 9 * E.inE(prog(t, 284, 299));
  const dia = 880 * zoom;
  const a = 1 - prog(t, 294, 299);
  discImg(ctx, ph.n, CX, CY, dia, rot, a);
  // jog ring
  const ra = (1 - prog(t, 284, 290)) * E.outC(prog(t, 236, 244));
  if (ra > 0) {
    const R = 880 / 2 + 36, ka = -PI / 2 + P * TAU / ph.N * 0.5;
    ctx.save(); ctx.globalAlpha *= ra;
    ctx.strokeStyle = C.lime; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(CX, CY, R, 0, TAU); ctx.stroke();
    // ticks
    for (let i = 0; i < ph.N; i++) { const an = -PI / 2 + i * TAU / ph.N + rot; line(ctx, CX + Math.cos(an) * (R + 10), CY + Math.sin(an) * (R + 10), CX + Math.cos(an) * (R + 26), CY + Math.sin(an) * (R + 26), 4, C.lime, 1, 'butt'); }
    const kx = CX + Math.cos(ka) * R, ky = CY + Math.sin(ka) * R;
    ctx.restore();
    cursor(ctx, kx + 10, ky + 10, { r: t * 0.05, a: ra });
  }
  // the centre becomes the spark
  const sp = E.outC(prog(t, 286, 298));
  if (sp > 0) spark(ctx, CX, CY, lerp(20, 130, sp), { grow: sp, r: lerp(-1.2, 0, sp) + (t - 296) * 0.02 });
}, 6);

// ============================================================ BEAT 5 — hands (296–404)
// Creation of Adam, vertical; then a montage that match-cuts on the spark.
const HANDS = [   // [from, image, px, py, size(h or w), mode, rot]
  [330, 'r_pinch', 0.86, 0.34, 1900, 'h', 0.0],
  [338, 'ecr_canif', 0.63, 0.25, 3200, 'h', 0.0],
  [346, 'jd_writer', 0.07, 0.72, 2100, 'h', 0.0],
  [354, 'r_scissors', 0.38, 0.62, 2100, 'h', 0.0],
  [362, 'god_hand', 0.011, 0.624, 1700, 'w', -0.2],
  [370, 'r_film', 0.60, 0.06, 1900, 'h', 0.0],
  [378, 'adam_hand', 0.99, 0.241, 1500, 'w', 0.15],
  [386, 'r_point', 0.004, 0.119, 1700, 'w', -PI / 2],
];
clip(298, 404, (ctx, t) => {
  // click-ripple: the 3D timeline shows through a growing hole
  const rp = prog(t, 392, 404);
  if (rp > 0) { ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.arc(CX, CY, E.inC(rp) * 1250, 0, TAU, true); ctx.clip('evenodd'); ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); }
  if (FR < 330) {
    const inA = E.outE(prog(t, 298, 312)), drift = E.ioSine(prog(t, 306, 330)) * 26;
    // Adam from below (finger up), robot from above (finger down)
    pin(ctx, 'adam_hand', 0.99, 0.241, CX, CY + 66 + (1 - inA) * 1000 - drift, { w: 1250, r: -PI / 2 });
    pin(ctx, 'r_point', 0.004, 0.119, CX, CY - 66 - (1 - inA) * 1000 + drift, { w: 1350, r: -PI / 2 });
  } else {
    let cur = HANDS[0]; HANDS.forEach(h => { if (FR >= h[0]) cur = h; });
    const [f0, n, px, py, sz, mode, rot] = cur;
    const kick = 1 + 0.04 * Math.exp(-(t - f0) / 3);
    pin(ctx, n, px, py, CX, CY, { [mode]: sz * kick, r: rot });
  }
  // the spark
  const pulse = 1 + 0.12 * Math.exp(-Math.max(0, t - 320) / 6) * (t > 320 ? 1 : 0);
  const s = 130 * pulse * (t < 330 ? 1 : 1 + 0.08 * Math.sin((t - 330) * 0.8));
  spark(ctx, CX, CY, s * (1 - E.inC(prog(t, 394, 402))), { r: (t - 296) * 0.02 });
  // ripple ring
  if (rp > 0) { ctx.save(); ctx.strokeStyle = C.lime; ctx.lineWidth = 10 * (1 - rp) + 2; ctx.beginPath(); ctx.arc(CX, CY, E.inC(rp) * 1250, 0, TAU); ctx.stroke(); ctx.restore(); }
}, 7);

// ============================================================ BEAT 6 — 3D timeline (400–540)  [placeholder until three_scene.js]
clip(392, 540, (ctx, t) => {
  if (window.draw3D) return window.draw3D(ctx, t);
  word(ctx, '3D timeline', FONTS.sans, 90, CX, CY, { color: C.mid });
}, 1);

// ============================================================ BEAT 7 — eye → lens → camera (540–612)
const EYES = [   // [from, image, px, py, size, mode]
  [540, 'android', 0.215, 0.235, 5200, 'h'],
  [548, 'head_front', 0.30, 0.37, 4600, 'h'],
  [556, 'metro_robot', 0.535, 0.186, 9000, 'h'],
  [564, 'melies', 0.40, 0.47, 4400, 'w'],
  [572, 'kin_camera', 0.82, 0.16, 3800, 'w'],
  [580, 'kin_proj', 0.06, 0.44, 3600, 'h'],
  [588, 'cam_obscura', 0.32, 0.66, 4200, 'w'],
];
clip(540, 616, (ctx, t) => {
  let cur = EYES[0]; EYES.forEach(e => { if (FR >= e[0]) cur = e; });
  const [f0, n, px, py, sz, mode] = cur;
  if (n !== 'cam_obscura') {
    const z = 1 + 0.05 * (1 - E.outC(prog(t, f0, f0 + 8)));
    pin(ctx, n, px, py, CX, CY, { [mode]: sz * z });
  } else {
    // pull back to the whole plate, travel to its title, push into the word "Camera"
    _CL = _CL || camLayout(ctx);
    const TITLE = { x: 0.4725, y: 0.040, w: 0.105 };
    const wEnd = 380 / TITLE.w, yWord = CAM.y - CAM.size * 0.27;
    const a = E.ioQuint(prog(t, 593, 602));
    const ax = lerp(px, TITLE.x, a), ay = lerp(py, TITLE.y, a);
    const sy = lerp(CY, yWord, a);
    const w = Math.exp(lerp(Math.log(lerp(sz, 1050, a)), Math.log(wEnd), E.ioC(prog(t, 601, 608))));
    const al = 1 - E.ioC(prog(t, 605, 609));
    pin(ctx, n, ax, ay, CX, sy, { w, a: al });
  }
  // lime lens ring (continuity) — shrinks away as we pull back
  const R = 150 * (1 - E.inBack(prog(t, 592, 600)));
  if (R > 1) { ctx.save(); ctx.strokeStyle = C.lime; ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(CX, CY, R, 0, TAU); ctx.stroke(); ctx.restore(); }
}, 8);

// ============================================================ BEAT 8 — camera → era → the line (604–770)
const CAM = { y: 1000, size: 250 };
const LINE = {
  // final layout (centred lines). each entry: [text, fam, size]
  y1: 790, y2: 1010, y3: 1230,
};
function camLayout(ctx) {
  ctx.font = `${CAM.size}px "${FONTS.sans}"`;
  const full = ctx.measureText('camera').width, cam = ctx.measureText('cam').width, era = ctx.measureText('era').width;
  return { full, cam, era, x0: CX - full / 2 };
}
let _CL = null;
const T_SEL = 626, T_RAZOR = 640, T_DEL = 644, T_SLIDE = 648, T_BUILD = 666;
function finalLayout(ctx) {
  const m = (txt, fam, size) => { ctx.font = `${size}px "${fam}"`; return ctx.measureText(txt).width; };
  const S1 = 172, S2s = 214, S2 = 172;
  const l1 = m('The AI', FONTS.sans, S1);
  const ed = m('editing', FONTS.serifI, S2s), sp = m(' ', FONTS.sans, S2), er = m('era', FONTS.sans, S2);
  const hb = m('has begun', FONTS.sans, S1), dots = 3 * 40 + 14;
  const l2 = ed + sp + er, l3 = hb + dots;
  return {
    S1, S2s, S2,
    the: { x: CX - l1 / 2, y: LINE.y1 },
    editing: { x: CX - l2 / 2, y: LINE.y2 },
    era: { x: CX - l2 / 2 + ed + sp, y: LINE.y2, w: er },
    has: { x: CX - l3 / 2, y: LINE.y3, w: hb },
  };
}
let _FL = null;
function maskRise(ctx, text, fam, size, x, y, u, color = C.ink) {
  // text rises into place from a baseline mask
  if (u <= 0) return;
  ctx.save();
  ctx.beginPath(); ctx.rect(x - 40, y - size * 1.05, 2000, size * 1.35); ctx.clip();
  ctx.font = `${size}px "${fam}"`; ctx.fillStyle = color; ctx.textBaseline = 'alphabetic';
  ctx.fillText(text, x, y + (1 - E.outQuint(u)) * size * 1.1);
  ctx.restore();
}
function typingDots(ctx, t, x, y, a = 1, spread = 1) {
  for (let i = 0; i < 3; i++) {
    const ti = 694 + i * 4;
    const u = E.outBack(prog(t, ti, ti + 6));
    if (u <= 0) continue;
    const wave = t > 706 ? Math.max(0, Math.sin((t - 706) * 0.17 - i * 0.9)) * 14 : 0;
    dot(ctx, x + i * 40 * spread, y - 16 - wave, 13 * u, C.terra, a);
  }
}
clip(604, 790, (ctx, t) => {
  _CL = _CL || camLayout(ctx); _FL = _FL || finalLayout(ctx);
  const L = _CL, F = _FL;
  // "camera" lands (letters drop in from the lens dot)
  const build = E.ioE(prog(t, T_BUILD, T_BUILD + 16));
  const slide = E.snap(prog(t, T_SLIDE, T_SLIDE + 12));
  const del = prog(t, T_DEL, T_DEL + 8);
  // era position: from its place inside "camera" → centred → final slot
  const eraX0 = L.x0 + L.cam, eraXc = CX - L.era / 2;
  const sEra = lerp(1, F.S2 / CAM.size, build);
  const eraX = lerp(lerp(eraX0, eraXc, slide), F.era.x, build);
  const eraY = lerp(CAM.y, F.era.y, build);
  // selection highlight over "cam" then over "era" in the final line
  const selA = E.snap(prog(t, T_SEL, T_SEL + 10));
  if (t < T_DEL + 6 && selA > 0) highlight(ctx, L.x0 - 10, L.x0 - 10 + (L.cam + 14) * selA, CAM.y - 200, 262, 1 - prog(t, T_DEL + 2, T_DEL + 6));
  // era highlight in the final line
  const eh = E.snap(prog(t, 704, 714)); const ehOut = E.inC(prog(t, 766, 774));
  if (eh > 0 && ehOut < 1) highlight(ctx, F.era.x - 12 + (F.era.w + 24) * ehOut, F.era.x - 12 + (F.era.w + 24) * eh, F.era.y - 138, 184, 1);
  // letters of "camera" — born at the engraving title's size, then grow to full size
  const yW = CAM.y - CAM.size * 0.27, sW = lerp(380 / L.full, 1, E.ioQuint(prog(t, 607, 619)));
  for (let i = 0; i < 6; i++) {
    const ch = 'camera'[i];
    ctx.save(); ctx.font = `${CAM.size}px "${FONTS.sans}"`;
    const before = ctx.measureText('camera'.slice(0, i)).width;
    const drop = E.ioC(prog(t, 605, 609));
    if (drop <= 0) { ctx.restore(); continue; }
    if (i < 3) {
      if (del >= 1) { ctx.restore(); continue; }
      const d = E.inBack(del);
      ctx.globalAlpha = drop * (1 - d);
      ctx.fillStyle = C.ink;
      ctx.translate(CX, yW); ctx.scale(sW, sW); ctx.translate(-CX, -yW);
      ctx.translate(L.x0 + before - d * 120, CAM.y + d * 60);
      ctx.scale(1 - d * 0.6, 1 - d * 0.6);
      ctx.fillText(ch, 0, 0);
    } else {
      if (t >= T_BUILD + 16) { ctx.restore(); continue; }
      const off = before - L.cam;
      ctx.globalAlpha = drop;
      ctx.fillStyle = C.ink;
      ctx.translate(CX, yW); ctx.scale(sW, sW); ctx.translate(-CX, -yW);
      ctx.translate(eraX + off * sEra, eraY);
      ctx.scale(sEra, sEra);
      ctx.fillText(ch, 0, 0);
    }
    ctx.restore();
  }
  // razor between m|e
  const rz = prog(t, T_RAZOR - 4, T_RAZOR + 2), rzo = 1 - prog(t, T_RAZOR + 4, T_RAZOR + 10);
  if (rz > 0 && rzo > 0) { const x = L.x0 + L.cam + 2; line(ctx, x, CAM.y - 330, x, lerp(CAM.y - 330, CAM.y + 120, E.outE(rz)), 8, C.lime, rzo, 'butt'); }
  // the rest of the line rises in
  // in: rise from the baseline mask; out: sink back into it (staggered)
  const io = (a0, k) => prog(t, a0, a0 + 16) * (1 - E.inQuint(prog(t, 766 + k * 2, 778 + k * 2)));
  maskRise(ctx, 'The AI', FONTS.sans, F.S1, F.the.x, F.the.y, io(T_BUILD + 6, 0));
  maskRise(ctx, 'editing', FONTS.serifI, F.S2s, F.editing.x, F.editing.y, io(T_BUILD + 10, 1));
  if (t >= T_BUILD + 16) maskRise(ctx, 'era', FONTS.sans, F.S2, F.era.x, F.era.y, 1 - E.inQuint(prog(t, 768, 780)));
  maskRise(ctx, 'has begun', FONTS.sans, F.S1, F.has.x, F.has.y, io(T_BUILD + 14, 2));
  // Claude typing… (merges into one dot at 780→790)
  const merge = E.ioE(prog(t, 776, 788));
  const dx = F.has.x + F.has.w + 22, dy = F.has.y;
  ctx.save(); ctx.translate(lerp(0, CX - (dx + 40), merge), lerp(0, CY - dy + 16, merge));
  typingDots(ctx, t, dx, dy, 1, 1 - merge);
  ctx.restore();
  // cursor selecting "cam"
  const ca = E.outC(prog(t, 618, 624)) * (1 - prog(t, T_RAZOR + 2, T_RAZOR + 6));
  if (ca > 0) { const cx = lerp(L.x0 - 10, L.x0 + L.cam, selA); cursor(ctx, cx + 20, CAM.y + 70, { a: ca, r: t * 0.05 }); }
}, 9);

// ============================================================ BEAT 9 — dot → spark → logo (786–900)
clip(786, 900, (ctx, t) => {
  const LW = 760;
  const g = logoGeom(CX, CY, LW);
  // the animated spark is the logo's own spark path → it lands exactly on the lockup
  const fx = g.ox + SPARK.cx * g.k, fy = g.oy + SPARK.cy * g.k, fsize = 2 * SPARK.rmax * g.k;
  const grow = prog(t, 788, 806);
  const move = E.ioQuint(prog(t, 806, 826));
  const bigS = 360;
  const sx = lerp(CX, fx, move), sy = lerp(CY, fy, move);
  const size = lerp(lerp(46, bigS, E.outC(grow)), fsize, move);
  const rot = lerp(-0.9, 0, E.outBack(grow)) * (1 - move);
  if (t < 826) spark(ctx, sx, sy, size, { grow: grow >= 1 ? 1 : E.outC(grow), r: rot, dotR: 0.18 });
  else logoSpark(ctx, CX, CY, LW);
  if (t >= 806) {
    const edge = t < 826 ? sx + size * 0.42 : -1e4;
    logoWord(ctx, CX, CY, LW, { clipX: edge, letter: (i, n) => { const u = E.outQuint(prog(t, 808 + i * 1.2, 826 + i * 1.2)); return { a: 1, dy: (1 - u) * 18 }; } });
  }
}, 11);
