"""
IsleTrial – Boss 02: Grand Navigator  (FULL REBUILD – MAXIMUM DETAIL)
======================================================================
Height  ~3.5 m  Ancient clockwork compass-head navigation golem.
Theme   Multi-ring compass head with spinning inner gyroscope,
        heavy iron & brass armoured torso, exposed clock-face
        chest window showing gears, 4 arms (2 primary claw arms +
        2 instrument arms), 3-ring orrery on back, steam vents,
        chained prisoner cages, skeleton crew crew decorations,
        targeting eye with red laser geometry, dangling skulls.

Mesh Objects Built:
  HEAD / COMPASS
    GN_CompassOuter       – bmesh outer bezel ring (thick iron)
    GN_CompassInner_*     – 3 concentric inner rings (brass, decreasing)
    GN_CompassFace        – flat disc face with engraved lines
    GN_CompassNeedle_N/S  – two crossed compass needles
    GN_CompassRose        – 8-point star rose overlay
    GN_TargetEye          – single mechanical targeting eye sphere + red laser rod
    GN_TargetEyeRing      – rotating ring around targeting eye
    GN_EyeSlit_*          – 4 slit openings on compass face
    GN_GyroPivot_L/R      – side pivot pin spheres

  TORSO
    GN_Torso              – bmesh heavy barrel torso with armour plating indent
    GN_ChestWindow        – clock-face porthole (glass + exposed gears)
    GN_Gear_*             – 6 visible gears inside chest window (bmesh teeth)
    GN_ArmourPlate_*      – 8 raised iron plate segments riveted to torso
    GN_Rivet_*            – 24 brass rivet spheres
    GN_SteamVent_*        – 4 exhaust vent pipes with steam cap
    GN_SteamPuff_*        – steam cloud sphere at each vent exit

  ORRERY BACK
    GN_OrreryRing_*       – 3 armillary sphere rings (outer / mid / inner)
    GN_OrrerySphere       – central planet sphere
    GN_OrreryPivot_*      – pivot rods connecting rings

  ARMS (×4)
    GN_ArmUpper_*/Lower_* – heavy plated limbs
    GN_Elbow_*/Wrist_*    – gear-joint spheres
    GN_ClawFinger_*       – 3 iron claw fingers each primary arm
    GN_Sextant_*/GN_Telescope_* – instruments in secondary arms

  LEGS
    GN_Thigh_*/Shin_*/Foot_* – armoured pillar legs with gear knees

  SCARY ATTACHMENTS
    GN_PrisonerCage_*     – 2 iron prisoner cages hanging from belt (with skulls inside)
    GN_ChainLoop_*        – 12 chain link loops forming cage/belt chains
    GN_SkeletonCrew_*     – 3 smaller skeleton decorations dangling from shoulders
    GN_NavigationSpike_*  – 6 map-spike weapons erupting from knuckles
    GN_MapStreamer_*       – 4 torn map parchment strips wrapped around body
    GN_AnchorHook_*       – 2 ship anchor hooks as belt trophies
    GN_SkullCollection_*  – 5 skulls mounted on trophy rack on back

Materials (full dual-path procedural + [UNITY] image slots):
  Mat_GN_Iron          – dark scored iron + Voronoi dents + scratch lines
  Mat_GN_Brass         – warm gold-brass + Musgrave + metallic specular
  Mat_GN_Glass         – near-transparent clock window + refraction
  Mat_GN_Bone          – aged ivory SSS
  Mat_GN_Steam         – near-white translucent vapour
  Mat_GN_Parchment     – yellowed paper + wave line detail
  Mat_GN_RedLaser      – emissive red laser target
  Mat_GN_Gold_Accent   – polished gold trophy medal accent

Run BEFORE 11_Boss_GrandNavigator_Rig.py
"""

import bpy, bmesh, math, random
from mathutils import Vector

rng = random.Random(77)

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

def add_bevel(obj,w=0.012,s=2):
    m=obj.modifiers.new('Bev','BEVEL'); m.width=w; m.segments=s; m.profile=0.5

def add_solidify(obj,t=0.04):
    m=obj.modifiers.new('Solid','SOLIDIFY'); m.thickness=t; m.offset=0.0

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

