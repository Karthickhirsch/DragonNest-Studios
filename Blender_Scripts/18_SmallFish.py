"""
IsleTrial – Sea Creature 04-D: Small Tropical Fish  (Model)
============================================================
Type    Tropical reef fish (angelfish shape) — GPU instancing swarms
Size    0.3 m long × 0.25 m tall × 0.08 m wide
Poly    Target 400–800 triangles (spawned in hundreds)

Parts built:
  SmallFish_Body         – laterally compressed oval bmesh body
  SmallFish_DorsalFin    – fan-shaped top fin
  SmallFish_TailFin      – forked symmetrical tail
  SmallFish_PectoralFin_L/R – small oval fins
  SmallFish_Eye_L/R      – simple sphere 0.012m

Materials: dual-path procedural + [UNITY] image slots
  Bright orange body with white stripe band

After creation: sets up a Particle System on a plane (50 fish preview).

Run BEFORE 18_SmallFish_Rig.py inside Blender ▸ Scripting tab.
"""

import bpy, bmesh, math
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)

def new_col(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c); return c

def link(col, obj):
    for ex in list(obj.users_collection): ex.objects.unlink(obj)
    col.objects.link(obj)

def add_sub(obj, lv=1):
    m = obj.modifiers.new('Sub', 'SUBSURF'); m.levels = lv; m.render_levels = lv

def add_solidify(obj, t=0.008):
    m = obj.modifiers.new('Solid', 'SOLIDIFY'); m.thickness = t; m.offset = 0.0

def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj; obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT'); obj.select_set(False)

def prim(tp, name, loc=(0,0,0), rot=(0,0,0), size=1.0, **kw):
    if tp=='sphere': bpy.ops.mesh.primitive_uv_sphere_add(radius=size,location=loc,rotation=rot,segments=kw.get('segs',14),ring_count=kw.get('rings',10))
    elif tp=='cyl':  bpy.ops.mesh.primitive_cylinder_add(radius=size,depth=kw.get('depth',1.0),location=loc,rotation=rot,vertices=kw.get('verts',10))
    obj = bpy.context.active_object; obj.name = name; return obj

def assign_mat(obj, mat):
    if obj.data.materials: obj.data.materials[0] = mat
    else: obj.data.materials.append(mat)

# ── Materials ──────────────────────────────────────────────────────

def _n(nd, ntype, loc, label=None):
    n = nd.new(ntype); n.location=loc
    if label: n.label=n.name=label; return n

def _img(nd, sname, loc):
    n = nd.new('ShaderNodeTexImage'); n.location=loc
    n.label=n.name=f'[UNITY] {sname}'; return n

def _mapping(nd, lk, scale=(8,8,8), loc=(-800,0)):
    tc=_n(nd,'ShaderNodeTexCoord',(loc[0]-150,loc[1]))
    mp=_n(nd,'ShaderNodeMapping',loc); mp.inputs['Scale'].default_value=(*scale,)
    lk.new(tc.outputs['UV'],mp.inputs['Vector']); return mp

def _mix_pi(nd, lk, proc, img_n, loc):
    mix=_n(nd,'ShaderNodeMixRGB',loc); mix.blend_type='MIX'; mix.inputs[0].default_value=0.0
    lk.new(proc,mix.inputs[1]); lk.new(img_n.outputs['Color'],mix.inputs[2]); return mix

def _base(name):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    nd=mat.node_tree.nodes; lk=mat.node_tree.links; nd.clear()
    bsdf=_n(nd,'ShaderNodeBsdfPrincipled',(500,0)); out=_n(nd,'ShaderNodeOutputMaterial',(800,0))
    lk.new(bsdf.outputs['BSDF'],out.inputs['Surface']); return mat,nd,lk,bsdf

