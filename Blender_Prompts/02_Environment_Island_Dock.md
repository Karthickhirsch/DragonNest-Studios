# Prompt 02 — Environment Models (Island, Dock, Rocks, Cliffs)

## Game Context
- Game: IsleTrial — 3D Ocean Adventure
- Environment style: Tropical/temperate island, real-scale, lush but not fantasy
- All assets export individually as FBX for Unity modular placement
- Graphics target: High quality — PBR materials, normal maps, AO ready

---

## Prompt 02-A — Tropical Island Base

```
Write a complete Blender Python (bpy) script to create a high-quality game-ready 
tropical island terrain asset for a Unity ocean game called IsleTrial.

Requirements:
- Blender 4.x compatible
- Island size: approximately 80m x 60m footprint, max height 20m
- Style: Realistic tropical island — sandy beach, rocky cliffs, flat jungle interior

GEOMETRY — Create the following objects:

1. "Island_Terrain"
   - Start with a subdivided plane: 60x60 grid, 80m x 60m size
   - Use bmesh to sculpt terrain:
     * Raise center into a hill (peak at 20m using smooth falloff)
     * Create a natural beach ring at edges (0-1m height, 8m wide)
     * Add rocky cliff faces on north side (steep 70-degree angle)
     * Add 3-4 smaller rocky outcrops using noise displacement
   - Apply Subdivision Surface modifier (level 2) for smooth terrain
   - Apply Displace modifier with Clouds texture (scale 8, strength 1.2) for surface detail
   - Assign vertex colors:
     * White/tan for beach areas (height < 1.5m)
     * Green for grassy areas (height 1.5m - 12m)
     * Dark grey for cliff/rock areas (slope > 45 degrees)
     * Dark green for jungle canopy areas (height > 8m, flat)

2. "Island_Cliffs_North"
   - Separate cliff face mesh on north side
   - Jagged, layered rock face using Voronoi displacement
   - Height: 15m, width: 30m
   - Sharp edges using edge crease + bevel modifier
   - Overhanging sections for visual drama

3. "Island_Beach_Sand"
   - Flat ring mesh following the island perimeter
   - Width: 6-10m, gentle slope toward water
   - Subdivided enough for wave ripple normal map
   - Vertex color: #F5DEB3 (wheat/sand)

4. "Island_Rocky_Outcrops" (collection of 5 rocks)
   - 5 individual rock meshes: Rock_01 through Rock_05
   - Sizes vary: 1m to 4m diameter
   - Irregular shape using Remesh + Displace with Musgrave texture
   - Some partially submerged (extend below Y=0)
   - Use Convex Hull to clean up geometry

MATERIALS:
- "Mat_Sand"          : Base #F5DEB3, roughness 0.95, height map for ripple detail
- "Mat_Grass_Island"  : Base #4A7A35, roughness 0.9, subsurface 0.1 (slight translucency)
- "Mat_Rock_Cliff"    : Base #5A5A5A, roughness 0.85, strong normal map, wet spec at bottom
- "Mat_Rock_Wet"      : Base #3A3A3A, roughness 0.3, metallic 0.05 (wet rock sheen)
- "Mat_Dirt_Path"     : Base #8B6347, roughness 0.95

UV UNWRAPPING:
- Island_Terrain: Use "Lightmap Pack" UV unwrap (for baking)
- All rocks: Smart UV Project, angle limit 66 degrees
- Set up a second UV channel on Island_Terrain for detail tiling textures

ORGANIZATION:
- Collection: "IsleTrial_Island"
- Empty parent: "Island_ROOT" at world origin (0,0,0)
- Apply all transforms

OUTPUT to console:
- Print island bounding box dimensions
- Print beach ring area in square meters
- Print "Ready for Unity: Export Island_ROOT as FBX"
```

---

## Prompt 02-B — Wooden Dock / Pier

