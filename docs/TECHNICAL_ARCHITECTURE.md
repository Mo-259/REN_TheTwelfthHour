# REN — Technical Architecture

## Current architecture decision

**Blueprint-first vertical slice.**

Reasons:
- current project is a Blueprint Third Person template
- user is new to Unreal
- fast iteration matters more than premature native architecture
- local Unreal MCP can manipulate Blueprints directly
- Python can automate editor setup

C++ is not forbidden, but must be justified before introduction.

## Sprint decisions (2026-09-30)

For the 7-day pre-alpha, the concrete choices in `docs/SPRINT_7DAY.md` → "Architecture decisions" take precedence over the more general targets below. Summary:
- `BP_NeferCharacter` / `BP_NamelessDead` / `BP_FaceEater` start as duplicates of the template `Variant_Combat` Blueprints (combo, charged attack, damage interfaces, StateTree AI, life bar, checkpoint volume already exist). Template assets are never edited in place.
- One non-World-Partition persistent level `L_REN_Slice` with always-loaded sublevels `L_Tomb_Blockout`, `L_Necropolis_Blockout`, `L_GateWest_Blockout` in a shared coordinate system (+Y toward the Duat).
- Fixed CameraActors + Set View Target with Blend instead of Sequencer for the sprint.

## Responsibility split

### Runtime gameplay
Use Blueprint for:
- player interaction
- doors
- clue triggers
- Heka interactions
- boss states
- health/damage prototype
- checkpoints prototype
- UI prompts
- encounter orchestration

### Editor automation
Use Unreal Python for:
- blockout generation
- actor placement
- world-lock export
- validation
- repetitive editor setup
- batch asset inspection
- report generation

Python must not be treated as runtime game logic.

### Local agent control
Use Unreal MCP when working locally:
- inspect live level state
- edit Blueprint graphs
- manipulate assets
- configure materials/lights
- build Sequencer content
- run automation tests

MCP tool calls should be serialized; do not issue overlapping editor mutations.

## Core Blueprint architecture target

### Player
`BP_NeferCharacter` eventually replaces stock Third Person character.

Initial interaction implementation may be added to the stock character, but move it into REN-owned assets before the slice is considered stable.

Recommended:
- `BP_NeferCharacter`
- `AC_Interaction` or equivalent interaction component if complexity grows
- `AC_Combat` only when combat warrants separation

Do not componentize everything prematurely.

### Input
- `IA_Interact`
- existing template movement/look/jump actions
- later:
  - `IA_AttackLight`
  - `IA_AttackHeavy`
  - `IA_Dodge`
  - `IA_LockOn`
  - `IA_Heka`

Mapping context naming:
- `IMC_REN_Default` when REN-specific input becomes stable

### Interaction
Base rule:
player performs a short forward trace from gameplay camera.

Prototype distance:
- 350 cm, measured from the player's depth along the camera ray (the trace start is projected from the camera forward to the pawn; a trace starting at the camera would end almost at the player because the camera sits 300–500 cm behind). Sphere trace, radius 30 cm. Exact recipe: `docs/tasks/P1_INTERACTION_FOUNDATION.md`.

Desired conceptual interface:
- `BPI_Interactable`
- function: `Interact(Interactor)`
- optional later:
  - `CanInteract`
  - `GetInteractionPrompt`

First interactables:
- `BP_BlankCartouche`
- `BP_ExitDoor`
- `BP_Sarcophagus`
- `BP_GlyphMechanism`

### Narrative clue triggers
Use explicit named Trigger Boxes / Blueprint Actors, not level-script spaghetti.

Avoid putting major gameplay logic in the Level Blueprint.

### Boss
`BP_FaceEater` prototype may initially be one Blueprint.

Use an explicit state enum:
- Dormant
- Intro
- Combat
- Exposed
- Staggered
- Defeated

Boss mechanic state must be readable and deterministic.

### Heka
Do not build a universal magic framework yet.

For slice, implement only what is required:
- Glyph interaction with specific mechanisms
- semantic visual language
- no generic projectile-magic system

## World locking

Once a level reaches "layout locked":
1. export actor transforms
2. commit manifest
3. validate before/after risky scripts
4. intentional changes require manifest refresh and devlog entry

## Save / checkpoints

For first playable slice:
- use level start / encounter restart
- avoid building production persistence early
- introduce a minimal checkpoint only after boss loop is playable

## UI

Minimal:
- small interaction prompt
- player health only when combat begins
- boss health only when boss begins
- no inventory HUD in slice

## Performance

Do not optimize by intuition.

Before performance work:
- establish representative scene
- profile
- identify actual bottleneck

Nanite/Lumen decisions belong to the art/performance pass, not the greybox stage.
