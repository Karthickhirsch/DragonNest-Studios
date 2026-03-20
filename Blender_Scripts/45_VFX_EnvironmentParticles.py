"""
45_VFX_EnvironmentParticles.py
IsleTrial — Environment & Atmospheric VFX Meshes
================================================
Mesh proxies for ambient environmental particles, atmospheric
effects, and world-event triggers referenced by game systems.

Objects created (each offset along X for easy separation):
  01 Water Splash Crown      — rising crown of water spikes
  02 Bubble Cluster          — group of spheres (underwater)
  03 Fire Wisp Flame         — teardrop flame mesh
  04 Ember Spark             — small flat diamond sparks
  05 Lava Vent Plume         — cone-shaped gas vent
  06 Steam Puff              — billowing layered cloud planes
  07 Ice Crystal Burst       — radial shard burst
  08 Blizzard Snowflake      — flat hexagonal snowflake mesh
  09 Fog Plane               — large flat animated plane
  10 Dust Devil Spiral       — helical ribbon
  11 Bioluminescent Spore    — glowing sphere cluster
  12 Ocean Spray Ring        — thin water ring
  13 Torch Flame             — lobed flame mesh
  14 Magic Rune Disc         — flat disc with engraved rune lines
  15 Shockwave Ground Crack  — flat star-crack disc

All materials: full procedural node networks + [UNITY] image slots
UV: smart_project on every mesh
Run in Blender >= 3.6
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(450045)

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
def build_water_mat():
    mat = bpy.data.materials.new("Mat_Env_Water")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.02; bsdf.inputs['Transmission Weight'].default_value = 0.8
    bsdf.inputs['IOR'].default_value = 1.33; bsdf.inputs['Base Color'].default_value = (0.1,0.4,0.9,1)
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-500, 200)
    wave.wave_type = 'RINGS'; wave.inputs['Scale'].default_value = 5.0; wave.inputs['Distortion'].default_value = 2.0
    bmp  = ns.new('ShaderNodeBump');           bmp.location = (380, 250)
    bmp.inputs['Strength'].default_value = 0.6
    img_a = img_slot(ns,"[UNITY] Water_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] Water_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] Water_Roughness", -660,-750)
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_fire_mat(tint=(1.0, 0.45, 0.0)):
    mat = bpy.data.materials.new(f"Mat_Env_Fire")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Base Color'].default_value = (*tint[:3], 1); bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Emission Color'].default_value = (*tint[:3], 1); bsdf.inputs['Emission Strength'].default_value = 6.0
    em   = ns.new('ShaderNodeEmission');       em.location = (400,-100)
    em.inputs['Color'].default_value = (*tint[:3], 1); em.inputs['Strength'].default_value = 12.0
    noise= ns.new('ShaderNodeTexNoise');       noise.location = (-500, 0)
    noise.inputs['Scale'].default_value = 6.0; noise.inputs['Detail'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location = (-250, 0)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] Fire_Emission", -660,-350)
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_ice_env_mat():
    mat = bpy.data.materials.new("Mat_Env_Ice")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.02; bsdf.inputs['Transmission Weight'].default_value = 0.88
    bsdf.inputs['IOR'].default_value = 1.55; bsdf.inputs['Base Color'].default_value = (0.5,0.85,1.0,1)
    bsdf.inputs['Emission Color'].default_value = (0.2,0.8,1.0,1); bsdf.inputs['Emission Strength'].default_value = 3.0
    em   = ns.new('ShaderNodeEmission');       em.location = (400,-100)
    em.inputs['Color'].default_value = (0.2,0.85,1.0,1); em.inputs['Strength'].default_value = 7.0
    img_e = img_slot(ns,"[UNITY] EnvIce_Emission", -400,-300)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_biolum_mat():
    mat = bpy.data.materials.new("Mat_Env_Biolum")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.0; bsdf.inputs['Transmission Weight'].default_value = 0.9
    bsdf.inputs['Base Color'].default_value = (0.1,0.9,0.6,1)
    bsdf.inputs['Emission Color'].default_value = (0.1,1.0,0.65,1); bsdf.inputs['Emission Strength'].default_value = 8.0
    em   = ns.new('ShaderNodeEmission');       em.location = (400,-100)
    em.inputs['Color'].default_value = (0.05,1.0,0.6,1); em.inputs['Strength'].default_value = 14.0
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-500, 0)
    wave.wave_type = 'RINGS'; wave.inputs['Scale'].default_value = 2.5; wave.inputs['Distortion'].default_value = 1.5
    cr   = ns.new('ShaderNodeValToRGB');       cr.location = (-250, 0)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.75;cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] Biolum_Emission", -660,-350)
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_cloud_mat():
    mat = bpy.data.materials.new("Mat_Env_Cloud")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Alpha'].default_value = 0.55; bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Base Color'].default_value = (0.88, 0.88, 0.88, 1)
    mat.blend_method = 'BLEND'
    noise= ns.new('ShaderNodeTexNoise');       noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 2.8; noise.inputs['Detail'].default_value = 5.0; noise.inputs['Roughness'].default_value = 0.7
    cr   = ns.new('ShaderNodeValToRGB');       cr.location = (-150, 100)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0.6,0.6,0.6,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (1.0,1.0,1.0,1)
    img_a = img_slot(ns,"[UNITY] Steam_Albedo", -560,-300)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_fog_mat():
    mat = bpy.data.materials.new("Mat_Env_Fog")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Alpha'].default_value = 0.25; bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Base Color'].default_value = (0.72, 0.75, 0.78, 1)
    mat.blend_method = 'BLEND'
    noise= ns.new('ShaderNodeTexNoise');       noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 1.5; noise.inputs['Detail'].default_value = 4.0
    img_a = img_slot(ns,"[UNITY] Fog_Albedo", -560,-300)
    lk.new(noise.outputs['Fac'], bsdf.inputs['Alpha'])
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_magic_mat():
    mat = bpy.data.materials.new("Mat_Env_Magic")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.4; bsdf.inputs['Base Color'].default_value = (0.3,0.1,0.8,1)
    bsdf.inputs['Emission Color'].default_value = (0.5,0.1,1.0,1); bsdf.inputs['Emission Strength'].default_value = 4.0
    em   = ns.new('ShaderNodeEmission');       em.location = (400,-100)
    em.inputs['Color'].default_value = (0.5,0.1,1.0,1); em.inputs['Strength'].default_value = 9.0
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location = (-500, 0)
    vor.voronoi_dimensions = '3D'; vor.inputs['Scale'].default_value = 6.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location = (-250, 0)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] Magic_Emission", -660,-350)
    img_a = img_slot(ns,"[UNITY] Magic_Albedo",   -660,-550)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_ground_crack_mat():
    mat = bpy.data.materials.new("Mat_Env_GroundCrack")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Roughness'].default_value = 0.90
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location = (-500, 200)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value = 5.0; mus.inputs['Detail'].default_value = 8.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location = (-250, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.04,0.03,0.02,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.22,0.16,0.10,1)
    bmp  = ns.new('ShaderNodeBump');           bmp.location = (380, 250)
    bmp.inputs['Strength'].default_value = 2.5; bmp.inputs['Distance'].default_value = 0.04
    img_a = img_slot(ns,"[UNITY] GroundCrack_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] GroundCrack_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] GroundCrack_Roughness", -660,-750)
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

# ── geometry builders ─────────────────────────────────────────────────────────
def build_water_splash_crown(name, mat=None):
    """Rising crown of water spikes with splash base."""
    bm = bmesh.new(); spike_count = 10; base_r = 0.5
    # base ring
    for s in range(28):
        a0 = 2*math.pi*s/28; a1 = 2*math.pi*(s+1)/28
        bm.faces.new([bm.verts.new(p) for p in [
            (base_r*math.cos(a0),base_r*math.sin(a0),0),
            (base_r*math.cos(a1),base_r*math.sin(a1),0),
            ((base_r*0.6)*math.cos(a1),(base_r*0.6)*math.sin(a1),0.05),
            ((base_r*0.6)*math.cos(a0),(base_r*0.6)*math.sin(a0),0.05)]])
    # spikes
    for si in range(spike_count):
        ang = 2*math.pi*si/spike_count + rng.uniform(-0.1,0.1)
        sz = rng.uniform(0.5, 1.0); sr = base_r*(0.85+0.1*math.cos(si*2))
        bx = sr*math.cos(ang); by = sr*math.sin(ang)
        segs = 5; rings = 10
        v_ring = []
        for r in range(rings+1):
            t = r/rings; z = t*sz
            radius = 0.045*(1-t*0.90)
            if radius < 0.003: radius = 0.003
            v_ring.append([bm.verts.new((bx+radius*math.cos(2*math.pi*s/segs),
                                          by+radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)])
        for r in range(rings):
            for s in range(segs):
                bm.faces.new([v_ring[r][s], v_ring[r][(s+1)%segs], v_ring[r+1][(s+1)%segs], v_ring[r+1][s]])
        tip = bm.verts.new((bx+rng.uniform(-0.02,0.02), by+rng.uniform(-0.02,0.02), sz+0.04))
        for s in range(segs): bm.faces.new([v_ring[rings][s], v_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_bubble_cluster(name, count=8, mat=None):
    bm = bmesh.new()
    for _ in range(count):
        cx = rng.uniform(-0.25,0.25); cy = rng.uniform(-0.25,0.25)
        cz = rng.uniform(0, 0.6); cr = rng.uniform(0.04, 0.14)
        segs = 8; vsegs = 6
        for vs in range(vsegs):
            va = vs/vsegs*math.pi; vb = (vs+1)/vsegs*math.pi
            for us in range(segs):
                ua = 2*math.pi*us/segs; ub = 2*math.pi*(us+1)/segs
                pts = [(cx+cr*math.sin(a)*math.cos(b), cy+cr*math.sin(a)*math.sin(b), cz+cr*math.cos(a))
                       for a,b in [(va,ua),(va,ub),(vb,ub),(vb,ua)]]
                bm.faces.new([bm.verts.new(p) for p in pts])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_flame_teardrop(name, height=0.9, mat=None):
    bm = bmesh.new(); segs = 10; rings = 18
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*height
        if t < 0.35: radius = 0.14*math.sin(t/0.35*math.pi*0.5)
        elif t < 0.8: radius = 0.14*(1 - (t-0.35)/0.45*0.6)
        else:         radius = 0.056*(1-(t-0.8)/0.2)
        if radius < 0.004: radius = 0.004
        flicker = 1 + 0.06*math.sin(t*math.pi*6)
        ring = [bm.verts.new((radius*flicker*math.cos(2*math.pi*s/segs),
                               radius*flicker*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    tip = bm.verts.new((rng.uniform(-0.03,0.03), 0, height+0.04))
    for s in range(segs): bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%segs], tip])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ember_spark(name, mat=None):
    bm = bmesh.new()
    for _ in range(15):
        cx = rng.uniform(-0.3,0.3); cy = rng.uniform(-0.3,0.3); cz = rng.uniform(0,0.5)
        r = rng.uniform(0.015, 0.045)
        pts = [(cx-r,cy,cz),(cx,cy-r,cz),(cx+r,cy,cz),(cx,cy+r,cz)]
        bm.faces.new([bm.verts.new(p) for p in pts])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_vent_plume(name, mat=None):
    bm = bmesh.new(); segs = 12; rings = 20; height = 2.0
    verts_ring = []
    for r in range(rings + 1):
        t = r/rings; z = t*height
        radius = 0.12 + t*0.55 + 0.06*math.sin(t*math.pi*4)
        ring = [bm.verts.new((radius*math.cos(2*math.pi*s/segs+t*1.8),
                               radius*math.sin(2*math.pi*s/segs+t*1.8), z)) for s in range(segs)]
        verts_ring.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(segs):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                          verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_steam_puff(name, mat=None):
    bm = bmesh.new()
    # stack of displaced cloud layers
    for li in range(5):
        z = li * 0.28; sz = 0.55 + li*0.15; segs_l = 8
        for iy in range(segs_l):
            for ix in range(segs_l):
                x0=(ix/segs_l-0.5)*sz; x1=((ix+1)/segs_l-0.5)*sz
                y0=(iy/segs_l-0.5)*sz; y1=((iy+1)/segs_l-0.5)*sz
                warp=0.04*math.sin(ix*1.9+iy*1.4+li*2.3)
                bm.faces.new([bm.verts.new(p) for p in [
                    (x0,y0,z+warp),(x1,y0,z+warp),(x1,y1,z+warp),(x0,y1,z+warp)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ice_crystal_burst(name, count=12, mat=None):
    bm = bmesh.new()
    for i in range(count):
        ang_h = 2*math.pi*i/count + rng.uniform(-0.2,0.2)
        ang_v = rng.uniform(-0.5, 0.5)
        cl = rng.uniform(0.25, 0.65); cr = rng.uniform(0.025, 0.055)
        segs = 5; rings = 8
        dx = math.cos(ang_h)*math.cos(ang_v); dy = math.sin(ang_h)*math.cos(ang_v); dz = math.sin(ang_v)
        v_ring = []
        for r in range(rings+1):
            t = r/rings; pos = t*cl
            radius = cr*(1-t*0.88)
            if radius < 0.004: radius = 0.004
            ring = [bm.verts.new((pos*dx + radius*math.cos(2*math.pi*s/segs)*(-dy),
                                   pos*dy + radius*math.sin(2*math.pi*s/segs),
                                   pos*dz + radius*math.cos(2*math.pi*s/segs)*dz*0.2)) for s in range(segs)]
            v_ring.append(ring)
        for r in range(rings):
            for s in range(segs):
                bm.faces.new([v_ring[r][s], v_ring[r][(s+1)%segs], v_ring[r+1][(s+1)%segs], v_ring[r+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_snowflake(name, mat=None):
    """Flat hexagonal snowflake with 6 arms and detail branches."""
    bm = bmesh.new(); arm_len = 0.35; arm_w = 0.025; branch_len = 0.10; branch_w = 0.015
    for ai in range(6):
        ang = 2*math.pi*ai/6
        dx = math.cos(ang); dy = math.sin(ang)
        px = -dy; py = dx  # perpendicular
        # main arm
        for si in range(16):
            t0 = si/16; t1 = (si+1)/16
            p0 = (t0*arm_len*dx, t0*arm_len*dy, 0); p1 = (t1*arm_len*dx, t1*arm_len*dy, 0)
            bm.faces.new([bm.verts.new(q) for q in [
                (p0[0]+arm_w*px, p0[1]+arm_w*py, 0),(p0[0]-arm_w*px, p0[1]-arm_w*py, 0),
                (p1[0]-arm_w*px, p1[1]-arm_w*py, 0),(p1[0]+arm_w*px, p1[1]+arm_w*py, 0)]])
        # side branches (3 per arm)
        for bi in range(3):
            bt = 0.2 + bi*0.25; bx = bt*arm_len*dx; by = bt*arm_len*dy
            for bside in [-1, 1]:
                b_ang = ang + bside * math.pi/3
                bdx = math.cos(b_ang); bdy = math.sin(b_ang)
                bpx = -bdy; bpy = bdx
                for sbi in range(6):
                    t0 = sbi/6; t1 = (sbi+1)/6
                    bp0 = (bx+t0*branch_len*bdx, by+t0*branch_len*bdy, 0)
                    bp1 = (bx+t1*branch_len*bdx, by+t1*branch_len*bdy, 0)
                    bm.faces.new([bm.verts.new(q) for q in [
                        (bp0[0]+branch_w*bpx, bp0[1]+branch_w*bpy, 0),(bp0[0]-branch_w*bpx, bp0[1]-branch_w*bpy, 0),
                        (bp1[0]-branch_w*bpx, bp1[1]-branch_w*bpy, 0),(bp1[0]+branch_w*bpx, bp1[1]+branch_w*bpy, 0)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_fog_plane(name, size=8.0, mat=None):
    bm = bmesh.new(); segs = 14
    for iy in range(segs):
        for ix in range(segs):
            x0=(ix/segs-0.5)*size; x1=((ix+1)/segs-0.5)*size
            y0=(iy/segs-0.5)*size; y1=((iy+1)/segs-0.5)*size
            warp=0.12*math.sin(ix*0.8+iy*1.1)
            bm.faces.new([bm.verts.new(p) for p in [(x0,y0,warp),(x1,y0,warp),(x1,y1,warp),(x0,y1,warp)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_dust_devil_spiral(name, height=2.5, mat=None):
    bm = bmesh.new(); segs_v = 30; width = 0.04
    for i in range(segs_v):
        t0 = i/segs_v; t1 = (i+1)/segs_v
        r = 0.15 + t0*0.35
        a0 = t0*math.pi*6; a1 = t1*math.pi*6
        z0 = t0*height; z1 = t1*height
        p0 = (r*math.cos(a0), r*math.sin(a0), z0)
        p1 = (r*math.cos(a1), r*math.sin(a1), z1)
        # tangent for width direction
        tang = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
        tlen = math.sqrt(tang[0]**2+tang[1]**2+tang[2]**2)+0.0001
        perp = (-tang[1]/tlen, tang[0]/tlen, 0)
        bm.faces.new([bm.verts.new(q) for q in [
            (p0[0]+perp[0]*width, p0[1]+perp[1]*width, p0[2]),
            (p0[0]-perp[0]*width, p0[1]-perp[1]*width, p0[2]),
            (p1[0]-perp[0]*width, p1[1]-perp[1]*width, p1[2]),
            (p1[0]+perp[0]*width, p1[1]+perp[1]*width, p1[2])]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_biolum_spore_cluster(name, count=8, mat=None):
    bm = bmesh.new()
    for _ in range(count):
        cx = rng.uniform(-0.3,0.3); cy = rng.uniform(-0.3,0.3); cz = rng.uniform(0,0.55)
        cr = rng.uniform(0.04, 0.12)
        segs = 8; vsegs = 6
        for vs in range(vsegs):
            va = vs/vsegs*math.pi; vb = (vs+1)/vsegs*math.pi
            for us in range(segs):
                ua = 2*math.pi*us/segs; ub = 2*math.pi*(us+1)/segs
                pts = [(cx+cr*math.sin(a)*math.cos(b), cy+cr*math.sin(a)*math.sin(b), cz+cr*math.cos(a))
                       for a,b in [(va,ua),(va,ub),(vb,ub),(vb,ua)]]
                bm.faces.new([bm.verts.new(p) for p in pts])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ocean_spray_ring(name, mat=None):
    """Thin expanding water ring."""
    bm = bmesh.new(); segs = 32; r = 0.9; thick = 0.04; h = 0.06
    for s in range(segs):
        a0 = 2*math.pi*s/segs; a1 = 2*math.pi*(s+1)/segs
        rvar0 = r*(1+0.04*math.sin(s*5.1)); rvar1 = r*(1+0.04*math.sin((s+1)*5.1))
        bm.faces.new([bm.verts.new(p) for p in [
            ((rvar0-thick)*math.cos(a0),(rvar0-thick)*math.sin(a0),0),
            (rvar0*math.cos(a0),rvar0*math.sin(a0),h),
            (rvar1*math.cos(a1),rvar1*math.sin(a1),h),
            ((rvar1-thick)*math.cos(a1),(rvar1-thick)*math.sin(a1),0)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_torch_flame(name, mat=None):
    """Multi-lobe torch flame."""
    bm = bmesh.new(); lobe_count = 4; height = 0.6
    for li in range(lobe_count):
        ang_off = 2*math.pi*li/lobe_count
        ox = 0.04*math.cos(ang_off); oy = 0.04*math.sin(ang_off)
        segs = 8; rings = 14
        verts_ring = []
        for r in range(rings+1):
            t = r/rings; z = t*height
            if t < 0.3:   radius = 0.06*math.sin(t/0.3*math.pi*0.5)
            elif t < 0.75:radius = 0.06*(1-(t-0.3)/0.45*0.5)
            else:         radius = 0.030*(1-(t-0.75)/0.25)
            if radius < 0.003: radius = 0.003
            ring = [bm.verts.new((ox+radius*math.cos(2*math.pi*s/segs),
                                   oy+radius*math.sin(2*math.pi*s/segs), z)) for s in range(segs)]
            verts_ring.append(ring)
        for r in range(rings):
            for s in range(segs):
                bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%segs],
                              verts_ring[r+1][(s+1)%segs], verts_ring[r+1][s]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_magic_rune_disc(name, mat=None):
    bm = bmesh.new(); segs = 36; rx = 1.0; ry = 1.0
    # outer ring
    ring_verts = [bm.verts.new((rx*math.cos(2*math.pi*s/segs),
                                 ry*math.sin(2*math.pi*s/segs), 0.01)) for s in range(segs)]
    bm.faces.new(ring_verts)
    # rune lines (radial spokes + inner ring)
    for i in range(8):
        ang = 2*math.pi*i/8; w = 0.018
        for ri in range(8):
            t0 = 0.25 + ri/8*0.65; t1 = 0.25 + (ri+1)/8*0.65
            r0 = rx*t0; r1 = rx*t1
            dx = math.cos(ang); dy = math.sin(ang); px = -dy; py = dx
            bm.faces.new([bm.verts.new(q) for q in [
                (r0*dx+w*px, r0*dy+w*py, 0.015),(r0*dx-w*px, r0*dy-w*py, 0.015),
                (r1*dx-w*px, r1*dy-w*py, 0.015),(r1*dx+w*px, r1*dy+w*py, 0.015)]])
    # inner circle
    ic_segs = 20; ic_r = 0.28
    for s in range(ic_segs):
        a0 = 2*math.pi*s/ic_segs; a1 = 2*math.pi*(s+1)/ic_segs; w = 0.02
        bm.faces.new([bm.verts.new(q) for q in [
            ((ic_r-w)*math.cos(a0),(ic_r-w)*math.sin(a0),0.015),
            (ic_r*math.cos(a0),ic_r*math.sin(a0),0.015),
            (ic_r*math.cos(a1),ic_r*math.sin(a1),0.015),
            ((ic_r-w)*math.cos(a1),(ic_r-w)*math.sin(a1),0.015)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

def build_ground_crack_disc(name, mat=None):
    bm = bmesh.new(); crack_count = 8
    for ci in range(crack_count):
        ang = 2*math.pi*ci/crack_count + rng.uniform(-0.2,0.2)
        cl = rng.uniform(0.5, 1.5); w = rng.uniform(0.04, 0.12)
        dx = math.cos(ang); dy = math.sin(ang); px = -dy; py = dx
        for si in range(10):
            t0 = si/10; t1 = (si+1)/10
            var_w = w*(1-t0*0.7)
            p0 = t0*cl; p1 = t1*cl
            branch_x = rng.uniform(-0.04,0.04); branch_y = rng.uniform(-0.04,0.04)
            bm.faces.new([bm.verts.new(q) for q in [
                (p0*dx+var_w*px+branch_x, p0*dy+var_w*py+branch_y, 0.01),
                (p0*dx-var_w*px+branch_x, p0*dy-var_w*py+branch_y, 0.01),
                (p1*dx-var_w*px, p1*dy-var_w*py, 0.01),
                (p1*dx+var_w*px, p1*dy+var_w*py, 0.01)]])
    mesh = bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat); smart_uv(obj); return obj

# ── scene assembly ────────────────────────────────────────────────────────────
def build_scene():
    for o in list(bpy.data.objects):   bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):    bpy.data.meshes.remove(m, do_unlink=True)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m, do_unlink=True)

    col = bpy.data.collections.new("VFX_EnvironmentParticles")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'water':  build_water_mat(),
        'fire':   build_fire_mat((1.0, 0.45, 0.0)),
        'fire2':  build_fire_mat((1.0, 0.75, 0.0)),
        'ice':    build_ice_env_mat(),
        'biolum': build_biolum_mat(),
        'cloud':  build_cloud_mat(),
        'fog':    build_fog_mat(),
        'magic':  build_magic_mat(),
        'crack':  build_ground_crack_mat(),
    }

    x_offset = 0
    def place(obj):
        nonlocal x_offset; obj.location=(x_offset,0,0); link(col,obj); x_offset+=4.0; return obj

    # 01 Water splash crown
    ws = build_water_splash_crown("VFX_WaterSplashCrown", mats['water']); place(ws)
    # 02 Bubble cluster
    bc = build_bubble_cluster("VFX_BubbleCluster", 8, mats['water']); place(bc)
    add_pt_light(col, bc.location, energy=2.0, color=(0.2,0.6,1.0), radius=0.3)
    # 03 Fire wisp flame
    ff = build_flame_teardrop("VFX_FireWisp", 0.9, mats['fire']); place(ff)
    add_pt_light(col, ff.location, energy=6.0, color=(1.0,0.45,0.0), radius=0.3)
    # 04 Ember sparks
    es = build_ember_spark("VFX_EmberSparks", mats['fire']); place(es)
    add_pt_light(col, es.location, energy=3.0, color=(1.0,0.35,0.0), radius=0.2)
    # 05 Lava vent plume
    vp = build_vent_plume("VFX_LavaVentPlume", mats['fire2']); place(vp)
    add_pt_light(col, vp.location, energy=5.0, color=(1.0,0.5,0.0), radius=0.8)
    # 06 Steam puff
    sp = build_steam_puff("VFX_SteamPuff", mats['cloud']); place(sp)
    # 07 Ice crystal burst
    ib = build_ice_crystal_burst("VFX_IceCrystalBurst", 12, mats['ice']); place(ib)
    add_pt_light(col, ib.location, energy=5.0, color=(0.2,0.85,1.0), radius=0.3)
    # 08 Snowflake
    sf = build_snowflake("VFX_Snowflake", mats['ice']); place(sf)
    add_pt_light(col, sf.location, energy=3.0, color=(0.2,0.8,1.0), radius=0.12)
    # 09 Fog plane
    fp = build_fog_plane("VFX_FogPlane", 8.0, mats['fog']); place(fp)
    # 10 Dust devil spiral
    dd = build_dust_devil_spiral("VFX_DustDevilSpiral", 2.5, mats['cloud']); place(dd)
    # 11 Bioluminescent spore cluster
    bs = build_biolum_spore_cluster("VFX_BiolumSpore", 8, mats['biolum']); place(bs)
    add_pt_light(col, bs.location, energy=6.0, color=(0.1,1.0,0.6), radius=0.3)
    # 12 Ocean spray ring
    osr = build_ocean_spray_ring("VFX_OceanSprayRing", mats['water']); place(osr)
    # 13 Torch flame
    tf = build_torch_flame("VFX_TorchFlame", mats['fire']); place(tf)
    add_pt_light(col, tf.location, energy=8.0, color=(1.0,0.55,0.0), radius=0.4)
    # 14 Magic rune disc
    rd = build_magic_rune_disc("VFX_MagicRuneDisc", mats['magic']); place(rd)
    add_pt_light(col, rd.location, energy=5.0, color=(0.5,0.2,1.0), radius=0.5)
    # 15 Shockwave ground crack
    gc = build_ground_crack_disc("VFX_ShockwaveCrack", mats['crack']); place(gc)

    print(f"[VFX_EnvironmentParticles] Built 15 environment VFX meshes.")
    print("Each object is spaced 4.0 units apart on X axis.")
    print("Export individually as FBX for Unity particle/VFX systems.")

build_scene()
