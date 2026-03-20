"""
IsleTrial — Blender 4.x Python Script
Script 32: Mystery Isle — The Forgotten Island  [FULL QUALITY REBUILD]
=======================================================================
Objects created (35 total):
  MysteryIsle_Terrain             — 52×52 brooding dark hills
  MysteryIsle_BeachSand           — dark sand ring
  MysteryStatue_Torso             — giant faceless statue torso, eroded
  MysteryStatue_Head              — smooth faceless head with hollow eyes
  MysteryStatue_EyeSocket_L/R     — glowing purple eye sockets
  MysteryStatue_Arm_Buried        — buried arm cylinder
  MysteryStatue_Hand              — hand emerging from ground
  MysteryIsle_Ring1_Stone_01..32  — outer ring standing stones
  MysteryIsle_Ring2_Stone_01..20  — middle ring
  MysteryIsle_Ring3_Stone_01..12  — inner ring
  MysteryIsle_RuneStone_01..12    — scattered glowing rune stones
  MysteryAltar_Tier1/2/3          — 3-tier altar platform
  MysteryAltar_Basin              — glowing carved basin
  MysteryAltar_Pillar_01..04      — altar surrounding pillars
  MysteryIsle_PathStone_*         — ancient stone path pieces
  MysteryIsle_Tree_01..10_Trunk   — twisted dead trees (with branches)
  MysteryIsle_FogPlane_01..05     — translucent fog patches

Dual-path PBR + [UNITY] image slots + smart UV on all meshes.
Run in Blender 4.x: Scripting tab → Run Script (Alt+P)
"""

import bpy, bmesh, math, random
from mathutils import Vector

rng = random.Random(131300)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
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

def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def smart_uv(obj, angle=60):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=angle, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)

def ns_lk(mat):
    mat.use_nodes = True
    return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, label, x, y):
    n = ns.new('ShaderNodeTexImage')
    n.label = n.name = label; n.location = (x, y)
    return n

