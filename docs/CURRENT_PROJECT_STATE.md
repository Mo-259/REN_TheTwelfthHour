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
- blank cartouche clue panel on player-right
- main corridor
- no-shadow test zone
- left side clue chamber
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
- `Scripts/Editor/REN_WorldLock_Core.py` — pure-Python compare logic + offline CLI.
- `Scripts/Editor/REN_Export_WorldLock.py` — schema-2 export; never overwrites an existing baseline (writes `.candidate.json`).
- `Scripts/Editor/REN_Validate_WorldLock.py` — wrap-aware rotation compare, duplicate-label / class / mesh / map-path checks, writes `ProjectDocs/WorldLocks/Reports/<World>.validation.json`.
- `Scripts/Tests/test_worldlock.py` — 18 offline tests (fake `unreal` module); run `python -m unittest discover -s Scripts/Tests`.
- No world-lock baseline has been exported yet.

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

## Repository audit findings (cloud, 2026-09-30)

- `/Game/REN/IA_Interact` exists (InputAction, Boolean). No asset references it: it is not mapped in any IMC and not used by `BP_ThirdPersonCharacter`. Location differs from the planned `/Game/REN/Gameplay/...` layout; do not move it without a redirector-aware local step.
- `Config/DefaultEngine.ini`: `GameDefaultMap` / `EditorStartupMap` still `Lvl_ThirdPerson`. `Config/DefaultEditor.ini` references nonexistent `/Game/TP_ThirdPerson/Maps/ThirdPersonExampleMap`. `DefaultGame.ini` ProjectName is still the template name.
- Builder v3 rotator order (code reading only): UE Python `unreal.Rotator(roll, pitch, yaw)`. `REN_PlayerStart` is spawned with `Rotator(0.0, 90.0, 0.0)` → pitch 90, not yaw 90. `REN_BlankCartouche_Relief` `(0,90,0)` → roll 90, likely a horizontal oval rather than a vertical cartouche. Confirm via first world-lock export; do not "fix" by re-running the builder after layout lock.
- No Git LFS / `.gitattributes`. Largest asset ~21 MB. LFS adoption is a pending user decision.
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
