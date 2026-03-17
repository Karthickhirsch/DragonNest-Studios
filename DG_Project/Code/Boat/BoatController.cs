using System.Collections;
using UnityEngine;
using IsleTrial.Player;

namespace IsleTrial.Boat
{
    /// <summary>
    /// Handles all boat movement, boost, anchor, harpoon, and lantern.
    /// Requires: Rigidbody, BoatStats, PlayerInputHandler.
    /// Attach all three to the Boat GameObject.
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    [RequireComponent(typeof(BoatStats))]
    public class BoatController : MonoBehaviour
    {
        [Header("Steering")]
        [SerializeField] private float _turnSpeed = 90f;       // degrees per second
        [SerializeField] private float _windInfluence = 0.3f;  // 0 = no wind, 1 = full wind

        [Header("Harpoon")]
        [SerializeField] private Transform _harpoonSpawnPoint;
        [SerializeField] private GameObject _harpoonProjectilePrefab;
        [SerializeField] private float _harpoonSpeed = 20f;

        [Header("Lantern")]
        [SerializeField] private Light _lanternLight;

        [Header("Wind (set by WeatherSystem)")]
        [SerializeField] private Vector3 _windDirection = Vector3.forward;
        [SerializeField] private float _windStrength = 2f;

        // ── Components ────────────────────────────────────────
        private Rigidbody _rb;
        private BoatStats _stats;
        private PlayerInputHandler _input;

        // ── State ─────────────────────────────────────────────
        private bool _anchored;
        private bool _isBoosting;
        private float _boostTimer;

        void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _stats = GetComponent<BoatStats>();
            _input = FindObjectOfType<PlayerInputHandler>();
        }

        void FixedUpdate()
        {
            if (_anchored) return;
            HandleSteering();
            HandleSpeed();
        }

        void Update()
        {
            HandleBoost();
            HandleAnchor();
            HandleHarpoon();
            HandleLantern();
        }

        // ── Steering ──────────────────────────────────────────

        private void HandleSteering()
        {
            float steerX = _input.SteerInput.x;
            if (Mathf.Abs(steerX) < 0.01f) return;
            transform.Rotate(Vector3.up, steerX * _turnSpeed * Time.fixedDeltaTime);
        }

        private void HandleSpeed()
        {
            float forwardInput = _input.SteerInput.y;
            float targetSpeed = _isBoosting ? _stats.BoostSpeed : _stats.MaxSpeed;

            // Wind influence
            float windDot = Vector3.Dot(transform.forward, _windDirection.normalized);
            float windBonus = windDot * _windStrength * _windInfluence;

            Vector3 force = transform.forward * (forwardInput * targetSpeed + windBonus);
            _rb.AddForce(force, ForceMode.Acceleration);

            // Clamp velocity
            if (_rb.velocity.magnitude > targetSpeed)
                _rb.velocity = _rb.velocity.normalized * targetSpeed;
        }

        // ── Boost ─────────────────────────────────────────────

        private void HandleBoost()
        {
            if (_input.BoostHeld && !_isBoosting && _stats.ConsumeBoost())
            {
                _isBoosting = true;
                _boostTimer = _stats.BoostDuration;
            }

            if (_isBoosting)
            {
                _boostTimer -= Time.deltaTime;
                if (_boostTimer <= 0) _isBoosting = false;
            }
        }

        // ── Anchor ────────────────────────────────────────────

        private void HandleAnchor()
        {
            if (!_input.AnchorPressed) return;
            _anchored = !_anchored;
            _rb.velocity = _anchored ? Vector3.zero : _rb.velocity;
            _rb.angularVelocity = Vector3.zero;
            Debug.Log(_anchored ? "[Boat] Anchored." : "[Boat] Anchor raised.");
        }

        // ── Harpoon ───────────────────────────────────────────

        private void HandleHarpoon()
        {
            if (!_input.HarpoonPressed || !_stats.CanHarpoon) return;
            if (!_stats.ConsumeHarpoonShot()) return;

            if (_harpoonProjectilePrefab != null && _harpoonSpawnPoint != null)
            {
                GameObject proj = Instantiate(_harpoonProjectilePrefab,
                    _harpoonSpawnPoint.position, _harpoonSpawnPoint.rotation);
                if (proj.TryGetComponent<Rigidbody>(out var projRb))
                    projRb.velocity = _harpoonSpawnPoint.forward * _harpoonSpeed;

                Destroy(proj, 5f);
            }
        }

        // ── Lantern ───────────────────────────────────────────

        private void HandleLantern()
        {
            if (!_input.LanternPressed) return;
            if (_lanternLight != null) _lanternLight.enabled = !_lanternLight.enabled;
        }

        // ── Wind (called by WeatherSystem) ────────────────────

        public void SetWind(Vector3 direction, float strength)
        {
            _windDirection = direction;
            _windStrength = strength;
        }

        public bool IsAnchored => _anchored;

        void OnCollisionEnter(Collision col)
        {
            float force = col.relativeVelocity.magnitude;
            if (force > 2f) _stats.TakeDamage(force * 2f);
        }
    }
}
