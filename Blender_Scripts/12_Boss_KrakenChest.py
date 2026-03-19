"""
IsleTrial – Boss 03: Kraken Chest King  (FULL REBUILD – MAXIMUM DETAIL)
========================================================================
Size    ~3.2 m wide × 2.8 m tall  (open/reared attack pose)
Theme   Colossal living mimic chest with full monstrous body:
        planked hull chest with iron banding, 16 tentacles (4 types),
        3 massive compound eyes, 3 rows shark teeth top/bottom,
        long forked tongue with taste buds, bioluminescent vein cracks,
        interior glow with treasure spilling out, broken ship mast
        impaled through lid, barnacle encrustation, 4 eye-stalks,
        ink spray apparatus on back, victim bone decorations.

Mesh Objects Built:
  CHEST HULL
    KC_ChestBody      – bmesh planked hull (8 plank strips per side)
    KC_ChestLid       – separate hinged lid (open 60°)
    KC_LidPlanks_*    – 8 raised plank ridges on lid
    KC_IronBand_*     – 6 iron banding hoops (torus rings)
    KC_HingeL/R       – 2 large iron hinge brackets
    KC_LockPlate      – central lock plate (broken open)
    KC_LockBolt_*     – 4 broken bolt stumps
    KC_BarnacleCluster_* – 10 barnacle patches on hull exterior

  MOUTH / TEETH / TONGUE
    KC_JawUpper       – bmesh upper jaw gum interior
    KC_JawLower       – bmesh lower jaw gum
    KC_TeethUpper_*   – 3 rows × 8 teeth = 24 upper teeth
    KC_TeethLower_*   – 3 rows × 8 teeth = 24 lower teeth
    KC_Tongue         – 3-segment tongue base + 2 forked tips
    KC_TasteBud_*     – 16 taste bud spheres on tongue surface
    KC_DroolFila_*    – 8 drool/slime filaments

  EYES
    KC_Eye_0/1/2      – 3 main eyes (3-layer each: socket/iris/pupil)
    KC_EyeStalk_*     – 4 extra eye stalks with smaller eyes on tips
    KC_EyeStalk_Eye_* – smaller sphere eyes on stalk tips

  TENTACLES (16 total, 4 types)
    KC_TentAttack_*   – 4 thick short attack arms (close range)
    KC_TentSucker_*   – 6 medium length arms with sucker disc rows
    KC_TentWhip_*     – 4 long whip tentacles (3 segments each)
    KC_TentGrab_*     – 2 massive grab arms with claw tips

  INTERIOR TREASURE
    KC_InteriorGlow   – emissive interior dome
    KC_GoldCoin_*     – 12 gold coin discs spilling out
    KC_GemCluster_*   – 6 gem stone pieces at opening
    KC_Chalice        – overturned goblet
    KC_TreasureBar_*  – 3 gold bar ingots

  SCARY ATTACHMENTS
    KC_ShipMast       – broken ship mast impaled through lid
    KC_MastFlag       – tattered flag strip on mast
    KC_InkSacApparatus – ink sac sphere + tube on back
    KC_InkNozzle      – ink spray nozzle tube
    KC_VictimBone_*   – 8 large victim bones embedded in chest
    KC_BioVeinCrack_* – 12 bioluminescent crack lines on hull
    KC_SlimeDrool_*   – 6 massive slime drool rope strands

Materials (full dual-path procedural + [UNITY] image slots):
  Mat_KC_Wood       – dark weathered plank wood + Musgrave grain
  Mat_KC_Iron       – rusted scored iron + Voronoi pitting
  Mat_KC_Flesh      – dark wet mouth flesh + SSS
  Mat_KC_Tooth      – bone-white ivory + SSS
  Mat_KC_Eye        – wet black sclera
  Mat_KC_Iris       – amber yellow iris + emissive
  Mat_KC_BioLum     – bioluminescent teal crack glow
  Mat_KC_Slime      – translucent toxic green
  Mat_KC_Gold       – polished gold metal
  Mat_KC_Gem        – deep red gem + transmission

Run BEFORE 12_Boss_KrakenChest_Rig.py
"""

import bpy, bmesh, math, random
from mathutils import Vector

rng = random.Random(88)

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

def _bump_n(nodes,links,mp,scale=20.0,strength=0.45,loc=(-400,-400)):
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

