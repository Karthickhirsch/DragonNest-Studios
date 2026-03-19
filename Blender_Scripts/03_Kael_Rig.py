"""
IsleTrial — Kael Character Rig
Blender 4.x Python Script

Creates a complete game-ready humanoid armature for Kael at 1.8m height.
Also creates a low-poly T-pose body mesh as the base for modelling.

Bone naming follows Unity Humanoid Avatar convention — Unity will
auto-map all bones with no manual reassignment needed.

Mixamo Compatibility
──────────────────────────────────────────────────────────────────
Option A (recommended): Upload the exported FBX to Mixamo.com →
  Mixamo auto-rigs it with its own bones + provides animations.
  Import back into Unity → set Rig to Humanoid → Unity maps Mixamo
  bones automatically.

Option B: Use this rig directly and download Mixamo animations
  separately (.fbx without skin), then retarget in Unity Animator.

Unity Import Settings
──────────────────────────────────────────────────────────────────
  Rig Type     : Humanoid
  Avatar       : Create From This Model
  Scale Factor : 1.0  (model is authored at real-world metres)
  Axis:          Y Up, -Z Forward (Blender default FBX export)
  Animations   : see Kael_Spec.md animation list

Bone Hierarchy
──────────────────────────────────────────────────────────────────
  Root (motion bone)
  └─ Hips
      ├─ Spine → Chest → UpperChest → Neck → Head
      ├─ LeftShoulder → LeftUpperArm → LeftLowerArm → LeftHand
      │     └─ LeftIndexProximal (3 fingers + thumb included)
      ├─ RightShoulder → RightUpperArm → RightLowerArm → RightHand
      ├─ LeftUpperLeg → LeftLowerLeg → LeftFoot → LeftToes
      └─ RightUpperLeg → RightLowerLeg → RightFoot → RightToes

  Extra bones (not in Humanoid Avatar, handled as Generic):
      Weapon_R  — cutlass bone, child of RightHand
      Compass   — compass glow bone, child of Hips
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
    for m in list(bpy.data.meshes):      bpy.data.meshes.remove(m)
    for a in list(bpy.data.armatures):   bpy.data.armatures.remove(a)


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
#  BONE DEFINITIONS  (head_xyz, tail_xyz)
#
#  Coordinate system: Blender default (Z up, Y forward)
#  Character faces +Y, arms along ±X in T-pose
#  Ground at Z = 0, top of head at Z ≈ 1.80
# ─────────────────────────────────────────────────────

# fmt: (head, tail, parent_name, connected)
BONES = {
    # ── Root / Hips ──────────────────────────────────
    'Root':             ((0.000,  0.000, 0.000), (0.000,  0.000, 0.100), None,           False),
    'Hips':             ((0.000,  0.000, 0.950), (0.000,  0.000, 1.050), 'Root',         False),

    # ── Spine chain ──────────────────────────────────
    'Spine':            ((0.000,  0.000, 1.050), (0.000,  0.000, 1.175), 'Hips',         True),
    'Chest':            ((0.000,  0.000, 1.175), (0.000,  0.000, 1.310), 'Spine',        True),
    'UpperChest':       ((0.000,  0.000, 1.310), (0.000,  0.000, 1.430), 'Chest',        True),
    'Neck':             ((0.000,  0.000, 1.430), (0.000,  0.000, 1.535), 'UpperChest',   True),
    'Head':             ((0.000,  0.000, 1.535), (0.000,  0.000, 1.780), 'Neck',         True),

    # ── Left arm ─────────────────────────────────────
    'LeftShoulder':     ((0.000,  0.000, 1.410), (-0.160, 0.000, 1.415), 'UpperChest',   False),
    'LeftUpperArm':     ((-0.160, 0.000, 1.415), (-0.440, 0.000, 1.405), 'LeftShoulder', True),
    'LeftLowerArm':     ((-0.440, 0.000, 1.405), (-0.700, 0.000, 1.395), 'LeftUpperArm', True),
    'LeftHand':         ((-0.700, 0.000, 1.395), (-0.810, 0.000, 1.390), 'LeftLowerArm', True),

    # Left fingers (index — minimal setup)
    'LeftIndexProximal':    ((-0.810, 0.010, 1.390), (-0.845, 0.020, 1.382), 'LeftHand', False),
    'LeftIndexIntermediate':((-0.845, 0.020, 1.382), (-0.868, 0.025, 1.376), 'LeftIndexProximal', True),
    'LeftIndexDistal':      ((-0.868, 0.025, 1.376), (-0.882, 0.028, 1.372), 'LeftIndexIntermediate', True),

    # Left middle finger
    'LeftMiddleProximal':   ((-0.812, 0.004, 1.390), (-0.850, 0.005, 1.380), 'LeftHand', False),
    'LeftMiddleIntermediate':((-0.850, 0.005, 1.380), (-0.876, 0.006, 1.373), 'LeftMiddleProximal', True),
    'LeftMiddleDistal':     ((-0.876, 0.006, 1.373), (-0.891, 0.007, 1.369), 'LeftMiddleIntermediate', True),

    # Left ring finger
    'LeftRingProximal':     ((-0.810, -0.006, 1.388), (-0.845, -0.010, 1.378), 'LeftHand', False),
    'LeftRingIntermediate': ((-0.845, -0.010, 1.378), (-0.868, -0.013, 1.372), 'LeftRingProximal', True),
    'LeftRingDistal':       ((-0.868, -0.013, 1.372), (-0.880, -0.015, 1.368), 'LeftRingIntermediate', True),

    # Left little finger
    'LeftLittleProximal':   ((-0.807, -0.016, 1.386), (-0.836, -0.025, 1.378), 'LeftHand', False),
    'LeftLittleIntermediate':((-0.836, -0.025, 1.378), (-0.854, -0.030, 1.373), 'LeftLittleProximal', True),
    'LeftLittleDistal':     ((-0.854, -0.030, 1.373), (-0.863, -0.033, 1.370), 'LeftLittleIntermediate', True),

    # Left thumb
    'LeftThumbProximal':    ((-0.705, 0.015, 1.385), (-0.730, 0.030, 1.372), 'LeftHand', False),
    'LeftThumbIntermediate':((-0.730, 0.030, 1.372), (-0.752, 0.040, 1.363), 'LeftThumbProximal', True),
    'LeftThumbDistal':      ((-0.752, 0.040, 1.363), (-0.765, 0.046, 1.357), 'LeftThumbIntermediate', True),

    # ── Right arm ────────────────────────────────────
    'RightShoulder':    ((0.000,  0.000, 1.410), (0.160,  0.000, 1.415), 'UpperChest',    False),
    'RightUpperArm':    ((0.160,  0.000, 1.415), (0.440,  0.000, 1.405), 'RightShoulder', True),
    'RightLowerArm':    ((0.440,  0.000, 1.405), (0.700,  0.000, 1.395), 'RightUpperArm', True),
    'RightHand':        ((0.700,  0.000, 1.395), (0.810,  0.000, 1.390), 'RightLowerArm', True),

    # Right fingers (mirror of left)
    'RightIndexProximal':    ((0.810, 0.010, 1.390), (0.845, 0.020, 1.382), 'RightHand', False),
    'RightIndexIntermediate':((0.845, 0.020, 1.382), (0.868, 0.025, 1.376), 'RightIndexProximal', True),
    'RightIndexDistal':      ((0.868, 0.025, 1.376), (0.882, 0.028, 1.372), 'RightIndexIntermediate', True),

    'RightMiddleProximal':   ((0.812, 0.004, 1.390), (0.850, 0.005, 1.380), 'RightHand', False),
    'RightMiddleIntermediate':((0.850, 0.005, 1.380), (0.876, 0.006, 1.373), 'RightMiddleProximal', True),
    'RightMiddleDistal':     ((0.876, 0.006, 1.373), (0.891, 0.007, 1.369), 'RightMiddleIntermediate', True),

    'RightRingProximal':     ((0.810, -0.006, 1.388), (0.845, -0.010, 1.378), 'RightHand', False),
    'RightRingIntermediate': ((0.845, -0.010, 1.378), (0.868, -0.013, 1.372), 'RightRingProximal', True),
    'RightRingDistal':       ((0.868, -0.013, 1.372), (0.880, -0.015, 1.368), 'RightRingIntermediate', True),

    'RightLittleProximal':   ((0.807, -0.016, 1.386), (0.836, -0.025, 1.378), 'RightHand', False),
    'RightLittleIntermediate':((0.836,-0.025, 1.378), (0.854, -0.030, 1.373), 'RightLittleProximal', True),
    'RightLittleDistal':     ((0.854, -0.030, 1.373),(0.863, -0.033, 1.370), 'RightLittleIntermediate', True),

    'RightThumbProximal':    ((0.705, 0.015, 1.385), (0.730, 0.030, 1.372), 'RightHand', False),
    'RightThumbIntermediate':((0.730, 0.030, 1.372), (0.752, 0.040, 1.363), 'RightThumbProximal', True),
    'RightThumbDistal':      ((0.752, 0.040, 1.363), (0.765, 0.046, 1.357), 'RightThumbIntermediate', True),

    # ── Left leg ─────────────────────────────────────
    'LeftUpperLeg':     ((-0.100, 0.000, 0.950), (-0.100, 0.010, 0.530), 'Hips',          False),
    'LeftLowerLeg':     ((-0.100, 0.010, 0.530), (-0.100, 0.005, 0.095), 'LeftUpperLeg',  True),
    'LeftFoot':         ((-0.100, 0.005, 0.095), (-0.100, 0.145, 0.020), 'LeftLowerLeg',  True),
    'LeftToes':         ((-0.100, 0.145, 0.020), (-0.100, 0.220, 0.010), 'LeftFoot',      True),

    # ── Right leg ────────────────────────────────────
    'RightUpperLeg':    ((0.100,  0.000, 0.950), (0.100,  0.010, 0.530), 'Hips',           False),
    'RightLowerLeg':    ((0.100,  0.010, 0.530), (0.100,  0.005, 0.095), 'RightUpperLeg',  True),
    'RightFoot':        ((0.100,  0.005, 0.095), (0.100,  0.145, 0.020), 'RightLowerLeg',  True),
    'RightToes':        ((0.100,  0.145, 0.020), (0.100,  0.220, 0.010), 'RightFoot',      True),

    # ── Extra (non-Humanoid) ─────────────────────────
    # Cutlass sheath → RightHand (weapon bone)
    'Weapon_R':         ((0.720, -0.040, 1.390), (0.720, -0.260, 1.380), 'RightHand',      False),
    # Compass at hip
    'Compass':          ((0.060,  0.080, 0.970), (0.060,  0.140, 0.970), 'Hips',           False),
}


# ─────────────────────────────────────────────────────
#  BUILD ARMATURE
# ─────────────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('Kael_Armature_Data')
    arm_obj  = bpy.data.objects.new('Kael_Armature', arm_data)
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

    object_mode()
    return arm_obj


# ─────────────────────────────────────────────────────
#  IK CONSTRAINTS  (feet + hands for animation)
# ─────────────────────────────────────────────────────

def add_ik_targets(arm_obj):
    """
    Add IK target empties for feet and hands.
    These are the bones animators key for walk cycles etc.
    """
    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    ik_bones = {
        'IK_Foot_L':  ((-0.100, 0.145, 0.020), (-0.100, 0.145, 0.140), 'Root'),
        'IK_Foot_R':  (( 0.100, 0.145, 0.020), ( 0.100, 0.145, 0.140), 'Root'),
        'IK_Hand_L':  ((-0.810, 0.000, 1.390), (-0.810, 0.000, 1.500), 'Root'),
        'IK_Hand_R':  (( 0.810, 0.000, 1.390), ( 0.810, 0.000, 1.500), 'Root'),
        # Pole targets (hint for knee/elbow bend direction)
        'Pole_Knee_L':((-0.100, -0.500, 0.530), (-0.100, -0.500, 0.630), 'Root'),
        'Pole_Knee_R':(( 0.100, -0.500, 0.530), ( 0.100, -0.500, 0.630), 'Root'),
        'Pole_Elbow_L':((-0.700, -0.400, 1.400), (-0.700,-0.400, 1.500), 'Root'),
        'Pole_Elbow_R':(( 0.700, -0.400, 1.400), ( 0.700,-0.400, 1.500), 'Root'),
    }
    for name, (head, tail, parent) in ik_bones.items():
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        b.parent = eb[parent]
        b.use_deform = False   # IK targets don't deform mesh

    object_mode()

    # Add IK constraints in pose mode
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def add_ik(bone, target_bone, chain, pole=None, pole_angle=0):
        if bone not in pb:
            return
        c = pb[bone].constraints.new('IK')
        c.target     = arm_obj
        c.subtarget  = target_bone
        c.chain_count = chain
        if pole:
            c.pole_target   = arm_obj
            c.pole_subtarget = pole
            c.pole_angle    = math.radians(pole_angle)

    add_ik('LeftFoot',  'IK_Foot_L', 3, 'Pole_Knee_L',  -90)
    add_ik('RightFoot', 'IK_Foot_R', 3, 'Pole_Knee_R',  -90)
    add_ik('LeftHand',  'IK_Hand_L', 2, 'Pole_Elbow_L', 180)
    add_ik('RightHand', 'IK_Hand_R', 2, 'Pole_Elbow_R', 180)

    object_mode()


# ─────────────────────────────────────────────────────
#  ROTATION LIMITS (prevent unrealistic bends)
# ─────────────────────────────────────────────────────

def add_rotation_limits(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def limit(bone, use_x, use_y, use_z,
              xmn=0, xmx=0, ymn=0, ymx=0, zmn=0, zmx=0):
        if bone not in pb:
            return
        c = pb[bone].constraints.new('LIMIT_ROTATION')
        c.owner_space = 'LOCAL'
        c.use_limit_x = use_x; c.min_x = math.radians(xmn); c.max_x = math.radians(xmx)
        c.use_limit_y = use_y; c.min_y = math.radians(ymn); c.max_y = math.radians(ymx)
        c.use_limit_z = use_z; c.min_z = math.radians(zmn); c.max_z = math.radians(zmx)

    # Spine — limit hyperextension
    for b in ['Spine', 'Chest', 'UpperChest']:
        limit(b, True, True, True, xmn=-25, xmx=30, ymn=-20, ymx=20, zmn=-20, zmx=20)
    limit('Neck', True, True, True, xmn=-35, xmx=35, ymn=-25, ymx=25, zmn=-30, zmx=30)
    limit('Head', True, True, True, xmn=-45, xmx=45, ymn=-40, ymx=40, zmn=-35, zmx=35)

    # Arms
    for side in ('Left', 'Right'):
        sign = -1 if side == 'Left' else 1
        limit(f'{side}UpperArm', True, True, True,
              xmn=-90,  xmx=180,
              ymn=-60*sign, ymx=60*sign,
              zmn=-100, zmx=100)
        limit(f'{side}LowerArm', True, False, True,
              xmn=0,   xmx=145,   # elbow only bends forward
              zmn=-5,  zmx=5)
        limit(f'{side}Hand', True, True, True,
              xmn=-70, xmx=70,
              ymn=-30, ymx=30,
              zmn=-20, zmx=20)

    # Legs
    for side in ('Left', 'Right'):
        limit(f'{side}UpperLeg', True, True, True,
              xmn=-100, xmx=50,
              ymn=-40,  ymx=40,
              zmn=-40,  zmx=40)
        limit(f'{side}LowerLeg', True, False, True,
              xmn=-145, xmx=0,    # knee bends back only
              zmn=-5,   zmx=5)
        limit(f'{side}Foot', True, True, True,
              xmn=-45, xmx=30,
              ymn=-15, ymx=15,
              zmn=-20, zmx=20)

    object_mode()


# ─────────────────────────────────────────────────────
#  LOW-POLY BODY MESH (T-Pose placeholder)
# ─────────────────────────────────────────────────────

def build_body_mesh():
    """
    Creates a simple low-poly humanoid body as a modelling reference.
    Replace with detailed Kael mesh after sculpting/importing.
    Each body region is a separate joined object for easy replacement.
    """
    bm = bmesh.new()

    def box(cx, cy, cz, sx, sy, sz):
        mat = __import__('mathutils').Matrix.Translation((cx, cy, cz))
        result = bmesh.ops.create_cube(bm, size=1.0)
        for v in result['verts']:
            v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
            v.co = mat @ v.co

    # Torso
    box(0,    0,    1.15, 0.38, 0.22, 0.30)
    # Hips
    box(0,    0,    0.98, 0.32, 0.20, 0.16)
    # Head
    box(0,    0,    1.65, 0.22, 0.22, 0.25)
    # Neck
    box(0,    0,    1.48, 0.10, 0.10, 0.12)

    # Left upper arm
    box(-0.30, 0, 1.41, 0.12, 0.12, 0.28)
    # Left lower arm
    box(-0.57, 0, 1.40, 0.10, 0.10, 0.26)
    # Left hand
    box(-0.76, 0, 1.39, 0.09, 0.06, 0.16)

    # Right upper arm
    box( 0.30, 0, 1.41, 0.12, 0.12, 0.28)
    # Right lower arm
    box( 0.57, 0, 1.40, 0.10, 0.10, 0.26)
    # Right hand
    box( 0.76, 0, 1.39, 0.09, 0.06, 0.16)

    # Left upper leg
    box(-0.10, 0, 0.74, 0.14, 0.14, 0.42)
    # Left lower leg
    box(-0.10, 0, 0.31, 0.12, 0.12, 0.42)
    # Left foot
    box(-0.10, 0.06, 0.05, 0.11, 0.22, 0.10)

    # Right upper leg
    box( 0.10, 0, 0.74, 0.14, 0.14, 0.42)
    # Right lower leg
    box( 0.10, 0, 0.31, 0.12, 0.12, 0.42)
    # Right foot
    box( 0.10, 0.06, 0.05, 0.11, 0.22, 0.10)

    # Eyes (small flat boxes)
    box(-0.055, 0.115, 1.665, 0.05, 0.02, 0.04)
    box( 0.055, 0.115, 1.665, 0.05, 0.02, 0.04)

    bm.normal_update()
    me = bpy.data.meshes.new('Kael_Body_Mesh')
    bm.to_mesh(me)
    bm.free()

    body = bpy.data.objects.new('Kael_Body', me)
    bpy.context.scene.collection.objects.link(body)

    # Simple skin-tone material
    mat = bpy.data.materials.new('Mat_Kael_Placeholder')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.80, 0.60, 0.46, 1.0)
        bsdf.inputs['Roughness'].default_value  = 0.85
    body.data.materials.append(mat)
    return body


# ─────────────────────────────────────────────────────
#  WEIGHT PAINT (auto weights)
# ─────────────────────────────────────────────────────

def bind_mesh_to_armature(body_obj, arm_obj):
    """Parent mesh to armature with automatic vertex weights."""
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')


# ─────────────────────────────────────────────────────
#  BONE COLORS
# ─────────────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    spine_bones  = ['Root', 'Hips', 'Spine', 'Chest', 'UpperChest', 'Neck', 'Head']
    left_bones   = [n for n in BONES if n.startswith('Left')]
    right_bones  = [n for n in BONES if n.startswith('Right')]
    ik_bones     = ['IK_Foot_L', 'IK_Foot_R', 'IK_Hand_L', 'IK_Hand_R',
                    'Pole_Knee_L', 'Pole_Knee_R', 'Pole_Elbow_L', 'Pole_Elbow_R']
    extra_bones  = ['Weapon_R', 'Compass']

    for b in spine_bones:
        if b in pb: pb[b].color.palette = 'THEME01'   # red — spine
    for b in left_bones:
        if b in pb: pb[b].color.palette = 'THEME04'   # green — left
    for b in right_bones:
        if b in pb: pb[b].color.palette = 'THEME03'   # blue — right
    for b in ik_bones:
        if b in pb: pb[b].color.palette = 'THEME10'   # cyan — IK
    for b in extra_bones:
        if b in pb: pb[b].color.palette = 'THEME09'   # yellow — extras

    object_mode()


# ─────────────────────────────────────────────────────
#  SHAPE KEYS (for facial expressions — optional)
# ─────────────────────────────────────────────────────

def add_shape_keys(body_obj):
    """Adds named shape key slots for facial expressions (fill in sculpt mode)."""
    activate(body_obj)
    bpy.ops.object.shape_key_add(from_mix=False)   # Basis
    body_obj.data.shape_keys.key_blocks[0].name = 'Basis'

    expressions = ['Smile', 'Frown', 'Blink_L', 'Blink_R',
                   'BrowUp', 'BrowDown', 'Surprised', 'Dead']
    for expr in expressions:
        bpy.ops.object.shape_key_add(from_mix=False)
        body_obj.data.shape_keys.key_blocks[-1].name = expr


# ─────────────────────────────────────────────────────
#  EXPORT REPORT
# ─────────────────────────────────────────────────────

def print_rig_report(arm_obj):
    total = len(arm_obj.data.bones)
    deform = sum(1 for b in arm_obj.data.bones if b.use_deform)
    print("\n" + "="*65)
    print("  IsleTrial — Kael Humanoid Rig Report")
    print("="*65)
    print(f"\n  Armature  : {arm_obj.name}")
    print(f"  Total bones   : {total}")
    print(f"  Deform bones  : {deform}")
    print(f"  IK/control    : {total - deform}")
    print("\n  Unity Humanoid Avatar auto-mapped bones:")
    unity_bones = [
        'Hips', 'Spine', 'Chest', 'UpperChest', 'Neck', 'Head',
        'LeftShoulder', 'LeftUpperArm', 'LeftLowerArm', 'LeftHand',
        'RightShoulder', 'RightUpperArm', 'RightLowerArm', 'RightHand',
        'LeftUpperLeg', 'LeftLowerLeg', 'LeftFoot', 'LeftToes',
        'RightUpperLeg', 'RightLowerLeg', 'RightFoot', 'RightToes',
    ]
    for b in unity_bones:
        status = '✓' if b in arm_obj.data.bones else '✗ MISSING'
        print(f"    {status}  {b}")
    print("\n  Extra (Generic) bones:")
    print("    Weapon_R  → cutlass, child of RightHand")
    print("    Compass   → compass glow, child of Hips")
    print("\n  Export settings:")
    print("    File → Export → FBX")
    print("    ✓ Apply Transform   ✓ Armature   ✓ Mesh")
    print("    Scale: 1.0   Axis: Y Up, -Z Forward")
    print("\n  Unity Import:")
    print("    Rig Type: Humanoid")
    print("    Avatar: Create From This Model")
    print("    Scale Factor: 1.0")
    print("\n  Mixamo (for animations):")
    print("    Upload Kael_Character.fbx to mixamo.com")
    print("    → Auto-rig  → download any animation pack")
    print("    → Import into Unity with Humanoid rig")
    print("="*65 + "\n")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def main():
    clear_scene()

    print("\n[KaelRig] Building armature...")
    arm_obj = build_armature()

    print("[KaelRig] Adding IK targets...")
    add_ik_targets(arm_obj)

    print("[KaelRig] Adding rotation limits...")
    add_rotation_limits(arm_obj)

    print("[KaelRig] Building placeholder body mesh...")
    body_obj = build_body_mesh()

    print("[KaelRig] Binding mesh to armature (auto weights)...")
    bind_mesh_to_armature(body_obj, arm_obj)

    print("[KaelRig] Adding shape key slots...")
    add_shape_keys(body_obj)

    print("[KaelRig] Colour-coding bones...")
    color_bones(arm_obj)

    # Set display
    activate(arm_obj)
    arm_obj.data.display_type = 'OCTAHEDRAL'
    arm_obj.show_in_front     = True

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
                    space.overlay.show_bones = True
                    space.overlay.show_relationship_lines = True
            break

    print_rig_report(arm_obj)


main()
