using System.Collections.Generic;
using UnityEngine;

namespace IsleTrial.Puzzles
{
    /// <summary>
    /// Symbol Match Puzzle: player rotates tiles to match a target pattern.
    /// 
    /// Setup in Unity:
    ///   1. Create child GameObjects for each tile.
    ///   2. Assign a SpriteRenderer on each tile child.
    ///   3. Fill _tiles list with each tile's SymbolTile component.
    ///   4. Set _solutionIndices (e.g. [2, 0, 1, 3] = tile0=symbol2, tile1=symbol0 ...).
    ///   5. Assign this component on a Puzzle root GameObject.
    /// </summary>
    public class SymbolMatchPuzzle : PuzzleBase
    {
        [Header("Tiles")]
        [SerializeField] private List<SymbolTile> _tiles;
        [SerializeField] private List<int> _solutionIndices;    // index per tile

        [Header("Cascade (optional)")]
        [Tooltip("If true, rotating tile i also rotates adjacent tiles")]
        [SerializeField] private bool _cascadeMode;

        public override void Initialize()
        {
            foreach (var tile in _tiles) tile.Initialize();
        }

        public override void OnPlayerInteract(GameObject player)
        {
            if (IsSolved) return;
            // The player must be close to a specific tile — handled by SymbolTile itself.
            // SymbolTile calls RotateTile() and notifies this puzzle.
        }

        /// <summary>Called by SymbolTile when the player interacts with it.</summary>
        public void RotateTile(SymbolTile tile)
        {
            if (IsSolved) return;
            int index = _tiles.IndexOf(tile);
            if (index < 0) return;

            tile.Rotate();

            if (_cascadeMode) CascadeRotate(index);

            if (CheckSolution()) MarkSolved();
        }

        private void CascadeRotate(int originIndex)
        {
            int left = originIndex - 1;
            int right = originIndex + 1;
            if (left >= 0) _tiles[left].Rotate();
            if (right < _tiles.Count) _tiles[right].Rotate();
        }

        private bool CheckSolution()
        {
            if (_tiles.Count != _solutionIndices.Count) return false;
            for (int i = 0; i < _tiles.Count; i++)
                if (_tiles[i].CurrentIndex != _solutionIndices[i]) return false;
            return true;
        }

        public override void Reset()
        {
            foreach (var tile in _tiles) tile.Initialize();
        }
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Individual rotating tile for SymbolMatchPuzzle.
    /// Attach to each tile child GameObject with a SpriteRenderer.
    /// </summary>
    public class SymbolTile : MonoBehaviour, IInteractable
    {
        [SerializeField] private List<Sprite> _symbols;
        [SerializeField] private SpriteRenderer _renderer;
        [SerializeField] private SymbolMatchPuzzle _parentPuzzle;

        public int CurrentIndex { get; private set; }

        public void Initialize()
        {
            CurrentIndex = 0;
            UpdateSprite();
        }

        public void Rotate()
        {
            CurrentIndex = (CurrentIndex + 1) % _symbols.Count;
            UpdateSprite();
        }

        public void Interact(object interactor)
        {
            _parentPuzzle?.RotateTile(this);
        }

        private void UpdateSprite()
        {
            if (_renderer != null && _symbols.Count > 0)
                _renderer.sprite = _symbols[CurrentIndex];
        }
    }
}
