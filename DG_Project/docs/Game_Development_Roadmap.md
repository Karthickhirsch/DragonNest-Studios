# IsleTrial — Game Development Roadmap
## What To Do Next & In What Order

---

## Current Project Status

| Area | Status | Location |
|---|---|---|
| C# Scripts (55 files) | ✅ Complete | `Code/` |
| Code Usage Guide | ✅ Complete | `Code/CODE_USAGE_GUIDE.md` |
| Blender Model Prompts | ✅ Complete | `Blender_Prompts/` |
| Blender Boat Script | ✅ Generated | `Blender_Scripts/01_Boat_MainVessel.py` |
| Unity Project | ❌ Not Started | — |
| 3D Models (FBX) | ❌ Not Started | — |
| Animations | ❌ Not Started | — |
| Audio & SFX | ❌ Not Started | — |
| ScriptableObject Assets | ❌ Not Started | — |
| Input Actions Asset | ❌ Not Started | — |
| Unity Scenes | ❌ Not Started | — |

---

## Phase 1 — Unity Project Foundation
> **Do this before anything else. All other phases depend on it.**

### Step 1: Create the Project
```
Unity Hub → New Project → 3D (URP) template
Name: IsleTrial
Location: anywhere outside this Code folder
```

### Step 2: Install Required Packages
Go to `Window → Package Manager → Unity Registry` and install:

| Package | Purpose |
|---|---|
| `Input System` | PlayerInputHandler.cs depends on this |
| `Cinemachine` | CameraShaker.cs depends on this |
| `TextMeshPro` | All UI scripts use TMP |
| `AI Navigation` | EnemyBase.cs uses NavMeshAgent |
| `Addressables` | SceneLoader.cs uses async loading |

> When Unity asks "Enable New Input System?" — click **YES** and let it restart.

### Step 3: Copy Scripts
```
Copy the entire Code/ folder → paste into Assets/ in your Unity project
Unity will compile all 55 scripts automatically
```

### Step 4: Create Input Actions Asset
```
1. Right-click in Project window → Create → Input Actions
2. Name it: PlayerInputActions
3. Add Action Maps:
   - Player  (Move, Attack, Dodge, Interact, Sprint, UseAbility)
   - Boat    (Steer, Boost, Anchor, Harpoon, Lantern)
   - UI      (Navigate, Submit, Cancel, Pause)
4. Click "Generate C# Class" at the top of the asset
5. Save
```

### Step 5: Create Layers & Tags
Go to `Edit → Project Settings → Tags and Layers` and add:

| Layers | Tags |
|---|---|
| Player | Player |
| Enemy | Enemy |
| Interactable | Boat |
| GrapplePoint | NPC |
| Reflect | Destructible |

### Step 6: Set Up Bootstrap Scene
```
File → New Scene → Save as "Bootstrap"
Add to Build Settings FIRST (index 0)
```

Create these GameObjects in Bootstrap:

```
Bootstrap (scene root)
├── GameManager
│     Components: GameManager.cs + SceneLoader.cs + SaveManager.cs
│
├── AudioManager
│     Components: AudioManager.cs + AudioSource x3
│
├── PoolManager
│     Components: PoolManager.cs
│     Pool Entries:
│       - "Projectile_Harpoon"   prefab: HarpoonPrefab     size: 5
│       - "Projectile_LavaBall"  prefab: LavaBallPrefab    size: 10
│       - "VFX_FireBurst"        prefab: FireBurstVFX      size: 8
│       - "VFX_IceShatter"       prefab: IceShatterVFX     size: 8
│       - "VFX_PuzzleSolve"      prefab: PuzzleSolveVFX    size: 4
│       - "VFX_BossHit"          prefab: BossHitVFX        size: 6
│
└── CameraRig
      Components: Camera + CinemachineBrain
```

### Step 7: Build Settings Scene Order
```
File → Build Settings → drag scenes in this order:
  0: Bootstrap
  1: MainMenu
  2: Ocean_World
  3: Island_00_Tutorial
  4: Island_01_Ember
  5: Island_01_Ember_Boss
  6: Island_02_Frost
  7: Island_02_Frost_Boss
```

