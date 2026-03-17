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
14. [Bosses — BossBase & Ignar](#14-bosses--bossbase--ignar)
15. [Puzzles — SymbolMatchPuzzle](#15-puzzles--symbolmatchpuzzle)
16. [Puzzles — LightBeamPuzzle](#16-puzzles--lightbeampuzzle)
17. [Puzzles — PushBlockPuzzle](#17-puzzles--pushblockpuzzle)
18. [World — WeatherSystem](#18-world--weathersystem)
19. [World — DayNightCycle](#19-world--daynightcycle)
20. [World — IslandProximityLoader](#20-world--islandproximityloader)
21. [Save System — SaveManager](#21-save-system--savemanager)
22. [UI — HUDManager](#22-ui--hudmanager)
23. [UI — BossHealthBarUI](#23-ui--bosshealthbarui)
24. [UI — DialogueManager](#24-ui--dialoguemanager)
25. [Audio — AudioManager](#25-audio--audiomanager)
26. [Utilities — PoolManager](#26-utilities--poolmanager)
27. [Utilities — CameraShaker](#27-utilities--camerashaker)
28. [Data — ScriptableObjects](#28-data--scriptableobjects)
29. [Complete Bootstrap Scene Setup](#29-complete-bootstrap-scene-setup)

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

## 14. Bosses — BossBase & Ignar

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

## 15. Puzzles — SymbolMatchPuzzle

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

## 16. Puzzles — LightBeamPuzzle

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

## 17. Puzzles — PushBlockPuzzle

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

## 18. World — WeatherSystem

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

## 19. World — DayNightCycle

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

## 20. World — IslandProximityLoader

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

## 21. Save System — SaveManager

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

## 22. UI — HUDManager

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

## 23. UI — BossHealthBarUI

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

## 24. UI — DialogueManager

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

## 25. Audio — AudioManager

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

## 26. Utilities — PoolManager

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

## 27. Utilities — CameraShaker

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

## 28. Data — ScriptableObjects

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

### Recommended Folder Structure:
```
Assets/_Game/ScriptableObjects/
  ├── Islands/       (IslandData assets)
  ├── Enemies/       (EnemyData assets)
  ├── Bosses/        (BossData assets)
  ├── Items/         (ItemData assets)
  ├── Abilities/     (AbilityData assets)
  └── Dialogues/     (DialogueSequence assets)
```

---

## 29. Complete Bootstrap Scene Setup

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

---

*Code Usage Guide Version: 1.0 | Last Updated: March 2026*
