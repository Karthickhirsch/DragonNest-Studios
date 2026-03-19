# Prompt 04 — Sea Creatures (Harpoon Targets & Ocean Life)

## Game Context
- Game: IsleTrial — 3D Ocean Adventure
- Boat has a harpoon — these are the TARGET creatures
- Creatures need proper bone rigging for animation in Unity
- Style: Realistic but slightly stylized — detailed, not horror
- Poly budget: Medium-high (3000–15000 tris per creature)
- All need: mesh + armature + basic shape keys for idle breathing

---

## Prompt 04-A — Large Fish (Primary Harpoon Target)

```
Write a complete Blender Python (bpy) script to create a high-quality large game fish 
model with armature for a Unity ocean adventure game called IsleTrial.

Fish type: Large deep-sea fish (inspired by tuna/marlin hybrid), 2.5m long

GEOMETRY:

1. "Fish_Body"
   - Start with a UV Sphere (32 segments, 16 rings)
   - Scale to elongated fish body: 2.5m x 0.6m x 0.5m
   - Shape refinement using proportional editing simulation:
     * Narrow the tail section (rear 40%): taper to 0.1m
     * Widen the shoulder/chest area: middle 30% is widest
     * Flatten belly slightly (scale Y at bottom vertices)
   - Apply Subdivision Surface level 2 for smooth surface
   - Add Multiresolution modifier for fine scale detail

2. "Fish_DorsalFin"
   - Triangular fin: 0.4m tall, 0.6m long base
   - Thin (0.02m thickness) with slightly curved profile
   - Spines visible: 6 thin cylindrical spines inside fin
   - Solidify modifier (0.015m thickness)
   - Positioned on top center of body

3. "Fish_PectoralFins" (2 objects: Left + Right)
   - "Fish_PectoralFin_L" and "Fish_PectoralFin_R"
   - Swept-back wing-like fins: 0.35m long, 0.2m wide
   - Mirror on X axis
   - Angled downward 20 degrees

4. "Fish_TailFin"
   - Forked crescent tail (lunate shape)
   - Two lobes: each 0.4m long, 0.15m wide at tip
   - Sickle shape using bezier curve extruded

5. "Fish_Eye_L" / "Fish_Eye_R"
   - Sphere: 0.04m radius
   - Inner iris sphere: 0.03m radius (darker)
   - Pupil: small dark disc
   - Positioned on sides of head

6. "Fish_Mouth"
   - Cut into head using boolean
   - Slightly open showing teeth
   - 8 small cone teeth (0.01m)

MATERIALS:
- "Mat_Fish_Body_Top"    : Base #1A3A5A (deep blue-grey), roughness 0.4, metallic 0.1
                           Iridescent sheen: add Color Ramp on Fresnel → mix with base
- "Mat_Fish_Body_Belly"  : Base #E8E0D0 (light silver), roughness 0.3
- "Mat_Fish_Fin"         : Base #1A3A5A, alpha 0.7 (slight translucency), roughness 0.5
- "Mat_Fish_Eye"         : Base #0A0A0A, roughness 0.05, specular 1.0 (wet eye)
- "Mat_Fish_Iris"        : Base #3A6A8A, roughness 0.02

ARMATURE — Create bone rig:
Armature object: "Fish_Armature"

Bones (create in edit mode):
- "Bone_Root"       : Base bone at fish center (0,0,0)
- "Bone_Body_01"    : Tail section (rear 30% of body)
- "Bone_Body_02"    : Mid body
- "Bone_Body_03"    : Chest/shoulder
- "Bone_Head"       : Head bone
- "Bone_Jaw"        : Lower jaw (child of Bone_Head)
- "Bone_Tail_01"    : First tail segment
- "Bone_Tail_02"    : Tail fork (child of Bone_Tail_01)
- "Bone_DorsalFin"  : Dorsal fin root
- "Bone_PectoralFin_L" / "_R" : Pectoral fin roots

Skinning:
- Parent Fish_Body to armature with Automatic Weights
- Parent each fin to armature, assign vertex groups manually to fin bones

SHAPE KEYS on Fish_Body:
- "Basis"        : Default shape
- "Swim_Left"    : Body bent 20 degrees left (tail curves left)
- "Swim_Right"   : Body bent 20 degrees right
- "Mouth_Open"   : Jaw open 30 degrees
- "Idle_Breathe" : Slight gill puff (scale gill area vertices 1.05)

ORGANIZATION:
- Collection: "IsleTrial_Fish"
- Parent mesh and armature to empty: "Fish_ROOT"
- Apply mesh transforms but NOT armature
- Print polycount and bone count
```