def mat_wood(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(3,3,3))
    musg=_n(n,'ShaderNodeTexMusgrave',(-700,300)); musg.musgrave_type='FBM'
    musg.inputs['Scale'].default_value=4.0; musg.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],musg.inputs['Vector'])
    wave=_n(n,'ShaderNodeTexWave',(-700,100)); wave.wave_type='BANDS'
    wave.inputs['Scale'].default_value=3.5; wave.inputs['Distortion'].default_value=2.8; wave.inputs['Detail'].default_value=6.0
    lk.new(mp.outputs['Vector'],wave.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-700,-100)); noise.inputs['Scale'].default_value=16.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mix_mw=_n(n,'ShaderNodeMixRGB',(-400,200)); mix_mw.blend_type='MULTIPLY'; mix_mw.inputs[0].default_value=0.55
    lk.new(musg.outputs['Fac'],mix_mw.inputs[1]); lk.new(wave.outputs['Color'],mix_mw.inputs[2])
    mix_wn=_n(n,'ShaderNodeMixRGB',(-200,150)); mix_wn.blend_type='OVERLAY'; mix_wn.inputs[0].default_value=0.22
    lk.new(mix_mw.outputs['Color'],mix_wn.inputs[1]); lk.new(noise.outputs['Fac'],mix_wn.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(50,200))
    cr.color_ramp.elements[0].color=(0.08,0.05,0.02,1)
    e1=cr.color_ramp.elements.new(0.40); e1.color=(0.20,0.12,0.05,1)
    cr.color_ramp.elements[1].color=(0.32,0.22,0.10,1)
    lk.new(mix_wn.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-700,-250))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(320,120))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.84
    bmp=_bump_n(n,lk,mp,scale=22.0,strength=0.50); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_iron_rusted(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(6,6,6))
    vor=_n(n,'ShaderNodeTexVoronoi',(-600,200)); vor.feature='DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value=12.0
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    noise=_n(n,'ShaderNodeTexNoise',(-600,0)); noise.inputs['Scale'].default_value=22.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    mix_vn=_n(n,'ShaderNodeMixRGB',(-300,100)); mix_vn.blend_type='OVERLAY'; mix_vn.inputs[0].default_value=0.48
    lk.new(vor.outputs['Distance'],mix_vn.inputs[1]); lk.new(noise.outputs['Fac'],mix_vn.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.16,0.06,0.02,1)   # rust brown
    e1=cr.color_ramp.elements.new(0.45); e1.color=(0.22,0.12,0.06,1)
    cr.color_ramp.elements[1].color=(0.14,0.14,0.16,1)   # iron grey
    lk.new(mix_vn.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-600,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.72; bsdf.inputs['Metallic'].default_value=0.70
    bmp=_bump_n(n,lk,mp,scale=24.0,strength=0.60); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_flesh_mouth(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(5,5,5))
    noise=_n(n,'ShaderNodeTexNoise',(-500,200)); noise.inputs['Scale'].default_value=14.0; noise.inputs['Detail'].default_value=8.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    vor=_n(n,'ShaderNodeTexVoronoi',(-500,0)); vor.inputs['Scale'].default_value=20.0
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    mix_nv=_n(n,'ShaderNodeMixRGB',(-250,100)); mix_nv.blend_type='MULTIPLY'; mix_nv.inputs[0].default_value=0.40
    lk.new(noise.outputs['Fac'],mix_nv.inputs[1]); lk.new(vor.outputs['Distance'],mix_nv.inputs[2])
    cr=_n(n,'ShaderNodeValToRGB',(-50,100))
    cr.color_ramp.elements[0].color=(0.35,0.06,0.06,1)
    cr.color_ramp.elements[1].color=(0.60,0.18,0.12,1)
    lk.new(mix_nv.outputs['Color'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-500,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.40
    bsdf.inputs['Subsurface Weight'].default_value=0.10
    bsdf.inputs['Subsurface Radius'].default_value=(0.80,0.28,0.28)
    bmp=_bump_n(n,lk,mp,scale=20.0,strength=0.35); lk.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    return mat

def mat_tooth(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(10,10,10))
    noise=_n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=18.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.82,0.80,0.70,1)
    cr.color_ramp.elements[1].color=(0.96,0.94,0.88,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-400,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.22
    bsdf.inputs['Subsurface Weight'].default_value=0.04
    return mat

def mat_eye_sclera(name):
    mat,n,lk,bsdf=_base(name)
    bsdf.inputs['Base Color'].default_value=(0.01,0.01,0.01,1)
    bsdf.inputs['Roughness'].default_value=0.02; bsdf.inputs['Specular IOR Level'].default_value=1.0
    return mat

def mat_iris_amber(name):
    mat,n,lk,bsdf=_base(name)
    mp=_mapping(n,lk,scale=(6,6,6))
    vor=_n(n,'ShaderNodeTexVoronoi',(-400,100)); vor.inputs['Scale'].default_value=22.0
    lk.new(mp.outputs['Vector'],vor.inputs['Vector'])
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.40,0.18,0.02,1)
    cr.color_ramp.elements[1].color=(0.80,0.50,0.06,1)
    lk.new(vor.outputs['Distance'],cr.inputs['Fac'])
    img_a=_img(n,f'{name}_Albedo',(-400,-200))
    mix_c=_mix_pi(n,lk,cr.outputs['Color'],img_a,(200,50))
    lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.04
    bsdf.inputs['Emission Color'].default_value=(0.60,0.30,0.02,1)
    bsdf.inputs['Emission Strength'].default_value=0.8
    return mat

def mat_biolum(name):
    mat,n,lk,bsdf=_base(name)
    wave=_n(n,'ShaderNodeTexWave',(-400,100)); wave.wave_type='BANDS'; wave.inputs['Scale'].default_value=6.0; wave.inputs['Distortion'].default_value=3.0
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.02,0.22,0.30,1)
    cr.color_ramp.elements[1].color=(0.06,0.72,0.80,1)
    lk.new(wave.outputs['Color'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Emission Color'].default_value=(0.04,0.80,0.90,1)
    bsdf.inputs['Emission Strength'].default_value=2.5
    bsdf.inputs['Roughness'].default_value=0.15
    return mat

def mat_slime(name):
    mat,n,lk,bsdf=_base(name)
    noise=_n(n,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=14.0
    cr=_n(n,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.02,0.22,0.04,1)
    cr.color_ramp.elements[1].color=(0.10,0.55,0.08,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.05
    bsdf.inputs['Transmission Weight'].default_value=0.50
    bsdf.inputs['Alpha'].default_value=0.72; mat.blend_method='BLEND'
    bsdf.inputs['Emission Color'].default_value=(0.04,0.40,0.04,1)
    bsdf.inputs['Emission Strength'].default_value=0.55
    return mat

def mat_gold(name):
    mat,n,lk,bsdf=_base(name)
    bsdf.inputs['Base Color'].default_value=(0.85,0.65,0.10,1)
    bsdf.inputs['Metallic'].default_value=1.0; bsdf.inputs['Roughness'].default_value=0.14
    return mat

def mat_gem(name):
    mat,n,lk,bsdf=_base(name)
    bsdf.inputs['Base Color'].default_value=(0.50,0.02,0.02,1)
    bsdf.inputs['Roughness'].default_value=0.02; bsdf.inputs['Transmission Weight'].default_value=0.75
    bsdf.inputs['IOR'].default_value=1.76
    return mat

def build_materials():
    return {
        'wood'  : mat_wood('Mat_KC_Wood'),
        'iron'  : mat_iron_rusted('Mat_KC_Iron'),
        'flesh' : mat_flesh_mouth('Mat_KC_Flesh'),
        'tooth' : mat_tooth('Mat_KC_Tooth'),
        'eye'   : mat_eye_sclera('Mat_KC_Eye'),
        'iris'  : mat_iris_amber('Mat_KC_Iris'),
        'bio'   : mat_biolum('Mat_KC_BioLum'),
        'slime' : mat_slime('Mat_KC_Slime'),
        'gold'  : mat_gold('Mat_KC_Gold'),
        'gem'   : mat_gem('Mat_KC_Gem'),
    }

# ═══════════════════════════════════════════════════════════════════
#  GEOMETRY
# ═══════════════════════════════════════════════════════════════════

def build_chest_hull(mats, col):
    """bmesh planked chest body (lower half) with iron bands, hinges, barnacles."""
    objs=[]
    bm=bmesh.new()
    W=1.20; H=0.72; D=0.90
    # 8 vertices per ring, 6 rings
    for ri in range(6):
        t=ri/5
        rw=W*(1.0-t*0.08); rh=H; rd=D*(1.0-t*0.05)
        for si in range(8):
            a=2*math.pi*si/8
            bm.verts.new(Vector((rw*math.cos(a)*0.85,rd*math.sin(a),t*H*0.5)))
    bm.verts.ensure_lookup_table()
    for ri in range(5):
        for si in range(8):
            v0=bm.verts[ri*8+si]; v1=bm.verts[ri*8+(si+1)%8]
            v2=bm.verts[(ri+1)*8+(si+1)%8]; v3=bm.verts[(ri+1)*8+si]
            try: bm.faces.new([v0,v1,v2,v3])
            except: pass
    # Bottom cap
    bc=bm.verts.new(Vector((0,0,-0.05)))
    for si in range(8):
        try: bm.faces.new([bm.verts[(si+1)%8],bm.verts[si],bc])
        except: pass
    mesh=bpy.data.meshes.new('KC_Body_Mesh'); bm.to_mesh(mesh); bm.free()
    body=bpy.data.objects.new('KC_ChestBody',mesh); body.location=(0,0,0.72)
    bpy.context.scene.collection.objects.link(body)
    assign_mat(body,mats['wood']); add_sub(body,2); smart_uv(body); link(col,body); objs.append(body)

    # 8 raised plank ridges on body sides
    for pi2 in range(8):
        pa=2*math.pi*pi2/8; pr=1.20
        px=pr*math.cos(pa)*0.88; pz=1.10
        plank=prim('cube',f'KC_BodyPlank_{pi2}',loc=(px,pr*math.sin(pa)*0.88,pz),size=0.10)
        plank.scale=(0.12,0.04,1.10); plank.rotation_euler=(0,0,pa)
        bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(plank,mats['wood']); add_bevel(plank,0.008,2); link(col,plank); objs.append(plank)

    # Lid (open at ~60°)
    lid=prim('cube','KC_ChestLid',loc=(0,-0.30,1.58),size=1.0)
    lid.scale=(2.42,1.88,0.14); lid.rotation_euler=(math.radians(-60),0,0)
    bpy.ops.object.transform_apply(scale=True,rotation=True)
    assign_mat(lid,mats['wood']); add_bevel(lid,0.015,2); smart_uv(lid); link(col,lid); objs.append(lid)

    # 8 lid plank ridges
    for li2 in range(8):
        la=2*math.pi*li2/8
        lx=1.0*math.sin(la); lz=0.08
        lp=prim('cube',f'KC_LidPlank_{li2}',loc=(lx,-0.60+0.15*li2,1.80),size=0.12)
        lp.scale=(0.12,0.04,2.0); lp.rotation_euler=(math.radians(-60),0,0)
        bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(lp,mats['wood']); link(col,lp); objs.append(lp)

    # 6 iron banding hoops
    band_z=[0.75,0.98,1.20,1.40,1.56,1.68]
    for bi2,bz2 in enumerate(band_z):
        band=prim('torus',f'KC_IronBand_{bi2}',loc=(0,0,bz2),major=1.24,minor=0.035,maj_seg=32,min_seg=8)
        band.scale=(1.0,0.88,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(band,mats['iron']); link(col,band); objs.append(band)

    # 2 large hinges
    for side,sx in [('L',-1.10),('R',1.10)]:
        hinge=prim('cube',f'KC_Hinge_{side}',loc=(sx,-0.62,1.50),size=0.22)
        hinge.scale=(0.55,0.25,0.80); bpy.ops.object.transform_apply(scale=True)
        assign_mat(hinge,mats['iron']); add_bevel(hinge,0.012,2); link(col,hinge); objs.append(hinge)

    # Central lock plate (broken open)
    lp2=prim('cube','KC_LockPlate',loc=(0,1.22,1.38),size=0.32)
    lp2.scale=(0.80,0.15,0.50); bpy.ops.object.transform_apply(scale=True)
    assign_mat(lp2,mats['iron']); add_bevel(lp2,0.014,2); link(col,lp2); objs.append(lp2)
    # 4 broken bolt stumps
    for boi2 in range(4):
        bx=(-0.10+boi2*0.07); bz=(1.28+boi2*0.06)
        bolt=prim('cyl',f'KC_LockBolt_{boi2}',loc=(bx,1.24,bz),size=0.022,depth=0.06,verts=6)
        assign_mat(bolt,mats['iron']); link(col,bolt); objs.append(bolt)

    # 10 barnacle patches
    barn_pos=[
        ( 1.10, 0.40,0.90),(-1.10, 0.40,0.90),( 1.05,-0.50,1.10),(-1.05,-0.50,1.10),
        ( 0.80, 0.80,1.30),(-0.80, 0.80,1.30),( 0,    0.90,0.80),(  0,-0.90,0.85),
        ( 0.60,-0.80,1.40),(-0.60,-0.80,1.40),
    ]
    for bni2,(bnx,bny,bnz) in enumerate(barn_pos):
        for bki2 in range(4):
            bangle=math.radians(bki2*90+rng.uniform(-20,20))
            bkx=bnx+0.06*math.cos(bangle); bky=bny+0.06*math.sin(bangle)
            barn=prim('cone',f'KC_Barnacle_{bni2}_{bki2}',loc=(bkx,bky,bnz),r1=0.028,r2=0.008,depth=0.060,verts=8)
            assign_mat(barn,mats['iron']); link(col,barn); objs.append(barn)
    return objs

def build_mouth_teeth_tongue(mats, col):
    """bmesh jaws, 3 rows × 8 = 24 teeth each jaw, 3-segment tongue + 16 taste buds."""
    objs=[]
    # Upper jaw interior gum
    bm_u=bmesh.new()
    for si in range(20):
        a=2*math.pi*si/20
        bm_u.verts.new(Vector((1.10*math.cos(a),0.30*math.sin(a)+0.10,1.52)))
        bm_u.verts.new(Vector((0.95*math.cos(a),0.26*math.sin(a)+0.08,1.30)))
    bm_u.verts.ensure_lookup_table()
    for si in range(20):
        try: bm_u.faces.new([bm_u.verts[si*2],bm_u.verts[(si*2+2)%40],bm_u.verts[(si*2+3)%40],bm_u.verts[si*2+1]])
        except: pass
    mesh_u=bpy.data.meshes.new('KC_JawUpper_Mesh'); bm_u.to_mesh(mesh_u); bm_u.free()
    jaw_u=bpy.data.objects.new('KC_JawUpper',mesh_u)
    bpy.context.scene.collection.objects.link(jaw_u)
    assign_mat(jaw_u,mats['flesh']); add_solidify(jaw_u,0.06); smart_uv(jaw_u); link(col,jaw_u); objs.append(jaw_u)

    # Lower jaw
    jaw_lo=prim('sphere','KC_JawLower',loc=(0,0.20,0.90),size=1.08,segs=20,rings=14)
    jaw_lo.scale=(1.0,0.35,0.30); bpy.ops.object.transform_apply(scale=True)
    assign_mat(jaw_lo,mats['flesh']); smart_uv(jaw_lo); link(col,jaw_lo); objs.append(jaw_lo)

    # Mouth interior sphere
    mint=prim('sphere','KC_MouthInterior',loc=(0,0.08,1.22),size=1.20,segs=18,rings=12)
    mint.scale=(0.88,0.38,0.35); bpy.ops.object.transform_apply(scale=True)
    assign_mat(mint,mats['flesh']); link(col,mint); objs.append(mint)

    # Upper teeth: 3 rows × 8 teeth
    for row in range(3):
        rs=1.0-row*0.18; rofs=row*0.06
        for ti2 in range(8):
            ta=math.radians(-32+ti2*10)
            tx=0.88*rs*math.sin(ta); tz=1.52-rofs
            ts=0.055-row*0.012; th=0.14-row*0.030
            tooth=prim('cone',f'KC_ToothUp_R{row}_{ti2}',loc=(tx,0.28,tz),r1=ts,r2=0.005,depth=th,verts=4,
                       rot=(math.radians(-18-row*8),0,ta))
            assign_mat(tooth,mats['tooth']); link(col,tooth); objs.append(tooth)

    # Lower teeth: 3 rows × 8 teeth
    for row in range(3):
        rs=1.0-row*0.18; rofs=row*0.05
        for ti2 in range(8):
            ta=math.radians(-28+ti2*9)
            tx=0.80*rs*math.sin(ta); tz=0.92+rofs
            ts=0.048-row*0.010; th=0.12-row*0.025
            tooth=prim('cone',f'KC_ToothLo_R{row}_{ti2}',loc=(tx,0.24,tz),r1=ts,r2=0.004,depth=th,verts=4,
                       rot=(math.radians(162+row*7),0,ta))
            assign_mat(tooth,mats['tooth']); link(col,tooth); objs.append(tooth)

    # Tongue (3 segments)
    t_segs=[(0,0.35,1.08,0.22),(0,0.55,1.18,0.18),(0,0.72,1.24,0.14)]
    for tsi2,(tx,ty,tz,tr) in enumerate(t_segs):
        ts2=prim('cyl',f'KC_Tongue_{tsi2}',loc=(tx,ty,tz),size=tr,depth=0.24,verts=10)
        ts2.scale=(1.0,2.2,0.50); bpy.ops.object.transform_apply(scale=True)
        assign_mat(ts2,mats['flesh']); add_sub(ts2,1); smart_uv(ts2); link(col,ts2); objs.append(ts2)
    # Forked tongue tips
    for side,sx in [('L',-0.10),('R',0.10)]:
        tip=prim('cone',f'KC_TongueTip_{side}',loc=(sx,0.92,1.28),r1=0.055,r2=0.010,depth=0.22,verts=8,
                 rot=(math.radians(-10),0,math.radians(sx*25)))
        assign_mat(tip,mats['flesh']); link(col,tip); objs.append(tip)

    # 16 taste buds on tongue surface
    for tbi2 in range(16):
        tba=rng.uniform(0,2*math.pi); tbr=rng.uniform(0.05,0.14)
        tbx=tbr*math.cos(tba); tby=0.45+rng.uniform(0,0.30)
        tbz=1.12+tbr*0.30
        tb=prim('sphere',f'KC_TasteBud_{tbi2}',loc=(tbx,tby,tbz),size=0.016,segs=6,rings=4)
        assign_mat(tb,mats['flesh']); link(col,tb); objs.append(tb)

    # 8 drool filaments hanging down
    for dri2 in range(8):
        dra=math.radians(-35+dri2*12); drx=0.55*math.sin(dra)
        drlen=rng.uniform(0.25,0.55)
        dr=prim('cone',f'KC_DroolFila_{dri2}',loc=(drx,0.30,0.95-drlen*0.5),r1=0.012,r2=0.003,depth=drlen,verts=4)
        assign_mat(dr,mats['slime']); link(col,dr); objs.append(dr)
    return objs

def build_eyes(mats, col):
    """3 main compound eyes (3-layer) + 4 eye stalks."""
    objs=[]
    eye_pos=[(0,1.22,1.55),(-0.52,1.10,1.38),( 0.52,1.10,1.38)]
    for ei2,(ex,ey,ez) in enumerate(eye_pos):
        # Socket
        sock=prim('sphere',f'KC_EyeSocket_{ei2}',loc=(ex,ey-0.02,ez),size=0.16+ei2*0.01,segs=14,rings=10)
        sock.scale=(1.0,0.55,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(sock,mats['eye']); link(col,sock); objs.append(sock)
        # Sclera
        eye_s=prim('sphere',f'KC_Eye_{ei2}',loc=(ex,ey+0.02,ez),size=0.13+ei2*0.01,segs=14,rings=10)
        eye_s.scale=(1.0,0.52,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(eye_s,mats['eye']); link(col,eye_s); objs.append(eye_s)
        # Iris
        iris=prim('cyl',f'KC_Iris_{ei2}',loc=(ex,ey+0.10,ez),size=0.085,depth=0.015,verts=16,rot=(math.radians(90),0,0))
        assign_mat(iris,mats['iris']); link(col,iris); objs.append(iris)
        # Pupil
        pupil=prim('cyl',f'KC_Pupil_{ei2}',loc=(ex,ey+0.13,ez),size=0.042,depth=0.010,verts=10,rot=(math.radians(90),0,0))
        assign_mat(pupil,mats['eye']); link(col,pupil); objs.append(pupil)
        # Outer ring
        ering=prim('torus',f'KC_EyeRing_{ei2}',loc=(ex,ey+0.04,ez),major=0.155,minor=0.022,maj_seg=20,min_seg=6,rot=(math.radians(90),0,0))
        assign_mat(ering,mats['flesh']); link(col,ering); objs.append(ering)

    # 4 eye stalks with smaller eyes
    stalk_pos=[(-1.05,0.60,1.70),( 1.05,0.60,1.70),(-0.80,0.90,1.90),( 0.80,0.90,1.90)]
    for sti2,(stx,sty,stz) in enumerate(stalk_pos):
        # Stalk tube
        stalk=seg_obj(f'KC_EyeStalk_{sti2}',(stx*0.60,sty*0.55,1.20),(stx,sty,stz),0.040,mats['flesh'],col,verts=8)
        objs.append(stalk)
        # Eye on stalk tip
        se=prim('sphere',f'KC_EyeStalk_Eye_{sti2}',loc=(stx,sty+0.04,stz),size=0.068,segs=10,rings=8)
        se.scale=(1.0,0.55,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(se,mats['eye']); link(col,se); objs.append(se)
        si_iris=prim('cyl',f'KC_SIris_{sti2}',loc=(stx,sty+0.06,stz),size=0.040,depth=0.010,verts=10,rot=(math.radians(90),0,0))
        assign_mat(si_iris,mats['iris']); link(col,si_iris); objs.append(si_iris)
    return objs

def build_tentacles(mats, col):
    """16 tentacles: 4 attack, 6 sucker, 4 whip, 2 grab arms."""
    objs=[]
    # ── 4 attack tentacles (thick, short, front-facing) ──
    for ai2 in range(4):
        aa=math.radians(-30+ai2*20)
        ax=0.70*math.sin(aa); ay=0.80; az=1.10
        for seg in range(3):
            t=(seg+0.5)/3; r=0.12-seg*0.025
            sx2=ax*(1+seg*0.5); sz2=az-seg*0.18
            sc=seg_obj(f'KC_TentAttack_{ai2}_{seg}',(ax*(1+max(0,seg-1)*0.5),ay,az-max(0,seg-1)*0.18),(sx2+ax*0.5,ay+0.12,sz2-0.18),r,mats['flesh'],col,verts=10)
            objs.append(sc)
        tip=prim('cone',f'KC_TentAttackTip_{ai2}',loc=(ax*2.5,ay+0.36,az-0.54),r1=0.040,r2=0.006,depth=0.22,verts=6)
        assign_mat(tip,mats['flesh']); link(col,tip); objs.append(tip)

    # ── 6 sucker tentacles (medium, with sucker disc rows) ──
    for sui2 in range(6):
        sa2=math.radians(sui2*60+10)
        sx3=1.10*math.cos(sa2); sy3=1.10*math.sin(sa2)*0.55; sz3=1.0
        for seg in range(4):
            r2=0.088-seg*0.016
            sp=seg_obj(f'KC_TentSucker_{sui2}_{seg}',(sx3*(1+seg*0.38),sy3,sz3-seg*0.28),(sx3*(1+(seg+1)*0.38),sy3+0.10,sz3-(seg+1)*0.28),r2,mats['flesh'],col,verts=10)
            objs.append(sp)
            # 3 sucker discs per segment
            for sdi2 in range(3):
                sda=math.radians(sdi2*120)
                sdx=sx3*(1+(seg+0.5)*0.38)+r2*1.2*math.cos(sda)
                sdz=sz3-(seg+0.5)*0.28+r2*1.2*math.sin(sda)*0.55
                sd=prim('cyl',f'KC_Sucker_{sui2}_{seg}_{sdi2}',loc=(sdx,sy3-0.05,sdz),size=r2*0.65,depth=0.020,verts=8,rot=(math.radians(90),0,0))
                assign_mat(sd,mats['flesh']); link(col,sd); objs.append(sd)

    # ── 4 whip tentacles (long, 3-segment, thin) ──
    for wi2 in range(4):
        wa=math.radians(wi2*90+22)
        wx=1.30*math.cos(wa); wy=1.30*math.sin(wa)*0.50; wz=0.90
        seg_ends=[(wx*0.5,wy,wz+0.20),(wx*0.9,wy+0.30,wz+0.05),(wx*1.6,wy+0.60,wz-0.30),(wx*2.2,wy+0.90,wz-0.70)]
        for si3 in range(3):
            r3=0.060-si3*0.015
            ws=seg_obj(f'KC_TentWhip_{wi2}_{si3}',seg_ends[si3],seg_ends[si3+1],r3,mats['flesh'],col,verts=8)
            objs.append(ws)

    # ── 2 massive grab arms with claw tips ──
    for gi2,gsx in [('L',-1),('R',1)]:
        gb_pts=[(gsx*1.10,0,1.30),(gsx*1.60,0.40,1.10),(gsx*2.10,0.80,0.80),(gsx*2.50,1.20,0.50)]
        for si4 in range(3):
            r4=0.15-si4*0.022
            gb=seg_obj(f'KC_TentGrab_{gi2}_{si4}',gb_pts[si4],gb_pts[si4+1],r4,mats['flesh'],col,verts=12)
            objs.append(gb)
        # 3 claw tips
        for ci2 in range(3):
            ca2=math.radians(-20+ci2*20)
            cx=gb_pts[-1][0]+gsx*0.12*math.cos(ca2)
            cz=gb_pts[-1][2]+0.12*math.sin(ca2)
            claw=prim('cone',f'KC_GrabClaw_{gi2}_{ci2}',loc=(cx,gb_pts[-1][1]+0.06,cz),r1=0.035,r2=0.005,depth=0.28,verts=4,
                      rot=(0,math.radians(gsx*(-20+ci2*15)),0))
            assign_mat(claw,mats['tooth']); link(col,claw); objs.append(claw)
    return objs

def build_treasure_interior(mats, col):
    """Interior glow + gold coins, gems, chalice, bars spilling out."""
    objs=[]
    # Glow dome
    glow=prim('sphere','KC_InteriorGlow',loc=(0,0.10,1.22),size=1.05,segs=16,rings=12)
    glow.scale=(0.84,0.34,0.32); bpy.ops.object.transform_apply(scale=True)
    assign_mat(glow,mats['bio']); link(col,glow); objs.append(glow)
    # 12 gold coins
    for ci2 in range(12):
        ca2=rng.uniform(0,2*math.pi); cr2=rng.uniform(0.20,0.80)
        cx=cr2*math.cos(ca2); cy=rng.uniform(0.20,0.80)
        cz=0.80+rng.uniform(-0.10,0.15)
        coin=prim('cyl',f'KC_GoldCoin_{ci2}',loc=(cx,cy,cz),size=0.055,depth=0.014,verts=12,rot=(rng.uniform(0,0.6),rng.uniform(0,0.6),0))
        assign_mat(coin,mats['gold']); link(col,coin); objs.append(coin)
    # 6 gem clusters
    gem_cols=[(0.65,0.12,1.24),(-.40,0.55,1.18),(0.30,0.40,0.95),(-.60,0.30,1.10),(0.12,0.72,1.20),(-.20,0.60,1.02)]
    for gi2,(gx,gy,gz) in enumerate(gem_cols):
        gem=prim('sphere',f'KC_Gem_{gi2}',loc=(gx,gy,gz),size=rng.uniform(0.040,0.075),segs=8,rings=6)
        assign_mat(gem,mats['gem']); link(col,gem); objs.append(gem)
    # Chalice
    chal=prim('cyl','KC_Chalice',loc=(-0.28,0.55,0.90),size=0.065,depth=0.18,verts=12,rot=(math.radians(-45),0,0))
    assign_mat(chal,mats['gold']); link(col,chal); objs.append(chal)
    # 3 gold bar ingots
    for bi3 in range(3):
        bar=prim('cube',f'KC_TreasureBar_{bi3}',loc=(0.20+bi3*0.10,0.40+bi3*0.06,0.92),size=0.10)
        bar.scale=(1.8,0.80,0.40); bar.rotation_euler=(0,0,math.radians(bi3*18))
        bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(bar,mats['gold']); link(col,bar); objs.append(bar)
    return objs

def build_scary_attachments(mats, col):
    """Broken mast, ink sac, victim bones, biolum crack lines, slime ropes."""
    objs=[]
    # ── Broken ship mast impaled through lid ──
    mast=prim('cyl','KC_ShipMast',loc=(0.28,-0.55,1.90),size=0.075,depth=2.20,verts=10,rot=(math.radians(-50),0,math.radians(12)))
    assign_mat(mast,mats['wood']); smart_uv(mast); link(col,mast); objs.append(mast)
    # Mast flag
    flag=prim('cube','KC_MastFlag',loc=(0.42,-0.40,2.70),size=0.30)
    flag.scale=(0.04,0.55,0.30); flag.rotation_euler=(math.radians(-50),0,math.radians(12))
    bpy.ops.object.transform_apply(scale=True,rotation=True)
    assign_mat(flag,mats['wood']); link(col,flag); objs.append(flag)
    # Mast cross beam
    cb=prim('cyl','KC_MastCrossbeam',loc=(0.22,-0.38,2.42),size=0.032,depth=0.68,verts=8,rot=(math.radians(-50),math.radians(90),0))
    assign_mat(cb,mats['wood']); link(col,cb); objs.append(cb)

    # ── Ink sac apparatus on back ──
    ink_sac=prim('sphere','KC_InkSacApparatus',loc=(0,-0.96,1.30),size=0.32,segs=14,rings=10)
    ink_sac.scale=(1.0,0.78,0.78); bpy.ops.object.transform_apply(scale=True)
    ink_mat=bpy.data.materials.new('Mat_KC_Ink'); ink_mat.use_nodes=True
    ink_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.01,0.01,0.02,1)
    ink_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.12
    assign_mat(ink_sac,ink_mat); add_sub(ink_sac,1); link(col,ink_sac); objs.append(ink_sac)
    # Ink nozzle tube
    nozzle=prim('cyl','KC_InkNozzle',loc=(0,-1.22,1.38),size=0.048,depth=0.30,verts=8,rot=(math.radians(40),0,0))
    assign_mat(nozzle,ink_mat); link(col,nozzle); objs.append(nozzle)
    # Ink drip
    ink_drip=prim('sphere','KC_InkDrip',loc=(0,-1.28,1.26),size=0.055,segs=8,rings=6)
    assign_mat(ink_drip,ink_mat); link(col,ink_drip); objs.append(ink_drip)

    # ── 8 victim bones embedded in chest hull ──
    bone_pos=[
        ( 1.12, 0.22,1.12),(-1.12, 0.22,1.12),( 1.08,-0.35,0.98),(-1.08,-0.35,0.98),
        ( 0.85, 0.75,1.35),(-0.85, 0.75,1.35),( 0.50,-0.82,0.88),(-0.50,-0.82,0.88),
    ]
    for vbi,(vbx,vby,vbz) in enumerate(bone_pos):
        vb=prim('cone',f'KC_VictimBone_{vbi}',loc=(vbx,vby,vbz),r1=0.024,r2=0.006,depth=0.22,verts=5,
                rot=(rng.uniform(-0.8,0.8),rng.uniform(-0.5,0.5),0))
        assign_mat(vb,mats['tooth']); link(col,vb); objs.append(vb)

    # ── 12 bioluminescent crack lines on hull ──
    crack_pos=[
        ( 0.88,0.52,1.20,55),(-0.88,0.52,1.20,125),( 0.72,-0.68,0.95,88),(-0.72,-0.68,0.95,92),
        ( 1.08, 0.10,1.05,72),(-1.08, 0.10,1.05,108),( 0.44, 0.88,1.42,44),(-0.44, 0.88,1.42,136),
        ( 0.88,-0.22,1.42,60),(-0.88,-0.22,1.42,120),( 0.28,-0.90,1.15,80),(-0.28,-0.90,1.15,100),
    ]
    for cki,(ckx,cky,ckz,ckr) in enumerate(crack_pos):
        crack=prim('cyl',f'KC_BioVeinCrack_{cki}',loc=(ckx,cky,ckz),size=0.010,depth=0.28,verts=4,rot=(0,math.radians(ckr),0))
        assign_mat(crack,mats['bio']); link(col,crack); objs.append(crack)

    # ── 6 massive slime drool rope strands ──
    for sli2 in range(6):
        sla=math.radians(-25+sli2*12); slx=0.60*math.sin(sla); sllen=rng.uniform(0.55,1.10)
        slr=prim('cone',f'KC_SlimeDrool_{sli2}',loc=(slx,0.28,1.05-sllen*0.5),r1=0.018,r2=0.005,depth=sllen,verts=5)
        assign_mat(slr,mats['slime']); link(col,slr); objs.append(slr)
    return objs

# ═══════════════════════════════════════════════════════════════════
#  ASSEMBLE
# ═══════════════════════════════════════════════════════════════════

def main():
    clear_scene()
    col=new_col('IsleTrial_Boss_KrakenChest')
    mats=build_materials()
    all_objs=[]
    all_objs+=build_chest_hull(mats,col)
    all_objs+=build_mouth_teeth_tongue(mats,col)
    all_objs+=build_eyes(mats,col)
    all_objs+=build_tentacles(mats,col)
    all_objs+=build_treasure_interior(mats,col)
    all_objs+=build_scary_attachments(mats,col)
    bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0))
    root=bpy.context.active_object; root.name='Boss_KrakenChest_ROOT'; link(col,root)
    for obj in all_objs:
        if obj.parent is None: obj.parent=root
    mc=sum(1 for o in col.objects if o.type=='MESH')
    print("="*60)
    print("[IsleTrial] Boss: Kraken Chest King – MAXIMUM DETAIL")
    print(f"  Mesh objects : {mc}")
    print(f"  Materials    : {len(bpy.data.materials)}")
    print("  Tentacles    : 16 (4 attack + 6 sucker + 4 whip + 2 grab)")
    print("  Teeth        : 24 upper + 24 lower (3 rows each)")
    print("  Scary adds   : mast impaled, ink sac, 8 victim bones,")
    print("                 12 biolum cracks, 6 slime ropes, 4 eye stalks")
    print("  Next: run 12_Boss_KrakenChest_Rig.py")
    print("="*60)

main()
