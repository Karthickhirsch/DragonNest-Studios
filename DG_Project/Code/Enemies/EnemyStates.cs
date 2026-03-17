using UnityEngine;
using UnityEngine.AI;

namespace IsleTrial.Enemies
{
    /// <summary>
    /// Idle/Patrol state: enemy walks between waypoints.
    /// </summary>
    public class EnemyIdleState : IState
    {
        private readonly EnemyBase _enemy;
        private readonly NavMeshAgent _agent;
        private readonly Transform[] _waypoints;
        private int _waypointIndex;

        public EnemyIdleState(EnemyBase enemy, NavMeshAgent agent, Transform[] waypoints)
        {
            _enemy = enemy;
            _agent = agent;
            _waypoints = waypoints;
        }

        public void Enter()
        {
            _agent.isStopped = false;
            GoToNextWaypoint();
        }

        public void Execute()
        {
            if (_enemy.PlayerInDetectionRange())
            {
                // Handled externally by enemy subclass
                return;
            }

            if (_waypoints == null || _waypoints.Length == 0) return;
            if (_agent.remainingDistance < 0.5f) GoToNextWaypoint();
        }

        public void Exit() { }

        private void GoToNextWaypoint()
        {
            if (_waypoints == null || _waypoints.Length == 0) return;
            _agent.SetDestination(_waypoints[_waypointIndex].position);
            _waypointIndex = (_waypointIndex + 1) % _waypoints.Length;
        }
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Alert state: enemy has spotted the player and chases them.
    /// </summary>
    public class EnemyAlertState : IState
    {
        private readonly EnemyBase _enemy;
        private readonly NavMeshAgent _agent;
        private Transform _player;

        public EnemyAlertState(EnemyBase enemy, NavMeshAgent agent, Transform player)
        {
            _enemy = enemy;
            _agent = agent;
            _player = player;
        }

        public void Enter() => _agent.isStopped = false;

        public void Execute()
        {
            if (_player != null) _agent.SetDestination(_player.position);
        }

        public void Exit() { }
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Attack state: enemy is in range and executing an attack.
    /// Override ExecuteAttack in each subclass for unique behavior.
    /// </summary>
    public class EnemyAttackState : IState
    {
        private readonly EnemyBase _enemy;
        private readonly NavMeshAgent _agent;
        private readonly Animator _animator;
        private readonly System.Action _attackCallback;
        private float _attackTimer;
        private readonly float _attackCooldown;

        private static readonly int HashAttack = Animator.StringToHash("Attack");

        public EnemyAttackState(EnemyBase enemy, NavMeshAgent agent,
            Animator animator, System.Action attackCallback, float cooldown = 1.5f)
        {
            _enemy = enemy;
            _agent = agent;
            _animator = animator;
            _attackCallback = attackCallback;
            _attackCooldown = cooldown;
        }

        public void Enter()
        {
            _agent.isStopped = true;
            _attackTimer = 0f;
        }

        public void Execute()
        {
            _attackTimer -= Time.deltaTime;
            if (_attackTimer <= 0f)
            {
                _animator.SetTrigger(HashAttack);
                _attackCallback?.Invoke();
                _attackTimer = _attackCooldown;
            }
        }

        public void Exit() => _agent.isStopped = false;
    }
}
