# Toran Soul Guardian — Mesh to Rig Binding Guide
**IsleTrial Project | Blender 4.x**

This guide walks you through every step of combining the detailed Toran mesh
(`46_NPC_Toran_SoulGuardian.py`) with the Toran rig
(`46_NPC_Toran_SoulGuardian_Rig.py`) inside Blender, then exporting a
game-ready FBX for Unity.

---

## Overview of What We Are Doing

```
Step 1 → Run Rig script         (creates armature + placeholder body)
Step 2 → Run Model script       (creates detailed mesh in same scene)
Step 3 → Delete placeholder     (remove the simple box body)
Step 4 → Position mesh on rig   (align model to armature T-pose)
Step 5 → Parent mesh to armature (bind with weights)
Step 6 → Fix weight painting    (check and clean up automatic weights)
Step 7 → Test with poses        (verify no broken deformation)
Step 8 → Export FBX for Unity
```

---

## Prerequisites

- Blender **4.0** or later installed
- Both script files in your Blender_Scripts folder:
  - `46_NPC_Toran_SoulGuardian_Rig.py`
  - `46_NPC_Toran_SoulGuardian.py`
- A new empty Blender project (File → New → General)

---

## Step 1 — Run the Rig Script

1. Open Blender → go to the **Scripting** workspace tab (top menu bar).
2. Click **Open** in the text editor panel.
3. Navigate to your `Blender_Scripts` folder and open
   `46_NPC_Toran_SoulGuardian_Rig.py`.
4. Click **▶ Run Script** (the play button, or press `Alt+P`).
5. You will see in the 3D Viewport:
   - An orange skeleton (`Toran_Armature`) in T-pose
   - A grey box-shaped placeholder body (`Toran_Body`)

> **What to check:** Open the Blender System Console
> (Window → Toggle System Console on Windows) and confirm you see
> `IsleTrial — Toran Soul Guardian Rig Report` printed with all 22
> Unity humanoid bones marked `✓`.

---

## Step 2 — Run the Model Script (in the SAME scene)

> ⚠️ **Do NOT click "New File" or "Clear Scene".** You must keep the
> armature that was just created.

1. In the Scripting workspace, click **Open** again.
2. Open `46_NPC_Toran_SoulGuardian.py`.
3. **Before running**, scroll to the very top of the script and find the
   `clear_scene()` call inside `main()`:

   ```python
   def main():
       clear_scene()   ← FIND THIS LINE
       ...
   ```

4. **Comment out** or **delete** the `clear_scene()` call so it reads:

   ```python
   def main():
       # clear_scene()   ← commented out — we keep the rig
       ...
   ```

5. Click **▶ Run Script**.
6. The detailed Toran mesh objects will now appear in the scene alongside
   the armature and placeholder.

> **What you should see in the Outliner (top-right panel):**
> ```
> Toran_Armature
> Toran_Body          ← placeholder (will be deleted in Step 3)
> Toran_Head
> Toran_Torso
> Toran_Coat
> Toran_Legs
> Toran_Boots
> Toran_Belt
> Toran_Chains (x6)
> Toran_GhostAura
> Toran_CompassBlade
> ... (all detailed mesh objects)
> ```

---

## Step 3 — Delete the Placeholder Body

1. In the **Outliner** (top-right), find `Toran_Body`.
2. Click it to select it.
3. Press **X** → **Delete** to remove it.

The placeholder is gone. The detailed mesh objects remain.

---

## Step 4 — Align the Detailed Mesh to the Armature

The detailed mesh is already authored at 1.82 m height in T-pose, so it
should align almost perfectly. Verify this:

1. Press **Numpad 1** to enter Front Orthographic view.
2. Click on the armature (`Toran_Armature`) to select it.
3. Press **H** to hide it temporarily.
4. Select all mesh objects: click one, then press **A** to select all.
5. Check the mesh looks like a proper T-pose humanoid at ~1.82 m.

**If the mesh is misaligned:**

1. Unhide the armature: press **Alt+H**.
2. Select all mesh objects (click one → press A).
3. Press **G** (grab), then move to align.
   - **G + Z** constrains movement to vertical.
   - **G + X** constrains to horizontal.
4. When aligned, press **Enter** to confirm.

**Check scale is correct:**

1. Select the armature.
2. Press **N** to open the side panel → **Item** tab.
3. Confirm Scale X, Y, Z are all **1.0**.
4. If not: press **Ctrl+A** → **Apply All Transforms**.
5. Do the same for each mesh object.

---

## Step 5 — Parent the Mesh Objects to the Armature

This is the core binding step. We will parent every mesh object to the
armature so the bones control the mesh.

### Method A — Parent All at Once (Recommended)

1. In the **Outliner**, select all mesh objects by clicking the first one,
   then holding **Shift** and clicking the last one.
   Include: Head, Torso, Coat, Legs, Boots, Belt, all detail pieces.

   > Do **NOT** include the Soul Chains or GhostAura at this stage —
   > these are handled separately in Step 5B.

2. Hold **Shift** and click `Toran_Armature` last (it must be the
   **active** object — highlighted brighter than the others).

