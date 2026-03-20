using UnityEngine;
using IsleTrial.Boat;
using IsleTrial.Player;
using IsleTrial.Data;

namespace IsleTrial.World
{
    /// <summary>
    /// Dock repair station. Player interacts to repair boat durability.
    /// Can cost items (e.g. Wood Planks) or be free.
    /// Attach to a dock/pier interact zone with a Trigger Collider.
    /// </summary>
    public class BoatRepairStation : MonoBehaviour, IInteractable
    {
        [Header("Repair")]
        [SerializeField] private float _repairAmount = 50f;
        [SerializeField] private bool _fullRepair = false;

        [Header("Cost (optional)")]
        [SerializeField] private bool _hasCost = false;
        [SerializeField] private ItemData _costItem;
        [SerializeField] private int _costAmount = 2;

        [Header("Cooldown")]
        [SerializeField] private float _cooldown = 30f;

        [Header("VFX")]
        [SerializeField] private ParticleSystem _repairVFX;
        [SerializeField] private AudioClip _repairSFX;
        [SerializeField] private AudioSource _audioSource;

        [Header("Indicator")]
        [SerializeField] private GameObject _interactIndicator;

        private float _cooldownTimer;
        private bool _onCooldown;

        void Update()
        {
            if (!_onCooldown) return;
            _cooldownTimer -= Time.deltaTime;
            if (_cooldownTimer <= 0f)
            {
                _onCooldown = false;
                if (_interactIndicator != null) _interactIndicator.SetActive(true);
            }
        }

        // ── IInteractable ─────────────────────────────────────

        public void Interact(object interactor)
        {
            if (_onCooldown)
            {
                Debug.Log($"[RepairStation] Cooldown: {_cooldownTimer:F1}s remaining.");
                return;
            }

            if (interactor is not Component comp) return;

            var boatStats = FindObjectOfType<BoatStats>();
            if (boatStats == null)
            {
                Debug.LogWarning("[RepairStation] No BoatStats found in scene.");
                return;
            }

            if (_hasCost && _costItem != null)
            {
                var inventory = comp.GetComponent<PlayerInventory>();
                if (inventory == null || inventory.CountItem(_costItem.ItemID) < _costAmount)
                {
                    Debug.Log($"[RepairStation] Need {_costAmount}x {_costItem.ItemName} to repair.");
                    return;
                }
                for (int i = 0; i < _costAmount; i++)
                    inventory.RemoveItem(_costItem);
            }

            PerformRepair(boatStats);
        }

        // ── Repair Logic ──────────────────────────────────────

        private void PerformRepair(BoatStats boatStats)
        {
            if (_fullRepair)
                boatStats.FullRepair();
            else
                boatStats.Repair(_repairAmount);

            if (_repairVFX != null) _repairVFX.Play();
            if (_audioSource != null && _repairSFX != null) _audioSource.PlayOneShot(_repairSFX);

            Debug.Log($"[RepairStation] Boat repaired. Durability: {boatStats.CurrentDurability}/{boatStats.MaxDurability}");

            _onCooldown = true;
            _cooldownTimer = _cooldown;
            if (_interactIndicator != null) _interactIndicator.SetActive(false);
        }
    }
}
