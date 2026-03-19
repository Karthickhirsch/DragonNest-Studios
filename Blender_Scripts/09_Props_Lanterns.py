"""
IsleTrial — Props: Lanterns  (03-D)
Blender 4.x  •  Python Script

Variety objects (each → Unity prefab):
──────────────────────────────────────────────────────
  Prop_Lantern_Mounted_A   – hexagonal iron cage, L-bracket arm
  Prop_Lantern_Mounted_B   – square cage variant, chain hang
  Prop_Lantern_Handheld_A  – cylindrical brass body with handle
  Prop_Lantern_Post_A      – lantern on a wooden post (env. scatter)

Materials (dual-path)
  Mat_Lantern_Iron   – dark iron cage
  Mat_Lantern_Brass  – warm brass body
  Mat_Lantern_Glass  – emissive amber glass (transmission)
  Mat_Lantern_Flame  – hot orange emissive flame proxy
  Mat_Lantern_Chain  – dark chain links
  Mat_Lantern_Wood   – post wood

Empties (Unity Light positions)
  Lantern_Mounted_A_LightPoint
  Lantern_Mounted_B_LightPoint
  Lantern_Handheld_A_LightPoint
  Lantern_Post_A_LightPoint
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ──────────────────────────────────────────────
#  SCENE / HELPERS
# ──────────────────────────────────────────────

def setup_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

def new_col(name):
    c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c

def link_obj(col, obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)

def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True); bpy.context.view_layer.objects.active=obj

def assign_mat(obj, mat):
    if obj.data.materials: obj.data.materials[0]=mat
    else: obj.data.materials.append(mat)

def uv_unwrap(obj):
    activate(obj); bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

def smooth_shade(obj):
    for p in obj.data.polygons: p.use_smooth=True

def make_root(name, loc=(0,0,0)):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    r=bpy.context.active_object; r.name=name; return r

def make_light_empty(name, loc):
    bpy.ops.object.empty_add(type='SPHERE', radius=0.04, location=loc)
    e=bpy.context.active_object; e.name=name; return e

# ──────────────────────────────────────────────
#  MATERIAL HELPERS
# ──────────────────────────────────────────────

def _n(nodes, ntype, loc, label=None):
    n=nodes.new(ntype); n.location=loc
    if label: n.label=label; n.name=label; return n

def _img(nodes, slot, loc):
    n=nodes.new('ShaderNodeTexImage'); n.location=loc; n.label=slot; n.name=slot; return n

def _cmap(nodes, links, scale=(10,10,10), loc=(-900,0)):
    tc=_n(nodes,'ShaderNodeTexCoord',(loc[0],loc[1]))
    mp=_n(nodes,'ShaderNodeMapping',(loc[0]+200,loc[1]))
    mp.inputs['Scale'].default_value=scale
    links.new(tc.outputs['UV'],mp.inputs['Vector']); return mp

def _bump(nodes, links, h_sock, s=0.35, d=0.006):
    b=_n(nodes,'ShaderNodeBump',(-100,-200))
    b.inputs['Strength'].default_value=s; b.inputs['Distance'].default_value=d
    links.new(h_sock,b.inputs['Height']); return b

# ──────────────────────────────────────────────
#  MATERIALS
# ──────────────────────────────────────────────

def build_iron_mat(name, base=(0.06,0.06,0.06)):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(400,0)); bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value=0.90; bsdf.inputs['Roughness'].default_value=0.55
    mp=_cmap(N,L,scale=(14,14,14),loc=(-900,0))
    noise=_n(N,'ShaderNodeTexNoise',(-680,80)); noise.inputs['Scale'].default_value=20.0
    noise.inputs['Detail'].default_value=5.0; L.new(mp.outputs['Vector'],noise.inputs['Vector'])
    dark=tuple(max(0,c*0.35) for c in base)
    cr=_n(N,'ShaderNodeValToRGB',(-420,80))
    cr.color_ramp.elements[0].color=(*dark,1.0); cr.color_ramp.elements[1].color=(*base,1.0)
    L.new(noise.outputs['Fac'],cr.inputs['Fac'])
    b=_bump(N,L,noise.outputs['Fac'],0.30,0.005)
    L.new(b.outputs['Normal'],bsdf.inputs['Normal'])
    img=_img(N,f'[UNITY] {name}_Albedo',(-680,-300))
    mix=_n(N,'ShaderNodeMixRGB',(-150,80),'Mix_Albedo'); mix.inputs['Fac'].default_value=0.0
    L.new(cr.outputs['Color'],mix.inputs['Color1']); L.new(img.outputs['Color'],mix.inputs['Color2'])
    L.new(mix.outputs['Color'],bsdf.inputs['Base Color']); return mat


def build_brass_mat(name, base=(0.72,0.52,0.14)):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(400,0)); bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value=0.92; bsdf.inputs['Roughness'].default_value=0.28
    mp=_cmap(N,L,scale=(12,12,12),loc=(-900,0))
    noise=_n(N,'ShaderNodeTexNoise',(-680,80)); noise.inputs['Scale'].default_value=16.0
    L.new(mp.outputs['Vector'],noise.inputs['Vector'])
    b=_bump(N,L,noise.outputs['Fac'],0.18,0.004); L.new(b.outputs['Normal'],bsdf.inputs['Normal'])
    bsdf.inputs['Base Color'].default_value=(*base,1.0)
    img=_img(N,f'[UNITY] {name}_Albedo',(-680,-300))
    mix=_n(N,'ShaderNodeMixRGB',(-150,80),'Mix_Unity'); mix.inputs['Fac'].default_value=0.0
    mix.inputs['Color1'].default_value=(*base,1.0); L.new(img.outputs['Color'],mix.inputs['Color2'])
    L.new(mix.outputs['Color'],bsdf.inputs['Base Color']); return mat


def build_glass_mat(name):
    mat=bpy.data.materials.new(name); mat.use_nodes=True; mat.blend_method='BLEND'
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(400,0)); bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value=(1.0,0.90,0.60,1.0)
    bsdf.inputs['Alpha'].default_value=0.30
    bsdf.inputs['Roughness'].default_value=0.05
    try:
        bsdf.inputs['Transmission Weight'].default_value=0.90
        bsdf.inputs['Emission Color'].default_value=(1.0,0.85,0.40,1.0)
        bsdf.inputs['Emission Strength'].default_value=1.8
    except KeyError: pass
    return mat


def build_flame_mat(name):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(300,0)); bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value=(1.0,0.55,0.05,1.0)
    try:
        bsdf.inputs['Emission Color'].default_value=(1.0,0.55,0.05,1.0)
        bsdf.inputs['Emission Strength'].default_value=4.5
    except KeyError: pass
    bsdf.inputs['Roughness'].default_value=1.0
    return mat


def build_wood_mat(name, dark=(0.28,0.16,0.05), light=(0.48,0.30,0.12)):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(400,0)); bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value=0.88
    mp=_cmap(N,L,scale=(9,9,9),loc=(-800,0))
    wave=_n(N,'ShaderNodeTexWave',(-600,80)); wave.wave_type='RINGS'; wave.rings_direction='Z'
    wave.inputs['Scale'].default_value=5.0; wave.inputs['Distortion'].default_value=4.5
    L.new(mp.outputs['Vector'],wave.inputs['Vector'])
    cr=_n(N,'ShaderNodeValToRGB',(-360,80))
    cr.color_ramp.elements[0].color=(*dark,1.0); cr.color_ramp.elements[1].color=(*light,1.0)
    L.new(wave.outputs['Color'],cr.inputs['Fac']); L.new(cr.outputs['Color'],bsdf.inputs['Base Color'])
    return mat

# ──────────────────────────────────────────────
#  CHAIN LINK HELPER
# ──────────────────────────────────────────────

def chain_link(name, center, rot_z=0, mat=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.025, minor_radius=0.007,
                                     major_segments=10, minor_segments=6, location=center)
    lk=bpy.context.active_object; lk.name=name
    lk.scale=(1.0,1.60,1.0); lk.rotation_euler.z=math.radians(rot_z)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    if mat: assign_mat(lk, mat)
    return lk

# ──────────────────────────────────────────────
#  CANDLE + FLAME (shared by all lanterns)
# ──────────────────────────────────────────────

def build_candle_flame(base_z, mats):
    objs=[]
    # Candle
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.012, depth=0.060,
                                        location=(0,0,base_z+0.030))
    candle=bpy.context.active_object; candle.name='_Candle'
    candle_mat=bpy.data.materials.new('Mat_Candle_Wax')
    candle_mat.use_nodes=True
    candle_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.94,0.90,0.80,1.0)
    candle_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.82
    assign_mat(candle, candle_mat); objs.append(candle)
    # Flame
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.010, radius2=0.001,
                                    depth=0.032, location=(0,0,base_z+0.076))
    flame=bpy.context.active_object; flame.name='_Flame'
    assign_mat(flame, mats['flame']); objs.append(flame)
    return objs

# ──────────────────────────────────────────────
#  LANTERN A — HEXAGONAL MOUNTED (iron cage)
# ──────────────────────────────────────────────

def build_lantern_mounted_a(mats, col):
    objs=[]

    # L-bracket arm
    bpy.ops.mesh.primitive_cube_add(location=(0,-0.125,0.80))
    arm_h=bpy.context.active_object; arm_h.name='Lantern_Mounted_A_ArmH'
    arm_h.scale=(0.028,0.125,0.028); bpy.ops.object.transform_apply(scale=True)
    assign_mat(arm_h, mats['iron']); objs.append(arm_h)

    bpy.ops.mesh.primitive_cube_add(location=(0,0.0,0.875))
    arm_v=bpy.context.active_object; arm_v.name='Lantern_Mounted_A_ArmV'
    arm_v.scale=(0.028,0.028,0.075); bpy.ops.object.transform_apply(scale=True)
    assign_mat(arm_v, mats['iron']); objs.append(arm_v)

    # Hanging ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.030, minor_radius=0.007,
                                     major_segments=10, minor_segments=6,
                                     location=(0,0,0.970))
    ring=bpy.context.active_object; ring.name='Lantern_Mounted_A_Ring'
    assign_mat(ring, mats['iron']); objs.append(ring)

    # 3-link chain
    for li in range(3):
        lk=chain_link(f'Lantern_Mounted_A_Chain_{li}', (0,0,0.940-li*0.048),
                      rot_z=90 if li%2==0 else 0, mat=mats['chain'])
        objs.append(lk)

    # Hexagonal cage frame — top plate
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.165, depth=0.018,
                                        location=(0,0,0.800))
    top_plate=bpy.context.active_object; top_plate.name='Lantern_Mounted_A_TopPlate'
    top_plate.scale=(1.0,1.0,1.0); bpy.ops.object.transform_apply(scale=True)
    assign_mat(top_plate, mats['iron']); objs.append(top_plate)

    # Top pyramidal cap
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.168, radius2=0.040,
                                    depth=0.085, location=(0,0,0.850))
    cap=bpy.context.active_object; cap.name='Lantern_Mounted_A_Cap'
    assign_mat(cap, mats['iron']); objs.append(cap)

    # 6 vertical bars
    for i in range(6):
        ang=math.radians(i*60)
        x=math.cos(ang)*0.148; y=math.sin(ang)*0.148
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.008, depth=0.260,
                                            location=(x,y,0.670))
        bar=bpy.context.active_object; bar.name=f'Lantern_Mounted_A_Bar_{i}'
        assign_mat(bar, mats['iron']); objs.append(bar)

    # Bottom plate
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.155, depth=0.018,
                                        location=(0,0,0.538))
    bot=bpy.context.active_object; bot.name='Lantern_Mounted_A_BotPlate'
    assign_mat(bot, mats['iron']); objs.append(bot)

    # Glass panels (6 sides)
    for i in range(6):
        ang = math.radians(i*60 + 30)
        x=math.cos(ang)*0.140; y=math.sin(ang)*0.140
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(x,y,0.670))
        glass=bpy.context.active_object; glass.name=f'Lantern_Mounted_A_Glass_{i}'
        glass.scale=(0.080,0.001,0.120); glass.rotation_euler.z=math.radians(i*60)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(glass, mats['glass']); objs.append(glass)

    # Candle + flame
    candle_objs=build_candle_flame(0.560, mats)
    for o in candle_objs: o.name=o.name.replace('_','Lantern_Mounted_A_',1); objs.append(o)

    # Light point empty
    light_pt=make_light_empty('Lantern_Mounted_A_LightPoint', (0,0,0.680))
    objs.append(light_pt)

    root=make_root('Prop_Lantern_Mounted_A_ROOT')
    for o in objs: o.parent=root; link_obj(col,o)
        
    for o in objs:
        if o.type=='MESH': uv_unwrap(o)
    link_obj(col,root)
    print(f"[Props] Lantern_Mounted_A LightPoint: (0, 0, 0.68)")

# ──────────────────────────────────────────────
#  LANTERN B — SQUARE CAGE, CHAIN HANG
# ──────────────────────────────────────────────

def build_lantern_mounted_b(mats, col):
    objs=[]

    # Square cage body
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0.650))
    cage=bpy.context.active_object; cage.name='Lantern_Mounted_B_Cage'
    cage.scale=(0.140,0.140,0.145); bpy.ops.object.transform_apply(scale=True)
    # Hollow out (remove inside)
    activate(cage)
    bpy.ops.object.mode_set(mode='EDIT')
    bm=bmesh.from_edit_mesh(cage.data)
    bmesh.ops.inset_individual(bm, faces=list(bm.faces), thickness=0.018, depth=-0.002)
    bmesh.update_edit_mesh(cage.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    bev=cage.modifiers.new('Bevel','BEVEL'); bev.width=0.006; bev.segments=2
    assign_mat(cage, mats['iron']); objs.append(cage)

    # Glass (4 sides)
    for ang, side in ((0,'F'),(90,'R'),(180,'B'),(270,'L')):
        a=math.radians(ang)
        x=math.cos(a)*0.142; y=math.sin(a)*0.142
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(x,y,0.650))
        gl=bpy.context.active_object; gl.name=f'Lantern_Mounted_B_Glass_{side}'
        gl.scale=(0.116,0.001,0.118); gl.rotation_euler.z=math.radians(ang)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(gl, mats['glass']); objs.append(gl)

    # Pyramidal top
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.155, radius2=0.030,
                                    depth=0.080, location=(0,0,0.830))
    cap2=bpy.context.active_object; cap2.name='Lantern_Mounted_B_Cap'
    cap2.rotation_euler.z=math.radians(45); bpy.ops.object.transform_apply(rotation=True)
    assign_mat(cap2, mats['iron']); objs.append(cap2)

    # Hanging ring + 4 chains
    bpy.ops.mesh.primitive_torus_add(major_radius=0.028, minor_radius=0.006,
                                     major_segments=10, minor_segments=6, location=(0,0,0.885))
    ring2=bpy.context.active_object; ring2.name='Lantern_Mounted_B_Ring'
    assign_mat(ring2, mats['chain']); objs.append(ring2)

    for li in range(4):
        lk=chain_link(f'Lantern_Mounted_B_Chain_{li}', (0,0,0.910+li*0.045),
                      rot_z=90 if li%2==0 else 0, mat=mats['chain'])
        objs.append(lk)

    # Candle
    candle_objs=build_candle_flame(0.510, mats)
    for o in candle_objs: o.name=o.name.replace('_','LanternB_',1); objs.append(o)

    light_pt=make_light_empty('Lantern_Mounted_B_LightPoint', (0,0,0.660))
    objs.append(light_pt)

    root=make_root('Prop_Lantern_Mounted_B_ROOT')
    for o in objs: o.parent=root; link_obj(col,o)
    for o in objs:
        if o.type=='MESH': uv_unwrap(o)
    link_obj(col,root)
    print(f"[Props] Lantern_Mounted_B LightPoint: (0, 0, 0.66)")

# ──────────────────────────────────────────────
#  LANTERN C — HAND-HELD CYLINDRICAL BRASS
# ──────────────────────────────────────────────

def build_lantern_handheld(mats, col):
    objs=[]

    # Oil reservoir base (slightly wider disc)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.092, depth=0.025,
                                        location=(0,0,0.0125))
    base=bpy.context.active_object; base.name='Lantern_Handheld_A_Base'
    assign_mat(base, mats['brass']); objs.append(base)

    # Main cylindrical brass body
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.080, depth=0.180,
                                        location=(0,0,0.115))
    body=bpy.context.active_object; body.name='Lantern_Handheld_A_Body'
    bev_b=body.modifiers.new('Bevel','BEVEL'); bev_b.width=0.008; bev_b.segments=2
    assign_mat(body, mats['brass']); objs.append(body)

    # Glass cylinder insert
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.072, depth=0.155,
                                        location=(0,0,0.115))
    gl=bpy.context.active_object; gl.name='Lantern_Handheld_A_Glass'
    assign_mat(gl, mats['glass']); objs.append(gl)

    # Top cap
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.085, radius2=0.038,
                                    depth=0.060, location=(0,0,0.235))
    top=bpy.context.active_object; top.name='Lantern_Handheld_A_TopCap'
    assign_mat(top, mats['brass']); objs.append(top)

    # Flip-up glass shield hinge (small flat rectangle on side)
    bpy.ops.mesh.primitive_cube_add(location=(0.082, 0, 0.200))
    shield=bpy.context.active_object; shield.name='Lantern_Handheld_A_Shield'
    shield.scale=(0.010, 0.060, 0.040); bpy.ops.object.transform_apply(scale=True)
    assign_mat(shield, mats['brass']); objs.append(shield)

    # Semicircular carrying handle
    pts_handle=[]
    for i in range(13):
        ang=math.pi * i / 12
        pts_handle.append((math.cos(ang)*0.055, 0, 0.270 + math.sin(ang)*0.055))
    for i, pt in enumerate(pts_handle):
        if i == 0 or i == len(pts_handle)-1: continue  # skip endpoints
        if i == 1:
            # Build tube from first to last through arc
            bm_h=bmesh.new()
            all_r=[]
            for pp in pts_handle:
                ring=[]
                for vi in range(6):
                    ang2=2*math.pi*vi/6
                    ring.append(bm_h.verts.new((pp[0]+math.cos(ang2)*0.006,
                                                pp[1]+math.sin(ang2)*0.006, pp[2])))
                all_r.append(ring)
            for ri in range(len(all_r)-1):
                for vi in range(6):
                    a=all_r[ri][vi]; b=all_r[ri][(vi+1)%6]
                    c=all_r[ri+1][(vi+1)%6]; d=all_r[ri+1][vi]
                    try: bm_h.faces.new([a,b,c,d])
                    except: pass
            mh=bpy.data.meshes.new('Lantern_Handheld_A_Handle')
            bm_h.to_mesh(mh); bm_h.free()
            handle_obj=bpy.data.objects.new('Lantern_Handheld_A_Handle',mh)
            bpy.context.scene.collection.objects.link(handle_obj)
            smooth_shade(handle_obj)
            assign_mat(handle_obj, mats['brass']); objs.append(handle_obj)
            break

    # Candle inside
    candle_objs=build_candle_flame(0.028, mats)
    for o in candle_objs: o.name=o.name.replace('_','LanternHH_',1); objs.append(o)

    light_pt=make_light_empty('Lantern_Handheld_A_LightPoint', (0,0,0.115))
    objs.append(light_pt)

    root=make_root('Prop_Lantern_Handheld_A_ROOT')
    for o in objs: o.parent=root; link_obj(col,o)
    for o in objs:
        if o.type=='MESH': uv_unwrap(o)
    link_obj(col,root)
    print(f"[Props] Lantern_Handheld_A LightPoint: (0, 0, 0.115)")

# ──────────────────────────────────────────────
#  LANTERN D — POST LANTERN (environment scatter)
# ──────────────────────────────────────────────

def build_lantern_post(mats, col):
    """Lantern mounted on top of a 1.4m wooden post — great island scatter."""
    objs=[]

    # Wooden post
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.042, depth=1.40,
                                        location=(0,0,0.70))
    post=bpy.context.active_object; post.name='Lantern_Post_A_Post'
    assign_mat(post, mats['wood']); objs.append(post)

    # Post base anchor (buried part disc)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.062, depth=0.080,
                                        location=(0,0,0.040))
    base=bpy.context.active_object; base.name='Lantern_Post_A_Base'
    assign_mat(base, mats['iron']); objs.append(base)

    # Arm bracket
    bpy.ops.mesh.primitive_cube_add(location=(0.080, 0, 1.460))
    arm=bpy.context.active_object; arm.name='Lantern_Post_A_Arm'
    arm.scale=(0.080, 0.024, 0.024); bpy.ops.object.transform_apply(scale=True)
    assign_mat(arm, mats['iron']); objs.append(arm)

    # Hexagonal cage (same as Mounted_A but offset to top of post)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.148, depth=0.018,
                                        location=(0.160,0,1.560))
    tp=bpy.context.active_object; tp.name='Lantern_Post_A_TopPlate'
    assign_mat(tp, mats['iron']); objs.append(tp)

    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.152, radius2=0.035,
                                    depth=0.075, location=(0.160,0,1.608))
    cap=bpy.context.active_object; cap.name='Lantern_Post_A_Cap'
    assign_mat(cap, mats['iron']); objs.append(cap)

    for i in range(6):
        ang=math.radians(i*60)
        x=0.160+math.cos(ang)*0.134; y=math.sin(ang)*0.134
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.007, depth=0.240,
                                            location=(x,y,1.440))
        bar=bpy.context.active_object; bar.name=f'Lantern_Post_A_Bar_{i}'
        assign_mat(bar, mats['iron']); objs.append(bar)

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.138, depth=0.016,
                                        location=(0.160,0,1.318))
    bp=bpy.context.active_object; bp.name='Lantern_Post_A_BotPlate'
    assign_mat(bp, mats['iron']); objs.append(bp)

    for i in range(6):
        ang=math.radians(i*60+30)
        x=0.160+math.cos(ang)*0.126; y=math.sin(ang)*0.126
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(x,y,1.440))
        gl=bpy.context.active_object; gl.name=f'Lantern_Post_A_Glass_{i}'
        gl.scale=(0.072,0.001,0.108); gl.rotation_euler.z=math.radians(i*60)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(gl, mats['glass']); objs.append(gl)

    candle_objs=build_candle_flame(1.328, mats)
    for o in candle_objs: o.name=o.name.replace('_','LanternPost_',1); objs.append(o)

    light_pt=make_light_empty('Lantern_Post_A_LightPoint', (0.160,0,1.440))
    objs.append(light_pt)

    root=make_root('Prop_Lantern_Post_A_ROOT')
    for o in objs: o.parent=root; link_obj(col,o)
    for o in objs:
        if o.type=='MESH': uv_unwrap(o)
    link_obj(col,root)
    print(f"[Props] Lantern_Post_A LightPoint: (0.16, 0, 1.44)")

# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    setup_scene()

    mats = {
        'iron'  : build_iron_mat('Mat_Lantern_Iron',  base=(0.06,0.06,0.06)),
        'brass' : build_brass_mat('Mat_Lantern_Brass', base=(0.72,0.52,0.14)),
        'glass' : build_glass_mat('Mat_Lantern_Glass'),
        'flame' : build_flame_mat('Mat_Lantern_Flame'),
        'chain' : build_iron_mat('Mat_Lantern_Chain', base=(0.10,0.10,0.10)),
        'wood'  : build_wood_mat('Mat_Lantern_Wood'),
    }

    col = new_col('IsleTrial_Props_Lanterns')

    build_lantern_mounted_a(mats, col)
    build_lantern_mounted_b(mats, col)
    build_lantern_handheld(mats, col)
    build_lantern_post(mats, col)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D': sp.shading.type='MATERIAL'
            break

    print("\n" + "="*65)
    print("  IsleTrial — Lantern Props Complete")
    print("="*65)
    print("  Prop_Lantern_Mounted_A  – hex iron cage  + L-bracket")
    print("  Prop_Lantern_Mounted_B  – square cage    + chain hang")
    print("  Prop_Lantern_Handheld_A – brass cylinder + wire handle")
    print("  Prop_Lantern_Post_A     – hex cage on 1.4m wooden post")
    print("  LightPoint empties      → attach Unity Point Light here")
    print("  Collection : IsleTrial_Props_Lanterns")
    print("="*65 + "\n")

main()
