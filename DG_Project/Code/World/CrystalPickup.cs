using System.Collections;
using UnityEngine;
using IsleTrial.Core;

namespace IsleTrial.World
{
    /// <summary>
    /// Collectible crystal pickup. Fires GameEvents.CrystalCollected on contact.
    /// HUDManager listens to that event to update the crystal slot icons.
    /// There are 6 crystals total — collecting all unlocks the final area.
    /// Attach to a crystal prefab with a Trigger Collider.
    /// </summary>
    public class CrystalPickup : MonoBehaviour
    {
        [Header("Crystal")]
        [SerializeField] private int _crystalIndex = 0;   // 0-5, unique per crystal

        [Header("Bob & Spin")]
        [SerializeField] private float _bobHeight = 0.2f;
        [SerializeField] private float _bobSpeed = 1.2f;
        [SerializeField] private float _rotateSpeed = 90f;

        [Header("VFX")]
        [SerializeField] private ParticleSystem _collectVFX;
        [SerializeField] private Light _glowLight;

        [Header("Layer")]
        [SerializeField] private LayerMask _playerLayer;

        private static int _totalCollected;

        private Vector3 _startPos;
        private bool _collected;

        void Start() => _startPos = transform.position;

        void Update()
        {
            if (_collected) return;
            float newY = _startPos.y + Mathf.Sin(Time.time * _bobSpeed) * _bobHeight;
            transform.position = new Vector3(transform.position.x, newY, transform.position.z);
            transform.Rotate(Vector3.up, _rotateSpeed * Time.deltaTime);

            if (_glowLight != null)
                _glowLight.intensity = 1.2f + Mathf.Sin(Time.time * 2f) * 0.4f;
        }

        void OnTriggerEnter(Collider other)
        {
            if (_collected) return;
            if ((_playerLayer.value & (1 << other.gameObject.layer)) == 0) return;

            _collected = true;
            _totalCollected++;

            GameEvents.CrystalCollected(_totalCollected);
            Debug.Log($"[Crystal] Collected crystal {_crystalIndex}. Total: {_totalCollected}/6");

            if (_totalCollected >= 6)
                GameEvents.IslandCompleted(null);  // Signals all crystals collected

            if (_collectVFX != null)
                Instantiate(_collectVFX, transform.position, Quaternion.identity);

            StartCoroutine(CollectAnimation());
        }

        private IEnumerator CollectAnimation()
        {
            float elapsed = 0f;
            Vector3 originalScale = transform.localScale;

            while (elapsed < 0.3f)
            {
                transform.localScale = Vector3.Lerp(originalScale, Vector3.zero, elapsed / 0.3f);
                elapsed += Time.deltaTime;
                yield return null;
            }

            Destroy(gameObject);
        }

        // Reset between scenes (call from GameManager if needed)
        public static void ResetCount() => _totalCollected = 0;
    }
}
