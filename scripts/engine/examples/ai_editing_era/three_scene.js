// three_scene.js — Beat 6: a flat timeline that tilts into clean 3D, gets razored, then we dive into a clip.
'use strict';
(function () {
  const T0 = 400, T1 = 540;
  let R, scene, cam, glc, clips = [], playhead, phLine, floorShadow, target;
  const TRACKS = [-2.3, -1.15, 0, 1.15, 2.3];
  const DEPTH = 0.92, THICK = 0.16;
  // [track, x0, length, image, cutAt (fraction) or null]
  const LAYOUT = [
    [0, -9.4, 2.6, 'marey_hurdle'], [0, -6.6, 1.8, 'jd_profile'], [0, -4.6, 3.1, 'mh3'], [0, -1.3, 2.2, 'kin_tripod', 0.5], [0, 1.1, 2.6, 'vesalius'], [0, 3.9, 2.0, 'jacquard'], [0, 6.1, 3.0, 'composition'],
    [1, -10.2, 3.0, 'turk_col'], [1, -7.0, 2.2, 'head_r'], [1, -4.6, 2.6, 'melies', 0.4], [1, -1.8, 1.6, 'jd_dog'], [1, 0.0, 2.8, 'praxi_photo', 0.55], [1, 3.0, 2.4, 'typewriter'], [1, 5.6, 2.8, 'r_film'],
    [2, -9.6, 2.0, 'metro_scene'], [2, -7.4, 2.8, 'cam_obscura'], [2, -4.4, 2.2, 'moviola_c'], [2, -2.0, 3.2, 'android'], [2, 1.4, 2.0, 'mh7'], [2, 3.6, 2.6, 'robot_engr'], [2, 6.4, 2.2, 'head_front'],
    [3, -10.4, 2.4, 'ecr_alpha'], [3, -7.8, 2.6, 'kin_camera'], [3, -5.0, 1.8, 'vaucanson'], [3, -3.0, 2.8, 'phen_couple', 0.45], [3, 0.0, 2.2, 'metro_robot'], [3, 2.4, 3.0, 'optics'], [3, 5.6, 2.4, 'r_pinch'],
    [4, -9.8, 3.2, 'imprimerie'], [4, -6.4, 2.0, 'head_l'], [4, -4.2, 2.6, 'mh9'], [4, -1.4, 2.4, 'jacquard_card', 0.5], [4, 1.2, 2.8, 'turk'], [4, 4.2, 2.0, 'phen_rats'], [4, 6.4, 2.6, 'r_scissors'],
  ];
  function texFor(name, w, d, px = 320) {
    const cw = Math.round(px * w), ch = Math.round(px * d);
    const c = document.createElement('canvas'); c.width = cw; c.height = ch;
    const x = c.getContext('2d');
    x.fillStyle = '#FFFFFF'; x.fillRect(0, 0, cw, ch);
    const im = IMG[name];
    if (im) {
      const contain = (META[name] || {}).kind !== 'photo';
      const s = contain ? Math.min(cw / im.width, ch / im.height) * 0.92 : Math.max(cw / im.width, ch / im.height);
      x.drawImage(im, (cw - im.width * s) / 2, (ch - im.height * s) / 2, im.width * s, im.height * s);
    }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    return t;
  }
  function makeClip(w, d, tex, u0 = 0, u1 = 1) {
    const g = new THREE.Group();
    const body = new THREE.Mesh(new RoundedBoxGeometry(w, THICK, d, 4, 0.05),
      new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.28, clearcoat: 1, clearcoatRoughness: 0.12, envMapIntensity: 0.55 }));
    body.castShadow = true; body.receiveShadow = true; g.add(body);
    const inset = 0.05;
    const pg = new THREE.PlaneGeometry(w - inset * 2, d - inset * 2);
    // map only the [u0,u1] slice (for split halves)
    const uv = pg.attributes.uv;
    for (let i = 0; i < uv.count; i++) uv.setX(i, u0 + uv.getX(i) * (u1 - u0));
    const face = new THREE.Mesh(pg, new THREE.MeshBasicMaterial({ map: tex }));
    face.rotation.x = -Math.PI / 2; face.position.y = THICK / 2 + 0.003; face.receiveShadow = true;
    g.add(face);
    return g;
  }
  window.init3D = function () {
    glc = document.createElement('canvas'); glc.width = W; glc.height = H;
    R = new THREE.WebGLRenderer({ canvas: glc, antialias: true, preserveDrawingBuffer: true, alpha: false });
    R.setPixelRatio(1); R.setSize(W, H, false);
    R.outputColorSpace = THREE.SRGBColorSpace;
    R.toneMapping = THREE.NoToneMapping;
    R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFShadowMap;
    scene = new THREE.Scene(); scene.background = new THREE.Color(0xffffff);
    const pm = new THREE.PMREMGenerator(R);
    scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    const hemi = new THREE.HemisphereLight(0xffffff, 0xdcdcdc, 1.1); scene.add(hemi);
    const sun = new THREE.DirectionalLight(0xffffff, 1.25);
    sun.position.set(-6, 14, 5); sun.castShadow = true;
    sun.shadow.mapSize.set(4096, 4096); sun.shadow.radius = 6; sun.shadow.bias = -0.0004;
    Object.assign(sun.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16, near: 1, far: 40 });
    scene.add(sun);
    floorShadow = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.ShadowMaterial({ opacity: 0.13 }));
    floorShadow.rotation.x = -Math.PI / 2; floorShadow.receiveShadow = true; scene.add(floorShadow);
    // faint track lanes
    TRACKS.forEach(z => {
      const lane = new THREE.Mesh(new THREE.PlaneGeometry(40, DEPTH + 0.1), new THREE.MeshBasicMaterial({ color: 0xf3f3f3 }));
      lane.rotation.x = -Math.PI / 2; lane.position.set(0, 0.001, z); scene.add(lane);
    });
    LAYOUT.forEach(([tr, x0, len, name, cut], i) => {
      const tex = texFor(name, len - 0.08 - 0.1, DEPTH - 0.1, name === 'android' ? 1500 : 320);
      const whole = makeClip(len - 0.08, DEPTH, tex);
      const c = { i, tr, x: x0 + len / 2, len, name, cut, whole };
      if (cut != null) {
        const lA = (len - 0.08) * cut, lB = (len - 0.08) * (1 - cut);
        c.a = makeClip(lA - 0.02, DEPTH, tex, 0, cut); c.b = makeClip(lB - 0.02, DEPTH, tex, cut, 1);
        c.ax = -((len - 0.08) / 2) + lA / 2; c.bx = (len - 0.08) / 2 - lB / 2;
        scene.add(c.a, c.b);
        c.seam = new THREE.Mesh(new THREE.BoxGeometry(0.035, THICK + 0.04, DEPTH + 0.12), new THREE.MeshBasicMaterial({ color: 0xc6f432, transparent: true }));
        scene.add(c.seam);
      }
      scene.add(whole);
      clips.push(c);
    });
    target = clips.find(c => c.name === 'android');
    // playhead: lime glass blade + floor line
    playhead = new THREE.Group();
    const sheet = new THREE.Mesh(new THREE.PlaneGeometry(6.4, 0.6), new THREE.MeshBasicMaterial({ color: 0xc6f432, transparent: true, opacity: 0.22, side: THREE.DoubleSide, depthWrite: false }));
    sheet.rotation.y = Math.PI / 2; playhead.add(sheet);
    const edge = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.05, 6.6), new THREE.MeshBasicMaterial({ color: 0xc6f432 }));
    edge.position.y = 0.3; playhead.add(edge);
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.13, 24, 16), new THREE.MeshBasicMaterial({ color: 0xc6f432 }));
    knob.position.set(0, 0.3, -3.3); playhead.add(knob);
    scene.add(playhead);
    phLine = new THREE.Mesh(new THREE.PlaneGeometry(0.08, 6.6), new THREE.MeshBasicMaterial({ color: 0xc6f432 }));
    phLine.rotation.x = -Math.PI / 2; scene.add(phLine);
    cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 200);
  };
  // ------------------------------------------------------------ camera
  // A: top-down over the timeline  →  B: low, looking down the tracks  →  C: straight above the android's eye
  // exact eye position inside the android texture (same contain maths as texFor)
  function faceGeom() {
    const c = target, fw = c.len - 0.08 - 0.1, fd = DEPTH - 0.1, im = IMG.android, px = 1500;
    const cw = Math.round(px * fw), ch = Math.round(px * fd);
    const s = Math.min(cw / im.width, ch / im.height) * 0.92;
    const x0 = (cw - im.width * s) / 2, y0 = (ch - im.height * s) / 2;
    return { fw, fd, u: (x0 + 0.215 * im.width * s) / cw, v: (y0 + 0.235 * im.height * s) / ch, hUnits: im.height * s / ch * fd };
  }
  let EYE = null;
  function eyeWorld() {
    EYE = EYE || faceGeom();
    const c = target, fw = c.len - 0.08 - 0.1, fd = DEPTH - 0.1;
    return new THREE.Vector3(c.x + (EYE.u - 0.5) * fw, 0, TRACKS[c.tr] + (EYE.v - 0.5) * fd);
  }
  function qLook(p, l, up) { const m = new THREE.Matrix4().lookAt(p, l, up); return new THREE.Quaternion().setFromRotationMatrix(m); }
  const LIFT = 0.0;
  function camAt(t) {
    const A = { p: new THREE.Vector3(0.4, 15.5, 0.0001), l: new THREE.Vector3(0.4, 0, 0), up: new THREE.Vector3(0, 0, -1) };
    const B = { p: new THREE.Vector3(-9.0, 3.0, 1.5), l: new THREE.Vector3(3.0, -0.6, -0.4), up: new THREE.Vector3(0, 1, 0) };
    const qa = qLook(A.p, A.l, A.up), qb = qLook(B.p, B.l, B.up);
    const u = E.ioQuint(prog(t, 422, 484));
    const pA = A.p.clone(); pA.y -= 1.8 * E.outC(prog(t, 400, 424));
    const p = new THREE.Vector3().lerpVectors(pA, B.p, u);
    p.y += Math.sin(u * Math.PI) * 2.4;
    const q = new THREE.Quaternion().slerpQuaternions(qa, qb, u);
    const push = E.ioC(prog(t, 484, 510));
    p.x += push * 2.4; p.y -= push * 0.6;
    // dive: end exactly above the eye, texture-up = screen-up
    const d = E.ioQuint(prog(t, 500, 531));
    if (d > 0) {
      const e = eyeWorld(); e.y = THICK + 0.003;
      const end = e.clone().add(new THREE.Vector3(0, DIVE_D * (1 + 0.04 * (1 - E.outC(prog(t, 531, 540)))), 0));
      const p0 = p.clone();
      // quadratic bezier with a raised control point
      const ctl = new THREE.Vector3((p0.x + end.x) / 2, Math.max(p0.y, end.y) + 2.2, (p0.z + end.z) / 2);
      p.set(0, 0, 0).addScaledVector(p0, (1 - d) ** 2).addScaledVector(ctl, 2 * (1 - d) * d).addScaledVector(end, d * d);
      const up = new THREE.Vector3(0, 1, 0).lerp(new THREE.Vector3(0, 0, -1), E.ioC(d)).normalize();
      const qe = qLook(p, e, up);
      q.slerp(qe, E.outC(prog(t, 500, 512)));
    }
    return { p, q };
  }
  // camera height above the face at the end of the dive so the 2D android (h = 5200*1.05) matches exactly
  const IMG_H_UNITS = () => faceGeom().hUnits;
  let DIVE_D = 0.55;
  function phX(t) { return kf(t, [[400, -11.5], [440, -7.0, E.ioC], [502, 7.5, E.ioC], [540, 10]]); }
  window.draw3D = function (ctx, t) {
    if (!R) { init3D(); DIVE_D = IMG_H_UNITS() / (5200 * 1.05 / H) / (2 * Math.tan(15 * Math.PI / 180)); }
    const px = phX(t);
    playhead.position.set(px, 0.3, 0); phLine.position.set(px, 0.004, 0);
    playhead.visible = phLine.visible = t < 508;
    clips.forEach(c => {
      const z = TRACKS[c.tr];
      const ti = 384 + c.tr * 2.5 + (c.tr % 2 ? (12 - c.x) : (c.x + 12)) * 0.75;
      const s = spring(t - ti, 2.4, 0.58);
      const dir = c.tr % 2 ? 1 : -1;
      const xoff = (1 - s) * 13 * dir;
      let y = THICK / 2 + Math.max(0, 1 - s) * 0.6; const rx = 0;
      if (c === target) y += LIFT * E.ioQuint(prog(t, 504, 532));
      if (c.cutT == null) {
        c.cutT = 1e9;
        if (c.cut != null) { const xc = c.x - c.len / 2 + c.len * c.cut; let tt = 400; while (tt < 540 && phX(tt) < xc) tt += 0.25; c.cutT = tt; }
      }
      const isCut = t >= c.cutT;
      c.whole.visible = !isCut;
      c.whole.position.set(c.x + xoff, y, z); c.whole.rotation.set(rx, 0, 0);
      if (c.a) {
        c.a.visible = c.b.visible = isCut;
        const sp = prog(t, c.cutT, c.cutT + 14), sep = E.outBack(sp) * 0.36, hop = Math.sin(clamp(sp * 1.6) * Math.PI) * 0.22;
        c.a.position.set(c.x + c.ax - sep + xoff, y + hop, z); c.b.position.set(c.x + c.bx + sep + xoff, y + hop * 0.7, z);
        c.a.rotation.set(0, 0, hop * 0.5); c.b.rotation.set(0, 0, -hop * 0.4);
        if (c.seam) { c.seam.visible = t >= c.cutT && t < c.cutT + 26; c.seam.position.set(c.x - c.len / 2 + c.len * c.cut + xoff, y + 0.02, z); c.seam.material.opacity = 1 - prog(t, c.cutT + 8, c.cutT + 26); c.seam.scale.x = 1 + E.outC(sp) * 8; }
      }
    });
    const k = camAt(t);
    cam.position.copy(k.p); cam.quaternion.copy(k.q); cam.updateMatrixWorld();
    R.render(scene, cam);
    ctx.drawImage(glc, 0, 0);
    // hand-off: the crisp 2D android fades in exactly over its 3D texture
    if (false && window.DBG_MARK) { const G = faceGeom(), c = target, z = TRACKS[c.tr], yF = THICK + 0.003;
      const im = IMG.android, cw = Math.round(1500 * G.fw), ch = Math.round(1500 * G.fd), s2 = Math.min(cw / im.width, ch / im.height) * 0.92;
      const iu = u => ((cw - im.width * s2) / 2 + u * im.width * s2) / cw, iv = v => ((ch - im.height * s2) / 2 + v * im.height * s2) / ch;
      [[iu(0.215), iv(0.235)], [iu(0.215), iv(0.0)], [iu(0.0), iv(0.235)], [iu(0.35), iv(0.40)], [iu(0.10), iv(0.40)]].forEach(([u,v]) => { const q = new THREE.Vector3(c.x + (u - 0.5) * G.fw, yF, z + (v - 0.5) * G.fd).project(cam); dot(ctx, (q.x+1)/2*W, (1-q.y)/2*H, 8, '#ff0000'); }); }
    const hand = prog(t, 524, 536);
    if (hand > 0) {
      // project the image rectangle of the android texture → affine-map the crisp 2D image onto it,
      // then settle onto beat 7's exact framing (eye at centre, h = 5460).
      const G = faceGeom(), c = target, im = IMG.android, z = TRACKS[c.tr], yF = THICK + 0.003;
      const cw = Math.round(1500 * G.fw), ch = Math.round(1500 * G.fd);
      const s2 = Math.min(cw / im.width, ch / im.height) * 0.92;
      const u0 = (cw - im.width * s2) / 2 / cw, u1 = 1 - u0, v0 = (ch - im.height * s2) / 2 / ch, v1 = 1 - v0;
      const P = (u, v) => { const q = new THREE.Vector3(c.x + (u - 0.5) * G.fw, yF, z + (v - 0.5) * G.fd).project(cam); return [(q.x + 1) / 2 * W, (1 - q.y) / 2 * H]; };
      const TL = P(u0, v0), TR = P(u1, v0), BL = P(u0, v1);
      // beat-7 target transform
      const hT = 5200 * 1.05, wT = hT * im.width / im.height;
      const TL2 = [CX - 0.215 * wT, CY - 0.235 * hT], TR2 = [TL2[0] + wT, TL2[1]], BL2 = [TL2[0], TL2[1] + hT];
      if (window.DBG_LOG) console.log(JSON.stringify({t, TL, TR, BL, TL2, TR2, BL2, D: DIVE_D, hU: G.hUnits, cam: cam.position.toArray()}));
      const k = E.ioC(prog(t, 530, 539));
      const L = (p, q) => [lerp(p[0], q[0], k), lerp(p[1], q[1], k)];
      const A = L(TL, TL2), B = L(TR, TR2), Cc = L(BL, BL2);
      ctx.save(); ctx.globalAlpha = window.DBG_OVERLAY_A != null ? window.DBG_OVERLAY_A : E.ioC(hand);
      ctx.setTransform((B[0] - A[0]) / im.width, (B[1] - A[1]) / im.width, (Cc[0] - A[0]) / im.height, (Cc[1] - A[1]) / im.height, A[0], A[1]);
      ctx.drawImage(im, 0, 0);
      ctx.restore();
    }
  };
})();
