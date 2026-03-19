"""
IsleTrial — Props: Rope, Chain & Net  (03-C)
Blender 4.x  •  Python Script

Variety objects (each → Unity prefab):
──────────────────────────────────────────────────────
  Prop_RopeCoil_A       – small tight coil (0.4m diameter)
  Prop_RopeCoil_B       – large loose coil (0.6m diameter)
  Prop_RopeBundle_A     – roll of rope tied in middle
  Prop_Chain_Segment    – 10-link iron chain (modular)
  Prop_Chain_Pile_A     – heap of chain links on ground
  Prop_AnchorChain      – 20-link catenary hang
  Prop_Net_Fishing      – 2×1.5m flat fishing net

Materials (dual-path)
  Mat_Rope_Hemp   – tan woven rope
  Mat_Chain_Iron  – dark iron chain links
  Mat_Net_Rope    – thin rope with alpha cutout
  Mat_Cork_Float  – cork orange-brown floats
  Mat_Lead_Weight – dark lead sinkers
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
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def link_obj(col, obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)

def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def assign_mat(obj, mat):
    if obj.data.materials: obj.data.materials[0] = mat
    else: obj.data.materials.append(mat)

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
    r=bpy.context.active_object; r.name=name; return r

# ──────────────────────────────────────────────
#  MATERIAL HELPERS
# ──────────────────────────────────────────────

def _n(nodes, ntype, loc, label=None):
    n=nodes.new(ntype); n.location=loc
    if label: n.label=label; n.name=label
    return n

def _img(nodes, slot, loc):
    n=nodes.new('ShaderNodeTexImage'); n.location=loc; n.label=slot; n.name=slot; return n

def _cmap(nodes, links, scale=(10,10,10), loc=(-900,0)):
    tc=_n(nodes,'ShaderNodeTexCoord',(loc[0],loc[1]))
    mp=_n(nodes,'ShaderNodeMapping',(loc[0]+200,loc[1]))
    mp.inputs['Scale'].default_value=scale
    links.new(tc.outputs['UV'],mp.inputs['Vector']); return mp

# ──────────────────────────────────────────────
#  MATERIALS
# ──────────────────────────────────────────────

def build_rope_mat(name, base=(0.77,0.64,0.35)):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(400,0))
    bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value=1.0; bsdf.inputs['Metallic'].default_value=0.0
    mp=_cmap(N,L,scale=(22,22,22),loc=(-900,0))
    wave=_n(N,'ShaderNodeTexWave',(-680,80))
    wave.wave_type='BANDS'; wave.bands_direction='Z'
    wave.inputs['Scale'].default_value=30.0; wave.inputs['Distortion'].default_value=2.5
    L.new(mp.outputs['Vector'],wave.inputs['Vector'])
    noise=_n(N,'ShaderNodeTexNoise',(-680,-100))
    noise.inputs['Scale'].default_value=8.0; noise.inputs['Detail'].default_value=4.0
    L.new(mp.outputs['Vector'],noise.inputs['Vector'])
    dark=tuple(max(0,c*0.52) for c in base)
    cr=_n(N,'ShaderNodeValToRGB',(-420,80))
    cr.color_ramp.elements[0].color=(*dark,1.0); cr.color_ramp.elements[1].color=(*base,1.0)
    L.new(wave.outputs['Color'],cr.inputs['Fac'])
    # Mix noise wear
    mix_n=_n(N,'ShaderNodeMixRGB',(-200,0)); mix_n.blend_type='MULTIPLY'; mix_n.inputs['Fac'].default_value=0.22
    cr_n=_n(N,'ShaderNodeValToRGB',(-420,-100))
    cr_n.color_ramp.elements[0].color=(0.72,0.72,0.72,1.0); cr_n.color_ramp.elements[1].color=(1.0,1.0,1.0,1.0)
    L.new(noise.outputs['Fac'],cr_n.inputs['Fac'])
    L.new(cr.outputs['Color'],mix_n.inputs['Color1']); L.new(cr_n.outputs['Color'],mix_n.inputs['Color2'])
    img=_img(N,f'[UNITY] {name}_Albedo',(-680,-320))
    mix_u=_n(N,'ShaderNodeMixRGB',(-50,0),'Mix_Unity'); mix_u.inputs['Fac'].default_value=0.0
    L.new(mix_n.outputs['Color'],mix_u.inputs['Color1']); L.new(img.outputs['Color'],mix_u.inputs['Color2'])
    L.new(mix_u.outputs['Color'],bsdf.inputs['Base Color'])
    return mat


def build_iron_mat(name, base=(0.10,0.10,0.10)):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(300,0)); bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value=(*base,1.0); bsdf.inputs['Metallic'].default_value=0.90
    bsdf.inputs['Roughness'].default_value=0.45
    return mat


def build_net_mat(name):
    """Semi-transparent net rope material with alpha clip."""
    mat=bpy.data.materials.new(name); mat.use_nodes=True; mat.blend_method='CLIP'; mat.shadow_method='CLIP'
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(400,0)); bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value=(0.77,0.64,0.35,1.0); bsdf.inputs['Roughness'].default_value=1.0
    # Alpha from image texture slot (will be net pattern texture in Unity)
    img_alpha=_img(N,f'[UNITY] {name}_Alpha',(-400,-200))
    L.new(img_alpha.outputs['Alpha'],bsdf.inputs['Alpha'])
    # Procedural fallback: set alpha 1.0 (fully visible until Unity texture loaded)
    bsdf.inputs['Alpha'].default_value=1.0
    return mat


def build_cork_mat(name, base=(0.62,0.38,0.18)):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    N=mat.node_tree.nodes; L=mat.node_tree.links; N.clear()
    out=_n(N,'ShaderNodeOutputMaterial',(300,0)); bsdf=_n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value=(*base,1.0); bsdf.inputs['Roughness'].default_value=0.88
    return mat

# ──────────────────────────────────────────────
#  TUBE HELPER (used for all rope/tube shapes)
# ──────────────────────────────────────────────

def tube_from_points(name, points, radius=0.008, segs=6):
    """Extrude a tube mesh along a list of 3D points."""
    bm = bmesh.new()
    all_rings = []
    for pt in points:
        ring = []
        for vi in range(segs):
            ang = 2*math.pi*vi/segs
            ring.append(bm.verts.new((pt[0]+math.cos(ang)*radius,
                                      pt[1]+math.sin(ang)*radius,
                                      pt[2])))
        all_rings.append(ring)
    for ri in range(len(all_rings)-1):
        for vi in range(segs):
            a=all_rings[ri][vi]; b=all_rings[ri][(vi+1)%segs]
            c=all_rings[ri+1][(vi+1)%segs]; d=all_rings[ri+1][vi]
            try: bm.faces.new([a,b,c,d])
            except: pass
    # Caps
    try: bm.faces.new(all_rings[0][::-1])
    except: pass
    try: bm.faces.new(all_rings[-1])
    except: pass
    mesh=bpy.data.meshes.new(name); bm.to_mesh(mesh); bm.free()
    obj=bpy.data.objects.new(name,mesh); bpy.context.scene.collection.objects.link(obj)
    smooth_shade(obj); return obj

# ──────────────────────────────────────────────
#  ROPE COIL VARIANTS
# ──────────────────────────────────────────────

def make_rope_coil(name, col, mat_rope, outer_r=0.40, inner_r=0.10, height=0.15, loops=6):
    """Spiral coil of rope on the ground."""
    pts = []
    total_steps = loops * 60
    for i in range(total_steps + 1):
        t = i / total_steps
        angle = t * math.pi * 2 * loops
        r = inner_r + (outer_r - inner_r) * (t % (1/loops) * loops)
        pts.append((math.cos(angle)*r, math.sin(angle)*r, t * height))
    coil = tube_from_points(f'{name}_Coil', pts, radius=0.014, segs=8)
    assign_mat(coil, mat_rope)
    root = make_root(f'{name}_ROOT')
    coil.parent = root; uv_unwrap(coil); link_obj(col, coil); link_obj(col, root)


def make_rope_coil_a(col, mat_rope):
    make_rope_coil('Prop_RopeCoil_A', col, mat_rope, outer_r=0.38, inner_r=0.10, height=0.14, loops=6)

def make_rope_coil_b(col, mat_rope):
    """Larger, looser coil."""
    make_rope_coil('Prop_RopeCoil_B', col, mat_rope, outer_r=0.58, inner_r=0.15, height=0.18, loops=5)

# ──────────────────────────────────────────────
#  ROPE BUNDLE
# ──────────────────────────────────────────────

def make_rope_bundle(col, mat_rope):
    objs = []
    # 3 parallel rope strands bundled together
    for strand_i in range(3):
        offset_x = (strand_i - 1) * 0.020
        pts = [(offset_x + math.sin(i/8)*0.006, i*0.005, (strand_i%2)*0.010)
               for i in range(70)]
        strand = tube_from_points(f'Prop_RopeBundle_A_Strand_{strand_i}', pts, radius=0.012, segs=6)
        strand.rotation_euler.x = math.radians(90)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(strand, mat_rope); objs.append(strand)

    # Tie band in the middle
    bpy.ops.mesh.primitive_torus_add(major_radius=0.038, minor_radius=0.008,
                                     major_segments=10, minor_segments=6, location=(0,0,0.165))
    tie=bpy.context.active_object; tie.name='Prop_RopeBundle_A_Tie'
    tie.scale=(1.0,0.4,1.0); bpy.ops.object.transform_apply(scale=True)
    assign_mat(tie, mat_rope); objs.append(tie)

    root=make_root('Prop_RopeBundle_A_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col,root)

# ──────────────────────────────────────────────
#  CHAIN LINK BUILDER
# ──────────────────────────────────────────────

def build_chain_link(name, center, rotation_z=0, major_r=0.040, minor_r=0.012):
    """Single oval chain link."""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_r, minor_radius=minor_r,
        major_segments=12, minor_segments=8,
        location=center)
    link=bpy.context.active_object; link.name=name
    link.scale=(1.0, 1.65, 1.0)  # stretch into oval
    link.rotation_euler.z=math.radians(rotation_z)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    return link

# ──────────────────────────────────────────────
#  CHAIN SEGMENT (10 links)
# ──────────────────────────────────────────────

def make_chain_segment(col, mat_iron):
    objs = []
    link_spacing = 0.095  # centre-to-centre
    for li in range(10):
        rot_z = 90 if li % 2 == 0 else 0
        link = build_chain_link(f'Prop_Chain_Segment_Link_{li}',
                                center=(0, li * link_spacing, 0),
                                rotation_z=rot_z)
        assign_mat(link, mat_iron); objs.append(link)
    root=make_root('Prop_Chain_Segment_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col,root)

# ──────────────────────────────────────────────
#  CHAIN PILE
# ──────────────────────────────────────────────

def make_chain_pile(col, mat_iron):
    """~12 links dumped in a heap — unique ground prop."""
    objs = []
    import random; random.seed(77)
    pile_pts = [
        (0, 0, 0), (0.08, 0.05, 0.04), (-0.06, 0.09, 0.04),
        (0.05, -0.08, 0.04), (-0.09, -0.04, 0.04), (0, 0.12, 0.08),
        (0.10, 0.10, 0.08), (-0.04, 0.02, 0.08), (0.02, -0.12, 0.08),
        (-0.10, 0.08, 0.12), (0.06, 0.06, 0.12), (-0.02, -0.06, 0.12),
    ]
    for li, pos in enumerate(pile_pts):
        rot_z = random.uniform(0, 360)
        rot_x = random.uniform(-30, 30)
        link = build_chain_link(f'Prop_Chain_Pile_A_Link_{li}', pos, rotation_z=rot_z)
        link.rotation_euler.x = math.radians(rot_x)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(link, mat_iron); objs.append(link)
    root=make_root('Prop_Chain_Pile_A_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col,root)

# ──────────────────────────────────────────────
#  ANCHOR CHAIN (20 links, catenary)
# ──────────────────────────────────────────────

def make_anchor_chain(col, mat_iron):
    objs = []
    n_links = 20
    total_length = 2.0
    # Catenary: sag parameter a, horizontal distance span
    span = 1.6; sag = 0.55

    for li in range(n_links):
        t = li / (n_links - 1)
        x = -span/2 + t * span
        # Catenary: y = a * cosh(x/a) - a  (a controls sag)
        a = (span**2) / (8 * sag)
        z = a * (math.cosh(x / a) - 1)
        z = sag - z  # flip so it sags downward
        rot_z = 90 if li % 2 == 0 else 0
        link = build_chain_link(f'Prop_AnchorChain_Link_{li}',
                                center=(0, x, z),
                                rotation_z=rot_z, major_r=0.044, minor_r=0.014)
        assign_mat(link, mat_iron); objs.append(link)
    root=make_root('Prop_AnchorChain_ROOT')
    for o in objs: o.parent=root; uv_unwrap(o); link_obj(col,o)
    link_obj(col,root)

# ──────────────────────────────────────────────
#  FISHING NET
# ──────────────────────────────────────────────

def make_fishing_net(col, mat_net, mat_cork, mat_lead):
    objs = []
    net_w = 2.0; net_h = 1.5
    grid_x = 10; grid_y = 8  # grid divisions
    cell_w = net_w / grid_x; cell_h = net_h / grid_y

    # Horizontal strands
    for yi in range(grid_y + 1):
        y = yi * cell_h - net_h/2
        pts = [(xi * cell_w - net_w/2, y, 0) for xi in range(grid_x + 1)]
        strand = tube_from_points(f'Net_H_{yi}', pts, radius=0.004, segs=5)
        assign_mat(strand, mat_net); objs.append(strand)

    # Vertical strands
    for xi in range(grid_x + 1):
        x = xi * cell_w - net_w/2
        pts = [(x, yi * cell_h - net_h/2, 0) for yi in range(grid_y + 1)]
        strand = tube_from_points(f'Net_V_{xi}', pts, radius=0.004, segs=5)
        assign_mat(strand, mat_net); objs.append(strand)

    # Cork floats on top edge (8)
    float_spacing = net_w / 7
    for fi in range(8):
        x = fi * float_spacing - net_w/2
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.055,
                                            location=(x, net_h/2, 0.028))
        flt=bpy.context.active_object; flt.name=f'Net_Float_{fi}'
        flt.rotation_euler.z = math.radians(90)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(flt, mat_cork); objs.append(flt)

    # Lead weights on bottom edge (8)
    weight_spacing = net_w / 7
    for wi in range(8):
        x = wi * weight_spacing - net_w/2
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6,
                                             radius=0.018, location=(x, -net_h/2, -0.018))
        wt=bpy.context.active_object; wt.name=f'Net_Weight_{wi}'
        wt.scale=(1.0,1.0,0.65); bpy.ops.object.transform_apply(scale=True)
        lead_mat=bpy.data.materials.new(f'Mat_Lead_Weight')
        lead_mat.use_nodes=True
        lead_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.12,0.12,0.14,1.0)
        lead_mat.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=0.80
        lead_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.65
        assign_mat(wt, lead_mat); objs.append(wt)

    root=make_root('Prop_Net_Fishing_ROOT')
    for o in objs:
        o.parent=root
        if o.type=='MESH': uv_unwrap(o)
        link_obj(col,o)
    link_obj(col,root)

# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    setup_scene()

    mat_rope  = build_rope_mat('Mat_Rope_Hemp',   base=(0.77,0.64,0.35))
    mat_iron  = build_iron_mat('Mat_Chain_Iron',  base=(0.10,0.10,0.10))
    mat_net   = build_net_mat('Mat_Net_Rope')
    mat_cork  = build_cork_mat('Mat_Cork_Float',  base=(0.62,0.38,0.18))
    mat_lead  = build_cork_mat('Mat_Lead_Weight', base=(0.12,0.12,0.14))

    col = new_col('IsleTrial_Props_RopeChain')

    make_rope_coil_a(col, mat_rope)
    make_rope_coil_b(col, mat_rope)
    make_rope_bundle(col, mat_rope)
    make_chain_segment(col, mat_iron)
    make_chain_pile(col, mat_iron)
    make_anchor_chain(col, mat_iron)
    make_fishing_net(col, mat_net, mat_cork, mat_lead)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D': sp.shading.type='MATERIAL'
            break

    print("\n" + "="*62)
    print("  IsleTrial — Rope & Chain Props Complete")
    print("="*62)
    print("  Prop_RopeCoil_A     – small tight coil")
    print("  Prop_RopeCoil_B     – large loose coil")
    print("  Prop_RopeBundle_A   – tied rope roll")
    print("  Prop_Chain_Segment  – 10-link segment (modular)")
    print("  Prop_Chain_Pile_A   – scattered chain heap")
    print("  Prop_AnchorChain    – 20-link catenary")
    print("  Prop_Net_Fishing    – 2 × 1.5 m fishing net")
    print("  Total prefabs : 7")
    print("  Collection    : IsleTrial_Props_RopeChain")
    print("="*62 + "\n")

main()
