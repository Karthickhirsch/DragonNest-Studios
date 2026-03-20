# IsleTrial — Blender → Unity Troubleshooting Guide

> **Reference for all 48 Blender scripts in `Blender_Scripts/`**
> Covers every error you can realistically face: Blender script errors,
> shading issues, FBX export problems, Unity import problems, material issues,
> rig/animation issues, and physics issues.

---

## Table of Contents

1. [Blender Script Errors](#1-blender-script-errors)
2. [Blender Shading Issues](#2-blender-shading-issues)
3. [FBX Export Issues](#3-fbx-export-issues)
4. [Unity Import Issues](#4-unity-import-issues)
5. [Unity Material & Shading Issues](#5-unity-material--shading-issues)
6. [Unity Rig & Animation Issues](#6-unity-rig--animation-issues)
7. [Unity Physics Issues](#7-unity-physics-issues)
8. [Performance / Optimization Issues](#8-performance--optimization-issues)
9. [Per-Asset Quick Reference](#9-per-asset-quick-reference)
10. [Master Export Checklist](#10-master-export-checklist)

---

## 1. Blender Script Errors

### ❌ `SyntaxError: invalid syntax`

**Cause:** A line in the script has a Python syntax mistake.

**How to find it:**
```
Blender > Scripting tab > Run Script
Look at the red error in the Info bar at the bottom
The line number is shown: e.g.  File "...", line 756
```

**Common causes and fixes:**

| Bad code | Fixed code | Why |
|---|---|---|
| `(-.1.20, 0, 3.80)` | `(-1.20, 0, 3.80)` | Double decimal point in float |
| `(−0.50, 0, 1.0)` | `(-0.50, 0, 1.0)` | Unicode minus `−` instead of hyphen `-` |
| `rot=(0,0,0` | `rot=(0,0,0)` | Missing closing parenthesis |
| `bm.verts.new(1,2,3)` | `bm.verts.new(Vector((1,2,3)))` | Missing `Vector()` wrapper |

**Quick fix — search for unicode minus in any script:**
```
Open script in Notepad → Edit > Replace
Find:    −   (paste the unicode minus character)
Replace: -   (type a normal hyphen)
Replace All
```

---

### ❌ `AttributeError: 'NoneType' object has no attribute 'name'`

**Cause:** A primitive was added but `bpy.context.active_object` returned `None`.

**Fix:** Add a `bpy.context.view_layer.update()` call before accessing the object:
```python
bpy.ops.mesh.primitive_cube_add(...)
bpy.context.view_layer.update()
obj = bpy.context.active_object
```

---

### ❌ `RuntimeError: Operator bpy.ops.object.mode_set.poll() failed`

**Cause:** `mode_set(mode='EDIT')` called when no object is active.

**Fix:** Always set the active object before changing mode:
```python
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
```

---

### ❌ `KeyError: 'Subsurface Weight'` or `KeyError: 'Emission Strength'`

**Cause:** The script was written for Blender 4.x but you are running Blender 3.x.

**Node input name differences:**

| Blender 4.x input name | Blender 3.x input name |
|---|---|
| `Subsurface Weight` | `Subsurface` |
| `Emission Strength` | `Emission Strength` ✓ (same) |
| `Specular IOR Level` | `Specular` |
| `Transmission Weight` | `Transmission` |
| `Sheen Weight` | `Sheen` |
| `Coat Weight` | `Clearcoat` |

**Fix:** In the failing script, find the `bsdf.inputs[...]` line and change the key:
```python
# Blender 4.x
bsdf.inputs['Subsurface Weight'].default_value = 0.05

# Blender 3.x
bsdf.inputs['Subsurface'].default_value = 0.05
```

> **Recommended:** Use **Blender 4.0 or higher** — all scripts were written for it.

---

### ❌ Script runs but nothing appears in the scene

**Cause:** The `clear_scene()` function ran but `link(col, obj)` failed silently.

**Fix:** Check the Outliner panel. If `IsleTrial_*` collection exists but is empty:
```
Blender > Scripting > Run Script again
Check: Outliner > Collections > IsleTrial_* > (should have objects)
If still empty: check the Console window for any error printed during run
```

---

### ❌ `RecursionError` or script freezes Blender

**Cause:** A loop with too many iterations (e.g. metaball script with many lumps).

**Fix for Cloud scripts (`28_Ocean_AtmosphericProps.py`):**
- The metaball conversion can be slow. Wait up to 60 seconds.
- If Blender freezes permanently: press `Esc`, reduce `lump_count` in the script.

---

## 2. Blender Shading Issues

### ❌ Black / Dark faces on the model

**Cause A — Inverted normals** (most common after Boolean operations)

**How to check:**
```
Viewport > Overlays dropdown > tick "Face Orientation"
Blue faces = correct (outward-facing)
Red faces  = inverted (inward-facing) ← these appear black in render
```

**Fix:**
```
Select All (A)
Mesh menu > Normals > Recalculate Outside   (or Shift+N in Edit Mode)
```

**Cause B — Missing material** — object has no material slot assigned.

**Fix:** Select object → Properties → Material tab → click `+ New` or assign existing.

---

### ❌ Model looks flat / no surface detail

**Cause:** Flat shading is applied instead of Smooth shading.

**Fix:**
```
Select All objects
Right-click > Shade Smooth

Then for crisp hard edges on flat surfaces:
Object Data Properties > Normals > tick "Auto Smooth"
Set angle to 30°
```

---

### ❌ Seams / visible lines between mesh segments

**Cause:** UV seams showing or overlapping UV islands fighting.

**Fix:**
```python
# The smart_uv() function in every script already handles this
# If seams show in render: re-run smart_uv manually:

bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

### ❌ Displacement modifier causes model to fall apart / explode

**Cause:** `DISPLACE` modifier strength is too high, or texture scale is wrong.

**Fix:**
```
Select object > Properties > Modifier tab > Displace
Reduce "Strength" from e.g. 0.55 → 0.15
```

**Affected scripts:** `26_Ocean_Shipwreck.py`, `28_Ocean_AtmosphericProps.py` (Rock Arch), `27_Ocean_WeatherProps.py` (Driftwood bark).

---

### ❌ Boolean cut (arch tunnel) leaves a hole or looks bad

**Cause:** Boolean modifier didn't apply cleanly. Happens with low-poly base mesh.

**Fix:**
```
1. Apply Subdivision Surface modifier first (click ▾ > Apply)
2. Then apply Boolean modifier
3. Then run Recalculate Normals (Shift+N)
```

---

### ❌ Procedural texture looks completely flat / gray

**Cause:** The `[UNITY]` Mix node has `Factor = 1.0` (switched to empty image slot).

**Fix:** In Shader Editor, find the `MixRGB` node labeled "Mix Proc/Image":
```
Set Factor = 0.0   → shows procedural preview  (default)
Set Factor = 1.0   → shows [UNITY] image slot  (for when textures are loaded)
```

---

### ❌ Emission / glow not visible

**Cause:** Viewport is in Solid mode, not Material Preview or Rendered mode.

**Fix:**
```
Press Z > Material Preview   (to see materials)
Press Z > Rendered           (to see full glow/emission)
```

Also check: `Render Properties > Color Management > Exposure` — if too low, emission is invisible.

---

### ❌ Glass / transparent material looks solid pink or white

**Cause:** `blend_method` not set, or Eevee render needs transparency enabled.

**Fix:**
```
Select object > Material Properties
Blend Mode: set to "Alpha Blend"

In Render Properties > Screen Space Reflections > tick "Refraction"
```

For Eevee specifically:
```
Material Properties > Settings > Shadow Mode = "None" (for glass)
```

---

## 3. FBX Export Issues

### ❌ Model comes into Unity at wrong scale (too large or tiny)

**Cause:** Blender's unit scale vs Unity's unit scale mismatch.

**Fix — Always use these FBX export settings:**
```
File > Export > FBX (.fbx)

Transform:
  Scale: 0.01
  Apply Transform: ✓ CHECKED
  Apply Scale: FBX Units Scale

Geometry:
  Apply Modifiers: ✓ CHECKED  (except Cloth — uncheck that)
  Smoothing: Face

Armature:
  Add Leaf Bones: ✗ UNCHECKED  (important for Unity)

Bake Animation: ✗ (unchecked, unless exporting animations)

Forward: -Z Forward
Up:       Y Up
```

---

### ❌ Rig bones are in wrong position after export

**Cause:** Object transformations not applied before export.

**Fix in Blender before export:**
```
Select the ROOT empty + all mesh children
Ctrl+A > Apply > All Transforms

Select the Armature
Ctrl+A > Apply > All Transforms
```

---

### ❌ Cloth sail / torn sail exports as a flat mesh (cloth simulation lost)

**This is intentional.** The Cloth modifier must NOT be applied in Blender.

**Workflow:**
```
Blender: Export FBX with Apply Modifiers = OFF  (don't apply Cloth)
Unity:   Add a "Cloth" component to the imported mesh object
         Set constraint vertices via Unity's Cloth tool
```

---

### ❌ Multiple objects export as one merged mesh

**Fix:** In FBX export dialog:
```
Object Types: ✓ Mesh  ✓ Armature  ✓ Empty
Path Mode: Copy
```

Make sure all objects are parented to the ROOT empty — Unity will respect the hierarchy.

---

### ❌ Particle systems (Small Fish school, VFX Splash) export wrong

**Particle systems do NOT export to FBX.** This is expected.

**Fix for Unity:**
- Export the single fish/droplet mesh
- In Unity: create a `Particle System` component
- Set **Shape > Mesh** = the imported fish mesh
- This replicates the school effect in Unity

---

## 4. Unity Import Issues

### ❌ Model imported but all materials are pink/magenta

**Cause:** Unity can't find materials — this always happens on first import.

**Fix:**
```
Select the FBX in Unity Project window
Inspector > Materials tab
Click "Extract Materials" button
Unity creates .mat files in your project
Now assign shaders (see Section 5 below)
```

---

### ❌ "The associated script cannot be found" warning

**This is not related to the 3D models.** This is a C# script reference issue.
Ignore it for the art pipeline — models will still work.

---

### ❌ Model appears completely white after import

**Cause:** Default Unity material with no textures assigned.

**Fix:** Assign the correct shader and PBR textures (see Section 5).

---

### ❌ Humanoid rig shows "Avatar Configuration has errors" (red bones)

**Cause:** Bone names don't perfectly match Unity's Humanoid requirements.

**All humanoid rigs in this project use Unity-standard naming:**
```
Hips, Spine, Chest, Neck, Head
UpperArm.L / UpperArm.R
LowerArm.L / LowerArm.R
Hand.L     / Hand.R
UpperLeg.L / UpperLeg.R
LowerLeg.L / LowerLeg.R
Foot.L     / Foot.R
```

**Fix if red bones appear:**
```
Inspector > Rig > Avatar Definition > Configure...
Drag missing bones from the bone list into the red slots manually
Click Done
```

---

### ❌ Model is rotated 90 degrees in Unity (facing down or sideways)

**Cause:** Blender's forward axis (-Y) vs Unity's forward axis (+Z).

**Fix — Option A (recommended, do in Blender):**
```
FBX export settings:
  Forward: -Z Forward
  Up: Y Up
```

**Fix — Option B (in Unity):**
```
Select FBX > Inspector > Model tab
Bake Axis Conversion: ✓ CHECKED
```

---

### ❌ Multiple FBX objects appear as a single mesh in Unity

**Cause:** Objects were not properly parented or not named correctly.

**Fix:** In Blender, make sure every object's parent is the `*_ROOT` empty.
The Unity hierarchy will mirror the Blender parent-child structure exactly.

---

## 5. Unity Material & Shading Issues

### ❌ Choosing the right shader for your render pipeline

| Render Pipeline | Correct Shader |
|---|---|
| **Built-in** (default Unity) | `Standard` |
| **URP** | `Universal Render Pipeline/Lit` |
| **HDRP** | `HDRP/Lit` |

> Check your pipeline: `Edit > Project Settings > Graphics > Scriptable Render Pipeline`

---

### ❌ Assigning PBR textures to each material

Every material in the scripts has `[UNITY]` named image slots.
These tell you exactly what textures to assign in Unity.

**Naming convention:**
```
[UNITY] Mat_Kael_Coat_Albedo     → drag to Base Color / Albedo slot
[UNITY] Mat_Kael_Coat_Normal     → drag to Normal Map slot
[UNITY] Mat_Kael_Coat_Roughness  → drag to Metallic/Smoothness slot (invert for Smoothness)
```

**Workflow per material:**
```
1. Select .mat file in Project window
2. Inspector > Shader > set to URP/Lit (or Standard)
3. Base Map       → assign [MatName]_Albedo.png
4. Normal Map     → assign [MatName]_Normal.png
5. Metallic Map   → assign [MatName]_Roughness.png
6. Emission       → assign [MatName]_Emission.png (glowing objects only)
```

---

### ❌ Normal map makes the surface look inverted / bumps go wrong direction

**Cause:** Blender exports OpenGL normal maps, Unity expects DirectX format.

**Fix — In Unity texture import settings:**
```
Project window > select Normal Map texture
Inspector:
  Texture Type: Normal Map   ← IMPORTANT
  Flip Green Channel: ✓ CHECKED
  Click Apply
```

---

### ❌ Roughness map makes everything shiny when it should be rough

**Cause:** Unity's Smoothness = `1 - Roughness`. The values are inverted.

**Fix — Option A:** In your texture tool (Photoshop / Substance), invert the roughness map before saving.

**Fix — Option B:** In Unity material:
```
Inspector > Surface Inputs > Smoothness Source = "Metallic Alpha"
Smoothness value: drag slider to 0 (fully rough)
```

---

### ❌ Glow / emission not visible in Unity

**Cause:** Emission not enabled on the material, or Post Processing Bloom not active.

**Fix — Material side:**
```
Inspector > Emission > tick the checkbox
Set Emission Color and HDR intensity (value > 1 for bloom)
```

**Fix — Post Processing:**
```
Main Camera > Add Component > Volume
Profile > Add Override > Bloom
Enable Bloom, set Threshold and Intensity
```

**Glowing objects in this project:**
- All compass needles and compass faces
- Bioluminescent elements (Kraken blade, Coral Titan cracks)
- Boss soul wisps (Dread Admiral)
- Lantern light points (`*_LightPoint` empties → add Unity `Light` component)
- Buoy signal lights
- Kael's iris eyes (subtle glow)

---

### ❌ Transparent / alpha materials show wrong sorting (objects visible through walls)

**Cause:** Transparent render queue ordering issue.

**Fix:**
```
Inspector > Surface Type: Transparent
Render Face: Both  (double-sided for torn sail / cloth)
Sorting Priority: increase value for objects that should render on top
```

---

### ❌ Water / ocean surface shader not working

**Cause:** The `29_Ocean_SurfaceReference.py` creates a reference plane only.
Unity needs a proper water shader — the exported mesh is just for placement/scale.

**Fix:**
```
Option A: Unity Asset Store > "Stylized Water 2" (free URP version)
Option B: Shader Graph > create a wave-animated vertex displacement shader
Option C: Use the OceanBuoyancy.cs already in Code/Boat/ — it references a water surface
```

---

## 6. Unity Rig & Animation Issues

### ❌ Animations from Mixamo don't map to Kael / Mushroom NPC

**Cause:** Mixamo requires the model to be re-uploaded for retargeting.

**Fix — Full Mixamo workflow:**
```
1. Export Kael_Character.fbx from Blender (with rig, no animation)
2. Go to mixamo.com > Upload Character
3. Mixamo auto-rigs (use the existing Humanoid rig)
4. Download any animation: Format=FBX, Skin=Without Skin
5. In Unity: drag animation FBX into Animator Controller
```

---

### ❌ Character's hands/feet slide during animation (foot sliding)

**Cause:** Root motion not enabled, or IK targets not set.

**Fix:**
```
Animator Controller > select clip > Inspector
Root Transform Rotation: Bake Into Pose ✓
Root Transform Position Y: Bake Into Pose ✓
Root Transform Position XZ: leave unchecked (for root motion)
```

---

### ❌ Generic rig (bosses, sea creatures, boat) shows no animation slots

**Cause:** Generic rigs don't use Humanoid mapping — animations must be directly assigned.

**Fix:**
```
Inspector > Rig > Animation Type = Generic
Root node: select the ROOT bone (e.g. Boss_Root, Fish_Root, Hull_Bone)
Animator Controller: create clips that reference specific bone names
```

---

### ❌ Boat rudder / compass rose / cannon don't animate

**Cause:** These are controlled by specific bones in the rig scripts.

**Bone names to target in Animator:**
```
Rudder_Bone       → rotate Z axis  (-45° to +45°)
CompassRose_Spin  → rotate Y axis  (continuous spin)
CannonL_Pitch     → rotate X axis  (-15° to +25°)
CannonR_Pitch     → rotate X axis
Anchor_IK_Target  → translate Z    (lower anchor)
```

---

### ❌ Shape keys (blend shapes) not visible in Unity

**Cause:** Shape keys are exported correctly but need to be referenced by name.

**How to use in Unity:**
```csharp
SkinnedMeshRenderer smr = GetComponent<SkinnedMeshRenderer>();

// Fish swim animation
smr.SetBlendShapeWeight(smr.sharedMesh.GetBlendShapeIndex("Swim_Left"),  value);
smr.SetBlendShapeWeight(smr.sharedMesh.GetBlendShapeIndex("Swim_Right"), value);

// Whale breach
smr.SetBlendShapeWeight(smr.sharedMesh.GetBlendShapeIndex("Breach_Arch"), value);

// Shark attack
smr.SetBlendShapeWeight(smr.sharedMesh.GetBlendShapeIndex("Attack_Open"), value);
```

**Shape key names per asset:**
| Asset | Shape Key Names |
|---|---|
| Large Fish | `Swim_Left`, `Swim_Right`, `Mouth_Open`, `Idle_Breathe` |
| Whale | `Breach_Arch`, `Dive_Curve`, `Tail_Up`, `Mouth_Open` |
| Shark | `Attack_Open`, `Swim_Curve_L`, `Swim_Curve_R`, `Gill_Flare` |
| Small Fish | `Swim_L`, `Swim_R` |

---

## 7. Unity Physics Issues

### ❌ Boat doesn't float — sinks or flies upward

**Cause:** Buoyancy float empties not connected to `OceanBuoyancy.cs`.

**Fix:**
```
1. On the Mushroom Boat prefab, find the Float_* empties:
   Float_Bow_L, Float_Bow_R, Float_Mid_L, Float_Mid_R
   Float_Stern_L, Float_Stern_R
2. In OceanBuoyancy.cs inspector > Float Points array
3. Drag each Float_* empty into the array
4. Set WaterLevel = 0 (matches Ocean_Buoyancy_Plane Y=0)
```

---

### ❌ Sail cloth tears / explodes in Unity physics

**Cause:** Cloth constraints not set — all vertices are free.

**Fix:**
```
Select Debris_Sail_Torn in scene
Inspector > Cloth component
Open "Edit Cloth Constraints" (the paint tool icon)
Paint the top edge vertices as Max Distance = 0  (pinned/fixed)
Paint the rest as Max Distance = 0.1 – 0.3
```

---

### ❌ Seagulls fall through the ocean / don't fly

**Cause:** Seabird meshes have no movement script.

**Fix — Simple flight script:**
```csharp
// Attach to SeaBird_Silhouette_A/B/C
void Update() {
    // Circle flight path
    float t = Time.time * flightSpeed;
    transform.position = new Vector3(
        Mathf.Cos(t) * radius,
        baseHeight + Mathf.Sin(t * 0.5f) * 2f,
        Mathf.Sin(t) * radius);
    transform.LookAt(transform.position + new Vector3(-Mathf.Sin(t), 0, Mathf.Cos(t)));
}
```

---

### ❌ Small fish school not working as GPU instances

**Fix:**
```
1. Import 18_SmallFish.fbx into Unity
2. Create a Material with GPU Instancing enabled:
   Inspector > Enable GPU Instancing: ✓
3. Particle System > Renderer tab:
   Render Mode: Mesh
   Mesh: SmallFish_Body
   Material: (instanced material)
4. Emission: 200–500 particles
5. Shape: Sphere, radius 5
```

---

## 8. Performance / Optimization Issues

### ❌ Game FPS drops when many models are visible

**PC target (primary):** Should maintain 60 FPS

**Quick fixes:**

| Problem | Fix |
|---|---|
| Too many high-poly objects visible | Add LOD Group component, reduce verts at distance |
| Subdivision too high | In Blender, set Subsurf level = 1 for export |
| Too many real-time lights | Bake lighting for static objects (Lightmapping) |
| Too many draw calls | Enable GPU Instancing on repeated props |
| Boss models complex | Only spawn one boss at a time |

**Polycount targets per asset category:**

| Category | Target Triangles |
|---|---|
| Player (Kael) | 5,000 – 8,000 |
| NPCs (Mushroom, Compass) | 4,000 – 7,000 |
| Bosses | 8,000 – 15,000 |
| Sea Creatures (large) | 5,000 – 10,000 |
| Small Fish (instanced) | 400 – 800 |
| Props (barrels, crates) | 200 – 800 |
| Environment (dock, island) | 10,000 – 25,000 |
| Shipwreck (hero asset) | 15,000 – 30,000 |

---

### ❌ Mobile performance too low (secondary target)

**Mobile-specific fixes:**

```
Texture resolution: reduce 2048×2048 → 1024×1024 in Unity import settings
Subdivision: apply at level 1 instead of level 2 before FBX export
Shadows: disable real-time shadows on all non-player objects
LOD: mandatory for all environment objects (LOD0/LOD1/LOD2)
Batching: Enable Static Batching on non-moving environment props
Particle limit: max 100 particles per system on mobile
```

---

## 9. Per-Asset Quick Reference

| Script | Rig Type | Shading Notes | Unity Notes |
|---|---|---|---|
| `01_Boat_MainVessel.py` | None (use `01_Boat_Rig.py`) | Check sail normals | Rigidbody + OceanBuoyancy.cs |
| `03_Kael_Model.py` | Humanoid (`03_Kael_Rig.py`) | 3-layer eyes: assign separate mats | Mixamo retarget OK |
| `04_MushroomNPC.py` | Humanoid Rig | Cap has procedural spore glow | MushroomCap_Wobble bone for idle |
| `05_CompassNPC.py` | Humanoid Rig | Compass face emission = 1.0 | CompassRose_Spin bone: add driver |
| `06_BirdSkeleton.py` | Generic Rig | Check wing normals (thin faces) | IK on wings: 3-bone chain |
| `07_MimicChest.py` | Generic Rig | Teeth are separate mesh objects | Lid_Bone: 0°→80° for attack |
| `08_MushroomBoat.py` | Generic Vehicle Rig | Hull boolean = apply before export | 6 Float_* empties → OceanBuoyancy |
| `10_Boss_MyceliumKing.py` | Generic Boss Rig | 12 compound eyes: emission mats | Spore VFX: use Boss_MyceliumKing_VFX empties |
| `15_LargeFish.py` | Generic Fish Rig | Iridescence: check Blender 4.x | Shape keys: Swim_Left/Right |
| `16_Whale.py` | Generic Fish Rig | Vertex paint for belly (manual step) | Breach_Arch shape key for jump |
| `17_Shark.py` | Generic Fish Rig | Ampullae pores: tiny sphere objects | Gill_Flare shape key |
| `18_SmallFish.py` | Minimal 4-bone | Bright tropical: no bump needed | GPU Instancing required |
| `19_Weapon_AncientTrident.py` | None (weapon) | Bioluminescent gem: emission | Attach_Hand empty → hand bone |
| `24_Prop_SoulCompass.py` | None (prop) | Soul wisps: emission + alpha | Trigger collider for pickup |
| `25_Ocean_Buoys.py` | None | Chain: apply Boolean before export | LightPoint_* empty → Point Light |
| `26_Ocean_Shipwreck.py` | None | Apply Displace before export | MeshCollider (convex = false) |
| `28_Ocean_AtmosphericProps.py` | None | Rock Arch: apply Boolean + Displace | Kelp Bulb: Rigidbody + Float script |
| `29_Ocean_SurfaceReference.py` | None | Reference only — delete before export | Use for shader alignment, then delete |

---

## 10. Master Export Checklist

Run through this for every model before importing to Unity.

### In Blender

```
□ Run script → confirm objects appear in Outliner
□ Open "Face Orientation" overlay → confirm all faces are BLUE
□ Select all → Right-click → Shade Smooth
□ Object Data Properties → Normals → Auto Smooth → 30°
□ Apply all modifiers EXCEPT:
    - Cloth modifier (keep for Unity physics)
    - Subdivision modifier (keep for level-of-detail flexibility)
□ Apply all transforms: Ctrl+A → All Transforms
□ Confirm ROOT empty exists and all objects are children of it
□ Confirm UV maps exist: UV Editing workspace → check UVs are unwrapped
□ Check scale: ROOT should be at (0,0,0), scale (1,1,1), rotation (0,0,0)
□ Delete the WaterlineRef plane (29_Ocean_SurfaceReference) before export
```

### FBX Export Settings

```
□ File > Export > FBX
□ Scale: 0.01
□ Apply Transform: ✓
□ Apply Scale: FBX Units Scale
□ Forward: -Z Forward
□ Up: Y Up
□ Object Types: ✓ Mesh, ✓ Armature, ✓ Empty
□ Apply Modifiers: ✓ (except Cloth)
□ Add Leaf Bones: ✗ UNCHECKED
□ Smoothing: Face
□ Filename: use asset name (e.g. Kael_Character.fbx, MushroomBoss.fbx)
```

### In Unity

```
□ Import FBX → Inspector > Model > Scale Factor: 1.0
□ Inspector > Rig:
    - Humanoid characters: Animation Type = Humanoid
    - Everything else: Animation Type = Generic → set Root Node
□ Inspector > Materials > Extract Materials
□ Assign correct shader to each material (URP Lit / Standard / HDRP Lit)
□ For each material: assign Albedo, Normal, Roughness textures
□ Normal maps: set Texture Type = Normal Map, Flip Green Channel ✓
□ Glowing parts: enable Emission on material, set HDR color
□ For LightPoint_* empties: Add > Light > Point Light
□ For Float_* empties: add to OceanBuoyancy.cs float points array
□ Test in Play mode: check scale, orientation, shading, no pink materials
```

---

## Quick Error Lookup

| You see this | Go to section |
|---|---|
| `SyntaxError` in Blender console | [1.1](#-syntaxerror-invalid-syntax) |
| `KeyError: 'Subsurface Weight'` | [1.4](#-keyerror-subsurface-weight-or-keyerror-emission-strength) |
| Black faces on model | [2.1](#-black--dark-faces-on-the-model) |
| Model looks flat/no detail | [2.2](#-model-looks-flat--no-surface-detail) |
| Wrong scale in Unity | [3.1](#-model-comes-into-unity-at-wrong-scale-too-large-or-tiny) |
| All materials pink/magenta | [4.1](#-model-imported-but-all-materials-are-pinkmagenta) |
| Normal map looks inverted | [5.3](#-normal-map-makes-the-surface-look-inverted--bumps-go-wrong-direction) |
| Glow not visible | [5.5](#-glow--emission-not-visible-in-unity) |
| Humanoid rig has red bones | [4.4](#-humanoid-rig-shows-avatar-configuration-has-errors-red-bones) |
| Mixamo animations don't fit | [6.1](#-animations-from-mixamo-dont-map-to-kael--mushroom-npc) |
| Boat sinks / flies | [7.1](#-boat-doesnt-float--sinks-or-flies-upward) |
| FPS dropping | [8.1](#-game-fps-drops-when-many-models-are-visible) |

---

*IsleTrial Project — Blender Scripts v1.0 | 48 scripts covering 30+ unique assets*
*Render Pipeline: URP recommended | Blender Version: 4.0+ required*
