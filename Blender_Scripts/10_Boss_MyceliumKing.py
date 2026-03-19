"""
IsleTrial – Boss 01: Mycelium King  (FULL REBUILD – MAXIMUM DETAIL)
====================================================================
Height  ~4.0 m  Colossal fungal overlord.
Theme   Enormous mushroom-capped humanoid body fused with decaying
        organic matter. Mycelium veins pulse across skin. Four arms
        — 2 massive club arms + 2 smaller spore-cannon arms.
        Ground beneath him erupts with root tendrils.

Mesh Objects Built:
  BODY
    MK_Body_Core        – bmesh 32×22 torso barrel (bulging gut, hump)
    MK_Body_InfectionVeins_* – 18 raised vein ridges across torso
    MK_Neck             – thick fungal neck cylinder
    MK_Gut_Bulge        – bloated lower belly sphere
    MK_BackHump         – dorsal mycelium growth hump

  HEAD
    MK_Head             – bmesh 28×20 rounded skull
    MK_CompoundEye_*    – 12 individual compound eye spheres (hexagonal cluster)
    MK_Jaw_Upper/Lower  – gaping jaw plates
    MK_Teeth_*          – 10 jagged upper + 10 lower teeth (irregular sizes)
    MK_Tongue           – thick forked tongue
    MK_NoseSlit_L/R     – sunken nostril slits
    MK_FaceDecay_*      – 6 decaying flesh patches where mushrooms break through

  MUSHROOM CAP
    MK_MushroomCap      – bmesh bell-curve cap (2.8 m diameter)
    MK_CapGills_*       – 24 underside gill plate strips
    MK_CapSpots_*       – 16 raised white cap spots
    MK_CapRing          – partial veil ring below cap
    MK_CapEdgeDrip_*    – 12 dripping slime filaments from cap rim

  ARMS (×4)
    MK_ArmUpper_*/MK_ArmLower_* – club arms (left pair) + spore arms (right pair)
    MK_Elbow_*/MK_Wrist_*  – joint spheres with mushroom growth
    MK_Fist_*/MK_Knuckle_* – club fist + sharp knuckle spikes
    MK_SporeCannon_L/R  – barrel + targeting ring + ammo drum

  LEGS
    MK_Thigh_*/MK_Shin_*/MK_Foot_* – thick pillar legs, wide fungal feet

  SCARY ATTACHMENTS
    MK_InfectedSkull_*  – 5 impaled victim skulls on shoulder spikes
    MK_ShoulderSpike_*  – 8 massive bone spikes erupting from shoulders
    MK_RootTendril_*    – 10 mycelium root tentacles erupting from ground
    MK_SporeSac_*       – 6 pulsating hanging spore pod sacs
    MK_BoneFragment_*   – 12 bone shards partially fused into torso skin
    MK_SporeCloud_*     – 4 floating spore burst spheres around body
    MK_InfectionDrip_*  – 8 dripping green infection rivulets on body

Materials (full dual-path procedural + [UNITY] image slots):
  Mat_MK_Flesh        – mottled grey-green putrid skin + Voronoi sores
  Mat_MK_Mushroom     – deep crimson cap + Musgrave mottling + spots
  Mat_MK_Vein         – bioluminescent green-yellow emissive veins
  Mat_MK_Spore        – pale dusty spore powder + wave diffusion
  Mat_MK_Bone         – aged ivory + SSS + fine noise cracks
  Mat_MK_Slime        – translucent toxic green slime
  Mat_MK_Eye          – compound black faceted eye
  Mat_MK_InfGlow      – infection glow (emissive pulsing green)

Run BEFORE 10_Boss_MyceliumKing_Rig.py
"""

import bpy, bmesh, math, random
from mathutils import Vector

rng = random.Random(42)

# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)

def new_col(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c); return c

def link(col, obj):
    for ex in list(obj.users_collection): ex.objects.unlink(obj)
    col.objects.link(obj)

def add_sub(obj, lv=2):
    m = obj.modifiers.new('Sub','SUBSURF'); m.levels=lv; m.render_levels=lv

def add_bevel(obj, w=0.015, s=2):
    m = obj.modifiers.new('Bev','BEVEL'); m.width=w; m.segments=s; m.profile=0.5

def add_solidify(obj, t=0.04):
    m = obj.modifiers.new('Solid','SOLIDIFY'); m.thickness=t; m.offset=0.0

def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj; obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT'); obj.select_set(False)

def prim(tp, name, loc=(0,0,0), rot=(0,0,0), size=1.0, **kw):
    if tp=='sphere':  bpy.ops.mesh.primitive_uv_sphere_add(radius=size,location=loc,rotation=rot,segments=kw.get('segs',22),ring_count=kw.get('rings',14))
    elif tp=='cyl':   bpy.ops.mesh.primitive_cylinder_add(radius=size,depth=kw.get('depth',1.0),location=loc,rotation=rot,vertices=kw.get('verts',16))
    elif tp=='cone':  bpy.ops.mesh.primitive_cone_add(radius1=kw.get('r1',size),radius2=kw.get('r2',0),depth=kw.get('depth',1.0),location=loc,rotation=rot,vertices=kw.get('verts',8))
    elif tp=='cube':  bpy.ops.mesh.primitive_cube_add(size=size,location=loc,rotation=rot)
    elif tp=='torus': bpy.ops.mesh.primitive_torus_add(major_radius=kw.get('major',size),minor_radius=kw.get('minor',0.06),location=loc,rotation=rot,major_segments=kw.get('maj_seg',24),minor_segments=kw.get('min_seg',8))
    obj = bpy.context.active_object; obj.name = name; return obj

def assign_mat(obj, mat):
    if obj.data.materials: obj.data.materials[0] = mat
    else: obj.data.materials.append(mat)

def seg_obj(name, p1, p2, radius, mat, col, verts=10):
    d = Vector(p2)-Vector(p1); mid = Vector(p1)+d*0.5
    obj = prim('cyl', name, loc=mid, size=radius, depth=d.length, verts=verts)
    obj.rotation_euler = d.to_track_quat('Z','Y').to_euler()
    assign_mat(obj, mat); smart_uv(obj); link(col, obj); return obj

# ═══════════════════════════════════════════════════════════════════
#  MATERIALS
# ═══════════════════════════════════════════════════════════════════

def _n(nodes, ntype, loc, label=None):
    nd = nodes.new(ntype); nd.location = loc
    if label: nd.label = nd.name = label; return nd

