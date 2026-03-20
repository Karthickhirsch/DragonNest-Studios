using System.Collections.Generic;
using UnityEngine;

namespace IsleTrial.Data
{
    /// <summary>
    /// ScriptableObject defining a weighted list of items that can be rolled.
    /// Used by ChestInteractable and enemy drop systems.
    /// Create: Right-click in Project → Create → IsleTrial → Loot Table
    /// </summary>
    [CreateAssetMenu(fileName = "LootTable_New", menuName = "IsleTrial/Loot Table")]
    public class LootTable : ScriptableObject
    {
        [System.Serializable]
        public class LootEntry
        {
            public ItemData Item;
            [Range(0.01f, 100f)]
            public float Weight = 10f;
            [Tooltip("0 = infinite, >0 = max times this item can be rolled from this table")]
            public int MaxRolls = 0;

            [System.NonSerialized] public int RollCount;
        }

        [Header("Entries")]
        [SerializeField] private List<LootEntry> _entries = new();

        [Header("Settings")]
        [SerializeField] private bool _allowDuplicates = true;
        [Tooltip("Chance (0-1) that Roll() returns null (empty roll / nothing drops)")]
        [SerializeField] [Range(0f, 1f)] private float _emptyChance = 0f;

        // ── Roll ──────────────────────────────────────────────

        /// <summary>Returns a random item weighted by each entry's Weight, or null on empty roll.</summary>
        public ItemData Roll()
        {
            if (Random.value < _emptyChance) return null;

            var eligible = GetEligibleEntries();
            if (eligible.Count == 0) return null;

            float totalWeight = 0f;
            foreach (var e in eligible) totalWeight += e.Weight;

            float roll = Random.Range(0f, totalWeight);
            float cumulative = 0f;

            foreach (var e in eligible)
            {
                cumulative += e.Weight;
                if (roll <= cumulative)
                {
                    e.RollCount++;
                    return e.Item;
                }
            }

            return eligible[eligible.Count - 1].Item;
        }

        /// <summary>Rolls multiple times and returns a list of items.</summary>
        public List<ItemData> RollMultiple(int count)
        {
            var results = new List<ItemData>();
            for (int i = 0; i < count; i++)
            {
                var item = Roll();
                if (item != null) results.Add(item);
            }
            return results;
        }

        /// <summary>Guarantees one item from the table regardless of empty chance.</summary>
        public ItemData RollGuaranteed()
        {
            float savedChance = _emptyChance;
            _emptyChance = 0f;
            var result = Roll();
            _emptyChance = savedChance;
            return result;
        }

        // ── Reset ─────────────────────────────────────────────

        /// <summary>Reset roll counts (call on new game or between dungeon runs).</summary>
        public void ResetRollCounts()
        {
            foreach (var e in _entries) e.RollCount = 0;
        }

        // ── Helpers ───────────────────────────────────────────

        private List<LootEntry> GetEligibleEntries()
        {
            var eligible = new List<LootEntry>();
            foreach (var e in _entries)
            {
                if (e.Item == null) continue;
                if (e.MaxRolls > 0 && e.RollCount >= e.MaxRolls) continue;
                eligible.Add(e);
            }
            return eligible;
        }

        // ── Editor Preview ────────────────────────────────────

        private void OnValidate()
        {
            if (_entries == null) return;
            float total = 0f;
            foreach (var e in _entries) if (e.Item != null) total += e.Weight;
            if (total > 0f)
            {
                // Normalize weights to 0-100 for display purposes only — don't overwrite
            }
        }
    }
}
