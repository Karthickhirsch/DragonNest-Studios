using UnityEngine;

namespace IsleTrial.Data
{
    /// <summary>
    /// ScriptableObject for one island.
    /// Create via: Right-click → Create → IsleTrial → Island Data
    /// Assign to IslandProximityLoader on each island marker object.
    /// </summary>
    [CreateAssetMenu(fileName = "New Island", menuName = "IsleTrial/Island Data")]
    public class IslandData : ScriptableObject
    {
        [Header("Identity")]
        public string IslandID;
        public string IslandName;
        [TextArea(2, 4)] public string IslandDescription;

        [Header("Scenes")]
        public string SceneName;         // e.g. "Island_01_Ember"
        public string BossSceneName;     // e.g. "BossFight_Ignar"

        [Header("Map")]
        public Sprite MapIcon;
        public Color ThemeColor = Color.white;

        [Header("Boss")]
        public BossData AssociatedBoss;

        [Header("Unlock Requirements")]
        public string[] RequiredCompletedIslandIDs;   // leave empty for starter islands
    }
}
