# REN — 7-Day Pre-Alpha Sprint

Created: 2026-09-30 (cloud). Owner decision: **quality over duration.**
Revision 2 (2026-09-30): user-approved with corrections 1–7 (world-lock purpose, baseline gating, skyline proxies, Variant_Combat as donor, no-shadow validation, Nameless Dead direction, Git LFS). The persistent slice world is approved.

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

1. **Variant_Combat is a DONOR, not unquestioned architecture** (approved for speed).
   - Before any duplication, the local Day-1 donor audit (`docs/audits/VARIANT_COMBAT_DONOR_AUDIT.md`) covers `BP_CombatCharacter`, `BP_CombatPlayerController`, `BP_CombatGameMode`, `BP_CombatEnemy`, StateTree dependencies, damage interfaces, animation assumptions, hardcoded references, level dependencies and UI dependencies.
   - Template assets are **never** edited in place. Required assets are duplicated into `/Game/REN/`, and every hardcoded reference is retargeted.
   - The player is `BP_NeferCharacter`, duplicated from `BP_CombatCharacter`. We add interaction, dodge and no-shadow.
   - Fallback: if the combat character plays badly in the tight Tomb, duplicate `BP_ThirdPersonCharacter` for Day 1–3 instead, and port the combat on Day 4.
2. **Enemies.** `BP_NamelessDead` is duplicated from `BP_CombatEnemy`, per `docs/NAMELESS_DEAD_SPEC.md`: one family, real humans, not undead.
   - **Face-Eater is NOT simply `BP_CombatEnemy` scaled to 3.8 m.** That is acceptable only as the first placeholder.
   - The generic enemy and StateTree may supply target acquisition, locomotion, basic approach and damage plumbing.
   - **Boss phase authority belongs to an explicit REN state machine**, `E_FaceEaterState` (Dormant, Intro, Combat, Exposed, Staggered, Defeated), owned by `BP_FaceEater`.
   - The generic StateTree must never override the phase. It runs only in Combat, and is stopped or paused in every other state. Damage acceptance is gated by the REN state.
   - The prototype still needs boss-specific work: capsule/collision review, attack ranges, animation timing, damage gating, Glyph interaction, the Exposed state and chest-seal vulnerability. This is spec'd in the P4 task; **not started yet**.
3. **Interaction is minimal.** It is `BPI_Interactable` with 3 functions and one trace that starts from the camera and is projected forward past the player. See `docs/tasks/P1_INTERACTION_FOUNDATION.md`. There is no generic interaction framework.
4. **The world is one persistent level with always-loaded sublevels** (APPROVED for the vertical slice; a known temporary solution, not necessarily the final shipping architecture; no streaming framework, no loading screens).
   - `L_REN_Slice` is a new non-World-Partition persistent level containing `L_Tomb_Blockout`, `L_Necropolis_Blockout` and `L_GateWest_Blockout`, all *Always Loaded*.
   - Why:
     - The Necropolis reveal looks at the real Necropolis, so the camera moves and the world does not.
     - There is no load or transition code.
     - Each area is its own binary file, so cloud-written builders and local work don't collide in Git.
   - Streaming volumes come only if profiling demands them.
   - Builders and world-lock scripts always run on the **standalone-opened sublevel map**, never inside the persistent level.
5. **All sublevels share one world coordinate system.**
   - +Y points toward the Duat, as in builder v3. The Necropolis starts beyond the Tomb reveal ledge (Y > 2975). The Gate of the West lies at y ≈ 5250+, beyond the Necropolis plaza.
   - Unreal is left-handed: facing +Y, **player-right = −X**. The details are in `docs/NECROPOLIS_GREYBOX_SPEC.md` §1.
   - The Tomb's `REN_DistantTower_A/B` and `REN_DistantGate` are **skyline proxies**. They are never duplicated; new areas build around and below them.
6. **Cinematics are minimal and not Sequencer.**
   - The Tomb wake and the Necropolis reveal are **gameplay-first**: the camera stays attached to Nefer, with optional ≤ 1–1.5 s arm/FOV assists and control retained (user direction, 2026-09-30).
   - Only the Anubis exchange uses a fixed `CameraActor` with `Set View Target with Blend`.
   - Sequencer is out of scope unless Day 6 has slack.
7. **Checkpoints and restart use `BP_Combat_CheckpointVolume`** from the template. There is no save system.
8. **UI** is `WBP_InteractPrompt`, `WBP_Subtitle`, the template `UI_LifeBar` (player), and one boss bar. That is all.
9. **No-shadow uses `Cast Shadow = false`** (approved for the sprint). Local validation must inspect **all** player visual components:
   - body skeletal mesh
   - clothing meshes
   - Reed Blade (when added)
   - accessories
   - capsule, contact-shadow and Lumen/VSM artifacts
   Success means Nefer produces no recognisable projected human shadow while nearby props cast obvious, correct shadows. There is no shadow framework unless the simple solution visibly fails.
10. **Heka for the slice is one mechanic.** Glyph pillars in the Face-Eater arena are `BPI_Interactable`. Interacting during the boss's recovery window exposes the chest seal. There is no spell system.

11. **World-lock protects spatial continuity.**
    - Location, rotation and scale changes, missing, added or duplicate actors, class changes and level-ownership changes are **failures**.
    - A mesh swapped at the same transform (greybox → final art) is an **asset change**: a warning by default, a failure only with `--strict-assets` / `STRICT_ASSETS = True`.
    - The first official Tomb baseline is exported only **after** the local orientation check confirms or fixes `REN_PlayerStart` and `REN_BlankCartouche_Relief`, and traversal passes.
