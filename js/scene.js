// Manidhay hero 3D scene (three.js).
// A realistic modern villa built procedurally with PBR materials, lit by a real HDRI sky.
// To show your own architect's model instead, put a .glb file in /models and set
// <canvas data-scene="hero" data-model="models/your-house.glb">.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

// CC0 sky from Poly Haven (polyhaven.com), used only for lighting and reflections
const HDRI = 'https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/kloofendal_48d_partly_cloudy_puresky_1k.hdr';
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

let seed = 7;
const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

/* ---------- Procedural textures (drawn once on a canvas) ---------- */
function canvasTexture(size, draw) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  draw(c.getContext('2d'), size);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  return t;
}
const speckle = (ctx, s, base, tones, count, maxR) => {
  ctx.fillStyle = base; ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < count; i++) {
    ctx.globalAlpha = rand() * .07;
    ctx.fillStyle = tones[i % tones.length];
    ctx.beginPath(); ctx.arc(rand() * s, rand() * s, rand() * maxR + .5, 0, 7); ctx.fill();
  }
  ctx.globalAlpha = 1;
};
const planks = (ctx, s, n, tones, vertical) => {
  const w = s / n;
  for (let i = 0; i < n; i++) {
    ctx.fillStyle = tones[Math.floor(rand() * tones.length)];
    vertical ? ctx.fillRect(i * w, 0, w, s) : ctx.fillRect(0, i * w, s, w);
    ctx.globalAlpha = .18; ctx.strokeStyle = '#3b2414';
    for (let g = 0; g < 7; g++) {
      ctx.lineWidth = rand() * 1.4 + .3;
      ctx.beginPath();
      const o = i * w + rand() * w;
      vertical ? (ctx.moveTo(o, 0), ctx.bezierCurveTo(o + 4, s * .3, o - 4, s * .7, o + 2, s))
               : (ctx.moveTo(0, o), ctx.bezierCurveTo(s * .3, o + 4, s * .7, o - 4, s, o + 2));
      ctx.stroke();
    }
    ctx.globalAlpha = .55; ctx.fillStyle = '#2a1a10';
    vertical ? ctx.fillRect(i * w, 0, 2, s) : ctx.fillRect(0, i * w, s, 2);
    ctx.globalAlpha = 1;
  }
};
const tiles = (ctx, s, n, base, joint, jitter) => {
  speckle(ctx, s, base, ['#ffffff', '#9c9486'], 1500, 3);
  const w = s / n;
  for (let x = 0; x < n; x++) for (let y = 0; y < n; y++) {
    ctx.globalAlpha = rand() * jitter; ctx.fillStyle = rand() > .5 ? '#ffffff' : '#7d766a';
    ctx.fillRect(x * w, y * w, w, w);
  }
  ctx.globalAlpha = 1; ctx.strokeStyle = joint; ctx.lineWidth = 3;
  for (let i = 0; i <= n; i++) { ctx.beginPath(); ctx.moveTo(i * w, 0); ctx.lineTo(i * w, s); ctx.moveTo(0, i * w); ctx.lineTo(s, i * w); ctx.stroke(); }
};
const withRepeat = (tex, x, y) => { const t = tex.clone(); t.repeat.set(x, y); t.needsUpdate = true; return t; };

