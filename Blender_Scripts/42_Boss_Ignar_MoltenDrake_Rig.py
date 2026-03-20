"""
42_Boss_Ignar_MoltenDrake_Rig.py
IsleTrial — Ignar the Molten Drake Boss Rig
============================================
Run AFTER 42_Boss_Ignar_MoltenDrake.py in the same Blender scene.

Creature:  Massive volcanic dragon  ~5.5 m body, 6.5 m wing span
Rig type:  Generic (not Humanoid — dragon boss)

Bone hierarchy:
  Root
  ├─ Spine1 → Spine2 → Spine3 → Spine4 → Spine5 → Spine6
  │   └─ Neck → Head → LowerJaw
  ├─ Tail1 → Tail2 → Tail3 → Tail4 → Tail5 → Tail6
  ├─ LF_Upper → LF_Lower → LF_Foot   (left front leg)
  ├─ RF_Upper → RF_Lower → RF_Foot   (right front leg)
  ├─ LB_Upper → LB_Lower → LB_Foot   (left back leg)
  ├─ RB_Upper → RB_Lower → RB_Foot   (right back leg)
  ├─ WingL_Base → WingL_Mid → WingL_Tip
  └─ WingR_Base → WingR_Mid → WingR_Tip

  Extra (non-deform):
  DorsalPlate_00 … DorsalPlate_09  (10 lava dorsal plates — scale for heat flare)
  FireBreath_Ctrl                  (particle system driver bone, child of Head)
  LavaGlow_Chest                   (drives chest crack emission, child of Spine3)

IK: all 4 feet, wing tips (for flight arcs)

Unity import:
  Rig Type   : Generic
  Root bone  : Root
  Scale      : 1.0
  Axis       : Y Up, -Z Forward
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ─────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.meshes):    bpy.data.meshes.remove(m)
    for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)

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
#  BONE DEFINITIONS
#  Positions match exactly those in 42_Boss_Ignar_MoltenDrake.py
# ─────────────────────────────────────────────────────

BONES = {
    # ── Core spine ───────────────────────────────────
    'Root':      ((0,0,0),      (0,0,0.5),    None,       False),
    'Spine1':    ((0,0,0.5),    (0,0,1.2),    'Root',     True),
    'Spine2':    ((0,0,1.2),    (0,0,2.0),    'Spine1',   True),
    'Spine3':    ((0,0,2.0),    (0,0,2.8),    'Spine2',   True),
    'Spine4':    ((0,0,2.8),    (0,0,3.5),    'Spine3',   True),
    'Spine5':    ((0,0,3.5),    (0,0,4.2),    'Spine4',   True),
    'Spine6':    ((0,0,4.2),    (0,0,4.7),    'Spine5',   True),
    'Neck':      ((0,0,4.7),    (0,0,5.6),    'Spine6',   True),
    'Head':      ((0,0,5.6),    (0,0,7.0),    'Neck',     True),
    'LowerJaw':  ((0,-0.5,5.8), (0,-0.5,4.8), 'Head',     False),

    # ── Tail ─────────────────────────────────────────
    'Tail1':     ((0,0,0.00),   (0,0,-0.55),  'Root',     False),
    'Tail2':     ((0,0,-0.55),  (0,0,-1.10),  'Tail1',    True),
    'Tail3':     ((0,0,-1.10),  (0,0,-1.65),  'Tail2',    True),
    'Tail4':     ((0,0,-1.65),  (0,0,-2.10),  'Tail3',    True),
    'Tail5':     ((0,0,-2.10),  (0,0,-2.50),  'Tail4',    True),
    'Tail6':     ((0,0,-2.50),  (0,0,-2.80),  'Tail5',    True),

    # ── Front legs ───────────────────────────────────
    'LF_Upper':  ((-0.80,0,1.5), (-0.80,0,0.70), 'Spine2', False),
    'LF_Lower':  ((-0.80,0,0.70),(-1.10,0,0.05), 'LF_Upper',True),
    'LF_Foot':   ((-1.10,0,0.05),(-1.10,0,-0.30),'LF_Lower',True),
    'RF_Upper':  (( 0.80,0,1.5), ( 0.80,0,0.70), 'Spine2', False),
    'RF_Lower':  (( 0.80,0,0.70),( 1.10,0,0.05), 'RF_Upper',True),
    'RF_Foot':   (( 1.10,0,0.05),( 1.10,0,-0.30),'RF_Lower',True),

    # ── Back legs ────────────────────────────────────
    'LB_Upper':  ((-0.85,0,3.5), (-0.85,0,2.70), 'Spine4', False),
    'LB_Lower':  ((-0.85,0,2.70),(-1.15,0,2.05), 'LB_Upper',True),
    'LB_Foot':   ((-1.15,0,2.05),(-1.15,0,1.75), 'LB_Lower',True),
    'RB_Upper':  (( 0.85,0,3.5), ( 0.85,0,2.70), 'Spine4', False),
    'RB_Lower':  (( 0.85,0,2.70),( 1.15,0,2.05), 'RB_Upper',True),
    'RB_Foot':   (( 1.15,0,2.05),( 1.15,0,1.75), 'RB_Lower',True),

    # ── Wings ────────────────────────────────────────
    'WingL_Base':((-0.85,0,2.8), (-1.80,0.2,3.50),'Spine3', False),
    'WingL_Mid': ((-1.80,0.2,3.50),(-4.50,0.4,4.20),'WingL_Base',True),
    'WingL_Tip': ((-4.50,0.4,4.20),(-7.20,0.2,4.60),'WingL_Mid', True),
    'WingR_Base':(( 0.85,0,2.8), ( 1.80,0.2,3.50),'Spine3', False),
    'WingR_Mid': (( 1.80,0.2,3.50),( 4.50,0.4,4.20),'WingR_Base',True),
    'WingR_Tip': (( 4.50,0.4,4.20),( 7.20,0.2,4.60),'WingR_Mid', True),
}

# Dorsal lava plates — at spine Z positions
_dorsal_z = [0.80,1.20,1.60,2.00,2.40,2.80,3.20,3.60,4.00,4.40]
_dorsal_parents = ['Spine1','Spine2','Spine2','Spine3','Spine3',
                    'Spine4','Spine4','Spine5','Spine5','Spine6']
EXTRA_BONES = {
    f'DorsalPlate_{i:02d}': (
        (0, 0.5, _dorsal_z[i]),
        (0, 1.0 + i*0.05, _dorsal_z[i]+0.55),
        _dorsal_parents[i],
        False
    ) for i in range(10)
}
EXTRA_BONES['FireBreath_Ctrl'] = ((0,0.5,6.80),(0,1.5,7.20),'Head',False)
EXTRA_BONES['LavaGlow_Chest']  = ((0,0.3,2.40),(0,0.3,3.20),'Spine3',False)


# ─────────────────────────────────────────────────────
#  BUILD ARMATURE
# ─────────────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('Ignar_Armature_Data')
    arm_obj  = bpy.data.objects.new('Ignar_Armature', arm_data)
    arm_obj.show_in_front = True
    bpy.context.scene.collection.objects.link(arm_obj)

    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    for name, (head, tail, parent, connected) in BONES.items():
        b = eb.new(name)
        b.head = Vector(head); b.tail = Vector(tail)
        if parent and parent in eb:
            b.parent = eb[parent]; b.use_connect = connected

    for name, (head, tail, parent, connected) in EXTRA_BONES.items():
        b = eb.new(name)
        b.head = Vector(head); b.tail = Vector(tail)
        b.use_deform = False
        if parent and parent in eb:
            b.parent = eb[parent]; b.use_connect = connected

    object_mode()
    return arm_obj


# ─────────────────────────────────────────────────────
#  IK TARGETS
# ─────────────────────────────────────────────────────

def add_ik_targets(arm_obj):
    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    ik_defs = {
        'IK_LF_Foot': ((-1.10,0,-0.30),(-1.10,0, 0.00),'Root'),
        'IK_RF_Foot': (( 1.10,0,-0.30),( 1.10,0, 0.00),'Root'),
        'IK_LB_Foot': ((-1.15,0, 1.75),(-1.15,0, 2.00),'Root'),
        'IK_RB_Foot': (( 1.15,0, 1.75),( 1.15,0, 2.00),'Root'),
        # Wing tip IK — for flight arc control
        'IK_WingL_Tip':((-7.20,0.2,4.60),(-7.20,0.2,5.00),'Root'),
        'IK_WingR_Tip':(( 7.20,0.2,4.60),( 7.20,0.2,5.00),'Root'),
        # Pole targets
        'Pole_LF':    ((-1.10,-1.20,0.40),(-1.10,-1.20,0.60),'Root'),
        'Pole_RF':    (( 1.10,-1.20,0.40),( 1.10,-1.20,0.60),'Root'),
        'Pole_LB':    ((-1.15,-1.20,2.20),(-1.15,-1.20,2.40),'Root'),
        'Pole_RB':    (( 1.15,-1.20,2.20),( 1.15,-1.20,2.40),'Root'),
    }
    for name, (head, tail, parent) in ik_defs.items():
        b = eb.new(name)
        b.head = Vector(head); b.tail = Vector(tail)
        b.parent = eb[parent]; b.use_deform = False

    object_mode()

    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def add_ik(bone, target, chain, pole=None, pole_angle=0):
        if bone not in pb: return
        c = pb[bone].constraints.new('IK')
        c.target = arm_obj; c.subtarget = target; c.chain_count = chain
        if pole:
            c.pole_target = arm_obj; c.pole_subtarget = pole
            c.pole_angle  = math.radians(pole_angle)

    add_ik('LF_Foot', 'IK_LF_Foot', 3, 'Pole_LF', -90)
    add_ik('RF_Foot', 'IK_RF_Foot', 3, 'Pole_RF', -90)
    add_ik('LB_Foot', 'IK_LB_Foot', 3, 'Pole_LB', -90)
    add_ik('RB_Foot', 'IK_RB_Foot', 3, 'Pole_RB', -90)
    add_ik('WingL_Tip','IK_WingL_Tip', 3)
    add_ik('WingR_Tip','IK_WingR_Tip', 3)

    # Jaw hinge limit
    if 'LowerJaw' in pb:
        c = pb['LowerJaw'].constraints.new('LIMIT_ROTATION')
        c.owner_space = 'LOCAL'
        c.use_limit_x = True
        c.min_x = math.radians(-55); c.max_x = math.radians(0)

    object_mode()


# ─────────────────────────────────────────────────────
#  ROTATION LIMITS
# ─────────────────────────────────────────────────────

def add_rotation_limits(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    def limit(bone, use_x, use_y, use_z,
              xmn=0, xmx=0, ymn=0, ymx=0, zmn=0, zmx=0):
        if bone not in pb: return
        c = pb[bone].constraints.new('LIMIT_ROTATION')
        c.owner_space = 'LOCAL'
        c.use_limit_x = use_x; c.min_x = math.radians(xmn); c.max_x = math.radians(xmx)
        c.use_limit_y = use_y; c.min_y = math.radians(ymn); c.max_y = math.radians(ymx)
        c.use_limit_z = use_z; c.min_z = math.radians(zmn); c.max_z = math.radians(zmx)

    for b in ['Spine1','Spine2','Spine3']:
        limit(b, True, True, True, xmn=-12, xmx=12, ymn=-22, ymx=22, zmn=-10, zmx=10)
    for b in ['Spine4','Spine5','Spine6']:
        limit(b, True, True, True, xmn=-10, xmx=10, ymn=-18, ymx=18, zmn=-8, zmx=8)
    limit('Neck', True, True, True, xmn=-35, xmx=35, ymn=-50, ymx=50, zmn=-25, zmx=25)
    limit('Head', True, True, True, xmn=-50, xmx=50, ymn=-60, ymx=60, zmn=-30, zmx=30)

    # Tail — heavy club tail
    for b in ['Tail1','Tail2']:
        limit(b, True, True, True, xmn=-12, xmx=12, ymn=-40, ymx=40, zmn=-10, zmx=10)
    for b in ['Tail3','Tail4','Tail5','Tail6']:
        limit(b, True, True, True, xmn=-8, xmx=8, ymn=-55, ymx=55, zmn=-8, zmx=8)

    # Legs
    for side in ('LF','RF'):
        limit(f'{side}_Upper', True, True, True, xmn=-90,xmx=90,ymn=-35,ymx=35,zmn=-70,zmx=70)
        limit(f'{side}_Lower', True, False, True, xmn=-130,xmx=10,zmn=-8,zmx=8)
    for side in ('LB','RB'):
        limit(f'{side}_Upper', True, True, True, xmn=-100,xmx=50,ymn=-35,ymx=35,zmn=-70,zmx=70)
        limit(f'{side}_Lower', True, False, True, xmn=-140,xmx=0,zmn=-8,zmx=8)

    # Wings — full flap range
    limit('WingL_Base', True, True, True, xmn=-80,xmx=60,ymn=-30,ymx=30,zmn=-90,zmx=90)
    limit('WingL_Mid',  True, True, True, xmn=-70,xmx=40,ymn=-20,ymx=20,zmn=-80,zmx=80)
    limit('WingL_Tip',  True, True, True, xmn=-60,xmx=30,ymn=-15,ymx=15,zmn=-70,zmx=70)
    limit('WingR_Base', True, True, True, xmn=-80,xmx=60,ymn=-30,ymx=30,zmn=-90,zmx=90)
    limit('WingR_Mid',  True, True, True, xmn=-70,xmx=40,ymn=-20,ymx=20,zmn=-80,zmx=80)
    limit('WingR_Tip',  True, True, True, xmn=-60,xmx=30,ymn=-15,ymx=15,zmn=-70,zmx=70)

    object_mode()


# ─────────────────────────────────────────────────────
#  PLACEHOLDER MESH
# ─────────────────────────────────────────────────────

def build_body_mesh():
    bm = bmesh.new()

    def box(cx, cy, cz, sx, sy, sz):
        mat = __import__('mathutils').Matrix.Translation((cx, cy, cz))
        result = bmesh.ops.create_cube(bm, size=1.0)
        for v in result['verts']:
            v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
            v.co = mat @ v.co

    # Body torso
    box(0, 0, 2.50,  1.60, 1.10, 2.50)
    # Neck
    box(0, 0, 5.15,  0.60, 0.60, 1.00)
    # Head
    box(0, 0.20, 6.30, 0.90, 1.20, 1.60)
    # Lower jaw
    box(0,-0.50, 5.50, 0.70, 0.30, 0.80)
    # Tail
    box(0, 0,-1.20,  0.70, 0.70, 2.60)
    # Front legs
    for sx in [-0.90, 0.90]:
        box(sx, 0, 0.90, 0.35, 0.35, 1.60)
    # Back legs
    for sx in [-0.95, 0.95]:
        box(sx, 0, 2.55, 0.38, 0.38, 1.70)
    # Wings (simplified planes)
    for sx in [-3.50, 3.50]:
        box(sx*0.5, 0.30, 3.80, abs(sx), 0.08, 1.40)

    bm.normal_update()
    me = bpy.data.meshes.new('Ignar_Body_Mesh')
    bm.to_mesh(me); bm.free()

    body = bpy.data.objects.new('Ignar_Body', me)
    bpy.context.scene.collection.objects.link(body)

    mat = bpy.data.materials.new('Mat_Ignar_Placeholder')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value     = (0.18, 0.06, 0.02, 1.0)
        bsdf.inputs['Roughness'].default_value      = 0.80
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.25, 0.0, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 0.6
    body.data.materials.append(mat)
    return body


# ─────────────────────────────────────────────────────
#  BONE COLOURS
# ─────────────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    spine  = ['Root','Spine1','Spine2','Spine3','Spine4','Spine5','Spine6',
              'Neck','Head','LowerJaw']
    tail   = ['Tail1','Tail2','Tail3','Tail4','Tail5','Tail6']
    left   = [n for n in list(BONES) if n.startswith('L')]
    right  = [n for n in list(BONES) if n.startswith('R')]
    wings  = [n for n in list(BONES) if 'Wing' in n]
    ik     = [n for n in pb.keys() if n.startswith('IK_') or n.startswith('Pole_')]
    dorsal = [n for n in EXTRA_BONES if n.startswith('Dorsal')]
    ctrl   = ['FireBreath_Ctrl','LavaGlow_Chest']

    for b in spine:
        if b in pb: pb[b].color.palette = 'THEME01'   # red
    for b in tail:
        if b in pb: pb[b].color.palette = 'THEME07'   # orange
    for b in left:
        if b in pb: pb[b].color.palette = 'THEME04'   # green
    for b in right:
        if b in pb: pb[b].color.palette = 'THEME03'   # blue
    for b in wings:
        if b in pb: pb[b].color.palette = 'THEME05'   # purple
    for b in ik:
        if b in pb: pb[b].color.palette = 'THEME10'   # cyan
    for b in dorsal:
        if b in pb: pb[b].color.palette = 'THEME09'   # yellow
    for b in ctrl:
        if b in pb: pb[b].color.palette = 'THEME02'   # magenta

    object_mode()


# ─────────────────────────────────────────────────────
#  REPORT
# ─────────────────────────────────────────────────────

def print_report(arm_obj):
    total  = len(arm_obj.data.bones)
    deform = sum(1 for b in arm_obj.data.bones if b.use_deform)
    print("\n" + "="*60)
    print("  IsleTrial — Ignar MoltenDrake Rig Report")
    print("="*60)
    print(f"  Armature     : {arm_obj.name}")
    print(f"  Total bones  : {total}")
    print(f"  Deform bones : {deform}")
    print(f"  IK/control   : {total - deform}")
    print(f"\n  Unity import:")
    print("    Rig Type: Generic   Root Bone: Root")
    print("    Scale: 1.0   Axis: Y Up, -Z Forward")
    print(f"\n  Animation clips needed (Phase 1 / 2 / 3):")
    for clip in ['Idle_Ground','Walk','Roar','WingFlap_Idle','TakeOff','Fly_Forward',
                 'Land','Attack_Bite','Attack_Claw_L','Attack_Claw_R',
                 'Attack_TailSlam','Attack_FireBreath','FireBreath_Loop',
                 'Wing_Shield','LavaSlam','TakeDamage','Death']:
        print(f"    {clip}")
    print(f"\n  Unity notes:")
    print("    FireBreath_Ctrl: link to ParticleSystem child transform")
    print("    DorsalPlate_* scale X/Y: driven by 'HeatIntensity' Animator param (0-1)")
    print("    WingL/R_Tip IK targets: keyframe for flight arc control")
    print("="*60 + "\n")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def main():
    clear_scene()
    print("\n[IgnarRig] Building armature...")
    arm_obj = build_armature()

    print("[IgnarRig] Adding IK targets...")
    add_ik_targets(arm_obj)

    print("[IgnarRig] Adding rotation limits...")
    add_rotation_limits(arm_obj)

    print("[IgnarRig] Building placeholder body...")
    body_obj = build_body_mesh()

    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True); arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    print("[IgnarRig] Colouring bones...")
    color_bones(arm_obj)

    activate(arm_obj)
    arm_obj.data.display_type = 'OCTAHEDRAL'
    arm_obj.show_in_front = True

    print_report(arm_obj)

main()
