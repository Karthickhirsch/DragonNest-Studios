# Model Spec — Player Character: Kael
## Isle of Trials — Player_and_Boat/

---

## Model Overview

| Field | Value |
|-------|-------|
| **Model Name** | Kael |
| **Role** | Main playable character |
| **Style** | Low poly stylized 3D |
| **Height in Game** | ~1.8 Unity units (1.8 meters) |
| **Target Polygons** | 4,000 – 8,000 triangles |
| **Texture Size** | 2048 x 2048 |
| **Rig Type** | Humanoid |
| **Animations Needed** | Yes (see animation list below) |
| **Unity Scale** | Set Scale Factor to 1.0 after import |

---

## Visual Description

**Body:**
- Young male sailor, slim but athletic build
- Age: early 20s
- Height: medium

**Outfit:**
- Worn navy blue coat with rolled-up sleeves
- Light tan pants tucked into brown leather boots
- A leather belt with a small pouch
- Fingerless sailing gloves
- A compass hanging from the belt

**Head:**
- Short messy brown hair, slightly windswept
- Determined, adventurous expression
- No beard — young face

**Weapon:**
- Short sailor's cutlass sheathed at the hip (separate model or integrated)

**Colors:**
- Primary: Navy blue, tan, brown
- Accent: Brass buckles and compass details
- Skin: Medium tone

---

## Pose for Export
- **T-pose** (arms straight out horizontally)
- Standing, centered on origin (feet at Y=0)
- Facing +Z direction (forward)

---

## Texture Maps Needed
- **Albedo/Color map** (main colors)
- **Normal map** (surface detail)
- **Emission map** (compass glows faintly — optional)

---

## Animations Required

| Animation Name | Type | Description |
|---------------|------|-------------|
| Idle | Loop | Gentle breathing, slight sway |
| Walk | Loop | Standard walk cycle |
| Run | Loop | Running forward |
| Attack | One-shot | Sword slash left-to-right |
| ChargedAttack | One-shot | Big overhead swing |
| Dodge | One-shot | Roll to the side |
| Interact | One-shot | Reach forward with hand |
| Dead | One-shot | Collapse to ground |
| FireDash | One-shot | Lunging forward dash |
| VineGrapple | One-shot | Arm extends forward with rope |
| HoldingLantern | Loop | Walking with lantern held up |

**Free Animation Source:**
- Mixamo (https://www.mixamo.com) — free animations for humanoid rigs
- Steps: Upload your model → Auto-rig → Download any animation pack

---

## AI Generation Prompt

Paste this into **Meshy.ai → Text to 3D**:

```
Low poly stylized 3D game character, young male sailor adventurer named Kael,
slim athletic build, early 20s, short messy brown windswept hair, determined expression,
wearing a worn navy blue sailor coat with rolled-up sleeves, tan pants tucked into
brown leather boots, leather belt with a small pouch and brass compass hanging from it,
fingerless sailing gloves, short cutlass sheathed at hip,
low poly stylized art style similar to Legend of Zelda Wind Waker,
clean geometry, vibrant colors, T-pose with arms outstretched horizontally,
centered on white background, game-ready mesh, front-facing, full body visible,
4000-8000 triangles, 2048x2048 texture
```

---

## Blender Creation Guide (If Making Manually)

### Step 1 — Basic Body Shape
1. Open Blender → Delete default cube
2. Add → Mesh → UV Sphere → Scale to roughly 1.8 tall
3. Use Loop Cut (Ctrl+R) to add waist, shoulders, hips
4. Select top portion → extrude head
5. Select arm regions → extrude arms
6. Select leg region → extrude legs
7. Keep polygon count low — no need for realistic detail

### Step 2 — Clothing
1. Select body faces in coat region → Separate (P)
2. Add slight offset (Solidify modifier) for coat thickness
3. Repeat for boots, belt

### Step 3 — Rig (Skeleton)
1. Add → Armature → Single Bone
2. In Edit Mode → extrude bones for spine, head, arms, legs
3. Match Unity Humanoid layout:
   - Hips → Spine → Chest → Neck → Head
   - UpperArm.L/R → LowerArm.L/R → Hand.L/R
   - UpperLeg.L/R → LowerLeg.L/R → Foot.L/R
4. Parent mesh to armature: Select mesh → Shift+Select armature → Ctrl+P → With Automatic Weights

### Step 4 — Export
1. File → Export → FBX
2. Settings: Apply Transform ✓, Scale = 0.01, Armature ✓, Mesh ✓
3. Name: `Kael_Character.fbx`

---

## Upgrade Versions (Cosmetic Unlocks)
Later you can create variant textures for:
- Kael_Outfit_Default.png
- Kael_Outfit_FireArmor.png (after Ember Isle)
- Kael_Outfit_IceArmor.png (after Frostveil)
- Kael_Outfit_StormArmor.png (final island)

These are just texture swaps on the same model — very easy to add.

---

## Unity Import Checklist
- [ ] FBX imported into `Assets/_Game/Art/Models/Player/`
- [ ] Rig set to Humanoid
- [ ] Avatar configured (all green bones in Humanoid mapping)
- [ ] Animator Controller created and assigned
- [ ] Scale Factor = 1.0
- [ ] Model faces +Z direction in scene
