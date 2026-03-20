# IsleTrial — Animation Design Document
**Every character · every animation clip · Unity Animator setup**

---

## How to Use This Document

For each character:
1. Open the character's `.blend` file in Blender.
2. Create each animation clip listed below using NLA (Non-Linear Animation) strips.
3. Export FBX with `Baked Animation` enabled.
4. In Unity → Inspector → Animation tab → confirm each clip appears.
5. Build the Animator Controller using the states and transitions listed.

---

## 1. Kael (Player Character)
**Rig:** `03_Kael_Rig.py` | Rig type: Humanoid | Height: 1.80 m

### Animation Clips

| Clip Name | Frames | Loop | Description |
|---|---|---|---|
| `Idle` | 0–120 | Yes | Subtle breathing, weight shift every 2 s |
| `Idle_Boat` | 0–80 | Yes | Standing on boat — lean with ocean sway |
| `Walk` | 0–60 | Yes | Normal walk cycle |
| `Run` | 0–40 | Yes | Sprint run cycle |
| `Dodge_Forward` | 0–25 | No | Quick forward roll |
| `Dodge_Back` | 0–25 | No | Step back + guard |
| `Dodge_Left` | 0–20 | No | Side step left |
| `Dodge_Right` | 0–20 | No | Side step right |
| `Sword_Slash_1` | 0–20 | No | Left-to-right horizontal slash |
| `Sword_Slash_2` | 0–22 | No | Right-to-left return slash |
| `Sword_Slash_3` | 0–18 | No | Overhead downward chop |
| `Sword_Thrust` | 0–16 | No | Forward stab (combo finisher) |
| `Ability_CompassBeam` | 0–50 | No | Raise compass, fire beam from hand |
| `Ability_Shield` | 0–30 | No | Compass glow shield summon |
| `Ability_Dash` | 0–15 | No | Forward burst dash |
| `Interact` | 0–35 | No | Reach forward with hand, press |
| `PickUp_Floor` | 0–40 | No | Crouch and pick up item |
| `Open_Chest` | 0–60 | No | Kneel, open chest lid |
| `Jump` | 0–20 | No | Jump takeoff |
| `Fall` | 0–30 | Yes | Falling loop |
| `Land` | 0–15 | No | Landing impact |
| `Swim_Idle` | 0–90 | Yes | Treading water |
| `Swim_Forward` | 0–50 | Yes | Swimming stroke |
| `Take_Damage` | 0–20 | No | Stagger back from hit |
| `Death` | 0–80 | No | Collapse forward, stay down |
| `Victory` | 0–90 | No | Raise sword, look at compass |
| `Steer_Left` | 0–30 | Yes | Hands on wheel, turning left |
| `Steer_Right` | 0–30 | Yes | Hands on wheel, turning right |

### Unity Animator Controller
```
States:       Idle → Walk → Run (by Speed float 0→1→2)
              Idle → Idle_Boat (by bool IsOnBoat)
              Any → Dodge_* (by trigger Dodge + direction int)
              Any → Sword_Slash_1 → Slash_2 → Slash_3 (combo timer)
              Any → Take_Damage (by trigger Hit)
              Any → Death (by bool IsDead)
              Idle → Interact (by trigger Interact)
              Idle → Ability_* (by trigger UseAbility + abilityIndex int)

Parameters:   Speed (float), IsOnBoat (bool), IsDead (bool),
              Dodge (trigger), Hit (trigger), Interact (trigger),
              UseAbility (trigger), AbilityIndex (int),
              IsSwimming (bool)
```

---

## 2. Toran (NPC / Boss Phase 3)
**Rig:** `46_NPC_Toran_SoulGuardian_Rig.py` | Rig type: Humanoid | Height: 1.82 m

| Clip Name | Frames | Loop | Description |
|---|---|---|---|
| `Idle_Bound` | 0–180 | Yes | Soul chains glowing, slight float, laboured breathing |
| `Float` | 0–120 | Yes | Gentle hover in spectral form |
| `Speak` | 0–90 | No | Head turns to Kael, arms gesture weakly |
| `Desperation` | 0–60 | No | Strains against chains — Possessed shape key activates |
| `ChainBreak_1` | 0–45 | No | Left chest chain shatters — reactive stumble |
| `ChainBreak_2` | 0–45 | No | Right chest chain shatters |
| `ChainBreak_3` | 0–45 | No | Left arm chain shatters |
| `ChainBreak_4` | 0–45 | No | Right arm chain shatters |
| `ChainBreak_5` | 0–45 | No | Left leg chain shatters |
| `ChainBreak_6` | 0–45 | No | Right leg chain shatters — full stumble |
| `Liberation` | 0–120 | No | All chains gone — stands tall, arms open, glow fades |
| `Fade_Out` | 0–200 | No | Slowly dissolves upward (GhostAura scale → 0) |
| `Take_Damage` | 0–20 | No | Chain pulls tighter, flinch |
| `Death` | 0–150 | No | Peaceful fade — Freed shape key, then dissolve |

