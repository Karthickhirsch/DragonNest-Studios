"""
39_Environment_UnderwaterRuins.py
IsleTrial — Underwater Ruins Environment Set
================================================
Creates an evocative deep-sea ruin complex: sunken temple columns,
cracked floor slabs, barnacle-crusted walls, submerged arches,
scattered amphora/pots, giant coral formations, seaweed forests,
broken statues, treasure debris, bioluminescent sea creatures
(mesh proxy), caustic light planes, silt ground, dive bubbles,
and deep-sea vent chimneys with glow effects.

All materials use full procedural node networks + [UNITY] image slots.
smart_uv() applied to every mesh. Run in Blender ≥ 3.6.
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(390039)

# ── helpers ───────────────────────────────────────────────────────────────────
def ns_lk(mat):
    return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, name, x, y):
    n = ns.new('ShaderNodeTexImage')
    n.label = name; n.location = (x, y)
    return n

def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def link(col, obj):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def add_pt_light(col, loc, energy, color, radius=0.3):
    bpy.ops.object.light_add(type='POINT', location=loc)
    lt = bpy.context.active_object
    lt.data.energy = energy; lt.data.color = color
    lt.data.shadow_soft_size = radius
    col.objects.link(lt)
    if lt.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(lt)
    return lt

# ── material builders ─────────────────────────────────────────────────────────
def build_submerged_stone_mat():
    mat = bpy.data.materials.new("Mat_UWRuins_SubmergedStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Metallic'].default_value  = 0.02
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-600, 200)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value   = 4.0
    mus.inputs['Detail'].default_value  = 8.0
    mus.inputs['Dimension'].default_value = 1.1
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.15, 0.18, 0.20, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.38, 0.42, 0.44, 1)
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-600,-100)
    noise.inputs['Scale'].default_value  = 16.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.65
    cr2  = ns.new('ShaderNodeValToRGB');       cr2.location  = (-300,-100)
    cr2.color_ramp.elements[0].position = 0.3
    cr2.color_ramp.elements[0].color = (0.08, 0.12, 0.14, 1)
    cr2.color_ramp.elements[1].position = 0.85
    cr2.color_ramp.elements[1].color = (0.25, 0.30, 0.32, 1)
    mix  = ns.new('ShaderNodeMixRGB');         mix.location  = (50, 100)
    mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = 0.5
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.6
    bmp.inputs['Distance'].default_value = 0.04
    img_a = img_slot(ns,"[UNITY] SubmergedStone_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] SubmergedStone_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] SubmergedStone_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr1.inputs['Fac'])
    lk.new(noise.outputs['Fac'],   cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],     bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_barnacle_mat():
    mat = bpy.data.materials.new("Mat_UWRuins_Barnacle")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.90
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'
    vor.inputs['Scale'].default_value = 7.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.30, 0.28, 0.25, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.55, 0.50, 0.44, 1)
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-600,-100)
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 5.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 2.2
    bmp.inputs['Distance'].default_value = 0.06
    img_a = img_slot(ns,"[UNITY] Barnacle_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] Barnacle_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] Barnacle_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'], cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],    mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],  mix2.inputs['Color2'])
    lk.new(noise.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_seaweed_mat():
    mat = bpy.data.materials.new("Mat_UWRuins_Seaweed")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.75
    bsdf.inputs['Transmission Weight'].default_value = 0.25
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-500, 200)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value      = 8.0
    wave.inputs['Distortion'].default_value = 4.0
    wave.inputs['Detail'].default_value     = 5.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-200, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.02, 0.12, 0.05, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.06, 0.35, 0.15, 1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 0.6
    img_a = img_slot(ns,"[UNITY] Seaweed_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] Seaweed_Normal", -660,-550)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(wave.outputs['Fac'],    cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_coral_mat():
    mat = bpy.data.materials.new("Mat_UWRuins_Coral")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.65
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'
    vor.inputs['Scale'].default_value = 5.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.7, 0.25, 0.15, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.9, 0.55, 0.35, 1)
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-600,-100)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 5.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.8
    bmp.inputs['Distance'].default_value = 0.05
    img_a = img_slot(ns,"[UNITY] Coral_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] Coral_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] Coral_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'], cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],    mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],  mix2.inputs['Color2'])
    lk.new(noise.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_silt_floor_mat():
    mat = bpy.data.materials.new("Mat_UWRuins_Silt")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.98
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-550, 200)
    mus.musgrave_type = 'FBM'
    mus.inputs['Scale'].default_value  = 2.5
    mus.inputs['Detail'].default_value = 8.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-250, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.18, 0.20, 0.22, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.35, 0.38, 0.40, 1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 0.6
    bmp.inputs['Distance'].default_value = 0.03
    img_a = img_slot(ns,"[UNITY] SiltFloor_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] SiltFloor_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] SiltFloor_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],     bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_caustic_mat():
    mat = bpy.data.materials.new("Mat_UWRuins_Caustic")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Alpha'].default_value = 0.0
    mat.blend_method = 'BLEND'
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.4, 0.9, 1.0, 1)
    em.inputs['Strength'].default_value = 1.5
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-500, 0)
    vor.voronoi_dimensions = '3D'
    vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-250, 0)
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (1,1,1,1)
    cr.color_ramp.elements[1].position = 0.15;cr.color_ramp.elements[1].color = (0,0,0,1)
    img_e = img_slot(ns,"[UNITY] Caustic_Emission", -660,-350)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_biolum_jelly_mat():
    mat = bpy.data.materials.new("Mat_UWRuins_Jellyfish")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Transmission Weight'].default_value = 0.90
    bsdf.inputs['IOR'].default_value = 1.35
    bsdf.inputs['Alpha'].default_value = 0.55
    mat.blend_method = 'BLEND'
    bsdf.inputs['Base Color'].default_value = (0.3, 0.7, 1.0, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.2, 0.8, 1.0, 1)
    em.inputs['Strength'].default_value = 4.0
    img_a = img_slot(ns,"[UNITY] Jellyfish_Albedo",   -400,-300)
    img_e = img_slot(ns,"[UNITY] Jellyfish_Emission", -400,-500)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_vent_mat():
    mat = bpy.data.materials.new("Mat_UWRuins_Vent")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.88
    bsdf.inputs['Base Color'].default_value = (0.06, 0.04, 0.04, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (1.0, 0.35, 0.05, 1)
    em.inputs['Strength'].default_value = 5.0
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-450, 0)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value  = 6.0
    mus.inputs['Detail'].default_value = 7.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.5; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_a = img_slot(ns,"[UNITY] Vent_Albedo",   -660,-350)
    img_e = img_slot(ns,"[UNITY] Vent_Emission", -660,-550)
    lk.new(mus.outputs['Fac'],     cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_rune_glow_mat():
    mat = bpy.data.materials.new("Mat_UWRuins_Rune")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.82
    bsdf.inputs['Emission Color'].default_value = (0.1, 0.8, 0.9, 1)
    bsdf.inputs['Emission Strength'].default_value = 3.0
    bsdf.inputs['Base Color'].default_value = (0.04, 0.08, 0.10, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.1, 0.85, 1.0, 1)
    em.inputs['Strength'].default_value = 6.0
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-450, 0)
    noise.inputs['Scale'].default_value = 7.0
    noise.inputs['Detail'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.4; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_a = img_slot(ns,"[UNITY] UWRune_Albedo",   -660,-350)
    img_e = img_slot(ns,"[UNITY] UWRune_Emission", -660,-550)
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

# ── geometry builders ─────────────────────────────────────────────────────────
def build_silt_floor(name, rx=20, ry=18, mat=None):
    bm = bmesh.new()
    segs_x, segs_y = 26, 22
    verts = []
    for iy in range(segs_y + 1):
        row = []
        for ix in range(segs_x + 1):
            fx = (ix / segs_x - 0.5) * 2 * rx
            fy = (iy / segs_y - 0.5) * 2 * ry
            fz = rng.uniform(-0.3, 0.3) + 0.4 * math.sin(fx * 0.25) * math.cos(fy * 0.25)
            row.append(bm.verts.new((fx, fy, fz)))
        verts.append(row)
    bm.verts.ensure_lookup_table()
    for iy in range(segs_y):
        for ix in range(segs_x):
            bm.faces.new([verts[iy][ix], verts[iy][ix+1],
                          verts[iy+1][ix+1], verts[iy+1][ix]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_sunken_column(name, height=5.0, radius=0.38, partial=1.0, mat=None):
    bm = bmesh.new()
    segs = 12; rings = 18
    verts_ring = []
    eff_h = height * partial
    for r in range(rings + 1):
        t = r / rings; z = t * eff_h
        ring = []
        for s in range(segs):
            ang = 2*math.pi*s/segs
            flute = 1.0 + 0.05 * math.cos(segs * 0.5 * ang)
            ring.append(bm.verts.new((radius*flute*math.cos(ang),
                                       radius*flute*math.sin(ang), z)))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    # base disc
    base_verts = [bm.verts.new((radius*1.3*math.cos(2*math.pi*s/segs),
                                 radius*1.3*math.sin(2*math.pi*s/segs), 0)) for s in range(segs)]
    bm.faces.new(base_verts[::-1])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_floor_slab(name, w=3.0, d=3.0, tilt_x=0.0, tilt_y=0.0, mat=None):
    bm = bmesh.new()
    segs_w, segs_d = 6, 6; thick = 0.35
    for iw in range(segs_w):
        for id2 in range(segs_d):
            x0 = (iw / segs_w - 0.5) * w
            x1 = ((iw+1) / segs_w - 0.5) * w
            y0 = (id2 / segs_d - 0.5) * d
            y1 = ((id2+1) / segs_d - 0.5) * d
            tilt_z = (x0 + x1) * 0.5 * math.tan(tilt_x) + (y0 + y1) * 0.5 * math.tan(tilt_y)
            pts_top = [(x0, y0, tilt_z + rng.uniform(-0.02, 0.02)),
                       (x1, y0, tilt_z + rng.uniform(-0.02, 0.02)),
                       (x1, y1, tilt_z + rng.uniform(-0.02, 0.02)),
                       (x0, y1, tilt_z + rng.uniform(-0.02, 0.02))]
            pts_bot = [(p[0], p[1], p[2] - thick) for p in pts_top]
            bv_t = [bm.verts.new(p) for p in pts_top]
            bv_b = [bm.verts.new(p) for p in pts_bot]
            bm.faces.new(bv_t)
            bm.faces.new(bv_b[::-1])
            for k in range(4):
                bm.faces.new([bv_t[k], bv_t[(k+1)%4], bv_b[(k+1)%4], bv_b[k]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_sunken_arch(name, span=4.5, height=5.5, mat=None):
    bm = bmesh.new()
    segs = 20
    def arch_pt(t):
        ang = math.pi * t
        return (span * 0.5 * math.cos(math.pi - ang), 0.0,
                height - span * 0.5 + span * 0.5 * math.sin(ang))
    for i in range(segs):
        t0 = i / segs; t1 = (i+1) / segs
        ox0, _, oz0 = arch_pt(t0)
        ox1, _, oz1 = arch_pt(t1)
        thick = 0.65
        pts = [(ox0, -thick, oz0), (ox0, thick, oz0),
               (ox1, thick, oz1), (ox1, -thick, oz1)]
        bm.faces.new([bm.verts.new(p) for p in pts])
    # pillars
    for px in [-span * 0.5, span * 0.5]:
        for rz in range(10):
            z0 = rz * (height - span * 0.5) / 9
            z1 = (rz+1) * (height - span * 0.5) / 9
            pr = 0.32
            pts_b = [bm.verts.new((px + pr*math.cos(2*math.pi*k/8),
                                    pr*math.sin(2*math.pi*k/8), z0)) for k in range(8)]
            pts_t = [bm.verts.new((px + pr*math.cos(2*math.pi*k/8),
                                    pr*math.sin(2*math.pi*k/8), z1)) for k in range(8)]
            for k in range(8):
                bm.faces.new([pts_b[k], pts_b[(k+1)%8], pts_t[(k+1)%8], pts_t[k]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_amphora(name, mat=None):
    bm = bmesh.new()
    profile = [(0.0,0),(0.18,0.1),(0.28,0.3),(0.22,0.7),(0.18,1.0),
               (0.20,1.2),(0.15,1.4),(0.08,1.55),(0.12,1.65),(0.08,1.8)]
    segs = 12
    verts_ring = []
    for pt in profile:
        r, z = pt
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs),
                               r*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(len(profile) - 1):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_seaweed_strand(name, height=2.5, segments=16, mat=None):
    bm = bmesh.new()
    for seg in range(segments):
        t0 = seg / segments; t1 = (seg+1) / segments
        z0 = t0 * height; z1 = t1 * height
        sway0 = 0.2 * math.sin(t0 * math.pi * 4)
        sway1 = 0.2 * math.sin(t1 * math.pi * 4)
        w = 0.06 * (1 - t0 * 0.5)
        v0 = bm.verts.new((sway0 - w, 0, z0))
        v1 = bm.verts.new((sway0 + w, 0, z0))
        v2 = bm.verts.new((sway1 + w, 0, z1))
        v3 = bm.verts.new((sway1 - w, 0, z1))
        bm.faces.new([v0, v1, v2, v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_coral_formation(name, branches=8, height=2.0, mat=None):
    bm = bmesh.new()
    # main trunk
    segs = 8; trunk_rings = 10
    verts_trunk = []
    for r in range(trunk_rings + 1):
        t = r / trunk_rings; z = t * height * 0.5
        tr = 0.12 * (1 - t * 0.4)
        ring = [bm.verts.new((tr*math.cos(2*math.pi*s/segs),
                               tr*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_trunk.append(ring)
    for r in range(trunk_rings):
        for s in range(segs):
            bm.faces.new([verts_trunk[r][s], verts_trunk[r][(s+1)%segs],
                          verts_trunk[r+1][(s+1)%segs], verts_trunk[r+1][s]])
    # branches
    for b in range(branches):
        bt = (b + 0.5) / branches
        bz = bt * height * 0.5
        ba = 2*math.pi*b/branches
        bl = height * 0.5 * math.sin(bt * math.pi) * rng.uniform(0.6, 1.0)
        bsegs2 = 8
        for bs in range(bsegs2):
            bt0 = bs / bsegs2; bt1 = (bs+1) / bsegs2
            bx0 = bl*bt0*math.cos(ba); by0 = bl*bt0*math.sin(ba)
            bx1 = bl*bt1*math.cos(ba); by1 = bl*bt1*math.sin(ba)
            bz0 = bz + bl * bt0 * 0.5; bz1 = bz + bl * bt1 * 0.5
            bw = 0.03 * (1 - bt0 * 0.7)
            v0 = bm.verts.new((bx0-bw, by0, bz0)); v1 = bm.verts.new((bx0+bw, by0, bz0))
            v2 = bm.verts.new((bx1+bw, by1, bz1)); v3 = bm.verts.new((bx1-bw, by1, bz1))
            bm.faces.new([v0, v1, v2, v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_jellyfish(name, loc, mat=None):
    bm = bmesh.new()
    # bell
    bell_segs = 16; bell_rings = 10
    verts_bell = []
    for r in range(bell_rings + 1):
        t = r / bell_rings
        z = t * 0.8
        bell_r = 0.55 * math.sin(t * math.pi * 0.6) * (1 + 0.05 * math.sin(t * math.pi * 4))
        ring = [bm.verts.new((bell_r*math.cos(2*math.pi*s/bell_segs),
                               bell_r*math.sin(2*math.pi*s/bell_segs), z)) for s in range(bell_segs)]
        verts_bell.append(ring)
    for r in range(bell_rings):
        for s in range(bell_segs):
            bm.faces.new([verts_bell[r][s], verts_bell[r][(s+1)%bell_segs],
                          verts_bell[r+1][(s+1)%bell_segs], verts_bell[r+1][s]])
    # tentacles
    for t2 in range(8):
        ta = 2*math.pi*t2/8
        tr2 = 0.3
        tlen = rng.uniform(1.0, 2.0)
        tsegs = 14
        for ts in range(tsegs):
            tt0 = ts / tsegs; tt1 = (ts+1) / tsegs
            tz0 = -tt0 * tlen; tz1 = -tt1 * tlen
            tsway = 0.1 * math.sin(tt0 * math.pi * 3 + t2)
            tw = 0.012 * (1 - tt0 * 0.8)
            tx0 = tr2*math.cos(ta) + tsway
            ty0 = tr2*math.sin(ta)
            v0 = bm.verts.new((tx0-tw, ty0, tz0)); v1 = bm.verts.new((tx0+tw, ty0, tz0))
            v2 = bm.verts.new((tx0+tw, ty0, tz1)); v3 = bm.verts.new((tx0-tw, ty0, tz1))
            bm.faces.new([v0, v1, v2, v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_vent_chimney(name, height=3.0, mat=None):
    bm = bmesh.new()
    segs = 10; rings = 16
    verts_ring = []
    for r in range(rings + 1):
        t = r / rings; z = t * height
        base_r = 0.40 + 0.12 * math.sin(t * math.pi * 3)
        ring = [bm.verts.new((base_r*math.cos(2*math.pi*s/segs + rng.uniform(-0.1,0.1)),
                               base_r*math.sin(2*math.pi*s/segs + rng.uniform(-0.1,0.1)), z))
                for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_caustic_plane(name, w=14, d=12, mat=None):
    bm = bmesh.new()
    segs_w, segs_d = 10, 8
    verts = []
    for iy in range(segs_d + 1):
        row = []
        for ix in range(segs_w + 1):
            fx = (ix / segs_w - 0.5) * w
            fy = (iy / segs_d - 0.5) * d
            row.append(bm.verts.new((fx, fy, 0.01)))
        verts.append(row)
    bm.verts.ensure_lookup_table()
    for iy in range(segs_d):
        for ix in range(segs_w):
            bm.faces.new([verts[iy][ix], verts[iy][ix+1],
                          verts[iy+1][ix+1], verts[iy+1][ix]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_broken_statue(name, mat=None):
    bm = bmesh.new()
    # torso block
    ts = 0.55; th = 1.8
    tv = [bm.verts.new(c) for c in [
        (-ts,-ts*0.7,0),(ts,-ts*0.7,0),(ts,ts*0.7,0),(-ts,ts*0.7,0),
        (-ts*0.8,-ts*0.6,th),(ts*0.8,-ts*0.6,th),(ts*0.8,ts*0.6,th),(-ts*0.8,ts*0.6,th)]]
    for f in [(0,1,2,3),(4,5,6,7),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([tv[i] for i in f])
    # rough broken neck
    neck_segs = 8
    neck_verts = [bm.verts.new((0.2*math.cos(2*math.pi*s/neck_segs + rng.uniform(-0.2,0.2)),
                                 0.2*math.sin(2*math.pi*s/neck_segs + rng.uniform(-0.2,0.2)),
                                 th + rng.uniform(-0.1, 0.1))) for s in range(neck_segs)]
    bm.faces.new(neck_verts)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_bubble(name, loc, mat=None):
    bm = bmesh.new()
    r = rng.uniform(0.04, 0.12)
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=r)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    if mat: assign_mat(obj, mat)
    return obj

# ── scene assembly ────────────────────────────────────────────────────────────
def build_scene():
    for o in list(bpy.data.objects):   bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):    bpy.data.meshes.remove(m, do_unlink=True)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m, do_unlink=True)

    col = bpy.data.collections.new("UnderwaterRuins")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'stone':    build_submerged_stone_mat(),
        'barnacle': build_barnacle_mat(),
        'seaweed':  build_seaweed_mat(),
        'coral':    build_coral_mat(),
        'silt':     build_silt_floor_mat(),
        'caustic':  build_caustic_mat(),
        'jelly':    build_biolum_jelly_mat(),
        'vent':     build_vent_mat(),
        'rune':     build_rune_glow_mat(),
    }

    objs = []

    # silt ground
    floor = build_silt_floor("UW_SiltFloor", 22, 18, mats['silt'])
    link(col, floor); objs.append(floor)

    # caustic light planes at multiple heights
    for ci, (cz, cw, cd) in enumerate([(0.5,16,14),(2.0,12,10),(4.0,10,8)]):
        cp = build_caustic_plane(f"UW_Caustic_{ci:02d}", cw, cd, mats['caustic'])
        cp.location = (rng.uniform(-2,2), rng.uniform(-2,2), cz)
        link(col, cp); objs.append(cp)
    add_pt_light(col, (0, 0, 8), energy=15.0, color=(0.4, 0.9, 1.0), radius=3.0)

    # floor slabs
    slab_cfgs = [
        ("UW_Slab_A",  3.0, 3.0, -0.05,  0.04,  ( 0, 0, 0)),
        ("UW_Slab_B",  2.8, 2.5,  0.04, -0.06,  ( 3.5, 0, -0.1)),
        ("UW_Slab_C",  3.2, 2.8, -0.06,  0.03,  (-3.5, 0, -0.15)),
        ("UW_Slab_D",  2.5, 3.0,  0.05,  0.05,  ( 0, 3.5, -0.08)),
        ("UW_Slab_E",  2.6, 2.4, -0.03, -0.07,  ( 0,-3.5, -0.12)),
        ("UW_Slab_F",  3.0, 2.8,  0.08, -0.04,  ( 7, 4, -0.2)),
        ("UW_Slab_G",  2.4, 3.2, -0.07,  0.06,  (-7,-4, -0.25)),
        ("UW_Slab_H",  2.8, 2.6,  0.04,  0.08,  ( 7,-4, -0.18)),
    ]
    for sname, sw, sd, stx, sty, sloc in slab_cfgs:
        sl = build_floor_slab(sname, sw, sd, stx, sty, mats['stone'])
        sl.location = sloc
        link(col, sl); objs.append(sl)

    # columns (rows)
    col_cfgs = [
        (-6, -8, 0, 4.5, 1.0), (-3, -8, 0, 5.2, 0.9), ( 0, -8, 0, 4.8, 1.0),
        ( 3, -8, 0, 5.5, 0.8), ( 6, -8, 0, 4.2, 1.0),
        (-6,  8, 0, 5.0, 1.0), (-3,  8, 0, 4.6, 0.85),( 0,  8, 0, 5.3, 1.0),
        ( 3,  8, 0, 4.9, 0.75),( 6,  8, 0, 5.1, 1.0),
    ]
    for ci, (cx, cy, cz, ch, cp) in enumerate(col_cfgs):
        c_obj = build_sunken_column(f"UW_Column_{ci:02d}", ch, 0.36, cp, mats['barnacle'])
        c_obj.location = (cx, cy, cz)
        link(col, c_obj); objs.append(c_obj)

    # arches
    arch_cfgs = [
        ("UW_Arch_A", ( 0, 0, 0), (0, 0, 0)),
        ("UW_Arch_B", ( 0, 8, 0), (0, 0, 0)),
        ("UW_Arch_C", ( 8, 0, 0), (0, 0, math.pi/2)),
        ("UW_Arch_D", (-8, 0, 0), (0, 0, math.pi/2)),
    ]
    for aname, aloc, arot in arch_cfgs:
        arch = build_sunken_arch(aname, 4.5, 5.5, mats['stone'])
        arch.location = aloc; arch.rotation_euler = arot
        link(col, arch); objs.append(arch)

    # rune-lit central altar slab
    altar = build_floor_slab("UW_Altar_Rune", 4.0, 4.0, 0.0, 0.0, mats['rune'])
    altar.location = (0, 0, 0.05)
    link(col, altar); objs.append(altar)
    add_pt_light(col, (0, 0, 0.6), energy=10.0, color=(0.1, 0.85, 1.0), radius=0.8)

    # seaweed forests
    sw_locs = [
        (5, 5), (-5, 6), (8, -3), (-8, -4), (3, -8), (-3, 9),
        (10, 2), (-10, 3), (6, 10), (-6, -10)
    ]
    for si, (swx, swy) in enumerate(sw_locs):
        for strand in range(rng.randint(4, 8)):
            swh = rng.uniform(1.5, 3.5)
            sw = build_seaweed_strand(f"UW_Seaweed_{si:02d}_S{strand}", swh, 16, mats['seaweed'])
            sw.location = (swx + rng.uniform(-0.6, 0.6), swy + rng.uniform(-0.6, 0.6), 0)
            link(col, sw); objs.append(sw)

    # coral formations
    coral_cfgs = [
        ("UW_Coral_A", ( 9, 5, 0), 10, 2.0),
        ("UW_Coral_B", (-9, 6, 0),  8, 1.8),
        ("UW_Coral_C", ( 9,-6, 0), 12, 2.4),
        ("UW_Coral_D", (-9,-5, 0),  9, 2.1),
        ("UW_Coral_E", ( 3, 0, 0),  6, 1.5),
        ("UW_Coral_F", (-4, 0, 0),  7, 1.6),
    ]
    for cname, cloc, cbranches, cheight in coral_cfgs:
        cr = build_coral_formation(cname, cbranches, cheight, mats['coral'])
        cr.location = cloc
        link(col, cr); objs.append(cr)

    # amphorae / pots scattered
    pot_locs = [(2,2,0),(4,-2,0),(-2,4,0),(-4,-1,0),(1,-4,0),(6,3,0),(-6,-2,0),(3,7,0)]
    for pi, ploc in enumerate(pot_locs):
        pot = build_amphora(f"UW_Amphora_{pi:02d}", mats['barnacle'])
        pot.location = ploc
        pot.rotation_euler = (rng.uniform(-0.3,0.3), rng.uniform(-0.3,0.3), rng.uniform(0, math.pi*2))
        link(col, pot); objs.append(pot)

    # broken statues
    statue_cfgs = [
        ("UW_Statue_A", (-4, -7, 0), (0.1, 0, 0.4)),
        ("UW_Statue_B", ( 5,  6, 0), (0.2, 0, 1.2)),
        ("UW_Statue_C", (-6,  4, 0), (0.3, 0.1, 2.1)),
    ]
    for stname, stloc, strot in statue_cfgs:
        st = build_broken_statue(stname, mats['stone'])
        st.location = stloc; st.rotation_euler = strot
        link(col, st); objs.append(st)

    # sea vent chimneys
    vent_cfgs = [
        ("UW_Vent_A", (12, 3, 0), 3.5),
        ("UW_Vent_B", (-12,-5, 0), 4.0),
        ("UW_Vent_C", ( 8,-12, 0), 2.8),
    ]
    for vname, vloc, vheight in vent_cfgs:
        vt = build_vent_chimney(vname, vheight, mats['vent'])
        vt.location = vloc
        link(col, vt); objs.append(vt)
        add_pt_light(col, (vloc[0], vloc[1], vheight),
                     energy=rng.uniform(8, 16), color=(1.0, 0.35, 0.05), radius=0.5)

    # jellyfish
    jelly_locs = [
        (3, 2, 5.0), (-4, 3, 6.5), (2,-4, 4.5), (-3,-2, 7.0),
        (5, 0, 5.5), (-5, 1, 6.0), (0, 5, 5.8), (1,-6, 4.8),
    ]
    for ji, jloc in enumerate(jelly_locs):
        jf = build_jellyfish(f"UW_Jellyfish_{ji:02d}", jloc, mats['jelly'])
        link(col, jf); objs.append(jf)
        add_pt_light(col, jloc, energy=rng.uniform(2, 5), color=(0.2, 0.8, 1.0), radius=0.2)

    # bubble particles
    bubble_locs = [
        (12, 3, 1.2), (12, 3, 2.0), (12, 3, 3.0),
        (-12,-5, 0.8),(-12,-5, 1.6),(-12,-5, 2.8),
        ( 8,-12, 1.0),( 8,-12, 2.2),( 8,-12, 3.5),
    ]
    for bi, bloc in enumerate(bubble_locs):
        bb = build_bubble(f"UW_Bubble_{bi:02d}", bloc, mats['jelly'])
        link(col, bb); objs.append(bb)

    # ambient underwater blue light
    add_pt_light(col, (0, 0, 15), energy=5.0, color=(0.1, 0.5, 1.0), radius=4.0)

    print(f"[UnderwaterRuins] Built {len(objs)} objects.")
    print("Export: File → Export → FBX, apply modifiers and transforms.")

build_scene()
