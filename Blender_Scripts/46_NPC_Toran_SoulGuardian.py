"""
46_NPC_Toran_SoulGuardian.py
IsleTrial — Toran, Kael's Father / The Soul Guardian
================================================
Toran is the emotional core of IsleTrial's story. He was a sailor
and Trial Runner who failed the 4th Trial 20 years ago and has been
bound as a Spirit Guardian ever since.

Visual Design:
  Build:    Same proportions as Kael (03_Kael_Model.py) but broader,
            heavier — a man in his 50s, weathered and powerful.
  Height:   1.82m (slightly taller than Kael)
  Clothing: Torn, salt-stained sailor coat (darker, more worn than Kael's)
            Rolled-up sleeves, open collar, rough leather belt with a
            broken buckle, worn-out boots, no gloves.
  Face:     Weathered, high cheekbones, deep-set eyes, a scar across
            the left brow, short silver-white hair (aged). Strong jaw.
  Detail:   Broken compass pendant (same design as Kael's Soul Compass
            but cracked and dark). Chain mail piece visible under torn coat.
  Spirit:   Soul-binding chains — 6 heavy glowing cyan chains that wrap
            around his torso, arms, and legs (these break in Phase 3).
            Translucent ghost aura layer over skin.
  Weapon:   Compass Blade (same weapon as in 22_Weapon_CompassBlade.py,
            but older, worn version).

Body parts (all bmesh):
  Head, Skull, Brow Ridge, Chin, Nose, Ears, Jaw, Scar
  Eyes (3-layer: sclera / iris / pupil) + Ghost Eye Glow
  Neck + Neck scar
  Ghost Aura Sphere (translucent overlay over full body)
  Torso body (skin visible at collar), Coat torso (torn, frayed edges)
  Coat front panels (torn edges), Raised collar, Shoulder pads (worn)
  Upper Sleeves L+R, Forearms L+R (rolled sleeves), Bare Hands L+R
  Coat Tails (torn at bottom, irregular)
  Chain mail (chest piece visible through torn coat)
  Pants L+R (dark, worn), Boots L+R (cracked leather, worn sole)
  Belt (cracked leather + broken brass buckle + 4 loops)
  Broken Compass Pendant (cracked, dark, non-glowing)
  Silver Hair (short, rough, wind-blown backward)
  Soul Chain x6 (glowing cyan binding chains — separate objects)
  Compass Blade (worn version)
  Soul Glow Aura (wide, dim translucent overlay sphere)

Materials (full procedural + [UNITY] image texture slots):
  Ghost_Skin, Torn_Coat, Pants, Worn_Boot, Belt_Leather,
  Silver_Hair, Eye_White, Eye_Iris_Ghost, Broken_Compass,
  Soul_Chain, Ghost_Aura, Chain_Mail, Blade_Steel_Worn

Armature: T-pose, same bone structure as Kael_Rig.py
          Root + Spine(3) + Neck + Head + LowerJaw
          L/R Shoulder + UpperArm + LowerArm + Hand
          L/R UpperLeg + LowerLeg + Foot + Toe

UV: smart_project on every mesh
Run in Blender >= 3.6  →  Scripting workspace → Run Script
Export as FBX with armature for Unity.
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(460046)

# ── scene helpers ─────────────────────────────────────────────────────────────
def ns_lk(mat): return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, name, x, y):
    n = ns.new('ShaderNodeTexImage'); n.label = name; n.location = (x, y); return n

def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

def assign_mat(obj, mat):
    obj.data.materials.clear(); obj.data.materials.append(mat)

def link(col, obj):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def add_subdiv(obj, lv=1):
    m = obj.modifiers.new('Sub', 'SUBSURF')
    m.levels = lv; m.render_levels = lv

def add_pt_light(col, loc, energy, color, radius=0.1):
    bpy.ops.object.light_add(type='POINT', location=loc)
    lt = bpy.context.active_object
    lt.data.energy = energy; lt.data.color = color; lt.data.shadow_soft_size = radius
    col.objects.link(lt)
    if lt.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(lt)
    return lt

# ── materials ─────────────────────────────────────────────────────────────────
def build_ghost_skin_mat():
    """Translucent ghost skin — slightly visible through itself, pale with blue tint."""
    mat = bpy.data.materials.new("Mat_Toran_GhostSkin")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (760, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (480, 150)
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Transmission Weight'].default_value = 0.20
    bsdf.inputs['Emission Color'].default_value = (0.3, 0.7, 0.9, 1)
    bsdf.inputs['Emission Strength'].default_value = 0.4
    em   = ns.new('ShaderNodeEmission');       em.location   = (480,-100)
    em.inputs['Color'].default_value    = (0.25, 0.65, 0.9, 1)
    em.inputs['Strength'].default_value = 0.8
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-600, 200)
    noise.inputs['Scale'].default_value  = 6.0; noise.inputs['Detail'].default_value = 5.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.70,0.55,0.50,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.88,0.72,0.65,1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (260, 280)
    bmp.inputs['Strength'].default_value = 0.6; bmp.inputs['Distance'].default_value = 0.02
    img_a = img_slot(ns,"[UNITY] Toran_Skin_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] Toran_Skin_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] Toran_Skin_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (260, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_torn_coat_mat():
    mat = bpy.data.materials.new("Mat_Toran_TornCoat")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.90
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-600, 200)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value = 8.0; mus.inputs['Detail'].default_value = 6.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.06,0.04,0.03,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.18,0.12,0.09,1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600,-100)
    vor.voronoi_dimensions = '3D'; vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 12.0
    cr2  = ns.new('ShaderNodeValToRGB');       cr2.location  = (-300,-100)
    cr2.color_ramp.elements[0].position = 0.0; cr2.color_ramp.elements[0].color = (0.0,0.0,0.0,1)
    cr2.color_ramp.elements[1].position = 0.10;cr2.color_ramp.elements[1].color = (1.0,1.0,1.0,1)
    mix  = ns.new('ShaderNodeMixRGB');         mix.location  = (50, 100)
    mix.blend_type = 'DARKEN'; mix.inputs['Fac'].default_value = 0.35
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (400, 280)
    bmp.inputs['Strength'].default_value = 1.2; bmp.inputs['Distance'].default_value = 0.03
    img_a = img_slot(ns,"[UNITY] Toran_Coat_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] Toran_Coat_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] Toran_Coat_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (400, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr1.inputs['Fac'])
    lk.new(vor.outputs['Distance'],cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],     bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_pants_mat():
    mat = bpy.data.materials.new("Mat_Toran_Pants")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.88
    noise= ns.new('ShaderNodeTexNoise');       noise.location = (-500, 100)
    noise.inputs['Scale'].default_value = 10.0; noise.inputs['Detail'].default_value = 5.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location = (-250, 100)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.08,0.07,0.06,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.20,0.16,0.12,1)
    img_a = img_slot(ns,"[UNITY] Toran_Pants_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] Toran_Pants_Normal", -660,-550)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_worn_boot_mat():
    mat = bpy.data.materials.new("Mat_Toran_WornBoot")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.92
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location = (-500, 100)
    mus.inputs['Scale'].default_value = 10.0; mus.inputs['Detail'].default_value = 6.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location = (-250, 100)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.05,0.03,0.02,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.18,0.10,0.06,1)
    img_a = img_slot(ns,"[UNITY] Toran_Boot_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] Toran_Boot_Normal", -660,-550)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_belt_mat():
    mat = bpy.data.materials.new("Mat_Toran_Belt")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Base Color'].default_value = (0.08, 0.04, 0.02, 1)
    img_a = img_slot(ns,"[UNITY] Toran_Belt_Albedo", -400,-250)
    img_n = img_slot(ns,"[UNITY] Toran_Belt_Normal", -400,-450)
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_silver_hair_mat():
    mat = bpy.data.materials.new("Mat_Toran_SilverHair")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.45; bsdf.inputs['Specular IOR Level'].default_value = 0.3
    noise= ns.new('ShaderNodeTexNoise');       noise.location = (-500, 100)
    noise.inputs['Scale'].default_value = 25.0; noise.inputs['Detail'].default_value = 4.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location = (-250, 100)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.68,0.68,0.68,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.95,0.95,0.95,1)
    img_a = img_slot(ns,"[UNITY] Toran_Hair_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] Toran_Hair_Normal", -660,-550)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_eye_white_mat():
    mat = bpy.data.materials.new("Mat_Toran_EyeWhite")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (700, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 0)
    bsdf.inputs['Roughness'].default_value = 0.12
    bsdf.inputs['Base Color'].default_value = (0.88, 0.88, 0.86, 1)
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_ghost_eye_mat():
    """Spirit-possessed eyes — glowing pale blue, hollow look."""
    mat = bpy.data.materials.new("Mat_Toran_GhostEye")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (600, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (350, 100)
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['Transmission Weight'].default_value = 0.5
    bsdf.inputs['Base Color'].default_value = (0.4, 0.78, 0.95, 1)
    em   = ns.new('ShaderNodeEmission');       em.location = (350, -100)
    em.inputs['Color'].default_value    = (0.3, 0.75, 1.0, 1)
    em.inputs['Strength'].default_value = 6.0
    img_e = img_slot(ns,"[UNITY] ToranEye_Emission", -350,-200)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_soul_chain_mat():
    mat = bpy.data.materials.new("Mat_Toran_SoulChain")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.05; bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Base Color'].default_value = (0.1, 0.6, 0.9, 1)
    bsdf.inputs['Emission Color'].default_value = (0.2, 0.8, 1.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 4.0
    em   = ns.new('ShaderNodeEmission');       em.location = (400,-100)
    em.inputs['Color'].default_value    = (0.1, 0.75, 1.0, 1)
    em.inputs['Strength'].default_value = 8.0
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-500, 0)
    wave.wave_type = 'BANDS'; wave.inputs['Scale'].default_value = 8.0
    wave.inputs['Distortion'].default_value = 1.5
    cr   = ns.new('ShaderNodeValToRGB');       cr.location = (-250, 0)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] SoulChain_Emission", -660,-350)
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_ghost_aura_mat():
    """Full-body translucent ghost overlay — wide cyan glow around Toran."""
    mat = bpy.data.materials.new("Mat_Toran_GhostAura")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    mat.blend_method = 'BLEND'
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Alpha'].default_value = 0.08
    bsdf.inputs['Base Color'].default_value = (0.2, 0.7, 0.95, 1)
    em   = ns.new('ShaderNodeEmission');       em.location = (400,-100)
    em.inputs['Color'].default_value    = (0.15, 0.65, 0.92, 1)
    em.inputs['Strength'].default_value = 1.5
    img_e = img_slot(ns,"[UNITY] GhostAura_Emission", -400,-250)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_broken_compass_mat():
    mat = bpy.data.materials.new("Mat_Toran_BrokenCompass")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.55; bsdf.inputs['Metallic'].default_value = 0.75
    bsdf.inputs['Base Color'].default_value = (0.28, 0.22, 0.12, 1)
    noise= ns.new('ShaderNodeTexNoise');       noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 20.0; noise.inputs['Detail'].default_value = 4.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location = (-150, 100)
    cr1.color_ramp.elements[0].position = 0.3; cr1.color_ramp.elements[0].color = (0.15,0.10,0.05,1)
    cr1.color_ramp.elements[1].position = 0.8; cr1.color_ramp.elements[1].color = (0.40,0.32,0.18,1)
    img_a = img_slot(ns,"[UNITY] Toran_Compass_Albedo",    -550,-300)
    img_n = img_slot(ns,"[UNITY] Toran_Compass_Normal",    -550,-500)
    img_r = img_slot(ns,"[UNITY] Toran_Compass_Roughness", -550,-700)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_chain_mail_mat():
    mat = bpy.data.materials.new("Mat_Toran_ChainMail")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.45; bsdf.inputs['Metallic'].default_value = 0.80
    bsdf.inputs['Base Color'].default_value = (0.25, 0.23, 0.20, 1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location = (-500, 200)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 18.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location = (380, 250)
    bmp.inputs['Strength'].default_value = 1.5
    img_a = img_slot(ns,"[UNITY] Toran_Mail_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] Toran_Mail_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] Toran_Mail_Roughness", -660,-750)
    lk.new(vor.outputs['Distance'], bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_blade_worn_mat():
    mat = bpy.data.materials.new("Mat_Toran_BladeWorn")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.45; bsdf.inputs['Metallic'].default_value = 0.88
    noise= ns.new('ShaderNodeTexNoise');       noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 15.0; noise.inputs['Detail'].default_value = 5.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location = (-150, 100)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.30,0.28,0.25,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.65,0.62,0.58,1)
    img_a = img_slot(ns,"[UNITY] ToranBlade_Albedo",    -550,-300)
    img_n = img_slot(ns,"[UNITY] ToranBlade_Normal",    -550,-500)
    img_r = img_slot(ns,"[UNITY] ToranBlade_Roughness", -550,-700)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

# ── geometry builders ─────────────────────────────────────────────────────────
def build_skull(name, mat=None):
    """Broad, weathered skull — wider than Kael's, deep-set eye sockets."""
    bm = bmesh.new(); segs = 16; rings = 18; h = 0.28
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t*h
        if t < 0.25:  rx = 0.16 + t*0.7; ry = 0.14 + t*0.55
        elif t < 0.7: rx = 0.33 + (t-0.25)*0.06; ry = 0.28 + (t-0.25)*0.04
        else:         rt=(t-0.7)/0.3; rx=0.36*(1-rt*0.12); ry=0.30*(1-rt*0.12)
        ring = [bm.verts.new((rx*math.cos(2*math.pi*s/segs),
                               ry*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    top = bm.verts.new((0, 0, h+0.015))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], top])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_face(name, mat=None):
    """Weathered face: strong jaw, hollow cheeks, scar over left brow."""
    bm = bmesh.new(); segs = 14; rings = 16; h = 0.20
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t*h
        if t < 0.25:  rx = 0.14; ry = 0.08
        elif t < 0.55:rx = 0.20 + (t-0.25)*0.12; ry = 0.12 + (t-0.25)*0.08
        else:         rt=(t-0.55)/0.45; rx=0.236*(1-rt*0.35); ry=0.146*(1-rt*0.30)
        ring = [bm.verts.new((rx*math.cos(2*math.pi*s/segs),
                               ry*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_nose(name, mat=None):
    bm = bmesh.new(); segs = 6; rings = 8
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*0.06
        if t < 0.5: rx = 0.025*math.sin(t/0.5*math.pi*0.5); ry = 0.020*math.sin(t/0.5*math.pi*0.5)
        else:       rx = 0.025*(1+(1-t)*0.5); ry = 0.020*(1+(1-t)*0.3)
        ring = [bm.verts.new((rx*math.cos(2*math.pi*s/segs),
                               ry*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_brow_scar(name, mat=None):
    """A flat raised scar line over left brow."""
    bm = bmesh.new(); segs = 8; scar_len = 0.06; scar_w = 0.008; scar_h = 0.003
    for si in range(segs):
        t0 = si/segs; t1 = (si+1)/segs
        x0 = t0*scar_len - scar_len*0.5; x1 = t1*scar_len - scar_len*0.5
        taper = 1 - abs(t0 - 0.5)*1.8
        if taper < 0.1: taper = 0.1
        bm.faces.new([bm.verts.new(p) for p in [
            (x0, -scar_w*taper, scar_h), (x1, -scar_w*taper, scar_h),
            (x1,  scar_w*taper, scar_h), (x0,  scar_w*taper, scar_h)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_eye(name, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.032)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); return obj

def build_iris(name, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.022)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); return obj

def build_ear(name, mat=None):
    bm = bmesh.new(); segs = 8
    pts = [(0,0,0),(0.04,0,0),(0.04,0,0.06),(0.01,0,0.072),(0,0,0.05)]
    for i in range(len(pts)-1):
        p0=pts[i]; p1=pts[i+1]
        bm.faces.new([bm.verts.new(q) for q in [
            (p0[0],p0[1]-0.008,p0[2]),(p1[0],p1[1]-0.008,p1[2]),
            (p1[0],p1[1]+0.008,p1[2]),(p0[0],p0[1]+0.008,p0[2])]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_neck(name, mat=None):
    bm = bmesh.new(); segs = 12; rings = 12; h = 0.16
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t*h
        r = 0.080 + 0.010*math.sin(t*math.pi)
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs),
                               r*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_torso(name, mat=None):
    """Broad, heavy torso — 10% wider than Kael's."""
    bm = bmesh.new(); segs = 16; rings = 22; h = 0.56
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t*h
        if t < 0.15:
            rx = 0.130 + t*1.0; ry = 0.110 + t*0.80
        elif t < 0.7:
            rx = 0.280 + 0.025*math.sin((t-0.15)/0.55*math.pi)
            ry = 0.228 + 0.018*math.sin((t-0.15)/0.55*math.pi)
        else:
            rt=(t-0.7)/0.3; rx=0.282*(1-rt*0.12); ry=0.232*(1-rt*0.10)
        ring = [bm.verts.new((rx*math.cos(2*math.pi*s/segs),
                               ry*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_coat(name, mat=None):
    """Torn coat over torso — slightly larger than torso with frayed hem."""
    bm = bmesh.new(); segs = 16; rings = 20; h = 0.60
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t*h
        if t < 0.12:
            rx = 0.145 + t*1.0; ry = 0.120 + t*0.80
        elif t < 0.72:
            rx = 0.260 + 0.035*math.sin((t-0.12)/0.60*math.pi)
            ry = 0.214 + 0.025*math.sin((t-0.12)/0.60*math.pi)
        else:
            rt=(t-0.72)/0.28; rx=0.268*(1-rt*0.08); ry=0.222*(1-rt*0.06)
        # frayed bottom: irregular edge at hem
        fray = 1 + (0.012*rng.uniform(-1,1) if t > 0.90 else 0)
        ring = [bm.verts.new((rx*fray*math.cos(2*math.pi*s/segs),
                               ry*fray*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_coat_tail(name, side=1, mat=None):
    """Single torn coat tail hanging from the rear."""
    bm = bmesh.new(); segs_w = 5; segs_h = 12; w = 0.13; h = 0.35
    for iw in range(segs_w):
        for ih in range(segs_h):
            x0=(iw/segs_w-0.5)*w*side; x1=((iw+1)/segs_w-0.5)*w*side
            z0=-ih/segs_h*h; z1=-(ih+1)/segs_h*h
            # taper toward bottom
            taper = 1 - ih/segs_h*0.5
            warp = 0.008*math.sin(iw*2.2+ih*1.5)
            bm.faces.new([bm.verts.new(p) for p in [
                (x0*taper, warp, z0),(x1*taper, warp, z0),
                (x1*taper*(1-0.06), warp, z1),(x0*taper*(1-0.06), warp, z1)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_chain_mail_piece(name, mat=None):
    """Small chain mail section visible through torn coat at chest."""
    bm = bmesh.new(); segs_w = 8; segs_h = 6; w = 0.18; h = 0.14
    for iw in range(segs_w):
        for ih in range(segs_h):
            x0=(iw/segs_w-0.5)*w; x1=((iw+1)/segs_w-0.5)*w
            z0=ih/segs_h*h; z1=(ih+1)/segs_h*h
            warp=0.004*math.sin(iw*2.5+ih*1.8)
            bm.faces.new([bm.verts.new(p) for p in [(x0,warp,z0),(x1,warp,z0),(x1,warp,z1),(x0,warp,z1)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_upper_arm(name, mat=None):
    bm = bmesh.new(); segs = 10; rings = 12; h = 0.26
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*h
        r = 0.068 - t*0.010
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs),
                               r*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_forearm(name, mat=None):
    bm = bmesh.new(); segs = 10; rings = 12; h = 0.24
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*h
        r = 0.055 - t*0.008
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs),
                               r*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_hand(name, mat=None):
    """Large bare hand — no gloves."""
    bm = bmesh.new(); segs = 10; rings = 8; h = 0.10
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*h
        rx = 0.050 - t*0.008; ry = 0.038 - t*0.006
        ring = [bm.verts.new((rx*math.cos(2*math.pi*s/segs),
                               ry*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    # finger stubs (4)
    for fi in range(4):
        fx = (fi - 1.5)*0.022; flen = 0.055; fr = 0.012
        for ri in range(6):
            t0 = ri/5; t1 = (ri+1)/5; z0 = -h - t0*flen; z1 = -h - t1*flen; cr = fr*(1-t0*0.4)
            pts_b = [bm.verts.new((fx+cr*math.cos(2*math.pi*s/6), cr*math.sin(2*math.pi*s/6), z0)) for s in range(6)]
            pts_t = [bm.verts.new((fx+cr*math.cos(2*math.pi*s/6), cr*math.sin(2*math.pi*s/6), z1)) for s in range(6)]
            for s in range(6):
                bm.faces.new([pts_b[s],pts_b[(s+1)%6],pts_t[(s+1)%6],pts_t[s]])
    # thumb
    tx = -0.062; tz = -h*0.6; tlen = 0.045; tr = 0.013
    for ri in range(4):
        t0 = ri/3; t1 = (ri+1)/3; z0 = tz - t0*tlen; z1 = tz - t1*tlen; cr = tr*(1-t0*0.3)
        pts_b = [bm.verts.new((tx+cr*math.cos(2*math.pi*s/6), cr*math.sin(2*math.pi*s/6), z0)) for s in range(6)]
        pts_t = [bm.verts.new((tx+cr*math.cos(2*math.pi*s/6), cr*math.sin(2*math.pi*s/6), z1)) for s in range(6)]
        for s in range(6):
            bm.faces.new([pts_b[s],pts_b[(s+1)%6],pts_t[(s+1)%6],pts_t[s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_pelvis(name, mat=None):
    bm = bmesh.new(); segs = 16; rings = 10; h = 0.22
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t*h
        rx = 0.24 - t*0.03; ry = 0.19 - t*0.02
        ring = [bm.verts.new((rx*math.cos(2*math.pi*s/segs),
                               ry*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_upper_leg(name, mat=None):
    bm = bmesh.new(); segs = 12; rings = 14; h = 0.44
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*h
        r = 0.090 - t*0.015
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs),
                               r*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_lower_leg(name, mat=None):
    bm = bmesh.new(); segs = 12; rings = 14; h = 0.42
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*h
        r = 0.072 - t*0.012
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs),
                               r*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_boot(name, mat=None):
    """Worn cracked boot."""
    bm = bmesh.new(); segs = 12; rings = 14; h = 0.22
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*h
        if t < 0.6: rx = 0.070; ry = 0.058
        else:       rt=(t-0.6)/0.4; rx=0.070+rt*0.020; ry=0.058+rt*0.015
        crack = 0.003 * rng.uniform(-1,1)
        ring = [bm.verts.new((rx*math.cos(2*math.pi*s/segs)+crack,
                               ry*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    bm.faces.new(verts_ring[rings][::-1])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_belt(name, mat=None):
    bm = bmesh.new(); segs = 32; r = 0.265; h = 0.035
    for s in range(segs):
        a0 = 2*math.pi*s/segs; a1 = 2*math.pi*(s+1)/segs
        bm.faces.new([bm.verts.new(p) for p in [
            (r*math.cos(a0),r*math.sin(a0),0),(r*math.cos(a1),r*math.sin(a1),0),
            (r*math.cos(a1),r*math.sin(a1),h),(r*math.cos(a0),r*math.sin(a0),h)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_broken_compass_pendant(name, mat=None):
    """Compass pendant — cracked, dark, no glow."""
    bm = bmesh.new()
    # case disc
    segs = 16; r = 0.028
    verts = [bm.verts.new((r*math.cos(2*math.pi*s/segs),
                            r*math.sin(2*math.pi*s/segs), 0)) for s in range(segs)]
    bm.faces.new(verts)
    # torus bezel
    for s in range(segs):
        a0=2*math.pi*s/segs; a1=2*math.pi*(s+1)/segs; ri=0.028; ro=0.034; h=0.006
        bm.faces.new([bm.verts.new(p) for p in [
            (ri*math.cos(a0),ri*math.sin(a0),0),(ro*math.cos(a0),ro*math.sin(a0),0),
            (ro*math.cos(a1),ro*math.sin(a1),0),(ri*math.cos(a1),ri*math.sin(a1),0)]])
    # crack line across face
    for ci in range(8):
        t = ci/8; cl = 0.028
        bm.faces.new([bm.verts.new(p) for p in [
            (-cl*0.6+t*cl, -0.001, 0.007),
            (-cl*0.6+(t+0.12)*cl, -0.001, 0.007),
            (-cl*0.6+(t+0.12)*cl+0.003*math.sin(t*10), 0.001, 0.007),
            (-cl*0.6+t*cl+0.003*math.sin(t*10), 0.001, 0.007)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_silver_hair(name, mat=None):
    """Short, windswept backward silver hair — rough, unkempt."""
    bm = bmesh.new(); tuft_count = 12
    for ti in range(tuft_count):
        ang = 2*math.pi*ti/tuft_count
        ox = 0.25*math.cos(ang); oy = 0.20*math.sin(ang)
        # sweep backward
        sweep_back = 0.04*(1-abs(math.sin(ang))*0.5)
        tlen = 0.04 + 0.03*abs(math.cos(ang)); tw = 0.015
        segs = 6
        for r in range(segs+1):
            t = r/segs; z = 0.26 + t*tlen
            bx = ox + sweep_back*t; by = oy - 0.015*t
            radius = tw*(1-t*0.75)
            if radius < 0.003: radius = 0.003
            if r > 0:
                for s in range(6):
                    v0=bm.verts.new((bx+radius*math.cos(2*math.pi*s/6),
                                     by+radius*math.sin(2*math.pi*s/6), z))
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_soul_chain(name, path_pts, mat=None):
    """A heavy spirit chain linking two points — segmented links."""
    bm = bmesh.new(); n_links = 10; link_r = 0.012; link_h = 0.032
    for li in range(n_links):
        t = li / n_links
        px = path_pts[0][0] + t*(path_pts[1][0]-path_pts[0][0])
        py = path_pts[0][1] + t*(path_pts[1][1]-path_pts[0][1])
        pz = path_pts[0][2] + t*(path_pts[1][2]-path_pts[0][2])
        sag = -0.04 * math.sin(t * math.pi)
        segs = 8
        # link ring
        for s in range(segs):
            a0 = 2*math.pi*s/segs; a1 = 2*math.pi*(s+1)/segs
            bm.faces.new([bm.verts.new(q) for q in [
                (px+link_r*math.cos(a0), py+link_r*math.sin(a0), pz+sag),
                (px+link_r*math.cos(a1), py+link_r*math.sin(a1), pz+sag),
                (px+link_r*math.cos(a1), py+link_r*math.sin(a1), pz+sag+link_h),
                (px+link_r*math.cos(a0), py+link_r*math.sin(a0), pz+sag+link_h)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_ghost_aura_sphere(name, mat=None):
    """Wide translucent sphere wrapping the entire body — ghost effect."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=14, radius=0.45)
    # slightly irregular
    for v in bm.verts:
        v.co.x += rng.uniform(-0.015, 0.015)
        v.co.y += rng.uniform(-0.015, 0.015)
        v.co.z += rng.uniform(-0.015, 0.015)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    return obj

def build_compass_blade_worn(name, mat=None):
    """Worn compass blade — same shape as Kael's but aged."""
    bm = bmesh.new()
    # blade: curved profile with compass-circle guard
    segs = 6; rings = 22; blade_len = 0.72
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*blade_len
        if t < 0.12:  rx = 0.009*math.sin(t/0.12*math.pi*0.5); ry = 0.004*math.sin(t/0.12*math.pi*0.5)
        elif t < 0.85:rx = 0.009*(1-(t-0.12)/0.73*0.55); ry = 0.004*(1-(t-0.12)/0.73*0.55)
        else:         rx = 0.004*(1-(t-0.85)/0.15); ry = 0.002*(1-(t-0.85)/0.15)
        if rx < 0.0015: rx = 0.0015
        # slight curve
        curve_x = 0.04*math.sin(t*math.pi*0.9)
        ring = [bm.verts.new((rx*math.cos(2*math.pi*s/segs)+curve_x,
                               ry*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0.04, 0, blade_len+0.025))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    # guard (compass circle)
    g_segs = 14; g_r = 0.065
    for s in range(g_segs):
        a0 = 2*math.pi*s/g_segs; a1 = 2*math.pi*(s+1)/g_segs
        bm.faces.new([bm.verts.new(p) for p in [
            (g_r*math.cos(a0),g_r*math.sin(a0),0.06),
            (g_r*math.cos(a1),g_r*math.sin(a1),0.06),
            (g_r*math.cos(a1),g_r*math.sin(a1),0.075),
            (g_r*math.cos(a0),g_r*math.sin(a0),0.075)]])
    # grip
    for r in range(10):
        t0=r/9; t1=(r+1)/9; z0=-t0*0.18; z1=-t1*0.18; gr=0.018
        pts_b = [bm.verts.new((gr*math.cos(2*math.pi*s/8), gr*math.sin(2*math.pi*s/8), z0)) for s in range(8)]
        pts_t = [bm.verts.new((gr*math.cos(2*math.pi*s/8), gr*math.sin(2*math.pi*s/8), z1)) for s in range(8)]
        for s in range(8):
            bm.faces.new([pts_b[s],pts_b[(s+1)%8],pts_t[(s+1)%8],pts_t[s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

# ── armature ──────────────────────────────────────────────────────────────────
def build_armature(name, col):
    bpy.ops.object.armature_add(enter_editmode=True, location=(0,0,0))
    arm_obj = bpy.context.active_object; arm_obj.name = name
    arm = arm_obj.data; arm.name = name + "_Data"
    bpy.ops.armature.select_all(action='SELECT'); bpy.ops.armature.delete()
    eb = arm.edit_bones
    # same structure as Kael — compatible rig for shared animations
    bone_defs = [
        ("Root",         None,          (0,0,0),          (0,0,0.12)),
        ("Pelvis",       "Root",        (0,0,0.12),       (0,0,0.38)),
        ("Spine1",       "Pelvis",      (0,0,0.38),       (0,0,0.66)),
        ("Spine2",       "Spine1",      (0,0,0.66),       (0,0,0.90)),
        ("Spine3",       "Spine2",      (0,0,0.90),       (0,0,1.08)),
        ("Neck",         "Spine3",      (0,0,1.08),       (0,0,1.20)),
        ("Head",         "Neck",        (0,0,1.20),       (0,0,1.52)),
        ("LowerJaw",     "Head",        (0,-0.04,1.24),   (0,-0.04,1.12)),
        # Right Arm
        ("R_Shoulder",   "Spine3",      ( 0.15,0,1.06),   ( 0.28,0,1.04)),
        ("R_UpperArm",   "R_Shoulder",  ( 0.28,0,1.04),   ( 0.28,0,0.80)),
        ("R_LowerArm",   "R_UpperArm",  ( 0.28,0,0.80),   ( 0.28,0,0.58)),
        ("R_Hand",       "R_LowerArm",  ( 0.28,0,0.58),   ( 0.28,0,0.48)),
        # Left Arm
        ("L_Shoulder",   "Spine3",      (-0.15,0,1.06),   (-0.28,0,1.04)),
        ("L_UpperArm",   "L_Shoulder",  (-0.28,0,1.04),   (-0.28,0,0.80)),
        ("L_LowerArm",   "L_UpperArm",  (-0.28,0,0.80),   (-0.28,0,0.58)),
        ("L_Hand",       "L_LowerArm",  (-0.28,0,0.58),   (-0.28,0,0.48)),
        # Right Leg
        ("R_UpperLeg",   "Pelvis",      ( 0.12,0,0.18),   ( 0.12,0,-0.24)),
        ("R_LowerLeg",   "R_UpperLeg",  ( 0.12,0,-0.24),  ( 0.12,0,-0.62)),
        ("R_Foot",       "R_LowerLeg",  ( 0.12,0,-0.62),  ( 0.12,0,-0.82)),
        ("R_Toe",        "R_Foot",      ( 0.12,0,-0.82),  ( 0.12,0.08,-0.86)),
        # Left Leg
        ("L_UpperLeg",   "Pelvis",      (-0.12,0,0.18),   (-0.12,0,-0.24)),
        ("L_LowerLeg",   "L_UpperLeg",  (-0.12,0,-0.24),  (-0.12,0,-0.62)),
        ("L_Foot",       "L_LowerLeg",  (-0.12,0,-0.62),  (-0.12,0,-0.82)),
        ("L_Toe",        "L_Foot",      (-0.12,0,-0.82),  (-0.12,0.08,-0.86)),
    ]
    created = {}
    for bname, parent, head, tail in bone_defs:
        b = eb.new(bname); b.head = head; b.tail = tail
        if parent and parent in created: b.parent = created[parent]
        created[bname] = b
    bpy.ops.object.mode_set(mode='OBJECT')
    col.objects.link(arm_obj)
    if arm_obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(arm_obj)
    return arm_obj

# ── scene assembly ────────────────────────────────────────────────────────────
def build_scene():
    for o in list(bpy.data.objects):   bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):    bpy.data.meshes.remove(m, do_unlink=True)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m, do_unlink=True)

    col = bpy.data.collections.new("Toran_SoulGuardian")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'skin':    build_ghost_skin_mat(),
        'coat':    build_torn_coat_mat(),
        'pants':   build_pants_mat(),
        'boot':    build_worn_boot_mat(),
        'belt':    build_belt_mat(),
        'hair':    build_silver_hair_mat(),
        'eye_w':   build_eye_white_mat(),
        'eye_i':   build_ghost_eye_mat(),
        'chain':   build_soul_chain_mat(),
        'aura':    build_ghost_aura_mat(),
        'compass': build_broken_compass_mat(),
        'mail':    build_chain_mail_mat(),
        'blade':   build_blade_worn_mat(),
    }
    objs = []

    # ── HEAD ──────────────────────────────────────────────────────────────────
    skull = build_skull("Toran_Skull", mats['skin']); skull.location=(0,0,1.24); link(col,skull); objs.append(skull)
    face  = build_face("Toran_Face",  mats['skin']); face.location=(0,0.25,1.24); link(col,face); objs.append(face)
    nose  = build_nose("Toran_Nose",  mats['skin']); nose.location=(0,0.44,1.35); link(col,nose); objs.append(nose)
    # brow scar (left side)
    scar  = build_brow_scar("Toran_BrowScar", mats['skin']); scar.location=(-0.08,0.43,1.47); scar.rotation_euler=(0,0.1,0.08); link(col,scar); objs.append(scar)
    # ears
    for side, ex, flip in [("L",-0.34, False),("R", 0.34, True)]:
        ear = build_ear(f"Toran_Ear_{side}", mats['skin'])
        ear.location=(ex,0.02,1.36)
        if flip: ear.rotation_euler=(0,0,math.pi)
        link(col,ear); objs.append(ear)
    # eyes
    for side, ex in [("L",-0.10),("R",0.10)]:
        ew = build_eye(f"Toran_EyeWhite_{side}", mats['eye_w']); ew.location=(ex,0.43,1.42); link(col,ew); objs.append(ew)
        ei = build_iris(f"Toran_Iris_{side}", mats['eye_i']);    ei.location=(ex,0.46,1.42); link(col,ei); objs.append(ei)
    add_pt_light(col,(0,0.45,1.42), energy=2.0, color=(0.3,0.75,1.0), radius=0.06)

    # hair
    hair = build_silver_hair("Toran_Hair", mats['hair']); hair.location=(0,-0.04,1.24); link(col,hair); objs.append(hair)

    # ── NECK & TORSO ─────────────────────────────────────────────────────────
    neck   = build_neck("Toran_Neck", mats['skin']); neck.location=(0,0,1.08); link(col,neck); objs.append(neck)
    torso  = build_torso("Toran_Torso", mats['skin']); torso.location=(0,0,0.52); link(col,torso); objs.append(torso)
    coat   = build_coat("Toran_Coat", mats['coat']); coat.location=(0,0,0.50); link(col,coat); objs.append(coat)
    # chain mail visible through torn chest opening
    mail   = build_chain_mail_piece("Toran_ChainMail", mats['mail']); mail.location=(0.06,0.26,0.80); link(col,mail); objs.append(mail)
    # coat tails
    for side, sv in [("L",-1),("R",1)]:
        ct = build_coat_tail(f"Toran_CoatTail_{side}", sv, mats['coat']); ct.location=(sv*0.08,-0.25,0.48); link(col,ct); objs.append(ct)
    # belt
    belt = build_belt("Toran_Belt", mats['belt']); belt.location=(0,0,0.54); link(col,belt); objs.append(belt)
    # broken compass pendant
    comp = build_broken_compass_pendant("Toran_BrokenCompass", mats['compass']); comp.location=(0,0.26,0.88); link(col,comp); objs.append(comp)
    pelvis = build_pelvis("Toran_Pelvis", mats['pants']); pelvis.location=(0,0,0.30); link(col,pelvis); objs.append(pelvis)

    # ── ARMS ─────────────────────────────────────────────────────────────────
    arm_cfgs = [
        ("L",  -0.28, 1.04, "L_UpperArm"),
        ("R",   0.28, 1.04, "R_UpperArm"),
    ]
    for side, ax, az, _ in arm_cfgs:
        ua = build_upper_arm(f"Toran_UpperArm_{side}", mats['coat']); ua.location=(ax,0,az); link(col,ua); objs.append(ua)
        fa = build_forearm(f"Toran_Forearm_{side}", mats['skin']); fa.location=(ax,0,az-0.26); link(col,fa); objs.append(fa)
        ha = build_hand(f"Toran_Hand_{side}", mats['skin']); ha.location=(ax,0,az-0.50); link(col,ha); objs.append(ha)

    # ── LEGS ─────────────────────────────────────────────────────────────────
    for side, lx in [("L",-0.12),("R",0.12)]:
        ul = build_upper_leg(f"Toran_UpperLeg_{side}", mats['pants']); ul.location=(lx,0,0.18); link(col,ul); objs.append(ul)
        ll = build_lower_leg(f"Toran_LowerLeg_{side}", mats['pants']); ll.location=(lx,0,-0.24); link(col,ll); objs.append(ll)
        bt = build_boot(f"Toran_Boot_{side}", mats['boot']); bt.location=(lx,0,-0.62); link(col,bt); objs.append(bt)

    # ── WEAPON (in right hand) ────────────────────────────────────────────────
    blade = build_compass_blade_worn("Toran_CompassBlade", mats['blade'])
    blade.location=(0.38, 0.05, 0.50); blade.rotation_euler=(0.1, 0, 0.15)
    link(col,blade); objs.append(blade)

    # ── GHOST AURA ────────────────────────────────────────────────────────────
    aura = build_ghost_aura_sphere("Toran_GhostAura", mats['aura'])
    aura.location=(0,0,0.80)
    link(col,aura); objs.append(aura)
    add_pt_light(col,(0,0,0.90), energy=3.5, color=(0.2,0.65,0.92), radius=0.8)

    # ── SOUL CHAINS (6) ───────────────────────────────────────────────────────
    # Chains wrap around: chest (2), arms (2), legs (2)
    chain_configs = [
        ("Toran_Chain_Chest_L",   [(-0.28,0,0.95), ( 0.28,0,0.55)]),
        ("Toran_Chain_Chest_R",   [( 0.28,0,0.90), (-0.25,0,0.58)]),
        ("Toran_Chain_LArm",      [(-0.28,0,0.78), (-0.28,0,0.52)]),
        ("Toran_Chain_RArm",      [( 0.28,0,0.78), ( 0.28,0,0.52)]),
        ("Toran_Chain_LLeg",      [(-0.12,0,0.15), (-0.12,0,-0.40)]),
        ("Toran_Chain_RLeg",      [( 0.12,0,0.15), ( 0.12,0,-0.40)]),
    ]
    for cname, cpts in chain_configs:
        ch = build_soul_chain(cname, cpts, mats['chain'])
        link(col,ch); objs.append(ch)
        mid_pt = ((cpts[0][0]+cpts[1][0])/2, (cpts[0][1]+cpts[1][1])/2, (cpts[0][2]+cpts[1][2])/2)
        add_pt_light(col, mid_pt, energy=1.5, color=(0.1,0.75,1.0), radius=0.12)

    # ── ARMATURE ─────────────────────────────────────────────────────────────
    arm = build_armature("Toran_Armature", col)
    arm.location=(0,0,0)
    for obj in objs:
        obj.parent = arm
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = arm

    print(f"[Toran_SoulGuardian] Built {len(objs)} mesh objects + 1 armature.")
    print("=== UNITY SETUP NOTES ===")
    print("Prefab: GhostAura sphere — set material blend to TRANSPARENT + script to pulse alpha")
    print("Soul Chains: Each chain is a separate object — animate scale to 0 in Phase 3 (breaking)")
    print("Eye material: emission strength drives the soul-possession visual — animate 0→8 in Phase 2")
    print("Broken compass: set as child of R_Hand bone — no emissive")
    print("Rig is identical to Kael's rig structure — can share idle/walk animations")
    print("Export: FBX with Armature + Mesh, Apply Transform")

build_scene()
