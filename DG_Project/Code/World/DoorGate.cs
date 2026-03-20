using System.Collections;
using UnityEngine;
using IsleTrial.Core;

namespace IsleTrial.World
{
    public enum DoorOpenMode { SlideUp, SlideAside, Rotate }

    /// <summary>
    /// A door or gate that opens when its linked puzzle is solved.
    /// Listens to GameEvents.OnPuzzleSolved and checks against _linkedPuzzleID.
    /// Also supports manual open/close via public API (for boss death, cutscenes, etc.).
    /// Attach to any door/gate GameObject.
    /// </summary>
    public class DoorGate : MonoBehaviour
    {
        [Header("Linking")]
        [SerializeField] private string _linkedPuzzleID;

        [Header("Open Settings")]
        [SerializeField] private DoorOpenMode _openMode = DoorOpenMode.SlideUp;
        [SerializeField] private float _openDistance = 3f;    // for slide modes
        [SerializeField] private float _openAngle = 90f;      // for rotate mode
        [SerializeField] private float _openDuration = 1.2f;
        [SerializeField] private AnimationCurve _openCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);

        [Header("VFX & Audio")]
        [SerializeField] private ParticleSystem _openVFX;
        [SerializeField] private AudioClip _openSFX;
        [SerializeField] private AudioSource _audioSource;

        private bool _isOpen;
        private Vector3 _closedPosition;
        private Quaternion _closedRotation;

        void Awake()
        {
            _closedPosition = transform.position;
            _closedRotation = transform.rotation;
        }

        void OnEnable()  => GameEvents.OnPuzzleSolved += OnPuzzleSolved;
        void OnDisable() => GameEvents.OnPuzzleSolved -= OnPuzzleSolved;

        private void OnPuzzleSolved(string puzzleID)
        {
            if (puzzleID == _linkedPuzzleID) Open();
        }

        // ── Public API ────────────────────────────────────────

        public void Open()
        {
            if (_isOpen) return;
            _isOpen = true;

            if (_openVFX != null) _openVFX.Play();
            if (_audioSource != null && _openSFX != null)
                _audioSource.PlayOneShot(_openSFX);

            StopAllCoroutines();
            StartCoroutine(AnimateDoor(true));
        }

        public void Close()
        {
            if (!_isOpen) return;
            _isOpen = false;
            StopAllCoroutines();
            StartCoroutine(AnimateDoor(false));
        }

        public void OpenImmediate()
        {
            _isOpen = true;
            ApplyOpenTransform(1f);
        }

        // ── Animation ─────────────────────────────────────────

        private IEnumerator AnimateDoor(bool opening)
        {
            float elapsed = 0f;
            while (elapsed < _openDuration)
            {
                float t = _openCurve.Evaluate(elapsed / _openDuration);
                ApplyOpenTransform(opening ? t : 1f - t);
                elapsed += Time.deltaTime;
                yield return null;
            }
            ApplyOpenTransform(opening ? 1f : 0f);
        }

        private void ApplyOpenTransform(float t)
        {
            switch (_openMode)
            {
                case DoorOpenMode.SlideUp:
                    transform.position = _closedPosition + Vector3.up * (_openDistance * t);
                    break;
                case DoorOpenMode.SlideAside:
                    transform.position = _closedPosition + transform.right * (_openDistance * t);
                    break;
                case DoorOpenMode.Rotate:
                    transform.rotation = _closedRotation * Quaternion.Euler(0, _openAngle * t, 0);
                    break;
            }
        }
    }
}
