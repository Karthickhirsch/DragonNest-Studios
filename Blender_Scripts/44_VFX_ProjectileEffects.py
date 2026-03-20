"""
44_VFX_ProjectileEffects.py
IsleTrial — Projectile & Combat VFX Meshes
================================================
Mesh proxies for every projectile and combat-related VFX object
referenced by C# scripts. Export each as a separate Unity prefab.

Objects created (each offset along X for easy separation):
  01 Harpoon Projectile     — elongated spike with barb
  02 Harpoon Trail Ring     — ring mesh for harpoon trail VFX
  03 Lava Ball              — cracked sphere with glow cracks
  04 Lava Puddle            — flat disc with molten pattern
  05 Lava Splash Ring       — expanding ring on lava impact
  06 Ice Shard              — faceted crystal spike
  07 Ice Spear (homing)     — longer faceted crystal spear
  08 Ice Wall Slab          — tall flat ice wall
  09 Frost Patch            — hexagonal frost disc on ground
  10 Frost Burst Ring       — expanding ring on frost impact
  11 Lightning Bolt         — zigzag segmented bolt
  12 Explosion Shockwave    — flat torus ring
  13 Energy Orb Projectile  — small glowing sphere
  14 Smoke Puff Plane       — billboarded plane proxy
  15 Blood/Impact Splatter  — flat star-burst disc

All materials: full procedural node networks + [UNITY] image slots
UV: smart_project on every mesh
Run in Blender >= 3.6
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(440044)

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
def add_pt_light(col, loc, energy, color, radius=0.15):
    bpy.ops.object.light_add(type='POINT', location=loc)
    lt = bpy.context.active_object
    lt.data.energy = energy; lt.data.color = color; lt.data.shadow_soft_size = radius
    col.objects.link(lt)
    if lt.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(lt)
    return lt

# ── materials ─────────────────────────────────────────────────────────────────
def build_metal_mat():
    mat = bpy.data.materials.new("Mat_VFX_Metal")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Roughness'].default_value = 0.25; bsdf.inputs['Metallic'].default_value = 0.90
    bsdf.inputs['Base Color'].default_value = (0.55, 0.52, 0.48, 1)
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location = (-400, 100)
    mus.inputs['Scale'].default_value = 8.0; mus.inputs['Detail'].default_value = 5.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location = (320, 200)
    bmp.inputs['Strength'].default_value = 0.5
    img_a = img_slot(ns,"[UNITY] Harpoon_Albedo",    -550,-300)
    img_n = img_slot(ns,"[UNITY] Harpoon_Normal",    -550,-500)
    img_r = img_slot(ns,"[UNITY] Harpoon_Roughness", -550,-700)
    lk.new(mus.outputs['Fac'], bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def build_lava_mat():
    mat = bpy.data.materials.new("Mat_VFX_Lava")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.88; bsdf.inputs['Base Color'].default_value = (0.05,0.02,0.0,1)
    bsdf.inputs['Emission Color'].default_value = (1.0,0.45,0.0,1); bsdf.inputs['Emission Strength'].default_value = 5.0
    em   = ns.new('ShaderNodeEmission');       em.location = (400,-100)
    em.inputs['Color'].default_value = (1.0,0.35,0.0,1); em.inputs['Strength'].default_value = 10.0
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location = (-500, 0)
    vor.voronoi_dimensions = '3D'; vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value = 4.5
    cr   = ns.new('ShaderNodeValToRGB');       cr.location = (-250, 0)
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (1,1,1,1)
    cr.color_ramp.elements[1].position = 0.15;cr.color_ramp.elements[1].color = (0,0,0,1)
    img_e = img_slot(ns,"[UNITY] Lava_Emission", -660,-350)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_ice_mat():
    mat = bpy.data.materials.new("Mat_VFX_Ice")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.03; bsdf.inputs['Transmission Weight'].default_value = 0.85
    bsdf.inputs['IOR'].default_value = 1.55; bsdf.inputs['Base Color'].default_value = (0.5,0.85,1.0,1)
    bsdf.inputs['Emission Color'].default_value = (0.2,0.8,1.0,1); bsdf.inputs['Emission Strength'].default_value = 3.0
    em   = ns.new('ShaderNodeEmission');       em.location = (400,-100)
    em.inputs['Color'].default_value = (0.2,0.85,1.0,1); em.inputs['Strength'].default_value = 7.0
    img_e = img_slot(ns,"[UNITY] Ice_Emission", -400,-300)
    img_a = img_slot(ns,"[UNITY] Ice_Albedo",   -400,-500)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_frost_patch_mat():
    mat = bpy.data.materials.new("Mat_VFX_FrostPatch")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.12; bsdf.inputs['Transmission Weight'].default_value = 0.3
    bsdf.inputs['Base Color'].default_value = (0.65,0.88,1.0,1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location = (-500, 200)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 8.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location = (-250, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.55,0.82,0.98,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.88,0.96,1.00,1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location = (380, 250)
    bmp.inputs['Strength'].default_value = 1.5
    img_a = img_slot(ns,"[UNITY] FrostPatch_Albedo", -660,-350)
    img_n = img_slot(ns,"[UNITY] FrostPatch_Normal", -660,-550)
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

def build_ring_mat(color=(1.0, 0.5, 0.0)):
    mat = bpy.data.materials.new(f"Mat_VFX_Ring_{int(color[0]*9)}")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (600, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (350, 100)
    bsdf.inputs['Alpha'].default_value = 0.6
    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    mat.blend_method = 'BLEND'
    em   = ns.new('ShaderNodeEmission');       em.location = (350,-100)
    em.inputs['Color'].default_value = (*color, 1); em.inputs['Strength'].default_value = 5.0
    img_e = img_slot(ns,f"[UNITY] Ring_Emission", -400,-200)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_lightning_mat():
    mat = bpy.data.materials.new("Mat_VFX_Lightning")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (600, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (350, 100)
    bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 1.0, 1); bsdf.inputs['Roughness'].default_value = 0.8
    em   = ns.new('ShaderNodeEmission');       em.location = (350,-100)
    em.inputs['Color'].default_value = (0.6, 0.8, 1.0, 1); em.inputs['Strength'].default_value = 15.0
    noise= ns.new('ShaderNodeTexNoise');       noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 20.0; noise.inputs['Detail'].default_value = 6.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location = (-150, 0)
    cr.color_ramp.elements[0].position = 0.4; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] Lightning_Emission", -660,-300)
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_energy_mat(color=(0.4, 0.2, 1.0)):
    mat = bpy.data.materials.new(f"Mat_VFX_Energy")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (600, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (350, 100)
    bsdf.inputs['Roughness'].default_value = 0.0; bsdf.inputs['Transmission Weight'].default_value = 0.9
    bsdf.inputs['IOR'].default_value = 1.45; bsdf.inputs['Base Color'].default_value = (*color, 1)
    em   = ns.new('ShaderNodeEmission');       em.location = (350,-100)
    em.inputs['Color'].default_value = (*color, 1); em.inputs['Strength'].default_value = 12.0
    img_e = img_slot(ns,"[UNITY] Energy_Emission", -400,-200)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_smoke_mat():
    mat = bpy.data.materials.new("Mat_VFX_Smoke")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Alpha'].default_value = 0.5; bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Base Color'].default_value = (0.35, 0.32, 0.30, 1)
    mat.blend_method = 'BLEND'
    noise= ns.new('ShaderNodeTexNoise');       noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 3.0; noise.inputs['Detail'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location = (-150, 100)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0.20,0.18,0.16,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (0.50,0.46,0.42,1)
    img_a = img_slot(ns,"[UNITY] Smoke_Albedo", -560,-300)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_impact_mat():
    mat = bpy.data.materials.new("Mat_VFX_Impact")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (600, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (350, 100)
    bsdf.inputs['Base Color'].default_value = (0.80, 0.15, 0.05, 1); bsdf.inputs['Roughness'].default_value = 0.9
    em   = ns.new('ShaderNodeEmission');       em.location = (350,-100)
    em.inputs['Color'].default_value = (1.0, 0.4, 0.05, 1); em.inputs['Strength'].default_value = 4.0
    img_a = img_slot(ns,"[UNITY] Impact_Albedo",   -400,-200)
    img_e = img_slot(ns,"[UNITY] Impact_Emission", -400,-400)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

# ── geometry builders ─────────────────────────────────────────────────────────
def build_harpoon(name, mat=None):
    bm = bmesh.new(); segs = 8; rings = 20; length = 1.2
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*length
        if t < 0.08:  radius = 0.04*math.sin(t/0.08*math.pi*0.5)
        elif t < 0.9: radius = 0.038 + 0.008*math.sin((t-0.08)/0.82*math.pi*4)
        else:         radius = 0.038*(1-(t-0.9)/0.1)
        if radius < 0.003: radius = 0.003
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs),
                               radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0, 0, length+0.05))
    for s in range(segs):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    # barbs
    for bi in range(3):
        ba = 2*math.pi*bi/3; bz = length*0.65; blen = 0.12
        v0 = bm.verts.new((0.038*math.cos(ba), 0.038*math.sin(ba), bz))
        v1 = bm.verts.new((0.13*math.cos(ba), 0.13*math.sin(ba), bz-blen))
        v2 = bm.verts.new((0.038*math.cos(ba), 0.038*math.sin(ba), bz+0.04))
        bm.faces.new([v0, v1, v2])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ring_vfx(name, r_inner=0.3, r_outer=0.45, height=0.08, segs=24, mat=None):
    bm = bmesh.new()
    for s in range(segs):
        a0 = 2*math.pi*s/segs; a1 = 2*math.pi*(s+1)/segs
        pts = [(r_outer*math.cos(a0),r_outer*math.sin(a0),0),
               (r_outer*math.cos(a1),r_outer*math.sin(a1),0),
               (r_outer*math.cos(a1),r_outer*math.sin(a1),height),
               (r_outer*math.cos(a0),r_outer*math.sin(a0),height)]
        bm.faces.new([bm.verts.new(p) for p in pts])
        # top face (annular)
        bm.faces.new([bm.verts.new(p) for p in [
            (r_inner*math.cos(a0),r_inner*math.sin(a0),height),
            (r_inner*math.cos(a1),r_inner*math.sin(a1),height),
            (r_outer*math.cos(a1),r_outer*math.sin(a1),height),
            (r_outer*math.cos(a0),r_outer*math.sin(a0),height)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_lava_ball(name, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=12, radius=0.32)
    for v in bm.verts:
        v.co.x += rng.uniform(-0.04,0.04); v.co.y += rng.uniform(-0.04,0.04); v.co.z += rng.uniform(-0.04,0.04)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_lava_puddle(name, mat=None):
    bm = bmesh.new(); segs = 24; rx = 1.0; ry = 0.85
    for s in range(segs):
        ang = 2*math.pi*s/segs; rvar = 1+0.15*rng.uniform(-1,1)
        bm.verts.new((rx*rvar*math.cos(ang), ry*rvar*math.sin(ang), 0.01))
    bm.verts.ensure_lookup_table(); bm.faces.new(bm.verts)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ice_shard(name, mat=None):
    bm = bmesh.new(); segs = 5; rings = 12; length = 0.50
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*length
        if t < 0.3:  radius = 0.065*math.sin(t/0.3*math.pi*0.5)
        else:        radius = 0.065*(1-(t-0.3)/0.7)
        if radius < 0.005: radius = 0.005
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs+rng.uniform(-0.1,0.1)),
                               radius*math.sin(2*math.pi*s/segs+rng.uniform(-0.1,0.1)), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0,0,length+0.04)); 
    for s in range(segs): bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ice_spear(name, mat=None):
    bm = bmesh.new(); segs = 6; rings = 18; length = 1.2
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*length
        if t < 0.18: radius = 0.09*math.sin(t/0.18*math.pi*0.5)
        elif t < 0.85: radius = 0.09 + 0.02*math.sin((t-0.18)/0.67*math.pi*3)
        else:        radius = 0.09*(1-(t-0.85)/0.15)
        if radius < 0.006: radius = 0.006
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs+rng.uniform(-0.06,0.06)),
                               radius*math.sin(2*math.pi*s/segs+rng.uniform(-0.06,0.06)), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((0,0,length+0.08))
    for s in range(segs): bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_frost_patch(name, mat=None):
    bm = bmesh.new(); segs = 32; rx = 1.2; ry = 1.0
    verts = []
    for s in range(segs):
        ang = 2*math.pi*s/segs; rvar = 1+0.12*math.sin(s*5.3)
        verts.append(bm.verts.new((rx*rvar*math.cos(ang), ry*rvar*math.sin(ang), 0.01)))
    bm.verts.ensure_lookup_table(); bm.faces.new(verts)
    # interior hex pattern
    for ix in range(3):
        for iy in range(3):
            hx = (ix-1)*0.6; hy = (iy-1)*0.55 + (ix%2)*0.28
            if hx*hx + hy*hy > 0.85: continue
            hr = 0.22; hsegs = 6
            hv = [bm.verts.new((hx+hr*math.cos(2*math.pi*hs/hsegs), hy+hr*math.sin(2*math.pi*hs/hsegs), 0.02))
                  for hs in range(hsegs)]
            bm.faces.new(hv)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ice_wall(name, mat=None):
    bm = bmesh.new(); w = 2.2; h = 3.2; thick = 0.30; segs_w = 8; segs_h = 14
    for iw in range(segs_w):
        for ih in range(segs_h):
            x0=(iw/segs_w-0.5)*w; x1=((iw+1)/segs_w-0.5)*w
            z0=ih/segs_h*h; z1=(ih+1)/segs_h*h
            warp=0.05*math.sin(iw*1.3+ih*0.7)
            bm.faces.new([bm.verts.new(p) for p in [(x0,warp,z0),(x1,warp,z0),(x1,warp,z1),(x0,warp,z1)]])
            bm.faces.new([bm.verts.new(p) for p in [(x0,warp+thick,z0),(x0,warp+thick,z1),(x1,warp+thick,z1),(x1,warp+thick,z0)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_lightning_bolt(name, length=3.0, mat=None):
    bm = bmesh.new(); segs = 14; w = 0.025
    zigs = [(rng.uniform(-0.3,0.3), rng.uniform(-0.3,0.3), i/segs*length) for i in range(segs+1)]
    for i in range(segs):
        p0 = zigs[i]; p1 = zigs[i+1]
        v0=bm.verts.new((p0[0]-w,p0[1],p0[2])); v1=bm.verts.new((p0[0]+w,p0[1],p0[2]))
        v2=bm.verts.new((p1[0]+w,p1[1],p1[2])); v3=bm.verts.new((p1[0]-w,p1[1],p1[2]))
        bm.faces.new([v0,v1,v2,v3])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_energy_orb_proj(name, radius=0.22, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=12, radius=radius)
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_smoke_plane(name, size=1.0, mat=None):
    bm = bmesh.new(); segs = 6
    for iy in range(segs):
        for ix in range(segs):
            x0=(ix/segs-0.5)*size; x1=((ix+1)/segs-0.5)*size
            z0=(iy/segs-0.5)*size; z1=((iy+1)/segs-0.5)*size
            warp=0.05*math.sin(ix*1.8+iy*2.1)
            bm.faces.new([bm.verts.new(p) for p in [(x0,warp,z0),(x1,warp,z0),(x1,warp,z1),(x0,warp,z1)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_impact_splatter(name, mat=None):
    bm = bmesh.new(); spike_count = 12; base_r = 0.12
    for i in range(spike_count):
        ang = 2*math.pi*i/spike_count + rng.uniform(-0.15,0.15)
        sl = base_r + rng.uniform(0.05, 0.25)
        sw = 0.04
        v0=bm.verts.new((0,0,0)); v1=bm.verts.new((sl*math.cos(ang)-sw,sl*math.sin(ang)-sw,0))
        v2=bm.verts.new((sl*math.cos(ang)+sw,sl*math.sin(ang)+sw,0))
        bm.faces.new([v0,v1,v2])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

# ── scene assembly ────────────────────────────────────────────────────────────
def build_scene():
    for o in list(bpy.data.objects):   bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):    bpy.data.meshes.remove(m, do_unlink=True)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m, do_unlink=True)

    col = bpy.data.collections.new("VFX_ProjectileEffects")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'metal':   build_metal_mat(),
        'lava':    build_lava_mat(),
        'ice':     build_ice_mat(),
        'frost':   build_frost_patch_mat(),
        'ring_l':  build_ring_mat((1.0, 0.4, 0.0)),
        'ring_i':  build_ring_mat((0.2, 0.8, 1.0)),
        'light':   build_lightning_mat(),
        'energy':  build_energy_mat((0.5, 0.2, 1.0)),
        'smoke':   build_smoke_mat(),
        'impact':  build_impact_mat(),
        'ring_exp':build_ring_mat((1.0, 0.8, 0.2)),
    }

    x_offset = 0
    def place(obj, name_label):
        nonlocal x_offset
        obj.location = (x_offset, 0, 0)
        link(col, obj)
        x_offset += 3.5
        return obj

    # 01 Harpoon
    h = build_harpoon("VFX_Harpoon", mats['metal']); place(h, "Harpoon")
    # 02 Harpoon trail ring
    hr = build_ring_vfx("VFX_HarpoonTrail", 0.10, 0.18, 0.04, 18, mats['ring_exp']); place(hr, "HarpoonTrail")
    # 03 Lava ball
    lb = build_lava_ball("VFX_LavaBall", mats['lava']); place(lb, "LavaBall")
    add_pt_light(col, lb.location, energy=8.0, color=(1.0,0.4,0.0), radius=0.3)
    # 04 Lava puddle
    lp = build_lava_puddle("VFX_LavaPuddle", mats['lava']); place(lp, "LavaPuddle")
    add_pt_light(col, lp.location, energy=5.0, color=(1.0,0.35,0.0), radius=0.8)
    # 05 Lava splash ring
    lsr = build_ring_vfx("VFX_LavaSplashRing", 0.5, 0.8, 0.06, 28, mats['ring_l']); place(lsr, "LavaSplash")
    # 06 Ice shard
    ish = build_ice_shard("VFX_IceShard", mats['ice']); place(ish, "IceShard")
    add_pt_light(col, ish.location, energy=4.0, color=(0.2,0.8,1.0), radius=0.1)
    # 07 Ice spear
    isp = build_ice_spear("VFX_IceSpear", mats['ice']); place(isp, "IceSpear")
    add_pt_light(col, isp.location, energy=5.0, color=(0.2,0.85,1.0), radius=0.12)
    # 08 Ice wall
    iw = build_ice_wall("VFX_IceWall", mats['ice']); place(iw, "IceWall")
    # 09 Frost patch
    fp = build_frost_patch("VFX_FrostPatch", mats['frost']); place(fp, "FrostPatch")
    # 10 Frost burst ring
    fbr = build_ring_vfx("VFX_FrostBurstRing", 0.4, 0.75, 0.05, 28, mats['ring_i']); place(fbr, "FrostBurst")
    # 11 Lightning bolt
    lb2 = build_lightning_bolt("VFX_LightningBolt", 3.0, mats['light']); place(lb2, "Lightning")
    add_pt_light(col, lb2.location, energy=12.0, color=(0.6,0.8,1.0), radius=0.5)
    # 12 Explosion shockwave ring
    esr = build_ring_vfx("VFX_ExplosionRing", 0.8, 1.5, 0.10, 32, mats['ring_exp']); place(esr, "ExplosionRing")
    # 13 Energy orb projectile
    eo = build_energy_orb_proj("VFX_EnergyOrb", 0.18, mats['energy']); place(eo, "EnergyOrb")
    add_pt_light(col, eo.location, energy=8.0, color=(0.5,0.2,1.0), radius=0.15)
    # 14 Smoke puff plane
    sp = build_smoke_plane("VFX_SmokePuff", 0.8, mats['smoke']); place(sp, "SmokePuff")
    # 15 Impact splatter
    imp = build_impact_splatter("VFX_ImpactSplatter", mats['impact']); place(imp, "Impact")

    print(f"[VFX_ProjectileEffects] Built 15 VFX prefab meshes.")
    print("Each object is spaced 3.5 units apart on X axis.")
    print("Export individually as FBX for Unity prefabs.")

build_scene()
