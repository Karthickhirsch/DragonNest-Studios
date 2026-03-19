# Prompt 05 — Ocean & Weather Assets

## Game Context
- Game: IsleTrial — includes a WeatherSystem (wind affects boat speed/direction)
- Ocean environment needs physical assets (not just shader-based)
- These are static mesh props that float, drift, or define the ocean scene
- Style: Realistic, weathered, sea-worn

---

## Prompt 05-A — Navigation Buoys & Floating Markers

```
Write a Blender Python script to create a set of 3 navigation buoy models 
for IsleTrial ocean environment.

--- BUOY TYPE 1: "Buoy_Marker_Red" ---
- Conical top, cylindrical body: 0.4m radius, 1.2m tall
- Top cone: 0.3m tall, angled marker fin on top
- 3 iron band rings around body (horizontal)
- Chain attachment at bottom (3 chain links visible)
- Number painted on side: Use text object "2" + boolean emboss 0.01m depth
- Barnacles on lower half (displacement modifier, low strength)
- Top light housing: small cage with red light sphere inside

--- BUOY TYPE 2: "Buoy_Marker_Green" ---
- Same construction as Red, swap color
- Can top instead of cone (flat cylindrical lid)
- Number "3" embossed

--- BUOY TYPE 3: "Buoy_Lighted_Large" ---
- Larger buoy: 0.7m radius, 2m tall
- Rounded capsule shape body
- Solar panel on top: flat rectangular panel, slightly angled
- Large light housing on mast: 0.3m cage with white light
- Anchor chain attachment visible at waterline
- Warning stripes: alternating orange/white painted bands

MATERIALS:
- "Mat_Buoy_Red_Paint"    : Base #CC2200, roughness 0.6, chipped paint normal map
- "Mat_Buoy_Green_Paint"  : Base #00882A, roughness 0.6
- "Mat_Buoy_Orange"       : Base #FF6600, roughness 0.55
- "Mat_Buoy_Iron_Rusty"   : Base #3A2010, metallic 0.5, roughness 0.85
- "Mat_Buoy_Light_Red"    : Base #FF2200, emission 3.0
- "Mat_Buoy_Light_White"  : Base #FFFFFF, emission 4.0
- "Mat_Barnacle"          : Base #6A6055, roughness 0.95

UV: Smart UV Project all, angle 55 degrees
Collection: "IsleTrial_Buoys"
Apply transforms, origin at waterline center of each buoy
Print: "Buoy waterline Y position: 0.0 — set this as water surface in Unity"
```

---

## Prompt 05-B — Shipwreck (Sunken/Beached)

```
Write a Blender Python script to create a dramatic shipwreck environmental asset
for IsleTrial — a sunken/half-beached old wooden ship.

This is a LARGE environment set piece (not the player's boat).
Old ship size: 18m long, 5m wide hull

GEOMETRY:

1. "Wreck_Hull_Main"
   - Broken ship hull: only 60% remains, rest is destroyed/missing
   - Tilted 35 degrees to starboard (right side down)
   - Use boolean cuts to create jagged broken edges
   - Hull planks visible: individual plank edge detail
   - Barnacles and seaweed on lower half
   - Holes in hull: 3-4 large irregular punctures

2. "Wreck_Mast_Broken"
   - Broken mast: 4m tall stump (original was 10m)
   - Snapped at top: jagged wooden break
   - Rope still hanging from break point (curve + bevel)
   - Fallen mast section: 6m long piece lying on deck

3. "Wreck_Deck_Planks"
   - Partially intact deck: gaps where planks are missing
   - Some planks bent upward, some sunken inward
   - Algae and sand accumulation in corners

4. "Wreck_Cargo_Scattered"
   - 4 barrels (use Prop_Barrel from prompt 03, slightly damaged)
   - 2 broken crates (split open, use boolean to cut)
   - Scattered coins/items (simple disc meshes glinting)

5. "Wreck_Coral_Growth"
   - Coral formations growing on hull: 8 coral clusters
   - Branching shapes using skin modifier on curves
   - Colors: orange, pink, white coral variants

6. "Wreck_Seaweed"
   - Long ribbon seaweed hanging from hull edges
   - Bezier curve + ribbon cross-section bevel
   - 12 strands of varying length (0.5m - 2m)
   - Translucent green material

MATERIALS:
- "Mat_Wreck_Wood_Old"    : Base #4A3018, roughness 0.95, strong normal, very dark
- "Mat_Wreck_Wood_Wet"    : Base #2A1A08, roughness 0.4 (submerged sections)
- "Mat_Wreck_Barnacle"    : Base #7A7060, roughness 0.95
- "Mat_Coral_Orange"      : Base #FF5500, roughness 0.8, slight emission 0.3
- "Mat_Coral_White"       : Base #F0EDE0, roughness 0.85
- "Mat_Seaweed"           : Base #1A6A20, roughness 0.7, alpha 0.8, translucent

Collection: "IsleTrial_Shipwreck"
Parent: "Wreck_ROOT"
Position wreck tilted: apply 35 degree rotation, then apply transforms
Print polycount breakdown per object
```

---

## Prompt 05-C — Weather Visual Assets (Storm & Fog Props)

