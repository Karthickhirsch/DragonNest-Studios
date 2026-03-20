using UnityEngine;
using UnityEngine.UI;
using TMPro;
using IsleTrial.Core;
using IsleTrial.SaveSystem;

namespace IsleTrial.UI
{
    /// <summary>
    /// Controls the main menu screen: Play, Continue, Quit buttons.
    /// Attach to the root panel of the MainMenu Canvas.
    /// Requires SaveManager and SceneLoader in the Bootstrap scene.
    /// </summary>
    public class MainMenuController : MonoBehaviour
    {
        [Header("Panels")]
        [SerializeField] private GameObject _mainPanel;
        [SerializeField] private GameObject _saveSlotPanel;

        [Header("Buttons")]
        [SerializeField] private Button _newGameButton;
        [SerializeField] private Button _continueButton;
        [SerializeField] private Button _loadButton;
        [SerializeField] private Button _quitButton;

        [Header("Save Slot Buttons")]
        [SerializeField] private Button _slot1Button;
        [SerializeField] private Button _slot2Button;
        [SerializeField] private Button _slot3Button;
        [SerializeField] private TextMeshProUGUI _slot1Label;
        [SerializeField] private TextMeshProUGUI _slot2Label;
        [SerializeField] private TextMeshProUGUI _slot3Label;

        [Header("Version Text")]
        [SerializeField] private TextMeshProUGUI _versionText;

        void Start()
        {
            if (_versionText != null)
                _versionText.text = $"v{Application.version}";

            _newGameButton.onClick.AddListener(OnNewGame);
            _continueButton.onClick.AddListener(OnContinue);
            _loadButton.onClick.AddListener(OnOpenLoadPanel);
            _quitButton.onClick.AddListener(OnQuit);

            _slot1Button.onClick.AddListener(() => OnLoadSlot(1));
            _slot2Button.onClick.AddListener(() => OnLoadSlot(2));
            _slot3Button.onClick.AddListener(() => OnLoadSlot(3));

            RefreshSaveSlotLabels();
            _saveSlotPanel.SetActive(false);

            // Continue is only available if auto-save slot exists
            bool hasSave = SaveManager.Instance != null && SaveManager.Instance.LoadGame(0) != null;
            _continueButton.interactable = hasSave;
        }

        // ── Button Handlers ───────────────────────────────────

        private void OnNewGame()
        {
            GameManager.Instance.ChangeState(GameState.Sailing);
            SceneLoader.Instance.LoadSceneAdditive("Ocean_World");
        }

        private void OnContinue()
        {
            var data = SaveManager.Instance.LoadGame(0);
            if (data == null) return;
            SaveManager.Instance.ApplySaveData(data);
            GameManager.Instance.ChangeState(GameState.Sailing);
            SceneLoader.Instance.LoadSceneAdditive("Ocean_World");
        }

        private void OnOpenLoadPanel()
        {
            _mainPanel.SetActive(false);
            _saveSlotPanel.SetActive(true);
        }

        private void OnLoadSlot(int slot)
        {
            var data = SaveManager.Instance.LoadGame(slot);
            if (data == null)
            {
                Debug.Log($"[MainMenu] No save in slot {slot}.");
                return;
            }
            SaveManager.Instance.ApplySaveData(data);
            GameManager.Instance.ChangeState(GameState.Sailing);
            SceneLoader.Instance.LoadSceneAdditive("Ocean_World");
        }

        private void OnQuit() => GameManager.Instance.QuitGame();

        // ── Save Slot Labels ──────────────────────────────────

        private void RefreshSaveSlotLabels()
        {
            SetSlotLabel(_slot1Label, 1);
            SetSlotLabel(_slot2Label, 2);
            SetSlotLabel(_slot3Label, 3);
        }

        private void SetSlotLabel(TextMeshProUGUI label, int slot)
        {
            if (label == null) return;
            var data = SaveManager.Instance != null ? SaveManager.Instance.LoadGame(slot) : null;
            label.text = data != null ? $"Slot {slot}  —  {data.SaveTimestamp}" : $"Slot {slot}  —  Empty";
        }

        public void OnBackFromLoadPanel()
        {
            _saveSlotPanel.SetActive(false);
            _mainPanel.SetActive(true);
        }
    }
}
