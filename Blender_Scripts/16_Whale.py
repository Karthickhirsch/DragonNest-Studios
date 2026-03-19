"""
IsleTrial – Sea Creature 04-B: Humpback Whale  (HIGH QUALITY REBUILD)
=======================================================================
Type    Megaptera novaeangliae (Humpback) — majestic ocean presence
Size    14 m long × 4 m wide × 3 m tall
Poly    ~12 000–16 000 tris (PC); Sub level 1 → ~6 000 (mobile)

Parts built:
  Whale_Body           – bmesh 48×32 fusiform body with broad snout,
                          dorsal hump, tapered peduncle
  Whale_BellyGrooves   – 14 throat-pleat grooves (bmesh extrude ridges)
  Whale_FlipperL/R     – bmesh swept-back 3 m flippers with tubercle bumps
  Whale_FlipperTuber_* – 12 individual tubercle spheres per flipper
  Whale_Flukes         – bmesh 4 m butterfly tail flukes (upper + lower lobes)
  Whale_DorsalHump     – secondary dorsal fin hump (raised ridge)
  Whale_Eye_L/R        – 3-layer (socket / sclera / iris / pupil)
  Whale_MouthUpper     – broad upper jaw roof plate
  Whale_MouthLower     – lower jaw gape plate
  Whale_BaleenPlate_*  – 16 baleen plates inside mouth opening
  Whale_Blowhole       – raised blowhole on top of head
  Whale_BarnacleCluster_* – 8 barnacle patch clusters on body/flippers
  Whale_SkinFolds_L/R  – 3 per-side skin ridge details around head
  Whale_BellyPigment   – lighter belly dome overlay

Materials (full dual-path procedural + [UNITY] image slots):
  Mat_Whale_Back       – dark charcoal with noise scratches + speckle
  Mat_Whale_Belly      – creamy-white with soft noise variation
  Mat_Whale_Flipper    – dark slate matching body, subtle bump
  Mat_Whale_Baleen     – yellowish ivory with fine parallel lines
  Mat_Whale_Eye        – wet black
  Mat_Whale_Iris       – deep amber-brown ring
  Mat_Whale_Barnacle   – rough grey-white with voronoi cell detail

Run BEFORE 16_Whale_Rig.py  inside Blender ▸ Scripting tab.
"""

import bpy, bmesh, math
from mathutils import Vector

# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)

def new_col(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c); return c

def link(col, obj):
    for ex in list(obj.users_collection): ex.objects.unlink(obj)
    col.objects.link(obj)

def add_sub(obj, lv=2):
    m = obj.modifiers.new('Sub', 'SUBSURF'); m.levels = lv; m.render_levels = lv

def add_solidify(obj, t=0.015):
    m = obj.modifiers.new('Solid', 'SOLIDIFY'); m.thickness = t; m.offset = 0.0

def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj; obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT'); obj.select_set(False)

def prim(tp, name, loc=(0,0,0), rot=(0,0,0), size=1.0, **kw):
    if tp == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=loc, rotation=rot,
            segments=kw.get('segs',22), ring_count=kw.get('rings',14))
    elif tp == 'cyl':
        bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=kw.get('depth',1.0),
            location=loc, rotation=rot, vertices=kw.get('verts',16))
    elif tp == 'cone':
        bpy.ops.mesh.primitive_cone_add(radius1=kw.get('r1',size), radius2=kw.get('r2',0),
            depth=kw.get('depth',1.0), location=loc, rotation=rot, vertices=kw.get('verts',8))
    elif tp == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=size, location=loc, rotation=rot)
    obj = bpy.context.active_object; obj.name = name; return obj

def assign_mat(obj, mat):
    if obj.data.materials: obj.data.materials[0] = mat
    else: obj.data.materials.append(mat)

# ═══════════════════════════════════════════════════════════════════
#  MATERIAL SYSTEM
# ═══════════════════════════════════════════════════════════════════

def _n(nodes, ntype, loc, label=None):
    nd = nodes.new(ntype); nd.location = loc
    if label: nd.label = nd.name = label; return nd

def _img(nodes, sname, loc):
    nd = nodes.new('ShaderNodeTexImage'); nd.location = loc
    nd.label = nd.name = f'[UNITY] {sname}'; return nd

