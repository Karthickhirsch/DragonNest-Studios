# Puzzle Design Document
## Isle of Trials — All Puzzle Types, Mechanics & Designs

---

## Table of Contents
1. [Puzzle Design Philosophy](#puzzle-design-philosophy)
2. [Puzzle Categories](#puzzle-categories)
3. [Puzzle Type 1 — Symbol Match](#puzzle-type-1--symbol-match)
4. [Puzzle Type 2 — Light Beam Redirection](#puzzle-type-2--light-beam-redirection)
5. [Puzzle Type 3 — Push & Weight Puzzles](#puzzle-type-3--push--weight-puzzles)
6. [Puzzle Type 4 — Sequence / Order Puzzles](#puzzle-type-4--sequence--order-puzzles)
7. [Puzzle Type 5 — Environmental Observation](#puzzle-type-5--environmental-observation)
8. [Puzzle Type 6 — Circuit / Flow Puzzles](#puzzle-type-6--circuit--flow-puzzles)
9. [Puzzle Type 7 — Elemental Interaction](#puzzle-type-7--elemental-interaction)
10. [Puzzle Type 8 — Timing & Rhythm](#puzzle-type-8--timing--rhythm)
11. [Puzzle Type 9 — Sound-Based Puzzles](#puzzle-type-9--sound-based-puzzles)
12. [Puzzle Type 10 — Memory Sequence](#puzzle-type-10--memory-sequence)
13. [Island-Specific Puzzle Designs](#island-specific-puzzle-designs)
14. [Difficulty Scaling Guidelines](#difficulty-scaling-guidelines)
15. [Hint System](#hint-system)

---

## 1. Puzzle Design Philosophy

### Core Principles
1. **Clarity** — The player should always know what they're trying to accomplish; the challenge is figuring out *how*.
2. **Fair Difficulty** — Every puzzle has all the information needed to solve it present in the environment. No guessing.
3. **Satisfying Feedback** — Solving a puzzle should feel rewarding: animation, sound, particle effects, new path opens.
4. **Fail Gracefully** — Wrong answers reset the puzzle, never punish with health loss (unless intended as a trap room).
5. **Teach → Use → Twist** — Each puzzle type is introduced simply, then used in context, then combined with another element.
6. **Optional Depth** — Main path puzzles are mandatory. Hidden puzzles are optional but rewarding.

### Puzzle Tagging System
Each puzzle in the game is tagged:
```
[Type] [Island] [Difficulty: 1-5] [Optional: Y/N] [Mechanic: Primary/Secondary]
```
Example: `[Symbol Match] [Ember Isle] [Diff: 2] [Optional: N] [Mechanic: Primary]`

---

## 2. Puzzle Categories

| Category | Description | Islands Used |
|----------|-------------|-------------|
| **Navigation Puzzles** | Moving through space safely | All |
| **Object Puzzles** | Manipulating items, blocks, switches | All |
| **Observation Puzzles** | Noticing and interpreting environment | All |
| **Timing Puzzles** | Acting at the right moment | All |
| **Sequence Puzzles** | Doing things in order | Islands 2, 4, 6 |
| **Elemental Puzzles** | Using player abilities | Islands 1-6 |
| **Combination Puzzles** | Multiple puzzle types combined | Islands 4, 5, 6 |

---

## 3. Puzzle Type 1 — Symbol Match

### Concept
Player rotates or arranges tiles/panels to match a target pattern found in the environment.

### Mechanic
- Tiles have 3-6 possible symbols.
- Player rotates each tile (clockwise) with Interact button.
- Solution is shown via: wall carvings, NPC dialogue, or found scrolls.
- Tiles may affect each other (rotating one rotates adjacent tiles).

### Variations

#### V1.1 — Simple Symbol Match (Tutorial / Island 1)
- 4 tiles, independent rotation.
- Solution shown directly on the wall above.
- Used to teach the concept.

```
[Wall Hint]         [Player Tiles]
  ★ ◆ ● ▲      →   rotate to match
```

#### V1.2 — Hidden Clue Symbol Match (Islands 2, 3)
- 6 tiles, solution split across 3 separate clue locations in the level.
- Player must explore to collect all clues before solving.

#### V1.3 — Cascading Tile Puzzle (Islands 4, 5)
- 9 tiles in a 3x3 grid.
- Rotating one tile rotates adjacent tiles (Rubik's Cube-style rule).
- Solution is a picture/symbol visible only when all tiles are correct.

### Implementation Notes
```csharp
public class SymbolTile : MonoBehaviour
{
    public List<Sprite> SymbolSprites;  // 4 possible symbols
    public int CurrentIndex { get; private set; }

    public void Rotate()
    {
        CurrentIndex = (CurrentIndex + 1) % SymbolSprites.Count;
        GetComponent<SpriteRenderer>().sprite = SymbolSprites[CurrentIndex];
        OnRotated?.Invoke(this);
    }
}
```

### Reward on Solve
- Door opens / gate rises with stone grinding SFX.
- Particle burst from the solved panel.

---

## 4. Puzzle Type 2 — Light Beam Redirection

### Concept
A beam of light must be directed to hit a target by placing or rotating mirrors, prisms, and filters.

### Mechanic
- Light Source emits a beam (LineRenderer in Unity).
- Mirrors redirect at 45° or 90° angles.
- Prisms split one beam into multiple.
- Color filters change beam color (used for colored target matching).
- Target Receiver activates when correct color/direction beam hits it.

### Variations

#### V2.1 — Basic Redirect (Island 2 — Ice)
- Single beam, 3 mirrors, one receiver.
- Mirrors are draggable to set positions; fixed rotation (45° only).

#### V2.2 — Multi-Beam (Island 4 — Desert)
- Sky Observatory puzzle: Sun acts as the light source (only active at in-game noon).
- Player aligns prisms to split sunbeam and hit 3 receivers simultaneously.
- Tied to Day/Night cycle.

#### V2.3 — Color Sequence (Island 5 — Storm)
- Three colored beams (red, blue, yellow) must mix at targets to create secondary colors.
- Multiple prisms and filters to arrange.

### Visual Design
- Active beams: bright colored LineRenderer with glow effect (bloom via URP post-process).
- Solved state: receiver glows brightly, emits particles.

```csharp
public class LightBeam : MonoBehaviour
{
    private LineRenderer _lr;

    void Update()
    {
        SimulateBeam(transform.position, transform.forward);
    }

    private void SimulateBeam(Vector3 origin, Vector3 direction, int depth = 0)
    {
        if (depth > 8) return; // Max reflections
        if (Physics.Raycast(origin, direction, out RaycastHit hit))
        {
            _lr.SetPosition(depth, origin);
            _lr.SetPosition(depth + 1, hit.point);

            if (hit.collider.TryGetComponent<Mirror>(out var mirror))
                SimulateBeam(hit.point, Vector3.Reflect(direction, hit.normal), depth + 1);
            else if (hit.collider.TryGetComponent<LightReceiver>(out var receiver))
                receiver.Activate();
        }
    }
}
```

---

## 5. Puzzle Type 3 — Push & Weight Puzzles

### Concept
Move heavy objects (blocks, statues) to pressure plates, correct positions, or to clear paths.

### Mechanic
- Player pushes blocks in 4 directions (grid-based movement).
- Block cannot be pulled (only pushed).
- Block falls off edges, resets from starting position.
- Multiple blocks may interact (stacking, chaining).

### Variations

#### V3.1 — Single Block (Tutorial)
- Push one block onto one pressure plate.
- Block starts adjacent to plate.
- Teaches the concept.

#### V3.2 — Multi-Block (Island 3 — Jungle)
- 3 blocks, 3 plates.
- Complex arrangement; blocks can block each other.
- Requires thinking ahead.

#### V3.3 — Moving Platform (Island 4 — Desert)
- Pressure plates are on moving platforms.
- Block must be pushed onto plate as platform aligns.
- Combines timing with spatial reasoning.

#### V3.4 — Weight Bridge (Island 5 — Storm)
- Multiple blocks of different weights.
- Scale/bridge tilts based on weight distribution.
- Player must balance the scale to create a walkable path.

### Implementation
```csharp
public class PushableBlock : MonoBehaviour
{
    [SerializeField] private float _pushCooldown = 0.3f;
    private bool _canBePushed = true;

    public void Push(Vector3 direction)
    {
        if (!_canBePushed) return;
        Vector3 targetPos = transform.position + direction;
        if (!Physics.Raycast(transform.position, direction, 1f))
        {
            transform.DOMove(targetPos, 0.2f).OnComplete(() => CheckPlates());
            _canBePushed = false;
            DOVirtual.DelayedCall(_pushCooldown, () => _canBePushed = true);
        }
    }
}
```

---

## 6. Puzzle Type 4 — Sequence / Order Puzzles

### Concept
Player must activate switches, tiles, or symbols in a specific order.

### Mechanic
- A sequence is shown (flash, glow, sound) then player must replicate it.
- Alternatively, clues in the environment indicate the correct order.
- Wrong order: puzzle resets and spawns an enemy wave.

### Variations

#### V4.1 — Watch & Repeat (Island 2 — Ice)
- 5 panels light up in sequence; player repeats.
- Simon Says style; sequence gets longer each round.

#### V4.2 — Environmental Clue Order (Islands 3, 4)
- Paintings/carvings show numbered symbols.
- Player finds the clues scattered in the level, maps the order.
- Press panels in that order.

#### V4.3 — Musical Sequence (Island 5 — Storm)
- Activating switches produces musical notes.
- Player must replicate a melody heard at the start of the room.
- Crosses with sound-based puzzles.

#### V4.4 — Reverse Sequence (Island 6 — Final)
- Shows a 10-step sequence.
- Player must activate it in **reverse** order.
- Tests memory and logic.

---

## 7. Puzzle Type 5 — Environmental Observation

### Concept
Player finds clues hidden in the level environment to deduce the puzzle solution.

### Mechanic
- Player uses Inspect button (F) to highlight clues.
- Clues can be: star patterns, carvings, paintings, shadows, reflections.
- Notebook icon appears in journal with clue recorded automatically.

### Variations

#### V5.1 — Shadow Reading (Island 4 — Desert)
- At a specific time of day, object shadows point to a direction on the floor mosaic.
- Player waits for the right time or manipulates a sundial.

#### V5.2 — Constellation Map (Island 5 — Storm)
- At night, stars in the sky form a pattern matching floor tiles.
- Player must look up at night (camera rotates) and replicate the pattern.

#### V5.3 — Hidden Message (Island 3 — Jungle)
- Vines are cut to reveal partial carvings.
- Each carving is part of a word; combine all 4 for the passcode.

#### V5.4 — Reflection Puzzle (Island 2 — Ice)
- Room with reflective ice walls.
- A symbol is only visible in the correct mirror angle.
- Player walks around to find the viewing angle.

---

## 8. Puzzle Type 6 — Circuit / Flow Puzzles

### Concept
Connect or redirect flow (electricity, water, steam) from source to destination by rotating or placing conduit pieces.

### Mechanic
- Grid-based pipe/wire segments.
- Player rotates each piece with Interact button.
- Active flow shown as animated line through correct connections.
- Leaks or shorts create hazards (shock, steam, flood).

### Variations

#### V6.1 — Pipe Flow (Island 1 — Ember)
- Steam pipes must be connected to cool the lava path.
- 4x4 grid; rotate pipe segments.

#### V6.2 — Electrical Circuit (Island 5 — Storm)
- Wire segments, battery, bulb/switch.
- Player routes electricity across 5x5 grid.
- Wrong connections cause shock damage.

#### V6.3 — Water Channel (Island 3 — Jungle)
- Channel water from spring to wilted plants.
- 6x6 grid; multiple branches.
- Opening all branches simultaneously unlocks bonus room.

#### V6.4 — Multi-Source Circuit (Island 6 — Final)
- 3 energy sources (fire, ice, lightning) must be routed to 3 receivers without mixing.
- 8x8 grid; hardest variant.

---

## 9. Puzzle Type 7 — Elemental Interaction

### Concept
Use player abilities (Fire Dash, Ice Shield, Vine Grapple, etc.) on environmental objects to solve puzzles.

### Mechanic
- Specific objects react to specific elements.
- Fire → melts ice, ignites torches, burns vines.
- Ice → freezes water, creates platforms, chills fire.
- Lightning → powers switches, stuns enemies.
- Nature → grows vines as bridges/platforms, blooms flowers.
- Sand → creates dust clouds (conceals), fills water.

### Examples

#### V7.1 — Fire Path (Island 3 — Jungle)
- A wall of ice blocks the way.
- Use Fire Dash to melt ice blocks → path opens.

#### V7.2 — Ice Bridge (Island 1 — Ember)
- Lava pool gap; player uses Ice Shield crystal dropped by enemy to freeze lava temporarily.
- Must cross quickly before ice melts.

#### V7.3 — Vine Bridge (Island 5 — Storm)
- Broken bridge; use Nature ability to grow vines from wall sockets.
- Creates a crossable vine bridge.

#### V7.4 — Lightning Rune (Island 4 — Desert)
- Ancient rune panel needs electric charge.
- Attract a Storm Imp (enemy), lure it to panel, let it shoot the panel.

---

## 10. Puzzle Type 8 — Timing & Rhythm

### Concept
Player must act at precise moments — moving through hazards, pressing switches during windows, or matching a rhythm.

### Mechanic
- Visual telegraphing: hazards have wind-up animations and glow before activating.
- Audio cue: SFX beat matches safe windows.
- Metronome-style some rooms — everything moves on a beat.

### Variations

#### V8.1 — Spinning Trap Dash (Island 1 — Ember)
- Rotating fire pillars; player must pass through the gap.
- Each pillar rotates at different speed.
- Layered: 2 pillars, then 3, then 4.

#### V8.2 — Pressure Plate Rush (Island 4 — Desert)
- 5 pressure plates must all be held simultaneously.
- But plates decay after 5 seconds.
- Player must place weighted objects quickly.

#### V8.3 — Rhythm Drum Puzzle (Island 3 — Jungle)
- 4 drums in a circle; each has a symbol.
- Tribal rhythm plays; player taps each drum on the beat it lights up.
- 3 successful rounds solve the puzzle.
- Implemented using music timing events (FMOD callbacks).

#### V8.4 — Storm Dash Gauntlet (Island 5 — Storm)
- Lightning strikes at timed intervals on floor tiles.
- Player must move from safe tile to safe tile.
- Grid illuminates predicted strike positions 2 seconds before.

---

## 11. Puzzle Type 9 — Sound-Based Puzzles

### Concept
Player uses sound as a clue or tool to solve the puzzle.

### Mechanic
- Inspect + audio cues: specific objects emit tones.
- Player hums back (matches tone by selecting from options).
- Or: sound directs player to a hidden object.
- Accessibility: visual indicator (waveform/animation) accompanies all sound cues.

### Variations

#### V9.1 — Tone Matching (Island 2 — Ice)
- Four ice bells; each has a pitch.
- An NPC sings a melody; player hits the bells in pitch order.

#### V9.2 — Echo Navigation (Island 3 — Jungle)
- Pitch-black cave; player claps and hears echo delay.
- Short delay = wall close; long delay = open space.
- Visual: ripple rings from player that change color near walls.

#### V9.3 — Frequency Lock (Island 5 — Storm)
- A locked door emits a pulse.
- Player finds three tuning forks scattered in the room.
- Must activate the correct fork to match the door's frequency.

---

## 12. Puzzle Type 10 — Memory Sequence

### Concept
Player watches a sequence, must remember and reproduce it.

### Mechanic
- Sequence shown once; no repeat (unless a hint token is used).
- Longer sequences in later islands.
- Sequence elements: symbols, positions, colors, or sounds.

### Variations

#### V10.1 — Panel Flash Repeat (Island 1 — Tutorial)
- 4 panels light up; player repeats.
- 4-step sequence.

#### V10.2 — Pattern Journey (Island 4 — Desert)
- Player watches a holographic path through a maze (once).
- Must walk the path from memory.
- Wrong turn: reset to start.

#### V10.3 — Multi-Layer Memory (Island 6 — Final)
- Shows symbol sequence, then color sequence, then position sequence.
- All three must be applied to the same set of tiles simultaneously.
- 12-step combined sequence.

---

## 13. Island-Specific Puzzle Designs

### Summary Table

| Island | Entry Puzzle | Main Puzzle | Bonus Puzzle | Type Combo |
|--------|-------------|-------------|-------------|------------|
| Driftwood (Tutorial) | Push box | Torch lighting | Hidden chest room | Push + Observation |
| Ember Isle | Steam pipe connect | Lava valve redirect | Symbol match on lava wall | Circuit + Symbol |
| Frostveil | Ice bell tones | Light prism refraction | Slide ice blocks maze | Sound + Light + Push |
| Thornwood | Vine cut sequence | Seed planting | Echo cave nav | Sequence + Observation + Sound |
| Dunestone | Statue compass | Solar observatory | Hieroglyph panel | Observation + Timing + Sequence |
| Stormcrest | Wire circuit | Capacitor charge order | Constellation night | Circuit + Sequence + Observation |
| Aethermoor | Multi-memory | All-element gauntlet | — | All types combined |

---

## 14. Difficulty Scaling Guidelines

| Island | Puzzle Steps | Clue Visibility | Reset Penalty | Time Pressure |
|--------|-------------|-----------------|---------------|---------------|
| Tutorial | 1-2 steps | Direct / On-screen | None | None |
| Island 1 | 2-3 steps | Near puzzle | None | None |
| Island 2 | 3-4 steps | Same room | None | Minimal |
| Island 3 | 4-5 steps | Spread in area | Minor enemy | Some |
| Island 4 | 5-6 steps | Spread in level | Enemy wave | Moderate |
| Island 5 | 6-7 steps | Must explore | Enemy wave | High |
| Island 6 | 8-12 steps | Must remember from all islands | Full reset | Extreme |

---

## 15. Hint System

### Hint Tiers
| Tier | Trigger | Content |
|------|---------|---------|
| **Hint 1** | Inspect nearby object | Vague directional hint ("There's a pattern on the ceiling...") |
| **Hint 2** | 3 minutes without progress | Slightly more specific ("Try matching the symbols in the mural...") |
| **Hint 3** | Hint Token (consumable item) | Direct hint without full solution |
| **Hint 4** | 5 minutes without progress + in Settings: Help Mode ON | Full solution shown step by step |

### Hint Token
- Found in chests, purchased from merchant ships.
- Uses per puzzle: 1 token = 1 Tier 3 hint.
- Encourages exploration but doesn't block progress.

### Accessibility Settings
- **Help Mode:** Enables Tier 4 hints automatically.
- **Extended Timer:** Doubles time windows on timing puzzles.
- **High Contrast Mode:** Enhances visual cues (puzzle glow, clue highlights).

---

*Document Version: 1.0 | Last Updated: March 2026*
