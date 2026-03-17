using System.Collections.Generic;
using UnityEngine;
using IsleTrial.Core;
using IsleTrial.Data;

namespace IsleTrial.Player
{
    /// <summary>
    /// Manages unlocked abilities and handles their activation.
    /// Attach to the Player GameObject.
    /// </summary>
    public class PlayerAbilityHandler : MonoBehaviour
    {
        [Header("Ability Slots")]
        [SerializeField] private AbilityData _activeAbility;

        [Header("Fire Dash")]
        [SerializeField] private ParticleSystem _fireDashVFX;
        [SerializeField] private float _fireDashDistance = 5f;
        [SerializeField] private float _fireDashDamage = 30f;
        [SerializeField] private LayerMask _enemyLayer;

        [Header("Ice Shield")]
        [SerializeField] private GameObject _iceShieldVisual;

        [Header("Vine Grapple")]
        [SerializeField] private LineRenderer _grappleLine;
        [SerializeField] private LayerMask _grappleLayer;
        [SerializeField] private float _grappleRange = 12f;

        [Header("Lightning Strike")]
        [SerializeField] private ParticleSystem _lightningVFX;
        [SerializeField] private float _lightningRadius = 3f;
        [SerializeField] private float _lightningDamage = 50f;

        private readonly List<AbilityData> _unlockedAbilities = new();
        private float _cooldownTimer;
        private bool _iceShieldActive;
        private CharacterController _cc;

        public bool IsOnCooldown => _cooldownTimer > 0;
        public float CooldownProgress => _activeAbility != null
            ? 1f - (_cooldownTimer / _activeAbility.Cooldown) : 1f;

        void Awake() => _cc = GetComponent<CharacterController>();

        void OnEnable() => GameEvents.OnAbilityUnlocked += OnAbilityUnlocked;
        void OnDisable() => GameEvents.OnAbilityUnlocked -= OnAbilityUnlocked;

        void Update()
        {
            if (_cooldownTimer > 0)
                _cooldownTimer -= Time.deltaTime;
        }

        // ── Unlock ────────────────────────────────────────────

        private void OnAbilityUnlocked(AbilityData ability)
        {
            if (!_unlockedAbilities.Contains(ability))
            {
                _unlockedAbilities.Add(ability);
                _activeAbility = ability;   // Auto-equip the newest ability
                Debug.Log($"[Abilities] Unlocked: {ability.AbilityName}");
            }
        }

        public void SetActiveAbility(AbilityData ability)
        {
            if (_unlockedAbilities.Contains(ability))
                _activeAbility = ability;
        }

        // ── Activation ────────────────────────────────────────

        public void ActivateAbility()
        {
            if (_activeAbility == null || IsOnCooldown) return;

            switch (_activeAbility.Type)
            {
                case AbilityType.FireDash:      UseFireDash();      break;
                case AbilityType.IceShield:     UseIceShield();     break;
                case AbilityType.VineGrapple:   UseVineGrapple();   break;
                case AbilityType.SandVeil:      UseSandVeil();      break;
                case AbilityType.LightningStrike: UseLightningStrike(); break;
            }

            _cooldownTimer = _activeAbility.Cooldown;
        }

        private void UseFireDash()
        {
            Vector3 dir = transform.forward;
            _cc.Move(dir * _fireDashDistance);
            if (_fireDashVFX != null) _fireDashVFX.Play();

            Collider[] hits = Physics.OverlapSphere(transform.position, 1.5f, _enemyLayer);
            foreach (var hit in hits)
                if (hit.TryGetComponent<IDamageable>(out var d))
                    d.TakeDamage(Mathf.RoundToInt(_fireDashDamage));
        }

        private void UseIceShield()
        {
            _iceShieldActive = !_iceShieldActive;
            if (_iceShieldVisual != null) _iceShieldVisual.SetActive(_iceShieldActive);
        }

        private void UseVineGrapple()
        {
            if (Physics.Raycast(transform.position, transform.forward,
                out RaycastHit hit, _grappleRange, _grappleLayer))
            {
                if (_grappleLine != null)
                {
                    _grappleLine.enabled = true;
                    _grappleLine.SetPosition(0, transform.position);
                    _grappleLine.SetPosition(1, hit.point);
                }
                // Lerp player toward grapple point
                StartCoroutine(GrapplePull(hit.point));
            }
        }

        private System.Collections.IEnumerator GrapplePull(Vector3 target)
        {
            float elapsed = 0f;
            float duration = 0.4f;
            Vector3 start = transform.position;
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                _cc.Move((target - transform.position).normalized * 18f * Time.deltaTime);
                yield return null;
            }
            if (_grappleLine != null) _grappleLine.enabled = false;
        }

        private void UseSandVeil()
        {
            // Trigger invisibility effect — handled by renderer tween
            StartCoroutine(SandVeilRoutine());
        }

        private System.Collections.IEnumerator SandVeilRoutine()
        {
            var renderers = GetComponentsInChildren<Renderer>();
            foreach (var r in renderers) r.enabled = false;
            yield return new WaitForSeconds(_activeAbility != null ? 3f : 3f);
            foreach (var r in renderers) r.enabled = true;
        }

        private void UseLightningStrike()
        {
            if (_lightningVFX != null) _lightningVFX.Play();
            Collider[] hits = Physics.OverlapSphere(transform.position + transform.forward * 2f,
                _lightningRadius, _enemyLayer);
            foreach (var hit in hits)
                if (hit.TryGetComponent<IDamageable>(out var d))
                    d.TakeDamage(Mathf.RoundToInt(_lightningDamage));
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.cyan;
            Gizmos.DrawWireSphere(transform.position, _lightningRadius);
        }
    }
}
