"""
IsleTrial – Sea Creature 04-C: Great White Shark  (Rig + Shape Keys)
=====================================================================
Armature: Shark_Armature
Bones:
  Bone_Root, Bone_Body_01..04, Bone_Head, Bone_Jaw,
  Bone_DorsalFin, Bone_Tail,
  Bone_Pectoral_L, Bone_Pectoral_R

Shape Keys on Shark_Body:
  Basis / Attack_Open / Swim_Curve_L / Swim_Curve_R / Gill_Flare

Run AFTER 17_Shark.py inside Blender ▸ Scripting tab.
"""

import bpy, math
from mathutils import Vector

def get_obj(name): return bpy.data.objects.get(name)
def deselect_all(): bpy.ops.object.select_all(action='DESELECT')
def set_active(obj):
    deselect_all(); bpy.context.view_layer.objects.active = obj; obj.select_set(True)

def build_shark_armature():
    deselect_all()
    bpy.ops.object.armature_add(enter_editmode=False, location=(0,0,0))
    arm = bpy.context.active_object
    arm.name = 'Shark_Armature'; arm.data.name = 'Shark_ArmatureData'
    arm.show_in_front = True
    set_active(arm); bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    for b in list(eb): eb.remove(b)

    def ab(name, head, tail, parent=None):
        b = eb.new(name); b.head=Vector(head); b.tail=Vector(tail)
        if parent: b.parent=eb[parent]; b.use_connect=False
        return b

    # Spine Y: tail=-2.5, head=+2.5
    ab('Bone_Root',      (0, 0,0),        (0, 0.10,0))
    ab('Bone_Body_01',   (0,-2.20,0),     (0,-1.40,0), 'Bone_Root')    # tail
    ab('Bone_Body_02',   (0,-1.40,0),     (0,-0.40,0), 'Bone_Body_01') # rear
    ab('Bone_Body_03',   (0,-0.40,0),     (0, 0.60,0), 'Bone_Body_02') # mid
    ab('Bone_Body_04',   (0, 0.60,0),     (0, 1.42,0), 'Bone_Body_03') # chest
    ab('Bone_Head',      (0, 1.42,0),     (0, 2.38,0), 'Bone_Body_04')
    ab('Bone_Jaw',       (0, 1.80,-0.05), (0, 2.20,-0.14), 'Bone_Head')
    ab('Bone_Tail',      (0,-2.20,0),     (0,-2.50,0), 'Bone_Body_01')
    ab('Bone_DorsalFin', (0,-0.20,0.38),  (0,-0.20,0.88), 'Bone_Body_03')
    ab('Bone_Pectoral_R',(0.48, 0.10,-0.10),(0.90,0.55,-0.22),'Bone_Body_04')
    ab('Bone_Pectoral_L',(-0.48,0.10,-0.10),(-0.90,0.55,-0.22),'Bone_Body_04')

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm

def skin_shark(arm):
    body = get_obj('Shark_Body')
    if body:
        deselect_all(); body.select_set(True); arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    fin_bones = {'Shark_DorsalFin_Main':'Bone_DorsalFin','Shark_DorsalFin_2nd':'Bone_Tail',
                 'Shark_CaudalFin':'Bone_Tail','Shark_PectoralFin_L':'Bone_Pectoral_L',
                 'Shark_PectoralFin_R':'Bone_Pectoral_R','Shark_PelvicFin_L':'Bone_Body_02',
                 'Shark_PelvicFin_R':'Bone_Body_02','Shark_AnalFin':'Bone_Tail'}
    for oname, bname in fin_bones.items():
        obj = get_obj(oname)
        if obj: obj.parent=arm; obj.parent_type='BONE'; obj.parent_bone=bname
    print("  Shark skinned to armature.")

def build_shape_keys():
    body = get_obj('Shark_Body')
    if not body: print("  [WARN] Shark_Body not found."); return
    set_active(body); mesh = body.data
    if mesh.shape_keys is None: body.shape_key_add(name='Basis',from_mix=False)
    else: mesh.shape_keys.key_blocks[0].name='Basis'
    basis = [v.co.copy() for v in mesh.vertices]
    def add_key(name): body.shape_key_add(name=name,from_mix=False); return mesh.shape_keys.key_blocks[name]

    # Attack_Open: jaw open, snout raised
    sk_a = add_key('Attack_Open')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        if co.y > 1.40:
            w = (co.y - 1.40) / 1.10
            if co.z < 0:
                co.z -= w * 0.18; co.y += w * 0.06  # drop jaw
            else:
                co.z += w * 0.06                      # lift snout
        sk_a.data[i].co = co

    # Swim_Curve_L: aggressive S-curve body, tail left
    sk_l = add_key('Swim_Curve_L')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        y_n = (co.y + 2.5) / 5.0
        co.x -= math.sin(y_n * math.pi * 1.4) * 0.30 * y_n
        sk_l.data[i].co = co

    # Swim_Curve_R: tail right
    sk_r = add_key('Swim_Curve_R')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        y_n = (co.y + 2.5) / 5.0
        co.x += math.sin(y_n * math.pi * 1.4) * 0.30 * y_n
        sk_r.data[i].co = co

    # Gill_Flare: gills slightly open
    sk_g = add_key('Gill_Flare')
    for i, v in enumerate(mesh.vertices):
        co = basis[i].copy()
        if 0.90 < co.y < 1.45 and abs(co.x) > 0.28:
            w = max(0, min(1, (abs(co.x)-0.28)/0.18))
            flar = math.sin((co.y - 0.90)/0.55 * math.pi) * 0.04 * w
            co.x += (1 if co.x > 0 else -1) * flar
        sk_g.data[i].co = co

    print("  Shape keys: Basis, Attack_Open, Swim_Curve_L, Swim_Curve_R, Gill_Flare")

def add_rotation_limits(arm):
    set_active(arm); bpy.ops.object.mode_set(mode='POSE')
    limits = {
        'Bone_Body_01':((-22,22),(-10,10),(-32,32)),
        'Bone_Body_02':((-18,18),(-8,8),(-28,28)),
        'Bone_Body_03':((-14,14),(-6,6),(-22,22)),
        'Bone_Body_04':((-10,10),(-5,5),(-15,15)),
        'Bone_Jaw':    ((-45,5),(-5,5),(-5,5)),
        'Bone_Tail':   ((-20,20),(-8,8),(-38,38)),
        'Bone_Pectoral_L':((-30,20),(-15,15),(-30,25)),
        'Bone_Pectoral_R':((-30,20),(-15,15),(-25,30)),
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
    arm = build_shark_armature()
    skin_shark(arm)
    build_shape_keys()
    add_rotation_limits(arm)
    col = bpy.data.collections.get('IsleTrial_Shark')
    if col and arm.name not in col.objects: col.objects.link(arm)
    root = get_obj('Shark_ROOT')
    if root: arm.parent = root
    deselect_all(); bpy.context.view_layer.objects.active = arm
    print("=" * 60)
    print("[IsleTrial] Great White Shark RIG built.")
    print(f"  Bones     : {len(arm.data.bones)}")
    print("  Shape keys: Basis, Attack_Open, Swim_Curve_L, Swim_Curve_R, Gill_Flare")
    print("  Unity: Rig → Generic | Root → Bone_Root")
    print("  Jaw animation: Bone_Jaw rotation X 0→-40° for bite")
    print("=" * 60)

main()
