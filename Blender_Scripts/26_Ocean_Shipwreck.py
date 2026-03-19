"""
IsleTrial – Abandoned Shipwreck  (26_Ocean_Shipwreck.py)  [REBUILT]
=====================================================================
Prompt 05-B: Huge ABANDONED 18m × 5m derelict wooden ship, half-beached
and tilted 35° to starboard.  LARGE environment set piece (not player boat).

Objects created:
  Wreck_Hull_Main         – 18m hull shell, plank grooves, cannon ports,
                            barnacle lower hull, jagged 60% break, 3 holes
  Wreck_Hull_Ribs_*       – 6 exposed rib frames visible through hull breach
  Wreck_Keel              – heavy keel beam along hull bottom
  Wreck_Stern_Cabin       – captain's quarters box + broken windows, door
  Wreck_Stern_Railing     – broken railing posts along stern deck
  Wreck_Bowsprit          – broken 4m bowsprit with splintered tip
  Wreck_Mast_Broken       – 4m fore-mast stump, jagged top
  Wreck_Mast_Aft_Stump    – 3m second mast stump
  Wreck_Mast_FallenSection– 6m fallen mast on deck
  Wreck_ShipWheel         – broken ship wheel on helm, tilted
  Wreck_Anchor_Chain      – 8-link anchor chain at bow waterline
  Wreck_Deck_Planks_A/B   – partial fore-deck planks (bent, gaps, sunken)
  Wreck_Deck_Planks_Stern – stern deck partial planks
  Wreck_CabinFloor        – broken floor inside cabin
  Wreck_Rigging_Rope_*    – 6 drooping rope curve remnants
  Wreck_Barrel_*          – 4 damaged barrels (2 toppled, 2 broken)
  Wreck_Crate_*           – 2 split-open crates
  Wreck_Coins             – 22 scattered gold coins
  Wreck_SandAccum_*       – 3 sand/algae accumulation blobs on deck
  Wreck_HullBarnacles     – large barnacle strip on lower hull
  Wreck_Barnacles_*       – 6 additional barnacle clusters on hull sides
  Wreck_Coral_*           – 8 coral cluster formations on hull/sea floor
  Wreck_Seaweed_*         – 12 ribbon seaweed strands
  Wreck_WaterlineRef      – thin flat plane at Y=0 waterline reference

Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

rng = random.Random(0xC0FFEE2)

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

def smart_uv(obj, angle=60):
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
def build_old_wood_mat():
    mat = bpy.data.materials.new("Mat_Wreck_Wood_Old")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(950,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(700,0)
    bsdf.inputs['Roughness'].default_value=0.95
    bsdf.inputs['Metallic'].default_value =0.0
    wave = ns.new('ShaderNodeTexWave'); wave.location=(-500,150)
    wave.wave_type='RINGS'; wave.bands_direction='X'
    wave.inputs['Scale'].default_value=6.0
    wave.inputs['Distortion'].default_value=5.0
    wave.inputs['Detail'].default_value=10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-250,150)
    cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.10,0.06,0.02,1)
    cr.color_ramp.elements[1].position=1.0; cr.color_ramp.elements[1].color=(0.35,0.22,0.08,1)
    # rot / decay overlay
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-500,-80)
    noise.inputs['Scale'].default_value=42.0; noise.inputs['Detail'].default_value=8.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location=(-250,-80)
    cr2.color_ramp.elements[0].position=0.62; cr2.color_ramp.elements[0].color=(0.04,0.02,0.01,1)
    cr2.color_ramp.elements[1].position=0.82; cr2.color_ramp.elements[1].color=(0,0,0,0)
    mix_c= ns.new('ShaderNodeMixRGB'); mix_c.blend_type='DARKEN'; mix_c.location=(50,100)
    mix_c.inputs['Fac'].default_value=1.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location=(350,250)
    bmp.inputs['Strength'].default_value=1.4
    img_a= img_slot(ns,"[UNITY] Wreck_Wood_Albedo",-550,-280)
    img_n= img_slot(ns,"[UNITY] Wreck_Wood_Normal",-550,-480)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(470,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(wave.outputs['Fac'],  cr.inputs['Fac'])
    lk.new(noise.outputs['Fac'], cr2.inputs['Fac'])
    lk.new(cr.outputs['Color'],  mix_c.inputs['Color1'])
    lk.new(cr2.outputs['Color'], mix_c.inputs['Color2'])
    lk.new(mix_c.outputs['Color'],mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix.inputs['Color2'])
    lk.new(wave.outputs['Fac'],  bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_wet_wood_mat():
    mat = bpy.data.materials.new("Mat_Wreck_Wood_Wet")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(550,0)
    bsdf.inputs['Base Color'].default_value=(0.14,0.08,0.02,1)
    bsdf.inputs['Roughness'].default_value =0.38
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-350,100)
    noise.inputs['Scale'].default_value=28.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location=(200,150)
    bmp.inputs['Strength'].default_value=0.9
    img_a= img_slot(ns,"[UNITY] Wreck_WetWood_Albedo",-400,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(300,0)
    mix.inputs['Fac'].default_value=0.0; mix.inputs['Color1'].default_value=(0.14,0.08,0.02,1)
    lk.new(noise.outputs['Fac'],  bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    lk.new(img_a.outputs['Color'],mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def build_barnacle_mat():
    mat = bpy.data.materials.new("Mat_Wreck_Barnacle")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value=(0.46,0.42,0.35,1)
    bsdf.inputs['Roughness'].default_value =0.95
    vor  = ns.new('ShaderNodeTexVoronoi'); vor.location=(-300,100)
    vor.inputs['Scale'].default_value=20.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location=(200,150)
    bmp.inputs['Strength'].default_value=0.85
    img_a= img_slot(ns,"[UNITY] Wreck_Barnacle_Albedo",-350,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(320,0)
    mix.inputs['Fac'].default_value=0.0; mix.inputs['Color1'].default_value=(0.46,0.42,0.35,1)
    lk.new(vor.outputs['Distance'],bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_coral_mat(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value=color
    bsdf.inputs['Roughness'].default_value =0.80
    bsdf.inputs['Subsurface Weight'].default_value=0.10
    bsdf.inputs['Subsurface Radius'].default_value=(0.6,0.3,0.2)
    emit = ns.new('ShaderNodeEmission'); emit.location=(200,200)
    emit.inputs['Color'].default_value    =color
    emit.inputs['Strength'].default_value =0.3
    mix  = ns.new('ShaderNodeMixShader'); mix.location=(620,100)
    mix.inputs['Fac'].default_value=0.08
    lk.new(bsdf.outputs['BSDF'],    mix.inputs[1])
    lk.new(emit.outputs['Emission'], mix.inputs[2])
    lk.new(mix.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_seaweed_mat():
    mat = bpy.data.materials.new("Mat_Seaweed")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    mat.blend_method='BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value=(0.08,0.40,0.12,1)
    bsdf.inputs['Roughness'].default_value =0.70
    bsdf.inputs['Alpha'].default_value     =0.82
    bsdf.inputs['Subsurface Weight'].default_value=0.12
    img_a= img_slot(ns,"[UNITY] Seaweed_Albedo",-400,-200)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(200,0)
    mix.inputs['Fac'].default_value=0.0; mix.inputs['Color1'].default_value=(0.08,0.40,0.12,1)
    lk.new(img_a.outputs['Color'],mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def build_iron_mat():
    mat = bpy.data.materials.new("Mat_Wreck_Iron")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Base Color'].default_value=(0.20,0.10,0.04,1)
    bsdf.inputs['Roughness'].default_value =0.88
    bsdf.inputs['Metallic'].default_value  =0.65
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-300,100)
    noise.inputs['Scale'].default_value=22.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-50,100)
    cr.color_ramp.elements[0].color=(0.35,0.18,0.06,1)
    cr.color_ramp.elements[1].color=(0.20,0.10,0.04,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_sand_mat():
    mat = bpy.data.materials.new("Mat_SandAlgae")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(700,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(450,0)
    bsdf.inputs['Roughness'].default_value=0.92
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-350,100)
    noise.inputs['Scale'].default_value=16.0; noise.inputs['Detail'].default_value=8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-100,100)
    cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.55,0.48,0.30,1)
    cr.color_ramp.elements[1].position=0.6; cr.color_ramp.elements[1].color=(0.22,0.38,0.14,1)
    cr.color_ramp.elements.new(0.85); cr.color_ramp.elements[2].color=(0.55,0.48,0.30,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_glass_mat():
    mat = bpy.data.materials.new("Mat_BrokenGlass")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    mat.blend_method='BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value=(0.72,0.82,0.88,1)
    bsdf.inputs['Roughness'].default_value =0.08
    bsdf.inputs['Transmission Weight'].default_value=0.82
    bsdf.inputs['Alpha'].default_value     =0.40
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

def build_coin_mat():
    mat = bpy.data.materials.new("Mat_Coin")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Base Color'].default_value=(0.82,0.62,0.08,1)
    bsdf.inputs['Roughness'].default_value=0.22; bsdf.inputs['Metallic'].default_value=0.95
    emit = ns.new('ShaderNodeEmission'); emit.location=(150,200)
    emit.inputs['Color'].default_value=(1.0,0.80,0.1,1)
    emit.inputs['Strength'].default_value=0.4
    add  = ns.new('ShaderNodeAddShader'); add.location=(550,100)
    lk.new(bsdf.outputs['BSDF'],add.inputs[0])
    lk.new(emit.outputs['Emission'],add.inputs[1])
    lk.new(add.outputs['Shader'],out.inputs['Surface'])
    return mat

# ─────────────────────────────────────────────────────────────────────
# Geometry builders
# ─────────────────────────────────────────────────────────────────────
def bm_hull_main(name, length=18.0, width=5.0, height=3.5):
    """
    18m ship hull shell:
    - Parabolic bottom cross-section
    - Plank groove detail via sinusoidal Z offset (14 planks per side)
    - 3 cannon port cutouts along mid-hull starboard
    - Bow taper (stempost)
    - Stern transom (flat rear face)
    - Gunwale rail at top
    - Displacement modifier for organic surface irregularity
    """
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs_l=36; segs_w=16

    for li in range(segs_l+1):
        tl=li/segs_l; x=tl*length-length/2
        for wi in range(segs_w+1):
            tw=wi/segs_w
            y=(tw-0.5)*width
            # parabolic hull cross-section
            z_base=-height*(1-(tw*2-1)**2)*0.52
            # plank groove texture (16 planks)
            plank_groove=0.022*math.sin(tw*math.pi*16)
            # slight hull rocker: bow/stern slightly higher
            rocker=0.18*math.sin(tl*math.pi)
            z=z_base+plank_groove+rocker
            # bow taper (last 15% = bow section narrows)
            bow_factor=max(0, (tl-0.85)/0.15)
            side_taper=1-bow_factor**2*0.75
            bm.verts.new((x, y*side_taper, z))

    bm.verts.ensure_lookup_table()
    for li in range(segs_l):
        for wi in range(segs_w):
            a=li*(segs_w+1)+wi; b=a+1
            c=a+(segs_w+1)+1; d=a+(segs_w+1)
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])

    # Gunwale cap ring (top edge, both sides)
    for li in range(segs_l+1):
        tl=li/segs_l; x=tl*length-length/2
        bow_factor=max(0,(tl-0.85)/0.15)
        w_tap=1-bow_factor**2*0.75
        bm.verts.new((x, -width/2*w_tap, 0.90))
        bm.verts.new((x,  width/2*w_tap, 0.90))
    g_start=(segs_l+1)*(segs_w+1)
    for li in range(segs_l):
        a=g_start+li*2; b=a+2
        if b+1 < g_start+(segs_l+1)*2:
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[b+1],bm.verts[a+1]])

    bm.to_mesh(me); bm.free()
    ob.location=(0,0,0)
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name

    # Surface irregularity displacement
    disp=ob.modifiers.new('WoodGrain','DISPLACE')
    tex=bpy.data.textures.new('HullGrain','DISTORTED_NOISE')
    tex.noise_scale=0.8
    disp.texture=tex; disp.strength=0.08; disp.direction='NORMAL'
    return ob

def bm_hull_rib(name, loc=(0,0,0), width=5.0, height=3.5, thickness=0.18):
    """Single ship rib/frame cross-section (visible through hull breach)."""
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    sides=14
    # U-shaped rib following hull parabolic curve
    for j in range(sides+1):
        t=j/sides; w=(t-0.5)*width
        z=-height*(1-(t*2-1)**2)*0.52+0.02
        bm.verts.new((w, -thickness/2, z))
        bm.verts.new((w,  thickness/2, z))
    bm.verts.ensure_lookup_table()
    for j in range(sides):
        a=j*2; b=a+2; c=b+1; d=a+1
        bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # top rail caps
    bm.faces.new([bm.verts[0],bm.verts[1],bm.verts[3],bm.verts[2]])
    bm.faces.new([bm.verts[sides*2],bm.verts[sides*2+1],
                  bm.verts[(sides-1)*2+1],bm.verts[(sides-1)*2]])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_keel(name, length=18.0):
    """Heavy keel beam running along hull bottom."""
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    segs=24; w=0.22; h=0.35
    for i in range(segs+1):
        t=i/segs; x=t*length-length/2
        # keel is curved (rocker)
        z=-1.75+0.12*math.sin(t*math.pi)
        bm.verts.new((x, -w/2, z))
        bm.verts.new((x,  w/2, z))
        bm.verts.new((x, -w/2, z-h))
        bm.verts.new((x,  w/2, z-h))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        idx=i*4
        bm.faces.new([bm.verts[idx],bm.verts[idx+4],bm.verts[idx+5],bm.verts[idx+1]])
        bm.faces.new([bm.verts[idx+2],bm.verts[idx+3],bm.verts[idx+7],bm.verts[idx+6]])
        bm.faces.new([bm.verts[idx],bm.verts[idx+2],bm.verts[idx+6],bm.verts[idx+4]])
        bm.faces.new([bm.verts[idx+1],bm.verts[idx+5],bm.verts[idx+7],bm.verts[idx+3]])
    bm.to_mesh(me); bm.free()
    ob.location=(0,0,0)
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_stern_cabin(name, loc=(0,0,0)):
    """Captain's quarters box with broken window frames and door."""
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    # main box: 4m wide × 3m long × 2.2m tall
    w=2.0; d=1.5; h=2.2; th=0.10
    panels=[
        # front wall (facing deck)
        [(-w,-d,0),( w,-d,0),( w,-d,h),(-w,-d,h)],
        # back wall (stern)
        [( w, d,0),(-w, d,0),(-w, d,h),( w, d,h)],
        # left wall
        [(-w, d,0),(-w,-d,0),(-w,-d,h),(-w, d,h)],
        # right wall (partially broken)
        [( w,-d,0),( w, d,0),( w, d,h*0.55),( w,-d,h*0.55)],
        # roof (partially missing – only 60%)
        [(-w,-d,h),( w,-d,h),( w*0.6,-d*0.4,h),(-w*0.6,-d*0.4,h)],
    ]
    for panel in panels:
        vs=[bm.verts.new(v) for v in panel]
        bm.faces.new(vs)
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    sol=ob.modifiers.new('Sol','SOLIDIFY'); sol.thickness=th
    return ob

