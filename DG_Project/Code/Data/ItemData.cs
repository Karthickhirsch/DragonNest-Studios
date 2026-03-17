using UnityEngine;

namespace IsleTrial.Data
{
    public enum ItemType
    {
        HealthPotion,
        RepairKit,
        WaterFlask,
        AntidoteBerry,
        HintToken,
        IceShard,
        KeyItem,
        CraftMaterial,
        Collectible
    }

    /// <summary>
    /// ScriptableObject for one inventory item.
    /// Create via: Right-click → Create → IsleTrial → Item Data
    /// </summary>
    [CreateAssetMenu(fileName = "New Item", menuName = "IsleTrial/Item Data")]
    public class ItemData : ScriptableObject
    {
        [Header("Identity")]
        public string ItemID;
        public string ItemName;
        [TextArea(1, 3)] public string Description;
        public Sprite Icon;

        [Header("Type")]
        public ItemType ItemType;

        [Header("Effect")]
        [Tooltip("HP restored for potions, durability for repair kit, etc.")]
        public int EffectAmount;

        [Header("Stack")]
        public bool IsStackable = true;
        public int MaxStack = 5;

        [Header("Value")]
        public int CoinValue = 10;
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Lookup database for all items. Create one ItemDatabase asset
    /// and assign all ItemData assets to the _allItems list.
    /// Right-click → Create → IsleTrial → Item Database
    /// </summary>
    [CreateAssetMenu(fileName = "ItemDatabase", menuName = "IsleTrial/Item Database")]
    public class ItemDatabase : ScriptableObject
    {
        public ItemData[] AllItems;

        public ItemData GetByID(string id)
        {
            foreach (var item in AllItems)
                if (item.ItemID == id) return item;
            return null;
        }
    }
}
