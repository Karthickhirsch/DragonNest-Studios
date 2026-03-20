"""
IsleTrial — Blender 4.x Python Script
Script 33: Sunken Temple Island  [FULL QUALITY REBUILD]
========================================================
Objects created (28 total):
  SunkenTemple_IsleBase           — rocky island base terrain
  SunkenTemple_FloorPlate_Above   — main temple floor above water
  SunkenTemple_Column_Above_01..05— 5 standing columns above water
  SunkenTemple_Entablature_Partial— broken horizontal beam
  SunkenTemple_BrokenTop_01..02   — fallen column tops
  SunkenTemple_Column_Sub_01..07  — 7 submerged leaning columns
  SunkenTemple_SubFloor           — cracked submerged floor slab
  SunkenTemple_AlgaeGrowth_01..04 — 4 algae/coral patches on floor
  SunkenTemple_ChamberOpening     — dark void chamber opening
  SunkenTemple_SubRuneFloor       — glowing glyph mosaic underwater
  SunkenTemple_VaultEntry         — sunken doorway arch
  SunkenTemple_ScatteredDebris_*  — 6 scattered stone blocks
  SunkenTemple_WaterSurface       — translucent water plane
  SunkenTemple_SeaweedStrand_01..08— 8 bezier seaweed curve strands
  SunkenTemple_CausticsPlane      — translucent caustic light plane

Dual-path PBR + [UNITY] image slots + smart UV on all meshes.
Run in Blender 4.x: Scripting tab → Run Script (Alt+P)
"""

import bpy, bmesh, math, random
from mathutils import Vector

rng = random.Random(310031)

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

def build_isle_rock_mat():
    """Rocky island base — Musgrave + Noise blend, weathered."""
    mat = bpy.data.materials.new("Mat_ST_IsleRock")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (950, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Roughness'].default_value = 0.88
    mus  = ns.new('ShaderNodeTexMusgrave'); mus.location = (-550, 200)
    mus.inputs['Scale'].default_value = 6.5; mus.inputs['Detail'].default_value = 8.0
    cr1  = ns.new('ShaderNodeValToRGB'); cr1.location = (-250, 200)
    cr1.color_ramp.elements[0].color = (0.18, 0.16, 0.14, 1)
    cr1.color_ramp.elements[1].color = (0.42, 0.40, 0.36, 1)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-550, -50)
    noise.inputs['Scale'].default_value = 38.0; noise.inputs['Detail'].default_value = 8.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-250, -50)
    cr2.color_ramp.elements[0].color = (0.25, 0.22, 0.18, 1)
    cr2.color_ramp.elements[1].color = (0.48, 0.44, 0.38, 1)
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'
    mix.location = (0, 80); mix.inputs['Fac'].default_value = 0.6
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (380, 220)
    bmp.inputs['Strength'].default_value = 1.4
    img_a = img_slot(ns, "[UNITY] IsleRock_Albedo", -590, -350)
    img_n = img_slot(ns, "[UNITY] IsleRock_Normal", -590, -550)
    fmix  = ns.new('ShaderNodeMixRGB'); fmix.location = (490, 0); fmix.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr1.inputs['Fac'])
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

def build_sandstone_mat():
    """Carved sandstone columns — warm tan, wave-grain."""
    mat = bpy.data.materials.new("Mat_ST_Sandstone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (950, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Roughness'].default_value = 0.85
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-550, 200)
    wave.wave_type = 'RINGS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value      = 8.0
    wave.inputs['Distortion'].default_value = 3.5
    wave.inputs['Detail'].default_value     = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-250, 200)
    cr.color_ramp.elements[0].color = (0.42, 0.36, 0.24, 1)
    cr.color_ramp.elements[1].color = (0.68, 0.58, 0.40, 1)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-550, -80)
    noise.inputs['Scale'].default_value = 45.0; noise.inputs['Detail'].default_value = 6.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-250, -80)
    cr2.color_ramp.elements[0].color = (0.30, 0.26, 0.18, 1)
    cr2.color_ramp.elements[1].color = (0.55, 0.47, 0.32, 1)
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'
    mix.location = (0, 80); mix.inputs['Fac'].default_value = 0.55
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (380, 230)
    bmp.inputs['Strength'].default_value = 1.2
    img_a = img_slot(ns, "[UNITY] Sandstone_Albedo", -590, -350)
    img_n = img_slot(ns, "[UNITY] Sandstone_Normal", -590, -550)
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

