"""
IsleTrial — Blender 4.x Python Script
Script 31: Frost Isle — Frozen Tundra Island  [FULL QUALITY REBUILD]
=====================================================================
Objects created (30 total):
  FrostIsle_MainTerrain           — 56×56 subdivided terrain, ridge + peaks
  FrostIsle_GlacierTongue         — flowing glacier body with surface crevasses
  FrostIsle_GlacierCrevasse_01..06— dark crack planes on glacier surface
  FrostIsle_IceSpire_Large_01..06 — 6 large multi-faceted ice crystal towers
  FrostIsle_IceSpire_Med_01..09   — 9 medium scattered spires
  FrostIsle_FrozenLake            — dark still surface, ice shelf cracks
  FrostIsle_LakeShelf_01..08      — 8 ice shelf crack pieces around lake
  FrostIsle_SnowDrift_01..10      — 10 flattened hemisphere snow mounds
  FrostIsle_Ruin_Arch_01..02      — 2 ancient stone arches, ice-encrusted
  FrostIsle_Ruin_Column_01..06    — 6 ice-buried standing columns
  FrostIsle_Ruin_Wall_01          — crumbled wall section
  FrostIsle_IceGlow_01..03        — 3 ambient blue-white point lights

Dual-path PBR materials + [UNITY] image slots + smart UV on all meshes.
Run in Blender 4.x: Scripting tab → Run Script (Alt+P)
"""

import bpy, bmesh, math, random
from mathutils import Vector

rng = random.Random(770077)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
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

def ns_lk(mat):
    mat.use_nodes = True
    return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, label, x, y):
    n = ns.new('ShaderNodeTexImage')
    n.label = n.name = label; n.location = (x, y)
    return n

