"""
IsleTrial — Compass-Head Explorer NPC / Enemy
Blender 4.x Python Script

Creates the compass-headed explorer character from the reference image:
  • Large circular brass compass head — rim, parchment face, compass rose
  • Red north needle + blue south needle
  • Angry owl-style eyes + small beak on compass face
  • Wide-brim brown leather explorer hat (Indiana Jones style)
  • Olive-green explorer jacket with buckle straps
  • Brown leather utility belt with multiple pouches + 2 red potion bottles
  • Left hand: flaming torch    Right hand: short machete/knife
  • Brown leather backpack with rolled map scroll
  • Short legs + chunky brown leather boots
  BONUS: Standalone pocket compass prop (the one shown top-right in reference)

Run in Blender → Scripting workspace → Run Script.
Mix Factor 0 = Procedural preview  |  Mix Factor 1 = load Unity PBR image maps

Unity Export
──────────────────────────────────────────────────────────────
  Collection  : IsleTrial_CompassNPC
  Root empty  : CompassNPC_ROOT
  Select ROOT → File → Export → FBX  |  Scale Factor: 1.0
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

# ═══════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for d in [bpy.data.meshes, bpy.data.materials,
              bpy.data.curves, bpy.data.collections]:
        for item in list(d): d.remove(item)


def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def new_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.normal_update(); bm.to_mesh(me); bm.free()
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


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def subsurf(obj, level=2):
    s = obj.modifiers.new('Subsurf','SUBSURF')
    s.levels = level; s.render_levels = level


# ═══════════════════════════════════════════════════════
#  DUAL-PATH MATERIAL BUILDER
# ═══════════════════════════════════════════════════════

def _n(nd, t, loc, lbl=None):
    n = nd.new(t); n.location = loc
    if lbl: n.label = lbl
    return n

def _img(nd, slot, loc):
    n = nd.new('ShaderNodeTexImage')
    n.location = loc; n.label = f'[UNITY] {slot}'; n.name = slot
    return n

def _mp(nd, lk, scale=(1,1,1), loc=(-900,0)):
    tc = _n(nd,'ShaderNodeTexCoord',(-1100,0))
    mp = _n(nd,'ShaderNodeMapping', loc)
    mp.inputs['Scale'].default_value = (scale[0], scale[1], scale[2])
    lk.new(tc.outputs['UV'], mp.inputs['Vector'])
    return mp

def _mix_pi(nd, lk, proc, img_nd, loc, lbl=''):
    m = _n(nd,'ShaderNodeMixRGB',loc,lbl)
    m.blend_type='MIX'; m.inputs['Fac'].default_value=0.0
    lk.new(proc, m.inputs['Color1'])
    lk.new(img_nd.outputs['Color'], m.inputs['Color2'])
    return m

def _bump(nd, lk, h_sock, strength, dist, loc):
    b = _n(nd,'ShaderNodeBump',loc)
    b.inputs['Strength'].default_value=strength
    b.inputs['Distance'].default_value=dist
    lk.new(h_sock, b.inputs['Height'])
    return b

def _base_mat(name, roughness=0.8, metallic=0.0,
              alpha=1.0, transmission=0.0,
              emission=None, emission_str=0.0):
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


# ── Brass / Gold  ─────────────────────────────────────────────────────
def mat_brass():
    mat, nd, lk, bsdf = _base_mat('Mat_Brass', roughness=0.30, metallic=0.95)
    mp = _mp(nd,lk,scale=(4,4,4))
    noise = _n(nd,'ShaderNodeTexNoise',(-480,280))
    noise.inputs['Scale'].default_value=80.0; noise.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,280))
    cramp.color_ramp.elements[0].color=(*hex_rgb('7A5010'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('D4A030'),1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,'Mat_Brass_Albedo',(-480,-200))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mx = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,240),'Albedo')
    lk.new(mx.outputs['Color'],bsdf.inputs['Base Color'])
    scratch = _n(nd,'ShaderNodeTexNoise',(-480,-420))
    scratch.inputs['Scale'].default_value=250.0; scratch.inputs['Detail'].default_value=10.0
    lk.new(mp.outputs['Vector'],scratch.inputs['Vector'])
    mrng = _n(nd,'ShaderNodeMapRange',(-180,-420))
    mrng.inputs['To Min'].default_value=0.22; mrng.inputs['To Max'].default_value=0.55
    lk.new(scratch.outputs['Fac'],mrng.inputs['Value'])
    lk.new(mrng.outputs['Result'],bsdf.inputs['Roughness'])
    bmp = _bump(nd,lk,noise.outputs['Fac'],0.25,0.02,(-80,-580))
    lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat


# ── Compass Parchment Face  ───────────────────────────────────────────
def mat_compass_face():
    """Aged parchment: warm noise + subtle vignette around edges."""
    mat, nd, lk, bsdf = _base_mat('Mat_CompassFace', roughness=0.88)
    mp = _mp(nd,lk,scale=(1,1,1))
    noise = _n(nd,'ShaderNodeTexNoise',(-480,300))
    noise.inputs['Scale'].default_value=6.0; noise.inputs['Detail'].default_value=8.0
    noise.inputs['Roughness'].default_value=0.55
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,300))
    cramp.color_ramp.elements[0].color=(*hex_rgb('B89A60'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('E8D8A0'),1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,'Mat_CompassFace_Albedo',(-480,-220))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mx = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,240),'Albedo')
    lk.new(mx.outputs['Color'],bsdf.inputs['Base Color'])
    bmp = _bump(nd,lk,noise.outputs['Fac'],0.15,0.01,(-80,-360))
    img_n = _img(nd,'Mat_CompassFace_Normal',(-480,-500))
    lk.new(mp.outputs['Vector'],img_n.inputs['Vector'])
    nmap = _n(nd,'ShaderNodeNormalMap',(-80,-470)); lk.new(img_n.outputs['Color'],nmap.inputs['Color'])
    mixn = _n(nd,'ShaderNodeMixRGB',(160,-410),label='Mix Normal')
    mixn.inputs['Fac'].default_value=0.0
    lk.new(bmp.outputs['Normal'],mixn.inputs['Color1'])
    lk.new(nmap.outputs['Normal'],mixn.inputs['Color2'])
    lk.new(mixn.outputs['Color'],bsdf.inputs['Normal'])
    return mat


# ── Compass Needle  ───────────────────────────────────────────────────
def mat_needle_red():
    mat, nd, lk, bsdf = _base_mat('Mat_NeedleRed', roughness=0.35, metallic=0.7)
    bsdf.inputs['Base Color'].default_value = (*hex_rgb('CC2020'), 1.0)
    return mat

def mat_needle_blue():
    mat, nd, lk, bsdf = _base_mat('Mat_NeedleBlue', roughness=0.35, metallic=0.7)
    bsdf.inputs['Base Color'].default_value = (*hex_rgb('2040A0'), 1.0)
    return mat


# ── Angry Eyes  ───────────────────────────────────────────────────────
def mat_eye_angry():
    mat, nd, lk, bsdf = _base_mat('Mat_EyeAngry', roughness=0.05)
    mp = _mp(nd,lk,scale=(1,1,1))
    noise = _n(nd,'ShaderNodeTexNoise',(-480,200))
    noise.inputs['Scale'].default_value=3.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,200))
    cramp.color_ramp.elements[0].color=(*hex_rgb('1A0800'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('5A2A00'),1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,'Mat_EyeAngry_Albedo',(-480,-180))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mx = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,180),'Albedo')
    lk.new(mx.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Emission Color'].default_value   = (*hex_rgb('602000'), 1.0)
    bsdf.inputs['Emission Strength'].default_value = 0.6
    return mat

def mat_eye_shine():
    mat, nd, lk, bsdf = _base_mat('Mat_EyeShine', roughness=0.0,
                                   emission=hex_rgb('FFFFFF'), emission_str=1.5)
    bsdf.inputs['Base Color'].default_value=(1,1,1,1)
    return mat


# ── Leather  ──────────────────────────────────────────────────────────
def mat_leather(name, hex_col, roughness=0.78):
    mat, nd, lk, bsdf = _base_mat(name, roughness=roughness)
    mp = _mp(nd,lk,scale=(5,5,5))
    noise = _n(nd,'ShaderNodeTexNoise',(-480,280))
    noise.inputs['Scale'].default_value=45.0; noise.inputs['Detail'].default_value=10.0
    noise.inputs['Roughness'].default_value=0.65
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    base = hex_rgb(hex_col)
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,280))
    cramp.color_ramp.elements[0].color=(*tuple(max(c-0.14,0) for c in base),1.0)
    cramp.color_ramp.elements[1].color=(*base,1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,f'{name}_Albedo',(-480,-220))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mx = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,240),'Albedo')
    lk.new(mx.outputs['Color'],bsdf.inputs['Base Color'])
    bmp = _bump(nd,lk,noise.outputs['Fac'],0.65,0.03,(-80,-370))
    img_n = _img(nd,f'{name}_Normal',(-480,-520))
    lk.new(mp.outputs['Vector'],img_n.inputs['Vector'])
    nmap = _n(nd,'ShaderNodeNormalMap',(-80,-490)); lk.new(img_n.outputs['Color'],nmap.inputs['Color'])
    mixn = _n(nd,'ShaderNodeMixRGB',(160,-430),label='Mix Normal')
    mixn.inputs['Fac'].default_value=0.0
    lk.new(bmp.outputs['Normal'],mixn.inputs['Color1'])
    lk.new(nmap.outputs['Normal'],mixn.inputs['Color2'])
    lk.new(mixn.outputs['Color'],bsdf.inputs['Normal'])
    mrng = _n(nd,'ShaderNodeMapRange',(-180,-750))
    mrng.inputs['To Min'].default_value=roughness-0.10; mrng.inputs['To Max'].default_value=roughness+0.10
    lk.new(noise.outputs['Fac'],mrng.inputs['Value'])
    lk.new(mrng.outputs['Result'],bsdf.inputs['Roughness'])
    return mat


# ── Explorer Jacket  ──────────────────────────────────────────────────
def mat_jacket():
    mat, nd, lk, bsdf = _base_mat('Mat_Jacket', roughness=0.92)
    mp = _mp(nd,lk,scale=(4,4,4))
    wave = _n(nd,'ShaderNodeTexWave',(-480,280))
    wave.wave_type='BANDS'; wave.bands_direction='X'
    wave.inputs['Scale'].default_value=28.0; wave.inputs['Distortion'].default_value=1.8
    wave.inputs['Detail'].default_value=6.0
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    noise = _n(nd,'ShaderNodeTexNoise',(-480,50))
    noise.inputs['Scale'].default_value=7.0; noise.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,280))
    cramp.color_ramp.elements[0].color=(*hex_rgb('3A4820'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('5C6A38'),1.0)
    lk.new(wave.outputs['Color'],cramp.inputs['Fac'])
    ov = _n(nd,'ShaderNodeMixRGB',(40,200))
    ov.blend_type='OVERLAY'; ov.inputs['Fac'].default_value=0.20
    lk.new(cramp.outputs['Color'],ov.inputs['Color1'])
    lk.new(noise.outputs['Color'],ov.inputs['Color2'])
    img_a = _img(nd,'Mat_Jacket_Albedo',(-480,-240))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mx = _mix_pi(nd,lk,ov.outputs['Color'],img_a,(280,220),'Albedo')
    lk.new(mx.outputs['Color'],bsdf.inputs['Base Color'])
    bmp = _bump(nd,lk,wave.outputs['Color'],0.5,0.03,(-80,-390))
    img_n = _img(nd,'Mat_Jacket_Normal',(-480,-540))
    lk.new(mp.outputs['Vector'],img_n.inputs['Vector'])
    nmap = _n(nd,'ShaderNodeNormalMap',(-80,-510)); lk.new(img_n.outputs['Color'],nmap.inputs['Color'])
    mixn = _n(nd,'ShaderNodeMixRGB',(160,-450),label='Mix Normal')
    mixn.inputs['Fac'].default_value=0.0
    lk.new(bmp.outputs['Normal'],mixn.inputs['Color1'])
    lk.new(nmap.outputs['Normal'],mixn.inputs['Color2'])
    lk.new(mixn.outputs['Color'],bsdf.inputs['Normal'])
    return mat


# ── Metal (Knife/Torch)  ──────────────────────────────────────────────
def mat_metal_blade():
    mat, nd, lk, bsdf = _base_mat('Mat_Blade', roughness=0.20, metallic=0.95)
    mp = _mp(nd,lk,scale=(6,1,1))
    noise = _n(nd,'ShaderNodeTexNoise',(-480,200))
    noise.inputs['Scale'].default_value=150.0; noise.inputs['Detail'].default_value=10.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,200))
    cramp.color_ramp.elements[0].color=(*hex_rgb('A0A0B0'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('E0E0F0'),1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,'Mat_Blade_Albedo',(-480,-200))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mx = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,180),'Albedo')
    lk.new(mx.outputs['Color'],bsdf.inputs['Base Color'])
    mrng = _n(nd,'ShaderNodeMapRange',(-180,-380))
    mrng.inputs['To Min'].default_value=0.12; mrng.inputs['To Max'].default_value=0.40
    lk.new(noise.outputs['Fac'],mrng.inputs['Value'])
    lk.new(mrng.outputs['Result'],bsdf.inputs['Roughness'])
    return mat


# ── Flame  ────────────────────────────────────────────────────────────
def mat_flame():
    mat, nd, lk, bsdf = _base_mat('Mat_Flame', roughness=0.0,
                                   emission=hex_rgb('FF8000'), emission_str=5.0)
    mp = _mp(nd,lk,scale=(2,2,4))
    noise = _n(nd,'ShaderNodeTexNoise',(-480,200))
    noise.inputs['Scale'].default_value=4.0; noise.inputs['Detail'].default_value=12.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,200))
    cramp.color_ramp.elements[0].color=(*hex_rgb('FF2000'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('FFCC00'),1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])
    lk.new(cramp.outputs['Color'],bsdf.inputs['Base Color'])
    mrng = _n(nd,'ShaderNodeMapRange',(-180,-200))
    mrng.inputs['To Min'].default_value=3.5; mrng.inputs['To Max'].default_value=6.5
    lk.new(noise.outputs['Fac'],mrng.inputs['Value'])
    lk.new(mrng.outputs['Result'],bsdf.inputs['Emission Strength'])
    return mat


# ── Red Potion  ───────────────────────────────────────────────────────
def mat_potion():
    mat, nd, lk, bsdf = _base_mat('Mat_Potion', roughness=0.04,
                                   alpha=0.55, transmission=0.9,
                                   emission=hex_rgb('FF1818'), emission_str=2.0)
    bsdf.inputs['Base Color'].default_value=(*hex_rgb('FF2828'),1.0)
    bsdf.inputs['IOR'].default_value=1.52
    return mat


# ── Torch Wood  ───────────────────────────────────────────────────────
def mat_torch_wood():
    mat, nd, lk, bsdf = _base_mat('Mat_TorchWood', roughness=0.90)
    mp = _mp(nd,lk,scale=(10,1,1))
    wave = _n(nd,'ShaderNodeTexWave',(-480,200))
    wave.wave_type='BANDS'; wave.bands_direction='X'
    wave.inputs['Scale'].default_value=20.0; wave.inputs['Distortion'].default_value=2.0
    wave.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,200))
    cramp.color_ramp.elements[0].color=(*hex_rgb('2A1808'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('6A3C1C'),1.0)
    lk.new(wave.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,'Mat_TorchWood_Albedo',(-480,-200))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mx = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,180),'Albedo')
    lk.new(mx.outputs['Color'],bsdf.inputs['Base Color'])
    bmp = _bump(nd,lk,wave.outputs['Color'],0.8,0.04,(-80,-340))
    lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat


# ── Scroll/Map  ───────────────────────────────────────────────────────
def mat_scroll():
    mat, nd, lk, bsdf = _base_mat('Mat_Scroll', roughness=0.92)
    mp = _mp(nd,lk,scale=(3,3,3))
    noise = _n(nd,'ShaderNodeTexNoise',(-480,200))
    noise.inputs['Scale'].default_value=5.0; noise.inputs['Detail'].default_value=6.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cramp = _n(nd,'ShaderNodeValToRGB',(-180,200))
    cramp.color_ramp.elements[0].color=(*hex_rgb('C0A870'),1.0)
    cramp.color_ramp.elements[1].color=(*hex_rgb('E0C890'),1.0)
    lk.new(noise.outputs['Color'],cramp.inputs['Fac'])
    img_a = _img(nd,'Mat_Scroll_Albedo',(-480,-200))
    lk.new(mp.outputs['Vector'],img_a.inputs['Vector'])
    mx = _mix_pi(nd,lk,cramp.outputs['Color'],img_a,(280,180),'Albedo')
    lk.new(mx.outputs['Color'],bsdf.inputs['Base Color'])
    return mat


# ═══════════════════════════════════════════════════════
#  GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

# ── Compass Rim  ─────────────────────────────────────────────────────
def build_compass_rim(mats):
    """Thick circular brass bezel — the main head shape."""
    bm = bmesh.new()
    SEGS  = 48
    R_IN  = 0.28
    R_OUT = 0.34
    DEPTH = 0.10
    Z_BASE = 0.80   # bottom of compass head

    for z in (Z_BASE, Z_BASE + DEPTH):
        for s in range(SEGS):
            a = (s/SEGS)*math.tau
            bm.verts.new(Vector((math.cos(a)*R_IN,  math.sin(a)*R_IN,  z)))
            bm.verts.new(Vector((math.cos(a)*R_OUT, math.sin(a)*R_OUT, z)))

    bm.verts.ensure_lookup_table()
    n4 = SEGS * 2

    for s in range(SEGS):
        s1 = (s+1) % SEGS
        bi  = s*2;   bi1 = s1*2
        bo  = s*2+1; bo1 = s1*2+1
        ti  = n4+s*2;   ti1 = n4+s1*2
        to_ = n4+s*2+1; to1 = n4+s1*2+1
        bm.faces.new([bm.verts[bi],  bm.verts[bi1], bm.verts[bo1], bm.verts[bo]])    # bottom
        bm.faces.new([bm.verts[ti],  bm.verts[ti1], bm.verts[to1], bm.verts[to_]])   # top
        bm.faces.new([bm.verts[bo],  bm.verts[bo1], bm.verts[to1], bm.verts[to_]])   # outer
        bm.faces.new([bm.verts[bi1], bm.verts[bi],  bm.verts[ti],  bm.verts[ti1]])   # inner
        bm.faces.new([bm.verts[bi],  bm.verts[bo],  bm.verts[to_], bm.verts[ti]])    # side a
        bm.faces.new([bm.verts[bo1], bm.verts[bi1], bm.verts[ti1], bm.verts[to1]])   # side b

    bm.normal_update()
    rim = new_obj('CompassHead_Rim', bm)
    subsurf(rim, 1)
    assign(rim, mats['brass'])
    smart_uv(rim)

    # Decorative knobs (small spheres around rim)
    knob_mats = mats['brass']
    for ki in range(8):
        a  = (ki/8) * math.tau
        bm2 = bmesh.new()
        bmesh.ops.create_uvsphere(bm2, u_segments=8, v_segments=6, radius=0.022)
        bm2.normal_update()
        knob = new_obj(f'_rim_knob_{ki}', bm2)
        knob.location = (math.cos(a)*(R_OUT+0.015), math.sin(a)*(R_OUT+0.015),
                         Z_BASE + DEPTH*0.5)
        knob.parent = rim
        assign(knob, mats['brass'])

    # Top hanging ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.030, minor_radius=0.008,
        major_segments=16, minor_segments=8,
        location=(0, 0, Z_BASE + DEPTH + 0.030))
    hring = bpy.context.active_object
    hring.name = 'CompassHead_Ring'
    assign(hring, mats['brass'])

    return rim


# ── Compass Face  ────────────────────────────────────────────────────
def build_compass_face(mats):
    """Flat parchment disc inside the rim."""
    bm = bmesh.new()
    SEGS = 48
    R    = 0.275
    Z    = 0.875

    center = bm.verts.new(Vector((0,0,Z)))
    ring   = [bm.verts.new(Vector((math.cos((s/SEGS)*math.tau)*R,
                                   math.sin((s/SEGS)*math.tau)*R, Z)))
              for s in range(SEGS)]
    for s in range(SEGS):
        bm.faces.new([center, ring[(s+1)%SEGS], ring[s]])

    bm.normal_update()
    face = new_obj('CompassHead_Face', bm)
    assign(face, mats['compass_face'])
    smart_uv(face)
    return face


# ── Compass Rose (geometry)  ─────────────────────────────────────────
def build_compass_rose(mats):
    """Raised star/rose geometry on the compass face."""
    rose_parts = []
    Z = 0.882

    # 8-point star: 4 long points (NESW) + 4 short diagonal
    point_defs = [
        (0,   0.20, 0.028, False),  # N — long
        (90,  0.20, 0.028, False),  # E
        (180, 0.20, 0.028, False),  # S
        (270, 0.20, 0.028, False),  # W
        (45,  0.12, 0.020, True),   # NE — short
        (135, 0.12, 0.020, True),   # SE
        (225, 0.12, 0.020, True),   # SW
        (315, 0.12, 0.020, True),   # NW
    ]
    for angle_d, length, half_w, is_short in point_defs:
        a  = math.radians(angle_d)
        bm = bmesh.new()
        # Diamond-shaped point
        verts = [
            bm.verts.new(Vector((0, 0, Z))),                         # center
            bm.verts.new(Vector((math.cos(a)*length,
                                 math.sin(a)*length, Z+0.008))),     # tip
            bm.verts.new(Vector((math.cos(a+math.pi/2)*half_w,
                                 math.sin(a+math.pi/2)*half_w, Z+0.003))),
            bm.verts.new(Vector((math.cos(a-math.pi/2)*half_w,
                                 math.sin(a-math.pi/2)*half_w, Z+0.003))),
        ]
        bm.faces.new([verts[0], verts[2], verts[1]])
        bm.faces.new([verts[0], verts[1], verts[3]])
        bm.normal_update()
        pname = f'_rose_pt_{angle_d}'
        pt = new_obj(pname, bm)
        assign(pt, mats['needle_red'] if angle_d == 0 else
                   (mats['needle_blue'] if angle_d == 180 else mats['brass']))
        rose_parts.append(pt)

    # Center circle
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=16, radius1=0.030, radius2=0.010, depth=0.012)
    bm.normal_update()
    center_knob = new_obj('_rose_center', bm)
    center_knob.location = (0, 0, Z)
    assign(center_knob, mats['brass'])
    rose_parts.append(center_knob)

    # Merge all rose parts
    activate(rose_parts[0])
    for p in rose_parts[1:]: p.select_set(True)
    bpy.ops.object.join()
    rose = bpy.context.active_object
    rose.name = 'CompassHead_Rose'
    smart_uv(rose)
    return rose


# ── Compass Needles  ─────────────────────────────────────────────────
def build_needles(mats):
    """Red north needle + blue south needle, raised slightly above face."""
    needles = []
    Z = 0.892
    for color, angle_d, mat_key, length in [
        ('Red',  0,   'needle_red',  0.18),
        ('Blue', 180, 'needle_blue', 0.14),
    ]:
        a  = math.radians(angle_d)
        bm = bmesh.new()
        hw = 0.018
        verts = [
            bm.verts.new(Vector(( 0, 0, Z))),
            bm.verts.new(Vector((math.cos(a)*length, math.sin(a)*length, Z+0.006))),
            bm.verts.new(Vector((math.cos(a+math.pi/2)*hw, math.sin(a+math.pi/2)*hw, Z+0.003))),
            bm.verts.new(Vector((math.cos(a-math.pi/2)*hw, math.sin(a-math.pi/2)*hw, Z+0.003))),
        ]
        bm.faces.new([verts[0],verts[2],verts[1]])
        bm.faces.new([verts[0],verts[1],verts[3]])
        bm.normal_update()
        nd = new_obj(f'CompassHead_Needle_{color}', bm)
        assign(nd, mats[mat_key])
        needles.append(nd)
    return needles


# ── Angry Eyes  ──────────────────────────────────────────────────────
def build_angry_eyes(mats):
    eyes = []
    Z_BASE = 0.830

    for side, sx in [('L',-0.090), ('R',0.090)]:
        bm = bmesh.new()
        # Angry triangular eye shape — slanted inward at top (angry frown)
        verts = [
            bm.verts.new(Vector((sx-0.040*(-1 if side=='L' else 1), 0.276, Z_BASE+0.020))),  # inner top
            bm.verts.new(Vector((sx+0.045*(-1 if side=='L' else 1), 0.276, Z_BASE+0.010))),  # outer top
            bm.verts.new(Vector((sx+0.040*(-1 if side=='L' else 1), 0.276, Z_BASE-0.020))),  # outer bottom
            bm.verts.new(Vector((sx-0.038*(-1 if side=='L' else 1), 0.276, Z_BASE-0.022))),  # inner bottom
        ]
        bm.faces.new(verts)
        bm.normal_update()
        eye = new_obj(f'CompassHead_Eye_{side}', bm)
        assign(eye, mats['eye_angry'])
        smart_uv(eye)

        # Shine dot
        bm2 = bmesh.new()
        bmesh.ops.create_uvsphere(bm2, u_segments=6, v_segments=4, radius=0.009)
        bm2.normal_update()
        shine = new_obj(f'CompassHead_EyeShine_{side}', bm2)
        shine.location = (sx+0.010*(-1 if side=='L' else 1), 0.278, Z_BASE+0.008)
        assign(shine, mats['eye_shine'])
        eyes.extend([eye, shine])
    return eyes


# ── Beak  ────────────────────────────────────────────────────────────
def build_beak(mats):
    bm = bmesh.new()
    verts = [
        bm.verts.new(Vector((-0.025, 0.272, 0.812))),
        bm.verts.new(Vector(( 0.025, 0.272, 0.812))),
        bm.verts.new(Vector((-0.012, 0.272, 0.796))),
        bm.verts.new(Vector(( 0.012, 0.272, 0.796))),
        bm.verts.new(Vector(( 0.000, 0.298, 0.804))),  # tip
    ]
    bm.faces.new([verts[0],verts[1],verts[3],verts[2]])
    bm.faces.new([verts[0],verts[4],verts[1]])
    bm.faces.new([verts[2],verts[3],verts[4]])
    bm.faces.new([verts[0],verts[2],verts[4]])
    bm.faces.new([verts[1],verts[4],verts[3]])
    bm.normal_update()
    beak = new_obj('CompassHead_Beak', bm)
    assign(beak, mats['brass'])
    smart_uv(beak)
    return beak


# ── Explorer Hat  ─────────────────────────────────────────────────────
def build_hat(mats):
    """Wide-brim explorer hat."""
    bm = bmesh.new()
    SEGS = 32

    # Crown (dome top)
    crown_rings = []
    for ri in range(8):
        t = ri / 7
        theta = t * math.radians(90)
        r = math.sin(theta) * 0.22
        z = 1.02 + math.cos(theta) * 0.16
        ring = [bm.verts.new(Vector((math.cos((s/SEGS)*math.tau)*r,
                                     math.sin((s/SEGS)*math.tau)*r, z)))
                for s in range(SEGS)]
        crown_rings.append(ring)

    crown_top = bm.verts.new(Vector((0,0,1.185)))
    for s in range(SEGS):
        bm.faces.new([crown_rings[-1][(s+1)%SEGS], crown_rings[-1][s], crown_top])

    for ri in range(len(crown_rings)-1):
        for s in range(SEGS):
            s1=(s+1)%SEGS
            bm.faces.new([crown_rings[ri][s],crown_rings[ri][s1],
                          crown_rings[ri+1][s1],crown_rings[ri+1][s]])

    # Brim (wide flat ring)
    brim_ir, brim_or = 0.225, 0.500
    brim_z_i, brim_z_o = 1.020, 0.985
    brim_top_in  = [bm.verts.new(Vector((math.cos((s/SEGS)*math.tau)*brim_ir,
                                          math.sin((s/SEGS)*math.tau)*brim_ir, brim_z_i)))
                    for s in range(SEGS)]
    brim_top_out = [bm.verts.new(Vector((math.cos((s/SEGS)*math.tau)*brim_or,
                                          math.sin((s/SEGS)*math.tau)*brim_or, brim_z_o)))
                    for s in range(SEGS)]
    brim_bot_in  = [bm.verts.new(Vector((math.cos((s/SEGS)*math.tau)*(brim_ir-0.01),
                                          math.sin((s/SEGS)*math.tau)*(brim_ir-0.01), brim_z_i-0.025)))
                    for s in range(SEGS)]
    brim_bot_out = [bm.verts.new(Vector((math.cos((s/SEGS)*math.tau)*brim_or,
                                          math.sin((s/SEGS)*math.tau)*brim_or, brim_z_o-0.020)))
                    for s in range(SEGS)]

    for s in range(SEGS):
        s1=(s+1)%SEGS
        # Connect crown base ring to brim inner
        bm.faces.new([crown_rings[0][s],crown_rings[0][s1],
                      brim_top_in[s1],brim_top_in[s]])
        # Top brim face
        bm.faces.new([brim_top_in[s],brim_top_in[s1],
                      brim_top_out[s1],brim_top_out[s]])
        # Outer brim edge
        bm.faces.new([brim_top_out[s],brim_top_out[s1],
                      brim_bot_out[s1],brim_bot_out[s]])
        # Bottom brim face
        bm.faces.new([brim_bot_out[s],brim_bot_out[s1],
                      brim_bot_in[s1],brim_bot_in[s]])
        # Inner brim edge
        bm.faces.new([brim_bot_in[s],brim_bot_in[s1],
                      brim_top_in[s1],brim_top_in[s]])

    bm.normal_update()
    hat = new_obj('Hat', bm)
    sub = hat.modifiers.new('Subsurf','SUBSURF'); sub.levels=2
    assign(hat, mats['hat'])
    smart_uv(hat)

    # Hat band (thin leather strip around crown)
    bm2 = bmesh.new()
    for s in range(SEGS):
        a0=(s/SEGS)*math.tau; a1=((s+1)/SEGS)*math.tau
        r0, r1 = 0.218, 0.225
        for z in (1.025, 1.060):
            for a, r in [(a0,r0),(a0,r1),(a1,r1),(a1,r0)]:
                bm2.verts.new(Vector((math.cos(a)*r, math.sin(a)*r, z)))
    bm2.normal_update()
    band = new_obj('Hat_Band', bm2)
    assign(band, mats['belt'])
    smart_uv(band)
    return hat


# ── Body / Jacket  ───────────────────────────────────────────────────
def build_body(mats):
    bm = bmesh.new()
    SEGS = 20
    sections = [
        (0.72, 0.22, 0.16),
        (0.60, 0.24, 0.17),
        (0.46, 0.24, 0.17),
        (0.30, 0.23, 0.16),
        (0.15, 0.22, 0.15),
        (0.05, 0.21, 0.14),
    ]
    rings = []
    for (z, w, d) in sections:
        ring = [bm.verts.new(Vector((math.cos((s/SEGS)*math.tau)*w,
                                     math.sin((s/SEGS)*math.tau)*d, z)))
                for s in range(SEGS)]
        rings.append(ring)

    for ri in range(len(rings)-1):
        for s in range(SEGS):
            s1=(s+1)%SEGS
            bm.faces.new([rings[ri][s],rings[ri][s1],
                          rings[ri+1][s1],rings[ri+1][s]])

    tc = bm.verts.new(Vector((0,0,0.73)))
    for s in range(SEGS):
        bm.faces.new([rings[0][s],rings[0][(s+1)%SEGS],tc])
    bc = bm.verts.new(Vector((0,0,0.04)))
    for s in range(SEGS):
        bm.faces.new([rings[-1][(s+1)%SEGS],rings[-1][s],bc])

    bm.normal_update()
    body = new_obj('Jacket_Body', bm)
    sub = body.modifiers.new('Subsurf','SUBSURF'); sub.levels=2
    assign(body, mats['jacket'])
    smart_uv(body)
    return body


# ── Arms  ────────────────────────────────────────────────────────────
def build_arms(mats):
    arms = []
    for side, sx, hold_angle in [('L',-1, 25), ('R', 1, -20)]:
        bm = bmesh.new()
        SEGS = 14
        # Slightly raised arms holding items
        arm_pts = [
            (sx*0.24, 0.00, 0.64, 0.075),
            (sx*0.30, 0.02, 0.54, 0.070),
            (sx*0.36, 0.04, 0.42, 0.065),
            (sx*0.34, 0.05, 0.30, 0.062),
            (sx*0.30, 0.06, 0.20, 0.058),
        ]
        rings = []
        for (ax,ay,az,ar) in arm_pts:
            ring=[bm.verts.new(Vector((ax+math.cos((s/SEGS)*math.tau)*ar,
                                       ay+math.sin((s/SEGS)*math.tau)*ar*0.8,az)))
                  for s in range(SEGS)]
            rings.append(ring)
        for ri in range(len(rings)-1):
            for s in range(SEGS):
                s1=(s+1)%SEGS
                bm.faces.new([rings[ri][s],rings[ri][s1],
                              rings[ri+1][s1],rings[ri+1][s]])
        bm.normal_update()
        arm = new_obj(f'Arm_{side}', bm)
        sub = arm.modifiers.new('Subsurf','SUBSURF'); sub.levels=1
        assign(arm, mats['jacket'])
        smart_uv(arm)
        arms.append(arm)
    return arms


# ── Hands  ───────────────────────────────────────────────────────────
def build_hands(mats):
    hands = []
    for side, sx in [('L',-1),('R',1)]:
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.055)
        for v in bm.verts: v.co.x*=0.82; v.co.y*=0.65; v.co.z*=0.78
        bm.normal_update()
        hand = new_obj(f'Hand_{side}', bm)
        hand.location = (sx*0.32, 0.07, 0.14)
        assign(hand, mat_leather('Mat_Glove','4A2A0A', roughness=0.82))
        smart_uv(hand)
        hands.append(hand)
    return hands


# ── Belt + Pouches  ──────────────────────────────────────────────────
def build_belt_and_pouches(mats):
    objs = []
    bm = bmesh.new()
    SEGS = 32; Z=0.28; THICK=0.022
    for s in range(SEGS):
        a0=(s/SEGS)*math.tau; a1=((s+1)/SEGS)*math.tau
        ri, ro = 0.210, 0.235
        vs = [bm.verts.new(Vector((math.cos(a)*r, math.sin(a)*r, zz)))
              for a,r,zz in [(a0,ri,Z),(a0,ro,Z),(a1,ro,Z),(a1,ri,Z),
                              (a0,ri,Z+THICK),(a0,ro,Z+THICK),(a1,ro,Z+THICK),(a1,ri,Z+THICK)]]
        for fi in [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]:
            bm.faces.new([vs[k] for k in fi])
    bm.normal_update()
    belt = new_obj('Belt', bm)
    assign(belt, mats['belt'])
    smart_uv(belt); objs.append(belt)

    # Buckle
    bm2 = bmesh.new(); bmesh.ops.create_cube(bm2, size=1)
    for v in bm2.verts: v.co.x*=0.055; v.co.y*=0.018; v.co.z*=0.038
    bm2.normal_update(); buckle = new_obj('Belt_Buckle', bm2)
    buckle.location=(0,0.232,Z+THICK/2); assign(buckle,mats['brass']); objs.append(buckle)

    # Belt pouches (3 small boxes on front/sides)
    pouch_positions = [(-0.18, 0.14, 0.225), (0.18, 0.14, 0.225), (0.00, 0.22, 0.215)]
    for pi_, (px,py,pz) in enumerate(pouch_positions):
        bm3 = bmesh.new(); bmesh.ops.create_cube(bm3, size=1)
        for v in bm3.verts: v.co.x*=0.055; v.co.y*=0.040; v.co.z*=0.065
        bm3.normal_update(); pouch = new_obj(f'Belt_Pouch_{pi_}', bm3)
        pouch.location=(px,py,pz); assign(pouch,mats['belt'])
        sub3=pouch.modifiers.new('Subsurf','SUBSURF'); sub3.levels=1
        smart_uv(pouch); objs.append(pouch)

    return objs


# ── Potion Bottles on Belt  ──────────────────────────────────────────
def build_potion_bottles(mats):
    bottles = []
    for bx in (-0.12, 0.12):
        bm = bmesh.new()
        for (z,r) in [(0,0.024),(0.015,0.026),(0.045,0.028),(0.065,0.026),
                      (0.080,0.018),(0.095,0.014),(0.100,0.014)]:
            ring=[bm.verts.new(Vector((math.cos((s/12)*math.tau)*r,
                                       math.sin((s/12)*math.tau)*r,z)))
                  for s in range(12)]
        bm.verts.ensure_lookup_table()
        # Build cylinder sections
        total_r = 7; SEGS = 12
        base_rings = []
        bm.free()
        bm = bmesh.new()
        pts = [(0,0.024),(0.015,0.026),(0.045,0.028),(0.065,0.026),
               (0.080,0.018),(0.095,0.014),(0.100,0.014)]
        rrings = []
        for (z,r) in pts:
            rr=[bm.verts.new(Vector((math.cos((s/SEGS)*math.tau)*r,
                                     math.sin((s/SEGS)*math.tau)*r,z)))
                for s in range(SEGS)]
            rrings.append(rr)
        for ri in range(len(rrings)-1):
            for s in range(SEGS):
                s1=(s+1)%SEGS
                bm.faces.new([rrings[ri][s],rrings[ri][s1],
                              rrings[ri+1][s1],rrings[ri+1][s]])
        bc=bm.verts.new(Vector((0,0,0)))
        for s in range(SEGS): bm.faces.new([rrings[0][(s+1)%SEGS],rrings[0][s],bc])
        tc=bm.verts.new(Vector((0,0,0.105)))
        for s in range(SEGS): bm.faces.new([rrings[-1][s],rrings[-1][(s+1)%SEGS],tc])
        bm.normal_update()
        bot = new_obj(f'Potion_{int(bx*100)}', bm)
        bot.location=(bx, 0.18, 0.200)
        bot.rotation_euler=(0,math.radians(10*(-1 if bx<0 else 1)),0)
        sub=bot.modifiers.new('Subsurf','SUBSURF'); sub.levels=1
        assign(bot,mats['potion'])
        smart_uv(bot); bottles.append(bot)
    return bottles


# ── Torch (Left Hand)  ───────────────────────────────────────────────
def build_torch(mats):
    objs = []
    # Handle
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=10, radius1=0.020, radius2=0.015, depth=0.32)
    bm.normal_update()
    handle = new_obj('Torch_Handle', bm)
    handle.location = (-0.36, 0.07, 0.30)
    handle.rotation_euler = (0, math.radians(15), math.radians(10))
    assign(handle, mats['torch_wood'])
    smart_uv(handle); objs.append(handle)

    # Torch head (wrapped cloth)
    bm2 = bmesh.new()
    bmesh.ops.create_cone(bm2, cap_ends=True, cap_tris=False,
                          segments=12, radius1=0.030, radius2=0.025, depth=0.07)
    bm2.normal_update()
    head = new_obj('Torch_Head', bm2)
    head.location = (-0.38, 0.08, 0.475)
    head.rotation_euler = (0, math.radians(15), math.radians(10))
    assign(head, mats['belt'])
    objs.append(head)

    # Flame (displaced cone)
    bm3 = bmesh.new()
    SEGS=12; RINGS=8
    for ri in range(RINGS+1):
        t=ri/RINGS
        r=0.032*(1-t*0.9)
        z=t*0.15
        noise_push=math.sin(t*math.pi)*0.010
        for s in range(SEGS):
            a=(s/SEGS)*math.tau
            bm3.verts.new(Vector((math.cos(a)*r+noise_push,
                                   math.sin(a)*r,z)))
    bm3.verts.ensure_lookup_table()
    for ri in range(RINGS):
        for s in range(SEGS):
            s1=(s+1)%SEGS
            bm3.faces.new([bm3.verts[ri*SEGS+s],bm3.verts[ri*SEGS+s1],
                           bm3.verts[(ri+1)*SEGS+s1],bm3.verts[(ri+1)*SEGS+s]])
    tip=bm3.verts.new(Vector((0,0,0.16)))
    for s in range(SEGS):
        bm3.faces.new([bm3.verts[RINGS*SEGS+s],bm3.verts[RINGS*SEGS+(s+1)%SEGS],tip])
    bm3.normal_update()
    flame = new_obj('Torch_Flame', bm3)
    flame.location = (-0.385, 0.085, 0.510)
    flame.rotation_euler = (0, math.radians(15), math.radians(10))
    assign(flame, mats['flame'])
    objs.append(flame)
    return objs


# ── Knife / Machete (Right Hand)  ────────────────────────────────────
def build_knife(mats):
    objs = []
    # Blade
    bm = bmesh.new()
    verts = [
        bm.verts.new(Vector((0.000,  0.000, 0.000))),  # guard bottom
        bm.verts.new(Vector((0.008,  0.000, 0.000))),
        bm.verts.new(Vector((0.005, -0.002, 0.340))),  # tip
        bm.verts.new(Vector((-0.002, 0.000, 0.340))),
        bm.verts.new(Vector((-0.015, 0.000, 0.000))),  # spine
        bm.verts.new(Vector((-0.015, 0.000, 0.340))),
    ]
    bm.faces.new([verts[0],verts[1],verts[2],verts[3]])
    bm.faces.new([verts[0],verts[4],verts[5],verts[3]])
    bm.faces.new([verts[1],verts[0],verts[4]])
    bm.faces.new([verts[2],verts[1],verts[4],verts[5]])
    bm.faces.new([verts[3],verts[2],verts[5]])
    bm.normal_update()
    blade = new_obj('Knife_Blade', bm)
    blade.location = (0.35, 0.04, 0.22)
    blade.rotation_euler = (math.radians(-5), math.radians(-12), math.radians(-8))
    assign(blade, mats['blade'])
    smart_uv(blade); objs.append(blade)

    # Handle
    bm2 = bmesh.new()
    bmesh.ops.create_cone(bm2, cap_ends=True, cap_tris=False,
                          segments=8, radius1=0.022, radius2=0.018, depth=0.16)
    bm2.normal_update()
    hndl = new_obj('Knife_Handle', bm2)
    hndl.location = (0.35, 0.04, 0.08)
    hndl.rotation_euler = blade.rotation_euler.copy()
    assign(hndl, mats['belt'])
    smart_uv(hndl); objs.append(hndl)

    # Guard
    bm3 = bmesh.new(); bmesh.ops.create_cube(bm3, size=1)
    for v in bm3.verts: v.co.x*=0.065; v.co.y*=0.015; v.co.z*=0.012
    bm3.normal_update()
    guard = new_obj('Knife_Guard', bm3)
    guard.location = blade.location.copy()
    guard.rotation_euler = blade.rotation_euler.copy()
    assign(guard, mats['brass'])
    objs.append(guard)
    return objs


# ── Legs + Boots  ─────────────────────────────────────────────────────
def build_legs_boots(mats):
    objs = []
    for side, sx in [('L',-1),('R',1)]:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                              segments=14, radius1=0.090, radius2=0.080, depth=0.16)
        bm.normal_update()
        leg = new_obj(f'Leg_{side}', bm)
        leg.location=(sx*0.095, 0, 0.04)
        assign(leg, mats['jacket']); smart_uv(leg); objs.append(leg)

        bm2 = bmesh.new()
        vs2 = [
            bm2.verts.new(Vector((-0.075,-0.065,0.000))),
            bm2.verts.new(Vector(( 0.075,-0.065,0.000))),
            bm2.verts.new(Vector(( 0.082, 0.120,0.000))),
            bm2.verts.new(Vector((-0.082, 0.120,0.000))),
            bm2.verts.new(Vector((-0.065,-0.055,0.230))),
            bm2.verts.new(Vector(( 0.065,-0.055,0.230))),
            bm2.verts.new(Vector(( 0.072, 0.105,0.230))),
            bm2.verts.new(Vector((-0.072, 0.105,0.230))),
        ]
        for fi in [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]:
            bm2.faces.new([vs2[k] for k in fi])
        bm2.normal_update()
        boot = new_obj(f'Boot_{side}', bm2)
        boot.location=(sx*0.095,0.012,-0.235)
        sub2=boot.modifiers.new('Subsurf','SUBSURF'); sub2.levels=2
        assign(boot,mats['boot']); smart_uv(boot); objs.append(boot)
    return objs


# ── Backpack  ─────────────────────────────────────────────────────────
def build_backpack(mats):
    bm = bmesh.new()
    W,D,H = 0.22,0.12,0.30
    vs = []
    for z in (0.18, 0.18+H):
        for x in (-W/2, W/2):
            for y in (-0.20-D, -0.20):
                vs.append(bm.verts.new(Vector((x,y,z))))
    for fi in [(0,1,3,2),(4,5,7,6),(0,1,5,4),(2,3,7,6),(1,3,7,5),(0,2,6,4)]:
        bm.faces.new([vs[k] for k in fi])
    bm.normal_update()
    pack = new_obj('Backpack', bm)
    sub=pack.modifiers.new('Subsurf','SUBSURF'); sub.levels=1
    assign(pack,mats['backpack']); smart_uv(pack)

    # Backpack straps
    for sx2 in (-0.07, 0.07):
        bm2=bmesh.new(); bmesh.ops.create_cube(bm2,size=1)
        for v in bm2.verts: v.co.x*=0.025; v.co.y*=0.28; v.co.z*=0.018
        bm2.normal_update(); strap=new_obj('_strap',bm2)
        strap.location=(sx2,-0.12,0.40); strap.rotation_euler=(math.radians(35),0,0)
        assign(strap,mats['belt'])

    return pack


# ── Map Scroll  ───────────────────────────────────────────────────────
def build_scroll(mats):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=16, radius1=0.040, radius2=0.040, depth=0.22)
    bm.normal_update()
    scroll = new_obj('Map_Scroll', bm)
    scroll.location = (0.10, -0.20, 0.52)
    scroll.rotation_euler = (math.radians(85), 0, math.radians(20))
    assign(scroll, mats['scroll'])
    smart_uv(scroll)
    return scroll


# ── Standalone Pocket Compass Prop  ──────────────────────────────────
def build_standalone_compass(mats):
    """The round pocket compass shown in the top-right of the reference image."""
    OFFSET = (2.0, 0, 0.5)  # staging area — separate from character
    objs = []

    # Outer case rim
    bm = bmesh.new()
    SEGS=40; RI=0.28; RO=0.34; D=0.08
    for z in (0, D):
        for s in range(SEGS):
            a=(s/SEGS)*math.tau
            bm.verts.new(Vector((math.cos(a)*RI+OFFSET[0], math.sin(a)*RI+OFFSET[1], z+OFFSET[2])))
            bm.verts.new(Vector((math.cos(a)*RO+OFFSET[0], math.sin(a)*RO+OFFSET[1], z+OFFSET[2])))
    bm.verts.ensure_lookup_table()
    n4=SEGS*2
    for s in range(SEGS):
        s1=(s+1)%SEGS
        bi=s*2; bi1=s1*2; bo=s*2+1; bo1=s1*2+1
        ti=n4+s*2; ti1=n4+s1*2; to_=n4+s*2+1; to1=n4+s1*2+1
        bm.faces.new([bm.verts[bi],bm.verts[bi1],bm.verts[bo1],bm.verts[bo]])
        bm.faces.new([bm.verts[ti],bm.verts[ti1],bm.verts[to1],bm.verts[to_]])
        bm.faces.new([bm.verts[bo],bm.verts[bo1],bm.verts[to1],bm.verts[to_]])
        bm.faces.new([bm.verts[bi1],bm.verts[bi],bm.verts[ti],bm.verts[ti1]])
    bm.normal_update()
    prop_rim = new_obj('Compass_Prop_Rim', bm)
    assign(prop_rim, mats['brass']); smart_uv(prop_rim); objs.append(prop_rim)

    # Face
    bm2=bmesh.new()
    fc=bm2.verts.new(Vector((OFFSET[0],OFFSET[1],D+0.005+OFFSET[2])))
    fring=[bm2.verts.new(Vector((math.cos((s/SEGS)*math.tau)*0.275+OFFSET[0],
                                  math.sin((s/SEGS)*math.tau)*0.275+OFFSET[1],
                                  D+0.005+OFFSET[2])))
           for s in range(SEGS)]
    for s in range(SEGS):
        bm2.faces.new([fc,fring[(s+1)%SEGS],fring[s]])
    bm2.normal_update()
    prop_face = new_obj('Compass_Prop_Face', bm2)
    assign(prop_face,mats['compass_face']); smart_uv(prop_face); objs.append(prop_face)

    # Top ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.028, minor_radius=0.008,
        major_segments=16, minor_segments=8,
        location=(OFFSET[0], OFFSET[1], D+0.045+OFFSET[2]))
    top_r=bpy.context.active_object; top_r.name='Compass_Prop_Ring'
    assign(top_r, mats['brass']); objs.append(top_r)

    return objs


# ═══════════════════════════════════════════════════════
#  SCENE ORGANISATION
# ═══════════════════════════════════════════════════════

def organise(all_objs):
    col = bpy.data.collections.new('IsleTrial_CompassNPC')
    bpy.context.scene.collection.children.link(col)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    root = bpy.context.active_object; root.name = 'CompassNPC_ROOT'
    for obj in all_objs:
        for c in list(obj.users_collection): c.objects.unlink(obj)
        col.objects.link(obj)
        if obj.parent is None and obj != root: obj.parent = root
    for c in list(root.users_collection): c.objects.unlink(root)
    col.objects.link(root)
    for obj in all_objs:
        if obj.type in ('MESH','CURVE'):
            activate(obj)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
            apply_all(obj)
    return root


def print_report(all_objs):
    print("\n" + "="*62)
    print("  IsleTrial — Compass NPC Build Report")
    print("="*62)
    for obj in all_objs:
        p = obj.location
        vc = len(obj.data.vertices) if hasattr(obj.data,'vertices') else '-'
        print(f"  {obj.name:<30} verts={str(vc):<6}  ({p.x:+.2f},{p.y:+.2f},{p.z:+.2f})")
    print(f"\n  Total objects : {len(all_objs)}")
    print("  Collection    : IsleTrial_CompassNPC")
    print("  Select CompassNPC_ROOT → File → Export → FBX")
    print("  Unity Scale Factor: 1.0")
    print("="*62 + "\n")


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

def main():
    clear_scene()
    random.seed(1)

    print("[CompassNPC] Building materials...")
    mats = {
        'brass'       : mat_brass(),
        'compass_face': mat_compass_face(),
        'needle_red'  : mat_needle_red(),
        'needle_blue' : mat_needle_blue(),
        'eye_angry'   : mat_eye_angry(),
        'eye_shine'   : mat_eye_shine(),
        'hat'         : mat_leather('Mat_Hat',        '5A3A18', roughness=0.82),
        'belt'        : mat_leather('Mat_Belt',       '4A2A10', roughness=0.72),
        'backpack'    : mat_leather('Mat_Backpack',   '6A4020', roughness=0.78),
        'boot'        : mat_leather('Mat_Boot',       '2E1808', roughness=0.80),
        'jacket'      : mat_jacket(),
        'potion'      : mat_potion(),
        'torch_wood'  : mat_torch_wood(),
        'flame'       : mat_flame(),
        'blade'       : mat_metal_blade(),
        'scroll'      : mat_scroll(),
    }

    print("[CompassNPC] Building geometry...")
    rim      = build_compass_rim(mats)
    face     = build_compass_face(mats)
    rose     = build_compass_rose(mats)
    needles  = build_needles(mats)
    eyes     = build_angry_eyes(mats)
    beak     = build_beak(mats)
    hat      = build_hat(mats)
    body     = build_body(mats)
    arms     = build_arms(mats)
    hands    = build_hands(mats)
    belt_objs = build_belt_and_pouches(mats)
    potions  = build_potion_bottles(mats)
    torch_objs = build_torch(mats)
    knife_objs = build_knife(mats)
    legs_boots = build_legs_boots(mats)
    backpack = build_backpack(mats)
    scroll   = build_scroll(mats)
    prop_compass = build_standalone_compass(mats)

    all_objs = ([rim, face, rose, beak, hat, body, backpack, scroll]
                + needles + eyes + arms + hands
                + belt_objs + potions + torch_objs + knife_objs
                + legs_boots + prop_compass)

    print("[CompassNPC] Organising scene...")
    root = organise(all_objs)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
            break

    print_report(all_objs)


main()
