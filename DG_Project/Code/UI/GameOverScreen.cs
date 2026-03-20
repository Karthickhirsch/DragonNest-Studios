using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using IsleTrial.Core;
using IsleTrial.SaveSystem;

namespace IsleTrial.UI
{
    /// <summary>
    /// Game Over screen shown when the player dies.
    /// Subscribes to GameEvents.OnPlayerDied.
    /// Fades in, then offers Retry (reload last save) or Main Menu.
    /// Attach to the GameOverPanel Canvas child (default inactive).
    /// </summary>
    public class GameOverScreen : MonoBehaviour
    {
        [Header("Panel")]
        [SerializeField] private CanvasGroup _canvasGroup;
        [SerializeField] private float _fadeInDuration = 1.5f;
        [SerializeField] private float _delayBeforeFade = 0.8f;

        [Header("Buttons")]
        [SerializeField] private Button _retryButton;
        [SerializeField] private Button _mainMenuButton;

        [Header("Text")]
        [SerializeField] private TextMeshProUGUI _deathMessageText;

        private static readonly string[] _deathMessages =
        {
            "The sea claims another soul...",
            "The islands will remember you.",
            "Lost to the deep.",
            "The storm was merciless.",
            "Courage alone wasn't enough."
        };

        void Start()
        {
            _canvasGroup.alpha = 0f;
            _canvasGroup.interactable = false;
            _canvasGroup.blocksRaycasts = false;
            gameObject.SetActive(false);

            _retryButton.onClick.AddListener(OnRetry);
            _mainMenuButton.onClick.AddListener(OnMainMenu);
        }

        void OnEnable()  => GameEvents.OnPlayerDied += OnPlayerDied;
        void OnDisable() => GameEvents.OnPlayerDied -= OnPlayerDied;

        // ── Event Handler ─────────────────────────────────────

        private void OnPlayerDied()
        {
            GameManager.Instance.ChangeState(GameState.GameOver);
            gameObject.SetActive(true);
            StartCoroutine(FadeInRoutine());
        }

        // ── Button Handlers ───────────────────────────────────

        private void OnRetry()
        {
            Time.timeScale = 1f;
            var data = SaveManager.Instance?.LoadGame(0);
            if (data != null)
                SaveManager.Instance.ApplySaveData(data);

            SceneLoader.Instance.UnloadScene("Ocean_World");
            SceneLoader.Instance.LoadSceneAdditive("Ocean_World", () =>
            {
                GameManager.Instance.ChangeState(GameState.Sailing);
                gameObject.SetActive(false);
            });
        }

        private void OnMainMenu()
        {
            Time.timeScale = 1f;
            SceneLoader.Instance.UnloadScene("Ocean_World");
            SceneLoader.Instance.LoadSceneAdditive("MainMenu");
            GameManager.Instance.ChangeState(GameState.MainMenu);
            gameObject.SetActive(false);
        }

        // ── Fade ──────────────────────────────────────────────

        private IEnumerator FadeInRoutine()
        {
            if (_deathMessageText != null)
                _deathMessageText.text = _deathMessages[Random.Range(0, _deathMessages.Length)];

            yield return new WaitForSecondsRealtime(_delayBeforeFade);

            float elapsed = 0f;
            while (elapsed < _fadeInDuration)
            {
                _canvasGroup.alpha = Mathf.Lerp(0f, 1f, elapsed / _fadeInDuration);
                elapsed += Time.unscaledDeltaTime;
                yield return null;
            }

            _canvasGroup.alpha = 1f;
            _canvasGroup.interactable = true;
            _canvasGroup.blocksRaycasts = true;
        }
    }
}
