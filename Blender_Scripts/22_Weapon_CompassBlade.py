"""
IsleTrial – Navigator's Compass Blade  (22_Weapon_CompassBlade.py)
===================================================================
A 1.1 m longsword forged from cartographic obsession.
Etched-map steel blade with a fuller groove, a compass-rose
cross-guard with 8 cardinal fins, dual gear-wheel quillons,
a mini telescope barrel, 4 directional gems, leather grip
with N-indicator ring, and a compass-rose disc pommel with
a visible glowing needle.
Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

rng = random.Random(0xD1A14C)

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
def build_blade_mat():
    mat = bpy.data.materials.new("CB_Steel")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(900,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(650,0)
    bsdf.inputs['Roughness'].default_value=0.22
    bsdf.inputs['Metallic'].default_value =0.95
    # blue-steel hue shift with map-etch lines
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-500,100)
    noise.inputs['Scale'].default_value=60.0
    noise.inputs['Detail'].default_value=4.0
    wave = ns.new('ShaderNodeTexWave'); wave.location=(-500,-100)
    wave.wave_type='BANDS'; wave.bands_direction='Z'
    wave.inputs['Scale'].default_value=42.0
    wave.inputs['Distortion'].default_value=0.8
    cr_w = ns.new('ShaderNodeValToRGB'); cr_w.location=(-250,-100)
    cr_w.color_ramp.elements[0].position=0.45; cr_w.color_ramp.elements[0].color=(0.06,0.12,0.28,1)
    cr_w.color_ramp.elements[1].position=0.55; cr_w.color_ramp.elements[1].color=(0.75,0.82,0.95,1)
    mix_n= ns.new('ShaderNodeMixRGB'); mix_n.blend_type='MULTIPLY'; mix_n.location=(-50,0)
    mix_n.inputs['Fac'].default_value=0.3
    img_a= img_slot(ns,"[UNITY] CB_Steel_Albedo",-550,-250)
    img_n= img_slot(ns,"[UNITY] CB_Steel_Normal",-550,-450)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(400,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(wave.outputs['Fac'],    cr_w.inputs['Fac'])
    lk.new(cr_w.outputs['Color'],  mix_n.inputs['Color1'])
    lk.new(noise.outputs['Fac'],   mix_n.inputs['Color2'])
    lk.new(mix_n.outputs['Color'], mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_brass_mat():
    mat = bpy.data.materials.new("CB_Brass")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(550,0)
    bsdf.inputs['Roughness'].default_value=0.38
    bsdf.inputs['Metallic'].default_value =0.90
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-400,100)
    noise.inputs['Scale'].default_value=20.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].position=0.2; cr.color_ramp.elements[0].color=(0.55,0.38,0.08,1)
    cr.color_ramp.elements[1].position=0.8; cr.color_ramp.elements[1].color=(0.88,0.65,0.18,1)
    img_a= img_slot(ns,"[UNITY] CB_Brass_Albedo",-450,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(350,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_leather_mat():
    mat = bpy.data.materials.new("CB_Leather")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Roughness'].default_value=0.78
    wave = ns.new('ShaderNodeTexWave'); wave.location=(-400,100)
    wave.inputs['Scale'].default_value=22.0
    wave.inputs['Distortion'].default_value=2.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].color=(0.12,0.06,0.02,1)
    cr.color_ramp.elements[1].color=(0.28,0.14,0.06,1)
    img_a= img_slot(ns,"[UNITY] CB_Leather_Albedo",-450,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(300,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_gem_mat(name, color=(0.1,0.6,1.0,1), emit_col=(0.15,0.7,1.0,1)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(400,0)
    bsdf.inputs['Base Color'].default_value      = color
    bsdf.inputs['Roughness'].default_value       = 0.04
    bsdf.inputs['Transmission Weight'].default_value = 0.80
    bsdf.inputs['IOR'].default_value             = 1.65
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,200)
    emit.inputs['Color'].default_value    = emit_col
    emit.inputs['Strength'].default_value = 2.0
    add  = ns.new('ShaderNodeAddShader'); add.location=(620,100)
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(emit.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_glass_mat():
    mat = bpy.data.materials.new("CB_Lens")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    mat.blend_method='BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value      =(0.85,0.92,0.98,1)
    bsdf.inputs['Roughness'].default_value       =0.02
    bsdf.inputs['Transmission Weight'].default_value=0.95
    bsdf.inputs['Alpha'].default_value           =0.35
    bsdf.inputs['IOR'].default_value             =1.52
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

# ─────────────────────────────────────────────────────────────────────
# BMesh builders
# ─────────────────────────────────────────────────────────────────────
def bm_blade(name, length=0.72, base_w=0.048, tip_w=0.004, thickness=0.012):
    """Longsword blade with tapered profile and central fuller groove."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=32
    for i in range(segs+1):
        t=i/segs; z=t*length
        w=base_w+(tip_w-base_w)*t**0.7
        th=thickness*(1-t*0.6)
        # fuller groove – reduce centre thickness
        fuller_depth=th*0.25*math.sin(t*math.pi)**0.5
        bm.verts.new(( w, 0, z))  # right edge
        bm.verts.new(( w*0.3,  th/2-fuller_depth, z))  # right top
        bm.verts.new((-w*0.3,  th/2-fuller_depth, z))  # left top
        bm.verts.new((-w, 0, z))  # left edge
        bm.verts.new((-w*0.3, -th/2+fuller_depth, z))  # left bot
        bm.verts.new(( w*0.3, -th/2+fuller_depth, z))  # right bot
    bm.verts.ensure_lookup_table()
    sides=6
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # tip point
    tip=bm.verts.new((0,0,length+0.04))
    for j in range(sides):
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],tip])
    # base edge cap
    bot=bm.verts.new((0,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_ricasso(name, loc=(0,0,0)):
    """Unsharpened ricasso section near cross-guard."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    w=0.048; th=0.014; h=0.09
    coords=[( w, 0,0),( w*0.35, th/2,0),(-w*0.35, th/2,0),
            (-w, 0,0),(-w*0.35,-th/2,0),( w*0.35,-th/2,0),
            ( w, 0,h),( w*0.35, th/2,h),(-w*0.35, th/2,h),
            (-w, 0,h),(-w*0.35,-th/2,h),( w*0.35,-th/2,h)]
    vs=[bm.verts.new(c) for c in coords]
    sides=6
    for j in range(sides):
        bm.faces.new([vs[j],vs[(j+1)%sides],vs[(j+1)%sides+sides],vs[j+sides]])
    bm.faces.new([vs[5],vs[4],vs[3],vs[2],vs[1],vs[0]])
    bm.faces.new([vs[6],vs[7],vs[8],vs[9],vs[10],vs[11]])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_compass_guard(name, loc=(0,0,0)):
    """8-point compass rose cross-guard."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    points=8; hub_r=0.042; arm_len=0.120; arm_w=0.022; th=0.016
    # hub
    for j in range(points*2):
        a=j*2*math.pi/(points*2)
        bm.verts.new((hub_r*math.cos(a), hub_r*math.sin(a), -th/2))
        bm.verts.new((hub_r*math.cos(a), hub_r*math.sin(a),  th/2))
    bm.verts.ensure_lookup_table()
    # arms (cardinal + ordinal)
    for pi in range(points):
        angle=pi*2*math.pi/points
        # arm tip
        tip_len=arm_len if pi%2==0 else arm_len*0.72
        tx=tip_len*math.cos(angle); ty=tip_len*math.sin(angle)
        w=arm_w*(0.5 if pi%2==1 else 1.0)
        perp_a=angle+math.pi/2
        for sign in (-1,1):
            bx=tx+w*sign*math.cos(perp_a); by=ty+w*sign*math.sin(perp_a)
            bm.verts.new((bx,by,-th/2))
            bm.verts.new((bx,by, th/2))
        # tip point
        bm.verts.new((tx+0.012*math.cos(angle),ty+0.012*math.sin(angle),-th/4))
        bm.verts.new((tx+0.012*math.cos(angle),ty+0.012*math.sin(angle), th/4))
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    mod = ob.modifiers.new('Sub','SUBSURF'); mod.levels=1; mod.render_levels=1
    return ob

def bm_gear_wheel(name, loc, teeth=14, outer_r=0.058, inner_r=0.038,
                  thickness=0.012, rot=(0,0,0)):
    """Flat gear disc with teeth."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    tooth_depth=outer_r-inner_r
    for i in range(teeth*4):
        a=i*2*math.pi/(teeth*4)
        # alternate between tooth tip and tooth root
        tooth_phase=(i%4) in (0,1)
        r=outer_r if tooth_phase else inner_r
        bm.verts.new((r*math.cos(a), r*math.sin(a), -thickness/2))
        bm.verts.new((r*math.cos(a), r*math.sin(a),  thickness/2))
    bm.verts.ensure_lookup_table()
    n=teeth*4
    for j in range(n):
        a=j*2; b=(j*2+2)%(n*2); c=b+1; d=a+1
        bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # hub hole – approximated by solid hub disc
    hub_r=inner_r*0.38
    for j in range(16):
        a=j*2*math.pi/16
        bm.verts.new((hub_r*math.cos(a),hub_r*math.sin(a),-thickness/2))
        bm.verts.new((hub_r*math.cos(a),hub_r*math.sin(a), thickness/2))
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_telescope(name, loc=(0,0,0), rot=(0,0,0)):
    """Mini telescope barrel side-mounted on guard."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=5; sides=10
    radii=[0.016,0.016,0.013,0.013,0.010,0.010]
    lengths=[0,0.04,0.04,0.06,0.06,0.08]
    z=0
    for seg_i,(r,dl) in enumerate(zip(radii,lengths)):
        z+=dl
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((r*math.cos(a),r*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    total_rings=len(radii)
    for i in range(total_rings-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    cap_b=bm.verts.new((0,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],cap_b])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_grip(name, loc=(0,0,0), length=0.20, r=0.022):
    """Leather-wrapped grip with diamond cross-section."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=20; sides=8
    for i in range(segs+1):
        t=i/segs; z=loc[2]+t*length
        # slight barrel shape
        bulge=1.0+0.12*math.sin(t*math.pi)
        rv=r*bulge
        # add wrap grooves
        groove=0.004*math.sin(t*math.pi*12)
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new(((rv+groove)*math.cos(a),(rv+groove)*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bot=bm.verts.new((0,0,loc[2]))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    top=bm.verts.new((0,0,loc[2]+length))
    for j in range(sides):
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],top])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_compass_pommel(name, loc=(0,0,0), r=0.040):
    """Compass rose disc pommel."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    # disc
    sides=24; th=0.022
    for j in range(sides):
        a=j*2*math.pi/sides
        bm.verts.new((r*math.cos(a),r*math.sin(a),-th))
        bm.verts.new((r*math.cos(a),r*math.sin(a), th))
    bm.verts.ensure_lookup_table()
    for j in range(sides):
        a=j*2; b=(j*2+2)%(sides*2); c=b+1; d=a+1
        bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # top and bottom caps using fan
    top_ctr=bm.verts.new((0,0,th)); bot_ctr=bm.verts.new((0,0,-th))
    for j in range(sides):
        bm.faces.new([bm.verts[j*2+1],bm.verts[((j+1)%sides)*2+1],top_ctr])
        bm.faces.new([bm.verts[((j+1)%sides)*2],bm.verts[j*2],bot_ctr])
    # raised compass points on top face
    for pi in range(8):
        angle=pi*2*math.pi/8
        pr=r*0.78; pz=th+0.008
        bm.verts.new((pr*math.cos(angle),pr*math.sin(angle),pz))
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    mod = ob.modifiers.new('Bevel','BEVEL'); mod.width=0.003; mod.segments=2
    return ob

def bm_compass_needle(name, loc=(0,0,0)):
    """Glowing compass needle – thin diamond cross-section blade."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    # N-pointing half
    verts=[bm.verts.new(v) for v in [
        ( 0.0, 0.032, 0.005),( 0.0, 0.032,-0.005),
        ( 0.004, 0, 0),     (-0.004, 0, 0),
        ( 0.0,-0.020, 0.004),( 0.0,-0.020,-0.004)]]
    bm.faces.new([verts[0],verts[2],verts[4],verts[5],verts[3],verts[1]])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_directional_gem(name, loc, r=0.012):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=5, radius=r, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    ob.scale = (1,1,0.6)
    return ob

def bm_map_rune(name, loc, rot=(0,0,0), size=0.030):
    """Etched coordinate rune panel on blade surface."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    s=size; d=0.002
    vs=[bm.verts.new(c) for c in [
        (-s,-s*0.5,0),(s,-s*0.5,0),(s,s*0.5,0),(-s,s*0.5,0),
        (-s,-s*0.5,d),(s,-s*0.5,d),(s,s*0.5,d),(-s,s*0.5,d)]]
    bm.faces.new([vs[0],vs[1],vs[2],vs[3]])
    bm.faces.new([vs[4],vs[7],vs[6],vs[5]])
    for q in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        bm.faces.new([vs[q[0]],vs[q[1]],vs[q[2]],vs[q[3]]])
    bm.to_mesh(me); bm.free()
    ob.location = loc; ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

# ─────────────────────────────────────────────────────────────────────
# Main creation function
# ─────────────────────────────────────────────────────────────────────
def create_compass_blade():
    clear_scene()
    col = new_col("IsleTrial_CompassBlade")

    mat_blade   = build_blade_mat()
    mat_brass   = build_brass_mat()
    mat_leather = build_leather_mat()
    mat_gem_N   = build_gem_mat("CB_Gem_N", color=(0.1,0.3,0.9,1), emit_col=(0.15,0.4,1.0,1))
    mat_gem_S   = build_gem_mat("CB_Gem_S", color=(0.9,0.1,0.1,1), emit_col=(1.0,0.15,0.15,1))
    mat_gem_E   = build_gem_mat("CB_Gem_E", color=(0.9,0.65,0.05,1), emit_col=(1.0,0.75,0.1,1))
    mat_gem_W   = build_gem_mat("CB_Gem_W", color=(0.1,0.75,0.2,1), emit_col=(0.15,0.9,0.25,1))
    mat_glass   = build_glass_mat()
    mat_needle  = build_gem_mat("CB_Needle", color=(0.9,0.2,0.1,1), emit_col=(1.0,0.25,0.1,1))

    objs = []

    # ── Root ───────────────────────────────────────────────────────
    bpy.ops.object.empty_add(type='ARROWS', location=(0,0,0))
    root = bpy.context.active_object
    root.name = "CompassBlade_ROOT"
    link(col, root)

    # ── BLADE ──────────────────────────────────────────────────────
    blade = bm_blade("CB_Blade", length=0.72, base_w=0.048, tip_w=0.004, thickness=0.012)
    blade.location=(0,0,0.09)
    assign_mat(blade, mat_blade)
    smart_uv(blade)
    link(col, blade); objs.append(blade)

    # ── RICASSO ────────────────────────────────────────────────────
    ricasso = bm_ricasso("CB_Ricasso", loc=(0,0,0.09))
    assign_mat(ricasso, mat_blade)
    smart_uv(ricasso)
    link(col, ricasso); objs.append(ricasso)

    # ── MAP RUNE OVERLAYS on blade ─────────────────────────────────
    rune_data = [
        ((0.025, 0.007, 0.35), (0, 0, 0)),
        ((-0.025,-0.007, 0.35), (0, math.pi, 0)),
        ((0.022, 0.007, 0.52), (0, 0, 0.2)),
        ((-0.022,-0.007, 0.52), (0, math.pi, -0.2)),
        ((0.018, 0.006, 0.65), (0, 0, 0.4)),
        ((-0.018,-0.006, 0.65), (0, math.pi, -0.4)),
        ((0.024, 0.007, 0.22), (0, 0, -0.1)),
        ((-0.024,-0.007, 0.22), (0, math.pi, 0.1)),
        ((0.020, 0.006, 0.44), (0, 0, 0.15)),
        ((-0.020,-0.006, 0.44), (0, math.pi, -0.15)),
    ]
    for ri, (rloc, rrot) in enumerate(rune_data):
        rp = bm_map_rune(f"CB_Rune_{ri}", loc=rloc, rot=rrot, size=0.024)
        assign_mat(rp, mat_brass)
        smart_uv(rp)
        link(col, rp); objs.append(rp)

    # ── COMPASS-ROSE CROSS-GUARD ────────────────────────────────────
    guard = bm_compass_guard("CB_CompassGuard", loc=(0,0,0.09))
    assign_mat(guard, mat_brass)
    smart_uv(guard)
    link(col, guard); objs.append(guard)

    # ── GEAR WHEEL QUILLONS ────────────────────────────────────────
    gear_L = bm_gear_wheel("CB_GearL", loc=(-0.095, 0, 0.09),
                            teeth=16, outer_r=0.052, inner_r=0.035,
                            thickness=0.014, rot=(math.pi/2, 0, 0))
    assign_mat(gear_L, mat_brass)
    smart_uv(gear_L)
    link(col, gear_L); objs.append(gear_L)

    gear_R = bm_gear_wheel("CB_GearR", loc=( 0.095, 0, 0.09),
                            teeth=16, outer_r=0.052, inner_r=0.035,
                            thickness=0.014, rot=(math.pi/2, 0, 0))
    assign_mat(gear_R, mat_brass)
    smart_uv(gear_R)
    link(col, gear_R); objs.append(gear_R)

    # ── TELESCOPE side mount ────────────────────────────────────────
    tele = bm_telescope("CB_Telescope",
                         loc=(0.066, 0, 0.09),
                         rot=(0, math.pi/2, 0))
    assign_mat(tele, mat_brass)
    smart_uv(tele)
    link(col, tele); objs.append(tele)

    # Lens glass cap for telescope
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=5,
                                          radius=0.012, location=(0.14, 0, 0.09))
    tele_lens = bpy.context.active_object
    tele_lens.name = tele_lens.data.name = "CB_TeleLens"
    tele_lens.scale = (0.4, 1.0, 1.0)
    assign_mat(tele_lens, mat_glass)
    smart_uv(tele_lens)
    link(col, tele_lens); objs.append(tele_lens)

    # ── DIRECTIONAL GEMS on guard cardinal points ───────────────────
    gem_data = [
        ("CB_GemN", (0, 0.108, 0.095), mat_gem_N),
        ("CB_GemS", (0,-0.108, 0.095), mat_gem_S),
        ("CB_GemE", ( 0.108, 0, 0.095), mat_gem_E),
        ("CB_GemW", (-0.108, 0, 0.095), mat_gem_W),
    ]
    for g_name, g_loc, g_mat in gem_data:
        gm = bm_directional_gem(g_name, loc=g_loc, r=0.014)
        assign_mat(gm, g_mat)
        smart_uv(gm)
        link(col, gm); objs.append(gm)

    # ── GRIP ────────────────────────────────────────────────────────
    grip = bm_grip("CB_Grip", loc=(0,0,-0.20), length=0.20, r=0.022)
    assign_mat(grip, mat_leather)
    smart_uv(grip)
    link(col, grip); objs.append(grip)

    # N-indicator ring on grip
    n_ring_loc = (0, 0, -0.14)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.004,
                                      major_segments=14, minor_segments=5,
                                      location=n_ring_loc)
    n_ring = bpy.context.active_object; n_ring.name = n_ring.data.name = "CB_NRing"
    assign_mat(n_ring, mat_brass)
    smart_uv(n_ring)
    link(col, n_ring); objs.append(n_ring)

    # ── COMPASS POMMEL ─────────────────────────────────────────────
    pommel = bm_compass_pommel("CB_Pommel", loc=(0,0,-0.24), r=0.040)
    assign_mat(pommel, mat_brass)
    smart_uv(pommel)
    link(col, pommel); objs.append(pommel)

    # Compass needle inside pommel
    needle = bm_compass_needle("CB_Needle_Mesh", loc=(0, 0, -0.218))
    assign_mat(needle, mat_needle)
    smart_uv(needle)
    link(col, needle); objs.append(needle)

    # Glass lens cap over pommel face
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6,
                                          radius=0.040, location=(0,0,-0.214))
    pom_lens = bpy.context.active_object
    pom_lens.name = pom_lens.data.name = "CB_PommelGlass"
    pom_lens.scale = (1, 1, 0.22)
    assign_mat(pom_lens, mat_glass)
    smart_uv(pom_lens)
    link(col, pom_lens); objs.append(pom_lens)

    # ── GUARD CENTRAL HUB collar ────────────────────────────────────
    bpy.ops.mesh.primitive_torus_add(major_radius=0.046, minor_radius=0.010,
                                      major_segments=18, minor_segments=6,
                                      location=(0,0,0.09))
    hub_ring = bpy.context.active_object
    hub_ring.name = hub_ring.data.name = "CB_GuardHub"
    assign_mat(hub_ring, mat_brass)
    smart_uv(hub_ring)
    link(col, hub_ring); objs.append(hub_ring)

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
    bpy.ops.object.empty_add(type='SINGLE_ARROW', location=(0,0,0.82))
    tip_pt = bpy.context.active_object
    tip_pt.name = "CB_BladePoint"
    tip_pt["unity_note"] = "Blade tip – damage ray origin"
    tip_pt.parent = root; link(col, tip_pt)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,-0.10))
    grip_pt = bpy.context.active_object
    grip_pt.name = "CB_GripPoint"
    grip_pt["unity_note"] = "Right Hand grip attach"
    grip_pt.parent = root; link(col, grip_pt)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_all(center=True)
                    break

    print("✓ Navigator's Compass Blade created – IsleTrial_CompassBlade collection ready for FBX export.")

create_compass_blade()
