# Game Design Document (GDD)
## Project: Isle of Trials — An Adventurous Puzzle Game

---

## Table of Contents
1. [Game Overview](#game-overview)
2. [Story & Narrative](#story--narrative)
3. [Core Gameplay Loop](#core-gameplay-loop)
4. [Player Mechanics](#player-mechanics)
5. [World Structure](#world-structure)
6. [Art Direction](#art-direction)
7. [Audio Direction](#audio-direction)
8. [Monetization & Progression](#monetization--progression)
9. [Target Audience](#target-audience)
10. [Platform & Genre](#platform--genre)

---

## 1. Game Overview

**Title:** Isle of Trials  
**Genre:** Adventure Puzzle  
**Platform:** PC (Windows/Mac), Mobile (iOS/Android)  
**Engine:** Unity 2022 LTS or higher  
**Player Count:** Single Player  
**Estimated Playtime:** 10–15 hours (main story), 20+ hours (100% completion)

**Elevator Pitch:**  
Isle of Trials is a top-down adventure puzzle game where the player navigates a vast mystical ocean on a boat, discovering hidden islands, each governed by a fearsome Boss and guarded by sea creatures and environmental puzzles. To unlock a path to the final island, the player must defeat all bosses and solve every island's mysteries.

---

## 2. Story & Narrative

### 2.1 Background
Long ago, the Archipelago of Aethermoor was a thriving civilization powered by six magical Tide Crystals. A catastrophic storm shattered the crystals, scattering them across six islands. Ancient guardians — twisted by dark energy — now protect each shard.

### 2.2 Player Character
**Name:** Kael (customizable)  
**Role:** A young sailor and puzzle-solver who discovers a mysterious map leading to the Archipelago.  
**Goal:** Collect all six Tide Crystals, defeat the island bosses, and restore the Aethermoor lighthouse to end the eternal storm.

### 2.3 Story Beats

| Act | Description |
|-----|-------------|
| Act 1 | Kael finds the map, sets sail, and reaches the first island (tutorial island). |
| Act 2 | Kael explores 4 major islands, each with unique challenges and a boss fight. |
| Act 3 | The true nature of the storm is revealed — a final hidden island with the ultimate boss. |
| Epilogue | Aethermoor is restored; each island is freed from the curse. |

### 2.4 Tone
- Lighthearted exploration mixed with tense boss encounters.
- Mystery-driven storytelling through environmental clues, messages in bottles, and NPC fishermen.
- No dialogue text walls — story told through cutscenes and environment.

---

## 3. Core Gameplay Loop

```
Sail on Sea
    ↓
Discover Island
    ↓
Explore Island (Collect clues, solve entry puzzle)
    ↓
Navigate Island Challenges (Puzzles, traps, sea creature encounters)
    ↓
Defeat Island Boss
    ↓
Collect Tide Crystal + Rewards
    ↓
Return to Sea / Find Next Island
    ↓
(Repeat until all 6 islands cleared)
    ↓
Final Island Unlocked → Final Boss → Ending
```

---

## 4. Player Mechanics

### 4.1 Boat Mechanics
| Mechanic | Description |
|----------|-------------|
| **Sailing** | WASD / joystick to steer; wind direction affects speed |
| **Boost** | Short speed burst; limited charges, recharges over time |
| **Anchor** | Stop the boat to interact with floating objects |
| **Harpoon** | Shoot at sea creatures or grapple distant objects |
| **Lantern** | Illuminate dark waters; reveals hidden paths |

### 4.2 On-Island Mechanics
| Mechanic | Description |
|----------|-------------|
| **Move** | WASD / joystick |
| **Interact** | E / A button — interact with levers, symbols, NPCs |
| **Attack** | Left Click / X button — basic melee attack |
| **Special Ability** | Right Click / Y button — island-specific ability unlocked per island |
| **Dodge** | Shift / B button |
| **Inspect** | F / LB — examine environmental clues |

### 4.3 Player Stats
- **Health:** 100 HP (upgradeable)
- **Stamina:** Used for dodge and sprint
- **Boat Durability:** Takes damage from sea hazards
- **Inventory:** 10 slots; consumables, keys, puzzle items

### 4.4 Progression
- Defeating a boss unlocks a new **special ability** for future islands.
- Crystals collected upgrade the boat's stats.
- Hidden chests and collectibles provide cosmetic upgrades.

---

## 5. World Structure

### 5.1 The Open Sea
- Semi-open world ocean with fog-of-war obscuring undiscovered islands.
- Dynamic weather: calm, stormy, foggy.
- Sea creatures patrol certain zones.
- Floating debris and messages in bottles contain lore and hints.
- Day/night cycle affecting visibility and enemy behavior.

### 5.2 Islands Overview

| Island # | Name | Theme | Boss |
|----------|------|-------|------|
| 0 | Driftwood Cay | Tutorial / Tropical | None (miniboss) |
| 1 | Ember Isle | Volcanic / Fire | Ignar the Molten Drake |
| 2 | Frostveil Atoll | Arctic / Ice | Kryss the Frozen Titan |
| 3 | Thornwood Reach | Jungle / Nature | Virenax the Vine Colossus |
| 4 | Dunestone Bay | Desert / Ancient Ruins | Phareth the Stone Warden |
| 5 | Stormcrest Peak | Storm / Lightning | Zephyrath the Sky Serpent |
| 6 | Aethermoor (Final) | Mystical / All Elements | The Shattered Sovereign |

### 5.3 Sea Zones
- **Safe Shallows:** Near starter island, no threats.
- **Coral Reefs:** Navigate carefully; sea creatures patrol.
- **Deep Abyss Channels:** High-threat zones with giant sea creatures.
- **Storm Belts:** Hazardous wind/wave zones between major islands.

---

## 6. Art Direction

### 6.1 Visual Style
- **Style:** Stylized 3D (similar to Zelda: Wind Waker meets Hades).
- **Color Palette:** Each island has a unique dominant color scheme.
- **Lighting:** Dynamic lighting with volumetric fog over the ocean.

### 6.2 Character Design
- Player character: Adventurous, practical sailor outfit, upgradeable visually.
- Bosses: Massive, environment-themed, iconic silhouettes.
- Sea Creatures: Based on mythological sea monsters (Kraken-kin, Leviathan shards, etc.).

### 6.3 UI Style
- Minimal HUD — health shown as a nautical compass/life ring.
- Diegetic inventory (chest on the boat).
- Map as a physical parchment the player opens.

---

## 7. Audio Direction

### 7.1 Music
| Context | Style |
|---------|-------|
| Open Sea — Calm | Soft orchestral, ocean ambiance |
| Open Sea — Storm | Intense strings, percussion |
| Island Exploration | Theme-specific (fire drums, ice chimes, jungle flutes) |
| Boss Fight | Epic cinematic orchestral with theme motif |
| Victory | Triumphant short fanfare |
| Cutscenes | Atmospheric, narrative-driven orchestral |

### 7.2 Sound Effects
- Realistic ocean SFX: waves, seagulls, whale calls.
- Puzzle interaction feedback sounds.
- Boss-specific roars and attack sounds.
- Boat damage and repair sounds.

---

## 8. Monetization & Progression

**Model:** One-time purchase (premium).  
**No pay-to-win mechanics.**  
**Optional DLC:** Additional islands and cosmetic packs.

---

## 9. Target Audience
- **Primary:** Ages 13–35, fans of puzzle-adventure games.
- **Secondary:** Casual gamers who enjoy exploration.
- **Inspired by:** The Legend of Zelda: Wind Waker, Subnautica, Sea of Thieves (toned down), Portal.

---

## 10. Platform & Genre
- **Primary Platform:** PC (Steam)
- **Secondary:** Nintendo Switch, Mobile
- **Genre Tags:** Puzzle, Adventure, Action, Exploration, Nautical

---

*Document Version: 1.0 | Last Updated: March 2026*
