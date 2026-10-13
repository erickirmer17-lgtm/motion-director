// capture.js — render frames of engine/index.html with headless Chrome.
// usage: node capture.js --from 0 --to 899 --out ../render/frames [--step 1 | --list 10,20] [--scale 0.5] [--sub N] [--workers 4] [--jpg]
//        [--w 1080 --h 1920 --fps 60]  (format; default 9:16 1080x1920@60)  [--verbose] (show 404s)
const http = require('http'), fs = require('fs'), path = require('path');
const puppeteer = require('puppeteer-core');
const ROOT = path.resolve(__dirname, '..');
const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => {
  if (v.startsWith('--')) a.push([v.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true]); return a;
}, []));
const from = +(args.from || 0), to = +(args.to || 899), step = +(args.step || 1);
const scale = +(args.scale || 1), sub = args.sub ? +args.sub : 0, workers = +(args.workers || 4);
const outDir = path.resolve(args.out || path.join(ROOT, 'render/frames'));
const list = args.list ? String(args.list).split(',').map(Number) : null;
const FW = +(args.w || 1080), FH = +(args.h || 1920), FPSA = +(args.fps || 60);
fs.mkdirSync(outDir, { recursive: true });

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.ttf': 'font/ttf', '.svg': 'image/svg+xml', '.webp': 'image/webp' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (err, d) => {
    if (err) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream', 'Cache-Control': 'no-store' }); res.end(d);
  });
});

(async () => {
  await new Promise(r => server.listen(0, r));
  const port = server.address().port;
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: 'new',
    args: ['--hide-scrollbars', '--force-device-scale-factor=1', '--use-angle=metal', '--enable-gpu-rasterization', '--ignore-gpu-blocklist', '--disable-background-timer-throttling', '--disable-renderer-backgrounding'],
  });
  const frames = list || [];
  if (!list) for (let f = from; f <= to; f += step) frames.push(f);
  const chunks = Array.from({ length: workers }, (_, w) => frames.filter((_, i) => i % workers === w));
  const t0 = Date.now(); let done = 0;
  await Promise.all(chunks.map(async (chunk) => {
    if (!chunk.length) return;
    const page = await browser.newPage();
    page.on('console', m => {
      const t = m.text();
      if (!args.verbose && /Failed to load resource.*404/.test(t)) return;      // favicon / optional logo.json / fonts.json
      if (m.type() === 'error' || m.type() === 'warn' || t.startsWith('[log]')) console.log('[page]', t);
    });
    page.on('pageerror', e => console.log('[pageerror]', e.message));
    await page.setViewport({ width: FW, height: FH, deviceScaleFactor: 1 });
    await page.goto(`http://localhost:${port}/engine/index.html?w=${FW}&h=${FH}&fps=${FPSA}`, { waitUntil: 'load' });
    await page.evaluate(() => window.READY);
    for (const f of chunk) {
      const dataUrl = await page.evaluate(({ f, sub, scale, jpg }) => {
        renderFrame(f, sub || undefined);
        const c = document.getElementById('out');
        if (scale !== 1) {
          const s = document.createElement('canvas'); s.width = Math.round(c.width * scale); s.height = Math.round(c.height * scale);
          const x = s.getContext('2d'); x.imageSmoothingQuality = 'high'; x.drawImage(c, 0, 0, s.width, s.height);
          return s.toDataURL(jpg ? 'image/jpeg' : 'image/png', 0.9);
        }
        return c.toDataURL(jpg ? 'image/jpeg' : 'image/png', 0.95);
      }, { f, sub, scale, jpg: !!args.jpg });
      const b64 = dataUrl.split(',')[1];
      fs.writeFileSync(path.join(outDir, `f${String(f).padStart(4, '0')}.${args.jpg ? 'jpg' : 'png'}`), Buffer.from(b64, 'base64'));
      done++;
      if (done % 25 === 0) console.log(`${done}/${frames.length}  ${((Date.now() - t0) / done).toFixed(0)} ms/frame`);
    }
    await page.close();
  }));
  console.log(`done ${frames.length} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
