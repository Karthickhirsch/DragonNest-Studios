"""
IsleTrial – Boss 05: Ancient Coral Titan  (FULL REBUILD – MAXIMUM DETAIL)
==========================================================================
Height  ~4.5 m  Colossal ocean titan encased in living coral armour.
Theme   Enormous humanoid body completely encrusted with branching
        coral growths, ship wreckage fused into torso chest-plate,
        ship's steering wheel embedded in left shoulder, anchor
        chain weapons, crab/barnacle infestation on body, massive
        anemone tentacle crown on head, kelp/seaweed draping from
        joints, bioluminescent coral veins, trapped sea creature
        skeletons visible inside coral body sections, giant anchor
        weapons in fists, coral-tipped horn spikes all over body.

Mesh Objects Built:
  BODY CORE
    CT_Body              – bmesh 36×24 massive titan torso (wide barrel)
    CT_Neck              – thick coral-crusted neck
    CT_Gut               – heavy gut overhang sphere
    CT_CoralGrowth_*     – 22 individual branching coral outcroppings on torso
    CT_BioVein_*         – 16 bioluminescent vein ridge lines on torso

  HEAD
    CT_Head              – bmesh 28×20 rounded stone-like head
    CT_HeadCoral_*       – 12 coral growths erupting from head surface
    CT_Eye_L/R           – deep-set eye spheres (3-layer: socket/iris/pupil)
    CT_EyeCoral_L/R      – coral ridge above each eye
    CT_Mouth             – wide flat mouth slit
    CT_Tooth_*           – 6 wide flat rocky teeth each jaw
    CT_Chin              – protruding rock-like chin

  ANEMONE CROWN
    CT_AnemoneBase       – thick ring base on top of head
    CT_AnemoneTentacle_* – 20 anemone tentacles (varying length + tip spheres)
    CT_AnemoneGlow_*     – glow spheres at tips of longer tentacles

  ARMS + HANDS
    CT_ArmUpper_*/Lower_* – massive armoured arm pillars
    CT_Elbow_*            – elbow joint coral clusters
    CT_CoralElbowSpike_*  – 4 coral spikes per elbow
    CT_Fist_*             – massive fist boulders
    CT_Anchor_L/R         – giant ship anchor weapons
    CT_AnchorShaft_*      – anchor shaft
    CT_AnchorFluke_*      – anchor fluke arms

  LEGS
    CT_Thigh_*/Shin_*/Foot_* – massive pillar legs
    CT_KneeCoralCluster_* – coral cluster at each knee
    CT_FootCoralSpike_*   – coral spikes erupting from feet

  SHIP WRECKAGE TORSO PLATE
    CT_ShipPlank_*        – 10 planks of ship hull fused into chest
    CT_ShipRib_*          – 4 exposed ship ribs
    CT_ShipWheel          – steering wheel on left shoulder
    CT_WheelSpoke_*       – 8 wheel spokes
    CT_AnchorChain_*      – 12 chain link segments on arms

  SCARY ATTACHMENTS
    CT_CrabClaw_L/R       – giant crab claw shoulder pauldrons
    CT_CrabLeg_*          – 6 crab legs per shoulder claw
    CT_KelpStrand_*       – 12 kelp/seaweed strands hanging from joints
    CT_KelpLeaf_*         – 3 leaves per strand
    CT_TrappedFishSkel_*  – 4 fish skeleton shapes inside coral body
    CT_BarnaclePatch_*    – 14 barnacle patches scattered on body
    CT_CoralHorn_*        – 14 large coral spike horns erupting from shoulders/back
    CT_BubbleCluster_*    – 8 bubble cluster spheres rising from body
    CT_SeaStarDecal_*     – 5 sea star shapes adhered to body

Materials (full dual-path procedural + [UNITY] image slots):
  Mat_CT_Stone       – grey-blue stone skin + Musgrave erosion cracks
  Mat_CT_Coral       – warm orange-red coral + Voronoi cell branching
  Mat_CT_BioLum      – teal bioluminescent vein glow
  Mat_CT_Wood        – dark waterlogged ship plank wood
  Mat_CT_Iron_Rust   – heavily rusted anchor/chain iron
  Mat_CT_Barnacle    – rough grey-white voronoi barnacle
  Mat_CT_Kelp        – translucent dark green kelp leaf
  Mat_CT_Bone        – aged bone for trapped fish skeletons
  Mat_CT_Anemone     – translucent pink anemone tentacles

Run BEFORE 14_Boss_CoralTitan_Rig.py
"""

import bpy, bmesh, math, random
from mathutils import Vector

rng = random.Random(55)

# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)

def new_col(name):
    c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c

def link(col,obj):
    for ex in list(obj.users_collection): ex.objects.unlink(obj)
    col.objects.link(obj)

def add_sub(obj,lv=2):
    m=obj.modifiers.new('Sub','SUBSURF'); m.levels=lv; m.render_levels=lv

def add_bevel(obj,w=0.015,s=2):
    m=obj.modifiers.new('Bev','BEVEL'); m.width=w; m.segments=s; m.profile=0.5

def smart_uv(obj):
    bpy.context.view_layer.objects.active=obj; obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66,island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT'); obj.select_set(False)

def prim(tp,name,loc=(0,0,0),rot=(0,0,0),size=1.0,**kw):
    if tp=='sphere':  bpy.ops.mesh.primitive_uv_sphere_add(radius=size,location=loc,rotation=rot,segments=kw.get('segs',22),ring_count=kw.get('rings',14))
    elif tp=='cyl':   bpy.ops.mesh.primitive_cylinder_add(radius=size,depth=kw.get('depth',1.0),location=loc,rotation=rot,vertices=kw.get('verts',16))
    elif tp=='cone':  bpy.ops.mesh.primitive_cone_add(radius1=kw.get('r1',size),radius2=kw.get('r2',0),depth=kw.get('depth',1.0),location=loc,rotation=rot,vertices=kw.get('verts',8))
    elif tp=='cube':  bpy.ops.mesh.primitive_cube_add(size=size,location=loc,rotation=rot)
    elif tp=='torus': bpy.ops.mesh.primitive_torus_add(major_radius=kw.get('major',size),minor_radius=kw.get('minor',0.06),location=loc,rotation=rot,major_segments=kw.get('maj_seg',24),minor_segments=kw.get('min_seg',8))
    obj=bpy.context.active_object; obj.name=name; return obj

def assign_mat(obj,mat):
    if obj.data.materials: obj.data.materials[0]=mat
    else: obj.data.materials.append(mat)

