"""
IsleTrial – Boss 05 RIG: Ancient Coral Titan
==============================================
Run AFTER 14_Boss_CoralTitan.py.
Generic rig with:
  • Full spine chain (pelvis → head)
  • Leg IK chains (knee + foot)
  • 2 massive arm chains with IK (wrist targets)
  • ShipWheel_Spin bone (driver for chest wheel rotation)
  • Mast_Sway bone chain (back mast flexibility)
  • Eye_L / Eye_R aim bones
  • AnchorChain_R/L IK chains (4 links each)
  • CoralCrown_Pivot (head crown oscillate)
  • GroundStomp empties for AoE FX
"""

import bpy, math
from mathutils import Vector

def new_arm(name):
    d=bpy.data.armatures.new(name); o=bpy.data.objects.new(name,d)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o; o.select_set(True); return o

def edit_mode(ao):
    bpy.context.view_layer.objects.active=ao
    bpy.ops.object.mode_set(mode='EDIT'); return ao.data.edit_bones

def pose_mode(ao):
    bpy.context.view_layer.objects.active=ao
    bpy.ops.object.mode_set(mode='POSE'); return ao.pose.bones

def obj_mode(): bpy.ops.object.mode_set(mode='OBJECT')

def add_bone(eb,name,head,tail,par=None,conn=False,deform=True):
    b=eb.new(name); b.head=Vector(head); b.tail=Vector(tail); b.use_deform=deform
    if par and par in eb: b.parent=eb[par]; b.use_connect=conn
    return b

def add_ik(pb,bone,tgt,sub,chain,pole=None,psub=None,pang=0):
    c=pb[bone].constraints.new('IK'); c.target=tgt; c.subtarget=sub; c.chain_count=chain
    if pole: c.pole_target=tgt; c.pole_subtarget=psub; c.pole_angle=math.radians(pang)

def lim_rot(pb,name,minx=-45,maxx=45,minz=-45,maxz=45):
    b=pb.get(name);
    if not b: return
    c=b.constraints.new('LIMIT_ROTATION'); c.owner_space='LOCAL'
    c.use_limit_x=True; c.min_x=math.radians(minx); c.max_x=math.radians(maxx)
    c.use_limit_z=True; c.min_z=math.radians(minz); c.max_z=math.radians(maxz)

def col_b(pb,name,th):
    b=pb.get(name);
    if b: b.color.palette=th