---

## Phase 2 — 3D Models via Blender
> Use the prompts in `Blender_Prompts/` — see `README.md` in that folder for how to use them.

### Build models in this order:

| Priority | Prompt File | Models | Why First |
|---|---|---|---|
| 1 | `01_Boat_MainVessel.md` | Boat hull, cabin, mast, harpoon, lantern, anchor | Player controls this from second one |
| 2 | `02_Environment_Island_Dock.md` | Island terrain, dock/pier, rocks, lighthouse | Needed for first scene |
| 3 | `03_Props_And_Pickups.md` | Harpoon, barrel, crate, chest, lanterns | Gameplay items |
| 4 | `04_Sea_Creatures.md` | Fish, whale, shark, small fish school | Harpoon targets |
| 5 | `05_Ocean_And_Weather_Assets.md` | Buoys, shipwreck, storm debris | World polish |

### Blender → Unity Export Settings
```
File → Export → FBX

Scale:              0.01
Apply Transform:    ✓ ON
Forward:            -Z Forward
Up:                 Y Up
Include:            Mesh + Armature (for creatures)
```

### Unity FBX Import Settings
After dragging FBX into Unity Project window:

```
Scale Factor:              0.01
Convert Units:             ✓ ON
Import Normals:            Import
Generate Lightmap UVs:     ✓ ON
Mesh Compression:          Low
Read/Write Enabled:        ✓ ON
```

For creatures with bones:
```
Animation Type:            Generic
Import BlendShapes:        ✓ ON
Optimize Game Objects:     OFF
```

---

## Phase 3 — ScriptableObject Data Assets
> Create these inside Unity. Right-click in Project window → Create → IsleTrial → [type]

### Islands

| Asset Name | IslandID | IslandName | SceneName | BossSceneName |
|---|---|---|---|---|
| `Island_Tutorial.asset` | `isle_tutorial` | Tutorial Island | `Island_00_Tutorial` | *(none)* |
| `Island_Ember.asset` | `isle_ember` | Ember Isle | `Island_01_Ember` | `Island_01_Ember_Boss` |
| `Island_Frost.asset` | `isle_frost` | Frost Isle | `Island_02_Frost` | `Island_02_Frost_Boss` |

### Enemies

| Asset Name | EnemyID | MaxHealth | MoveSpeed | AttackDamage | Detection |
|---|---|---|---|---|---|
| `EmberLizard.asset` | `enemy_ember_lizard` | 60 | 4 | 15 | 8 |
| `FrostSlug.asset` | `enemy_frost_slug` | 80 | 2.5 | 12 | 7 |

### Bosses

| Asset Name | BossID | BossName | MaxHealth | UnlockedAbility |
|---|---|---|---|---|
| `Ignar.asset` | `boss_ignar` | Ignar the Molten Drake | 800 | Fire Dash AbilityData |
| `Glaciara.asset` | `boss_glaciara` | Glaciara the Frost Warden | 1000 | Ice Shield AbilityData |

### Items

| Asset Name | ItemID | ItemName | ItemType | EffectAmount |
|---|---|---|---|---|
| `HealthPotion.asset` | `item_health_potion` | Health Potion | HealthPotion | 50 |
| `WoodPlank.asset` | `item_wood_plank` | Wood Plank | Material | 0 |
| `IceShard.asset` | `item_ice_shard` | Ice Shard | Material | 0 |
| `GoldCoin.asset` | `item_gold_coin` | Gold Coin | Currency | 1 |
| `AntidoteBerry.asset` | `item_antidote` | Antidote Berry | AntidoteBerry | 0 |

### Abilities (5 total — one per boss + extras)

