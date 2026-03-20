"""
43_Boss_Glaciara_FrostWarden_Rig.py
IsleTrial — Glaciara the Frost Warden Boss Rig
================================================
Run AFTER 43_Boss_Glaciara_FrostWarden.py in the same Blender scene.

Creature:  3.8 m towering ice humanoid boss
Rig type:  Generic (large non-standard humanoid — too large for
           Unity Humanoid Avatar auto-mapping without errors)

Bone hierarchy:
  Root
  ├─ Pelvis → Spine1 → Spine2 → Spine3 → Spine4 → Neck → Head
  ├─ L_Shoulder → L_Upper → L_Lower   (left arm — club fist, no fingers)
  ├─ R_Shoulder → R_Upper → R_Lower   (right arm — club fist)
  ├─ L_ULeg → L_LLeg                  (left leg — pillar)
  ├─ R_ULeg → R_LLeg                  (right leg — pillar)
  └─ Cape_L / Cape_C / Cape_R         (3 frozen cape panels)

  Extra (non-deform):
  IceCrown_00 … IceCrown_07   (8 crown spire bones — scale for phase shift)
  ChestCore                   (glowing core slit — drives emission intensity)
  IceShard_Ctrl               (projectile spawn point, child of R_Lower)
  IceWall_Ctrl                (wall spawn point, child of Root)

IK: both hands, both feet.

Unity import:
  Rig Type   : Generic
  Root bone  : Root
  Scale      : 1.0
  Axis       : Y Up, -Z Forward

Note: Glaciara uses Generic rig so the non-standard arm proportions
(club fists, no hand bones) do not trigger Humanoid Avatar errors.
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
#  Positions match exactly those in 43_Boss_Glaciara_FrostWarden.py
# ─────────────────────────────────────────────────────

BONES = {
    # ── Root / Pelvis ─────────────────────────────────
    'Root':       ((0,0,0),       (0,0,0.5),      None,         False),
    'Pelvis':     ((0,0,0.5),     (0,0,0.95),     'Root',       True),

    # ── Spine chain ──────────────────────────────────
    'Spine1':     ((0,0,0.95),    (0,0,1.55),     'Pelvis',     True),
    'Spine2':     ((0,0,1.55),    (0,0,2.10),     'Spine1',     True),
    'Spine3':     ((0,0,2.10),    (0,0,2.60),     'Spine2',     True),
    'Spine4':     ((0,0,2.60),    (0,0,2.95),     'Spine3',     True),
    'Neck':       ((0,0,2.95),    (0,0,3.35),     'Spine4',     True),
    'Head':       ((0,0,3.35),    (0,0,4.10),     'Neck',       True),

    # ── Left arm ─────────────────────────────────────
    'L_Shoulder': ((-0.75,0,2.85),(-1.30,0,2.65), 'Spine4',    False),
    'L_Upper':    ((-1.30,0,2.65),(-1.30,0,1.92), 'L_Shoulder',True),
    'L_Lower':    ((-1.30,0,1.92),(-1.30,0,1.05), 'L_Upper',   True),

    # ── Right arm ────────────────────────────────────
    'R_Shoulder': (( 0.75,0,2.85),( 1.30,0,2.65), 'Spine4',    False),
    'R_Upper':    (( 1.30,0,2.65),( 1.30,0,1.92), 'R_Shoulder',True),
    'R_Lower':    (( 1.30,0,1.92),( 1.30,0,1.05), 'R_Upper',   True),

    # ── Legs ─────────────────────────────────────────
    'L_ULeg':     ((-0.42,0,0.95),(-0.42,0,0.05), 'Pelvis',    False),
    'L_LLeg':     ((-0.42,0,0.05),(-0.42,0,-0.85),'L_ULeg',    True),
    'R_ULeg':     (( 0.42,0,0.95),( 0.42,0,0.05), 'Pelvis',    False),
    'R_LLeg':     (( 0.42,0,0.05),( 0.42,0,-0.85),'R_ULeg',    True),

    # ── Cape panels ──────────────────────────────────
    'Cape_L':     ((-0.65,0,2.45),(-0.65,0,1.45), 'Spine3',    False),
    'Cape_C':     (( 0.00,0,2.45),( 0.00,0,1.45), 'Spine3',    False),
    'Cape_R':     (( 0.65,0,2.45),( 0.65,0,1.45), 'Spine3',    False),
}

# Crown spires — 8 spires arranged in circle above head
_crown_angles = [i * (360/8) for i in range(8)]
EXTRA_BONES = {}
for i, angle_deg in enumerate(_crown_angles):
    a = math.radians(angle_deg)
    r = 0.28
    EXTRA_BONES[f'IceCrown_{i:02d}'] = (
        (r*math.cos(a), r*math.sin(a), 3.95),
        (r*1.4*math.cos(a), r*1.4*math.sin(a), 4.75),
        'Head', False
    )
EXTRA_BONES['ChestCore']      = ((0, 0.35, 2.30),(0, 0.35, 2.80),'Spine3',  False)
EXTRA_BONES['IceShard_Ctrl']  = ((-1.30, 0.25, 1.05),(-1.30, 0.65, 1.05),'L_Lower',False)
EXTRA_BONES['IceWall_Ctrl']   = ((0, 2.0, 0.50),(0, 3.0, 0.50),'Root',   False)


# ─────────────────────────────────────────────────────
#  BUILD ARMATURE
# ─────────────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('Glaciara_Armature_Data')
    arm_obj  = bpy.data.objects.new('Glaciara_Armature', arm_data)
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

    # Cape panels are non-deform — driven by physics simulation in Unity
    for cape in ['Cape_L','Cape_C','Cape_R']:
        if cape in eb: eb[cape].use_deform = False

    object_mode()
    return arm_obj


# ─────────────────────────────────────────────────────
#  IK TARGETS
# ─────────────────────────────────────────────────────

def add_ik_targets(arm_obj):
    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones

    ik_defs = {
        'IK_Hand_L':   ((-1.30,0,1.05),(-1.30,0,1.30),'Root'),
        'IK_Hand_R':   (( 1.30,0,1.05),( 1.30,0,1.30),'Root'),
        'IK_Foot_L':   ((-0.42,0,-0.85),(-0.42,0,-0.60),'Root'),
        'IK_Foot_R':   (( 0.42,0,-0.85),( 0.42,0,-0.60),'Root'),
        'Pole_Elbow_L':((-1.30,-0.80,1.92),(-1.30,-0.80,2.10),'Root'),
        'Pole_Elbow_R':(( 1.30,-0.80,1.92),( 1.30,-0.80,2.10),'Root'),
        'Pole_Knee_L': ((-0.42,-0.80,0.05),(-0.42,-0.80,0.20),'Root'),
        'Pole_Knee_R': (( 0.42,-0.80,0.05),( 0.42,-0.80,0.20),'Root'),
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

    add_ik('L_Lower','IK_Hand_L', 2, 'Pole_Elbow_L', 180)
    add_ik('R_Lower','IK_Hand_R', 2, 'Pole_Elbow_R', 180)
    add_ik('L_LLeg', 'IK_Foot_L', 2, 'Pole_Knee_L',  -90)
    add_ik('R_LLeg', 'IK_Foot_R', 2, 'Pole_Knee_R',  -90)

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

    # Spine — heavy ice giant, limited mobility
    for b in ['Spine1','Spine2']:
        limit(b, True, True, True, xmn=-15, xmx=20, ymn=-15, ymx=15, zmn=-15, zmx=15)
    for b in ['Spine3','Spine4']:
        limit(b, True, True, True, xmn=-12, xmx=18, ymn=-12, ymx=12, zmn=-12, zmx=12)
    limit('Neck', True, True, True, xmn=-30, xmx=30, ymn=-20, ymx=20, zmn=-25, zmx=25)
    limit('Head', True, True, True, xmn=-40, xmx=40, ymn=-30, ymx=30, zmn=-30, zmx=30)

    # Arms — massive clubs, simple 2-bone chain
    for side in ('L','R'):
        limit(f'{side}_Shoulder', True, True, True,
              xmn=-90, xmx=90, ymn=-40, ymx=40, zmn=-90, zmx=90)
        limit(f'{side}_Upper', True, True, True,
              xmn=-110, xmx=80, ymn=-35, ymx=35, zmn=-80, zmx=80)
        limit(f'{side}_Lower', True, False, True,
              xmn=0, xmx=145, zmn=-8, zmx=8)

    # Legs — pillar legs, limited range
    for side in ('L','R'):
        limit(f'{side}_ULeg', True, True, True,
              xmn=-85, xmx=45, ymn=-30, ymx=30, zmn=-40, zmx=40)
        limit(f'{side}_LLeg', True, False, True,
              xmn=-130, xmx=0, zmn=-5, zmx=5)

    # Cape panels — wind/physics driven
    for cape in ['Cape_L','Cape_C','Cape_R']:
        limit(cape, True, False, True, xmn=-60, xmx=60, zmn=-25, zmx=25)

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

    # Torso (wide hulking chest)
    box(0, 0, 1.80,  1.40, 0.90, 1.40)
    # Pelvis (wide hips)
    box(0, 0, 0.72,  1.10, 0.75, 0.46)
    # Head (large)
    box(0, 0, 3.72,  0.78, 0.72, 0.75)
    # Neck
    box(0, 0, 3.15,  0.40, 0.40, 0.40)
    # Left arm
    box(-1.30, 0, 1.88, 0.40, 0.40, 1.60)
    # Right arm
    box( 1.30, 0, 1.88, 0.40, 0.40, 1.60)
    # Left fist
    box(-1.30, 0, 1.05, 0.55, 0.55, 0.55)
    # Right fist
    box( 1.30, 0, 1.05, 0.55, 0.55, 0.55)
    # Left leg
    box(-0.42, 0, 0.05, 0.45, 0.45, 0.90)
    # Right leg
    box( 0.42, 0, 0.05, 0.45, 0.45, 0.90)

    bm.normal_update()
    me = bpy.data.meshes.new('Glaciara_Body_Mesh')
    bm.to_mesh(me); bm.free()

    body = bpy.data.objects.new('Glaciara_Body', me)
    bpy.context.scene.collection.objects.link(body)

    mat = bpy.data.materials.new('Mat_Glaciara_Placeholder')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value     = (0.70, 0.88, 1.00, 1.0)
        bsdf.inputs['Roughness'].default_value      = 0.05
        bsdf.inputs['Transmission Weight'].default_value = 0.4
        bsdf.inputs['Emission Color'].default_value = (0.30, 0.80, 1.00, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 0.5
    body.data.materials.append(mat)
    return body


# ─────────────────────────────────────────────────────
#  BONE COLOURS
# ─────────────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    spine  = ['Root','Pelvis','Spine1','Spine2','Spine3','Spine4','Neck','Head']
    left   = [n for n in list(BONES) if n.startswith('L_')]
    right  = [n for n in list(BONES) if n.startswith('R_')]
    cape   = ['Cape_L','Cape_C','Cape_R']
    ik     = [n for n in pb.keys() if n.startswith('IK_') or n.startswith('Pole_')]
    crown  = [n for n in EXTRA_BONES if n.startswith('IceCrown')]
    ctrl   = ['ChestCore','IceShard_Ctrl','IceWall_Ctrl']

    for b in spine:
        if b in pb: pb[b].color.palette = 'THEME01'   # red
    for b in left:
        if b in pb: pb[b].color.palette = 'THEME04'   # green
    for b in right:
        if b in pb: pb[b].color.palette = 'THEME03'   # blue
    for b in cape:
        if b in pb: pb[b].color.palette = 'THEME05'   # purple
    for b in ik:
        if b in pb: pb[b].color.palette = 'THEME10'   # cyan
    for b in crown:
        if b in pb: pb[b].color.palette = 'THEME08'   # white/light
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
    print("  IsleTrial — Glaciara FrostWarden Rig Report")
    print("="*60)
    print(f"  Armature     : {arm_obj.name}")
    print(f"  Total bones  : {total}")
    print(f"  Deform bones : {deform}")
    print(f"  IK/control   : {total - deform}")
    print(f"\n  Unity import:")
    print("    Rig Type: Generic   Root Bone: Root")
    print("    Scale: 1.0   Axis: Y Up, -Z Forward")
    print(f"\n  Animation clips needed (Phase 1 / 2 / 3):")
    for clip in ['Idle','Walk','Roar_Phase1','Roar_Phase2','Roar_Phase3',
                 'Attack_FistSlam_L','Attack_FistSlam_R','Attack_DoubleSlam',
                 'Attack_IceShard','Attack_IceWall','Attack_Blizzard',
                 'CrownFlare','PhaseTransition','TakeDamage','Death','Frozen']:
        print(f"    {clip}")
    print(f"\n  Unity notes:")
    print("    IceCrown_* scale: Animator param 'CrownSize' (0→1) — grows on phase shift")
    print("    ChestCore: link to chest glow Point Light transform")
    print("    IceShard_Ctrl: Instantiate IceShard prefab here (from script 43)")
    print("    IceWall_Ctrl: Instantiate IceWall prefab here (from script 43)")
    print("    Cape_L/C/R: add Cloth/Spring Joint in Unity for physics drape")
    print("="*60 + "\n")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def main():
    clear_scene()
    print("\n[GlaciaraRig] Building armature...")
    arm_obj = build_armature()

    print("[GlaciaraRig] Adding IK targets...")
    add_ik_targets(arm_obj)

    print("[GlaciaraRig] Adding rotation limits...")
    add_rotation_limits(arm_obj)

    print("[GlaciaraRig] Building placeholder body...")
    body_obj = build_body_mesh()

    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True); arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    print("[GlaciaraRig] Colouring bones...")
    color_bones(arm_obj)

    activate(arm_obj)
    arm_obj.data.display_type = 'OCTAHEDRAL'
    arm_obj.show_in_front = True

    print_report(arm_obj)

main()
