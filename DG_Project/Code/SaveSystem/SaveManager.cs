using System.IO;
using UnityEngine;
using IsleTrial.Core;
using IsleTrial.Player;
using IsleTrial.Boat;

namespace IsleTrial.SaveSystem
{
    /// <summary>
    /// Saves and loads game data to/from JSON on disk.
    /// Attach to the Bootstrap scene's persistent manager GameObject.
    /// </summary>
    public class SaveManager : MonoBehaviour
    {
        public static SaveManager Instance { get; private set; }

        private const string SAVE_FOLDER = "/saves/";
        private const string SAVE_EXTENSION = ".json";
        private const int MAX_SLOTS = 3;

        private string SavePath => Application.persistentDataPath + SAVE_FOLDER;

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Directory.CreateDirectory(SavePath);
        }

        void OnEnable()
        {
            GameEvents.OnBossDefeated += OnBossDefeated;
            GameEvents.OnIslandCompleted += OnIslandCompleted;
        }

        void OnDisable()
        {
            GameEvents.OnBossDefeated -= OnBossDefeated;
            GameEvents.OnIslandCompleted -= OnIslandCompleted;
        }

        // ── Auto Save Triggers ────────────────────────────────

        private void OnBossDefeated(Data.BossData boss) => AutoSave();
        private void OnIslandCompleted(Data.IslandData island) => AutoSave();

        private void AutoSave() => SaveGame(0); // Slot 0 = auto-save

        // ── Save ──────────────────────────────────────────────

        public void SaveGame(int slot)
        {
            GameSaveData data = CollectSaveData(slot);
            string json = JsonUtility.ToJson(data, prettyPrint: true);
            string path = GetSavePath(slot);
            File.WriteAllText(path, json);
            Debug.Log($"[SaveManager] Saved slot {slot} → {path}");
        }

        private GameSaveData CollectSaveData(int slot)
        {
            var data = new GameSaveData
            {
                SlotName = slot == 0 ? "AutoSave" : $"Slot {slot}",
                SaveTimestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm"),
            };

            // Player
            var player = FindObjectOfType<PlayerStats>();
            var playerCtrl = FindObjectOfType<PlayerController>();
            if (player != null)
            {
                data.PlayerHealth = player.CurrentHealth;
                data.PlayerMaxHealth = player.MaxHealth;
            }
            if (playerCtrl != null)
                data.PlayerPosition = new Vector3Data(playerCtrl.transform.position);

            // Inventory
            var inventory = FindObjectOfType<PlayerInventory>();
            if (inventory != null)
                data.InventoryItemIDs = inventory.GetItemIDList();

            // Boat
            var boat = FindObjectOfType<BoatStats>();
            var boatCtrl = FindObjectOfType<BoatController>();
            if (boat != null) data.BoatDurability = boat.CurrentDurability;
            if (boatCtrl != null)
                data.BoatPosition = new Vector3Data(boatCtrl.transform.position);

            return data;
        }

        // ── Load ──────────────────────────────────────────────

        public GameSaveData LoadGame(int slot)
        {
            string path = GetSavePath(slot);
            if (!File.Exists(path))
            {
                Debug.Log($"[SaveManager] No save found at slot {slot}.");
                return null;
            }
            string json = File.ReadAllText(path);
            return JsonUtility.FromJson<GameSaveData>(json);
        }

        public void ApplySaveData(GameSaveData data)
        {
            if (data == null) return;

            var player = FindObjectOfType<PlayerStats>();
            var playerCtrl = FindObjectOfType<PlayerController>();
            if (player != null) player.Heal(data.PlayerHealth - player.CurrentHealth);
            if (playerCtrl != null && data.PlayerPosition != null)
                playerCtrl.transform.position = data.PlayerPosition.ToVector3();

            var boat = FindObjectOfType<BoatController>();
            if (boat != null && data.BoatPosition != null)
                boat.transform.position = data.BoatPosition.ToVector3();

            Debug.Log("[SaveManager] Save data applied.");
        }

        // ── Utilities ─────────────────────────────────────────

        public bool SlotExists(int slot) => File.Exists(GetSavePath(slot));

        public void DeleteSlot(int slot)
        {
            string path = GetSavePath(slot);
            if (File.Exists(path)) File.Delete(path);
        }

        private string GetSavePath(int slot) => $"{SavePath}slot{slot}{SAVE_EXTENSION}";
    }
}
