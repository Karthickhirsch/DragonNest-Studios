using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace IsleTrial.Audio
{
    /// <summary>
    /// Simple AudioManager that handles music crossfading and SFX playback.
    /// For FMOD integration, replace PlayOneShot calls with FMOD event calls.
    /// Attach to the Bootstrap scene's persistent manager GameObject.
    /// Assign AudioSources: _musicSource (for music), _sfxSource (for SFX).
    /// </summary>
    public class AudioManager : MonoBehaviour
    {
        public static AudioManager Instance { get; private set; }

        [Header("Sources")]
        [SerializeField] private AudioSource _musicSourceA;   // Crossfade A
        [SerializeField] private AudioSource _musicSourceB;   // Crossfade B
        [SerializeField] private AudioSource _sfxSource;

        [Header("Volumes")]
        [SerializeField, Range(0f, 1f)] private float _masterVolume = 1f;
        [SerializeField, Range(0f, 1f)] private float _musicVolume = 0.6f;
        [SerializeField, Range(0f, 1f)] private float _sfxVolume = 1f;

        [Header("Crossfade")]
        [SerializeField] private float _crossfadeDuration = 2f;

        private AudioSource _activeMusic;
        private AudioSource _inactiveMusic;
        private Coroutine _crossfadeCoroutine;

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            _activeMusic = _musicSourceA;
            _inactiveMusic = _musicSourceB;
        }

        // ── Music ─────────────────────────────────────────────

        public void PlayMusic(AudioClip clip, bool loop = true)
        {
            if (_activeMusic.clip == clip) return;
            if (_crossfadeCoroutine != null) StopCoroutine(_crossfadeCoroutine);
            _crossfadeCoroutine = StartCoroutine(CrossfadeMusic(clip, loop));
        }

        public void StopMusic()
        {
            if (_crossfadeCoroutine != null) StopCoroutine(_crossfadeCoroutine);
            StartCoroutine(FadeOut(_activeMusic, _crossfadeDuration));
        }

        private IEnumerator CrossfadeMusic(AudioClip newClip, bool loop)
        {
            _inactiveMusic.clip = newClip;
            _inactiveMusic.loop = loop;
            _inactiveMusic.volume = 0f;
            _inactiveMusic.Play();

            float t = 0;
            float startVolume = _activeMusic.volume;
            float targetVolume = _musicVolume * _masterVolume;

            while (t < 1f)
            {
                t += Time.deltaTime / _crossfadeDuration;
                _activeMusic.volume = Mathf.Lerp(startVolume, 0f, t);
                _inactiveMusic.volume = Mathf.Lerp(0f, targetVolume, t);
                yield return null;
            }

            _activeMusic.Stop();
            // Swap roles
            (_activeMusic, _inactiveMusic) = (_inactiveMusic, _activeMusic);
        }

        private IEnumerator FadeOut(AudioSource source, float duration)
        {
            float start = source.volume;
            float t = 0;
            while (t < 1f) { t += Time.deltaTime / duration; source.volume = Mathf.Lerp(start, 0f, t); yield return null; }
            source.Stop();
        }

        // ── SFX ───────────────────────────────────────────────

        public void PlaySFX(AudioClip clip)
        {
            if (clip == null) return;
            _sfxSource.PlayOneShot(clip, _sfxVolume * _masterVolume);
        }

        public void PlaySFXAtPosition(AudioClip clip, Vector3 position)
        {
            if (clip == null) return;
            AudioSource.PlayClipAtPoint(clip, position, _sfxVolume * _masterVolume);
        }

        // ── Volume Control ────────────────────────────────────

        public void SetMasterVolume(float vol)
        {
            _masterVolume = Mathf.Clamp01(vol);
            ApplyVolumes();
        }

        public void SetMusicVolume(float vol)
        {
            _musicVolume = Mathf.Clamp01(vol);
            ApplyVolumes();
        }

        public void SetSFXVolume(float vol) => _sfxVolume = Mathf.Clamp01(vol);

        private void ApplyVolumes()
        {
            if (_activeMusic != null)
                _activeMusic.volume = _musicVolume * _masterVolume;
        }
    }
}
