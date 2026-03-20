using System.Collections;
using UnityEngine;
using IsleTrial.Player;

namespace IsleTrial.Enemies
{
    /// <summary>
    /// Frost Isle enemy: a slow, armoured slug that slows the player on hit.
    /// On death: leaves a frost patch that applies further slow to nearby players.
    /// Attach to the FrostSlug prefab.
    /// </summary>
    public class FrostSlug : EnemyBase
    {
        [Header("Frost Slug")]
        [SerializeField] private float _slowMultiplier = 0.5f;   // 0.5 = half speed
        [SerializeField] private float _slowDuration = 3f;
        [SerializeField] private int _armorPoints = 2;           // absorbed hits before taking real damage

        [Header("Frost Patch On Death")]
        [SerializeField] private GameObject _frostPatchPrefab;
        [SerializeField] private float _frostPatchDuration = 6f;

        [Header("VFX")]
        [SerializeField] private ParticleSystem _hitIceVFX;
        [SerializeField] private ParticleSystem _deathFrostVFX;

        private int _remainingArmor;
        private static readonly int HashFrostAttack = Animator.StringToHash("Attack");

        protected override void Awake()
        {
            base.Awake();
            _remainingArmor = _armorPoints;
        }

        protected override void Update()
        {
            base.Update();
            if (IsDead || IsStunned) return;

            if (PlayerInAttackRange())
                _stateMachine.ChangeState(CreateAttackState());
            else if (PlayerInDetectionRange())
                _stateMachine.ChangeState(CreateAlertState());
            else if (!(_stateMachine.CurrentState is EnemyIdleState))
                _stateMachine.ChangeState(CreateIdleState());
        }

        protected override IState CreateIdleState()
            => new EnemyIdleState(this, _agent, _patrolWaypoints);

        protected override IState CreateAlertState()
            => new EnemyAlertState(this, _agent, _playerTransform);

        protected override IState CreateAttackState()
            => new EnemyAttackState(this, _agent, _animator, FrostAttack, 2.5f);

        // ── Frost Attack ──────────────────────────────────────

        private void FrostAttack()
        {
            if (_playerTransform == null || !PlayerInAttackRange()) return;

            _animator.SetTrigger(HashFrostAttack);

            if (_playerTransform.TryGetComponent<PlayerStats>(out var stats))
            {
                stats.TakeDamage(_data != null ? _data.AttackDamage : 10);
                StartCoroutine(SlowRoutine(stats));
            }
        }

        private IEnumerator SlowRoutine(PlayerStats stats)
        {
            stats.ApplySpeedModifier(_slowMultiplier);
            yield return new WaitForSeconds(_slowDuration);
            if (stats != null) stats.ResetSpeedModifier();
        }

        // ── IDamageable Override (armor absorption) ───────────

        public override void TakeDamage(int damage)
        {
            if (_remainingArmor > 0)
            {
                _remainingArmor--;
                if (_hitIceVFX != null) _hitIceVFX.Play();
                Debug.Log($"[FrostSlug] Armor absorbed hit. Armor left: {_remainingArmor}");
                return;
            }
            base.TakeDamage(damage);
        }

        // ── Death: spawn frost patch ──────────────────────────

        void OnDestroy()
        {
            if (!IsDead) return;

            if (_deathFrostVFX != null)
                Instantiate(_deathFrostVFX, transform.position, Quaternion.identity);

            if (_frostPatchPrefab != null)
            {
                var patch = Instantiate(_frostPatchPrefab, transform.position, Quaternion.identity);
                Destroy(patch, _frostPatchDuration);
            }
        }

        new void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, _detectionRadius);
            Gizmos.color = Color.cyan;
            Gizmos.DrawWireSphere(transform.position, _attackRadius);
        }
    }
}
