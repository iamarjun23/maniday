# Builds the hero house and exports models/house.glb.
# Run: blender -b -P models/house.py -- models/house.glb <texture-scratch-dir>
# Blender Z-up, front of the house faces -Y (the glTF exporter turns that into three.js +Z).
import bpy, bmesh, math, random, sys, os
import numpy as np
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = os.path.abspath(argv[0] if argv else os.path.join(os.path.dirname(__file__), 'house.glb'))
TMP = os.path.abspath(argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(OUT), '_tex'))
os.makedirs(TMP, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
rng = np.random.default_rng(7)
random.seed(7)

# ------------------------------------------------------------------ textures (tileable, made with numpy)
def vnoise(n, cx, cy=None):
    cy = cy or cx
    g = rng.random((cy, cx)).astype(np.float32)
    def ax(c):
        t = np.arange(n) * c / n
        i0 = np.floor(t).astype(int); f = t - i0
        return i0, (i0 + 1) % c, f * f * (3 - 2 * f)
    x0, x1, fx = ax(cx); y0, y1, fy = ax(cy)
    fx = fx[None, :]; fy = fy[:, None]
    a = g[y0][:, x0]; b = g[y0][:, x1]; c = g[y1][:, x0]; d = g[y1][:, x1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

def fbm(n, c, octs=4):
    s = np.zeros((n, n), np.float32); amp = 1; tot = 0
    for o in range(octs):
        cc = min(n, c * 2 ** o)
        s += vnoise(n, cc) * amp; tot += amp; amp *= .5
    return s / tot

def lerp(c0, c1, t):
    t = np.clip(t, 0, 1)[..., None]
    return np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t

def normal_from(h, s):
    dx = np.roll(h, -1, 1) - np.roll(h, 1, 1)
    dy = np.roll(h, -1, 0) - np.roll(h, 1, 0)
    nrm = np.stack([-dx * s, -dy * s, np.ones_like(h)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    return nrm * .5 + .5

def image(name, rgb, data=False):
    n = rgb.shape[0]
    a = np.ones((n, n, 4), np.float32); a[..., :3] = np.clip(rgb, 0, 1)
    img = bpy.data.images.new(name, n, n)
    img.pixels.foreach_set(a.ravel())
    img.filepath_raw = os.path.join(TMP, name + '.png'); img.file_format = 'PNG'; img.save()
    if data: img.colorspace_settings.name = 'Non-Color'
    return img

N = 1024
X = np.broadcast_to((np.arange(N) / N)[None, :], (N, N))
Y = np.broadcast_to((np.arange(N) / N)[:, None], (N, N))

def tex_plaster():
    t = .55 * fbm(N, 6, 4) + .45 * vnoise(N, 256)
    streak = vnoise(N, 96, 3)                       # faint vertical rain streaks
    rgb = lerp((.76, .74, .7), (.87, .86, .83), t) * (1 - .06 * streak)[..., None]
    return image('plaster', rgb)

def tex_terrace():
    tx = X * 8; ty = Y * 8
    joint = ((tx % 1) < .03) | ((ty % 1) < .03)
    tone = rng.uniform(.9, 1.07, (8, 8))[ty.astype(int) % 8, tx.astype(int) % 8]
    t = fbm(N, 8, 5)
    rgb = lerp((.5, .48, .45), (.66, .64, .6), t) * tone[..., None]
    rgb[joint] = (.36, .35, .33)
    return image('terrace', rgb), image('terrace_n', normal_from(.15 * t - joint, 2.0), True)

def tex_concrete():
    t = fbm(N, 6, 5)
    pits = (vnoise(N, 256) > .9).astype(np.float32) * .08
    return image('concrete', lerp((.55, .54, .51), (.7, .69, .66), t) - pits[..., None])

def tex_wood(name, light, dark):
    warp = fbm(N, 3, 3)
    fib = vnoise(N, 256, 8)
    ring = .5 + .5 * np.sin(2 * np.pi * (X * 26 + warp * 3))
    t = .55 * ring + .45 * fib
    board = np.minimum((X * 4).astype(int), 3)
    seam = (np.arange(N)[None, :] % (N // 4) < 2) & np.ones((N, 1), bool)
    rgb = lerp(dark, light, t) * (0.92 + rng.random(4)[board][..., None] * .14)
    rgb[seam] *= .4
    h = t * .25 - seam * 1.0
    return image(name, rgb), image(name + '_n', normal_from(h, 2.0), True)

def tex_stone():
    n = 1024
    rgb = np.zeros((n, n, 3), np.float32); h = np.zeros((n, n), np.float32)
    pal = np.array([(.62, .6, .56), (.53, .5, .46), (.7, .66, .6), (.48, .45, .41), (.66, .6, .52), (.58, .55, .5)], np.float32)
    noise = fbm(n, 16, 4); g = 5
    y = 0
    while y < n:
        rh = int(rng.integers(90, 170)); rh = n - y if n - y < 150 else rh
        off = int(rng.integers(0, n)); col = (np.arange(n) - off) % n
        widths = []
        while sum(widths) < n: widths.append(int(rng.integers(120, 340)))
        edges = np.minimum(np.cumsum(widths), n); starts = np.concatenate([[0], edges[:-1]])
        idx = np.searchsorted(edges, col, side='right'); idx = np.minimum(idx, len(widths) - 1)
        local = col - starts[idx]
        colors = pal[rng.integers(0, len(pal), len(widths))] * rng.uniform(.9, 1.1, (len(widths), 1))
        band = slice(y, y + rh)
        rgb[band] = colors[idx][None, :, :]
        grout = (local < g)[None, :] | (np.arange(rh) < g)[:, None]
        hh = np.where(grout, 0, 1.0)
        rgb[band][grout] = (.36, .34, .31)
        h[band] = hh
        y += rh
    rgb *= (.82 + .36 * noise)[..., None]
    h = h + .35 * noise
    return image('stone', rgb), image('stone_n', normal_from(h, 3.0), True)

def tex_paving():
    tx = X * 4; ty = Y * 4
    jx = (tx % 1) < .014; jy = (ty % 1) < .014
    joint = jx | jy
    tone = rng.uniform(.9, 1.08, (4, 4))[ty.astype(int) % 4, tx.astype(int) % 4]
    t = fbm(N, 8, 4)
    rgb = lerp((.56, .54, .5), (.68, .66, .62), t) * tone[..., None]
    rgb[joint] = (.3, .29, .27)
    h = .2 * t - joint
    return image('paving', rgb), image('paving_n', normal_from(h, 2.0), True)

def tex_grass():
    base = fbm(N, 6, 5); fine = vnoise(N, 256); blade = vnoise(N, 512, 96)
    t = .4 * base + .35 * fine + .25 * blade
    rgb = lerp((.09, .15, .05), (.22, .29, .11), t)
    dry = np.clip((fbm(N, 3, 3) - .58) * 4, 0, 1) * .5
    rgb = rgb * (1 - dry[..., None]) + np.array((.42, .42, .2), np.float32) * dry[..., None]
    return image('grass', rgb), image('grass_n', normal_from(fine * .6 + blade * .4, 2.5), True)

def tex_soil():
    t = .5 + .5 * np.sin(2 * np.pi * (Y * 7 + fbm(N, 4, 3) * 1.6))
    return image('soil', lerp((.3, .22, .15), (.45, .34, .24), .6 * t + .4 * vnoise(N, 128)))

def tex_leaf():
    t = .5 * fbm(N, 8, 4) + .5 * vnoise(N, 160)
    return image('leaf', lerp((.04, .09, .02), (.13, .2, .06), t))

def tex_trunk():
    ring = (np.sin(2 * np.pi * (Y * 9 + vnoise(N, 6, 2) * .4)) > .55).astype(np.float32)
    t = .5 * fbm(N, 16, 4) + .5 * vnoise(N, 256, 32)
    rgb = lerp((.27, .23, .19), (.47, .42, .36), t) * (1 - .35 * ring)[..., None]
    return image('trunk', rgb), image('trunk_n', normal_from(t * .3 - ring * .8, 3.0), True)

def tex_solar():
    cx = (X * 6) % 1; cy = (Y * 6) % 1
    line = (cx < .03) | (cy < .03)
    rgb = lerp((.04, .07, .16), (.08, .13, .26), fbm(N, 4, 3))
    rgb[line] = (.55, .58, .62)
    return image('solar', rgb)

# ------------------------------------------------------------------ materials
def inp(node, *names):
    for n in names:
        if n in node.inputs: return node.inputs[n]

MATS, UVS = {}, {}
def mat(name, color=(1, 1, 1), rough=.8, metal=0., tex=None, nrm=None, nrm_k=1., alpha=1., emit=None, ds=False, uv=1.):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes.get('Principled BSDF')
    inp(p, 'Base Color').default_value = (*color, 1)
    inp(p, 'Roughness').default_value = rough
    inp(p, 'Metallic').default_value = metal
    if tex:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = tex
        nt.links.new(t.outputs['Color'], inp(p, 'Base Color'))
    if nrm:
        t2 = nt.nodes.new('ShaderNodeTexImage'); t2.image = nrm
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nrm_k
        nt.links.new(t2.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], inp(p, 'Normal'))
    if alpha < 1:
        inp(p, 'Alpha').default_value = alpha
        for k, v in (('blend_method', 'BLEND'), ('surface_render_method', 'BLENDED')):
            try: setattr(m, k, v)
            except Exception: pass
    if emit:
        inp(p, 'Emission Color', 'Emission').default_value = (*emit, 1)
        s = inp(p, 'Emission Strength')
        if s: s.default_value = 6
    m.use_backface_culling = not ds
    MATS[name] = m; UVS[name] = uv
    return m

mat('plaster', tex=tex_plaster(), rough=.92, uv=3)
mat('concrete', tex=tex_concrete(), rough=.88, uv=3)
w, wn = tex_wood('wood', (.74, .52, .32), (.5, .32, .18)); mat('wood', tex=w, nrm=wn, rough=.55, uv=1.4)
w, wn = tex_wood('wood_dark', (.42, .27, .16), (.24, .14, .08)); mat('wood_dark', tex=w, nrm=wn, rough=.5, uv=1.4)
s, sn = tex_stone(); mat('stone', tex=s, nrm=sn, rough=.85, uv=2.4)
s, sn = tex_paving(); mat('paving', tex=s, nrm=sn, rough=.8, uv=2.4)
s, sn = tex_grass(); mat('grass', tex=s, nrm=sn, rough=.95, uv=4)
mat('soil', tex=tex_soil(), rough=.95, uv=2)
mat('leaf', tex=tex_leaf(), rough=.8, uv=1.5)
mat('solar', tex=tex_solar(), rough=.2, metal=.3, uv=1)
mat('metal', (.08, .08, .09), rough=.35, metal=.7)
mat('glass', (.72, .82, .86), rough=.03, alpha=.28)
mat('fabric', (.8, .74, .66), rough=1)
mat('fabric2', (.62, .4, .3), rough=1)
mat('rug', (.76, .7, .6), rough=1)
mat('white', (.93, .92, .89), rough=.6)
mat('dark', (.13, .12, .11), rough=.5)
mat('lamp', (1, .92, .8), rough=.5, emit=(1, .78, .5))
s_, sn_ = tex_terrace(); mat('terrace', tex=s_, nrm=sn_, rough=.85, uv=2.4)
mat('pvc', (.42, .42, .4), rough=.5)
mat('ac', (.82, .82, .8), rough=.45)
mat('curtain', (.9, .87, .82), rough=1)
mat('carpaint', (.42, .03, .03), rough=.3, metal=.5)
mat('carglass', (.02, .03, .04), rough=.05, metal=.3)
mat('carplastic', (.04, .04, .045), rough=.6)
mat('tyre', (.03, .03, .03), rough=.9)
mat('alloy', (.72, .73, .75), rough=.25, metal=.9)
mat('headlight', (.9, .93, .95), rough=.1, emit=(.9, .95, 1))
mat('taillight', (.5, .02, .02), rough=.2, emit=(.8, .02, .01))
mat('palm', (.1, .19, .05), rough=.75, ds=True)
mat('foliage', (.22, .34, .1), rough=.8, ds=True)
s, sn = tex_trunk(); mat('trunk', tex=s, nrm=sn, rough=.95, uv=.9)
mat('palm_dry', (.42, .33, .18), rough=.85, ds=True)
mat('bark', (.27, .2, .14), rough=.95)
mat('tank', (.05, .05, .06), rough=.55)
mat('pot', (.62, .33, .2), rough=.9)
mat('coconut', (.36, .32, .13), rough=.8)

# ------------------------------------------------------------------ geometry accumulators: one object per (group, material)
ACC, GROUPS, LIGHTS, NRM = {}, {}, [], {}
def group(name, origin=(0, 0, 0)): GROUPS[name] = Vector(origin); return name

def emit(bm, g, m, M=None, smooth=None):
    bm.normal_update()
    flags = [bool(smooth(f)) if smooth else False for f in bm.faces]
    if M is not None: bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    V, F, S = ACC.setdefault((g, m), ([], [], []))
    bm.verts.index_update(); off = len(V)
    V.extend(v.co.copy() for v in bm.verts)
    for f, s in zip(bm.faces, flags): F.append(tuple(off + v.index for v in f.verts)); S.append(s)
    bm.free()

def bevel(bm, b):
    if b > .001:
        bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=b, segments=2, profile=.5, affect='EDGES', clamp_overlap=True)

def box(g, m, x0, y0, z0, x1, y1, z1, bev=.015, M=None):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector(((v.co.x + .5) * (x1 - x0) + x0, (v.co.y + .5) * (y1 - y0) + y0, (v.co.z + .5) * (z1 - z0) + z0))
    bevel(bm, min(bev, .4 * min(x1 - x0, y1 - y0, z1 - z0)))
    emit(bm, g, m, M)

def cone(bm, seg, r1, r2, h):
    try: bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h)
    except TypeError: bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, diameter1=r1, diameter2=r2, depth=h)

def cyl(g, m, base, r, h, seg=24, r2=None, rot=None, bev=0):
    bm = bmesh.new(); cone(bm, seg, r, r if r2 is None else r2, h)
    bmesh.ops.translate(bm, vec=Vector((0, 0, h / 2)), verts=bm.verts)
    bevel(bm, bev)
    M = Matrix.Translation(Vector(base)) @ (rot or Matrix.Identity(4))
    emit(bm, g, m, M, smooth=lambda f: abs(f.normal.z) < .7)

def blob(g, m, c, r, sub=3, jit=.16, squash=1.):
    bm = bmesh.new()
    try: bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    except TypeError: bmesh.ops.create_icosphere(bm, subdivisions=sub, diameter=r)
    a, b, cc = (random.uniform(0, 6) for _ in range(3))
    for v in bm.verts:
        n = v.co.normalized()
        k = 1 + jit * math.sin(3.1 * n.x + a) * math.sin(2.7 * n.y + b) * math.sin(3.3 * n.z + cc) * 2 + random.uniform(-.04, .04)
        v.co = Vector((n.x * r * k, n.y * r * k, n.z * r * k * squash))
    emit(bm, g, m, Matrix.Translation(Vector(c)), smooth=lambda f: True)

def raw(g, m, verts, faces, smooth=False, normals=None):
    """normals: optional per-vertex custom normals (foliage shades as one rounded canopy)."""
    V, F, S = ACC.setdefault((g, m), ([], [], []))
    if normals is not None:
        nl = NRM.setdefault((g, m), [])
        nl.extend([(0, 0, 1)] * (len(V) - len(nl))); nl.extend(tuple(n) for n in normals)
    off = len(V); V.extend(Vector(v) for v in verts)
    for f in faces: F.append(tuple(off + i for i in f)); S.append(smooth)

def bush(g, c, r, squash=1.):
    """Leaf clusters: a dark core plus cards that three.js textures with alpha-cut leaves."""
    blob(g, 'leaf', c, r * .66, 2, .15, squash)
    c = Vector(c); verts, faces, nrm = [], [], []
    for _ in range(max(18, int(190 * r * r))):
        d = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1) + .35)).normalized()
        p = c + Vector((d.x * r, d.y * r, d.z * r * squash)) * random.uniform(.72, 1.06)
        n = (d + Vector((random.gauss(0, .5), random.gauss(0, .5), random.gauss(0, .5)))).normalized()
        u = n.cross(Vector((0, 0, 1)))
        u = u.normalized() if u.length > 1e-3 else Vector((1, 0, 0))
        v = n.cross(u); a = random.uniform(0, 6.28)
        u, v = u * math.cos(a) + v * math.sin(a), v * math.cos(a) - u * math.sin(a)
        s = max(.12, r * random.uniform(.24, .36))
        o = len(verts); verts += [p - u * s - v * s, p + u * s - v * s, p + u * s + v * s, p - u * s + v * s]
        faces.append((o, o + 1, o + 2, o + 3))
        for q in verts[-4:]:
            w = q - c; nrm.append(Vector((w.x, w.y, w.z / squash + .35 * r)).normalized())
    raw(g, 'foliage', verts, faces, True, nrm)