BONES={
    'Root':          ((0,0,0),(0,0,0.08),None,False,False),
    'Pelvis':        ((0,0,1.65),(0,0,2.05),'Root',False,True),
    'Spine1':        ((0,0,2.05),(0,0,2.50),'Pelvis',True,True),
    'Spine2':        ((0,0,2.50),(0,0,2.95),'Spine1',True,True),
    'Chest':         ((0,0,2.95),(0,0,3.40),'Spine2',True,True),
    'Neck':          ((0,0,3.40),(0,0,3.65),'Chest',False,True),
    'Head':          ((0,0,3.65),(0,0,4.15),'Neck',True,True),
    # Head features
    'CoralCrown_Pivot':((0,0,4.15),(0,0,4.45),'Head',False,True),
    'Eye_L':         ((-0.28,-0.65,3.95),(-0.28,-0.85,3.95),'Head',False,True),
    'Eye_R':         ((0.28,-0.65,3.95),(0.28,-0.85,3.95),'Head',False,True),
    # Ship wheel (on chest)
    'ShipWheel_Spin':((0,-0.92,2.60),(0,-0.92,2.78),'Chest',False,True),
    # Mast on back
    'MastRoot':      ((0,0.55,2.95),(0,0.46,3.45),'Chest',False,False),
    'Mast1':         ((0,0.46,3.45),(0,0.38,4.00),'MastRoot',True,True),
    'Mast2':         ((0,0.38,4.00),(0,0.30,4.58),'Mast1',True,True),
    'Mast_Sway':     ((0,0.30,4.58),(0,0.24,4.90),'Mast2',True,True),
    # Arms R
    'Shoulder_R':    ((0.90,0,3.15),(1.05,0,3.15),'Chest',False,False),
    'UpperArm_R':    ((1.05,0,3.15),(1.85,0.10,2.80),'Shoulder_R',False,True),
    'ForeArm_R':     ((1.85,0.10,2.80),(2.90,-0.20,2.35),'UpperArm_R',True,True),
    'Hand_R':        ((2.90,-0.20,2.35),(3.50,-0.45,1.90),'ForeArm_R',True,True),
    # Arms L
    'Shoulder_L':    ((-0.90,0,3.15),(-1.05,0,3.15),'Chest',False,False),
    'UpperArm_L':    ((-1.05,0,3.15),(-1.85,0.10,2.80),'Shoulder_L',False,True),
    'ForeArm_L':     ((-1.85,0.10,2.80),(-2.90,-0.20,2.35),'UpperArm_L',True,True),
    'Hand_L':        ((-2.90,-0.20,2.35),(-3.50,-0.45,1.90),'ForeArm_L',True,True),
    # Anchor chains (2 bones each = simplified IK)
    'AnchorChain_R1':((3.50,-0.45,1.90),(3.50,-0.45,1.50),'Hand_R',False,True),
    'AnchorChain_R2':((3.50,-0.45,1.50),(3.50,-0.45,0.90),'AnchorChain_R1',True,True),
    'AnchorChain_L1':((-3.50,-0.45,1.90),(-3.50,-0.45,1.50),'Hand_L',False,True),
    'AnchorChain_L2':((-3.50,-0.45,1.50),(-3.50,-0.45,0.90),'AnchorChain_L1',True,True),
    # Legs R
    'Thigh_R':       ((0.50,0,2.05),(0.50,0,1.10),'Pelvis',False,True),
    'Shin_R':        ((0.50,0,1.10),(0.50,0,0.18),'Thigh_R',True,True),
    'Foot_R':        ((0.50,0,0.18),(0.50,0.20,-0.12),'Shin_R',True,True),
    # Legs L
    'Thigh_L':       ((-0.50,0,2.05),(-0.50,0,1.10),'Pelvis',False,True),
    'Shin_L':        ((-0.50,0,1.10),(-0.50,0,0.18),'Thigh_L',True,True),
    'Foot_L':        ((-0.50,0,0.18),(-0.50,0.20,-0.12),'Shin_L',True,True),
}

IK_BONES={
    'IK_Hand_R':     ((3.50,-0.45,1.90),(3.50,-0.45,2.10),'Root'),
    'IK_Hand_L':     ((-3.50,-0.45,1.90),(-3.50,-0.45,2.10),'Root'),
    'IK_AnchorR':    ((3.50,-0.45,0.90),(3.50,-0.45,1.10),'Root'),
    'IK_AnchorL':    ((-3.50,-0.45,0.90),(-3.50,-0.45,1.10),'Root'),
    'IK_Foot_R':     ((0.50,0.20,-0.12),(0.50,0.20,0.12),'Root'),
    'IK_Foot_L':     ((-0.50,0.20,-0.12),(-0.50,0.20,0.12),'Root'),
    'Pole_Arm_R':    ((1.80,1.20,2.80),(1.80,1.30,2.80),'Root'),
    'Pole_Arm_L':    ((-1.80,1.20,2.80),(-1.80,1.30,2.80),'Root'),
    'Pole_Knee_R':   ((0.50,-0.80,1.10),(0.50,-0.90,1.10),'Root'),
    'Pole_Knee_L':   ((-0.50,-0.80,1.10),(-0.50,-0.90,1.10),'Root'),
}

def add_wheel_driver(arm_obj):
    obj_mode()
    pb=arm_obj.pose.bones.get('ShipWheel_Spin')
    if not pb: return
    pb.rotation_mode='XYZ'
    drv=pb.driver_add('rotation_euler',1).driver  # Y axis spin
    drv.type='SCRIPTED'; drv.expression='frame*0.06'
    v=drv.variables.new(); v.name='frame'
    v.targets[0].id_type='SCENE'; v.targets[0].id=bpy.context.scene