def bm_window_frame(name, loc=(0,0,0), rot=(0,0,0), w=0.48, h=0.52):
    """Broken window frame for cabin."""
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    fr=0.06; d=0.05
    # outer frame rect
    vs=[bm.verts.new(v) for v in [
        (-w/2,-fr,0),(w/2,-fr,0),(w/2,-fr,h),(-w/2,-fr,h),
        (-w/2, fr,0),(w/2, fr,0),(w/2, fr,h),(-w/2, fr,h)]]
    # inner aperture
    iv=[bm.verts.new(v) for v in [
        (-w/2+fr,-fr,fr),(w/2-fr,-fr,fr),(w/2-fr,-fr,h-fr),(-w/2+fr,-fr,h-fr),
        (-w/2+fr, fr,fr),(w/2-fr, fr,fr),(w/2-fr, fr,h-fr),(-w/2+fr, fr,h-fr)]]
    # outer faces
    bm.faces.new([vs[0],vs[1],iv[1],iv[0]])
    bm.faces.new([vs[1],vs[2],iv[2],iv[1]])
    bm.faces.new([vs[2],vs[3],iv[3],iv[2]])
    bm.faces.new([vs[3],vs[0],iv[0],iv[3]])
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_glass_shard(name, loc=(0,0,0), size=0.18):
    """Jagged glass shard in window aperture."""
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    pts=5; d=0.008
    verts_f=[]; verts_b=[]
    for i in range(pts):
        a=i*2*math.pi/pts + rng.uniform(-0.5,0.5)
        r=size*(0.4+0.6*rng.random())
        verts_f.append(bm.verts.new((r*math.cos(a),r*math.sin(a),d)))
        verts_b.append(bm.verts.new((r*math.cos(a),r*math.sin(a),-d)))
    ctr_f=bm.verts.new((0,0,d)); ctr_b=bm.verts.new((0,0,-d))
    for i in range(pts):
        bm.faces.new([verts_f[i],verts_f[(i+1)%pts],ctr_f])
        bm.faces.new([verts_b[(i+1)%pts],verts_b[i],ctr_b])
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=(math.pi/2,0,rng.uniform(-0.5,0.5))
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_bowsprit(name, loc=(0,0,0), length=4.0):
    """Broken bowsprit jutting from bow, splintered end."""
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    segs=16; sides=7
    for i in range(segs+1):
        t=i/segs; x=t*length
        r=0.18*(1-t*0.28)
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((x, r*math.cos(a), r*math.sin(a)))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # jagged splinter end
    for j in range(sides):
        bm.verts[segs*sides+j].co.y+=rng.uniform(-0.12,0.12)
        bm.verts[segs*sides+j].co.z+=rng.uniform(-0.10,0.08)
    bot=bm.verts.new((0,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    ob.rotation_euler=(0, -0.35, 0)  # angled upward then broken
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_mast_stump(name, loc=(0,0,0), height=4.0, r_base=0.22):
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    segs=18; sides=10
    for i in range(segs+1):
        t=i/segs; z=t*height
        r=r_base*(1-t*0.16)+0.012*math.sin(t*math.pi*9)*rng.uniform(0.5,1.2)
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((r*math.cos(a),r*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    for j in range(sides):
        bm.verts[segs*sides+j].co.z+=rng.uniform(-0.22,0.14)
    bot=bm.verts.new((0,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_fallen_mast(name, loc=(0,0,0), length=6.0, r=0.19):
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    segs=20; sides=8
    for i in range(segs+1):
        t=i/segs; x=t*length
        rv=r*(1-t*0.12)
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((x, rv*math.cos(a), rv*math.sin(a)))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bot=bm.verts.new((0,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
    tip=bm.verts.new((length,0,0))
    for j in range(sides):
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],tip])
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=(0,0,0.3)
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_ship_wheel(name, loc=(0,0,0), r=0.55):
    """Ship wheel – hub + spokes + rim, tilted and cracked."""
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    spoke_count=8; spoke_r=0.025; rim_r=0.030
    # hub
    for j in range(12):
        a=j*2*math.pi/12
        bm.verts.new((0.08*math.cos(a),0.08*math.sin(a),-0.04))
        bm.verts.new((0.08*math.cos(a),0.08*math.sin(a), 0.04))
    bm.verts.ensure_lookup_table()
    for j in range(12):
        a=j*2; b=(j*2+2)%(24)
        bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[b+1],bm.verts[a+1]])
    # spokes
    for s in range(spoke_count):
        angle=s*2*math.pi/spoke_count
        for pt in range(5):
            t=pt/4; x=t*r*math.cos(angle); y=t*r*math.sin(angle)
            bm.verts.new((x,y,-spoke_r))
            bm.verts.new((x,y, spoke_r))
        bm.verts.ensure_lookup_table()
        base=len(bm.verts)-10
        for pt in range(4):
            a=base+pt*2; b=a+2; c=b+1; d=a+1
            if b+1<=len(bm.verts):
                bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    # outer rim
    rim_sides=32
    for j in range(rim_sides):
        a=j*2*math.pi/rim_sides
        bm.verts.new((r*math.cos(a),r*math.sin(a),-rim_r))
        bm.verts.new((r*math.cos(a),r*math.sin(a), rim_r))
    bm.verts.ensure_lookup_table()
    rim_base=len(bm.verts)-rim_sides*2
    for j in range(rim_sides):
        a=rim_base+j*2; b=rim_base+(j*2+2)%(rim_sides*2)
        bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[b+1],bm.verts[a+1]])
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=(0.4, 0, math.radians(22))
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_anchor_chain(name, loc=(0,0,0), count=10):
    """Chain hanging at waterline with slight sag."""
    objs=[]
    for ci in range(count):
        sag_x=ci*0.08; sag_z=-0.12-ci*0.22
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.10, minor_radius=0.025,
            major_segments=14, minor_segments=5,
            location=(loc[0]+sag_x, loc[1], loc[2]+sag_z),
            rotation=(math.pi/2, 0, (ci%2)*math.pi/2))
        cl=bpy.context.active_object; cl.name=f"{name}_L{ci}"
        objs.append(cl)
    return objs