def build_submerged_stone_mat():
    """Submerged stone — dark, algae-stained, Voronoi pitting."""
    mat = bpy.data.materials.new("Mat_ST_SubStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (950, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Roughness'].default_value = 0.78
    vor  = ns.new('ShaderNodeTexVoronoi'); vor.location = (-580, 200)
    vor.inputs['Scale'].default_value = 14.0
    cr1  = ns.new('ShaderNodeValToRGB'); cr1.location = (-300, 200)
    cr1.color_ramp.elements[0].color = (0.08, 0.10, 0.12, 1)
    cr1.color_ramp.elements[1].color = (0.24, 0.28, 0.32, 1)
    # Algae overlay (Noise with green tint)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-580, -80)
    noise.inputs['Scale'].default_value = 20.0; noise.inputs['Detail'].default_value = 6.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-280, -80)
    cr2.color_ramp.elements[0].position = 0.4; cr2.color_ramp.elements[0].color = (0.08,0.10,0.12,1)
    cr2.color_ramp.elements[1].position = 0.7; cr2.color_ramp.elements[1].color = (0.10,0.22,0.09,1)
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'MIX'
    mix.location = (0, 80); mix.inputs['Fac'].default_value = 0.5
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (380, 220)
    bmp.inputs['Strength'].default_value = 0.8
    img_a = img_slot(ns, "[UNITY] SubStone_Albedo", -610, -350)
    img_n = img_slot(ns, "[UNITY] SubStone_Normal", -610, -550)
    fmix  = ns.new('ShaderNodeMixRGB'); fmix.location = (500, 0); fmix.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'],  cr1.inputs['Fac'])
    lk.new(noise.outputs['Fac'],     cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],     mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],     mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],     fmix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],   fmix.inputs['Color2'])
    lk.new(vor.outputs['Distance'],  bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],    bsdf.inputs['Normal'])
    lk.new(fmix.outputs['Color'],    bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],     out.inputs['Surface'])
    return mat

def build_rune_glow_mat():
    """Submerged glowing rune mosaic — teal-green emission."""
    mat = bpy.data.materials.new("Mat_ST_GlowRune")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Base Color'].default_value = (0.15, 0.50, 0.38, 1)
    bsdf.inputs['Roughness'].default_value  = 0.30
    emit = ns.new('ShaderNodeEmission'); emit.location = (250, 200)
    emit.inputs['Color'].default_value    = (0.10, 0.85, 0.55, 1)
    emit.inputs['Strength'].default_value = 5.0
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-450, 200)
    noise.inputs['Scale'].default_value = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-150, 200)
    cr.color_ramp.elements[0].position = 0.4; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (1,1,1,1)
    mix_s= ns.new('ShaderNodeMixShader'); mix_s.location = (730, 100)
    img_e = img_slot(ns, "[UNITY] Rune_Emission", -490, -350)
    lk.new(noise.outputs['Fac'],       cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],        mix_s.inputs['Fac'])
    lk.new(bsdf.outputs['BSDF'],       mix_s.inputs[1])
    lk.new(emit.outputs['Emission'],   mix_s.inputs[2])
    lk.new(mix_s.outputs['Shader'],    out.inputs['Surface'])
    return mat

