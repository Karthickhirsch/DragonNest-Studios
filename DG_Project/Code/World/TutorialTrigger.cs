using UnityEngine;
using TMPro;
using System.Collections;
using IsleTrial.Core;

namespace IsleTrial.World
{
    /// <summary>
    /// Trigger zone that displays a tutorial message when the player first enters.
    /// Shown once — remembered via PlayerPrefs so it doesn't repeat after reload.
    /// Place trigger zones around the Tutorial Island to guide the player.
    /// Attach to an empty GameObject with a Trigger Collider.
    /// </summary>
    public class TutorialTrigger : MonoBehaviour
    {
        [Header("Tutorial Content")]
        [SerializeField] private string _triggerID;             // Unique ID, e.g. "tut_movement"
        [SerializeField] [TextArea(2, 5)] private string _message;
        [SerializeField] private Sprite _icon;                  // Optional icon in the panel

        [Header("Display")]
        [SerializeField] private float _displayDuration = 4f;
        [SerializeField] private bool _showOnce = true;

        [Header("UI (auto-found if null)")]
        [SerializeField] private TutorialHintPanel _hintPanel;

        [Header("Player Layer")]
        [SerializeField] private LayerMask _playerLayer;

        private bool _triggered;

        void Start()
        {
            if (_showOnce && PlayerPrefs.GetInt($"TutShown_{_triggerID}", 0) == 1)
                _triggered = true;

            if (_hintPanel == null)
                _hintPanel = FindObjectOfType<TutorialHintPanel>();
        }

        void OnTriggerEnter(Collider other)
        {
            if (_triggered) return;
            if ((_playerLayer.value & (1 << other.gameObject.layer)) == 0) return;

            _triggered = true;
            if (_showOnce) PlayerPrefs.SetInt($"TutShown_{_triggerID}", 1);

            _hintPanel?.ShowHint(_message, _icon, _displayDuration);
            Debug.Log($"[Tutorial] Trigger fired: {_triggerID}");
        }

        /// <summary>Reset this trigger (e.g. on New Game).</summary>
        public static void ResetAll()
        {
            foreach (var trig in FindObjectsOfType<TutorialTrigger>())
            {
                PlayerPrefs.DeleteKey($"TutShown_{trig._triggerID}");
                trig._triggered = false;
            }
        }
    }

    /// <summary>
    /// UI panel that displays tutorial hint messages.
    /// Attach to the TutorialHintPanel Canvas child.
    /// </summary>
    public class TutorialHintPanel : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private CanvasGroup _canvasGroup;
        [SerializeField] private TextMeshProUGUI _messageText;
        [SerializeField] private UnityEngine.UI.Image _iconImage;
        [SerializeField] private float _fadeDuration = 0.4f;

        private Coroutine _activeRoutine;

        void Start()
        {
            _canvasGroup.alpha = 0f;
            gameObject.SetActive(false);
        }

        public void ShowHint(string message, Sprite icon, float duration)
        {
            if (_activeRoutine != null) StopCoroutine(_activeRoutine);
            _activeRoutine = StartCoroutine(DisplayRoutine(message, icon, duration));
        }

        private IEnumerator DisplayRoutine(string message, Sprite icon, float duration)
        {
            gameObject.SetActive(true);
            _messageText.text = message;

            if (_iconImage != null)
            {
                _iconImage.sprite = icon;
                _iconImage.gameObject.SetActive(icon != null);
            }

            // Fade in
            float t = 0f;
            while (t < _fadeDuration)
            {
                _canvasGroup.alpha = t / _fadeDuration;
                t += Time.deltaTime;
                yield return null;
            }
            _canvasGroup.alpha = 1f;

            yield return new WaitForSeconds(duration);

            // Fade out
            t = 0f;
            while (t < _fadeDuration)
            {
                _canvasGroup.alpha = 1f - (t / _fadeDuration);
                t += Time.deltaTime;
                yield return null;
            }

            _canvasGroup.alpha = 0f;
            gameObject.SetActive(false);
        }
    }
}
