"""
IsleTrial — Mushroom NPC Rig
Blender 4.x Python Script

Run AFTER 04_MushroomNPC.py  (mesh objects must exist in scene).

Character proportions  (height ≈ 1.10 m  — short stocky NPC):
  Ground → Z=0   |   Head (cap top) → Z=1.20

Bone Hierarchy
──────────────────────────────────────────────────────────────────────
  Root
  └─ Hips  (Z≈0.38)
      ├─ Spine → Chest → Neck → Head
      │   └─ MushroomCap_Root → MushroomCap_Wobble  (cap bounce/sway)
      │       └─ MossCollar                           (collar jiggle)
      ├─ LeftShoulder → LeftUpperArm → LeftLowerArm → LeftHand
      │   └─ Staff_Hold  (staff grip bone, child of LeftHand)
      ├─ RightShoulder → RightUpperArm → RightLowerArm → RightHand
      ├─ LeftUpperLeg → LeftLowerLeg → LeftFoot → LeftToes
      └─ RightUpperLeg → RightLowerLeg → RightFoot → RightToes

  IK control bones (non-deform):
      IK_Foot_L / R   IK_Hand_L / R   Pole targets

Unity Humanoid Avatar
──────────────────────────────────────────────────────────────────────
  All 22 required bones present — Unity auto-maps on import.
  Extra bones (MushroomCap_Root, MushroomCap_Wobble, MossCollar,
  Staff_Hold) are Generic bones — drive via Unity Animator.

  Rig Type     : Humanoid
  Scale Factor : 1.0
  Avatar       : Create From This Model
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ─────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────

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

def get_obj(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        print(f"[MushroomRig] WARNING: '{name}' not found — skipping.")
    return obj

# ─────────────────────────────────────────────────────
#  BONE TABLE
#  All positions scaled for  height ≈ 1.10 m  character
#  Blender: Z-up, Y-forward, T-pose arms along ±X
# ─────────────────────────────────────────────────────
#
#  Mushroom proportions vs Kael:
#    hips   0.38  (kael 0.95)
#    chest  0.60
#    neck   0.72
#    head   0.80 – 0.92   (stem face zone)
#    cap    0.92 – 1.20
#    arms   shoulder Z≈0.65, extend to ±0.46 in X
#    legs   upper Z 0.38 – 0.12, lower Z 0.12 – 0.00
# ─────────────────────────────────────────────────────

BONES = {
    # ── Root / Hips
    'Root':             ((0.000,  0.000, 0.000), (0.000,  0.000, 0.060), None,           False),
    'Hips':             ((0.000,  0.000, 0.380), (0.000,  0.000, 0.440), 'Root',         False),

    # ── Spine chain
    'Spine':            ((0.000,  0.000, 0.440), (0.000,  0.000, 0.540), 'Hips',         True),
    'Chest':            ((0.000,  0.000, 0.540), (0.000,  0.000, 0.640), 'Spine',        True),
    'Neck':             ((0.000,  0.000, 0.640), (0.000,  0.000, 0.720), 'Chest',        True),
    'Head':             ((0.000,  0.000, 0.720), (0.000,  0.000, 0.860), 'Neck',         True),

    # ── Mushroom cap (extra — Generic in Unity)
    'MushroomCap_Root': ((0.000,  0.000, 0.920), (0.000,  0.000, 1.030), 'Head',         False),
    'MushroomCap_Wobble':((0.000, 0.000, 1.030), (0.000,  0.000, 1.200), 'MushroomCap_Root', True),
    'MossCollar':       ((0.000,  0.000, 0.680), (0.000,  0.000, 0.730), 'Chest',        False),

    # ── Left arm
    'LeftShoulder':     ((0.000,  0.000, 0.635), (-0.120, 0.000, 0.640), 'Chest',        False),
    'LeftUpperArm':     ((-0.120, 0.000, 0.640), (-0.300, 0.000, 0.630), 'LeftShoulder', True),
    'LeftLowerArm':     ((-0.300, 0.000, 0.630), (-0.450, 0.000, 0.622), 'LeftUpperArm', True),
    'LeftHand':         ((-0.450, 0.000, 0.622), (-0.520, 0.000, 0.618), 'LeftLowerArm', True),
    # Staff grip bone
    'Staff_Hold':       ((-0.520, 0.000, 0.618), (-0.520, 0.000, 0.480), 'LeftHand',     False),

    # ── Right arm
    'RightShoulder':    ((0.000,  0.000, 0.635), (0.120,  0.000, 0.640), 'Chest',        False),
    'RightUpperArm':    ((0.120,  0.000, 0.640), (0.300,  0.000, 0.630), 'RightShoulder',True),
    'RightLowerArm':    ((0.300,  0.000, 0.630), (0.450,  0.000, 0.622), 'RightUpperArm',True),
    'RightHand':        ((0.450,  0.000, 0.622), (0.520,  0.000, 0.618), 'RightLowerArm',True),

    # ── Left leg
    'LeftUpperLeg':     ((-0.080, 0.000, 0.380), (-0.080, 0.005, 0.200), 'Hips',         False),
    'LeftLowerLeg':     ((-0.080, 0.005, 0.200), (-0.080, 0.002, 0.040), 'LeftUpperLeg', True),
    'LeftFoot':         ((-0.080, 0.002, 0.040), (-0.080, 0.090, 0.010), 'LeftLowerLeg', True),
    'LeftToes':         ((-0.080, 0.090, 0.010), (-0.080, 0.140, 0.005), 'LeftFoot',     True),

    # ── Right leg
    'RightUpperLeg':    ((0.080,  0.000, 0.380), (0.080,  0.005, 0.200), 'Hips',         False),
    'RightLowerLeg':    ((0.080,  0.005, 0.200), (0.080,  0.002, 0.040), 'RightUpperLeg',True),
    'RightFoot':        ((0.080,  0.002, 0.040), (0.080,  0.090, 0.010), 'RightLowerLeg',True),
    'RightToes':        ((0.080,  0.090, 0.010), (0.080,  0.140, 0.005), 'RightFoot',    True),
}

IK_BONES = {
    'IK_Foot_L':    ((-0.080, 0.090, 0.010), (-0.080, 0.090, 0.100), 'Root'),
    'IK_Foot_R':    (( 0.080, 0.090, 0.010), ( 0.080, 0.090, 0.100), 'Root'),
    'IK_Hand_L':    ((-0.520, 0.000, 0.618), (-0.520, 0.000, 0.720), 'Root'),
    'IK_Hand_R':    (( 0.520, 0.000, 0.618), ( 0.520, 0.000, 0.720), 'Root'),
    'Pole_Knee_L':  ((-0.080, -0.350, 0.200),(-0.080, -0.350, 0.280), 'Root'),
    'Pole_Knee_R':  (( 0.080, -0.350, 0.200),( 0.080, -0.350, 0.280), 'Root'),
    'Pole_Elbow_L': ((-0.380, -0.280, 0.625),(-0.380, -0.280, 0.700), 'Root'),
    'Pole_Elbow_R': (( 0.380, -0.280, 0.625),( 0.380, -0.280, 0.700), 'Root'),
}

# ─────────────────────────────────────────────────────
#  BUILD ARMATURE
# ─────────────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('MushroomNPC_Armature_Data')
    arm_obj  = bpy.data.objects.new('MushroomNPC_Armature', arm_data)
    arm_obj.show_in_front = True
    bpy.context.scene.collection.objects.link(arm_obj)

    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    for name, (head, tail, parent, connected) in BONES.items():
        b = eb.new(name)
        b.head = Vector(head); b.tail = Vector(tail)
        if parent and parent in eb:
            b.parent = eb[parent]; b.use_connect = connected

    for name, (head, tail, parent) in IK_BONES.items():
        b = eb.new(name)
        b.head = Vector(head); b.tail = Vector(tail)
        b.use_deform = False
        if parent in eb: b.parent = eb[parent]

    object_mode()
    return arm_obj


# ─────────────────────────────────────────────────────
#  IK CONSTRAINTS
# ─────────────────────────────────────────────────────

def setup_ik(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def ik(bone, target, chain, pole=None, pole_angle=0):
        if bone not in pb: return
        c = pb[bone].constraints.new('IK')
        c.target = arm_obj; c.subtarget = target; c.chain_count = chain
        if pole:
            c.pole_target = arm_obj; c.pole_subtarget = pole
            c.pole_angle  = math.radians(pole_angle)

    ik('LeftFoot',  'IK_Foot_L', 3, 'Pole_Knee_L',  -90)
    ik('RightFoot', 'IK_Foot_R', 3, 'Pole_Knee_R',  -90)
    ik('LeftHand',  'IK_Hand_L', 2, 'Pole_Elbow_L', 180)
    ik('RightHand', 'IK_Hand_R', 2, 'Pole_Elbow_R', 180)
    object_mode()


# ─────────────────────────────────────────────────────
#  ROTATION LIMITS
# ─────────────────────────────────────────────────────

def setup_limits(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def lim(bone, ux,uy,uz, xn=0,xx=0, yn=0,yx=0, zn=0,zx=0):
        if bone not in pb: return
        c = pb[bone].constraints.new('LIMIT_ROTATION')
        c.owner_space='LOCAL'
        c.use_limit_x=ux; c.min_x=math.radians(xn); c.max_x=math.radians(xx)
        c.use_limit_y=uy; c.min_y=math.radians(yn); c.max_y=math.radians(yx)
        c.use_limit_z=uz; c.min_z=math.radians(zn); c.max_z=math.radians(zx)

    # Spine
    for b in ['Spine','Chest']:
        lim(b, True,True,True, xn=-20,xx=25, yn=-18,yx=18, zn=-18,zx=18)
    lim('Neck',  True,True,True, xn=-30,xx=30, yn=-25,yx=25, zn=-25,zx=25)
    lim('Head',  True,True,True, xn=-35,xx=35, yn=-30,yx=30, zn=-28,zx=28)

    # Cap wobble — large range for bouncy animation
    lim('MushroomCap_Root',   True,True,True, xn=-20,xx=20, yn=-20,yx=20, zn=-20,zx=20)
    lim('MushroomCap_Wobble', True,True,True, xn=-30,xx=30, yn=-30,yx=30, zn=-30,zx=30)
    lim('MossCollar',         True,True,True, xn=-15,xx=15, yn=-15,yx=15, zn=-15,zx=15)

    # Arms
    for side in ('Left','Right'):
        s = -1 if side=='Left' else 1
        lim(f'{side}UpperArm', True,True,True,
            xn=-90,xx=160, yn=-55*s,yx=55*s, zn=-90,zx=90)
        lim(f'{side}LowerArm', True,False,True,
            xn=0,xx=140, zn=-5,zx=5)
        lim(f'{side}Hand',     True,True,True,
            xn=-60,xx=60, yn=-25,yx=25, zn=-18,zx=18)

    # Legs
    for side in ('Left','Right'):
        lim(f'{side}UpperLeg', True,True,True,
            xn=-95,xx=45, yn=-38,yx=38, zn=-38,zx=38)
        lim(f'{side}LowerLeg', True,False,True,
            xn=-140,xx=0, zn=-5,zx=5)
        lim(f'{side}Foot',     True,True,True,
            xn=-40,xx=28, yn=-12,yx=12, zn=-18,zx=18)

    object_mode()


# ─────────────────────────────────────────────────────
#  BONE COLORS
# ─────────────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones
    spine  = ['Root','Hips','Spine','Chest','Neck','Head']
    cap    = ['MushroomCap_Root','MushroomCap_Wobble','MossCollar','Staff_Hold']
    left   = [n for n in BONES if n.startswith('Left')]
    right  = [n for n in BONES if n.startswith('Right')]
    ik_bns = list(IK_BONES.keys())

    for b in spine:
        if b in pb: pb[b].color.palette = 'THEME01'   # red
    for b in cap:
        if b in pb: pb[b].color.palette = 'THEME06'   # purple — special bones
    for b in left:
        if b in pb: pb[b].color.palette = 'THEME04'   # green
    for b in right:
        if b in pb: pb[b].color.palette = 'THEME03'   # blue
    for b in ik_bns:
        if b in pb: pb[b].color.palette = 'THEME10'   # cyan

    object_mode()


# ─────────────────────────────────────────────────────
#  BIND MESHES TO ARMATURE
# ─────────────────────────────────────────────────────

BONE_PARENT_MAP = {
    # Rigid bone-parented objects (no weight paint needed)
    'MushroomCap'       : 'MushroomCap_Root',
    'MushroomCap_Spots' : 'MushroomCap_Root',
    'Bell'              : 'Staff_Hold',
    'Bell_Clapper'      : 'Staff_Hold',
    'Staff'             : 'Staff_Hold',
}

SKIN_MESHES = [
    'MushroomStem', 'Jacket_Body', 'Arm_L', 'Arm_R',
    'Hand_L', 'Hand_R', 'Belt', 'Belt_Buckle',
    'Leg_L', 'Leg_R', 'Boot_L', 'Boot_R',
    'Backpack', 'Bedroll', 'MossCollar',
]


def bind_meshes(arm_obj):
    # Rigid bone parenting
    for mesh_name, bone_name in BONE_PARENT_MAP.items():
        obj = bpy.data.objects.get(mesh_name)
        if obj is None: continue
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        obj.parent = arm_obj
        obj.parent_type = 'BONE'
        obj.parent_bone = bone_name

    # Auto-weight skinned meshes
    skin_objs = [bpy.data.objects.get(n) for n in SKIN_MESHES
                 if bpy.data.objects.get(n)]
    if skin_objs:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in skin_objs:
            obj.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')


# ─────────────────────────────────────────────────────
#  ATTACH TO COLLECTION ROOT
# ─────────────────────────────────────────────────────

def attach_to_root(arm_obj):
    root = bpy.data.objects.get('MushroomNPC_ROOT')
    if root:
        arm_obj.parent = root
        print("[MushroomRig] Armature parented to MushroomNPC_ROOT.")
    col = bpy.data.collections.get('IsleTrial_MushroomNPC')
    if col and arm_obj.name not in col.objects:
        for c in list(arm_obj.users_collection): c.objects.unlink(arm_obj)
        col.objects.link(arm_obj)


# ─────────────────────────────────────────────────────
#  REPORT
# ─────────────────────────────────────────────────────

def print_report(arm_obj):
    print("\n" + "="*62)
    print("  IsleTrial — Mushroom NPC Rig Report")
    print("="*62)
    total   = len(arm_obj.data.bones)
    deform  = sum(1 for b in arm_obj.data.bones if b.use_deform)
    print(f"\n  Armature     : {arm_obj.name}")
    print(f"  Total bones  : {total}")
    print(f"  Deform bones : {deform}   IK/Control: {total-deform}")
    print("\n  Unity Humanoid bones (22 required):")
    required = ['Hips','Spine','Chest','Neck','Head',
                'LeftShoulder','LeftUpperArm','LeftLowerArm','LeftHand',
                'RightShoulder','RightUpperArm','RightLowerArm','RightHand',
                'LeftUpperLeg','LeftLowerLeg','LeftFoot','LeftToes',
                'RightUpperLeg','RightLowerLeg','RightFoot','RightToes']
    for b in required:
        ok = '✓' if b in arm_obj.data.bones else '✗ MISSING'
        print(f"    {ok}  {b}")
    print("\n  Extra (Generic) bones — drive via Unity Animator:")
    print("    MushroomCap_Root    → cap base position")
    print("    MushroomCap_Wobble  → cap bounce/sway animation")
    print("    MossCollar          → collar jiggle")
    print("    Staff_Hold          → staff grip transform")
    print("\n  Export: select MushroomNPC_ROOT → FBX")
    print("  Unity: Rig → Humanoid | Avatar: Create From This Model")
    print("="*62 + "\n")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def main():
    print("\n[MushroomRig] Building armature...")
    arm_obj = build_armature()

    print("[MushroomRig] Setting up IK...")
    setup_ik(arm_obj)

    print("[MushroomRig] Setting rotation limits...")
    setup_limits(arm_obj)

    print("[MushroomRig] Binding meshes...")
    bind_meshes(arm_obj)

    print("[MushroomRig] Colouring bones...")
    color_bones(arm_obj)

    attach_to_root(arm_obj)

    activate(arm_obj)
    arm_obj.data.display_type = 'OCTAHEDRAL'
    arm_obj.show_in_front     = True

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.overlay.show_bones = True
            break

    print_report(arm_obj)


main()
