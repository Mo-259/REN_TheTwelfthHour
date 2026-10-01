# REN — MASTER LOCAL EXECUTION ORDER (the one file to follow)

For: the user + **local** Claude Code with Unreal MCP, on the machine that runs Unreal Editor 5.8.
Purpose: execute and ship the vertical slice **in order**, without losing track of state. This file only sequences the work; the detailed steps live in the task files it links. **Do not skip ahead.**

## Ground rules (apply to every phase)

1. **Cloud specs are not implementation.** A phase is DONE only when its local PIE acceptance passes in Unreal and is committed. Until then the task board says `LOCAL_VALIDATION_REQUIRED`.
2. **One phase at a time.** Finish, validate and commit a phase before starting the next.
3. **Before every major local mutation:** `git status` must be **clean**. If it isn't, make a checkpoint commit first (`chore: checkpoint before <phase>`).
4. **After each verified milestone:** commit and push (suggested messages below). **Never commit a broken milestone as completed.** If you must save partial work, commit it as `wip: <phase> — NOT VALIDATED` and keep the board status `IN_PROGRESS`.
5. **No destructive Git:** no `reset --hard`, `clean -fd`, force push, history rewrite, `git lfs migrate` or `git add --renormalize`.
6. **Serialized MCP:** inspect → edit → compile → save → inspect → PIE. Never overlap editor mutations.
7. **World-lock:** builders and world-lock scripts run on **standalone-opened sublevels** (`L_Tomb_Blockout`, `L_Necropolis_Blockout`, `L_GateWest_Blockout`), never inside `L_REN_Slice`. Any unexplained CHANGED/MISSING = **stop**.
8. **Never edit** `/Game/Variant_Combat/` or other template assets.
9. **Visual references:** read `ProjectDocs/References/REFERENCE_MANIFEST.md` before any art work. As of 2026-10-01 it is **not in the repo**, so every character visual is `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`. No phase below *requires* reference masters.
10. **On any STOP:** don't improvise. Commit only safe work (as `wip`), write the STOP reason in `docs/DEVLOG.md`, push, and report it. A cloud session can review the pushed reports.
11. **After every phase:** update `docs/CURRENT_PROJECT_STATE.md` (verified facts only), `docs/TASK_BOARD.md` and `docs/DEVLOG.md`.

## Phase overview

| # | Phase | Task file(s) | Sprint day | Timebox | References needed |
|---|---|---|---|---|---|
| 0 | Pre-flight | this file §0, `docs/LOCAL_MCP_HANDOFF.md` | Day 1 (start) | ≤ 1 h | No |
| 1 | Interaction, donor audit, Tomb baseline | `docs/tasks/P1_INTERACTION_FOUNDATION.md` | Day 1 | ≈ 1 day | No |
| 2 | Tomb beats | `docs/tasks/P2_TOMB_BEATS.md` | Day 2 | ≈ 4 h + ≤ 1.5 h cuttable | No |
| 3 | Necropolis + Anubis | `docs/tasks/P2_NECROPOLIS_ANUBIS.md` | Day 3 | ≈ 1 day | No (Anubis stays a placeholder) |
| 4 | Gate of the West greybox | `docs/tasks/P3_GATE_WEST.md` | Day 4 (AM) | ≈ 2–2.5 h | No |
| 5 | First combat | `docs/tasks/P3_FIRST_COMBAT.md` (+ `docs/IMPLEMENTATION_P3_COMBAT.md`) | Day 4 (PM) | ≈ 4–5 h | No |
| 6 | Face-Eater | `docs/tasks/P4_FACE_EATER.md` (+ spec, implementation, `docs/QA_FACE_EATER.md`) | Day 5 | ≈ 1 day | No (boss stays a placeholder) |
| 7 | Polish + end-of-slice beat | `docs/tasks/P5_POLISH_AND_SHIP.md` | Day 6 | ≈ 1 day | Only for optional visual polish |
| 8 | Freeze + full QA | `docs/tasks/P5_POLISH_AND_SHIP.md` §QA, `docs/QA_ACCEPTANCE.md`, `docs/QA_FACE_EATER.md`, `docs/BUG_TRIAGE.md` | Day 7 (AM) | ≈ 3–4 h | No |
| 9 | Package build | `docs/BUILD_RELEASE_CHECKLIST.md` | Day 7 (PM) | ≈ 2–3 h | No |

Supporting docs: `docs/PERFORMANCE_AND_POLISH_BUDGET.md` (profiling in phases 7–9), `docs/BUG_TRIAGE.md` (from phase 1 onward).

---

## §0 Pre-flight

