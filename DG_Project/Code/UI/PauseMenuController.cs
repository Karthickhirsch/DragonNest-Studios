using UnityEngine;
using UnityEngine.UI;
using IsleTrial.Core;
using IsleTrial.SaveSystem;

namespace IsleTrial.UI
{
    /// <summary>
    /// Pause menu: toggled with Escape key.
    /// Handles Resume, Save, Load Main Menu, and Quit.
    /// Attach to the PauseMenuPanel Canvas child (default inactive).
    /// </summary>
    public class PauseMenuController : MonoBehaviour
    {
        [Header("Panel")]
        [SerializeField] private GameObject _pausePanel;

        [Header("Buttons")]
        [SerializeField] private Button _resumeButton;
        [SerializeField] private Button _saveButton;
        [SerializeField] private Button _mainMenuButton;
        [SerializeField] private Button _quitButton;

        [Header("Feedback")]
        [SerializeField] private TMPro.TextMeshProUGUI _saveConfirmText;
        [SerializeField] private float _saveConfirmDisplayTime = 2f;

        private bool _isPaused;
        private float _saveConfirmTimer;

        void Start()
        {
            _resumeButton.onClick.AddListener(Resume);
            _saveButton.onClick.AddListener(SaveGame);
            _mainMenuButton.onClick.AddListener(ReturnToMainMenu);
            _quitButton.onClick.AddListener(QuitGame);

            _pausePanel.SetActive(false);
            if (_saveConfirmText != null) _saveConfirmText.gameObject.SetActive(false);
        }

        void Update()
        {
            if (Input.GetKeyDown(KeyCode.Escape))
                Toggle();

            if (_saveConfirmTimer > 0)
            {
                _saveConfirmTimer -= Time.unscaledDeltaTime;
                if (_saveConfirmTimer <= 0 && _saveConfirmText != null)
                    _saveConfirmText.gameObject.SetActive(false);
            }
        }

        // ── Controls ──────────────────────────────────────────

        public void Toggle()
        {
            // Block pausing during boss fight cutscenes or game over
            var state = GameManager.Instance.CurrentState;
            if (state == GameState.GameOver || state == GameState.Cutscene) return;

            if (_isPaused) Resume(); else Pause();
        }

        public void Pause()
        {
            _isPaused = true;
            _pausePanel.SetActive(true);
            GameManager.Instance.ChangeState(GameState.Paused);
        }

        public void Resume()
        {
            _isPaused = false;
            _pausePanel.SetActive(false);
            GameManager.Instance.ChangeState(GameState.Sailing);
        }

        private void SaveGame()
        {
            SaveManager.Instance?.SaveGame(0);  // Auto-save slot

            if (_saveConfirmText != null)
            {
                _saveConfirmText.text = "Game Saved!";
                _saveConfirmText.gameObject.SetActive(true);
                _saveConfirmTimer = _saveConfirmDisplayTime;
            }
        }

        private void ReturnToMainMenu()
        {
            _isPaused = false;
            Time.timeScale = 1f;
            SceneLoader.Instance.UnloadScene("Ocean_World");
            SceneLoader.Instance.LoadSceneAdditive("MainMenu");
            GameManager.Instance.ChangeState(GameState.MainMenu);
        }

        private void QuitGame() => GameManager.Instance.QuitGame();
    }
}
