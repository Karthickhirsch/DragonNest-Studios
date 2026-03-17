using UnityEngine;
using UnityEngine.InputSystem;

namespace IsleTrial.Player
{
    /// <summary>
    /// Reads raw input from Unity's New Input System and exposes clean properties.
    /// Requires a PlayerInputActions asset generated from the Input Actions editor.
    /// Attach to the Player GameObject.
    /// </summary>
    public class PlayerInputHandler : MonoBehaviour
    {
        // ── Read-only Input Properties ────────────────────────
        public Vector2 MoveInput { get; private set; }
        public bool AttackPressed { get; private set; }
        public bool AttackHeld { get; private set; }
        public bool DodgePressed { get; private set; }
        public bool InteractPressed { get; private set; }
        public bool AbilityPressed { get; private set; }
        public bool SprintHeld { get; private set; }
        public bool MapPressed { get; private set; }
        public bool InventoryPressed { get; private set; }
        public bool PausePressed { get; private set; }

        // ── Boat Input Properties ─────────────────────────────
        public Vector2 SteerInput { get; private set; }
        public bool BoostHeld { get; private set; }
        public bool AnchorPressed { get; private set; }
        public bool HarpoonPressed { get; private set; }
        public bool LanternPressed { get; private set; }

        private PlayerInputActions _actions;

        void Awake()
        {
            _actions = new PlayerInputActions();
            BindPlayerActions();
            BindBoatActions();
            BindUIActions();
        }

        void OnEnable() => _actions.Enable();
        void OnDisable() => _actions.Disable();

        void LateUpdate()
        {
            // Reset single-frame pressed flags after every frame
            AttackPressed = false;
            DodgePressed = false;
            InteractPressed = false;
            AbilityPressed = false;
            MapPressed = false;
            InventoryPressed = false;
            PausePressed = false;
            AnchorPressed = false;
            HarpoonPressed = false;
            LanternPressed = false;
        }

        private void BindPlayerActions()
        {
            _actions.Player.Move.performed += ctx => MoveInput = ctx.ReadValue<Vector2>();
            _actions.Player.Move.canceled += ctx => MoveInput = Vector2.zero;

            _actions.Player.Attack.performed += ctx => { AttackPressed = true; AttackHeld = true; };
            _actions.Player.Attack.canceled += ctx => AttackHeld = false;

            _actions.Player.Dodge.performed += ctx => DodgePressed = true;
            _actions.Player.Interact.performed += ctx => InteractPressed = true;
            _actions.Player.Ability.performed += ctx => AbilityPressed = true;

            _actions.Player.Sprint.performed += ctx => SprintHeld = true;
            _actions.Player.Sprint.canceled += ctx => SprintHeld = false;

            _actions.Player.Map.performed += ctx => MapPressed = true;
            _actions.Player.Inventory.performed += ctx => InventoryPressed = true;
        }

        private void BindBoatActions()
        {
            _actions.Boat.Steer.performed += ctx => SteerInput = ctx.ReadValue<Vector2>();
            _actions.Boat.Steer.canceled += ctx => SteerInput = Vector2.zero;

            _actions.Boat.Boost.performed += ctx => BoostHeld = true;
            _actions.Boat.Boost.canceled += ctx => BoostHeld = false;

            _actions.Boat.Anchor.performed += ctx => AnchorPressed = true;
            _actions.Boat.Harpoon.performed += ctx => HarpoonPressed = true;
            _actions.Boat.Lantern.performed += ctx => LanternPressed = true;
        }

        private void BindUIActions()
        {
            _actions.UI.Pause.performed += ctx => PausePressed = true;
        }

        public void SwitchToBoatMap() => _actions.Boat.Enable();
        public void SwitchToIslandMap() => _actions.Player.Enable();
        public void DisableAll() => _actions.Disable();
    }
}
