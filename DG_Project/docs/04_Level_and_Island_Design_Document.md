# Level & Island Design Document
## Isle of Trials — All Islands, Zones & Layouts

---

## Table of Contents
1. [Design Principles](#design-principles)
2. [Ocean World Layout](#ocean-world-layout)
3. [Island 0 — Driftwood Cay (Tutorial)](#island-0--driftwood-cay-tutorial)
4. [Island 1 — Ember Isle](#island-1--ember-isle)
5. [Island 2 — Frostveil Atoll](#island-2--frostveil-atoll)
6. [Island 3 — Thornwood Reach](#island-3--thornwood-reach)
7. [Island 4 — Dunestone Bay](#island-4--dunestone-bay)
8. [Island 5 — Stormcrest Peak](#island-5--stormcrest-peak)
9. [Island 6 — Aethermoor (Final)](#island-6--aethermoor-final)
10. [Sea Zones & Encounters](#sea-zones--encounters)

---

## 1. Design Principles

### Core Level Design Philosophy
1. **Teach before Test** — Every mechanic is introduced safely before being used in a dangerous context.
2. **Layered Complexity** — Early islands are simple, later islands combine multiple puzzle types.
3. **Exploration Reward** — Hidden paths, collectibles, and lore are placed for curious players.
4. **Environmental Storytelling** — The state of each island tells the story of its fall.
5. **Pacing** — Each island follows: Arrive → Explore → Puzzle → Combat → Boss → Reward.

### Island Layout Formula
```
[Entry Beach / Dock Area]
        ↓
[Outdoor Exploration Zone (2-3 areas)]
        ↓
[Inner Sanctum / Temple / Dungeon]
        ↓
[Pre-Boss Challenge Room]
        ↓
[Boss Arena]
        ↓
[Crystal Chamber (reward)]
```

---

## 2. Ocean World Layout

### 2.1 Map Layout (Top-Down View)
```
                    [ Island 5: Stormcrest ]
                           |
  [ Island 2: Frost ] --- [ OPEN SEA ] --- [ Island 1: Ember ]
                    \         |         /
                     \   [ Island 0 ] /
                      \   (Tutorial)  /
                       \      |      /
                        [ Player Start ]
                              |
             [ Island 3: Jungle ] --- [ Island 4: Desert ]
                              |
                    [ Island 6: Aethermoor ]
                         (Hidden / Locked)
```

### 2.2 Sea Zones Between Islands

| Zone Name | Location | Hazards | Notes |
|-----------|----------|---------|-------|
| Safe Shallows | Around tutorial island | None | Tutorial sailing area |
| Coral Passage | East of tutorial | Coral reefs, Jellyfish | First natural obstacle |
| Ember Straits | West, toward Ember Isle | Razorfin Sharks, Lava Rocks | Boats need repair kit |
| Ice Drift | Northwest | Iceberg fields, Tide Serpents | Reduced visibility |
| Canopy Current | South | Vine ambush (from water), Serpents | Strong current |
| Sand Swell | Southeast | Buried sand traps, ancient ruins in water | Ancient wrecks to explore |
| Storm Belt | North | Lightning storms, Storm Rays | Very high danger |
| Abyss Gate | Center-South | Abyssal Kraken, pitch darkness | Requires Lantern + full gear |

---

## 3. Island 0 — Driftwood Cay (Tutorial)

### Overview
| Field | Details |
|-------|---------|
| **Theme** | Tropical, bright, colorful |
| **Difficulty** | Very Easy (Tutorial) |
| **Boss** | None — Miniboss: Driftwood Golem |
| **Crystal** | None — unlock: Compass & Map |
| **Key Mechanic Introduced** | Basic movement, interact, attack, puzzle basics |

### Areas

#### Area 1: Sandy Beach
- Player arrives by boat, docks at pier.
- **Teaching moment:** Movement, camera.
- Friendly fisherman NPC gives basic instructions.
- Find a broken crate with **Inventory tutorial** item inside.

#### Area 2: Coconut Palm Grove
- Light platforming (step over logs, duck under branches).
- **Teaching moment:** Jump and dodge.
- First enemy: Driftwood Crab (very weak, slow).
- Hidden path: Behind waterfall → leads to collectible.

#### Area 3: Old Shack Ruins
- **First Puzzle:** Push Box onto pressure plate → opens door.
- Lore item found inside (message in a bottle).
- Chest with first **health upgrade**.

#### Area 4: Hilltop Temple
- Winding path up hill, tougher Driftwood Crabs.
- **Entry Puzzle:** Light all 4 torches using a torch you carry.
- Inside temple: Miniboss — Driftwood Golem.

#### Miniboss: Driftwood Golem
- Pattern: Slow slam, rock throw.
- Weakness: Hit the glowing crystal on its back.
- Reward: Map Scroll (unlocks ocean map) + Compass.

### Layout Diagram
```
[Pier / Dock] → [Sandy Beach] → [Palm Grove]
                                      ↓
                              [Old Shack Ruins]
                                      ↓
                              [Hill Path (Combat)]
                                      ↓
                              [Hilltop Temple + Golem]
```

---

## 4. Island 1 — Ember Isle

### Overview
| Field | Details |
|-------|---------|
| **Theme** | Volcanic, fire, magma |
| **Difficulty** | Easy |
| **Boss** | Ignar the Molten Drake |
| **Crystal** | Fire Tide Crystal |
| **Ability Unlocked** | Fire Dash |
| **Color Palette** | Oranges, reds, blacks |

### Areas

#### Area 1: Ash Shore
- Volcanic beach with black sand, red sky.
- Enemies: Ember Lizards (run toward player, explode on death).
- Teaching moment: Don't let them explode near you → dodge timing.
- Environmental Hazard: Random lava spurts from ground.

#### Area 2: Lava River Crossing
- Must use stone platforms that bob in lava.
- **Puzzle:** Activate 3 switches in order to raise platforms.
- Enemy: Magma Bat (aerial, requires timing to hit).

#### Area 3: Ignar's Forge (Underground)
- Indoor area — forge/workshop aesthetic.
- **Main Puzzle:** Redirect steam jets using pipe valves to cool a path of lava.
- Lore: Ancient fire-wielders who lived here.

#### Area 4: Dragon's Gullet (Pre-Boss)
- Narrow canyon, lava walls closing in as player runs.
- Sprint mechanic tested here.
- Last checkpoint before boss.

#### Boss Arena: Caldera Pit
- Circular arena with lava pools around edges.
- Rising lava mechanic in Phase 2.

### Boss: Ignar the Molten Drake
| Phase | HP | Attacks |
|-------|----|----|
| Phase 1 | 100% → 60% | Fire breath sweep, tail slam, lava ball spit |
| Phase 2 | 60% → 30% | Lava rises; gains dive attack; faster movement |
| Phase 3 | 30% → 0% | Arena cracks; platforms fall; berserker charge |

**Weakness:** Ice (use ice crystals found in arena) → apply to weak point on belly.

---

## 5. Island 2 — Frostveil Atoll

### Overview
| Field | Details |
|-------|---------|
| **Theme** | Arctic, ice caves, tundra |
| **Difficulty** | Easy-Medium |
| **Boss** | Kryss the Frozen Titan |
| **Crystal** | Ice Tide Crystal |
| **Ability Unlocked** | Ice Shield |
| **Color Palette** | Blues, whites, cyan, silver |

### Areas

#### Area 1: Frozen Docklands
- Slippery ice physics on floor.
- **Teaching moment:** Ice slide physics (players slip further).
- Enemies: Snow Wolves (fast, pack tactics).
- Igloo NPC gives backstory.

#### Area 2: Glacier Caverns
- Dark cave system, illuminated by glowing ice crystals.
- **Puzzle:** Slide ice blocks into correct positions to unblock paths.
- Ice Serpent patrols inside.

#### Area 3: Frost Cathedral
- Grand frozen temple interior.
- **Main Puzzle:** Light beam refraction using ice prisms.
- Three beams must all hit the central altar simultaneously.

#### Area 4: Blizzard Pass (Pre-Boss)
- Outdoor blizzard zone; extremely low visibility.
- Follow glowing ice markers to navigate.
- Wind pushback forces careful movement.

#### Boss Arena: The Frozen Throne
- Throne room encased in ice.
- Kryss grows as HP decreases (phase visual change).

### Boss: Kryss the Frozen Titan
| Phase | HP | Attacks |
|-------|----|----|
| Phase 1 | 100% → 65% | Icicle throw, frost breath, ground slam |
| Phase 2 | 65% → 35% | Freeze pools on floor; adds Ice Clone minions |
| Phase 3 | 35% → 0% | Full arena freeze attempt; charges blindly |

**Weakness:** Fire Dash ability (from Island 1) stuns Kryss temporarily.

---

## 6. Island 3 — Thornwood Reach

### Overview
| Field | Details |
|-------|---------|
| **Theme** | Dense jungle, overgrown ruins, nature |
| **Difficulty** | Medium |
| **Boss** | Virenax the Vine Colossus |
| **Crystal** | Nature Tide Crystal |
| **Ability Unlocked** | Vine Grapple |
| **Color Palette** | Deep greens, gold, brown |

### Areas

#### Area 1: Mangrove Landing
- Dense canopy; limited visibility.
- Enemies: Thorn Sprites (small, fast, ambush from plants).
- **Teaching moment:** Use light to detect hidden enemies.

#### Area 2: Ancient Overgrown Ruins
- Temple ruins covered in vines.
- **Puzzle:** Cut vines in specific order to open paths.
- Wrong order resets and spawns enemies.

#### Area 3: Canopy Level
- Vertical exploration: player must climb vines, use grapple points.
- **Vine Grapple** ability introduced here (anchor points on ceiling).
- Platforming challenge above a deep chasm.

#### Area 4: Heart of the Jungle
- Huge open clearing; ancient altar in center.
- **Main Puzzle:** Plant seeds in correct soil patches using clues from environment. Flowers grow to reveal hidden symbols → matches lock pattern.

#### Boss Arena: Root Throne
- Giant root structure arena.
- Ground covered in thick roots that block movement.

### Boss: Virenax the Vine Colossus
| Phase | HP | Attacks |
|-------|----|----|
| Phase 1 | 100% → 60% | Vine whip, root trap (roots burst from ground), slam |
| Phase 2 | 60% → 35% | Sprouts extra vine arms; moves faster; poison spit |
| Phase 3 | 35% → 0% | Arena fills with rising poison mist; frenzy mode |

**Weakness:** Fire (Fire Dash ignites vines temporarily, creating windows to attack).

---

## 7. Island 4 — Dunestone Bay

### Overview
| Field | Details |
|-------|---------|
| **Theme** | Desert, ancient ruins, archaeology |
| **Difficulty** | Medium-Hard |
| **Boss** | Phareth the Stone Warden |
| **Crystal** | Earth Tide Crystal |
| **Ability Unlocked** | Sand Veil |
| **Color Palette** | Sandy yellows, terracotta, gold |

### Areas

#### Area 1: Desert Shore
- Scorching heat; stamina drains faster outdoors.
- Find water flask (consumable) near wrecked ship.
- Enemies: Sand Scarabs (burrow underground, ambush).

#### Area 2: Excavation Site
- Ancient dig site with scaffolding and tunnels.
- **Puzzle:** Flip statues to face correct compass direction based on star map clue.
- Archaeologist ghost NPC gives cryptic hints.

#### Area 3: Crypt Labyrinth
- Underground maze lit by torches.
- **Puzzle:** Hieroglyph sequence — press wall panels in correct order (shown on ceiling fresco).
- Trap rooms with rolling boulders.

#### Area 4: Sky Observatory
- Top of a ruined ziggurat.
- **Main Puzzle:** Align telescope lenses and mirrors to project light onto a specific floor mosaic at "noon" (Day/Night system).

#### Boss Arena: The Colosseum of Sand
- Open-air circular arena; shifting sand floor (traction reduced).

### Boss: Phareth the Stone Warden
| Phase | HP | Attacks |
|-------|----|----|
| Phase 1 | 100% → 65% | Stone fist slam, rock projectiles, sand tornado |
| Phase 2 | 65% → 35% | Partial underground movement; pops up under player |
| Phase 3 | 35% → 0% | Arena walls close in; spawns scarab minions; enrages |

**Weakness:** Water (Use water flask items in arena to crack stone armor).

---

## 8. Island 5 — Stormcrest Peak

### Overview
| Field | Details |
|-------|---------|
| **Theme** | Mountain peak, storm, electricity |
| **Difficulty** | Hard |
| **Boss** | Zephyrath the Sky Serpent |
| **Crystal** | Storm Tide Crystal |
| **Ability Unlocked** | Lightning Strike |
| **Color Palette** | Dark purples, electric blue, silver, stormcloud grey |

### Areas

#### Area 1: Stormcliff Base
- Rain and wind; constant knockback from gusts.
- Enemies: Storm Imps (teleport around, throw lightning bolts).
- **Teaching moment:** Grounding rods reduce damage in lightning zones.

#### Area 2: Thunder Canyon
- Narrow path; lightning strikes at intervals (visual telegraph before strike).
- **Puzzle:** Route electricity through a circuit board of wire segments to open gate.

#### Area 3: Skybridge Ruins
- Crumbling bridge crossing above storm clouds.
- Platform sections collapse after weight.
- Enemy: Storm Ray (aerial, dive-bombs player).

#### Area 4: Lightning Spire Interior
- **Main Puzzle:** Charge capacitors in correct order and sequence to power the door.
- Giant Tesla coils fire across the room — must time movement.

#### Boss Arena: Summit Altar
- Open mountaintop; exposed to storm.
- Flying boss fight — platform jumping required.

### Boss: Zephyrath the Sky Serpent
| Phase | HP | Attacks |
|-------|----|----|
| Phase 1 | 100% → 60% | Wind slam, lightning breath, tail sweep |
| Phase 2 | 60% → 30% | Summons storm vortex; lifts player; aerial attacks |
| Phase 3 | 30% → 0% | Dives into storm clouds; ambushes from random directions |

**Weakness:** Grounding rod items (placed in arena by player, drains boss HP on contact).

---

## 9. Island 6 — Aethermoor (Final Island)

### Overview
| Field | Details |
|-------|---------|
| **Theme** | All elements combined; ethereal, crumbling civilization |
| **Difficulty** | Very Hard |
| **Boss** | The Shattered Sovereign |
| **Crystal** | All 6 crystals restored into one |
| **Ability Unlocked** | All abilities combined (Ultimate Form) |
| **Color Palette** | All island colors swirling; crystalline, prismatic |

### Areas

#### Area 1: Causeway of Memories
- All past island environments blend together.
- Ghost echoes of past inhabitants.
- **Memory Puzzle:** Replay sequences of symbols from each island's puzzle (test of all previous knowledge).

#### Area 2: Crystal Sanctum
- Puzzle using all 5 abilities in sequence to navigate.
- Combines: Fire Dash gaps, Ice Shield deflection, Vine Grapple, Sand Veil stealth, Lightning Strike targets.

#### Area 3: The Shattered Hall
- Boss ante-chamber.
- All 6 Tide Crystal slots must be filled (automatically fills as player arrives with all crystals).
- Cutscene: Sovereign awakens.

#### Final Boss Arena: Aethermoor Core
- Shifting arena combining elements of all boss arenas.
- Multi-phase with all element types.

### Final Boss: The Shattered Sovereign
| Phase | HP | Attacks | Element |
|-------|----|----|---|
| Phase 1 | 100% → 75% | All basic boss attacks from previous bosses | Random |
| Phase 2 | 75% → 50% | Two elements simultaneously; arena shifts | Mixed |
| Phase 3 | 50% → 25% | Full arena transformation; all hazards active | All |
| Phase 4 | 25% → 0% | Desperate mode; one-shot mechanics; pure chaos | Ultimate |

**Weakness:** Use all 5 abilities in correct elemental order corresponding to crystal slots.

---

## 10. Sea Zones & Encounters

### Random Sea Events (while sailing)
| Event | Description | Frequency |
|-------|-------------|-----------|
| Message in Bottle | Lore / hint for next island | Common |
| Treasure Chest (floating) | Random item drop | Uncommon |
| Shipwreck | Small exploration mini-scene | Rare |
| Sea Creature Attack | Creature chases/attacks boat | Varies by zone |
| Merchant Ship | Trade items for upgrades | Uncommon |
| Storm Surge | Sudden storm, high waves | Zone-dependent |
| Lost Sailor NPC | Side quest / extra lore | Rare |
| Whale Pod | Peaceful; follow for hidden island fragment | Very Rare |

### Sea Creature Encounter Zones
| Zone | Creatures | Threat Level |
|------|-----------|-------------|
| Safe Shallows | None | None |
| Coral Passage | Jellyfish, small sharks | Low |
| Ember Straits | Razorfin Sharks, Lava Eels | Medium |
| Ice Drift | Ice Serpents, Frost Crabs | Medium |
| Canopy Current | River Serpents, Ambush Vines | Medium-High |
| Storm Belt | Storm Rays, Thunder Eels | High |
| Abyss Gate | Abyssal Kraken, Deep Leviathan | Extreme |

---

*Document Version: 1.0 | Last Updated: March 2026*
