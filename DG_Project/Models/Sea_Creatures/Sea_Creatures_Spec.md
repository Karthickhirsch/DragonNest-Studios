# Model Specs — Sea Creatures
## Isle of Trials — Sea_Creatures/

---

## Sea Creature 1 — Coral Jellyfish
**Zone:** Coral Passage | **Size:** ~1.5 x 1.5 x 1.0 units

### Visual Description
- Large translucent jellyfish with a coral-patterned bell (dome)
- Bell has pink, orange and white coral patterns on the surface
- Long trailing tentacles (8–12 of them), wispy and translucent
- Glows faintly from inside
- Colors: Translucent pink/white dome, glowing pink and coral orange tentacles

### AI Prompt
```
Low poly stylized 3D game creature, large ocean jellyfish, translucent dome bell
with colorful coral pink and orange patterns across the surface, 10 long wispy translucent
trailing tentacles below the bell, soft inner bioluminescent pink glow from inside the bell,
graceful drifting floating pose, low poly Wind Waker style,
translucent pink white and coral orange color scheme with soft glow,
white background, centered, game-ready mesh, 1000-2000 triangles, 1024x1024 texture
```

---

## Sea Creature 2 — Razorfin Shark
**Zone:** Open Ocean | **Size:** ~3.0 x 0.8 x 1.2 units

### Visual Description
- A sleek aggressive-looking shark with an oversized razor-edged dorsal fin
- Dark blue-grey on top, white underbelly
- Rows of visible sharp teeth in a slight menacing grin
- Serrated fin edges like saw blades
- Glowing red predator eyes
- Colors: Dark ocean blue-grey top, white belly, red eyes, silver fin edges

### AI Prompt
```
Low poly stylized 3D game creature, aggressive ocean shark with oversized serrated razor
dorsal fin, sleek hydrodynamic body, dark ocean blue-grey coloring on top fading to
white underbelly, rows of clearly visible sharp triangular teeth in open mouth,
glowing menacing red predatory eyes, fin edges appear sharpened like saw blades,
swimming pose from the side, low poly Wind Waker style,
dark blue-grey and white with red eyes and silver sharp fin, white background, centered,
game-ready mesh, 1500-3000 triangles, 1024x1024 texture
```

---

## Sea Creature 3 — Tide Serpent
**Zone:** Mid-Ocean | **Size:** ~6.0 x 1.0 x 1.0 units

### Visual Description
- A very long ocean serpent, thicker than Zephyrath, more aquatic and less sky-dragon
- Covered in overlapping dark teal sea scales
- Blunt rounded head like a sea snake, with whisker-like feelers
- Glowing bio-luminescent spots along the sides (like a deep sea fish)
- Fin ridge along the back
- Colors: Dark teal, blue-green scales, bio-luminescent cyan spots, white eyes

### AI Prompt
```
Low poly stylized 3D game creature, large deep ocean sea serpent creature,
very long sinuous body covered in dark teal blue-green overlapping scales,
blunt rounded sea-snake head with short antenna feelers, ridge fin along the back,
rows of bioluminescent glowing cyan spots along both sides of the body like a deep sea fish,
blank white glowing eyes, thick muscular coiling body, underwater coil pose,
low poly Wind Waker style, dark teal blue-green scales with glowing cyan bioluminescent spots,
white background, centered, game-ready mesh,
3000-6000 triangles, 1024x1024 texture
```

---

## Sea Creature 4 — Frost Crab (Sea)
**Zone:** Near Island 2 | **Size:** ~1.5 x 1.5 x 0.7 units

### Visual Description
- A large crab with a shell made of solid blue-white ice
- Six sharp ice spike legs
- Massive claws that are blunt ice clubs (not pinchers — they slam)
- Frost breath vents on the shell
- Glowing pale blue eyes
- Colors: Pale ice blue shell, white ice legs, blue glowing eyes