def gear_wheel(name,loc,outer_r,inner_r,teeth,thickness,mat,col,rot=(0,0,0)):
    """bmesh gear wheel with properly shaped teeth."""
    bm=bmesh.new()
    verts_outer=[]; verts_inner=[]
    for i in range(teeth*4):
        a=2*math.pi*i/(teeth*4)
        t_frac=(i%4)/4.0
        r=outer_r if t_frac<0.5 else inner_r+(outer_r-inner_r)*0.3
        verts_outer.append(bm.verts.new(Vector((r*math.cos(a),r*math.sin(a),thickness*0.5))))
        verts_inner.append(bm.verts.new(Vector((inner_r*0.55*math.cos(a),inner_r*0.55*math.sin(a),thickness*0.5))))
    # Top face fan
    n=len(verts_outer)
    for i in range(n):
        try: bm.faces.new([verts_outer[i],verts_outer[(i+1)%n],verts_inner[(i+1)%n],verts_inner[i]])
        except: pass
    # Mirror bottom
    bottom_o=[bm.verts.new(Vector((v.co.x,v.co.y,-thickness*0.5))) for v in verts_outer]
    bottom_i=[bm.verts.new(Vector((v.co.x,v.co.y,-thickness*0.5))) for v in verts_inner]
    for i in range(n):
        try: bm.faces.new([bottom_o[(i+1)%n],bottom_o[i],bottom_i[i],bottom_i[(i+1)%n]])
        except: pass
    # Side walls
    for i in range(n):
        try:
            bm.faces.new([verts_outer[i],bottom_o[i],bottom_o[(i+1)%n],verts_outer[(i+1)%n]])
            bm.faces.new([verts_inner[(i+1)%n],bottom_i[(i+1)%n],bottom_i[i],verts_inner[i]])
        except: pass
    mesh=bpy.data.meshes.new(f'{name}_Mesh'); bm.to_mesh(mesh); bm.free()
    obj=bpy.data.objects.new(name,mesh); obj.location=loc; obj.rotation_euler=rot
    bpy.context.scene.collection.objects.link(obj)
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

def _mapping(nodes,links,scale=(5,5,5),loc=(-900,0)):
    tc=_n(nodes,'ShaderNodeTexCoord',(loc[0]-200,loc[1]))
    mp=_n(nodes,'ShaderNodeMapping',loc)
    mp.inputs['Scale'].default_value=(*scale,)
    links.new(tc.outputs['UV'],mp.inputs['Vector']); return mp

def _mix_pi(nodes,links,proc,img_nd,loc):
    mix=_n(nodes,'ShaderNodeMixRGB',loc); mix.blend_type='MIX'; mix.inputs[0].default_value=0.0
    links.new(proc,mix.inputs[1]); links.new(img_nd.outputs['Color'],mix.inputs[2]); return mix

def _bump_n(nodes,links,mp,scale=24.0,strength=0.38,loc=(-400,-400)):
    bn=_n(nodes,'ShaderNodeTexNoise',loc)
    bn.inputs['Scale'].default_value=scale; bn.inputs['Detail'].default_value=10.0
    links.new(mp.outputs['Vector'],bn.inputs['Vector'])
    img_n=_img(nodes,'_NormalMap',(loc[0],loc[1]-180))
    mix_n=_mix_pi(nodes,links,bn.outputs['Fac'],img_n,(loc[0]+260,loc[1]-90))
    bmp=_n(nodes,'ShaderNodeBump',(loc[0]+480,loc[1]-90))
    bmp.inputs['Strength'].default_value=strength
    links.new(mix_n.outputs['Color'],bmp.inputs['Height']); return bmp

def _base(name):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    n=mat.node_tree.nodes; lk=mat.node_tree.links; n.clear()
    bsdf=_n(n,'ShaderNodeBsdfPrincipled',(700,0))
    out=_n(n,'ShaderNodeOutputMaterial',(1000,0))
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface']); return mat,n,lk,bsdf

