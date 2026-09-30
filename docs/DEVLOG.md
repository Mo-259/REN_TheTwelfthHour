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
