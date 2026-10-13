// core.js — deterministic 2D compositor helpers for "The AI Editing Era".
// All times are in FRAMES (60 fps, float). Canvas is 1080x1920.
'use strict';
const W = 1080, H = 1920, FPS = 60;
const C = {
  bg: '#FFFFFF', ink: '#0E0E0E', lime: '#C6F432', limeDeep: '#A6DA12', limeInk: '#5E7D00',
  terra: '#D97757', gray: '#EDEDED', mid: '#A2A2A2', soft: '#F4F4F4',
};
const PI = Math.PI, TAU = Math.PI * 2;

// ---------------------------------------------------------------- math
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const mix = (a, b, t) => Array.isArray(a) ? a.map((v, i) => lerp(v, b[i], t)) : lerp(a, b, t);
function hash(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }

// ---------------------------------------------------------------- easing
const E = {
  lin: t => t,
  inQ: t => t * t, outQ: t => 1 - (1 - t) * (1 - t),
  ioQ: t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
  inC: t => t * t * t, outC: t => 1 - Math.pow(1 - t, 3),
  ioC: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  outQuint: t => 1 - Math.pow(1 - t, 5), inQuint: t => t ** 5,
  ioQuint: t => t < .5 ? 16 * t ** 5 : 1 - Math.pow(-2 * t + 2, 5) / 2,
  outE: t => t >= 1 ? 1 : 1 - Math.pow(2, -10 * t),
  inE: t => t <= 0 ? 0 : Math.pow(2, 10 * t - 10),
  ioE: t => t <= 0 ? 0 : t >= 1 ? 1 : t < .5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2,
  outBack: t => { const s = 1.70158; return 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2); },
  outBackS: t => { const s = 0.9; return 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2); },
  inBack: t => { const s = 1.70158; return (s + 1) * t * t * t - s * t * t; },
  outSine: t => Math.sin(t * PI / 2), ioSine: t => -(Math.cos(PI * t) - 1) / 2,
};
// CSS-style cubic-bezier
E.bez = (x1, y1, x2, y2) => t => {
  if (t <= 0) return 0; if (t >= 1) return 1;
  let u = t;
  for (let i = 0; i < 8; i++) {
    const x = 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u * u * x2 + u ** 3 - t;
    const dx = 3 * (1 - u) ** 2 * x1 + 6 * (1 - u) * u * (x2 - x1) + 3 * u * u * (1 - x2);
    if (Math.abs(x) < 1e-6 || dx === 0) break; u -= x / dx; u = clamp(u);
  }
  return 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u * u * y2 + u ** 3;
};
E.snap = E.bez(0.2, 0.0, 0.0, 1.0);      // UI snap — fast attack, long settle
E.swift = E.bez(0.7, 0.0, 0.15, 1.0);    // slow-in, very fast out (whip)
E.glide = E.bez(0.45, 0.0, 0.1, 1.0);
// damped spring 0→1 over frames (freq Hz, damping ratio)
function spring(f, freq = 3.2, damp = 0.55) {
  if (f <= 0) return 0;
  const t = f / FPS, w = TAU * freq, z = damp;
  if (z < 1) { const wd = w * Math.sqrt(1 - z * z); return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + z * w / wd * Math.sin(wd * t)); }
  return 1 - Math.exp(-w * t) * (1 + w * t);
}
// keyframes: [[f, value, ease?], ...] — ease applies to the segment ARRIVING at that key
function kf(t, keys) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const [f0, v0] = keys[i - 1], [f1, v1, ez] = keys[i];
      const u = (ez || E.ioC)((t - f0) / (f1 - f0));
      return mix(v0, v1, u);
    }
  }
  return keys[keys.length - 1][1];
}

// ---------------------------------------------------------------- assets
const IMG = {};
const META = {};
async function loadImages(manifest) {
  await Promise.all(Object.entries(manifest).map(async ([k, v]) => {
    const src = typeof v === 'string' ? v : v.src;
    const im = new Image(); im.src = src; await im.decode();
    IMG[k] = im; META[k] = typeof v === 'string' ? {} : v;
  }));
}
async function loadFonts(list) {
  for (const [fam, src, desc] of list) { const ff = new FontFace(fam, `url(${src})`, desc || {}); await ff.load(); document.fonts.add(ff); }
}

