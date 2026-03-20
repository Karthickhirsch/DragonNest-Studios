"""
42_Boss_Ignar_MoltenDrake.py
IsleTrial — Ignar the Molten Drake (Ember Isle Boss)
================================================
Massive volcanic dragon boss that fires lava balls and breathes
fire.  Phase 1: lava ball volleys.  Phase 2+: raging fire breath.

Visual design:
  Body     — 5.5m long, powerful barrel torso, lava crack skin
  Neck     — thick, armoured, 1.2m
  Head     — enormous jaws, ram-horn crown, glowing eye sockets
  Legs     — 4 pillar legs with claw feet, lava glow joints
  Wings    — two large bone-membrane wings, 6m span each
  Tail     — heavy club tail, 2.2m, spine spikes
  Dorsal   — row of 10 jagged lava-glowing spine plates
  Lava Orb — separate projectile prefab (2 variants)

All materials: full procedural node networks + [UNITY] image slots
Armature: Root + Spine(6) + Neck + Head + Jaw + Tail(6) + 4 legs
          + Wing_L/R (base, mid, tip) + 10 dorsal plates
UV: smart_project on every mesh
Run in Blender >= 3.6
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(420042)

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
def add_pt_light(col, loc, energy, color, radius=0.3):
    bpy.ops.object.light_add(type='POINT', location=loc)
    lt = bpy.context.active_object
    lt.data.energy = energy; lt.data.color = color; lt.data.shadow_soft_size = radius
    col.objects.link(lt)
    if lt.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(lt)
    return lt

# ── materials ─────────────────────────────────────────────────────────────────
def build_molten_rock_mat():
    mat = bpy.data.materials.new("Mat_Ignar_MoltenRock")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (750, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 150)
    bsdf.inputs['Roughness'].default_value = 0.90
    bsdf.inputs['Metallic'].default_value  = 0.05
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.35, 0.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 0.8
    em   = ns.new('ShaderNodeEmission');       em.location   = (450,-150)
    em.inputs['Color'].default_value    = (1.0, 0.3, 0.0, 1)
    em.inputs['Strength'].default_value = 3.0
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'; vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 3.5
    cr_crack = ns.new('ShaderNodeValToRGB');   cr_crack.location = (-300, 200)
    cr_crack.color_ramp.elements[0].position = 0.0; cr_crack.color_ramp.elements[0].color = (1,1,1,1)
    cr_crack.color_ramp.elements[1].position = 0.12;cr_crack.color_ramp.elements[1].color = (0,0,0,1)
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-600,-100)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value = 4.5; mus.inputs['Detail'].default_value = 9.0
    cr_rock = ns.new('ShaderNodeValToRGB');    cr_rock.location = (-300,-100)
    cr_rock.color_ramp.elements[0].position = 0.0; cr_rock.color_ramp.elements[0].color = (0.04,0.02,0.01,1)
    cr_rock.color_ramp.elements[1].position = 1.0; cr_rock.color_ramp.elements[1].color = (0.14,0.06,0.02,1)
    mix  = ns.new('ShaderNodeMixRGB');         mix.location  = (50, 100)
    mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = 0.5
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (200, 280)
    bmp.inputs['Strength'].default_value = 2.2; bmp.inputs['Distance'].default_value = 0.06
    img_a = img_slot(ns,"[UNITY] Ignar_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] Ignar_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] Ignar_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (200, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'], cr_crack.inputs['Fac'])
    lk.new(cr_crack.outputs['Color'],em.inputs['Strength'])
    lk.new(mus.outputs['Fac'],       cr_rock.inputs['Fac'])
    lk.new(cr_rock.outputs['Color'], mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],   mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],       bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],    bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],    bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],     add.inputs[0])
    lk.new(em.outputs['Emission'],   add.inputs[1])
    lk.new(add.outputs['Shader'],    out.inputs['Surface'])
    return mat

def build_wing_membrane_mat():
    mat = bpy.data.materials.new("Mat_Ignar_WingMembrane")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Transmission Weight'].default_value = 0.45
    bsdf.inputs['Base Color'].default_value = (0.08, 0.03, 0.01, 1)
    bsdf.inputs['Emission Color'].default_value = (0.8, 0.2, 0.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 1.0
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (1.0, 0.3, 0.0, 1)
    em.inputs['Strength'].default_value = 2.0
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-500, 0)
    vor.voronoi_dimensions = '3D'; vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-250, 0)
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (1,1,1,1)
    cr.color_ramp.elements[1].position = 0.2; cr.color_ramp.elements[1].color = (0,0,0,1)
    img_a = img_slot(ns,"[UNITY] IgnarWing_Albedo",   -660,-350)
    img_e = img_slot(ns,"[UNITY] IgnarWing_Emission", -660,-550)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_lava_glow_mat():
    mat = bpy.data.materials.new("Mat_Ignar_LavaGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (700, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (520, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (280, 100)
    bsdf.inputs['Roughness'].default_value = 0.85; bsdf.inputs['Base Color'].default_value = (0.05,0.01,0.0,1)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.4, 0.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 5.0
    em   = ns.new('ShaderNodeEmission');       em.location   = (280,-100)
    em.inputs['Color'].default_value    = (1.0, 0.45, 0.0, 1)
    em.inputs['Strength'].default_value = 10.0
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-400, 0)
    noise.inputs['Scale'].default_value = 8.0; noise.inputs['Detail'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-150, 0)
    cr.color_ramp.elements[0].position = 0.4; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] IgnarGlow_Emission", -450,-300)
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_eye_fire_mat():
    mat = bpy.data.materials.new("Mat_Ignar_Eye")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (700, 0)
    em   = ns.new('ShaderNodeEmission');       em.location   = (450, 0)
    em.inputs['Color'].default_value    = (1.0, 0.55, 0.0, 1)
    em.inputs['Strength'].default_value = 18.0
    img_e = img_slot(ns,"[UNITY] IgnarEye_Emission", -400,-200)
    lk.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

def build_horn_mat():
    mat = bpy.data.materials.new("Mat_Ignar_Horn")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.70
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-500, 200)
    mus.inputs['Scale'].default_value = 6.0; mus.inputs['Detail'].default_value = 6.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-200, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.04,0.02,0.01,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.22,0.10,0.04,1)
    img_a = img_slot(ns,"[UNITY] IgnarHorn_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] IgnarHorn_Normal", -660,-550)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_lava_ball_mat():
    mat = bpy.data.materials.new("Mat_Ignar_LavaBall")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.88; bsdf.inputs['Base Color'].default_value = (0.05,0.02,0.0,1)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.45, 0.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 6.0
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (1.0, 0.35, 0.0, 1)
    em.inputs['Strength'].default_value = 12.0
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-500, 0)
    vor.voronoi_dimensions = '3D'; vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-250, 0)
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (1,1,1,1)
    cr.color_ramp.elements[1].position = 0.15;cr.color_ramp.elements[1].color = (0,0,0,1)
    img_e = img_slot(ns,"[UNITY] LavaBall_Emission", -660,-350)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

# ── geometry ──────────────────────────────────────────────────────────────────
def build_body(name, mat=None):
    bm = bmesh.new(); segs_l = 24; segs_r = 18; body_len = 5.5
    verts_ring = []
    for i in range(segs_l + 1):
        t = i / segs_l; z = t * body_len - 1.0
        if t < 0.15:   rx = 0.50 + t*0.8;  ry = 0.42 + t*0.5
        elif t < 0.75: belly_t=(t-0.15)/0.6; rx=0.72+0.30*math.sin(belly_t*math.pi); ry=0.58+0.20*math.sin(belly_t*math.pi)
        else:          rt=(t-0.75)/0.25;  rx=0.90*(1-rt*0.65); ry=0.72*(1-rt*0.65)
        if rx < 0.05: rx = 0.05
        ring = []
        for s in range(segs_r):
            ang = 2*math.pi*s/segs_r
            bx = rx*math.cos(ang)
            by = ry*math.sin(ang)*(0.70 if math.sin(ang) < 0 else 1.0)
            ring.append(bm.verts.new((bx, by, z + rng.uniform(-0.015,0.015))))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(segs_l):
        for s in range(segs_r):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs_r],
                          verts_ring[i+1][(s+1)%segs_r], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_neck(name, mat=None):
    bm = bmesh.new(); segs = 14; rings = 18; neck_len = 1.6
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t * neck_len
        sway = 0.15 * math.sin(t * math.pi * 1.2)
        r = 0.58 - t * 0.12
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs)+sway*0.3,
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

def build_head(name, mat=None):
    bm = bmesh.new(); segs = 16; rings = 22; head_len = 1.5
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t * head_len
        if t < 0.25:   rx = 0.45 + t * 1.2; ry = 0.38 + t * 0.8
        elif t < 0.65: rx = 0.75 + (t-0.25)*0.2; ry = 0.58 + (t-0.25)*0.05
        else:          rt=(t-0.65)/0.35; rx=0.83*(1-rt*0.9); ry=0.62*(1-rt*0.9)
        ring = []
        for s in range(segs):
            ang = 2*math.pi*s/segs
            # boss head is wider than tall, with prominent brow ridge
            bx = rx * math.cos(ang)
            by = ry * math.sin(ang) * (0.55 if math.sin(ang) < 0 else 1.15)
            ring.append(bm.verts.new((bx, by, z)))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    tip = bm.verts.new((0, 0, head_len + 0.12))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_lower_jaw(name, mat=None):
    bm = bmesh.new(); segs = 14; rings = 14; jaw_len = 1.1
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t * jaw_len
        rx = 0.65*(1-t*0.85); ry = 0.20*(1-t*0.75)
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

def build_horn(name, length=1.0, mat=None):
    bm = bmesh.new(); segs = 6; rings = 16
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t * length
        curve = 0.22 * math.sin(t * math.pi)
        radius = 0.12*(1-t*0.88)*(1 + 0.06*math.sin(t*math.pi*4))
        if radius < 0.008: radius = 0.008
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs) + curve,
                               radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0.22, 0, length + 0.05))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_eye(name, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=10, radius=0.18)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); return obj

def build_leg(name, upper_len=0.9, lower_len=0.7, mat=None):
    bm = bmesh.new(); segs = 12
    # upper
    for ring in range(12):
        t0 = ring/11; t1 = (ring+1)/11
        z0 = -t0*upper_len; z1 = -t1*upper_len
        r = 0.28*(1-t0*0.25)
        pts_b = [bm.verts.new((r*math.cos(2*math.pi*s/segs), r*math.sin(2*math.pi*s/segs), z0)) for s in range(segs)]
        pts_t = [bm.verts.new((r*math.cos(2*math.pi*s/segs), r*math.sin(2*math.pi*s/segs), z1)) for s in range(segs)]
        for s in range(segs):
            bm.faces.new([pts_b[s], pts_b[(s+1)%segs], pts_t[(s+1)%segs], pts_t[s]])
    # knee joint glow sphere
    knee_segs = 8
    kz = -upper_len
    kv = [bm.verts.new((0.32*math.cos(2*math.pi*s/knee_segs),
                         0.32*math.sin(2*math.pi*s/knee_segs), kz)) for s in range(knee_segs)]
    # lower
    for ring in range(12):
        t0 = ring/11; t1 = (ring+1)/11
        z0 = kz - t0*lower_len*0.85
        z1 = kz - t1*lower_len*0.85
        x0 = t0*lower_len*0.50; x1 = t1*lower_len*0.50
        r = 0.22*(1-t0*0.3)
        pts_b = [bm.verts.new((x0+r*math.cos(2*math.pi*s/segs), r*math.sin(2*math.pi*s/segs), z0)) for s in range(segs)]
        pts_t = [bm.verts.new((x1+r*math.cos(2*math.pi*s/segs), r*math.sin(2*math.pi*s/segs), z1)) for s in range(segs)]
        for s in range(segs):
            bm.faces.new([pts_b[s], pts_b[(s+1)%segs], pts_t[(s+1)%segs], pts_t[s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_claw(name, mat=None):
    bm = bmesh.new(); segs = 6; rings = 10; cl = 0.35
    verts_ring = []
    for r in range(rings+1):
        t = r/rings; z = t*cl
        radius = 0.06*(1-t*0.90)*(1+0.05*math.sin(t*math.pi*3))
        if radius < 0.004: radius = 0.004
        curve = 0.08*math.sin(t*math.pi)
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs)+curve,
                               radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0.08, 0, cl+0.06))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_wing(name, span=6.0, side=1, mat=None):
    """Wing with 4 bone fingers and membrane between them."""
    bm = bmesh.new(); x_dir = side
    # wing base spine
    spine_pts = [(0, 0, 0), (span*0.3*x_dir, 0.1, span*0.15),
                 (span*0.6*x_dir, 0.2, span*0.25), (span*0.9*x_dir, 0.1, span*0.18)]
    # 4 finger bones
    fingers = [
        [(span*0.3*x_dir, 0.1, span*0.15), (span*0.55*x_dir, 0.25, span*0.50)],
        [(span*0.3*x_dir, 0.1, span*0.15), (span*0.62*x_dir, 0.15, span*0.38)],
        [(span*0.4*x_dir, 0.2, span*0.22), (span*0.75*x_dir, 0.12, span*0.28)],
        [(span*0.5*x_dir, 0.2, span*0.25), (span*0.90*x_dir, 0.08, span*0.18)],
    ]
    wing_verts = []
    # draw membrane between spine and fingers
    base_w = 0.04
    for fi, (f_start, f_end) in enumerate(fingers):
        segs = 12
        for seg in range(segs):
            t0 = seg/segs; t1 = (seg+1)/segs
            p0 = (f_start[0]+t0*(f_end[0]-f_start[0]),
                  f_start[1]+t0*(f_end[1]-f_start[1]),
                  f_start[2]+t0*(f_end[2]-f_start[2]))
            p1 = (f_start[0]+t1*(f_end[0]-f_start[0]),
                  f_start[1]+t1*(f_end[1]-f_start[1]),
                  f_start[2]+t1*(f_end[2]-f_start[2]))
            w = base_w*(1+t0*2)
            v0=bm.verts.new((p0[0]-w*0.5, p0[1]-w, p0[2]))
            v1=bm.verts.new((p0[0]+w*0.5, p0[1]+w, p0[2]))
            v2=bm.verts.new((p1[0]+w*0.5, p1[1]+w, p1[2]))
            v3=bm.verts.new((p1[0]-w*0.5, p1[1]-w, p1[2]))
            bm.faces.new([v0,v1,v2,v3])
    # membrane surface (simplified)
    tips = [fingers[fi][1] for fi in range(4)]
    base = (0, 0, 0)
    for ti in range(len(tips)-1):
        segs_m = 10
        for s in range(segs_m):
            t0 = s/segs_m; t1 = (s+1)/segs_m
            p_a0 = (base[0]+t0*(tips[ti][0]-base[0]), base[1]+t0*(tips[ti][1]-base[1]),
                    base[2]+t0*(tips[ti][2]-base[2]))
            p_a1 = (base[0]+t1*(tips[ti][0]-base[0]), base[1]+t1*(tips[ti][1]-base[1]),
                    base[2]+t1*(tips[ti][2]-base[2]))
            p_b0 = (base[0]+t0*(tips[ti+1][0]-base[0]), base[1]+t0*(tips[ti+1][1]-base[1]),
                    base[2]+t0*(tips[ti+1][2]-base[2]))
            p_b1 = (base[0]+t1*(tips[ti+1][0]-base[0]), base[1]+t1*(tips[ti+1][1]-base[1]),
                    base[2]+t1*(tips[ti+1][2]-base[2]))
            bm.faces.new([bm.verts.new(p) for p in [p_a0, p_a1, p_b1, p_b0]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_tail(name, mat=None):
    bm = bmesh.new(); segs = 12; rings = 30; tail_len = 2.8
    verts_ring = []
    for i in range(rings + 1):
        t = i/rings; z = t * tail_len
        if t < 0.3: r = 0.68 - t * 0.3
        else:       r = 0.59*(1 - (t-0.3)/0.7)**1.4
        if r < 0.015: r = 0.015
        sway = 0.30 * math.sin(t * math.pi * 2.5)
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs)+sway*0.35,
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

def build_dorsal_plate(name, height=0.6, width=0.25, mat=None):
    bm = bmesh.new(); segs = 8; rings = 14
    verts_ring = []
    for r in range(rings+1):
        t = r/rings; z = t * height
        # spear-shaped profile
        if t < 0.4: rw = width*0.5*math.sin(t/0.4*math.pi*0.5)
        else:       rw = width*0.5*(1-(t-0.4)/0.6)**0.7
        if rw < 0.005: rw = 0.005
        rd = rw * 0.35
        ring = [bm.verts.new((rw*math.cos(2*math.pi*s/segs),
                               rd*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0, 0, height+0.06))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_lava_ball(name, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=12, radius=0.35)
    # noise deform
    for v in bm.verts:
        nz = rng.uniform(-0.04, 0.04)
        v.co.x += rng.uniform(-0.04, 0.04)
        v.co.y += rng.uniform(-0.04, 0.04)
        v.co.z += nz
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
    bone_defs = [
        ("Root",     None,       (0,0,0),     (0,0,0.5)),
        ("Spine1",   "Root",     (0,0,0.5),   (0,0,1.2)),
        ("Spine2",   "Spine1",   (0,0,1.2),   (0,0,2.0)),
        ("Spine3",   "Spine2",   (0,0,2.0),   (0,0,2.8)),
        ("Spine4",   "Spine3",   (0,0,2.8),   (0,0,3.5)),
        ("Spine5",   "Spine4",   (0,0,3.5),   (0,0,4.2)),
        ("Spine6",   "Spine5",   (0,0,4.2),   (0,0,4.7)),
        ("Neck",     "Spine6",   (0,0,4.7),   (0,0,5.6)),
        ("Head",     "Neck",     (0,0,5.6),   (0,0,7.0)),
        ("LowerJaw", "Head",     (0,-0.5,5.8),(0,-0.5,4.8)),
        ("Tail1",    "Root",     (0,0,0.0),   (0,0,-0.55)),
        ("Tail2",    "Tail1",    (0,0,-0.55), (0,0,-1.10)),
        ("Tail3",    "Tail2",    (0,0,-1.10), (0,0,-1.65)),
        ("Tail4",    "Tail3",    (0,0,-1.65), (0,0,-2.10)),
        ("Tail5",    "Tail4",    (0,0,-2.10), (0,0,-2.50)),
        ("Tail6",    "Tail5",    (0,0,-2.50), (0,0,-2.80)),
        # Front legs
        ("LF_Upper", "Spine2",  (-0.80,0,1.5),(-0.80,0,0.70)),
        ("LF_Lower", "LF_Upper",(-0.80,0,0.70),(-1.10,0,0.05)),
        ("LF_Foot",  "LF_Lower",(-1.10,0,0.05),(-1.10,0,-0.30)),
        ("RF_Upper", "Spine2",  ( 0.80,0,1.5),( 0.80,0,0.70)),
        ("RF_Lower", "RF_Upper",( 0.80,0,0.70),( 1.10,0,0.05)),
        ("RF_Foot",  "RF_Lower",( 1.10,0,0.05),( 1.10,0,-0.30)),
        # Back legs
        ("LB_Upper", "Spine4",  (-0.85,0,3.5),(-0.85,0,2.70)),
        ("LB_Lower", "LB_Upper",(-0.85,0,2.70),(-1.15,0,2.05)),
        ("LB_Foot",  "LB_Lower",(-1.15,0,2.05),(-1.15,0,1.75)),
        ("RB_Upper", "Spine4",  ( 0.85,0,3.5),( 0.85,0,2.70)),
        ("RB_Lower", "RB_Upper",( 0.85,0,2.70),( 1.15,0,2.05)),
        ("RB_Foot",  "RB_Lower",( 1.15,0,2.05),( 1.15,0,1.75)),
        # Wings
        ("WingL_Base","Spine3", (-0.85,0,2.8),(-1.80,0.2,3.50)),
        ("WingL_Mid", "WingL_Base",(-1.80,0.2,3.50),(-4.50,0.4,4.20)),
        ("WingL_Tip", "WingL_Mid",(-4.50,0.4,4.20),(-7.20,0.2,4.60)),
        ("WingR_Base","Spine3", ( 0.85,0,2.8),( 1.80,0.2,3.50)),
        ("WingR_Mid", "WingR_Base",( 1.80,0.2,3.50),( 4.50,0.4,4.20)),
        ("WingR_Tip", "WingR_Mid",( 4.50,0.4,4.20),( 7.20,0.2,4.60)),
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

    col = bpy.data.collections.new("Ignar_MoltenDrake")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'rock':   build_molten_rock_mat(),
        'wing':   build_wing_membrane_mat(),
        'glow':   build_lava_glow_mat(),
        'eye':    build_eye_fire_mat(),
        'horn':   build_horn_mat(),
        'lavaball': build_lava_ball_mat(),
    }
    objs = []

    body = build_body("Ignar_Body", mats['rock']); body.location = (0,0,0.65); link(col,body); objs.append(body)
    neck = build_neck("Ignar_Neck", mats['rock']); neck.location = (0,0,4.60); link(col,neck); objs.append(neck)
    head = build_head("Ignar_Head", mats['rock']); head.location = (0,0,5.50); link(col,head); objs.append(head)
    jaw  = build_lower_jaw("Ignar_LowerJaw", mats['rock']); jaw.location=(0,-0.55,5.65); link(col,jaw); objs.append(jaw)
    tail = build_tail("Ignar_Tail", mats['rock']); tail.location=(0,0,0.65); link(col,tail); objs.append(tail)

    # eyes
    for side, ex in [("L",-0.50),("R",0.50)]:
        eye = build_eye(f"Ignar_Eye_{side}", mats['eye']); eye.location=(ex,0.62,6.65)
        link(col,eye); objs.append(eye)
        add_pt_light(col,(ex,0.62,6.65), energy=15.0, color=(1.0,0.5,0.0), radius=0.15)

    # horns
    horn_cfgs = [
        ("Ignar_Horn_L",  (-0.45, 0.52, 7.10), (0, 0, 0.5), 1.2),
        ("Ignar_Horn_R",  ( 0.45, 0.52, 7.10), (0, 0,-0.5), 1.2),
        ("Ignar_Horn_LS", (-0.25, 0.45, 6.90), (0, 0, 0.3), 0.75),
        ("Ignar_Horn_RS", ( 0.25, 0.45, 6.90), (0, 0,-0.3), 0.75),
    ]
    for hname, hloc, hrot, hlen in horn_cfgs:
        h = build_horn(hname, hlen, mats['horn']); h.location=hloc; h.rotation_euler=hrot
        link(col,h); objs.append(h)

    # legs + claws
    leg_cfgs = [
        ("Ignar_LF_Leg",(-0.85,0,1.50),(0,0,0),      0.9, 0.75),
        ("Ignar_RF_Leg",( 0.85,0,1.50),(0,0,math.pi), 0.9, 0.75),
        ("Ignar_LB_Leg",(-0.90,0,3.50),(0,0,0),       0.95,0.80),
        ("Ignar_RB_Leg",( 0.90,0,3.50),(0,0,math.pi), 0.95,0.80),
    ]
    for lname, lloc, lrot, lul, lll in leg_cfgs:
        lg = build_leg(lname, lul, lll, mats['rock']); lg.location=lloc; lg.rotation_euler=lrot
        link(col,lg); objs.append(lg)
        add_pt_light(col,(lloc[0], lloc[1], lloc[2]-lul), energy=4.0, color=(1.0,0.35,0.0), radius=0.3)
        for ci in range(3):
            ca = (ci-1)*0.18
            claw = build_claw(f"{lname}_Claw_{ci}", mats['rock'])
            claw.location=(lloc[0]+ca*0.5, lloc[1]+lul*0.25, lloc[2]-lul-lll*0.85)
            claw.rotation_euler=(0.4,0,ca); link(col,claw); objs.append(claw)

    # dorsal plates
    dorsal_z = [1.2, 1.7, 2.2, 2.75, 3.25, 3.7, 4.1, 4.45, 4.75, 5.0]
    dorsal_h = [0.5, 0.7, 0.85,0.92, 0.88, 0.80,0.68,0.52, 0.38, 0.28]
    dorsal_w = [0.22,0.28,0.32,0.35, 0.32, 0.28,0.24,0.20, 0.15, 0.12]
    for di, (dz, dh, dw) in enumerate(zip(dorsal_z, dorsal_h, dorsal_w)):
        dp = build_dorsal_plate(f"Ignar_Dorsal_{di:02d}", dh, dw, mats['glow'])
        dp.location=(0, 0.88, dz); dp.rotation_euler=(-0.15,0,0)
        link(col,dp); objs.append(dp)
        add_pt_light(col,(0,0.88,dz+dh*0.5), energy=rng.uniform(2,5), color=(1.0,0.35,0.0), radius=0.15)

    # wings
    wing_L = build_wing("Ignar_Wing_L", 6.5, -1, mats['wing']); wing_L.location=(0,0,2.8)
    wing_R = build_wing("Ignar_Wing_R", 6.5,  1, mats['wing']); wing_R.location=(0,0,2.8)
    link(col,wing_L); link(col,wing_R); objs.extend([wing_L, wing_R])

    # lava ball projectile (separate prefab)
    lb = build_lava_ball("Ignar_LavaBall_Prefab", mats['lavaball'])
    lb.location = (8, 0, 0)  # offset — export as separate Unity prefab
    link(col, lb); objs.append(lb)
    add_pt_light(col, (8, 0, 0), energy=10.0, color=(1.0, 0.45, 0.0), radius=0.3)

    # body glow
    add_pt_light(col, (0,0,2.5), energy=8.0, color=(1.0,0.35,0.0), radius=1.5)
    add_pt_light(col, (0,0,4.5), energy=5.0, color=(1.0,0.35,0.0), radius=1.0)

    # armature
    arm = build_armature("Ignar_Armature", col)
    for obj in objs: obj.parent = arm; obj.modifiers.new("Armature",'ARMATURE').object = arm

    print(f"[Ignar_MoltenDrake] Built {len(objs)} mesh objects + 1 armature.")
    print("Export: FBX with Armature + Mesh, Apply Transform")

build_scene()
