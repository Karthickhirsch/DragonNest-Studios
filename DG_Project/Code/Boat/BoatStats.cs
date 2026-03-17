using UnityEngine;
using IsleTrial.Core;

namespace IsleTrial.Boat
{
    /// <summary>
    /// Stores the boat's stats and durability.
    /// Attach to the Boat GameObject alongside BoatController.
    /// </summary>
    public class BoatStats : MonoBehaviour
    {
        [Header("Speed")]
        [SerializeField] private float _baseMaxSpeed = 8f;
        [SerializeField] private float _boostSpeed = 16f;

        [Header("Boost")]
        [SerializeField] private int _maxBoostCharges = 3;
        [SerializeField] private float _boostDuration = 1.5f;
        [SerializeField] private float _boostRechargeCooldown = 6f;

        [Header("Durability")]
        [SerializeField] private float _maxDurability = 100f;

        [Header("Harpoon")]
        [SerializeField] private int _maxHarpoonShots = 3;
        [SerializeField] private float _harpoonReloadTime = 2f;

        // ── Public Properties ─────────────────────────────────
        public float MaxSpeed => _baseMaxSpeed;
        public float BoostSpeed => _boostSpeed;
        public float BoostDuration => _boostDuration;
        public int MaxBoostCharges => _maxBoostCharges;
        public int CurrentBoostCharges { get; private set; }
        public float CurrentDurability { get; private set; }
        public float MaxDurability => _maxDurability;
        public int CurrentHarpoonShots { get; private set; }
        public bool CanHarpoon => CurrentHarpoonShots > 0;

        private float _boostRechargeTimer;
        private float _harpoonReloadTimer;

        void Awake()
        {
            CurrentBoostCharges = _maxBoostCharges;
            CurrentDurability = _maxDurability;
            CurrentHarpoonShots = _maxHarpoonShots;
        }

        void Update()
        {
            HandleBoostRecharge();
            HandleHarpoonReload();
        }

        // ── Boost ─────────────────────────────────────────────

        public bool ConsumeBoost()
        {
            if (CurrentBoostCharges <= 0) return false;
            CurrentBoostCharges--;
            _boostRechargeTimer = _boostRechargeCooldown;
            return true;
        }

        private void HandleBoostRecharge()
        {
            if (CurrentBoostCharges >= _maxBoostCharges) return;
            _boostRechargeTimer -= Time.deltaTime;
            if (_boostRechargeTimer <= 0)
            {
                CurrentBoostCharges++;
                _boostRechargeTimer = _boostRechargeCooldown;
            }
        }

        // ── Durability ────────────────────────────────────────

        public void TakeDamage(float amount)
        {
            CurrentDurability = Mathf.Max(0, CurrentDurability - amount);
            GameEvents.BoatDurabilityChanged(CurrentDurability, _maxDurability);
            if (CurrentDurability <= 0) OnBoatDestroyed();
        }

        public void Repair(float amount)
        {
            CurrentDurability = Mathf.Min(_maxDurability, CurrentDurability + amount);
            GameEvents.BoatDurabilityChanged(CurrentDurability, _maxDurability);
        }

        public void FullRepair()
        {
            CurrentDurability = _maxDurability;
            GameEvents.BoatDurabilityChanged(CurrentDurability, _maxDurability);
        }

        public void UpgradeDurability(float bonus)
        {
            _maxDurability += bonus;
            CurrentDurability += bonus;
            GameEvents.BoatDurabilityChanged(CurrentDurability, _maxDurability);
        }

        // ── Harpoon ───────────────────────────────────────────

        public bool ConsumeHarpoonShot()
        {
            if (!CanHarpoon) return false;
            CurrentHarpoonShots--;
            _harpoonReloadTimer = _harpoonReloadTime;
            return true;
        }

        private void HandleHarpoonReload()
        {
            if (CurrentHarpoonShots >= _maxHarpoonShots) return;
            _harpoonReloadTimer -= Time.deltaTime;
            if (_harpoonReloadTimer <= 0)
            {
                CurrentHarpoonShots = _maxHarpoonShots;
                _harpoonReloadTimer = 0;
            }
        }

        private void OnBoatDestroyed()
        {
            Debug.Log("[Boat] Boat destroyed!");
            // Trigger wash-ashore logic via GameManager
            GameManager.Instance.ChangeState(GameState.OnIsland);
        }
    }
}
