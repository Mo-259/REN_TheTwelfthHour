# REN — Current Project State

Last known state: 2026-09-30.

This file is the operational handoff. Update it whenever implementation state materially changes.

## Engine / project

- Engine: Unreal Engine 5.8.
- Base project: Third Person template, Blueprint project.
- Runtime template character is still the stock Third Person mannequin/character.
- Project name used during setup: `REN_TheTwelfthHour`.
- Python Editor Script Plugin is reported enabled by the user (v3 builder ran). NOTE: the committed `.uproject` does not list `PythonScriptPlugin`; confirm locally (LOCAL_VALIDATION_REQUIRED).
- Unreal MCP is planned for local agentic work; do not assume it is configured until verified locally.

## Level work completed

Known level:
- `/Game/REN/Worlds/Tomb/L_Tomb_Blockout`

A Python-generated Tomb opening greybox was successfully executed locally.

The v3 opening builder was designed to create:
- burial chamber
- sarcophagus placeholder / lid / platform
- blank cartouche clue panel on the player-left (+X) wall
- main corridor
- no-shadow test zone
- optional side clue chamber on the player-right (−X)
- clue prop placeholders
- trigger placeholders
- monumental exit door
- transition tunnel
- reveal ledge
- distant blockout silhouettes for the beginning of the Vertical Necropolis
- temporary greybox lights
- player start

Known trigger labels from v3:
- `REN_Trigger_BlankCartouche`
- `REN_Trigger_ShadowClue`
- `REN_Trigger_SideClue`
- `REN_Trigger_ExitReveal`

The user confirmed the v3 script completed.

## Existing editor automation

Expected file:
- `Scripts/Editor/REN_Tomb_Opening_Greybox_Builder_v3.py`

Status (cloud audit 2026-09-30): present in repo. `L_Tomb_Blockout.umap` contains exactly the 58 `REN_` actor labels this script generates (string scan of the binary; no extras, none missing). Transforms are NOT verifiable from cloud.

World-lock tooling (hardened 2026-09-30, cloud; Unreal execution LOCAL_VALIDATION_REQUIRED):
- `Scripts/Editor/REN_WorldLock_Core.py`: pure-Python compare logic + offline CLI (`--strict-assets`).
  - Schema 3 records the owning level.
  - **Spatial failures**: transform, missing/added/duplicate, class change, level-ownership change, map mismatch.
  - **Asset changes**: a mesh swapped at the same transform. Warning by default; fails only in strict mode.
- `Scripts/Editor/REN_Export_WorldLock.py`: never overwrites an existing baseline (writes `.candidate.json`).
- `Scripts/Editor/REN_Validate_WorldLock.py`: `STRICT_ASSETS = False` by default. Writes `ProjectDocs/WorldLocks/Reports/<World>.validation.json`.
- `Scripts/Editor/REN_Inspect_TombOrientation.py`: READ-ONLY check of the `REN_PlayerStart` / `REN_BlankCartouche_Relief` orientation. Must pass (or confirmed errors must be fixed) **before** the first official Tomb baseline.
- Tests: `Scripts/Tests/` (49 offline tests; fake `unreal` module). Run `python -m unittest discover -s Scripts/Tests`.
- **No world-lock baseline has been exported yet.**

Vertical Necropolis package (cloud-prepared 2026-09-30; **NOT built in Unreal**):
- `Scripts/Editor/REN_Necropolis_Layout.py`: pure layout data, 210 items, validated offline.
- `Scripts/Editor/REN_Necropolis_Greybox_Builder_v1.py`: prefix `REN_NEC_`. Refuses in the wrong world, refuses when Tomb/foreign REN actors are loaded (allows `REN_INT_*`/`REN_CAM_*`), and refuses when a baseline is locked. Re-run safe.
- Design: `docs/NECROPOLIS_GREYBOX_SPEC.md`. Local Day-3 task: `docs/tasks/P2_NECROPOLIS_ANUBIS.md`.

Day-2 Tomb beats package (cloud-prepared 2026-09-30; **NOT executed in Unreal**): `docs/tasks/P2_TOMB_BEATS.md`. It is gameplay-first (instant control at spawn, no cut at the reveal), with the Arabic subtitle font moved to Day 2. The project contains **no audio assets**; placeholders must be user-sourced.

Gate of the West + first combat package (cloud-prepared 2026-09-30; **NOT built or executed in Unreal**):
- `Scripts/Editor/REN_GateWest_Layout.py` (61 items, including the arena entry-lock slab + ArenaEnter trigger added for C-05; validated offline against the Tomb reference and all Necropolis solids, plus static Face-Eater arena-requirement tests)
- `Scripts/Editor/REN_GateWest_Greybox_Builder_v1.py` (prefix `REN_GW_`, same guards as Necropolis)
- `docs/GATE_WEST_GREYBOX_SPEC.md`, `docs/tasks/P3_GATE_WEST.md`
- `docs/IMPLEMENTATION_P3_COMBAT.md` (donor assumptions A1–A10 **unverified**; decision D1 child vs duplicate), `docs/tasks/P3_FIRST_COMBAT.md`
- The Face-Eater arena is a **shell only** (markers `*_PLACEHOLDER`). **No boss logic exists.**

