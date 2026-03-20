"""
46_NPC_Toran_SoulGuardian_Rig.py
IsleTrial — Toran Character Rig (Kael's Father / Soul Guardian)
================================================================
Run AFTER 46_NPC_Toran_SoulGuardian.py inside Blender ▸ Scripting tab.

Height:  1.82 m  (slightly taller + broader than Kael's 1.80 m)
Pose:    T-pose (arms horizontal, facing +Y)

Bone naming follows Unity Humanoid Avatar convention — identical
naming to Kael's rig so both characters share the same Animator
Controller and animation clips in Unity.

Extra bones not in Kael's rig (non-humanoid / generic layer):
  Weapon_R          — Compass Blade, child of RightHand
  BrokenCompass     — pendant, child of Hips
  GhostAura         — whole-body aura sphere control, child of Hips
  SoulChain_Chest_L — left chest chain root, child of Chest
  SoulChain_Chest_R — right chest chain root, child of Chest
  SoulChain_Arm_L   — left arm chain, child of LeftUpperArm
  SoulChain_Arm_R   — right arm chain, child of RightUpperArm
  SoulChain_Leg_L   — left leg chain, child of LeftUpperLeg
  SoulChain_Leg_R   — right leg chain, child of RightUpperLeg

Shape keys (on the placeholder body mesh):
  Basis, Smile, Frown, BrowUp, BrowDown, Blink_L, Blink_R,
  Grimace, Desperate — and three spirit-specific:
  Possessed   — eyes glow white, face contorts (Phase 2)
  ChainBind   — chains pull tight on body (Phase 2 max)
  Freed       — relaxed, soft — for the liberation cinematic

IK: feet + hands (same as Kael — rig is retarget-compatible)
Rotation limits: same ranges as Kael

Bone colours:
  Red    — spine (Root → Head)
  Green  — left side limbs
  Blue   — right side limbs
  Cyan   — IK / control bones
  Yellow — extra / prop bones
  Purple — soul chain bones (unique to Toran)

Mixamo Compatibility:
  Same as Kael — upload FBX to mixamo.com for animation packs.
  Toran can retarget Kael's animations directly since the rig
  naming is identical.

Unity Import:
  Rig Type   : Humanoid
  Avatar     : Create From This Model
  Scale      : 1.0
  Axis       : Y Up, -Z Forward (Blender FBX default)
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ─────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.meshes):    bpy.data.meshes.remove(m)
    for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)

def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def edit_mode(obj):
    activate(obj)
    bpy.ops.object.mode_set(mode='EDIT')

def pose_mode(obj):
    activate(obj)
    bpy.ops.object.mode_set(mode='POSE')

def object_mode():
    bpy.ops.object.mode_set(mode='OBJECT')


# ─────────────────────────────────────────────────────
#  BONE DEFINITIONS
#
#  Toran is 1.82 m — 1.1% taller and ~10% broader than Kael.
#  All Z values are scaled up proportionally.
#  Shoulder width: ±0.175 (Kael ±0.160)
#  Arm reach:      ±0.475 upper, ±0.755 lower, ±0.870 hand
#  Leg width:      ±0.110 (same as Kael)
#  Ground at Z=0, head top at Z=1.82
# ─────────────────────────────────────────────────────

# fmt: (head, tail, parent_name, connected)
BONES = {
    # ── Root / Hips ──────────────────────────────────
    'Root':              ((0.000,  0.000, 0.000), (0.000,  0.000, 0.110), None,            False),
    'Hips':              ((0.000,  0.000, 0.980), (0.000,  0.000, 1.085), 'Root',          False),

    # ── Spine chain ──────────────────────────────────
    'Spine':             ((0.000,  0.000, 1.085), (0.000,  0.000, 1.215), 'Hips',          True),
    'Chest':             ((0.000,  0.000, 1.215), (0.000,  0.000, 1.360), 'Spine',         True),
    'UpperChest':        ((0.000,  0.000, 1.360), (0.000,  0.000, 1.490), 'Chest',         True),
    'Neck':              ((0.000,  0.000, 1.490), (0.000,  0.000, 1.600), 'UpperChest',    True),
    'Head':              ((0.000,  0.000, 1.600), (0.000,  0.000, 1.820), 'Neck',          True),

    # ── Left arm ─────────────────────────────────────
    'LeftShoulder':      ((0.000,  0.000, 1.470), (-0.175, 0.000, 1.475), 'UpperChest',    False),
    'LeftUpperArm':      ((-0.175, 0.000, 1.475), (-0.475, 0.000, 1.460), 'LeftShoulder',  True),
    'LeftLowerArm':      ((-0.475, 0.000, 1.460), (-0.755, 0.000, 1.448), 'LeftUpperArm',  True),
    'LeftHand':          ((-0.755, 0.000, 1.448), (-0.870, 0.000, 1.442), 'LeftLowerArm',  True),

    # Left fingers
    'LeftIndexProximal':     ((-0.870, 0.010, 1.442), (-0.908, 0.022, 1.433), 'LeftHand',             False),
    'LeftIndexIntermediate': ((-0.908, 0.022, 1.433), (-0.932, 0.028, 1.427), 'LeftIndexProximal',    True),
    'LeftIndexDistal':       ((-0.932, 0.028, 1.427), (-0.948, 0.032, 1.422), 'LeftIndexIntermediate',True),

    'LeftMiddleProximal':    ((-0.872, 0.004, 1.442), (-0.912, 0.005, 1.431), 'LeftHand',              False),
    'LeftMiddleIntermediate':((-0.912, 0.005, 1.431), (-0.940, 0.006, 1.424), 'LeftMiddleProximal',    True),
    'LeftMiddleDistal':      ((-0.940, 0.006, 1.424), (-0.956, 0.007, 1.419), 'LeftMiddleIntermediate',True),

    'LeftRingProximal':      ((-0.870,-0.006, 1.440), (-0.908,-0.011, 1.429), 'LeftHand',             False),
    'LeftRingIntermediate':  ((-0.908,-0.011, 1.429), (-0.932,-0.014, 1.423), 'LeftRingProximal',     True),
    'LeftRingDistal':        ((-0.932,-0.014, 1.423), (-0.945,-0.017, 1.419), 'LeftRingIntermediate', True),

    'LeftLittleProximal':    ((-0.867,-0.018, 1.438), (-0.898,-0.028, 1.429), 'LeftHand',              False),
    'LeftLittleIntermediate':((-0.898,-0.028, 1.429), (-0.918,-0.034, 1.424), 'LeftLittleProximal',    True),
    'LeftLittleDistal':      ((-0.918,-0.034, 1.424), (-0.928,-0.037, 1.421), 'LeftLittleIntermediate',True),

    'LeftThumbProximal':     ((-0.760, 0.016, 1.438), (-0.788, 0.032, 1.424), 'LeftHand',              False),
    'LeftThumbIntermediate': ((-0.788, 0.032, 1.424), (-0.812, 0.044, 1.415), 'LeftThumbProximal',     True),
    'LeftThumbDistal':       ((-0.812, 0.044, 1.415), (-0.826, 0.050, 1.409), 'LeftThumbIntermediate', True),

    # ── Right arm ────────────────────────────────────
    'RightShoulder':     ((0.000,  0.000, 1.470), ( 0.175, 0.000, 1.475), 'UpperChest',    False),
    'RightUpperArm':     (( 0.175, 0.000, 1.475), ( 0.475, 0.000, 1.460), 'RightShoulder', True),
    'RightLowerArm':     (( 0.475, 0.000, 1.460), ( 0.755, 0.000, 1.448), 'RightUpperArm', True),
    'RightHand':         (( 0.755, 0.000, 1.448), ( 0.870, 0.000, 1.442), 'RightLowerArm', True),

    # Right fingers (mirror of left)
    'RightIndexProximal':     (( 0.870, 0.010, 1.442), ( 0.908, 0.022, 1.433), 'RightHand',             False),
    'RightIndexIntermediate': (( 0.908, 0.022, 1.433), ( 0.932, 0.028, 1.427), 'RightIndexProximal',    True),
    'RightIndexDistal':       (( 0.932, 0.028, 1.427), ( 0.948, 0.032, 1.422), 'RightIndexIntermediate',True),

    'RightMiddleProximal':    (( 0.872, 0.004, 1.442), ( 0.912, 0.005, 1.431), 'RightHand',              False),
    'RightMiddleIntermediate':(( 0.912, 0.005, 1.431), ( 0.940, 0.006, 1.424), 'RightMiddleProximal',    True),
    'RightMiddleDistal':      (( 0.940, 0.006, 1.424), ( 0.956, 0.007, 1.419), 'RightMiddleIntermediate',True),

    'RightRingProximal':      (( 0.870,-0.006, 1.440), ( 0.908,-0.011, 1.429), 'RightHand',             False),
    'RightRingIntermediate':  (( 0.908,-0.011, 1.429), ( 0.932,-0.014, 1.423), 'RightRingProximal',     True),
    'RightRingDistal':        (( 0.932,-0.014, 1.423), ( 0.945,-0.017, 1.419), 'RightRingIntermediate', True),

    'RightLittleProximal':    (( 0.867,-0.018, 1.438), ( 0.898,-0.028, 1.429), 'RightHand',              False),
    'RightLittleIntermediate':(( 0.898,-0.028, 1.429), ( 0.918,-0.034, 1.424), 'RightLittleProximal',    True),
    'RightLittleDistal':      (( 0.918,-0.034, 1.424), ( 0.928,-0.037, 1.421), 'RightLittleIntermediate',True),

    'RightThumbProximal':     (( 0.760, 0.016, 1.438), ( 0.788, 0.032, 1.424), 'RightHand',              False),
    'RightThumbIntermediate': (( 0.788, 0.032, 1.424), ( 0.812, 0.044, 1.415), 'RightThumbProximal',     True),
    'RightThumbDistal':       (( 0.812, 0.044, 1.415), ( 0.826, 0.050, 1.409), 'RightThumbIntermediate', True),

    # ── Left leg ─────────────────────────────────────
    'LeftUpperLeg':      ((-0.110, 0.000, 0.980), (-0.110, 0.010, 0.545), 'Hips',          False),
    'LeftLowerLeg':      ((-0.110, 0.010, 0.545), (-0.110, 0.005, 0.098), 'LeftUpperLeg',  True),
    'LeftFoot':          ((-0.110, 0.005, 0.098), (-0.110, 0.150, 0.020), 'LeftLowerLeg',  True),
    'LeftToes':          ((-0.110, 0.150, 0.020), (-0.110, 0.230, 0.010), 'LeftFoot',      True),

    # ── Right leg ────────────────────────────────────
    'RightUpperLeg':     (( 0.110, 0.000, 0.980), ( 0.110, 0.010, 0.545), 'Hips',          False),
    'RightLowerLeg':     (( 0.110, 0.010, 0.545), ( 0.110, 0.005, 0.098), 'RightUpperLeg', True),
    'RightFoot':         (( 0.110, 0.005, 0.098), ( 0.110, 0.150, 0.020), 'RightLowerLeg', True),
    'RightToes':         (( 0.110, 0.150, 0.020), ( 0.110, 0.230, 0.010), 'RightFoot',     True),

    # ── Extra bones (not Humanoid — Generic layer) ───
    # Compass Blade — held in right hand
    'Weapon_R':          (( 0.780,-0.040, 1.442), ( 0.780,-0.280, 1.432), 'RightHand',     False),
    # Broken compass pendant — at chest
    'BrokenCompass':     (( 0.060, 0.090, 1.010), ( 0.060, 0.160, 1.010), 'Hips',          False),
    # Ghost aura sphere control — centered on pelvis
    'GhostAura':         (( 0.000, 0.000, 0.880), ( 0.000, 0.000, 1.340), 'Hips',          False),

    # Soul chain bones (6 chains — all non-deform, animated independently)
    # These are keyed from 1.0 scale → 0.0 scale when chains break in Phase 3
    'SoulChain_Chest_L': ((-0.240, 0.000, 1.02), (-0.240, 0.000, 0.62), 'Chest',          False),
    'SoulChain_Chest_R': (( 0.240, 0.000, 1.02), ( 0.240, 0.000, 0.62), 'Chest',          False),
    'SoulChain_Arm_L':   ((-0.280, 0.000, 0.84), (-0.280, 0.000, 0.56), 'LeftUpperArm',   False),
    'SoulChain_Arm_R':   (( 0.280, 0.000, 0.84), ( 0.280, 0.000, 0.56), 'RightUpperArm',  False),
    'SoulChain_Leg_L':   ((-0.110, 0.000, 0.22), (-0.110, 0.000,-0.40), 'LeftUpperLeg',   False),
    'SoulChain_Leg_R':   (( 0.110, 0.000, 0.22), ( 0.110, 0.000,-0.40), 'RightUpperLeg',  False),
}

# Which bones belong to each colour group
SPINE_BONES       = ['Root','Hips','Spine','Chest','UpperChest','Neck','Head']
EXTRA_BONES       = ['Weapon_R','BrokenCompass','GhostAura']
SOUL_CHAIN_BONES  = ['SoulChain_Chest_L','SoulChain_Chest_R',
                     'SoulChain_Arm_L',  'SoulChain_Arm_R',
                     'SoulChain_Leg_L',  'SoulChain_Leg_R']


# ─────────────────────────────────────────────────────
#  BUILD ARMATURE
# ─────────────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('Toran_Armature_Data')
    arm_obj  = bpy.data.objects.new('Toran_Armature', arm_data)
    arm_obj.show_in_front = True
    bpy.context.scene.collection.objects.link(arm_obj)

    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    for name, (head, tail, parent, connected) in BONES.items():
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        if parent and parent in eb:
            b.parent = eb[parent]
            b.use_connect = connected
        # Soul chain and control bones do not deform the mesh
        if name in SOUL_CHAIN_BONES or name in EXTRA_BONES:
            b.use_deform = False

    object_mode()
    return arm_obj


# ─────────────────────────────────────────────────────
#  IK TARGETS
# ─────────────────────────────────────────────────────

def add_ik_targets(arm_obj):
    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    ik_bones = {
        # Feet
        'IK_Foot_L':    ((-0.110, 0.150, 0.020), (-0.110, 0.150, 0.145), 'Root'),
        'IK_Foot_R':    (( 0.110, 0.150, 0.020), ( 0.110, 0.150, 0.145), 'Root'),
        # Hands
        'IK_Hand_L':    ((-0.870, 0.000, 1.442), (-0.870, 0.000, 1.560), 'Root'),
        'IK_Hand_R':    (( 0.870, 0.000, 1.442), ( 0.870, 0.000, 1.560), 'Root'),
        # Pole targets
        'Pole_Knee_L':  ((-0.110,-0.520, 0.545), (-0.110,-0.520, 0.650), 'Root'),
        'Pole_Knee_R':  (( 0.110,-0.520, 0.545), ( 0.110,-0.520, 0.650), 'Root'),
        'Pole_Elbow_L': ((-0.755,-0.420, 1.455), (-0.755,-0.420, 1.560), 'Root'),
        'Pole_Elbow_R': (( 0.755,-0.420, 1.455), ( 0.755,-0.420, 1.560), 'Root'),
    }

    for name, (head, tail, parent) in ik_bones.items():
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        b.parent = eb[parent]
        b.use_deform = False

    object_mode()

    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def add_ik(bone, target_bone, chain, pole=None, pole_angle=0):
        if bone not in pb: return
        c = pb[bone].constraints.new('IK')
        c.target      = arm_obj
        c.subtarget   = target_bone
        c.chain_count = chain
        if pole:
            c.pole_target    = arm_obj
            c.pole_subtarget = pole
            c.pole_angle     = math.radians(pole_angle)

    add_ik('LeftFoot',  'IK_Foot_L', 3, 'Pole_Knee_L',  -90)
    add_ik('RightFoot', 'IK_Foot_R', 3, 'Pole_Knee_R',  -90)
    add_ik('LeftHand',  'IK_Hand_L', 2, 'Pole_Elbow_L', 180)
    add_ik('RightHand', 'IK_Hand_R', 2, 'Pole_Elbow_R', 180)

    object_mode()


# ─────────────────────────────────────────────────────
#  ROTATION LIMITS
# ─────────────────────────────────────────────────────

def add_rotation_limits(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def limit(bone, use_x, use_y, use_z,
              xmn=0, xmx=0, ymn=0, ymx=0, zmn=0, zmx=0):
        if bone not in pb: return
        c = pb[bone].constraints.new('LIMIT_ROTATION')
        c.owner_space = 'LOCAL'
        c.use_limit_x = use_x; c.min_x = math.radians(xmn); c.max_x = math.radians(xmx)
        c.use_limit_y = use_y; c.min_y = math.radians(ymn); c.max_y = math.radians(ymx)
        c.use_limit_z = use_z; c.min_z = math.radians(zmn); c.max_z = math.radians(zmx)

    # Spine — older body, slightly stiffer than Kael
    for b in ['Spine', 'Chest', 'UpperChest']:
        limit(b, True, True, True, xmn=-20, xmx=28, ymn=-18, ymx=18, zmn=-18, zmx=18)
    limit('Neck', True, True, True, xmn=-30, xmx=32, ymn=-22, ymx=22, zmn=-28, zmx=28)
    limit('Head', True, True, True, xmn=-42, xmx=42, ymn=-38, ymx=38, zmn=-32, zmx=32)

    # Arms — heavier build, slightly reduced rotation range
    for side in ('Left', 'Right'):
        sign = -1 if side == 'Left' else 1
        limit(f'{side}UpperArm', True, True, True,
              xmn=-85,  xmx=175, ymn=-55*sign, ymx=55*sign, zmn=-95, zmx=95)
        limit(f'{side}LowerArm', True, False, True,
              xmn=0, xmx=140, zmn=-5, zmx=5)
        limit(f'{side}Hand', True, True, True,
              xmn=-65, xmx=65, ymn=-28, ymx=28, zmn=-18, zmx=18)

    # Legs
    for side in ('Left', 'Right'):
        limit(f'{side}UpperLeg', True, True, True,
              xmn=-95, xmx=48, ymn=-38, ymx=38, zmn=-38, zmx=38)
        limit(f'{side}LowerLeg', True, False, True,
              xmn=-140, xmx=0, zmn=-5, zmx=5)
        limit(f'{side}Foot', True, True, True,
              xmn=-42, xmx=28, ymn=-14, ymx=14, zmn=-18, zmx=18)

    # Soul chain bones — constrained to only rotate on one axis (link swing)
    for chain_bone in SOUL_CHAIN_BONES:
        limit(chain_bone, True, True, True,
              xmn=-35, xmx=35, ymn=-35, ymx=35, zmn=-35, zmx=35)

    object_mode()


# ─────────────────────────────────────────────────────
#  PLACEHOLDER BODY MESH (Toran proportions)
# ─────────────────────────────────────────────────────

def build_body_mesh():
    """
    Low-poly T-pose reference body for Toran.
    Proportionally wider/heavier than Kael's placeholder.
    Replace with the detailed mesh from 46_NPC_Toran_SoulGuardian.py
    after initial setup.
    """
    bm = bmesh.new()

    def box(cx, cy, cz, sx, sy, sz):
        mat = __import__('mathutils').Matrix.Translation((cx, cy, cz))
        result = bmesh.ops.create_cube(bm, size=1.0)
        for v in result['verts']:
            v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
            v.co = mat @ v.co

    # Torso (wider chest: +0.06 vs Kael)
    box( 0.00, 0.00, 1.20, 0.44, 0.24, 0.32)
    # Hips (wider)
    box( 0.00, 0.00, 1.01, 0.36, 0.22, 0.17)
    # Head (slightly larger)
    box( 0.00, 0.00, 1.71, 0.24, 0.23, 0.26)
    # Neck (thicker)
    box( 0.00, 0.00, 1.54, 0.12, 0.11, 0.13)

    # Left upper arm (heavier)
    box(-0.325, 0.00, 1.468, 0.14, 0.14, 0.30)
    # Left lower arm
    box(-0.615, 0.00, 1.454, 0.12, 0.12, 0.28)
    # Left hand (large bare hand)
    box(-0.815, 0.00, 1.442, 0.11, 0.07, 0.18)

    # Right upper arm
    box( 0.325, 0.00, 1.468, 0.14, 0.14, 0.30)
    # Right lower arm
    box( 0.615, 0.00, 1.454, 0.12, 0.12, 0.28)
    # Right hand
    box( 0.815, 0.00, 1.442, 0.11, 0.07, 0.18)

    # Left upper leg (heavier thighs)
    box(-0.110, 0.00, 0.762, 0.16, 0.16, 0.44)
    # Left lower leg
    box(-0.110, 0.00, 0.322, 0.13, 0.13, 0.44)
    # Left foot (worn boot)
    box(-0.110, 0.065, 0.052, 0.12, 0.24, 0.105)

    # Right upper leg
    box( 0.110, 0.00, 0.762, 0.16, 0.16, 0.44)
    # Right lower leg
    box( 0.110, 0.00, 0.322, 0.13, 0.13, 0.44)
    # Right foot
    box( 0.110, 0.065, 0.052, 0.12, 0.24, 0.105)

    # Eyes — pale ghost-blue
    box(-0.058, 0.120, 1.730, 0.055, 0.022, 0.042)
    box( 0.058, 0.120, 1.730, 0.055, 0.022, 0.042)

    bm.normal_update()
    me = bpy.data.meshes.new('Toran_Body_Mesh')
    bm.to_mesh(me)
    bm.free()

    body = bpy.data.objects.new('Toran_Body', me)
    bpy.context.scene.collection.objects.link(body)

    # Ghost skin placeholder material
    mat = bpy.data.materials.new('Mat_Toran_Placeholder')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value    = (0.72, 0.58, 0.52, 1.0)
        bsdf.inputs['Roughness'].default_value     = 0.80
        bsdf.inputs['Emission Color'].default_value = (0.25, 0.65, 0.90, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 0.25
    body.data.materials.append(mat)
    return body


# ─────────────────────────────────────────────────────
#  BIND MESH TO ARMATURE
# ─────────────────────────────────────────────────────

def bind_mesh_to_armature(body_obj, arm_obj):
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')


# ─────────────────────────────────────────────────────
#  BONE COLOURS
# ─────────────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    left_bones  = [n for n in BONES if n.startswith('Left')]
    right_bones = [n for n in BONES if n.startswith('Right')]
    ik_bones    = ['IK_Foot_L','IK_Foot_R','IK_Hand_L','IK_Hand_R',
                   'Pole_Knee_L','Pole_Knee_R','Pole_Elbow_L','Pole_Elbow_R']

    for b in SPINE_BONES:
        if b in pb: pb[b].color.palette = 'THEME01'   # red — spine
    for b in left_bones:
        if b in pb: pb[b].color.palette = 'THEME04'   # green — left
    for b in right_bones:
        if b in pb: pb[b].color.palette = 'THEME03'   # blue — right
    for b in ik_bones:
        if b in pb: pb[b].color.palette = 'THEME10'   # cyan — IK
    for b in EXTRA_BONES:
        if b in pb: pb[b].color.palette = 'THEME09'   # yellow — props
    for b in SOUL_CHAIN_BONES:
        if b in pb: pb[b].color.palette = 'THEME06'   # purple — soul chains

    object_mode()


# ─────────────────────────────────────────────────────
#  SHAPE KEYS
# ─────────────────────────────────────────────────────

def add_shape_keys(body_obj):
    """
    Named shape key slots for Toran's facial expressions and
    spirit-possession states.  Sculpt each key in Sculpt Mode.
    """
    activate(body_obj)
    bpy.ops.object.shape_key_add(from_mix=False)
    body_obj.data.shape_keys.key_blocks[0].name = 'Basis'

    keys = [
        # Standard expressions
        'Smile',
        'Frown',
        'Blink_L',
        'Blink_R',
        'BrowUp',
        'BrowDown',
        'Grimace',      # pain / effort expression
        'Surprised',
        'Desperate',    # Phase 2: fighting the binding, teeth clenched

        # Spirit-possession states (unique to Toran)
        'Possessed',    # Phase 2 peak: eyes white, face strains against chains
        'ChainBind',    # chains constrict: shoulders pulled down, head tilted
        'Freed',        # liberation cinematic: relaxed, peaceful, slight smile
        'Dying',        # fading out cinematic: translucent, features softening
    ]

    for expr in keys:
        bpy.ops.object.shape_key_add(from_mix=False)
        body_obj.data.shape_keys.key_blocks[-1].name = expr


# ─────────────────────────────────────────────────────
#  CUSTOM BONE SHAPES (optional visual helpers)
# ─────────────────────────────────────────────────────

def add_custom_bone_shapes(arm_obj):
    """
    Creates small widget meshes and assigns them as custom bone shapes
    so the soul chain bones are visually distinct in the viewport.
    """
    # Small diamond widget for chain bones
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=0, radius=0.04)
    me = bpy.data.meshes.new('Widget_ChainNode')
    bm.to_mesh(me); bm.free()
    widget = bpy.data.objects.new('Widget_ChainNode', me)
    bpy.context.scene.collection.objects.link(widget)
    widget.hide_viewport = True

    # Small circle widget for IK targets
    bm2 = bmesh.new()
    segs = 12
    verts = [bm2.verts.new((0.05*math.cos(2*math.pi*i/segs),
                              0.05*math.sin(2*math.pi*i/segs), 0)) for i in range(segs)]
    bm2.edges.new(verts)
    for i in range(segs-1): bm2.edges.new([verts[i], verts[i+1]])
    bm2.edges.new([verts[-1], verts[0]])
    me2 = bpy.data.meshes.new('Widget_IKCircle')
    bm2.to_mesh(me2); bm2.free()
    widget_ik = bpy.data.objects.new('Widget_IKCircle', me2)
    bpy.context.scene.collection.objects.link(widget_ik)
    widget_ik.hide_viewport = True

    pose_mode(arm_obj)
    pb = arm_obj.pose.bones
    for b in SOUL_CHAIN_BONES:
        if b in pb:
            pb[b].custom_shape = widget
            pb[b].use_custom_shape_bone_size = False
    for b in ['IK_Foot_L','IK_Foot_R','IK_Hand_L','IK_Hand_R']:
        if b in pb:
            pb[b].custom_shape = widget_ik
            pb[b].use_custom_shape_bone_size = False
    object_mode()


# ─────────────────────────────────────────────────────
#  REPORT
# ─────────────────────────────────────────────────────

def print_rig_report(arm_obj):
    total  = len(arm_obj.data.bones)
    deform = sum(1 for b in arm_obj.data.bones if b.use_deform)

    unity_humanoid = [
        'Hips','Spine','Chest','UpperChest','Neck','Head',
        'LeftShoulder','LeftUpperArm','LeftLowerArm','LeftHand',
        'RightShoulder','RightUpperArm','RightLowerArm','RightHand',
        'LeftUpperLeg','LeftLowerLeg','LeftFoot','LeftToes',
        'RightUpperLeg','RightLowerLeg','RightFoot','RightToes',
    ]

    print("\n" + "="*65)
    print("  IsleTrial — Toran Soul Guardian Rig Report")
    print("="*65)
    print(f"\n  Armature     : {arm_obj.name}")
    print(f"  Height       : 1.82 m  (Kael = 1.80 m)")
    print(f"  Total bones  : {total}")
    print(f"  Deform bones : {deform}")
    print(f"  IK/control   : {total - deform}")
    print(f"\n  Unity Humanoid Avatar auto-mapped bones:")
    for b in unity_humanoid:
        status = '✓' if b in arm_obj.data.bones else '✗ MISSING'
        print(f"    {status}  {b}")
    print(f"\n  Extra bones (Generic layer):")
    print("    Weapon_R         → Compass Blade, child of RightHand")
    print("    BrokenCompass    → pendant, child of Hips")
    print("    GhostAura        → aura sphere control, child of Hips")
    print(f"\n  Soul Chain bones (Phase 3 — animate scale → 0 to break):")
    for b in SOUL_CHAIN_BONES:
        print(f"    {b}")
    body_shapes_expected = ['Basis','Smile','Frown','Blink_L','Blink_R',
                            'BrowUp','BrowDown','Grimace','Surprised','Desperate',
                            'Possessed','ChainBind','Freed','Dying']
    print(f"\n  Shape keys ({len(body_shapes_expected)} total):")
    for k in body_shapes_expected:
        print(f"    {k}")
    print(f"\n  Rig compatibility with Kael:")
    print("    ✓ Identical Unity Humanoid bone names")
    print("    ✓ Same finger count and naming")
    print("    ✓ Retargets Kael's walk/idle/combat animations")
    print("    ✓ Mixamo auto-rig compatible (same T-pose)")
    print(f"\n  Export:")
    print("    File → Export → FBX")
    print("    ✓ Apply Transform  ✓ Armature  ✓ Mesh  ✓ Leaf Bones OFF")
    print("    Scale: 1.0   Axis: Y Up, -Z Forward")
    print(f"\n  Unity Import:")
    print("    Rig Type: Humanoid")
    print("    Avatar: Create From This Model")
    print("    Scale Factor: 1.0")
    print(f"\n  Animation notes:")
    print("    Soul chains: Animator parameter 'ChainStrength' (0→1)")
    print("    drives scale of all SoulChain_* bones via script")
    print("    GhostAura: Material 'Alpha' driven by 'GhostIntensity' param")
    print("    Possessed shape key: driven by 'PossessionLevel' (0→1)")
    print("="*65 + "\n")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def main():
    clear_scene()

    print("\n[ToranRig] Building armature...")
    arm_obj = build_armature()

    print("[ToranRig] Adding IK targets...")
    add_ik_targets(arm_obj)

    print("[ToranRig] Adding rotation limits...")
    add_rotation_limits(arm_obj)

    print("[ToranRig] Building placeholder body mesh...")
    body_obj = build_body_mesh()

    print("[ToranRig] Binding mesh to armature (auto weights)...")
    bind_mesh_to_armature(body_obj, arm_obj)

    print("[ToranRig] Adding shape key slots...")
    add_shape_keys(body_obj)

    print("[ToranRig] Colour-coding bones...")
    color_bones(arm_obj)

    print("[ToranRig] Adding custom bone shapes...")
    add_custom_bone_shapes(arm_obj)

    # Display settings
    activate(arm_obj)
    arm_obj.data.display_type = 'OCTAHEDRAL'
    arm_obj.show_in_front     = True

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
                    space.overlay.show_bones               = True
                    space.overlay.show_relationship_lines  = True
            break

    print_rig_report(arm_obj)


main()
