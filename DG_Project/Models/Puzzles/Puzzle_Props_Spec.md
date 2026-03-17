# Model Specs — Puzzle Props
## Isle of Trials — Puzzles/

---

## All Puzzle Props

These are the physical objects used across all puzzle types. Most are simple geometric shapes with stylized detail.

---

## Prop 1 — Symbol Tile (Rotating Panel)
**Puzzle:** Symbol Match | **Size:** 0.8 x 0.1 x 0.8 units

### Visual Description
- A flat square stone tile set into a wall or floor
- Slightly recessed center panel that rotates
- Ancient carvings around the border
- The center shows a symbol (swappable texture)
- Glows faintly when at correct orientation

### AI Prompt
```
Low poly stylized 3D game prop, square flat stone tile panel, slightly recessed rotating
center section with ancient symbol carved into it, decorative carved border frame,
faint magical glow lines at edges, ancient stone wall mounted panel appearance,
low poly Wind Waker style, grey stone with faint golden glow accents,
white background, top-down view showing face, game-ready mesh, 200-400 triangles
```

---

## Prop 2 — Mirror (Light Beam Puzzle)
**Puzzle:** Light Beam | **Size:** 0.6 x 0.1 x 1.0 units

### Visual Description
- A tall rectangular mirror in a decorative stone frame
- The mirror surface is polished metal (not glass — stylized)
- Stone frame has ancient carved patterns
- Sits on a rotating stone base
- Glows when a beam hits it

### AI Prompt
```
Low poly stylized 3D game prop, ancient stone-framed mirror on a rotating pedestal base,
tall rectangular polished bronze metal mirror surface that reflects light,
decorative carved stone frame around the mirror with ancient patterns,
round rotating stone base at the bottom that can spin freely,
low poly Wind Waker style, grey stone frame with polished bronze mirror and gold carvings,
white background, centered, game-ready mesh, 300-500 triangles
```

---

## Prop 3 — Light Receiver (Target)
**Puzzle:** Light Beam | **Size:** 0.8 x 0.8 x 0.8 units

### Visual Description
- A stone pedestal with a crystal bowl on top
- The bowl is empty and dull until a light beam hits it
- When activated: crystal glows brightly
- Has carved channel patterns leading to a gate mechanism

### AI Prompt
```
Low poly stylized 3D game prop, stone pedestal with a crystal bowl receptor on top,
short square stone pedestal with carved channel patterns on the sides,
shallow bowl shape on top made of grey crystal, inactive and dull appearance,
(active state: add bright yellow glow to the crystal bowl via emissive texture),
low poly Wind Waker style, grey stone with clear crystal bowl,
white background, centered, game-ready mesh, 200-400 triangles
```

---

## Prop 4 — Push Block
**Puzzle:** Push Block | **Size:** 1.0 x 1.0 x 1.0 units

### Visual Description
- A perfect cube stone block with ancient carved symbols on each face
- Heavy looking, slightly rough stone texture
- Small carved handles on the sides (visual only — not functional)
- Worn at the edges from being pushed

### AI Prompt
```
Low poly stylized 3D game prop, heavy stone cube block with ancient carved symbols
on each face — different symbol per face, worn edges from being pushed across stone floors,
rough grey sandstone texture, small decorative carved handles on each side face,
sturdy and heavy appearance, low poly Wind Waker style, sandy grey stone,
white background, centered at perfect cube angle, game-ready mesh, 200-400 triangles
```

---

## Prop 5 — Pressure Plate
**Puzzle:** Push Block / Timing | **Size:** 1.0 x 0.1 x 1.0 units

### Visual Description
- A flat square floor panel slightly recessed into the ground
- Has corner bracket details in metal
- A faint glyph in the center
- Inactive: grey stone, Activated: glows green

### AI Prompt
```
Low poly stylized 3D game prop, flat square floor pressure plate, slightly lower than floor level,
metal corner bracket details reinforcing the edges, ancient glyph symbol in the center,
appears as if it can be pressed down, low poly Wind Waker style,
grey stone with aged metal corner fittings (active version: center glyph glows green),
white background, top-down angle view, game-ready mesh, 100-200 triangles
```