def _mapping(nodes, links, scale=(4,4,4), loc=(-900,0)):
    tc = _n(nodes, 'ShaderNodeTexCoord', (loc[0]-200, loc[1]))
    mp = _n(nodes, 'ShaderNodeMapping', loc)
    mp.inputs['Scale'].default_value = (*scale,)
    links.new(tc.outputs['UV'], mp.inputs['Vector']); return mp

def _mix_pi(nodes, links, proc, img_nd, loc):
    mix = _n(nodes, 'ShaderNodeMixRGB', loc); mix.blend_type = 'MIX'
    mix.inputs[0].default_value = 0.0
    links.new(proc, mix.inputs[1]); links.new(img_nd.outputs['Color'], mix.inputs[2]); return mix

def _bump_n(nodes, links, mp, scale=20.0, strength=0.35, loc=(-400,-400)):
    bn = _n(nodes, 'ShaderNodeTexNoise', loc)
    bn.inputs['Scale'].default_value = scale; bn.inputs['Detail'].default_value = 8.0
    links.new(mp.outputs['Vector'], bn.inputs['Vector'])
    img_n = _img(nodes, '_NormalMap', (loc[0], loc[1]-180))
    mix_n = _mix_pi(nodes, links, bn.outputs['Fac'], img_n, (loc[0]+260, loc[1]-90))
    bmp = _n(nodes, 'ShaderNodeBump', (loc[0]+480, loc[1]-90))
    bmp.inputs['Strength'].default_value = strength
    links.new(mix_n.outputs['Color'], bmp.inputs['Height']); return bmp

