"""
IsleTrial — Environment Pack
02A  Tropical Island Terrain
02B  Wooden Dock / Pier
02C  Modular Rock Pack  (Rock_A … Rock_H)
02D  Lighthouse

Blender 4.x Python Script
Run inside Blender → Scripting workspace → Run Script.

Each section is wrapped in its own function so you can call only the
parts you need.  Call   main()   to build everything at once.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ═══════════════════════════════════════════════════════
#  GLOBAL HELPERS
# ═══════════════════════════════════════════════════════

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for curve in list(bpy.data.curves):
        bpy.data.curves.remove(curve)


def link_to_scene(obj):
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)


def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def new_mesh_obj(name, bm_data):
    me = bpy.data.meshes.new(name)
    bm_data.normal_update()
    bm_data.to_mesh(me)
    bm_data.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def apply_all(obj):
    activate(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def smart_uv(obj, angle=66, margin=0.02):
    activate(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')


def set_origin_to_bottom(obj):
    activate(obj)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location.z -= obj.dimensions.z / 2


def set_origin_center(obj):
    activate(obj)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')


def make_collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def move_to_collection(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def make_root_empty(name, location=(0, 0, 0)):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    root = bpy.context.active_object
    root.name = name
    return root


def parent_to(child, parent):
    if child.parent is None:
        child.parent = parent


def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def hex_to_rgb(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


# ═══════════════════════════════════════════════════════════════════════
#  RICH MATERIAL BUILDER
#
#  Every material has TWO parallel paths wired into a Mix node:
#
#   [Procedural nodes]  ──┐
#                         ├─ Mix (Fac=0) → BSDF   ← Blender preview
#   [Image Tex slot]   ──┘
#
#  Mix Factor = 0  →  100 % procedural  (default — no files needed)
#  Mix Factor = 1  →  100 % image tex   (load Unity PBR map & flip)
#
#  Image Texture nodes are labelled "[UNITY] MatName_Channel" —
#  find them in Shader Editor to slot in your Unity texture maps.
# ═══════════════════════════════════════════════════════════════════════

def _n(nodes, node_type, loc, label=None):
    nd = nodes.new(node_type)
    nd.location = loc
    if label:
        nd.label = label
    return nd


def _img(nodes, slot_name, loc):
    """Empty Image Texture placeholder — load your Unity PBR map here."""
    nd = nodes.new('ShaderNodeTexImage')
    nd.location = loc
    nd.label = f'[UNITY] {slot_name}'
    nd.name  = slot_name
    return nd


def _mapping(nodes, links, scale=(1.0, 1.0, 1.0), loc=(-900, 0)):
    tc = _n(nodes, 'ShaderNodeTexCoord', (-1100, 0))
    mp = _n(nodes, 'ShaderNodeMapping',   loc)
    mp.inputs['Scale'].default_value = (scale[0], scale[1], scale[2])
    links.new(tc.outputs['UV'], mp.inputs['Vector'])
    return tc, mp


def _mix_pi(nodes, links, proc_socket, img_nd, loc, lbl=''):
    """Mix:  proc → Color1,  image → Color2.  Factor 0 = procedural."""
    mix = _n(nodes, 'ShaderNodeMixRGB', loc, label=f'Mix {lbl}')
    mix.blend_type = 'MIX'
    mix.inputs['Fac'].default_value = 0.0
    links.new(proc_socket,             mix.inputs['Color1'])
    links.new(img_nd.outputs['Color'], mix.inputs['Color2'])
    return mix


# ── Wood  ─────────────────────────────────────────────────────────────
def build_wood_mat(name, dark, light, roughness=0.90, metallic=0.0, su=10.0):
    """Wave grain + noise surface.  Image slots: Albedo · Normal · Roughness"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (1100, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (680,  0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value = metallic

    _, mp = _mapping(nd, lk, scale=(su, 1.0, 1.0))

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

    img_a = _img(nd, f'{name}_Albedo', (-480, -260))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, ov.outputs['Color'], img_a, (280, 250), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    noise_n = _n(nd, 'ShaderNodeTexNoise', (-480, -500))
    noise_n.inputs['Scale'].default_value = 35.0; noise_n.inputs['Detail'].default_value = 10.0
    lk.new(mp.outputs['Vector'], noise_n.inputs['Vector'])
    bump = _n(nd, 'ShaderNodeBump', (-80, -430))
    bump.inputs['Strength'].default_value = 0.55; bump.inputs['Distance'].default_value = 0.05
    lk.new(noise_n.outputs['Fac'], bump.inputs['Height'])

    img_n = _img(nd, f'{name}_Normal', (-480, -720))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd, 'ShaderNodeNormalMap', (-80, -690))
    lk.new(img_n.outputs['Color'], nmap.inputs['Color'])

    mix_n = _n(nd, 'ShaderNodeMixRGB', (160, -560), label='Mix Normal')
    mix_n.inputs['Fac'].default_value = 0.0
    lk.new(bump.outputs['Normal'], mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'], mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])

    noise_r = _n(nd, 'ShaderNodeTexNoise', (-480, -960))
    noise_r.inputs['Scale'].default_value = 50.0
    lk.new(mp.outputs['Vector'], noise_r.inputs['Vector'])
    mrng = _n(nd, 'ShaderNodeMapRange', (-180, -960))
    mrng.inputs['To Min'].default_value = roughness - 0.08
    mrng.inputs['To Max'].default_value = roughness + 0.07
    lk.new(noise_r.outputs['Fac'], mrng.inputs['Value'])

    img_r = _img(nd, f'{name}_Roughness', (-480, -1160))
    lk.new(mp.outputs['Vector'], img_r.inputs['Vector'])
    mix_r = _n(nd, 'ShaderNodeMixRGB', (200, -960), label='Mix Roughness')
    mix_r.inputs['Fac'].default_value = 0.0
    lk.new(mrng.outputs['Result'], mix_r.inputs['Color1'])
    lk.new(img_r.outputs['Color'], mix_r.inputs['Color2'])
    lk.new(mix_r.outputs['Color'], bsdf.inputs['Roughness'])

    return mat


# ── Stone / Rock  ─────────────────────────────────────────────────────
def build_stone_mat(name, dark, light, roughness=0.88, metallic=0.0, wet=False):
    """
    Musgrave for large-scale rock variation + Voronoi crack overlay.
    Wet rocks get a height-based gloss mix (low roughness near base).
    Image slots: Albedo · Normal · Roughness
    """
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (1200, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (780,  0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value = metallic

    _, mp = _mapping(nd, lk, scale=(2.0, 2.0, 2.0))

    # Musgrave for base colour variation
    musg = _n(nd, 'ShaderNodeTexMusgrave', (-480, 300))
    musg.musgrave_type = 'FBM'
    musg.inputs['Scale'].default_value    = 3.5
    musg.inputs['Detail'].default_value   = 8.0
    musg.inputs['Lacunarity'].default_value = 2.0
    musg.inputs['Dimension'].default_value  = 0.8
    lk.new(mp.outputs['Vector'], musg.inputs['Vector'])

    cramp = _n(nd, 'ShaderNodeValToRGB', (-180, 300))
    cramp.color_ramp.elements[0].position = 0.30; cramp.color_ramp.elements[0].color = (*dark,  1.0)
    cramp.color_ramp.elements[1].position = 0.80; cramp.color_ramp.elements[1].color = (*light, 1.0)
    lk.new(musg.outputs['Fac'], cramp.inputs['Fac'])

    # Voronoi crack overlay
    voro = _n(nd, 'ShaderNodeTexVoronoi', (-480, 50))
    voro.inputs['Scale'].default_value = 6.0
    lk.new(mp.outputs['Vector'], voro.inputs['Vector'])
    ov = _n(nd, 'ShaderNodeMixRGB', (50, 220))
    ov.blend_type = 'MULTIPLY'; ov.inputs['Fac'].default_value = 0.35
    lk.new(cramp.outputs['Color'], ov.inputs['Color1'])
    lk.new(voro.outputs['Color'],  ov.inputs['Color2'])

    img_a = _img(nd, f'{name}_Albedo', (-480, -260))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, ov.outputs['Color'], img_a, (300, 220), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    # Normal — musgrave bump + voronoi cracks
    bump = _n(nd, 'ShaderNodeBump', (-80, -440))
    bump.inputs['Strength'].default_value = 0.85; bump.inputs['Distance'].default_value = 0.08
    lk.new(musg.outputs['Fac'], bump.inputs['Height'])

    img_n = _img(nd, f'{name}_Normal', (-480, -640))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd, 'ShaderNodeNormalMap', (-80, -610))
    lk.new(img_n.outputs['Color'], nmap.inputs['Color'])

    mix_n = _n(nd, 'ShaderNodeMixRGB', (160, -510), label='Mix Normal')
    mix_n.inputs['Fac'].default_value = 0.0
    lk.new(bump.outputs['Normal'], mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'], mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])

    # Roughness — Musgrave variation; wet rocks get extra gloss at bottom
    musg_r = _n(nd, 'ShaderNodeTexMusgrave', (-480, -900))
    musg_r.inputs['Scale'].default_value = 8.0
    lk.new(mp.outputs['Vector'], musg_r.inputs['Vector'])
    mrng = _n(nd, 'ShaderNodeMapRange', (-180, -900))
    mrng.inputs['To Min'].default_value = roughness - 0.12
    mrng.inputs['To Max'].default_value = roughness + 0.08
    lk.new(musg_r.outputs['Fac'], mrng.inputs['Value'])

    if wet:
        # Gradient: low-Z = wet (low roughness), high-Z = dry
        tc_w = _n(nd, 'ShaderNodeTexCoord', (-480, -1100))
        sep  = _n(nd, 'ShaderNodeSeparateXYZ', (-280, -1100))
        lk.new(tc_w.outputs['Generated'], sep.inputs['Vector'])
        mrng_wet = _n(nd, 'ShaderNodeMapRange', (-80, -1100))
        mrng_wet.inputs['From Min'].default_value = 0.0
        mrng_wet.inputs['From Max'].default_value = 0.5
        mrng_wet.inputs['To Min'].default_value   = 0.18
        mrng_wet.inputs['To Max'].default_value   = roughness
        lk.new(sep.outputs['Z'], mrng_wet.inputs['Value'])
        mix_wet = _n(nd, 'ShaderNodeMixRGB', (160, -1000), label='Wet Blend')
        mix_wet.inputs['Fac'].default_value = 0.0
        lk.new(mrng.outputs['Result'],     mix_wet.inputs['Color1'])
        lk.new(mrng_wet.outputs['Result'], mix_wet.inputs['Color2'])
        final_rough = mix_wet.outputs['Color']
    else:
        final_rough = mrng.outputs['Result']

    img_r = _img(nd, f'{name}_Roughness', (-480, -1300))
    lk.new(mp.outputs['Vector'], img_r.inputs['Vector'])
    mix_r = _n(nd, 'ShaderNodeMixRGB', (360, -900), label='Mix Roughness')
    mix_r.inputs['Fac'].default_value = 0.0
    lk.new(final_rough,            mix_r.inputs['Color1'])
    lk.new(img_r.outputs['Color'], mix_r.inputs['Color2'])
    lk.new(mix_r.outputs['Color'], bsdf.inputs['Roughness'])

    return mat


# ── Sand  ─────────────────────────────────────────────────────────────
def build_sand_mat(name, base):
    """
    Wave ripple texture for beach sand detail.
    Image slots: Albedo · Normal · Roughness
    """
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (1000, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (600,  0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Metallic'].default_value  = 0.0

    _, mp = _mapping(nd, lk, scale=(5.0, 5.0, 5.0))

    # Large ripple waves
    wave = _n(nd, 'ShaderNodeTexWave', (-480, 280))
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value      = 30.0
    wave.inputs['Distortion'].default_value = 0.8
    wave.inputs['Detail'].default_value     = 6.0
    lk.new(mp.outputs['Vector'], wave.inputs['Vector'])

    # Fine grain noise
    grain = _n(nd, 'ShaderNodeTexNoise', (-480, 50))
    grain.inputs['Scale'].default_value = 120.0; grain.inputs['Detail'].default_value = 8.0
    grain.inputs['Roughness'].default_value = 0.55
    lk.new(mp.outputs['Vector'], grain.inputs['Vector'])

    cramp = _n(nd, 'ShaderNodeValToRGB', (-180, 280))
    cramp.color_ramp.elements[0].color = (*tuple(max(c-0.07,0) for c in base), 1.0)
    cramp.color_ramp.elements[1].color = (*tuple(min(c+0.06,1) for c in base), 1.0)
    lk.new(wave.outputs['Color'], cramp.inputs['Fac'])

    ov = _n(nd, 'ShaderNodeMixRGB', (50, 200))
    ov.blend_type = 'OVERLAY'; ov.inputs['Fac'].default_value = 0.15
    lk.new(cramp.outputs['Color'], ov.inputs['Color1'])
    lk.new(grain.outputs['Color'], ov.inputs['Color2'])

    img_a = _img(nd, f'{name}_Albedo', (-480, -240))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, ov.outputs['Color'], img_a, (280, 200), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    # Normal — wave ripple bump
    bump = _n(nd, 'ShaderNodeBump', (-80, -400))
    bump.inputs['Strength'].default_value = 0.35; bump.inputs['Distance'].default_value = 0.03
    lk.new(wave.outputs['Color'], bump.inputs['Height'])

    img_n = _img(nd, f'{name}_Normal', (-480, -560))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd, 'ShaderNodeNormalMap', (-80, -530))
    lk.new(img_n.outputs['Color'], nmap.inputs['Color'])

    mix_n = _n(nd, 'ShaderNodeMixRGB', (160, -460), label='Mix Normal')
    mix_n.inputs['Fac'].default_value = 0.0
    lk.new(bump.outputs['Normal'], mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'], mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])

    return mat


# ── Grass  ────────────────────────────────────────────────────────────
def build_grass_mat(name, base, subsurface=0.08):
    """
    Noise-driven colour variation + subsurface for translucent blades.
    Image slots: Albedo · Normal
    """
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (1000, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (600,  0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.90
    bsdf.inputs['Metallic'].default_value  = 0.0
    bsdf.inputs['Subsurface Weight'].default_value = subsurface
    bsdf.inputs['Subsurface Radius'].default_value = (0.12, 0.28, 0.08)

    _, mp = _mapping(nd, lk, scale=(3.0, 3.0, 3.0))

    noise = _n(nd, 'ShaderNodeTexNoise', (-480, 280))
    noise.inputs['Scale'].default_value = 4.0; noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])

    cramp = _n(nd, 'ShaderNodeValToRGB', (-180, 280))
    cramp.color_ramp.elements[0].color = (*tuple(max(c-0.10,0) for c in base), 1.0)
    cramp.color_ramp.elements[1].color = (*tuple(min(c+0.08,1) for c in base), 1.0)
    lk.new(noise.outputs['Color'], cramp.inputs['Fac'])

    img_a = _img(nd, f'{name}_Albedo', (-480, -200))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, cramp.outputs['Color'], img_a, (280, 240), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    bump = _n(nd, 'ShaderNodeBump', (-80, -380))
    bump.inputs['Strength'].default_value = 0.3; bump.inputs['Distance'].default_value = 0.04
    lk.new(noise.outputs['Fac'], bump.inputs['Height'])

    img_n = _img(nd, f'{name}_Normal', (-480, -520))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd, 'ShaderNodeNormalMap', (-80, -490))
    lk.new(img_n.outputs['Color'], nmap.inputs['Color'])

    mix_n = _n(nd, 'ShaderNodeMixRGB', (160, -430), label='Mix Normal')
    mix_n.inputs['Fac'].default_value = 0.0
    lk.new(bump.outputs['Normal'], mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'], mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])

    return mat


# ── Dirt  ─────────────────────────────────────────────────────────────
def build_dirt_mat(name, base):
    """Dirt path: Musgrave colour clumps + noise bump."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (900, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (500, 0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Metallic'].default_value  = 0.0

    _, mp = _mapping(nd, lk, scale=(4.0, 4.0, 4.0))

    musg = _n(nd, 'ShaderNodeTexMusgrave', (-480, 200))
    musg.inputs['Scale'].default_value = 5.0; musg.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['Vector'], musg.inputs['Vector'])
    cramp = _n(nd, 'ShaderNodeValToRGB', (-180, 200))
    cramp.color_ramp.elements[0].color = (*tuple(max(c-0.12,0) for c in base), 1.0)
    cramp.color_ramp.elements[1].color = (*base, 1.0)
    lk.new(musg.outputs['Fac'], cramp.inputs['Fac'])

    img_a = _img(nd, f'{name}_Albedo', (-480, -200))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, cramp.outputs['Color'], img_a, (260, 200), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    bump = _n(nd, 'ShaderNodeBump', (-80, -360))
    bump.inputs['Strength'].default_value = 0.4; bump.inputs['Distance'].default_value = 0.04
    lk.new(musg.outputs['Fac'], bump.inputs['Height'])
    lk.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


# ── Metal  ────────────────────────────────────────────────────────────
def build_metal_mat(name, base, metallic=0.85, roughness=0.4):
    """Dark metal with noise surface + scratch roughness variation."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (1000, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (600,  0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value = metallic

    _, mp = _mapping(nd, lk, scale=(3.0, 3.0, 3.0))

    noise_c = _n(nd, 'ShaderNodeTexNoise', (-480, 260))
    noise_c.inputs['Scale'].default_value = 120.0; noise_c.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['Vector'], noise_c.inputs['Vector'])
    cramp = _n(nd, 'ShaderNodeValToRGB', (-200, 260))
    cramp.color_ramp.elements[0].color = (*base, 1.0)
    cramp.color_ramp.elements[1].color = (*tuple(min(c+0.07,1) for c in base), 1.0)
    lk.new(noise_c.outputs['Fac'], cramp.inputs['Fac'])

    img_a = _img(nd, f'{name}_Albedo', (-480, -180))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, cramp.outputs['Color'], img_a, (260, 220), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    scratch = _n(nd, 'ShaderNodeTexNoise', (-480, -380))
    scratch.inputs['Scale'].default_value = 300.0; scratch.inputs['Detail'].default_value = 12.0
    lk.new(mp.outputs['Vector'], scratch.inputs['Vector'])
    mrng = _n(nd, 'ShaderNodeMapRange', (-180, -380))
    mrng.inputs['To Min'].default_value = roughness
    mrng.inputs['To Max'].default_value = roughness + 0.28
    lk.new(scratch.outputs['Fac'], mrng.inputs['Value'])

    img_r = _img(nd, f'{name}_Roughness', (-480, -580))
    lk.new(mp.outputs['Vector'], img_r.inputs['Vector'])
    mix_r = _n(nd, 'ShaderNodeMixRGB', (160, -380), label='Mix Roughness')
    mix_r.inputs['Fac'].default_value = 0.0
    lk.new(mrng.outputs['Result'], mix_r.inputs['Color1'])
    lk.new(img_r.outputs['Color'], mix_r.inputs['Color2'])
    lk.new(mix_r.outputs['Color'], bsdf.inputs['Roughness'])

    noise_n = _n(nd, 'ShaderNodeTexNoise', (-480, -800))
    noise_n.inputs['Scale'].default_value = 200.0
    lk.new(mp.outputs['Vector'], noise_n.inputs['Vector'])
    bump = _n(nd, 'ShaderNodeBump', (-80, -720))
    bump.inputs['Strength'].default_value = 0.18
    lk.new(noise_n.outputs['Fac'], bump.inputs['Height'])
    lk.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


# ── Rope  ─────────────────────────────────────────────────────────────
def build_rope_mat(name, base):
    """Diagonal wave bands for twisted fibre look."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
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

    img_a = _img(nd, f'{name}_Albedo', (-480, -240))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd, lk, cramp.outputs['Color'], img_a, (260, 240), 'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    bump = _n(nd, 'ShaderNodeBump', (-80, -420))
    bump.inputs['Strength'].default_value = 0.85; bump.inputs['Distance'].default_value = 0.03
    lk.new(wave.outputs['Color'], bump.inputs['Height'])
    lk.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


# ── Glass Transmission  ───────────────────────────────────────────────
def build_glass_trans_mat(name, base, alpha=0.15, ior=1.45):
    """Physically correct transmission glass for lighthouse panels."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (700, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (300, 0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value          = (*base, 1.0)
    bsdf.inputs['Roughness'].default_value           = 0.05
    bsdf.inputs['Metallic'].default_value            = 0.0
    bsdf.inputs['Alpha'].default_value               = alpha
    bsdf.inputs['Transmission Weight'].default_value = 1.0
    bsdf.inputs['IOR'].default_value                 = ior

    return mat


# ── Emissive Beacon  ──────────────────────────────────────────────────
def build_emissive_mat(name, base, emission_str=5.0):
    """Pure emissive material for lighthouse beacon / lantern glass."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()

    out  = _n(nd, 'ShaderNodeOutputMaterial', (700, 0))
    bsdf = _n(nd, 'ShaderNodeBsdfPrincipled',  (300, 0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value          = (*base, 1.0)
    bsdf.inputs['Roughness'].default_value           = 0.0
    bsdf.inputs['Emission Color'].default_value      = (*base, 1.0)
    bsdf.inputs['Emission Strength'].default_value   = emission_str

    return mat


# ═══════════════════════════════════════════════════════
#  02-A  TROPICAL ISLAND
# ═══════════════════════════════════════════════════════

def build_island_materials():
    return {
        'sand'    : build_sand_mat('Mat_Sand',
                        hex_to_rgb('F5DEB3')),
        'grass'   : build_grass_mat('Mat_Grass_Island',
                        hex_to_rgb('4A7A35'), subsurface=0.10),
        'rock'    : build_stone_mat('Mat_Rock_Cliff',
                        dark=hex_to_rgb('3D3D3D'), light=hex_to_rgb('727272'),
                        roughness=0.88),
        'wet_rock': build_stone_mat('Mat_Rock_Wet',
                        dark=hex_to_rgb('252525'), light=hex_to_rgb('4A4A4A'),
                        roughness=0.28, metallic=0.05, wet=True),
        'dirt'    : build_dirt_mat('Mat_Dirt_Path',
                        hex_to_rgb('8B6347')),
    }


def smooth_falloff(dx, dy, radius):
    d = math.sqrt(dx*dx + dy*dy) / radius
    if d >= 1.0:
        return 0.0
    t = 1.0 - d
    return t * t * (3 - 2 * t)


def pseudo_noise(x, y, seed=0):
    """Simple deterministic noise (no numpy dependency)."""
    ix, iy = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - ix, y - iy
    def rnd(a, b):
        n = (a * 1619 + b * 31337 + seed * 6971) & 0x7FFFFFFF
        n = (n >> 13) ^ n
        return ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7FFFFFFF) / 2147483648.0
    v00 = rnd(ix,   iy)
    v10 = rnd(ix+1, iy)
    v01 = rnd(ix,   iy+1)
    v11 = rnd(ix+1, iy+1)
    fx3 = fx * fx * (3 - 2 * fx)
    fy3 = fy * fy * (3 - 2 * fy)
    return (v00*(1-fx3) + v10*fx3) * (1-fy3) + (v01*(1-fx3) + v11*fx3) * fy3


def create_island_terrain(mats):
    GRID    = 60
    SIZE_X  = 80.0
    SIZE_Y  = 60.0
    PEAK_H  = 20.0
    BEACH_H = 1.2
    BEACH_W = 10.0

    me = bpy.data.meshes.new('Island_Terrain')
    bm = bmesh.new()

    col_layer = bm.loops.layers.color.new('Col')

    verts = []
    for row in range(GRID + 1):
        row_v = []
        for col in range(GRID + 1):
            nx = (col / GRID - 0.5) * SIZE_X
            ny = (row / GRID - 0.5) * SIZE_Y
            cx, cy = nx / (SIZE_X * 0.5), ny / (SIZE_Y * 0.5)

            # Hill peak
            hill = smooth_falloff(cx, cy, 0.6) * PEAK_H
            # Beach ring
            dist = math.sqrt(cx*cx + cy*cy)
            beach_t = max(0.0, min(1.0, (dist - 0.55) / 0.35))
            beach_h = (1.0 - beach_t) * BEACH_H
            # North cliff wall
            cliff = 0.0
            if ny > SIZE_Y * 0.35:
                cliff_t = (ny - SIZE_Y * 0.35) / (SIZE_Y * 0.15)
                cliff_t = max(0.0, min(1.0, cliff_t))
                cliff = cliff_t * 12.0 * smooth_falloff(cx, 0.0, 0.8)
            # Surface noise
            noise = (pseudo_noise(nx * 0.15, ny * 0.15, 1) * 2.0 +
                     pseudo_noise(nx * 0.40, ny * 0.40, 2) * 0.8 +
                     pseudo_noise(nx * 0.90, ny * 0.90, 3) * 0.3) * 1.2
            z = max(beach_h, hill + noise * 0.5) + cliff
            v = bm.verts.new(Vector((nx, ny, z)))
            row_v.append(v)
        verts.append(row_v)

    bm.verts.ensure_lookup_table()

    faces = []
    for r in range(GRID):
        for c in range(GRID):
            f = bm.faces.new([verts[r][c], verts[r][c+1],
                              verts[r+1][c+1], verts[r+1][c]])
            faces.append(f)

    # Vertex color by height
    for f in bm.faces:
        avg_z = sum(v.co.z for v in f.verts) / len(f.verts)
        if avg_z < 1.5:
            col = (0.96, 0.87, 0.70, 1.0)   # sand
        elif avg_z < 8.0:
            col = (0.29, 0.48, 0.21, 1.0)   # grass
        elif avg_z < 14.0:
            col = (0.18, 0.35, 0.14, 1.0)   # jungle canopy
        else:
            col = (0.35, 0.35, 0.35, 1.0)   # cliff/rock
        for loop in f.loops:
            loop[col_layer] = col

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.calc_normals_split()

    terrain = bpy.data.objects.new('Island_Terrain', me)
    bpy.context.scene.collection.objects.link(terrain)

    sub = terrain.modifiers.new('Subsurf', 'SUBSURF')
    sub.levels = 2

    displace_tex = bpy.data.textures.new('Island_Clouds', type='CLOUDS')
    displace_tex.noise_scale = 8.0
    displace_mod = terrain.modifiers.new('Displace', 'DISPLACE')
    displace_mod.texture = displace_tex
    displace_mod.strength = 1.2
    displace_mod.mid_level = 0.5

    assign_mat(terrain, mats['grass'])
    smart_uv(terrain, angle=45, margin=0.01)
    return terrain


def create_island_cliffs(mats):
    me = bpy.data.meshes.new('Island_Cliffs_North')
    bm = bmesh.new()

    SEGS_X, SEGS_Z = 20, 12
    W, H = 30.0, 15.0

    verts = []
    for sz in range(SEGS_Z + 1):
        row = []
        for sx in range(SEGS_X + 1):
            x   = (sx / SEGS_X - 0.5) * W
            z   = (sz / SEGS_Z) * H
            noi = (pseudo_noise(x * 0.25, z * 0.35, 10) - 0.5) * 4.0
            # Overhang: upper sections lean outward
            lean = max(0.0, (sz / SEGS_Z - 0.5)) * 3.0
            y = noi + lean
            row.append(bm.verts.new(Vector((x, y, z))))
        verts.append(row)

    for r in range(SEGS_Z):
        for c in range(SEGS_X):
            bm.faces.new([verts[r][c], verts[r][c+1],
                          verts[r+1][c+1], verts[r+1][c]])

    # Cap bottom and sides
    bottom = [verts[0][c] for c in range(SEGS_X+1)]
    bot_back = [bm.verts.new(Vector((v.co.x, v.co.y - 2.0, 0))) for v in bottom]
    for i in range(SEGS_X):
        bm.faces.new([bottom[i], bottom[i+1], bot_back[i+1], bot_back[i]])

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    cliff = bpy.data.objects.new('Island_Cliffs_North', me)
    bpy.context.scene.collection.objects.link(cliff)
    cliff.location = (0, 30.0, 0)

    bevel = cliff.modifiers.new('Bevel', 'BEVEL')
    bevel.width = 0.15
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'

    assign_mat(cliff, mats['rock'])
    smart_uv(cliff)
    return cliff


def create_beach_ring(mats):
    me = bpy.data.meshes.new('Island_Beach_Sand')
    bm = bmesh.new()

    SEGS  = 48
    IR    = 18.0   # inner radius (where hill starts)
    OR    = 30.0   # outer edge, meets water

    for i in range(SEGS):
        a0 = (i / SEGS) * math.tau
        a1 = ((i+1) / SEGS) * math.tau
        ix0, iy0 = math.cos(a0) * IR, math.sin(a0) * IR
        ix1, iy1 = math.cos(a1) * IR, math.sin(a1) * IR
        ox0, oy0 = math.cos(a0) * OR, math.sin(a0) * OR
        ox1, oy1 = math.cos(a1) * OR, math.sin(a1) * OR
        vi  = bm.verts.new(Vector((ix0, iy0, 1.0)))
        vi1 = bm.verts.new(Vector((ix1, iy1, 1.0)))
        vo  = bm.verts.new(Vector((ox0, oy0, 0.0)))
        vo1 = bm.verts.new(Vector((ox1, oy1, 0.0)))
        bm.faces.new([vi, vo, vo1, vi1])

    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    beach = bpy.data.objects.new('Island_Beach_Sand', me)
    bpy.context.scene.collection.objects.link(beach)
    assign_mat(beach, mats['sand'])
    smart_uv(beach)
    return beach


def create_rocky_outcrops(mats):
    rng = random.Random(42)
    rocks = []
    placements = [
        (15, 8,  0.0, 2.5),
        (-12, 5, 0.2, 1.5),
        (8, -14,  0.0, 3.5),
        (-18, -8, 0.1, 2.0),
        (20, -10, 0.0, 1.8),
    ]
    for idx, (rx, ry, rz, size) in enumerate(placements):
        me = bpy.data.meshes.new(f'Rock_0{idx+1}')
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=size * 0.5)
        for v in bm.verts:
            nx = pseudo_noise(v.co.x * 2.1, v.co.y * 2.3, idx)
            ny = pseudo_noise(v.co.y * 2.5, v.co.z * 1.9, idx + 5)
            nz = pseudo_noise(v.co.z * 2.2, v.co.x * 2.7, idx + 10)
            v.co += Vector((nx - 0.5, ny - 0.5, nz - 0.5)) * size * 0.35
        bm.normal_update()
        bm.to_mesh(me)
        bm.free()

        rock = bpy.data.objects.new(f'Island_Rocky_Outcrops_Rock_0{idx+1}', me)
        bpy.context.scene.collection.objects.link(rock)
        rock.location = (rx, ry, rz - 0.3)
        assign_mat(rock, mats['wet_rock'] if rz < 0 else mats['rock'])
        smart_uv(rock)
        rocks.append(rock)
    return rocks


def build_island(col):
    mats    = build_island_materials()
    terrain = create_island_terrain(mats)
    cliffs  = create_island_cliffs(mats)
    beach   = create_beach_ring(mats)
    rocks   = create_rocky_outcrops(mats)

    all_objs = [terrain, cliffs, beach] + rocks
    root = make_root_empty('Island_ROOT')

    for obj in all_objs:
        set_origin_center(obj)
        apply_all(obj)
        move_to_collection(obj, col)
        parent_to(obj, root)

    move_to_collection(root, col)

    bb = terrain.dimensions
    print(f"\n[Island] Terrain bounding box: {bb.x:.1f}m x {bb.y:.1f}m x {bb.z:.1f}m")
    print(f"[Island] Approx beach ring area: {math.pi * (30**2 - 18**2):.0f} m²")
    print("[Island] Ready for Unity: Export Island_ROOT as FBX\n")
    return root


# ═══════════════════════════════════════════════════════
#  02-B  WOODEN DOCK
# ═══════════════════════════════════════════════════════

def build_dock_materials():
    return {
        'old_wood': build_wood_mat('Mat_Dock_Wood_Old',
                        dark=hex_to_rgb('4A3520'), light=hex_to_rgb('8C6A40'),
                        roughness=0.94, su=12.0),
        'wet_wood': build_wood_mat('Mat_Dock_Wood_Wet',
                        dark=hex_to_rgb('2E1E0A'), light=hex_to_rgb('6A4828'),
                        roughness=0.52, su=10.0),
        'rope'    : build_rope_mat('Mat_Dock_Rope',
                        hex_to_rgb('C4A35A')),
        'iron'    : build_metal_mat('Mat_Dock_Iron',
                        hex_to_rgb('1A1A1A'), metallic=0.82, roughness=0.58),
    }


def create_dock_platform(mats):
    bm = bmesh.new()
    plank_w   = 0.20
    plank_h   = 0.05
    plank_gap = 0.025
    dock_len  = 20.0
    dock_w    = 4.0
    n_planks  = int(dock_w / (plank_w + plank_gap))
    skip_set  = {7, 14}   # missing planks for realism
    rng = random.Random(7)

    for i in range(n_planks):
        if i in skip_set:
            continue
        x0 = -dock_w / 2 + i * (plank_w + plank_gap)
        x1 = x0 + plank_w
        dz = rng.uniform(-0.01, 0.01)
        z0, z1 = 0.0 + dz, plank_h + dz
        vs = [
            bm.verts.new((x0, 0.0,     z0)),
            bm.verts.new((x1, 0.0,     z0)),
            bm.verts.new((x1, dock_len, z0)),
            bm.verts.new((x0, dock_len, z0)),
            bm.verts.new((x0, 0.0,     z1)),
            bm.verts.new((x1, 0.0,     z1)),
            bm.verts.new((x1, dock_len, z1)),
            bm.verts.new((x0, dock_len, z1)),
        ]
        face_ids = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(0,3,7,4),(1,2,6,5)]
        for fi in face_ids:
            bm.faces.new([vs[k] for k in fi])

    obj = new_mesh_obj('Dock_MainPlatform', bm)
    obj.location = (0, 0, 1.2)
    assign_mat(obj, mats['old_wood'])
    smart_uv(obj)
    return obj


def create_dock_supports(mats):
    PAIRS     = 10
    SPACING   = 2.0
    POST_R    = 0.075
    POST_DPTH = 2.5
    rng = random.Random(13)
    objs = []

    for pi in range(PAIRS):
        y = pi * SPACING
        for side in (-1, 1):
            bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                                  segments=8,
                                  radius1=POST_R * 0.7, radius2=POST_R,
                                  depth=POST_DPTH)
            obj = new_mesh_obj(f'_dock_post_{pi}_{side}', bm)
            lean_x = rng.uniform(-math.radians(3), math.radians(3))
            lean_y = rng.uniform(-math.radians(3), math.radians(3))
            obj.rotation_euler = (lean_x, lean_y, 0)
            obj.location = (side * 1.8, y, 1.2 - POST_DPTH / 2)
            assign_mat(obj, mats['wet_wood'])
            objs.append(obj)

        # Cross-brace
        bm2 = bmesh.new()
        bmesh.ops.create_cone(bm2, cap_ends=True, cap_tris=False,
                              segments=6, radius1=0.05, radius2=0.05, depth=3.8)
        brace = new_mesh_obj(f'_dock_brace_{pi}', bm2)
        brace.rotation_euler = (0, math.radians(90), 0)
        brace.location = (0, y, 0.2)
        assign_mat(brace, mats['old_wood'])
        objs.append(brace)

    # Merge all support objects into one
    activate(objs[0])
    for o in objs[1:]:
        o.select_set(True)
    bpy.ops.object.join()
    support_obj = bpy.context.active_object
    support_obj.name = 'Dock_Supports'
    assign_mat(support_obj, mats['wet_wood'])
    smart_uv(support_obj)
    return support_obj


def create_dock_railings(mats):
    rail_objs = []
    for side, x_pos in [('Port', -2.1), ('Stbd', 2.1)]:
        for height_idx, h in enumerate([0.4, 0.7, 1.0]):
            curve_data = bpy.data.curves.new(f'_rail_curve_{side}_{height_idx}', 'CURVE')
            curve_data.dimensions = '3D'
            curve_data.bevel_depth  = 0.018
            curve_data.bevel_resolution = 4
            curve_data.use_fill_caps = True

            spline = curve_data.splines.new('NURBS')
            n_pts  = 12
            spline.points.add(n_pts - 1)
            for k in range(n_pts):
                y   = (k / (n_pts - 1)) * 20.0
                sag = math.sin(k / (n_pts - 1) * math.pi) * -0.05  # natural sag
                spline.points[k].co = (x_pos, y, 1.2 + h + sag, 1.0)

            spline.use_endpoint_u = True
            obj = bpy.data.objects.new(f'_dock_rail_{side}_{height_idx}', curve_data)
            bpy.context.scene.collection.objects.link(obj)
            assign_mat(obj, mats['rope'])
            rail_objs.append(obj)

    # Join all railing curves
    activate(rail_objs[0])
    for o in rail_objs[1:]:
        o.select_set(True)
    bpy.ops.object.join()
    railing = bpy.context.active_object
    railing.name = 'Dock_Railings'
    return railing


def create_mooring_posts(mats):
    objs = []
    for i, (x, y) in enumerate([(-1.5, 19.0), (1.5, 19.0), (-1.5, 17.5), (1.5, 17.5)]):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                              segments=8, radius1=0.10, radius2=0.10, depth=0.9)
        post = new_mesh_obj(f'_mooring_{i}', bm)
        post.location = (x, y, 1.2 + 0.45)
        assign_mat(post, mats['old_wood'])

        # Iron cap
        bm2 = bmesh.new()
        bmesh.ops.create_cone(bm2, cap_ends=True, cap_tris=False,
                              segments=8, radius1=0.12, radius2=0.08, depth=0.12)
        cap = new_mesh_obj(f'_mooring_cap_{i}', bm2)
        cap.location = (x, y, 1.2 + 0.9 + 0.06)
        assign_mat(cap, mats['iron'])

        # Rope ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.15, minor_radius=0.02,
            major_segments=16, minor_segments=6,
            location=(x, y, 1.2 + 0.5))
        rope_ring = bpy.context.active_object
        rope_ring.name = f'_mooring_rope_{i}'
        assign_mat(rope_ring, mats['rope'])

        objs += [post, cap, rope_ring]

    activate(objs[0])
    for o in objs[1:]:
        o.select_set(True)
    bpy.ops.object.join()
    merged = bpy.context.active_object
    merged.name = 'Dock_MooringPosts'
    smart_uv(merged)
    return merged


def create_dock_ladder(mats):
    objs = []
    RUNGS  = 6
    SIDE_R = 0.025
    RUNG_R = 0.015
    TOP_Y  = 1.2
    BOT_Y  = -0.8
    X_OFF  = 2.1

    for side_x in (-0.2, 0.2):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                              segments=6, radius1=SIDE_R, radius2=SIDE_R,
                              depth=abs(TOP_Y - BOT_Y))
        side = new_mesh_obj('_ladder_side', bm)
        side.location = (X_OFF + side_x, 0.5, (TOP_Y + BOT_Y) / 2)
        assign_mat(side, mats['rope'])
        objs.append(side)

    for r in range(RUNGS):
        t  = r / (RUNGS - 1)
        z  = BOT_Y + t * (TOP_Y - BOT_Y)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                              segments=6, radius1=RUNG_R, radius2=RUNG_R, depth=0.45)
        rung = new_mesh_obj(f'_ladder_rung_{r}', bm)
        rung.rotation_euler = (0, math.radians(90), 0)
        rung.location = (X_OFF, 0.5, z)
        assign_mat(rung, mats['old_wood'])
        objs.append(rung)

    activate(objs[0])
    for o in objs[1:]:
        o.select_set(True)
    bpy.ops.object.join()
    ladder = bpy.context.active_object
    ladder.name = 'Dock_Ladder'
    smart_uv(ladder)
    return ladder


def create_dock_accessories(mats):
    objs = []

    # Wooden crate
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.5)
    crate = new_mesh_obj('_crate', bm)
    crate.location = (1.0, 16.0, 1.2 + 0.25)
    assign_mat(crate, mats['old_wood'])
    smart_uv(crate)
    objs.append(crate)

    # Coil of rope
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.4, minor_radius=0.06,
        major_segments=24, minor_segments=8,
        location=(-1.2, 15.0, 1.2 + 0.06))
    coil = bpy.context.active_object
    coil.name = '_rope_coil'
    assign_mat(coil, mats['rope'])
    objs.append(coil)

    # Fishing net (simple grid mesh draped over railing)
    for ni, ny in enumerate([5.0, 12.0]):
        net_me = bpy.data.meshes.new(f'_net_{ni}')
        net_bm = bmesh.new()
        rows, cols = 8, 6
        for r in range(rows + 1):
            for c in range(cols + 1):
                u = c / cols
                v_ = r / rows
                x  = (u - 0.5) * 1.5 + 2.1
                z  = 1.2 + 1.0 - v_ * 1.4
                sag = math.sin(u * math.pi) * -0.15
                net_bm.verts.new(Vector((x, ny, z + sag)))
        net_bm.verts.ensure_lookup_table()
        for r in range(rows):
            for c in range(cols):
                i = r * (cols + 1) + c
                net_bm.faces.new([net_bm.verts[i], net_bm.verts[i+1],
                                  net_bm.verts[i+cols+2], net_bm.verts[i+cols+1]])
        net_bm.normal_update()
        net_bm.to_mesh(net_me)
        net_bm.free()
        net_obj = bpy.data.objects.new(f'_fishing_net_{ni}', net_me)
        bpy.context.scene.collection.objects.link(net_obj)
        assign_mat(net_obj, mats['rope'])
        objs.append(net_obj)

    activate(objs[0])
    for o in objs[1:]:
        o.select_set(True)
    bpy.ops.object.join()
    acc = bpy.context.active_object
    acc.name = 'Dock_Accessories'
    smart_uv(acc)
    return acc


def build_dock(col):
    mats     = build_dock_materials()
    platform = create_dock_platform(mats)
    supports = create_dock_supports(mats)
    railings = create_dock_railings(mats)
    moorings = create_mooring_posts(mats)
    ladder   = create_dock_ladder(mats)
    acc      = create_dock_accessories(mats)

    all_objs = [platform, supports, railings, moorings, ladder, acc]
    root = make_root_empty('Dock_ROOT')

    for obj in all_objs:
        set_origin_center(obj)
        apply_all(obj)
        move_to_collection(obj, col)
        parent_to(obj, root)

    move_to_collection(root, col)
    print("[Dock] Build complete — Dock_ROOT ready for FBX export.")
    return root


# ═══════════════════════════════════════════════════════
#  02-C  MODULAR ROCK PACK
# ═══════════════════════════════════════════════════════

ROCK_SPECS = {
    'Rock_A': dict(scale=(3.0, 2.0, 0.8), seed=1,  noise_s=1.8, disp=0.3, wet=False, mossy=False),
    'Rock_B': dict(scale=(0.6, 0.6, 2.5), seed=2,  noise_s=2.5, disp=0.4, wet=False, mossy=False),
    'Rock_C': dict(scale=(2.0, 2.0, 1.4), seed=3,  noise_s=1.5, disp=0.45, wet=False, mossy=False),
    'Rock_D': dict(scale=(1.5, 1.5, 1.2), seed=4,  noise_s=1.2, disp=0.18, wet=False, mossy=True),
    'Rock_E': dict(scale=(1.2, 0.9, 0.15),seed=5,  noise_s=3.0, disp=0.08, wet=False, mossy=False),
    'Rock_F': dict(scale=(1.8, 1.2, 1.6), seed=6,  noise_s=2.0, disp=0.5,  wet=False, mossy=False),
    'Rock_G': dict(scale=(2.0, 1.0, 1.0), seed=7,  noise_s=1.6, disp=0.35, wet=True,  mossy=False),
    'Rock_H': dict(scale=(2.2, 2.2, 1.5), seed=8,  noise_s=1.3, disp=0.4,  wet=False, mossy=False),
}


def build_rock_materials():
    rock_configs = {
        'Rock_A': ('6A6560', '8A8580', 0.90, 0.0,  False),
        'Rock_B': ('6F6865', '8F8C88', 0.88, 0.0,  False),
        'Rock_C': ('686360', '888078', 0.92, 0.0,  False),
        'Rock_D': ('485848', '687868', 0.87, 0.0,  False),  # mossy tint
        'Rock_E': ('72706C', '92908C', 0.90, 0.0,  False),
        'Rock_F': ('5E5B58', '7E7B78', 0.88, 0.0,  False),
        'Rock_G': ('2A2520', '4A4540', 0.26, 0.05, True),   # wet/submerged
        'Rock_H': ('6A6862', '8A8882', 0.91, 0.0,  False),
    }
    mats = {}
    for rname, (dark_h, light_h, rough, metal, wet) in rock_configs.items():
        mats[rname] = build_stone_mat(
            f'Mat_{rname}',
            dark=hex_to_rgb(dark_h), light=hex_to_rgb(light_h),
            roughness=rough, metallic=metal, wet=wet)
    return mats


def displace_verts(bm_obj, scale, strength, seed):
    for v in bm_obj.verts:
        n = (pseudo_noise(v.co.x * scale, v.co.y * scale, seed) +
             pseudo_noise(v.co.y * scale, v.co.z * scale, seed + 100) +
             pseudo_noise(v.co.z * scale, v.co.x * scale, seed + 200)) / 3.0
        v.co += v.normal * (n - 0.5) * strength


def create_single_rock(name, spec, mat):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.5)

    bm.verts.ensure_lookup_table()
    displace_verts(bm, spec['noise_s'], spec['disp'] * 1.5, spec['seed'])
    # Fine detail pass
    displace_verts(bm, spec['noise_s'] * 3, spec['disp'] * 0.5, spec['seed'] + 50)

    if name == 'Rock_C':
        # Cluster: add 2 satellite spheres merged
        for cx, cy in [(0.6, 0.4), (-0.5, 0.3)]:
            sphere = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.35)
            for v in sphere['verts']:
                v.co += Vector((cx, cy, -0.1))
                n = pseudo_noise(v.co.x * 2, v.co.y * 2, spec['seed'] + 20)
                v.co += v.normal * (n - 0.5) * 0.2

    if name == 'Rock_F':
        # Crack: split verts down center
        for v in bm.verts:
            if abs(v.co.x) < 0.06:
                v.co.x += 0.06 if v.co.x >= 0 else -0.06

    if name == 'Rock_H':
        # Pile: scatter extra small spheres
        for pi in range(4):
            rng = random.Random(pi + 99)
            sr = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.22)
            ox = rng.uniform(-0.5, 0.5)
            oy = rng.uniform(-0.5, 0.5)
            for v in sr['verts']:
                v.co += Vector((ox, oy, 0.0))

    bm.normal_update()
    obj = new_mesh_obj(name, bm)
    obj.scale = spec['scale']

    if spec['wet']:
        obj.location = (0, 0, -spec['scale'][2] * 0.4)  # partially submerged

    bevel = obj.modifiers.new('Bevel', 'BEVEL')
    bevel.width = 0.02
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'

    # Mossy vertex color
    if spec['mossy']:
        activate(obj)
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        bpy.ops.paint.vertex_color_set()
        bpy.ops.object.mode_set(mode='OBJECT')
        vcol = obj.data.vertex_colors.new(name='moss')
        for poly in obj.data.polygons:
            avg_z = sum(obj.data.vertices[vi].co.z for vi in poly.vertices) / len(poly.vertices)
            col = (0.24, 0.35, 0.19, 1.0) if avg_z > 0.0 else (0.38, 0.35, 0.32, 1.0)
            for li in poly.loop_indices:
                vcol.data[li].color = col

    assign_mat(obj, mat)
    apply_all(obj)
    smart_uv(obj)
    set_origin_to_bottom(obj)
    return obj


def build_rocks(col):
    mats = build_rock_materials()
    rock_objs = []
    grid_spacing = 5.0

    for idx, (name, spec) in enumerate(ROCK_SPECS.items()):
        obj = create_single_rock(name, spec, mats[name])
        obj.location = (idx * grid_spacing, 100.0, 0)   # staging area
        move_to_collection(obj, col)
        verts = len(obj.data.vertices)
        faces = len(obj.data.polygons)
        print(f"[Rocks] {name:8s} — verts: {verts:5d}  faces: {faces:5d}")
        rock_objs.append(obj)

    print(f"[Rocks] {len(rock_objs)} modular rocks ready in collection 'IsleTrial_Rocks'")
    return rock_objs


# ═══════════════════════════════════════════════════════
#  02-D  LIGHTHOUSE
# ═══════════════════════════════════════════════════════

def build_lighthouse_materials():
    return {
        'white' : build_stone_mat('Mat_Lighthouse_White',
                     dark=hex_to_rgb('DCDADA'), light=hex_to_rgb('F5F2F2'),
                     roughness=0.72),
        'stone' : build_stone_mat('Mat_Lighthouse_Stone',
                     dark=hex_to_rgb('5A5048'), light=hex_to_rgb('A09080'),
                     roughness=0.92),
        'metal' : build_metal_mat('Mat_Lighthouse_Metal',
                     hex_to_rgb('2A2F35'), metallic=0.87, roughness=0.38),
        'glass' : build_glass_trans_mat('Mat_Lighthouse_Glass',
                     hex_to_rgb('88CCFF'), alpha=0.15, ior=1.45),
        'light' : build_emissive_mat('Mat_Lighthouse_Light',
                     hex_to_rgb('FFFF88'), emission_str=5.0),
    }


def create_lighthouse_tower(mats):
    bm = bmesh.new()
    SEGS   = 16
    BANDS  = 30
    BASE_R = 2.5
    TOP_R  = 1.8
    HEIGHT = 15.0

    for band in range(BANDS + 1):
        t = band / BANDS
        r = BASE_R + (TOP_R - BASE_R) * t
        z = t * HEIGHT
        for s in range(SEGS):
            a = (s / SEGS) * math.tau
            bm.verts.new(Vector((math.cos(a) * r, math.sin(a) * r, z)))

    bm.verts.ensure_lookup_table()
    for band in range(BANDS):
        for s in range(SEGS):
            s1  = (s + 1) % SEGS
            i00 = band * SEGS + s
            i10 = band * SEGS + s1
            i01 = (band + 1) * SEGS + s
            i11 = (band + 1) * SEGS + s1
            bm.faces.new([bm.verts[i00], bm.verts[i10],
                          bm.verts[i11], bm.verts[i01]])

    # Top cap
    top_center = bm.verts.new(Vector((0, 0, HEIGHT)))
    top_ring_start = BANDS * SEGS
    for s in range(SEGS):
        s1 = (s + 1) % SEGS
        bm.faces.new([bm.verts[top_ring_start + s],
                      bm.verts[top_ring_start + s1],
                      top_center])

    # Bottom cap
    bot_center = bm.verts.new(Vector((0, 0, 0)))
    for s in range(SEGS):
        s1 = (s + 1) % SEGS
        bm.faces.new([bm.verts[s1], bm.verts[s], bot_center])

    bm.normal_update()
    obj = new_mesh_obj('Lighthouse_Tower', bm)

    # Boolean window openings (6 evenly spaced vertically)
    for wi in range(6):
        z_pos = 2.5 + wi * (HEIGHT - 3.0) / 5
        a     = (wi / 6) * math.tau
        rx    = math.cos(a) * (BASE_R + 0.1)
        ry    = math.sin(a) * (BASE_R + 0.1)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(rx, ry, z_pos))
        win = bpy.context.active_object
        win.name = f'_lh_win_cut_{wi}'
        win.scale = (0.4, 0.8, 0.7)
        bool_m = obj.modifiers.new(f'Win_{wi}', 'BOOLEAN')
        bool_m.operation = 'DIFFERENCE'
        bool_m.object    = win
        bpy.ops.object.select_all(action='DESELECT')
        win.select_set(True)
        bpy.context.view_layer.objects.active = win

    activate(obj)
    assign_mat(obj, mats['white'])
    smart_uv(obj)
    return obj


def create_lantern_room(mats):
    objs = []
    PANELS = 8
    R      = 2.0
    H      = 1.5

    # Metal frame ring (top + bottom)
    for z_off in (0.0, H):
        bm = bmesh.new()
        verts_bot, verts_top = [], []
        for p in range(PANELS):
            a = (p / PANELS) * math.tau
            verts_bot.append(bm.verts.new(Vector((math.cos(a)*R,     math.sin(a)*R,     z_off))))
            verts_top.append(bm.verts.new(Vector((math.cos(a)*R*1.02, math.sin(a)*R*1.02, z_off + 0.08))))
        for p in range(PANELS):
            p1 = (p + 1) % PANELS
            bm.faces.new([verts_bot[p], verts_bot[p1], verts_top[p1], verts_top[p]])
        bm.normal_update()
        ring = new_mesh_obj(f'_lh_ring_{z_off}', bm)
        ring.location = (0, 0, 15.0)
        assign_mat(ring, mats['metal'])
        objs.append(ring)

    # Glass panels
    for p in range(PANELS):
        a0 = (p / PANELS) * math.tau
        a1 = ((p + 1) / PANELS) * math.tau
        bm = bmesh.new()
        vs = [
            bm.verts.new(Vector((math.cos(a0)*R*0.98, math.sin(a0)*R*0.98, 0.05))),
            bm.verts.new(Vector((math.cos(a1)*R*0.98, math.sin(a1)*R*0.98, 0.05))),
            bm.verts.new(Vector((math.cos(a1)*R*0.98, math.sin(a1)*R*0.98, H - 0.05))),
            bm.verts.new(Vector((math.cos(a0)*R*0.98, math.sin(a0)*R*0.98, H - 0.05))),
        ]
        bm.faces.new(vs)
        bm.normal_update()
        panel = new_mesh_obj(f'_lh_glass_{p}', bm)
        panel.location = (0, 0, 15.0)
        assign_mat(panel, mats['glass'])
        objs.append(panel)

    # Rotating beacon (emissive cone)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=8, radius1=0.3, radius2=0.05, depth=1.5)
    beacon = new_mesh_obj('_lh_beacon', bm)
    beacon.location = (0, 0, 15.0 + H * 0.5)
    beacon.rotation_euler = (math.radians(90), 0, 0)
    assign_mat(beacon, mats['light'])
    objs.append(beacon)

    activate(objs[0])
    for o in objs[1:]:
        o.select_set(True)
    bpy.ops.object.join()
    room = bpy.context.active_object
    room.name = 'Lighthouse_LanternRoom'
    smart_uv(room)
    return room


def create_lighthouse_base(mats):
    bm = bmesh.new()
    W, H = 6.0, 1.5
    verts = [
        bm.verts.new((-W/2, -W/2, 0)),
        bm.verts.new(( W/2, -W/2, 0)),
        bm.verts.new(( W/2,  W/2, 0)),
        bm.verts.new((-W/2,  W/2, 0)),
        bm.verts.new((-W/2, -W/2, H)),
        bm.verts.new(( W/2, -W/2, H)),
        bm.verts.new(( W/2,  W/2, H)),
        bm.verts.new((-W/2,  W/2, H)),
    ]
    faces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(3,0,4,7)]
    for fi in faces:
        bm.faces.new([verts[k] for k in fi])

    bm.normal_update()
    base = new_mesh_obj('Lighthouse_Base', bm)

    # Door arch boolean
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.55, depth=2.0,
                                         location=(0, -W/2 - 0.01, H * 0.65))
    door_cut = bpy.context.active_object
    door_cut.name = '_lh_door_cut'
    door_cut.rotation_euler = (math.radians(90), 0, 0)
    door_bool = base.modifiers.new('Door', 'BOOLEAN')
    door_bool.operation = 'DIFFERENCE'
    door_bool.object    = door_cut
    bpy.ops.object.select_all(action='DESELECT')
    door_cut.select_set(True)
    bpy.context.view_layer.objects.active = door_cut

    activate(base)
    assign_mat(base, mats['stone'])
    smart_uv(base)
    return base


def create_lighthouse_railing(mats):
    objs = []
    POSTS = 16
    R     = 2.1
    Z_OFF = 16.5

    for p in range(POSTS):
        a = (p / POSTS) * math.tau
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                              segments=6, radius1=0.04, radius2=0.04, depth=0.8)
        post = new_mesh_obj(f'_lh_rail_post_{p}', bm)
        post.location = (math.cos(a) * R, math.sin(a) * R, Z_OFF)
        assign_mat(post, mats['metal'])
        objs.append(post)

    # Horizontal rings
    for z_ring in (Z_OFF + 0.35, Z_OFF + 0.65):
        curve_data = bpy.data.curves.new('_lh_rail_ring', 'CURVE')
        curve_data.dimensions   = '3D'
        curve_data.bevel_depth  = 0.02
        curve_data.use_fill_caps = True
        spline = curve_data.splines.new('NURBS')
        spline.points.add(POSTS)
        for p in range(POSTS + 1):
            a = (p / POSTS) * math.tau
            spline.points[p].co = (math.cos(a)*R, math.sin(a)*R, z_ring, 1.0)
        spline.use_cyclic_u = True
        ring_obj = bpy.data.objects.new('_lh_rail_ring', curve_data)
        bpy.context.scene.collection.objects.link(ring_obj)
        assign_mat(ring_obj, mats['metal'])
        objs.append(ring_obj)

    activate(objs[0])
    for o in objs[1:]:
        o.select_set(True)
    bpy.ops.object.join()
    railing = bpy.context.active_object
    railing.name = 'Lighthouse_Railing_Top'
    smart_uv(railing)
    return railing


def create_lighthouse_steps(mats):
    objs = []
    STEPS  = 12
    INNER_R = 2.6
    STEP_W  = 1.2
    STEP_H  = 0.22
    STEP_D  = 0.55

    for s in range(STEPS):
        t  = s / STEPS
        a  = t * math.tau * 1.5          # 1.5 full turns
        r  = INNER_R + STEP_W / 2
        cx = math.cos(a) * r
        cy = math.sin(a) * r
        z  = s * STEP_H

        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        step = new_mesh_obj(f'_lh_step_{s}', bm)
        step.scale   = (STEP_W, STEP_D, STEP_H)
        step.location = (cx, cy, z + STEP_H / 2)
        step.rotation_euler = (0, 0, a + math.radians(90))
        assign_mat(step, mats['stone'])
        objs.append(step)

    activate(objs[0])
    for o in objs[1:]:
        o.select_set(True)
    bpy.ops.object.join()
    steps = bpy.context.active_object
    steps.name = 'Lighthouse_Steps'
    smart_uv(steps)
    return steps


def build_lighthouse(col):
    mats   = build_lighthouse_materials()
    tower  = create_lighthouse_tower(mats)
    room   = create_lantern_room(mats)
    base   = create_lighthouse_base(mats)
    rail   = create_lighthouse_railing(mats)
    steps  = create_lighthouse_steps(mats)

    all_objs = [tower, room, base, rail, steps]
    root = make_root_empty('Lighthouse_ROOT', location=(200, 0, 0))

    for obj in all_objs:
        obj.location.x += 200   # move to staging area with root
        set_origin_center(obj)
        apply_all(obj)
        move_to_collection(obj, col)
        parent_to(obj, root)

    move_to_collection(root, col)
    print("[Lighthouse] Build complete — Lighthouse_ROOT ready for FBX export.")
    return root


# ═══════════════════════════════════════════════════════
#  VIEWPORT SHADING
# ═══════════════════════════════════════════════════════

def set_material_preview():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
            break


# ═══════════════════════════════════════════════════════
#  MAIN — builds all 4 assets
# ═══════════════════════════════════════════════════════

def main():
    clear_scene()
    random.seed(0)

    col_island = make_collection('IsleTrial_Island')
    col_dock   = make_collection('IsleTrial_Dock')
    col_rocks  = make_collection('IsleTrial_Rocks')
    col_lh     = make_collection('IsleTrial_Lighthouse')

    print("\n" + "="*60)
    print("  IsleTrial — Environment Pack Build")
    print("="*60)

    build_island(col_island)
    build_dock(col_dock)
    build_rocks(col_rocks)
    build_lighthouse(col_lh)

    set_material_preview()

    print("\n" + "="*60)
    print("  All environment assets built successfully.")
    print("  Collections: IsleTrial_Island | IsleTrial_Dock |")
    print("               IsleTrial_Rocks  | IsleTrial_Lighthouse")
    print("  Select each ROOT empty and export as individual FBX files.")
    print("="*60 + "\n")


main()
