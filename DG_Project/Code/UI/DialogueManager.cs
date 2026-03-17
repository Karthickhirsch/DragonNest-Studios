using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using IsleTrial.Data;

namespace IsleTrial.UI
{
    /// <summary>
    /// Shows NPC and environmental dialogue lines.
    /// Attach to the DialoguePanel UI GameObject.
    /// Assign all UI element references in the Inspector.
    /// </summary>
    public class DialogueManager : MonoBehaviour
    {
        public static DialogueManager Instance { get; private set; }

        [Header("UI References")]
        [SerializeField] private GameObject _dialoguePanel;
        [SerializeField] private TextMeshProUGUI _speakerNameText;
        [SerializeField] private TextMeshProUGUI _bodyText;
        [SerializeField] private Image _speakerPortrait;
        [SerializeField] private GameObject _continueIndicator;

        [Header("Typewriter Effect")]
        [SerializeField] private float _charDelay = 0.03f;

        private bool _isPlaying;
        private bool _skipRequested;

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        void Start()
        {
            if (_dialoguePanel != null) _dialoguePanel.SetActive(false);
        }

        // ── Public API ────────────────────────────────────────

        public void StartDialogue(DialogueSequence sequence, System.Action onComplete = null)
        {
            if (_isPlaying) return;
            StartCoroutine(PlaySequence(sequence, onComplete));
        }

        public void Skip()
        {
            _skipRequested = true;
        }

        // ── Coroutines ────────────────────────────────────────

        private IEnumerator PlaySequence(DialogueSequence sequence, System.Action onComplete)
        {
            _isPlaying = true;
            if (_dialoguePanel != null) _dialoguePanel.SetActive(true);

            foreach (var line in sequence.Lines)
            {
                yield return StartCoroutine(ShowLine(line));
                // Wait for player to press E/A/continue
                if (_continueIndicator != null) _continueIndicator.SetActive(true);
                yield return new WaitUntil(() => _skipRequested);
                _skipRequested = false;
                if (_continueIndicator != null) _continueIndicator.SetActive(false);
            }

            if (_dialoguePanel != null) _dialoguePanel.SetActive(false);
            _isPlaying = false;
            onComplete?.Invoke();
        }

        private IEnumerator ShowLine(DialogueLine line)
        {
            if (_speakerNameText != null) _speakerNameText.text = line.SpeakerName;
            if (_speakerPortrait != null)
            {
                _speakerPortrait.enabled = line.SpeakerPortrait != null;
                _speakerPortrait.sprite = line.SpeakerPortrait;
            }

            if (_bodyText != null)
            {
                _bodyText.text = string.Empty;
                foreach (char c in line.Text)
                {
                    _bodyText.text += c;
                    if (_skipRequested)
                    {
                        _bodyText.text = line.Text;
                        _skipRequested = false;
                        break;
                    }
                    yield return new WaitForSecondsRealtime(_charDelay);
                }
            }
        }
    }
}
