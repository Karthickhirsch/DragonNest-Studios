"""
IsleTrial – Sea Creature 04-A: Large Fish  (Rig + Shape Keys)
==============================================================
Armature: Fish_Armature
Bones:
  Bone_Root                  – world anchor
  Bone_Body_01..03           – spine chain tail → chest
  Bone_Head                  – head
  Bone_Jaw                   – lower jaw (child of Bone_Head)
  Bone_Tail_01               – first tail segment
  Bone_Tail_02               – tail fork (child of Bone_Tail_01)
  Bone_DorsalFin             – dorsal fin root
  Bone_PectoralFin_L/R       – pectoral fin roots

Shape Keys on Fish_Body:
  Basis / Swim_Left / Swim_Right / Mouth_Open / Idle_Breathe

Run AFTER 15_LargeFish.py inside Blender ▸ Scripting tab.
"""

import bpy, math
from mathutils import Vector

# ─────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────

def get_obj(name):
    return bpy.data.objects.get(name)

def deselect_all():
    bpy.ops.object.select_all(action='DESELECT')

def set_active(obj):
    deselect_all()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

def get_col(name):
    return bpy.data.collections.get(name)

def link_to_col(col, obj):
    if col and obj.name not in col.objects:
        col.objects.link(obj)

# ─────────────────────────────────────────────────────────────────
#  BUILD ARMATURE
# ─────────────────────────────────────────────────────────────────

def build_fish_armature():
    """Create Fish_Armature with full spine, fin, jaw chain."""
    deselect_all()
    bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = 'Fish_Armature'
    arm_obj.data.name = 'Fish_ArmatureData'
    arm_obj.show_in_front = True

    set_active(arm_obj)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_obj.data.edit_bones

    # Remove default bone
    for b in list(eb): eb.remove(b)

    def add_bone(name, head, tail, parent=None, roll=0.0):
        bone = eb.new(name)
        bone.head = Vector(head); bone.tail = Vector(tail)
        bone.roll = roll
        if parent: bone.parent = eb[parent]; bone.use_connect = False
        return bone

    # Fish body Y axis: tail = -1.25, head = +1.25
    # ── Root ──
    add_bone('Bone_Root',     (0, 0, 0),       (0, 0.10, 0))

    # ── Spine chain: tail → head ──
    add_bone('Bone_Body_01',  (0,-1.10, 0),    (0,-0.60, 0), 'Bone_Root')   # tail section
    add_bone('Bone_Body_02',  (0,-0.60, 0),    (0, 0.00, 0), 'Bone_Body_01') # mid body
    add_bone('Bone_Body_03',  (0, 0.00, 0),    (0, 0.62, 0), 'Bone_Body_02') # chest/shoulder
    add_bone('Bone_Head',     (0, 0.62, 0),    (0, 1.20, 0), 'Bone_Body_03') # head

    # ── Jaw ──
    add_bone('Bone_Jaw',      (0, 1.05,-0.05), (0, 1.22,-0.12), 'Bone_Head')

    # ── Tail segment chain ──
    add_bone('Bone_Tail_01',  (0,-1.10, 0),    (0,-1.20, 0), 'Bone_Body_01')
    add_bone('Bone_Tail_02',  (0,-1.20, 0),    (0,-1.30, 0), 'Bone_Tail_01')

    # ── Dorsal fin ──
    add_bone('Bone_DorsalFin',(0, 0.05, 0.24), (0, 0.05, 0.48), 'Bone_Body_03')

    # ── Pectoral fins ──
    add_bone('Bone_PectoralFin_R', (0.28, 0.38,-0.04), (0.50, 0.55,-0.10), 'Bone_Body_03')
    add_bone('Bone_PectoralFin_L',(-0.28, 0.38,-0.04),(-0.50, 0.55,-0.10), 'Bone_Body_03')

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

# ─────────────────────────────────────────────────────────────────
#  SKIN FISH BODY TO ARMATURE
# ─────────────────────────────────────────────────────────────────

def skin_body(arm_obj):
    """Parent Fish_Body to armature with Automatic Weights."""
    body = get_obj('Fish_Body')
    if body is None: print("  [WARN] Fish_Body not found – run 15_LargeFish.py first"); return
    deselect_all()
    body.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    print("  Fish_Body parented to armature (Automatic Weights).")

