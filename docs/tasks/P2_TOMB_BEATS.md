# Local Task — P2 Tomb Beats (Sprint Day 2)

Execution: **local Unreal + MCP only.** Written in cloud; every step is LOCAL_VALIDATION_REQUIRED.
Task-board IDs: P2-01…P2-04, P0-11, P0-12. No C++. No Sequencer. No Gate of the West or Face-Eater work.

**Goal:** make the Tomb opening feel like an authored game sequence, played entirely through gameplay:

1. wake at the sarcophagus
2. explore the burial chamber
3. examine the Blank Cartouche
4. discover that Nefer has no shadow
5. optional side chamber
6. open the exit
7. walk the tunnel
8. reach the reveal ledge

No blockers, no lore dump, no cinematic overkill.

**Time budget: about half a day (≈4 h core + ≤1.5 h cuttable; audio sourcing deferred).** Each section has a timebox. When a timebox runs out, cut the section's optional parts (see "Cut list") and move on.

Serialize MCP calls: **inspect → edit → compile → save → inspect → PIE test.** Never overlap editor mutations.

## Orientation (built geometry, user-approved)

Facing +Y (the spawn direction), **player-right = −X**:

| Beat | Actor(s) | Side |
|---|---|---|
| Blank Cartouche | `REN_BlankCartouche_Panel` / `_Relief`, +X wall of the burial chamber | **player-LEFT** |
| Offering table + canopic jars | x ≈ −240 | player-right |
| Shadow light | `REN_Light_ShadowTest` at (−130, 900, 250) | player-right |
| Shadow props | Column at x ≈ 95 (player-left); pedestal and jars at x ≈ −70..−35 (player-right) | lane between them: x ≈ −30..72 |
| Shadow wall | `REN_Corridor_Right` (+X, **player-left**) takes the prop shadows | player-left |
| Side clue chamber | opening at y 1020..1320 on −X | **player-RIGHT** |

(Builder-v3 labels `…Left…`/`…Right…` mean map −X/+X; ignore them for player direction.)

## World-lock rules for today

- The Tomb baseline **must already exist** (Day 1, P0-05, with P0-17 resolved). If it's missing, **stop**.
- **Do not move, rotate or scale:** walls, corridor, sarcophagus, cartouche, side-chamber geometry, props, exit, tunnel, reveal ledge, existing lights, existing triggers.
- **Allowed:**
  - property changes on existing actors: light colour, intensity, radius, shadows, material, mobility
  - new actors (`REN_INT_*`, `REN_Light_*`, `REN_Prop_*`, `REN_Audio_*`)
  - components inside REN Blueprints
- **Triggers: reuse before creating** (user direction). Inspect the existing v3 trigger actors first (step 0.6). Reuse any that is correctly located, has suitable bounds and can be safely bound. A new trigger or Box component is created **only** if the existing one is unsuitable, and the reason is recorded. **Never move or rescale an existing world-locked trigger** to fit a Blueprint without approval.

## 0. Prerequisites and audit (read-only) — 15 min

1. `git pull`; `git status` must be clean. Make a **checkpoint commit** (`chore: pre-Day-2 checkpoint`).
2. `python -m unittest discover -s Scripts/Tests` must pass.
3. Open `L_Tomb_Blockout` standalone and run `REN_Validate_WorldLock.py`. It must **PASS**.
4. Confirm these exist from Day 1 and compile cleanly:
   - `BP_NeferCharacter`, `BP_REN_PlayerController` (with `ShowSubtitle(Text, Duration)`), `BP_REN_GameMode`
   - `BPI_Interactable`, `WBP_InteractPrompt`, `WBP_Subtitle`
   - `BP_BlankCartouche` (`REN_INT_BlankCartouche`)
   - `BP_ExitDoor` (`REN_INT_ExitDoor`)