def mat_orange(name):
    mat,nd,lk,bsdf=_base(name)
    mp=_mapping(nd,lk,scale=(6,6,6))
    noise=_n(nd,'ShaderNodeTexNoise',(-400,100)); noise.inputs['Scale'].default_value=10.0
    lk.new(mp.outputs['Vector'],noise.inputs['Vector'])
    cr=_n(nd,'ShaderNodeValToRGB',(-100,100))
    cr.color_ramp.elements[0].color=(0.90,0.25,0.00,1)   # #FF6600 bright orange
    cr.color_ramp.elements[1].color=(1.00,0.40,0.04,1)
    lk.new(noise.outputs['Fac'],cr.inputs['Fac'])
    img_a=_img(nd,f'{name}_Albedo',(-400,-200)); mix_c=_mix_pi(nd,lk,cr.outputs['Color'],img_a,(200,50)); lk.new(mix_c.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=0.30; bsdf.inputs['Metallic'].default_value=0.05
    bsdf.inputs['Specular IOR Level'].default_value=0.55
    return mat

def mat_white_stripe(name):
    mat,nd,lk,bsdf=_base(name)
    bsdf.inputs['Base Color'].default_value=(1.0,1.0,1.0,1)
    bsdf.inputs['Roughness'].default_value=0.25
    bsdf.inputs['Specular IOR Level'].default_value=0.60
    return mat

def mat_eye(name):
    mat,nd,lk,bsdf=_base(name)
    bsdf.inputs['Base Color'].default_value=(0.018,0.018,0.018,1)
    bsdf.inputs['Roughness'].default_value=0.02
    bsdf.inputs['Specular IOR Level'].default_value=1.2
    return mat

def mat_fin_orange(name):
    mat,nd,lk,bsdf=_base(name)
    bsdf.inputs['Base Color'].default_value=(0.92,0.30,0.02,1)
    bsdf.inputs['Roughness'].default_value=0.35
    bsdf.inputs['Transmission Weight'].default_value=0.22
    mat.blend_method='BLEND'; return mat

def build_materials():
    return {
        'orange'  : mat_orange('Mat_SmallFish_Orange'),
        'white'   : mat_white_stripe('Mat_SmallFish_White_Stripe'),
        'eye'     : mat_eye('Mat_SmallFish_Eye'),
        'fin_org' : mat_fin_orange('Mat_SmallFish_Fin'),
    }

# ── Body ──────────────────────────────────────────────────────────

def build_body(mats, col):
    """Optimized laterally compressed oval body (low poly)."""
    objs = []
    bm = bmesh.new()
    # Angelfish profile: tall compressed body
    # Keep low poly: 16 segs × 12 rings
    segs = 16; rings = 12
    L = 0.15; W = 0.04; H = 0.125   # half-extents

    verts_grid = []
    for ri in range(rings+1):
        t = ri/rings; y = -L + t*2*L
        # Width: narrow at head and tail
        if t < 0.20:   w = W*(t/0.20)*0.6
        elif t < 0.55: w = W*(0.6 + (t-0.20)/0.35*0.4)
        elif t < 0.72: w = W*1.0
        elif t < 0.90: w = W*(1.0-(t-0.72)/0.18*0.70)
        else:          w = W*(0.30-(t-0.90)/0.10*0.28)
        # Height: tall compressed body
        if t < 0.15:   h = H*(t/0.15)*0.5
        elif t < 0.42: h = H*(0.5+(t-0.15)/0.27*0.5)
        elif t < 0.65: h = H*1.0
        elif t < 0.88: h = H*(1.0-(t-0.65)/0.23*0.30)
        else:          h = H*(0.70-(t-0.88)/0.12*0.65)
        ring = []
        for si in range(segs):
            a = 2*math.pi*si/segs
            x = w*math.cos(a); z = h*math.sin(a)
            if z < 0: z *= 0.72
            ring.append(bm.verts.new(Vector((x,y,z))))
        verts_grid.append(ring)
    for ri in range(rings):
        for si in range(segs):
            v0=verts_grid[ri][si]; v1=verts_grid[ri][(si+1)%segs]
            v2=verts_grid[ri+1][(si+1)%segs]; v3=verts_grid[ri+1][si]
            try: bm.faces.new([v0,v1,v2,v3])
            except: pass
    tc=bm.verts.new(Vector((0,-L,0))); hc=bm.verts.new(Vector((0,L,0)))
    for si in range(segs):
        try:
            bm.faces.new([verts_grid[0][(si+1)%segs],verts_grid[0][si],tc])
            bm.faces.new([verts_grid[-1][si],verts_grid[-1][(si+1)%segs],hc])
        except: pass
    mesh = bpy.data.meshes.new('SmallFish_Body_Mesh'); bm.to_mesh(mesh); bm.free()
    body = bpy.data.objects.new('SmallFish_Body', mesh)
    bpy.context.scene.collection.objects.link(body)
    assign_mat(body, mats['orange'])
    body.data.materials.append(mats['white'])
    add_sub(body, 1); smart_uv(body); link(col, body); objs.append(body)

    # White stripe band (mid-body cylinder)
    stripe = prim('cyl','SmallFish_Stripe',loc=(0,0.005,0),size=0.043,depth=0.062,verts=14)
    stripe.scale=(0.90,1.0,0.90); bpy.ops.object.transform_apply(scale=True)
    assign_mat(stripe, mats['white']); link(col, stripe); objs.append(stripe)
    return objs

def build_dorsal_fin(mats, col):
    """Fan-shaped top fin (low poly: 6 faces)."""
    objs = []
    bm = bmesh.new()
    pts = [Vector((0,-0.06,0.12)),Vector((0,0.00,0.18)),Vector((0,0.06,0.15)),
           Vector((0,0.10,0.10)),Vector((0,0.06,0.00)),Vector((0,-0.06,0.00))]
    for pt in pts: bm.verts.new(pt)
    bm.verts.ensure_lookup_table()
    ctr = bm.verts.new(Vector((0,0.02,0.04)))
    for i in range(len(pts)):
        try: bm.faces.new([bm.verts[i],bm.verts[(i+1)%len(pts)],ctr])
        except: pass
    mesh = bpy.data.meshes.new('SmallFish_DorsalFin_Mesh'); bm.to_mesh(mesh); bm.free()
    fin = bpy.data.objects.new('SmallFish_DorsalFin',mesh)
    fin.location=(0,0.02,0.12)
    bpy.context.scene.collection.objects.link(fin)
    assign_mat(fin,mats['fin_org']); add_solidify(fin,0.006); smart_uv(fin); link(col,fin); objs.append(fin)
    return objs

def build_tail_fin(mats, col):
    """Forked symmetrical tail (low poly)."""
    objs = []
    bm = bmesh.new()
    ty = -0.15
    pts = [Vector((0,ty,0)),Vector((0.06,ty-0.06,0.06)),Vector((0.08,ty-0.14,0.12)),
           Vector((0.04,ty-0.16,0.14)),Vector((0,ty-0.10,0.08)),
           Vector((0,ty-0.10,-0.08)),Vector((0.04,ty-0.16,-0.14)),
           Vector((0.08,ty-0.14,-0.12)),Vector((0.06,ty-0.06,-0.06))]
    for pt in pts: bm.verts.new(pt)
    bm.verts.ensure_lookup_table()
    bmesh.ops.convex_hull(bm,input=bm.verts)
    mesh = bpy.data.meshes.new('SmallFish_TailFin_Mesh'); bm.to_mesh(mesh); bm.free()
    tail = bpy.data.objects.new('SmallFish_TailFin',mesh)
    bpy.context.scene.collection.objects.link(tail)
    assign_mat(tail,mats['fin_org']); add_solidify(tail,0.006); smart_uv(tail); link(col,tail); objs.append(tail)
    return objs

def build_pectoral_fins(mats, col):
    """Small oval pectoral fins."""
    objs = []
    for side, sx in [('L',-1),('R',1)]:
        fin = prim('cyl',f'SmallFish_PectoralFin_{side}',loc=(sx*0.042,0.04,-0.02),
                   size=0.030,depth=0.004,verts=10)
        fin.scale=(0.70,2.20,0.55); fin.rotation_euler=(0,math.radians(-12),0)
        bpy.ops.object.transform_apply(scale=True,rotation=True)
        assign_mat(fin,mats['fin_org']); add_solidify(fin,0.005); smart_uv(fin); link(col,fin); objs.append(fin)
    return objs

def build_eyes(mats, col):
    objs = []
    for side, sx in [('L',-1),('R',1)]:
        eye = prim('sphere',f'SmallFish_Eye_{side}',loc=(sx*0.038,0.08,0.02),size=0.012,segs=8,rings=6)
        eye.scale=(0.62,0.40,0.90); bpy.ops.object.transform_apply(scale=True)
        assign_mat(eye,mats['eye']); link(col,eye); objs.append(eye)
    return objs

# ── Particle School Setup ──────────────────────────────────────────

def setup_particle_school(col, fish_root):
    """Create a preview plane emitting 50 SmallFish via particle system."""
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0, 0, 3))
    plane = bpy.context.active_object; plane.name = 'Fish_School_Emitter'
    link(col, plane)
    ps = plane.modifiers.new('FishSchool', 'PARTICLE_SYSTEM')
    settings = plane.particle_systems['FishSchool'].settings
    settings.type = 'HAIR'
    settings.use_advanced_hair = True
    settings.count = 50
    settings.render_type = 'OBJECT'
    settings.instance_object = fish_root
    settings.use_rotation_instance = True
    settings.particle_size = 1.0
    settings.size_random = 0.20
    print("  Particle school emitter created: Fish_School_Emitter (50 fish)")
    print("  Tip: Change count to 200-500 for GPU instanced schools in Unity")

