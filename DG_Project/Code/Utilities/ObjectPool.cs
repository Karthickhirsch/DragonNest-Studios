using System.Collections.Generic;
using UnityEngine;

namespace IsleTrial.Utilities
{
    /// <summary>
    /// Generic MonoBehaviour-based object pool.
    /// Create a pool in PoolManager.cs; do not attach this directly.
    /// </summary>
    public class ObjectPool<T> where T : MonoBehaviour
    {
        private readonly Queue<T> _pool = new();
        private readonly T _prefab;
        private readonly Transform _parent;

        public int Available => _pool.Count;

        public ObjectPool(T prefab, int initialSize, Transform parent = null)
        {
            _prefab = prefab;
            _parent = parent;
            for (int i = 0; i < initialSize; i++) CreateNew(active: false);
        }

        public T Get(Vector3 position, Quaternion rotation)
        {
            T obj = _pool.Count > 0 ? _pool.Dequeue() : CreateNew(active: false);
            obj.transform.SetPositionAndRotation(position, rotation);
            obj.gameObject.SetActive(true);
            return obj;
        }

        public void Return(T obj)
        {
            obj.gameObject.SetActive(false);
            _pool.Enqueue(obj);
        }

        private T CreateNew(bool active)
        {
            T obj = Object.Instantiate(_prefab, _parent);
            obj.gameObject.SetActive(active);
            return obj;
        }
    }

    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// PoolManager: central hub for all named object pools.
    /// Attach to a persistent manager GameObject in Bootstrap scene.
    /// Register prefabs in the Inspector under PoolEntries.
    /// </summary>
    public class PoolManager : MonoBehaviour
    {
        public static PoolManager Instance { get; private set; }

        [System.Serializable]
        public class PoolEntry
        {
            public string Key;
            public GameObject Prefab;
            [Min(1)] public int InitialSize = 10;
        }

        [SerializeField] private List<PoolEntry> _poolEntries;

        private readonly Dictionary<string, Queue<GameObject>> _pools = new();
        private readonly Dictionary<string, GameObject> _prefabMap = new();

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);

            foreach (var entry in _poolEntries)
            {
                _prefabMap[entry.Key] = entry.Prefab;
                _pools[entry.Key] = new Queue<GameObject>();
                for (int i = 0; i < entry.InitialSize; i++)
                {
                    var obj = Instantiate(entry.Prefab, transform);
                    obj.SetActive(false);
                    _pools[entry.Key].Enqueue(obj);
                }
            }
        }

        public GameObject Get(string key, Vector3 position, Quaternion rotation)
        {
            if (!_pools.ContainsKey(key))
            {
                Debug.LogWarning($"[Pool] Key not found: {key}");
                return null;
            }

            GameObject obj = _pools[key].Count > 0
                ? _pools[key].Dequeue()
                : Instantiate(_prefabMap[key], transform);

            obj.transform.SetPositionAndRotation(position, rotation);
            obj.SetActive(true);
            return obj;
        }

        public void Return(string key, GameObject obj)
        {
            if (!_pools.ContainsKey(key)) { Destroy(obj); return; }
            obj.SetActive(false);
            _pools[key].Enqueue(obj);
        }

        public void ReturnAfterDelay(string key, GameObject obj, float delay)
            => StartCoroutine(ReturnDelayed(key, obj, delay));

        private System.Collections.IEnumerator ReturnDelayed(string key, GameObject obj, float delay)
        {
            yield return new WaitForSeconds(delay);
            Return(key, obj);
        }
    }
}