- **Prerequisites:** Windows machine with UE 5.8; Git and **Git LFS**; the repo cloned.
- **Do:**
  1. `git lfs install` (once per machine).
  2. `git pull`, then `git lfs pull`.
  3. Open `REN_TheTwelfthHour.uproject` and let shaders compile.
  4. Check that the Python Editor Script Plugin is enabled (P0-09).
  5. Configure Unreal MCP (`docs/LOCAL_MCP_HANDOFF.md`).
  6. Start local Claude from the project root.
  7. Run `python -m unittest discover -s Scripts/Tests`.
- **STOP if:** the project fails to open; `.uasset`/`.umap` files are LFS pointer text (run `git lfs pull` first); tests fail; MCP can't connect after the handoff steps (you can continue manually in the Editor, but log it).
- **Expected output:** the project opens; tests pass; MCP is connected (or a logged manual mode).
- **PIE acceptance:** none.
- **World-lock:** none.
- **Commit:** none (no changes). If MCP config files were generated, confirm they're appropriate to commit before committing.

## §1 Interaction foundation, donor audit, Tomb baseline — `P1_INTERACTION_FOUNDATION.md`

- **Prerequisites:** §0 done.
- **Order inside the task:**
  1. Donor audit (written to `docs/audits/VARIANT_COMBAT_DONOR_AUDIT.md`, including the D1 class-dependency questions).
  2. Tomb orientation check.
  3. Floating-prop procedure (P0-17).
  4. Traversal check.
  5. **Then** the first official Tomb baseline.
  6. Then the interaction work (Nefer, input, `BPI_Interactable`, trace, prompt, subtitle, Cartouche, Exit Door).
- **STOP conditions:** as listed in the task, including:
  - an orientation verdict of UNEXPECTED / NOT_FOUND / DUPLICATE
  - sarcophagus separation unclear
  - a donor contradicting the spec
  - D1 requiring a child class when a duplicate already exists
- **Expected output:**
  - the audit file
  - `Reports/L_Tomb_Blockout.orientation_check.json`
  - the official `L_Tomb_Blockout.worldlock.json`
  - the REN player Blueprints and the interaction assets
- **PIE acceptance:** P1 §8 tests 1–10.
- **World-lock:**
  - Export the baseline **only after** orientation, props and traversal are confirmed.
  - After the interaction work, validate: only ADDED `REN_INT_*`. Promote the candidate.
- **Commits:**
  - `level: lock Tomb baseline after orientation/prop fixes`
  - `feat: implement REN interaction foundation`

## §2 Tomb beats — `P2_TOMB_BEATS.md`

- **Prerequisites:** §1 committed; the official Tomb baseline exists.
- **STOP conditions:**
  - the Tomb baseline is missing
  - no-shadow fails after the ray-tracing check
  - the trigger audit is unclear about reuse
  - unexplained drift
- **Expected output:**
  - `L_REN_Slice`
  - the Arabic subtitle font (or a logged English fallback)
  - wake, Cartouche, no-shadow (`ApplySheutState`), shadow clue, side clue, heavy door, gameplay-first reveal
  - light/exposure pass
  - nullable audio hooks
- **PIE acceptance:** P2 §11 tests 1–13, including the no-audio run and two timings.
- **World-lock:** validate the Tomb; only the expected ADDED actors. Promote.
- **Commit:** `feat: complete Tomb opening gameplay`

## §3 Necropolis + Anubis — `P2_NECROPOLIS_ANUBIS.md`

- **Prerequisites:** §2 committed.
- **STOP conditions:**
  - the builder refuses (report its message verbatim)
  - the Glyph slab can be bypassed and an invisible blocker isn't enough
  - Arabic rendering is broken
- **Expected output:**
  - `L_Necropolis_Blockout` (210 builder actors) added to the slice
  - Glyph mechanism, shadow tease, fall recovery
  - Anubis placeholder + encounter
- **PIE acceptance:** the task's §7 tests 1–12 (time from ledge to plaza 2.5–4.5 min).
- **World-lock:** **first Necropolis baseline** after the PIE pass. Validate the Tomb.
- **Commit:** `feat: build Vertical Necropolis traversal`

## §4 Gate of the West greybox — `P3_GATE_WEST.md`

- **Prerequisites:** §3 committed.
- **STOP conditions:**
  - the builder refuses
  - the Gate tag lookup fails
  - `REN_DistantGate` bounds differ from the spec
- **Expected output:**
  - `L_GateWest_Blockout` with **61** builder actors, including `REN_GW_ArenaGate_Slab` and `REN_GW_Trigger_ArenaEnter`
  - the Gate sinks at runtime
  - checkpoints
