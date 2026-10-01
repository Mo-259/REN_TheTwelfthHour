# REN — P4 Face-Eater: Implementation Design (Blueprint only)

Status: cloud static design, 2026-10-01; **revision 2** (no hidden cap, animation-sync rule, slab safety, movement bounds). Not PIE-tested. Design source: `docs/FACE_EATER_BOSS_SPEC.md`. Local task: `docs/tasks/P4_FACE_EATER.md`.
No C++, no Sequencer, no final art. Visuals are `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.

## 1. Assets (no framework explosion)

`/Game/REN/Gameplay/Bosses/FaceEater/`:

| Asset | Purpose |
|---|---|
| `E_FaceEaterState` | Dormant, Intro, Combat, Exposed, Staggered, Defeated |
| `E_FaceEaterAttack` | None, HookSweep, HeavyStrike, Grab. One small enum, for scheduling and debug |
| `BP_FaceEater` | The boss **and** the encounter orchestration (state machine, attacks, damage gate, glyph registry, entry slab, reset) |
| `BP_FaceEaterGlyph` | One logic for all four pillars (`BPI_Interactable`) |
| `WBP_FaceEaterBossBar` | Name + one health bar |

No separate encounter controller, attack classes or data assets. Placeholder visuals are a REN material instance and simple shapes, labelled TEMP.

## 2. Donor integration decision gate (decided LOCALLY from the audit; not decided here)

Inputs: `docs/audits/VARIANT_COMBAT_DONOR_AUDIT.md` answers A1–A10 (`docs/IMPLEMENTATION_P3_COMBAT.md`) and the outcome of the Day-4 first combat.

| Question (from the audit / Day 4) | If YES | If NO |
|---|---|---|
| G1: Does the player's attack reach any actor implementing `BPI_Damageable` (an interface call on the hit actor), independent of the actor's class? | `BP_FaceEater` can be a plain Character implementing `BPI_Damageable` (option F) | The player's hit path needs donor class membership → option R (child/duplicate of `BP_CombatEnemy`, per D1) |
| G2: Can the donor StateTree / AI be prevented from attacking on its own (logic not started, or a REN duplicate tree containing only approach/face tasks)? | R is allowed: reuse the donor capsule, movement, AI controller and the approach part of the tree in Combat only | Use REN locomotion (F-style MoveTo) even inside option R |
| G3: Does the donor enemy have its own death/health path that could fire independently? | Disable or override it in the REN class (never edit the template). Health lives only in `BP_FaceEater` | — |
| G4: Does the donor provide a hit component or bone on damage? | Optional upgrade: restrict Exposed damage to a `ChestSeal` hit-box | Any hit during Exposed counts (default) |

- **Option F (minimal fallback, recommended unless G1 = NO):** parent `Character`, default `AIController`. Combat locomotion: `AI MoveTo(Player, AcceptanceRadius 300)` re-issued every 0.5 s while idle, plus RInterp facing. Implements `BPI_Damageable` (the donor interface is **referenced**, not duplicated) → forwards to `HandleIncomingHit`.
- **Option R (reuse):** a child or duplicate of `BP_CombatEnemy` (per D1). The StateTree logic **never starts automatically**. In Combat, only approach/face runs (a REN duplicate `ST_FaceEater` if the donor tree contains attacks). All donor attack tasks are unreachable. Phase, attacks and damage are REN-owned exactly as below.
- **Either way:** the REN state machine is the only phase authority; attacks are REN-scripted; health is REN-owned.

**STOP condition:** if neither F nor R can receive player hits without editing template assets → stop and report.

## 3. `BP_FaceEater` — components (TEMP_PLACEHOLDER visuals)

- Capsule: radius **90**, half-height **190** (≈ 3.8 m). CharacterMovement max walk 300 cm/s.
- Mesh: mannequin scaled to about 2.1 (TEMP) with a REN placeholder material instance (not grey, no emissive). Editor-only TextRender `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY` (Hidden in Game).
- `ChestSeal`: a StaticMesh (engine shape) at chest height (≈ Z +70 relative to the capsule centre), with `SealClosedRelative` / `SealOpenRelative` transforms (e.g. a 70° hinge or a 30 cm outward translation). No collision needed for the prototype. TEMP.
- Optional `ChestSealHitbox` (Sphere r 60, overlap only), used only if G4 = YES.
- No staff collision. Hits are queries (§5).

## 4. `BP_FaceEater` — variables

| Variable | Type | Default |
|---|---|---|
| `State` | `E_FaceEaterState` | Dormant |
| `CurrentAttack` | `E_FaceEaterAttack` | None |
| `Health` / `MaxHealth` | Float | 100 / 100 |
| `ExposedHitDamage` | Float | 7 (tune 6–8). **No per-cycle cap variable** (spec §6) |
| `IntroDuration`, `ExposedDuration`, `StaggerDuration`, `PostStaggerGrace`, `IdleGap` | Float | 2.0, 4.0, 1.2, 1.0, 0.8 |
| `bGlyphWindowOpen` | Bool | false |
| `Generation` | Int | 0 (incremented on every reset and every state change) |
| `AttackCountSinceHeavy`, `ConsecutiveSweeps`, `AttacksSinceGrab`, `bFirstAttackDone` | Int/Int/Int/Bool | 0, 0, 99, false |
| `bEnableGrab` | Bool | true (cut → false) |
| `DeflectCount`, `WindowsWithoutGlyph`, `bHintShown` | Int/Int/Bool | 0, 0, false |
| `Glyphs` | `BP_FaceEaterGlyph` array (instance-editable) | 4 pillar glyph instances |
| `ArenaEnterTrigger`, `ArenaGateSlab`, `DormantMarker`, `CenterMarker` | Actor refs (instance-editable) | `REN_GW_Trigger_ArenaEnter`, `REN_GW_ArenaGate_Slab`, `REN_GW_Marker_FaceEater_Center_PLACEHOLDER` (both markers) |
| `SlabOpenZ` / `SlabRise` | Float | captured at BeginPlay / 640 |
| `SlabSafetyTries`, `SlabSafetyMaxTries`, `SlabSafetyInterval` | Int/Int/Float | 0, 10, 0.1 |
| `SlabClosureMin` / `SlabClosureMax` | Vector | (−360, 8390, 0) / (360, 8610, 600): the slab's raised footprint + 60 cm horizontal margin |
| `ArenaCenter` | Actor ref | `REN_GW_Marker_FaceEater_Center_PLACEHOLDER` |
| `BoundsMainMin` / `BoundsMainMax` | Vector2D | (−1000, 8850) / (1000, 10350) |
| `BoundsMouthMin` / `BoundsMouthMax` | Vector2D | (−200, 10350) / (200, 10550) |
| `bReturningToBounds`, `OutOfBoundsTime` | Bool / Float | false / 0 |
| `bEncounterArmed`, `bBound` | Bool | true, false |
| `AttackStartTime` | Float | for the watchdog |
| `bDebugTelegraphs`, `bDebugState` | Bool | true (pre-alpha), false |
| Sounds | Sound refs, all **nullable** | None |

Dispatchers: `OnBossStateChanged(NewState)`, `OnGlyphWindowChanged(bOpen)`, `OnBossDefeated`.

## 5. Functions and flows

**`SetBossState(NewState)`** is the only writer of `State`:
1. Return if `State == Defeated`.
2. `Generation++` (invalidates any pending sequence from the old state).
3. Exit actions for the old state:
   - leaving Exposed → close the seal (lerp 0.25 s, or instant on reset)
   - always → `CloseGlyphWindow()` and `CurrentAttack = None`
4. Set `State`.
5. Entry actions:
   - **Dormant:** StopAI, hide the bar.
   - **Intro:** StopAI, show the bar (fade). `DelayWithGen(IntroDuration)` → `SetBossState(Combat)`.
   - **Combat:** StartAI (locomotion only; the move target is always `ClampToBounds(PlayerLocation)`). Set `bFirstAttackDone` handling. Schedule the first decision after `PostStaggerGrace` (or immediately after Intro).
   - **Exposed:** StopAI and stop movement (`StopMovementImmediately`), disable rotation (`bUseControllerDesiredRotation` / `OrientRotationToMovement` off). Open the seal (0.25 s). `DelayWithGen(ExposedDuration)` → `SetBossState(Staggered)`.
   - **Staggered:** StopAI. Close the seal. `DelayWithGen(StaggerDuration)` → for each glyph `ResetCycle()` → `SetBossState(Combat)`.
   - **Defeated:** StopAI permanently. Close the window, disable all glyphs, fade the bar. Lower the entry slab (Timeline 1.5 s). Broadcast `OnBossDefeated`. TEMP subtitle.
6. Broadcast `OnBossStateChanged`. Run `CheckInvariants()`.

**`DelayWithGen(Seconds) → then`:** capture `G = Generation`; after the delay (or a timer), **continue only if `Generation == G` and `State` is as expected.** This is the single mechanism that kills stale timers, attack sequences and the Exposed/Stagger timers after a state change or reset. Avoid raw `Delay` nodes elsewhere.

**Movement bounds** (spec §4a):
- `IsInBounds(P, Margin=0)` → P (2D) inside `BoundsMain` or `BoundsMouth` (shrunk by `Margin`).
- `ClampToBounds(P)` → the nearest point inside the bounds.
- Every Combat locomotion tick (0.5 s re-issue): if `!IsInBounds(BossLoc, 25)` → `bReturningToBounds = true` → `AI MoveTo(ClampToBounds(BossLoc) pushed 100 cm toward ArenaCenter)`; on arrival or once back in bounds with the 25 cm margin → `bReturningToBounds = false`. Otherwise MoveTo `ClampToBounds(PlayerLoc)` (acceptance 300).
- **Never teleport** in normal Combat. The watchdog alone may teleport (emergency).

**Attack scheduler** (`DecideNextAttack`, runs while `State == Combat AND CurrentAttack == None`, every 0.25 s via `DelayWithGen`):
0. **Guard:** if `bReturningToBounds` or `!IsInBounds(BossLoc)` → skip (no attack selection), re-schedule.
1. `Dist` = 2D distance to the player; `Angle` = angle to the player relative to the boss's facing.
2. Rules in order (spec §4):
   - `!bFirstAttackDone` → Heavy
   - `AttackCountSinceHeavy ≥ 2` and `Dist ≤ 650` → Heavy
   - Grab conditions
   - Sweep/Heavy by distance
   - `ConsecutiveSweeps ≥ 2` → Heavy
   - `Dist > 650` → keep approaching (AI)
3. `StartAttack(Type)`: re-check `IsInBounds(BossLoc)` (return if false), then `CurrentAttack = Type`, `AttackStartTime = now`, **pause AI movement**, then run the attack sequence.

**Attack sequence** (one function per attack, all built with `DelayWithGen`):
```
Anticipation: track toward player (rate limit) for T_track; then lock facing for T_lock
  (optional DrawDebug telegraph if bDebugTelegraphs)
