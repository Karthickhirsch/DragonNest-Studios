# IsleTrial — Unity Project Setup Guide
**Step-by-step from zero to a running game**

---

## Overview

```
Phase 1 → Create Unity project + install packages
Phase 2 → Import all C# scripts
Phase 3 → Import all FBX models
Phase 4 → Create ScriptableObject assets
Phase 5 → Build scenes
Phase 6 → Wire everything together
Phase 7 → Test & first playthrough
```

---

## Phase 1 — Create the Unity Project

### Step 1 — New Project
```
Unity Hub → New Project
Template  : 3D (URP)     ← Universal Render Pipeline (required for PBR materials)
Name      : IsleTrial
Location  : C:\Users\YourName\Projects\IsleTrial   (NOT inside DG_Project folder)
Unity ver : 2022.3 LTS or 6000.0 LTS
```

Click **Create Project** and wait for it to open.

### Step 2 — Install Required Packages
`Window → Package Manager → Unity Registry`

Install these packages in order:

| Package | Why it is needed |
|---|---|
| **Input System** | `PlayerInputHandler.cs` uses `PlayerInput` component |
| **Cinemachine** | `CameraShaker.cs` uses `CinemachineImpulseSource` |
| **TextMeshPro** | All UI scripts use TMP_Text components |
| **AI Navigation** | `EnemyBase.cs` uses `NavMeshAgent` |
| **Addressables** | `SceneLoader.cs` uses async scene loading |
| **Universal RP** | Already included in URP template — verify it is present |

> When Unity asks **"Enable New Input System?"** — click **YES** and
> allow Unity to restart.

> When TextMeshPro asks to import TMP Essentials — click **Import**.

### Step 3 — Project Settings

`Edit → Project Settings`:

**Player tab:**
```
Company Name    : YourStudio
Product Name    : IsleTrial
Version         : 0.1.0
API Level       : .NET Standard 2.1
```

**Physics tab:**
```
Gravity         : (0, -12, 0)    ← slightly stronger for heavier ocean feel
Default Contact Offset : 0.01
```

**Time tab:**
```
Fixed Timestep  : 0.02    (50 fps physics)
```

**Tags & Layers — add these tags:**
```
Player, Enemy, Boss, Boat, NPC, Interactable, Pickup,
Projectile, Island, Ocean, Trigger, DestructibleProp
```

**Tags & Layers — add these layers:**
```
Layer 8  : Player
Layer 9  : Enemy
Layer 10 : Boat
Layer 11 : Ocean
Layer 12 : Island
Layer 13 : Projectile
Layer 14 : Interactable
```

**Physics Matrix — uncheck collisions between:**
```
Projectile ↔ Projectile   (no bullet-to-bullet)
Ocean ↔ Island            (no ocean mesh colliding terrain)
```

---

## Phase 2 — Import C# Scripts

### Step 4 — Copy Script Folder
```
1. Open File Explorer
2. Navigate to: C:\Users\skarthick-a\Videos\DG_Project\Code\
3. Copy the entire Code folder
4. Paste into: [YourUnityProject]\Assets\
5. Unity will auto-compile all 55 scripts (this may take 30-60 seconds)
```

### Step 5 — Fix Assembly References
If you see red errors about missing namespaces, it is because new packages
were not yet recognized. Fix:

```
1. Close Visual Studio if open
2. Unity: Edit → Preferences → External Tools → Regenerate Project Files
3. Open any .cs file from the Project window — VS reopens with correct references
```

### Step 6 — Create Input Actions Asset
```
1. Right-click in Project window → Create → Input Actions
2. Name it: PlayerInputActions
3. Save it in: Assets/Code/Input/
4. Double-click to open the Input Actions editor
```

Add these Action Maps exactly:

**Action Map: Player**
| Action | Type | Bindings |
|---|---|---|
| Move | Value (Vector2) | WASD, Left Stick |
| Attack | Button | Left Mouse, X button |
| Dodge | Button | Space, Circle |
| Interact | Button | E, Square |
| Sprint | Button | Shift, L3 |
| UseAbility | Button | Q, Triangle |
| AbilityNext | Button | Mouse Wheel Up, RB |
| AbilityPrev | Button | Mouse Wheel Down, LB |

**Action Map: Boat**
| Action | Type | Bindings |
|---|---|---|
| Steer | Value (Vector2) | WASD, Left Stick |
| Boost | Button | Shift, R2 |
| Anchor | Button | Space, Square |
| FireHarpoon | Button | Left Mouse, R1 |
| Lantern | Button | F, DPad Down |

