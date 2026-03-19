"""
IsleTrial – Weather Visual Assets  (27_Ocean_WeatherProps.py)  [REBUILT]
=========================================================================
Prompt 05-C: Storm & weather prop meshes.

  Driftwood_01…05  Bleached logs (skin-modifier organic volume)
                   Each: main trunk + 2–3 branches + root nub + knot bumps
                   + bark-striation grooves + waterlogged darkened end

  Debris_Plank_01/02/03  Broken planks (bmesh)
                   Splintered ends, plank bow, nail holes, rot patches,
                   algae stain strip on one end

  Debris_Plank_Short_01/02  Shorter broken stave fragments

  Debris_Barrel_Half  Half-barrel (bmesh half-cylinder)
                   Visible interior staves, 3 iron bands, cracked stave,
                   broken top hoop, spill stain disc at base

  Debris_Rope_Tangled  Tangled rope mass
                   6 overlapping curve loops + frayed fiber end cubes

  Debris_Sail_Torn  Torn sail cloth (bmesh grid)
                   Grommet ring holes along top edge, rope tie curves,
                   painted sun symbol disc, algae/mold stain patches,
                   Cloth modifier (keep for Unity physics)

  Debris_Mast_Fragment  1.5 m splintered mast pole
                   Painted stripe ring, rope remnant curve, metal band

  Debris_Hatch_Cover  Broken ship hatch: 4×4 plank grid + frame
  Debris_Canvas_Bundle  Rolled wet canvas with rope ties (3)

  VFX_Splash_Mesh  Splash crown: 18-drop outer ring + 8-drop inner crown
                   + base wave disc

  VFX_FoamPatch   Irregular foam disc + 6 inner bubble clusters
                   + displacement modifier

Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

rng = random.Random(0xD7A440)

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def new_col(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def link(col, obj):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def smart_uv(obj, angle=60):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=angle, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)

def new_mesh_obj(name, bm, col):
    me = bpy.data.meshes.new(name + '_Mesh')
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob

# ─────────────────────────────────────────────────────────────────────────────
#  MATERIAL SYSTEM  (dual-path: procedural + [UNITY] image slots)
# ─────────────────────────────────────────────────────────────────────────────

def _n(ns, t, loc, label=None):
    nd = ns.new(t); nd.location = loc
    if label: nd.label = nd.name = label
    return nd

def _img(ns, slot_name, loc):
    nd = ns.new('ShaderNodeTexImage'); nd.location = loc
    nd.label = nd.name = f'[UNITY] {slot_name}'
    return nd

def _base_mat(name):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    ns = mat.node_tree.nodes; lk = mat.node_tree.links; ns.clear()
    bsdf = _n(ns, 'ShaderNodeBsdfPrincipled', (400, 0))
    out  = _n(ns, 'ShaderNodeOutputMaterial',  (700, 0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat, ns, lk, bsdf

def build_driftwood_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Driftwood")
    mp = _n(ns, 'ShaderNodeTexCoord', (-820, 0))
    mapping = _n(ns, 'ShaderNodeMapping', (-640, 0))
    mapping.inputs['Scale'].default_value = (6.0, 6.0, 6.0)
    lk.new(mp.outputs['Object'], mapping.inputs['Vector'])
    # Main wood grain (noise)
    noise = _n(ns, 'ShaderNodeTexNoise', (-440, 200))
    noise.inputs['Scale'].default_value = 16.0
    noise.inputs['Detail'].default_value = 12.0
    noise.inputs['Roughness'].default_value = 0.70
    lk.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    cr = _n(ns, 'ShaderNodeValToRGB', (-200, 200))
    cr.color_ramp.elements[0].color = (0.65, 0.60, 0.50, 1)
    cr.color_ramp.elements[1].color = (0.88, 0.84, 0.74, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    # Surface aging darkening (Voronoi cracks)
    vor = _n(ns, 'ShaderNodeTexVoronoi', (-440, -40))
    vor.inputs['Scale'].default_value = 22.0
    lk.new(mapping.outputs['Vector'], vor.inputs['Vector'])
    age_mix = _n(ns, 'ShaderNodeMixRGB', (-60, 100))
    age_mix.blend_type = 'MULTIPLY'
    age_mix.inputs[0].default_value = 0.24
    lk.new(cr.outputs['Color'], age_mix.inputs[1])
    lk.new(vor.outputs['Color'], age_mix.inputs[2])
    # [UNITY] image slot
    img = _img(ns, 'Driftwood_Albedo', (-440, -240))
    img_n = _img(ns, 'Driftwood_Normal', (-440, -440))
    mix = _n(ns, 'ShaderNodeMixRGB', (160, 100))
    mix.inputs[0].default_value = 0.0
    lk.new(age_mix.outputs['Color'], mix.inputs[1])
    lk.new(img.outputs['Color'], mix.inputs[2])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bmp = _n(ns, 'ShaderNodeBump', (160, -200))
    bmp.inputs['Strength'].default_value = 0.55
    lk.new(noise.outputs['Fac'], bmp.inputs['Height'])
    nm = _n(ns, 'ShaderNodeNormalMap', (160, -400))
    lk.new(img_n.outputs['Color'], nm.inputs['Color'])
    mix_n = _n(ns, 'ShaderNodeMixRGB', (320, -300))
    mix_n.inputs[0].default_value = 0.0
    lk.new(bmp.outputs['Normal'], mix_n.inputs[1])
    lk.new(nm.outputs['Normal'], mix_n.inputs[2])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.95
    return mat

def build_old_wood_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Debris_Wood")
    mp = _n(ns, 'ShaderNodeTexCoord', (-820, 0))
    mapping = _n(ns, 'ShaderNodeMapping', (-640, 0))
    mapping.inputs['Scale'].default_value = (8.0, 8.0, 8.0)
    lk.new(mp.outputs['Object'], mapping.inputs['Vector'])
    wave = _n(ns, 'ShaderNodeTexWave', (-440, 200))
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 10.0
    wave.inputs['Distortion'].default_value = 4.0
    wave.inputs['Detail'].default_value = 6.0
    lk.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    noise = _n(ns, 'ShaderNodeTexNoise', (-440, -40))
    noise.inputs['Scale'].default_value = 30.0
    lk.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    cr = _n(ns, 'ShaderNodeValToRGB', (-200, 200))
    cr.color_ramp.elements[0].color = (0.14, 0.08, 0.03, 1)
    cr.color_ramp.elements[1].color = (0.32, 0.20, 0.08, 1)
    lk.new(wave.outputs['Fac'], cr.inputs['Fac'])
    grain_mix = _n(ns, 'ShaderNodeMixRGB', (-50, 90))
    grain_mix.blend_type = 'OVERLAY'
    grain_mix.inputs[0].default_value = 0.14
    lk.new(cr.outputs['Color'], grain_mix.inputs[1])
    lk.new(noise.outputs['Fac'], grain_mix.inputs[2])
    img = _img(ns, 'Debris_Wood_Albedo', (-440, -240))
    img_n = _img(ns, 'Debris_Wood_Normal', (-440, -440))
    mix = _n(ns, 'ShaderNodeMixRGB', (180, 80))
    mix.inputs[0].default_value = 0.0
    lk.new(grain_mix.outputs['Color'], mix.inputs[1])
    lk.new(img.outputs['Color'], mix.inputs[2])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bmp = _n(ns, 'ShaderNodeBump', (180, -200))
    bmp.inputs['Strength'].default_value = 0.88
    lk.new(wave.outputs['Fac'], bmp.inputs['Height'])
    nm = _n(ns, 'ShaderNodeNormalMap', (180, -400))
    lk.new(img_n.outputs['Color'], nm.inputs['Color'])
    mix_n = _n(ns, 'ShaderNodeMixRGB', (340, -300))
    mix_n.inputs[0].default_value = 0.0
    lk.new(bmp.outputs['Normal'], mix_n.inputs[1])
    lk.new(nm.outputs['Normal'], mix_n.inputs[2])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.92
    return mat

def build_rope_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Rope_Debris")
    mp = _n(ns, 'ShaderNodeTexCoord', (-680, 0))
    noise = _n(ns, 'ShaderNodeTexNoise', (-460, 200))
    noise.inputs['Scale'].default_value = 32.0
    noise.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['UV'], noise.inputs['Vector'])
    cr = _n(ns, 'ShaderNodeValToRGB', (-220, 200))
    cr.color_ramp.elements[0].color = (0.33, 0.23, 0.10, 1)
    cr.color_ramp.elements[1].color = (0.56, 0.44, 0.22, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    img = _img(ns, 'Rope_Albedo', (-460, -220))
    mix = _n(ns, 'ShaderNodeMixRGB', (180, 100))
    mix.inputs[0].default_value = 0.0
    lk.new(cr.outputs['Color'], mix.inputs[1])
    lk.new(img.outputs['Color'], mix.inputs[2])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.90
    bsdf.inputs['Sheen Weight'].default_value = 0.12
    return mat

def build_sail_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Sail_Torn")
    mat.blend_method = 'BLEND'
    mp = _n(ns, 'ShaderNodeTexCoord', (-700, 0))
    noise = _n(ns, 'ShaderNodeTexNoise', (-480, 200))
    noise.inputs['Scale'].default_value = 60.0
    noise.inputs['Detail'].default_value = 4.0
    lk.new(mp.outputs['UV'], noise.inputs['Vector'])
    cr_base = _n(ns, 'ShaderNodeValToRGB', (-230, 200))
    cr_base.color_ramp.elements[0].color = (0.72, 0.66, 0.54, 1)
    cr_base.color_ramp.elements[1].color = (0.84, 0.78, 0.64, 1)
    lk.new(noise.outputs['Fac'], cr_base.inputs['Fac'])
    # Algae stain (dark green gradient)
    stain = _n(ns, 'ShaderNodeTexNoise', (-480, -40))
    stain.inputs['Scale'].default_value = 4.0
    lk.new(mp.outputs['UV'], stain.inputs['Vector'])
    cr_stain = _n(ns, 'ShaderNodeValToRGB', (-230, -40))
    cr_stain.color_ramp.elements[0].color = (0.08, 0.18, 0.06, 1)
    cr_stain.color_ramp.elements[1].color = (0.72, 0.66, 0.54, 1)
    cr_stain.color_ramp.elements[0].position = 0.0
    cr_stain.color_ramp.elements[1].position = 0.45
    lk.new(stain.outputs['Fac'], cr_stain.inputs['Fac'])
    stain_blend = _n(ns, 'ShaderNodeMixRGB', (-40, 100))
    stain_blend.blend_type = 'MIX'
    stain_blend.inputs[0].default_value = 0.30
    lk.new(cr_base.outputs['Color'], stain_blend.inputs[1])
    lk.new(cr_stain.outputs['Color'], stain_blend.inputs[2])
    img = _img(ns, 'Sail_Albedo', (-480, -240))
    mix = _n(ns, 'ShaderNodeMixRGB', (180, 80))
    mix.inputs[0].default_value = 0.0
    lk.new(stain_blend.outputs['Color'], mix.inputs[1])
    lk.new(img.outputs['Color'], mix.inputs[2])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.86
    bsdf.inputs['Alpha'].default_value = 0.92
    bsdf.inputs['Sheen Weight'].default_value = 0.10
    return mat

def build_canvas_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Canvas_Bundle")
    mp = _n(ns, 'ShaderNodeTexCoord', (-680, 0))
    wave = _n(ns, 'ShaderNodeTexWave', (-460, 200))
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = 14.0
    wave.inputs['Distortion'].default_value = 2.0
    lk.new(mp.outputs['UV'], wave.inputs['Vector'])
    cr = _n(ns, 'ShaderNodeValToRGB', (-220, 200))
    cr.color_ramp.elements[0].color = (0.64, 0.58, 0.44, 1)
    cr.color_ramp.elements[1].color = (0.80, 0.74, 0.60, 1)
    lk.new(wave.outputs['Fac'], cr.inputs['Fac'])
    img = _img(ns, 'Canvas_Albedo', (-460, -220))
    mix = _n(ns, 'ShaderNodeMixRGB', (180, 100))
    mix.inputs[0].default_value = 0.0
    lk.new(cr.outputs['Color'], mix.inputs[1])
    lk.new(img.outputs['Color'], mix.inputs[2])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.88
    bsdf.inputs['Sheen Weight'].default_value = 0.08
    return mat

def build_water_vfx_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Water_VFX")
    mat.blend_method = 'BLEND'
    bsdf.inputs['Base Color'].default_value = (0.50, 0.78, 1.00, 1)
    bsdf.inputs['Roughness'].default_value = 0.08
    bsdf.inputs['Transmission Weight'].default_value = 0.82
    bsdf.inputs['Alpha'].default_value = 0.72
    bsdf.inputs['IOR'].default_value = 1.33
    bsdf.inputs['Emission Color'].default_value = (0.50, 0.78, 1.00, 1)
    bsdf.inputs['Emission Strength'].default_value = 0.08
    return mat

def build_foam_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Foam_VFX")
    mat.blend_method = 'BLEND'
    mp = _n(ns, 'ShaderNodeTexCoord', (-680, 0))
    noise = _n(ns, 'ShaderNodeTexNoise', (-460, 200))
    noise.inputs['Scale'].default_value = 40.0
    noise.inputs['Detail'].default_value = 10.0
    lk.new(mp.outputs['UV'], noise.inputs['Vector'])
    cr = _n(ns, 'ShaderNodeValToRGB', (-220, 200))
    cr.color_ramp.elements[0].color = (0.94, 0.96, 1.00, 1)
    cr.color_ramp.elements[1].color = (1.00, 1.00, 1.00, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.92
    bsdf.inputs['Alpha'].default_value = 0.86
    bmp = _n(ns, 'ShaderNodeBump', (180, -100))
    bmp.inputs['Strength'].default_value = 0.22
    lk.new(noise.outputs['Fac'], bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    return mat

def build_iron_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_IronBand")
    bsdf.inputs['Base Color'].default_value = (0.12, 0.11, 0.10, 1)
    bsdf.inputs['Metallic'].default_value = 0.88
    bsdf.inputs['Roughness'].default_value = 0.58
    return mat

# ─────────────────────────────────────────────────────────────────────────────
#  DRIFTWOOD PIECES
# ─────────────────────────────────────────────────────────────────────────────

def build_driftwood_piece(col, name, loc=(0,0,0), length=1.2, branches=2, mat=None):
    """Organic driftwood log: trunk + branches + root nub + knot bumps + bark grooves."""
    me = bpy.data.meshes.new(name + '_Mesh')
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 14
    # Main trunk vertices + edges
    for i in range(segs + 1):
        t = i / segs
        x = t * length
        y = 0.042 * math.sin(t * math.pi * 2.8)
        z = 0.030 * math.sin(t * math.pi * 2.1 + 0.6)
        bm.verts.new(Vector((x, y, z)))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        bm.edges.new([bm.verts[i], bm.verts[i + 1]])

    trunk_count = segs + 1

    # Branches
    for b in range(branches):
        split_i = int((0.35 + b * 0.28) * segs)
        base_v = bm.verts[split_i]
        br_segs = 6
        angle = rng.uniform(0.3, math.pi * 2)
        br_len = rng.uniform(0.20, 0.55)
        br_verts = []
        for j in range(br_segs + 1):
            t = j / br_segs
            bm.verts.new(Vector((
                base_v.co.x + br_len * t * math.cos(angle) * 0.7,
                base_v.co.y + br_len * t * math.sin(angle) * 0.7,
                base_v.co.z + br_len * t * 0.45)))
            br_verts.append(len(bm.verts) - 1)
        bm.verts.ensure_lookup_table()
        bm.edges.new([bm.verts[split_i], bm.verts[br_verts[0]]])
        for j in range(br_segs):
            bm.edges.new([bm.verts[br_verts[j]], bm.verts[br_verts[j + 1]]])

    # Root nub at base
    for ri in range(3):
        a = math.radians(ri * 120)
        bm.verts.new(Vector((
            rng.uniform(-0.08, -0.04),
            math.cos(a) * 0.10,
            math.sin(a) * 0.08)))
    root_start = trunk_count + branches * 7
    bm.verts.ensure_lookup_table()
    for ri in range(3):
        bm.edges.new([bm.verts[0], bm.verts[root_start + ri]])

    bm.to_mesh(me)
    bm.free()
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)

    # Skin modifier for organic volume
    skin_mod = ob.modifiers.new('Skin', 'SKIN')
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.skin_resize(value=(rng.uniform(0.050, 0.085),
                                          rng.uniform(0.050, 0.085),
                                          rng.uniform(0.050, 0.085)))
    bpy.ops.object.mode_set(mode='OBJECT')
    ob.select_set(False)
    sub = ob.modifiers.new('Sub', 'SUBSURF')
    sub.levels = 1; sub.render_levels = 2
    # Displacement for bark texture
    disp = ob.modifiers.new('BarkStriation', 'DISPLACE')
    bt = bpy.data.textures.new(f'{name}_Bark', 'DISTORTED_NOISE')
    bt.noise_scale = 0.18
    disp.texture = bt; disp.strength = 0.018; disp.direction = 'NORMAL'

    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)

    # Knot hole bumps (2 small spheres on trunk surface)
    for ki in range(2):
        t_k = 0.25 + ki * 0.35
        kx = t_k * length
        ky = 0.042 * math.sin(t_k * math.pi * 2.8)
        kz = 0.030 * math.sin(t_k * math.pi * 2.1 + 0.6)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6,
                                              radius=0.026,
                                              location=(loc[0] + kx, loc[1] + ky + 0.065, loc[2] + kz))
        knot = bpy.context.active_object
        knot.name = f"{name}_Knot_{ki}"
        knot.scale = (0.6, 0.3, 0.6)
        bpy.ops.object.transform_apply(scale=True)
        if mat:
            assign_mat(knot, mat)
        link(col, knot)

    link(col, ob)
    return ob

# ─────────────────────────────────────────────────────────────────────────────
#  DEBRIS PLANKS
# ─────────────────────────────────────────────────────────────────────────────

def bm_debris_plank(col, name, loc=(0,0,0), length=0.7, width=0.14, rot=(0,0,0), mat=None):
    """Broken plank: splintered ends, bow, nail holes, rot patches."""
    bm = bmesh.new()
    th = 0.042; segs = 10
    for i in range(segs + 1):
        t = i / segs
        x = t * length - length / 2
        z = 0.016 * math.sin(t * math.pi)  # bow
        bm.verts.new(Vector((x, -width / 2, z + th / 2)))
        bm.verts.new(Vector((x,  width / 2, z + th / 2)))
        bm.verts.new(Vector((x, -width / 2, z - th / 2)))
        bm.verts.new(Vector((x,  width / 2, z - th / 2)))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        idx = i * 4
        bm.faces.new([bm.verts[idx],     bm.verts[idx+4], bm.verts[idx+5], bm.verts[idx+1]])  # top
        bm.faces.new([bm.verts[idx+2],   bm.verts[idx+3], bm.verts[idx+7], bm.verts[idx+6]])  # bottom
        bm.faces.new([bm.verts[idx],     bm.verts[idx+2], bm.verts[idx+6], bm.verts[idx+4]])  # side A
        bm.faces.new([bm.verts[idx+1],   bm.verts[idx+5], bm.verts[idx+7], bm.verts[idx+3]])  # side B
    # Splinter jag at both ends
    for ei in range(4):
        bm.verts[ei].co.x += rng.uniform(-0.045, 0.045)
        bm.verts[ei].co.z += rng.uniform(-0.018, 0.018)
        last_ei = (segs) * 4 + ei
        if last_ei < len(bm.verts):
            bm.verts[last_ei].co.x += rng.uniform(-0.040, 0.040)
            bm.verts[last_ei].co.z += rng.uniform(-0.014, 0.014)
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc; ob.rotation_euler = rot
    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)

    # Nail holes (2-3 small cylinders inset into top face)
    for ni in range(rng.randint(2, 3)):
        nail_x = rng.uniform(-length * 0.35, length * 0.35)
        nail_y = rng.uniform(-width * 0.25, width * 0.25)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=6, radius=0.006, depth=0.048,
            location=(loc[0] + nail_x, loc[1] + nail_y, loc[2] + th / 2 - 0.005))
        nail = bpy.context.active_object
        nail.name = f"{name}_Nail_{ni}"
        mat_nail, nn, ln, bn = _base_mat(f'Mat_{name}_Nail')
        bn.inputs['Base Color'].default_value = (0.15, 0.10, 0.06, 1)
        bn.inputs['Metallic'].default_value = 0.70
        bn.inputs['Roughness'].default_value = 0.72
        assign_mat(nail, mat_nail)
        link(col, nail)

    # Rot patch (small dark flat disc on surface)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=6, radius=0.044,
        location=(loc[0] + length * 0.28, loc[1], loc[2] + th / 2 + 0.002))
    rot_patch = bpy.context.active_object
    rot_patch.name = f"{name}_RotPatch"
    rot_patch.scale = (1.0, 1.0, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    mat_rp, nrp, lrp, brp = _base_mat(f'Mat_{name}_Rot')
    brp.inputs['Base Color'].default_value = (0.04, 0.04, 0.02, 1)
    brp.inputs['Roughness'].default_value = 0.98
    assign_mat(rot_patch, mat_rp)
    link(col, rot_patch)

    return ob

# ─────────────────────────────────────────────────────────────────────────────
#  BARREL HALF
# ─────────────────────────────────────────────────────────────────────────────

def bm_barrel_half(col, name, loc=(0,0,0), mat=None, mat_iron=None):
    """Half-barrel: semi-cylinder with interior staves, 3 bands, 1 cracked stave, spill disc."""
    bm = bmesh.new()
    segs = 14; sides = 22; h = 0.72; r = 0.30
    for i in range(segs + 1):
        t = i / segs; z = t * h
        bulge = 1.0 + 0.13 * math.sin(t * math.pi)
        rv = r * bulge
        for j in range(sides + 1):
            a = (j / sides) * math.pi
            bm.verts.new(Vector((rv * math.cos(a), rv * math.sin(a), z)))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a = i * (sides + 1) + j
            b = a + 1
            c = a + (sides + 1) + 1
            d = a + (sides + 1)
            bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
    # Bottom semicircle cap
    bot = bm.verts.new(Vector((0, 0, 0)))
    for j in range(sides):
        bm.faces.new([bm.verts[j + 1], bm.verts[j], bot])
    # Cut face (flat vertical face)
    cut_bot = [bm.verts[i * (sides + 1)] for i in range(segs + 1)]
    cut_top = [bm.verts[i * (sides + 1) + sides] for i in range(segs + 1)]
    bm.faces.new(cut_bot + cut_top[::-1])
    # Interior bottom disc (visible inside)
    in_disc_verts = []
    for j in range(sides + 1):
        a = (j / sides) * math.pi
        in_disc_verts.append(bm.verts.new(Vector((r * 0.90 * math.cos(a), r * 0.90 * math.sin(a), 0.02))))
    bm.faces.new(in_disc_verts)
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc
    ob.rotation_euler = (0, 0, rng.uniform(-0.4, 0.4))
    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)

    # Iron bands (3)
    for bi, bz_off in enumerate([0.10, 0.38, 0.62]):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=r * 1.06,
            minor_radius=0.018,
            major_segments=sides + 1, minor_segments=6,
            location=(loc[0], loc[1], loc[2] + bz_off),
            rotation=(0, 0, math.pi / 2))
        band = bpy.context.active_object
        band.name = f"{name}_Band_{bi}"
        band.scale = (1.0, 0.5, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        if mat_iron:
            assign_mat(band, mat_iron)
        link(col, band)

    # Cracked stave (thin dark stripe cube)
    bpy.ops.mesh.primitive_cube_add(size=0.012, location=(loc[0] + r * 0.98, loc[1] + 0.0, loc[2] + h * 0.55))
    crack_stave = bpy.context.active_object
    crack_stave.name = f"{name}_CrackedStave"
    crack_stave.scale = (0.4, 0.4, 22.0)
    crack_stave.rotation_euler = (0, 0, math.radians(6))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    mat_cs, ncs, lcs, bcs = _base_mat(f'Mat_{name}_Crack')
    bcs.inputs['Base Color'].default_value = (0.03, 0.02, 0.01, 1)
    bcs.inputs['Roughness'].default_value = 0.98
    assign_mat(crack_stave, mat_cs); link(col, crack_stave)

    # Spill stain at base
    bpy.ops.mesh.primitive_circle_add(vertices=20, radius=r * 1.2,
                                       location=(loc[0], loc[1] + 0.06, loc[2] + 0.002), fill_type='NGON')
    stain = bpy.context.active_object
    stain.name = f"{name}_SpillStain"
    mat_st, nst, lst, bst = _base_mat(f'Mat_{name}_Stain')
    bst.inputs['Base Color'].default_value = (0.08, 0.06, 0.03, 1)
    bst.inputs['Roughness'].default_value = 0.96
    assign_mat(stain, mat_st); link(col, stain)

    return ob

# ─────────────────────────────────────────────────────────────────────────────
#  TORN SAIL
# ─────────────────────────────────────────────────────────────────────────────

def bm_torn_sail(col, name, loc=(0,0,0), w=1.5, h=0.8, mat=None):
    """Torn sail: bmesh grid, grommet holes, rope ties, painted symbol disc, Cloth modifier."""
    bm = bmesh.new()
    cols_s = 18; rows_s = 12
    for r in range(rows_s + 1):
        for c in range(cols_s + 1):
            tx = c / cols_s * w
            ty = r / rows_s * h
            z = 0.09 * math.sin(tx / w * math.pi) * math.sin(ty / h * math.pi)
            if c > cols_s * 0.60 and rng.random() < 0.32:
                z = 0
                tx += rng.uniform(-0.06, 0.06)
                ty += rng.uniform(-0.04, 0.04)
            bm.verts.new(Vector((tx - w / 2, ty - h / 2, z)))
    bm.verts.ensure_lookup_table()
    for r in range(rows_s):
        for c in range(cols_s):
            a = r * (cols_s + 1) + c
            b = a + 1
            cc = a + (cols_s + 1) + 1
            d = a + (cols_s + 1)
            bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[cc], bm.verts[d]])
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc
    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)
    # Cloth modifier (DO NOT APPLY – keep for Unity physics)
    cl = ob.modifiers.new('Cloth', 'CLOTH')
    cl.settings.quality = 5; cl.settings.mass = 0.28
    cl.settings.tension_stiffness = 15.0
    cl.settings.shear_stiffness = 5.0

    # Grommet rings along top edge (6)
    for gi in range(6):
        gx = loc[0] - w / 2 + (gi + 0.5) * (w / 6)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.020, minor_radius=0.006,
            major_segments=12, minor_segments=5,
            location=(gx, loc[1] + h / 2, loc[2]))
        grom = bpy.context.active_object
        grom.name = f"{name}_Grommet_{gi}"
        mat_gr, ng, lg, bg = _base_mat(f'Mat_{name}_Brass')
        bg.inputs['Base Color'].default_value = (0.62, 0.46, 0.12, 1)
        bg.inputs['Metallic'].default_value = 0.92
        bg.inputs['Roughness'].default_value = 0.30
        assign_mat(grom, mat_gr); link(col, grom)

    # Rope tie curves (4)
    for ri in range(4):
        gx = loc[0] - w / 2 + (ri + 0.5) * (w / 4)
        bpy.ops.curve.primitive_bezier_curve_add(location=(gx, loc[1] + h / 2, loc[2]))
        rtie = bpy.context.active_object
        rtie.name = f"{name}_RopeTie_{ri}"
        rtie.data.bevel_depth = 0.008
        rtie.data.bevel_resolution = 2
        rtie.data.dimensions = '3D'
        sp = rtie.data.splines[0]
        sp.bezier_points[0].co = Vector((0, 0, 0))
        sp.bezier_points[1].co = Vector((rng.uniform(-0.10, 0.10), 0.25 + ri * 0.05, 0.12))
        sp.bezier_points[0].handle_right = Vector((0, 0.08, 0.06))
        sp.bezier_points[1].handle_left  = Vector((0, 0.12, 0.02))
        mat_rt, nrt, lrt, brt = _base_mat(f'Mat_{name}_RopeTie')
        brt.inputs['Base Color'].default_value = (0.50, 0.38, 0.18, 1)
        brt.inputs['Roughness'].default_value = 0.88
        assign_mat(rtie, mat_rt); link(col, rtie)

    # Painted sun symbol disc (faded, on sail face)
    bpy.ops.mesh.primitive_circle_add(vertices=16, radius=0.12,
                                       location=(loc[0] - 0.15, loc[1] - 0.10, loc[2] + 0.002),
                                       fill_type='NGON')
    symbol = bpy.context.active_object
    symbol.name = f"{name}_SunSymbol"
    mat_sy, nsy, lsy, bsy = _base_mat(f'Mat_{name}_Symbol')
    bsy.inputs['Base Color'].default_value = (0.65, 0.32, 0.08, 1)
    bsy.inputs['Roughness'].default_value = 0.94
    bsy.inputs['Alpha'].default_value = 0.55
    mat_sy.blend_method = 'BLEND'
    assign_mat(symbol, mat_sy); link(col, symbol)

    return ob

# ─────────────────────────────────────────────────────────────────────────────
#  MAST FRAGMENT
# ─────────────────────────────────────────────────────────────────────────────

def bm_mast_fragment(col, name, loc=(0,0,0), length=1.5, mat=None, mat_iron=None):
    """1.5m splintered mast pole + painted stripe + rope remnant + metal band."""
    bm = bmesh.new()
    segs = 16; sides = 8
    for i in range(segs + 1):
        t = i / segs; x = t * length
        r = 0.058 * (1 - t * 0.14) * (1 + 0.06 * rng.random())
        for j in range(sides):
            a = j * 2 * math.pi / sides
            bm.verts.new(Vector((x, r * math.cos(a), r * math.sin(a))))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            c = (i + 1) * sides + (j + 1) % sides
            d = (i + 1) * sides + j
            bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
    # Jagged splinter tip
    for j in range(sides):
        idx = segs * sides + j
        bm.verts[idx].co.x += rng.uniform(-0.08, 0.08)
        bm.verts[idx].co.y += rng.uniform(-0.025, 0.025)
    # Bottom cap
    bot = bm.verts.new(Vector((0, 0, 0)))
    for j in range(sides):
        bm.faces.new([bm.verts[(j + 1) % sides], bm.verts[j], bot])
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc
    ob.rotation_euler = (0, rng.uniform(-0.28, 0.28), 0)
    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)

    # Painted stripe ring (mid-mast)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.062, minor_radius=0.008,
        major_segments=14, minor_segments=5,
        location=(loc[0] + length * 0.45, loc[1], loc[2]))
    stripe = bpy.context.active_object
    stripe.name = f"{name}_PaintStripe"
    mat_sp, nsp, lsp, bsp = _base_mat(f'Mat_{name}_Stripe')
    bsp.inputs['Base Color'].default_value = (0.65, 0.08, 0.06, 1)
    bsp.inputs['Roughness'].default_value = 0.90
    assign_mat(stripe, mat_sp); link(col, stripe)

    # Metal band
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.064, minor_radius=0.012,
        major_segments=14, minor_segments=5,
        location=(loc[0] + length * 0.20, loc[1], loc[2]))
    mband = bpy.context.active_object
    mband.name = f"{name}_MetalBand"
    if mat_iron:
        assign_mat(mband, mat_iron)
    link(col, mband)

    # Rope remnant (dangling bezier)
    bpy.ops.curve.primitive_bezier_curve_add(
        location=(loc[0] + length * 0.70, loc[1], loc[2]))
    rope_rem = bpy.context.active_object
    rope_rem.name = f"{name}_RopeRemnant"
    rope_rem.data.bevel_depth = 0.010
    rope_rem.data.bevel_resolution = 2
    rope_rem.data.dimensions = '3D'
    sp = rope_rem.data.splines[0]
    sp.bezier_points[0].co = Vector((0, 0, 0))
    sp.bezier_points[1].co = Vector((0.08, 0.12, -0.42))
    sp.bezier_points[0].handle_right = Vector((0, 0.04, -0.14))
    sp.bezier_points[1].handle_left  = Vector((0.04, 0.08, -0.22))
    mat_rp, nrp, lrp, brp = _base_mat(f'Mat_{name}_Rope')
    brp.inputs['Base Color'].default_value = (0.48, 0.36, 0.16, 1)
    brp.inputs['Roughness'].default_value = 0.88
    assign_mat(rope_rem, mat_rp); link(col, rope_rem)

    return ob

# ─────────────────────────────────────────────────────────────────────────────
#  TANGLED ROPE BALL
# ─────────────────────────────────────────────────────────────────────────────

def bm_tangled_rope(col, name, loc=(0,0,0), radius=0.30, mat=None):
    """Tangled rope ball: 8 overlapping curve loops + frayed end tufts."""
    lx, ly, lz = loc
    rope_objs = []

    # Outer main loop
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, location=loc)
    base = bpy.context.active_object
    base.name = f"{name}_Base"
    base.data.bevel_depth = 0.012
    base.data.bevel_resolution = 3
    if mat:
        assign_mat(base, mat)
    link(col, base); rope_objs.append(base)

    # Additional overlapping loops (8)
    for loop in range(8):
        lr = radius * (0.42 + loop * 0.07)
        bpy.ops.curve.primitive_bezier_circle_add(
            radius=lr,
            location=(lx + rng.uniform(-0.10, 0.10),
                       ly + rng.uniform(-0.10, 0.10),
                       lz + rng.uniform(-0.10, 0.10)))
        lp = bpy.context.active_object
        lp.name = f"{name}_Loop{loop}"
        lp.data.bevel_depth = rng.uniform(0.007, 0.012)
        lp.data.bevel_resolution = 3
        lp.rotation_euler = (rng.uniform(-1.4, 1.4),
                              rng.uniform(-1.4, 1.4),
                              rng.uniform(0, math.pi * 2))
        if mat:
            assign_mat(lp, mat)
        link(col, lp); rope_objs.append(lp)

    # Frayed fiber end tufts (4 thin short cylinders splayed)
    for fi in range(4):
        fa = math.radians(fi * 90)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=5, radius=0.005, depth=0.08,
            location=(lx + math.cos(fa) * 0.22, ly + math.sin(fa) * 0.22, lz + rng.uniform(-0.05, 0.08)),
            rotation=(rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8), fa))
        fray = bpy.context.active_object
        fray.name = f"{name}_Fray_{fi}"
        if mat:
            assign_mat(fray, mat)
        link(col, fray); rope_objs.append(fray)

    return rope_objs

# ─────────────────────────────────────────────────────────────────────────────
#  HATCH COVER
# ─────────────────────────────────────────────────────────────────────────────

def bm_hatch_cover(col, name, loc=(0,0,0), mat=None, mat_iron=None):
    """Broken ship hatch: 4×4 plank grid with perimeter frame + iron studs."""
    bm = bmesh.new()
    rows = 4; cols_h = 4; pw = 0.20; ph = 0.20; thick = 0.038
    for r in range(rows):
        for c in range(cols_h):
            x0 = c * pw - pw * cols_h / 2
            y0 = r * ph - ph * rows / 2
            x1 = x0 + pw - 0.006
            y1 = y0 + ph - 0.006
            z_var = rng.uniform(0, 0.012)
            v0 = bm.verts.new(Vector((x0, y0, thick + z_var)))
            v1 = bm.verts.new(Vector((x1, y0, thick + z_var)))
            v2 = bm.verts.new(Vector((x1, y1, thick + z_var)))
            v3 = bm.verts.new(Vector((x0, y1, thick + z_var)))
            v4 = bm.verts.new(Vector((x0, y0, 0)))
            v5 = bm.verts.new(Vector((x1, y0, 0)))
            v6 = bm.verts.new(Vector((x1, y1, 0)))
            v7 = bm.verts.new(Vector((x0, y1, 0)))
            bm.faces.new([v0, v1, v2, v3])
            bm.faces.new([v4, v7, v6, v5])
            bm.faces.new([v0, v4, v5, v1])
            bm.faces.new([v1, v5, v6, v2])
            bm.faces.new([v2, v6, v7, v3])
            bm.faces.new([v3, v7, v4, v0])
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc
    ob.rotation_euler = (0, rng.uniform(-0.25, 0.25), rng.uniform(-0.30, 0.30))
    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)

    # Perimeter frame bars
    hw = pw * cols_h / 2; hh = ph * rows / 2
    for side, sloc, sscale in [
        ('N', (loc[0],      loc[1] + hh,  loc[2] + thick), (hw * 2 + 0.04, 0.04, thick)),
        ('S', (loc[0],      loc[1] - hh,  loc[2] + thick), (hw * 2 + 0.04, 0.04, thick)),
        ('E', (loc[0] + hw, loc[1],        loc[2] + thick), (0.04, hh * 2, thick)),
        ('W', (loc[0] - hw, loc[1],        loc[2] + thick), (0.04, hh * 2, thick)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=0.04, location=sloc)
        frame = bpy.context.active_object
        frame.name = f"{name}_Frame_{side}"
        frame.scale = sscale
        bpy.ops.object.transform_apply(scale=True)
        if mat_iron:
            assign_mat(frame, mat_iron)
        link(col, frame)

    # Corner iron studs
    for rx, ry in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8, ring_count=6, radius=0.028,
            location=(loc[0] + rx, loc[1] + ry, loc[2] + thick + 0.014))
        stud = bpy.context.active_object
        stud.name = f"{name}_Stud"
        stud.scale = (1.0, 1.0, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        if mat_iron:
            assign_mat(stud, mat_iron)
        link(col, stud)

    return ob

# ─────────────────────────────────────────────────────────────────────────────
#  CANVAS BUNDLE
# ─────────────────────────────────────────────────────────────────────────────

def bm_canvas_bundle(col, name, loc=(0,0,0), mat=None, mat_rope=None):
    """Rolled wet canvas bundle with 3 rope tie bands."""
    bm = bmesh.new()
    segs = 16; sides = 14; length = 0.88; r = 0.14
    for i in range(segs + 1):
        t = i / segs; x = t * length
        r_cur = r * (1 + 0.06 * math.sin(t * math.pi * 3))
        for j in range(sides):
            a = j * 2 * math.pi / sides
            bm.verts.new(Vector((x, r_cur * math.cos(a), r_cur * math.sin(a))))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            c = (i + 1) * sides + (j + 1) % sides
            d = (i + 1) * sides + j
            bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
    # End caps
    bot = bm.verts.new(Vector((0, 0, 0)))
    for j in range(sides):
        bm.faces.new([bm.verts[(j + 1) % sides], bm.verts[j], bot])
    top = bm.verts.new(Vector((length, 0, 0)))
    for j in range(sides):
        bm.faces.new([bm.verts[segs * sides + j],
                      bm.verts[segs * sides + (j + 1) % sides], top])
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc
    ob.rotation_euler = (rng.uniform(-0.2, 0.2), rng.uniform(-0.1, 0.1), rng.uniform(0, math.pi))
    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)

    # Rope tie bands (3)
    for bi in range(3):
        bt = 0.18 + bi * 0.28
        bpy.ops.mesh.primitive_torus_add(
            major_radius=r * 1.10, minor_radius=0.014,
            major_segments=16, minor_segments=6,
            location=(loc[0] + bt * length, loc[1], loc[2]))
        band = bpy.context.active_object
        band.name = f"{name}_RopeBand_{bi}"
        if mat_rope:
            assign_mat(band, mat_rope)
        link(col, band)

    return ob

# ─────────────────────────────────────────────────────────────────────────────
#  VFX SPLASH MESH
# ─────────────────────────────────────────────────────────────────────────────

def bm_water_drop(col, name, loc=(0,0,0), r=0.048, mat=None):
    """Single teardrop water droplet."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=r)
    for v in bm.verts:
        if v.co.z > r * 0.28:
            factor = (v.co.z - r * 0.28) / (r * 0.72)
            v.co.x *= (1 - factor * 0.84)
            v.co.y *= (1 - factor * 0.84)
            v.co.z += factor * r * 0.65
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc
    if mat:
        assign_mat(ob, mat)
    return ob