```
Write a complete Blender Python (bpy) script to create a high-quality modular 
wooden dock/pier for a Unity ocean game (IsleTrial).

Requirements:
- The dock extends from shore into water
- Total length: 20m, width: 4m
- Realistic weathered wood construction
- Player can dock their boat here

GEOMETRY:

1. "Dock_MainPlatform"
   - Wooden plank surface: 20m long, 4m wide
   - Individual plank geometry: each plank 0.2m wide, 0.05m thick, 4m long
   - Slight height variation between planks (±0.01m) for realism
   - 2 missing planks (gap) for detail
   - End of dock has mooring post area

2. "Dock_Supports" (structural pillars)
   - 10 pairs of wooden support posts (every 2m along length)
   - Each post: 0.15m diameter cylinder, 2m tall below deck
   - Cross-brace beams between each pair
   - Posts taper slightly at bottom (driven into seabed)
   - Some posts lean slightly (use random small rotation ±3 degrees)

3. "Dock_Railings"
   - Rope railings on both long sides
   - Use Curve objects with circular bevel (0.02m radius)
   - Rope sags naturally between posts
   - 3 rope lines stacked vertically (0.4m, 0.7m, 1.0m heights)

4. "Dock_MooringPosts" (4 posts at dock end)
   - Thick wooden bollards: 0.2m diameter, 0.9m tall above deck
   - Rope loops around them (torus geometry)
   - Iron cap on top (dark metal material)

5. "Dock_Ladder"
   - Rope/wood ladder hanging off one side of dock into water
   - 6 rungs, 0.05m diameter rope sides, 0.03m wooden rungs

6. "Dock_Accessories"
   - 2 fishing nets hanging/draped over railing (cloth-simulated, then applied)
   - 1 wooden crate on dock (0.5m cube, planked sides)
   - 1 coil of rope (torus with rope texture, 0.4m radius)

MATERIALS:
- "Mat_Dock_Wood_Old"   : Base #7A5C35, roughness 0.95, high normal intensity for worn grain
- "Mat_Dock_Wood_Wet"   : Base #5A4020, roughness 0.5 (wet sections near waterline)
- "Mat_Dock_Rope"       : Base #C4A35A, roughness 1.0, slight normal for braid detail
- "Mat_Dock_Iron"       : Base #1A1A1A, metallic 0.8, roughness 0.6

UV UNWRAPPING: Smart UV Project for all, angle 66 degrees, margin 0.02

ORGANIZATION:
- Collection: "IsleTrial_Dock"
- Empty parent: "Dock_ROOT" at world origin
- Dock extends in the +Z direction from origin
- Water surface level = Y 0.0 (dock deck at Y=1.2m)
```

---

## Prompt 02-C — Modular Rock Pack (Scatter-Ready)

```
Write a Blender Python script to create a pack of 8 modular rock/boulder meshes
for procedural scattering in a Unity ocean game environment.

Each rock should be unique. Name them: Rock_A through Rock_H

Rock specifications:
- Rock_A: Large flat boulder, 3m x 2m x 0.8m, good for sitting/stepping on
- Rock_B: Tall spire rock, 0.6m base, 2.5m tall, sharp top
- Rock_C: Medium cluster — 3 rocks grown together, 2m overall
- Rock_D: Mossy round boulder, 1.5m diameter, very smooth top
- Rock_E: Flat stepping stone, 1.2m x 0.9m x 0.15m, slightly tilted
- Rock_F: Cracked rock with visible split down center, 1.8m
- Rock_G: Underwater rock (designed to sit half-submerged), 2m x 1m
- Rock_H: Pile of 4-5 small rocks grouped together

For each rock:
1. Start with an Icosphere (subdivisions 3)
2. Apply Displace modifier with Musgrave texture (different scale per rock)
3. Apply Remesh modifier (voxel, 0.05m) for clean topology
4. Apply second Displace for fine surface detail
5. Add Bevel modifier (width 0.02, segments 2) on sharp edges
6. Smart UV Project (angle 66)
7. Assign material "Mat_Rock_[A-H]" with slight color variation

Material variations:
- Dry rock: roughness 0.9, base around #6A6560
- Wet rock (G): roughness 0.25, darker base #3A3530
- Mossy (D): mix with green #3D5A30 vertex color on top surface

Output:
- Collection: "IsleTrial_Rocks"
- Print each rock's polycount after creation
- Apply all transforms, set origins to bottom-center (for easy ground placement)
```

---

## Prompt 02-D — Lighthouse

```
Write a Blender Python script to create a high-quality lighthouse model for IsleTrial.

Specifications:
- Total height: 18m
- Style: Classic coastal lighthouse, stone/white painted

Objects:
1. "Lighthouse_Tower"
   - Tapered cylinder: base radius 2.5m, top radius 1.8m, height 15m
   - Stone texture geometry: horizontal band subdivisions every 0.5m
   - 6 small window openings (use boolean) evenly spaced vertically
   - Slight inward taper using a bezier curve profile + screw modifier

2. "Lighthouse_LanternRoom"
   - Glass-paneled octagonal room at top: 2m radius, 1.5m tall
   - 8 glass panels (separate mesh for emissive/glass material)
   - Metal frame between panels (0.05m beams)
   - Rotating light beacon inside (cone shape, emissive)

3. "Lighthouse_Base"
   - Stone foundation platform: 6m x 6m, 1.5m tall
   - Rough stone texture geometry
   - Entrance door arch (boolean cut)

4. "Lighthouse_Railing_Top"
   - Metal railing around lantern room
   - Thin metal posts (0.04m) with horizontal bars

5. "Lighthouse_Steps"
   - External spiral staircase around lower 3m of tower
   - 12 stone steps

MATERIALS:
- "Mat_Lighthouse_White"  : Base #F0EDED, roughness 0.7, slight normal for plaster texture  
- "Mat_Lighthouse_Stone"  : Base #8A7D6E, roughness 0.9, strong displacement/normal
- "Mat_Lighthouse_Metal"  : Base #2A2F35, metallic 0.85, roughness 0.4
- "Mat_Lighthouse_Glass"  : Base #88CCFF, alpha 0.15, transmission 1.0, IOR 1.45
- "Mat_Lighthouse_Light"  : Base #FFFF88, emission 5.0

Collection: "IsleTrial_Lighthouse"
Parent empty: "Lighthouse_ROOT"
```
