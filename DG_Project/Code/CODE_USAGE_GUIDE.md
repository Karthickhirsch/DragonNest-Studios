# Code Usage Guide
## Isle of Trials — How to Set Up Every Script in Unity

> For each script: what to attach it to, what fields to fill in the Inspector, and what to create/connect in the Unity Editor.

---

## Table of Contents
1. [Project Setup Checklist](#1-project-setup-checklist)
2. [Core — GameManager](#2-core--gamemanager)
3. [Core — SceneLoader](#3-core--sceneloader)
4. [Core — GameEvents](#4-core--gameevents)
5. [Player — PlayerController](#5-player--playercontroller)
6. [Player — PlayerStats](#6-player--playerstats)
7. [Player — PlayerInventory](#7-player--playerinventory)
8. [Player — PlayerInputHandler](#8-player--playerinputhandler)
9. [Player — PlayerAbilityHandler](#9-player--playerabilityhandler)
10. [Boat — BoatController](#10-boat--boatcontroller)
11. [Boat — BoatStats](#11-boat--boatstats)
12. [Boat — OceanBuoyancy](#12-boat--oceanbuoyancy)
13. [Enemies — EnemyBase & EmberLizard](#13-enemies--enemybase--emberlizard)
14. [Enemies — FrostSlug](#14-enemies--frostslug)
15. [Bosses — BossBase & Ignar](#15-bosses--bossbase--ignar)
16. [Bosses — Glaciara FrostWarden](#16-bosses--glaciara-frostwarden)
17. [Puzzles — SymbolMatchPuzzle](#17-puzzles--symbolmatchpuzzle)
18. [Puzzles — LightBeamPuzzle](#18-puzzles--lightbeampuzzle)
19. [Puzzles — PushBlockPuzzle](#19-puzzles--pushblockpuzzle)
20. [World — WeatherSystem](#20-world--weathersystem)
21. [World — DayNightCycle](#21-world--daynightcycle)
22. [World — IslandProximityLoader](#22-world--islandproximityloader)
23. [World — NPC](#23-world--npc)
24. [World — ChestInteractable](#24-world--chestinteractable)
25. [World — DoorGate](#25-world--doorgate)
26. [World — ItemPickup](#26-world--itempickup)
27. [World — CrystalPickup](#27-world--crystalpickup)
28. [World — BoatRepairStation](#28-world--boatrepairstation)
29. [World — TutorialTrigger](#29-world--tutorialtrigger)
30. [Boat — HarpoonProjectile](#30-boat--harpoonprojectile)
31. [Bosses — LavaBallProjectile & LavaPuddle](#31-bosses--lavaballprojectile--lavapuddle)
32. [Save System — SaveManager](#32-save-system--savemanager)
33. [UI — MainMenuController](#33-ui--mainmenucontroller)
34. [UI — PauseMenuController](#34-ui--pausemenucontroller)
35. [UI — GameOverScreen](#35-ui--gameoverscreen)
36. [UI — HUDManager](#36-ui--hudmanager)
37. [UI — BossHealthBarUI](#37-ui--bosshealthbarui)
38. [UI — DialogueManager](#38-ui--dialoguemanager)
39. [UI — MapUI](#39-ui--mapui)
40. [Audio — AudioManager](#40-audio--audiomanager)
41. [Utilities — PoolManager](#41-utilities--poolmanager)
42. [Utilities — CameraShaker](#42-utilities--camerashaker)
43. [Data — ScriptableObjects (incl. LootTable)](#43-data--scriptableobjects)
44. [Complete Bootstrap Scene Setup](#44-complete-bootstrap-scene-setup)

---

## 1. Project Setup Checklist

Before adding any scripts, do this once:

```
[ ] Create a new Unity project (3D URP template)
[ ] Install packages: Input System, Cinemachine, TextMeshPro, NavMesh, Addressables
[ ] Copy the entire Code/ folder into your project's Assets/ folder
[ ] Unity will ask "Enable New Input System?" — click YES and restart
[ ] Generate a PlayerInputActions asset:
      Window → Input System Package → create PlayerInputActions.inputactions
      Add Action Maps: Player, Boat, UI
      Add actions per map (Move, Attack, Dodge, Interact, etc.)
      Click "Generate C# Class" button at top
[ ] Create a Bootstrap scene (File → New Scene → save as Bootstrap)
[ ] Add Bootstrap to Build Settings first (File → Build Settings → Add Open Scenes)
```

---

## 2. Core — GameManager

**File:** `Core/GameManager.cs`

### Attach to:
A GameObject named **"GameManager"** in the **Bootstrap scene**.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Starting State` | Set to `MainMenu` for production, `Sailing` for testing |

### Unity Steps:
1. Create → Empty GameObject → rename **"GameManager"**
2. Add Component → `GameManager`
3. The GameObject will auto-survive scene loads (`DontDestroyOnLoad`)

### How it works:
- Call `GameManager.Instance.ChangeState(GameState.Sailing)` from any script when switching modes.
- Other scripts subscribe to `GameEvents.OnGameStateChanged` to react.

---

## 3. Core — SceneLoader

**File:** `Core/SceneLoader.cs`

### Attach to:
The same **"GameManager"** GameObject in Bootstrap scene (or a sibling "SceneLoader").

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Loading Screen UI` | Drag in a Canvas GameObject that shows a loading spinner |

### Unity Steps:
1. Create a UI Canvas → add a panel with a loading icon → rename **"LoadingScreen"**
2. Set the panel active = **false** by default
3. Drag the Canvas into `Loading Screen UI` on SceneLoader

### How to use in other scripts:
```csharp
// Load an island additively
SceneLoader.Instance.LoadSceneAdditive("Island_01_Ember", () => Debug.Log("Loaded!"));

// Unload it later
SceneLoader.Instance.UnloadScene("Island_01_Ember");
```

> **Important:** Every scene name must be added to **File → Build Settings** for this to work.

---

## 4. Core — GameEvents

**File:** `Core/GameEvents.cs`

### Attach to: Nothing — this is a static class.

### How to subscribe (in any script):
```csharp
void OnEnable()  => GameEvents.OnPlayerDied += HandlePlayerDeath;
void OnDisable() => GameEvents.OnPlayerDied -= HandlePlayerDeath;

void HandlePlayerDeath() { /* show game over screen */ }
```

### How to fire an event (from a system):
```csharp
GameEvents.PlayerHealthChanged(currentHP, maxHP);
```

> **Rule:** Always unsubscribe in `OnDisable` to avoid memory leaks.

---

## 5. Player — PlayerController

**File:** `Player/PlayerController.cs`

### Attach to:
The **Player prefab root GameObject**.

### Required Components (auto-enforced):
- `CharacterController`
- `PlayerStats`
- `PlayerInputHandler`
- `Animator`

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Camera Transform` | Drag the **Main Camera** (or Cinemachine camera target) |
| `Interact Layer` | Create a Layer named "Interactable" → assign it |
| `Interact Range` | `2` |
| `Attack Hit Point` | Create an empty child Transform at the player's sword tip |
| `Attack Radius` | `1` |
| `Enemy Layer` | Create a Layer named "Enemy" → assign it |
| `Charge Time Required` | `1.5` |
| `Charged Attack VFX` | Drag in a Particle System prefab |

### Unity Steps:
1. Create Player prefab → add `CharacterController` (radius=0.3, height=1.8)
2. Add `Animator` → assign a controller with states: Idle, Walk, Run, Attack, ChargedAttack, Dodge, Dead
3. Create an empty child at sword level → name it **"AttackPoint"** → drag into `Attack Hit Point`
4. Add `PlayerController`, `PlayerStats`, `PlayerInputHandler`, `PlayerAbilityHandler`

### Animator States Needed:
```
Idle → (Speed > 0.1) → Walk
Walk → (Speed > 0.8) → Run
Any → (Trigger: Attack) → Attack
Any → (Trigger: ChargedAttack) → ChargedAttack
Any → (Trigger: Dodge) → Dodge
Any → (Trigger: Dead) → Dead
```

---

## 6. Player — PlayerStats

**File:** `Player/PlayerStats.cs`

### Attach to: Player prefab (same GameObject as PlayerController).

### Inspector Setup:
| Field | Recommended Value |
|-------|-------------------|
| `Max Health` | `100` |
| `Regen Delay` | `5` |
| `Regen Rate` | `3` |
| `Move Speed` | `5` |
| `Sprint Multiplier` | `1.6` |
| `Dodge Speed` | `10` |
| `Dodge Duration` | `0.25` |
| `Attack Damage` | `20` |
| `Charged Attack Multiplier` | `3` |
| `Invincibility Frames` | `8` |
| `Max Stamina` | `100` |
| `Stamina Drain Per Dodge` | `20` |
| `Stamina Regen Rate` | `15` |

### How to deal damage from another script:
```csharp
var stats = player.GetComponent<PlayerStats>();
stats.TakeDamage(25);
```

---

## 7. Player — PlayerInventory

**File:** `Player/PlayerInventory.cs`

### Attach to: Player prefab.

### Inspector Setup:
| Field | Value |
|-------|-------|
| `Max Slots` | `10` |

### How to add items from a chest/pickup script:
```csharp
var inventory = FindObjectOfType<PlayerInventory>();
inventory.AddItem(someItemData);
```

---

## 8. Player — PlayerInputHandler

**File:** `Player/PlayerInputHandler.cs`

### Attach to: Player prefab.

### Requirement:
- You must have generated the `PlayerInputActions` C# class from your Input Actions asset first.

### No Inspector fields required — all binding is done in code.

### To check input in any script:
```csharp
var input = GetComponent<PlayerInputHandler>();
if (input.AttackPressed) { /* do attack */ }
```

---

## 9. Player — PlayerAbilityHandler

**File:** `Player/PlayerAbilityHandler.cs`

### Attach to: Player prefab.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Active Ability` | Leave empty — auto-set when ability is unlocked |
| `Fire Dash VFX` | Drag a fire trail Particle System prefab |
| `Fire Dash Distance` | `5` |
| `Fire Dash Damage` | `30` |
| `Enemy Layer` | Set to "Enemy" layer |
| `Ice Shield Visual` | Drag a sphere/shield mesh child GameObject |
| `Grapple Line` | Drag a LineRenderer component |
| `Grapple Layer` | Create layer "GrapplePoint" → assign |
| `Grapple Range` | `12` |
| `Lightning VFX` | Drag lightning Particle System |
| `Lightning Radius` | `3` |
| `Lightning Damage` | `50` |

### How abilities unlock:
When a boss is defeated → `GameEvents.AbilityUnlocked(ability)` fires → `PlayerAbilityHandler` auto-receives it and equips it.

---

## 10. Boat — BoatController

**File:** `Boat/BoatController.cs`

### Attach to: The **Boat prefab** root GameObject.

### Required Components:
- `Rigidbody` (mass=500, drag=1, angular drag=2)
- `BoatStats`

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Turn Speed` | `90` |
| `Wind Influence` | `0.3` |
| `Harpoon Spawn Point` | Create a child Transform at boat bow → drag in |
| `Harpoon Projectile Prefab` | A prefab with Rigidbody (isKinematic=false) + Collider |
| `Harpoon Speed` | `20` |
| `Lantern Light` | Drag the boat's Point Light child |
| `Wind Direction` | Leave default (changed at runtime by WeatherSystem) |

### Unity Steps:
1. Create Boat model → apply Rigidbody → freeze rotation X and Z (or let physics handle naturally)
2. Tag the boat with **Tag: "Boat"** — required by `IslandProximityLoader`
3. Add 4 empty child Transforms at hull corners for `OceanBuoyancy`

---

## 11. Boat — BoatStats

**File:** `Boat/BoatStats.cs`

### Attach to: Boat prefab (same GameObject as BoatController).

### Inspector Setup:
| Field | Value |
|-------|-------|
| `Base Max Speed` | `8` |
| `Boost Speed` | `16` |
| `Max Boost Charges` | `3` |
| `Boost Duration` | `1.5` |
| `Boost Recharge Cooldown` | `6` |
| `Max Durability` | `100` |
| `Max Harpoon Shots` | `3` |
| `Harpoon Reload Time` | `2` |

---

## 12. Boat — OceanBuoyancy

**File:** `Boat/OceanBuoyancy.cs`

### Attach to: Boat prefab.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Wave Height` | `1.5` |
| `Wave Frequency` | `0.5` |
| `Wave Speed` | `1` |
| `Buoyancy Force` | `15` |
| `Water Drag` | `2` |
| `Water Angular Drag` | `1` |
| `Water Level` | `0` (Y position of your ocean plane) |
| `Float Points` | Drag 4 child Transforms (boat hull corners) |

### Unity Steps:
1. Create 4 empty child GameObjects at each corner of the boat hull
2. Name them: FloatPoint_FL, FloatPoint_FR, FloatPoint_BL, FloatPoint_BR
3. Drag all 4 into the `Float Points` array

---

## 13. Enemies — EnemyBase & EmberLizard


**File:** `Enemies/EnemyBase.cs`, `Enemies/EmberLizard.cs`

### Attach to: Enemy prefabs. Never attach `EnemyBase` directly — use a subclass like `EmberLizard`.

### Required Components:
- `NavMeshAgent`
- `Animator`
- A Collider (CapsuleCollider)

### Inspector Setup (EmberLizard example):
| Field | Value |
|-------|-------|
| `Data` | Drag the `EmberLizard.asset` ScriptableObject |
| `Detection Radius` | `8` |
| `Attack Radius` | `2` |
| `Player Layer` | "Player" layer |
| `Patrol Waypoints` | Drag 2-4 empty GameObjects in the scene as patrol targets |
| `Explosion Radius` | `2` |
| `Explosion Damage` | `30` |
| `Explosion VFX` | Drag a fire explosion Particle System prefab |

### Unity Steps:
1. Bake a NavMesh for each island scene: **Window → AI → Navigation → Bake**
2. Set the enemy prefab's layer to **"Enemy"**
3. Create the `EnemyData` ScriptableObject (see section 28) and assign it

### Animator States Needed:
```
Walk (when NavMeshAgent is moving)
Attack (Trigger)
Stun (Trigger)
Dead (Trigger)
```

---

## 14. Enemies — FrostSlug

**File:** `Enemies/FrostSlug.cs`

### Attach to: FrostSlug enemy prefab (same setup as EmberLizard).

### Required Components:
- `NavMeshAgent`
- `Animator`
- `CapsuleCollider`

### Inspector Setup:
| Field | Value |
|-------|-------|
| `Data` | Drag `FrostSlug.asset` EnemyData ScriptableObject |
| `Detection Radius` | `7` |
| `Attack Radius` | `1.8` |
| `Player Layer` | "Player" layer |
| `Patrol Waypoints` | 2–4 patrol point Transforms |
| `Slow Multiplier` | `0.5` (half speed) |
| `Slow Duration` | `3` |
| `Armor Points` | `2` (absorbs 2 hits before taking damage) |
| `Frost Patch Prefab` | Prefab with Trigger Collider + FrostSlow script |
| `Frost Patch Duration` | `6` |
| `Hit Ice VFX` | Ice particle prefab (plays when armor absorbs hit) |
| `Death Frost VFX` | Frost burst particle prefab |

### Armour System:
FrostSlug absorbs the first `Armor Points` hits, playing an ice VFX but dealing no damage to HP. After armour breaks, `TakeDamage` works normally via `EnemyBase`.

### Animator States Needed:
```
Walk, Attack, Stun, Dead
```

### Speed Modifier:
On hit, FrostSlug calls `PlayerStats.ApplySpeedModifier(0.5f)`. Speed resets after `Slow Duration` seconds via `PlayerStats.ResetSpeedModifier()`.

---

## 15. Bosses — BossBase & Ignar

**File:** `Bosses/BossBase.cs`, `Bosses/Ignar_MoltenDrake.cs`

### Attach to: Boss prefab. Use `Ignar_MoltenDrake` (not `BossBase` directly).

### Inspector Setup (Ignar):
| Field | What to set |
|-------|-------------|
| `Data` | Drag `Ignar.asset` BossData ScriptableObject |
| `Phase2 Threshold` | `0.6` (60% HP) |
| `Phase3 Threshold` | `0.3` (30% HP) |
| `Phase Transition VFX` | Particle System that plays on phase change |
| `Death VFX` | Explosion/dissolve Particle System |
| `Breath Origin` | Child Transform at dragon's mouth |
| `Fire Breath VFX` | Fire breath Particle System |
| `Lava Ball Prefab` | Fireball prefab (Rigidbody + damage collider) |
| `Lava Spawn Point` | Child Transform at mouth |
| `Lava Plane` | The rising lava mesh in the arena |
| `Lava Rise Target` | `1.5` |
| `Floor Tiles` | Array of arena floor tile GameObjects |

### Animator States Needed:
```
Idle
Phase (Integer parameter: 1, 2, 3)
TailSlam (Trigger)
Dive (Trigger)
DiveLand (Trigger)
Charge (Trigger)
Hit (Trigger)
Dead (Trigger)
```

---

## 16. Bosses — Glaciara FrostWarden

**File:** `Bosses/Glaciara_FrostWarden.cs`

### Attach to: GlaciaraBoss prefab. Same setup as Ignar.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Data` | Drag `Glaciara.asset` BossData ScriptableObject |
| `Phase2 Threshold` | `0.6` |
| `Phase3 Threshold` | `0.3` |
| `Phase Transition VFX` | Ice burst Particle System |
| `Death VFX` | Shattering ice Particle System |
| `Ice Shard Prefab` | Prefab with Rigidbody + IceShardProjectile + Collider |
| `Shard Spawn Point` | Child Transform at boss mouth/hand |
| `Shard Count` | `5` |
| `Shard Spread` | `30` (degrees) |
| `Ice Wall Prefab` | Tall ice wall mesh prefab |
| `Ice Wall Spawn Points` | 3–4 Transforms around the arena |
| `Charge Speed` | `18` |
| `Charge Damage` | `35` |
| `Blizzard VFX` | Full-arena snow particle system |
| `Ice Spear Prefab` | Prefab with IceSpearHoming + Collider |
| `Spear Count` | `8` |
| `Blizzard Slow Multiplier` | `0.4` |

### Phase Breakdown:
| Phase | Trigger | Attacks |
|-------|---------|---------|
| Phase 1 | Start | Ice shard spread volley |
| Phase 2 | 60% HP | Summons ice walls + charge attack |
| Phase 3 | 30% HP | Activates blizzard + homing ice spears |

### Animator States Needed:
```
Idle, Phase (Int), Shoot (Trigger), Charge (Trigger), Blizzard (Trigger), Hit (Trigger), Dead (Trigger)
```

### Helper Scripts (same file):
- `IceShardProjectile` — Attach to the ice shard prefab. Calls `Initialise(damage, layer)` before launch.
- `IceSpearHoming` — Attach to the ice spear prefab. Calls `Initialise(target, damage, layer)` and homes toward player.

---

## 17. Puzzles — SymbolMatchPuzzle

**File:** `Puzzles/SymbolMatchPuzzle.cs`

### Attach to: A Puzzle root GameObject in the island scene.

### Setup steps in Unity:
1. Create an empty GameObject → name it **"Puzzle_SymbolMatch_01"**
2. Add `SymbolMatchPuzzle` component
3. Create 4 child GameObjects for tiles → name them Tile_0, Tile_1, Tile_2, Tile_3
4. On each tile: add `SpriteRenderer` + `SymbolTile` component
5. On each `SymbolTile`: assign `Symbols` list (4 sprites) and drag the parent puzzle into `Parent Puzzle`
6. On `SymbolMatchPuzzle`:

| Field | What to set |
|-------|-------------|
| `Puzzle ID` | `"EmberIsle_SymbolPuzzle_01"` (unique string) |
| `Reward Object` | Drag the door/gate that opens when solved |
| `Solved VFX` | Drag a particle system |
| `Tiles` | Drag all 4 SymbolTile components |
| `Solution Indices` | e.g. `[2, 0, 3, 1]` — the correct symbol index per tile |
| `Cascade Mode` | Check if adjacent tiles should rotate together |

---

## 18. Puzzles — LightBeamPuzzle

**File:** `Puzzles/LightBeamPuzzle.cs`

### Setup steps in Unity:
1. Create root GameObject → add `LightBeamPuzzle`
2. Create child GameObject → add `LightBeamEmitter` + `LineRenderer`
   - On LineRenderer: Width=0.05, Material=a bright Unlit Color material
3. Place `Mirror` GameObjects in scene → assign layer to `Reflect Layer` on emitter
4. Place `LightReceiver` GameObjects → assign a Renderer with two materials (active/inactive colors)

### Inspector Setup (LightBeamPuzzle):
| Field | What to set |
|-------|-------------|
| `Puzzle ID` | `"FrostIsle_LightPuzzle_01"` |
| `Emitter` | Drag the LightBeamEmitter child |
| `Receivers` | Drag all LightReceiver components (can be multiple) |
| `Reward Object` | Door/chest that opens on solve |

### Inspector Setup (LightBeamEmitter):
| Field | What to set |
|-------|-------------|
| `Max Reflections` | `8` |
| `Max Distance` | `50` |
| `Reflect Layer` | Layer containing mirrors AND receivers |
| `Beam Color` | Yellow or white |

---

## 19. Puzzles — PushBlockPuzzle

**File:** `Puzzles/PushBlockPuzzle.cs`

### Setup steps in Unity:
1. Create root → add `PushBlockPuzzle`
2. Create block GameObjects → add `PushableBlock` component + BoxCollider + Rigidbody (isKinematic=true)
3. Create plate GameObjects → add `PressurePlate` component + BoxCollider (isTrigger=true) + MeshRenderer

### Inspector Setup (PushBlockPuzzle):
| Field | What to set |
|-------|-------------|
| `Puzzle ID` | `"TutorialIsland_PushPuzzle_01"` |
| `Blocks` | Drag all PushableBlock components |
| `Plates` | Drag all PressurePlate components |
| `Reward Object` | Drag the door that opens |

### Inspector Setup (PushableBlock):
| Field | What to set |
|-------|-------------|
| `Move Distance` | `1` (must match grid unit size) |
| `Move Duration` | `0.2` |
| `Blocking Layers` | "Default" + "Wall" layers (to prevent phasing through walls) |

### Inspector Setup (PressurePlate):
| Field | What to set |
|-------|-------------|
| `Plate Renderer` | Drag MeshRenderer on the plate |
| `Active Color` | Green |
| `Inactive Color` | Grey |

---

## 20. World — WeatherSystem

**File:** `World/WeatherSystem.cs`

### Attach to: A manager GameObject in the **Ocean_World scene**.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Wind Zone` | Add a `WindZone` component to a child → drag in |
| `Rain Particles` | Drag a rain Particle System (set to worldspace, downward) |
| `Post Process Volume` | Drag the scene's Global Volume |
| `Sun Light` | Drag the Directional Light |
| `Boat` | Drag the BoatController |
| `Calm Profile` | Create a Volume Profile asset for calm weather |
| `Stormy Profile` | Create a Volume Profile asset (darker, contrast) |
| `Foggy Profile` | Create a Volume Profile asset (fog override enabled) |
| `Transition Duration` | `5` |
| `Auto Change` | ✓ enabled |
| `Min/Max Weather Duration` | 120 / 300 |

### To trigger specific weather from a boss fight script:
```csharp
FindObjectOfType<WeatherSystem>().SetWeather(WeatherState.Stormy);
```

---

## 21. World — DayNightCycle

**File:** `World/DayNightCycle.cs`

### Attach to: Manager GameObject in Ocean_World scene.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Sun` | Drag the scene's Directional Light |
| `Moon` | Drag a second Directional Light (intensity 0.3, blue-ish) |
| `Day Duration Minutes` | `24` |
| `Sun Color Over Day` | Create a Gradient: warm orange at dawn, white at noon, orange at dusk, dark at night |
| `Sun Intensity Curve` | AnimationCurve: 0 at t=0, peaks at t=0.5, back to 0 at t=1 |
| `Skybox Material` | Drag the scene's skybox material |
| `Skybox Blend Property` | `"_Blend"` (or the correct property name on your skybox shader) |

### Use in puzzle scripts:
```csharp
var dayNight = FindObjectOfType<DayNightCycle>();
if (dayNight.IsNoon()) ActivateSolarPuzzle();
```

---

## 22. World — IslandProximityLoader

**File:** `World/IslandProximityLoader.cs`

### Attach to: Each island marker GameObject in the Ocean_World scene.

### Unity Steps:
1. In Ocean_World scene, create empty GameObjects at each island's world position
2. Name them: Island_Marker_Tutorial, Island_Marker_Ember, etc.
3. Add `IslandProximityLoader` to each

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Island Data` | Drag the matching `IslandData.asset` ScriptableObject |
| `Discover Distance` | `300` |
| `Load Distance` | `150` |
| `Unload Distance` | `350` |
| `Map Marker Icon` | Drag a world-space UI icon or sprite that appears on discover |

> **Important:** The island scenes must be in **Build Settings** for additive loading to work.

---

## 23. World — NPC

**File:** `World/NPC.cs`

### Attach to: Any NPC prefab with a non-trigger Collider.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Dialogue` | Drag the NPC's `DialogueSequence` ScriptableObject |
| `Repeat Dialogue` | OFF (plays once) or ON (plays every interaction) |
| `Interact Indicator` | A child GameObject with a "!" Sprite above the NPC's head |
| `Indicator Bob Speed` | `1.5` |
| `Face Player On Interact` | ✓ ON |

### Unity Steps:
1. Create NPC prefab → add Capsule Collider + Animator + NPC script
2. Create a child GameObject named "Indicator" → add a world-space Canvas with "!" Image
3. Set NPC's layer to "NPC" (or "Default") — must NOT be "Enemy"
4. Create `DialogueSequence` ScriptableObject (see section 43) and drag into `Dialogue`

### Change dialogue at runtime (e.g. after a quest step):
```csharp
npc.SetDialogue(newDialogueSequence, resetSpokenFlag: true);
```

---

## 24. World — ChestInteractable

**File:** `World/ChestInteractable.cs`

### Attach to: TreasureChest prefab with an Animator + Collider.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Loot Table` | Drag a `LootTable.asset` ScriptableObject (see section 43) |
| `Loot Count` | `2` (items given per open) |
| `Loot Spawn Point` | Child Transform above the chest opening |
| `Open VFX` | Particle System that plays when chest opens |
| `Open SFX` | Audio clip for chest creak |
| `Interact Indicator` | "!" GameObject above the chest |

### Animator Setup:
Add a trigger parameter `Open` and a state "Open" that plays the lid-opening animation.

### How to link with a puzzle reward:
Set the chest as the `Reward Object` on `PuzzleBase` — when `CompletePuzzle()` fires, it activates the chest.

---

## 25. World — DoorGate

**File:** `World/DoorGate.cs`

### Attach to: Any door, gate, or portcullis GameObject.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Linked Puzzle ID` | The exact `PuzzleID` string from the puzzle that opens this door |
| `Open Mode` | `SlideUp` (portcullis), `SlideAside` (sliding door), `Rotate` (hinged door) |
| `Open Distance` | `3` for SlideUp/Aside. Ignored in Rotate mode. |
| `Open Angle` | `90` for Rotate mode. |
| `Open Duration` | `1.2` seconds |
| `Open Curve` | AnimationCurve — EaseInOut default |
| `Open VFX` | Particle System that plays on open |
| `Open SFX` | Door creak/open audio clip |

### To open from a script (e.g. after boss death):
```csharp
GetComponent<DoorGate>().Open();
GetComponent<DoorGate>().OpenImmediate();  // No animation
```

### To link to a puzzle:
Set `Linked Puzzle ID` to match the puzzle's `Puzzle ID` field. DoorGate auto-listens to `GameEvents.OnPuzzleSolved`.

---

## 26. World — ItemPickup

**File:** `World/ItemPickup.cs`

### Attach to: Any collectible item prefab with a Trigger Collider.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Item` | Drag the `ItemData.asset` this pickup contains |
| `Bob Height` | `0.15` |
| `Bob Speed` | `1.5` |
| `Rotate Speed` | `60` (degrees/second) |
| `Collect VFX` | Particle System that plays on collect |
| `Player Layer` | "Player" layer |

### Unity Steps:
1. Create a prefab with a mesh (use your Blender models), a Trigger SphereCollider, and `ItemPickup`
2. Set the collider layer to something visible but not "Enemy"
3. Spawn via `Instantiate` or place directly in the scene

---

## 27. World — CrystalPickup

**File:** `World/CrystalPickup.cs`

### Attach to: Each of the 6 crystal collectible prefabs.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Crystal Index` | `0` through `5` — each crystal must have a **unique index** |
| `Bob Height` | `0.2` |
| `Bob Speed` | `1.2` |
| `Rotate Speed` | `90` |
| `Collect VFX` | Crystal burst particle system |
| `Glow Light` | Child Point Light on the crystal |
| `Player Layer` | "Player" layer |

### HUD wiring:
`HUDManager` subscribes to `GameEvents.OnCrystalCollected` — make sure `HUDManager` has the 6 crystal slot icons assigned.

### How to reset between playthroughs:
```csharp
CrystalPickup.ResetCount();  // Call on New Game
```

---

## 28. World — BoatRepairStation

**File:** `World/BoatRepairStation.cs`

### Attach to: A repair zone on the dock (Trigger Collider).

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Repair Amount` | `50` (partial repair per use) |
| `Full Repair` | ✓ ON to always fully restore durability |
| `Has Cost` | ✓ ON if repair requires items |
| `Cost Item` | Drag the `ItemData.asset` for "Wood Plank" or similar |
| `Cost Amount` | `2` |
| `Cooldown` | `30` seconds before it can be used again |
| `Repair VFX` | Hammering/sparks particle system |
| `Repair SFX` | Wood-hammering audio clip |
| `Interact Indicator` | "Repair" label or wrench icon |

### Notes:
- If `Has Cost` is OFF, repair is free and instant.
- Calls `BoatStats.Repair(amount)` or `BoatStats.FullRepair()` based on `Full Repair` setting.
- Fires `GameEvents.BoatDurabilityChanged` automatically via `BoatStats`.

---

## 29. World — TutorialTrigger

**File:** `World/TutorialTrigger.cs`

### Attach to: Empty GameObjects placed around Tutorial Island.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Trigger ID` | Short unique string: `"tut_movement"`, `"tut_attack"`, etc. |
| `Message` | The hint text to display: `"Press WASD to move. Hold Shift to sprint."` |
| `Icon` | Optional sprite shown alongside the message |
| `Display Duration` | `4` seconds |
| `Show Once` | ✓ ON — saved to PlayerPrefs so it doesn't repeat |
| `Player Layer` | "Player" layer |

### `TutorialHintPanel` Setup:
1. Create a Canvas child panel named "TutorialHintPanel"
2. Add `TutorialHintPanel` component
3. Add `CanvasGroup`, a `TextMeshProUGUI`, and an optional `Image` for icon
4. Set panel inactive by default — `TutorialTrigger` auto-finds it via `FindObjectOfType`

### Suggested Tutorial Trigger IDs (place zones around the island):
```
"tut_movement"   → Near starting beach
"tut_combat"     → Near first enemy spawn
"tut_interact"   → Near first NPC/chest
"tut_boat"       → At the dock
"tut_map"        → First open ocean view
```

### Reset all triggers (New Game):
```csharp
TutorialTrigger.ResetAll();
```

---

## 30. Boat — HarpoonProjectile

**File:** `Boat/HarpoonProjectile.cs`

### Attach to: The harpoon projectile prefab (alongside Rigidbody + Collider).

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Damage` | `40` |
| `Hit Layers` | Layers to hit: Enemy + Boss + Default |
| `Enable Pull` | ✓ ON — pulls hit Rigidbody toward the boat |
| `Pull Force` | `8` |
| `Pull Duration` | `1.5` seconds |
| `Hit VFX` | Impact spark particle system |
| `Trail` | TrailRenderer component on the harpoon |

### Unity Steps:
1. Create a harpoon projectile prefab → add Rigidbody (`isKinematic = false`) + CapsuleCollider (isTrigger = true)
2. Add `HarpoonProjectile` component
3. In `BoatController` Inspector: drag this prefab into `Harpoon Projectile Prefab`
4. Register in `PoolManager`: key = `"Projectile_Harpoon"`, size = `5`

### How pull works:
On trigger enter, the projectile stops and applies `AddForce` toward the spawn point on the hit Rigidbody for `Pull Duration` seconds, then self-destroys.

---

## 31. Bosses — LavaBallProjectile & LavaPuddle

**File:** `Bosses/LavaBallProjectile.cs`

### LavaBallProjectile — Attach to: LavaBall prefab.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Direct Damage` | `30` |
| `Splash Damage` | `15` |
| `Splash Radius` | `2.5` |
| `Player Layer` | "Player" layer |
| `Leave Puddle` | ✓ ON |
| `Puddle Prefab` | LavaPuddle prefab with LavaPuddle script + Trigger Collider |
| `Puddle Duration` | `4` seconds |
| `Puddle Damage Per Second` | `8` |
| `Trail VFX` | Fire trail Particle System |
| `Impact VFX` | Lava explosion Particle System |

### LavaPuddle — Attach to: LavaPuddle prefab.
No Inspector setup — initialized by `LavaBallProjectile` via `Initialise(dps, layer)`.

### Unity Steps:
1. Create LavaBall prefab → Rigidbody + SphereCollider + `LavaBallProjectile`
2. Create LavaPuddle prefab → flat disc mesh + Trigger CylinderCollider + `LavaPuddle`
3. Register LavaBall in `PoolManager`: key = `"Projectile_LavaBall"`, size = `10`
4. Drag LavaBall prefab into `Ignar_MoltenDrake`'s `Lava Ball Prefab` field

---

## 33. UI — MainMenuController

**File:** `UI/MainMenuController.cs`

### Attach to: Root panel of the MainMenu Canvas.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Main Panel` | The main button panel GameObject |
| `Save Slot Panel` | The load-game slot selection panel (default inactive) |
| `New Game Button` | Button → "New Game" |
| `Continue Button` | Button → "Continue" (loads auto-save slot 0) |
| `Load Button` | Button → "Load Game" (opens save slot panel) |
| `Quit Button` | Button → "Quit" |
| `Slot 1/2/3 Button` | The three save slot buttons |
| `Slot 1/2/3 Label` | TMP texts showing save timestamps |
| `Version Text` | TMP text (auto-fills with `Application.version`) |

### Notes:
- Continue is only interactive if auto-save (slot 0) exists in `SaveManager`.
- New Game calls `GameManager.ChangeState(Sailing)` + `SceneLoader.LoadSceneAdditive("Ocean_World")`.

---

## 34. UI — PauseMenuController

**File:** `UI/PauseMenuController.cs`

### Attach to: The PauseMenuPanel Canvas child (default inactive).

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Pause Panel` | The panel root GameObject |
| `Resume Button` | "Resume" button |
| `Save Button` | "Save Game" button |
| `Main Menu Button` | "Main Menu" button |
| `Quit Button` | "Quit Game" button |
| `Save Confirm Text` | TMP text: "Game Saved!" (shown briefly) |
| `Save Confirm Display Time` | `2` seconds |

### Toggle Key: `Escape` (default). Blocked during GameOver and Cutscene states.

### To open pause from a button (e.g. in-game menu icon):
```csharp
FindObjectOfType<PauseMenuController>().Pause();
```

---

## 35. UI — GameOverScreen

**File:** `UI/GameOverScreen.cs`

### Attach to: The GameOverPanel Canvas child (default **inactive**).

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Canvas Group` | CanvasGroup on the panel root |
| `Fade In Duration` | `1.5` |
| `Delay Before Fade` | `0.8` (pause after player death before panel appears) |
| `Retry Button` | "Try Again" button |
| `Main Menu Button` | "Main Menu" button |
| `Death Message Text` | TMP text (auto-filled with a random death message) |

### How it works:
Subscribes to `GameEvents.OnPlayerDied` → fades in panel → Retry reloads from auto-save, Main Menu returns to main menu.

---

## 39. UI — MapUI

**File:** `UI/MapUI.cs`

### Attach to: The MapPanel Canvas child (default inactive).

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Map Panel` | The map overlay panel |
| `Toggle Key` | `M` key |
| `Map Rect` | RectTransform of the background map image |
| `World Size` | `(2000, 2000)` — matches your ocean world XZ dimensions |
| `Player Dot` | Small RectTransform dot for player position |
| `Player Transform` | Drag the Player GameObject (auto-found if null) |
| `Boat Dot` | Small RectTransform dot for boat position |
| `Boat Transform` | Drag the Boat GameObject (auto-found if null) |
| `Island Marker Prefab` | Prefab: Image + TMP label for discovered islands |
| `Marker Parent` | A parent Transform inside the map panel for markers |

### Island Markers:
Automatically created when `GameEvents.OnIslandDiscovered` fires. Call `PlaceIslandMarker(islandID, normalizedPos)` to position them precisely on your map texture.

---

## 32. Save System — SaveManager

**File:** `SaveSystem/SaveManager.cs`

### Attach to: The persistent manager GameObject in Bootstrap scene.

### No Inspector fields required.

### How to save/load from UI buttons:
```csharp
// In a save slot button's OnClick:
SaveManager.Instance.SaveGame(1);    // Slot 1

// In a load slot button's OnClick:
var data = SaveManager.Instance.LoadGame(1);
SaveManager.Instance.ApplySaveData(data);
```

### Where saves are stored:
`Application.persistentDataPath/saves/slot0.json` (auto-save)
`Application.persistentDataPath/saves/slot1.json`

---

## 36. UI — HUDManager

**File:** `UI/HUDManager.cs`

### Attach to: A Canvas child GameObject named **"HUD"**.

### Unity Steps (Canvas setup):
1. Create a Canvas (Screen Space — Overlay)
2. Add child Image for health bar (fill type = Horizontal Fill)
3. Add child Image for stamina bar
4. Add child Image for durability bar (inside a parent panel)
5. Add child Image for ability icon + a radial fill image on top for cooldown

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Health Fill` | Drag the health bar Image component |
| `Health Text` | Drag a TextMeshPro showing "100/100" |
| `Stamina Fill` | Drag the stamina Image |
| `Stamina Group` | Drag a CanvasGroup on the stamina bar panel |
| `Boat Durability Root` | Drag the entire boat durability panel |
| `Durability Fill` | Drag the boat durability Image |
| `Ability Icon` | Drag the ability icon Image |
| `Ability Cooldown Fill` | Drag a radial fill Image overlaying the ability icon |
| `Ability Name Text` | Drag a TMP text under the ability icon |
| `Crystal Count Text` | Drag a TMP showing "0/6" |
| `Crystal Slot Icons` | Drag 6 crystal icon Images (set inactive by default) |

---

## 37. UI — BossHealthBarUI

**File:** `UI/BossHealthBarUI.cs`

### Attach to: A UI panel named **"BossHealthBarPanel"** on the HUD Canvas.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Panel Group` | CanvasGroup on the panel root (for fade in/out) |
| `Panel Rect` | RectTransform of the panel |
| `Health Fill` | Image (fill type = Horizontal Fill) for boss HP |
| `Health Damage Fill` | Same size Image behind the HP fill (red/orange color) |
| `Boss Name Text` | TMP text showing "Ignar the Molten Drake" |
| `Phase Text` | TMP text showing "Phase I", "Phase II" |
| `Slide In Duration` | `0.5` |
| `Damage Fill Lag Speed` | `1.5` |

### Set panel active = false in default state.

---

## 38. UI — DialogueManager

**File:** `UI/DialogueManager.cs`

### Attach to: A UI panel named **"DialoguePanel"**.

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Dialogue Panel` | The panel root GameObject (active/inactive to show/hide) |
| `Speaker Name Text` | TMP text (e.g. "Old Fisherman") |
| `Body Text` | TMP text for dialogue line |
| `Speaker Portrait` | UI Image for character portrait |
| `Continue Indicator` | A small "Press E" icon that blinks |
| `Char Delay` | `0.03` (typewriter speed) |

### How to trigger from an NPC:
```csharp
// On your NPC GameObject, attach this:
public class NPC : MonoBehaviour, IInteractable
{
    [SerializeField] private DialogueSequence _dialogue;

    public void Interact(object interactor)
    {
        DialogueManager.Instance.StartDialogue(_dialogue);
    }
}
```

---

## 40. Audio — AudioManager

**File:** `Audio/AudioManager.cs`

### Attach to: Persistent manager GameObject in Bootstrap scene.

### Unity Steps:
1. Add two `AudioSource` components on the same GameObject (for crossfade A/B)
2. Add a third `AudioSource` for SFX

### Inspector Setup:
| Field | What to set |
|-------|-------------|
| `Music Source A` | First AudioSource component |
| `Music Source B` | Second AudioSource component |
| `SFX Source` | Third AudioSource component |
| `Master Volume` | `1.0` |
| `Music Volume` | `0.6` |
| `SFX Volume` | `1.0` |
| `Crossfade Duration` | `2` |

### How to play music from a scene:
```csharp
AudioManager.Instance.PlayMusic(myOceanClip, loop: true);
```

### How to play SFX:
```csharp
AudioManager.Instance.PlaySFX(hitSound);
AudioManager.Instance.PlaySFXAtPosition(splashSound, hitPosition);
```

---

## 41. Utilities — PoolManager

**File:** `Utilities/ObjectPool.cs`

### Attach to: Persistent manager GameObject in Bootstrap scene.

### Inspector Setup:
Add entries to `Pool Entries` for every spawnable object:

| Key | Prefab | Initial Size |
|-----|--------|-------------|
| `Projectile_Harpoon` | Harpoon projectile prefab | 5 |
| `Projectile_LavaBall` | Lava ball prefab | 10 |
| `VFX_FireBurst` | Fire burst particle prefab | 8 |
| `VFX_IceShatter` | Ice shatter particle prefab | 8 |
| `VFX_PuzzleSolve` | Star burst particle prefab | 4 |
| `VFX_BossHit` | Boss hit flash prefab | 6 |

### How to use in any script:
```csharp
// Spawn
var obj = PoolManager.Instance.Get("VFX_FireBurst", transform.position, Quaternion.identity);

// Return after 2 seconds
PoolManager.Instance.ReturnAfterDelay("VFX_FireBurst", obj, 2f);
```

---

## 42. Utilities — CameraShaker

**File:** `Utilities/CameraShaker.cs`

### Attach to: Your **CinemachineVirtualCamera** GameObject.

### Unity Steps:
1. On the CinemachineVirtualCamera → click **Add Extension** → choose **CinemachineBasicMultiChannelPerlin**
2. Set the Noise Profile to a "6D Shake" or "Handheld" profile from Cinemachine's built-in samples

### How to shake from any script:
```csharp
CameraShaker.Instance.ShakeLight();               // Small hit feedback
CameraShaker.Instance.ShakeMedium();              // Boss hit
CameraShaker.Instance.ShakeHeavy();               // Explosion / phase transition
CameraShaker.Instance.Shake(intensity: 2f, duration: 0.4f);  // Custom
```

---

## 43. Data — ScriptableObjects

### How to create ScriptableObjects:

**EnemyData:**
Right-click in Project window → `Create → IsleTrial → Enemy Data`
Fill in: EnemyID, EnemyName, MaxHealth, MoveSpeed, AttackDamage, DetectionRadius

**BossData:**
Right-click → `Create → IsleTrial → Boss Data`
Fill in: BossID, BossName, MaxHealth, Phase thresholds, UnlockedAbility, ArenaSceneName

**IslandData:**
Right-click → `Create → IsleTrial → Island Data`
Fill in: IslandID, IslandName, SceneName (exact scene name), BossSceneName, AssociatedBoss

**ItemData:**
Right-click → `Create → IsleTrial → Item Data`
Fill in: ItemID, ItemName, ItemType, EffectAmount, Icon sprite

**AbilityData:**
Right-click → `Create → IsleTrial → Ability Data`
Fill in: AbilityID, AbilityName, Type (select from enum), Cooldown, Damage, Icon

**DialogueSequence:**
Right-click → `Create → IsleTrial → Dialogue Sequence`
Fill in each line: SpeakerName, Text, optional Portrait sprite

**LootTable:**
Right-click → `Create → IsleTrial → Loot Table`
Add entries: each entry has an `ItemData`, a `Weight` (higher = more likely), and optional `Max Rolls`
Set `Empty Chance` (0–1) if you want a chance of no drop.
```csharp
// Roll one random item:
ItemData item = myLootTable.Roll();

// Roll multiple (e.g. chest with 2 items):
List<ItemData> items = myLootTable.RollMultiple(2);

// Guaranteed item (ignores empty chance):
ItemData item = myLootTable.RollGuaranteed();

// Reset between runs:
myLootTable.ResetRollCounts();
```

### Recommended Folder Structure:
```
Assets/_Game/ScriptableObjects/
  ├── Islands/       (IslandData assets)
  ├── Enemies/       (EnemyData assets)
  ├── Bosses/        (BossData assets)
  ├── Items/         (ItemData assets)
  ├── Abilities/     (AbilityData assets)
  ├── Dialogues/     (DialogueSequence assets)
  └── LootTables/    (LootTable assets)
```

---

## 44. Complete Bootstrap Scene Setup

The Bootstrap scene is the first scene that loads and persists everything.

### GameObjects in Bootstrap scene:

```
Bootstrap (scene root)
├── GameManager          [GameManager.cs, SceneLoader.cs, SaveManager.cs]
├── AudioManager         [AudioManager.cs + 3 AudioSource components]
├── PoolManager          [PoolManager.cs]
└── CameraRig (optional) [CinemachineBrain on MainCamera]
```

### Scene Load Order in Build Settings:
```
0: Bootstrap       ← loads first, always
1: MainMenu
2: Ocean_World
3: Island_00_Tutorial
4: Island_01_Ember
... (all island scenes)
... (all boss fight scenes)
```

### How Bootstrap auto-loads MainMenu:
Add this to GameManager:
```csharp
void Start()
{
    ChangeState(GameState.MainMenu);
    SceneLoader.Instance.LoadSceneAdditive("MainMenu");
}
```

---

## Quick Troubleshooting

| Problem | Solution |
|---------|---------|
| `NullReferenceException` on `Instance` | Check the Bootstrap scene loads first in Build Settings |
| Input not working | Regenerate `PlayerInputActions.cs` after editing the Input Actions asset |
| NavMesh agent not moving | Bake the NavMesh in Window → AI → Navigation → Bake |
| Scenes not loading additively | Add all scenes to File → Build Settings |
| Puzzle not detecting player | Check the Interactable layer is assigned and PlayerController's `_interactLayer` matches |
| Boss health bar not appearing | Confirm `GameEvents.BossEncountered()` is being called in `BossBase.Start()` |
| Pool key not found warning | Register the prefab in PoolManager's `Pool Entries` list |
| Camera not shaking | Add `CinemachineBasicMultiChannelPerlin` extension to the virtual camera |
| Door won't open after puzzle solved | Ensure `DoorGate._linkedPuzzleID` exactly matches `PuzzleBase._puzzleID` |
| Harpoon does nothing on hit | Check `HarpoonProjectile._hitLayers` includes the target's layer |
| Chest won't give items | Assign a `LootTable` asset to `ChestInteractable._lootTable` |
| NPC dialogue not starting | Assign a `DialogueSequence` to `NPC._dialogue` and confirm `DialogueManager` is in the scene |
| FrostSlug not slowing player | Confirm `PlayerStats` is on the Player GameObject (FrostSlug calls `ApplySpeedModifier`) |
| Tutorial hint not showing | Add `TutorialHintPanel` to the HUD Canvas; `TutorialTrigger` finds it via `FindObjectOfType` |
| Map not showing player dot | Assign `Player Transform` and `Map Rect` in `MapUI` Inspector |
| Loot Table always returns null | Check all entries have a valid `Item` assigned and `Empty Chance` is not 1.0 |
| Game Over screen not appearing | Confirm `GameOverScreen` is in the scene and `GameEvents.PlayerDied()` is firing |
| Pause menu blocks input | Ensure `PauseMenuController` calls `GameManager.ChangeState(Paused)` — check Time.timeScale is restored on Resume |

---

*Code Usage Guide Version: 2.0 | Last Updated: March 2026*
*Added: HarpoonProjectile, ItemPickup, CrystalPickup, NPC, ChestInteractable, DoorGate, LavaBallProjectile,*
*PauseMenuController, GameOverScreen, FrostSlug, Glaciara_FrostWarden, BoatRepairStation, MapUI, TutorialTrigger, LootTable*
