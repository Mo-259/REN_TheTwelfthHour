# Local Task — P1 Interaction Foundation (Sprint Day 1)

Execution: **local Unreal + MCP only.** Written in cloud; every step is LOCAL_VALIDATION_REQUIRED.
Covers TASK_BOARD P1-01 … P1-08 plus the Nefer character bootstrap.

Serialize MCP calls: inspect → mutate → compile/save → inspect.

## 0. Audit first (no edits)

1. **Git LFS:** run `git lfs install` once on this machine, **before** the first `git pull`. The repo now tracks `*.uasset`/`*.umap` in LFS (forward-only; see `.gitattributes`). Never run `git lfs migrate` or `git add --renormalize .`.
2. `git pull`, then `git status` must be clean. Make a checkpoint commit if it is not.
3. Run the offline tests: `python -m unittest discover -s Scripts/Tests`. They must all pass.
4. **Tomb orientation check (read-only).** Open `/Game/REN/Worlds/Tomb/L_Tomb_Blockout` standalone and run `Scripts/Editor/REN_Inspect_TombOrientation.py`. Record the verdicts from the log and from `ProjectDocs/WorldLocks/Reports/L_Tomb_Blockout.orientation_check.json`.
   - **Do NOT export the world-lock baseline yet.** Section 2a covers the order.
5. **Variant_Combat donor audit (read-only).** Write the answers to `docs/audits/VARIANT_COMBAT_DONOR_AUDIT.md`. Variant_Combat is a *donor*, not unquestioned architecture:
   - `BP_CombatGameMode`: Default Pawn, Player Controller, HUD, and any other class references or checkpoint/respawn logic.
   - `BP_CombatPlayerController`: where Input Mapping Contexts are added (BeginPlay?), which IMCs, UI creation, and respawn handling.
   - `BP_CombatCharacter`:
     - camera (spring-arm length, socket offset, camera-side toggle)
     - components and implemented interfaces (`BPI_Attacker`, `BPI_Damageable`, `BPI_Activatable`)
     - Anim Blueprint (`ABP_Manny_Combat`), montage slots and anim notifies (`AN_AttackCombo`, `AN_AttackDamage`, `AN_ChargedAttack`)
     - whether it creates `UI_LifeBar` itself
     - death/respawn behaviour
   - `BP_CombatEnemy` + `BP_CombatAIController`:
     - StateTree `ST_CombatEnemy` with its tasks, conditions and EQS queries
     - how targets are chosen
     - how damage is applied and received
     - health variables and death
     - which parts are hard-wired to the player class
   - `BP_Combat_EnemySpawner`, `BP_Combat_CheckpointVolume`, `BP_Combat_ActivationVolume`: dependencies.
   - `IMC_Combat` and `IMC_Default`: which keys/buttons are used. Is `E` free? Which gamepad face button is free?
   - **Hardcoded references**: any Blueprint referencing `Lvl_Combat` actors, level names, `/Game/Variant_Combat/...` asset paths, or `GetAllActorsOfClass` on template classes. List every one. They must be retargeted after duplication.
   - **UI dependencies**: widgets used and who creates them.
   - `L_Tomb_Blockout` World Settings: GameMode Override.
   - `REN_ExitDoor`: Mobility (expected Static).
6. If anything contradicts this spec, stop and report before continuing.

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
- Spawn facing is handled in section 2a. Do not change actor transforms here.

## 2a. Confirm orientation, fix only confirmed errors, THEN lock the Tomb

Do not lock a known-bad transform. Follow this order strictly:

1. **Inspect.** Use the step 0.4 verdicts. The code-reading *hypotheses* are listed below; don't treat them as facts:
   - `REN_PlayerStart`: pitch 90 instead of yaw 90.
   - `REN_BlankCartouche_Relief`: rolled 90°, giving a horizontal slab instead of a vertical cartouche.
2. **Confirm.** Only a `WRONG` / `WRONG_HORIZONTAL` verdict counts as confirmed. `UNEXPECTED`, `NOT_FOUND` or `DUPLICATE` → stop and report.
3. **Fix only the confirmed errors**, in the Details panel, changing rotation only:
   - PlayerStart → Rotation X(roll)=0, Y(pitch)=0, Z(yaw)=90.
   - Cartouche relief → Rotation 0, 0, 0 (location and scale unchanged). The result is a vertical 72 × 145 cm slab on the wall.
   - The rounded cartouche silhouette comes later as a mesh swap at the same transform. World-lock treats that as an *asset change*, not drift.
   Save, re-run `REN_Inspect_TombOrientation.py`, and expect `ALL OK`.
4. **Verify traversal** in PIE (P0-06):
   - spawn facing +Y, not inside collision
   - burial chamber → corridor → side chamber → exit door area → tunnel → reveal ledge
   - no snags, no falls through the world
5. **Then export the first official baseline:** with `L_Tomb_Blockout` open standalone, run `REN_Export_WorldLock.py`. It writes `L_Tomb_Blockout.worldlock.json`. Commit it together with the orientation report, and log in DEVLOG which fixes were applied.
6. From now on, builder v3 refuses to run (layout locked).

Left/right note: facing +Y (spawn direction), the **player's right is −X**. The Blank Cartouche (+X) is therefore on the player's **left**, and the side chamber (−X) is on the player's **right**. The docs previously said the opposite. **Do not mirror anything.** Report which side it reads as in PIE; the user decides whether the documented intent changes.

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
10. After exiting PIE: run `REN_Validate_WorldLock.py`. The baseline was taken after the section 2a fixes, so the expected result is REVIEW REQUIRED with **only** ADDED `REN_INT_*` actors. Any MISSING, any CHANGED greybox actor (especially `REN_ExitDoor`, which must be back at its closed transform outside PIE), any class/level change, or any DUPLICATE = FAIL. ASSET CHANGE warnings should not occur today. If the differences are only the expected ones, export (writes the candidate), promote it to baseline, and log it in DEVLOG.

## 9. Hand-back

- Commit the Blueprints/UI assets, the updated world-lock + validation report, and `docs/` updates (CURRENT_PROJECT_STATE, TASK_BOARD, DEVLOG).
- In the report, include the step-0 audit answers and `docs/audits/VARIANT_COMBAT_DONOR_AUDIT.md`. The cloud specs for combat and the Face-Eater depend on them.
- Commit the orientation report and the first official Tomb baseline.