def light(name, x, y, z, kind='in'): LIGHTS.append((f'L_{kind}_{name}', (x, y, z)))

# ------------------------------------------------------------------ helpers for walls and glazing
def wall_x(g, m, y0, y1, x0, x1, z0, z1, holes=()):
    """Wall running along X with rectangular holes (hx0, hx1, hz0, hz1)."""
    xs = sorted({x0, x1, *[min(max(h[0], x0), x1) for h in holes], *[min(max(h[1], x0), x1) for h in holes]})
    for a, b in zip(xs, xs[1:]):
        if b - a < 1e-4: continue
        hit = [h for h in holes if h[0] <= a + 1e-4 and h[1] >= b - 1e-4]
        if not hit: box(g, m, a, y0, z0, b, y1, z1); continue
        h = hit[0]
        if h[2] > z0 + 1e-4: box(g, m, a, y0, z0, b, y1, h[2])
        if h[3] < z1 - 1e-4: box(g, m, a, y0, h[3], b, y1, z1)

def wall_y(g, m, x0, x1, y0, y1, z0, z1, holes=()):
    ys = sorted({y0, y1, *[min(max(h[0], y0), y1) for h in holes], *[min(max(h[1], y0), y1) for h in holes]})
    for a, b in zip(ys, ys[1:]):
        if b - a < 1e-4: continue
        hit = [h for h in holes if h[0] <= a + 1e-4 and h[1] >= b - 1e-4]
        if not hit: box(g, m, x0, a, z0, x1, b, z1); continue
        h = hit[0]
        if h[2] > z0 + 1e-4: box(g, m, x0, a, z0, x1, b, h[2])
        if h[3] < z1 - 1e-4: box(g, m, x0, a, h[3], x1, b, z1)