---

## Prop 6 — Lever / Switch
**Puzzle:** Sequence / Circuit | **Size:** 0.3 x 0.3 x 0.8 units

### Visual Description
- A wall-mounted stone bracket with an iron lever handle
- Handle rotates up/down when activated
- Glowing indicator stone above the lever (red=off, green=on)

### AI Prompt
```
Low poly stylized 3D game prop, wall-mounted stone bracket with an iron lever switch,
stone mounting plate fixed to wall, iron bar lever that rotates up or down,
small glowing indicator gem above lever (red when off, green when activated),
chunky mechanical appearance, low poly Wind Waker style,
grey stone mount with dark iron lever and colored gem indicator,
white background, side view, game-ready mesh, 200-300 triangles
```

---

## Prop 7 — Pipe Segment (Circuit/Flow Puzzle)
**Puzzle:** Circuit/Flow | **Size:** 1.0 x 1.0 x 0.2 units (grid square)

### Visual Description
- A square flat wall panel with a pipe section built into it
- The pipe is visible as a raised channel on the panel face
- Can be: straight, L-shaped, T-shaped, or cross (+) shape
- Glows when active flow passes through

### Variants Needed:
- Pipe_Straight.fbx
- Pipe_LShape.fbx
- Pipe_TShape.fbx
- Pipe_Cross.fbx

### AI Prompt
```
Low poly stylized 3D game prop, square flat stone wall panel with raised pipe channel carved
into the face, the pipe channel runs in an L-shape from one edge to a perpendicular edge,
pipe has a circular cross section with visible steam/liquid channel groove,
slightly worn stone panel background, low poly Wind Waker style,
grey stone panel with copper-colored pipe groove, white background, centered front view,
game-ready mesh, 200-400 triangles
```
(Repeat with "straight", "T-shape", "cross" variations)

---

## Prop 8 — Tide Crystal (Collectible)
**Puzzle:** Boss Reward | **Size:** 0.5 x 0.5 x 0.8 units

### Visual Description
- A beautiful floating crystal shard, glowing from inside
- Each island's crystal has a different color and shape
- Floats and rotates slowly above a stone pedestal
- Shape: slightly irregular natural crystal formation

### Variants (6 total):
| Name | Color | Shape |
|------|-------|-------|
| Fire Crystal | Orange/Red | Jagged, asymmetric |
| Ice Crystal | Pale Blue | Smooth, elongated hexagon |
| Nature Crystal | Deep Green | Spiral organic form |
| Earth Crystal | Sandy Gold | Square-ish, heavy |
| Storm Crystal | Electric Purple | Branching forked |
| True Crystal (final) | Prismatic/White | Perfect diamond |

### AI Prompt — Fire Crystal
```
Low poly stylized 3D game collectible item, fire tide crystal, single irregular crystal shard
floating mid-air, jagged asymmetric flame-like shape, vivid glowing orange-red color from inside
like contained fire, faceted crystal surface with deep orange glow in the cracks,
dramatic magical glow aura around it, low poly Wind Waker style,
vivid orange and red crystal with inner fire glow, white background, centered,
game-ready mesh, 100-300 triangles
```
(Repeat for each crystal with its color/shape)

---

## Unity Import Checklist (Puzzle Props)
- [ ] All puzzle props in `Assets/_Game/Art/Models/Puzzles/`
- [ ] Pressure plate: Collider set to **isTrigger = true**
- [ ] Push block: Rigidbody with **isKinematic = true** + BoxCollider
- [ ] Mirror: Collider added for beam raycast detection
- [ ] Symbol tile: SpriteRenderer on face for symbol swap
- [ ] Lever: Animator for on/off rotation
- [ ] Crystal: Add spinning/floating animation via simple DOTween call or Animator
- [ ] Create Prefab variants for each pipe shape