# ─────────────────────────────────────────────────────────────────
#  ASSEMBLE
# ─────────────────────────────────────────────────────────────────

def main():
    clear_scene()
    col  = new_col('IsleTrial_SmallFish')
    mats = build_materials()
    all_objs = []
    all_objs += build_body(mats, col)
    all_objs += build_dorsal_fin(mats, col)
    all_objs += build_tail_fin(mats, col)
    all_objs += build_pectoral_fins(mats, col)
    all_objs += build_eyes(mats, col)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    root = bpy.context.active_object; root.name = 'SmallFish_ROOT'; link(col, root)
    for obj in all_objs:
        if obj.parent is None: obj.parent = root

    setup_particle_school(col, root)

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = root

    # Count triangles (approximate)
    tri_count = 0
    for obj in all_objs:
        if obj.type == 'MESH':
            mesh = obj.data
            for poly in mesh.polygons:
                tri_count += max(0, len(poly.vertices) - 2)

    mc = sum(1 for o in col.objects if o.type=='MESH')
    print("=" * 60)
    print("[IsleTrial] Small Tropical Fish model built successfully.")
    print(f"  Mesh objects : {mc}  (excl. emitter)")
    print(f"  SmallFish polycount: ~{tri_count*2} triangles — suitable for GPU instancing")
    print()
    print("  Stripe: assign white material to mid-band verts in edit mode")
    print("  Unity: GPU Instancing ✓ | LOD not needed at this poly count")
    print("  School: 50 fish preview in viewport (particle system)")
    print("  Next: run 18_SmallFish_Rig.py")
    print("=" * 60)

main()
