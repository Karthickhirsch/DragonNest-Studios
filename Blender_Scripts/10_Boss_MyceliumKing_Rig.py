"""
IsleTrial – Boss 01 RIG: Mycelium King
========================================
Run AFTER 10_Boss_MyceliumKing.py.
Adds a Generic armature with:
  • Full body spine / head
  • 4-arm chains (2 upper humanoid + 2 root-tendril)
  • MushroomCap_Sway chain
  • SporeCannonPitch bone
  • Spore-sac deform bones
  • IK targets for all 4 hand/tendril tips
  • Root-stomp ability empties
"""

import bpy, math
from mathutils import Vector

# ─── helpers ────────────────────────────────────────────────────────────────

def get_arm():
    for obj in bpy.context.scene.objects:
        if obj.name == 'Boss_MyceliumKing_ROOT':
            return obj
    return None

def new_armature(name):
    arm_data = bpy.data.armatures.new(name)
    arm_obj  = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)
    return arm_obj

def edit_mode(arm_obj):
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    return arm_obj.data.edit_bones

def pose_mode(arm_obj):
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    return arm_obj.pose.bones

def object_mode():
    bpy.ops.object.mode_set(mode='OBJECT')

def add_bone(edit_bones, name, head, tail, parent_name=None, connected=False):
    b = edit_bones.new(name)
    b.head = Vector(head); b.tail = Vector(tail)
    if parent_name and parent_name in edit_bones:
        b.parent = edit_bones[parent_name]
        b.use_connect = connected
    return b

def add_ik(pose_bones, bone_name, target_obj, subtarget, chain_count, pole=None, pole_sub=None, pole_angle=0):
    pb = pose_bones[bone_name]
    c = pb.constraints.new('IK')
    c.target = target_obj; c.subtarget = subtarget
    c.chain_count = chain_count
    if pole:
        c.pole_target = target_obj; c.pole_subtarget = pole_sub
        c.pole_angle = math.radians(pole_angle)

def limit_rot(pose_bones, bone_name, use_x=True, use_y=False, use_z=True,
              minx=-45, maxx=45, miny=-30, maxy=30, minz=-45, maxz=45):
    pb = pose_bones.get(bone_name)
    if not pb: return
    c = pb.constraints.new('LIMIT_ROTATION')
    c.owner_space = 'LOCAL'
    c.use_limit_x = use_x; c.min_x = math.radians(minx); c.max_x = math.radians(maxx)
    c.use_limit_y = use_y; c.min_y = math.radians(miny); c.max_y = math.radians(maxy)
    c.use_limit_z = use_z; c.min_z = math.radians(minz); c.max_z = math.radians(maxz)

def color_bone(pose_bones, name, theme):
    pb = pose_bones.get(name)
    if not pb: return
    pb.color.palette = theme

# ─── bone tables ─────────────────────────────────────────────────────────────
# (head_xyz, tail_xyz, parent, connected, deform)

