"""
IsleTrial — Bird Skeleton NPC  (Rig)
Blender 4.x  •  Python Script

Run AFTER  06_BirdSkeleton.py

NOTE: Unity Rig Type → GENERIC  (not Humanoid — the character
      has wings instead of hands and bird-like feet).
      Use Animator Controller + custom clips for movement.

Bone Hierarchy
──────────────────────────────────────────────────────────────────────
  Root
  └─ Hips
      ├─ Spine → Chest → Neck_1 → Neck_2 → Head
      │   ├─ Beak_Root → Beak_Tip
      │   ├─ EyeLid_L / EyeLid_R   (blink bones, non-deform)
      │   └─ Neck_2  (already listed)
      │
      ├─ Wing_L  (shoulder pivot)
      │   └─ WingUpper_L → WingLower_L → WingWrist_L
      │       ├─ WingFinger_L_0 → WingFinger_L_0_Tip
      │       ├─ WingFinger_L_1 → WingFinger_L_1_Tip
      │       └─ WingFinger_L_2 → WingFinger_L_2_Tip
      │
      ├─ Wing_R  (mirrored)
      │
      ├─ UpperLeg_L → LowerLeg_L → Ankle_L → Foot_L
      │   ├─ Toe_Main_L  → Toe_Main_Tip_L
      │   ├─ Toe_Inner_L → Toe_Inner_Tip_L
      │   ├─ Toe_Outer_L → Toe_Outer_Tip_L
      │   └─ Toe_Back_L  → Toe_Back_Tip_L
      │
      └─ UpperLeg_R → … (mirrored)

  IK targets (non-deform, parented to Root):
      IK_Foot_L / R  •  Pole_Knee_L / R
      IK_Wing_L / R  •  Pole_Wing_L / R  (wing tip targets)
"""

import bpy
import math
from mathutils import Vector

# ──────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────

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

# ──────────────────────────────────────────────
#  BONE TABLE
# ──────────────────────────────────────────────
#  (head_xyz, tail_xyz, parent_name, use_connect, use_deform)
# ──────────────────────────────────────────────