**Action Map: UI**
| Action | Type | Bindings |
|---|---|---|
| Navigate | Value (Vector2) | Arrow keys, D-pad |
| Submit | Button | Enter, A button |
| Cancel | Button | Escape, B button |
| Pause | Button | Escape, Start |

After creating actions: click **Save Asset** → then in Inspector on the
asset set **Generate C# Class** ✓ and click **Apply**.

Drag the `PlayerInputActions` asset to the `PlayerInputHandler.cs` component
in the scene later.

---

## Phase 3 — Import FBX Models

### Step 7 — Create Folder Structure in Assets
```
Assets/
├── Models/
│   ├── Characters/
│   │   ├── Kael/
│   │   ├── Toran/
│   │   ├── NPCs/
│   │   └── Enemies/
│   ├── Bosses/
│   ├── Boats/
│   ├── Environment/
│   │   ├── Islands/
│   │   ├── Ruins/
│   │   └── Ocean/
│   ├── Props/
│   ├── Weapons/
│   └── VFX/
├── Materials/
│   ├── Characters/
│   ├── Environment/
│   └── VFX/
├── Textures/
├── Animations/
│   ├── Kael/
│   ├── Toran/
│   ├── Enemies/
│   └── Bosses/
├── Prefabs/
│   ├── Characters/
│   ├── Enemies/
│   ├── Bosses/
│   ├── Props/
│   └── VFX/
├── ScriptableObjects/
│   ├── EnemyData/
│   ├── BossData/
│   ├── ItemData/
│   └── LootTables/
├── Scenes/
├── Audio/
│   ├── Music/
│   └── SFX/
└── Code/          ← scripts go here (copied in Step 4)
```

### Step 8 — Export FBX from Blender
For each Blender script, run the rig script in the same scene as the
model script (see `Toran_Mesh_Rig_Binding_Guide.md` for full process),
then export:

```
File → Export → FBX
  Scale : 1.0
  Axis  : Y Up, -Z Forward
  ☑ Apply Transform
  ☑ Armature
  ☑ Mesh
  ☑ Baked Animation (if animations exist)
  ☐ Add Leaf Bones  (OFF)
```

### Step 9 — Import Settings per Model Type

**Humanoid characters (Kael, Toran):**
```
Select FBX → Inspector → Rig tab:
  Animation Type : Humanoid
  Avatar         : Create From This Model
  Click Configure → verify all bones are green
  Apply
```

**Generic creatures (EmberLizard, FrostSlug, Ignar, Glaciara, sea creatures):**
```
Select FBX → Inspector → Rig tab:
  Animation Type : Generic
  Root node      : Root
  Apply
```

**Static environment (islands, ruins, caves):**
```
Select FBX → Inspector → Rig tab:
  Animation Type : None
Model tab:
  ☑ Generate Colliders (for large terrain pieces)
  ☑ Bake Axis Conversion
  Apply
```

**Materials (for all models):**
```
Select FBX → Inspector → Materials tab:
  Location : Use External Materials (Legacy)
  Click Extract Materials → choose Assets/Materials/[category]/
  Unity creates .mat files for each material
  Assign URP/Lit shader to each material
  Plug in textures exported from Blender (see note below)
```

> **Texture Export from Blender:**
> Each script has material nodes with `[UNITY]` image texture slots.
> After baking textures in Blender (Render → Bake):
> - Albedo → Albedo/Base Color slot
> - Normal → Normal Map slot (set Texture Type to Normal Map)
> - Roughness → Roughness slot (in R channel of a packed texture)
> - Emission → Emission slot

---

## Phase 4 — Create ScriptableObject Assets

### Step 10 — EnemyData Assets
```
Right-click in Assets/ScriptableObjects/EnemyData/
→ Create → IsleTrial → EnemyData
Create one file per enemy (see ScriptableObject_Data_Sheet.md for values)
```

Enemies to create:
`EmberLizard_Data`, `FrostSlug_Data`, `MimicChest_Data`,
`BirdSkeleton_Data`, and all 33 enemies from the GDD.

### Step 11 — BossData Assets
```
Assets/ScriptableObjects/BossData/
→ Create → IsleTrial → BossData
```

Create: `Ignar_Data`, `Glaciara_Data`, `MyceliumKing_Data`,
`GrandNavigator_Data`, `KrakenChest_Data`, `DreadAdmiral_Data`,
`CoralTitan_Data`

