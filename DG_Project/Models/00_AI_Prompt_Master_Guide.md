# AI Prompt Master Guide
## How to Generate 3D Models for Isle of Trials Using AI Tools

---

## What AI 3D Generation Tools Are

These are websites where you type a text description and the AI creates a 3D model for you — no Blender skills needed.

---

## Best Free AI 3D Model Tools (2026)

| Tool | Link | Free Tier | Best For |
|------|------|-----------|----------|
| **Meshy.ai** | https://www.meshy.ai | Yes (limited credits/day) | Characters, props, environment |
| **CSM.ai** | https://csm.ai | Yes (limited) | Environment, props |
| **Luma AI Genie** | https://lumalabs.ai/genie | Yes | Quick concept models |
| **Rodin (Hyper3D)** | https://hyper3d.ai | Yes (limited) | Characters, creatures |
| **Tripo3D** | https://www.tripo3d.ai | Yes | Props and objects |
| **Shap-E (OpenAI)** | https://github.com/openai/shap-e | Free (local) | Simple shapes |
| **Sketchfab** | https://sketchfab.com | Free download | Existing free models to reuse |

**Recommended for beginners: Start with Meshy.ai — it has the best quality and easiest interface.**

---

## How to Use Meshy.ai (Step by Step)

### Step 1 — Create Account
1. Go to https://www.meshy.ai
2. Click "Sign Up" — free with Google account
3. You get free credits daily

### Step 2 — Choose Generation Mode

**Text to 3D:**
- Click "Text to 3D"
- Paste the prompt from this folder
- Click Generate
- Wait 2–5 minutes
- Download the .OBJ or .FBX file

**Image to 3D:**
- Draw or find a reference image first
- Upload it + add a text description
- Better results than text-only for complex shapes

### Step 3 — Download Settings
Always download with these settings:
- **Format:** FBX (works best with Unity)
- **Texture:** Include textures
- **Resolution:** 1024 or 2048

### Step 4 — Import into Unity
1. Drag the FBX file into `Assets/_Game/Art/Models/` folder
2. Unity imports it automatically
3. In the Inspector → Model tab → set **Scale Factor** to 0.01 (FBX files are often 100x too big)
4. In Inspector → Rig tab → set **Animation Type** to Humanoid (for characters) or None (for props)

---

## Prompt Formula — How to Write Good Prompts

Every prompt in this folder follows this formula:

```
[Art Style] + [Object Name] + [Shape/Form Description] + [Key Details] +
[Materials/Colors] + [Mood/Tone] + [Technical Requirements]
```

### Example (Bad Prompt):
```
a dragon
```

### Example (Good Prompt):
```
Low poly stylized 3D game character, fire dragon with molten lava skin,
large muscular body, wide wingspan, horned skull, glowing orange eyes,
orange and black color scheme, cracked rocky texture with lava glow underneath,
game-ready mesh, no background, T-pose, centered on white background
```

---

## Art Style for ALL Models in This Game

Use this style description at the start of EVERY prompt to keep models consistent:

```
Low poly stylized 3D game asset, Nintendo Zelda Wind Waker art style,
clean geometry, smooth rounded edges, vibrant colors, game-ready mesh,
no background, white background, centered object
```

---

## Polygon Count Guidelines

| Model Type | Target Polygons |
|-----------|----------------|
| Player character | 3,000 – 8,000 tris |
| Enemy (small) | 1,000 – 3,000 tris |
| Enemy (large) | 3,000 – 6,000 tris |
| Boss | 8,000 – 20,000 tris |
| Environment prop (small) | 100 – 500 tris |
| Environment prop (large) | 500 – 2,000 tris |
| Island terrain chunk | 2,000 – 5,000 tris |

---

## Texture Guidelines

| Model Type | Texture Size |
|-----------|-------------|
| Player | 2048 x 2048 |
| Bosses | 2048 x 2048 |
| Enemies | 1024 x 1024 |
| Props (important) | 1024 x 1024 |
| Props (background) | 512 x 512 |

---

## If AI Output Quality Is Not Good Enough

Try these fixes:
1. **Add more detail to prompt** — describe specific body parts
2. **Use "Image to 3D"** — sketch the shape on paper, photograph it, upload as reference
3. **Use Sketchfab** — search for a similar free model and modify it in Blender
4. **Use Kenney.nl** — free stylized low-poly packs (perfect match for this game)
5. **Use ProBuilder in Unity** — for simple shapes (rocks, platforms, walls)

---

## Quick Reference — Which Tool for What

| Need | Use This |
|------|----------|
| Humanoid character (player, NPC) | Meshy.ai Text to 3D or Rodin |
| Monster / creature | Meshy.ai or Rodin |
| Rock / tree / plant | Tripo3D or Kenney.nl free packs |
| Building / ruins | Tripo3D or ProBuilder in Unity |
| Boat | Meshy.ai or Kenney Pirate Kit |
| Weapon / tool | Meshy.ai |
| UI icon (flat) | Not a 3D tool — use Krita/GIMP |
| Particle VFX | Unity Particle System (not a model) |

---

## Free Model Alternatives (No Generation Needed)

Before generating a model, always check if a free one already exists:

| Site | Link | What to search |
|------|------|---------------|
| Kenney.nl | https://kenney.nl/assets | "pirate", "nature", "dungeon" |
| Quaternius | https://quaternius.com | "stylized", "nature", "characters" |
| OpenGameArt | https://opengameart.org | Any keyword |
| Sketchfab | https://sketchfab.com | Filter: Free, Downloadable |
| Unity Asset Store | https://assetstore.unity.com | Filter: Free |

---

*Guide Version: 1.0 | Last Updated: March 2026*
