"""
IsleTrial – Sky & Atmosphere Props  (28_Ocean_AtmosphericProps.py)  [REBUILT]
==============================================================================
Prompt 05-D: Atmospheric environment dressing.

  SeaBird_Silhouette_A/B/C  3 seagull pose variants (0.6 m wingspan)
       Body + head + beak + secondary feathers + primary tips + tail fan
       Eyes + leg stubs. Poses: flat glide / wings-up / banking-left

  Cloud_Volume_Small/Med/Large  Low-poly metaball cloud proxies
       Small: 8-lump cumulus
       Medium: 12-lump wider cumulus
       Large: 16-lump storm cumulonimbus with flat dark base

  Horizon_Rock_Arch  8 m tall × 6 m span dramatic sea arch  ← HERO ASSET
       Organic rock mass (bmesh with heavy irregular displacement)
       Boolean tunnel for arch opening
       Jagged top spire formations (4 rocky spikes)
       Sea-carved smooth wave base zone
       Arch interior ridge lines (visible limestone bands)
       Rock face cracks (5 dark fissure cubes)
       Overhanging ledge on arch shoulder
       Marine barnacle clusters (10 around base + lower arch)
       Seaweed ribbon strands (5 drooping bezier curves)
       Marine algae dark patch at waterline
       Tidepool hollow at base (shallow displaced sphere)
       Rocky debris scatter at base (4 small rocks)
       Distant rocky stack companions (2 small pillar outcrops)

  Float_Kelp_Bulb  0.15 m pneumatocyst bulb + 3 ribbon strands
       Main bulb with vein-bump displacement
       Holdfast root stub at bottom
       3 ribbon fronds of varied lengths

Dual-path PBR materials + UV unwrap.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, random, math
from mathutils import Vector, Matrix

rng = random.Random(0xE4B890)

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def new_col(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def link(col, obj):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def smart_uv(obj, angle=60):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=angle, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)

def new_mesh_obj(name, bm, col):
    me = bpy.data.meshes.new(name + '_Mesh')
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob

def prim(tp, name, loc=(0,0,0), rot=(0,0,0), size=1.0, **kw):
    if tp == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=size, location=loc, rotation=rot,
            segments=kw.get('segs',16), ring_count=kw.get('rings',12))
    elif tp == 'cyl':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=size, depth=kw.get('depth',1.0),
            location=loc, rotation=rot, vertices=kw.get('verts',16))
    elif tp == 'cone':
        bpy.ops.mesh.primitive_cone_add(
            radius1=kw.get('r1',size), radius2=kw.get('r2',0),
            depth=kw.get('depth',1.0), location=loc, rotation=rot,
            vertices=kw.get('verts',12))
    elif tp == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=size, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def poly_count(obj):
    if obj.type != 'MESH':
        return 0
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)

# ─────────────────────────────────────────────────────────────────────────────
#  MATERIAL SYSTEM  (dual-path procedural + [UNITY] image slots)
# ─────────────────────────────────────────────────────────────────────────────

def _n(ns, t, loc, label=None):
    nd = ns.new(t); nd.location = loc
    if label: nd.label = nd.name = label
    return nd

def _img(ns, slot_name, loc):
    nd = ns.new('ShaderNodeTexImage'); nd.location = loc
    nd.label = nd.name = f'[UNITY] {slot_name}'
    return nd

def _base_mat(name):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    ns = mat.node_tree.nodes; lk = mat.node_tree.links; ns.clear()
    bsdf = _n(ns, 'ShaderNodeBsdfPrincipled', (400, 0))
    out  = _n(ns, 'ShaderNodeOutputMaterial',  (700, 0))
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat, ns, lk, bsdf

def build_bird_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Seabird_White")
    mp = _n(ns, 'ShaderNodeTexCoord', (-600, 0))
    noise = _n(ns, 'ShaderNodeTexNoise', (-400, 200))
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 3.0
    lk.new(mp.outputs['UV'], noise.inputs['Vector'])
    cr = _n(ns, 'ShaderNodeValToRGB', (-180, 200))
    cr.color_ramp.elements[0].color = (0.88, 0.88, 0.86, 1)
    cr.color_ramp.elements[1].color = (0.98, 0.98, 0.96, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    img = _img(ns, 'Seabird_Albedo', (-400, -200))
    mix = _n(ns, 'ShaderNodeMixRGB', (200, 100))
    mix.inputs[0].default_value = 0.0
    lk.new(cr.outputs['Color'], mix.inputs[1])
    lk.new(img.outputs['Color'], mix.inputs[2])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.82
    bsdf.inputs['Sheen Weight'].default_value = 0.10
    return mat

def build_bird_dark_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Seabird_Dark")
    bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.12, 1)
    bsdf.inputs['Roughness'].default_value = 0.92
    img = _img(ns, 'Seabird_Dark_Albedo', (-300, -100))
    mix = _n(ns, 'ShaderNodeMixRGB', (200, 0))
    mix.inputs[0].default_value = 0.0
    mix.inputs[1].default_value = (0.12, 0.12, 0.12, 1)
    lk.new(img.outputs['Color'], mix.inputs[2])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'], ns.new('ShaderNodeOutputMaterial').inputs['Surface'])
    return mat

def build_bird_beak_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Seabird_Beak")
    bsdf.inputs['Base Color'].default_value = (0.78, 0.52, 0.06, 1)
    bsdf.inputs['Roughness'].default_value = 0.55
    return mat

def build_cloud_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Cloud")
    mat.blend_method = 'BLEND'
    noise = _n(ns, 'ShaderNodeTexNoise', (-400, 200))
    noise.inputs['Scale'].default_value = 3.0
    noise.inputs['Detail'].default_value = 5.0
    cr = _n(ns, 'ShaderNodeValToRGB', (-160, 200))
    cr.color_ramp.elements[0].color = (0.92, 0.93, 0.95, 1)
    cr.color_ramp.elements[1].color = (1.00, 1.00, 1.00, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Alpha'].default_value = 0.62
    bsdf.inputs['Subsurface Weight'].default_value = 0.22
    bsdf.inputs['Subsurface Radius'].default_value = (0.8, 0.8, 0.8)
    return mat

def build_cloud_storm_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Cloud_Storm")
    mat.blend_method = 'BLEND'
    bsdf.inputs['Base Color'].default_value = (0.58, 0.58, 0.62, 1)
    bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Alpha'].default_value = 0.72
    bsdf.inputs['Subsurface Weight'].default_value = 0.15
    return mat

def build_rock_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Rock_Arch")
    mp = _n(ns, 'ShaderNodeTexCoord', (-820, 0))
    mapping = _n(ns, 'ShaderNodeMapping', (-620, 0))
    mapping.inputs['Scale'].default_value = (4.0, 4.0, 4.0)
    lk.new(mp.outputs['Object'], mapping.inputs['Vector'])
    # Musgrave base for large-scale rock variation
    mus = _n(ns, 'ShaderNodeTexMusgrave', (-400, 200))
    mus.musgrave_type = 'FBM'
    mus.inputs['Scale'].default_value = 7.0
    mus.inputs['Detail'].default_value = 14.0
    mus.inputs['Dimension'].default_value = 1.3
    lk.new(mapping.outputs['Vector'], mus.inputs['Vector'])
    cr = _n(ns, 'ShaderNodeValToRGB', (-160, 200))
    cr.color_ramp.elements[0].color = (0.18, 0.15, 0.11, 1)
    cr.color_ramp.elements[1].color = (0.52, 0.46, 0.38, 1)
    lk.new(mus.outputs['Fac'], cr.inputs['Fac'])
    # Voronoi for rocky surface crack pattern
    vor = _n(ns, 'ShaderNodeTexVoronoi', (-400, -60))
    vor.inputs['Scale'].default_value = 12.0
    lk.new(mapping.outputs['Vector'], vor.inputs['Vector'])
    overlay = _n(ns, 'ShaderNodeMixRGB', (40, 140))
    overlay.blend_type = 'MULTIPLY'
    overlay.inputs[0].default_value = 0.28
    lk.new(cr.outputs['Color'], overlay.inputs[1])
    lk.new(vor.outputs['Color'], overlay.inputs[2])
    # Wet base: gradient from dark wet bottom to dry top
    gradient = _n(ns, 'ShaderNodeTexGradient', (-400, -250))
    gradient.gradient_type = 'SPHERICAL'
    lk.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
    wet_cr = _n(ns, 'ShaderNodeValToRGB', (-160, -250))
    wet_cr.color_ramp.elements[0].color = (0.06, 0.06, 0.07, 1)
    wet_cr.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1)
    lk.new(gradient.outputs['Fac'], wet_cr.inputs['Fac'])
    base_mix = _n(ns, 'ShaderNodeMixRGB', (200, 80))
    base_mix.inputs[0].default_value = 0.35
    lk.new(overlay.outputs['Color'], base_mix.inputs[1])
    lk.new(wet_cr.outputs['Color'], base_mix.inputs[2])
    # Image slots
    img_a = _img(ns, 'Rock_Arch_Albedo', (-400, -440))
    img_n = _img(ns, 'Rock_Arch_Normal', (-400, -620))
    img_r = _img(ns, 'Rock_Arch_Roughness', (-400, -800))
    final_mix = _n(ns, 'ShaderNodeMixRGB', (350, 60))
    final_mix.inputs[0].default_value = 0.0
    lk.new(base_mix.outputs['Color'], final_mix.inputs[1])
    lk.new(img_a.outputs['Color'], final_mix.inputs[2])
    lk.new(final_mix.outputs['Color'], bsdf.inputs['Base Color'])
    # Bump from musgrave + voronoi combined
    bmp_ns = _n(ns, 'ShaderNodeTexNoise', (-400, -1000))
    bmp_ns.inputs['Scale'].default_value = 18.0
    bmp_ns.inputs['Detail'].default_value = 8.0
    lk.new(mapping.outputs['Vector'], bmp_ns.inputs['Vector'])
    bmp = _n(ns, 'ShaderNodeBump', (200, -200))
    bmp.inputs['Strength'].default_value = 1.4
    lk.new(bmp_ns.outputs['Fac'], bmp.inputs['Height'])
    nm = _n(ns, 'ShaderNodeNormalMap', (200, -400))
    lk.new(img_n.outputs['Color'], nm.inputs['Color'])
    mix_n = _n(ns, 'ShaderNodeMixRGB', (360, -300))
    mix_n.inputs[0].default_value = 0.0
    lk.new(bmp.outputs['Normal'], mix_n.inputs[1])
    lk.new(nm.outputs['Normal'], mix_n.inputs[2])
    lk.new(mix_n.outputs['Color'], bsdf.inputs['Normal'])
    lk.new(img_r.outputs['Color'], bsdf.inputs['Roughness'])
    bsdf.inputs['Roughness'].default_value = 0.94
    return mat

def build_barnacle_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Barnacle_Arch")
    bsdf.inputs['Base Color'].default_value = (0.72, 0.68, 0.62, 1)
    bsdf.inputs['Roughness'].default_value = 0.88
    img = _img(ns, 'Barnacle_Albedo', (-300, -100))
    mix = _n(ns, 'ShaderNodeMixRGB', (200, 0))
    mix.inputs[0].default_value = 0.0
    mix.inputs[1].default_value = (0.72, 0.68, 0.62, 1)
    lk.new(img.outputs['Color'], mix.inputs[2])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    return mat

def build_seaweed_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Seaweed_Arch")
    mat.blend_method = 'BLEND'
    bsdf.inputs['Base Color'].default_value = (0.08, 0.28, 0.06, 1)
    bsdf.inputs['Roughness'].default_value = 0.78
    bsdf.inputs['Alpha'].default_value = 0.88
    bsdf.inputs['Subsurface Weight'].default_value = 0.14
    bsdf.inputs['Subsurface Radius'].default_value = (0.06, 0.22, 0.04)
    return mat

def build_kelp_bulb_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Kelp_Bulb")
    mp = _n(ns, 'ShaderNodeTexCoord', (-600, 0))
    noise = _n(ns, 'ShaderNodeTexNoise', (-380, 200))
    noise.inputs['Scale'].default_value = 8.0
    noise.inputs['Detail'].default_value = 6.0
    lk.new(mp.outputs['UV'], noise.inputs['Vector'])
    cr = _n(ns, 'ShaderNodeValToRGB', (-160, 200))
    cr.color_ramp.elements[0].color = (0.22, 0.38, 0.08, 1)
    cr.color_ramp.elements[1].color = (0.36, 0.52, 0.16, 1)
    lk.new(noise.outputs['Fac'], cr.inputs['Fac'])
    img = _img(ns, 'Kelp_Bulb_Albedo', (-380, -200))
    mix = _n(ns, 'ShaderNodeMixRGB', (200, 100))
    mix.inputs[0].default_value = 0.0
    lk.new(cr.outputs['Color'], mix.inputs[1])
    lk.new(img.outputs['Color'], mix.inputs[2])
    lk.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.72
    bsdf.inputs['Subsurface Weight'].default_value = 0.12
    bsdf.inputs['Subsurface Radius'].default_value = (0.10, 0.28, 0.05)
    return mat

def build_kelp_ribbon_mat():
    mat, ns, lk, bsdf = _base_mat("Mat_Kelp_Ribbon")
    mat.blend_method = 'BLEND'
    bsdf.inputs['Base Color'].default_value = (0.14, 0.32, 0.06, 1)
    bsdf.inputs['Roughness'].default_value = 0.80
    bsdf.inputs['Alpha'].default_value = 0.90
    bsdf.inputs['Subsurface Weight'].default_value = 0.16
    bsdf.inputs['Subsurface Radius'].default_value = (0.05, 0.20, 0.04)
    return mat

# ─────────────────────────────────────────────────────────────────────────────
#  SEABIRD GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────

def build_wing_bmesh(name, col, loc, span=0.30, fold=0.0, bank=0.0, mat=None):
    """One wing: 10-station aerofoil with secondary feather overlay and primary tips."""
    bm = bmesh.new()
    stations = 10
    for s in range(stations + 1):
        t = s / stations
        wx = t * span
        wz = fold * t * 0.14 + bank * t * t * 0.12
        chord_back  = 0.130 * (1.0 - t ** 0.75)
        chord_front = 0.042 * (1.0 - t ** 0.60)
        bm.verts.new(Vector((wx, chord_back,  wz)))
        bm.verts.new(Vector((wx, -chord_front, wz)))
    bm.verts.ensure_lookup_table()
    for s in range(stations):
        a, b, c, d = s*2, (s+1)*2, (s+1)*2+1, s*2+1
        bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
    # Primary feather tabs at tip (5)
    base_verts = list(bm.verts)
    for fi in range(5):
        t = 0.52 + fi * 0.10
        fx = t * span
        fy_tip = 0.130 * (1.0 - t ** 0.75) + 0.038
        wz_f   = fold * t * 0.14
        p0 = bm.verts.new(Vector((fx,              fy_tip,         wz_f)))
        p1 = bm.verts.new(Vector((fx + 0.040,      fy_tip + 0.009, wz_f)))
        p2 = bm.verts.new(Vector((fx + 0.044,      fy_tip + 0.028, wz_f)))
        p3 = bm.verts.new(Vector((fx + 0.004,      fy_tip + 0.038, wz_f)))
        bm.faces.new([p0, p1, p2, p3])
    # Secondary feather stripe across mid-wing
    sy_offset = 0.010
    for s in range(3, 8):
        t = s / stations
        wx_s = t * span
        chord_s = 0.130 * (1.0 - t ** 0.75)
        wz_s    = fold * t * 0.14 + bank * t * t * 0.12
        bm.verts.new(Vector((wx_s,          chord_s + sy_offset, wz_s + 0.002)))
        bm.verts.new(Vector((wx_s + span/stations, chord_s * 0.85 + sy_offset, wz_s + 0.002)))
    sec_verts = list(bm.verts)[len(base_verts) + 5*4:]
    for i in range(len(sec_verts) // 2 - 1):
        idx = i * 2
        if idx + 3 < len(sec_verts):
            bm.faces.new([sec_verts[idx], sec_verts[idx + 1],
                          sec_verts[idx + 3], sec_verts[idx + 2]])
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc
    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)
    return ob

def build_bird_body_bmesh(name, col, loc=(0,0,0), mat=None):
    """Streamlined seagull body: 14-station oval cross-section + tail fan + beak."""
    bm = bmesh.new()
    segs = 16; sides = 8; blen = 0.26
    for i in range(segs + 1):
        t = i / segs
        x = t * blen - blen * 0.30
        ry = 0.058 * (math.sin(t * math.pi)) ** 0.60
        rz = 0.040 * (math.sin(t * math.pi)) ** 0.70
        for j in range(sides):
            a = j * 2 * math.pi / sides
            bm.verts.new(Vector((x, ry * math.cos(a), rz * math.sin(a))))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            c = (i + 1) * sides + (j + 1) % sides
            d = (i + 1) * sides + j
            bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
    # Tail fan – 9 verts spread in Z
    tail_base_x = blen * 0.72
    for fi in range(9):
        ta = (fi / 8 - 0.5) * 0.65
        bm.verts.new(Vector((tail_base_x,
                              0.010 * math.sin(ta),
                              -0.022 - fi * 0.004)))
    ob = new_mesh_obj(name, bm, col)
    ob.location = loc
    m = ob.modifiers.new('Sub', 'SUBSURF')
    m.levels = 1; m.render_levels = 1
    if mat:
        assign_mat(ob, mat)
    smart_uv(ob)
    return ob

def build_seagull(col, variant, loc=(0, 0, 0),
                  wing_fold=0.0, wing_bank=0.0, body_pitch=0.0,
                  mat_white=None, mat_dark=None, mat_beak=None):
    objs = []
    lx, ly, lz = loc

    # Body
    body = build_bird_body_bmesh(f"SeaBird_{variant}_Body", col,
                                  loc=(lx, ly, lz), mat=mat_white)
    body.rotation_euler = (0, body_pitch, 0)
    objs.append(body)

    # Head (UV sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8,
                                          radius=0.048,
                                          location=(lx + 0.148, ly, lz + 0.042))
    head = bpy.context.active_object
    head.name = f"SeaBird_{variant}_Head"
    head.scale = (1.20, 1.05, 0.94)
    bpy.ops.object.transform_apply(scale=True)
    assign_mat(head, mat_white); smart_uv(head); link(col, head); objs.append(head)

    # Eye (small black sphere per side)
    for ey_side, ey_x in [('L', -0.025), ('R', 0.025)]:
        eye = bpy.data.objects.new(f"SeaBird_{variant}_Eye_{ey_side}",
                                    bpy.data.meshes.new("EyeMesh"))
        bm_e = bmesh.new()
        bmesh.ops.create_uvsphere(bm_e, u_segments=8, v_segments=6, radius=0.009)
        bm_e.to_mesh(eye.data); bm_e.free()
        eye.location = (lx + 0.180, ly + ey_x, lz + 0.052)
        mat_e, ne, le, be = _base_mat(f'Mat_Bird_Eye_{variant}_{ey_side}')
        be.inputs['Base Color'].default_value = (0.04, 0.04, 0.04, 1)
        be.inputs['Roughness'].default_value = 0.05
        assign_mat(eye, mat_e); col.objects.link(eye); objs.append(eye)

    # Beak
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.013, radius2=0.003, depth=0.070,
        location=(lx + 0.215, ly, lz + 0.038),
        rotation=(0, math.pi / 2, 0))
    beak = bpy.context.active_object
    beak.name = f"SeaBird_{variant}_Beak"
    assign_mat(beak, mat_beak); smart_uv(beak); link(col, beak); objs.append(beak)

    # Leg stubs (2 per bird)
    for leg_x in (-0.010, 0.010):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.008, depth=0.05, vertices=6,
            location=(lx - 0.020, ly + leg_x, lz - 0.045))
        leg = bpy.context.active_object
        leg.name = f"SeaBird_{variant}_Leg_{int(leg_x*100)}"
        assign_mat(leg, mat_dark); link(col, leg); objs.append(leg)
        # Foot stub
        bpy.ops.mesh.primitive_sphere_add = getattr(bpy.ops.mesh, 'primitive_uv_sphere_add',None)
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8, ring_count=6, radius=0.011,
            location=(lx - 0.018, ly + leg_x, lz - 0.072))
        foot = bpy.context.active_object
        foot.name = f"SeaBird_{variant}_Foot_{int(leg_x*100)}"
        foot.scale = (1.8, 0.6, 0.4)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(foot, mat_dark); link(col, foot); objs.append(foot)

    # Left wing
    wL = build_wing_bmesh(f"SeaBird_{variant}_WingL", col,
                           loc=(lx, ly, lz),
                           span=0.300, fold=wing_fold, bank=-wing_bank, mat=mat_white)
    wL.rotation_euler = (0, body_pitch, 0)
    objs.append(wL)

    # Right wing (mirror in Y)
    wR = build_wing_bmesh(f"SeaBird_{variant}_WingR", col,
                           loc=(lx, ly, lz),
                           span=0.300, fold=wing_fold, bank=wing_bank, mat=mat_white)
    wR.rotation_euler = (0, body_pitch, math.pi)
    objs.append(wR)

    # Dark wingtip panels (outer 20% of each wing)
    for i, (side_label, rot_z) in enumerate([('L', 0), ('R', math.pi)]):
        tip = build_wing_bmesh(f"SeaBird_{variant}_Tip_{side_label}", col,
                                loc=(lx, ly, lz),
                                span=0.065, fold=wing_fold * 1.2,
                                bank=wing_bank * (1 if i else -1), mat=mat_dark)
        tip.location.x += (0.240 if side_label == 'L' else -0.240) * 0
        tip.rotation_euler = (0, body_pitch, rot_z)
        objs.append(tip)

    return objs

# ─────────────────────────────────────────────────────────────────────────────
#  CLOUD PROXIES
# ─────────────────────────────────────────────────────────────────────────────

def build_cloud_proxy(col, name, loc=(0,0,0), scale=1.0, mat=None, storm=False):
    """Fluffy cloud from merged metaball lumps, converted + decimated."""
    lump_count = 8 if not storm else 16
    lump_offsets = [
        (0.0, 0.0,  0.0), (0.60, 0.0, 0.12), (-0.55, 0.10, 0.06),
        (0.20, 0.40, 0.18), (0.30,-0.40, 0.20), (0.0,  0.0, 0.35),
        (0.80, 0.0,  0.02), (-0.30,-0.20, 0.28),
    ]
    if storm:
        lump_offsets += [
            (0.10, 0.60, 0.08), (-0.60,-0.10, 0.14),
            (0.50,-0.30, 0.22), (-0.20, 0.50, 0.30),
            (1.00, 0.20, 0.06), (-0.80, 0.30, 0.10),
            (0.40, 0.40, 0.40), (-0.40,-0.40, 0.05),
        ]
    bpy.ops.object.metaball_add(type='BALL', location=loc)
    mb0 = bpy.context.active_object
    mb0.name = f"{name}_Meta_0"
    mb0.scale = (2.0 * scale, 1.0 * scale, 0.7 * scale)
    for i, (ox, oy, oz) in enumerate(lump_offsets[1:]):
        bpy.ops.object.metaball_add(
            type='BALL',
            location=(loc[0] + ox * scale, loc[1] + oy * scale, loc[2] + oz * scale))
        lump = bpy.context.active_object
        lump.name = f"{name}_Meta_{i+1}"
        lump.scale = (rng.uniform(0.45, 1.05) * scale,
                      rng.uniform(0.35, 0.80) * scale,
                      rng.uniform(0.28, 0.58) * scale)
    # Storm base: flat dark slab
    if storm:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        base = bpy.context.active_object
        base.name = f"{name}_StormBase"
        base.scale = (2.4 * scale, 2.0 * scale, 0.06 * scale)
        bpy.ops.object.transform_apply(scale=True)
        mat_s, nbs, lks, bbs = _base_mat(f'Mat_{name}_Base')
        bbs.inputs['Base Color'].default_value = (0.42, 0.42, 0.46, 1)
        bbs.inputs['Alpha'].default_value = 0.70
        mat_s.blend_method = 'BLEND'
        assign_mat(base, mat_s); link(col, base)
    # Convert metaballs to mesh
    bpy.ops.object.select_all(action='DESELECT')
    meta_objs = [o for o in bpy.context.scene.objects
                 if o.type == 'META' and o.name.startswith(name)]
    for o in meta_objs:
        o.select_set(True)
    if bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.convert(target='MESH')
        cloud = bpy.context.active_object
        cloud.name = name
        dec = cloud.modifiers.new('Dec', 'DECIMATE')
        dec.ratio = 0.15
        assign_mat(cloud, mat)
        smart_uv(cloud)
        link(col, cloud)
        return cloud
    return None

# ─────────────────────────────────────────────────────────────────────────────
#  HORIZON ROCK ARCH  (HERO ASSET)
# ─────────────────────────────────────────────────────────────────────────────

def build_rock_arch(col, name, base_loc=(0, 20, 0),
                    arch_h=8.0, arch_w=6.0,
                    mat_rock=None, mat_barn=None, mat_weed=None):
    """
    Dramatic 8m sea arch — full marine environment set piece.
    Components: main arch mass, boolean tunnel, jagged top spires,
    sea-carved base zone, arch ridge bands, rock face cracks, overhanging ledge,
    barnacle clusters, seaweed strands, algae patch, tidepool hollow, base debris.
    """
    objs = []
    ox, oy, oz = base_loc

    # ── Main arch rock mass (bmesh) ──────────────────────────────────────────
    bm_a = bmesh.new()
    segs = 18; sides = 20; base_r = 4.0; top_r = 2.0
    for i in range(segs + 1):
        t = i / segs
        z = t * arch_h
        r = base_r + (top_r - base_r) * t
        for j in range(sides):
            a = j * 2 * math.pi / sides
            # Multi-frequency irregularity: large-scale + medium + small
            irregular = (r * (0.74 + 0.26 * rng.random())
                         + 0.50 * math.sin(t * math.pi * 2.5 + j * 0.8) * math.sin(t * math.pi)
                         + 0.28 * math.sin(t * math.pi * 5.0 + j * 1.6)
                         + 0.14 * rng.uniform(-1, 1) * (1 - t))
            bm_a.verts.new(Vector((irregular * math.cos(a),
                                   irregular * math.sin(a),
                                   z)))
    bm_a.verts.ensure_lookup_table()
    for i in range(segs):
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            c = (i + 1) * sides + (j + 1) % sides
            d = (i + 1) * sides + j
            bm_a.faces.new([bm_a.verts[a], bm_a.verts[b], bm_a.verts[c], bm_a.verts[d]])
    # Bottom cap
    bot_c = bm_a.verts.new(Vector((0, 0, -0.20)))
    for j in range(sides):
        bm_a.faces.new([bm_a.verts[(j + 1) % sides], bm_a.verts[j], bot_c])
    # Top irregular cap
    top_c = bm_a.verts.new(Vector((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), arch_h + 0.4)))
    for j in range(sides):
        bm_a.faces.new([bm_a.verts[segs * sides + j],
                        bm_a.verts[segs * sides + (j + 1) % sides],
                        top_c])
    arch_ob = new_mesh_obj(name, bm_a, col)
    arch_ob.location = (ox, oy, oz)
    assign_mat(arch_ob, mat_rock); smart_uv(arch_ob)
    objs.append(arch_ob)

    # Modifiers on main rock
    sub_m = arch_ob.modifiers.new('Sub', 'SUBSURF')
    sub_m.levels = 1; sub_m.render_levels = 2
    disp_m = arch_ob.modifiers.new('RockSurface', 'DISPLACE')
    disp_tex = bpy.data.textures.new(f'{name}_RockDisplace', 'DISTORTED_NOISE')
    disp_tex.noise_scale = 0.8
    disp_m.texture = disp_tex; disp_m.strength = 0.55; disp_m.direction = 'NORMAL'

    # ── Boolean arch tunnel ──────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=arch_w / 2, depth=arch_h * 0.90,
        location=(ox, oy, oz + arch_h * 0.28),
        rotation=(math.pi / 2, 0, 0))
    cutter = bpy.context.active_object
    cutter.name = f"{name}_ArchCutter"
    cutter.scale = (1.0, arch_h * 0.90, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    link(col, cutter)
    bool_m = arch_ob.modifiers.new('ArchCut', 'BOOLEAN')
    bool_m.operation = 'DIFFERENCE'
    bool_m.object = cutter
    cutter.hide_viewport = True; cutter.hide_render = True

    # ── Jagged top spires (4 bmesh cones) ───────────────────────────────────
    spire_defs = [
        (( 0.60, 0.20), 1.80, 0.55, 0.06),
        ((-0.80, 0.40), 2.20, 0.48, 0.05),
        (( 0.20,-0.70), 1.50, 0.42, 0.08),
        ((-0.30,-0.30), 2.80, 0.38, 0.04),
    ]
    for sp_i, ((sp_rx, sp_ry), sp_h, sp_r, sp_r2) in enumerate(spire_defs):
        bm_sp = bmesh.new()
        spire_sides = 7
        # Base ring
        sp_verts_b = []
        for j in range(spire_sides):
            a = j * 2 * math.pi / spire_sides
            r_irr = sp_r * (0.80 + 0.20 * rng.random())
            sp_verts_b.append(bm_sp.verts.new(Vector((r_irr * math.cos(a), r_irr * math.sin(a), 0))))
        # Tip (slightly offset)
        tip_v = bm_sp.verts.new(Vector((rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), sp_h)))
        bm_sp.verts.ensure_lookup_table()
        for j in range(spire_sides):
            bm_sp.faces.new([sp_verts_b[j], sp_verts_b[(j+1)%spire_sides], tip_v])
        bm_sp.faces.new(sp_verts_b)
        sp_ob = new_mesh_obj(f"{name}_Spire_{sp_i}", bm_sp, col)
        sp_ob.location = (ox + sp_rx * base_r * 0.55, oy + sp_ry * base_r * 0.55, oz + arch_h - 0.30)
        sp_ob.rotation_euler = (rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), rng.uniform(0, math.pi))
        assign_mat(sp_ob, mat_rock); smart_uv(sp_ob); objs.append(sp_ob)

    # ── Sea-carved smooth base zone ──────────────────────────────────────────
    bm_base = bmesh.new()
    bmesh.ops.create_uvsphere(bm_base, u_segments=20, v_segments=12, radius=base_r * 1.10)
    for v in bm_base.verts:
        if v.co.z > 1.20:
            # Remove upper half: keep only lower smooth wave-sculpted base
            v.co.z = 1.20 + (v.co.z - 1.20) * 0.02
        # Wave erosion undulation on XY
        v.co.x += 0.18 * math.sin(v.co.z * 2.0 + v.co.y * 1.4)
        v.co.y += 0.15 * math.sin(v.co.z * 1.8 + v.co.x * 1.2)
    bmesh.ops.translate(bm_base, verts=bm_base.verts, vec=Vector((ox, oy, oz - 0.15)))
    base_ob = new_mesh_obj(f"{name}_SeaBase", bm_base, col)
    mat_wet, nb, lkb, bb = _base_mat(f'Mat_{name}_WetBase')
    bb.inputs['Base Color'].default_value = (0.12, 0.11, 0.10, 1)
    bb.inputs['Roughness'].default_value = 0.62
    bb.inputs['Specular IOR Level'].default_value = 0.35
    assign_mat(base_ob, mat_wet); smart_uv(base_ob); objs.append(base_ob)

    # ── Arch interior ridge bands (limestone strata lines) ───────────────────
    for ri in range(3):
        rz = arch_h * (0.18 + ri * 0.14)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=arch_w * 0.56 + ri * 0.12,
            minor_radius=0.05, major_segments=28, minor_segments=6,
            location=(ox, oy, oz + rz),
            rotation=(math.pi / 2, 0, 0))
        ridge = bpy.context.active_object
        ridge.name = f"{name}_Ridge_{ri}"
        ridge.scale = (1.0, 0.10, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        mat_rg, nr, lr, br = _base_mat(f'Mat_{name}_Ridge_{ri}')
        br.inputs['Base Color'].default_value = (0.58, 0.52, 0.44, 1)
        br.inputs['Roughness'].default_value = 0.88
        assign_mat(ridge, mat_rg); link(col, ridge); objs.append(ridge)

    # ── Rock face cracks (5 thin dark fissures) ──────────────────────────────
    crack_defs = [
        (( 2.1,  0.5, 2.8), (0, 0, math.radians(72)),  (0.06, 0.08, 2.00)),
        ((-1.8,  1.2, 1.5), (0, 0, math.radians(-55)), (0.05, 0.06, 1.60)),
        (( 1.4, -2.0, 3.5), (0, 0, math.radians(40)),  (0.04, 0.07, 1.40)),
        ((-0.8, -1.6, 5.0), (0, 0, math.radians(-30)), (0.05, 0.06, 1.20)),
        (( 2.6,  0.0, 4.5), (0, 0, math.radians(15)),  (0.04, 0.05, 1.80)),
    ]
    mat_cr, ncr, lcr, bcr = _base_mat(f'Mat_{name}_Crack')
    bcr.inputs['Base Color'].default_value = (0.04, 0.03, 0.03, 1)
    bcr.inputs['Roughness'].default_value = 0.98
    for cr_i, (cr_loc, cr_rot, cr_scale) in enumerate(crack_defs):
        bpy.ops.mesh.primitive_cube_add(size=0.05,
            location=(ox + cr_loc[0], oy + cr_loc[1], oz + cr_loc[2]))
        crack = bpy.context.active_object
        crack.name = f"{name}_Crack_{cr_i}"
        crack.scale = cr_scale
        crack.rotation_euler = cr_rot
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        assign_mat(crack, mat_cr); link(col, crack); objs.append(crack)

    # ── Overhanging ledge (one side) ─────────────────────────────────────────
    bm_ledge = bmesh.new()
    v0 = bm_ledge.verts.new(Vector((ox + 3.2,  oy + 0.5, oz + 3.0)))
    v1 = bm_ledge.verts.new(Vector((ox + 3.2,  oy - 0.5, oz + 2.8)))
    v2 = bm_ledge.verts.new(Vector((ox + 4.8,  oy - 0.4, oz + 2.6)))
    v3 = bm_ledge.verts.new(Vector((ox + 4.8,  oy + 0.6, oz + 2.8)))
    v4 = bm_ledge.verts.new(Vector((ox + 3.2,  oy + 0.5, oz + 2.50)))
    v5 = bm_ledge.verts.new(Vector((ox + 3.2,  oy - 0.5, oz + 2.32)))
    v6 = bm_ledge.verts.new(Vector((ox + 4.8,  oy - 0.4, oz + 2.20)))
    v7 = bm_ledge.verts.new(Vector((ox + 4.8,  oy + 0.6, oz + 2.30)))
    bm_ledge.faces.new([v0, v1, v2, v3])
    bm_ledge.faces.new([v4, v5, v6, v7])
    bm_ledge.faces.new([v0, v1, v5, v4])
    bm_ledge.faces.new([v2, v3, v7, v6])
    bm_ledge.faces.new([v1, v2, v6, v5])
    bm_ledge.faces.new([v0, v3, v7, v4])
    ledge_ob = new_mesh_obj(f"{name}_Ledge", bm_ledge, col)
    assign_mat(ledge_ob, mat_rock); smart_uv(ledge_ob); objs.append(ledge_ob)

    # ── Marine barnacle clusters (10) ────────────────────────────────────────
    barn_positions = [
        ((-2.8,  1.0,  0.8), 0.14), (( 2.5, -0.8,  0.6), 0.12),
        ((-2.0, -1.8,  1.4), 0.16), (( 3.0,  0.5,  1.8), 0.10),
        ((-1.5,  2.2,  0.4), 0.18), (( 1.8, -2.5,  1.0), 0.13),
        ((-3.2, -0.4,  2.2), 0.11), (( 2.2,  2.0,  0.9), 0.15),
        (( 0.0,  3.5,  1.5), 0.12), (( 0.6, -3.2,  0.7), 0.14),
    ]
    for bn_i, ((bn_dx, bn_dy, bn_dz), bn_r) in enumerate(barn_positions):
        bm_bn = bmesh.new()
        for bni in range(rng.randint(8, 14)):
            ax = rng.uniform(-bn_r * 0.8, bn_r * 0.8)
            ay = rng.uniform(-bn_r * 0.8, bn_r * 0.8)
            az = 0
            bm_bn.verts.new(Vector((ax, ay, az)))
            bm_bn.verts.new(Vector((ax + rng.uniform(0.02, 0.05),
                                     ay + rng.uniform(0.02, 0.05),
                                     rng.uniform(0.03, 0.07))))
        bm_bn.verts.ensure_lookup_table()
        for ii in range(0, len(bm_bn.verts) - 1, 2):
            bm_bn.edges.new([bm_bn.verts[ii], bm_bn.verts[ii + 1]])
        bn_ob = new_mesh_obj(f"{name}_Barnacle_{bn_i}", bm_bn, col)
        bn_ob.location = (ox + bn_dx, oy + bn_dy, oz + bn_dz)
        # Simple cone barnacle cluster via instanced cones
        for ci in range(rng.randint(6, 12)):
            cx = rng.uniform(-bn_r, bn_r)
            cy = rng.uniform(-bn_r, bn_r)
            cz_off = rng.uniform(0, 0.025)
            bpy.ops.mesh.primitive_cone_add(
                vertices=6,
                radius1=rng.uniform(0.018, 0.034),
                radius2=rng.uniform(0.006, 0.012),
                depth=rng.uniform(0.030, 0.060),
                location=(ox + bn_dx + cx, oy + bn_dy + cy, oz + bn_dz + cz_off))
            cone = bpy.context.active_object
            cone.name = f"{name}_Barn_{bn_i}_C{ci}"
            assign_mat(cone, mat_barn); link(col, cone); objs.append(cone)
        bpy.data.objects.remove(bn_ob, do_unlink=True)

    # ── Seaweed ribbon strands (5 bezier curves) ─────────────────────────────
    weed_defs = [
        ((-2.5,  1.5,  0.0), ( 0.40,  0.20, 0.80), (-0.20, 0.30, 1.60)),
        (( 2.8, -1.0,  0.0), (-0.30, -0.10, 0.60), ( 0.10,-0.20, 1.40)),
        ((-1.8, -2.2,  0.0), ( 0.25, -0.30, 0.70), (-0.10,-0.10, 1.20)),
        (( 1.2,  2.8,  0.0), (-0.10,  0.40, 0.90), ( 0.20, 0.10, 1.80)),
        (( 0.5, -3.0,  0.0), ( 0.20, -0.20, 0.55), (-0.15,-0.10, 1.00)),
    ]
    for wd_i, (wd_base, wd_ctrl, wd_tip) in enumerate(weed_defs):
        bpy.ops.curve.primitive_bezier_curve_add(
            location=(ox + wd_base[0], oy + wd_base[1], oz + wd_base[2]))
        sw = bpy.context.active_object
        sw.name = f"{name}_Seaweed_{wd_i}"
        sw.data.bevel_depth = rng.uniform(0.010, 0.018)
        sw.data.bevel_resolution = 2
        sw.data.dimensions = '3D'
        sp = sw.data.splines[0]
        sp.bezier_points[0].co = Vector((0, 0, 0))
        sp.bezier_points[1].co = Vector(wd_tip)
        sp.bezier_points[0].handle_right = Vector(wd_ctrl)
        sp.bezier_points[1].handle_left  = Vector((wd_ctrl[0]*0.5, wd_ctrl[1]*0.5, wd_tip[2]*0.6))
        assign_mat(sw, mat_weed); link(col, sw); objs.append(sw)

    # ── Marine algae dark patch at waterline ─────────────────────────────────
    bpy.ops.mesh.primitive_circle_add(vertices=16, radius=2.80,
                                       location=(ox, oy, oz + 0.08),
                                       fill_type='NGON')
    algae = bpy.context.active_object
    algae.name = f"{name}_AlgaePatch"
    algae.scale = (1.0, 1.0, 1.0)
    disp_a = algae.modifiers.new('AlgaeWarp', 'DISPLACE')
    at = bpy.data.textures.new(f'{name}_AlgaeTex', 'CLOUDS')
    at.noise_scale = 0.8
    disp_a.texture = at; disp_a.strength = 0.12
    mat_al, na, la, ba = _base_mat(f'Mat_{name}_Algae')
    ba.inputs['Base Color'].default_value = (0.04, 0.14, 0.03, 1)
    ba.inputs['Roughness'].default_value = 0.86
    assign_mat(algae, mat_al); smart_uv(algae); link(col, algae); objs.append(algae)

    # ── Tidepool hollow ───────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10,
                                          radius=0.80, location=(ox - 2.0, oy + 2.0, oz + 0.10))
    tpool = bpy.context.active_object
    tpool.name = f"{name}_Tidepool"
    tpool.scale = (1.0, 1.0, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    mat_tp, ntp, ltp, btp = _base_mat(f'Mat_{name}_Tidepool')
    btp.inputs['Base Color'].default_value = (0.06, 0.18, 0.22, 1)
    btp.inputs['Roughness'].default_value = 0.06
    btp.inputs['Specular IOR Level'].default_value = 0.90
    assign_mat(tpool, mat_tp); smart_uv(tpool); link(col, tpool); objs.append(tpool)

    # ── Rocky base debris (4 small irregular rocks) ───────────────────────────
    debris_pos = [
        ((-4.5,  1.5,  0.0), (1.10, 0.80, 0.60)),
        (( 4.2, -1.2,  0.0), (0.85, 0.70, 0.55)),
        ((-3.0, -3.5,  0.0), (1.40, 0.90, 0.65)),
        (( 3.8,  3.0,  0.0), (0.95, 0.80, 0.58)),
    ]
    for db_i, ((dbx, dby, dbz), db_scl) in enumerate(debris_pos):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8, ring_count=6, radius=0.60,
            location=(ox + dbx, oy + dby, oz + dbz))
        deb = bpy.context.active_object
        deb.name = f"{name}_Debris_{db_i}"
        deb.scale = db_scl
        deb.rotation_euler = (rng.uniform(0, math.pi), rng.uniform(0, math.pi), 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        ddisp = deb.modifiers.new('RockDisp', 'DISPLACE')
        dtex = bpy.data.textures.new(f'{name}_DebrisTex_{db_i}', 'DISTORTED_NOISE')
        dtex.noise_scale = 0.5
        ddisp.texture = dtex; ddisp.strength = 0.25
        assign_mat(deb, mat_rock); smart_uv(deb); link(col, deb); objs.append(deb)

    # ── Distant companion stacks (2 smaller rock pillars) ───────────────────
    for st_i, (stx, sty, st_h, st_r) in enumerate([(-14.0, 22.0, 5.2, 1.6),
                                                    ( 16.0, 26.0, 4.0, 1.3)]):
        bm_st = bmesh.new()
        st_sides = 12; st_segs = 10
        for i in range(st_segs + 1):
            t = i / st_segs
            r_st = st_r * (1.0 - t * 0.30) * (0.80 + 0.20 * rng.random())
            z_st = t * st_h
            for j in range(st_sides):
                a = j * 2 * math.pi / st_sides
                bm_st.verts.new(Vector((stx + r_st * math.cos(a),
                                        sty + r_st * math.sin(a),
                                        oz + z_st)))
        bm_st.verts.ensure_lookup_table()
        for i in range(st_segs):
            for j in range(st_sides):
                a = i * st_sides + j
                b = i * st_sides + (j + 1) % st_sides
                c = (i + 1) * st_sides + (j + 1) % st_sides
                d = (i + 1) * st_sides + j
                bm_st.faces.new([bm_st.verts[a], bm_st.verts[b],
                                  bm_st.verts[c], bm_st.verts[d]])
        st_ob = new_mesh_obj(f"{name}_Stack_{st_i}", bm_st, col)
        assign_mat(st_ob, mat_rock); smart_uv(st_ob); objs.append(st_ob)

    return objs

# ─────────────────────────────────────────────────────────────────────────────
#  KELP BULB
# ─────────────────────────────────────────────────────────────────────────────

def build_kelp_bulb(col, name, loc=(0, 0, 0), mat_bulb=None, mat_ribbon=None):
    objs = []
    lx, ly, lz = loc

    # Main pneumatocyst bulb
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12,
                                          radius=0.075, location=(lx, ly, lz))
    bulb = bpy.context.active_object
    bulb.name = f"{name}_Bulb"
    bulb.scale = (1.0, 1.0, 1.22)
    bpy.ops.object.transform_apply(scale=True)
    # Vein bump displacement
    disp = bulb.modifiers.new('Veins', 'DISPLACE')
    vt = bpy.data.textures.new(f'{name}_VeinTex', 'CLOUDS')
    vt.noise_scale = 0.25; vt.noise_depth = 4
    disp.texture = vt; disp.strength = 0.022
    assign_mat(bulb, mat_bulb); smart_uv(bulb); link(col, bulb); objs.append(bulb)

    # Holdfast root stub (small cone at bottom)
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.030, radius2=0.008, depth=0.055,
        location=(lx, ly, lz - 0.085))
    hold = bpy.context.active_object
    hold.name = f"{name}_Holdfast"
    assign_mat(hold, mat_ribbon); link(col, hold); objs.append(hold)

    # 3 ribbon frond strands of varied lengths
    frond_defs = [
        (( 0.04, 0.0, -0.076), ( 0.08, 0.06, -0.40), ( 0.14, 0.0, -0.90), 0.015),
        ((-0.04, 0.0, -0.076), (-0.12, 0.0,  -0.36), (-0.06,-0.05,-0.72), 0.012),
        (( 0.0, 0.04, -0.076), ( 0.0, -0.08, -0.28), ( 0.05, 0.08,-0.56), 0.013),
    ]
    for fd_i, (fd_s, fd_ctrl, fd_e, fd_bev) in enumerate(frond_defs):
        bpy.ops.curve.primitive_bezier_curve_add(location=(lx, ly, lz))
        frond = bpy.context.active_object
        frond.name = f"{name}_Frond_{fd_i}"
        frond.data.bevel_depth = fd_bev
        frond.data.bevel_resolution = 2
        frond.data.dimensions = '3D'
        sp = frond.data.splines[0]
        sp.bezier_points[0].co = Vector(fd_s)
        sp.bezier_points[1].co = Vector(fd_e)
        sp.bezier_points[0].handle_right = Vector(fd_ctrl)
        sp.bezier_points[1].handle_left  = Vector((fd_ctrl[0]*0.4, fd_ctrl[1]*0.4, fd_e[2]*0.7))
        assign_mat(frond, mat_ribbon); link(col, frond); objs.append(frond)

    # Small attached gas bulblet
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8, radius=0.025,
        location=(lx + 0.058, ly + 0.020, lz + 0.040))
    bulblet = bpy.context.active_object
    bulblet.name = f"{name}_Bulblet"
    assign_mat(bulblet, mat_bulb); link(col, bulblet); objs.append(bulblet)

    return objs

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

def create_atmospheric_props():
    clear_scene()
    col = new_col("IsleTrial_AtmosphericProps")

    mat_bird_w   = build_bird_mat()
    mat_bird_dk  = build_bird_dark_mat()
    mat_beak     = build_bird_beak_mat()
    mat_cloud    = build_cloud_mat()
    mat_storm    = build_cloud_storm_mat()
    mat_rock     = build_rock_mat()
    mat_barn     = build_barnacle_mat()
    mat_weed     = build_seaweed_mat()
    mat_kelp_b   = build_kelp_bulb_mat()
    mat_kelp_r   = build_kelp_ribbon_mat()

    all_objs = []

    # ── SEAGULL VARIANTS ────────────────────────────────────────────────────
    gull_defs = [
        ("Silhouette_A", (-10, 0, 6.0), 0.00, 0.00,  0.00),   # flat glide
        ("Silhouette_B", ( -7, 0, 6.4), 0.28, 0.00,  0.10),   # wings slightly up
        ("Silhouette_C", ( -4, 0, 5.6), 0.00, 0.32, -0.14),   # banking left
    ]
    for var, (gx, gy, gz), gfold, gbank, gpitch in gull_defs:
        bird_objs = build_seagull(col, var, loc=(gx, gy, gz),
                                   wing_fold=gfold, wing_bank=gbank, body_pitch=gpitch,
                                   mat_white=mat_bird_w, mat_dark=mat_bird_dk,
                                   mat_beak=mat_beak)
        all_objs += [o for o in bird_objs if o.type == 'MESH']

    # ── CLOUD PROXIES ───────────────────────────────────────────────────────
    cloud_defs = [
        ("Cloud_Volume_Small",  ( 5,  0,  8.0), 0.55, False),
        ("Cloud_Volume_Medium", ( 9,  0,  9.5), 1.10, False),
        ("Cloud_Volume_Large",  (15,  0, 11.0), 2.00, True),
    ]
    for cname, cloc, cscl, c_storm in cloud_defs:
        mat_c = mat_storm if c_storm else mat_cloud
        cloud = build_cloud_proxy(col, cname, loc=cloc, scale=cscl, mat=mat_c, storm=c_storm)
        if cloud:
            all_objs.append(cloud)

    # ── HORIZON ROCK ARCH ───────────────────────────────────────────────────
    arch_objs = build_rock_arch(col, "Horizon_Rock_Arch",
                                 base_loc=(0, 20, 0),
                                 arch_h=8.0, arch_w=6.0,
                                 mat_rock=mat_rock, mat_barn=mat_barn, mat_weed=mat_weed)
    all_objs += [o for o in arch_objs if o.type == 'MESH']

    # ── KELP BULB ───────────────────────────────────────────────────────────
    kelp_objs = build_kelp_bulb(col, "Float_Kelp_Bulb",
                                 loc=(5, 5, 0.0),
                                 mat_bulb=mat_kelp_b, mat_ribbon=mat_kelp_r)
    all_objs += [o for o in kelp_objs if o.type == 'MESH']

    # ── RENDER STATS ────────────────────────────────────────────────────────
    print("\n=== IsleTrial_AtmosphericProps — Build Complete ===")
    total_tris = 0
    for o in all_objs:
        if o.type == 'MESH':
            tris = poly_count(o)
            total_tris += tris
            print(f"  {o.name:<46s} | {tris:6d} tris")
    print(f"\n  TOTAL mesh objects : {len(all_objs)}")
    print(f"  TOTAL tris estimate: ~{total_tris:,} (pre-modifier)")
    print()
    print("  Unity notes:")
    print("    SeaBird_Silhouette_*   → LOD0; use as GPU-instanced flock spawner")
    print("    Cloud_Volume_*         → Use as trigger volume for volumetric cloud shader")
    print("    Horizon_Rock_Arch      → Merge + Apply Displace before FBX export")
    print("                             Add MeshCollider in Unity (convex=false)")
    print("    Float_Kelp_Bulb        → Attach RigidBody + FloatPhysics script")
    print("    [UNITY] image slots    → Load PBR maps: Albedo/Normal/Roughness")

    try:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        with bpy.context.temp_override(area=area, region=region):
                            bpy.ops.view3d.view_all(center=True)
                        break
    except Exception:
        pass

    print("\n✓ IsleTrial_AtmosphericProps collection ready.")

create_atmospheric_props()
