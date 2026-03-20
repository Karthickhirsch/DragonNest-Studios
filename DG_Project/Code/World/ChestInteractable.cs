using System.Collections;
using UnityEngine;
using IsleTrial.Data;
using IsleTrial.Player;

namespace IsleTrial.World
{
    /// <summary>
    /// Treasure chest that opens when the player interacts with it.
    /// Spawns loot from an assigned LootTable. Can only be opened once.
    /// Requires: Animator with "Open" trigger, Collider on chest.
    /// Attach to TreasureChest prefab.
    /// </summary>
    public class ChestInteractable : MonoBehaviour, IInteractable
    {
        [Header("Loot")]
        [SerializeField] private LootTable _lootTable;
        [SerializeField] private int _lootCount = 2;
        [SerializeField] private Transform _lootSpawnPoint;

        [Header("VFX")]
        [SerializeField] private ParticleSystem _openVFX;
        [SerializeField] private AudioClip _openSFX;

        [Header("Indicator")]
        [SerializeField] private GameObject _interactIndicator;

        private Animator _animator;
        private AudioSource _audioSource;
        private bool _opened;

        private static readonly int HashOpen = Animator.StringToHash("Open");

        void Awake()
        {
            _animator = GetComponent<Animator>();
            _audioSource = GetComponent<AudioSource>();
        }

        // ── IInteractable ─────────────────────────────────────

        public void Interact(object interactor)
        {
            if (_opened) return;
            _opened = true;

            if (_interactIndicator != null) _interactIndicator.SetActive(false);
            if (_animator != null) _animator.SetTrigger(HashOpen);
            if (_openVFX != null) _openVFX.Play();
            if (_audioSource != null && _openSFX != null) _audioSource.PlayOneShot(_openSFX);

            if (interactor is Component comp)
                StartCoroutine(SpawnLootRoutine(comp.GetComponent<PlayerInventory>()));
        }

        // ── Loot Spawning ─────────────────────────────────────

        private IEnumerator SpawnLootRoutine(PlayerInventory inventory)
        {
            yield return new WaitForSeconds(0.5f);   // Wait for lid to open

            if (_lootTable == null || inventory == null) yield break;

            Vector3 spawnPos = _lootSpawnPoint != null
                ? _lootSpawnPoint.position
                : transform.position + Vector3.up * 0.5f;

            for (int i = 0; i < _lootCount; i++)
            {
                ItemData item = _lootTable.Roll();
                if (item == null) continue;

                inventory.AddItem(item);
                Core.GameEvents.ItemPickedUp(item);
                Debug.Log($"[Chest] Gave item: {item.ItemName}");

                yield return new WaitForSeconds(0.1f);
            }
        }
    }
}
