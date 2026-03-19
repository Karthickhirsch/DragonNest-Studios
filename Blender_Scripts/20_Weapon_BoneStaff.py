"""
IsleTrial – Cursed Bone Staff  (20_Weapon_BoneStaff.py)
=========================================================
A 1.9 m necromancer polearm: gnarled bone shaft segments,
a full skull topper with glowing amber eye gems, orbiting
soul wisps, crossed bone brace, hanging chain ornaments,
leather-wrapped grip, and carved runic rings.
Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

rng = random.Random(0xBEEF77)

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
# Node helpers
# ─────────────────────────────────────────────────────────────────────
def ns_lk(mat):
    mat.use_nodes = True
    return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, label, x, y):
    n = ns.new('ShaderNodeTexImage')
    n.label = n.name = label
    n.location = (x, y)
    return n

# ─────────────────────────────────────────────────────────────────────
# Materials
# ─────────────────────────────────────────────────────────────────────
def build_bone_mat():
    mat = bpy.data.materials.new("BS_Bone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(900,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(600,0)
    bsdf.inputs['Roughness'].default_value=0.78
    bsdf.inputs['Metallic'].default_value =0.0
    # procedural aged bone colour
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-400,150)
    noise.inputs['Scale'].default_value   =14.0
    noise.inputs['Detail'].default_value  =8.0
    noise.inputs['Roughness'].default_value=0.6
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,150)
    cr.color_ramp.elements[0].position=0.2; cr.color_ramp.elements[0].color=(0.62,0.55,0.38,1)
    cr.color_ramp.elements[1].position=0.8; cr.color_ramp.elements[1].color=(0.88,0.82,0.65,1)
    # stain overlay
    noise2= ns.new('ShaderNodeTexNoise'); noise2.location=(-400,-50)
    noise2.inputs['Scale'].default_value=32.0
    noise2.inputs['Detail'].default_value=4.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location=(-150,-50)
    cr2.color_ramp.elements[0].position=0.6; cr2.color_ramp.elements[0].color=(0.42,0.35,0.18,1)
    cr2.color_ramp.elements[1].position=0.85; cr2.color_ramp.elements[1].color=(0,0,0,0)
    stain_mix= ns.new('ShaderNodeMixRGB'); stain_mix.blend_type='MULTIPLY'; stain_mix.location=(100,100)
    stain_mix.inputs['Fac'].default_value=1.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location=(300,200)
    bmp.inputs['Strength'].default_value=0.5
    img_a= img_slot(ns,"[UNITY] BS_Bone_Albedo",-450,-200)
    img_n= img_slot(ns,"[UNITY] BS_Bone_Normal",-450,-400)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(400,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(noise2.outputs['Fac'],  cr2.inputs['Fac'])
    lk.new(cr.outputs['Color'],    stain_mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   stain_mix.inputs['Color2'])
    lk.new(stain_mix.outputs['Color'], mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_leather_mat():
    mat = bpy.data.materials.new("BS_Leather")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(550,0)
    bsdf.inputs['Roughness'].default_value=0.80
    bsdf.inputs['Metallic'].default_value =0.0
    wave = ns.new('ShaderNodeTexWave'); wave.location=(-400,100)
    wave.wave_type='BANDS'; wave.inputs['Scale'].default_value=22.0
    wave.inputs['Distortion'].default_value=2.5
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.10,0.05,0.02,1)
    cr.color_ramp.elements[1].position=1.0; cr.color_ramp.elements[1].color=(0.25,0.12,0.06,1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location=(300,200)
    bmp.inputs['Strength'].default_value=0.35
    img_a= img_slot(ns,"[UNITY] BS_Leather_Albedo",-450,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(380,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_gem_glow_mat():
    mat = bpy.data.materials.new("BS_GemGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(400,0)
    bsdf.inputs['Base Color'].default_value      =(0.92,0.55,0.05,1)
    bsdf.inputs['Roughness'].default_value       =0.05
    bsdf.inputs['Transmission Weight'].default_value=0.75
    bsdf.inputs['IOR'].default_value             =1.55
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,200)
    emit.inputs['Color'].default_value    =(1.0,0.65,0.1,1)
    emit.inputs['Strength'].default_value =2.5
    add  = ns.new('ShaderNodeAddShader'); add.location=(620,100)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(emit.outputs['Emission'],add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_soul_mat():
    mat = bpy.data.materials.new("BS_Soul")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    mat.blend_method='BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(400,0)
    bsdf.inputs['Base Color'].default_value      =(0.5,1.0,0.6,1)
    bsdf.inputs['Roughness'].default_value       =0.0
    bsdf.inputs['Alpha'].default_value           =0.45
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,200)
    emit.inputs['Color'].default_value    =(0.4,1.0,0.5,1)
    emit.inputs['Strength'].default_value =3.0
    mix  = ns.new('ShaderNodeMixShader'); mix.location=(600,100)
    mix.inputs['Fac'].default_value=0.5
    lk.new(bsdf.outputs['BSDF'],    mix.inputs[1])
    lk.new(emit.outputs['Emission'], mix.inputs[2])
    lk.new(mix.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_dark_iron_mat():
    mat = bpy.data.materials.new("BS_DarkIron")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value=(0.08,0.07,0.06,1)
    bsdf.inputs['Roughness'].default_value =0.55
    bsdf.inputs['Metallic'].default_value  =0.95
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_rune_mat():
    mat = bpy.data.materials.new("BS_Rune")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value=(0.06,0.06,0.10,1)
    bsdf.inputs['Roughness'].default_value =0.38
    bsdf.inputs['Metallic'].default_value  =0.75
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,200)
    emit.inputs['Color'].default_value    =(0.2,0.9,0.3,1)
    emit.inputs['Strength'].default_value =1.0
    mix  = ns.new('ShaderNodeMixShader'); mix.location=(600,100)
    mix.inputs['Fac'].default_value=0.18
    lk.new(bsdf.outputs['BSDF'],    mix.inputs[1])
    lk.new(emit.outputs['Emission'], mix.inputs[2])
    lk.new(mix.outputs['Shader'],   out.inputs['Surface'])
    return mat

# ─────────────────────────────────────────────────────────────────────
# BMesh builders
# ─────────────────────────────────────────────────────────────────────
def bm_bone_shaft(name, length=1.6, base_r=0.032, joints=6):
    """Irregular multi-segment bone shaft with knobby joints."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs_per_joint = 8; sides = 8
    total = joints * segs_per_joint
    for i in range(total + 1):
        t = i / total
        z = t * length
        seg = int(t * joints)
        local_t = (t * joints) - seg
        # joint bulge
        bulge = 1.0 + 0.22 * math.sin(local_t * math.pi) ** 2
        r = base_r * bulge * (0.92 + 0.12 * rng.uniform(-1,1))
        # slight organic bend
        ox = 0.008 * math.sin(t * math.pi * 4.2)
        oy = 0.006 * math.cos(t * math.pi * 3.7 + 0.4)
        for j in range(sides):
            a = j * 2*math.pi/sides
            bm.verts.new((ox+r*math.cos(a), oy+r*math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for i in range(total):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # caps
    bot=bm.verts.new((0,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    tip=bm.verts.new((0,0,length))
    for j in range(sides):
        bm.faces.new([bm.verts[total*sides+j],bm.verts[total*sides+(j+1)%sides],tip])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_skull(name, loc=(0,0,0)):
    """Stylised humanoid skull: braincase + jaw + eye sockets."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    # braincase – deformed sphere
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.090)
    # stretch to skull shape
    for v in bm.verts:
        v.co.z += 0.028 if v.co.z > 0 else -0.015
        v.co.y *= 1.18  # elongate front-back
        if v.co.z < -0.04:
            v.co.z -= 0.015  # jaw notch
    # cheekbones
    for v in bm.verts:
        if abs(v.co.x) > 0.05 and -0.03 < v.co.z < 0.03 and v.co.y < 0.0:
            v.co.x *= 1.15
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    mod = ob.modifiers.new('Sub','SUBSURF'); mod.levels=1; mod.render_levels=2
    return ob

def bm_jaw(name, loc=(0,0,0)):
    """Lower jaw bone."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    # U-shaped jaw strip
    jaw_pts = []
    for j in range(9):
        t = j / 8
        a = math.pi + t * math.pi
        x = 0.058 * math.cos(a)
        y = 0.032 * math.sin(a) + 0.020
        jaw_pts.append((x, y))
    for (x,y) in jaw_pts:
        bm.verts.new((x, y-0.10, -0.105))
        bm.verts.new((x, y-0.10, -0.130))
    bm.verts.ensure_lookup_table()
    n = len(jaw_pts)
    for i in range(n-1):
        a=i*2; b=a+2; c=b+1; d=a+1
        bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_eye_socket_gem(name, loc, r=0.022):
    """Small glowing amber gem for skull eye socket."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=r, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_horn(name, loc, length=0.12, r_base=0.014, rot=(0,0,0)):
    """Pointed bone horn for skull crown."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=8; sides=6
    for i in range(segs+1):
        t=i/segs; r=r_base*(1-t)**0.7
        z=t*length
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
    tip=bm.verts.new((0,0,length))
    for j in range(sides):
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],tip])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_tooth(name, loc, h=0.025, r=0.008, rot=(0,0,0)):
    """Single fang tooth."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=5; sides=5
    for i in range(segs+1):
        t=i/segs; r2=r*(1-t)**0.6; z=t*h
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((r2*math.cos(a),r2*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            if i<segs-1:
                bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    tip=bm.verts.new((0,0,h))
    for j in range(sides):
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],tip])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_cross_bone(name, loc, length=0.28, r=0.018, rot=(0,0,0)):
    """Cylindrical bone rod for cross-brace."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=8; sides=6
    for i in range(segs+1):
        t=i/segs; z=t*length-length/2
        bulge=1.0+0.15*math.sin(t*math.pi)
        r2=r*bulge*(1.0+0.05*math.sin(t*math.pi*5))
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((r2*math.cos(a),r2*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    cap_b=bm.verts.new((0,0,-length/2))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],cap_b])
    cap_t=bm.verts.new((0,0,length/2))
    for j in range(sides):
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],cap_t])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_rune_ring(name, loc, r=0.042, depth=0.015):
    """Carved runic ring around shaft."""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=r, minor_radius=depth,
        major_segments=18, minor_segments=6,
        location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_chain_link(name, loc, mr=0.018, minor=0.004, rot_z=0.0):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=mr, minor_radius=minor,
        major_segments=12, minor_segments=5,
        location=loc, rotation=(math.pi/2, 0, rot_z))
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_bone_ornament(name, loc, size=0.042):
    """Small skull fragment / pendant dangling from chain."""
    bpy.ops.mesh.primitive_ico_sphere_add(radius=size, subdivisions=1, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    # flatten a bit to look like a bone nugget
    ob.scale = (1.0, 0.7, 0.85)
    return ob

def bm_soul_wisp(name, loc, r=0.026):
    """Tiny glowing sphere soul fragment."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=5, radius=r, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_foot_spike(name, loc=(0,0,0), length=0.22):
    """Iron spike at staff base."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides=6; segs=10
    for i in range(segs+1):
        t=i/segs; z=-t*length
        r=0.022*(1-t)**0.55
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

def bm_leather_wrap(name, loc, length=0.38, r=0.038):
    """Helical leather wrap band."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    turns=6; pts=turns*12
    for i in range(pts+1):
        t=i/pts
        angle=t*turns*2*math.pi
        z=loc[2]+t*length
        bm.verts.new((r*math.cos(angle)*1.04,r*math.sin(angle)*1.04,z))
        bm.verts.new((r*math.cos(angle)*1.08,r*math.sin(angle)*1.08,z+length/pts*0.5))
    bm.verts.ensure_lookup_table()
    for i in range(pts):
        a=i*2; b=(i+1)*2; c=(i+1)*2+1; d=i*2+1
        if b+1 < len(bm.verts):
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

# ─────────────────────────────────────────────────────────────────────
# Main creation function
# ─────────────────────────────────────────────────────────────────────
def create_bone_staff():
    clear_scene()
    col = new_col("IsleTrial_BoneStaff")

    mat_bone     = build_bone_mat()
    mat_leather  = build_leather_mat()
    mat_gem_glow = build_gem_glow_mat()
    mat_soul     = build_soul_mat()
    mat_iron     = build_dark_iron_mat()
    mat_rune     = build_rune_mat()

    objs = []

    # ── Root empty ─────────────────────────────────────────────────
    bpy.ops.object.empty_add(type='ARROWS', location=(0,0,0))
    root = bpy.context.active_object
    root.name = "BoneStaff_ROOT"
    link(col, root)

    # ── SHAFT ──────────────────────────────────────────────────────
    shaft = bm_bone_shaft("BS_Shaft", length=1.62, base_r=0.030, joints=7)
    assign_mat(shaft, mat_bone)
    smart_uv(shaft)
    link(col, shaft); objs.append(shaft)

    # ── LEATHER GRIP wrapping ──────────────────────────────────────
    grip = bm_leather_wrap("BS_LeatherGrip", loc=(0,0,0.52), length=0.38, r=0.036)
    assign_mat(grip, mat_leather)
    smart_uv(grip)
    link(col, grip); objs.append(grip)

    # ── RUNE RINGS ─────────────────────────────────────────────────
    rune_ring_zs = [0.28, 0.72, 1.10, 1.45]
    for ri, rz in enumerate(rune_ring_zs):
        rr = bm_rune_ring(f"BS_RuneRing_{ri}", loc=(0,0,rz), r=0.040, depth=0.013)
        assign_mat(rr, mat_rune)
        smart_uv(rr)
        link(col, rr); objs.append(rr)

    # ── CROSS-BONE BRACE near top ──────────────────────────────────
    cb_a = bm_cross_bone("BS_CrossBone_A", loc=(0,0,1.52), length=0.30, r=0.016,
                         rot=(0, math.pi/2, 0.35))
    assign_mat(cb_a, mat_bone)
    smart_uv(cb_a)
    link(col, cb_a); objs.append(cb_a)

    cb_b = bm_cross_bone("BS_CrossBone_B", loc=(0,0,1.52), length=0.28, r=0.014,
                         rot=(0, math.pi/2, -0.35))
    assign_mat(cb_b, mat_bone)
    smart_uv(cb_b)
    link(col, cb_b); objs.append(cb_b)

    # ── SKULL TOPPER ───────────────────────────────────────────────
    skull = bm_skull("BS_Skull", loc=(0, 0, 1.72))
    assign_mat(skull, mat_bone)
    smart_uv(skull)
    link(col, skull); objs.append(skull)

    # ── JAW ────────────────────────────────────────────────────────
    jaw = bm_jaw("BS_Jaw", loc=(0, 0, 1.72))
    assign_mat(jaw, mat_bone)
    smart_uv(jaw)
    link(col, jaw); objs.append(jaw)

    # ── EYE SOCKET GEMS ────────────────────────────────────────────
    eye_locs = [(-0.032, -0.055, 1.755), (0.032, -0.055, 1.755)]
    for ei, eloc in enumerate(eye_locs):
        eg = bm_eye_socket_gem(f"BS_EyeGem_{ei}", loc=eloc, r=0.020)
        assign_mat(eg, mat_gem_glow)
        smart_uv(eg)
        link(col, eg); objs.append(eg)

    # ── SKULL CROWN HORNS ──────────────────────────────────────────
    horn_defs = [
        ("BS_Horn_C",  (0, -0.02, 1.84), 0.14, 0.013, (-0.15, 0, 0)),
        ("BS_Horn_L",  (-0.04, -0.02, 1.82), 0.11, 0.011, (-0.15, 0, -0.4)),
        ("BS_Horn_R",  ( 0.04, -0.02, 1.82), 0.11, 0.011, (-0.15, 0,  0.4)),
        ("BS_Horn_BL", (-0.035, 0.03, 1.80), 0.09, 0.010, ( 0.2, 0, -0.5)),
        ("BS_Horn_BR", ( 0.035, 0.03, 1.80), 0.09, 0.010, ( 0.2, 0,  0.5)),
    ]
    for h_name, h_loc, h_len, h_r, h_rot in horn_defs:
        h = bm_horn(h_name, loc=h_loc, length=h_len, r_base=h_r, rot=h_rot)
        assign_mat(h, mat_bone)
        smart_uv(h)
        link(col, h); objs.append(h)

    # ── SKULL TEETH ────────────────────────────────────────────────
    tooth_data = [
        ((-0.04, -0.085, 1.630), (0,0,0)),
        ((-0.025,-0.088, 1.628), (0,0,0.2)),
        (( 0.025,-0.088, 1.628), (0,0,-0.2)),
        (( 0.04, -0.085, 1.630), (0,0,0)),
        ((-0.04, -0.082, 1.665), (math.pi,0,0)),
        (( 0.04, -0.082, 1.665), (math.pi,0,0)),
    ]
    for ti, (t_loc, t_rot) in enumerate(tooth_data):
        t = bm_tooth(f"BS_Tooth_{ti}", loc=t_loc, h=0.022, r=0.007, rot=t_rot)
        assign_mat(t, mat_bone)
        smart_uv(t)
        link(col, t); objs.append(t)

    # ── SOUL WISPS orbiting skull ───────────────────────────────────
    wisp_data = [
        ("BS_Wisp_A", ( 0.14, 0.00, 1.80), 0.026),
        ("BS_Wisp_B", (-0.10, 0.10, 1.85), 0.022),
        ("BS_Wisp_C", ( 0.06,-0.12, 1.90), 0.020),
        ("BS_Wisp_D", (-0.14,-0.05, 1.78), 0.018),
    ]
    for w_name, w_loc, w_r in wisp_data:
        w = bm_soul_wisp(w_name, loc=w_loc, r=w_r)
        assign_mat(w, mat_soul)
        smart_uv(w)
        link(col, w); objs.append(w)

    # ── HANGING CHAINS with bone pendants ──────────────────────────
    chain_attach = [
        ((-0.040, 0, 1.52), -0.14, -0.16, -0.18, -0.20, -0.24),
        (( 0.040, 0, 1.52), -0.14, -0.16, -0.18, -0.20, -0.24),
    ]
    for side_i, (attach, *z_offsets) in enumerate(chain_attach):
        for li, dz in enumerate(z_offsets):
            cl = bm_chain_link(f"BS_Chain_{side_i}_{li}",
                               loc=(attach[0], attach[1], attach[2]+dz),
                               mr=0.016, minor=0.004,
                               rot_z=(li%2)*math.pi/2)
            assign_mat(cl, mat_iron)
            smart_uv(cl)
            link(col, cl); objs.append(cl)
        # bone ornament at end
        pend_loc = (attach[0], attach[1], attach[2]-0.28)
        pend = bm_bone_ornament(f"BS_Pendant_{side_i}", loc=pend_loc, size=0.030)
        assign_mat(pend, mat_bone)
        smart_uv(pend)
        link(col, pend); objs.append(pend)

    # ── FOOT SPIKE ─────────────────────────────────────────────────
    spike = bm_foot_spike("BS_FootSpike", loc=(0,0,0), length=0.24)
    assign_mat(spike, mat_iron)
    smart_uv(spike)
    link(col, spike); objs.append(spike)

    # ── MODIFIERS ──────────────────────────────────────────────────
    for o in objs:
        if o.type == 'MESH':
            bev = o.modifiers.new('Bevel','BEVEL')
            bev.width    = 0.002
            bev.segments = 2

    # ── PARENT all to root ─────────────────────────────────────────
    for o in objs:
        o.parent = root

    # ── UNITY ATTACHMENT EMPTIES ────────────────────────────────────
    bpy.ops.object.empty_add(type='SINGLE_ARROW', location=(0,0,1.92))
    top_vfx = bpy.context.active_object
    top_vfx.name = "BS_SkullTopVFX"
    top_vfx["unity_note"] = "Soul particle VFX spawn point"
    top_vfx.parent = root; link(col, top_vfx)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0.68))
    grip_pt = bpy.context.active_object
    grip_pt.name = "BS_GripPoint"
    grip_pt["unity_note"] = "Player hand IK grip – Right Hand"
    grip_pt.parent = root; link(col, grip_pt)

    # ── Viewport frame ─────────────────────────────────────────────
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_all(center=True)
                    break

    print("✓ Cursed Bone Staff created – IsleTrial_BoneStaff collection ready for FBX export.")

create_bone_staff()
