"""
36_Environment_BioluminescentFlora.py
IsleTrial — Bioluminescent Flora Environment Set
================================================
Creates a magical glowing plant ecosystem: towering bioluminescent
trees, frond-leaf canopies, glowing ferns, luminous ground cover,
pulsing vine tendrils, spore pods, giant glowing mushrooms, coral-like
fronds, floating spore particles (mesh proxies), root tangles, and a
central glow pool surrounded by flora.

All materials use full procedural node networks + [UNITY] image slots.
smart_uv() applied to every mesh. Run in Blender ≥ 3.6.
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(360036)

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
def build_biolum_trunk_mat():
    mat = bpy.data.materials.new("Mat_BioFlora_Trunk")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (750, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 150)
    bsdf.inputs['Roughness'].default_value = 0.75
    bsdf.inputs['Emission Color'].default_value = (0.05, 0.6, 0.4, 1)
    bsdf.inputs['Emission Strength'].default_value = 1.2
    em   = ns.new('ShaderNodeEmission');       em.location   = (450,-100)
    em.inputs['Color'].default_value    = (0.05, 0.7, 0.5, 1)
    em.inputs['Strength'].default_value = 2.5
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-550, 150)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value      = 6.0
    wave.inputs['Distortion'].default_value = 5.0
    wave.inputs['Detail'].default_value     = 7.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-250, 150)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.02, 0.10, 0.07, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.05, 0.30, 0.20, 1)
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-550,-100)
    noise.inputs['Scale'].default_value  = 25.0
    noise.inputs['Detail'].default_value = 5.0
    cr2  = ns.new('ShaderNodeValToRGB');       cr2.location  = (-250,-100)
    cr2.color_ramp.elements[0].position = 0.35; cr2.color_ramp.elements[0].color = (0,0,0,1)
    cr2.color_ramp.elements[1].position = 0.65; cr2.color_ramp.elements[1].color = (1,1,1,1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (200, 250)
    bmp.inputs['Strength'].default_value = 1.2
    img_a = img_slot(ns,"[UNITY] BioTrunk_Albedo",   -660,-350)
    img_n = img_slot(ns,"[UNITY] BioTrunk_Normal",   -660,-550)
    img_e = img_slot(ns,"[UNITY] BioTrunk_Emission", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (200, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(wave.outputs['Fac'],    cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   cr2.inputs['Fac'])
    lk.new(cr2.outputs['Color'],   em.inputs['Strength'])
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_biolum_leaf_mat(color=(0.05, 0.9, 0.55)):
    mat = bpy.data.materials.new("Mat_BioFlora_Leaf")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.45
    bsdf.inputs['Transmission Weight'].default_value = 0.3
    bsdf.inputs['Emission Color'].default_value = (*color, 1)
    bsdf.inputs['Emission Strength'].default_value = 2.0
    bsdf.inputs['Base Color'].default_value = (*[v*0.6 for v in color], 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-150)
    em.inputs['Color'].default_value    = (*color, 1)
    em.inputs['Strength'].default_value = 3.5
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-450, 0)
    vor.voronoi_dimensions = '3D'
    vor.inputs['Scale'].default_value = 8.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.6; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_a = img_slot(ns,"[UNITY] BioLeaf_Albedo",   -660,-300)
    img_e = img_slot(ns,"[UNITY] BioLeaf_Emission", -660,-500)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_glow_fern_mat():
    mat = bpy.data.materials.new("Mat_BioFlora_Fern")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.60
    bsdf.inputs['Base Color'].default_value = (0.04, 0.22, 0.12, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.1, 0.9, 0.5, 1)
    em.inputs['Strength'].default_value = 2.0
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-400, 0)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-150, 0)
    cr.color_ramp.elements[0].position = 0.5; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_a = img_slot(ns,"[UNITY] Fern_Albedo",   -660,-300)
    img_e = img_slot(ns,"[UNITY] Fern_Emission", -660,-500)
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_spore_pod_mat():
    mat = bpy.data.materials.new("Mat_BioFlora_SporePod")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.30
    bsdf.inputs['Transmission Weight'].default_value = 0.5
    bsdf.inputs['IOR'].default_value = 1.40
    bsdf.inputs['Base Color'].default_value = (0.6, 0.2, 0.8, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.8, 0.2, 1.0, 1)
    em.inputs['Strength'].default_value = 5.0
    img_a = img_slot(ns,"[UNITY] SporePod_Albedo",   -400,-300)
    img_e = img_slot(ns,"[UNITY] SporePod_Emission", -400,-500)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_ground_glow_mat():
    mat = bpy.data.materials.new("Mat_BioFlora_GroundGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Base Color'].default_value = (0.02, 0.12, 0.08, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.05, 0.8, 0.45, 1)
    em.inputs['Strength'].default_value = 1.5
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-450, 0)
    vor.voronoi_dimensions = '3D'
    vor.inputs['Scale'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.4; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_a = img_slot(ns,"[UNITY] GroundGlow_Albedo",   -660,-300)
    img_e = img_slot(ns,"[UNITY] GroundGlow_Emission", -660,-500)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_vine_tendril_mat():
    mat = bpy.data.materials.new("Mat_BioFlora_Tendril")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Base Color'].default_value = (0.05, 0.25, 0.15, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.1, 1.0, 0.5, 1)
    em.inputs['Strength'].default_value = 1.8
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-450, 0)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 10.0
    wave.inputs['Distortion'].default_value = 3.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.4; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_a = img_slot(ns,"[UNITY] Tendril_Albedo",   -660,-300)
    img_e = img_slot(ns,"[UNITY] Tendril_Emission", -660,-500)
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_pool_water_mat():
    mat = bpy.data.materials.new("Mat_BioFlora_GlowPool")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['Transmission Weight'].default_value = 0.85
    bsdf.inputs['IOR'].default_value = 1.33
    bsdf.inputs['Base Color'].default_value = (0.02, 0.15, 0.10, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.05, 0.85, 0.55, 1)
    em.inputs['Strength'].default_value = 4.0
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-450, 0)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 2.0
    wave.inputs['Distortion'].default_value = 1.5
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_n = img_slot(ns,"[UNITY] GlowPool_Normal",   -660,-300)
    img_e = img_slot(ns,"[UNITY] GlowPool_Emission", -660,-500)
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_coral_mat(hue=(0.05, 0.8, 0.5)):
    mat = bpy.data.materials.new("Mat_BioFlora_Coral")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Emission Color'].default_value = (*hue, 1)
    bsdf.inputs['Emission Strength'].default_value = 1.8
    bsdf.inputs['Base Color'].default_value = (*[v*0.7 for v in hue], 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (*hue, 1)
    em.inputs['Strength'].default_value = 3.0
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-450, 0)
    vor.voronoi_dimensions = '3D'
    vor.inputs['Scale'].default_value = 6.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.2; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.5; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_a = img_slot(ns,"[UNITY] Coral_Albedo",   -660,-300)
    img_e = img_slot(ns,"[UNITY] Coral_Emission", -660,-500)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

# ── geometry builders ─────────────────────────────────────────────────────────
def build_bio_trunk(name, height=7.0, base_r=0.50, mat=None):
    bm = bmesh.new()
    segs = 12; rings = 22
    verts_ring = []
    for r in range(rings + 1):
        t = r / rings; z = t * height
        # organic sway
        sway_x = 0.4 * math.sin(t * math.pi * 1.8 + 0.5)
        sway_y = 0.25 * math.sin(t * math.pi * 2.3 + 1.0)
        radius = base_r * (1.0 - t * 0.65) * (1.0 + 0.06 * math.sin(t * math.pi * 8))
        if radius < 0.04: radius = 0.04
        ring = []
        for s in range(segs):
            ang = 2*math.pi*s/segs
            rx2 = radius * (1.0 + 0.08 * math.cos(segs*0.5*ang)) * math.cos(ang)
            ry2 = radius * (1.0 + 0.08 * math.sin(segs*0.5*ang)) * math.sin(ang)
            ring.append(bm.verts.new((sway_x + rx2, sway_y + ry2, z)))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    # root buttresses
    for b in range(5):
        ba = 2*math.pi*b/5
        bx = base_r * 1.8 * math.cos(ba); by = base_r * 1.8 * math.sin(ba)
        for ri2 in range(6):
            t0 = ri2 / 5; t1 = (ri2+1) / 5
            r0 = base_r * (1-t0*0.9); r1 = base_r * (1-t1*0.9)
            z0 = t0 * 1.5; z1 = t1 * 1.5
            p_inner_b = (base_r*0.6*math.cos(ba), base_r*0.6*math.sin(ba), z0)
            p_outer_b = (bx*(1-t0), by*(1-t0), z0 * 0.2)
            p_inner_t = (base_r*0.6*math.cos(ba), base_r*0.6*math.sin(ba), z1)
            p_outer_t = (bx*(1-t1), by*(1-t1), z1 * 0.2)
            bv = [bm.verts.new(p) for p in [p_outer_b, p_inner_b, p_inner_t, p_outer_t]]
            bm.faces.new(bv)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_frond_leaf(name, length=2.5, width=0.55, segs=16, mat=None):
    bm = bmesh.new()
    for i in range(segs):
        t0 = i / segs; t1 = (i+1) / segs
        x0 = t0 * length; x1 = t1 * length
        w0 = width * math.sin(math.pi * t0) * (1 - t0 * 0.5)
        w1 = width * math.sin(math.pi * t1) * (1 - t1 * 0.5)
        curl0 = 0.25 * t0**2 * length
        curl1 = 0.25 * t1**2 * length
        v0 = bm.verts.new((x0, -w0 * 0.5, curl0))
        v1 = bm.verts.new((x0,  w0 * 0.5, curl0))
        v2 = bm.verts.new((x1,  w1 * 0.5, curl1))
        v3 = bm.verts.new((x1, -w1 * 0.5, curl1))
        bm.faces.new([v0, v1, v2, v3])
        # midrib
        vm0 = bm.verts.new((x0, 0, curl0 + 0.01))
        vm1 = bm.verts.new((x1, 0, curl1 + 0.01))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_glow_fern(name, frond_count=8, frond_len=1.2, mat=None):
    bm = bmesh.new()
    for f in range(frond_count):
        fa = 2*math.pi*f/frond_count + rng.uniform(-0.15, 0.15)
        fl = frond_len * rng.uniform(0.7, 1.0)
        segs = 12
        for i in range(segs):
            t0 = i / segs; t1 = (i+1) / segs
            r0 = fl * t0; r1 = fl * t1
            ang0 = fa + 0.3 * math.sin(t0 * math.pi)
            ang1 = fa + 0.3 * math.sin(t1 * math.pi)
            z0 = fl * 0.6 * math.sin(t0 * math.pi * 0.7)
            z1 = fl * 0.6 * math.sin(t1 * math.pi * 0.7)
            w = 0.04 * (1 - t0 * 0.8)
            p0 = (r0*math.cos(ang0) - w, r0*math.sin(ang0), z0)
            p1 = (r0*math.cos(ang0) + w, r0*math.sin(ang0), z0)
            p2 = (r1*math.cos(ang1) + w, r1*math.sin(ang1), z1)
            p3 = (r1*math.cos(ang1) - w, r1*math.sin(ang1), z1)
            bm.faces.new([bm.verts.new(p) for p in [p0,p1,p2,p3]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_spore_pod(name, mat=None):
    bm = bmesh.new()
    # teardrop shape
    segs_r = 12; segs_v = 18; bulge = 0.55; neck = 0.18
    verts_grid = []
    for v in range(segs_v + 1):
        tv = v / segs_v
        z = tv * 1.8 - 0.3
        if tv < 0.6:
            r = bulge * math.sin(tv / 0.6 * math.pi * 0.5)
        else:
            r = bulge * (1 - (tv - 0.6) / 0.4) * 0.8 + neck * (tv - 0.6) / 0.4
        ring = [bm.verts.new((r*math.cos(2*math.pi*s/segs_r),
                               r*math.sin(2*math.pi*s/segs_r), z)) for s in range(segs_r)]
        verts_grid.append(ring)
    bm.verts.ensure_lookup_table()
    for v in range(segs_v):
        for s in range(segs_r):
            bm.faces.new([verts_grid[v][s], verts_grid[v][(s+1)%segs_r],
                          verts_grid[v+1][(s+1)%segs_r], verts_grid[v+1][s]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_ground_cover(name, cx, cy, radius=3.0, mat=None):
    bm = bmesh.new()
    patch_segs = 18
    for ps in range(patch_segs):
        ang = 2*math.pi*ps/patch_segs + rng.uniform(-0.1, 0.1)
        r = radius * rng.uniform(0.6, 1.0)
        bm.verts.new((cx + r*math.cos(ang), cy + r*math.sin(ang), rng.uniform(0.0, 0.04)))
    bm.verts.ensure_lookup_table()
    bm.faces.new(bm.verts)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_glow_pool(name, rx=5.5, ry=4.5, mat=None):
    bm = bmesh.new()
    segs = 28
    for s in range(segs):
        ang = 2*math.pi*s/segs
        rvar = 1.0 + 0.12 * math.sin(s * 3.7)
        bm.verts.new((rx*rvar*math.cos(ang), ry*rvar*math.sin(ang), 0.02))
    bm.verts.ensure_lookup_table()
    bm.faces.new(bm.verts)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_coral_frond(name, height=2.5, spread=1.0, branches=8, mat=None):
    bm = bmesh.new()
    # main stalk
    segs = 14
    for i in range(segs):
        t0 = i / segs; t1 = (i+1) / segs
        z0 = t0 * height; z1 = t1 * height
        r0 = 0.06 * (1-t0*0.6); r1 = 0.06 * (1-t1*0.6)
        for s in range(6):
            a0 = 2*math.pi*s/6; a1 = 2*math.pi*(s+1)/6
            v0 = bm.verts.new((r0*math.cos(a0), r0*math.sin(a0), z0))
            v1 = bm.verts.new((r0*math.cos(a1), r0*math.sin(a1), z0))
            v2 = bm.verts.new((r1*math.cos(a1), r1*math.sin(a1), z1))
            v3 = bm.verts.new((r1*math.cos(a0), r1*math.sin(a0), z1))
            bm.faces.new([v0,v1,v2,v3])
    # side branches
    for b in range(branches):
        bt = (b + 0.5) / branches
        bz = bt * height
        ba = 2*math.pi*b/branches
        bl = spread * math.sin(bt * math.pi) * rng.uniform(0.6, 1.0)
        bsegs = 8
        for bs in range(bsegs):
            bt0 = bs / bsegs; bt1 = (bs+1) / bsegs
            bx0 = bl*bt0*math.cos(ba); by0 = bl*bt0*math.sin(ba)
            bx1 = bl*bt1*math.cos(ba); by1 = bl*bt1*math.sin(ba)
            bzh = bz + bl * bt0 * 0.3
            bw  = 0.025 * (1 - bt0 * 0.8)
            v0 = bm.verts.new((bx0-bw, by0, bzh))
            v1 = bm.verts.new((bx0+bw, by0, bzh))
            v2 = bm.verts.new((bx1+bw, by1, bz + bl*bt1*0.3))
            v3 = bm.verts.new((bx1-bw, by1, bz + bl*bt1*0.3))
            bm.faces.new([v0,v1,v2,v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_vine_tendril(name, height=5.0, coils=2.5, mat=None):
    bm = bmesh.new()
    segs = 60; r_coil = 0.5; w = 0.025
    for i in range(segs):
        t0 = i / segs; t1 = (i+1) / segs
        z0 = t0 * height; z1 = t1 * height
        a0 = t0 * 2*math.pi*coils; a1 = t1 * 2*math.pi*coils
        r = r_coil * (1 - t0 * 0.8)
        x0 = r*math.cos(a0); y0 = r*math.sin(a0)
        x1 = r*math.cos(a1); y1 = r*math.sin(a1)
        v0 = bm.verts.new((x0-w, y0, z0)); v1 = bm.verts.new((x0+w, y0, z0))
        v2 = bm.verts.new((x1+w, y1, z1)); v3 = bm.verts.new((x1-w, y1, z1))
        bm.faces.new([v0,v1,v2,v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_giant_mushroom(name, cap_r=1.8, stem_h=3.5, mat=None):
    bm = bmesh.new()
    segs = 16
    # stem with organic bulge
    stem_rings = 18
    verts_stem = []
    for r in range(stem_rings + 1):
        t = r / stem_rings; z = t * stem_h
        bulge = 1.0 + 0.12 * math.sin(t * math.pi)
        sr = 0.22 * bulge * (1 - t * 0.35)
        ring = [bm.verts.new((sr*math.cos(2*math.pi*s/segs),
                               sr*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_stem.append(ring)
    for r in range(stem_rings):
        for s in range(segs):
            bm.faces.new([verts_stem[r][s], verts_stem[r][(s+1)%segs],
                          verts_stem[r+1][(s+1)%segs], verts_stem[r+1][s]])
    # cap
    cap_segs_r = 20; cap_rings_v = 12
    cap_verts = []
    for v in range(cap_rings_v + 1):
        tv = v / cap_rings_v
        ang_v = tv * math.pi * 0.60
        cz = stem_h + cap_r * 0.45 * math.sin(ang_v)
        cr2 = cap_r * (1 + 0.15 * tv) * math.cos(ang_v * 0.6)
        ring = [bm.verts.new((cr2*math.cos(2*math.pi*s/cap_segs_r),
                               cr2*math.sin(2*math.pi*s/cap_segs_r), cz)) for s in range(cap_segs_r)]
        cap_verts.append(ring)
    for v in range(cap_rings_v):
        for s in range(cap_segs_r):
            bm.faces.new([cap_verts[v][s], cap_verts[v][(s+1)%cap_segs_r],
                          cap_verts[v+1][(s+1)%cap_segs_r], cap_verts[v+1][s]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_spore_particle(name, loc, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=5, radius=0.06 + rng.uniform(0,0.04))
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

    col = bpy.data.collections.new("BioluminescentFlora")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'trunk':   build_biolum_trunk_mat(),
        'leaf_g':  build_biolum_leaf_mat((0.05, 0.90, 0.55)),
        'leaf_b':  build_biolum_leaf_mat((0.10, 0.55, 1.00)),
        'fern':    build_glow_fern_mat(),
        'pod':     build_spore_pod_mat(),
        'ground':  build_ground_glow_mat(),
        'tendril': build_vine_tendril_mat(),
        'pool':    build_pool_water_mat(),
        'coral_g': build_coral_mat((0.05, 0.85, 0.50)),
        'coral_p': build_coral_mat((0.75, 0.20, 1.00)),
    }

    objs = []

    # central glow pool
    pool = build_glow_pool("BioFlora_GlowPool", 5.5, 4.5, mats['pool'])
    pool.location = (0, 0, 0)
    link(col, pool); objs.append(pool)
    add_pt_light(col, (0, 0, 0.3), energy=20.0, color=(0.05, 0.85, 0.55), radius=1.5)

    # ground cover patches
    ground_positions = [
        (4,3), (-3,5), (6,-2), (-5,-3), (2,-6), (-6,2), (8,0), (-2,8)
    ]
    for gi, (gx, gy) in enumerate(ground_positions):
        gc = build_ground_cover(f"BioFlora_Ground_{gi:02d}", gx, gy,
                                 rng.uniform(2.0, 3.5), mats['ground'])
        link(col, gc); objs.append(gc)

    # bio-luminescent trees
    tree_configs = [
        ("BioFlora_Tree_A", ( 8, 6, 0), 8.5, 0.55, 0, mats['trunk']),
        ("BioFlora_Tree_B", (-8, 5, 0), 7.0, 0.48, 0, mats['trunk']),
        ("BioFlora_Tree_C", ( 7,-7, 0), 9.0, 0.60, 0, mats['trunk']),
        ("BioFlora_Tree_D", (-7,-6, 0), 6.5, 0.42, 0, mats['trunk']),
        ("BioFlora_Tree_E", (12, 0, 0), 10.0, 0.65, 0, mats['trunk']),
        ("BioFlora_Tree_F", (-11,0, 0), 7.5, 0.50, 0, mats['trunk']),
    ]
    for tname, tloc, th, tr, _, tmat in tree_configs:
        tr_obj = build_bio_trunk(tname, th, tr, tmat)
        tr_obj.location = tloc
        link(col, tr_obj); objs.append(tr_obj)
        add_pt_light(col, (tloc[0], tloc[1], th * 0.5),
                     energy=rng.uniform(4, 10), color=(0.05, 0.8, 0.5), radius=0.8)

        # frond leaves on each tree
        for fn in range(6):
            fa = 2*math.pi*fn/6 + rng.uniform(-0.2, 0.2)
            fz = th * rng.uniform(0.6, 0.9)
            fl = rng.uniform(1.8, 3.0)
            frond = build_frond_leaf(f"{tname}_Frond_{fn}", fl, 0.5, 14,
                                      mats['leaf_g'] if fn % 2 == 0 else mats['leaf_b'])
            frond.location = (tloc[0] + tr*math.cos(fa), tloc[1] + tr*math.sin(fa), fz)
            frond.rotation_euler = (rng.uniform(-0.3,0.3), rng.uniform(-0.2,0.2), fa + math.pi/2)
            link(col, frond); objs.append(frond)

    # glow ferns
    fern_locs = [
        (3,5,0), (-4,4,0), (5,-3,0), (-5,-2,0), (2,-5,0),
        (-2,7,0), (6,2,0), (-7,3,0), (4,-7,0), (-3,-7,0)
    ]
    for fi, floc in enumerate(fern_locs):
        fn = build_glow_fern(f"BioFlora_Fern_{fi:02d}",
                              rng.randint(6, 10), rng.uniform(0.8, 1.4), mats['fern'])
        fn.location = floc
        link(col, fn); objs.append(fn)
        add_pt_light(col, (floc[0], floc[1], 0.6),
                     energy=rng.uniform(0.5, 1.5), color=(0.1, 0.9, 0.5), radius=0.2)

    # spore pods hanging from trees / on stalks
    pod_cfgs = [
        ("BioFlora_Pod_A", (9, 7, 5.0)), ("BioFlora_Pod_B", (-9, 5, 4.5)),
        ("BioFlora_Pod_C", (8,-8, 6.0)), ("BioFlora_Pod_D", (-8,-7, 5.5)),
        ("BioFlora_Pod_E", (12, 1, 7.0)),("BioFlora_Pod_F", (-10, 1, 4.0)),
    ]
    for pname, ploc in pod_cfgs:
        pd = build_spore_pod(pname, mats['pod'])
        pd.location = ploc
        link(col, pd); objs.append(pd)
        add_pt_light(col, ploc, energy=rng.uniform(3,7), color=(0.8,0.2,1.0), radius=0.2)

    # coral fronds around pool
    coral_configs = [
        ("BioFlora_Coral_A", (5, 3, 0), (0,0,0.3),    2.0, 0.8, mats['coral_g']),
        ("BioFlora_Coral_B", (-4,4, 0), (0,0,1.2),    2.5, 1.0, mats['coral_p']),
        ("BioFlora_Coral_C", (4,-4, 0), (0,0,2.4),    1.8, 0.7, mats['coral_g']),
        ("BioFlora_Coral_D", (-5,-3,0), (0,0,3.5),    2.2, 0.9, mats['coral_p']),
        ("BioFlora_Coral_E", (2, 5, 0), (0,0,0.8),    1.5, 0.6, mats['coral_g']),
        ("BioFlora_Coral_F", (-3,-5,0), (0,0,1.6),    2.8, 1.1, mats['coral_p']),
    ]
    for cname, cloc, crot, ch, csp, cmat in coral_configs:
        cf = build_coral_frond(cname, ch, csp, rng.randint(6,10), cmat)
        cf.location = cloc; cf.rotation_euler = crot
        link(col, cf); objs.append(cf)
        add_pt_light(col, (cloc[0], cloc[1], ch*0.5),
                     energy=rng.uniform(2,5), color=(0.05,0.85,0.5), radius=0.3)

    # vine tendrils
    tendril_locs = [
        ("BioFlora_Tendril_A", (6, 8, 0), (0,0,0.5), 5.0, 2.5),
        ("BioFlora_Tendril_B", (-6,8, 0), (0,0,1.5), 4.5, 3.0),
        ("BioFlora_Tendril_C", (10,-2, 0),(0,0,2.0), 6.0, 2.0),
        ("BioFlora_Tendril_D", (-9,-4,0), (0,0,0.8), 5.5, 2.8),
    ]
    for tvname, tvloc, tvrot, tvh, tvcoils in tendril_locs:
        tv = build_vine_tendril(tvname, tvh, tvcoils, mats['tendril'])
        tv.location = tvloc; tv.rotation_euler = tvrot
        link(col, tv); objs.append(tv)

    # giant mushrooms
    giant_cfgs = [
        ("BioFlora_GiantMush_A", (10, 8, 0), 1.5, 2.8),
        ("BioFlora_GiantMush_B", (-10,-8,0), 1.2, 2.5),
        ("BioFlora_GiantMush_C", (0, 12, 0), 1.8, 3.2),
    ]
    for gname, gloc, gcr, gsh in giant_cfgs:
        gm = build_giant_mushroom(gname, gcr, gsh, mats['fern'])
        gm.location = gloc
        link(col, gm); objs.append(gm)
        add_pt_light(col, (gloc[0], gloc[1], gsh + gcr * 0.5),
                     energy=rng.uniform(6, 12), color=(0.1, 0.85, 0.5), radius=0.5)

    # floating spore particles
    spore_locs = [
        (1.5, 2, 3.5), (-2, 3, 4.0), (3, -1, 2.8), (-3, 0, 3.2),
        (0.5, 4, 5.0), (2.5,-3, 2.5), (-1, -2, 4.5), (4, 1, 3.0),
        (-4, 2, 2.2), (2, 5, 4.8), (-2,-4, 3.8), (5, -2, 2.0),
    ]
    for si, sloc in enumerate(spore_locs):
        sp = build_spore_particle(f"BioFlora_Spore_{si:02d}", sloc, mats['pod'])
        link(col, sp); objs.append(sp)

    print(f"[BioluminescentFlora] Built {len(objs)} objects.")
    print("Export: File → Export → FBX, apply modifiers and transforms.")

build_scene()
