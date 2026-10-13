// scene.js — STARTER. Copy to <project>/engine/scene.js and replace the beats.
// Full worked example: examples/ai_editing_era/scene.js (900 f, 9 beats, every morph in references/morph-cookbook.md).
'use strict';
const SHUTTER = 0.5;                                   // 180° shutter, in frames
const Q = new URLSearchParams(location.search);
const SUB_DEFAULT = +(Q.get('sub') || 1);
function subsamples(f) { return SUB_DEFAULT; }        // capture.js --sub N overrides
const has = n => !!IMG[n];
const CX = W / 2, CY = H / 2;

// ------------------------------------------------------------ clip registry
const CLIPS = [];
function clip(a, b, draw, z = 0) { CLIPS.push({ a, b, draw, z }); CLIPS.sort((p, q) => p.z - q.z); }
let FR = 0;                                            // integer frame: use for HARD-CUT decisions (never the sub-frame t)
function drawScene(ctx, t, f) {
  FR = f;
  for (const c of CLIPS) if (f >= c.a && f < c.b) { ctx.save(); c.draw(ctx, t, f); ctx.restore(); }
}

// ------------------------------------------------------------ BEAT 1 — word lands, razor cuts it, halves part (0–44)
const CUT = { cy: 930, ang: -0.5, t0: 4, t1: 14, split0: 22, split1: 44 };
function titleWord(ctx, t) {
  const u = E.outE(prog(t, -6, 12));
  ctx.save(); ctx.translate(CX, CUT.cy); ctx.scale(lerp(1.08, 1, u), lerp(1.08, 1, u)); ctx.translate(-CX, -CUT.cy);
  word(ctx, 'cut', FONTS.serif, 500, CX, CUT.cy + 120, { glyph: () => ({ blur: lerp(10, 0, u) }) });
  ctx.restore();
}
clip(0, 46, (ctx, t) => {
  if (FR < CUT.split0) {
    titleWord(ctx, t);
    const p = E.ioQ(prog(t, CUT.t0, CUT.t1)), L = 1400, dx = Math.cos(CUT.ang), dy = Math.sin(CUT.ang);
    if (p > 0) line(ctx, CX - dx * L, CUT.cy - dy * L, CX + dx * L * (2 * p - 1), CUT.cy + dy * L * (2 * p - 1), 10, C.lime, 1, 'butt');
  } else {
    beat2(ctx, t);                                     // next scene shows through the gap
    const d = kf(t, [[CUT.split0, 0], [CUT.split1, 1300, E.ioE]]);
    const nx = -Math.sin(CUT.ang), ny = Math.cos(CUT.ang), tx = Math.cos(CUT.ang), ty = Math.sin(CUT.ang);
    for (const s of [-1, 1]) {
      ctx.save(); ctx.translate(nx * d * s, ny * d * s);
      const B = 4000; ctx.beginPath();
      ctx.moveTo(CX - tx * B, CUT.cy - ty * B); ctx.lineTo(CX + tx * B, CUT.cy + ty * B);
      ctx.lineTo(CX + tx * B + nx * B * s, CUT.cy + ty * B + ny * B * s); ctx.lineTo(CX - tx * B + nx * B * s, CUT.cy - ty * B + ny * B * s);
      ctx.closePath(); ctx.clip(); ctx.fillStyle = C.bg; ctx.fillRect(-3000, -3000, W + 6000, H + 6000);
      titleWord(ctx, 30); ctx.restore();
    }
  }
}, 10);

// ------------------------------------------------------------ BEAT 2 — an image framed by a lime crop box (22–120)
function beat2(ctx, t) {
  const [cx, cy, w, h] = kf(t, [[22, [CX, 900, 860, 600]], [70, [CX, 900, 860, 600]], [78, [CX, 900, 640, 640], E.snap]]);
  const name = Object.keys(IMG)[0];                    // replace with a manifest key
  if (!name) return;
  img(ctx, name, { x: CX, y: 900, w: 1300, a: 0.13 }); // ghost outside the crop
  ctx.save(); ctx.beginPath(); ctx.rect(cx - w / 2, cy - h / 2, w, h); ctx.clip();
  ctx.fillStyle = C.bg; ctx.fillRect(cx - w / 2, cy - h / 2, w, h); img(ctx, name, { x: CX, y: 900, w: 1300 }); ctx.restore();
  ctx.save(); ctx.strokeStyle = C.lime; ctx.lineWidth = 6; ctx.strokeRect(cx - w / 2, cy - h / 2, w, h); ctx.restore();
}
clip(46, 120, (ctx, t) => beat2(ctx, t));

// ------------------------------------------------------------ BEAT 3 — dot → spark → logo lockup (120–240)
clip(120, 240, (ctx, t) => {
  if (!LOGO.bs) { spark(ctx, CX, CY, lerp(46, 360, E.outC(prog(t, 122, 140))), { grow: E.outC(prog(t, 122, 140)) }); return; }
  const LW = 760, g = logoGeom(CX, CY, LW);
  const fx = g.ox + SPARK.cx * g.k, fy = g.oy + SPARK.cy * g.k, fsize = 2 * SPARK.rmax * g.k;
  const grow = prog(t, 122, 140), move = E.ioQuint(prog(t, 140, 160));
  const sx = lerp(CX, fx, move), sy = lerp(CY, fy, move), size = lerp(lerp(46, 360, E.outC(grow)), fsize, move);
  if (FR < 160) spark(ctx, sx, sy, size, { grow: grow >= 1 ? 1 : E.outC(grow), r: lerp(-0.9, 0, E.outBack(grow)) * (1 - move), dotR: 0.18 });
  else logoSpark(ctx, CX, CY, LW);
  if (t >= 140) logoWord(ctx, CX, CY, LW, { clipX: FR < 160 ? sx + size * 0.42 : -1e4 });
}, 11);
