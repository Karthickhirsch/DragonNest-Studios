"""
IsleTrial – Navigation Buoys  (25_Ocean_Buoys.py)
===================================================
Prompt 05-A: 3 sea-worn navigation buoys.
  • Buoy_Marker_Red   – conical top, iron bands, chain, barnacles, red cage light
  • Buoy_Marker_Green – flat lid, same body, green paint, cage light
  • Buoy_Lighted_Large– capsule body, solar panel, mast, warning stripes, anchor chain
Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

rng = random.Random(0xB0A710)

# ─────────────────────────────────────────────────────────────────────
# Scene helpers
# ─────────────────────────────────────────────────────────────────────
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

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

def add_mat(obj, mat):
    obj.data.materials.append(mat)

def smart_uv(obj, angle=55):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=angle, island_margin=0.02)
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
def build_paint_mat(name, base_color, roughness=0.60):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(850,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(580,0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value  = roughness
    bsdf.inputs['Metallic'].default_value   = 0.0
    # chipped paint noise
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-400,100)
    noise.inputs['Scale'].default_value   = 28.0
    noise.inputs['Detail'].default_value  = 10.0
    noise.inputs['Roughness'].default_value = 0.65
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].position=0.65; cr.color_ramp.elements[0].color=(0.12,0.08,0.04,1)
    cr.color_ramp.elements[1].position=0.80; cr.color_ramp.elements[1].color=(0,0,0,0)
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type='MIX'; mix.location=(100,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(mix.inputs['Fac'], cr.outputs['Color'])
    base_c = ns.new('ShaderNodeRGB'); base_c.location=(-150,-100)
    base_c.outputs[0].default_value=base_color
    img_a= img_slot(ns, f"[UNITY] {name}_Albedo",-450,-200)
    img_n= img_slot(ns, f"[UNITY] {name}_Normal",-450,-400)
    mix_final= ns.new('ShaderNodeMixRGB'); mix_final.location=(380,0)
    mix_final.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'],  cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],   mix.inputs['Fac'])
    lk.new(base_c.outputs['Color'],mix.inputs['Color1'])
    lk.new(cr.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],  mix_final.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix_final.inputs['Color2'])
    lk.new(mix_final.outputs['Color'], bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def build_iron_rusty_mat():
    mat = bpy.data.materials.new("Mat_Buoy_Iron_Rusty")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(550,0)
    bsdf.inputs['Base Color'].default_value=(0.22,0.13,0.06,1)
    bsdf.inputs['Roughness'].default_value =0.85
    bsdf.inputs['Metallic'].default_value  =0.50
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-350,100)
    noise.inputs['Scale'].default_value=20.0; noise.inputs['Detail'].default_value=8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-100,100)
    cr.color_ramp.elements[0].color=(0.38,0.18,0.06,1)
    cr.color_ramp.elements[1].color=(0.22,0.10,0.04,1)
    img_a= img_slot(ns,"[UNITY] Mat_Iron_Albedo",-400,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(250,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_light_mat(name, color, strength=3.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    emit = ns.new('ShaderNodeEmission'); emit.location=(350,0)
    emit.inputs['Color'].default_value    = color
    emit.inputs['Strength'].default_value = strength
    lk.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

def build_barnacle_mat():
    mat = bpy.data.materials.new("Mat_Barnacle")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value=(0.42,0.38,0.34,1)
    bsdf.inputs['Roughness'].default_value =0.95
    vor  = ns.new('ShaderNodeTexVoronoi'); vor.location=(-350,100)
    vor.inputs['Scale'].default_value=22.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location=(200,150)
    bmp.inputs['Strength'].default_value=0.75
    lk.new(vor.outputs['Distance'], bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_glass_mat():
    mat = bpy.data.materials.new("Mat_Buoy_Glass")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    mat.blend_method='BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value=(0.85,0.95,0.98,1)
    bsdf.inputs['Roughness'].default_value =0.05
    bsdf.inputs['Transmission Weight'].default_value=0.88
    bsdf.inputs['Alpha'].default_value     =0.35
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# ─────────────────────────────────────────────────────────────────────
# Shared geometry helpers
# ─────────────────────────────────────────────────────────────────────
def make_cylinder(name, r, depth, loc=(0,0,0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth,
                                         location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def make_cone(name, r1, r2, depth, loc=(0,0,0), verts=24):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                     depth=depth, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def make_sphere(name, r, loc=(0,0,0), segs=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=8, radius=r, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def make_torus(name, major_r, minor_r, loc=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_r, minor_radius=minor_r,
                                      major_segments=20, minor_segments=6, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_iron_band(name, loc, r, minor=0.020):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=minor,
                                      major_segments=24, minor_segments=6, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_chain_link(name, loc, mr=0.030, minor=0.008, rot_z=0.0):
    bpy.ops.mesh.primitive_torus_add(major_radius=mr, minor_radius=minor,
                                      major_segments=14, minor_segments=5,
                                      location=loc, rotation=(math.pi/2, 0, rot_z))
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_cage_bar(name, loc, length=0.25, r=0.006, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=r, depth=length,
                                         location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_barnacle_patch(name, loc, count=8, spread=0.15):
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    for _ in range(count):
        cx=rng.uniform(-spread,spread); cy=rng.uniform(-spread,spread)
        r=rng.uniform(0.012,0.030); h=rng.uniform(0.015,0.035); segs=6
        for j in range(segs):
            a=j*2*math.pi/segs
            bm.verts.new((cx+r*math.cos(a),cy+r*math.sin(a),0))
        bm.verts.ensure_lookup_table()
        base=len(bm.verts)-segs
        tip=bm.verts.new((cx,cy,h))
        rh =bm.verts.new((cx,cy,h*0.3))
        for j in range(segs):
            bm.faces.new([bm.verts[base+j],bm.verts[base+(j+1)%segs],rh])
        for j in range(segs):
            bm.faces.new([rh,bm.verts[base+(j+1)%segs],bm.verts[base+j],tip])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_light_cage(name, loc, cage_r=0.080, cage_h=0.18, bars=8):
    """Cylindrical wire cage for buoy light housing."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    bar_r=0.005
    # vertical bars
    for i in range(bars):
        a=i*2*math.pi/bars
        cx=cage_r*math.cos(a); cy=cage_r*math.sin(a)
        for j in range(4):
            t=j/3; z=t*cage_h-cage_h/2
            bm.verts.new((cx,cy,z))
    bm.verts.ensure_lookup_table()
    # horizontal rings top & bottom
    for ring_z in (-cage_h/2+0.01, 0, cage_h/2-0.01):
        for i in range(bars):
            a=i*2*math.pi/bars
            bm.verts.new((cage_r*math.cos(a),cage_r*math.sin(a),ring_z))
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    mod=ob.modifiers.new('Skin','SKIN')
    for v in ob.data.vertices:
        ob.data.skin_vertices[0].data[v.index].radius=(bar_r,bar_r)
    return ob

