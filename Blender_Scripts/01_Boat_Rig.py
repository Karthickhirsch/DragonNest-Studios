"""
IsleTrial — Boat Rig
Blender 4.x Python Script

Run AFTER 01_Boat_MainVessel.py (boat mesh objects must exist in scene).

What this script adds
─────────────────────
Armature : "Boat_Armature"
  Root          — world-space control bone at deck origin
  ├─ Sail_Base  — base of mast attachment
  │   ├─ Sail_Mid   — mid-sail billow control
  │   └─ Sail_Tip   — top-of-sail billow control
  ├─ HarpoonMount   — Y-axis aim rotation (bow gun)
  ├─ Rudder         — Z-axis steering rotation
  ├─ Lantern        — sway bone (hanging lantern)
  ├─ Anchor_Root    — anchor chain IK root
  │   ├─ Anchor_Link_00..07  — IK chain (8 links)
  │   └─ Anchor_IK_Target    — IK goal (move to drop anchor)
  └─ Wheel          — ship wheel rotation bone

Buoyancy float empties (for OceanBuoyancy.cs)
  Buoy_FL / FR / BL / BR  — parented to Boat_ROOT

After running:
  • Each mesh part is parented to its control bone
  • Armature is parented to Boat_ROOT empty
  • Select Boat_ROOT → Export FBX (include Armature)

Unity Setup
──────────────────────────────────────────────────────
  BoatController._harpoonSpawnPoint  = HarpoonMount bone
  BoatController._lanternLight child = Lantern bone
  OceanBuoyancy floatPoints          = Buoy_FL/FR/BL/BR transforms
  Animator parameters to expose:
    "SailBillow"   (Float 0-1)  → drives Sail_Mid.rotation.z
    "AnchorDrop"   (Float 0-1)  → drives Anchor_IK_Target position
    "RudderAngle"  (Float -1,1) → drives Rudder.rotation.y
    "WheelSpin"    (Float)      → drives Wheel.rotation.x
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# ─────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────

def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def get_or_warn(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        print(f"[BoatRig] WARNING: '{name}' not found in scene — skipping parent.")
    return obj


def edit_mode(arm_obj):
    activate(arm_obj)
    bpy.ops.object.mode_set(mode='EDIT')
    return arm_obj.data.edit_bones


def pose_mode(arm_obj):
    activate(arm_obj)
    bpy.ops.object.mode_set(mode='POSE')
    return arm_obj.pose.bones


def object_mode():
    bpy.ops.object.mode_set(mode='OBJECT')


def add_bone(edit_bones, name, head, tail, parent=None, connected=False):
    b = edit_bones.new(name)
    b.head = Vector(head)
    b.tail = Vector(tail)
    if parent:
        b.parent = edit_bones[parent]
        b.use_connect = connected
    return b


# ─────────────────────────────────────────────────────
#  1. CREATE ARMATURE
# ─────────────────────────────────────────────────────

def create_boat_armature():
    arm_data = bpy.data.armatures.new('Boat_Armature_Data')
    arm_obj  = bpy.data.objects.new('Boat_Armature', arm_data)
    arm_obj.location = (0, 0, 0)
    arm_obj.show_in_front = True
    bpy.context.scene.collection.objects.link(arm_obj)

    eb = edit_mode(arm_obj)

    # ── Root ──────────────────────────────────────────
    add_bone(eb, 'Root',
             head=(0, 0, 0),
             tail=(0, 0, 0.4))

    # ── Sail chain ────────────────────────────────────
    # Mast is at (0, 1.5, 3.05) in scene; boat deck ~0.05
    add_bone(eb, 'Sail_Base',
             head=(0,  1.5, 0.1),
             tail=(0,  1.5, 1.5),
             parent='Root')
    add_bone(eb, 'Sail_Mid',
             head=(0,  1.5, 1.5),
             tail=(0,  1.5, 3.0),
             parent='Sail_Base', connected=True)
    add_bone(eb, 'Sail_Tip',
             head=(0,  1.5, 3.0),
             tail=(0,  1.5, 4.2),
             parent='Sail_Mid', connected=True)

    # ── Harpoon mount ─────────────────────────────────
    # HarpoonMount is at (0, 4.5, 0.2)
    add_bone(eb, 'HarpoonMount',
             head=(0,  4.5, 0.2),
             tail=(0,  5.3, 0.2),    # points forward (+Y)
             parent='Root')

    # ── Rudder ────────────────────────────────────────
    # Rudder is at (0, -5.0, -0.3)
    add_bone(eb, 'Rudder',
             head=(0, -5.0, 0.1),
             tail=(0, -5.0, -0.8),
             parent='Root')

    # ── Lantern ───────────────────────────────────────
    # Lantern at (-1.0, -2.2, 1.4) — sway on X axis
    add_bone(eb, 'Lantern',
             head=(-1.0, -2.2, 1.7),  # hook point
             tail=(-1.0, -2.2, 1.2),  # hanging down
             parent='Root')

    # ── Ship Wheel ────────────────────────────────────
    add_bone(eb, 'Wheel',
             head=(0, -3.0, 1.1),
             tail=(0, -3.0, 1.5),
             parent='Root')

    # ── Anchor IK chain ───────────────────────────────
    # 8 chain links from bow, hanging down
    LINK_H   = 0.12
    LINK_COUNT = 8
    add_bone(eb, 'Anchor_Root',
             head=(0,  4.2,  0.0),
             tail=(0,  4.2, -0.12),
             parent='Root')

    prev = 'Anchor_Root'
    for i in range(LINK_COUNT):
        bname = f'Anchor_Link_{i:02d}'
        hz = -0.12 - i * LINK_H
        tz = hz - LINK_H
        add_bone(eb, bname,
                 head=(0, 4.2, hz),
                 tail=(0, 4.2, tz),
                 parent=prev, connected=(i > 0))
        prev = bname

    # IK Target (control bone that gets keyed to drop anchor)
    last_tail_z = -0.12 - LINK_COUNT * LINK_H
    add_bone(eb, 'Anchor_IK_Target',
             head=(0, 4.2, last_tail_z),
             tail=(0, 4.2, last_tail_z - 0.2),
             parent='Root')           # NOT connected to chain

    object_mode()
    return arm_obj


# ─────────────────────────────────────────────────────
#  2. IK CONSTRAINT ON ANCHOR CHAIN
# ─────────────────────────────────────────────────────

def setup_anchor_ik(arm_obj):
    """Add IK constraint to the last anchor link targeting Anchor_IK_Target."""
    pb = pose_mode(arm_obj)

    last_link_name = f'Anchor_Link_{7:02d}'
    if last_link_name not in pb:
        print(f"[BoatRig] IK bone '{last_link_name}' not found.")
        object_mode()
        return

    ik = pb[last_link_name].constraints.new('IK')
    ik.target        = arm_obj
    ik.subtarget     = 'Anchor_IK_Target'
    ik.chain_count   = 8
    ik.use_rotation  = False

    object_mode()


# ─────────────────────────────────────────────────────
#  3. BONE ROTATION LIMITS (for Unity Animator clamping)
# ─────────────────────────────────────────────────────

def setup_rotation_limits(arm_obj):
    pb = pose_mode(arm_obj)

    def limit_rot(bone_name, use_x, use_y, use_z,
                  x_min=0, x_max=0, y_min=0, y_max=0, z_min=0, z_max=0):
        if bone_name not in pb:
            return
        c = pb[bone_name].constraints.new('LIMIT_ROTATION')
        c.owner_space = 'LOCAL'
        c.use_limit_x = use_x; c.min_x = math.radians(x_min); c.max_x = math.radians(x_max)
        c.use_limit_y = use_y; c.min_y = math.radians(y_min); c.max_y = math.radians(y_max)
        c.use_limit_z = use_z; c.min_z = math.radians(z_min); c.max_z = math.radians(z_max)

    # Sail bones — billow forward/back only (Y rotation)
    limit_rot('Sail_Mid', False, True, False, y_min=-25, y_max=25)
    limit_rot('Sail_Tip', False, True, False, y_min=-30, y_max=30)

    # Harpoon — Y rotation only (horizontal sweep)
    limit_rot('HarpoonMount', True, False, True,
              x_min=-30, x_max=15,
              z_min=-60, z_max=60)

    # Rudder — Y rotation only (steering)
    limit_rot('Rudder', False, True, False, y_min=-35, y_max=35)

    # Lantern — X sway only
    limit_rot('Lantern', True, False, False, x_min=-20, x_max=20)

    object_mode()


# ─────────────────────────────────────────────────────
#  4. PARENT MESH OBJECTS TO BONES
# ─────────────────────────────────────────────────────

def parent_meshes_to_bones(arm_obj):
    """
    Each boat mesh object is parented to its control bone using
    'Bone' parent type (no weight painting needed — rigid attachment).
    """
    BONE_MAP = {
        'Boat_Sail'        : 'Sail_Base',
        'Boat_HarpoonMount': 'HarpoonMount',
        'Boat_Rudder'      : 'Rudder',
        'Boat_Lantern'     : 'Lantern',
        'Boat_Lantern_Glass': 'Lantern',
    }
    for mesh_name, bone_name in BONE_MAP.items():
        mesh_obj = get_or_warn(mesh_name)
        if mesh_obj is None:
            continue
        # Clear existing parent, keep transform
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # Parent to bone
        mesh_obj.parent      = arm_obj
        mesh_obj.parent_type = 'BONE'
        mesh_obj.parent_bone = bone_name

    # Boat hull, deck, mast, anchor, railing — skinned to armature (weight paint)
    hull_parts = ['Boat_Hull', 'Boat_Deck', 'Boat_Mast', 'Boat_Cabin',
                  'Boat_Anchor', 'Boat_Railing_Port', 'Boat_Railing_Stbd']
    for mesh_name in hull_parts:
        mesh_obj = get_or_warn(mesh_name)
        if mesh_obj is None:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        # Parent with armature deform + automatic weights
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')


# ─────────────────────────────────────────────────────
#  5. BUOYANCY FLOAT POINT EMPTIES
# ─────────────────────────────────────────────────────

def create_buoyancy_floats():
    """
    4 empty objects at hull corners for OceanBuoyancy.cs float points.
    Positions match Boat_Spec.md exactly.
    """
    floats = {
        'Buoy_FL': (-1.5, 3.0, -0.3),   # Front Left
        'Buoy_FR': ( 1.5, 3.0, -0.3),   # Front Right
        'Buoy_BL': (-1.5, -3.0, -0.3),  # Back Left
        'Buoy_BR': ( 1.5, -3.0, -0.3),  # Back Right
    }
    boat_root = bpy.data.objects.get('Boat_ROOT')
    empties = []
    for name, pos in floats.items():
        bpy.ops.object.empty_add(type='SPHERE', radius=0.15, location=pos)
        emp = bpy.context.active_object
        emp.name = name
        emp.empty_display_size = 0.15
        if boat_root:
            emp.parent = boat_root
        empties.append(emp)
    return empties


# ─────────────────────────────────────────────────────
#  6. CUSTOM BONE SHAPES (visual helpers)
# ─────────────────────────────────────────────────────

def set_bone_colors(arm_obj):
    """Color-code bones by function for clarity in pose mode."""
    pb = pose_mode(arm_obj)

    color_map = {
        'Root'            : 'THEME01',   # red
        'Sail_Base'       : 'THEME04',   # green
        'Sail_Mid'        : 'THEME04',
        'Sail_Tip'        : 'THEME04',
        'HarpoonMount'    : 'THEME09',   # yellow
        'Rudder'          : 'THEME09',
        'Lantern'         : 'THEME07',   # orange
        'Wheel'           : 'THEME03',   # blue
        'Anchor_Root'     : 'THEME06',   # purple
        'Anchor_IK_Target': 'THEME10',   # cyan
    }
    for i in range(8):
        color_map[f'Anchor_Link_{i:02d}'] = 'THEME06'

    for bname, theme in color_map.items():
        if bname in pb:
            pb[bname].color.palette = theme

    object_mode()


# ─────────────────────────────────────────────────────
#  7. PARENT ARMATURE TO BOAT_ROOT
# ─────────────────────────────────────────────────────

def attach_to_boat_root(arm_obj):
    boat_root = bpy.data.objects.get('Boat_ROOT')
    if boat_root:
        arm_obj.parent = boat_root
        print("[BoatRig] Armature parented to Boat_ROOT.")
    else:
        print("[BoatRig] Boat_ROOT not found — armature left unparented.")


# ─────────────────────────────────────────────────────
#  8. EXPORT REPORT
# ─────────────────────────────────────────────────────

def print_rig_report(arm_obj, floats):
    print("\n" + "="*60)
    print("  IsleTrial Boat Rig — Report")
    print("="*60)
    pb = arm_obj.pose.bones
    print(f"\nArmature: {arm_obj.name}")
    print(f"Bone count: {len(pb)}\n")
    for b in arm_obj.data.bones:
        pos = b.head_local
        print(f"  {b.name:<24} head=({pos.x:+.3f}, {pos.y:+.3f}, {pos.z:+.3f})")
    print("\nBuoyancy Float Points:")
    for e in floats:
        p = e.location
        print(f"  {e.name:<12} pos=({p.x:+.2f}, {p.y:+.2f}, {p.z:+.2f})")
    print("\nUnity Animator bones to expose as parameters:")
    print("  Sail_Mid / Sail_Tip   → SailBillow (Float)")
    print("  Anchor_IK_Target      → AnchorDrop (Float)")
    print("  Rudder                → RudderAngle (Float)")
    print("  HarpoonMount          → HarpoonYaw / HarpoonPitch (Float)")
    print("  Wheel                 → WheelSpin (Float)")
    print("\nReady to export: select Boat_ROOT → File → Export → FBX")
    print("  FBX settings: Apply Transform ✓, Armature ✓, Mesh ✓")
    print("="*60 + "\n")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def main():
    print("\n[BoatRig] Starting boat rig build...")

    arm_obj = create_boat_armature()
    setup_anchor_ik(arm_obj)
    setup_rotation_limits(arm_obj)
    parent_meshes_to_bones(arm_obj)
    set_bone_colors(arm_obj)
    attach_to_boat_root(arm_obj)
    floats = create_buoyancy_floats()

    # Switch to Material Preview and show armature overlay
    activate(arm_obj)
    arm_obj.data.display_type = 'STICK'
    arm_obj.show_in_front     = True
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.overlay.show_bones = True
            break

    print_rig_report(arm_obj, floats)


main()