3. Press **Ctrl+P** → a menu appears → choose:
   ```
   ▶ With Automatic Weights
   ```

4. Blender calculates vertex weights automatically. This may take
   5–15 seconds depending on mesh complexity.

5. A message `Automatic Weights` confirms success.
   If you see `Bone Heat Weighting Failed`, see the Troubleshooting
   section at the end of this guide.

### Method B — Parent Soul Chains to Their Bones

The 6 soul chain mesh objects should follow specific bones, not the full
body weight system.

For **each** soul chain (`SoulChain_Chest_L`, `SoulChain_Chest_R`,
`SoulChain_Arm_L`, `SoulChain_Arm_R`, `SoulChain_Leg_L`, `SoulChain_Leg_R`):

1. Click the corresponding chain mesh object in the Outliner.
2. Then **Shift+click** the `Toran_Armature`.
3. Press **Ctrl+P** → **Bone** (not Automatic Weights).
4. In the popup, type the matching bone name, for example:
   `SoulChain_Chest_L`.
5. Repeat for all 6 chains.

### Method C — Parent GhostAura to GhostAura Bone

1. Select `Toran_GhostAura` mesh.
2. Shift+click `Toran_Armature`.
3. Press **Ctrl+P** → **Bone** → type `GhostAura`.

---

## Step 6 — Fix Weight Painting (Critical for Good Deformation)

Automatic weights are a starting point. You must check and fix problem
areas, especially:

- **Shoulders** — often bleed weight between torso and arm
- **Hips/waist** — coat fabric may fold incorrectly
- **Neck/head** — hair or collar may distort

### How to Check Weights

1. Select `Toran_Torso` (or whichever mesh you want to check).
2. In the top-left dropdown change mode from **Object Mode** → **Weight Paint**.
3. The mesh turns blue (0 = no influence) to red (1 = full influence).
4. In the **N panel** (press N) → **Item** tab → expand **Vertex Groups**.
5. Click a bone name in the list (e.g., `Spine`) to see its weight map.
   - Red = fully controlled by this bone
   - Blue = not controlled by this bone

### How to Fix Weights

Select the armature → enter **Pose Mode** → rotate a bone to see live
deformation, then fix by:

**Adding weight:**
1. Back in Weight Paint mode on the mesh.
2. Set **Weight** slider to 1.0, **Radius** and **Strength** as needed.
3. Paint red on areas that should follow this bone.

**Removing weight:**
1. Set **Weight** to 0.0.
2. Paint over areas that should NOT follow this bone.

**Auto-normalize** (recommended):
1. In Weight Paint mode → Properties panel on the right → **Options**.
2. Enable **Auto Normalize** so total weights always add up to 1.0.

### Common Fixes Table

| Problem | Bone to fix | Fix |
|---|---|---|
| Torso folds at shoulder when arm lifts | `LeftShoulder` / `LeftUpperArm` | Increase LeftShoulder weight near armpit |
| Coat clips through legs when walking | `LeftUpperLeg` | Reduce leg weight on coat bottom hem |
| Head stretches neck | `Neck` / `Head` | Ensure clean falloff at chin line |
| Chain floats away from body | `SoulChain_*` | Re-parent with **Bone** method (Step 5B) |
| Fingers look stiff | Finger proximal bones | Paint weight onto each finger segment |

---

## Step 7 — Test with Poses

Before export, verify the rig deforms correctly by posing it.

1. Click `Toran_Armature` → switch to **Pose Mode** (Ctrl+Tab or top dropdown).
2. Press **A** to select all bones.
3. Try these test poses:

**Walk test:**
- Select `LeftUpperLeg` → press **R+X** → type `30` → Enter (rotate 30° forward)
- Select `RightUpperLeg` → press **R+X** → type `-30` → Enter
- Look for mesh tearing at hips, crotch area

**Arm raise test:**
- Select `LeftUpperArm` → press **R+Z** → type `90` → Enter (lift arm 90°)
- Check shoulder area for skin breakage

**Soul chain test:**
- Select `SoulChain_Chest_L` → press **R+Y** → type `45` → Enter
- The chain mesh should rotate in place without dragging the torso

**Reset pose when done:**
- Press **A** (select all) → **Alt+R** (reset rotation) → **Alt+G** (reset position)

---

## Step 8 — Export FBX for Unity

Once weights are clean and poses look correct, export the combined rig + mesh.

### Export Settings

1. **File → Export → FBX (.fbx)**
2. Configure the right panel:

```
Include
  ☑ Limit to: Selected Objects (optional, if you want only Toran)
  ☑ Object Types: Armature, Mesh

Transform
  Scale: 1.00
  Apply Scalings: FBX Units Scale
  ☑ Apply Unit
  Forward: -Z Forward
  Up: Y Up
  ☑ Apply Transform

Geometry
  Smoothing: Face
  ☑ Apply Modifiers

Armature
  ☑ Add Leaf Bones: OFF (uncheck this)
  Primary Bone Axis: Y Axis
  Secondary Bone Axis: X Axis

Animation
  ☑ Baked Animation (only if you have keyframes)
```

3. Name the file: `Toran_SoulGuardian.fbx`
4. Click **Export FBX**.

