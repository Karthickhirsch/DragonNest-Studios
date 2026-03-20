using System.Collections;
using UnityEngine;
using IsleTrial.Player;

namespace IsleTrial.Bosses
{
    /// <summary>
    /// Lava ball projectile fired by Ignar_MoltenDrake.
    /// On impact: deals direct damage + AoE splash damage in a radius.
    /// Spawned and returned via PoolManager.
    /// Attach to the LavaBall prefab alongside a Rigidbody + SphereCollider.
    /// </summary>
    public class LavaBallProjectile : MonoBehaviour
    {
        [Header("Damage")]
        [SerializeField] private int _directDamage = 30;
        [SerializeField] private int _splashDamage = 15;
        [SerializeField] private float _splashRadius = 2.5f;
        [SerializeField] private LayerMask _playerLayer;

        [Header("Lava Puddle")]
        [SerializeField] private bool _leavePuddle = true;
        [SerializeField] private GameObject _puddlePrefab;
        [SerializeField] private float _puddleDuration = 4f;
        [SerializeField] private float _puddleDamagePerSecond = 8f;

        [Header("VFX")]
        [SerializeField] private ParticleSystem _trailVFX;
        [SerializeField] private ParticleSystem _impactVFX;

        private bool _hasImpacted;

        void OnEnable() => _hasImpacted = false;

        void OnCollisionEnter(Collision col)
        {
            if (_hasImpacted) return;
            _hasImpacted = true;

            PlayImpactVFX(col.contacts[0].point);
            DealSplashDamage(col.contacts[0].point);

            if (_leavePuddle && _puddlePrefab != null)
            {
                var puddle = Instantiate(_puddlePrefab, col.contacts[0].point, Quaternion.identity);
                if (puddle.TryGetComponent<LavaPuddle>(out var lp))
                {
                    lp.Initialise(_puddleDamagePerSecond, _playerLayer);
                    Destroy(puddle, _puddleDuration);
                }
            }

            // Return to pool or destroy
            Utilities.PoolManager.Instance?.ReturnAfterDelay("Projectile_LavaBall", gameObject, 0.1f);
            if (Utilities.PoolManager.Instance == null) Destroy(gameObject);
        }

        // ── Damage ────────────────────────────────────────────

        private void DealSplashDamage(Vector3 origin)
        {
            Collider[] hits = Physics.OverlapSphere(origin, _splashRadius, _playerLayer);
            foreach (var hit in hits)
            {
                if (hit.TryGetComponent<PlayerStats>(out var stats))
                {
                    float dist = Vector3.Distance(origin, hit.transform.position);
                    float falloff = Mathf.Clamp01(1f - dist / _splashRadius);
                    int dmg = Mathf.RoundToInt(Mathf.Lerp(_splashDamage * 0.5f, _directDamage, falloff));
                    stats.TakeDamage(dmg);
                }
            }
        }

        private void PlayImpactVFX(Vector3 pos)
        {
            if (_impactVFX != null)
                Instantiate(_impactVFX, pos, Quaternion.identity);
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = new Color(1f, 0.3f, 0f, 0.3f);
            Gizmos.DrawWireSphere(transform.position, _splashRadius);
        }
    }

    /// <summary>
    /// Damage-over-time zone left by a LavaBall impact.
    /// Attach to the lava puddle prefab with a Trigger Collider.
    /// </summary>
    public class LavaPuddle : MonoBehaviour
    {
        private float _dpsAmount;
        private LayerMask _playerLayer;

        public void Initialise(float dps, LayerMask layer)
        {
            _dpsAmount = dps;
            _playerLayer = layer;
        }

        void OnTriggerStay(Collider other)
        {
            if ((_playerLayer.value & (1 << other.gameObject.layer)) == 0) return;
            if (other.TryGetComponent<PlayerStats>(out var stats))
                stats.TakeDamage(Mathf.RoundToInt(_dpsAmount * Time.deltaTime));
        }
    }
}
