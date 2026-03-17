using UnityEngine;
using UnityEngine.UI;
using TMPro;
using IsleTrial.Core;
using IsleTrial.Data;

namespace IsleTrial.UI
{
    /// <summary>
    /// Manages all HUD elements: health, stamina, boat durability, ability icon.
    /// Attach to the HUD Canvas GameObject in your scene.
    /// Assign all UI element references in the Inspector.
    /// </summary>
    public class HUDManager : MonoBehaviour
    {
        [Header("Health")]
        [SerializeField] private Image _healthFill;
        [SerializeField] private TextMeshProUGUI _healthText;

        [Header("Stamina")]
        [SerializeField] private Image _staminaFill;
        [SerializeField] private CanvasGroup _staminaGroup;   // Fades out at full

        [Header("Boat Durability")]
        [SerializeField] private GameObject _boatDurabilityRoot;  // Entire panel
        [SerializeField] private Image _durabilityFill;
        [SerializeField] private TextMeshProUGUI _durabilityText;

        [Header("Ability")]
        [SerializeField] private Image _abilityIcon;
        [SerializeField] private Image _abilityCooldownFill;   // Radial fill
        [SerializeField] private TextMeshProUGUI _abilityNameText;

        [Header("Crystal Counter")]
        [SerializeField] private TextMeshProUGUI _crystalCountText;
        [SerializeField] private GameObject[] _crystalSlotIcons;  // 6 icons

        private int _crystalsCollected;

        void OnEnable()
        {
            GameEvents.OnPlayerHealthChanged += UpdateHealth;
            GameEvents.OnBoatDurabilityChanged += UpdateBoatDurability;
            GameEvents.OnCrystalCollected += UpdateCrystals;
            GameEvents.OnAbilityUnlocked += UpdateAbilityIcon;
            GameEvents.OnGameStateChanged += OnGameStateChanged;
        }

        void OnDisable()
        {
            GameEvents.OnPlayerHealthChanged -= UpdateHealth;
            GameEvents.OnBoatDurabilityChanged -= UpdateBoatDurability;
            GameEvents.OnCrystalCollected -= UpdateCrystals;
            GameEvents.OnAbilityUnlocked -= UpdateAbilityIcon;
            GameEvents.OnGameStateChanged -= OnGameStateChanged;
        }

        // ── Health ────────────────────────────────────────────

        private void UpdateHealth(int current, int max)
        {
            float ratio = max > 0 ? (float)current / max : 0f;
            if (_healthFill != null) _healthFill.fillAmount = ratio;
            if (_healthText != null) _healthText.text = $"{current}/{max}";
        }

        // ── Boat Durability ───────────────────────────────────

        private void UpdateBoatDurability(float current, float max)
        {
            if (_boatDurabilityRoot != null)
                _boatDurabilityRoot.SetActive(true);

            float ratio = max > 0 ? current / max : 0f;
            if (_durabilityFill != null) _durabilityFill.fillAmount = ratio;
            if (_durabilityText != null) _durabilityText.text = $"{Mathf.CeilToInt(current)}/{Mathf.CeilToInt(max)}";
        }

        // ── Crystals ──────────────────────────────────────────

        private void UpdateCrystals(int totalCount)
        {
            _crystalsCollected = totalCount;
            if (_crystalCountText != null) _crystalCountText.text = $"{totalCount}/6";

            for (int i = 0; i < _crystalSlotIcons.Length; i++)
                if (_crystalSlotIcons[i] != null)
                    _crystalSlotIcons[i].SetActive(i < totalCount);
        }

        // ── Ability ───────────────────────────────────────────

        private void UpdateAbilityIcon(AbilityData ability)
        {
            if (_abilityIcon != null) _abilityIcon.sprite = ability.Icon;
            if (_abilityNameText != null) _abilityNameText.text = ability.AbilityName;
        }

        // ── Stamina (called directly from PlayerStats) ────────

        public void UpdateStamina(float current, float max)
        {
            float ratio = max > 0 ? current / max : 0f;
            if (_staminaFill != null) _staminaFill.fillAmount = ratio;
            if (_staminaGroup != null)
                _staminaGroup.alpha = ratio >= 1f ? 0f : 1f;
        }

        // ── Cooldown (called from PlayerAbilityHandler each frame) ─

        public void UpdateAbilityCooldown(float progress)  // 0=on cooldown, 1=ready
        {
            if (_abilityCooldownFill != null)
                _abilityCooldownFill.fillAmount = progress;
        }

        // ── Game State ────────────────────────────────────────

        private void OnGameStateChanged(GameState from, GameState to)
        {
            bool sailing = to == GameState.Sailing;
            if (_boatDurabilityRoot != null) _boatDurabilityRoot.SetActive(sailing);
        }
    }
}
