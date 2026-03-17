using System.Collections.Generic;
using UnityEngine;

namespace IsleTrial.Puzzles
{
    /// <summary>
    /// Light Beam Puzzle: a beam bounces off mirrors and must hit a receiver.
    /// 
    /// Setup in Unity:
    ///   1. Create a LightBeamEmitter child (this component draws the beam).
    ///   2. Place Mirror GameObjects with Mirror component in the scene.
    ///   3. Place a LightReceiver GameObject with LightReceiver component.
    ///   4. Assign _receivers list (can require multiple).
    ///   5. Add this component on Puzzle root GameObject.
    /// </summary>
    public class LightBeamPuzzle : PuzzleBase
    {
        [Header("Beam")]
        [SerializeField] private LightBeamEmitter _emitter;
        [SerializeField] private List<LightReceiver> _receivers;

        public override void Initialize()
        {
            foreach (var r in _receivers) r.OnActivated += CheckAllReceiversHit;
        }

        public override void OnPlayerInteract(GameObject player) { }

        public override void Reset()
        {
            foreach (var r in _receivers) r.Deactivate();
        }

        private void CheckAllReceiversHit()
        {
            foreach (var r in _receivers)
                if (!r.IsActive) return;
            MarkSolved();
        }

        void OnDestroy()
        {
            foreach (var r in _receivers) r.OnActivated -= CheckAllReceiversHit;
        }
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Emits and simulates a light beam that bounces off Mirror components.
    /// Attach to the beam source GameObject. Requires a LineRenderer.
    /// </summary>
    [RequireComponent(typeof(LineRenderer))]
    public class LightBeamEmitter : MonoBehaviour
    {
        [SerializeField] private int _maxReflections = 8;
        [SerializeField] private float _maxDistance = 50f;
        [SerializeField] private LayerMask _reflectLayer;
        [SerializeField] private Color _beamColor = Color.yellow;

        private LineRenderer _lr;
        private readonly List<Vector3> _points = new();

        void Awake()
        {
            _lr = GetComponent<LineRenderer>();
            _lr.startColor = _beamColor;
            _lr.endColor = _beamColor;
            _lr.startWidth = 0.05f;
            _lr.endWidth = 0.05f;
        }

        void Update()
        {
            _points.Clear();
            _points.Add(transform.position);
            SimulateBeam(transform.position, transform.forward, 0);
            _lr.positionCount = _points.Count;
            _lr.SetPositions(_points.ToArray());
        }

        private void SimulateBeam(Vector3 origin, Vector3 direction, int depth)
        {
            if (depth >= _maxReflections) return;
            if (!Physics.Raycast(origin, direction, out RaycastHit hit, _maxDistance, _reflectLayer))
            {
                _points.Add(origin + direction * _maxDistance);
                return;
            }

            _points.Add(hit.point);

            if (hit.collider.TryGetComponent<Mirror>(out _))
            {
                Vector3 reflected = Vector3.Reflect(direction, hit.normal);
                SimulateBeam(hit.point + reflected * 0.01f, reflected, depth + 1);
            }
            else if (hit.collider.TryGetComponent<LightReceiver>(out var receiver))
            {
                receiver.Activate();
            }
        }
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Place on mirror GameObjects. Player can rotate them in the scene.
    /// Attach to mirror child objects.
    /// </summary>
    public class Mirror : MonoBehaviour, IInteractable
    {
        [SerializeField] private float _rotationStep = 45f;

        public void Interact(object interactor)
        {
            transform.Rotate(Vector3.up, _rotationStep);
        }
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Attach to the target receiver object. Activates when beam hits it.
    /// </summary>
    public class LightReceiver : MonoBehaviour
    {
        [SerializeField] private Renderer _visualRenderer;
        [SerializeField] private Color _activeColor = Color.yellow;
        [SerializeField] private Color _inactiveColor = Color.gray;

        public bool IsActive { get; private set; }
        public System.Action OnActivated;

        private bool _hitThisFrame;

        void Awake() => UpdateColor();

        void LateUpdate()
        {
            if (IsActive && !_hitThisFrame)
            {
                IsActive = false;
                UpdateColor();
            }
            _hitThisFrame = false;
        }

        public void Activate()
        {
            _hitThisFrame = true;
            if (!IsActive)
            {
                IsActive = true;
                UpdateColor();
                OnActivated?.Invoke();
            }
        }

        public void Deactivate()
        {
            IsActive = false;
            _hitThisFrame = false;
            UpdateColor();
        }

        private void UpdateColor()
        {
            if (_visualRenderer != null)
                _visualRenderer.material.color = IsActive ? _activeColor : _inactiveColor;
        }
    }
}