function makeMaterials() {
  const plasterTex = canvasTexture(512, (c, s) => speckle(c, s, '#efebe4', ['#d8d1c4', '#ffffff', '#c9c1b2'], 5000, 5));
  const concreteTex = canvasTexture(512, (c, s) => speckle(c, s, '#bdb7ad', ['#a59e92', '#d6d0c6', '#8f897f'], 6000, 6));
  const woodV = canvasTexture(512, (c, s) => planks(c, s, 10, ['#8c5a36', '#9a6640', '#7d4f2f', '#a87148'], true));
  const woodH = canvasTexture(512, (c, s) => planks(c, s, 10, ['#8f6040', '#a06c47', '#7f5434', '#ad7650'], false));
  const grassTex = canvasTexture(512, (c, s) => speckle(c, s, '#4f7a3a', ['#3e6a2c', '#6b9449', '#5c8540', '#2f5a24'], 14000, 3));
  const paverTex = canvasTexture(512, (c, s) => tiles(c, s, 4, '#d9d3c6', '#aaa294', .06));
  const poolTex = canvasTexture(256, (c, s) => tiles(c, s, 8, '#2a8db5', '#7fc4de', .08));

  const std = (o) => new THREE.MeshStandardMaterial({ roughness: .8, metalness: 0, ...o });
  return {
    plaster: std({ map: plasterTex, roughness: .92 }),
    concrete: std({ map: concreteTex, roughness: .95 }),
    wood: std({ map: woodV, roughness: .62 }),
    deck: std({ map: withRepeat(woodH, 3, 1), roughness: .7 }),
    paver: std({ map: withRepeat(paverTex, 3, 1), roughness: .9 }),
    paverSq: std({ map: paverTex, roughness: .9 }),
    grass: std({ map: withRepeat(grassTex, 10, 10), roughness: 1 }),
    soil: std({ color: 0x1a2733, roughness: 1 }),
    frame: std({ color: 0x1d2226, metalness: .7, roughness: .35 }),
    interior: std({ color: 0x5b4636, emissive: 0xffb064, emissiveIntensity: .12, roughness: .9 }),
    sofa: std({ color: 0xcfc6b8, roughness: 1 }),
    rug: std({ color: 0x8a7a68, roughness: 1 }),
    lightStrip: new THREE.MeshStandardMaterial({ color: 0xfff1d6, emissive: 0xffc27a, emissiveIntensity: 2.2 }),
    lamp: new THREE.MeshStandardMaterial({ color: 0xfff1d6, emissive: 0xffb050, emissiveIntensity: 3 }),
    glass: new THREE.MeshPhysicalMaterial({ color: 0xe6f0f5, metalness: 0, roughness: .04, transmission: .92, thickness: .05, ior: 1.5, envMapIntensity: 1.4 }),
    water: new THREE.MeshPhysicalMaterial({ color: 0x2387b0, map: withRepeat(poolTex, 4, 1.3), roughness: .06, metalness: .05, clearcoat: 1, clearcoatRoughness: .05, envMapIntensity: 1.6 }),
    bark: std({ color: 0x5a4433, roughness: 1 }),
    leaves: [0x3f6b34, 0x4d7c3c, 0x5b8a45, 0x35602d].map(c => std({ color: c, roughness: .85, flatShading: true })),
    ring: new THREE.MeshBasicMaterial({ color: 0xf0a30a, transparent: true, opacity: .6, side: THREE.DoubleSide }),
  };
}

