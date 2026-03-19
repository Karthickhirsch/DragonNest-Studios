"""
IsleTrial – Boss 04 RIG: Dread Admiral
========================================
Run AFTER 13_Boss_DreadAdmiral.py.
Generic rig with:
  • Full spine chain (pelvis → head)
  • Bird legs with IK (knee + ankle + toe tip)
  • 2 upper arms with IK (sword hands)
  • 2 cannon shoulder arms (free rotate)
  • Hat_Tilt bone (dramatic flair)
  • SoulOrb bone (floating in ribcage)
  • SwordSlash_R/L (FK animation)
  • CannonPitch_R/L (aim up/down)
  • SpectralAura bone (pulse scale)
  • GhostSummon empty (spawn point)
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

def lim_rot(pb,name,minx=-45,maxx=45,minz=-45,maxz=45,uy=False,miny=-30,maxy=30):
    b=pb.get(name);
    if not b: return
    c=b.constraints.new('LIMIT_ROTATION'); c.owner_space='LOCAL'
    c.use_limit_x=True; c.min_x=math.radians(minx); c.max_x=math.radians(maxx)
    c.use_limit_y=uy; c.min_y=math.radians(miny); c.max_y=math.radians(maxy)
    c.use_limit_z=True; c.min_z=math.radians(minz); c.max_z=math.radians(maxz)

def col_b(pb,name,th):
    b=pb.get(name);
    if b: b.color.palette=th

BONES={
    'Root':          ((0,0,0),(0,0,0.06),None,False,False),
    'Pelvis':        ((0,0,1.46),(0,0,1.65),'Root',False,True),
    'Spine1':        ((0,0,1.65),(0,0,1.90),'Pelvis',True,True),
    'Spine2':        ((0,0,1.90),(0,0,2.20),'Spine1',True,True),
    'Chest':         ((0,0,2.20),(0,0,2.60),'Spine2',True,True),
    'Neck':          ((0,0,2.60),(0,0,2.80),'Chest',False,True),
    'Head':          ((0,0,2.80),(0,0,3.10),'Neck',True,True),
    'Hat_Root':      ((0,0,3.10),(0,0,3.30),'Head',False,False),
    'Hat_Tilt':      ((0,0,3.30),(0,0,3.65),'Hat_Root',True,True),
    # Soul orb (floats inside ribcage)
    'SoulOrb':       ((0,0.10,2.10),(0,0.10,2.38),'Spine2',False,True),
    # Upper sword arms R
    'Shoulder_R':    ((0.52,0,2.55),(0.65,0,2.55),'Chest',False,False),
    'UpperArm_R':    ((0.65,0,2.55),(1.20,-0.10,2.30),'Shoulder_R',False,True),
    'ForeArm_R':     ((1.20,-0.10,2.30),(1.85,-0.30,1.90),'UpperArm_R',True,True),
    'SwordHand_R':   ((1.85,-0.30,1.90),(2.10,-0.42,1.62),'ForeArm_R',True,True),
    # Upper sword arms L
    'Shoulder_L':    ((-0.52,0,2.55),(-0.65,0,2.55),'Chest',False,False),
    'UpperArm_L':    ((-0.65,0,2.55),(-1.20,-0.10,2.30),'Shoulder_L',False,True),
    'ForeArm_L':     ((-1.20,-0.10,2.30),(-1.85,-0.30,1.90),'UpperArm_L',True,True),
    'SwordHand_L':   ((-1.85,-0.30,1.90),(-2.10,-0.42,1.62),'ForeArm_L',True,True),
    # Cannon shoulder arms
    'CannonArm_R':   ((0.52,0.10,2.45),(0.85,0.40,2.62),'Chest',False,True),
    'CannonPitch_R': ((0.85,0.40,2.62),(1.05,0.58,2.62),'CannonArm_R',True,True),
    'CannonArm_L':   ((-0.52,0.10,2.45),(-0.85,0.40,2.62),'Chest',False,True),
    'CannonPitch_L': ((-0.85,0.40,2.62),(-1.05,0.58,2.62),'CannonArm_L',True,True),
    # Bird legs R
    'Femur_R':       ((0.22,0,1.45),(0.22,0,0.75),'Pelvis',False,True),
    'Tibia_R':       ((0.22,0,0.75),(0.22,0.18,0.22),'Femur_R',True,True),
    'Ankle_R':       ((0.22,0.18,0.22),(0.22,-0.05,-0.04),'Tibia_R',True,True),
    'Toe_R':         ((0.22,-0.05,-0.04),(0.22,-0.36,-0.12),'Ankle_R',True,True),
    # Bird legs L
    'Femur_L':       ((-0.22,0,1.45),(-0.22,0,0.75),'Pelvis',False,True),
    'Tibia_L':       ((-0.22,0,0.75),(-0.22,0.18,0.22),'Femur_L',True,True),
    'Ankle_L':       ((-0.22,0.18,0.22),(-0.22,-0.05,-0.04),'Tibia_L',True,True),
    'Toe_L':         ((-0.22,-0.05,-0.04),(-0.22,-0.36,-0.12),'Ankle_L',True,True),
    # Spectral aura
    'SpectralAura':  ((0,0,2.10),(0,0,2.40),'Spine2',False,True),
}

IK_BONES={
    'IK_SwordHand_R': ((2.10,-0.42,1.62),(2.10,-0.42,1.80),'Root'),
    'IK_SwordHand_L': ((-2.10,-0.42,1.62),(-2.10,-0.42,1.80),'Root'),
    'IK_Toe_R':       ((0.22,-0.36,-0.12),(0.22,-0.36,0.10),'Root'),
    'IK_Toe_L':       ((-0.22,-0.36,-0.12),(-0.22,-0.36,0.10),'Root'),
    'Pole_Arm_R':     ((1.10,0.80,2.30),(1.10,0.90,2.30),'Root'),
    'Pole_Arm_L':     ((-1.10,0.80,2.30),(-1.10,0.90,2.30),'Root'),
    'Pole_Knee_R':    ((0.22,-0.65,0.75),(0.22,-0.75,0.75),'Root'),
    'Pole_Knee_L':    ((-0.22,-0.65,0.75),(-0.22,-0.75,0.75),'Root'),
}

def build_rig():
    ao=new_arm('DA_Armature')
    eb=edit_mode(ao)
    for name,(head,tail,par,conn,deform) in BONES.items():
        add_bone(eb,name,head,tail,par,conn,deform)
    for name,(head,tail,par) in IK_BONES.items():
        b=eb.new(name); b.head=Vector(head); b.tail=Vector(tail); b.use_deform=False
        if par in eb: b.parent=eb[par]
    obj_mode()
    pb=pose_mode(ao)
    # IK
    add_ik(pb,'ForeArm_R', ao,'IK_SwordHand_R',2,pole='Pole_Arm_R', psub='Pole_Arm_R', pang=-90)
    add_ik(pb,'ForeArm_L', ao,'IK_SwordHand_L',2,pole='Pole_Arm_L', psub='Pole_Arm_L', pang=-90)
    add_ik(pb,'Tibia_R',   ao,'IK_Toe_R',       2,pole='Pole_Knee_R',psub='Pole_Knee_R',pang=90)
    add_ik(pb,'Tibia_L',   ao,'IK_Toe_L',       2,pole='Pole_Knee_L',psub='Pole_Knee_L',pang=90)
    # Limits
    lim_rot(pb,'Spine1',    minx=-20,maxx=25)
    lim_rot(pb,'Spine2',    minx=-15,maxx=30)
    lim_rot(pb,'Neck',      minx=-25,maxx=35)
    lim_rot(pb,'Head',      minx=-30,maxx=30,minz=-45,maxz=45)
    lim_rot(pb,'Hat_Tilt',  minx=-20,maxx=20,minz=-15,maxz=15)
    lim_rot(pb,'SoulOrb',   minx=-360,maxx=360,minz=-360,maxz=360)
    lim_rot(pb,'CannonPitch_R',minx=-35,maxx=20,minz=0,maxz=0)
    lim_rot(pb,'CannonPitch_L',minx=-35,maxx=20,minz=0,maxz=0)
    lim_rot(pb,'Femur_R',   minx=-80,maxx=50)
    lim_rot(pb,'Femur_L',   minx=-80,maxx=50)
    lim_rot(pb,'Tibia_R',   minx=0,maxx=130,minz=0,maxz=0)
    lim_rot(pb,'Tibia_L',   minx=0,maxx=130,minz=0,maxz=0)
    lim_rot(pb,'Ankle_R',   minx=-50,maxx=50)
    lim_rot(pb,'Ankle_L',   minx=-50,maxx=50)
    # Colours
    spine=['Root','Pelvis','Spine1','Spine2','Chest','Neck','Head']
    for n in spine: col_b(pb,n,'THEME04')
    for n in ['Hat_Root','Hat_Tilt']: col_b(pb,n,'THEME09')
    for n in ['SoulOrb','SpectralAura']: col_b(pb,n,'THEME06')
    for n in ['Shoulder_R','UpperArm_R','ForeArm_R','SwordHand_R','CannonArm_R','CannonPitch_R']: col_b(pb,n,'THEME01')
    for n in ['Shoulder_L','UpperArm_L','ForeArm_L','SwordHand_L','CannonArm_L','CannonPitch_L']: col_b(pb,n,'THEME03')
    for n in ['Femur_R','Tibia_R','Ankle_R','Toe_R','Femur_L','Tibia_L','Ankle_L','Toe_L']: col_b(pb,n,'THEME05')
    for n in list(IK_BONES.keys()): col_b(pb,n,'THEME08')
    obj_mode()
    return ao

def bind_meshes(arm_obj):
    root_e=bpy.data.objects.get('Boss_DreadAdmiral_ROOT')
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
    col=bpy.data.collections.get('IsleTrial_Boss_DreadAdmiral')
    if col and ao.name not in col.objects:
        col.objects.link(ao)
        if ao.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(ao)
    print("[IsleTrial] Boss Dread Admiral RIG built.")
    print("  Bones:", len(ao.data.bones))
    print("  Ability bones: CannonPitch R/L, SwordHand R/L (IK), SoulOrb, Hat_Tilt, SpectralAura")

main()