def bm_stripe_band(name, loc, r, height, color_mat, white_mat):
    """Alternating colour stripe cylinder (for large buoy)."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    bands=8; sides=24
    for i in range(bands+1):
        t=i/bands; z=t*height
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((r*math.cos(a),r*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(bands):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bot=bm.verts.new((0,0,0)); top=bm.verts.new((0,0,height))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
        bm.faces.new([bm.verts[bands*sides+j],bm.verts[bands*sides+(j+1)%sides],top])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    # alternating materials per face band
    ob.data.materials.append(color_mat)
    ob.data.materials.append(white_mat)
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_solar_panel(name, loc=(0,0,0), rot=(0,0,0)):
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    w=0.22; h=0.14; d=0.012
    vs=[bm.verts.new(c) for c in [
        (-w,-h,0),(w,-h,0),(w,h,0),(-w,h,0),
        (-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)]]
    bm.faces.new([vs[0],vs[1],vs[2],vs[3]])
    bm.faces.new([vs[4],vs[7],vs[6],vs[5]])
    for q in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        bm.faces.new([vs[q[0]],vs[q[1]],vs[q[2]],vs[q[3]]])
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_fin(name, loc=(0,0,0), rot=(0,0,0), size=0.18):
    """Triangular marker fin on buoy top."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    vs=[bm.verts.new(c) for c in [
        (-size/2,0.005,0),(size/2,0.005,0),(0,0.005,size*0.8),
        (-size/2,-0.005,0),(size/2,-0.005,0),(0,-0.005,size*0.8)]]
    bm.faces.new([vs[0],vs[1],vs[2]])
    bm.faces.new([vs[3],vs[5],vs[4]])
    bm.faces.new([vs[0],vs[2],vs[5],vs[3]])
    bm.faces.new([vs[1],vs[4],vs[5],vs[2]])
    bm.faces.new([vs[0],vs[3],vs[4],vs[1]])
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

