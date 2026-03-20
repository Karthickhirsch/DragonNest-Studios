# IsleTrial — ScriptableObject Data Sheet
**All enemy, boss, weapon, and item values for Unity Inspector**

---

## How to Use

1. Create each asset: `Right-click in Project → Create → IsleTrial → [type]`
2. Name the file exactly as shown in the **Asset Name** column
3. Fill in Inspector values from the tables below

---

## 1. EnemyData Assets

> Path: `Assets/ScriptableObjects/EnemyData/`

### Tutorial Isle Enemies

| Asset Name | MaxHealth | MoveSpeed | AttackDamage | AttackRange | DetectRange | XPReward | Level |
|---|---|---|---|---|---|---|---|
| `TutorialCrab_Data` | 30 | 2.0 | 5 | 1.2 | 8 | 10 | 1 |
| `TutorialSlime_Data` | 20 | 1.5 | 3 | 1.0 | 6 | 8 | 1 |
| `TutorialGull_Data` | 15 | 5.0 | 4 | 1.5 | 12 | 12 | 1 |

### Ember Isle Enemies

| Asset Name | MaxHealth | MoveSpeed | AttackDamage | AttackRange | DetectRange | XPReward | Level |
|---|---|---|---|---|---|---|---|
| `EmberLizard_Data` | 120 | 4.5 | 22 | 2.0 | 15 | 85 | 8 |
| `LavaCrab_Data` | 90 | 2.5 | 18 | 1.5 | 10 | 60 | 7 |
| `AshWraith_Data` | 70 | 6.0 | 15 | 1.8 | 18 | 70 | 8 |
| `MagmaToad_Data` | 110 | 2.0 | 25 | 1.2 | 8 | 75 | 8 |
| `CinderHound_Data` | 85 | 6.5 | 18 | 1.8 | 20 | 65 | 7 |
| `ObsidianGolem_Data` | 200 | 1.5 | 35 | 2.5 | 12 | 120 | 9 |

### Frost Isle Enemies

| Asset Name | MaxHealth | MoveSpeed | AttackDamage | AttackRange | DetectRange | XPReward | Level |
|---|---|---|---|---|---|---|---|
| `FrostSlug_Data` | 140 | 1.8 | 20 | 1.5 | 12 | 90 | 10 |
| `IceCrawler_Data` | 80 | 3.5 | 16 | 1.4 | 14 | 65 | 10 |
| `SnowSerpent_Data` | 100 | 5.5 | 22 | 2.2 | 16 | 80 | 11 |
| `GlacierWalker_Data` | 160 | 2.0 | 28 | 2.0 | 10 | 100 | 11 |
| `FrostPhantom_Data` | 60 | 7.0 | 12 | 1.6 | 20 | 70 | 10 |

### Mystery Isle Enemies

| Asset Name | MaxHealth | MoveSpeed | AttackDamage | AttackRange | DetectRange | XPReward | Level |
|---|---|---|---|---|---|---|---|
| `ShadowHound_Data` | 95 | 7.5 | 20 | 2.0 | 22 | 95 | 13 |
| `StoneGuardian_Data` | 220 | 1.2 | 38 | 2.8 | 10 | 130 | 14 |
| `VoidWraith_Data` | 75 | 8.0 | 18 | 1.8 | 25 | 100 | 13 |
| `RuneSpider_Data` | 65 | 6.0 | 14 | 1.5 | 16 | 80 | 13 |
| `CurseBlob_Data` | 55 | 2.5 | 10 | 1.2 | 8 | 60 | 12 |

### Sunken Temple Enemies

| Asset Name | MaxHealth | MoveSpeed | AttackDamage | AttackRange | DetectRange | XPReward | Level |
|---|---|---|---|---|---|---|---|
| `DeepFishman_Data` | 110 | 4.0 | 24 | 2.0 | 14 | 100 | 15 |
| `CoralSentinel_Data` | 180 | 2.0 | 32 | 2.5 | 12 | 120 | 15 |
| `AbyssalJelly_Data` | 50 | 3.0 | 12 | 1.0 | 10 | 75 | 14 |
| `SeaWitch_Data` | 120 | 5.0 | 28 | 8.0 | 20 | 110 | 16 |

