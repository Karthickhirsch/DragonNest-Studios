"""
IsleTrial – Sea Creature 04-B: Humpback Whale  (Rig + Shape Keys)
==================================================================
Armature: Whale_Armature
Bones:
  Bone_Root
  Bone_Body_01..05  – spine chain (tail→head)
  Bone_Head         – head
  Bone_Jaw_Lower    – lower jaw
  Bone_Flipper_L/R  – pectoral flipper roots
  Bone_Fluke_L/R    – fluke lobes

Shape Keys on Whale_Body:
  Basis / Breach_Arch / Dive_Curve / Tail_Up / Mouth_Open

Run AFTER 16_Whale.py inside Blender ▸ Scripting tab.
"""

import bpy, math
from mathutils import Vector

def get_obj(name): return bpy.data.objects.get(name)
def deselect_all(): bpy.ops.object.select_all(action='DESELECT')
def set_active(obj):
    deselect_all(); bpy.context.view_layer.objects.active = obj; obj.select_set(True)

def build_whale_armature():
    deselect_all()
    bpy.ops.object.armature_add(enter_editmode=False, location=(0,0,0))
    arm = bpy.context.active_object
    arm.name = 'Whale_Armature'; arm.data.name = 'Whale_ArmatureData'
    arm.show_in_front = True
    set_active(arm)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    for b in list(eb): eb.remove(b)

    def ab(name, head, tail, parent=None):
        b = eb.new(name); b.head = Vector(head); b.tail = Vector(tail)
        if parent: b.parent = eb[parent]; b.use_connect = False
        return b

    # Spine (tail Y=-7 → head Y=+7)
    ab('Bone_Root',     (0, 0, 0),         (0, 0.15, 0))
    ab('Bone_Body_01',  (0,-6.50, 0),       (0,-4.50, 0), 'Bone_Root')   # tail stock
    ab('Bone_Body_02',  (0,-4.50, 0),       (0,-2.00, 0), 'Bone_Body_01') # rear body
    ab('Bone_Body_03',  (0,-2.00, 0),       (0, 1.00, 0), 'Bone_Body_02') # mid body (hump)
    ab('Bone_Body_04',  (0, 1.00, 0),       (0, 4.00, 0), 'Bone_Body_03') # chest
    ab('Bone_Body_05',  (0, 4.00, 0),       (0, 6.20, 0), 'Bone_Body_04') # neck
    ab('Bone_Head',     (0, 6.20, 0),       (0, 7.00, 0), 'Bone_Body_05')
    ab('Bone_Jaw_Lower',(0, 6.50,-0.25),    (0, 7.00,-0.45), 'Bone_Head')

    # Flukes
    ab('Bone_Fluke_L',  (0,-7.00, 0),       (-1.80,-7.40,-0.10), 'Bone_Body_01')
    ab('Bone_Fluke_R',  (0,-7.00, 0),       ( 1.80,-7.40,-0.10), 'Bone_Body_01')

    # Flippers
    ab('Bone_Flipper_L',(-2.10,-0.50,-0.20),(-3.40, 1.80,-0.38), 'Bone_Body_03')
    ab('Bone_Flipper_R',( 2.10,-0.50,-0.20),( 3.40, 1.80,-0.38), 'Bone_Body_03')

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm

def skin_whale(arm):
    body = get_obj('Whale_Body')
    if body:
        deselect_all(); body.select_set(True); arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for oname, bname in [('Whale_Flipper_L','Bone_Flipper_L'),('Whale_Flipper_R','Bone_Flipper_R'),
                          ('Whale_Flukes','Bone_Body_01'),('Whale_DorsalHump','Bone_Body_03')]:
        obj = get_obj(oname)
        if obj: obj.parent = arm; obj.parent_type = 'BONE'; obj.parent_bone = bname
    print("  Whale_Body skinned. Flippers + Flukes parented to bones.")

def build_shape_keys():
    body = get_obj('Whale_Body')
    if not body: print("  [WARN] Whale_Body not found."); return
    set_active(body); mesh = body.data
    if mesh.shape_keys is None: body.shape_key_add(name='Basis', from_mix=False)
    else: mesh.shape_keys.key_blocks[0].name = 'Basis'
    basis = [v.co.copy() for v in mesh.vertices]

    def add_key(name): body.shape_key_add(name=name, from_mix=False); return mesh.shape_keys.key_blocks[name]

    # Breach_Arch: body arched upward
    sk_ba = add_key('Breach_Arch')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        y_n = (co.y + 7.0) / 14.0   # 0=tail, 1=head
        arch = math.sin(y_n * math.pi) * 1.80
        co.z += arch
        sk_ba.data[i].co = co

    # Dive_Curve: body curved downward
    sk_dc = add_key('Dive_Curve')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        y_n = (co.y + 7.0) / 14.0
        curve = math.sin(y_n * math.pi) * 1.50
        co.z -= curve
        sk_dc.data[i].co = co

    # Tail_Up: tail section raised (fluke display)
    sk_tu = add_key('Tail_Up')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        if co.y < -3.0:
            weight = min(1.0, (-3.0 - co.y) / 4.0)
            co.z += weight * 1.60
        sk_tu.data[i].co = co

    # Mouth_Open: lower jaw dropped
    sk_mo = add_key('Mouth_Open')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        if co.y > 5.5 and co.z < 0:
            w = max(0, (co.y - 5.5) / 1.5) * max(0, (-co.z - 0.2) / 1.0)
            co.z -= w * 1.20
            co.y += w * 0.15
        sk_mo.data[i].co = co

    print("  Shape keys: Basis, Breach_Arch, Dive_Curve, Tail_Up, Mouth_Open")

def add_rotation_limits(arm):
    set_active(arm); bpy.ops.object.mode_set(mode='POSE')
    limits = {
        'Bone_Body_01': ((-20,20),(-8,8),(-30,30)),
        'Bone_Body_02': ((-18,18),(-6,6),(-25,25)),
        'Bone_Body_03': ((-12,12),(-5,5),(-18,18)),
        'Bone_Body_04': ((-10,10),(-4,4),(-12,12)),
        'Bone_Body_05': ((-8,8),(-4,4),(-10,10)),
        'Bone_Jaw_Lower':((-45,5),(-5,5),(-5,5)),
        'Bone_Fluke_L':  ((-25,25),(-25,25),(-20,20)),
        'Bone_Fluke_R':  ((-25,25),(-25,25),(-20,20)),
        'Bone_Flipper_L':((-30,30),(-20,20),(-35,35)),
        'Bone_Flipper_R':((-30,30),(-20,20),(-35,35)),
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
    print("  Rotation limits applied.")

def main():
    arm = build_whale_armature()
    skin_whale(arm)
    build_shape_keys()
    add_rotation_limits(arm)
    col = bpy.data.collections.get('IsleTrial_Whale')
    if col and arm.name not in col.objects: col.objects.link(arm)
    root = get_obj('Whale_ROOT')
    if root: arm.parent = root
    deselect_all(); bpy.context.view_layer.objects.active = arm
    print("=" * 60)
    print("[IsleTrial] Humpback Whale RIG built.")
    print(f"  Bones     : {len(arm.data.bones)}")
    print("  Shape keys: Basis, Breach_Arch, Dive_Curve, Tail_Up, Mouth_Open")
    print("  Unity: Rig → Generic | Root → Bone_Root | BlendShapes for animations")
    print("=" * 60)

main()
