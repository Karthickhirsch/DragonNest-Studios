# Boss & Enemy Design Document
## Isle of Trials — All Bosses, Enemies & Sea Creatures

---

## Table of Contents
1. [Design Philosophy](#design-philosophy)
2. [Enemy Tier System](#enemy-tier-system)
3. [Common Enemies (Island)](#common-enemies-island)
4. [Common Enemies (Sea)](#common-enemies-sea)
5. [Boss 0 — Driftwood Golem (Miniboss)](#boss-0--driftwood-golem-miniboss)
6. [Boss 1 — Ignar the Molten Drake](#boss-1--ignar-the-molten-drake)
7. [Boss 2 — Kryss the Frozen Titan](#boss-2--kryss-the-frozen-titan)
8. [Boss 3 — Virenax the Vine Colossus](#boss-3--virenax-the-vine-colossus)
9. [Boss 4 — Phareth the Stone Warden](#boss-4--phareth-the-stone-warden)
10. [Boss 5 — Zephyrath the Sky Serpent](#boss-5--zephyrath-the-sky-serpent)
11. [Final Boss — The Shattered Sovereign](#final-boss--the-shattered-sovereign)
12. [AI Behavior Patterns](#ai-behavior-patterns)
13. [Balancing Guidelines](#balancing-guidelines)

---

## 1. Design Philosophy

### Boss Design Principles
1. **Readable Telegraphing** — Every attack has a wind-up animation. Players can always react if they're paying attention.
2. **Pattern Learning** — Bosses repeat patterns, allowing mastery. New patterns introduced in later phases.
3. **Weakness is Discoverable** — The boss's weakness is hinted at in the arena environment (ice crystals against fire boss, etc.).
4. **Multi-Phase Drama** — Phase transitions are dramatic visual events (armor cracks, form changes, arena transforms).
5. **No Cheese** — Bosses should not be trivially defeatable by standing in one spot or spam-attacking.
6. **Theme Harmony** — Each boss's attacks, design, and arena reflect the island's theme and story.

### Enemy Design Principles
- Every enemy type has one clearly readable behavior.
- Enemies escalate in complexity across islands.
- New enemies are introduced in safe contexts before being mixed with others.

---

## 2. Enemy Tier System

| Tier | Name | Description | HP | Damage |
|------|------|-------------|----|----|
| T1 | **Minion** | Basic grunt; one attack; slow | Low | Low |
| T2 | **Soldier** | Medium HP; two attacks; moderate speed | Medium | Medium |
| T3 | **Elite** | High HP; three attacks; fast; special ability | High | High |
| T4 | **Miniboss** | Area sub-boss; multiple phases | Very High | High |
| T5 | **Island Boss** | Full boss fight; 3 phases; unique arena | Extreme | Extreme |
| T6 | **Final Boss** | Multi-phase endgame boss | Maximum | Maximum |

---

## 3. Common Enemies (Island)

### 3.1 Driftwood Crab (Tutorial)
| Field | Value |
|-------|-------|
| **Tier** | T1 |
| **HP** | 20 |
| **Speed** | Slow |
| **Attack** | Claw pinch (melee) |
| **Behavior** | Patrol → charge player on detect |
| **Weakness** | Stomp attack (knockdown) |
| **Drop** | Shell Fragment (craft material) |

### 3.2 Ember Lizard (Island 1)
| Field | Value |
|-------|-------|
| **Tier** | T1-T2 |
| **HP** | 30 |
| **Speed** | Fast |
| **Attack** | Charge → explode on death (2m radius) |
| **Behavior** | Beelines toward player; will sacrifice itself |
| **Weakness** | Ranged harpoon (kill at distance) |
| **Drop** | Ember Shard |
| **Design Note** | Player must learn to keep distance, not fight up close |

### 3.3 Magma Bat (Island 1)
| Field | Value |
|-------|-------|
| **Tier** | T2 |
| **HP** | 25 |
| **Speed** | Fast (aerial) |
| **Attack** | Dive bomb, fire spit (projectile) |
| **Behavior** | Circles overhead, dive attacks if player stays still |
| **Weakness** | Hit during dive animation (brief stun) |
| **Drop** | Wing Membrane (rare) |

### 3.4 Snow Wolf (Island 2)
| Field | Value |
|-------|-------|
| **Tier** | T2 |
| **HP** | 40 |
| **Speed** | Very Fast |
| **Attack** | Bite, pounce (knockdown) |
| **Behavior** | Packs of 3; coordinate flanking |
| **Weakness** | Fire damage |
| **Drop** | Wolf Pelt |
| **Design Note** | First enemy that groups up and coordinates |

### 3.5 Ice Serpent (Island 2)
| Field | Value |
|-------|-------|
| **Tier** | T3 |
| **HP** | 80 |
| **Speed** | Medium |
| **Attack** | Frost breath (cone), tail sweep, freeze spit |
| **Behavior** | Patrol; if player hit by freeze, charges |
| **Weakness** | Fire Dash breaks ice armor |
| **Drop** | Frost Scale (valuable) |

### 3.6 Thorn Sprite (Island 3)
| Field | Value |
|-------|-------|
| **Tier** | T1 |
| **HP** | 15 |
| **Speed** | Very Fast |
| **Attack** | Thorn dart (ranged, low damage) |
| **Behavior** | Hide in plants; emerge when player passes; scatter if hit |
| **Weakness** | AoE attack hits entire cluster |
| **Drop** | Thorn Needle |

### 3.7 Jungle Ape (Island 3)
| Field | Value |
|-------|-------|
| **Tier** | T2-T3 |
| **HP** | 60 |
| **Speed** | Medium-Fast |
| **Attack** | Ground slam (shockwave), rock throw, charge |
| **Behavior** | Territorial; calls for others if alarmed |
| **Weakness** | Dodge the shockwave, attack backside |
| **Drop** | Rare Fruit (health restore) |

### 3.8 Sand Scarab (Island 4)
| Field | Value |
|-------|-------|
| **Tier** | T2 |
| **HP** | 35 |
| **Speed** | Fast (underground: very fast) |
| **Attack** | Burrow → emerge under player; mandible slash |
| **Behavior** | Circles underground, ambushes |
| **Weakness** | Stomp when it emerges (stun window) |
| **Drop** | Carapace Piece |

### 3.9 Storm Imp (Island 5)
| Field | Value |
|-------|-------|
| **Tier** | T2-T3 |
| **HP** | 45 |
| **Speed** | Fast + teleport |
| **Attack** | Lightning bolt (ranged), teleport behind player |
| **Behavior** | Never stays still; teleports every 3 attacks |
| **Weakness** | Grounding rod item stops teleport ability |
| **Drop** | Spark Core |

### 3.10 Storm Ray (Island 5)
| Field | Value |
|-------|-------|
| **Tier** | T3 |
| **HP** | 70 |
| **Speed** | Fast (aerial) |
| **Attack** | Shadow dive (signals on floor), electric shock beam |
| **Behavior** | Glides high, casts shadow telegraph, dives |
| **Weakness** | Harpoon shot during glide phase |
| **Drop** | Ray Wing |

---

## 4. Common Enemies (Sea)

### 4.1 Coral Jellyfish
| Field | Value |
|-------|-------|
| **Tier** | T1 (Sea) |
| **HP** | Boat: 5 damage per contact |
| **Speed** | Drifts (current-based) |
| **Attack** | Passive contact stun — slows boat for 3 seconds |
| **Behavior** | Does not chase; just drifts in clusters |
| **Counter** | Steer around; harpoon to clear path |

### 4.2 Razorfin Shark
| Field | Value |
|-------|-------|
| **Tier** | T2 (Sea) |
| **HP** | Boat: 15 damage per hit |
| **Speed** | Fast |
| **Attack** | Circles boat, then rams from below |
| **Behavior** | Detects boat noise within 40m; follows and rams |
| **Counter** | Boost speed to outrun; harpoon to deter |

### 4.3 Tide Serpent
| Field | Value |
|-------|-------|
| **Tier** | T3 (Sea) |
| **HP** | Boat: 25 damage per hit |
| **Speed** | Medium |
| **Attack** | Surface lunge (knocks boat sideways), coil wrap (stops movement) |
| **Behavior** | Patrols routes; if entered, attacks aggressively |
| **Counter** | Harpoon at head during surface animation |

### 4.4 Frost Crab (Sea, near Island 2)
| Field | Value |
|-------|-------|
| **Tier** | T2 (Sea) |
| **HP** | Boat: 10 damage; freezes boat on contact |
| **Speed** | Slow |
| **Attack** | Claw latch (reduces steering for 5s), ice spit |
| **Behavior** | Ambush from ice formations |
| **Counter** | Fire on latched claw to detach |

### 4.5 Abyssal Kraken Shard
| Field | Value |
|-------|-------|
| **Tier** | T5 (Sea) — Roaming Mini-Boss |
| **HP** | Boat: 50 damage; several hits to repel |
| **Speed** | Medium (slow surface, fast beneath) |
| **Attack** | Tentacle slam on boat, ink cloud (blinds), submerge + grab |
| **Behavior** | Patrols Abyss Gate zone; attacks any boat that enters |
| **Counter** | Harpoon tentacles (3 hits per tentacle); light reveals weak spot |

### 4.6 Deep Leviathan
| Field | Value |
|-------|-------|
| **Tier** | T6 (Sea) — Optional Super-Boss |
| **Description** | Enormous serpent; circles beneath Abyss Gate |
| **Behavior** | Only attacks if player idles in Abyss Gate for 60 seconds |
| **Counter** | Escape by boosting out of zone |
| **Note** | Cannot be defeated; purely an avoidance encounter |

---

## 5. Boss 0 — Driftwood Golem (Miniboss)

### Lore
An ancient guardian built from shipwrecked wood and cursed driftwood, animated by the island's residual magic. A gentle test of the player's combat readiness.

### Stats
| Field | Value |
|-------|-------|
| **HP** | 150 |
| **Arena** | Hilltop Temple (Tutorial Island) |
| **Phases** | 1 (simple pattern) |
| **Weakness** | Glowing crystal on back |

### Attack Pattern

| Attack | Description | Telegraph | Dodge Direction |
|--------|-------------|-----------|-----------------|
| Slow Slam | Raises fist, slams down | Fist glows yellow | Roll sideways |
| Rock Throw | Picks up chunk, throws in arc | Wind-up animation (2s) | Step sideways |
| Stomp Wave | Stomps, shockwave radiates | Foot stamps ground, rumble SFX | Jump or roll back |

### Fight Flow
1. Player sees Golem standing inert; activating puzzle awakens it.
2. Simple 3-attack loop.
3. Player needs to get behind Golem (dodge) to hit crystal on back.
4. After 50 HP, Golem gains a new attack: Spin Sweep.
5. Defeat → crumbles, drops Map Scroll + Compass.

---

## 6. Boss 1 — Ignar the Molten Drake

### Lore
Once a noble fire guardian of Ember Isle's forge, Ignar was driven mad by the shattered Tide Crystal's dark energy. Now a raging, lava-drenched serpentine drake that floods the island in magma.

### Stats
| Field | Value |
|-------|-------|
| **HP** | 600 |
| **Arena** | Caldera Pit (volcanic crater) |
| **Phases** | 3 |
| **Weakness** | Belly weak point (yellow glow); Ice items in arena |
| **Reward** | Fire Tide Crystal + Fire Dash ability |

### Phase 1 (100% → 60% HP) — The Warden
| Attack | Description | Telegraph | Counter |
|--------|-------------|-----------|---------|
| Fire Breath Sweep | Sweeps mouth left-to-right | Inhale animation (1.5s) | Run same direction as sweep |
| Lava Ball Spit | 3 lava balls arc toward player | Mouth glows orange | Dodge between gaps |
| Tail Slam | Swings tail across arena | Tail raises, SFX growl | Roll toward boss |
| Wing Gust | Flaps wings, pushes player toward lava | Spreads wings wide | Crouch / hold ground |

### Phase 2 (60% → 30% HP) — The Inferno
*Transition: Arena lava rises. Some platforms become unavailable.*
| Attack | New / Changed | Description |
|--------|--------------|-------------|
| Lava Dive | New | Ignar dives into lava, re-emerges under player (shadow telegraphs position) |
| Fire Wall | New | Summons ring of fire that closes inward (run outward to escape) |
| Rapid Fire Spit | Upgraded | Now fires 6 lava balls in a spread |

### Phase 3 (30% → 0% HP) — The Berserker
*Transition: Arena cracks; some floor tiles break and fall into lava. Ignar glows red.*
| Attack | New / Changed | Description |
|--------|--------------|-------------|
| Berserker Charge | New | Charges full speed across arena; telegraphed by pawing ground |
| Eruption | New | Lava fountains burst from 5 random floor tiles (visual cue 2s before) |
| Rage Mode | Changed | All attacks 30% faster; shorter telegraph windows |

### Strategy Summary
- Phase 1: Dodge attacks, use Ice item on glowing belly to stun → hit exposed belly.
- Phase 2: Avoid lava pools; watch for dive shadow.
- Phase 3: Prioritize safe footing over offense.

---

## 7. Boss 2 — Kryss the Frozen Titan

### Lore
Kryss was the ancient keeper of Frostveil's glaciers, ensuring the island's water supply. Now frozen solid by the corrupted Tide Crystal, it is a colossal being of living ice that grows larger the more it is damaged.

### Stats
| Field | Value |
|-------|-------|
| **HP** | 750 |
| **Arena** | The Frozen Throne |
| **Phases** | 3 |
| **Weakness** | Fire Dash causes crack damage; glowing chest core |
| **Reward** | Ice Tide Crystal + Ice Shield ability |
| **Special** | Kryss grows visually larger with each phase |

### Phase 1 (100% → 65% HP) — The Glacier
| Attack | Description | Telegraph |
|--------|-------------|-----------|
| Icicle Barrage | 8 icicles rain from above | Red circles on floor |
| Frost Breath | Slow horizontal sweep; leaves ice patches | Mouth opens wide, mist forms |
| Ground Pound | Jumps, lands hard; shockwave | Rises in air (2s hang) |
| Ice Arm Grab | Reaches out to grab player; squeezes | Arm extends slowly |

### Phase 2 (65% → 35% HP) — The Blizzard
*Transition: Floor gains ice patches (slippery). Kryss spawns Ice Clones.*
| Attack | Description |
|--------|-------------|
| Ice Clone Summon | Spawns 2 clones; clones mimic main attack pattern |
| Frost Nova | Expands ice ring outward; freeze floor around boss |
| Snowstorm Whirl | Slow spinning; pulls player in with wind; then shoves |

### Phase 3 (35% → 0% HP) — The Desperate Blizzard
*Transition: Kryss attempts to freeze entire arena. If successful, 5-second escape timer before player frozen.*
| Attack | Description |
|--------|-------------|
| Arena Freeze | Full arena ice wave; player must reach warm torch pedestals |
| Blind Charge | Kryss charges blindly across arena; erratic direction |
| Shard Storm | Spins and releases shards in all directions |

---

## 8. Boss 3 — Virenax the Vine Colossus

### Lore
Virenax was a gentle nature spirit that tended Thornwood's rainforest. The corrupted crystal caused the spirit to merge with the jungle itself, becoming a massive colossus of twisted vines, wood, and thorns.

### Stats
| Field | Value |
|-------|-------|
| **HP** | 800 |
| **Arena** | Root Throne — giant circular clearing |
| **Phases** | 3 |
| **Weakness** | Fire Dash ignites vine segments; exposed heart on chest |
| **Reward** | Nature Tide Crystal + Vine Grapple ability |

### Phase 1 (100% → 60% HP)
| Attack | Description |
|--------|-------------|
| Vine Whip | Sends vine tendrils along ground in a line |
| Root Trap | Roots burst from ground at player position (2s delay) |
| Body Slam | Falls forward; huge AoE |
| Thorn Shower | Rains thorns in small area; tracks player for 2s |

### Phase 2 (60% → 35% HP) — Toxic Mode
*Transition: Virenax grows extra vine arms. Ground poison mist rises slowly.*
| Attack | New |
|--------|-----|
| Poison Spit | Long-range glob; creates poison pool |
| Multi-Whip | All 4 vine arms whip simultaneously |
| Vine Cage | Summons vine cage around player (escape with Fire Dash) |

### Phase 3 (35% → 0% HP) — Frenzy
*Transition: Mist rises to waist height (reduces stamina); Virenax screeches.*
| Attack | New |
|--------|-----|
| Vine Cyclone | Spins body; vine arms sweep 360° |
| Root Eruption | Multiple root bursts across full arena simultaneously |
| Desperate Merge | Colossus partially sinks into ground; attacks from multiple spots |

---

## 9. Boss 4 — Phareth the Stone Warden

### Lore
Phareth was the immortal stone guardian who protected Dunestone Bay's ancient ruins for 3,000 years. When the Tide Crystal corrupted the ruins, Phareth's stone body cracked and dark energy filled the cracks. Now it destroys what it once protected.

### Stats
| Field | Value |
|-------|-------|
| **HP** | 850 |
| **Arena** | The Colosseum of Sand |
| **Phases** | 3 |
| **Weakness** | Water (Water Flask from arena) cracks stone armor; glowing fissures on body |
| **Reward** | Earth Tide Crystal + Sand Veil ability |

### Phase 1 (100% → 65% HP)
| Attack | Description |
|--------|-------------|
| Stone Fist | Slams fist down; craters floor; falling rocks nearby |
| Rock Volley | Picks up chunks of arena floor; throws 3 rocks |
| Sand Tornado | Spins; creates sand funnel; moves toward player |
| Stomp Shockwave | Stomps; ground cracks radiate outward in X pattern |

### Phase 2 (65% → 35% HP) — Subterranean Mode
*Transition: Phareth partially sinks into sand. Only top half visible.*
| Attack | Description |
|--------|-------------|
| Underground Charge | Burrows completely; reappears under player |
| Emerges + Slam | Bursts from ground; shockwave when lands |
| Scarab Summon | Calls 4 Sand Scarabs as distraction |

### Phase 3 (35% → 0% HP) — Crumbling Giant
*Transition: Stone armor cracks fully; glowing core exposed on chest.*
| Attack | New |
|--------|-----|
| Arena Compression | Walls begin sliding inward (reduces available space) |
| Rock Storm | Continuous rock rain in 3 zones that rotate |
| Last Stand | Enrage: speed doubles; all attacks deal 50% more damage |

---

## 10. Boss 5 — Zephyrath the Sky Serpent

### Lore
Zephyrath was the embodiment of the sky above Stormcrest Peak — a graceful aerial serpent that kept storm clouds in balance. Corrupted by the crystal, it now commands uncontrolled storms that lash the entire northern sea.

### Stats
| Field | Value |
|-------|-------|
| **HP** | 900 |
| **Arena** | Summit Altar (open mountaintop) |
| **Phases** | 3 |
| **Weakness** | Grounding Rods (placed by player); disrupts electrical attacks |
| **Reward** | Storm Tide Crystal + Lightning Strike ability |
| **Special** | Flying boss — player uses platforms and grapple to reach attack points |

### Phase 1 (100% → 60% HP)
| Attack | Description |
|--------|-------------|
| Wind Slam | Dives at player; wind gust knocks player off platforms if not anchored |
| Lightning Breath | Breath arcs lightning; zigzag pattern |
| Tail Sweep | Sweeps tail across multiple platforms |
| Cloud Veil | Disappears into clouds; reappears at random platform |

### Phase 2 (60% → 30% HP) — Storm King
*Transition: Storm intensity doubles; rain/wind increases; visibility reduced.*
| Attack | Description |
|--------|-------------|
| Storm Vortex | Creates tornado that lifts player; player must escape via grapple |
| Aerial Spin | Rolls through multiple platforms; must dodge timing |
| Lightning Storm | 6 lightning bolts strike sequential platforms; safe spot moves |

### Phase 3 (30% → 0% HP) — The Final Storm
*Transition: Zephyrath retreats into clouds. Only appears to attack — very hard to predict.*
| Attack | Description |
|--------|-------------|
| Ambush Dive | Appears from random direction with very short telegraph |
| Mega Storm | Arena-wide lightning storm; grounding rods are ONLY safe spots |
| Serpent's Wrath | Full speed charge loop around entire arena 3 times |

---

## 11. Final Boss — The Shattered Sovereign

### Lore
The Shattered Sovereign is what remains of Aethermoor's ancient ruler — a being of pure magical energy, shattered by the original storm and held together by dark crystal energy. It contains aspects of all 6 corrupted guardians and is the source of the eternal storm.

### Stats
| Field | Value |
|-------|-------|
| **HP** | 2,400 (across 4 phases) |
| **Arena** | Aethermoor Core — shifting elemental arena |
| **Phases** | 4 |
| **Weakness** | Use all 5 abilities in order: Fire → Ice → Nature → Sand → Lightning on glowing seals |
| **Reward** | True Ending + Credits |

### Phase 1 (100% → 75% HP) — The Remembered Form
- Cycles through attacks borrowed from each of the 5 bosses.
- One element at a time; pattern is predictable.

### Phase 2 (75% → 50% HP) — The Fractured Form
- Attacks combine two elements simultaneously (e.g., fire + ice = steam burst).
- Arena shifts between two island themes.

### Phase 3 (50% → 25% HP) — The Storm Embodied
- All elemental hazards active simultaneously.
- Must seal 3 of the 5 ability seals to weaken it.

### Phase 4 (25% → 0% HP) — The Final Dissolution
- Goes berserk; attacks become semi-random.
- Arena collapses; unstable footing.
- Player must seal final 2 ability seals on the boss's body directly.
- Final seal triggers the ending cutscene.

---

## 12. AI Behavior Patterns

### State Machine Overview
```
[Idle / Patrol]
      ↓ (detection)
[Alert / Pursue]
      ↓ (in range)
[Combat]
    ├── [Attack A] ← (cooldown)
    ├── [Attack B] ← (HP threshold)
    └── [Attack C] ← (context)
      ↓ (HP = 0)
[Death]
```

### Boss Behavior Decision Tree
```
Evaluate:
  1. Distance to Player
     - Close → Melee attack
     - Medium → Ranged/projectile attack
     - Far → Move toward player / summon
  2. HP Threshold
     - Below 60% → Activate Phase 2 attacks
     - Below 30% → Activate Phase 3 (enrage)
  3. Attack Cooldown
     - If primary attack on cooldown → secondary attack
  4. Arena State
     - Environmental hazards trigger specific attacks
```

### Difficulty Modifiers
| Mode | HP Multiplier | Damage Multiplier | Telegraph Duration |
|------|--------------|-------------------|-------------------|
| Easy | 0.75x | 0.75x | +50% longer |
| Normal | 1.0x | 1.0x | Standard |
| Hard | 1.25x | 1.3x | Standard |
| Challenge | 1.5x | 1.6x | -25% shorter |

---

## 13. Balancing Guidelines

### Boss Fight Duration Targets
| Boss | Target Duration (Normal) |
|------|--------------------------|
| Driftwood Golem | 2–4 minutes |
| Ignar | 5–8 minutes |
| Kryss | 6–9 minutes |
| Virenax | 7–10 minutes |
| Phareth | 7–10 minutes |
| Zephyrath | 8–12 minutes |
| The Shattered Sovereign | 12–20 minutes |

### Hit Feel Guidelines
- Player hit feedback: screen flash (red tint), camera shake (small), SFX hit sound.
- Player death: slow-motion 0.5s, death animation, game over screen.
- Boss hit feedback: hitflash on boss model, SFX impact, HP bar updates.
- Phase transition: cinematic camera cut, boss scream SFX, particle burst, arena transformation.

### Dodge Window Tuning
- Player invincibility frames during dodge: 8 frames (0.13s at 60fps).
- Enemy attack active frames: minimum 10 frames (gives player reaction time).
- All attacks telegraphed minimum 0.5s before active frames.

---

*Document Version: 1.0 | Last Updated: March 2026*
