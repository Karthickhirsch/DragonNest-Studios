using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using IsleTrial.Core;

namespace IsleTrial.UI
{
    /// <summary>
    /// Boss health bar that slides in when a boss encounter starts.
    /// Attach to a UI Canvas child panel named "BossHealthBarPanel".
    /// Assign all references in the Inspector.
    /// </summary>
    public class BossHealthBarUI : MonoBehaviour
    {
        [Header("Panel")]
        [SerializeField] private CanvasGroup _panelGroup;
        [SerializeField] private RectTransform _panelRect;

        [Header("Bar")]
        [SerializeField] private Image _healthFill;
        [SerializeField] private Image _healthDamageFill;   // Red lag bar behind main fill
        [SerializeField] private TextMeshProUGUI _bossNameText;
        [SerializeField] private TextMeshProUGUI _phaseText;

        [Header("Animation")]
        [SerializeField] private float _slideInDuration = 0.5f;
        [SerializeField] private float _damageFillLagSpeed = 1.5f;

        private float _targetFill;
        private Coroutine _slideCoroutine;

        void OnEnable()
        {
            GameEvents.OnBossEncountered += OnBossEncountered;
            GameEvents.OnBossHealthChanged += OnBossHealthChanged;
            GameEvents.OnBossDefeated += OnBossDefeated;
        }

        void OnDisable()
        {
            GameEvents.OnBossEncountered -= OnBossEncountered;
            GameEvents.OnBossHealthChanged -= OnBossHealthChanged;
            GameEvents.OnBossDefeated -= OnBossDefeated;
        }

        void Start()
        {
            if (_panelGroup != null) _panelGroup.alpha = 0f;
        }

        void Update()
        {
            // Lag fill slowly follows main fill
            if (_healthDamageFill != null && _healthFill != null)
            {
                _healthDamageFill.fillAmount = Mathf.MoveTowards(
                    _healthDamageFill.fillAmount,
                    _healthFill.fillAmount,
                    _damageFillLagSpeed * Time.deltaTime
                );
            }
        }

        private void OnBossEncountered(Data.BossData boss)
        {
            if (_bossNameText != null) _bossNameText.text = boss.BossName;
            if (_healthFill != null) _healthFill.fillAmount = 1f;
            if (_healthDamageFill != null) _healthDamageFill.fillAmount = 1f;
            if (_phaseText != null) _phaseText.text = "Phase I";

            if (_slideCoroutine != null) StopCoroutine(_slideCoroutine);
            _slideCoroutine = StartCoroutine(SlideIn());
        }

        private void OnBossHealthChanged(float current, float max)
        {
            _targetFill = max > 0 ? current / max : 0f;
            if (_healthFill != null) _healthFill.fillAmount = _targetFill;
        }

        private void OnBossDefeated(Data.BossData boss)
        {
            if (_slideCoroutine != null) StopCoroutine(_slideCoroutine);
            _slideCoroutine = StartCoroutine(SlideOut());
        }

        private IEnumerator SlideIn()
        {
            float t = 0;
            while (t < 1f)
            {
                t += Time.deltaTime / _slideInDuration;
                if (_panelGroup != null) _panelGroup.alpha = Mathf.Lerp(0, 1, t);
                yield return null;
            }
        }

        private IEnumerator SlideOut()
        {
            float t = 0;
            while (t < 1f)
            {
                t += Time.deltaTime / _slideInDuration;
                if (_panelGroup != null) _panelGroup.alpha = Mathf.Lerp(1, 0, t);
                yield return null;
            }
        }

        public void SetPhaseText(string phase)
        {
            if (_phaseText != null) _phaseText.text = phase;
        }
    }
}