### Ocean Enemies

| Asset Name | MaxHealth | MoveSpeed | AttackDamage | AttackRange | DetectRange | XPReward | Level |
|---|---|---|---|---|---|---|---|
| `PirateSailor_Data` | 100 | 3.5 | 20 | 2.5 | 20 | 70 | varies |
| `SeaSerpent_Data` | 350 | 6.0 | 45 | 3.0 | 30 | 200 | 12 |
| `KrakenTentacle_Data` | 80 | 1.0 | 15 | 2.0 | 5 | 50 | 14 |
| `GhostShip_Data` | 500 | 4.0 | 60 | 10.0 | 40 | 300 | 16 |

### Generic Enemies

| Asset Name | MaxHealth | MoveSpeed | AttackDamage | AttackRange | DetectRange | XPReward | Level |
|---|---|---|---|---|---|---|---|
| `MimicChest_Data` | 150 | 4.0 | 30 | 1.8 | 2 | 120 | varies |
| `BirdSkeleton_Data` | 40 | 8.0 | 12 | 1.2 | 18 | 45 | varies |

---

## 2. BossData Assets

> Path: `Assets/ScriptableObjects/BossData/`

| Asset Name | MaxHealth | Phase2Threshold | Phase3Threshold | BaseAttackDamage | ArenaRadius | XPReward |
|---|---|---|---|---|---|---|
| `Ignar_Data` | 1200 | 0.66 | 0.33 | 55 | 25.0 | 1500 |
| `Glaciara_Data` | 1000 | 0.66 | 0.33 | 48 | 20.0 | 1400 |
| `MyceliumKing_Data` | 800 | 0.50 | 0.25 | 40 | 18.0 | 1200 |
| `GrandNavigator_Data` | 900 | 0.60 | 0.30 | 45 | 22.0 | 1300 |
| `KrakenChest_Data` | 600 | 0.50 | — | 38 | 15.0 | 1000 |
| `DreadAdmiral_Data` | 1100 | 0.66 | 0.33 | 52 | 24.0 | 1450 |
| `CoralTitan_Data` | 1400 | 0.66 | 0.33 | 60 | 28.0 | 1600 |

### Boss Phase Attack Damage Multipliers

| Boss | Phase 1 | Phase 2 | Phase 3 |
|---|---|---|---|
| Ignar | 1.0× | 1.4× | 1.8× |
| Glaciara | 1.0× | 1.35× | 1.75× |
| MyceliumKing | 1.0× | 1.3× | 1.6× |
| GrandNavigator | 1.0× | 1.4× | 1.9× |
| CoralTitan | 1.0× | 1.5× | 2.0× |

### Ignar MoltenDrake — Phase Abilities

| Phase | Ability | Damage | Cooldown | Range |
|---|---|---|---|---|
| 1 | Bite | 55 | 3.0 s | 4.0 m |
| 1 | Claw Swipe | 40 | 2.0 s | 3.5 m |
| 1 | Tail Slam | 50 | 5.0 s | 5.0 m (arc) |
| 1-3 | Fire Breath | 25 /tick | 8.0 s | 12.0 m (cone) |
| 2 | Wing Slam | 70 | 6.0 s | 6.0 m |
| 2 | Lava Ball | 60 | 4.5 s | 20.0 m |
| 3 | Lava Eruption Slam | 120 | 10.0 s | 8.0 m (AoE) |

### Glaciara FrostWarden — Phase Abilities

| Phase | Ability | Damage | Cooldown | Range |
|---|---|---|---|---|
| 1 | Fist Slam L/R | 48 | 2.5 s | 3.5 m |
| 1-3 | Ice Shard | 35 | 2.0 s | 15.0 m |
| 2 | Double Fist Slam | 80 | 5.0 s | 4.0 m (AoE) |
| 2 | Ice Wall | 0 dmg | 8.0 s | 12.0 m (blocks) |
| 2-3 | Crown Flare | 40 each bolt | 6.0 s | 360° |
| 3 | Blizzard | 20 /tick | 15.0 s | 10.0 m (AoE) |
| 3 | Permafrost | Freeze 3s | 12.0 s | 8.0 m |

---

## 3. ItemData Assets

> Path: `Assets/ScriptableObjects/ItemData/`

