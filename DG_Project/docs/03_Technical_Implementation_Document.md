# Technical Implementation Document
## Isle of Trials — Unity Architecture & Systems

---

## Table of Contents
1. [Unity Project Setup](#unity-project-setup)
2. [Scene Architecture](#scene-architecture)
3. [Core Systems](#core-systems)
4. [Player System](#player-system)
5. [Boat System](#boat-system)
6. [Enemy & AI System](#enemy--ai-system)
7. [Puzzle System](#puzzle-system)
8. [Boss Fight System](#boss-fight-system)
9. [Sea & Environment System](#sea--environment-system)
10. [Save & Load System](#save--load-system)
11. [UI System](#ui-system)
12. [Audio System](#audio-system)
13. [Performance Guidelines](#performance-guidelines)
14. [Folder Structure](#folder-structure)

---

## 1. Unity Project Setup

### 1.1 Unity Version
- **Recommended:** Unity 2022.3 LTS or Unity 6 (6000.x)
- **Render Pipeline:** Universal Render Pipeline (URP)
- **Target Resolution:** 1920x1080 (PC), 1280x720 (Mobile)
- **Target Frame Rate:** 60 FPS (PC), 30 FPS (Mobile)

### 1.2 Required Packages
```
com.unity.inputsystem                  (New Input System)
com.unity.cinemachine                  (Camera management)
com.unity.render-pipelines.universal   (URP)
com.unity.textmeshpro                  (UI Text)
com.unity.addressables                 (Asset management)
com.unity.ai.navigation                (NavMesh AI)
com.unity.postprocessing               (Visual polish)
com.unity.timeline                     (Cutscenes)
com.unity.audio.dsp-graph              (Advanced audio — optional)
```

### 1.3 Third-Party Packages (Asset Store)
```
DOTween Pro         — Animation/tweening
FMOD Unity          — Advanced audio
Odin Inspector      — Editor tooling
Febucci Text Animator — Dialogue text effects (optional)
```

---

## 2. Scene Architecture

### 2.1 Scene List

| Scene Name | Purpose |
|------------|---------|
| `Bootstrap` | First scene; loads GameManager, global services |
| `MainMenu` | Title screen, settings, load game |
| `Ocean_World` | Main open sea; additive loading of islands |
| `Island_00_Tutorial` | Driftwood Cay |
| `Island_01_Ember` | Ember Isle |
| `Island_02_Frost` | Frostveil Atoll |
| `Island_03_Jungle` | Thornwood Reach |
| `Island_04_Desert` | Dunestone Bay |
| `Island_05_Storm` | Stormcrest Peak |
| `Island_06_Final` | Aethermoor |
| `BossFight_XX` | Boss arenas loaded additively |
| `Cutscene_XX` | Cutscene scenes (Timeline-driven) |

### 2.2 Additive Scene Loading
```csharp
// Islands are loaded additively when the player approaches
SceneManager.LoadSceneAsync("Island_01_Ember", LoadSceneMode.Additive);
// Unloaded when the player sails away (beyond threshold distance)
SceneManager.UnloadSceneAsync("Island_01_Ember");
```

### 2.3 Scene Loading Manager
```
SceneLoadManager.cs
  ├── LoadIsland(string islandSceneName)
  ├── UnloadIsland(string islandSceneName)
  ├── LoadBossArena(string bossSceneName)
  ├── ShowLoadingScreen()
  └── HideLoadingScreen()
```

---

## 3. Core Systems

### 3.1 GameManager (Singleton)
```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    public GameState CurrentState { get; private set; }
    public PlayerData PlayerData { get; private set; }
    public IslandRegistry IslandRegistry { get; private set; }

    public void ChangeState(GameState newState) { ... }
}

public enum GameState
{
    MainMenu,
    Sailing,
    OnIsland,
    BossFight,
    Cutscene,
    Paused,
    GameOver
}
```

### 3.2 EventSystem (Observer Pattern)
All major game events are broadcast via a central event bus to decouple systems.
```csharp
public static class GameEvents
{
    public static event Action<IslandData> OnIslandDiscovered;
    public static event Action<BossData> OnBossDefeated;
    public static event Action<CrystalData> OnCrystalCollected;
    public static event Action<int> OnPlayerHealthChanged;
    public static event Action OnPlayerDied;
    public static event Action<PuzzleData> OnPuzzleSolved;
    public static event Action<string> OnSceneLoaded;

    public static void TriggerBossDefeated(BossData data) 
        => OnBossDefeated?.Invoke(data);
    // etc.
}
```

### 3.3 Service Locator
```csharp
public static class ServiceLocator
{
    private static Dictionary<Type, object> _services = new();

    public static void Register<T>(T service) 
        => _services[typeof(T)] = service;

    public static T Get<T>() 
        => (T)_services[typeof(T)];
}
```

---

## 4. Player System

### 4.1 Player Controller (On Island)
```
PlayerController.cs
  ├── HandleMovement()       — CharacterController-based movement
  ├── HandleCombat()         — Attack, dodge
  ├── HandleInteraction()    — Raycast-based E/interact
  ├── HandleAbility()        — Per-island special ability
  └── HandleStamina()        — Stamina depletion/regen

PlayerStats.cs
  ├── int MaxHealth
  ├── int CurrentHealth
  ├── float MoveSpeed
  ├── float DodgeSpeed
  ├── float AttackDamage
  └── void TakeDamage(int amount)

PlayerInventory.cs
  ├── List<ItemData> Items
  ├── AddItem(ItemData)
  ├── RemoveItem(ItemData)
  └── HasItem(string itemId)
```

### 4.2 Player Abilities (Unlocked per Island)
| Island | Ability Unlocked | Description |
|--------|-----------------|-------------|
| Ember Isle | **Fire Dash** | Dash through enemies, leaving fire trail |
| Frostveil | **Ice Shield** | Temporary freeze protection, reflect projectiles |
| Thornwood | **Vine Grapple** | Grapple to anchor points across gaps |
| Dunestone | **Sand Veil** | Brief invisibility / enemy detection immunity |
| Stormcrest | **Lightning Strike** | Ranged AoE lightning slam |

### 4.3 Input System Mapping
```csharp
// Using Unity New Input System
public class PlayerInputHandler : MonoBehaviour
{
    private PlayerInputActions _inputActions;

    void Awake()
    {
        _inputActions = new PlayerInputActions();
        _inputActions.Player.Move.performed += OnMove;
        _inputActions.Player.Attack.performed += OnAttack;
        _inputActions.Player.Dodge.performed += OnDodge;
        _inputActions.Player.Interact.performed += OnInteract;
        _inputActions.Player.Ability.performed += OnAbility;
    }
}
```

---

## 5. Boat System

### 5.1 Boat Controller
```
BoatController.cs
  ├── HandleSailing()        — Physics-based movement (Rigidbody)
  ├── HandleWind()           — Wind direction affects speed multiplier
  ├── HandleBoost()          — Burst speed, cooldown timer
  ├── HandleAnchor()         — Toggle anchor state
  ├── HandleHarpoon()        — Fire harpoon projectile
  ├── HandleLantern()        — Toggle lantern light radius
  └── HandleDamage()         — Collision with hazards

BoatStats.cs
  ├── float MaxSpeed
  ├── float CurrentDurability
  ├── float MaxDurability
  ├── int BoostCharges
  └── void RepairBoat(float amount)
```

### 5.2 Ocean Physics
```csharp
// Buoyancy simulation using wave height sampling
public class OceanBuoyancy : MonoBehaviour
{
    [SerializeField] private float _waveHeight = 1.5f;
    [SerializeField] private float _waveFrequency = 0.5f;
    [SerializeField] private Transform[] _floatPoints;

    private Rigidbody _rb;

    void FixedUpdate()
    {
        foreach (var point in _floatPoints)
        {
            float waveY = GetWaveHeight(point.position.x, point.position.z);
            if (point.position.y < waveY)
            {
                float submersion = waveY - point.position.y;
                _rb.AddForceAtPosition(Vector3.up * submersion * 9.81f, point.position);
            }
        }
    }

    private float GetWaveHeight(float x, float z)
    {
        return Mathf.Sin(x * _waveFrequency + Time.time) * _waveHeight
             + Mathf.Sin(z * _waveFrequency * 0.7f + Time.time * 1.3f) * _waveHeight * 0.5f;
    }
}
```

### 5.3 Sea Creature Collision
- Sea creatures target the boat using NavMesh agents (adapted for ocean).
- Collision with creature reduces boat durability.
- Harpoon can stun/repel creatures temporarily.

---

## 6. Enemy & AI System

### 6.1 Enemy Base Class
```csharp
public abstract class EnemyBase : MonoBehaviour
{
    [SerializeField] protected EnemyData _data;
    protected EnemyStateMachine _stateMachine;
    protected Transform _playerTarget;

    protected virtual void Start()
    {
        _stateMachine = new EnemyStateMachine();
        _stateMachine.Initialize(new EnemyIdleState(this));
    }

    public abstract void Attack();
    public virtual void TakeDamage(int damage) { ... }
    public virtual void Die() { ... }
}
```

### 6.2 Enemy State Machine
```
States:
  ├── EnemyIdleState      — Patrols waypoints, plays idle animation
  ├── EnemyAlertState     — Player detected; moves toward player
  ├── EnemyAttackState    — Within attack range; executes attack pattern
  ├── EnemyStunState      — Hit by puzzle/harpoon; brief pause
  └── EnemyDeadState      — Death animation, drop loot, destroy

Transitions:
  Idle → Alert        (PlayerEntersDetectionRadius)
  Alert → Attack      (PlayerEntersAttackRadius)
  Attack → Alert      (PlayerExitsAttackRadius)
  Any → Stun          (StunEffect applied)
  Any → Dead          (HP reaches 0)
```

### 6.3 Sea Creature Types
| Creature | Behavior | Threat |
|----------|----------|--------|
| Coral Jellyfish | Drifts slowly, stuns on contact | Low |
| Razorfin Shark | Chases boat aggressively | Medium |
| Tide Serpent | Patrols routes, lunges | High |
| Abyssal Kraken Shard | Grabs boat, locks movement | Very High |
| Storm Ray | Flies above, drops lightning bolts | High |

---

## 7. Puzzle System

### 7.1 Puzzle Framework
```csharp
public abstract class PuzzleBase : MonoBehaviour
{
    public string PuzzleID;
    public bool IsSolved { get; private set; }

    public event Action<string> OnPuzzleSolved;

    protected void MarkSolved()
    {
        IsSolved = true;
        OnPuzzleSolved?.Invoke(PuzzleID);
        GameEvents.TriggerPuzzleSolved(new PuzzleData(PuzzleID));
    }

    public abstract void Initialize();
    public abstract void OnPlayerInteract(PlayerController player);
    public abstract void Reset();
}
```

### 7.2 Puzzle Types & Implementation

#### Symbol Match Puzzle
```csharp
public class SymbolMatchPuzzle : PuzzleBase
{
    [SerializeField] private List<SymbolTile> _tiles;
    [SerializeField] private List<SymbolData> _solution;

    public override void OnPlayerInteract(PlayerController player)
    {
        // Rotate tile to next symbol
        // Check if current arrangement matches solution
        if (CheckSolution()) MarkSolved();
    }

    private bool CheckSolution()
    {
        for (int i = 0; i < _tiles.Count; i++)
            if (_tiles[i].CurrentSymbol != _solution[i]) return false;
        return true;
    }
}
```

#### Light Beam Puzzle
```csharp
public class LightBeamPuzzle : PuzzleBase
{
    [SerializeField] private LightSource _source;
    [SerializeField] private List<Mirror> _mirrors;
    [SerializeField] private LightReceiver _target;

    void Update()
    {
        // Raycast from source, bounce off mirrors, check if target hit
        SimulateBeam();
    }

    private void SimulateBeam() { ... }
}
```

### 7.3 Puzzle State Persistence
```csharp
// Puzzle states are saved in PuzzleSaveData
[Serializable]
public class PuzzleSaveData
{
    public string PuzzleID;
    public bool IsSolved;
    public List<int> CurrentState; // Stores puzzle-specific state
}
```

---

## 8. Boss Fight System

### 8.1 Boss Base Class
```csharp
public abstract class BossBase : MonoBehaviour
{
    [SerializeField] protected BossData _data;
    protected BossPhase _currentPhase;
    protected int _currentHealth;

    public event Action<BossBase> OnBossDefeated;

    protected abstract void EnterPhase(BossPhase phase);
    protected abstract void ExecuteAttackPattern();
    public abstract void TakeDamage(int damage);

    protected void CheckPhaseTransition()
    {
        float healthPercent = (float)_currentHealth / _data.MaxHealth;
        if (healthPercent <= 0.5f && _currentPhase == BossPhase.Phase1)
            EnterPhase(BossPhase.Phase2);
        else if (healthPercent <= 0.2f && _currentPhase == BossPhase.Phase2)
            EnterPhase(BossPhase.Phase3);
    }
}

public enum BossPhase { Phase1, Phase2, Phase3 }
```

### 8.2 Boss Arena
- Boss arenas are separate scenes loaded additively during transition.
- Cinemachine camera switches to boss-focused framing on entry.
- Arena boundaries enforced by invisible colliders.
- Boss health bar UI activates on arena entry.

### 8.3 Boss Attack Patterns
```csharp
// Attack patterns are ScriptableObjects for easy tuning
[CreateAssetMenu(menuName = "Boss/AttackPattern")]
public class BossAttackPattern : ScriptableObject
{
    public string PatternName;
    public float Cooldown;
    public float Damage;
    public AnimationClip AttackAnimation;
    public GameObject ProjectilePrefab;
    public BossPhase RequiredPhase;
}
```

---

## 9. Sea & Environment System

### 9.1 Ocean Shader
- Use Unity's URP ShaderGraph to create stylized ocean.
- Vertex displacement for waves.
- Foam on shore contact using depth texture.
- Subsurface scattering for underwater light.

### 9.2 Weather System
```csharp
public class WeatherSystem : MonoBehaviour
{
    public WeatherState CurrentWeather { get; private set; }

    [SerializeField] private WindZone _windZone;
    [SerializeField] private ParticleSystem _rainParticles;
    [SerializeField] private Volume _postProcessVolume;

    public void SetWeather(WeatherState state)
    {
        CurrentWeather = state;
        switch (state)
        {
            case WeatherState.Calm: ApplyCalmWeather(); break;
            case WeatherState.Stormy: ApplyStormyWeather(); break;
            case WeatherState.Foggy: ApplyFoggyWeather(); break;
        }
    }
}
```

### 9.3 Day/Night Cycle
- 24-minute real-time cycle (1 in-game day = 24 minutes)
- Directional light rotation simulates sun/moon.
- Enemies have different patrol behaviors at night.
- Some puzzles only activate at specific times.

### 9.4 Fog of War (Ocean Map)
- Ocean map starts fully fogged.
- Player discovery radius clears fog dynamically (RenderTexture-based).
- Discovered islands are marked permanently.

---

## 10. Save & Load System

### 10.1 Save Data Structure
```csharp
[Serializable]
public class GameSaveData
{
    public string SaveSlotName;
    public DateTime SaveTime;

    // Player
    public int PlayerHealth;
    public Vector3 PlayerPosition;
    public List<string> UnlockedAbilities;

    // Boat
    public float BoatDurability;
    public Vector3 BoatPosition;
    public List<string> BoatUpgrades;

    // World
    public List<string> DiscoveredIslands;
    public List<string> DefeatedBosses;
    public List<string> CollectedCrystals;
    public List<PuzzleSaveData> PuzzleStates;

    // Inventory
    public List<string> InventoryItemIDs;
}
```

### 10.2 Save Manager
```csharp
public class SaveManager : MonoBehaviour
{
    private const string SAVE_PATH = "/saves/";

    public void SaveGame(int slot)
    {
        GameSaveData data = CollectSaveData();
        string json = JsonUtility.ToJson(data, true);
        File.WriteAllText(Application.persistentDataPath + SAVE_PATH + $"slot{slot}.json", json);
    }

    public GameSaveData LoadGame(int slot)
    {
        string path = Application.persistentDataPath + SAVE_PATH + $"slot{slot}.json";
        if (!File.Exists(path)) return null;
        return JsonUtility.FromJson<GameSaveData>(File.ReadAllText(path));
    }

    // Auto-save on island completion and boss defeat
}
```

---

## 11. UI System

### 11.1 UI Screens
| Screen | Description |
|--------|-------------|
| `HUD` | Health, stamina, boat durability, active ability |
| `InventoryUI` | Item grid, item inspection |
| `MapUI` | Parchment-style ocean map |
| `PauseMenu` | Resume, settings, save, quit |
| `BossHealthBar` | Boss name + health bar (activates in boss fight) |
| `PuzzleUI` | Puzzle-specific overlay |
| `DialogueUI` | NPC/environmental text (TMPro animated) |
| `MainMenu` | New Game, Continue, Settings, Quit |

### 11.2 HUD Implementation
- Health: Custom heart/ring widget using Unity UI Image fill.
- Stamina: Simple fill bar, fades when full.
- Boat Durability: Only visible while sailing; shows on damage.
- Ability Icon: Shows cooldown using radial fill shader.

---

## 12. Audio System

### 12.1 FMOD Integration
```csharp
public class AudioManager : MonoBehaviour
{
    public static AudioManager Instance;

    public void PlaySFX(string eventPath)
        => FMODUnity.RuntimeManager.PlayOneShot(eventPath);

    public void PlayMusic(string eventPath)
    {
        // Start new music bank with crossfade
    }

    public void SetMusicParameter(string param, float value)
    {
        // Set FMOD parameter (e.g., "intensity" for dynamic music)
    }
}
```

### 12.2 Adaptive Music
- Ocean music transitions smoothly based on weather state.
- Boss fight music uses layered stems that add intensity per phase.
- FMOD parameters: `BossPhase`, `WeatherIntensity`, `PlayerHealth`.

---

## 13. Performance Guidelines

| Budget | PC | Mobile |
|--------|----|----|
| **Draw Calls** | < 300 | < 150 |
| **Triangles** | < 500k | < 200k |
| **Textures (VRAM)** | < 512 MB | < 256 MB |
| **Frame Time** | < 16.6ms (60fps) | < 33ms (30fps) |
| **Batching** | GPU Instancing, Static Batching | SRP Batcher |

### Optimization Techniques
- LOD (Level of Detail) groups for environment meshes.
- Occlusion Culling enabled for all island scenes.
- Object Pooling for enemies, projectiles, and particles.
- Addressables for async asset loading; unload unused assets.
- Texture atlasing for island-specific assets.

---

## 14. Folder Structure

```
Assets/
├── _Game/
│   ├── Scripts/
│   │   ├── Core/           (GameManager, EventSystem, ServiceLocator)
│   │   ├── Player/         (PlayerController, Stats, Inventory, Abilities)
│   │   ├── Boat/           (BoatController, BoatStats, OceanBuoyancy)
│   │   ├── Enemies/        (EnemyBase, StateMachine, SeaCreatures)
│   │   ├── Bosses/         (BossBase, individual boss scripts)
│   │   ├── Puzzles/        (PuzzleBase, puzzle type scripts)
│   │   ├── World/          (WeatherSystem, DayNight, FogOfWar)
│   │   ├── UI/             (HUD, PauseMenu, MapUI, BossHealthBar)
│   │   ├── Audio/          (AudioManager, FMOD wrappers)
│   │   └── Save/           (SaveManager, SaveData)
│   ├── ScriptableObjects/
│   │   ├── Enemies/
│   │   ├── Bosses/
│   │   ├── Items/
│   │   ├── Islands/
│   │   └── Puzzles/
│   ├── Prefabs/
│   │   ├── Player/
│   │   ├── Boat/
│   │   ├── Enemies/
│   │   ├── Bosses/
│   │   ├── Puzzles/
│   │   └── VFX/
│   ├── Scenes/
│   ├── Art/
│   │   ├── Models/
│   │   ├── Textures/
│   │   ├── Materials/
│   │   ├── Animations/
│   │   └── VFX/
│   ├── Audio/
│   │   ├── Music/
│   │   └── SFX/
│   └── UI/
│       ├── Sprites/
│       └── Fonts/
└── ThirdParty/
    ├── DOTween/
    ├── FMOD/
    └── OdinInspector/
```

---

*Document Version: 1.0 | Last Updated: March 2026*
