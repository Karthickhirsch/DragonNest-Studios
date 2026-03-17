using UnityEngine;
using UnityEngine.SceneManagement;

namespace IsleTrial.Core
{
    public enum GameState
    {
        MainMenu,
        Sailing,
        OnIsland,
        BossFight,
        Cutscene,
        Paused,
        GameOver
    }

    /// <summary>
    /// Central manager that owns the current game state.
    /// Attach to a GameObject in the Bootstrap scene and mark DontDestroyOnLoad.
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Initial State")]
        [SerializeField] private GameState _startingState = GameState.MainMenu;

        public GameState CurrentState { get; private set; }

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        void Start()
        {
            ChangeState(_startingState);
        }

        public void ChangeState(GameState newState)
        {
            GameState previous = CurrentState;
            CurrentState = newState;

            switch (newState)
            {
                case GameState.Paused:
                    Time.timeScale = 0f;
                    break;
                case GameState.Cutscene:
                    Time.timeScale = 0f;
                    break;
                default:
                    Time.timeScale = 1f;
                    break;
            }

            GameEvents.GameStateChanged(previous, newState);
            Debug.Log($"[GameManager] State: {previous} → {newState}");
        }

        public void QuitGame()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }
    }
}
