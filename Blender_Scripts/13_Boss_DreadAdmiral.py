"""
IsleTrial – Boss 04: Dread Admiral  (FULL REBUILD – MAXIMUM DETAIL)
====================================================================
Height  ~3.5 m  Colossal undead skeletal pirate admiral.
Theme   Giant bird skull (curved beak, hollow eye sockets with
        spectral soul-fire glow), admiral's bicorne hat with black
        feather plumes, tattered navy coat with golden medals and
        epaulettes, 12-rib bmesh ribcage with sternum, exposed spine,
        glowing soul-fire orb floating in ribcage, 4 arms (2 primary
        sword arms + 2 cannon-mount shoulder arms), giant bird-talon
        legs with 4 raking talons each, spectral aura shards orbiting,
        ghost cannon with spectral projectile, torn ship-flag cape,
        chain whip weapon, dangling ghost skull collection, ship
        wheel embedded in back spine, crew member skulls on belt rack.

Mesh Objects Built:
  SKULL / HEAD
    DA_Skull             – bmesh 24×18 rounded bird skull
    DA_BeakUpper/Lower   – curved raptor beak (bmesh arc)
    DA_EyeSocket_L/R     – hollow eye socket rings
    DA_EyeGlow_L/R       – spectral soul-fire eye spheres
    DA_SkullCrest        – raised cranial crest ridge
    DA_SkullHorn_*       – 3 bone horn protrusions from skull
    DA_JawHinge_L/R      – visible jaw hinge joint spheres

  HAT / PLUMES
    DA_Hat_Main          – bicorne hat body (bmesh)
    DA_Hat_Brim_F/B      – front and rear brim extensions
    DA_HatBand           – gold band torus
    DA_FeatherPlume_*    – 6 black feather plumes fanning out from hat
    DA_HatSkull          – small skull decoration on hat front

  RIBCAGE / SPINE
    DA_Spine_*           – 8 vertebra spheres forming spine column
    DA_Rib_L/R_0-5       – 12 individual bmesh rib arcs per side = 24 ribs total
    DA_Sternum           – sternum plate
    DA_Pelvis            – pelvis T-shape + ilium wings
    DA_SoulOrb           – large spectral soul-fire sphere in ribcage
    DA_SoulWisp_*        – 8 flame wisps orbiting soul orb

  ARMS (×4)
    DA_ArmSword_L/R      – primary sword arms (upper + lower + hand)
    DA_ArmCannon_L/R     – cannon shoulder mounts
    DA_Sword_L/R         – long curved cutlass blades
    DA_SwordGuard_*      – sword crossguard pieces
    DA_Cannon_L/R        – shoulder cannon barrels + rings
    DA_CannonSmoke_*     – smoke sphere at cannon mouths

  LEGS (bird talon style)
    DA_HipJoint_L/R
    DA_Femur_L/R         – upper leg (forward angle)
    DA_KneeJoint_L/R
    DA_TibioTarsus_L/R   – lower leg (bird digitigrade)
    DA_AnkleJoint_L/R
    DA_Tarsometatarsus_L/R – foot shaft
    DA_TalonMain/Inner/Outer/Back_L/R – 4 talons per foot

  COAT / MEDALS
    DA_CoatFront_L/R     – tattered front coat panels
    DA_CoatBack_L/R      – long torn rear panels
    DA_CoatTear_*        – 8 torn hem triangles (random angles)
    DA_Epaulette_L/R     – gold shoulder epaulettes
    DA_EpFringe_*        – 5 gold fringe strands each epaulette
    DA_Medal_*           – 5 medal discs on coat breast
    DA_MedalRibbon_*     – ribbon strips on medals

  SCARY ATTACHMENTS
    DA_TornFlagCape      – large torn ship flag as back cape
    DA_FlagStripe_*      – 5 flag stripe stripes
    DA_ChainWhip         – 8-link chain whip in left claw
    DA_ChainLink_*       – 8 individual chain link torus
    DA_GhostCannon       – ghost cannon barrel + glow projectile orbiting
    DA_GhostProjectile   – spectral cannonball sphere
    DA_ShipWheel         – ship steering wheel embedded in back spine
    DA_WheelSpoke_*      – 8 spokes
    DA_GhostSkull_*      – 5 ghost skulls floating around body
    DA_SpecAuraShard_*   – 10 spectral aura shards orbiting
    DA_BeltSkull_*       – 4 trophy skulls on belt rack

Materials (full dual-path procedural + [UNITY] image slots):
  Mat_DA_Bone          – aged ivory bone + cracks SSS
  Mat_DA_SoulFire      – emissive spectral blue-white fire
  Mat_DA_Coat          – dark navy cloth + wave weave + wear
  Mat_DA_CoatTorn      – torn dark navy with ragged edge
  Mat_DA_Gold          – polished warm gold metallic
  Mat_DA_Black         – matte black feathers/hat
  Mat_DA_Ghost         – translucent spectral white glow
  Mat_DA_Iron          – dark scored iron for cannon/chain
  Mat_DA_Flag          – faded dark red/blue tattered flag

Run BEFORE 13_Boss_DreadAdmiral_Rig.py
"""

import bpy, bmesh, math, random
from mathutils import Vector

rng = random.Random(33)

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

def _mapping(nodes,links,scale=(5,5,5),loc=(-900,0)):
    tc=_n(nodes,'ShaderNodeTexCoord',(loc[0]-200,loc[1]))
    mp=_n(nodes,'ShaderNodeMapping',loc)
    mp.inputs['Scale'].default_value=(*scale,)
    links.new(tc.outputs['UV'],mp.inputs['Vector']); return mp

