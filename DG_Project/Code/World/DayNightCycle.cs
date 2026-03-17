using UnityEngine;

namespace IsleTrial.World
{
    public enum TimeOfDay { Dawn, Morning, Afternoon, Evening, Night }

    /// <summary>
    /// Rotates the directional light to simulate a day/night cycle.
    /// Attach to a persistent manager object in the Ocean_World scene.
    /// Assign the Directional Light as _sun.
    /// </summary>
    public class DayNightCycle : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Light _sun;
        [SerializeField] private Light _moon;

        [Header("Cycle Settings")]
        [Tooltip("How many real-world minutes = one full in-game day")]
        [SerializeField] private float _dayDurationMinutes = 24f;

        [Header("Colors")]
        [SerializeField] private Gradient _sunColorOverDay;
        [SerializeField] private AnimationCurve _sunIntensityCurve;

        [Header("Sky")]
        [SerializeField] private Material _skyboxMaterial;
        [SerializeField] private string _skyboxBlendProperty = "_Blend";

        public float TimeOfDayNormalized { get; private set; }  // 0 = midnight, 0.5 = noon
        public TimeOfDay CurrentTimeOfDay { get; private set; }

        private float _dayDurationSeconds;
        private float _currentTime;

        void Awake()
        {
            _dayDurationSeconds = _dayDurationMinutes * 60f;
            _currentTime = _dayDurationSeconds * 0.25f; // Start at dawn
        }

        void Update()
        {
            _currentTime += Time.deltaTime;
            if (_currentTime >= _dayDurationSeconds) _currentTime = 0f;

            TimeOfDayNormalized = _currentTime / _dayDurationSeconds;
            UpdateSun();
            UpdateSkybox();
            UpdateTimeEnum();
        }

        private void UpdateSun()
        {
            if (_sun == null) return;
            float sunAngle = TimeOfDayNormalized * 360f - 90f;
            _sun.transform.rotation = Quaternion.Euler(sunAngle, -30f, 0f);

            if (_sunColorOverDay != null)
                _sun.color = _sunColorOverDay.Evaluate(TimeOfDayNormalized);
            if (_sunIntensityCurve != null)
                _sun.intensity = _sunIntensityCurve.Evaluate(TimeOfDayNormalized);

            // Moon is opposite the sun
            if (_moon != null)
            {
                _moon.transform.rotation = Quaternion.Euler(sunAngle + 180f, -30f, 0f);
                _moon.enabled = TimeOfDayNormalized > 0.75f || TimeOfDayNormalized < 0.25f;
            }
        }

        private void UpdateSkybox()
        {
            if (_skyboxMaterial == null) return;
            // Blend between day sky (0) and night sky (1)
            float blend = TimeOfDayNormalized > 0.5f
                ? Mathf.InverseLerp(0.5f, 0.75f, TimeOfDayNormalized)
                : Mathf.InverseLerp(0.25f, 0f, TimeOfDayNormalized);
            _skyboxMaterial.SetFloat(_skyboxBlendProperty, blend);
        }

        private void UpdateTimeEnum()
        {
            float t = TimeOfDayNormalized;
            CurrentTimeOfDay = t switch
            {
                < 0.1f => TimeOfDay.Dawn,
                < 0.35f => TimeOfDay.Morning,
                < 0.6f => TimeOfDay.Afternoon,
                < 0.75f => TimeOfDay.Evening,
                _ => TimeOfDay.Night
            };
        }

        /// <summary>Returns true if it's currently daytime (sun visible).</summary>
        public bool IsDaytime() => TimeOfDayNormalized >= 0.1f && TimeOfDayNormalized <= 0.75f;

        /// <summary>Returns true if it's around noon (for solar puzzles).</summary>
        public bool IsNoon() => TimeOfDayNormalized >= 0.45f && TimeOfDayNormalized <= 0.55f;
    }
}