### Unity Animator
```
States:       Idle_Bound (default)
              Desperation (triggered by 'ChainCount' int drops)
              ChainBreak_1..6 (triggered by 'BreakChain' int 1-6)
              Liberation (triggered when ChainCount == 0)
              Fade_Out (trigger 'FadeOut')

Parameters:   ChainCount (int 0-6), BreakChain (int), FadeOut (trigger)
```

---

## 3. EmberLizard (Enemy)
**Rig:** `40_Enemy_EmberLizard_Rig.py` | Rig type: Generic

| Clip Name | Frames | Loop | Description |
|---|---|---|---|
| `Idle` | 0–120 | Yes | Breathing, occasional tail flick, eye blink |
| `Walk` | 0–50 | Yes | Four-legged prowl — body sways laterally |
| `Run` | 0–30 | Yes | Fast quadruped sprint |
| `Attack_Bite` | 0–30 | No | Lunge head forward, jaw snaps shut |
| `Attack_Swipe` | 0–25 | No | Front claw rakes horizontally |
| `SpineFlare` | 0–40 | No | Dorsal spines fan out, body arches — threat display |
| `TailWhip` | 0–35 | No | Tail swings 180° — wide area attack |
| `Roar` | 0–60 | No | Head lifts, jaw opens, spine flare combo |
| `TakeDamage` | 0–18 | No | Body flinch, spine recoil |
| `Death` | 0–80 | No | Stumble, collapse on side, lava cracks dim |

### Unity Animator
```
States:       Idle (default) → Walk → Run (by Speed)
              Any → Attack_Bite (trigger Attack, range check)
              Any → Attack_Swipe (trigger Swipe)
              Any → TailWhip (trigger TailWhip)
              Idle → Roar (trigger Roar, on aggro)
              Idle → SpineFlare (trigger Flare, on low health)
              Any → TakeDamage (trigger Hit)
              Any → Death (bool IsDead)

Parameters:   Speed (float), Attack (trigger), Swipe (trigger),
              TailWhip (trigger), Roar (trigger), Flare (trigger),
              Hit (trigger), IsDead (bool)
```

---

## 4. FrostSlug (Enemy)
**Rig:** `41_Enemy_FrostSlug_Rig.py` | Rig type: Generic

| Clip Name | Frames | Loop | Description |
|---|---|---|---|
| `Idle` | 0–150 | Yes | Body pulses slightly, eyestalks swivel independently |
| `SlideForward` | 0–60 | Yes | Whole body undulates as slug glides forward |
| `TurnLeft` | 0–30 | No | Head + front spine arc left |
| `TurnRight` | 0–30 | No | Head + front spine arc right |
| `Attack_Spit` | 0–45 | No | Head rears back, mouth opens, ice glob fires |
| `Attack_BodySlam` | 0–50 | No | Rears up on tail, slams body forward |
| `ShellRecoil` | 0–20 | No | Shell plates shudder and tighten on hit |
| `SlowEffect` | 0–80 | Yes | Slower undulation — plays when player is slowed |
| `TakeDamage` | 0–20 | No | Full body recoil, eyestalks retract |
| `Death` | 0–100 | No | Body deflates, shell cracks, frost patch spawns |

### Unity Animator
```
States:       Idle (default) → SlideForward (by Speed > 0)
              SlideForward → TurnLeft/Right (by TurnDir int)
              Any → Attack_Spit (trigger Spit)
              Any → Attack_BodySlam (trigger BodySlam)
              Any → ShellRecoil (trigger Hit, if shell intact)
              Any → TakeDamage (trigger Hit, if shell broken)
              Any → Death (bool IsDead)

Parameters:   Speed (float), TurnDir (int -1/0/1),
              Spit (trigger), BodySlam (trigger),
              Hit (trigger), IsDead (bool), ShellIntact (bool)
```

---

## 5. Ignar the Molten Drake (Boss)
**Rig:** `42_Boss_Ignar_MoltenDrake_Rig.py` | Rig type: Generic