BONES = {
    # ── Core spine
    'Root':         ((0.000, 0.000, 0.000), (0.000, 0.000, 0.060), None,          False, False),
    'Pelvis':       ((0.000, 0.000, 0.700), (0.000, 0.000, 1.000), 'Root',        False, True),
    'Spine1':       ((0.000, 0.000, 1.000), (0.000, 0.000, 1.400), 'Pelvis',      True,  True),
    'Spine2':       ((0.000, 0.000, 1.400), (0.000, 0.000, 1.850), 'Spine1',      True,  True),
    'Chest':        ((0.000, 0.000, 1.850), (0.000, 0.000, 2.350), 'Spine2',      True,  True),
    'Neck':         ((0.000, 0.000, 2.800), (0.000, 0.000, 3.050), 'Chest',       False, True),
    'Head':         ((0.000, 0.000, 3.050), (0.000, 0.000, 3.350), 'Neck',        True,  True),

    # ── Mushroom cap chain
    'MushroomCap_Root': ((0.000, 0.000, 3.350),(0.000, 0.000, 3.650),'Head',        False, True),
    'MushroomCap_Sway': ((0.000, 0.000, 3.650),(0.000, 0.000, 4.200),'MushroomCap_Root',True, True),

    # ── Upper arms (R/L) – humanoid style
    'UpperShoulder_R': ((0.580, 0.000, 2.550),(0.700, 0.000, 2.550),'Chest',       False, False),
    'UpperArm_R':      ((0.700, 0.000, 2.550),(1.200,-0.100, 2.350),'UpperShoulder_R',False,True),
    'UpperForeArm_R':  ((1.200,-0.100, 2.350),(1.850,-0.300, 2.000),'UpperArm_R',  True,  True),
    'UpperHand_R':     ((1.850,-0.300, 2.000),(2.150,-0.450, 1.780),'UpperForeArm_R',True,True),

    'UpperShoulder_L': ((-0.580, 0.000, 2.550),(-0.700, 0.000, 2.550),'Chest',    False, False),
    'UpperArm_L':      ((-0.700, 0.000, 2.550),(-1.200,-0.100, 2.350),'UpperShoulder_L',False,True),
    'UpperForeArm_L':  ((-1.200,-0.100, 2.350),(-1.850,-0.300, 2.000),'UpperArm_L',True, True),
    'UpperHand_L':     ((-1.850,-0.300, 2.000),(-2.150,-0.450, 1.780),'UpperForeArm_L',True,True),

    # ── Lower root-tendril arms
    'RootArm_R':       ((0.500, 0.000, 1.900),(1.000, 0.150, 1.600),'Spine2',     False, True),
    'RootForeArm_R':   ((1.000, 0.150, 1.600),(1.550, 0.350, 1.200),'RootArm_R',  True,  True),
    'RootTip_R':       ((1.550, 0.350, 1.200),(1.900, 0.400, 0.800),'RootForeArm_R',True,True),

    'RootArm_L':       ((-0.500, 0.000, 1.900),(-1.000, 0.150, 1.600),'Spine2',   False, True),
    'RootForeArm_L':   ((-1.000, 0.150, 1.600),(-1.550, 0.350, 1.200),'RootArm_L',True,  True),
    'RootTip_L':       ((-1.550, 0.350, 1.200),(-1.900, 0.400, 0.800),'RootForeArm_L',True,True),

    # ── Spore cannon (right shoulder mount)
    'SporeCannonMount': ((0.620,-0.250, 2.680),(0.700,-0.350, 2.750),'Chest',      False, False),
    'SporeCannonPitch': ((0.700,-0.350, 2.750),(0.900,-0.650, 2.900),'SporeCannonMount',True,True),

    # ── Spore sac deform (chest + sides)
    'SporeSac_C':  ((0.000,-0.300, 2.400),(0.000,-0.300, 2.650),'Chest',          False, True),
    'SporeSac_R':  ((0.520, 0.000, 1.750),(0.620, 0.000, 1.900),'Spine2',         False, True),
    'SporeSac_L':  ((-0.520, 0.000, 1.750),(-0.620, 0.000, 1.900),'Spine2',       False, True),
}

IK_BONES = {
    # (head, tail, parent)
    'IK_UpperHand_R': ((2.150,-0.450, 1.780),(2.150,-0.450, 1.900),'Root'),
    'IK_UpperHand_L': ((-2.150,-0.450,1.780),(-2.150,-0.450,1.900),'Root'),
    'IK_RootTip_R':   ((1.900, 0.400, 0.800),(1.900, 0.400, 0.950),'Root'),
    'IK_RootTip_L':   ((-1.900,0.400, 0.800),(-1.900,0.400, 0.950),'Root'),
    'Pole_UpperArm_R':((1.100, 0.800, 2.350),(1.100, 0.900, 2.350),'Root'),
    'Pole_UpperArm_L':((-1.100,0.800, 2.350),(-1.100,0.900, 2.350),'Root'),
    'Pole_RootArm_R': ((1.200, 1.100, 1.400),(1.200, 1.200, 1.400),'Root'),
    'Pole_RootArm_L': ((-1.200,1.100, 1.400),(-1.200,1.200,1.400),'Root'),
}

# ─── build ───────────────────────────────────────────────────────────────────

