# Model Spec — Player Boat
## Isle of Trials — Player_and_Boat/

---

## Model Overview

| Field | Value |
|-------|-------|
| **Model Name** | PlayerBoat |
| **Role** | Player's sailing vessel across the ocean |
| **Style** | Low poly stylized wooden sailboat |
| **Size in Game** | ~4 wide x 8 long x 3 tall Unity units |
| **Target Polygons** | 2,000 – 5,000 triangles |
| **Texture Size** | 2048 x 2048 |
| **Rig Type** | None (static mesh — sails animated separately) |
| **Unity Scale** | Set Scale Factor to 0.01 after import |

---

## Visual Description

**Hull:**
- Classic wooden sailboat hull shape (pointed bow, wide stern)
- Worn weathered wood planks with visible grain and gaps
- Slightly battered — this is an adventurer's boat, not a luxury yacht
- Brass rivets along the hull edges
- A small wooden anchor hanging off the bow

**Deck:**
- Open flat deck with a ship wheel at the back (stern)
- A small wooden mast in the center
- A coil of rope near the harpoon mount
- A small wooden chest on deck (the player's inventory chest)
- A hanging lantern on a pole at the bow

**Sails:**
- One main sail — canvas/cloth texture, slightly torn at edges
- Color: Off-white/cream with a simple compass rose symbol painted on it
- Can be a separate mesh (for wind billowing animation)

**Additional Details:**
- Harpoon launcher mounted on the bow (a simple crank-style launcher)
- Small wooden figurehead at the bow (stylized fish or bird)
- Life ring hanging on the side

**Colors:**
- Hull: Warm brown wood tones (oak/mahogany)
- Sails: Cream/off-white
- Metal parts: Aged brass/bronze
- Rope: Light tan

---

## Separate Mesh Parts (for animation/interaction)

| Part | File Name | Purpose |
|------|-----------|---------|
| Hull (main) | Boat_Hull.fbx | Main static mesh |
| Sail | Boat_Sail.fbx | Separate for cloth simulation |
| Ship Wheel | Boat_Wheel.fbx | Rotates when steering |
| Lantern | Boat_Lantern.fbx | Toggleable light source |
| Harpoon Launcher | Boat_Harpoon.fbx | Rotates to aim |
| Anchor | Boat_Anchor.fbx | Drops when anchored |

---

## Float Points (for OceanBuoyancy.cs)
Create 4 empty child Transforms at the hull corners:
```
Position (relative to boat center):
  FL: (-1.5, -0.3, 3.0)   — Front Left
  FR: ( 1.5, -0.3, 3.0)   — Front Right
  BL: (-1.5, -0.3, -3.0)  — Back Left
  BR: ( 1.5, -0.3, -3.0)  — Back Right
```

---

## AI Generation Prompt

Paste into **Meshy.ai → Text to 3D**:

```
Low poly stylized 3D game asset, small wooden sailing boat for an adventure game,
classic sailboat hull with pointed bow and wide stern, weathered worn wooden planks
with brass rivets, single mast with a large cream-colored sail bearing a compass rose symbol,
ship wheel at the stern, small wooden chest on deck, hanging lantern on bow pole,
harpoon launcher mounted on the bow, coil of rope visible on deck,
wooden anchor hanging at bow, slightly battered adventurous look,
low poly stylized art style similar to Legend of Zelda Wind Waker,
warm brown wood colors, cream sails, aged brass metal fittings,
viewed from 3/4 angle above, centered on white background, game-ready mesh,
2000-5000 triangles, 2048x2048 texture
```

**For Sail only:**
```
Low poly stylized 3D game asset, single rectangular cloth sail for a small sailboat,
slightly billowing in wind, off-white cream canvas texture with hand-painted compass rose
symbol in the center, slightly worn and torn edges, subtle cloth fold details,
game-ready mesh, centered on white background, 500 triangles
```

---

## Blender Creation Guide

### Step 1 — Hull
1. Add → Mesh → Cube
2. Scale: X=2, Y=4, Z=1
3. In Edit Mode → select bottom face → scale to narrow it (boat hull V-shape)
4. Select front face → scale smaller and extrude forward to form the bow point
5. Loop cut along the length to add plank lines → slightly offset alternate rows (plank look)
6. Add Subdivision Surface modifier level 1 for smooth hull curve
7. Apply modifier before export

### Step 2 — Deck
1. Select top faces → extrude slightly up
2. Add a flat plane on top for the walking deck

### Step 3 — Mast
1. Add → Mesh → Cylinder → Scale tall and thin (0.1 x 0.1 x 4)
2. Position at boat center

### Step 4 — Sail
1. Add → Mesh → Plane → Scale to sail size
2. Subdivide 4 times for cloth detail
3. Apply Wave modifier for a gentle billow effect

### Step 5 — Props (Wheel, Chest, Lantern)
- Ship Wheel: Add Torus → delete half → add spokes with cylinders
- Chest: Simple cube with lid, rounded edges
- Lantern: Cylinder + cone top, glass material inside

### Step 6 — Export
- Export each part separately as FBX
- Or export whole boat as one FBX with named mesh objects inside

---

## Unity Import & Setup Checklist
- [ ] Boat_Hull.fbx → `Assets/_Game/Art/Models/Boat/`
- [ ] Tag boat root GameObject: **"Boat"** (required by IslandProximityLoader.cs)
- [ ] Add Rigidbody (mass=500, drag=1, angular drag=2)
- [ ] Add OceanBuoyancy.cs + assign 4 float point Transforms
- [ ] Add BoatController.cs + BoatStats.cs
- [ ] Add BoxCollider for main hull
- [ ] Assign Boat_Wheel to ship wheel child, add rotation script
- [ ] Assign Boat_Lantern light component — connect to BoatController._lanternLight
- [ ] Scale Factor = 0.01 on FBX import

---

## Free Alternative
Download **Kenney's Pirate Kit**: https://kenney.nl/assets/pirate-kit
It includes a perfect low-poly boat that works immediately with no modification.
