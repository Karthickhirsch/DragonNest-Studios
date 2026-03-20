"""
35_Environment_CaveSystems.py
IsleTrial — Cave Systems Environment Set
================================================
Creates a dramatic underground cave environment: stalactite/stalagmite
forests, cave pools, crystal formations, collapsed tunnels, bone piles,
glowing mineral veins, cave mushrooms, underground waterfalls (mesh proxy),
rubble choke-points, hanging roots, drip stalactites, and cave floor
with pebble scatter.

All materials use full procedural node networks + [UNITY] image slots.
smart_uv() applied to every mesh.  Run in Blender ≥ 3.6.
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(350035)

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
def build_cave_rock_mat():
    mat = bpy.data.materials.new("Mat_Cave_Rock")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.90
    bsdf.inputs['Metallic'].default_value  = 0.0
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-600, 200)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value   = 5.5
    mus.inputs['Detail'].default_value  = 9.0
    mus.inputs['Dimension'].default_value = 1.3
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.06, 0.05, 0.05, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.28, 0.24, 0.22, 1)
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-600,-100)
    noise.inputs['Scale'].default_value  = 18.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.7
    cr2  = ns.new('ShaderNodeValToRGB');       cr2.location  = (-300,-100)
    cr2.color_ramp.elements[0].position = 0.2
    cr2.color_ramp.elements[0].color = (0.10, 0.09, 0.08, 1)
    cr2.color_ramp.elements[1].position = 0.9
    cr2.color_ramp.elements[1].color = (0.32, 0.28, 0.25, 1)
    mix  = ns.new('ShaderNodeMixRGB');         mix.location  = (50, 100)
    mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = 0.5
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 2.0
    bmp.inputs['Distance'].default_value = 0.05
    img_a = img_slot(ns,"[UNITY] CaveRock_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] CaveRock_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] CaveRock_Roughness", -660,-750)
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

def build_cave_crystal_mat(hue=(0.3, 0.9, 0.8)):
    mat = bpy.data.materials.new("Mat_Cave_Crystal")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (750, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 150)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Transmission Weight'].default_value = 0.85
    bsdf.inputs['IOR'].default_value = 1.55
    bsdf.inputs['Emission Color'].default_value = (*hue, 1)
    bsdf.inputs['Emission Strength'].default_value = 2.5
    bsdf.inputs['Base Color'].default_value = (*[v*0.6 for v in hue], 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (450,-150)
    em.inputs['Color'].default_value    = (*hue, 1)
    em.inputs['Strength'].default_value = 4.0
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-400, 0)
    noise.inputs['Scale'].default_value  = 12.0
    noise.inputs['Detail'].default_value = 3.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-150, 0)
    cr.color_ramp.elements[0].position = 0.4; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] Crystal_Emission",-660,-300)
    img_a = img_slot(ns,"[UNITY] Crystal_Albedo",  -660,-500)
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_wet_rock_mat():
    mat = bpy.data.materials.new("Mat_Cave_WetRock")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.20
    bsdf.inputs['Specular IOR Level'].default_value = 0.7
    bsdf.inputs['Base Color'].default_value = (0.06, 0.07, 0.09, 1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'
    vor.inputs['Scale'].default_value = 4.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.5
    bmp.inputs['Distance'].default_value = 0.02
    img_a = img_slot(ns,"[UNITY] WetRock_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] WetRock_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] WetRock_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    mix2.inputs['Color1'].default_value = (0.06, 0.07, 0.09, 1)
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(vor.outputs['Distance'],bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_cave_pool_mat():
    mat = bpy.data.materials.new("Mat_Cave_Pool")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['Transmission Weight'].default_value = 0.75
    bsdf.inputs['IOR'].default_value = 1.33
    bsdf.inputs['Base Color'].default_value = (0.02, 0.06, 0.12, 1)
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-550, 200)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value      = 1.5
    wave.inputs['Distortion'].default_value = 2.0
    wave.inputs['Detail'].default_value     = 3.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 0.3
    bmp.inputs['Distance'].default_value = 0.01
    img_n = img_slot(ns,"[UNITY] CavePool_Normal", -660,-350)
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_cave_mushroom_mat():
    mat = bpy.data.materials.new("Mat_Cave_Mushroom")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (750, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 100)
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Emission Color'].default_value = (0.1, 0.8, 0.5, 1)
    bsdf.inputs['Emission Strength'].default_value = 1.5
    em   = ns.new('ShaderNodeEmission');       em.location   = (450,-100)
    em.inputs['Color'].default_value    = (0.1, 0.8, 0.5, 1)
    em.inputs['Strength'].default_value = 3.0
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-400, 100)
    noise.inputs['Scale'].default_value  = 15.0
    noise.inputs['Detail'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-150, 100)
    cr.color_ramp.elements[0].position = 0.0
    cr.color_ramp.elements[0].color = (0.02, 0.12, 0.06, 1)
    cr.color_ramp.elements[1].position = 1.0
    cr.color_ramp.elements[1].color = (0.08, 0.55, 0.30, 1)
    img_a = img_slot(ns,"[UNITY] Mushroom_Albedo",   -660,-300)
    img_e = img_slot(ns,"[UNITY] Mushroom_Emission", -660,-500)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (200, 100)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_mineral_vein_mat():
    mat = bpy.data.materials.new("Mat_Cave_MineralVein")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (750, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 150)
    bsdf.inputs['Roughness'].default_value = 0.15
    bsdf.inputs['Metallic'].default_value  = 0.6
    bsdf.inputs['Base Color'].default_value = (0.55, 0.82, 0.55, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (450,-150)
    em.inputs['Color'].default_value    = (0.2, 1.0, 0.4, 1)
    em.inputs['Strength'].default_value = 2.5
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-500, 0)
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value      = 8.0
    wave.inputs['Distortion'].default_value = 3.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.45; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.60; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_a = img_slot(ns,"[UNITY] MineralVein_Albedo",   -660,-350)
    img_e = img_slot(ns,"[UNITY] MineralVein_Emission", -660,-550)
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_cave_floor_mat():
    mat = bpy.data.materials.new("Mat_Cave_Floor")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.95
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-550, 200)
    mus.musgrave_type = 'FBM'
    mus.inputs['Scale'].default_value  = 3.0
    mus.inputs['Detail'].default_value = 8.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-250, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.05, 0.04, 0.04, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.18, 0.16, 0.14, 1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.6
    bmp.inputs['Distance'].default_value = 0.06
    img_a = img_slot(ns,"[UNITY] CaveFloor_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] CaveFloor_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] CaveFloor_Roughness", -660,-750)
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

def build_root_mat():
    mat = bpy.data.materials.new("Mat_Cave_Root")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.88
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-500, 200)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value      = 8.0
    wave.inputs['Distortion'].default_value = 3.5
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-200, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.08, 0.05, 0.02, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.25, 0.16, 0.08, 1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.0
    img_a = img_slot(ns,"[UNITY] Root_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] Root_Normal", -660,-550)
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

def build_bone_mat():
    mat = bpy.data.materials.new("Mat_Cave_Bone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Roughness'].default_value = 0.78
    bsdf.inputs['Base Color'].default_value = (0.75, 0.70, 0.58, 1)
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-400, 150)
    noise.inputs['Scale'].default_value  = 25.0
    noise.inputs['Detail'].default_value = 4.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-100, 150)
    cr1.color_ramp.elements[0].position = 0.3
    cr1.color_ramp.elements[0].color = (0.60, 0.55, 0.42, 1)
    cr1.color_ramp.elements[1].position = 0.8
    cr1.color_ramp.elements[1].color = (0.82, 0.77, 0.64, 1)
    img_a = img_slot(ns,"[UNITY] Bone_Albedo", -660,-300)
    img_n = img_slot(ns,"[UNITY] Bone_Normal", -660,-500)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (280, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

# ── geometry builders ─────────────────────────────────────────────────────────
def build_cave_ceiling(name, rx=18, ry=14, mat=None):
    bm = bmesh.new()
    segs_x, segs_y = 22, 18
    verts = []
    for iy in range(segs_y + 1):
        row = []
        for ix in range(segs_x + 1):
            fx = (ix / segs_x - 0.5) * 2 * rx
            fy = (iy / segs_y - 0.5) * 2 * ry
            r = math.sqrt((fx/rx)**2 + (fy/ry)**2)
            fz = 8.0 + 3.5 * math.cos(r * math.pi * 0.5) + rng.uniform(-0.6, 0.6)
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

def build_cave_floor_mesh(name, rx=18, ry=14, mat=None):
    bm = bmesh.new()
    segs_x, segs_y = 20, 16
    verts = []
    for iy in range(segs_y + 1):
        row = []
        for ix in range(segs_x + 1):
            fx = (ix / segs_x - 0.5) * 2 * rx
            fy = (iy / segs_y - 0.5) * 2 * ry
            fz = rng.uniform(-0.4, 0.4) + 0.5 * math.sin(fx * 0.4) * math.cos(fy * 0.4)
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

def build_stalactite(name, length=2.5, base_r=0.22, mat=None):
    bm = bmesh.new()
    segs = 10; rings = 14
    verts_ring = []
    for r in range(rings + 1):
        t = r / rings
        z = -t * length
        radius = base_r * (1.0 - t) * (1.0 + 0.08 * math.sin(t * math.pi * 6))
        if radius < 0.005: radius = 0.005
        ring = []
        for s in range(segs):
            ang = 2*math.pi*s/segs + rng.uniform(-0.05, 0.05)
            ring.append(bm.verts.new((radius * math.cos(ang), radius * math.sin(ang), z)))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0, 0, -length - 0.05))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_stalagmite(name, height=2.0, base_r=0.28, mat=None):
    bm = bmesh.new()
    segs = 10; rings = 14
    verts_ring = []
    for r in range(rings + 1):
        t = r / rings; z = t * height
        radius = base_r * (1.0 - t * 0.92) * (1.0 + 0.06 * math.sin(t * math.pi * 5))
        if radius < 0.005: radius = 0.005
        ring = []
        for s in range(segs):
            ang = 2*math.pi*s/segs + rng.uniform(-0.04, 0.04)
            ring.append(bm.verts.new((radius*math.cos(ang), radius*math.sin(ang), z)))
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((rng.uniform(-0.02,0.02), rng.uniform(-0.02,0.02), height + 0.06))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_crystal_cluster(name, count=5, mat=None):
    bm = bmesh.new()
    for _ in range(count):
        cx = rng.uniform(-0.4, 0.4); cy = rng.uniform(-0.4, 0.4)
        h = rng.uniform(0.5, 1.8)
        r = rng.uniform(0.06, 0.16)
        tilt_x = rng.uniform(-0.25, 0.25)
        tilt_y = rng.uniform(-0.25, 0.25)
        segs = 6
        pts_b = [(cx + r*math.cos(2*math.pi*s/segs), cy + r*math.sin(2*math.pi*s/segs), 0) for s in range(segs)]
        bv_b = [bm.verts.new(p) for p in pts_b]
        tip  = bm.verts.new((cx + tilt_x*h, cy + tilt_y*h, h))
        bm.faces.new(bv_b[::-1])
        for s in range(segs):
            bm.faces.new([bv_b[s], bv_b[(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_cave_pool_mesh(name, rx=3.5, ry=2.8, mat=None):
    bm = bmesh.new()
    segs = 20
    for s in range(segs):
        ang = 2*math.pi*s/segs
        r_var = 1.0 + 0.18 * rng.uniform(-1, 1)
        bm.verts.new((rx*r_var*math.cos(ang), ry*r_var*math.sin(ang), 0.02))
    bm.verts.ensure_lookup_table()
    bm.faces.new(bm.verts)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_cave_mushroom(name, cap_r=0.45, stem_h=0.55, mat=None):
    bm = bmesh.new()
    segs = 12
    # stem
    for ring in range(8):
        z0 = ring * stem_h / 7; z1 = (ring+1) * stem_h / 7
        sr = 0.08 * (1.0 - ring * 0.05)
        bv_b = [bm.verts.new((sr*math.cos(2*math.pi*s/segs), sr*math.sin(2*math.pi*s/segs), z0)) for s in range(segs)]
        bv_t = [bm.verts.new((sr*math.cos(2*math.pi*s/segs), sr*math.sin(2*math.pi*s/segs), z1)) for s in range(segs)]
        for s in range(segs):
            bm.faces.new([bv_b[s], bv_b[(s+1)%segs], bv_t[(s+1)%segs], bv_t[s]])
    # cap dome
    cap_segs = 14; cap_rings = 8
    cap_verts = []
    for r in range(cap_rings + 1):
        t = r / cap_rings
        ang_v = t * math.pi * 0.55
        cz = stem_h + cap_r * 0.45 * math.sin(ang_v)
        cr2 = cap_r * math.cos(ang_v - math.pi * 0.05)
        ring = [bm.verts.new((cr2*math.cos(2*math.pi*s/cap_segs),
                               cr2*math.sin(2*math.pi*s/cap_segs), cz)) for s in range(cap_segs)]
        cap_verts.append(ring)
    for r in range(cap_rings):
        for s in range(cap_segs):
            bm.faces.new([cap_verts[r][s], cap_verts[r][(s+1)%cap_segs],
                          cap_verts[r+1][(s+1)%cap_segs], cap_verts[r+1][s]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_hanging_root(name, drop=3.0, strands=6, mat=None):
    bm = bmesh.new()
    for s in range(strands):
        ox = rng.uniform(-0.5, 0.5); oy = rng.uniform(-0.5, 0.5)
        segs = 14; w = 0.015
        for seg in range(segs):
            t0 = seg / segs; t1 = (seg+1) / segs
            sway = 0.12 * math.sin(t0 * math.pi * 3 + s)
            z0 = -t0 * drop; z1 = -t1 * drop
            v0 = bm.verts.new((ox + sway - w, oy, z0))
            v1 = bm.verts.new((ox + sway + w, oy, z0))
            v2 = bm.verts.new((ox + sway + w, oy, z1))
            v3 = bm.verts.new((ox + sway - w, oy, z1))
            bm.faces.new([v0, v1, v2, v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_waterfall_proxy(name, width=2.0, height=6.0, mat=None):
    bm = bmesh.new()
    segs_w = 8; segs_h = 20
    for iw in range(segs_w):
        for ih in range(segs_h):
            x0 = (iw / segs_w - 0.5) * width
            x1 = ((iw+1) / segs_w - 0.5) * width
            z0 = -(ih / segs_h) * height
            z1 = -((ih+1) / segs_h) * height
            depth = 0.05 * math.sin(ih * 0.8 + iw * 0.5)
            v0 = bm.verts.new((x0, depth, z0))
            v1 = bm.verts.new((x1, depth, z0))
            v2 = bm.verts.new((x1, depth, z1))
            v3 = bm.verts.new((x0, depth, z1))
            bm.faces.new([v0, v1, v2, v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_collapsed_tunnel(name, length=8.0, mat=None):
    bm = bmesh.new()
    segs = 16; arch_segs = 10; radius = 2.0
    for i in range(segs):
        t = i / segs; t2 = (i+1) / segs
        z0 = t * length; z1 = t2 * length
        # partial arch (collapsed, varies per segment)
        max_ang = math.pi * rng.uniform(0.6, 1.0)
        ring0 = [bm.verts.new((radius*math.cos(a), radius*math.sin(a), z0))
                 for a in [k * max_ang / arch_segs for k in range(arch_segs + 1)]]
        ring1 = [bm.verts.new((radius*math.cos(a), radius*math.sin(a), z1))
                 for a in [k * max_ang / arch_segs for k in range(arch_segs + 1)]]
        for k in range(arch_segs):
            bm.faces.new([ring0[k], ring0[k+1], ring1[k+1], ring1[k]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_bone_pile(name, count=14, mat=None):
    bm = bmesh.new()
    for _ in range(count):
        cx = rng.uniform(-1.5, 1.5); cy = rng.uniform(-1.5, 1.5)
        bl = rng.uniform(0.2, 0.7); br = rng.uniform(0.02, 0.05)
        ang = rng.uniform(0, math.pi)
        segs = 6
        for seg in range(segs):
            t0 = seg / segs; t1 = (seg+1) / segs
            z0 = t0 * bl; z1 = t1 * bl
            r0 = br * (1 - t0 * 0.3); r1 = br * (1 - t1 * 0.3)
            pts_b = [(cx + r0*math.cos(a + ang), cy + r0*math.sin(a + ang), rng.uniform(0, 0.12))
                     for a in [2*math.pi*s/6 for s in range(6)]]
            pts_t = [(cx + r1*math.cos(a + ang), cy + r1*math.sin(a + ang), z1 * 0.4)
                     for a in [2*math.pi*s/6 for s in range(6)]]
            bv_b = [bm.verts.new(p) for p in pts_b]
            bv_t = [bm.verts.new(p) for p in pts_t]
            for k in range(6):
                bm.faces.new([bv_b[k], bv_b[(k+1)%6], bv_t[(k+1)%6], bv_t[k]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_mineral_vein_strip(name, length=6.0, mat=None):
    bm = bmesh.new()
    segs = 20
    for i in range(segs):
        t0 = i / segs; t1 = (i+1) / segs
        x0 = t0 * length - length * 0.5
        x1 = t1 * length - length * 0.5
        z_wave0 = 0.15 * math.sin(t0 * math.pi * 5)
        z_wave1 = 0.15 * math.sin(t1 * math.pi * 5)
        w = rng.uniform(0.06, 0.14); h = rng.uniform(0.04, 0.08)
        v0 = bm.verts.new((x0, -w, z_wave0))
        v1 = bm.verts.new((x0,  w, z_wave0))
        v2 = bm.verts.new((x1,  w, z_wave1 + h))
        v3 = bm.verts.new((x1, -w, z_wave1 + h))
        bm.faces.new([v0, v1, v2, v3])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

# ── scene assembly ────────────────────────────────────────────────────────────
def build_scene():
    for o in list(bpy.data.objects):   bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):    bpy.data.meshes.remove(m, do_unlink=True)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m, do_unlink=True)

    col = bpy.data.collections.new("CaveSystems")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'rock':     build_cave_rock_mat(),
        'crystal':  build_cave_crystal_mat((0.2, 0.9, 0.7)),
        'crystal2': build_cave_crystal_mat((0.8, 0.3, 1.0)),
        'wet':      build_wet_rock_mat(),
        'pool':     build_cave_pool_mat(),
        'mushroom': build_cave_mushroom_mat(),
        'vein':     build_mineral_vein_mat(),
        'floor':    build_cave_floor_mat(),
        'root':     build_root_mat(),
        'bone':     build_bone_mat(),
    }

    objs = []

    # cave structure
    ceiling = build_cave_ceiling("Cave_Ceiling", 18, 14, mats['wet'])
    link(col, ceiling); objs.append(ceiling)

    floor = build_cave_floor_mesh("Cave_Floor", 18, 14, mats['floor'])
    link(col, floor); objs.append(floor)

    tunnel = build_collapsed_tunnel("Cave_Tunnel_Main", 10.0, mats['rock'])
    tunnel.location = (0, 16, 0); tunnel.rotation_euler = (math.pi/2, 0, 0)
    link(col, tunnel); objs.append(tunnel)

    tunnel2 = build_collapsed_tunnel("Cave_Tunnel_Side", 7.0, mats['wet'])
    tunnel2.location = (14, 0, 0); tunnel2.rotation_euler = (math.pi/2, 0, math.pi/2)
    link(col, tunnel2); objs.append(tunnel2)

    # stalactites
    stalac_cfgs = [
        (0, 8, 8.5, 3.0, 0.26), (-4, 6, 9.0, 2.2, 0.20), (4, 6, 8.8, 3.5, 0.30),
        (-6, 0, 8.2, 2.8, 0.24), (6, 0, 9.5, 4.0, 0.28), (-2,-5, 8.0, 2.5, 0.22),
        (2,-5, 9.2, 3.2, 0.25), (-8, 4, 8.6, 2.0, 0.18), (8, 4, 8.4, 1.8, 0.16),
        (0,-8, 9.0, 3.8, 0.32), (-4,-2, 8.5, 2.6, 0.21), (4,-2, 8.3, 2.4, 0.19),
    ]
    for si, (sx, sy, sz, sl, sr) in enumerate(stalac_cfgs):
        st = build_stalactite(f"Cave_Stalactite_{si:02d}", sl, sr, mats['wet'])
        st.location = (sx, sy, sz)
        link(col, st); objs.append(st)

    # stalagmites
    stalag_cfgs = [
        (3, 7, 0, 2.5, 0.28), (-3, 7, 0, 1.8, 0.22), (5,-4, 0, 3.0, 0.32),
        (-5,-4, 0, 2.2, 0.26), (7, 2, 0, 1.5, 0.18), (-7, 2, 0, 2.8, 0.30),
        (1,-8, 0, 2.0, 0.24), (-1,-8, 0, 1.6, 0.20),
    ]
    for si, (sx, sy, sz, sh, sr) in enumerate(stalag_cfgs):
        sm = build_stalagmite(f"Cave_Stalagmite_{si:02d}", sh, sr, mats['rock'])
        sm.location = (sx, sy, sz)
        link(col, sm); objs.append(sm)

    # crystal clusters
    crystal_cfgs = [
        ("Cave_Crystals_A", (8, -6, 0), (0,0,0),       5, mats['crystal']),
        ("Cave_Crystals_B", (-8,-8, 0), (0,0,0.8),     4, mats['crystal2']),
        ("Cave_Crystals_C", (10, 6, 0), (0,0,1.5),     6, mats['crystal']),
        ("Cave_Crystals_D", (-10,4, 0), (0.1,0,0),     3, mats['crystal2']),
        ("Cave_Crystals_E", (2,-12, 0), (0,0,2.0),     5, mats['crystal']),
        ("Cave_Crystals_F", (-2,12, 0), (0,0,0.4),     4, mats['crystal2']),
    ]
    for cname, cloc, crot, cnt, cmat in crystal_cfgs:
        cc = build_crystal_cluster(cname, cnt, cmat)
        cc.location = cloc; cc.rotation_euler = crot
        link(col, cc); objs.append(cc)
        add_pt_light(col, (cloc[0], cloc[1], cloc[2]+0.8),
                     energy=rng.uniform(3, 8),
                     color=(0.2,1.0,0.6) if cmat == mats['crystal'] else (0.8,0.3,1.0),
                     radius=0.2)

    # cave pools
    pool1 = build_cave_pool_mesh("Cave_Pool_A", 4.0, 3.2, mats['pool'])
    pool1.location = (-5, -5, 0.05)
    link(col, pool1); objs.append(pool1)

    pool2 = build_cave_pool_mesh("Cave_Pool_B", 2.5, 2.0, mats['pool'])
    pool2.location = (9, 3, 0.05)
    link(col, pool2); objs.append(pool2)

    add_pt_light(col, (-5,-5,0.5), energy=5.0, color=(0.1,0.4,0.8), radius=0.4)
    add_pt_light(col, (9, 3, 0.5), energy=4.0, color=(0.1,0.4,0.8), radius=0.3)

    # mushrooms
    mush_cfgs = [
        (2, 4, 0, 0.55, 0.65), (-3, 3, 0, 0.40, 0.50), (4,-3, 0, 0.35, 0.45),
        (-4,-6, 0, 0.60, 0.70), (6, 0, 0, 0.45, 0.55), (-6,-2, 0, 0.30, 0.40),
        (0, 6, 0, 0.50, 0.60), (3,-7, 0, 0.42, 0.52),
    ]
    for mi, (mx, my, mz, mcr, msh) in enumerate(mush_cfgs):
        ms = build_cave_mushroom(f"Cave_Mushroom_{mi:02d}", mcr, msh, mats['mushroom'])
        ms.location = (mx, my, mz)
        link(col, ms); objs.append(ms)
        add_pt_light(col, (mx, my, mz + msh + mcr * 0.5),
                     energy=rng.uniform(0.5,1.5), color=(0.1,0.8,0.5), radius=0.1)

    # hanging roots from ceiling
    root_cfgs = [
        (0, 5, 9, 3.5, 5), (-4, 2, 8.5, 3.0, 4), (4, 2, 9.2, 2.8, 6),
        (-2,-4, 8.8, 4.0, 5), (3,-6, 9.0, 3.2, 4),
    ]
    for ri, (rx2, ry2, rz2, rd, rstr) in enumerate(root_cfgs):
        rt = build_hanging_root(f"Cave_Root_{ri:02d}", rd, rstr, mats['root'])
        rt.location = (rx2, ry2, rz2)
        link(col, rt); objs.append(rt)

    # mineral veins on walls/floor
    vein_cfgs = [
        ("Cave_Vein_A", ( 12, -3, 2.5), (0, math.pi/2, 0.2), 5.0),
        ("Cave_Vein_B", (-12, 2, 3.0),  (0, math.pi/2, -0.3), 4.5),
        ("Cave_Vein_C", (0, 12, 1.8),   (0, 0, 0.4), 6.0),
        ("Cave_Vein_D", (-3, -12, 2.2), (0, 0, -0.5), 5.5),
    ]
    for vname, vloc, vrot, vlen in vein_cfgs:
        vn = build_mineral_vein_strip(vname, vlen, mats['vein'])
        vn.location = vloc; vn.rotation_euler = vrot
        link(col, vn); objs.append(vn)
        add_pt_light(col, vloc, energy=rng.uniform(4,8), color=(0.2,1.0,0.4), radius=0.3)

    # waterfall proxy
    wf = build_waterfall_proxy("Cave_Waterfall", 2.0, 6.0, mats['pool'])
    wf.location = (-13, 0, 6.0)
    link(col, wf); objs.append(wf)
    add_pt_light(col, (-13, 0, 3.0), energy=8.0, color=(0.3,0.5,1.0), radius=0.6)

    # bone piles in dark corners
    bone_cfgs = [
        ("Cave_Bones_A", (10, -8, 0)),
        ("Cave_Bones_B", (-10,-10, 0)),
        ("Cave_Bones_C", (8, 10, 0)),
    ]
    for bname, bloc in bone_cfgs:
        bp = build_bone_pile(bname, 16, mats['bone'])
        bp.location = bloc
        link(col, bp); objs.append(bp)

    # ambient low lights
    add_pt_light(col, (0, 0, 4.0), energy=2.0, color=(0.15, 0.2, 0.35), radius=1.0)

    print(f"[CaveSystems] Built {len(objs)} objects.")
    print("Export: File → Export → FBX, apply modifiers and transforms.")

build_scene()