def bm_splash_ring(col, name, loc=(0,0,0), ring_r=1.5, drops=18, drop_r=0.048, mat=None):
    """Outer ring of 18 drops + inner crown of 8 drops + base wave disc."""
    all_objs = []
    # Outer ring
    for i in range(drops):
        angle = i * 2 * math.pi / drops
        phase = i / drops
        x = ring_r * math.cos(angle)
        y = ring_r * math.sin(angle)
        z = 0.28 + 0.18 * math.sin(phase * math.pi)
        d = bm_water_drop(col, f"{name}_DropOut{i:02d}",
                           loc=(loc[0] + x, loc[1] + y, loc[2] + z),
                           r=drop_r * (0.68 + 0.32 * math.sin(phase * math.pi)),
                           mat=mat)
        d.rotation_euler = (angle + math.pi / 2, -0.40 * math.sin(phase * math.pi), 0)
        all_objs.append(d)
    # Inner crown (8 drops)
    for i in range(8):
        angle = i * 2 * math.pi / 8
        x = ring_r * 0.42 * math.cos(angle)
        y = ring_r * 0.42 * math.sin(angle)
        z = 0.40 + 0.08 * math.sin(i * math.pi / 4)
        d = bm_water_drop(col, f"{name}_DropIn{i:02d}",
                           loc=(loc[0] + x, loc[1] + y, loc[2] + z),
                           r=drop_r * 0.62, mat=mat)
        d.rotation_euler = (angle + math.pi / 2, -0.30, 0)
        all_objs.append(d)
    # Base wave annulus disc
    bm_base = bmesh.new()
    bsides = 36
    r_in = ring_r * 0.22; r_out = ring_r * 0.90
    for j in range(bsides):
        a = j * 2 * math.pi / bsides
        bm_base.verts.new(Vector((r_in  * math.cos(a), r_in  * math.sin(a), 0.018)))
        bm_base.verts.new(Vector((r_out * math.cos(a), r_out * math.sin(a), 0.11 + 0.042 * rng.random())))
    bm_base.verts.ensure_lookup_table()
    for j in range(bsides):
        a = j * 2; b = (j * 2 + 2) % (bsides * 2); c = b + 1; d = a + 1
        bm_base.faces.new([bm_base.verts[a], bm_base.verts[b],
                            bm_base.verts[c], bm_base.verts[d]])
    base_ob = new_mesh_obj(f"{name}_BaseDisc", bm_base, col)
    base_ob.location = loc
    if mat:
        assign_mat(base_ob, mat)
    smart_uv(base_ob)
    all_objs.append(base_ob)
    return all_objs

