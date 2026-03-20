"""
34_Environment_AncientRuins.py
IsleTrial — Ancient Ruins Environment Set
================================================
Produces a dense ruined complex: crumbled temple walls, sunken
courtyards, broken obelisks, mossy archways, scattered stone
fragments, altar dais, floor-tile fields, column rows, carved
relief panels, vines, debris piles, firefly glow spheres.

All geometry uses bmesh for custom detail.
Every material has a full procedural node network PLUS dedicated
[UNITY] image-texture slots (Albedo / Normal / Roughness / Emission).
smart_uv() is called on every mesh object.

Run inside Blender ≥ 3.6:  Scripting workspace → Run Script
Export each collection as FBX for Unity.
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

# ── helpers ──────────────────────────────────────────────────────────────────
rng = random.Random(340034)

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

def link(parent_col, obj):
    parent_col.objects.link(obj)
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
def build_mossy_stone_mat():
    mat = bpy.data.materials.new("Mat_Ruins_MossyStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial');  out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled');  bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.88
    bsdf.inputs['Metallic'].default_value  = 0.0
    mus  = ns.new('ShaderNodeTexMusgrave');     mus.location  = (-600, 200)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value  = 4.0
    mus.inputs['Detail'].default_value = 8.0
    mus.inputs['Dimension'].default_value = 1.1
    cr_stone = ns.new('ShaderNodeValToRGB');    cr_stone.location = (-300, 200)
    cr_stone.color_ramp.elements[0].position = 0.0
    cr_stone.color_ramp.elements[0].color = (0.18, 0.16, 0.14, 1)
    cr_stone.color_ramp.elements[1].position = 1.0
    cr_stone.color_ramp.elements[1].color = (0.42, 0.38, 0.32, 1)
    noise = ns.new('ShaderNodeTexNoise');       noise.location = (-600, -100)
    noise.inputs['Scale'].default_value  = 14.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.65
    cr_moss = ns.new('ShaderNodeValToRGB');     cr_moss.location = (-300, -100)
    cr_moss.color_ramp.elements[0].position = 0.5
    cr_moss.color_ramp.elements[0].color = (0.08, 0.14, 0.05, 1)
    cr_moss.color_ramp.elements[1].position = 1.0
    cr_moss.color_ramp.elements[1].color = (0.14, 0.24, 0.06, 1)
    mix  = ns.new('ShaderNodeMixRGB');          mix.location  = (50, 100)
    mix.blend_type = 'MIX'
    bmp  = ns.new('ShaderNodeBump');            bmp.location  = (380, 280)
    bmp.inputs['Strength'].default_value = 1.4
    bmp.inputs['Distance'].default_value = 0.04
    img_a = img_slot(ns, "[UNITY] MossyStone_Albedo",    -660, -350)
    img_n = img_slot(ns, "[UNITY] MossyStone_Normal",    -660, -550)
    img_r = img_slot(ns, "[UNITY] MossyStone_Roughness", -660, -750)
    mix2  = ns.new('ShaderNodeMixRGB');         mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr_stone.inputs['Fac'])
    lk.new(noise.outputs['Fac'],   cr_moss.inputs['Fac'])
    lk.new(cr_stone.outputs['Color'], mix.inputs['Color1'])
    lk.new(cr_moss.outputs['Color'],  mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   mix.inputs['Fac'])
    lk.new(mix.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],     bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_carved_stone_mat():
    mat = bpy.data.materials.new("Mat_Ruins_CarvedStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.82
    bsdf.inputs['Metallic'].default_value  = 0.02
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'
    vor.inputs['Scale'].default_value = 3.5
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.22, 0.19, 0.15, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.50, 0.44, 0.36, 1)
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-600, -100)
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value      = 6.0
    wave.inputs['Distortion'].default_value = 3.0
    wave.inputs['Detail'].default_value     = 5.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.8
    bmp.inputs['Distance'].default_value = 0.03
    img_a = img_slot(ns, "[UNITY] CarvedStone_Albedo",    -660, -350)
    img_n = img_slot(ns, "[UNITY] CarvedStone_Normal",    -660, -550)
    img_r = img_slot(ns, "[UNITY] CarvedStone_Roughness", -660, -750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'],  cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],     mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],   mix2.inputs['Color2'])
    lk.new(wave.outputs['Fac'],      bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],    bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],    bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],     out.inputs['Surface'])
    return mat

def build_ancient_floor_mat():
    mat = bpy.data.materials.new("Mat_Ruins_AncientFloor")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.78
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-550, 200)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value      = 2.0
    wave.inputs['Distortion'].default_value = 2.5
    wave.inputs['Detail'].default_value     = 4.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-250, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.30, 0.26, 0.20, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.55, 0.48, 0.36, 1)
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-550, -100)
    noise.inputs['Scale'].default_value = 22.0
    noise.inputs['Detail'].default_value = 5.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 0.8
    bmp.inputs['Distance'].default_value = 0.03
    img_a = img_slot(ns, "[UNITY] AncientFloor_Albedo",    -660, -350)
    img_n = img_slot(ns, "[UNITY] AncientFloor_Normal",    -660, -550)
    img_r = img_slot(ns, "[UNITY] AncientFloor_Roughness", -660, -750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(wave.outputs['Fac'],    cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_ruin_wood_mat():
    mat = bpy.data.materials.new("Mat_Ruins_Wood")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.85
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-550, 200)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value      = 5.0
    wave.inputs['Distortion'].default_value = 4.5
    wave.inputs['Detail'].default_value     = 6.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-250, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.10, 0.06, 0.03, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.32, 0.22, 0.12, 1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.2
    bmp.inputs['Distance'].default_value = 0.04
    img_a = img_slot(ns, "[UNITY] RuinWood_Albedo",    -660, -350)
    img_n = img_slot(ns, "[UNITY] RuinWood_Normal",    -660, -550)
    img_r = img_slot(ns, "[UNITY] RuinWood_Roughness", -660, -750)
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

def build_rune_glow_mat(color_val=(0.2, 0.9, 0.6)):
    mat = bpy.data.materials.new("Mat_Ruins_RuneGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (800, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (600, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (300, 100)
    bsdf.inputs['Roughness'].default_value = 0.3
    bsdf.inputs['Emission Strength'].default_value = 3.5
    bsdf.inputs['Emission Color'].default_value = (*color_val, 1)
    bsdf.inputs['Base Color'].default_value = (*[v*0.4 for v in color_val], 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (300, -100)
    em.inputs['Color'].default_value    = (*color_val, 1)
    em.inputs['Strength'].default_value = 5.0
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-400, 0)
    noise.inputs['Scale'].default_value  = 8.0
    noise.inputs['Detail'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-150, 0)
    cr.color_ramp.elements[0].position = 0.4; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns, "[UNITY] RuneGlow_Emission", -660, -350)
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_vine_mat():
    mat = bpy.data.materials.new("Mat_Ruins_Vine")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.92
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-500, 200)
    noise.inputs['Scale'].default_value  = 20.0
    noise.inputs['Detail'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 200)
    cr.color_ramp.elements[0].position = 0.3
    cr.color_ramp.elements[0].color = (0.04, 0.10, 0.02, 1)
    cr.color_ramp.elements[1].position = 0.8
    cr.color_ramp.elements[1].color = (0.08, 0.22, 0.04, 1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (350, 250)
    bmp.inputs['Strength'].default_value = 0.7
    img_a = img_slot(ns, "[UNITY] Vine_Albedo",    -660, -350)
    img_n = img_slot(ns, "[UNITY] Vine_Normal",    -660, -550)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (350, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_dust_mat():
    mat = bpy.data.materials.new("Mat_Ruins_Dust")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (700, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 0)
    bsdf.inputs['Roughness'].default_value = 0.98
    bsdf.inputs['Base Color'].default_value = (0.45, 0.40, 0.30, 1)
    img_a = img_slot(ns, "[UNITY] Dust_Albedo",    -400, -300)
    img_n = img_slot(ns, "[UNITY] Dust_Normal",    -400, -500)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (200, 0)
    mix2.inputs['Fac'].default_value = 0.0
    mix2.inputs['Color1'].default_value = (0.45, 0.40, 0.30, 1)
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_firefly_mat():
    mat = bpy.data.materials.new("Mat_Ruins_Firefly")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (700, 0)
    em   = ns.new('ShaderNodeEmission');       em.location   = (450, 0)
    em.inputs['Color'].default_value    = (0.6, 1.0, 0.3, 1)
    em.inputs['Strength'].default_value = 12.0
    lk.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

# ── geometry builders ─────────────────────────────────────────────────────────
def build_crumbled_wall(name, length=8.0, height=3.5, thickness=1.0, mat=None):
    bm = bmesh.new()
    segments = int(length / 1.2)
    # Base wall verts with random top erosion
    verts = []
    for i in range(segments + 1):
        x = (i / segments) * length - length * 0.5
        h = height * rng.uniform(0.55, 1.0)
        verts.append(bm.verts.new((x, 0, 0)))
        verts.append(bm.verts.new((x, 0, h)))
        verts.append(bm.verts.new((x, thickness, 0)))
        verts.append(bm.verts.new((x, thickness, h)))
    bm.verts.ensure_lookup_table()
    n = segments + 1
    for i in range(segments):
        b = i * 4
        # front face
        bm.faces.new([verts[b], verts[b+1], verts[b+5], verts[b+4]])
        # back face
        bm.faces.new([verts[b+2], verts[b+6], verts[b+7], verts[b+3]])
        # top face
        bm.faces.new([verts[b+1], verts[b+3], verts[b+7], verts[b+5]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_ruin_column(name, height=5.5, radius=0.36, flutes=10, mat=None):
    bm = bmesh.new()
    segs = flutes * 4
    rings = 16
    verts_grid = []
    for r in range(rings + 1):
        t = r / rings
        z = t * height
        ring_verts = []
        for s in range(segs):
            ang = 2 * math.pi * s / segs
            flute_r = radius + 0.045 * math.cos(flutes * ang)
            taper = 1.0 - 0.12 * t
            x = flute_r * taper * math.cos(ang)
            y = flute_r * taper * math.sin(ang)
            ring_verts.append(bm.verts.new((x, y, z)))
        verts_grid.append(ring_verts)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            ns2 = (s + 1) % segs
            bm.faces.new([verts_grid[r][s], verts_grid[r][ns2],
                          verts_grid[r+1][ns2], verts_grid[r+1][s]])
    # capital slab
    cap_h = 0.4
    cap_r = radius * 1.5
    cap_verts = [bm.verts.new((cap_r * math.cos(2*math.pi*i/8),
                               cap_r * math.sin(2*math.pi*i/8),
                               height + cap_h)) for i in range(8)]
    base_cap = [bm.verts.new((cap_r * math.cos(2*math.pi*i/8),
                               cap_r * math.sin(2*math.pi*i/8),
                               height)) for i in range(8)]
    for i in range(8):
        bm.faces.new([base_cap[i], base_cap[(i+1)%8], cap_verts[(i+1)%8], cap_verts[i]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_obelisk(name, height=7.0, base_w=0.9, mat=None):
    bm = bmesh.new()
    rings = 20
    verts_ring = []
    for r in range(rings + 1):
        t = r / rings
        z = t * height
        taper = 1.0 - t * 0.85
        w = base_w * taper * 0.5
        ring = []
        for cx, cy in [(-w,-w),( w,-w),( w, w),(-w, w)]:
            ring.append(bm.verts.new((cx, cy, z + rng.uniform(-0.02, 0.02))))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(4):
            ns2 = (s + 1) % 4
            bm.faces.new([verts_ring[r][s], verts_ring[r][ns2],
                          verts_ring[r+1][ns2], verts_ring[r+1][s]])
    # pyramid tip
    tip = bm.verts.new((0, 0, height + 0.5))
    for s in range(4):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%4], tip])
    # inscribe rune grooves on each face (loop cuts)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_archway(name, span=4.0, height=5.0, thickness=0.8, mat=None):
    bm = bmesh.new()
    segs = 20
    def arch_pt(t):
        ang = math.pi * t
        return (span * 0.5 * math.cos(math.pi - ang),
                0.0,
                height - span * 0.5 + span * 0.5 * math.sin(ang))
    # outer arch ring
    o_pts, i_pts = [], []
    for i in range(segs + 1):
        t = i / segs
        ox, _, oz = arch_pt(t)
        o_pts.append(bm.verts.new((ox * 1.0,  thickness * 0.5, oz)))
        i_pts.append(bm.verts.new((ox * 0.85, thickness * 0.5, oz * 0.95 + 0.1)))
    o_pts2, i_pts2 = [], []
    for i in range(segs + 1):
        t = i / segs
        ox, _, oz = arch_pt(t)
        o_pts2.append(bm.verts.new((ox * 1.0, -thickness * 0.5, oz)))
        i_pts2.append(bm.verts.new((ox * 0.85,-thickness * 0.5, oz * 0.95 + 0.1)))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        bm.faces.new([o_pts[i], o_pts[i+1], o_pts2[i+1], o_pts2[i]])
        bm.faces.new([i_pts[i], i_pts2[i], i_pts2[i+1], i_pts[i+1]])
        bm.faces.new([o_pts[i], i_pts[i], i_pts[i+1], o_pts[i+1]])
        bm.faces.new([o_pts2[i], o_pts2[i+1], i_pts2[i+1], i_pts2[i]])
    # pillars
    for px in [-span * 0.5, span * 0.5]:
        for rz in range(12):
            z0 = rz * (height - span * 0.5) / 11
            z1 = (rz+1) * (height - span * 0.5) / 11
            r2 = 0.32
            pts_bot = [bm.verts.new((px + r2*math.cos(2*math.pi*k/8),
                                     r2*math.sin(2*math.pi*k/8), z0)) for k in range(8)]
            pts_top = [bm.verts.new((px + r2*math.cos(2*math.pi*k/8),
                                     r2*math.sin(2*math.pi*k/8), z1)) for k in range(8)]
            for k in range(8):
                bm.faces.new([pts_bot[k], pts_bot[(k+1)%8],
                               pts_top[(k+1)%8], pts_top[k]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_floor_tile_field(name, tiles_x=8, tiles_y=8, tile_size=1.2, mat=None):
    bm = bmesh.new()
    for tx in range(tiles_x):
        for ty in range(tiles_y):
            if rng.random() < 0.15: continue  # missing tiles for ruin feel
            x0 = tx * tile_size - tiles_x * tile_size * 0.5
            y0 = ty * tile_size - tiles_y * tile_size * 0.5
            gap = 0.04
            h = rng.uniform(-0.06, 0.06)
            v0 = bm.verts.new((x0 + gap, y0 + gap, h))
            v1 = bm.verts.new((x0 + tile_size - gap, y0 + gap, h + rng.uniform(-0.02,0.02)))
            v2 = bm.verts.new((x0 + tile_size - gap, y0 + tile_size - gap, h + rng.uniform(-0.02,0.02)))
            v3 = bm.verts.new((x0 + gap, y0 + tile_size - gap, h + rng.uniform(-0.02,0.02)))
            bm.faces.new([v0, v1, v2, v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_altar_dais(name, tiers=3, mat=None):
    bm = bmesh.new()
    for tier in range(tiers):
        s = (tiers - tier) * 2.2
        z0 = tier * 0.45
        z1 = z0 + 0.45
        corners = [(-s,-s,z0),(s,-s,z0),(s,s,z0),(-s,s,z0),
                   (-s,-s,z1),(s,-s,z1),(s,s,z1),(-s,s,z1)]
        bv = [bm.verts.new(c) for c in corners]
        faces = [(0,1,2,3),(4,5,6,7),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
        for f in faces: bm.faces.new([bv[i] for i in f])
    # altar top stone
    ts = 1.2; tz = tiers * 0.45
    tv = [bm.verts.new(c) for c in [(-ts,-ts,tz),(ts,-ts,tz),(ts,ts,tz),(-ts,ts,tz),
                                     (-ts,-ts,tz+0.6),(ts,-ts,tz+0.6),(ts,ts,tz+0.6),(-ts,ts,tz+0.6)]]
    for f in [(0,1,2,3),(4,5,6,7),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([tv[i] for i in f])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_rubble_pile(name, count=18, spread=2.5, mat=None):
    bm = bmesh.new()
    for _ in range(count):
        cx = rng.uniform(-spread, spread)
        cy = rng.uniform(-spread, spread)
        cz = rng.uniform(0, 0.5)
        sx = rng.uniform(0.1, 0.6)
        sy = rng.uniform(0.1, 0.5)
        sz = rng.uniform(0.05, 0.3)
        rot = rng.uniform(0, math.pi)
        corners_base = [
            (-sx*math.cos(rot)+sy*math.sin(rot), -sx*math.sin(rot)-sy*math.cos(rot), cz),
            ( sx*math.cos(rot)+sy*math.sin(rot),  sx*math.sin(rot)-sy*math.cos(rot), cz),
            ( sx*math.cos(rot)-sy*math.sin(rot),  sx*math.sin(rot)+sy*math.cos(rot), cz),
            (-sx*math.cos(rot)-sy*math.sin(rot), -sx*math.sin(rot)+sy*math.cos(rot), cz),
        ]
        corners_top = [(c[0]+cx, c[1]+cy, cz+sz) for c in corners_base]
        corners_base = [(c[0]+cx, c[1]+cy, c[2]) for c in corners_base]
        bv_b = [bm.verts.new(c) for c in corners_base]
        bv_t = [bm.verts.new(c) for c in corners_top]
        bm.faces.new(bv_b)
        bm.faces.new(bv_t[::-1])
        for i in range(4):
            bm.faces.new([bv_b[i], bv_b[(i+1)%4], bv_t[(i+1)%4], bv_t[i]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_vine_drape(name, attach_x, attach_z, length=2.5, strands=5, mat=None):
    bm = bmesh.new()
    for s in range(strands):
        ox = attach_x + rng.uniform(-0.3, 0.3)
        oz = attach_z
        segs = 12
        for seg in range(segs):
            t = seg / segs
            t2 = (seg+1) / segs
            sag = 0.3 * math.sin(math.pi * t)
            sag2 = 0.3 * math.sin(math.pi * t2)
            p0 = (ox + sag, rng.uniform(-0.05,0.05), oz - t * length)
            p1 = (ox + sag2, rng.uniform(-0.05,0.05), oz - t2 * length)
            w = 0.025
            v0 = bm.verts.new((p0[0]-w, p0[1], p0[2]))
            v1 = bm.verts.new((p0[0]+w, p0[1], p0[2]))
            v2 = bm.verts.new((p1[0]+w, p1[1], p1[2]))
            v3 = bm.verts.new((p1[0]-w, p1[1], p1[2]))
            bm.faces.new([v0, v1, v2, v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_relief_panel(name, width=2.0, height=1.5, mat=None):
    bm = bmesh.new()
    # panel face
    verts = [bm.verts.new(c) for c in [
        (-width/2, 0, 0), (width/2, 0, 0),
        (width/2, 0, height), (-width/2, 0, height)]]
    bm.faces.new(verts)
    # carved relief bands
    for band in range(5):
        bz = height * (band + 0.5) / 5.0
        bh = height * 0.06
        br = 0.04  # relief depth
        bv = [bm.verts.new(c) for c in [
            (-width/2*0.9, -br, bz), (width/2*0.9, -br, bz),
            (width/2*0.9, -br, bz + bh), (-width/2*0.9, -br, bz + bh)]]
        bm.faces.new(bv)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_firefly_sphere(name, loc, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.06)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    if mat: assign_mat(obj, mat)
    return obj

def build_broken_beam(name, length=3.5, w=0.22, mat=None):
    bm = bmesh.new()
    segs = 10
    for i in range(segs):
        t0 = i / segs; t1 = (i+1) / segs
        z0 = t0 * length; z1 = t1 * length
        sag = 0.15 * math.sin(math.pi * t0)
        sag2 = 0.15 * math.sin(math.pi * t1)
        pts_b = [(-w/2, -w/2, z0+sag), (w/2,-w/2, z0+sag),
                 (w/2,  w/2, z0+sag), (-w/2, w/2, z0+sag)]
        pts_t = [(-w/2, -w/2, z1+sag2),(w/2,-w/2, z1+sag2),
                 (w/2,  w/2, z1+sag2), (-w/2, w/2, z1+sag2)]
        bv_b = [bm.verts.new(p) for p in pts_b]
        bv_t = [bm.verts.new(p) for p in pts_t]
        for k in range(4):
            bm.faces.new([bv_b[k], bv_b[(k+1)%4], bv_t[(k+1)%4], bv_t[k]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_well(name, mat=None):
    bm = bmesh.new()
    segs = 16; r_out = 0.80; r_in = 0.60
    rings = 8; height = 1.0
    for ring in range(rings):
        z0 = ring * height / rings
        z1 = (ring+1) * height / rings
        for s in range(segs):
            a0 = 2*math.pi*s/segs; a1 = 2*math.pi*(s+1)/segs
            rvar = rng.uniform(0.97, 1.03)
            pts = [(r_out*rvar*math.cos(a0), r_out*rvar*math.sin(a0), z0),
                   (r_out*rvar*math.cos(a1), r_out*rvar*math.sin(a1), z0),
                   (r_out*rvar*math.cos(a1), r_out*rvar*math.sin(a1), z1),
                   (r_out*rvar*math.cos(a0), r_out*rvar*math.sin(a0), z1)]
            bm.faces.new([bm.verts.new(p) for p in pts])
    # rim
    for s in range(segs):
        a0 = 2*math.pi*s/segs; a1 = 2*math.pi*(s+1)/segs
        pts = [(r_out*math.cos(a0), r_out*math.sin(a0), height),
               (r_out*math.cos(a1), r_out*math.sin(a1), height),
               (r_in*math.cos(a1), r_in*math.sin(a1), height),
               (r_in*math.cos(a0), r_in*math.sin(a0), height)]
        bm.faces.new([bm.verts.new(p) for p in pts])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_stone_statue_base(name, mat=None):
    bm = bmesh.new()
    # stepped pedestal
    for tier in range(3):
        s = (3 - tier) * 0.65
        z0 = tier * 0.35; z1 = z0 + 0.35
        segs = 8
        pts_b = [(s*math.cos(2*math.pi*i/segs), s*math.sin(2*math.pi*i/segs), z0) for i in range(segs)]
        pts_t = [(s*math.cos(2*math.pi*i/segs), s*math.sin(2*math.pi*i/segs), z1) for i in range(segs)]
        bv_b = [bm.verts.new(p) for p in pts_b]
        bv_t = [bm.verts.new(p) for p in pts_t]
        bm.faces.new(bv_b[::-1])
        bm.faces.new(bv_t)
        for i in range(segs):
            bm.faces.new([bv_b[i], bv_b[(i+1)%segs], bv_t[(i+1)%segs], bv_t[i]])
    # rough torso block
    tz = 1.05; ts = 0.45; th = 1.4
    tv = [bm.verts.new(c) for c in [
        (-ts,-ts,tz),(ts,-ts,tz),(ts,ts,tz),(-ts,ts,tz),
        (-ts*0.8,-ts*0.8,tz+th),(ts*0.8,-ts*0.8,tz+th),
        (ts*0.8,ts*0.8,tz+th),(-ts*0.8,ts*0.8,tz+th)]]
    for f in [(0,1,2,3),(4,5,6,7),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([tv[i] for i in f])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

# ── scene assembly ────────────────────────────────────────────────────────────
def build_scene():
    # clean slate
    for o in list(bpy.data.objects):  bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):   bpy.data.meshes.remove(m, do_unlink=True)
    for m in list(bpy.data.materials):bpy.data.materials.remove(m, do_unlink=True)

    col = bpy.data.collections.new("AncientRuins")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'moss':    build_mossy_stone_mat(),
        'carved':  build_carved_stone_mat(),
        'floor':   build_ancient_floor_mat(),
        'wood':    build_ruin_wood_mat(),
        'rune':    build_rune_glow_mat((0.3, 0.85, 0.5)),
        'vine':    build_vine_mat(),
        'dust':    build_dust_mat(),
        'firefly': build_firefly_mat(),
    }

    objs = []

    # ── ground courtyard floor ──
    floor = build_floor_tile_field("Ruins_CourtFloor_A", 10, 10, 1.1, mats['floor'])
    floor.location = (0, 0, 0)
    link(col, floor); objs.append(floor)

    floor2 = build_floor_tile_field("Ruins_CourtFloor_B", 6, 6, 1.0, mats['floor'])
    floor2.location = (14, 0, -0.4)
    link(col, floor2); objs.append(floor2)

    # ── crumbled walls (perimeter) ──
    wall_configs = [
        ("Ruins_Wall_North",    10.0, 3.8, 1.0,  ( 0,  7, 0), (0, 0, 0)),
        ("Ruins_Wall_South",     8.0, 2.5, 0.9,  ( 0, -7, 0), (0, 0, 0)),
        ("Ruins_Wall_East",      9.0, 4.2, 1.1,  ( 8,  0, 0), (0, 0, math.pi/2)),
        ("Ruins_Wall_West",      7.0, 3.0, 0.9,  (-8,  0, 0), (0, 0, math.pi/2)),
        ("Ruins_Wall_Inner_A",   5.0, 2.2, 0.8,  ( 4,  3, 0), (0, 0, math.pi/4)),
        ("Ruins_Wall_Inner_B",   4.5, 1.8, 0.7,  (-3, -4, 0), (0, 0, math.pi/6)),
    ]
    for wname, wl, wh, wt, wloc, wrot in wall_configs:
        w = build_crumbled_wall(wname, wl, wh, wt, mats['moss'])
        w.location = wloc; w.rotation_euler = wrot
        link(col, w); objs.append(w)

    # ── columns ──
    col_positions = [
        (-4, -5, 0, 5.5), ( 4, -5, 0, 5.0), (-4, 5, 0, 5.8), ( 4, 5, 0, 4.2),
        (-8, -2, 0, 6.0), ( 8, -2, 0, 3.5), (-8,  2, 0, 5.2), (10,  4, 0, 4.8),
    ]
    for ci, (cx, cy, cz, ch) in enumerate(col_positions):
        c_obj = build_ruin_column(f"Ruins_Column_{ci:02d}", ch, 0.34, 10, mats['carved'])
        c_obj.location = (cx, cy, cz)
        link(col, c_obj); objs.append(c_obj)

    # ── obelisks ──
    ob1 = build_obelisk("Ruins_Obelisk_A", 7.5, 0.9, mats['carved'])
    ob1.location = (-12, 0, 0)
    link(col, ob1); objs.append(ob1)

    ob2 = build_obelisk("Ruins_Obelisk_B", 5.5, 0.7, mats['rune'])
    ob2.location = (15, -4, 0); ob2.rotation_euler = (0, 0.15, 0)
    link(col, ob2); objs.append(ob2)

    ob3 = build_obelisk("Ruins_Obelisk_C", 4.0, 0.6, mats['moss'])
    ob3.location = (15, 4, 0); ob3.rotation_euler = (0.1, 0, 0.05)
    link(col, ob3); objs.append(ob3)

    # ── arches ──
    arch1 = build_archway("Ruins_Arch_Main", 5.5, 6.0, 0.9, mats['moss'])
    arch1.location = (0, 7, 0)
    link(col, arch1); objs.append(arch1)

    arch2 = build_archway("Ruins_Arch_Side", 3.5, 4.5, 0.75, mats['carved'])
    arch2.location = (-8, 0, 0); arch2.rotation_euler = (0, 0, math.pi/2)
    link(col, arch2); objs.append(arch2)

    arch3 = build_archway("Ruins_Arch_Broken", 4.0, 3.8, 0.8, mats['moss'])
    arch3.location = (14, 5, 0); arch3.rotation_euler = (0.08, 0, math.pi/4)
    link(col, arch3); objs.append(arch3)

    # ── altar dais (central focus) ──
    altar = build_altar_dais("Ruins_Altar_Main", 3, mats['carved'])
    altar.location = (0, 0, 0)
    link(col, altar); objs.append(altar)

    # rune glow altar stone on top
    rune_stone = build_obelisk("Ruins_RuneStone_Altar", 1.2, 0.25, mats['rune'])
    rune_stone.location = (0, 0, 1.4)
    link(col, rune_stone); objs.append(rune_stone)

    # ── rubble piles ──
    rubble_locs = [(-6,4,0), (6,-4,0), (-2,-7,0), (10,0,0), (-10,5,0), (4,8,0)]
    for ri, rloc in enumerate(rubble_locs):
        rb = build_rubble_pile(f"Ruins_Rubble_{ri:02d}", 16, 2.2, mats['moss'])
        rb.location = rloc
        link(col, rb); objs.append(rb)

    # ── relief panels ──
    panel_cfgs = [
        ("Ruins_Panel_A", 2.0, 1.5, ( 0, 7.05, 1.0), (0, 0, 0)),
        ("Ruins_Panel_B", 1.8, 1.3, (-4, 7.05, 0.8), (0, 0, 0)),
        ("Ruins_Panel_C", 1.6, 1.2, ( 8, 0.05, 1.0), (0, 0, math.pi/2)),
    ]
    for pname, pw, ph, ploc, prot in panel_cfgs:
        p = build_relief_panel(pname, pw, ph, mats['carved'])
        p.location = ploc; p.rotation_euler = prot
        link(col, p); objs.append(p)

    # ── vine drapes ──
    vine_cfgs = [
        ("Ruins_Vines_A", -4.0, 5.5, 2.8),
        ("Ruins_Vines_B",  4.0, 4.2, 2.5),
        ("Ruins_Vines_C", -8.0, 3.0, 3.0),
        ("Ruins_Vines_D",  0.0, 6.5, 2.2),
    ]
    for vname, vx, vz, vl in vine_cfgs:
        vd = build_vine_drape(vname, vx, vz, vl, 6, mats['vine'])
        link(col, vd); objs.append(vd)

    # ── wooden beams (collapsed roof) ──
    beam_cfgs = [
        ("Ruins_Beam_A", 4.5, 0.24, (-2, 1, 2.5), (0.4, 0.1, 0.3)),
        ("Ruins_Beam_B", 3.8, 0.20, ( 3,-2, 1.8), (0.2, 0.3, 0.8)),
        ("Ruins_Beam_C", 5.0, 0.26, (-5,-3, 3.0), (0.5, 0.0, 0.1)),
    ]
    for bname, bl, bw, bloc, brot in beam_cfgs:
        bm_obj = build_broken_beam(bname, bl, bw, mats['wood'])
        bm_obj.location = bloc; bm_obj.rotation_euler = brot
        link(col, bm_obj); objs.append(bm_obj)

    # ── stone well ──
    well = build_well("Ruins_Well", mats['moss'])
    well.location = (5, 5, 0)
    link(col, well); objs.append(well)

    # ── stone statue bases ──
    statue1 = build_stone_statue_base("Ruins_Statue_A", mats['carved'])
    statue1.location = (-3, 5, 0)
    link(col, statue1); objs.append(statue1)

    statue2 = build_stone_statue_base("Ruins_Statue_B", mats['moss'])
    statue2.location = (3, 5, 0)
    link(col, statue2); objs.append(statue2)

    # ── dust patches ──
    for di in range(5):
        bm2 = bmesh.new()
        cx = rng.uniform(-8, 8); cy = rng.uniform(-8, 8)
        rx = rng.uniform(1.5, 3.0); ry = rng.uniform(1.0, 2.5)
        for vv in range(12):
            ang = 2*math.pi*vv/12
            bm2.verts.new((cx + rx*math.cos(ang), cy + ry*math.sin(ang), 0.01))
        bm2.verts.ensure_lookup_table()
        bm2.faces.new(bm2.verts)
        mesh2 = bpy.data.meshes.new(f"Ruins_Dust_{di:02d}")
        bm2.to_mesh(mesh2); bm2.free()
        d_obj = bpy.data.objects.new(f"Ruins_Dust_{di:02d}", mesh2)
        assign_mat(d_obj, mats['dust'])
        smart_uv(d_obj)
        link(col, d_obj); objs.append(d_obj)

    # ── firefly glow spheres ──
    firefly_locs = [
        (2, 3, 2.5), (-3, 4, 1.8), (0, -2, 3.0), (5, 1, 2.2),
        (-5, -2, 1.5), (1, 6, 2.8), (-1, -5, 2.0), (4, -3, 1.6),
    ]
    for fi, floc in enumerate(firefly_locs):
        ff = build_firefly_sphere(f"Ruins_Firefly_{fi:02d}", floc, mats['firefly'])
        link(col, ff); objs.append(ff)
        add_pt_light(col, floc, energy=rng.uniform(0.8, 2.5),
                     color=(0.5, 1.0, 0.3), radius=0.1)

    # ── central altar point light (eerie green glow) ──
    add_pt_light(col, (0, 0, 1.8), energy=12.0, color=(0.3, 0.9, 0.4), radius=0.5)
    add_pt_light(col, (15, -4, 4.0), energy=6.0, color=(0.4, 0.7, 1.0), radius=0.3)

    print(f"[AncientRuins] Built {len(objs)} objects in collection '{col.name}'")
    print("Export: File → Export → FBX, select collection, apply transforms.")

build_scene()
