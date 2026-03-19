"""
IsleTrial — Treasure Mimic Chest  (Rig)
Blender 4.x  •  Python Script

Run AFTER  07_MimicChest.py

NOTE: Unity Rig Type → GENERIC  (not Humanoid — the chest is a prop).
      Expose Animator parameters to drive open/close, blink, tentacle sway.

Bone Hierarchy
──────────────────────────────────────────────────────────────────────
  Root
  ├─ Chest_Body_Bone          (rigid, deform: false — moves whole body)
  │
  ├─ Lid_Pivot                (hinge point at Z=0.460, Y=+0.242)
  │   └─ Lid_Bone             (the lid plate + teeth + lock hasp)
  │
  ├─ Eye_Root                 (non-deform, anchors eye group)
  │   ├─ Eye_Ball             (whole eyeball rotation)
  │   ├─ EyeLid_Top_Bone      (top lid close)
  │   └─ EyeLid_Bot_Bone      (bottom lid close)
  │
  ├─ Tongue_Root → Tongue_Mid → Tongue_Tip_L
  │                           └─ Tongue_Tip_R
  │
  ├─ Tentacle_0_Root → Tentacle_0_Mid → Tentacle_0_Tip
  ├─ Tentacle_1_Root → Tentacle_1_Mid → Tentacle_1_Tip
  ├─ Tentacle_2_Root → Tentacle_2_Mid → Tentacle_2_Tip
  └─ Tentacle_3_Root → Tentacle_3_Mid → Tentacle_3_Tip

Unity Animator parameters:
  LidAngle      (Float 0–1)  → Lid_Pivot.rotation.x   (0=closed, 1=open)
  Blink         (Trigger)    → EyeLid_Top/Bot converge
  EyeLook_H/V   (Float)      → Eye_Ball.rotation.y / .x
  TentacleWave  (Float)      → drive all Tentacle_*_Mid rotation.z
  TongueLick    (Trigger)    → Tongue_Root → Tip forward motion
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
#  (head, tail, parent, use_connect, use_deform)
# ──────────────────────────────────────────────

BONES = {
    # ── Anchor
    'Root':           ((0.000,  0.000, 0.000), (0.000,  0.000, 0.060), None,              False, False),

    # ── Chest body (non-deform control for physics/sliding)
    'Chest_Body_Bone':((0.000,  0.000, 0.000), (0.000,  0.000, 0.460), 'Root',            False, False),

    # ── Lid pivot — hinge axis at back of chest (Y = +0.250, Z = 0.460)
    'Lid_Pivot':      ((0.000,  0.250, 0.460), (0.000,  0.250, 0.530), 'Root',            False, False),
    'Lid_Bone':       ((0.000,  0.250, 0.530), (0.000,  0.000, 0.680), 'Lid_Pivot',       False, True),

    # ── Eye group
    'Eye_Root':       ((0.000, -0.265, 0.360), (0.000, -0.265, 0.430), 'Root',            False, False),
    'Eye_Ball':       ((0.000, -0.265, 0.360), (0.000, -0.320, 0.360), 'Eye_Root',        False, True),
    'EyeLid_Top_Bone':((0.000, -0.258, 0.435), (0.000, -0.258, 0.470), 'Eye_Root',        False, True),
    'EyeLid_Bot_Bone':((0.000, -0.258, 0.285), (0.000, -0.258, 0.250), 'Eye_Root',        False, True),

    # ── Tongue chain
    'Tongue_Root':    ((0.000, -0.190, 0.440), (0.000, -0.250, 0.418), 'Root',            False, True),
    'Tongue_Mid':     ((0.000, -0.250, 0.418), (0.000, -0.340, 0.390), 'Tongue_Root',     True,  True),
    'Tongue_Tip_L':   ((-0.028,-0.340, 0.390), (-0.038,-0.390, 0.372), 'Tongue_Mid',      True,  True),
    'Tongue_Tip_R':   (( 0.028,-0.340, 0.390), ( 0.038,-0.390, 0.372), 'Tongue_Mid',      False, True),

    # ── Tentacle 0  (left outer)
    'Tentacle_0_Root':((-0.180,-0.200, 0.460), (-0.230,-0.295, 0.395), 'Root',            False, True),
    'Tentacle_0_Mid': ((-0.230,-0.295, 0.395), (-0.310,-0.375, 0.270), 'Tentacle_0_Root', True,  True),
    'Tentacle_0_Tip': ((-0.310,-0.375, 0.270), (-0.385,-0.420, 0.140), 'Tentacle_0_Mid',  True,  True),

    # ── Tentacle 1  (left inner)
    'Tentacle_1_Root':((-0.100,-0.220, 0.460), (-0.110,-0.335, 0.370), 'Root',            False, True),
    'Tentacle_1_Mid': ((-0.110,-0.335, 0.370), (-0.095,-0.425, 0.210), 'Tentacle_1_Root', True,  True),
    'Tentacle_1_Tip': ((-0.095,-0.425, 0.210), (-0.080,-0.500, 0.075), 'Tentacle_1_Mid',  True,  True),

    # ── Tentacle 2  (right inner)
    'Tentacle_2_Root':((0.080, -0.220, 0.460), (0.090, -0.340, 0.360), 'Root',            False, True),
    'Tentacle_2_Mid': ((0.090, -0.340, 0.360), (0.080, -0.430, 0.200), 'Tentacle_2_Root', True,  True),
    'Tentacle_2_Tip': ((0.080, -0.430, 0.200), (0.065, -0.510, 0.060), 'Tentacle_2_Mid',  True,  True),

    # ── Tentacle 3  (right outer)
    'Tentacle_3_Root':((0.200, -0.200, 0.460), (0.255, -0.295, 0.385), 'Root',            False, True),
    'Tentacle_3_Mid': ((0.255, -0.295, 0.385), (0.330, -0.370, 0.260), 'Tentacle_3_Root', True,  True),
    'Tentacle_3_Tip': ((0.330, -0.370, 0.260), (0.360, -0.405, 0.120), 'Tentacle_3_Mid',  True,  True),
}

# ──────────────────────────────────────────────
#  BUILD ARMATURE
# ──────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('MimicChest_Armature_Data')
    arm_obj  = bpy.data.objects.new('MimicChest_Armature', arm_data)
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

    object_mode()
    return arm_obj

# ──────────────────────────────────────────────
#  ROTATION LIMITS
# ──────────────────────────────────────────────

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

    # Lid: rotates around X axis at pivot (0=closed, 110=fully open)
    lim('Lid_Bone', True, True, True, xn=-115, xx=5, yn=-5, yx=5, zn=-5, zx=5)

    # Eye ball — horizontal + vertical tracking range
    lim('Eye_Ball', True, True, True, xn=-30, xx=30, yn=-35, yx=35, zn=-5, zx=5)

    # Eye lids — open/close
    lim('EyeLid_Top_Bone', True, False, False, xn=-45, xx=5)
    lim('EyeLid_Bot_Bone', True, False, False, xn=-5,  xx=45)

    # Tongue — can swing forward and side to side
    lim('Tongue_Root', True, True, True, xn=-15, xx=45, yn=-20, yx=20, zn=-15, zx=15)
    lim('Tongue_Mid',  True, True, True, xn=-20, xx=40, yn=-25, yx=25, zn=-20, zx=20)
    for side in ('L', 'R'):
        lim(f'Tongue_Tip_{side}', True, True, True,
            xn=-25, xx=25, yn=-30, yx=30, zn=-25, zx=25)

    # Tentacles — each joint can sway significantly
    for ti in range(4):
        for seg in ('Root', 'Mid', 'Tip'):
            lim(f'Tentacle_{ti}_{seg}', True, True, True,
                xn=-60, xx=60, yn=-60, yx=60, zn=-60, zx=60)

    object_mode()

# ──────────────────────────────────────────────
#  BONE COLORS
# ──────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    chest_bns   = ['Root', 'Chest_Body_Bone', 'Lid_Pivot', 'Lid_Bone']
    eye_bns     = ['Eye_Root', 'Eye_Ball', 'EyeLid_Top_Bone', 'EyeLid_Bot_Bone']
    tongue_bns  = ['Tongue_Root', 'Tongue_Mid', 'Tongue_Tip_L', 'Tongue_Tip_R']
    tent_bns    = [n for n in BONES if 'Tentacle' in n]

    for b in chest_bns:
        if b in pb: pb[b].color.palette = 'THEME01'   # red
    for b in eye_bns:
        if b in pb: pb[b].color.palette = 'THEME09'   # yellow
    for b in tongue_bns:
        if b in pb: pb[b].color.palette = 'THEME06'   # purple
    for b in tent_bns:
        if b in pb: pb[b].color.palette = 'THEME07'   # teal

    object_mode()

# ──────────────────────────────────────────────
#  BIND MESHES
# ──────────────────────────────────────────────

# Rigid bone-parented objects (follow a single bone exactly)
RIGID_MAP = {
    'Chest_Body'    : 'Chest_Body_Bone',
    'Band_Front_0'  : 'Chest_Body_Bone',
    'Band_Front_1'  : 'Chest_Body_Bone',
    'Band_Front_2'  : 'Chest_Body_Bone',
    'Band_Back_0'   : 'Chest_Body_Bone',
    'Band_Back_1'   : 'Chest_Body_Bone',
    'Band_Back_2'   : 'Chest_Body_Bone',
    'Band_Side_L_0' : 'Chest_Body_Bone',
    'Band_Side_L_1' : 'Chest_Body_Bone',
    'Band_Side_L_2' : 'Chest_Body_Bone',
    'Band_Side_R_0' : 'Chest_Body_Bone',
    'Band_Side_R_1' : 'Chest_Body_Bone',
    'Band_Side_R_2' : 'Chest_Body_Bone',
    'Lock_Plate'    : 'Chest_Body_Bone',
    'Keyhole'       : 'Chest_Body_Bone',
    'Hinge_L'       : 'Chest_Body_Bone',
    'Hinge_R'       : 'Chest_Body_Bone',
    'Chest_Lid'     : 'Lid_Bone',
    'Tooth_Top_0'   : 'Lid_Bone',
    'Tooth_Top_1'   : 'Lid_Bone',
    'Tooth_Top_2'   : 'Lid_Bone',
    'Tooth_Top_3'   : 'Lid_Bone',
    'Tooth_Top_4'   : 'Lid_Bone',
    'Tooth_Top_5'   : 'Lid_Bone',
    'Eye_Sclera'    : 'Eye_Ball',
    'Eye_Iris'      : 'Eye_Ball',
    'Eye_Pupil'     : 'Eye_Ball',
    'Eyelid_Top'    : 'EyeLid_Top_Bone',
    'Eyelid_Bot'    : 'EyeLid_Bot_Bone',
    'Interior_Glow' : 'Chest_Body_Bone',
}

# Corner brackets (auto-generated names)
for ci in range(2):
    for xi in (-1, 1):
        for yi in (-1, 1):
            RIGID_MAP[f'Corner_{xi}_{yi}_{ci}'] = 'Chest_Body_Bone'

# Coins
for ci in range(5):
    RIGID_MAP[f'Coin_{ci}'] = 'Chest_Body_Bone'

# Teeth on body — bottom teeth stay on body
for ti in range(6):
    RIGID_MAP[f'Tooth_Bot_{ti}'] = 'Chest_Body_Bone'

# Auto-weighted (soft-body style) objects
SKIN_MESHES = ['Tongue', 'Tongue_Tip_L', 'Tongue_Tip_R',
               'Tentacle_0', 'Tentacle_1', 'Tentacle_2', 'Tentacle_3']


def bind_meshes(arm_obj):
    # Rigid parents
    for mesh_name, bone_name in RIGID_MAP.items():
        obj = bpy.data.objects.get(mesh_name)
        if obj is None: continue
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        obj.parent      = arm_obj
        obj.parent_type = 'BONE'
        obj.parent_bone = bone_name

    # Auto-weight soft meshes
    skin_objs = [bpy.data.objects.get(n) for n in SKIN_MESHES
                 if bpy.data.objects.get(n)]
    if skin_objs:
        bpy.ops.object.select_all(action='DESELECT')
        for o in skin_objs:
            o.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# ──────────────────────────────────────────────
#  ATTACH TO COLLECTION ROOT
# ──────────────────────────────────────────────

def attach_to_root(arm_obj):
    root = bpy.data.objects.get('MimicChest_ROOT')
    if root:
        arm_obj.parent = root
    col = bpy.data.collections.get('IsleTrial_MimicChest')
    if col and arm_obj.name not in col.objects:
        for c in list(arm_obj.users_collection):
            c.objects.unlink(arm_obj)
        col.objects.link(arm_obj)

# ──────────────────────────────────────────────
#  REPORT
# ──────────────────────────────────────────────

def print_report(arm_obj):
    total  = len(arm_obj.data.bones)
    deform = sum(1 for b in arm_obj.data.bones if b.use_deform)
    print("\n" + "="*65)
    print("  IsleTrial — Treasure Mimic Chest Rig Report")
    print("="*65)
    print(f"\n  Armature     : {arm_obj.name}")
    print(f"  Total bones  : {total}")
    print(f"  Deform bones : {deform}   Control: {total - deform}")
    print("\n  Bone groups  (by color):")
    print("    RED    — Root / Chest body / Lid")
    print("    YELLOW — Eye ball + lids")
    print("    PURPLE — Tongue chain")
    print("    TEAL   — All 4 tentacle chains  (3 bones each)")
    print("\n  Unity import:")
    print("    Rig Type  →  Generic  (NOT Humanoid)")
    print("    Root bone →  Root")
    print("\n  Suggested Animator parameters:")
    print("    LidAngle      (Float 0-1) → Lid_Pivot.rotation.x")
    print("    Blink         (Trigger)   → EyeLid_Top/Bot_Bone converge")
    print("    EyeLook_H/V   (Float)     → Eye_Ball.rotation.y / .x")
    print("    TentacleWave  (Float)     → Tentacle_*_Mid.rotation.z  (all)")
    print("    TongueLick    (Trigger)   → Tongue_Root forward animation")
    print("="*65 + "\n")

# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    print("\n[MimicChest_Rig] Building armature...")
    arm = build_armature()

    print("[MimicChest_Rig] Rotation limits...")
    setup_limits(arm)

    print("[MimicChest_Rig] Binding meshes...")
    bind_meshes(arm)

    print("[MimicChest_Rig] Colouring bones...")
    color_bones(arm)

    attach_to_root(arm)

    activate(arm)
    arm.data.display_type = 'OCTAHEDRAL'
    arm.show_in_front     = True

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D':
                    sp.shading.type       = 'MATERIAL'
                    sp.overlay.show_bones = True
            break

    print_report(arm)


main()
