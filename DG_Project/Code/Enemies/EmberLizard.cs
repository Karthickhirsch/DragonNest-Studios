using UnityEngine;
using UnityEngine.AI;
using IsleTrial.Player;

namespace IsleTrial.Enemies
{
    /// <summary>
    /// Ember Isle enemy: charges the player and explodes on death.
    /// Example of how to extend EnemyBase.
    /// Attach to the EmberLizard prefab.
    /// </summary>
    public class EmberLizard : EnemyBase
    {
        [Header("Lizard Specific")]
        [SerializeField] private float _explosionRadius = 2f;
        [SerializeField] private float _explosionDamage = 30f;
        [SerializeField] private ParticleSystem _explosionVFX;
        [SerializeField] private LayerMask _playerLayer;

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
            => new EnemyAttackState(this, _agent, _animator, ChargeAndExplode, 2f);

        private void ChargeAndExplode()
        {
            if (_playerTransform == null) return;
            _agent.SetDestination(_playerTransform.position);

            if (Vector3.Distance(transform.position, _playerTransform.position) < 1f)
                TakeDamage(CurrentHP + 1); // Force death → triggers explosion
        }

        public override void TakeDamage(int damage)
        {
            base.TakeDamage(damage);
            if (CurrentHP <= 0) Explode();
        }

        private void Explode()
        {
            if (_explosionVFX != null) Instantiate(_explosionVFX, transform.position, Quaternion.identity);

            Collider[] hits = Physics.OverlapSphere(transform.position, _explosionRadius, _playerLayer);
            foreach (var hit in hits)
                if (hit.TryGetComponent<PlayerStats>(out var stats))
                    stats.TakeDamage(Mathf.RoundToInt(_explosionDamage));
        }

        void OnDrawGizmosSelected()
        {
            base.OnDrawGizmosSelected();
            Gizmos.color = Color.magenta;
            Gizmos.DrawWireSphere(transform.position, _explosionRadius);
        }

        // Workaround: base class has private OnDrawGizmosSelected
        private void OnDrawGizmosSelected2() { }
    }
}
