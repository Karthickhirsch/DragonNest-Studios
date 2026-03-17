using UnityEngine;
using IsleTrial.Core;
using IsleTrial.Data;

namespace IsleTrial.World
{
    /// <summary>
    /// Loads and unloads an island's scene additively based on boat proximity.
    /// Place one of these on each island marker in the Ocean_World scene.
    /// Assign the IslandData ScriptableObject in the Inspector.
    /// </summary>
    public class IslandProximityLoader : MonoBehaviour
    {
        [Header("Island")]
        [SerializeField] private IslandData _islandData;

        [Header("Distance Thresholds")]
        [SerializeField] private float _discoverDistance = 300f;  // Fog clears
        [SerializeField] private float _loadDistance = 150f;      // Scene loads
        [SerializeField] private float _unloadDistance = 350f;    // Scene unloads

        [Header("Map Marker")]
        [SerializeField] private GameObject _mapMarkerIcon;

        private Transform _boat;
        private bool _isLoaded;
        private bool _isDiscovered;

        void Start()
        {
            var boatGO = GameObject.FindGameObjectWithTag("Boat");
            if (boatGO != null) _boat = boatGO.transform;

            if (_mapMarkerIcon != null) _mapMarkerIcon.SetActive(false);
        }

        void Update()
        {
            if (_boat == null) return;
            float dist = Vector3.Distance(transform.position, _boat.position);
            HandleDiscovery(dist);
            HandleLoading(dist);
        }

        private void HandleDiscovery(float dist)
        {
            if (_isDiscovered || dist > _discoverDistance) return;
            _isDiscovered = true;
            if (_mapMarkerIcon != null) _mapMarkerIcon.SetActive(true);
            GameEvents.IslandDiscovered(_islandData);
            Debug.Log($"[Proximity] Discovered island: {_islandData.IslandName}");
        }

        private void HandleLoading(float dist)
        {
            if (!_isLoaded && dist <= _loadDistance)
            {
                _isLoaded = true;
                SceneLoader.Instance.LoadSceneAdditive(_islandData.SceneName, () =>
                {
                    GameEvents.IslandEntered(_islandData);
                });
            }
            else if (_isLoaded && dist > _unloadDistance)
            {
                _isLoaded = false;
                SceneLoader.Instance.UnloadScene(_islandData.SceneName);
            }
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.green;
            Gizmos.DrawWireSphere(transform.position, _loadDistance);
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, _discoverDistance);
            Gizmos.color = Color.red;
            Gizmos.DrawWireSphere(transform.position, _unloadDistance);
        }
    }
}
