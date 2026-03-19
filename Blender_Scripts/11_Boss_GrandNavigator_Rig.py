"""
IsleTrial – Boss 02 RIG: Grand Navigator
==========================================
Run AFTER 11_Boss_GrandNavigator.py.
Generic armature with:
  • Spine / head chain
  • 2 primary arms with IK (+ pole targets)
  • 2 secondary instrument arms with IK
  • Gear-joint knees (leg IK)
  • CompassFace_Pivot  (head yaw for beam ability)
  • CompassRose_Spin   (continuous rotation driver)
  • OrreryRing_1/2/3   (gyroscope spin bones)
  • TelescopeElev      (aim up/down)
  • GearStorm_L/R      (spinning attack empties)
"""

import bpy, math
from mathutils import Vector

def get_root():
    return bpy.data.objects.get('Boss_GrandNavigator_ROOT')

def new_arm(name):
    d=bpy.data.armatures.new(name)
    o=bpy.data.objects.new(name,d)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    return o

def edit_mode(ao):
    bpy.context.view_layer.objects.active=ao
    bpy.ops.object.mode_set(mode='EDIT')
    return ao.data.edit_bones

def pose_mode(ao):
    bpy.context.view_layer.objects.active=ao
    bpy.ops.object.mode_set(mode='POSE')
    return ao.pose.bones

def obj_mode(): bpy.ops.object.mode_set(mode='OBJECT')

def add_bone(eb,name,head,tail,par=None,conn=False):
    b=eb.new(name); b.head=Vector(head); b.tail=Vector(tail)
    if par and par in eb: b.parent=eb[par]; b.use_connect=conn
    return b

def add_ik(pb,bone,tgt,sub,chain,pole=None,psub=None,pang=0):
    c=pb[bone].constraints.new('IK')
    c.target=tgt; c.subtarget=sub; c.chain_count=chain
    if pole: c.pole_target=tgt; c.pole_subtarget=psub; c.pole_angle=math.radians(pang)

def lim_rot(pb,name,minx=-45,maxx=45,miny=-30,maxy=30,minz=-45,maxz=45,uy=False):
    b=pb.get(name);
    if not b: return
    c=b.constraints.new('LIMIT_ROTATION'); c.owner_space='LOCAL'
    c.use_limit_x=True; c.min_x=math.radians(minx); c.max_x=math.radians(maxx)
    c.use_limit_y=uy; c.min_y=math.radians(miny); c.max_y=math.radians(maxy)
    c.use_limit_z=True; c.min_z=math.radians(minz); c.max_z=math.radians(maxz)

def col_bone(pb,name,theme):
    b=pb.get(name);
    if b: b.color.palette=theme

