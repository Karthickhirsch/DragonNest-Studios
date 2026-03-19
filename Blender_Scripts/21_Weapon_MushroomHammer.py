"""
IsleTrial – Mycelium War Hammer  (21_Weapon_MushroomHammer.py)
================================================================
A 1.45 m two-handed war hammer with a mushroom-cap head,
radiating gill plates, spore vents with bioluminescent glow,
mycelium tendrils spiralling the handle, bone shard spikes,
a glowing spore sac, iron reinforcement bands, and small
secondary mushrooms sprouting from the grip.
Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

rng = random.Random(0xCA3FE9)

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
def build_wood_mat():
    mat = bpy.data.materials.new("MH_Wood")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(900,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(650,0)
    bsdf.inputs['Roughness'].default_value=0.82
    bsdf.inputs['Metallic'].default_value =0.0
    wave = ns.new('ShaderNodeTexWave'); wave.location=(-400,100)
    wave.wave_type='RINGS'; wave.bands_direction='X'
    wave.inputs['Scale'].default_value=8.0
    wave.inputs['Distortion'].default_value=3.5
    wave.inputs['Detail'].default_value=6.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.22,0.12,0.05,1)
    cr.color_ramp.elements[1].position=1.0; cr.color_ramp.elements[1].color=(0.46,0.28,0.14,1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location=(350,200)
    bmp.inputs['Strength'].default_value=0.4
    img_a= img_slot(ns,"[UNITY] MH_Wood_Albedo",-450,-200)
    img_n= img_slot(ns,"[UNITY] MH_Wood_Normal",-450,-400)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(450,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_mushroom_mat():
    mat = bpy.data.materials.new("MH_Mushroom")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(900,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(650,0)
    bsdf.inputs['Roughness'].default_value=0.72
    bsdf.inputs['Metallic'].default_value =0.0
    bsdf.inputs['Subsurface Weight'].default_value=0.12
    bsdf.inputs['Subsurface Radius'].default_value=(0.6,0.3,0.1)
    # speckled cap pattern
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-500,150)
    noise.inputs['Scale'].default_value   =28.0
    noise.inputs['Detail'].default_value  =10.0
    noise.inputs['Roughness'].default_value=0.55
    vor  = ns.new('ShaderNodeTexVoronoi'); vor.location=(-500,-50)
    vor.inputs['Scale'].default_value=18.0
    cr_n = ns.new('ShaderNodeValToRGB'); cr_n.location=(-250,150)
    cr_n.color_ramp.elements[0].position=0.3; cr_n.color_ramp.elements[0].color=(0.52,0.28,0.10,1)
    cr_n.color_ramp.elements[1].position=0.75; cr_n.color_ramp.elements[1].color=(0.82,0.55,0.25,1)
    cr_v = ns.new('ShaderNodeValToRGB'); cr_v.location=(-250,-50)
    cr_v.color_ramp.elements[0].position=0.55; cr_v.color_ramp.elements[0].color=(1,1,1,0)
    cr_v.color_ramp.elements[1].position=0.80; cr_v.color_ramp.elements[1].color=(0.15,0.08,0.03,1)
    over = ns.new('ShaderNodeMixRGB'); over.blend_type='OVERLAY'; over.location=(-50,100)
    over.inputs['Fac'].default_value=0.55
    img_a= img_slot(ns,"[UNITY] MH_Mushroom_Albedo",-550,-250)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(350,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'], cr_n.inputs['Fac'])
    lk.new(vor.outputs['Distance'],cr_v.inputs['Fac'])
    lk.new(cr_n.outputs['Color'],over.inputs['Color1'])
    lk.new(cr_v.outputs['Color'],over.inputs['Color2'])
    lk.new(over.outputs['Color'],mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix.inputs['Color2'])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_mycelium_mat():
    mat = bpy.data.materials.new("MH_Mycelium")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(550,0)
    bsdf.inputs['Roughness'].default_value=0.88
    bsdf.inputs['Metallic'].default_value =0.0
    bsdf.inputs['Subsurface Weight'].default_value=0.08
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-400,100)
    noise.inputs['Scale'].default_value   =35.0
    noise.inputs['Detail'].default_value  =12.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.82,0.80,0.72,1)
    cr.color_ramp.elements[1].position=1.0; cr.color_ramp.elements[1].color=(0.95,0.94,0.88,1)
    img_a= img_slot(ns,"[UNITY] MH_Mycelium_Albedo",-450,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(300,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'], mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_spore_glow_mat():
    mat = bpy.data.materials.new("MH_SporeGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    mat.blend_method='BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(400,0)
    bsdf.inputs['Base Color'].default_value      =(0.55,1.0,0.25,1)
    bsdf.inputs['Roughness'].default_value       =0.05
    bsdf.inputs['Alpha'].default_value           =0.70
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,200)
    emit.inputs['Color'].default_value    =(0.5,1.0,0.2,1)
    emit.inputs['Strength'].default_value =3.5
    mix  = ns.new('ShaderNodeMixShader'); mix.location=(600,100)
    mix.inputs['Fac'].default_value=0.55
    lk.new(bsdf.outputs['BSDF'],    mix.inputs[1])
    lk.new(emit.outputs['Emission'], mix.inputs[2])
    lk.new(mix.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_metal_mat():
    mat = bpy.data.materials.new("MH_Metal")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value=(0.15,0.12,0.10,1)
    bsdf.inputs['Roughness'].default_value =0.58
    bsdf.inputs['Metallic'].default_value  =0.92
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_bone_mat():
    mat = bpy.data.materials.new("MH_Bone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Roughness'].default_value=0.75
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-300,100)
    noise.inputs['Scale'].default_value=12.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-50,100)
    cr.color_ramp.elements[0].color=(0.60,0.52,0.35,1)
    cr.color_ramp.elements[1].color=(0.85,0.78,0.60,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

# ─────────────────────────────────────────────────────────────────────
# BMesh builders
# ─────────────────────────────────────────────────────────────────────
def bm_handle(name, length=1.05):
    """Gnarled wooden handle with bark texture bumps."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=32; sides=8
    for i in range(segs+1):
        t=i/segs; z=t*length
        r=0.030+0.006*math.sin(t*math.pi*6)*math.sin(t*math.pi)
        r += rng.uniform(-0.003, 0.003)
        twist=t*math.pi*0.8
        for j in range(sides):
            a=j*2*math.pi/sides+twist
            bm.verts.new((r*math.cos(a),r*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
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

def bm_mushroom_cap(name, loc=(0,0,0)):
    """Broad asymmetric mushroom cap head for the hammer."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    rings=16; sides=20
    # dome profile
    for i in range(rings+1):
        t=i/rings
        # cap dome shape: broad base → curved dome
        if t < 0.5:
            r = 0.22 + 0.04*t/0.5
        else:
            r = 0.26*(1-(t-0.5)/0.5)**0.4
        z = 0.26*math.sin(t*math.pi*0.85) - 0.02
        # slight asymmetry (weapon impact side)
        z_off = -0.015 * math.sin(t*math.pi) if t > 0.3 else 0
        for j in range(sides):
            a=j*2*math.pi/sides
            # flatten impact face
            rx=r*(1.0+0.15*abs(math.cos(a)))
            ry=r
            bm.verts.new((rx*math.cos(a), ry*math.sin(a), z+z_off))
    bm.verts.ensure_lookup_table()
    for i in range(rings):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # bottom cap
    bot=bm.verts.new((0,0,-0.02))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    # dome top
    top=bm.verts.new((0,0,0.24))
    for j in range(sides):
        bm.faces.new([bm.verts[rings*sides+j],bm.verts[rings*sides+(j+1)%sides],top])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    mod = ob.modifiers.new('Sub','SUBSURF'); mod.levels=1; mod.render_levels=2
    return ob

def bm_gill_plate(name, loc, length=0.20, height=0.04, rot_z=0.0):
    """Single gill plate radiating under mushroom cap."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=8
    for i in range(segs+1):
        t=i/segs
        x=t*length
        # curved gill profile
        z=height*(1-t)**0.5*math.sin(t*math.pi)
        bm.verts.new((x, 0.003, z))
        bm.verts.new((x,-0.003, z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        a=i*2; b=a+2; c=b+1; d=a+1
        if b+1 < len(bm.verts):
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler = (0, 0, rot_z)
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_spore_vent(name, loc, r=0.022):
    """Circular vent hole with a glowing inner sac."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=r, depth=0.012,
                                         location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_spore_sac(name, loc, r=0.06):
    """Bulging glowing spore sac on back of cap."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8,
                                          radius=r, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    ob.scale = (1.0, 0.75, 0.65)
    return ob

def bm_mycelium_tendril(name, start, end, r=0.009):
    """Spiralling mycelium tendril from handle to head."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=20; sides=5
    sx,sy,sz = start; ex,ey,ez = end
    for i in range(segs+1):
        t=i/segs
        x=sx+(ex-sx)*t + 0.025*math.cos(t*math.pi*5+rng.uniform(0,1))
        y=sy+(ey-sy)*t + 0.025*math.sin(t*math.pi*5+rng.uniform(0,1))
        z=sz+(ez-sz)*t
        rv=r*(0.7+0.3*math.sin(t*math.pi))
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((x+rv*math.cos(a),y+rv*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_bone_shard(name, loc, length=0.10, rot=(0,0,0)):
    """Bone fragment jutting from cap surface."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=6; sides=4
    for i in range(segs+1):
        t=i/segs; z=t*length
        r=0.010*(1-t)**0.6
        for j in range(sides):
            a=j*2*math.pi/sides+t*0.5
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

def bm_iron_band(name, loc, r=0.038, depth=0.025):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=r, minor_radius=depth*0.45,
        major_segments=16, minor_segments=5, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_mini_mushroom(name, loc, scale=1.0):
    """Small secondary mushroom growing on handle."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    # stem
    segs=5; sides=6; stem_h=0.06*scale
    for i in range(segs+1):
        t=i/segs; z=t*stem_h
        r=0.012*scale*(1-0.3*t)
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((r*math.cos(a),r*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # cap
    cap_r=0.040*scale; cap_h=0.035*scale; cap_z=stem_h
    cap_segs=8
    for i in range(cap_segs+1):
        t=i/cap_segs
        r=cap_r*math.sin(t*math.pi*0.85)
        z=cap_z+cap_h*(1-math.cos(t*math.pi*0.85))*0.5
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((r*math.cos(a),r*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    n_stem = (segs+1)*sides
    for i in range(cap_segs):
        for j in range(sides):
            a=(n_stem+i*sides+j); b=(n_stem+i*sides+(j+1)%sides)
            c=(n_stem+(i+1)*sides+(j+1)%sides); d=(n_stem+(i+1)*sides+j)
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_impact_plate(name, loc=(0,0,0)):
    """Flat metal impact face on the hammer head."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    r=0.18; d=0.018; sides=20
    for j in range(sides):
        a=j*2*math.pi/sides
        bm.verts.new((r*math.cos(a),r*math.sin(a),-d))
        bm.verts.new((r*math.cos(a),r*math.sin(a), d))
    bm.verts.ensure_lookup_table()
    for j in range(sides):
        a=j*2; b=j*2+2 if j<sides-1 else 0; c=b+1; dd=a+1
        bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[dd]])
    bot=bm.verts.new((0,0,-d)); top=bm.verts.new((0,0,d))
    for j in range(sides):
        a=j*2; b=(j*2+2)%(sides*2)
        bm.faces.new([bm.verts[b],bm.verts[a],bot])
        bm.faces.new([bm.verts[a+1],bm.verts[b+1],top])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler=(math.pi/2,0,0)
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

# ─────────────────────────────────────────────────────────────────────
# Main creation function
# ─────────────────────────────────────────────────────────────────────
def create_mushroom_hammer():
    clear_scene()
    col = new_col("IsleTrial_MushroomHammer")

    mat_wood     = build_wood_mat()
    mat_mushroom = build_mushroom_mat()
    mat_mycelium = build_mycelium_mat()
    mat_glow     = build_spore_glow_mat()
    mat_metal    = build_metal_mat()
    mat_bone     = build_bone_mat()

    objs = []

    # ── Root ───────────────────────────────────────────────────────
    bpy.ops.object.empty_add(type='ARROWS', location=(0,0,0))
    root = bpy.context.active_object
    root.name = "MushroomHammer_ROOT"
    link(col, root)

    # ── HANDLE ─────────────────────────────────────────────────────
    handle = bm_handle("MH_Handle", length=1.05)
    assign_mat(handle, mat_wood)
    smart_uv(handle)
    link(col, handle); objs.append(handle)

    # ── IRON BANDS on handle ────────────────────────────────────────
    band_zs = [0.12, 0.55, 0.95]
    for bi, bz in enumerate(band_zs):
        band = bm_iron_band(f"MH_Band_{bi}", loc=(0,0,bz), r=0.036, depth=0.022)
        assign_mat(band, mat_metal)
        smart_uv(band)
        link(col, band); objs.append(band)

    # ── MYCELIUM TENDRILS spiralling handle ─────────────────────────
    tendril_angles = [0.0, 1.26, 2.51, 3.77, 5.03]
    for ti, ta in enumerate(tendril_angles):
        sx = 0.035*math.cos(ta); sy = 0.035*math.sin(ta)
        ex = 0.10*math.cos(ta+1.0); ey = 0.10*math.sin(ta+1.0)
        tend = bm_mycelium_tendril(
            f"MH_Tendril_{ti}",
            start=(sx, sy, 0.10+ti*0.18),
            end=(ex, ey, 0.90+ti*0.02),
            r=0.007+rng.uniform(-0.002,0.002))
        assign_mat(tend, mat_mycelium)
        smart_uv(tend)
        link(col, tend); objs.append(tend)

    # ── MUSHROOM CAP HEAD ──────────────────────────────────────────
    cap = bm_mushroom_cap("MH_Cap", loc=(0, 0, 1.10))
    assign_mat(cap, mat_mushroom)
    smart_uv(cap)
    link(col, cap); objs.append(cap)

    # ── IMPACT FACE plates ─────────────────────────────────────────
    impact_a = bm_impact_plate("MH_ImpactFace_A", loc=(0, 0.24, 1.10))
    assign_mat(impact_a, mat_metal)
    smart_uv(impact_a)
    link(col, impact_a); objs.append(impact_a)

    # ── GILL PLATES under cap ──────────────────────────────────────
    gill_count = 16
    for gi in range(gill_count):
        angle = gi * 2*math.pi/gill_count
        gl = 0.18*(0.7+0.3*rng.random())
        gill = bm_gill_plate(
            f"MH_Gill_{gi}",
            loc=(0.012*math.cos(angle), 0.012*math.sin(angle), 1.065),
            length=gl, height=0.045,
            rot_z=angle)
        assign_mat(gill, mat_mushroom)
        smart_uv(gill)
        link(col, gill); objs.append(gill)

    # ── SPORE VENTS on cap top ─────────────────────────────────────
    vent_data = [
        (0.10, 0.05, 1.32), (-0.10, 0.06, 1.30),
        (0.06,-0.10, 1.28), (-0.06,-0.10, 1.28),
    ]
    for vi, (vx,vy,vz) in enumerate(vent_data):
        vent = bm_spore_vent(f"MH_Vent_{vi}", loc=(vx,vy,vz), r=0.020)
        assign_mat(vent, mat_metal)
        smart_uv(vent)
        link(col, vent); objs.append(vent)
        # glow inside vent
        inner = bm_spore_vent(f"MH_VentGlow_{vi}", loc=(vx,vy,vz+0.004), r=0.014)
        assign_mat(inner, mat_glow)
        smart_uv(inner)
        link(col, inner); objs.append(inner)

    # ── SPORE SAC on back of cap ───────────────────────────────────
    sac = bm_spore_sac("MH_SporeSac", loc=(0, -0.22, 1.18), r=0.065)
    assign_mat(sac, mat_glow)
    smart_uv(sac)
    link(col, sac); objs.append(sac)

    # ── BONE SHARDS on cap surface ─────────────────────────────────
    bone_positions = [
        (0.18, 0.05, 1.22, (0.3,-0.5,0.2)),
        (-0.18,-0.05, 1.22, (-0.3,0.5,-0.2)),
        (0.12, 0.18, 1.30, (0.5,0.2,0.8)),
        (-0.12,-0.18, 1.28, (-0.5,-0.2,-0.8)),
        (0.20, -0.12, 1.18, (0.2,-0.3,0.5)),
        (-0.15, 0.16, 1.20, (-0.2,0.3,-0.4)),
    ]
    for bi, (bx,by,bz,brot) in enumerate(bone_positions):
        bs = bm_bone_shard(f"MH_Bone_{bi}",
                           loc=(bx,by,bz), length=0.10,
                           rot=brot)
        assign_mat(bs, mat_bone)
        smart_uv(bs)
        link(col, bs); objs.append(bs)

    # ── MINI MUSHROOMS on handle ────────────────────────────────────
    mini_data = [
        ((0.034, 0.010, 0.30), 0.75),
        ((-0.030, 0.020, 0.48), 0.55),
        ((0.020,-0.032, 0.72), 0.65),
    ]
    for mi, (mloc, msc) in enumerate(mini_data):
        mm = bm_mini_mushroom(f"MH_MiniMush_{mi}", loc=mloc, scale=msc)
        assign_mat(mm, mat_mushroom)
        smart_uv(mm)
        link(col, mm); objs.append(mm)

    # ── HEAD-HANDLE SOCKET (neck junction) ─────────────────────────
    neck = bm_iron_band("MH_HeadSocket", loc=(0,0,1.06), r=0.050, depth=0.038)
    assign_mat(neck, mat_metal)
    smart_uv(neck)
    link(col, neck); objs.append(neck)

    # ── MODIFIERS ──────────────────────────────────────────────────
    for o in objs:
        if o.type == 'MESH':
            bev = o.modifiers.new('Bevel','BEVEL')
            bev.width    = 0.002
            bev.segments = 2

    # ── PARENT ─────────────────────────────────────────────────────
    for o in objs:
        o.parent = root

    # ── UNITY EMPTIES ──────────────────────────────────────────────
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0.55))
    grip_pt = bpy.context.active_object
    grip_pt.name = "MH_GripPoint"
    grip_pt["unity_note"] = "Two-hand grip centre – map to PlayerHandL & PlayerHandR"
    grip_pt.parent = root; link(col, grip_pt)

    bpy.ops.object.empty_add(type='SINGLE_ARROW', location=(0, 0.30, 1.12))
    impact_pt = bpy.context.active_object
    impact_pt.name = "MH_ImpactPoint"
    impact_pt["unity_note"] = "Hitbox origin – weapon damage collider"
    impact_pt.parent = root; link(col, impact_pt)

    bpy.ops.object.empty_add(type='SPHERE', location=(0,-0.22,1.18))
    vfx_pt = bpy.context.active_object
    vfx_pt.name = "MH_SporeVFX"
    vfx_pt["unity_note"] = "Spore particle VFX emitter"
    vfx_pt.parent = root; link(col, vfx_pt)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_all(center=True)
                    break

    print("✓ Mycelium War Hammer created – IsleTrial_MushroomHammer collection ready for FBX export.")

create_mushroom_hammer()