def glazing(g, axis, c, a0, a1, z0, z1, n=1, transom=None, sill=True):
    """Aluminium-framed glass in an opening. axis 'x': opening runs along X at y=c; 'y': along Y at x=c."""
    f, d = .06, .05
    def bar(a, b, za, zb):
        if axis == 'x': box(g, 'metal', a, c - d, za, b, c + d, zb, .006)
        else: box(g, 'metal', c - d, a, za, c + d, b, zb, .006)
    bar(a0, a1, z0, z0 + f); bar(a0, a1, z1 - f, z1)
    bar(a0, a0 + f, z0, z1); bar(a1 - f, a1, z0, z1)
    for i in range(1, n):
        a = a0 + (a1 - a0) * i / n; bar(a - f / 2, a + f / 2, z0, z1)
    if transom: bar(a0, a1, transom - f / 2, transom + f / 2)
    if axis == 'x': box(g, 'glass', a0, c - .01, z0, a1, c + .01, z1, 0)
    else: box(g, 'glass', c - .01, a0, z0, c + .01, a1, z1, 0)
    if sill and z0 > .6:
        if axis == 'x': box(g, 'concrete', a0 - .05, c - .2, z0 - .06, a1 + .05, c + .02, z0, .01)

# ------------------------------------------------------------------ the house
P, S0, S1 = .45, 3.65, 3.95          # plinth top, ground slab underside / top
F0, R0, R1 = S1, 7.05, 7.33          # first floor level, roof underside / top
T = .25