| Clip Name | Phase | Frames | Loop | Description |
|---|---|---|---|---|
| `Idle_Ground` | 1-3 | 0–180 | Yes | Heavy breathing, tail sways, wings fold |
| `Walk` | 1-3 | 0–60 | Yes | Slow heavy quadruped walk |
| `Roar` | 1-3 | 0–80 | No | Head rears back, wings spread, fire burst |
| `WingFlap_Idle` | 2-3 | 0–120 | Yes | Hovering in place — wings beat |
| `TakeOff` | 2-3 | 0–50 | No | Back legs push off, wings spread and launch |
| `Fly_Forward` | 2-3 | 0–60 | Yes | Full flight — wings stroke, body pitches |
| `Land` | 2-3 | 0–50 | No | Approach + impact landing — ground shake |
| `Attack_Bite` | 1-3 | 0–35 | No | Neck lunges forward, jaw snaps |
| `Attack_Claw_L` | 1-3 | 0–28 | No | Left front claw slam |
| `Attack_Claw_R` | 1-3 | 0–28 | No | Right front claw slam |
| `Attack_TailSlam` | 1-3 | 0–40 | No | Tail swings wide 180° |
| `Attack_FireBreath` | 1-3 | 0–30 | No | Head tilts, mouth opens — fire breath starts |
| `FireBreath_Loop` | 1-3 | 0–40 | Yes | Sustained fire breath — head sweeps |
| `FireBreath_End` | 1-3 | 0–20 | No | Mouth closes, smoke puff |
| `Wing_Shield` | 2-3 | 0–35 | No | Wings fold around body — damage reduction |
| `LavaSlam` | 3 | 0–70 | No | Rises on back legs, slams both front claws — Phase 3 rage |
| `TakeDamage` | 1-3 | 0–22 | No | Body recoil, wing snap |
| `PhaseTransition_2` | — | 0–100 | No | Body cracks open, lava erupts, flight starts |
| `PhaseTransition_3` | — | 0–100 | No | Lands with earthquake, dorsal plates full flare |
| `Death` | — | 0–180 | No | Stumbles, wings collapse, slow fall, lava extinguishes |

### Unity Animator
```
Layers:       Base (locomotion + attacks)
              Additive: WingFlap (blended during flight)

States:       Idle_Ground → Walk (Speed)
              Idle_Ground → TakeOff (trigger Fly, Phase >= 2)
              WingFlap_Idle → Fly_Forward (Speed > 0, IsFlying)
              WingFlap_Idle → Land (trigger Land)
              Any → Attack_* (triggers, distance-gated)
              Any → FireBreath_Start → FireBreath_Loop → FireBreath_End
              Any → TakeDamage (trigger Hit)
              Any → PhaseTransition_2/3 (trigger PhaseChange + PhaseIndex)
              Any → Death (bool IsDead)

Parameters:   Speed (float), IsFlying (bool), PhaseIndex (int 1-3),
              PhaseChange (trigger), Fly (trigger), Land (trigger),
              Attack (trigger), AttackType (int), Hit (trigger),
              IsDead (bool), FireBreath (bool)
```

---

## 6. Glaciara the Frost Warden (Boss)
**Rig:** `43_Boss_Glaciara_FrostWarden_Rig.py` | Rig type: Generic

| Clip Name | Phase | Frames | Loop | Description |
|---|---|---|---|---|
| `Idle` | 1-3 | 0–150 | Yes | Arms slightly raised, frost breath visible, crown glows |
| `Walk` | 1-3 | 0–70 | Yes | Heavy stomping walk — ground cracks |
| `Roar_Phase1` | 1 | 0–80 | No | Arms spread wide, frost breath blast |
| `Roar_Phase2` | 2 | 0–90 | No | Crown spires extend, ice shard volley fires |
| `Roar_Phase3` | 3 | 0–100 | No | Full blizzard erupts from body, crown max size |
| `Attack_FistSlam_L` | 1-3 | 0–40 | No | Left fist raises high, slams ground |
| `Attack_FistSlam_R` | 1-3 | 0–40 | No | Right fist raises high, slams ground |
| `Attack_DoubleSlam` | 2-3 | 0–60 | No | Both fists slam simultaneously — shockwave |
| `Attack_IceShard` | 1-3 | 0–35 | No | Left arm extends, shard launches from IceShard_Ctrl |
| `Attack_IceWall` | 2-3 | 0–45 | No | Both arms cross, slam outward — wall rises |
| `Attack_Blizzard` | 3 | 0–60 | No | Arms raise overhead — sustained blizzard AOE |
| `CrownFlare` | 2-3 | 0–50 | No | Crown spires pulse outward, each fires ice bolt |
| `TakeDamage` | 1-3 | 0–22 | No | Body shudders, cracks appear |
| `PhaseTransition_2` | — | 0–90 | No | Kneels, ice explosion, stands with crown expanded |
| `PhaseTransition_3` | — | 0–100 | No | Body cracks, inner blue fire erupts, full power |
| `Frozen` | — | 0–30 | No | Entire body freezes solid (player ability effect) |
| `Death` | — | 0–200 | No | Kneels slowly, cracks spread, shatters into ice fragments |

