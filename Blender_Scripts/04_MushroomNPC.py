"""
IsleTrial — Mushroom NPC Character
Blender 4.x Python Script

Creates the cute Amanita-mushroom adventurer NPC shown in the reference image:
  • Large red/orange mushroom cap with raised white spots
  • Cream stem face with big eyes and a smile
  • Fluffy green moss collar
  • Olive-green jacket with brown leather belt straps
  • Red glowing potion bottle on belt
  • Large brown leather backpack with rolled bedroll
  • Twisted wooden walking staff with brass bell
  • Chunky brown leather boots

Run in Blender → Scripting workspace → Run Script.
All materials use the dual-path system:
  Mix Factor 0 = Procedural (works immediately, no files)
  Mix Factor 1 = Image Texture (load Unity PBR maps and flip)

Unity Export
──────────────────────────────────────────────────────────────
  Collection  : IsleTrial_MushroomNPC
  Root empty  : MushroomNPC_ROOT
  Select ROOT → File → Export → FBX
  Scale Factor in Unity: 1.0
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ═══════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for d in [bpy.data.meshes, bpy.data.materials,
              bpy.data.curves, bpy.data.collections]:
        for item in list(d):
            d.remove(item)


def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def link(obj):
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)


def new_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def smart_uv(obj, angle=66, margin=0.02):
    activate(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')


def apply_all(obj):
    activate(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def set_smooth(obj, shade=True):
    activate(obj)
    bpy.ops.object.shade_smooth() if shade else bpy.ops.object.shade_flat()


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


# ═══════════════════════════════════════════════════════
#  DUAL-PATH MATERIAL BUILDER
#  Mix Factor 0 = procedural  |  Mix Factor 1 = image tex
# ═══════════════════════════════════════════════════════

def _n(nd, t, loc, lbl=None):
    n = nd.new(t); n.location = loc
    if lbl: n.label = lbl
    return n

def _img(nd, slot, loc):
    n = nd.new('ShaderNodeTexImage')
    n.location = loc; n.label = f'[UNITY] {slot}'; n.name = slot
    return n

def _mapping(nd, lk, scale=(1,1,1), loc=(-900,0)):
    tc = _n(nd,'ShaderNodeTexCoord',(-1100,0))
    mp = _n(nd,'ShaderNodeMapping', loc)
    mp.inputs['Scale'].default_value = (scale[0], scale[1], scale[2])
    lk.new(tc.outputs['UV'], mp.inputs['Vector'])
    return mp

def _mix_pi(nd, lk, proc, img_nd, loc, lbl=''):
    m = _n(nd,'ShaderNodeMixRGB', loc, lbl)
    m.blend_type='MIX'; m.inputs['Fac'].default_value=0.0
    lk.new(proc,               m.inputs['Color1'])
    lk.new(img_nd.outputs['Color'], m.inputs['Color2'])
    return m

def _bump(nd, lk, height_socket, strength, dist, loc):
    b = _n(nd,'ShaderNodeBump', loc)
    b.inputs['Strength'].default_value = strength
    b.inputs['Distance'].default_value = dist
    lk.new(height_socket, b.inputs['Height'])
    return b

def _new_mat(name, roughness=0.8, metallic=0.0,
             alpha=1.0, transmission=0.0, emission=None, emission_str=0.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    if alpha < 1.0: mat.blend_method = 'BLEND'
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()
    out  = _n(nd,'ShaderNodeOutputMaterial',(1200,0))
    bsdf = _n(nd,'ShaderNodeBsdfPrincipled', (700,0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value           = roughness
    bsdf.inputs['Metallic'].default_value            = metallic
    bsdf.inputs['Alpha'].default_value               = alpha
    bsdf.inputs['Transmission Weight'].default_value = transmission
    if emission:
        bsdf.inputs['Emission Color'].default_value    = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission_str
    return mat, nd, lk, bsdf


def mat_mushroom_cap():
    """Orange-red cap: Noise variation + white spot highlight."""
    mat, nd, lk, bsdf = _new_mat('Mat_MushroomCap', roughness=0.72)
    mp = _mapping(nd, lk, scale=(2,2,2))

    noise = _n(nd,'ShaderNodeTexNoise',(-480,300))
    noise.inputs['Scale'].default_value   = 5.0
    noise.inputs['Detail'].default_value  = 10.0
    noise.inputs['Roughness'].default_value = 0.5
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])

    cramp = _n(nd,'ShaderNodeValToRGB',(-180,300))
    cramp.color_ramp.elements[0].position = 0.35
    cramp.color_ramp.elements[0].color    = (*hex_rgb('C84010'), 1.0)  # deep red
    cramp.color_ramp.elements[1].position = 0.80
    cramp.color_ramp.elements[1].color    = (*hex_rgb('F06030'), 1.0)  # bright orange
    lk.new(noise.outputs['Color'], cramp.inputs['Fac'])

    img_a = _img(nd,'Mat_MushroomCap_Albedo',(-480,-260))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd,lk, cramp.outputs['Color'], img_a, (280,250),'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    bump = _bump(nd,lk, noise.outputs['Fac'], 0.6, 0.03, (-80,-380))
    img_n = _img(nd,'Mat_MushroomCap_Normal',(-480,-520))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd,'ShaderNodeNormalMap',(-80,-490))
    lk.new(img_n.outputs['Color'], nmap.inputs['Color'])
    mix_n = _n(nd,'ShaderNodeMixRGB',(160,-440),label='Mix Normal')
    mix_n.inputs['Fac'].default_value = 0.0
    lk.new(bump.outputs['Normal'], mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'], mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])
    return mat


def mat_cap_spots():
    """White raised spots on the cap: slightly glossy, smooth."""
    mat, nd, lk, bsdf = _new_mat('Mat_CapSpots', roughness=0.55)
    bsdf.inputs['Base Color'].default_value = (0.98, 0.95, 0.90, 1.0)
    img_a = _img(nd,'Mat_CapSpots_Albedo',(-300,100))
    mp = _mapping(nd,lk,scale=(1,1,1))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd,lk, bsdf.inputs['Base Color'].default_value[:3], img_a, (200,80),'Albedo')
    return mat


def mat_stem():
    """Cream/tan stem: subtle noise for organic surface."""
    mat, nd, lk, bsdf = _new_mat('Mat_MushroomStem', roughness=0.80)
    mp = _mapping(nd,lk,scale=(3,3,3))

    noise = _n(nd,'ShaderNodeTexNoise',(-480,280))
    noise.inputs['Scale'].default_value = 8.0; noise.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['Vector'], noise.inputs['Vector'])

    cramp = _n(nd,'ShaderNodeValToRGB',(-180,280))
    cramp.color_ramp.elements[0].color = (*hex_rgb('C8A878'), 1.0)
    cramp.color_ramp.elements[1].color = (*hex_rgb('E8D0A8'), 1.0)
    lk.new(noise.outputs['Color'], cramp.inputs['Fac'])

    img_a = _img(nd,'Mat_MushroomStem_Albedo',(-480,-200))
    lk.new(mp.outputs['Vector'], img_a.inputs['Vector'])
    mix_a = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,240),'Albedo')
    lk.new(mix_a.outputs['Color'], bsdf.inputs['Base Color'])

    bump = _bump(nd,lk,noise.outputs['Fac'],0.3,0.02,(-80,-350))
    img_n = _img(nd,'Mat_MushroomStem_Normal',(-480,-480))
    lk.new(mp.outputs['Vector'], img_n.inputs['Vector'])
    nmap = _n(nd,'ShaderNodeNormalMap',(-80,-450)); lk.new(img_n.outputs['Color'],nmap.inputs['Color'])
    mix_n = _n(nd,'ShaderNodeMixRGB',(160,-400),label='Mix Normal')
    mix_n.inputs['Fac'].default_value=0.0
    lk.new(bump.outputs['Normal'],mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'],mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'],bsdf.inputs['Normal'])
    return mat


def mat_eye():
    mat, nd, lk, bsdf = _new_mat('Mat_Eye', roughness=0.05, metallic=0.0)
    bsdf.inputs['Base Color'].default_value = (*hex_rgb('1A0E08'), 1.0)
    return mat


def mat_eye_shine():
    mat, nd, lk, bsdf = _new_mat('Mat_EyeShine', roughness=0.0,
                                   emission=hex_rgb('FFFFFF'), emission_str=1.0)
    bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)
    return mat


def mat_moss():
    """Fluffy green moss collar."""
    mat, nd, lk, bsdf = _new_mat('Mat_MossCollar', roughness=0.95)
    mp = _mapping(nd,lk,scale=(6,6,6))

    noise = _n(nd,'ShaderNodeTexNoise',(-480,280))
    noise.inputs['Scale'].default_value = 12.0; noise.inputs['Detail'].default_value = 12.0
    noise.inputs['Roughness'].default_value = 0.7
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])

    cramp = _n(nd,'ShaderNodeValToRGB',(-180,280))
    cramp.color_ramp.elements[0].color = (*hex_rgb('2A4A18'), 1.0)
    cramp.color_ramp.elements[1].color = (*hex_rgb('5A8028'), 1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])

    img_a = _img(nd,'Mat_MossCollar_Albedo',(-480,-200))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mix_a = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,240),'Albedo')
    lk.new(mix_a.outputs['Color'],bsdf.inputs['Base Color'])

    bump = _bump(nd,lk,noise.outputs['Fac'],1.2,0.05,(-80,-360))
    lk.new(bump.outputs['Normal'],bsdf.inputs['Normal'])

    bsdf.inputs['Subsurface Weight'].default_value = 0.06
    return mat


def mat_jacket():
    """Olive-green worn fabric jacket."""
    mat, nd, lk, bsdf = _new_mat('Mat_Jacket', roughness=0.92)
    mp = _mapping(nd,lk,scale=(4,4,4))

    wave = _n(nd,'ShaderNodeTexWave',(-480,280))
    wave.wave_type='BANDS'; wave.bands_direction='X'
    wave.inputs['Scale'].default_value=30.0; wave.inputs['Distortion'].default_value=1.5
    wave.inputs['Detail'].default_value=6.0
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])

    noise = _n(nd,'ShaderNodeTexNoise',(-480,50))
    noise.inputs['Scale'].default_value=8.0; noise.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])

    cramp = _n(nd,'ShaderNodeValToRGB',(-180,280))
    cramp.color_ramp.elements[0].color = (*hex_rgb('3A4820'), 1.0)
    cramp.color_ramp.elements[1].color = (*hex_rgb('5A6A38'), 1.0)
    lk.new(wave.outputs['Color'],cramp.inputs['Fac'])

    ov = _n(nd,'ShaderNodeMixRGB',(40,200))
    ov.blend_type='OVERLAY'; ov.inputs['Fac'].default_value=0.20
    lk.new(cramp.outputs['Color'],ov.inputs['Color1'])
    lk.new(noise.outputs['Color'],ov.inputs['Color2'])

    img_a = _img(nd,'Mat_Jacket_Albedo',(-480,-250))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mix_a = _mix_pi(nd,lk,ov.outputs['Color'],img_a,(280,220),'Albedo')
    lk.new(mix_a.outputs['Color'],bsdf.inputs['Base Color'])

    bump = _bump(nd,lk,wave.outputs['Color'],0.5,0.03,(-80,-400))
    img_n = _img(nd,'Mat_Jacket_Normal',(-480,-550))
    lk.new(mp.outputs['Vector'],img_n.inputs['Vector'])
    nmap = _n(nd,'ShaderNodeNormalMap',(-80,-520)); lk.new(img_n.outputs['Color'],nmap.inputs['Color'])
    mix_n = _n(nd,'ShaderNodeMixRGB',(160,-460),label='Mix Normal')
    mix_n.inputs['Fac'].default_value=0.0
    lk.new(bump.outputs['Normal'],mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'],mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'],bsdf.inputs['Normal'])
    return mat


def mat_leather(name, hex_col, roughness=0.75):
    """Brown leather — used for belt, straps, backpack, boots."""
    mat, nd, lk, bsdf = _new_mat(name, roughness=roughness)
    mp = _mapping(nd,lk,scale=(5,5,5))

    noise = _n(nd,'ShaderNodeTexNoise',(-480,280))
    noise.inputs['Scale'].default_value=40.0; noise.inputs['Detail'].default_value=10.0
    noise.inputs['Roughness'].default_value=0.65
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])

    cramp = _n(nd,'ShaderNodeValToRGB',(-180,280))
    base = hex_rgb(hex_col)
    cramp.color_ramp.elements[0].color = (*tuple(max(c-0.12,0) for c in base), 1.0)
    cramp.color_ramp.elements[1].color = (*base, 1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])

    img_a = _img(nd,f'{name}_Albedo',(-480,-220))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mix_a = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,240),'Albedo')
    lk.new(mix_a.outputs['Color'],bsdf.inputs['Base Color'])

    bump = _bump(nd,lk,noise.outputs['Fac'],0.6,0.03,(-80,-370))
    img_n = _img(nd,f'{name}_Normal',(-480,-510))
    lk.new(mp.outputs['Vector'],img_n.inputs['Vector'])
    nmap = _n(nd,'ShaderNodeNormalMap',(-80,-480)); lk.new(img_n.outputs['Color'],nmap.inputs['Color'])
    mix_n = _n(nd,'ShaderNodeMixRGB',(160,-420),label='Mix Normal')
    mix_n.inputs['Fac'].default_value=0.0
    lk.new(bump.outputs['Normal'],mix_n.inputs['Color1'])
    lk.new(nmap.outputs['Normal'],mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'],bsdf.inputs['Normal'])

    mrng = _n(nd,'ShaderNodeMapRange',(-180,-750))
    mrng.inputs['To Min'].default_value = roughness-0.10
    mrng.inputs['To Max'].default_value = roughness+0.10
    lk.new(noise.outputs['Fac'],mrng.inputs['Value'])
    lk.new(mrng.outputs['Result'],bsdf.inputs['Roughness'])
    return mat


def mat_potion_glass():
    """Red glowing potion bottle."""
    mat, nd, lk, bsdf = _new_mat('Mat_PotionGlass', roughness=0.04,
                                   alpha=0.55, transmission=0.9,
                                   emission=hex_rgb('FF2020'), emission_str=1.8)
    bsdf.inputs['Base Color'].default_value = (*hex_rgb('FF3030'), 1.0)
    bsdf.inputs['IOR'].default_value = 1.52
    mp = _mapping(nd,lk,scale=(1,1,1))
    noise = _n(nd,'ShaderNodeTexNoise',(-480,100))
    noise.inputs['Scale'].default_value=2.0; noise.inputs['Detail'].default_value=2.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mrng = _n(nd,'ShaderNodeMapRange',(-180,100))
    mrng.inputs['To Min'].default_value=1.5; mrng.inputs['To Max'].default_value=2.2
    lk.new(noise.outputs['Fac'],mrng.inputs['Value'])
    lk.new(mrng.outputs['Result'],bsdf.inputs['Emission Strength'])
    return mat


def mat_wood_staff():
    """Twisted dark brown wood for the staff."""
    mat, nd, lk, bsdf = _new_mat('Mat_Staff', roughness=0.88)
    mp = _mapping(nd,lk,scale=(12,1,1))
    wave = _n(nd,'ShaderNodeTexWave',(-480,280))
    wave.wave_type='BANDS'; wave.bands_direction='DIAGONAL'
    wave.inputs['Scale'].default_value=25.0; wave.inputs['Distortion'].default_value=4.0
    wave.inputs['Detail'].default_value=10.0
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,280))
    cramp.color_ramp.elements[0].color=(*hex_rgb('281408'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('5C3820'),1.0)
    lk.new(wave.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,'Mat_Staff_Albedo',(-480,-220))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mix_a = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,240),'Albedo')
    lk.new(mix_a.outputs['Color'],bsdf.inputs['Base Color'])
    bump = _bump(nd,lk,wave.outputs['Color'],0.9,0.04,(-80,-370))
    lk.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    return mat


def mat_brass():
    """Brass metal for bell + buckles."""
    mat, nd, lk, bsdf = _new_mat('Mat_Brass', roughness=0.35, metallic=0.95)
    mp = _mapping(nd,lk,scale=(4,4,4))
    noise = _n(nd,'ShaderNodeTexNoise',(-480,200))
    noise.inputs['Scale'].default_value=80.0; noise.inputs['Detail'].default_value=6.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,200))
    cramp.color_ramp.elements[0].color=(*hex_rgb('8A6820'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('C8A840'),1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,'Mat_Brass_Albedo',(-480,-200))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mix_a = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,180),'Albedo')
    lk.new(mix_a.outputs['Color'],bsdf.inputs['Base Color'])
    scratch = _n(nd,'ShaderNodeTexNoise',(-480,-420))
    scratch.inputs['Scale'].default_value=200.0; scratch.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],scratch.inputs['Vector'])
    mrng = _n(nd,'ShaderNodeMapRange',(-180,-420))
    mrng.inputs['To Min'].default_value=0.28; mrng.inputs['To Max'].default_value=0.65
    lk.new(scratch.outputs['Fac'],mrng.inputs['Value'])
    lk.new(mrng.outputs['Result'],bsdf.inputs['Roughness'])
    return mat


def mat_bedroll():
    """Rolled fabric on top of backpack."""
    mat, nd, lk, bsdf = _new_mat('Mat_Bedroll', roughness=0.95)
    mp = _mapping(nd,lk,scale=(3,3,3))
    wave = _n(nd,'ShaderNodeTexWave',(-480,200))
    wave.wave_type='BANDS'; wave.bands_direction='X'
    wave.inputs['Scale'].default_value=20.0; wave.inputs['Distortion'].default_value=0.5
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,200))
    cramp.color_ramp.elements[0].color=(*hex_rgb('C8B080'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('E8D0A0'),1.0)
    lk.new(wave.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,'Mat_Bedroll_Albedo',(-480,-200))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mix_a = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,180),'Albedo')
    lk.new(mix_a.outputs['Color'],bsdf.inputs['Base Color'])
    return mat


# ═══════════════════════════════════════════════════════
#  GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

# ── Mushroom Cap ────────────────────────────────────────
def build_mushroom_cap(mats):
    bm = bmesh.new()
    SEGS = 32
    RINGS = 16
    CAP_R = 0.72   # radius at widest
    CAP_H = 0.42   # height of dome

    # Build dome profile: flattened hemisphere with rolled lip
    verts = []
    center_top = bm.verts.new(Vector((0, 0, CAP_H)))
    verts.append([center_top])

    for r in range(1, RINGS + 1):
        t = r / RINGS
        # Theta from 0 (top) to 120 degrees (gives a rolled mushroom shape)
        theta = t * math.radians(120)
        rr = math.sin(theta) * CAP_R
        zz = math.cos(theta) * CAP_H
        # Add slight lip flare at bottom
        if t > 0.75:
            flare = (t - 0.75) / 0.25
            rr += flare * 0.18
            zz -= flare * 0.06
        ring = []
        for s in range(SEGS):
            a = (s / SEGS) * math.tau
            ring.append(bm.verts.new(Vector((math.cos(a)*rr, math.sin(a)*rr, zz))))
        verts.append(ring)

    # Top cap faces (fan from center_top)
    for s in range(SEGS):
        s1 = (s + 1) % SEGS
        bm.faces.new([center_top, verts[1][s1], verts[1][s]])

    # Ring quads
    for r in range(1, RINGS):
        for s in range(SEGS):
            s1 = (s + 1) % SEGS
            bm.faces.new([verts[r][s], verts[r][s1],
                          verts[r+1][s1], verts[r+1][s]])

    # Bottom cap ring (flat underside rim)
    bottom_center = bm.verts.new(Vector((0, 0, verts[-1][0].co.z)))
    for s in range(SEGS):
        s1 = (s + 1) % SEGS
        bm.faces.new([verts[-1][s1], verts[-1][s], bottom_center])

    bm.normal_update()
    cap = new_obj('MushroomCap', bm)
    cap.location = (0, 0, 1.05)

    sub = cap.modifiers.new('Subsurf','SUBSURF')
    sub.levels = 2
    assign(cap, mats['cap'])
    smart_uv(cap)
    return cap


# ── White Spots on Cap ──────────────────────────────────
def build_cap_spots(mats):
    """Raised hemispheres scattered across the cap surface."""
    rng = random.Random(42)
    spot_objs = []

    # Spot positions: (phi_deg from top, theta_deg rotation, scale)
    spot_defs = [
        (20, 0,   0.095), (22, 130, 0.080), (23, 255, 0.085),
        (45, 45,  0.075), (46, 170, 0.080), (44, 295, 0.070),
        (62, 10,  0.065), (64, 100, 0.060), (63, 200, 0.068), (60, 310, 0.062),
        (78, 55,  0.050), (79, 145, 0.052), (77, 240, 0.048),
    ]
    CAP_R = 0.72; CAP_H = 0.42

    for phi_d, theta_d, sc in spot_defs:
        phi   = math.radians(phi_d * 1.0)
        theta = math.radians(theta_d)
        rr    = math.sin(phi) * CAP_R
        zz    = math.cos(phi) * CAP_H

        # Lip flare correction
        t = phi_d / 120.0
        if t > 0.75:
            fl = (t - 0.75) / 0.25; rr += fl*0.18; zz -= fl*0.06

        cx = math.cos(theta) * rr
        cy = math.sin(theta) * rr
        cz = zz + 1.05   # cap is offset by 1.05 in Z

        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=sc)
        # Keep only upper hemisphere
        for v in list(bm.verts):
            if v.co.z < -0.02:
                bm.verts.remove(v)
        bm.normal_update()
        spot = new_obj(f'_capspot', bm)
        spot.location = (cx, cy, cz)

        # Orient normal to cap surface
        nx = math.cos(theta)*math.sin(phi)
        ny = math.sin(theta)*math.sin(phi)
        nz = math.cos(phi)
        spot.rotation_euler = Vector((nx, ny, nz)).to_track_quat('Z','Y').to_euler()

        assign(spot, mats['spots'])
        spot_objs.append(spot)

    # Join all spots into one object
    activate(spot_objs[0])
    for s in spot_objs[1:]:
        s.select_set(True)
    bpy.ops.object.join()
    merged = bpy.context.active_object
    merged.name = 'MushroomCap_Spots'
    smart_uv(merged)
    return merged


# ── Stem / Face ─────────────────────────────────────────
def build_stem(mats):
    bm = bmesh.new()
    # Tapered cylinder: wider at top (cap junction), narrower at collar
    SEGS = 20
    sections = [
        # (z, r)
        (1.05, 0.32),  # top, meets cap underside
        (0.92, 0.28),
        (0.78, 0.24),
        (0.65, 0.22),  # face level (collar here)
    ]
    rings = []
    for (z, r) in sections:
        ring = []
        for s in range(SEGS):
            a = (s / SEGS) * math.tau
            ring.append(bm.verts.new(Vector((math.cos(a)*r, math.sin(a)*r, z))))
        rings.append(ring)

    for ri in range(len(rings)-1):
        for s in range(SEGS):
            s1 = (s+1) % SEGS
            bm.faces.new([rings[ri][s], rings[ri][s1],
                          rings[ri+1][s1], rings[ri+1][s]])

    # Top cap (hidden under mushroom cap)
    top_c = bm.verts.new(Vector((0,0,1.06)))
    for s in range(SEGS):
        bm.faces.new([rings[0][s], rings[0][(s+1)%SEGS], top_c])

    bm.normal_update()
    stem = new_obj('MushroomStem', bm)
    sub = stem.modifiers.new('Subsurf','SUBSURF'); sub.levels=2
    assign(stem, mats['stem'])
    smart_uv(stem)
    return stem


# ── Eyes ────────────────────────────────────────────────
def build_eyes(mats):
    eyes = []
    for side, ax in [('L', -0.085), ('R', 0.085)]:
        # Main eye sphere
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=0.058)
        eye = new_obj(f'Eye_{side}', bm)
        eye.location = (ax, 0.215, 0.840)
        assign(eye, mats['eye'])
        smart_uv(eye)

        # Shine dot
        bm2 = bmesh.new()
        bmesh.ops.create_uvsphere(bm2, u_segments=8, v_segments=6, radius=0.016)
        shine = new_obj(f'EyeShine_{side}', bm2)
        shine.location = (ax + 0.018*(-1 if side=='L' else 1), 0.236, 0.858)
        assign(shine, mats['eye_shine'])
        eyes.extend([eye, shine])
    return eyes


# ── Smile ────────────────────────────────────────────────
def build_smile(mats):
    curve = bpy.data.curves.new('Smile_Curve','CURVE')
    curve.dimensions  = '3D'
    curve.bevel_depth = 0.008
    curve.bevel_resolution = 3
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(2)
    pts = spline.bezier_points
    # Left end, center dip, right end
    pts[0].co = Vector((-0.06, 0.218, 0.784))
    pts[1].co = Vector(( 0.00, 0.222, 0.776))
    pts[2].co = Vector(( 0.06, 0.218, 0.784))
    for p in pts:
        p.handle_left_type  = 'AUTO'
        p.handle_right_type = 'AUTO'
    smile_obj = bpy.data.objects.new('Smile', curve)
    bpy.context.scene.collection.objects.link(smile_obj)
    assign(smile_obj, mats['eye'])
    return smile_obj


# ── Moss Collar ──────────────────────────────────────────
def build_collar(mats):
    bm = bmesh.new()
    SEGS  = 32
    INNER = 0.22
    OUTER = 0.36
    Z_BOT = 0.62
    Z_TOP = 0.72
    FLUFF_ROWS = 4

    for row in range(FLUFF_ROWS):
        zt = Z_BOT + (row / (FLUFF_ROWS-1)) * (Z_TOP - Z_BOT)
        r_in  = INNER + row * 0.015
        r_out = OUTER - row * 0.012
        for s in range(SEGS):
            a0 = (s     / SEGS) * math.tau
            a1 = ((s+1) / SEGS) * math.tau
            # Each segment: small rounded lobe
            for ai, ri in [(a0,r_in),(a0,r_out),(a1,r_out),(a1,r_in)]:
                bm.verts.new(Vector((math.cos(ai)*ri, math.sin(ai)*ri, zt)))

    bm.verts.ensure_lookup_table()
    n = len(bm.verts)
    for i in range(0, n-4, 4):
        try:
            bm.faces.new([bm.verts[i], bm.verts[i+1],
                          bm.verts[i+2], bm.verts[i+3]])
        except: pass

    bm.normal_update()
    collar = new_obj('MossCollar', bm)
    sub = collar.modifiers.new('Subsurf','SUBSURF'); sub.levels=1
    assign(collar, mats['moss'])
    smart_uv(collar)
    return collar


# ── Body / Jacket ────────────────────────────────────────
def build_body(mats):
    bm = bmesh.new()
    # Rounded trapezoidal torso
    sections = [
        # (z, w, d)   w=half-width X, d=half-depth Y
        (0.62, 0.22, 0.17),   # shoulder level (just below collar)
        (0.50, 0.24, 0.18),
        (0.38, 0.23, 0.17),
        (0.22, 0.22, 0.16),   # waist
        (0.08, 0.21, 0.15),   # hip
    ]
    SEGS = 20
    rings = []
    for (z, w, d) in sections:
        ring = []
        for s in range(SEGS):
            a = (s / SEGS) * math.tau
            rx = math.cos(a) * w
            ry = math.sin(a) * d
            ring.append(bm.verts.new(Vector((rx, ry, z))))
        rings.append(ring)

    for ri in range(len(rings)-1):
        for s in range(SEGS):
            s1 = (s+1) % SEGS
            bm.faces.new([rings[ri][s], rings[ri][s1],
                          rings[ri+1][s1], rings[ri+1][s]])

    top_c = bm.verts.new(Vector((0,0,0.63)))
    for s in range(SEGS):
        bm.faces.new([rings[0][s], rings[0][(s+1)%SEGS], top_c])

    bot_c = bm.verts.new(Vector((0,0,0.07)))
    for s in range(SEGS):
        bm.faces.new([rings[-1][(s+1)%SEGS], rings[-1][s], bot_c])

    bm.normal_update()
    body = new_obj('Jacket_Body', bm)
    sub = body.modifiers.new('Subsurf','SUBSURF'); sub.levels=2
    assign(body, mats['jacket'])
    smart_uv(body)
    return body


# ── Arms ─────────────────────────────────────────────────
def build_arms(mats):
    arms = []
    for side, sx in [('L', -1), ('R', 1)]:
        bm = bmesh.new()
        SEGS = 14
        # Upper arm + forearm sections
        arm_sections = [
            (sx*0.22, 0, 0.55, 0.075),
            (sx*0.28, 0, 0.48, 0.070),
            (sx*0.32, 0.015, 0.38, 0.065),
            (sx*0.30, 0.020, 0.28, 0.062),
            (sx*0.26, 0.025, 0.18, 0.058),
        ]
        rings = []
        for (ax, ay, az, ar) in arm_sections:
            ring = []
            for s in range(SEGS):
                a = (s / SEGS) * math.tau
                ring.append(bm.verts.new(
                    Vector((ax + math.cos(a)*ar, ay + math.sin(a)*ar*0.7, az))))
            rings.append(ring)
        for ri in range(len(rings)-1):
            for s in range(SEGS):
                s1 = (s+1) % SEGS
                bm.faces.new([rings[ri][s], rings[ri][s1],
                              rings[ri+1][s1], rings[ri+1][s]])
        bm.normal_update()
        arm = new_obj(f'Arm_{side}', bm)
        sub = arm.modifiers.new('Subsurf','SUBSURF'); sub.levels=1
        assign(arm, mats['jacket'])
        smart_uv(arm)
        arms.append(arm)
    return arms


# ── Hands ────────────────────────────────────────────────
def build_hands(mats):
    hands = []
    for side, sx in [('L',-1),('R',1)]:
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.060)
        for v in bm.verts:
            v.co.x *= 0.85; v.co.y *= 0.65; v.co.z *= 0.80
        bm.normal_update()
        hand = new_obj(f'Hand_{side}', bm)
        hand.location = (sx*0.26, 0.03, 0.12)
        assign(hand, mats['stem'])   # same tan skin colour
        smart_uv(hand)
        hands.append(hand)
    return hands


# ── Belt ─────────────────────────────────────────────────
def build_belt(mats):
    bm = bmesh.new()
    SEGS = 32
    Z = 0.22; THICK = 0.025

    for s in range(SEGS):
        a0 = (s     / SEGS) * math.tau
        a1 = ((s+1) / SEGS) * math.tau
        ri, ro = 0.215, 0.245
        verts = [
            bm.verts.new(Vector((math.cos(a0)*ri, math.sin(a0)*ri, Z))),
            bm.verts.new(Vector((math.cos(a0)*ro, math.sin(a0)*ro, Z))),
            bm.verts.new(Vector((math.cos(a1)*ro, math.sin(a1)*ro, Z))),
            bm.verts.new(Vector((math.cos(a1)*ri, math.sin(a1)*ri, Z))),
            bm.verts.new(Vector((math.cos(a0)*ri, math.sin(a0)*ri, Z+THICK))),
            bm.verts.new(Vector((math.cos(a0)*ro, math.sin(a0)*ro, Z+THICK))),
            bm.verts.new(Vector((math.cos(a1)*ro, math.sin(a1)*ro, Z+THICK))),
            bm.verts.new(Vector((math.cos(a1)*ri, math.sin(a1)*ri, Z+THICK))),
        ]
        for fi in [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]:
            bm.faces.new([verts[k] for k in fi])

    bm.normal_update()
    belt = new_obj('Belt', bm)
    assign(belt, mats['belt'])
    smart_uv(belt)
    return belt


# ── Belt Buckle ──────────────────────────────────────────
def build_buckle(mats):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co.x *= 0.06; v.co.y *= 0.02; v.co.z *= 0.04
    bm.normal_update()
    buckle = new_obj('Belt_Buckle', bm)
    buckle.location = (0, 0.24, 0.232)
    assign(buckle, mats['brass'])
    smart_uv(buckle)
    return buckle


# ── Potion Bottle ────────────────────────────────────────
def build_potion(mats):
    bm = bmesh.new()
    # Bottle body
    bottle_sections = [
        (0, 0.030),  # base
        (0.02, 0.032),
        (0.06, 0.035),
        (0.09, 0.034),
        (0.11, 0.025),  # neck
        (0.13, 0.018),
        (0.14, 0.018),
    ]
    SEGS = 14
    rings = []
    for (z, r) in bottle_sections:
        ring = []
        for s in range(SEGS):
            a = (s/SEGS)*math.tau
            ring.append(bm.verts.new(Vector((math.cos(a)*r, math.sin(a)*r, z))))
        rings.append(ring)

    for ri in range(len(rings)-1):
        for s in range(SEGS):
            s1=(s+1)%SEGS
            bm.faces.new([rings[ri][s],rings[ri][s1],rings[ri+1][s1],rings[ri+1][s]])

    bot_c = bm.verts.new(Vector((0,0,0)))
    for s in range(SEGS): bm.faces.new([rings[0][(s+1)%SEGS],rings[0][s],bot_c])
    top_c = bm.verts.new(Vector((0,0,0.145)))
    for s in range(SEGS): bm.faces.new([rings[-1][s],rings[-1][(s+1)%SEGS],top_c])

    bm.normal_update()
    potion = new_obj('Potion_Bottle', bm)
    potion.location = (0.22, 0.05, 0.23)
    potion.rotation_euler = (0, math.radians(12), 0)
    sub = potion.modifiers.new('Subsurf','SUBSURF'); sub.levels=1
    assign(potion, mats['potion'])
    smart_uv(potion)
    return potion


# ── Backpack ─────────────────────────────────────────────
def build_backpack(mats):
    bm = bmesh.new()
    # Main bag body
    W, D, H = 0.24, 0.14, 0.32
    verts = []
    for z in (0.15, 0.15+H):
        for x in (-W/2, W/2):
            for y in (-0.18-D, -0.18):
                verts.append(bm.verts.new(Vector((x, y, z))))

    faces = [(0,1,3,2),(4,5,7,6),(0,1,5,4),(2,3,7,6),(1,3,7,5),(0,2,6,4)]
    for fi in faces:
        bm.faces.new([verts[k] for k in fi])

    bm.normal_update()
    pack = new_obj('Backpack', bm)
    sub = pack.modifiers.new('Subsurf','SUBSURF'); sub.levels=1
    assign(pack, mats['backpack'])
    smart_uv(pack)

    # Straps
    for sx, sy_off in [(-0.08, 0), (0.08, 0)]:
        bm2 = bmesh.new()
        bmesh.ops.create_cube(bm2, size=1)
        for v in bm2.verts:
            v.co.x *= 0.03; v.co.y *= 0.32; v.co.z *= 0.02
        bm2.normal_update()
        strap = new_obj('_strap', bm2)
        strap.location = (sx, -0.10, 0.37)
        strap.rotation_euler = (math.radians(35), 0, 0)
        assign(strap, mats['belt'])
        pack_objs = [pack, strap]

    return pack


# ── Bedroll ──────────────────────────────────────────────
def build_bedroll(mats):
    bm = bmesh.new()
    SEGS = 20
    R = 0.055; L = 0.26
    for s in range(SEGS):
        a0 = (s/SEGS)*math.tau; a1 = ((s+1)/SEGS)*math.tau
        for y in (0, L):
            vl = [
                bm.verts.new(Vector((math.cos(a0)*R, y, math.sin(a0)*R))),
                bm.verts.new(Vector((math.cos(a1)*R, y, math.sin(a1)*R))),
            ]
        # side face
        y0_a0 = bm.verts[-4]; y0_a1 = bm.verts[-3]
        y1_a0 = bm.verts[-2]; y1_a1 = bm.verts[-1]

    bm.normal_update()
    # Actually build it properly with ops
    bm.free()
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=20, radius1=0.055, radius2=0.055, depth=0.26)
    bm.normal_update()
    roll = new_obj('Bedroll', bm)
    roll.location  = (0, -0.18, 0.50)
    roll.rotation_euler = (math.radians(90), 0, 0)
    sub = roll.modifiers.new('Subsurf','SUBSURF'); sub.levels=1
    assign(roll, mats['bedroll'])
    smart_uv(roll)
    return roll


# ── Legs + Boots ─────────────────────────────────────────
def build_legs_boots(mats):
    objs = []
    for side, sx in [('L',-1),('R',1)]:
        # Upper leg (short, hidden under jacket)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                              segments=14, radius1=0.085, radius2=0.075, depth=0.14)
        leg = new_obj(f'Leg_{side}', bm)
        leg.location = (sx*0.095, 0, 0.04)
        assign(leg, mats['jacket'])
        smart_uv(leg); objs.append(leg)

        # Boot — chunky rounded block
        bm2 = bmesh.new()
        verts = [
            bm2.verts.new(Vector((-0.07, -0.06, 0.00))),
            bm2.verts.new(Vector(( 0.07, -0.06, 0.00))),
            bm2.verts.new(Vector(( 0.08,  0.12, 0.00))),
            bm2.verts.new(Vector((-0.08,  0.12, 0.00))),
            bm2.verts.new(Vector((-0.06, -0.05, 0.22))),
            bm2.verts.new(Vector(( 0.06, -0.05, 0.22))),
            bm2.verts.new(Vector(( 0.07,  0.10, 0.22))),
            bm2.verts.new(Vector((-0.07,  0.10, 0.22))),
        ]
        for fi in [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]:
            bm2.faces.new([verts[k] for k in fi])
        bm2.normal_update()
        boot = new_obj(f'Boot_{side}', bm2)
        boot.location = (sx*0.095, 0.015, -0.22)
        sub2 = boot.modifiers.new('Subsurf','SUBSURF'); sub2.levels=2
        assign(boot, mats['boot'])
        smart_uv(boot); objs.append(boot)
    return objs


# ── Staff ────────────────────────────────────────────────
def build_staff(mats):
    bm = bmesh.new()
    # Twisted staff: 3 twisting segments
    SEGS   = 12
    HEIGHT = 1.10
    STEPS  = 30
    twist_per_step = math.tau * 1.5 / STEPS

    rings = []
    for st in range(STEPS+1):
        t   = st / STEPS
        z   = t * HEIGHT - 0.05
        tw  = st * twist_per_step
        # Slight S-curve in X
        x_off = math.sin(t * math.pi) * 0.04
        ring  = []
        r     = 0.022 - t*0.005  # tapers slightly
        for s in range(SEGS):
            a = (s/SEGS)*math.tau + tw
            ring.append(bm.verts.new(Vector((
                math.cos(a)*r + x_off,
                math.sin(a)*r,
                z))))
        rings.append(ring)

    for ri in range(STEPS):
        for s in range(SEGS):
            s1=(s+1)%SEGS
            bm.faces.new([rings[ri][s],rings[ri][s1],
                          rings[ri+1][s1],rings[ri+1][s]])

    # End caps
    bc = bm.verts.new(Vector((0,0,-0.05)))
    for s in range(SEGS): bm.faces.new([rings[0][(s+1)%SEGS],rings[0][s],bc])
    tc = bm.verts.new(Vector((0,0,HEIGHT-0.05)))
    for s in range(SEGS): bm.faces.new([rings[-1][s],rings[-1][(s+1)%SEGS],tc])

    bm.normal_update()
    staff = new_obj('Staff', bm)
    staff.location = (-0.30, 0.05, 0)
    staff.rotation_euler = (0, math.radians(-6), 0)
    assign(staff, mats['staff'])
    smart_uv(staff)
    return staff


# ── Bell ─────────────────────────────────────────────────
def build_bell(mats):
    bm = bmesh.new()
    SEGS = 16
    # Bell profile: hemispherical top + flared bottom
    bell_pts = [
        (0.00, 0.00), (0.04, 0.01), (0.06, 0.04),
        (0.055,0.07), (0.04, 0.09), (0.02, 0.095),
    ]
    prev = None
    for (r, z) in bell_pts:
        ring = [bm.verts.new(Vector((
            math.cos((s/SEGS)*math.tau)*r,
            math.sin((s/SEGS)*math.tau)*r, z)))
            for s in range(SEGS)]
        if prev:
            for s in range(SEGS):
                s1=(s+1)%SEGS
                bm.faces.new([prev[s],prev[s1],ring[s1],ring[s]])
        else:
            top_c = bm.verts.new(Vector((0,0,-0.01)))
            for s in range(SEGS): bm.faces.new([ring[(s+1)%SEGS],ring[s],top_c])
        prev = ring

    bm.normal_update()
    bell = new_obj('Bell', bm)
    bell.location = (-0.30, 0.05, 1.08)
    sub = bell.modifiers.new('Subsurf','SUBSURF'); sub.levels=1
    assign(bell, mats['brass'])
    smart_uv(bell)

    # Clapper (small sphere inside bell)
    bm2 = bmesh.new()
    bmesh.ops.create_uvsphere(bm2, u_segments=8, v_segments=6, radius=0.010)
    bm2.normal_update()
    clapper = new_obj('Bell_Clapper', bm2)
    clapper.location = (-0.30, 0.05, 1.042)
    assign(clapper, mats['brass'])

    return [bell, clapper]


# ═══════════════════════════════════════════════════════
#  SCENE ORGANISATION
# ═══════════════════════════════════════════════════════

def organise(all_objs):
    col = bpy.data.collections.new('IsleTrial_MushroomNPC')
    bpy.context.scene.collection.children.link(col)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = 'MushroomNPC_ROOT'

    for obj in all_objs:
        for c in list(obj.users_collection): c.objects.unlink(obj)
        col.objects.link(obj)
        if obj.parent is None and obj != root:
            obj.parent = root

    for c in list(root.users_collection): c.objects.unlink(root)
    col.objects.link(root)

    for obj in all_objs:
        if obj.type in ('MESH','CURVE'):
            activate(obj)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            apply_all(obj)
    return root


def print_report(all_objs, root):
    print("\n" + "="*60)
    print("  IsleTrial — Mushroom NPC Build Report")
    print("="*60)
    for obj in all_objs:
        p = obj.location
        verts = len(obj.data.vertices) if hasattr(obj.data,'vertices') else '-'
        print(f"  {obj.name:<28} verts={str(verts):<6}  "
              f"pos=({p.x:+.2f},{p.y:+.2f},{p.z:+.2f})")
    print(f"\n  Total objects: {len(all_objs)}")
    print("  Collection: IsleTrial_MushroomNPC")
    print("  Select MushroomNPC_ROOT → Export FBX")
    print("  Unity Scale Factor: 1.0")
    print("="*60 + "\n")


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

def main():
    clear_scene()
    random.seed(0)

    print("[MushroomNPC] Building materials...")
    mats = {
        'cap'      : mat_mushroom_cap(),
        'spots'    : mat_cap_spots(),
        'stem'     : mat_stem(),
        'eye'      : mat_eye(),
        'eye_shine': mat_eye_shine(),
        'moss'     : mat_moss(),
        'jacket'   : mat_jacket(),
        'belt'     : mat_leather('Mat_Belt',     '5A3A18', roughness=0.70),
        'backpack' : mat_leather('Mat_Backpack',  '6A4A28', roughness=0.78),
        'boot'     : mat_leather('Mat_Boot',      '3A2010', roughness=0.80),
        'potion'   : mat_potion_glass(),
        'staff'    : mat_wood_staff(),
        'brass'    : mat_brass(),
        'bedroll'  : mat_bedroll(),
    }

    print("[MushroomNPC] Building geometry...")
    cap      = build_mushroom_cap(mats)
    spots    = build_cap_spots(mats)
    stem     = build_stem(mats)
    eyes     = build_eyes(mats)
    smile    = build_smile(mats)
    collar   = build_collar(mats)
    body     = build_body(mats)
    arms     = build_arms(mats)
    hands    = build_hands(mats)
    belt     = build_belt(mats)
    buckle   = build_buckle(mats)
    potion   = build_potion(mats)
    backpack = build_backpack(mats)
    bedroll  = build_bedroll(mats)
    legs_boots = build_legs_boots(mats)
    staff    = build_staff(mats)
    bell_parts = build_bell(mats)

    all_objs = ([cap, spots, stem, smile, collar, body, belt, buckle,
                 potion, backpack, bedroll, staff]
                + eyes + arms + hands + legs_boots + bell_parts)

    print("[MushroomNPC] Organising scene...")
    root = organise(all_objs)

    # Material preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
            break

    print_report(all_objs, root)


main()
