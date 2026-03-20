"""
41_Enemy_FrostSlug_Rig.py
IsleTrial — FrostSlug Creature Rig
=====================================
Run AFTER 41_Enemy_FrostSlug.py in the same Blender scene.

Creature:  Large armoured frost slug  ~2 m long
Rig type:  Generic (not Humanoid — invertebrate creature)

Bone hierarchy:
  Root
  ├─ Spine1 → Spine2 → Spine3 → Spine4 → Spine5 → Head
  │               └─ Eyestalk_L / Eyestalk_R  (children of Head)
  ├─ Shell_1 … Shell_5  (children of respective Spine bones — pose control)
  └─ Tail  (child of Root — trailing slime body)

  Extra (non-deform):
  SlimeTrail       — drives slime trail length via scale
  FrostPatch_Ctrl  — prefab spawn control (scale to 0 when slug is alive)

IK: eyestalks track a look-at target (simple copy-rotation constraint)

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
#  Positions match exactly those in 41_Enemy_FrostSlug.py
# ─────────────────────────────────────────────────────

BONES = {
    # ── Core spine (body wave) ────────────────────────
    'Root':      ((0,0,0),        (0,0,0.30),     None,      False),
    'Spine1':    ((0,0,0.30),     (0,0,0.65),     'Root',    True),
    'Spine2':    ((0,0,0.65),     (0,0,1.00),     'Spine1',  True),
    'Spine3':    ((0,0,1.00),     (0,0,1.35),     'Spine2',  True),
    'Spine4':    ((0,0,1.35),     (0,0,1.65),     'Spine3',  True),
    'Spine5':    ((0,0,1.65),     (0,0,1.90),     'Spine4',  True),
    'Head':      ((0,0,1.90),     (0,0,2.22),     'Spine5',  True),

    # ── Eyestalks ────────────────────────────────────
    'Eyestalk_L':((-0.12,0.28,2.12),(-0.12,0.28,2.52),'Head',False),
    'Eyestalk_R':(( 0.12,0.28,2.12),( 0.12,0.28,2.52),'Head',False),

    # ── Shell plates (dorsal — rotate for recoil) ────
    'Shell_1':   ((0,0.32,0.40),  (0,0.32,0.60),  'Spine1',  False),
    'Shell_2':   ((0,0.32,0.75),  (0,0.32,0.95),  'Spine2',  False),
    'Shell_3':   ((0,0.32,1.05),  (0,0.32,1.25),  'Spine2',  False),
    'Shell_4':   ((0,0.32,1.35),  (0,0.32,1.55),  'Spine3',  False),
    'Shell_5':   ((0,0.32,1.60),  (0,0.32,1.78),  'Spine4',  False),

    # ── Tail ─────────────────────────────────────────
    'Tail':      ((0,0,0.00),     (0,0,-0.30),    'Root',    False),
}

EXTRA_BONES = {
    # Slime trail length control — scale Z to extend/contract trail
    'SlimeTrail':    ((0,-0.16,0.14),(0,-0.16,-0.80),'Root', False),
    # Frost patch prefab control — placed at world origin offset (Z=0)
    'FrostPatch_Ctrl':((0,0,-1.0),  (0,0,-1.20),    'Root', False),
}


# ─────────────────────────────────────────────────────
#  BUILD ARMATURE
# ─────────────────────────────────────────────────────

def build_armature():
    arm_data = bpy.data.armatures.new('FrostSlug_Armature_Data')
    arm_obj  = bpy.data.objects.new('FrostSlug_Armature', arm_data)
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

    # Shell bones are non-deform (they drive mesh via constraints)
    for shell in ['Shell_1','Shell_2','Shell_3','Shell_4','Shell_5']:
        if shell in eb: eb[shell].use_deform = False

    object_mode()
    return arm_obj


# ─────────────────────────────────────────────────────
#  CONSTRAINTS
# ─────────────────────────────────────────────────────

def add_constraints(arm_obj):
    # Eyestalk look-at empty
    edit_mode(arm_obj)
    eb = arm_obj.data.edit_bones
    b = eb.new('EyeTarget')
    b.head = Vector((0, 1.0, 2.30))
    b.tail = Vector((0, 1.0, 2.40))
    b.parent = eb['Root']
    b.use_deform = False
    object_mode()

    pose_mode(arm_obj)
    pb = arm_obj.pose.bones
    for stalk in ['Eyestalk_L','Eyestalk_R']:
        if stalk in pb:
            c = pb[stalk].constraints.new('DAMPED_TRACK')
            c.target    = arm_obj
            c.subtarget = 'EyeTarget'
            c.track_axis = 'TRACK_Y'

    # Jaw limit (no jaw on slug — head opens by scaling)
    # Shell recoil limits — shells only rotate back (Z axis)
    for shell in ['Shell_1','Shell_2','Shell_3','Shell_4','Shell_5']:
        if shell in pb:
            c = pb[shell].constraints.new('LIMIT_ROTATION')
            c.owner_space = 'LOCAL'
            c.use_limit_x = True; c.min_x = math.radians(-35); c.max_x = math.radians(10)
            c.use_limit_z = True; c.min_z = math.radians(-20); c.max_z = math.radians(20)

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

    # Spine — slugs undulate vertically and laterally
    for b in ['Spine1','Spine2','Spine3']:
        limit(b, True, True, True, xmn=-20, xmx=20, ymn=-30, ymx=30, zmn=-10, zmx=10)
    for b in ['Spine4','Spine5']:
        limit(b, True, True, True, xmn=-25, xmx=25, ymn=-35, ymx=35, zmn=-12, zmx=12)
    limit('Head', True, True, True, xmn=-40, xmx=40, ymn=-45, ymx=45, zmn=-20, zmx=20)
    limit('Tail', True, True, True, xmn=-15, xmx=15, ymn=-40, ymx=40, zmn=-10, zmx=10)

    # Eyestalks — wide independent range
    for e in ['Eyestalk_L','Eyestalk_R']:
        limit(e, True, True, True, xmn=-60, xmx=60, ymn=-60, ymx=60, zmn=-90, zmx=90)

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

    # Main body slug
    box(0, 0, 1.00,  0.62, 0.50, 1.70)
    # Head (slightly wider)
    box(0, 0, 2.08,  0.50, 0.44, 0.38)
    # Tail
    box(0, 0,-0.12,  0.30, 0.28, 0.30)

    bm.normal_update()
    me = bpy.data.meshes.new('FrostSlug_Body_Mesh')
    bm.to_mesh(me); bm.free()

    body = bpy.data.objects.new('FrostSlug_Body', me)
    bpy.context.scene.collection.objects.link(body)

    mat = bpy.data.materials.new('Mat_FrostSlug_Placeholder')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value     = (0.55, 0.70, 0.85, 1.0)
        bsdf.inputs['Roughness'].default_value      = 0.30
        bsdf.inputs['Emission Color'].default_value = (0.30, 0.80, 1.00, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 0.35
    body.data.materials.append(mat)
    return body


# ─────────────────────────────────────────────────────
#  BONE COLOURS
# ─────────────────────────────────────────────────────

def color_bones(arm_obj):
    pose_mode(arm_obj)
    pb = arm_obj.pose.bones

    spine  = ['Root','Spine1','Spine2','Spine3','Spine4','Spine5','Head','Tail']
    shell  = ['Shell_1','Shell_2','Shell_3','Shell_4','Shell_5']
    eyes   = ['Eyestalk_L','Eyestalk_R','EyeTarget']
    extras = list(EXTRA_BONES)

    for b in spine:
        if b in pb: pb[b].color.palette = 'THEME01'   # red
    for b in shell:
        if b in pb: pb[b].color.palette = 'THEME03'   # blue
    for b in eyes:
        if b in pb: pb[b].color.palette = 'THEME10'   # cyan
    for b in extras:
        if b in pb: pb[b].color.palette = 'THEME09'   # yellow

    object_mode()


# ─────────────────────────────────────────────────────
#  REPORT
# ─────────────────────────────────────────────────────

def print_report(arm_obj):
    total  = len(arm_obj.data.bones)
    deform = sum(1 for b in arm_obj.data.bones if b.use_deform)
    print("\n" + "="*60)
    print("  IsleTrial — FrostSlug Rig Report")
    print("="*60)
    print(f"  Armature     : {arm_obj.name}")
    print(f"  Total bones  : {total}")
    print(f"  Deform bones : {deform}")
    print(f"  IK/control   : {total - deform}")
    print(f"\n  Unity import:")
    print("    Rig Type: Generic   Root Bone: Root")
    print("    Scale: 1.0   Axis: Y Up, -Z Forward")
    print(f"\n  Animation clips needed:")
    for clip in ['Idle','SlideForward','TurnLeft','TurnRight','Attack_Spit',
                 'Attack_BodySlam','ShellRecoil','SlowEffect','TakeDamage','Death']:
        print(f"    {clip}")
    print(f"\n  Unity notes:")
    print("    SlimeTrail bone scale-Z → drives SlimeMaterial 'TrailLength' shader param")
    print("    FrostPatch_Ctrl scale → Instantiate FrostPatch prefab on death")
    print("="*60 + "\n")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def main():
    clear_scene()
    print("\n[FrostSlugRig] Building armature...")
    arm_obj = build_armature()

    print("[FrostSlugRig] Adding constraints...")
    add_constraints(arm_obj)

    print("[FrostSlugRig] Adding rotation limits...")
    add_rotation_limits(arm_obj)

    print("[FrostSlugRig] Building placeholder body...")
    body_obj = build_body_mesh()

    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True); arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    print("[FrostSlugRig] Colouring bones...")
    color_bones(arm_obj)

    activate(arm_obj)
    arm_obj.data.display_type = 'OCTAHEDRAL'
    arm_obj.show_in_front = True

    print_report(arm_obj)

main()