/* ---------- The villa ---------- */
function buildVilla(M) {
  const villa = new THREE.Group();
  const box = (w, h, d, m, x, y, z, cast = true) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m);
    mesh.position.set(x, y, z);
    mesh.castShadow = cast; mesh.receiveShadow = true;
    villa.add(mesh);
    return mesh;
  };

  // Plinth
  box(12.8, .3, 8.8, M.concrete, -1, .15, 0);

  // Ground floor: solid wing (wood-clad front) + glazed living room
  box(5, 3, 8, M.plaster, -4.5, 1.8, 0);
  box(5, 3, .08, M.wood, -4.5, 1.8, 4.04);
  box(.09, .09, .14, M.lamp, -6.3, 2.6, 4.12, false);
  box(.09, .09, .14, M.lamp, -2.7, 2.6, 4.12, false);
  box(7, 3, .3, M.plaster, 1.5, 1.8, -3.85);                      // back wall
  box(7, .05, 7.4, M.interior, 1.5, .33, -.3, false);              // floor
  box(.3, 3, 7.4, M.interior, -1.85, 1.8, -.3, false);             // inner wall
  box(6.4, .05, 7, M.interior, 1.5, 3.27, -.3, false);             // ceiling
  box(5.5, .04, .25, M.lightStrip, 1.5, 3.22, 2.4, false);         // cove light
  box(3.2, .45, 1, M.sofa, 1.2, .55, 1.2);                         // sofa
  box(3.2, .4, .25, M.sofa, 1.2, .9, .8);
  box(4, .02, 2.6, M.rug, 1.5, .36, 1.8, false);
  box(7, 3, .04, M.glass, 1.5, 1.8, 3.55, false);                  // front glazing
  box(.04, 3, 7.4, M.glass, 5, 1.8, -.3, false);                   // side glazing
  for (const x of [-2, -.25, 1.5, 3.25, 5]) box(.07, 3, .1, M.frame, x, 1.8, 3.58, false);
  for (const y of [.34, 3.26]) box(7, .08, .1, M.frame, 1.5, y, 3.58, false);
  for (const z of [-4, -1.5, 1, 3.55]) box(.1, 3, .07, M.frame, 5.02, 1.8, z, false);

  // First-floor slab doubling as a canopy over the deck
  box(12.9, .35, 8.9, M.plaster, -.85, 3.475, .15);

  // First floor: cantilevered box with a recessed ribbon window and timber louvres
  box(13, 2.9, 6.2, M.plaster, 1.5, 5.1, -.5);                     // main mass (z -3.6..2.6)
  box(13, .65, .8, M.plaster, 1.5, 3.975, 3);                      // sill band
  box(13, .65, .8, M.plaster, 1.5, 6.225, 3);                      // head band
  box(1, 1.6, .8, M.plaster, -4.5, 5.1, 3);                        // left return
  box(2, 1.6, .8, M.plaster, 7, 5.1, 3);                           // right return
  box(2, 2.9, .06, M.wood, 7, 5.1, 3.43);                          // timber-clad end
  box(10, 1.6, .05, M.interior, 1, 5.1, 2.62, false);              // interior behind glass
  box(9, .04, .2, M.lightStrip, 1, 5.85, 2.75, false);
  box(10, 1.6, .04, M.glass, 1, 5.1, 3.3, false);
  for (let x = -4; x <= 6.01; x += 2) box(.06, 1.6, .08, M.frame, x, 5.1, 3.32, false);
  for (let x = 2.2; x <= 5.8; x += .3) box(.06, 1.6, .22, M.wood, x, 5.1, 3.5);
  // cantilever underside soffit in timber
  box(3, .04, 6.2, M.wood, 6.5, 3.63, -.5, false);

  // Roof slab with a thin overhang
  box(13.6, .35, 7.8, M.plaster, 1.5, 6.725, -.1);

  // Terrace on the ground-floor roof with frameless glass railing
  box(2.3, 1, .03, M.glass, -6.15, 4.15, 4.55, false);
  box(.03, 1, 8.8, M.glass, -7.27, 4.15, .15, false);

  // Deck, pool and coping
  box(13, .2, 2.4, M.deck, 1.5, .1, 5.6);
  box(13, .2, .8, M.paver, 1.5, .1, 11);
  box(13, .2, .6, M.paver, 1.5, .1, 7.1);
  box(2, .2, 3.2, M.paverSq, -4, .1, 9);
  box(.5, .2, 3.2, M.paverSq, 7.75, .1, 9);
  box(10.5, .04, 3.2, M.water, 2.25, .12, 9, false);
  // stepping stones to the garden
  for (let i = 0; i < 4; i++) box(.9, .08, .6, M.paverSq, -6.2 + i * .15, .04, 5.2 + i * 1.3);

  // Precast compound wall (a Manidhay service) along the back of the plot
  for (let x = -9; x <= 11; x += 2.5) {
    box(.28, 2, .28, M.concrete, x, 1, -7.5);
    if (x < 11) {
      box(2.22, 1.7, .12, M.concrete, x + 1.25, .95, -7.5);
    }
  }

  // Trees and shrubs: blobby, noise-displaced foliage for a natural silhouette
  const blob = (r, detail = 2) => {
    const g = new THREE.IcosahedronGeometry(r, detail);
    const p = g.attributes.position, v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) {
      v.fromBufferAttribute(p, i);
      const n = Math.sin(v.x * 2.3) + Math.sin(v.y * 2.9 + 1.3) + Math.sin(v.z * 2.1 + 2.1);
      v.multiplyScalar(1 + n * .07);
      p.setXYZ(i, v.x, v.y, v.z);
    }
    g.computeVertexNormals();
    return g;
  };
  const tree = (x, z, h) => {
    const g = new THREE.Group();
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(.09 * h / 5, .16 * h / 5, h * .55, 8), M.bark);
    trunk.position.y = h * .275; trunk.castShadow = true;
    g.add(trunk);
    for (let k = 0; k < 5; k++) {
      const r = h * (.16 + rand() * .08);
      const leaf = new THREE.Mesh(blob(r), M.leaves[Math.floor(rand() * M.leaves.length)]);
      const a = rand() * Math.PI * 2, d = k ? h * .14 : 0;
      leaf.position.set(Math.cos(a) * d, h * (.62 + rand() * .2), Math.sin(a) * d);
      leaf.castShadow = leaf.receiveShadow = true;
      g.add(leaf);
    }
    g.position.set(x, 0, z);
    g.rotation.y = rand() * 6;
    villa.add(g);
  };
  for (const [x, z, h] of [[-10, -4.5, 6.5], [-9.6, 2.2, 5], [9.8, -5.6, 7], [11, 1.5, 5.5], [-6, -6.2, 5.5], [3.5, -6.3, 6], [12.3, -2.4, 4.5], [-9, 8, 4.2], [10.5, 7.5, 4.8]]) tree(x, z, h);
  const shrub = (x, z, r) => {
    const s = new THREE.Mesh(blob(r, 1), M.leaves[Math.floor(rand() * M.leaves.length)]);
    s.position.set(x, r * .55, z); s.scale.y = .7; s.castShadow = s.receiveShadow = true;
    villa.add(s);
  };
  for (const [x, z, r] of [[-8.2, -1, .7], [-8.4, .6, .55], [-8, 3.4, .65], [-5, 7.3, .5], [8.8, 7.1, .6], [8.6, 10.6, .5], [-5.6, 11.4, .55], [6.2, -4.8, .6]]) shrub(x, z, r);

  villa.position.set(-1, 0, -2.2); // centre the composition on the base
  return villa;
}