---

## Step 9 — Import into Unity

1. Copy `Toran_SoulGuardian.fbx` into your Unity project's
   `Assets/Models/Characters/` folder.
2. Click the file in the Project panel → **Inspector** opens.
3. Go to the **Rig** tab:
   - Animation Type: **Humanoid**
   - Avatar Definition: **Create From This Model**
   - Click **Configure...** to verify all 22 bones are auto-mapped (green)
4. Go to the **Materials** tab:
   - Location: **Use External Materials (Legacy)** or create a material
     mapping for each PBR material slot.
5. Click **Apply**.

### Unity Script Setup for Soul Chains

The soul chain bones need a C# script to animate them breaking.
In Unity, on the Toran GameObject, find the `TorianBossController.cs`
component and assign the 6 chain `Transform` references in the Inspector:

```
Soul Chain Bones (drag from Hierarchy):
  Soul Chain Chest L  →  Toran_Armature/Root/Hips/.../SoulChain_Chest_L
  Soul Chain Chest R  →  Toran_Armature/Root/Hips/.../SoulChain_Chest_R
  Soul Chain Arm L    →  ...SoulChain_Arm_L
  Soul Chain Arm R    →  ...SoulChain_Arm_R
  Soul Chain Leg L    →  ...SoulChain_Leg_L
  Soul Chain Leg R    →  ...SoulChain_Leg_R
```

The script will animate their `localScale` from `Vector3.one → Vector3.zero`
when each chain is destroyed during Phase 3.

---

## Troubleshooting

### "Bone Heat Weighting Failed"

This happens when mesh geometry has internal faces or is too close to bones.

**Fix:**
1. Select the problem mesh.
2. Switch to Edit Mode (Tab).
3. Press **M → Merge by Distance** (removes duplicate vertices).
4. Press **Alt+N → Recalculate Outside** (fixes inverted normals).
5. Switch back to Object Mode.
6. Retry the parent operation (Ctrl+P → With Automatic Weights).

### Mesh Does Not Follow Bones at All

The mesh has been parented but without proper vertex groups.

**Fix:**
1. Select the mesh → Object Properties (orange square icon in Properties panel).
2. Scroll down to **Relations** → check **Parent** is `Toran_Armature` and
   **Parent Type** is `Armature`.
3. If not, redo the Ctrl+P step.

### Mesh Deforms Wildly When a Bone Rotates

The vertex group for that bone has extreme weights in unexpected areas.

**Fix:**
1. Enter **Weight Paint** mode on the mesh.
2. In N panel → select the bone's vertex group.
3. Click **Weights → Smooth** (in the top bar) to blur the weights.
4. Alternatively, use a **Normalize All** operation:
   Weights menu → Normalize All.

### Soul Chain Floats Off the Body

The chain mesh was parented to Armature with automatic weights instead
of to the specific bone.

**Fix:**
1. Select the chain mesh → right-click → **Clear Parent** (Alt+P → Clear).
2. Re-parent using **Ctrl+P → Bone** and type the exact bone name.

### Wrong Scale in Unity (Toran appears 100x too big or small)

**Fix in Blender:**
1. Select everything (A).
2. Ctrl+A → **Apply All Transforms**.
3. Re-export FBX with Scale: 1.0.

**Fix in Unity:**
1. Select the FBX in Project panel → Rig tab.
2. Change **Scale Factor** from 100 to 1 → Apply.

---

## Quick Reference — Keyboard Shortcuts Used

| Action | Shortcut |
|---|---|
| Run script | Alt+P |
| Select all | A |
| Delete selected | X |
| Grab/move | G |
| Rotate | R |
| Constrain to axis | G/R then X, Y, or Z |
| Confirm action | Enter |
| Cancel action | Esc or Right-click |
| Parent menu | Ctrl+P |
| Clear parent | Alt+P |
| Hide selected | H |
| Unhide all | Alt+H |
| Toggle Edit/Object mode | Tab |
| Toggle Pose/Object mode | Ctrl+Tab |
| Reset rotation in Pose | Alt+R |
| Reset position in Pose | Alt+G |
| Side panel (N panel) | N |
| Front view | Numpad 1 |
| Side view | Numpad 3 |
| Top view | Numpad 7 |

---

## Final Checklist Before Handing Off to Unity

```
☐  Rig script ran — all 22 Unity humanoid bones confirmed ✓
☐  Model script ran in same scene (clear_scene commented out)
☐  Placeholder Toran_Body deleted
☐  All body mesh objects parented to armature (Ctrl+P → Auto Weights)
☐  Soul chains parented to their specific bones (Ctrl+P → Bone)
☐  GhostAura parented to GhostAura bone (Ctrl+P → Bone)
☐  Weight paint verified — no wild deformation on arm raise / leg lift
☐  All transforms applied (Ctrl+A → Apply All Transforms)
☐  FBX exported with Y Up, -Z Forward, Scale 1.0, No Leaf Bones
☐  Unity Rig Type set to Humanoid, all bones auto-mapped green
☐  Soul chain Transform references assigned in TorianBossController
```

---

*Guide version 1.0 — IsleTrial Project*
