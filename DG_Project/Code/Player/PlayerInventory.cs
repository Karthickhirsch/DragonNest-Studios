using System.Collections.Generic;
using UnityEngine;
using IsleTrial.Core;
using IsleTrial.Data;

namespace IsleTrial.Player
{
    /// <summary>
    /// Manages the player's items.
    /// Attach to the Player GameObject.
    /// </summary>
    public class PlayerInventory : MonoBehaviour
    {
        [Header("Settings")]
        [SerializeField] private int _maxSlots = 10;

        private readonly List<ItemData> _items = new();

        public IReadOnlyList<ItemData> Items => _items;
        public int SlotCount => _maxSlots;
        public int UsedSlots => _items.Count;
        public bool IsFull => _items.Count >= _maxSlots;

        // ── Add / Remove ──────────────────────────────────────

        public bool AddItem(ItemData item)
        {
            if (IsFull)
            {
                Debug.Log("[Inventory] Full — cannot add item.");
                return false;
            }
            _items.Add(item);
            GameEvents.ItemPickedUp(item);
            return true;
        }

        public bool RemoveItem(ItemData item)
        {
            return _items.Remove(item);
        }

        public bool RemoveItemByID(string itemID)
        {
            var item = _items.Find(i => i.ItemID == itemID);
            if (item == null) return false;
            return _items.Remove(item);
        }

        // ── Queries ───────────────────────────────────────────

        public bool HasItem(string itemID) => _items.Exists(i => i.ItemID == itemID);

        public ItemData GetItem(string itemID) => _items.Find(i => i.ItemID == itemID);

        public int CountItem(string itemID) => _items.FindAll(i => i.ItemID == itemID).Count;

        // ── Use Item ──────────────────────────────────────────

        public void UseItem(ItemData item, PlayerStats stats)
        {
            if (!_items.Contains(item)) return;

            switch (item.ItemType)
            {
                case ItemType.HealthPotion:
                    stats.Heal(item.EffectAmount);
                    break;
                case ItemType.AntidoteBerry:
                    // StatusEffectSystem.Instance.CurePoison();  (extend later)
                    break;
            }

            GameEvents.ItemUsed(item);
            RemoveItem(item);
        }

        // ── Save / Load Helpers ───────────────────────────────

        public List<string> GetItemIDList()
        {
            var ids = new List<string>();
            foreach (var item in _items) ids.Add(item.ItemID);
            return ids;
        }

        public void LoadFromIDList(List<string> ids, ItemDatabase database)
        {
            _items.Clear();
            foreach (var id in ids)
            {
                var item = database.GetByID(id);
                if (item != null) _items.Add(item);
            }
        }
    }
}