### Step 12 — ItemData Assets
```
Assets/ScriptableObjects/ItemData/
→ Create → IsleTrial → ItemData
```

Create items: `HealthPotion`, `RepairKit`, `EmberCrystal`, `FrostCrystal`,
`MystCrystal`, `RareCrystal`, `SoulEssence`, `CompassShard`,
`AncientMap`, `BoatPlank`, `Rope`, `IronNail` and all weapons.

### Step 13 — LootTable Assets
```
Assets/ScriptableObjects/LootTables/
→ Create → IsleTrial → LootTable
```

Create: `EmberIsle_LootTable`, `FrostIsle_LootTable`,
`MysteryIsle_LootTable`, `SunkenTemple_LootTable`,
`Tutorial_LootTable`, `Ocean_LootTable`

---

## Phase 5 — Build Scenes

### Step 14 — Scene List
Create the following scenes in `Assets/Scenes/`:

| Scene File | Description |
|---|---|
| `MainMenu.unity` | Title screen, play/settings/quit |
| `TutorialIsle.unity` | Act 1 — Tutorial Island |
| `Ocean.unity` | Open ocean traversal scene (persistent) |
| `EmberIsle.unity` | Act 2 — Ember Island + Ignar boss |
| `FrostIsle.unity` | Act 2 — Frost Island + Glaciara boss |
| `MysteryIsle.unity` | Act 2 — Mystery Island |
| `SunkenTemple.unity` | Act 2 — Underwater temple |
| `StormNexus.unity` | Act 3 — Final confrontation |
| `GameOver.unity` | Game over screen |

### Step 15 — Scene Setup (Ocean scene — start here)

**1. Terrain:**
- Import `29_Ocean_SurfaceReference.fbx` → drag to scene at (0,0,0)
- Add a Plane (large — scale 500x500) for ocean floor at Y=-50
- Add NavMesh Surface component → Bake for enemy land areas

**2. Lighting:**
- Directional Light → set color to warm amber (0.95, 0.85, 0.70)
- Intensity: 1.2
- Add `Fog` → Exponential Squared → density 0.008, color (0.45, 0.55, 0.65)

**3. Camera:**
- Create Camera object → add `Cinemachine Virtual Camera`
- Add `CameraShaker.cs` component
- Set follow target to Kael transform

**4. GameManager:**
- Create empty `GameManager` GameObject
- Add `GameManager.cs`, `GameEvents.cs`, `SceneLoader.cs` components
- In Inspector on GameManager: assign all Scene names to the scene list

**5. Audio:**
- Create empty `AudioManager` GameObject
- Add `AudioManager.cs`
- Assign music clips: OceanAmbient, CombatTheme_1, CombatTheme_Boss, Victory

---

## Phase 6 — Wire Everything Together

### Step 16 — Player Setup

```
1. Drag Kael FBX into scene
2. Add components:
   - PlayerController.cs
   - PlayerStats.cs
   - PlayerInventory.cs
   - PlayerAbilityHandler.cs
   - PlayerInputHandler.cs  ← assign PlayerInputActions asset
   - Animator             ← assign Kael Animator Controller
   - CharacterController   (radius 0.4, height 1.8)
   - Rigidbody            (Is Kinematic OFF, constraints: freeze X/Z rotation)

3. Add child objects:
   - WeaponHolder (empty, child of RightHand bone)
     → Add HarpoonProjectile spawn point
   - CompassHolder (empty, child of Hips bone)
   - CameraTarget (empty, at eye level Z=1.65)

4. Create Player Prefab:
   Drag from Hierarchy to Assets/Prefabs/Characters/
```

### Step 17 — Enemy Setup (EmberLizard example)

```
1. Drag EmberLizard FBX into scene
2. Add components:
   - EmberLizard.cs
   - EnemyBase.cs     (base class — auto-included)
   - NavMeshAgent     (speed 3.5, stopping distance 1.8, radius 0.6)
   - Animator         (assign EmberLizard Animator Controller)
   - Rigidbody        (Is Kinematic ON — NavMesh controls movement)
   - CapsuleCollider  (radius 0.8, height 2.2, centre Y=1.1)

3. In EmberLizard.cs Inspector:
   - Enemy Data      : EmberLizard_Data (ScriptableObject)
   - Loot Table      : EmberIsle_LootTable
   - Attack Points   : assign each attack hitbox child transform

4. Create Prefab → Assets/Prefabs/Enemies/

5. Repeat for every other enemy
```

### Step 18 — Boss Setup (Ignar example)

