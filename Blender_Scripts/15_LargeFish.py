"""
IsleTrial – Sea Creature 04-A: Large Fish  (HIGH QUALITY REBUILD)
==================================================================
Type    Tuna / Marlin hybrid — primary harpoon target
Size    2.5 m long × 0.60 m wide × 0.50 m tall
Poly    ~8 000–11 000 tris (PC); Sub level 1 → ~4 000 (mobile)

Parts built:
  Fish_Body           – bmesh 36×24 fusiform body, tapered peduncle
  Fish_ScaleRows      – 8 shimmer scale strip overlays on flanks
  Fish_DorsalFin      – bmesh triangular dorsal with 7 spine rods
  Fish_PectoralFin_L/R – bmesh swept-back wing fins, angled 20°
  Fish_PelvicFin_L/R  – small ventral fins
  Fish_AnalFin        – small fin opposite dorsal (rear belly)
  Fish_TailFin        – bmesh forked lunate tail (upper+lower lobes)
  Fish_TailKeel_L/R   – lateral keels at caudal peduncle
  Fish_Eye_L/R        – 3-layer (socket darkening / iris rings / pupil)
  Fish_JawUpper/Lower – open mouth geometry
  Fish_Teeth_Up/Lo    – 8 cone teeth each jaw
  Fish_LateralLine_L/R – groove overlay along full flank
  Fish_GillCover_L/R  – operculum plate with visible gill slit

Materials (full dual-path procedural + [UNITY] image slots):
  Mat_Fish_Body_Top    – deep blue-grey with voronoi scale pattern + Fresnel iridescence
  Mat_Fish_Body_Belly  – silver-white with subtle noise variation
  Mat_Fish_Fin         – translucent dark blue-grey, wave node vein detail
  Mat_Fish_Eye         – wet black sclera
  Mat_Fish_Iris        – voronoi ring iris + glow
  Mat_Fish_Tooth       – ivory with subsurface scatter

Run BEFORE 15_LargeFish_Rig.py  inside Blender ▸ Scripting tab.
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

def add_bevel(obj, w=0.008, s=2):
    m = obj.modifiers.new('Bev', 'BEVEL'); m.width = w; m.segments = s

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
    elif tp == 'torus':
        bpy.ops.mesh.primitive_torus_add(major_radius=kw.get('major',size),
            minor_radius=kw.get('minor',0.05), location=loc, rotation=rot,
            major_segments=kw.get('maj_seg',24), minor_segments=kw.get('min_seg',8))
    obj = bpy.context.active_object; obj.name = name; return obj

def assign_mat(obj, mat):
    if obj.data.materials: obj.data.materials[0] = mat
    else: obj.data.materials.append(mat)

# ═══════════════════════════════════════════════════════════════════
#  MATERIAL SYSTEM  – dual-path procedural + [UNITY] image slots
# ═══════════════════════════════════════════════════════════════════

def _n(nodes, ntype, loc, label=None):
    nd = nodes.new(ntype); nd.location = loc
    if label: nd.label = nd.name = label; return nd

def _img(nodes, sname, loc):
    nd = nodes.new('ShaderNodeTexImage'); nd.location = loc
    nd.label = nd.name = f'[UNITY] {sname}'; return nd

def _mapping(nodes, links, scale=(5,5,5), loc=(-900,0)):
    tc = _n(nodes, 'ShaderNodeTexCoord', (loc[0]-200, loc[1]))
    mp = _n(nodes, 'ShaderNodeMapping', loc)
    mp.inputs['Scale'].default_value = (*scale,)
    links.new(tc.outputs['UV'], mp.inputs['Vector']); return mp

def _mix_pi(nodes, links, proc, img_nd, loc):
    mix = _n(nodes, 'ShaderNodeMixRGB', loc); mix.blend_type = 'MIX'
    mix.inputs[0].default_value = 0.0
    links.new(proc, mix.inputs[1]); links.new(img_nd.outputs['Color'], mix.inputs[2]); return mix

def _bump_n(nodes, links, mp, scale=22.0, strength=0.40, loc=(-400,-400)):
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
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat, n, lk, bsdf

# ── Body top (iridescent blue-grey with voronoi scale shimmer) ────
def mat_fish_top(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(5,5,5))

    # Voronoi for scale cell pattern
    vor = _n(n, 'ShaderNodeTexVoronoi', (-700, 350))
    vor.inputs['Scale'].default_value = 28.0; vor.voronoi_dimensions = '3D'
    lk.new(mp.outputs['Vector'], vor.inputs['Vector'])

    # Noise for overall body colour variation
    noise = _n(n, 'ShaderNodeTexNoise', (-700, 150))
    noise.inputs['Scale'].default_value = 8.0; noise.inputs['Detail'].default_value = 8.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])

    # Wave for lateral stripe bands
    wave = _n(n, 'ShaderNodeTexWave', (-700, -50))
    wave.wave_type = 'BANDS'; wave.inputs['Scale'].default_value = 1.6
    wave.inputs['Distortion'].default_value = 0.8; wave.inputs['Detail'].default_value = 4.0
    lk.new(mp.outputs['Vector'], wave.inputs['Vector'])

    # Mix scale + noise
    mix_vn = _n(n, 'ShaderNodeMixRGB', (-400, 250))
    mix_vn.blend_type = 'OVERLAY'; mix_vn.inputs[0].default_value = 0.42
    lk.new(vor.outputs['Distance'], mix_vn.inputs[1])
    lk.new(noise.outputs['Fac'], mix_vn.inputs[2])

    # Mix with stripe wave
    mix_ws = _n(n, 'ShaderNodeMixRGB', (-200, 200))
    mix_ws.blend_type = 'MULTIPLY'; mix_ws.inputs[0].default_value = 0.28
    lk.new(mix_vn.outputs['Color'], mix_ws.inputs[1])
    lk.new(wave.outputs['Color'], mix_ws.inputs[2])

    # Colour ramp: deep blue-grey palette
    cr = _n(n, 'ShaderNodeValToRGB', (50, 200))
    cr.color_ramp.elements[0].color = (0.06, 0.14, 0.22, 1)   # deep #1A3A5A
    e1 = cr.color_ramp.elements.new(0.40); e1.color = (0.10, 0.22, 0.38, 1)
    cr.color_ramp.elements[1].color = (0.16, 0.32, 0.50, 1)
    lk.new(mix_ws.outputs['Color'], cr.inputs['Fac'])

    # Fresnel iridescent sheen
    fres = _n(n, 'ShaderNodeFresnel', (-400, 0)); fres.inputs['IOR'].default_value = 1.46
    cr2 = _n(n, 'ShaderNodeValToRGB', (-100, 0))
    cr2.color_ramp.elements[0].color = (0.06, 0.14, 0.22, 1)
    e2 = cr2.color_ramp.elements.new(0.55); e2.color = (0.20, 0.62, 0.82, 1)
    cr2.color_ramp.elements[1].color = (0.75, 0.95, 1.00, 1)
    lk.new(fres.outputs['Fac'], cr2.inputs['Fac'])

    # Screen blend: base + iridescence
    mix_fr = _n(n, 'ShaderNodeMixRGB', (300, 150))
    mix_fr.blend_type = 'SCREEN'; mix_fr.inputs[0].default_value = 0.38
    lk.new(cr.outputs['Color'], mix_fr.inputs[1])
    lk.new(cr2.outputs['Color'], mix_fr.inputs[2])

    img_a = _img(n, f'{name}_Albedo', (-700, -250))
    mix_c = _mix_pi(n, lk, mix_fr.outputs['Color'], img_a, (520, 100))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness: varied by scale cells
    mr = _n(n, 'ShaderNodeMapRange', (50, -100))
    mr.inputs['From Min'].default_value = 0.2; mr.inputs['From Max'].default_value = 0.8
    mr.inputs['To Min'].default_value = 0.28; mr.inputs['To Max'].default_value = 0.48
    lk.new(vor.outputs['Distance'], mr.inputs['Value'])
    lk.new(mr.outputs['Result'], bsdf.inputs['Roughness'])

    bsdf.inputs['Metallic'].default_value = 0.10
    bsdf.inputs['Specular IOR Level'].default_value = 0.60
    bmp = _bump_n(n, lk, mp, scale=28.0, strength=0.25)
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    return mat

# ── Belly (silver-white with soft variation) ──────────────────────
def mat_fish_belly(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(6,6,6))
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 200))
    noise.inputs['Scale'].default_value = 12.0; noise.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    vor = _n(n, 'ShaderNodeTexVoronoi', (-500, 0)); vor.inputs['Scale'].default_value = 22.0
    lk.new(mp.outputs['Vector'], vor.inputs['Vector'])
    mix_nv = _n(n, 'ShaderNodeMixRGB', (-250, 100)); mix_nv.blend_type = 'OVERLAY'; mix_nv.inputs[0].default_value = 0.20
    lk.new(noise.outputs['Fac'], mix_nv.inputs[1]); lk.new(vor.outputs['Distance'], mix_nv.inputs[2])
    cr = _n(n, 'ShaderNodeValToRGB', (-50, 100))
    cr.color_ramp.elements[0].color = (0.70, 0.68, 0.62, 1)   # #E8E0D0
    cr.color_ramp.elements[1].color = (0.92, 0.92, 0.88, 1)
    lk.new(mix_nv.outputs['Color'], cr.inputs['Fac'])
    img_a = _img(n, f'{name}_Albedo', (-500, -200))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.30
    bsdf.inputs['Metallic'].default_value = 0.08
    bsdf.inputs['Specular IOR Level'].default_value = 0.55
    return mat

# ── Fin (translucent with vein wave pattern) ──────────────────────
def mat_fin(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(10,10,10))
    wave = _n(n, 'ShaderNodeTexWave', (-600, 200)); wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = 8.0; wave.inputs['Distortion'].default_value = 2.5
    wave.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['Vector'], wave.inputs['Vector'])
    noise = _n(n, 'ShaderNodeTexNoise', (-600, 0)); noise.inputs['Scale'].default_value = 18.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    mix_wn = _n(n, 'ShaderNodeMixRGB', (-300, 100)); mix_wn.blend_type = 'MULTIPLY'; mix_wn.inputs[0].default_value = 0.45
    lk.new(wave.outputs['Color'], mix_wn.inputs[1]); lk.new(noise.outputs['Fac'], mix_wn.inputs[2])
    cr = _n(n, 'ShaderNodeValToRGB', (-50, 100))
    cr.color_ramp.elements[0].color = (0.04, 0.12, 0.22, 1)
    cr.color_ramp.elements[1].color = (0.12, 0.26, 0.42, 1)
    lk.new(mix_wn.outputs['Color'], cr.inputs['Fac'])
    img_a = _img(n, f'{name}_Albedo', (-600, -200))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.48
    bsdf.inputs['Transmission Weight'].default_value = 0.32
    bsdf.inputs['Alpha'].default_value = 0.80
    mat.blend_method = 'BLEND'
    bmp = _bump_n(n, lk, mp, scale=20.0, strength=0.22)
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    return mat

# ── Eye sclera (wet black) ────────────────────────────────────────
def mat_eye_sclera(name):
    mat, n, lk, bsdf = _base(name)
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['Specular IOR Level'].default_value = 1.0
    bsdf.inputs['Metallic'].default_value = 0.05
    return mat

# ── Iris (voronoi ring pattern + glow) ───────────────────────────
def mat_iris(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(4,4,4))
    vor = _n(n, 'ShaderNodeTexVoronoi', (-500, 200)); vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 22.0; lk.new(mp.outputs['Vector'], vor.inputs['Vector'])
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 0)); noise.inputs['Scale'].default_value = 30.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    mix_vi = _n(n, 'ShaderNodeMixRGB', (-250, 100)); mix_vi.blend_type = 'OVERLAY'; mix_vi.inputs[0].default_value = 0.30
    lk.new(vor.outputs['Distance'], mix_vi.inputs[1]); lk.new(noise.outputs['Fac'], mix_vi.inputs[2])
    cr = _n(n, 'ShaderNodeValToRGB', (-50, 100))
    cr.color_ramp.elements[0].color = (0.02, 0.12, 0.22, 1)   # dark centre
    e1 = cr.color_ramp.elements.new(0.35); e1.color = (0.06, 0.26, 0.44, 1)  # #3A6A8A
    cr.color_ramp.elements[1].color = (0.14, 0.50, 0.72, 1)
    lk.new(mix_vi.outputs['Color'], cr.inputs['Fac'])
    img_a = _img(n, f'{name}_Albedo', (-500, -200))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['Emission Color'].default_value = (0.06, 0.28, 0.44, 1)
    bsdf.inputs['Emission Strength'].default_value = 0.6
    return mat

# ── Tooth (ivory + SSS) ───────────────────────────────────────────
def mat_tooth(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(10,10,10))
    noise = _n(n, 'ShaderNodeTexNoise', (-400, 100)); noise.inputs['Scale'].default_value = 14.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-100, 100))
    cr.color_ramp.elements[0].color = (0.82, 0.80, 0.72, 1)
    cr.color_ramp.elements[1].color = (0.96, 0.94, 0.88, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    img_a = _img(n, f'{name}_Albedo', (-400, -200))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['Subsurface Weight'].default_value = 0.05
    bsdf.inputs['Subsurface Radius'].default_value = (0.85, 0.70, 0.55)
    return mat

# ── Gill / operculum (darker wet flesh) ───────────────────────────
def mat_gill(name):
    mat, n, lk, bsdf = _base(name)
    mp = _mapping(n, lk, scale=(8,8,8))
    noise = _n(n, 'ShaderNodeTexNoise', (-400, 100)); noise.inputs['Scale'].default_value = 18.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-100, 100))
    cr.color_ramp.elements[0].color = (0.28, 0.08, 0.05, 1)
    cr.color_ramp.elements[1].color = (0.45, 0.14, 0.08, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    img_a = _img(n, f'{name}_Albedo', (-400, -200))
    mix_c = _mix_pi(n, lk, cr.outputs['Color'], img_a, (200, 50))
    lk.new(mix_c.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.65
    bsdf.inputs['Subsurface Weight'].default_value = 0.08
    return mat

def build_materials():
    return {
        'top'    : mat_fish_top('Mat_Fish_Body_Top'),
        'belly'  : mat_fish_belly('Mat_Fish_Body_Belly'),
        'fin'    : mat_fin('Mat_Fish_Fin'),
        'eye_s'  : mat_eye_sclera('Mat_Fish_Eye'),
        'iris'   : mat_iris('Mat_Fish_Iris'),
        'tooth'  : mat_tooth('Mat_Fish_Tooth'),
        'gill'   : mat_gill('Mat_Fish_Gill'),
    }

# ═══════════════════════════════════════════════════════════════════
#  GEOMETRY
# ═══════════════════════════════════════════════════════════════════

def build_fish_body(mats, col):
    """bmesh 36×24 fusiform fish body with tapered peduncle and belly flatten."""
    objs = []
    bm = bmesh.new()
    segs = 36; rings = 24
    L = 1.25; W = 0.30; H = 0.25

    verts_grid = []
    for ri in range(rings + 1):
        t = ri / rings; y = -L + t * 2 * L
        # Fusiform width profile
        if t < 0.08:   w = W * (t/0.08) * 0.30
        elif t < 0.45: w = W * (0.30 + (t-0.08)/0.37 * 0.70)
        elif t < 0.65: w = W * 1.0
        elif t < 0.85: w = W * (1.0 - (t-0.65)/0.20 * 0.60)
        else:          w = W * max(0.05, 0.40 - (t-0.85)/0.15 * 0.35)
        # Height profile
        if t < 0.10:   h = H * (t/0.10) * 0.55
        elif t < 0.55: h = H * (0.55 + (t-0.10)/0.45 * 0.45)
        elif t < 0.72: h = H * 1.0
        elif t < 0.90: h = H * (1.0 - (t-0.72)/0.18 * 0.30)
        else:          h = H * max(0.08, 0.70 - (t-0.90)/0.10 * 0.62)
        ring = []
        for si in range(segs):
            a = 2 * math.pi * si / segs
            x = w * math.cos(a); z = h * math.sin(a)
            if z < 0: z *= 0.72   # flatten belly
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
    mesh = bpy.data.meshes.new('Fish_Body_Mesh'); bm.to_mesh(mesh); bm.free()
    body = bpy.data.objects.new('Fish_Body', mesh)
    bpy.context.scene.collection.objects.link(body)
    assign_mat(body, mats['top'])
    body.data.materials.append(mats['belly'])
    add_sub(body, 2); smart_uv(body); link(col, body); objs.append(body)

    # ── Scale rows (8 shimmer strips along flanks) ──
    scale_y_positions = [-0.80, -0.55, -0.30, -0.05, 0.18, 0.42, 0.65, 0.85]
    for i, sy in enumerate(scale_y_positions):
        t = (sy + 1.25) / 2.50
        # Body width at this Y position (approximated)
        if t < 0.65: sw = W * min(1.0, t/0.65)
        else:        sw = W * (1.0 - (t-0.65)/0.35 * 0.7)
        for side, sz_sign in [(1, 0.09), (-1, -0.09)]:
            sr = prim('torus', f'Fish_ScaleRow_{i}_{"R" if side>0 else "L"}',
                      loc=(0, sy, sz_sign), major=sw*0.85, minor=0.012,
                      maj_seg=28, min_seg=6)
            sr.scale = (1.0, 1.0, 0.25); bpy.ops.object.transform_apply(scale=True)
            assign_mat(sr, mats['top']); link(col, sr); objs.append(sr)

    # ── Lateral lines ──
    for side, sx in [('L', -0.295), ('R', 0.295)]:
        lat = prim('cyl', f'Fish_LateralLine_{side}', loc=(sx, 0, 0.04),
                   size=0.008, depth=2.18, verts=6, rot=(0, math.radians(90), 0))
        assign_mat(lat, mats['top']); link(col, lat); objs.append(lat)

    # ── Caudal peduncle keels (lateral keels at tail narrow) ──
    for side, sz in [('Up', 0.09), ('Lo', -0.09)]:
        keel = prim('cyl', f'Fish_TailKeel_{side}', loc=(0, -1.02, sz),
                    size=0.018, depth=0.30, verts=6, rot=(0, math.radians(90), 0))
        keel.scale = (0.30, 1.0, 1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(keel, mats['top']); link(col, keel); objs.append(keel)

    return objs

def build_dorsal_fin(mats, col):
    """bmesh dorsal with proper convex profile + 7 internal spine rods."""
    objs = []
    bm = bmesh.new()
    # More detailed dorsal profile (8 outline points)
    fin_pts = [
        Vector((0, -0.32, 0.00)),   # front base
        Vector((0, -0.26, 0.28)),   # front rise
        Vector((0, -0.10, 0.40)),   # peak front
        Vector((0,  0.02, 0.44)),   # peak top
        Vector((0,  0.18, 0.38)),   # peak rear
        Vector((0,  0.32, 0.22)),   # rear mid
        Vector((0,  0.36, 0.00)),   # rear base
    ]
    for pt in fin_pts: bm.verts.new(pt)
    bm.verts.ensure_lookup_table()
    # Triangulate the outline fan
    n_pts = len(fin_pts)
    base_idx = n_pts
    ctr = bm.verts.new(Vector((0, 0.02, 0.18)))   # interior centre
    for i in range(n_pts - 1):
        try: bm.faces.new([bm.verts[i], bm.verts[i+1], ctr])
        except: pass
    try: bm.faces.new([bm.verts[n_pts-1], bm.verts[0], ctr])
    except: pass
    mesh = bpy.data.meshes.new('Fish_DorsalFin_Mesh'); bm.to_mesh(mesh); bm.free()
    fin = bpy.data.objects.new('Fish_DorsalFin', mesh)
    fin.location = (0, -0.05, 0.24)
    bpy.context.scene.collection.objects.link(fin)
    assign_mat(fin, mats['fin']); add_solidify(fin, 0.015); add_sub(fin, 1)
    smart_uv(fin); link(col, fin); objs.append(fin)

    # 7 spine rods inside dorsal
    spine_positions = [-0.28,-0.16,-0.04,0.06,0.14,0.22,0.30]
    spine_heights   = [ 0.26, 0.36, 0.42,0.44,0.40,0.32,0.20]
    for i, (sy, sh) in enumerate(zip(spine_positions, spine_heights)):
        spine = prim('cyl', f'Fish_DorsalSpine_{i}', loc=(0, sy + 0.05, sh*0.5 + 0.24),
                     size=0.005, depth=sh, verts=6)
        assign_mat(spine, mats['fin']); link(col, spine); objs.append(spine)

    # Fin base ridge (raised line connecting front-rear base)
    ridge = prim('cyl', 'Fish_DorsalRidge', loc=(0, 0.02, 0.24),
                 size=0.018, depth=0.72, verts=6, rot=(0, math.radians(90), 0))
    assign_mat(ridge, mats['top']); link(col, ridge); objs.append(ridge)
    return objs

def build_pectoral_fins(mats, col):
    """bmesh swept-back pectoral fins with membrane detail."""
    objs = []
    for side, sx in [('R', 1), ('L', -1)]:
        bm = bmesh.new()
        # 8-point swept wing profile
        pts = [
            Vector((sx*0.00,  0.06,  0.00)),   # root front
            Vector((sx*0.00,  0.18,  0.00)),   # root rear
            Vector((sx*0.12,  0.32, -0.03)),
            Vector((sx*0.24,  0.46, -0.06)),
            Vector((sx*0.33,  0.58, -0.10)),
            Vector((sx*0.35,  0.52, -0.11)),   # tip
            Vector((sx*0.28,  0.36, -0.09)),
            Vector((sx*0.14,  0.18, -0.05)),
        ]
        for pt in pts: bm.verts.new(pt)
        bm.verts.ensure_lookup_table()
        n_pts = len(pts)
        for i in range(1, n_pts - 1):
            try: bm.faces.new([bm.verts[0], bm.verts[i], bm.verts[i+1]])
            except: pass
        try: bm.faces.new([bm.verts[0], bm.verts[n_pts-1], bm.verts[1]])
        except: pass
        mesh = bpy.data.meshes.new(f'Fish_PectoralFin_{side}_Mesh')
        bm.to_mesh(mesh); bm.free()
        fin = bpy.data.objects.new(f'Fish_PectoralFin_{side}', mesh)
        fin.location = (sx*0.28, 0.38, -0.04)
        fin.rotation_euler = (0, math.radians(-20), 0)
        bpy.context.scene.collection.objects.link(fin)
        assign_mat(fin, mats['fin']); add_solidify(fin, 0.010); add_sub(fin, 1)
        smart_uv(fin); link(col, fin); objs.append(fin)

        # 4 pectoral fin spine rods
        for sri in range(4):
            t_s = 0.20 + sri * 0.20
            spt = Vector((sx*0.00,0.06,0.00)).lerp(Vector((sx*0.35,0.52,-0.11)), t_s)
            sroot = Vector((sx*0.00,0.18,0.00)).lerp(Vector((sx*0.00,0.06,0.00)), t_s*0.5)
            sp = prim('cyl', f'Fish_PecSpine_{side}_{sri}',
                      loc=(fin.location[0]+spt.x, fin.location[1]+spt.y, fin.location[2]+spt.z),
                      size=0.004, depth=0.10, verts=6)
            assign_mat(sp, mats['fin']); link(col, sp); objs.append(sp)

    return objs

def build_tail_fin(mats, col):
    """bmesh lunate (crescent) tail fin with upper + lower lobes."""
    objs = []
    bm = bmesh.new()
    ty = -1.25
    # Upper lobe
    upper = [
        Vector((0,    ty,       0.00)),
        Vector((0,    ty-0.06,  0.08)),
        Vector((0.08, ty-0.20,  0.24)),
        Vector((0.12, ty-0.34,  0.40)),
        Vector((0.14, ty-0.44,  0.50)),   # tip
        Vector((0.06, ty-0.48,  0.52)),
        Vector((-0.02,ty-0.40,  0.46)),
        Vector((-0.04,ty-0.24,  0.28)),
        Vector((0,    ty-0.10,  0.14)),
    ]
    # Lower lobe (mirror)
    lower = [
        Vector((0,    ty-0.06, -0.08)),
        Vector((0.08, ty-0.20, -0.24)),
        Vector((0.12, ty-0.34, -0.40)),
        Vector((0.14, ty-0.44, -0.50)),   # tip
        Vector((0.06, ty-0.48, -0.52)),
        Vector((-0.02,ty-0.40, -0.46)),
        Vector((-0.04,ty-0.24, -0.28)),
        Vector((0,    ty-0.10, -0.14)),
    ]
    all_pts = upper + lower
    for pt in all_pts: bm.verts.new(pt)
    bm.verts.ensure_lookup_table()
    bmesh.ops.convex_hull(bm, input=bm.verts)
    mesh = bpy.data.meshes.new('Fish_TailFin_Mesh'); bm.to_mesh(mesh); bm.free()
    tail = bpy.data.objects.new('Fish_TailFin', mesh)
    bpy.context.scene.collection.objects.link(tail)
    assign_mat(tail, mats['fin']); add_solidify(tail, 0.012); add_sub(tail, 1)
    smart_uv(tail); link(col, tail); objs.append(tail)

    # Tail fin central spar
    spar = prim('cyl', 'Fish_TailSpar', loc=(0, ty-0.22, 0),
                size=0.014, depth=0.48, verts=6, rot=(math.radians(90), 0, 0))
    assign_mat(spar, mats['top']); link(col, spar); objs.append(spar)

    # Pelvic fins
    for side, sx in [('L',-0.12),('R',0.12)]:
        pv = prim('cyl', f'Fish_PelvicFin_{side}', loc=(sx, 0.10, -0.22),
                  size=0.058, depth=0.004, verts=10)
        pv.scale = (0.8, 2.4, 1.0); pv.rotation_euler = (0, math.radians(-18), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(pv, mats['fin']); add_solidify(pv, 0.008); smart_uv(pv); link(col, pv); objs.append(pv)

    # Anal fin
    bm2 = bmesh.new()
    af = [Vector((0,-0.90,-0.20)),Vector((0,-1.05,-0.30)),Vector((0,-1.18,-0.22)),Vector((0,-0.96,-0.16))]
    for pt in af: bm2.verts.new(pt)
    bm2.verts.ensure_lookup_table(); bm2.faces.new([bm2.verts[0],bm2.verts[1],bm2.verts[2],bm2.verts[3]])
    mesh2 = bpy.data.meshes.new('Fish_AnalFin_Mesh'); bm2.to_mesh(mesh2); bm2.free()
    anal = bpy.data.objects.new('Fish_AnalFin', mesh2)
    bpy.context.scene.collection.objects.link(anal)
    assign_mat(anal, mats['fin']); add_solidify(anal, 0.010); smart_uv(anal); link(col, anal); objs.append(anal)
    return objs

def build_eyes(mats, col):
    """3-layer eye: socket darkening sphere / iris ring disc / pupil."""
    objs = []
    for side, sx in [('L', -0.22), ('R', 0.22)]:
        ex, ey, ez = sx, 0.82, 0.08
        # Orbit socket (darkening sphere behind eye)
        sock = prim('sphere', f'Fish_EyeSocket_{side}', loc=(ex, ey-0.008, ez), size=0.052, segs=14, rings=10)
        sock.scale = (1.0, 0.60, 1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(sock, mats['eye_s']); link(col, sock); objs.append(sock)
        # Eye sclera
        eye = prim('sphere', f'Fish_Eye_{side}', loc=(ex, ey+0.006, ez), size=0.040, segs=14, rings=10)
        eye.scale = (1.0, 0.55, 1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(eye, mats['eye_s']); link(col, eye); objs.append(eye)
        # Iris disc
        iris = prim('cyl', f'Fish_Iris_{side}', loc=(ex, ey+0.032, ez), size=0.028,
                    depth=0.006, verts=14, rot=(math.radians(90), 0, 0))
        assign_mat(iris, mats['iris']); link(col, iris); objs.append(iris)
        # Pupil (small dark disc)
        pupil = prim('cyl', f'Fish_Pupil_{side}', loc=(ex, ey+0.038, ez), size=0.014,
                     depth=0.004, verts=10, rot=(math.radians(90), 0, 0))
        assign_mat(pupil, mats['eye_s']); link(col, pupil); objs.append(pupil)
        # Specular highlight
        hi_mat = bpy.data.materials.new(f'Mat_EyeHi_{side}')
        hi_mat.use_nodes = True; hi_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(1,1,1,1)
        hi = prim('sphere', f'Fish_EyeHi_{side}', loc=(ex+sx*0.006, ey+0.042, ez+0.008), size=0.005, segs=6, rings=4)
        assign_mat(hi, hi_mat); link(col, hi); objs.append(hi)
    return objs

def build_mouth_and_jaw(mats, col):
    """Open mouth with upper/lower jaw geometry and 8+8 teeth."""
    objs = []
    # Upper jaw
    jaw_up = prim('cyl', 'Fish_JawUpper', loc=(0, 1.20, -0.02), size=0.068, depth=0.030, verts=22)
    jaw_up.scale = (1.0, 1.0, 0.44); bpy.ops.object.transform_apply(scale=True)
    assign_mat(jaw_up, mats['top']); smart_uv(jaw_up); link(col, jaw_up); objs.append(jaw_up)

    # Lower jaw (angled down)
    jaw_lo = prim('cyl', 'Fish_JawLower', loc=(0, 1.18, -0.10), size=0.058, depth=0.024, verts=22)
    jaw_lo.scale = (1.0, 1.0, 0.38); jaw_lo.rotation_euler=(math.radians(14),0,0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    assign_mat(jaw_lo, mats['belly']); smart_uv(jaw_lo); link(col, jaw_lo); objs.append(jaw_lo)

    # Mouth interior (visible gum)
    interior = prim('sphere', 'Fish_Mouth_Interior', loc=(0, 1.16, -0.05), size=0.12, segs=14, rings=10)
    interior.scale = (0.88, 0.55, 0.42); bpy.ops.object.transform_apply(scale=True)
    assign_mat(interior, mats['gill']); link(col, interior); objs.append(interior)

    # Upper teeth (8)
    for i in range(8):
        ta = math.radians(-28 + i * 8)
        tx = 0.052 * math.sin(ta)
        tooth = prim('cone', f'Fish_ToothUp_{i}', loc=(tx, 1.205, 0.00),
                     r1=0.008, r2=0.001, depth=0.028, verts=4, rot=(math.radians(-10),0,0))
        assign_mat(tooth, mats['tooth']); link(col, tooth); objs.append(tooth)

    # Lower teeth (8)
    for i in range(8):
        ta = math.radians(-24 + i * 8)
        tx = 0.045 * math.sin(ta)
        tooth = prim('cone', f'Fish_ToothLo_{i}', loc=(tx, 1.200, -0.08),
                     r1=0.007, r2=0.001, depth=0.025, verts=4, rot=(math.radians(165),0,0))
        assign_mat(tooth, mats['tooth']); link(col, tooth); objs.append(tooth)
    return objs

def build_gill_covers(mats, col):
    """Operculum plates + visible gill slits (3 per side)."""
    objs = []
    for side, sx in [('L',-1),('R',1)]:
        # Operculum plate
        gc = prim('sphere', f'Fish_GillCover_{side}', loc=(sx*0.24, 0.62, 0.02), size=0.18, segs=16, rings=12)
        gc.scale = (0.55, 0.72, 0.88); bpy.ops.object.transform_apply(scale=True)
        assign_mat(gc, mats['top']); add_sub(gc, 1); smart_uv(gc); link(col, gc); objs.append(gc)

        # Gill slit lines (3 thin arcs behind operculum)
        for gi in range(3):
            gz = 0.06 - gi * 0.06
            gs = prim('cyl', f'Fish_GillSlit_{side}_{gi}',
                      loc=(sx*0.26, 0.54 - gi*0.04, gz),
                      size=0.005, depth=0.18, verts=6,
                      rot=(math.radians(72), math.radians(sx*12), 0))
            assign_mat(gs, mats['gill']); link(col, gs); objs.append(gs)
    return objs

# ═══════════════════════════════════════════════════════════════════
#  ASSEMBLE
# ═══════════════════════════════════════════════════════════════════

def main():
    clear_scene()
    col  = new_col('IsleTrial_Fish')
    mats = build_materials()

    all_objs = []
    all_objs += build_fish_body(mats, col)
    all_objs += build_dorsal_fin(mats, col)
    all_objs += build_pectoral_fins(mats, col)
    all_objs += build_tail_fin(mats, col)
    all_objs += build_eyes(mats, col)
    all_objs += build_mouth_and_jaw(mats, col)
    all_objs += build_gill_covers(mats, col)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    root = bpy.context.active_object; root.name = 'Fish_ROOT'; link(col, root)
    for obj in all_objs:
        if obj.parent is None: obj.parent = root

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = root
    mc = sum(1 for o in col.objects if o.type=='MESH')
    print("=" * 60)
    print("[IsleTrial] Large Fish (HIGH QUALITY) built.")
    print(f"  Mesh objects : {mc}")
    print(f"  Materials    : {len(bpy.data.materials)}")
    print(f"  Body segments: 36×24 rings (high quality)")
    print(f"  Scale rows   : 16 shimmer strips on flanks")
    print(f"  Teeth        : 8 upper + 8 lower")
    print(f"  Gill covers  : operculum + 3 slits per side")
    print()
    print("  Subdivision: level 2 (PC) → 1 for mobile")
    print("  Next: run 15_LargeFish_Rig.py")
    print("=" * 60)

main()