---

## Prompt 04-B — Whale (Large Epic Encounter)

```
Write a Blender Python script to create a high-quality humpback whale model 
for IsleTrial — this is a large, dramatic ocean encounter creature.

Whale size: 14m long, 4m wide, 3m tall at hump

GEOMETRY:

1. "Whale_Body"
   - Start with a Capsule or elongated sphere
   - Final dimensions: 14m x 4m x 3m
   - Head shape: broad, squared-off snout (not dolphin-round)
   - Jaw line: lower jaw extends slightly beyond upper (baleen whale shape)
   - Throat pleats: 12 parallel grooves running from chin to belly (use Multiresolution + sculpt-like displacement)
   - Dorsal hump: raised section at 2/3 body length, small dorsal knob (not tall fin)
   - Peduncle (tail stock): narrow, keeled section before tail
   - Tubercles: bumpy nodules on head edge and pectoral fins (small sphere booleans or displacement)

2. "Whale_Flippers" (Left + Right, 3m long each)
   - "Whale_Flipper_L" / "Whale_Flipper_R"
   - Long swept pectoral fins, 3m long x 0.8m wide
   - Bumpy leading edge (tubercles)
   - Thin at tip (0.05m), thicker at root (0.25m)

3. "Whale_Flukes"
   - Tail fin: 4m wide tip-to-tip, butterfly shape
   - Deep notch at center
   - Natural curve: tips point slightly downward
   - Thin edges (solidify 0.05m)

4. "Whale_Eye_L" / "Whale_Eye_R"
   - Small eye (0.08m) on side of head, behind and below corner of mouth
   - Surrounded by wrinkled skin displacement

5. "Whale_Mouth_Line"
   - Curved mouth line cut: arched from tip of snout, curving down to throat
   - Slight opening showing baleen plates inside (thin rectangular sheets, dark)

MATERIALS:
- "Mat_Whale_Dark"     : Base #1A1F2A (very dark blue-grey), roughness 0.6
- "Mat_Whale_Belly"    : Base #D0D0C8 (mottled light grey-white), roughness 0.65
- "Mat_Whale_Barnacle" : Base #8A8070, roughness 0.95 (scattered on skin - vertex paint)
- "Mat_Whale_Eye"      : Base #050808, roughness 0.05, specular 1.0
- "Mat_Baleen"         : Base #2A2010, roughness 0.85 (inside mouth plates)

Vertex Painting:
- Paint belly/white pattern on underside using vertex colors
- Paint barnacle clusters near head and flipper roots

ARMATURE — "Whale_Armature":
Bones:
- "Bone_Root"
- "Bone_Body_01" through "Bone_Body_05" (spine chain, tail to head)
- "Bone_Head"
- "Bone_Jaw_Lower"
- "Bone_Fluke_L" / "Bone_Fluke_R"
- "Bone_Flipper_L" / "Bone_Flipper_R"

SHAPE KEYS:
- "Basis"
- "Breach_Arch"  : Body arched upward for breaching animation
- "Dive_Curve"   : Body curved downward for diving
- "Tail_Up"      : Tail flukes raised (fluke display before dive)
- "Mouth_Open"   : Jaw dropped for feeding lunge

ORGANIZATION:
- Collection: "IsleTrial_Whale"
- Empty parent: "Whale_ROOT"
- Print total polycount, bone count
- Print: "Whale is designed for Unity Animator: use Shape Keys as BlendShapes"
```