```
1. Drag Ignar FBX into scene
2. Add components:
   - Ignar_MoltenDrake.cs
   - BossBase.cs          (auto-included)
   - NavMeshAgent         (speed 2.5, stopping distance 4.0, radius 2.0)
   - Animator             (Ignar Animator Controller)
   - Rigidbody            (Is Kinematic ON)
   - BoxCollider          (approximate body volume)

3. In Inspector:
   - Boss Data            : Ignar_Data
   - Phase2 Health        : 0.66 (triggers at 66% health)
   - Phase3 Health        : 0.33 (triggers at 33% health)
   - Lava Ball Prefab     : LavaBall_Prefab
   - Fire Breath Point    : assign FireBreath_Ctrl bone Transform

4. Create boss arena trigger:
   - Large Box Collider (Is Trigger) → BossArena_Trigger tag
   - On enter: GameEvents.OnBossAreaEntered.Invoke(ignarInstance)

5. Create Prefab → Assets/Prefabs/Bosses/
```

### Step 19 — UI Setup

```
Canvas (Screen Space — Camera):
  ├── HUDCanvas
  │   ├── HealthBar      → HealthBar.cs
  │   ├── StaminaBar
  │   ├── BoatHealthBar
  │   ├── AbilitySlots   → AbilityUI.cs
  │   └── MinimapDisplay → MapUI.cs
  ├── PauseMenuPanel    → PauseMenuController.cs (disabled by default)
  ├── GameOverPanel     → GameOverScreen.cs (disabled by default)
  └── MainMenuPanel     → MainMenuController.cs (active only in MainMenu scene)

All text fields: use TextMeshPro components
All images: assign sprites from Assets/UI/Sprites/
```

### Step 20 — NavMesh Bake

For each island/environment scene:
```
1. Select all terrain/ground objects in Hierarchy
2. Inspector → Static ▸ Navigation Static ✓
3. Window → AI → Navigation → Bake tab
   Agent Radius : 0.5
   Agent Height : 2.0
   Max Slope    : 45
   Step Height  : 0.4
4. Click Bake
5. Verify blue NavMesh overlay covers all walkable surfaces
```

---

## Phase 7 — Test Checklist

Run through this checklist before each play test session:

```
☐  Game starts from MainMenu scene (File → Build Settings → set scene order)
☐  Kael spawns correctly on TutorialIsle
☐  Player moves with WASD (check Input System is enabled)
☐  Camera follows Kael
☐  Basic sword attack connects with enemy
☐  Enemy takes damage → health bar updates
☐  Enemy dies → loot drops → can be picked up
☐  Boat can be boarded (Interact key near dock)
☐  Boat moves on ocean
☐  Harpoon fires from boat
☐  Transition from ocean to island works (trigger zone)
☐  Boss arena triggers boss fight music
☐  Boss Phase 2 triggers at 66% health
☐  Boss dies → chest spawns → next island unlocks
☐  Pause menu opens (Escape) and resumes correctly
☐  Game over screen appears on Kael death
☐  ScriptableObject data (health/damage) reads correctly in combat
```

---

## Common Issues & Fixes

| Problem | Fix |
|---|---|
| Scripts fail to compile — missing namespace | Check Package Manager — all packages from Step 2 installed? |
| Player slides instead of walking | Ensure CharacterController has correct radius; check PlayerController `_isGrounded` logic |
| Enemy stuck / won't move | NavMesh not baked — redo Step 20 |
| Models appear 100x scale in Unity | FBX export scale was wrong — re-export with Scale 1.0 and Apply Transform |
| Materials appear pink in Unity | Shader not assigned — select material, change shader to Universal Render Pipeline/Lit |
| No audio plays | AudioManager not in scene, or audio clips not assigned in Inspector |
| Input doesn't work | New Input System not enabled — Edit → Project Settings → Player → Active Input Handling: Both |
| Animator does nothing | Animator Controller not assigned to the Animator component on the character |
| Boss health bar not showing | BossHealthBar UI component not subscribed to `GameEvents.OnBossDamaged` |

---

## Build for Windows (final)

```
File → Build Settings
  Platform     : PC, Mac & Linux Standalone
  Target       : Windows x86_64
  Scenes        : add all scenes in correct order (MainMenu first)

Player Settings:
  Resolution    : 1920x1080 default, allow resize
  Quality       : Ultra (for development)
  Icon          : assign game icon

Build → choose output folder → IsleTrial.exe created
```

---

*Guide version 1.0 — IsleTrial Project*