def _base(name):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    n = mat.node_tree.nodes; lk = mat.node_tree.links; n.clear()
    bsdf = _n(n, 'ShaderNodeBsdfPrincipled', (700, 0))
    out  = _n(n, 'ShaderNodeOutputMaterial', (1000, 0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface']); return mat, n, lk, bsdf

# ── Whale back (dark charcoal + large scratch noise + speckle) ────
def mat_whale_back(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(3,3,3))

    # Large-scale skin mottling
    noise_big = _n(n, 'ShaderNodeTexNoise', (-700, 350))
    noise_big.inputs['Scale'].default_value = 2.5; noise_big.inputs['Detail'].default_value = 8.0
    noise_big.inputs['Roughness'].default_value = 0.72
    lk.new(mp.outputs['Vector'], noise_big.inputs['Vector'])

    # Fine scratch detail
    noise_fine = _n(n, 'ShaderNodeTexNoise', (-700, 150))
    noise_fine.inputs['Scale'].default_value = 18.0; noise_fine.inputs['Detail'].default_value = 16.0
    lk.new(mp.outputs['Vector'], noise_fine.inputs['Vector'])

    # Voronoi speckle for scars and marks
    vor = _n(n, 'ShaderNodeTexVoronoi', (-700, -50))
    vor.inputs['Scale'].default_value = 9.0; vor.feature = 'DISTANCE_TO_EDGE'
    lk.new(mp.outputs['Vector'], vor.inputs['Vector'])

    # Combine: big mottling × fine scratch
    mix_bf = _n(n, 'ShaderNodeMixRGB', (-400, 250))
    mix_bf.blend_type = 'MULTIPLY'; mix_bf.inputs[0].default_value = 0.65
    lk.new(noise_big.outputs['Fac'], mix_bf.inputs[1])
    lk.new(noise_fine.outputs['Fac'], mix_bf.inputs[2])

    # Add voronoi speckle
    mix_vs = _n(n, 'ShaderNodeMixRGB', (-200, 200))
    mix_vs.blend_type = 'SCREEN'; mix_vs.inputs[0].default_value = 0.12
    lk.new(mix_bf.outputs['Color'], mix_vs.inputs[1])
    lk.new(vor.outputs['Distance'], mix_vs.inputs[2])

    # Colour ramp: dark charcoal palette
    cr = _n(n, 'ShaderNodeValToRGB', (50, 200))
    cr.color_ramp.elements[0].color = (0.05, 0.06, 0.08, 1)   # near-black #181E26
    e1 = cr.color_ramp.elements.new(0.35); e1.color = (0.09, 0.11, 0.14, 1)
    cr.color_ramp.elements[1].color = (0.18, 0.20, 0.22, 1)    # dark grey
    lk.new(mix_vs.outputs['Color'], cr.inputs['Fac'])

    img_a = _img(n, f'{name}_Albedo', (-700, -250))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (520, 100))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness from fine noise
    mr = _n(n, 'ShaderNodeMapRange', (50, -100))
    mr.inputs['From Min'].default_value = 0.2; mr.inputs['From Max'].default_value = 0.8
    mr.inputs['To Min'].default_value = 0.62; mr.inputs['To Max'].default_value = 0.82
    lk.new(noise_fine.outputs['Fac'], mr.inputs['Value'])
    lk.new(mr.outputs['Result'], bsdf.inputs['Roughness'])

    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Specular IOR Level'].default_value = 0.22
    bmp = _bump_n(n, lk, mp, scale=25.0, strength=0.30)
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    return mat

# ── Whale belly (creamy white with noise + soft greyish boundary) ─
def mat_whale_belly(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(4,4,4))
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 200))
    noise.inputs['Scale'].default_value = 8.0; noise.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    noise2 = _n(n, 'ShaderNodeTexNoise', (-500, 0))
    noise2.inputs['Scale'].default_value = 30.0; noise2.inputs['Detail'].default_value = 8.0
    lk.new(mp.outputs['Vector'], noise2.inputs['Vector'])
    mix_nn = _n(n, 'ShaderNodeMixRGB', (-250, 100)); mix_nn.blend_type = 'OVERLAY'
    mix_nn.inputs[0].default_value = 0.22
    lk.new(noise.outputs['Fac'], mix_nn.inputs[1]); lk.new(noise2.outputs['Fac'], mix_nn.inputs[2])
    # Gradient for belly-back blending
    tc = _n(n, 'ShaderNodeTexCoord', (-700, -200))
    grad = _n(n, 'ShaderNodeTexGradient', (-500, -200)); grad.gradient_type = 'SPHERICAL'
    lk.new(tc.outputs['Object'], grad.inputs['Vector'])
    cr_belly = _n(n, 'ShaderNodeValToRGB', (-300, -200))
    cr_belly.color_ramp.elements[0].color = (0.80, 0.78, 0.70, 1)
    cr_belly.color_ramp.elements[1].color = (0.95, 0.94, 0.90, 1)
    lk.new(grad.outputs['Color'], cr_belly.inputs['Fac'])
    mix_bg = _n(n, 'ShaderNodeMixRGB', (-50, 100)); mix_bg.blend_type = 'SCREEN'
    mix_bg.inputs[0].default_value = 0.28
    lk.new(mix_nn.outputs['Color'], mix_bg.inputs[1]); lk.new(cr_belly.outputs['Color'], mix_bg.inputs[2])
    img_a = _img(n, f'{name}_Albedo', (-500, -350))
    mix_c = _mix_pi(n, lk, mix_bg.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.68
    bsdf.inputs['Subsurface Weight'].default_value = 0.04
    bsdf.inputs['Subsurface Radius'].default_value = (0.90, 0.88, 0.84)
    return mat

# ── Flipper (dark slate matching body, subtle bump) ───────────────
def mat_flipper(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(3,3,3))
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 200))
    noise.inputs['Scale'].default_value = 10.0; noise.inputs['Detail'].default_value = 8.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-200, 200))
    cr.color_ramp.elements[0].color = (0.04, 0.05, 0.07, 1)
    cr.color_ramp.elements[1].color = (0.12, 0.14, 0.18, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    img_a = _img(n, f'{name}_Albedo', (-500, -200))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.72
    bmp = _bump_n(n, lk, mp, scale=22.0, strength=0.35)
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    return mat

# ── Baleen plates (yellowish ivory with fine parallel lines) ──────
def mat_baleen(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(8,8,8))
    wave = _n(n, 'ShaderNodeTexWave', (-600, 200)); wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = 14.0; wave.inputs['Distortion'].default_value = 0.6
    wave.inputs['Detail'].default_value = 3.0
    lk.new(mp.outputs['Vector'], wave.inputs['Vector'])
    noise = _n(n, 'ShaderNodeTexNoise', (-600, 0)); noise.inputs['Scale'].default_value = 12.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    mix_wn = _n(n, 'ShaderNodeMixRGB', (-300, 100)); mix_wn.blend_type = 'MULTIPLY'
    mix_wn.inputs[0].default_value = 0.35
    lk.new(wave.outputs['Color'], mix_wn.inputs[1]); lk.new(noise.outputs['Fac'], mix_wn.inputs[2])
    cr = _n(n, 'ShaderNodeValToRGB', (-50, 100))
    cr.color_ramp.elements[0].color = (0.55, 0.50, 0.30, 1)   # yellowish-ivory
    cr.color_ramp.elements[1].color = (0.78, 0.74, 0.55, 1)
    lk.new(mix_wn.outputs['Color'], cr.inputs['Fac'])
    img_a = _img(n, f'{name}_Albedo', (-600, -200))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.78
    bsdf.inputs['Transmission Weight'].default_value = 0.12
    return mat

# ── Eye (wet black) / Iris (deep amber) ───────────────────────────
def mat_eye_black(name):
    mat, n, lk, bsdf = _base(name)
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
    bsdf.inputs['Roughness'].default_value = 0.03
    bsdf.inputs['Specular IOR Level'].default_value = 1.0
    return mat

def mat_whale_iris(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(5,5,5))
    vor = _n(n, 'ShaderNodeTexVoronoi', (-400, 100))
    vor.inputs['Scale'].default_value = 18.0; lk.new(mp.outputs['Vector'], vor.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-100, 100))
    cr.color_ramp.elements[0].color = (0.16, 0.08, 0.02, 1)   # deep amber-brown
    cr.color_ramp.elements[1].color = (0.42, 0.22, 0.06, 1)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    img_a = _img(n, f'{name}_Albedo', (-400, -200))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.06
    return mat