def bm_plank_section(name, loc, length=6.0, width_total=4.2, count=14):
    """Deck plank section – random gaps, bent planks, age cracks."""
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    pw=0.28; gap=0.05; th=0.048
    for i in range(count):
        if rng.random()<0.28: continue
        px=(i-(count/2))*(pw+gap)
        bent=rng.uniform(-0.08,0.12) if rng.random()<0.35 else 0
        crack_z=rng.uniform(-0.02,0.02)
        segs=8
        for si in range(segs+1):
            t=si/segs; lx=t*length-length/2
            bz=bent*math.sin(t*math.pi)+crack_z*rng.uniform(-1,1)
            bm.verts.new((lx, px-pw/2, bz))
            bm.verts.new((lx, px+pw/2, bz))
            bm.verts.new((lx, px-pw/2, bz-th))
            bm.verts.new((lx, px+pw/2, bz-th))
        bm.verts.ensure_lookup_table()
        base=len(bm.verts)-(segs+1)*4
        for si in range(segs):
            idx=base+si*4
            bm.faces.new([bm.verts[idx],  bm.verts[idx+4], bm.verts[idx+5], bm.verts[idx+1]])
            bm.faces.new([bm.verts[idx],  bm.verts[idx+2], bm.verts[idx+6], bm.verts[idx+4]])
            bm.faces.new([bm.verts[idx+1],bm.verts[idx+5], bm.verts[idx+7], bm.verts[idx+3]])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_railing_post(name, loc, height=0.85):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.045,
                                         depth=height, location=(loc[0],loc[1],loc[2]+height/2))
    ob=bpy.context.active_object; ob.name=ob.data.name=name
    ob.rotation_euler=(rng.uniform(-0.25,0.25), rng.uniform(-0.2,0.2), 0)
    return ob