# ─────────────────────────────────────────────────────────────────────────────
# MATERIAL BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def build_dark_moss_mat():
    """Brooding dark grass/moss — Wave + Noise, desaturated greens."""
    mat = bpy.data.materials.new("Mat_Mystery_DarkMoss")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (950, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Subsurface Weight'].default_value = 0.04
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-600, 150)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value      = 4.0
    wave.inputs['Distortion'].default_value = 8.0
    wave.inputs['Detail'].default_value     = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-300, 150)
    cr.color_ramp.elements[0].color = (0.06, 0.10, 0.05, 1)
    cr.color_ramp.elements[1].color = (0.18, 0.28, 0.10, 1)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-600, -100)
    noise.inputs['Scale'].default_value  = 22.0
    noise.inputs['Detail'].default_value = 8.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-300, -100)
    cr2.color_ramp.elements[0].color = (0.04, 0.08, 0.03, 1)
    cr2.color_ramp.elements[1].color = (0.20, 0.30, 0.12, 1)
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'DARKEN'
    mix.location = (0, 50); mix.inputs['Fac'].default_value = 0.6
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (400, 200)
    bmp.inputs['Strength'].default_value = 0.7
    img_a = img_slot(ns, "[UNITY] Mystery_Moss_Albedo", -640, -350)
    img_n = img_slot(ns, "[UNITY] Mystery_Moss_Normal", -640, -550)
    fmix  = ns.new('ShaderNodeMixRGB'); fmix.location = (500, 0)
    fmix.inputs['Fac'].default_value = 0.0
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(noise.outputs['Fac'],   cr2.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   fmix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], fmix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(fmix.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_dark_sand_mat():
    """Shore dark sand, coarse grain noise."""
    mat = bpy.data.materials.new("Mat_Mystery_DarkSand")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Roughness'].default_value = 0.93
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-450, 150)
    noise.inputs['Scale'].default_value  = 50.0
    noise.inputs['Detail'].default_value = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-150, 150)
    cr.color_ramp.elements[0].color = (0.22, 0.18, 0.14, 1)
    cr.color_ramp.elements[1].color = (0.38, 0.32, 0.25, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (250, 200)
    bmp.inputs['Strength'].default_value = 0.25
    img_a = img_slot(ns, "[UNITY] Mystery_Sand_Albedo", -500, -300)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (350, 0)
    mix.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_ancient_stone_mat():
    """Ancient worn stone — Musgrave-heavy, deep crevice darks."""
    mat = bpy.data.materials.new("Mat_Mystery_AncientStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (950, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Roughness'].default_value = 0.88
    mus  = ns.new('ShaderNodeTexMusgrave'); mus.location = (-600, 200)
    mus.musgrave_type = 'HYBRID_MULTIFRACTAL'
    mus.inputs['Scale'].default_value   = 9.0
    mus.inputs['Detail'].default_value  = 12.0
    mus.inputs['Dimension'].default_value = 0.9
    cr1  = ns.new('ShaderNodeValToRGB'); cr1.location = (-300, 200)
    cr1.color_ramp.elements[0].color = (0.08, 0.07, 0.08, 1)
    cr1.color_ramp.elements[1].color = (0.30, 0.28, 0.32, 1)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-600, -50)
    noise.inputs['Scale'].default_value  = 42.0
    noise.inputs['Detail'].default_value = 5.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-300, -50)
    cr2.color_ramp.elements[0].color = (0.18, 0.16, 0.20, 1)
    cr2.color_ramp.elements[1].color = (0.36, 0.33, 0.38, 1)
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'
    mix.location = (0, 100); mix.inputs['Fac'].default_value = 0.75
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (400, 250)
    bmp.inputs['Strength'].default_value = 1.8
    bmp.inputs['Distance'].default_value = 0.04
    img_a = img_slot(ns, "[UNITY] AncientStone_Albedo", -640, -350)
    img_n = img_slot(ns, "[UNITY] AncientStone_Normal", -640, -550)
    fmix  = ns.new('ShaderNodeMixRGB'); fmix.location = (500, 0)
    fmix.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr1.inputs['Fac'])
    lk.new(noise.outputs['Fac'],   cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   fmix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], fmix.inputs['Color2'])
    lk.new(mus.outputs['Fac'],     bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(fmix.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_rune_glow_mat():
    """Glowing carved runes — green-teal emission pulse."""
    mat = bpy.data.materials.new("Mat_Mystery_RuneGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Base Color'].default_value = (0.15, 0.45, 0.30, 1)
    bsdf.inputs['Roughness'].default_value  = 0.35
    emit = ns.new('ShaderNodeEmission'); emit.location = (250, 200)
    emit.inputs['Color'].default_value    = (0.15, 0.85, 0.45, 1)
    emit.inputs['Strength'].default_value = 4.5
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-400, 200)
    noise.inputs['Scale'].default_value  = 15.0
    noise.inputs['Detail'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-100, 200)
    cr.color_ramp.elements[0].position = 0.45; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.7;  cr.color_ramp.elements[1].color = (1,1,1,1)
    mix_s= ns.new('ShaderNodeMixShader'); mix_s.location = (730, 100)
    img_a = img_slot(ns, "[UNITY] Rune_Albedo",   -450, -300)
    img_e = img_slot(ns, "[UNITY] Rune_Emission", -450, -500)
    lk.new(noise.outputs['Fac'],       cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],        mix_s.inputs['Fac'])
    lk.new(bsdf.outputs['BSDF'],       mix_s.inputs[1])
    lk.new(emit.outputs['Emission'],   mix_s.inputs[2])
    lk.new(mix_s.outputs['Shader'],    out.inputs['Surface'])
    return mat

def build_altar_stone_mat():
    """Altar — dark purple-veined stone, slight sheen."""
    mat = bpy.data.materials.new("Mat_Mystery_AltarStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (650, 0)
    bsdf.inputs['Roughness'].default_value = 0.72
    bsdf.inputs['Metallic'].default_value  = 0.05
    mus  = ns.new('ShaderNodeTexMusgrave'); mus.location = (-550, 150)
    mus.inputs['Scale'].default_value  = 12.0
    mus.inputs['Detail'].default_value = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-250, 150)
    cr.color_ramp.elements[0].color = (0.06, 0.04, 0.09, 1)
    cr.color_ramp.elements[1].color = (0.22, 0.16, 0.30, 1)
    # Vein detail
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-550, -100)
    noise.inputs['Scale'].default_value = 55.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-250, -100)
    cr2.color_ramp.elements[0].position = 0.78; cr2.color_ramp.elements[0].color = (0.3, 0.1, 0.5, 1)
    cr2.color_ramp.elements[1].position = 0.9;  cr2.color_ramp.elements[1].color = (0, 0, 0, 1)
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'ADD'
    mix.location = (20, 50); mix.inputs['Fac'].default_value = 0.4
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (400, 200)
    bmp.inputs['Strength'].default_value = 1.2
    img_a = img_slot(ns, "[UNITY] Altar_Albedo", -600, -350)
    lk.new(mus.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(noise.outputs['Fac'],  cr2.inputs['Fac'])
    lk.new(cr.outputs['Color'],   mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],  mix.inputs['Color2'])
    lk.new(mus.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def build_altar_glow_mat():
    """Altar basin — strong purple emission."""
    mat = bpy.data.materials.new("Mat_Mystery_AltarGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (700, 0)
    emit = ns.new('ShaderNodeEmission'); emit.location = (400, 0)
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-300, 100)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value      = 2.5
    wave.inputs['Distortion'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-50, 100)
    cr.color_ramp.elements[0].color = (0.35, 0.02, 0.65, 1)
    cr.color_ramp.elements[1].color = (0.7,  0.05, 1.0,  1)
    lk.new(wave.outputs['Fac'],        cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],        emit.inputs['Color'])
    emit.inputs['Strength'].default_value = 7.0
    lk.new(emit.outputs['Emission'],   out.inputs['Surface'])
    return mat