def _img(nodes, sname, loc):
    nd = nodes.new('ShaderNodeTexImage'); nd.location = loc
    nd.label = nd.name = f'[UNITY] {sname}'; return nd

def _mapping(nodes, links, scale=(4,4,4), loc=(-900,0)):
    tc = _n(nodes,'ShaderNodeTexCoord',(loc[0]-200,loc[1]))
    mp = _n(nodes,'ShaderNodeMapping',loc)
    mp.inputs['Scale'].default_value = (*scale,)
    links.new(tc.outputs['UV'], mp.inputs['Vector']); return mp

def _mix_pi(nodes, links, proc, img_nd, loc):
    mix = _n(nodes,'ShaderNodeMixRGB',loc); mix.blend_type='MIX'; mix.inputs[0].default_value=0.0
    links.new(proc, mix.inputs[1]); links.new(img_nd.outputs['Color'], mix.inputs[2]); return mix

def _bump_n(nodes, links, mp, scale=20.0, strength=0.45, loc=(-400,-400)):
    bn = _n(nodes,'ShaderNodeTexNoise',loc)
    bn.inputs['Scale'].default_value=scale; bn.inputs['Detail'].default_value=10.0
    links.new(mp.outputs['Vector'], bn.inputs['Vector'])
    img_n = _img(nodes,'_NormalMap',(loc[0],loc[1]-180))
    mix_n = _mix_pi(nodes,links,bn.outputs['Fac'],img_n,(loc[0]+260,loc[1]-90))
    bmp = _n(nodes,'ShaderNodeBump',(loc[0]+480,loc[1]-90))
    bmp.inputs['Strength'].default_value=strength
    links.new(mix_n.outputs['Color'], bmp.inputs['Height']); return bmp

def _base(name):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    n=mat.node_tree.nodes; lk=mat.node_tree.links; n.clear()
    bsdf=_n(n,'ShaderNodeBsdfPrincipled',(700,0))
    out=_n(n,'ShaderNodeOutputMaterial',(1000,0))
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface']); return mat,n,lk,bsdf

def mat_flesh(name):
    mat,n,lk,bsdf = _base(name)
    mp = _mapping(n,lk,scale=(3,3,3))
    # Large mottling
    noise_big = _n(n,'ShaderNodeTexNoise',(-700,350))
    noise_big.inputs['Scale'].default_value=3.0; noise_big.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],noise_big.inputs['Vector'])
    # Sore/lesion Voronoi
    vor = _n(n,'ShaderNodeTexVoronoi',(-700,150))
    vor.inputs['Scale'].default_value=7.0; vor.feature='DISTANCE_TO_EDGE'
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    # Fine skin texture
    noise_fine = _n(n,'ShaderNodeTexNoise',(-700,-50))
    noise_fine.inputs['Scale'].default_value=22.0; noise_fine.inputs['Detail'].default_value=12.0
    lk.new(mp.outputs['Vector'],noise_fine.inputs['Vector'])
    # Infection blotch wave
    wave = _n(n,'ShaderNodeTexWave',(-700,-250)); wave.wave_type='RINGS'
    wave.inputs['Scale'].default_value=4.0; wave.inputs['Distortion'].default_value=3.5
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    # Blend: mottling * voronoi sores
    mix_mv = _n(n,'ShaderNodeMixRGB',(-400,250)); mix_mv.blend_type='MULTIPLY'; mix_mv.inputs[0].default_value=0.60
    lk.new(noise_big.outputs['Fac'],mix_mv.inputs[1]); lk.new(vor.outputs['Distance'],mix_mv.inputs[2])
    # Add fine skin detail
    mix_fs = _n(n,'ShaderNodeMixRGB',(-200,200)); mix_fs.blend_type='OVERLAY'; mix_fs.inputs[0].default_value=0.22
    lk.new(mix_mv.outputs['Color'],mix_fs.inputs[1]); lk.new(noise_fine.outputs['Fac'],mix_fs.inputs[2])
    # Infection wave blend
    mix_wi = _n(n,'ShaderNodeMixRGB',(-50,150)); mix_wi.blend_type='SCREEN'; mix_wi.inputs[0].default_value=0.15
    lk.new(mix_fs.outputs['Color'],mix_wi.inputs[1]); lk.new(wave.outputs['Color'],mix_wi.inputs[2])
    # Colour ramp: grey-green putrid flesh
    cr = _n(n,'ShaderNodeValToRGB',(180,200))
    cr.color_ramp.elements[0].color=(0.10,0.14,0.08,1)   # very dark grey-green
    e1=cr.color_ramp.elements.new(0.35); e1.color=(0.22,0.28,0.14,1)
    e2=cr.color_ramp.elements.new(0.65); e2.color=(0.32,0.38,0.18,1)
    cr.color_ramp.elements[1].color=(0.42,0.44,0.22,1)
    lk.new(mix_wi.outputs['Color'],cr.inputs['Fac'])
    img_a = _img(n,f'{name}_Albedo',(-700,-400))
    mix_c = _mix_pi(n,lk,cr.outputs['Color'],img_a,(440,120))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    # Roughness variation
    mr = _n(n,'ShaderNodeMapRange',(180,-120))
    mr.inputs['From Min'].default_value=0.2; mr.inputs['From Max'].default_value=0.8
    mr.inputs['To Min'].default_value=0.62; mr.inputs['To Max'].default_value=0.82
    lk.new(noise_fine.outputs['Fac'],mr.inputs['Value']); lk.new(mr.outputs['Result'],bsdf.inputs['Roughness'])
    bsdf.inputs['Subsurface Weight'].default_value=0.06
    bsdf.inputs['Subsurface Radius'].default_value=(0.22,0.30,0.10)
    bmp = _bump_n(n,lk,mp,scale=28.0,strength=0.48); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_mushroom_cap(name):
    mat,n,lk,bsdf = _base(name)
    mp = _mapping(n,lk,scale=(2,2,2))
    musg = _n(n,'ShaderNodeTexMusgrave',(-700,300)); musg.musgrave_type='FBM'
    musg.inputs['Scale'].default_value=5.0; musg.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],musg.inputs['Vector'])
    noise = _n(n,'ShaderNodeTexNoise',(-700,100)); noise.inputs['Scale'].default_value=12.0; noise.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    vor = _n(n,'ShaderNodeTexVoronoi',(-700,-100)); vor.inputs['Scale'].default_value=18.0
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    mix_mn = _n(n,'ShaderNodeMixRGB',(-400,200)); mix_mn.blend_type='MULTIPLY'; mix_mn.inputs[0].default_value=0.55
    lk.new(musg.outputs['Fac'],mix_mn.inputs[1]); lk.new(noise.outputs['Fac'],mix_mn.inputs[2])
    mix_mv = _n(n,'ShaderNodeMixRGB',(-200,150)); mix_mv.blend_type='OVERLAY'; mix_mv.inputs[0].default_value=0.28
    lk.new(mix_mn.outputs['Color'],mix_mv.inputs[1]); lk.new(vor.outputs['Distance'],mix_mv.inputs[2])
    cr = _n(n,'ShaderNodeValToRGB',(50,200))
    cr.color_ramp.elements[0].color=(0.28,0.02,0.02,1)   # deep crimson #720505
    e1=cr.color_ramp.elements.new(0.40); e1.color=(0.50,0.06,0.04,1)
    cr.color_ramp.elements[1].color=(0.72,0.12,0.06,1)
    lk.new(mix_mv.outputs['Color'],cr.inputs['Fac'])
    img_a = _img(n,f'{name}_Albedo',(-700,-250))
    mix_c = _mix_pi(n,lk,cr.outputs['Color'],img_a,(320,120))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.72
    bsdf.inputs['Subsurface Weight'].default_value=0.08
    bsdf.inputs['Subsurface Radius'].default_value=(0.60,0.08,0.04)
    bmp = _bump_n(n,lk,mp,scale=18.0,strength=0.55); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_vein(name):
    mat,n,lk,bsdf = _base(name)
    mp = _mapping(n,lk,scale=(6,6,6))
    wave = _n(n,'ShaderNodeTexWave',(-600,200)); wave.wave_type='BANDS'
    wave.inputs['Scale'].default_value=8.0; wave.inputs['Distortion'].default_value=4.0; wave.inputs['Detail'].default_value=6.0
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    noise = _n(n,'ShaderNodeTexNoise',(-600,0)); noise.inputs['Scale'].default_value=20.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mix_wn = _n(n,'ShaderNodeMixRGB',(-300,100)); mix_wn.blend_type='MULTIPLY'; mix_wn.inputs[0].default_value=0.50
    lk.new(wave.outputs['Color'],mix_wn.inputs[1]); lk.new(noise.outputs['Fac'],mix_wn.inputs[2])
    cr = _n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.02,0.18,0.02,1)
    cr.color_ramp.elements[1].color=(0.08,0.58,0.06,1)   # bright bioluminescent green
    lk.new(mix_wn.outputs['Color'],cr.inputs['Fac'])
    img_a = _img(n,f'{name}_Albedo',(-600,-200))
    mix_c = _mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Emission Color'].default_value=(0.04,0.70,0.04,1)
    bsdf.inputs['Emission Strength'].default_value=1.8
    bsdf.inputs['Roughness'].default_value=0.22
    return mat

