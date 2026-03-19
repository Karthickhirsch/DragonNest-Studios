# IsleTrial — Blender Model Generation Prompts
## How to Use These Prompts to Generate 3D Models with AI

---

## What Is This Folder?

This folder contains **AI prompts** designed to generate complete Blender Python scripts.
Instead of creating 3D models manually, you:
1. Copy a prompt from these files
2. Give it to an AI (ChatGPT, Claude, Gemini, Copilot)
3. AI writes the Blender Python code
4. You run the code in Blender → 3D model appears
5. Export as FBX → Import into Unity

---

## Prompt Files Overview

| File | What It Creates | Priority |
|---|---|---|
| `01_Boat_MainVessel.md` | Player boat (hull, cabin, mast, harpoon, lantern, anchor) | HIGH — Do First |
| `02_Environment_Island_Dock.md` | Island terrain, cliffs, dock/pier, rocks, lighthouse | HIGH |
| `03_Props_And_Pickups.md` | Harpoon projectile, barrels, crates, treasure chest, lanterns, rope | MEDIUM |
| `04_Sea_Creatures.md` | Fish, whale, shark, small fish school (with armatures) | MEDIUM |
| `05_Ocean_And_Weather_Assets.md` | Buoys, shipwreck, storm debris, ocean reference mesh | LOW — Do Last |

---

## Step-by-Step: How to Use a Prompt

### Step 1 — Open the prompt file
Open any `.md` file in this folder and find the code block marked:
```
Write a complete Blender Python (bpy) script to create...
```

### Step 2 — Copy the full prompt
Copy everything inside that code block (the entire prompt text).

### Step 3 — Open your AI of choice
Best options (ranked):
1. **Claude** (claude.ai) — Best at long structured scripts
2. **ChatGPT GPT-4o** — Great for Blender scripts, widely tested
3. **GitHub Copilot** — Good if you want inline suggestions

### Step 4 — Paste prompt + add this prefix
Before pasting, add this line at the start:

```
You are an expert Blender Python developer. Write production-ready bpy code.
Make sure all code is Blender 4.x compatible and runs without errors.
Use bmesh for geometry creation where possible for better control.

[PASTE PROMPT HERE]
```

### Step 5 — Run in Blender
1. Open Blender (version 4.0 or higher recommended)
2. Go to **Scripting** tab (top menu)
3. Click **New** to create a new script
4. **Paste** the generated code
5. Click **Run Script** (▶ button) or press `Alt + P`
6. Watch the model appear in the 3D viewport!

### Step 6 — Fix errors (if any)
If Blender shows an error in the bottom info bar:
- Copy the error message
- Go back to AI: "I got this error: [paste error]. Fix the script."
- AI will correct and return fixed code

### Step 7 — Export to Unity
1. In Blender: select the ROOT empty object
2. Go to `File → Export → FBX (.fbx)`
3. Settings:
   - Scale: `0.01` (Blender meters → Unity centimeters correction)
   - Apply Transform: ✓ ON
   - Include: Mesh + Armature (if creature)
   - Forward: `-Z Forward`
   - Up: `Y Up`
4. Save to: `c:\Users\skarthick-a\Videos\DG_Project\Assets\Models\`

---

## AI Tips for Better Results

### If the code is too long and AI cuts it off:
```
Continue from where you stopped. Start from the section: [last section name]
```

### If a specific part looks wrong:
```
The [object name] geometry looks wrong. Rewrite only that section.
Keep all other parts the same.
```

### If you want variations:
```
Give me 3 variations of the [object] with different sizes/styles.
Keep the same code structure but change: [what to change]
```

### To add more detail after basic model is done:
```
The base model is created. Now add more detail to [object]:
- [specific detail 1]
- [specific detail 2]
Use the existing object named "[name]" already in the scene.
```

---

## Model Priority Order for IsleTrial

Build in this order (each builds on the previous):

```
Week 1: Boat (01) → Test in Unity with BoatController.cs
Week 2: Dock + Island (02) → Build the starting area
Week 3: Props (03) → Harpoon, barrels, chest for gameplay
Week 4: Sea Creatures (04) → Harpoon targets, wildlife
Week 5: Ocean Assets (05) → Polish the world
```

---

## Unity FBX Import Settings (Quick Reference)

After importing any FBX into Unity:

| Setting | Value |
|---|---|
| Scale Factor | `0.01` |
| Convert Units | ✓ ON |
| Import Normals | `Import` |
| Import Tangents | `Calculate Tangent Space` |
| Generate Lightmap UVs | ✓ ON |
| Mesh Compression | `Low` |
| Read/Write Enabled | ✓ ON (for procedural buoyancy) |

For creatures with armatures:
| Setting | Value |
|---|---|
| Animation Type | `Humanoid` or `Generic` |
| Import BlendShapes | ✓ ON |
| Optimize Game Objects | OFF (keep bones accessible) |

---

## Naming Conventions (Already Used in All Prompts)

All models follow this naming pattern so Unity scripts can find them:

- **Game objects**: `[Category]_[Part]` → `Boat_Hull`, `Boat_Lantern`
- **Materials**: `Mat_[Category]_[Description]` → `Mat_Wood_Hull`
- **Root empties**: `[Category]_ROOT` → `Boat_ROOT`, `Island_ROOT`
- **Bones**: `Bone_[BodyPart]` → `Bone_Head`, `Bone_Tail_01`
- **LODs**: `[Object]_LOD0`, `_LOD1`, `_LOD2`
- **Light points**: `[Object]_LightPoint`

---

## Connection to BoatController.cs

After creating the boat model (Prompt 01), wire these in Unity Inspector:

```
BoatController.cs fields → Blender object to drag in:
_harpoonSpawnPoint  →  Boat_HarpoonMount (child Transform)
_lanternLight       →  Boat_Lantern → Add Light component here
```

```
BoatStats.cs (drag to same GameObject as BoatController):
Attach to: Boat_ROOT GameObject
```

---

## Texture Baking (After Model is Generated)

For the best visual quality, after generating each model, also ask AI:

```
Write a Blender Python script to bake the following texture maps for 
the [Model Name] objects in the scene:
1. Albedo/Color map: 2048x2048
2. Normal map: 2048x2048 (DirectX format for Unity)
3. Roughness/Metallic map: 2048x2048
4. Ambient Occlusion map: 2048x2048
Save all textures to: //textures/[ModelName]/
Use cycles renderer for baking.
```

---

*These prompts are specific to IsleTrial — a Unity ocean adventure game.*
*Boat features: harpoon, lantern, anchor, boost, wind influence.*
*All models target high-quality graphics (not AAA but visually rich).*
