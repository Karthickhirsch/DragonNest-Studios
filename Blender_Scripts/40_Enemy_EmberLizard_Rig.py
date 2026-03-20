"""
40_Enemy_EmberLizard_Rig.py
IsleTrial — EmberLizard Creature Rig
=====================================
Run AFTER 40_Enemy_EmberLizard.py in the same Blender scene.

Creature:  Volcanic lava lizard  ~1.5 m long
Rig type:  Generic (not Humanoid — quadruped creature)

Bone hierarchy:
  Root
  ├─ Spine1 → Spine2 → Spine3 → Spine4 → Neck → Head → LowerJaw
  ├─ Tail1 → Tail2 → Tail3 → Tail4 → Tail5
  ├─ LF_Upper → LF_Lower → LF_Foot   (left front leg)
  ├─ RF_Upper → RF_Lower → RF_Foot   (right front leg)
  ├─ LB_Upper → LB_Lower → LB_Foot   (left back leg)
  └─ RB_Upper → RB_Lower → RB_Foot   (right back leg)

  Extra (non-deform):
  DorsalSpine_00 … DorsalSpine_06  (7 spine spikes — scale for combat flare)
  LavaGlow_Belly                   (drives belly lava material emission)

IK targets on all 4 feet (ground contact control).

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
#  Bone positions match exactly those in 40_Enemy_EmberLizard.py
#  Creature stands with body axis along Z (vertical reference pose)
# ─────────────────────────────────────────────────────

BONES = {
    # ── Core spine ───────────────────────────────────
    'Root':      ((0,0,0),        (0,0,0.25),    None,       False),
    'Spine1':    ((0,0,0.25),     (0,0,0.55),    'Root',     True),
    'Spine2':    ((0,0,0.55),     (0,0,0.90),    'Spine1',   True),
    'Spine3':    ((0,0,0.90),     (0,0,1.20),    'Spine2',   True),
    'Spine4':    ((0,0,1.20),     (0,0,1.50),    'Spine3',   True),
    'Neck':      ((0,0,1.50),     (0,0,1.75),    'Spine4',   True),
    'Head':      ((0,0,1.75),     (0,0,2.20),    'Neck',     True),
    'LowerJaw':  ((0,-0.12,1.80), (0,-0.12,1.42),'Head',     False),

    # ── Tail ─────────────────────────────────────────
    'Tail1':     ((0,0,0.00),     (0,0,-0.35),   'Root',     False),
    'Tail2':     ((0,0,-0.35),    (0,0,-0.70),   'Tail1',    True),
    'Tail3':     ((0,0,-0.70),    (0,0,-1.00),   'Tail2',    True),
    'Tail4':     ((0,0,-1.00),    (0,0,-1.25),   'Tail3',    True),
    'Tail5':     ((0,0,-1.25),    (0,0,-1.42),   'Tail4',    True),

    # ── Front legs ───────────────────────────────────
    'LF_Upper':  ((-0.32,0,0.40), (-0.32,0,0.00), 'Spine1',  False),
    'LF_Lower':  ((-0.32,0,0.00), (-0.48,0,-0.32),'LF_Upper',True),
    'LF_Foot':   ((-0.48,0,-0.32),(-0.48,0,-0.50),'LF_Lower',True),
    'RF_Upper':  (( 0.32,0,0.40), ( 0.32,0,0.00), 'Spine1',  False),
    'RF_Lower':  (( 0.32,0,0.00), ( 0.48,0,-0.32),'RF_Upper',True),
    'RF_Foot':   (( 0.48,0,-0.32),( 0.48,0,-0.50),'RF_Lower',True),

    # ── Back legs ────────────────────────────────────
    'LB_Upper':  ((-0.35,0,0.95), (-0.35,0,0.55), 'Spine3',  False),
    'LB_Lower':  ((-0.35,0,0.55), (-0.50,0,0.25), 'LB_Upper',True),
    'LB_Foot':   ((-0.50,0,0.25), (-0.50,0,0.08), 'LB_Lower',True),
    'RB_Upper':  (( 0.35,0,0.95), ( 0.35,0,0.55), 'Spine3',  False),
    'RB_Lower':  (( 0.35,0,0.55), ( 0.50,0,0.25), 'RB_Upper',True),
    'RB_Foot':   (( 0.50,0,0.25), ( 0.50,0,0.08), 'RB_Lower',True),
}

# Non-deform control bones
EXTRA_BONES = {
    # 7 dorsal spine control bones — scale X/Y for combat flare
    'DorsalSpine_00': ((0,0.30,0.70), (0,0.50,0.80), 'Spine2', False),
    'DorsalSpine_01': ((0,0.30,0.88), (0,0.52,1.00), 'Spine2', False),
    'DorsalSpine_02': ((0,0.30,1.05), (0,0.54,1.18), 'Spine3', False),
    'DorsalSpine_03': ((0,0.30,1.20), (0,0.56,1.35), 'Spine3', False),
    'DorsalSpine_04': ((0,0.30,1.35), (0,0.54,1.48), 'Spine4', False),
    'DorsalSpine_05': ((0,0.30,1.50), (0,0.50,1.60), 'Spine4', False),
    'DorsalSpine_06': ((0,0.30,1.62), (0,0.46,1.70), 'Neck',   False),
    # Belly glow emission driver
    'LavaGlow_Belly': ((0,-0.31,0.52),(0,-0.31,1.10),'Spine2', False),
}


# ─────────────────────────────────────────────────────
#  BUILD ARMATURE
# ─────────────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('EmberLizard_Armature_Data')
    arm_obj  = bpy.data.objects.new('EmberLizard_Armature', arm_data)
    arm_obj.show_in_front = True
    bpy.context.scene.collection.objects.link(arm_obj)

    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    for name, (head, tail, parent, connected) in BONES.items():
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        if parent and parent in eb:
            b.parent = eb[parent]
            b.use_connect = connected

    for name, (head, tail, parent, connected) in EXTRA_BONES.items():
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        b.use_deform = False
        if parent and parent in eb:
            b.parent = eb[parent]
            b.use_connect = connected

    object_mode()
    return arm_obj


# ─────────────────────────────────────────────────────
#  IK TARGETS — all 4 feet
# ─────────────────────────────────────────────────────

def add_ik_targets(arm_obj):
    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    ik_defs = {
        'IK_LF_Foot': ((-0.48,0,-0.50),(-0.48,0,-0.30),'Root'),
        'IK_RF_Foot': (( 0.48,0,-0.50),( 0.48,0,-0.30),'Root'),
        'IK_LB_Foot': ((-0.50,0, 0.08),(-0.50,0, 0.28),'Root'),
        'IK_RB_Foot': (( 0.50,0, 0.08),( 0.50,0, 0.28),'Root'),
        # Pole targets (knee/elbow hint)
        'Pole_LF':    ((-0.48,-0.50,-0.20),(-0.48,-0.50,-0.10),'Root'),
        'Pole_RF':    (( 0.48,-0.50,-0.20),( 0.48,-0.50,-0.10),'Root'),
        'Pole_LB':    ((-0.50,-0.50, 0.30),(-0.50,-0.50, 0.40),'Root'),
        'Pole_RB':    (( 0.50,-0.50, 0.30),( 0.50,-0.50, 0.40),'Root'),
    }

    for name, (head, tail, parent) in ik_defs.items():
        b = eb.new(name)
        b.head = Vector(head); b.tail = Vector(tail)
        b.parent = eb[parent]
        b.use_deform = False

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

    add_ik('LF_Foot','IK_LF_Foot', 3, 'Pole_LF', -90)
    add_ik('RF_Foot','IK_RF_Foot', 3, 'Pole_RF', -90)
    add_ik('LB_Foot','IK_LB_Foot', 3, 'Pole_LB', -90)
    add_ik('RB_Foot','IK_RB_Foot', 3, 'Pole_RB', -90)

    # Jaw track constraint — keeps jaw hinging correctly
    if 'LowerJaw' in pb:
        c = pb['LowerJaw'].constraints.new('LIMIT_ROTATION')
        c.owner_space = 'LOCAL'
        c.use_limit_x = True
        c.min_x = math.radians(-45); c.max_x = math.radians(0)

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

    # Spine — serpentine lateral bending
    for b in ['Spine1','Spine2','Spine3','Spine4']:
        limit(b, True, True, True, xmn=-15, xmx=15, ymn=-30, ymx=30, zmn=-15, zmx=15)
    limit('Neck',     True, True, True, xmn=-30, xmx=30, ymn=-40, ymx=40, zmn=-20, zmx=20)
    limit('Head',     True, True, True, xmn=-45, xmx=45, ymn=-50, ymx=50, zmn=-25, zmx=25)

    # Tail — wide lateral swing
    for b in ['Tail1','Tail2','Tail3']:
        limit(b, True, True, True, xmn=-10, xmx=10, ymn=-45, ymx=45, zmn=-10, zmx=10)
    for b in ['Tail4','Tail5']:
        limit(b, True, True, True, xmn=-5, xmx=5, ymn=-55, ymx=55, zmn=-5, zmx=5)

    # Front legs
    limit('LF_Upper', True, True, True, xmn=-80, xmx=80, ymn=-30, ymx=30, zmn=-60, zmx=60)
    limit('LF_Lower', True, False, True, xmn=-120, xmx=10, zmn=-5, zmx=5)
    limit('RF_Upper', True, True, True, xmn=-80, xmx=80, ymn=-30, ymx=30, zmn=-60, zmx=60)
    limit('RF_Lower', True, False, True, xmn=-120, xmx=10, zmn=-5, zmx=5)

    # Back legs
    limit('LB_Upper', True, True, True, xmn=-90, xmx=45, ymn=-30, ymx=30, zmn=-60, zmx=60)
    limit('LB_Lower', True, False, True, xmn=-130, xmx=0, zmn=-5, zmx=5)
    limit('RB_Upper', True, True, True, xmn=-90, xmx=45, ymn=-30, ymx=30, zmn=-60, zmx=60)
    limit('RB_Lower', True, False, True, xmn=-130, xmx=0, zmn=-5, zmx=5)

    object_mode()


# ─────────────────────────────────────────────────────
#  PLACEHOLDER BODY MESH
# ─────────────────────────────────────────────────────

def build_body_mesh():
    bm = bmesh.new()

    def box(cx, cy, cz, sx, sy, sz):
        mat = __import__('mathutils').Matrix.Translation((cx, cy, cz))
        result = bmesh.ops.create_cube(bm, size=1.0)
        for v in result['verts']:
            v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
            v.co = mat @ v.co

    # Body
    box(0, 0, 0.90,  0.60, 0.40, 0.55)
    # Neck
    box(0, 0, 1.62,  0.24, 0.24, 0.24)
    # Head
    box(0, 0.05, 2.00, 0.36, 0.45, 0.38)
    # Lower jaw
    box(0,-0.12, 1.76, 0.28, 0.20, 0.18)
    # Tail
    box(0, 0,-0.55,  0.28, 0.28, 0.80)
    # Front legs L/R
    for sx in [-0.32, 0.32]:
        box(sx, 0, 0.18, 0.14, 0.14, 0.42)
    # Back legs L/R
    for sx in [-0.35, 0.35]:
        box(sx, 0, 0.50, 0.16, 0.16, 0.46)

    bm.normal_update()
    me = bpy.data.meshes.new('EmberLizard_Body_Mesh')
    bm.to_mesh(me); bm.free()

    body = bpy.data.objects.new('EmberLizard_Body', me)
    bpy.context.scene.collection.objects.link(body)

    mat = bpy.data.materials.new('Mat_EmberLizard_Placeholder')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value     = (0.25, 0.12, 0.05, 1.0)
        bsdf.inputs['Roughness'].default_value      = 0.75
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.35, 0.0, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 0.4
    body.data.materials.append(mat)
    return body


# ─────────────────────────────────────────────────────
#  BONE COLOURS
# ─────────────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    spine = ['Root','Spine1','Spine2','Spine3','Spine4','Neck','Head','LowerJaw']
    tail  = ['Tail1','Tail2','Tail3','Tail4','Tail5']
    left  = [n for n in list(BONES)+list(EXTRA_BONES) if n.startswith('L')]
    right = [n for n in list(BONES)+list(EXTRA_BONES) if n.startswith('R')]
    ik    = [n for n in pb.keys() if n.startswith('IK_') or n.startswith('Pole_')]
    dorsal= [n for n in EXTRA_BONES if n.startswith('Dorsal')]

    for b in spine:
        if b in pb: pb[b].color.palette = 'THEME01'  # red
    for b in tail:
        if b in pb: pb[b].color.palette = 'THEME07'  # orange
    for b in left:
        if b in pb: pb[b].color.palette = 'THEME04'  # green
    for b in right:
        if b in pb: pb[b].color.palette = 'THEME03'  # blue
    for b in ik:
        if b in pb: pb[b].color.palette = 'THEME10'  # cyan
    for b in dorsal:
        if b in pb: pb[b].color.palette = 'THEME09'  # yellow
    if 'LavaGlow_Belly' in pb:
        pb['LavaGlow_Belly'].color.palette = 'THEME02'  # magenta

    object_mode()


# ─────────────────────────────────────────────────────
#  REPORT
# ─────────────────────────────────────────────────────

def print_report(arm_obj):
    total  = len(arm_obj.data.bones)
    deform = sum(1 for b in arm_obj.data.bones if b.use_deform)
    print("\n" + "="*60)
    print("  IsleTrial — EmberLizard Rig Report")
    print("="*60)
    print(f"  Armature     : {arm_obj.name}")
    print(f"  Total bones  : {total}")
    print(f"  Deform bones : {deform}")
    print(f"  IK/control   : {total - deform}")
    print(f"\n  Deform bone list:")
    for b in arm_obj.data.bones:
        if b.use_deform:
            print(f"    {b.name}")
    print(f"\n  Unity import:")
    print("    Rig Type: Generic   Root Bone: Root")
    print("    Scale: 1.0   Axis: Y Up, -Z Forward")
    print(f"\n  Animation clips needed:")
    for clip in ['Idle','Walk','Run','Attack_Bite','Attack_Swipe',
                 'SpineFlare','TailWhip','TakeDamage','Death','Roar']:
        print(f"    {clip}")
    print("="*60 + "\n")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def main():
    clear_scene()
    print("\n[EmberLizardRig] Building armature...")
    arm_obj = build_armature()

    print("[EmberLizardRig] Adding IK targets...")
    add_ik_targets(arm_obj)

    print("[EmberLizardRig] Adding rotation limits...")
    add_rotation_limits(arm_obj)

    print("[EmberLizardRig] Building placeholder body...")
    body_obj = build_body_mesh()

    # Bind
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True); arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    print("[EmberLizardRig] Colouring bones...")
    color_bones(arm_obj)

    activate(arm_obj)
    arm_obj.data.display_type = 'OCTAHEDRAL'
    arm_obj.show_in_front = True

    print_report(arm_obj)

main()
