"""
IsleTrial – Kraken Blade  (23_Weapon_KrakenBlade.py)
======================================================
A 1.0 m short-sword forged from Kraken chitin.  The blade
has a wavy serrated edge with bioluminescent ink channels,
a tentacle-coil cross-guard with sucker rings, a barnacle-
studded knuckle-duster guard, deep-sea pearl pommel, rope-
and-tendon grip, and glowing sucker pads along the flat.
Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

rng = random.Random(0xE0CAFE)

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
def build_chitin_blade_mat():
    mat = bpy.data.materials.new("KB_Chitin")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(950,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(700,0)
    bsdf.inputs['Roughness'].default_value=0.28
    bsdf.inputs['Metallic'].default_value =0.45
    bsdf.inputs['Specular IOR Level'].default_value=0.88
    # deep ocean colour with iridescent tint
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-550,150)
    noise.inputs['Scale'].default_value   =18.0
    noise.inputs['Detail'].default_value  =10.0
    noise.inputs['Roughness'].default_value=0.55
    cr1  = ns.new('ShaderNodeValToRGB'); cr1.location=(-300,150)
    cr1.color_ramp.elements[0].position=0.0; cr1.color_ramp.elements[0].color=(0.02,0.06,0.18,1)
    cr1.color_ramp.elements[1].position=1.0; cr1.color_ramp.elements[1].color=(0.08,0.28,0.42,1)
    # bio-ink vein channels (wave texture)
    wave = ns.new('ShaderNodeTexWave'); wave.location=(-550,-50)
    wave.wave_type='BANDS'; wave.bands_direction='Z'
    wave.inputs['Scale'].default_value=55.0
    wave.inputs['Distortion'].default_value=1.2
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location=(-300,-50)
    cr2.color_ramp.elements[0].position=0.48; cr2.color_ramp.elements[0].color=(0,0,0,0)
    cr2.color_ramp.elements[1].position=0.55; cr2.color_ramp.elements[1].color=(0.2,0.9,0.8,1)
    emit = ns.new('ShaderNodeEmission'); emit.location=(-100,-50)
    emit.inputs['Strength'].default_value=1.8
    mix_col= ns.new('ShaderNodeMixRGB'); mix_col.blend_type='ADD'; mix_col.location=(-50,100)
    mix_col.inputs['Fac'].default_value=0.35
    img_a= img_slot(ns,"[UNITY] KB_Chitin_Albedo",-600,-250)
    img_n= img_slot(ns,"[UNITY] KB_Chitin_Normal",-600,-450)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(450,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'],   cr1.inputs['Fac'])
    lk.new(wave.outputs['Fac'],    cr2.inputs['Fac'])
    lk.new(cr2.outputs['Color'],   emit.inputs['Color'])
    lk.new(cr1.outputs['Color'],   mix_col.inputs['Color1'])
    lk.new(emit.outputs['Emission'],mix_col.inputs['Color2'])
    lk.new(mix_col.outputs['Color'],mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_tentacle_mat():
    mat = bpy.data.materials.new("KB_Tentacle")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(550,0)
    bsdf.inputs['Roughness'].default_value=0.68
    bsdf.inputs['Metallic'].default_value =0.0
    bsdf.inputs['Subsurface Weight'].default_value=0.15
    bsdf.inputs['Subsurface Radius'].default_value=(0.3,0.5,0.8)
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-400,100)
    noise.inputs['Scale'].default_value=22.0
    noise.inputs['Detail'].default_value=8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.04,0.10,0.22,1)
    cr.color_ramp.elements[1].position=1.0; cr.color_ramp.elements[1].color=(0.12,0.30,0.45,1)
    img_a= img_slot(ns,"[UNITY] KB_Tentacle_Albedo",-450,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(300,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'], mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_sucker_glow_mat():
    mat = bpy.data.materials.new("KB_SuckerGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    mat.blend_method='BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(400,0)
    bsdf.inputs['Base Color'].default_value      =(0.15,0.90,0.80,1)
    bsdf.inputs['Roughness'].default_value       =0.05
    bsdf.inputs['Alpha'].default_value           =0.70
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,200)
    emit.inputs['Color'].default_value    =(0.1,1.0,0.85,1)
    emit.inputs['Strength'].default_value =3.0
    mix  = ns.new('ShaderNodeMixShader'); mix.location=(600,100)
    mix.inputs['Fac'].default_value=0.6
    lk.new(bsdf.outputs['BSDF'],    mix.inputs[1])
    lk.new(emit.outputs['Emission'], mix.inputs[2])
    lk.new(mix.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_barnacle_mat():
    mat = bpy.data.materials.new("KB_Barnacle")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Roughness'].default_value=0.90
    vor  = ns.new('ShaderNodeTexVoronoi'); vor.location=(-350,100)
    vor.inputs['Scale'].default_value=20.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-100,100)
    cr.color_ramp.elements[0].color=(0.42,0.38,0.32,1)
    cr.color_ramp.elements[1].color=(0.68,0.62,0.54,1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location=(250,150)
    bmp.inputs['Strength'].default_value=0.7
    lk.new(vor.outputs['Distance'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    bsdf.inputs['Base Color'])
    lk.new(vor.outputs['Distance'],bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_rope_mat():
    mat = bpy.data.materials.new("KB_Rope")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Roughness'].default_value=0.88
    wave = ns.new('ShaderNodeTexWave'); wave.location=(-400,100)
    wave.inputs['Scale'].default_value=28.0
    wave.inputs['Distortion'].default_value=1.5
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,100)
    cr.color_ramp.elements[0].color=(0.32,0.22,0.10,1)
    cr.color_ramp.elements[1].color=(0.58,0.44,0.22,1)
    lk.new(wave.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_pearl_mat():
    mat = bpy.data.materials.new("KB_Pearl")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value=(0.88,0.88,0.92,1)
    bsdf.inputs['Roughness'].default_value =0.08
    bsdf.inputs['Metallic'].default_value  =0.15
    bsdf.inputs['Sheen Weight'].default_value=0.6
    bsdf.inputs['Specular IOR Level'].default_value=1.0
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

# ─────────────────────────────────────────────────────────────────────
# BMesh builders
# ─────────────────────────────────────────────────────────────────────
def bm_kraken_blade(name, length=0.62):
    """Wavy serrated Kraken chitin blade with ink channel grooves."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=40; sides=6
    for i in range(segs+1):
        t=i/segs; z=t*length
        # width tapers to tip
        w=0.044*(1-t**0.8)
        # wavy serrated edge – sinusoidal
        wave_x=0.006*math.sin(t*math.pi*12)*(1-t)
        th=0.010*(1-t*0.6)
        # fuller groove depth
        fg=th*0.20*math.sin(t*math.pi)
        # 6-profile cross-section
        bm.verts.new(( w+wave_x,  0, z))
        bm.verts.new(( w*0.3,  th/2-fg, z))
        bm.verts.new((-w*0.3,  th/2-fg, z))
        bm.verts.new((-w-wave_x,  0, z))
        bm.verts.new((-w*0.3, -th/2+fg, z))
        bm.verts.new(( w*0.3, -th/2+fg, z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    tip=bm.verts.new((0,0,length+0.035))
    for j in range(sides):
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],tip])
    bot=bm.verts.new((0,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_sucker_pad(name, loc, r=0.014, depth=0.008):
    """Single sucker disc (concave cup) on blade flat."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides=10
    for j in range(sides):
        a=j*2*math.pi/sides
        bm.verts.new((r*math.cos(a),r*math.sin(a), 0.0))
    # concave centre
    ctr=bm.verts.new((0,0,-depth))
    bm.verts.ensure_lookup_table()
    for j in range(sides):
        bm.faces.new([bm.verts[j],bm.verts[(j+1)%sides],ctr])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def bm_tentacle_coil(name, loc=(0,0,0), r=0.100, turns=1.4, thick=0.018):
    """Coiled tentacle segment forming the cross-guard."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    pts=int(turns*32); sides=7
    for i in range(pts+1):
        t=i/pts
        angle=t*turns*2*math.pi
        # spiral radius decreases toward tip
        sr=r*(1-t*0.25)
        cx=sr*math.cos(angle); cy=sr*math.sin(angle)
        cz=(t-0.5)*0.045  # slight vertical sweep
        rv=thick*(0.6+0.4*math.cos(t*math.pi))
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((cx+rv*math.cos(a),cy+rv*math.sin(a),cz))
    bm.verts.ensure_lookup_table()
    for i in range(pts):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bm.to_mesh(me); bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    mod = ob.modifiers.new('Sub','SUBSURF'); mod.levels=1; mod.render_levels=2
    return ob

def bm_sucker_ring(name, loc, major_r=0.012, minor_r=0.004):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_r, minor_radius=minor_r,
        major_segments=12, minor_segments=5, location=loc)
    ob = bpy.context.active_object
    ob.name = ob.data.name = name
    return ob

def bm_barnacle_cluster(name, loc, count=4):
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    for _ in range(count):
        cx=rng.uniform(-0.025,0.025); cy=rng.uniform(-0.025,0.025)
        r=rng.uniform(0.008,0.018); h=rng.uniform(0.012,0.025); segs=6
        for j in range(segs):
            a=j*2*math.pi/segs
            bm.verts.new((cx+r*math.cos(a),cy+r*math.sin(a),0))
        bm.verts.ensure_lookup_table()
        base=len(bm.verts)-segs
        tip=bm.verts.new((cx,cy,h))
        rh =bm.verts.new((cx,cy,h*0.28))
        for j in range(segs):
            bm.faces.new([bm.verts[base+j],bm.verts[base+(j+1)%segs],rh])
        for j in range(segs):
            bm.faces.new([rh,bm.verts[base+(j+1)%segs],bm.verts[base+j],tip])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_knuckle_guard(name, loc=(0,0,0)):
    """D-guard knuckle bow, barnacle-encrusted."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    pts=18; r=0.075; tube_r=0.015
    for i in range(pts+1):
        t=i/pts; angle=t*math.pi
        cx=-r*math.cos(angle); cy=0; cz=-r*math.sin(angle)-0.02
        for j in range(8):
            a=j*2*math.pi/8
            bm.verts.new((cx+tube_r*math.cos(a),cy+tube_r*math.sin(a),cz))
    bm.verts.ensure_lookup_table()
    sides=8
    for i in range(pts):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_rope_grip(name, loc=(0,0,0), length=0.18, r=0.022):
    """Rope-wrapped grip segment."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=28; sides=8; turns=5
    for i in range(segs+1):
        t=i/segs; z=loc[2]+t*length
        twist=t*turns*2*math.pi
        rv=r*(1+0.06*math.sin(t*math.pi*turns*2))
        for j in range(sides):
            a=j*2*math.pi/sides+twist
            bm.verts.new((rv*math.cos(a),rv*math.sin(a),z))
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
    ob.name=ob.data.name=name
    return ob

def bm_pearl_pommel(name, loc=(0,0,0), r=0.035):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=9,
                                          radius=r, location=loc)
    ob = bpy.context.active_object
    ob.name=ob.data.name=name
    return ob