12. **Git LFS is forward-only** for `*.uasset`/`*.umap` (`.gitattributes`). There is no history rewrite or migration of old commits. Every local machine runs `git lfs install` once.

Temporary shortcuts must be listed in `docs/CURRENT_PROJECT_STATE.md` under "Known temporary solutions".

## Day plan

Each day has a **local** track (the user in Unreal with MCP) and a **cloud** track that prepares the next local day. A day is done only when its exit criteria pass in PIE.

### Day 1 — Foundation + interaction
- Local:
  - `git lfs install`.
  - Check the Python plugin (P0-09).
  - Donor audit.
  - **Orientation check → fix only confirmed errors → PIE traversal (P0-06) → THEN the official Tomb baseline (P0-05).**
  - Configure MCP (P0-07).
  - Execute `docs/tasks/P1_INTERACTION_FOUNDATION.md`.
- Cloud: DONE early. The Necropolis + Anubis package is ready (`docs/NECROPOLIS_GREYBOX_SPEC.md`, builder v1, `docs/tasks/P2_NECROPOLIS_ANUBIS.md`), along with `docs/NAMELESS_DEAD_SPEC.md`.
- Exit: in the Tomb, interact with the Cartouche and the Door, then walk to the reveal ledge. The official Tomb baseline is committed.

### Day 2 — Tomb beats complete (Tier A content, greybox art)
- Local: execute `docs/tasks/P2_TOMB_BEATS.md` (≈4 h core + ≤2 h cuttable):
  - `L_REN_Slice`
  - the Arabic subtitle font
  - wake with instant control
  - Cartouche examine
  - no-shadow with full component validation, plus shadow-clue staging
  - the one-clue side chamber (player-right)
  - heavy door
  - **gameplay-first reveal (no cut, no CameraActor, no Sequencer)**
  - light/exposure pass
  - audio placeholders (user-sourced)
- Cloud: `docs/tasks/P2_TOMB_BEATS.md` DONE. Next: Gate of the West + arena builder (C-03) and the P3 combat spec (C-04), once approved.
- Exit: 0–8 minutes play end-to-end with no blockers. The no-shadow validation (decision 9) passes for all player visual components.

### Day 3 — Necropolis + Anubis
- Local: execute `docs/tasks/P2_NECROPOLIS_ANUBIS.md`:
  - builder → sublevel
  - Glyph teaching moment
  - shadow tease
  - fall recovery
  - still Anubis placeholder with the Arabic subtitle exchange and a fixed camera
- Cloud: P4 Face-Eater spec (states, attacks, telegraph timings, glyph mechanic).
- Exit: walk from the Tomb to the Gate approach in one session with no loading.

### Day 4 — Gate of the West + first combat (≈ one workday)
- Local:
  - Part 1: `docs/tasks/P3_GATE_WEST.md` (≈2–2.5 h). GateWest builder (59 actors), the runtime Gate sink (property changes only on `REN_DistantGate`), checkpoints, light pass, and the arena **shell** (markers only).
  - Part 2: `docs/tasks/P3_FIRST_COMBAT.md` (≈4–5 h).
    - A donor-audit gate (A1–A10) and decision D1 (child vs duplicate).
    - The donor attack chain, a `BP_NamelessDead` TEMP placeholder, death → checkpoint restart, and an encounter controller with reset plus combat-gate unlock.
    - Camera checks.
    - Dodge **only if needed for fairness**.
- Cloud: C-03/C-04 DONE early. Next: the P4 Face-Eater spec (C-05), once approved. Audio sourcing is deferred to polish.
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
| Builder v3 cleanup deletes **all** `REN_` actors in loaded levels | v3 now refuses to run unless the open world is `L_Tomb_Blockout`. New builders use their own prefixes (`REN_NEC_`, `REN_GW_`) and refuse if foreign REN actors are loaded |
| Locking a bad Tomb transform | Read-only orientation check + fix only confirmed errors before the first baseline |
| Left/right docs vs geometry (player-right = −X) | RESOLVED: Tomb kept as built. Cartouche is player-left, side chamber player-right |
| Floating Tomb props (code reading) → detached shadows in the no-shadow beat | Measure on Day 1. Z-only fix before baseline, with user approval (P0-17) |
| Tomb shorter than 4 min | Accepted if the beats are good; measured on Day 2. No padding |
| No audio assets in project | User decision: nullable hooks only; sourcing deferred to the polish pass |
| Duplicated donor classes break donor casts (StateTree, notifies, UI) | Decision D1: use child Blueprints where the audit finds casts. Templates are still never edited |
| Visual drift toward template mannequins | Reference manifest rule (`.claude/rules/visual-references.md`); all characters `TEMP_PLACEHOLDER` until masters exist |
| Gate sink via cross-level tag lookup fails | Report; never move `REN_DistantGate` between levels without approval |
| Arabic subtitles render as boxes | Import an OFL Arabic font; composite font in `WBP_Subtitle` (Day 3 task §6) |
| Generic StateTree fights the boss phase logic | REN state machine owns the phase; StateTree runs only in Combat |
| Necropolis shorter than its 8-minute bracket (≈2.5–4.5 min) | Accepted; no padding (quality over duration) |
| Actors land in the wrong sublevel | Builders run only on standalone-opened sublevel maps; manual placement uses the Levels panel current-level check |
| Binary map merge conflicts | One area per map; never edit the same map in two sessions |
| Timeline slip | Apply the cut order; never trade Tier A polish for duration |
