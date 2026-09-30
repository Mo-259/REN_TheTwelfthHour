# Local Task — P1 Interaction Foundation (Sprint Day 1)

Execution: **local Unreal + MCP only.** Written in cloud; every step is LOCAL_VALIDATION_REQUIRED.
Covers TASK_BOARD P1-01 … P1-08 plus the Nefer character bootstrap.

Serialize MCP calls: inspect → mutate → compile/save → inspect.

## 0. Audit first (no edits)

1. `git pull`, then `git status` must be clean. Make a checkpoint commit if it is not.
2. Open `/Game/REN/Worlds/Tomb/L_Tomb_Blockout`. Run `Scripts/Editor/REN_Export_WorldLock.py` (writes the baseline) and commit it.
3. Inspect and write down the answers (in the task report):
   - `BP_CombatGameMode`: Default Pawn, Player Controller, HUD.
   - `BP_CombatPlayerController`: where Input Mapping Contexts are added (BeginPlay?) and which IMCs.
   - `IMC_Combat` and `IMC_Default`: which keys/buttons are used. Is `E` free? Which gamepad face button is free?
   - `BP_CombatCharacter`: camera setup (spring-arm length), components, existing interfaces (`BPI_Attacker`, `BPI_Damageable`), and whether it shows `UI_LifeBar` itself.
   - `L_Tomb_Blockout` World Settings: GameMode Override.
   - `REN_ExitDoor`: Mobility (expected Static).
4. If anything contradicts this spec, stop and report before continuing.

## 1. Folders

Create:
- `/Game/REN/Gameplay/Player/`
- `/Game/REN/Gameplay/Interaction/`
- `/Game/REN/UI/`

Leave `/Game/REN/IA_Interact` where it is for the sprint. Moving it creates redirector churn for no player value. This is a documented temporary location.

## 2. Player bootstrap (template duplicates, never edit templates)

| New asset | Duplicated from |
|---|---|
| `/Game/REN/Gameplay/Player/BP_NeferCharacter` | `/Game/Variant_Combat/Blueprints/BP_CombatCharacter` |
| `/Game/REN/Gameplay/Player/BP_REN_PlayerController` | `/Game/Variant_Combat/Blueprints/BP_CombatPlayerController` |
| `/Game/REN/Gameplay/Player/BP_REN_GameMode` | `/Game/Variant_Combat/Blueprints/BP_CombatGameMode` |

- `BP_REN_GameMode`: set Default Pawn = `BP_NeferCharacter` and Player Controller = `BP_REN_PlayerController`.
- `L_Tomb_Blockout` World Settings: set GameMode Override = `BP_REN_GameMode`.
- Compile, save, then check in PIE that the player spawns at `REN_PlayerStart`, moves, attacks and the camera works.
  - If the combat character feels wrong in the 3 m corridor (camera clipping, side-offset camera), note it. The **fallback** is to duplicate `/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter` as `BP_NeferCharacter` instead and port combat on Day 4 (see `docs/SPRINT_7DAY.md`).
- Check spawn facing. The v3 builder probably spawned `REN_PlayerStart` with **pitch 90 instead of yaw 90**. Check the world-lock JSON. If rotation is not `[0, 0, 90]`, fix only that actor's rotation to yaw 90 / pitch 0, re-export as a candidate, promote it, and log it in DEVLOG.

## 3. Input

- Create `/Game/REN/Gameplay/Player/IMC_REN_Default`.
  - `IA_Interact` → Keyboard `E`, plus a free gamepad face button (from the step-0 audit).
  - Triggers: **Pressed** (fires once per press; no hold-repeat).
- `BP_REN_PlayerController`, after the existing IMC setup: Add Mapping Context `IMC_REN_Default`, **Priority 1**.
- `IA_Interact` stays Boolean (already so).

## 4. `BPI_Interactable`

`/Game/REN/Gameplay/Interaction/BPI_Interactable` with exactly 3 functions:

| Function | Inputs | Output |
|---|---|---|
| `CanInteract` | `Interactor` (Actor) | `bCan` (Boolean) |
| `GetInteractionPrompt` | none | `Prompt` (Text) |
| `Interact` | `Interactor` (Actor) | none |

Implementers return `true` / `"Interact"` unless there is a reason not to. No base class; implementers are separate small Actors.

## 5. Trace and focus in `BP_NeferCharacter`

Variables:
- `FocusedInteractable` (Actor, not replicated)
- `InteractRange` (Float) = 350.0
- `InteractRadius` (Float) = 30.0
- `PromptWidget` (`WBP_InteractPrompt` ref)

Function **`FindInteractable` → Actor**:

1. `CamLoc`, `CamFwd` = the player camera manager's camera location and forward vector.
2. **Project the start to the player**, because the camera sits 300–500 cm behind:
   `Depth = Dot(GetActorLocation - CamLoc, CamFwd)`
   `Start = CamLoc + CamFwd * max(Depth, 0)`
   `End = Start + CamFwd * InteractRange`
