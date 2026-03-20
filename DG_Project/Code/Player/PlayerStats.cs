using UnityEngine;
using IsleTrial.Core;

namespace IsleTrial.Player
{
    /// <summary>
    /// Stores and manages all player numeric stats.
    /// Attach to the Player GameObject alongside PlayerController.
    /// </summary>
    public class PlayerStats : MonoBehaviour
    {
        [Header("Health")]
        [SerializeField] private int _maxHealth = 100;
        [SerializeField] private float _regenDelay = 5f;       // seconds before regen starts
        [SerializeField] private float _regenRate = 3f;         // HP per second

        [Header("Movement")]
        [SerializeField] private float _moveSpeed = 5f;
        [SerializeField] private float _sprintMultiplier = 1.6f;
        [SerializeField] private float _dodgeSpeed = 10f;
        [SerializeField] private float _dodgeDuration = 0.25f;

        [Header("Combat")]
        [SerializeField] private float _attackDamage = 20f;
        [SerializeField] private float _chargedAttackMultiplier = 3f;
        [SerializeField] private int _invincibilityFrames = 8;

        [Header("Stamina")]
        [SerializeField] private float _maxStamina = 100f;
        [SerializeField] private float _staminaDrainPerDodge = 20f;
        [SerializeField] private float _staminaRegenRate = 15f;

        // ── Public Read Properties ────────────────────────────
        public int CurrentHealth { get; private set; }
        public int MaxHealth => _maxHealth;
        public float CurrentStamina { get; private set; }
        public float MaxStamina => _maxStamina;
        public float MoveSpeed => _moveSpeed;
        public float SprintMultiplier => _sprintMultiplier;
        public float DodgeSpeed => _dodgeSpeed;
        public float DodgeDuration => _dodgeDuration;
        public float AttackDamage => _attackDamage;
        public float ChargedAttackMultiplier => _chargedAttackMultiplier;
        public int InvincibilityFrames => _invincibilityFrames;
        public bool IsAlive => CurrentHealth > 0;

        private float _regenTimer;
        private bool _isInvincible;
        private int _iFrameCounter;

        void Awake()
        {
            CurrentHealth = _maxHealth;
            CurrentStamina = _maxStamina;
        }

        void Update()
        {
            HandleRegen();
            HandleIFrames();
            HandleStaminaRegen();
        }

        // ── Health ────────────────────────────────────────────

        public void TakeDamage(int amount)
        {
            if (_isInvincible || !IsAlive) return;

            CurrentHealth = Mathf.Max(0, CurrentHealth - amount);
            _regenTimer = 0f;
            _iFrameCounter = _invincibilityFrames;
            _isInvincible = true;

            GameEvents.PlayerHealthChanged(CurrentHealth, _maxHealth);

            if (CurrentHealth <= 0) GameEvents.PlayerDied();
        }

        public void Heal(int amount)
        {
            if (!IsAlive) return;
            CurrentHealth = Mathf.Min(_maxHealth, CurrentHealth + amount);
            GameEvents.PlayerHealthChanged(CurrentHealth, _maxHealth);
        }

        public void UpgradeMaxHealth(int bonus)
        {
            _maxHealth += bonus;
            CurrentHealth = Mathf.Min(CurrentHealth + bonus, _maxHealth);
            GameEvents.PlayerHealthChanged(CurrentHealth, _maxHealth);
        }

        // ── Stamina ───────────────────────────────────────────

        public bool UseStamina(float amount)
        {
            if (CurrentStamina < amount) return false;
            CurrentStamina -= amount;
            return true;
        }

        public bool CanDodge() => CurrentStamina >= _staminaDrainPerDodge;

        public void ConsumeDodgeStamina() => UseStamina(_staminaDrainPerDodge);

        // ── Speed Modifier (used by FrostSlug slow, etc.) ─────

        private float _speedMultiplier = 1f;
        public float SpeedMultiplier => _speedMultiplier;

        public void ApplySpeedModifier(float multiplier) => _speedMultiplier = Mathf.Clamp(multiplier, 0.1f, 2f);
        public void ResetSpeedModifier() => _speedMultiplier = 1f;

        // ── Private ───────────────────────────────────────────

        private void HandleRegen()
        {
            if (CurrentHealth >= _maxHealth) return;
            _regenTimer += Time.deltaTime;
            if (_regenTimer >= _regenDelay)
                Heal(Mathf.RoundToInt(_regenRate * Time.deltaTime));
        }

        private void HandleIFrames()
        {
            if (!_isInvincible) return;
            _iFrameCounter--;
            if (_iFrameCounter <= 0) _isInvincible = false;
        }

        private void HandleStaminaRegen()
        {
            if (CurrentStamina >= _maxStamina) return;
            CurrentStamina = Mathf.Min(_maxStamina, CurrentStamina + _staminaRegenRate * Time.deltaTime);
        }
    }
}
