# Local Task — Vertical Necropolis + Anubis (Sprint Day 3)

Execution: **local Unreal + MCP only.** Written in cloud; every step is LOCAL_VALIDATION_REQUIRED.
Design: `docs/NECROPOLIS_GREYBOX_SPEC.md`. Builder: `Scripts/Editor/REN_Necropolis_Greybox_Builder_v1.py`.
Task-board IDs: P2-05, P5-01, P0-12 (if not done on Day 2).

Serialize MCP calls: inspect → mutate → compile/save → inspect. Never edit `Variant_Combat` or other template assets in place.

## 0. Preconditions and audit (no edits)

1. `git pull`, then `git status` must be clean. Confirm `git lfs install` has been run on this machine (`git lfs env` shows hooks).
2. Run the offline tests: `python -m unittest discover -s Scripts/Tests`. They must all pass.
3. These must already exist from Day 1–2. If any is missing, **stop** and finish that first:
   - `BPI_Interactable`, the trace/focus in `BP_NeferCharacter`, `WBP_InteractPrompt`, and `WBP_Subtitle` with `ShowSubtitle(Text, Duration)` on `BP_REN_PlayerController`
   - `BP_ExitDoor`, whose sinking-slab Timeline pattern is reused here
   - Nefer no-shadow (Day 2, P2-01)
   - The official Tomb baseline `ProjectDocs/WorldLocks/L_Tomb_Blockout.worldlock.json`
4. Validate the Tomb: open `L_Tomb_Blockout` standalone and run `REN_Validate_WorldLock.py`. Expected result: PASS.
5. Report what the persistent slice level looks like: does `L_REN_Slice` exist, and which sublevels are in it?

## 1. Create and build the Necropolis sublevel

1. Create folder `/Game/REN/Worlds/Necropolis/`.
2. File → New Level → **Empty Level** (not Open World; it must not use World Partition). Save it as `/Game/REN/Worlds/Necropolis/L_Necropolis_Blockout`.
3. With **only** `L_Necropolis_Blockout` open, run `Scripts/Editor/REN_Necropolis_Greybox_Builder_v1.py`.
   - Expected log: `REN Necropolis Greybox Builder v1 COMPLETE`, `Spawned: 210 | REN_NEC_ actors now in level: 210 (expected 210)`, and no warnings.
   - If it refuses (wrong world, foreign REN actors, or layout validation), report the message verbatim. Do not work around it.
4. Visual check in the editor viewport (read-only):
   - No floating steps.
   - The Outliner folders `REN_NEC/Geometry`, `/Mechanisms`, `/Blockers`, `/Dressing`, `/Triggers`, `/Markers` and `/Lights` exist.
   - `REN_NEC_GlyphSeal_Slab` has Mobility = Movable.
   - `REN_NEC_Ledge_InvisWall_Front` and `REN_NEC_S1_InvisWall_PX` are Hidden in Game.
5. Save.

## 2. Compose into the slice world

