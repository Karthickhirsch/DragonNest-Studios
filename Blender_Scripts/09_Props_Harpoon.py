"""
IsleTrial — Props: Harpoon  (03-A)
Blender 4.x  •  Python Script

Variety objects created (each becomes a Unity prefab):
────────────────────────────────────────────────────
  Harpoon_Projectile   – single fired harpoon  (1.2 m)
  Harpoon_Rack_A       – wall rack with 3 stacked harpoons
  Harpoon_Stuck_A      – harpoon embedded in wood (tilted 12°)

Materials (dual-path)
  Mat_Harpoon_Iron     – polished dark iron tip/head
  Mat_Harpoon_Iron_Old – worn shaft iron
  Mat_Harpoon_Rope     – hemp rope coil
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

def uv_unwrap(obj, angle=55.0):
    activate(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=angle, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

# ──────────────────────────────────────────────
#  MATERIAL NODE HELPERS
# ──────────────────────────────────────────────

def _n(nodes, ntype, loc, label=None):
    n = nodes.new(ntype); n.location = loc
    if label: n.label = label; n.name = label
    return n

def _img(nodes, slot, loc):
    n = nodes.new('ShaderNodeTexImage'); n.location = loc
    n.label = slot; n.name = slot; return n

def _cmap(nodes, links, scale=(10,10,10), loc=(-900,0)):
    tc = _n(nodes,'ShaderNodeTexCoord',(loc[0],loc[1]))
    mp = _n(nodes,'ShaderNodeMapping',(loc[0]+200,loc[1]))
    mp.inputs['Scale'].default_value = scale
    links.new(tc.outputs['UV'], mp.inputs['Vector'])
    return mp

def _bump(nodes, links, h_sock, s=0.4, d=0.006):
    b = _n(nodes,'ShaderNodeBump',(-100,-200))
    b.inputs['Strength'].default_value=s; b.inputs['Distance'].default_value=d
    links.new(h_sock, b.inputs['Height']); return b

# ──────────────────────────────────────────────
#  MATERIALS
# ──────────────────────────────────────────────

def build_iron_mat(name, base=(0.11,0.11,0.11), metallic=1.0, roughness=0.25):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes; L = mat.node_tree.links; N.clear()
    out  = _n(N,'ShaderNodeOutputMaterial',(400,0))
    bsdf = _n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value  = metallic
    bsdf.inputs['Roughness'].default_value = roughness

    mp = _cmap(N, L, scale=(14,14,14), loc=(-900,0))
    noise = _n(N,'ShaderNodeTexNoise',(-680,80))
    noise.inputs['Scale'].default_value = 22.0
    noise.inputs['Detail'].default_value = 6.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    dark = tuple(max(0,c*0.40) for c in base)
    cr = _n(N,'ShaderNodeValToRGB',(-420,80))
    cr.color_ramp.elements[0].color = (*dark,1.0)
    cr.color_ramp.elements[1].color = (*base,1.0)
    L.new(noise.outputs['Fac'], cr.inputs['Fac'])

    b = _bump(N,L,noise.outputs['Fac'],0.28,0.005)
    L.new(b.outputs['Normal'], bsdf.inputs['Normal'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-680,-300))
    mix = _n(N,'ShaderNodeMixRGB',(-160,80),'Mix_Albedo')
    mix.inputs['Fac'].default_value = 0.0
    L.new(cr.outputs['Color'], mix.inputs['Color1'])
    L.new(img.outputs['Color'], mix.inputs['Color2'])
    L.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_rope_mat(name, base=(0.77,0.64,0.35)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes; L = mat.node_tree.links; N.clear()
    out  = _n(N,'ShaderNodeOutputMaterial',(300,0))
    bsdf = _n(N,'ShaderNodeBsdfPrincipled',(0,0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Metallic'].default_value  = 0.0

    mp = _cmap(N, L, scale=(22,22,22), loc=(-800,0))
    wave = _n(N,'ShaderNodeTexWave',(-600,80))
    wave.wave_type='BANDS'; wave.bands_direction='Z'
    wave.inputs['Scale'].default_value = 28.0
    wave.inputs['Distortion'].default_value = 2.2
    L.new(mp.outputs['Vector'], wave.inputs['Vector'])

    dark = tuple(max(0,c*0.55) for c in base)
    cr = _n(N,'ShaderNodeValToRGB',(-360,80))
    cr.color_ramp.elements[0].color = (*dark,1.0)
    cr.color_ramp.elements[1].color = (*base,1.0)
    L.new(wave.outputs['Color'], cr.inputs['Fac'])
    L.new(cr.outputs['Color'], bsdf.inputs['Base Color'])
    return mat

# ──────────────────────────────────────────────
#  BUILD HARPOON (single)
# ──────────────────────────────────────────────

def build_harpoon(mats, offset=(0,0,0), name_prefix=''):
    """Builds one complete harpoon. Returns list of mesh objects."""
    objs = []
    ox, oy, oz = offset

    # ── Shaft (tapered cylinder: thin ends, wider middle)
    bm = bmesh.new()
    segs = 10; length = 1.0
    rings = 12
    for ri in range(rings + 1):
        t = ri / rings
        # radius profile: thinner at ends, wider at ~40%
        r = 0.032 + 0.013 * math.sin(t * math.pi) * (1 + 0.5 * math.sin(t * 2.8))
        for vi in range(segs):
            ang = 2 * math.pi * vi / segs
            bm.verts.new((ox + math.cos(ang)*r, oy + t*length, oz + math.sin(ang)*r))
    bm.verts.ensure_lookup_table()
    for ri in range(rings):
        for vi in range(segs):
            a = ri*segs + vi; b = ri*segs + (vi+1)%segs
            c = (ri+1)*segs + (vi+1)%segs; d = (ri+1)*segs + vi
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    # Cap ends
    bot_verts = [bm.verts[vi] for vi in range(segs)]
    top_verts = [bm.verts[rings*segs + vi] for vi in range(segs)]
    try: bm.faces.new(bot_verts[::-1])
    except: pass
    try: bm.faces.new(top_verts)
    except: pass

    mesh = bpy.data.meshes.new(f'{name_prefix}Harpoon_Shaft')
    bm.to_mesh(mesh); bm.free()
    shaft = bpy.data.objects.new(f'{name_prefix}Harpoon_Shaft', mesh)
    bpy.context.scene.collection.objects.link(shaft)
    for p in shaft.data.polygons: p.use_smooth = True
    sub = shaft.modifiers.new('Sub','SUBSURF'); sub.levels = 1
    assign_mat(shaft, mats['iron_old']); objs.append(shaft)

    # ── Head (conical tip)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.042, radius2=0.001,
                                    depth=0.14, location=(ox, oy + 1.07, oz))
    head = bpy.context.active_object
    head.name = f'{name_prefix}Harpoon_Head'
    bev = head.modifiers.new('Bevel','BEVEL'); bev.width=0.004; bev.segments=2
    assign_mat(head, mats['iron']); objs.append(head)

    # ── Barbs (2 hooks, angled backward)
    for side, sx in (('L',-1),('R',1)):
        bm2 = bmesh.new()
        # Barb: small swept spike starting at 0.88m, angling back and out
        base_pt  = Vector((ox + sx*0.042, oy + 0.92, oz))
        mid_pt   = Vector((ox + sx*0.090, oy + 0.86, oz + 0.010))
        tip_pt   = Vector((ox + sx*0.110, oy + 0.80, oz + 0.005))
        pts = [base_pt, mid_pt, tip_pt]
        for pi_idx in range(len(pts)):
            r2 = max(0.003, 0.012 - pi_idx*0.004)
            for vi in range(8):
                ang = 2*math.pi*vi/8
                cx = pts[pi_idx].x + math.cos(ang)*r2*0.6
                cz = pts[pi_idx].z + math.sin(ang)*r2
                bm2.verts.new((cx, pts[pi_idx].y, cz))
        bm2.verts.ensure_lookup_table()
        for ri in range(len(pts)-1):
            for vi in range(8):
                a=ri*8+vi; b=ri*8+(vi+1)%8; c=(ri+1)*8+(vi+1)%8; d=(ri+1)*8+vi
                try: bm2.faces.new([bm2.verts[a],bm2.verts[b],bm2.verts[c],bm2.verts[d]])
                except: pass
        m2 = bpy.data.meshes.new(f'{name_prefix}Barb_{side}')
        bm2.to_mesh(m2); bm2.free()
        barb = bpy.data.objects.new(f'{name_prefix}Barb_{side}', m2)
        bpy.context.scene.collection.objects.link(barb)
        for p in barb.data.polygons: p.use_smooth = True
        assign_mat(barb, mats['iron']); objs.append(barb)

    # ── Rope ring at rear
    bpy.ops.mesh.primitive_torus_add(major_radius=0.042, minor_radius=0.006,
                                     major_segments=12, minor_segments=8,
                                     location=(ox, oy - 0.04, oz))
    ring = bpy.context.active_object
    ring.name = f'{name_prefix}Harpoon_RopeRing'
    ring.rotation_euler.x = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(ring, mats['iron']); objs.append(ring)

    # ── Rope coil at rear
    coil_pts = []
    for i in range(72):
        t = i / 72
        loops = 6
        r_coil = 0.055
        cx = ox + math.cos(t * math.pi * 2 * loops) * r_coil
        cy = oy - 0.08 - t * 0.12
        cz = oz + math.sin(t * math.pi * 2 * loops) * r_coil
        coil_pts.append((cx, cy, cz))
    bm3 = bmesh.new()
    segs3 = 6; r3 = 0.008
    all_r = []
    for pt in coil_pts:
        ring3 = []
        for vi in range(segs3):
            ang = 2*math.pi*vi/segs3
            ring3.append(bm3.verts.new((pt[0]+math.cos(ang)*r3, pt[1], pt[2]+math.sin(ang)*r3)))
        all_r.append(ring3)
    for ri in range(len(all_r)-1):
        for vi in range(segs3):
            a=all_r[ri][vi]; b=all_r[ri][(vi+1)%segs3]
            c=all_r[ri+1][(vi+1)%segs3]; d=all_r[ri+1][vi]
            try: bm3.faces.new([a,b,c,d])
            except: pass
    m3 = bpy.data.meshes.new(f'{name_prefix}Harpoon_RopeCoil')
    bm3.to_mesh(m3); bm3.free()
    coil = bpy.data.objects.new(f'{name_prefix}Harpoon_RopeCoil', m3)
    bpy.context.scene.collection.objects.link(coil)
    for p in coil.data.polygons: p.use_smooth = True
    assign_mat(coil, mats['rope']); objs.append(coil)

    return objs

# ──────────────────────────────────────────────
#  VARIANTS
# ──────────────────────────────────────────────

def build_harpoon_rack(mats, col):
    """3 harpoons mounted horizontally on a wall rack — nice island prop."""
    objs = []

    # Rack frame
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.80))
    rack = bpy.context.active_object
    rack.name = 'Harpoon_Rack_Frame'
    rack.scale = (0.06, 0.65, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(rack, mats['iron_old']); objs.append(rack)

    # 2 horizontal pegs
    for px in (-0.28, 0.28):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018,
                                            depth=0.12, location=(px, -0.05, 0.80))
        peg = bpy.context.active_object
        peg.name = f'Harpoon_Rack_Peg_{int(px*100)}'
        peg.rotation_euler.x = math.radians(90)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(peg, mats['iron']); objs.append(peg)

    # 3 harpoons resting on rack, slightly staggered
    for hi in range(3):
        z_offset = 0.96 + hi * 0.055
        hop = build_harpoon(mats, offset=(0, -0.14, z_offset), name_prefix=f'Rack_H{hi}_')
        objs.extend(hop)

    # Root empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = 'Harpoon_Rack_A_ROOT'
    for o in objs:
        o.parent = root
        link_obj(col, o)
    link_obj(col, root)
    print(f"[Props] Harpoon_Rack_A: {len(objs)} objects")


def build_harpoon_stuck(mats, col):
    """Harpoon embedded at 12° tilt — prop for 'used' / combat aftermath."""
    objs = build_harpoon(mats, name_prefix='Stuck_')
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = 'Harpoon_Stuck_A_ROOT'
    for o in objs:
        o.parent = root
        o.rotation_euler.x = math.radians(12)
        link_obj(col, o)
    link_obj(col, root)
    print(f"[Props] Harpoon_Stuck_A: {len(objs)} objects")

# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    setup_scene()

    mats = {
        'iron'     : build_iron_mat('Mat_Harpoon_Iron',     base=(0.11,0.11,0.11), metallic=1.0, roughness=0.25),
        'iron_old' : build_iron_mat('Mat_Harpoon_Iron_Old', base=(0.16,0.14,0.12), metallic=0.70, roughness=0.70),
        'rope'     : build_rope_mat('Mat_Harpoon_Rope',     base=(0.77,0.64,0.35)),
    }

    col = new_col('IsleTrial_Props_Harpoon')

    # Variant 1 — Projectile (clean single harpoon)
    proj_objs = build_harpoon(mats, name_prefix='')
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    proj_root = bpy.context.active_object
    proj_root.name = 'Harpoon_Projectile_ROOT'
    tip_pos = None
    for o in proj_objs:
        o.parent = proj_root
        link_obj(col, o)
        if 'Head' in o.name:
            # Compute approximate tip world position
            tip_pos = (o.location.x, o.location.y + 0.14, o.location.z)
        uv_unwrap(o)
    link_obj(col, proj_root)

    # Variant 2 — Rack with 3 harpoons
    build_harpoon_rack(mats, col)

    # Variant 3 — Stuck in ground
    build_harpoon_stuck(mats, col)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D':
                    sp.shading.type = 'MATERIAL'
            break

    print("\n" + "="*60)
    print("  IsleTrial — Harpoon Props Complete")
    print("="*60)
    print("  Variants  : Harpoon_Projectile · Harpoon_Rack_A · Harpoon_Stuck_A")
    if tip_pos:
        print(f"  Tip pos   : {tip_pos}  ← Unity hit-detection point")
    print("  Collection: IsleTrial_Props_Harpoon")
    print("="*60 + "\n")

main()