| Asset Name | AbilityID | Type | Cooldown | Damage |
|---|---|---|---|---|
| `FireDash.asset` | `ability_fire_dash` | FireDash | 8 | 30 |
| `IceShield.asset` | `ability_ice_shield` | IceShield | 12 | 0 |
| `VineGrapple.asset` | `ability_vine_grapple` | VineGrapple | 6 | 0 |
| `LightningStrike.asset` | `ability_lightning` | LightningStrike | 10 | 50 |
| `TidalWave.asset` | `ability_tidal_wave` | TidalWave | 15 | 40 |

### LootTables

| Asset Name | Use For | Entries |
|---|---|---|
| `LootTable_Chest_Basic.asset` | Normal chests | HealthPotion (40%), WoodPlank (35%), GoldCoin (25%) |
| `LootTable_Chest_Boss.asset` | Post-boss chests | HealthPotion x2 (50%), AbilityData item (50%) |
| `LootTable_Enemy_Ember.asset` | EmberLizard drops | GoldCoin (60%), nothing (40%) |
| `LootTable_Enemy_Frost.asset` | FrostSlug drops | IceShard (50%), GoldCoin (30%), nothing (20%) |

### Recommended Folder Structure in Unity
```
Assets/
└── _Game/
    ├── Scripts/           ← paste Code/ contents here
    ├── Models/            ← FBX exports from Blender
    ├── Animations/        ← Animator controllers + clips
    ├── Audio/
    │   ├── Music/
    │   └── SFX/
    ├── Prefabs/
    │   ├── Player/
    │   ├── Boat/
    │   ├── Enemies/
    │   ├── Bosses/
    │   ├── Props/
    │   └── VFX/
    ├── Materials/
    ├── Textures/
    └── ScriptableObjects/
        ├── Islands/
        ├── Enemies/
        ├── Bosses/
        ├── Items/
        ├── Abilities/
        ├── Dialogues/
        └── LootTables/
```

---

## Phase 4 — Scene Building
> Build scenes in this order — each one depends on the previous.

### Scene 1: MainMenu
```
Canvas (Screen Space Overlay)
└── MainMenuPanel
      Components: MainMenuController.cs
      Children:
        - Title Text (TMP): "Isle of Trials"
        - New Game Button
        - Continue Button
        - Load Button → opens SaveSlotPanel
        - Quit Button
        - Version Text (TMP)
      SaveSlotPanel (default inactive):
        - Slot1 Button + Slot1 Label (TMP)
        - Slot2 Button + Slot2 Label (TMP)
        - Slot3 Button + Slot3 Label (TMP)
        - Back Button
```

### Scene 2: Ocean_World
```
Directional Light (Sun)
WeatherManager   [WeatherSystem.cs + DayNightCycle.cs]
Ocean Plane      [200m x 200m, Ocean shader material]
Boat Prefab      [BoatController + BoatStats + OceanBuoyancy + Rigidbody]
Island Markers   (empty GameObjects at island positions with IslandProximityLoader.cs)
  - Island_Marker_Tutorial   [IslandData: Island_Tutorial.asset]
  - Island_Marker_Ember      [IslandData: Island_Ember.asset]
  - Island_Marker_Frost      [IslandData: Island_Frost.asset]
CinemachineVirtualCamera    [follows Boat_ROOT]
HUD Canvas       [HUDManager + BossHealthBarUI + PauseMenuController + GameOverScreen + MapUI]
```

### Scene 3: Island_00_Tutorial
```
Terrain          (from Blender island export)
Dock             (from Blender dock export)
NavMesh Surface  (bake in Window → AI → Navigation)

Player Spawn     (empty Transform, tagged "SpawnPoint")

NPCs:
  - OldFisherman (NPC.cs, DialogueSequence: intro dialogue)

Props:
  - Barrel x3 (no interaction)
  - Crate x2  (no interaction)
  - TreasureChest (ChestInteractable, LootTable: Chest_Basic)

Puzzles:
  - PushBlockPuzzle_01 → linked DoorGate_01 (opens beach cave)

Tutorial Triggers (TutorialTrigger.cs):
  - tut_movement    (near spawn)
  - tut_interact    (near NPC)
  - tut_combat      (near dummy target)
  - tut_boat        (at dock)

Repair Station   (BoatRepairStation.cs, free repair, no cost)
Crystal_01       (CrystalPickup, crystalIndex: 0)
```

