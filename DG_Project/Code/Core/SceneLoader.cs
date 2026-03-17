using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace IsleTrial.Core
{
    /// <summary>
    /// Handles additive scene loading/unloading.
    /// Attach to the Bootstrap scene's persistent manager GameObject.
    /// </summary>
    public class SceneLoader : MonoBehaviour
    {
        public static SceneLoader Instance { get; private set; }

        [Header("Loading Screen")]
        [SerializeField] private GameObject _loadingScreenUI;

        private readonly HashSet<string> _loadedScenes = new();

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        // ── Public API ────────────────────────────────────────

        public void LoadSceneAdditive(string sceneName, Action onComplete = null)
        {
            if (_loadedScenes.Contains(sceneName))
            {
                onComplete?.Invoke();
                return;
            }
            StartCoroutine(LoadRoutine(sceneName, onComplete));
        }

        public void UnloadScene(string sceneName, Action onComplete = null)
        {
            if (!_loadedScenes.Contains(sceneName))
            {
                onComplete?.Invoke();
                return;
            }
            StartCoroutine(UnloadRoutine(sceneName, onComplete));
        }

        public void LoadSceneSingle(string sceneName)
        {
            StartCoroutine(LoadSingleRoutine(sceneName));
        }

        public bool IsSceneLoaded(string sceneName) => _loadedScenes.Contains(sceneName);

        // ── Coroutines ────────────────────────────────────────

        private IEnumerator LoadRoutine(string sceneName, Action onComplete)
        {
            SetLoadingScreen(true);
            AsyncOperation op = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
            while (!op.isDone) yield return null;
            _loadedScenes.Add(sceneName);
            SetLoadingScreen(false);
            onComplete?.Invoke();
            GameEvents.GameStateChanged(GameManager.Instance.CurrentState, GameManager.Instance.CurrentState);
        }

        private IEnumerator UnloadRoutine(string sceneName, Action onComplete)
        {
            AsyncOperation op = SceneManager.UnloadSceneAsync(sceneName);
            while (!op.isDone) yield return null;
            _loadedScenes.Remove(sceneName);
            Resources.UnloadUnusedAssets();
            onComplete?.Invoke();
        }

        private IEnumerator LoadSingleRoutine(string sceneName)
        {
            SetLoadingScreen(true);
            _loadedScenes.Clear();
            AsyncOperation op = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Single);
            while (!op.isDone) yield return null;
            _loadedScenes.Add(sceneName);
            SetLoadingScreen(false);
        }

        private void SetLoadingScreen(bool visible)
        {
            if (_loadingScreenUI != null)
                _loadingScreenUI.SetActive(visible);
        }
    }
}