---

## Prompt 04-C — Shark (Aggressive Encounter)

```
Write a Blender Python script to create a high-quality shark model for IsleTrial.
Shark type: Great White, 5m long, aggressive encounter creature.

GEOMETRY:

1. "Shark_Body"
   - Torpedo shape: 5m x 1.0m x 0.8m
   - Conical snout, slightly flattened underside
   - Powerful mid-body, tapers to caudal peduncle
   - Lateral line groove: subtle groove along each side (edge crease)

2. "Shark_DorsalFin_Main"   — Tall triangular fin: 0.7m tall, 0.5m base
3. "Shark_DorsalFin_Second" — Smaller second dorsal: 0.2m tall, near tail
4. "Shark_PectoralFins"     — Long swept pectorals: 0.8m x 0.35m (L+R)
5. "Shark_PelvicFins"       — Small paired fins beneath: 0.25m
6. "Shark_AnalFin"          — Small fin opposite second dorsal
7. "Shark_CaudalFin"        — Crescent tail: upper lobe 0.6m, lower lobe 0.45m
8. "Shark_Gills"            — 5 gill slit cutouts on each side (boolean cuts)
9. "Shark_Eye_L/R"          — Black sclera, 0.035m, rolled-back whites shape key
10. "Shark_Teeth_Upper/Lower" — 3 rows of triangular teeth in jaw

MATERIALS:
- "Mat_Shark_Back"    : Base #4A5055 (blue-grey), roughness 0.45, slight iridescence
- "Mat_Shark_Belly"   : Base #E8E5E0 (off white), roughness 0.4
- "Mat_Shark_Eye"     : Base #020202, roughness 0.02
- "Mat_Shark_Teeth"   : Base #F5F0E8, roughness 0.35, slight translucency
- "Mat_Shark_Mouth"   : Base #CC3322 (inside mouth pink-red), roughness 0.6

ARMATURE — "Shark_Armature":
- "Bone_Root", "Bone_Body_01" through "Bone_Body_04"
- "Bone_Head", "Bone_Jaw"
- "Bone_DorsalFin", "Bone_Tail"
- "Bone_Pectoral_L" / "_R"

SHAPE KEYS:
- "Basis"
- "Attack_Open"  : Jaw wide open, snout raised (attack pose)
- "Swim_Curve_L/R": Aggressive S-curve swim
- "Gill_Flare"   : Gill slits slightly open

Collection: "IsleTrial_Shark"
Parent: "Shark_ROOT"
```

---

## Prompt 04-D — Small Fish School (Ambient Wildlife)

```
Write a Blender Python script to create a small tropical fish model for IsleTrial
that will be used in particle systems / schools of fish.

Keep it optimized: target 400-800 triangles (this is spawned in hundreds).

Fish type: Tropical reef fish (inspired by angelfish shape), 0.3m long

1. "SmallFish_Body"    : Laterally compressed oval body, 0.3m x 0.25m x 0.08m
2. "SmallFish_DorsalFin" : Fan-shaped top fin
3. "SmallFish_TailFin"  : Forked tail, symmetrical
4. "SmallFish_PectoralFins" : Small oval fins (L+R)
5. "SmallFish_Eye_L/R"  : Simple sphere 0.012m

MATERIALS (bright tropical colors):
- "Mat_SmallFish_Body"   : Bright stripe pattern — use 2 materials:
  * "Mat_SmallFish_Orange": Base #FF6600, roughness 0.3, slight metallic 0.05
  * "Mat_SmallFish_White_Stripe": Base #FFFFFF, roughness 0.25
- "Mat_SmallFish_Eye"    : Base #050505, specular 1.0

Armature: Simple 3-bone spine + tail bone only (for GPU instancing friendly animation)

SHAPE KEYS:
- "Swim_L" / "Swim_R": Tail wag for swimming cycle

Collection: "IsleTrial_SmallFish"
After creation, set up a Particle System on a plane to preview school of 50 fish.
Print: "SmallFish polycount: X triangles — suitable for GPU instancing"
```