# --- site: diorama base, plinth, steps, driveway, compound wall, gate, shrubs
site = group('site')
box(site, 'soil', -13, -10, -1.0, 13, 10, -.03, .04)
box(site, 'grass', -13, -10, -.03, 13, 10, 0, .02)
box(site, 'concrete', -6.6, -5.3, 0, 6.6, 5.1, P - .04, .02)
box(site, 'paving', -6.6, -5.3, P - .04, 6.6, 5.1, P, .01)
for i, (y0, h) in enumerate(((-6.2, .15), (-5.9, .30))):
    box(site, 'paving', 1.6, y0, 0, 4.4, -5.3, h, .01)
box(site, 'paving', .3, -9.7, 0, 7.6, -6.2, .025, .005)
box(site, 'paving', 4.4, -6.2, 0, 7.6, -5.3, .025, .005)
for k in range(5):  # stepping stones to the side lawn
    box(site, 'paving', -1.0 - k * 1.1, -7.0 + k * .35, 0, -.4 - k * 1.1, -6.4 + k * .35, .03, .01)

def wall_run(axis, fixed, a0, a1, h, gap=None):
    """Readymade precast compound wall: I-section posts with stacked slabs between them."""
    n = max(1, round((a1 - a0) / 2.5)); pos = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
    for p in pos:
        if gap and gap[0] + .05 < p < gap[1] - .05: continue
        if axis == 'x': box(site, 'concrete', p - .09, fixed - .09, 0, p + .09, fixed + .09, h + .08, .01)
        else: box(site, 'concrete', fixed - .09, p - .09, 0, fixed + .09, p + .09, h + .08, .01)
    for a, b in zip(pos, pos[1:]):
        if gap and a >= gap[0] - .05 and b <= gap[1] + .05: continue
        for k in range(3):
            za, zb = .02 + k * h / 3, (k + 1) * h / 3 - .01
            if axis == 'x': box(site, 'concrete', a + .09, fixed - .04, za, b - .09, fixed + .04, zb, .008)
            else: box(site, 'concrete', fixed - .04, a + .09, za, fixed + .04, b - .09, zb, .008)

wall_run('x', -9.75, -12.75, 12.75, 1.15, gap=(-.05, 7.7))
wall_run('x', 9.75, -12.75, 12.75, 1.5)
wall_run('y', -12.75, -9.75, 9.75, 1.5)
wall_run('y', 12.75, -9.75, 9.75, 1.5)
# sliding gate
gx0, gx1 = .12, 3.8   # sliding gate, pushed open
box(site, 'metal', gx0, -9.79, .08, gx1, -9.71, .14, .005)
box(site, 'metal', gx0, -9.79, 1.12, gx1, -9.71, 1.18, .005)
x = gx0 + .06
while x < gx1 - .05:
    box(site, 'metal', x, -9.775, .14, x + .035, -9.725, 1.12, .004); x += .13
# bollard lights along the drive
for bx in (0, 7.9):
    for by in (-8.6, -7.0):
        box(site, 'dark', bx - .07, by - .07, 0, bx + .07, by + .07, .55, .01)
        box(site, 'lamp', bx - .065, by - .065, .42, bx + .065, by + .065, .52, .005)
        light(f'b{bx}{by}', bx, by, .6, 'out')
# shrubs: along the plinth and inside the front wall
for i in range(10):
    bush(site, (-6.2 + i * .78, -5.8, .3), .42 + random.uniform(-.06, .08), .8)
for xx in list(np.arange(-12, -.6, .85)) + list(np.arange(8.6, 12.2, .85)):
    bush(site, (xx + random.uniform(-.1, .1), -9.2, .4), .5 + random.uniform(-.05, .1), .85)
for yy in np.arange(-8.4, 9.2, .95):
    bush(site, (-12.15, yy + random.uniform(-.1, .1), .5), .55 + random.uniform(-.05, .1), .9)
    bush(site, (12.15, yy + random.uniform(-.1, .1), .5), .55 + random.uniform(-.05, .1), .9)

# --- ground floor
gf = group('ground')
# block A: living and dining, glass front
box(gf, 'plaster', -6, -4.5, P, -5.75, -4.25, S0)                                   # corner pier
wall_y(gf, 'plaster', -6, -5.75, -4.25, 4.5, P, S0, [(-1, 1.6, P + .6, S0 - .5)])
wall_x(gf, 'plaster', 4.25, 4.5, -5.75, 1.2, P, S0)
glazing(gf, 'x', -4.38, -5.75, 1.2, P, S0, n=5, transom=P + 2.55)
glazing(gf, 'y', -5.88, -1, 1.6, P + .6, S0 - .5, n=2)
# block B: entrance, stone feature wall
wall_y(gf, 'plaster', 1.2, 1.45, -4.5, 4.5, P, S0)
wall_x(gf, 'plaster', -3.6, -3.35, 1.45, 6, P, S0, [(2.05, 3.15, P, P + 2.45), (4.1, 5.6, P + 1.0, P + 2.3)])
wall_x(gf, 'stone', -3.67, -3.6, 3.4, 6.07, P, S0, [(4.1, 5.6, P + 1.0, P + 2.3)])
wall_y(gf, 'stone', 6, 6.07, -3.67, 4.5, P, S0, [(-1.5, 1.5, P + 1.0, P + 2.3)])
wall_y(gf, 'plaster', 5.75, 6, -3.35, 4.5, P, S0, [(-1.5, 1.5, P + 1.0, P + 2.3)])
wall_x(gf, 'plaster', 4.25, 4.5, 1.45, 5.75, P, S0, [(2.5, 4.5, P + 1.2, P + 2.2)])
glazing(gf, 'x', -3.48, 4.1, 5.6, P + 1.0, P + 2.3, n=2)
glazing(gf, 'y', 5.88, -1.5, 1.5, P + 1.0, P + 2.3, n=2)
glazing(gf, 'x', 4.38, 2.5, 4.5, P + 1.2, P + 2.2, n=2)
box(gf, 'wood_dark', 2.07, -3.52, P, 3.13, -3.44, P + 2.43, .01)                  # front door
box(gf, 'metal', 2.92, -3.6, P + .75, 2.96, -3.52, P + 1.65, .005)                   # pull handle
box(gf, 'metal', 2.0, -3.62, P, 2.05, -3.36, P + 2.5, .004); box(gf, 'metal', 3.15, -3.62, P, 3.2, -3.36, P + 2.5, .004)
box(gf, 'metal', 2.0, -3.62, P + 2.45, 3.2, -3.36, P + 2.5, .004)
box(gf, 'wood', 1.45, -3.66, P + .2, 1.95, -3.6, S0 - .2, .01)                       # wood panel beside the door
box(gf, 'wood', -5.75, -4.38, P, 1.2, 4.25, P + .03, .005)                           # floors
box(gf, 'wood', 1.45, -3.35, P, 5.75, 4.25, P + .03, .005)
# slab with deep front overhang over the porch, and an LED strip under its edge
box(gf, 'plaster', -6.25, -5.0, S0, 6.25, 4.75, S1, .025)
box(gf, 'plaster', -2.2, -5.6, S0, 6.25, -5.0, S1, .02)
box(gf, 'lamp', -6.2, -4.97, S0 - .025, 6.2, -4.92, S0, .004)
box(gf, 'wood', -6.25, -5.02, S0 - .02, 6.25, -5.0, S1 + .0, .002)                   # thin teak fascia

