# Unity — Position, Rotation & Movement
### The Complete Beginner Guide (No Confusion Left Behind)

---

## Table of Contents

1. [The 3D World — X, Y, Z Explained](#1-the-3d-world--x-y-z-explained)
2. [Transform — The One Component Every Object Has](#2-transform--the-one-component-every-object-has)
3. [Position — Where Is the Object?](#3-position--where-is-the-object)
4. [World Space vs Local Space](#4-world-space-vs-local-space)
5. [Moving Objects — Every Method Explained](#5-moving-objects--every-method-explained)
6. [Rotation — The Most Confusing Topic Made Simple](#6-rotation--the-most-confusing-topic-made-simple)
7. [Euler Angles — Degrees You Already Know](#7-euler-angles--degrees-you-already-know)
8. [Quaternion — The Scary One Explained Simply](#8-quaternion--the-scary-one-explained-simply)
9. [Rotating Objects — Every Method Explained](#9-rotating-objects--every-method-explained)
10. [Scale — Making Objects Bigger or Smaller](#10-scale--making-objects-bigger-or-smaller)
11. [Direction Vectors — forward, right, up](#11-direction-vectors--forward-right-up)
12. [Vector3 Math You Actually Need](#12-vector3-math-you-actually-need)
13. [LookAt — Making Objects Face a Target](#13-lookat--making-objects-face-a-target)
14. [Parent and Child Objects](#14-parent-and-child-objects)
15. [Lerp and Slerp — Smooth Movement](#15-lerp-and-slerp--smooth-movement)
16. [Common Real-World Examples](#16-common-real-world-examples)
17. [Cheat Sheet](#17-cheat-sheet)

---

## 1. The 3D World — X, Y, Z Explained

Before anything else, you need to understand the **three axes** Unity uses. Think of your room:

```
        Y (Up)
        │
        │
        │_________ X (Right)
       /
      /
     Z (Forward — toward you)
```

| Axis | Direction | Think of it as |
|------|-----------|---------------|
| **X** | Left ←→ Right | Moving sideways |
| **Y** | Down ↕ Up | Moving up or falling down |
| **Z** | Back ↔ Forward | Moving forward or backward |

Every object in Unity has a position described as three numbers: **(X, Y, Z)**.

- A position of **(0, 0, 0)** means the object is at the very **center of the world** (called the origin).
- A position of **(5, 0, 0)** means the object is **5 units to the right** of center.
- A position of **(0, 3, 0)** means the object is **3 units above** the ground.
- A position of **(0, 0, -10)** means the object is **10 units behind** the origin.

```
Example scene layout (top-down view):
                     Z+
                     │
           (-3,0,2)  │  (3,0,2)
                     │
    X- ──────────────0────────────── X+
                     │
           (-3,0,-2) │  (3,0,-2)
                     │
                     Z-
```

---

## 2. Transform — The One Component Every Object Has

Every single GameObject in Unity **always has a Transform**. You cannot remove it. It stores three things:

```
Transform
├── Position  → Where is this object in the world?
├── Rotation  → Which direction is this object facing?
└── Scale     → How big or small is this object?
```

You access the Transform of any MonoBehaviour script using `transform` (lowercase):

```csharp
// These all work from inside any MonoBehaviour
transform.position          // This object's position
transform.rotation          // This object's rotation (as Quaternion)
transform.eulerAngles       // This object's rotation (as XYZ degrees)
transform.localScale        // This object's scale
transform.forward           // The direction this object is facing
```

To access another object's transform:

```csharp
[SerializeField] private GameObject _enemy;

void Update()
{
    Vector3 enemyPos = _enemy.transform.position;
}
```

---

## 3. Position — Where Is the Object?

### Reading Position

```csharp
Vector3 myPosition = transform.position;

// Individual components
float myX = transform.position.x;
float myY = transform.position.y;
float myZ = transform.position.z;

Debug.Log("I am at: " + transform.position);
// Output: I am at: (3.0, 0.0, 5.0)
```

### Setting Position (Teleporting)

```csharp
// Move to a specific point instantly (teleport)
transform.position = new Vector3(0f, 0f, 0f);   // Go to world center
transform.position = new Vector3(5f, 2f, -3f);  // Go to X=5, Y=2, Z=-3

// Useful shortcut: only change one axis
// You CANNOT do: transform.position.x = 5f;  ← This does NOT work in Unity
// You MUST do:
Vector3 pos = transform.position;
pos.x = 5f;
transform.position = pos;
```

**Why can't you do `transform.position.x = 5f`?**
Because `transform.position` returns a **copy** of the Vector3, not the real one. Changing a copy does nothing. You must grab the copy, change it, then set the whole thing back.

### Distance Between Two Objects

```csharp
Vector3 playerPos = transform.position;
Vector3 enemyPos = enemy.transform.position;

float distance = Vector3.Distance(playerPos, enemyPos);
Debug.Log("Distance to enemy: " + distance);

// Trigger something when close enough
if (distance < 5f)
{
    Debug.Log("Enemy is nearby!");
}
```

---

## 4. World Space vs Local Space

This is one of the most confusing concepts. Pay close attention.

### World Space

**World Space** is the position/rotation measured from the **center of the entire world (0,0,0)**. It never changes based on parents.

```csharp
transform.position      // World space position
transform.eulerAngles   // World space rotation
```

```
World (0,0,0)
    │
    └── Car at World Position (10, 0, 5)
            │
            └── Wheel at World Position (11, 0, 5)
```

### Local Space

**Local Space** is the position/rotation measured **relative to the parent object**. If the parent moves, the child moves with it, but its local position stays the same.

```csharp
transform.localPosition     // Position relative to parent
transform.localEulerAngles  // Rotation relative to parent
transform.localScale        // Scale relative to parent
```

```
Car at World Position (10, 0, 5)
    │
    └── Wheel at Local Position (1, 0, 0)
        (which means: 1 unit to the right of the car)
        (World position of wheel = 10+1, 0+0, 5+0 = (11, 0, 5))

If the Car moves to World Position (20, 0, 5):
    └── Wheel is still at Local Position (1, 0, 0)
        But its World position is now (21, 0, 5)
```

### When to Use Which?

| Situation | Use |
|-----------|-----|
| Finding distance between two objects | `transform.position` (World) |
| Moving an object in its own direction | `transform.localPosition` or `Translate` |
| Camera following a player | `transform.position` (World) |
| Attaching a sword to a hand bone | `transform.localPosition` (Local) |
| Spawning a bullet at the barrel | `transform.position` (World) |

---

## 5. Moving Objects — Every Method Explained

### Method 1 — Direct Assignment (Teleport)

```csharp
transform.position = new Vector3(10f, 0f, 0f);
```
- Instantly teleports the object. No smooth movement.
- Use for: spawning, resetting position, cutscenes.
- **Does NOT interact with physics.** The object phases through walls.

---

### Method 2 — Adding to Position

```csharp
void Update()
{
    transform.position += new Vector3(0f, 0f, 1f) * Time.deltaTime;
    // Moves 1 unit per second in the world Z direction
}
```
- Simple and direct.
- The direction is always **world space** — Z+ is always world-forward regardless of which way the object is facing.
- Use for: simple scripted movement, non-physics objects.

---

### Method 3 — Transform.Translate (Relative Movement)

```csharp
void Update()
{
    // Move in the object's OWN forward direction
    transform.Translate(Vector3.forward * _speed * Time.deltaTime);

    // Move in WORLD forward direction (same as adding to position)
    transform.Translate(Vector3.forward * _speed * Time.deltaTime, Space.World);
}
```

**This is the key difference between Translate and += :**

```
Object is facing right (rotated 90 degrees on Y axis)

transform.position += Vector3.forward * 5f
→ Object moves in WORLD Z direction (straight into the screen)

transform.Translate(Vector3.forward * 5f)
→ Object moves in ITS OWN forward direction (to the right, because it's rotated)
```

**Default:** `Translate` uses **local space** (the object's own directions).
**With `Space.World`:** Uses world directions (same as adding to position).

---

### Method 4 — Vector3.MoveTowards (Move to a Target, No Overshoot)

```csharp
[SerializeField] private Transform _target;
[SerializeField] private float _speed = 3f;

void Update()
{
    transform.position = Vector3.MoveTowards(
        transform.position,   // Current position
        _target.position,     // Target position
        _speed * Time.deltaTime  // Max distance to move this frame
    );
}
```

- Moves toward a point at a **steady speed**.
- **Never overshoots** — stops exactly at the target.
- Use for: enemies walking to a waypoint, projectiles, slow doors.

---

### Method 5 — Vector3.Lerp (Smooth Follow)

```csharp
void Update()
{
    transform.position = Vector3.Lerp(
        transform.position,     // Start (current position)
        _target.position,       // End (target position)
        _followSpeed * Time.deltaTime  // How fast to approach (0 to 1)
    );
}
```

- Gets **faster when far away** and **slows down near the target**.
- Creates that classic "easing in" smooth movement feel.
- Use for: cameras, UI elements, smooth transitions.

**Important:** Lerp with a low `t` value (like `0.1f`) never fully reaches the target — it just gets extremely close. Use `MoveTowards` if you need it to arrive exactly.

---

### Method 6 — Rigidbody (Physics Movement)

```csharp
private Rigidbody _rb;
void Awake() { _rb = GetComponent<Rigidbody>(); }

void FixedUpdate()
{
    // Push with a force
    _rb.AddForce(transform.forward * _speed, ForceMode.Acceleration);

    // Set velocity directly
    _rb.velocity = transform.forward * _speed;
}
```

- Respects physics: collides with walls, affected by gravity, has momentum.
- **Must be done in `FixedUpdate`**, not `Update`.
- Use for: any object that needs realistic physics (players, vehicles, projectiles).

---

## 6. Rotation — The Most Confusing Topic Made Simple

Rotation is confusing because Unity stores it internally as a **Quaternion** (4 numbers), but you think about rotation as **degrees** (Euler angles).

Here is the simple mental model:

```
What YOU think about:   Euler Angles  (X degrees, Y degrees, Z degrees)
What Unity stores:      Quaternion    (x, y, z, w) — 4 numbers, never touch directly

Unity handles the conversion between the two automatically.
You mostly work with Euler angles and Unity deals with Quaternions behind the scenes.
```

### What do X, Y, Z rotation mean?

Imagine holding a toy airplane:

| Rotation Axis | What It Does | Real World Name |
|---------------|-------------|-----------------|
| **X rotation** | Nose tilts up or down | Pitch |
| **Y rotation** | Turns left or right | Yaw |
| **Z rotation** | Tilts/rolls sideways | Roll |

```
        Pitch (X)          Yaw (Y)            Roll (Z)
        ─────────          ───────            ────────
        nose up/down    turning left/right    tilting sideways

        ↑ nose              ← →                 ↙ ↘
        ──────           ──plane──           ───plane───
        ↓ tail
```

---

## 7. Euler Angles — Degrees You Already Know

**Euler Angles** are the rotation expressed in simple degrees (0° to 360°). This is how you think about rotation normally.

### Reading Rotation

```csharp
Vector3 rotation = transform.eulerAngles;

float pitchX = transform.eulerAngles.x;  // Tilt up/down
float yawY   = transform.eulerAngles.y;  // Turn left/right
float rollZ  = transform.eulerAngles.z;  // Roll sideways

Debug.Log("Facing direction: " + transform.eulerAngles.y + " degrees");
```

### Setting Rotation (Snap to exact angle)

```csharp
// Face north (toward Z+)
transform.eulerAngles = new Vector3(0f, 0f, 0f);

// Face right (90 degrees turn on Y axis)
transform.eulerAngles = new Vector3(0f, 90f, 0f);

// Face left
transform.eulerAngles = new Vector3(0f, -90f, 0f);
// or
transform.eulerAngles = new Vector3(0f, 270f, 0f);

// Face backward
transform.eulerAngles = new Vector3(0f, 180f, 0f);

// Tilt nose up 45 degrees
transform.eulerAngles = new Vector3(-45f, 0f, 0f);
// (Negative X tilts up, positive X tilts down in Unity)
```

### Common Y Rotation Values (Top-Down View)

```
          0°  (North / Z+)
          │
  270°  ──┼──  90°
  (West)  │  (East)
          │
         180° (South / Z-)
```

### Setting One Axis Only

```csharp
// Only change the Y rotation, keep X and Z the same
Vector3 euler = transform.eulerAngles;
euler.y = 90f;
transform.eulerAngles = euler;
```

---

## 8. Quaternion — The Scary One Explained Simply

A **Quaternion** is how Unity stores rotation internally. It uses 4 numbers (x, y, z, w) and avoids a problem called **Gimbal Lock** that Euler angles have.

**You almost never need to understand the math.** You just need to know how to use it.

```csharp
// NEVER set Quaternion values directly like this
transform.rotation = new Quaternion(0.5f, 0.2f, 0.1f, 0.8f);  // ← Don't do this

// ALWAYS use these helper methods instead:
Quaternion.Euler(x, y, z)      // Create rotation from degrees
Quaternion.identity            // Zero rotation (no rotation at all)
Quaternion.LookRotation(dir)   // Create rotation that faces a direction
Quaternion.Slerp(a, b, t)      // Smoothly blend between two rotations
Quaternion.AngleAxis(angle, axis) // Rotate by angle around an axis
```

### Quaternion.Euler — Convert Degrees to Quaternion

```csharp
// Set rotation using degrees (most common)
transform.rotation = Quaternion.Euler(0f, 90f, 0f);  // Face right

// Same as:
transform.eulerAngles = new Vector3(0f, 90f, 0f);
```

### Quaternion.identity — No Rotation

```csharp
// Reset rotation to default (no rotation)
transform.rotation = Quaternion.identity;
// Same as: transform.eulerAngles = Vector3.zero;
```

### Quaternion.LookRotation — Face a Direction

```csharp
// Make the object face the direction it is moving
Vector3 moveDirection = new Vector3(1f, 0f, 1f);  // Moving diagonally
transform.rotation = Quaternion.LookRotation(moveDirection);
// Object now faces diagonally (45 degrees)
```

### Why Does Unity Use Quaternions at All?

There is a problem called **Gimbal Lock** with Euler angles. It happens when two rotation axes line up and you lose one axis of rotation. You may have seen it in 3D software where an object suddenly can't rotate one way. Quaternions mathematically avoid this completely. Unity uses them internally so rotation always works correctly. You don't need to understand the math — just use the helper functions above.

---

## 9. Rotating Objects — Every Method Explained

### Method 1 — Transform.Rotate (Add rotation every frame)

```csharp
void Update()
{
    // Spin around the Y axis (turn left/right) at 90 degrees per second
    transform.Rotate(Vector3.up, 90f * Time.deltaTime);

    // Tilt nose up at 45 degrees per second
    transform.Rotate(Vector3.right, 45f * Time.deltaTime);

    // Roll at 30 degrees per second
    transform.Rotate(Vector3.forward, 30f * Time.deltaTime);

    // Or pass all three at once (X, Y, Z degrees per frame)
    transform.Rotate(new Vector3(0f, 90f, 0f) * Time.deltaTime);
}
```

**Space parameter:**

```csharp
// Rotate in LOCAL space (default) — relative to the object's own axes
transform.Rotate(Vector3.up, 90f * Time.deltaTime, Space.Self);

// Rotate in WORLD space — always rotates around world Y, regardless of current tilt
transform.Rotate(Vector3.up, 90f * Time.deltaTime, Space.World);
```

---

### Method 2 — Setting eulerAngles Directly (Snap to angle)

```csharp
// Instantly snap to face right
transform.eulerAngles = new Vector3(0f, 90f, 0f);

// Smoothly rotate toward a target angle using Mathf.LerpAngle
float currentY = transform.eulerAngles.y;
float targetY = 90f;
float smoothY = Mathf.LerpAngle(currentY, targetY, 5f * Time.deltaTime);
transform.eulerAngles = new Vector3(0f, smoothY, 0f);
```

---

### Method 3 — Quaternion.Slerp (Smooth Rotation Toward Target)

`Slerp` stands for **Spherical Linear Interpolation**. It smoothly rotates from one rotation to another.

```csharp
[SerializeField] private Transform _target;
[SerializeField] private float _rotateSpeed = 3f;

void Update()
{
    // Find the direction to the target
    Vector3 direction = _target.position - transform.position;

    // Create the target rotation (facing that direction)
    Quaternion targetRotation = Quaternion.LookRotation(direction);

    // Smoothly rotate toward it
    transform.rotation = Quaternion.Slerp(
        transform.rotation,    // Current rotation
        targetRotation,        // Target rotation
        _rotateSpeed * Time.deltaTime  // Speed (0=no movement, 1=instant)
    );
}
```

Use `Slerp` for rotations. Use `Lerp` for positions. They both do smooth blending but `Slerp` is designed for angles and handles the "shortest path" correctly.

---

### Method 4 — Quaternion.RotateTowards (Rotate at Fixed Speed)

```csharp
void Update()
{
    Vector3 direction = _target.position - transform.position;
    Quaternion targetRotation = Quaternion.LookRotation(direction);

    transform.rotation = Quaternion.RotateTowards(
        transform.rotation,
        targetRotation,
        _degreesPerSecond * Time.deltaTime  // Max degrees to rotate this frame
    );
}
```

- Rotates at a **constant speed** in degrees per second.
- **Never overshoots** — stops exactly at the target rotation.
- Use this over `Slerp` when you want predictable, consistent rotation speed.

---

### Method 5 — Rigidbody.MoveRotation (Physics Rotation)

```csharp
void FixedUpdate()
{
    Quaternion deltaRotation = Quaternion.Euler(0f, _turnSpeed * Time.fixedDeltaTime, 0f);
    _rb.MoveRotation(_rb.rotation * deltaRotation);
}
```

- Use when the object has a Rigidbody and physics matters.
- Respects collision during rotation.

---

## 10. Scale — Making Objects Bigger or Smaller

Scale multiplies the object's size. A scale of `(1, 1, 1)` is normal size. `(2, 2, 2)` is double size.

```csharp
// Set scale
transform.localScale = new Vector3(1f, 1f, 1f);    // Normal size
transform.localScale = new Vector3(2f, 2f, 2f);    // Double size
transform.localScale = new Vector3(0.5f, 0.5f, 0.5f); // Half size
transform.localScale = Vector3.one * 3f;             // Triple size (shorthand)

// Only scale on one axis (stretch)
transform.localScale = new Vector3(1f, 3f, 1f);    // Stretch tall (3x height)
transform.localScale = new Vector3(3f, 1f, 1f);    // Stretch wide

// Animate scale (pulse effect)
void Update()
{
    float pulse = 1f + Mathf.Sin(Time.time * 2f) * 0.1f;  // Oscillates 0.9 to 1.1
    transform.localScale = Vector3.one * pulse;
}
```

**Note:** Always use `localScale`, not `lossyScale`. `lossyScale` is the **world scale** (including parent's scale) and it is read-only.

---

## 11. Direction Vectors — forward, right, up

These are the most used shorthand properties. They give you a **unit vector** (length = 1) pointing in that direction **from the object's current rotation**.

```csharp
transform.forward   // Direction the object is FACING (its blue arrow / Z+)
transform.right     // Direction to the object's RIGHT (its red arrow / X+)
transform.up        // Direction above the object (its green arrow / Y+)

// Opposites
-transform.forward  // Behind the object
-transform.right    // Left of the object
-transform.up       // Below the object
```

### World directions vs Object directions

```csharp
// These are ALWAYS the same regardless of rotation
Vector3.forward  // (0, 0, 1)  — World Z+
Vector3.right    // (1, 0, 0)  — World X+
Vector3.up       // (0, 1, 0)  — World Y+

// These CHANGE with the object's rotation
transform.forward  // Where THIS object is facing RIGHT NOW
transform.right    // THIS object's right direction RIGHT NOW
transform.up       // THIS object's up direction RIGHT NOW
```

```
Example:
Object is rotated 90 degrees on Y (facing right):

    transform.forward = (1, 0, 0)   ← Pointing right (world X+), not world Z+
    transform.right   = (0, 0, -1)  ← Pointing backward (world Z-)
    transform.up      = (0, 1, 0)   ← Still pointing up (Y never changes)
```

### Practical Uses

```csharp
// Shoot a bullet forward from this object
GameObject bullet = Instantiate(_bulletPrefab, transform.position, transform.rotation);
bullet.GetComponent<Rigidbody>().velocity = transform.forward * _bulletSpeed;

// Check if an object is in front of me or behind me
Vector3 directionToTarget = (target.position - transform.position).normalized;
float dot = Vector3.Dot(transform.forward, directionToTarget);
// dot > 0  → target is in FRONT of me
// dot < 0  → target is BEHIND me
// dot = 0  → target is exactly to my side

// Move in the direction I'm facing
transform.position += transform.forward * _speed * Time.deltaTime;

// Jump in the up direction (local up)
_rb.AddForce(transform.up * _jumpForce, ForceMode.Impulse);
```

---

## 12. Vector3 Math You Actually Need

### Adding and Subtracting Vectors

```csharp
Vector3 a = new Vector3(1f, 0f, 0f);  // 1 unit right
Vector3 b = new Vector3(0f, 0f, 1f);  // 1 unit forward

Vector3 combined = a + b;   // (1, 0, 1) — right AND forward
Vector3 diff = b - a;       // (-1, 0, 1) — the direction from A to B
```

### Finding Direction Between Two Points

```csharp
Vector3 myPosition     = transform.position;         // (0, 0, 0)
Vector3 targetPosition = new Vector3(3f, 0f, 4f);    // (3, 0, 4)

// Raw direction (NOT normalized — its length is the distance)
Vector3 rawDirection = targetPosition - myPosition;  // (3, 0, 4)

// Normalized direction (length = 1, just the direction, no distance info)
Vector3 direction = (targetPosition - myPosition).normalized;  // (0.6, 0, 0.8)

// Always normalize when you just want "which way", not "how far"
```

### Magnitude — The Length/Distance of a Vector

```csharp
Vector3 v = new Vector3(3f, 0f, 4f);

float length = v.magnitude;          // √(3²+0²+4²) = √25 = 5
float lengthSq = v.sqrMagnitude;     // 25 (faster — avoids square root)
```

**Use `sqrMagnitude` for distance comparisons** — it avoids the expensive square root:

```csharp
// Slow (uses Mathf.Sqrt internally)
if (Vector3.Distance(transform.position, target.position) < 5f) { }

// Fast (compare squared values instead)
if ((transform.position - target.position).sqrMagnitude < 25f) { } // 5² = 25
```

### Dot Product — How Aligned Are Two Directions?

```csharp
float dot = Vector3.Dot(directionA, directionB);
```

Both vectors should be normalized. The result:

```
dot =  1.0  → Pointing in EXACTLY the same direction
dot =  0.5  → 60 degrees apart
dot =  0.0  → PERPENDICULAR (90 degrees apart)
dot = -0.5  → 120 degrees apart
dot = -1.0  → Pointing in EXACTLY opposite directions
```

**Real example — is the enemy visible?**

```csharp
void CanISeeEnemy()
{
    Vector3 dirToEnemy = (enemy.position - transform.position).normalized;
    float dot = Vector3.Dot(transform.forward, dirToEnemy);

    if (dot > 0.5f)
        Debug.Log("Enemy is in my field of view!");
    // dot > 0.5 means within 60 degrees of my facing direction
}
```

### Cross Product — Find a Perpendicular Direction

```csharp
// Find a direction perpendicular to both A and B
Vector3 perp = Vector3.Cross(Vector3.forward, Vector3.right);
// Result: Vector3.down (the perpendicular to forward and right is downward)
```

Use case: finding the "up" direction of a surface, making an object align to a slope.

---

## 13. LookAt — Making Objects Face a Target

### Simple LookAt

```csharp
void Update()
{
    // Always face the player
    transform.LookAt(_player.transform);

    // Face a specific world position
    transform.LookAt(new Vector3(0f, 0f, 0f));

    // Look at but keep upright (ignore Y difference — good for enemies on ground)
    Vector3 targetPos = _player.transform.position;
    targetPos.y = transform.position.y;  // Lock Y to same height
    transform.LookAt(targetPos);
}
```

### Smooth LookAt

`LookAt` is instant. For smooth rotation use `Quaternion.Slerp`:

```csharp
void Update()
{
    Vector3 direction = _player.transform.position - transform.position;
    direction.y = 0f;  // Keep level (don't tilt up/down)

    if (direction != Vector3.zero)
    {
        Quaternion targetRot = Quaternion.LookRotation(direction);
        transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, 5f * Time.deltaTime);
    }
}
```

**Why `if (direction != Vector3.zero)`?**
If the target is at the exact same position, `direction` becomes (0,0,0) and `LookRotation` would crash. This guard prevents that.

---

## 14. Parent and Child Objects

In Unity's scene hierarchy, objects can be **parents** and **children**. Children follow their parent.

```
── Car (Parent)
     ├── Body (Child)
     ├── Wheel_FL (Child)
     ├── Wheel_FR (Child)
     └── Driver (Child)
            └── Hand (Grandchild)
```

If the **Car** moves to position (10, 0, 0), all children move with it automatically.

### Accessing Hierarchy

```csharp
// Get this object's parent
Transform parent = transform.parent;

// Get children
Transform firstChild = transform.GetChild(0);  // First child
int childCount = transform.childCount;

// Loop through all children
foreach (Transform child in transform)
{
    Debug.Log(child.name);
}

// Set a new parent
childObject.transform.SetParent(newParent.transform);

// Detach from parent (make it a root object)
transform.SetParent(null);
```

### World vs Local Position with Parents

```csharp
// Parent is at world position (10, 0, 0)
// Child has local position (1, 0, 0)
// Child's WORLD position = (11, 0, 0)

transform.position       // World: (11, 0, 0)
transform.localPosition  // Local: (1, 0, 0)

// Moving a child:
transform.localPosition += Vector3.right;  // Moves relative to parent
transform.position += Vector3.right;       // Moves in world space
```

---

## 15. Lerp and Slerp — Smooth Movement

These two functions are used constantly in Unity for smooth animations.

### Vector3.Lerp — Smooth Position

**Lerp** = Linear Interpolation. It finds a point between two values.

```csharp
Vector3 result = Vector3.Lerp(start, end, t);
// t = 0.0  → result = start
// t = 0.5  → result = halfway between start and end
// t = 1.0  → result = end
```

**Smooth follow (most common use):**

```csharp
void Update()
{
    // Every frame, move 5% closer to the target
    // The closer you are, the slower you move (smooth ease-in)
    transform.position = Vector3.Lerp(transform.position, _target.position, 5f * Time.deltaTime);
}
```

**Fixed duration move (one-shot):**

```csharp
IEnumerator MoveToTarget(Vector3 destination, float duration)
{
    Vector3 startPos = transform.position;
    float elapsed = 0f;

    while (elapsed < duration)
    {
        elapsed += Time.deltaTime;
        float t = elapsed / duration;              // 0 to 1 over the duration
        transform.position = Vector3.Lerp(startPos, destination, t);
        yield return null;
    }

    transform.position = destination;  // Snap to exact position at the end
}
```

### Quaternion.Slerp — Smooth Rotation

**Slerp** = Spherical Linear Interpolation. Like Lerp but designed for rotations. Always takes the **shortest arc** between two rotations.

```csharp
// Smooth rotate toward target rotation
transform.rotation = Quaternion.Slerp(
    transform.rotation,    // Current
    targetRotation,        // Target
    _speed * Time.deltaTime
);
```

**Why Slerp for rotations and not Lerp?**
`Quaternion.Lerp` also exists but it can give incorrect results at extreme angles. `Slerp` always finds the shortest rotational path and gives smooth, correct results. Use `Slerp` for rotations always.

### Mathf.Lerp — Smooth Single Values

```csharp
// Smooth a float value
float current = 0f;
float target  = 100f;

void Update()
{
    current = Mathf.Lerp(current, target, 3f * Time.deltaTime);
    // Use for: audio volume, light intensity, UI opacity
}

// Smooth an angle (handles 359→1 correctly, won't go the long way around)
float angle = Mathf.LerpAngle(currentAngle, targetAngle, speed * Time.deltaTime);
```

---

## 16. Common Real-World Examples

### Camera Follow Player

```csharp
public class CameraFollow : MonoBehaviour
{
    [SerializeField] private Transform _player;
    [SerializeField] private Vector3 _offset = new Vector3(0f, 5f, -7f);
    [SerializeField] private float _followSpeed = 5f;

    void LateUpdate()  // Always LateUpdate for cameras!
    {
        // Target position = player's position + offset behind/above them
        Vector3 targetPos = _player.position + _offset;

        // Smooth follow
        transform.position = Vector3.Lerp(transform.position, targetPos, _followSpeed * Time.deltaTime);

        // Always look at the player
        transform.LookAt(_player);
    }
}
```

---

### Enemy Follows Player

```csharp
public class EnemyChase : MonoBehaviour
{
    [SerializeField] private Transform _player;
    [SerializeField] private float _moveSpeed = 3f;
    [SerializeField] private float _rotateSpeed = 5f;
    [SerializeField] private float _stoppingDistance = 1.5f;

    void Update()
    {
        float distance = Vector3.Distance(transform.position, _player.position);

        // Rotate to face player
        Vector3 direction = (_player.position - transform.position).normalized;
        direction.y = 0f;  // Keep on the ground — don't tilt upward
        if (direction != Vector3.zero)
        {
            Quaternion targetRot = Quaternion.LookRotation(direction);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, _rotateSpeed * Time.deltaTime);
        }

        // Move toward player if far enough
        if (distance > _stoppingDistance)
        {
            transform.position = Vector3.MoveTowards(
                transform.position,
                _player.position,
                _moveSpeed * Time.deltaTime
            );
        }
    }
}
```

---

### Bullet Moving Forward

```csharp
public class Bullet : MonoBehaviour
{
    [SerializeField] private float _speed = 20f;
    [SerializeField] private float _lifetime = 3f;

    void Start()
    {
        Destroy(gameObject, _lifetime);  // Auto-destroy after 3 seconds
    }

    void Update()
    {
        // Move forward in the direction this object is facing
        transform.position += transform.forward * _speed * Time.deltaTime;
    }
}
```

---

### Spinning Collectible

```csharp
public class Collectible : MonoBehaviour
{
    [SerializeField] private float _spinSpeed = 90f;   // degrees per second
    [SerializeField] private float _bobHeight = 0.3f;  // how high it bobs
    [SerializeField] private float _bobSpeed = 2f;

    private Vector3 _startPosition;

    void Start()
    {
        _startPosition = transform.position;
    }

    void Update()
    {
        // Spin around Y axis
        transform.Rotate(Vector3.up, _spinSpeed * Time.deltaTime);

        // Bob up and down using a sine wave
        float newY = _startPosition.y + Mathf.Sin(Time.time * _bobSpeed) * _bobHeight;
        transform.position = new Vector3(transform.position.x, newY, transform.position.z);
    }
}
```

---

### Projectile Arc (Throw with Physics)

```csharp
public class ThrowableObject : MonoBehaviour
{
    [SerializeField] private float _throwForce = 10f;
    [SerializeField] private float _throwAngle = 45f;  // degrees above horizontal

    private Rigidbody _rb;

    void Start()
    {
        _rb = GetComponent<Rigidbody>();
        Throw();
    }

    void Throw()
    {
        // Rotate the launch direction upward by _throwAngle
        Quaternion angleOffset = Quaternion.AngleAxis(-_throwAngle, transform.right);
        Vector3 throwDir = angleOffset * transform.forward;

        _rb.AddForce(throwDir * _throwForce, ForceMode.Impulse);
    }
}
```

---

## 17. Cheat Sheet

```
POSITION
─────────────────────────────────────────────────────
transform.position              Read/Write world position
transform.localPosition         Read/Write local (relative to parent) position
transform.position.x / .y / .z Read only one axis

Move options:
  transform.position = new Vector3(x, y, z)       Teleport
  transform.position += direction * speed * dt    Move by offset
  transform.Translate(dir * speed * dt)           Move in local space
  Vector3.MoveTowards(cur, target, speed * dt)    Steady, no overshoot
  Vector3.Lerp(cur, target, speed * dt)           Smooth ease-in


ROTATION
─────────────────────────────────────────────────────
transform.eulerAngles           Read/Write degrees (world)
transform.localEulerAngles      Read/Write degrees (local)
transform.rotation              Read/Write Quaternion (world)
transform.localRotation         Read/Write Quaternion (local)

Rotate options:
  transform.eulerAngles = new Vector3(x, y, z)    Snap to angle
  transform.Rotate(axis, degrees * dt)            Add rotation
  transform.LookAt(target)                        Instantly face target
  Quaternion.Slerp(cur, target, speed * dt)       Smooth rotation
  Quaternion.RotateTowards(cur, target, deg * dt) Steady, no overshoot

Quaternion helpers (use these, never touch x/y/z/w directly):
  Quaternion.Euler(x, y, z)       Create from degrees
  Quaternion.identity             No rotation
  Quaternion.LookRotation(dir)    Create from direction vector
  Quaternion.AngleAxis(a, axis)   Rotate by angle around axis


SCALE
─────────────────────────────────────────────────────
transform.localScale = new Vector3(x, y, z)
transform.localScale = Vector3.one * multiplier


DIRECTIONS (change with object rotation)
─────────────────────────────────────────────────────
transform.forward   Where object is facing (Z+)
transform.right     Object's right (X+)
transform.up        Object's up (Y+)
-transform.forward  Behind
-transform.right    Left
-transform.up       Below

WORLD directions (never change):
Vector3.forward = (0,0,1)
Vector3.right   = (1,0,0)
Vector3.up      = (0,1,0)


VECTOR3 MATH
─────────────────────────────────────────────────────
Vector3.Distance(a, b)              Distance between two points
(b - a).normalized                  Direction from A to B
v.magnitude                         Length of vector
v.normalized                        Same direction, length = 1
Vector3.Dot(a, b)                   Alignment (-1 to 1)
Vector3.Cross(a, b)                 Perpendicular vector
Vector3.Lerp(a, b, t)               Blend between two positions
Vector3.MoveTowards(cur, tgt, spd)  Move at constant speed


SPACE REMINDER
─────────────────────────────────────────────────────
World Space  → Measured from (0,0,0) of the scene
Local Space  → Measured from the object's parent

transform.position     = World
transform.localPosition = Local
transform.Translate()  = Local by default (Space.Self)
transform.Rotate()     = Local by default (Space.Self)
```

---

*Keep this file open while coding — refer to it whenever you get confused about position or rotation.*