BONES={
    'Root':          ((0,0,0),(0,0,0.06),None,False,False),
    'Pelvis':        ((0,0,1.35),(0,0,1.65),'Root',False,True),
    'Spine1':        ((0,0,1.65),(0,0,1.95),'Pelvis',True,True),
    'Spine2':        ((0,0,1.95),(0,0,2.30),'Spine1',True,True),
    'Chest':         ((0,0,2.30),(0,0,2.70),'Spine2',True,True),
    'Neck':          ((0,0,2.70),(0,0,2.90),'Chest',False,True),
    'Head':          ((0,0,2.90),(0,0,3.20),'Neck',True,True),
    # Compass head sub-bones
    'CompassFace_Pivot':((0,0,3.05),(0,0,3.20),'Head',False,True),
    'CompassRose_Spin': ((0,-0.06,3.05),(0,-0.06,3.20),'CompassFace_Pivot',False,True),
    # Legs
    'Thigh_R':       ((0.32,0,1.55),(0.32,0,0.65),'Pelvis',False,True),
    'Shin_R':        ((0.32,0,0.65),(0.32,0,0.18),'Thigh_R',True,True),
    'Foot_R':        ((0.32,0,-0.14),(0.32,0.25,-0.14),'Shin_R',False,True),
    'Thigh_L':       ((-0.32,0,1.55),(-0.32,0,0.65),'Pelvis',False,True),
    'Shin_L':        ((-0.32,0,0.65),(-0.32,0,0.18),'Thigh_L',True,True),
    'Foot_L':        ((-0.32,0,-0.14),(-0.32,0.25,-0.14),'Shin_L',False,True),
    # Primary arms
    'Shoulder_R':    ((0.58,0,2.55),(0.70,0,2.55),'Chest',False,False),
    'UpperArm_R':    ((0.70,0,2.55),(1.25,-0.10,2.30),'Shoulder_R',False,True),
    'ForeArm_R':     ((1.25,-0.10,2.30),(1.90,-0.35,1.90),'UpperArm_R',True,True),
    'Hand_R':        ((1.90,-0.35,1.90),(2.20,-0.55,1.65),'ForeArm_R',True,True),
    'Shoulder_L':    ((-0.58,0,2.55),(-0.70,0,2.55),'Chest',False,False),
    'UpperArm_L':    ((-0.70,0,2.55),(-1.25,-0.10,2.30),'Shoulder_L',False,True),
    'ForeArm_L':     ((-1.25,-0.10,2.30),(-1.90,-0.35,1.90),'UpperArm_L',True,True),
    'Hand_L':        ((-1.90,-0.35,1.90),(-2.20,-0.55,1.65),'ForeArm_L',True,True),
    # Secondary instrument arms
    'InstrSh_R':     ((0.50,0,2.00),(0.60,0,2.00),'Chest',False,False),
    'InstrArm_R':    ((0.60,0,2.00),(1.15,0.20,1.70),'InstrSh_R',False,True),
    'InstrFore_R':   ((1.15,0.20,1.70),(1.65,0.50,1.45),'InstrArm_R',True,True),
    'TelescopeElev': ((1.65,0.50,1.45),(1.90,0.65,1.45),'InstrFore_R',True,True),
    'InstrSh_L':     ((-0.50,0,2.00),(-0.60,0,2.00),'Chest',False,False),
    'InstrArm_L':    ((-0.60,0,2.00),(-1.15,0.20,1.70),'InstrSh_L',False,True),
    'InstrFore_L':   ((-1.15,0.20,1.70),(-1.65,0.50,1.45),'InstrArm_L',True,True),
    # Orrery bones
    'OrreryMount':   ((0,0.42,2.25),(0,0.55,2.25),'Chest',False,False),
    'OrreryRing1':   ((0,0.48,2.25),(0,0.48,2.45),'OrreryMount',False,True),
    'OrreryRing2':   ((0,0.48,2.25),(0,0.48,2.45),'OrreryMount',False,True),
    'OrreryRing3':   ((0,0.48,2.25),(0,0.48,2.45),'OrreryMount',False,True),
}

IK_BONES={
    'IK_Hand_R':    ((2.20,-0.55,1.65),(2.20,-0.55,1.80),'Root'),
    'IK_Hand_L':    ((-2.20,-0.55,1.65),(-2.20,-0.55,1.80),'Root'),
    'IK_Instr_R':   ((1.65,0.50,1.45),(1.65,0.50,1.60),'Root'),
    'IK_Instr_L':   ((-1.65,0.50,1.45),(-1.65,0.50,1.60),'Root'),
    'IK_Foot_R':    ((0.32,0.25,-0.14),(0.32,0.25,0.08),'Root'),
    'IK_Foot_L':    ((-0.32,0.25,-0.14),(-0.32,0.25,0.08),'Root'),
    'Pole_Arm_R':   ((1.10,0.80,2.30),(1.10,0.90,2.30),'Root'),
    'Pole_Arm_L':   ((-1.10,0.80,2.30),(-1.10,0.90,2.30),'Root'),
    'Pole_Knee_R':  ((0.32,-0.60,0.65),(0.32,-0.70,0.65),'Root'),
    'Pole_Knee_L':  ((-0.32,-0.60,0.65),(-0.32,-0.70,0.65),'Root'),
}

def add_rose_driver(arm_obj):
    """Continuous compass rose spin."""
    obj_mode()
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active=arm_obj
    # Access pose bone and add rotation Z driver
    pb=arm_obj.pose.bones.get('CompassRose_Spin')
    if not pb: return
    pb.rotation_mode='XYZ'
    drv=pb.driver_add('rotation_euler',2).driver
    drv.type='SCRIPTED'
    drv.expression='frame*0.045'  # degrees per frame → adjust in Unity
    v=drv.variables.new(); v.name='frame'
    v.targets[0].id_type='SCENE'; v.targets[0].id=bpy.context.scene