3. `SphereTraceByChannel` from Start to End, radius `InteractRadius`, channel `Visibility`, ignore Self.
4. If Hit Actor implements `BPI_Interactable` and `CanInteract(self)` → return it. Otherwise return None.

Focus update: **no Tick.** In BeginPlay, run `Set Timer by Event` every 0.1 s, looping:
- `NewFocus = FindInteractable()`
- If NewFocus ≠ FocusedInteractable: set it. If valid, show the prompt with `GetInteractionPrompt()`. Otherwise hide it.

Input: **`IA_Interact` Started** (not Triggered):
- If `FocusedInteractable` is valid and `CanInteract(self)` → `Interact(self)`.
- Then force an immediate focus refresh, so a door that just opened hides the prompt.

## 6. UI

- `/Game/REN/UI/WBP_InteractPrompt`: a small bottom-center text, `E — Interact` (with the prompt text substituted). Create it in `BP_NeferCharacter` BeginPlay, add it to the viewport, and hide it.
- `/Game/REN/UI/WBP_Subtitle`: a bottom text line. Add a function `ShowSubtitle(Text, Duration)` on `BP_REN_PlayerController` that owns the single instance. A new line replaces the current one, and it auto-hides after Duration. This is reused by the Cartouche, the side clues and Anubis.
- Style: plain, restrained serif or clean sans in off-white; no glow.

## 7. Interactables

Rule: **do not move or replace greybox actors.** Interactables are added *on top of* the existing world-locked geometry.

### 7a. `BP_BlankCartouche`

`/Game/REN/Gameplay/Interaction/BP_BlankCartouche`:
- Root: a Box Collision about 60 × 180 × 260 cm. Collision: **Custom**, Visibility = Block, everything else Ignore. The pawn walks through it; only traces hit it.
- Place it over `REN_BlankCartouche_Relief` / `_Panel` (around `(370, 110, 215)`), covering the relief's front face. Label: `REN_INT_BlankCartouche`.
- `Interact`:
  - `ShowSubtitle` with TEMP text: *"A name was carved here. Someone cut it out."* (4 s). This wording is editable script, not canon.
  - Set `bSeen = true`.
- `GetInteractionPrompt` → "Examine".
- Repeat interactions are allowed (the subtitle shows again).

### 7b. `BP_ExitDoor`

`/Game/REN/Gameplay/Interaction/BP_ExitDoor`:
- Instance-editable `DoorActor` (Actor ref) → set to `REN_ExitDoor`. Set `REN_ExitDoor` **Mobility = Movable**. This is a property change, not a transform change.
- Root: a Box Collision on the corridor side of the door (about 200 × 60 × 300, Visibility Block only). Label: `REN_INT_ExitDoor`.
- `bOpen` = false.
- `CanInteract` → `NOT bOpen AND NOT bMoving`.
- `Interact`:
  - A Timeline of 2.5 s with an ease-in curve lowers `DoorActor` by **320 cm** in Z (a stone slab sinking into the floor; mass comes from slow ease-in).
  - Placeholder camera shake optional.
  - On finish set `bOpen = true`.
  - The end position is deterministic: `start Z − 320`.
- `GetInteractionPrompt` → "Open".
- Door acceptance: the player can't be trapped (the door moves down, away from the player), and collision moves with the mesh.

### 7c. `BP_Sarcophagus` (P1-07, optional on Day 1; cut order #6)

Same volume pattern over `REN_Sarcophagus_Lid`. `Interact` → subtitle TEMP line, nothing else.

## 8. Acceptance tests (PIE) — report each PASS/FAIL

1. The player spawns at `REN_PlayerStart` facing +Y (toward the corridor), not inside collision.
2. Looking at the Cartouche from 1–3 m shows the "E — Examine" prompt without pixel-perfect aim. Looking away hides it within about 0.1 s.
3. One E press → exactly one subtitle. Holding E does not repeat.
4. Pressing E while looking at a wall or a non-interactable does nothing, with no errors in the log.
5. The prompt never appears for the player's own body or for trigger boxes.
6. The Exit Door opens once and the prompt disappears after opening. A second E does nothing.
7. After opening, the player walks through the tunnel to `REN_RevealLedge` without snagging.
8. The door's end Z equals its start Z − 320 (check in the Details panel during PIE).
9. The Output Log shows no Blueprint errors or "Accessed None" during a full Tomb run.
10. After exiting PIE: run `REN_Validate_WorldLock.py`. The expected result is REVIEW REQUIRED with **only** these differences: ADDED `REN_INT_*` actors, plus the `REN_PlayerStart` rotation if it was fixed. Any MISSING, any CHANGED greybox actor (especially `REN_ExitDoor`, which must be back at its closed transform outside PIE), or any DUPLICATE = FAIL. If the differences are only the expected ones, export (writes the candidate), promote it to baseline, and log it in DEVLOG.

## 9. Hand-back

- Commit the Blueprints/UI assets, the updated world-lock + validation report, and `docs/` updates (CURRENT_PROJECT_STATE, TASK_BOARD, DEVLOG).
- In the report, include the step-0 audit answers. The cloud Day-2 spec depends on them.
