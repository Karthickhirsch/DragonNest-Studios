# Prompt 03 — Props & Pickup Items

## Game Context
- Game: IsleTrial — 3D Ocean Adventure
- These are in-game interactive objects the player picks up, shoots, or interacts with
- Props must match the boat controller features: harpoon, lantern, anchor, cargo
- Keep poly count optimized but high quality (1000–5000 tris per prop)
- Export individually as FBX for Unity prefab creation

---

## Prompt 03-A — Harpoon Projectile

```
Write a Blender Python script to create a high-quality harpoon projectile model
for a Unity game called IsleTrial.

This is the projectile fired from the boat's harpoon cannon.

Specifications:
- Total length: 1.2m
- Style: Realistic iron/steel harpoon, sharp barbed tip, rope attachment at rear

Objects to create:

1. "Harpoon_Shaft"
   - Cylindrical metal shaft: 0.04m radius, 1.0m length
   - Slight taper: thicker at middle (0.045m), thinner at both ends (0.032m)
   - Use bezier curve + screw modifier for smooth profile

2. "Harpoon_Head"
   - Conical sharp tip: 0.12m long, cone from 0.04m to sharp point
   - 2 barbed hooks on sides: curved spike shape, 0.06m long, angled backward 45 degrees
   - Model barbs by extruding and rotating faces from the shaft
   - Sharp edges on barbs using edge crease

3. "Harpoon_Rope_Ring"
   - Small iron ring at rear of shaft
   - Torus: major radius 0.04m, minor radius 0.005m
   - Used for rope attachment point

4. "Harpoon_Rope_Coil" (optional, for idle/docked state)
   - Rope coil hanging from ring: 6 loops of rope
   - Use Curve + Bevel (0.008m radius)

MATERIALS:
- "Mat_Harpoon_Iron"     : Base #1C1C1C, metallic 1.0, roughness 0.25 (sharp polished edges)
- "Mat_Harpoon_Iron_Old" : Base #2A2520, metallic 0.7, roughness 0.7 (worn shaft)
- "Mat_Harpoon_Rope"     : Base #C4A35A, roughness 1.0

UV: Smart UV Project, angle 55 degrees
Collection: "IsleTrial_Harpoon"
Parent: "Harpoon_ROOT" at origin
Apply all transforms, set origin to rear of shaft (spawn point)

Print: "Harpoon tip position (for hit detection): [tip world position]"
```

---

## Prompt 03-B — Barrel, Crate & Treasure Chest Props

```
Write a Blender Python script to create 3 interactive prop models for IsleTrial:
a barrel, a wooden crate, and a treasure chest.

--- BARREL ---
Object: "Prop_Barrel"
- Classic wooden barrel: 0.5m diameter, 0.7m tall
- Curved stave construction: 12 vertical wood planks with slight outward bulge
- 2 iron bands (hoops) around barrel at 1/4 and 3/4 height
- Lid on top (separate, removable in Unity)
- Materials:
  * "Mat_Barrel_Wood": Base #8B5E2A, roughness 0.9, normal for plank gaps
  * "Mat_Barrel_Iron": Base #1A1A1A, metallic 0.85, roughness 0.55
- Add bung hole (small circle cutout) on side

--- WOODEN CRATE ---
Object: "Prop_Crate"
- Wooden shipping crate: 0.6m x 0.5m x 0.5m
- 6 faces, each with 3 horizontal planks + corner wooden reinforcement strips
- Iron corner brackets on all 8 corners
- Rope handle loops on 2 sides (torus + short cylinder shape)
- Top planks should be separate mesh (lid) for opening animation
- "IsleTrial" burned/stamped text on one face (use text object + boolean)
- Materials:
  * "Mat_Crate_Wood": Base #9E7040, roughness 0.92
  * "Mat_Crate_Iron_Bracket": Base #222222, metallic 0.9, roughness 0.5

--- TREASURE CHEST ---
Object: "Prop_TreasureChest"
Base dimensions: 0.7m wide, 0.45m deep, 0.4m tall body + 0.25m domed lid

Parts:
1. "TreasureChest_Body"   — Box with slightly inset panels, plank detail
2. "TreasureChest_Lid"    — Domed arc lid (use curve + solidify)
3. "TreasureChest_Lock"   — Front iron padlock: rectangular body + shackle
4. "TreasureChest_Hinges" — 2 iron hinge strips on back (flat rectangular plates)
5. "TreasureChest_Trim"   — Iron banding strips: top edge, middle, corners
6. "TreasureChest_Interior" — Inside base (visible when lid opens), dark wood planks

Materials:
- "Mat_Chest_Wood_Dark"  : Base #5A3A1A, roughness 0.88, aged dark wood
- "Mat_Chest_Iron"       : Base #151515, metallic 0.85, roughness 0.6
- "Mat_Chest_Gold_Trim"  : Base #C8A000, metallic 0.95, roughness 0.3 (decorative gold edge)
- "Mat_Chest_Interior"   : Base #3A2010, roughness 0.95

UV: Smart UV Project on all
Collection: "IsleTrial_Props"
Apply all transforms, origin at base-center of each object
```