# --- first floor and terrace
ff = group('upper')
wall_x(ff, 'plaster', -5.6, -5.35, -2.2, 6.25, F0, R0, [(-1.95, 1.6, F0, R0), (2.6, 5.6, F0 + .9, F0 + 2.4)])
glazing(ff, 'x', -5.48, -1.95, 1.6, F0, R0, n=3, transom=F0 + 2.5)
glazing(ff, 'x', -5.48, 2.6, 5.6, F0 + .9, F0 + 2.4, n=2)
x = 1.75
while x < 6.2:  # vertical teak louvers
    box(ff, 'wood', x, -5.95, F0 + .04, x + .07, -5.65, R0 - .02, .008); x += .2
box(ff, 'wood', 1.7, -5.95, F0, 6.25, -5.65, F0 + .05, .005)
wall_y(ff, 'plaster', -2.2, -1.95, -5.6, 4.5, F0, R0, [(-4.2, 1.0, F0, F0 + 2.6)])
glazing(ff, 'y', -2.08, -4.2, 1.0, F0, F0 + 2.6, n=3)
wall_y(ff, 'plaster', 6.0, 6.25, -5.6, 4.5, F0, R0, [(-2.0, 1.5, F0 + .9, F0 + 2.3)])
glazing(ff, 'y', 6.13, -2.0, 1.5, F0 + .9, F0 + 2.3, n=2)
wall_x(ff, 'plaster', 4.25, 4.5, -2.2, 6.25, F0, R0, [(0, 3.2, F0 + 1.0, F0 + 2.3)])
glazing(ff, 'x', 4.38, 0, 3.2, F0 + 1.0, F0 + 2.3, n=2)
box(ff, 'plaster', 1.6, -5.35, F0, 1.75, 0, R0)                                      # bedroom | study
box(ff, 'plaster', -1.95, 0, F0, 1.75, .15, R0)
box(ff, 'wood', -1.95, -5.35, F0, 6.0, 4.25, F0 + .03, .005)
# terrace: deck, glass railing, pergola
box(ff, 'wood', -6.25, -5.0, F0, -2.2, 4.75, F0 + .05, .005)
for (x0, y0, x1, y1) in ((-6.2, -4.98, -2.2, -4.94), (-6.22, -4.94, -6.18, 4.72)):
    box(ff, 'glass', x0, y0, F0 + .14, x1, y1, F0 + 1.08, 0)
    box(ff, 'metal', x0 - .02, y0 - .02, F0 + .05, x1 + .02, y1 + .02, F0 + .15, .005)
    box(ff, 'metal', x0 - .015, y0 - .015, F0 + 1.07, x1 + .015, y1 + .015, F0 + 1.11, .005)
for py in (-4.75, -.9):
    box(ff, 'wood', -6.02, py - .07, F0 + .05, -5.88, py + .07, F0 + 2.75, .01)
box(ff, 'wood', -6.04, -4.86, F0 + 2.6, -5.86, -.79, F0 + 2.8, .01)
y = -4.8
while y < -.8:
    box(ff, 'wood', -6.15, y, F0 + 2.8, -2.2, y + .07, F0 + 2.92, .006); y += .3

# --- roof: thin overhanging slab, stair headroom, water tank, solar panels
rf = group('roof')
box(rf, 'plaster', -2.8, -6.3, R0, 6.85, 5.1, R1, .03)
box(rf, 'terrace', -2.65, -6.15, R1, 6.7, 4.95, R1 + .02, .004)
for (x0, y0, x1, y1) in ((-2.8, -6.3, 6.85, -6.15), (-2.8, 4.95, 6.85, 5.1), (-2.8, -6.15, -2.65, 4.95), (6.7, -6.15, 6.85, 4.95)):
    box(rf, 'plaster', x0, y0, R1, x1, y1, R1 + .4, .015)
    box(rf, 'concrete', x0 - .02, y0 - .02, R1 + .4, x1 + .02, y1 + .02, R1 + .45, .01)
box(rf, 'lamp', -2.75, -6.27, R0 - .025, 6.8, -6.22, R0, .004)
box(rf, 'plaster', 3.6, 1.6, R1, 5.9, 4.4, R1 + 2.3)
box(rf, 'wood_dark', 4.2, 1.55, R1, 5.0, 1.6, R1 + 2.0, .008)
box(rf, 'plaster', 3.4, 1.4, R1 + 2.3, 6.1, 4.6, R1 + 2.45, .02)
box(rf, 'terrace', 3.5, 1.5, R1 + 2.45, 6.0, 4.5, R1 + 2.46, .003)
cyl(rf, 'concrete', (4.75, 3.0, R1 + 2.45), .5, .12, 32)
cyl(rf, 'tank', (4.75, 3.0, R1 + 2.57), .62, 1.15, 40, r2=.6, bev=.03)
cyl(rf, 'tank', (4.75, 3.0, R1 + 3.72), .24, .08, 24)
for k in range(1, 5):  # ribs
    cyl(rf, 'tank', (4.75, 3.0, R1 + 2.57 + k * .23), .635, .03, 40)
tilt = Matrix.Rotation(math.radians(15), 4, 'X')
for cx in (-1.4, .75):
    for cy in (-2.6, -.6):
        c = Vector((cx, cy, R1 + .55))
        M = Matrix.Translation(c) @ tilt
        box(rf, 'solar', -.98, -.5, -.02, .98, .5, .02, .004, M=M)
        box(rf, 'metal', -1.0, -.52, -.035, 1.0, .52, -.02, .003, M=M)
        for sx in (-.8, .8):
            box(rf, 'metal', cx + sx - .02, cy - .3, R1, cx + sx + .02, cy - .26, R1 + .45, .003)
            box(rf, 'metal', cx + sx - .02, cy + .26, R1, cx + sx + .02, cy + .3, R1 + .7, .003)

# --- interiors (grow up from their floors in the hero animation)
ig = group('int_ground', (0, 0, P))
box(ig, 'rug', -5.5, -2.0, P + .03, -1.9, 1.0, P + .045, .005)
box(ig, 'fabric', -5.3, .55, P + .03, -2.5, 1.45, P + .42, .05)                       # sofa
box(ig, 'fabric', -5.3, 1.2, P + .42, -2.5, 1.45, P + .88, .05)
box(ig, 'fabric', -5.3, -.7, P + .03, -4.4, .55, P + .42, .05)
for x0, x1 in ((-5.25, -4.3), (-4.25, -3.4), (-3.35, -2.55)):
    box(ig, 'fabric', x0, .6, P + .42, x1, 1.22, P + .55, .05)
