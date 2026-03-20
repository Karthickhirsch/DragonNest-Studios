"""
IsleTrial — Blender 4.x Python Script
Script 30: Ember Isle — Volcanic Island  [FULL QUALITY REBUILD]
================================================================
Objects created (28 total):
  EmberIsle_VolcanoTerrain        — 64×64 subdivided plane, cone + noise sculpt
  EmberIsle_CalderaRim            — jagged lava-rim torus ring at peak
  EmberIsle_CraterLavaPool        — glowing orange lava pool in caldera
  EmberIsle_BasaltCliffFace_N/E   — two thick cliff slabs, voronoi-displaced
  EmberIsle_BasaltColumn_01..06   — 6 hexagonal basalt column pillars
  EmberIsle_ObsidianSpire_01..08  — 8 twisted obsidian glass spires
  EmberIsle_LavaVent_01..08       — 8 glowing ground-crack lava vents
  EmberIsle_LavaRiver_01..03      — 3 bezier lava river curves (+ inner glow)
  EmberIsle_CooledLavaField_01..03— 3 flat hardened lava plains
  EmberIsle_ScorchedTree_01..12   — 12 dead trees (trunk + branches)
  EmberIsle_AshPatch_01..05       — 5 ash drift planes
  EmberIsle_SulfurVentSmoke_01..04— 4 translucent cone smoke wisps
  EmberIsle_VolcanoLight          — orange point light (caldera glow)

Dual-path PBR materials + [UNITY] image texture slots + smart UV on all meshes.
Run in Blender 4.x: Scripting tab → Run Script (Alt+P)
Export: Select all in IsleTrial_EmberIsle → FBX (scale 0.01, Apply Transform ON)
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(420042)

# ─────────────────────────────────────────────────────────────────────────────
# Scene / utility helpers
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

def add_mat(obj, mat):
    obj.data.materials.append(mat)

def smart_uv(obj, angle=60):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=angle, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)

def apply_transforms(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)

def ns_lk(mat):
    mat.use_nodes = True
    return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, label, x, y):
    n = ns.new('ShaderNodeTexImage')
    n.label = n.name = label
    n.location = (x, y)
    return n

# ─────────────────────────────────────────────────────────────────────────────
# MATERIAL BUILDERS — full procedural node trees + [UNITY] image slots
# ─────────────────────────────────────────────────────────────────────────────

def build_volcanic_rock_mat():
    """Dark basalt with cracked surface detail — Musgrave + Noise blend."""
    mat = bpy.data.materials.new("Mat_Ember_VolcanicRock")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (700, 0)
    bsdf.inputs['Roughness'].default_value  = 0.92
    bsdf.inputs['Metallic'].default_value   = 0.0
    # Musgrave for large-scale rock pattern
    mus  = ns.new('ShaderNodeTexMusgrave'); mus.location = (-600, 200)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value   = 5.0
    mus.inputs['Detail'].default_value  = 8.0
    mus.inputs['Dimension'].default_value = 1.2
    cr1  = ns.new('ShaderNodeValToRGB'); cr1.location = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0;  cr1.color_ramp.elements[0].color = (0.04, 0.03, 0.02, 1)
    cr1.color_ramp.elements[1].position = 1.0;  cr1.color_ramp.elements[1].color = (0.16, 0.12, 0.09, 1)
    # Fine noise overlay for micro detail
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-600, -100)
    noise.inputs['Scale'].default_value  = 35.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.7
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-300, -100)
    cr2.color_ramp.elements[0].position = 0.35; cr2.color_ramp.elements[0].color = (0.06, 0.04, 0.03, 1)
    cr2.color_ramp.elements[1].position = 0.80; cr2.color_ramp.elements[1].color = (0.20, 0.14, 0.10, 1)
    # Mix base + detail
    mix  = ns.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.location = (50, 100)
    mix.inputs['Fac'].default_value = 0.65
    # Bump from musgrave
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (400, 250)
    bmp.inputs['Strength'].default_value = 1.6
    bmp.inputs['Distance'].default_value = 0.05
    # [UNITY] slots
    img_a = img_slot(ns, "[UNITY] EmberRock_Albedo",  -650, -350)
    img_n = img_slot(ns, "[UNITY] EmberRock_Normal",  -650, -550)
    img_r = img_slot(ns, "[UNITY] EmberRock_Roughness",-650,-750)
    mix2  = ns.new('ShaderNodeMixRGB'); mix2.location = (450, 0)
    mix2.inputs['Fac'].default_value = 0.0  # 0 = procedural, 1 = Unity maps
    lk.new(mus.outputs['Fac'],    cr1.inputs['Fac'])
    lk.new(noise.outputs['Fac'],  cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],  mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],  mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],  mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'], bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def build_lava_mat():
    """Molten lava — animated wave distortion + strong emission."""
    mat = bpy.data.materials.new("Mat_Ember_MoltenLava")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (500, 0)
    bsdf.inputs['Roughness'].default_value   = 0.18
    bsdf.inputs['Metallic'].default_value    = 0.0
    wave = ns.new('ShaderNodeTexWave');  wave.location = (-500, 150)
    wave.wave_type = 'RINGS'; wave.bands_direction = 'DIAGONAL'
    wave.inputs['Scale'].default_value       = 3.5
    wave.inputs['Distortion'].default_value  = 8.0
    wave.inputs['Detail'].default_value      = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-200, 150)
    cr.color_ramp.elements[0].position = 0.0;  cr.color_ramp.elements[0].color = (0.80, 0.08, 0.0, 1)
    cr.color_ramp.elements[1].position = 0.5;  cr.color_ramp.elements[1].color = (1.0,  0.45, 0.0, 1)
    cr.color_ramp.elements.new(1.0);            cr.color_ramp.elements[2].color = (1.0,  0.95, 0.3, 1)
    emit = ns.new('ShaderNodeEmission');  emit.location = (200, 200)
    emit.inputs['Color'].default_value    = (1.0, 0.4, 0.05, 1)
    emit.inputs['Strength'].default_value = 8.0
    add  = ns.new('ShaderNodeAddShader'); add.location = (700, 100)
    img_a = img_slot(ns, "[UNITY] Lava_Albedo",   -550, -300)
    img_e = img_slot(ns, "[UNITY] Lava_Emission", -550, -500)
    lk.new(wave.outputs['Fac'],       cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],       bsdf.inputs['Base Color'])
    lk.new(cr.outputs['Color'],       emit.inputs['Color'])
    lk.new(bsdf.outputs['BSDF'],      add.inputs[0])
    lk.new(emit.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],     out.inputs['Surface'])
    return mat

def build_cooled_lava_mat():
    """Hardened cooled lava — dark crust with ember-crack glow veins."""
    mat = bpy.data.materials.new("Mat_Ember_CooledLava")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (600, 0)
    bsdf.inputs['Roughness'].default_value  = 0.93
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-550, 150)
    noise.inputs['Scale'].default_value  = 12.0
    noise.inputs['Detail'].default_value = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-250, 150)
    cr.color_ramp.elements[0].position = 0.0;  cr.color_ramp.elements[0].color = (0.06, 0.04, 0.03, 1)
    cr.color_ramp.elements[1].position = 0.55; cr.color_ramp.elements[1].color = (0.18, 0.08, 0.04, 1)
    cr.color_ramp.elements.new(0.75);           cr.color_ramp.elements[2].color = (0.60, 0.14, 0.01, 1)
    cr.color_ramp.elements.new(0.90);           cr.color_ramp.elements[3].color = (0.06, 0.04, 0.03, 1)
    emit = ns.new('ShaderNodeEmission'); emit.location = (200, 200)
    emit.inputs['Strength'].default_value = 2.0
    emit.inputs['Color'].default_value    = (0.9, 0.25, 0.01, 1)
    mix_s= ns.new('ShaderNodeMixShader'); mix_s.location = (750, 100)
    mix_s.inputs['Fac'].default_value = 0.12
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (300, 250)
    bmp.inputs['Strength'].default_value = 1.2
    img_a = img_slot(ns, "[UNITY] CooledLava_Albedo",  -580, -300)
    img_n = img_slot(ns, "[UNITY] CooledLava_Normal",  -580, -500)
    lk.new(noise.outputs['Fac'],      cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],       bsdf.inputs['Base Color'])
    lk.new(cr.outputs['Color'],       emit.inputs['Color'])
    lk.new(noise.outputs['Fac'],      bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],     bsdf.inputs['Normal'])
    lk.new(bsdf.outputs['BSDF'],      mix_s.inputs[1])
    lk.new(emit.outputs['Emission'],  mix_s.inputs[2])
    lk.new(mix_s.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_obsidian_mat():
    """Black volcanic glass — metallic, sharp, wave-faceted."""
    mat = bpy.data.materials.new("Mat_Ember_Obsidian")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Base Color'].default_value  = (0.03, 0.02, 0.04, 1)
    bsdf.inputs['Roughness'].default_value   = 0.06
    bsdf.inputs['Metallic'].default_value    = 0.55
    bsdf.inputs['Specular IOR Level'].default_value = 0.85
    wave = ns.new('ShaderNodeTexWave');  wave.location = (-400, 150)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'DIAGONAL'
    wave.inputs['Scale'].default_value      = 8.0
    wave.inputs['Distortion'].default_value = 3.0
    wave.inputs['Detail'].default_value     = 12.0
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (200, 200)
    bmp.inputs['Strength'].default_value = 0.5
    bmp.inputs['Distance'].default_value = 0.02
    emit_crack = ns.new('ShaderNodeEmission'); emit_crack.location = (200, -150)
    emit_crack.inputs['Color'].default_value    = (1.0, 0.3, 0.0, 1)
    emit_crack.inputs['Strength'].default_value = 4.0
    noise_crack = ns.new('ShaderNodeTexNoise'); noise_crack.location = (-400, -200)
    noise_crack.inputs['Scale'].default_value  = 80.0
    noise_crack.inputs['Detail'].default_value = 2.0
    cr_crack= ns.new('ShaderNodeValToRGB'); cr_crack.location = (-100, -200)
    cr_crack.color_ramp.elements[0].position = 0.85; cr_crack.color_ramp.elements[0].color = (0,0,0,1)
    cr_crack.color_ramp.elements[1].position = 0.95; cr_crack.color_ramp.elements[1].color = (1,1,1,1)
    mix_s = ns.new('ShaderNodeMixShader'); mix_s.location = (720, 50)
    img_a = img_slot(ns, "[UNITY] Obsidian_Albedo", -450, -450)
    lk.new(wave.outputs['Fac'],         bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],        bsdf.inputs['Normal'])
    lk.new(noise_crack.outputs['Fac'],   cr_crack.inputs['Fac'])
    lk.new(cr_crack.outputs['Color'],    mix_s.inputs['Fac'])
    lk.new(bsdf.outputs['BSDF'],         mix_s.inputs[1])
    lk.new(emit_crack.outputs['Emission'],mix_s.inputs[2])
    lk.new(mix_s.outputs['Shader'],      out.inputs['Surface'])
    return mat

def build_lava_glow_mat():
    """Pure emission — used for inner lava glow ribbons."""
    mat = bpy.data.materials.new("Mat_Ember_LavaGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (600, 0)
    emit = ns.new('ShaderNodeEmission'); emit.location = (300, 0)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-200, 100)
    noise.inputs['Scale'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (50, 100)
    cr.color_ramp.elements[0].color = (1.0, 0.2, 0.0, 1)
    cr.color_ramp.elements[1].color = (1.0, 0.85, 0.1, 1)
    lk.new(noise.outputs['Fac'],      cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],       emit.inputs['Color'])
    emit.inputs['Strength'].default_value = 10.0
    lk.new(emit.outputs['Emission'],  out.inputs['Surface'])
    return mat

def build_ash_mat():
    """Volcanic ash ground — pale grey, fine noise grain."""
    mat = bpy.data.materials.new("Mat_Ember_Ash")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Roughness'].default_value = 0.98
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-450, 150)
    noise.inputs['Scale'].default_value  = 55.0
    noise.inputs['Detail'].default_value = 10.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-150, 150)
    cr.color_ramp.elements[0].color = (0.22, 0.20, 0.18, 1)
    cr.color_ramp.elements[1].color = (0.52, 0.49, 0.45, 1)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (250, 200)
    bmp.inputs['Strength'].default_value = 0.3
    img_a = img_slot(ns, "[UNITY] Ash_Albedo", -500, -300)
    mix   = ns.new('ShaderNodeMixRGB'); mix.location = (350, 0)
    mix.inputs['Fac'].default_value = 0.0
    lk.new(noise.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     mix.inputs['Color1'])
    lk.new(img_a.outputs['Color'],  mix.inputs['Color2'])
    lk.new(noise.outputs['Fac'],    bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(mix.outputs['Color'],    bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_scorched_wood_mat():
    """Charred dead wood — burnt dark, wood-grain wave."""
    mat = bpy.data.materials.new("Mat_Ember_ScorchedWood")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (650, 0)
    bsdf.inputs['Roughness'].default_value = 0.97
    wave = ns.new('ShaderNodeTexWave'); wave.location = (-500, 100)
    wave.wave_type = 'RINGS'; wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value      = 12.0
    wave.inputs['Distortion'].default_value = 4.0
    wave.inputs['Detail'].default_value     = 8.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-200, 100)
    cr.color_ramp.elements[0].color = (0.025, 0.015, 0.010, 1)
    cr.color_ramp.elements[1].color = (0.080, 0.050, 0.030, 1)
    # ember glow in cracks
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-500, -150)
    noise.inputs['Scale'].default_value  = 60.0
    noise.inputs['Detail'].default_value = 3.0
    cr2  = ns.new('ShaderNodeValToRGB'); cr2.location = (-200, -150)
    cr2.color_ramp.elements[0].position = 0.88; cr2.color_ramp.elements[0].color = (0,0,0,1)
    cr2.color_ramp.elements[1].position = 0.95; cr2.color_ramp.elements[1].color = (1,1,1,1)
    emit = ns.new('ShaderNodeEmission'); emit.location = (150, -100)
    emit.inputs['Color'].default_value    = (0.9, 0.2, 0.0, 1)
    emit.inputs['Strength'].default_value = 1.5
    mix_s= ns.new('ShaderNodeMixShader'); mix_s.location = (800, 50)
    bmp  = ns.new('ShaderNodeBump'); bmp.location = (350, 250)
    bmp.inputs['Strength'].default_value = 0.8
    img_a = img_slot(ns, "[UNITY] ScorchedWood_Albedo", -550, -400)
    lk.new(wave.outputs['Fac'],        cr.inputs['Fac'])
    lk.new(noise.outputs['Fac'],       cr2.inputs['Fac'])
    lk.new(cr2.outputs['Color'],       mix_s.inputs['Fac'])
    lk.new(wave.outputs['Fac'],        bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],      bsdf.inputs['Normal'])
    lk.new(cr.outputs['Color'],        bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],       mix_s.inputs[1])
    lk.new(emit.outputs['Emission'],   mix_s.inputs[2])
    lk.new(mix_s.outputs['Shader'],    out.inputs['Surface'])
    return mat

def build_sulfur_smoke_mat():
    """Translucent yellow-grey smoke wisps."""
    mat = bpy.data.materials.new("Mat_Ember_SulfurSmoke")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location = (700, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (450, 0)
    bsdf.inputs['Base Color'].default_value  = (0.75, 0.72, 0.55, 1)
    bsdf.inputs['Roughness'].default_value   = 1.0
    bsdf.inputs['Alpha'].default_value       = 0.18
    bsdf.inputs['Subsurface Weight'].default_value = 0.5
    bsdf.inputs['Subsurface Radius'].default_value = (0.8, 0.8, 0.7)
    noise= ns.new('ShaderNodeTexNoise'); noise.location = (-350, 100)
    noise.inputs['Scale'].default_value = 3.0
    cr   = ns.new('ShaderNodeValToRGB'); cr.location = (-50, 100)
    cr.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1)
    cr.color_ramp.elements[1].color = (0.18, 0.0, 0.0, 1)  # alpha mask
    lk.new(noise.outputs['Fac'],    bsdf.inputs['Alpha'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

print("[EmberIsle] All materials built.")

# ─────────────────────────────────────────────────────────────────────────────
# GEOMETRY BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def build_volcano_terrain(name, size=100.0, peak_h=28.0, grid=64):
    """Main volcano terrain with caldera, flow channels, beach ring."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()

    step = size / grid
    for gi in range(grid + 1):
        for gj in range(grid + 1):
            x = (gi / grid - 0.5) * size
            y = (gj / grid - 0.5) * size
            nx, ny = x / (size * 0.5), y / (size * 0.5)
            dist = math.sqrt(nx*nx + ny*ny)

            # Volcano cone
            cone = max(0.0, 1.0 - dist * 1.08) ** 1.55 * peak_h
            # Caldera depression at summit
            caldera = max(0.0, 1.0 - (dist * 7.5) ** 2) * 5.5
            # Lava flow channels (radial sine)
            angle = math.atan2(ny, nx)
            channels = (math.sin(angle * 4) * 0.5 + math.sin(angle * 7 + 0.4) * 0.3) * \
                       max(0.0, 1.0 - dist * 1.4) * 4.5
            # Hardened lava field (base)
            lava_field = (math.sin(nx * 5.5) * math.cos(ny * 4.8) * 0.7 +
                          math.sin(nx * 10 + ny * 7.5) * 0.35) * max(0.0, dist - 0.25) * 3.5
            # Beach ring
            beach = max(0.0, 0.9 - max(0.0, dist - 0.78) * 5.0) * 0.7
            # Surface noise
            noise = (math.sin(nx * 14.0 + ny * 11.0) * 0.4 +
                     math.sin(nx * 22.0 - ny * 17.0) * 0.2 +
                     math.sin(nx * 7.5 + ny * 19.0) * 0.15)
            z = cone - caldera + channels + lava_field + beach + noise * 0.9
            bm.verts.new((x, y, z))

    bm.verts.ensure_lookup_table()
    for gi in range(grid):
        for gj in range(grid):
            a = gi * (grid + 1) + gj
            b = a + 1
            c = a + (grid + 1) + 1
            d = a + (grid + 1)
            try:
                bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except:
                pass

    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name

    # Subdivision + displacement
    sub = ob.modifiers.new("Subd", 'SUBSURF')
    sub.levels = 2; sub.render_levels = 3
    disp = ob.modifiers.new("DisplaceDetail", 'DISPLACE')
    tex = bpy.data.textures.new("VolcanoMusgrave", type='MUSGRAVE')
    tex.musgrave_type = 'RIDGED_MULTIFRACTAL'
    tex.noise_scale = 4.0; tex.noise_intensity = 1.3
    disp.texture = tex; disp.strength = 1.9; disp.texture_coords = 'LOCAL'
    return ob

