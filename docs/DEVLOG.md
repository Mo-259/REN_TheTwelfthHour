# REN — Development Log

## 2026-09-30 — Unreal project bootstrap

- Unreal Engine 5.8 project created from Third Person template.
- Third-person movement/camera verified by user.
- Python Editor Script Plugin enabled.
- Python automation chosen for repetitive editor blockout work.
- `L_Tomb_Blockout` created under `/Game/REN/Worlds/Tomb/`.
- Early builder version exposed execution/world-switch issues.
- Builder workflow changed to operate inside the currently open level.
- Tomb Opening Greybox Builder v3 executed successfully.
- v3 includes burial chamber, sarcophagus, Blank Cartouche clue, corridor, no-shadow clue zone, side room, exit, transition tunnel, reveal ledge, triggers, and temporary lights.
- Decision: use Claude Code Cloud temporarily for repository preparation; use local Unreal MCP when local Claude access is available.
- Decision: Blueprint-first vertical slice; Python for editor automation; no premature C++ migration.

## Next

- Install Claude development kit in project root.
- Audit repo from cloud.
- Preserve v3 script in source control.
- Prepare interaction foundation package.
- Configure local Unreal MCP later.

## 2026-09-30 — Cloud audit + P0-08 world-lock hardening (Claude Code Cloud)

Audit:
- DevKit files in repo are byte-identical to the uploaded DevKit zip.
- `L_Tomb_Blockout.umap` contains exactly the 58 `REN_` labels the v3 builder generates.
- Found `/Game/REN/IA_Interact` (unmapped, unreferenced). Found stale default-map config and a missing `PythonScriptPlugin` entry in `.uproject`.
- Suspected builder rotator-order issue (PlayerStart pitch 90; cartouche relief roll 90), to confirm via first export.

P0-08:
- Added `Scripts/Editor/REN_WorldLock_Core.py` (shared pure-Python logic + CLI).
- Export: schema 2 (map path, static mesh, duplicate labels); writes a `.candidate.json` instead of overwriting an existing baseline.
- Validate: wrap-aware rotation, duplicate / class / mesh / map checks, JSON report under `ProjectDocs/WorldLocks/Reports/`.
- Added `Scripts/Tests/test_worldlock.py`: 18 tests pass in cloud (fake `unreal` module).
- LOCAL_VALIDATION_REQUIRED: run export + validate in Unreal on `L_Tomb_Blockout`, commit baseline.

## 2026-09-30 — 7-day pre-alpha sprint planning (Claude Code Cloud)

- User constraint: ~30-min playable pre-alpha in 7 days; quality over duration; Tomb (0–8) and Face-Eater are polish tier A.
- Found template `Variant_Combat` content (combo/charged attack, damage interfaces, StateTree enemy AI, spawner, checkpoint volume, life bar). Decision: build Nefer / Nameless Dead / Face-Eater from REN-owned duplicates of these instead of new combat code.
- Decision: persistent `L_REN_Slice` + always-loaded sublevels (Tomb, Necropolis, GateWest) in shared coordinates; builders/world-lock run on standalone sublevel maps.
- Decision: fixed CameraActor view-target blends instead of Sequencer during the sprint.
- Design correction: interaction trace start is projected from the camera to the pawn; a raw 350 cm trace from a camera 3–5 m behind would barely pass the player.
- Added `docs/SPRINT_7DAY.md`, `docs/tasks/P1_INTERACTION_FOUNDATION.md`; scope amendment in VERTICAL_SLICE_SPEC (new Beat 7.5 Nameless Dead, design TBD).
- Guarded builder v3 (wrong world / locked layout) — 2 new tests; 20/20 offline tests pass. Unreal run LOCAL_VALIDATION_REQUIRED.

## 2026-09-30 — Corrections 1–7 + Necropolis/Anubis package (Claude Code Cloud)

User approved the audit and sprint direction, with corrections. Applied:
1. World-lock purpose = spatial continuity.
   - Mesh swaps at the same transform are now ASSET CHANGES (warning); `--strict-assets` / `STRICT_ASSETS` makes them fail.
   - Transform, missing, added, duplicate, class and level-ownership changes all fail.
   - Schema 3 records the owning level.