### Scene 4: Island_01_Ember (+ Boss Scene)
```
Terrain (volcanic, dark rocks)
NavMesh Surface

Enemies:
  - EmberLizard x6 (patrol groups of 2)

Props:
  - TreasureChest x2 (LootTable: Chest_Basic)

Puzzles:
  - SymbolMatchPuzzle_01 → opens gate to boss arena

Crystal_02 (crystalIndex: 1)

--- Island_01_Ember_Boss scene ---
Ignar Boss Arena:
  - Ignar Prefab (Ignar_MoltenDrake.cs)
  - Lava Plane (rising mesh, assigned to Ignar._lavaPlane)
  - Arena floor tiles (array assigned to Ignar._floorTiles)
  - BossMusic AudioSource
  - WeatherSystem override: Stormy on Phase 2
```

### Scene 5: Island_02_Frost (+ Boss Scene)
```
Terrain (icy, snow-covered)
NavMesh Surface

Enemies:
  - FrostSlug x6

Props:
  - TreasureChest x2 (LootTable: Chest_Basic)
  - IceCrystal pickups as environment dressing

Puzzles:
  - LightBeamPuzzle_01 → opens path to boss

Crystal_03 (crystalIndex: 2)

--- Island_02_Frost_Boss scene ---
Glaciara Arena:
  - Glaciara Prefab (Glaciara_FrostWarden.cs)
  - Ice Wall Spawn Points (3 Transforms around arena)
  - Blizzard VFX (full arena particle system)
```

---

## Phase 5 — Animations

### Player Animator Controller
```
States needed:
  Idle        → default
  Walk        → Speed > 0.1 (float param)
  Run         → Speed > 0.8
  Attack      → Trigger: Attack
  ChargedAtk  → Trigger: ChargedAttack
  Dodge       → Trigger: Dodge
  Dead        → Trigger: Dead
  Ability     → Trigger: UseAbility (per ability type)
```

### Enemy Animator Controllers (EmberLizard & FrostSlug)
```
States needed:
  Idle
  Walk        → NavMeshAgent.velocity.magnitude > 0.1
  Attack      → Trigger: Attack
  Stun        → Trigger: Stun
  Dead        → Trigger: Dead
```

### Boss Animator Controllers
```
Ignar:
  Idle, Phase (Int: 1/2/3), TailSlam, Dive, DiveLand, Charge, Hit, Dead

Glaciara:
  Idle, Phase (Int: 1/2/3), Shoot, Charge, Blizzard, Hit, Dead
```

### Boat — No Animator Needed
The boat uses Rigidbody physics + OceanBuoyancy. Only the sail cloth simulation in Blender needs to be applied.

---

## Phase 6 — Audio

### Minimum Audio Assets Needed

| Sound | Type | Where Used |
|---|---|---|
| `ocean_ambient.wav` | Music loop | Ocean_World scene |
| `island_ambient_ember.wav` | Music loop | Island_01_Ember |
| `island_ambient_frost.wav` | Music loop | Island_02_Frost |
| `boss_ignar.wav` | Music loop | Boss fight scenes |
| `boss_glaciara.wav` | Music loop | Glaciara fight |
| `player_attack.wav` | SFX | PlayerController |
| `player_hit.wav` | SFX | PlayerStats.TakeDamage |
| `player_dodge.wav` | SFX | PlayerController |
| `player_death.wav` | SFX | GameEvents.PlayerDied |
| `boat_sail.wav` | SFX loop | BoatController (moving) |
| `boat_boost.wav` | SFX | BoatController.HandleBoost |
| `harpoon_fire.wav` | SFX | BoatController.HandleHarpoon |
| `harpoon_hit.wav` | SFX | HarpoonProjectile |
| `chest_open.wav` | SFX | ChestInteractable |
| `puzzle_solved.wav` | SFX | PuzzleBase.CompletePuzzle |
| `door_open.wav` | SFX | DoorGate |
| `crystal_collect.wav` | SFX | CrystalPickup |
| `boss_phase_change.wav` | SFX | BossBase.TransitionToPhase |
| `ui_click.wav` | SFX | All UI buttons |