// ---------------------------------------------------------------- drawing
// draw image centered at (x,y) with height h (or width w), rotation r (rad), alpha a
function img(ctx, name, o = {}) {
  const im = IMG[name]; if (!im) throw new Error('missing image ' + name);
  const a = o.a == null ? 1 : o.a; if (a <= 0.001) return;
  let w, h;
  if (o.h != null) { h = o.h; w = h * im.width / im.height; }
  else if (o.w != null) { w = o.w; h = w * im.height / im.width; }
  else { w = im.width * (o.s || 1); h = im.height * (o.s || 1); }
  const ax = o.ax == null ? 0.5 : o.ax, ay = o.ay == null ? 0.5 : o.ay;
  ctx.save();
  ctx.globalAlpha *= a;
  if (o.comp) ctx.globalCompositeOperation = o.comp;
  if (o.blur > 0.25) ctx.filter = `blur(${o.blur.toFixed(2)}px)`;
  ctx.translate(o.x == null ? W / 2 : o.x, o.y == null ? H / 2 : o.y);
  if (o.r) ctx.rotate(o.r);
  if (o.sx) ctx.scale(o.sx, o.sy || 1);
  if (o.shadow) { ctx.shadowColor = o.shadow.c || 'rgba(0,0,0,0.18)'; ctx.shadowBlur = o.shadow.b || 40; ctx.shadowOffsetY = o.shadow.y || 18; }
  ctx.drawImage(im, -w * ax, -h * ay, w, h);
  ctx.restore();
}
// cover-fit an image into a rect (centered at cx,cy), optional focus (0..1) & zoom
function cover(ctx, name, cx, cy, rw, rh, o = {}) {
  const im = IMG[name]; if (!im) throw new Error('missing image ' + name);
  const fx = o.fx == null ? 0.5 : o.fx, fy = o.fy == null ? 0.5 : o.fy, z = o.z || 1;
  const s = Math.max(rw / im.width, rh / im.height) * z;
  const w = im.width * s, h = im.height * s;
  ctx.save();
  ctx.globalAlpha *= (o.a == null ? 1 : o.a);
  ctx.translate(cx, cy); if (o.r) ctx.rotate(o.r);
  ctx.beginPath(); ctx.rect(-rw / 2, -rh / 2, rw, rh); ctx.clip();
  if (o.blur > 0.25) ctx.filter = `blur(${o.blur.toFixed(2)}px)`;
  // focus point fx,fy of image lands at rect centre (clamped so the image always covers)
  let ox = -fx * w, oy = -fy * h;
  ox = clamp(ox, rw / 2 - w, -rw / 2); oy = clamp(oy, rh / 2 - h, -rh / 2);
  ctx.drawImage(im, ox + (o.dx || 0), oy + (o.dy || 0), w, h);
  ctx.restore();
}
function rrect(ctx, x, y, w, h, r) {
  r = Math.min(r, Math.abs(w) / 2, Math.abs(h) / 2);
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}