Face-Eater boss package (cloud-prepared 2026-10-01; **mechanics only; NOT implemented or PIE-tested**):
- `docs/FACE_EATER_BOSS_SPEC.md`, `docs/IMPLEMENTATION_P4_FACE_EATER.md`, `docs/tasks/P4_FACE_EATER.md`, `docs/QA_FACE_EATER.md`
- The donor strategy is not decided: gate G1–G4 picks option F or R locally.
- Planned assets (none exist yet): `/Game/REN/Gameplay/Bosses/FaceEater/` → `BP_FaceEater`, `E_FaceEaterState`, `E_FaceEaterAttack`, `BP_FaceEaterGlyph`, `WBP_FaceEaterBossBar`.
- All Face-Eater visuals are `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.

Visual references: `ProjectDocs/References/` / `REFERENCE_MANIFEST.md` are **not yet in the repository**. Rule: `.claude/rules/visual-references.md`. Until the masters exist, all character and weapon visuals are `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.

## Tomb skyline / landmark proxies

These are created by builder v3 in `L_Tomb_Blockout`, beyond the reveal ledge:
- `REN_DistantTower_A`: player-right, near
- `REN_DistantTower_B`: player-left, far, tallest
- `REN_DistantGate`: on the axis; the Gate of the West façade

Rules:
- Keep their transforms. They must never be duplicated by other builders.
- Their mesh may be replaced later at the same transform (world-lock reports an asset change).
- The Necropolis adds foundations and a plinth below them.

## Tomb orientation (USER DECISION 2026-09-30: KEEP AS BUILT)

Unreal is left-handed. Facing +Y (spawn direction), **player-right = −X**.
- **Blank Cartouche: player-LEFT (+X wall).** Accepted.
- **Side clue chamber: player-RIGHT (−X).** Accepted.
- Shadow-test light `REN_Light_ShadowTest` is on the player-right (x −130). Prop shadows fall toward the player-left wall.
- The Tomb is **not mirrored**. No Tomb geometry moves because of this. The docs now use player-perspective terms.
- Builder-v3 labels `…Left…`/`…Right…` (e.g. `REN_Corridor_Left_A`, `REN_Reveal_LeftPier`) mean map −X/+X, i.e. the opposite of the player's view. The labels are kept; renaming would break world-lock continuity.

## Suspected floating props (code reading, 2026-09-30) — fix APPROVED with procedure, before the Day-1 baseline

Builder v3 uses the centre-pivot 100 cm Engine cube, and several prop centres are too high, so their bottoms float above the surface below. **Hypothesis until measured locally:**

| Actor | Bottom z | Surface below | Gap |
|---|---|---|---|
| `REN_ShadowTest_Pedestal` | 25 | floor 0 | 25 cm |
| `REN_ShadowTest_JarA` / `JarB` | 18 / 20 | floor 0 | 18 / 20 cm |
| `REN_Canopic_01..03` | 20 | floor 0 | 20 cm |
| `REN_OfferingTable_Main` | 25 | floor 0 | 25 cm |
| `REN_Side_CluePedestal` | 32.5 | floor 0 | 32.5 cm |
| `REN_Side_Table` | 25 | floor 0 | 25 cm |
| `REN_Sarcophagus_Base` | 25 | platform top 12.5 | 12.5 cm |
| `REN_Sarcophagus_Lid` | 126 | base top 95 | 31 cm |

Detached shadows under the pedestal and jars would weaken the no-shadow beat.

**User decision (2026-09-30):** confirmed floating props may be corrected **before** the first official Tomb baseline, following the procedure in `docs/tasks/P1_INTERACTION_FOUNDATION.md` (P0-17):
- inspect and measure the real gap
- confirm the prop is meant to rest on the surface
- change **Z only**
- re-check visually
- then export the baseline

Ordinary support props (pedestal, jars, canopics, tables) are fixed if confirmed; the shadow-zone props are the priority. **The sarcophagus base and lid are not lowered automatically**: first judge whether the separation is intentional, and stop and report if uncertain. Gaps of 1 cm or less are tolerated.

## Production plan

Active: 7-day pre-alpha sprint, see `docs/SPRINT_7DAY.md` (quality over duration). Day-1 local task: `docs/tasks/P1_INTERACTION_FOUNDATION.md`.

Template assets relevant to the sprint (present by path; internals NOT inspected, binary):
- `/Game/Variant_Combat/Blueprints/`: `BP_CombatCharacter`, `BP_CombatGameMode`, `BP_CombatPlayerController`, `BPI_Damageable`, `BPI_Attacker`, `BPI_Activatable`, camera shakes
- `/Game/Variant_Combat/Blueprints/AI/`: `BP_CombatEnemy`, `BP_CombatAIController`, `BP_Combat_EnemySpawner`, `ST_CombatEnemy` (StateTree), EQS queries
- `/Game/Variant_Combat/Blueprints/Interactables/`: `BP_Combat_CheckpointVolume`, `BP_Combat_ActivationVolume`, `BP_Combat_Dummy`
- `/Game/Variant_Combat/Anims/`: `AM_ComboAttack`, `AM_ChargedAttack`, attack notifies; `/Game/Variant_Combat/UI/UI_LifeBar`; `IMC_Combat`, `IA_ComboAttack`, `IA_ChargedAttack`
- No dodge exists in the template.

