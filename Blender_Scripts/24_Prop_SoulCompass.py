"""
IsleTrial – Soul Compass (Revival Prop)  (24_Prop_SoulCompass.py)
==================================================================
A rare pickup prop: a ~15 cm ornate brass compass whose needle
points to fallen teammates rather than north.  Using it releases
a captured soul to revive one ally.

Components:
  • Octagonal brass compass body with thick rune-engraved rim
  • Magnifying glass top (open lid, shown ajar)
  • Ornate hinged lid (open, visible back carved scene)
  • Painted 16-point compass rose base plate
  • Glowing ethereal needle (teal/white gradient)
  • 3 soul-wisp fragments orbiting above on ethereal chains
  • Rune panel overlays on 8 rim faces
  • Warm brass chain fob (5 links)
  • Heart-cartouche carved into lid interior
  • Soft emission halo ring under compass body
  • 4 floating spark ornaments
  • _SoulRevive_TriggerPoint  empty for Unity pickup collider
  • _ReviveLightPoint  empty for Unity point-light glow

Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

rng = random.Random(0xF1A9E2)

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

def ns_lk(mat):
    mat.use_nodes = True
    return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, label, x, y):
    n = ns.new('ShaderNodeTexImage')
    n.label = n.name = label; n.location = (x, y)
    return n

# ─────────────────────────────────────────────────────────────────────
# Materials
# ─────────────────────────────────────────────────────────────────────
def build_brass_mat():
    mat = bpy.data.materials.new("SC_Brass")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(900,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(650,0)
    bsdf.inputs['Roughness'].default_value=0.35
    bsdf.inputs['Metallic'].default_value =0.92
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-450,150)
    noise.inputs['Scale'].default_value   =22.0
    noise.inputs['Detail'].default_value  =8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-200,150)
    cr.color_ramp.elements[0].position=0.1; cr.color_ramp.elements[0].color=(0.45,0.28,0.05,1)
    cr.color_ramp.elements[1].position=0.9; cr.color_ramp.elements[1].color=(0.90,0.68,0.20,1)
    # patina green pits
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location=(-200,-50)
    cr2.color_ramp.elements[0].position=0.7; cr2.color_ramp.elements[0].color=(0.20,0.42,0.25,0)
    cr2.color_ramp.elements[1].position=0.85; cr2.color_ramp.elements[1].color=(0.18,0.40,0.22,1)
    noise2=ns.new('ShaderNodeTexNoise'); noise2.location=(-450,-50)
    noise2.inputs['Scale'].default_value=38.0
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type='MIX'; mix.location=(100,100)
    mix.inputs['Fac'].default_value=0.25
    img_a= img_slot(ns,"[UNITY] SC_Brass_Albedo",-500,-250)
    img_n= img_slot(ns,"[UNITY] SC_Brass_Normal",-500,-450)
    mix2 = ns.new('ShaderNodeMixRGB'); mix2.location=(400,0)
    mix2.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(noise2.outputs['Fac'],  cr2.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_soul_mat():
    mat = bpy.data.materials.new("SC_Soul")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    mat.blend_method='BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value      =(0.55,0.95,1.0,1)
    bsdf.inputs['Roughness'].default_value       =0.0
    bsdf.inputs['Transmission Weight'].default_value=0.60
    bsdf.inputs['Alpha'].default_value           =0.55
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,250)
    emit.inputs['Color'].default_value    =(0.4,1.0,0.95,1)
    emit.inputs['Strength'].default_value =4.0
    mix  = ns.new('ShaderNodeMixShader'); mix.location=(650,150)
    mix.inputs['Fac'].default_value=0.55
    lk.new(bsdf.outputs['BSDF'],    mix.inputs[1])
    lk.new(emit.outputs['Emission'], mix.inputs[2])
    lk.new(mix.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_glass_mat():
    mat = bpy.data.materials.new("SC_Glass")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    mat.blend_method='BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value      =(0.88,0.95,1.0,1)
    bsdf.inputs['Roughness'].default_value       =0.02
    bsdf.inputs['Transmission Weight'].default_value=0.92
    bsdf.inputs['Alpha'].default_value           =0.28
    bsdf.inputs['IOR'].default_value             =1.52
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_rose_mat():
    mat = bpy.data.materials.new("SC_Rose")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Roughness'].default_value=0.65
    bsdf.inputs['Metallic'].default_value =0.0
    # concentric ring compass pattern
    tex  = ns.new('ShaderNodeTexCoord'); tex.location=(-600,100)
    sep  = ns.new('ShaderNodeSeparateXYZ'); sep.location=(-450,100)
    dist = ns.new('ShaderNodeMath'); dist.operation='SQRT'; dist.location=(-300,50)
    mul_x= ns.new('ShaderNodeMath'); mul_x.operation='MULTIPLY'; mul_x.location=(-400,150)
    mul_y= ns.new('ShaderNodeMath'); mul_y.operation='MULTIPLY'; mul_y.location=(-400,-50)
    add_sq=ns.new('ShaderNodeMath'); add_sq.operation='ADD'; add_sq.location=(-340,50)
    wave  = ns.new('ShaderNodeTexWave'); wave.location=(-150,100)
    wave.wave_type='RINGS'; wave.inputs['Scale'].default_value=8.0
    wave.inputs['Distortion'].default_value=0.3
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(50,100)
    cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.72,0.58,0.20,1)
    cr.color_ramp.elements[1].position=0.5; cr.color_ramp.elements[1].color=(0.12,0.10,0.08,1)
    img_a= img_slot(ns,"[UNITY] SC_Rose_Albedo",-500,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(350,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(wave.outputs['Color'],  cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_rune_mat():
    mat = bpy.data.materials.new("SC_Rune")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value=(0.06,0.06,0.10,1)
    bsdf.inputs['Roughness'].default_value =0.35
    bsdf.inputs['Metallic'].default_value  =0.78
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,200)
    emit.inputs['Color'].default_value    =(0.4,0.9,1.0,1)
    emit.inputs['Strength'].default_value =1.5
    mix  = ns.new('ShaderNodeMixShader'); mix.location=(620,100)
    mix.inputs['Fac'].default_value=0.25
    lk.new(bsdf.outputs['BSDF'],    mix.inputs[1])
    lk.new(emit.outputs['Emission'], mix.inputs[2])
    lk.new(mix.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_chain_mat():
    mat = bpy.data.materials.new("SC_Chain")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value=(0.55,0.38,0.08,1)
    bsdf.inputs['Roughness'].default_value =0.42
    bsdf.inputs['Metallic'].default_value  =0.95
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_halo_mat():
    mat = bpy.data.materials.new("SC_Halo")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    mat.blend_method='BLEND'
    emit = ns.new('ShaderNodeEmission'); emit.location=(300,0)
    emit.inputs['Color'].default_value    =(0.4,1.0,0.9,1)
    emit.inputs['Strength'].default_value =3.5
    lk.new(emit.outputs['Emission'],out.inputs['Surface'])
    return mat

def build_needle_mat():
    mat = bpy.data.materials.new("SC_Needle")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value      =(0.2,0.95,0.85,1)
    bsdf.inputs['Roughness'].default_value       =0.0
    bsdf.inputs['Metallic'].default_value        =0.1
    emit = ns.new('ShaderNodeEmission'); emit.location=(150,200)
    emit.inputs['Color'].default_value    =(0.3,1.0,0.9,1)
    emit.inputs['Strength'].default_value =5.0
    add  = ns.new('ShaderNodeAddShader'); add.location=(550,100)
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(emit.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_spark_mat():
    mat = bpy.data.materials.new("SC_Spark")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    mat.blend_method='BLEND'
    emit = ns.new('ShaderNodeEmission'); emit.location=(300,0)
    emit.inputs['Color'].default_value    =(1.0,0.95,0.5,1)
    emit.inputs['Strength'].default_value =6.0
    lk.new(emit.outputs['Emission'],out.inputs['Surface'])
    return mat

# ─────────────────────────────────────────────────────────────────────
# BMesh builders
# ─────────────────────────────────────────────────────────────────────
def bm_compass_body(name, r=0.072, height=0.032):
    """Thick octagonal compass body with chamfered top & bottom rim."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides=8
    # outer chamfered ring (3 z-levels: bottom bevel, main, top bevel)
    z_levels=[(0, r),(0.008, r),(height-0.008, r),(height, r)]
    rim_r=r*0.88  # inner rim step
    for zv, rv in z_levels:
        for j in range(sides):
            a=j*2*math.pi/sides + math.pi/sides
            bm.verts.new((rv*math.cos(a),rv*math.sin(a),zv))
    # inner rim wall
    inner_z=[(0.008,rim_r),(height-0.008,rim_r)]
    for zv, rv in inner_z:
        for j in range(sides):
            a=j*2*math.pi/sides + math.pi/sides
            bm.verts.new((rv*math.cos(a),rv*math.sin(a),zv))
    bm.verts.ensure_lookup_table()
    n_outer_levels=len(z_levels)
    # outer side faces
    for li in range(n_outer_levels-1):
        for j in range(sides):
            a=li*sides+j; b=li*sides+(j+1)%sides
            c=(li+1)*sides+(j+1)%sides; d=(li+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # bottom cap
    bot=bm.verts.new((0,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    mod = ob.modifiers.new('Bevel','BEVEL'); mod.width=0.004; mod.segments=2
    return ob

def bm_compass_face(name, r=0.068, z=0.032):
    """Flat inner face disc (compass rose base)."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides=32
    for j in range(sides):
        a=j*2*math.pi/sides
        bm.verts.new((r*math.cos(a),r*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    ctr=bm.verts.new((0,0,z))
    for j in range(sides):
        bm.faces.new([bm.verts[j],bm.verts[(j+1)%sides],ctr])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_compass_rose_points(name, z=0.034, r=0.060):
    """16-point compass rose raised points on face disc."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    pts=16
    for pi in range(pts):
        angle=pi*2*math.pi/pts
        major=(pi%2==0)
        arm_len=r*(0.82 if major else 0.60)
        arm_w=0.010 if major else 0.006
        perp=angle+math.pi/2
        tip_r=arm_len*0.92
        for sign in (-1,1):
            bx=arm_w*sign*math.cos(perp)
            by=arm_w*sign*math.sin(perp)
            bm.verts.new((bx,by,z))
        bm.verts.new((arm_len*math.cos(angle),arm_len*math.sin(angle),z+0.004))
    bm.verts.ensure_lookup_table()
    for pi in range(pts):
        a=pi*3; tip=a+2; left=a; right=a+1
        if tip < len(bm.verts):
            bm.faces.new([bm.verts[left],bm.verts[tip],bm.verts[right]])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_needle(name, z=0.034):
    """Ethereal compass needle – elongated diamond cross-section."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    # N half – long arm
    vs=[bm.verts.new(v) for v in [
        (0, 0.058, z+0.006),(0, 0.058, z-0.006),   # tip face
        (0.004, 0, z),(0, 0, z+0.006),(0,0,z-0.006),  # centre
        (-0.004, 0, z),
        (0,-0.028, z+0.004),(0,-0.028, z-0.004)        # S tail
    ]]
    bm.faces.new([vs[0],vs[3],vs[2],vs[1]])
    bm.faces.new([vs[0],vs[5],vs[3]])
    bm.faces.new([vs[2],vs[3],vs[6],vs[7]])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_glass_lens(name, r=0.070, z=0.034):
    """Thin magnifying glass lens sitting in compass rim."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides=24; dome_h=0.008
    for j in range(sides):
        a=j*2*math.pi/sides
        bm.verts.new((r*math.cos(a),r*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    apex=bm.verts.new((0,0,z+dome_h))
    for j in range(sides):
        bm.faces.new([bm.verts[j],bm.verts[(j+1)%sides],apex])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_lid(name, r=0.072, height=0.010, open_angle=0.9):
    """Compass lid shown open at ~50°, with back-carved scene."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides=8; th=height
    # octagonal lid disc
    for j in range(sides):
        a=j*2*math.pi/sides+math.pi/sides
        bm.verts.new((r*math.cos(a),r*math.sin(a), 0))
        bm.verts.new((r*math.cos(a),r*math.sin(a), th))
    bm.verts.ensure_lookup_table()
    for j in range(sides):
        a=j*2; b=(j*2+2)%(sides*2); c=b+1; d=a+1
        bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bot=bm.verts.new((0,0,0)); top=bm.verts.new((0,0,th))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides*2],bm.verts[j*2],bot])
        bm.faces.new([bm.verts[j*2+1],bm.verts[(j+1)%sides*2+1],top])
    bm.to_mesh(me); bm.free()
    # pivot on bottom edge, rotate open
    ob.location=(0, -r, 0.032)
    ob.rotation_euler=(open_angle, 0, 0)
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_rune_panel(name, loc, rot=(0,0,0), w=0.040, h=0.026, d=0.003):
    """Rune-engraved panel on compass rim face."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    vs=[bm.verts.new(c) for c in [
        (-w/2,-d,0),( w/2,-d,0),( w/2,-d,h),(-w/2,-d,h),
        (-w/2, d,0),( w/2, d,0),( w/2, d,h),(-w/2, d,h)]]
    bm.faces.new([vs[0],vs[1],vs[2],vs[3]])
    bm.faces.new([vs[4],vs[7],vs[6],vs[5]])
    for q in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        bm.faces.new([vs[q[0]],vs[q[1]],vs[q[2]],vs[q[3]]])
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_soul_wisp(name, loc, r=0.016):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=5, radius=r, location=loc)
    ob = bpy.context.active_object; ob.name=ob.data.name=name
    return ob

def bm_ethereal_chain(name, attach_z, end_z, angle):
    """3-link thin ethereal chain from base to soul wisp."""
    links=[]
    locs=[attach_z+(end_z-attach_z)*t for t in [0.2,0.5,0.8]]
    r_h=0.030; r_off=r_h*0.8
    for li, lz in enumerate(locs):
        x=r_off*math.cos(angle); y=r_off*math.sin(angle)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.008, minor_radius=0.002,
            major_segments=8, minor_segments=4,
            location=(x,y,lz), rotation=(math.pi/2,0,angle+(li%2)*math.pi/2))
        cl=bpy.context.active_object
        cl.name=cl.data.name=f"{name}_L{li}"
        links.append(cl)
    return links

def bm_halo_ring(name, loc, r=0.085, minor=0.006):
    """Flat emission ring halo under compass."""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=r, minor_radius=minor,
        major_segments=32, minor_segments=5, location=loc)
    ob = bpy.context.active_object; ob.name=ob.data.name=name
    return ob