BONES = {
    # ── Core
    'Root':       ((0.000,  0.000, 0.000), (0.000,  0.000, 0.055), None,     False, True),
    'Hips':       ((0.000,  0.000, 0.520), (0.000,  0.000, 0.580), 'Root',   False, True),

    # ── Spine
    'Spine':      ((0.000,  0.000, 0.580), (0.000,  0.000, 0.660), 'Hips',   True,  True),
    'Chest':      ((0.000,  0.000, 0.660), (0.000,  0.000, 0.780), 'Spine',  True,  True),
    'Neck_1':     ((0.000,  0.000, 0.780), (0.000,  0.000, 0.840), 'Chest',  True,  True),
    'Neck_2':     ((0.000,  0.000, 0.840), (0.000,  0.000, 0.900), 'Neck_1', True,  True),
    'Head':       ((0.000,  0.000, 0.900), (0.000,  0.000, 1.010), 'Neck_2', True,  True),

    # ── Beak
    'Beak_Root':  ((0.000, -0.048, 0.952), (0.000, -0.180, 0.942), 'Head',   False, True),
    'Beak_Tip':   ((0.000, -0.180, 0.942), (0.000, -0.320, 0.932), 'Beak_Root', True, True),

    # ── Eye lids (non-deform)
    'EyeLid_L':   ((-0.088, -0.038, 0.975), (-0.088, -0.038, 1.010), 'Head', False, False),
    'EyeLid_R':   (( 0.088, -0.038, 0.975), ( 0.088, -0.038, 1.010), 'Head', False, False),

    # ── Left wing
    'Wing_L':        ((-0.115,  0.000, 0.780), (-0.180,  0.000, 0.780), 'Chest', False, True),
    'WingUpper_L':   ((-0.180,  0.000, 0.780), (-0.400, -0.020, 0.772), 'Wing_L',      True,  True),
    'WingLower_L':   ((-0.400, -0.020, 0.772), (-0.660, -0.010, 0.752), 'WingUpper_L', True,  True),
    'WingWrist_L':   ((-0.660, -0.010, 0.752), (-0.720, -0.010, 0.748), 'WingLower_L', True,  True),
    'WingFinger_L_0':((-0.720, -0.010, 0.748), (-0.860, -0.016, 0.728), 'WingWrist_L', False, True),
    'WingFinger_L_0_Tip':((-0.860,-0.016,0.728), (-0.920,-0.018,0.720), 'WingFinger_L_0', True, True),
    'WingFinger_L_1':((-0.720, -0.010, 0.748), (-0.824, -0.014, 0.650), 'WingWrist_L', False, True),
    'WingFinger_L_1_Tip':((-0.824,-0.014,0.650), (-0.876,-0.015,0.638), 'WingFinger_L_1', True, True),
    'WingFinger_L_2':((-0.720, -0.010, 0.748), (-0.760, -0.008, 0.572), 'WingWrist_L', False, True),
    'WingFinger_L_2_Tip':((-0.760,-0.008,0.572), (-0.800,-0.008,0.560), 'WingFinger_L_2', True, True),

    # ── Right wing (mirror)
    'Wing_R':        ((0.115,  0.000, 0.780), (0.180,  0.000, 0.780), 'Chest',  False, True),
    'WingUpper_R':   ((0.180,  0.000, 0.780), (0.400, -0.020, 0.772), 'Wing_R', True,  True),
    'WingLower_R':   ((0.400, -0.020, 0.772), (0.660, -0.010, 0.752), 'WingUpper_R', True, True),
    'WingWrist_R':   ((0.660, -0.010, 0.752), (0.720, -0.010, 0.748), 'WingLower_R', True, True),
    'WingFinger_R_0':((0.720, -0.010, 0.748), (0.860, -0.016, 0.728), 'WingWrist_R', False, True),
    'WingFinger_R_0_Tip':((0.860,-0.016,0.728),(0.920,-0.018,0.720), 'WingFinger_R_0', True, True),
    'WingFinger_R_1':((0.720, -0.010, 0.748), (0.824, -0.014, 0.650), 'WingWrist_R', False, True),
    'WingFinger_R_1_Tip':((0.824,-0.014,0.650),(0.876,-0.015,0.638), 'WingFinger_R_1', True, True),
    'WingFinger_R_2':((0.720, -0.010, 0.748), (0.760, -0.008, 0.572), 'WingWrist_R', False, True),
    'WingFinger_R_2_Tip':((0.760,-0.008,0.572),(0.800,-0.008,0.560), 'WingFinger_R_2', True, True),

    # ── Left leg (bird proportions)
    'UpperLeg_L':  ((-0.072,  0.010, 0.500), (-0.082,  0.028, 0.340), 'Hips',       False, True),
    'LowerLeg_L':  ((-0.082,  0.028, 0.340), (-0.070, -0.014, 0.165), 'UpperLeg_L', True,  True),
    'Ankle_L':     ((-0.070, -0.014, 0.165), (-0.068,  0.005, 0.042), 'LowerLeg_L', True,  True),
    'Foot_L':      ((-0.068,  0.005, 0.042), (-0.068,  0.005, 0.008), 'Ankle_L',    True,  True),
    'Toe_Main_L':      ((-0.068, 0.005, 0.008), (-0.072, -0.105, -0.026), 'Foot_L', False, True),
    'Toe_Main_Tip_L':  ((-0.072,-0.105,-0.026), (-0.076,-0.155,-0.044), 'Toe_Main_L', True, True),
    'Toe_Inner_L':     ((-0.068, 0.005, 0.008), (-0.010, -0.088, -0.024), 'Foot_L', False, True),
    'Toe_Inner_Tip_L': ((-0.010,-0.088,-0.024), ( 0.030,-0.128,-0.042), 'Toe_Inner_L', True, True),
    'Toe_Outer_L':     ((-0.068, 0.005, 0.008), (-0.118,-0.090, -0.022), 'Foot_L', False, True),
    'Toe_Outer_Tip_L': ((-0.118,-0.090,-0.022), (-0.158,-0.130,-0.040), 'Toe_Outer_L', True, True),
    'Toe_Back_L':      ((-0.068, 0.005, 0.008), (-0.065,  0.078, -0.010), 'Foot_L', False, True),
    'Toe_Back_Tip_L':  ((-0.065, 0.078,-0.010), (-0.062,  0.118, -0.028), 'Toe_Back_L', True, True),

    # ── Right leg
    'UpperLeg_R':  ((0.072,  0.010, 0.500), (0.082,  0.028, 0.340), 'Hips',       False, True),
    'LowerLeg_R':  ((0.082,  0.028, 0.340), (0.070, -0.014, 0.165), 'UpperLeg_R', True,  True),
    'Ankle_R':     ((0.070, -0.014, 0.165), (0.068,  0.005, 0.042), 'LowerLeg_R', True,  True),
    'Foot_R':      ((0.068,  0.005, 0.042), (0.068,  0.005, 0.008), 'Ankle_R',    True,  True),
    'Toe_Main_R':      ((0.068, 0.005, 0.008), (0.072, -0.105, -0.026), 'Foot_R', False, True),
    'Toe_Main_Tip_R':  ((0.072,-0.105,-0.026), (0.076,-0.155,-0.044), 'Toe_Main_R',  True, True),
    'Toe_Inner_R':     ((0.068, 0.005, 0.008), (0.010, -0.088, -0.024), 'Foot_R', False, True),
    'Toe_Inner_Tip_R': ((0.010,-0.088,-0.024), (-0.030,-0.128,-0.042), 'Toe_Inner_R', True, True),
    'Toe_Outer_R':     ((0.068, 0.005, 0.008), (0.118, -0.090, -0.022), 'Foot_R', False, True),
    'Toe_Outer_Tip_R': ((0.118,-0.090,-0.022), (0.158,-0.130,-0.040), 'Toe_Outer_R', True, True),
    'Toe_Back_R':      ((0.068, 0.005, 0.008), (0.065,  0.078, -0.010), 'Foot_R', False, True),
    'Toe_Back_Tip_R':  ((0.065, 0.078,-0.010), (0.062,  0.118, -0.028), 'Toe_Back_R', True, True),
}

