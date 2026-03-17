using UnityEngine;

namespace IsleTrial.Boat
{
    /// <summary>
    /// Simulates wave-based buoyancy.
    /// Attach to the Boat GameObject. Requires Rigidbody.
    /// Assign 4 FloatPoints at the corners of the boat hull in the Inspector.
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    public class OceanBuoyancy : MonoBehaviour
    {
        [Header("Wave Settings")]
        [SerializeField] private float _waveHeight = 1.5f;
        [SerializeField] private float _waveFrequency = 0.5f;
        [SerializeField] private float _waveSpeed = 1f;

        [Header("Buoyancy")]
        [SerializeField] private float _buoyancyForce = 15f;
        [SerializeField] private float _waterDrag = 2f;
        [SerializeField] private float _waterAngularDrag = 1f;
        [SerializeField] private float _waterLevel = 0f;

        [Header("Float Points")]
        [Tooltip("Assign 4 child Transforms at boat hull corners")]
        [SerializeField] private Transform[] _floatPoints;

        private Rigidbody _rb;

        void Awake() => _rb = GetComponent<Rigidbody>();

        void FixedUpdate()
        {
            _rb.drag = _waterDrag;
            _rb.angularDrag = _waterAngularDrag;

            if (_floatPoints == null || _floatPoints.Length == 0) return;

            foreach (var point in _floatPoints)
            {
                float waveY = GetWaveHeight(point.position.x, point.position.z);
                float submersion = waveY - point.position.y;

                if (submersion > 0)
                {
                    _rb.AddForceAtPosition(
                        Vector3.up * _buoyancyForce * submersion,
                        point.position,
                        ForceMode.Force
                    );
                }
            }
        }

        /// <summary>
        /// Returns the ocean surface Y at a given world X,Z position using sine waves.
        /// Also used by the Ocean Shader to stay in sync (pass same parameters).
        /// </summary>
        public float GetWaveHeight(float x, float z)
        {
            float time = Time.time * _waveSpeed;
            return _waterLevel
                + Mathf.Sin(x * _waveFrequency + time) * _waveHeight
                + Mathf.Sin(z * _waveFrequency * 0.7f + time * 1.3f) * _waveHeight * 0.5f;
        }

        void OnDrawGizmosSelected()
        {
            if (_floatPoints == null) return;
            Gizmos.color = Color.cyan;
            foreach (var p in _floatPoints)
                if (p != null) Gizmos.DrawSphere(p.position, 0.1f);
        }
    }
}
