"""
IsleTrial — Mushroom Boat  (Main Vessel v2)
Blender 4.x  •  Python Script

Concept: mushroom-cabin sailing boat — large enough for
         2 Mushroom NPCs  +  2 Compass NPCs  +  1 Kael

Hull dimensions
──────────────────────────────────────────
  Total length   :  9.0 m  (Y −4.5 → +4.5)
  Beam at midship:  3.6 m  (X −1.80 → +1.80)
  Keel to deck   :  1.82 m (Z 0 → 1.82)
  Deck area      : ~7.5 × 2.8 m  ≈ 21 m²  (≈ 4 m² / person)

Coordinate system
──────────────────────────────────────────
  Z = 0    waterline / keel
  Z = 1.82 deck / gunwale
  Y = −4.5 bow (front)
  Y = +4.5 stern (back)
  X = 0    centreline

Mesh objects
──────────────────────────────────────────
  Hull · Deck · Deck_Rim
  Moss_Trim_L/R  (green moss on gunwale)
  Cabin_Base  Cabin_Door  Cabin_Window_L/R
  MushroomCap  MushroomSpot_0-7  Mushroom_Stem
  Compass_Frame  Compass_Face  Compass_Needle_NS  Compass_Needle_EW
  Cannon_Carriage_L/R  Cannon_Barrel_L/R  Cannon_Wheel_L/R
  Lantern_Body_0-3  Lantern_Glass_0-3  Lantern_Chain_0-3
  Chest_0/1  Crate_0/1/2
  Anchor  Anchor_Chain_0-7  Mooring_Ring_L/R
  Rudder  Bow_Figurehead

Materials (dual-path: procedural + [UNITY] image slots)
──────────────────────────────────────────
  Mat_Hull_Wood     – dark aged hull planks
  Mat_Deck_Wood     – lighter deck boards
  Mat_Cabin_Wood    – medium brown cabin
  Mat_Iron          – dark oxidised iron
  Mat_Mushroom_Cap  – orange-red with noise spots
  Mat_Moss          – bright green organic
  Mat_Lantern_Glass – warm emissive amber
  Mat_Brass         – warm gold/brass compass hardware
  Mat_Compass_Face  – parchment star-rose
  Mat_Rope          – tan rope

Run 08_MushroomBoat_Rig.py AFTER this script.
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
    for p in obj.data.polygons:
        p.use_smooth = True

# ──────────────────────────────────────────────
#  MATERIAL NODE HELPERS
# ──────────────────────────────────────────────

def _n(nodes, ntype, loc, label=None):
    n = nodes.new(ntype)
    n.location = loc
    if label:
        n.label = label
        n.name  = label
    return n

def _img(nodes, slot_name, loc):
    n = nodes.new('ShaderNodeTexImage')
    n.location = loc
    n.label    = slot_name
    n.name     = slot_name
    return n

def _coord_map(nodes, links, scale=(6, 6, 6), loc=(-1000, 0)):
    tc = _n(nodes, 'ShaderNodeTexCoord', (loc[0],       loc[1]))
    mp = _n(nodes, 'ShaderNodeMapping',  (loc[0] + 200, loc[1]))
    mp.inputs['Scale'].default_value = scale
    links.new(tc.outputs['UV'], mp.inputs['Vector'])
    return mp

def _bump(nodes, links, height_sock, strength=0.5, dist=0.01):
    b = _n(nodes, 'ShaderNodeBump', (-100, -200))
    b.inputs['Strength'].default_value = strength
    b.inputs['Distance'].default_value = dist
    links.new(height_sock, b.inputs['Height'])
    return b

# ──────────────────────────────────────────────
#  MATERIALS
# ──────────────────────────────────────────────

def build_wood_mat(name, dark, light, roughness=0.88, scale=8.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (500, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (100, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value  = 0.0

    mp = _coord_map(N, L, scale=(scale, scale, scale), loc=(-1000, 100))

    wave = _n(N, 'ShaderNodeTexWave', (-700, 200))
    wave.wave_type = 'RINGS'; wave.rings_direction = 'X'
    wave.inputs['Scale'].default_value      = 4.0
    wave.inputs['Distortion'].default_value = 5.0
    wave.inputs['Detail'].default_value     = 8.0
    L.new(mp.outputs['Vector'], wave.inputs['Vector'])

    noise = _n(N, 'ShaderNodeTexNoise', (-700, -80))
    noise.inputs['Scale'].default_value     = 10.0
    noise.inputs['Detail'].default_value    = 6.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    cr = _n(N, 'ShaderNodeValToRGB', (-420, 130))
    cr.color_ramp.elements[0].color = (*dark,  1.0)
    cr.color_ramp.elements[1].color = (*light, 1.0)
    L.new(wave.outputs['Color'], cr.inputs['Fac'])

    # Noise-driven roughness
    cr_r = _n(N, 'ShaderNodeValToRGB', (-420, -80))
    cr_r.color_ramp.elements[0].color = (roughness - 0.08,) * 3 + (1.0,)
    cr_r.color_ramp.elements[1].color = (min(1, roughness + 0.12),) * 3 + (1.0,)
    L.new(noise.outputs['Fac'], cr_r.inputs['Fac'])
    L.new(cr_r.outputs['Color'], bsdf.inputs['Roughness'])

    # Bump from wood rings
    bmp = _bump(N, L, wave.outputs['Color'], 0.55, 0.012)
    L.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-700, -340))
    mix = _n(N, 'ShaderNodeMixRGB', (-150, 130), 'Mix_Albedo')
    mix.inputs['Fac'].default_value = 0.0
    L.new(cr.outputs['Color'],  mix.inputs['Color1'])
    L.new(img.outputs['Color'], mix.inputs['Color2'])
    L.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_iron_mat(name, base=(0.08, 0.07, 0.07)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (400, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Metallic'].default_value  = 0.88
    bsdf.inputs['Roughness'].default_value = 0.70

    mp = _coord_map(N, L, scale=(14, 14, 14), loc=(-900, 0))
    noise = _n(N, 'ShaderNodeTexNoise', (-680, 80))
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 5.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    dark = tuple(max(0, c * 0.45) for c in base)
    cr = _n(N, 'ShaderNodeValToRGB', (-400, 80))
    cr.color_ramp.elements[0].color = (*dark, 1.0)
    cr.color_ramp.elements[1].color = (*base, 1.0)
    L.new(noise.outputs['Fac'], cr.inputs['Fac'])

    bmp = _bump(N, L, noise.outputs['Fac'], 0.3, 0.006)
    L.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-680, -300))
    mix = _n(N, 'ShaderNodeMixRGB', (-150, 80), 'Mix_Albedo')
    mix.inputs['Fac'].default_value = 0.0
    L.new(cr.outputs['Color'],  mix.inputs['Color1'])
    L.new(img.outputs['Color'], mix.inputs['Color2'])
    L.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_mushroom_mat(name, base=(0.82, 0.28, 0.05)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (400, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.82
    bsdf.inputs['Metallic'].default_value  = 0.0
    try:
        bsdf.inputs['Subsurface Weight'].default_value = 0.06
    except KeyError:
        pass

    mp = _coord_map(N, L, scale=(4, 4, 4), loc=(-900, 0))
    noise = _n(N, 'ShaderNodeTexNoise', (-680, 80))
    noise.inputs['Scale'].default_value  = 6.0
    noise.inputs['Detail'].default_value = 5.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    vor = _n(N, 'ShaderNodeTexVoronoi', (-680, -100))
    vor.inputs['Scale'].default_value = 10.0
    vor.feature = 'SMOOTH_F1'
    L.new(mp.outputs['Vector'], vor.inputs['Vector'])

    dark = tuple(max(0, c * 0.60) for c in base)
    cr = _n(N, 'ShaderNodeValToRGB', (-400, 80))
    cr.color_ramp.elements[0].color = (*dark, 1.0)
    cr.color_ramp.elements[1].color = (*base, 1.0)
    L.new(noise.outputs['Fac'], cr.inputs['Fac'])

    mix_v = _n(N, 'ShaderNodeMixRGB', (-200, 0))
    mix_v.blend_type = 'MULTIPLY'
    mix_v.inputs['Fac'].default_value = 0.20
    L.new(cr.outputs['Color'],  mix_v.inputs['Color1'])
    L.new(vor.outputs['Color'], mix_v.inputs['Color2'])

    bmp = _bump(N, L, noise.outputs['Fac'], 0.40, 0.010)
    L.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-680, -340))
    mix_u = _n(N, 'ShaderNodeMixRGB', (-50, 0), 'Mix_Unity')
    mix_u.inputs['Fac'].default_value = 0.0
    L.new(mix_v.outputs['Color'], mix_u.inputs['Color1'])
    L.new(img.outputs['Color'],   mix_u.inputs['Color2'])
    L.new(mix_u.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_moss_mat(name, base=(0.15, 0.42, 0.08)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (300, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Metallic'].default_value  = 0.0

    mp = _coord_map(N, L, scale=(20, 20, 20), loc=(-800, 0))
    noise = _n(N, 'ShaderNodeTexNoise', (-580, 80))
    noise.inputs['Scale'].default_value  = 18.0
    noise.inputs['Detail'].default_value = 6.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    dark = tuple(max(0, c * 0.5) for c in base)
    cr = _n(N, 'ShaderNodeValToRGB', (-340, 80))
    cr.color_ramp.elements[0].color = (*dark, 1.0)
    cr.color_ramp.elements[1].color = (*base, 1.0)
    L.new(noise.outputs['Fac'], cr.inputs['Fac'])
    L.new(cr.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_emissive_mat(name, color=(1.0, 0.72, 0.18), strength=3.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (300, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value  = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value   = 0.05
    try:
        bsdf.inputs['Emission Color'].default_value    = (*color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = strength
    except KeyError:
        pass
    return mat


def build_brass_mat(name, base=(0.78, 0.55, 0.18)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (300, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (*base, 1.0)
    bsdf.inputs['Metallic'].default_value   = 0.95
    bsdf.inputs['Roughness'].default_value  = 0.28

    mp = _coord_map(N, L, scale=(12, 12, 12), loc=(-800, 0))
    noise = _n(N, 'ShaderNodeTexNoise', (-600, 80))
    noise.inputs['Scale'].default_value = 16.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])
    bmp = _bump(N, L, noise.outputs['Fac'], 0.18, 0.004)
    L.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    return mat


def build_compass_face_mat(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (300, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value = (0.92, 0.88, 0.72, 1.0)
    bsdf.inputs['Roughness'].default_value  = 0.72
    bsdf.inputs['Metallic'].default_value   = 0.0

    mp = _coord_map(N, L, scale=(3, 3, 3), loc=(-800, 0))
    noise = _n(N, 'ShaderNodeTexNoise', (-600, 80))
    noise.inputs['Scale'].default_value  = 5.0
    noise.inputs['Detail'].default_value = 3.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    cr = _n(N, 'ShaderNodeValToRGB', (-360, 80))
    cr.color_ramp.elements[0].color = (0.80, 0.74, 0.58, 1.0)
    cr.color_ramp.elements[1].color = (0.94, 0.90, 0.76, 1.0)
    L.new(noise.outputs['Fac'], cr.inputs['Fac'])
    L.new(cr.outputs['Color'], bsdf.inputs['Base Color'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-600, -280))
    mix = _n(N, 'ShaderNodeMixRGB', (-120, 80), 'Mix_Unity')
    mix.inputs['Fac'].default_value = 0.0
    L.new(cr.outputs['Color'],  mix.inputs['Color1'])
    L.new(img.outputs['Color'], mix.inputs['Color2'])
    L.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def build_rope_mat(name, base=(0.72, 0.58, 0.30)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (300, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.90
    bsdf.inputs['Metallic'].default_value  = 0.0

    mp = _coord_map(N, L, scale=(20, 20, 20), loc=(-800, 0))
    wave = _n(N, 'ShaderNodeTexWave', (-600, 80))
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 25.0
    wave.inputs['Distortion'].default_value = 2.5
    L.new(mp.outputs['Vector'], wave.inputs['Vector'])

    dark = tuple(max(0, c * 0.58) for c in base)
    cr = _n(N, 'ShaderNodeValToRGB', (-360, 80))
    cr.color_ramp.elements[0].color = (*dark, 1.0)
    cr.color_ramp.elements[1].color = (*base, 1.0)
    L.new(wave.outputs['Color'], cr.inputs['Fac'])
    L.new(cr.outputs['Color'], bsdf.inputs['Base Color'])
    return mat

# ──────────────────────────────────────────────
#  HULL  (port-side profile + mirror modifier)
# ──────────────────────────────────────────────

def build_hull(mats):
    """
    Hull cross-section built from stations.
    Port side (X ≤ 0) created in bmesh; mirror modifier adds starboard.
    Stations: (y, half_width, keel_z, deck_z)
    6 ring-verts per station (keel → bilge → gunwale)
    """
    objs = []

    stations = [
        (-4.40, 0.00, 1.42, 1.55),
        (-3.90, 0.22, 0.52, 1.62),
        (-3.00, 0.80, 0.12, 1.72),
        (-1.50, 1.08, 0.02, 1.79),
        ( 0.00, 1.20, 0.00, 1.82),
        ( 1.50, 1.18, 0.02, 1.80),
        ( 3.00, 1.05, 0.12, 1.74),
        ( 3.90, 0.78, 0.40, 1.64),
        ( 4.40, 0.58, 0.80, 1.56),
    ]
    NR = 6  # rings per station from keel to deck
    NS = len(stations)

    bm = bmesh.new()
    all_rings = []

    for (y, hw, kz, dz) in stations:
        ring = []
        for ri in range(NR):
            t  = ri / (NR - 1)
            ang = t * math.pi / 2
            x  = -hw * math.sin(ang)
            z  = kz + (dz - kz) * (1.0 - math.cos(ang))
            ring.append(bm.verts.new((x, y, z)))
        all_rings.append(ring)

    # Quad faces between adjacent stations
    for si in range(NS - 1):
        r0 = all_rings[si]
        r1 = all_rings[si + 1]
        for vi in range(NR - 1):
            try:
                bm.faces.new([r0[vi], r0[vi + 1], r1[vi + 1], r1[vi]])
            except Exception:
                pass

    # Bow: triangle-fan from bow-tip station (hw≈0, all verts clumped)
    bow = all_rings[0]
    for vi in range(NR - 1):
        try:
            bm.faces.new([bow[0], all_rings[1][vi], all_rings[1][vi + 1]])
        except Exception:
            pass

    # Stern transom n-gon
    stern = all_rings[-1]
    try:
        bm.faces.new(stern[::-1])
    except Exception:
        for vi in range(1, NR - 1):
            try:
                bm.faces.new([stern[0], stern[vi + 1], stern[vi]])
            except Exception:
                pass

    # Keel bottom strip (connect all keel vertices)
    keel_verts = [r[0] for r in all_rings]
    for ki in range(NS - 1):
        try:
            bm.faces.new([keel_verts[ki + 1], keel_verts[ki],
                           all_rings[ki][0], all_rings[ki + 1][0]])
        except Exception:
            pass

    mesh = bpy.data.meshes.new('Hull')
    bm.to_mesh(mesh)
    bm.free()

    hull = bpy.data.objects.new('Hull', mesh)
    bpy.context.scene.collection.objects.link(hull)
    smooth_shade(hull)

    mir = hull.modifiers.new('Mirror', 'MIRROR')
    mir.use_axis[0] = True
    mir.merge_threshold = 0.015

    sub = hull.modifiers.new('Sub', 'SUBSURF')
    sub.levels = 2

    assign_mat(hull, mats['hull_wood'])
    objs.append(hull)

    # Inner hull (slightly smaller duplicate for interior visibility)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1.30))
    inner = bpy.context.active_object
    inner.name = 'Hull_Inner'
    inner.scale = (1.15, 4.30, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    sub2 = inner.modifiers.new('Sub', 'SUBSURF')
    sub2.levels = 1
    assign_mat(inner, mats['hull_wood'])
    objs.append(inner)

    return objs

# ──────────────────────────────────────────────
#  DECK
# ──────────────────────────────────────────────

def build_deck(mats):
    objs = []

    # Main deck floor
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 1.82))
    deck = bpy.context.active_object
    deck.name = 'Deck'
    deck.scale = (1.18, 4.35, 1.0)
    bpy.ops.object.transform_apply(scale=True)

    # Add loop cuts for plank appearance in texture
    activate(deck)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=8)
    bpy.ops.object.mode_set(mode='OBJECT')

    sol = deck.modifiers.new('Solidify', 'SOLIDIFY')
    sol.thickness = 0.055; sol.offset = -1.0
    assign_mat(deck, mats['deck_wood'])
    objs.append(deck)

    # Deck rim (gunwale — raised edge around deck)
    for side, x in (('L', -1), ('R', 1)):
        bpy.ops.mesh.primitive_cube_add(location=(x * 1.20, 0, 1.94))
        rim = bpy.context.active_object
        rim.name = f'Deck_Rim_{side}'
        rim.scale = (0.058, 4.30, 0.068)
        bpy.ops.object.transform_apply(scale=True)
        bev = rim.modifiers.new('Bevel', 'BEVEL')
        bev.width = 0.012; bev.segments = 2
        assign_mat(rim, mats['deck_wood'])
        objs.append(rim)

    # Bow and stern rim caps
    for label, y in (('Bow', -4.28), ('Stern', 4.28)):
        bpy.ops.mesh.primitive_cube_add(location=(0, y, 1.94))
        cap = bpy.context.active_object
        cap.name = f'Deck_Rim_{label}'
        cap.scale = (1.26, 0.06, 0.068)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(cap, mats['deck_wood'])
        objs.append(cap)

    # Moss trim along both sides of gunwale
    for side, x in (('L', -1.22), ('R', 1.22)):
        bpy.ops.mesh.primitive_cube_add(location=(x, 0, 1.88))
        moss = bpy.context.active_object
        moss.name = f'Moss_Trim_{side[0]}'
        moss.scale = (0.04, 4.25, 0.042)
        bpy.ops.object.transform_apply(scale=True)

        activate(moss)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.subdivide(number_cuts=12)
        bm = bmesh.from_edit_mesh(moss.data)
        import random; random.seed(42)
        for v in bm.verts:
            if abs(v.co.z - 1.88) < 0.05:
                v.co.z += random.uniform(0, 0.04)
        bmesh.update_edit_mesh(moss.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        assign_mat(moss, mats['moss'])
        objs.append(moss)

    return objs

# ──────────────────────────────────────────────
#  MUSHROOM CABIN
# ──────────────────────────────────────────────

def build_cabin(mats):
    objs = []

    # Cabin base walls — central 3m section
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 2.62))
    cabin = bpy.context.active_object
    cabin.name = 'Cabin_Base'
    cabin.scale = (0.90, 1.60, 0.80)
    bpy.ops.object.transform_apply(scale=True)

    # Cut out door opening on front face
    activate(cabin)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(cabin.data)
    front_faces = [f for f in bm.faces if f.normal.y < -0.9]
    for f in front_faces:
        bmesh.ops.inset_individual(bm, faces=[f], thickness=0.06, depth=0)
    bmesh.update_edit_mesh(cabin.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    sub = cabin.modifiers.new('Sub', 'SUBSURF'); sub.levels = 1
    assign_mat(cabin, mats['cabin_wood'])
    objs.append(cabin)

    # Door frame arch
    bpy.ops.mesh.primitive_cube_add(location=(0, -0.912, 2.36))
    door_frame = bpy.context.active_object
    door_frame.name = 'Cabin_Door_Frame'
    door_frame.scale = (0.38, 0.04, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(door_frame, mats['iron'])
    objs.append(door_frame)

    # Door panels
    bpy.ops.mesh.primitive_cube_add(location=(0, -0.924, 2.38))
    door = bpy.context.active_object
    door.name = 'Cabin_Door'
    door.scale = (0.34, 0.030, 0.50)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(door, mats['cabin_wood'])
    objs.append(door)

    # Windows (left and right of cabin)
    for side, x in (('L', -0.914), ('R', 0.914)):
        bpy.ops.mesh.primitive_cube_add(location=(x, 0, 2.72))
        win = bpy.context.active_object
        win.name = f'Cabin_Window_{side}'
        win.scale = (0.030, 0.22, 0.26)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(win, mats['brass'])
        objs.append(win)

        # Window glass glow
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(x * 1.005, 0, 2.72))
        wg = bpy.context.active_object
        wg.name = f'Cabin_Window_Glass_{side}'
        wg.scale = (0.015, 0.19, 0.22)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(wg, mats['lantern_glass'])
        objs.append(wg)

    # Stem (mushroom stalk connecting cabin to cap)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.52, depth=0.80,
                                        location=(0, 0, 3.82))
    stem = bpy.context.active_object
    stem.name = 'Mushroom_Stem'
    stem.scale = (1.0, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(stem, mats['cabin_wood'])
    objs.append(stem)

    return objs


def build_mushroom_cap(mats):
    objs = []

    # Large mushroom cap (main roof)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16,
                                         radius=2.60, location=(0, 0, 4.10))
    cap = bpy.context.active_object
    cap.name = 'MushroomCap'
    cap.scale = (1.0, 0.95, 0.60)
    bpy.ops.object.transform_apply(scale=True)

    # Remove lower hemisphere (below Z=2.90)
    activate(cap)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(cap.data)
    to_del = [v for v in bm.verts if v.co.z < 2.88]
    bmesh.ops.delete(bm, geom=to_del, context='VERTS')
    bpy.ops.mesh.select_all(action='SELECT')
    # Flatten bottom edge
    for v in bm.verts:
        if v.co.z < 3.00:
            v.co.z = 2.92
    bmesh.update_edit_mesh(cap.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Fill the bottom hole
    activate(cap)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.boundary_edges()
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode='OBJECT')

    smooth_shade(cap)
    sub = cap.modifiers.new('Sub', 'SUBSURF'); sub.levels = 2
    assign_mat(cap, mats['mushroom'])
    objs.append(cap)

    # White spots on the cap
    spot_positions = [
        (0.80,  0.40, 5.50), (-0.90,  0.20, 5.30), ( 0.20, -0.80, 5.60),
        (-0.40, -0.60, 5.80), ( 0.55, -1.20, 5.10), (-1.10, -0.80, 4.90),
        ( 1.30, -0.30, 4.80), (-0.20,  1.20, 5.20),
    ]
    for si, (x, y, z) in enumerate(spot_positions):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8,
                                             radius=0.28, location=(x, y, z))
        spot = bpy.context.active_object
        spot.name = f'MushroomSpot_{si}'
        spot.scale = (1.0, 1.0, 0.22)
        bpy.ops.object.transform_apply(scale=True)
        bpy.data.materials.new(f'Mat_MushroomSpot_{si}')
        spot_mat = bpy.data.materials['Mat_MushroomSpot_0'] if si == 0 else bpy.data.materials.new(f'Mat_MushroomSpot_{si}')
        spot_mat = bpy.data.materials.new(f'Mat_MushroomSpot')
        spot_mat.use_nodes = True
        spot_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.95, 0.92, 0.82, 1.0)
        spot_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.85
        assign_mat(spot, spot_mat)
        objs.append(spot)

    # Decorative rim ring at cap edge
    bpy.ops.mesh.primitive_torus_add(major_radius=2.55, minor_radius=0.075,
                                     major_segments=40, minor_segments=8,
                                     location=(0, 0, 3.00))
    rim = bpy.context.active_object
    rim.name = 'Cap_Rim'
    rim.scale = (1.0, 0.95, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(rim, mats['cabin_wood'])
    objs.append(rim)

    return objs

# ──────────────────────────────────────────────
#  COMPASS ROSE INSTRUMENT
# ──────────────────────────────────────────────

def build_compass(mats):
    objs = []

    # Main compass frame (torus)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.92, minor_radius=0.085,
                                     major_segments=36, minor_segments=10,
                                     location=(0, -1.60, 2.30))
    frame = bpy.context.active_object
    frame.name = 'Compass_Frame'
    frame.rotation_euler.x = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(frame, mats['brass'])
    objs.append(frame)

    # Inner ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.80, minor_radius=0.045,
                                     major_segments=36, minor_segments=8,
                                     location=(0, -1.62, 2.30))
    inner_ring = bpy.context.active_object
    inner_ring.name = 'Compass_InnerRing'
    inner_ring.rotation_euler.x = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(inner_ring, mats['brass'])
    objs.append(inner_ring)

    # Compass face disc
    bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.80, depth=0.030,
                                        location=(0, -1.64, 2.30))
    face = bpy.context.active_object
    face.name = 'Compass_Face'
    face.rotation_euler.x = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(face, mats['compass_face'])
    objs.append(face)

    # N-S needle (red/white — thin flat diamond)
    bpy.ops.mesh.primitive_cube_add(location=(0, -1.67, 2.30))
    ns = bpy.context.active_object
    ns.name = 'Compass_Needle_NS'
    ns.scale = (0.06, 0.008, 0.72)
    bpy.ops.object.transform_apply(scale=True)
    needle_mat = bpy.data.materials.new('Mat_Compass_Needle_NS')
    needle_mat.use_nodes = True
    needle_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.85, 0.10, 0.10, 1.0)
    needle_mat.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 0.9
    needle_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.2
    assign_mat(ns, needle_mat)
    objs.append(ns)

    # E-W needle (blue)
    bpy.ops.mesh.primitive_cube_add(location=(0, -1.67, 2.30))
    ew = bpy.context.active_object
    ew.name = 'Compass_Needle_EW'
    ew.scale = (0.72, 0.008, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    ew_mat = bpy.data.materials.new('Mat_Compass_Needle_EW')
    ew_mat.use_nodes = True
    ew_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.10, 0.25, 0.80, 1.0)
    ew_mat.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 0.9
    ew_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.2
    assign_mat(ew, ew_mat)
    objs.append(ew)

    # Compass mount bracket
    bpy.ops.mesh.primitive_cube_add(location=(0, -1.55, 1.95))
    bracket = bpy.context.active_object
    bracket.name = 'Compass_Mount'
    bracket.scale = (0.12, 0.10, 0.38)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(bracket, mats['iron'])
    objs.append(bracket)

    # Decorative bolts on frame
    for angle_deg in range(0, 360, 45):
        a = math.radians(angle_deg)
        x = math.cos(a) * 0.92; z = math.sin(a) * 0.92
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.030,
                                            depth=0.055, location=(x, -1.660, 2.30 + z))
        bolt = bpy.context.active_object
        bolt.name = f'Compass_Bolt_{angle_deg}'
        bolt.rotation_euler.x = math.radians(90)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(bolt, mats['brass'])
        objs.append(bolt)

    return objs

# ──────────────────────────────────────────────
#  CANNONS
# ──────────────────────────────────────────────

def build_cannons(mats):
    objs = []

    for side, sx, y_off in (('L', -1, -2.50), ('R', 1, -2.50)):
        # Cannon carriage (wooden base with wheels)
        bpy.ops.mesh.primitive_cube_add(location=(sx * 1.08, y_off, 2.10))
        carr = bpy.context.active_object
        carr.name = f'Cannon_Carriage_{side}'
        carr.scale = (0.30, 0.68, 0.22)
        bpy.ops.object.transform_apply(scale=True)
        bev = carr.modifiers.new('Bevel', 'BEVEL')
        bev.width = 0.018; bev.segments = 2
        assign_mat(carr, mats['cabin_wood'])
        objs.append(carr)

        # 2 wheels
        for wy_off in (-0.32, 0.32):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.028,
                                             major_segments=20, minor_segments=8,
                                             location=(sx * 1.08, y_off + wy_off, 1.92))
            wh = bpy.context.active_object
            wh.name = f'Cannon_Wheel_{side}_{int(wy_off*100)}'
            wh.rotation_euler.x = math.radians(90)
            bpy.ops.object.transform_apply(rotation=True)
            assign_mat(wh, mats['iron'])
            objs.append(wh)

        # Cannon barrel
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.095, depth=1.60,
                                            location=(sx * 1.30, y_off - 0.30, 2.24))
        barrel = bpy.context.active_object
        barrel.name = f'Cannon_Barrel_{side}'
        barrel.rotation_euler.y = math.radians(90)
        barrel.scale = (1.0, 1.0, 1.0)
        bpy.ops.object.transform_apply(rotation=True)
        # Taper toward muzzle
        activate(barrel)
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(barrel.data)
        for v in bm.verts:
            if v.co.y < -0.50:  # muzzle end
                fac = (v.co.y + 0.80) / 0.30
                fac = max(0, min(1, fac))
                v.co.x *= (0.70 + 0.30 * fac)
                v.co.z *= (0.70 + 0.30 * fac)
        bmesh.update_edit_mesh(barrel.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        bev2 = barrel.modifiers.new('Bevel', 'BEVEL'); bev2.width = 0.008; bev2.segments = 2
        assign_mat(barrel, mats['iron'])
        objs.append(barrel)

        # Barrel bands (3 iron rings)
        for bi, by in enumerate([-0.20, 0.05, 0.30]):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.105, minor_radius=0.018,
                                             major_segments=12, minor_segments=6,
                                             location=(sx * 1.30, y_off + by - 0.30, 2.24))
            band = bpy.context.active_object
            band.name = f'Cannon_Band_{side}_{bi}'
            band.rotation_euler.y = math.radians(90)
            bpy.ops.object.transform_apply(rotation=True)
            assign_mat(band, mats['iron'])
            objs.append(band)

    return objs

# ──────────────────────────────────────────────
#  LANTERNS (4)
# ──────────────────────────────────────────────

def build_lanterns(mats):
    objs = []

    # Lantern positions: bow-L, bow-R, stern-L, stern-R
    lantern_pos = [
        (-1.10, -3.60, 2.38, 'Bow_L'),
        ( 1.10, -3.60, 2.38, 'Bow_R'),
        (-1.10,  3.60, 2.38, 'Stern_L'),
        ( 1.10,  3.60, 2.38, 'Stern_R'),
    ]

    for i, (x, y, z, label) in enumerate(lantern_pos):
        # Chain from rim to lantern (3 links)
        z_rim = 2.02
        chain_len = z - z_rim
        for ci in range(4):
            t = ci / 3
            cz = z_rim + t * chain_len
            bpy.ops.mesh.primitive_torus_add(major_radius=0.025, minor_radius=0.008,
                                             major_segments=8, minor_segments=6,
                                             location=(x, y, cz))
            link = bpy.context.active_object
            link.name = f'Lantern_Chain_{i}_{ci}'
            if ci % 2 == 0:
                link.rotation_euler.x = math.radians(90)
            else:
                link.rotation_euler.z = math.radians(90)
            bpy.ops.object.transform_apply(rotation=True)
            assign_mat(link, mats['iron'])
            objs.append(link)

        # Lantern body (cage)
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
        body = bpy.context.active_object
        body.name = f'Lantern_Body_{i}'
        body.scale = (0.095, 0.095, 0.145)
        bpy.ops.object.transform_apply(scale=True)
        bev = body.modifiers.new('Bevel', 'BEVEL')
        bev.width = 0.018; bev.segments = 2
        assign_mat(body, mats['iron'])
        objs.append(body)

        # Top cap
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.10, radius2=0.025,
                                        depth=0.08, location=(x, y, z + 0.175))
        cap_l = bpy.context.active_object
        cap_l.name = f'Lantern_Cap_{i}'
        assign_mat(cap_l, mats['iron'])
        objs.append(cap_l)

        # Glass glow
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6,
                                             radius=0.075, location=(x, y, z))
        glass = bpy.context.active_object
        glass.name = f'Lantern_Glass_{i}'
        assign_mat(glass, mats['lantern_glass'])
        objs.append(glass)

    return objs

# ──────────────────────────────────────────────
#  CARGO (CHESTS + CRATES)
# ──────────────────────────────────────────────

def build_cargo(mats):
    objs = []

    # Treasure chests (back of deck)
    chest_positions = [(-0.60, 2.80, 1.82), (0.60, 2.80, 1.82)]
    for ci, (x, y, z) in enumerate(chest_positions):
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z + 0.18))
        chest = bpy.context.active_object
        chest.name = f'Chest_{ci}'
        chest.scale = (0.28, 0.22, 0.18)
        bpy.ops.object.transform_apply(scale=True)
        bev = chest.modifiers.new('Bevel', 'BEVEL')
        bev.width = 0.012; bev.segments = 2
        assign_mat(chest, mats['cabin_wood'])
        objs.append(chest)

        # Iron band
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z + 0.18))
        band = bpy.context.active_object
        band.name = f'Chest_Band_{ci}'
        band.scale = (0.285, 0.225, 0.030)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(band, mats['iron'])
        objs.append(band)

        # Lock
        bpy.ops.mesh.primitive_cube_add(location=(x, y - 0.226, z + 0.20))
        lock = bpy.context.active_object
        lock.name = f'Chest_Lock_{ci}'
        lock.scale = (0.040, 0.015, 0.040)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(lock, mats['iron'])
        objs.append(lock)

    # Crates
    crate_pos = [
        ( 0.75, 1.20, 1.82),
        (-0.80, 1.40, 1.82),
        ( 0.80, 1.80, 2.14),  # stacked
    ]
    for ci, (x, y, z) in enumerate(crate_pos):
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z + 0.16))
        crate = bpy.context.active_object
        crate.name = f'Crate_{ci}'
        crate.scale = (0.22, 0.22, 0.16)
        bpy.ops.object.transform_apply(scale=True)
        bev = crate.modifiers.new('Bevel', 'BEVEL')
        bev.width = 0.008; bev.segments = 2
        assign_mat(crate, mats['cabin_wood'])
        objs.append(crate)

        # Crate cross-bands (2 iron straps)
        for axis in (0, 1):
            bpy.ops.mesh.primitive_cube_add(location=(x, y, z + 0.16))
            strap = bpy.context.active_object
            strap.name = f'Crate_Strap_{ci}_{axis}'
            if axis == 0:
                strap.scale = (0.225, 0.016, 0.165)
            else:
                strap.scale = (0.016, 0.225, 0.165)
            bpy.ops.object.transform_apply(scale=True)
            assign_mat(strap, mats['iron'])
            objs.append(strap)

    return objs

# ──────────────────────────────────────────────
#  RIGGING (ANCHOR, CHAINS, MOORING)
# ──────────────────────────────────────────────

def build_rigging(mats):
    objs = []

    # Anchor (iron)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.042, depth=1.20,
                                        location=(0, -3.80, 0.80))
    shaft = bpy.context.active_object
    shaft.name = 'Anchor_Shaft'
    assign_mat(shaft, mats['iron'])
    objs.append(shaft)

    # Anchor flukes
    for fx, label in ((-1, 'L'), (1, 'R')):
        bpy.ops.mesh.primitive_cube_add(location=(fx * 0.28, -3.80, 0.22))
        fluke = bpy.context.active_object
        fluke.name = f'Anchor_Fluke_{label}'
        fluke.scale = (0.28, 0.06, 0.14)
        fluke.rotation_euler = (0, 0, math.radians(fx * 30))
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(fluke, mats['iron'])
        objs.append(fluke)

    # Anchor crossbar
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.030, depth=0.80,
                                        location=(0, -3.80, 1.38))
    crossbar = bpy.context.active_object
    crossbar.name = 'Anchor_Crossbar'
    crossbar.rotation_euler.z = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(crossbar, mats['iron'])
    objs.append(crossbar)

    # Anchor chain (8 links from bow deck to anchor)
    chain_start = Vector((0, -4.10, 1.95))
    chain_end   = Vector((0, -3.80, 1.40))
    for li in range(8):
        t = li / 7
        pos = chain_start.lerp(chain_end, t)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.038, minor_radius=0.012,
                                         major_segments=8, minor_segments=6,
                                         location=(pos.x, pos.y, pos.z))
        link = bpy.context.active_object
        link.name = f'Anchor_Chain_{li}'
        if li % 2 == 0:
            link.rotation_euler.z = math.radians(90)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(link, mats['iron'])
        objs.append(link)

    # Mooring rings on hull sides (large iron rings)
    for side, x in (('L', -1.78), ('R', 1.78)):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.022,
                                         major_segments=16, minor_segments=8,
                                         location=(x, 0.50, 1.30))
        ring = bpy.context.active_object
        ring.name = f'Mooring_Ring_{side}'
        ring.rotation_euler.y = math.radians(90)
        bpy.ops.object.transform_apply(rotation=True)
        assign_mat(ring, mats['iron'])
        objs.append(ring)

    # Rudder (stern, below waterline)
    bpy.ops.mesh.primitive_cube_add(location=(0, 4.58, 0.72))
    rudder = bpy.context.active_object
    rudder.name = 'Rudder'
    rudder.scale = (0.060, 0.095, 0.72)
    bpy.ops.object.transform_apply(scale=True)
    bev_r = rudder.modifiers.new('Bevel', 'BEVEL')
    bev_r.width = 0.010; bev_r.segments = 2
    assign_mat(rudder, mats['hull_wood'])
    objs.append(rudder)

    # Bow figurehead — simple carved scroll
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.14, radius2=0.04,
                                    depth=0.42, location=(0, -4.62, 1.48))
    fig = bpy.context.active_object
    fig.name = 'Bow_Figurehead'
    fig.rotation_euler.x = math.radians(-35)
    bpy.ops.object.transform_apply(rotation=True)
    assign_mat(fig, mats['cabin_wood'])
    objs.append(fig)

    return objs

# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    setup_scene()

    mats = {
        'hull_wood'    : build_wood_mat('Mat_Hull_Wood',    dark=(0.20, 0.11, 0.04), light=(0.38, 0.22, 0.09), roughness=0.90, scale=7.0),
        'deck_wood'    : build_wood_mat('Mat_Deck_Wood',    dark=(0.28, 0.16, 0.06), light=(0.50, 0.32, 0.13), roughness=0.85, scale=9.0),
        'cabin_wood'   : build_wood_mat('Mat_Cabin_Wood',   dark=(0.32, 0.18, 0.07), light=(0.58, 0.38, 0.16), roughness=0.82, scale=10.0),
        'iron'         : build_iron_mat('Mat_Iron',         base=(0.09, 0.08, 0.07)),
        'mushroom'     : build_mushroom_mat('Mat_Mushroom_Cap', base=(0.82, 0.28, 0.06)),
        'moss'         : build_moss_mat('Mat_Moss',         base=(0.16, 0.42, 0.08)),
        'lantern_glass': build_emissive_mat('Mat_Lantern_Glass', color=(1.00, 0.76, 0.22), strength=3.8),
        'brass'        : build_brass_mat('Mat_Brass',       base=(0.78, 0.55, 0.18)),
        'compass_face' : build_compass_face_mat('Mat_Compass_Face'),
        'rope'         : build_rope_mat('Mat_Rope',         base=(0.72, 0.58, 0.30)),
    }

    all_objs = []
    all_objs.extend(build_hull(mats))
    all_objs.extend(build_deck(mats))
    all_objs.extend(build_cabin(mats))
    all_objs.extend(build_mushroom_cap(mats))
    all_objs.extend(build_compass(mats))
    all_objs.extend(build_cannons(mats))
    all_objs.extend(build_lanterns(mats))
    all_objs.extend(build_cargo(mats))
    all_objs.extend(build_rigging(mats))

    print(f"[MushroomBoat] UV unwrapping {len(all_objs)} objects...")
    for obj in all_objs:
        if obj.type == 'MESH':
            uv_unwrap(obj)

    col = new_col('IsleTrial_MushroomBoat')
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = 'MushroomBoat_ROOT'
    link_obj(col, root)
    for obj in all_objs:
        obj.parent = root
        link_obj(col, obj)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D':
                    sp.shading.type = 'MATERIAL'
            break

    print("\n" + "="*65)
    print("  IsleTrial — Mushroom Boat Model Complete")
    print("="*65)
    print(f"  Objects      : {len(all_objs)}")
    print("  Materials    : 10  (procedural + [UNITY] image slots)")
    print("  Hull         : 9.0 m  ×  3.6 m  ×  1.82 m")
    print("  Deck area    : ~21 m²  (fits 5 characters easily)")
    print("  Collection   : IsleTrial_MushroomBoat")
    print("  Next step    : Run 08_MushroomBoat_Rig.py")
    print("="*65 + "\n")


main()
