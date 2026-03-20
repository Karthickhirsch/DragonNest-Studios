"""
37_Environment_AtmosphericMysteries.py
IsleTrial — Atmospheric Mysteries Environment Set
================================================
Creates a deeply atmospheric, eerie environment: floating island
fragments, arcane energy orbs, stone monolith gates, rift/portal
archways, reality-tear mesh effects, fog planes, spectral lanterns,
cracked ground planes, scattered arcane runes, levitating debris,
storm cloud proxies, and a dramatic arcane nexus.

All materials use full procedural node networks + [UNITY] image slots.
smart_uv() applied to every mesh. Run in Blender ≥ 3.6.
"""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

rng = random.Random(370037)

# ── helpers ───────────────────────────────────────────────────────────────────
def ns_lk(mat):
    return mat.node_tree.nodes, mat.node_tree.links

def img_slot(ns, name, x, y):
    n = ns.new('ShaderNodeTexImage')
    n.label = name; n.location = (x, y)
    return n

def smart_uv(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def link(col, obj):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def add_pt_light(col, loc, energy, color, radius=0.3):
    bpy.ops.object.light_add(type='POINT', location=loc)
    lt = bpy.context.active_object
    lt.data.energy = energy; lt.data.color = color
    lt.data.shadow_soft_size = radius
    col.objects.link(lt)
    if lt.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(lt)
    return lt

# ── material builders ─────────────────────────────────────────────────────────
def build_dark_stone_mat():
    mat = bpy.data.materials.new("Mat_Atmos_DarkStone")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.88
    bsdf.inputs['Metallic'].default_value  = 0.05
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-600, 200)
    mus.musgrave_type = 'RIDGED_MULTIFRACTAL'
    mus.inputs['Scale'].default_value   = 4.5
    mus.inputs['Detail'].default_value  = 9.0
    mus.inputs['Dimension'].default_value = 1.2
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0
    cr1.color_ramp.elements[0].color = (0.04, 0.03, 0.05, 1)
    cr1.color_ramp.elements[1].position = 1.0
    cr1.color_ramp.elements[1].color = (0.14, 0.12, 0.18, 1)
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600,-100)
    vor.voronoi_dimensions = '3D'
    vor.inputs['Scale'].default_value = 5.0
    cr2  = ns.new('ShaderNodeValToRGB');       cr2.location  = (-300,-100)
    cr2.color_ramp.elements[0].position = 0.0
    cr2.color_ramp.elements[0].color = (0.08, 0.06, 0.10, 1)
    cr2.color_ramp.elements[1].position = 1.0
    cr2.color_ramp.elements[1].color = (0.20, 0.16, 0.25, 1)
    mix  = ns.new('ShaderNodeMixRGB');         mix.location  = (50, 100)
    mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = 0.6
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.8
    bmp.inputs['Distance'].default_value = 0.05
    img_a = img_slot(ns,"[UNITY] DarkStone_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] DarkStone_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] DarkStone_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr1.inputs['Fac'])
    lk.new(vor.outputs['Distance'],cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],   mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mus.outputs['Fac'],     bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],  bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_arcane_glow_mat(color=(0.5, 0.2, 1.0)):
    mat = bpy.data.materials.new("Mat_Atmos_ArcaneGlow")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.10
    bsdf.inputs['Transmission Weight'].default_value = 0.80
    bsdf.inputs['IOR'].default_value = 1.50
    bsdf.inputs['Emission Color'].default_value = (*color, 1)
    bsdf.inputs['Emission Strength'].default_value = 4.0
    bsdf.inputs['Base Color'].default_value = (*[v*0.5 for v in color], 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (*color, 1)
    em.inputs['Strength'].default_value = 8.0
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-450, 0)
    noise.inputs['Scale'].default_value  = 10.0
    noise.inputs['Detail'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] ArcaneGlow_Emission", -660,-350)
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_rift_mat():
    mat = bpy.data.materials.new("Mat_Atmos_Rift")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['Transmission Weight'].default_value = 1.0
    bsdf.inputs['IOR'].default_value = 1.0
    bsdf.inputs['Base Color'].default_value = (0.0, 0.0, 0.0, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.3, 0.0, 0.8, 1)
    em.inputs['Strength'].default_value = 10.0
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-500, 0)
    vor.voronoi_dimensions = '3D'
    vor.inputs['Scale'].default_value = 6.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-250, 0)
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.25;cr.color_ramp.elements[1].color = (1,1,1,1)
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-500,-200)
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = 8.0
    wave.inputs['Distortion'].default_value = 4.0
    mix  = ns.new('ShaderNodeMixRGB');         mix.location  = (-50, 0)
    mix.blend_type = 'SCREEN'; mix.inputs['Fac'].default_value = 0.5
    img_e = img_slot(ns,"[UNITY] Rift_Emission", -660,-400)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(wave.outputs['Fac'],     mix.inputs['Color1'])
    lk.new(cr.outputs['Color'],     mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

def build_fog_plane_mat():
    mat = bpy.data.materials.new("Mat_Atmos_Fog")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Alpha'].default_value     = 0.35
    bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Base Color'].default_value = (0.55, 0.50, 0.65, 1)
    mat.blend_method = 'BLEND'
    noise= ns.new('ShaderNodeTexNoise');       noise.location= (-400, 100)
    noise.inputs['Scale'].default_value = 2.5
    noise.inputs['Detail'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-150, 100)
    cr.color_ramp.elements[0].position = 0.3
    cr.color_ramp.elements[0].color = (0.45, 0.42, 0.55, 1)
    cr.color_ramp.elements[1].position = 0.8
    cr.color_ramp.elements[1].color = (0.65, 0.62, 0.75, 1)
    img_a = img_slot(ns,"[UNITY] Fog_Albedo", -660,-300)
    lk.new(noise.outputs['Fac'],   cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_cracked_ground_mat():
    mat = bpy.data.materials.new("Mat_Atmos_CrackedGround")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (1000, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (680, 0)
    bsdf.inputs['Roughness'].default_value = 0.92
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-600, 200)
    vor.voronoi_dimensions = '3D'
    vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 3.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-300, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.0,0.0,0.0,1)
    cr1.color_ramp.elements[1].position = 0.15;cr1.color_ramp.elements[1].color = (0.1,0.08,0.14,1)
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-600,-100)
    mus.inputs['Scale'].default_value = 4.0
    mus.inputs['Detail'].default_value = 6.0
    cr2  = ns.new('ShaderNodeValToRGB');       cr2.location  = (-300,-100)
    cr2.color_ramp.elements[0].position = 0.0
    cr2.color_ramp.elements[0].color = (0.08, 0.06, 0.12, 1)
    cr2.color_ramp.elements[1].position = 1.0
    cr2.color_ramp.elements[1].color = (0.22, 0.18, 0.30, 1)
    mix  = ns.new('ShaderNodeMixRGB');         mix.location  = (50, 100)
    mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = 0.5
    bmp  = ns.new('ShaderNodeBump');           bmp.location  = (380, 250)
    bmp.inputs['Strength'].default_value = 1.5
    bmp.inputs['Distance'].default_value = 0.04
    img_a = img_slot(ns,"[UNITY] CrackedGround_Albedo",    -660,-350)
    img_n = img_slot(ns,"[UNITY] CrackedGround_Normal",    -660,-550)
    img_r = img_slot(ns,"[UNITY] CrackedGround_Roughness", -660,-750)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (380, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(vor.outputs['Distance'], cr1.inputs['Fac'])
    lk.new(mus.outputs['Fac'],      cr2.inputs['Fac'])
    lk.new(cr1.outputs['Color'],    mix.inputs['Color1'])
    lk.new(cr2.outputs['Color'],    mix.inputs['Color2'])
    lk.new(mix.outputs['Color'],    mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'],  mix2.inputs['Color2'])
    lk.new(vor.outputs['Distance'], bmp.inputs['Height'])
    lk.new(bmp.outputs['Normal'],   bsdf.inputs['Normal'])
    lk.new(mix2.outputs['Color'],   bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat

def build_spectral_lantern_mat():
    mat = bpy.data.materials.new("Mat_Atmos_SpectralLantern")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (800, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (580, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (320, 100)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Metallic'].default_value  = 0.8
    bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.15, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (320,-100)
    em.inputs['Color'].default_value    = (0.3, 0.8, 1.0, 1)
    em.inputs['Strength'].default_value = 8.0
    img_a = img_slot(ns,"[UNITY] Lantern_Albedo",   -400,-300)
    img_e = img_slot(ns,"[UNITY] Lantern_Emission", -400,-500)
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_energy_orb_mat(color=(0.4, 0.2, 1.0)):
    mat = bpy.data.materials.new("Mat_Atmos_EnergyOrb")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 150)
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['Transmission Weight'].default_value = 0.95
    bsdf.inputs['IOR'].default_value = 1.45
    bsdf.inputs['Base Color'].default_value = (*[v*0.4 for v in color], 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (*color, 1)
    em.inputs['Strength'].default_value = 15.0
    wave = ns.new('ShaderNodeTexWave');        wave.location = (-450, 0)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 3.0
    wave.inputs['Distortion'].default_value = 3.5
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = (0,0,0,1)
    cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = (1,1,1,1)
    img_e = img_slot(ns,"[UNITY] EnergyOrb_Emission", -660,-350)
    lk.new(wave.outputs['Fac'],    cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],    em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],   add.inputs[0])
    lk.new(em.outputs['Emission'], add.inputs[1])
    lk.new(add.outputs['Shader'],  out.inputs['Surface'])
    return mat

def build_storm_cloud_mat():
    mat = bpy.data.materials.new("Mat_Atmos_StormCloud")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (800, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (550, 0)
    bsdf.inputs['Alpha'].default_value = 0.7
    bsdf.inputs['Roughness'].default_value = 1.0
    mat.blend_method = 'BLEND'
    mus  = ns.new('ShaderNodeTexMusgrave');    mus.location  = (-500, 200)
    mus.musgrave_type = 'FBM'
    mus.inputs['Scale'].default_value  = 1.8
    mus.inputs['Detail'].default_value = 7.0
    cr1  = ns.new('ShaderNodeValToRGB');       cr1.location  = (-200, 200)
    cr1.color_ramp.elements[0].position = 0.0; cr1.color_ramp.elements[0].color = (0.06,0.04,0.10,1)
    cr1.color_ramp.elements[1].position = 1.0; cr1.color_ramp.elements[1].color = (0.28,0.22,0.38,1)
    img_a = img_slot(ns,"[UNITY] StormCloud_Albedo", -660,-300)
    mix2  = ns.new('ShaderNodeMixRGB');        mix2.location = (200, 0)
    mix2.inputs['Fac'].default_value = 0.0
    lk.new(mus.outputs['Fac'],     cr1.inputs['Fac'])
    lk.new(cr1.outputs['Color'],   mix2.inputs['Color1'])
    lk.new(img_a.outputs['Color'], mix2.inputs['Color2'])
    lk.new(mix2.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def build_rune_crack_mat():
    mat = bpy.data.materials.new("Mat_Atmos_RuneCrack")
    mat.use_nodes = True
    ns, lk = ns_lk(mat); ns.clear()
    out  = ns.new('ShaderNodeOutputMaterial'); out.location  = (900, 0)
    add  = ns.new('ShaderNodeAddShader');      add.location  = (680, 0)
    bsdf = ns.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 100)
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Base Color'].default_value = (0.08, 0.06, 0.12, 1)
    em   = ns.new('ShaderNodeEmission');       em.location   = (400,-100)
    em.inputs['Color'].default_value    = (0.5, 0.1, 1.0, 1)
    em.inputs['Strength'].default_value = 6.0
    vor  = ns.new('ShaderNodeTexVoronoi');     vor.location  = (-450, 0)
    vor.voronoi_dimensions = '3D'
    vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 4.0
    cr   = ns.new('ShaderNodeValToRGB');       cr.location   = (-200, 0)
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (1,1,1,1)
    cr.color_ramp.elements[1].position = 0.1; cr.color_ramp.elements[1].color = (0,0,0,1)
    img_a = img_slot(ns,"[UNITY] RuneCrack_Albedo",   -660,-350)
    img_e = img_slot(ns,"[UNITY] RuneCrack_Emission", -660,-550)
    lk.new(vor.outputs['Distance'], cr.inputs['Fac'])
    lk.new(cr.outputs['Color'],     em.inputs['Strength'])
    lk.new(bsdf.outputs['BSDF'],    add.inputs[0])
    lk.new(em.outputs['Emission'],  add.inputs[1])
    lk.new(add.outputs['Shader'],   out.inputs['Surface'])
    return mat

# ── geometry builders ─────────────────────────────────────────────────────────
def build_monolith(name, height=10.0, base_w=1.2, mat=None):
    bm = bmesh.new()
    rings = 24
    verts_ring = []
    for r in range(rings + 1):
        t = r / rings; z = t * height
        taper = 1.0 - t * 0.80
        w = base_w * taper * 0.5
        # slight twist
        twist = t * math.pi * 0.1
        corners = [
            (-w*math.cos(twist)-w*0.3*math.sin(twist),
             -w*math.sin(twist)+w*0.3*math.cos(twist), z),
            ( w*math.cos(twist)-w*0.3*math.sin(twist),
              w*math.sin(twist)+w*0.3*math.cos(twist), z),
            ( w*math.cos(twist)+w*0.3*math.sin(twist),
             -w*math.sin(twist)+w*0.3*math.cos(twist), z + rng.uniform(-0.02, 0.02)),
            (-w*math.cos(twist)+w*0.3*math.sin(twist),
             -w*math.sin(twist)-w*0.3*math.cos(twist), z + rng.uniform(-0.02, 0.02)),
        ]
        verts_ring.append([bm.verts.new(c) for c in corners])
    bm.verts.ensure_lookup_table()
    for r in range(rings):
        for s in range(4):
            bm.faces.new([verts_ring[r][s], verts_ring[r][(s+1)%4],
                          verts_ring[r+1][(s+1)%4], verts_ring[r+1][s]])
    # tip
    tip = bm.verts.new((0, 0, height + 0.8))
    for s in range(4):
        bm.faces.new([verts_ring[rings][s], verts_ring[rings][(s+1)%4], tip])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_portal_arch(name, span=5.0, height=7.0, mat_stone=None, mat_rift=None):
    bm_stone = bmesh.new()
    segs = 24
    def arch_pt(t):
        ang = math.pi * t
        return (span * 0.5 * math.cos(math.pi - ang), 0.0,
                height - span * 0.5 + span * 0.5 * math.sin(ang))
    # stone arch body
    for i in range(segs):
        t0 = i / segs; t1 = (i+1) / segs
        ox0, _, oz0 = arch_pt(t0)
        ox1, _, oz1 = arch_pt(t1)
        thick = 0.7
        pts = [(ox0*1.0, -thick, oz0), (ox0*1.0, thick, oz0),
               (ox1*1.0, thick, oz1), (ox1*1.0, -thick, oz1)]
        bm_stone.faces.new([bm_stone.verts.new(p) for p in pts])
        pts_i = [(ox0*0.82,-thick, oz0*0.96+0.1),
                 (ox0*0.82, thick, oz0*0.96+0.1),
                 (ox1*0.82, thick, oz1*0.96+0.1),
                 (ox1*0.82,-thick, oz1*0.96+0.1)]
        bm_stone.faces.new([bm_stone.verts.new(p) for p in [pts[0], pts_i[0], pts_i[3], pts[3]]])
        bm_stone.faces.new([bm_stone.verts.new(p) for p in [pts[1], pts[2], pts_i[2], pts_i[1]]])
    # pillars
    for px in [-span * 0.5, span * 0.5]:
        for rz in range(12):
            z0 = rz * (height - span * 0.5) / 11
            z1 = (rz+1) * (height - span * 0.5) / 11
            pr = 0.38
            pts_bot = [bm_stone.verts.new((px + pr*math.cos(2*math.pi*k/8),
                                           pr*math.sin(2*math.pi*k/8), z0)) for k in range(8)]
            pts_top = [bm_stone.verts.new((px + pr*math.cos(2*math.pi*k/8),
                                           pr*math.sin(2*math.pi*k/8), z1)) for k in range(8)]
            for k in range(8):
                bm_stone.faces.new([pts_bot[k], pts_bot[(k+1)%8],
                                    pts_top[(k+1)%8], pts_top[k]])
    mesh_s = bpy.data.meshes.new(name + "_Stone")
    bm_stone.to_mesh(mesh_s); bm_stone.free()
    obj_s = bpy.data.objects.new(name + "_Stone", mesh_s)
    if mat_stone: assign_mat(obj_s, mat_stone)
    smart_uv(obj_s)

    # rift portal fill
    bm_rift = bmesh.new()
    rift_verts = []
    rift_segs = 20
    for i in range(rift_segs + 1):
        t = i / rift_segs
        rx2, _, rz = arch_pt(t)
        rift_verts.append(bm_rift.verts.new((rx2 * 0.82, 0, rz * 0.96 + 0.1)))
    # create fill as fan triangles
    cx = 0; cz = height * 0.5
    center = bm_rift.verts.new((cx, 0, cz))
    for i in range(rift_segs):
        bm_rift.faces.new([rift_verts[i], rift_verts[i+1], center])
    # ground fill rectangle
    for x, z in [(-span*0.4, 0), (span*0.4, 0), (span*0.4, height - span*0.5), (-span*0.4, height - span*0.5)]:
        bm_rift.verts.new((x, 0, z))
    bm_rift.verts.ensure_lookup_table()
    n = len(bm_rift.verts)
    bm_rift.faces.new([bm_rift.verts[n-4], bm_rift.verts[n-3],
                       bm_rift.verts[n-2], bm_rift.verts[n-1]])
    mesh_r = bpy.data.meshes.new(name + "_Rift")
    bm_rift.to_mesh(mesh_r); bm_rift.free()
    obj_r = bpy.data.objects.new(name + "_Rift", mesh_r)
    if mat_rift: assign_mat(obj_r, mat_rift)
    smart_uv(obj_r)
    return obj_s, obj_r

def build_floating_fragment(name, size=3.0, mat=None):
    bm = bmesh.new()
    # irregular rock chunk
    segs = 8; rings = 7
    verts = []
    for r in range(rings):
        t = r / (rings - 1)
        z = (t - 0.5) * size * rng.uniform(0.8, 1.2)
        ring_r = size * 0.5 * math.sin(t * math.pi) * rng.uniform(0.7, 1.3)
        ring = []
        for s in range(segs):
            ang = 2*math.pi*s/segs + rng.uniform(-0.2, 0.2)
            r2 = ring_r * rng.uniform(0.75, 1.25)
            ring.append(bm.verts.new((r2*math.cos(ang), r2*math.sin(ang), z)))
        verts.append(ring)
    bm.verts.ensure_lookup_table()
    for r in range(rings - 1):
        for s in range(segs):
            bm.faces.new([verts[r][s], verts[r][(s+1)%segs],
                          verts[r+1][(s+1)%segs], verts[r+1][s]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_energy_orb(name, radius=0.5, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=16, radius=radius)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_cracked_ground_plane(name, size_x=20, size_y=20, mat=None):
    bm = bmesh.new()
    segs_x, segs_y = 24, 24
    verts = []
    for iy in range(segs_y + 1):
        row = []
        for ix in range(segs_x + 1):
            fx = (ix / segs_x - 0.5) * size_x
            fy = (iy / segs_y - 0.5) * size_y
            fz = rng.uniform(-0.3, 0.3) + 0.2 * math.sin(fx * 0.5) * math.sin(fy * 0.5)
            row.append(bm.verts.new((fx, fy, fz)))
        verts.append(row)
    bm.verts.ensure_lookup_table()
    for iy in range(segs_y):
        for ix in range(segs_x):
            bm.faces.new([verts[iy][ix], verts[iy][ix+1],
                          verts[iy+1][ix+1], verts[iy+1][ix]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_fog_plane(name, w=12, d=10, mat=None):
    bm = bmesh.new()
    segs_w, segs_d = 8, 6
    verts = []
    for iy in range(segs_d + 1):
        row = []
        for ix in range(segs_w + 1):
            fx = (ix / segs_w - 0.5) * w
            fy = (iy / segs_d - 0.5) * d
            fz = rng.uniform(-0.15, 0.15)
            row.append(bm.verts.new((fx, fy, fz)))
        verts.append(row)
    bm.verts.ensure_lookup_table()
    for iy in range(segs_d):
        for ix in range(segs_w):
            bm.faces.new([verts[iy][ix], verts[iy][ix+1],
                          verts[iy+1][ix+1], verts[iy+1][ix]])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_spectral_lantern(name, mat=None):
    bm = bmesh.new()
    # lantern cage
    cage_h = 0.6; cage_r = 0.18; cage_segs = 8
    for i in range(cage_segs):
        a0 = 2*math.pi*i/cage_segs; a1 = 2*math.pi*(i+1)/cage_segs
        # vertical bars
        for z in [0, cage_h]:
            bm.verts.new((cage_r*math.cos(a0), cage_r*math.sin(a0), z))
        # horizontal rings
        for ring_h in [0, cage_h*0.5, cage_h]:
            v0 = bm.verts.new((cage_r*math.cos(a0), cage_r*math.sin(a0), ring_h))
            v1 = bm.verts.new((cage_r*math.cos(a1), cage_r*math.sin(a1), ring_h))
    # hook top
    for t in range(8):
        ang = t * math.pi / 7
        bm.verts.new((cage_r*0.5*math.cos(ang), 0, cage_h + 0.12*math.sin(ang)))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_reality_tear(name, mat=None):
    bm = bmesh.new()
    # jagged tear shape
    segs = 16
    verts_out = []
    for i in range(segs):
        ang = 2*math.pi*i/segs
        r = 1.2 + 0.5 * math.sin(i * 3.7) + rng.uniform(-0.15, 0.15)
        verts_out.append(bm.verts.new((r*math.cos(ang), 0, r*math.sin(ang) * 2.0)))
    bm.verts.ensure_lookup_table()
    center = bm.verts.new((0, 0.05, 0))
    for i in range(segs):
        bm.faces.new([verts_out[i], verts_out[(i+1)%segs], center])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

def build_arcane_nexus(name, mat_stone=None, mat_rune=None):
    bm = bmesh.new()
    # central platform ring
    pr = 4.0; pth = 0.5; ring_segs = 32
    for s in range(ring_segs):
        a0 = 2*math.pi*s/ring_segs; a1 = 2*math.pi*(s+1)/ring_segs
        pts = [(pr*math.cos(a0),pr*math.sin(a0),0),(pr*math.cos(a1),pr*math.sin(a1),0),
               (pr*math.cos(a1),pr*math.sin(a1),pth),(pr*math.cos(a0),pr*math.sin(a0),pth)]
        bm.faces.new([bm.verts.new(p) for p in pts])
        # outer
        pr2 = pr + 0.8
        pts2= [(pr2*math.cos(a0),pr2*math.sin(a0),0),(pr2*math.cos(a1),pr2*math.sin(a1),0),
               (pr2*math.cos(a1),pr2*math.sin(a1),pth),(pr2*math.cos(a0),pr2*math.sin(a0),pth)]
        bm.faces.new([bm.verts.new(p) for p in pts2])
        bm.faces.new([bm.verts.new(p) for p in [
            (pr*math.cos(a0),pr*math.sin(a0),pth),
            (pr*math.cos(a1),pr*math.sin(a1),pth),
            (pr2*math.cos(a1),pr2*math.sin(a1),pth),
            (pr2*math.cos(a0),pr2*math.sin(a0),pth)]])
    # center floor disc
    disc_segs = 24
    disc_verts = [bm.verts.new((pr*0.9*math.cos(2*math.pi*s/disc_segs),
                                 pr*0.9*math.sin(2*math.pi*s/disc_segs), pth*0.9))
                  for s in range(disc_segs)]
    bm.verts.ensure_lookup_table()
    bm.faces.new(disc_verts)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat_stone: assign_mat(obj, mat_stone)
    smart_uv(obj)
    return obj

def build_storm_cloud(name, w=8, h=3, d=5, mat=None):
    bm = bmesh.new()
    # multiple overlapping lobes
    lobe_count = 6
    for lb in range(lobe_count):
        cx = rng.uniform(-w*0.3, w*0.3)
        cy = rng.uniform(-d*0.2, d*0.2)
        cz = rng.uniform(-h*0.2, h*0.3)
        lw = rng.uniform(w*0.4, w*0.7)
        lh = rng.uniform(h*0.4, h*0.8)
        ld = rng.uniform(d*0.4, d*0.7)
        segs_u = 10; segs_v = 8
        for v in range(segs_v):
            lat0 = math.pi * v / segs_v - math.pi/2
            lat1 = math.pi * (v+1) / segs_v - math.pi/2
            for u in range(segs_u):
                lon0 = 2*math.pi*u/segs_u
                lon1 = 2*math.pi*(u+1)/segs_u
                pts = [
                    (cx+lw*math.cos(lat0)*math.cos(lon0), cy+ld*math.cos(lat0)*math.sin(lon0), cz+lh*math.sin(lat0)),
                    (cx+lw*math.cos(lat0)*math.cos(lon1), cy+ld*math.cos(lat0)*math.sin(lon1), cz+lh*math.sin(lat0)),
                    (cx+lw*math.cos(lat1)*math.cos(lon1), cy+ld*math.cos(lat1)*math.sin(lon1), cz+lh*math.sin(lat1)),
                    (cx+lw*math.cos(lat1)*math.cos(lon0), cy+ld*math.cos(lat1)*math.sin(lon0), cz+lh*math.sin(lat1)),
                ]
                bm.faces.new([bm.verts.new(p) for p in pts])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat: assign_mat(obj, mat)
    smart_uv(obj)
    return obj

# ── scene assembly ────────────────────────────────────────────────────────────
def build_scene():
    for o in list(bpy.data.objects):   bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):    bpy.data.meshes.remove(m, do_unlink=True)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m, do_unlink=True)

    col = bpy.data.collections.new("AtmosphericMysteries")
    bpy.context.scene.collection.children.link(col)

    mats = {
        'dark':    build_dark_stone_mat(),
        'arcane':  build_arcane_glow_mat((0.5, 0.2, 1.0)),
        'arcane2': build_arcane_glow_mat((0.1, 0.8, 1.0)),
        'rift':    build_rift_mat(),
        'fog':     build_fog_plane_mat(),
        'cracked': build_cracked_ground_mat(),
        'lantern': build_spectral_lantern_mat(),
        'orb_p':   build_energy_orb_mat((0.5, 0.1, 1.0)),
        'orb_b':   build_energy_orb_mat((0.1, 0.6, 1.0)),
        'cloud':   build_storm_cloud_mat(),
        'rune':    build_rune_crack_mat(),
    }

    objs = []

    # ground
    ground = build_cracked_ground_plane("Atmos_Ground", 24, 22, mats['cracked'])
    ground.location = (0, 0, 0)
    link(col, ground); objs.append(ground)

    # arcane nexus platform (central)
    nexus = build_arcane_nexus("Atmos_Nexus", mats['dark'], mats['rune'])
    nexus.location = (0, 0, 0)
    link(col, nexus); objs.append(nexus)
    add_pt_light(col, (0, 0, 1.0), energy=25.0, color=(0.5, 0.1, 1.0), radius=2.0)

    # portal arches
    arch_configs = [
        ("Atmos_Portal_A", ( 0, 12, 0), (0, 0, 0)),
        ("Atmos_Portal_B", (12,  0, 0), (0, 0, math.pi/2)),
        ("Atmos_Portal_C", (-12, 0, 0), (0, 0, math.pi/2)),
        ("Atmos_Portal_D", ( 0,-12, 0), (0, 0, 0)),
    ]
    for aname, aloc, arot in arch_configs:
        obj_s, obj_r = build_portal_arch(aname, 5.0, 7.0, mats['dark'], mats['rift'])
        obj_s.location = aloc; obj_s.rotation_euler = arot
        obj_r.location = aloc; obj_r.rotation_euler = arot
        link(col, obj_s); link(col, obj_r)
        objs.extend([obj_s, obj_r])
        add_pt_light(col, aloc, energy=12.0, color=(0.3, 0.0, 0.8), radius=1.0)

    # monoliths
    mono_cfgs = [
        ("Atmos_Monolith_A", ( 5, 5, 0), 9.5, mats['dark']),
        ("Atmos_Monolith_B", (-5, 5, 0), 8.0, mats['arcane']),
        ("Atmos_Monolith_C", ( 5,-5, 0), 7.5, mats['dark']),
        ("Atmos_Monolith_D", (-5,-5, 0), 10.0,mats['arcane']),
        ("Atmos_Monolith_E", (10, 0, 0), 6.5, mats['rune']),
        ("Atmos_Monolith_F", (-10,0, 0), 7.0, mats['rune']),
        ("Atmos_Monolith_G", ( 0, 8, 0), 5.5, mats['arcane2']),
        ("Atmos_Monolith_H", ( 0,-8, 0), 6.0, mats['dark']),
    ]
    for mname, mloc, mh, mmat in mono_cfgs:
        mn = build_monolith(mname, mh, 1.1, mmat)
        mn.location = mloc
        link(col, mn); objs.append(mn)
        if mmat == mats['arcane'] or mmat == mats['arcane2'] or mmat == mats['rune']:
            add_pt_light(col, (mloc[0], mloc[1], mh*0.5),
                         energy=rng.uniform(5,12), color=(0.5,0.1,1.0), radius=0.5)

    # floating island fragments
    frag_cfgs = [
        ("Atmos_Fragment_A", (7, 8, 8.0),   3.5, mats['dark']),
        ("Atmos_Fragment_B", (-8, 6, 10.0), 2.8, mats['dark']),
        ("Atmos_Fragment_C", (8,-7, 7.0),   4.0, mats['rune']),
        ("Atmos_Fragment_D", (-7,-8, 9.0),  3.0, mats['arcane']),
        ("Atmos_Fragment_E", (3, 0, 12.0),  2.5, mats['dark']),
        ("Atmos_Fragment_F", (-3, 0, 11.0), 2.0, mats['rune']),
    ]
    for fname, floc, fsize, fmat in frag_cfgs:
        frag = build_floating_fragment(fname, fsize, fmat)
        frag.location = floc
        link(col, frag); objs.append(frag)
        add_pt_light(col, floc, energy=rng.uniform(3,8), color=(0.4,0.1,1.0), radius=0.5)

    # energy orbs
    orb_cfgs = [
        ("Atmos_Orb_A", (0, 0, 6.0), 0.7, mats['orb_p']),
        ("Atmos_Orb_B", (4, 0, 4.5), 0.5, mats['orb_b']),
        ("Atmos_Orb_C", (-4,0, 5.0), 0.5, mats['orb_p']),
        ("Atmos_Orb_D", (0, 4, 4.5), 0.6, mats['orb_b']),
        ("Atmos_Orb_E", (0,-4, 5.5), 0.45,mats['orb_p']),
        ("Atmos_Orb_F", (7, 8, 9.5), 0.4, mats['orb_b']),
        ("Atmos_Orb_G", (-8,6, 11.0),0.35,mats['orb_p']),
    ]
    for oname, oloc, orad, omat in orb_cfgs:
        orb = build_energy_orb(oname, orad, omat)
        orb.location = oloc
        link(col, orb); objs.append(orb)
        add_pt_light(col, oloc, energy=rng.uniform(8,18), color=(0.5,0.1,1.0), radius=orad*0.5)

    # reality tears
    tear_cfgs = [
        ("Atmos_Tear_A", ( 8, 3, 3.0), (0.1, 0, 0.3)),
        ("Atmos_Tear_B", (-8,-3, 2.5), (0.2, 0, 0.8)),
        ("Atmos_Tear_C", ( 3,-9, 4.0), (0,   0, 1.2)),
    ]
    for tname, tloc, trot in tear_cfgs:
        tear = build_reality_tear(tname, mats['rift'])
        tear.location = tloc; tear.rotation_euler = trot
        link(col, tear); objs.append(tear)
        add_pt_light(col, tloc, energy=rng.uniform(6,14), color=(0.3,0.0,0.8), radius=0.4)

    # fog planes at different heights
    fog_cfgs = [
        ("Atmos_Fog_A", ( 0, 0, 0.8), (0,0,0),        16, 14),
        ("Atmos_Fog_B", ( 5, 5, 1.5), (0.05,0,0.3),   10, 8),
        ("Atmos_Fog_C", (-6,-4, 1.2), (0, 0.04, -0.2),12, 9),
    ]
    for fgname, fgloc, fgrot, fgw, fgd in fog_cfgs:
        fg = build_fog_plane(fgname, fgw, fgd, mats['fog'])
        fg.location = fgloc; fg.rotation_euler = fgrot
        link(col, fg); objs.append(fg)

    # storm cloud proxies
    cloud_cfgs = [
        ("Atmos_Cloud_A", ( 0, 0, 18), (0,0,0),   10, 4, 7),
        ("Atmos_Cloud_B", (10, 5, 22), (0,0,0.5),  8, 3, 5),
        ("Atmos_Cloud_C", (-8,-6, 20), (0,0,-0.3), 9, 3, 6),
    ]
    for cname, cloc, crot, cw, ch, cd in cloud_cfgs:
        cl = build_storm_cloud(cname, cw, ch, cd, mats['cloud'])
        cl.location = cloc; cl.rotation_euler = crot
        link(col, cl); objs.append(cl)

    # spectral lanterns
    lantern_locs = [
        ( 4, 4, 5.0), (-4, 4, 4.5), ( 4,-4, 5.5),
        (-4,-4, 4.0), ( 9, 0, 6.0), (-9, 0, 5.5),
    ]
    for li, lloc in enumerate(lantern_locs):
        ln = build_spectral_lantern(f"Atmos_Lantern_{li:02d}", mats['lantern'])
        ln.location = lloc
        link(col, ln); objs.append(ln)
        add_pt_light(col, lloc, energy=rng.uniform(3, 6), color=(0.3,0.8,1.0), radius=0.15)

    print(f"[AtmosphericMysteries] Built {len(objs)} objects.")
    print("Export: File → Export → FBX, apply modifiers and transforms.")

build_scene()