def seg_obj(name,p1,p2,radius,mat,col,verts=10):
    d=Vector(p2)-Vector(p1); mid=Vector(p1)+d*0.5
    obj=prim('cyl',name,loc=mid,size=radius,depth=d.length,verts=verts)
    obj.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    assign_mat(obj,mat); smart_uv(obj); link(col,obj); return obj

# ═══════════════════════════════════════════════════════════════════
#  MATERIALS
# ═══════════════════════════════════════════════════════════════════

def _n(nodes,ntype,loc,label=None):
    nd=nodes.new(ntype); nd.location=loc
    if label: nd.label=nd.name=label; return nd

def _img(nodes,sname,loc):
    nd=nodes.new('ShaderNodeTexImage'); nd.location=loc
    nd.label=nd.name=f'[UNITY] {sname}'; return nd

def _mapping(nodes,links,scale=(4,4,4),loc=(-900,0)):
    tc=_n(nodes,'ShaderNodeTexCoord',(loc[0]-200,loc[1]))
    mp=_n(nodes,'ShaderNodeMapping',loc)
    mp.inputs['Scale'].default_value=(*scale,)
    links.new(tc.outputs['UV'],mp.inputs['Vector']); return mp

def _mix_pi(nodes,links,proc,img_nd,loc):
    mix=_n(nodes,'ShaderNodeMixRGB',loc); mix.blend_type='MIX'; mix.inputs[0].default_value=0.0
    links.new(proc,mix.inputs[1]); links.new(img_nd.outputs['Color'],mix.inputs[2]); return mix

def _bump_n(nodes,links,mp,scale=20.0,strength=0.50,loc=(-400,-400)):
    bn=_n(nodes,'ShaderNodeTexNoise',loc); bn.inputs['Scale'].default_value=scale; bn.inputs['Detail'].default_value=10.0
    links.new(mp.outputs['Vector'],bn.inputs['Vector'])
    img_n=_img(nodes,'_NormalMap',(loc[0],loc[1]-180))
    mix_n=_mix_pi(nodes,links,bn.outputs['Fac'],img_n,(loc[0]+260,loc[1]-90))
    bmp=_n(nodes,'ShaderNodeBump',(loc[0]+480,loc[1]-90)); bmp.inputs['Strength'].default_value=strength
    links.new(mix_n.outputs['Color'],bmp.inputs['Height']); return bmp

def _base(name):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    n=mat.node_tree.nodes; lk=mat.node_tree.links; n.clear()
    bsdf=_n(n,'ShaderNodeBsdfPrincipled',(700,0))
    out=_n(n,'ShaderNodeOutputMaterial',(1000,0))
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface']); return mat,n,lk,bsdf

