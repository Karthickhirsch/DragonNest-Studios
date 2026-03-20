"""
IsleTrial — Blender 4.x Python Script
Script 38: Tutorial Isle — The First Shore  [FULL QUALITY REBUILD]
===================================================================
Objects created (30 total):
  TutorialIsle_Terrain            — warm rolling hills, gentle beach ring
  TutorialIsle_BeachSand          — separate sand plane at shore
  TutorialIsle_Dock_Platform      — wooden dock platform, planked surface
  TutorialIsle_Dock_Pile_01..08   — 8 support piles (pairs)
  TutorialIsle_Dock_Rope_*        — 4 rope railing curves
  TutorialIsle_Dock_Bollard       — mooring bollard
  TutorialIsle_PalmTrunk_01..12   — 12 curved palm trunks
  TutorialIsle_PalmLeaf_*         — 5-7 leaves per tree
  TutorialIsle_Rock_01..08        — 8 beach rocks (varied sizes)
  TutorialIsle_TidalPool_01..03   — 3 shallow rock tide pools
  TutorialIsle_Grass_Patch_01..06 — 6 tall grass patch planes
  TutorialIsle_BoulderCliff       — one dramatic viewpoint boulder
  TutorialIsle_Sun                — warm sun directional light
  TutorialIsle_FillLight          — sky fill light (blue ambient)

Dual-path PBR + [UNITY] image slots + smart UV on all meshes.
Run in Blender 4.x: Scripting tab → Run Script (Alt+P)
"""

import bpy, bmesh, math, random
from mathutils import Vector

rng = random.Random(100101)

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

