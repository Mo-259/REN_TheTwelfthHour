# Local Task — P3 Gate of the West Greybox (Sprint Day 4, part 1)

Execution: **local Unreal + MCP only.** Written in cloud; every step is LOCAL_VALIDATION_REQUIRED.
Design: `docs/GATE_WEST_GREYBOX_SPEC.md`. Builder: `Scripts/Editor/REN_GateWest_Greybox_Builder_v1.py`. Task-board: P4-01 (arena shell), P3-07 (space).
**Timebox: about 2–2.5 h.** No Face-Eater logic, no C++, no Sequencer. Template assets are never edited.

Serialize MCP calls: **inspect → edit → compile → save → inspect → PIE test.**

## 0. Preconditions and audit (read-only) — 15 min

1. `git pull`; `git status` must be clean. Make a checkpoint commit. `python -m unittest discover -s Scripts/Tests` must pass.
2. Required from Days 1–3:
   - `L_REN_Slice` with Tomb and Necropolis always loaded
   - Tomb and Necropolis baselines committed
   - the Anubis encounter working
   - `ShowSubtitle`
   - the interaction system
   If any is missing, **stop**.
3. Validate the Tomb and the Necropolis standalone with `REN_Validate_WorldLock.py`. Expected: PASS for both.
4. Inspect `REN_DistantGate`: record its Mobility, Tags and live bounds. The expected bounds are x ±250, y 5250..5350, z 0..1100. Report any difference before continuing.
5. Visual reference rule: `ProjectDocs/References/REFERENCE_MANIFEST.md`. It isn't present yet, so all visuals today are greybox or `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.

## 1. Build the sublevel — 20 min

1. Create folder `/Game/REN/Worlds/GateWest/`. File → New Level → **Empty Level** (not Open World). Save it as `L_GateWest_Blockout`.
2. With only that level open, run the builder.
   - Expected log: `REN Gate of the West Greybox Builder v1 COMPLETE` and `Spawned: 59 | REN_GW_ actors now in level: 59 (expected 59)`, with no warnings.
   - If it refuses, report the message verbatim.
3. Check: `REN_GW_CombatGate_Slab` has Mobility = Movable. The Outliner folders `REN_GW/...` exist. Save.
4. In `L_REN_Slice`, open the Levels window → Add Existing `L_GateWest_Blockout`, set Always Loaded with an identity transform. Visually confirm that the passage starts flush at the north edge of the Necropolis plinth, directly behind the Gate.

## 2. Gate opening (property changes on one Tomb actor) — 30 min

1. Open `L_Tomb_Blockout` (standalone or as the current level). On `REN_DistantGate`, set **Mobility = Movable** and add Actor Tag `REN_GateWestLeaf`. **Do not touch its transform.** Save.
2. Create `/Game/REN/Gameplay/Interaction/BP_GateWestOpener`:
   - Variables:
     - `TriggerActor` (Actor ref, instance-editable) → `REN_GW_Trigger_GateOpen` (same GW level)
     - `SinkDistance` = 1100, `Duration` = 6.0
     - `OpenSound` (Sound, nullable)
     - `bOpened`, `GateActor` (Actor)
   - BeginPlay:
     1. `GetAllActorsWithTag(REN_GateWestLeaf)`. If the count isn't 1 → `PrintString` / log an error and return.
     2. Bind `TriggerActor.OnActorBeginOverlap`.
   - On overlap by the player pawn, if `NOT bOpened`:
     1. Set `bOpened = true`.
     2. If `OpenSound` is valid, play it at the gate.
     3. Timeline (`Duration`, ease-in) sets GateActor Z to `StartZ − SinkDistance`. The end state is deterministic.
     4. Optional: a restrained camera shake (reuse the Day-2 `BP_CameraShake_DoorRumble` if it exists).
3. Place it in `L_GateWest_Blockout`, label `REN_INT_GW_GateOpener`, and set its references. Save.

Failure note: if tag lookup across sublevels fails in PIE, check that the Tomb is Always Loaded in the slice and the tag is spelled exactly. **Don't** move the gate to another level to work around it; report instead.

## 3. Checkpoints — 20 min

Use the approach decided in `docs/IMPLEMENTATION_P3_COMBAT.md` §5 (donor checkpoint volume if viable, otherwise `BP_REN_Checkpoint`):
- `REN_INT_GW_Checkpoint_Approach` → bound to `REN_GW_Trigger_Checkpoint_Approach`, respawn transform = `REN_GW_Respawn_Approach`.
- `REN_INT_GW_Checkpoint_ArenaApproach` → `REN_GW_Trigger_Checkpoint_ArenaApproach` / `REN_GW_Respawn_ArenaApproach`.

Combat logic and the combat gate come from `docs/tasks/P3_FIRST_COMBAT.md`, which is part 2 of this day.

## 4. Light pass (greybox) — 20 min

Change existing `REN_GW_Light_*` properties only:
- passage and corridor: dim and cool
- court: bright enough to read enemy silhouettes and wind-ups
- arena: even, with no dark corners
- recess: very dim, so it reads as the boss entrance

Keep the exposure from `REN_PPV_Slice` (Day 2). No fog, no bloom increase.

## 5. PIE tests (from `L_REN_Slice`) — PASS/FAIL each — 25 min

1. Continuous run from the Necropolis plaza with no loading. Stepping onto the plaza sinks the Gate once, over 6 s; it ends flush.
2. The passage is walkable. The camera doesn't clip through the lintels or walls at normal distance.
3. From the passage, the court and the stelae are visible down the axis. Enemy markers are in view (enemies come in part 2).
4. The combat gate blocks progress; it can't be jumped or squeezed past.
5. With the slab temporarily lowered (console or a test key; revert afterwards), the corridor → arena is walkable. The recess reads as the boss entrance. The four pillar shells leave comfortable lanes.
6. Camera in the arena: it's never trapped between a pillar and a wall; the whole-arena read is good.
7. The checkpoints register. A forced respawn (e.g. `kill` / debug) places the player at the matching `Respawn_*` facing +Y.
8. No Blueprint errors in the log.
9. **Timing:** plaza → combat gate, excluding the fight. Expected about 20–30 s.

## 6. World-lock (after section 5 passes)

1. Open `L_GateWest_Blockout` standalone and export → the first GW baseline. Commit it.
2. Validate the Tomb standalone. Expected: PASS. `REN_DistantGate` had only property changes (mobility and tags aren't tracked), so there should be no spatial differences. Any CHANGED line = FAIL.
3. Validate the Necropolis. Expected: PASS.

## 7. Hand-back

- Commit the assets (LFS), the GW baseline and validation reports, and docs (CURRENT_PROJECT_STATE, TASK_BOARD, DEVLOG).
- Report: the section 5 results, a gate-opening screenshot, a court screenshot from the passage, and an arena overview screenshot.