IK_BONES = {
    'IK_Foot_L':   ((-0.068, -0.105, -0.026), (-0.068, -0.105, 0.070), 'Root'),
    'IK_Foot_R':   (( 0.068, -0.105, -0.026), ( 0.068, -0.105, 0.070), 'Root'),
    'Pole_Knee_L': ((-0.082, -0.380,  0.340), (-0.082, -0.380, 0.420), 'Root'),
    'Pole_Knee_R': (( 0.082, -0.380,  0.340), ( 0.082, -0.380, 0.420), 'Root'),
    'IK_Wing_L':   ((-0.900, -0.018,  0.728), (-0.900, -0.018, 0.820), 'Root'),
    'IK_Wing_R':   (( 0.900, -0.018,  0.728), ( 0.900, -0.018, 0.820), 'Root'),
    'Pole_Wing_L': ((-0.400, -0.300,  0.772), (-0.400, -0.300, 0.840), 'Root'),
    'Pole_Wing_R': (( 0.400, -0.300,  0.772), ( 0.400, -0.300, 0.840), 'Root'),
}

# ──────────────────────────────────────────────
#  BUILD
# ──────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('BirdSkeleton_Armature_Data')
    arm_obj  = bpy.data.objects.new('BirdSkeleton_Armature', arm_data)
    arm_obj.show_in_front = True
    bpy.context.scene.collection.objects.link(arm_obj)

    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    for name, (head, tail, parent, connected, deform) in BONES.items():
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        b.use_deform = deform
        if parent and parent in eb:
            b.parent = eb[parent]
            b.use_connect = connected

    for name, (head, tail, parent) in IK_BONES.items():
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        b.use_deform = False
        if parent in eb:
            b.parent = eb[parent]

    object_mode()
    return arm_obj


