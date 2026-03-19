"""
IsleTrial – Ocean Surface Reference Mesh  (29_Ocean_SurfaceReference.py)
=========================================================================
Prompt 05-E: Reference meshes for aligning Unity water shader & buoyancy.
  • Ocean_Surface_Reference – 200×200m, 40×40 grid, Ocean modifier, Y=0
  • Ocean_Buoyancy_Plane    – 200×200m, NO subdivision, Y=0 exactly
  • Ocean_Depth_Markers     – 5 empties at 0m, -5m, -10m, -20m, -50m
Materials as specified.  Prints all alignment guidance notes.
Run inside Blender 3.x/4.x Text Editor → Run Script.
"""

import bpy, bmesh, math

# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────
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
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=angle, island_margin=0.01)
    bpy.ops.object.mode_set(mode='OBJECT')

def ns_lk(mat):
    mat.use_nodes = True
    return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, label, x, y):
    n = ns.new('ShaderNodeTexImage')
    n.label = n.name = label; n.location = (x, y)
    return n

# ─────────────────────────────────────────────────────────────────────
# Materials
# ─────────────────────────────────────────────────────────────────────
def build_ocean_preview_mat():
    mat = bpy.data.materials.new("Mat_Ocean_Preview")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    mat.blend_method = 'BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(550,0)
    bsdf.inputs['Base Color'].default_value      = (0.04, 0.23, 0.35, 1)
    bsdf.inputs['Roughness'].default_value       = 0.10
    bsdf.inputs['Metallic'].default_value        = 0.0
    bsdf.inputs['Transmission Weight'].default_value = 0.55
    bsdf.inputs['Alpha'].default_value           = 0.50
    bsdf.inputs['IOR'].default_value             = 1.33
    # subtle foam crest noise
    noise= ns.new('ShaderNodeTexNoise'); noise.location=(-400,150)
    noise.inputs['Scale'].default_value=0.08; noise.inputs['Detail'].default_value=6.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location=(-150,150)
    cr.color_ramp.elements[0].position=0.55; cr.color_ramp.elements[0].color=(0.04,0.23,0.35,1)
    cr.color_ramp.elements[1].position=0.78; cr.color_ramp.elements[1].color=(0.7,0.85,0.95,1)
    img_a= img_slot(ns,"[UNITY] Ocean_Albedo",-450,-200)
    img_n= img_slot(ns,"[UNITY] Ocean_Normal",-450,-400)
    mix  = ns.new('ShaderNodeMixRGB'); mix.location=(280,0)
    mix.inputs['Fac'].default_value=0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_invisible_collider_mat():
    mat = bpy.data.materials.new("Mat_Invisible_Collider")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location=(600,0)
    mat.blend_method = 'BLEND'
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location=(350,0)
    bsdf.inputs['Alpha'].default_value = 0.0
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# ─────────────────────────────────────────────────────────────────────
# Geometry builders
# ─────────────────────────────────────────────────────────────────────
def build_ocean_surface_reference(col, mat):
    """200×200m plane, 40×40 grid, Ocean modifier for wave preview."""
    # Use grid primitive for 40×40 mesh
    bpy.ops.mesh.primitive_grid_add(
        x_subdivisions=40, y_subdivisions=40,
        size=200.0, location=(0, 0, 0))
    ob = bpy.context.active_object
    ob.name = ob.data.name = "Ocean_Surface_Reference"

    # Add Ocean modifier
    ocean_mod = ob.modifiers.new('OceanPreview', 'OCEAN')
    ocean_mod.geometry_mode  = 'DISPLACE'
    ocean_mod.resolution     = 8
    ocean_mod.scale          = 1.0
    ocean_mod.wave_scale     = 0.30
    ocean_mod.wave_scale_min = 0.01
    ocean_mod.choppiness     = 0.8
    ocean_mod.wind_velocity  = 6.0
    ocean_mod.spatial_size   = 50
    ocean_mod.random_seed    = 42

    # Subsurf for smooth displacement preview
    sub = ob.modifiers.new('Sub','SUBSURF')
    sub.levels = 1; sub.render_levels = 1

    ob["unity_note"] = ("REFERENCE ONLY – not the final water in Unity. "
                         "Y=0.0 is the exact water surface level.")
    ob["water_surface_y"] = 0.0

    assign_mat(ob, mat)
    smart_uv(ob)
    link(col, ob)
    return ob

