using System;
using System.Collections.Generic;
using UnityEngine;

namespace IsleTrial.SaveSystem
{
    [Serializable]
    public class Vector3Data
    {
        public float x, y, z;
        public Vector3Data(Vector3 v) { x = v.x; y = v.y; z = v.z; }
        public Vector3 ToVector3() => new Vector3(x, y, z);
    }

    [Serializable]
    public class PuzzleSaveData
    {
        public string PuzzleID;
        public bool IsSolved;
        public List<int> TileState;   // Stores puzzle-specific configuration
    }

    /// <summary>
    /// The complete serializable save state of the game.
    /// Converted to/from JSON by SaveManager.
    /// </summary>
    [Serializable]
    public class GameSaveData
    {
        // ── Meta ──────────────────────────────────────────────
        public string SlotName;
        public string SaveTimestamp;
        public int PlaytimeSeconds;

        // ── Player ────────────────────────────────────────────
        public int PlayerHealth;
        public int PlayerMaxHealth;
        public Vector3Data PlayerPosition;
        public List<string> UnlockedAbilityIDs = new();

        // ── Boat ──────────────────────────────────────────────
        public float BoatDurability;
        public Vector3Data BoatPosition;
        public List<string> BoatUpgradeIDs = new();

        // ── World ─────────────────────────────────────────────
        public List<string> DiscoveredIslandIDs = new();
        public List<string> CompletedIslandIDs = new();
        public List<string> DefeatedBossIDs = new();
        public int CrystalsCollected;

        // ── Puzzles ───────────────────────────────────────────
        public List<PuzzleSaveData> PuzzleStates = new();

        // ── Inventory ─────────────────────────────────────────
        public List<string> InventoryItemIDs = new();
        public int Coins;
    }
}