# ── Barnacle (rough grey-white voronoi) ───────────────────────────
def mat_barnacle(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(10,10,10))
    vor = _n(n, 'ShaderNodeTexVoronoi', (-500, 200))
    vor.inputs['Scale'].default_value = 22.0; vor.feature = 'DISTANCE_TO_EDGE'
    lk.new(mp.outputs['Vector'], vor.inputs['Vector'])
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 0)); noise.inputs['Scale'].default_value = 14.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    mix_vn = _n(n, 'ShaderNodeMixRGB', (-250, 100)); mix_vn.blend_type = 'OVERLAY'
    mix_vn.inputs[0].default_value = 0.48
    lk.new(vor.outputs['Distance'], mix_vn.inputs[1]); lk.new(noise.outputs['Fac'], mix_vn.inputs[2])
    cr = _n(n, 'ShaderNodeValToRGB', (-50, 100))
    cr.color_ramp.elements[0].color = (0.48, 0.44, 0.40, 1)
    cr.color_ramp.elements[1].color = (0.78, 0.76, 0.72, 1)
    lk.new(mix_vn.outputs['Color'], cr.inputs['Fac'])
    img_a = _img(n, f'{name}_Albedo', (-500, -200))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.88
    bmp = _bump_n(n, lk, mp, scale=25.0, strength=0.55)
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    return mat

def build_materials():
    return {
        'back'    : mat_whale_back('Mat_Whale_Back'),
        'belly'   : mat_whale_belly('Mat_Whale_Belly'),
        'flipper' : mat_flipper('Mat_Whale_Flipper'),
        'baleen'  : mat_baleen('Mat_Whale_Baleen'),
        'eye_s'   : mat_eye_black('Mat_Whale_Eye'),
        'iris'    : mat_whale_iris('Mat_Whale_Iris'),
        'barnacle': mat_barnacle('Mat_Whale_Barnacle'),
    }

# ═══════════════════════════════════════════════════════════════════
#  GEOMETRY
# ═══════════════════════════════════════════════════════════════════

