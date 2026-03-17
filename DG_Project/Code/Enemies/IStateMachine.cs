namespace IsleTrial.Enemies
{
    /// <summary>
    /// Contract for all state objects used in StateMachine.
    /// </summary>
    public interface IState
    {
        void Enter();
        void Execute();
        void Exit();
    }

    /// <summary>
    /// Generic reusable state machine.
    /// Create one instance inside any class that needs states (enemies, bosses, player).
    /// </summary>
    public class StateMachine
    {
        public IState CurrentState { get; private set; }

        public void Initialize(IState startState)
        {
            CurrentState = startState;
            CurrentState.Enter();
        }

        public void ChangeState(IState newState)
        {
            CurrentState?.Exit();
            CurrentState = newState;
            CurrentState?.Enter();
        }

        public void Update()
        {
            CurrentState?.Execute();
        }
    }
}