def build_water_surface_mat():
    """Water surface — translucent, Wave distorted."""
    mat = bpy.data.materials.new("Mat_ST_WaterSurface")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Base Color'].default_value        = (0.08, 0.22, 0.32, 1)
    bsdf.inputs['Roughness'].default_value         = 0.04
    bsdf.inputs['Transmission Weight'].default_value = 0.90
    bsdf.inputs['IOR'].default_value               = 1.33
    bsdf.inputs['Alpha'].default_value             = 0.42
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-550, 150)
    wave.wave_type = 'RINGS'; wave.bands_direction = 'DIAGONAL'
    wave.inputs['Scale'].default_value      = 2.0
    wave.inputs['Distortion'].default_value = 4.0
    wave.inputs['Detail'].default_value     = 12.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (350, 200)
    bmp.inputs['Strength'].default_value = 0.45
    img_n = img_slot(ns, "[UNITY] Water_Normal", -580, -350)
    lk.new(wave.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_algae_mat():
    """Algae/coral growth on submerged stone."""
    mat = bpy.data.materials.new("Mat_ST_Algae")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Roughness'].default_value = 0.88
    bsdf.inputs['Subsurface Weight'].default_value = 0.08
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-450, 150)
    noise.inputs['Scale'].default_value  = 22.0
    noise.inputs['Detail'].default_value = 8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-150, 150)
    cr.color_ramp.elements[0].color = (0.06, 0.18, 0.06, 1)
    cr.color_ramp.elements[1].color = (0.20, 0.45, 0.15, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (250, 200)
    bmp.inputs['Strength'].default_value = 0.6
    img_a = img_slot(ns, "[UNITY] Algae_Albedo", -500, -300)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (360, 0); mix.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],   bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_dark_void_mat():
    """Chamber void — pure near-black."""
    mat = bpy.data.materials.new("Mat_ST_DarkVoid")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (600, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (350, 0)
    bsdf.inputs['Base Color'].default_value = (0.01, 0.01, 0.02, 1)
    bsdf.inputs['Roughness'].default_value  = 0.98
    lk.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_seaweed_mat():
    """Seaweed strands — translucent green."""
    mat = bpy.data.materials.new("Mat_ST_Seaweed")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Base Color'].default_value  = (0.05, 0.38, 0.12, 1)
    bsdf.inputs['Roughness'].default_value   = 0.72
    bsdf.inputs['Alpha'].default_value       = 0.82
    bsdf.inputs['Subsurface Weight'].default_value = 0.12
    img_a = img_slot(ns, "[UNITY] Seaweed_Albedo", -450, -200)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (250, 0)
    mix.inputs['Fac'].default_value = 0.0
    mix.inputs['Color1'].default_value = (0.05, 0.38, 0.12, 1)
    lk.new(img_a.outputs['Color'], mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_caustic_mat():
    """Caustic light pattern plane under water."""
    mat = bpy.data.materials.new("Mat_ST_Caustic")
    mat.use_nodes = True
    mat.blend_method = 'ADD'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (700, 0)
    emit = ns.new('ShaderNodeEmission'); emit.location = (400, 0)
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-300, 100)
    wave.wave_type = 'RINGS'; wave.bands_direction = 'DIAGONAL'
    wave.inputs['Scale'].default_value      = 5.0
    wave.inputs['Distortion'].default_value = 8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-50, 100)
    cr.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1)
    cr.color_ramp.elements[1].color = (0.6, 0.85, 0.9, 1)
    lk.new(wave.outputs['Fac'],       cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],       emit.inputs['Color'])
    emit.inputs['Strength'].default_value = 1.2
    lk.new(emit.outputs['Emission'],  out.inputs['Surface'])
    return mat

print("[SunkenTemple] All materials built.")