2. No locking known-bad transforms.
   - Added the read-only `REN_Inspect_TombOrientation.py`.
   - Day-1 order is now: inspect → fix confirmed errors only → PIE traversal → official baseline.
3. Tomb `REN_DistantTower_A/B` and `REN_DistantGate` are documented as skyline proxies. The Necropolis builds foundations and a plinth below them and never duplicates them (enforced by tests).
4. Variant_Combat is treated as a donor.
   - A full donor audit precedes duplication.
   - Face-Eater phase authority belongs to the REN state machine; the StateTree runs only in Combat.
5. No-shadow validation covers all player visual components.
6. `docs/NAMELESS_DEAD_SPEC.md`: real human Egyptians losing individuality, not undead. One family.
7. `.gitattributes`: forward-only LFS for `*.uasset`/`*.umap`. No history rewrite, and the legacy binaries show no status churn (verified). Local `git lfs install` required.

New package:
- `docs/NECROPOLIS_GREYBOX_SPEC.md`
- `Scripts/Editor/REN_Necropolis_Layout.py` (210 items)
- `Scripts/Editor/REN_Necropolis_Greybox_Builder_v1.py`
- `docs/tasks/P2_NECROPOLIS_ANUBIS.md`
- Honest Necropolis+Anubis estimate: 2.5–4.5 min, unpadded.

Finding: Unreal is left-handed. Facing +Y, player-right = −X, so the Blank Cartouche is on the player's LEFT and the side chamber on the RIGHT, contrary to the docs. Geometry is unchanged; this is a user decision (P0-16).

Offline tests: 49/49 pass. Everything in Unreal is LOCAL_VALIDATION_REQUIRED.

## 2026-09-30 — Tomb kept as built + C-02 Day-2 Tomb beats task (Claude Code Cloud)

- User decision: **keep the Tomb exactly as built; do not mirror.** The Blank Cartouche is player-left and the side chamber player-right. Docs are updated to player perspective, and the two misleading builder-v3 comments are corrected (comments only; geometry untouched). P0-16 DONE.
- New finding (code reading, hypothesis): several Tomb props float above the surface below them (a centre-pivot cube with centres too high):
  - shadow pedestal 25 cm, jars 18–20 cm, canopics 20 cm, tables 25–32.5 cm
  - sarcophagus base 12.5 cm above the platform, lid 31 cm above the base
  This would detach shadows in the no-shadow beat. Added P0-17 (measure on Day 1; Z-only fix before baseline, **only with user approval**).
- Created `docs/tasks/P2_TOMB_BEATS.md`: the exact Day-2 local MCP task.
  - Gameplay-first wake and reveal (no Sequencer, no CameraActor, optional ≤1–1.5 s assists).
  - Cartouche examine with a TEMP Arabic line.
  - `ApplySheutState()` no-shadow across all primitive and attached components, with RT/contact checks.
  - `BP_ShadowClue` delayed TEMP line.
  - A one-clue side chamber with generic `BP_ExamineClue`.
  - Heavy deterministic door.
  - Lighting and manual exposure.
  - User-sourced audio placeholders.
  - PIE order, world-lock close-out, rollback notes and a cut list.
- The Arabic subtitle font moved from Day 3 to Day 2, since the Tomb lines are Arabic.
- Static review: no C++, no Sequencer, no final-art dependency. Core ≈4 h, cuttables ≤2 h, and the audio files are an external dependency.
- All Day-2 items are LOCAL_VALIDATION_REQUIRED.

## 2026-09-30 — C-03 Gate of the West + C-04 first combat spec; user decisions (Claude Code Cloud)

User decisions applied:
- **P0-17 approved with a procedure.** Inspect, measure and confirm, then change Z only (preserving X, Y, rotation and scale), re-check, and only then export the baseline.
  - Support props: fix if confirmed; the shadow-zone props are the priority.
  - Sarcophagus base and lid: never lowered automatically. Judge intent; stop if uncertain.
  - Tolerance: 1 cm or less.