1. Open `L_REN_Slice` (create it if Day 2 didn't: Empty Level at `/Game/REN/Worlds/L_REN_Slice`, with `L_Tomb_Blockout` added).
2. Levels window → Add Existing → `L_Necropolis_Blockout`. Set Streaming Method = **Always Loaded**. Check that the level transform is **identity** (no offset).
3. `L_REN_Slice` World Settings: GameMode Override = `BP_REN_GameMode`.
4. Visual check: S1's top meets the Tomb ledge front. The tower foundations continue the Tomb towers downward without seams or offsets. The gate plinth sits under `REN_DistantGate`.
5. **Never run a builder while `L_REN_Slice` is open.** The builders refuse anyway.

## 3. Glyph mechanism (teaches the Face-Eater glyph mechanic)

`/Game/REN/Gameplay/Heka/BP_GlyphMechanism`, implementing `BPI_Interactable`:
- Root: a Box Collision about 40 × 180 × 280 cm, **Visibility = Block**, everything else Ignore (same pattern as the Blank Cartouche).
- Instance-editable `SlabActor` (Actor ref) → `REN_NEC_GlyphSeal_Slab`. It's in the same sublevel, so there is no cross-level reference.
- `SinkDistance` = 460. `bUsed` = false.
- `CanInteract` → `NOT bUsed`. `GetInteractionPrompt` → "Read".
- `Interact`:
  - `bUsed = true`.
  - Optional: swap the panel's material to a REN-owned dark "ink-filled" material instance for grooves filling with ink. Restrained, no glow.
  - `ShowSubtitle` with a TEMP line (editable, not canon), 3 s. Placeholder: *"Words cut in stone. They remember how to open."*
  - Timeline, 3.0 s ease-in-out: the slab's Z drops by `SinkDistance` from its start Z. The end state is deterministic.
- Place it over `REN_NEC_GlyphPanel` (about (245, 4500, −400)) inside `L_Necropolis_Blockout`. Label: `REN_INT_NEC_Glyph`.

## 4. Independent-shadow tease

`/Game/REN/Gameplay/Heka/BP_ShadowTease`:
- A SkeletalMeshComponent with `SKM_Manny_Simple` (or Quinn):
  - **Visible = false** (Hidden in Game), **Cast Hidden Shadow = true**, Cast Shadow = true
  - no collision
  - animation mode Single Node, `MF_Unarmed_Walk_Fwd`, looping
- Instance-editable `EndPoint` (Actor ref) → `REN_NEC_Marker_ShadowWalk_End`, and `TriggerActor` → `REN_NEC_Trigger_ShadowTease`.
- On the trigger's BeginOverlap by the player pawn, **once**:
  1. Face the end point.
  2. Move to it over about 4 s (Timeline lerp of actor location).
  3. Hide the component, or set Cast Hidden Shadow = false.
- Place it at `REN_NEC_Marker_ShadowWalk_Start` (−760, 3780, −600), facing −X (toward the end point). Label: `REN_INT_NEC_ShadowTease`.
- Lighting: `REN_NEC_Light_ShadowTease` must cast a clear shadow on Tower A's −Y face. Tune its intensity and cone only. **Do not move the light or the tower.**
- If Lumen/VSM makes the hidden-shadow read poorly, report it with a screenshot before trying alternatives. The fallback is an animated decal, a Day-6 decision.

## 5. Fall recovery (Necropolis only)

`/Game/REN/Gameplay/Checkpoints/BP_FallRecovery`:
- Instance-editable `TriggerActor` → `REN_NEC_Trigger_FallRecovery`, and `RespawnPoints` (array) → `REN_NEC_Respawn_Ledge`, `_Court`, `_BridgeHead`.
- On player overlap:
  1. Camera fade out (0.25 s).
  2. Teleport to the respawn point **nearest in XY** to the player's current location, using its rotation.
  3. Fade in.
- Label: `REN_INT_NEC_FallRecovery`. Not the Level Blueprint.

## 6. Anubis placeholder encounter (no fight, no animation set)

### Placeholder actor

`/Game/REN/Characters/Gods/Anubis/BP_AnubisPlaceholder`:
- Capsule: radius 40, half-height 105, blocks the pawn.
- Skeletal mesh `SKM_Manny_Simple`, scaled to about 2.05 m tall, playing `MM_Idle` at **play rate 0.0**, so it holds the first frame.
- Materials: a REN-owned off-white linen material instance on the body.
- A **black, elongated jackal-head proxy** (engine shapes attached to the head socket).
  - Tall, lean and dignified.
  - No gold spam, no muscular exaggeration, no glowing eyes.
  - This is a placeholder only; the art pass replaces it at the same transform. Label it **`TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`**: in the asset description, and with an editor-only TextRender (Hidden in Game).
  - Visual authority comes from `ProjectDocs/References/REFERENCE_MANIFEST.md` once present. Never reshape Anubis toward the mannequin.
- Place it at `REN_NEC_Marker_Anubis` (0, 4950, 0), facing −Y (yaw −90). Label: `REN_INT_NEC_Anubis`.

### Encounter logic

`/Game/REN/Gameplay/Interaction/BP_AnubisEncounter`, one actor, label `REN_INT_NEC_AnubisEncounter`. References (all in the same sublevel):
- `SlowTrigger` → `REN_NEC_Trigger_AnubisSlow`
- `DialogueTrigger` → `REN_NEC_Trigger_AnubisDialogue`
- `EncounterCamera` → a new **CameraActor** `REN_CAM_NEC_Anubis` at about (−160, 4520, 170), aimed at Anubis's head (about (0, 4950, 220)), FOV about 40
- `bDone` flag

Slow trigger (player enters):
- Store the player's MaxWalkSpeed, then set it to about 180 cm/s.
- Disable jump if trivial; otherwise skip that.
- **Only slow if needed.** If the unslowed walk reads well, leave this off and write that down.

Dialogue trigger (player enters, `NOT bDone`):
1. `bDone = true`. Disable player movement input (camera look may stay).
2. `Set View Target with Blend` → EncounterCamera, 1.0 s, cubic.
3. Subtitles (Arabic primary, English secondary line; editable script, not canon):
   - Anubis: "اسمك." / *"Your name."*, 2.5 s, then a 1.0 s pause
   - Nefer: "مش فاكر." / *"I don't remember."*, 2.5 s, then a 1.5 s pause
   - Anubis: "يبقى حد قتلك مرتين." / *"Then someone killed you twice."*, 3.5 s
4. Blend back to the player pawn (1.0 s). Re-enable input. Restore MaxWalkSpeed.
5. Anubis **does not move**. The player walks past him (150 cm of clearance on each side).

### Arabic text

The Arabic subtitle font `F_REN_Subtitle` is set up on **Day 2** (`docs/tasks/P2_TOMB_BEATS.md` §2).
- If Day 2 fell back to English, fix it here first: import an OFL Arabic font and give the Composite Font an Arabic sub-font range.
- In PIE, check that the letters are connected and the text reads right-to-left. Screenshot it.

## 7. Acceptance tests (PIE from `L_REN_Slice`) — report each PASS/FAIL

1. Continuous run from `REN_PlayerStart` through the Tomb, the ledge, the Necropolis and the gate plaza, with no loading.
2. From the ledge, the Gate is centred and framed by Tower A (player-right) and Tower B (player-left). The Bridge Head is visible across the gap.
3. A running jump from the ledge or the top of S1 cannot reach the Bridge Head.
4. S1 and S2 are walkable up and down without snagging. There are no ledge-edge falls anywhere along the route.
5. The shadow tease triggers once. A human shadow crosses Tower A's face while nobody is visible. **Nefer casts no shadow in the same light.**
6. The Glyph shows the "E — Read" prompt. One press sinks the slab (3 s). A second press does nothing. The slab ends exactly 460 cm lower.
7. The slab cannot be bypassed:
   - try jumping onto the wall
   - try walking along the court parapet around the corner wall
   - try any diagonal jump from the court into the landing
   Report any bypass with coordinates.
8. Falling into the void anywhere triggers the fade and a respawn at the nearest respawn point, facing +Y.
9. The Anubis dialogue plays once. The camera blends in and out smoothly. Input returns. Anubis never moves. Arabic renders correctly.
10. Walk past Anubis to the plaza. The gate and its wings block further progress (GateWest is not built yet).
11. No "Accessed None" or Blueprint errors in the Output Log.
12. Measure and record the playthrough time from the ledge to the plaza. The expected range is 2.5–4.5 minutes.

## 8. World-lock (only after section 7 passes)

1. Open `L_Necropolis_Blockout` **standalone**. Run `REN_Export_WorldLock.py`, which writes the first Necropolis baseline. Commit it.
2. Open `L_Tomb_Blockout` standalone and run `REN_Validate_WorldLock.py`. Expected: PASS, or only the reviewed differences.
3. Don't export world-locks while `L_REN_Slice` is open. The per-sublevel baselines are the reference.

## 9. Hand-back

- Commit the new REN assets (LFS), the Necropolis baseline and validation reports, and `docs/` updates (CURRENT_PROJECT_STATE, TASK_BOARD, DEVLOG).
- The report must include:
  - the section 7 results and the measured time
  - any bypass coordinates
  - shadow-tease screenshots
  - an Arabic subtitle screenshot
  - the Anubis framing screenshot