def mat_spore(name):
    mat,n,lk,bsdf = _base(name)
    mp = _mapping(n,lk,scale=(8,8,8))
    noise = _n(n,'ShaderNodeTexNoise',(-500,200)); noise.inputs['Scale'].default_value=14.0; noise.inputs['Detail'].default_value=6.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    vor = _n(n,'ShaderNodeTexVoronoi',(-500,0)); vor.inputs['Scale'].default_value=24.0
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    mix_nv = _n(n,'ShaderNodeMixRGB',(-250,100)); mix_nv.blend_type='OVERLAY'; mix_nv.inputs[0].default_value=0.32
    lk.new(noise.outputs['Fac'],mix_nv.inputs[1]); lk.new(vor.outputs['Distance'],mix_nv.inputs[2])
    cr = _n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.62,0.62,0.42,1)   # dusty pale
    cr.color_ramp.elements[1].color=(0.86,0.86,0.68,1)
    lk.new(mix_nv.outputs['Color'],cr.inputs['Fac'])
    img_a = _img(n,f'{name}_Albedo',(-500,-200))
    mix_c = _mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.90
    bsdf.inputs['Transmission Weight'].default_value=0.08
    return mat

def mat_bone(name):
    mat,n,lk,bsdf = _base(name)
    mp = _mapping(n,lk,scale=(8,8,8))
    noise = _n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=18.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr = _n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.62,0.58,0.46,1)
    cr.color_ramp.elements[1].color=(0.84,0.80,0.68,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    img_a = _img(n,f'{name}_Albedo',(-400,-200))
    mix_c = _mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.62
    bsdf.inputs['Subsurface Weight'].default_value=0.04
    bsdf.inputs['Subsurface Radius'].default_value=(0.88,0.76,0.58)
    return mat

def mat_slime(name):
    mat,n,lk,bsdf = _base(name)
    mp = _mapping(n,lk,scale=(10,10,10))
    noise = _n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=16.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr = _n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.02,0.22,0.02,1)
    cr.color_ramp.elements[1].color=(0.14,0.58,0.08,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    img_a = _img(n,f'{name}_Albedo',(-400,-200))
    mix_c = _mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.06
    bsdf.inputs['Transmission Weight'].default_value=0.55
    bsdf.inputs['Alpha'].default_value=0.75; mat.blend_method='BLEND'
    bsdf.inputs['Emission Color'].default_value=(0.02,0.40,0.02,1)
    bsdf.inputs['Emission Strength'].default_value=0.60
    return mat

def mat_compound_eye(name):
    mat,n,lk,bsdf = _base(name)
    mp = _mapping(n,lk,scale=(12,12,12))
    vor = _n(n,'ShaderNodeTexVoronoi',(-400,100)); vor.inputs['Scale'].default_value=30.0; vor.feature='DISTANCE_TO_EDGE'
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    cr = _n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.02,0.04,0.02,1)
    cr.color_ramp.elements[1].color=(0.06,0.16,0.06,1)
    lk.new(vor.outputs['Distance'],cr.inputs['Fac'])
    img_a = _img(n,f'{name}_Albedo',(-400,-200))
    mix_c = _mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.04
    bsdf.inputs['Emission Color'].default_value=(0.04,0.30,0.02,1)
    bsdf.inputs['Emission Strength'].default_value=0.8
    return mat

