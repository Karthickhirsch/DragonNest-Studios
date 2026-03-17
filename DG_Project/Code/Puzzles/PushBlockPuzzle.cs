using System.Collections.Generic;
using System.Collections;
using UnityEngine;

namespace IsleTrial.Puzzles
{
    /// <summary>
    /// Push Block Puzzle: player shoves blocks onto pressure plates.
    /// 
    /// Setup in Unity:
    ///   1. Create PushableBlock child GameObjects and add PushableBlock component.
    ///   2. Create PressurePlate GameObjects and add PressurePlate component.
    ///   3. Assign _blocks and _plates lists on this component.
    ///   4. Pair each block with the plate it must land on using _blockPlatePairs.
    /// </summary>
    public class PushBlockPuzzle : PuzzleBase
    {
        [Header("Puzzle Objects")]
        [SerializeField] private List<PushableBlock> _blocks;
        [SerializeField] private List<PressurePlate> _plates;

        public override void Initialize()
        {
            foreach (var plate in _plates)
                plate.OnActivated += CheckAllPlatesActive;
        }

        public override void OnPlayerInteract(GameObject player) { }

        public override void Reset()
        {
            foreach (var block in _blocks) block.ResetToStart();
            foreach (var plate in _plates) plate.Deactivate();
        }

        private void CheckAllPlatesActive()
        {
            foreach (var plate in _plates)
                if (!plate.IsActive) return;
            MarkSolved();
        }

        void OnDestroy()
        {
            foreach (var plate in _plates) plate.OnActivated -= CheckAllPlatesActive;
        }
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Block that the player can push. Attach to a block prefab.
    /// Requires a Rigidbody (isKinematic = true) and Collider.
    /// </summary>
    public class PushableBlock : MonoBehaviour, IInteractable
    {
        [SerializeField] private float _moveDistance = 1f;
        [SerializeField] private float _moveDuration = 0.2f;
        [SerializeField] private LayerMask _blockingLayers;

        private Vector3 _startPosition;
        private bool _isMoving;

        void Awake() => _startPosition = transform.position;

        /// <summary>Called by player when they push the block from a direction.</summary>
        public void Push(Vector3 direction)
        {
            if (_isMoving) return;
            direction = RoundDirection(direction);
            Vector3 target = transform.position + direction * _moveDistance;

            if (Physics.Raycast(transform.position, direction, _moveDistance, _blockingLayers))
            {
                Debug.Log("[PushBlock] Path blocked.");
                return;
            }
            StartCoroutine(MoveRoutine(target));
        }

        public void Interact(object interactor)
        {
            // Player calls Push with their forward direction
            if (interactor is GameObject player)
                Push(player.transform.forward);
        }

        public void ResetToStart()
        {
            StopAllCoroutines();
            _isMoving = false;
            transform.position = _startPosition;
        }

        private IEnumerator MoveRoutine(Vector3 target)
        {
            _isMoving = true;
            float elapsed = 0f;
            Vector3 start = transform.position;
            while (elapsed < _moveDuration)
            {
                elapsed += Time.deltaTime;
                transform.position = Vector3.Lerp(start, target, elapsed / _moveDuration);
                yield return null;
            }
            transform.position = target;
            _isMoving = false;
        }

        private Vector3 RoundDirection(Vector3 dir)
        {
            dir.y = 0;
            dir = dir.normalized;
            float angle = Mathf.Atan2(dir.x, dir.z) * Mathf.Rad2Deg;
            angle = Mathf.Round(angle / 90f) * 90f;
            return new Vector3(Mathf.Sin(angle * Mathf.Deg2Rad), 0, Mathf.Cos(angle * Mathf.Deg2Rad));
        }
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Pressure plate that activates when a block lands on it.
    /// Attach to a flat surface GameObject with a trigger Collider (isTrigger = true).
    /// </summary>
    public class PressurePlate : MonoBehaviour
    {
        [SerializeField] private Renderer _plateRenderer;
        [SerializeField] private Color _activeColor = Color.green;
        [SerializeField] private Color _inactiveColor = Color.gray;

        public bool IsActive { get; private set; }
        public System.Action OnActivated;
        public System.Action OnDeactivated;

        void Awake() => UpdateColor();

        void OnTriggerEnter(Collider other)
        {
            if (!other.TryGetComponent<PushableBlock>(out _)) return;
            IsActive = true;
            UpdateColor();
            OnActivated?.Invoke();
        }

        void OnTriggerExit(Collider other)
        {
            if (!other.TryGetComponent<PushableBlock>(out _)) return;
            IsActive = false;
            UpdateColor();
            OnDeactivated?.Invoke();
        }

        public void Deactivate()
        {
            IsActive = false;
            UpdateColor();
        }

        private void UpdateColor()
        {
            if (_plateRenderer != null)
                _plateRenderer.material.color = IsActive ? _activeColor : _inactiveColor;
        }
    }
}