def build_statue_stone_mat():
    """Statue — worn grey stone, no features."""
    mat = bpy.data.materials.new("Mat_Mystery_StatueStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (850, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (600, 0)
    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Subsurface Weight'].default_value = 0.03
    mus  = ns.new('ShaderNodeTexMusgrave'); mus.location = (-500, 150)
    mus.inputs['Scale'].default_value = 7.0; mus.inputs['Detail'].default_value = 8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-200, 150)
    cr.color_ramp.elements[0].color = (0.12, 0.11, 0.14, 1)
    cr.color_ramp.elements[1].color = (0.32, 0.30, 0.34, 1)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-500, -100)
    noise.inputs['Scale'].default_value = 30.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (300, 200)
    bmp.inputs['Strength'].default_value = 0.9
    img_a = img_slot(ns, "[UNITY] Statue_Albedo", -550, -350)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (400, 0); mix.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],   mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],  bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def build_statue_eye_mat():
    """Glowing hollow eye sockets — deep purple void."""
    mat = bpy.data.materials.new("Mat_Mystery_StatueEyes")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (650, 0)
    emit = ns.new('ShaderNodeEmission'); emit.location = (400, 0)
    emit.inputs['Color'].default_value    = (0.45, 0.0, 0.85, 1)
    emit.inputs['Strength'].default_value = 9.0
    lk.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

