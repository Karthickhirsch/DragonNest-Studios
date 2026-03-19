"""
IsleTrial — Mushroom Boat  (Rig)
Blender 4.x  •  Python Script

Run AFTER  08_MushroomBoat.py

Unity Rig Type → GENERIC  (vehicle / prop rig)

Bone Hierarchy
──────────────────────────────────────────────────────────────────────
  BoatRoot  (world-space anchor)
  └─ Hull_Bone              (entire boat body — driven by buoyancy)
      │
      ├─ Rudder_Pivot        (stern rudder — rotate Y for steering)
      │
      ├─ MushroomCap_Root    (cap base, stable connection to stem)
      │   └─ MushroomCap_Sway  (secondary wobble in wind/waves)
      │
      ├─ Compass_Face_Pivot  (compass head tilt — subtle nod)
      │   └─ Compass_Rose_Spin  (needle / rose rotation — driven by script)
      │
      ├─ Cannon_L_Pivot → Cannon_L_Pitch   (left cannon aim)
      ├─ Cannon_R_Pivot → Cannon_R_Pitch   (right cannon aim)
      │
      ├─ Lantern_0_Pivot  (bow-left  — swing in waves)
      ├─ Lantern_1_Pivot  (bow-right)
      ├─ Lantern_2_Pivot  (stern-left)
      ├─ Lantern_3_Pivot  (stern-right)
      │
      ├─ Anchor_Chain_IK_Root → Chain_0 → Chain_1 → Chain_2
      │   → Chain_3 → Chain_4 → Chain_5 → Chain_6 → Anchor_End
      │
      └─ Float_0 … Float_5   (empty-parented buoyancy points)

IK:
  Anchor_End uses IK with target Anchor_IK_Target (child of BoatRoot,
  drag to seabed position at runtime).

Unity Animator parameters:
  RudderAngle   (Float −45→+45)  → Rudder_Pivot.rotation.y
  CannonPitch_L (Float −5→+15)   → Cannon_L_Pitch.rotation.x
  CannonPitch_R (Float −5→+15)   → Cannon_R_Pitch.rotation.x
  CapSway       (Float)          → MushroomCap_Sway.rotation.z
  CompassSpin   (Float)          → Compass_Rose_Spin.rotation.z
  LanternSwing  (Float)          → all Lantern_*_Pivot.rotation.z
  AnchorDrop    (Float 0→1)      → Anchor_IK_Target.location.z
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
    # ── World anchor
    'BoatRoot':    ((0.000,  0.000, 0.000), (0.000,  0.000, 0.080), None,       False, False),

    # ── Hull — deforms entire mesh; driven by buoyancy system
    'Hull_Bone':   ((0.000,  0.000, 0.000), (0.000,  0.000, 1.820), 'BoatRoot', False, True),

    # ── Rudder
    'Rudder_Pivot':((0.000,  4.580, 0.720), (0.000,  4.580, 1.440), 'Hull_Bone', False, False),
    'Rudder_Blade':((0.000,  4.580, 1.440), (0.000,  4.900, 1.440), 'Rudder_Pivot', False, True),

    # ── Mushroom cap
    'MushroomCap_Root': ((0.000, 0.000, 3.420), (0.000, 0.000, 3.820), 'Hull_Bone',          False, True),
    'MushroomCap_Sway': ((0.000, 0.000, 3.820), (0.000, 0.000, 5.200), 'MushroomCap_Root',   True,  True),

    # ── Compass
    'Compass_Face_Pivot': ((0.000, -1.600, 2.300), (0.000, -1.600, 2.700), 'Hull_Bone',             False, False),
    'Compass_Rose_Spin':  ((0.000, -1.650, 2.300), (0.000, -1.800, 2.300), 'Compass_Face_Pivot',    False, True),

    # ── Left cannon
    'Cannon_L_Pivot': ((-1.080, -2.500, 2.200), (-1.080, -2.500, 2.420), 'Hull_Bone', False, False),
    'Cannon_L_Pitch': ((-1.080, -2.500, 2.420), (-1.080, -2.500, 2.700), 'Cannon_L_Pivot', False, True),

    # ── Right cannon
    'Cannon_R_Pivot': ((1.080, -2.500, 2.200), (1.080, -2.500, 2.420), 'Hull_Bone', False, False),
    'Cannon_R_Pitch': ((1.080, -2.500, 2.420), (1.080, -2.500, 2.700), 'Cannon_R_Pivot', False, True),

    # ── Lanterns (pivot at chain attachment on gunwale)
    'Lantern_0_Pivot': ((-1.10, -3.60, 2.020), (-1.10, -3.60, 2.420), 'Hull_Bone', False, True),
    'Lantern_1_Pivot': (( 1.10, -3.60, 2.020), ( 1.10, -3.60, 2.420), 'Hull_Bone', False, True),
    'Lantern_2_Pivot': ((-1.10,  3.60, 2.020), (-1.10,  3.60, 2.420), 'Hull_Bone', False, True),
    'Lantern_3_Pivot': (( 1.10,  3.60, 2.020), ( 1.10,  3.60, 2.420), 'Hull_Bone', False, True),

    # ── Anchor chain — 8 links + end
    'Chain_Root': ((0.000, -4.100, 1.950), (0.000, -4.100, 1.620), 'Hull_Bone',  False, True),
    'Chain_0':    ((0.000, -4.100, 1.620), (0.000, -4.080, 1.340), 'Chain_Root', True,  True),
    'Chain_1':    ((0.000, -4.080, 1.340), (0.000, -4.000, 1.060), 'Chain_0',    True,  True),
    'Chain_2':    ((0.000, -4.000, 1.060), (0.000, -3.920, 0.800), 'Chain_1',    True,  True),
    'Chain_3':    ((0.000, -3.920, 0.800), (0.000, -3.880, 0.560), 'Chain_2',    True,  True),
    'Chain_4':    ((0.000, -3.880, 0.560), (0.000, -3.840, 0.340), 'Chain_3',    True,  True),
    'Chain_5':    ((0.000, -3.840, 0.340), (0.000, -3.810, 0.140), 'Chain_4',    True,  True),
    'Chain_6':    ((0.000, -3.810, 0.140), (0.000, -3.800, -0.02), 'Chain_5',    True,  True),
    'Anchor_End': ((0.000, -3.800, -0.02), (0.000, -3.800, -0.20), 'Chain_6',    True,  True),
}

IK_BONES = {
    'Anchor_IK_Target': ((0.000, -3.800, -0.20), (0.000, -3.800, 0.040), 'BoatRoot'),
}

# Buoyancy float empty positions (Y = bow→stern, X = port/starboard)
FLOAT_POINTS = [
    (-0.85, -3.50, 0.05),  # bow-port
    ( 0.85, -3.50, 0.05),  # bow-stbd
    (-1.10,  0.00, 0.00),  # mid-port
    ( 1.10,  0.00, 0.00),  # mid-stbd
    (-0.85,  3.50, 0.05),  # stern-port
    ( 0.85,  3.50, 0.05),  # stern-stbd
]

# ──────────────────────────────────────────────
#  BUILD ARMATURE
# ──────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('MushroomBoat_Armature_Data')
    arm_obj  = bpy.data.objects.new('MushroomBoat_Armature', arm_data)
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

# ──────────────────────────────────────────────
#  IK CONSTRAINT (anchor chain)
# ──────────────────────────────────────────────

def setup_ik(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    if 'Anchor_End' in pb:
        c = pb['Anchor_End'].constraints.new('IK')
        c.target      = arm_obj
        c.subtarget   = 'Anchor_IK_Target'
        c.chain_count = 8    # entire chain length

    object_mode()

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

    # Hull — gentle ocean roll/pitch
    lim('Hull_Bone', True, True, True, xn=-8, xx=8, yn=-5, yx=5, zn=-10, zx=10)

    # Rudder — hard turn range
    lim('Rudder_Pivot', False, True, False, yn=-50, yx=50)
    lim('Rudder_Blade', True, True, True, xn=-5, xx=5, yn=-5, yx=5, zn=-5, zx=5)

    # Mushroom cap — gentle sway
    lim('MushroomCap_Root', True, True, True, xn=-8, xx=8, yn=-8, yx=8, zn=-8, zx=8)
    lim('MushroomCap_Sway', True, True, True, xn=-18, xx=18, yn=-12, yx=12, zn=-18, zx=18)

    # Compass — subtle nod
    lim('Compass_Face_Pivot', True, True, True, xn=-10, xx=10, yn=-8, yx=8, zn=-8, zx=8)
    lim('Compass_Rose_Spin',  True, True, False, xn=-5, xx=5, yn=-5, yx=5)

    # Cannons
    for side in ('L', 'R'):
        lim(f'Cannon_{side}_Pivot', False, True, True, yn=-25, yx=25, zn=-12, zx=12)
        lim(f'Cannon_{side}_Pitch', True, False, False, xn=-5, xx=18)

    # Lanterns — pendulum swing
    for li in range(4):
        lim(f'Lantern_{li}_Pivot', True, True, True, xn=-22, xx=22, yn=-18, yx=18, zn=-22, zx=22)

    # Anchor chain links — free range for physics-like IK
    for ci in ['Chain_Root', 'Chain_0', 'Chain_1', 'Chain_2', 'Chain_3',
               'Chain_4', 'Chain_5', 'Chain_6', 'Anchor_End']:
        lim(ci, True, True, True, xn=-65, xx=65, yn=-65, yx=65, zn=-65, zx=65)

    object_mode()

# ──────────────────────────────────────────────
#  COMPASS ROSE SPIN DRIVER
# ──────────────────────────────────────────────

def add_rose_driver(arm_obj):
    """Compass rose slowly rotates with time."""
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones
    if 'Compass_Rose_Spin' not in pb:
        object_mode(); return

    pb['Compass_Rose_Spin'].rotation_mode = 'XYZ'
    try:
        fc = arm_obj.driver_add('pose.bones["Compass_Rose_Spin"].rotation_euler', 2)
        fc.driver.type       = 'SCRIPTED'
        fc.driver.expression = 'frame * 0.025'
    except Exception as e:
        print(f"[MushroomBoatRig] Compass driver note: {e}")
    object_mode()

# ──────────────────────────────────────────────
#  BONE COLORS
# ──────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    core    = ['BoatRoot', 'Hull_Bone', 'Rudder_Pivot', 'Rudder_Blade']
    cap_bns = ['MushroomCap_Root', 'MushroomCap_Sway']
    comp_bns = ['Compass_Face_Pivot', 'Compass_Rose_Spin']
    cannon_bns = ['Cannon_L_Pivot', 'Cannon_L_Pitch', 'Cannon_R_Pivot', 'Cannon_R_Pitch']
    lantern_bns = [f'Lantern_{i}_Pivot' for i in range(4)]
    chain_bns = ['Chain_Root', 'Chain_0', 'Chain_1', 'Chain_2', 'Chain_3',
                 'Chain_4', 'Chain_5', 'Chain_6', 'Anchor_End']
    ik_bns  = list(IK_BONES.keys())

    for b in core:
        if b in pb: pb[b].color.palette = 'THEME01'   # red
    for b in cap_bns:
        if b in pb: pb[b].color.palette = 'THEME06'   # orange
    for b in comp_bns:
        if b in pb: pb[b].color.palette = 'THEME09'   # yellow
    for b in cannon_bns:
        if b in pb: pb[b].color.palette = 'THEME08'   # dark red
    for b in lantern_bns:
        if b in pb: pb[b].color.palette = 'THEME04'   # green
    for b in chain_bns:
        if b in pb: pb[b].color.palette = 'THEME07'   # teal
    for b in ik_bns:
        if b in pb: pb[b].color.palette = 'THEME10'   # cyan

    object_mode()

# ──────────────────────────────────────────────
#  BIND MESHES
# ──────────────────────────────────────────────

RIGID_MAP = {
    # Hull body — parented to Hull_Bone
    'Hull'              : 'Hull_Bone',
    'Hull_Inner'        : 'Hull_Bone',
    'Deck'              : 'Hull_Bone',
    'Deck_Rim_L'        : 'Hull_Bone',
    'Deck_Rim_R'        : 'Hull_Bone',
    'Deck_Rim_Bow'      : 'Hull_Bone',
    'Deck_Rim_Stern'    : 'Hull_Bone',
    'Moss_Trim_L'       : 'Hull_Bone',
    'Moss_Trim_R'       : 'Hull_Bone',
    'Cabin_Base'        : 'Hull_Bone',
    'Cabin_Door_Frame'  : 'Hull_Bone',
    'Cabin_Door'        : 'Hull_Bone',
    'Cabin_Window_L'    : 'Hull_Bone',
    'Cabin_Window_R'    : 'Hull_Bone',
    'Cabin_Window_Glass_L' : 'Hull_Bone',
    'Cabin_Window_Glass_R' : 'Hull_Bone',
    'Mushroom_Stem'     : 'MushroomCap_Root',
    'Cap_Rim'           : 'MushroomCap_Root',
    'MushroomCap'       : 'MushroomCap_Sway',
    # Mushroom spots follow the cap sway
    **{f'MushroomSpot_{i}': 'MushroomCap_Sway' for i in range(8)},
    # Compass
    'Compass_Frame'     : 'Compass_Face_Pivot',
    'Compass_InnerRing' : 'Compass_Face_Pivot',
    'Compass_Face'      : 'Compass_Face_Pivot',
    'Compass_Needle_NS' : 'Compass_Rose_Spin',
    'Compass_Needle_EW' : 'Compass_Rose_Spin',
    'Compass_Mount'     : 'Hull_Bone',
    **{f'Compass_Bolt_{a}': 'Compass_Face_Pivot' for a in range(0, 360, 45)},
    # Cannons
    'Cannon_Carriage_L' : 'Cannon_L_Pivot',
    'Cannon_Barrel_L'   : 'Cannon_L_Pitch',
    'Cannon_Carriage_R' : 'Cannon_R_Pivot',
    'Cannon_Barrel_R'   : 'Cannon_R_Pitch',
    **{f'Cannon_Band_L_{i}': 'Cannon_L_Pitch' for i in range(3)},
    **{f'Cannon_Band_R_{i}': 'Cannon_R_Pitch' for i in range(3)},
    **{f'Cannon_Wheel_L_{i}': 'Cannon_L_Pivot' for i in (-32, 32)},
    **{f'Cannon_Wheel_R_{i}': 'Cannon_R_Pivot' for i in (-32, 32)},
    # Lanterns
    **{f'Lantern_Body_{i}'  : f'Lantern_{i}_Pivot' for i in range(4)},
    **{f'Lantern_Cap_{i}'   : f'Lantern_{i}_Pivot' for i in range(4)},
    **{f'Lantern_Glass_{i}' : f'Lantern_{i}_Pivot' for i in range(4)},
    **{f'Lantern_Chain_{i}_{ci}': 'Hull_Bone' for i in range(4) for ci in range(4)},
    # Anchor + chain
    'Anchor_Shaft'   : 'Anchor_End',
    'Anchor_Fluke_L' : 'Anchor_End',
    'Anchor_Fluke_R' : 'Anchor_End',
    'Anchor_Crossbar': 'Chain_Root',
    **{f'Anchor_Chain_{li}': f'Chain_{li}' if li < 7 else 'Chain_6' for li in range(8)},
    # Cargo
    **{f'Chest_{i}'      : 'Hull_Bone' for i in range(2)},
    **{f'Chest_Band_{i}' : 'Hull_Bone' for i in range(2)},
    **{f'Chest_Lock_{i}' : 'Hull_Bone' for i in range(2)},
    **{f'Crate_{i}'      : 'Hull_Bone' for i in range(3)},
    **{f'Crate_Strap_{i}_{a}': 'Hull_Bone' for i in range(3) for a in range(2)},
    # Mooring + Rudder + Figurehead
    'Mooring_Ring_L' : 'Hull_Bone',
    'Mooring_Ring_R' : 'Hull_Bone',
    'Rudder'         : 'Rudder_Blade',
    'Bow_Figurehead' : 'Hull_Bone',
}


def bind_meshes(arm_obj):
    for mesh_name, bone_name in RIGID_MAP.items():
        obj = bpy.data.objects.get(mesh_name)
        if obj is None:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        obj.parent      = arm_obj
        obj.parent_type = 'BONE'
        obj.parent_bone = bone_name

# ──────────────────────────────────────────────
#  BUOYANCY FLOAT EMPTIES
# ──────────────────────────────────────────────

def add_float_points(arm_obj):
    """
    6 empties parented to Hull_Bone.
    In Unity, attach the FloatPoint component to each.
    BoatController.cs reads these positions for buoyancy forces.
    """
    col = bpy.data.collections.get('IsleTrial_MushroomBoat')
    for fi, (x, y, z) in enumerate(FLOAT_POINTS):
        bpy.ops.object.empty_add(type='SPHERE', radius=0.12, location=(x, y, z))
        emp = bpy.context.active_object
        emp.name = f'Float_Point_{fi}'
        emp.parent      = arm_obj
        emp.parent_type = 'BONE'
        emp.parent_bone = 'Hull_Bone'
        if col:
            for c in list(emp.users_collection):
                c.objects.unlink(emp)
            col.objects.link(emp)

# ──────────────────────────────────────────────
#  ATTACH TO COLLECTION ROOT
# ──────────────────────────────────────────────

def attach_to_root(arm_obj):
    root = bpy.data.objects.get('MushroomBoat_ROOT')
    if root:
        arm_obj.parent = root
    col = bpy.data.collections.get('IsleTrial_MushroomBoat')
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
    print("\n" + "="*68)
    print("  IsleTrial — Mushroom Boat Rig Report")
    print("="*68)
    print(f"\n  Armature      : {arm_obj.name}")
    print(f"  Total bones   : {total}")
    print(f"  Deform bones  : {deform}   Control: {total - deform}")
    print("\n  Bone groups   (by color):")
    print("    RED       — BoatRoot / Hull / Rudder")
    print("    ORANGE    — Mushroom cap sway bones")
    print("    YELLOW    — Compass face + rose spin")
    print("    DARK RED  — Left + Right cannon pivots/pitch")
    print("    GREEN     — Lantern swing pivots  (× 4)")
    print("    TEAL      — Anchor chain IK  (8 links)")
    print("    CYAN      — Anchor IK target")
    print(f"\n  Float points  : {len(FLOAT_POINTS)}  (spheres, parented to Hull_Bone)")
    print("\n  Unity import:")
    print("    Rig Type   →  Generic  (vehicle / prop)")
    print("    Root bone  →  BoatRoot")
    print("\n  Animator parameters to expose:")
    print("    RudderAngle   (Float -45→+45) → Rudder_Pivot.rotation.y")
    print("    CannonPitch_L (Float -5→+15)  → Cannon_L_Pitch.rotation.x")
    print("    CannonPitch_R (Float -5→+15)  → Cannon_R_Pitch.rotation.x")
    print("    CapSway       (Float)         → MushroomCap_Sway.rotation.z")
    print("    CompassSpin   (Float)         → Compass_Rose_Spin.rotation.z")
    print("    LanternSwing  (Float)         → Lantern_*_Pivot.rotation.z")
    print("    AnchorDrop    (Float 0→1)     → Anchor_IK_Target.location.z")
    print("\n  Capacity: 2 Mushroom NPCs + 2 Compass NPCs + 1 Kael")
    print("  Deck area: ~21 m²  (spacious — no clipping)")
    print("="*68 + "\n")

# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    print("\n[MushroomBoatRig] Building armature...")
    arm = build_armature()

    print("[MushroomBoatRig] IK anchor chain...")
    setup_ik(arm)

    print("[MushroomBoatRig] Rotation limits...")
    setup_limits(arm)

    print("[MushroomBoatRig] Compass rose driver...")
    add_rose_driver(arm)

    print("[MushroomBoatRig] Binding meshes...")
    bind_meshes(arm)

    print("[MushroomBoatRig] Adding float empties...")
    add_float_points(arm)

    print("[MushroomBoatRig] Colouring bones...")
    color_bones(arm)

    attach_to_root(arm)

    activate(arm)
    arm.data.display_type = 'STICK'
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
