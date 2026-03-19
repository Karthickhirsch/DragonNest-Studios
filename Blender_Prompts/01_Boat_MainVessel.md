# Prompt 01 — Main Boat / Player Vessel (IsleTrial)

## Game Context
- Game Name: IsleTrial
- Game Type: 3D Ocean Adventure / Action
- Graphics Target: High quality (not AAA, but visually rich — similar to Sea of Thieves lite)
- Engine: Unity (export as FBX)
- The boat is the MAIN player-controlled vessel.

---

## What the Boat Needs (from BoatController.cs)
- Harpoon mount point (forward-facing spawn point)
- Lantern (toggleable light source on the boat)
- Anchor (drops down from the hull)
- Sail (optional, influenced by wind)
- Boost visual element (exhaust/wake area at rear)

---

## Prompt to Give AI (Copy this exactly)

```
Write a complete Blender Python (bpy) script to create a high-quality, game-ready 
fishing/adventure boat model for a Unity game called IsleTrial.

Requirements:
- Blender version: 4.x compatible
- The boat should be approximately 10 meters long, 3 meters wide, 2.5 meters tall
- Style: Realistic wooden fishing boat, slightly weathered, not cartoon

GEOMETRY — Create the following separate mesh objects, each named exactly:
1. "Boat_Hull"        — Main hull, V-shaped bottom, raised bow, flat stern
                        Use bmesh to create a proper curved hull profile
                        Add subdivision surface modifier (level 2)
                        Planks direction should run bow to stern
2. "Boat_Cabin"       — Small wooden wheelhouse/cabin (1.5m x 2m x 1.8m)
                        Positioned at center-rear of hull
                        Has 4 small window cut-outs using boolean modifier
                        Sloped roof (not flat)
3. "Boat_Mast"        — Single wooden mast (0.15m radius, 6m tall)
                        Positioned at center-front of cabin
                        Add crossbar at 4m height (1.5m wide each side)
4. "Boat_Sail"        — Rectangular sail mesh (3m wide, 4m tall)
                        Attached to mast, slightly billowed shape using lattice deform
                        UV unwrapped for texture painting
5. "Boat_HarpoonMount" — Metal rotating base (cylinder 0.3m radius, 0.2m tall)
                         Mounted on the bow (front) of the boat
                         Has a barrel tube pointing forward (0.08m radius, 0.8m long)
                         This is the harpoon spawn point reference object
6. "Boat_Lantern"     — Hanging lantern on a small iron hook bracket
                        Position: left side of cabin exterior, at eye height
                        Lantern cage: hexagonal, 0.15m size
                        Glass pane inside cage (separate mesh for emissive material)
7. "Boat_Anchor"      — Traditional ship anchor shape
                        Chain attached (modeled as separate linked cylinders)
                        Position: hanging at bow, can be lowered
                        Size: 0.8m tall
8. "Boat_Rudder"      — Flat wooden rudder at stern, underwater
9. "Boat_Railing"     — Rope railing along both sides of the deck
                        Use curve + bevel for rope look
10. "Boat_Deck"       — Flat deck planks on top of hull
                        Individual plank geometry (not just flat plane)

MATERIALS — Create and assign named materials:
- "Mat_Wood_Hull"      : Base color #8B6914, roughness 0.85, normal map ready
- "Mat_Wood_Planks"    : Base color #A0782A, roughness 0.9, slight grain bump
- "Mat_Metal_Dark"     : Base color #2A2A2A, metallic 0.9, roughness 0.3
- "Mat_Sail_Canvas"    : Base color #E8DFC0, roughness 0.95, cloth-like
- "Mat_Lantern_Glass"  : Base color #FFFFAA, emission strength 2.0 (for baked glow)
- "Mat_Rope"           : Base color #C4A35A, roughness 1.0

UV UNWRAPPING:
- Run Smart UV Project on all mesh objects
- Set island margin to 0.02
- Scale UV islands to maximize texture space

ORGANIZATION:
- Create a collection named "IsleTrial_Boat"
- Parent all objects to an empty named "Boat_ROOT" at world origin
- Set origin of each object to its geometric center
- Apply all transforms (scale, rotation) before export

EXPORT SETTINGS (print to console):
- Print: "Ready to export: Select Boat_ROOT and export as FBX"
- Print each object name and its world position for Unity reference
- Print: "Harpoon spawn point: [Boat_HarpoonMount world position]"

After creating all geometry, set viewport shading to Material Preview.
```

---

## Follow-Up Prompts (run after the main script)

### Add LOD Variants
```
Using the existing boat objects in the scene, write a Blender Python script to:
1. Duplicate each "IsleTrial_Boat" object
2. Apply Decimate modifier (ratio 0.4) to create LOD1 versions
3. Apply Decimate modifier (ratio 0.15) to create LOD2 versions
4. Name them with suffixes: _LOD0, _LOD1, _LOD2
5. Move LOD1 and LOD2 to separate collections named "IsleTrial_Boat_LOD1" and "IsleTrial_Boat_LOD2"
```

### Add Weathering Details
```
Write a Blender Python script to add weathering to the IsleTrial boat:
1. Add a Geometry Nodes modifier to "Boat_Hull" that:
   - Scatters small rust spots (dark brown vertex color) near metal parts
   - Adds algae/moss vertex color (dark green) along the waterline (Y < 0)
2. Add a Wave texture to the hull normal map node for wood grain
3. Add scratches to "Boat_Hull" using a white noise texture mixed with wood material
```

### Bake Ambient Occlusion
```
Write a Blender Python script to:
1. Select all objects in the "IsleTrial_Boat" collection
2. Create a new 2048x2048 image texture named "Boat_AO_Bake"
3. Bake ambient occlusion for all boat objects into that texture
4. Save the baked texture to: //textures/Boat_AO.png
```

---

## Unity Setup After Export
- Import FBX into Unity
- Boat_HarpoonMount position = assign to `_harpoonSpawnPoint` in BoatController.cs
- Boat_Lantern = assign `Light` component child = `_lanternLight` in BoatController.cs
- Boat_ROOT = main GameObject with Rigidbody + BoatController + BoatStats