# ─────────────────────────────────────────────────────────────────────
# Number emboss
# ─────────────────────────────────────────────────────────────────────
def emboss_number(col, body_obj, number_str, loc, mat_paint):
    """Text object parented to buoy body as embossed number marker."""
    bpy.ops.object.text_add(location=loc)
    txt = bpy.context.active_object
    txt.data.body = number_str
    txt.data.extrude = 0.012
    txt.data.size     = 0.18
    txt.data.align_x  = 'CENTER'
    txt.name = f"Buoy_Number_{number_str}"
    bpy.ops.object.convert(target='MESH')
    txt_mesh = bpy.context.active_object
    txt_mesh.name = f"Buoy_Number_{number_str}"
    assign_mat(txt_mesh, mat_paint)
    link(col, txt_mesh)
    return txt_mesh

# ─────────────────────────────────────────────────────────────────────
# Buoy builder functions
# ─────────────────────────────────────────────────────────────────────
def build_red_buoy(col, mat_red, mat_iron, mat_barnacle,
                   mat_red_light, mat_glass):
    """Buoy_Marker_Red – conical, 0.4m radius, 1.2m tall."""
    objs = []
    bpy.ops.object.empty_add(type='ARROWS', location=(-2.5,0,0))
    root = bpy.context.active_object; root.name="Buoy_Marker_Red"; link(col,root)

    # Body
    body = make_cylinder("BMR_Body", r=0.40, depth=1.20, loc=(-2.5,0,0.60), verts=28)
    assign_mat(body, mat_red); smart_uv(body); link(col,body); objs.append(body)

    # Cone top
    cone = make_cone("BMR_Cone", r1=0.40, r2=0.02, depth=0.30,
                     loc=(-2.5,0,1.35), verts=28)
    assign_mat(cone, mat_red); smart_uv(cone); link(col,cone); objs.append(cone)

    # Marker fin on cone tip
    fin = bm_fin("BMR_Fin", loc=(-2.5,0,1.55), rot=(0,0,0), size=0.20)
    assign_mat(fin, mat_red); smart_uv(fin); link(col,fin); objs.append(fin)

    # 3 iron band rings
    for bi, bz in enumerate([0.25, 0.60, 0.95]):
        band = bm_iron_band(f"BMR_Band_{bi}", loc=(-2.5,0,bz), r=0.42, minor=0.022)
        assign_mat(band, mat_iron); smart_uv(band); link(col,band); objs.append(band)

    # Bottom ring + 3 chain links
    bot_ring = bm_iron_band("BMR_BottomRing", loc=(-2.5,0,0.04), r=0.38, minor=0.028)
    assign_mat(bot_ring, mat_iron); smart_uv(bot_ring); link(col,bot_ring); objs.append(bot_ring)
    for ci in range(3):
        cl = bm_chain_link(f"BMR_Chain_{ci}", loc=(-2.5,0,-0.06-ci*0.08),
                           mr=0.040, minor=0.010, rot_z=(ci%2)*math.pi/2)
        assign_mat(cl, mat_iron); smart_uv(cl); link(col,cl); objs.append(cl)

    # Barnacle patches on lower half
    for bi in range(5):
        angle=bi*2*math.pi/5
        bp = bm_barnacle_patch(f"BMR_Barnacles_{bi}",
                                loc=(-2.5+0.40*math.cos(angle), 0.40*math.sin(angle), 0.25+bi*0.04),
                                count=6, spread=0.10)
        assign_mat(bp, mat_barnacle); smart_uv(bp); link(col,bp); objs.append(bp)

    # Light housing cage at top
    cage = bm_light_cage("BMR_Cage", loc=(-2.5,0,1.62), cage_r=0.060, cage_h=0.14, bars=8)
    assign_mat(cage, mat_iron); link(col,cage); objs.append(cage)

    # Red light sphere inside cage
    light_sph = make_sphere("BMR_LightSphere", r=0.030, loc=(-2.5,0,1.68))
    assign_mat(light_sph, mat_red_light); smart_uv(light_sph)
    link(col,light_sph); objs.append(light_sph)

    # Glass dome over light
    glass_dome = make_sphere("BMR_LightGlass", r=0.062, loc=(-2.5,0,1.66), segs=10)
    assign_mat(glass_dome, mat_glass); smart_uv(glass_dome)
    link(col,glass_dome); objs.append(glass_dome)

    # Unity light point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-2.5,0,1.68))
    lpt = bpy.context.active_object; lpt.name="BMR_LightPoint"
    lpt["unity_note"]="PointLight Red – 8m range, intensity 2.5, flashing"
    link(col,lpt); lpt.parent=root

    for o in objs: o.parent=root
    return root

