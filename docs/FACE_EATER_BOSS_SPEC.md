# REN — Face-Eater: Vertical-Slice Boss Spec (MECHANICS ONLY)

Status: cloud design, 2026-10-01. **Nothing is PIE-tested.** Implementation: `docs/IMPLEMENTATION_P4_FACE_EATER.md`. Local task: `docs/tasks/P4_FACE_EATER.md`. QA: `docs/QA_FACE_EATER.md`.

**Visual status:** `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.
- `ProjectDocs/References/REFERENCE_MANIFEST.md` is not yet in the repo.
- This spec makes **no** art decisions (armour, materials, colours, anatomy, VFX language, animation style).
- The locked canon used here is limited to:
  - ~3.8 m funerary humanoid
  - empty vertical cartouche head
  - identity fragments in the torso
  - hooked/extraction staff
  - no skull imagery
  - no faceless-monster redesign
  - core concept: identity theft / extraction

## 1. What the fight teaches

**Normal damage is not enough.**
- The player survives the boss's attacks.
- The player notices that blade hits don't move the health bar.
- The player uses what the Blank Cartouche and the Necropolis Glyph taught: **interact with carved names at the right moment**.
- That opens the boss's **chest seal**. The seal physically becomes vulnerable; it is not a glowing orb.
- Then the player deals real damage in a short, obvious window.

It is one polished slice boss, not a Souls-scale system:
- understandable on the first attempt
- readable in third person
- distinct from the Nameless Dead (who are damaged directly)
- restart-safe
- cannot soft-lock

## 2. Core loop

1. The player enters the arena (`REN_GW_Trigger_ArenaEnter`). The entry slab rises.
2. Dormant → **Intro** (≤ 2 s) → **Combat**.
3. In Combat the boss attacks. Blade hits are **deflected (0 damage, clear feedback)**.
4. A committed attack ends in a **recovery** that explicitly opens the Glyph window (`bGlyphWindowOpen`).
5. The player interacts with **any one** of the four Glyph pillars while the window is open.
6. The chest seal opens → **Exposed** (4 s, no attacks, no movement). Hits deal real damage.
7. The window ends → **Staggered** (1.2 s, the seal closes, the boss regathers) → Combat. The pillars reset.
8. Repeat. When health reaches 0 during Exposed → **Defeated**. The entry slab lowers.

The **first attack after Intro is always the Heavy Strike**, the clearest teaching moment.

## 3. State machine — `E_FaceEaterState` (sole phase authority)

There are exactly six states. **Only `BP_FaceEater` changes state, through `SetBossState(NewState)`.** Generic AI or StateTree logic may run **only in Combat**, and only for locomotion and facing. It never chooses attacks or phases.

| State | Entered when | Exits to | Attacks | Damage accepted | Generic AI | Glyph interaction | Camera / UI | On restart |
|---|---|---|---|---|---|---|---|---|
| **Dormant** | Level start; `ResetEncounter()` | Intro (player overlaps ArenaEnter) | none | **0** (ignored) | **stopped** | disabled | Boss bar hidden | Boss teleported to its Dormant marker |
| **Intro** | ArenaEnter overlap while Dormant | Combat (after `IntroDuration` 2.0 s) | none | **0** | **stopped** | disabled | Boss bar fades in, name shown. No camera takeover | → Dormant |
| **Combat** | Intro end; Staggered end | Exposed (valid Glyph); Combat (attack loop) | Hook Sweep, Heavy Strike, (Grab) | **0, deflected with feedback** (§6) | **allowed**: approach and face only, paused while an attack sequence runs | **only** while `bGlyphWindowOpen` | Bar visible | → Dormant |
| **Exposed** | `RequestExpose()` succeeds | Staggered (timer `ExposedDuration` 4.0 s); Defeated (Health ≤ 0) | none | **full** (`ExposedHitDamage`, per-cycle cap) | **stopped** (no move, no rotate) | disabled | Bar visible (drops) | → Dormant |
| **Staggered** | Exposed timer ends with Health > 0 | Combat (after `StaggerDuration` 1.2 s, plus a 1.0 s attack grace) | none | **0** (the seal is closing) | **stopped** | disabled (pillars reset at exit) | Bar visible | → Dormant |
| **Defeated** | Health ≤ 0 (only reachable from Exposed) | terminal | none | ignored | **stopped permanently** | disabled permanently | Bar fades out; `OnBossDefeated` fires | **Stays Defeated** (never resurrected) |

Invariant checks run on every state change (implementation §7). For example: in any non-Combat state, the AI must be stopped, the glyph window closed and the attack hitboxes inactive.

## 4. Attack set (budget: 2 mandatory + 1 cuttable)

**Common rules:**
- The boss is **stationary during an attack**: no lunge, no root motion.
- Tracking is allowed only during the early anticipation. It **locks** before the active frames, so there's no 180° snap after commitment.
- Hits are resolved by **explicit geometric queries** at scripted times (not animation notifies, not physics). Each attack hits the player **at most once**.
- Attacks are never cancelled by player damage (the boss doesn't flinch in Combat). Every attack sequence is aborted by a state change or a reset (generation token, implementation §6).
- After recovery: a 0.8 s idle/reposition gap, then the scheduler picks the next attack.
- Damage is expressed as a **fraction of the player's MaxHealth**, so it's independent of donor units.
- Placeholder anticipation: the boss stops, turns and holds a readable pose (a donor montage at reduced play-rate, `TEMP_PLACEHOLDER`). An optional dev-only telegraph shape (`bDebugTelegraphs`) draws the hit area. It is **not** final VFX language.

| | **1. Hook Sweep** (mandatory) | **2. Heavy Strike** (mandatory) | **3. Identity Extraction Grab** (CUTTABLE) |
|---|---|---|---|
| Purpose | Space control / lateral evasion test | High commitment, **safest Glyph teaching moment** | Punishes hugging the boss |
| Start condition | Player within 450 cm and within ±100° of the boss's facing | Player within 650 cm (any angle; the boss turns) | Player within 300 cm and within ±45°; not used in the last 2 attacks |
| Preferred range | 250–420 | 300–600 | ≤ 250 |
| Anticipation | **1.0 s**: tracking ≤ 120°/s for 0.7 s, then **locked** 0.3 s | **1.4 s**: tracking ≤ 90°/s for 1.0 s, then **locked** 0.4 s | **0.8 s**: tracking ≤ 150°/s for 0.5 s, then locked 0.3 s (reach telegraph) |
| Active window | 0.35 s. Queries at +0.0 and +0.2 s: horizontal arc, radius **420** from the boss centre, **±80°** around the locked facing | 0.25 s. One query at +0.1 s: circle of radius **220** centred **400** ahead | 0.3 s. One query at +0.1 s: sphere of radius **150** centred 250 ahead, ±45° |
| Recovery | **1.6 s** | **3.0 s** ("staff stuck in the ground") | On miss: **2.2 s**. On hit: 1.0 s |
| Glyph window | Opens at RecoveryStart for **1.5 s** (a *possible* opportunity) | Opens at RecoveryStart for **2.8 s** (*guaranteed* reachable anywhere; see §8) | On miss: 2.0 s. On hit: **none** |
| Damage (of player MaxHealth) | 20% | 35% | 25% |
| Knockback | Lateral, away from the arc: 500 XY / 150 Z | Away from the impact centre: 700 XY / 200 Z | Pushed back 600 XY, plus 0.8 s of player input lock ("extraction" feedback) |
| Player's intended answer | Step out of the arc sideways or back (or dodge, if one exists) | Read the long wind-up, get out of the circle, **then go to a pillar** | Don't hug the boss; step back when it reaches |
| After | Back to scheduler | Back to scheduler | Back to scheduler |

**Scheduler (Combat only, re-evaluated every 0.25 s while idle):**
1. The first attack after Intro is **Heavy Strike**.
2. A Heavy Strike is guaranteed at least every **3rd** attack.
3. Otherwise pick by distance: within 300 (and Grab enabled and allowed) → Grab 40% / Sweep 60%; within 450 → Sweep 60% / Heavy 40%; within 650 → Heavy; beyond 650 → approach (AI).
4. Never 3 Sweeps in a row.

The Grab **does not** apply any stolen-name status. Its prototype consequence is damage, knockback and a short input lock only.

## 5. Glyph pillars and the recovery window

- The four arena pillars `REN_GW_Arena_GlyphPillar_01..04` (fixed landmarks) each get the **same** `BP_FaceEaterGlyph` (`BPI_Interactable`), layered on top like the Cartouche. **One logic for all four.**
- **The window is explicit.** Only attack sequences call `OpenGlyphWindow(Duration)` and `CloseGlyphWindow()`. They write `bGlyphWindowOpen` and fire `OnGlyphWindowChanged(bOpen)`. Nothing infers it from animation state.
- `CanInteract` is true **only if** `bEnabled AND Boss.State == Combat AND Boss.bGlyphWindowOpen AND NOT bUsedThisCycle`.
- **One valid interaction → `Boss.RequestExpose(GlyphIndex)`.** The boss re-checks the same conditions (authoritative). If valid: close the window, abort the rest of the recovery, set `bUsedThisCycle` on that glyph, and enter **Exposed**.
- **Invalid interaction is not consumed.** No prompt is shown (the P1 focus logic hides it when `CanInteract` is false), E does nothing, and no error popup appears.
- **Spatial choice, not busywork:** any pillar works. All pillars reset when the Exposed cycle ends (Staggered → Combat).
- **Feedback hooks** (nullable): `OnGlyphWindowChanged` drives an optional material-state parameter on the pillars (`TEMP_PLACEHOLDER`, e.g. a groove-darkening scalar) and an optional sound. The prompt appearing is the primary signal.
- **One-time hint** (cuttable): a TEMP subtitle fires once, after 6 deflected hits **or** after 2 opened windows without a Glyph use:
  - Arabic is TEMP and editable. English placeholder: *"The seal answers to carved names."*

## 6. Damage model (state-gated; no RPG resistances)

Every incoming player hit goes through **one** function, `HandleIncomingHit(Instigator)`.

| State | Health effect | Feedback |
|---|---|---|
| Dormant, Intro, Staggered | 0 (ignored) | none / soft deflect |
| **Combat** | **0** | **Deflect:** 0.05 s hit-stop on the player, a small camera shake, a nullable deflect sound. The boss does not flinch. The health bar doesn't move. Counts toward the hint |
| **Exposed** | `ExposedHitDamage` = **7** per hit, capped at `CycleDamageCap` = **35** per Exposed window | Bar drops visibly, plus a nullable hit sound |
| Defeated | ignored | none |

**Decision: option A (0 damage in Combat, with clear physical feedback), not B (chip damage).**
- Chip damage lets a patient player brute-force the boss and skip the lesson.
- It makes the health bar move during Combat, which contradicts "my normal attacks are not solving this".
- A rigid "deflect" (hit-stop, shake, no flinch, a still bar) says *blocked*, not *broken*. The player still gets physical feedback for every hit.

**Health:**
- `MaxHealth` = **100**. The boss counts hits itself; donor damage amounts are ignored, so the fight doesn't depend on donor tuning.
- A cap of 35 per cycle means at least **3** cycles with excellent play (35 + 35 + 30). A typical first-timer landing 3–4 hits per window needs **4–5** cycles.
- Exposed is 4.0 s. Tune `ExposedHitDamage`, `CycleDamageCap` and `ExposedDuration` only, never MaxHealth inflation.
- In Exposed, **any** player hit on the boss counts as a hit on the open seal. The prototype doesn't require bone or component targeting, because donor hit data is unverified. Restricting hits to a `ChestSeal` hit-box is a later upgrade, only if the donor reports hit components.

## 7. Exposed and Staggered

- **Exposed (4.0 s):**
  - On entry, the chest seal **physically opens**: the placeholder `ChestSeal` component moves from its closed to its open relative transform over 0.25 s. `TEMP_PLACEHOLDER` shape; no glow.
  - AI stopped, no movement, **no rotation** (the player can position freely), no attacks.
  - Full damage per §6.
  - Exit: the timer → Staggered, or Health ≤ 0 → Defeated (immediately).
- **Staggered (1.2 s):**
  - Kept as a short, deliberate **closing beat**: the seal closes, the boss regathers, and no damage or attacks happen. Then Combat resumes with a 1.0 s grace period before the first attack.
  - Recommendation: Staggered adds player value only as this **fair, readable window-ending**, so keep it short. It is **not** a posture system and **not** a bonus-damage window. A bonus window after the seal visibly closes would contradict the one rule the player just learned: *seal open = damage*.
- **Defeated:** stop everything; the seal stays open (placeholder); the boss collapses or holds still; the bar fades; the entry slab lowers; `OnBossDefeated` fires.
  - Narrative payoff hooks: canon says killed monsters yield a Ren Glyph. Placeholder: a TEMP subtitle and the slice end card (separate task).

## 8. Arena requirements (static; checked in `Scripts/Tests/test_gatewest_layout.py`)

These are taken from the existing GateWest shell and were not redesigned. The only addition is the entry lock and the ArenaEnter trigger.

| Requirement | Value | Status (offline test) |
|---|---|---|
| Arena interior | 2200 × 1900 cm, walls 900, open top | ✔ |
| Sweep room around the boss centre marker | ≥ 420 + 200 cm to the side walls; ≥ 620 to the end walls | ✔ |
| Worst distance from any point to the nearest pillar face | **766 cm** → (766 − 300 reach) / 500 cm/s + 0.5 s reaction ≈ **1.4 s** < Heavy window 2.8 s | ✔ (guaranteed) |
| Sweep window (1.5 s) | Reachable when fighting within ~5 m of a pillar | ✔ (a "possible" opportunity) |
| Boss can follow everywhere | Pillar–wall gaps (390), pillar–pillar gaps (1180 × 680) and pillar–end-wall gaps all ≥ boss diameter + margin (200) | ✔ |
| Corner cheese | Player in a corner vs boss touching both walls: at most ≈ 187 cm apart (centre to centre) < sweep reach 420 | ✔ |
| Boss recess | 600 wide, lintel at 700 > boss height 380 + 50 | ✔ |
| Entry lock | `REN_GW_ArenaGate_Slab` rests below the threshold and rises 640 to 600 tall (unjumpable). ArenaEnter is ≥ 150 cm past the slab, full arena width | ✔ |
| Camera | No roof; walls 900. Lock-on: none | PIE check |
| Pillar collision / camera trapping | 3.3 m lanes | PIE check |

Assumed values (verify locally): boss capsule radius 90 / height 380; player run speed 500 cm/s; P1 interaction trace 350 cm.

## 9. Encounter start, checkpoint and reset

- **Start:** the boss stands Dormant at `REN_GW_Marker_FaceEater_Center_PLACEHOLDER` (0, 9550), visible from the corridor (a readable approach). The player crosses ArenaEnter → the slab rises (1.5 s) → Intro (2 s) → Combat.
  - No Sequencer, no camera takeover.
  - Optional (cuttable): Dormant at `…_Start_PLACEHOLDER` in the recess, with the boss walking out during Intro.
- **Checkpoint:** `REN_GW_Respawn_ArenaApproach` (0, 8000), outside the arena.
- **Reset on player death (non-negotiable):** `ResetEncounter()` (implementation §6) restores everything:
  - health and state
  - timers, timelines and sequences (generation token)
  - glyphs and the window
  - the chest seal and hit areas
  - the AI
  - the boss transform
  - the boss bar
  - the entry slab (lowered, open)
  - the arena trigger (re-armed)
  The player respawns outside with the slab open. There are no duplicate actors: the boss is placed once and never destroyed; Defeated is a state.

## 10. Soft-lock prevention

| Failure | Prevention |
|---|---|
| Glyph used but the boss never becomes Exposed | `RequestExpose` is the only path. It validates and immediately calls `SetBossState(Exposed)` in the same call. The glyph is marked used **only if** the request succeeds |
| Boss dies outside Defeated | Health changes only inside `HandleIncomingHit` (Exposed only). Health ≤ 0 → `SetBossState(Defeated)` in the same call. The donor death path is disabled or overridden |
| Boss stuck in recovery | Every recovery is a timer/sequence that always ends in `ReturnToCombatIdle()`. A watchdog forces Combat-idle if an attack sequence exceeds 6 s |
| All glyphs disabled forever | Glyph `bUsedThisCycle` is reset at every Staggered → Combat and in `ResetEncounter`. `bEnabled` is derived from the boss state, not latched |
| Player respawns but the boss stays active | `OnPlayerRespawned` → `ResetEncounter()`. The generation token kills any pending timer or sequence |
| Boss AI running while Exposed | Every `SetBossState` stops or starts the AI. The invariant check logs an error if the AI is running outside Combat |
| Chest stays vulnerable after leaving Exposed | `SetBossState` closes the seal on **every** exit from Exposed. Damage gating reads the state, not the seal |
| Entrance stays locked after defeat | Defeated → slab lowers (deterministic). Reset → slab set to its open transform directly |
| Duplicate boss instances | The boss is level-placed once and never spawned or destroyed. Bindings happen once in BeginPlay, guarded by `bBound` |
| Boss falls outside the arena | The arena is enclosed and locked during the fight. If the boss's Z < −500 → watchdog teleports it to the Center marker |
| Player trapped behind the gate | The slab only rises when ArenaEnter is overlapped (≥ 150 cm past it) and the player is verified inside (Y > 8600). Reset and defeat lower it |

## 11. Out of scope (this week)

Multiple phases or forms, a posture system, a stolen-name status, lock-on, Sequencer intro, final art/VFX/audio, arena hazards, more attacks, and Glyph-count escalation (only if playtests show the fight is too easy).