def mat_infection_glow(name):
    mat,n,lk,bsdf = _base(name)
    noise = _n(n,'ShaderNodeTexNoise',(-300,100)); noise.inputs['Scale'].default_value=20.0
    cr = _n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.04,0.28,0.02,1)
    cr.color_ramp.elements[1].color=(0.18,0.80,0.06,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Emission Color'].default_value=(0.08,1.0,0.04,1)
    bsdf.inputs['Emission Strength'].default_value=3.0
    bsdf.inputs['Roughness'].default_value=0.80
    return mat

def build_materials():
    return {
        'flesh'   : mat_flesh('Mat_MK_Flesh'),
        'cap'     : mat_mushroom_cap('Mat_MK_Mushroom'),
        'vein'    : mat_vein('Mat_MK_Vein'),
        'spore'   : mat_spore('Mat_MK_Spore'),
        'bone'    : mat_bone('Mat_MK_Bone'),
        'slime'   : mat_slime('Mat_MK_Slime'),
        'eye'     : mat_compound_eye('Mat_MK_Eye'),
        'glow'    : mat_infection_glow('Mat_MK_InfGlow'),
    }

# ═══════════════════════════════════════════════════════════════════
#  GEOMETRY
# ═══════════════════════════════════════════════════════════════════

def build_torso(mats, col):
    """bmesh 32×22 barrel torso with bulging gut and infection veins."""
    objs = []
    bm = bmesh.new()
    segs=32; rings=22; W=0.90; H=1.30
    verts_grid=[]
    for ri in range(rings+1):
        t=ri/rings; y=-H+t*2*H
        if t<0.12:   w=W*(t/0.12)*0.55
        elif t<0.40: w=W*(0.55+(t-0.12)/0.28*0.45)
        elif t<0.60: w=W*1.0
        elif t<0.80: w=W*(1.0-(t-0.60)/0.20*0.12)  # belly bulge stays wide
        else:        w=W*(0.88-(t-0.80)/0.20*0.28)
        if t<0.15:   h=H*(t/0.15)*0.50
        elif t<0.55: h=H*(0.50+(t-0.15)/0.40*0.50)
        elif t<0.80: h=H*1.0
        else:        h=H*(1.0-(t-0.80)/0.20*0.18)
        ring=[]
        for si in range(segs):
            a=2*math.pi*si/segs
            x=w*math.cos(a); z=h*math.sin(a)
            if z<0: z*=0.88  # slight flatten bottom
            # Gut bulge at front centre
            if a<math.pi*0.4 or a>math.pi*1.6:
                belly_t=min(1.0,abs(math.cos(a))*1.2)
                if 0.35<t<0.75: x*=(1.0+belly_t*0.28)
            ring.append(bm.verts.new(Vector((x,y,z))))
        verts_grid.append(ring)
    for ri in range(rings):
        for si in range(segs):
            v0=verts_grid[ri][si]; v1=verts_grid[ri][(si+1)%segs]
            v2=verts_grid[ri+1][(si+1)%segs]; v3=verts_grid[ri+1][si]
            try: bm.faces.new([v0,v1,v2,v3])
            except: pass
    tc=bm.verts.new(Vector((0,-H,0))); hc=bm.verts.new(Vector((0,H,0)))
    for si in range(segs):
        try:
            bm.faces.new([verts_grid[0][(si+1)%segs],verts_grid[0][si],tc])
            bm.faces.new([verts_grid[-1][si],verts_grid[-1][(si+1)%segs],hc])
        except: pass
    mesh=bpy.data.meshes.new('MK_Body_Mesh'); bm.to_mesh(mesh); bm.free()
    body=bpy.data.objects.new('MK_Body_Core',mesh)
    body.location=(0,0,2.20)
    bpy.context.scene.collection.objects.link(body)
    assign_mat(body,mats['flesh']); add_sub(body,2); smart_uv(body); link(col,body); objs.append(body)

    # Neck
    neck=prim('cyl','MK_Neck',loc=(0,0,3.62),size=0.44,depth=0.48,verts=16)
    assign_mat(neck,mats['flesh']); add_sub(neck,1); smart_uv(neck); link(col,neck); objs.append(neck)

    # Gut bulge overhang sphere
    gut=prim('sphere','MK_Gut_Bulge',loc=(0.12,0,1.50),size=0.75,segs=18,rings=14)
    gut.scale=(1.0,1.0,0.72); bpy.ops.object.transform_apply(scale=True)
    assign_mat(gut,mats['flesh']); add_sub(gut,1); smart_uv(gut); link(col,gut); objs.append(gut)

    # Back hump (mycelium growth)
    hump=prim('sphere','MK_BackHump',loc=(0,-0.78,2.80),size=0.55,segs=14,rings=10)
    hump.scale=(0.88,0.68,0.80); bpy.ops.object.transform_apply(scale=True)
    assign_mat(hump,mats['cap']); add_sub(hump,1); smart_uv(hump); link(col,hump); objs.append(hump)

    # Infection vein ridges (18 raised ridges across torso)
    vein_positions=[
        (0.82,0,2.40,85),(0.72,0.40,2.60,70),(0.60,-0.50,2.20,95),
        (-0.82,0,2.40,85),(-0.72,0.40,2.60,70),(-0.60,-0.50,2.20,95),
        (0.50,0,3.10,80),(0.35,0.60,2.90,72),(-0.50,0,3.10,80),(-0.35,0.60,2.90,72),
        (0.70,0,1.80,88),(0.55,-0.40,1.60,92),(-0.70,0,1.80,88),(-0.55,-0.40,1.60,92),
        (0.30,0.80,2.50,65),(-0.30,0.80,2.50,65),(0.20,-0.88,2.40,82),(-0.20,-0.88,2.40,82),
    ]
    for i,(vx,vy,vz,vr) in enumerate(vein_positions):
        vn=prim('cyl',f'MK_InfectionVein_{i}',loc=(vx,vy,vz),size=0.022,depth=0.38,verts=6,
                rot=(0,math.radians(vr),math.radians(i*20)))
        assign_mat(vn,mats['vein']); link(col,vn); objs.append(vn)

    return objs

def build_head(mats, col):
    """bmesh head with 12 compound eyes, jaws, teeth, forked tongue."""
    objs=[]
    # Main skull
    bm=bmesh.new(); segs=28; rings=20
    for ri in range(rings+1):
        t=ri/rings; a_lat=math.pi*t
        z=0.52*math.cos(a_lat)
        r=0.48*math.sin(a_lat)
        if t<0.25: r*=(0.7+t/0.25*0.3)   # narrow brow
        if t>0.75: r*=(1.0-(t-0.75)/0.25*0.18)  # narrow chin
        ring=[]
        for si in range(segs):
            a=2*math.pi*si/segs
            ring.append(bm.verts.new(Vector((r*math.cos(a),r*math.sin(a),z))))
        if ri>0:
            prev=bm.verts[len(bm.verts)-segs*2:len(bm.verts)-segs] if ri>1 else None
        if ri==rings: bm.verts.new(Vector((0,0,-0.52)))
    bm.verts.ensure_lookup_table()
    all_v=list(bm.verts)
    for ri in range(rings):
        for si in range(segs):
            v0=all_v[ri*segs+si]; v1=all_v[ri*segs+(si+1)%segs]
            v2=all_v[(ri+1)*segs+(si+1)%segs] if (ri+1)*segs+(si+1)%segs<len(all_v)-1 else all_v[-1]
            v3=all_v[(ri+1)*segs+si] if (ri+1)*segs+si<len(all_v)-1 else all_v[-1]
            try: bm.faces.new([v0,v1,v2,v3])
            except: pass
    mesh=bpy.data.meshes.new('MK_Head_Mesh'); bm.to_mesh(mesh); bm.free()
    head=bpy.data.objects.new('MK_Head',mesh)
    head.location=(0,0,3.90); head.scale=(1.0,1.0,1.12)
    bpy.context.scene.collection.objects.link(head)
    assign_mat(head,mats['flesh']); bpy.ops.object.transform_apply(scale=True)
    add_sub(head,2); smart_uv(head); link(col,head); objs.append(head)

    # 12 compound eyes in hexagonal cluster on face
    eye_positions=[
        # Inner ring (4)
        (0.14,0.44,3.98),(-.14,0.44,3.98),(0,0.46,4.12),(0,0.42,3.84),
        # Outer ring (8)
        (0.28,0.42,4.06),(-0.28,0.42,4.06),(0.22,0.44,4.20),(-0.22,0.44,4.20),
        (0.22,0.40,3.76),(-0.22,0.40,3.76),(0.08,0.46,4.28),(-0.08,0.46,4.28),
    ]
    for i,(ex,ey,ez) in enumerate(eye_positions):
        eye=prim('sphere',f'MK_CompoundEye_{i}',loc=(ex,ey,ez),size=0.058,segs=10,rings=8)
        assign_mat(eye,mats['eye']); link(col,eye); objs.append(eye)
        # Eye socket darkening rim
        rim=prim('torus',f'MK_EyeRim_{i}',loc=(ex,ey-0.005,ez),major=0.062,minor=0.012,maj_seg=12,min_seg=6,rot=(math.radians(90),0,0))
        assign_mat(rim,mats['flesh']); link(col,rim); objs.append(rim)

    # Jaw upper
    jaw_up=prim('sphere','MK_Jaw_Upper',loc=(0,0.42,3.60),size=0.44,segs=18,rings=12)
    jaw_up.scale=(1.0,0.65,0.38); bpy.ops.object.transform_apply(scale=True)
    assign_mat(jaw_up,mats['flesh']); smart_uv(jaw_up); link(col,jaw_up); objs.append(jaw_up)
    # Jaw lower
    jaw_lo=prim('sphere','MK_Jaw_Lower',loc=(0,0.40,3.44),size=0.42,segs=18,rings=12)
    jaw_lo.scale=(1.0,0.62,0.32); jaw_lo.rotation_euler=(math.radians(24),0,0)
    bpy.ops.object.transform_apply(scale=True,rotation=True)
    assign_mat(jaw_lo,mats['flesh']); smart_uv(jaw_lo); link(col,jaw_lo); objs.append(jaw_lo)

    # 10 upper teeth + 10 lower teeth (irregular sizes)
    for i in range(10):
        ta=math.radians(-36+i*9)
        tx=0.38*math.sin(ta); ts=0.038+rng.uniform(-0.012,0.016)
        th=0.095+rng.uniform(-0.025,0.040)
        tu=prim('cone',f'MK_ToothUp_{i}',loc=(tx,0.44,3.58),r1=ts,r2=0.004,depth=th,verts=4,
                rot=(math.radians(-14+rng.uniform(-8,8)),0,ta))
        assign_mat(tu,mats['bone']); link(col,tu); objs.append(tu)
        tl=prim('cone',f'MK_ToothLo_{i}',loc=(tx,0.42,3.44),r1=ts*0.88,r2=0.003,depth=th*0.85,verts=4,
                rot=(math.radians(160+rng.uniform(-8,8)),0,ta))
        assign_mat(tl,mats['bone']); link(col,tl); objs.append(tl)

    # Forked tongue
    for side,sx in [('L',-1),('R',1)]:
        tng=prim('cone',f'MK_Tongue_{side}',loc=(sx*0.06,0.52,3.48),r1=0.038,r2=0.008,depth=0.24,verts=6,
                 rot=(math.radians(-35),0,math.radians(sx*18)))
        assign_mat(tng,mats['slime']); link(col,tng); objs.append(tng)

    # Nose slits
    for side,sx in [('L',-1),('R',1)]:
        ns=prim('cyl',f'MK_NoseSlit_{side}',loc=(sx*0.12,0.46,3.82),size=0.018,depth=0.055,verts=6,
                rot=(math.radians(60),0,math.radians(sx*22)))
        assign_mat(ns,mats['flesh']); link(col,ns); objs.append(ns)

    # 6 decay patches where mushrooms burst through skin
    decay_pos=[(0.32,0.30,4.10),(-.32,0.30,4.10),(0,0.50,3.72),(0.24,-0.30,3.95),(-.24,-0.30,3.95),(0,-0.42,4.05)]
    for i,(dpx,dpy,dpz) in enumerate(decay_pos):
        dp=prim('sphere',f'MK_FaceDecay_{i}',loc=(dpx,dpy,dpz),size=0.055,segs=8,rings=6)
        dp.scale=(1.0,0.40,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(dp,mats['cap']); link(col,dp); objs.append(dp)
        # Small mushroom stalk erupting from decay
        stk=prim('cone',f'MK_FaceShroom_{i}',loc=(dpx,dpy-0.04,dpz),r1=0.022,r2=0.010,depth=0.10,verts=8,
                 rot=(math.radians(-90+rng.uniform(-15,15)),0,math.radians(i*60)))
        assign_mat(stk,mats['flesh']); link(col,stk); objs.append(stk)
    return objs

def build_mushroom_cap(mats, col):
    """bmesh bell-curve cap 2.8 m diameter, gills, spots, veil ring, drip filaments."""
    objs=[]
    bm=bmesh.new(); segs=40; rings=18; R=1.40; H=0.80
    verts_grid=[]
    for ri in range(rings+1):
        t=ri/rings
        if t<0.30:   r=R*(t/0.30)*0.60
        elif t<0.70: r=R*(0.60+(t-0.30)/0.40*0.40)
        else:        r=R*(1.0-(t-0.70)/0.30*0.05)  # slight flare at rim
        z=H*(1.0-t)**1.6 * 1.15   # bell curve height
        ring=[]
        for si in range(segs):
            a=2*math.pi*si/segs
            ring.append(bm.verts.new(Vector((r*math.cos(a),r*math.sin(a),z+4.50))))
        verts_grid.append(ring)
    # Top cap
    top_v=bm.verts.new(Vector((0,0,H+4.50)))
    for si in range(segs):
        try: bm.faces.new([verts_grid[0][(si+1)%segs],verts_grid[0][si],top_v])
        except: pass
    for ri in range(rings):
        for si in range(segs):
            v0=verts_grid[ri][si]; v1=verts_grid[ri][(si+1)%segs]
            v2=verts_grid[ri+1][(si+1)%segs]; v3=verts_grid[ri+1][si]
            try: bm.faces.new([v0,v1,v2,v3])
            except: pass
    mesh=bpy.data.meshes.new('MK_MushroomCap_Mesh'); bm.to_mesh(mesh); bm.free()
    cap=bpy.data.objects.new('MK_MushroomCap',mesh)
    bpy.context.scene.collection.objects.link(cap)
    assign_mat(cap,mats['cap']); add_sub(cap,2); smart_uv(cap); link(col,cap); objs.append(cap)

    # 24 gill plate strips under cap
    for i in range(24):
        ga=2*math.pi*i/24; gr=0.20+rng.uniform(0,0.80)
        gx=R*0.70*math.cos(ga); gy=R*0.70*math.sin(ga)
        gill=prim('cube',f'MK_CapGill_{i}',loc=(gx,gy,4.52),size=0.01)
        gill.scale=(0.012,gr,0.055); gill.rotation_euler=(0,0,ga)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(gill,mats['slime']); link(col,gill); objs.append(gill)

    # 16 raised spots on cap top
    for i in range(16):
        sr=rng.uniform(0.18,0.90); sa=rng.uniform(0,2*math.pi)
        sx2=sr*R*math.cos(sa); sy2=sr*R*math.sin(sa); sz2=H*(1-(sr)**1.6)*1.15+4.50
        spt=prim('sphere',f'MK_CapSpot_{i}',loc=(sx2,sy2,sz2+0.04),size=rng.uniform(0.040,0.080),segs=8,rings=6)
        spt.scale=(1.0,1.0,0.42); bpy.ops.object.transform_apply(scale=True)
        assign_mat(spt,mats['spore']); link(col,spt); objs.append(spt)

    # Partial veil ring
    veil=prim('torus','MK_CapRing',loc=(0,0,4.52),major=1.02,minor=0.040,maj_seg=36,min_seg=8)
    assign_mat(veil,mats['spore']); link(col,veil); objs.append(veil)

    # 12 dripping slime filaments from cap rim
    for i in range(12):
        da=2*math.pi*i/12; dr=R*0.92
        dx=dr*math.cos(da); dy=dr*math.sin(da)
        driplen=rng.uniform(0.20,0.60)
        drip=prim('cone',f'MK_CapDrip_{i}',loc=(dx,dy,4.48-driplen*0.5),
                  r1=0.014,r2=0.003,depth=driplen,verts=5,rot=(0,0,da))
        assign_mat(drip,mats['slime']); link(col,drip); objs.append(drip)
    return objs

def build_arms(mats, col):
    """Four arms: 2 massive club arms (left pair) + 2 spore-cannon arms (right pair)."""
    objs=[]
    arm_configs=[
        # (prefix, shoulder_loc, dir_sign, is_club)
        ('MK_ArmClub_L',   (-1.05, 0, 2.90),  -1, True),
        ('MK_ArmClub_R',   ( 1.05, 0, 2.90),   1, True),
        ('MK_ArmSpore_L',  (-0.70, 0, 2.60),  -1, False),
        ('MK_ArmSpore_R',  ( 0.70, 0, 2.60),   1, False),
    ]
    for prefix,sh_loc,ds,is_club in arm_configs:
        upper_r=0.22 if is_club else 0.15
        lower_r=0.20 if is_club else 0.13
        elbow_loc=(sh_loc[0]+ds*0.55, sh_loc[1], sh_loc[2]-0.65)
        wrist_loc=(sh_loc[0]+ds*1.10, sh_loc[1], sh_loc[2]-1.30)
        fist_loc=(sh_loc[0]+ds*1.35, sh_loc[1], sh_loc[2]-1.58)
        # Shoulder joint
        sj=prim('sphere',f'{prefix}_Shoulder',loc=sh_loc,size=upper_r*1.2,segs=14,rings=10)
        assign_mat(sj,mats['flesh']); add_sub(sj,1); smart_uv(sj); link(col,sj); objs.append(sj)
        # Upper arm
        ua=seg_obj(f'{prefix}_Upper',sh_loc,elbow_loc,upper_r,mats['flesh'],col,verts=12); objs.append(ua)
        # Elbow joint + mushroom growth
        ej=prim('sphere',f'{prefix}_Elbow',loc=elbow_loc,size=upper_r*1.18,segs=12,rings=10)
        assign_mat(ej,mats['flesh']); add_sub(ej,1); link(col,ej); objs.append(ej)
        eg=prim('cone',f'{prefix}_ElbowShroom',loc=(elbow_loc[0],elbow_loc[1]-0.08,elbow_loc[2]),
                r1=0.06,r2=0.025,depth=0.14,verts=8,rot=(math.radians(-90),0,0))
        assign_mat(eg,mats['cap']); link(col,eg); objs.append(eg)
        # Lower arm
        la=seg_obj(f'{prefix}_Lower',elbow_loc,wrist_loc,lower_r,mats['flesh'],col,verts=12); objs.append(la)
        # Wrist joint
        wj=prim('sphere',f'{prefix}_Wrist',loc=wrist_loc,size=lower_r*1.12,segs=12,rings=8)
        assign_mat(wj,mats['flesh']); add_sub(wj,1); link(col,wj); objs.append(wj)
        if is_club:
            # Club fist
            fist=prim('sphere',f'{prefix}_Fist',loc=fist_loc,size=0.30,segs=16,rings=12)
            fist.scale=(1.0,1.0,0.78); bpy.ops.object.transform_apply(scale=True)
            assign_mat(fist,mats['flesh']); add_sub(fist,1); smart_uv(fist); link(col,fist); objs.append(fist)
            # 5 knuckle spikes
            for ki in range(5):
                ka=math.radians(-24+ki*12)
                kx=fist_loc[0]+0.24*math.sin(ka)
                ksp=prim('cone',f'{prefix}_Knuckle_{ki}',loc=(kx,fist_loc[1],fist_loc[2]+0.15),
                         r1=0.022,r2=0.004,depth=0.18,verts=4,rot=(0,math.radians(-30),ka))
                assign_mat(ksp,mats['bone']); link(col,ksp); objs.append(ksp)
        else:
            # Spore cannon assembly
            cannon=prim('cyl',f'{prefix}_Cannon',loc=fist_loc,size=0.12,depth=0.50,verts=12,
                        rot=(0,math.radians(90*ds),0))
            assign_mat(cannon,mats['spore']); smart_uv(cannon); link(col,cannon); objs.append(cannon)
            # Cannon barrel ring
            ring_c=prim('torus',f'{prefix}_CannonRing',loc=fist_loc,major=0.14,minor=0.022,maj_seg=18,min_seg=6,
                        rot=(0,math.radians(90*ds),0))
            assign_mat(ring_c,mats['vein']); link(col,ring_c); objs.append(ring_c)
            # Ammo drum
            drum=prim('cyl',f'{prefix}_AmmoDrum',loc=(fist_loc[0],fist_loc[1]-0.12,fist_loc[2]),
                      size=0.18,depth=0.22,verts=8)
            assign_mat(drum,mats['spore']); smart_uv(drum); link(col,drum); objs.append(drum)
    return objs

def build_legs(mats, col):
    """Two pillar legs with thick fungal feet."""
    objs=[]
    for side,sx in [('L',-1),('R',1)]:
        hip=(sx*0.58,0,1.22); knee=(sx*0.60,0,0.62); ankle=(sx*0.56,0,0.20)
        foot=(sx*0.60,0.24,0.06)
        # Hip joint
        hj=prim('sphere',f'MK_Hip_{side}',loc=hip,size=0.32,segs=14,rings=10)
        assign_mat(hj,mats['flesh']); add_sub(hj,1); link(col,hj); objs.append(hj)
        # Thigh
        th=seg_obj(f'MK_Thigh_{side}',hip,knee,0.25,mats['flesh'],col,verts=14); objs.append(th)
        # Knee joint
        kj=prim('sphere',f'MK_Knee_{side}',loc=knee,size=0.28,segs=12,rings=10)
        assign_mat(kj,mats['flesh']); add_sub(kj,1); link(col,kj); objs.append(kj)
        # Shin
        sh=seg_obj(f'MK_Shin_{side}',knee,ankle,0.22,mats['flesh'],col,verts=12); objs.append(sh)
        # Ankle joint
        aj=prim('sphere',f'MK_Ankle_{side}',loc=ankle,size=0.24,segs=12,rings=8)
        assign_mat(aj,mats['flesh']); add_sub(aj,1); link(col,aj); objs.append(aj)
        # Foot (flat wide mushroom pad)
        ft=prim('cyl',f'MK_Foot_{side}',loc=foot,size=0.38,depth=0.14,verts=12)
        ft.scale=(1.0,1.6,0.60); bpy.ops.object.transform_apply(scale=True)
        assign_mat(ft,mats['flesh']); add_sub(ft,1); smart_uv(ft); link(col,ft); objs.append(ft)
        # 3 toe stumps
        for ti in range(3):
            tx=sx*(0.30+ti*0.14); tz=0.10
            toe=prim('cone',f'MK_Toe_{side}_{ti}',loc=(tx,0.55,tz),r1=0.08,r2=0.02,depth=0.22,verts=6,
                     rot=(math.radians(-20),0,0))
            assign_mat(toe,mats['flesh']); link(col,toe); objs.append(toe)
    return objs

def build_scary_attachments(mats, col):
    """Impaled skulls, shoulder bone spikes, root tendrils, spore sacs, bone fragments, infection drips."""
    objs=[]

    # ── 5 impaled victim skulls on shoulder spikes ──
    spike_positions=[
        (-1.20,0,3.40),(-1.10,-0.25,3.20),(-0.95,0.28,3.30),
        ( 1.20,0,3.40),( 1.10,-0.25,3.20),
    ]
    for i,(spx,spy,spz) in enumerate(spike_positions):
        # Shoulder spike bone
        sp=prim('cone',f'MK_ShoulderSpike_{i}',loc=(spx,spy,spz+0.16),
                r1=0.035,r2=0.008,depth=0.36,verts=4,rot=(0,0,math.radians(i*35)))
        assign_mat(sp,mats['bone']); link(col,sp); objs.append(sp)
        # Skull impaled on spike
        sk=prim('sphere',f'MK_InfectedSkull_{i}',loc=(spx,spy,spz+0.40),size=0.12,segs=12,rings=10)
        sk.scale=(1.0,0.90,1.10); bpy.ops.object.transform_apply(scale=True)
        assign_mat(sk,mats['bone']); link(col,sk); objs.append(sk)
        # Skull eye sockets
        for se,exo in enumerate([-0.04,0.04]):
            sket=prim('sphere',f'MK_SkullEye_{i}_{se}',loc=(spx+exo,spy-0.06,spz+0.44),size=0.030,segs=8,rings=6)
            assign_mat(sket,mats['glow']); link(col,sket); objs.append(sket)
        # Green infection drip from skull
        skd=prim('cone',f'MK_SkullDrip_{i}',loc=(spx,spy,spz+0.28),r1=0.012,r2=0.003,depth=0.22,verts=4)
        assign_mat(skd,mats['slime']); link(col,skd); objs.append(skd)

    # ── 3 extra large shoulder bone spikes ──
    big_spikes=[(-1.35,0,3.10),(0,-.88,3.50),(1.35,0,3.10)]
    for i,(bsx,bsy,bsz) in enumerate(big_spikes):
        bs=prim('cone',f'MK_BigSpike_{i}',loc=(bsx,bsy,bsz),r1=0.055,r2=0.008,depth=0.55,verts=4,
                rot=(math.radians(rng.uniform(-20,20)),math.radians(rng.uniform(-15,15)),0))
        assign_mat(bs,mats['bone']); link(col,bs); objs.append(bs)

    # ── 10 mycelium root tendrils erupting from ground ──
    for i in range(10):
        ra=2*math.pi*i/10+rng.uniform(-0.3,0.3)
        rd=rng.uniform(0.80,1.80)
        rx=rd*math.cos(ra); ry=rd*math.sin(ra); rlen=rng.uniform(0.45,1.10)
        rt=prim('cone',f'MK_RootTendril_{i}',loc=(rx,ry,rlen*0.5-0.1),
                r1=0.040,r2=0.008,depth=rlen,verts=5,
                rot=(math.radians(rng.uniform(-25,25)),math.radians(rng.uniform(-25,25)),ra))
        assign_mat(rt,mats['vein']); link(col,rt); objs.append(rt)
        # Small mushroom tip on each tendril
        rm=prim('sphere',f'MK_RootTip_{i}',loc=(rx,ry,rlen-0.05),size=0.055,segs=8,rings=6)
        assign_mat(rm,mats['cap']); link(col,rm); objs.append(rm)

    # ── 6 pulsating hanging spore sacs ──
    sac_positions=[(-0.70,0,2.10),(-0.50,0.55,1.90),(0,0.65,1.80),(0.70,0,2.10),(0.50,0.55,1.90),(0,-0.65,2.00)]
    for i,(sax,say,saz) in enumerate(sac_positions):
        saclen=rng.uniform(0.28,0.52)
        sac=prim('sphere',f'MK_SporeSac_{i}',loc=(sax,say,saz),size=rng.uniform(0.10,0.16),segs=10,rings=8)
        sac.scale=(1.0,1.0,1.45); bpy.ops.object.transform_apply(scale=True)
        assign_mat(sac,mats['spore']); link(col,sac); objs.append(sac)
        # Hanging stalk
        stk=prim('cyl',f'MK_SacStalk_{i}',loc=(sax,say,saz+0.22),size=0.012,depth=0.30,verts=5)
        assign_mat(stk,mats['flesh']); link(col,stk); objs.append(stk)
        # Infection glow pulsing inside sac
        gl=prim('sphere',f'MK_SacGlow_{i}',loc=(sax,say,saz),size=0.06,segs=6,rings=4)
        assign_mat(gl,mats['glow']); link(col,gl); objs.append(gl)

    # ── 12 bone shards fused into torso skin ──
    bone_fuse_pos=[
        (0.82,0,2.80),(-.82,0,2.80),(0.70,0.50,3.10),(-.70,0.50,3.10),
        (0.75,-0.40,2.50),(-.75,-0.40,2.50),(0.60,0,1.80),(-.60,0,1.80),
        (0.30,0.82,2.60),(-.30,0.82,2.60),(0.50,-0.70,3.20),(-.50,-0.70,3.20),
    ]
    for i,(bfx,bfy,bfz) in enumerate(bone_fuse_pos):
        bf=prim('cone',f'MK_BoneFragment_{i}',loc=(bfx,bfy,bfz),r1=0.018,r2=0.004,depth=0.18,verts=4,
                rot=(math.radians(rng.uniform(-60,60)),math.radians(rng.uniform(-30,30)),0))
        assign_mat(bf,mats['bone']); link(col,bf); objs.append(bf)

    # ── 4 spore cloud burst spheres floating near body ──
    cloud_pos=[(-1.20,0,3.80),(1.20,0,3.80),(0,1.10,2.50),(0,-1.10,2.50)]
    for i,(cx,cy,cz) in enumerate(cloud_pos):
        cloud=prim('sphere',f'MK_SporeCloud_{i}',loc=(cx,cy,cz),size=rng.uniform(0.15,0.26),segs=8,rings=6)
        cloud.scale=(1.0,1.0,0.72); bpy.ops.object.transform_apply(scale=True)
        assign_mat(cloud,mats['spore']); link(col,cloud); objs.append(cloud)

    # ── 8 infection drip rivulets on body ──
    drip_pos=[(0.68,0,2.70),(-.68,0,2.70),(0.42,0.60,3.00),(-.42,0.60,3.00),(0.55,-0.50,2.40),(-.55,-0.50,2.40),(0.20,0.82,2.80),(-.20,0.82,2.80)]
    for i,(drx,dry,drz) in enumerate(drip_pos):
        dlen=rng.uniform(0.30,0.70)
        dr=prim('cone',f'MK_InfectionDrip_{i}',loc=(drx,dry,drz-dlen*0.5),
                r1=0.010,r2=0.003,depth=dlen,verts=4)
        assign_mat(dr,mats['slime']); link(col,dr); objs.append(dr)
    return objs

# ═══════════════════════════════════════════════════════════════════
#  ASSEMBLE
# ═══════════════════════════════════════════════════════════════════

def main():
    clear_scene()
    col  = new_col('IsleTrial_Boss_MyceliumKing')
    mats = build_materials()
    # Patch missing 'glow' key alias in scary attachments
    mats['glow'] = mats['glow'] if 'glow' in mats else mats['vein']

    all_objs=[]
    all_objs += build_torso(mats, col)
    all_objs += build_head(mats, col)
    all_objs += build_mushroom_cap(mats, col)
    all_objs += build_arms(mats, col)
    all_objs += build_legs(mats, col)
    all_objs += build_scary_attachments(mats, col)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    root=bpy.context.active_object; root.name='Boss_MyceliumKing_ROOT'; link(col,root)
    for obj in all_objs:
        if obj.parent is None: obj.parent=root

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active=root
    mc=sum(1 for o in col.objects if o.type=='MESH')
    print("="*60)
    print("[IsleTrial] Boss: Mycelium King – MAXIMUM DETAIL")
    print(f"  Mesh objects : {mc}")
    print(f"  Materials    : {len(bpy.data.materials)}")
    print("  Scary adds   : 5 impaled skulls, 10 root tendrils,")
    print("                 6 spore sacs, 12 bone fragments, 4 spore clouds")
    print("  Next: run 10_Boss_MyceliumKing_Rig.py")
    print("="*60)

main()
