# Unity Coding Documentation
### A Complete Beginner-Friendly Reference

---

## Table of Contents

1. [What is a Unity Script?](#1-what-is-a-unity-script)
2. [MonoBehaviour — The Heart of Unity Scripts](#2-monobehaviour--the-heart-of-unity-scripts)
3. [Unity Lifecycle Methods (Execution Order)](#3-unity-lifecycle-methods-execution-order)
4. [Variables and SerializeField](#4-variables-and-serializefield)
5. [GetComponent — Talking to Other Components](#5-getcomponent--talking-to-other-components)
6. [Input System](#6-input-system)
7. [Transform — Moving, Rotating, Scaling](#7-transform--moving-rotating-scaling)
8. [Rigidbody — Physics Movement](#8-rigidbody--physics-movement)
9. [Vector3 — Positions and Directions](#9-vector3--positions-and-directions)
10. [Time — Frame Rate Independence](#10-time--frame-rate-independence)
11. [Instantiate and Destroy](#11-instantiate-and-destroy)
12. [Coroutines — Waiting Over Time](#12-coroutines--waiting-over-time)
13. [Collision and Trigger Events](#13-collision-and-trigger-events)
14. [Debug — Logging and Testing](#14-debug--logging-and-testing)
15. [RequireComponent and Attributes](#15-requirecomponent-and-attributes)
16. [Properties and Access Modifiers](#16-properties-and-access-modifiers)
17. [FindObjectOfType — Finding Scripts in the Scene](#17-findobjectoftype--finding-scripts-in-the-scene)
18. [Mathf — Math Helpers](#18-mathf--math-helpers)
19. [Common Patterns and Best Practices](#19-common-patterns-and-best-practices)

---

## 1. What is a Unity Script?

A Unity script is a **C# file** you attach to a GameObject in the scene. It gives that object behavior — like moving, reacting to input, playing sounds, or dealing damage.

Think of a GameObject as a blank toy. The script is the **instruction manual** that tells the toy what to do and when to do it.

```csharp
using UnityEngine;

public class MyFirstScript : MonoBehaviour
{
    void Start()
    {
        Debug.Log("Hello, Unity!");
    }
}
```

- `using UnityEngine;` — Imports all Unity tools so you can use things like `Vector3`, `Rigidbody`, `Debug`, etc.
- `public class MyFirstScript` — Names your script. This name **must match the filename** exactly.
- `: MonoBehaviour` — Makes this a Unity script that can be attached to a GameObject.

---

## 2. MonoBehaviour — The Heart of Unity Scripts

`MonoBehaviour` is the **base class** every Unity script inherits from. When you inherit from it, your script gains access to all Unity lifecycle methods (Awake, Start, Update, etc.) and can be dragged onto GameObjects in the Inspector.

```csharp
public class PlayerController : MonoBehaviour
{
    // Your code lives here
}
```

**Why inherit from MonoBehaviour?**
Without it, Unity has no idea your script exists. It cannot call `Update()`, cannot show it in the Inspector, and cannot attach it to a GameObject. It would just be a plain C# class — useful for data, but invisible to Unity.

---

## 3. Unity Lifecycle Methods (Execution Order)

These are **special methods Unity calls automatically** at different points in the game. You never call them yourself — Unity does.

```
Game Starts
    │
    ▼
Awake()         ← Called first, even before the object is fully active
    │
    ▼
OnEnable()      ← Called when the object becomes active/enabled
    │
    ▼
Start()         ← Called once before the first frame
    │
    ▼
── Every Frame ──────────────────────────────
    │
    ├── FixedUpdate()   ← Physics tick (fixed interval, ~50x/sec)
    ├── Update()        ← Every frame (variable, ~60x/sec)
    └── LateUpdate()    ← After all Updates are done
── End Frame ────────────────────────────────
    │
    ▼
OnDisable()     ← Called when the object is disabled
    │
    ▼
OnDestroy()     ← Called just before the object is deleted
```

### `Awake()`

```csharp
void Awake()
{
    _rb = GetComponent<Rigidbody>();
}
```

- Runs **once**, when the object first loads into the scene.
- Runs even if the object is **disabled**.
- Best place to **get component references** and set up internal state.
- Runs **before** `Start()`.

**When to use:** Any setup that other scripts might need before the game begins. If Script B's `Start()` depends on Script A being ready, Script A should set itself up in `Awake()`.

---

### `Start()`

```csharp
void Start()
{
    _health = _maxHealth;
    Debug.Log("Player is ready!");
}
```

- Runs **once**, just before the **first frame** the object is active.
- Runs **after** all `Awake()` calls are done.
- Best place to **initialize gameplay values** (starting health, starting position, etc.).

**When to use:** Any setup that depends on other scripts being ready first, since all `Awake()` calls have already finished.

---

### `Update()`

```csharp
void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
    {
        Jump();
    }
}
```

- Runs **every frame**.
- Frame rate is NOT fixed — it runs faster on a powerful PC (120 fps) and slower on a weak one (30 fps).
- Best for **reading input**, **updating UI**, and **non-physics logic**.

**When NOT to use:** Never apply physics forces here. The inconsistent frame rate will make movement jittery on different machines.

---

### `FixedUpdate()`

```csharp
void FixedUpdate()
{
    _rb.AddForce(Vector3.forward * _speed);
}
```

- Runs at a **fixed interval** (default: 50 times per second, every 0.02 seconds).
- Completely independent of frame rate.
- **Only place** where you should apply Rigidbody forces or physics calculations.

**Why fixed?** Physics engines need consistent time steps to calculate collisions and forces correctly. Variable timing would cause objects to phase through walls or behave differently on each machine.

---

### `LateUpdate()`

```csharp
void LateUpdate()
{
    // Move camera to follow player AFTER player has moved
    _camera.transform.position = _player.transform.position + _offset;
}
```

- Runs **after all `Update()` calls** for the current frame are done.
- Best for **cameras** and anything that must react to what happened during `Update()`.

**Why it exists:** If your camera followed the player in `Update()`, it might move before the player does (depending on script execution order), causing a one-frame lag. `LateUpdate()` guarantees the player has already moved.

---

### `OnEnable()` and `OnDisable()`

```csharp
void OnEnable()
{
    // Subscribe to an event when this object turns on
    GameEvents.OnPlayerDied += HandlePlayerDied;
}

void OnDisable()
{
    // Always unsubscribe when turning off to prevent memory leaks
    GameEvents.OnPlayerDied -= HandlePlayerDied;
}
```

- `OnEnable` fires whenever `gameObject.SetActive(true)` is called.
- `OnDisable` fires whenever `gameObject.SetActive(false)` is called.
- Critical for **subscribing/unsubscribing from events** correctly.

---

### `OnDestroy()`

```csharp
void OnDestroy()
{
    Debug.Log("This object was destroyed.");
    // Final cleanup goes here
}
```

- Runs once just before `Destroy(gameObject)` finishes.
- Use for final cleanup: cancelling coroutines, unsubscribing events, saving data.

---

## 4. Variables and SerializeField

Variables store data that your script uses. Unity has a special way of making private variables visible in the Inspector.

### Access Modifiers

```csharp
public float speed = 5f;       // Visible in Inspector AND accessible by other scripts
private float _health = 100f;  // Hidden from Inspector AND hidden from other scripts
[SerializeField] private float _jumpForce = 10f; // Visible in Inspector, hidden from other scripts
```

**Best practice:** Always use `private` with `[SerializeField]`. This keeps your variable protected from other scripts accidentally changing it, while still letting designers tweak it in the Inspector.

### Why `[SerializeField]`?

The Unity Inspector only shows `public` variables by default. `[SerializeField]` is a special **attribute** that tells Unity: *"Show this private variable in the Inspector anyway."*

```csharp
[Header("Movement Settings")]          // Creates a bold label in the Inspector
[SerializeField] private float _speed = 5f;
[SerializeField] private float _jumpHeight = 2f;

[Space(10)]                            // Adds visual spacing in the Inspector
[Header("Health Settings")]
[SerializeField] private int _maxHealth = 100;
[Tooltip("How long the invincibility lasts after taking damage")]
[SerializeField] private float _invincibilityDuration = 1.5f;
```

### Common Variable Types

| Type | What It Stores | Example |
|------|---------------|---------|
| `int` | Whole numbers | `int score = 0;` |
| `float` | Decimal numbers | `float speed = 5.5f;` |
| `bool` | True or false | `bool isAlive = true;` |
| `string` | Text | `string playerName = "Hero";` |
| `Vector3` | 3D position/direction | `Vector3 spawnPoint;` |
| `GameObject` | Any scene object | `GameObject enemy;` |
| `Transform` | Position + Rotation + Scale | `Transform target;` |
| `Rigidbody` | Physics component | `Rigidbody rb;` |

---

## 5. GetComponent — Talking to Other Components

`GetComponent<T>()` finds a component of type `T` on the **same GameObject**. It is how scripts communicate with other components.

```csharp
private Rigidbody _rb;
private Animator _animator;
private AudioSource _audio;

void Awake()
{
    _rb = GetComponent<Rigidbody>();
    _animator = GetComponent<Animator>();
    _audio = GetComponent<AudioSource>();
}
```

**Why store the result?** `GetComponent` searches through all components on the object every time it is called. If you call it inside `Update()`, it searches 60 times per second — very wasteful. Store the result in `Awake()` and reuse it.

### Variants

```csharp
// Get a component on THIS GameObject
Rigidbody rb = GetComponent<Rigidbody>();

// Get a component on a CHILD GameObject
Rigidbody childRb = GetComponentInChildren<Rigidbody>();

// Get a component on the PARENT GameObject
Rigidbody parentRb = GetComponentInParent<Rigidbody>();

// Safe version — returns true/false, doesn't throw an error if missing
if (TryGetComponent<Rigidbody>(out Rigidbody rb))
{
    rb.AddForce(Vector3.up * 10f);
}
```

**Always prefer `TryGetComponent`** when the component might not exist. It is safer than `GetComponent` because it will not throw a NullReferenceException if the component is missing.

---

## 6. Input System

Unity provides two ways to read input: the **Legacy Input System** and the newer **Input System package**.

### Legacy Input System (Built-in)

```csharp
void Update()
{
    // Keyboard keys
    if (Input.GetKeyDown(KeyCode.Space))   // Pressed THIS frame
        Jump();

    if (Input.GetKey(KeyCode.W))           // Held down
        MoveForward();

    if (Input.GetKeyUp(KeyCode.Space))     // Released THIS frame
        StopJumping();

    // Mouse
    if (Input.GetMouseButtonDown(0))       // Left click (0=left, 1=right, 2=middle)
        Shoot();

    float mouseX = Input.GetAxis("Mouse X");  // Mouse movement delta
    float mouseY = Input.GetAxis("Mouse Y");

    // Axes (mapped in Edit > Project Settings > Input Manager)
    float horizontal = Input.GetAxis("Horizontal");  // A/D or Left/Right arrow (-1 to 1)
    float vertical = Input.GetAxis("Vertical");      // W/S or Up/Down arrow (-1 to 1)
}
```

### GetKeyDown vs GetKey vs GetKeyUp

| Method | When It Returns True |
|--------|---------------------|
| `GetKeyDown` | Only on the **exact frame** the key is first pressed |
| `GetKey` | Every frame the key is **held down** |
| `GetKeyUp` | Only on the **exact frame** the key is released |

---

## 7. Transform — Moving, Rotating, Scaling

Every GameObject has a `Transform` component. It stores position, rotation, and scale. You access it through `transform` (lowercase) in any MonoBehaviour.

### Position

```csharp
// Read position
Vector3 pos = transform.position;           // World position
Vector3 localPos = transform.localPosition; // Position relative to parent

// Set position directly (teleport)
transform.position = new Vector3(0f, 5f, 0f);

// Move smoothly over time
transform.position += transform.forward * _speed * Time.deltaTime;

// Move using Translate (relative to current rotation)
transform.Translate(Vector3.forward * _speed * Time.deltaTime);
```

### Rotation

```csharp
// Read rotation (as Euler angles in degrees)
Vector3 euler = transform.eulerAngles;

// Set rotation
transform.rotation = Quaternion.Euler(0f, 90f, 0f);  // Face right

// Rotate over time
transform.Rotate(Vector3.up, 90f * Time.deltaTime);  // Spin around Y axis

// Look at a target
transform.LookAt(target.transform);

// Smoothly rotate toward a target
Vector3 direction = target.position - transform.position;
Quaternion targetRotation = Quaternion.LookRotation(direction);
transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, _rotateSpeed * Time.deltaTime);
```

### Scale

```csharp
// Double the size
transform.localScale = new Vector3(2f, 2f, 2f);

// Scale using Vector3.one (1,1,1 = normal size)
transform.localScale = Vector3.one * 1.5f;
```

### Direction Shortcuts

```csharp
transform.forward   // The direction the object is facing (blue arrow)
transform.right     // The object's right direction (red arrow)
transform.up        // The object's up direction (green arrow)

// Negatives give opposite directions
transform.forward * -1  // Behind
-transform.right        // Left
```

---

## 8. Rigidbody — Physics Movement

A `Rigidbody` component makes a GameObject part of the physics simulation. It gives the object mass, gravity, drag, and the ability to be pushed by forces.

```csharp
private Rigidbody _rb;

void Awake()
{
    _rb = GetComponent<Rigidbody>();
}
```

### AddForce — Pushing an Object

```csharp
// Push forward with a force
_rb.AddForce(transform.forward * 500f);

// ForceMode options:
_rb.AddForce(Vector3.up * 10f, ForceMode.Force);        // Continuous force (uses mass)
_rb.AddForce(Vector3.up * 10f, ForceMode.Acceleration); // Continuous force (ignores mass)
_rb.AddForce(Vector3.up * 10f, ForceMode.Impulse);      // Instant hit (uses mass) — good for jumps
_rb.AddForce(Vector3.up * 10f, ForceMode.VelocityChange); // Instant hit (ignores mass)
```

**ForceMode Guide:**

| ForceMode | Type | Uses Mass? | Best For |
|-----------|------|-----------|---------|
| `Force` | Continuous | Yes | Engines, wind |
| `Acceleration` | Continuous | No | Uniform movement |
| `Impulse` | Instant | Yes | Realistic hit/jump |
| `VelocityChange` | Instant | No | Snappy jump, uniform hit |

### Velocity — Direct Speed Control

```csharp
// Read current speed
float currentSpeed = _rb.velocity.magnitude;  // Total speed
Vector3 currentVelocity = _rb.velocity;        // Speed + direction

// Set velocity directly (bypasses forces)
_rb.velocity = transform.forward * 10f;        // Move forward at speed 10

// Clamp speed so it never exceeds a maximum
if (_rb.velocity.magnitude > _maxSpeed)
    _rb.velocity = _rb.velocity.normalized * _maxSpeed;

// Stop the object instantly
_rb.velocity = Vector3.zero;
_rb.angularVelocity = Vector3.zero;  // Also stop rotation
```

### Rigidbody Constraints

```csharp
// Freeze position on certain axes (useful for 2D games or top-down)
_rb.constraints = RigidbodyConstraints.FreezePositionY;  // Can't move up/down
_rb.constraints = RigidbodyConstraints.FreezeRotation;   // Can't rotate at all

// Freeze multiple axes
_rb.constraints = RigidbodyConstraints.FreezePositionY 
                | RigidbodyConstraints.FreezeRotationX 
                | RigidbodyConstraints.FreezeRotationZ;
```

---

## 9. Vector3 — Positions and Directions

`Vector3` stores three float values: X, Y, Z. It represents both **positions in space** and **directions**.

### Creating Vectors

```csharp
Vector3 position = new Vector3(1f, 2f, 3f);   // X=1, Y=2, Z=3
Vector3 up = Vector3.up;                        // (0, 1, 0)
Vector3 forward = Vector3.forward;              // (0, 0, 1)
Vector3 zero = Vector3.zero;                    // (0, 0, 0)
Vector3 one = Vector3.one;                      // (1, 1, 1)
```

### Shortcuts

| Shorthand | Value | Meaning |
|-----------|-------|---------|
| `Vector3.zero` | (0, 0, 0) | Origin / stopped |
| `Vector3.one` | (1, 1, 1) | Full scale |
| `Vector3.up` | (0, 1, 0) | World up |
| `Vector3.down` | (0, -1, 0) | World down |
| `Vector3.forward` | (0, 0, 1) | World forward |
| `Vector3.back` | (0, 0, -1) | World backward |
| `Vector3.right` | (1, 0, 0) | World right |
| `Vector3.left` | (-1, 0, 0) | World left |

### Vector Math

```csharp
Vector3 a = new Vector3(1, 0, 0);
Vector3 b = new Vector3(0, 0, 1);

// Distance between two points
float dist = Vector3.Distance(a, b);

// Direction from A to B (unit vector)
Vector3 direction = (b - a).normalized;

// Length of a vector
float length = a.magnitude;

// Normalized (length of exactly 1, direction preserved)
Vector3 dir = a.normalized;

// Dot product — how aligned two directions are (-1 to 1)
float dot = Vector3.Dot(a, b);
// dot = 1   → same direction
// dot = 0   → perpendicular
// dot = -1  → opposite directions

// Cross product — find a direction perpendicular to two vectors
Vector3 perp = Vector3.Cross(a, b);

// Lerp — smoothly move between two positions
Vector3 result = Vector3.Lerp(startPos, endPos, 0.5f); // Halfway point

// Move toward a position at a fixed speed (does not overshoot)
transform.position = Vector3.MoveTowards(transform.position, target, _speed * Time.deltaTime);

// Smooth follow
transform.position = Vector3.Lerp(transform.position, target, _followSpeed * Time.deltaTime);
```

---

## 10. Time — Frame Rate Independence

`Time` is Unity's timer class. The most important values are `deltaTime` and `fixedDeltaTime`.

```csharp
Time.deltaTime        // Seconds since the last frame (varies per frame)
Time.fixedDeltaTime   // Seconds per physics tick (always the same, default 0.02s)
Time.time             // Total seconds since the game started
Time.timeScale        // Controls game speed (0 = paused, 1 = normal, 2 = double speed)
Time.unscaledDeltaTime // Delta time ignoring timeScale (useful for pause menus)
```

### Why Multiply by `Time.deltaTime`?

```csharp
// WITHOUT deltaTime — speed depends on frame rate
transform.position += Vector3.forward * 5f;
// At 60fps: moves 5 * 60 = 300 units/second
// At 30fps: moves 5 * 30 = 150 units/second (half speed on slow machines!)

// WITH deltaTime — frame rate independent
transform.position += Vector3.forward * 5f * Time.deltaTime;
// At 60fps: 5 * (1/60) * 60 = 5 units/second
// At 30fps: 5 * (1/30) * 30 = 5 units/second (same speed always!)
```

Always multiply movement, rotation, and any time-based logic by `Time.deltaTime` (in `Update`) or `Time.fixedDeltaTime` (in `FixedUpdate`).

### Pause the Game

```csharp
// Pause
Time.timeScale = 0f;

// Resume
Time.timeScale = 1f;

// For UI animations that should still run during pause
float uiDelta = Time.unscaledDeltaTime;
```

---

## 11. Instantiate and Destroy

`Instantiate` creates a copy of a GameObject (or Prefab) in the scene. `Destroy` removes it.

### Instantiate

```csharp
[SerializeField] private GameObject _bulletPrefab;
[SerializeField] private Transform _spawnPoint;

void Shoot()
{
    // Spawn at a specific position and rotation
    GameObject bullet = Instantiate(_bulletPrefab, _spawnPoint.position, _spawnPoint.rotation);

    // Spawn at world origin
    GameObject obj = Instantiate(_bulletPrefab);

    // Spawn as a child of another object
    GameObject child = Instantiate(_bulletPrefab, parentTransform);

    // Access components on the spawned object
    if (bullet.TryGetComponent<Rigidbody>(out var rb))
        rb.velocity = _spawnPoint.forward * _bulletSpeed;
}
```

### Destroy

```csharp
// Destroy immediately
Destroy(gameObject);

// Destroy after a delay (seconds)
Destroy(gameObject, 3f);

// Destroy a specific component (not the whole object)
Destroy(GetComponent<BoxCollider>());

// Destroy another object
Destroy(enemyObject);
Destroy(enemyObject, 2f);
```

**Important:** `Destroy` does not happen instantly. The object is flagged for destruction and removed at the **end of the current frame**. Code after `Destroy(gameObject)` still runs.

---

## 12. Coroutines — Waiting Over Time

A Coroutine is a function that can **pause in the middle** and resume later. This is Unity's way of doing things over time without blocking the game.

```csharp
void Start()
{
    StartCoroutine(FadeOut());         // Start the coroutine
    StartCoroutine(SpawnEnemies());
}

IEnumerator FadeOut()
{
    float alpha = 1f;
    while (alpha > 0f)
    {
        alpha -= Time.deltaTime;
        // Update the UI transparency here
        yield return null;             // Wait one frame, then continue
    }
    Debug.Log("Fade complete!");
}

IEnumerator SpawnEnemies()
{
    while (true)                       // Loop forever
    {
        SpawnOneEnemy();
        yield return new WaitForSeconds(3f);  // Wait 3 seconds before spawning again
    }
}

IEnumerator CountdownTimer(int seconds)
{
    for (int i = seconds; i > 0; i--)
    {
        Debug.Log(i);
        yield return new WaitForSeconds(1f);
    }
    Debug.Log("GO!");
}
```

### Yield Options

| Yield Statement | What It Does |
|----------------|-------------|
| `yield return null` | Wait one frame |
| `yield return new WaitForSeconds(2f)` | Wait 2 real seconds |
| `yield return new WaitForFixedUpdate()` | Wait for the next physics tick |
| `yield return new WaitUntil(() => _isReady)` | Wait until a condition is true |
| `yield return new WaitWhile(() => _isLoading)` | Wait while a condition is true |

### Stopping Coroutines

```csharp
// Store the reference when starting
Coroutine myRoutine = StartCoroutine(FadeOut());

// Stop it later
StopCoroutine(myRoutine);

// Stop ALL coroutines on this script
StopAllCoroutines();
```

---

## 13. Collision and Trigger Events

Unity calls these methods automatically when objects collide. You never call them yourself.

### Colliders (Physical Collision)

```csharp
// Called when this object physically touches another
void OnCollisionEnter(Collision collision)
{
    Debug.Log("Hit: " + collision.gameObject.name);

    // How fast was the impact?
    float impactSpeed = collision.relativeVelocity.magnitude;

    // Get the component on the object we hit
    if (collision.gameObject.TryGetComponent<Enemy>(out var enemy))
        enemy.TakeDamage(10f);
}

// Called every frame while touching
void OnCollisionStay(Collision collision) { }

// Called when contact ends
void OnCollisionExit(Collision collision) { }
```

### Triggers (Invisible Detection Zone)

A trigger is a collider with **Is Trigger** checked. Objects pass through it but it still detects them.

```csharp
void OnTriggerEnter(Collider other)
{
    if (other.CompareTag("Player"))
    {
        Debug.Log("Player entered the zone!");
        // Give item, start cutscene, open door, etc.
    }
}

void OnTriggerStay(Collider other) { }   // Every frame while inside
void OnTriggerExit(Collider other) { }   // When leaving
```

### Collision vs Trigger — When to Use Which

| Use Case | Use Collider (OnCollision) | Use Trigger (OnTrigger) |
|----------|--------------------------|------------------------|
| Player walks into a wall | ✅ | ❌ |
| Player walks into a pickup | ❌ | ✅ |
| Bullet hits an enemy | ✅ | ✅ (either works) |
| Player enters a checkpoint zone | ❌ | ✅ |
| Physics-based crash damage | ✅ | ❌ |

### Tags and Layers

```csharp
// Check the tag of the colliding object
if (collision.gameObject.CompareTag("Enemy"))     // Fast — use this
if (collision.gameObject.tag == "Enemy")          // Slow — avoid this

// Check the layer
if (collision.gameObject.layer == LayerMask.NameToLayer("Ground"))
```

---

## 14. Debug — Logging and Testing

`Debug` is your best friend during development. It writes messages to the Unity Console window.

```csharp
Debug.Log("This is a normal message.");
Debug.LogWarning("This is a warning — something might be wrong.");
Debug.LogError("This is an error — something is definitely wrong.");

// Log with a variable
int score = 100;
Debug.Log("Current score: " + score);
Debug.Log($"Current score: {score}");  // String interpolation (cleaner)

// Draw lines in the Scene view (for visualizing directions)
Debug.DrawLine(Vector3.zero, Vector3.forward * 5f, Color.red);
Debug.DrawRay(transform.position, transform.forward * 10f, Color.green);
```

**Note:** `Debug.Log` has a small performance cost. Remove or comment them out in the final build, or use `#if UNITY_EDITOR` guards.

```csharp
#if UNITY_EDITOR
    Debug.Log("This only runs in the editor, not in a build.");
#endif
```

---

## 15. RequireComponent and Attributes

Attributes are **special tags** placed above classes, methods, or variables using `[AttributeName]`. They modify how Unity treats that element.

```csharp
// Force a component to always exist on this GameObject
[RequireComponent(typeof(Rigidbody))]
[RequireComponent(typeof(AudioSource))]
public class PlayerController : MonoBehaviour { }

// Organize Inspector with headers and spacing
[Header("Movement")]
[SerializeField] private float _speed = 5f;
[Space(10)]
[Header("Combat")]
[SerializeField] private int _damage = 10;

// Show a tooltip when hovering in the Inspector
[Tooltip("Speed in units per second")]
[SerializeField] private float _speed = 5f;

// Clamp a number in the Inspector (min, max)
[Range(0f, 100f)]
[SerializeField] private float _volume = 50f;

// Hide a public variable from the Inspector
[HideInInspector]
public int internalId;

// Call a method directly from a button in the Inspector (Editor only)
[ContextMenu("Reset Health")]
void ResetHealth()
{
    _health = _maxHealth;
}
```

---

## 16. Properties and Access Modifiers

### Access Modifiers

```csharp
public int Value;       // Any script can read AND write this
private int _value;     // Only this script can read and write this
protected int _value;   // This script AND scripts that inherit from it
internal int _value;    // Any script in the same assembly (project)
```

**Best Practice:** Default to `private`. Only make something `public` if other scripts genuinely need to access it.

### Properties — Controlled Access

Properties let you expose data **in a controlled way** — read-only, write-only, or with validation logic.

```csharp
private int _health;

// Read-only property — others can read but not set it
public int Health => _health;

// Or the longer form
public int Health { get { return _health; } }

// Read + Write with validation
public int Health
{
    get { return _health; }
    set { _health = Mathf.Clamp(value, 0, _maxHealth); }  // Clamp on set
}

// Write-only (rare)
public string Password { set { _password = Hash(value); } }
```

### Usage example

```csharp
// From another script
if (player.Health <= 0)
    GameOver();

player.Health = 50;  // This will clamp automatically
```

---

## 17. FindObjectOfType — Finding Scripts in the Scene

`FindObjectOfType<T>()` searches the **entire scene** for any active object that has a component of type `T`.

```csharp
void Awake()
{
    // Find the GameManager script anywhere in the scene
    _gameManager = FindObjectOfType<GameManager>();

    // Find the player's health component
    _playerHealth = FindObjectOfType<PlayerHealth>();
}
```

**Warning:** `FindObjectOfType` is **expensive** — it scans every object in the scene. Never call it in `Update()`. Always call it in `Awake()` or `Start()` and cache the result.

### Better Alternatives

```csharp
// Singleton pattern — the most common solution
// GameManager.cs
public static GameManager Instance { get; private set; }

void Awake()
{
    if (Instance == null)
        Instance = this;
    else
        Destroy(gameObject);  // Only one can exist
}

// Any other script can now access it without searching:
GameManager.Instance.AddScore(10);
```

---

## 18. Mathf — Math Helpers

`Mathf` is Unity's math library for common operations on floats.

```csharp
// Absolute value (remove the negative sign)
float abs = Mathf.Abs(-5f);   // Returns 5

// Clamp — keep a value within a range
float clamped = Mathf.Clamp(value, 0f, 100f);  // Never below 0 or above 100
int clampedInt = Mathf.Clamp(score, 0, 999);

// Min and Max
float smaller = Mathf.Min(a, b);
float larger = Mathf.Max(a, b);

// Round, Floor, Ceil
int rounded = Mathf.RoundToInt(3.7f);  // Returns 4
int floored = Mathf.FloorToInt(3.9f);  // Returns 3 (always round down)
int ceiled  = Mathf.CeilToInt(3.1f);   // Returns 4 (always round up)

// Power and Square Root
float squared = Mathf.Pow(3f, 2f);   // 3² = 9
float sqrt = Mathf.Sqrt(16f);        // √16 = 4

// Linear Interpolation (blend between two values)
float result = Mathf.Lerp(0f, 100f, 0.5f);   // Returns 50 (halfway)
float smooth = Mathf.Lerp(current, target, Time.deltaTime * 5f);  // Smooth approach

// Trigonometry (angle in radians)
float sin = Mathf.Sin(Mathf.PI / 2f);   // Returns 1
float cos = Mathf.Cos(0f);              // Returns 1

// Convert between degrees and radians
float radians = 90f * Mathf.Deg2Rad;   // 90 degrees → ~1.57 radians
float degrees = 1.57f * Mathf.Rad2Deg; // ~1.57 radians → 90 degrees

// Infinity and PI
float inf = Mathf.Infinity;
float pi = Mathf.PI;      // 3.14159...

// Ping-pong — bounces between 0 and a max
float bounce = Mathf.PingPong(Time.time, 1f);  // Goes 0→1→0→1→...

// Smooth step — smooth curve between 0 and 1
float smooth = Mathf.SmoothStep(0f, 1f, t);
```

---

## 19. Common Patterns and Best Practices

### Guard Clauses (Early Return)

Instead of deeply nested if-statements, return early when conditions are not met.

```csharp
// Bad — hard to read (arrow of doom)
void Shoot()
{
    if (_isAlive)
    {
        if (_hasGun)
        {
            if (_ammo > 0)
            {
                FireBullet();
            }
        }
    }
}

// Good — flat and readable
void Shoot()
{
    if (!_isAlive) return;
    if (!_hasGun) return;
    if (_ammo <= 0) return;

    FireBullet();
}
```

### Null Checks

Always check references before using them to avoid NullReferenceExceptions.

```csharp
// Unsafe
_lanternLight.enabled = false;  // Crashes if light was not assigned

// Safe
if (_lanternLight != null)
    _lanternLight.enabled = false;

// Modern C# null-conditional operator (even cleaner)
_lanternLight?.gameObject.SetActive(false);
```

### Ternary Operator

A one-line if/else for simple assignments.

```csharp
// Long version
string label;
if (_isAnchored)
    label = "Anchored";
else
    label = "Moving";

// Short ternary version
string label = _isAnchored ? "Anchored" : "Moving";

// In Unity
_rb.velocity = _isAnchored ? Vector3.zero : _rb.velocity;
```

### Caching References

Never call `GetComponent`, `FindObjectOfType`, or `GameObject.Find` inside `Update`. Always cache in `Awake`.

```csharp
// BAD — searches every single frame (very slow)
void Update()
{
    GetComponent<Rigidbody>().AddForce(Vector3.up);
}

// GOOD — searches once, reuses the result
private Rigidbody _rb;
void Awake() { _rb = GetComponent<Rigidbody>(); }
void Update() { _rb.AddForce(Vector3.up); }
```

### Namespace

Namespaces group your code and prevent name conflicts between scripts.

```csharp
namespace MyGame.Player
{
    public class PlayerController : MonoBehaviour { }
}

namespace MyGame.Enemies
{
    public class PlayerController : MonoBehaviour { }  // No conflict!
}

// To use a class from another namespace
using MyGame.Player;
```

### Singleton Pattern

Ensures only one instance of a script exists (GameManager, AudioManager, etc.).

```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject); // Optional: survive scene loads
    }

    public void AddScore(int amount)
    {
        _score += amount;
    }
}

// Access from any script, anywhere
GameManager.Instance.AddScore(100);
```

---

## Quick Reference Card

```
LIFECYCLE ORDER
───────────────────────────────
Awake → OnEnable → Start
→ [FixedUpdate → Update → LateUpdate] (repeating)
→ OnDisable → OnDestroy

PHYSICS RULES
───────────────────────────────
Forces / velocity    →  FixedUpdate
Input reading        →  Update
Camera follow        →  LateUpdate
Always * Time.deltaTime (Update) or Time.fixedDeltaTime (FixedUpdate)

GETCOMPONENT RULES
───────────────────────────────
Always cache in Awake
Never call in Update
Use TryGetComponent for safety

COLLISION RULES
───────────────────────────────
OnCollision = physical contact (solid walls, floors)
OnTrigger   = invisible zones (pickups, checkpoints)
Both sides need a Collider
One side needs a Rigidbody

NULL SAFETY
───────────────────────────────
if (thing != null) thing.DoSomething();
thing?.DoSomething();     // Null conditional
TryGetComponent instead of GetComponent
```

---

*Documentation version: Unity 2022 LTS / 2023+*
*All concepts apply to Unity 6 as well.*