// ---------------------------------------------------------------- text
const FONTS = { serif: 'ISerif', serifI: 'ISerifItalic', sans: 'InterD600', sansB: 'InterD700', sansM: 'InterD500', sansX: 'InterD800' };
const _lay = {};
// glyph layout with kerning: returns [{ch,x,w}], width — x is left edge relative to string start
function layout(ctx, str, fam, size, track = 0) {
  const key = str + '|' + fam + '|' + size + '|' + track;
  if (_lay[key]) return _lay[key];
  ctx.save(); ctx.font = `${size}px "${fam}"`; ctx.letterSpacing = '0px';
  const g = [];
  for (let i = 0; i < str.length; i++) {
    const x0 = ctx.measureText(str.slice(0, i)).width + i * track;
    const w = ctx.measureText(str[i]).width;
    g.push({ ch: str[i], x: x0, w });
  }
  const width = ctx.measureText(str).width + (str.length - 1) * track;
  const m = ctx.measureText('Hxgk');
  ctx.restore();
  return (_lay[key] = { g, width, asc: m.actualBoundingBoxAscent, desc: m.actualBoundingBoxDescent });
}
// draw a word; per-glyph callback can alter {dx,dy,s,a,r,blur,color,fam}
function word(ctx, str, fam, size, x, y, o = {}) {
  const L = layout(ctx, str, fam, size, o.track || 0);
  const align = o.align == null ? 0.5 : o.align;
  const x0 = x - L.width * align;
  ctx.save();
  ctx.textBaseline = 'alphabetic';
  for (let i = 0; i < L.g.length; i++) {
    const gl = L.g[i];
    const p = Object.assign({ dx: 0, dy: 0, s: 1, a: 1, r: 0, blur: 0, color: o.color || C.ink, fam }, o.glyph ? o.glyph(i, gl, L) : {});
    if (p.a <= 0.002 || gl.ch === ' ') continue;
    ctx.save();
    ctx.globalAlpha *= p.a * (o.a == null ? 1 : o.a);
    ctx.fillStyle = p.color;
    ctx.font = `${size}px "${p.fam}"`;
    if (p.blur > 0.3) ctx.filter = `blur(${p.blur.toFixed(2)}px)`;
    const cx = x0 + gl.x + gl.w / 2 + p.dx, cy = y + p.dy;
    ctx.translate(cx, cy - size * 0.33); ctx.rotate(p.r); ctx.scale(p.s * (p.sx || 1), p.s * (p.sy || 1)); ctx.translate(0, size * 0.33);
    if (p.fam !== fam) { ctx.textAlign = 'center'; ctx.fillText(gl.ch, 0, 0); }
    else { ctx.textAlign = 'left'; ctx.fillText(gl.ch, -gl.w / 2, 0); }
    ctx.restore();
  }
  ctx.restore();
  return { x0, width: L.width, L };
}

