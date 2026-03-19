"""
IsleTrial – Sea Creature 04-D: Small Tropical Fish  (Rig + Shape Keys)
=======================================================================
Armature: SmallFish_Armature
Bones (minimal — GPU instancing friendly):
  Bone_Root
  Bone_Spine_01   – rear body
  Bone_Spine_02   – mid body
  Bone_Tail       – tail segment (drives tail wag)

Shape Keys on SmallFish_Body:
  Basis / Swim_L / Swim_R

Design note:
  Keep bones at 4 total so the GPU skinning cost is minimal.
  Unity: use a simple looping animation clip (Swim_L → Swim_R).
  For schools of 100+ fish, use GPU Instancing in Unity renderer.

Run AFTER 18_SmallFish.py inside Blender ▸ Scripting tab.
"""

import bpy, math
from mathutils import Vector

def get_obj(name): return bpy.data.objects.get(name)
def deselect_all(): bpy.ops.object.select_all(action='DESELECT')
def set_active(obj):
    deselect_all(); bpy.context.view_layer.objects.active = obj; obj.select_set(True)

def build_armature():
    deselect_all()
    bpy.ops.object.armature_add(enter_editmode=False, location=(0,0,0))
    arm = bpy.context.active_object
    arm.name = 'SmallFish_Armature'; arm.data.name = 'SmallFish_ArmatureData'
    arm.show_in_front = True
    set_active(arm); bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    for b in list(eb): eb.remove(b)

    def ab(name, head, tail, parent=None):
        b = eb.new(name); b.head=Vector(head); b.tail=Vector(tail)
        if parent: b.parent=eb[parent]; b.use_connect=False
        return b

    # Fish body Y: tail=-0.15, head=+0.15
    ab('Bone_Root',     (0, 0,    0),    (0, 0.01, 0))
    ab('Bone_Spine_01', (0,-0.12, 0),   (0,-0.04, 0), 'Bone_Root')    # rear
    ab('Bone_Spine_02', (0,-0.04, 0),   (0, 0.08, 0), 'Bone_Spine_01') # mid
    ab('Bone_Tail',     (0,-0.12, 0),   (0,-0.16, 0), 'Bone_Spine_01') # tail segment

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm

def skin_fish(arm):
    body = get_obj('SmallFish_Body')
    if body:
        deselect_all(); body.select_set(True); arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for oname, bname in [('SmallFish_DorsalFin','Bone_Spine_02'),
                          ('SmallFish_TailFin','Bone_Tail'),
                          ('SmallFish_PectoralFin_L','Bone_Spine_02'),
                          ('SmallFish_PectoralFin_R','Bone_Spine_02')]:
        obj = get_obj(oname)
        if obj: obj.parent=arm; obj.parent_type='BONE'; obj.parent_bone=bname
    print("  SmallFish_Body skinned to armature.")

def build_shape_keys():
    body = get_obj('SmallFish_Body')
    if not body: print("  [WARN] SmallFish_Body not found."); return
    set_active(body); mesh = body.data
    if mesh.shape_keys is None: body.shape_key_add(name='Basis',from_mix=False)
    else: mesh.shape_keys.key_blocks[0].name='Basis'
    basis = [v.co.copy() for v in mesh.vertices]
    def add_key(name): body.shape_key_add(name=name,from_mix=False); return mesh.shape_keys.key_blocks[name]

    # Swim_L: tail wags left
    sk_l = add_key('Swim_L')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        y_n = max(0, (-co.y + 0.0) / 0.15)   # 0 at mid, 1 at tail
        co.x -= math.sin(y_n * math.pi * 0.6) * 0.055 * y_n
        sk_l.data[i].co = co

    # Swim_R: tail wags right
    sk_r = add_key('Swim_R')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        y_n = max(0, (-co.y + 0.0) / 0.15)
        co.x += math.sin(y_n * math.pi * 0.6) * 0.055 * y_n
        sk_r.data[i].co = co

    print("  Shape keys: Basis, Swim_L, Swim_R")

def add_rotation_limits(arm):
    set_active(arm); bpy.ops.object.mode_set(mode='POSE')
    limits = {
        'Bone_Spine_01':((-14,14),(-5,5),(-22,22)),
        'Bone_Spine_02':((-10,10),(-4,4),(-16,16)),
        'Bone_Tail':    ((-12,12),(-4,4),(-28,28)),
    }
    for bname,(rx,ry,rz) in limits.items():
        pb = arm.pose.bones.get(bname)
        if pb is None: continue
        c = pb.constraints.new('LIMIT_ROTATION')
        c.use_limit_x=True; c.min_x=math.radians(rx[0]); c.max_x=math.radians(rx[1])
        c.use_limit_y=True; c.min_y=math.radians(ry[0]); c.max_y=math.radians(ry[1])
        c.use_limit_z=True; c.min_z=math.radians(rz[0]); c.max_z=math.radians(rz[1])
        c.owner_space='LOCAL'
    bpy.ops.object.mode_set(mode='OBJECT')

def main():
    arm = build_armature()
    skin_fish(arm)
    build_shape_keys()
    add_rotation_limits(arm)
    col = bpy.data.collections.get('IsleTrial_SmallFish')
    if col and arm.name not in col.objects: col.objects.link(arm)
    root = get_obj('SmallFish_ROOT')
    if root: arm.parent = root
    deselect_all(); bpy.context.view_layer.objects.active = arm
    print("=" * 60)
    print("[IsleTrial] Small Fish RIG built.")
    print(f"  Bones     : {len(arm.data.bones)}  (GPU-instancing friendly)")
    print("  Shape keys: Basis, Swim_L, Swim_R")
    print()
    print("  Unity animation setup:")
    print("    1. Create Animation clip 'Fish_Swim' (0.8s loop)")
    print("    2. Bone_Tail: Z rotate -20° at 0s → +20° at 0.4s → -20° at 0.8s")
    print("    3. Enable GPU Instancing on SmallFish material")
    print("    4. Use Unity ParticleSystem with Render → Mesh for school")
    print("=" * 60)

main()
