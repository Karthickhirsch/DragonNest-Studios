using UnityEngine;
using IsleTrial.Data;
using IsleTrial.UI;

namespace IsleTrial.World
{
    /// <summary>
    /// NPC that the player can interact with to trigger dialogue.
    /// Implements IInteractable — PlayerController calls Interact() on press E.
    /// Optionally shows a floating indicator (! or ?) above the NPC's head.
    /// Attach to any NPC prefab alongside a Collider (isTrigger = false).
    /// </summary>
    public class NPC : MonoBehaviour, IInteractable
    {
        [Header("Dialogue")]
        [SerializeField] private DialogueSequence _dialogue;
        [SerializeField] private bool _repeatDialogue = false;

        [Header("Indicator")]
        [SerializeField] private GameObject _interactIndicator;   // "!" sprite above head
        [SerializeField] private float _indicatorBobSpeed = 1.5f;
        [SerializeField] private float _indicatorBobHeight = 0.08f;

        [Header("Face Player")]
        [SerializeField] private bool _facePlayerOnInteract = true;

        private bool _hasSpoken;
        private Vector3 _indicatorStartLocalPos;

        void Start()
        {
            if (_interactIndicator != null)
            {
                _indicatorStartLocalPos = _interactIndicator.transform.localPosition;
                _interactIndicator.SetActive(true);
            }
        }

        void Update()
        {
            if (_interactIndicator == null || !_interactIndicator.activeSelf) return;

            float newY = _indicatorStartLocalPos.y
                + Mathf.Sin(Time.time * _indicatorBobSpeed) * _indicatorBobHeight;
            _interactIndicator.transform.localPosition = new Vector3(
                _indicatorStartLocalPos.x, newY, _indicatorStartLocalPos.z);
        }

        // ── IInteractable ─────────────────────────────────────

        public void Interact(object interactor)
        {
            if (_hasSpoken && !_repeatDialogue) return;
            if (_dialogue == null)
            {
                Debug.LogWarning($"[NPC] {name}: No DialogueSequence assigned.");
                return;
            }

            if (_facePlayerOnInteract && interactor is Component comp)
            {
                Vector3 dir = (comp.transform.position - transform.position).normalized;
                dir.y = 0;
                if (dir != Vector3.zero)
                    transform.rotation = Quaternion.LookRotation(dir);
            }

            _hasSpoken = true;

            if (_interactIndicator != null)
                _interactIndicator.SetActive(false);

            DialogueManager.Instance.StartDialogue(_dialogue);
        }

        // ── Public API ────────────────────────────────────────

        /// <summary>Swap dialogue at runtime (e.g. after a quest step).</summary>
        public void SetDialogue(DialogueSequence newDialogue, bool resetSpokenFlag = true)
        {
            _dialogue = newDialogue;
            if (resetSpokenFlag) _hasSpoken = false;
            if (_interactIndicator != null) _interactIndicator.SetActive(true);
        }
    }
}
