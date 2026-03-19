"""
IsleTrial — Main Player Vessel
Blender 4.x Python Script

Run this in Blender's Scripting workspace (Text Editor → Run Script).
Creates all boat geometry, materials, UV maps, and organises the scene
ready for FBX export to Unity.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for col in bpy.data.collections:
        bpy.data.collections.remove(col)


def new_obj(name, mesh_data):
    obj = bpy.data.objects.new(name, mesh_data)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transforms(obj):
    activate(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def smart_uv(obj):
    activate(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')


def assign_mat(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


# ─────────────────────────────────────────────────────────────────────
#  RICH MATERIAL BUILDER
#
#  Every material contains THREE parallel paths:
#
#   [Procedural nodes]  ──┐
#                         ├─ Mix (Fac=0) → BSDF   ← active in Blender
#   [Image Tex slot]   ──┘
#
#  Mix Factor = 0  →  100 % procedural  (default, no files needed)
#  Mix Factor = 1  →  100 % image tex   (load Unity PBR maps and flip)
#
#  Image Texture nodes are labelled "[UNITY] MatName_Channel" so you
#  can find them instantly in the Shader Editor when baking for Unity.
# ─────────────────────────────────────────────────────────────────────

def _n(nodes, node_type, loc, label=None):
    nd = nodes.new(node_type)
    nd.location = loc
    if label:
        nd.label = label
    return nd


def _img(nodes, slot_name, loc):
    """Empty Image Texture node — load your Unity PBR map here."""
    nd = nodes.new('ShaderNodeTexImage')
    nd.location = loc
    nd.label    = f'[UNITY] {slot_name}'
    nd.name     = slot_name
    return nd


def _mapping(nodes, links, scale=(1.0, 1.0, 1.0), loc=(-900, 0)):
    tc = _n(nodes, 'ShaderNodeTexCoord', (-1100, 0))
    mp = _n(nodes, 'ShaderNodeMapping',   loc)
    mp.inputs['Scale'].default_value = (scale[0], scale[1], scale[2])
    links.new(tc.outputs['UV'], mp.inputs['Vector'])
    return tc, mp


def _mix_pi(nodes, links, proc_socket, img_nd, loc, lbl=''):
    """Wire:  proc → Mix ← img.  Factor 0 = full procedural."""
    mix = _n(nodes, 'ShaderNodeMixRGB', loc, label=f'Mix {lbl}')
    mix.blend_type = 'MIX'
    mix.inputs['Fac'].default_value = 0.0
    links.new(proc_socket,              mix.inputs['Color1'])
    links.new(img_nd.outputs['Color'],  mix.inputs['Color2'])
    return mix


# ── Wood  ─────────────────────────────────────────────────────────────
def build_wood_mat(name, dark, light, roughness=0.88, metallic=0.0, su=10.0):
    """
    Wave bands for grain lines + Noise overlay for surface variation.
    Image slots: Albedo · Normal · Roughness
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (1100, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (680,  0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value = metallic

    _, mp = _mapping(nd, lk, scale=(su, 1.0, 1.0))

    # Albedo — wave grain
    wave = _n(nd, 'ShaderNodeTexWave', (-480, 300))
    wave.wave_type = 'BANDS'; wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value            = 18.0
    wave.inputs['Distortion'].default_value       = 2.5
    wave.inputs['Detail'].default_value           = 12.0
    wave.inputs['Detail Scale'].default_value     = 2.0
    wave.inputs['Detail Roughness'].default_value = 0.65
    lk.new(mp.outputs['Vector'], wave.inputs['Vector'])

    cramp = _n(nd, 'ShaderNodeValToRGB', (-180, 300))
    cramp.color_ramp.elements[0].position = 0.35; cramp.color_ramp.elements[0].color = (*dark,  1.0)
    cramp.color_ramp.elements[1].position = 0.75; cramp.color_ramp.elements[1].color = (*light, 1.0)
    lk.new(wave.outputs['Color'], cramp.inputs['Fac'])

    noise_c = _n(nd, 'ShaderNodeTexNoise', (-480, 50))
    noise_c.inputs['Scale'].default_value = 6.0; noise_c.inputs['Detail'].default_value = 8.0
    lk.new(mp.outputs['Vector'], noise_c.inputs['Vector'])

    ov = _n(nd, 'ShaderNodeMixRGB', (50, 250))
    ov.blend_type = 'OVERLAY'; ov.inputs['Fac'].default_value = 0.22
    lk.new(cramp.outputs['Color'], ov.inputs['Color1'])
    lk.new(noise_c.outputs['Color'], ov.inputs['Color2'])

    img_a = _img(nd, f'{name}_Albedo', (-480, -280))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, ov.outputs['Color'], img_a, (280, 250), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    # Normal — noise bump
    noise_n = _n(nd, 'ShaderNodeTexNoise', (-480, -520))
    noise_n.inputs['Scale'].default_value = 35.0; noise_n.inputs['Detail'].default_value = 10.0
    lk.new(mp.outputs['Vector'], noise_n.inputs['Vector'])
    bump = _n(nd, 'ShaderNodeBump', (-80, -440))
    bump.inputs['Strength'].default_value = 0.55; bump.inputs['Distance'].default_value = 0.05
    lk.new(noise_n.outputs['Fac'], bump.inputs['Height'])

    img_n = _img(nd, f'{name}_Normal', (-480, -740))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd, 'ShaderNodeNormalMap', (-80, -700))
    lk.new(img_n.outputs['Color'], nmap.inputs['Color'])

    mix_n = _n(nd, 'ShaderNodeMixRGB', (160, -580), label='Mix Normal')
    mix_n.inputs['Fac'].default_value = 0.0
    lk.new(bump.outputs['Normal'],  mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'],  mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'],  bsdf.inputs['Normal'])

    # Roughness — noise variation
    noise_r = _n(nd, 'ShaderNodeTexNoise', (-480, -980))
    noise_r.inputs['Scale'].default_value = 50.0; noise_r.inputs['Detail'].default_value = 4.0
    lk.new(mp.outputs['Vector'], noise_r.inputs['Vector'])
    mrng = _n(nd, 'ShaderNodeMapRange', (-180, -980))
    mrng.inputs['To Min'].default_value = roughness - 0.08
    mrng.inputs['To Max'].default_value = roughness + 0.07
    lk.new(noise_r.outputs['Fac'], mrng.inputs['Value'])

    img_r = _img(nd, f'{name}_Roughness', (-480, -1180))
    lk.new(mp.outputs['Vector'], img_r.inputs['Vector'])
    mix_r = _n(nd, 'ShaderNodeMixRGB', (200, -980), label='Mix Roughness')
    mix_r.inputs['Fac'].default_value = 0.0
    lk.new(mrng.outputs['Result'],   mix_r.inputs['Color1'])
    lk.new(img_r.outputs['Color'],   mix_r.inputs['Color2'])
    lk.new(mix_r.outputs['Color'],   bsdf.inputs['Roughness'])

    return mat