# ─────────────────────────────────────────────────────────────────────────────
# GEOMETRY BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def build_isle_base(name, size=60.0, grid=40):
    """Low rocky island with hollowed centre for temple."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    for gi in range(grid + 1):
        for gj in range(grid + 1):
            x = (gi / grid - 0.5) * size
            y = (gj / grid - 0.5) * size
            nx, ny = x / (size * 0.5), y / (size * 0.5)
            dist = math.sqrt(nx*nx + ny*ny)
            h = max(0.0, 1.0 - dist * 1.35) ** 1.4 * 5.5
            # Depression at centre (temple sits here)
            h -= max(0.0, 1.0 - dist * 5.2) * 2.0
            # Rocky shore
            h += max(0.0, 0.7 - max(0.0, dist - 0.72) * 4.0) * 0.5
            n = (math.sin(nx*9+ny*7)*0.3 + math.sin(nx*15-ny*12)*0.15)
            bm.verts.new((x, y, h + n * 0.4))
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
    return ob

def build_temple_floor_plate(name, loc, w=18.0, d=12.0, sink_south=True):
    """Temple floor slab — cracks, slight southward sinking."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    nx, ny = 20, 14
    for j in range(ny + 1):
        ty = j / ny
        for i in range(nx + 1):
            tx = i / nx
            x = (tx - 0.5) * w
            y = (ty - 0.5) * d
            z = 0.0
            if sink_south and ty > 0.5:
                z -= (ty - 0.5) * 5.0  # south half sinks
            # Crack displacement
            z += math.sin(x * 3.2 + y * 2.8) * 0.06
            z += math.sin(x * 8.5 - y * 6.2) * 0.03
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
    sol = ob.modifiers.new("Solidify", 'SOLIDIFY'); sol.thickness = 0.5
    return ob

def build_column(name, loc, height=5.5, radius=0.55, lean=(0.0, 0.0),
                  fluted=True, submerged=False):
    """Temple column — fluted or plain, with capital."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides = 10; segs = 22
    for si in range(segs + 1):
        t = si / segs; z = t * height
        r = radius * (1.0 - abs(t - 0.5) * 0.05)  # entasis (slight bulge)
        # Capital flare at top
        if t > 0.85:
            r *= 1.0 + (t - 0.85) / 0.15 * 0.45
        # Base plinth flare
        if t < 0.08:
            r *= 1.0 + (0.08 - t) / 0.08 * 0.35
        for vi in range(sides):
            a = vi / sides * math.pi * 2
            rf = r * (1.0 + (math.sin(a * sides * 0.5) * 0.04 if fluted else 0))
            lx = lean[0] * t; ly = lean[1] * t
            erosion = math.sin(z * 2.5 + vi * 0.8) * (0.02 if submerged else 0.01)
            bm.verts.new((lx + rf * math.cos(a) + erosion,
                           ly + rf * math.sin(a) + erosion, z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si*sides+vi; b = si*sides+(vi+1)%sides
            c = (si+1)*sides+(vi+1)%sides; d = (si+1)*sides+vi
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    # Caps
    try: bm.faces.new([bm.verts[v] for v in range(sides)][::-1])
    except: pass
    try: bm.faces.new([bm.verts[segs*sides+v] for v in range(sides)])
    except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_entablature(name, loc, length=12.0, crack_side=1):
    """Horizontal beam/lintel above columns, partially broken."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    nx = 18; w = 0.7; h = 0.68
    for i in range(nx + 1):
        t = i / nx
        x = (t - 0.5) * length
        # Crack on one side
        crack_drop = max(0.0, (t - 0.5) * crack_side) ** 2 * 2.5
        for cx, cz in [(-w/2, 0), (w/2, 0), (w/2, h), (-w/2, h)]:
            bm.verts.new((x, cx, cz - crack_drop + math.sin(x * 1.8) * 0.04))
    bm.verts.ensure_lookup_table()
    for i in range(nx):
        for ci in range(4):
            a = i*4+ci; b = i*4+(ci+1)%4
            c = (i+1)*4+(ci+1)%4; d = (i+1)*4+ci
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_vault_arch(name, loc, major_r=3.0, minor_r=0.5):
    """Sunken vault doorway arch."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    outer_segs = 20; tube_segs = 8
    for os in range(outer_segs + 1):
        t = os / outer_segs
        a_outer = t * math.pi  # semicircle
        for ts in range(tube_segs):
            a_inner = ts / tube_segs * math.pi * 2
            x = (major_r + minor_r * math.cos(a_inner)) * math.cos(a_outer)
            z = (major_r + minor_r * math.cos(a_inner)) * math.sin(a_outer)
            y = minor_r * math.sin(a_inner)
            # Worn erosion
            x += math.sin(a_outer * 5 + a_inner) * 0.03
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for os in range(outer_segs):
        for ts in range(tube_segs):
            a = os*tube_segs+ts; b = os*tube_segs+(ts+1)%tube_segs
            c = (os+1)*tube_segs+(ts+1)%tube_segs; d = (os+1)*tube_segs+ts
            try: bm.faces.new([bm.verts[a],bm.verts[b],bm.verts[c],bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_algae_patch(name, loc, size=3.0):
    """Irregular algae blob on submerged floor."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 16
    for i in range(segs):
        a = i / segs * math.pi * 2
        r = size * (0.7 + math.sin(a * 4 + rng.uniform(0,1)) * 0.3)
        bm.verts.new((r * math.cos(a), r * math.sin(a), 0))
    center = bm.verts.new((0, 0, -0.05))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        try: bm.faces.new([bm.verts[i], bm.verts[(i+1)%segs], center])
        except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler.z = rng.uniform(0, math.pi*2)
    ob.name = ob.data.name = name
    return ob

