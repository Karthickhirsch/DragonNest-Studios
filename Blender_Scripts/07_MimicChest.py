"""
IsleTrial — Treasure Mimic Chest  (Model)
Blender 4.x  •  Python Script

Creates the Mimic Chest enemy — modelled in open/attack state.

Dimensions  (closed):  W=0.70  H=0.72  D=0.50
Lid pivot at Z=0.46  (back hinge line)

Mesh objects
────────────────────────────────────────────────────────
  Chest_Body        – main box with wood plank detail
  Chest_Lid         – curved top lid (open ~110°)
  Band_Front_0-2    – 3 horizontal iron straps (front)
  Band_Back_0-2     – back straps
  Band_Side_L/R_0-2 – side straps
  Corner_Bracket_0-7 – 8 corner iron brackets
  Lock_Plate        – front center lock housing
  Lock_Hasp         – lock clasp (on lid)
  Hinge_L / Hinge_R – 2 back hinges
  Eye_Sclera        – white of eye (front face, center-upper)
  Eye_Iris          – yellow-amber iris, cat slit pupil
  Eye_Pupil         – dark slit
  Eyelid_Top / Bot  – lids for blink animation
  Tooth_Top_0-5     – 6 upper teeth (on lid inner edge)
  Tooth_Bot_0-5     – 6 lower teeth (on body top inner edge)
  Tongue            – thick fleshy tongue hanging over front edge
  Tentacle_0-3      – 4 tentacle tubes emerging from inside
  Coins             – pile of gold coins inside
  Interior_Glow     – emissive plane inside chest

Materials  (dual-path)
────────────────────────────────────────────────────────
  Mat_Wood_Chest    – dark aged wood, plank grain
  Mat_Iron_Aged     – oxidised dark iron
  Mat_Eye_Iris      – amber iris with slit pupil
  Mat_Eye_Sclera    – off-white, slightly veined
  Mat_Teeth         – ivory bone
  Mat_Tongue        – bright purple-pink, wet
  Mat_Tentacle      – deep purple, slight sheen
  Mat_Gold          – metallic warm gold

Run 07_MimicChest_Rig.py AFTER this script.
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ──────────────────────────────────────────────
#  SCENE
# ──────────────────────────────────────────────

def setup_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

def new_col(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def link_obj(col, obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def assign_mat(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def uv_unwrap(obj):
    activate(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

# ──────────────────────────────────────────────
#  MATERIAL NODE HELPERS
# ──────────────────────────────────────────────

def _n(nodes, ntype, loc, label=None):
    n = nodes.new(ntype)
    n.location = loc
    if label:
        n.label = label
        n.name  = label
    return n

def _img(nodes, slot_name, loc):
    n = nodes.new('ShaderNodeTexImage')
    n.location = loc
    n.label    = slot_name
    n.name     = slot_name
    return n

def _coord_map(nodes, links, scale=(6, 6, 6), loc=(-1000, 0)):
    tc = _n(nodes, 'ShaderNodeTexCoord', (loc[0],       loc[1]))
    mp = _n(nodes, 'ShaderNodeMapping',  (loc[0] + 200, loc[1]))
    mp.inputs['Scale'].default_value = scale
    links.new(tc.outputs['UV'], mp.inputs['Vector'])
    return mp

# ──────────────────────────────────────────────
#  MATERIALS
# ──────────────────────────────────────────────

def build_wood_mat(name, dark=(0.22, 0.12, 0.04), light=(0.42, 0.26, 0.10), roughness=0.88):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (500, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (100, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value  = 0.0

    mp = _coord_map(N, L, scale=(9, 9, 9), loc=(-1000, 100))

    wave = _n(N, 'ShaderNodeTexWave', (-700, 200))
    wave.wave_type = 'RINGS'; wave.rings_direction = 'X'
    wave.inputs['Scale'].default_value      = 5.0
    wave.inputs['Distortion'].default_value = 4.5
    wave.inputs['Detail'].default_value     = 8.0
    wave.inputs['Detail Scale'].default_value = 2.0
    L.new(mp.outputs['Vector'], wave.inputs['Vector'])

    noise = _n(N, 'ShaderNodeTexNoise', (-700, -80))
    noise.inputs['Scale'].default_value     = 8.0
    noise.inputs['Detail'].default_value    = 6.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    cr = _n(N, 'ShaderNodeValToRGB', (-420, 100))
    cr.color_ramp.elements[0].color = (*dark,  1.0)
    cr.color_ramp.elements[1].color = (*light, 1.0)
    L.new(wave.outputs['Color'], cr.inputs['Fac'])

    noise_rgh = _n(N, 'ShaderNodeValToRGB', (-420, -80))
    noise_rgh.color_ramp.elements[0].color = (roughness - 0.1,) * 3 + (1.0,)
    noise_rgh.color_ramp.elements[1].color = (min(1, roughness + 0.12),) * 3 + (1.0,)
    L.new(noise.outputs['Fac'], noise_rgh.inputs['Fac'])
    L.new(noise_rgh.outputs['Color'], bsdf.inputs['Roughness'])

    bump = _n(N, 'ShaderNodeBump', (-100, -200))
    bump.inputs['Strength'].default_value = 0.55
    bump.inputs['Distance'].default_value = 0.012
    L.new(wave.outputs['Color'],  bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-700, -340))
    mix = _n(N, 'ShaderNodeMixRGB', (-150, 200), 'Mix_Albedo')
    mix.inputs['Fac'].default_value = 0.0
    L.new(cr.outputs['Color'],  mix.inputs['Color1'])
    L.new(img.outputs['Color'], mix.inputs['Color2'])
    L.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_iron_mat(name, base=(0.08, 0.07, 0.07), roughness=0.72):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (400, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value  = 0.85
    bsdf.inputs['Roughness'].default_value = roughness

    mp = _coord_map(N, L, scale=(12, 12, 12), loc=(-900, 0))
    noise = _n(N, 'ShaderNodeTexNoise', (-680, 80))
    noise.inputs['Scale'].default_value     = 18.0
    noise.inputs['Detail'].default_value    = 5.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    cr = _n(N, 'ShaderNodeValToRGB', (-400, 80))
    dark  = tuple(max(0, c * 0.5) for c in base)
    cr.color_ramp.elements[0].color = (*dark, 1.0)
    cr.color_ramp.elements[1].color = (*base, 1.0)
    L.new(noise.outputs['Fac'], cr.inputs['Fac'])

    bump = _n(N, 'ShaderNodeBump', (-100, -200))
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.006
    L.new(noise.outputs['Fac'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-680, -300))
    mix = _n(N, 'ShaderNodeMixRGB', (-150, 80), 'Mix_Albedo')
    mix.inputs['Fac'].default_value = 0.0
    L.new(cr.outputs['Color'],  mix.inputs['Color1'])
    L.new(img.outputs['Color'], mix.inputs['Color2'])
    L.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_eye_iris_mat(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (400, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Metallic'].default_value  = 0.0

    tc = _n(N, 'ShaderNodeTexCoord', (-900, 0))
    mp = _n(N, 'ShaderNodeMapping',  (-700, 0))
    L.new(tc.outputs['UV'], mp.inputs['Vector'])

    # Radial gradient for iris
    grad = _n(N, 'ShaderNodeTexGradient', (-500, 0))
    grad.gradient_type = 'RADIAL'
    L.new(mp.outputs['Vector'], grad.inputs['Vector'])

    # Pupil slit (wave)
    wave = _n(N, 'ShaderNodeTexWave', (-500, -200))
    wave.wave_type = 'BANDS'; wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 3.0
    wave.inputs['Distortion'].default_value = 0.0
    L.new(mp.outputs['Vector'], wave.inputs['Vector'])

    cr_iris = _n(N, 'ShaderNodeValToRGB', (-280, 0))
    cr_iris.color_ramp.elements[0].color = (0.62, 0.38, 0.02, 1.0)  # amber outer
    cr_iris.color_ramp.elements[1].color = (0.95, 0.75, 0.10, 1.0)  # yellow inner
    cr_iris.color_ramp.elements[0].position = 0.3
    L.new(grad.outputs['Color'], cr_iris.inputs['Fac'])

    cr_pupil = _n(N, 'ShaderNodeValToRGB', (-280, -200))
    cr_pupil.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    cr_pupil.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    cr_pupil.color_ramp.elements[0].position = 0.46
    cr_pupil.color_ramp.elements[1].position = 0.54
    L.new(wave.outputs['Color'], cr_pupil.inputs['Fac'])

    mix_pupil = _n(N, 'ShaderNodeMixRGB', (-60, -100))
    mix_pupil.blend_type = 'MULTIPLY'
    mix_pupil.inputs['Fac'].default_value = 1.0
    L.new(cr_iris.outputs['Color'],  mix_pupil.inputs['Color1'])
    L.new(cr_pupil.outputs['Color'], mix_pupil.inputs['Color2'])
    L.new(mix_pupil.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_simple_mat(name, color, roughness=0.5, metallic=0.0, emit_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (300, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value   = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value    = roughness
    bsdf.inputs['Metallic'].default_value     = metallic
    if emit_strength > 0:
        try:
            bsdf.inputs['Emission Color'].default_value    = (*color, 1.0)
            bsdf.inputs['Emission Strength'].default_value = emit_strength
        except KeyError:
            pass
    return mat


def build_tongue_mat(name, base=(0.72, 0.15, 0.45)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (400, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['Metallic'].default_value  = 0.0
    try:
        bsdf.inputs['Subsurface Weight'].default_value = 0.18
    except KeyError:
        pass

    mp = _coord_map(N, L, scale=(10, 10, 10), loc=(-900, 0))
    noise = _n(N, 'ShaderNodeTexNoise', (-680, 80))
    noise.inputs['Scale'].default_value  = 12.0
    noise.inputs['Detail'].default_value = 5.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    dark = tuple(max(0, c * 0.55) for c in base)
    cr = _n(N, 'ShaderNodeValToRGB', (-420, 80))
    cr.color_ramp.elements[0].color = (*dark, 1.0)
    cr.color_ramp.elements[1].color = (*base, 1.0)
    L.new(noise.outputs['Fac'], cr.inputs['Fac'])

    bump = _n(N, 'ShaderNodeBump', (-100, -150))
    bump.inputs['Strength'].default_value = 0.25
    bump.inputs['Distance'].default_value = 0.006
    L.new(noise.outputs['Fac'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-680, -300))
    mix = _n(N, 'ShaderNodeMixRGB', (-150, 80), 'Mix_Albedo')
    mix.inputs['Fac'].default_value = 0.0
    L.new(cr.outputs['Color'],  mix.inputs['Color1'])
    L.new(img.outputs['Color'], mix.inputs['Color2'])
    L.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_tentacle_mat(name, base=(0.30, 0.04, 0.50)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (400, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.30
    bsdf.inputs['Metallic'].default_value  = 0.0
    try:
        bsdf.inputs['Subsurface Weight'].default_value = 0.12
    except KeyError:
        pass

    mp = _coord_map(N, L, scale=(8, 8, 8), loc=(-900, 0))
    noise = _n(N, 'ShaderNodeTexNoise', (-680, 80))
    noise.inputs['Scale'].default_value  = 9.0
    noise.inputs['Detail'].default_value = 6.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    vor = _n(N, 'ShaderNodeTexVoronoi', (-680, -100))
    vor.inputs['Scale'].default_value = 14.0
    vor.feature = 'SMOOTH_F1'
    L.new(mp.outputs['Vector'], vor.inputs['Vector'])

    dark = tuple(max(0, c * 0.45) for c in base)
    cr = _n(N, 'ShaderNodeValToRGB', (-400, 80))
    cr.color_ramp.elements[0].color = (*dark, 1.0)
    cr.color_ramp.elements[1].color = (*base, 1.0)
    L.new(noise.outputs['Fac'], cr.inputs['Fac'])

    mix_vor = _n(N, 'ShaderNodeMixRGB', (-200, 0))
    mix_vor.blend_type = 'OVERLAY'
    mix_vor.inputs['Fac'].default_value = 0.28
    L.new(cr.outputs['Color'],  mix_vor.inputs['Color1'])
    L.new(vor.outputs['Color'], mix_vor.inputs['Color2'])

    bump = _n(N, 'ShaderNodeBump', (-100, -200))
    bump.inputs['Strength'].default_value = 0.40
    bump.inputs['Distance'].default_value = 0.008
    L.new(noise.outputs['Fac'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-680, -340))
    mix_u = _n(N, 'ShaderNodeMixRGB', (-50, 0), 'Mix_Albedo')
    mix_u.inputs['Fac'].default_value = 0.0
    L.new(mix_vor.outputs['Color'], mix_u.inputs['Color1'])
    L.new(img.outputs['Color'],     mix_u.inputs['Color2'])
    L.new(mix_u.outputs['Color'],   bsdf.inputs['Base Color'])
    return mat


def build_gold_mat(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (300, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (1.00, 0.78, 0.18, 1.0)
    bsdf.inputs['Metallic'].default_value   = 1.0
    bsdf.inputs['Roughness'].default_value  = 0.22
    return mat

# ──────────────────────────────────────────────
#  CHEST BODY
# ──────────────────────────────────────────────

def build_chest_body(mats):
    objs = []

    # Main body box
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.225))
    body = bpy.context.active_object
    body.name = 'Chest_Body'
    body.scale = (0.350, 0.250, 0.225)
    bpy.ops.object.transform_apply(scale=True)

    # Add plank-line loop cuts on front face
    activate(body)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(body.data)

    # Inset front face for plank depth illusion
    front_faces = [f for f in bm.faces if f.normal.y < -0.9]
    bmesh.ops.inset_individual(bm, faces=front_faces, thickness=0.008, depth=-0.005)

    # Bevel all edges for chamfer
    result = bmesh.ops.bevel(bm, geom=[e for e in bm.edges], offset=0.006,
                             segments=2, profile=0.5, affect='EDGES')
    bmesh.update_edit_mesh(body.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    bev = body.modifiers.new('Bevel', 'BEVEL')
    bev.width = 0.005; bev.segments = 2
    assign_mat(body, mats['wood'])
    objs.append(body)

    return objs, body


def build_chest_lid(mats):
    objs = []

    # Lid — slightly curved top (curved using lattice-like scaling)
    bpy.ops.mesh.primitive_cube_add(location=(0, -0.008, 0.530))
    lid = bpy.context.active_object
    lid.name = 'Chest_Lid'
    lid.scale = (0.350, 0.242, 0.130)
    bpy.ops.object.transform_apply(scale=True)

    # Curve the lid top — subdivide and push up center vertices
    activate(lid)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=3)
    bm = bmesh.from_edit_mesh(lid.data)
    top_verts = [v for v in bm.verts if v.co.z > 0.648]
    for v in top_verts:
        dist = math.sqrt(v.co.x ** 2 + v.co.y ** 2) / 0.40
        v.co.z += max(0, (1.0 - dist) * 0.025)
    bmesh.update_edit_mesh(lid.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Rotate lid to open position (~110 deg around hinge at Z=0.46, Y=0.242)
    lid.location.z   = 0.460
    bpy.ops.object.transform_apply(location=True)
    lid.location.y   = 0.242
    bpy.ops.object.transform_apply(location=True)
    lid.rotation_euler = (math.radians(-108), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    lid.location.y  = -0.242
    lid.location.z   = 0.460
    bpy.ops.object.transform_apply(location=True)

    assign_mat(lid, mats['wood'])
    objs.append(lid)

    return objs, lid


def build_metal_hardware(mats):
    objs = []
    w = 0.354
    d = 0.254

    # Iron bands on all 4 faces (3 horizontal bands each)
    band_z = [0.090, 0.225, 0.362]
    for zi, z in enumerate(band_z):
        # Front / Back
        for yf, label in ((-(d), 'Front'), (d, 'Back')):
            bpy.ops.mesh.primitive_cube_add(location=(0, yf, z))
            band = bpy.context.active_object
            band.name = f'Band_{label}_{zi}'
            band.scale = (w, 0.008, 0.018)
            bpy.ops.object.transform_apply(scale=True)
            assign_mat(band, mats['iron'])
            objs.append(band)
        # Sides
        for xf, label in ((-w, 'Side_L'), (w, 'Side_R')):
            bpy.ops.mesh.primitive_cube_add(location=(xf, 0, z))
            band = bpy.context.active_object
            band.name = f'Band_{label}_{zi}'
            band.scale = (0.008, d, 0.018)
            bpy.ops.object.transform_apply(scale=True)
            assign_mat(band, mats['iron'])
            objs.append(band)

    # Corner brackets (8 corners)
    for xi, xv in ((-1, -w + 0.012), (1, w - 0.012)):
        for yi, yv in ((-1, -d + 0.012), (1, d - 0.012)):
            for zi, zv in enumerate([0.025, 0.425]):
                bpy.ops.mesh.primitive_cube_add(location=(xv, yv, zv))
                brk = bpy.context.active_object
                brk.name = f'Corner_{xi}_{yi}_{zi}'
                brk.scale = (0.030, 0.030, 0.025 + zi * 0.380)
                bpy.ops.object.transform_apply(scale=True)
                assign_mat(brk, mats['iron'])
                objs.append(brk)

    # Lock plate (front center)
    bpy.ops.mesh.primitive_cube_add(location=(0, -(d + 0.010), 0.225))
    lock_p = bpy.context.active_object
    lock_p.name = 'Lock_Plate'
    lock_p.scale = (0.050, 0.012, 0.060)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(lock_p, mats['iron'])
    objs.append(lock_p)

    # Keyhole
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.016,
                                        depth=0.015, location=(0, -(d + 0.022), 0.240))
    kh = bpy.context.active_object
    kh.name = 'Keyhole'
    assign_mat(kh, mats['iron'])
    objs.append(kh)

    # Hinges (back, 2)
    for hx in (-0.22, 0.22):
        bpy.ops.mesh.primitive_cube_add(location=(hx, d + 0.005, 0.460))
        hinge = bpy.context.active_object
        hinge.name = f'Hinge_{"L" if hx < 0 else "R"}'
        hinge.scale = (0.038, 0.018, 0.058)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(hinge, mats['iron'])
        objs.append(hinge)

    return objs

# ──────────────────────────────────────────────
#  EYE
# ──────────────────────────────────────────────

def build_eye(mats):
    objs = []

    # Sclera (white of eye, bulging out from front face)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10,
                                         radius=0.075, location=(0, -0.265, 0.360))
    scl = bpy.context.active_object
    scl.name = 'Eye_Sclera'
    scl.scale = (1.0, 0.58, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(scl, mats['sclera'])
    objs.append(scl)

    # Iris (slightly protruding from sclera)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10,
                                         radius=0.052, location=(0, -0.298, 0.360))
    iris = bpy.context.active_object
    iris.name = 'Eye_Iris'
    iris.scale = (1.0, 0.40, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(iris, mats['iris'])
    objs.append(iris)

    # Pupil slit
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6,
                                         radius=0.022, location=(0, -0.308, 0.360))
    pupil = bpy.context.active_object
    pupil.name = 'Eye_Pupil'
    pupil.scale = (0.28, 0.35, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(pupil, mats['pupil'])
    objs.append(pupil)

    # Eyelids
    for side, zoff in (('Top', 0.050), ('Bot', -0.050)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8,
                                             radius=0.078, location=(0, -0.258, 0.360 + zoff))
        eld = bpy.context.active_object
        eld.name = f'Eyelid_{side}'
        eld.scale = (1.0, 0.48, 0.42)
        bpy.ops.object.transform_apply(scale=True)
        # Position to cover half the sclera
        assign_mat(eld, mats['wood'])
        objs.append(eld)

    return objs

# ──────────────────────────────────────────────
#  TEETH
# ──────────────────────────────────────────────

def build_teeth(mats):
    objs = []

    # 6 upper teeth on lid inner edge (after lid opens, they're on the "roof")
    top_y_base = -0.245
    for ti in range(6):
        x = (ti - 2.5) * 0.095
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.028, radius2=0.004,
                                        depth=0.095, location=(x, top_y_base, 0.462))
        tooth = bpy.context.active_object
        tooth.name = f'Tooth_Top_{ti}'
        tooth.scale = (0.7, 0.6, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(tooth, mats['teeth'])
        objs.append(tooth)

    # 6 lower teeth on body top edge
    bot_y_base = -0.240
    for ti in range(6):
        x = (ti - 2.5) * 0.095
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.028, radius2=0.004,
                                        depth=0.092, location=(x, bot_y_base, 0.448))
        tooth = bpy.context.active_object
        tooth.name = f'Tooth_Bot_{ti}'
        tooth.scale = (0.7, 0.6, 1.0)
        tooth.rotation_euler.x = math.pi
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        tooth.location.z = 0.448
        assign_mat(tooth, mats['teeth'])
        objs.append(tooth)

    return objs

# ──────────────────────────────────────────────
#  TONGUE
# ──────────────────────────────────────────────

def build_tongue(mats):
    objs = []

    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8,
                                         radius=0.08, location=(0, -0.245, 0.395))
    tongue = bpy.context.active_object
    tongue.name = 'Tongue'
    tongue.scale = (0.70, 0.85, 0.45)
    bpy.ops.object.transform_apply(scale=True)

    # Shape tongue with loop cuts + push forward
    activate(tongue)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bm = bmesh.from_edit_mesh(tongue.data)
    for v in bm.verts:
        if v.co.y < -0.245:
            v.co.y -= (v.co.y + 0.245) * 0.6
            v.co.z -= 0.04
    bmesh.update_edit_mesh(tongue.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    sol = tongue.modifiers.new('Subdiv', 'SUBSURF')
    sol.levels = 2
    assign_mat(tongue, mats['tongue'])
    objs.append(tongue)

    # Tongue tip (forked)
    for txoff in (-0.028, 0.028):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6,
                                             radius=0.032, location=(txoff, -0.370, 0.372))
        tip = bpy.context.active_object
        tip.name = f'Tongue_Tip_{"L" if txoff < 0 else "R"}'
        tip.scale = (0.6, 0.95, 0.5)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(tip, mats['tongue'])
        objs.append(tip)

    return objs

# ──────────────────────────────────────────────
#  TENTACLES
# ──────────────────────────────────────────────

def build_tentacles(mats):
    objs = []

    # 4 tentacles, each a subdivided curve/tube emerging from the chest opening
    tentacle_configs = [
        # (root_xyz, mid_offset_xyz, tip_xyz, name)
        ((-0.18, -0.20, 0.460), (-0.28, -0.38, 0.320), (-0.38, -0.42, 0.140), 'Tentacle_0'),
        ((-0.10, -0.22, 0.460), (-0.12, -0.45, 0.280), (-0.08, -0.50, 0.080), 'Tentacle_1'),
        (( 0.08, -0.22, 0.460), ( 0.10, -0.46, 0.260), ( 0.06, -0.52, 0.060), 'Tentacle_2'),
        (( 0.20, -0.20, 0.460), ( 0.30, -0.38, 0.300), ( 0.36, -0.40, 0.120), 'Tentacle_3'),
    ]
    for root, mid, tip, tname in tentacle_configs:
        # Build a tapered tube along a curved path using bmesh
        bm = bmesh.new()
        segments = 12
        pts = [Vector(root), Vector(mid), Vector(tip)]

        # Catmull-Rom interpolation along 3 control points
        all_verts = []
        for si in range(segments + 1):
            t = si / segments
            if t <= 0.5:
                t2 = t * 2
                p = (1 - t2) * Vector(pts[0]) + t2 * Vector(pts[1])
            else:
                t2 = (t - 0.5) * 2
                p = (1 - t2) * Vector(pts[1]) + t2 * Vector(pts[2])

            r = max(0.006, 0.040 * (1.0 - t * 0.85))  # taper toward tip
            ring = []
            for vi in range(8):
                angle = 2 * math.pi * vi / 8
                ring.append(bm.verts.new((p.x + math.cos(angle) * r,
                                          p.y + math.sin(angle) * r,
                                          p.z)))
            all_verts.append(ring)

        # Connect rings with faces
        for si in range(segments):
            ring_a = all_verts[si]
            ring_b = all_verts[si + 1]
            for vi in range(8):
                bm.faces.new([ring_a[vi], ring_a[(vi + 1) % 8],
                               ring_b[(vi + 1) % 8], ring_b[vi]])

        # Close tip
        tip_center = bm.verts.new(Vector(tip))
        for vi in range(8):
            bm.faces.new([all_verts[-1][vi], all_verts[-1][(vi + 1) % 8], tip_center])

        mesh = bpy.data.meshes.new(tname)
        bm.to_mesh(mesh); bm.free()
        obj = bpy.data.objects.new(tname, mesh)
        bpy.context.scene.collection.objects.link(obj)

        sub = obj.modifiers.new('Sub', 'SUBSURF'); sub.levels = 2
        assign_mat(obj, mats['tentacle'])
        objs.append(obj)

    return objs

# ──────────────────────────────────────────────
#  COINS + INTERIOR GLOW
# ──────────────────────────────────────────────

def build_interior(mats):
    objs = []

    # Interior emissive glow plane
    bpy.ops.mesh.primitive_plane_add(size=0.55, location=(0, 0, 0.468))
    glow = bpy.context.active_object
    glow.name = 'Interior_Glow'
    glow.scale = (0.62, 0.44, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(glow, mats['glow'])
    objs.append(glow)

    # A few gold coins in a pile
    coin_positions = [
        (0, -0.05, 0.470), (-0.08, 0.04, 0.470), (0.10, -0.08, 0.470),
        (-0.04, 0.10, 0.475), (0.06, 0.06, 0.478),
    ]
    for ci, pos in enumerate(coin_positions):
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.040,
                                            depth=0.012, location=pos)
        coin = bpy.context.active_object
        coin.name = f'Coin_{ci}'
        coin.rotation_euler = (math.radians(ci * 18), math.radians(ci * 22), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(coin, mats['gold'])
        objs.append(coin)

    return objs

# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    setup_scene()

    mats = {
        'wood'     : build_wood_mat('Mat_Wood_Chest',    dark=(0.22, 0.12, 0.04), light=(0.42, 0.26, 0.10)),
        'iron'     : build_iron_mat('Mat_Iron_Aged',     base=(0.08, 0.07, 0.07)),
        'iris'     : build_eye_iris_mat('Mat_Eye_Iris'),
        'sclera'   : build_simple_mat('Mat_Eye_Sclera',  color=(0.92, 0.90, 0.86), roughness=0.08),
        'pupil'    : build_simple_mat('Mat_Eye_Pupil',   color=(0.02, 0.02, 0.02), roughness=0.05),
        'teeth'    : build_simple_mat('Mat_Teeth',       color=(0.88, 0.85, 0.72), roughness=0.68),
        'tongue'   : build_tongue_mat('Mat_Tongue',      base=(0.72, 0.15, 0.42)),
        'tentacle' : build_tentacle_mat('Mat_Tentacle',  base=(0.32, 0.05, 0.52)),
        'gold'     : build_gold_mat('Mat_Gold'),
        'glow'     : build_simple_mat('Mat_Interior_Glow', color=(0.42, 0.08, 0.65),
                                      roughness=1.0, emit_strength=2.8),
    }

    all_objs = []
    body_objs, chest_body = build_chest_body(mats)
    all_objs.extend(body_objs)
    lid_objs, chest_lid = build_chest_lid(mats)
    all_objs.extend(lid_objs)
    all_objs.extend(build_metal_hardware(mats))
    all_objs.extend(build_eye(mats))
    all_objs.extend(build_teeth(mats))
    all_objs.extend(build_tongue(mats))
    all_objs.extend(build_tentacles(mats))
    all_objs.extend(build_interior(mats))

    print(f"[MimicChest] UV unwrapping {len(all_objs)} objects...")
    for obj in all_objs:
        if obj.type == 'MESH':
            uv_unwrap(obj)

    col = new_col('IsleTrial_MimicChest')
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = 'MimicChest_ROOT'
    link_obj(col, root)
    for obj in all_objs:
        obj.parent = root
        link_obj(col, obj)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D':
                    sp.shading.type = 'MATERIAL'
            break

    print("\n" + "="*62)
    print("  IsleTrial — Treasure Mimic Chest Model Complete")
    print("="*62)
    print(f"  Objects    : {len(all_objs)}")
    print("  Materials  : 10  (procedural + [UNITY] image slots)")
    print("  State      : Open / attack pose")
    print("  Collection : IsleTrial_MimicChest")
    print("  Next step  : Run 07_MimicChest_Rig.py")
    print("="*62 + "\n")


main()