### Consumables

| Asset Name | DisplayName | Description | StackSize | DropWeight | HealAmount |
|---|---|---|---|---|---|
| `HealthPotion_Data` | Health Potion | Restores 50 HP | 10 | 0.40 | 50 |
| `LargeHealthPotion_Data` | Large Potion | Restores 100 HP | 5 | 0.15 | 100 |
| `RepairKit_Data` | Repair Kit | Repairs 30 boat HP | 5 | 0.25 | 0 |
| `LargeRepairKit_Data` | Full Repair Kit | Fully repairs boat | 3 | 0.08 | 0 |

### Crafting / Currency Materials

| Asset Name | DisplayName | Description | StackSize | Value (coins) |
|---|---|---|---|---|
| `EmberCrystal_Data` | Ember Crystal | From Ember Isle — enhances fire abilities | 20 | 50 |
| `FrostCrystal_Data` | Frost Crystal | From Frost Isle — enhances ice resistance | 20 | 50 |
| `MystCrystal_Data` | Mystery Crystal | From Mystery Isle — unlocks hidden paths | 20 | 80 |
| `RareCrystal_Data` | Rare Soul Crystal | Toran's chains — key story item | 1 | 0 |
| `SoulEssence_Data` | Soul Essence | Dropped by spectral enemies | 30 | 30 |
| `CompassShard_Data` | Compass Shard | Pieces of Toran's compass | 1 | 0 |
| `AncientMap_Data` | Ancient Map Fragment | Reveals hidden islands | 5 | 200 |
| `BoatPlank_Data` | Boat Plank | Boat repair material (manual) | 20 | 15 |
| `Rope_Data` | Rope | Boat repair + docking | 20 | 10 |
| `IronNail_Data` | Iron Nail | Boat repair material | 30 | 5 |
| `GoldCoin_Data` | Gold Coin | Currency for NPC shops | 999 | 1 |

### Weapons

| Asset Name | DisplayName | BaseDamage | AttackSpeed | Rarity | Unlock Condition |
|---|---|---|---|---|---|
| `Weapon_Cutlass_Data` | Kael's Cutlass | 25 | 1.2 | Common | Start |
| `Weapon_CompassBlade_Data` | Compass Blade | 35 | 1.0 | Rare | Tutorial boss |
| `Weapon_AncientTrident_Data` | Ancient Trident | 40 | 0.9 | Epic | Sunken Temple |
| `Weapon_BoneStaff_Data` | Bone Staff | 30 | 1.1 | Rare | BirdSkeleton boss |
| `Weapon_MushroomHammer_Data` | Mushroom Hammer | 45 | 0.7 | Rare | MyceliumKing drop |
| `Weapon_KrakenBlade_Data` | Kraken Blade | 55 | 0.85 | Legendary | KrakenChest drop |
| `Weapon_SoulCompass_Data` | Soul Compass | 60 | 1.0 | Legendary | Act 3 — Toran freed |

---

## 4. LootTable Assets

> Path: `Assets/ScriptableObjects/LootTables/`

### Tutorial_LootTable
| Item | Drop Chance | Min Qty | Max Qty |
|---|---|---|---|
| HealthPotion | 40% | 1 | 2 |
| GoldCoin | 80% | 5 | 15 |
| BoatPlank | 20% | 1 | 3 |

### EmberIsle_LootTable
| Item | Drop Chance | Min Qty | Max Qty |
|---|---|---|---|
| EmberCrystal | 55% | 1 | 3 |
| HealthPotion | 30% | 1 | 2 |
| GoldCoin | 90% | 20 | 50 |
| RepairKit | 15% | 1 | 1 |
| RareCrystal | 5% | 1 | 1 |

### FrostIsle_LootTable
| Item | Drop Chance | Min Qty | Max Qty |
|---|---|---|---|
| FrostCrystal | 55% | 1 | 3 |
| HealthPotion | 30% | 1 | 2 |
| GoldCoin | 90% | 20 | 50 |
| LargeRepairKit | 10% | 1 | 1 |
| RareCrystal | 5% | 1 | 1 |