def build_green_buoy(col, mat_green, mat_iron, mat_barnacle,
                     mat_green_light, mat_glass):
    """Buoy_Marker_Green – flat lid cap variant."""
    objs=[]
    bpy.ops.object.empty_add(type='ARROWS', location=(0,0,0))
    root=bpy.context.active_object; root.name="Buoy_Marker_Green"; link(col,root)

    body=make_cylinder("BMG_Body", r=0.40, depth=1.20, loc=(0,0,0.60), verts=28)
    assign_mat(body, mat_green); smart_uv(body); link(col,body); objs.append(body)

    # Flat cylindrical can lid instead of cone
    lid=make_cylinder("BMG_Lid", r=0.42, depth=0.10, loc=(0,0,1.25), verts=28)
    assign_mat(lid, mat_iron); smart_uv(lid); link(col,lid); objs.append(lid)
    lid_top=make_cylinder("BMG_LidTop", r=0.30, depth=0.05, loc=(0,0,1.32), verts=20)
    assign_mat(lid_top, mat_green); smart_uv(lid_top); link(col,lid_top); objs.append(lid_top)

    # 3 iron bands
    for bi, bz in enumerate([0.25, 0.60, 0.95]):
        band=bm_iron_band(f"BMG_Band_{bi}", loc=(0,0,bz), r=0.42, minor=0.022)
        assign_mat(band, mat_iron); smart_uv(band); link(col,band); objs.append(band)

    # Bottom ring + chains
    bot_ring=bm_iron_band("BMG_BottomRing", loc=(0,0,0.04), r=0.38, minor=0.028)
    assign_mat(bot_ring,mat_iron); smart_uv(bot_ring); link(col,bot_ring); objs.append(bot_ring)
    for ci in range(3):
        cl=bm_chain_link(f"BMG_Chain_{ci}", loc=(0,0,-0.06-ci*0.08),
                         mr=0.040, minor=0.010, rot_z=(ci%2)*math.pi/2)
        assign_mat(cl,mat_iron); smart_uv(cl); link(col,cl); objs.append(cl)

    # Barnacles lower half
    for bi in range(5):
        angle=bi*2*math.pi/5
        bp=bm_barnacle_patch(f"BMG_Barnacles_{bi}",
                              loc=(0.40*math.cos(angle),0.40*math.sin(angle),0.22+bi*0.04),
                              count=5, spread=0.09)
        assign_mat(bp,mat_barnacle); smart_uv(bp); link(col,bp); objs.append(bp)

    # Light cage on lid
    cage=bm_light_cage("BMG_Cage", loc=(0,0,1.38), cage_r=0.055, cage_h=0.12, bars=8)
    assign_mat(cage,mat_iron); link(col,cage); objs.append(cage)
    light_sph=make_sphere("BMG_LightSphere", r=0.028, loc=(0,0,1.44))
    assign_mat(light_sph, mat_green_light); smart_uv(light_sph)
    link(col,light_sph); objs.append(light_sph)
    glass_dome=make_sphere("BMG_LightGlass", r=0.058, loc=(0,0,1.42), segs=10)
    assign_mat(glass_dome,mat_glass); smart_uv(glass_dome)
    link(col,glass_dome); objs.append(glass_dome)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,1.44))
    lpt=bpy.context.active_object; lpt.name="BMG_LightPoint"
    lpt["unity_note"]="PointLight Green – 8m range, intensity 2.5, flashing"
    link(col,lpt); lpt.parent=root

    for o in objs: o.parent=root
    return root