box(ig, 'fabric2', -4.0, 1.0, P + .5, -3.55, 1.2, P + .9, .06)
box(ig, 'fabric2', -3.1, 1.0, P + .5, -2.7, 1.2, P + .88, .06)
box(ig, 'wood', -4.3, -1.05, P + .36, -3.0, -.25, P + .42, .015)                     # coffee table
box(ig, 'dark', -4.1, -.9, P + .03, -3.2, -.4, P + .36, .01)
cyl(ig, 'metal', (-5.35, -1.7, P + .03), .16, .03, 24)                               # floor lamp
cyl(ig, 'metal', (-5.35, -1.7, P + .06), .015, 1.45, 8)
cyl(ig, 'lamp', (-5.35, -1.7, P + 1.45), .2, .3, 28, r2=.15)
light('floor', -5.35, -1.7, P + 1.4)
box(ig, 'wood', -1.6, 1.6, P + .72, .6, 2.6, P + .78, .015)                          # dining
for lx, ly in ((-1.45, 1.75), (.45, 1.75), (-1.45, 2.45), (.45, 2.45)):
    box(ig, 'dark', lx - .03, ly - .03, P + .03, lx + .03, ly + .03, P + .72, .005)
for cx in (-1.1, -.5, .1):
    for s in (-1, 1):
        cy = 2.1 + s * .78
        box(ig, 'fabric', cx - .22, cy - .22, P + .44, cx + .22, cy + .22, P + .5, .02)
        box(ig, 'fabric', cx - .22, cy + s * .18, P + .5, cx + .22, cy + s * .23, P + 1.0, .02)
        box(ig, 'dark', cx - .2, cy - .2, P + .03, cx + .2, cy + .2, P + .44, .004)
    cyl(ig, 'metal', (cx, 2.1, P + 2.1), .006, S0 - P - 2.1, 6)
    blob(ig, 'lamp', (cx, 2.1, P + 2.0), .14, 2, 0, 1)
    light(f'pend{cx}', cx, 2.1, P + 1.9)
box(ig, 'white', -1.8, 3.6, P + .03, 1.0, 4.25, P + .9, .01)                          # kitchen
box(ig, 'dark', -1.85, 3.55, P + .9, 1.05, 4.25, P + .95, .01)
box(ig, 'wood', -1.8, 3.9, P + 1.9, 1.0, 4.25, P + 2.6, .01)
box(ig, 'dark', -4.6, 4.2, P + 1.2, -3.0, 4.25, P + 2.3, .005)                      # art
box(ig, 'fabric2', -4.5, 4.18, P + 1.3, -3.1, 4.2, P + 2.2, .002)
for px, py in ((.55, -3.7), (-5.3, -3.8)):                                           # indoor plants
    cyl(ig, 'pot', (px, py, P + .03), .28, .5, 28, r2=.22, bev=.02)
    bush(ig, (px, py, P + 1.05), .55, 1.2)
for lx, ly in ((-4.4, -2.6), (-1.8, -2.6), (-4.4, .6), (4.0, 0), (3.2, -2.4)):
    cyl(ig, 'lamp', (lx, ly, S0 - .03), .18, .03, 24)
    light(f'c{lx}{ly}', lx, ly, S0 - .4)
box(ig, 'wood', 4.0, 3.9, P + .03, 5.7, 4.25, P + 2.2, .01)                          # shelf in block B
box(ig, 'fabric', 2.6, 1.0, P + .03, 4.6, 1.9, P + .45, .05)

iu = group('int_upper', (0, 0, F0))
box(iu, 'wood', -1.2, -.25, F0, .9, 0, F0 + 1.25, .02)                               # bedroom
box(iu, 'wood_dark', -1.1, -2.4, F0 + .03, .8, -.25, F0 + .35, .02)
box(iu, 'white', -1.05, -2.35, F0 + .35, .75, -.3, F0 + .6, .06)
box(iu, 'fabric2', -1.08, -2.38, F0 + .58, .78, -1.1, F0 + .66, .04)
for x0, x1 in ((-.95, -.2), (-.05, .65)):
    box(iu, 'white', x0, -.7, F0 + .6, x1, -.32, F0 + .76, .06)
for sx in (-1.55, 1.15):
    box(iu, 'wood', sx - .22, -.65, F0 + .03, sx + .22, -.2, F0 + .5, .01)
    cyl(iu, 'lamp', (sx, -.42, F0 + .5), .11, .28, 20, r2=.08)
    light(f'bed{sx}', sx, -.42, F0 + .9)
box(iu, 'rug', -1.6, -3.6, F0 + .03, 1.3, -1.6, F0 + .045, .005)
cyl(iu, 'lamp', (-.2, -2.5, R0 - .03), .2, .03, 24); light('bedc', -.2, -2.5, R0 - .4)
box(iu, 'wood', 2.8, -5.0, F0 + .72, 5.0, -4.35, F0 + .77, .01)                     # study
box(iu, 'wood', 2.85, -4.95, F0 + .03, 2.9, -4.4, F0 + .72, .005); box(iu, 'wood', 4.9, -4.95, F0 + .03, 4.95, -4.4, F0 + .72, .005)
box(iu, 'dark', 3.6, -4.95, F0 + .78, 4.3, -4.9, F0 + 1.2, .005)
box(iu, 'fabric', 3.7, -4.1, F0 + .45, 4.2, -3.6, F0 + .52, .02); box(iu, 'fabric', 3.7, -3.65, F0 + .52, 4.2, -3.6, F0 + 1.0, .02)
box(iu, 'wood', 1.8, -1.0, F0 + .03, 5.9, -.6, F0 + 2.3, .01)
cyl(iu, 'lamp', (3.9, -2.6, R0 - .03), .2, .03, 24); light('study', 3.9, -2.6, R0 - .4)
light('hall', 2.0, 2.0, R0 - .5)

# downpipes, AC outdoor units, wall lights by the door
for (px, py, z0, z1) in ((6.34, 4.3, P, R1), (-6.09, -4.6, P, S1), (-2.29, -5.69, S1, R1)):
    cyl('upper', 'pvc', (px, py, z0), .055, z1 - z0, 14)
    cyl('upper', 'pvc', (px, py, z1 - .25), .07, .1, 14)
for (x0, x1, y0, y1, z0, grp) in ((6.25, 6.55, 2.0, 2.85, F0 + .3, 'upper'), (-6.3, -6.0, 2.2, 3.05, P + .3, 'ground')):
    box(grp, 'ac', x0, y0, z0, x1, y1, z0 + .6, .02)
    fx = x1 if x0 > 0 else x0
    cyl(grp, 'dark', (fx, (y0 + y1) / 2, z0 + .3), .21, .012, 28, rot=Matrix.Rotation(math.radians(90 if x0 > 0 else -90), 4, 'Y'))