def mat_stone(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(3,3,3))
    musg=_n(n,'ShaderNodeTexMusgrave',(-700,350)); musg.musgrave_type='RIDGED_MULTIFRACTAL'
    musg.inputs['Scale'].default_value=5.0; musg.inputs['Detail'].default_value=10.0
    lk.new(mp.outputs['Vector'],musg.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-700,150)); noise.inputs['Scale'].default_value=18.0; noise.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    vor=_n(n,'ShaderNodeTexVoronoi',(-700,-50)); vor.feature='DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value=10.0
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    mix_mn=_n(n,'ShaderNodeMixRGB',(-400,250)); mix_mn.blend_type='MULTIPLY'; mix_mn.inputs[0].default_value=0.55
    lk.new(musg.outputs['Fac'],mix_mn.inputs[1]); lk.new(noise.outputs['Fac'],mix_mn.inputs[2])
    mix_mv=_n(n,'ShaderNodeMixRGB',(-200,200)); mix_mv.blend_type='OVERLAY'; mix_mv.inputs[0].default_value=0.22
    lk.new(mix_mn.outputs['Color'],mix_mv.inputs[1]); lk.new(vor.outputs['Distance'],mix_mv.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(50,200))
    cr.color_ramp.elements[0].color=(0.18,0.22,0.28,1)   # grey-blue stone
    e1=cr.color_ramp.elements.new(0.40); e1.color=(0.28,0.32,0.38,1)
    cr.color_ramp.elements[1].color=(0.40,0.44,0.50,1)
    lk.new(mix_mv.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-700,-250))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(320,120))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    mr=_n(n,'ShaderNodeMapRange',(50,-120))
    mr.inputs['From Min'].default_value=0.2; mr.inputs['From Max'].default_value=0.8
    mr.inputs['To Min'].default_value=0.68; mr.inputs['To Max'].default_value=0.88
    lk.new(noise.outputs['Fac'],mr.inputs['Value']); lk.new(mr.outputs['Result'],bsdf.inputs['Roughness'])
    bmp=_bump_n(n,lk,mp,scale=28.0,strength=0.65); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_coral(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(5,5,5))
    vor=_n(n,'ShaderNodeTexVoronoi',(-600,200)); vor.inputs['Scale'].default_value=16.0; vor.feature='DISTANCE_TO_EDGE'
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-600,0)); noise.inputs['Scale'].default_value=24.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    musg=_n(n,'ShaderNodeTexMusgrave',(-600,-200)); musg.musgrave_type='FBM'; musg.inputs['Scale'].default_value=8.0
    lk.new(mp.outputs['Vector'],musg.inputs['Vector'])
    mix_vn=_n(n,'ShaderNodeMixRGB',(-300,200)); mix_vn.blend_type='MULTIPLY'; mix_vn.inputs[0].default_value=0.48
    lk.new(vor.outputs['Distance'],mix_vn.inputs[1]); lk.new(noise.outputs['Fac'],mix_vn.inputs[2])
    mix_vm=_n(n,'ShaderNodeMixRGB',(-100,150)); mix_vm.blend_type='OVERLAY'; mix_vm.inputs[0].default_value=0.28
    lk.new(mix_vn.outputs['Color'],mix_vm.inputs[1]); lk.new(musg.outputs['Fac'],mix_vm.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(150,200))
    cr.color_ramp.elements[0].color=(0.45,0.08,0.04,1)   # dark coral red
    e1=cr.color_ramp.elements.new(0.42); e1.color=(0.75,0.22,0.08,1)
    cr.color_ramp.elements[1].color=(0.95,0.50,0.18,1)   # bright orange coral
    lk.new(mix_vm.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-600,-300))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(380,120))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.76
    bsdf.inputs['Subsurface Weight'].default_value=0.05
    bsdf.inputs['Subsurface Radius'].default_value=(0.72,0.22,0.10)
    bmp=_bump_n(n,lk,mp,scale=22.0,strength=0.55); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_biolum(name):
    mat,n,lk,bsdf=_base(name)
    wave=_n(n,'ShaderNodeTexWave',(-400,100)); wave.wave_type='BANDS'; wave.inputs['Scale'].default_value=8.0; wave.inputs['Distortion'].default_value=3.5
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.02,0.28,0.32,1)
    cr.color_ramp.elements[1].color=(0.06,0.78,0.88,1)
    lk.new(wave.outputs['Color'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Emission Color'].default_value=(0.04,0.85,0.95,1)
    bsdf.inputs['Emission Strength'].default_value=2.8
    bsdf.inputs['Roughness'].default_value=0.15
    return mat

def mat_waterlogged_wood(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(4,4,4))
    musg=_n(n,'ShaderNodeTexMusgrave',(-600,200)); musg.musgrave_type='FBM'; musg.inputs['Scale'].default_value=3.5; musg.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],musg.inputs['Vector'])
    wave=_n(n,'ShaderNodeTexWave',(-600,0)); wave.wave_type='BANDS'; wave.inputs['Scale'].default_value=3.0; wave.inputs['Distortion'].default_value=2.0
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    mix_mw=_n(n,'ShaderNodeMixRGB',(-300,100)); mix_mw.blend_type='MULTIPLY'; mix_mw.inputs[0].default_value=0.52
    lk.new(musg.outputs['Fac'],mix_mw.inputs[1]); lk.new(wave.outputs['Color'],mix_mw.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.04,0.04,0.06,1)
    cr.color_ramp.elements[1].color=(0.16,0.14,0.10,1)
    lk.new(mix_mw.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-600,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.88
    bmp=_bump_n(n,lk,mp,scale=20.0,strength=0.60); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_iron_rust(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(5,5,5))
    vor=_n(n,'ShaderNodeTexVoronoi',(-500,200)); vor.feature='DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value=14.0
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-500,0)); noise.inputs['Scale'].default_value=22.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mix_vn=_n(n,'ShaderNodeMixRGB',(-250,100)); mix_vn.blend_type='OVERLAY'; mix_vn.inputs[0].default_value=0.48
    lk.new(vor.outputs['Distance'],mix_vn.inputs[1]); lk.new(noise.outputs['Fac'],mix_vn.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.22,0.06,0.02,1)   # rust
    cr.color_ramp.elements[1].color=(0.14,0.14,0.16,1)   # iron
    lk.new(mix_vn.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-500,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value=0.68; bsdf.inputs['Roughness'].default_value=0.80
    bmp=_bump_n(n,lk,mp,scale=24.0,strength=0.60); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_barnacle(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(10,10,10))
    vor=_n(n,'ShaderNodeTexVoronoi',(-400,100)); vor.inputs['Scale'].default_value=22.0; vor.feature='DISTANCE_TO_EDGE'
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-400,-50)); noise.inputs['Scale'].default_value=16.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mix_vn=_n(n,'ShaderNodeMixRGB',(-150,50)); mix_vn.blend_type='OVERLAY'; mix_vn.inputs[0].default_value=0.40
    lk.new(vor.outputs['Distance'],mix_vn.inputs[1]); lk.new(noise.outputs['Fac'],mix_vn.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(50,50))
    cr.color_ramp.elements[0].color=(0.42,0.40,0.36,1)
    cr.color_ramp.elements[1].color=(0.74,0.72,0.68,1)
    lk.new(mix_vn.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-400,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.88
    bmp=_bump_n(n,lk,mp,scale=26.0,strength=0.65); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_kelp(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(8,8,8))
    wave=_n(n,'ShaderNodeTexWave',(-500,100)); wave.wave_type='BANDS'; wave.inputs['Scale'].default_value=5.0; wave.inputs['Distortion'].default_value=1.5
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    cr=_n(n,'ShaderNodeValToRGB',(-200,100))
    cr.color_ramp.elements[0].color=(0.02,0.14,0.02,1)
    cr.color_ramp.elements[1].color=(0.06,0.36,0.06,1)
    lk.new(wave.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-500,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.72
    bsdf.inputs['Transmission Weight'].default_value=0.30
    bsdf.inputs['Alpha'].default_value=0.75; mat.blend_method='BLEND'
    return mat

def mat_bone(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(8,8,8))
    noise=_n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=18.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.60,0.56,0.44,1); cr.color_ramp.elements[1].color=(0.82,0.78,0.66,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-400,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.62
    bsdf.inputs['Subsurface Weight'].default_value=0.04
    return mat

def mat_anemone(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(10,10,10))
    noise=_n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=16.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.55,0.08,0.28,1)   # dark pink
    cr.color_ramp.elements[1].color=(0.88,0.45,0.60,1)   # bright pink
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-400,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.42
    bsdf.inputs['Transmission Weight'].default_value=0.20
    bsdf.inputs['Subsurface Weight'].default_value=0.08
    return mat

def build_materials():
    return {
        'stone'   : mat_stone('Mat_CT_Stone'),
        'coral'   : mat_coral('Mat_CT_Coral'),
        'bio'     : mat_biolum('Mat_CT_BioLum'),
        'wood'    : mat_waterlogged_wood('Mat_CT_Wood'),
        'iron'    : mat_iron_rust('Mat_CT_Iron'),
        'barnacle': mat_barnacle('Mat_CT_Barnacle'),
        'kelp'    : mat_kelp('Mat_CT_Kelp'),
        'bone'    : mat_bone('Mat_CT_Bone'),
        'anemone' : mat_anemone('Mat_CT_Anemone'),
    }

# ═══════════════════════════════════════════════════════════════════
#  GEOMETRY
# ═══════════════════════════════════════════════════════════════════

def build_body(mats, col):
    """36×24 bmesh massive barrel torso with coral growths and bio veins."""
    objs=[]
    bm=bmesh.new(); segs=36; rings=24; W=1.10; H=1.50
    verts_grid=[]
    for ri in range(rings+1):
        t=ri/rings; y=-H+t*2*H
        if t<0.10:   w=W*(t/0.10)*0.52
        elif t<0.45: w=W*(0.52+(t-0.10)/0.35*0.48)
        elif t<0.65: w=W*1.0
        elif t<0.85: w=W*(1.0-(t-0.65)/0.20*0.14)
        else:        w=W*(0.86-(t-0.85)/0.15*0.22)
        if t<0.12:   h=H*(t/0.12)*0.45
        elif t<0.60: h=H*(0.45+(t-0.12)/0.48*0.55)
        elif t<0.82: h=H*1.0
        else:        h=H*(1.0-(t-0.82)/0.18*0.18)
        ring=[]
        for si in range(segs):
            a=2*math.pi*si/segs
            ring.append(bm.verts.new(Vector((w*math.cos(a),w*math.sin(a),y))))
        verts_grid.append(ring)
    for ri in range(rings):
        for si in range(segs):
            v0=verts_grid[ri][si]; v1=verts_grid[ri][(si+1)%segs]
            v2=verts_grid[ri+1][(si+1)%segs]; v3=verts_grid[ri+1][si]
            try: bm.faces.new([v0,v1,v2,v3])
            except: pass
    tc=bm.verts.new(Vector((0,0,-H))); hc=bm.verts.new(Vector((0,0,H)))
    for si in range(segs):
        try:
            bm.faces.new([verts_grid[0][(si+1)%segs],verts_grid[0][si],tc])
            bm.faces.new([verts_grid[-1][si],verts_grid[-1][(si+1)%segs],hc])
        except: pass
    mesh=bpy.data.meshes.new('CT_Body_Mesh'); bm.to_mesh(mesh); bm.free()
    body=bpy.data.objects.new('CT_Body',mesh); body.location=(0,0,2.50)
    bpy.context.scene.collection.objects.link(body)
    assign_mat(body,mats['stone']); add_sub(body,2); smart_uv(body); link(col,body); objs.append(body)

    # Neck
    neck=prim('cyl','CT_Neck',loc=(0,0,4.12),size=0.55,depth=0.60,verts=18)
    assign_mat(neck,mats['stone']); add_sub(neck,1); smart_uv(neck); link(col,neck); objs.append(neck)
    # Gut
    gut=prim('sphere','CT_Gut',loc=(0.12,0,1.52),size=0.90,segs=20,rings=16)
    gut.scale=(1.0,1.0,0.75); bpy.ops.object.transform_apply(scale=True)
    assign_mat(gut,mats['stone']); add_sub(gut,1); smart_uv(gut); link(col,gut); objs.append(gut)

    # 22 coral growth outcroppings on torso
    coral_pos=[
        ( 1.08, 0, 3.20),(-1.08, 0, 3.20),( 1.05, 0, 2.60),(-1.05, 0, 2.60),
        ( 1.02, 0, 2.00),(-1.02, 0, 2.00),( 0.95, 0, 1.42),(-0.95, 0, 1.42),
        ( 0, 1.08, 3.00),( 0,-1.08, 3.00),( 0, 1.05, 2.40),( 0,-1.05, 2.40),
        ( 0.72, 0.72, 3.40),(-0.72, 0.72, 3.40),( 0.72,-0.72, 3.40),(-0.72,-0.72, 3.40),
        ( 0.80, 0.60, 1.80),(-0.80, 0.60, 1.80),( 0.60,-0.80, 2.20),(-0.60,-0.80, 2.20),
        ( 0, 0, 4.05),( 0.50, 0, 4.02),
    ]
    for ci,(cx,cy,cz) in enumerate(coral_pos):
        # Main coral branch
        cbr=prim('cone',f'CT_CoralGrowth_{ci}_Main',loc=(cx,cy,cz),r1=rng.uniform(0.04,0.09),r2=0.010,
                 depth=rng.uniform(0.20,0.45),verts=5,rot=(rng.uniform(-0.4,0.4),rng.uniform(-0.3,0.3),math.radians(ci*16)))
        assign_mat(cbr,mats['coral']); link(col,cbr); objs.append(cbr)
        # 2-3 sub-branches
        for sbi in range(rng.randint(2,3)):
            sba=math.radians(sbi*120+rng.uniform(-20,20))
            sbr=prim('cone',f'CT_CoralGrowth_{ci}_Sub{sbi}',loc=(cx+0.08*math.cos(sba),cy+0.08*math.sin(sba),cz+0.12),
                     r1=0.022,r2=0.005,depth=rng.uniform(0.12,0.25),verts=5,
                     rot=(rng.uniform(-0.5,0.5),rng.uniform(-0.5,0.5),sba))
            assign_mat(sbr,mats['coral']); link(col,sbr); objs.append(sbr)

    # 16 bioluminescent vein ridge lines
    bio_pos=[
        ( 0.88, 0, 3.10, 70),(-0.88, 0, 3.10,110),( 0.75, 0, 2.50, 75),(-0.75, 0, 2.50,105),
        ( 0.65, 0, 1.90, 80),(-0.65, 0, 1.90,100),( 0, 0.88, 3.05, 90),( 0,-0.88, 3.05, 90),
        ( 0.55, 0.65, 3.30, 68),(-0.55, 0.65, 3.30,112),( 0.55,-0.65, 2.80, 72),(-0.55,-0.65, 2.80,108),
        ( 0.42, 0.80, 2.20, 64),(-0.42, 0.80, 2.20,116),( 0.35,-0.85, 2.80, 78),(-0.35,-0.85, 2.80,102),
    ]
    for bvi,(bvx,bvy,bvz,bvr) in enumerate(bio_pos):
        bv=prim('cyl',f'CT_BioVein_{bvi}',loc=(bvx,bvy,bvz),size=0.014,depth=0.42,verts=4,rot=(0,math.radians(bvr),math.radians(bvi*22)))
        assign_mat(bv,mats['bio']); link(col,bv); objs.append(bv)
    return objs

def build_head(mats, col):
    """bmesh head with 12 coral growths, deep-set eyes, wide rocky teeth, anemone crown."""
    objs=[]
    bm=bmesh.new(); segs=28; rings=20
    for ri in range(rings+1):
        t=ri/rings; a_lat=math.pi*t
        z=0.55*math.cos(a_lat); r=0.52*math.sin(a_lat)
        if t<0.22: r*=(0.60+t/0.22*0.40)
        if t>0.78: r*=(1.0-(t-0.78)/0.22*0.25)
        for si in range(segs):
            a=2*math.pi*si/segs
            bm.verts.new(Vector((r*math.cos(a),r*math.sin(a),z)))
    bm.verts.ensure_lookup_table()
    all_v=list(bm.verts)
    for ri in range(rings):
        for si in range(segs):
            v0=all_v[ri*segs+si]; v1=all_v[ri*segs+(si+1)%segs]
            v2idx=(ri+1)*segs+(si+1)%segs; v3idx=(ri+1)*segs+si
            if v2idx<len(all_v) and v3idx<len(all_v):
                try: bm.faces.new([v0,v1,all_v[v2idx],all_v[v3idx]])
                except: pass
    mesh=bpy.data.meshes.new('CT_Head_Mesh'); bm.to_mesh(mesh); bm.free()
    head=bpy.data.objects.new('CT_Head',mesh); head.location=(0,0,4.60); head.scale=(1.0,1.0,1.08)
    bpy.context.scene.collection.objects.link(head)
    assign_mat(head,mats['stone']); bpy.ops.object.transform_apply(scale=True)
    add_sub(head,2); smart_uv(head); link(col,head); objs.append(head)

    # 12 coral growths on head
    hc_pos=[(0.40,0.12,4.88),(-.40,0.12,4.88),(0.32,-.30,4.80),(-.32,-.30,4.80),(0,0.44,4.92),(0,-.44,4.82),(0.28,0.32,5.02),(-.28,0.32,5.02),(0.46,-.08,4.70),(-.46,-.08,4.70),(0.12,-.42,4.72),(-.12,-.42,4.72)]
    for hci,(hcx,hcy,hcz) in enumerate(hc_pos):
        hcgr=prim('cone',f'CT_HeadCoral_{hci}',loc=(hcx,hcy,hcz),r1=rng.uniform(0.025,0.055),r2=0.006,depth=rng.uniform(0.14,0.30),verts=5,
                  rot=(rng.uniform(-0.3,0.3),rng.uniform(-0.3,0.3),math.radians(hci*30)))
        assign_mat(hcgr,mats['coral']); link(col,hcgr); objs.append(hcgr)

    # Eyes
    for side,sx in [('L',-0.28),('R',0.28)]:
        ez2=4.62; ey2=0.44
        sock=prim('sphere',f'CT_EyeSocket_{side}',loc=(sx,ey2-0.04,ez2),size=0.14,segs=12,rings=10)
        sock.scale=(1.0,0.55,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(sock,mats['stone']); link(col,sock); objs.append(sock)
        eye=prim('sphere',f'CT_Eye_{side}',loc=(sx,ey2+0.02,ez2),size=0.11,segs=12,rings=10)
        eye.scale=(1.0,0.52,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(eye,mats['bio']); link(col,eye); objs.append(eye)
        iris=prim('cyl',f'CT_Iris_{side}',loc=(sx,ey2+0.09,ez2),size=0.070,depth=0.014,verts=14,rot=(math.radians(90),0,0))
        assign_mat(iris,mats['coral']); link(col,iris); objs.append(iris)
        pupil=prim('cyl',f'CT_Pupil_{side}',loc=(sx,ey2+0.11,ez2),size=0.035,depth=0.010,verts=10,rot=(math.radians(90),0,0))
        assign_mat(pupil,mats['stone']); link(col,pupil); objs.append(pupil)
        # Coral ridge brow
        brow=prim('cone',f'CT_EyeCoral_{side}',loc=(sx,ey2-0.06,ez2+0.14),r1=0.050,r2=0.012,depth=0.18,verts=5,
                  rot=(math.radians(-20),0,math.radians(sx*30)))
        assign_mat(brow,mats['coral']); link(col,brow); objs.append(brow)

    # Mouth slit + 6 rocky teeth
    mouth=prim('cyl','CT_Mouth',loc=(0,0.50,4.40),size=0.36,depth=0.035,verts=20,rot=(math.radians(90),0,0))
    mouth.scale=(1.0,1.0,0.30); bpy.ops.object.transform_apply(scale=True)
    assign_mat(mouth,mats['stone']); link(col,mouth); objs.append(mouth)
    chin=prim('sphere','CT_Chin',loc=(0,0.48,4.24),size=0.18,segs=12,rings=8)
    chin.scale=(1.0,0.60,0.55); bpy.ops.object.transform_apply(scale=True)
    assign_mat(chin,mats['stone']); link(col,chin); objs.append(chin)
    for ti2 in range(6):
        ta2=math.radians(-25+ti2*10); tx2=0.30*math.sin(ta2)
        tooth=prim('cube',f'CT_Tooth_{ti2}',loc=(tx2,0.52,4.38),size=0.08)
        tooth.scale=(0.55,0.30,0.70); bpy.ops.object.transform_apply(scale=True)
        assign_mat(tooth,mats['barnacle']); link(col,tooth); objs.append(tooth)

    # Anemone crown (ring base + 20 tentacles)
    anbase=prim('torus','CT_AnemoneBase',loc=(0,0,5.20),major=0.38,minor=0.065,maj_seg=24,min_seg=10)
    assign_mat(anbase,mats['anemone']); link(col,anbase); objs.append(anbase)
    for ani in range(20):
        ana=math.radians(ani*18); anr=0.32+rng.uniform(-0.06,0.10)
        anx=anr*math.cos(ana); any2=anr*math.sin(ana)
        anlen=rng.uniform(0.25,0.65)
        ant=prim('cone',f'CT_AnemoneTentacle_{ani}',loc=(anx,any2,5.22+anlen*0.5),r1=0.020,r2=0.006,depth=anlen,verts=6,
                 rot=(rng.uniform(-0.3,0.3),rng.uniform(-0.3,0.3),ana))
        assign_mat(ant,mats['anemone']); link(col,ant); objs.append(ant)
        # Glow tip on longer tentacles
        if anlen>0.45:
            atip=prim('sphere',f'CT_AnemoneGlow_{ani}',loc=(anx,any2,5.22+anlen),size=0.025,segs=6,rings=4)
            assign_mat(atip,mats['bio']); link(col,atip); objs.append(atip)
    return objs

def build_arms(mats, col):
    """Massive armoured arm pillars with coral elbows, anchor weapons."""
    objs=[]
    for side,sx in [('L',-1),('R',1)]:
        sh=(sx*1.18,0,3.70); elbow=(sx*1.90,0,2.90); wrist=(sx*2.55,0,2.10); fist=(sx*2.80,0,1.78)
        # Shoulder sphere
        sj=prim('sphere',f'CT_ShoulderJoint_{side}',loc=sh,size=0.38,segs=16,rings=12)
        assign_mat(sj,mats['stone']); add_sub(sj,1); smart_uv(sj); link(col,sj); objs.append(sj)
        # Coral on shoulder
        for sci in range(4):
            sca=math.radians(sci*90+22)
            sc=prim('cone',f'CT_ShoulderCoral_{side}_{sci}',loc=(sh[0]+0.32*math.cos(sca),sh[1]+0.32*math.sin(sca),sh[2]+0.10),
                    r1=0.040,r2=0.010,depth=0.22,verts=5,rot=(rng.uniform(-0.3,0.3),rng.uniform(-0.3,0.3),sca))
            assign_mat(sc,mats['coral']); link(col,sc); objs.append(sc)
        # Upper arm
        ua=seg_obj(f'CT_ArmUpper_{side}',sh,elbow,0.28,mats['stone'],col,verts=14); objs.append(ua)
        # Elbow cluster (4 coral spikes)
        ej=prim('sphere',f'CT_ElbowJoint_{side}',loc=elbow,size=0.32,segs=14,rings=12)
        assign_mat(ej,mats['stone']); add_sub(ej,1); link(col,ej); objs.append(ej)
        for eci in range(4):
            eca=math.radians(eci*90); ecr=0.32
            esp=prim('cone',f'CT_CoralElbowSpike_{side}_{eci}',loc=(elbow[0]+ecr*math.cos(eca),elbow[1]+ecr*math.sin(eca),elbow[2]),
                     r1=0.038,r2=0.008,depth=0.28,verts=5,rot=(rng.uniform(-0.4,0.4),rng.uniform(-0.3,0.3),eca))
            assign_mat(esp,mats['coral']); link(col,esp); objs.append(esp)
        # Lower arm
        la=seg_obj(f'CT_ArmLower_{side}',elbow,wrist,0.22,mats['stone'],col,verts=12); objs.append(la)
        # Fist rock
        fist_s=prim('sphere',f'CT_Fist_{side}',loc=fist,size=0.42,segs=16,rings=12)
        fist_s.scale=(1.0,1.0,0.82); bpy.ops.object.transform_apply(scale=True)
        assign_mat(fist_s,mats['stone']); add_sub(fist_s,1); smart_uv(fist_s); link(col,fist_s); objs.append(fist_s)

        # Giant anchor weapon
        anch_loc=(fist[0]+sx*0.10,fist[1],fist[2]-0.30)
        # Anchor ring
        anchor_ring=prim('torus',f'CT_AnchorRing_{side}',loc=(anch_loc[0],anch_loc[1],anch_loc[2]+0.55),major=0.20,minor=0.045,maj_seg=20,min_seg=8)
        assign_mat(anchor_ring,mats['iron']); link(col,anchor_ring); objs.append(anchor_ring)
        # Anchor shaft
        anchor_shaft=seg_obj(f'CT_AnchorShaft_{side}',(anch_loc[0],anch_loc[1],anch_loc[2]+0.45),(anch_loc[0],anch_loc[1],anch_loc[2]-0.60),0.065,mats['iron'],col,verts=10); objs.append(anchor_shaft)
        # Anchor cross bar
        cbar=prim('cyl',f'CT_AnchorCrossbar_{side}',loc=(anch_loc[0],anch_loc[1],anch_loc[2]+0.22),size=0.040,depth=0.68,verts=8,rot=(0,math.radians(90),0))
        assign_mat(cbar,mats['iron']); link(col,cbar); objs.append(cbar)
        # Anchor flukes (2 arms)
        for fli,flsx in enumerate([-1,1]):
            fluke=prim('cone',f'CT_AnchorFluke_{side}_{fli}',loc=(anch_loc[0]+flsx*0.22,anch_loc[1],anch_loc[2]-0.55),
                       r1=0.050,r2=0.012,depth=0.26,verts=4,rot=(math.radians(flsx*45),0,0))
            assign_mat(fluke,mats['iron']); link(col,fluke); objs.append(fluke)

        # Anchor chain links on arm
        for cli in range(6):
            cly=cli*0.10-0.25
            cl=prim('torus',f'CT_AnchorChain_{side}_{cli}',loc=(elbow[0],elbow[1],elbow[2]+0.12+cli*0.12),major=0.055,minor=0.018,maj_seg=12,min_seg=6,rot=(math.radians(cli*30),0,0))
            assign_mat(cl,mats['iron']); link(col,cl); objs.append(cl)
    return objs

def build_legs(mats, col):
    """Massive pillar legs with knee coral clusters and foot spikes."""
    objs=[]
    for side,sx in [('L',-1),('R',1)]:
        hip=(sx*0.68,0,1.58); knee=(sx*0.72,0,0.82); ankle=(sx*0.68,0,0.24); foot=(sx*0.72,0.32,0.10)
        hj=prim('sphere',f'CT_HipJoint_{side}',loc=hip,size=0.38,segs=14,rings=12)
        assign_mat(hj,mats['stone']); add_sub(hj,1); link(col,hj); objs.append(hj)
        thigh=seg_obj(f'CT_Thigh_{side}',hip,knee,0.32,mats['stone'],col,verts=14); objs.append(thigh)
        # Knee coral cluster
        kj=prim('sphere',f'CT_KneeJoint_{side}',loc=knee,size=0.35,segs=14,rings=10)
        assign_mat(kj,mats['stone']); add_sub(kj,1); link(col,kj); objs.append(kj)
        for kci in range(5):
            kca=math.radians(kci*72)
            kcs=prim('cone',f'CT_KneeCoral_{side}_{kci}',loc=(knee[0]+0.30*math.cos(kca),knee[1]+0.30*math.sin(kca),knee[2]),
                     r1=0.035,r2=0.008,depth=0.24,verts=5,rot=(rng.uniform(-0.4,0.4),rng.uniform(-0.3,0.3),kca))
            assign_mat(kcs,mats['coral']); link(col,kcs); objs.append(kcs)
        shin=seg_obj(f'CT_Shin_{side}',knee,ankle,0.26,mats['stone'],col,verts=12); objs.append(shin)
        aj=prim('sphere',f'CT_AnkleJoint_{side}',loc=ankle,size=0.28,segs=12,rings=10)
        assign_mat(aj,mats['stone']); link(col,aj); objs.append(aj)
        ft=prim('cyl',f'CT_Foot_{side}',loc=foot,size=0.45,depth=0.18,verts=14)
        ft.scale=(1.0,1.80,0.55); bpy.ops.object.transform_apply(scale=True)
        assign_mat(ft,mats['stone']); add_sub(ft,1); smart_uv(ft); link(col,ft); objs.append(ft)
        # 3 coral spikes from foot
        for fsi in range(3):
            fsx2=sx*(0.28+fsi*0.16); fz2=0.12
            fps=prim('cone',f'CT_FootCoralSpike_{side}_{fsi}',loc=(fsx2,0.55,fz2),r1=0.035,r2=0.008,depth=0.28,verts=5,rot=(math.radians(-25),0,0))
            assign_mat(fps,mats['coral']); link(col,fps); objs.append(fps)
    return objs

def build_ship_wreckage(mats, col):
    """Ship planks fused into chest, ribs, ship wheel on left shoulder."""
    objs=[]
    # 10 ship planks embedded in chest
    for pi in range(10):
        pa=math.radians(-40+pi*10)
        px=0.88*math.cos(pa); py=0.88*math.sin(pa)*0.62
        plank=prim('cube',f'CT_ShipPlank_{pi}',loc=(px,py,2.60),size=0.20)
        plank.scale=(0.15,0.04,1.10); plank.rotation_euler=(0,0,pa+math.radians(90))
        bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(plank,mats['wood']); add_bevel(plank,0.008,2); smart_uv(plank); link(col,plank); objs.append(plank)
    # 4 exposed ship ribs
    for ri in range(4):
        rpa=math.radians(-30+ri*22)
        rib_pt1=(0.80*math.cos(rpa),0.80*math.sin(rpa)*0.62,2.20+ri*0.25)
        rib_pt2=(1.08*math.cos(rpa),1.08*math.sin(rpa)*0.62,2.30+ri*0.22)
        rrib=seg_obj(f'CT_ShipRib_{ri}',rib_pt1,rib_pt2,0.030,mats['wood'],col,verts=8); objs.append(rrib)

    # Ship wheel on left shoulder
    wheel=prim('torus','CT_ShipWheel',loc=(-1.30,0,3.95),major=0.42,minor=0.038,maj_seg=28,min_seg=8,rot=(0,math.radians(90),0))
    assign_mat(wheel,mats['wood']); link(col,wheel); objs.append(wheel)
    for wi2 in range(8):
        wa2=math.radians(wi2*45)
        spoke=seg_obj(f'CT_WheelSpoke_{wi2}',(-1.30,0,3.95),(-1.30,0.42*math.sin(wa2),3.95+0.42*math.cos(wa2)),0.018,mats['wood'],col,verts=6)
        objs.append(spoke)
    hub=prim('sphere','CT_WheelHub',loc=(-1.30,0,3.95),size=0.075,segs=10,rings=8)
    assign_mat(hub,mats['iron']); link(col,hub); objs.append(hub)
    return objs

def build_scary_attachments(mats, col):
    """Crab claws, kelp strands, trapped fish skeletons, barnacle patches, coral horns, bubbles, sea stars."""
    objs=[]
    # ── Giant crab claw pauldrons on shoulders ──
    for side,sx in [('L',-1),('R',1)]:
        # Main claw base
        cb=prim('sphere',f'CT_CrabClaw_{side}',loc=(sx*1.30,0,4.12),size=0.30,segs=14,rings=10)
        cb.scale=(1.0,0.62,0.70); bpy.ops.object.transform_apply(scale=True)
        assign_mat(cb,mats['barnacle']); add_sub(cb,1); link(col,cb); objs.append(cb)
        # 2 claw arms
        for cli2,clang in enumerate([-22,22]):
            clx=sx*(1.55+cli2*0.12); clz=4.10+cli2*0.10
            claw=prim('cone',f'CT_CrabClaw_{side}_Arm{cli2}',loc=(clx,0,clz),r1=0.055,r2=0.010,depth=0.40,verts=4,
                      rot=(0,math.radians(sx*clang),0))
            assign_mat(claw,mats['barnacle']); link(col,claw); objs.append(claw)
        # 6 crab legs per shoulder cluster
        for cleg in range(6):
            clega=math.radians(cleg*50-100); clegr=0.28
            clegx=sx*(1.30+clegr*math.cos(clega)); clegz=4.12+clegr*math.sin(clega)
            cl2=prim('cyl',f'CT_CrabLeg_{side}_{cleg}',loc=(clegx,0.12,clegz),size=0.014,depth=0.24,verts=6,rot=(0,math.radians(sx*clega*0.6),0))
            assign_mat(cl2,mats['barnacle']); link(col,cl2); objs.append(cl2)

    # ── 12 kelp/seaweed strands hanging from joints ──
    kelp_attach=[(sx*1.90,0,2.90) for sx in [-1,1]] + [(sx*0.72,0,0.82) for sx in [-1,1]] + \
                [(sx*0.68,0,0.24) for sx in [-1,1]] + [(0,0,1.58),(0,0,4.12),(sx*1.18,0,3.70) for sx in [-1,1]] + [(0,0,2.50),(0,0,3.00)]
    for ki2,kp in enumerate(kelp_attach[:12]):
        for ks in range(2):
            ksa=rng.uniform(0,2*math.pi); ksr=rng.uniform(0.08,0.18)
            ksx2=kp[0]+ksr*math.cos(ksa); ksy2=kp[1]+ksr*math.sin(ksa)
            klen=rng.uniform(0.35,0.80)
            kstrand=prim('cone',f'CT_KelpStrand_{ki2}_{ks}',loc=(ksx2,ksy2,kp[2]-klen*0.5),r1=0.018,r2=0.005,depth=klen,verts=4)
            assign_mat(kstrand,mats['kelp']); link(col,kstrand); objs.append(kstrand)
            # 3 kelp leaf blades per strand
            for kl in range(3):
                klz=kp[2]-klen*(0.25+kl*0.25)
                kleaf=prim('cube',f'CT_KelpLeaf_{ki2}_{ks}_{kl}',loc=(ksx2,ksy2,klz),size=0.06)
                kleaf.scale=(0.04,0.60,0.28); kleaf.rotation_euler=(0,0,rng.uniform(-0.5,0.5))
                bpy.ops.object.transform_apply(scale=True,rotation=True)
                assign_mat(kleaf,mats['kelp']); link(col,kleaf); objs.append(kleaf)

    # ── 4 trapped fish skeleton shapes inside coral body ──
    fish_pos=[(0.50,0.55,3.20),(-.50,0.55,3.20),(0.30,-0.65,2.80),(-.30,-0.65,2.80)]
    for fsi2,(fsx,fsy,fsz) in enumerate(fish_pos):
        # Fish spine
        fspine=prim('cyl',f'CT_FishSpine_{fsi2}',loc=(fsx,fsy,fsz),size=0.012,depth=0.30,verts=6,rot=(0,math.radians(90),0))
        assign_mat(fspine,mats['bone']); link(col,fspine); objs.append(fspine)
        # 4 fish ribs
        for fri2 in range(4):
            frx=fsx-0.08+fri2*0.055
            frb=prim('cyl',f'CT_FishRib_{fsi2}_{fri2}',loc=(frx,fsy,fsz),size=0.006,depth=0.12,verts=4,rot=(math.radians(75),0,0))
            assign_mat(frb,mats['bone']); link(col,frb); objs.append(frb)
        # Fish skull
        fsk2=prim('sphere',f'CT_FishSkull_{fsi2}',loc=(fsx+0.18,fsy,fsz),size=0.048,segs=8,rings=6)
        fsk2.scale=(1.20,0.85,0.85); bpy.ops.object.transform_apply(scale=True)
        assign_mat(fsk2,mats['bone']); link(col,fsk2); objs.append(fsk2)

    # ── 14 barnacle patches scattered on body ──
    barn_pat_pos=[
        ( 1.05, 0.30,3.40),(-1.05, 0.30,3.40),( 1.02,-0.45,2.80),(-1.02,-0.45,2.80),
        ( 0.88, 0.70,2.20),(-0.88, 0.70,2.20),( 0.80,-0.80,1.90),(-0.80,-0.80,1.90),
        ( 0.55, 0.85,3.80),(-0.55, 0.85,3.80),( 0.42,-0.90,3.50),(-0.42,-0.90,3.50),
        ( 0, 0.92,2.60),( 0,-0.92,2.60),
    ]
    for bpi2,(bpx,bpy2,bpz) in enumerate(barn_pat_pos):
        for bki2 in range(5):
            bba=math.radians(bki2*72+rng.uniform(-15,15))
            bbr=rng.uniform(0.04,0.09)
            bbx=bpx+bbr*math.cos(bba); bby2=bpy2+bbr*math.sin(bba)
            bb=prim('cone',f'CT_Barnacle_{bpi2}_{bki2}',loc=(bbx,bby2,bpz),r1=0.022,r2=0.006,depth=0.050,verts=8)
            assign_mat(bb,mats['barnacle']); link(col,bb); objs.append(bb)

    # ── 14 large coral spike horns on shoulders and back ──
    horn_pos=[
        (-1.30, 0, 3.80, -0.5, 0.2),( 1.30, 0, 3.80,  0.5, 0.2),
        (-1.20, 0, 3.50, -0.4, 0.3),( 1.20, 0, 3.50,  0.4, 0.3),
        (-1.10,-0.50,3.20,-0.3,-0.4),( 1.10,-0.50,3.20, 0.3,-0.4),
        ( 0,-1.12,3.60, 0.0,-0.5),( 0,-1.08,3.00, 0.0,-0.5),
        (-0.85,-0.85,2.80,-0.3,-0.5),( 0.85,-0.85,2.80, 0.3,-0.5),
        (-0.70,-0.90,2.20,-0.2,-0.5),( 0.70,-0.90,2.20, 0.2,-0.5),
        ( 0,-1.04,1.80, 0.0,-0.5),( 0,-0.95,1.40, 0.0,-0.5),
    ]
    for hni,(hnx,hny,hnz,hrx,hry) in enumerate(horn_pos):
        horn=prim('cone',f'CT_CoralHorn_{hni}',loc=(hnx,hny,hnz),r1=rng.uniform(0.050,0.090),r2=0.010,depth=rng.uniform(0.35,0.65),verts=5,
                  rot=(hrx,hry,math.radians(hni*25)))
        assign_mat(horn,mats['coral']); link(col,horn); objs.append(horn)
        # Horn sub-branch
        hbr=prim('cone',f'CT_CoralHornSub_{hni}',loc=(hnx+rng.uniform(-0.10,0.10),hny,hnz+0.20),r1=0.025,r2=0.005,depth=rng.uniform(0.14,0.22),verts=5,
                 rot=(hrx+rng.uniform(-0.4,0.4),hry+rng.uniform(-0.3,0.3),0))
        assign_mat(hbr,mats['coral']); link(col,hbr); objs.append(hbr)

    # ── 8 bubble cluster spheres rising from body ──
    for bui in range(8):
        bua=math.radians(bui*45); bur=rng.uniform(0.75,1.20)
        bux=bur*math.cos(bua); buy=bur*math.sin(bua); buz=rng.uniform(1.50,3.80)
        for busi in range(3):
            bs=prim('sphere',f'CT_Bubble_{bui}_{busi}',loc=(bux+rng.uniform(-0.06,0.06),buy,buz+busi*0.12),size=rng.uniform(0.022,0.055),segs=6,rings=4)
            assign_mat(bs,mats['bio']); link(col,bs); objs.append(bs)

    # ── 5 sea star shapes adhered to body ──
    ss_pos=[(0.88,0.22,2.88),(-.88,0.22,2.88),(0.60,-0.72,3.30),(-.60,-0.72,3.30),(0,0.92,2.10)]
    for ssi,(ssx,ssy,ssz) in enumerate(ss_pos):
        for sspi in range(5):
            sspa=math.radians(sspi*72+rng.uniform(-5,5))
            sspr=rng.uniform(0.08,0.12)
            sspx=ssx+sspr*math.cos(sspa); sspy=ssy+sspr*math.sin(sspa)
            ssparm=prim('cone',f'CT_SeaStar_{ssi}_Arm{sspi}',loc=(sspx,sspy,ssz),r1=0.018,r2=0.005,depth=rng.uniform(0.10,0.16),verts=4,
                        rot=(math.radians(90),0,sspa))
            assign_mat(ssparm,mats['coral']); link(col,ssparm); objs.append(ssparm)
        # Sea star centre
        ssctr=prim('sphere',f'CT_SeaStar_{ssi}_Ctr',loc=(ssx,ssy,ssz),size=0.030,segs=6,rings=4)
        assign_mat(ssctr,mats['barnacle']); link(col,ssctr); objs.append(ssctr)
    return objs

# ═══════════════════════════════════════════════════════════════════
#  ASSEMBLE
# ═══════════════════════════════════════════════════════════════════

def main():
    clear_scene()
    col=new_col('IsleTrial_Boss_CoralTitan')
    mats=build_materials()
    all_objs=[]
    all_objs+=build_body(mats,col)
    all_objs+=build_head(mats,col)
    all_objs+=build_arms(mats,col)
    all_objs+=build_legs(mats,col)
    all_objs+=build_ship_wreckage(mats,col)
    all_objs+=build_scary_attachments(mats,col)
    bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0))
    root=bpy.context.active_object; root.name='Boss_CoralTitan_ROOT'; link(col,root)
    for obj in all_objs:
        if obj.parent is None: obj.parent=root
    mc=sum(1 for o in col.objects if o.type=='MESH')
    print("="*60)
    print("[IsleTrial] Boss: Ancient Coral Titan – MAXIMUM DETAIL")
    print(f"  Mesh objects : {mc}")
    print(f"  Materials    : {len(bpy.data.materials)}")
    print("  Coral growths: 22 on torso + 12 on head + 14 horns")
    print("  Scary adds   : giant crab claws, 12 kelp strands,")
    print("                 4 trapped fish skeletons, 14 barnacle patches,")
    print("                 8 bubble clusters, 5 sea stars, ship wreckage")
    print("  Next: run 14_Boss_CoralTitan_Rig.py")
    print("="*60)

main()