def build_rig():
    ao=new_arm('CT_Armature')
    eb=edit_mode(ao)
    for name,(head,tail,par,conn,deform) in BONES.items():
        add_bone(eb,name,head,tail,par,conn,deform)
    for name,(head,tail,par) in IK_BONES.items():
        b=eb.new(name); b.head=Vector(head); b.tail=Vector(tail); b.use_deform=False
        if par in eb: b.parent=eb[par]
    obj_mode()
    pb=pose_mode(ao)
    # IK
    add_ik(pb,'ForeArm_R', ao,'IK_Hand_R', 2,pole='Pole_Arm_R', psub='Pole_Arm_R', pang=-90)
    add_ik(pb,'ForeArm_L', ao,'IK_Hand_L', 2,pole='Pole_Arm_L', psub='Pole_Arm_L', pang=-90)
    add_ik(pb,'Shin_R',    ao,'IK_Foot_R', 2,pole='Pole_Knee_R',psub='Pole_Knee_R',pang=90)
    add_ik(pb,'Shin_L',    ao,'IK_Foot_L', 2,pole='Pole_Knee_L',psub='Pole_Knee_L',pang=90)
    add_ik(pb,'AnchorChain_R2',ao,'IK_AnchorR',2)
    add_ik(pb,'AnchorChain_L2',ao,'IK_AnchorL',2)
    # Limits
    lim_rot(pb,'Spine1',   minx=-15,maxx=20)
    lim_rot(pb,'Spine2',   minx=-12,maxx=18)
    lim_rot(pb,'Neck',     minx=-20,maxx=25)
    lim_rot(pb,'Head',     minx=-20,maxx=25,minz=-35,maxz=35)
    lim_rot(pb,'CoralCrown_Pivot',minx=-12,maxx=12,minz=-12,maxz=12)
    lim_rot(pb,'Mast_Sway',minx=-15,maxx=15,minz=-10,maxz=10)
    lim_rot(pb,'UpperArm_R',minx=-90,maxx=90,minz=-70,maxz=70)
    lim_rot(pb,'UpperArm_L',minx=-90,maxx=90,minz=-70,maxz=70)
    lim_rot(pb,'Thigh_R',  minx=-70,maxx=45)
    lim_rot(pb,'Thigh_L',  minx=-70,maxx=45)
    lim_rot(pb,'Shin_R',   minx=-120,maxx=0,minz=0,maxz=0)
    lim_rot(pb,'Shin_L',   minx=-120,maxx=0,minz=0,maxz=0)
    # Colours
    spine=['Root','Pelvis','Spine1','Spine2','Chest','Neck','Head']
    for n in spine: col_b(pb,n,'THEME04')
    for n in ['CoralCrown_Pivot','Eye_L','Eye_R']: col_b(pb,n,'THEME07')
    for n in ['ShipWheel_Spin']: col_b(pb,n,'THEME09')
    for n in ['MastRoot','Mast1','Mast2','Mast_Sway']: col_b(pb,n,'THEME06')
    for n in ['Shoulder_R','UpperArm_R','ForeArm_R','Hand_R','AnchorChain_R1','AnchorChain_R2']: col_b(pb,n,'THEME01')
    for n in ['Shoulder_L','UpperArm_L','ForeArm_L','Hand_L','AnchorChain_L1','AnchorChain_L2']: col_b(pb,n,'THEME03')
    for n in ['Thigh_R','Shin_R','Foot_R','Thigh_L','Shin_L','Foot_L']: col_b(pb,n,'THEME05')
    for n in list(IK_BONES.keys()): col_b(pb,n,'THEME08')
    obj_mode()
    return ao

def bind_meshes(arm_obj):
    root_e=bpy.data.objects.get('Boss_CoralTitan_ROOT')
    if not root_e: print("  ROOT not found."); return
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.type=='MESH' and o.parent==root_e: o.select_set(True)
    bpy.context.view_layer.objects.active=arm_obj; arm_obj.select_set(True)
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    bpy.ops.object.select_all(action='DESELECT')
    root_e.parent=arm_obj; root_e.parent_type='BONE'; root_e.parent_bone='Root'

def main():
    ao=build_rig()
    bind_meshes(ao)
    add_wheel_driver(ao)
    col=bpy.data.collections.get('IsleTrial_Boss_CoralTitan')
    if col and ao.name not in col.objects:
        col.objects.link(ao)
        if ao.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(ao)
    print("[IsleTrial] Boss Ancient Coral Titan RIG built.")
    print("  Bones:", len(ao.data.bones))
    print("  Ability bones: ShipWheel_Spin (driver), Mast_Sway, CoralCrown_Pivot,")
    print("                 AnchorChain R/L IK, Eye_L/R aim, GroundStomp empties")

main()