### MysteryIsle_LootTable
| Item | Drop Chance | Min Qty | Max Qty |
|---|---|---|---|
| MystCrystal | 55% | 1 | 3 |
| SoulEssence | 40% | 1 | 4 |
| GoldCoin | 90% | 25 | 60 |
| AncientMap | 8% | 1 | 1 |
| RareCrystal | 5% | 1 | 1 |

### SunkenTemple_LootTable
| Item | Drop Chance | Min Qty | Max Qty |
|---|---|---|---|
| SoulEssence | 50% | 2 | 5 |
| MystCrystal | 30% | 1 | 2 |
| GoldCoin | 90% | 30 | 70 |
| CompassShard | 15% | 1 | 1 |
| RareCrystal | 8% | 1 | 1 |

### Ocean_LootTable
| Item | Drop Chance | Min Qty | Max Qty |
|---|---|---|---|
| GoldCoin | 95% | 15 | 40 |
| BoatPlank | 35% | 1 | 3 |
| Rope | 25% | 1 | 2 |
| IronNail | 30% | 2 | 5 |
| HealthPotion | 20% | 1 | 1 |

---

## 5. Player Stats (set on PlayerStats.cs component in Inspector)

| Stat | Starting Value | Max Value | Notes |
|---|---|---|---|
| MaxHealth | 100 | 300 | increases +20 per level |
| MaxStamina | 100 | 200 | used for sprinting and dodge |
| MoveSpeed | 5.0 | 8.0 | base walking speed (m/s) |
| SprintMultiplier | 1.6 | — | sprint = MoveSpeed × 1.6 |
| AttackDamage | 25 | 120 | weapon damage added on top |
| Defense | 5 | 60 | reduces incoming damage |
| DodgeInvincibility | 0.35 s | — | i-frames on dodge |
| StaminaRegen | 15 /s | — | stamina recovery rate |
| HealthRegen | 0 /s | 5 /s | default 0; increases with upgrades |

---

## 6. Boat Stats (set on BoatStats.cs in Inspector)

| Stat | Value | Notes |
|---|---|---|
| MaxDurability | 150 | damaged by enemies, reefs |
| BaseSpeed | 8.0 m/s | ocean travel speed |
| BoostSpeed | 14.0 m/s | boost duration 3 s, cooldown 8 s |
| TurnRate | 45 °/s | steering rotation speed |
| HarpoonDamage | 40 | harpoon projectile damage |
| HarpoonRange | 25.0 m | max harpoon reach |
| HarpoonCooldown | 2.5 s | fire rate |
| LanternRadius | 15.0 m | light range in fog/night |

---

## 7. Ability Stats (set on PlayerAbilityHandler.cs in Inspector)

| Ability | Damage | Cooldown | Duration | Mana Cost | Unlock |
|---|---|---|---|---|---|
| CompassBeam | 60 | 8.0 s | instant | 20 | Tutorial end |
| SoulShield | 0 | 12.0 s | 4.0 s | 30 | EmberIsle cleared |
| PhaseStep | 0 | 6.0 s | instant | 15 | FrostIsle cleared |
| SoulChainBreak | 80 AoE | 20.0 s | instant | 50 | MysteryIsle cleared |

---

## 8. Level Progression Table

| Level | XP Required (total) | Reward |
|---|---|---|
| 1 | 0 | Start |
| 2 | 100 | +20 MaxHealth |
| 3 | 250 | +1 Ability slot |
| 4 | 500 | +5 AttackDamage |
| 5 | 850 | +20 MaxHealth, +5 Defense |
| 6 | 1300 | CompassBeam upgrade (damage +20) |
| 7 | 1900 | +10 AttackDamage |
| 8 | 2600 | +20 MaxHealth, Harpoon upgrade |
| 9 | 3500 | +5 Defense, StaminaRegen +5 |
| 10 | 4500 | SoulShield upgrade (duration +2 s) |
| 11 | 5800 | +15 AttackDamage |
| 12 | 7200 | +20 MaxHealth |
| 13 | 8800 | PhaseStep upgrade (2 charges) |
| 14 | 10600 | +10 AttackDamage, +5 Defense |
| 15 | 12800 | SoulChainBreak (final ability) |
| 16 | 15000 | +30 MaxHealth — max character power |

---

*Document version 1.0 — IsleTrial Project*