def bm_tentacle_tip(name, loc, length=0.08, r=0.012, rot=(0,0,0)):
    """Curling tentacle tip ornament."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs=12; sides=6
    for i in range(segs+1):
        t=i/segs
        angle=t*math.pi*1.2
        cx=t*length; cz=length*0.3*math.sin(angle)
        rv=r*(1-t)**0.5
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((cx+rv*math.cos(a),rv*math.sin(a),cz))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_ricasso_block(name, loc=(0,0,0), w=0.048, h=0.08, th=0.014):
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    vs=[bm.verts.new(c) for c in [
        (-w,-th,0),(w,-th,0),(w,th,0),(-w,th,0),
        (-w,-th,h),(w,-th,h),(w,th,h),(-w,th,h)]]
    bm.faces.new([vs[0],vs[1],vs[2],vs[3]])
    bm.faces.new([vs[4],vs[7],vs[6],vs[5]])
    for q in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        bm.faces.new([vs[q[0]],vs[q[1]],vs[q[2]],vs[q[3]]])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

# ─────────────────────────────────────────────────────────────────────
# Main creation function
# ─────────────────────────────────────────────────────────────────────
def create_kraken_blade():
    clear_scene()
    col = new_col("IsleTrial_KrakenBlade")

    mat_chitin   = build_chitin_blade_mat()
    mat_tentacle = build_tentacle_mat()
    mat_sucker   = build_sucker_glow_mat()
    mat_barnacle = build_barnacle_mat()
    mat_rope     = build_rope_mat()
    mat_pearl    = build_pearl_mat()

    objs = []

    # ── Root ───────────────────────────────────────────────────────
    bpy.ops.object.empty_add(type='ARROWS', location=(0,0,0))
    root = bpy.context.active_object
    root.name = "KrakenBlade_ROOT"
    link(col, root)

    # ── BLADE ──────────────────────────────────────────────────────
    blade = bm_kraken_blade("KB_Blade", length=0.62)
    blade.location=(0,0,0.08)
    assign_mat(blade, mat_chitin)
    smart_uv(blade)
    link(col, blade); objs.append(blade)

    # ── RICASSO block ───────────────────────────────────────────────
    ricasso = bm_ricasso_block("KB_Ricasso", loc=(0,0,0.08), w=0.044, h=0.08, th=0.012)
    assign_mat(ricasso, mat_chitin)
    smart_uv(ricasso)
    link(col, ricasso); objs.append(ricasso)

    # ── BIOLUMINESCENT SUCKER PADS on blade flat ────────────────────
    sucker_data = [
        (0.026, 0.007, 0.22), (-0.026,-0.007, 0.22),
        (0.022, 0.007, 0.34), (-0.022,-0.007, 0.34),
        (0.018, 0.006, 0.46), (-0.018,-0.006, 0.46),
        (0.014, 0.005, 0.56), (-0.014,-0.005, 0.56),
        (0.010, 0.004, 0.62), (-0.010,-0.004, 0.62),
    ]
    for si, (sx,sy,sz) in enumerate(sucker_data):
        sp = bm_sucker_pad(f"KB_Sucker_{si}", loc=(sx,sy,sz), r=0.012, depth=0.006)
        assign_mat(sp, mat_sucker)
        smart_uv(sp)
        link(col, sp); objs.append(sp)

    # ── TENTACLE COIL CROSS-GUARD ───────────────────────────────────
    coil_L = bm_tentacle_coil("KB_CoilL", loc=(0, 0, 0.08),
                               r=0.095, turns=1.25, thick=0.018)
    assign_mat(coil_L, mat_tentacle)
    smart_uv(coil_L)
    link(col, coil_L); objs.append(coil_L)

    coil_R = bm_tentacle_coil("KB_CoilR", loc=(0, 0, 0.08),
                               r=0.095, turns=1.25, thick=0.018)
    coil_R.rotation_euler=(0, 0, math.pi)
    assign_mat(coil_R, mat_tentacle)
    smart_uv(coil_R)
    link(col, coil_R); objs.append(coil_R)

    # ── SUCKER RINGS on coil tentacles ─────────────────────────────
    coil_sucker_locs = [
        ( 0.082,0,0.08),(-0.082,0,0.08),
        ( 0.070,0.040,0.09),(-0.070,-0.040,0.09),
        ( 0.050,0.078,0.07),(-0.050,-0.078,0.07),
        ( 0.088,0.020,0.06),(-0.088,-0.020,0.06),
    ]
    for ri, rloc in enumerate(coil_sucker_locs):
        sr = bm_sucker_ring(f"KB_CoilSucker_{ri}", loc=rloc, major_r=0.013, minor_r=0.004)
        assign_mat(sr, mat_sucker)
        smart_uv(sr)
        link(col, sr); objs.append(sr)

    # ── TENTACLE TIPS curling off guard ────────────────────────────
    tip_data = [
        ((0.105, 0, 0.08), (0,-0.5,0)),
        ((-0.105, 0, 0.08), (0, 0.5, math.pi)),
        ((0, 0.095, 0.085), (0.5,0,math.pi/2)),
        ((0,-0.095, 0.085), (-0.5,0,-math.pi/2)),
    ]
    for ti, (tloc, trot) in enumerate(tip_data):
        tt = bm_tentacle_tip(f"KB_TentacleTip_{ti}", loc=tloc, length=0.08, r=0.010, rot=trot)
        assign_mat(tt, mat_tentacle)
        smart_uv(tt)
        link(col, tt); objs.append(tt)

    # ── KNUCKLE D-GUARD ─────────────────────────────────────────────
    knuckle = bm_knuckle_guard("KB_KnuckleGuard", loc=(0,0,0.02))
    assign_mat(knuckle, mat_tentacle)
    smart_uv(knuckle)
    link(col, knuckle); objs.append(knuckle)

    # ── BARNACLE CLUSTERS on guard & knuckle ───────────────────────
    barnacle_positions = [
        (0.08, 0, 0.07), (-0.08, 0, 0.07),
        (0, 0.08, 0.04), (0,-0.08, 0.04),
        (0.06,-0.06,-0.04), (-0.06,0.06,-0.04),
    ]
    for bi, bpos in enumerate(barnacle_positions):
        bc = bm_barnacle_cluster(f"KB_Barnacle_{bi}", loc=bpos, count=rng.randint(3,6))
        assign_mat(bc, mat_barnacle)
        smart_uv(bc)
        link(col, bc); objs.append(bc)

    # ── ROPE-AND-TENDON GRIP ────────────────────────────────────────
    grip = bm_rope_grip("KB_Grip", loc=(0,0,-0.20), length=0.20, r=0.022)
    assign_mat(grip, mat_rope)
    smart_uv(grip)
    link(col, grip); objs.append(grip)

    # ── TENDON BINDING BAND ─────────────────────────────────────────
    for bi, bz in enumerate([-0.04, -0.14]):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.028, minor_radius=0.006,
                                          major_segments=14, minor_segments=5,
                                          location=(0,0,bz))
        band = bpy.context.active_object
        band.name = band.data.name = f"KB_GripBand_{bi}"
        assign_mat(band, mat_tentacle)
        smart_uv(band)
        link(col, band); objs.append(band)

    # ── DEEP-SEA PEARL POMMEL ───────────────────────────────────────
    pommel = bm_pearl_pommel("KB_Pommel", loc=(0,0,-0.24), r=0.036)
    assign_mat(pommel, mat_pearl)
    smart_uv(pommel)
    link(col, pommel); objs.append(pommel)

    # Tiny tentacle wrap on pommel
    bpy.ops.mesh.primitive_torus_add(major_radius=0.036, minor_radius=0.010,
                                      major_segments=16, minor_segments=5,
                                      location=(0,0,-0.24))
    pom_wrap = bpy.context.active_object
    pom_wrap.name = pom_wrap.data.name = "KB_PommelWrap"
    assign_mat(pom_wrap, mat_tentacle)
    smart_uv(pom_wrap)
    link(col, pom_wrap); objs.append(pom_wrap)

    # ── BLADE EDGE SERRATION DETAIL ─────────────────────────────────
    for si in range(8):
        t=(si+0.5)/8
        z=0.10+t*0.48
        w=0.044*(1-t**0.8)
        tooth = bm_tentacle_tip(f"KB_Serration_{si}",
                                 loc=(w+0.004, 0, z),
                                 length=0.016, r=0.004,
                                 rot=(0, math.pi/2, 0))
        assign_mat(tooth, mat_chitin)
        smart_uv(tooth)
        link(col, tooth); objs.append(tooth)

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
    bpy.ops.object.empty_add(type='SINGLE_ARROW', location=(0,0,0.72))
    tip_pt = bpy.context.active_object
    tip_pt.name = "KB_BladePoint"
    tip_pt["unity_note"] = "Blade tip – damage ray origin"
    tip_pt.parent = root; link(col, tip_pt)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,-0.10))
    grip_pt = bpy.context.active_object
    grip_pt.name = "KB_GripPoint"
    grip_pt["unity_note"] = "Right Hand grip attach point"
    grip_pt.parent = root; link(col, grip_pt)

    bpy.ops.object.empty_add(type='SPHERE', location=(0, 0.06, 0.08))
    guard_vfx = bpy.context.active_object
    guard_vfx.name = "KB_GuardInkVFX"
    guard_vfx["unity_note"] = "Ink particle / bioluminescence VFX"
    guard_vfx.parent = root; link(col, guard_vfx)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_all(center=True)
                    break

    print("✓ Kraken Blade created – IsleTrial_KrakenBlade collection ready for FBX export.")

create_kraken_blade()