def skin_fins(arm_obj):
    """Assign fin objects to their respective armature bones via parenting."""
    fin_bones = {
        'Fish_DorsalFin'       : 'Bone_DorsalFin',
        'Fish_PectoralFin_L'   : 'Bone_PectoralFin_L',
        'Fish_PectoralFin_R'   : 'Bone_PectoralFin_R',
        'Fish_TailFin'         : 'Bone_Tail_02',
        'Fish_AnalFin'         : 'Bone_Tail_01',
        'Fish_PelvicFin_L'     : 'Bone_Body_02',
        'Fish_PelvicFin_R'     : 'Bone_Body_02',
    }
    for obj_name, bone_name in fin_bones.items():
        obj = get_obj(obj_name)
        if obj is None: continue
        obj.parent = arm_obj
        obj.parent_type = 'BONE'
        obj.parent_bone = bone_name
        obj.matrix_parent_inverse = arm_obj.matrix_world.inverted()
    print("  Fins parented to bone targets.")

# ─────────────────────────────────────────────────────────────────
#  SHAPE KEYS
# ─────────────────────────────────────────────────────────────────

def build_shape_keys():
    """Add swim, jaw, and breathe shape keys to Fish_Body."""
    body = get_obj('Fish_Body')
    if body is None: print("  [WARN] Fish_Body not found."); return

    set_active(body)
    mesh = body.data

    # Helper: add a shape key from Basis
    def add_key(name):
        body.shape_key_add(name=name, from_mix=False)
        return mesh.shape_keys.key_blocks[name]

    # Basis
    if mesh.shape_keys is None:
        body.shape_key_add(name='Basis', from_mix=False)
    else:
        mesh.shape_keys.key_blocks[0].name = 'Basis'

    basis_verts = [v.co.copy() for v in mesh.vertices]

    # ── Swim_Left: tail curves left (negative X) ──
    sk_l = add_key('Swim_Left')
    for i, v in enumerate(mesh.vertices):
        co = basis_verts[i].copy()
        y_norm = (co.y + 1.25) / 2.50  # 0=head, 1=tail normalised
        deflection = math.sin(y_norm * math.pi * 0.5) * 0.28 * y_norm
        co.x -= deflection
        sk_l.data[i].co = co

    # ── Swim_Right: tail curves right (+X) ──
    sk_r = add_key('Swim_Right')
    for i, v in enumerate(mesh.vertices):
        co = basis_verts[i].copy()
        y_norm = (co.y + 1.25) / 2.50
        deflection = math.sin(y_norm * math.pi * 0.5) * 0.28 * y_norm
        co.x += deflection
        sk_r.data[i].co = co

    # ── Mouth_Open: drop lower jaw vertices ──
    sk_m = add_key('Mouth_Open')
    for i, v in enumerate(mesh.vertices):
        co = basis_verts[i].copy()
        # Lower-front head vertices drop down
        if co.y > 0.90 and co.z < 0.0:
            weight = max(0, (co.y - 0.90) / 0.35) * max(0, (-co.z) / 0.12)
            co.z -= weight * 0.10
            co.y += weight * 0.04
        sk_m.data[i].co = co

    # ── Idle_Breathe: slight puff of gill/shoulder area ──
    sk_b = add_key('Idle_Breathe')
    for i, v in enumerate(mesh.vertices):
        co = basis_verts[i].copy()
        # Gill zone: Y 0.4–0.75
        if 0.40 < co.y < 0.75:
            t = (co.y - 0.40) / 0.35
            puff = math.sin(t * math.pi) * 0.038
            dist = math.sqrt(co.x**2 + co.z**2)
            if dist > 0.001:
                co.x += co.x / dist * puff
                co.z += co.z / dist * puff * 0.7
        sk_b.data[i].co = co

    print("  Shape keys created: Basis, Swim_Left, Swim_Right, Mouth_Open, Idle_Breathe")

# ─────────────────────────────────────────────────────────────────
#  IK CONSTRAINTS FOR FISH SPINE
# ─────────────────────────────────────────────────────────────────

