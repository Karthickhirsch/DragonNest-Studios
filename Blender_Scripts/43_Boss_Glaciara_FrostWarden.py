"""
43_Boss_Glaciara_FrostWarden.py
IsleTrial — Glaciara the Frost Warden (Frost Isle Boss)
================================================
Towering ice elemental boss: 3.8m humanoid warden clad in massive
frost-crystal armour plates, with a crown of 8 ice spires,
glowing blue core, frozen cape, and heavy fist-club hands.
Phase 3 creates a blizzard aura and fires homing ice spears.

Visual design:
  Torso    — hulking armoured barrel, glowing core slit on chest
  Shoulders— two massive pauldrons with crystal spikes
  Arms     — thick ice-armoured upper/lower, no fingers (fist clubs)
  Legs     — heavy pillar legs, cracked ice knee guards
  Head     — featureless face-plate, hollow glowing eye sockets
  Crown    — 8 ice spires radiating from brow
  Cape     — jagged frozen cape trailing from shoulders
  Weapons  — ice shard (projectile) + ice spear (homing) prefabs
  Ice wall — separate prefab slab

All materials: full procedural node networks + [UNITY] image slots
Armature: Root + Spine(4) + Head + Neck + L/R Arm(upper/lower/fist)
          + L/R Leg(upper/lower/foot) + Cape(3 panels)
UV: smart_project on every mesh
Run in Blender >= 3.6
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(430043)

def ns_lk(mat): return mat.node_tree.nodes, mat.node_tree.links
def img_slot(ns, name, x, y):
    n = ns.new('ShaderNodeTexImage'); n.label = name; n.location = (x, y); return n
def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
def assign_mat(obj, mat): obj.data.materials.clear(); obj.data.materials.append(mat)
def link(col, obj):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)
def add_pt_light(col, loc, energy, color, radius=0.2):
    bpy.ops.object.light_add(type='POINT', location=loc)
    lt = bpy.context.active_object
    lt.data.energy = energy; lt.data.color = color; lt.data.shadow_soft_size = radius
    col.objects.link(lt)
    if lt.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(lt)
    return lt

# ── materials ─────────────────────────────────────────────────────────────────
def build_ice_armor_mat():
    mat = bpy.data.materials.new("Mat_Glaciara_IceArmor")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['Transmission Weight'].default_value = 0.55
    bsdf.inputs['IOR'].default_value = 1.52
    bsdf.inputs['Metallic'].default_value = 0.08
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 6.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.48,0.72,0.96,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.85,0.94,1.00,1)
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-600,-100)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value = 4.0; mus.inputs['Detail'].default_value = 8.0
    cr2  = ns.new('ShaderNodeValToRGB');       cr2.location  = (-300,-100)
    cr2.color_ramp.elements[0].position = 0.0; cr2.color_ramp.elements[0].color = (0.35,0.60,0.88,1)
    cr2.color_ramp.elements[1].position = 1.0; cr2.color_ramp.elements[1].color = (0.75,0.90,1.00,1)
    mix  = ns.new('ShaderNodeMixRGB');         mix.location  = (50, 100)
    mix.blend_type = 'SCREEN'; mix.inputs['Fac'].default_value = 0.4
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 2.5; bmp.inputs['Distance'].default_value = 0.06
    img_a = img_slot(ns,"[UNITY] Glaciara_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] Glaciara_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] Glaciara_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'], cr1.inputs['Fac'])
    lk.new(mus.outputs['Fac'],      cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],    mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],    mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],    mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],  mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],      bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_ice_core_mat():
    mat = bpy.data.materials.new("Mat_Glaciara_IceCore")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['Transmission Weight'].default_value = 0.95
    bsdf.inputs['IOR'].default_value = 1.45
    bsdf.inputs['Emission Color'].default_value = (0.2, 0.8, 1.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 6.0
    bsdf.inputs['Base Color'].default_value = (0.3, 0.8, 1.0, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.1, 0.75, 1.0, 1)
    em.inputs['Strength'].default_value = 14.0
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-450, 0)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 3.0; wave.inputs['Distortion'].default_value = 2.5
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.35;cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.75;cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] GlaciaraCore_Emission", -660,-350)
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_ice_crown_mat():
    mat = bpy.data.materials.new("Mat_Glaciara_Crown")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['Transmission Weight'].default_value = 0.80
    bsdf.inputs['IOR'].default_value = 1.55
    bsdf.inputs['Base Color'].default_value = (0.55, 0.88, 1.0, 1)
    bsdf.inputs['Emission Color'].default_value = (0.2, 0.8, 1.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 3.5
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.2, 0.85, 1.0, 1)
    em.inputs['Strength'].default_value = 6.0
    img_e = img_slot(ns,"[UNITY] GlaciaraCrown_Emission", -400,-300)
    img_a = img_slot(ns,"[UNITY] GlaciaraCrown_Albedo",   -400,-500)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_eye_glow_mat():
    mat = bpy.data.materials.new("Mat_Glaciara_Eye")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (700, 0)
    em   = ns.new('ShaderNodeEmission');       em.location   = (450, 0)
    em.inputs['Color'].default_value    = (0.2, 0.85, 1.0, 1)
    em.inputs['Strength'].default_value = 16.0
    img_e = img_slot(ns,"[UNITY] GlaciaraEye_Emission", -400,-200)
    lk.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

def build_frozen_cape_mat():
    mat = bpy.data.materials.new("Mat_Glaciara_FrozenCape")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.15
    bsdf.inputs['Transmission Weight'].default_value = 0.35
    bsdf.inputs['Base Color'].default_value = (0.55, 0.80, 0.96, 1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-500, 200)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 8.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-250, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.40,0.68,0.92,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.80,0.92,1.00,1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.8
    img_a = img_slot(ns,"[UNITY] FrozenCape_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] FrozenCape_Normal", -660,-550)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'], cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],    mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],  mix2.inputs['Color2'])
    lk.new(vor.outputs['Distance'], bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_ice_projectile_mat():
    mat = bpy.data.materials.new("Mat_Glaciara_IceProjectile")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.03
    bsdf.inputs['Transmission Weight'].default_value = 0.85
    bsdf.inputs['IOR'].default_value = 1.55
    bsdf.inputs['Base Color'].default_value = (0.5, 0.85, 1.0, 1)
    bsdf.inputs['Emission Color'].default_value = (0.2, 0.8, 1.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 4.0
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.2, 0.85, 1.0, 1)
    em.inputs['Strength'].default_value = 8.0
    img_e = img_slot(ns,"[UNITY] IceProj_Emission", -400,-300)
    img_a = img_slot(ns,"[UNITY] IceProj_Albedo",   -400,-500)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_ice_wall_mat():
    mat = bpy.data.materials.new("Mat_Glaciara_IceWall")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.06
    bsdf.inputs['Transmission Weight'].default_value = 0.70
    bsdf.inputs['IOR'].default_value = 1.50
    bsdf.inputs['Base Color'].default_value = (0.55, 0.82, 0.98, 1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 4.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 2.0
    img_a = img_slot(ns,"[UNITY] IceWall_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] IceWall_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] IceWall_Roughness", -660,-750)
    lk.new(vor.outputs['Distance'], bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

# ── geometry ──────────────────────────────────────────────────────────────────
def build_torso(name, mat=None):
    bm = bmesh.new(); segs = 16; rings = 20; height = 1.8
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t * height
        rx = 0.65 + 0.08*math.sin(t*math.pi)
        ry = 0.55 + 0.06*math.sin(t*math.pi)
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
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_pelvis(name, mat=None):
    bm = bmesh.new(); segs = 16; rings = 10; height = 0.9
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t*height
        rx = 0.72 - t*0.10; ry = 0.58 - t*0.08
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
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_head(name, mat=None):
    bm = bmesh.new(); segs = 14; rings = 18; head_h = 0.9
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t * head_h
        if t < 0.3:   rx = 0.38 + t*0.5; ry = 0.32 + t*0.4
        elif t < 0.7: rx = 0.53 + (t-0.3)*0.05; ry = 0.44
        else:         rt=(t-0.7)/0.3; rx=0.55*(1-rt*0.55); ry=0.44*(1-rt*0.55)
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
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_neck(name, mat=None):
    bm = bmesh.new(); segs = 12; rings = 10; neck_h = 0.55
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t*neck_h
        r = 0.38 - t*0.04
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
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_pauldron(name, side=1, mat=None):
    """Massive shoulder armour with crystal spike."""
    bm = bmesh.new(); segs = 14; rings = 12
    rx = 0.55; ry = 0.42; rz = 0.40
    all_rows = []
    for v in range(rings + 1):
        tv = v/rings; ang_v = tv*math.pi*0.6
        z = rz*math.sin(ang_v)
        r_u = rx*math.cos(ang_v*0.7); r_v = ry*math.cos(ang_v*0.7)
        row = [bm.verts.new((r_u*math.cos(2*math.pi*u/segs)*side,
                              r_v*math.sin(2*math.pi*u/segs), z)) for u in range(segs)]
        all_rows.append(row)
    bm.verts.ensure_lookup_table()
    for v in range(rings):
        for u in range(segs):
            bm.faces.new([all_rows[v][u], all_rows[v][(u+1)%segs],
                          all_rows[v+1][(u+1)%segs], all_rows[v+1][u]])
    bm.faces.new(all_rows[0][::-1])
    # crystal spike on top
    segs2 = 6; spike_h = 0.55
    for r in range(8+1):
        t = r/8; sz = t*spike_h
        sr = 0.08*(1-t*0.88)
        if sr < 0.005: sr = 0.005
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_upper_arm(name, mat=None):
    bm = bmesh.new(); segs = 12; rings = 14; arm_h = 0.80
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*arm_h
        r = 0.28 + 0.04*math.sin(t*math.pi)
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
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_forearm_fist(name, mat=None):
    """Combined forearm + fist club (no individual fingers)."""
    bm = bmesh.new(); segs = 12; rings = 22; arm_h = 1.0
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*arm_h
        if t < 0.55: r = 0.22 + 0.02*math.sin(t*math.pi*3)
        else:        r = 0.22 + (t-0.55)*0.8  # fist club expands
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs),
                               r*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    # fist cap
    bm.faces.new(verts_ring[rings][::-1])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_upper_leg(name, mat=None):
    bm = bmesh.new(); segs = 14; rings = 16; leg_h = 1.0
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*leg_h
        r = 0.38 + 0.06*math.sin(t*math.pi)
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
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_lower_leg_boot(name, mat=None):
    bm = bmesh.new(); segs = 14; rings = 20; leg_h = 1.0
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = -t*leg_h
        if t < 0.65: r = 0.32 + 0.03*math.sin(t*math.pi*4)
        else:        r = 0.32 + (t-0.65)*0.6  # boot flares out
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs),
                               r*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    bm.faces.new(verts_ring[rings][::-1])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_crown_spire(name, height=0.8, mat=None):
    bm = bmesh.new(); segs = 5; rings = 14
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*height
        radius = 0.055*(1-t*0.90)*(1+0.08*math.sin(t*math.pi*5))
        if radius < 0.005: radius = 0.005
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs),
                               radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0, 0, height+0.04))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_eye_socket(name, mat=None):
    bm = bmesh.new(); segs = 10
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=8, radius=0.10)
    for v in bm.verts:
        if v.co.y < 0: v.co.y *= 0.3  # flatten into head
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); return obj

def build_core_slit(name, mat=None):
    """Glowing chest core — elongated teardrop slot."""
    bm = bmesh.new(); segs = 12; rings = 14; height = 0.6
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*height
        if t < 0.2:  rx = 0.06*math.sin(t/0.2*math.pi*0.5); ry = 0.10*math.sin(t/0.2*math.pi*0.5)
        elif t < 0.8:belly=(t-0.2)/0.6; rx=0.06+0.04*math.sin(belly*math.pi); ry=0.10+0.06*math.sin(belly*math.pi)
        else:        rt=(t-0.8)/0.2; rx=0.06*(1-rt); ry=0.10*(1-rt)
        if rx < 0.005: rx = 0.005
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
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_frozen_cape_panel(name, w=0.55, h=1.2, mat=None):
    bm = bmesh.new(); segs_w = 6; segs_h = 14
    for iw in range(segs_w):
        for ih in range(segs_h):
            x0 = (iw/segs_w - 0.5)*w; x1 = ((iw+1)/segs_w - 0.5)*w
            z0 = -ih/segs_h*h; z1 = -(ih+1)/segs_h*h
            warp = 0.04*math.sin(iw*1.5 + ih*0.8)
            bm.faces.new([bm.verts.new(p) for p in [
                (x0, warp, z0),(x1, warp, z0),
                (x1, warp+0.01, z1),(x0, warp+0.01, z1)]])
    # jagged bottom edge
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ice_shard_projectile(name, mat=None):
    """Straight ice shard — Unity prefab."""
    bm = bmesh.new(); segs = 5; rings = 10; length = 0.45
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*length
        if t < 0.3: radius = 0.06*math.sin(t/0.3*math.pi*0.5)
        else:       radius = 0.06*(1-(t-0.3)/0.7)
        if radius < 0.005: radius = 0.005
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs),
                               radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0, 0, length+0.04))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ice_spear_projectile(name, mat=None):
    """Long homing ice spear — Unity prefab."""
    bm = bmesh.new(); segs = 6; rings = 16; length = 1.2
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*length
        if t < 0.2: radius = 0.085*math.sin(t/0.2*math.pi*0.5)
        elif t < 0.8: radius = 0.085 + 0.015*math.sin((t-0.2)/0.6*math.pi*2)
        else:       radius = 0.085*(1-(t-0.8)/0.2)
        if radius < 0.006: radius = 0.006
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs+rng.uniform(-0.05,0.05)),
                               radius*math.sin(2*math.pi*s/segs+rng.uniform(-0.05,0.05)), z))
                for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0, 0, length+0.08))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ice_wall_slab(name, mat=None):
    bm = bmesh.new(); segs_w = 8; segs_h = 14; w = 2.5; h = 3.5; thick = 0.35
    for iw in range(segs_w):
        for ih in range(segs_h):
            x0=(iw/segs_w-0.5)*w; x1=((iw+1)/segs_w-0.5)*w
            z0=ih/segs_h*h;       z1=(ih+1)/segs_h*h
            warp=0.06*math.sin(iw*1.2+ih*0.9)
            # front
            bm.faces.new([bm.verts.new(p) for p in [(x0,warp,z0),(x1,warp,z0),(x1,warp,z1),(x0,warp,z1)]])
            # back
            bm.faces.new([bm.verts.new(p) for p in [(x0,warp+thick,z0),(x0,warp+thick,z1),(x1,warp+thick,z1),(x1,warp+thick,z0)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

# ── armature ──────────────────────────────────────────────────────────────────
def build_armature(name, col):
    bpy.ops.object.armature_add(enter_editmode=True, location=(0,0,0))
    arm_obj = bpy.context.active_object; arm_obj.name = name
    arm = arm_obj.data; arm.name = name + "_Data"
    bpy.ops.armature.select_all(action='SELECT'); bpy.ops.armature.delete()
    eb = arm.edit_bones
    body_h = 0.95  # feet to hip
    bone_defs = [
        ("Root",      None,        (0,0,0),            (0,0,0.5)),
        ("Pelvis",    "Root",      (0,0,0.5),           (0,0,0.95)),
        ("Spine1",    "Pelvis",    (0,0,0.95),          (0,0,1.55)),
        ("Spine2",    "Spine1",    (0,0,1.55),          (0,0,2.10)),
        ("Spine3",    "Spine2",    (0,0,2.10),          (0,0,2.60)),
        ("Spine4",    "Spine3",    (0,0,2.60),          (0,0,2.95)),
        ("Neck",      "Spine4",    (0,0,2.95),          (0,0,3.35)),
        ("Head",      "Neck",      (0,0,3.35),          (0,0,4.10)),
        # Arms
        ("L_Shoulder","Spine4",   (-0.75,0,2.85),      (-1.30,0,2.65)),
        ("L_Upper",   "L_Shoulder",(-1.30,0,2.65),     (-1.30,0,1.92)),
        ("L_Lower",   "L_Upper",  (-1.30,0,1.92),      (-1.30,0,1.05)),
        ("R_Shoulder","Spine4",   ( 0.75,0,2.85),      ( 1.30,0,2.65)),
        ("R_Upper",   "R_Shoulder",( 1.30,0,2.65),     ( 1.30,0,1.92)),
        ("R_Lower",   "R_Upper",  ( 1.30,0,1.92),      ( 1.30,0,1.05)),
        # Legs
        ("L_ULeg",   "Pelvis",   (-0.42,0,0.95),      (-0.42,0,0.05)),
        ("L_LLeg",   "L_ULeg",   (-0.42,0,0.05),      (-0.42,0,-0.85)),
        ("R_ULeg",   "Pelvis",   ( 0.42,0,0.95),      ( 0.42,0,0.05)),
        ("R_LLeg",   "R_ULeg",   ( 0.42,0,0.05),      ( 0.42,0,-0.85)),
        # Cape
        ("Cape_L",   "Spine3",   (-0.65,0,2.45),      (-0.65,0,1.45)),
        ("Cape_C",   "Spine3",   ( 0.00,0,2.45),      ( 0.00,0,1.45)),
        ("Cape_R",   "Spine3",   ( 0.65,0,2.45),      ( 0.65,0,1.45)),
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

    col = bpy.data.collections.new("Glaciara_FrostWarden")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'armor':  build_ice_armor_mat(),
        'core':   build_ice_core_mat(),
        'crown':  build_ice_crown_mat(),
        'eye':    build_eye_glow_mat(),
        'cape':   build_frozen_cape_mat(),
        'proj':   build_ice_projectile_mat(),
        'wall':   build_ice_wall_mat(),
    }
    objs = []

    # body parts
    pelvis = build_pelvis("Glaciara_Pelvis", mats['armor']); pelvis.location=(0,0,0.95); link(col,pelvis); objs.append(pelvis)
    torso  = build_torso("Glaciara_Torso", mats['armor']);   torso.location=(0,0,1.75);  link(col,torso);  objs.append(torso)
    neck   = build_neck("Glaciara_Neck", mats['armor']);     neck.location=(0,0,3.48);   link(col,neck);   objs.append(neck)
    head   = build_head("Glaciara_Head", mats['armor']);     head.location=(0,0,3.88);   link(col,head);   objs.append(head)

    # glowing chest core
    core = build_core_slit("Glaciara_Core", mats['core']); core.location=(0,0.66,2.40); core.rotation_euler=(-math.pi/2,0,0)
    link(col,core); objs.append(core)
    add_pt_light(col,(0,0.68,2.70), energy=18.0, color=(0.2,0.8,1.0), radius=0.4)

    # pauldrons
    for side, sx, mat_s in [("L",-1.0, mats['armor']),("R", 1.0, mats['armor'])]:
        p = build_pauldron(f"Glaciara_Pauldron_{side}", side=1 if side=="L" else -1, mat=mat_s)
        p.location=(sx*1.18, 0, 2.85); link(col,p); objs.append(p)

    # arms
    for side, sx in [("L",-1.30),("R",1.30)]:
        ua = build_upper_arm(f"Glaciara_UpperArm_{side}", mats['armor']); ua.location=(sx,0,2.65); link(col,ua); objs.append(ua)
        fa = build_forearm_fist(f"Glaciara_ForearmFist_{side}", mats['armor']); fa.location=(sx,0,1.92); link(col,fa); objs.append(fa)

    # legs
    for side, sx in [("L",-0.42),("R",0.42)]:
        ul = build_upper_leg(f"Glaciara_UpperLeg_{side}", mats['armor']); ul.location=(sx,0,0.95); link(col,ul); objs.append(ul)
        ll = build_lower_leg_boot(f"Glaciara_LowerLeg_{side}", mats['armor']); ll.location=(sx,0,0.05); link(col,ll); objs.append(ll)

    # eye sockets
    for side, ex in [("L",-0.22),("R",0.22)]:
        eye = build_eye_socket(f"Glaciara_Eye_{side}", mats['eye']); eye.location=(ex,0.44,4.25)
        link(col,eye); objs.append(eye)
        add_pt_light(col,(ex,0.44,4.25), energy=8.0, color=(0.2,0.85,1.0), radius=0.08)

    # crown spires (8 around top of head)
    for ci in range(8):
        ang = 2*math.pi*ci/8
        cr_x = 0.38*math.cos(ang); cr_y = 0.38*math.sin(ang)
        cr_h = 0.60 + 0.20*math.sin(ci*2.3)
        sp = build_crown_spire(f"Glaciara_Crown_{ci:02d}", cr_h, mats['crown'])
        sp.location=(cr_x, cr_y, 4.65); sp.rotation_euler=(ang*0.25, 0, ang)
        link(col,sp); objs.append(sp)
        add_pt_light(col,(cr_x,cr_y,4.65+cr_h), energy=rng.uniform(2,4), color=(0.2,0.85,1.0), radius=0.08)

    # frozen cape panels
    cape_cfgs = [
        ("Glaciara_Cape_L", (-0.55, -0.70, 2.55), (0.15, 0, 0.25), 0.55, 1.4),
        ("Glaciara_Cape_C", ( 0.00, -0.72, 2.55), (0.12, 0, 0.0),  0.65, 1.6),
        ("Glaciara_Cape_R", ( 0.55, -0.70, 2.55), (0.15, 0,-0.25), 0.55, 1.4),
    ]
    for cname, cloc, crot, cw, ch in cape_cfgs:
        cp = build_frozen_cape_panel(cname, cw, ch, mats['cape'])
        cp.location=cloc; cp.rotation_euler=crot; link(col,cp); objs.append(cp)

    # projectile prefabs (offset — separate Unity prefabs)
    shard = build_ice_shard_projectile("Glaciara_IceShard_Prefab", mats['proj'])
    shard.location=(6, 0, 0); link(col,shard); objs.append(shard)
    add_pt_light(col,(6,0,0), energy=4.0, color=(0.2,0.85,1.0), radius=0.08)

    spear = build_ice_spear_projectile("Glaciara_IceSpear_Prefab", mats['proj'])
    spear.location=(8, 0, 0); link(col,spear); objs.append(spear)
    add_pt_light(col,(8,0,0.5), energy=5.0, color=(0.2,0.85,1.0), radius=0.12)

    wall = build_ice_wall_slab("Glaciara_IceWall_Prefab", mats['wall'])
    wall.location=(11, 0, 0); link(col,wall); objs.append(wall)

    # body ambient
    add_pt_light(col,(0,0,2.0), energy=4.0, color=(0.2,0.8,1.0), radius=1.5)

    # armature
    arm = build_armature("Glaciara_Armature", col)
    for obj in objs: obj.parent=arm; obj.modifiers.new("Armature",'ARMATURE').object=arm

    print(f"[Glaciara_FrostWarden] Built {len(objs)} mesh objects + 1 armature.")
    print("Prefabs to extract: IceShard (offset 6,0,0), IceSpear (8,0,0), IceWall (11,0,0)")
    print("Export: FBX with Armature + Mesh, Apply Transform")

build_scene()
