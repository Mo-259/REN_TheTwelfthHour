# Local Task — P5 Polish, End-of-Slice Beat and Ship (Sprint Days 6–7)

Execution: **local Unreal + MCP only.** Written in cloud; every step is LOCAL_VALIDATION_REQUIRED.
Order: `docs/tasks/MASTER_LOCAL_EXECUTION_ORDER.md` §7–§9. Supporting docs: `docs/BUG_TRIAGE.md`, `docs/PERFORMANCE_AND_POLISH_BUDGET.md`, `docs/BUILD_RELEASE_CHECKLIST.md`.

**This is NOT an unlimited art pass.**
- Don't rebuild systems during polish. If something needs a rebuild, log it as a bug and stop.
- Feature freeze happens before final QA (Day 7 midday).
- No C++, no Sequencer, never edit template assets. World-locked geometry doesn't move.

Visual rule: read `ProjectDocs/References/REFERENCE_MANIFEST.md` first. Without a master for a subject, keep its placeholder (`TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`). Art mesh swaps are only allowed at identical transforms (world-lock reports an ASSET CHANGE).

Workflow: **inspect → edit → compile → save → inspect → PIE**, with a checkpoint commit before each block.

## Priority order (work strictly top-down; timeboxes from the performance and polish budget §6)

1. **Gameplay bugs:** all BLOCKER, then HIGH (`docs/BUG_TRIAGE.md`).
2. **Combat readability:**
   - Nameless Dead wind-ups are readable
   - Face-Eater placeholder pose and debug telegraph agree with the damage window (QA A11)
   - Exposed state is unmistakable
3. **Camera:**
   - Tomb corridor and shadow lane
   - court
   - arena framing of the 3.8 m boss; the optional arm tweak per the P4 implementation §9
   - no wall snapping
4. **Lighting and readability:**
   - floor, path, doors, props and Nefer's silhouette readable everywhere
   - no crushed blacks
   - exposure is stable
   - the no-shadow clue still reads
5. **Hit feedback:** hit-stop, restrained shake, deflect versus real-damage contrast on the boss.
6. **Essential audio, only if assets already exist locally.** Assign them to the nullable hooks; never source or import during this task unless the user provides the files.
7. **Visual polish, only with reference masters.** Otherwise skip it.

After each block: a short PIE regression of the affected area, then world-lock validation if any level actor was touched.

## End-of-slice reward beat (required; placeholder presentation)

Purpose: clearly communicate **VERTICAL SLICE COMPLETE** after the Face-Eater is defeated. No loot screen, inventory or skill tree. No floating runes or glowing magic circles.

**Assets** (minimal):
- `/Game/REN/UI/WBP_EndCard`, the only new widget
- logic added to `BP_REN_GameMode`
- no new framework

**Flow:**
1. `BP_FaceEater` entering **Defeated** (P4) already does: combat ends, the entry slab lowers (exit unlocked), the boss bar fades. Add a call to `BP_REN_GameMode.BeginSliceEnd()` (cast the GameMode).
2. `BeginSliceEnd()`:
   - Guard with `bSliceEnded` (once only).
   - **Player control stays enabled.** Don't disable input yet.
3. After 1.5 s, the **reward beat** (Ren Glyph / recovered name), using placeholder presentation built only from existing language:
   - TEMP subtitle lines (editable script, not canon wording), Arabic primary + English, for example English: *"…a name, given back."* then *"Ren Glyph recovered."*
   - Optional: drive the existing Glyph pillars' material hook to their "ink-filled" state. Physical and semantic: carved grooves, ink; no floating symbols.
   - Optional: a nullable sound hook.
4. After about 6 s from defeat: create `WBP_EndCard` and fade it in over 1.0 s. Text:
   - `REN — THE TWELFTH HOUR`
   - `VERTICAL SLICE COMPLETE`
   - `Pre-alpha · greybox and placeholder characters (not visual authority)`
   - measured run time (optional)
   - buttons **Restart** (`OpenLevel L_REN_Slice`) and **Quit** (`QuitGame`)
5. When the end card shows: input mode UI only, cursor visible, gamepad focus on Restart.
6. Player death after defeat can't occur in an enclosed, cleared arena. If it ever happens, the boss stays Defeated (P4 reset rule).

**Checks:**
- The beat fires exactly once.
- Control remains until the card appears.
- Restart starts at the Tomb cleanly.
- Quit exits.
- No debug text.
- Arabic renders correctly.

## Day 6 — polish (≈ 1 day)

1. Checkpoint commit. Triage all known bugs.
2. Work the priority list with the timeboxes. Implement the end-of-slice beat (≈ 1 h; it's required).
3. First performance captures (Standalone): P-T2, P-N1, P-C1, P-F1. Act only per the performance priority order.
4. One full playthrough. Log bugs.
5. Validate world-lock for all three sublevels and commit `polish: vertical slice pass`.

## Day 7 — freeze, QA, ship

1. **Feature freeze (by midday):** from here on, only BLOCKER/HIGH fixes, each with its own commit (`fix: BUG-0xx …`).
2. **Full QA:**
   - `docs/QA_ACCEPTANCE.md` (greybox, interaction, no-shadow, door, boss, continuity, cinematic, performance)
   - `docs/QA_FACE_EATER.md` regression (at minimum S*, D*, R*, E*, B*, H*)
   - **three full playthroughs** with recorded times
   - restart tests in combat and the boss fight
3. Performance capture on the packaged build per `docs/PERFORMANCE_AND_POLISH_BUDGET.md`.
4. **Package:** follow `docs/BUILD_RELEASE_CHECKLIST.md` completely.
5. Commit `build: prepare pre-alpha package` (docs, reports and notes only). Update CURRENT_PROJECT_STATE, TASK_BOARD and DEVLOG with verified results.

## STOP conditions

- A fix would require a system rewrite or new mechanic → stop and log it (the post-slice backlog).
- A fix would move world-locked geometry → stop and ask the user.
- An art decision is needed without a reference master → keep the placeholder and log the question.
- A BLOCKER is unresolved at the Day-7 cutoff → decide with the user: cut the feature (per the task cut orders) or delay the build. **Never ship a known BLOCKER silently.**

## Cut order (polish; from the top)

1. Visual polish
2. Optional audio
3. Pillar ink-fill on the reward beat
4. Camera arm tweak
5. Lighting beyond readability

**Never cut:** BLOCKER/HIGH fixes, the end-of-slice beat (subtitle + end card), full QA, and the build checklist.
