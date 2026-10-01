# Local Task — P4 Face-Eater Boss (Sprint Day 5)

Execution: **local Unreal + MCP only.** Written in cloud; every step is LOCAL_VALIDATION_REQUIRED.
Read first:
- `docs/FACE_EATER_BOSS_SPEC.md` (design)
- `docs/IMPLEMENTATION_P4_FACE_EATER.md` (Blueprint structure)
- `docs/QA_FACE_EATER.md` (test matrix)
- `ProjectDocs/References/REFERENCE_MANIFEST.md` (visual rule: until a Face-Eater master exists, everything visual is `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`; do not design the boss's look)

Task-board: P4-02…P4-08. **Timebox: one workday (≈ 6.5 h core + ≤ 1.5 h cuttable).** No C++, no Sequencer, no final art, **never edit `/Game/Variant_Combat/`**.

Workflow for every step: **inspect → edit → compile → save → inspect → PIE.** One MCP mutation at a time.

## STOP conditions (stop and report; do not improvise)

- **S1:** Day-4 prerequisites are missing (Gate built, first combat working, `OnPlayerRespawned` restart working).
- **S2:** Neither donor option F nor R can receive player hits without editing template assets (implementation §2).
- **S3:** The donor AI cannot be prevented from attacking or changing behaviour on its own outside REN control (G2 = NO, *and* REN MoveTo locomotion also fails).
- **S4:** `REN_GW_ArenaGate_Slab` or `REN_GW_Trigger_ArenaEnter` is missing (the GW builder was run before the C-05 layout update). The fix is a **re-run of the GW builder only while no GW baseline exists**; otherwise report it, because adding them by hand needs approval.
- **S5:** Any world-lock CHANGED/MISSING appears in Tomb, Necropolis or GateWest after the work.
- **S6:** Restart test R3 fails twice after fixes.
- **S7:** A visual decision would be required (e.g. "what should the chest seal look like"). Use a placeholder and log the question instead.

## 0. Preconditions and audit (read-only) — 20 min

1. `git pull`; `git status` clean. Make a checkpoint commit. `python -m unittest discover -s Scripts/Tests` must pass.
2. Validate all three sublevels standalone with `REN_Validate_WorldLock.py`. Expected: PASS, or only the reviewed `REN_INT_*` additions.
3. Confirm the Day-4 results: `docs/audits/VARIANT_COMBAT_DONOR_AUDIT.md` (A1–A10, D1); the encounter restart; `BP_REN_GameMode.OnPlayerRespawned`; the player damage path; any dodge `bInvulnerable` variable. If any is missing → **S1**.
4. In `L_GateWest_Blockout`, confirm these exist: `REN_GW_Arena_GlyphPillar_01..04`, `REN_GW_Marker_FaceEater_Center_PLACEHOLDER`, `REN_GW_ArenaGate_Slab` (Movable, resting below the threshold), `REN_GW_Trigger_ArenaEnter`. If any is missing → **S4**.
5. **Donor gate G1–G4** (implementation §2): answer each from the audit plus a small PIE probe. For example, place a plain `Character` implementing `BPI_Damageable` that prints on damage, and hit it. Record the answers and **choose F or R** in `docs/audits/VARIANT_COMBAT_DONOR_AUDIT.md`. → **S2/S3** if blocked.

## 1. Assets and skeleton — 45 min

1. Create `/Game/REN/Gameplay/Bosses/FaceEater/`, then the enums `E_FaceEaterState` (exact order: Dormant, Intro, Combat, Exposed, Staggered, Defeated) and `E_FaceEaterAttack` (None, HookSweep, HeavyStrike, Grab).
2. Create `BP_FaceEater` per the chosen option (F: parent `Character` + implements `BPI_Damageable`; R: child/duplicate per D1, with donor tree logic **not** auto-starting).
   - Components per implementation §3, including the TEMP placeholder mesh and material, the editor-only TEMP TextRender, and the `ChestSeal` component.
   - All variables and dispatchers per §4.
3. Implement `SetBossState`, `DelayWithGen`, `CheckInvariants` and `StopAI`/`StartAI` (§5). Compile and save.
4. Place it in `L_GateWest_Blockout` at `REN_GW_Marker_FaceEater_Center_PLACEHOLDER` (0, 9550, ~190), facing −Y. Label `REN_INT_GW_FaceEater`. Set the instance refs (trigger, slab, markers). Save.
5. **PIE smoke test:** the boss stands Dormant and doesn't move or attack; hitting it does nothing; no log errors.

## 2. Encounter start and entry lock — 30 min

1. BeginPlay: capture `SlabOpenZ`. Bind ArenaEnter overlap and `GameMode.OnPlayerRespawned` → `ResetEncounter` (once, `bBound`).
2. ArenaEnter → raise the slab 640 over 1.5 s → `SetBossState(Intro)` → after 2 s, Combat.
3. Create `WBP_FaceEaterBossBar` (§8); show it in Intro and hide it in Dormant.
4. PIE: entering locks the arena, the bar appears, the boss turns toward the player, and Combat begins (locomotion only for now).

## 3. Attacks — 2 h (Grab: +40 min, cuttable)

1. Implement the scheduler and `ReturnToCombatIdle` (§5).
2. Implement **Heavy Strike**, then **Hook Sweep**, exactly per spec §4: timings, tracking lock, hit queries, damage fractions, knockback. Each must call `OpenGlyphWindow` at RecoveryStart and end via `ReturnToCombatIdle`.
3. Placeholder anticipation: stop, turn, and play a donor montage at reduced play-rate or hold a pose (TEMP). Enable the `bDebugTelegraphs` debug shapes.
4. Implement the watchdog.
5. PIE: attack timings feel readable; the first attack is always Heavy; there's no snap after the lock; each attack hits at most once; knockback works; no attacks happen outside Combat.
6. **Grab (cuttable):** implement only if steps 1–5 pass within budget; otherwise set `bEnableGrab = false` and log it as cut.

## 4. Damage gate, Exposed, Staggered, Defeated — 60 min

1. Route the player's hits → `HandleIncomingHit` (via `BPI_Damageable` or the option-R override). **Disable or override any donor health/death path** in the REN class (G3).
2. Combat deflect feedback (hit-stop, shake, nullable sound); the bar does not move.
3. Exposed: the seal opens (TEMP shape), the AI stops, no rotation, 4 s, 7 per hit, cap 35. Staggered 1.2 s, then a 1.0 s grace. Defeated: everything stops, the bar fades, the slab lowers, `OnBossDefeated` fires, TEMP subtitle.
4. PIE: Exposed reached via the console or debug only for now (temporary debug key; **remove it before hand-back**).

## 5. Glyph pillars — 45 min

1. Create `BP_FaceEaterGlyph` (implementation §7). Place 4 instances over `REN_GW_Arena_GlyphPillar_01..04`: labels `REN_INT_GW_FaceEaterGlyph_01..04`, `GlyphIndex` 1–4, `BossRef` = the boss, `PillarActor` = the matching pillar. Add them to the boss's `Glyphs` array.
2. PIE:
   - the prompt appears **only** during a recovery window
   - one interaction → Exposed
   - an invalid press is not consumed
   - all pillars reset after Staggered
3. Remove the step-4 debug key.

## 6. Reset — 45 min (non-negotiable)

1. Implement `ResetEncounter()` exactly per implementation §6, including the generation increment, the instant slab reset, glyph `ResetAll`, the boss teleport and hiding the bar.
2. Confirm the arena checkpoint: `REN_INT_GW_Checkpoint_ArenaApproach` → `REN_GW_Respawn_ArenaApproach`.
3. Run QA **R1–R6** (`docs/QA_FACE_EATER.md`), including **restart ×3** (and ×3 again mid-attack and mid-Exposed). → **S6** if R3 fails twice.

## 7. Hint, camera, polish of readability — 30 min (cuttable items marked)

1. The one-time hint (cuttable).
2. Camera checks per QA C1–C4. Optional arm +≤100 cm in the encounter; restore it on reset and defeat; record the values.
3. Tune only `ExposedHitDamage`, `CycleDamageCap`, `ExposedDuration` and the attack timings. Target 3–5 exposure cycles for a first-timer. Record the final numbers.

## 8. Full QA and validation — 60 min

1. Run all of `docs/QA_FACE_EATER.md` and record PASS/FAIL per ID.
2. World-lock: validate Tomb, Necropolis and GateWest standalone. Expected: only ADDED `REN_INT_GW_*` in GateWest; no CHANGED/MISSING → else **S5**. Promote the GW candidate if it's clean.
3. Git: **no changes under `Content/Variant_Combat/`**.
4. Commit the assets (LFS), audit updates, validation reports, and docs (CURRENT_PROJECT_STATE, TASK_BOARD, DEVLOG).
5. The report must include:
   - the F/R choice and G1–G4 answers
   - the QA table
   - the final tuning numbers
   - the measured fight time and number of cycles (2 runs)
   - what was cut
   - screenshots: the seal open, a debug telegraph of each attack, the boss bar

## Cut order (cut from the top)

1. Grab (`bEnableGrab = false`)
2. Intro walk-out from the recess (already the default: start at Center)
3. One-time hint
4. Camera arm tweak
5. Glyph material-state hook (the prompt alone signals the window)
6. Deflect sound and shake (keep the hit-stop)

**Never cut:**
- the state machine as the sole authority
- Heavy Strike + Hook Sweep
- the explicit glyph window
- 1-glyph → Exposed → damage
- 0-damage Combat with deflect hit-stop
- Defeated → slab lowers
- `ResetEncounter` with restart ×3
- the soft-lock protections (generation token, watchdog, invariants)
- the QA matrix