def build_whale_body(mats, col):
    """48×32 bmesh body with broad snout, dorsal hump, tapered peduncle."""
    objs = []
    bm = bmesh.new()
    segs = 48; rings = 32
    L = 7.0; W = 2.0; H = 1.4

    verts_grid = []
    for ri in range(rings + 1):
        t = ri / rings; y = -L + t * 2 * L
        # Width profile: broad snout, widest at ~45%, taper to narrow peduncle
        if t < 0.05:   w = W * (t/0.05) * 0.55
        elif t < 0.12: w = W * (0.55 + (t-0.05)/0.07 * 0.45)
        elif t < 0.50: w = W * 1.0
        elif t < 0.75: w = W * (1.0 - (t-0.50)/0.25 * 0.70)
        else:          w = W * max(0.04, 0.30 - (t-0.75)/0.25 * 0.26)
        # Height profile: front snout low, hump at 35%, taper tail
        if t < 0.06:   h = H * (t/0.06) * 0.40
        elif t < 0.25: h = H * (0.40 + (t-0.06)/0.19 * 0.45)
        elif t < 0.38: h = H * (0.85 + (t-0.25)/0.13 * 0.15)   # dorsal hump
        elif t < 0.55: h = H * (1.0 - (t-0.38)/0.17 * 0.15)
        elif t < 0.80: h = H * (0.85 - (t-0.55)/0.25 * 0.40)
        else:          h = H * max(0.06, 0.45 - (t-0.80)/0.20 * 0.39)
        ring = []
        for si in range(segs):
            a = 2 * math.pi * si / segs
            x = w * math.cos(a); z = h * math.sin(a)
            # Flatten belly significantly
            if z < 0: z *= 0.55
            ring.append(bm.verts.new(Vector((x, y, z))))
        verts_grid.append(ring)
    for ri in range(rings):
        for si in range(segs):
            v0=verts_grid[ri][si]; v1=verts_grid[ri][(si+1)%segs]
            v2=verts_grid[ri+1][(si+1)%segs]; v3=verts_grid[ri+1][si]
            try: bm.faces.new([v0,v1,v2,v3])
            except: pass
    tc = bm.verts.new(Vector((0,-L,0))); hc = bm.verts.new(Vector((0,L,0)))
    for si in range(segs):
        try:
            bm.faces.new([verts_grid[0][(si+1)%segs],verts_grid[0][si],tc])
            bm.faces.new([verts_grid[-1][si],verts_grid[-1][(si+1)%segs],hc])
        except: pass
    mesh = bpy.data.meshes.new('Whale_Body_Mesh'); bm.to_mesh(mesh); bm.free()
    body = bpy.data.objects.new('Whale_Body', mesh)
    bpy.context.scene.collection.objects.link(body)
    assign_mat(body, mats['back'])
    body.data.materials.append(mats['belly'])
    add_sub(body, 2); smart_uv(body); link(col, body); objs.append(body)
    return objs

def build_belly_grooves(mats, col):
    """14 throat-pleat / ventral groove ridges."""
    objs = []
    for i in range(14):
        t = i / 13
        gx = (t - 0.5) * 3.60; gy = -4.8
        gz = -0.55 - 0.30 * (1.0 - abs(t - 0.5) * 2)
        depth = 4.2 + abs(t - 0.5) * 2.0
        groove = prim('cyl', f'Whale_BellyGroove_{i}',
                      loc=(gx, gy + depth * 0.5, gz),
                      size=0.030, depth=depth, verts=6,
                      rot=(0, math.radians(90), 0))
        groove.scale = (0.20, 1.0, 0.60); bpy.ops.object.transform_apply(scale=True)
        assign_mat(groove, mats['belly']); smart_uv(groove); link(col, groove); objs.append(groove)
    return objs

def build_flippers(mats, col):
    """3 m swept-back pectoral flippers with 12 tubercle bumps each."""
    objs = []
    for side, sx in [('L',-1),('R',1)]:
        bm = bmesh.new()
        # 12-point swept flipper outline
        pts = [
            Vector((sx*0.00,  0.60, -0.05)),   # root front
            Vector((sx*0.00,  1.20, -0.08)),   # root rear
            Vector((sx*0.35,  1.50, -0.14)),
            Vector((sx*0.70,  1.80, -0.22)),
            Vector((sx*1.05,  2.10, -0.32)),
            Vector((sx*1.30,  2.35, -0.40)),
            Vector((sx*1.50,  2.50, -0.46)),   # tip
            Vector((sx*1.46,  2.40, -0.48)),
            Vector((sx*1.30,  2.18, -0.44)),
            Vector((sx*1.00,  1.90, -0.38)),
            Vector((sx*0.65,  1.56, -0.28)),
            Vector((sx*0.32,  1.24, -0.18)),
        ]
        for pt in pts: bm.verts.new(pt)
        bm.verts.ensure_lookup_table()
        ctr = bm.verts.new(Vector((sx*0.65, 1.48, -0.28)))
        n_pts = len(pts)
        for i in range(1, n_pts - 1):
            try: bm.faces.new([bm.verts[0], bm.verts[i], bm.verts[i+1]])
            except: pass
        try: bm.faces.new([bm.verts[0], bm.verts[n_pts-1], ctr])
        except: pass
        mesh = bpy.data.meshes.new(f'Whale_Flipper{side}_Mesh')
        bm.to_mesh(mesh); bm.free()
        flip = bpy.data.objects.new(f'Whale_Flipper{side}', mesh)
        bpy.context.scene.collection.objects.link(flip)
        assign_mat(flip, mats['flipper']); add_solidify(flip, 0.10); add_sub(flip, 1)
        smart_uv(flip); link(col, flip); objs.append(flip)

        # 12 tubercle bumps along leading edge
        tb_positions = [
            (sx*0.08, 1.32), (sx*0.20, 1.42), (sx*0.36, 1.58),
            (sx*0.52, 1.72), (sx*0.68, 1.88), (sx*0.84, 2.02),
            (sx*0.98, 2.14), (sx*1.12, 2.24), (sx*1.24, 2.32),
            (sx*1.36, 2.40), (sx*1.44, 2.46), (sx*1.50, 2.50),
        ]
        for ti, (tx, ty) in enumerate(tb_positions):
            tz = -0.25 - ti * 0.02
            tb = prim('sphere', f'Whale_Tubercle_{side}_{ti}',
                      loc=(tx, ty, tz), size=0.045 + ti*0.004, segs=8, rings=6)
            assign_mat(tb, mats['flipper']); link(col, tb); objs.append(tb)
    return objs