def mat_iron(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(5,5,5))
    musg=_n(n,'ShaderNodeTexMusgrave',(-700,300)); musg.musgrave_type='FBM'
    musg.inputs['Scale'].default_value=8.0; musg.inputs['Detail'].default_value=10.0
    lk.new(mp.outputs['Vector'],musg.inputs['Vector'])
    vor=_n(n,'ShaderNodeTexVoronoi',(-700,100)); vor.feature='DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value=14.0; lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-700,-100)); noise.inputs['Scale'].default_value=28.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mix_mv=_n(n,'ShaderNodeMixRGB',(-400,200)); mix_mv.blend_type='MULTIPLY'; mix_mv.inputs[0].default_value=0.58
    lk.new(musg.outputs['Fac'],mix_mv.inputs[1]); lk.new(vor.outputs['Distance'],mix_mv.inputs[2])
    mix_fn=_n(n,'ShaderNodeMixRGB',(-200,150)); mix_fn.blend_type='OVERLAY'; mix_fn.inputs[0].default_value=0.22
    lk.new(mix_mv.outputs['Color'],mix_fn.inputs[1]); lk.new(noise.outputs['Fac'],mix_fn.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(50,200))
    cr.color_ramp.elements[0].color=(0.06,0.06,0.08,1)
    e1=cr.color_ramp.elements.new(0.40); e1.color=(0.14,0.14,0.16,1)
    cr.color_ramp.elements[1].color=(0.24,0.24,0.26,1)
    lk.new(mix_fn.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-700,-250))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(320,120))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    mr=_n(n,'ShaderNodeMapRange',(50,-120))
    mr.inputs['From Min'].default_value=0.2; mr.inputs['From Max'].default_value=0.8
    mr.inputs['To Min'].default_value=0.48; mr.inputs['To Max'].default_value=0.72
    lk.new(noise.outputs['Fac'],mr.inputs['Value']); lk.new(mr.outputs['Result'],bsdf.inputs['Roughness'])
    bsdf.inputs['Metallic'].default_value=0.92
    bmp=_bump_n(n,lk,mp,scale=28.0,strength=0.42); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_brass(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(6,6,6))
    musg=_n(n,'ShaderNodeTexMusgrave',(-600,200)); musg.musgrave_type='RIDGED_MULTIFRACTAL'
    musg.inputs['Scale'].default_value=6.0; musg.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],musg.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-600,0)); noise.inputs['Scale'].default_value=20.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mix_mn=_n(n,'ShaderNodeMixRGB',(-300,100)); mix_mn.blend_type='MULTIPLY'; mix_mn.inputs[0].default_value=0.45
    lk.new(musg.outputs['Fac'],mix_mn.inputs[1]); lk.new(noise.outputs['Fac'],mix_mn.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.42,0.28,0.05,1)
    e1=cr.color_ramp.elements.new(0.45); e1.color=(0.65,0.46,0.10,1)
    cr.color_ramp.elements[1].color=(0.80,0.62,0.18,1)
    lk.new(mix_mn.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-600,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value=0.95
    mr=_n(n,'ShaderNodeMapRange',(50,-100))
    mr.inputs['From Min'].default_value=0.2; mr.inputs['From Max'].default_value=0.8
    mr.inputs['To Min'].default_value=0.18; mr.inputs['To Max'].default_value=0.38
    lk.new(noise.outputs['Fac'],mr.inputs['Value']); lk.new(mr.outputs['Result'],bsdf.inputs['Roughness'])
    bmp=_bump_n(n,lk,mp,scale=22.0,strength=0.28); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_glass(name):
    mat,n,lk,bsdf=_base(name)
    bsdf.inputs['Base Color'].default_value=(0.60,0.72,0.65,1)
    bsdf.inputs['Roughness'].default_value=0.04
    bsdf.inputs['Transmission Weight'].default_value=0.82
    bsdf.inputs['Alpha'].default_value=0.28; mat.blend_method='BLEND'
    bsdf.inputs['IOR'].default_value=1.52
    return mat

def mat_bone(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(8,8,8))
    noise=_n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=18.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.62,0.58,0.46,1)
    cr.color_ramp.elements[1].color=(0.84,0.80,0.68,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-400,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.62
    bsdf.inputs['Subsurface Weight'].default_value=0.04
    bsdf.inputs['Subsurface Radius'].default_value=(0.88,0.76,0.58)
    return mat

def mat_steam(name):
    mat,n,lk,bsdf=_base(name)
    noise=_n(n,'ShaderNodeTexNoise',(-300,100)); noise.inputs['Scale'].default_value=8.0
    cr=_n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.72,0.72,0.72,1)
    cr.color_ramp.elements[1].color=(0.96,0.96,0.96,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.92
    bsdf.inputs['Alpha'].default_value=0.42; mat.blend_method='BLEND'
    return mat

def mat_parchment(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(10,10,10))
    wave=_n(n,'ShaderNodeTexWave',(-500,200)); wave.wave_type='BANDS'
    wave.inputs['Scale'].default_value=6.0; wave.inputs['Distortion'].default_value=1.5
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-500,0)); noise.inputs['Scale'].default_value=20.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mix_wn=_n(n,'ShaderNodeMixRGB',(-250,100)); mix_wn.blend_type='MULTIPLY'; mix_wn.inputs[0].default_value=0.30
    lk.new(wave.outputs['Color'],mix_wn.inputs[1]); lk.new(noise.outputs['Fac'],mix_wn.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.62,0.54,0.32,1)
    cr.color_ramp.elements[1].color=(0.86,0.78,0.54,1)
    lk.new(mix_wn.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-500,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.84
    return mat

def mat_red_laser(name):
    mat,n,lk,bsdf=_base(name)
    bsdf.inputs['Base Color'].default_value=(1.0,0.02,0.02,1)
    bsdf.inputs['Emission Color'].default_value=(1.0,0.02,0.02,1)
    bsdf.inputs['Emission Strength'].default_value=5.0
    bsdf.inputs['Roughness'].default_value=0.05
    return mat

def mat_gold_accent(name):
    mat,n,lk,bsdf=_base(name)
    bsdf.inputs['Base Color'].default_value=(0.88,0.72,0.12,1)
    bsdf.inputs['Metallic'].default_value=1.0
    bsdf.inputs['Roughness'].default_value=0.10
    bsdf.inputs['Specular IOR Level'].default_value=1.0
    return mat

def build_materials():
    return {
        'iron'    : mat_iron('Mat_GN_Iron'),
        'brass'   : mat_brass('Mat_GN_Brass'),
        'glass'   : mat_glass('Mat_GN_Glass'),
        'bone'    : mat_bone('Mat_GN_Bone'),
        'steam'   : mat_steam('Mat_GN_Steam'),
        'parch'   : mat_parchment('Mat_GN_Parchment'),
        'laser'   : mat_red_laser('Mat_GN_RedLaser'),
        'gold'    : mat_gold_accent('Mat_GN_GoldAccent'),
    }

# ═══════════════════════════════════════════════════════════════════
#  GEOMETRY
# ═══════════════════════════════════════════════════════════════════

def build_compass_head(mats, col):
    """Multi-ring compass head with gyroscope rings, targeting eye, slit openings."""
    objs=[]
    HZ=3.20   # head centre Z

    # Outer bezel ring (thick iron)
    bz=prim('torus','GN_CompassOuter',loc=(0,0,HZ),major=0.62,minor=0.110,maj_seg=36,min_seg=14)
    assign_mat(bz,mats['iron']); add_bevel(bz,0.015,2); smart_uv(bz); link(col,bz); objs.append(bz)

    # 3 concentric inner rings (brass, decreasing)
    ring_radii=[0.50,0.36,0.22]; ring_minors=[0.040,0.032,0.025]
    for ri,(rr,rm) in enumerate(zip(ring_radii,ring_minors)):
        rg=prim('torus',f'GN_CompassInner_{ri}',loc=(0,0,HZ),major=rr,minor=rm,maj_seg=32,min_seg=10,
                rot=(0,math.radians(30*ri),math.radians(22*ri)))
        assign_mat(rg,mats['brass']); smart_uv(rg); link(col,rg); objs.append(rg)

    # Compass face disc
    face=prim('cyl','GN_CompassFace',loc=(0,0.55,HZ),size=0.55,depth=0.035,verts=36,rot=(math.radians(90),0,0))
    assign_mat(face,mats['iron']); add_bevel(face,0.008,2); smart_uv(face); link(col,face); objs.append(face)

    # Compass needle N (long)
    needle_n=prim('cone','GN_CompassNeedle_N',loc=(0,0.56,HZ+0.22),r1=0.028,r2=0.004,depth=0.44,verts=6)
    assign_mat(needle_n,mats['brass']); link(col,needle_n); objs.append(needle_n)
    # Compass needle S (short, opposite)
    needle_s=prim('cone','GN_CompassNeedle_S',loc=(0,0.56,HZ-0.20),r1=0.022,r2=0.004,depth=0.36,verts=6,rot=(math.radians(180),0,0))
    assign_mat(needle_s,mats['iron']); link(col,needle_s); objs.append(needle_s)

    # 8-point compass rose overlay (8 triangular points)
    for rpi in range(8):
        rpa=math.radians(rpi*45)
        rpx=0.34*math.sin(rpa); rpz=HZ+0.34*math.cos(rpa)
        rpo=prim('cone',f'GN_CompassRose_{rpi}',loc=(rpx,0.57,rpz),r1=0.025,r2=0.004,depth=0.14,verts=3,
                 rot=(math.radians(90),rpa,0))
        assign_mat(rpo,mats['gold']); link(col,rpo); objs.append(rpo)

    # Targeting eye (mechanical single eye sphere)
    tge=prim('sphere','GN_TargetEye',loc=(0,0.62,HZ+0.08),size=0.10,segs=16,rings=12)
    tge.scale=(1.0,0.58,1.0); bpy.ops.object.transform_apply(scale=True)
    assign_mat(tge,mats['glass']); link(col,tge); objs.append(tge)
    # Red iris ring
    tgi=prim('torus','GN_TargetIris',loc=(0,0.65,HZ+0.08),major=0.06,minor=0.014,maj_seg=18,min_seg=6,rot=(math.radians(90),0,0))
    assign_mat(tgi,mats['laser']); link(col,tgi); objs.append(tgi)
    # Red laser rod (targeting beam)
    laser=prim('cyl','GN_TargetLaser',loc=(0,1.10,HZ+0.08),size=0.004,depth=1.20,verts=6,rot=(math.radians(90),0,0))
    assign_mat(laser,mats['laser']); link(col,laser); objs.append(laser)
    # Rotating ring around targeting eye
    ter=prim('torus','GN_TargetEyeRing',loc=(0,0.62,HZ+0.08),major=0.13,minor=0.018,maj_seg=24,min_seg=8,rot=(math.radians(90),0,0))
    assign_mat(ter,mats['brass']); link(col,ter); objs.append(ter)

    # 4 slit openings (mechanical eye slits on compass face)
    for si in range(4):
        sa=math.radians(si*90+45); sr=0.30
        sx=sr*math.sin(sa); sz=HZ+sr*math.cos(sa)
        slt=prim('cyl',f'GN_EyeSlit_{si}',loc=(sx,0.54,sz),size=0.025,depth=0.045,verts=6,
                 rot=(math.radians(90),sa,0))
        slt.scale=(0.30,1.0,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(slt,mats['iron']); link(col,slt); objs.append(slt)

    # Side gyro pivot pins
    for side,sx in [('L',-1),('R',1)]:
        gp=prim('cyl',f'GN_GyroPivot_{side}',loc=(sx*0.65,0,HZ),size=0.055,depth=0.18,verts=8,rot=(0,math.radians(90),0))
        assign_mat(gp,mats['brass']); link(col,gp); objs.append(gp)
        gph=prim('sphere',f'GN_GyroPivotHead_{side}',loc=(sx*0.76,0,HZ),size=0.070,segs=10,rings=8)
        assign_mat(gph,mats['iron']); link(col,gph); objs.append(gph)
    return objs

def build_torso(mats, col):
    """bmesh barrel torso with armour plating, chest window, gears, rivets, steam vents."""
    objs=[]
    bm=bmesh.new(); segs=28; rings=20; W=0.72; H=1.20
    verts_grid=[]
    for ri in range(rings+1):
        t=ri/rings; y=-H+t*2*H
        if t<0.10:   w=W*(t/0.10)*0.60
        elif t<0.45: w=W*(0.60+(t-0.10)/0.35*0.40)
        elif t<0.65: w=W*1.0
        elif t<0.85: w=W*(1.0-(t-0.65)/0.20*0.15)
        else:        w=W*(0.85-(t-0.85)/0.15*0.20)
        h=H*0.78 if t<0.50 else H*(0.78+(t-0.50)*0.44)
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
    mesh=bpy.data.meshes.new('GN_Torso_Mesh'); bm.to_mesh(mesh); bm.free()
    torso=bpy.data.objects.new('GN_Torso',mesh); torso.location=(0,0,2.00)
    bpy.context.scene.collection.objects.link(torso)
    assign_mat(torso,mats['iron']); add_sub(torso,2); smart_uv(torso); link(col,torso); objs.append(torso)

    # Chest clock window (round porthole)
    cw=prim('cyl','GN_ChestWindow',loc=(0,0.68,2.15),size=0.30,depth=0.055,verts=24,rot=(math.radians(90),0,0))
    assign_mat(cw,mats['glass']); link(col,cw); objs.append(cw)
    cw_frame=prim('torus','GN_ChestWindowFrame',loc=(0,0.66,2.15),major=0.32,minor=0.028,maj_seg=24,min_seg=8,rot=(math.radians(90),0,0))
    assign_mat(cw_frame,mats['brass']); link(col,cw_frame); objs.append(cw_frame)

    # 6 visible gears inside chest (using gear_wheel helper)
    gear_configs=[
        ('GN_Gear_Main',  (0,0.64,2.20),  0.18,0.13,18,0.028),
        ('GN_Gear_Left',  (-0.14,0.64,2.10),0.12,0.08,14,0.022),
        ('GN_Gear_Right', ( 0.14,0.64,2.10),0.12,0.08,14,0.022),
        ('GN_Gear_Top',   (0,0.64,2.34),   0.10,0.06,12,0.018),
        ('GN_Gear_SmL',   (-0.08,0.64,2.00),0.06,0.04,8,0.014),
        ('GN_Gear_SmR',   ( 0.08,0.64,2.00),0.06,0.04,8,0.014),
    ]
    for gname,gloc,gr_o,gr_i,gteeth,gth in gear_configs:
        g=gear_wheel(gname,gloc,gr_o,gr_i,gteeth,gth,mats['brass'],col,rot=(math.radians(90),0,0))
        objs.append(g)

    # 8 armour plate segments riveted to torso
    plate_pos=[
        (0.68,0,2.40),(-.68,0,2.40),(0.68,0,1.80),(-.68,0,1.80),
        (0,0.68,2.40),(0,-.68,2.40),(0,0.68,1.80),(0,-.68,1.80),
    ]
    for i,(px,py,pz) in enumerate(plate_pos):
        pl=prim('cube',f'GN_ArmourPlate_{i}',loc=(px,py,pz),size=0.28)
        pl.scale=(0.35,0.14,0.55); bpy.ops.object.transform_apply(scale=True)
        assign_mat(pl,mats['iron']); add_bevel(pl,0.010,2); smart_uv(pl); link(col,pl); objs.append(pl)
        # 3 rivets per plate
        for ri in range(3):
            rv=prim('sphere',f'GN_Rivet_{i}_{ri}',loc=(px,py-0.08,pz+(-0.10+ri*0.10)),size=0.018,segs=6,rings=4)
            assign_mat(rv,mats['brass']); link(col,rv); objs.append(rv)

    # 4 steam exhaust vent pipes
    vent_pos=[(-0.62,-0.42,2.70),(.62,-0.42,2.70),(-0.55,-0.50,1.60),(.55,-0.50,1.60)]
    for i,(vx,vy,vz) in enumerate(vent_pos):
        vp=prim('cyl',f'GN_SteamVent_{i}',loc=(vx,vy,vz),size=0.055,depth=0.38,verts=10,rot=(math.radians(-30+i*5),0,0))
        assign_mat(vp,mats['iron']); smart_uv(vp); link(col,vp); objs.append(vp)
        vc=prim('torus',f'GN_VentCap_{i}',loc=(vx+0.04*math.cos(i),vy-0.18,vz+0.14),major=0.062,minor=0.018,maj_seg=12,min_seg=6)
        assign_mat(vc,mats['brass']); link(col,vc); objs.append(vc)
        sp=prim('sphere',f'GN_SteamPuff_{i}',loc=(vx+0.04,vy-0.30,vz+0.28),size=rng.uniform(0.06,0.10),segs=8,rings=6)
        sp.scale=(1.0,1.0,0.55); bpy.ops.object.transform_apply(scale=True)
        assign_mat(sp,mats['steam']); link(col,sp); objs.append(sp)
    return objs

def build_orrery(mats, col):
    """3-ring armillary sphere gyroscope on back of torso."""
    objs=[]
    oz=2.30; oy=-0.90
    ring_radii=[0.55,0.40,0.28]
    ring_rots=[(0,0,0),(math.radians(60),0,math.radians(30)),(math.radians(30),math.radians(45),0)]
    for ri,(rr,rrot) in enumerate(zip(ring_radii,ring_rots)):
        rg=prim('torus',f'GN_OrreryRing_{ri}',loc=(0,oy,oz),major=rr,minor=0.028-ri*0.005,maj_seg=28,min_seg=8,rot=rrot)
        assign_mat(rg,mats['brass']); link(col,rg); objs.append(rg)
    # Central sphere
    cs=prim('sphere','GN_OrrerySphere',loc=(0,oy,oz),size=0.10,segs=14,rings=10)
    assign_mat(cs,mats['gold']); link(col,cs); objs.append(cs)
    # 3 pivot rods
    for pri in range(3):
        pa=math.radians(pri*60)
        px=0.55*math.cos(pa); pz=oz+0.55*math.sin(pa)
        pro=prim('cyl',f'GN_OrreryPivot_{pri}',loc=(px*0.5,oy,oz+0.55*math.sin(pa)*0.5),size=0.012,depth=0.58,verts=6,rot=(0,pa+math.radians(90),0))
        assign_mat(pro,mats['iron']); link(col,pro); objs.append(pro)
    return objs

def build_arms(mats, col):
    """4 arms: 2 primary claw arms + 2 secondary instrument arms."""
    objs=[]
    arm_defs=[
        ('GN_ArmPri_L', (-0.90,0,2.80), -1, True),
        ('GN_ArmPri_R', ( 0.90,0,2.80),  1, True),
        ('GN_ArmSec_L', (-0.65,0,2.55), -1, False),
        ('GN_ArmSec_R', ( 0.65,0,2.55),  1, False),
    ]
    for prefix,sh,ds,is_claw in arm_defs:
        ur=0.20 if is_claw else 0.14
        elbow=(sh[0]+ds*0.62,sh[1],sh[2]-0.72)
        wrist=(sh[0]+ds*1.24,sh[1],sh[2]-1.42)
        fist =(sh[0]+ds*1.52,sh[1],sh[2]-1.72)
        # Shoulder sphere
        sj=prim('sphere',f'{prefix}_Shoulder',loc=sh,size=ur*1.25,segs=14,rings=10)
        assign_mat(sj,mats['iron']); add_sub(sj,1); link(col,sj); objs.append(sj)
        # Gear ring at shoulder joint
        sg=gear_wheel(f'{prefix}_ShoulderGear',sh,ur*1.32,ur*0.85,12,0.040,mats['brass'],col,rot=(0,math.radians(90),0))
        objs.append(sg)
        # Upper arm
        ua=seg_obj(f'{prefix}_Upper',sh,elbow,ur,mats['iron'],col,verts=12); objs.append(ua)
        # Elbow gear joint
        eg=gear_wheel(f'{prefix}_ElbowGear',elbow,ur*1.28,ur*0.80,10,0.038,mats['brass'],col,rot=(0,math.radians(90),0))
        objs.append(eg)
        # Lower arm
        la=seg_obj(f'{prefix}_Lower',elbow,wrist,ur*0.88,mats['iron'],col,verts=12); objs.append(la)
        # Wrist sphere
        wj=prim('sphere',f'{prefix}_Wrist',loc=wrist,size=ur*1.12,segs=12,rings=8)
        assign_mat(wj,mats['brass']); link(col,wj); objs.append(wj)
        if is_claw:
            # 3 claw fingers
            for fi in range(3):
                fa=math.radians(-16+fi*16)
                fx=fist[0]+ds*math.cos(fa)*0.24; fz=fist[2]+math.sin(fa)*0.10
                claw=prim('cone',f'{prefix}_Claw_{fi}',loc=(fx,fist[1],fz),r1=0.030,r2=0.004,depth=0.30,verts=4,
                          rot=(0,math.radians(ds*(-20+fi*15)),0))
                assign_mat(claw,mats['iron']); link(col,claw); objs.append(claw)
                # Knuckle rivet
                kr=prim('sphere',f'{prefix}_KnuckleRivet_{fi}',loc=(fx,fist[1]-0.06,fz),size=0.018,segs=6,rings=4)
                assign_mat(kr,mats['brass']); link(col,kr); objs.append(kr)
        else:
            # Secondary arm instrument: sextant (L) or telescope (R)
            if ds<0:
                # Sextant frame
                sf=prim('cyl',f'{prefix}_Sextant',loc=fist,size=0.16,depth=0.05,verts=3,rot=(0,0,math.radians(30)))
                sf.scale=(1.0,0.55,1.0); bpy.ops.object.transform_apply(scale=True)
                assign_mat(sf,mats['brass']); link(col,sf); objs.append(sf)
            else:
                # Telescope barrel
                tb=prim('cyl',f'{prefix}_Telescope',loc=(fist[0]+ds*0.18,fist[1],fist[2]),size=0.055,depth=0.44,verts=12,rot=(0,math.radians(90),0))
                assign_mat(tb,mats['brass']); link(col,tb); objs.append(tb)
                # Telescope lens ring
                tl=prim('torus',f'{prefix}_TeleLens',loc=(fist[0]+ds*0.38,fist[1],fist[2]),major=0.060,minor=0.016,maj_seg=16,min_seg=6,rot=(0,math.radians(90),0))
                assign_mat(tl,mats['glass']); link(col,tl); objs.append(tl)
    return objs

def build_legs(mats, col):
    objs=[]
    for side,sx in [('L',-1),('R',1)]:
        hip=(sx*0.55,0,1.18); knee=(sx*0.58,0,0.60); ankle=(sx*0.54,0,0.18)
        foot=(sx*0.58,0.20,0.08)
        hj=prim('sphere',f'GN_Hip_{side}',loc=hip,size=0.30,segs=14,rings=10)
        assign_mat(hj,mats['iron']); add_sub(hj,1); link(col,hj); objs.append(hj)
        th=seg_obj(f'GN_Thigh_{side}',hip,knee,0.22,mats['iron'],col); objs.append(th)
        # Knee gear
        kg=gear_wheel(f'GN_KneeGear_{side}',knee,0.28,0.18,16,0.055,mats['brass'],col,rot=(0,math.radians(90),0))
        objs.append(kg)
        sh=seg_obj(f'GN_Shin_{side}',knee,ankle,0.18,mats['iron'],col); objs.append(sh)
        aj=prim('sphere',f'GN_Ankle_{side}',loc=ankle,size=0.22,segs=12,rings=8)
        assign_mat(aj,mats['iron']); link(col,aj); objs.append(aj)
        ft=prim('cyl',f'GN_Foot_{side}',loc=foot,size=0.28,depth=0.16,verts=10)
        ft.scale=(1.0,1.6,0.55); bpy.ops.object.transform_apply(scale=True)
        assign_mat(ft,mats['iron']); add_bevel(ft,0.012,2); smart_uv(ft); link(col,ft); objs.append(ft)
    return objs

def build_scary_attachments(mats, col):
    """Prisoner cages, chain loops, skeleton crew decorations, navigation spikes, map streamers, anchor hooks, skull collection."""
    objs=[]

    # ── 2 prisoner cages hanging from belt ──
    for cage_i,cage_sx in [('L',-0.80),('R',0.80)]:
        # Cage frame (4 vertical bars + 2 rings)
        cage_z=0.70; cage_y=0.20
        for bi in range(4):
            ba=math.radians(bi*90+45)
            bx=cage_sx+0.12*math.cos(ba); by=cage_y+0.12*math.sin(ba)
            bar=prim('cyl',f'GN_CageBar_{cage_i}_{bi}',loc=(bx,by,cage_z),size=0.012,depth=0.36,verts=6)
            assign_mat(bar,mats['iron']); link(col,bar); objs.append(bar)
        for cri,crz in enumerate([cage_z+0.18,cage_z-0.18]):
            cr=prim('torus',f'GN_CageRing_{cage_i}_{cri}',loc=(cage_sx,cage_y,crz),major=0.14,minor=0.016,maj_seg=16,min_seg=6)
            assign_mat(cr,mats['iron']); link(col,cr); objs.append(cr)
        # Skull inside cage
        sk=prim('sphere',f'GN_CageSkull_{cage_i}',loc=(cage_sx,cage_y,cage_z),size=0.09,segs=10,rings=8)
        sk.scale=(1.0,0.88,1.06); bpy.ops.object.transform_apply(scale=True)
        assign_mat(sk,mats['bone']); link(col,sk); objs.append(sk)
        # Hanging chain to belt
        for chi in range(4):
            cl=prim('torus',f'GN_CageChain_{cage_i}_{chi}',loc=(cage_sx,cage_y,cage_z+0.22+chi*0.08),major=0.030,minor=0.010,maj_seg=10,min_seg=6,rot=(math.radians(chi*45),0,0))
            assign_mat(cl,mats['iron']); link(col,cl); objs.append(cl)

    # ── 3 skeleton crew decorations dangling from shoulders ──
    skel_pos=[(-1.10,-0.20,2.20),( 1.10,-0.20,2.20),(0,-0.90,2.00)]
    for si2,(skx,sky,skz) in enumerate(skel_pos):
        # Mini skull
        ms=prim('sphere',f'GN_SkelCrew_{si2}_Skull',loc=(skx,sky,skz),size=0.075,segs=10,rings=8)
        assign_mat(ms,mats['bone']); link(col,ms); objs.append(ms)
        # Ribcage (2 ribs per side)
        for ri2 in range(2):
            for srib,sxr in [('L',-1),('R',1)]:
                rb=prim('cyl',f'GN_SkelCrew_{si2}_Rib_{ri2}_{srib}',loc=(skx+sxr*0.04,sky,skz-0.05-ri2*0.06),size=0.008,depth=0.10,verts=5,rot=(0,math.radians(sxr*55),0))
                assign_mat(rb,mats['bone']); link(col,rb); objs.append(rb)
        # Chain to shoulder
        for cli in range(3):
            cl=prim('torus',f'GN_SkelChain_{si2}_{cli}',loc=(skx,sky,skz+0.10+cli*0.08),major=0.022,minor=0.008,maj_seg=10,min_seg=5,rot=(math.radians(cli*60),0,0))
            assign_mat(cl,mats['iron']); link(col,cl); objs.append(cl)

    # ── 6 navigation spike weapons on knuckles ──
    spike_pos=[
        (-1.60,0,1.28),(-1.52,0,1.14),(-1.44,0,1.02),
        ( 1.60,0,1.28),( 1.52,0,1.14),( 1.44,0,1.02),
    ]
    for spi,(spx,spy,spz) in enumerate(spike_pos):
        nsp=prim('cone',f'GN_NavSpike_{spi}',loc=(spx,spy-0.04,spz),r1=0.018,r2=0.003,depth=0.22,verts=4,
                 rot=(math.radians(-20)*(1 if spx<0 else -1),0,0))
        assign_mat(nsp,mats['brass']); link(col,nsp); objs.append(nsp)

    # ── 4 torn map parchment streamers ──
    for mpi in range(4):
        mpa=math.radians(mpi*90+22); mpr=0.72
        mpx=mpr*math.cos(mpa); mpy=mpr*math.sin(mpa)
        mp_strip=prim('cube',f'GN_MapStreamer_{mpi}',loc=(mpx,mpy,2.10),size=0.30)
        mp_strip.scale=(0.08,0.80,0.55); mp_strip.rotation_euler=(0,0,mpa)
        bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(mp_strip,mats['parch']); link(col,mp_strip); objs.append(mp_strip)

    # ── 2 ship anchor hooks as belt trophies ──
    for ani,anx in [('L',-0.38),('R',0.38)]:
        ah=prim('torus',f'GN_AnchorHook_{ani}',loc=(anx,0.65,0.95),major=0.10,minor=0.020,maj_seg=14,min_seg=6,rot=(math.radians(90),0,0))
        assign_mat(ah,mats['iron']); link(col,ah); objs.append(ah)
        as2=prim('cyl',f'GN_AnchorShaft_{ani}',loc=(anx,0.65,1.12),size=0.016,depth=0.22,verts=6)
        assign_mat(as2,mats['iron']); link(col,as2); objs.append(as2)
        at=prim('cyl',f'GN_AnchorTop_{ani}',loc=(anx,0.65,1.24),size=0.040,depth=0.030,verts=8)
        assign_mat(at,mats['brass']); link(col,at); objs.append(at)

    # ── 5 skulls on trophy rack on back ──
    for tri in range(5):
        tra=math.radians(-40+tri*20)
        trx=0.40*math.sin(tra); trz=2.90-abs(math.cos(tra))*0.18
        trs=prim('sphere',f'GN_TrophySkull_{tri}',loc=(trx,-0.80,trz),size=0.075,segs=10,rings=8)
        trs.scale=(1.0,0.88,1.06); bpy.ops.object.transform_apply(scale=True)
        assign_mat(trs,mats['bone']); link(col,trs); objs.append(trs)
        # Trophy mount spike
        trmount=prim('cone',f'GN_TrophyMount_{tri}',loc=(trx,-0.72,trz),r1=0.012,r2=0.003,depth=0.14,verts=4,rot=(math.radians(90),0,0))
        assign_mat(trmount,mats['iron']); link(col,trmount); objs.append(trmount)
    return objs

# ═══════════════════════════════════════════════════════════════════
#  ASSEMBLE
# ═══════════════════════════════════════════════════════════════════

def main():
    clear_scene()
    col=new_col('IsleTrial_Boss_GrandNavigator')
    mats=build_materials()
    all_objs=[]
    all_objs+=build_compass_head(mats,col)
    all_objs+=build_torso(mats,col)
    all_objs+=build_orrery(mats,col)
    all_objs+=build_arms(mats,col)
    all_objs+=build_legs(mats,col)
    all_objs+=build_scary_attachments(mats,col)
    bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0))
    root=bpy.context.active_object; root.name='Boss_GrandNavigator_ROOT'; link(col,root)
    for obj in all_objs:
        if obj.parent is None: obj.parent=root
    mc=sum(1 for o in col.objects if o.type=='MESH')
    print("="*60)
    print("[IsleTrial] Boss: Grand Navigator – MAXIMUM DETAIL")
    print(f"  Mesh objects : {mc}")
    print(f"  Materials    : {len(bpy.data.materials)}")
    print("  Scary adds   : prisoner cages, skeleton crew chains,")
    print("                 navigation spikes, map streamers, skull trophies")
    print("  Next: run 11_Boss_GrandNavigator_Rig.py")
    print("="*60)

main()