5. Inspect and record the following (they're needed below):
   - `BP_NeferCharacter`: **every** PrimitiveComponent (skeletal meshes, static meshes, attached actors/weapons from the donor), the spring-arm name and `TargetArmLength`, and the camera FOV.
   - Live bounds of `REN_Side_CluePedestal` (top Z) and `REN_Side_WallTablet` (front face X).
   - Current properties of `REN_Light_Burial`, `_ShadowTest`, `_Corridor`, `_Side`, `_DuatReveal`: intensity, radius, Cast Shadows, source radius, mobility.

6. **Existing trigger audit (read-only).** For each of `REN_Trigger_BlankCartouche`, `REN_Trigger_ShadowClue`, `REN_Trigger_SideClue` and `REN_Trigger_ExitReveal`, record the class, the world bounds (from `GetActorBounds`, or BoxExtent × scale) and the collision profile (must overlap Pawn). Then decide REUSE or UNSUITABLE:

   | Trigger | Needed for | REUSE if its bounds (expanded by the ~35 cm capsule radius)… |
   |---|---|---|
   | `REN_Trigger_ShadowClue` | §5c shadow line | cover the whole walkable lane between pedestal and column (x ≈ −30..72) somewhere in y ≈ 880..980, so every player crosses it |
   | `REN_Trigger_ExitReveal` | §8 FOV assist | span the tunnel mouth width (x ≈ −150..150) somewhere in y ≈ 2550..2800 |
   | `REN_Trigger_BlankCartouche` | not needed (the Cartouche uses the P1 interaction trace) | kept as a placeholder; unused today |
   | `REN_Trigger_SideClue` | not needed (the side clue uses the interaction trace) | kept as a placeholder; unused today |

   Record each decision in the hand-back report.

If anything is missing or contradicts this file: **stop and report**.

## 1. Slice world + default map (P0-12, P0-11) — 15 min

1. File → New Level → **Empty Level** (not Open World). Save it as `/Game/REN/Worlds/L_REN_Slice`.
2. Levels window → Add Existing → `L_Tomb_Blockout`. Streaming = **Always Loaded**, identity transform.
3. `L_REN_Slice` World Settings: GameMode Override = `BP_REN_GameMode`.
4. Project Settings → Maps & Modes: Editor Startup Map and Game Default Map = `L_REN_Slice`. This fixes the stale `Lvl_ThirdPerson` config.
5. **All PIE tests today run from `L_REN_Slice`.** World-lock and builders still run on the standalone `L_Tomb_Blockout`.

Failure note: if PIE from the slice spawns at the wrong place, check that exactly one PlayerStart exists (`REN_PlayerStart`) and that the Tomb is Always Loaded.

## 2. Arabic subtitle font (moved from Day 3; needed today) — 20 min

1. Import an OFL Arabic font (e.g. Noto Naskh Arabic, Regular) into `/Game/REN/UI/Fonts/`.
2. Create a Composite Font `F_REN_Subtitle`:
   - default typeface = the existing Latin font
   - add a sub-font with the Arabic character range (U+0600–U+06FF, U+0750–U+077F, U+FB50–U+FDFF, U+FE70–U+FEFF) using the Arabic font
3. `WBP_Subtitle` text uses `F_REN_Subtitle`. Justification: Center. Leave text shaping at the project default.
4. Test with `ShowSubtitle("ده مش تآكل... الاسم اتشال.", 3)`. The letters must be connected and read right to left.

Failure note: if shaping or direction fails within the timebox, use an **English TEMP line** for today and log the issue. Day 3 must solve it (the Anubis dialogue).

## 3. Wake at the sarcophagus — 20 min (assist is cuttable)

**Baseline behaviour (non-negotiable):** the player spawns at `REN_PlayerStart` (0, −350, ~110), facing +Y, with the sarcophagus directly ahead. **Control is available on the first frame.** No cutscene.

**Optional micro-assist** (≤ 1.5 s, control retained), in `BP_NeferCharacter`:

- Variables:
  - `bPlayOpeningAssist` (Bool, instance-editable, default true)
  - `OpeningArmLength` (Float) = 140
  - `DefaultArmLength` (Float), captured at BeginPlay
- BeginPlay, if `bPlayOpeningAssist` and `GetGameMode` → `BP_REN_GameMode.bOpeningPlayed == false`:
  1. Set `bOpeningPlayed = true` (Bool on `BP_REN_GameMode`, default false).
  2. PlayerCameraManager → `StartCameraFade(1 → 0, 1.0 s)`: a fade in from black, for the waking read.
  3. Set the spring-arm `TargetArmLength = OpeningArmLength`, then a **Timeline** `TL_OpeningArm` (1.5 s, ease-out) lerps it back to `DefaultArmLength`.
- **Do not** disable input. **Do not** use a CameraActor.

Failure note: if the arm lerp fights the combat character's camera logic, delete the assist and keep only the fade (or nothing).

## 4. Blank Cartouche — "a personal name was deliberately removed" — 30 min

Extend `BP_BlankCartouche` (from P1):

- New instance-editable variables:
  - `ExamineLine` (Text) = `ده مش تآكل... الاسم اتشال.` — **TEMP**, editable (meaning: "This isn't erosion... the name was removed.")
  - `ExamineLineEN` (Text) = "This isn't erosion... the name was removed." Secondary line; show it if `WBP_Subtitle` supports two lines, otherwise skip.
  - `ExamineSound` (Sound) = **None by default** (nullable; §9)
  - `LineDuration` (Float) = 4.0
- `Interact(Interactor)`:
  1. If `ExamineSound` is valid → `PlaySoundAtLocation` at the relief, volume 0.6.
  2. **Optional face-target (cuttable):** call `BP_NeferCharacter.FaceTarget(ReliefLocation)`:
     - disable movement input
     - Timeline 0.25 s: actor yaw lerps to `FindLookAtRotation(yaw only)`
     - re-enable input after 0.6 s
  3. `ShowSubtitle(ExamineLine, LineDuration)`.
- `GetInteractionPrompt` → "Examine". Repeat interactions are allowed.
- **Optional visual focus (cuttable):** add `REN_Light_CartoucheGrazing`, a new point light at about (330, 110, 330):
  - intensity low (≈ 800), radius 300, warm 2800 K
  - so it rakes across the panel and the cut edge reads in relief
- **No** glow, runes, UI panel or activation effect.

## 5. No-shadow (P2-01) — the major identity beat — 45 min

### 5a. Setup in `BP_NeferCharacter`

- Variable `bHasSheut` (Bool, default **false**). This is the only "state"; it is not a framework.
- Function **`ApplySheutState()`**:
  1. `GetComponentsByClass(PrimitiveComponent)` on self. For each:
     - `SetCastShadow(bHasSheut)`
     - `SetCastHiddenShadow(false)`
     - Cast Contact Shadow = `bHasSheut` (use the `SetCastContactShadow` node if available, otherwise set it in each component's Details)
  2. `GetAttachedActors` (weapons/accessories, including the future Reed Blade) → for each actor, repeat step 1 on its PrimitiveComponents.
- Call `ApplySheutState()` at the end of BeginPlay **and** after anything is attached (e.g. a weapon equip from the donor).
- In the Details panel, also check that the Capsule is Hidden in Game (the template default).

### 5b. Validation — every visual component

Place the player at about (0, 900, 0) under `REN_Light_ShadowTest`, then check each item:

| Check | PASS when |
|---|---|
| Body skeletal mesh | no projected silhouette on the floor or on the player-left wall (`REN_Corridor_Right`) |
| Clothing / hair / accessory meshes (if any) | same |
| Weapon / Reed Blade placeholder (if attached by the donor) | same (a floating blade shadow is a FAIL) |
| Duplicate visual meshes (e.g. a donor "mesh for shadows" component) | none cast a shadow |
| Contact shadows / Lumen screen traces | at most faint foot-contact darkening, no human outline |
| Ray tracing (`r.RayTracing=True` in the project) | if a shadow persists only with RT: set the offending component's **Visible in Ray Tracing = false**, re-test |
| Props | Column, pedestal and jars cast **obvious, crisp** shadows toward the player-left wall/floor |

- **Do not** disable shadows on the light or scene-wide, move the light, or add camera-dependent tricks.
- If the simple method visibly fails after the RT check, **stop and report** with screenshots. Don't build a shadow framework.

### 5c. Shadow-clue staging — `BP_ShadowClue`

Create `/Game/REN/Gameplay/Heka/BP_ShadowClue`, place it at about (0, 940, 100) and label it `REN_INT_ShadowClue`:
- **If `REN_Trigger_ShadowClue` was judged REUSE (step 0.6):** instance-editable `TriggerActor` (Actor ref) → `REN_Trigger_ShadowClue`. In BeginPlay, bind `TriggerActor.OnActorBeginOverlap`. The BP has no volume of its own.
- **Only if UNSUITABLE:** give the BP its own Box component, extent (150, 90, 100), overlapping Pawn only (this covers the full corridor width at the prop lane), and record why the v3 trigger was unsuitable.
- Variables:
  - `Line` (Text) = `...وظلي؟` — **TEMP** (meaning: "...and my shadow?")
  - `LineEN` = "...and my shadow?"
  - `Delay` (Float) = 2.0
  - `bFired` (Bool)
- On BeginOverlap by the player pawn, if `NOT bFired`:
  1. Set `bFired = true`.
  2. Delay by `Delay`.
  3. `ShowSubtitle(Line, 2.5)`.
- No input lock, no popup, no camera change.

### 5d. Light tuning (property changes only)

`REN_Light_ShadowTest`:
- Cast Shadows = true
- **Source Radius 0–2** (crisp shadows)
- Use Temperature, 3000 K
- intensity and radius tuned until the prop shadows are unmistakable on the player-left wall

`REN_Light_Corridor` (fill): lower its intensity if it washes out the clue. Its Cast Shadows may be set false **only if** double prop shadows confuse the read. Record the decision.

## 6. Side clue chamber (player-right, optional) — 40 min

**One strong clue:** a personal-name tablet whose name was **deliberately scraped out**, with the scribal tool that did it lying nearby.

1. **The tablet:** `REN_Side_WallTablet`, on the far −X wall, facing +X. Don't move it.
   - Cuttable: add `REN_Prop_Side_TabletScrape`, a thin box on its front face in the upper third, where a name column would be:
     - about x −871..−869, y 1170..1250, z 200..240, measured against the live front face from step 0.5
     - material `MI_REN_Greybox_Scrape`: dark, rough, desaturated; a REN-owned MI of a simple REN master material; no emissive
   - It reads as a chiselled-away patch, not decay.
2. **The tool:** `REN_Prop_Side_Chisel`, a new StaticMeshActor using the Engine cube, about 3 × 25 × 3 cm.
   - Lay it on top of `REN_Side_CluePedestal` using the live top Z, rotated in yaw only (e.g. 20°).
   - Optionally add `REN_Prop_Side_Scraper`, a flat 8 × 15 × 1 cm piece.
3. **Interaction:** `/Game/REN/Gameplay/Interaction/BP_ExamineClue`, a generic, reusable, minimal Blueprint implementing `BPI_Interactable`:
   - Box component (Visibility = Block only), sized per instance.
   - Instance-editable: `Prompt` (Text, "Examine"), `Line` (Text), `LineEN` (Text), `Sound` (Sound), `Duration` (Float 4.0).
   - `Interact` → optional sound → `ShowSubtitle(Line, Duration)`.
   - Place it over the tablet's front face with a box of about 30 × 140 × 180. Label `REN_INT_SideClue_Tablet`.
   - `Line` = `القطع متعمد.` — **TEMP** (meaning: "The cut is deliberate."). `LineEN` = "The cut is deliberate."
4. **Do not add more lore objects.** No Meru references, no text panels.
5. The chamber stays **optional**. Nothing on the critical path depends on it.

## 7. Exit door weight — 25 min (sound and shake cuttable)

Extend `BP_ExitDoor` (P1). Keep the deterministic 320 cm lowering over 2.5 s:

- Nullable sound hooks (§9): `DoorGrind` (Sound, default None) plays at Timeline start via a spawned/attached audio component and stops at finish, and `DoorThud` (Sound, default None) plays at finish. Both are guarded with `IsValid`.
- **Optional, restrained camera shake:** `/Game/REN/Gameplay/Player/BP_CameraShake_DoorRumble`, a REN-owned duplicate of the template `BP_CameraShake_Hit_Player` with amplitude about 25% and a 2.5 s duration. Start it with the Timeline, scale 0.5, only if the player is within 10 m.
- **Dust:** skip unless a suitable Niagara system already exists in the project. **Do not** author VFX today.
- The door must not be openable twice. The player can't be trapped, because the door moves down and away from the player.

## 8. Reveal — gameplay-first — 25 min (assist cuttable)

**Baseline (non-negotiable):** door → tunnel → ledge, with the **gameplay camera attached to Nefer the whole time.** No cut, no CameraActor, no Sequencer. The composition does the work: the tunnel's framing opens onto the ledge, the piers and the skyline proxies (`REN_DistantTower_A` player-right, `REN_DistantTower_B` player-left, `REN_DistantGate` on the axis). On Day 2 only the proxies are visible; the Necropolis is added on Day 3.

**Optional micro-assist** (≤ 1 s, control retained), `/Game/REN/Gameplay/Player/BP_RevealAssist`, label `REN_INT_RevealAssist`:
- Volume:
  - **If `REN_Trigger_ExitReveal` was judged REUSE (step 0.6):** instance-editable `TriggerActor` → `REN_Trigger_ExitReveal`, bound in BeginPlay.
  - **Only if UNSUITABLE:** give the BP its own Box component, extent (150, 60, 120), at about (0, 2600, 120), and record why.
- On first player overlap:
  1. Timeline 0.8 s, ease-in-out: player camera FOV `Base → Base + 8`.
  2. Hold 6 s.
  3. Ease back over 1.5 s. (A timer, not a second volume.)
- No pitch forcing, no input changes. If it feels like the camera is "doing something", delete it.

## 9. Audio hooks (no sourcing today) — 10 min

User decision: **audio must not block Day 2.** The project has no sound assets, and sourcing is **deferred to the polish pass**.
- Implement hooks only where trivial:
  - `ExamineSound` on the Cartouche / `BP_ExamineClue`
  - `DoorGrind` / `DoorThud` on `BP_ExitDoor`
- **Every Sound variable is nullable.** Guard every play with `IsValid`, and gameplay must work **with no sound assigned**. This is PIE test 13.
- **Don't** search for, download or import audio. **Don't** spend time on audio unless usable assets already exist locally; if they do, assign them to the hooks (≤ 20 min).
- Names reserved for the polish pass (`/Game/REN/Audio/Placeholder/`):
  - `S_REN_StoneSlab_Grind_Loop`, `S_REN_StoneSlab_Thud`
  - `S_REN_StoneScrape_Short`
  - `S_REN_TombAmbience_Loop`
  - `S_REN_Footstep_Stone_01..03`
- No footstep system today. Anim-notify footsteps would require editing template animations, which is forbidden. No music, no "Egyptian" instrument loops.

## 10. Lighting / readability pass — timebox 60 min

These are property changes on existing lights, plus new lights only where stated. **No light is moved.**

| Zone | Light | Target |
|---|---|---|
| Burial chamber | `REN_Light_Burial` | warm practical, ~2700 K, floor, sarcophagus and cartouche readable |
| Shadow clue | `REN_Light_ShadowTest` | section 5d: the strongest directional read in the Tomb |
| Side chamber | `REN_Light_Side` | warm ~2800 K, tablet readable from the doorway |
| Exit tunnel | **new** `REN_Light_Tunnel` at (0, 2350, 330) | cool transition ~7000 K, low intensity |
| Reveal | `REN_Light_DuatReveal` | cool Duat ~9500 K; clear separation from the warm Tomb |

**Exposure:** add an unbound PostProcessVolume `REN_PPV_Slice` to `L_REN_Slice`:
- Metering Mode = **Manual**; tune Exposure Compensation once so the floor reads everywhere (no pumping between the dark Tomb and the bright reveal)
- Bloom ≤ 0.3
- no heavy vignette
- no fog added to hide geometry

**Readability check** (walk the whole route): the player must always read the floor, doors, the path, props and **Nefer's silhouette**. No crushed blacks.

## 11. PIE test order (from `L_REN_Slice`) — PASS/FAIL each

1. **Spawn:** control on frame 1. Any opening assist is ≤ 1.5 s. The sarcophagus is directly ahead.
2. **Burial chamber:** readable. The cartouche wall is on the **player-left**.
3. **Cartouche:** the "E — Examine" prompt shows. One press gives sound (if imported) and the TEMP line, with Arabic rendering correctly. No glow or UI panel.
4. **No-shadow:** every row of the 5b table passes. The props' shadows are obvious and Nefer's is absent, from 3 different camera angles (state survives camera changes).
5. **Shadow line:** `...وظلي؟` appears once, about 2 s after entering the clue zone. Gameplay never stops.
6. **Side chamber:** reachable on the **player-right**. The tablet scrape and chisel read. The TEMP line appears. It's optional: skipping it doesn't block anything.
7. **Exit door:** heavy (grind, thud, optional light shake). Opens once. The prompt disappears. The end Z is exactly −320 from the start.
8. **Tunnel → ledge:** the camera stays gameplay-attached, with no cut. Any FOV assist is ≤ 1 s and subtle. Control is never lost.
9. **Reveal read:** tunnel cool, exterior cool. The towers and gate proxies read as landmarks.
10. **Readability:** no crushed blacks or exposure pumping anywhere along the route.
11. **Log:** no "Accessed None" or Blueprint errors during a full run.
12. **Timing:** record two runs, one direct and one exploring everything. **Target: 4–7 meaningful minutes. Do NOT pad.** The cloud estimate for current content is about 3–4.5 min. Report the real numbers.
13. **No-audio run:** with every Sound variable empty, the full route plays with no errors or "Accessed None".

## 12. World-lock close-out

1. Open `L_Tomb_Blockout` standalone and run `REN_Validate_WorldLock.py`.
   - **Expected:** REVIEW REQUIRED with **only ADDED** `REN_INT_*`, `REN_Light_Tunnel`, optional `REN_Light_CartoucheGrazing`, `REN_Prop_Side_*`, `REN_Audio_*`.
   - **FAIL:** any MISSING, any CHANGED (transform, class or level), any DUPLICATE. That means unexplained drift. Find it and revert it.
   - Note that light *property* changes are not tracked by world-lock; only transforms, classes, meshes and levels are.
2. If only the expected additions appear: export (writes the candidate), review it with `python Scripts/Editor/REN_WorldLock_Core.py <baseline> <candidate>`, promote it to the baseline, and log it in DEVLOG.

## 13. Rollback / failure notes

- Checkpoint commit first (step 0). Any section that breaks compilation → revert that asset from Git rather than patching blind.
- **No-shadow fails:** do the RT check (5b). If it still fails → stop, report screenshots, and don't build a framework.
- **Arabic fails:** English TEMP lines today; fix on Day 3.
- **Camera assist fights the donor camera:** delete the assist. The baseline behaviour is enough.
- **Audio:** hooks are nullable. Nothing depends on sound being assigned.
- **Validation shows unexplained drift:** don't promote. Revert the moved actor to its baseline transform (from the JSON) and re-validate.

## 14. Hand-back

- Commit assets (LFS), the promoted Tomb baseline and validation report, and `docs/` updates (CURRENT_PROJECT_STATE, TASK_BOARD, DEVLOG).
- The report must include:
  - section 11 PASS/FAIL results with the two timings
  - a no-shadow screenshot showing props casting shadows while Nefer casts none
  - an Arabic subtitle screenshot
  - what was cut
  - the light property values chosen

## Cut list (cut from the top when a timebox runs out)

1. Door camera shake
2. Reveal FOV assist
3. Opening arm assist (keep the fade or nothing)
4. Cartouche face-target turn
5. Cartouche grazing light
6. Side-tablet scrape mesh (keep the chisel + line)

(Audio is not on this list: only nullable hooks are built today, and sourcing is deferred.)

**Never cut:**
- spawn with instant control
- the cartouche examine line
- no-shadow with validation
- shadow-clue staging and light tuning
- the side-chamber interaction
- heavy deterministic door (nullable sound hooks)
- gameplay-camera reveal
- exposure stability
- world-lock validation
