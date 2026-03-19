"""
IsleTrial — Bird Skeleton NPC  (Model)
Blender 4.x  •  Python Script

Creates the Bird Skeleton enemy.  Height ≈ 1.10 m, T-pose.

Mesh objects
────────────────────────────────────────────────────────
  Skull / Beak / EyeGlow_L / EyeGlow_R
  Neck_Vertebra_0-2
  Spine_Vertebra_0-3  /  Sternum  /  Pelvis
  Rib_L/R_0-5  (3 segments each)
  ShoulderBlade_L/R
  WingUpper/Lower/Finger_L/R  (bone-shaped cylinders)
  WingMembrane_L/R  (torn cloth plane)
  Femur / KneeJoint / Tibia / AnkleJoint / Tarsometatarsus  ×2
  Toe_Main/Inner/Outer/Back  + Claw_*  ×2 sides

Materials  (dual-path: procedural preview + [UNITY] image slots)
────────────────────────────────────────────────────────
  Mat_Bone_Ivory      – warm ivory, subtle noise cracks, SSS
  Mat_Bone_Aged       – darker extremity bone
  Mat_EyeGlow_Purple  – emissive purple glow
  Mat_TornCloth       – dark maroon, woven + noise wear

Run 06_BirdSkeleton_Rig.py AFTER this script.
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

# ──────────────────────────────────────────────
#  MESH HELPERS
# ──────────────────────────────────────────────

def bone_cyl(name, p1, p2, radius=0.025):
    """Oriented cylinder from p1 to p2 — simulates a bone shaft."""
    p1v, p2v = Vector(p1), Vector(p2)
    length = (p2v - p1v).length
    if length < 0.001:
        length = 0.001
    mid = (p1v + p2v) / 2.0

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=length, location=mid)
    obj = bpy.context.active_object
    obj.name = name

    z = Vector((0, 0, 1))
    direction = (p2v - p1v).normalized()
    dot = z.dot(direction)
    if abs(dot) < 0.9999:
        q = z.rotation_difference(direction)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = q
    elif dot < 0:
        obj.rotation_euler = (math.pi, 0, 0)
    return obj

def joint_sphere(name, loc, radius=0.030):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=radius, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def uv_unwrap(obj):
    activate(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

# ──────────────────────────────────────────────
#  MATERIAL NODES HELPERS
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

def _coord_map(nodes, links, scale=(8, 8, 8), loc=(-1000, 0)):
    tc = _n(nodes, 'ShaderNodeTexCoord', (loc[0],       loc[1]))
    mp = _n(nodes, 'ShaderNodeMapping',  (loc[0] + 200, loc[1]))
    mp.inputs['Scale'].default_value = scale
    links.new(tc.outputs['UV'], mp.inputs['Vector'])
    return mp

# ──────────────────────────────────────────────
#  MATERIALS
# ──────────────────────────────────────────────

def build_bone_mat(name, base=(0.88, 0.82, 0.66), roughness=0.70, aged=False):
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
    try:
        bsdf.inputs['Subsurface Weight'].default_value = 0.06
    except KeyError:
        pass

    mp = _coord_map(N, L, scale=(10, 10, 10), loc=(-1000, 100))

    # Noise for age stains
    noise = _n(N, 'ShaderNodeTexNoise', (-700, 200))
    noise.inputs['Scale'].default_value      = 14.0
    noise.inputs['Detail'].default_value     = 8.0
    noise.inputs['Roughness'].default_value  = 0.65
    noise.inputs['Distortion'].default_value = 0.3
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    # Voronoi cracks
    vor = _n(N, 'ShaderNodeTexVoronoi', (-700, -80))
    vor.inputs['Scale'].default_value = 20.0
    vor.feature = 'DISTANCE_TO_EDGE'
    L.new(mp.outputs['Vector'], vor.inputs['Vector'])

    dark = tuple(max(0.0, c * (0.55 if aged else 0.70)) for c in base)
    cr_col = _n(N, 'ShaderNodeValToRGB', (-400, 200))
    cr_col.color_ramp.elements[0].color = (*dark, 1.0)
    cr_col.color_ramp.elements[1].color = (*base, 1.0)
    L.new(noise.outputs['Fac'], cr_col.inputs['Fac'])

    # Roughness variation
    cr_rgh = _n(N, 'ShaderNodeValToRGB', (-400, -80))
    lo = max(0.0, roughness - 0.12)
    hi = min(1.0, roughness + 0.18)
    cr_rgh.color_ramp.elements[0].color = (lo, lo, lo, 1.0)
    cr_rgh.color_ramp.elements[1].color = (hi, hi, hi, 1.0)
    L.new(noise.outputs['Fac'], cr_rgh.inputs['Fac'])
    L.new(cr_rgh.outputs['Color'], bsdf.inputs['Roughness'])

    # Bump from voronoi cracks
    bump = _n(N, 'ShaderNodeBump', (-100, -200))
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.008
    mul = _n(N, 'ShaderNodeMixRGB', (-380, -250))
    mul.blend_type = 'MULTIPLY'
    mul.inputs['Fac'].default_value = 0.5
    L.new(vor.outputs['Distance'],  mul.inputs['Color1'])
    L.new(noise.outputs['Fac'],     mul.inputs['Color2'])
    L.new(mul.outputs['Color'],     bump.inputs['Height'])
    L.new(bump.outputs['Normal'],   bsdf.inputs['Normal'])

    # Unity image slot + blend
    img = _img(N, f'[UNITY] {name}_Albedo', (-700, -320))
    mix = _n(N, 'ShaderNodeMixRGB', (-150, 200), 'Mix_Albedo')
    mix.inputs['Fac'].default_value = 0.0
    L.new(cr_col.outputs['Color'],  mix.inputs['Color1'])
    L.new(img.outputs['Color'],     mix.inputs['Color2'])
    L.new(mix.outputs['Color'],     bsdf.inputs['Base Color'])

    return mat


def build_emissive_mat(name, color=(0.45, 0.0, 0.85), strength=5.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (300, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (0, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value            = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value             = 0.1
    bsdf.inputs['Metallic'].default_value              = 0.0
    try:
        bsdf.inputs['Emission Color'].default_value    = (*color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = strength
    except KeyError:
        pass
    return mat


def build_cloth_mat(name, base=(0.18, 0.04, 0.22)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()

    out  = _n(N, 'ShaderNodeOutputMaterial', (500, 0))
    bsdf = _n(N, 'ShaderNodeBsdfPrincipled',  (100, 0))
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = 0.93
    bsdf.inputs['Metallic'].default_value  = 0.0

    mp = _coord_map(N, L, scale=(16, 16, 16), loc=(-1000, 0))

    wave = _n(N, 'ShaderNodeTexWave', (-700, 100))
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'DIAGONAL'
    wave.inputs['Scale'].default_value      = 22.0
    wave.inputs['Distortion'].default_value = 3.8
    L.new(mp.outputs['Vector'], wave.inputs['Vector'])

    noise = _n(N, 'ShaderNodeTexNoise', (-700, -120))
    noise.inputs['Scale'].default_value     = 7.0
    noise.inputs['Detail'].default_value    = 5.0
    L.new(mp.outputs['Vector'], noise.inputs['Vector'])

    dark = tuple(max(0.0, c * 0.45) for c in base)
    cr = _n(N, 'ShaderNodeValToRGB', (-420, -120))
    cr.color_ramp.elements[0].color = (*dark, 1.0)
    cr.color_ramp.elements[1].color = (*base, 1.0)
    L.new(noise.outputs['Fac'], cr.inputs['Fac'])

    cr_w = _n(N, 'ShaderNodeValToRGB', (-420, 100))
    cr_w.color_ramp.elements[0].color = (0.55, 0.55, 0.55, 1.0)
    cr_w.color_ramp.elements[1].color = (1.0,  1.0,  1.0,  1.0)
    L.new(wave.outputs['Color'], cr_w.inputs['Fac'])

    mix_col = _n(N, 'ShaderNodeMixRGB', (-160, 0))
    mix_col.blend_type = 'MULTIPLY'
    mix_col.inputs['Fac'].default_value = 0.35
    L.new(cr.outputs['Color'],   mix_col.inputs['Color1'])
    L.new(cr_w.outputs['Color'], mix_col.inputs['Color2'])

    bump = _n(N, 'ShaderNodeBump', (-100, -200))
    bump.inputs['Strength'].default_value = 0.30
    bump.inputs['Distance'].default_value = 0.005
    L.new(noise.outputs['Fac'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    img = _img(N, f'[UNITY] {name}_Albedo', (-700, -340))
    mix_u = _n(N, 'ShaderNodeMixRGB', (50, 0), 'Mix_Unity')
    mix_u.inputs['Fac'].default_value = 0.0
    L.new(mix_col.outputs['Color'], mix_u.inputs['Color1'])
    L.new(img.outputs['Color'],     mix_u.inputs['Color2'])
    L.new(mix_u.outputs['Color'],   bsdf.inputs['Base Color'])
    return mat

# ──────────────────────────────────────────────
#  SKULL + BEAK
# ──────────────────────────────────────────────

def build_skull(mats):
    objs = []

    # Cranium
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.135, location=(0, 0.025, 0.960))
    skull = bpy.context.active_object
    skull.name = 'BirdSkull'
    skull.scale = (0.98, 1.22, 1.05)
    bpy.ops.object.transform_apply(scale=True)

    # Flatten skull bottom, shape forward jut
    activate(skull)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(skull.data)
    for v in bm.verts:
        if v.co.z < 0.895:
            v.co.z = 0.895
        if v.co.y < -0.04:
            v.co.y *= 1.35
    bmesh.update_edit_mesh(skull.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    mod = skull.modifiers.new('Sub', 'SUBSURF')
    mod.levels = 2
    assign_mat(skull, mats['bone'])
    objs.append(skull)

    # Beak (tapered 4-sided cone, flattened)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.052, radius2=0.004,
                                    depth=0.28, location=(0, -0.24, 0.940))
    beak = bpy.context.active_object
    beak.name = 'BirdBeak'
    beak.rotation_euler = (math.radians(11), 0, 0)
    beak.scale = (0.58, 1.0, 0.32)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bk_bev = beak.modifiers.new('Bevel', 'BEVEL')
    bk_bev.width = 0.004; bk_bev.segments = 2
    assign_mat(beak, mats['bone_aged'])
    objs.append(beak)

    # Lower beak jaw
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.038, radius2=0.003,
                                    depth=0.22, location=(0, -0.20, 0.928))
    jaw = bpy.context.active_object
    jaw.name = 'BirdJaw'
    jaw.rotation_euler = (math.radians(18), 0, 0)
    jaw.scale = (0.52, 1.0, 0.24)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    assign_mat(jaw, mats['bone_aged'])
    objs.append(jaw)

    # Eye sockets
    for sx, side in ((-0.088, 'L'), (0.088, 'R')):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8,
                                             radius=0.052, location=(sx, -0.028, 0.968))
        sock = bpy.context.active_object
        sock.name = f'EyeSocket_{side}'
        sock.scale = (1.0, 0.62, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(sock, mats['bone_aged'])
        objs.append(sock)

    # Glowing eye orbs
    for sx, side in ((-0.088, 'L'), (0.088, 'R')):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8,
                                             radius=0.044, location=(sx, -0.040, 0.968))
        eye = bpy.context.active_object
        eye.name = f'EyeGlow_{side}'
        eye.scale = (0.88, 0.58, 0.88)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(eye, mats['eye_glow'])
        objs.append(eye)

    return objs

# ──────────────────────────────────────────────
#  NECK
# ──────────────────────────────────────────────

def build_neck(mats):
    objs = []
    verts = [(0, 0.005, 0.820), (0, 0.002, 0.870), (0, -0.004, 0.910)]
    for i, pos in enumerate(verts):
        j = joint_sphere(f'Neck_Vertebra_{i}', pos, 0.026)
        j.scale = (1.0, 1.18, 0.62)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(j, mats['bone'])
        objs.append(j)
        if i < len(verts) - 1:
            sh = bone_cyl(f'Neck_Shaft_{i}', pos, verts[i + 1], radius=0.013)
            assign_mat(sh, mats['bone'])
            objs.append(sh)
    return objs

# ──────────────────────────────────────────────
#  RIBCAGE + SPINE + PELVIS
# ──────────────────────────────────────────────

def build_ribcage(mats):
    objs = []

    # Spine vertebrae
    spine_z = [0.525, 0.590, 0.655, 0.720, 0.785]
    for i in range(len(spine_z) - 1):
        mid_z = (spine_z[i] + spine_z[i + 1]) / 2
        j = joint_sphere(f'Spine_Vert_{i}', (0, 0, mid_z), 0.026)
        j.scale = (1.0, 1.15, 0.65)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(j, mats['bone'])
        objs.append(j)

    # Sternum (keel)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.020,
                                        depth=0.22, location=(0, -0.092, 0.660))
    st = bpy.context.active_object
    st.name = 'Sternum'
    assign_mat(st, mats['bone'])
    objs.append(st)

    # Ribs — (width, z) pairs
    rib_layout = [
        (0.60, 0.840), (0.64, 0.780), (0.66, 0.720),
        (0.64, 0.668), (0.56, 0.625), (0.44, 0.590),
    ]
    for ri, (w, z) in enumerate(rib_layout):
        for side, sx in (('L', -1), ('R', 1)):
            p0 = (sx * 0.030,  0.015, z)
            p1 = (sx * w * 0.50,  sx * 0.045, z - 0.018)
            p2 = (sx * w * 0.46, -0.048, z - 0.050)
            p3 = (sx * 0.040, -0.088, z - 0.075)
            pts = [p0, p1, p2, p3]
            for si in range(len(pts) - 1):
                r = max(0.005, 0.014 - si * 0.002)
                seg = bone_cyl(f'Rib_{side}_{ri}_{si}', pts[si], pts[si + 1], radius=r)
                assign_mat(seg, mats['bone'])
                objs.append(seg)

    # Shoulder blades
    for sx, side in ((-1, 'L'), (1, 'R')):
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.048, radius2=0.010,
                                        depth=0.115, location=(sx * 0.115, 0.062, 0.792))
        blade = bpy.context.active_object
        blade.name = f'ShoulderBlade_{side}'
        blade.scale = (1.0, 0.38, 1.0)
        blade.rotation_euler = (math.radians(-14), 0, math.radians(sx * -24))
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(blade, mats['bone'])
        objs.append(blade)

    # Pelvis
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8,
                                         radius=0.076, location=(0, 0, 0.520))
    pelv = bpy.context.active_object
    pelv.name = 'Pelvis'
    pelv.scale = (1.42, 0.88, 0.68)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(pelv, mats['bone'])
    objs.append(pelv)

    return objs

# ──────────────────────────────────────────────
#  WINGS
# ──────────────────────────────────────────────

def build_wings(mats):
    objs = []

    for side, sx in (('L', -1), ('R', 1)):
        # Shoulder joint
        sj = joint_sphere(f'WingShoulder_{side}', (sx * 0.115, 0, 0.780), 0.036)
        assign_mat(sj, mats['bone'])
        objs.append(sj)

        p_sho = (sx * 0.115,  0.000, 0.780)
        p_elb = (sx * 0.400, -0.020, 0.772)
        p_wri = (sx * 0.660, -0.010, 0.752)

        upper = bone_cyl(f'WingUpper_{side}', p_sho, p_elb, radius=0.022)
        assign_mat(upper, mats['bone'])
        objs.append(upper)

        ej = joint_sphere(f'WingElbow_{side}', p_elb, 0.027)
        assign_mat(ej, mats['bone'])
        objs.append(ej)

        lower = bone_cyl(f'WingLower_{side}', p_elb, p_wri, radius=0.016)
        assign_mat(lower, mats['bone'])
        objs.append(lower)

        wj = joint_sphere(f'WingWrist_{side}', p_wri, 0.022)
        assign_mat(wj, mats['bone'])
        objs.append(wj)

        # 3 wing finger bones fanning outward
        tips = [
            (sx * 0.900, -0.018, 0.725),
            (sx * 0.862, -0.015, 0.648),
            (sx * 0.795, -0.008, 0.575),
        ]
        for fi, tip in enumerate(tips):
            f = bone_cyl(f'WingFinger_{side}_{fi}', p_wri, tip, radius=0.009)
            assign_mat(f, mats['bone_aged'])
            objs.append(f)

        # Wing membrane — subdivided plane for deformation
        cx = sx * ((p_sho[0] + tips[-1][0]) / 2.0)
        cz = (p_sho[2] + tips[-1][2]) / 2.0
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(cx, -0.012, cz))
        mem = bpy.context.active_object
        mem.name = f'WingMembrane_{side}'
        mem.scale = (abs(cx - p_sho[0]) * 1.1, 0.28, (p_sho[2] - tips[-1][2]) * 1.8 + 0.15)
        bpy.ops.object.transform_apply(scale=True)

        activate(mem)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.subdivide(number_cuts=6)
        bpy.ops.object.mode_set(mode='OBJECT')

        sol = mem.modifiers.new('Solidify', 'SOLIDIFY')
        sol.thickness = 0.004
        assign_mat(mem, mats['cloth'])
        objs.append(mem)

    return objs

# ──────────────────────────────────────────────
#  LEGS + TALONS
# ──────────────────────────────────────────────

def build_legs(mats):
    objs = []

    for side, sx in (('L', -1), ('R', 1)):
        p_hip   = (sx * 0.072,  0.010, 0.500)
        p_knee  = (sx * 0.082,  0.028, 0.340)
        p_ankle = (sx * 0.070, -0.014, 0.165)
        p_tbase = (sx * 0.068,  0.005, 0.042)

        fem = bone_cyl(f'Femur_{side}', p_hip, p_knee, radius=0.025)
        assign_mat(fem, mats['bone']); objs.append(fem)

        kj = joint_sphere(f'KneeJoint_{side}', p_knee, 0.028)
        assign_mat(kj, mats['bone']); objs.append(kj)

        tib = bone_cyl(f'Tibia_{side}', p_knee, p_ankle, radius=0.018)
        assign_mat(tib, mats['bone']); objs.append(tib)

        aj = joint_sphere(f'AnkleJoint_{side}', p_ankle, 0.024)
        assign_mat(aj, mats['bone']); objs.append(aj)

        tmt = bone_cyl(f'Tarsometatarsus_{side}', p_ankle, p_tbase, radius=0.013)
        assign_mat(tmt, mats['bone_aged']); objs.append(tmt)

        talon_offsets = {
            'Main':  ( sx * 0.004, -0.112, -0.034),
            'Inner': ( sx * 0.058, -0.092, -0.032),
            'Outer': (-sx * 0.048, -0.094, -0.030),
            'Back':  ( sx * 0.003,  0.075, -0.018),
        }
        for tname, toff in talon_offsets.items():
            p_tip = (p_tbase[0] + toff[0], p_tbase[1] + toff[1], p_tbase[2] + toff[2])
            toe = bone_cyl(f'Toe_{tname}_{side}', p_tbase, p_tip, radius=0.008)
            assign_mat(toe, mats['bone_aged']); objs.append(toe)

            # Claw
            cv = Vector(p_tip) + Vector(toff) * 0.38 + Vector((0, 0, -0.016))
            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.008, radius2=0.001,
                                            depth=0.050, location=cv)
            claw = bpy.context.active_object
            claw.name = f'Claw_{tname}_{side}'
            dv = (cv - Vector(p_tip)).normalized()
            if dv.length > 0.001:
                q = Vector((0, 0, -1)).rotation_difference(dv)
                claw.rotation_mode = 'QUATERNION'
                claw.rotation_quaternion = q
            assign_mat(claw, mats['bone_aged']); objs.append(claw)

    return objs

# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    setup_scene()

    mats = {
        'bone'      : build_bone_mat('Mat_Bone_Ivory',  base=(0.90, 0.84, 0.68), roughness=0.68),
        'bone_aged' : build_bone_mat('Mat_Bone_Aged',   base=(0.72, 0.62, 0.46), roughness=0.80, aged=True),
        'eye_glow'  : build_emissive_mat('Mat_EyeGlow_Purple', color=(0.42, 0.0, 0.88), strength=5.5),
        'cloth'     : build_cloth_mat('Mat_TornCloth',  base=(0.18, 0.04, 0.22)),
    }

    all_objs = []
    all_objs.extend(build_skull(mats))
    all_objs.extend(build_neck(mats))
    all_objs.extend(build_ribcage(mats))
    all_objs.extend(build_wings(mats))
    all_objs.extend(build_legs(mats))

    print(f"[BirdSkeleton] UV unwrapping {len(all_objs)} objects...")
    for obj in all_objs:
        if obj.type == 'MESH':
            uv_unwrap(obj)

    col  = new_col('IsleTrial_BirdSkeleton')
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = 'BirdSkeleton_ROOT'
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

    print("\n" + "="*60)
    print("  IsleTrial — Bird Skeleton Model Complete")
    print("="*60)
    print(f"  Objects    : {len(all_objs)}")
    print("  Materials  : 4  (procedural + [UNITY] image slots)")
    print("  Collection : IsleTrial_BirdSkeleton")
    print("  Next step  : Run 06_BirdSkeleton_Rig.py")
    print("="*60 + "\n")


main()