def build_ocean_buoyancy_plane(col, mat):
    """Simple 200×200m flat quad – NO subdivision – used by Unity buoyancy scripts."""
    bpy.ops.mesh.primitive_plane_add(size=200.0, location=(0, 0, 0))
    ob = bpy.context.active_object
    ob.name = ob.data.name = "Ocean_Buoyancy_Plane"
    ob["unity_note"] = ("Assign to WaterSurface field in BoatBuoyancy.cs and "
                         "CharacterBuoyancy.cs. Y=0.0 exactly.")
    ob["water_surface_y"] = 0.0
    assign_mat(ob, mat)
    link(col, ob)
    return ob

def build_depth_markers(col):
    """5 empties at creature spawn depth zones."""
    depth_data = [
        ("Depth_0m",   0,   0,   0.0,  "Water surface – spawn floating items, small fish school"),
        ("Depth_5m",   0,   0,  -5.0,  "Shallow zone – coral, small fish, sea stars"),
        ("Depth_10m",  0,   0, -10.0,  "Mid-depth – Large Fish, Shark patrol territory"),
        ("Depth_20m",  0,   0, -20.0,  "Deep zone – Whale migration paths, Kraken Chest boss"),
        ("Depth_50m",  0,   0, -50.0,  "Abyss – reserved for future deep-sea content"),
    ]
    empties = []
    for name, x, y, z, note in depth_data:
        bpy.ops.object.empty_add(type='ARROWS', location=(x, y, z))
        e = bpy.context.active_object
        e.name = name
        e["depth_m"]    = abs(z)
        e["unity_note"] = note
        e.empty_display_size = 3.0
        link(col, e)
        empties.append(e)
    return empties

def build_buoy_float_reference(col):
    """Visual guides for buoy waterline and boat hull depth."""
    # Waterline marker ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=3.0, minor_radius=0.08,
        major_segments=40, minor_segments=6,
        location=(0, 0, 0))
    wl = bpy.context.active_object
    wl.name = "Ref_WaterlineRing"
    wl_mat = bpy.data.materials.new("Mat_WaterlineRef")
    wl_mat.use_nodes = True
    ns, lk = ns_lk(wl_mat); ns.clear()
    out = ns.new('ShaderNodeOutputMaterial'); out.location=(500,0)
    emit = ns.new('ShaderNodeEmission'); emit.location=(250,0)
    emit.inputs['Color'].default_value    = (1.0, 0.8, 0.0, 1)
    emit.inputs['Strength'].default_value = 2.0
    lk.new(emit.outputs['Emission'], out.inputs['Surface'])
    assign_mat(wl, wl_mat)
    link(col, wl)

    # Hull depth marker ring (-0.8m)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=2.5, minor_radius=0.06,
        major_segments=40, minor_segments=5,
        location=(0, 0, -0.8))
    hull = bpy.context.active_object
    hull.name = "Ref_HullDepthRing"
    hull_mat = bpy.data.materials.new("Mat_HullDepthRef")
    hull_mat.use_nodes = True
    ns2, lk2 = ns_lk(hull_mat); ns2.clear()
    out2 = ns2.new('ShaderNodeOutputMaterial'); out2.location=(500,0)
    emit2 = ns2.new('ShaderNodeEmission'); emit2.location=(250,0)
    emit2.inputs['Color'].default_value    = (0.0, 0.8, 1.0, 1)
    emit2.inputs['Strength'].default_value = 2.0
    lk2.new(emit2.outputs['Emission'], out2.inputs['Surface'])
    assign_mat(hull, hull_mat)
    link(col, hull)

    # Anchor depth marker (-3.0m)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=2.0, minor_radius=0.05,
        major_segments=40, minor_segments=5,
        location=(0, 0, -3.0))
    anc = bpy.context.active_object
    anc.name = "Ref_AnchorMinDepthRing"
    anc_mat = bpy.data.materials.new("Mat_AnchorDepthRef")
    anc_mat.use_nodes = True
    ns3, lk3 = ns_lk(anc_mat); ns3.clear()
    out3 = ns3.new('ShaderNodeOutputMaterial'); out3.location=(500,0)
    emit3 = ns3.new('ShaderNodeEmission'); emit3.location=(250,0)
    emit3.inputs['Color'].default_value    = (1.0, 0.2, 0.2, 1)
    emit3.inputs['Strength'].default_value = 2.0
    lk3.new(emit3.outputs['Emission'], out3.inputs['Surface'])
    assign_mat(anc, anc_mat)
    link(col, anc)
    return wl, hull, anc