def build_debris_block(name, loc, size=1.0):
    """Scattered stone block debris."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    hw = size * rng.uniform(0.4, 0.8); hd = size * rng.uniform(0.3, 0.6); hh = size * rng.uniform(0.2, 0.5)
    for cx, cy, cz in [(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),
                        (-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]:
        bm.verts.new((cx+rng.uniform(-0.04,0.04)*size,
                       cy+rng.uniform(-0.04,0.04)*size,
                       cz+rng.uniform(-0.04,0.04)*size))
    bm.verts.ensure_lookup_table()
    faces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(0,3,7,4),(1,2,6,5)]
    for f in faces:
        try: bm.faces.new([bm.verts[v] for v in f])
        except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (rng.uniform(-0.4,0.4), rng.uniform(-0.4,0.4), rng.uniform(0, math.pi*2))
    ob.name = ob.data.name = name
    return ob

# ─────────────────────────────────────────────────────────────────────────────
# SCENE ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────
clear_scene()
rng = random.Random(310031)

col_root   = new_col("IsleTrial_SunkenTemple")
col_isle   = new_col("SunkenTemple_Island")
col_above  = new_col("SunkenTemple_AboveWater")
col_below  = new_col("SunkenTemple_Submerged")
col_water  = new_col("SunkenTemple_Water")
col_detail = new_col("SunkenTemple_Details")
col_lights = new_col("SunkenTemple_Lighting")

mat_isle_rock = build_isle_rock_mat()
mat_sandstone = build_sandstone_mat()
mat_sub_stone = build_submerged_stone_mat()
mat_rune_glow = build_rune_glow_mat()
mat_water     = build_water_surface_mat()
mat_algae     = build_algae_mat()
mat_void      = build_dark_void_mat()
mat_seaweed   = build_seaweed_mat()
mat_caustic   = build_caustic_mat()

# ── 1. ISLAND BASE ────────────────────────────────────────────────────────────
isle = build_isle_base("SunkenTemple_IsleBase")
assign_mat(isle, mat_isle_rock); smart_uv(isle)
link(col_isle, isle)
print("[SunkenTemple] Island base created.")

# ── 2. TEMPLE FLOOR ABOVE WATER ───────────────────────────────────────────────
floor_above = build_temple_floor_plate("SunkenTemple_FloorPlate_Above", (0, 2, 0.25))
assign_mat(floor_above, mat_sandstone); smart_uv(floor_above)
link(col_above, floor_above)

# ── 3. ABOVE-WATER COLUMNS ────────────────────────────────────────────────────
above_col_cfg = [
    ((-6, 5, 0.5), 5.5), ((0, 5, 0.5), 5.8), ((6, 5, 0.5), 5.2),
    ((-6, 3, 0.5), 4.8), ((6, 3, 0.5), 5.0),
]
for i, (cloc, ch) in enumerate(above_col_cfg):
    col_obj = build_column(f"SunkenTemple_Column_Above_{i+1:02d}",
                             cloc, ch, fluted=True)
    assign_mat(col_obj, mat_sandstone); smart_uv(col_obj)
    link(col_above, col_obj)

# Broken column tops (fallen)
for bi, (floc, frot) in enumerate([
    ((-6, 5, 5.8), (-0.3, 0.5, 0.2)),
    (( 0, 5, 6.1), (0.2, -0.3, 0.15)),
]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.55, depth=1.5,
                                         location=(floc[0], floc[1]+rng.uniform(-1,1), floc[2]-0.3))
    broken = bpy.context.active_object
    broken.name = f"SunkenTemple_BrokenTop_{bi+1:02d}"
    broken.rotation_euler = frot
    assign_mat(broken, mat_sandstone); smart_uv(broken)
    link(col_above, broken)

# Entablature
entab = build_entablature("SunkenTemple_Entablature_Partial", (-3, 4.5, 6.5))
assign_mat(entab, mat_sandstone); smart_uv(entab)
link(col_above, entab)
print("[SunkenTemple] Above-water structure created.")

# ── 4. SUBMERGED COLUMNS ──────────────────────────────────────────────────────
sub_col_cfg = [
    ((-6,-2,-1), 4.5, (0.06, 0.04)), ((-6,-5,-3), 5.0, (-0.08, 0.05)),
    ((-6,-8,-5), 4.2, (0.12, -0.06)), ((0,-2,-1), 4.8, (0.04, -0.04)),
    ((0,-5,-3),  5.2, (-0.06, 0.08)), ((6,-2,-1),  4.5, (0.05, 0.06)),
    ((6,-5,-3),  5.0, (0.09, -0.05)),
]
for i, (sloc, sh, slean) in enumerate(sub_col_cfg):
    scol = build_column(f"SunkenTemple_Column_Sub_{i+1:02d}",
                          sloc, sh, radius=0.52,
                          lean=slean, submerged=True)
    assign_mat(scol, mat_sub_stone); smart_uv(scol)
    link(col_below, scol)

# ── 5. SUBMERGED FLOOR ────────────────────────────────────────────────────────
sub_floor = build_temple_floor_plate("SunkenTemple_SubFloor", (0, -6, -3.5), sink_south=False)
assign_mat(sub_floor, mat_algae); smart_uv(sub_floor)
link(col_below, sub_floor)

# Algae patches on subfloor
algae_locs = [(-4, -4, -3.2), (3, -6, -3.2), (-2, -9, -3.1), (5, -3, -3.2)]
for i, aloc in enumerate(algae_locs):
    ap = build_algae_patch(f"SunkenTemple_AlgaeGrowth_{i+1:02d}",
                             aloc, size=2.0+rng.uniform(0, 1.5))
    assign_mat(ap, mat_algae); smart_uv(ap)
    link(col_below, ap)

# ── 6. DARK CHAMBER OPENING ───────────────────────────────────────────────────
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=2.8, depth=0.4, location=(0,-8,-4))
chamber = bpy.context.active_object; chamber.name = "SunkenTemple_ChamberOpening"
assign_mat(chamber, mat_void); smart_uv(chamber)
link(col_below, chamber)

# ── 7. GLOWING RUNE FLOOR ─────────────────────────────────────────────────────
bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0,-5,-3.15))
rune_floor = bpy.context.active_object; rune_floor.name = "SunkenTemple_SubRuneFloor"
assign_mat(rune_floor, mat_rune_glow); smart_uv(rune_floor)
link(col_below, rune_floor)
# Rune glow light
rl = bpy.data.lights.new("SubRune_GlowLight", type='POINT')
rl.energy = 2200; rl.color = (0.1, 0.85, 0.55); rl.shadow_soft_size = 2.0
rlo = bpy.data.objects.new("SubRune_GlowLight", rl)
rlo.location = (0, -5, -1.5); bpy.context.scene.collection.objects.link(rlo)
link(col_lights, rlo)

# ── 8. VAULT ENTRY ARCH ────────────────────────────────────────────────────────
arch = build_vault_arch("SunkenTemple_VaultEntry", (0, -8.5, -4.0))
assign_mat(arch, mat_sub_stone); smart_uv(arch)
link(col_below, arch)

# ── 9. SCATTERED STONE DEBRIS ─────────────────────────────────────────────────
debris_locs = [
    (-8, 2, 0.3), (8, 4, 0.2), (-10, -4, -0.5), (10, -2, -0.4),
    (-4, -12, -2.0), (5, -11, -2.5)
]
for i, dloc in enumerate(debris_locs):
    db = build_debris_block(f"SunkenTemple_ScatteredDebris_{i+1:02d}", dloc,
                              size=1.2 + rng.uniform(-0.3, 0.8))
    assign_mat(db, mat_sub_stone if dloc[2] < 0 else mat_sandstone)
    smart_uv(db); link(col_detail, db)

# ── 10. WATER SURFACE ────────────────────────────────────────────────────────
bpy.ops.mesh.primitive_plane_add(size=50, location=(0,-8, 0.04))
water = bpy.context.active_object; water.name = "SunkenTemple_WaterSurface"
bm = bmesh.new(); bm.from_mesh(water.data)
for v in bm.verts:
    v.co.z += math.sin(v.co.x*1.4+v.co.y*1.1)*0.04
bm.to_mesh(water.data); bm.free()
assign_mat(water, mat_water); smart_uv(water)
link(col_water, water)

# Caustics plane (slightly below water surface)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0,-6,-0.5))
caustic = bpy.context.active_object; caustic.name = "SunkenTemple_CausticsPlane"
assign_mat(caustic, mat_caustic); smart_uv(caustic)
link(col_water, caustic)

# ── 11. SEAWEED STRANDS (bezier) ──────────────────────────────────────────────
sw_locs = [(-8,-4,-3.5),(8,-3,-3.5),(-5,-10,-3.5),(4,-12,-3.5),
            (-9,-8,-3),(7,-9,-3.2),(0,-14,-3.5),(-3,-2,-2)]
for i,(swx,swy,swz) in enumerate(sw_locs):
    swh = 3.0 + rng.uniform(0, 5.0)
    swd = bpy.data.curves.new(f"SeaweedCurve_{i+1:02d}", type='CURVE')
    swd.dimensions = '3D'
    spl = swd.splines.new('BEZIER')
    spl.bezier_points.add(2)
    pts_sw = [(swx,swy,swz),(swx+0.4,swy,swz+swh*0.4),(swx-0.3,swy+0.3,swz+swh)]
    for pi,(px,py,pz) in enumerate(pts_sw):
        bp = spl.bezier_points[pi]
        bp.co = (px,py,pz); bp.handle_left_type = bp.handle_right_type = 'AUTO'
    swd.bevel_depth = 0.04; swd.extrude = 0.12
    swo = bpy.data.objects.new(f"SunkenTemple_SeaweedStrand_{i+1:02d}", swd)
    bpy.context.scene.collection.objects.link(swo)
    assign_mat(swo, mat_seaweed)
    link(col_detail, swo)

# Root
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
root = bpy.context.active_object; root.name = "SunkenTemple_ROOT"
link(col_root, root)

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("SUNKEN TEMPLE — FULL QUALITY BUILD COMPLETE")
print("="*65)
print("  Island base   : rocky terrain, temple depression at centre")
print("  Above water   : floor plate + 5 columns + entablature + 2 broken tops")
print(f"  Submerged     : {len(sub_col_cfg)} columns + sub-floor + algae patches")
print("  Chamber void  : dark cylinder opening + vault arch")
print("  Rune floor    : glowing glyph mosaic (teal-green)")
print(f"  Debris blocks : {len(debris_locs)}")
print("  Water surface : translucent + Wave normal + caustic plane")
print(f"  Seaweed       : {len(sw_locs)} bezier strands")
print("  Materials     : 9 full node trees + [UNITY] image slots")
print("  UV            : smart_project on all mesh objects")
print(f"\n  Unity: underwater blue VolumeProfile + caustic light projector")
print(f"  The rune floor / vault arch = key story moment / puzzle gate")
print("="*65)