def build_large_buoy(col, mat_orange, mat_white, mat_iron, mat_white_light, mat_glass):
    """Buoy_Lighted_Large – 0.7m radius capsule, mast, solar panel."""
    objs=[]
    bpy.ops.object.empty_add(type='ARROWS', location=(3.5,0,0))
    root=bpy.context.active_object; root.name="Buoy_Lighted_Large"; link(col,root)

    mat_wp_white = bpy.data.materials.new("Mat_Buoy_White")
    mat_wp_white.use_nodes=True
    ns,lk=ns_lk(mat_wp_white); ns.clear()
    out=ns.new('ShaderNodeOutputMaterial'); out.location=(500,0)
    bsdf=ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(250,0)
    bsdf.inputs['Base Color'].default_value=(0.88,0.88,0.88,1)
    bsdf.inputs['Roughness'].default_value=0.62
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])

    # Capsule body (cylinder + two hemisphere caps)
    body_cyl=make_cylinder("BLL_BodyCyl", r=0.70, depth=1.60, loc=(3.5,0,0.80), verts=32)
    assign_mat(body_cyl, mat_orange); smart_uv(body_cyl); link(col,body_cyl); objs.append(body_cyl)
    cap_top=make_sphere("BLL_CapTop", r=0.70, loc=(3.5,0,1.60), segs=16)
    assign_mat(cap_top, mat_orange); smart_uv(cap_top); link(col,cap_top); objs.append(cap_top)
    cap_bot=make_sphere("BLL_CapBot", r=0.70, loc=(3.5,0,0.0), segs=16)
    assign_mat(cap_bot, mat_orange); smart_uv(cap_bot); link(col,cap_bot); objs.append(cap_bot)

    # Warning stripes – alternating band rings (torus pairs)
    stripe_zs=[0.30,0.60,0.90,1.20,1.50]
    for si,sz in enumerate(stripe_zs):
        col_mat=mat_white if si%2==0 else mat_orange
        stripe=bm_iron_band(f"BLL_Stripe_{si}", loc=(3.5,0,sz), r=0.72, minor=0.080)
        assign_mat(stripe, col_mat); smart_uv(stripe); link(col,stripe); objs.append(stripe)

    # Iron bands
    for bi, bz in enumerate([0.15, 0.80, 1.45]):
        band=bm_iron_band(f"BLL_Band_{bi}", loc=(3.5,0,bz), r=0.73, minor=0.028)
        assign_mat(band,mat_iron); smart_uv(band); link(col,band); objs.append(band)

    # Mast
    mast=make_cylinder("BLL_Mast", r=0.045, depth=1.30, loc=(3.5,0,2.25), verts=10)
    assign_mat(mast,mat_iron); smart_uv(mast); link(col,mast); objs.append(mast)

    # Solar panel on mast
    panel=bm_solar_panel("BLL_SolarPanel", loc=(3.5,0,2.95), rot=(-0.35,0,0))
    sp_mat=bpy.data.materials.new("Mat_SolarPanel")
    sp_mat.use_nodes=True; ns2,lk2=ns_lk(sp_mat); ns2.clear()
    out2=ns2.new('ShaderNodeOutputMaterial'); out2.location=(500,0)
    bsdf2=ns2.new('ShaderNodeBsdfPrincipled'); bsdf2.location=(250,0)
    bsdf2.inputs['Base Color'].default_value=(0.05,0.08,0.18,1)
    bsdf2.inputs['Roughness'].default_value=0.18; bsdf2.inputs['Metallic'].default_value=0.6
    lk2.new(bsdf2.outputs['BSDF'],out2.inputs['Surface'])
    assign_mat(panel,sp_mat); smart_uv(panel); link(col,panel); objs.append(panel)

    # Large light housing on mast top
    big_cage=bm_light_cage("BLL_LightCage", loc=(3.5,0,3.02), cage_r=0.15, cage_h=0.30, bars=12)
    assign_mat(big_cage,mat_iron); link(col,big_cage); objs.append(big_cage)
    big_light=make_sphere("BLL_LightSphere", r=0.080, loc=(3.5,0,3.10), segs=10)
    assign_mat(big_light,mat_white_light); smart_uv(big_light)
    link(col,big_light); objs.append(big_light)
    big_glass=make_sphere("BLL_LightGlass", r=0.15, loc=(3.5,0,3.10), segs=12)
    assign_mat(big_glass,mat_glass); smart_uv(big_glass)
    link(col,big_glass); objs.append(big_glass)

    # Anchor chain at waterline
    for ci in range(5):
        cl=bm_chain_link(f"BLL_AnchorChain_{ci}", loc=(3.5,0,-0.08-ci*0.12),
                         mr=0.055, minor=0.015, rot_z=(ci%2)*math.pi/2)
        assign_mat(cl,mat_iron); smart_uv(cl); link(col,cl); objs.append(cl)

    # Bottom eyebolt
    eye=make_torus("BLL_EyeBolt", major_r=0.060, minor_r=0.014, loc=(3.5,0,-0.08))
    assign_mat(eye,mat_iron); smart_uv(eye); link(col,eye); objs.append(eye)

    # Unity reference
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(3.5,0,3.10))
    lpt=bpy.context.active_object; lpt.name="BLL_LightPoint"
    lpt["unity_note"]="PointLight White – 20m range, intensity 4.0, revolving"
    link(col,lpt); lpt.parent=root

    for o in objs: o.parent=root
    return root

# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
def create_buoys():
    clear_scene()
    col = new_col("IsleTrial_Buoys")

    mat_red    = build_paint_mat("Mat_Buoy_Red_Paint",   (0.80,0.13,0.00,1), 0.60)
    mat_green  = build_paint_mat("Mat_Buoy_Green_Paint", (0.00,0.53,0.16,1), 0.60)
    mat_orange = build_paint_mat("Mat_Buoy_Orange",      (1.00,0.40,0.00,1), 0.55)
    mat_white  = build_paint_mat("Mat_Buoy_White_Paint", (0.85,0.85,0.85,1), 0.60)
    mat_iron   = build_iron_rusty_mat()
    mat_barn   = build_barnacle_mat()
    mat_r_light= build_light_mat("Mat_Buoy_Light_Red",   (1.0,0.13,0.0,1), 3.0)
    mat_g_light= build_light_mat("Mat_Buoy_Light_Green", (0.0,1.0,0.2,1), 3.0)
    mat_w_light= build_light_mat("Mat_Buoy_Light_White", (1.0,1.0,1.0,1), 4.0)
    mat_glass  = build_glass_mat()

    # Build 3 buoys
    red   = build_red_buoy(col, mat_red, mat_iron, mat_barn, mat_r_light, mat_glass)
    green = build_green_buoy(col, mat_green, mat_iron, mat_barn, mat_g_light, mat_glass)
    large = build_large_buoy(col, mat_orange, mat_white, mat_iron, mat_w_light, mat_glass)

    # Modifiers – Bevel on all mesh objects
    for obj in col.all_objects:
        if obj.type=='MESH' and obj.modifiers.get('Bevel') is None:
            bev=obj.modifiers.new('Bevel','BEVEL')
            bev.width=0.003; bev.segments=2

    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            for region in area.regions:
                if region.type=='WINDOW':
                    with bpy.context.temp_override(area=area,region=region):
                        bpy.ops.view3d.view_all(center=True)
                    break

    print("Buoy waterline Y position: 0.0 — set this as water surface in Unity")
    print("✓ IsleTrial_Buoys collection ready – 3 buoys: Red (left), Green (centre), Large (right)")

create_buoys()
