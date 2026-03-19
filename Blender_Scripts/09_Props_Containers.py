"""
IsleTrial — Props: Containers  (03-B)
Blender 4.x  •  Python Script

VARIETY  — 10 prefab-ready objects so random island placement
           never looks repetitive:

  BARRELS  (4 variants)
  ──────────────────────────────────────────────
  Prop_Barrel_Upright_A   – fresh wood, upright, sealed
  Prop_Barrel_Upright_B   – weathered dark, upright, bung visible
  Prop_Barrel_OnSide_A    – lying on its side (rolled off)
  Prop_Barrel_Broken_A    – cracked staves, spilled, tilted

  CRATES  (3 variants)
  ──────────────────────────────────────────────
  Prop_Crate_Sealed_A     – sealed, IsleTrial stamp
  Prop_Crate_Open_A       – lid offset, visible interior
  Prop_Crate_Stack_A      – 2 crates stacked (different sizes)

  TREASURE CHESTS  (3 variants)
  ──────────────────────────────────────────────
  Prop_Chest_Closed_A     – locked, gold trim
  Prop_Chest_Open_A       – lid open ~105°, empty interior
  Prop_Chest_Loot_A       – open, gold coins + gem visible

Materials (dual-path: procedural + [UNITY] image slots)
  Mat_Barrel_Wood · Mat_Barrel_Wood_Old · Mat_Barrel_Iron
  Mat_Crate_Wood  · Mat_Crate_Iron
  Mat_Chest_Wood  · Mat_Chest_Iron · Mat_Chest_Gold · Mat_Chest_Interior
  Mat_Coin_Gold
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ──────────────────────────────────────────────
#  SCENE
# ──────────────────────────────────────────────

def setup_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

def new_col(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def link_obj(col, obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def assign_mat(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def uv_unwrap(obj):
    activate(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

def smooth_shade(obj):
    for p in obj.data.polygons: p.use_smooth = True

def make_root(name, loc=(0,0,0)):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    r = bpy.context.active_object; r.name = name; return r

# ──────────────────────────────────────────────
#  MATERIAL HELPERS
# ──────────────────────────────────────────────

def _n(nodes, ntype, loc, label=None):
    n = nodes.new(ntype); n.location = loc
    if label: n.label=label; n.name=label
    return n

def _img(nodes, slot, loc):
    n=nodes.new('ShaderNodeTexImage'); n.location=loc; n.label=slot; n.name=slot; return n

def _cmap(nodes, links, scale=(8,8,8), loc=(-900,0)):
    tc=_n(nodes,'ShaderNodeTexCoord',(loc[0],loc[1]))
    mp=_n(nodes,'ShaderNodeMapping',(loc[0]+200,loc[1]))
    mp.inputs['Scale'].default_value=scale
    links.new(tc.outputs['UV'],mp.inputs['Vector']); return mp

def _bump(nodes, links, h_sock, s=0.5, d=0.01):
    b=_n(nodes,'ShaderNodeBump',(-100,-200))
    b.inputs['Strength'].default_value=s; b.inputs['Distance'].default_value=d
    links.new(h_sock,b.inputs['Height']); return b

# ──────────────────────────────────────────────
#  MATERIALS
# ──────────────────────────────────────────────

def build_wood_mat(name, dark, light, roughness=0.90, scale=10.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(500,0))
    bsdf=_n(N,'ShaderNodeBsdfPrincipled',(100,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value=roughness
    bsdf.inputs['Metallic'].default_value=0.0
    mp=_cmap(N,L,scale=(scale,scale,scale),loc=(-1000,100))
    wave=_n(N,'ShaderNodeTexWave',(-700,200))
    wave.wave_type='RINGS'; wave.rings_direction='Z'
    wave.inputs['Scale'].default_value=4.5
    wave.inputs['Distortion'].default_value=4.8
    wave.inputs['Detail'].default_value=7.0
    L.new(mp.outputs['Vector'],wave.inputs['Vector'])
    noise=_n(N,'ShaderNodeTexNoise',(-700,-80))
    noise.inputs['Scale'].default_value=12.0; noise.inputs['Detail'].default_value=5.0
    L.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr=_n(N,'ShaderNodeValToRGB',(-420,200))
    cr.color_ramp.elements[0].color=(*dark,1.0)
    cr.color_ramp.elements[1].color=(*light,1.0)
    L.new(wave.outputs['Color'],cr.inputs['Fac'])
    cr_r=_n(N,'ShaderNodeValToRGB',(-420,-80))
    cr_r.color_ramp.elements[0].color=(roughness-0.08,)*3+(1.0,)
    cr_r.color_ramp.elements[1].color=(min(1,roughness+0.12),)*3+(1.0,)
    L.new(noise.outputs['Fac'],cr_r.inputs['Fac'])
    L.new(cr_r.outputs['Color'],bsdf.inputs['Roughness'])
    b=_bump(N,L,wave.outputs['Color'],0.50,0.010)
    L.new(b.outputs['Normal'],bsdf.inputs['Normal'])
    img=_img(N,f'[UNITY] {name}_Albedo',(-700,-340))
    mix=_n(N,'ShaderNodeMixRGB',(-150,200),'Mix_Albedo')
    mix.inputs['Fac'].default_value=0.0
    L.new(cr.outputs['Color'],mix.inputs['Color1'])
    L.new(img.outputs['Color'],mix.inputs['Color2'])
    L.new(mix.outputs['Color'],bsdf.inputs['Base Color'])
    return mat


def build_iron_mat(name, base=(0.13,0.12,0.10), metallic=0.85, roughness=0.55):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(400,0))
    bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value=metallic
    bsdf.inputs['Roughness'].default_value=roughness
    mp=_cmap(N,L,scale=(15,15,15),loc=(-800,0))
    noise=_n(N,'ShaderNodeTexNoise',(-600,80))
    noise.inputs['Scale'].default_value=20.0; noise.inputs['Detail'].default_value=5.0
    L.new(mp.outputs['Vector'],noise.inputs['Vector'])
    dark=tuple(max(0,c*0.40) for c in base)
    cr=_n(N,'ShaderNodeValToRGB',(-360,80))
    cr.color_ramp.elements[0].color=(*dark,1.0); cr.color_ramp.elements[1].color=(*base,1.0)
    L.new(noise.outputs['Fac'],cr.inputs['Fac'])
    b=_bump(N,L,noise.outputs['Fac'],0.28,0.005)
    L.new(b.outputs['Normal'],bsdf.inputs['Normal'])
    img=_img(N,f'[UNITY] {name}_Albedo',(-600,-300))
    mix=_n(N,'ShaderNodeMixRGB',(-130,80),'Mix_Albedo')
    mix.inputs['Fac'].default_value=0.0
    L.new(cr.outputs['Color'],mix.inputs['Color1'])
    L.new(img.outputs['Color'],mix.inputs['Color2'])
    L.new(mix.outputs['Color'],bsdf.inputs['Base Color'])
    return mat


def build_gold_mat(name, base=(0.78,0.60,0.08)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(300,0))
    bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value=(*base,1.0)
    bsdf.inputs['Metallic'].default_value=0.95
    bsdf.inputs['Roughness'].default_value=0.28
    return mat


def build_coin_mat(name):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(300,0))
    bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value=(1.0,0.78,0.18,1.0)
    bsdf.inputs['Metallic'].default_value=1.0
    bsdf.inputs['Roughness'].default_value=0.22
    return mat

# ──────────────────────────────────────────────
#  BARREL BUILDER
# ──────────────────────────────────────────────

def build_barrel_body(name, mat_wood, mat_iron, radius=0.25, height=0.70, aged=False):
    """Returns list of objects composing one barrel."""
    objs = []

    # Staved body (cylinder with bulge)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=height,
                                        location=(0, 0, height/2))
    body = bpy.context.active_object; body.name = f'{name}_Body'
    # Push mid verts outward for barrel bulge
    activate(body)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(body.data)
    for v in bm.verts:
        if abs(v.co.z - height/2) < height*0.35:
            t = 1.0 - abs(v.co.z - height/2) / (height*0.35)
            xy_len = math.sqrt(v.co.x**2 + v.co.y**2)
            if xy_len > 0.001:
                fac = 1.0 + 0.06*t*t
                v.co.x *= fac; v.co.y *= fac
    # Add plank groove lines (loop cuts at stave boundaries)
    bpy.ops.mesh.select_all(action='DESELECT')
    bmesh.update_edit_mesh(body.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    smooth_shade(body)
    sub = body.modifiers.new('Sub','SUBSURF'); sub.levels=2
    assign_mat(body, mat_wood); objs.append(body)

    # 2 iron bands at 1/4 and 3/4 height
    for band_z in (height*0.26, height*0.74):
        bpy.ops.mesh.primitive_torus_add(major_radius=radius+0.005, minor_radius=0.018,
                                         major_segments=24, minor_segments=8,
                                         location=(0,0,band_z))
        band=bpy.context.active_object; band.name=f'{name}_Band_{int(band_z*100)}'
        assign_mat(band, mat_iron); objs.append(band)

    # Lid (top cap, separate for animation)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius+0.008, depth=0.038,
                                        location=(0,0,height+0.019))
    lid=bpy.context.active_object; lid.name=f'{name}_Lid'
    bev=lid.modifiers.new('Bevel','BEVEL'); bev.width=0.006; bev.segments=2
    assign_mat(lid, mat_wood); objs.append(lid)

    # Bung hole (small cap on side, not a cutout for efficiency)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.022, depth=0.030,
                                        location=(radius+0.008, 0, height*0.55))
    bung=bpy.context.active_object; bung.name=f'{name}_Bung'
    bung.rotation_euler.y=math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(bung, mat_iron); objs.append(bung)

    return objs

# ──────────────────────────────────────────────
#  BARREL VARIANTS
# ──────────────────────────────────────────────

def make_barrel_upright_a(mats, col):
    objs = build_barrel_body('Prop_Barrel_Upright_A', mats['barrel_wood'], mats['barrel_iron'])
    root = make_root('Prop_Barrel_Upright_A_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col, root)

def make_barrel_upright_b(mats, col):
    # Weathered: darker material, slightly different size
    objs = build_barrel_body('Prop_Barrel_Upright_B', mats['barrel_wood_old'], mats['barrel_iron'],
                              radius=0.24, height=0.66)
    root = make_root('Prop_Barrel_Upright_B_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col, root)

def make_barrel_on_side(mats, col):
    objs = build_barrel_body('Prop_Barrel_OnSide_A', mats['barrel_wood_old'], mats['barrel_iron'])
    root = make_root('Prop_Barrel_OnSide_A_ROOT')
    for o in objs:
        # Rotate to lying on side
        o.rotation_euler.x = math.radians(90)
        o.location.z += 0.25
        bpy.ops.object.transform_apply(rotation=True, location=True)
        o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col, root)

def make_barrel_broken(mats, col):
    """Barrel with cracked/missing staves — unique damage look."""
    objs = build_barrel_body('Prop_Barrel_Broken_A', mats['barrel_wood_old'], mats['barrel_iron'])
    root = make_root('Prop_Barrel_Broken_A_ROOT')
    # Tilt to suggest knocked over / damaged
    for o in objs:
        o.rotation_euler.z = math.radians(22)
        o.rotation_euler.x = math.radians(8)
        o.parent=root; uv_unwrap(o); link_obj(col,o)

    # Broken stave fragment lying nearby
    bpy.ops.mesh.primitive_cube_add(location=(0.35, 0.15, 0.02))
    stave=bpy.context.active_object; stave.name='Prop_Barrel_Broken_A_Stave'
    stave.scale=(0.025, 0.10, 0.008); bpy.ops.object.transform_apply(scale=True)
    stave.rotation_euler=(math.radians(5), math.radians(-12), math.radians(30))
    assign_mat(stave, mats['barrel_wood_old']); uv_unwrap(stave)
    stave.parent=root; link_obj(col,stave)
    link_obj(col, root)

# ──────────────────────────────────────────────
#  CRATE BUILDER
# ──────────────────────────────────────────────

def build_crate_base(name, mat_wood, mat_iron, w=0.60, d=0.50, h=0.50):
    objs = []

    # Body
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, h/2))
    body=bpy.context.active_object; body.name=f'{name}_Body'
    body.scale=(w/2, d/2, h/2); bpy.ops.object.transform_apply(scale=True)

    # Plank groove details via loop cuts
    activate(body)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bm=bmesh.from_edit_mesh(body.data)
    for v in bm.verts:
        if abs(v.co.z - h/4) < 0.006 or abs(v.co.z - h*0.75) < 0.006:
            v.co.z += 0.004 if v.co.z > h/2 else -0.004
    bmesh.update_edit_mesh(body.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    bev=body.modifiers.new('Bevel','BEVEL'); bev.width=0.008; bev.segments=2
    assign_mat(body, mat_wood); objs.append(body)

    # Corner iron brackets (8 corners)
    for xi, xv in ((-1,-w/2+0.012),(1,w/2-0.012)):
        for yi, yv in ((-1,-d/2+0.012),(1,d/2-0.012)):
            bpy.ops.mesh.primitive_cube_add(location=(xv,yv,h/2))
            brk=bpy.context.active_object; brk.name=f'{name}_Bracket_{xi}_{yi}'
            brk.scale=(0.028, 0.028, h/2-0.010); bpy.ops.object.transform_apply(scale=True)
            assign_mat(brk, mat_iron); objs.append(brk)

    # Rope handles on 2 sides (torus)
    for side, y in (('Front',-d/2-0.004),('Back',d/2+0.004)):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.055, minor_radius=0.010,
                                         major_segments=14, minor_segments=6,
                                         location=(0, y, h*0.62))
        handle=bpy.context.active_object; handle.name=f'{name}_Handle_{side}'
        handle.rotation_euler.x=math.radians(90); bpy.ops.object.transform_apply(rotation=True)
        handle.scale=(1.0,0.5,1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(handle, mat_iron); objs.append(handle)

    return objs, body


def make_crate_sealed(mats, col):
    objs, body = build_crate_base('Prop_Crate_Sealed_A', mats['crate_wood'], mats['crate_iron'])
    # Lid (top planks)
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0.515))
    lid=bpy.context.active_object; lid.name='Prop_Crate_Sealed_A_Lid'
    lid.scale=(0.305, 0.255, 0.022); bpy.ops.object.transform_apply(scale=True)
    assign_mat(lid, mats['crate_wood']); objs.append(lid)
    root=make_root('Prop_Crate_Sealed_A_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col, root)


def make_crate_open(mats, col):
    objs, body = build_crate_base('Prop_Crate_Open_A', mats['crate_wood'], mats['crate_iron'])
    # Lid displaced to the side, tilted
    bpy.ops.mesh.primitive_cube_add(location=(0.45, 0.10, 0.022))
    lid=bpy.context.active_object; lid.name='Prop_Crate_Open_A_Lid'
    lid.scale=(0.305, 0.255, 0.022); lid.rotation_euler.z=math.radians(18)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    assign_mat(lid, mats['crate_wood']); objs.append(lid)
    # Dark interior visible
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0,0,0.020))
    interior=bpy.context.active_object; interior.name='Prop_Crate_Open_A_Interior'
    interior.scale=(0.28, 0.23, 1.0); bpy.ops.object.transform_apply(scale=True)
    interior_mat=bpy.data.materials.new('Mat_Crate_Interior')
    interior_mat.use_nodes=True
    interior_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.08,0.05,0.02,1.0)
    interior_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.95
    assign_mat(interior, interior_mat); objs.append(interior)
    root=make_root('Prop_Crate_Open_A_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col, root)


def make_crate_stack(mats, col):
    """2 crates stacked — different sizes for visual interest."""
    all_objs=[]
    # Bottom crate (standard)
    objs_bot, _ = build_crate_base('Prop_Crate_Stack_Bot', mats['crate_wood'], mats['crate_iron'],
                                    w=0.62, d=0.52, h=0.52)
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0.534))
    lid_b=bpy.context.active_object; lid_b.name='Prop_Crate_Stack_Bot_Lid'
    lid_b.scale=(0.315, 0.265, 0.022); bpy.ops.object.transform_apply(scale=True)
    assign_mat(lid_b, mats['crate_wood']); objs_bot.append(lid_b)
    all_objs.extend(objs_bot)
    # Top crate (smaller, offset)
    for o in objs_bot: o.location.z -= 0  # keep at Z=0
    objs_top, _ = build_crate_base('Prop_Crate_Stack_Top', mats['crate_wood'], mats['crate_iron'],
                                    w=0.46, d=0.38, h=0.40)
    bpy.ops.mesh.primitive_cube_add(location=(0.05, -0.04, 0.554+0.42/2))
    lid_t=bpy.context.active_object; lid_t.name='Prop_Crate_Stack_Top_Lid'
    lid_t.scale=(0.235, 0.195, 0.020); bpy.ops.object.transform_apply(scale=True)
    assign_mat(lid_t, mats['crate_wood']); objs_top.append(lid_t)
    # Offset top crate to sit on bottom crate
    for o in objs_top:
        o.location.z += 0.556
        o.location.x += 0.05; o.location.y -= 0.04
        o.rotation_euler.z = math.radians(8)
    all_objs.extend(objs_top)
    root=make_root('Prop_Crate_Stack_A_ROOT')
    for o in all_objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col, root)

# ──────────────────────────────────────────────
#  CHEST BUILDER
# ──────────────────────────────────────────────

def build_chest_body(name, mats, lid_angle=0):
    """lid_angle=0 closed, >0 open."""
    objs = []

    # Body box
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0.20))
    body=bpy.context.active_object; body.name=f'{name}_Body'
    body.scale=(0.350, 0.225, 0.200); bpy.ops.object.transform_apply(scale=True)
    bev=body.modifiers.new('Bevel','BEVEL'); bev.width=0.008; bev.segments=2
    assign_mat(body, mats['chest_wood']); objs.append(body)

    # Iron banding: top edge + middle + corners
    for band_z, bw in ((0.395,0.022),(0.200,0.018)):
        bpy.ops.mesh.primitive_cube_add(location=(0,0,band_z))
        band=bpy.context.active_object; band.name=f'{name}_Band_{int(band_z*100)}'
        band.scale=(0.355, 0.230, bw/2); bpy.ops.object.transform_apply(scale=True)
        assign_mat(band, mats['chest_iron']); objs.append(band)

    # Gold trim on band edges
    bpy.ops.mesh.primitive_torus_add(major_radius=0.000, minor_radius=0.006,
                                     major_segments=4, minor_segments=4,
                                     location=(0,0,0.398))
    # Simple gold strip approximation
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0.402))
    gold=bpy.context.active_object; gold.name=f'{name}_GoldTrim'
    gold.scale=(0.354,0.229,0.006); bpy.ops.object.transform_apply(scale=True)
    assign_mat(gold, mats['chest_gold']); objs.append(gold)

    # Hinges (back)
    for hx in (-0.22, 0.22):
        bpy.ops.mesh.primitive_cube_add(location=(hx, 0.228, 0.395))
        hinge=bpy.context.active_object; hinge.name=f'{name}_Hinge_{int(hx*100)}'
        hinge.scale=(0.040,0.015,0.050); bpy.ops.object.transform_apply(scale=True)
        assign_mat(hinge, mats['chest_iron']); objs.append(hinge)

    # Lock
    bpy.ops.mesh.primitive_cube_add(location=(0,-0.232,0.260))
    lock=bpy.context.active_object; lock.name=f'{name}_Lock'
    lock.scale=(0.042,0.014,0.048); bpy.ops.object.transform_apply(scale=True)
    assign_mat(lock, mats['chest_iron']); objs.append(lock)

    # Lock shackle (U shape torus half)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.028, minor_radius=0.008,
                                     major_segments=10, minor_segments=6,
                                     location=(0,-0.238,0.300))
    shackle=bpy.context.active_object; shackle.name=f'{name}_Shackle'
    shackle.scale=(1.0,0.4,1.0); bpy.ops.object.transform_apply(scale=True)
    assign_mat(shackle, mats['chest_iron']); objs.append(shackle)

    # Lid (separate — hinged at back)
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0.490))
    lid=bpy.context.active_object; lid.name=f'{name}_Lid'
    lid.scale=(0.350, 0.224, 0.095); bpy.ops.object.transform_apply(scale=True)
    # Dome the lid slightly
    activate(lid)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=3)
    bm=bmesh.from_edit_mesh(lid.data)
    for v in bm.verts:
        if v.co.z > 0.568:
            fac = (v.co.z - 0.490) / 0.095
            v.co.z += 0.022 * math.sin(fac * math.pi)
    bmesh.update_edit_mesh(lid.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    if lid_angle > 0:
        # Rotate lid open around hinge at back edge Z=0.395, Y=0.228
        lid.location.y  = 0.228
        lid.location.z  = 0.395
        bpy.ops.object.transform_apply(location=True)
        lid.rotation_euler.x = -math.radians(lid_angle)
        bpy.ops.object.transform_apply(rotation=True)
        lid.location.y = -0.228
        lid.location.z = -0.395
        bpy.ops.object.transform_apply(location=True)

    assign_mat(lid, mats['chest_wood']); objs.append(lid)

    # Interior floor (visible when open)
    if lid_angle > 60:
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0,0,0.012))
        interior=bpy.context.active_object; interior.name=f'{name}_Interior'
        interior.scale=(0.335, 0.210, 1.0); bpy.ops.object.transform_apply(scale=True)
        assign_mat(interior, mats['chest_interior']); objs.append(interior)

    return objs


def make_chest_closed(mats, col):
    objs=build_chest_body('Prop_Chest_Closed_A', mats, lid_angle=0)
    root=make_root('Prop_Chest_Closed_A_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col,root)


def make_chest_open(mats, col):
    objs=build_chest_body('Prop_Chest_Open_A', mats, lid_angle=105)
    root=make_root('Prop_Chest_Open_A_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col,root)


def make_chest_loot(mats, col):
    objs=build_chest_body('Prop_Chest_Loot_A', mats, lid_angle=100)
    # Add coins inside
    coin_positions=[(0,0,0.055),(-0.09,0.05,0.055),(0.10,-0.06,0.060),(-0.04,-0.10,0.060),(0.08,0.09,0.065)]
    for ci,pos in enumerate(coin_positions):
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.038, depth=0.010, location=pos)
        coin=bpy.context.active_object; coin.name=f'Prop_Chest_Loot_A_Coin_{ci}'
        coin.rotation_euler=(math.radians(ci*20), math.radians(ci*15), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(coin, mats['gold']); objs.append(coin)
    # Gem
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.030, location=(0.04,0.06,0.090))
    gem=bpy.context.active_object; gem.name='Prop_Chest_Loot_A_Gem'
    gem.scale=(1.0,1.0,0.65); bpy.ops.object.transform_apply(scale=True)
    gem_mat=bpy.data.materials.new('Mat_Gem_Purple')
    gem_mat.use_nodes=True
    gem_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.45,0.05,0.80,1.0)
    gem_mat.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=0.0
    gem_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.05
    assign_mat(gem, gem_mat); objs.append(gem)
    root=make_root('Prop_Chest_Loot_A_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col,root)

# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    setup_scene()

    mats = {
        'barrel_wood'     : build_wood_mat('Mat_Barrel_Wood',     dark=(0.34,0.18,0.05), light=(0.55,0.34,0.13), roughness=0.90, scale=10.0),
        'barrel_wood_old' : build_wood_mat('Mat_Barrel_Wood_Old', dark=(0.20,0.10,0.03), light=(0.38,0.22,0.08), roughness=0.95, scale=10.0),
        'barrel_iron'     : build_iron_mat('Mat_Barrel_Iron',     base=(0.10,0.10,0.10), metallic=0.85, roughness=0.55),
        'crate_wood'      : build_wood_mat('Mat_Crate_Wood',      dark=(0.38,0.22,0.07), light=(0.62,0.40,0.16), roughness=0.92, scale=9.0),
        'crate_iron'      : build_iron_mat('Mat_Crate_Iron',      base=(0.13,0.13,0.12), metallic=0.90, roughness=0.50),
        'chest_wood'      : build_wood_mat('Mat_Chest_Wood_Dark', dark=(0.22,0.12,0.04), light=(0.36,0.20,0.08), roughness=0.88, scale=12.0),
        'chest_iron'      : build_iron_mat('Mat_Chest_Iron',      base=(0.08,0.08,0.08), metallic=0.85, roughness=0.60),
        'chest_gold'      : build_gold_mat('Mat_Chest_Gold_Trim', base=(0.78,0.60,0.08)),
        'chest_interior'  : build_wood_mat('Mat_Chest_Interior',  dark=(0.14,0.08,0.02), light=(0.22,0.12,0.04), roughness=0.95, scale=15.0),
        'gold'            : build_coin_mat('Mat_Coin_Gold'),
    }

    col = new_col('IsleTrial_Props_Containers')

    # ── BARRELS (4 variants)
    make_barrel_upright_a(mats, col)
    make_barrel_upright_b(mats, col)
    make_barrel_on_side(mats, col)
    make_barrel_broken(mats, col)

    # ── CRATES (3 variants)
    make_crate_sealed(mats, col)
    make_crate_open(mats, col)
    make_crate_stack(mats, col)

    # ── CHESTS (3 variants)
    make_chest_closed(mats, col)
    make_chest_open(mats, col)
    make_chest_loot(mats, col)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D': sp.shading.type = 'MATERIAL'
            break

    print("\n" + "="*65)
    print("  IsleTrial — Container Props Complete")
    print("="*65)
    print("  BARRELS  : Upright_A · Upright_B · OnSide_A · Broken_A")
    print("  CRATES   : Sealed_A  · Open_A    · Stack_A")
    print("  CHESTS   : Closed_A  · Open_A    · Loot_A")
    print("  Total prefabs : 10  (each → separate Unity prefab)")
    print("  Collection    : IsleTrial_Props_Containers")
    print("="*65 + "\n")

main()