### AI Prompt
```
Low poly stylized 3D game creature, large arctic ice crab, shell carapace made of solid
pale blue-white ice with frost crystal formations on top, six sharp pointed ice spike legs,
two massive club-like ice claw arms designed for slamming not pinching,
small frost breath vents visible on the shell surface, pale blue glowing eyes,
wide aggressive stance, low poly Wind Waker style,
pale ice blue and white color scheme with blue glowing eyes,
white background, centered, game-ready mesh,
2000-3500 triangles, 1024x1024 texture
```

---

## Sea Creature 5 — Abyssal Kraken Shard
**Zone:** Abyss Gate | **Size:** ~5.0 x 5.0 x 2.0 units (tentacles spread)

### Visual Description
- NOT a full kraken — this is a fragment, just the tentacle cluster
- A dark fleshy mass with 6 thick tentacles spreading outward
- Skin is pitch black with dark purple bioluminescent ring patterns
- Each tentacle tip has a glowing eye (5 glowing purple eyes total)
- At the center: a toothy beak-like mouth
- Colors: Pitch black skin, dark purple bioluminescent rings, purple eyes, pale beak

### AI Prompt
```
Low poly stylized 3D game creature, abyssal kraken tentacle creature, not a full kraken —
just a dark mass with 6 thick powerful tentacles spreading in all directions,
pitch black slimy-looking skin with dark purple bioluminescent ring patterns down each tentacle,
a sharp toothy beak mouth at the center mass, glowing purple eyes on each tentacle tip,
terrifying deep sea creature appearance, spreading reaching tentacle pose,
low poly Wind Waker style, pitch black with dark purple glow and pale beak,
white background, centered above-view, game-ready mesh,
4000-8000 triangles, 1024x1024 texture
```

---

## Sea Creature 6 — Deep Leviathan
**Zone:** Abyss Gate (background / environmental) | **Size:** ~30+ units (HUGE)

### Visual Description
- An absolutely massive serpent seen only as a dark shape passing beneath the waves
- Body is enormous — the player's boat is tiny in comparison
- Dark void black color, barely visible outline, just glowing white eyes in the deep
- Seen mostly as a massive shadow beneath the ocean surface
- NOT meant to fight — only a visual threat / avoidance encounter

### AI Prompt
```
Low poly stylized 3D game creature, colossal leviathan sea serpent viewed from above the water,
impossibly massive body visible as a dark shadow just beneath the ocean surface,
only the glowing white eyes are clearly visible piercing up through dark deep water,
enormous serpentine outline barely suggested through dark water, pure scale and dread,
low poly Wind Waker style, near-black deep ocean color with only white glowing eyes visible,
dark ocean water overhead view, centered, game-ready mesh,
5000-10000 triangles, 2048x2048 texture
```

---

## Sea Creature Animations

| Creature | Animations Needed |
|----------|------------------|
| Coral Jellyfish | Float (pulsing bell loop), Sting (tentacle spread) |
| Razorfin Shark | Swim (loop), Circle (tight turn loop), Ram (straight charge) |
| Tide Serpent | Slither (swim loop), Lunge (forward strike), Coil (wrap) |
| Frost Crab | Walk (6-leg scuttle), Slam (claw down), Freeze (ice spit) |
| Kraken Shard | Reach (tentacle extend), Grab (wrap around), Slam (down hit) |
| Deep Leviathan | Swim (slow massive loop) — barely visible in game |

---

## Unity Import Checklist (Sea Creatures)
- [ ] FBX in `Assets/_Game/Art/Models/SeaCreatures/`
- [ ] Add Rigidbody with appropriate constraints
- [ ] Add Collider for boat damage detection
- [ ] Kraken: Multiple child colliders (one per tentacle)
- [ ] Add appropriate AI script (sea creature patrol scripts)
- [ ] Jellyfish: No rigidbody needed — just waypoint drift coroutine
- [ ] Layer: "SeaCreature" for boat collision detection
- [ ] Scale appropriately — Leviathan should look enormous next to boat
