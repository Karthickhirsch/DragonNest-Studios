# Unity Architecture Document
## Isle of Trials — Unity Systems, Patterns & Code Structure

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Design Patterns Used](#design-patterns-used)
3. [ScriptableObject Architecture](#scriptableobject-architecture)
4. [Scene Management Architecture](#scene-management-architecture)
5. [State Machine Implementation](#state-machine-implementation)
6. [Object Pooling System](#object-pooling-system)
7. [Input System Architecture](#input-system-architecture)
8. [Camera System](#camera-system)
9. [VFX Architecture](#vfx-architecture)
10. [Dialogue & Cutscene System](#dialogue--cutscene-system)
11. [Testing Strategy](#testing-strategy)
12. [Code Standards & Conventions](#code-standards--conventions)

---

## 1. Architecture Overview

### High-Level System Map

```
┌─────────────────────────────────────────────────────────┐
│                    Bootstrap Scene                       │
│  GameManager | SaveManager | AudioManager | EventBus     │
└────────────────────────┬────────────────────────────────┘
                         │ Persistent across scenes
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
   ┌──────────┐   ┌─────────────┐  ┌──────────┐
   │MainMenu  │   │ Ocean_World │  │ Island_XX│
   │  Scene   │   │   Scene     │  │  Scene   │
   └──────────┘   └──────┬──────┘  └────┬─────┘
                         │              │
                   ┌─────┘         ┌────┘
                   ↓               ↓
              BoatSystem      PlayerSystem
              WeatherSystem   EnemySystem
              SeaCreatures    PuzzleSystem
              MapSystem       BossFight
```

### Key Architecture Decisions
1. **Event-Driven** — Systems communicate via events, not direct references.
2. **ScriptableObject-Driven Data** — All game data in SOs; no magic numbers in code.
3. **Additive Scene Loading** — Ocean world persists; islands load/unload additively.
4. **Object Pooling** — All spawned objects (enemies, projectiles, VFX) use pools.
5. **State Machine** — Player, enemies, and bosses use explicit state machines.

---

## 2. Design Patterns Used

### 2.1 Singleton (Restricted Use)
Only used for truly global systems that must exist once:
```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
}
```
Singletons: `GameManager`, `SaveManager`, `AudioManager`, `InputManager`

### 2.2 Observer / Event Bus
Systems publish events; others subscribe without direct coupling:
```csharp
public static class GameEvents
{
    public static event Action<int> OnPlayerHealthChanged;
    public static event Action<string> OnIslandEntered;
    public static event Action<BossData> OnBossDefeated;
    public static event Action<PuzzleData> OnPuzzleSolved;

    public static void PlayerHealthChanged(int newHealth) 
        => OnPlayerHealthChanged?.Invoke(newHealth);
}

// Subscriber example (HUD)
void OnEnable() => GameEvents.OnPlayerHealthChanged += UpdateHealthUI;
void OnDisable() => GameEvents.OnPlayerHealthChanged -= UpdateHealthUI;
```

### 2.3 State Machine
Used for Player, Enemies, and Bosses:
```csharp
public interface IState
{
    void Enter();
    void Execute();
    void Exit();
}

public class StateMachine
{
    private IState _currentState;

    public void Initialize(IState startState) { _currentState = startState; _currentState.Enter(); }

    public void ChangeState(IState newState)
    {
        _currentState?.Exit();
        _currentState = newState;
        _currentState.Enter();
    }

    public void Update() => _currentState?.Execute();
}
```

### 2.4 Command Pattern (for Undo in Puzzles)
Push-block puzzles support undo:
```csharp
public interface ICommand { void Execute(); void Undo(); }

public class PushBlockCommand : ICommand
{
    private PushableBlock _block;
    private Vector3 _direction;
    private Vector3 _previousPosition;

    public void Execute() { _previousPosition = _block.transform.position; _block.MoveTo(_previousPosition + _direction); }
    public void Undo() { _block.MoveTo(_previousPosition); }
}

public class PuzzleCommandHistory
{
    private Stack<ICommand> _history = new();

    public void ExecuteCommand(ICommand cmd) { cmd.Execute(); _history.Push(cmd); }
    public void UndoLast() { if (_history.Count > 0) _history.Pop().Undo(); }
}
```

### 2.5 Object Pool Pattern
```csharp
public class ObjectPool<T> where T : MonoBehaviour
{
    private Queue<T> _pool = new();
    private T _prefab;
    private Transform _parent;

    public ObjectPool(T prefab, int initialSize, Transform parent)
    {
        _prefab = prefab; _parent = parent;
        for (int i = 0; i < initialSize; i++) CreateNew(false);
    }

    public T Get()
    {
        T obj = _pool.Count > 0 ? _pool.Dequeue() : CreateNew(true);
        obj.gameObject.SetActive(true);
        return obj;
    }

    public void Return(T obj) { obj.gameObject.SetActive(false); _pool.Enqueue(obj); }

    private T CreateNew(bool active)
    {
        T obj = Object.Instantiate(_prefab, _parent);
        obj.gameObject.SetActive(active);
        return obj;
    }
}
```

### 2.6 ScriptableObject as Data (Strategy Pattern)
```csharp
[CreateAssetMenu(menuName = "Enemy/EnemyData")]
public class EnemyData : ScriptableObject
{
    public string EnemyName;
    public int MaxHealth;
    public float MoveSpeed;
    public float AttackDamage;
    public float DetectionRadius;
    public float AttackRadius;
    public List<BossAttackPattern> AttackPatterns;
    public GameObject PrefabReference;
    public AudioClip DeathSound;
    public GameObject DeathVFX;
}
```

---

## 3. ScriptableObject Architecture

### 3.1 SO Hierarchy
```
ScriptableObjects/
├── Game/
│   ├── IslandRegistry.asset      (list of all islands + completion state)
│   └── GameConfig.asset          (global game settings, difficulty modifiers)
├── Islands/
│   ├── Island_00_Tutorial.asset
│   ├── Island_01_Ember.asset
│   └── ... (one per island)
├── Enemies/
│   ├── DriftwoodCrab.asset
│   ├── EmberLizard.asset
│   └── ... (one per enemy type)
├── Bosses/
│   ├── DriftwoodGolem.asset
│   ├── Ignar.asset
│   └── ... (one per boss)
├── Items/
│   ├── HealthPotion.asset
│   ├── RepairKit.asset
│   └── ...
├── Puzzles/
│   ├── PuzzleConfig_LightBeam.asset
│   └── ...
└── Abilities/
    ├── FireDash.asset
    ├── IceShield.asset
    └── ...
```

### 3.2 Island Data SO
```csharp
[CreateAssetMenu(menuName = "Game/IslandData")]
public class IslandData : ScriptableObject
{
    public string IslandID;
    public string IslandName;
    public string SceneName;
    public string BossSceneName;
    public Sprite MapIcon;
    public Color ThemeColor;
    public IslandTheme Theme;
    public BossData AssociatedBoss;
    public AbilityData UnlockedAbility;
    public List<string> RequiredIslandIDs; // Prerequisite islands
}
```

---

## 4. Scene Management Architecture

### 4.1 Scene Loader
```csharp
public class SceneLoader : MonoBehaviour
{
    public static SceneLoader Instance { get; private set; }

    private List<string> _loadedScenes = new();

    public async Task LoadSceneAdditive(string sceneName, Action onLoaded = null)
    {
        if (_loadedScenes.Contains(sceneName)) return;

        ShowLoadingIndicator(true);
        AsyncOperation op = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
        while (!op.isDone) await Task.Yield();

        _loadedScenes.Add(sceneName);
        ShowLoadingIndicator(false);
        onLoaded?.Invoke();
    }

    public async Task UnloadScene(string sceneName)
    {
        if (!_loadedScenes.Contains(sceneName)) return;

        AsyncOperation op = SceneManager.UnloadSceneAsync(sceneName);
        while (!op.isDone) await Task.Yield();
        _loadedScenes.Remove(sceneName);
        Resources.UnloadUnusedAssets();
    }
}
```

### 4.2 Island Proximity Trigger
```csharp
public class IslandProximityLoader : MonoBehaviour
{
    [SerializeField] private IslandData _islandData;
    [SerializeField] private float _loadDistance = 200f;
    [SerializeField] private float _unloadDistance = 400f;

    private Transform _boat;
    private bool _isLoaded;

    void Update()
    {
        float dist = Vector3.Distance(transform.position, _boat.position);

        if (!_isLoaded && dist < _loadDistance)
        {
            _ = SceneLoader.Instance.LoadSceneAdditive(_islandData.SceneName);
            _isLoaded = true;
        }
        else if (_isLoaded && dist > _unloadDistance)
        {
            _ = SceneLoader.Instance.UnloadScene(_islandData.SceneName);
            _isLoaded = false;
        }
    }
}
```

---

## 5. State Machine Implementation

### 5.1 Player States
```csharp
// States
public class PlayerIdleState : IState
{
    private PlayerController _player;
    public PlayerIdleState(PlayerController player) => _player = player;

    public void Enter() => _player.Animator.SetBool("IsMoving", false);
    public void Execute()
    {
        if (_player.InputHandler.MoveInput.magnitude > 0.1f)
            _player.StateMachine.ChangeState(_player.MoveState);
        if (_player.InputHandler.AttackPressed)
            _player.StateMachine.ChangeState(_player.AttackState);
    }
    public void Exit() { }
}

public class PlayerAttackState : IState
{
    private PlayerController _player;
    private float _attackDuration = 0.4f;
    private float _timer;

    public void Enter() { _timer = _attackDuration; _player.Animator.SetTrigger("Attack"); _player.DealDamage(); }
    public void Execute() { _timer -= Time.deltaTime; if (_timer <= 0) _player.StateMachine.ChangeState(_player.IdleState); }
    public void Exit() { }
}
```

### 5.2 Enemy States
```
EnemyIdleState    → Patrols waypoints
EnemyAlertState   → Moves toward player, plays alert animation
EnemyAttackState  → Executes attack coroutine
EnemyStunState    → Plays stun animation, pauses AI
EnemyDeadState    → Death animation, disable collider, notify pool
```

---

## 6. Object Pooling System

### 6.1 PoolManager
```csharp
public class PoolManager : MonoBehaviour
{
    public static PoolManager Instance;

    [System.Serializable]
    public class PoolEntry
    {
        public string Key;
        public GameObject Prefab;
        public int InitialSize;
    }

    [SerializeField] private List<PoolEntry> _poolEntries;
    private Dictionary<string, Queue<GameObject>> _pools = new();

    void Awake()
    {
        Instance = this;
        foreach (var entry in _poolEntries)
        {
            _pools[entry.Key] = new Queue<GameObject>();
            for (int i = 0; i < entry.InitialSize; i++)
            {
                var obj = Instantiate(entry.Prefab, transform);
                obj.SetActive(false);
                _pools[entry.Key].Enqueue(obj);
            }
        }
    }

    public GameObject Get(string key, Vector3 position, Quaternion rotation)
    {
        if (!_pools.ContainsKey(key) || _pools[key].Count == 0)
            return Instantiate(_poolEntries.Find(e => e.Key == key).Prefab, position, rotation);

        var obj = _pools[key].Dequeue();
        obj.transform.SetPositionAndRotation(position, rotation);
        obj.SetActive(true);
        return obj;
    }

    public void Return(string key, GameObject obj)
    {
        obj.SetActive(false);
        _pools[key].Enqueue(obj);
    }
}
```

### Pool Keys (Registered Prefabs)
```
"Projectile_Harpoon"
"Projectile_LavaBall"
"Projectile_IceShard"
"Enemy_EmberLizard"
"Enemy_SandScarab"
"VFX_FireBurst"
"VFX_IceShatter"
"VFX_PuzzleSolve"
"VFX_BossHit"
```

---

## 7. Input System Architecture

### 7.1 Input Actions Asset
```
PlayerInputActions.inputactions
  └── ActionMaps:
      ├── Player (on island)
      │   ├── Move (Vector2, Composite WASD)
      │   ├── Attack (Button, LeftMouse / A)
      │   ├── Dodge (Button, Shift / B)
      │   ├── Interact (Button, E / X)
      │   ├── Ability (Button, RightMouse / Y)
      │   └── Sprint (Button, Ctrl)
      ├── Boat (sailing)
      │   ├── Steer (Vector2, Composite WASD)
      │   ├── Boost (Button, Shift / RT)
      │   ├── Anchor (Button, Space / LT)
      │   ├── Harpoon (Button, LMB / RB)
      │   └── Lantern (Button, L / LB)
      └── UI
          ├── Navigate (Vector2)
          ├── Submit (Button)
          └── Cancel (Button)
```

### 7.2 Input Handler
```csharp
public class InputHandler : MonoBehaviour
{
    private PlayerInputActions _actions;

    public Vector2 MoveInput { get; private set; }
    public bool AttackPressed { get; private set; }
    public bool DodgePressed { get; private set; }
    public bool InteractPressed { get; private set; }

    void Awake()
    {
        _actions = new PlayerInputActions();
        _actions.Player.Move.performed += ctx => MoveInput = ctx.ReadValue<Vector2>();
        _actions.Player.Move.canceled += ctx => MoveInput = Vector2.zero;
        _actions.Player.Attack.performed += ctx => AttackPressed = true;
        _actions.Player.Dodge.performed += ctx => DodgePressed = true;
    }

    void LateUpdate()
    {
        // Reset single-frame inputs
        AttackPressed = false;
        DodgePressed = false;
        InteractPressed = false;
    }

    void OnEnable() => _actions.Enable();
    void OnDisable() => _actions.Disable();
}
```

---

## 8. Camera System

### 8.1 Cinemachine Setup
```
CinemachineBrain (on Main Camera)
│
├── VCam_Sailing          — Top-down sailing view, follows boat
│   ├── FOV: 60
│   ├── Follow: Boat Transform
│   └── Offset: (0, 25, -10)
│
├── VCam_Island           — 3/4 isometric island view
│   ├── FOV: 55
│   ├── Follow: Player Transform
│   └── Offset: (0, 15, -12)
│
├── VCam_BossIntro        — Cinematic reveal of boss
│   ├── Manual keyframed path
│   └── Priority: 20 (overrides others during intro)
│
├── VCam_BossFight        — Slightly pulled back for boss arenas
│   ├── FOV: 65
│   ├── Follow: Midpoint(Player, Boss)
│   └── Dynamic Offset based on distance
│
└── VCam_Cutscene         — Story cutscene cameras (multiple per scene)
```

### 8.2 Camera Shake
```csharp
public class CameraShaker : MonoBehaviour
{
    public static CameraShaker Instance;
    private CinemachineVirtualCamera _vCam;
    private CinemachineBasicMultiChannelPerlin _noise;

    public void Shake(float intensity, float duration)
        => StartCoroutine(ShakeRoutine(intensity, duration));

    private IEnumerator ShakeRoutine(float intensity, float duration)
    {
        _noise.m_AmplitudeGain = intensity;
        _noise.m_FrequencyGain = intensity * 2;
        yield return new WaitForSeconds(duration);
        _noise.m_AmplitudeGain = 0;
        _noise.m_FrequencyGain = 0;
    }
}
```

---

## 9. VFX Architecture

### 9.1 VFX Manager
```csharp
public class VFXManager : MonoBehaviour
{
    public static VFXManager Instance;

    [System.Serializable]
    public class VFXEntry { public string Key; public GameObject Prefab; }
    [SerializeField] private List<VFXEntry> _vfxEntries;

    public void PlayVFX(string key, Vector3 position, float duration = 2f)
    {
        var obj = PoolManager.Instance.Get(key, position, Quaternion.identity);
        StartCoroutine(ReturnAfterDelay(key, obj, duration));
    }

    private IEnumerator ReturnAfterDelay(string key, GameObject obj, float delay)
    {
        yield return new WaitForSeconds(delay);
        PoolManager.Instance.Return(key, obj);
    }
}
```

### 9.2 VFX Keys
```
"VFX_FireBurst"        — On fire impact or Fire Dash
"VFX_IceShatter"       — On ice break
"VFX_VineGrow"         — On vine grapple use
"VFX_SandPuff"         — On Sand Veil activation
"VFX_LightningStrike"  — On Lightning Strike ability
"VFX_PuzzleSolve"      — On puzzle completion (star burst, gold particles)
"VFX_BossPhaseChange"  — On boss phase transition (large shockwave)
"VFX_CrystalCollect"   — On Tide Crystal collection
"VFX_PlayerDeath"      — Player dies
"VFX_EnemyDeath"       — Enemy dies
"VFX_HarpoonImpact"    — Harpoon hits target
```

---

## 10. Dialogue & Cutscene System

### 10.1 Dialogue System
```csharp
[System.Serializable]
public class DialogueLine
{
    public string SpeakerName;
    public string Text;
    public AudioClip VoiceClip;     // Optional
    public Sprite SpeakerPortrait;  // Optional
}

[CreateAssetMenu(menuName = "Dialogue/DialogueSequence")]
public class DialogueSequence : ScriptableObject
{
    public List<DialogueLine> Lines;
    public bool PauseGameDuringDialogue;
}

public class DialogueManager : MonoBehaviour
{
    public static DialogueManager Instance;
    [SerializeField] private DialogueUI _ui;

    public void StartDialogue(DialogueSequence sequence)
    {
        if (sequence.PauseGameDuringDialogue) Time.timeScale = 0;
        StartCoroutine(PlaySequence(sequence));
    }

    private IEnumerator PlaySequence(DialogueSequence sequence)
    {
        foreach (var line in sequence.Lines)
        {
            _ui.ShowLine(line);
            yield return new WaitUntil(() => Input.GetKeyDown(KeyCode.E));
        }
        _ui.Hide();
        if (Time.timeScale == 0) Time.timeScale = 1;
    }
}
```

### 10.2 Cutscene System (Unity Timeline)
```
Each cutscene is a Timeline asset:
CutsceneTimeline.playableAsset
  ├── Cinemachine Track  — Camera cuts + animation
  ├── Animation Track    — Character animations
  ├── Audio Track        — Music + SFX timed cues
  ├── Activation Track   — Enable/disable GameObjects
  └── Signal Track       — Fire GameEvents at specific times
```

```csharp
public class CutsceneManager : MonoBehaviour
{
    [SerializeField] private PlayableDirector _director;

    public void PlayCutscene(TimelineAsset timeline, Action onComplete = null)
    {
        GameEvents.CutsceneStarted();
        _director.playableAsset = timeline;
        _director.Play();
        _director.stopped += _ => { GameEvents.CutsceneEnded(); onComplete?.Invoke(); };
    }
}
```

---

## 11. Testing Strategy

### 11.1 Unit Tests (Unity Test Runner)
```
Tests/
├── SaveManagerTests.cs       — Serialize/deserialize save data
├── PuzzleSystemTests.cs      — Puzzle state logic
├── InventoryTests.cs         — Add/remove/stack items
├── StatMachineTests.cs       — State transition logic
└── PoolManagerTests.cs       — Pool get/return behavior
```

### 11.2 Integration Tests
- Scene loading/unloading without memory leaks.
- Boss phase transitions trigger correct events.
- Save/load restores exact game state.

### 11.3 Playtest Checklist (Per Island)
```
[ ] Player can complete island from start to crystal collect
[ ] All puzzles solvable and resettable
[ ] Boss fight completable on all 3 difficulty settings
[ ] No out-of-bounds escape routes
[ ] All checkpoints function correctly
[ ] No blocking bugs (game cannot progress)
[ ] Frame rate stays within budget throughout island
[ ] Auto-save triggers on island complete
```

---

## 12. Code Standards & Conventions

### Naming Conventions
| Element | Convention | Example |
|---------|-----------|---------|
| Classes | PascalCase | `PlayerController` |
| Methods | PascalCase | `TakeDamage()` |
| Private fields | _camelCase | `_currentHealth` |
| Public properties | PascalCase | `CurrentHealth` |
| Constants | UPPER_SNAKE | `MAX_HEALTH` |
| Interfaces | IPascalCase | `IInteractable` |
| Enums | PascalCase | `GameState.Playing` |
| Events | OnPascalCase | `OnPlayerDied` |

### Script Template
```csharp
using UnityEngine;

namespace IsleTrial.Systems
{
    /// <summary>
    /// Brief description of what this script does.
    /// </summary>
    public class MyClass : MonoBehaviour
    {
        // ── Serialized Fields ─────────────────────────────
        [Header("Config")]
        [SerializeField] private MyData _data;

        // ── Private Fields ────────────────────────────────
        private StateMachine _stateMachine;

        // ── Public Properties ─────────────────────────────
        public int CurrentValue { get; private set; }

        // ── Unity Lifecycle ───────────────────────────────
        private void Awake() { }
        private void Start() { }
        private void Update() { }
        private void OnDestroy() { }

        // ── Public Methods ────────────────────────────────
        public void Initialize() { }

        // ── Private Methods ───────────────────────────────
        private void DoSomething() { }
    }
}
```

### Best Practices
- No `FindObjectOfType` in Update loops — cache references in Awake/Start.
- No magic numbers — use named constants or ScriptableObject values.
- Always unsubscribe from events in `OnDisable`/`OnDestroy`.
- Use `TryGetComponent` instead of `GetComponent` for optional components.
- Coroutines for time-based effects; `async/await` for scene loading.
- Profile before optimizing — use Unity Profiler to identify real bottlenecks.

---

*Document Version: 1.0 | Last Updated: March 2026*
