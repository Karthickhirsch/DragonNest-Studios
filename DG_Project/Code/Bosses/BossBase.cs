using System.Collections;
using UnityEngine;
using IsleTrial.Core;
using IsleTrial.Data;

namespace IsleTrial.Bosses
{
    public enum BossPhase { Phase1, Phase2, Phase3 }

    /// <summary>
    /// Base class for all island bosses.
    /// Extend this for each specific boss (Ignar, Kryss, etc.).
    /// Attach derived boss scripts to boss prefabs.
    /// </summary>
    public abstract class BossBase : MonoBehaviour, IDamageable
    {
        [Header("Boss Data")]
        [SerializeField] protected BossData _data;

        [Header("Phase Thresholds (% HP)")]
        [SerializeField] protected float _phase2Threshold = 0.6f;
        [SerializeField] protected float _phase3Threshold = 0.3f;

        [Header("VFX")]
        [SerializeField] protected ParticleSystem _phaseTransitionVFX;
        [SerializeField] protected ParticleSystem _deathVFX;

        // ── State ─────────────────────────────────────────────
        public int CurrentHP { get; protected set; }
        public BossPhase CurrentPhase { get; protected set; }
        public bool IsDead { get; protected set; }
        public bool IsInvulnerable { get; protected set; }

        protected Animator _animator;
        protected float _attackTimer;

        // ── Animator Hashes ───────────────────────────────────
        protected static readonly int HashPhase = Animator.StringToHash("Phase");
        protected static readonly int HashDead = Animator.StringToHash("Dead");
        protected static readonly int HashHit = Animator.StringToHash("Hit");

        protected virtual void Awake()
        {
            _animator = GetComponent<Animator>();
            if (_data != null) CurrentHP = _data.MaxHealth;
        }

        protected virtual void Start()
        {
            CurrentPhase = BossPhase.Phase1;
            GameEvents.BossEncountered(_data);
            GameEvents.BossHealthChanged(CurrentHP, _data != null ? _data.MaxHealth : 1);
            EnterPhase(BossPhase.Phase1);
        }

        protected virtual void Update()
        {
            if (IsDead) return;
            CheckPhaseTransition();

            _attackTimer -= Time.deltaTime;
            if (_attackTimer <= 0) ExecuteAttackPattern();
        }

        // ── Phase Management ──────────────────────────────────

        private void CheckPhaseTransition()
        {
            if (_data == null) return;
            float pct = (float)CurrentHP / _data.MaxHealth;

            if (CurrentPhase == BossPhase.Phase1 && pct <= _phase2Threshold)
                StartCoroutine(TransitionToPhase(BossPhase.Phase2));
            else if (CurrentPhase == BossPhase.Phase2 && pct <= _phase3Threshold)
                StartCoroutine(TransitionToPhase(BossPhase.Phase3));
        }

        private IEnumerator TransitionToPhase(BossPhase newPhase)
        {
            // Brief invulnerability during transition
            IsInvulnerable = true;
            if (_phaseTransitionVFX != null) _phaseTransitionVFX.Play();
            _animator.SetInteger(HashPhase, (int)newPhase);
            yield return new WaitForSeconds(2f);
            CurrentPhase = newPhase;
            IsInvulnerable = false;
            EnterPhase(newPhase);
        }

        // ── Abstract Methods (implement per boss) ─────────────

        protected abstract void EnterPhase(BossPhase phase);
        protected abstract void ExecuteAttackPattern();

        // ── IDamageable ───────────────────────────────────────

        public virtual void TakeDamage(int damage)
        {
            if (IsDead || IsInvulnerable) return;
            CurrentHP = Mathf.Max(0, CurrentHP - damage);

            _animator.SetTrigger(HashHit);
            GameEvents.BossHealthChanged(CurrentHP, _data != null ? _data.MaxHealth : 1);

            if (CurrentHP <= 0) StartCoroutine(DieRoutine());
        }

        // ── Death ─────────────────────────────────────────────

        private IEnumerator DieRoutine()
        {
            IsDead = true;
            IsInvulnerable = true;
            _animator.SetTrigger(HashDead);
            if (_deathVFX != null) _deathVFX.Play();

            yield return new WaitForSeconds(3f);

            GameEvents.BossDefeated(_data);
            if (_data != null && _data.UnlockedAbility != null)
                GameEvents.AbilityUnlocked(_data.UnlockedAbility);

            OnBossDefeated();
            Destroy(gameObject, 1f);
        }

        protected virtual void OnBossDefeated()
        {
            // Override in subclasses for crystal spawn, door open, etc.
        }
    }
}
