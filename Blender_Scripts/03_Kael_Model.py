"""
IsleTrial – Player Character: Kael  (03_Kael_Model.py)  [REBUILT]
==================================================================
Spec    Player_and_Boat/Player_Kael_Spec.md
Height  1.8 m  (feet at Z=0, head top at Z=1.80)
Pose    T-pose  (arms horizontal, facing +Y)
Polys   ~5,000–8,000 triangles target

Body parts:
  Head .............. bmesh oval skull + brow ledge + chin definition
  Face features ..... bmesh nose bridge + nostrils + mouth line + cheek pads
  Ears .............. bmesh flat ear shapes (L+R)
  Eyes .............. 3-layer per eye: sclera / iris+emission / pupil
  Neck .............. cylinder + adam's apple stub
  Neck bandana ...... thin cloth ring at base of neck (sailor detail)
  Torso underlayer .. body under coat
  Coat torso ........ main coat body (navy blue)
  Coat panels ....... front-left + front-right lapel flap panels
  Collar ............ raised coat collar
  Epaulettes ........ shoulder pads L+R (cone-disc shapes)
  Breast pocket ..... flap + seam line (left chest)
  Upper sleeves ..... coat fabric upper arm L+R
  Rolled cuffs ...... fold-back cuff band (darker coat fabric)
  Bare forearms ..... skin visible below rolled cuffs L+R
  Coat tails ........ bmesh flared coat-tail panels hanging at back (L+R)
  Shoulder trim ..... gold braid strip on each shoulder
  Gloves ............ fingerless palm + knuckle pads + 4 finger stubs + thumb
  Pants ............. thigh + shin panels (L+R)
  Boots ............. upper + toe-cap + heel block + sole + fold cuff + strap buckle (L+R)
  Belt .............. strap + 6 punch holes + brass buckle plate + 4 belt loops
  Side pouch ........ pouch body + flap + clasp stud + 2 rivets
  Compass pendant ... brass case + bezel torus + glass lens + 8-pt rose + needle + 6 chain links
  Hair .............. cap + 8 directional windswept tufts + 2 sideburn wisps
  Cutlass blade ..... bmesh curved pirate blade with fuller groove + spine ridge
  Cutlass guard ..... quillon bar + D-guard half-ring (bmesh arc)
  Cutlass grip ...... cylinder + 4 leather wrap bands + cord knot
  Cutlass pommel .... flattened sphere
  Scabbard .......... leather body + tip cap + throat collar torus

Materials (dual-path procedural + [UNITY] image texture slots):
  Skin, Coat, Undershirt, Pants, Boot, Belt, Glove,
  Brass, Iron, BladeSteel, Hair, Eye_Iris, Eye_White, Compass

Run BEFORE 03_Kael_Rig.py  inside Blender ▸ Scripting tab.
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(0xAE7D32)

# ─────────────────────────────────────────────────────────────────────────────
#  SCENE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def new_col(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def link(col, obj):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def add_sub(obj, lv=2):
    m = obj.modifiers.new('Sub', 'SUBSURF')
    m.levels = lv; m.render_levels = lv

def add_bevel(obj, w=0.008, s=2):
    m = obj.modifiers.new('Bev', 'BEVEL')
    m.width = w; m.segments = s

def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)

def new_mesh_obj(name, bm, col):
    me = bpy.data.meshes.new(name + '_Mesh')
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob

def prim(tp, name, loc=(0, 0, 0), rot=(0, 0, 0), size=1.0, **kw):
    if tp == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=size, location=loc, rotation=rot,
            segments=kw.get('segs', 20), ring_count=kw.get('rings', 14))
    elif tp == 'cyl':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=size, depth=kw.get('depth', 1.0),
            location=loc, rotation=rot, vertices=kw.get('verts', 16))
    elif tp == 'cone':
        bpy.ops.mesh.primitive_cone_add(
            radius1=kw.get('r1', size), radius2=kw.get('r2', 0),
            depth=kw.get('depth', 1.0), location=loc, rotation=rot,
            vertices=kw.get('verts', 12))
    elif tp == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=size, location=loc, rotation=rot)
    elif tp == 'torus':
        bpy.ops.mesh.primitive_torus_add(
            major_radius=kw.get('major', size), minor_radius=kw.get('minor', 0.06),
            location=loc, rotation=rot,
            major_segments=kw.get('maj_seg', 24), minor_segments=kw.get('min_seg', 8))
    elif tp == 'plane':
        bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def assign_mat(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# ─────────────────────────────────────────────────────────────────────────────
#  MATERIAL SYSTEM  (dual-path: procedural + [UNITY] image texture slots)
# ─────────────────────────────────────────────────────────────────────────────

def _n(nodes, ntype, loc, label=None):
    nd = nodes.new(ntype)
    nd.location = loc
    if label:
        nd.label = nd.name = label
    return nd

def _img(nodes, slot_name, loc):
    nd = nodes.new('ShaderNodeTexImage')
    nd.location = loc
    nd.label = nd.name = f'[UNITY] {slot_name}'
    return nd

def _mapping(nodes, links, scale=(6, 6, 6), loc=(-900, 0)):
    tc = _n(nodes, 'ShaderNodeTexCoord', (loc[0] - 200, loc[1]))
    mp = _n(nodes, 'ShaderNodeMapping', loc)
    mp.inputs['Scale'].default_value = (*scale,)
    links.new(tc.outputs['UV'], mp.inputs['Vector'])
    return mp

def _mix_pi(nodes, links, proc_sock, img_nd, mix_loc):
    mix = _n(nodes, 'ShaderNodeMixRGB', mix_loc)
    mix.blend_type = 'MIX'
    mix.inputs[0].default_value = 0.0
    links.new(proc_sock, mix.inputs[1])
    links.new(img_nd.outputs['Color'], mix.inputs[2])
    return mix

def _bump(nodes, links, mp, scale=20.0, strength=0.4, loc=(-400, -400)):
    bn = _n(nodes, 'ShaderNodeTexNoise', loc)
    bn.inputs['Scale'].default_value = scale
    links.new(mp.outputs['Vector'], bn.inputs['Vector'])
    bmp = _n(nodes, 'ShaderNodeBump', (loc[0] + 300, loc[1]))
    bmp.inputs['Strength'].default_value = strength
    links.new(bn.outputs['Fac'], bmp.inputs['Height'])
    return bmp

def _base_mat(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    n = mat.node_tree.nodes
    lk = mat.node_tree.links
    n.clear()
    bsdf = _n(n, 'ShaderNodeBsdfPrincipled', (400, 0))
    out = _n(n, 'ShaderNodeOutputMaterial', (700, 0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat, n, lk, bsdf

# ── Skin  ─────────────────────────────────────────────────────────────────────
def build_skin_mat(name):
    mat, n, lk, bsdf = _base_mat(name)
    mp = _mapping(n, lk, scale=(5, 5, 5))
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 200))
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.55
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    vor = _n(n, 'ShaderNodeTexVoronoi', (-500, 0))
    vor.inputs['Scale'].default_value = 20.0
    lk.new(mp.outputs['Vector'], vor.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-180, 200))
    cr.color_ramp.elements[0].color = (0.66, 0.40, 0.22, 1)
    cr.color_ramp.elements[1].color = (0.83, 0.58, 0.38, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    overlay = _n(n, 'ShaderNodeMixRGB', (-50, 100))
    overlay.blend_type = 'OVERLAY'
    overlay.inputs[0].default_value = 0.08
    lk.new(cr.outputs['Color'], overlay.inputs[1])
    lk.new(vor.outputs['Color'], overlay.inputs[2])
    img = _img(n, f'{name}_Albedo', (-500, -220))
    mix = _mix_pi(n, lk, overlay.outputs['Color'], img, (200, 120))
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bmp = _bump(n, lk, mp, scale=18.0, strength=0.22)
    img_n = _img(n, f'{name}_Normal', (-400, -520))
    nm = _n(n, 'ShaderNodeNormalMap', (-100, -480))
    lk.new(img_n.outputs['Color'], nm.inputs['Color'])
    mix_n = _n(n, 'ShaderNodeMixRGB', (50, -460))
    mix_n.inputs[0].default_value = 0.0
    lk.new(bmp.outputs['Normal'], mix_n.inputs[1])
    lk.new(nm.outputs['Normal'], mix_n.inputs[2])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.72
    bsdf.inputs['Subsurface Weight'].default_value = 0.05
    bsdf.inputs['Subsurface Radius'].default_value = (0.82, 0.36, 0.22)
    return mat

# ── Cloth  ────────────────────────────────────────────────────────────────────
def build_cloth_mat(name, dark, light, roughness=0.88):
    mat, n, lk, bsdf = _base_mat(name)
    mp = _mapping(n, lk, scale=(9, 9, 9))
    wave = _n(n, 'ShaderNodeTexWave', (-500, 200))
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = 7.0
    wave.inputs['Distortion'].default_value = 1.4
    wave.inputs['Detail'].default_value = 4.0
    lk.new(mp.outputs['Vector'], wave.inputs['Vector'])
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 0))
    noise.inputs['Scale'].default_value = 40.0
    noise.inputs['Detail'].default_value = 2.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-200, 200))
    cr.color_ramp.elements[0].color = (*dark, 1)
    cr.color_ramp.elements[1].color = (*light, 1)
    lk.new(wave.outputs['Color'], cr.inputs['Fac'])
    wear = _n(n, 'ShaderNodeMixRGB', (-80, 100))
    wear.blend_type = 'MULTIPLY'
    wear.inputs[0].default_value = 0.12
    lk.new(cr.outputs['Color'], wear.inputs[1])
    lk.new(noise.outputs['Fac'], wear.inputs[2])
    img = _img(n, f'{name}_Albedo', (-500, -220))
    mix = _mix_pi(n, lk, wear.outputs['Color'], img, (200, 120))
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bmp = _bump(n, lk, mp, scale=28.0, strength=0.32)
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Sheen Weight'].default_value = 0.18
    return mat

# ── Leather ───────────────────────────────────────────────────────────────────
def build_leather_mat(name, base=(0.28, 0.14, 0.06)):
    mat, n, lk, bsdf = _base_mat(name)
    mp = _mapping(n, lk, scale=(11, 11, 11))
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 200))
    noise.inputs['Scale'].default_value = 18.0
    noise.inputs['Roughness'].default_value = 0.68
    noise.inputs['Detail'].default_value = 5.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    vor = _n(n, 'ShaderNodeTexVoronoi', (-500, 0))
    vor.inputs['Scale'].default_value = 28.0
    lk.new(mp.outputs['Vector'], vor.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-200, 200))
    cr.color_ramp.elements[0].color = (*[x * 0.62 for x in base], 1)
    cr.color_ramp.elements[1].color = (*base, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    grain = _n(n, 'ShaderNodeMixRGB', (-60, 90))
    grain.blend_type = 'SCREEN'
    grain.inputs[0].default_value = 0.06
    lk.new(cr.outputs['Color'], grain.inputs[1])
    lk.new(vor.outputs['Color'], grain.inputs[2])
    img = _img(n, f'{name}_Albedo', (-500, -220))
    mix = _mix_pi(n, lk, grain.outputs['Color'], img, (200, 120))
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bmp = _bump(n, lk, mp, scale=26.0, strength=0.52)
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.64
    bsdf.inputs['Specular IOR Level'].default_value = 0.28
    return mat

# ── Metal (brass / iron) ─────────────────────────────────────────────────────
def build_metal_mat(name, base=(0.72, 0.52, 0.16), roughness=0.28):
    mat, n, lk, bsdf = _base_mat(name)
    mp = _mapping(n, lk, scale=(14, 14, 14))
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 100))
    noise.inputs['Scale'].default_value = 35.0
    noise.inputs['Detail'].default_value = 3.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    mr = _n(n, 'ShaderNodeMapRange', (-200, 100))
    mr.inputs['From Min'].default_value = 0.3
    mr.inputs['From Max'].default_value = 0.7
    mr.inputs['To Min'].default_value = roughness - 0.10
    mr.inputs['To Max'].default_value = roughness + 0.14
    lk.new(noise.outputs['Fac'], mr.inputs['Value'])
    lk.new(mr.outputs['Result'], bsdf.inputs['Roughness'])
    rgb = _n(n, 'ShaderNodeRGB', (-200, -60))
    rgb.outputs[0].default_value = (*base, 1)
    img = _img(n, f'{name}_Albedo', (-500, -220))
    mix = _mix_pi(n, lk, rgb.outputs['Color'], img, (200, 10))
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = 0.92
    return mat

# ── Blade Steel  ──────────────────────────────────────────────────────────────
def build_blade_mat(name):
    mat, n, lk, bsdf = _base_mat(name)
    mp = _mapping(n, lk, scale=(16, 16, 16))
    wave = _n(n, 'ShaderNodeTexWave', (-500, 200))
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 24.0
    wave.inputs['Distortion'].default_value = 0.4
    lk.new(mp.outputs['Vector'], wave.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-200, 200))
    cr.color_ramp.elements[0].color = (0.08, 0.09, 0.10, 1)
    cr.color_ramp.elements[1].color = (0.68, 0.72, 0.78, 1)
    lk.new(wave.outputs['Color'], cr.inputs['Fac'])
    img = _img(n, f'{name}_Albedo', (-500, -220))
    mix = _mix_pi(n, lk, cr.outputs['Color'], img, (200, 120))
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.14
    bsdf.inputs['Anisotropic'].default_value = 0.40
    return mat

# ── Hair  ─────────────────────────────────────────────────────────────────────
def build_hair_mat(name):
    mat, n, lk, bsdf = _base_mat(name)
    mp = _mapping(n, lk, scale=(14, 14, 14))
    wave = _n(n, 'ShaderNodeTexWave', (-500, 200))
    wave.inputs['Scale'].default_value = 12.0
    wave.inputs['Distortion'].default_value = 3.5
    wave.inputs['Detail'].default_value = 4.0
    lk.new(mp.outputs['Vector'], wave.inputs['Vector'])
    noise = _n(n, 'ShaderNodeTexNoise', (-500, 0))
    noise.inputs['Scale'].default_value = 22.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-200, 200))
    cr.color_ramp.elements[0].color = (0.16, 0.07, 0.02, 1)
    cr.color_ramp.elements[1].color = (0.40, 0.22, 0.07, 1)
    lk.new(wave.outputs['Color'], cr.inputs['Fac'])
    hlt = _n(n, 'ShaderNodeMixRGB', (-60, 80))
    hlt.blend_type = 'ADD'
    hlt.inputs[0].default_value = 0.04
    lk.new(cr.outputs['Color'], hlt.inputs[1])
    lk.new(noise.outputs['Fac'], hlt.inputs[2])
    img = _img(n, f'{name}_Albedo', (-500, -220))
    mix = _mix_pi(n, lk, hlt.outputs['Color'], img, (200, 120))
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.78
    bsdf.inputs['Specular IOR Level'].default_value = 0.48
    return mat

# ── Eye White  ────────────────────────────────────────────────────────────────
def build_eye_white_mat(name):
    mat, n, lk, bsdf = _base_mat(name)
    bsdf.inputs['Base Color'].default_value = (0.95, 0.94, 0.92, 1)
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Specular IOR Level'].default_value = 0.40
    return mat

# ── Eye Iris (with emission glow)  ────────────────────────────────────────────
def build_eye_iris_mat(name, iris_color=(0.12, 0.30, 0.58)):
    mat, n, lk, bsdf = _base_mat(name)
    mp = _mapping(n, lk, scale=(4, 4, 4))
    vor = _n(n, 'ShaderNodeTexVoronoi', (-500, 200))
    vor.inputs['Scale'].default_value = 8.0
    lk.new(mp.outputs['Vector'], vor.inputs['Vector'])
    cr = _n(n, 'ShaderNodeValToRGB', (-200, 200))
    cr.color_ramp.elements[0].color = (*[x * 0.50 for x in iris_color], 1)
    cr.color_ramp.elements[1].color = (*iris_color, 1)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    img = _img(n, f'{name}_Albedo', (-500, -220))
    mix = _mix_pi(n, lk, cr.outputs['Color'], img, (200, 120))
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Emission Color'].default_value = (*iris_color, 1)
    bsdf.inputs['Emission Strength'].default_value = 0.30
    bsdf.inputs['Roughness'].default_value = 0.05
    return mat

# ── Compass glow  ─────────────────────────────────────────────────────────────
def build_compass_mat(name):
    mat, n, lk, bsdf = _base_mat(name)
    bsdf.inputs['Base Color'].default_value = (0.78, 0.65, 0.22, 1)
    bsdf.inputs['Metallic'].default_value = 0.96
    bsdf.inputs['Roughness'].default_value = 0.16
    bsdf.inputs['Emission Color'].default_value = (0.50, 0.75, 1.00, 1)
    bsdf.inputs['Emission Strength'].default_value = 1.0
    return mat

def build_materials():
    return {
        'skin':       build_skin_mat('Mat_Kael_Skin'),
        'coat':       build_cloth_mat('Mat_Kael_Coat',
                          dark=(0.04, 0.07, 0.20), light=(0.09, 0.13, 0.32), roughness=0.85),
        'undershirt': build_cloth_mat('Mat_Kael_Undershirt',
                          dark=(0.70, 0.64, 0.50), light=(0.86, 0.80, 0.66), roughness=0.92),
        'pants':      build_cloth_mat('Mat_Kael_Pants',
                          dark=(0.48, 0.38, 0.16), light=(0.66, 0.54, 0.26), roughness=0.90),
        'boot':       build_leather_mat('Mat_Kael_Boot',    base=(0.22, 0.10, 0.04)),
        'belt':       build_leather_mat('Mat_Kael_Belt',    base=(0.24, 0.11, 0.04)),
        'glove':      build_leather_mat('Mat_Kael_Glove',   base=(0.30, 0.15, 0.05)),
        'brass':      build_metal_mat('Mat_Kael_Brass',     base=(0.72, 0.52, 0.16), roughness=0.26),
        'iron':       build_metal_mat('Mat_Kael_Iron',      base=(0.18, 0.16, 0.14), roughness=0.46),
        'blade':      build_blade_mat('Mat_Kael_BladeSteel'),
        'hair':       build_hair_mat('Mat_Kael_Hair'),
        'eye_white':  build_eye_white_mat('Mat_Kael_Eye_White'),
        'eye_iris':   build_eye_iris_mat('Mat_Kael_Eye_Iris'),
        'compass':    build_compass_mat('Mat_Kael_Compass'),
        'gold':       build_metal_mat('Mat_Kael_Gold', base=(0.88, 0.68, 0.10), roughness=0.18),
    }

# ─────────────────────────────────────────────────────────────────────────────
#  GEOMETRY
#
#  Z layout  (T-pose facing +Y):
#    0.00 – 0.04   boot sole bottom
#    0.04 – 0.56   boot upper
#    0.56 – 0.90   shin (under boot cuff)
#    0.90 – 1.30   thigh
#    1.30 – 1.52   hips / pelvis
#    1.52 – 1.88   torso
#    1.88 – 1.96   neck
#    1.96 – 2.22   head (center 2.08)
#    2.14 – 2.25   hair cap top
#
#  T-pose arm (X-positive = right):
#    Shoulder  X=±0.20, Z=1.90
#    Elbow     X=±0.74, Z=1.80
#    Wrist     X=±1.22, Z=1.72
#    Hand-tip  X=±1.42, Z=1.68
# ─────────────────────────────────────────────────────────────────────────────

# ── HEAD  ─────────────────────────────────────────────────────────────────────
def build_head(mats, col):
    """bmesh oval skull with brow ledge, cheekbone bulge, chin taper."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=22, v_segments=16, radius=0.148)
    # Sculpt-like vertex moves: brow forward, chin slight point, cheeks wider
    for v in bm.verts:
        z, y, x = v.co.z, v.co.y, v.co.x
        # Narrow Y axis (head slightly flat front-back)
        v.co.y = y * 0.87
        # Taller Z axis
        v.co.z = z * 1.10
        # Brow ridge: push forward verts at brow height
        if 0.072 < v.co.z < 0.115 and v.co.y < -0.05 and abs(v.co.x) < 0.10:
            v.co.y -= 0.008
            v.co.z += 0.005
        # Chin: slight forward + downward taper
        if v.co.z < -0.10 and v.co.y < -0.02:
            v.co.y -= 0.006
        # Cheekbones: widen slightly
        if -0.04 < v.co.z < 0.06 and v.co.y < -0.08 and abs(v.co.x) > 0.06:
            v.co.x *= 1.06
    # Translate to final head centre Z=2.08
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((0, 0, 2.08)))
    head = new_mesh_obj('Kael_Head', bm, col)
    assign_mat(head, mats['skin'])
    add_sub(head, 2)
    smart_uv(head)
    return [head]