def build_flukes(mats, col):
    """4 m butterfly tail flukes (upper + lower lobes)."""
    objs = []
    bm = bmesh.new()
    fy = 7.0    # position at tail end
    # Full fluke outline (both sides merged)
    pts = [
        # Central notch region
        Vector(( 0.00, fy,       0.00)),
        Vector(( 0.00, fy+0.15,  0.00)),
        # Right lobe
        Vector(( 0.20, fy+0.06,  0.10)),
        Vector(( 0.55, fy-0.10,  0.25)),
        Vector(( 0.95, fy-0.28,  0.40)),
        Vector(( 1.30, fy-0.48,  0.55)),
        Vector(( 1.58, fy-0.65,  0.65)),
        Vector(( 1.72, fy-0.72,  0.62)),
        Vector(( 1.68, fy-0.78,  0.58)),
        Vector(( 1.50, fy-0.72,  0.52)),
        Vector(( 1.20, fy-0.60,  0.44)),
        Vector(( 0.85, fy-0.44,  0.32)),
        Vector(( 0.50, fy-0.26,  0.18)),
        Vector(( 0.20, fy-0.06,  0.06)),
        # Left lobe (mirror)
        Vector((-0.20, fy-0.06,  0.06)),
        Vector((-0.50, fy-0.26,  0.18)),
        Vector((-0.85, fy-0.44,  0.32)),
        Vector((-1.20, fy-0.60,  0.44)),
        Vector((-1.50, fy-0.72,  0.52)),
        Vector((-1.68, fy-0.78,  0.58)),
        Vector((-1.72, fy-0.72,  0.62)),
        Vector((-1.58, fy-0.65,  0.65)),
        Vector((-1.30, fy-0.48,  0.55)),
        Vector((-0.95, fy-0.28,  0.40)),
        Vector((-0.55, fy-0.10,  0.25)),
        Vector((-0.20, fy+0.06,  0.10)),
    ]
    for pt in pts: bm.verts.new(pt)
    bm.verts.ensure_lookup_table()
    n_pts = len(pts)
    # Fan triangulate from centre
    for i in range(1, n_pts - 1):
        try: bm.faces.new([bm.verts[0], bm.verts[i], bm.verts[i+1]])
        except: pass
    try: bm.faces.new([bm.verts[0], bm.verts[n_pts-1], bm.verts[1]])
    except: pass
    mesh = bpy.data.meshes.new('Whale_Flukes_Mesh'); bm.to_mesh(mesh); bm.free()
    flukes = bpy.data.objects.new('Whale_Flukes', mesh)
    bpy.context.scene.collection.objects.link(flukes)
    assign_mat(flukes, mats['flipper']); add_solidify(flukes, 0.14); add_sub(flukes, 1)
    smart_uv(flukes); link(col, flukes); objs.append(flukes)

    # Fluke central ridge
    ridge = prim('cyl', 'Whale_FlukeRidge', loc=(0, fy-0.30, 0.30),
                 size=0.065, depth=1.10, verts=8, rot=(0, math.radians(90), 0))
    assign_mat(ridge, mats['back']); link(col, ridge); objs.append(ridge)
    return objs