for sx in (1.7, 3.25):
    box('ground', 'dark', sx, -3.76, P + 1.95, sx + .14, -3.68, P + 2.25, .01)
    box('ground', 'lamp', sx + .02, -3.78, P + 1.98, sx + .12, -3.76, P + 2.22, .004)
light('door', 2.6, -4.2, P + 2.0, 'out')

def curtain(g, x0, x1, y, z0, z1):
    """Gathered sheer curtain: alternating folds just inside the glass."""
    n = max(3, int((x1 - x0) / .09))
    for i in range(n):
        a = x0 + (x1 - x0) * i / n; b = a + (x1 - x0) / n
        o = .05 if i % 2 else 0
        box(g, 'curtain', a, y + o, z0, b, y + o + .025, z1, .004)
curtain('int_upper', -1.9, -1.3, -5.33, F0 + .05, R0 - .08)
curtain('int_upper', 1.0, 1.55, -5.33, F0 + .05, R0 - .08)
curtain('int_ground', -5.7, -5.05, -4.3, P + .05, S0 - .1)
curtain('int_ground', .45, 1.15, -4.3, P + .05, S0 - .1)
for lx in (-5.0, -3.6):                                                              # terrace loungers
    box(iu, 'wood', lx - .35, -3.9, F0 + .05, lx + .35, -2.0, F0 + .3, .02)
    box(iu, 'fabric', lx - .32, -3.4, F0 + .3, lx + .32, -2.0, F0 + .38, .03)
    box(iu, 'fabric', lx - .32, -3.9, F0 + .3, lx + .32, -3.4, F0 + .75, .03, M=None)
for px, py, s in ((-5.85, -4.55, 1), (-2.6, -4.55, .8), (-5.85, 4.3, 1.1), (-2.6, 3.0, .9)):
    cyl(iu, 'pot', (px, py, F0 + .05), .26 * s, .55 * s, 28, r2=.2 * s, bev=.02)
    bush(iu, (px, py, F0 + .05 + .55 * s + .35 * s), .45 * s, 1.1)

# --- trees: each its own group so it can grow from its base
def palm(name, x, y, h, lean):
    g = group(name, (x, y, 0))
    n = 18; pts = [Vector((x + lean[0] * (i / n) ** 2, y + lean[1] * (i / n) ** 2, h * i / n)) for i in range(n + 1)]
    for i in range(n):
        a, b = pts[i], pts[i + 1]; d = b - a
        r = .19 * (1 - .3 * i / n) + .1 * max(0, 1 - i / 2)
        cyl(g, 'trunk', a, r * 1.03, d.length * 1.02, 16, r2=r * .97, rot=d.to_track_quat('Z', 'Y').to_matrix().to_4x4())
    top = pts[-1]
    for k in range(9):
        a = k * 2.4
        blob(g, 'coconut', top + Vector((math.cos(a) * .24, math.sin(a) * .24, -.3 - (k % 3) * .1)), .14, 1, 0, 1)
    cyl(g, 'trunk', top - Vector((0, 0, .5)), .26, .6, 16, r2=.16)
    for dry in (False, True):
        verts, faces, nrm = [], [], []
        fronds = 3 if dry else 20
        for j in range(fronds):
            az = j * 2 * math.pi / fronds + random.uniform(-.2, .2)
            if dry: el0, L, drop = -.9, random.uniform(2.0, 2.6), .3
            else:   el0, L, drop = random.uniform(.15, 1.0), random.uniform(2.5, 3.2), random.uniform(.9, 1.3)
            hd = Vector((math.cos(az), math.sin(az), 0)); side = Vector((math.sin(az), -math.cos(az), 0))
            p = top.copy(); m = 28
            for i in range(m):
                t = i / m; el = el0 - t * (el0 + drop) * (1.3 if el0 > .8 else 1)
                q = p + (hd * math.cos(el) + Vector((0, 0, math.sin(el)))) * L / m
                tg = (q - p).normalized()
                if i > 2:
                    ll = (.85 * math.sin(math.pi * min(1, t * 1.15)) + .15) * random.uniform(.85, 1.1)
                    for sg in (-1, 1):
                        sd = side * sg * math.cos(.35) + Vector((0, 0, .35 if not dry else -.6))
                        mid = p + sd * ll * .5 + Vector((0, 0, -.06 * ll)) + tg * .12
                        tip = p + sd * ll + Vector((0, 0, -.5 * ll)) + tg * .32
                        w = tg * .05
                        o = len(verts); verts += [p, p + w * 1.6, mid + w, mid - w * .2, tip]
                        faces += [(o, o + 1, o + 2, o + 3), (o + 3, o + 2, o + 4)]
                o = len(verts); verts += [p - side * .025, p + side * .025, q + side * .02, q - side * .02]
                faces.append((o, o + 1, o + 2, o + 3))
                p = q
        for v in verts: nrm.append(((v - top).normalized() + Vector((0, 0, .35))).normalized())
        raw(g, 'palm_dry' if dry else 'palm', verts, faces, True, nrm)

def tree(name, x, y, s):
    """Trunk that forks into branches, each carrying an uneven leaf cluster."""
    g = group(name, (x, y, 0))
    base = Vector((x, y, 0)); fork = base + Vector((random.uniform(-.15, .15), random.uniform(-.15, .15), 1.7 * s))
    d = fork - base
    cyl(g, 'bark', base, .17 * s, d.length, 14, r2=.12 * s, rot=d.to_track_quat('Z', 'Y').to_matrix().to_4x4())
    ends = []
    for k in range(5):
        a = k * 2 * math.pi / 5 + random.uniform(-.3, .3); up = random.uniform(.55, 1.0); L = random.uniform(1.1, 1.6) * s
        e = fork + Vector((math.cos(a) * math.cos(up), math.sin(a) * math.cos(up), math.sin(up))) * L
        dd = e - fork
        cyl(g, 'bark', fork, .09 * s, dd.length, 10, r2=.04 * s, rot=dd.to_track_quat('Z', 'Y').to_matrix().to_4x4())
        ends.append(e)
    for e in ends: bush(g, tuple(e + Vector((0, 0, .25 * s))), random.uniform(.7, .95) * s, .8)
    bush(g, tuple(fork + Vector((0, 0, 1.6 * s))), 1.0 * s, .8)
    for k in range(3):
        a = random.uniform(0, 6.28)
        bush(g, tuple(fork + Vector((math.cos(a) * .7 * s, math.sin(a) * .7 * s, random.uniform(.6, 1.2) * s))), .65 * s, .85)

palm('palm_0', -10.0, -4.8, 5.4, (.9, .2))
palm('palm_1', -10.8, 4.4, 6.4, (-.4, .5))
palm('palm_2', -1.5, 8.6, 7.6, (.4, -.3))
palm('palm_3', 9.4, -7.6, 5.8, (.7, -.3))
tree('tree_0', -8.2, 7.0, 1.1)
tree('tree_1', 10.6, -4.6, .85)
tree('tree_2', -3.4, -8.5, .6)

