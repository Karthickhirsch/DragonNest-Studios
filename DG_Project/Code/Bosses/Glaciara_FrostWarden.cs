using System.Collections;
using UnityEngine;
using IsleTrial.Player;

namespace IsleTrial.Bosses
{
    /// <summary>
    /// Glaciara the Frost Warden — second island boss (Frost Isle).
    /// Phase 1: Ice Shard volley.
    /// Phase 2: Summons ice walls + charges through them.
    /// Phase 3: Full-arena blizzard with homing ice spears.
    /// Attach to the GlaciaraBoss prefab.
    /// </summary>
    public class Glaciara_FrostWarden : BossBase
    {
        [Header("Phase 1 — Ice Shards")]
        [SerializeField] private GameObject _iceShardPrefab;
        [SerializeField] private Transform _shardSpawnPoint;
        [SerializeField] private int _shardCount = 5;
        [SerializeField] private float _shardSpread = 30f;    // degrees total spread

        [Header("Phase 2 — Ice Walls & Charge")]
        [SerializeField] private GameObject _iceWallPrefab;
        [SerializeField] private Transform[] _iceWallSpawnPoints;
        [SerializeField] private float _chargeSpeed = 18f;
        [SerializeField] private float _chargeDuration = 0.8f;
        [SerializeField] private int _chargeDamage = 35;

        [Header("Phase 3 — Blizzard")]
        [SerializeField] private ParticleSystem _blizzardVFX;
        [SerializeField] private GameObject _iceSpearPrefab;
        [SerializeField] private int _spearCount = 8;
        [SerializeField] private float _blizzardSlowMultiplier = 0.4f;

        [Header("References")]
        [SerializeField] private LayerMask _playerLayer;

        private Transform _playerTransform;
        private static readonly int HashCharge = Animator.StringToHash("Charge");
        private static readonly int HashShoot = Animator.StringToHash("Shoot");
        private static readonly int HashBlizzard = Animator.StringToHash("Blizzard");

        protected override void Awake()
        {
            base.Awake();
            _playerTransform = FindObjectOfType<PlayerController>()?.transform;
        }

        // ── Phase Entry ───────────────────────────────────────

        protected override void EnterPhase(BossPhase phase)
        {
            switch (phase)
            {
                case BossPhase.Phase1:
                    _attackTimer = 3f;
                    break;
                case BossPhase.Phase2:
                    StartCoroutine(SummonIceWalls());
                    _attackTimer = 2f;
                    break;
                case BossPhase.Phase3:
                    if (_blizzardVFX != null) _blizzardVFX.Play();
                    _attackTimer = 1.5f;
                    ApplyBlizzardSlow();
                    break;
            }
        }

        // ── Attack Pattern ────────────────────────────────────

        protected override void ExecuteAttackPattern()
        {
            switch (CurrentPhase)
            {
                case BossPhase.Phase1:
                    StartCoroutine(ShootIceShards());
                    _attackTimer = Random.Range(2.5f, 4f);
                    break;
                case BossPhase.Phase2:
                    if (Random.value > 0.4f)
                        StartCoroutine(ChargeAttack());
                    else
                        StartCoroutine(ShootIceShards());
                    _attackTimer = Random.Range(2f, 3.5f);
                    break;
                case BossPhase.Phase3:
                    StartCoroutine(HomingIceSpears());
                    _attackTimer = Random.Range(1.5f, 2.5f);
                    break;
            }
        }

        // ── Phase 1: Ice Shards ───────────────────────────────

        private IEnumerator ShootIceShards()
        {
            if (_iceShardPrefab == null || _shardSpawnPoint == null) yield break;

            _animator.SetTrigger(HashShoot);
            yield return new WaitForSeconds(0.4f);

            float halfSpread = _shardSpread * 0.5f;
            for (int i = 0; i < _shardCount; i++)
            {
                float angle = Mathf.Lerp(-halfSpread, halfSpread,
                    _shardCount > 1 ? (float)i / (_shardCount - 1) : 0.5f);

                Quaternion rot = _shardSpawnPoint.rotation * Quaternion.Euler(0, angle, 0);
                var shard = Instantiate(_iceShardPrefab, _shardSpawnPoint.position, rot);

                if (shard.TryGetComponent<Rigidbody>(out var rb))
                    rb.velocity = rot * Vector3.forward * 14f;

                if (shard.TryGetComponent<IceShardProjectile>(out var proj))
                    proj.Initialise(20, _playerLayer);

                Destroy(shard, 4f);
                yield return new WaitForSeconds(0.06f);
            }
        }

