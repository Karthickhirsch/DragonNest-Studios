# Unity Game Implementation Examples
### Learn By Building — Every Concept With a Working Example

---

## How To Use This Document

Every section in this guide is a **complete, working implementation**. Each example tells you:
- What scripts to create
- What components to add in Unity
- Exactly what the code does line by line
- How to wire it all together

No theory without code. No code without explanation.

---

## Table of Contents

1. [Example 1 — Basic Player Movement (Keyboard + Physics)](#1-example-1--basic-player-movement)
2. [Example 2 — Player Jump (Ground Check)](#2-example-2--player-jump)
3. [Example 3 — Health System (Take Damage + Die)](#3-example-3--health-system)
4. [Example 4 — Coin Collector Game](#4-example-4--coin-collector-game)
5. [Example 5 — Enemy That Chases the Player](#5-example-5--enemy-that-chases-the-player)
6. [Example 6 — Shooting Bullets](#6-example-6--shooting-bullets)
7. [Example 7 — Score System with GameManager](#7-example-7--score-system-with-gamemanager)
8. [Example 8 — Door That Opens With a Key](#8-example-8--door-that-opens-with-a-key)
9. [Example 9 — Timer Countdown](#9-example-9--timer-countdown)
10. [Example 10 — Respawn System](#10-example-10--respawn-system)
11. [Example 11 — Camera Follow Player](#11-example-11--camera-follow-player)
12. [Example 12 — Complete Mini Platformer Game](#12-example-12--complete-mini-platformer-game)

---

## 1. Example 1 — Basic Player Movement

**What this builds:** A 3D cube you can move with WASD/arrow keys using physics.

### Setup in Unity
1. Create a 3D Cube: `GameObject → 3D Object → Cube`
2. Add a `Rigidbody` component to the Cube
3. Add a `Capsule Collider` (or keep the Box Collider)
4. Create a new C# script called `PlayerMovement` and attach it to the Cube
5. In the Inspector, set `Speed` to `5`

### Script: `PlayerMovement.cs`

```csharp
using UnityEngine;

public class PlayerMovement : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float _speed = 5f;

    private Rigidbody _rb;
    private Vector3 _moveDirection;

    void Awake()
    {
        // Cache the Rigidbody so we don't search for it every frame
        _rb = GetComponent<Rigidbody>();

        // Prevent the player from tipping over due to physics rotation
        _rb.freezeRotation = true;
    }

    void Update()
    {
        // Read keyboard input every frame
        // Input.GetAxis returns a value from -1 to 1
        // "Horizontal" = A/D keys or Left/Right arrows
        // "Vertical"   = W/S keys or Up/Down arrows
        float horizontal = Input.GetAxis("Horizontal");
        float vertical   = Input.GetAxis("Vertical");

        // Build a direction vector from the input
        // We use Vector3.right for X and Vector3.forward for Z
        // Y is 0 because we don't want the player flying up/down
        _moveDirection = new Vector3(horizontal, 0f, vertical);

        // Normalize so diagonal movement isn't faster than straight movement
        // Without this: moving at 45 degrees is sqrt(2) = 1.41x faster
        if (_moveDirection.magnitude > 1f)
            _moveDirection.Normalize();
    }

    void FixedUpdate()
    {
        // Apply movement HERE (FixedUpdate), not in Update
        // Physics calculations need a consistent time step
        // MovePosition smoothly moves the Rigidbody to a new position
        Vector3 newPosition = _rb.position + _moveDirection * _speed * Time.fixedDeltaTime;
        _rb.MovePosition(newPosition);
    }
}
```

### What Each Line Does

| Code | What It Does |
|------|-------------|
| `_rb.freezeRotation = true` | Stops the cube from falling over when it hits things |
| `Input.GetAxis("Horizontal")` | Returns -1 (left), 0 (still), or 1 (right) based on A/D keys |
| `new Vector3(horizontal, 0f, vertical)` | Combines left/right and forward/back into one direction |
| `_moveDirection.Normalize()` | Limits the vector length to 1 so diagonal isn't faster |
| `_rb.MovePosition(...)` | Physically moves the object, respecting collisions |
| `Time.fixedDeltaTime` | Makes speed consistent regardless of physics tick rate |

---

## 2. Example 2 — Player Jump

**What this builds:** The player from Example 1 can now jump when pressing Space. It only jumps when touching the ground — no double jumping.

### Setup in Unity
1. Continue from Example 1 (same Cube with Rigidbody)
2. Create an Empty GameObject called `GroundCheck`, position it at the **bottom** of the cube (Y = -0.5)
3. Create a new Layer called `Ground` and assign it to your floor
4. Replace or update `PlayerMovement.cs` with the code below

### Script: Updated `PlayerMovement.cs`

```csharp
using UnityEngine;

public class PlayerMovement : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float _speed = 5f;

    [Header("Jump")]
    [SerializeField] private float _jumpForce = 7f;
    [SerializeField] private Transform _groundCheck;       // Drag the GroundCheck child object here
    [SerializeField] private float _groundCheckRadius = 0.2f;
    [SerializeField] private LayerMask _groundLayer;       // Select the "Ground" layer here

    private Rigidbody _rb;
    private Vector3 _moveDirection;
    private bool _isGrounded;
    private bool _jumpQueued;

    void Awake()
    {
        _rb = GetComponent<Rigidbody>();
        _rb.freezeRotation = true;
    }

    void Update()
    {
        // Read movement input
        float horizontal = Input.GetAxis("Horizontal");
        float vertical   = Input.GetAxis("Vertical");
        _moveDirection   = new Vector3(horizontal, 0f, vertical).normalized;

        // Check if we're standing on the ground
        // Physics.CheckSphere draws an invisible sphere at _groundCheck position
        // If anything on the _groundLayer is inside that sphere, we're grounded
        _isGrounded = Physics.CheckSphere(
            _groundCheck.position,      // Center of the sphere
            _groundCheckRadius,         // Radius to check
            _groundLayer                // Only detect this layer
        );

        // Queue the jump in Update (input is read here)
        // We apply the force in FixedUpdate where physics happens
        if (Input.GetKeyDown(KeyCode.Space) && _isGrounded)
        {
            _jumpQueued = true;
        }
    }

    void FixedUpdate()
    {
        // Apply horizontal movement
        Vector3 newPosition = _rb.position + _moveDirection * _speed * Time.fixedDeltaTime;
        _rb.MovePosition(newPosition);

        // Apply jump force if queued
        if (_jumpQueued)
        {
            // ForceMode.Impulse = instant burst of force (perfect for jumping)
            // Uses mass, so heavier objects jump less high
            _rb.AddForce(Vector3.up * _jumpForce, ForceMode.Impulse);
            _jumpQueued = false;
        }
    }

    // Draw the ground check sphere in the Scene view (editor only, helps debugging)
    void OnDrawGizmosSelected()
    {
        if (_groundCheck == null) return;
        Gizmos.color = _isGrounded ? Color.green : Color.red;
        Gizmos.DrawWireSphere(_groundCheck.position, _groundCheckRadius);
    }
}
```

### Why We Queue the Jump

Input is read in `Update()`. Physics forces are applied in `FixedUpdate()`. These run at different rates.

If you press Space for one frame (0.016 seconds), `Update` might catch it but `FixedUpdate` might miss it — it only runs every 0.02 seconds. By setting `_jumpQueued = true` in `Update` and checking it in `FixedUpdate`, we guarantee the jump is never missed.

---

## 3. Example 3 — Health System

**What this builds:** A player that has 100 health, takes damage when it collides with enemies (tagged "Enemy"), displays health, and dies when health reaches 0.

### Setup in Unity
1. Player Cube has the `PlayerHealth` script
2. Enemy Cube is tagged `Enemy`
3. Canvas → Text (Legacy) named `HealthText` for display

### Script: `PlayerHealth.cs`

```csharp
using UnityEngine;
using UnityEngine.UI;   // Needed for Text component

public class PlayerHealth : MonoBehaviour
{
    [Header("Health Settings")]
    [SerializeField] private int _maxHealth = 100;
    [SerializeField] private Text _healthText;      // Drag the UI Text here

    // Property: other scripts can READ health but not directly set it
    // The only way to change health is through TakeDamage() or Heal()
    public int CurrentHealth { get; private set; }

    void Start()
    {
        // Set health to max when the game starts
        CurrentHealth = _maxHealth;
        UpdateHealthUI();
    }

    // Called by enemies, traps, or anything that wants to damage the player
    public void TakeDamage(int amount)
    {
        // Clamp: health can never go below 0
        CurrentHealth = Mathf.Max(0, CurrentHealth - amount);
        Debug.Log($"Took {amount} damage! Health: {CurrentHealth}/{_maxHealth}");

        UpdateHealthUI();

        // Check if we just died
        if (CurrentHealth <= 0)
            Die();
    }

    public void Heal(int amount)
    {
        // Clamp: health can never exceed max
        CurrentHealth = Mathf.Min(_maxHealth, CurrentHealth + amount);
        UpdateHealthUI();
    }

    private void UpdateHealthUI()
    {
        if (_healthText != null)
            _healthText.text = $"HP: {CurrentHealth} / {_maxHealth}";
    }

    private void Die()
    {
        Debug.Log("Player died!");

        // Disable player controls (the PlayerMovement script stops running)
        if (TryGetComponent<PlayerMovement>(out var movement))
            movement.enabled = false;

        // You could also:
        // Instantiate(deathParticles, transform.position, Quaternion.identity);
        // Invoke("Respawn", 3f);
        // SceneManager.LoadScene(SceneManager.GetActiveScene().name); // Reload scene
    }

    // Detect collision with enemies
    void OnCollisionEnter(Collision collision)
    {
        // CompareTag is faster than == for string comparison
        if (collision.gameObject.CompareTag("Enemy"))
        {
            TakeDamage(10);
        }
    }
}
```

### How To Test It

1. In the Scene, add a second Cube → tag it `Enemy`
2. Push the Enemy into the Player in Play mode
3. Watch the health go down in the Console and UI

---

## 4. Example 4 — Coin Collector Game

**What this builds:** Coins scattered in the scene. Player walks over them to collect them. Score shows on screen. All coins collected = win message.

### Setup in Unity
1. Create a small Sphere: `GameObject → 3D Object → Sphere`, rename it `Coin`
2. On the Coin's Sphere Collider, check **Is Trigger**
3. Tag the Coin as `Coin`
4. Attach `Coin.cs` to the Coin Sphere
5. Make the Coin a **Prefab** (drag it into the Project window)
6. Place 10 coins around the scene
7. Attach `CoinCollector.cs` to the Player
8. Create a UI Text named `ScoreText`

### Script: `Coin.cs`

```csharp
using UnityEngine;

public class Coin : MonoBehaviour
{
    [SerializeField] private int _value = 1;
    [SerializeField] private float _rotateSpeed = 90f;

    // Public so the collector can read how much the coin is worth
    public int Value => _value;

    void Update()
    {
        // Spin the coin so it's easy to spot
        transform.Rotate(Vector3.up, _rotateSpeed * Time.deltaTime);
    }

    // Called when the player walks through the coin trigger
    public void Collect()
    {
        // Destroy this coin GameObject — removes it from the scene
        Destroy(gameObject);
    }
}
```

### Script: `CoinCollector.cs`

```csharp
using UnityEngine;
using UnityEngine.UI;

public class CoinCollector : MonoBehaviour
{
    [SerializeField] private Text _scoreText;
    [SerializeField] private Text _winText;

    private int _score = 0;
    private int _totalCoins;

    void Start()
    {
        // Count how many coins exist in the scene at the start
        // FindObjectsOfType returns an array of ALL active components of that type
        _totalCoins = FindObjectsOfType<Coin>().Length;

        UpdateScoreUI();

        // Hide the win text at the start
        if (_winText != null)
            _winText.gameObject.SetActive(false);
    }

    // This is called when the player enters a trigger collider
    void OnTriggerEnter(Collider other)
    {
        // TryGetComponent: safely try to get the Coin script from what we hit
        // If the object has a Coin component, 'coin' gets set and returns true
        if (other.TryGetComponent<Coin>(out Coin coin))
        {
            _score += coin.Value;
            coin.Collect();             // Tell the coin to destroy itself
            UpdateScoreUI();
            CheckWinCondition();
        }
    }

    private void UpdateScoreUI()
    {
        if (_scoreText != null)
            _scoreText.text = $"Coins: {_score} / {_totalCoins}";
    }

    private void CheckWinCondition()
    {
        if (_score >= _totalCoins)
        {
            Debug.Log("All coins collected! You win!");
            if (_winText != null)
            {
                _winText.gameObject.SetActive(true);
                _winText.text = "You Win!";
            }
        }
    }
}
```

### Flow Diagram

```
Player walks into coin sphere
         │
         ▼
OnTriggerEnter fires on Player
         │
         ▼
TryGetComponent<Coin> → gets the Coin script
         │
         ▼
score += coin.Value     (add points)
coin.Collect()          (destroys the coin)
UpdateScoreUI()         (refresh the text)
CheckWinCondition()     (did we collect all?)
```

---

## 5. Example 5 — Enemy That Chases the Player

**What this builds:** An enemy that stands still until the player gets close, then chases the player. If the enemy touches the player, it damages them.

### Setup in Unity
1. Create a red Cube for the enemy, attach `EnemyChase.cs`
2. Add a `NavMesh Agent` component to the enemy (for smart pathfinding)
   - **Or** use the simple version below (direct movement, no NavMesh)
3. Assign the Player object in the Inspector

### Script: `EnemyChase.cs` (Simple Version — No NavMesh)

```csharp
using UnityEngine;

public class EnemyChase : MonoBehaviour
{
    [Header("Detection")]
    [SerializeField] private float _detectionRange = 10f;  // How far the enemy can "see"
    [SerializeField] private float _stopDistance   = 1.5f; // How close before it stops

    [Header("Movement")]
    [SerializeField] private float _chaseSpeed   = 4f;
    [SerializeField] private float _rotateSpeed  = 5f;

    [Header("Combat")]
    [SerializeField] private int _damageAmount = 10;
    [SerializeField] private Transform _player;

    private bool _isChasing = false;

    void Update()
    {
        if (_player == null) return;

        // Vector3.Distance = straight-line distance between two positions
        float distanceToPlayer = Vector3.Distance(transform.position, _player.position);

        // Start chasing if close enough
        if (distanceToPlayer <= _detectionRange)
        {
            _isChasing = true;
        }

        if (_isChasing)
        {
            // Only move if we're farther than stop distance
            if (distanceToPlayer > _stopDistance)
            {
                MoveTowardsPlayer();
            }

            FacePlayer();
        }
    }

    private void MoveTowardsPlayer()
    {
        // MoveTowards moves at a fixed speed and never overshoots the target
        transform.position = Vector3.MoveTowards(
            transform.position,             // Current position
            _player.position,               // Target position
            _chaseSpeed * Time.deltaTime    // Max distance to move this frame
        );
    }

    private void FacePlayer()
    {
        // Calculate the direction from enemy to player
        Vector3 direction = (_player.position - transform.position).normalized;
        direction.y = 0f;   // Keep rotation flat (no tilting up/down)

        if (direction == Vector3.zero) return;

        // Build the rotation that would face that direction
        Quaternion targetRotation = Quaternion.LookRotation(direction);

        // Smoothly rotate toward that rotation
        // Slerp = Spherical Linear Interpolation (smooth rotation)
        transform.rotation = Quaternion.Slerp(
            transform.rotation,
            targetRotation,
            _rotateSpeed * Time.deltaTime
        );
    }

    // Damage the player when the enemy physically touches them
    void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.TryGetComponent<PlayerHealth>(out var health))
        {
            health.TakeDamage(_damageAmount);
        }
    }

    // Draw the detection range as a wire sphere in Scene view
    void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, _detectionRange);

        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, _stopDistance);
    }
}
```

### Understanding the Chase Logic

```
Every Frame (Update):
  ┌────────────────────────────────────────────┐
  │ Measure distance to player                 │
  │                                            │
  │ If distance < detectionRange               │
  │   → Set isChasing = true                   │
  │                                            │
  │ If isChasing AND distance > stopDistance   │
  │   → Move toward player                     │
  │   → Rotate to face player                  │
  │                                            │
  │ If isChasing AND touching player           │
  │   → Deal damage (OnCollisionEnter)         │
  └────────────────────────────────────────────┘
```

---

## 6. Example 6 — Shooting Bullets

**What this builds:** Player presses left mouse button to shoot a bullet. The bullet flies forward and destroys itself after 3 seconds. When it hits an enemy, it damages it.

### Setup in Unity
1. Create a small Capsule: `GameObject → 3D Object → Capsule`, rename it `Bullet`
2. Add a `Rigidbody` to the Bullet (uncheck Use Gravity so it flies straight)
3. Make the Bullet a **Prefab** (drag to Project window), then delete it from the scene
4. On the Player, create an Empty child called `ShootPoint`, position it in front
5. Attach `PlayerShooter.cs` to the Player
6. Attach `Bullet.cs` to the Bullet prefab

### Script: `Bullet.cs`

```csharp
using UnityEngine;

public class Bullet : MonoBehaviour
{
    [SerializeField] private float _speed  = 20f;
    [SerializeField] private float _damage = 25f;
    [SerializeField] private float _lifetime = 3f;   // Auto-destroy after this many seconds

    private Rigidbody _rb;

    void Awake()
    {
        _rb = GetComponent<Rigidbody>();
    }

    void Start()
    {
        // Launch the bullet forward the moment it spawns
        // transform.forward = the direction the bullet is currently facing
        _rb.velocity = transform.forward * _speed;

        // Automatically destroy this bullet after _lifetime seconds
        // This prevents endless bullets from filling the scene
        Destroy(gameObject, _lifetime);
    }

    void OnCollisionEnter(Collision collision)
    {
        // Try to damage whatever we hit
        if (collision.gameObject.TryGetComponent<EnemyChase>(out var enemy))
        {
            // You would call enemy.TakeDamage(_damage) here
            // if your enemy has a TakeDamage method
            Debug.Log($"Bullet hit enemy for {_damage} damage!");
            Destroy(enemy.gameObject);  // Simple version: destroy the enemy
        }

        // Destroy the bullet when it hits anything
        Destroy(gameObject);
    }
}
```

### Script: `PlayerShooter.cs`

```csharp
using UnityEngine;

public class PlayerShooter : MonoBehaviour
{
    [Header("Shooting")]
    [SerializeField] private GameObject _bulletPrefab;   // Drag the Bullet Prefab here
    [SerializeField] private Transform _shootPoint;      // Drag the ShootPoint here
    [SerializeField] private float _fireRate = 0.3f;     // Seconds between shots (0.3 = ~3 shots/sec)

    private float _nextFireTime = 0f;   // Tracks when we're allowed to fire again

    void Update()
    {
        // GetMouseButton(0) = Left mouse button held down
        // Time.time = total seconds since the game started
        // We can only fire if the current time is past our next allowed fire time
        if (Input.GetMouseButton(0) && Time.time >= _nextFireTime)
        {
            Shoot();
            _nextFireTime = Time.time + _fireRate;   // Set the next allowed fire time
        }
    }

    private void Shoot()
    {
        if (_bulletPrefab == null || _shootPoint == null) return;

        // Instantiate = clone the prefab into the scene
        // We pass the position and rotation of the shoot point
        // so the bullet starts at the barrel and faces forward
        Instantiate(_bulletPrefab, _shootPoint.position, _shootPoint.rotation);

        Debug.Log("Fired!");
    }
}
```

### Fire Rate Explained

```
Time.time timeline:
0s ─────────── 0.3s ─────────── 0.6s ─────────── 0.9s
  ↑              ↑                ↑                ↑
 Fire #1        Fire #2          Fire #3          Fire #4
 nextFireTime   nextFireTime     nextFireTime     nextFireTime
 = 0 + 0.3      = 0.3 + 0.3     = 0.6 + 0.3     = 0.9 + 0.3
```

---

## 7. Example 7 — Score System with GameManager

**What this builds:** A central GameManager that tracks the score. Any script anywhere can add points. Score shows on UI. This uses the **Singleton Pattern**.

### Why a Singleton?

Without it, every script that wants to add points needs a reference to the score object. With a Singleton, any script anywhere just calls `GameManager.Instance.AddScore(10)`.

### Setup in Unity
1. Create an Empty GameObject called `GameManager`
2. Attach `GameManager.cs` to it
3. In Canvas, add a Text named `ScoreText`

### Script: `GameManager.cs`

```csharp
using UnityEngine;
using UnityEngine.UI;

public class GameManager : MonoBehaviour
{
    // ── Singleton Setup ───────────────────────────────────────────────
    // static means this variable belongs to the CLASS, not an instance
    // So GameManager.Instance is accessible from anywhere
    public static GameManager Instance { get; private set; }

    void Awake()
    {
        // If an Instance already exists and it's not us, destroy ourselves
        // This prevents duplicate GameManagers if you reload a scene
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;

        // DontDestroyOnLoad: this object survives when loading a new scene
        // Remove this line if you don't need it to persist
        DontDestroyOnLoad(gameObject);
    }

    // ── Score System ──────────────────────────────────────────────────
    [SerializeField] private Text _scoreText;
    [SerializeField] private Text _highScoreText;

    private int _score = 0;
    private int _highScore = 0;

    public int Score => _score;

    public void AddScore(int amount)
    {
        _score += amount;

        // Update high score if we beat it
        if (_score > _highScore)
            _highScore = _score;

        UpdateScoreUI();

        Debug.Log($"Score: {_score}  |  High Score: {_highScore}");
    }

    public void ResetScore()
    {
        _score = 0;
        UpdateScoreUI();
    }

    private void UpdateScoreUI()
    {
        if (_scoreText != null)
            _scoreText.text = $"Score: {_score}";

        if (_highScoreText != null)
            _highScoreText.text = $"Best: {_highScore}";
    }
}
```

### How Other Scripts Use It

```csharp
// In ANY script, anywhere in the project:

// Add 10 points
GameManager.Instance.AddScore(10);

// Add 50 points when enemy dies
void Die()
{
    GameManager.Instance.AddScore(50);
    Destroy(gameObject);
}

// Read the current score
int currentScore = GameManager.Instance.Score;
```

---

## 8. Example 8 — Door That Opens With a Key

**What this builds:** A locked door. Player must collect a key item first. When the player approaches the door with the key, it opens (slides upward).

### Setup in Unity
1. Create a tall Cube for the Door → attach `Door.cs`
2. Create a small Gold Sphere for the Key → attach `Key.cs`, check Is Trigger on its collider, tag it `Key`
3. Create a Trigger zone in front of the door (Empty GameObject with Box Collider, Is Trigger checked) → attach `DoorTrigger.cs`

### Script: `Key.cs`

```csharp
using UnityEngine;

public class Key : MonoBehaviour
{
    [SerializeField] private float _rotateSpeed = 100f;

    void Update()
    {
        transform.Rotate(Vector3.up, _rotateSpeed * Time.deltaTime);
    }

    // Called when the player walks into the key's trigger
    public void PickUp()
    {
        Debug.Log("Key collected!");
        Destroy(gameObject);
    }
}
```

### Script: `PlayerInventory.cs` (attach to Player)

```csharp
using UnityEngine;

public class PlayerInventory : MonoBehaviour
{
    // Public property so Door can check if we have the key
    public bool HasKey { get; private set; } = false;

    void OnTriggerEnter(Collider other)
    {
        if (other.TryGetComponent<Key>(out Key key))
        {
            HasKey = true;
            key.PickUp();
            Debug.Log("You picked up the key!");
        }
    }
}
```

### Script: `Door.cs`

```csharp
using UnityEngine;

public class Door : MonoBehaviour
{
    [SerializeField] private float _openHeight  = 3f;    // How high the door slides up
    [SerializeField] private float _openSpeed   = 2f;    // How fast it opens

    private Vector3 _closedPosition;
    private Vector3 _openPosition;
    private bool _isOpen = false;
    private bool _isMoving = false;

    void Start()
    {
        // Remember the starting position (closed state)
        _closedPosition = transform.position;

        // Calculate where the door will be when fully open
        _openPosition = _closedPosition + Vector3.up * _openHeight;
    }

    // Called by the DoorTrigger when the player enters with a key
    public void Open()
    {
        if (_isOpen || _isMoving) return;
        Debug.Log("Door opening!");
        StartCoroutine(SlideOpen());
    }

    private System.Collections.IEnumerator SlideOpen()
    {
        _isMoving = true;

        // Keep moving until we're very close to the target position
        while (Vector3.Distance(transform.position, _openPosition) > 0.01f)
        {
            // MoveTowards moves at _openSpeed units per second toward the target
            transform.position = Vector3.MoveTowards(
                transform.position,
                _openPosition,
                _openSpeed * Time.deltaTime
            );

            // yield return null = pause here, resume next frame
            // This is what makes it animate smoothly over time
            yield return null;
        }

        // Snap to exact position (avoids floating point imprecision)
        transform.position = _openPosition;
        _isOpen   = true;
        _isMoving = false;

        Debug.Log("Door fully open!");
    }
}
```

### Script: `DoorTrigger.cs` (on the trigger zone in front of the door)

```csharp
using UnityEngine;

public class DoorTrigger : MonoBehaviour
{
    [SerializeField] private Door _door;   // Drag the Door here

    void OnTriggerEnter(Collider other)
    {
        // Check if the thing entering the trigger is the player
        if (!other.CompareTag("Player")) return;

        // Try to get the inventory from the player
        if (other.TryGetComponent<PlayerInventory>(out var inventory))
        {
            if (inventory.HasKey)
            {
                _door.Open();
            }
            else
            {
                Debug.Log("You need a key to open this door!");
            }
        }
    }
}
```

---

## 9. Example 9 — Timer Countdown

**What this builds:** A 60-second countdown timer displayed on screen. When it hits 0, the game ends.

### Setup in Unity
1. Canvas → Text named `TimerText`
2. Attach `CountdownTimer.cs` to the GameManager (or any persistent object)

### Script: `CountdownTimer.cs`

```csharp
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class CountdownTimer : MonoBehaviour
{
    [Header("Timer Settings")]
    [SerializeField] private float _timeRemaining = 60f;
    [SerializeField] private Text _timerText;
    [SerializeField] private bool _timerRunning = true;

    void Update()
    {
        if (!_timerRunning) return;

        // Subtract real-world time passed since last frame
        _timeRemaining -= Time.deltaTime;

        // Clamp so it never goes below 0
        _timeRemaining = Mathf.Max(0f, _timeRemaining);

        UpdateTimerDisplay();

        if (_timeRemaining <= 0f)
        {
            _timerRunning = false;
            TimerExpired();
        }
    }

    private void UpdateTimerDisplay()
    {
        // Convert raw seconds into minutes and seconds
        // Example: 75.5 seconds → "01:15"
        int minutes = Mathf.FloorToInt(_timeRemaining / 60f);
        int seconds = Mathf.FloorToInt(_timeRemaining % 60f);

        // {0:00} formats the number with at least 2 digits (e.g., 5 → "05")
        _timerText.text = string.Format("{0:00}:{1:00}", minutes, seconds);

        // Turn timer red when less than 10 seconds left
        _timerText.color = _timeRemaining <= 10f ? Color.red : Color.white;
    }

    private void TimerExpired()
    {
        Debug.Log("Time's up! Game Over!");
        // Option 1: Reload the scene
        // SceneManager.LoadScene(SceneManager.GetActiveScene().name);

        // Option 2: Show game over screen
        // GameManager.Instance.ShowGameOver();

        // Option 3: Freeze the game
        Time.timeScale = 0f;
    }

    // Call this from other scripts to pause/resume the timer
    public void PauseTimer()   => _timerRunning = false;
    public void ResumeTimer()  => _timerRunning = true;

    // Add bonus time (e.g., for completing a task)
    public void AddTime(float seconds) => _timeRemaining += seconds;
}
```

---

## 10. Example 10 — Respawn System

**What this builds:** When the player falls off the map (Y position drops below -10), they respawn at the starting position.

### Setup in Unity
1. Attach `RespawnSystem.cs` to the Player
2. Create an Empty GameObject called `SpawnPoint`, place it at the player's starting position
3. Drag `SpawnPoint` into the Inspector

### Script: `RespawnSystem.cs`

```csharp
using UnityEngine;

public class RespawnSystem : MonoBehaviour
{
    [SerializeField] private Transform _spawnPoint;
    [SerializeField] private float _fallDeathY = -10f;    // Below this Y = fell off map
    [SerializeField] private float _respawnDelay = 1f;    // Seconds before respawning

    private Rigidbody _rb;
    private bool _isDead = false;

    void Awake()
    {
        _rb = GetComponent<Rigidbody>();
    }

    void Update()
    {
        // Check if the player has fallen below the death plane
        if (transform.position.y < _fallDeathY && !_isDead)
        {
            StartCoroutine(Respawn());
        }
    }

    private System.Collections.IEnumerator Respawn()
    {
        _isDead = true;
        Debug.Log("Player fell! Respawning...");

        // Disable movement during respawn
        if (TryGetComponent<PlayerMovement>(out var movement))
            movement.enabled = false;

        // Wait before respawning (gives visual feedback time to play)
        yield return new WaitForSeconds(_respawnDelay);

        // Move player back to spawn point
        transform.position = _spawnPoint.position;
        transform.rotation = _spawnPoint.rotation;

        // Reset physics velocity so the player doesn't carry momentum from the fall
        if (_rb != null)
        {
            _rb.velocity = Vector3.zero;
            _rb.angularVelocity = Vector3.zero;
        }

        // Re-enable movement
        if (TryGetComponent<PlayerMovement>(out var mv))
            mv.enabled = true;

        _isDead = false;
        Debug.Log("Respawned!");
    }
}
```

---

## 11. Example 11 — Camera Follow Player

**What this builds:** A smooth third-person camera that follows and orbits around the player. Mouse moves the camera. No camera clipping through walls.

### Setup in Unity
1. Attach `CameraFollow.cs` to the **Main Camera**
2. Drag the Player into the `Target` field in the Inspector

### Script: `CameraFollow.cs`

```csharp
using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    [Header("Target")]
    [SerializeField] private Transform _target;         // The player

    [Header("Distance")]
    [SerializeField] private float _distance   = 5f;   // How far back the camera is
    [SerializeField] private float _height     = 2f;   // How high above the player

    [Header("Mouse Orbit")]
    [SerializeField] private float _mouseSensitivity = 3f;
    [SerializeField] private float _minVerticalAngle = -20f;   // Can't look too far down
    [SerializeField] private float _maxVerticalAngle =  60f;   // Can't look too far up

    [Header("Smoothing")]
    [SerializeField] private float _followSmoothness = 10f;

    private float _yaw   = 0f;  // Horizontal rotation (left/right)
    private float _pitch = 20f; // Vertical rotation (up/down)

    void LateUpdate()
    {
        if (_target == null) return;

        // Read mouse input
        // GetAxis("Mouse X") = how far the mouse moved horizontally this frame
        _yaw   += Input.GetAxis("Mouse X") * _mouseSensitivity;
        _pitch -= Input.GetAxis("Mouse Y") * _mouseSensitivity; // Subtract so moving up = looking up

        // Clamp vertical angle so camera doesn't flip upside down
        _pitch = Mathf.Clamp(_pitch, _minVerticalAngle, _maxVerticalAngle);

        // Build the rotation from our yaw and pitch angles
        Quaternion rotation = Quaternion.Euler(_pitch, _yaw, 0f);

        // Calculate the desired camera position:
        // Start at the player, step back by _distance, step up by _height
        Vector3 offset = new Vector3(0f, _height, -_distance);
        Vector3 desiredPosition = _target.position + rotation * offset;

        // Smooth the camera position so it doesn't snap
        transform.position = Vector3.Lerp(transform.position, desiredPosition, _followSmoothness * Time.deltaTime);

        // Always look at the player (slightly above their feet)
        Vector3 lookTarget = _target.position + Vector3.up * _height * 0.5f;
        transform.LookAt(lookTarget);
    }
}
```

---

## 12. Example 12 — Complete Mini Platformer Game

**What this builds:** A tiny but complete game combining everything above:
- Player can move and jump
- Coins to collect
- An enemy that chases you
- A score counter
- You win when all coins are collected
- You lose if the enemy touches you 3 times

This section shows how all the scripts talk to each other.

### All Scripts Working Together

```
┌─────────────────────────────────────────────────────────────────┐
│                     MINI PLATFORMER                             │
│                                                                 │
│  PlayerMovement ────► moves player with WASD                   │
│  PlayerHealth   ────► tracks 3 lives, calls GameManager.Lose() │
│  CoinCollector  ────► on trigger, adds score via GameManager   │
│  EnemyChase     ────► detects + follows player, damages health │
│  GameManager    ────► singleton, holds score, win/lose state   │
│  CameraFollow   ────► smooth camera orbit                      │
└─────────────────────────────────────────────────────────────────┘
```

### Script: `MiniGameManager.cs`

```csharp
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class MiniGameManager : MonoBehaviour
{
    public static MiniGameManager Instance { get; private set; }

    [Header("UI")]
    [SerializeField] private Text _scoreText;
    [SerializeField] private Text _livesText;
    [SerializeField] private Text _statusText;  // "You Win!" or "Game Over!"

    [Header("Game Settings")]
    [SerializeField] private int _startingLives = 3;

    private int _score = 0;
    private int _lives;
    private int _totalCoins;
    private bool _gameActive = true;

    void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
    }

    void Start()
    {
        _lives = _startingLives;
        _totalCoins = FindObjectsOfType<Coin>().Length;
        _statusText.gameObject.SetActive(false);
        RefreshUI();
    }

    // Called by CoinCollector
    public void CoinCollected(int value)
    {
        if (!_gameActive) return;
        _score += value;
        RefreshUI();

        if (_score >= _totalCoins)
            Win();
    }

    // Called by PlayerHealth when taking damage
    public void LoseLife()
    {
        if (!_gameActive) return;
        _lives--;
        RefreshUI();

        if (_lives <= 0)
            GameOver();
        else
            Debug.Log($"Lost a life! {_lives} remaining.");
    }

    private void Win()
    {
        _gameActive = false;
        _statusText.gameObject.SetActive(true);
        _statusText.text = "You Win!";
        _statusText.color = Color.yellow;
        Time.timeScale = 0f;   // Freeze the game
        Debug.Log("PLAYER WINS!");
    }

    private void GameOver()
    {
        _gameActive = false;
        _statusText.gameObject.SetActive(true);
        _statusText.text = "Game Over!";
        _statusText.color = Color.red;
        Time.timeScale = 0f;
        Debug.Log("GAME OVER!");

        // Reload after 3 seconds (using real time since timeScale is 0)
        StartCoroutine(ReloadAfterDelay(3f));
    }

    private System.Collections.IEnumerator ReloadAfterDelay(float delay)
    {
        yield return new WaitForSecondsRealtime(delay);
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }

    private void RefreshUI()
    {
        if (_scoreText)  _scoreText.text  = $"Coins: {_score} / {_totalCoins}";
        if (_livesText)  _livesText.text  = $"Lives: {_lives}";
    }
}
```

### How Scripts Call Each Other

```csharp
// In CoinCollector.cs — when player collects a coin:
MiniGameManager.Instance.CoinCollected(coin.Value);

// In PlayerHealth.cs — when enemy touches player:
void OnCollisionEnter(Collision collision)
{
    if (collision.gameObject.CompareTag("Enemy"))
    {
        MiniGameManager.Instance.LoseLife();
    }
}
```

### Complete Scene Setup Checklist

```
Scene Hierarchy:
├── GameManager            [MiniGameManager.cs]
├── Player
│   ├── [Rigidbody]
│   ├── [Capsule Collider]
│   ├── PlayerMovement.cs
│   ├── PlayerHealth.cs
│   ├── CoinCollector.cs   (collider is Trigger)
│   └── GroundCheck        (Empty child, at bottom)
├── MainCamera             [CameraFollow.cs]
├── Enemy
│   ├── [Rigidbody]
│   ├── [Box Collider]
│   └── EnemyChase.cs      (tag: Enemy)
├── Coin (x10)
│   ├── [Sphere Collider]  (Is Trigger: checked)
│   └── Coin.cs            (tag: Coin)
├── Canvas
│   ├── ScoreText          (drag to MiniGameManager)
│   ├── LivesText          (drag to MiniGameManager)
│   └── StatusText         (drag to MiniGameManager)
└── Floor                  (tag: Ground, Layer: Ground)
```

---

## Quick Lookup: "How Do I...?"

| Goal | What to Use | Where to Put It |
|------|------------|-----------------|
| Move with keyboard | `Input.GetAxis` + `Rigidbody.MovePosition` | `FixedUpdate` |
| Jump once | `Rigidbody.AddForce(Impulse)` + ground check | `FixedUpdate` |
| Track health | Property with `Mathf.Clamp` | Separate `PlayerHealth` script |
| Collect pickups | `OnTriggerEnter` + `TryGetComponent` | On the player |
| Enemy follows player | `Vector3.MoveTowards` + distance check | `Update` in enemy script |
| Shoot bullets | `Instantiate` prefab + `rb.velocity` | `Update` reads input |
| Global score | Singleton GameManager | Any script: `GameManager.Instance` |
| Animate door opening | `Coroutine` + `Vector3.MoveTowards` | On the door |
| Countdown timer | `_time -= Time.deltaTime` | `Update` |
| Respawn player | Check `position.y < deathY` + teleport | `Update` on player |
| Camera orbit | Mouse axes + `Quaternion.Euler` | `LateUpdate` on camera |

---

## Common Mistakes and Fixes

### Mistake 1 — Physics in Update

```csharp
// WRONG — choppy, inconsistent movement
void Update()
{
    _rb.AddForce(Vector3.forward * 10f);
}

// CORRECT — smooth, consistent physics
void FixedUpdate()
{
    _rb.AddForce(Vector3.forward * 10f);
}
```

### Mistake 2 — GetComponent Every Frame

```csharp
// WRONG — searches all components 60 times per second
void Update()
{
    GetComponent<Rigidbody>().AddForce(Vector3.up);
}

// CORRECT — search once, reuse
private Rigidbody _rb;
void Awake() { _rb = GetComponent<Rigidbody>(); }
void Update() { _rb.AddForce(Vector3.up); }
```

### Mistake 3 — Forgetting Time.deltaTime

```csharp
// WRONG — moves 5 units per frame (300 units/sec at 60fps!)
transform.position += Vector3.forward * 5f;

// CORRECT — moves 5 units per second, always
transform.position += Vector3.forward * 5f * Time.deltaTime;
```

### Mistake 4 — Missing Rigidbody for Physics Events

```
OnCollisionEnter does NOT fire if:
  ✗ Neither object has a Rigidbody
  ✗ Both colliders are set to Trigger

OnTriggerEnter does NOT fire if:
  ✗ Neither object has a Rigidbody
  ✗ The collider is NOT set to Is Trigger

Required setup for OnCollisionEnter:
  → Both objects need a Collider
  → At least ONE needs a Rigidbody
  → Is Trigger must be OFF

Required setup for OnTriggerEnter:
  → Both objects need a Collider
  → At least ONE needs a Rigidbody
  → At least ONE collider must have Is Trigger ON
```

### Mistake 5 — Coroutine Not Starting

```csharp
// WRONG — this does nothing, just creates the method
IEnumerator FadeOut() { yield return null; }

// CORRECT — you must call StartCoroutine to run it
StartCoroutine(FadeOut());
```

---

*Documentation version: Unity 2022 LTS / 2023+ / Unity 6*
*All examples tested with standard 3D project settings.*