def bm_heart_glyph(name, loc, size=0.025, z_up=0.0):
    """Simple heart-shaped flat cartouche."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    pts=20; d=0.002
    for i in range(pts):
        t=i/pts * 2*math.pi
        x=size*(16*math.sin(t)**3)/16
        y=size*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/16
        bm.verts.new((x,y+size*0.3,d))
    bm.verts.ensure_lookup_table()
    ctr=bm.verts.new((0,size*0.3,d))
    for i in range(pts):
        bm.faces.new([bm.verts[i],bm.verts[(i+1)%pts],ctr])
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=(0,0,0)
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_chain_fob(name, start_z=-0.004, links=5):
    """Brass fob chain hanging from compass base."""
    chain_links=[]
    for li in range(links):
        z=start_z-li*0.016
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.008, minor_radius=0.003,
            major_segments=10, minor_segments=4,
            location=(0, 0.070, z),
            rotation=(math.pi/2, 0, (li%2)*math.pi/2))
        cl=bpy.context.active_object
        cl.name=cl.data.name=f"{name}_L{li}"
        chain_links.append(cl)
    return chain_links

def bm_spark(name, loc, r=0.006):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=5, ring_count=3, radius=r, location=loc)
    ob = bpy.context.active_object; ob.name=ob.data.name=name
    return ob

# ─────────────────────────────────────────────────────────────────────
# Main creation function
# ─────────────────────────────────────────────────────────────────────
def create_soul_compass():
    clear_scene()
    col = new_col("IsleTrial_SoulCompass")

    mat_brass  = build_brass_mat()
    mat_soul   = build_soul_mat()
    mat_glass  = build_glass_mat()
    mat_rose   = build_rose_mat()
    mat_rune   = build_rune_mat()
    mat_chain  = build_chain_mat()
    mat_halo   = build_halo_mat()
    mat_needle = build_needle_mat()
    mat_spark  = build_spark_mat()

    objs = []

    # ── Root ───────────────────────────────────────────────────────
    bpy.ops.object.empty_add(type='ARROWS', location=(0,0,0))
    root = bpy.context.active_object
    root.name = "SoulCompass_ROOT"
    link(col, root)

    # ── COMPASS BODY ───────────────────────────────────────────────
    body = bm_compass_body("SC_Body", r=0.072, height=0.034)
    assign_mat(body, mat_brass)
    smart_uv(body)
    link(col, body); objs.append(body)

    # ── COMPASS FACE (inner base disc) ─────────────────────────────
    face = bm_compass_face("SC_Face", r=0.068, z=0.034)
    assign_mat(face, mat_rose)
    smart_uv(face)
    link(col, face); objs.append(face)

    # ── COMPASS ROSE RAISED POINTS ─────────────────────────────────
    rose = bm_compass_rose_points("SC_CompassRose", z=0.036, r=0.058)
    assign_mat(rose, mat_brass)
    smart_uv(rose)
    link(col, rose); objs.append(rose)

    # ── ETHEREAL NEEDLE ─────────────────────────────────────────────
    needle = bm_needle("SC_Needle", z=0.037)
    assign_mat(needle, mat_needle)
    smart_uv(needle)
    link(col, needle); objs.append(needle)

    # ── GLASS LENS ─────────────────────────────────────────────────
    lens = bm_glass_lens("SC_Lens", r=0.070, z=0.036)
    assign_mat(lens, mat_glass)
    smart_uv(lens)
    link(col, lens); objs.append(lens)

    # ── OPEN LID ────────────────────────────────────────────────────
    lid = bm_lid("SC_Lid", r=0.070, height=0.012, open_angle=0.88)
    assign_mat(lid, mat_brass)
    smart_uv(lid)
    link(col, lid); objs.append(lid)

    # ── HEART GLYPH on lid interior ────────────────────────────────
    heart = bm_heart_glyph("SC_HeartGlyph",
                            loc=(0, -0.072*0.5, 0.048), size=0.018)
    heart.rotation_euler=(0.88, 0, 0)
    assign_mat(heart, mat_rune)
    smart_uv(heart)
    link(col, heart); objs.append(heart)

    # ── RUNE PANELS on 8 rim faces ─────────────────────────────────
    for ri in range(8):
        angle=ri*2*math.pi/8+math.pi/8
        rx=(0.074)*math.cos(angle); ry=(0.074)*math.sin(angle)
        rot_z=angle
        rp = bm_rune_panel(f"SC_Rune_{ri}",
                            loc=(rx,ry,0.010),
                            rot=(0, 0, rot_z+math.pi/2),
                            w=0.038, h=0.020, d=0.003)
        assign_mat(rp, mat_rune)
        smart_uv(rp)
        link(col, rp); objs.append(rp)

    # ── HALO RING under body ────────────────────────────────────────
    halo = bm_halo_ring("SC_Halo", loc=(0,0,-0.004), r=0.082, minor=0.005)
    assign_mat(halo, mat_halo)
    smart_uv(halo)
    link(col, halo); objs.append(halo)

    # ── 3 SOUL WISPS orbiting above ─────────────────────────────────
    wisp_angles = [0.0, 2.094, 4.189]  # 120° apart
    wisp_r_orbit = 0.060
    wisp_z = 0.095
    for wi, wa in enumerate(wisp_angles):
        wx=wisp_r_orbit*math.cos(wa); wy=wisp_r_orbit*math.sin(wa)
        wisp_r=0.018-wi*0.002
        w = bm_soul_wisp(f"SC_Wisp_{wi}", loc=(wx,wy,wisp_z+wi*0.012), r=wisp_r)
        assign_mat(w, mat_soul)
        smart_uv(w)
        link(col, w); objs.append(w)

        # Ethereal chain links to body
        chain_links = bm_ethereal_chain(f"SC_EtherChain_{wi}",
                                         attach_z=0.038, end_z=wisp_z+wi*0.012,
                                         angle=wa)
        for cl in chain_links:
            assign_mat(cl, mat_soul)
            smart_uv(cl)
            link(col, cl); objs.append(cl)

    # ── BRASS CHAIN FOB ─────────────────────────────────────────────
    fob_links = bm_chain_fob("SC_Fob", start_z=-0.006, links=5)
    for fl in fob_links:
        assign_mat(fl, mat_chain)
        smart_uv(fl)
        link(col, fl); objs.append(fl)

    # ── HINGE detail ───────────────────────────────────────────────
    for hi in range(3):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.005,
                                             depth=0.014,
                                             location=(0, -0.070, 0.032+hi*0.0),
                                             rotation=(0,0,0))
        hinge = bpy.context.active_object
        hinge.name = hinge.data.name = f"SC_Hinge_{hi}"
        hinge.location = (0+(hi-1)*0.020, -0.070, 0.030)
        assign_mat(hinge, mat_brass)
        smart_uv(hinge)
        link(col, hinge); objs.append(hinge)

    # ── RIM BUMPERS (decorative nubs on 8 corners) ─────────────────
    for ri in range(8):
        angle=ri*2*math.pi/8+math.pi/8
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=6, ring_count=4, radius=0.009,
            location=(0.075*math.cos(angle), 0.075*math.sin(angle), 0.034))
        nub = bpy.context.active_object
        nub.name = nub.data.name = f"SC_RimNub_{ri}"
        assign_mat(nub, mat_brass)
        smart_uv(nub)
        link(col, nub); objs.append(nub)

    # ── FLOATING SPARKS ─────────────────────────────────────────────
    spark_pos = [
        ( 0.095, 0.030, 0.080), (-0.088, 0.040, 0.075),
        ( 0.020,-0.092, 0.085), (-0.060,-0.065, 0.110),
    ]
    for spi, spos in enumerate(spark_pos):
        sp = bm_spark(f"SC_Spark_{spi}", loc=spos, r=0.006)
        assign_mat(sp, mat_spark)
        smart_uv(sp)
        link(col, sp); objs.append(sp)

    # ── MODIFIERS ──────────────────────────────────────────────────
    for o in objs:
        if o.type == 'MESH':
            bev = o.modifiers.new('Bevel','BEVEL')
            bev.width    = 0.001
            bev.segments = 2

    # ── PARENT all to root ─────────────────────────────────────────
    for o in objs:
        o.parent = root
    for fl in fob_links:
        fl.parent = root

    # ── UNITY EMPTIES ──────────────────────────────────────────────
    # Pickup trigger collider point
    bpy.ops.object.empty_add(type='SPHERE', location=(0,0,0.05))
    trigger = bpy.context.active_object
    trigger.name = "_SoulRevive_TriggerPoint"
    trigger["unity_note"] = ("SphereCollider (isTrigger=true, r=0.15) – attach "
                              "SoulReviveProp.cs here.  When player enters, show "
                              "Revive prompt and call ReviveSystem.ReviveTeammate().")
    trigger.empty_display_size = 0.15
    trigger.parent = root; link(col, trigger)

    # Glow light point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0.06))
    light_pt = bpy.context.active_object
    light_pt.name = "_ReviveLightPoint"
    light_pt["unity_note"] = ("Unity PointLight (teal #40FFD9, range=1.2m, "
                               "intensity=1.8) – parent here for pickup glow. "
                               "Animate intensity 1.0→2.5 using a sine curve.")
    light_pt.parent = root; link(col, light_pt)

    # Soul VFX emitter
    bpy.ops.object.empty_add(type='CIRCLE', location=(0,0,0.10))
    vfx_pt = bpy.context.active_object
    vfx_pt.name = "_SoulParticleVFX"
    vfx_pt["unity_note"] = ("Particle System spawn point – play SoulReleaseVFX "
                              "on pickup.  Soul particles drift upward and fade.")
    vfx_pt.parent = root; link(col, vfx_pt)

    # ── Viewport frame ─────────────────────────────────────────────
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_all(center=True)
                    break

    print("✓ Soul Compass revival prop created – IsleTrial_SoulCompass collection ready for FBX export.")
    print("  Unity: Attach SoulReviveProp.cs to _SoulRevive_TriggerPoint empty.")
    print("  Unity: Add PointLight child at _ReviveLightPoint for ambient glow.")
    print("  Unity: Play SoulReleaseVFX particle system on pickup at _SoulParticleVFX.")

create_soul_compass()