Active: at scripted offsets run HitQuery (arc / circle / sphere) → if hit && !bHitThisAttack → ApplyBossHitToPlayer(frac, knockback)
RecoveryStart: if attack grants a window → OpenGlyphWindow(WindowDuration)
Recovery: wait T_recovery (window closes itself at its own timer, never after recovery end)
End: CloseGlyphWindow(); if window opened and unused → WindowsWithoutGlyph++ → maybe hint
     ReturnToCombatIdle()
```

**`ReturnToCombatIdle()`:** `CurrentAttack = None`, update the counters, resume AI movement, `DelayWithGen(IdleGap)` → `DecideNextAttack`.

**`OpenGlyphWindow(D)` / `CloseGlyphWindow()`:** set `bGlyphWindowOpen` and broadcast `OnGlyphWindowChanged`. Open also does `DelayWithGen(D)` → Close.

**`RequestExpose(GlyphIndex) → bool`:** if `State == Combat AND bGlyphWindowOpen AND CurrentAttack != None (in recovery)` → `WindowsWithoutGlyph = 0`, `SetBossState(Exposed)`, return true. Otherwise return false (nothing consumed).

**`HandleIncomingHit(Instigator)`** is the only path that changes Health:
- **Exposed:** `Health −= ExposedHitDamage` (clamped at 0), update the bar **on every valid hit** (no hidden cap). If `Health ≤ 0` → `SetBossState(Defeated)`. (If a cap is ever approved: on reaching it, call `SetBossState(Staggered)` immediately so the seal visibly closes. Never silently reject hits while the seal is open.)
- **Combat:** deflect feedback (player `CustomTimeDilation` 0.05 s, small camera shake, nullable sound), `DeflectCount++` → maybe hint.
- **Other states:** ignore.

**`ApplyBossHitToPlayer(Fraction, KnockXY, KnockZ, InputLockSeconds)`:**
- Guards: player valid, not dead, `State == Combat`, and `bInvulnerable` (if a dodge exists) is false.
- Damage = `Fraction × Player.MaxHealth` through the **player's existing damage path** (the donor `BPI_Damageable`, or the REN fallback from P3).
- Launch the character; optionally disable input briefly.

**Active-window timing.** For the TEMP placeholder, the attack sequence's scripted timings drive Anticipation → Active → Recovery, and the placeholder pose/montage must be timed to show the strike inside the Active window (the visual and the damage agree).
- **Future (approved animation):** add an Anim Notify / Notify State / montage event `FE_ActiveBegin` (and optionally `FE_ActiveEnd`) on the attack montage.
- The sequence then waits for `FE_ActiveBegin` instead of the scripted Active offset, accepting it **only** if it matches `CurrentAttack` and the captured `Generation`.
- The scripted offset remains as a timeout fallback (e.g. scripted time + 0.3 s), so a missing notify can't stall the attack.
- The state machine remains the authority. The target offset between visible impact and damage is ≤ ~0.1 s.

**Hit queries** (geometric, no physics), on 2D positions:
- Sweep: `Dist ≤ 420` and `|Angle| ≤ 80°` and `|Zdiff| < 250`.
- Heavy: `Distance(Player, BossLoc + Fwd·400) ≤ 220 + 42`.
- Grab: `Distance(Player, BossLoc + Fwd·250) ≤ 150 + 42` and `|Angle| ≤ 45°`.

**Hint:** `if !bHintShown && (DeflectCount ≥ 6 || WindowsWithoutGlyph ≥ 2)` → `ShowSubtitle(TEMP line, 3.5 s)`, `bHintShown = true`.

**Watchdog** (looping 0.5 s timer, independent of the generation token; **emergency recovery only**):
- If `CurrentAttack != None` and `now − AttackStartTime > 6 s` → log an error and `ReturnToCombatIdle()`.
- `OutOfBoundsTime` accumulates while `!IsInBounds(BossLoc)` (reset when back in bounds). If it exceeds **5 s**, or the boss's Z < −500 → log an error and teleport to `ArenaCenter`. This never happens in normal play; walking back to the bounds is the normal path.

**`CheckInvariants()`** (logs errors only; never changes state):
- Not Combat ⇒ AI stopped and `bGlyphWindowOpen == false`.
- Not Exposed ⇒ the seal is closed or closing.
- Defeated ⇒ Health ≤ 0 and the slab is not raised.

## 6. `ResetEncounter()` (bound to `BP_REN_GameMode.OnPlayerRespawned`, once, in BeginPlay)

```
if State == Defeated: ensure slab open; return            // never resurrect
Generation++                                              // kills all DelayWithGen chains
StopAI(); StopMovementImmediately()
CurrentAttack = None; bGlyphWindowOpen = false; broadcast OnGlyphWindowChanged(false)
State = Dormant (direct assignment inside reset; then OnBossStateChanged)
Health = MaxHealth; counters reset; bFirstAttackDone = false; bReturningToBounds = false; OutOfBoundsTime = 0
ChestSeal → SealClosedRelative (instant)
SetActorLocationAndRotation(DormantMarker, Teleport) ; velocity = 0
for g in Glyphs: g.ResetAll()                             // bUsedThisCycle=false, material default
stop slab Timeline + clear the slab safety retry; ArenaGateSlab → Z = SlabOpenZ (instant); SlabSafetyTries = 0
Boss bar hidden
bEncounterArmed = true
CheckInvariants()
```

- **No temporary actors exist by design** (hits are queries; telegraphs are debug draws), so none can linger.
- **Bindings** (`ArenaEnterTrigger.OnActorBeginOverlap`, `GameMode.OnPlayerRespawned`) are made once in BeginPlay, guarded by `bBound`, so there are never duplicate bindings.

**ArenaEnter overlap → safe closure** (spec §9; never push, launch or trap the pawn):
1. If `bEncounterArmed AND State == Dormant AND Player.Y > 8600` → `bEncounterArmed = false`, `SlabSafetyTries = 0`, `TryCloseSlab()`.
2. `TryCloseSlab()`: `if PlayerCapsuleOverlapsBox(SlabClosureMin, SlabClosureMax)` (capsule AABB vs box; include Z so jumping counts):
   - `SlabSafetyTries++`. If `< SlabSafetyMaxTries` → `DelayWithGen(SlabSafetyInterval)` → `TryCloseSlab()`.
   - Otherwise → **log a warning**, leave the slab open, stay **Dormant**, `bEncounterArmed = true` (re-armed), return.
3. If clear → play `TL_SlabRise` (1.5 s, `+SlabRise`, **no sweep**). On **each Timeline update**: if the player overlaps the closure box → **Reverse** the Timeline (lower back to open). When it is fully open again: stay Dormant, re-arm, log a warning.
4. On `TL_SlabRise` Finished (fully closed) → `SetBossState(Intro)`.
5. Defeated → `TL_SlabRise` reverse/lower (exit open). Reset → instant open (§6).

## 7. `BP_FaceEaterGlyph` (`BPI_Interactable`)

Variables:
- `BossRef` (`BP_FaceEater`, instance-editable)
- `bEnabled` (default true)
- `bUsedThisCycle`
- `GlyphIndex` (Int)
- `PillarActor` (Actor ref → `REN_GW_Arena_GlyphPillar_0N`)
- optional `ReceptiveParamName` (Name) for a material scalar on the pillar
- optional `ActivateSound` (nullable)

Components:
- a Box Collision about 160 × 160 × 300, **Visibility Block only**, placed over the pillar (Cartouche pattern)
- the pillar mesh stays the greybox actor

Functions:
- `CanInteract(Interactor)` → `IsValid(BossRef) AND bEnabled AND BossRef.State == Combat AND BossRef.bGlyphWindowOpen AND NOT bUsedThisCycle`
- `GetInteractionPrompt` → "Read" (TEMP)
- `Interact(Interactor)` → if `CanInteract` AND `BossRef.RequestExpose(GlyphIndex)` → `bUsedThisCycle = true`, nullable sound, optional material pulse. Else → nothing (not consumed).
- `ResetCycle()` → `bUsedThisCycle = false`
- `ResetAll()` → `ResetCycle()`, material default
- BeginPlay: bind `BossRef.OnGlyphWindowChanged` → set the material parameter (optional), **once**.

## 8. `WBP_FaceEaterBossBar`

- Name text "Face-Eater" (the canon name; style TEMP) and one ProgressBar (`Health / MaxHealth`).
- Created once by `BP_FaceEater` at BeginPlay, added to the viewport, hidden.
- Shown in Intro (fade 0.5 s), hidden on Dormant/reset, faded on Defeated.
- No phase markers, no numbers, no mechanic state.

## 9. Camera

- Donor camera (no redesign, no lock-on).
- Optional, measured: while the encounter is active, raise the spring-arm length by ≤ 100 cm so the 3.8 m boss stays in frame. Restore it on Defeated and Reset. Record the values.

## 10. Static self-review (2026-10-01)

| Concern | Result |
|---|---|
| Overengineering | Removed: separate encounter controller, attack data assets, posture, phases, lock-on, Sequencer. 5 small assets total |
| Systems not needed this week | Grab is cuttable (`bEnableGrab`); hint, intro walk-out and camera arm tweak are cuttable |
| Unclear feedback | Deflect + still bar (Combat); the prompt appears only when valid; the seal visibly opens; the bar drops only in Exposed; one hint |
| Mechanic repetition | Two attacks with distinct answers (sideways vs. backwards); first-attack-Heavy teaching; 3–5 cycles |
| Soft-lock risk | Single state writer, generation token, watchdog, invariants, deterministic slab, reset on respawn (spec §10) |
| Hidden dependency on final art | None for the **placeholder**: scripted timings drive the Active window. **Not** a permanent independence: once approved animations exist, the Active window must be synced to the visible impact via an Anim Notify / montage event (spec §4, QA A11/A12) |
| Hidden damage cap | Removed (rev 2). Every valid Exposed hit moves the bar |
| Hidden C++ dependency | None (Blueprint timers, Timelines, AI MoveTo, interfaces) |
| Hidden Sequencer dependency | None |
| Donor coupling | Isolated behind gate G1–G4; health, phase and attacks are REN-owned in both options |
