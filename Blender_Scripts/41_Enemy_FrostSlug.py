"""
41_Enemy_FrostSlug.py
IsleTrial — Frost Slug Enemy Model
================================================
Frost Isle enemy: a slow, armoured slug that slows the player
on hit and leaves a frost patch on death.

Visual design:
  Body    — long tapered slug body with wave-undulated underside
  Armour  — 5 heavy segmented frost-crystal shell plates on back
  Eyestalks — 2 retractable stalks with glowing blue bulb tips
  Frost crystals — clusters growing from shell cracks
  Slime trail — thin flat strip on underside
  Mucus collar — frill around front of body

All materials: full procedural node networks + [UNITY] image slots
Armature: Spine(6) + Eyestalk_L/R(2ea) + Shell plates (pose bones)
UV: smart_project on every mesh
Run in Blender >= 3.6
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(410041)

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
def build_slug_body_mat():
    mat = bpy.data.materials.new("Mat_FrostSlug_Body")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['Specular IOR Level'].default_value = 0.6
    bsdf.inputs['Transmission Weight'].default_value = 0.12
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-600, 200)
    noise.inputs['Scale'].default_value  = 12.0; noise.inputs['Detail'].default_value = 6.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.08,0.12,0.18,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.22,0.30,0.38,1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600,-100)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 6.0
    cr2  = ns.new('ShaderNodeValToRGB');       cr2.location  = (-300,-100)
    cr2.color_ramp.elements[0].position = 0.0; cr2.color_ramp.elements[0].color = (0.05,0.10,0.15,1)
    cr2.color_ramp.elements[1].position = 1.0; cr2.color_ramp.elements[1].color = (0.15,0.25,0.35,1)
    mix  = ns.new('ShaderNodeMixRGB');         mix.location  = (50, 100)
    mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = 0.5
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 0.5; bmp.inputs['Distance'].default_value = 0.02
    img_a = img_slot(ns,"[UNITY] FrostSlug_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] FrostSlug_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] FrostSlug_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr1.inputs['Fac'])
    lk.new(vor.outputs['Distance'],cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_frost_shell_mat():
    mat = bpy.data.materials.new("Mat_FrostSlug_Shell")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Transmission Weight'].default_value = 0.65
    bsdf.inputs['IOR'].default_value = 1.50
    bsdf.inputs['Metallic'].default_value = 0.1
    bsdf.inputs['Base Color'].default_value = (0.65, 0.82, 0.96, 1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 7.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.55,0.80,0.98,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.88,0.95,1.00,1)
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-600,-100)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value = 4.0; mus.inputs['Detail'].default_value = 7.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 2.2; bmp.inputs['Distance'].default_value = 0.06
    img_a = img_slot(ns,"[UNITY] FrostShell_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] FrostShell_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] FrostShell_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'], cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],    mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],  mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],      bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_ice_crystal_mat():
    mat = bpy.data.materials.new("Mat_FrostSlug_IceCrystal")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['Transmission Weight'].default_value = 0.88
    bsdf.inputs['IOR'].default_value = 1.55
    bsdf.inputs['Emission Color'].default_value = (0.4, 0.85, 1.0, 1)
    bsdf.inputs['Emission Strength'].default_value = 2.5
    bsdf.inputs['Base Color'].default_value = (0.6, 0.88, 1.0, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.3, 0.8, 1.0, 1)
    em.inputs['Strength'].default_value = 4.0
    img_e = img_slot(ns,"[UNITY] FrostCrystal_Emission", -400,-300)
    img_a = img_slot(ns,"[UNITY] FrostCrystal_Albedo",   -400,-500)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_eye_glow_mat():
    mat = bpy.data.materials.new("Mat_FrostSlug_Eye")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (700, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (520, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (280, 100)
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['Transmission Weight'].default_value = 0.9
    bsdf.inputs['Base Color'].default_value = (0.2, 0.7, 1.0, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (280,-100)
    em.inputs['Color'].default_value    = (0.3, 0.8, 1.0, 1)
    em.inputs['Strength'].default_value = 10.0
    img_e = img_slot(ns,"[UNITY] SlugEye_Emission", -300,-200)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_slime_mat():
    mat = bpy.data.materials.new("Mat_FrostSlug_Slime")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Specular IOR Level'].default_value = 0.9
    bsdf.inputs['Transmission Weight'].default_value = 0.4
    bsdf.inputs['Base Color'].default_value = (0.12, 0.22, 0.35, 1)
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-500, 200)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 6.0; wave.inputs['Distortion'].default_value = 2.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 0.3
    img_n = img_slot(ns,"[UNITY] Slime_Normal", -660,-300)
    img_r = img_slot(ns,"[UNITY] Slime_Roughness",-660,-500)
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_frost_frill_mat():
    mat = bpy.data.materials.new("Mat_FrostSlug_Frill")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.15
    bsdf.inputs['Transmission Weight'].default_value = 0.5
    bsdf.inputs['Base Color'].default_value = (0.55, 0.80, 0.96, 1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-500, 200)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 10.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-250, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.45,0.70,0.92,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.82,0.92,1.00,1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.4
    img_a = img_slot(ns,"[UNITY] FrostFrill_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] FrostFrill_Normal", -660,-550)
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

# ── geometry ──────────────────────────────────────────────────────────────────
def build_slug_body(name, mat=None):
    bm = bmesh.new()
    segs_l = 28; segs_r = 16; body_len = 2.0
    verts_ring = []
    for i in range(segs_l + 1):
        t = i / segs_l
        z = t * body_len
        if t < 0.12:    # rounded head end
            rx = 0.30 * math.sin(t/0.12 * math.pi * 0.5)
            ry = 0.22 * math.sin(t/0.12 * math.pi * 0.5)
        elif t < 0.75:  # main body
            belly_t = (t - 0.12) / 0.63
            rx = 0.30 + 0.08 * math.sin(belly_t * math.pi)
            ry = 0.22 + 0.04 * math.sin(belly_t * math.pi)
        else:           # rear taper
            rt = (t - 0.75) / 0.25
            rx = 0.30 * (1 - rt * 0.85)
            ry = 0.22 * (1 - rt * 0.85)
        if rx < 0.015: rx = 0.015
        if ry < 0.012: ry = 0.012
        # slug is flattened on the bottom
        ring = []
        for s in range(segs_r):
            ang = 2*math.pi*s/segs_r
            bx = rx * math.cos(ang)
            by = ry * math.sin(ang)
            if by < -ry * 0.15: by = -ry * 0.15  # flat bottom
            # undulation
            bz = 0.02 * math.sin(t * math.pi * 8 + s * 0.5)
            ring.append(bm.verts.new((bx, by, z + bz)))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(segs_l):
        for s in range(segs_r):
            bm.faces.new([verts_ring[i][s], verts_ring[i][(s+1)%segs_r],
                          verts_ring[i+1][(s+1)%segs_r], verts_ring[i+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_shell_plate(name, scale_x=0.40, scale_y=0.32, scale_z=0.14, mat=None):
    """One armour shell segment — thick dome shape."""
    bm = bmesh.new()
    segs_u = 14; segs_v = 10
    for v in range(segs_v + 1):
        tv = v / segs_v
        ang_v = tv * math.pi * 0.55
        z = scale_z * math.sin(ang_v)
        rx2 = scale_x * math.cos(ang_v * 0.7)
        ry2 = scale_y * math.cos(ang_v * 0.7)
        row = [bm.verts.new((rx2*math.cos(2*math.pi*u/segs_u),
                              ry2*math.sin(2*math.pi*u/segs_u), z)) for u in range(segs_u)]
        if v == 0:
            first_row = row
        if v > 0:
            prev_row = [bm.verts.new((rx2_prev*math.cos(2*math.pi*u/segs_u),
                                       ry2_prev*math.sin(2*math.pi*u/segs_u), z_prev)) for u in range(segs_u)]
    bm.verts.ensure_lookup_table()
    # rebuild cleanly
    bm2 = bmesh.new()
    all_rows = []
    for v in range(segs_v + 1):
        tv = v / segs_v; ang_v = tv * math.pi * 0.55
        z = scale_z * math.sin(ang_v)
        rx2 = scale_x * math.cos(ang_v * 0.7)
        ry2 = scale_y * math.cos(ang_v * 0.7)
        row = [bm2.verts.new((rx2*math.cos(2*math.pi*u/segs_u),
                               ry2*math.sin(2*math.pi*u/segs_u), z)) for u in range(segs_u)]
        all_rows.append(row)
    bm2.verts.ensure_lookup_table()
    for v in range(segs_v):
        for u in range(segs_u):
            bm2.faces.new([all_rows[v][u], all_rows[v][(u+1)%segs_u],
                           all_rows[v+1][(u+1)%segs_u], all_rows[v+1][u]])
    # flat base
    bm2.faces.new(all_rows[0][::-1])
    mesh = bpy.data.meshes.new(name); bm2.to_mesh(mesh); bm2.free(); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_eyestalk(name, stalk_len=0.35, bulb_r=0.08, mat_stalk=None, mat_eye=None):
    objs_out = []
    # stalk
    bm = bmesh.new(); segs = 8; rings = 12
    verts_ring = []
    for r in range(rings + 1):
        t = r / rings; z = t * stalk_len
        radius = 0.030 * (1 + 0.15 * math.sin(t * math.pi))
        sway = 0.04 * math.sin(t * math.pi * 2)
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs) + sway,
                               radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    mesh = bpy.data.meshes.new(name + "_Stalk"); bm.to_mesh(mesh); bm.free()
    stalk = bpy.data.objects.new(name + "_Stalk", mesh)
    if mat_stalk: assign_mat(stalk, mat_stalk); smart_uv(stalk)
    objs_out.append(stalk)
    # bulb
    bm2 = bmesh.new()
    bmesh.ops.create_uvsphere(bm2, u_segments=12, v_segments=10, radius=bulb_r)
    mesh2 = bpy.data.meshes.new(name + "_Bulb"); bm2.to_mesh(mesh2); bm2.free()
    bulb = bpy.data.objects.new(name + "_Bulb", mesh2)
    bulb.location = (0.04 * math.sin(stalk_len), 0, stalk_len)
    if mat_eye: assign_mat(bulb, mat_eye)
    objs_out.append(bulb)
    return objs_out

def build_ice_crystal_cluster(name, count=5, mat=None):
    bm = bmesh.new()
    for _ in range(count):
        cx = rng.uniform(-0.15, 0.15); cy = rng.uniform(-0.15, 0.15)
        h = rng.uniform(0.10, 0.35); r = rng.uniform(0.02, 0.06)
        tilt_x = rng.uniform(-0.3, 0.3); tilt_y = rng.uniform(-0.3, 0.3)
        segs = 6
        bv = [bm.verts.new((cx + r*math.cos(2*math.pi*s/segs),
                             cy + r*math.sin(2*math.pi*s/segs), 0)) for s in range(segs)]
        tip = bm.verts.new((cx + tilt_x*h, cy + tilt_y*h, h))
        bm.faces.new(bv[::-1])
        for s in range(segs): bm.faces.new([bv[s], bv[(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_slime_trail(name, length=2.0, mat=None):
    bm = bmesh.new()
    segs_l = 20; segs_w = 6; width = 0.30
    for il in range(segs_l):
        for iw in range(segs_w):
            t0 = il/segs_l; t1 = (il+1)/segs_l
            w0 = width*(1-t0*0.5); w1 = width*(1-t1*0.5)
            x0a = (iw/segs_w - 0.5)*w0; x0b = ((iw+1)/segs_w - 0.5)*w0
            x1a = (iw/segs_w - 0.5)*w1; x1b = ((iw+1)/segs_w - 0.5)*w1
            z0 = t0*length; z1 = t1*length
            warp0 = 0.005*math.sin(t0*math.pi*10+iw)
            warp1 = 0.005*math.sin(t1*math.pi*10+iw)
            bm.faces.new([bm.verts.new(p) for p in [
                (x0a, warp0, z0),(x0b, warp0, z0),(x1b, warp1, z1),(x1a, warp1, z1)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_mucus_frill(name, mat=None):
    bm = bmesh.new()
    frill_segs = 20; frill_radius = 0.38; frill_height = 0.22
    for s in range(frill_segs):
        ang0 = 2*math.pi*s/frill_segs; ang1 = 2*math.pi*(s+1)/frill_segs
        r0 = frill_radius * (1 + 0.12 * math.sin(s * 3.7))
        r1 = frill_radius * (1 + 0.12 * math.sin((s+1) * 3.7))
        bm.faces.new([bm.verts.new(p) for p in [
            (r0*math.cos(ang0), r0*math.sin(ang0), 0.0),
            (r0*math.cos(ang0)*0.6, r0*math.sin(ang0)*0.6, frill_height),
            (r1*math.cos(ang1)*0.6, r1*math.sin(ang1)*0.6, frill_height),
            (r1*math.cos(ang1), r1*math.sin(ang1), 0.0)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_frost_patch_ground(name, mat=None):
    """Flat frost patch left on death."""
    bm = bmesh.new()
    segs = 22; rx = 1.2; ry = 1.0
    for s in range(segs):
        ang = 2*math.pi*s/segs
        rvar = 1 + 0.18 * math.sin(s * 4.1)
        bm.verts.new((rx*rvar*math.cos(ang), ry*rvar*math.sin(ang), 0.01))
    bm.verts.ensure_lookup_table(); bm.faces.new(bm.verts)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_frost_trail_crystal(name, mat=None):
    """Small ice crystal that spawns in the slug's trail."""
    bm = bmesh.new()
    h = rng.uniform(0.10, 0.20); r = 0.04; segs = 5
    bv = [bm.verts.new((r*math.cos(2*math.pi*s/segs), r*math.sin(2*math.pi*s/segs), 0)) for s in range(segs)]
    tip = bm.verts.new((rng.uniform(-0.02,0.02), rng.uniform(-0.02,0.02), h))
    bm.faces.new(bv[::-1])
    for s in range(segs): bm.faces.new([bv[s], bv[(s+1)%segs], tip])
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
        ("Root",    None,      (0,0,0),    (0,0,0.30)),
        ("Spine1",  "Root",    (0,0,0.30), (0,0,0.65)),
        ("Spine2",  "Spine1",  (0,0,0.65), (0,0,1.00)),
        ("Spine3",  "Spine2",  (0,0,1.00), (0,0,1.35)),
        ("Spine4",  "Spine3",  (0,0,1.35), (0,0,1.65)),
        ("Spine5",  "Spine4",  (0,0,1.65), (0,0,1.90)),
        ("Head",    "Spine5",  (0,0,1.90), (0,0,2.22)),
        ("Eyestalk_L","Head",  (-0.12,0.28,2.12),(-0.12,0.28,2.52)),
        ("Eyestalk_R","Head",  ( 0.12,0.28,2.12),( 0.12,0.28,2.52)),
        ("Shell_1", "Spine1",  (0,0.32,0.40),(0,0.32,0.60)),
        ("Shell_2", "Spine2",  (0,0.32,0.75),(0,0.32,0.95)),
        ("Shell_3", "Spine2",  (0,0.32,1.05),(0,0.32,1.25)),
        ("Shell_4", "Spine3",  (0,0.32,1.35),(0,0.32,1.55)),
        ("Shell_5", "Spine4",  (0,0.32,1.60),(0,0.32,1.78)),
        ("Tail",    "Root",    (0,0,0.0),  (0,0,-0.30)),
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

    col = bpy.data.collections.new("FrostSlug")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'body':    build_slug_body_mat(),
        'shell':   build_frost_shell_mat(),
        'crystal': build_ice_crystal_mat(),
        'eye':     build_eye_glow_mat(),
        'slime':   build_slime_mat(),
        'frill':   build_frost_frill_mat(),
    }

    objs = []

    # main body
    body = build_slug_body("FrostSlug_Body", mats['body'])
    body.location = (0, 0, 0.18)
    link(col, body); objs.append(body)

    # slime trail (underneath, behind)
    trail = build_slime_trail("FrostSlug_SlimeTrail", 2.0, mats['slime'])
    trail.location = (0, -0.16, 0.14)
    link(col, trail); objs.append(trail)

    # mucus frill (collar at front)
    frill = build_mucus_frill("FrostSlug_Frill", mats['frill'])
    frill.location = (0, 0, 2.30)
    link(col, frill); objs.append(frill)

    # armour shell plates (5 segments along back)
    shell_configs = [
        ("FrostSlug_Shell_1", (0, 0.28, 0.50), (0.3, 0, 0), 0.40, 0.32, 0.18),
        ("FrostSlug_Shell_2", (0, 0.30, 0.82), (0.2, 0, 0), 0.44, 0.35, 0.20),
        ("FrostSlug_Shell_3", (0, 0.30, 1.14), (0.1, 0, 0), 0.46, 0.36, 0.22),
        ("FrostSlug_Shell_4", (0, 0.28, 1.44), (0.0, 0, 0), 0.42, 0.33, 0.19),
        ("FrostSlug_Shell_5", (0, 0.25, 1.70), (0.0, 0, 0), 0.35, 0.28, 0.15),
    ]
    for sname, sloc, srot, sx, sy, sz in shell_configs:
        sh = build_shell_plate(sname, sx, sy, sz, mats['shell'])
        sh.location = sloc; sh.rotation_euler = srot
        link(col, sh); objs.append(sh)

    # ice crystal clusters growing from shell cracks
    crystal_cfgs = [
        ("FrostSlug_Crys_A", (-0.25, 0.28, 0.75), (0, 0, 0.5),  4),
        ("FrostSlug_Crys_B", ( 0.22, 0.28, 1.10), (0, 0, -0.4), 5),
        ("FrostSlug_Crys_C", (-0.15, 0.28, 1.45), (0, 0, 0.2),  3),
        ("FrostSlug_Crys_D", ( 0.18, 0.28, 1.60), (0, 0, 1.2),  4),
        ("FrostSlug_Crys_E", ( 0.0,  0.32, 0.50), (0, 0, 0),    6),
    ]
    for cname, cloc, crot, cnt in crystal_cfgs:
        cl = build_ice_crystal_cluster(cname, cnt, mats['crystal'])
        cl.location = cloc; cl.rotation_euler = crot
        link(col, cl); objs.append(cl)
        add_pt_light(col, cloc, energy=rng.uniform(2, 4), color=(0.3, 0.8, 1.0), radius=0.1)

    # eyestalks
    for side, ex, angle in [("L", -0.12, -0.25), ("R", 0.12, 0.25)]:
        stalk_parts = build_eyestalk(f"FrostSlug_Eyestalk_{side}", 0.38, 0.085,
                                      mats['body'], mats['eye'])
        for sp in stalk_parts:
            sp.location = (ex, 0.20, 2.12)
            sp.rotation_euler = (angle, 0, 0)
            link(col, sp); objs.append(sp)
        add_pt_light(col, (ex, 0.55, 2.50), energy=3.0, color=(0.3, 0.8, 1.0), radius=0.05)

    # frost patch (separate prefab object)
    fp = build_frost_patch_ground("FrostSlug_FrostPatch", mats['crystal'])
    fp.location = (4, 0, 0)  # offset — used as separate prefab in Unity
    link(col, fp); objs.append(fp)

    # trail crystals (scattered behind)
    for ti in range(6):
        tc = build_frost_trail_crystal(f"FrostSlug_TrailCrys_{ti:02d}", mats['crystal'])
        tc.location = (rng.uniform(-0.2, 0.2), -0.15, ti * 0.22 + 0.14)
        link(col, tc); objs.append(tc)

    # body ambient light (cold blue glow)
    add_pt_light(col, (0, 0.15, 1.0), energy=3.0, color=(0.3, 0.7, 1.0), radius=0.8)

    # armature
    arm = build_armature("FrostSlug_Armature", col)
    arm.location = (0, 0, 0)
    for obj in objs:
        obj.parent = arm
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = arm

    print(f"[FrostSlug] Built {len(objs)} mesh objects + 1 armature.")
    print("Bones: Root, Spine1-5, Head, Eyestalk_L/R, Shell_1-5, Tail")
    print("Export: File → Export → FBX, check Armature + Mesh, Apply Transform")

build_scene()
