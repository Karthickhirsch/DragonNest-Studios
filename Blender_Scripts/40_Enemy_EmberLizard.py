"""
40_Enemy_EmberLizard.py
IsleTrial — Ember Lizard Enemy Model
================================================
Ember Isle enemy that charges and explodes on death.
A heavy, low-to-ground volcanic lizard with glowing ember
cracks along its spine and underbelly, bulging explosive-
looking abdomen, four powerful legs with claw toes, thick
neck, broad jaw, and a thick club tail.

Geometry:  bmesh for all body parts
Materials: full procedural node networks + [UNITY] image slots
Armature:  Spine(4)+Head+Jaw+Tail(5)+LFLeg/RFLeg/LBLeg/RBLeg(3ea)
UV:        smart_project on every mesh
Run in Blender >= 3.6  →  Scripting workspace → Run Script
Export as FBX with armature for Unity.
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(400040)

# ── helpers ───────────────────────────────────────────────────────────────────
def ns_lk(mat):
    return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, name, x, y):
    n = ns.new('ShaderNodeTexImage'); n.label = name; n.location = (x, y)
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

def add_pt_light(col, loc, energy, color, radius=0.2):
    bpy.ops.object.light_add(type='POINT', location=loc)
    lt = bpy.context.active_object
    lt.data.energy = energy; lt.data.color = color; lt.data.shadow_soft_size = radius
    col.objects.link(lt)
    if lt.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(lt)
    return lt

# ── material builders ─────────────────────────────────────────────────────────
def build_ember_scale_mat():
    mat = bpy.data.materials.new("Mat_EmberLizard_Scales")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (750, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 150)
    bsdf.inputs['Roughness'].default_value = 0.78
    bsdf.inputs['Metallic'].default_value  = 0.05
    bsdf.inputs['Emission Strength'].default_value = 0.5
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.25, 0.0, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (450,-150)
    em.inputs['Color'].default_value    = (1.0, 0.3, 0.0, 1)
    em.inputs['Strength'].default_value = 1.5
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 9.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.06,0.03,0.01,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.22,0.10,0.04,1)
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-600,-100)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value  = 5.0; mus.inputs['Detail'].default_value = 8.0
    cr2  = ns.new('ShaderNodeValToRGB');       cr2.location  = (-300,-100)
    cr2.color_ramp.elements[0].position = 0.5; cr2.color_ramp.elements[0].color = (0,0,0,1)
    cr2.color_ramp.elements[1].position = 0.85;cr2.color_ramp.elements[1].color = (1,1,1,1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (200, 280)
    bmp.inputs['Strength'].default_value = 2.0; bmp.inputs['Distance'].default_value = 0.04
    img_a = img_slot(ns,"[UNITY] EmberLizard_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] EmberLizard_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] EmberLizard_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (200, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'],  cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],     mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],   mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],       cr2.inputs['Fac'])
    lk.new(cr2.outputs['Color'],     em.inputs['Strength'])
    lk.new(vor.outputs['Distance'],  bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],    bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],    bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],     add.inputs[0])
    lk.new(em.outputs['Emission'],   add.inputs[1])
    lk.new(add.outputs['Shader'],    out.inputs['Surface'])
    return mat

def build_lava_crack_mat():
    mat = bpy.data.materials.new("Mat_EmberLizard_LavaCrack")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.92
    bsdf.inputs['Base Color'].default_value = (0.05, 0.02, 0.01, 1)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.35, 0.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 5.0
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (1.0, 0.4, 0.0, 1)
    em.inputs['Strength'].default_value = 8.0
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-500, 0)
    vor.voronoi_dimensions = '3D'; vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-250, 0)
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (1,1,1,1)
    cr.color_ramp.elements[1].position = 0.12;cr.color_ramp.elements[1].color = (0,0,0,1)
    img_e = img_slot(ns,"[UNITY] EmberCrack_Emission", -660,-350)
    lk.new(vor.outputs['Distance'],  cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],      em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],     add.inputs[0])
    lk.new(em.outputs['Emission'],   add.inputs[1])
    lk.new(add.outputs['Shader'],    out.inputs['Surface'])
    return mat

def build_belly_mat():
    mat = bpy.data.materials.new("Mat_EmberLizard_Belly")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.65
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-500, 200)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 12.0; wave.inputs['Distortion'].default_value = 2.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-200, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.18,0.06,0.02,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.40,0.18,0.06,1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 0.8
    img_a = img_slot(ns,"[UNITY] EmberBelly_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] EmberBelly_Normal", -660,-550)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(wave.outputs['Fac'],   cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],  mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix2.inputs['Color2'])
    lk.new(wave.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'], bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def build_eye_glow_mat():
    mat = bpy.data.materials.new("Mat_EmberLizard_Eye")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (700, 0)
    em   = ns.new('ShaderNodeEmission');       em.location   = (450, 0)
    em.inputs['Color'].default_value    = (1.0, 0.5, 0.0, 1)
    em.inputs['Strength'].default_value = 12.0
    img_e = img_slot(ns,"[UNITY] EmberEye_Emission", -400,-200)
    lk.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

def build_claw_mat():
    mat = bpy.data.materials.new("Mat_EmberLizard_Claw")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Base Color'].default_value = (0.05, 0.03, 0.02, 1)
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-400, 100)
    noise.inputs['Scale'].default_value = 18.0; noise.inputs['Detail'].default_value = 4.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (300, 200)
    bmp.inputs['Strength'].default_value = 1.2
    img_a = img_slot(ns,"[UNITY] EmberClaw_Albedo", -660,-300)
    lk.new(noise.outputs['Fac'], bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_spine_spike_mat():
    mat = bpy.data.materials.new("Mat_EmberLizard_Spine")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Base Color'].default_value = (0.04, 0.02, 0.01, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (1.0, 0.25, 0.0, 1)
    em.inputs['Strength'].default_value = 3.0
    img_e = img_slot(ns,"[UNITY] EmberSpine_Emission", -400,-300)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

# ── geometry builders ─────────────────────────────────────────────────────────
def build_body(name, mat=None):
    """Elongated lizard body with bulging explosive belly."""
    bm = bmesh.new()
    segs_l = 22; segs_r = 14
    verts_ring = []
    body_len = 2.4
    for i in range(segs_l + 1):
        t = i / segs_l
        z = t * body_len - body_len * 0.3
        # Profile: narrow front, bulging belly center, narrow rear
        if t < 0.2:   # neck transition
            rx = 0.22 + t * 0.3; ry = 0.18 + t * 0.25
        elif t < 0.65: # belly bulge
            belly_t = (t - 0.2) / 0.45
            rx = 0.28 + 0.38 * math.sin(belly_t * math.pi)
            ry = 0.22 + 0.28 * math.sin(belly_t * math.pi)
        else:          # rear tapering to tail
            rear_t = (t - 0.65) / 0.35
            rx = 0.28 * (1 - rear_t * 0.6)
            ry = 0.22 * (1 - rear_t * 0.6)
        # flatten bottom for ground contact
        ring = []
        for s in range(segs_r):
            ang = 2*math.pi*s/segs_r
            bx = rx * math.cos(ang)
            by = ry * math.sin(ang) * (0.6 if math.sin(ang) < 0 else 1.0)
            ring.append(bm.verts.new((bx, by, z + rng.uniform(-0.01,0.01))))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(segs_l):
        for s in range(segs_r):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs_r],
                          verts_ring[i+1][(s+1)%segs_r], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_head(name, mat=None):
    """Broad, wide lizard head with pronounced jaw socket."""
    bm = bmesh.new()
    segs = 14; rings = 16; head_len = 0.65
    verts_ring = []
    for i in range(rings + 1):
        t = i / rings
        z = t * head_len
        if t < 0.3:
            rx = 0.20 + t * 0.8; ry = 0.16 + t * 0.55
        elif t < 0.7:
            rx = 0.44 + (t-0.3)*0.15; ry = 0.32 + (t-0.3)*0.05
        else:
            rx = 0.50 * (1 - (t-0.7)*1.5); ry = 0.34 * (1 - (t-0.7)*1.5)
        ring = []
        for s in range(segs):
            ang = 2*math.pi*s/segs
            bx = rx * math.cos(ang)
            by = ry * math.sin(ang) * (0.55 if math.sin(ang) < 0 else 1.1)
            ring.append(bm.verts.new((bx, by, z)))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs],
                          verts_ring[i+1][(s+1)%segs], verts_ring[i+1][s]])
    # snout cap
    tip = bm.verts.new((0, 0, head_len + 0.08))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_lower_jaw(name, mat=None):
    """Lower jaw plate."""
    bm = bmesh.new()
    segs = 10; rings = 10; jaw_len = 0.55
    verts_ring = []
    for i in range(rings + 1):
        t = i / rings
        z = t * jaw_len
        rx = 0.38 * (1 - t * 0.85); ry = 0.12 * (1 - t * 0.7)
        ring = []
        for s in range(segs):
            ang = 2*math.pi*s/segs
            ring.append(bm.verts.new((rx*math.cos(ang), ry*math.sin(ang), z)))
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

def build_eye(name, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.075)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    return obj

def build_leg(name, upper_len=0.45, lower_len=0.35, mat=None):
    """3-segment leg: upper, lower, foot."""
    bm = bmesh.new()
    segs = 8
    # upper limb
    for ring in range(10):
        t0 = ring/9; t1 = (ring+1)/9
        z0 = -t0*upper_len; z1 = -t1*upper_len
        r0 = 0.10*(1-t0*0.3); r1 = 0.10*(1-t1*0.3)
        pts_b = [bm.verts.new((r0*math.cos(2*math.pi*s/segs), r0*math.sin(2*math.pi*s/segs), z0)) for s in range(segs)]
        pts_t = [bm.verts.new((r0*math.cos(2*math.pi*s/segs), r0*math.sin(2*math.pi*s/segs), z1)) for s in range(segs)]
        for s in range(segs):
            bm.faces.new([pts_b[s], pts_b[(s+1)%segs], pts_t[(s+1)%segs], pts_t[s]])
    # lower limb (angled forward)
    knee_z = -upper_len
    for ring in range(10):
        t0 = ring/9; t1 = (ring+1)/9
        z0 = knee_z - t0*lower_len*0.8
        z1 = knee_z - t1*lower_len*0.8
        x0 = t0*lower_len*0.45; x1 = t1*lower_len*0.45
        r = 0.07*(1-t0*0.25)
        pts_b = [bm.verts.new((x0+r*math.cos(2*math.pi*s/segs), r*math.sin(2*math.pi*s/segs), z0)) for s in range(segs)]
        pts_t = [bm.verts.new((x1+r*math.cos(2*math.pi*s/segs), r*math.sin(2*math.pi*s/segs), z1)) for s in range(segs)]
        for s in range(segs):
            bm.faces.new([pts_b[s], pts_b[(s+1)%segs], pts_t[(s+1)%segs], pts_t[s]])
    # foot pad
    foot_z = knee_z - lower_len*0.8
    foot_x = lower_len*0.45
    for ix in range(4):
        cx = foot_x + ix*0.055 - 0.08; cy = (ix-1.5)*0.06
        bm.faces.new([bm.verts.new(p) for p in [
            (cx, cy-0.02, foot_z), (cx+0.05, cy-0.02, foot_z),
            (cx+0.05, cy+0.02, foot_z), (cx, cy+0.02, foot_z)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_claw(name, mat=None):
    bm = bmesh.new()
    segs = 6; rings = 8; cl = 0.12
    verts_ring = []
    for r in range(rings+1):
        t = r/rings; z = t*cl
        radius = 0.025*(1-t*0.88)
        if radius < 0.003: radius = 0.003
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs),
                               radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0, 0, cl+0.02))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_tail(name, mat=None):
    """Thick club tail tapering to narrow tip."""
    bm = bmesh.new()
    segs = 10; rings = 26; tail_len = 1.4
    verts_ring = []
    for i in range(rings+1):
        t = i/rings
        z = t * tail_len
        # thick club base, then taper fast
        if t < 0.35:
            r = 0.20 + t*0.1
        else:
            r = 0.24*(1-(t-0.35)/0.65)**1.5
        if r < 0.012: r = 0.012
        sway = 0.18 * math.sin(t*math.pi*2.5)
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs)+sway*0.4,
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

def build_spine_spike(name, height=0.18, mat=None):
    bm = bmesh.new()
    segs = 6; rings = 8
    verts_ring = []
    for r in range(rings+1):
        t = r/rings; z = t*height
        radius = 0.035*(1-t*0.85)*(1+0.08*math.sin(t*math.pi*4))
        if radius < 0.003: radius = 0.003
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs),
                               radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((rng.uniform(-0.01,0.01), rng.uniform(-0.01,0.01), height+0.03))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

def build_neck(name, mat=None):
    bm = bmesh.new()
    segs = 12; rings = 12; neck_len = 0.35
    verts_ring = []
    for i in range(rings+1):
        t = i/rings; z = t*neck_len
        r = 0.22 - t*0.04
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

def build_lava_crack_strip(name, length=0.5, mat=None):
    """A glowing crack strip applied along spine."""
    bm = bmesh.new()
    segs = 16
    for i in range(segs):
        t0 = i/segs; t1 = (i+1)/segs
        z0 = t0*length; z1 = t1*length
        w = 0.018*(1-abs(t0-0.5)*1.8)
        if w < 0.003: w = 0.003
        v0 = bm.verts.new((-w, 0.001, z0)); v1 = bm.verts.new((w, 0.001, z0))
        v2 = bm.verts.new((w, 0.001, z1)); v3 = bm.verts.new((-w, 0.001, z1))
        bm.faces.new([v0,v1,v2,v3])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj); return obj

# ── armature builder ──────────────────────────────────────────────────────────
def build_armature(name, col):
    bpy.ops.object.armature_add(enter_editmode=True, location=(0,0,0))
    arm_obj = bpy.context.active_object
    arm_obj.name = name
    arm = arm_obj.data; arm.name = name + "_Data"
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.delete()
    eb = arm.edit_bones

    # Spine chain
    spine_positions = [
        ("Root",  None,          (0,0,0),    (0,0,0.25)),
        ("Spine1","Root",        (0,0,0.25), (0,0,0.55)),
        ("Spine2","Spine1",      (0,0,0.55), (0,0,0.90)),
        ("Spine3","Spine2",      (0,0,0.90), (0,0,1.20)),
        ("Spine4","Spine3",      (0,0,1.20), (0,0,1.50)),
        ("Neck",  "Spine4",      (0,0,1.50), (0,0,1.75)),
        ("Head",  "Neck",        (0,0,1.75), (0,0,2.20)),
        ("LowerJaw","Head",      (0,-0.12,1.80),(0,-0.12,1.42)),
        # Tail
        ("Tail1", "Root",        (0,0,0.0),  (0,0,-0.35)),
        ("Tail2", "Tail1",       (0,0,-0.35),(0,0,-0.70)),
        ("Tail3", "Tail2",       (0,0,-0.70),(0,0,-1.00)),
        ("Tail4", "Tail3",       (0,0,-1.00),(0,0,-1.25)),
        ("Tail5", "Tail4",       (0,0,-1.25),(0,0,-1.42)),
        # Front legs
        ("LF_Upper","Spine1",   (-0.32, 0, 0.40),(-0.32, 0, 0.00)),
        ("LF_Lower","LF_Upper", (-0.32, 0, 0.00),(-0.48, 0,-0.32)),
        ("LF_Foot", "LF_Lower", (-0.48, 0,-0.32),(-0.48, 0,-0.50)),
        ("RF_Upper","Spine1",   ( 0.32, 0, 0.40),( 0.32, 0, 0.00)),
        ("RF_Lower","RF_Upper", ( 0.32, 0, 0.00),( 0.48, 0,-0.32)),
        ("RF_Foot", "RF_Lower", ( 0.48, 0,-0.32),( 0.48, 0,-0.50)),
        # Back legs
        ("LB_Upper","Spine3",   (-0.35, 0, 0.95),(-0.35, 0, 0.55)),
        ("LB_Lower","LB_Upper", (-0.35, 0, 0.55),(-0.50, 0, 0.25)),
        ("LB_Foot", "LB_Lower", (-0.50, 0, 0.25),(-0.50, 0, 0.08)),
        ("RB_Upper","Spine3",   ( 0.35, 0, 0.95),( 0.35, 0, 0.55)),
        ("RB_Lower","RB_Upper", ( 0.35, 0, 0.55),( 0.50, 0, 0.25)),
        ("RB_Foot", "RB_Lower", ( 0.50, 0, 0.25),( 0.50, 0, 0.08)),
    ]
    created = {}
    for bname, parent, head, tail in spine_positions:
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

    col = bpy.data.collections.new("EmberLizard")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'scale':  build_ember_scale_mat(),
        'crack':  build_lava_crack_mat(),
        'belly':  build_belly_mat(),
        'eye':    build_eye_glow_mat(),
        'claw':   build_claw_mat(),
        'spine':  build_spine_spike_mat(),
    }

    objs = []

    # main body parts
    body = build_body("EmberLizard_Body", mats['scale'])
    body.location = (0, 0, 0.52)
    link(col, body); objs.append(body)

    neck = build_neck("EmberLizard_Neck", mats['scale'])
    neck.location = (0, 0, 1.45)
    link(col, neck); objs.append(neck)

    head = build_head("EmberLizard_Head", mats['scale'])
    head.location = (0, 0, 1.70)
    link(col, head); objs.append(head)

    jaw = build_lower_jaw("EmberLizard_LowerJaw", mats['belly'])
    jaw.location = (0, -0.12, 1.74)
    link(col, jaw); objs.append(jaw)

    tail = build_tail("EmberLizard_Tail", mats['scale'])
    tail.location = (0, 0, 0.52)
    link(col, tail); objs.append(tail)

    # eyes
    for side, ex in [("L", -0.22), ("R", 0.22)]:
        eye = build_eye(f"EmberLizard_Eye_{side}", mats['eye'])
        eye.location = (ex, 0.28, 2.15)
        link(col, eye); objs.append(eye)
        add_pt_light(col, (ex, 0.28, 2.15), energy=3.0, color=(1.0, 0.5, 0.0), radius=0.05)

    # legs
    leg_configs = [
        ("EmberLizard_LF_Leg", (-0.32, 0, 0.90), (0, 0, 0),       0.45, 0.35),
        ("EmberLizard_RF_Leg", ( 0.32, 0, 0.90), (0, 0, math.pi), 0.45, 0.35),
        ("EmberLizard_LB_Leg", (-0.35, 0, 0.68), (0, 0, 0),       0.48, 0.38),
        ("EmberLizard_RB_Leg", ( 0.35, 0, 0.68), (0, 0, math.pi), 0.48, 0.38),
    ]
    for lname, lloc, lrot, lul, lll in leg_configs:
        lg = build_leg(lname, lul, lll, mats['scale'])
        lg.location = lloc; lg.rotation_euler = lrot
        link(col, lg); objs.append(lg)
        # claws
        for ci in range(3):
            ca = (ci - 1) * 0.15
            claw = build_claw(f"{lname}_Claw_{ci}", mats['claw'])
            claw.location = (lloc[0] + ca*0.3, lloc[1] + lul*0.2, lloc[2]-lul-lll*0.8)
            claw.rotation_euler = (0.3, 0, ca)
            link(col, claw); objs.append(claw)

    # spine spikes
    spine_z_positions = [0.70, 0.88, 1.05, 1.20, 1.35, 1.50, 1.62]
    spine_heights     = [0.12, 0.16, 0.20, 0.22, 0.20, 0.16, 0.12]
    for si, (sz, sh) in enumerate(zip(spine_z_positions, spine_heights)):
        spike = build_spine_spike(f"EmberLizard_Spine_{si:02d}", sh, mats['spine'])
        spike.location = (0, 0.30, sz)
        spike.rotation_euler = (-0.2, 0, 0)
        link(col, spike); objs.append(spike)

    # lava crack strips along spine
    crack_configs = [
        ("EmberLizard_Crack_Belly",  (0, -0.31, 0.52), (math.pi, 0, 0), 1.6),
        ("EmberLizard_Crack_Left",   (-0.28, 0.1, 0.52),(0, -0.4, 0),   1.2),
        ("EmberLizard_Crack_Right",  ( 0.28, 0.1, 0.52),(0,  0.4, 0),   1.2),
        ("EmberLizard_Crack_Head",   (0, 0.28, 1.80),   (0.2, 0, 0),    0.5),
    ]
    for cname, cloc, crot, clen in crack_configs:
        cr = build_lava_crack_strip(cname, clen, mats['crack'])
        cr.location = cloc; cr.rotation_euler = crot
        link(col, cr); objs.append(cr)

    # belly underbelly
    belly_strip = build_lava_crack_strip("EmberLizard_Belly_Strip", 1.8, mats['belly'])
    belly_strip.location = (0, -0.32, 0.52)
    link(col, belly_strip); objs.append(belly_strip)

    # glow lights for lava cracks
    add_pt_light(col, (0, 0, 0.90), energy=4.0, color=(1.0, 0.35, 0.0), radius=0.5)
    add_pt_light(col, (0, 0, 1.30), energy=2.5, color=(1.0, 0.35, 0.0), radius=0.3)

    # armature
    arm = build_armature("EmberLizard_Armature", col)
    arm.location = (0, 0, 0)

    # parent all mesh objects to armature
    for obj in objs:
        obj.parent = arm
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = arm

    print(f"[EmberLizard] Built {len(objs)} mesh objects + 1 armature.")
    print("Bones: Root, Spine1-4, Neck, Head, LowerJaw, Tail1-5, LF/RF/LB/RB Upper/Lower/Foot")
    print("Export: File → Export → FBX, check Armature + Mesh, Apply Transform")

build_scene()
