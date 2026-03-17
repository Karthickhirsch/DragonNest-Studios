using System;
using IsleTrial.Data;

namespace IsleTrial.Core
{
    /// <summary>
    /// Central event bus. Subscribe from any script; avoids direct references between systems.
    /// Never attach to a GameObject — this is a static class.
    /// </summary>
    public static class GameEvents
    {
        // ── Game State ────────────────────────────────────────
        public static event Action<GameState, GameState> OnGameStateChanged;
        public static void GameStateChanged(GameState from, GameState to)
            => OnGameStateChanged?.Invoke(from, to);

        // ── Player ────────────────────────────────────────────
        public static event Action<int, int> OnPlayerHealthChanged;   // (current, max)
        public static void PlayerHealthChanged(int current, int max)
            => OnPlayerHealthChanged?.Invoke(current, max);

        public static event Action OnPlayerDied;
        public static void PlayerDied() => OnPlayerDied?.Invoke();

        public static event Action<AbilityData> OnAbilityUnlocked;
        public static void AbilityUnlocked(AbilityData ability)
            => OnAbilityUnlocked?.Invoke(ability);

        // ── Boat ──────────────────────────────────────────────
        public static event Action<float, float> OnBoatDurabilityChanged;  // (current, max)
        public static void BoatDurabilityChanged(float current, float max)
            => OnBoatDurabilityChanged?.Invoke(current, max);

        // ── Islands ───────────────────────────────────────────
        public static event Action<IslandData> OnIslandDiscovered;
        public static void IslandDiscovered(IslandData island)
            => OnIslandDiscovered?.Invoke(island);

        public static event Action<IslandData> OnIslandEntered;
        public static void IslandEntered(IslandData island)
            => OnIslandEntered?.Invoke(island);

        public static event Action<IslandData> OnIslandCompleted;
        public static void IslandCompleted(IslandData island)
            => OnIslandCompleted?.Invoke(island);

        // ── Bosses ────────────────────────────────────────────
        public static event Action<BossData> OnBossEncountered;
        public static void BossEncountered(BossData boss)
            => OnBossEncountered?.Invoke(boss);

        public static event Action<BossData> OnBossDefeated;
        public static void BossDefeated(BossData boss)
            => OnBossDefeated?.Invoke(boss);

        public static event Action<float, float> OnBossHealthChanged;  // (current, max)
        public static void BossHealthChanged(float current, float max)
            => OnBossHealthChanged?.Invoke(current, max);

        // ── Puzzles ───────────────────────────────────────────
        public static event Action<string> OnPuzzleSolved;
        public static void PuzzleSolved(string puzzleID)
            => OnPuzzleSolved?.Invoke(puzzleID);

        // ── Items ─────────────────────────────────────────────
        public static event Action<ItemData> OnItemPickedUp;
        public static void ItemPickedUp(ItemData item)
            => OnItemPickedUp?.Invoke(item);

        public static event Action<ItemData> OnItemUsed;
        public static void ItemUsed(ItemData item)
            => OnItemUsed?.Invoke(item);

        // ── Crystals ──────────────────────────────────────────
        public static event Action<int> OnCrystalCollected;  // total collected count
        public static void CrystalCollected(int totalCount)
            => OnCrystalCollected?.Invoke(totalCount);

        // ── Cutscenes ─────────────────────────────────────────
        public static event Action OnCutsceneStarted;
        public static void CutsceneStarted() => OnCutsceneStarted?.Invoke();

        public static event Action OnCutsceneEnded;
        public static void CutsceneEnded() => OnCutsceneEnded?.Invoke();
    }
}