def build_rig():
    arm_obj = new_armature('MK_Armature')
    eb = edit_mode(arm_obj)

    for name,(head,tail,par,conn,_) in BONES.items():
        add_bone(eb, name, head, tail, par, conn)
    for name,(head,tail,par) in IK_BONES.items():
        b = eb.new(name)
        b.head = Vector(head); b.tail = Vector(tail)
        if par in eb: b.parent = eb[par]
        b.use_deform = False

    object_mode()
    pb = pose_mode(arm_obj)

    # IK constraints
    add_ik(pb, 'UpperForeArm_R', arm_obj, 'IK_UpperHand_R', 2, pole='Pole_UpperArm_R', pole_sub='Pole_UpperArm_R', pole_angle=-90)
    add_ik(pb, 'UpperForeArm_L', arm_obj, 'IK_UpperHand_L', 2, pole='Pole_UpperArm_L', pole_sub='Pole_UpperArm_L', pole_angle=-90)
    add_ik(pb, 'RootForeArm_R',  arm_obj, 'IK_RootTip_R',   2, pole='Pole_RootArm_R',  pole_sub='Pole_RootArm_R',  pole_angle=90)
    add_ik(pb, 'RootForeArm_L',  arm_obj, 'IK_RootTip_L',   2, pole='Pole_RootArm_L',  pole_sub='Pole_RootArm_L',  pole_angle=90)

    # Rotation limits
    limit_rot(pb, 'Spine1',      minx=-25,maxx=25)
    limit_rot(pb, 'Spine2',      minx=-20,maxx=35)
    limit_rot(pb, 'Neck',        minx=-30,maxx=45)
    limit_rot(pb, 'Head',        minx=-30,maxx=30,minz=-40,maxz=40)
    limit_rot(pb, 'MushroomCap_Sway', minx=-20,maxx=20,minz=-20,maxz=20)
    limit_rot(pb, 'SporeCannonPitch', minx=-40,maxx=20,use_z=False)
    limit_rot(pb, 'UpperArm_R',  minx=-90,maxx=90,minz=-60,maxz=60)
    limit_rot(pb, 'UpperArm_L',  minx=-90,maxx=90,minz=-60,maxz=60)
    limit_rot(pb, 'RootArm_R',   minx=-60,maxx=60,minz=-45,maxz=45)
    limit_rot(pb, 'RootArm_L',   minx=-60,maxx=60,minz=-45,maxz=45)

    # Bone colour themes
    spine_bones = ['Root','Pelvis','Spine1','Spine2','Chest','Neck','Head']
    cap_bones   = ['MushroomCap_Root','MushroomCap_Sway']
    arm_r_bones = ['UpperShoulder_R','UpperArm_R','UpperForeArm_R','UpperHand_R']
    arm_l_bones = ['UpperShoulder_L','UpperArm_L','UpperForeArm_L','UpperHand_L']
    root_r      = ['RootArm_R','RootForeArm_R','RootTip_R']
    root_l      = ['RootArm_L','RootForeArm_L','RootTip_L']
    cannon_b    = ['SporeCannonMount','SporeCannonPitch']
    ik_bones_list = list(IK_BONES.keys())

    for n in spine_bones: color_bone(pb, n, 'THEME04')  # yellow
    for n in cap_bones:   color_bone(pb, n, 'THEME06')  # green
    for n in arm_r_bones: color_bone(pb, n, 'THEME01')  # red
    for n in arm_l_bones: color_bone(pb, n, 'THEME03')  # blue
    for n in root_r:      color_bone(pb, n, 'THEME09')  # orange
    for n in root_l:      color_bone(pb, n, 'THEME10')  # teal
    for n in cannon_b:    color_bone(pb, n, 'THEME07')  # purple
    for n in ik_bones_list: color_bone(pb, n, 'THEME14') # grey

    object_mode()
    return arm_obj

def bind_meshes(arm_obj):
    """Parent all mesh objects (and sub-empties) to armature."""
    root_empty = bpy.data.objects.get('Boss_MyceliumKing_ROOT')
    if not root_empty:
        print("  WARNING: ROOT empty not found – run 10_Boss_MyceliumKing.py first.")
        return
    bpy.ops.object.select_all(action='DESELECT')
    meshes = [o for o in bpy.context.scene.objects
              if o.type == 'MESH' and o.parent == root_empty]
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    bpy.ops.object.select_all(action='DESELECT')

    # Parent root empty to armature root bone
    root_empty.parent = arm_obj
    root_empty.parent_type = 'BONE'
    root_empty.parent_bone = 'Root'

def main():
    arm = build_rig()
    bind_meshes(arm)
    # Link into collection
    col = bpy.data.collections.get('IsleTrial_Boss_MyceliumKing')
    if col and arm.name not in col.objects:
        col.objects.link(arm)
        if arm.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(arm)
    print("[IsleTrial] Boss Mycelium King RIG built.")
    print("  Bones:", len(arm.data.bones))
    print("  IK chains: 4 (upper arms + root arms)")
    print("  Ability bones: SporeCannonPitch, MushroomCap_Sway, SporeSac x3")

main()
