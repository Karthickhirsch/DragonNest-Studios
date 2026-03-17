using UnityEngine;

namespace IsleTrial.Data
{
    public enum AbilityType
    {
        FireDash,
        IceShield,
        VineGrapple,
        SandVeil,
        LightningStrike
    }

    /// <summary>
    /// ScriptableObject for one player ability.
    /// Create via: Right-click → Create → IsleTrial → Ability Data
    /// Assign to BossData.UnlockedAbility on each boss.
    /// </summary>
    [CreateAssetMenu(fileName = "New Ability", menuName = "IsleTrial/Ability Data")]
    public class AbilityData : ScriptableObject
    {
        [Header("Identity")]
        public string AbilityID;
        public string AbilityName;
        [TextArea(1, 3)] public string Description;
        public Sprite Icon;

        [Header("Type")]
        public AbilityType Type;

        [Header("Stats")]
        public float Cooldown = 8f;
        public float Damage = 30f;
        public float Range = 5f;
        public float Duration = 3f;    // For timed effects like Sand Veil

        [Header("VFX & Audio")]
        public ParticleSystem ActivationVFXPrefab;
        public AudioClip ActivationSound;
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// ScriptableObject for a dialogue sequence.
    /// Create via: Right-click → Create → IsleTrial → Dialogue Sequence
    /// </summary>
    [CreateAssetMenu(fileName = "New Dialogue", menuName = "IsleTrial/Dialogue Sequence")]
    public class DialogueSequence : ScriptableObject
    {
        public DialogueLine[] Lines;
        public bool PauseGameDuringDialogue = true;
    }

    [System.Serializable]
    public class DialogueLine
    {
        public string SpeakerName;
        [TextArea(2, 6)] public string Text;
        public Sprite SpeakerPortrait;
        public AudioClip VoiceClip;
    }
}