# ── Metal  ────────────────────────────────────────────────────────────
def build_metal_mat(name, base, metallic=0.9, roughness=0.3):
    """
    High-freq noise for micro surface + scratch overlay on roughness.
    Image slots: Albedo · Normal · Roughness · Metallic
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (1100, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (680,  0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value = metallic

    _, mp = _mapping(nd, lk, scale=(3.0, 3.0, 3.0))

    # Albedo — subtle micro-variation
    noise_c = _n(nd, 'ShaderNodeTexNoise', (-480, 280))
    noise_c.inputs['Scale'].default_value = 120.0; noise_c.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['Vector'], noise_c.inputs['Vector'])
    cramp = _n(nd, 'ShaderNodeValToRGB', (-200, 280))
    cramp.color_ramp.elements[0].color = (*base, 1.0)
    cramp.color_ramp.elements[1].color = (*tuple(min(c + 0.07, 1.0) for c in base), 1.0)
    lk.new(noise_c.outputs['Fac'], cramp.inputs['Fac'])

    img_a = _img(nd, f'{name}_Albedo', (-480, -200))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, cramp.outputs['Color'], img_a, (280, 250), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness — scratches via high-freq noise threshold
    scratch = _n(nd, 'ShaderNodeTexNoise', (-480, -420))
    scratch.inputs['Scale'].default_value = 300.0; scratch.inputs['Detail'].default_value = 12.0
    scratch.inputs['Roughness'].default_value = 0.85
    lk.new(mp.outputs['Vector'], scratch.inputs['Vector'])
    mrng = _n(nd, 'ShaderNodeMapRange', (-180, -420))
    mrng.inputs['To Min'].default_value = roughness
    mrng.inputs['To Max'].default_value = roughness + 0.28
    lk.new(scratch.outputs['Fac'], mrng.inputs['Value'])

    img_r = _img(nd, f'{name}_Roughness', (-480, -640))
    lk.new(mp.outputs['Vector'], img_r.inputs['Vector'])
    mix_r = _n(nd, 'ShaderNodeMixRGB', (200, -420), label='Mix Roughness')
    mix_r.inputs['Fac'].default_value = 0.0
    lk.new(mrng.outputs['Result'], mix_r.inputs['Color1'])
    lk.new(img_r.outputs['Color'], mix_r.inputs['Color2'])
    lk.new(mix_r.outputs['Color'], bsdf.inputs['Roughness'])

    # Normal — micro-surface bump
    noise_n = _n(nd, 'ShaderNodeTexNoise', (-480, -880))
    noise_n.inputs['Scale'].default_value = 200.0; noise_n.inputs['Detail'].default_value = 8.0
    lk.new(mp.outputs['Vector'], noise_n.inputs['Vector'])
    bump = _n(nd, 'ShaderNodeBump', (-80, -800))
    bump.inputs['Strength'].default_value = 0.2; bump.inputs['Distance'].default_value = 0.02
    lk.new(noise_n.outputs['Fac'], bump.inputs['Height'])

    img_n = _img(nd, f'{name}_Normal', (-480, -1080))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd, 'ShaderNodeNormalMap', (-80, -1040))
    lk.new(img_n.outputs['Color'], nmap.inputs['Color'])

    mix_n = _n(nd, 'ShaderNodeMixRGB', (160, -900), label='Mix Normal')
    mix_n.inputs['Fac'].default_value = 0.0
    lk.new(bump.outputs['Normal'], mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'], mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])

    return mat


# ── Canvas  ───────────────────────────────────────────────────────────
def build_canvas_mat(name, base):
    """
    Crossed wave textures simulate woven cloth.
    Image slots: Albedo · Normal
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (1000, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (600,  0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Metallic'].default_value  = 0.0

    _, mp = _mapping(nd, lk, scale=(4.0, 4.0, 4.0))

    def wave(direction, y):
        w = _n(nd, 'ShaderNodeTexWave', (-480, y))
        w.wave_type = 'BANDS'; w.bands_direction = direction
        w.inputs['Scale'].default_value      = 40.0
        w.inputs['Distortion'].default_value = 0.45
        w.inputs['Detail'].default_value     = 4.0
        lk.new(mp.outputs['Vector'], w.inputs['Vector'])
        return w

    wu = wave('X', 300); wv = wave('Y', 50)
    weave = _n(nd, 'ShaderNodeMixRGB', (-200, 200))
    weave.blend_type = 'MULTIPLY'; weave.inputs['Fac'].default_value = 0.65
    lk.new(wu.outputs['Color'], weave.inputs['Color1'])
    lk.new(wv.outputs['Color'], weave.inputs['Color2'])

    cramp = _n(nd, 'ShaderNodeValToRGB', (20, 300))
    cramp.color_ramp.elements[0].color = (*tuple(max(c-0.06,0) for c in base), 1.0)
    cramp.color_ramp.elements[1].color = (*base, 1.0)
    lk.new(weave.outputs['Color'], cramp.inputs['Fac'])

    img_a = _img(nd, f'{name}_Albedo', (-480, -260))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, cramp.outputs['Color'], img_a, (280, 230), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    # Normal — bump from weave pattern
    bump = _n(nd, 'ShaderNodeBump', (-80, -420))
    bump.inputs['Strength'].default_value = 0.45; bump.inputs['Distance'].default_value = 0.02
    lk.new(weave.outputs['Color'], bump.inputs['Height'])

    img_n = _img(nd, f'{name}_Normal', (-480, -580))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd, 'ShaderNodeNormalMap', (-80, -550))
    lk.new(img_n.outputs['Color'], nmap.inputs['Color'])

    mix_n = _n(nd, 'ShaderNodeMixRGB', (160, -480), label='Mix Normal')
    mix_n.inputs['Fac'].default_value = 0.0
    lk.new(bump.outputs['Normal'], mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'], mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])

    return mat


# ── Rope  ─────────────────────────────────────────────────────────────
def build_rope_mat(name, base):
    """
    Diagonal wave bands for twisted fibre look.
    Image slots: Albedo · Normal
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (1000, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (600,  0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Metallic'].default_value  = 0.0

    _, mp = _mapping(nd, lk, scale=(6.0, 1.0, 1.0))

    wave = _n(nd, 'ShaderNodeTexWave', (-480, 280))
    wave.wave_type = 'BANDS'; wave.bands_direction = 'DIAGONAL'
    wave.inputs['Scale'].default_value            = 35.0
    wave.inputs['Distortion'].default_value       = 3.0
    wave.inputs['Detail'].default_value           = 8.0
    wave.inputs['Detail Roughness'].default_value = 0.8
    lk.new(mp.outputs['Vector'], wave.inputs['Vector'])

    cramp = _n(nd, 'ShaderNodeValToRGB', (-200, 280))
    cramp.color_ramp.elements[0].color = (*tuple(max(c-0.14,0) for c in base), 1.0)
    cramp.color_ramp.elements[1].color = (*base, 1.0)
    lk.new(wave.outputs['Color'], cramp.inputs['Fac'])

    noise_c = _n(nd, 'ShaderNodeTexNoise', (-480, 50))
    noise_c.inputs['Scale'].default_value = 80.0; noise_c.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['Vector'], noise_c.inputs['Vector'])
    ov = _n(nd, 'ShaderNodeMixRGB', (20, 200))
    ov.blend_type = 'OVERLAY'; ov.inputs['Fac'].default_value = 0.18
    lk.new(cramp.outputs['Color'], ov.inputs['Color1'])
    lk.new(noise_c.outputs['Color'], ov.inputs['Color2'])

    img_a = _img(nd, f'{name}_Albedo', (-480, -260))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, ov.outputs['Color'], img_a, (260, 200), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    bump = _n(nd, 'ShaderNodeBump', (-80, -440))
    bump.inputs['Strength'].default_value = 0.85; bump.inputs['Distance'].default_value = 0.03
    lk.new(wave.outputs['Color'], bump.inputs['Height'])

    img_n = _img(nd, f'{name}_Normal', (-480, -600))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd, 'ShaderNodeNormalMap', (-80, -570))
    lk.new(img_n.outputs['Color'], nmap.inputs['Color'])

    mix_n = _n(nd, 'ShaderNodeMixRGB', (160, -500), label='Mix Normal')
    mix_n.inputs['Fac'].default_value = 0.0
    lk.new(bump.outputs['Normal'], mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'], mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])

    return mat


# ── Glass / Emissive  ─────────────────────────────────────────────────
def build_glass_mat(name, base, emission_str=2.5):
    """
    Translucent emissive lantern glass.  No image slots — baked glow.
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (800, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (400, 0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value          = (*base, 1.0)
    bsdf.inputs['Roughness'].default_value           = 0.04
    bsdf.inputs['Metallic'].default_value            = 0.0
    bsdf.inputs['Alpha'].default_value               = 0.55
    bsdf.inputs['Transmission Weight'].default_value = 0.8
    bsdf.inputs['Emission Color'].default_value      = (*base, 1.0)

    # Noise-driven emission flicker
    _, mp = _mapping(nd, lk, scale=(1.0, 1.0, 1.0), loc=(-500, -200))
    flicker = _n(nd, 'ShaderNodeTexNoise', (-300, -200))
    flicker.inputs['Scale'].default_value  = 1.5
    flicker.inputs['Detail'].default_value = 2.0
    lk.new(mp.outputs['Vector'], flicker.inputs['Vector'])
    mrng = _n(nd, 'ShaderNodeMapRange', (-50, -200))
    mrng.inputs['To Min'].default_value = emission_str * 0.78
    mrng.inputs['To Max'].default_value = emission_str * 1.20
    lk.new(flicker.outputs['Fac'],   mrng.inputs['Value'])
    lk.new(mrng.outputs['Result'],   bsdf.inputs['Emission Strength'])

    return mat


# ─────────────────────────────────────────────
#  MATERIALS
# ─────────────────────────────────────────────

def build_materials():
    mats = {}
    mats['wood_hull']     = build_wood_mat(
        'Mat_Wood_Hull',
        dark=(0.33, 0.21, 0.04), light=(0.55, 0.38, 0.10),
        roughness=0.87, su=10.0)
    mats['wood_planks']   = build_wood_mat(
        'Mat_Wood_Planks',
        dark=(0.38, 0.24, 0.06), light=(0.62, 0.45, 0.14),
        roughness=0.90, su=13.0)
    mats['metal_dark']    = build_metal_mat(
        'Mat_Metal_Dark',
        base=(0.10, 0.10, 0.10), metallic=0.92, roughness=0.28)
    mats['sail_canvas']   = build_canvas_mat(
        'Mat_Sail_Canvas',
        base=(0.91, 0.88, 0.75))
    mats['lantern_glass'] = build_glass_mat(
        'Mat_Lantern_Glass',
        base=(1.0, 1.0, 0.67), emission_str=2.5)
    mats['rope']          = build_rope_mat(
        'Mat_Rope',
        base=(0.77, 0.64, 0.35))
    return mats


# ─────────────────────────────────────────────
#  1. BOAT HULL
# ─────────────────────────────────────────────

def create_hull(mats):
    """
    V-shaped hull: raised bow, flat stern.
    Built with bmesh cross-sections extruded along the length axis (Y).
    """
    me = bpy.data.meshes.new('Boat_Hull')
    bm = bmesh.new()

    # Cross-section profile generator
    # Returns a list of (x, z) pairs for a V-bottom hull
    def hull_section(width, depth, floor_w, deck_h):
        hw = width / 2.0
        fw = floor_w / 2.0
        pts = [
            (-hw,   0.0),       # deck port gunwale
            (-fw,  -depth),     # keel port
            ( fw,  -depth),     # keel stbd
            ( hw,   0.0),       # deck stbd gunwale
        ]
        return pts

    # Stations along Y axis (bow → stern = +Y … -Y)
    stations = [
        # (y_pos, width, depth, floor_w, deck_h)
        ( 5.0, 0.3, 0.1, 0.05, 0.0),   # bow tip
        ( 4.0, 1.2, 1.0, 0.15, 0.0),
        ( 2.5, 2.4, 1.4, 0.30, 0.0),
        ( 0.5, 3.0, 1.5, 0.40, 0.0),
        (-1.5, 3.0, 1.5, 0.40, 0.0),
        (-3.5, 2.8, 1.3, 0.45, 0.0),
        (-5.0, 2.5, 0.9, 0.50, 0.0),   # stern (flat)
    ]

    loops = []
    for (y, w, d, fw, dh) in stations:
        pts = hull_section(w, d, fw, dh)
        ring = []
        for (x, z) in pts:
            v = bm.verts.new(Vector((x, y, z)))
            ring.append(v)
        loops.append(ring)

    # Side faces between consecutive stations
    for i in range(len(loops) - 1):
        a, b = loops[i], loops[i + 1]
        n = len(a)
        for j in range(n - 1):
            bm.faces.new([a[j], a[j+1], b[j+1], b[j]])

    # Cap stern (last station)
    stern = loops[-1]
    bm.faces.new(stern)

    # Cap bow (first station — just a face between 4 verts)
    bow = loops[0]
    bm.faces.new(bow)

    # Deck strip (top edge of each section)
    for i in range(len(loops) - 1):
        a, b = loops[i], loops[i + 1]
        bm.faces.new([a[0], b[0], b[-1], a[-1]])

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    hull = new_obj('Boat_Hull', me)
    hull.location = (0, 0, 0)

    # Subdivision surface
    sub = hull.modifiers.new('Subsurf', 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2

    assign_mat(hull, mats['wood_hull'])
    smart_uv(hull)
    return hull


# ─────────────────────────────────────────────
#  2. BOAT DECK
# ─────────────────────────────────────────────

def create_deck(mats):
    """Individual plank geometry on top of the hull."""
    me = bpy.data.meshes.new('Boat_Deck')
    bm = bmesh.new()

    plank_w   = 0.18
    plank_h   = 0.04
    plank_gap = 0.02
    deck_len  = 8.0    # bow to stern
    deck_w    = 2.6

    n_planks  = int(deck_w / (plank_w + plank_gap))
    start_x   = -(n_planks / 2.0) * (plank_w + plank_gap) + plank_w / 2.0

    for i in range(n_planks):
        x = start_x + i * (plank_w + plank_gap)
        verts = [
            bm.verts.new(Vector((x - plank_w/2,  deck_len/2,  0))),
            bm.verts.new(Vector((x + plank_w/2,  deck_len/2,  0))),
            bm.verts.new(Vector((x + plank_w/2, -deck_len/2,  0))),
            bm.verts.new(Vector((x - plank_w/2, -deck_len/2,  0))),
            bm.verts.new(Vector((x - plank_w/2,  deck_len/2,  plank_h))),
            bm.verts.new(Vector((x + plank_w/2,  deck_len/2,  plank_h))),
            bm.verts.new(Vector((x + plank_w/2, -deck_len/2,  plank_h))),
            bm.verts.new(Vector((x - plank_w/2, -deck_len/2,  plank_h))),
        ]
        faces = [
            [0,1,2,3], [4,5,6,7],
            [0,1,5,4], [2,3,7,6],
            [1,2,6,5], [0,3,7,4],
        ]
        for f in faces:
            bm.faces.new([verts[idx] for idx in f])

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    deck = new_obj('Boat_Deck', me)
    deck.location = (0, -0.5, 0.05)
    assign_mat(deck, mats['wood_planks'])
    smart_uv(deck)
    return deck


# ─────────────────────────────────────────────
#  3. BOAT CABIN
# ─────────────────────────────────────────────

def create_cabin(mats):
    """Small wooden wheelhouse, centre-rear, sloped roof."""
    me = bpy.data.meshes.new('Boat_Cabin')
    bm = bmesh.new()

    W, L, H = 1.5, 2.0, 1.8
    hw, hl = W/2, L/2
    ridge_h = H + 0.5

    # Base box verts
    base_verts = [
        bm.verts.new((-hw, -hl, 0)),
        bm.verts.new(( hw, -hl, 0)),
        bm.verts.new(( hw,  hl, 0)),
        bm.verts.new((-hw,  hl, 0)),
        bm.verts.new((-hw, -hl, H)),
        bm.verts.new(( hw, -hl, H)),
        bm.verts.new(( hw,  hl, H)),
        bm.verts.new((-hw,  hl, H)),
    ]
    # Roof ridge verts
    ridge_verts = [
        bm.verts.new((0, -hl, ridge_h)),
        bm.verts.new((0,  hl, ridge_h)),
    ]

    # Walls
    bm.faces.new([base_verts[0], base_verts[1], base_verts[5], base_verts[4]])
    bm.faces.new([base_verts[2], base_verts[3], base_verts[7], base_verts[6]])
    bm.faces.new([base_verts[1], base_verts[2], base_verts[6], base_verts[5]])
    bm.faces.new([base_verts[3], base_verts[0], base_verts[4], base_verts[7]])
    # Floor
    bm.faces.new([base_verts[0], base_verts[3], base_verts[2], base_verts[1]])
    # Roof slopes
    bm.faces.new([base_verts[4], base_verts[5], ridge_verts[0]])
    bm.faces.new([base_verts[6], base_verts[7], ridge_verts[1]])
    bm.faces.new([base_verts[5], base_verts[6], ridge_verts[1], ridge_verts[0]])
    bm.faces.new([base_verts[7], base_verts[4], ridge_verts[0], ridge_verts[1]])

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    cabin = new_obj('Boat_Cabin', me)
    cabin.location = (0, -2.0, 0.05)

    # Window boolean cut-outs (4 small boxes)
    for side, pos_y, pos_z in [
        ('front', -hl - 0.01,  H * 0.55),
        ('back',   hl + 0.01,  H * 0.55),
        ('left',  -hl + 0.4,   H * 0.55),
        ('right',  hl - 0.4,   H * 0.55),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1)
        win = bpy.context.active_object
        win.name = f'_win_cut_{side}'
        win.location = cabin.location + Vector((
            0 if 'front' in side or 'back' in side else (-hw - 0.05 if 'left' in side else hw + 0.05),
            pos_y + cabin.location.y - cabin.location.y,
            pos_z + cabin.location.z
        ))
        win.scale = (0.35, 0.05, 0.35)
        bool_mod = cabin.modifiers.new(f'Bool_{side}', 'BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = win
        bpy.ops.object.select_all(action='DESELECT')
        win.select_set(True)
        bpy.context.view_layer.objects.active = win

    activate(cabin)
    assign_mat(cabin, mats['wood_planks'])
    smart_uv(cabin)
    return cabin


# ─────────────────────────────────────────────
#  4. BOAT MAST
# ─────────────────────────────────────────────

def create_mast(mats):
    """Single wooden mast with crossbar at 4 m height."""
    me = bpy.data.meshes.new('Boat_Mast')
    bm = bmesh.new()

    bmesh.ops.create_cone(bm,
        cap_ends=True, cap_tris=False,
        segments=8,
        radius1=0.15, radius2=0.10,
        depth=6.0)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    mast = new_obj('Boat_Mast', me)
    mast.location = (0, 1.5, 3.05)   # Z offset so base sits at deck level

    # Crossbar
    cb_me = bpy.data.meshes.new('_crossbar')
    cb_bm = bmesh.new()
    bmesh.ops.create_cone(cb_bm,
        cap_ends=True, cap_tris=False,
        segments=8,
        radius1=0.06, radius2=0.06,
        depth=3.0)
    cb_bm.normal_update()
    cb_bm.to_mesh(cb_me)
    cb_bm.free()

    crossbar = new_obj('_Boat_Mast_Crossbar', cb_me)
    crossbar.rotation_euler = (0, math.radians(90), 0)
    crossbar.location = (0, 1.5, 4.05)   # 4 m up the mast

    assign_mat(mast, mats['wood_hull'])
    assign_mat(crossbar, mats['wood_hull'])
    smart_uv(mast)
    smart_uv(crossbar)

    crossbar.parent = mast
    return mast


# ─────────────────────────────────────────────
#  5. BOAT SAIL
# ─────────────────────────────────────────────

def create_sail(mats):
    """Rectangular sail, slightly billowed using a simple displacement."""
    me = bpy.data.meshes.new('Boat_Sail')
    bm = bmesh.new()

    cols, rows = 6, 8
    w, h = 3.0, 4.0
    for r in range(rows + 1):
        for c in range(cols + 1):
            u = c / cols
            v_  = r / rows
            x = (u - 0.5) * w
            z = v_ * h
            # Billow: push centre verts forward
            billow = math.sin(u * math.pi) * math.sin(v_ * math.pi) * 0.25
            bm.verts.new(Vector((x, billow, z)))

    bm.verts.ensure_lookup_table()
    for r in range(rows):
        for c in range(cols):
            i  = r * (cols + 1) + c
            bm.faces.new([
                bm.verts[i],
                bm.verts[i + 1],
                bm.verts[i + cols + 2],
                bm.verts[i + cols + 1],
            ])

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    sail = new_obj('Boat_Sail', me)
    sail.location = (0, 1.5, 3.05)   # base of mast height

    assign_mat(sail, mats['sail_canvas'])
    smart_uv(sail)
    return sail


# ─────────────────────────────────────────────
#  6. HARPOON MOUNT
# ─────────────────────────────────────────────

def create_harpoon_mount(mats):
    """Metal rotating base + forward barrel. This object's world position
    is the harpoon spawn point in Unity (BoatController._harpoonSpawnPoint)."""
    me = bpy.data.meshes.new('Boat_HarpoonMount')
    bm = bmesh.new()

    # Rotating base disc
    bmesh.ops.create_cone(bm,
        cap_ends=True, cap_tris=False,
        segments=16,
        radius1=0.3, radius2=0.3,
        depth=0.2)

    # Barrel tube (translated forward)
    mat_fwd = Matrix.Translation(Vector((0, 0.5, 0.1)))
    barrel_result = bmesh.ops.create_cone(bm,
        cap_ends=True, cap_tris=False,
        segments=8,
        radius1=0.08, radius2=0.08,
        depth=0.8)

    # Translate barrel verts forward
    for v in barrel_result['verts']:
        v.co = mat_fwd @ v.co

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    mount = new_obj('Boat_HarpoonMount', me)
    mount.location = (0, 4.5, 0.2)   # bow of boat, deck level
    mount.rotation_euler = (math.radians(-90), 0, 0)

    assign_mat(mount, mats['metal_dark'])
    smart_uv(mount)
    return mount


# ─────────────────────────────────────────────
#  7. BOAT LANTERN
# ─────────────────────────────────────────────

def create_lantern(mats):
    """Hexagonal cage lantern on left side of cabin.
    The glass inside is assigned the emissive material."""

    # Cage — hexagonal prism (outer frame)
    cage_me = bpy.data.meshes.new('Boat_Lantern')
    bm = bmesh.new()
    bmesh.ops.create_cone(bm,
        cap_ends=True, cap_tris=False,
        segments=6,
        radius1=0.15, radius2=0.15,
        depth=0.25)
    bm.normal_update()
    bm.to_mesh(cage_me)
    bm.free()

    lantern = new_obj('Boat_Lantern', cage_me)
    lantern.location = (-1.0, -2.2, 1.4)   # left side of cabin, eye height
    assign_mat(lantern, mats['metal_dark'])

    # Glass pane (inner smaller hexagon, emissive)
    glass_me = bpy.data.meshes.new('Boat_Lantern_Glass')
    bm2 = bmesh.new()
    bmesh.ops.create_cone(bm2,
        cap_ends=True, cap_tris=False,
        segments=6,
        radius1=0.10, radius2=0.10,
        depth=0.22)
    bm2.normal_update()
    bm2.to_mesh(glass_me)
    bm2.free()

    glass = new_obj('Boat_Lantern_Glass', glass_me)
    glass.location = lantern.location.copy()
    glass.parent   = lantern
    assign_mat(glass, mats['lantern_glass'])

    # Hook bracket (thin cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6, radius=0.015, depth=0.3,
        location=(lantern.location.x, lantern.location.y, lantern.location.z + 0.28))
    hook = bpy.context.active_object
    hook.name = '_Lantern_Hook'
    hook.parent = lantern
    assign_mat(hook, mats['metal_dark'])

    smart_uv(lantern)
    smart_uv(glass)
    return lantern


# ─────────────────────────────────────────────
#  8. BOAT ANCHOR
# ─────────────────────────────────────────────

def create_anchor(mats):
    """Traditional anchor: ring + shank + flukes + chain links."""
    me = bpy.data.meshes.new('Boat_Anchor')
    bm = bmesh.new()

    # Shank (vertical bar)
    bmesh.ops.create_cone(bm,
        cap_ends=True, cap_tris=False,
        segments=8,
        radius1=0.04, radius2=0.03,
        depth=0.7)

    # Stock bar (horizontal, at top)
    stock_res = bmesh.ops.create_cone(bm,
        cap_ends=True, cap_tris=False,
        segments=8,
        radius1=0.03, radius2=0.03,
        depth=0.5)
    for v in stock_res['verts']:
        v.co = Matrix.Rotation(math.radians(90), 4, 'Y') @ v.co
        v.co.z += 0.35

    # Fluke arms (2 curved prongs at bottom)
    for side in (-1, 1):
        fluke_res = bmesh.ops.create_cone(bm,
            cap_ends=True, cap_tris=False,
            segments=6,
            radius1=0.025, radius2=0.015,
            depth=0.35)
        for v in fluke_res['verts']:
            v.co = Matrix.Rotation(math.radians(45 * side), 4, 'Y') @ v.co
            v.co.z -= 0.25
            v.co.x += 0.08 * side

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    anchor = new_obj('Boat_Anchor', me)
    anchor.location = (0, 4.2, -0.8)
    assign_mat(anchor, mats['metal_dark'])

    # Chain links (8 cylinders, each slightly offset + rotated)
    prev = anchor
    for i in range(8):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.05, minor_radius=0.015,
            major_segments=12, minor_segments=6,
            location=(0, 4.2, -0.8 + 0.07 * (i + 1)))
        link = bpy.context.active_object
        link.name = f'_chain_link_{i}'
        link.rotation_euler = (0, math.radians(90 if i % 2 == 0 else 0), 0)
        link.parent = anchor
        assign_mat(link, mats['metal_dark'])

    smart_uv(anchor)
    return anchor


# ─────────────────────────────────────────────
#  9. BOAT RUDDER
# ─────────────────────────────────────────────

def create_rudder(mats):
    """Flat wooden rudder at stern, mostly underwater."""
    me = bpy.data.meshes.new('Boat_Rudder')
    bm = bmesh.new()

    verts = [
        bm.verts.new((-0.05, 0, -0.6)),
        bm.verts.new(( 0.05, 0, -0.6)),
        bm.verts.new(( 0.05, 0,  0.5)),
        bm.verts.new((-0.05, 0,  0.5)),
        bm.verts.new((-0.3,  0, -0.9)),
        bm.verts.new(( 0.3,  0, -0.9)),
    ]
    bm.faces.new([verts[0], verts[1], verts[5], verts[4]])
    bm.faces.new([verts[0], verts[3], verts[2], verts[1]])

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    rudder = new_obj('Boat_Rudder', me)
    rudder.location = (0, -5.0, -0.3)
    assign_mat(rudder, mats['wood_hull'])
    smart_uv(rudder)
    return rudder


# ─────────────────────────────────────────────
#  10. BOAT RAILING
# ─────────────────────────────────────────────

def create_railing(mats):
    """Rope railing along both sides using a bezier curve with bevel."""
    railings = []
    for side, x_sign in [('Port', -1), ('Stbd', 1)]:
        bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0))
        curve_obj = bpy.context.active_object
        curve_obj.name = f'Boat_Railing_{side}'

        spline = curve_obj.data.splines[0]
        spline.bezier_points[0].co = Vector((x_sign * 1.35,  4.2, 0.35))
        spline.bezier_points[1].co = Vector((x_sign * 1.35, -4.8, 0.35))

        for bp in spline.bezier_points:
            bp.handle_left_type  = 'AUTO'
            bp.handle_right_type = 'AUTO'

        curve_obj.data.bevel_depth  = 0.025
        curve_obj.data.bevel_resolution = 3
        curve_obj.data.use_fill_caps = True

        assign_mat(curve_obj, mats['rope'])
        railings.append(curve_obj)
    return railings


# ─────────────────────────────────────────────
#  SCENE ORGANISATION
# ─────────────────────────────────────────────

def build_collection_and_root(all_objects):
    # Create collection
    col = bpy.data.collections.new('IsleTrial_Boat')
    bpy.context.scene.collection.children.link(col)

    # Create ROOT empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = 'Boat_ROOT'

    # Move all objects into collection and parent to ROOT
    for obj in all_objects:
        # Move to collection
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
        if obj.name != 'Boat_ROOT' and obj.parent is None:
            obj.parent = root

    # Move ROOT itself into collection
    for c in root.users_collection:
        c.objects.unlink(root)
    col.objects.link(root)

    return root


def set_origins(all_objects):
    for obj in all_objects:
        if obj.type in ('MESH', 'CURVE', 'EMPTY'):
            activate(obj)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')


def apply_all_transforms(all_objects):
    for obj in all_objects:
        if obj.type in ('MESH', 'CURVE'):
            apply_transforms(obj)


# ─────────────────────────────────────────────
#  CONSOLE EXPORT REPORT
# ─────────────────────────────────────────────

def print_export_info(all_objects, harpoon_mount):
    print("\n" + "="*60)
    print("  IsleTrial Boat — Export Report")
    print("="*60)
    for obj in all_objects:
        if obj.type in ('MESH', 'CURVE', 'EMPTY'):
            pos = obj.location
            print(f"  {obj.name:<30} pos=({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f})")
    hp = harpoon_mount.location
    print(f"\nHarpoon spawn point: ({hp.x:.3f}, {hp.y:.3f}, {hp.z:.3f})")
    print("\nReady to export: Select Boat_ROOT and export as FBX")
    print("="*60 + "\n")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    clear_scene()

    mats = build_materials()

    hull     = create_hull(mats)
    deck     = create_deck(mats)
    cabin    = create_cabin(mats)
    mast     = create_mast(mats)
    sail     = create_sail(mats)
    harpoon  = create_harpoon_mount(mats)
    lantern  = create_lantern(mats)
    anchor   = create_anchor(mats)
    rudder   = create_rudder(mats)
    railings = create_railing(mats)

    primary_objects = [hull, deck, cabin, mast, sail, harpoon, lantern, anchor, rudder]
    all_objects     = primary_objects + railings

    # Collect any helper objects created during build
    scene_objects = list(bpy.context.scene.collection.objects)
    extra = [o for o in scene_objects if o not in all_objects and o.name != 'Boat_ROOT']
    all_objects += extra

    set_origins(all_objects)
    apply_all_transforms(all_objects)

    root = build_collection_and_root(all_objects)

    # Viewport: Material Preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
            break

    print_export_info(all_objects, harpoon)


main()
