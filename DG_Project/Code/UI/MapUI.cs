using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using IsleTrial.Core;
using IsleTrial.Data;

namespace IsleTrial.UI
{
    /// <summary>
    /// World map overlay toggled with M key.
    /// Subscribes to GameEvents.OnIslandDiscovered to add island markers.
    /// Shows the player's live position as a dot.
    /// Attach to the MapPanel Canvas child (default inactive).
    /// </summary>
    public class MapUI : MonoBehaviour
    {
        [Header("Panel")]
        [SerializeField] private GameObject _mapPanel;
        [SerializeField] private KeyCode _toggleKey = KeyCode.M;

        [Header("Map Image")]
        [SerializeField] private RectTransform _mapRect;        // The background map image rect
        [SerializeField] private Vector2 _worldSize = new Vector2(2000f, 2000f);  // world XZ extents

        [Header("Player Marker")]
        [SerializeField] private RectTransform _playerDot;
        [SerializeField] private Transform _playerTransform;

        [Header("Island Markers")]
        [SerializeField] private GameObject _islandMarkerPrefab;  // prefab: Image + TMP label
        [SerializeField] private Transform _markerParent;

        [Header("Boat Marker")]
        [SerializeField] private RectTransform _boatDot;
        [SerializeField] private Transform _boatTransform;

        private bool _isOpen;
        private readonly Dictionary<string, RectTransform> _markers = new();

        void Start()
        {
            _mapPanel.SetActive(false);

            if (_playerTransform == null)
                _playerTransform = FindObjectOfType<Player.PlayerController>()?.transform;

            if (_boatTransform == null)
            {
                var boatCtrl = FindObjectOfType<Boat.BoatController>();
                if (boatCtrl != null) _boatTransform = boatCtrl.transform;
            }
        }

        void OnEnable()  => GameEvents.OnIslandDiscovered += OnIslandDiscovered;
        void OnDisable() => GameEvents.OnIslandDiscovered -= OnIslandDiscovered;

        void Update()
        {
            if (Input.GetKeyDown(_toggleKey)) Toggle();

            if (!_isOpen) return;

            UpdateMarkerPosition(_playerDot, _playerTransform);
            UpdateMarkerPosition(_boatDot, _boatTransform);
        }

        // ── Toggle ────────────────────────────────────────────

        public void Toggle()
        {
            var state = GameManager.Instance.CurrentState;
            if (state == GameState.GameOver || state == GameState.Cutscene) return;

            _isOpen = !_isOpen;
            _mapPanel.SetActive(_isOpen);
        }

        // ── Island Discovered ─────────────────────────────────

        private void OnIslandDiscovered(IslandData island)
        {
            if (island == null || _islandMarkerPrefab == null) return;
            if (_markers.ContainsKey(island.IslandID)) return;

            var marker = Instantiate(_islandMarkerPrefab, _markerParent);
            var markerRect = marker.GetComponent<RectTransform>();
            _markers[island.IslandID] = markerRect;

            var label = marker.GetComponentInChildren<TextMeshProUGUI>();
            if (label != null) label.text = island.IslandName;

            // Position marker based on island scene center (use IslandData world position if available)
            // For now, place at a default offset; override with island.WorldPosition if you add that field
            Debug.Log($"[MapUI] Island discovered: {island.IslandName}");
        }

        // ── World → Map Position ──────────────────────────────

        private void UpdateMarkerPosition(RectTransform marker, Transform worldTransform)
        {
            if (marker == null || worldTransform == null || _mapRect == null) return;

            Vector2 mapSize = _mapRect.sizeDelta;
            float nx = (worldTransform.position.x + _worldSize.x * 0.5f) / _worldSize.x;
            float nz = (worldTransform.position.z + _worldSize.y * 0.5f) / _worldSize.y;

            marker.anchoredPosition = new Vector2(
                (nx - 0.5f) * mapSize.x,
                (nz - 0.5f) * mapSize.y);
        }

        /// <summary>Called externally to mark a specific island position on the map.</summary>
        public void PlaceIslandMarker(string islandID, Vector2 mapNormalizedPos)
        {
            if (!_markers.TryGetValue(islandID, out var markerRect)) return;
            if (_mapRect == null) return;
            Vector2 mapSize = _mapRect.sizeDelta;
            markerRect.anchoredPosition = new Vector2(
                (mapNormalizedPos.x - 0.5f) * mapSize.x,
                (mapNormalizedPos.y - 0.5f) * mapSize.y);
        }
    }
}