### Unity Animator
```
States:       Idle (default) → Walk (Speed)
              Any → Attack_FistSlam_L/R (trigger Slam, SlamSide)
              Any → Attack_IceShard (trigger IceShard)
              Any → Attack_IceWall (trigger IceWall, Phase >= 2)
              Any → Attack_Blizzard (trigger Blizzard, Phase == 3)
              Any → CrownFlare (trigger CrownFlare, Phase >= 2)
              Idle → Roar_Phase* (trigger Roar, by PhaseIndex)
              Any → TakeDamage (trigger Hit)
              Any → Frozen (trigger Frozen)
              Frozen → Idle (trigger Unfreeze, timed)
              Any → PhaseTransition_2/3 (trigger PhaseChange)
              Any → Death (bool IsDead)

Parameters:   Speed (float), PhaseIndex (int 1-3), PhaseChange (trigger),
              Slam (trigger), SlamSide (int 0/1), IceShard (trigger),
              IceWall (trigger), Blizzard (trigger), CrownFlare (trigger),
              Roar (trigger), Hit (trigger), Frozen (trigger),
              Unfreeze (trigger), IsDead (bool)
```

---

## 7. Other NPCs

### MushroomNPC (`04_MushroomNPC_Rig.py`)
| Clip | Loop | Description |
|---|---|---|
| `Idle` | Yes | Gentle sway, cap bobs |
| `Talk` | Yes | Body bobs while speaking |
| `Wave` | No | One arm waves — shop greeting |
| `Startled` | No | Jumps back, cap lifts |

### CompassNPC (`05_CompassNPC_Rig.py`)
| Clip | Loop | Description |
|---|---|---|
| `Idle` | Yes | Floating, compass needle rotates slowly |
| `Point` | No | Extends arm, points in direction |
| `Spin` | No | Full 360 spin — hint animation |

### BirdSkeleton (`06_BirdSkeleton_Rig.py`)
| Clip | Loop | Description |
|---|---|---|
| `Idle_Perch` | Yes | Perched — head tilts side to side |
| `FlyIdle` | Yes | Flapping in place |
| `FlyForward` | Yes | Full flight cycle |
| `Attack_Dive` | No | Dive bomb downward |
| `Death` | No | Fall apart |

### MimicChest (`07_MimicChest_Rig.py`)
| Clip | Loop | Description |
|---|---|---|
| `Idle_Closed` | Yes | Locked still — looks like normal chest |
| `Open_Transform` | No | Lid lifts, legs unfold, jump scare |
| `Walk` | Yes | Chest walks on lid-legs |
| `Attack_Bite` | No | Lid snaps shut |
| `Death` | No | Collapses back into chest shape |

---

## 8. Sea Creatures

### LargeFish / Shark (`15_LargeFish_Rig.py`, `17_Shark_Rig.py`)
| Clip | Loop | Description |
|---|---|---|
| `Swim_Idle` | Yes | Gentle tail fin oscillation |
| `Swim_Fast` | Yes | Faster full-body S-curve |
| `Attack` | No | Lunge forward, mouth opens |
| `Death` | No | Slow drift down, fin stops |

### Whale (`16_Whale_Rig.py`)
| Clip | Loop | Description |
|---|---|---|
| `Swim` | Yes | Full body whale undulation |
| `Breach` | No | Jumps out of water arc |
| `Dive` | No | Tail lifts as it goes under |

---

## 9. Export Workflow Per Character

```
1. Open the character's .blend file in Blender
2. Open NLA Editor (Ctrl+Space or strip panel)
3. For each clip:
   a. Set start frame and end frame
   b. Press I to insert keyframe at key poses
   c. Create NLA strip: Action Editor → Push Down
   d. Name the strip exactly as listed in this doc
4. Select Armature + all mesh objects
5. File → Export → FBX
   ☑ Selected Objects
   ☑ Apply Transform
   ☑ Armature
   ☑ Mesh
   ☑ Baked Animation
   ☐ Leaf Bones (OFF)
   Scale: 1.0  Axis: Y Up  -Z Forward
6. Import into Unity
   → Animation tab → verify all clip names appear
   → Set loop on clips marked Yes above
   → Build Animator Controller per section above
```

---

## 10. Mixamo Shortcut (Recommended for Humanoid Characters)

For **Kael** and **Toran** (Humanoid rig), you can skip hand-keying basic
locomotion clips by using Mixamo:

```
1. Export character as FBX (no animation) from Blender
2. Upload to mixamo.com → Auto-Rig
3. Download animation packs: Locomotion, Combat, Reactions
4. Import all FBX files into Unity
5. Set each to Humanoid rig
6. Drag clips into the Animator Controller
7. Custom clips (CompassBeam, ChainBreak, Liberation etc.) 
   must still be hand-keyed in Blender or Unity's Animation window
```

---

*Document version 1.0 — IsleTrial Project*