def setup_ik(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def ik(bone, tgt, chain, pole=None, pole_angle=0):
        if bone not in pb: return
        c = pb[bone].constraints.new('IK')
        c.target = arm_obj; c.subtarget = tgt; c.chain_count = chain
        if pole:
            c.pole_target   = arm_obj
            c.pole_subtarget = pole
            c.pole_angle    = math.radians(pole_angle)

    ik('Foot_L', 'IK_Foot_L', 3, 'Pole_Knee_L', -90)
    ik('Foot_R', 'IK_Foot_R', 3, 'Pole_Knee_R', -90)
    ik('WingFinger_L_0_Tip', 'IK_Wing_L', 4, 'Pole_Wing_L', 90)
    ik('WingFinger_R_0_Tip', 'IK_Wing_R', 4, 'Pole_Wing_R', 90)
    object_mode()


def setup_limits(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def lim(bone, ux, uy, uz, xn=0, xx=0, yn=0, yx=0, zn=0, zx=0):
        if bone not in pb: return
        c = pb[bone].constraints.new('LIMIT_ROTATION')
        c.owner_space = 'LOCAL'
        c.use_limit_x = ux; c.min_x = math.radians(xn); c.max_x = math.radians(xx)
        c.use_limit_y = uy; c.min_y = math.radians(yn); c.max_y = math.radians(yx)
        c.use_limit_z = uz; c.min_z = math.radians(zn); c.max_z = math.radians(zx)

    lim('Spine',  True, True, True, xn=-20, xx=25, yn=-18, yx=18, zn=-18, zx=18)
    lim('Chest',  True, True, True, xn=-18, xx=22, yn=-15, yx=15, zn=-15, zx=15)
    lim('Neck_1', True, True, True, xn=-30, xx=30, yn=-25, yx=25, zn=-25, zx=25)
    lim('Neck_2', True, True, True, xn=-30, xx=30, yn=-20, yx=20, zn=-20, zx=20)
    lim('Head',   True, True, True, xn=-40, xx=40, yn=-35, yx=35, zn=-30, zx=30)
    lim('Beak_Root', True, True, True, xn=-35, xx=15, yn=-10, yx=10, zn=-8,  zx=8)

    for s in ('L', 'R'):
        sx = -1 if s == 'L' else 1
        lim(f'Wing_{s}',      True, True, True, xn=-25, xx=25, yn=-20, yx=20, zn=-30, zx=30)
        lim(f'WingUpper_{s}', True, True, True, xn=-90, xx=90, yn=-45*sx, yx=45*sx, zn=-90, zx=90)
        lim(f'WingLower_{s}', True, False, True, xn=-140, xx=0,  zn=-10, zx=10)
        for fi in range(3):
            lim(f'WingFinger_{s}_{fi}', True, False, True, xn=-80, xx=10, zn=-5, zx=5)

        lim(f'UpperLeg_{s}', True, True, True, xn=-100, xx=50, yn=-40, yx=40, zn=-40, zx=40)
        lim(f'LowerLeg_{s}', True, False, True, xn=0, xx=145, zn=-5, zx=5)
        lim(f'Ankle_{s}',    True, True, True, xn=-45, xx=30, yn=-15, yx=15, zn=-20, zx=20)
        for toe in ('Main', 'Inner', 'Outer', 'Back'):
            lim(f'Toe_{toe}_{s}', True, False, True, xn=-55, xx=10, zn=-8, zx=8)

    object_mode()


def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    spine  = ['Root', 'Hips', 'Spine', 'Chest', 'Neck_1', 'Neck_2', 'Head', 'Beak_Root', 'Beak_Tip']
    eyes   = ['EyeLid_L', 'EyeLid_R']
    left   = [n for n in BONES if n.endswith('_L') and not n.startswith('IK') and not n.startswith('Pole')]
    right  = [n for n in BONES if n.endswith('_R') and not n.startswith('IK') and not n.startswith('Pole')]
    ik_bns = list(IK_BONES.keys())

    for b in spine:
        if b in pb: pb[b].color.palette = 'THEME01'
    for b in eyes:
        if b in pb: pb[b].color.palette = 'THEME09'
    for b in left:
        if b in pb: pb[b].color.palette = 'THEME04'
    for b in right:
        if b in pb: pb[b].color.palette = 'THEME03'
    for b in ik_bns:
        if b in pb: pb[b].color.palette = 'THEME10'

    object_mode()


def bind_meshes(arm_obj):
    # All meshes auto-weight skin
    col = bpy.data.collections.get('IsleTrial_BirdSkeleton')
    skin_objs = []
    if col:
        for obj in col.all_objects:
            if obj.type == 'MESH' and obj.name not in ('BirdSkeleton_ROOT',):
                skin_objs.append(obj)

    if skin_objs:
        bpy.ops.object.select_all(action='DESELECT')
        for o in skin_objs:
            o.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')


def attach_to_root(arm_obj):
    root = bpy.data.objects.get('BirdSkeleton_ROOT')
    if root:
        arm_obj.parent = root
    col = bpy.data.collections.get('IsleTrial_BirdSkeleton')
    if col and arm_obj.name not in col.objects:
        for c in list(arm_obj.users_collection):
            c.objects.unlink(arm_obj)
        col.objects.link(arm_obj)


def print_report(arm_obj):
    print("\n" + "="*62)
    print("  IsleTrial — Bird Skeleton Rig Report")
    print("="*62)
    total  = len(arm_obj.data.bones)
    deform = sum(1 for b in arm_obj.data.bones if b.use_deform)
    print(f"\n  Armature     : {arm_obj.name}")
    print(f"  Total bones  : {total}")
    print(f"  Deform bones : {deform}   Control/IK: {total - deform}")
    print("\n  Bone groups  (by color):")
    print("    RED    — Root / Spine / Head / Beak")
    print("    YELLOW — Eye lid control bones")
    print("    GREEN  — Left wing + left leg")
    print("    BLUE   — Right wing + right leg")
    print("    CYAN   — IK targets + pole targets")
    print("\n  Unity import:")
    print("    Rig Type  →  Generic  (NOT Humanoid)")
    print("    Root bone →  Root")
    print("    Animator  →  custom wing flap / walk / idle clips")
    print("="*62 + "\n")


def main():
    print("\n[BirdSkeleton_Rig] Building armature...")
    arm = build_armature()

    print("[BirdSkeleton_Rig] IK setup...")
    setup_ik(arm)

    print("[BirdSkeleton_Rig] Rotation limits...")
    setup_limits(arm)

    print("[BirdSkeleton_Rig] Binding meshes...")
    bind_meshes(arm)

    print("[BirdSkeleton_Rig] Colouring bones...")
    color_bones(arm)

    attach_to_root(arm)

    activate(arm)
    arm.data.display_type = 'STICK'
    arm.show_in_front     = True

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D':
                    sp.shading.type    = 'MATERIAL'
                    sp.overlay.show_bones = True
            break

    print_report(arm)


main()