def build_creature_spawn_zones(col):
    """Flat disc indicators showing horizontal creature spawn territories."""
    zones = [
        ("SpawnZone_SmallFish",    50,  0.0,  (0.2,0.8,0.2,1), 0.08),
        ("SpawnZone_LargeFish",    80, -5.0,  (0.2,0.5,0.9,1), 0.12),
        ("SpawnZone_Shark",       120, -8.0,  (0.9,0.2,0.2,1), 0.15),
        ("SpawnZone_Whale",       180,-15.0,  (0.4,0.4,0.9,1), 0.10),
    ]
    for zname, zr, zz, zcol, zstr in zones:
        bpy.ops.mesh.primitive_circle_add(vertices=48, radius=zr,
                                           fill_type='NGON', location=(0,0,zz))
        z_ob = bpy.context.active_object; z_ob.name = zname
        z_mat = bpy.data.materials.new(f"Mat_{zname}")
        z_mat.use_nodes = True
        ns_z, lk_z = ns_lk(z_mat); ns_z.clear()
        out_z = ns_z.new('ShaderNodeOutputMaterial'); out_z.location=(500,0)
        z_mat.blend_method='BLEND'
        bsdf_z = ns_z.new('ShaderNodeBsdfPrincipled'); bsdf_z.location=(250,0)
        bsdf_z.inputs['Base Color'].default_value=zcol
        bsdf_z.inputs['Alpha'].default_value=0.12
        lk_z.new(bsdf_z.outputs['BSDF'],out_z.inputs['Surface'])
        assign_mat(z_ob, z_mat)
        z_ob["unity_note"] = f"Sea creature spawn radius – see {zname.replace('SpawnZone_','')}.cs"
        link(col, z_ob)

# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
def create_ocean_reference():
    clear_scene()
    col = new_col("IsleTrial_OceanReference")

    mat_ocean   = build_ocean_surface_reference.__doc__ and build_ocean_preview_mat()
    mat_invis   = build_invisible_collider_mat()

    # build mats
    mat_ocean   = build_ocean_preview_mat()

    # ── 1. Ocean Surface Reference ─────────────────────────────────
    ocean_ref = build_ocean_surface_reference(col, mat_ocean)

    # ── 2. Buoyancy Plane ──────────────────────────────────────────
    buoy_plane = build_ocean_buoyancy_plane(col, mat_invis)
    # slight Z offset so it doesn't Z-fight with the reference
    buoy_plane.location.z = 0.001

    # ── 3. Depth Markers ───────────────────────────────────────────
    depth_markers = build_depth_markers(col)

    # ── 4. Visual depth reference rings ────────────────────────────
    wl_ring, hull_ring, anc_ring = build_buoy_float_reference(col)

    # ── 5. Creature spawn zone overlays ────────────────────────────
    build_creature_spawn_zones(col)

    # ── Custom properties for Unity pipeline ───────────────────────
    ocean_ref["water_surface_y"]         = 0.0
    ocean_ref["boat_hull_loaded_y"]      = -0.8
    ocean_ref["anchor_min_depth_y"]      = -3.0
    ocean_ref["ocean_modifier_wave_scale"] = 0.30

    # ── Print alignment notes ─────────────────────────────────────
    print("=" * 62)
    print("  IsleTrial – Ocean Reference Notes")
    print("=" * 62)
    print("  Water surface Y level       : 0.0")
    print("  Boat hull (loaded) Y extent : -0.8")
    print("  Anchor bottom chain min Y   : -3.0 minimum")
    print()
    print("  Depth Zone Guide:")
    print("    Depth_0m   :  Surface   – small fish, floating props")
    print("    Depth_5m   :  Shallow   – coral, reef fish, sea stars")
    print("    Depth_10m  :  Mid-water – large fish, shark patrols")
    print("    Depth_20m  :  Deep      – whale, KrakenChest boss")
    print("    Depth_50m  :  Abyss     – reserved / future content")
    print()
    print("  Unity Setup Instructions:")
    print("    1. Export Ocean_Buoyancy_Plane as FBX → assign to")
    print("       BoatBuoyancy.cs > WaterSurface field")
    print("    2. Ocean_Surface_Reference is PREVIEW ONLY –")
    print("       replace with Unity water shader in final build")
    print("    3. Depth marker empties guide creature SpawnManager.cs")
    print("    4. SpawnZone_* discs show creature territory radii –")
    print("       delete before export (reference use only)")
    print("=" * 62)
    print("✓ IsleTrial_OceanReference collection ready.")

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_all(center=True)
                    break

create_ocean_reference()
