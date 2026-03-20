using System.Collections;
using UnityEngine;
using IsleTrial.Player;

namespace IsleTrial.Boat
{
    /// <summary>
    /// Behaviour for the harpoon projectile fired by BoatController.
    /// On hit: deals damage, sticks into the target, and optionally pulls it.
    /// Attach to the harpoon projectile prefab alongside a Rigidbody + Collider.
    /// </summary>
    public class HarpoonProjectile : MonoBehaviour
    {
        [Header("Damage")]
        [SerializeField] private int _damage = 40;
        [SerializeField] private LayerMask _hitLayers;

        [Header("Pull")]
        [SerializeField] private bool _enablePull = true;
        [SerializeField] private float _pullForce = 8f;
        [SerializeField] private float _pullDuration = 1.5f;

        [Header("VFX")]
        [SerializeField] private ParticleSystem _hitVFX;
        [SerializeField] private TrailRenderer _trail;

        // ── State ─────────────────────────────────────────────
        private Rigidbody _rb;
        private bool _hasHit;

        void Awake() => _rb = GetComponent<Rigidbody>();

        void OnTriggerEnter(Collider other)
        {
            if (_hasHit) return;
            if ((_hitLayers.value & (1 << other.gameObject.layer)) == 0) return;

            _hasHit = true;
            StopProjectile();

            if (other.TryGetComponent<IDamageable>(out var target))
                target.TakeDamage(_damage);

            PlayHitVFX();

            if (_enablePull && other.attachedRigidbody != null)
                StartCoroutine(PullRoutine(other.attachedRigidbody));
            else
                StartCoroutine(DestroyAfterDelay(3f));
        }

        // ── Internals ─────────────────────────────────────────

        private void StopProjectile()
        {
            if (_rb == null) return;
            _rb.velocity = Vector3.zero;
            _rb.isKinematic = true;
            if (_trail != null) _trail.emitting = false;
        }

        private void PlayHitVFX()
        {
            if (_hitVFX != null)
                Instantiate(_hitVFX, transform.position, Quaternion.identity);
        }

        private IEnumerator PullRoutine(Rigidbody targetRb)
        {
            float elapsed = 0f;
            targetRb.isKinematic = false;

            while (elapsed < _pullDuration)
            {
                if (targetRb == null) break;
                Vector3 dir = (transform.position - targetRb.position).normalized;
                targetRb.AddForce(dir * _pullForce, ForceMode.Acceleration);
                elapsed += Time.deltaTime;
                yield return null;
            }

            Destroy(gameObject);
        }

        private IEnumerator DestroyAfterDelay(float delay)
        {
            yield return new WaitForSeconds(delay);
            Destroy(gameObject);
        }
    }
}