def build_wet_stone_mat():
    """Wet dark stone paths."""
    mat = bpy.data.materials.new("Mat_Mystery_WetStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Base Color'].default_value = (0.10, 0.10, 0.12, 1)
    bsdf.inputs['Roughness'].default_value  = 0.42
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 20.0; noise.inputs['Detail'].default_value = 6.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (250, 200)
    bmp.inputs['Strength'].default_value = 0.6
    img_a = img_slot(ns, "[UNITY] WetStone_Albedo", -450, -300)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (350, 0); mix.inputs['Fac'].default_value = 0.0
    mix.inputs['Color1'].default_value = (0.10, 0.10, 0.12, 1)
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_dead_tree_mat():
    """Dead twisted trees — dark, wet, mossy."""
    mat = bpy.data.materials.new("Mat_Mystery_DeadTree")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (850, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (600, 0)
    bsdf.inputs['Roughness'].default_value = 0.93
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-500, 100)
    wave.wave_type = 'RINGS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 10.0; wave.inputs['Distortion'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-200, 100)
    cr.color_ramp.elements[0].color = (0.04, 0.05, 0.03, 1)
    cr.color_ramp.elements[1].color = (0.12, 0.14, 0.09, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (300, 200)
    bmp.inputs['Strength'].default_value = 1.1
    img_a = img_slot(ns, "[UNITY] DeadTree_Albedo", -550, -300)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (420, 0); mix.inputs['Fac'].default_value = 0.0
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_fog_mat():
    """Translucent fog patch — soft grey alpha."""
    mat = bpy.data.materials.new("Mat_Mystery_Fog")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (700, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 0)
    bsdf.inputs['Base Color'].default_value  = (0.72, 0.74, 0.78, 1)
    bsdf.inputs['Roughness'].default_value   = 1.0
    bsdf.inputs['Alpha'].default_value       = 0.12
    bsdf.inputs['Subsurface Weight'].default_value = 0.6
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

print("[MysteryIsle] All materials built.")

# ─────────────────────────────────────────────────────────────────────────────
# GEOMETRY BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def build_mystery_terrain(name, size=90.0, grid=52):
    """Brooding uneven hills, hidden valleys, oppressive silhouette."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    for gi in range(grid + 1):
        for gj in range(grid + 1):
            x = (gi / grid - 0.5) * size
            y = (gj / grid - 0.5) * size
            nx, ny = x / (size * 0.5), y / (size * 0.5)
            dist = math.sqrt(nx*nx + ny*ny)
            # Central flat-topped hill
            hill = max(0.0, 1.0 - dist * 1.18) ** 1.25 * 12.5
            plateau = -max(0.0, 1.0 - dist * 5.5) * 2.2
            # Secondary hills creating hidden valleys
            h2 = max(0.0, 1.0 - math.sqrt((nx-0.48)**2+(ny-0.28)**2)*2.6)**2 * 7.5
            h3 = max(0.0, 1.0 - math.sqrt((nx+0.42)**2+(ny-0.38)**2)*3.2)**2 * 5.8
            h4 = max(0.0, 1.0 - math.sqrt((nx-0.18)**2+(ny+0.52)**2)*2.9)**2 * 6.2
            # Hollow passages between hills
            hollow = -abs(math.sin(nx*3.8+0.3)*math.cos(ny*3.2))*0.9*max(0, 1-dist)
            # Shore ring
            shore = max(0.0, 0.65 - max(0.0, dist - 0.76)*3.5)
            # Multi-octave surface noise
            n  = (math.sin(nx*11.0+ny*9.0)*0.38 +
                  math.sin(nx*19.0-ny*15.5)*0.20 +
                  math.sin(nx*7.0+ny*21.0)*0.16)
            z = hill + plateau + h2 + h3 + h4 + hollow + shore + n * 0.65
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for gi in range(grid):
        for gj in range(grid):
            a = gi * (grid + 1) + gj
            try:
                bm.faces.new([bm.verts[a], bm.verts[a+1],
                               bm.verts[a+grid+2], bm.verts[a+grid+1]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    sub = ob.modifiers.new("Subd", 'SUBSURF'); sub.levels = 2
    disp = ob.modifiers.new("MysteryNoise", 'DISPLACE')
    tex = bpy.data.textures.new("MystNoiseT", type='MUSGRAVE')
    tex.musgrave_type = 'HYBRID_MULTIFRACTAL'
    tex.noise_scale = 5.0; tex.noise_intensity = 0.85
    disp.texture = tex; disp.strength = 0.75; disp.texture_coords = 'LOCAL'
    return ob

def build_statue_torso(name, loc):
    """Massive eroded stone torso, narrowed at shoulders."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    nx, nz = 10, 16
    for zi in range(nz + 1):
        t = zi / nz
        z = t * 10.0
        # Body profile: wide base tapering to shoulders at top
        w = 4.5 * (1.0 - t * 0.25)
        d = 2.8 * (1.0 - t * 0.2)
        for xi in range(nx + 1):
            u = xi / nx
            x = (u - 0.5) * 2 * w
            for side in range(4):
                pass  # simplified to box
        # 4 corners per height
        for cx, cy in [(-w,-d),(w,-d),(w,d),(-w,d)]:
            # erosion on surface
            ox = math.sin(t * 3.5 + cx * 0.4) * 0.12
            oy = math.sin(t * 2.8 + cy * 0.3) * 0.10
            bm.verts.new((cx + ox, cy + oy, z))
    bm.verts.ensure_lookup_table()
    n_rings = nz + 1; per_ring = 4
    for zi in range(nz):
        for ci in range(per_ring):
            a = zi * per_ring + ci
            b = zi * per_ring + (ci + 1) % per_ring
            c = (zi + 1) * per_ring + (ci + 1) % per_ring
            d = (zi + 1) * per_ring + ci
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    # top and bottom caps
    for cap_ring in [0, nz]:
        cap_verts = [bm.verts[cap_ring * per_ring + ci] for ci in range(per_ring)]
        if cap_ring == 0:
            cap_verts = cap_verts[::-1]
        try: bm.faces.new(cap_verts)
        except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    sub = ob.modifiers.new("TorsoSubd", 'SUBSURF'); sub.levels = 2
    disp = ob.modifiers.new("TorsoErosion", 'DISPLACE')
    tex = bpy.data.textures.new("TorsoErosionT", type='MUSGRAVE')
    tex.noise_scale = 2.5; tex.noise_intensity = 0.9
    disp.texture = tex; disp.strength = 0.22; disp.texture_coords = 'LOCAL'
    return ob

def build_standing_stone(name, loc, height=4.0, width=0.42, depth=0.25, lean_x=0.0):
    """Single standing ritual stone, rectangular cross-section."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 14
    for si in range(segs + 1):
        t = si / segs
        z = t * height
        # Slight narrowing at top
        scale_t = 1.0 - t * 0.12
        hw = width * 0.5 * scale_t
        hd = depth * 0.5 * scale_t
        offset_x = lean_x * t
        for cx, cy in [(-hw,-hd),(hw,-hd),(hw,hd),(-hw,hd)]:
            noise_x = math.sin(z * 3.5 + cx * 8) * 0.012
            noise_y = math.sin(z * 2.8 + cy * 6) * 0.010
            bm.verts.new((cx + offset_x + noise_x, cy + noise_y, z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for ci in range(4):
            a = si * 4 + ci; b = si * 4 + (ci+1) % 4
            c = (si+1) * 4 + (ci+1) % 4; d = (si+1) * 4 + ci
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    # caps
    bot = [bm.verts[v] for v in range(4)][::-1]
    top = [bm.verts[segs*4 + v] for v in range(4)]
    try: bm.faces.new(bot)
    except: pass
    try: bm.faces.new(top)
    except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_rune_stone(name, loc, height=2.0):
    """Tall flat rune stone slab."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    w, d, segs = 0.45, 0.22, 16
    for si in range(segs + 1):
        t = si / segs; z = t * height
        scale_t = 1.0 - t * 0.08
        hw = w * 0.5 * scale_t; hd = d * 0.5
        for cx, cy in [(-hw,-hd),(hw,-hd),(hw,hd),(-hw,hd)]:
            bm.verts.new((cx + math.sin(z*2.5)*0.015, cy, z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for ci in range(4):
            a = si*4+ci; b = si*4+(ci+1)%4
            c = (si+1)*4+(ci+1)%4; d = (si+1)*4+ci
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    try: bm.faces.new([bm.verts[v] for v in range(4)][::-1])
    except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler.z = rng.uniform(0, math.pi*2)
    ob.name = ob.data.name = name
    return ob

def build_altar_tier(name, loc, radius, height, segs=8):
    """Octagonal altar tier."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    rings = 6
    for ri in range(rings + 1):
        t = ri / rings; z = t * height
        r = radius * (1.0 + math.sin(t * math.pi) * 0.04)
        for vi in range(segs):
            a = vi / segs * math.pi * 2 + math.pi / segs
            r_carved = r * (1.0 + math.sin(a * segs * 0.5) * 0.02)
            bm.verts.new((r_carved * math.cos(a), r_carved * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for ri in range(rings):
        for vi in range(segs):
            a = ri * segs + vi; b = ri * segs + (vi+1) % segs
            c = (ri+1) * segs + (vi+1) % segs; d = (ri+1) * segs + vi
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    # Top cap
    top = [bm.verts[rings * segs + v] for v in range(segs)]
    try: bm.faces.new(top)
    except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_altar_basin(name, loc):
    """Bowl-shaped glowing basin on altar top."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    rim_segs = 20; depth_segs = 8; rim_r = 0.85; depth = 0.35
    # Rim ring
    for i in range(rim_segs):
        a = i / rim_segs * math.pi * 2
        bm.verts.new((rim_r * math.cos(a), rim_r * math.sin(a), 0))
    # Depth rings
    for di in range(1, depth_segs + 1):
        t = di / depth_segs
        r = rim_r * (1.0 - t * 0.7)
        z = -depth * math.sin(t * math.pi * 0.5)
        for i in range(rim_segs):
            a = i / rim_segs * math.pi * 2
            bm.verts.new((r * math.cos(a), r * math.sin(a), z))
    center = bm.verts.new((0, 0, -depth))
    bm.verts.ensure_lookup_table()
    for di in range(depth_segs):
        for i in range(rim_segs):
            a = di * rim_segs + i; b = di * rim_segs + (i+1) % rim_segs
            c = (di+1) * rim_segs + (i+1) % rim_segs; d = (di+1) * rim_segs + i
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    # Bottom fan to center
    base = depth_segs * rim_segs
    for i in range(rim_segs):
        try:
            bm.faces.new([bm.verts[base+i], bm.verts[base+(i+1)%rim_segs], center])
        except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_twisted_trunk(name, loc, height=5.0, lean=(0.2, 0.1)):
    """Twisted dead tree trunk with organic lean."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides = 7; segs = 22
    for si in range(segs + 1):
        t = si / segs; z = t * height
        r = (0.16 + (1.0-t)*0.1) * rng.uniform(0.88, 1.12)
        twist = t * math.pi * 0.7
        lx = math.sin(t * math.pi * 1.4) * lean[0] * height * 0.5
        ly = math.sin(t * math.pi * 1.1) * lean[1] * height * 0.5
        for vi in range(sides):
            a = vi / sides * math.pi * 2 + twist
            bm.verts.new((lx + r * math.cos(a), ly + r * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si*sides+vi; b = si*sides+(vi+1)%sides
            c = (si+1)*sides+(vi+1)%sides; d = (si+1)*sides+vi
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_fog_plane(name, loc, size=22.0):
    """Low translucent fog plane."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    n = 8
    for j in range(n+1):
        for i in range(n+1):
            x = (i/n - 0.5) * size * rng.uniform(0.8, 1.2)
            y = (j/n - 0.5) * size * rng.uniform(0.8, 1.2)
            z = rng.uniform(-0.05, 0.05)
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for j in range(n):
        for i in range(n):
            a = j*(n+1)+i
            try:
                bm.faces.new([bm.verts[a],bm.verts[a+1],
                               bm.verts[a+n+2],bm.verts[a+n+1]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (rng.uniform(-0.04,0.04), rng.uniform(-0.04,0.04),
                          rng.uniform(0, math.pi))
    ob.name = ob.data.name = name
    return ob

# ─────────────────────────────────────────────────────────────────────────────
# SCENE ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────
clear_scene()
rng = random.Random(131300)

col_root   = new_col("IsleTrial_MysteryIsle")
col_terr   = new_col("MysteryIsle_Terrain")
col_statue = new_col("MysteryIsle_AncientStatue")
col_rings  = new_col("MysteryIsle_StoneRings")
col_runes  = new_col("MysteryIsle_RuneStones")
col_altar  = new_col("MysteryIsle_Altar")
col_path   = new_col("MysteryIsle_PathStones")
col_trees  = new_col("MysteryIsle_DeadTrees")
col_fog    = new_col("MysteryIsle_Fog")
col_lights = new_col("MysteryIsle_Lighting")

mat_moss    = build_dark_moss_mat()
mat_sand    = build_dark_sand_mat()
mat_stone   = build_ancient_stone_mat()
mat_rune    = build_rune_glow_mat()
mat_altar_s = build_altar_stone_mat()
mat_altar_g = build_altar_glow_mat()
mat_statue  = build_statue_stone_mat()
mat_eye     = build_statue_eye_mat()
mat_wet     = build_wet_stone_mat()
mat_tree    = build_dead_tree_mat()
mat_fog     = build_fog_mat()

# ── 1. TERRAIN ─────────────────────────────────────────────────────────────────
terrain = build_mystery_terrain("MysteryIsle_Terrain")
assign_mat(terrain, mat_moss)
smart_uv(terrain, angle=45)
link(col_terr, terrain)

# Beach sand ring (separate plane slightly above terrain edge)
sand = build_fog_plane("MysteryIsle_BeachSand", (0, 0, 0.04), size=90)
assign_mat(sand, mat_sand); smart_uv(sand)
link(col_terr, sand)
print("[MysteryIsle] Terrain created.")

# ── 2. THE GREAT FACELESS STATUE ─────────────────────────────────────────────
torso = build_statue_torso("MysteryStatue_Torso", (0, 38, 0))
assign_mat(torso, mat_statue); smart_uv(torso)
link(col_statue, torso)

# Head — smooth sphere, scaled
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=18,
                                      radius=2.8, location=(0, 38, 14.8))
head = bpy.context.active_object; head.name = "MysteryStatue_Head"
head.scale = (1.0, 0.85, 1.15)
bm = bmesh.new(); bm.from_mesh(head.data)
for v in bm.verts:
    # Smooth eroded face side
    if v.co.y < 0:
        v.co.x *= 0.93; v.co.z *= 0.94
    # Ancient surface worn bumps
    a = math.atan2(v.co.x, v.co.z)
    v.co.x += math.sin(a * 6 + v.co.y * 1.5) * 0.05
    v.co.z += math.cos(a * 5 + v.co.x * 1.2) * 0.04
bm.to_mesh(head.data); bm.free()
assign_mat(head, mat_statue); smart_uv(head)
link(col_statue, head)

# Eye sockets
for side, label in [(-1, 'L'), (1, 'R')]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8,
                                          radius=0.46, location=(side*0.9, 35.7, 15.2))
    eye = bpy.context.active_object; eye.name = f"MysteryStatue_EyeSocket_{label}"
    eye.scale = (1.0, 0.5, 0.88)
    assign_mat(eye, mat_eye); smart_uv(eye)
    link(col_statue, eye)
    # Glow light
    el = bpy.data.lights.new(f"StatueEye_{label}_Light", type='POINT')
    el.energy = 700; el.color = (0.45, 0.0, 0.9); el.shadow_soft_size = 0.3
    elo = bpy.data.objects.new(f"StatueEye_{label}_Light", el)
    elo.location = (side*0.9, 36.2, 15.2); bpy.context.scene.collection.objects.link(elo)
    link(col_statue, elo)

# Buried arm cylinder
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.2, depth=8.0, location=(-6, 34, -1))
arm = bpy.context.active_object; arm.name = "MysteryStatue_Arm_Buried"
arm.rotation_euler = (math.radians(30), 0, math.radians(25))
assign_mat(arm, mat_statue); smart_uv(arm)
link(col_statue, arm)

# Hand emerging from ground
bpy.ops.mesh.primitive_cube_add(size=1, location=(-9, 30, 0.3))
hand = bpy.context.active_object; hand.name = "MysteryStatue_Hand"
hand.scale = (2.4, 1.4, 0.42)
bm = bmesh.new(); bm.from_mesh(hand.data)
for v in bm.verts:
    v.co.x += math.sin(v.co.y*3+v.co.z*4)*0.1
bm.to_mesh(hand.data); bm.free()
assign_mat(hand, mat_statue); smart_uv(hand)
link(col_statue, hand)
print("[MysteryIsle] Great Faceless Statue created.")

# ── 3. THREE STONE RINGS ──────────────────────────────────────────────────────
ring_configs = [
    (18.5, 32, mat_stone, "Ring1"),
    ( 9.5, 20, mat_stone, "Ring2"),
    ( 4.2, 12, mat_stone, "Ring3"),
]
for ring_r, ring_count, mat_r, ring_prefix in ring_configs:
    for si in range(ring_count):
        angle = si / ring_count * math.pi * 2
        sx = math.cos(angle) * ring_r
        sy = math.sin(angle) * ring_r
        sz = 11.5  # on hill top
        stone_h = 4.2 + rng.uniform(-0.8, 2.0)
        buried   = rng.uniform(0.3, 1.0)
        stone = build_standing_stone(
            f"MysteryIsle_{ring_prefix}_Stone_{si+1:02d}",
            (sx, sy, sz + (stone_h - buried) * 0.5 - 0.3),
            height=stone_h + buried,
            width=0.42 + rng.uniform(-0.08, 0.12),
            depth=0.24 + rng.uniform(-0.04, 0.08),
            lean_x=rng.uniform(-0.06, 0.06)
        )
        stone.rotation_euler = (rng.uniform(-0.06, 0.06),
                                  rng.uniform(-0.06, 0.06),
                                  angle + rng.uniform(-0.15, 0.15))
        assign_mat(stone, mat_r); smart_uv(stone)
        link(col_rings, stone)

total_ring_stones = sum(c[1] for c in ring_configs)
print(f"[MysteryIsle] {total_ring_stones} standing stones across 3 rings.")

# ── 4. RUNE STONES ────────────────────────────────────────────────────────────
rune_positions = [
    (14,8,5),(-12,14,6),(20,-5,3),(-18,-10,4),
    (8,-18,2),(-6,22,7),(22,16,4),(-20,5,5),
    (10,25,6),(-25,-6,3),(16,-20,2),(-8,-28,1)
]
for i,(px,py,pz) in enumerate(rune_positions):
    rs = build_rune_stone(f"MysteryIsle_RuneStone_{i+1:02d}",
                            (px, py, pz + 0.9),
                            height=1.8 + rng.uniform(-0.3, 1.2))
    assign_mat(rs, mat_stone); rs.data.materials.append(mat_rune)
    smart_uv(rs)
    link(col_runes, rs)
    # Glow light
    rl = bpy.data.lights.new(f"RuneStone_{i+1:02d}_Light", type='POINT')
    rl.energy = 140; rl.color = (0.15, 0.9, 0.45); rl.shadow_soft_size = 0.5
    rlo = bpy.data.objects.new(f"RuneStone_{i+1:02d}_Light", rl)
    rlo.location = (px, py, pz + 3.0); bpy.context.scene.collection.objects.link(rlo)
    link(col_runes, rlo)
print(f"[MysteryIsle] {len(rune_positions)} rune stones placed.")

# ── 5. CENTRAL ALTAR ──────────────────────────────────────────────────────────
altar_z = 11.5
t1 = build_altar_tier("MysteryAltar_Tier1", (0, 0, altar_z), 5.2, 0.75)
assign_mat(t1, mat_altar_s); smart_uv(t1); link(col_altar, t1)

t2 = build_altar_tier("MysteryAltar_Tier2", (0, 0, altar_z + 0.75), 3.1, 0.65)
assign_mat(t2, mat_altar_s); smart_uv(t2); link(col_altar, t2)

t3 = build_altar_tier("MysteryAltar_Tier3", (0, 0, altar_z + 1.4), 1.6, 0.55)
assign_mat(t3, mat_altar_s); smart_uv(t3); link(col_altar, t3)

basin = build_altar_basin("MysteryAltar_Basin", (0, 0, altar_z + 2.1))
assign_mat(basin, mat_altar_g); smart_uv(basin); link(col_altar, basin)

altar_light = bpy.data.lights.new("MysteryAltar_GlowLight", type='POINT')
altar_light.energy = 2500; altar_light.color = (0.5, 0.05, 0.95)
altar_light.shadow_soft_size = 1.8
alo = bpy.data.objects.new("MysteryAltar_GlowLight", altar_light)
alo.location = (0, 0, altar_z + 4.0); bpy.context.scene.collection.objects.link(alo)
link(col_altar, alo)

# 4 altar pillars
for pi_i in range(4):
    pa = pi_i / 4 * math.pi * 2 + math.pi * 0.25
    px2 = math.cos(pa) * 1.3; py2 = math.sin(pa) * 1.3
    pil = build_standing_stone(f"MysteryAltar_Pillar_{pi_i+1:02d}",
                                 (px2, py2, altar_z + 1.95),
                                 height=2.8, width=0.11, depth=0.11)
    assign_mat(pil, mat_stone); smart_uv(pil); link(col_altar, pil)
print("[MysteryIsle] Central altar created.")

# ── 6. STONE PATH TO ALTAR ────────────────────────────────────────────────────
path_pts = [(0,-34,0.2),(3,-27,1.5),(-2,-20,3.5),(4,-12,6.5),(-1,-5,9.0),(0,0,11.0)]
for seg in range(len(path_pts)-1):
    p1, p2 = path_pts[seg], path_pts[seg+1]
    for t in [0.15, 0.40, 0.65, 0.88]:
        px3 = p1[0] + (p2[0]-p1[0])*t + rng.uniform(-1.5, 1.5)
        py3 = p1[1] + (p2[1]-p1[1])*t + rng.uniform(-1.0, 1.0)
        pz3 = p1[2] + (p2[2]-p1[2])*t
        ps = build_standing_stone(
            f"MysteryIsle_PathStone_{seg}_{int(t*100)}",
            (px3, py3, pz3 + 0.06),
            height=0.16, width=1.3+rng.uniform(-0.2,0.6), depth=0.9+rng.uniform(-0.1,0.4)
        )
        ps.rotation_euler.z = rng.uniform(-0.4, 0.4)
        assign_mat(ps, mat_wet); smart_uv(ps); link(col_path, ps)

# ── 7. TWISTED DEAD TREES ─────────────────────────────────────────────────────
tree_spots = [(18,10),(-14,16),(22,-8),(-20,-14),(10,-22),
               (-8,25),(24,18),(-26,8),(12,28),(-10,-26)]
for i, (tx, ty) in enumerate(tree_spots):
    tz = 3.5 + rng.uniform(0, 4.5)
    trunk = build_twisted_trunk(f"MysteryIsle_Tree_{i+1:02d}_Trunk",
                                   (tx, ty, tz),
                                   height=4.0 + rng.uniform(0, 3.5),
                                   lean=(rng.uniform(-0.2,0.2), rng.uniform(-0.2,0.2)))
    assign_mat(trunk, mat_tree); smart_uv(trunk)
    link(col_trees, trunk)
    # 2-3 branches
    for b in range(rng.randint(2, 3)):
        ba = rng.uniform(0, math.pi*2)
        bl = 1.4 + rng.uniform(0, 2.0)
        bz = tz + trunk.scale.z * rng.uniform(0.6, 0.9) if hasattr(trunk, 'scale') else tz + 3
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=5, radius=0.045+rng.uniform(0,0.03),
            depth=bl, location=(tx+math.cos(ba)*bl*0.5, ty+math.sin(ba)*bl*0.5, bz+0.3))
        br = bpy.context.active_object
        br.name = f"MysteryIsle_Tree_{i+1:02d}_Branch_{b+1}"
        br.rotation_euler = (math.pi*0.5 - rng.uniform(0.1,0.5), 0, ba)
        assign_mat(br, mat_tree); smart_uv(br)
        link(col_trees, br)
print(f"[MysteryIsle] {len(tree_spots)} twisted dead trees created.")

# ── 8. FOG PATCHES ────────────────────────────────────────────────────────────
fog_locs = [(-25,15,1.4),(20,-20,1.6),(-10,30,1.5),(15,5,1.3),(-30,-10,1.8)]
for i, (fx, fy, fz) in enumerate(fog_locs):
    fp = build_fog_plane(f"MysteryIsle_FogPlane_{i+1:02d}",
                           (fx, fy, fz), size=rng.uniform(18, 32))
    assign_mat(fp, mat_fog); link(col_fog, fp)

# Root
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
root = bpy.context.active_object; root.name = "MysteryIsle_ROOT"
link(col_root, root)

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("MYSTERY ISLE — FULL QUALITY BUILD COMPLETE")
print("="*65)
print("  Terrain     : 52×52 grid, brooding dark hills, Musgrave detail")
print("  Great Statue: torso + head + 2 eye sockets(glow) + buried arm + hand")
print(f"  Stone rings : 3 rings = {total_ring_stones} standing stones")
print(f"  Rune stones : {len(rune_positions)} (glow lights)")
print("  Central altar: 3 tiers + carved basin + 4 pillars")
print(f"  Stone path  : {(len(path_pts)-1)*4} path stones winding up hill")
print(f"  Dead trees  : {len(tree_spots)} twisted trunks + branches")
print("  Fog patches : 5 translucent planes")
print("  Materials   : 11 full node trees + [UNITY] image slots")
print("  UV          : smart_project on all mesh objects")
print(f"\n  Unity: heavy green-grey fog + reverb audio + statue eye trigger")
print("="*65)