def build_rig():
    ao=new_arm('GN_Armature')
    eb=edit_mode(ao)
    for name,(head,tail,par,conn,_) in BONES.items():
        add_bone(eb,name,head,tail,par,conn)
    for name,(head,tail,par) in IK_BONES.items():
        b=eb.new(name); b.head=Vector(head); b.tail=Vector(tail)
        if par in eb: b.parent=eb[par]
        b.use_deform=False
    obj_mode()
    pb=pose_mode(ao)
    # IK
    add_ik(pb,'ForeArm_R',  ao,'IK_Hand_R', 2,pole='Pole_Arm_R',psub='Pole_Arm_R',pang=-90)
    add_ik(pb,'ForeArm_L',  ao,'IK_Hand_L', 2,pole='Pole_Arm_L',psub='Pole_Arm_L',pang=-90)
    add_ik(pb,'InstrFore_R',ao,'IK_Instr_R',2)
    add_ik(pb,'InstrFore_L',ao,'IK_Instr_L',2)
    add_ik(pb,'Shin_R',     ao,'IK_Foot_R', 2,pole='Pole_Knee_R',psub='Pole_Knee_R',pang=90)
    add_ik(pb,'Shin_L',     ao,'IK_Foot_L', 2,pole='Pole_Knee_L',psub='Pole_Knee_L',pang=90)
    # Limits
    lim_rot(pb,'Spine1',   minx=-20,maxx=25)
    lim_rot(pb,'Spine2',   minx=-15,maxx=30)
    lim_rot(pb,'Neck',     minx=-25,maxx=30)
    lim_rot(pb,'Head',     minx=-25,maxx=35,minz=-40,maxz=40)
    lim_rot(pb,'CompassFace_Pivot', minx=-15,maxx=15,minz=-80,maxz=80)
    lim_rot(pb,'TelescopeElev',     minx=-50,maxx=30,minz=0,maxz=0)
    lim_rot(pb,'Thigh_R',  minx=-80,maxx=50)
    lim_rot(pb,'Thigh_L',  minx=-80,maxx=50)
    lim_rot(pb,'Shin_R',   minx=-120,maxx=0,minz=0,maxz=0)
    lim_rot(pb,'Shin_L',   minx=-120,maxx=0,minz=0,maxz=0)
    # Colours
    spine=['Root','Pelvis','Spine1','Spine2','Chest','Neck','Head']
    for n in spine: col_bone(pb,n,'THEME04')
    for n in ['CompassFace_Pivot','CompassRose_Spin']: col_bone(pb,n,'THEME07')
    for n in ['Shoulder_R','UpperArm_R','ForeArm_R','Hand_R']: col_bone(pb,n,'THEME01')
    for n in ['Shoulder_L','UpperArm_L','ForeArm_L','Hand_L']: col_bone(pb,n,'THEME03')
    for n in ['InstrSh_R','InstrArm_R','InstrFore_R','TelescopeElev']: col_bone(pb,n,'THEME09')
    for n in ['InstrSh_L','InstrArm_L','InstrFore_L']: col_bone(pb,n,'THEME10')
    for n in ['Thigh_R','Shin_R','Foot_R','Thigh_L','Shin_L','Foot_L']: col_bone(pb,n,'THEME05')
    for n in ['OrreryMount','OrreryRing1','OrreryRing2','OrreryRing3']: col_bone(pb,n,'THEME14')
    for n in list(IK_BONES.keys()): col_bone(pb,n,'THEME08')
    obj_mode()
    return ao

def bind_meshes(arm_obj):
    root_e=bpy.data.objects.get('Boss_GrandNavigator_ROOT')
    if not root_e: print("  ROOT not found – run model script first."); return
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.type=='MESH' and o.parent==root_e:
            o.select_set(True)
    bpy.context.view_layer.objects.active=arm_obj; arm_obj.select_set(True)
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    bpy.ops.object.select_all(action='DESELECT')
    root_e.parent=arm_obj; root_e.parent_type='BONE'; root_e.parent_bone='Root'

def main():
    ao=build_rig()
    bind_meshes(ao)
    add_rose_driver(ao)
    col=bpy.data.collections.get('IsleTrial_Boss_GrandNavigator')
    if col and ao.name not in col.objects:
        col.objects.link(ao)
        if ao.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(ao)
    print("[IsleTrial] Boss Grand Navigator RIG built.")
    print("  Bones:", len(ao.data.bones))
    print("  Ability bones: CompassFace_Pivot, CompassRose_Spin (driver), TelescopeElev, OrreryRings x3")

main()