# ─────────────────────────────────────────────────────────────────────────────
#  VFX FOAM PATCH
# ─────────────────────────────────────────────────────────────────────────────

def bm_foam_patch(col, name, loc=(0,0,0), r=1.5, mat=None):
    """Irregular foam disc + inner bubble clusters + displacement modifier."""
    bm = bmesh.new()
    sides = 40
    for j in range(sides):
        a = j * 2 * math.pi / sides
        rv = r * (0.74 + 0.26 * rng.random())
        bm.verts.new(Vector((rv * math.cos(a), rv * math.sin(a), 0)))
    bm.verts.ensure_lookup_table()
    ctr = bm.verts.new(Vector((0, 0, 0)))
    for j in range(sides):
        bm.faces.new([bm.verts[j], bm.verts[(j + 1) % sides], ctr])
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc
    noise_tex = bpy.data.textures.new(f'{name}_FoamNoise', 'DISTORTED_NOISE')
    noise_tex.noise_scale = 0.55
    disp = ob.modifiers.new('FoamDisp', 'DISPLACE')
    disp.texture = noise_tex; disp.strength = 0.038; disp.direction = 'Z'
    sub = ob.modifiers.new('Sub', 'SUBSURF'); sub.levels = 2
    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)

    # Inner bubble clusters (6 small sphere groups)
    for bi in range(6):
        a = bi * math.pi / 3
        bx = loc[0] + r * 0.44 * math.cos(a)
        by = loc[1] + r * 0.44 * math.sin(a)
        for bj in range(rng.randint(3, 5)):
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8, ring_count=6,
                radius=rng.uniform(0.04, 0.10),
                location=(bx + rng.uniform(-0.08, 0.08),
                           by + rng.uniform(-0.08, 0.08),
                           loc[2] + rng.uniform(0.01, 0.04)))
            bubble = bpy.context.active_object
            bubble.name = f"{name}_Bubble_{bi}_{bj}"
            bubble.scale = (1.0, 1.0, rng.uniform(0.18, 0.35))
            bpy.ops.object.transform_apply(scale=True)
            if mat:
                assign_mat(bubble, mat)
            link(col, bubble)

    return ob

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