### How to wire audio
```csharp
// In any script:
AudioManager.Instance.PlaySFX(hitSound);
AudioManager.Instance.PlaySFXAtPosition(splashSound, position);
AudioManager.Instance.PlayMusic(oceanAmbient, loop: true);
```

---

## Phase 7 — Testing Checklist

Work through this before calling the game complete:

### Core Loop
```
[ ] Player spawns in Tutorial Island correctly
[ ] Player can move, sprint, dodge, attack
[ ] Player health depletes and regenerates
[ ] Player dies → GameOver screen appears → Retry works
[ ] Boat moves with WASD, turns, boosts
[ ] Boat harpoon fires → hits enemy → deals damage
[ ] Boat lantern toggles on/off
[ ] Boat anchor stops movement
[ ] Ocean buoyancy makes boat bob correctly
[ ] WeatherSystem changes wind → affects boat speed
```

### Progression
```
[ ] Tutorial NPC dialogue triggers and plays
[ ] Tutorial puzzle can be completed → door opens
[ ] Tutorial chest opens → item added to inventory
[ ] Crystal collected → HUD slot fills
[ ] Sailing to Ember Isle triggers proximity load
[ ] EmberLizard detects, chases, attacks player
[ ] EmberLizard explodes on death
[ ] Symbol puzzle solved → gate to boss opens
[ ] Ignar boss fight: all 3 phases trigger correctly
[ ] Ignar defeated → ability unlocks → save triggers
[ ] Sailing to Frost Isle → FrostSlug levels
[ ] FrostSlug armour absorbs 2 hits, then takes damage
[ ] FrostSlug slows player on hit
[ ] LightBeam puzzle solved → path to Glaciara opens
[ ] Glaciara fight: ice shards, walls, blizzard all work
[ ] Glaciara defeated → second ability unlocks
```

### UI
```
[ ] HUD shows health, stamina, boat durability, crystals
[ ] Boss HP bar slides in when boss spawns
[ ] Pause menu opens with ESC → all buttons work
[ ] Map shows player dot, boat dot, discovered islands
[ ] Game saved → "Game Saved!" message appears
[ ] Load game restores player position and inventory
[ ] Tutorial hints appear and fade correctly
```

---

## Quick Reference — Key Script Connections

```
BoatController._harpoonSpawnPoint  → Boat_HarpoonMount child Transform
BoatController._lanternLight       → Boat_Lantern → Point Light child
BoatController (WeatherSystem)     → WeatherSystem.SetWind() called by WeatherSystem
IslandProximityLoader._islandData  → IslandData ScriptableObject asset
DoorGate._linkedPuzzleID           → must match PuzzleBase._puzzleID exactly
ChestInteractable._lootTable       → LootTable ScriptableObject asset
Ignar._lavaPlane                   → the rising lava mesh in boss arena
BossData.UnlockedAbility           → AbilityData ScriptableObject asset
```

---

## Estimated Time Per Phase

| Phase | Estimated Time | Difficulty |
|---|---|---|
| Phase 1 — Unity Setup | 1–2 hours | Easy |
| Phase 2 — 3D Models (Blender + AI) | 3–7 days | Medium |
| Phase 3 — ScriptableObjects | 2–3 hours | Easy |
| Phase 4 — Scene Building | 3–5 days | Medium |
| Phase 5 — Animations | 2–4 days | Hard |
| Phase 6 — Audio | 1–2 days | Easy |
| Phase 7 — Testing & Fixing | 3–5 days | Medium |
| **Total** | **~3–4 weeks** | |

---

*IsleTrial Development Roadmap — March 2026*
*Start with Phase 1. Each phase unlocks the next.*