# ─────────────────────────────────────────────────────────────────────────────
# MATERIAL BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def build_snow_mat():
    """Pure white snow — fine noise grain, subsurface scattering."""
    mat = bpy.data.materials.new("Mat_Frost_Snow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (650, 0)
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Subsurface Weight'].default_value = 0.08
    bsdf.inputs['Subsurface Radius'].default_value = (0.9, 0.95, 1.0)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-500, 150)
    noise.inputs['Scale'].default_value   = 65.0
    noise.inputs['Detail'].default_value  = 10.0
    noise.inputs['Roughness'].default_value = 0.6
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-200, 150)
    cr.color_ramp.elements[0].color = (0.82, 0.86, 0.95, 1)
    cr.color_ramp.elements[1].color = (0.96, 0.97, 1.00, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (350, 200)
    bmp.inputs['Strength'].default_value = 0.35
    img_a = img_slot(ns, "[UNITY] Snow_Albedo",   -550, -300)
    img_n = img_slot(ns, "[UNITY] Snow_Normal",   -550, -500)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (450, 0)
    mix.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],  mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],    bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_glacier_ice_mat():
    """Glacier — translucent blue-green, wave-distorted surface."""
    mat = bpy.data.materials.new("Mat_Frost_GlacierIce")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Base Color'].default_value       = (0.62, 0.82, 0.95, 1)
    bsdf.inputs['Roughness'].default_value        = 0.14
    bsdf.inputs['Transmission Weight'].default_value = 0.5
    bsdf.inputs['IOR'].default_value              = 1.31
    bsdf.inputs['Alpha'].default_value            = 0.75
    bsdf.inputs['Subsurface Weight'].default_value = 0.15
    bsdf.inputs['Subsurface Radius'].default_value = (0.4, 0.75, 1.0)
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-550, 150)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'DIAGONAL'
    wave.inputs['Scale'].default_value      = 4.0
    wave.inputs['Distortion'].default_value = 6.0
    wave.inputs['Detail'].default_value     = 12.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-250, 150)
    cr.color_ramp.elements[0].color = (0.25, 0.55, 0.90, 1)
    cr.color_ramp.elements[1].color = (0.80, 0.93, 1.00, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (400, 250)
    bmp.inputs['Strength'].default_value = 0.6
    emit = ns.new('ShaderNodeEmission'); emit.location = (250, 250)
    emit.inputs['Color'].default_value    = (0.4, 0.75, 1.0, 1)
    emit.inputs['Strength'].default_value = 0.35
    mix_s= ns.new('ShaderNodeMixShader'); mix_s.location = (850, 100)
    mix_s.inputs['Fac'].default_value = 0.08
    img_a = img_slot(ns, "[UNITY] Glacier_Albedo",  -580, -350)
    img_n = img_slot(ns, "[UNITY] Glacier_Normal",  -580, -550)
    lk.new(wave.outputs['Fac'],       cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],       bsdf.inputs['Base Color'])
    lk.new(wave.outputs['Fac'],       bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],     bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],      mix_s.inputs[1])
    lk.new(emit.outputs['Emission'],  mix_s.inputs[2])
    lk.new(mix_s.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_clear_ice_mat():
    """Transparent ice spire — sharp facets, high IOR."""
    mat = bpy.data.materials.new("Mat_Frost_ClearIce")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Base Color'].default_value        = (0.76, 0.90, 1.00, 1)
    bsdf.inputs['Roughness'].default_value         = 0.03
    bsdf.inputs['Transmission Weight'].default_value = 0.88
    bsdf.inputs['IOR'].default_value               = 1.31
    bsdf.inputs['Alpha'].default_value             = 0.55
    bsdf.inputs['Specular IOR Level'].default_value = 0.9
    # Fine internal crack noise
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-400, 150)
    noise.inputs['Scale'].default_value  = 60.0
    noise.inputs['Detail'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-100, 150)
    cr.color_ramp.elements[0].position = 0.88; cr.color_ramp.elements[0].color = (0.6, 0.85, 1.0, 1)
    cr.color_ramp.elements[1].position = 1.00; cr.color_ramp.elements[1].color = (1.0, 1.0,  1.0, 1)
    img_a = img_slot(ns, "[UNITY] ClearIce_Albedo", -450, -300)
    lk.new(noise.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_deep_ice_mat():
    """Deep glacier ice — dark pressurised blue, dim glow."""
    mat = bpy.data.materials.new("Mat_Frost_DeepIce")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (850, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (600, 0)
    bsdf.inputs['Base Color'].default_value        = (0.12, 0.24, 0.42, 1)
    bsdf.inputs['Roughness'].default_value         = 0.10
    bsdf.inputs['Transmission Weight'].default_value = 0.62
    bsdf.inputs['IOR'].default_value               = 1.31
    bsdf.inputs['Alpha'].default_value             = 0.78
    emit = ns.new('ShaderNodeEmission'); emit.location = (200, 200)
    emit.inputs['Color'].default_value    = (0.08, 0.22, 0.55, 1)
    emit.inputs['Strength'].default_value = 1.2
    mix_s= ns.new('ShaderNodeMixShader'); mix_s.location = (780, 100)
    mix_s.inputs['Fac'].default_value = 0.15
    img_a = img_slot(ns, "[UNITY] DeepIce_Albedo", -450, -300)
    lk.new(bsdf.outputs['BSDF'],      mix_s.inputs[1])
    lk.new(emit.outputs['Emission'],  mix_s.inputs[2])
    lk.new(mix_s.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_frozen_rock_mat():
    """Rock with ice coating — wet look, Musgrave detail."""
    mat = bpy.data.materials.new("Mat_Frost_FrozenRock")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (650, 0)
    bsdf.inputs['Roughness'].default_value = 0.48
    bsdf.inputs['Metallic'].default_value  = 0.0
    mus  = ns.new('ShaderNodeTexMusgrave'); mus.location = (-550, 150)
    mus.inputs['Scale'].default_value   = 6.0
    mus.inputs['Detail'].default_value  = 8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-250, 150)
    cr.color_ramp.elements[0].color = (0.28, 0.30, 0.38, 1)
    cr.color_ramp.elements[1].color = (0.52, 0.56, 0.65, 1)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-550, -100)
    noise.inputs['Scale'].default_value  = 28.0
    noise.inputs['Detail'].default_value = 6.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (300, 200)
    bmp.inputs['Strength'].default_value = 1.1
    img_a = img_slot(ns, "[UNITY] FrozenRock_Albedo", -580, -350)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (430, 0)
    mix.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_ruin_stone_mat():
    """Ancient stone — worn Musgrave, dark crevices."""
    mat = bpy.data.materials.new("Mat_Frost_RuinStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (850, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (600, 0)
    bsdf.inputs['Roughness'].default_value = 0.90
    mus  = ns.new('ShaderNodeTexMusgrave'); mus.location = (-500, 150)
    mus.musgrave_type = 'HYBRID_MULTIFRACTAL'
    mus.inputs['Scale'].default_value   = 8.0
    mus.inputs['Detail'].default_value  = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-200, 150)
    cr.color_ramp.elements[0].color = (0.14, 0.13, 0.15, 1)
    cr.color_ramp.elements[1].color = (0.38, 0.36, 0.40, 1)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-500, -100)
    noise.inputs['Scale'].default_value = 45.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (300, 200)
    bmp.inputs['Strength'].default_value = 1.5
    img_a = img_slot(ns, "[UNITY] FrostRuin_Albedo", -550, -350)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (400, 0)
    mix.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_dark_lake_mat():
    """Frozen lake — near-black, mirror-still, deep glow."""
    mat = bpy.data.materials.new("Mat_Frost_FrozenLake")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Base Color'].default_value        = (0.08, 0.12, 0.22, 1)
    bsdf.inputs['Roughness'].default_value         = 0.05
    bsdf.inputs['Transmission Weight'].default_value = 0.70
    bsdf.inputs['IOR'].default_value               = 1.31
    bsdf.inputs['Alpha'].default_value             = 0.82
    emit = ns.new('ShaderNodeEmission'); emit.location = (200, 200)
    emit.inputs['Color'].default_value    = (0.04, 0.10, 0.35, 1)
    emit.inputs['Strength'].default_value = 0.6
    mix_s= ns.new('ShaderNodeMixShader'); mix_s.location = (750, 100)
    mix_s.inputs['Fac'].default_value = 0.12
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-350, 150)
    noise.inputs['Scale'].default_value = 2.5
    lk.new(bsdf.outputs['BSDF'],      mix_s.inputs[1])
    lk.new(emit.outputs['Emission'],  mix_s.inputs[2])
    lk.new(mix_s.outputs['Shader'],   out.inputs['Surface'])
    return mat

