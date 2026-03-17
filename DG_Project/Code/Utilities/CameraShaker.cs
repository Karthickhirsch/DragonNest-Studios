using System.Collections;
using UnityEngine;
using Cinemachine;

namespace IsleTrial.Utilities
{
    /// <summary>
    /// Camera shake via Cinemachine noise.
    /// Attach to the same GameObject as your main CinemachineVirtualCamera.
    /// Requires: CinemachineVirtualCamera with Noise extension added.
    /// </summary>
    public class CameraShaker : MonoBehaviour
    {
        public static CameraShaker Instance { get; private set; }

        [Header("Presets")]
        [SerializeField] private float _lightShakeIntensity = 0.5f;
        [SerializeField] private float _mediumShakeIntensity = 1.5f;
        [SerializeField] private float _heavyShakeIntensity = 3f;

        private CinemachineVirtualCamera _vcam;
        private CinemachineBasicMultiChannelPerlin _noise;
        private Coroutine _shakeCoroutine;

        void Awake()
        {
            Instance = this;
            _vcam = GetComponent<CinemachineVirtualCamera>();
            _noise = _vcam?.GetCinemachineComponent<CinemachineBasicMultiChannelPerlin>();
        }

        // ── Public API ────────────────────────────────────────

        public void ShakeLight(float duration = 0.2f)   => Shake(_lightShakeIntensity, duration);
        public void ShakeMedium(float duration = 0.3f)  => Shake(_mediumShakeIntensity, duration);
        public void ShakeHeavy(float duration = 0.5f)   => Shake(_heavyShakeIntensity, duration);

        public void Shake(float intensity, float duration)
        {
            if (_noise == null) return;
            if (_shakeCoroutine != null) StopCoroutine(_shakeCoroutine);
            _shakeCoroutine = StartCoroutine(ShakeRoutine(intensity, duration));
        }

        // ── Coroutine ─────────────────────────────────────────

        private IEnumerator ShakeRoutine(float intensity, float duration)
        {
            _noise.m_AmplitudeGain = intensity;
            _noise.m_FrequencyGain = intensity * 1.5f;
            yield return new WaitForSeconds(duration);

            // Smooth recovery
            float t = 0;
            float start = intensity;
            while (t < 1f)
            {
                t += Time.deltaTime / 0.15f;
                float val = Mathf.Lerp(start, 0f, t);
                _noise.m_AmplitudeGain = val;
                _noise.m_FrequencyGain = val * 1.5f;
                yield return null;
            }
            _noise.m_AmplitudeGain = 0f;
            _noise.m_FrequencyGain = 0f;
        }
    }
}
