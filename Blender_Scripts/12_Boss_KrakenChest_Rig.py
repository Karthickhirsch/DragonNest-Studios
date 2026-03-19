"""
IsleTrial – Boss 03 RIG: Kraken Chest King
============================================
Run AFTER 12_Boss_KrakenChest.py.
Generic rig with:
  • Chest_Body + Lid_Pivot / Lid_Bone (jaw opening)
  • 3 Eye bones (EyeBall_C, _L, _R) with eyelids
  • 3-bone Tongue chain
  • 10 Tentacle chains × 3 bones each
  • Crown_Pivot (lid crown weapons rotation)
  • TreasureGlow bone (interior emission pulse)
  • Ability empties for FX
"""

import bpy, math
from mathutils import Vector

def new_arm(name):
    d=bpy.data.armatures.new(name); o=bpy.data.objects.new(name,d)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o; o.select_set(True); return o

def edit_mode(ao):
    bpy.context.view_layer.objects.active=ao
    bpy.ops.object.mode_set(mode='EDIT')
    return ao.data.edit_bones

def pose_mode(ao):
    bpy.context.view_layer.objects.active=ao
    bpy.ops.object.mode_set(mode='POSE')
    return ao.pose.bones

def obj_mode(): bpy.ops.object.mode_set(mode='OBJECT')

def add_bone(eb,name,head,tail,par=None,conn=False,deform=True):
    b=eb.new(name); b.head=Vector(head); b.tail=Vector(tail); b.use_deform=deform
    if par and par in eb: b.parent=eb[par]; b.use_connect=conn
    return b

def lim_rot(pb,name,minx=-45,maxx=45,minz=-45,maxz=45):
    b=pb.get(name);
    if not b: return
    c=b.constraints.new('LIMIT_ROTATION'); c.owner_space='LOCAL'
    c.use_limit_x=True; c.min_x=math.radians(minx); c.max_x=math.radians(maxx)
    c.use_limit_z=True; c.min_z=math.radians(minz); c.max_z=math.radians(maxz)

def col_b(pb,name,theme):
    b=pb.get(name);
    if b: b.color.palette=theme

BONES={
    'Root':        ((0,0,0),(0,0,0.06),None,False,False),
    'Chest_Body':  ((0,0,0),(0,0,1.35),'Root',False,True),
    'Lid_Pivot':   ((0,0,1.36),(0,0,1.45),'Root',False,False),
    'Lid_Bone':    ((0,0,1.45),(0,-0.35,1.70),'Lid_Pivot',False,True),
    # Eyes
    'EyeRoot_C':   ((0,-1.00,1.10),(0,-1.00,1.28),'Root',False,False),
    'EyeBall_C':   ((0,-1.00,1.28),(0,-1.00,1.38),'EyeRoot_C',True,True),
    'EyeLid_C_T':  ((0,-0.96,1.30),(0,-0.96,1.44),'EyeRoot_C',False,True),
    'EyeLid_C_B':  ((0,-0.96,1.00),(0,-0.96,0.88),'EyeRoot_C',False,True),
    'EyeRoot_L':   ((-0.75,-0.86,0.72),(-0.75,-0.86,0.88),'Root',False,False),
    'EyeBall_L':   ((-0.75,-0.86,0.88),(-0.75,-0.86,0.98),'EyeRoot_L',True,True),
    'EyeRoot_R':   ((0.75,-0.86,0.72),(0.75,-0.86,0.88),'Root',False,False),
    'EyeBall_R':   ((0.75,-0.86,0.88),(0.75,-0.86,0.98),'EyeRoot_R',True,True),
    # Tongue chain
    'Tongue1':     ((0,-0.85,1.30),(0,-1.00,1.28),'Chest_Body',False,True),
    'Tongue2':     ((0,-1.00,1.28),(0,-1.18,1.22),'Tongue1',True,True),
    'Tongue3':     ((0,-1.18,1.22),(0,-1.35,1.14),'Tongue2',True,True),
    # Crown
    'Crown_Pivot': ((0,-0.35,1.70),(0,-0.35,1.90),'Lid_Bone',False,False),
    # Interior glow
    'TreasureGlow':((0,0,1.20),(0,0,1.45),'Chest_Body',False,True),
}

# 10 tentacle chains × 3 bones
TENTACLE_ROOTS=[
    ('L1',(-1.30,-0.10,0.80),(-2.80,-0.80,1.20)),
    ('L2',(-1.30, 0.50,0.50),(-2.60, 1.80,0.20)),
    ('L3',(-1.20, 0.90,1.00),(-2.20, 2.50,1.60)),
    ('L4',(-1.00,-0.50,0.30),(-1.80,-2.00,-0.30)),
    ('CL',(-0.80,-0.80,0.80),(-0.80,-3.20, 0.80)),
    ('R1',( 1.30,-0.10,0.80),( 2.80,-0.80,1.20)),
    ('R2',( 1.30, 0.50,0.50),( 2.60, 1.80,0.20)),
    ('R3',( 1.20, 0.90,1.00),( 2.20, 2.50,1.60)),
    ('R4',( 1.00,-0.50,0.30),( 1.80,-2.00,-0.30)),
    ('CR',( 0.80,-0.80,0.80),( 0.80,-3.20, 0.80)),
]

