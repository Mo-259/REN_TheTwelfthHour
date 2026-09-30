# REN — 7-Day Pre-Alpha Sprint

Created: 2026-09-30 (cloud). Owner decision: **quality over duration.**

Goal: a playable pre-alpha of ~30 minutes, where **0–8 min (Tomb) and the Face-Eater encounter get the highest polish**. If the choice is 30 mediocre minutes or 10–15 excellent minutes plus rough playable content, choose the latter.

## Honest duration estimate

A greybox of the current Tomb takes about 2–3 minutes to walk through. Minutes come from pacing, observation and encounters, not from corridor length. A realistic first-time playthrough at end of sprint is **15–25 minutes**. Don't pad the time with empty traversal. Report the measured playtime on Day 7.

## Content map and polish tiers

| Time | Section | Tier | Sublevel |
|---|---|---|---|
| 0–8 | Tomb of No Name: wake, Blank Cartouche, no-shadow, side chamber, exit, reveal | **A (polish)** | `L_Tomb_Blockout` (exists) |
| 8–16 | Vertical Necropolis traversal + Anubis | B (clean, rough art) | `L_Necropolis_Blockout` (new) |
| 16–22 | First combat: Nameless Dead | C (rough but fair) | `L_GateWest_Blockout` (new) |
| 22–30 | Gate of the West + Face-Eater | **A (polish)** | `L_GateWest_Blockout` (new) |

Tier A: lighting pass, camera tuning, audio placeholders, telegraphs, zero known bugs.
Tier B: readable route, no blockers, placeholder art OK.
Tier C: playable, fair, can restart; visual placeholders OK.

## Architecture decisions for the sprint (fastest path)

1. **The player is built from the template's combat character.** Duplicate `/Game/Variant_Combat/Blueprints/BP_CombatCharacter` → `/Game/REN/Gameplay/Player/BP_NeferCharacter`. We get the combo attack, charged attack, damage interfaces and life bar for free. We add interaction, dodge and the no-shadow setting. Template assets are never edited in place.
   - Fallback: if the combat character plays badly in the tight Tomb, duplicate `BP_ThirdPersonCharacter` for Day 1–3 instead, and port the combat on Day 4.
2. **Enemies are built from the template's combat enemy.** Duplicate `BP_CombatEnemy` → `BP_NamelessDead`. Face-Eater starts from a duplicate as well (`BP_FaceEater`), scaled to ~3.8 m, with an explicit state enum (`E_FaceEaterState`) that gates damage and phase. The template StateTree is kept for movement and attack selection. Nothing is rebuilt from scratch.
3. **Interaction is minimal.** It is `BPI_Interactable` with 3 functions and one trace that starts from the camera and is projected forward past the player. See `docs/tasks/P1_INTERACTION_FOUNDATION.md`. There is no generic interaction framework.
4. **The world is one persistent level with always-loaded sublevels.**
   - `L_REN_Slice` is a new non-World-Partition persistent level containing `L_Tomb_Blockout`, `L_Necropolis_Blockout` and `L_GateWest_Blockout`, all *Always Loaded*.
   - Why:
     - The Necropolis reveal looks at the real Necropolis, so the camera moves and the world does not.
     - There is no load or transition code.
     - Each area is its own binary file, so cloud-written builders and local work don't collide in Git.
   - Streaming volumes come only if profiling demands them.
   - Builders and world-lock scripts always run on the **standalone-opened sublevel map**, never inside the persistent level.
5. **All sublevels share one world coordinate system.** +Y points toward the Duat, as in builder v3. The Necropolis starts beyond the Tomb reveal ledge (Y > 2975), and the Gate of the West lies beyond the Necropolis. Coordinates are defined in each builder header.
6. **Cinematics are camera actors, not Sequencer.** Reveal and Anubis framing use `Set View Target with Blend` to a fixed `CameraActor`, then return control. Sequencer is out of scope unless Day 6 has slack.
7. **Checkpoints and restart use `BP_Combat_CheckpointVolume`** from the template. There is no save system.
8. **UI** is `WBP_InteractPrompt`, `WBP_Subtitle`, the template `UI_LifeBar` (player), and one boss bar. That is all.
9. **No-shadow is a single mesh setting.** On `BP_NeferCharacter` the Mesh has `Cast Shadow = false`. The design work goes into lighting the clue zone, not into code.
10. **Heka for the slice is one mechanic.** Glyph pillars in the Face-Eater arena are `BPI_Interactable`. Interacting during the boss's recovery window exposes the chest seal. There is no spell system.

Temporary shortcuts must be listed in `docs/CURRENT_PROJECT_STATE.md` under "Known temporary solutions".

## Day plan

Each day has a **local** track (the user in Unreal with MCP) and a **cloud** track that prepares the next local day. A day is done only when its exit criteria pass in PIE.

