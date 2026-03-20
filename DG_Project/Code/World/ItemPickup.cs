using UnityEngine;
using IsleTrial.Core;
using IsleTrial.Data;
using IsleTrial.Player;

namespace IsleTrial.World
{
    /// <summary>
    /// World pickup that adds an item to PlayerInventory on contact.
    /// Attach to any collectible item prefab with a Trigger Collider.
    /// Plays a bob animation while idle.
    /// </summary>
    public class ItemPickup : MonoBehaviour
    {
        [Header("Item")]
        [SerializeField] private ItemData _item;

        [Header("Bob Animation")]
        [SerializeField] private float _bobHeight = 0.15f;
        [SerializeField] private float _bobSpeed = 1.5f;
        [SerializeField] private float _rotateSpeed = 60f;

        [Header("VFX")]
        [SerializeField] private ParticleSystem _collectVFX;

        [Header("Layer")]
        [SerializeField] private LayerMask _playerLayer;

        private Vector3 _startPos;
        private bool _collected;

        void Start() => _startPos = transform.position;

        void Update()
        {
            if (_collected) return;
            float newY = _startPos.y + Mathf.Sin(Time.time * _bobSpeed) * _bobHeight;
            transform.position = new Vector3(transform.position.x, newY, transform.position.z);
            transform.Rotate(Vector3.up, _rotateSpeed * Time.deltaTime);
        }

        void OnTriggerEnter(Collider other)
        {
            if (_collected) return;
            if ((_playerLayer.value & (1 << other.gameObject.layer)) == 0) return;

            if (!other.TryGetComponent<PlayerInventory>(out var inventory)) return;
            if (_item == null) return;

            _collected = true;
            inventory.AddItem(_item);
            GameEvents.ItemPickedUp(_item);

            if (_collectVFX != null)
                Instantiate(_collectVFX, transform.position, Quaternion.identity);

            Destroy(gameObject);
        }
    }
}