def create_weather_props():
    clear_scene()
    col = new_col("IsleTrial_WeatherProps")

    mat_drift   = build_driftwood_mat()
    mat_wood    = build_old_wood_mat()
    mat_rope    = build_rope_mat()
    mat_sail    = build_sail_mat()
    mat_canvas  = build_canvas_mat()
    mat_water   = build_water_vfx_mat()
    mat_foam    = build_foam_mat()
    mat_iron    = build_iron_mat()

    # ── DRIFTWOOD 01–05 ────────────────────────────────────────────────────
    driftwood_data = [
        ("Driftwood_01", (-8.0,  0.0, 0), 1.80, 2),
        ("Driftwood_02", (-6.0,  2.2, 0), 1.20, 1),
        ("Driftwood_03", (-4.2, -1.8, 0), 2.10, 3),
        ("Driftwood_04", (-2.2,  1.2, 0), 0.85, 2),
        ("Driftwood_05", (-0.8, -2.2, 0), 1.55, 2),
    ]
    for dname, dloc, dlen, dbr in driftwood_data:
        dw = build_driftwood_piece(col, dname, loc=dloc, length=dlen, branches=dbr, mat=mat_drift)

    # ── DEBRIS PLANKS 01–03 ────────────────────────────────────────────────
    plank_data = [
        ("Debris_Plank_01", (1.2,  0.0, 0), 0.80, 0.14, (0, 0,  0.30)),
        ("Debris_Plank_02", (2.4, -0.8, 0), 0.55, 0.13, (0, 0, -0.52)),
        ("Debris_Plank_03", (3.2,  0.6, 0), 0.65, 0.15, (0, 0,  0.82)),
    ]
    for pname, ploc, plen, pw, prot in plank_data:
        bm_debris_plank(col, pname, loc=ploc, length=plen, width=pw, rot=prot, mat=mat_wood)

    # Short stave fragments
    for si in range(2):
        bm_debris_plank(col, f"Debris_Plank_Short_{si+1}",
                        loc=(4.2 + si * 0.8, rng.uniform(-0.6, 0.6), 0),
                        length=0.32, width=0.10,
                        rot=(0, 0, rng.uniform(-1.2, 1.2)),
                        mat=mat_wood)

    # ── BARREL HALF ────────────────────────────────────────────────────────
    bm_barrel_half(col, "Debris_Barrel_Half", loc=(6.0, 0, 0),
                   mat=mat_wood, mat_iron=mat_iron)

    # ── TANGLED ROPE BALL ──────────────────────────────────────────────────
    bm_tangled_rope(col, "Debris_Rope_Tangled", loc=(8.2, 0, 0.30),
                    radius=0.30, mat=mat_rope)

    # ── TORN SAIL ──────────────────────────────────────────────────────────
    bm_torn_sail(col, "Debris_Sail_Torn", loc=(10.2, 0, 0.06), w=1.5, h=0.8, mat=mat_sail)

    # ── MAST FRAGMENT ──────────────────────────────────────────────────────
    bm_mast_fragment(col, "Debris_Mast_Fragment", loc=(12.2, 0, 0),
                     length=1.5, mat=mat_wood, mat_iron=mat_iron)

    # ── HATCH COVER ────────────────────────────────────────────────────────
    bm_hatch_cover(col, "Debris_Hatch_Cover", loc=(14.5, 0, 0),
                   mat=mat_wood, mat_iron=mat_iron)

    # ── CANVAS BUNDLE ──────────────────────────────────────────────────────
    bm_canvas_bundle(col, "Debris_Canvas_Bundle", loc=(16.5, 0, 0.14),
                     mat=mat_canvas, mat_rope=mat_rope)

    # ── VFX SPLASH MESH ────────────────────────────────────────────────────
    splash_objs = bm_splash_ring(col, "VFX_Splash_Mesh", loc=(0, 6.5, 0),
                                  ring_r=1.5, drops=18, drop_r=0.048, mat=mat_water)
    for so in splash_objs:
        if so.type == 'MESH':
            smart_uv(so)

    # ── VFX FOAM PATCH ─────────────────────────────────────────────────────
    bm_foam_patch(col, "VFX_FoamPatch", loc=(5.5, 6.5, 0), r=1.5, mat=mat_foam)

    print("\n[IsleTrial] WeatherProps – Build Complete.")
    print("  Collection: IsleTrial_WeatherProps")
    print()
    print("  Props created:")
    print("    Driftwood_01…05        → Beach/shore scatter debris")
    print("    Debris_Plank_01…03     → Broken planks w/ splinters + nail holes + rot")
    print("    Debris_Plank_Short_01/02 → Small stave fragments")
    print("    Debris_Barrel_Half     → Half barrel + bands + cracked stave + spill stain")
    print("    Debris_Rope_Tangled    → 8-loop tangled rope + frayed ends")
    print("    Debris_Sail_Torn       → Cloth sail + grommets + rope ties + sun symbol")
    print("    Debris_Mast_Fragment   → Splintered mast + stripe + rope remnant + band")
    print("    Debris_Hatch_Cover     → 4×4 plank hatch + iron frame + studs")
    print("    Debris_Canvas_Bundle   → Rolled canvas + 3 rope tie bands")
    print("    VFX_Splash_Mesh        → 18-drop outer ring + 8-drop crown + base disc")
    print("    VFX_FoamPatch          → Irregular foam disc + bubble clusters")
    print()
    print("  Unity notes:")
    print("    Debris_Sail_Torn: Keep Cloth modifier unapplied → assign Unity Cloth component")
    print("    VFX_Splash_Mesh + VFX_FoamPatch → Use as ParticleSystem shape references")
    print("    All driftwood pieces → Float physics with Rigidbody + Buoyancy script")
    print("    [UNITY] image slots → Assign PBR maps (Albedo / Normal / Roughness)")

create_weather_props()