def add_ik_target(arm_obj):
    """Add IK target empty for tail-driven swim animation."""
    bpy.ops.object.empty_add(type='SPHERE', location=(0, -1.35, 0))
    ik_target = bpy.context.active_object
    ik_target.name = 'Fish_IK_TailTarget'
    ik_target.empty_display_size = 0.10

    # Parent to root empty if it exists
    root = get_obj('Fish_ROOT')
    if root: ik_target.parent = root

    # Add IK constraint on Bone_Body_01
    set_active(arm_obj)
    bpy.ops.object.mode_set(mode='POSE')
    pb = arm_obj.pose.bones.get('Bone_Tail_02')
    if pb:
        ik = pb.constraints.new('IK')
        ik.target = ik_target
        ik.chain_count = 4
        ik.use_location = True
        ik.influence = 0.80
    bpy.ops.object.mode_set(mode='OBJECT')
    print("  IK tail target: Fish_IK_TailTarget (chain length 4)")

def add_rotation_limits(arm_obj):
    """Add rotation limits to spine bones for realistic bend."""
    set_active(arm_obj)
    bpy.ops.object.mode_set(mode='POSE')
    limits = {
        'Bone_Body_01': ((-20, 20), (-12, 12), (-30, 30)),
        'Bone_Body_02': ((-15, 15), (-10, 10), (-25, 25)),
        'Bone_Body_03': ((-12, 12), (-8,  8),  (-18, 18)),
        'Bone_Tail_01': ((-18, 18), (-8,  8),  (-35, 35)),
        'Bone_Tail_02': ((-12, 12), (-5,  5),  (-28, 28)),
        'Bone_Jaw':     ((-40, 0),  (-5,  5),  (-5,   5)),
    }
    for bname, (rx, ry, rz) in limits.items():
        pb = arm_obj.pose.bones.get(bname)
        if pb is None: continue
        c = pb.constraints.new('LIMIT_ROTATION')
        c.use_limit_x = True; c.min_x = math.radians(rx[0]); c.max_x = math.radians(rx[1])
        c.use_limit_y = True; c.min_y = math.radians(ry[0]); c.max_y = math.radians(ry[1])
        c.use_limit_z = True; c.min_z = math.radians(rz[0]); c.max_z = math.radians(rz[1])
        c.owner_space = 'LOCAL'
    bpy.ops.object.mode_set(mode='OBJECT')
    print("  Rotation limits applied to spine + jaw bones.")

# ─────────────────────────────────────────────────────────────────
#  PARENT TO COLLECTION
# ─────────────────────────────────────────────────────────────────

def attach_to_scene(arm_obj):
    col = get_col('IsleTrial_Fish')
    if col: link_to_col(col, arm_obj)
    root = get_obj('Fish_ROOT')
    if root: arm_obj.parent = root
    # Attach armature modifier to body
    body = get_obj('Fish_Body')
    if body:
        mod = body.modifiers.new('FishArmature', 'ARMATURE')
        mod.object = arm_obj
        # Move armature modifier before Sub/Solidify
        while body.modifiers[0].name != 'FishArmature':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = body
            body.select_set(True)
            bpy.ops.object.modifier_move_up({'object': body}, modifier='FishArmature')

# ─────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    arm_obj = build_fish_armature()
    skin_body(arm_obj)
    skin_fins(arm_obj)
    build_shape_keys()
    add_ik_target(arm_obj)
    add_rotation_limits(arm_obj)
    attach_to_scene(arm_obj)

    deselect_all()
    bpy.context.view_layer.objects.active = arm_obj

    bone_count = len(arm_obj.data.bones)
    print("=" * 60)
    print("[IsleTrial] Large Fish RIG built successfully.")
    print(f"  Armature  : Fish_Armature")
    print(f"  Bones     : {bone_count}")
    print(f"  Shape keys: Basis, Swim_Left, Swim_Right, Mouth_Open, Idle_Breathe")
    print()
    print("  Unity Animator setup:")
    print("    Rig Type → Generic  |  Root bone → Bone_Root")
    print("    Shape Keys → BlendShapes  |  Swim_Left + Swim_Right → swim cycle")
    print("    Bone_Jaw → jaw open/close animation")
    print("  Export: FBX | Armature ✓ | Mesh ✓ | Scale 0.01")
    print("=" * 60)

main()