- **PIE acceptance:** the task's §5 tests 1–9.
- **World-lock:** **first GateWest baseline**. Validate the Tomb: `REN_DistantGate` should show property changes only.
- **Commit (checkpoint):** `level: build Gate of the West greybox`

## §5 First combat — `P3_FIRST_COMBAT.md`

- **Prerequisites:** §4 committed; donor audit complete.
- **STOP conditions:** D1 conflict; the donor AI is unusable and the fallback fails; any change under `Content/Variant_Combat/`.
- **Expected output:**
  - `BP_NamelessDead` (TEMP)
  - death → checkpoint restart
  - `BP_EncounterController`
  - camera checks recorded
  - dodge added or deferred (with the decision logged)
- **PIE acceptance:** the task's §8 tests 1–11 (restart ×3).
- **World-lock:** validate GateWest (only ADDED `REN_INT_GW_*`). Promote.
- **Commit:** `feat: add Gate of the West first combat`

## §6 Face-Eater — `P4_FACE_EATER.md`

- **Prerequisites:** §5 committed; `OnPlayerRespawned` restart working.
- **STOP conditions:** S1–S8 in the task, including:
  - the donor can't receive hits without editing templates
  - the entry slab can't close safely without pushing the pawn
  - restart failing twice
- **Expected output:**
  - `BP_FaceEater`, `E_FaceEaterState`, `E_FaceEaterAttack`, `BP_FaceEaterGlyph` ×4, `WBP_FaceEaterBossBar`
  - the F/R donor decision logged
- **PIE acceptance:** `docs/QA_FACE_EATER.md`, **all non-N/A cases**, including **E1–E6** (slab safety), **B1–B5** (bounds) and **R1–R7** (restart ×3).
- **World-lock:** validate all three sublevels. Promote GateWest.
- **Commit:** `feat: implement Face-Eater core encounter`

## §7 Polish + end-of-slice beat — `P5_POLISH_AND_SHIP.md` (Day 6)

- **Prerequisites:** §6 committed; the slice is completable end to end.
- **STOP conditions:** a polish change requires rebuilding a system → stop (log it as a bug instead); an art decision is required without a reference master → keep the placeholder.
- **Expected output:**
  - the bug list reduced per `docs/BUG_TRIAGE.md`
  - readability, camera, lighting and feedback passes
  - the end-of-slice reward beat + end card
  - the first performance captures
- **PIE acceptance:** P5 task checks; one full playthrough with no BLOCKER/HIGH.
- **World-lock:** validate all three. Any art mesh swap shows as an ASSET CHANGE (review it); there must be no spatial changes.
- **Commit:** `polish: vertical slice pass`

## §8 Feature freeze + full QA (Day 7 morning)

- **Freeze:** from now on only BLOCKER/HIGH fixes (`docs/BUG_TRIAGE.md`).
- **Do:** three full playthroughs (record times); `docs/QA_ACCEPTANCE.md`; `docs/QA_FACE_EATER.md` regression; restart tests; performance captures on a Standalone/packaged build.
- **STOP if:** a BLOCKER can't be fixed within the timebox → decide with the user: cut the feature (cut orders) or delay the build.
- **Commit:** `fix: <bug ids>` per fix; `docs: QA results for pre-alpha`.

## §9 Package build (Day 7 afternoon) — `BUILD_RELEASE_CHECKLIST.md`

- **Prerequisites:** §8 clean of BLOCKER/HIGH (or each one accepted by the user in writing in DEVLOG).
- **Expected output:** a Development Win64 package outside the repo; checklist completed; release notes with known issues.
- **Commit:** `build: prepare pre-alpha package` (docs/notes/reports only; **never commit the packaged build**).

---

## Status tracker (fill in locally; keep in sync with `docs/TASK_BOARD.md`)

| Phase | Status (TODO / IN_PROGRESS / STOP / DONE) | Commit | Date | Notes |
|---|---|---|---|---|
| 0 Pre-flight | TODO | | | |
| 1 Interaction / audit / Tomb baseline | TODO | | | |
| 2 Tomb beats | TODO | | | |
| 3 Necropolis + Anubis | TODO | | | |
| 4 Gate greybox | TODO | | | |
| 5 First combat | TODO | | | |
| 6 Face-Eater | TODO | | | |
| 7 Polish + end beat | TODO | | | |
| 8 Freeze + QA | TODO | | | |
| 9 Package | TODO | | | |

**If the schedule slips:** apply each task's cut order. **Never skip** a phase's PIE acceptance or world-lock step to save time. Quality beats duration: a shorter, solid slice ships; a broken longer one doesn't.