- **Day-2 triggers:** inspect and reuse the existing `REN_Trigger_*` when suitable. A new volume is created only if one is unsuitable (with the reason recorded). World-locked triggers are never moved to fit a Blueprint.
- **Audio:** it must not block. Nullable hooks only, and gameplay must work with no sound. Sourcing is deferred to polish, and the cloud never imports audio.
- **Reference pack:** added `.claude/rules/visual-references.md` and a CLAUDE.md pointer to `ProjectDocs/References/REFERENCE_MANIFEST.md`, which is not yet in the repo. Placeholders are labelled `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.

C-03 Gate of the West package:
- `REN_GateWest_Layout.py` (59 items), builder v1 (`REN_GW_`), `GATE_WEST_GREYBOX_SPEC.md`, `tasks/P3_GATE_WEST.md`.
- Layout: passage (500 wide, lintels), 18×14 m combat court, sealed combat gate, corridor, 22×19 m arena **shell** with 4 Glyph-pillar shells and an on-axis boss recess. Markers only; no boss logic.
- The Gate opens by sinking the Tomb proxy `REN_DistantGate` at runtime: tag and mobility are property changes only, so there is no transform or level change.
- Honest time estimate: about 1.5–3 min excluding the boss.

C-04 first combat:
- `IMPLEMENTATION_P3_COMBAT.md` with donor assumptions A1–A10, all unverified.
- Decision **D1**: use child Blueprints instead of duplicates wherever donor assets cast to the donor classes. Duplicates would silently break those casts; templates are still never edited. A D1 note was added to the Day-1 task.
- Encounter controller with deterministic reset; minimal Blueprint restart fallback; dodge only if needed for fairness (documented timing).
- `tasks/P3_FIRST_COMBAT.md`.

Offline tests: 66/66 pass. Nothing is Unreal-validated.

## 2026-10-01 — C-05 Face-Eater boss mechanics package (Claude Code Cloud)

- The reference pack is still absent (`ProjectDocs/References/`). Mechanics only; all visuals are `TEMP_PLACEHOLDER`; no art decisions.
- Created:
  - `docs/FACE_EATER_BOSS_SPEC.md`: loop, state table, attacks, glyph window, damage model, arena requirements, reset, soft-lock table.
  - `docs/IMPLEMENTATION_P4_FACE_EATER.md`: assets, variables, functions, donor gate G1–G4, reset flow, self-review.
  - `docs/tasks/P4_FACE_EATER.md`: local MCP task with STOP conditions S1–S7.
  - `docs/QA_FACE_EATER.md`: 61 test cases across states, attacks, glyphs, damage, defeat, restart, camera/arena and hygiene.
- Key decisions:
  - **Combat deals 0 damage with deflect feedback** (no chip), so the lesson can't be brute-forced.
  - **One** valid glyph per recovery window → Exposed. Any of the 4 pillars works; all reset after the cycle.
  - The explicit `bGlyphWindowOpen` is opened and closed only by attack sequences.
  - **Staggered** is kept as a 1.2 s, no-damage seal-closing beat (not a bonus window).
  - Health 100, 7 per Exposed hit, cap 35 per cycle → 3–5 cycles. The first attack is always Heavy (the teaching moment).
  - Generation-token timers, a watchdog and invariant checks prevent stale sequences and soft-locks.
- **Gap found and fixed:** the arena had no entry trigger or lock (the player could leave mid-fight and the boss could follow). Added `REN_GW_ArenaGate_Slab` (rests below the threshold, rises 640) and `REN_GW_Trigger_ArenaEnter` to the not-yet-built GW layout (59 → 61 items). Additive only; no existing transform changed.
- Static arena-requirement tests (6 new) cover:
  - worst distance to a pillar face = **766 cm** → Heavy window reachable from anywhere (≈1.4 s < 2.8 s)
  - no boss-proof pockets, and no corner safe spots
  - the recess fits the boss
  - the entry lock is safe
- Offline tests: 72/72 pass. Nothing is PIE-validated; the donor integration is undecided (local gate).