def car(cx, cy):
    """Compact red crossover parked nose-in on the driveway. Built along local +X, turned to face the house."""
    g = group('car', (cx, cy, 0))
    Mc = Matrix.Translation(Vector((cx, cy, 0))) @ Matrix.Rotation(math.pi / 2, 4, 'Z')
    def extrude(m, prof, y0, y1, bev):
        bm = bmesh.new()
        a = [bm.verts.new((x, y0, z)) for x, z in prof]; b = [bm.verts.new((x, y1, z)) for x, z in prof]
        bm.faces.new(a[::-1]); bm.faces.new(b)
        for i in range(len(prof)):
            j = (i + 1) % len(prof); bm.faces.new((a[i], a[j], b[j], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bevel(bm, bev)
        emit(bm, g, m, Mc, smooth=lambda f: abs(f.normal.y) < .9)
    def arch(xc):
        return [(xc + .4 * math.cos(math.radians(a)), .32 + .4 * math.sin(math.radians(a))) for a in range(180, -1, -15)]
    body = ([(-1.97, .24)] + arch(-1.25) + [(-.85, .22), (.85, .22)] + arch(1.25) +
            [(1.97, .24), (2.03, .48), (1.99, .7), (1.6, .87), (.75, .97), (-1.85, .99), (-2.0, .88), (-2.03, .5)])
    extrude('carpaint', body, -.87, .87, .06)
    extrude('carglass', [(-1.88, .96), (.8, .96), (-.02, 1.5), (-1.45, 1.53), (-1.86, 1.12)], -.76, .76, .05)
    box(g, 'carpaint', -1.44, -.73, 1.49, 0, .73, 1.57, .035, M=Mc)
    for sg in (-1, 1):
        y0, y1 = sorted((sg * .7, sg * .78))
        extrude('carpaint', [(.8, .96), (.7, .96), (-.08, 1.51), (-.01, 1.51)], y0, y1, .01)            # A pillar
        extrude('carplastic', [(-.62, .96), (-.52, .96), (-.52, 1.51), (-.62, 1.51)], y0, y1, .01)        # B pillar
        y0, y1 = sorted((sg * .66, sg * .78))
        extrude('carpaint', [(-1.88, .96), (-1.42, .96), (-1.28, 1.52), (-1.45, 1.53), (-1.86, 1.12)], y0, y1, .01)  # C pillar
        box(g, 'carpaint', .5, sg * .86, .97, .72, sg * 1.02, 1.1, .02, M=Mc)                           # mirror
        box(g, 'carplastic', -1.35, sg * .58, 1.56, -.15, sg * .65, 1.62, .01, M=Mc)                    # roof rail
        box(g, 'carplastic', -.85, sg * .84, .22, .85, sg * .89, .36, .01, M=Mc)                        # sill
        box(g, 'headlight', 1.86, sg * .5, .69, 2.0, sg * .8, .79, .015, M=Mc)
        box(g, 'taillight', -2.05, sg * .48, .78, -1.94, sg * .84, .9, .01, M=Mc)
        for wx in (-1.25, 1.25):                                                                     # wheels
            W = Mc @ Matrix.Translation(Vector((wx, sg * .89, .32))) @ Matrix.Rotation(math.pi / 2 * sg, 4, 'X')
            for m, r, h, z in (('tyre', .32, .22, 0), ('carplastic', .2, .01, -.005), ('alloy', .06, .02, -.01)):
                bm = bmesh.new(); cone(bm, 32, r, r, h)
                bmesh.ops.translate(bm, vec=Vector((0, 0, h / 2 + z)), verts=bm.verts)
                if m == 'tyre': bevel(bm, .04)
                emit(bm, g, m, W, smooth=lambda f: abs(f.normal.z) < .7)
            for k in range(5):
                box(g, 'alloy', -.025, 0, -.012, .025, .21, .004, .006, M=W @ Matrix.Rotation(k * 2 * math.pi / 5, 4, 'Z'))
    box(g, 'carplastic', 1.62, -.85, .2, 2.06, .85, .44, .03, M=Mc)        # bumpers
    box(g, 'carplastic', -2.06, -.85, .2, -1.62, .85, .44, .03, M=Mc)
    box(g, 'carplastic', 1.97, -.5, .47, 2.05, .5, .67, .01, M=Mc)         # grille
    box(g, 'taillight', -2.04, -.48, .83, -1.99, .48, .86, .004, M=Mc)     # light bar
    box(g, 'white', 2.04, -.26, .3, 2.08, .26, .41, .004, M=Mc)            # plates
    box(g, 'white', -2.08, -.26, .5, -2.04, .26, .61, .004, M=Mc)

car(6.0, -7.55)

# ------------------------------------------------------------------ build objects and export
coll = bpy.context.scene.collection
EMPTY = {}
for name, origin in GROUPS.items():
    e = bpy.data.objects.new(name, None); e.location = origin; coll.objects.link(e); EMPTY[name] = e

for (g, m), (V, F, S) in ACC.items():
    o = GROUPS[g]
    me = bpy.data.meshes.new(f'{g}.{m}')
    me.from_pydata([tuple(v - o) for v in V], [], F)
    me.update()
    me.polygons.foreach_set('use_smooth', S[:len(me.polygons)])
    if (g, m) in NRM:
        nl = NRM[(g, m)]; nl.extend([(0, 0, 1)] * (len(V) - len(nl)))
        me.normals_split_custom_set_from_vertices(nl)
    uv = me.uv_layers.new(name='UVMap'); k = 1 / UVS[m]
    co = [me.vertices[i].co + o for i in range(len(me.vertices))]
    for poly in me.polygons:
        if m == 'foliage':
            for j, li in enumerate(poly.loop_indices): uv.data[li].uv = ((0, 0), (1, 0), (1, 1), (0, 1))[j % 4]
            continue
        n = poly.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            c = co[me.loops[li].vertex_index]
            uv.data[li].uv = (c.y * k, c.z * k) if ax == 0 else (c.x * k, c.z * k) if ax == 1 else (c.x * k, c.y * k)
    me.materials.append(MATS[m])
    ob = bpy.data.objects.new(me.name, me); coll.objects.link(ob); ob.parent = EMPTY[g]

for name, pos in LIGHTS:
    e = bpy.data.objects.new(name, None); e.location = pos; coll.objects.link(e)

kw = dict(filepath=OUT, export_format='GLB', export_cameras=False, export_lights=False,
          export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7)
try: bpy.ops.export_scene.gltf(**kw, export_image_format='JPEG')
except TypeError: bpy.ops.export_scene.gltf(**kw)
print('EXPORTED', OUT, os.path.getsize(OUT), 'bytes,', sum(len(f) for _, f, _ in ACC.values()), 'faces')