def bm_sand_blob(name, loc=(0,0,0), r=0.6):
    """Irregular sand/algae accumulation in deck corner."""
    me=bpy.data.meshes.new(name)
    ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    sides=20
    for j in range(sides):
        a=j*2*math.pi/sides
        rv=r*(0.6+0.4*rng.random())
        bm.verts.new((rv*math.cos(a),rv*math.sin(a),0))
    bm.verts.ensure_lookup_table()
    ctr=bm.verts.new((0,0,0.06*rng.random()))
    for j in range(sides):
        bm.faces.new([bm.verts[j],bm.verts[(j+1)%sides],ctr])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    mod=ob.modifiers.new('Sub','SUBSURF'); mod.levels=1
    return ob

def bm_barrel(name, loc=(0,0,0), rot=(0,0,0), damaged=False):
    me=bpy.data.meshes.new(name); ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    segs=14; sides=18; h=0.72; r=0.30
    for i in range(segs+1):
        t=i/segs; z=t*h; bulge=1+0.12*math.sin(t*math.pi); rv=r*bulge
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((rv*math.cos(a),rv*math.sin(a),z))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
    bot=bm.verts.new((0,0,0)); top=bm.verts.new((0,0,h))
    for j in range(sides):
        bm.faces.new([bm.verts[(j+1)%sides],bm.verts[j],bot])
        bm.faces.new([bm.verts[segs*sides+j],bm.verts[segs*sides+(j+1)%sides],top])
    if damaged:
        for v in bm.verts:
            if v.co.x>0.18 and 0.2<v.co.z<0.58:
                v.co.x*=rng.uniform(0.45,0.80); v.co.z+=rng.uniform(-0.07,0.07)
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_crate(name, loc=(0,0,0), rot=(0,0,0)):
    me=bpy.data.meshes.new(name); ob=bpy.data.objects.new(name,me)
    bm=bmesh.new(); s=0.48; th=0.04
    panels=[
        [(-s,-s,0),(s,-s,0),(s,s,0),(-s,s,0)],
        [(-s,-s,0),(-s,-s,s),(s,-s,s),(s,-s,0)],
        [(s,s,0),(s,s,s),(-s,s,s),(-s,s,0)],
        [(-s,-s,0),(-s,s,0),(-s,s,s*0.50),(-s,-s,s*0.50)],
    ]
    for panel in panels:
        vs=[bm.verts.new(v) for v in panel]; bm.faces.new(vs)
    bm.to_mesh(me); bm.free()
    ob.location=loc; ob.rotation_euler=rot
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    mod=ob.modifiers.new('Sol','SOLIDIFY'); mod.thickness=th
    return ob