def build_rig():
    ao=new_arm('KC_Armature')
    eb=edit_mode(ao)
    for name,(head,tail,par,conn,deform) in BONES.items():
        add_bone(eb,name,head,tail,par,conn,deform)
    # Add tentacle bones
    for (tid,base,tip) in TENTACLE_ROOTS:
        bv=Vector(base); tv=Vector(tip)
        p1=bv; p2=bv.lerp(tv,0.33); p3=bv.lerp(tv,0.66)
        pn=None
        for si,(ph,pt) in enumerate([(p1,p2),(p2,p3),(p3,tv)]):
            bname=f'Tent_{tid}_{si+1}'
            par_name=f'Tent_{tid}_{si}' if si>0 else 'Root'
            b=add_bone(eb,bname,ph,pt,par_name,si>0,True)
    # IK targets for tentacle tips
    for (tid,base,tip) in TENTACLE_ROOTS:
        ik_name=f'IK_Tent_{tid}'
        tv=Vector(tip)
        b=eb.new(ik_name); b.head=tv; b.tail=tv+Vector((0,0,0.15))
        b.parent=eb['Root']; b.use_deform=False
    obj_mode()
    pb=pose_mode(ao)
    # IK on tentacle chains
    for (tid,_,_) in TENTACLE_ROOTS:
        c=pb[f'Tent_{tid}_3'].constraints.new('IK')
        c.target=ao; c.subtarget=f'IK_Tent_{tid}'; c.chain_count=3
    # Limits
    lim_rot(pb,'Lid_Bone',minx=-120,maxx=0,minz=0,maxz=0)
    lim_rot(pb,'EyeBall_C',minx=-30,maxx=30,minz=-30,maxz=30)
    lim_rot(pb,'EyeBall_L',minx=-25,maxx=25,minz=-25,maxz=25)
    lim_rot(pb,'EyeBall_R',minx=-25,maxx=25,minz=-25,maxz=25)
    lim_rot(pb,'EyeLid_C_T',minx=-40,maxx=10,minz=0,maxz=0)
    lim_rot(pb,'EyeLid_C_B',minx=-10,maxx=40,minz=0,maxz=0)
    lim_rot(pb,'Tongue1',minx=-20,maxx=20,minz=-15,maxz=15)
    lim_rot(pb,'Tongue2',minx=-25,maxx=25,minz=-20,maxz=20)
    lim_rot(pb,'Tongue3',minx=-30,maxx=30,minz=-25,maxz=25)
    for (tid,_,_) in TENTACLE_ROOTS:
        for si in range(1,4):
            lim_rot(pb,f'Tent_{tid}_{si}',minx=-60,maxx=60,minz=-60,maxz=60)
    # Colours
    for n in ['Root','Chest_Body','TreasureGlow']: col_b(pb,n,'THEME04')
    for n in ['Lid_Pivot','Lid_Bone','Crown_Pivot']: col_b(pb,n,'THEME09')
    for n in ['EyeRoot_C','EyeBall_C','EyeLid_C_T','EyeLid_C_B']: col_b(pb,n,'THEME07')
    for n in ['EyeRoot_L','EyeBall_L','EyeRoot_R','EyeBall_R']: col_b(pb,n,'THEME06')
    for n in ['Tongue1','Tongue2','Tongue3']: col_b(pb,n,'THEME10')
    for (tid,_,_) in TENTACLE_ROOTS:
        theme='THEME01' if 'L' in tid else 'THEME03'
        for si in range(1,4): col_b(pb,f'Tent_{tid}_{si}',theme)
    obj_mode()
    return ao

def bind_meshes(arm_obj):
    root_e=bpy.data.objects.get('Boss_KrakenChest_ROOT')
    if not root_e: print("  ROOT not found – run model script first."); return
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
    col=bpy.data.collections.get('IsleTrial_Boss_KrakenChest')
    if col and ao.name not in col.objects:
        col.objects.link(ao)
        if ao.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(ao)
    total_tent=len(TENTACLE_ROOTS)*3
    print("[IsleTrial] Boss Kraken Chest King RIG built.")
    print("  Bones:", len(ao.data.bones))
    print(f"  Tentacle chains: {len(TENTACLE_ROOTS)} × 3 bones = {total_tent} bones")
    print("  Ability bones: EyeBall ×3, Lid_Bone, Crown_Pivot, Tongue ×3, TreasureGlow")

main()