# ── FACE FEATURES  ────────────────────────────────────────────────────────────
def build_face_features(mats, col):
    """Nose bridge + nostrils + brow pads + mouth line + chin pad."""
    objs = []

    # Nose bridge – small cone angled outward
    nose = prim('cone', 'Kael_NoseBridge',
                loc=(0, -0.150, 2.048),
                r1=0.020, r2=0.009, depth=0.028, verts=8,
                rot=(math.radians(82), 0, 0))
    assign_mat(nose, mats['skin']); objs.append(nose)

    # Nostril wings (L+R) – small flattened spheres
    for sx in (-0.013, 0.013):
        nos = prim('sphere', f'Kael_Nostril_{"L" if sx < 0 else "R"}',
                   loc=(sx, -0.157, 2.032), size=0.013, segs=10, rings=6)
        nos.scale = (1.0, 0.42, 0.62)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(nos, mats['skin']); objs.append(nos)

    # Brow pads (subtle): L+R small flattened oblongs above eye socket
    for sx in (-0.058, 0.058):
        brow = prim('sphere', f'Kael_Brow_{"L" if sx < 0 else "R"}',
                    loc=(sx, -0.140, 2.128), size=0.030, segs=10, rings=6)
        brow.scale = (2.0, 0.25, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(brow, mats['skin']); objs.append(brow)

    # Mouth line – very thin elongated cube just below nose
    mouth = prim('cube', 'Kael_MouthLine', loc=(0, -0.153, 2.012), size=0.007)
    mouth.scale = (5.0, 0.50, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(mouth, mats['skin']); objs.append(mouth)

    # Lower lip pad
    lip = prim('sphere', 'Kael_LowerLip', loc=(0, -0.152, 2.000),
               size=0.016, segs=10, rings=6)
    lip.scale = (2.2, 0.45, 0.65)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(lip, mats['skin']); objs.append(lip)

    # Chin dimple pad
    chin = prim('sphere', 'Kael_Chin', loc=(0, -0.144, 1.982),
                size=0.020, segs=10, rings=6)
    chin.scale = (1.5, 0.50, 0.70)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(chin, mats['skin']); objs.append(chin)

    return objs

# ── EARS  ─────────────────────────────────────────────────────────────────────
def build_ears(mats, col):
    """Flat ear shapes – bmesh half-oval with lobe extension."""
    objs = []
    for side, sx in [('R', 0.150), ('L', -0.150)]:
        bm = bmesh.new()
        # Outer ear ring (8 verts)
        ring = []
        for i in range(8):
            a = math.radians(i * 45.0 - 90.0)
            ring.append(bm.verts.new(Vector((0.0,
                                             math.sin(a) * 0.024,
                                             math.cos(a) * 0.032))))
        # Inner hollow center (slightly inset on X)
        center = bm.verts.new(Vector((-0.006, 0.0, 0.004)))
        bm.verts.ensure_lookup_table()
        # Fan faces from center
        for i in range(8):
            bm.faces.new([ring[i], ring[(i + 1) % 8], center])
        # Ear lobe tab
        lobe = bm.verts.new(Vector((0.0, 0.0, -0.045)))
        bm.faces.new([ring[5], ring[6], lobe])
        bm.faces.new([ring[6], ring[7], lobe])
        # Inner rim fold tube (solidify via translate)
        bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((sx, -0.020, 2.055)))
        ob = new_mesh_obj(f'Kael_Ear_{side}', bm, col)
        # Flip normal for L ear
        if sx < 0:
            ob.scale.x = -1.0
            bpy.ops.object.transform_apply(scale=True)
        assign_mat(ob, mats['skin'])
        smart_uv(ob)
        objs.append(ob)
    return objs

# ── EYES (3-layer)  ───────────────────────────────────────────────────────────
def build_eyes(mats, col):
    """3 layers per eye: sclera sphere, iris disc, pupil disc."""
    objs = []
    for side, sx in [('R', 0.064), ('L', -0.064)]:
        # Sclera
        sclera = prim('sphere', f'Kael_Sclera_{side}',
                      loc=(sx, -0.138, 2.100), size=0.030, segs=14, rings=10)
        sclera.scale = (1.0, 0.38, 0.74)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(sclera, mats['eye_white']); smart_uv(sclera)
        objs.append(sclera)
        # Iris
        iris = prim('cyl', f'Kael_Iris_{side}',
                    loc=(sx, -0.145, 2.100), size=0.017, depth=0.004, verts=16)
        iris.scale = (1.0, 0.22, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(iris, mats['eye_iris']); smart_uv(iris)
        objs.append(iris)
        # Pupil
        pupil = prim('cyl', f'Kael_Pupil_{side}',
                     loc=(sx, -0.147, 2.100), size=0.008, depth=0.003, verts=12)
        pupil.scale = (1.0, 0.22, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        mat_pu, np, lkp, bp = _base_mat(f'Mat_Kael_Pupil_{side}')
        bp.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
        bp.inputs['Roughness'].default_value = 0.05
        assign_mat(pupil, mat_pu)
        objs.append(pupil)
    return objs

# ── NECK + BANDANA  ───────────────────────────────────────────────────────────
def build_neck(mats, col):
    objs = []
    neck = prim('cyl', 'Kael_Neck', loc=(0, 0, 1.920), size=0.055, depth=0.18, verts=14)
    assign_mat(neck, mats['skin']); smart_uv(neck); objs.append(neck)
    # Adam's apple stub
    aa = prim('sphere', 'Kael_AdamsApple', loc=(0, -0.048, 1.906),
              size=0.014, segs=8, rings=6)
    aa.scale = (0.85, 1.0, 0.70)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(aa, mats['skin']); objs.append(aa)
    # Sailor's bandana at collar line
    band = prim('torus', 'Kael_Bandana', loc=(0, 0, 1.885),
                major=0.060, minor=0.012,
                maj_seg=20, min_seg=6,
                rot=(0, 0, 0))
    band.scale = (1.0, 0.82, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(band, mats['undershirt']); objs.append(band)
    # Bandana knot (front)
    knot = prim('sphere', 'Kael_BandanaKnot', loc=(0, -0.062, 1.886),
                size=0.014, segs=8, rings=6)
    knot.scale = (1.6, 0.80, 0.90)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(knot, mats['undershirt']); objs.append(knot)
    return objs

# ── COAT MAIN TORSO  ──────────────────────────────────────────────────────────
def build_coat_torso(mats, col):
    """Main coat body – chest/back panels, front V-opening, collar, tails."""
    objs = []

    # Main coat torso cylinder
    torso = prim('cyl', 'Kael_CoatTorso', loc=(0, 0, 1.660),
                 size=0.195, depth=0.70, verts=22)
    torso.scale = (1.0, 0.72, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(torso, mats['coat']); add_sub(torso, 1); smart_uv(torso)
    objs.append(torso)

    # Undershirt V-strip (front chest gap)
    chest_v = prim('cube', 'Kael_ChestVee', loc=(0, -0.147, 1.755), size=0.062)
    chest_v.scale = (1.0, 0.18, 2.60)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(chest_v, mats['undershirt']); objs.append(chest_v)

    # Left + right front panel flaps
    for sx in (-0.055, 0.055):
        panel = prim('cube', f'Kael_CoatPanel_{"L" if sx < 0 else "R"}',
                     loc=(sx, -0.151, 1.760), size=0.054)
        panel.scale = (1.55, 0.20, 2.60)
        panel.rotation_euler = (0, 0, math.radians(8) * (-1 if sx < 0 else 1))
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(panel, mats['coat']); objs.append(panel)

    # Collar raised ring
    collar = prim('cyl', 'Kael_Collar', loc=(0, 0, 1.890),
                  size=0.074, depth=0.065, verts=18)
    collar.scale = (1.0, 0.76, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(collar, mats['coat']); smart_uv(collar); objs.append(collar)

    # Collar back fold (slight extra ring behind)
    col_back = prim('cyl', 'Kael_CollarBack', loc=(0, 0.030, 1.896),
                    size=0.072, depth=0.040, verts=14)
    col_back.scale = (1.0, 0.5, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(col_back, mats['coat']); objs.append(col_back)

    return objs

# ── COAT TAILS (bmesh)  ───────────────────────────────────────────────────────
def build_coat_tails(mats, col):
    """Two flared coat-tail panels hanging from the back of the coat."""
    objs = []
    for side, sx in [('R', 0.065), ('L', -0.065)]:
        bm = bmesh.new()
        # Tail shape: quad with wider bottom + slight flare
        # Top-inner, Top-outer, Bottom-outer (flared), Bottom-inner (flared)
        v0 = bm.verts.new(Vector((sx - 0.04,  0.055,  1.310)))   # top-inner
        v1 = bm.verts.new(Vector((sx + 0.04,  0.050,  1.320)))   # top-outer
        v2 = bm.verts.new(Vector((sx + 0.072, 0.060,  0.920)))   # bot-outer
        v3 = bm.verts.new(Vector((sx - 0.018, 0.058,  0.900)))   # bot-inner
        # Mid verts for gentle S-curve
        vm = bm.verts.new(Vector((sx + 0.020, 0.056,  1.120)))   # mid-outer
        bm.verts.ensure_lookup_table()
        bm.faces.new([v0, v1, vm, v3])
        bm.faces.new([v3, vm, v2, bm.verts.new(
            Vector((sx - 0.018, 0.058, 0.980)))])
        bm.faces.new([v3, bm.verts[-1], v2,
                      bm.verts.new(Vector((sx - 0.016, 0.058, 0.900)))])
        bm.normal_update()
        ob = new_mesh_obj(f'Kael_CoatTail_{side}', bm, col)
        m = ob.modifiers.new('Sub', 'SUBSURF')
        m.levels = 1; m.render_levels = 1
        assign_mat(ob, mats['coat']); smart_uv(ob)
        objs.append(ob)
    return objs

# ── EPAULETTES + SHOULDER TRIM  ───────────────────────────────────────────────
def build_epaulettes(mats, col):
    objs = []
    for side, sx in [('R', 0.20), ('L', -0.20)]:
        # Shoulder pad base – flattened half-cone
        ep_base = prim('cone', f'Kael_Epaulette_{side}',
                       loc=(sx, 0, 1.905), r1=0.072, r2=0.055, depth=0.028, verts=16,
                       rot=(math.radians(90) * (-1 if sx > 0 else 1), 0, 0))
        ep_base.scale = (1.0, 0.45, 1.0)
        bpy.ops.object.transform_apply(scale=True, rotation=False)
        assign_mat(ep_base, mats['coat']); smart_uv(ep_base); objs.append(ep_base)

        # Gold braid strip across top of shoulder
        braid = prim('cyl', f'Kael_ShoulderBraid_{side}',
                     loc=(sx, 0, 1.905), size=0.056, depth=0.010, verts=14,
                     rot=(math.radians(90) * (-1 if sx > 0 else 1), 0, 0))
        braid.scale = (1.0, 0.42, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(braid, mats['gold']); objs.append(braid)

        # Shoulder decoration studs (3 per side)
        for i in range(3):
            a = math.radians(i * 28 - 28)
            stud_x = sx + math.cos(a) * 0.050
            stud_z = 1.905 + math.sin(a) * 0.014
            stud = prim('sphere', f'Kael_Stud_{side}_{i}',
                        loc=(stud_x, -0.045, stud_z), size=0.006, segs=8, rings=6)
            assign_mat(stud, mats['gold']); objs.append(stud)
    return objs

# ── BREAST POCKET  ────────────────────────────────────────────────────────────
def build_breast_pocket(mats, col):
    objs = []
    # Pocket flap
    flap = prim('cube', 'Kael_BreastPocketFlap', loc=(-0.10, -0.152, 1.796), size=0.032)
    flap.scale = (1.55, 0.22, 0.82)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(flap, mats['coat']); add_bevel(flap, 0.004, 2); objs.append(flap)
    # Pocket seam line (thin cube)
    seam = prim('cube', 'Kael_BreastPocketSeam', loc=(-0.10, -0.153, 1.810), size=0.002)
    seam.scale = (25.0, 0.5, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(seam, mats['iron']); objs.append(seam)
    # Pocket stud button
    btn = prim('cyl', 'Kael_PocketBtn', loc=(-0.10, -0.155, 1.796),
               size=0.007, depth=0.008, verts=10)
    assign_mat(btn, mats['brass']); objs.append(btn)
    return objs

# ── SLEEVES + CUFFS  ──────────────────────────────────────────────────────────
def build_sleeves(mats, col):
    objs = []
    for side, sx in [('R', 1), ('L', -1)]:
        # Upper sleeve (coat fabric)
        sl = prim('cyl', f'Kael_Sleeve_{side}',
                  loc=(sx * 0.50, 0, 1.848), size=0.056, depth=0.58,
                  rot=(0, math.radians(90), 0), verts=14)
        assign_mat(sl, mats['coat']); add_sub(sl, 1); smart_uv(sl)
        objs.append(sl)

        # Rolled cuff band (slightly larger diameter, darker shade)
        cuff = prim('cyl', f'Kael_Cuff_{side}',
                    loc=(sx * 0.835, 0, 1.830), size=0.060, depth=0.082,
                    rot=(0, math.radians(90), 0), verts=14)
        assign_mat(cuff, mats['coat']); objs.append(cuff)

        # Undershirt visible at cuff edge
        cuff_shirt = prim('cyl', f'Kael_CuffShirt_{side}',
                          loc=(sx * 0.870, 0, 1.826), size=0.058, depth=0.022,
                          rot=(0, math.radians(90), 0), verts=14)
        assign_mat(cuff_shirt, mats['undershirt']); objs.append(cuff_shirt)

        # Sleeve gold trim stripe near cuff
        trim = prim('torus', f'Kael_SleeveTrim_{side}',
                    loc=(sx * 0.790, 0, 1.830),
                    major=0.060, minor=0.004,
                    maj_seg=16, min_seg=6,
                    rot=(0, math.radians(90), 0))
        assign_mat(trim, mats['gold']); objs.append(trim)

    return objs

# ── BARE FOREARMS  ────────────────────────────────────────────────────────────
def build_forearms(mats, col):
    objs = []
    for side, sx in [('R', 1), ('L', -1)]:
        fa = prim('cyl', f'Kael_BareArm_{side}',
                  loc=(sx * 0.988, 0, 1.770), size=0.038, depth=0.48,
                  rot=(0, math.radians(90), 0), verts=12)
        assign_mat(fa, mats['skin']); smart_uv(fa); objs.append(fa)
        # Wrist bone bump
        wb = prim('sphere', f'Kael_WristBump_{side}',
                  loc=(sx * 1.188, 0, 1.756), size=0.018, segs=8, rings=6)
        wb.scale = (0.40, 0.80, 0.70)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(wb, mats['skin']); objs.append(wb)
    return objs

# ── GLOVES + HANDS  ───────────────────────────────────────────────────────────
def build_gloves_hands(mats, col):
    objs = []
    for side, sx in [('R', 1), ('L', -1)]:
        # Palm – fingerless glove body
        palm = prim('sphere', f'Kael_Palm_{side}',
                    loc=(sx * 1.312, 0, 1.724), size=0.060, segs=14, rings=10)
        palm.scale = (0.64, 0.54, 0.92)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(palm, mats['glove']); smart_uv(palm); objs.append(palm)

        # Knuckle pad ridge
        knuck = prim('cyl', f'Kael_KnucklePad_{side}',
                     loc=(sx * 1.342, -0.008, 1.734), size=0.042, depth=0.014,
                     rot=(0, math.radians(90), 0), verts=12)
        knuck.scale = (1.0, 1.0, 0.30)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(knuck, mats['glove']); objs.append(knuck)

        # Exposed skin fingertips (4 fingers)
        for fi in range(4):
            fa = fi - 1.5
            fx = sx * (1.375 + fi * 0.008)
            fz = 1.720 - abs(fa) * 0.016
            ftip = prim('cone', f'Kael_FingerTip_{side}_{fi}',
                        loc=(fx, fa * 0.010, fz), r1=0.014, r2=0.008, depth=0.040, verts=8,
                        rot=(0, math.radians(90) * sx, 0))
            assign_mat(ftip, mats['skin']); objs.append(ftip)

        # Thumb
        thumb = prim('sphere', f'Kael_Thumb_{side}',
                     loc=(sx * 1.302, -0.028, 1.660), size=0.018, segs=10, rings=8)
        thumb.scale = (0.70, 0.90, 1.40)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(thumb, mats['skin']); objs.append(thumb)

    return objs

# ── PANTS + LEGS  ─────────────────────────────────────────────────────────────
def build_pants_legs(mats, col):
    objs = []
    for side, sx in [('R', 0.10), ('L', -0.10)]:
        # Thigh
        thigh = prim('cyl', f'Kael_Thigh_{side}', loc=(sx, 0, 1.110),
                     size=0.110, depth=0.78, verts=14)
        assign_mat(thigh, mats['pants']); add_sub(thigh, 1); smart_uv(thigh)
        objs.append(thigh)
        # Inner thigh seam line
        seam = prim('cube', f'Kael_ThighSeam_{side}',
                    loc=(sx * 0.60, 0, 1.110), size=0.004)
        seam.scale = (0.5, 0.5, 95.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(seam, mats['pants']); objs.append(seam)
        # Shin
        shin = prim('cyl', f'Kael_Shin_{side}', loc=(sx, 0, 0.660),
                    size=0.082, depth=0.48, verts=12)
        assign_mat(shin, mats['pants']); add_sub(shin, 1); smart_uv(shin)
        objs.append(shin)
        # Pant cuff tuck at boot-top
        cuff = prim('cyl', f'Kael_PantCuff_{side}', loc=(sx, 0, 0.430),
                    size=0.088, depth=0.042, verts=12)
        assign_mat(cuff, mats['pants']); objs.append(cuff)
    return objs

# ── BOOTS  ────────────────────────────────────────────────────────────────────
def build_boots(mats, col):
    objs = []
    for side, sx in [('R', 0.10), ('L', -0.10)]:
        # Main boot upper shaft
        boot_up = prim('cyl', f'Kael_BootUpper_{side}', loc=(sx, 0, 0.310),
                       size=0.089, depth=0.500, verts=14)
        assign_mat(boot_up, mats['boot']); add_sub(boot_up, 1); smart_uv(boot_up)
        objs.append(boot_up)

        # Boot fold-over cuff at top
        fold = prim('cyl', f'Kael_BootFold_{side}', loc=(sx, 0, 0.562),
                    size=0.094, depth=0.058, verts=14)
        assign_mat(fold, mats['boot']); objs.append(fold)

        # Toe cap – rounded front extension
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.052)
        for v in bm.verts:
            v.co.y = v.co.y * 1.55  # elongate forward
            v.co.z = v.co.z * 0.50  # flatten vertically
            if v.co.z < -0.018:
                v.co.z = -0.018      # flat sole plane
        bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((sx, -0.040, 0.054)))
        toe = new_mesh_obj(f'Kael_BootToe_{side}', bm, col)
        assign_mat(toe, mats['boot']); smart_uv(toe); objs.append(toe)

        # Boot sole (elongated flat disc)
        sole = prim('cyl', f'Kael_BootSole_{side}', loc=(sx, -0.010, 0.025),
                    size=0.090, depth=0.048, verts=14)
        sole.scale = (1.0, 1.46, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(sole, mats['iron']); add_bevel(sole, 0.010, 2); smart_uv(sole)
        objs.append(sole)

        # Heel block
        heel = prim('cube', f'Kael_Heel_{side}', loc=(sx, 0.056, 0.042), size=0.058)
        heel.scale = (1.50, 0.72, 0.80)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(heel, mats['boot']); add_bevel(heel, 0.008, 2); objs.append(heel)

        # Boot buckle strap (small horizontal strap mid-boot)
        strap = prim('cube', f'Kael_BootStrap_{side}',
                     loc=(sx, -0.042, 0.290), size=0.010)
        strap.scale = (9.20, 0.60, 0.50)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(strap, mats['belt']); objs.append(strap)

        # Buckle hardware
        buckle_h = prim('cube', f'Kael_BootBuckle_{side}',
                        loc=(sx - 0.074 * (1 if sx > 0 else -1), -0.044, 0.290), size=0.012)
        buckle_h.scale = (1.0, 0.40, 1.60)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(buckle_h, mats['brass']); objs.append(buckle_h)

    return objs

# ── BELT  ─────────────────────────────────────────────────────────────────────
def build_belt(mats, col):
    objs = []
    # Belt strap ring
    belt = prim('cyl', 'Kael_Belt', loc=(0, 0, 1.342), size=0.200, depth=0.048, verts=24)
    belt.scale = (1.0, 0.74, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(belt, mats['belt']); add_bevel(belt, 0.008, 2); smart_uv(belt)
    objs.append(belt)

    # Brass buckle plate (front centre)
    buckle = prim('cube', 'Kael_Buckle', loc=(0, -0.152, 1.342), size=0.030)
    buckle.scale = (2.20, 0.38, 1.60)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(buckle, mats['brass']); add_bevel(buckle, 0.004, 2); objs.append(buckle)

    # Buckle pin bar
    pin = prim('cube', 'Kael_BucklePin', loc=(0, -0.155, 1.342), size=0.004)
    pin.scale = (1.0, 0.40, 8.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(pin, mats['iron']); objs.append(pin)

    # Belt loops (6 positions around strap)
    for bx in (-0.16, -0.09, -0.02, 0.02, 0.09, 0.16):
        loop = prim('torus', f'Kael_BeltLoop_{int(bx*100)}',
                    loc=(bx, -0.148, 1.342), major=0.010, minor=0.003,
                    maj_seg=12, min_seg=5)
        assign_mat(loop, mats['belt']); objs.append(loop)

    # Belt punch holes (5 small cylinders recessed into belt front)
    for i, bx in enumerate([-0.080, -0.040, 0.000, 0.040, 0.080]):
        hole = prim('cyl', f'Kael_BeltHole_{i}',
                    loc=(bx, -0.154, 1.315), size=0.004, depth=0.010, verts=8,
                    rot=(math.radians(90), 0, 0))
        mat_h, nh, lkh, bh = _base_mat(f'Mat_Kael_BeltHole')
        bh.inputs['Base Color'].default_value = (0.04, 0.02, 0.01, 1)
        assign_mat(hole, mat_h); objs.append(hole)

    return objs

# ── SIDE POUCH  ───────────────────────────────────────────────────────────────
def build_pouch(mats, col):
    objs = []
    # Pouch body
    body = prim('cube', 'Kael_Pouch', loc=(-0.178, -0.116, 1.232), size=0.055)
    body.scale = (1.22, 0.72, 1.62)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(body, mats['belt']); add_bevel(body, 0.008, 2); smart_uv(body)
    objs.append(body)

    # Pouch flap
    flap = prim('cube', 'Kael_PouchFlap', loc=(-0.178, -0.148, 1.306), size=0.052)
    flap.scale = (1.28, 0.22, 0.58)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(flap, mats['belt']); add_bevel(flap, 0.006, 2); objs.append(flap)

    # Clasp stud
    clasp = prim('sphere', 'Kael_PouchClasp', loc=(-0.178, -0.152, 1.290),
                 size=0.010, segs=8, rings=6)
    assign_mat(clasp, mats['brass']); objs.append(clasp)

    # Rivets (2)
    for dx in (-0.030, 0.030):
        riv = prim('sphere', f'Kael_PouchRivet_{int(dx*100)}',
                   loc=(-0.178 + dx, -0.118, 1.285), size=0.007, segs=8, rings=6)
        assign_mat(riv, mats['brass']); objs.append(riv)

    return objs

# ── COMPASS PENDANT  ──────────────────────────────────────────────────────────
def build_compass_pendant(mats, col):
    """Detailed compass: brass case disc + bezel + glass + 8-pt rose + needle."""
    objs = []
    cx, cy, cz = 0.082, -0.155, 1.208

    # Main brass case (disc)
    case = prim('cyl', 'Kael_CompassCase', loc=(cx, cy, cz),
                size=0.030, depth=0.016, verts=20)
    assign_mat(case, mats['brass']); smart_uv(case); objs.append(case)

    # Bezel outer ring (torus around edge)
    bezel = prim('torus', 'Kael_CompassBezel', loc=(cx, cy, cz),
                 major=0.030, minor=0.006,
                 maj_seg=20, min_seg=8,
                 rot=(math.radians(90), 0, 0))
    assign_mat(bezel, mats['brass']); objs.append(bezel)

    # Glass lens face (clear thin disc)
    glass = prim('cyl', 'Kael_CompassGlass', loc=(cx, cy - 0.009, cz),
                 size=0.026, depth=0.003, verts=20)
    mat_gl, ng, lkg, bg = _base_mat('Mat_Kael_Glass')
    bg.inputs['Base Color'].default_value = (0.85, 0.95, 1.0, 1)
    bg.inputs['Transmission Weight'].default_value = 0.90
    bg.inputs['Roughness'].default_value = 0.02
    assign_mat(glass, mat_gl); objs.append(glass)

    # Compass rose face (8 cardinal points – bmesh star)
    bm = bmesh.new()
    centre_v = bm.verts.new(Vector((cx, cy - 0.012, cz)))
    rose_pts = []
    for i in range(8):
        a = math.radians(i * 45.0)
        r = 0.022 if i % 2 == 0 else 0.014
        rose_pts.append(bm.verts.new(
            Vector((cx + math.cos(a) * r, cy - 0.011, cz + math.sin(a) * r))))
    bm.verts.ensure_lookup_table()
    for i in range(8):
        bm.faces.new([centre_v, rose_pts[i], rose_pts[(i + 1) % 8]])
    rose = new_mesh_obj('Kael_CompassRose', bm, col)
    assign_mat(rose, mats['compass']); smart_uv(rose); objs.append(rose)

    # Compass needle (elongated diamond, glowing)
    needle = prim('cone', 'Kael_CompassNeedle',
                  loc=(cx, cy - 0.014, cz), r1=0.004, r2=0, depth=0.022, verts=6,
                  rot=(0, 0, math.radians(22)))
    assign_mat(needle, mats['compass']); objs.append(needle)
    needle_s = prim('cone', 'Kael_CompassNeedle_S',
                    loc=(cx, cy - 0.014, cz), r1=0.003, r2=0, depth=0.014, verts=6,
                    rot=(0, 0, math.radians(22 + 180)))
    mat_ns, nns, lns, bns = _base_mat('Mat_Kael_NeedleSouth')
    bns.inputs['Base Color'].default_value = (0.85, 0.08, 0.06, 1)
    bns.inputs['Emission Color'].default_value = (1.0, 0.1, 0.06, 1)
    bns.inputs['Emission Strength'].default_value = 0.8
    assign_mat(needle_s, mat_ns); objs.append(needle_s)

    # Case hinge tab at top
    hinge = prim('cyl', 'Kael_CompassHinge', loc=(cx, cy, cz + 0.032),
                 size=0.005, depth=0.014, verts=8)
    assign_mat(hinge, mats['brass']); objs.append(hinge)

    # Chain links (6 flat tori climbing up to belt)
    for i in range(6):
        lz = cz + 0.034 + i * 0.016
        lrot = (0, math.radians(90) if i % 2 == 0 else 0, 0)
        link_o = prim('torus', f'Kael_ChainLink_{i}',
                      loc=(cx, cy, lz), major=0.008, minor=0.003,
                      maj_seg=10, min_seg=5, rot=lrot)
        assign_mat(link_o, mats['brass']); objs.append(link_o)

    return objs

# ── HAIR  ─────────────────────────────────────────────────────────────────────
def build_hair(mats, col):
    objs = []
    # Main hair cap
    cap = prim('sphere', 'Kael_HairCap', loc=(0, 0.010, 2.170), size=0.155, segs=20, rings=14)
    cap.scale = (1.0, 0.86, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(cap, mats['hair']); add_sub(cap, 1); smart_uv(cap)
    objs.append(cap)

    # Directional windswept tufts (8 tufts, swept toward +X right side)
    tuft_data = [
        ('FwdLeft',   (-0.065, -0.118, 2.230), (0.38, 0.72, 0.44)),
        ('FwdCentre', ( 0.020, -0.124, 2.236), (0.48, 0.68, 0.40)),
        ('FwdRight',  ( 0.090, -0.115, 2.224), (0.56, 0.66, 0.38)),
        ('SideRight', ( 0.148,  0.032, 2.212), (0.28, 0.92, 0.44)),
        ('SideRight2',( 0.140,  0.010, 2.196), (0.38, 0.88, 0.38)),
        ('BackLeft',  (-0.080,  0.120, 2.200), (0.50, 0.82, 0.40)),
        ('TopCentre', ( 0.036, -0.028, 2.262), (0.36, 0.60, 0.52)),
        ('TopRight',  ( 0.080,  0.018, 2.248), (0.44, 0.62, 0.46)),
    ]
    for tname, tloc, tscl in tuft_data:
        t = prim('sphere', f'Kael_HairTuft_{tname}', loc=tloc, size=0.046, segs=10, rings=8)
        t.scale = tscl
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(t, mats['hair']); objs.append(t)

    # Sideburn wisps
    for sx, slabel in [(-0.120, 'L'), (0.120, 'R')]:
        wisp = prim('sphere', f'Kael_HairWisp_{slabel}',
                    loc=(sx, -0.056, 2.026), size=0.028, segs=8, rings=6)
        wisp.scale = (0.56, 0.44, 1.30)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(wisp, mats['hair']); objs.append(wisp)

    # Nape strand at back of neck
    nape = prim('sphere', 'Kael_HairNape', loc=(0, 0.080, 1.956),
                size=0.036, segs=8, rings=6)
    nape.scale = (0.60, 0.50, 1.60)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(nape, mats['hair']); objs.append(nape)

    return objs

# ── CUTLASS (bmesh curved blade)  ────────────────────────────────────────────
def build_cutlass(mats, col):
    """Curved pirate cutlass: bmesh blade + fuller + D-guard + grip + pommel."""
    objs = []

    # ── Blade (bmesh) ──
    bm = bmesh.new()
    # 12 cross-section stations along blade: (offset_along_blade, half_width, half_thick, curve_fwd)
    stations = [
        (0.000, 0.025, 0.007, 0.000),   # 0 base at guard
        (0.060, 0.025, 0.006, 0.006),
        (0.120, 0.024, 0.006, 0.014),
        (0.180, 0.023, 0.005, 0.022),
        (0.240, 0.022, 0.005, 0.030),
        (0.300, 0.020, 0.004, 0.038),
        (0.370, 0.018, 0.004, 0.044),
        (0.430, 0.015, 0.003, 0.048),
        (0.500, 0.012, 0.003, 0.050),
        (0.560, 0.008, 0.002, 0.050),
        (0.610, 0.004, 0.001, 0.048),   # near tip
        (0.640, 0.001, 0.001, 0.046),   # tip
    ]
    bx0, by0, bz0 = -0.132, -0.112, 1.310
    loops = []
    for (u, hw, ht, cy) in stations:
        bz = bz0 + u
        by_cur = by0 + cy
        v0 = bm.verts.new(Vector((bx0 - hw, by_cur - ht, bz)))   # edge-bottom
        v1 = bm.verts.new(Vector((bx0 + hw, by_cur - ht, bz)))   # spine-bottom
        v2 = bm.verts.new(Vector((bx0 + hw, by_cur + ht, bz)))   # spine-top
        v3 = bm.verts.new(Vector((bx0 - hw, by_cur + ht, bz)))   # edge-top
        loops.append((v0, v1, v2, v3))
    bm.verts.ensure_lookup_table()
    # Side faces
    for i in range(len(loops) - 1):
        a, b = loops[i], loops[i + 1]
        bm.faces.new([a[0], b[0], b[1], a[1]])
        bm.faces.new([a[1], b[1], b[2], a[2]])
        bm.faces.new([a[2], b[2], b[3], a[3]])
        bm.faces.new([a[3], b[3], b[0], a[0]])
    # Base cap
    bm.faces.new([loops[0][0], loops[0][1], loops[0][2], loops[0][3]])
    # Tip cap
    tip = loops[-1]
    bm.faces.new([tip[0], tip[1], tip[2], tip[3]])
    blade_ob = new_mesh_obj('Kael_CutlassBlade', bm, col)
    assign_mat(blade_ob, mats['blade'])
    add_bevel(blade_ob, 0.002, 1)
    smart_uv(blade_ob)
    objs.append(blade_ob)

    # ── Fuller groove (thin spine strip)  ──
    full_bm = bmesh.new()
    for (u, hw, ht, cy) in stations[:-3]:
        bz = bz0 + u
        by_cur = by0 + cy
        v_a = full_bm.verts.new(Vector((bx0 + hw + 0.002, by_cur - 0.002, bz)))
        v_b = full_bm.verts.new(Vector((bx0 + hw + 0.002, by_cur + 0.002, bz)))
    verts = list(full_bm.verts)
    full_bm.verts.ensure_lookup_table()
    for i in range(len(verts) // 2 - 1):
        idx = i * 2
        full_bm.faces.new([verts[idx], verts[idx + 2], verts[idx + 3], verts[idx + 1]])
    fuller = new_mesh_obj('Kael_BladeFuller', full_bm, col)
    mat_fu, nfu, lkfu, bfu = _base_mat('Mat_Kael_Fuller')
    bfu.inputs['Base Color'].default_value = (0.05, 0.06, 0.08, 1)
    bfu.inputs['Metallic'].default_value = 1.0
    bfu.inputs['Roughness'].default_value = 0.22
    assign_mat(fuller, mat_fu)
    objs.append(fuller)

    # ── Quillon cross-guard bar  ──
    guard = prim('cube', 'Kael_Quillon', loc=(bx0, by0, bz0 + 0.000), size=0.018)
    guard.scale = (3.80, 0.52, 0.46)
    guard.rotation_euler = (0, 0, 0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(guard, mats['brass']); add_bevel(guard, 0.004, 2)
    objs.append(guard)

    # ── D-guard ring (bmesh half torus arc)  ──
    dg_bm = bmesh.new()
    n_seg = 16
    major_r = 0.048
    minor_r = 0.007
    for i in range(n_seg + 1):
        a = math.radians(i * 180.0 / n_seg)    # 0 to 180 degrees
        cx_d = bx0 + math.cos(a) * major_r
        cz_d = bz0 + math.sin(a) * major_r - major_r * 0.50
        for j in range(8):
            b = math.radians(j * 45.0)
            vx = cx_d + math.cos(b) * minor_r
            vz = cz_d + math.sin(b) * minor_r
            dg_bm.verts.new(Vector((vx, by0, vz)))
    dg_bm.verts.ensure_lookup_table()
    cols_d = n_seg + 1
    for i in range(cols_d - 1):
        for j in range(8):
            a_idx = i * 8 + j
            b_idx = (i + 1) * 8 + j
            c_idx = (i + 1) * 8 + (j + 1) % 8
            d_idx = i * 8 + (j + 1) % 8
            dg_bm.faces.new([dg_bm.verts[a_idx], dg_bm.verts[b_idx],
                              dg_bm.verts[c_idx], dg_bm.verts[d_idx]])
    dg_ob = new_mesh_obj('Kael_DGuard', dg_bm, col)
    assign_mat(dg_ob, mats['brass'])
    smart_uv(dg_ob)
    objs.append(dg_ob)

    # ── Grip cylinder + leather wraps  ──
    grip = prim('cyl', 'Kael_CutlassGrip',
                loc=(bx0, by0, bz0 - 0.075), size=0.016, depth=0.148, verts=10)
    assign_mat(grip, mats['glove']); smart_uv(grip); objs.append(grip)

    # Wrap bands (4 angled tori)
    for i in range(4):
        wz = bz0 - 0.028 - i * 0.028
        wrap = prim('torus', f'Kael_GripWrap_{i}',
                    loc=(bx0, by0, wz), major=0.017, minor=0.005,
                    maj_seg=14, min_seg=6)
        assign_mat(wrap, mats['belt']); objs.append(wrap)

    # Grip cord knot at bottom
    knot = prim('sphere', 'Kael_GripKnot', loc=(bx0, by0, bz0 - 0.152), size=0.014)
    assign_mat(knot, mats['belt']); objs.append(knot)

    # ── Pommel  ──
    pommel = prim('sphere', 'Kael_Pommel', loc=(bx0, by0, bz0 - 0.168),
                  size=0.022, segs=12, rings=8)
    pommel.scale = (1.35, 0.80, 1.35)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(pommel, mats['brass']); objs.append(pommel)

    return objs

# ── SCABBARD  ─────────────────────────────────────────────────────────────────
def build_scabbard(mats, col):
    objs = []
    bx0, by0, bz0 = -0.132, -0.112, 1.310

    # Leather scabbard body
    scab = prim('cube', 'Kael_Scabbard', loc=(bx0 - 0.008, by0 + 0.008, bz0 - 0.190), size=0.030)
    scab.scale = (0.68, 0.42, 8.20)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(scab, mats['belt']); add_bevel(scab, 0.006, 2); smart_uv(scab)
    objs.append(scab)

    # Throat collar torus (top of scabbard where blade enters)
    throat = prim('torus', 'Kael_ScabbardThroat',
                  loc=(bx0, by0, bz0 + 0.010), major=0.020, minor=0.007,
                  maj_seg=16, min_seg=6)
    assign_mat(throat, mats['brass']); objs.append(throat)

    # Tip cap
    tipc = prim('cone', 'Kael_ScabbardTip',
                loc=(bx0 - 0.008, by0 + 0.008, bz0 - 0.450),
                r1=0.020, r2=0.004, depth=0.065, verts=8)
    assign_mat(tipc, mats['brass']); objs.append(tipc)

    # Mid strap keeper
    keep = prim('torus', 'Kael_ScabbardKeeper',
                loc=(bx0, by0, bz0 - 0.220), major=0.020, minor=0.005,
                maj_seg=14, min_seg=5)
    assign_mat(keep, mats['belt']); objs.append(keep)

    return objs

# ── COAT BUTTONS + GOLD TRIM  ─────────────────────────────────────────────────
def build_coat_details(mats, col):
    objs = []
    # 5 brass buttons down coat front
    for i, bz in enumerate([1.800, 1.720, 1.640, 1.560, 1.490]):
        btn = prim('cyl', f'Kael_CoatButton_{i}', loc=(0, -0.151, bz),
                   size=0.012, depth=0.013, verts=10)
        assign_mat(btn, mats['brass']); objs.append(btn)
        # Button stitch ring
        stitc = prim('torus', f'Kael_BtnStitch_{i}',
                     loc=(0, -0.152, bz), major=0.012, minor=0.002,
                     maj_seg=12, min_seg=4,
                     rot=(math.radians(90), 0, 0))
        assign_mat(stitc, mats['iron']); objs.append(stitc)

    # Gold front trim (vertical line along coat opening edge)
    for sx in (-0.040, 0.040):
        trim = prim('cube', f'Kael_CoatTrim_{"L" if sx < 0 else "R"}',
                    loc=(sx, -0.152, 1.640), size=0.003)
        trim.scale = (0.8, 0.5, 100.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(trim, mats['gold']); objs.append(trim)

    # Coat hem band (bottom of coat, gold trim)
    hem = prim('torus', 'Kael_CoatHem', loc=(0, 0, 1.312),
               major=0.200, minor=0.006, maj_seg=24, min_seg=6)
    hem.scale = (1.0, 0.74, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(hem, mats['gold']); objs.append(hem)

    return objs

# ─────────────────────────────────────────────────────────────────────────────
#  ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────

def main():
    clear_scene()
    col = new_col('IsleTrial_Kael')
    mats = build_materials()

    all_objs = []
    all_objs += build_head(mats, col)
    all_objs += build_face_features(mats, col)
    all_objs += build_ears(mats, col)
    all_objs += build_eyes(mats, col)
    all_objs += build_neck(mats, col)
    all_objs += build_coat_torso(mats, col)
    all_objs += build_coat_tails(mats, col)
    all_objs += build_epaulettes(mats, col)
    all_objs += build_breast_pocket(mats, col)
    all_objs += build_sleeves(mats, col)
    all_objs += build_forearms(mats, col)
    all_objs += build_gloves_hands(mats, col)
    all_objs += build_pants_legs(mats, col)
    all_objs += build_boots(mats, col)
    all_objs += build_belt(mats, col)
    all_objs += build_pouch(mats, col)
    all_objs += build_compass_pendant(mats, col)
    all_objs += build_hair(mats, col)
    all_objs += build_cutlass(mats, col)
    all_objs += build_scabbard(mats, col)
    all_objs += build_coat_details(mats, col)

    # ROOT empty for Unity prefab pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = 'Kael_ROOT'
    link(col, root)

    for obj in all_objs:
        if obj.parent is None:
            obj.parent = root

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = root

    tri_count = sum(len(o.data.polygons) * 2 for o in all_objs if o.type == 'MESH')

    print("\n[IsleTrial] Kael model built successfully.")
    print(f"  Objects   : {len(all_objs)}")
    print(f"  Materials : {len(bpy.data.materials)}")
    print(f"  Est. tris : ~{tri_count:,}  (before subdivision)")
    print()
    print("  Parts included:")
    print("    Head (bmesh sculpted) + brow/nose/ears/chin/mouth geometry")
    print("    3-layer eyes (sclera + glowing iris + pupil)")
    print("    Neck + adam's apple + sailor bandana")
    print("    Navy coat + front panels + collar + epaulettes + tails + hem")
    print("    Breast pocket + gold trim + 5 buttons + shoulder braid")
    print("    Rolled cuffs + gold sleeve trim + bare forearms + wrist bones")
    print("    Fingerless gloves + knuckle pads + skin fingertips + thumbs")
    print("    Tan pants + thigh seams + pant cuffs tucked into boots")
    print("    Detailed boots: toe-cap + upper + fold + sole + heel + strap buckle")
    print("    Leather belt + buckle + pin + 6 loops + 5 punch holes")
    print("    Side pouch + flap + clasp + 2 rivets")
    print("    Compass pendant: case + bezel + glass + 8pt rose + N/S needle + 6 chain links")
    print("    Hair cap + 8 windswept directional tufts + sideburns + nape strand")
    print("    Cutlass: bmesh curved blade + fuller groove + quillon + D-guard arc")
    print("             + grip + 4 wrap bands + cord knot + brass pommel")
    print("    Scabbard: leather body + throat collar + tip cap + mid keeper")
    print()
    print("  Unity workflow:")
    print("    Run 03_Kael_Rig.py NEXT to add Humanoid armature")
    print("    Export: File > Export > FBX")
    print("    Settings: Apply Transform ✓ | Scale 0.01 | Armature ✓ | Mesh ✓")
    print("    Filename: Kael_Character.fbx")
    print("    Rig Type: Humanoid | Avatar Configure (all green)")
    print("    Materials: Set [UNITY] image slots to your PBR map files")
    print("               Albedo 2048×2048 | Normal 2048×2048 | Emission 1024×1024")

main()