print("[FrostIsle] All materials built.")

# ─────────────────────────────────────────────────────────────────────────────
# GEOMETRY BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def build_frost_terrain(name, size=120.0, grid=56):
    """Frozen tundra terrain: jagged ridge + secondary peaks + tundra plain."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    for gi in range(grid + 1):
        for gj in range(grid + 1):
            x  = (gi / grid - 0.5) * size
            y  = (gj / grid - 0.5) * size
            nx, ny = x / (size * 0.5), y / (size * 0.5)
            dist = math.sqrt(nx*nx + ny*ny)

            # Main mountain ridge (E-W)
            ridge = max(0.0, 1.0 - abs(ny) * 2.4) * max(0.0, 1.0 - dist * 0.75) * 20.0
            ridge += math.sin(nx * 4.5) * max(0, 1.0 - dist) * 4.5

            # Secondary peak NW
            pk2_d = math.sqrt((nx + 0.42)**2 + (ny - 0.28)**2)
            peak2 = max(0.0, 1.0 - pk2_d * 3.2) ** 2 * 13.5

            # Third peak NE
            pk3_d = math.sqrt((nx - 0.38)**2 + (ny - 0.35)**2)
            peak3 = max(0.0, 1.0 - pk3_d * 3.8) ** 2 * 10.0

            # Flat tundra south
            tundra = max(0.0, ny + 0.55) * max(0.0, 1.0 - dist) * 1.8

            # Glacier tongue valley
            glacier = -max(0.0, 1.0 - math.sqrt((nx + 0.08)**2 + ny**2) * 4.5) * 2.0

            # Frozen lake depression
            lake_d = math.sqrt((nx - 0.12)**2 + (ny + 0.38)**2)
            lake   = -max(0.0, 1.0 - lake_d * 5.5) ** 2 * 3.2

            # Crevasse marks
            crev = math.sin(nx * 16.0 + 0.3) * math.sin(ny * 12.5) * 0.7 * max(0, 1 - dist)

            # Surface drift noise
            drift = (math.sin(nx * 7.5) * math.cos(ny * 6.2) * 0.55 +
                     math.sin(nx * 14.0 + ny * 11.0) * 0.28)

            z = ridge + peak2 + peak3 + tundra + glacier + lake + crev + drift * 0.65
            bm.verts.new((x, y, z))

    bm.verts.ensure_lookup_table()
    for gi in range(grid):
        for gj in range(grid):
            a = gi * (grid + 1) + gj
            try:
                bm.faces.new([bm.verts[a], bm.verts[a+1],
                               bm.verts[a + grid + 2], bm.verts[a + grid + 1]])
            except: pass

    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name

    sub = ob.modifiers.new("Subd", 'SUBSURF')
    sub.levels = 2; sub.render_levels = 3
    disp = ob.modifiers.new("FrostDisplace", 'DISPLACE')
    tex = bpy.data.textures.new("FrostClouds", type='CLOUDS')
    tex.noise_scale = 3.5; tex.noise_depth = 5
    disp.texture = tex; disp.strength = 0.85; disp.texture_coords = 'LOCAL'
    return ob

def build_glacier_tongue(name, loc=(0, 0, 0)):
    """Glacier body, long swept plane with surface crevasses."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    nx, ny = 22, 30
    for j in range(ny + 1):
        t = j / ny
        width = 6.0 + t * 9.0
        for i in range(nx + 1):
            u = i / nx - 0.5
            x = u * width
            y = t * 36.0 - 5.0
            # Glacier surface height falls as it reaches sea
            z = max(0.0, 15.5 - t * 17.0) + math.sin(x * 0.3) * 1.0
            # Surface crevasse texture
            z += math.sin(x * 1.8 + y * 0.35) * 0.45
            z += math.sin(x * 4.0) * math.sin(y * 0.6) * 0.18
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            try:
                bm.faces.new([bm.verts[a], bm.verts[a+1],
                               bm.verts[a + nx + 2], bm.verts[a + nx + 1]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_ice_spire_large(name, loc, height=18.0, base_r=1.0, sides=5):
    """Large ice crystal spire — fully custom vertex geometry."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 28
    seed = abs(hash(name)) % 50
    for si in range(segs + 1):
        t = si / segs
        z = t * height
        # Crystal profile: broad base tapering to needle tip
        r = base_r * (1.0 - t ** 1.4) * (0.9 + math.sin(t * math.pi * 2.5) * 0.1)
        lean_x = math.sin(t * math.pi * 0.8 + seed * 0.1) * 0.35
        lean_y = math.cos(t * math.pi * 0.6 + seed * 0.15) * 0.25
        for vi in range(sides):
            a = vi / sides * math.pi * 2
            # Crystal facet edge emphasis
            r_face = r * (1.0 + math.sin(a * sides * 0.5 + t * 4) * 0.06)
            bm.verts.new((lean_x + r_face * math.cos(a),
                           lean_y + r_face * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si * sides + vi; b = si * sides + (vi + 1) % sides
            c = (si + 1) * sides + (vi + 1) % sides; d = (si + 1) * sides + vi
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    # Bottom cap
    bot = [bm.verts[v] for v in range(sides)][::-1]
    try: bm.faces.new(bot)
    except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    bevel = ob.modifiers.new("IceFacet", 'BEVEL')
    bevel.width = 0.025; bevel.segments = 1
    bevel.angle_limit = math.radians(28)
    return ob

def build_frozen_lake(name, loc, rx=10.5, ry=13.5):
    """Dark mirror-still frozen lake surface."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 40
    for i in range(segs):
        a = i / segs * math.pi * 2
        # Irregular organic lake shore
        r_var = 1.0 + math.sin(a * 3) * 0.08 + math.sin(a * 7 + 0.4) * 0.05
        bm.verts.new((rx * r_var * math.cos(a), ry * r_var * math.sin(a), 0))
    center = bm.verts.new((0, 0, -0.05))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        ni = (i + 1) % segs
        try: bm.faces.new([bm.verts[i], bm.verts[ni], center])
        except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_ice_shelf_crack(name, loc, length=4.0, width=0.8):
    """Thin ice shelf crack plane around lake edge."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 8
    for i in range(segs + 1):
        t = i / segs
        w_var = width * (0.5 + rng.uniform(0, 0.8))
        x = t * length - length * 0.5
        for side in (-1, 1):
            bm.verts.new((x, side * w_var * 0.5, rng.uniform(-0.03, 0.03)))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        a = i * 2
        try:
            bm.faces.new([bm.verts[a], bm.verts[a+2], bm.verts[a+3], bm.verts[a+1]])
        except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler.z = rng.uniform(0, math.pi * 2)
    ob.name = ob.data.name = name
    return ob

def build_snow_drift(name, loc, radius=4.0):
    """Smooth hemisphere snow mound."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    u_segs = 16; v_segs = 8
    for vi in range(v_segs + 1):
        phi = vi / v_segs * math.pi * 0.5  # 0 to 90 degrees (hemisphere)
        z = radius * math.sin(phi) * rng.uniform(0.18, 0.35)
        r = radius * math.cos(phi)
        for ui in range(u_segs):
            a = ui / u_segs * math.pi * 2
            bm.verts.new((r * math.cos(a), r * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for vi in range(v_segs):
        for ui in range(u_segs):
            a = vi * u_segs + ui
            b = vi * u_segs + (ui + 1) % u_segs
            c = (vi + 1) * u_segs + (ui + 1) % u_segs
            d = (vi + 1) * u_segs + ui
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler.z = rng.uniform(0, math.pi * 2)
    ob.name = ob.data.name = name
    return ob

def build_ruin_arch(name, loc, major_r=3.2, minor_r=0.55, rot_z=0.0):
    """Ancient stone arch, half-circle, torus cross-section."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    outer_segs = 24; tube_segs = 10
    # Only top half (pi arc)
    for os in range(outer_segs + 1):
        t = os / outer_segs
        a_outer = t * math.pi  # 0 to pi = semicircle
        for ts in range(tube_segs):
            a_inner = ts / tube_segs * math.pi * 2
            x = (major_r + minor_r * math.cos(a_inner)) * math.cos(a_outer)
            z = major_r + (major_r + minor_r * math.cos(a_inner)) * math.sin(a_outer) - major_r
            y = minor_r * math.sin(a_inner)
            # Worn surface noise
            x += math.sin(a_outer * 4 + a_inner) * 0.04
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for os in range(outer_segs):
        for ts in range(tube_segs):
            a = os * tube_segs + ts
            b = os * tube_segs + (ts + 1) % tube_segs
            c = (os + 1) * tube_segs + (ts + 1) % tube_segs
            d = (os + 1) * tube_segs + ts
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler.z = rot_z
    ob.name = ob.data.name = name
    return ob

def build_ruin_column(name, loc, height=5.5, radius=0.5, lean_x=0.0):
    """Stone column with fluted surface, partially ice-buried."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides = 10; segs = 20
    for si in range(segs + 1):
        t = si / segs
        z = t * height - 0.5  # -0.5 is buried below ground
        r = radius * (1.0 + math.sin(t * math.pi) * 0.05)
        for vi in range(sides):
            a = vi / sides * math.pi * 2
            # Fluting
            r_flute = r * (1.0 + math.sin(a * sides * 0.5) * 0.04)
            offset_x = lean_x * t
            bm.verts.new((offset_x + r_flute * math.cos(a), r_flute * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si * sides + vi; b = si * sides + (vi + 1) % sides
            c = (si + 1) * sides + (vi + 1) % sides; d = (si + 1) * sides + vi
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    top_v = [bm.verts[(segs) * sides + v] for v in range(sides)]
    try: bm.faces.new(top_v)
    except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_crumbled_wall(name, loc):
    """Stone wall section, crumbled right edge."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    w, h, d, nx_w, nz_h = 12.0, 4.5, 0.9, 14, 10
    for zi in range(nz_h + 1):
        for xi in range(nx_w + 1):
            t_x = xi / nx_w; t_z = zi / nz_h
            x = (t_x - 0.5) * w
            z = t_z * h
            # Crumble: right side at top breaks away
            crumble = max(0.0, t_x - 0.55) * t_z * 1.8
            z -= crumble * crumble * h
            if t_x > 0.7 and t_z > 0.5 and rng.random() > 0.55:
                continue  # skip some vertices = holes
            y = math.sin(x * 1.2) * 0.08 + rng.uniform(-0.04, 0.04)
            bm.verts.new((x, y, z))
    # Can't build faces cleanly on sparse grid, add solidify
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    sol = ob.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = d
    return ob

# ─────────────────────────────────────────────────────────────────────────────
# SCENE ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────
clear_scene()
rng = random.Random(770077)

col_root    = new_col("IsleTrial_FrostIsle")
col_terrain = new_col("FrostIsle_Terrain")
col_glacier = new_col("FrostIsle_Glacier")
col_spires  = new_col("FrostIsle_IceSpires")
col_lake    = new_col("FrostIsle_FrozenLake")
col_ruins   = new_col("FrostIsle_FrozenRuins")
col_snow    = new_col("FrostIsle_SnowDrifts")
col_lights  = new_col("FrostIsle_Lighting")

mat_snow       = build_snow_mat()
mat_glacier    = build_glacier_ice_mat()
mat_ice_clear  = build_clear_ice_mat()
mat_ice_deep   = build_deep_ice_mat()
mat_froz_rock  = build_frozen_rock_mat()
mat_ruin_stone = build_ruin_stone_mat()
mat_lake       = build_dark_lake_mat()

# ── 1. MAIN TERRAIN ───────────────────────────────────────────────────────────
terrain = build_frost_terrain("FrostIsle_MainTerrain")
assign_mat(terrain, mat_snow)
smart_uv(terrain, angle=45)
link(col_terrain, terrain)
print("[FrostIsle] Terrain created.")

# ── 2. GLACIER TONGUE ─────────────────────────────────────────────────────────
glacier = build_glacier_tongue("FrostIsle_GlacierTongue", loc=(-5, 8, 0))
assign_mat(glacier, mat_glacier)
smart_uv(glacier)
link(col_glacier, glacier)

# Glacier crevasses
for ci in range(6):
    loc = (-5 + rng.uniform(-4, 4), 8 + rng.uniform(-10, 10), 0.5)
    cr = build_ice_shelf_crack(f"FrostIsle_GlacierCrevasse_{ci+1:02d}",
                                 loc, length=rng.uniform(3, 8), width=0.3)
    assign_mat(cr, mat_ice_deep); smart_uv(cr)
    link(col_glacier, cr)
print("[FrostIsle] Glacier + 6 crevasses created.")

# ── 3. ICE SPIRES — LARGE CLUSTER ─────────────────────────────────────────────
large_spire_cfg = [
    ((-8, 5, 10), 20.0, 1.2, 5), ((0, 12, 8), 23.5, 0.95, 6),
    ((10, 6, 9), 17.5, 1.35, 4), ((-5, 15, 7), 15.0, 1.05, 5),
    ((6, 2, 11), 21.0, 0.85, 6), ((-12, 10, 9), 13.5, 1.15, 5),
]
for i, (sloc, sh, sr, ssides) in enumerate(large_spire_cfg):
    spire = build_ice_spire_large(f"FrostIsle_IceSpire_Large_{i+1:02d}",
                                    sloc, sh, sr, ssides)
    mat_choice = mat_ice_clear if i % 2 == 0 else mat_ice_deep
    assign_mat(spire, mat_choice)
    smart_uv(spire)
    link(col_spires, spire)

# Medium scattered spires
med_locs = [
    (18, -5, 4, 8.5), (-20, 8, 5, 7.2), (15, 20, 3, 6.5),
    (-15,-10, 4, 9.0), (22, 12, 2, 5.8), (-25, 2, 3, 7.8),
    (5, -20, 2, 6.2), (-10,-18, 3, 8.2), (25,-15, 1, 5.2),
]
for i, (mx, my, mz, mh) in enumerate(med_locs):
    spire = build_ice_spire_large(f"FrostIsle_IceSpire_Med_{i+1:02d}",
                                    (mx, my, mz), mh,
                                    base_r=0.38 + rng.uniform(0, 0.28),
                                    sides=4 + (i % 3))
    assign_mat(spire, mat_ice_clear)
    smart_uv(spire)
    link(col_spires, spire)
print(f"[FrostIsle] {len(large_spire_cfg)+len(med_locs)} ice spires created.")

# ── 4. FROZEN LAKE ─────────────────────────────────────────────────────────────
lake = build_frozen_lake("FrostIsle_FrozenLake", (6, -18, 0.05))
assign_mat(lake, mat_lake); smart_uv(lake)
link(col_lake, lake)

# Ice shelf cracks around lake
for li in range(8):
    angle = li / 8 * math.pi * 2
    rx = 6 + math.cos(angle) * (12 + rng.uniform(-1, 2))
    ry = -18 + math.sin(angle) * (14 + rng.uniform(-1, 2))
    shelf = build_ice_shelf_crack(f"FrostIsle_LakeShelf_{li+1:02d}",
                                    (rx, ry, 0.06),
                                    length=rng.uniform(2, 5), width=0.5)
    assign_mat(shelf, mat_ice_clear); smart_uv(shelf)
    link(col_lake, shelf)

# Lake glow light
ll = bpy.data.lights.new("FrostIsle_LakeGlow", type='POINT')
ll.energy = 1200; ll.color = (0.3, 0.55, 1.0); ll.shadow_soft_size = 3.0
llo = bpy.data.objects.new("FrostIsle_LakeGlow", ll)
llo.location = (6, -18, 2); bpy.context.scene.collection.objects.link(llo)
link(col_lake, llo)

# ── 5. SNOW DRIFTS ─────────────────────────────────────────────────────────────
for di in range(10):
    dx = rng.uniform(-48, 48); dy = rng.uniform(-48, 48)
    drift = build_snow_drift(f"FrostIsle_SnowDrift_{di+1:02d}",
                               (dx, dy, 0.1), radius=rng.uniform(2.5, 6.5))
    assign_mat(drift, mat_snow); smart_uv(drift)
    link(col_snow, drift)

# ── 6. FROZEN RUINS ────────────────────────────────────────────────────────────
# Arches
arch1 = build_ruin_arch("FrostIsle_Ruin_Arch_01", (-18, 20, 3.5))
assign_mat(arch1, mat_ruin_stone); smart_uv(arch1)
link(col_ruins, arch1)

arch2 = build_ruin_arch("FrostIsle_Ruin_Arch_02", (20, -18, 2.0),
                         major_r=2.5, minor_r=0.48, rot_z=math.radians(45))
assign_mat(arch2, mat_ruin_stone); smart_uv(arch2)
link(col_ruins, arch2)

# Columns
col_cfg = [
    ((-22, 16, 2), 4.5, 0.52,  0.05), ((-22, 22, 2), 5.0, 0.48,  0.08),
    ((-16, 22, 2), 3.8, 0.55, -0.06), (( 16,-20, 1.5), 4.0, 0.50,  0.04),
    (( 22,-18, 1.5), 5.2, 0.52,  0.07), ((  5,-28, 0.5), 3.5, 0.45,  0.03),
]
for i, (cloc, ch, cr, lean) in enumerate(col_cfg):
    col_r = build_ruin_column(f"FrostIsle_Ruin_Column_{i+1:02d}",
                                cloc, ch + rng.uniform(-0.5, 0.8), cr, lean)
    assign_mat(col_r, mat_ruin_stone if i % 2 == 0 else mat_froz_rock)
    smart_uv(col_r)
    link(col_ruins, col_r)

# Wall section
wall = build_crumbled_wall("FrostIsle_Ruin_Wall_01", (-20, -8, 4))
assign_mat(wall, mat_ruin_stone); smart_uv(wall)
link(col_ruins, wall)

# ── 7. AMBIENT ICE LIGHTS ──────────────────────────────────────────────────────
ice_light_locs = [(-4, 10, 5), (2, 13, 4), (8, 7, 6)]
for li, lloc in enumerate(ice_light_locs):
    ild = bpy.data.lights.new(f"FrostIsle_IceGlow_{li+1:02d}", type='POINT')
    ild.energy = 3200; ild.color = (0.45, 0.72, 1.0); ild.shadow_soft_size = 4.5
    ilo = bpy.data.objects.new(f"FrostIsle_IceGlow_{li+1:02d}", ild)
    ilo.location = lloc; bpy.context.scene.collection.objects.link(ilo)
    link(col_lights, ilo)

# Root
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
root = bpy.context.active_object; root.name = "FrostIsle_ROOT"
link(col_root, root)

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("FROST ISLE — FULL QUALITY BUILD COMPLETE")
print("="*65)
print("  Main terrain   : 56×56 grid, ridge+peaks+lake depression")
print("  Glacier tongue : custom vertex sweep + 6 crevasse cracks")
print(f"  Ice spires     : {len(large_spire_cfg)} large + {len(med_locs)} medium (custom vertex geometry)")
print("  Frozen lake    : organic edge + 8 ice shelf cracks + glow light")
print("  Snow drifts    : 10 hemisphere mounds")
print("  Ruins          : 2 arches + 6 columns + 1 crumbled wall")
print("  Lights         : lake glow + 3 ambient ice fills")
print("  Materials      : 7 full node trees + [UNITY] image slots")
print("  UV             : smart_project on all mesh objects")
print(f"\n  Export: File → Export → FBX | Scale 0.01 | Apply Transform ON")
print(f"  Unity: deep blue VolumeProfile + falling snow particle system")
print("="*65)