def build_caldera_rim(name, radius=8.2, height=22.5):
    """Jagged torus rim around volcano peak."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 48; ring = 12
    minor = 1.6
    for s in range(segs):
        a_outer = s / segs * math.pi * 2
        for r in range(ring):
            a_inner = r / ring * math.pi * 2
            x = (radius + minor * math.cos(a_inner)) * math.cos(a_outer)
            y = (radius + minor * math.cos(a_inner)) * math.sin(a_outer)
            z = height + minor * math.sin(a_inner)
            # Jagged: add spike variations
            z += math.sin(a_outer * 8) * 0.9 + math.sin(a_outer * 13) * 0.45
            x += math.sin(a_outer * 5) * 0.15
            bm.verts.new((x, y, z))

    bm.verts.ensure_lookup_table()
    for s in range(segs):
        for r in range(ring):
            a = s * ring + r
            b = s * ring + (r + 1) % ring
            c = ((s + 1) % segs) * ring + (r + 1) % ring
            d = ((s + 1) % segs) * ring + r
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass

    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = ob.data.name = name
    return ob

def build_crater_pool(name, loc=(0, 0, 20.5)):
    """Glowing lava pool at caldera bottom."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 32
    for i in range(segs):
        a = i / segs * math.pi * 2
        r = 6.0 + math.sin(a * 5) * 0.4 + math.sin(a * 11) * 0.2
        bm.verts.new((r * math.cos(a), r * math.sin(a), 0))
    center = bm.verts.new((0, 0, -0.3))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        bm.faces.new([bm.verts[i], bm.verts[(i + 1) % segs], center])
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.name = ob.data.name = name
    return ob

