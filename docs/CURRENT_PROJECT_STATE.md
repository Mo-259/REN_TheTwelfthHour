# REN — Current Project State

Last known state: 2026-09-30.

This file is the operational handoff. Update it whenever implementation state materially changes.

## Engine / project

- Engine: Unreal Engine 5.8.
- Base project: Third Person template, Blueprint project.
- Runtime template character is still the stock Third Person mannequin/character.
- Project name used during setup: `REN_TheTwelfthHour`.
- Python Editor Script Plugin is enabled.
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

Important:
The script was originally executed from an external downloaded file. Audit whether it has actually been copied into the repository. If absent, restore it from this dev kit.

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