/* ---------- Scene ---------- */
async function createScene(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = .95;
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture; // until the sky loads
  new RGBELoader().load(HDRI, hdr => {
    scene.environment = pmrem.fromEquirectangular(hdr).texture;
    hdr.dispose();
  });

  scene.add(new THREE.HemisphereLight(0xdbe8f5, 0x2b3a2a, .35));
  const sun = new THREE.DirectionalLight(0xffe7c4, 2.4);
  sun.position.set(16, 22, 14);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -19, right: 19, top: 19, bottom: -19, near: 1, far: 80 });
  sun.shadow.bias = -.0003;
  sun.shadow.normalBias = .03;
  sun.shadow.radius = 4;
  scene.add(sun);

  const M = makeMaterials();
  const root = new THREE.Group();
  scene.add(root);

  // Round lawn base with an amber ring
  const base = new THREE.Mesh(new THREE.CylinderGeometry(15.5, 15.9, .8, 128), [M.soil, M.grass, M.soil]);
  base.position.y = -.4; base.receiveShadow = true;
  const ring = new THREE.Mesh(new THREE.RingGeometry(15.95, 16.1, 160), M.ring);
  ring.rotation.x = -Math.PI / 2; ring.position.y = -.79;
  root.add(base, ring);

  if (canvas.dataset.model) {
    const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
    const gltf = await new GLTFLoader().loadAsync(canvas.dataset.model);
    const model = gltf.scene;
    const bounds = new THREE.Box3().setFromObject(model);
    const size = bounds.getSize(new THREE.Vector3());
    const scale = 24 / Math.max(size.x, size.z);
    model.scale.setScalar(scale);
    bounds.setFromObject(model);
    model.position.sub(bounds.getCenter(new THREE.Vector3())).setY(-bounds.min.y);
    model.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; });
    root.add(model);
  } else {
    root.add(buildVilla(M));
  }

  const camera = new THREE.PerspectiveCamera(28, 1, .1, 300);
  const target = new THREE.Vector3(0, 2.2, 0);
  const resize = () => {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    // distance that fits a sphere around the whole base, whichever way the canvas is shaped
    const halfV = THREE.MathUtils.degToRad(camera.fov / 2);
    const halfH = Math.atan(Math.tan(halfV) * camera.aspect);
    camera.userData.r = 15.5 / Math.sin(Math.min(halfV, halfH));
  };
  new ResizeObserver(resize).observe(canvas);
  resize();

  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  addEventListener('pointermove', e => {
    mouse.tx = e.clientX / innerWidth * 2 - 1;
    mouse.ty = e.clientY / innerHeight * 2 - 1;
  }, { passive: true });

  const clock = new THREE.Clock();
  let spin = 0;
  const frame = () => {
    const dt = Math.min(clock.getDelta(), .05);
    if (!reduceMotion) spin += dt * .07;
    mouse.x += (mouse.tx - mouse.x) * .04;
    mouse.y += (mouse.ty - mouse.y) * .04;
    const angle = .55 + Math.sin(spin) * .55 + mouse.x * .18;   // gentle sway, mostly front-facing
    const elev = .36 - mouse.y * .05;
    const r = camera.userData.r;
    camera.position.set(Math.sin(angle) * Math.cos(elev) * r, target.y + Math.sin(elev) * r, Math.cos(angle) * Math.cos(elev) * r);
    camera.lookAt(target);
    renderer.render(scene, camera);
  };

  // Only render while on screen
  let raf = 0, onScreen = false;
  const loop = () => { if (!onScreen) { raf = 0; return; } frame(); raf = requestAnimationFrame(loop); };
  new IntersectionObserver(([e]) => {
    onScreen = e.isIntersecting;
    if (onScreen && !raf) { clock.getDelta(); loop(); }
  }).observe(canvas);
  frame();
}

for (const canvas of document.querySelectorAll('canvas[data-scene]')) {
  createScene(canvas)
    .then(() => canvas.closest('[data-3d]')?.classList.add('is-3d'))
    .catch(err => console.warn('3D scene unavailable, showing fallback', err));
}
