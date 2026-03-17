using System.Collections;
using UnityEngine;
using IsleTrial.Player;

namespace IsleTrial.Bosses
{
    /// <summary>
    /// Boss 1: Ignar the Molten Drake — Ember Isle.
    /// Shows how to extend BossBase with 3 phases.
    /// Attach to the Ignar prefab alongside BossBase fields.
    /// </summary>
    public class Ignar_MoltenDrake : BossBase
    {
        [Header("Ignar Attacks")]
        [SerializeField] private Transform _breathOrigin;
        [SerializeField] private ParticleSystem _fireBreathVFX;
        [SerializeField] private GameObject _lavaBallPrefab;
        [SerializeField] private Transform _lavaSpawnPoint;
        [SerializeField] private float _lavaBallSpeed = 8f;

        [Header("Phase 2 — Lava Rise")]
        [SerializeField] private Transform _lavaPlane;
        [SerializeField] private float _lavaRiseTarget = 1.5f;
        [SerializeField] private float _lavaRiseSpeed = 0.3f;

        [Header("Phase 3 — Floor Cracks")]
        [SerializeField] private GameObject[] _floorTiles;

        [Header("Weak Point")]
        [SerializeField] private Collider _bellyWeakPoint;
        [SerializeField] private int _weakPointDamageMultiplier = 3;

        private Transform _player;
        private int _attackIndex;
        private bool _lavaRising;

        protected override void Start()
        {
            base.Start();
            _player = FindObjectOfType<PlayerController>()?.transform;
        }

        protected override void EnterPhase(BossPhase phase)
        {
            _attackTimer = 2f;
            switch (phase)
            {
                case BossPhase.Phase1:
                    Debug.Log("[Ignar] Phase 1: Warden");
                    break;
                case BossPhase.Phase2:
                    Debug.Log("[Ignar] Phase 2: Inferno — lava rises!");
                    _lavaRising = true;
                    StartCoroutine(RaiseLava());
                    break;
                case BossPhase.Phase3:
                    Debug.Log("[Ignar] Phase 3: Berserker — floor breaks!");
                    StartCoroutine(BreakFloorTiles());
                    break;
            }
        }

        protected override void ExecuteAttackPattern()
        {
            if (_player == null) return;

            switch (CurrentPhase)
            {
                case BossPhase.Phase1:
                    Phase1Attack();
                    break;
                case BossPhase.Phase2:
                    Phase2Attack();
                    break;
                case BossPhase.Phase3:
                    Phase3Attack();
                    break;
            }
        }

        // ── Phase 1 Attacks ───────────────────────────────────

        private void Phase1Attack()
        {
            _attackIndex = (_attackIndex + 1) % 3;
            switch (_attackIndex)
            {
                case 0: StartCoroutine(FireBreathSweep()); _attackTimer = 3f; break;
                case 1: StartCoroutine(LavaBallSpit(3)); _attackTimer = 4f; break;
                case 2: TailSlam(); _attackTimer = 2.5f; break;
            }
        }

        private IEnumerator FireBreathSweep()
        {
            if (_fireBreathVFX != null) _fireBreathVFX.Play();
            FacePlayer();
            yield return new WaitForSeconds(1.5f);
            // Rotate sweep over 1s — handled via animation
            if (_fireBreathVFX != null) _fireBreathVFX.Stop();
        }

        private IEnumerator LavaBallSpit(int count)
        {
            for (int i = 0; i < count; i++)
            {
                SpawnLavaBall();
                yield return new WaitForSeconds(0.4f);
            }
        }

        private void SpawnLavaBall()
        {
            if (_lavaBallPrefab == null || _player == null) return;
            Vector3 dir = (_player.position - _lavaSpawnPoint.position).normalized;
            var ball = Instantiate(_lavaBallPrefab, _lavaSpawnPoint.position, Quaternion.identity);
            if (ball.TryGetComponent<Rigidbody>(out var rb))
                rb.velocity = dir * _lavaBallSpeed;
            Destroy(ball, 6f);
        }

        private void TailSlam()
        {
            _animator.SetTrigger("TailSlam");
        }

        // ── Phase 2 Attacks ───────────────────────────────────

        private void Phase2Attack()
        {
            _attackIndex = (_attackIndex + 1) % 3;
            switch (_attackIndex)
            {
                case 0: StartCoroutine(LavaDive()); _attackTimer = 5f; break;
                case 1: StartCoroutine(LavaBallSpit(6)); _attackTimer = 3f; break;
                case 2: TailSlam(); _attackTimer = 2f; break;
            }
        }

        private IEnumerator LavaDive()
        {
            _animator.SetTrigger("Dive");
            // Shadow indicator handled by separate shadow GameObject on arena floor
            yield return new WaitForSeconds(2f);
            if (_player != null) transform.position = _player.position + Vector3.up * 5f;
            _animator.SetTrigger("DiveLand");
        }

        // ── Phase 3 Attacks ───────────────────────────────────

        private void Phase3Attack()
        {
            StartCoroutine(BerserkerCharge());
            _attackTimer = 4f;
        }

        private IEnumerator BerserkerCharge()
        {
            _animator.SetTrigger("Charge");
            float elapsed = 0f;
            while (elapsed < 1.5f)
            {
                elapsed += Time.deltaTime;
                transform.position = Vector3.MoveTowards(transform.position,
                    _player != null ? _player.position : transform.position, 15f * Time.deltaTime);
                yield return null;
            }
        }

        // ── Helpers ───────────────────────────────────────────

        private IEnumerator RaiseLava()
        {
            if (_lavaPlane == null) yield break;
            float targetY = _lavaPlane.position.y + _lavaRiseTarget;
            while (_lavaPlane.position.y < targetY)
            {
                _lavaPlane.position += Vector3.up * _lavaRiseSpeed * Time.deltaTime;
                yield return null;
            }
        }

        private IEnumerator BreakFloorTiles()
        {
            foreach (var tile in _floorTiles)
            {
                if (tile != null) tile.SetActive(false);
                yield return new WaitForSeconds(0.3f);
            }
        }

        private void FacePlayer()
        {
            if (_player == null) return;
            Vector3 dir = (_player.position - transform.position).normalized;
            dir.y = 0;
            transform.rotation = Quaternion.LookRotation(dir);
        }

        // ── Weak Point ────────────────────────────────────────

        public void TakeDamageAtWeakPoint(int baseDamage)
        {
            TakeDamage(baseDamage * _weakPointDamageMultiplier);
        }
    }
}