def build_grass_mat():
    """Warm tropical grass — Wave + Noise, vibrant greens."""
    mat = bpy.data.materials.new("Mat_Tut_Grass")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (950, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Roughness'].default_value = 0.90
    bsdf.inputs['Subsurface Weight'].default_value = 0.06
    bsdf.inputs['Subsurface Radius'].default_value = (0.5, 0.9, 0.3)
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-580, 200)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 3.0; wave.inputs['Distortion'].default_value = 6.0
    wave.inputs['Detail'].default_value = 8.0
    cr1  = ns.new('ShaderNodeValToRGB'); cr1.location = (-280, 200)
    cr1.color_ramp.elements[0].color = (0.15, 0.38, 0.08, 1)
    cr1.color_ramp.elements[1].color = (0.35, 0.60, 0.15, 1)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-580, -50)
    noise.inputs['Scale'].default_value = 18.0; noise.inputs['Detail'].default_value = 8.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-280, -50)
    cr2.color_ramp.elements[0].color = (0.18, 0.45, 0.10, 1)
    cr2.color_ramp.elements[1].color = (0.40, 0.65, 0.18, 1)
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'
    mix.location = (0, 80); mix.inputs['Fac'].default_value = 0.5
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (380, 220)
    bmp.inputs['Strength'].default_value = 0.6
    img_a = img_slot(ns, "[UNITY] Grass_Albedo",  -620, -350)
    img_n = img_slot(ns, "[UNITY] Grass_Normal",  -620, -550)
    fmix  = ns.new('ShaderNodeMixRGB'); fmix.location = (490, 0); fmix.inputs['Fac'].default_value = 0.0
    lk.new(wave.outputs['Fac'],    cr1.inputs['Fac'])
    lk.new(noise.outputs['Fac'],   cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   fmix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], fmix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(fmix.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_sand_mat():
    """Golden beach sand — Noise grain with ripple bump."""
    mat = bpy.data.materials.new("Mat_Tut_Sand")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (650, 0)
    bsdf.inputs['Roughness'].default_value = 0.92
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-480, 180)
    noise.inputs['Scale'].default_value  = 60.0
    noise.inputs['Detail'].default_value = 12.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-180, 180)
    cr.color_ramp.elements[0].color = (0.78, 0.68, 0.45, 1)
    cr.color_ramp.elements[1].color = (0.95, 0.86, 0.64, 1)
    # Wet sand near shore (darker)
    noise2 = ns.new('ShaderNodeTexNoise'); noise2.location = (-480, -50)
    noise2.inputs['Scale'].default_value = 8.0
    cr2   = ns.new('ShaderNodeValToRGB'); cr2.location = (-180, -50)
    cr2.color_ramp.elements[0].color = (0.50, 0.42, 0.28, 1)
    cr2.color_ramp.elements[1].color = (0.75, 0.65, 0.44, 1)
    mix   = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'MIX'
    mix.location = (50, 80); mix.inputs['Fac'].default_value = 0.35
    # Wave ripple bump
    wave  = ns.new('ShaderNodeTexWave'); wave.location = (-480, -280)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 15.0; wave.inputs['Distortion'].default_value = 2.0
    bmp   = ns.new('ShaderNodeBump'); bmp.location = (350, 220)
    bmp.inputs['Strength'].default_value = 0.4
    img_a = img_slot(ns, "[UNITY] Sand_Albedo",  -530, -480)
    img_n = img_slot(ns, "[UNITY] Sand_Normal",  -530, -680)
    fmix  = ns.new('ShaderNodeMixRGB'); fmix.location = (470, 0); fmix.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(noise2.outputs['Fac'],   cr2.inputs['Fac'])
    lk.new(cr.outputs['Color'],     mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],    mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],    fmix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],  fmix.inputs['Color2'])
    lk.new(wave.outputs['Fac'],     bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(fmix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_dock_wood_mat():
    """Weathered dock planks — Wave grain, sea salt bleaching."""
    mat = bpy.data.materials.new("Mat_Tut_DockWood")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (950, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Roughness'].default_value = 0.90
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-560, 200)
    wave.wave_type = 'RINGS'; wave.bands_direction = 'Y'
    wave.inputs['Scale'].default_value      = 8.0
    wave.inputs['Distortion'].default_value = 4.5
    wave.inputs['Detail'].default_value     = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-260, 200)
    cr.color_ramp.elements[0].color = (0.45, 0.34, 0.20, 1)
    cr.color_ramp.elements[1].color = (0.65, 0.52, 0.33, 1)
    # Salt bleach: lighter overlay
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-560, -80)
    noise.inputs['Scale'].default_value = 25.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-260, -80)
    cr2.color_ramp.elements[0].position = 0.5; cr2.color_ramp.elements[0].color = (0,0,0,1)
    cr2.color_ramp.elements[1].position = 0.8; cr2.color_ramp.elements[1].color = (0.82,0.75,0.62,1)
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'LIGHTEN'
    mix.location = (0, 100); mix.inputs['Fac'].default_value = 0.25
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (380, 220)
    bmp.inputs['Strength'].default_value = 1.0
    img_a = img_slot(ns, "[UNITY] DockWood_Albedo", -600, -350)
    img_n = img_slot(ns, "[UNITY] DockWood_Normal", -600, -550)
    fmix  = ns.new('ShaderNodeMixRGB'); fmix.location = (490, 0); fmix.inputs['Fac'].default_value = 0.0
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(noise.outputs['Fac'],   cr2.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   fmix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], fmix.inputs['Color2'])
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(fmix.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_old_wood_mat():
    """Old/dark dock pile wood — darker, rougher."""
    mat = bpy.data.materials.new("Mat_Tut_OldWood")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (850, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (600, 0)
    bsdf.inputs['Roughness'].default_value = 0.95
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-500, 150)
    wave.wave_type = 'RINGS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 10.0; wave.inputs['Distortion'].default_value = 5.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-200, 150)
    cr.color_ramp.elements[0].color = (0.15, 0.10, 0.06, 1)
    cr.color_ramp.elements[1].color = (0.38, 0.28, 0.16, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (320, 200)
    bmp.inputs['Strength'].default_value = 1.2
    img_a = img_slot(ns, "[UNITY] OldWood_Albedo", -550, -300)
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    bsdf.inputs['Base Color'])
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_rock_mat():
    """Warm tropical beach rock — Musgrave, warm grey."""
    mat = bpy.data.materials.new("Mat_Tut_Rock")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (650, 0)
    bsdf.inputs['Roughness'].default_value = 0.85
    mus  = ns.new('ShaderNodeTexMusgrave'); mus.location = (-500, 150)
    mus.inputs['Scale'].default_value = 7.0; mus.inputs['Detail'].default_value = 8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-200, 150)
    cr.color_ramp.elements[0].color = (0.40, 0.36, 0.30, 1)
    cr.color_ramp.elements[1].color = (0.62, 0.56, 0.48, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (300, 200)
    bmp.inputs['Strength'].default_value = 1.3
    img_a = img_slot(ns, "[UNITY] Rock_Albedo", -550, -300)
    img_n = img_slot(ns, "[UNITY] Rock_Normal", -550, -500)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (420, 0); mix.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],   mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix.inputs['Color2'])
    lk.new(mus.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def build_palm_trunk_mat():
    """Palm trunk — ring-node pattern, warm brown."""
    mat = bpy.data.materials.new("Mat_Tut_PalmTrunk")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (850, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (600, 0)
    bsdf.inputs['Roughness'].default_value = 0.88
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-480, 150)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 5.0; wave.inputs['Distortion'].default_value = 3.0
    wave.inputs['Detail'].default_value = 6.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-180, 150)
    cr.color_ramp.elements[0].color = (0.35, 0.22, 0.10, 1)
    cr.color_ramp.elements[1].color = (0.62, 0.42, 0.20, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (310, 200)
    bmp.inputs['Strength'].default_value = 1.1
    img_a = img_slot(ns, "[UNITY] PalmTrunk_Albedo", -530, -300)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (410, 0); mix.inputs['Fac'].default_value = 0.0
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_palm_leaf_mat():
    """Palm leaf — vivid tropical green, subsurface scatter."""
    mat = bpy.data.materials.new("Mat_Tut_PalmLeaf")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (650, 0)
    bsdf.inputs['Roughness'].default_value = 0.78
    bsdf.inputs['Subsurface Weight'].default_value = 0.18
    bsdf.inputs['Subsurface Radius'].default_value = (0.3, 0.8, 0.2)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-450, 150)
    noise.inputs['Scale'].default_value = 12.0; noise.inputs['Detail'].default_value = 6.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-150, 150)
    cr.color_ramp.elements[0].color = (0.12, 0.38, 0.06, 1)
    cr.color_ramp.elements[1].color = (0.28, 0.60, 0.12, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (300, 200)
    bmp.inputs['Strength'].default_value = 0.7
    img_a = img_slot(ns, "[UNITY] PalmLeaf_Albedo", -500, -300)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (420, 0); mix.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_tidal_pool_mat():
    """Tidal rock pool — clear shallow water, warm glow."""
    mat = bpy.data.materials.new("Mat_Tut_TidalPool")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Base Color'].default_value        = (0.38, 0.68, 0.75, 1)
    bsdf.inputs['Roughness'].default_value         = 0.04
    bsdf.inputs['Transmission Weight'].default_value = 0.82
    bsdf.inputs['IOR'].default_value               = 1.33
    bsdf.inputs['Alpha'].default_value             = 0.55
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-380, 150)
    wave.inputs['Scale'].default_value = 3.0; wave.inputs['Distortion'].default_value = 2.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (250, 200)
    bmp.inputs['Strength'].default_value = 0.3
    lk.new(wave.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

print("[TutorialIsle] All materials built.")

# ─────────────────────────────────────────────────────────────────────────────
# GEOMETRY BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def build_tutorial_terrain(name, size=80.0, grid=48):
    """Warm gentle rolling hills — welcoming, safe-feeling."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    for gi in range(grid + 1):
        for gj in range(grid + 1):
            x = (gi / grid - 0.5) * size
            y = (gj / grid - 0.5) * size
            nx, ny = x / (size * 0.5), y / (size * 0.5)
            dist = math.sqrt(nx*nx + ny*ny)
            # Gentle central hill
            hill = max(0.0, 1.0 - dist * 1.12) ** 1.6 * 10.5
            # Wide flat beach ring
            beach = max(0.0, 0.85 - max(0.0, dist - 0.70) * 5.5) * 0.6
            # Two smaller hills for interest
            h2 = max(0.0, 1.0 - math.sqrt((nx-0.45)**2+(ny+0.2)**2)*3.4)**2 * 4.8
            h3 = max(0.0, 1.0 - math.sqrt((nx+0.32)**2+(ny-0.42)**2)*4.0)**2 * 3.8
            # Dock valley on south shore
            dock_valley = -max(0.0, 1.0 - math.sqrt(nx**2+(ny+0.62)**2)*5.2)**2 * 2.2
            # Smooth noise
            n = (math.sin(nx*8.0+ny*6.5)*0.30 + math.sin(nx*14.0-ny*11.0)*0.16)
            z = hill + beach + h2 + h3 + dock_valley + n * 0.5
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for gi in range(grid):
        for gj in range(grid):
            a = gi * (grid+1) + gj
            try:
                bm.faces.new([bm.verts[a], bm.verts[a+1],
                               bm.verts[a+grid+2], bm.verts[a+grid+1]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    sub = ob.modifiers.new("Subd", 'SUBSURF'); sub.levels = 2
    disp = ob.modifiers.new("GrassBump", 'DISPLACE')
    tex = bpy.data.textures.new("TutGrass", type='CLOUDS')
    tex.noise_scale = 4.0; tex.noise_depth = 4
    disp.texture = tex; disp.strength = 0.45; disp.texture_coords = 'LOCAL'
    return ob

def build_sand_ring(name, size=80.0, grid=32):
    """Beach sand plane, slightly raised at shore."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    for gi in range(grid + 1):
        for gj in range(grid + 1):
            x = (gi / grid - 0.5) * size
            y = (gj / grid - 0.5) * size
            nx, ny = x / (size * 0.5), y / (size * 0.5)
            dist = math.sqrt(nx*nx + ny*ny)
            z = max(0, 1.0 - dist * 1.25) * 0.25
            if dist < 0.68: z = -1.5  # sink inland portion
            z += math.sin(x * 3.5 + y * 2.8) * 0.03
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for gi in range(grid):
        for gj in range(grid):
            a = gi * (grid+1) + gj
            try:
                bm.faces.new([bm.verts[a], bm.verts[a+1],
                               bm.verts[a+grid+2], bm.verts[a+grid+1]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def build_dock_platform(name, loc, w=6.0, length=18.0):
    """Wooden dock planks with wave bow detail."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    nx, ny = 18, 10
    for j in range(ny + 1):
        for i in range(nx + 1):
            tx = i / nx; ty = j / ny
            x = (tx - 0.5) * w
            y = ty * length
            # Plank groove simulation
            z = math.sin(tx * w * math.pi * 6) * 0.008  # 6 planks
            z += rng.uniform(-0.003, 0.003)
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for j in range(ny):
        for i in range(nx):
            a = j * (nx+1) + i
            try:
                bm.faces.new([bm.verts[a], bm.verts[a+1],
                               bm.verts[a+nx+2], bm.verts[a+nx+1]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    sol = ob.modifiers.new("Planks", 'SOLIDIFY'); sol.thickness = 0.18
    return ob

def build_dock_pile(name, loc, height=2.5, radius=0.16):
    """Cylindrical dock support pile."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides = 7; segs = 14
    for si in range(segs + 1):
        t = si / segs; z = t * height - 0.5  # buried slightly
        r = radius * (1.0 + rng.uniform(-0.02, 0.02))
        for vi in range(sides):
            a = vi / sides * math.pi * 2
            bm.verts.new((r * math.cos(a), r * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si*sides+vi; b = si*sides+(vi+1)%sides
            c = (si+1)*sides+(vi+1)%sides; d = (si+1)*sides+vi
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_beach_rock(name, loc, base_r=1.0):
    """Organic rounded beach rock."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    u_segs = 14; v_segs = 10
    for vi in range(v_segs + 1):
        phi = vi / v_segs * math.pi
        for ui in range(u_segs):
            theta = ui / u_segs * math.pi * 2
            r = base_r * (1.0 + math.sin(phi * 3 + theta * 2) * 0.12
                           + rng.uniform(-0.06, 0.08))
            rz = r * 0.65  # flatten vertically
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = rz * math.cos(phi)
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for vi in range(v_segs):
        for ui in range(u_segs):
            a = vi * u_segs + ui; b = vi * u_segs + (ui+1)%u_segs
            c = (vi+1) * u_segs + (ui+1)%u_segs; d = (vi+1) * u_segs + ui
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler.z = rng.uniform(0, math.pi * 2)
    ob.name = ob.data.name = name
    return ob

def build_tidal_pool(name, loc, radius=1.6):
    """Rock-rimmed tidal pool."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 20
    for i in range(segs):
        a = i / segs * math.pi * 2
        r = radius * (1.0 + math.sin(a * 5 + rng.uniform(0,1)) * 0.12)
        bm.verts.new((r * math.cos(a), r * math.sin(a), 0))
    center = bm.verts.new((0, 0, -0.25))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        try: bm.faces.new([bm.verts[i], bm.verts[(i+1)%segs], center])
        except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_palm_trunk_geo(name, loc, height=7.0, lean_end=(0.8, 0.5)):
    """Curved palm trunk, custom vertex geometry."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides = 8; segs = 22
    for si in range(segs + 1):
        t = si / segs; z = t * height
        r = 0.20 + (1.0 - t) * 0.08
        lx = math.sin(t * math.pi * 0.85) * lean_end[0]
        ly = math.sin(t * math.pi * 0.70) * lean_end[1]
        for vi in range(sides):
            a = vi / sides * math.pi * 2
            # Ring-node bump pattern
            r_node = r * (1.0 + math.sin(z * 3.5) * 0.04)
            bm.verts.new((lx + r_node * math.cos(a),
                           ly + r_node * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si*sides+vi; b = si*sides+(vi+1)%sides
            c = (si+1)*sides+(vi+1)%sides; d = (si+1)*sides+vi
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

# ─────────────────────────────────────────────────────────────────────────────
# SCENE ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────
clear_scene()
rng = random.Random(100101)

col_root   = new_col("IsleTrial_TutorialIsle")
col_terr   = new_col("TutorialIsle_Terrain")
col_trees  = new_col("TutorialIsle_PalmTrees")
col_rocks  = new_col("TutorialIsle_Rocks")
col_dock   = new_col("TutorialIsle_Dock")
col_detail = new_col("TutorialIsle_Details")
col_lights = new_col("TutorialIsle_Lighting")

mat_grass   = build_grass_mat()
mat_sand    = build_sand_mat()
mat_dock_wd = build_dock_wood_mat()
mat_old_wd  = build_old_wood_mat()
mat_rock    = build_rock_mat()
mat_palm_tr = build_palm_trunk_mat()
mat_palm_lf = build_palm_leaf_mat()
mat_pool    = build_tidal_pool_mat()

# ── 1. TERRAIN ─────────────────────────────────────────────────────────────────
terrain = build_tutorial_terrain("TutorialIsle_Terrain")
assign_mat(terrain, mat_grass); smart_uv(terrain, angle=45)
link(col_terr, terrain)

sand = build_sand_ring("TutorialIsle_BeachSand")
assign_mat(sand, mat_sand); smart_uv(sand)
link(col_terr, sand)
print("[TutorialIsle] Terrain + beach created.")

# ── 2. WOODEN DOCK ─────────────────────────────────────────────────────────────
dock_platform = build_dock_platform("TutorialIsle_Dock_Platform", (0, -30, 1.05))
assign_mat(dock_platform, mat_dock_wd); smart_uv(dock_platform)
link(col_dock, dock_platform)

# Support piles (8 pairs along dock length)
pile_count = 0
for pi_i in range(8):
    pz = -23 - pi_i * 2.5
    for side in (-1, 1):
        pile = build_dock_pile(f"TutorialIsle_Dock_Pile_{pile_count+1:02d}",
                                 (side * 2.3, pz, 0.0))
        assign_mat(pile, mat_old_wd); smart_uv(pile)
        link(col_dock, pile)
        pile_count += 1

# Rope railings (4 curves)
for side in (-1, 1):
    for rope_h in [0.7, 1.15]:
        rc = bpy.data.curves.new(f"DockRope_{side}_{int(rope_h*100)}", type='CURVE')
        rc.dimensions = '3D'
        rs = rc.splines.new('BEZIER')
        rs.bezier_points.add(1)
        rs.bezier_points[0].co = (side*3.25, -22, 1.0+rope_h)
        rs.bezier_points[0].handle_left_type = rs.bezier_points[0].handle_right_type = 'AUTO'
        rs.bezier_points[1].co = (side*3.25, -41, 1.0+rope_h)
        rs.bezier_points[1].handle_left_type = rs.bezier_points[1].handle_right_type = 'AUTO'
        rc.bevel_depth = 0.022; rc.bevel_resolution = 4
        rope_obj = bpy.data.objects.new(f"TutorialIsle_Dock_Rope_{side}_{int(rope_h*100)}", rc)
        bpy.context.scene.collection.objects.link(rope_obj)
        assign_mat(rope_obj, mat_old_wd)
        link(col_dock, rope_obj)

# Mooring bollard
bollard = build_dock_pile("TutorialIsle_Dock_Bollard", (2.6, -40, 1.45),
                            height=0.9, radius=0.24)
assign_mat(bollard, mat_old_wd); smart_uv(bollard)
link(col_dock, bollard)
print("[TutorialIsle] Dock created.")

# ── 3. PALM TREES (12) ─────────────────────────────────────────────────────────
palm_spots = [
    (12,8,8.5), (-10,12,7.5), (18,-5,5.5), (-15,5,7.0),
    (8,16,9.5), (-6,-14,5.0), (20,12,3.0), (-18,-8,4.5),
    (14,-16,6.5), (-12,18,8.5), (6,-20,5.0), (-20,14,4.0)
]
for i, (px, py, pz) in enumerate(palm_spots):
    ht = 5.5 + rng.uniform(0, 4.0)
    lean_x = rng.uniform(-0.8, 0.8); lean_y = rng.uniform(-0.6, 0.6)

    trunk = build_palm_trunk_geo(f"TutorialIsle_PalmTrunk_{i+1:02d}",
                                   (px, py, pz), ht, (lean_x, lean_y))
    assign_mat(trunk, mat_palm_tr); smart_uv(trunk)
    link(col_trees, trunk)

    # 5-7 fan leaves
    top_x = px + lean_x; top_y = py + lean_y; top_z = pz + ht
    n_leaves = rng.randint(5, 7)
    for li in range(n_leaves):
        leaf_angle = li / n_leaves * math.pi * 2 + rng.uniform(-0.2, 0.2)
        leaf_len = 3.0 + rng.uniform(-0.4, 1.8)
        # Leaf as bezier curve
        lc = bpy.data.curves.new(f"LeafCurve_{i}_{li}", type='CURVE')
        lc.dimensions = '3D'
        ls = lc.splines.new('BEZIER')
        ls.bezier_points.add(2)
        leaf_pts = [
            (top_x, top_y, top_z),
            (top_x + math.cos(leaf_angle)*leaf_len*0.5,
             top_y + math.sin(leaf_angle)*leaf_len*0.5,
             top_z + 0.6),
            (top_x + math.cos(leaf_angle)*leaf_len,
             top_y + math.sin(leaf_angle)*leaf_len,
             top_z - 1.5)
        ]
        for pi2, (lpx, lpy, lpz) in enumerate(leaf_pts):
            bp = ls.bezier_points[pi2]
            bp.co = (lpx, lpy, lpz)
            bp.handle_left_type = bp.handle_right_type = 'AUTO'
        lc.bevel_depth = 0.038; lc.extrude = 0.24
        leaf_obj = bpy.data.objects.new(f"TutorialIsle_PalmLeaf_{i+1:02d}_{li+1:02d}", lc)
        bpy.context.scene.collection.objects.link(leaf_obj)
        assign_mat(leaf_obj, mat_palm_lf)
        link(col_trees, leaf_obj)
print(f"[TutorialIsle] {len(palm_spots)} palm trees + leaves created.")

# ── 4. BEACH ROCKS ─────────────────────────────────────────────────────────────
rock_spots = [
    (22, 5, 0, 1.0), (24, 8, 0, 0.7), (23, 6.5, 0, 0.55),
    (-22,-4, 0, 0.9), (-24,-2, 0, 0.65), (18,-18, 0, 1.1),
    (-16,-20, 0, 0.8), (-5, 28, 0, 1.3)
]
for i, (rx, ry, rz, rr) in enumerate(rock_spots):
    rock = build_beach_rock(f"TutorialIsle_Rock_{i+1:02d}",
                              (rx, ry, rz + rr * 0.3), base_r=rr)
    rock.scale.z = rng.uniform(0.55, 0.8)
    assign_mat(rock, mat_rock); smart_uv(rock)
    link(col_rocks, rock)

# ── 5. TIDAL POOLS ─────────────────────────────────────────────────────────────
pool_locs = [(24, 3, 0.05), (-23, 6, 0.05), (20, 18, 0.05)]
for i, ploc in enumerate(pool_locs):
    pool = build_tidal_pool(f"TutorialIsle_TidalPool_{i+1:02d}",
                               ploc, radius=1.5 + rng.uniform(-0.3, 0.6))
    assign_mat(pool, mat_pool); smart_uv(pool)
    link(col_detail, pool)

# ── 6. VIEWPOINT BOULDER CLIFF ────────────────────────────────────────────────
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=4.5, location=(0, 22, 6.5))
boulder = bpy.context.active_object; boulder.name = "TutorialIsle_BoulderCliff"
boulder.scale = (1.5, 0.9, 1.2)
bm = bmesh.new(); bm.from_mesh(boulder.data)
for v in bm.verts:
    v.co.x += math.sin(v.co.z * 1.5 + v.co.y * 0.8) * 0.15
    v.co.y += math.cos(v.co.z * 1.2 + v.co.x * 0.6) * 0.12
    v.co.z += rng.uniform(-0.08, 0.12)
bm.to_mesh(boulder.data); bm.free()
assign_mat(boulder, mat_rock); smart_uv(boulder)
link(col_rocks, boulder)

# ── 7. TALL GRASS PATCHES ─────────────────────────────────────────────────────
grass_locs = [(8,12,3.5),(-10,5,4.0),(15,-5,3.0),(-8,18,5.5),(12,20,4.5),(-5,-8,2.5)]
for i, (gx, gy, gz) in enumerate(grass_locs):
    gsize = 3.0 + rng.uniform(0, 3.5)
    me_g = bpy.data.meshes.new(f"GrassPatch_{i+1:02d}")
    ob_g = bpy.data.objects.new(f"TutorialIsle_Grass_Patch_{i+1:02d}", me_g)
    bm_g = bmesh.new()
    for bi in range(12):
        ba = bi / 12 * math.pi * 2; br = rng.uniform(0.3, gsize * 0.5)
        bx = gx + math.cos(ba) * br; by = gy + math.sin(ba) * br
        bh = 0.8 + rng.uniform(0, 1.2)
        bm_g.verts.new((bx - 0.05, by, gz)); bm_g.verts.new((bx + 0.05, by, gz))
        bm_g.verts.new((bx + rng.uniform(-0.08,0.08), by + rng.uniform(-0.05,0.05), gz + bh))
    bm_g.verts.ensure_lookup_table()
    for bi in range(12):
        a = bi*3; b = a+1; c = a+2
        try: bm_g.faces.new([bm_g.verts[a], bm_g.verts[b], bm_g.verts[c]])
        except: pass
    bm_g.to_mesh(me_g); bm_g.free()
    bpy.context.scene.collection.objects.link(ob_g)
    assign_mat(ob_g, mat_grass); smart_uv(ob_g)
    link(col_detail, ob_g)

# ── 8. SUN AND FILL LIGHTS ────────────────────────────────────────────────────
sun_d = bpy.data.lights.new("TutorialIsle_Sun", type='SUN')
sun_d.energy = 5.5; sun_d.color = (1.0, 0.93, 0.78); sun_d.angle = math.radians(2.5)
sun_o = bpy.data.objects.new("TutorialIsle_Sun", sun_d)
sun_o.location = (20, -20, 40)
sun_o.rotation_euler = (math.radians(52), 0, math.radians(-32))
bpy.context.scene.collection.objects.link(sun_o); link(col_lights, sun_o)

fill_d = bpy.data.lights.new("TutorialIsle_FillLight", type='SUN')
fill_d.energy = 1.2; fill_d.color = (0.6, 0.75, 1.0)
fill_o = bpy.data.objects.new("TutorialIsle_FillLight", fill_d)
fill_o.location = (-30, 20, 30)
fill_o.rotation_euler = (math.radians(60), 0, math.radians(140))
bpy.context.scene.collection.objects.link(fill_o); link(col_lights, fill_o)

# Root
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
root = bpy.context.active_object; root.name = "TutorialIsle_ROOT"
link(col_root, root)

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("TUTORIAL ISLE — FULL QUALITY BUILD COMPLETE")
print("="*65)
print("  Terrain    : 48×48 gentle warm hills, beach sand ring")
print(f"  Palm trees : {len(palm_spots)} (curved trunks + bezier leaves)")
print(f"  Beach rocks: {len(rock_spots)}")
print("  Tidal pools: 3")
print("  Dock       : planked platform + 16 piles + 4 ropes + bollard")
print("  Viewpoint boulder cliff: 1")
print("  Grass patches: 6")
print("  Lighting   : warm directional sun + cool sky fill")
print("  Materials  : 8 full node trees + [UNITY] image slots")
print("  UV         : smart_project on all mesh objects")
print(f"\n  Unity: warm golden VolumeProfile + ambient shore audio")
print(f"  Dock = player start + boat spawn + first NPC (fisherman)")
print(f"  North shore: place skeleton from Script 37 for first 'wow'")
print("="*65)