### Day 1 — Foundation + interaction
- Local:
  - Export the world-lock baseline for Tomb (P0-05), check the Python plugin (P0-09), play the Tomb in PIE (P0-06).
  - Configure MCP (P0-07).
  - Execute `docs/tasks/P1_INTERACTION_FOUNDATION.md`, covering the Nefer character, IMC, interface, trace, prompt, subtitle, Blank Cartouche and Exit Door.
- Cloud: Necropolis + Anubis greybox builder (`REN_Necropolis_Greybox_Builder_v1.py`) and the P2 Tomb-beats spec.
- Exit: in the Tomb, interact with the Cartouche and the Door, then walk to the reveal ledge.

### Day 2 — Tomb beats complete (Tier A content, greybox art)
- Local:
  - No-shadow setting plus clue-zone light tuning.
  - Side clue interactables.
  - Sarcophagus wake start.
  - Exit reveal camera.
  - Create `L_REN_Slice` and add the Tomb sublevel.
- Cloud: Gate of the West + arena builder, and the P3 combat spec.
- Exit: 0–8 minutes play end-to-end with no blockers. The no-shadow clue is readable without a tutorial.

### Day 3 — Necropolis + Anubis
- Local:
  - Run the Necropolis builder and add it as a sublevel.
  - Traversal pass.
  - Anubis placeholder NPC (a still mannequin) with a proximity trigger, subtitle exchange and a view-target shot.
- Cloud: P4 Face-Eater spec (states, attacks, telegraph timings, glyph mechanic).
- Exit: walk from the Tomb to the Gate approach in one session with no loading.

### Day 4 — First combat
- Local:
  - `BP_NamelessDead` (from `BP_CombatEnemy`).
  - Dodge (`IA_Dodge`, a simple launch or root-motion-free dash with brief invulnerability).
  - One or two small encounters, a checkpoint, and death → restart.
  - Run the GateWest builder.
- Cloud: audio placeholder list, Tomb lighting pass spec, and a review of recorded issues.
- Exit: the fight is fair, restart works, and the player never soft-locks.

### Day 5 — Face-Eater core loop
- Local:
  - `BP_FaceEater` with `E_FaceEaterState` (Dormant, Intro, Combat, Exposed, Staggered, Defeated).
  - Hook sweep, heavy strike, recovery window, glyph pillars → Exposed → chest-seal damage.
  - Boss bar, and a defeat → Ren-glyph reward beat → end card.
- Cloud: bug triage and polish checklists.
- Exit: the boss can be beaten the intended way, cannot be cheesed by normal attacks alone, and restart works.

### Day 6 — Polish Tier A (Tomb + Face-Eater)
- Local:
  - Lighting, exposure and camera distance.
  - Telegraph clarity.
  - Hit feedback.
  - Placeholder SFX: stone, door mass, staff impact, ambience.
  - Simple Egyptian greybox kit dressing (flat reliefs, cartouche shape, pillars). No neon, no floating runes.
- Exit: Tier A sections have no known bugs, and every QA_ACCEPTANCE item for them passes.

### Day 7 — Lock + ship the pre-alpha
- Feature freeze by midday.
- Three full playthroughs with timing recorded.
- Fix blockers only.
- Package a Development build.
- Update the world-locks and docs.
- Exit: a packaged build starts at the Tomb and reaches the end card.

## Cut order (if behind schedule)

Cut from the top first. The items under "never cut" stay regardless.

1. Anubis view-target shot. The subtitle exchange alone is enough.
2. Second Nameless Dead encounter. Keep one.
3. Necropolis side branches. Keep the main route.
4. Grab attack on Face-Eater. Keep sweep + heavy strike.
5. Dodge i-frames polish. Keep a basic dash.
6. Sarcophagus interaction. Replace with a wake start at the sarcophagus.

Never cut:
- Blank Cartouche, the no-shadow clue, Exit Door and the reveal.
- The Face-Eater glyph → Exposed → chest-seal loop.
- Restart that doesn't soft-lock.

Fallback if the glyph mechanic slips: Exposed triggers after a stagger from N hits during recovery, with the glyph restored on Day 6.

## Risks

| Risk | Mitigation |
|---|---|
| The user is new to Unreal, so the local track is the bottleneck | Cloud writes exact step lists and builders a day ahead; each task has PIE tests |
| Behaviour inside the template combat character is unknown from the cloud | The Day-1 local audit of `BP_CombatCharacter`, `BP_CombatPlayerController` and `IMC_Combat` comes before any change |
| Builder v3 cleanup deletes **all** `REN_` actors in loaded levels | v3 now refuses to run unless the open world is `L_Tomb_Blockout`. New builders use their own prefixes (`REN_NEC_`, `REN_GW_`) |
| Actors land in the wrong sublevel | Builders run only on standalone-opened sublevel maps; manual placement uses the Levels panel current-level check |
| Binary map merge conflicts | One area per map; never edit the same map in two sessions |
| Timeline slip | Apply the cut order; never trade Tier A polish for duration |