        // ── Phase 2: Ice Walls ────────────────────────────────

        private IEnumerator SummonIceWalls()
        {
            yield return new WaitForSeconds(1f);
            foreach (var spawnPoint in _iceWallSpawnPoints)
            {
                if (spawnPoint == null) continue;
                var wall = Instantiate(_iceWallPrefab, spawnPoint.position, spawnPoint.rotation);
                Destroy(wall, 20f);
            }
        }

        private IEnumerator ChargeAttack()
        {
            if (_playerTransform == null) yield break;

            _animator.SetTrigger(HashCharge);
            yield return new WaitForSeconds(0.5f);

            Vector3 dir = (_playerTransform.position - transform.position).normalized;
            dir.y = 0;

            float elapsed = 0f;
            while (elapsed < _chargeDuration)
            {
                transform.position += dir * _chargeSpeed * Time.deltaTime;
                elapsed += Time.deltaTime;

                Collider[] hits = Physics.OverlapSphere(transform.position, 1.2f, _playerLayer);
                foreach (var hit in hits)
                    if (hit.TryGetComponent<PlayerStats>(out var stats))
                        stats.TakeDamage(_chargeDamage);

                yield return null;
            }
        }

        // ── Phase 3: Blizzard + Homing Spears ─────────────────

        private void ApplyBlizzardSlow()
        {
            var player = FindObjectOfType<PlayerStats>();
            if (player != null) player.ApplySpeedModifier(_blizzardSlowMultiplier);
        }

        private IEnumerator HomingIceSpears()
        {
            if (_iceSpearPrefab == null || _playerTransform == null) yield break;

            _animator.SetTrigger(HashBlizzard);
            yield return new WaitForSeconds(0.6f);

            for (int i = 0; i < _spearCount; i++)
            {
                float angle = (360f / _spearCount) * i;
                Vector3 spawnOffset = Quaternion.Euler(0, angle, 0) * Vector3.forward * 4f;
                Vector3 spawnPos = transform.position + spawnOffset + Vector3.up * 2f;

                var spear = Instantiate(_iceSpearPrefab, spawnPos, Quaternion.identity);
                if (spear.TryGetComponent<IceSpearHoming>(out var homing))
                    homing.Initialise(_playerTransform, 25, _playerLayer);

                Destroy(spear, 6f);
                yield return new WaitForSeconds(0.15f);
            }
        }

        protected override void OnBossDefeated()
        {
            // Restore player speed if blizzard was active
            var player = FindObjectOfType<PlayerStats>();
            player?.ResetSpeedModifier();

            if (_blizzardVFX != null) _blizzardVFX.Stop();
            Debug.Log("[Glaciara] Defeated! Frost Isle cleared.");
        }
    }

    // ─────────────────────────────────────────────────────────
    // Helper projectile scripts (nested — same file for brevity)
    // ─────────────────────────────────────────────────────────

    /// <summary>Straight-flying ice shard. Attach to shard prefab.</summary>
    public class IceShardProjectile : MonoBehaviour
    {
        private int _damage;
        private LayerMask _playerLayer;
        private bool _hit;

        public void Initialise(int damage, LayerMask layer) { _damage = damage; _playerLayer = layer; }

        void OnTriggerEnter(Collider other)
        {
            if (_hit) return;
            if ((_playerLayer.value & (1 << other.gameObject.layer)) == 0) return;
            _hit = true;
            if (other.TryGetComponent<PlayerStats>(out var s)) s.TakeDamage(_damage);
            Destroy(gameObject);
        }
    }

    /// <summary>Homing ice spear that tracks the player. Attach to spear prefab.</summary>
    public class IceSpearHoming : MonoBehaviour
    {
        private Transform _target;
        private int _damage;
        private LayerMask _playerLayer;
        private bool _hit;
        private float _speed = 10f;

        public void Initialise(Transform target, int damage, LayerMask layer)
        { _target = target; _damage = damage; _playerLayer = layer; }

        void Update()
        {
            if (_hit || _target == null) return;
            Vector3 dir = (_target.position - transform.position).normalized;
            transform.position += dir * _speed * Time.deltaTime;
            transform.rotation = Quaternion.LookRotation(dir);
        }

        void OnTriggerEnter(Collider other)
        {
            if (_hit) return;
            if ((_playerLayer.value & (1 << other.gameObject.layer)) == 0) return;
            _hit = true;
            if (other.TryGetComponent<PlayerStats>(out var s)) s.TakeDamage(_damage);
            Destroy(gameObject);
        }
    }
}
