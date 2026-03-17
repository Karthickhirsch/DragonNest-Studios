using UnityEngine;

namespace IsleTrial.Data
{
    /// <summary>
    /// ScriptableObject for one boss.
    /// Create via: Right-click → Create → IsleTrial → Boss Data
    /// Assign to each boss prefab's BossBase-derived component.
    /// </summary>
    [CreateAssetMenu(fileName = "New Boss", menuName = "IsleTrial/Boss Data")]
    public class BossData : ScriptableObject
    {
        [Header("Identity")]
        public string BossID;
        public string BossName;
        [TextArea(2, 5)] public string Lore;
        public Sprite Portrait;

        [Header("Stats")]
        public int MaxHealth = 600;
        public float Phase2HealthPercent = 0.6f;
        public float Phase3HealthPercent = 0.3f;

        [Header("Reward")]
        public AbilityData UnlockedAbility;
        public string CrystalType;           // "Fire", "Ice", etc.

        [Header("Arena")]
        public string ArenaSceneName;        // e.g. "BossFight_Ignar"

        [Header("Music")]
        public AudioClip BossTheme;
        public AudioClip VictoryStinger;
    }
}