---

## Prompt 03-C — Rope, Chain & Anchor Accessories

```
Write a Blender Python script to create rope and chain accessory props for IsleTrial.

1. "Prop_RopeCoil"
   - Coiled rope on ground: 0.4m outer radius, 0.1m inner radius, 0.15m tall
   - Use curve + bevel: multiple spiral loops
   - "Mat_Rope_Hemp": Base #C4A35A, roughness 1.0

2. "Prop_RopeBundle"
   - Bundle of rope tied in middle: 0.3m long roll
   - Tied with thin rope band at center
   - Use multiple braided curve objects twisted together

3. "Prop_Chain_Segment" (modular — links together)
   - Single chain link: oval shape, 0.08m x 0.05m, wire thickness 0.012m
   - Use torus (major 0.04, minor 0.012) stretched into oval
   - Alternate links rotated 90 degrees
   - Create 10-link segment
   - "Mat_Chain_Iron": Base #1A1A1A, metallic 0.9, roughness 0.45

4. "Prop_AnchorChain" (full anchor chain)
   - 20 chain links, hanging in a natural catenary curve
   - Use bezier curve to guide link positions
   - Connects to "Boat_Anchor" object from prompt 01

5. "Prop_Net_Fishing"
   - Fishing net spread flat: 2m x 1.5m
   - Grid of thin rope strands (0.008m diameter curves)
   - Cork floats on top edge: 8 small cylinders
   - Lead weights on bottom edge: 8 small spheres
   - "Mat_Net_Rope": Base #C4A35A, roughness 1.0, alpha clip at 0.3 for mesh holes
   - UV mapped for transparency cutout texture

Collection: "IsleTrial_Accessories"
Apply transforms, logical origins
```

---

## Prompt 03-D — Lantern Props (Wall & Hand-Held)

```
Write a Blender Python script to create 2 lantern variants for IsleTrial:
one mounted lantern (for boat) and one hand-held/collectible lantern.

--- MOUNTED BOAT LANTERN ---
Object: "Prop_Lantern_Mounted"
- Iron bracket arm: L-shaped, 0.05m square profile, 0.25m long arm
- Hexagonal lantern cage: 0.15m inscribed radius, 0.25m tall
  * 6 vertical iron bars (0.01m diameter)
  * Top hexagonal cap (slightly pyramidal)
  * Bottom hexagonal base plate
- 6 glass pane inserts between bars (separate mesh)
- Candle/flame inside: small cylinder + cone for flame shape
- Hanging ring at top: torus 0.03m
- Chain hanging from ring: 3-link chain

--- HAND-HELD LANTERN ---
Object: "Prop_Lantern_Handheld"
- Cylindrical body: 0.08m radius, 0.18m tall, 8-sided
- Glass cylinder insert (emissive material)
- Top cap with carrying handle: semicircular wire handle
- Brass finish on body
- Flip-up glass shield mechanism (modeled, hinged)
- Oil reservoir at bottom (small disc, slightly wider)

MATERIALS:
- "Mat_Lantern_Iron"   : Base #0F0F0F, metallic 0.9, roughness 0.55
- "Mat_Lantern_Brass"  : Base #B8860B, metallic 0.92, roughness 0.28
- "Mat_Lantern_Glass"  : Base #FFEEAA, alpha 0.3, transmission 0.9, emission 1.5
- "Mat_Lantern_Flame"  : Base #FF8800, emission 4.0 (for baked light proxy)
- "Mat_Lantern_Chain"  : Base #1A1A1A, metallic 0.85, roughness 0.5

UV: Smart UV Project
Collection: "IsleTrial_Lanterns"
Set each lantern's light emission center as an Empty named:
- "Lantern_Mounted_LightPoint"
- "Lantern_Handheld_LightPoint"
These empties become Unity Light component positions.

Print both empty world positions on script completion.
```