Builder v3 safety guard (2026-09-30): refuses to run unless `L_Tomb_Blockout` is the open world and no Tomb world-lock baseline exists (override flag `FORCE_REBUILD_AFTER_LOCK`).

## Known temporary solutions

- `/Game/REN/IA_Interact` stays at the REN root for the sprint (not moved to `Gameplay/`).
- Interactables are collision volumes placed over greybox meshes (not mesh replacements).
- **Persistent slice world** (approved for the vertical slice only):
  - `L_REN_Slice`, non-World-Partition, with always-loaded sublevels `L_Tomb_Blockout`, `L_Necropolis_Blockout` and `L_GateWest_Blockout` in one coordinate system.
  - No streaming framework, no loading screens.
  - Not necessarily the shipping architecture.
- **Variant_Combat as donor**: REN-owned duplicates of the template combat Blueprints. Template assets are never edited. The donor audit must precede duplication.
- **Face-Eater placeholder**: may start as a scaled `BP_CombatEnemy` duplicate. Phase authority belongs to the REN state machine (see `docs/SPRINT_7DAY.md` decision 2).
- **No-shadow**: `Cast Shadow = false` on the player visual components (no shadow framework).
- **Anubis**: a still mannequin placeholder with a proxy jackal head and a fixed CameraActor (no Sequencer). `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.
- **Gate of the West opening**: the Tomb proxy `REN_DistantGate` gets Movable plus the tag `REN_GateWestLeaf` (property changes only) and is sunk at runtime by `BP_GateWestOpener` in the GW level via tag lookup (no cross-level hard reference, no level move).
- **Donor class strategy (D1)**: REN combat classes may be *child* Blueprints of the Variant_Combat classes (keeps a dependency on `/Game/Variant_Combat/`) where the audit shows donor casts.
- **Audio**: nullable hooks only; no sound assets until the polish pass.

## Repository audit findings (cloud, 2026-09-30)

- `/Game/REN/IA_Interact` exists (InputAction, Boolean). No asset references it: it is not mapped in any IMC and not used by `BP_ThirdPersonCharacter`. Location differs from the planned `/Game/REN/Gameplay/...` layout; do not move it without a redirector-aware local step.
- `Config/DefaultEngine.ini`: `GameDefaultMap` / `EditorStartupMap` still `Lvl_ThirdPerson`. `Config/DefaultEditor.ini` references nonexistent `/Game/TP_ThirdPerson/Maps/ThirdPersonExampleMap`. `DefaultGame.ini` ProjectName is still the template name.
- Builder v3 rotator order (code reading only; a HYPOTHESIS until the local check): UE Python `unreal.Rotator(roll, pitch, yaw)`.
  - `REN_PlayerStart` is spawned with `Rotator(0.0, 90.0, 0.0)` → pitch 90, not yaw 90.
  - `REN_BlankCartouche_Relief` `(0,90,0)` → roll 90, likely a horizontal slab rather than a vertical cartouche.
  - Confirm with `REN_Inspect_TombOrientation.py` **before** the first baseline. Fix only confirmed errors (rotation only). Never re-run the builder to fix them.
- Git LFS: **adopted forward-only** (2026-09-30) via `.gitattributes` (`*.uasset`, `*.umap`). The 449 bootstrap binaries stay as normal blobs; no history rewrite. **Local setup required: `git lfs install`** on every machine.
- No `Source/` folder (Blueprint-only, as intended).

## Runtime gameplay state

Not yet implemented / not yet verified:
- custom Nefer character
- Reed Blade
- interaction input
- interaction interface/base
- Blank Cartouche runtime interaction
- Exit Door runtime interaction
- Sarcophagus runtime interaction
- Heka/Glyph runtime interaction
- no-shadow runtime mechanic
- narrative prompts/UI
- custom combat changes
- Face-Eater runtime boss
- Anubis encounter
- checkpoints/save flow
- cinematic Sequencer content

Do not claim these exist until live project audit proves they do.

## Art state

The final in-engine art has not been built.

There are approved external visual references/concepts for:
- Nefer
- Seth
- Ra at night
- Anubis bridge reveal
- Apep hero scale
- Face-Eater master
- Solar Barque gameplay layout
- Vertical Necropolis gameplay look
- Tomb exit
- Name erasure
- Nefer eye

These are design references, not proof that corresponding Unreal assets exist.

## Immediate target

First runtime milestone:
- player can traverse the v3 Tomb greybox
- interact with Blank Cartouche
- experience the no-shadow clue
- interact with Exit Door
- reach the reveal ledge
- all with stable geometry and clean third-person gameplay

## Source-of-truth note

If the live Unreal project differs from this document, the live project wins. Update this document after auditing.
