# Solo Developer Starter Guide
## Isle of Trials — Everything You Need as a Beginner

> You have the game idea, the docs, and the code. Now here is everything else you need — software, learning, free assets, tools, and a realistic step-by-step plan to actually build this game alone.

---

## Table of Contents
1. [Be Honest With Yourself First](#1-be-honest-with-yourself-first)
2. [Software to Install (All Free)](#2-software-to-install-all-free)
3. [What to Learn — In Order](#3-what-to-learn--in-order)
4. [Free Learning Resources](#4-free-learning-resources)
5. [Free Assets (No Money Needed)](#5-free-assets-no-money-needed)
6. [Paid Tools Worth Buying Later](#6-paid-tools-worth-buying-later)
7. [Your Realistic Solo Roadmap](#7-your-realistic-solo-roadmap)
8. [Daily Work Habit for Solo Dev](#8-daily-work-habit-for-solo-dev)
9. [Where to Get Help When Stuck](#9-where-to-get-help-when-stuck)
10. [Common Beginner Mistakes to Avoid](#10-common-beginner-mistakes-to-avoid)
11. [PC Requirements](#11-pc-requirements)

---

## 1. Be Honest With Yourself First

This is the most important section. Read it carefully.

**Isle of Trials is a large game.** It has:
- An open ocean world
- 7 islands with unique themes
- 6 boss fights with 3 phases each
- 10+ puzzle types
- A save system, weather system, day/night cycle
- UI, audio, animations, VFX

**For a solo beginner, building this full game could take 3–5 years.**

That is not a reason to give up. It is a reason to be smart about it.

### The Smart Approach for You:

```
DO NOT build the whole game at once.

Instead:
  Step 1 → Learn Unity basics (2-3 months)
  Step 2 → Build just ONE tiny island — the Tutorial Island
  Step 3 → Make it fun and complete
  Step 4 → Add one more island
  Step 5 → Repeat until the full game exists
```

**Every professional game was built this way — one piece at a time.**

---

## 2. Software to Install (All Free)

Install all of these before doing anything else.

### 2.1 Unity Hub + Unity Editor
**What it is:** The game engine where you build everything.
**Download:** https://unity.com/download

Steps:
1. Download and install **Unity Hub**
2. Inside Unity Hub → click **"Install Editor"**
3. Choose **Unity 2022.3 LTS** (LTS = Long Term Support = most stable)
4. During install, check these modules:
   - ✓ Microsoft Visual Studio Community (free code editor)
   - ✓ Windows Build Support
   - ✓ Android Build Support (for mobile, optional now)
5. Click Install — takes 20-40 minutes

**Cost: FREE**

---

### 2.2 Visual Studio Community (Code Editor)
**What it is:** Where you write and edit C# scripts.
**Download:** Installed automatically with Unity, OR https://visualstudio.microsoft.com/

Steps after install:
1. Open Visual Studio
2. Go to: Tools → Get Tools and Features
3. Install workload: **"Game development with Unity"**

**Cost: FREE**

> **Alternative:** VS Code (lighter weight) — https://code.visualstudio.com/
> Install the "C# Dev Kit" and "Unity" extensions from VS Code marketplace.

---

### 2.3 Git + GitHub Desktop
**What it is:** Saves your project history. If you break something, you can go back.
**Download:** https://desktop.github.com/

Steps:
1. Create a free account at https://github.com
2. Install GitHub Desktop
3. Create a new repository for your game project
4. Commit your project every time you finish a working feature

**Cost: FREE**
> **WARNING:** Never work without Git. Losing weeks of work to a crash is heartbreaking and avoidable.

---

### 2.4 Blender (3D Modeling)
**What it is:** Create 3D models for islands, characters, objects.
**Download:** https://www.blender.org/download/

You will use this to make:
- Island environment meshes (rocks, trees, buildings)
- Character models
- Boat model

**Cost: FREE**
> You do NOT need to become a professional modeler. Learn enough to make simple low-poly models. This game suits a stylized low-poly art style perfectly.

---

### 2.5 GIMP or Krita (2D Art / Textures)
**What it is:** Free alternatives to Photoshop for making textures and UI.

- **GIMP:** https://www.gimp.org/ (general image editing)
- **Krita:** https://krita.org/ (better for painting/concept art)

You will use this for:
- Textures for 3D models
- UI icons (health bar, ability icons)
- Map icons, sprites
- Concept sketches

**Cost: FREE**

---

### 2.6 Audacity (Audio Editing)
**What it is:** Free audio editor for trimming, adjusting sound effects.
**Download:** https://www.audacityteam.org/

**Cost: FREE**

---

### 2.7 Notion or Obsidian (Personal Project Notes)
**What it is:** Keep your design notes, tasks, bugs, and ideas organized.
- **Notion:** https://www.notion.so/ (free tier is great)
- **Obsidian:** https://obsidian.md/ (fully offline, free)

**Cost: FREE**

---

## 3. What to Learn — In Order

Do NOT try to learn everything at once. Follow this exact order.

### Phase A — Unity Basics (Month 1–2)
Learn these before touching ANY of the game code:

| Topic | Why You Need It |
|-------|----------------|
| Unity Editor layout | Know where everything is (Hierarchy, Inspector, Project, Scene, Game) |
| GameObjects & Components | Everything in Unity is a GameObject with components attached |
| Transform (position, rotation, scale) | Moving things in 3D space |
| C# basics | Variables, if/else, loops, functions, classes |
| MonoBehaviour | The base class every Unity script uses |
| Start() and Update() | Where to initialize and run code |
| SerializeField / Inspector | How to expose variables to the Unity UI |
| Prefabs | Reusable GameObjects you can stamp into scenes |
| Scenes | How levels and menus are organized |

**Time investment: 1–2 hours per day for 6–8 weeks**

---

### Phase B — Intermediate Unity (Month 3–4)
After you can make a basic game, learn these:

| Topic | Why You Need It |
|-------|----------------|
| Physics (Rigidbody, Collider) | Boat physics, enemy collision, ocean buoyancy |
| CharacterController | Player movement on islands |
| NavMesh + NavMeshAgent | Enemy pathfinding / AI movement |
| Animator + Animation Clips | Make characters move smoothly |
| UI (Canvas, Image, TextMeshPro) | HUD, health bars, menus |
| ScriptableObjects | Store game data (item stats, enemy stats) cleanly |
| Scene management | Load/unload scenes for each island |

---

### Phase C — Advanced Topics (Month 5+)
Only after you have a working prototype:

| Topic | Why You Need It |
|-------|----------------|
| Cinemachine | Smart camera for sailing and boss fights |
| Shader Graph (URP) | Ocean shader, VFX materials |
| VFX Graph / Particle System | Fire, ice, lightning effects |
| Input System (new) | Player and boat controls |
| Audio (AudioSource, AudioMixer) | Music crossfade, SFX |
| JSON Save System | Save/load game data |
| Object Pooling | Performance for spawned objects |

---

## 4. Free Learning Resources

### Unity Official (Best Starting Point)
| Resource | Link | What to learn |
|----------|------|----------------|
| Unity Learn | https://learn.unity.com | Start with "Unity Essentials" pathway |
| Unity Manual | https://docs.unity3d.com | Reference while building |
| Unity Scripting API | https://docs.unity3d.com/ScriptReference | Look up any C# function |

### YouTube Channels (Free, Excellent Quality)
| Channel | Best For |
|---------|----------|
| **Brackeys** | Best beginner Unity tutorials (older but still works) |
| **Code Monkey** | Clean Unity tutorials, C# patterns |
| **Game Maker's Toolkit** | Game design thinking (not code, but essential) |
| **Sebastian Lague** | Advanced Unity topics (pathfinding, terrain, water) |
| **Jason Weimann** | Unity architecture and best practices |
| **Goldmetal** | Beginner-friendly step-by-step game builds |

### Specific Tutorials for This Game
Search these exact terms on YouTube:

| What You Need | Search Term |
|--------------|-------------|
| Ocean/water in Unity | "Unity URP stylized ocean shader" |
| Boat movement | "Unity boat controller physics" |
| Top-down player | "Unity top-down player controller" |
| Enemy AI | "Unity NavMesh enemy AI tutorial" |
| Boss fight | "Unity boss fight phases tutorial" |
| Save system | "Unity save game JSON tutorial" |
| Day night cycle | "Unity day night cycle directional light" |
| Puzzle system | "Unity puzzle game tutorial" |

### C# Learning (if you don't know C#)
| Resource | Link |
|----------|------|
| C# for Unity (free) | https://learn.unity.com/course/beginner-programming |
| Microsoft C# Docs | https://learn.microsoft.com/en-us/dotnet/csharp |
| freeCodeCamp C# | Search "freeCodeCamp C# full course" on YouTube |

---

## 5. Free Assets (No Money Needed)

You don't need to create everything from scratch. Use these free resources.

### 3D Models
| Source | Link | What to get |
|--------|------|-------------|
| **Unity Asset Store (Free)** | https://assetstore.unity.com | Filter by FREE — thousands of assets |
| **Kenney.nl** | https://kenney.nl/assets | Excellent free low-poly 3D packs |
| **Sketchfab (Free)** | https://sketchfab.com | Download free 3D models |
| **Quaternius** | https://quaternius.com | Free stylized low-poly packs (perfect for your game) |
| **OpenGameArt** | https://opengameart.org | Free game art, models, textures |

**Recommended free packs for this game:**
- Kenney's "Pirate Kit" — boats, islands, sea objects
- Kenney's "Nature Kit" — trees, rocks, plants
- Quaternius "Stylized Nature" — perfect for jungle island
- Unity Asset Store: search "Low Poly Water", "Low Poly Island"

---

### Textures
| Source | Link |
|--------|------|
| **Poly Haven** | https://polyhaven.com — Free 4K textures, HDRIs |
| **Ambient CG** | https://ambientcg.com — Free PBR textures |
| **Texture Haven** | Included in Poly Haven |

---

### Audio — Music
| Source | Link | Notes |
|--------|------|-------|
| **Freesound.org** | https://freesound.org | Free SFX (attribution required for some) |
| **OpenGameArt Music** | https://opengameart.org | Free game music |
| **Free Music Archive** | https://freemusicarchive.org | Free music with licenses |
| **Kevin MacLeod** | https://incompetech.com | Royalty-free music (attribution) |
| **Pixabay Music** | https://pixabay.com/music | No attribution needed |

---

### Audio — Sound Effects
| Source | Link |
|--------|------|
| Freesound.org | Waves, wind, fire, ice sounds |
| Kenney Audio | https://kenney.nl/assets — free SFX packs |
| Mixkit | https://mixkit.co/free-sound-effects |
| ZapSplat | https://www.zapsplat.com |

---

### Unity Asset Store — Essential FREE Packages
Search these on https://assetstore.unity.com (filter: Price = Free):

| Package | Use |
|---------|-----|
| **Starter Assets — Third Person** | Base player controller to learn from |
| **Low Poly Water** | Ocean surface |
| **Simple Low Poly Nature Pack** | Island environments |
| **DOTween** | Animation/tweening (free version works great) |
| **TextMeshPro** | Already included with Unity |
| **Cinemachine** | Already included as a package |
| **ProBuilder** | Built-in — create geometry inside Unity |
| **ProGrids** | Built-in — grid snapping for level design |

---

## 6. Paid Tools Worth Buying Later

**Only buy these after you've been developing for 3+ months and know you need them.**

| Tool | Price | What It Does |
|------|-------|-------------|
| **Unity Asset Store assets** | $5–$60 | Environment packs, characters, animations |
| **Odin Inspector** | ~$55 one-time | Makes the Unity Inspector 10x better |
| **Amplify Shader Editor** | ~$60 | Visual shader editor (good for ocean) |
| **FMOD Studio** | Free for indie (<$200k revenue) | Professional audio |
| **Adobe Substance Painter** | ~$20/month | Professional 3D texturing |
| **Spine 2D** | ~$70 one-time | If you decide to use 2D animations |

> **Total you should spend as a beginner: $0**
> Everything in section 5 is completely free and good enough to ship a full game.

---

## 7. Your Realistic Solo Roadmap

Here is a REALISTIC plan broken into stages. Do not skip stages.

### Stage 1 — Learn Unity Basics (2–3 months)
**Goal:** Be able to make a simple game from scratch.

Tasks:
- [ ] Install all software from Section 2
- [ ] Complete "Unity Essentials" on learn.unity.com (free)
- [ ] Watch Brackeys "How to make a Video Game" series on YouTube (free)
- [ ] Make a tiny test game (any genre — just something that works)
- [ ] Learn C# basics: variables, if statements, loops, classes
- [ ] Understand: GameObjects, Components, Prefabs, Scenes

**Do NOT start Isle of Trials yet.**

---

### Stage 2 — Build the Prototype Island (1–2 months)
**Goal:** One island that is fun to walk around in.

Tasks:
- [ ] Create a new Unity project with URP
- [ ] Download free low-poly island assets (Kenney/Quaternius)
- [ ] Build Tutorial Island layout in Unity (rough blockmesh)
- [ ] Get the player walking around (use Starter Assets as reference)
- [ ] Add one simple enemy that patrols
- [ ] Add one push-block puzzle
- [ ] Make sure it's FUN to play

**Milestone: Show this to one friend. If they enjoy it, keep going.**

---

### Stage 3 — Add the Boat (1 month)
**Goal:** Player can sail between two points.

Tasks:
- [ ] Create a boat model (Kenney pirate kit or Blender)
- [ ] Implement BoatController.cs from the Code folder
- [ ] Set up OceanBuoyancy.cs
- [ ] Make the boat feel satisfying to drive
- [ ] Add one sea creature (just patrol, basic collision)

---

### Stage 4 — First Real Island + Boss (2–3 months)
**Goal:** One complete island with a boss fight.

Tasks:
- [ ] Build Ember Isle (volcanic theme)
- [ ] Implement Ignar_MoltenDrake.cs boss fight
- [ ] Add Fire Tide Crystal reward
- [ ] Implement Fire Dash ability
- [ ] Make the boss fight feel exciting (camera shake, sound, VFX)

---

### Stage 5 — Systems Polish (1–2 months)
**Goal:** Save system, HUD, inventory all working.

Tasks:
- [ ] HUD showing health, ability, boat durability
- [ ] Save/Load game (JSON)
- [ ] Inventory with items
- [ ] Map system showing discovered islands
- [ ] Weather changes at sea

---

### Stage 6 — Remaining Islands (6–12 months)
Add one island at a time:
- Island 2 (Ice)
- Island 3 (Jungle)
- Island 4 (Desert)
- Island 5 (Storm)
- Island 6 (Final)

Each island follows the same formula: build environment → add puzzles → build boss → add ability reward.

---

### Stage 7 — Polish & Release
- VFX and particles
- Final audio pass
- Difficulty balancing
- Bug fixing
- Build for PC
- Upload to itch.io (free) or Steam ($100 fee)

---

## 8. Daily Work Habit for Solo Dev

The biggest challenge for solo developers is **staying consistent**.

### Recommended Daily Schedule (even 1 hour counts):

```
Monday    — Code one small feature
Tuesday   — Fix bugs from Monday
Wednesday — Work on environment/art
Thursday  — Code one small feature
Friday    — Test and polish what you built this week
Saturday  — Watch one tutorial, learn something new
Sunday    — Rest (seriously, rest prevents burnout)
```

### The "One Task Rule":
Every day, write down ONE specific task to complete. Not "work on the game." Something like:
- "Make the player jump"
- "Add health potion pickup"
- "Build the dock area for Tutorial Island"

Completing one small task every day = a finished game after a year.

### Track your progress:
Use Notion or a simple text file to log what you did each day. Looking back at progress is very motivating.

---

## 9. Where to Get Help When Stuck

You WILL get stuck. Every developer does. Here is where to go:

### For Unity/C# Questions:
| Resource | How to Use |
|----------|-----------|
| **Unity Forums** | https://forum.unity.com — ask anything |
| **Unity Discussions** | https://discussions.unity.com |
| **Stack Overflow** | https://stackoverflow.com — search C# errors |
| **Reddit r/unity** | https://reddit.com/r/unity |
| **Reddit r/gamedev** | https://reddit.com/r/gamedev |

### For Error Messages:
1. Copy the FULL error message from Unity's Console window
2. Paste it into Google
3. Usually the first StackOverflow or Unity Forum result has the answer

### Discord Servers (Real-Time Help):
- Unity Discord: https://discord.gg/unity
- Game Dev League: https://discord.gg/gamedev
- Brackeys Discord: (search "Brackeys Discord" — very helpful community)

### AI Help (like me!):
- Paste error messages and ask what they mean
- Ask "how do I add X to my game in Unity"
- Ask me to explain any script in the Code/ folder

---

## 10. Common Beginner Mistakes to Avoid

### ❌ Mistake 1: Starting Too Big
Don't build all 7 islands at once. Build ONE island completely first.

### ❌ Mistake 2: Skipping Learning
Don't copy the Code/ folder into Unity and expect it to work without understanding it first. Spend 2 months learning basics first. The code will make much more sense after.

### ❌ Mistake 3: No Version Control
Not using Git is like doing a 10-hour drawing and not saving. One crash and it's gone.
**Commit to GitHub every single time you finish a working feature.**

### ❌ Mistake 4: Perfectionism
Don't spend 2 weeks making the perfect rock texture. Make something that looks decent, move on, and come back to polish later.

### ❌ Mistake 5: Scope Creep
Don't add new features before the existing ones work. Stick to the plan.

### ❌ Mistake 6: Working in Isolation Too Long
Show your game to real people after every major milestone. Their feedback is invaluable. Share on Reddit r/unity or r/gamedev.

### ❌ Mistake 7: Ignoring Console Errors
Red errors in Unity's Console = your game is broken. Never ignore them. Fix each error before adding new features.

### ❌ Mistake 8: Copying Code Without Understanding
If you paste a script and don't understand what it does, search for a tutorial that explains it. Understanding beats copy-pasting.

---

## 11. PC Requirements

Make sure your computer can handle Unity development.

### Minimum Specs:
| Component | Minimum |
|-----------|---------|
| OS | Windows 10 (64-bit) |
| CPU | Intel Core i5 (any recent generation) |
| RAM | 8 GB |
| GPU | Any GPU with DirectX 11 support |
| Storage | 20 GB free (Unity takes ~10 GB, projects grow) |
| Internet | Needed for downloading assets and tutorials |

### Recommended Specs for Comfortable Development:
| Component | Recommended |
|-----------|-------------|
| CPU | Intel Core i7 / AMD Ryzen 7 |
| RAM | 16 GB |
| GPU | NVIDIA GTX 1060 or better |
| Storage | SSD with 50+ GB free |

> If your PC is slow, use **smaller scenes** and **low-poly placeholder art** during development. Replace with final art at the end.

---

## Your First 7 Days Action Plan

**Day 1:** Install Unity Hub, Unity 2022.3 LTS, Visual Studio Community

**Day 2:** Open Unity. Watch: "Unity Interface Overview" on YouTube (30 min). Click around, don't be scared.

**Day 3:** Start "Unity Essentials" on learn.unity.com. Complete the first 2 modules.

**Day 4:** Watch Brackeys "How to Make a Video Game" Episode 1 on YouTube. Follow along.

**Day 5:** Create a brand new empty project. Place some 3D objects (cubes, spheres). Move them around. Add a Rigidbody to one and press Play.

**Day 6:** Install GitHub Desktop. Create a repository. Commit your test project.

**Day 7:** Download Kenney's free pirate kit. Import it into Unity. Look at the models.

**After 7 days:** You will have Unity installed, know the basics of the interface, and have your first version-controlled project. That is a real start.

---

## Summary: Your Toolkit

| Category | Tool | Cost |
|----------|------|------|
| Game Engine | Unity 2022.3 LTS | FREE |
| Code Editor | Visual Studio Community | FREE |
| Version Control | Git + GitHub Desktop | FREE |
| 3D Modeling | Blender | FREE |
| 2D Art / Textures | Krita + GIMP | FREE |
| Audio Editing | Audacity | FREE |
| Free 3D Assets | Kenney.nl + Quaternius | FREE |
| Free Music/SFX | Freesound.org + Pixabay | FREE |
| Free Unity Assets | Unity Asset Store (free filter) | FREE |
| Project Notes | Notion | FREE |
| Learning | Unity Learn + YouTube | FREE |
| Help & Community | Reddit + Unity Forums + Discord | FREE |

**Total cost to start: $0.00**

Everything you need to build this game exists for free. The only investment is your time and persistence.

---

> **Final Encouragement:** Every game developer started knowing nothing. The difference between people who finish games and people who don't is simply: **keep going, one small task at a time.** Your documentation and code are already ahead of where most beginners start. You have everything you need.

---

*Guide Version: 1.0 | Created: March 2026*