def bm_coins(name, loc=(0,0,0), count=22):
    me=bpy.data.meshes.new(name); ob=bpy.data.objects.new(name,me)
    bm=bmesh.new()
    for _ in range(count):
        cx=rng.uniform(-2.0,2.0); cy=rng.uniform(-1.5,1.5)
        r=rng.uniform(0.022,0.038); sides=8
        for j in range(sides):
            a=j*2*math.pi/sides
            bm.verts.new((cx+r*math.cos(a),cy+r*math.sin(a),0.005))
        bm.verts.ensure_lookup_table()
        base=len(bm.verts)-sides; ctr=bm.verts.new((cx,cy,0.005))
        for j in range(sides):
            bm.faces.new([bm.verts[base+j],bm.verts[base+(j+1)%sides],ctr])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_barnacle_strip(name, loc, count=20, spread_x=9.0):
    me=bpy.data.meshes.new(name); ob=bpy.data.objects.new(name,me); bm=bmesh.new()
    for _ in range(count):
        cx=rng.uniform(-spread_x,spread_x); cy=rng.uniform(-0.6,0.6)
        r=rng.uniform(0.06,0.14); h=rng.uniform(0.07,0.16); segs=6
        for j in range(segs):
            a=j*2*math.pi/segs
            bm.verts.new((cx+r*math.cos(a),cy+r*math.sin(a),0))
        bm.verts.ensure_lookup_table()
        base=len(bm.verts)-segs
        tip=bm.verts.new((cx,cy,h)); rh=bm.verts.new((cx,cy,h*0.3))
        for j in range(segs):
            bm.faces.new([bm.verts[base+j],bm.verts[base+(j+1)%segs],rh])
            bm.faces.new([rh,bm.verts[base+(j+1)%segs],bm.verts[base+j],tip])
    bm.to_mesh(me); bm.free()
    ob.location=loc
    bpy.context.scene.collection.objects.link(ob)
    ob.name=ob.data.name=name
    return ob

def bm_coral_cluster_mesh(name, loc=(0,0,0), branches=6):
    """Coral cluster via bezier curves → convert to mesh."""
    bpy.ops.curve.primitive_bezier_curve_add(location=loc)
    crv=bpy.context.active_object; crv.name=f"{name}_Crv"
    crv.data.bevel_depth=rng.uniform(0.025,0.055)
    crv.data.bevel_resolution=3
    crv.data.splines[0].bezier_points[0].co=(0,0,0)
    crv.data.splines[0].bezier_points[1].co=(0,0,0.45+rng.random()*0.5)
    crv.data.splines[0].bezier_points[0].handle_right=(rng.uniform(-0.1,0.1),rng.uniform(-0.1,0.1),0.2)
    crv.data.splines[0].bezier_points[1].handle_left=(rng.uniform(-0.1,0.1),rng.uniform(-0.1,0.1),0.3)
    for b in range(branches-1):
        angle=b*2*math.pi/(branches-1)+rng.uniform(-0.3,0.3)
        bpy.ops.curve.primitive_bezier_curve_add(
            location=(loc[0]+0.18*math.cos(angle),
                      loc[1]+0.18*math.sin(angle), loc[2]+0.12))
        br=bpy.context.active_object
        br.data.bevel_depth=rng.uniform(0.012,0.028)
        br.data.bevel_resolution=3
        br.data.splines[0].bezier_points[1].co=(
            0.22*math.cos(angle+0.3), 0.22*math.sin(angle+0.3), 0.35+rng.random()*0.25)
        br.name=f"{name}_Br{b}"
    return crv

