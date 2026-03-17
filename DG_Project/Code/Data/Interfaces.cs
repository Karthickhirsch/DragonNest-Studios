namespace IsleTrial
{
    /// <summary>
    /// Any object that can receive damage (player, enemy, boss, destructible).
    /// </summary>
    public interface IDamageable
    {
        void TakeDamage(int damage);
    }

    /// <summary>
    /// Any object the player can press E to interact with
    /// (puzzles, NPCs, levers, doors, chests, etc.).
    /// </summary>
    public interface IInteractable
    {
        void Interact(object interactor);
    }
}