```
Write a Blender Python script to create physical weather-related mesh assets
for IsleTrial's weather system (referenced in BoatController WeatherSystem).

--- DRIFTWOOD COLLECTION ---
Create 5 driftwood pieces: "Driftwood_01" through "Driftwood_05"
- Weathered log shapes: 0.5m to 2m long, branching
- Use skin modifier on a curve with random thickness
- Bleached white-grey color, smooth from water erosion
- Scatter on beaches and floating in water
- "Mat_Driftwood": Base #D0C8B8, roughness 0.95

--- STORM DEBRIS PACK ---
1. "Debris_Plank_01/02/03" : Broken wooden planks, 0.3m-0.8m long
2. "Debris_Barrel_Half"    : Split barrel, half remaining (boolean cut)
3. "Debris_Rope_Tangled"   : Tangled rope ball: 0.3m radius, use curve knots
4. "Debris_Sail_Torn"      : Torn sail fragment: 1.5m x 0.8m, torn edges
                             Use cloth simulation then apply for natural drape
5. "Debris_Mast_Fragment"  : 1.5m broken wood pole, splintered end

--- WATER SPLASH MESH (for VFX proxy) ---
Object: "VFX_Splash_Mesh"
- Ring of water droplets rising outward
- 16 water drop shapes arranged in 1.5m radius ring
- Drop shape: teardrop (sphere pinched at top)
- Use for particle system reference shape in Unity
- "Mat_Water_VFX": Base #88CCFF, alpha 0.7, transmission 0.8, roughness 0.1

--- FOAM PATCH MESH ---
Object: "VFX_FoamPatch"
- Irregular flat disc: 3m diameter
- Bumpy surface (foam texture displacement, strength 0.05)
- Used on boat wake in Unity
- "Mat_Foam": Base #F8F8F8, roughness 0.9, alpha 0.85

Collection: "IsleTrial_WeatherProps"
Apply transforms on all static objects
Do NOT apply transforms on cloth-simulated objects (keep for Unity physics)
```

---

## Prompt 05-D — Sky & Atmosphere Props (Volumetric Helpers)

```
Write a Blender Python script to create sky reference objects and atmospheric
props for IsleTrial's ocean skybox environment.

1. "SeaBird_Silhouette" (x3 variants)
   - Seagull in glide pose: 0.6m wingspan
   - Simple but detailed enough for mid-distance: wing curve, tail fan, head/beak
   - 3 pose variants: wings flat, wings slightly up, banking left
   - "Mat_Seabird": Base #EEEEEE, roughness 0.8 (white bird)
   - "Mat_Seabird_Dark": Base #2A2A2A (wingtip feathers, roughness 0.9)

2. "Cloud_Volume_Proxy" (mesh stand-in for Unity cloud shader)
   - 3 cloud shapes: Small, Medium, Large
   - Fluffy rounded geometry using Metaball → converted to mesh
   - Very low poly (these just block out volume positions)
   - "Mat_Cloud": Base #FFFFFF, roughness 1.0, alpha 0.6

3. "Horizon_Rock_Arch"
   - Dramatic sea arch: 8m tall, 6m wide arch opening
   - Rocky natural stone, sea-carved smooth base, jagged top
   - Use boolean cylinder on a rock mass for the arch opening
   - Good for background/horizon dressing

4. "Float_Kelp_Bulb" (x1 model, scattered via Unity particle)
   - Kelp bulb float: 0.15m sphere, slightly wrinkled
   - Thin kelp ribbon hanging down: 0.8m, ribbon cross-section
   - "Mat_Kelp_Bulb": Base #4A6A20, roughness 0.8
   - "Mat_Kelp_Ribbon": Base #2A5A15, roughness 0.85, alpha 0.9, translucent

Collection: "IsleTrial_AtmosphericProps"
Print render stats for each: polygon count and material count
```

---

## Prompt 05-E — Ocean Surface Reference Mesh (for shader alignment)

```
Write a Blender Python script to create an ocean surface reference mesh
for IsleTrial — used to align Unity's water shader and set buoyancy.

1. "Ocean_Surface_Reference"
   - Flat plane: 200m x 200m, centered at world origin
   - Y = 0.0 (this is the exact water surface level)
   - Subdivided: 40 x 40 grid (enough for displacement preview)
   - Apply Ocean modifier: scale 1.0, resolution 8, wave scale 0.3
   - This is a REFERENCE ONLY — not the final water in Unity
   - "Mat_Ocean_Preview": Base #0A3A5A, alpha 0.5, roughness 0.1

2. "Ocean_Buoyancy_Plane"
   - Simple 200m x 200m, NO subdivision
   - Y = 0.0 exactly
   - Used in Unity: assign to WaterSurface field in buoyancy scripts
   - "Mat_Invisible_Collider": alpha 0.0 (invisible)

3. "Ocean_Depth_Markers" (visual reference empties)
   - 5 empties placed at: 0m, -5m, -10m, -20m, -50m depth (Y axis)
   - Named: "Depth_0m", "Depth_5m" etc.
   - Used as reference for creature spawn depth zones

Print:
- "Water surface Y level: 0.0"
- "Boat hull should extend to Y: -0.8 when loaded"
- "Anchor bottom chain should reach Y: -3.0 minimum"

Collection: "IsleTrial_OceanReference"
```
