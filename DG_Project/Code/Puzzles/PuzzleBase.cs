using System;
using UnityEngine;
using IsleTrial.Core;

namespace IsleTrial.Puzzles
{
    /// <summary>
    /// Base class for all puzzles. Every puzzle must extend this.
    /// Override Initialize(), OnPlayerInteract(), and Reset().
    /// Add a PuzzleBase-derived component to a Puzzle root GameObject in the scene.
    /// </summary>
    public abstract class PuzzleBase : MonoBehaviour
    {
        [Header("Puzzle Settings")]
        [SerializeField] private string _puzzleID;
        [SerializeField] private GameObject _rewardObject;       // Door, gate, chest, etc.
        [SerializeField] private ParticleSystem _solvedVFX;
        [SerializeField] private AudioSource _solvedAudio;

        public string PuzzleID => _puzzleID;
        public bool IsSolved { get; private set; }

        public event Action<string> OnPuzzleSolvedEvent;

        protected virtual void Start()
        {
            Initialize();
        }

        /// <summary>Called once at start to set up puzzle state.</summary>
        public abstract void Initialize();

        /// <summary>Called when the player presses Interact on the puzzle.</summary>
        public abstract void OnPlayerInteract(GameObject player);

        /// <summary>Called to reset the puzzle to its default state.</summary>
        public abstract void Reset();

        /// <summary>Call this from derived classes when the solution is correct.</summary>
        protected void MarkSolved()
        {
            if (IsSolved) return;
            IsSolved = true;

            if (_solvedVFX != null) _solvedVFX.Play();
            if (_solvedAudio != null) _solvedAudio.Play();
            if (_rewardObject != null) _rewardObject.SetActive(true);

            OnPuzzleSolvedEvent?.Invoke(_puzzleID);
            GameEvents.PuzzleSolved(_puzzleID);

            Debug.Log($"[Puzzle] Solved: {_puzzleID}");
        }

        public bool LoadSolvedState(bool savedState)
        {
            if (savedState)
            {
                IsSolved = true;
                if (_rewardObject != null) _rewardObject.SetActive(true);
            }
            return savedState;
        }
    }
}