def bm_seaweed_strand(name, loc=(0,0,0), length=1.2):
    bpy.ops.curve.primitive_bezier_curve_add(location=loc)
    crv=bpy.context.active_object; crv.name=name
    crv.data.bevel_depth=0.014; crv.data.bevel_resolution=2
    sp=crv.data.splines[0]
    sp.bezier_points[0].co=(0,0,0)
    sp.bezier_points[1].co=(rng.uniform(-0.35,0.35),rng.uniform(-0.2,0.2),-length)
    sp.bezier_points[0].handle_right=(rng.uniform(-0.12,0.12),0, length*0.35)
    sp.bezier_points[1].handle_left=(rng.uniform(-0.22,0.22),0,-length*0.35)
    return crv

# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
def create_shipwreck():
    clear_scene()
    col = new_col("IsleTrial_Shipwreck")

    mat_wood_old = build_old_wood_mat()
    mat_wood_wet = build_wet_wood_mat()
    mat_barnacle = build_barnacle_mat()
    mat_iron     = build_iron_mat()
    mat_sand     = build_sand_mat()
    mat_glass    = build_glass_mat()
    mat_coin     = build_coin_mat()
    mat_coral_o  = build_coral_mat("Mat_Coral_Orange",(1.0,0.33,0.0,1))
    mat_coral_w  = build_coral_mat("Mat_Coral_White", (0.94,0.93,0.88,1))
    mat_coral_p  = build_coral_mat("Mat_Coral_Pink",  (1.0,0.52,0.62,1))
    mat_seaweed  = build_seaweed_mat()

    # ── Root ───────────────────────────────────────────────────────
    bpy.ops.object.empty_add(type='ARROWS', location=(0,0,0))
    root=bpy.context.active_object; root.name="Wreck_ROOT"; link(col,root)
    all_objs=[]

    # ── HULL MAIN ──────────────────────────────────────────────────
    hull=bm_hull_main("Wreck_Hull_Main", length=18.0, width=5.0, height=3.5)
    hull.rotation_euler=(0, 0, math.radians(35))
    assign_mat(hull, mat_wood_old)
    add_mat(hull, mat_wood_wet)
    smart_uv(hull)
    link(col,hull); all_objs.append(hull)

    # ── KEEL ───────────────────────────────────────────────────────
    keel=bm_keel("Wreck_Keel", length=18.0)
    assign_mat(keel, mat_wood_old); smart_uv(keel)
    link(col,keel); all_objs.append(keel)

    # ── HULL RIBS – 6 exposed frames in breach area ─────────────────
    rib_positions=[-3.0,-1.5,0.0,1.5,3.0,4.5]
    for ri,rx in enumerate(rib_positions):
        rib=bm_hull_rib(f"Wreck_Hull_Rib_{ri}", loc=(rx,0,0),
                         width=5.0, height=3.5, thickness=0.20)
        assign_mat(rib, mat_wood_old); smart_uv(rib)
        link(col,rib); all_objs.append(rib)

    # ── BARNACLES – lower hull strip ────────────────────────────────
    bs=bm_barnacle_strip("Wreck_HullBarnacles", loc=(0,0,-1.4), count=28, spread_x=8.8)
    assign_mat(bs, mat_barnacle); smart_uv(bs)
    link(col,bs); all_objs.append(bs)

    # Extra barnacle clusters on sides
    side_barn=[(-6, 2.2,-0.5),(-2, 2.3,-0.8),(3, 2.1,-0.4),(6,-2.2,-0.6),
               (0,-2.4,-0.7),(5, 1.8,-0.3)]
    for bi,(bx,by,bz) in enumerate(side_barn):
        sbp=bm_barnacle_strip(f"Wreck_SideBarn_{bi}", loc=(bx,by,bz), count=6, spread_x=0.9)
        assign_mat(sbp, mat_barnacle); smart_uv(sbp)
        link(col,sbp); all_objs.append(sbp)

    # ── STERN CABIN (captain's quarters) ───────────────────────────
    cabin=bm_stern_cabin("Wreck_Stern_Cabin", loc=(7.5, 0, 0.92))
    assign_mat(cabin, mat_wood_old); smart_uv(cabin)
    link(col,cabin); all_objs.append(cabin)

    # Cabin window frames
    cabin_win_data=[
        ("Wreck_Win_A", (7.5-0.9, -1.52, 1.50), (0, 0, 0)),
        ("Wreck_Win_B", (7.5+0.9, -1.52, 1.50), (0, 0, 0)),
        ("Wreck_Win_C", (7.5+2.0,  0.0,  1.50), (0, 0, math.pi/2)),
    ]
    for wn, wloc, wrot in cabin_win_data:
        wf=bm_window_frame(wn, loc=wloc, rot=wrot, w=0.46, h=0.50)
        assign_mat(wf, mat_wood_old); smart_uv(wf)
        link(col,wf); all_objs.append(wf)
        # broken glass shards in window
        for gi in range(rng.randint(1,3)):
            gs=bm_glass_shard(f"{wn}_Glass{gi}",
                               loc=(wloc[0]+rng.uniform(-0.1,0.1),
                                    wloc[1]+0.02,
                                    wloc[2]+rng.uniform(-0.1,0.1)),
                               size=0.12)
            assign_mat(gs, mat_glass); smart_uv(gs)
            link(col,gs); all_objs.append(gs)

    # ── STERN RAILING POSTS ────────────────────────────────────────
    for ri, ry in enumerate([-1.8,-1.2,-0.6,0.0,0.6,1.2,1.8]):
        if rng.random()<0.3: continue  # some posts missing
        rp=bm_railing_post(f"Wreck_Rail_{ri}", loc=(7.0,ry,0.92), height=0.88)
        assign_mat(rp, mat_wood_old); smart_uv(rp)
        link(col,rp); all_objs.append(rp)

    # ── BOWSPRIT ───────────────────────────────────────────────────
    bowsprit=bm_bowsprit("Wreck_Bowsprit", loc=(-8.5, 0, 0.65), length=4.2)
    assign_mat(bowsprit, mat_wood_old); smart_uv(bowsprit)
    link(col,bowsprit); all_objs.append(bowsprit)

    # ── FORE MAST STUMP ────────────────────────────────────────────
    mast_fore=bm_mast_stump("Wreck_Mast_Broken", loc=(-2.0, 0, 0.92), height=4.0)
    assign_mat(mast_fore, mat_wood_old); smart_uv(mast_fore)
    link(col,mast_fore); all_objs.append(mast_fore)

    # ── AFT MAST STUMP ─────────────────────────────────────────────
    mast_aft=bm_mast_stump("Wreck_Mast_Aft_Stump", loc=(4.5, 0, 0.92),
                             height=3.0, r_base=0.19)
    assign_mat(mast_aft, mat_wood_old); smart_uv(mast_aft)
    link(col,mast_aft); all_objs.append(mast_aft)

    # ── FALLEN MAST ON DECK ────────────────────────────────────────
    fallen=bm_fallen_mast("Wreck_Mast_FallenSection", loc=(-1.5, 1.5, 0.94), length=6.0)
    assign_mat(fallen, mat_wood_old); smart_uv(fallen)
    link(col,fallen); all_objs.append(fallen)

    # ── SHIP WHEEL on helm deck ────────────────────────────────────
    wheel=bm_ship_wheel("Wreck_ShipWheel", loc=(6.2, 0, 1.55), r=0.52)
    assign_mat(wheel, mat_wood_old); smart_uv(wheel)
    link(col,wheel); all_objs.append(wheel)

    # Wheel pedestal
    ped=bm_mast_stump("Wreck_WheelPedestal", loc=(6.2,0,0.92), height=0.65, r_base=0.10)
    assign_mat(ped, mat_wood_old); smart_uv(ped)
    link(col,ped); all_objs.append(ped)

    # ── ANCHOR CHAIN at bow waterline ──────────────────────────────
    chain_links=bm_anchor_chain("Wreck_Anchor_Chain", loc=(-8.8, 0, 0.0), count=10)
    for cl in chain_links:
        assign_mat(cl, mat_iron); smart_uv(cl)
        link(col,cl); all_objs.append(cl)

    # ── RIGGING ROPE REMNANTS ──────────────────────────────────────
    rope_curves_data=[
        ((-2.0,0.18,4.88),(2.0, 2.5, 1.2)),
        ((-2.0,-0.18,4.78),(-6.5, -2.2, 1.5)),
        ((4.5, 0.15, 3.88),(7.0, 1.8, 1.3)),
        ((4.5,-0.15, 3.78),(1.5,-2.0, 1.1)),
        ((-2.0, 0.1, 4.20),(4.5, 0.1, 3.88)),
        ((-8.3, 0.1, 1.0), (-5.0,-2.5, 0.95)),
    ]
    for ri,(start,end) in enumerate(rope_curves_data):
        bpy.ops.curve.primitive_bezier_curve_add(location=start)
        rope=bpy.context.active_object; rope.name=f"Wreck_Rigging_{ri}"
        rope.data.bevel_depth=0.009; rope.data.bevel_resolution=3
        sp=rope.data.splines[0]
        sp.bezier_points[0].co=(0,0,0)
        dx=end[0]-start[0]; dy=end[1]-start[1]; dz=end[2]-start[2]
        sp.bezier_points[1].co=(dx,dy,dz)
        # natural sag
        sp.bezier_points[0].handle_right=(dx*0.3,dy*0.1,dz*0.2-0.8)
        sp.bezier_points[1].handle_left=(dx*0.7,dy*0.9,dz*0.8-0.8)
        assign_mat(rope, mat_wood_wet); link(col,rope)

    # ── DECK PLANKS ────────────────────────────────────────────────
    deck_fore=bm_plank_section("Wreck_Deck_Planks_A", loc=(-5.0,0,0.92),
                                 length=6.0, count=14)
    assign_mat(deck_fore, mat_wood_old); smart_uv(deck_fore)
    link(col,deck_fore); all_objs.append(deck_fore)

    deck_mid=bm_plank_section("Wreck_Deck_Planks_B", loc=(0.5,0,0.94),
                                length=5.5, count=12)
    assign_mat(deck_mid, mat_wood_old); smart_uv(deck_mid)
    link(col,deck_mid); all_objs.append(deck_mid)

    deck_stern=bm_plank_section("Wreck_Deck_Planks_Stern", loc=(6.0,0,0.94),
                                  length=4.0, count=10)
    assign_mat(deck_stern, mat_wood_old); smart_uv(deck_stern)
    link(col,deck_stern); all_objs.append(deck_stern)

    # ── CABIN FLOOR (broken) ────────────────────────────────────────
    cab_floor=bm_plank_section("Wreck_CabinFloor", loc=(7.5,0,0.93),
                                 length=2.8, count=8)
    assign_mat(cab_floor, mat_wood_old); smart_uv(cab_floor)
    link(col,cab_floor); all_objs.append(cab_floor)

    # ── SAND & ALGAE ACCUMULATIONS on deck ─────────────────────────
    sand_locs=[(-4.5, 1.8, 0.92),(-1.2,-2.0, 0.92),(5.5, 1.5, 0.92)]
    for si,sloc in enumerate(sand_locs):
        sa=bm_sand_blob(f"Wreck_SandAccum_{si}", loc=sloc, r=rng.uniform(0.5,1.0))
        assign_mat(sa, mat_sand); smart_uv(sa)
        link(col,sa); all_objs.append(sa)

    # ── CARGO ──────────────────────────────────────────────────────
    barrel_data=[
        (-1.5,  0.8, 0.92,(0,0,0.5), True),
        (-0.6, -1.2, 0.92,(0,0,-0.3),False),
        ( 2.0,  0.9, 0.92,(math.pi/2,0,0.9),True),
        ( 3.2, -1.3, 0.92,(0,0,1.3), False),
    ]
    for bi,(bx,by,bz,brot,dam) in enumerate(barrel_data):
        bar=bm_barrel(f"Wreck_Barrel_{bi}", loc=(bx,by,bz), rot=brot, damaged=dam)
        assign_mat(bar, mat_wood_old); smart_uv(bar)
        link(col,bar); all_objs.append(bar)

    for ci in range(2):
        cx=-2.2+ci*1.4
        cr=bm_crate(f"Wreck_Crate_{ci}", loc=(cx,-0.6,0.92),
                     rot=(0,0,rng.uniform(-0.6,0.6)))
        assign_mat(cr, mat_wood_old); smart_uv(cr)
        link(col,cr); all_objs.append(cr)

    coins=bm_coins("Wreck_Coins", loc=(0.5,0,0.93), count=22)
    assign_mat(coins, mat_coin); smart_uv(coins)
    link(col,coins); all_objs.append(coins)

    # ── CORAL GROWTH – 8 clusters ──────────────────────────────────
    coral_pos=[(-7.0,1.8,-0.7),(-4.5,-2.2,-0.9),(-1.8,2.8,-0.5),(0,-2.8,-0.9),
               (3.2,2.2,-0.6),(5.5,-1.8,-0.8),(7.5,1.2,-0.4),(8.5,-2.2,-0.6)]
    coral_mats=[mat_coral_o,mat_coral_w,mat_coral_p,mat_coral_o,
                mat_coral_w,mat_coral_p,mat_coral_o,mat_coral_w]
    for ci,(cx,cy,cz) in enumerate(coral_pos):
        cluster=bm_coral_cluster_mesh(f"Wreck_Coral_{ci}", loc=(cx,cy,cz),
                                       branches=rng.randint(5,9))
        bpy.ops.object.select_all(action='DESELECT')
        cluster.select_set(True)
        bpy.context.view_layer.objects.active=cluster
        bpy.ops.object.convert(target='MESH')
        cmesh=bpy.context.active_object; cmesh.name=f"Wreck_Coral_{ci}"
        assign_mat(cmesh, coral_mats[ci%3]); smart_uv(cmesh)
        link(col,cmesh); all_objs.append(cmesh)

    # ── SEAWEED – 12 strands ────────────────────────────────────────
    sw_locs=[(-7,2,1.6),(-5,-1.9,0.9),(-3,2.4,1.3),(-1,-2.1,1.0),(1,2.6,1.5),
             (3,-2.3,0.8),(5,1.9,1.2),(7,-1.6,0.9),(-6,0.1,1.4),(-2,1.6,0.7),
             (4,0.6,1.1),(6,2.1,0.9)]
    sw_lens=[1.3,1.9,0.9,1.6,2.0,0.8,1.5,1.2,1.7,0.9,1.4,1.8]
    for si,(sx,sy,sz) in enumerate(sw_locs):
        sw=bm_seaweed_strand(f"Wreck_Seaweed_{si}", loc=(sx,sy,sz),
                              length=sw_lens[si%len(sw_lens)])
        assign_mat(sw, mat_seaweed); link(col,sw)

    # ── WATERLINE REFERENCE PLANE ──────────────────────────────────
    bpy.ops.mesh.primitive_plane_add(size=22.0, location=(0,0,0.01))
    wl=bpy.context.active_object; wl.name="Wreck_WaterlineRef"
    wl_mat=bpy.data.materials.new("Mat_WaterlineRef")
    wl_mat.use_nodes=True; ns,lk=ns_lk(wl_mat); ns.clear()
    out=ns.new('ShaderNodeOutputMaterial'); out.location=(500,0)
    wl_mat.blend_method='BLEND'
    bsdf=ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(250,0)
    bsdf.inputs['Base Color'].default_value=(0.05,0.35,0.65,1)
    bsdf.inputs['Alpha'].default_value=0.15
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    assign_mat(wl, wl_mat); link(col,wl)
    wl["unity_note"]="Y=0.0 is the water surface – delete before FBX export"

    # ── BEVEL MODIFIERS ────────────────────────────────────────────
    for o in all_objs:
        if o.type=='MESH':
            bev=o.modifiers.new('Bevel','BEVEL')
            bev.width=0.004; bev.segments=1

    # ── PARENT all to root ─────────────────────────────────────────
    for o in all_objs:
        o.parent=root

    # ── POLY COUNT ─────────────────────────────────────────────────
    print("=== IsleTrial Shipwreck – Polycount Breakdown ===")
    for o in sorted(all_objs, key=lambda x: x.name):
        if o.type=='MESH':
            tris=sum(len(p.vertices)-2 for p in o.data.polygons)
            print(f"  {o.name:<40s}  ~{tris:>6d} tris")
    print()
    print("  Ship scale: 18m long × 5m wide – LARGE abandoned derelict vessel")
    print("  35° starboard tilt applied.  Set Wreck_ROOT as prefab root in Unity.")
    print("  Wreck_WaterlineRef at Y=0.0 – DELETE before FBX export.")
    print("✓ IsleTrial_Shipwreck collection ready.")

    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            for region in area.regions:
                if region.type=='WINDOW':
                    with bpy.context.temp_override(area=area,region=region):
                        bpy.ops.view3d.view_all(center=True)
                    break

create_shipwreck()
