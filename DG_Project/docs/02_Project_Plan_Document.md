# Project Plan Document
## Isle of Trials — Development Roadmap

---

## Table of Contents
1. [Project Summary](#project-summary)
2. [Team Roles](#team-roles)
3. [Development Phases](#development-phases)
4. [Milestone Timeline](#milestone-timeline)
5. [Sprint Breakdown](#sprint-breakdown)
6. [Risk Register](#risk-register)
7. [Tools & Technology Stack](#tools--technology-stack)
8. [Definition of Done](#definition-of-done)

---

## 1. Project Summary

| Field | Details |
|-------|---------|
| **Project Name** | Isle of Trials |
| **Engine** | Unity 2022 LTS (or Unity 6) |
| **Total Estimated Duration** | 18 months |
| **Target Release** | Q4 2027 |
| **Development Model** | Agile (2-week sprints) |

---

## 2. Team Roles

| Role | Responsibilities |
|------|----------------|
| **Game Designer** | GDD, level design, puzzle design, balancing |
| **Unity Developer (Lead)** | Core systems, player controller, game loop |
| **Unity Developer (Junior)** | UI, save system, scene management |
| **3D Artist** | Environment, characters, bosses, VFX |
| **2D/UI Artist** | HUD, menus, map, icons |
| **Animator** | Player, boss, and enemy animations |
| **Sound Designer** | SFX, music integration |
| **QA Tester** | Bug tracking, playtesting, feedback |
| **Project Manager** | Sprint planning, tracking, communication |

> For indie solo/small teams: combine roles as needed. Unity Asset Store can substitute for several 3D/2D assets in early phases.

---

## 3. Development Phases

### Phase 0: Pre-Production (Months 1–2)
- Finalize GDD, all design documents
- Define tech stack and Unity project structure
- Create prototype / proof-of-concept for core mechanics
- Asset style guide created
- Set up version control (GitHub/GitLab)

### Phase 1: Vertical Slice (Months 3–4)
- One fully playable island (Tutorial Island — Driftwood Cay)
- Boat sailing mechanic functional
- One puzzle type fully implemented
- Basic enemy AI
- Placeholder art and sound

### Phase 2: Core Systems Development (Months 5–8)
- All core gameplay systems built and tested:
  - Boat mechanics (full)
  - Player combat and abilities
  - Puzzle system framework
  - Enemy AI framework
  - Boss fight system
  - Save/Load system
  - Inventory system
  - Map system
- 2 islands fully playable (with placeholder art)

### Phase 3: Content Production (Months 9–13)
- All 7 islands built and playable
- All 6 boss fights implemented
- All puzzle types implemented
- Full enemy roster built
- Sea zones and encounters designed
- Story cutscenes scripted and blocked
- Audio integrated (temp music/SFX)

### Phase 4: Art & Audio Polish (Months 14–16)
- Final art assets replace placeholders
- Full animations implemented
- Final music and SFX integrated
- Visual effects (VFX) polished
- UI/UX final pass

### Phase 5: QA & Balancing (Month 17)
- Full playtesting sessions
- Difficulty balancing for all islands and bosses
- Bug fixing
- Performance optimization

### Phase 6: Launch Preparation (Month 18)
- Gold build
- Store page setup (Steam, etc.)
- Trailer production
- Marketing assets
- Launch!

---

## 4. Milestone Timeline

| Milestone | Target Month | Deliverable |
|-----------|-------------|-------------|
| M0 — Pre-Production Complete | Month 2 | All docs, project setup, prototype |
| M1 — Vertical Slice | Month 4 | Playable tutorial island |
| M2 — Core Systems Complete | Month 8 | All game systems functional |
| M3 — Alpha Build | Month 10 | All islands playable (gray-box) |
| M4 — Beta Build | Month 14 | All content complete, temp assets |
| M5 — Content Complete | Month 16 | Final art, audio, cutscenes |
| M6 — Release Candidate | Month 17 | QA-certified build |
| M7 — Gold / Launch | Month 18 | Published game |

---

## 5. Sprint Breakdown

### Sprint Structure (2 weeks each)
- **Sprint Planning:** Day 1 — Define tasks and assign tickets
- **Daily Standups:** 15-min sync (async if remote)
- **Mid-Sprint Check:** Day 7 — Demo progress
- **Sprint Review:** Day 14 — Demo complete features
- **Retrospective:** Day 14 — What went well / improvements

### Example Sprint (Sprint 5 — Boat Mechanics)

| Task | Owner | Priority | Estimate |
|------|-------|----------|----------|
| Implement boat steering physics | Dev Lead | High | 3 days |
| Wind direction system | Dev Lead | High | 2 days |
| Boost ability + cooldown | Dev Junior | Medium | 1 day |
| Anchor interaction system | Dev Junior | Medium | 2 days |
| Harpoon projectile mechanic | Dev Lead | Medium | 2 days |
| Boat damage & durability UI | Dev Junior | Low | 1 day |
| QA testing boat mechanics | QA | High | 1 day |

---

## 6. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Scope creep (too many islands/features) | High | High | Lock scope at Phase 2; use change request process |
| Art bottleneck | Medium | High | Use asset store placeholders; hire freelancers if needed |
| Unity version incompatibility | Low | Medium | Stick to LTS version; avoid experimental features |
| Team member unavailability | Medium | Medium | Cross-train team members on critical systems |
| Performance issues on mobile | Medium | High | Profile early; set performance budgets per scene |
| Boss fight design being too hard/easy | High | Medium | Extensive playtesting; adjustable difficulty parameters |
| Puzzle design not fun | Medium | High | User test puzzles in Phase 1; iterate early |

---

## 7. Tools & Technology Stack

| Category | Tool |
|----------|------|
| **Engine** | Unity 2022 LTS / Unity 6 |
| **Language** | C# |
| **Version Control** | Git + GitHub / GitLab |
| **Project Tracking** | Trello / Jira / Notion |
| **3D Modeling** | Blender |
| **2D Art / UI** | Adobe Illustrator / Figma |
| **Texturing** | Substance Painter |
| **Animation** | Unity Animator + Blender |
| **VFX** | Unity VFX Graph / Particle System |
| **Audio** | FMOD + Audacity |
| **Communication** | Discord / Slack |
| **Build Distribution** | Steam (PC), App Stores (Mobile) |
| **CI/CD** | Unity Cloud Build |

### Key Unity Packages
- Universal Render Pipeline (URP)
- Cinemachine (camera)
- Input System (new)
- NavMesh (enemy pathfinding)
- TextMeshPro (UI text)
- DOTween (animations/tweening)
- Addressables (asset loading)

---

## 8. Definition of Done

A feature is considered "Done" when:
- [ ] Feature is fully implemented per design doc spec
- [ ] Feature has been tested by at least one QA pass
- [ ] No Critical or High severity bugs remain
- [ ] Feature performs within budget (frame time, memory)
- [ ] Code is reviewed and merged to main branch
- [ ] Scene/level build does not break existing features
- [ ] Documentation updated if applicable

---

*Document Version: 1.0 | Last Updated: March 2026*
