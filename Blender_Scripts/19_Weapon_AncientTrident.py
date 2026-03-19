"""
IsleTrial – Ancient Trident  (19_Weapon_AncientTrident.py)
============================================================
Oceanic relic weapon – a 2.4 m polearm dragged from the deep.
Three serrated prongs, barnacle encrustations, runic engravings,
bioluminescent gem core, oxidised-bronze fittings, and a heavy
chain-ring pommel.  Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

# ── Reproducible randomness ───────────────────────────────────────────
rng = random.Random(0xA23F)

# ─────────────────────────────────────────────────────────────────────
# Scene helpers
# ─────────────────────────────────────────────────────────────────────
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

def new_col(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def link(col, obj):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

# ─────────────────────────────────────────────────────────────────────
# Primitive shortcuts
# ─────────────────────────────────────────────────────────────────────
def add_cylinder(name, verts=12, r=0.05, depth=1.0, loc=(0,0,0), rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth,
                                         location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def add_ico(name, r=0.05, sub=2, loc=(0,0,0)):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=sub, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def add_cone(name, verts=8, r1=0.05, r2=0.0, depth=0.3, loc=(0,0,0), rot=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                     depth=depth, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def add_torus(name, major_r=0.1, minor_r=0.015, loc=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_r, minor_radius=minor_r,
                                      major_segments=20, minor_segments=8, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

# ─────────────────────────────────────────────────────────────────────
# Node-based dual-path material builder
# ─────────────────────────────────────────────────────────────────────
def nodes(mat):
    mat.use_nodes = True
    return mat.node_tree.nodes, mat.node_tree.links

def img_node(tree_nodes, label, x, y):
    n = tree_nodes.new('ShaderNodeTexImage')
    n.label = n.name = label
    n.location = (x, y)
    return n

def build_bronze_mat():
    mat = bpy.data.materials.new("AT_Bronze")
    mat.use_nodes = True
    ns, lk = nodes(mat)
    ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(900,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(600,0)
    bsdf.inputs['Roughness'].default_value = 0.62
    bsdf.inputs['Metallic'].default_value  = 0.88
    bsdf.inputs['Base Color'].default_value = (0.36, 0.22, 0.08, 1)
    # procedural patina
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-400,100)
    noise.inputs['Scale'].default_value   = 18.0
    noise.inputs['Detail'].default_value  = 8.0
    noise.inputs['Roughness'].default_value = 0.65
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].position=0.3; cr.color_ramp.elements[0].color=(0.12,0.38,0.20,1)
    cr.color_ramp.elements[1].position=0.7; cr.color_ramp.elements[1].color=(0.36,0.22,0.08,1)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(200,100)
    mix.inputs['Fac'].default_value=0.45
    img_a= img_node(ns,"[UNITY] AT_Bronze_Albedo",-450,-150)
    img_n= img_node(ns,"[UNITY] AT_Bronze_Normal",-450,-350)
    img_r= img_node(ns,"[UNITY] AT_Bronze_Roughness",-450,-550)
    mix2 = ns.new('ShaderNodeMixRGB'); mix2.location=(400,0)
    mix2.blend_type='MIX'; mix2.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_stone_mat():
    mat = bpy.data.materials.new("AT_Stone")
    mat.use_nodes = True
    ns, lk = nodes(mat)
    ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(550,0)
    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Metallic'].default_value  = 0.0
    mus  = ns.new('ShaderNodeTexMusgrave'); mus.location=(-400,100)
    mus.inputs['Scale'].default_value = 12.0
    mus.inputs['Detail'].default_value= 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.62,0.58,0.52,1)
    cr.color_ramp.elements[1].position=1.0; cr.color_ramp.elements[1].color=(0.88,0.85,0.78,1)
    img_a= img_node(ns,"[UNITY] AT_Stone_Albedo",-450,-150)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(300,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(mus.outputs['Fac'],  cr.inputs['Fac'])
    lk.new(cr.outputs['Color'], mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_barnacle_mat():
    mat = bpy.data.materials.new("AT_Barnacle")
    mat.use_nodes = True
    ns, lk = nodes(mat)
    ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(550,0)
    bsdf.inputs['Roughness'].default_value = 0.92
    bsdf.inputs['Metallic'].default_value  = 0.0
    vor  = ns.new('ShaderNodeTexVoronoi'); vor.location=(-400,100)
    vor.inputs['Scale'].default_value = 22.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.48,0.44,0.38,1)
    cr.color_ramp.elements[1].position=1.0; cr.color_ramp.elements[1].color=(0.72,0.68,0.60,1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location=(300,100)
    bmp.inputs['Strength'].default_value=0.6
    img_a= img_node(ns,"[UNITY] AT_Barnacle_Albedo",-450,-150)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(200,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(vor.outputs['Distance'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(vor.outputs['Distance'],bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_gem_mat():
    mat = bpy.data.materials.new("AT_Gem")
    mat.use_nodes = True
    ns, lk = nodes(mat)
    ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value      = (0.05, 0.38, 0.88, 1)
    bsdf.inputs['Roughness'].default_value       = 0.05
    bsdf.inputs['Metallic'].default_value        = 0.0
    bsdf.inputs['Transmission Weight'].default_value = 0.85
    bsdf.inputs['IOR'].default_value             = 1.62
    emit = ns.new('ShaderNodeEmission'); emit.location=(250,200)
    emit.inputs['Color'].default_value    = (0.1, 0.5, 1.0, 1)
    emit.inputs['Strength'].default_value = 1.8
    add  = ns.new('ShaderNodeAddShader'); add.location=(650,200)
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_rune_mat():
    mat = bpy.data.materials.new("AT_Rune")
    mat.use_nodes = True
    ns, lk = nodes(mat)
    ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value=(0.08,0.08,0.12,1)
    bsdf.inputs['Roughness'].default_value =0.4
    bsdf.inputs['Metallic'].default_value  =0.7
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,200)
    emit.inputs['Color'].default_value    =(0.15,0.55,1.0,1)
    emit.inputs['Strength'].default_value =0.8
    mix  = ns.new('ShaderNodeMixShader'); mix.location=(600,100)
    mix.inputs['Fac'].default_value=0.15
    lk.new(bsdf.outputs['BSDF'],mix.inputs[1])
    lk.new(emit.outputs['Emission'],mix.inputs[2])
    lk.new(mix.outputs['Shader'],out.inputs['Surface'])
    return mat

def build_chain_mat():
    mat = bpy.data.materials.new("AT_Chain")
    mat.use_nodes = True
    ns, lk = nodes(mat)
    ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value=(0.12,0.10,0.08,1)
    bsdf.inputs['Roughness'].default_value =0.55
    bsdf.inputs['Metallic'].default_value  =0.95
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

# ─────────────────────────────────────────────────────────────────────
# BMesh helpers
# ─────────────────────────────────────────────────────────────────────
def bm_prong(name, length=0.72, base_r=0.028, tip_r=0.006,
             barb_count=3, loc=(0,0,0), angle_y=0.0):
    """Single trident prong: tapered shaft with serrated barbs."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 16
    # shaft rings
    for i in range(segs + 1):
        t = i / segs
        r = base_r + (tip_r - base_r) * t
        z = t * length
        for j in range(8):
            a = j * math.pi / 4
            bm.verts.new((r*math.cos(a), r*math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(8):
            a = i*8+j; b = i*8+(j+1)%8
            c = (i+1)*8+(j+1)%8; d = (i+1)*8+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # tip cap
    tip_ring_start = segs*8
    ctr = bm.verts.new((0,0,length+0.04))
    for j in range(8):
        bm.faces.new([bm.verts[tip_ring_start+j], bm.verts[tip_ring_start+(j+1)%8], ctr])
    # base cap
    bot = bm.verts.new((0,0,0))
    for j in range(8):
        bm.faces.new([bm.verts[(j+1)%8], bm.verts[j], bot])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler = (0, angle_y, 0)
    bpy.context.scene.collection.objects.link(ob)
    return ob

def bm_shaft(name, length=2.0):
    """Octagonal tapered staff shaft with spiral grooves."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 40; sides = 8
    for i in range(segs + 1):
        t = i / segs
        z = t * length
        r = 0.034 - 0.010 * t + 0.004 * math.sin(t * math.pi)
        twist = t * math.pi * 1.5  # spiral
        for j in range(sides):
            a = j * 2*math.pi/sides + twist
            bm.verts.new((r*math.cos(a), r*math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a = i*sides+j; b = i*sides+(j+1)%sides
            c = (i+1)*sides+(j+1)%sides; d = (i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # caps
    bot=bm.verts.new((0,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    top=bm.verts.new((0,0,length))
    for j in range(sides):
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],top])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_crossguard(name):
    """Ornate cross-guard with 4 finned lobes."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    # central hub
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.065)
    # 4 curved arms
    arm_dirs = [(1,0),(0,1),(-1,0),(0,-1)]
    for dx,dy in arm_dirs:
        for k in range(5):
            t = (k+1)/5
            r = 0.02*(1-t*0.5)
            x = dx*0.12*t; y = dy*0.12*t; z = 0
            for j in range(6):
                a = j*math.pi/3
                bm.verts.new((x+r*math.cos(a), y+r*math.sin(a), z+r*math.sin(a)*0.3))
    bm.verts.ensure_lookup_table()
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    mod = ob.modifiers.new('Sub','SUBSURF'); mod.levels=1; mod.render_levels=2
    return ob

def bm_barb(name, loc, rot_z=0.0):
    """Reverse barb on prong edge."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    verts = [
        bm.verts.new((0, 0, 0)),
        bm.verts.new((0.018, 0, 0.004)),
        bm.verts.new((0.038, 0, -0.002)),
        bm.verts.new((0.022, 0.006, 0.002)),
        bm.verts.new((0, 0.004, 0.008)),
    ]
    bm.faces.new([verts[0],verts[1],verts[3],verts[4]])
    bm.faces.new([verts[1],verts[2],verts[3]])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler = (0, 0, rot_z)
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_barnacle_cluster(name, loc, count=5):
    """Group of barnacle cone stubs."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    for _ in range(count):
        cx = rng.uniform(-0.03, 0.03)
        cy = rng.uniform(-0.03, 0.03)
        r  = rng.uniform(0.008, 0.018)
        h  = rng.uniform(0.012, 0.028)
        segs = 6
        for j in range(segs):
            a = j*2*math.pi/segs
            bm.verts.new((cx+r*math.cos(a), cy+r*math.sin(a), 0))
        bm.verts.ensure_lookup_table()
        base = len(bm.verts) - segs
        tip  = bm.verts.new((cx, cy, h))
        ring_hole = bm.verts.new((cx, cy, h*0.3))
        for j in range(segs):
            bm.faces.new([bm.verts[base+j], bm.verts[base+(j+1)%segs], ring_hole])
        for j in range(segs):
            bm.faces.new([ring_hole, bm.verts[base+(j+1)%segs], bm.verts[base+j], tip])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_rune_plate(name, loc, rot=(0,0,0), size=0.045):
    """Flat etched rune panel overlay."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    s = size; d = 0.003
    coords = [(-s,-s/2,0),(s,-s/2,0),(s,s/2,0),(-s,s/2,0),
              (-s,-s/2,d),(s,-s/2,d),(s,s/2,d),(-s,s/2,d)]
    vs = [bm.verts.new(c) for c in coords]
    bm.faces.new([vs[0],vs[1],vs[2],vs[3]])
    bm.faces.new([vs[4],vs[7],vs[6],vs[5]])
    sides=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    for q in sides: bm.faces.new([vs[q[0]],vs[q[1]],vs[q[2]],vs[q[3]]])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_chain_link(name, loc, major_r=0.022, minor_r=0.005, rot_z=0.0):
    """Single chain link as a torus-like quad."""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_r, minor_radius=minor_r,
        major_segments=14, minor_segments=6,
        location=loc, rotation=(math.pi/2, 0, rot_z))
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_gem_socket(name, loc, r=0.032):
    """Diamond-cut gem stone."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=r)
    # flatten bottom
    for v in bm.verts:
        if v.co.z < -r*0.3:
            v.co.z = -r*0.3
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_decorative_ring(name, loc, major_r=0.048, minor_r=0.010):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_r, minor_radius=minor_r,
        major_segments=16, minor_segments=6,
        location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_pommel_spike(name, loc, length=0.18):
    """Tapered spike pommel with ring collar."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=10; sides=8
    for i in range(segs+1):
        t=i/segs; z=-t*length
        r=0.030*(1-t)**0.5 if t<1 else 0
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((r*math.cos(a),r*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            if i<segs-1:
                bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    tip=bm.verts.new((0,0,-length))
    for j in range(sides):
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],tip])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

# ─────────────────────────────────────────────────────────────────────
# Main creation function
# ─────────────────────────────────────────────────────────────────────
def create_ancient_trident():
    clear_scene()
    col = new_col("IsleTrial_AncientTrident")

    # ── Materials ──────────────────────────────────────────────────
    mat_bronze   = build_bronze_mat()
    mat_stone    = build_stone_mat()
    mat_barnacle = build_barnacle_mat()
    mat_gem      = build_gem_mat()
    mat_rune     = build_rune_mat()
    mat_chain    = build_chain_mat()

    objs = []

    # ── Root empty ─────────────────────────────────────────────────
    bpy.ops.object.empty_add(type='ARROWS', location=(0,0,0))
    root = bpy.context.active_object
    root.name = "AncientTrident_ROOT"
    link(col, root)

    # ── SHAFT ──────────────────────────────────────────────────────
    shaft = bm_shaft("AT_Shaft", length=1.68)
    assign_mat(shaft, mat_bronze)
    smart_uv(shaft)
    link(col, shaft); objs.append(shaft)

    # ── CROSS-GUARD ────────────────────────────────────────────────
    guard = bm_crossguard("AT_CrossGuard")
    guard.location = (0, 0, 1.68)
    assign_mat(guard, mat_bronze)
    smart_uv(guard)
    link(col, guard); objs.append(guard)

    # ── GEM SOCKET at guard center ─────────────────────────────────
    gem = bm_gem_socket("AT_Gem_Core", loc=(0,0,1.72), r=0.038)
    assign_mat(gem, mat_gem)
    smart_uv(gem)
    link(col, gem); objs.append(gem)

    # ── THREE PRONGS ───────────────────────────────────────────────
    prong_defs = [
        ("AT_Prong_Center",  0.78, (0.00, 0.00, 1.70), 0.0),
        ("AT_Prong_Left",    0.62, (-0.095, 0.00, 1.72), 0.30),
        ("AT_Prong_Right",   0.62, ( 0.095, 0.00, 1.72),-0.30),
    ]
    for p_name, p_len, p_loc, p_ang in prong_defs:
        p = bm_prong(p_name, length=p_len, base_r=0.022, tip_r=0.004,
                     loc=p_loc, angle_y=p_ang)
        assign_mat(p, mat_stone)
        smart_uv(p)
        link(col, p); objs.append(p)

    # ── BARBS on each prong ────────────────────────────────────────
    barb_data = [
        ("AT_Barb_CL", (0.018, 0, 1.92), 0.0),
        ("AT_Barb_CR", (-0.018, 0, 1.92), math.pi),
        ("AT_Barb_LL", (-0.10, 0, 1.98), 0.3),
        ("AT_Barb_LR", (-0.12, 0, 1.88), -0.3),
        ("AT_Barb_RL", ( 0.10, 0, 1.98),-0.3),
        ("AT_Barb_RR", ( 0.12, 0, 1.88), 0.3),
    ]
    for b_name, b_loc, b_rz in barb_data:
        b = bm_barb(b_name, b_loc, rot_z=b_rz)
        assign_mat(b, mat_stone)
        smart_uv(b)
        link(col, b); objs.append(b)

    # ── DECORATIVE BRONZE RINGS along shaft ────────────────────────
    ring_locs = [0.42, 0.84, 1.26, 1.62]
    for ri, z in enumerate(ring_locs):
        r = bm_decorative_ring(f"AT_Ring_{ri}", loc=(0,0,z), major_r=0.046, minor_r=0.009)
        assign_mat(r, mat_bronze)
        smart_uv(r)
        link(col, r); objs.append(r)

    # ── BARNACLE CLUSTERS on shaft ─────────────────────────────────
    barnacle_positions = [
        (0.034, 0, 0.32), (-0.034, 0, 0.55), (0, 0.034, 0.78),
        (-0.034, 0, 1.05), (0.034, 0.020, 1.38),
    ]
    for bi, bpos in enumerate(barnacle_positions):
        bc = bm_barnacle_cluster(f"AT_Barnacle_{bi}", loc=bpos, count=rng.randint(4,7))
        assign_mat(bc, mat_barnacle)
        smart_uv(bc)
        link(col, bc); objs.append(bc)

    # ── BARNACLE CLUSTERS on guard ─────────────────────────────────
    guard_barnacle_pos = [
        (0.06, 0.04, 1.66), (-0.06, -0.04, 1.66),
        (0.04, -0.06, 1.70), (-0.04, 0.06, 1.70),
    ]
    for bi, bpos in enumerate(guard_barnacle_pos):
        bc = bm_barnacle_cluster(f"AT_GBarnacle_{bi}", loc=bpos, count=3)
        assign_mat(bc, mat_barnacle)
        smart_uv(bc)
        link(col, bc); objs.append(bc)

    # ── RUNE PLATES on shaft ───────────────────────────────────────
    rune_data = [
        ((0.036, 0, 0.60), (0, math.pi/2, 0)),
        ((-0.036, 0, 0.90), (0, -math.pi/2, 0)),
        ((0, 0.036, 1.20), (math.pi/2, 0, 0)),
        ((0.036, 0, 1.50), (0, math.pi/2, 0.5)),
        ((-0.036, 0, 0.30), (0, -math.pi/2, 0.3)),
        ((0, -0.036, 1.00), (-math.pi/2, 0, 0.2)),
        ((0.030, 0.018, 0.75), (0.2, math.pi/2, 0)),
        ((-0.018, 0.030, 1.40), (-0.2, -math.pi/2, 0)),
    ]
    for ri, (rloc, rrot) in enumerate(rune_data):
        rp = bm_rune_plate(f"AT_Rune_{ri}", loc=rloc, rot=rrot, size=0.038)
        assign_mat(rp, mat_rune)
        smart_uv(rp)
        link(col, rp); objs.append(rp)

    # ── POMMEL SPIKE at base ───────────────────────────────────────
    pom = bm_pommel_spike("AT_Pommel", loc=(0,0,0), length=0.20)
    assign_mat(pom, mat_bronze)
    smart_uv(pom)
    link(col, pom); objs.append(pom)

    # ── CHAIN LINKS at pommel ──────────────────────────────────────
    chain_z = [-0.22, -0.28, -0.34, -0.40, -0.46]
    for ci, cz in enumerate(chain_z):
        cl = bm_chain_link(f"AT_ChainLink_{ci}",
                           loc=(0, 0, cz),
                           major_r=0.020, minor_r=0.005,
                           rot_z=(ci % 2) * math.pi/2)
        assign_mat(cl, mat_chain)
        smart_uv(cl)
        link(col, cl); objs.append(cl)

    # ── CHAIN RING at pommel top ───────────────────────────────────
    chain_ring = bm_decorative_ring("AT_ChainRing", loc=(0,0,-0.19), major_r=0.032, minor_r=0.007)
    assign_mat(chain_ring, mat_chain)
    smart_uv(chain_ring)
    link(col, chain_ring); objs.append(chain_ring)

    # ── SMALL ACCENT GEMS on guard arms ────────────────────────────
    accent_gem_locs = [(0.08,0,1.68),(-0.08,0,1.68),(0,0.08,1.68),(0,-0.08,1.68)]
    for ai, aloc in enumerate(accent_gem_locs):
        ag = bm_gem_socket(f"AT_AccentGem_{ai}", loc=aloc, r=0.012)
        assign_mat(ag, mat_gem)
        smart_uv(ag)
        link(col, ag); objs.append(ag)

    # ── SEAWEED TEXTURE STRIPS on shaft ────────────────────────────
    for si in range(3):
        angle = si * 2*math.pi/3
        sz = 0.50 + si*0.38
        strip = add_cylinder(f"AT_WeedStrip_{si}", verts=6,
                              r=0.004, depth=0.18,
                              loc=(0.038*math.cos(angle), 0.038*math.sin(angle), sz),
                              rot=(rng.uniform(-0.4,0.4), rng.uniform(-0.4,0.4), angle))
        assign_mat(strip, mat_barnacle)
        smart_uv(strip)
        link(col, strip); objs.append(strip)

    # ── PRONG JUNCTION COLLAR ──────────────────────────────────────
    collar = add_cylinder("AT_ProngCollar", verts=16, r=0.055, depth=0.062, loc=(0,0,1.695))
    assign_mat(collar, mat_bronze)
    smart_uv(collar)
    link(col, collar); objs.append(collar)

    # ── MODIFIERS for all mesh objects ─────────────────────────────
    for o in objs:
        if o.type == 'MESH':
            bev = o.modifiers.new('Bevel','BEVEL')
            bev.width   = 0.003
            bev.segments = 2

    # ── PARENT everything to root ──────────────────────────────────
    for o in objs:
        o.parent = root

    # ── UNITY EXPORT NOTES (empty with custom property) ────────────
    bpy.ops.object.empty_add(type='SINGLE_ARROW', location=(0,0,2.55))
    tip_marker = bpy.context.active_object
    tip_marker.name = "AT_TipPoint"
    tip_marker["unity_note"] = "Weapon tip VFX attachment point"
    tip_marker.parent = root
    link(col, tip_marker)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,-0.48))
    hold_marker = bpy.context.active_object
    hold_marker.name = "AT_GripPoint"
    hold_marker["unity_note"] = "Player hand IK grip attach – Right Hand"
    hold_marker.parent = root
    link(col, hold_marker)

    # ── Final viewport framing ─────────────────────────────────────
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_all(center=True)
                    break

    print("✓ Ancient Trident created – IsleTrial_AncientTrident collection ready for FBX export.")

create_ancient_trident()