def build_basalt_cliff(name, loc, scale, rot_z=0.0):
    """Thick cliff slab with Voronoi-displaced surface."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    w, d, h, segs = 1.0, 1.0, 1.0, 12
    for zi in range(segs + 1):
        for xi in range(segs + 1):
            x = (xi / segs - 0.5) * w
            z = (zi / segs) * h
            # Layered cliff strata
            y_strata = math.sin(z * 6.0) * 0.04 + math.sin(z * 14.0) * 0.02
            y_rough  = math.sin(x * 9.0 + z * 5.0) * 0.06
            bm.verts.new((x, y_strata + y_rough, z))
    bm.verts.ensure_lookup_table()
    for zi in range(segs):
        for xi in range(segs):
            a = zi * (segs + 1) + xi
            try:
                bm.faces.new([bm.verts[a], bm.verts[a+1],
                               bm.verts[a + segs + 2], bm.verts[a + segs + 1]])
            except: pass
    # Front face thickening
    face_verts = [v for v in bm.verts if abs(v.co.y) < 0.01]
    for v in face_verts:
        bm.verts.new((v.co.x, v.co.y - 0.1, v.co.z))
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.scale = scale; ob.rotation_euler.z = rot_z
    ob.name = ob.data.name = name
    disp = ob.modifiers.new("VoronoiCliff", 'DISPLACE')
    tex = bpy.data.textures.new(f"CliffVor_{name}", type='VORONOI')
    tex.noise_scale = 1.8
    disp.texture = tex; disp.strength = 0.8; disp.direction = 'X'
    sol = ob.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.3
    return ob

def build_basalt_column(name, loc, height=8.0, radius=0.9):
    """Hexagonal basalt column pillar."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides = 6; segs = 18
    for si in range(segs + 1):
        z = si / segs * height
        for vi in range(sides):
            a = vi / sides * math.pi * 2 + math.pi / 6
            r = radius * (1.0 + math.sin(z * 3.0) * 0.03)
            bm.verts.new((r * math.cos(a), r * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si * sides + vi
            b = si * sides + (vi + 1) % sides
            c = (si + 1) * sides + (vi + 1) % sides
            d = (si + 1) * sides + vi
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    # Top cap
    top_verts = [bm.verts[(segs) * sides + v] for v in range(sides)]
    bm.faces.new(top_verts)
    # Bottom cap
    bot_verts = [bm.verts[v] for v in range(sides)][::-1]
    bm.faces.new(bot_verts)
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_obsidian_spire(name, loc, height=14.0, base_r=1.2):
    """Twisted obsidian glass spire."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides = 5 + (hash(name) % 3); segs = 24
    seed = hash(name) % 100
    for si in range(segs + 1):
        t = si / segs
        z = t * height
        r = base_r * (1.0 - t ** 1.3)
        twist = t * math.pi * 0.55
        for vi in range(sides):
            a = vi / sides * math.pi * 2 + twist
            # Faceted glass surface
            r_facet = r * (1.0 + math.sin(a * sides * 0.5) * 0.08)
            bm.verts.new((r_facet * math.cos(a), r_facet * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si * sides + vi
            b = si * sides + (vi + 1) % sides
            c = (si + 1) * sides + (vi + 1) % sides
            d = (si + 1) * sides + vi
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    bot = [bm.verts[v] for v in range(sides)][::-1]
    bm.faces.new(bot)
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    bevel = ob.modifiers.new("BevelGlass", 'BEVEL')
    bevel.width = 0.03; bevel.segments = 1
    bevel.angle_limit = math.radians(35)
    return ob

def build_lava_vent(name, loc, vent_r=0.7, depth=0.25):
    """Ground crack lava vent."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    segs = 16
    for i in range(segs):
        a = i / segs * math.pi * 2
        r = vent_r + math.sin(a * 5) * 0.12 + math.sin(a * 11) * 0.06
        bm.verts.new((r * math.cos(a), r * math.sin(a), 0))
    # Inner glowing floor
    for i in range(segs):
        a = i / segs * math.pi * 2
        r2 = vent_r * 0.45
        bm.verts.new((r2 * math.cos(a), r2 * math.sin(a), -depth))
    center = bm.verts.new((0, 0, -depth - 0.08))
    bm.verts.ensure_lookup_table()
    for i in range(segs):
        ni = (i + 1) % segs
        try:
            bm.faces.new([bm.verts[i], bm.verts[ni],
                           bm.verts[segs + ni], bm.verts[segs + i]])
            bm.faces.new([bm.verts[segs + i], bm.verts[segs + ni], center])
        except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_cooled_lava_field(name, loc, size_x=18.0, size_y=12.0):
    """Flat hardened lava plain with noise surface."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    nx, ny = 20, 14
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = (i / nx - 0.5) * size_x
            y = (j / ny - 0.5) * size_y
            z = math.sin(x * 0.8 + y * 0.6) * 0.35 + math.sin(x * 2.5 + y * 1.8) * 0.15
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            try:
                bm.faces.new([bm.verts[a], bm.verts[a + 1],
                               bm.verts[a + nx + 2], bm.verts[a + nx + 1]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_scorched_trunk(name, loc, height=5.0, lean=(0.1, 0.05)):
    """Charred dead tree trunk, curved."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides = 7; segs = 20
    for si in range(segs + 1):
        t = si / segs
        z = t * height
        r = (0.18 + (1.0 - t) * 0.08) * (0.9 + rng.uniform(-0.05, 0.1))
        lean_x = math.sin(t * math.pi * 1.5) * lean[0] * height
        lean_y = math.sin(t * math.pi * 1.2) * lean[1] * height
        for vi in range(sides):
            a = vi / sides * math.pi * 2
            bm.verts.new((lean_x + r * math.cos(a),
                           lean_y + r * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si * sides + vi; b = si * sides + (vi + 1) % sides
            c = (si + 1) * sides + (vi + 1) % sides; d = (si + 1) * sides + vi
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

def build_branch(name, start, end, radius=0.04):
    """Single tree branch as cylinder."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    sv, ev = Vector(start), Vector(end)
    length = (ev - sv).length
    mid = (sv + ev) * 0.5
    bm = bmesh.new()
    sides = 5; segs = 6
    for si in range(segs + 1):
        t = si / segs
        r = radius * (1.0 - t * 0.6)
        for vi in range(sides):
            a = vi / sides * math.pi * 2
            bm.verts.new((r * math.cos(a), r * math.sin(a), (t - 0.5) * length))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si * sides + vi; b = si * sides + (vi + 1) % sides
            c = (si + 1) * sides + (vi + 1) % sides; d = (si + 1) * sides + vi
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    # Aim branch from start to end
    direction = ev - sv
    ob.location = mid
    if direction.length > 0.001:
        ob.rotation_mode = 'QUATERNION'
        ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direction.normalized())
    ob.name = ob.data.name = name
    return ob

def build_ash_patch(name, loc, size=10.0):
    """Irregular ash drift plane."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    n = 12
    for j in range(n + 1):
        for i in range(n + 1):
            x = (i / n - 0.5) * size
            y = (j / n - 0.5) * size * rng.uniform(0.7, 1.3)
            z = rng.uniform(-0.05, 0.05)
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    for j in range(n):
        for i in range(n):
            a = j * (n + 1) + i
            try:
                bm.faces.new([bm.verts[a], bm.verts[a+1],
                               bm.verts[a + n + 2], bm.verts[a + n + 1]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler.z = rng.uniform(0, math.pi * 2)
    ob.name = ob.data.name = name
    return ob

def build_smoke_wisp(name, loc, height=6.0, base_r=1.2):
    """Translucent cone smoke wisp."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    sides = 12; segs = 16
    for si in range(segs + 1):
        t = si / segs
        r = base_r * (1.0 - t * 0.65) * (1.0 + math.sin(t * math.pi * 3) * 0.15)
        z = t * height
        for vi in range(sides):
            a = vi / sides * math.pi * 2
            # Wisp drift
            drift_x = math.sin(t * math.pi * 2 + 0.5) * 0.4
            bm.verts.new((r * math.cos(a) + drift_x, r * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for si in range(segs):
        for vi in range(sides):
            a = si * sides + vi; b = si * sides + (vi + 1) % sides
            c = (si + 1) * sides + (vi + 1) % sides; d = (si + 1) * sides + vi
            try: bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]])
            except: pass
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.name = ob.data.name = name
    return ob

# ─────────────────────────────────────────────────────────────────────────────
# SCENE ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────
clear_scene()
rng = random.Random(420042)

col_root    = new_col("IsleTrial_EmberIsle")
col_terrain = new_col("EmberIsle_Terrain")
col_spires  = new_col("EmberIsle_ObsidianSpires")
col_vents   = new_col("EmberIsle_LavaVents")
col_trees   = new_col("EmberIsle_ScorchedTrees")
col_lava    = new_col("EmberIsle_LavaRivers")
col_cliffs  = new_col("EmberIsle_Cliffs")
col_effects = new_col("EmberIsle_Effects")

# Build all materials
mat_volc_rock   = build_volcanic_rock_mat()
mat_lava        = build_lava_mat()
mat_cooled_lava = build_cooled_lava_mat()
mat_obsidian    = build_obsidian_mat()
mat_lava_glow   = build_lava_glow_mat()
mat_ash         = build_ash_mat()
mat_wood        = build_scorched_wood_mat()
mat_smoke       = build_sulfur_smoke_mat()

# ── 1. VOLCANO TERRAIN ───────────────────────────────────────────────────────
terrain = build_volcano_terrain("EmberIsle_VolcanoTerrain")
assign_mat(terrain, mat_volc_rock)
smart_uv(terrain, angle=45)
link(col_terrain, terrain)
print("[EmberIsle] Volcano terrain created.")

# ── 2. CALDERA RIM ────────────────────────────────────────────────────────────
rim = build_caldera_rim("EmberIsle_CalderaRim")
assign_mat(rim, mat_cooled_lava)
smart_uv(rim)
link(col_terrain, rim)

# ── 3. CRATER LAVA POOL ───────────────────────────────────────────────────────
pool = build_crater_pool("EmberIsle_CraterLavaPool", loc=(0, 0, 20.8))
assign_mat(pool, mat_lava)
smart_uv(pool)
link(col_terrain, pool)
# Crater glow light
vl = bpy.data.lights.new("EmberIsle_CraterLight", type='POINT')
vl.energy = 15000; vl.color = (1.0, 0.3, 0.05); vl.shadow_soft_size = 8.0
vlo = bpy.data.objects.new("EmberIsle_CraterLight", vl)
vlo.location = (0, 0, 24); bpy.context.scene.collection.objects.link(vlo)
link(col_terrain, vlo)

# ── 4. BASALT CLIFF FACES ─────────────────────────────────────────────────────
cliff_configs = [
    ("EmberIsle_BasaltCliffFace_N", ( 0,  45,  2), (28, 4, 18), math.radians(0)),
    ("EmberIsle_BasaltCliffFace_E", ( 45,  0,  2), (28, 4, 14), math.radians(90)),
]
for cname, cloc, cscale, crot in cliff_configs:
    cl = build_basalt_cliff(cname, cloc, cscale, crot)
    assign_mat(cl, mat_volc_rock)
    smart_uv(cl)
    link(col_cliffs, cl)

# ── 5. BASALT COLUMNS ─────────────────────────────────────────────────────────
col_positions = [
    (( 22, 18, 2), 9.5, 0.85), ((-18, 25, 1), 7.5, 0.70), (( 28, -8, 1), 11.0, 1.0),
    ((-25, -5, 2), 8.0, 0.75), (( 15, 30, 1), 6.5, 0.65), ((-10, -28, 1), 8.5, 0.80),
]
for i, (pos, ht, rad) in enumerate(col_positions):
    bc = build_basalt_column(f"EmberIsle_BasaltColumn_{i+1:02d}", pos, ht, rad)
    assign_mat(bc, mat_volc_rock)
    smart_uv(bc)
    link(col_cliffs, bc)
print(f"[EmberIsle] {len(col_positions)} basalt columns created.")

# ── 6. OBSIDIAN SPIRES ────────────────────────────────────────────────────────
spire_configs = [
    (( 18, 12, 0), 14.0, 1.2), ((-22, 8, 0), 11.0, 1.0), (( 10,-20, 0), 16.5, 1.4),
    ((-14,-16, 0), 12.5, 0.9), (( 25, -5, 0),  9.5, 1.1), ((-28, 15, 0), 13.5, 1.05),
    ((  5, 28, 0), 10.0, 0.95),(( -8,-30, 0),  8.5, 0.85),
]
for i, (sp, sh, sr) in enumerate(spire_configs):
    spire = build_obsidian_spire(f"EmberIsle_ObsidianSpire_{i+1:02d}", sp, sh, sr)
    assign_mat(spire, mat_obsidian)
    smart_uv(spire)
    link(col_spires, spire)
print(f"[EmberIsle] {len(spire_configs)} obsidian spires created.")

# ── 7. LAVA VENTS ─────────────────────────────────────────────────────────────
vent_locs = [
    (12, 8, 0.2), (-10, 14, 0.3), (5, -18, 0.1), (-18, -5, 0.2),
    (20,-12, 0.1), (-5, 22, 0.3), (15, 18, 0.15), (-22,-18, 0.2),
]
for i, (vx, vy, vz) in enumerate(vent_locs):
    vent = build_lava_vent(f"EmberIsle_LavaVent_{i+1:02d}", (vx, vy, vz),
                            vent_r=0.6 + rng.uniform(-0.1, 0.4),
                            depth=0.25 + rng.uniform(0, 0.15))
    assign_mat(vent, mat_lava)
    smart_uv(vent)
    link(col_vents, vent)
    # Point light per vent
    vtl = bpy.data.lights.new(f"VentLight_{i+1:02d}", type='POINT')
    vtl.energy = 900; vtl.color = (1.0, 0.35, 0.02); vtl.shadow_soft_size = 0.5
    vtlo = bpy.data.objects.new(f"VentLight_{i+1:02d}", vtl)
    vtlo.location = (vx, vy, vz + 1.5); bpy.context.scene.collection.objects.link(vtlo)
    link(col_vents, vtlo)
print(f"[EmberIsle] {len(vent_locs)} lava vents + lights created.")

# ── 8. LAVA RIVERS (bezier curve + inner glow ribbon) ─────────────────────────
river_paths = [
    [(0,0,22),(6,3,18),(12,8,12),(20,15,4),(28,20,0.5)],
    [(0,0,22),(-5,4,17),(-10,10,11),(-15,18,5),(-22,25,0.5)],
    [(0,0,22),(3,-6,16),(8,-14,9),(12,-22,3),(16,-30,0.5)],
]
for ri, pts in enumerate(river_paths):
    for kind, (bdepth, mat_r) in enumerate([(1.9, mat_cooled_lava), (0.65, mat_lava_glow)]):
        cdata = bpy.data.curves.new(f"EmberIsle_LavaRiver{ri+1:02d}_{kind}", type='CURVE')
        cdata.dimensions = '3D'
        spl = cdata.splines.new('BEZIER')
        spl.bezier_points.add(len(pts) - 1)
        for pi, (px, py, pz) in enumerate(pts):
            bp = spl.bezier_points[pi]
            bp.co = (px, py, pz + kind * 0.08)
            bp.handle_left_type = bp.handle_right_type = 'AUTO'
        cdata.bevel_depth = bdepth; cdata.bevel_resolution = 5
        robj = bpy.data.objects.new(f"EmberIsle_LavaRiver{ri+1:02d}_{kind}", cdata)
        bpy.context.scene.collection.objects.link(robj)
        assign_mat(robj, mat_r)
        link(col_lava, robj)
print(f"[EmberIsle] {len(river_paths)} lava rivers (+ glow cores) created.")

# ── 9. COOLED LAVA FIELDS ─────────────────────────────────────────────────────
field_configs = [
    ("EmberIsle_CooledLavaField_01", (22, 10, 0.3), 20.0, 14.0),
    ("EmberIsle_CooledLavaField_02", (-18, 20, 0.4), 16.0, 11.0),
    ("EmberIsle_CooledLavaField_03", (10, -22, 0.2), 18.0, 12.0),
]
for fname, floc, fx, fy in field_configs:
    field = build_cooled_lava_field(fname, floc, fx, fy)
    assign_mat(field, mat_cooled_lava)
    smart_uv(field)
    link(col_terrain, field)

# ── 10. SCORCHED TREES (12) + BRANCHES ────────────────────────────────────────
tree_positions = [
    (16, 5, 8.5), (-12, 18, 7.0), (22,-10, 5.0), (-20,-8,  6.5),
    ( 8, 22, 9.0), (-8, -22, 4.5), (28, 8, 2.0),  (-26, 12, 3.5),
    (14,-18, 6.0), (-16, 20, 8.0), (10, 26, 7.5),  (-24,-4, 4.0),
]
for i, (tx, ty, tz) in enumerate(tree_positions):
    h = 3.5 + rng.uniform(0, 3.5)
    trunk = build_scorched_trunk(f"EmberIsle_ScorchedTree_{i+1:02d}_Trunk",
                                   (tx, ty, tz), h,
                                   lean=(rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12)))
    assign_mat(trunk, mat_wood); smart_uv(trunk)
    link(col_trees, trunk)

    # 2-4 branches per tree
    num_br = rng.randint(2, 4)
    for b in range(num_br):
        ba = (b / num_br) * math.pi * 2 + rng.uniform(-0.4, 0.4)
        bl = 1.2 + rng.uniform(0, 2.0)
        bstart = (tx, ty, tz + h * rng.uniform(0.5, 0.85))
        bend   = (tx + math.cos(ba) * bl,
                   ty + math.sin(ba) * bl,
                   tz + h * rng.uniform(0.5, 0.85) + rng.uniform(-0.3, 0.8))
        br = build_branch(f"EmberIsle_ScorchedTree_{i+1:02d}_Branch_{b+1}",
                           bstart, bend, radius=0.055 + rng.uniform(0, 0.035))
        assign_mat(br, mat_wood); smart_uv(br)
        link(col_trees, br)
print(f"[EmberIsle] {len(tree_positions)} scorched trees with branches created.")

# ── 11. ASH PATCHES ────────────────────────────────────────────────────────────
ash_locs = [(20, 16, 0.2), (-14, 20, 0.3), (24,-8, 0.1), (-20,-12, 0.2), (10,-25, 0.1)]
for i, (ax, ay, az) in enumerate(ash_locs):
    ap = build_ash_patch(f"EmberIsle_AshPatch_{i+1:02d}",
                          (ax, ay, az), 10.0 + rng.uniform(0, 8.0))
    assign_mat(ap, mat_ash); smart_uv(ap)
    link(col_terrain, ap)

# ── 12. SULFUR SMOKE WISPS ────────────────────────────────────────────────────
smoke_locs = [(12, 8, 0.5), (-10, 14, 0.4), (5, -18, 0.3), (20, -12, 0.5)]
for i, (sx, sy, sz) in enumerate(smoke_locs):
    wisp = build_smoke_wisp(f"EmberIsle_SulfurVentSmoke_{i+1:02d}",
                              (sx, sy, sz), height=5.0 + rng.uniform(0, 4.0))
    assign_mat(wisp, mat_smoke); smart_uv(wisp)
    link(col_effects, wisp)

# ── Root empty ────────────────────────────────────────────────────────────────
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
root = bpy.context.active_object
root.name = "EmberIsle_ROOT"
link(col_root, root)

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("EMBER ISLE — FULL QUALITY BUILD COMPLETE")
print("="*65)
print("  Objects: terrain, caldera rim, crater lava pool")
print(f"  Basalt cliff faces     : 2")
print(f"  Basalt columns         : {len(col_positions)}")
print(f"  Obsidian spires        : {len(spire_configs)} (twisted, faceted)")
print(f"  Lava vents + lights    : {len(vent_locs)}")
print(f"  Lava river curves      : {len(river_paths)} (+ inner glow cores)")
print(f"  Cooled lava fields     : {len(field_configs)}")
print(f"  Scorched trees         : {len(tree_positions)} (with branches)")
print(f"  Ash patches            : {len(ash_locs)}")
print(f"  Sulfur smoke wisps     : {len(smoke_locs)}")
print("  Materials: 8 full procedural node trees + [UNITY] image slots")
print("  UV: smart_project on all mesh objects")
print(f"\n  Export: Select IsleTrial_EmberIsle collection")
print(f"  File → Export → FBX | Scale: 0.01 | Apply Transform: ON")
print(f"  Unity: orange/red VolumeProfile fog + ember particle system")
print("="*65)