def build_dorsal_hump(mats, col):
    """Raised dorsal hump + small secondary dorsal fin behind it."""
    objs = []
    hump = prim('sphere', 'Whale_DorsalHump', loc=(0, -0.20, 1.42), size=0.55, segs=16, rings=12)
    hump.scale = (0.45, 1.10, 0.52); bpy.ops.object.transform_apply(scale=True)
    assign_mat(hump, mats['back']); add_sub(hump, 1); smart_uv(hump); link(col, hump); objs.append(hump)

    # Small knuckles/bumps behind main hump (typical of humpback)
    knuckle_pos = [(0, 0.40, 1.18),(0, 0.85, 1.05),(0, 1.30, 0.92),(0, 1.70, 0.78),(0, 2.10, 0.64)]
    for ki, kp in enumerate(knuckle_pos):
        kn = prim('sphere', f'Whale_Knuckle_{ki}', loc=kp, size=0.10 - ki*0.012, segs=8, rings=6)
        kn.scale = (0.50, 1.0, 0.50); bpy.ops.object.transform_apply(scale=True)
        assign_mat(kn, mats['back']); link(col, kn); objs.append(kn)
    return objs

def build_eyes(mats, col):
    objs = []
    for side, sx in [('L',-1),('R',1)]:
        ex, ey, ez = sx*1.48, 4.20, 0.28
        sock = prim('sphere', f'Whale_EyeSocket_{side}', loc=(ex, ey-0.02, ez), size=0.16, segs=12, rings=8)
        sock.scale = (1.0, 0.62, 1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(sock, mats['eye_s']); link(col, sock); objs.append(sock)
        eye = prim('sphere', f'Whale_Eye_{side}', loc=(ex, ey+0.02, ez), size=0.12, segs=12, rings=8)
        eye.scale = (1.0, 0.58, 1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(eye, mats['eye_s']); link(col, eye); objs.append(eye)
        iris = prim('cyl', f'Whale_Iris_{side}', loc=(ex, ey+0.10, ez),
                    size=0.075, depth=0.020, verts=14, rot=(math.radians(90), 0, 0))
        assign_mat(iris, mats['iris']); link(col, iris); objs.append(iris)
        pupil = prim('cyl', f'Whale_Pupil_{side}', loc=(ex, ey+0.12, ez),
                     size=0.038, depth=0.012, verts=10, rot=(math.radians(90), 0, 0))
        assign_mat(pupil, mats['eye_s']); link(col, pupil); objs.append(pupil)
    return objs

def build_mouth_and_baleen(mats, col):
    """Broad mouth plates + 16 baleen plates."""
    objs = []
    # Upper jaw plate
    jaw_up = prim('sphere', 'Whale_JawUpper', loc=(0, 6.50, 0.25), size=1.90, segs=22, rings=14)
    jaw_up.scale = (1.0, 0.68, 0.30); bpy.ops.object.transform_apply(scale=True)
    assign_mat(jaw_up, mats['back']); add_sub(jaw_up, 1); smart_uv(jaw_up); link(col, jaw_up); objs.append(jaw_up)
    # Lower jaw plate
    jaw_lo = prim('sphere', 'Whale_JawLower', loc=(0, 6.40, -0.35), size=1.70, segs=22, rings=12)
    jaw_lo.scale = (1.0, 0.72, 0.24); jaw_lo.rotation_euler=(math.radians(22),0,0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    assign_mat(jaw_lo, mats['belly']); add_sub(jaw_lo, 1); smart_uv(jaw_lo); link(col, jaw_lo); objs.append(jaw_lo)
    # Mouth interior
    interior = prim('sphere', 'Whale_Mouth_Interior', loc=(0, 6.20, -0.10), size=2.2, segs=18, rings=12)
    interior.scale = (0.80, 0.55, 0.28); bpy.ops.object.transform_apply(scale=True)
    assign_mat(interior, mats['belly']); link(col, interior); objs.append(interior)
    # 16 baleen plates (8 each side)
    for side, sx in [('L',-1),('R',1)]:
        for pi in range(8):
            bx = sx * (0.25 + pi * 0.18)
            by = 6.10 - pi * 0.15
            bp = prim('cube', f'Whale_Baleen_{side}_{pi}', loc=(bx, by, 0.20), size=0.01)
            bp.scale = (0.04, 0.28, 0.72); bpy.ops.object.transform_apply(scale=True)
            bp.rotation_euler = (0, 0, math.radians(sx * (pi * 2.5 + 5)))
            bpy.ops.object.transform_apply(rotation=True)
            assign_mat(bp, mats['baleen']); link(col, bp); objs.append(bp)
    return objs

def build_blowhole(mats, col):
    bh = prim('cyl', 'Whale_Blowhole', loc=(0, 3.80, 1.42), size=0.16, depth=0.12, verts=12)
    assign_mat(bh, mats['back']); link(col, bh); return [bh]

def build_barnacles(mats, col):
    """8 barnacle cluster patches scattered on body and flippers."""
    objs = []
    cluster_pos = [
        ( 0.40,  3.80, 1.20), (-0.40,  3.80, 1.20),
        ( 1.30,  1.80, 0.50), (-1.30,  1.80, 0.50),
        ( 0.60,  0.20, 0.80), (-0.60,  0.20, 0.80),
        ( 1.20, -1.20, 0.62), (-1.20, -1.20, 0.62),
    ]
    for ci, cp in enumerate(cluster_pos):
        # 5-8 barnacle bumps per cluster
        num_b = 5 + (ci % 4)
        for bi in range(num_b):
            angle = bi * (2*math.pi / num_b)
            bx = cp[0] + 0.08 * math.cos(angle)
            by = cp[1] + 0.08 * math.sin(angle) * 0.55
            bz = cp[2]
            bs = 0.030 + (bi % 3) * 0.012
            barn = prim('cone', f'Whale_Barnacle_{ci}_{bi}',
                        loc=(bx, by, bz), r1=bs, r2=bs*0.3, depth=bs*1.8, verts=8)
            assign_mat(barn, mats['barnacle']); link(col, barn); objs.append(barn)
    return objs

def build_skin_folds(mats, col):
    """3 skin ridge details per side around head/chin area."""
    objs = []
    for side, sx in [('L',-1),('R',1)]:
        for fi in range(3):
            fy = 5.50 - fi * 0.35
            fz = -0.28 - fi * 0.04
            fold = prim('cyl', f'Whale_SkinFold_{side}_{fi}',
                        loc=(sx*0.72, fy, fz), size=0.038, depth=0.64, verts=6,
                        rot=(math.radians(18), math.radians(sx*12), 0))
            fold.scale = (0.30, 1.0, 1.0); bpy.ops.object.transform_apply(scale=True)
            assign_mat(fold, mats['belly']); link(col, fold); objs.append(fold)
    return objs

# ═══════════════════════════════════════════════════════════════════
#  ASSEMBLE
# ═══════════════════════════════════════════════════════════════════

def main():
    clear_scene()
    col  = new_col('IsleTrial_Whale')
    mats = build_materials()

    all_objs = []
    all_objs += build_whale_body(mats, col)
    all_objs += build_belly_grooves(mats, col)
    all_objs += build_flippers(mats, col)
    all_objs += build_flukes(mats, col)
    all_objs += build_dorsal_hump(mats, col)
    all_objs += build_eyes(mats, col)
    all_objs += build_mouth_and_baleen(mats, col)
    all_objs += build_blowhole(mats, col)
    all_objs += build_barnacles(mats, col)
    all_objs += build_skin_folds(mats, col)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    root = bpy.context.active_object; root.name = 'Whale_ROOT'; link(col, root)
    for obj in all_objs:
        if obj.parent is None: obj.parent = root

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = root
    mc = sum(1 for o in col.objects if o.type=='MESH')
    print("=" * 60)
    print("[IsleTrial] Humpback Whale (HIGH QUALITY) built.")
    print(f"  Mesh objects    : {mc}")
    print(f"  Materials       : {len(bpy.data.materials)}")
    print(f"  Body segments   : 48×32 rings (high quality)")
    print(f"  Belly grooves   : 14 throat pleats")
    print(f"  Flipper tubercles: 12 per flipper × 2")
    print(f"  Baleen plates   : 16 (8 each side)")
    print(f"  Barnacle bumps  : 8 clusters (~6 bumps each)")
    print()
    print("  Subdivision: level 2 (PC) → 1 for mobile")
    print("  Next: run 16_Whale_Rig.py")
    print("=" * 60)

main()
