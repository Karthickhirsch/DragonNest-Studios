using System.Collections;
using UnityEngine;
using UnityEngine.Rendering;
using IsleTrial.Boat;

namespace IsleTrial.World
{
    public enum WeatherState { Calm, Cloudy, Stormy, Foggy }

    /// <summary>
    /// Controls ocean weather, wind, fog, rain, and post-process volume.
    /// Attach to a persistent manager GameObject in the Ocean_World scene.
    /// </summary>
    public class WeatherSystem : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private WindZone _windZone;
        [SerializeField] private ParticleSystem _rainParticles;
        [SerializeField] private Volume _postProcessVolume;
        [SerializeField] private Light _sunLight;
        [SerializeField] private BoatController _boat;

        [Header("Weather Profiles")]
        [SerializeField] private VolumeProfile _calmProfile;
        [SerializeField] private VolumeProfile _stormyProfile;
        [SerializeField] private VolumeProfile _foggyProfile;

        [Header("Transition")]
        [SerializeField] private float _transitionDuration = 5f;

        [Header("Auto-Change")]
        [SerializeField] private bool _autoChange = true;
        [SerializeField] private float _minWeatherDuration = 120f;
        [SerializeField] private float _maxWeatherDuration = 300f;

        public WeatherState CurrentWeather { get; private set; }

        private float _weatherTimer;
        private Coroutine _transitionCoroutine;

        void Start()
        {
            SetWeather(WeatherState.Calm, instant: true);
            ScheduleNextWeather();
        }

        void Update()
        {
            if (!_autoChange) return;
            _weatherTimer -= Time.deltaTime;
            if (_weatherTimer <= 0) PickRandomWeather();
        }

        // ── Public API ────────────────────────────────────────

        public void SetWeather(WeatherState state, bool instant = false)
        {
            CurrentWeather = state;
            if (_transitionCoroutine != null) StopCoroutine(_transitionCoroutine);
            _transitionCoroutine = StartCoroutine(TransitionWeather(state, instant ? 0 : _transitionDuration));
        }

        // ── Internals ─────────────────────────────────────────

        private IEnumerator TransitionWeather(WeatherState state, float duration)
        {
            switch (state)
            {
                case WeatherState.Calm:
                    SetWind(0.5f, Vector3.forward);
                    SetRain(false);
                    SetPostProcess(_calmProfile, duration);
                    SetSunIntensity(1.2f, duration);
                    break;

                case WeatherState.Cloudy:
                    SetWind(1f, Vector3.forward);
                    SetRain(false);
                    SetSunIntensity(0.7f, duration);
                    break;

                case WeatherState.Stormy:
                    SetWind(3f, RandomWindDirection());
                    SetRain(true);
                    SetPostProcess(_stormyProfile, duration);
                    SetSunIntensity(0.3f, duration);
                    _boat?.SetWind(RandomWindDirection(), 4f);
                    break;

                case WeatherState.Foggy:
                    SetWind(0.3f, Vector3.forward);
                    SetRain(false);
                    SetPostProcess(_foggyProfile, duration);
                    break;
            }
            yield return null;
        }

        private void SetWind(float strength, Vector3 direction)
        {
            if (_windZone == null) return;
            _windZone.windMain = strength;
            _windZone.transform.rotation = Quaternion.LookRotation(direction);
        }

        private void SetRain(bool active)
        {
            if (_rainParticles == null) return;
            if (active) _rainParticles.Play();
            else _rainParticles.Stop();
        }

        private void SetPostProcess(VolumeProfile profile, float duration)
        {
            if (_postProcessVolume == null || profile == null) return;
            StartCoroutine(LerpVolumeWeight(profile, duration));
        }

        private IEnumerator LerpVolumeWeight(VolumeProfile target, float duration)
        {
            _postProcessVolume.profile = target;
            float t = 0;
            while (t < duration) { t += Time.deltaTime; yield return null; }
        }

        private void SetSunIntensity(float target, float duration)
        {
            if (_sunLight == null) return;
            StartCoroutine(LerpSun(target, duration));
        }

        private IEnumerator LerpSun(float target, float duration)
        {
            float start = _sunLight.intensity;
            float t = 0;
            while (t < 1f)
            {
                t += Time.deltaTime / duration;
                _sunLight.intensity = Mathf.Lerp(start, target, t);
                yield return null;
            }
        }

        private void PickRandomWeather()
        {
            WeatherState[] options = { WeatherState.Calm, WeatherState.Cloudy,
                                       WeatherState.Stormy, WeatherState.Foggy };
            SetWeather(options[Random.Range(0, options.Length)]);
            ScheduleNextWeather();
        }

        private void ScheduleNextWeather()
            => _weatherTimer = Random.Range(_minWeatherDuration, _maxWeatherDuration);

        private Vector3 RandomWindDirection()
        {
            float angle = Random.Range(0f, 360f);
            return new Vector3(Mathf.Sin(angle * Mathf.Deg2Rad), 0, Mathf.Cos(angle * Mathf.Deg2Rad));
        }
    }
}
