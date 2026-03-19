"""
IsleTrial — Compass NPC Rig
Blender 4.x Python Script

Run AFTER 05_CompassNPC.py  (mesh objects must exist in scene).

Character proportions  (height ≈ 1.25 m — slightly taller than Mushroom NPC):
  Ground → Z=0   |   Hat brim top → Z=1.26

Bone Hierarchy
──────────────────────────────────────────────────────────────────────
  Root
  └─ Hips  (Z≈0.42)
      ├─ Spine → Chest → Neck → Head
      │   ├─ CompassFace_Pivot   (the whole compass head rigid mount)
      │   │   └─ CompassRose_Spin  (compass rose + needles rotate here)
      │   └─ Hat_Root → Hat_Tilt   (hat can tilt/fly off)
      │
      ├─ LeftShoulder → LeftUpperArm → LeftLowerArm → LeftHand
      │   └─ Torch_Hold   (torch bone — child of LeftHand)
      │
      ├─ RightShoulder → RightUpperArm → RightLowerArm → RightHand
      │   └─ Knife_Hold   (knife bone — child of RightHand)
      │
      ├─ LeftUpperLeg → LeftLowerLeg → LeftFoot → LeftToes
      └─ RightUpperLeg → RightLowerLeg → RightFoot → RightToes

  IK control bones (non-deform):
      IK_Foot_L / R   IK_Hand_L / R   Pole targets

Unity Humanoid Avatar
──────────────────────────────────────────────────────────────────────
  All 22 required bones present — Unity auto-maps on import.
  Extra bones (CompassFace_Pivot, CompassRose_Spin, Hat_Root,
  Hat_Tilt, Torch_Hold, Knife_Hold) are Generic — drive via Animator.

  Animator parameter ideas:
    "RoseSpinSpeed" (Float)  → drive CompassRose_Spin.rotation.z
    "HatTilt"       (Float)  → drive Hat_Tilt.rotation.x
    "TorchFlicker"  (Float)  → drive Torch_Hold scale / child flame
    "KnifeSlash"    (Trigger) → trigger right arm slash animation

  Rig Type     : Humanoid
  Scale Factor : 1.0
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


# ─────────────────────────────────────────────────────
#  BONE TABLE
#  Proportions for  height ≈ 1.25 m  stocky explorer
# ─────────────────────────────────────────────────────

BONES = {
    # ── Root / Hips
    'Root':             ((0.000,  0.000, 0.000), (0.000,  0.000, 0.065), None,            False),
    'Hips':             ((0.000,  0.000, 0.420), (0.000,  0.000, 0.490), 'Root',          False),

    # ── Spine chain
    'Spine':            ((0.000,  0.000, 0.490), (0.000,  0.000, 0.590), 'Hips',          True),
    'Chest':            ((0.000,  0.000, 0.590), (0.000,  0.000, 0.700), 'Spine',         True),
    'Neck':             ((0.000,  0.000, 0.700), (0.000,  0.000, 0.790), 'Chest',         True),
    'Head':             ((0.000,  0.000, 0.790), (0.000,  0.000, 0.930), 'Neck',          True),

    # ── Compass head (extra Generic bones)
    'CompassFace_Pivot':((0.000,  0.000, 0.840), (0.000,  0.000, 0.950), 'Head',          False),
    'CompassRose_Spin': ((0.000,  0.000, 0.875), (0.000,  0.000, 0.950), 'CompassFace_Pivot', False),

    # ── Hat (extra Generic bones)
    'Hat_Root':         ((0.000,  0.000, 0.940), (0.000,  0.000, 1.020), 'Head',          False),
    'Hat_Tilt':         ((0.000,  0.000, 1.020), (0.000,  0.000, 1.110), 'Hat_Root',      True),

    # ── Left arm
    'LeftShoulder':     ((0.000,  0.000, 0.695), (-0.130, 0.000, 0.700), 'Chest',         False),
    'LeftUpperArm':     ((-0.130, 0.000, 0.700), (-0.330, 0.000, 0.688), 'LeftShoulder',  True),
    'LeftLowerArm':     ((-0.330, 0.000, 0.688), (-0.500, 0.000, 0.678), 'LeftUpperArm',  True),
    'LeftHand':         ((-0.500, 0.000, 0.678), (-0.575, 0.000, 0.674), 'LeftLowerArm',  True),
    # Torch grip
    'Torch_Hold':       ((-0.575, 0.000, 0.674), (-0.575, 0.000, 0.510), 'LeftHand',      False),

    # ── Right arm
    'RightShoulder':    ((0.000,  0.000, 0.695), (0.130,  0.000, 0.700), 'Chest',         False),
    'RightUpperArm':    ((0.130,  0.000, 0.700), (0.330,  0.000, 0.688), 'RightShoulder', True),
    'RightLowerArm':    ((0.330,  0.000, 0.688), (0.500,  0.000, 0.678), 'RightUpperArm', True),
    'RightHand':        ((0.500,  0.000, 0.678), (0.575,  0.000, 0.674), 'RightLowerArm', True),
    # Knife grip
    'Knife_Hold':       ((0.575,  0.000, 0.674), (0.575,  0.000, 0.340), 'RightHand',     False),

    # ── Left leg
    'LeftUpperLeg':     ((-0.095, 0.000, 0.420), (-0.095, 0.005, 0.220), 'Hips',          False),
    'LeftLowerLeg':     ((-0.095, 0.005, 0.220), (-0.095, 0.002, 0.045), 'LeftUpperLeg',  True),
    'LeftFoot':         ((-0.095, 0.002, 0.045), (-0.095, 0.100, 0.012), 'LeftLowerLeg',  True),
    'LeftToes':         ((-0.095, 0.100, 0.012), (-0.095, 0.155, 0.006), 'LeftFoot',      True),

    # ── Right leg
    'RightUpperLeg':    ((0.095,  0.000, 0.420), (0.095,  0.005, 0.220), 'Hips',          False),
    'RightLowerLeg':    ((0.095,  0.005, 0.220), (0.095,  0.002, 0.045), 'RightUpperLeg', True),
    'RightFoot':        ((0.095,  0.002, 0.045), (0.095,  0.100, 0.012), 'RightLowerLeg', True),
    'RightToes':        ((0.095,  0.100, 0.012), (0.095,  0.155, 0.006), 'RightFoot',     True),
}

IK_BONES = {
    'IK_Foot_L':    ((-0.095, 0.100, 0.012), (-0.095, 0.100, 0.110), 'Root'),
    'IK_Foot_R':    (( 0.095, 0.100, 0.012), ( 0.095, 0.100, 0.110), 'Root'),
    'IK_Hand_L':    ((-0.575, 0.000, 0.674), (-0.575, 0.000, 0.780), 'Root'),
    'IK_Hand_R':    (( 0.575, 0.000, 0.674), ( 0.575, 0.000, 0.780), 'Root'),
    'Pole_Knee_L':  ((-0.095, -0.380, 0.220),(-0.095, -0.380, 0.300), 'Root'),
    'Pole_Knee_R':  (( 0.095, -0.380, 0.220),( 0.095, -0.380, 0.300), 'Root'),
    'Pole_Elbow_L': ((-0.420, -0.300, 0.682),(-0.420, -0.300, 0.760), 'Root'),
    'Pole_Elbow_R': (( 0.420, -0.300, 0.682),( 0.420, -0.300, 0.760), 'Root'),
}


# ─────────────────────────────────────────────────────
#  BUILD ARMATURE
# ─────────────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('CompassNPC_Armature_Data')
    arm_obj  = bpy.data.objects.new('CompassNPC_Armature', arm_data)
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
        c.owner_space = 'LOCAL'
        c.use_limit_x=ux; c.min_x=math.radians(xn); c.max_x=math.radians(xx)
        c.use_limit_y=uy; c.min_y=math.radians(yn); c.max_y=math.radians(yx)
        c.use_limit_z=uz; c.min_z=math.radians(zn); c.max_z=math.radians(zx)

    # Spine
    for b in ['Spine','Chest']:
        lim(b, True,True,True, xn=-22,xx=28, yn=-18,yx=18, zn=-18,zx=18)
    lim('Neck', True,True,True, xn=-32,xx=32, yn=-28,yx=28, zn=-26,zx=26)
    lim('Head', True,True,True, xn=-40,xx=40, yn=-35,yx=35, zn=-30,zx=30)

    # Compass face — limited nod/tilt (it's a heavy head!)
    lim('CompassFace_Pivot', True,True,True,
        xn=-18,xx=18, yn=-15,yx=15, zn=-15,zx=15)
    # Compass rose — FREE spin on Z (the rose rotates!)
    lim('CompassRose_Spin', True,True,False,
        xn=-5,xx=5, yn=-5,yx=5)

    # Hat — can tilt forward (when running) or fly off
    lim('Hat_Root',  True,True,True, xn=-12,xx=12, yn=-10,yx=10, zn=-8,zx=8)
    lim('Hat_Tilt',  True,True,True, xn=-30,xx=15, yn=-20,yx=20, zn=-20,zx=20)

    # Arms
    for side in ('Left','Right'):
        s = -1 if side=='Left' else 1
        lim(f'{side}UpperArm', True,True,True,
            xn=-90,xx=165, yn=-55*s,yx=55*s, zn=-90,zx=90)
        lim(f'{side}LowerArm', True,False,True,
            xn=0,xx=145, zn=-5,zx=5)
        lim(f'{side}Hand', True,True,True,
            xn=-65,xx=65, yn=-28,yx=28, zn=-20,zx=20)

    # Legs
    for side in ('Left','Right'):
        lim(f'{side}UpperLeg', True,True,True,
            xn=-100,xx=48, yn=-40,yx=40, zn=-40,zx=40)
        lim(f'{side}LowerLeg', True,False,True,
            xn=-145,xx=0, zn=-5,zx=5)
        lim(f'{side}Foot', True,True,True,
            xn=-42,xx=30, yn=-14,yx=14, zn=-18,zx=18)

    object_mode()


# ─────────────────────────────────────────────────────
#  COMPASS ROSE SPIN DRIVER
#  Adds a rotation driver to CompassRose_Spin so it
#  continuously rotates — visible in viewport animations.
# ─────────────────────────────────────────────────────

def add_rose_spin_driver(arm_obj):
    """
    Drive CompassRose_Spin.rotation_euler.z with a 'frame' variable
    so the compass rose rotates as time advances.
    In Unity this bone is driven via Animator float 'RoseSpinSpeed'.
    """
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones
    if 'CompassRose_Spin' not in pb:
        object_mode(); return

    bone = pb['CompassRose_Spin']
    bone.rotation_mode = 'XYZ'

    # Add driver on Z rotation
    fc = arm_obj.animation_data_create()
    data_path = f'pose.bones["CompassRose_Spin"].rotation_euler'
    try:
        drv = arm_obj.driver_add(data_path, 2)   # index 2 = Z
        drv.driver.type = 'SCRIPTED'
        drv.driver.expression = 'frame * 0.04'   # ~2.3 deg per frame
    except Exception as e:
        print(f"[CompassRig] Driver note: {e}")

    object_mode()


# ─────────────────────────────────────────────────────
#  BONE COLORS
# ─────────────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    spine_bns  = ['Root','Hips','Spine','Chest','Neck','Head']
    compass_bns= ['CompassFace_Pivot','CompassRose_Spin','Hat_Root','Hat_Tilt']
    weapon_bns = ['Torch_Hold','Knife_Hold']
    left_bns   = [n for n in BONES if n.startswith('Left')]
    right_bns  = [n for n in BONES if n.startswith('Right')]
    ik_bns     = list(IK_BONES.keys())

    for b in spine_bns:
        if b in pb: pb[b].color.palette = 'THEME01'   # red
    for b in compass_bns:
        if b in pb: pb[b].color.palette = 'THEME09'   # yellow — compass special
    for b in weapon_bns:
        if b in pb: pb[b].color.palette = 'THEME08'   # orange — weapon bones
    for b in left_bns:
        if b in pb: pb[b].color.palette = 'THEME04'   # green
    for b in right_bns:
        if b in pb: pb[b].color.palette = 'THEME03'   # blue
    for b in ik_bns:
        if b in pb: pb[b].color.palette = 'THEME10'   # cyan

    object_mode()


# ─────────────────────────────────────────────────────
#  BIND MESHES TO ARMATURE
# ─────────────────────────────────────────────────────

BONE_PARENT_MAP = {
    # Rigid bone-parented objects
    'CompassHead_Rim'      : 'CompassFace_Pivot',
    'CompassHead_Face'     : 'CompassFace_Pivot',
    'CompassHead_Rose'     : 'CompassRose_Spin',
    'CompassHead_Needle_Red'  : 'CompassRose_Spin',
    'CompassHead_Needle_Blue' : 'CompassRose_Spin',
    'CompassHead_Eye_L'    : 'CompassFace_Pivot',
    'CompassHead_Eye_R'    : 'CompassFace_Pivot',
    'CompassHead_EyeShine_L': 'CompassFace_Pivot',
    'CompassHead_EyeShine_R': 'CompassFace_Pivot',
    'CompassHead_Beak'     : 'CompassFace_Pivot',
    'CompassHead_Ring'     : 'CompassFace_Pivot',
    'Hat'                  : 'Hat_Root',
    'Hat_Band'             : 'Hat_Root',
    'Torch_Handle'         : 'Torch_Hold',
    'Torch_Head'           : 'Torch_Hold',
    'Torch_Flame'          : 'Torch_Hold',
    'Knife_Blade'          : 'Knife_Hold',
    'Knife_Handle'         : 'Knife_Hold',
    'Knife_Guard'          : 'Knife_Hold',
}

SKIN_MESHES = [
    'Jacket_Body', 'Arm_L', 'Arm_R', 'Hand_L', 'Hand_R',
    'Belt', 'Belt_Buckle',
    'Belt_Pouch_0', 'Belt_Pouch_1', 'Belt_Pouch_2',
    'Leg_L', 'Leg_R', 'Boot_L', 'Boot_R',
    'Backpack', 'Map_Scroll',
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
        obj.parent      = arm_obj
        obj.parent_type = 'BONE'
        obj.parent_bone = bone_name

    # Potion bottles — bone parent to hips
    for pname in ['Potion_-12', 'Potion_12']:
        obj = bpy.data.objects.get(pname)
        if obj is None: continue
        obj.parent = arm_obj; obj.parent_type='BONE'; obj.parent_bone='Hips'

    # Auto-weight skinned meshes
    skin_objs = [bpy.data.objects.get(n) for n in SKIN_MESHES
                 if bpy.data.objects.get(n)]
    if skin_objs:
        bpy.ops.object.select_all(action='DESELECT')
        for o in skin_objs: o.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')


# ─────────────────────────────────────────────────────
#  ATTACH TO COLLECTION ROOT
# ─────────────────────────────────────────────────────

def attach_to_root(arm_obj):
    root = bpy.data.objects.get('CompassNPC_ROOT')
    if root:
        arm_obj.parent = root
        print("[CompassRig] Armature parented to CompassNPC_ROOT.")
    col = bpy.data.collections.get('IsleTrial_CompassNPC')
    if col and arm_obj.name not in col.objects:
        for c in list(arm_obj.users_collection): c.objects.unlink(arm_obj)
        col.objects.link(arm_obj)


# ─────────────────────────────────────────────────────
#  REPORT
# ─────────────────────────────────────────────────────

def print_report(arm_obj):
    print("\n" + "="*65)
    print("  IsleTrial — Compass NPC Rig Report")
    print("="*65)
    total  = len(arm_obj.data.bones)
    deform = sum(1 for b in arm_obj.data.bones if b.use_deform)
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
    print("    CompassFace_Pivot  → whole compass head rigid attach")
    print("    CompassRose_Spin   → rose/needle spin (Blender driver: frame*0.04)")
    print("    Hat_Root           → hat base (physics parent)")
    print("    Hat_Tilt           → hat tilt/fly-off animation")
    print("    Torch_Hold         → torch grip + flame child")
    print("    Knife_Hold         → knife grip transform")
    print("\n  Unity Animator params to expose:")
    print("    RoseSpinSpeed  (Float)   → CompassRose_Spin.rotation.z")
    print("    HatTilt        (Float)   → Hat_Tilt.rotation.x")
    print("    TorchFlicker   (Float)   → scale Torch_Flame Z")
    print("    KnifeSlash     (Trigger) → right arm slash clip")
    print("\n  Export: select CompassNPC_ROOT → FBX")
    print("  Unity: Rig → Humanoid | Avatar: Create From This Model")
    print("="*65 + "\n")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def main():
    print("\n[CompassRig] Building armature...")
    arm_obj = build_armature()

    print("[CompassRig] Setting up IK...")
    setup_ik(arm_obj)

    print("[CompassRig] Setting rotation limits...")
    setup_limits(arm_obj)

    print("[CompassRig] Adding compass rose spin driver...")
    add_rose_spin_driver(arm_obj)

    print("[CompassRig] Binding meshes...")
    bind_meshes(arm_obj)

    print("[CompassRig] Colouring bones...")
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
