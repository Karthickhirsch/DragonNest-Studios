using UnityEngine;

namespace IsleTrial.Data
{
    /// <summary>
    /// ScriptableObject holding all stats and references for one enemy type.
    /// Create via: Right-click in Project → Create → IsleTrial → Enemy Data
    /// Assign to each enemy prefab's EnemyBase-derived component.
    /// </summary>
    [CreateAssetMenu(fileName = "New Enemy", menuName = "IsleTrial/Enemy Data")]
    public class EnemyData : ScriptableObject
    {
        [Header("Identity")]
        public string EnemyID;
        public string EnemyName;
        [TextArea] public string Description;

        [Header("Stats")]
        public int MaxHealth = 50;
        public float MoveSpeed = 3.5f;
        public float AttackDamage = 10f;
        public float DetectionRadius = 8f;
        public float AttackRadius = 2f;
        public float AttackCooldown = 1.5f;

        [Header("Drops")]
        public ItemData[] PossibleDrops;
        [Range(0f, 1f)] public float DropChance = 0.4f;

        [Header("Prefab & VFX")]
        public GameObject PrefabReference;
        public GameObject DeathVFX;
        public AudioClip DeathSound;
        public AudioClip HitSound;
    }
}