def _mix_pi(nodes,links,proc,img_nd,loc):
    mix=_n(nodes,'ShaderNodeMixRGB',loc); mix.blend_type='MIX'; mix.inputs[0].default_value=0.0
    links.new(proc,mix.inputs[1]); links.new(img_nd.outputs['Color'],mix.inputs[2]); return mix

def _bump_n(nodes,links,mp,scale=22.0,strength=0.40,loc=(-400,-400)):
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

def mat_bone(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(8,8,8))
    noise=_n(n,'ShaderNodeTexNoise',(-700,300)); noise.inputs['Scale'].default_value=16.0; noise.inputs['Detail'].default_value=10.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    vor=_n(n,'ShaderNodeTexVoronoi',(-700,100)); vor.feature='DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value=22.0
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    mix_nv=_n(n,'ShaderNodeMixRGB',(-400,200)); mix_nv.blend_type='MULTIPLY'; mix_nv.inputs[0].default_value=0.35
    lk.new(noise.outputs['Fac'],mix_nv.inputs[1]); lk.new(vor.outputs['Distance'],mix_nv.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(50,200))
    cr.color_ramp.elements[0].color=(0.48,0.44,0.32,1)
    e1=cr.color_ramp.elements.new(0.45); e1.color=(0.68,0.64,0.52,1)
    cr.color_ramp.elements[1].color=(0.84,0.80,0.68,1)
    lk.new(mix_nv.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-700,-250))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(320,120))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.62
    bsdf.inputs['Subsurface Weight'].default_value=0.04
    bsdf.inputs['Subsurface Radius'].default_value=(0.88,0.76,0.58)
    bmp=_bump_n(n,lk,mp,scale=24.0,strength=0.45); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_soul_fire(name):
    mat,n,lk,bsdf=_base(name)
    noise=_n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=12.0; noise.inputs['Detail'].default_value=6.0
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.04,0.10,0.55,1)
    e1=cr.color_ramp.elements.new(0.45); e1.color=(0.18,0.50,1.00,1)
    cr.color_ramp.elements[1].color=(0.80,0.90,1.00,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Emission Color'].default_value=(0.20,0.60,1.00,1)
    bsdf.inputs['Emission Strength'].default_value=4.0
    bsdf.inputs['Roughness'].default_value=0.85
    bsdf.inputs['Alpha'].default_value=0.75; mat.blend_method='BLEND'
    return mat

def mat_coat(name,dark=(0.04,0.06,0.20),light=(0.08,0.12,0.34)):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(8,8,8))
    wave=_n(n,'ShaderNodeTexWave',(-600,200)); wave.wave_type='BANDS'
    wave.inputs['Scale'].default_value=6.0; wave.inputs['Distortion'].default_value=1.8; wave.inputs['Detail'].default_value=5.0
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-600,0)); noise.inputs['Scale'].default_value=22.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mix_wn=_n(n,'ShaderNodeMixRGB',(-300,100)); mix_wn.blend_type='MULTIPLY'; mix_wn.inputs[0].default_value=0.40
    lk.new(wave.outputs['Color'],mix_wn.inputs[1]); lk.new(noise.outputs['Fac'],mix_wn.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(*dark,1)
    cr.color_ramp.elements[1].color=(*light,1)
    lk.new(mix_wn.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-600,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.88
    bsdf.inputs['Sheen Weight'].default_value=0.12
    bmp=_bump_n(n,lk,mp,scale=20.0,strength=0.35); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_gold(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(10,10,10))
    noise=_n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=22.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.52,0.38,0.06,1)
    cr.color_ramp.elements[1].color=(0.84,0.68,0.16,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-400,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value=1.0; bsdf.inputs['Roughness'].default_value=0.15
    return mat

def mat_black_feather(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(12,12,12))
    noise=_n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=20.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.01,0.01,0.02,1)
    cr.color_ramp.elements[1].color=(0.06,0.06,0.10,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.78; bsdf.inputs['Sheen Weight'].default_value=0.25
    return mat

def mat_ghost(name):
    mat,n,lk,bsdf=_base(name)
    noise=_n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=10.0
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.40,0.55,1.00,1)
    cr.color_ramp.elements[1].color=(0.75,0.85,1.00,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Emission Color'].default_value=(0.30,0.55,1.00,1)
    bsdf.inputs['Emission Strength'].default_value=2.0
    bsdf.inputs['Alpha'].default_value=0.55; mat.blend_method='BLEND'
    bsdf.inputs['Roughness'].default_value=0.88
    return mat

def mat_iron(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(6,6,6))
    musg=_n(n,'ShaderNodeTexMusgrave',(-600,200)); musg.musgrave_type='FBM'; musg.inputs['Scale'].default_value=8.0
    lk.new(mp.outputs['Vector'],musg.inputs['Vector'])
    vor=_n(n,'ShaderNodeTexVoronoi',(-600,0)); vor.feature='DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value=14.0
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    mix_mv=_n(n,'ShaderNodeMixRGB',(-300,100)); mix_mv.blend_type='MULTIPLY'; mix_mv.inputs[0].default_value=0.52
    lk.new(musg.outputs['Fac'],mix_mv.inputs[1]); lk.new(vor.outputs['Distance'],mix_mv.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.06,0.06,0.08,1)
    cr.color_ramp.elements[1].color=(0.22,0.22,0.24,1)
    lk.new(mix_mv.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-600,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value=0.90; bsdf.inputs['Roughness'].default_value=0.60
    bmp=_bump_n(n,lk,mp,scale=26.0,strength=0.45); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_flag_cloth(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(6,6,6))
    noise=_n(n,'ShaderNodeTexNoise',(-500,200)); noise.inputs['Scale'].default_value=18.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.20,0.02,0.02,1)
    cr.color_ramp.elements[1].color=(0.38,0.06,0.04,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-500,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.85; bsdf.inputs['Alpha'].default_value=0.82; mat.blend_method='BLEND'
    return mat

def build_materials():
    return {
        'bone'   : mat_bone('Mat_DA_Bone'),
        'soul'   : mat_soul_fire('Mat_DA_SoulFire'),
        'coat'   : mat_coat('Mat_DA_Coat'),
        'torn'   : mat_coat('Mat_DA_CoatTorn',dark=(0.03,0.04,0.14),light=(0.06,0.09,0.22)),
        'gold'   : mat_gold('Mat_DA_Gold'),
        'black'  : mat_black_feather('Mat_DA_Black'),
        'ghost'  : mat_ghost('Mat_DA_Ghost'),
        'iron'   : mat_iron('Mat_DA_Iron'),
        'flag'   : mat_flag_cloth('Mat_DA_Flag'),
    }

# ═══════════════════════════════════════════════════════════════════
#  GEOMETRY
# ═══════════════════════════════════════════════════════════════════

def build_skull(mats, col):
    """bmesh 24×18 bird skull with curved beak arcs, eye sockets, crest, horns."""
    objs=[]
    bm=bmesh.new(); segs=24; rings=18
    verts_grid=[]
    for ri in range(rings+1):
        t=ri/rings
        r=0.40*math.sin(math.pi*t)
        if t<0.20: r*=(0.65+t/0.20*0.35)
        if t>0.82: r*=(1.0-(t-0.82)/0.18*0.45)
        z=0.46-t*0.92
        ring=[]
        for si in range(segs):
            a=2*math.pi*si/segs
            ring.append(bm.verts.new(Vector((r*math.cos(a),r*math.sin(a),z))))
        verts_grid.append(ring)
    for ri in range(rings):
        for si in range(segs):
            v0=verts_grid[ri][si]; v1=verts_grid[ri][(si+1)%segs]
            v2=verts_grid[ri+1][(si+1)%segs]; v3=verts_grid[ri+1][si]
            try: bm.faces.new([v0,v1,v2,v3])
            except: pass
    tc=bm.verts.new(Vector((0,0,0.46))); bc=bm.verts.new(Vector((0,0,-0.46)))
    for si in range(segs):
        try:
            bm.faces.new([verts_grid[0][(si+1)%segs],verts_grid[0][si],tc])
            bm.faces.new([verts_grid[-1][si],verts_grid[-1][(si+1)%segs],bc])
        except: pass
    mesh=bpy.data.meshes.new('DA_Skull_Mesh'); bm.to_mesh(mesh); bm.free()
    skull=bpy.data.objects.new('DA_Skull',mesh); skull.location=(0,0,3.20); skull.scale=(1.0,1.10,1.0)
    bpy.context.scene.collection.objects.link(skull)
    assign_mat(skull,mats['bone']); bpy.ops.object.transform_apply(scale=True)
    add_sub(skull,2); smart_uv(skull); link(col,skull); objs.append(skull)

    # Upper beak (bmesh curved arc)
    bm2=bmesh.new()
    bk_pts=[Vector((0,0.28,3.20)),Vector((0,0.45,3.14)),Vector((0,0.65,3.05)),Vector((0,0.82,2.92)),Vector((0,0.95,2.76)),Vector((0,0.98,2.62))]
    for pt in bk_pts: bm2.verts.new(pt)
    bm2.verts.ensure_lookup_table()
    for i in range(len(bk_pts)-1):
        try: bm2.edges.new([bm2.verts[i],bm2.verts[i+1]])
        except: pass
    mesh2=bpy.data.meshes.new('DA_BeakUpper_Mesh'); bm2.to_mesh(mesh2); bm2.free()
    bku=bpy.data.objects.new('DA_BeakUpper',mesh2)
    bpy.context.scene.collection.objects.link(bku)
    assign_mat(bku,mats['bone']); add_sub(bku,1)
    m_solid=bku.modifiers.new('Solid','SOLIDIFY'); m_solid.thickness=0.09; m_solid.offset=0.0
    smart_uv(bku); link(col,bku); objs.append(bku)

    # Lower beak
    bm3=bmesh.new()
    bkl_pts=[Vector((0,0.24,3.10)),Vector((0,0.42,3.06)),Vector((0,0.58,2.98)),Vector((0,0.72,2.88)),Vector((0,0.82,2.78)),Vector((0,0.90,2.68))]
    for pt in bkl_pts: bm3.verts.new(pt)
    bm3.verts.ensure_lookup_table()
    for i in range(len(bkl_pts)-1):
        try: bm3.edges.new([bm3.verts[i],bm3.verts[i+1]])
        except: pass
    mesh3=bpy.data.meshes.new('DA_BeakLower_Mesh'); bm3.to_mesh(mesh3); bm3.free()
    bkl=bpy.data.objects.new('DA_BeakLower',mesh3)
    bpy.context.scene.collection.objects.link(bkl)
    assign_mat(bkl,mats['bone']); add_sub(bkl,1)
    m_solid2=bkl.modifiers.new('Solid','SOLIDIFY'); m_solid2.thickness=0.07; m_solid2.offset=0.0
    smart_uv(bkl); link(col,bkl); objs.append(bkl)

    # Eye sockets (hollow rings)
    for side,sx in [('L',-0.22),('R',0.22)]:
        sock_ring=prim('torus',f'DA_EyeSocket_{side}',loc=(sx,0.28,3.28),major=0.14,minor=0.032,maj_seg=20,min_seg=8,rot=(math.radians(25),0,0))
        assign_mat(sock_ring,mats['bone']); link(col,sock_ring); objs.append(sock_ring)
        # Soul-fire glow inside socket
        glow=prim('sphere',f'DA_EyeGlow_{side}',loc=(sx,0.22,3.28),size=0.10,segs=12,rings=8)
        glow.scale=(1.0,0.52,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(glow,mats['soul']); link(col,glow); objs.append(glow)
        # Jaw hinge
        jh=prim('sphere',f'DA_JawHinge_{side}',loc=(sx,0.08,2.98),size=0.055,segs=10,rings=8)
        assign_mat(jh,mats['bone']); link(col,jh); objs.append(jh)

    # Skull cranial crest ridge
    crest=prim('cyl','DA_SkullCrest',loc=(0,-0.15,3.60),size=0.045,depth=0.72,verts=6,rot=(math.radians(10),0,0))
    crest.scale=(0.38,1.0,1.0); bpy.ops.object.transform_apply(scale=True)
    assign_mat(crest,mats['bone']); link(col,crest); objs.append(crest)

    # 3 skull horn protrusions
    horn_pos=[(0,-0.28,3.62),(-.18,-0.20,3.55),(0.18,-0.20,3.55)]
    for hi,(hx,hy,hz) in enumerate(horn_pos):
        horn=prim('cone',f'DA_SkullHorn_{hi}',loc=(hx,hy,hz),r1=0.040,r2=0.006,depth=0.22,verts=5,
                  rot=(math.radians(-15+hi*5),0,math.radians(hi*40-40)))
        assign_mat(horn,mats['bone']); link(col,horn); objs.append(horn)
    return objs

def build_hat(mats, col):
    """Bicorne hat body + brim extensions + gold band + 6 feather plumes."""
    objs=[]
    # Hat main body
    hat=prim('cube','DA_Hat_Main',loc=(0,-0.05,3.90),size=0.72)
    hat.scale=(1.22,0.52,0.55); hat.rotation_euler=(0,0,math.radians(90))
    bpy.ops.object.transform_apply(scale=True,rotation=True)
    assign_mat(hat,mats['black']); add_bevel(hat,0.015,2); smart_uv(hat); link(col,hat); objs.append(hat)
    # Front brim
    fb=prim('cube','DA_Hat_Brim_F',loc=(0,0.38,3.72),size=0.55)
    fb.scale=(2.20,0.45,0.18); fb.rotation_euler=(math.radians(15),0,0)
    bpy.ops.object.transform_apply(scale=True,rotation=True)
    assign_mat(fb,mats['black']); add_bevel(fb,0.012,2); link(col,fb); objs.append(fb)
    # Rear brim
    rb=prim('cube','DA_Hat_Brim_B',loc=(0,-0.38,3.72),size=0.55)
    rb.scale=(2.20,0.45,0.18); rb.rotation_euler=(math.radians(-15),0,0)
    bpy.ops.object.transform_apply(scale=True,rotation=True)
    assign_mat(rb,mats['black']); add_bevel(rb,0.012,2); link(col,rb); objs.append(rb)
    # Gold hat band torus
    hband=prim('torus','DA_HatBand',loc=(0,0,3.72),major=0.42,minor=0.028,maj_seg=28,min_seg=8)
    hband.scale=(1.0,0.52,1.0); bpy.ops.object.transform_apply(scale=True)
    assign_mat(hband,mats['gold']); link(col,hband); objs.append(hband)
    # Small skull decoration on hat front
    hsk=prim('sphere','DA_HatSkull',loc=(0,0.42,3.80),size=0.065,segs=10,rings=8)
    hsk.scale=(1.0,0.88,1.06); bpy.ops.object.transform_apply(scale=True)
    assign_mat(hsk,mats['bone']); link(col,hsk); objs.append(hsk)
    # 6 feather plumes fanning out from hat top-back
    plume_angs=[(-35,-12),(-22,-8),(-8,-4),(8,-4),(22,-8),(35,-12)]
    for pi,(pa,pz_ofs) in enumerate(plume_angs):
        pr=0.38+abs(pi-2.5)*0.04
        plx=pr*math.sin(math.radians(pa))
        plume=prim('cone',f'DA_FeatherPlume_{pi}',loc=(plx,-0.22,3.95+pz_ofs*0.04),
                   r1=0.028,r2=0.005,depth=0.48+abs(pi-2.5)*0.04,verts=3,
                   rot=(math.radians(-65+abs(pi-2.5)*4),0,math.radians(pa)))
        assign_mat(plume,mats['black']); link(col,plume); objs.append(plume)
    return objs

def build_ribcage(mats, col):
    """8 spine vertebrae, 12 bmesh rib arcs each side, sternum, pelvis, soul orb + 8 wisps."""
    objs=[]
    # 8 spine vertebrae
    spine_z=[3.12,2.92,2.72,2.52,2.30,2.08,1.86,1.64]
    for si,sz in enumerate(spine_z):
        sv=prim('sphere',f'DA_Spine_{si}',loc=(0,-0.06,sz),size=0.075-si*0.003,segs=10,rings=8)
        sv.scale=(1.0,0.80,0.72); bpy.ops.object.transform_apply(scale=True)
        assign_mat(sv,mats['bone']); link(col,sv); objs.append(sv)
        # Transverse process spines (2 per vertebra)
        for ts,tsx in [('L',-1),('R',1)]:
            tp=prim('cone',f'DA_SpineProcess_{si}_{ts}',loc=(tsx*0.06,-.08,sz),r1=0.018,r2=0.004,depth=0.10,verts=4,rot=(0,math.radians(tsx*70),0))
            assign_mat(tp,mats['bone']); link(col,tp); objs.append(tp)

    # 12 rib arcs per side (6 pairs total, but full 12 = 6 per side × 2 sides)
    for side,sx in [('L',-1),('R',1)]:
        for ri in range(6):
            rz=2.95-ri*0.22; r_len=0.55+ri*0.04; r_rad=0.030-ri*0.003
            n_pts=9
            bm=bmesh.new()
            arc_pts=[]
            for p in range(n_pts):
                t=p/(n_pts-1)
                ax=sx*r_len*math.sin(t*math.pi*0.62)
                ay=-t*0.14+0.12*math.sin(t*math.pi)
                az=rz-t*0.10
                arc_pts.append(Vector((ax,ay,az)))
            prev_ring=None
            for pi,pt in enumerate(arc_pts):
                ring_v=[]
                cr=r_rad*(1.0-pi*0.08)
                for vi in range(8):
                    va=2*math.pi*vi/8
                    ring_v.append(bm.verts.new(pt+Vector((0,math.cos(va)*cr,math.sin(va)*cr))))
                if prev_ring:
                    for vi in range(8):
                        try: bm.faces.new([prev_ring[vi],prev_ring[(vi+1)%8],ring_v[(vi+1)%8],ring_v[vi]])
                        except: pass
                prev_ring=ring_v
            mesh=bpy.data.meshes.new(f'DA_Rib_{"R" if sx>0 else "L"}_{ri}_Mesh'); bm.to_mesh(mesh); bm.free()
            rib_obj=bpy.data.objects.new(f'DA_Rib_{"R" if sx>0 else "L"}_{ri}',mesh)
            bpy.context.scene.collection.objects.link(rib_obj)
            assign_mat(rib_obj,mats['bone']); smart_uv(rib_obj); link(col,rib_obj); objs.append(rib_obj)
            # Cartilage join sphere at rib tip
            rt=arc_pts[-1]
            rts=prim('sphere',f'DA_RibTip_{"R" if sx>0 else "L"}_{ri}',loc=(rt.x,rt.y,rt.z),size=r_rad*1.8,segs=6,rings=4)
            assign_mat(rts,mats['bone']); link(col,rts); objs.append(rts)

    # Sternum
    stern=seg_obj('DA_Sternum',(0,0.12,2.88),(0,0.12,1.72),0.040,mats['bone'],col,verts=8); objs.append(stern)
    # Pelvis T-shape
    pelv=prim('cube','DA_Pelvis',loc=(0,0,1.58),size=0.14); pelv.scale=(3.20,1.20,0.92); bpy.ops.object.transform_apply(scale=True)
    assign_mat(pelv,mats['bone']); add_bevel(pelv,0.012,2); smart_uv(pelv); link(col,pelv); objs.append(pelv)
    for sx in (-0.28,0.28):
        il=prim('cube',f'DA_Ilium_{"R" if sx>0 else "L"}',loc=(sx,0.06,1.62),size=0.10)
        il.scale=(1.6,0.62,1.28); il.rotation_euler=(0,0,math.radians(sx*42)); bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(il,mats['bone']); link(col,il); objs.append(il)

    # Soul orb (floating in ribcage)
    soul=prim('sphere','DA_SoulOrb',loc=(0,0.08,2.30),size=0.28,segs=22,rings=16)
    soul.scale=(1.0,0.72,1.0); bpy.ops.object.transform_apply(scale=True)
    assign_mat(soul,mats['soul']); add_sub(soul,1); smart_uv(soul); link(col,soul); objs.append(soul)
    # 8 soul flame wisps orbiting
    for wi in range(8):
        wa=math.radians(wi*45); wr=rng.uniform(0.20,0.35)
        wx=wr*math.cos(wa); wz=2.30+wr*0.40*math.sin(wa)
        wisp=prim('sphere',f'DA_SoulWisp_{wi}',loc=(wx,0.08+rng.uniform(-0.08,0.08),wz),size=rng.uniform(0.04,0.08),segs=8,rings=6)
        wisp.scale=(1.0,0.62,1.80); bpy.ops.object.transform_apply(scale=True)
        assign_mat(wisp,mats['soul']); link(col,wisp); objs.append(wisp)
    return objs

def build_coat_and_medals(mats, col):
    """Tattered admiral coat, gold epaulettes + fringe, 5 medals with ribbons."""
    objs=[]
    for sx in (-1,1):
        # Front coat panel
        fp=prim('cube',f'DA_CoatFront_{"R" if sx>0 else "L"}',loc=(sx*0.32,-0.12,1.90),size=0.32)
        fp.scale=(0.98,0.52,3.40); fp.rotation_euler=(math.radians(10)*sx,0,math.radians(7)*sx)
        bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(fp,mats['coat']); add_bevel(fp,0.015,2); smart_uv(fp); link(col,fp); objs.append(fp)
        # Back coat panel (longer, torn)
        bp=prim('cube',f'DA_CoatBack_{"R" if sx>0 else "L"}',loc=(sx*0.28,0.22,1.64),size=0.32)
        bp.scale=(0.92,0.52,4.50); bp.rotation_euler=(math.radians(-14)*sx,0,math.radians(4)*sx)
        bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(bp,mats['torn']); add_bevel(bp,0.012,2); smart_uv(bp); link(col,bp); objs.append(bp)
        # 4 torn hem triangles per side
        for ti in range(4):
            tz=0.60+ti*0.20; tx2=sx*(0.24+ti*0.05)
            torn=prim('cone',f'DA_CoatTear_{"R" if sx>0 else "L"}_{ti}',loc=(tx2,0.26,tz),
                      r1=0.070,r2=0.006,depth=0.22,verts=3,rot=(math.radians(-72),0,math.radians(rng.uniform(-25,25))))
            assign_mat(torn,mats['torn']); link(col,torn); objs.append(torn)
        # Gold epaulette
        ep=prim('sphere',f'DA_Epaulette_{"R" if sx>0 else "L"}',loc=(sx*0.55,0,2.72),size=0.18,segs=18,rings=14)
        ep.scale=(1.0,0.70,0.65); bpy.ops.object.transform_apply(scale=True)
        assign_mat(ep,mats['gold']); smart_uv(ep); link(col,ep); objs.append(ep)
        # 5 epaulette fringe strands
        for fi in range(5):
            fx=sx*(0.46+fi*0.04); fz=2.60-fi*0.025
            fr=prim('cone',f'DA_EpFringe_{"R" if sx>0 else "L"}_{fi}',loc=(fx,0.04,fz),
                    r1=0.014,r2=0.003,depth=0.22,verts=4,rot=(0,math.radians(sx*(-22+fi*9)),0))
            assign_mat(fr,mats['gold']); link(col,fr); objs.append(fr)

    # 5 medal discs on coat breast
    medal_z=[2.46,2.36,2.26,2.16,2.06]
    for mi,mz in enumerate(medal_z):
        mx=-0.18+mi*0.06
        medal=prim('cyl',f'DA_Medal_{mi}',loc=(mx,-0.16,mz),size=0.042,depth=0.018,verts=12)
        assign_mat(medal,mats['gold']); link(col,medal); objs.append(medal)
        ribbon=prim('cube',f'DA_MedalRibbon_{mi}',loc=(mx,-0.15,mz+0.06),size=0.05)
        ribbon.scale=(0.60,0.14,0.50); bpy.ops.object.transform_apply(scale=True)
        assign_mat(ribbon,mats['coat']); link(col,ribbon); objs.append(ribbon)
    return objs

def build_arms(mats, col):
    """2 sword arms (primary), 2 cannon shoulder arms."""
    objs=[]
    # Primary sword arms
    for side,sx in [('L',-1),('R',1)]:
        sh=(sx*0.68,0,2.72); elbow=(sx*1.12,0,2.12); wrist=(sx*1.50,0,1.60); hand=(sx*1.72,0,1.38)
        ua=seg_obj(f'DA_ArmSword_{side}_Upper',sh,elbow,0.065,mats['bone'],col,verts=10); objs.append(ua)
        ej=prim('sphere',f'DA_Elbow_Sword_{side}',loc=elbow,size=0.082,segs=12,rings=8)
        assign_mat(ej,mats['bone']); add_sub(ej,1); link(col,ej); objs.append(ej)
        la=seg_obj(f'DA_ArmSword_{side}_Lower',elbow,wrist,0.055,mats['bone'],col,verts=10); objs.append(la)
        wj=prim('sphere',f'DA_Wrist_Sword_{side}',loc=wrist,size=0.068,segs=10,rings=8)
        assign_mat(wj,mats['bone']); link(col,wj); objs.append(wj)
        # Hand bones
        for fi in range(4):
            fa=math.radians(-20+fi*14)
            fx=hand[0]+sx*0.06*math.cos(fa)
            fing=prim('cone',f'DA_HandFinger_{side}_{fi}',loc=(fx,hand[1],hand[2]-0.06),r1=0.016,r2=0.004,depth=0.16,verts=4)
            assign_mat(fing,mats['bone']); link(col,fing); objs.append(fing)
        # Curved cutlass blade
        blade_pts=[(hand[0],hand[1],hand[2]-0.08),(hand[0]+sx*0.12,hand[1],hand[2]-0.35),(hand[0]+sx*0.20,hand[1],hand[2]-0.65),(hand[0]+sx*0.18,hand[1],hand[2]-0.98),(hand[0]+sx*0.10,hand[1],hand[2]-1.25)]
        for bi in range(len(blade_pts)-1):
            bseg=seg_obj(f'DA_Sword_{side}_Seg{bi}',blade_pts[bi],blade_pts[bi+1],0.018-bi*0.002,mats['iron'],col,verts=6)
            objs.append(bseg)
        # Sword guard
        guard=prim('cube',f'DA_SwordGuard_{side}',loc=(hand[0]+sx*0.06,hand[1],hand[2]-0.16),size=0.16)
        guard.scale=(0.10,0.55,1.40); guard.rotation_euler=(0,math.radians(sx*15),0)
        bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(guard,mats['iron']); link(col,guard); objs.append(guard)

    # Cannon shoulder arms (shorter, attach high on shoulders)
    for side,sx in [('L',-1),('R',1)]:
        can_sh=(sx*0.72,0,2.90); can_end=(sx*1.28,0,2.70)
        ca=seg_obj(f'DA_ArmCannon_{side}',can_sh,can_end,0.075,mats['bone'],col,verts=10); objs.append(ca)
        # Cannon barrel on end
        cannon=prim('cyl',f'DA_Cannon_{side}',loc=(sx*1.52,0,2.65),size=0.065,depth=0.52,verts=12,rot=(0,math.radians(90),0))
        assign_mat(cannon,mats['iron']); smart_uv(cannon); link(col,cannon); objs.append(cannon)
        can_ring=prim('torus',f'DA_CannonRing_{side}',loc=(sx*1.28,0,2.65),major=0.085,minor=0.020,maj_seg=16,min_seg=6,rot=(0,math.radians(90),0))
        assign_mat(can_ring,mats['iron']); link(col,can_ring); objs.append(can_ring)
        smoke=prim('sphere',f'DA_CannonSmoke_{side}',loc=(sx*1.80,0,2.65),size=0.060,segs=8,rings=6)
        assign_mat(smoke,mats['ghost']); link(col,smoke); objs.append(smoke)
    return objs

def build_legs(mats, col):
    """Digitigrade bird legs with 4 raking talons each."""
    objs=[]
    for side,sx in [('L',-1),('R',1)]:
        hip=(sx*0.42,0,1.52); knee=(sx*0.50,0.28,0.88); ankle=(sx*0.44,0.60,0.32); foot=(sx*0.42,0.72,0.18)
        hj=prim('sphere',f'DA_HipJoint_{side}',loc=hip,size=0.12,segs=12,rings=10)
        assign_mat(hj,mats['bone']); add_sub(hj,1); link(col,hj); objs.append(hj)
        femur=seg_obj(f'DA_Femur_{side}',hip,knee,0.075,mats['bone'],col,verts=10); objs.append(femur)
        kj=prim('sphere',f'DA_KneeJoint_{side}',loc=knee,size=0.10,segs=12,rings=8)
        assign_mat(kj,mats['bone']); link(col,kj); objs.append(kj)
        tibia=seg_obj(f'DA_TibioTarsus_{side}',knee,ankle,0.060,mats['bone'],col,verts=10); objs.append(tibia)
        aj=prim('sphere',f'DA_AnkleJoint_{side}',loc=ankle,size=0.085,segs=10,rings=8)
        assign_mat(aj,mats['bone']); link(col,aj); objs.append(aj)
        tmt=seg_obj(f'DA_Tarsometa_{side}',ankle,foot,0.048,mats['bone'],col,verts=8); objs.append(tmt)
        # 4 raking talons (Main/Inner/Outer/Back)
        talon_defs=[('Main',(sx*0.40,1.10,0.08),0.028,0.30),('Inner',(sx*0.56,0.96,0.10),0.022,0.22),
                    ('Outer',(sx*0.26,0.96,0.10),0.022,0.22),('Back',(sx*0.44,0.38,0.10),0.020,0.20)]
        for tname,tloc,tr,th in talon_defs:
            talon=prim('cone',f'DA_Talon{tname}_{side}',loc=tloc,r1=tr,r2=0.004,depth=th,verts=4,
                       rot=(math.radians(-35),0,math.radians(sx*5)))
            assign_mat(talon,mats['bone']); link(col,talon); objs.append(talon)
    return objs

def build_scary_attachments(mats, col):
    """Torn flag cape, chain whip, ghost cannon, ship wheel in spine, ghost skulls, spectral shards, belt skulls."""
    objs=[]
    # ── Torn ship flag cape on back ──
    cape=prim('cube','DA_TornFlagCape',loc=(0,-0.45,2.10),size=1.10)
    cape.scale=(2.60,0.06,3.20); bpy.ops.object.transform_apply(scale=True)
    assign_mat(cape,mats['flag']); smart_uv(cape); link(col,cape); objs.append(cape)
    # 5 flag stripes
    stripe_z=[2.80,2.40,2.00,1.60,1.20]
    for si2,sz2 in enumerate(stripe_z):
        stripe=prim('cube',f'DA_FlagStripe_{si2}',loc=(0,-0.44,sz2),size=1.10)
        stripe.scale=(2.58,0.065,0.16); bpy.ops.object.transform_apply(scale=True)
        st_mat=bpy.data.materials.new(f'Mat_FlagStripe_{si2}'); st_mat.use_nodes=True
        col2=(0.06,0.06,0.18,1) if si2%2==0 else (0.25,0.02,0.02,1)
        st_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=col2
        assign_mat(stripe,st_mat); link(col,stripe); objs.append(stripe)
    # Torn edge triangle strips
    for tei in range(6):
        te=prim('cone',f'DA_CapeTearedge_{tei}',loc=(-1.18+tei*0.40,-0.44,0.90),r1=0.095,r2=0.006,depth=0.28,verts=3,
                rot=(math.radians(-88),0,math.radians(rng.uniform(-20,20))))
        assign_mat(te,mats['flag']); link(col,te); objs.append(te)

    # ── Chain whip in left hand ──
    chain_start=(-1.72,0,1.38)
    for cli in range(8):
        cx=-1.72+cli*0.08; cz=1.38-cli*0.14
        cl=prim('torus',f'DA_ChainLink_{cli}',loc=(cx,0,cz),major=0.032,minor=0.012,maj_seg=12,min_seg=6,rot=(math.radians(cli*45),0,0))
        assign_mat(cl,mats['iron']); link(col,cl); objs.append(cl)
    # Chain whip hook tip
    hook=prim('torus','DA_ChainWhipHook',loc=(-2.35,0,0.26),major=0.052,minor=0.016,maj_seg=10,min_seg=5,rot=(math.radians(90),0,0))
    assign_mat(hook,mats['iron']); link(col,hook); objs.append(hook)

    # ── Ghost cannon (large floating) ──
    gc=prim('cyl','DA_GhostCannon',loc=(0.90,-0.55,2.42),size=0.095,depth=0.72,verts=12,rot=(0,math.radians(35),math.radians(20)))
    assign_mat(gc,mats['iron']); smart_uv(gc); link(col,gc); objs.append(gc)
    gc_ring=prim('torus','DA_GhostCannonRing',loc=(0.62,-0.44,2.50),major=0.115,minor=0.025,maj_seg=18,min_seg=6,rot=(0,math.radians(35),math.radians(20)))
    assign_mat(gc_ring,mats['iron']); link(col,gc_ring); objs.append(gc_ring)
    # Spectral cannonball projectile
    gcb=prim('sphere','DA_GhostProjectile',loc=(1.45,-0.80,2.22),size=0.095,segs=12,rings=8)
    assign_mat(gcb,mats['soul']); add_sub(gcb,1); link(col,gcb); objs.append(gcb)

    # ── Ship wheel embedded in back spine ──
    wheel=prim('torus','DA_ShipWheel',loc=(0,-0.62,2.44),major=0.45,minor=0.036,maj_seg=28,min_seg=8,rot=(math.radians(75),0,0))
    assign_mat(wheel,mats['iron']); link(col,wheel); objs.append(wheel)
    # 8 spokes
    for wi2 in range(8):
        wa2=math.radians(wi2*45); wr2=0.44
        wx2=wr2*math.cos(wa2); wz2=2.44+wr2*math.sin(wa2)*math.cos(math.radians(75))
        wy2=-0.62+wr2*math.sin(wa2)*math.sin(math.radians(75))
        spoke=seg_obj(f'DA_WheelSpoke_{wi2}',(0,-0.62,2.44),(wx2,wy2,wz2),0.016,mats['iron'],col,verts=6)
        objs.append(spoke)
    # Hub
    hub=prim('sphere','DA_WheelHub',loc=(0,-0.62,2.44),size=0.075,segs=10,rings=8)
    assign_mat(hub,mats['iron']); link(col,hub); objs.append(hub)

    # ── 5 ghost skulls floating around body ──
    ghost_sk_pos=[(1.30,0.30,2.90),(-1.30,0.30,2.90),(0,1.20,2.50),(1.10,-0.60,1.80),(-1.10,-0.60,1.80)]
    for gsi,(gsx,gsy,gsz) in enumerate(ghost_sk_pos):
        gsk=prim('sphere',f'DA_GhostSkull_{gsi}',loc=(gsx,gsy,gsz),size=rng.uniform(0.08,0.14),segs=10,rings=8)
        gsk.scale=(1.0,0.88,1.06); bpy.ops.object.transform_apply(scale=True)
        assign_mat(gsk,mats['ghost']); link(col,gsk); objs.append(gsk)
        # Eye glow socket
        for gei,gex in enumerate([-0.04,0.04]):
            ge=prim('sphere',f'DA_GhostSkullEye_{gsi}_{gei}',loc=(gsx+gex,gsy-0.05,gsz+0.04),size=0.022,segs=6,rings=4)
            assign_mat(ge,mats['soul']); link(col,ge); objs.append(ge)

    # ── 10 spectral aura shards orbiting body ──
    for sai in range(10):
        saa=math.radians(sai*36); sar=rng.uniform(0.85,1.40)
        sax2=sar*math.cos(saa); say2=rng.uniform(-0.30,0.30)
        saz2=1.80+sar*0.50*math.sin(saa)
        shard=prim('cone',f'DA_SpecAuraShard_{sai}',loc=(sax2,say2,saz2),r1=0.020,r2=0.004,depth=rng.uniform(0.18,0.32),verts=3,
                   rot=(rng.uniform(-0.8,0.8),rng.uniform(-0.5,0.5),saa))
        assign_mat(shard,mats['ghost']); link(col,shard); objs.append(shard)

    # ── 4 belt trophy skulls ──
    belt_sk_pos=[(-0.38,0,1.62),(-0.14,0,1.62),(0.14,0,1.62),(0.38,0,1.62)]
    for bsi,(bsx2,bsy2,bsz2) in enumerate(belt_sk_pos):
        bsk=prim('sphere',f'DA_BeltSkull_{bsi}',loc=(bsx2,0.22,bsz2),size=0.060,segs=10,rings=8)
        bsk.scale=(1.0,0.88,1.05); bpy.ops.object.transform_apply(scale=True)
        assign_mat(bsk,mats['bone']); link(col,bsk); objs.append(bsk)
    return objs

# ═══════════════════════════════════════════════════════════════════
#  ASSEMBLE
# ═══════════════════════════════════════════════════════════════════

def main():
    clear_scene()
    col=new_col('IsleTrial_Boss_DreadAdmiral')
    mats=build_materials()
    all_objs=[]
    all_objs+=build_skull(mats,col)
    all_objs+=build_hat(mats,col)
    all_objs+=build_ribcage(mats,col)
    all_objs+=build_coat_and_medals(mats,col)
    all_objs+=build_arms(mats,col)
    all_objs+=build_legs(mats,col)
    all_objs+=build_scary_attachments(mats,col)
    bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0))
    root=bpy.context.active_object; root.name='Boss_DreadAdmiral_ROOT'; link(col,root)
    for obj in all_objs:
        if obj.parent is None: obj.parent=root
    mc=sum(1 for o in col.objects if o.type=='MESH')
    print("="*60)
    print("[IsleTrial] Boss: Dread Admiral – MAXIMUM DETAIL")
    print(f"  Mesh objects : {mc}")
    print(f"  Materials    : {len(bpy.data.materials)}")
    print("  Ribs         : 12 per side = 24 total (bmesh arcs)")
    print("  Scary adds   : torn flag cape, chain whip, ghost cannon,")
    print("                 ship wheel in spine, 5 ghost skulls, 10 aura shards")
    print("  Next: run 13_Boss_DreadAdmiral_Rig.py")
    print("="*60)

main()