// ---------------------------------------------------------------- Claude spark
// Official symbol path (viewBox 100x100). Sampled into a polar polygon so we can
// grow it from a dot with per-ray timing (perfect dot → spark morph).
const SPARK_D = 'm19.6 66.5 19.7-11 .3-1-.3-.5h-1l-3.3-.2-11.2-.3L14 53l-9.5-.5-2.4-.5L0 49l.2-1.5 2-1.3 2.9.2 6.3.5 9.5.6 6.9.4L38 49.1h1.6l.2-.7-.5-.4-.4-.4L29 41l-10.6-7-5.6-4.1-3-2-1.5-2-.6-4.2 2.7-3 3.7.3.9.2 3.7 2.9 8 6.1L37 36l1.5 1.2.6-.4.1-.3-.7-1.1L33 25l-6-10.4-2.7-4.3-.7-2.6c-.3-1-.4-2-.4-3l3-4.2L28 0l4.2.6L33.8 2l2.6 6 4.1 9.3L47 29.9l2 3.8 1 3.4.3 1h.7v-.5l.5-7.2 1-8.7 1-11.2.3-3.2 1.6-3.8 3-2L61 2.6l2 2.9-.3 1.8-1.1 7.7L59 27.1l-1.5 8.2h.9l1-1.1 4.1-5.4 6.9-8.6 3-3.5L77 13l2.3-1.8h4.3l3.1 4.7-1.4 4.9-4.4 5.6-3.7 4.7-5.3 7.1-3.2 5.7.3.4h.7l12-2.6 6.4-1.1 7.6-1.3 3.5 1.6.4 1.6-1.4 3.4-8.2 2-9.6 2-14.3 3.4-.2.1.2.3 6.4.6 2.8.2h6.8l12.6 1 3.3 2 1.9 2.7-.3 2-5.1 2.6-6.8-1.6-16-3.8-5.4-1.3h-.8v.4l4.6 4.5 8.3 7.5L89 80.1l.5 2.4-1.3 2-1.4-.2-9.2-7-3.6-3.1-8-6.8h-.5v.7l1.8 2.7 9.8 14.7.5 4.5-.7 1.4-2.6 1-2.7-.6-5.8-8-6-9-4.7-8.2-.5.4-2.9 30.2-1.3 1.5-3 1.2-2.5-2-1.4-3 1.4-6.2 1.6-8 1.3-6.4 1.2-7.9.7-2.6v-.2H49L43 72l-9 12.3-7.2 7.6-1.7.7-3-1.5.3-2.8L24 86l10-12.8 6-7.9 4-4.6-.1-.5h-.3L17.2 77.4l-4.7.6-2-2 .2-3 1-1 8-5.5Z';
const SPARK = { pts: null, cx: 50, cy: 50, rmax: 50 };
function initSpark(d) {
  d = d || SPARK_D;
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  p.setAttribute('d', d); svg.appendChild(p); document.body.appendChild(svg);
  const L = p.getTotalLength(), N = 900, pts = [];
  for (let i = 0; i < N; i++) { const q = p.getPointAtLength(L * i / N); pts.push([q.x, q.y]); }
  // centre = the point where the rays meet (area centroid is close enough; refine with bbox mid)
  let ax = 0, ay = 0, A = 0;
  for (let i = 0; i < N; i++) { const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % N]; const c = x0 * y1 - x1 * y0; A += c; ax += (x0 + x1) * c; ay += (y0 + y1) * c; }
  SPARK.cx = ax / (3 * A); SPARK.cy = ay / (3 * A);
  SPARK.pts = pts.map(([x, y]) => { const dx = x - SPARK.cx, dy = y - SPARK.cy; return { x, y, th: Math.atan2(dy, dx), r: Math.hypot(dx, dy) }; });
  SPARK.rmax = Math.max(...SPARK.pts.map(q => q.r));
  SPARK.path = new Path2D(d);
  document.body.removeChild(svg);
}
// draw spark centred at (x,y), size = diameter in px. grow: 0 (dot of radius dotR*size) → 1 (full spark)
function spark(ctx, x, y, size, o = {}) {
  const grow = o.grow == null ? 1 : o.grow, rot = o.r || 0, color = o.color || C.terra;
  const k = size / (2 * SPARK.rmax);
  ctx.save(); ctx.globalAlpha *= (o.a == null ? 1 : o.a);
  if (o.blur > 0.3) ctx.filter = `blur(${o.blur.toFixed(2)}px)`;
  ctx.translate(x, y); ctx.rotate(rot); ctx.scale(k * (o.sx || 1), k * (o.sy || 1));
  ctx.fillStyle = color;
  if (grow >= 0.999) { ctx.translate(-SPARK.cx, -SPARK.cy); ctx.fill(SPARK.path); }
  else {
    const dotR = (o.dotR == null ? 0.16 : o.dotR) * SPARK.rmax;
    ctx.beginPath();
    const spread = o.spread == null ? 0.35 : o.spread;
    SPARK.pts.forEach((q, i) => {
      // ray tips leave later than the core → rays shoot out of the dot
      const lag = (q.r / SPARK.rmax) * spread;
      const e = (o.ease || E.outC)(clamp((grow * (1 + spread) - lag)));
      const r = lerp(dotR, q.r, e);
      const xx = Math.cos(q.th) * r, yy = Math.sin(q.th) * r;
      if (i === 0) ctx.moveTo(xx, yy); else ctx.lineTo(xx, yy);
    });
    ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}
function dot(ctx, x, y, r, color, a = 1) {
  if (r <= 0 || a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.restore();
}
function line(ctx, x0, y0, x1, y1, w, color, a = 1, cap = 'round') {
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = cap;
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke(); ctx.restore();
}

// ---------------------------------------------------------------- Claude logo (official lockup)
const LOGO = {};
async function initLogo() {
  const j = await (await fetch('../assets/brand/logo.json')).json();
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  const mk = d => { const p = document.createElementNS('http://www.w3.org/2000/svg', 'path'); p.setAttribute('d', d); svg.appendChild(p); return p; };
  const ps = mk(j.spark), pw = mk(j.word); document.body.appendChild(svg);
  const bs = ps.getBBox(), bw = pw.getBBox();
  document.body.removeChild(svg);
  Object.assign(LOGO, { sparkD: j.spark, spark: new Path2D(j.spark), word: new Path2D(j.word), bs, bw,
    // full lockup bbox in path coords
    x0: Math.min(bs.x, bw.x), x1: Math.max(bs.x + bs.width, bw.x + bw.width),
    y0: Math.min(bs.y, bw.y), y1: Math.max(bs.y + bs.height, bw.y + bw.height) });
  // per-letter clip ranges for the wordmark: split by x gaps in a rasterised alpha profile
  const c = document.createElement('canvas'); c.width = Math.ceil(bw.width) + 4; c.height = Math.ceil(bw.height) + 4;
  const x = c.getContext('2d'); x.translate(2 - bw.x, 2 - bw.y); x.fill(LOGO.word);
  const d = x.getImageData(0, 0, c.width, c.height).data, cols = [];
  for (let i = 0; i < c.width; i++) { let s = 0; for (let k = 0; k < c.height; k++) s += d[(k * c.width + i) * 4 + 3]; cols.push(s > 0); }
  const runs = []; let s0 = null;
  cols.forEach((v, i) => { if (v && s0 === null) s0 = i; if (!v && s0 !== null) { runs.push([s0, i]); s0 = null; } });
  if (s0 !== null) runs.push([s0, cols.length]);
  LOGO.letters = runs.map(([a, b]) => [a - 2 + bw.x, b - 2 + bw.x]);
}
// draw the lockup so the full lockup width = width, centred at (cx, cy).
// o.sparkFn(ctx, sx, sy, sizePx) lets the caller draw its own (animated) spark at the logo-spark position.
function logoGeom(cx, cy, width) {
  const k = width / (LOGO.x1 - LOGO.x0);
  const ox = cx - (LOGO.x0 + (LOGO.x1 - LOGO.x0) / 2) * k, oy = cy - (LOGO.y0 + (LOGO.y1 - LOGO.y0) / 2) * k;
  const bs = LOGO.bs;
  return { k, ox, oy, sx: ox + (bs.x + bs.width / 2) * k, sy: oy + (bs.y + bs.height / 2) * k, sw: bs.width * k, sh: bs.height * k };
}
function logoWord(ctx, cx, cy, width, o = {}) {
  const g = logoGeom(cx, cy, width);
  ctx.save(); ctx.globalAlpha *= (o.a == null ? 1 : o.a);
  ctx.fillStyle = '#0f0f0d';
  LOGO.letters.forEach(([a, b], i) => {
    const p = o.letter ? o.letter(i, LOGO.letters.length) : { a: 1, dy: 0 };
    if (p.a <= 0) return;
    ctx.save(); ctx.globalAlpha *= p.a;
    ctx.beginPath(); ctx.rect(g.ox + (a - 1) * g.k, -9999, (b - a + 2) * g.k, 99999);
    if (o.clipX != null) { ctx.clip(); ctx.beginPath(); ctx.rect(o.clipX, -9999, 99999, 99999); }
    ctx.clip();
    ctx.translate(g.ox, g.oy + (p.dy || 0)); ctx.scale(g.k, g.k); ctx.fill(LOGO.word);
    ctx.restore();
  });
  ctx.restore();
  return g;
}
function logoSpark(ctx, cx, cy, width, o = {}) {
  const g = logoGeom(cx, cy, width);
  ctx.save(); ctx.globalAlpha *= (o.a == null ? 1 : o.a); ctx.fillStyle = C.terra;
  ctx.translate(g.ox, g.oy); ctx.scale(g.k, g.k); ctx.fill(LOGO.spark); ctx.restore();
  return g;
}
