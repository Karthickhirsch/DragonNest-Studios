using UnityEngine;
using IsleTrial.Core;

namespace IsleTrial.Player
{
    /// <summary>
    /// Main on-island player controller.
    /// Requires: CharacterController, PlayerStats, PlayerInputHandler, Animator.
    /// Attach all four components to the Player GameObject.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    [RequireComponent(typeof(PlayerStats))]
    [RequireComponent(typeof(PlayerInputHandler))]
    [RequireComponent(typeof(Animator))]
    public class PlayerController : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Transform _cameraTransform;
        [SerializeField] private LayerMask _interactLayer;
        [SerializeField] private float _interactRange = 2f;

        [Header("Combat")]
        [SerializeField] private Transform _attackHitPoint;
        [SerializeField] private float _attackRadius = 1f;
        [SerializeField] private LayerMask _enemyLayer;
        [SerializeField] private float _chargeTimeRequired = 1.5f;
        [SerializeField] private ParticleSystem _chargedAttackVFX;

        // ── Components ────────────────────────────────────────
        private CharacterController _cc;
        private PlayerStats _stats;
        private PlayerInputHandler _input;
        private Animator _animator;

        // ── State ─────────────────────────────────────────────
        private Vector3 _velocity;
        private bool _isDodging;
        private float _dodgeTimer;
        private Vector3 _dodgeDirection;

        private bool _isAttacking;
        private float _attackTimer;
        private float _chargeTimer;
        private bool _isChargingAttack;

        private bool _isDead;

        // ── Animator Hashes ───────────────────────────────────
        private static readonly int HashSpeed = Animator.StringToHash("Speed");
        private static readonly int HashAttack = Animator.StringToHash("Attack");
        private static readonly int HashChargedAttack = Animator.StringToHash("ChargedAttack");
        private static readonly int HashDodge = Animator.StringToHash("Dodge");
        private static readonly int HashDead = Animator.StringToHash("Dead");

        void Awake()
        {
            _cc = GetComponent<CharacterController>();
            _stats = GetComponent<PlayerStats>();
            _input = GetComponent<PlayerInputHandler>();
            _animator = GetComponent<Animator>();
        }

        void OnEnable() => GameEvents.OnPlayerDied += OnDied;
        void OnDisable() => GameEvents.OnPlayerDied -= OnDied;

        void Update()
        {
            if (_isDead) return;
            HandleGravity();
            HandleDodge();
            if (!_isDodging && !_isAttacking)
            {
                HandleMovement();
                HandleChargeAttack();
            }
            if (!_isAttacking) HandleQuickAttack();
            HandleInteract();
        }

        // ── Movement ──────────────────────────────────────────

        private void HandleMovement()
        {
            Vector2 raw = _input.MoveInput;
            if (raw.sqrMagnitude < 0.01f)
            {
                _animator.SetFloat(HashSpeed, 0f);
                return;
            }

            Vector3 camForward = Vector3.ProjectOnPlane(_cameraTransform.forward, Vector3.up).normalized;
            Vector3 camRight = Vector3.ProjectOnPlane(_cameraTransform.right, Vector3.up).normalized;
            Vector3 moveDir = (camForward * raw.y + camRight * raw.x).normalized;

            float speed = _stats.MoveSpeed * (_input.SprintHeld ? _stats.SprintMultiplier : 1f);
            _cc.Move(moveDir * speed * Time.deltaTime);

            transform.rotation = Quaternion.Slerp(transform.rotation,
                Quaternion.LookRotation(moveDir), 15f * Time.deltaTime);

            _animator.SetFloat(HashSpeed, _input.SprintHeld ? 1f : 0.5f);
        }

        // ── Dodge ─────────────────────────────────────────────

        private void HandleDodge()
        {
            if (_input.DodgePressed && !_isDodging && _stats.CanDodge())
            {
                _isDodging = true;
                _dodgeTimer = _stats.DodgeDuration;
                _stats.ConsumeDodgeStamina();
                _dodgeDirection = _input.MoveInput.sqrMagnitude > 0.01f
                    ? transform.forward
                    : -transform.forward;
                _animator.SetTrigger(HashDodge);
            }

            if (_isDodging)
            {
                _dodgeTimer -= Time.deltaTime;
                _cc.Move(_dodgeDirection * _stats.DodgeSpeed * Time.deltaTime);
                if (_dodgeTimer <= 0) _isDodging = false;
            }
        }

        // ── Attack ────────────────────────────────────────────

        private void HandleQuickAttack()
        {
            if (!_input.AttackPressed || _isChargingAttack) return;
            _isAttacking = true;
            _attackTimer = 0.4f;
            _animator.SetTrigger(HashAttack);
            DealDamage(_stats.AttackDamage);
        }

        private void HandleChargeAttack()
        {
            if (_input.AttackHeld)
            {
                _chargeTimer += Time.deltaTime;
                _isChargingAttack = _chargeTimer >= _chargeTimeRequired;
                if (_isChargingAttack && _chargedAttackVFX != null && !_chargedAttackVFX.isPlaying)
                    _chargedAttackVFX.Play();
            }
            else if (_isChargingAttack)
            {
                _isAttacking = true;
                _attackTimer = 0.6f;
                _animator.SetTrigger(HashChargedAttack);
                DealDamage(_stats.AttackDamage * _stats.ChargedAttackMultiplier);
                _chargeTimer = 0;
                _isChargingAttack = false;
                if (_chargedAttackVFX != null) _chargedAttackVFX.Stop();
            }
            else
            {
                _chargeTimer = 0;
                _isChargingAttack = false;
            }

            if (_isAttacking)
            {
                _attackTimer -= Time.deltaTime;
                if (_attackTimer <= 0) _isAttacking = false;
            }
        }

        private void DealDamage(float damage)
        {
            Collider[] hits = Physics.OverlapSphere(_attackHitPoint.position, _attackRadius, _enemyLayer);
            foreach (var hit in hits)
            {
                if (hit.TryGetComponent<IDamageable>(out var damageable))
                    damageable.TakeDamage(Mathf.RoundToInt(damage));
            }
        }

        // ── Interact ──────────────────────────────────────────

        private void HandleInteract()
        {
            if (!_input.InteractPressed) return;
            if (Physics.SphereCast(transform.position, 0.5f, transform.forward,
                out RaycastHit hit, _interactRange, _interactLayer))
            {
                if (hit.collider.TryGetComponent<IInteractable>(out var interactable))
                    interactable.Interact(this);
            }
        }

        // ── Gravity ───────────────────────────────────────────

        private void HandleGravity()
        {
            if (_cc.isGrounded && _velocity.y < 0) _velocity.y = -2f;
            _velocity.y += Physics.gravity.y * Time.deltaTime;
            _cc.Move(_velocity * Time.deltaTime);
        }

        // ── Death ─────────────────────────────────────────────

        private void OnDied()
        {
            _isDead = true;
            _animator.SetTrigger(HashDead);
            _input.DisableAll();
        }

        void OnDrawGizmosSelected()
        {
            if (_attackHitPoint == null) return;
            Gizmos.color = Color.red;
            Gizmos.DrawWireSphere(_attackHitPoint.position, _attackRadius);
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, _interactRange);
        }
    }
}
