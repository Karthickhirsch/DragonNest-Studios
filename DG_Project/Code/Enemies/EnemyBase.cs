using System.Collections;
using UnityEngine;
using UnityEngine.AI;
using IsleTrial.Data;
using IsleTrial.Player;

namespace IsleTrial.Enemies
{
    /// <summary>
    /// Base class for all on-island enemies.
    /// Requires NavMeshAgent. Extend this for each enemy type.
    /// Attach derived scripts to enemy prefabs (not this class directly).
    /// </summary>
    [RequireComponent(typeof(NavMeshAgent))]
    [RequireComponent(typeof(Animator))]
    public abstract class EnemyBase : MonoBehaviour, IDamageable
    {
        [Header("Data")]
        [SerializeField] protected EnemyData _data;

        [Header("Detection")]
        [SerializeField] protected float _detectionRadius = 8f;
        [SerializeField] protected float _attackRadius = 2f;
        [SerializeField] protected LayerMask _playerLayer;

        [Header("Patrol")]
        [SerializeField] protected Transform[] _patrolWaypoints;

        // ── Components ────────────────────────────────────────
        protected NavMeshAgent _agent;
        protected Animator _animator;
        protected StateMachine _stateMachine;
        protected Transform _playerTransform;

        // ── State ─────────────────────────────────────────────
        public int CurrentHP { get; protected set; }
        public bool IsDead { get; protected set; }
        public bool IsStunned { get; protected set; }

        // ── Animator Hashes ───────────────────────────────────
        protected static readonly int HashWalk = Animator.StringToHash("Walk");
        protected static readonly int HashAttack = Animator.StringToHash("Attack");
        protected static readonly int HashStun = Animator.StringToHash("Stun");
        protected static readonly int HashDead = Animator.StringToHash("Dead");

        protected virtual void Awake()
        {
            _agent = GetComponent<NavMeshAgent>();
            _animator = GetComponent<Animator>();

            if (_data != null)
            {
                CurrentHP = _data.MaxHealth;
                _agent.speed = _data.MoveSpeed;
            }
        }

        protected virtual void Start()
        {
            _playerTransform = FindObjectOfType<PlayerController>()?.transform;
            _stateMachine = new StateMachine();
            _stateMachine.Initialize(CreateIdleState());
        }

        protected virtual void Update()
        {
            if (IsDead || IsStunned) return;
            _stateMachine.Update();
        }

        // ── Abstract Factory for States ───────────────────────

        protected abstract IState CreateIdleState();
        protected abstract IState CreateAlertState();
        protected abstract IState CreateAttackState();

        // ── IDamageable ───────────────────────────────────────

        public virtual void TakeDamage(int damage)
        {
            if (IsDead) return;
            CurrentHP -= damage;
            SpawnHitVFX();
            if (CurrentHP <= 0) StartCoroutine(DieRoutine());
        }

        public virtual void ApplyStun(float duration)
        {
            if (IsDead) return;
            StartCoroutine(StunRoutine(duration));
        }

        // ── Utilities ─────────────────────────────────────────

        public bool PlayerInDetectionRange()
        {
            if (_playerTransform == null) return false;
            return Vector3.Distance(transform.position, _playerTransform.position) <= _detectionRadius;
        }

        public bool PlayerInAttackRange()
        {
            if (_playerTransform == null) return false;
            return Vector3.Distance(transform.position, _playerTransform.position) <= _attackRadius;
        }

        // ── Coroutines ────────────────────────────────────────

        private IEnumerator DieRoutine()
        {
            IsDead = true;
            _agent.isStopped = true;
            _animator.SetTrigger(HashDead);
            if (_data != null && _data.DeathVFX != null)
                Instantiate(_data.DeathVFX, transform.position, Quaternion.identity);
            yield return new WaitForSeconds(2f);
            Destroy(gameObject);
        }

        private IEnumerator StunRoutine(float duration)
        {
            IsStunned = true;
            _agent.isStopped = true;
            _animator.SetTrigger(HashStun);
            yield return new WaitForSeconds(duration);
            IsStunned = false;
            _agent.isStopped = false;
        }

        private void SpawnHitVFX()
        {
            // Spawn from pool later — for now just log
            Debug.Log($"[Enemy] {name} took damage. HP: {CurrentHP}");
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, _detectionRadius);
            Gizmos.color = Color.red;
            Gizmos.DrawWireSphere(transform.position, _attackRadius);
        }
    }
}
