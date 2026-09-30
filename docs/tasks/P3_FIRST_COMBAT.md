# Local Task — P3 First Combat (Sprint Day 4, part 2)

Execution: **local Unreal + MCP only.** Written in cloud; every step is LOCAL_VALIDATION_REQUIRED.
Design and decisions: `docs/IMPLEMENTATION_P3_COMBAT.md` (read it first). Enemy direction: `docs/NAMELESS_DEAD_SPEC.md`. Space: `docs/tasks/P3_GATE_WEST.md` must be done (part 1).
Task-board: P3-01…P3-07. **Timebox: about 4–5 h.** No Face-Eater, no C++, no Sequencer. **Never edit `/Game/Variant_Combat/` assets.**

Serialize MCP calls: **inspect → edit → compile → save → inspect → PIE test.**

## 0. Preconditions — 20 min

1. `git status` clean. Make a checkpoint commit.
2. **The donor audit must exist**: `docs/audits/VARIANT_COMBAT_DONOR_AUDIT.md` (Day 1).
   - Fill in any gaps now, for assumptions A1–A10 in the implementation doc.
   - Record the result for each assumption as TRUE, FALSE or PARTIAL.
3. **Decide D1 per class** (child vs duplicate) from A8 and write the decision into the audit file.
   - If `BP_NeferCharacter` was created as a duplicate on Day 1 but A8 is TRUE, **stop and report**. Converting it (reparenting to `BP_CombatCharacter`, or re-creating it as a child and porting the Day 1–2 additions) is a decision for the user.
4. Visual rule: no reference master exists, so enemy visuals are `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.

## 1. Player combat baseline — 30 min

1. PIE in the Gate court with `BP_NeferCharacter`. Confirm the donor combo (A1) and the charged attack work under REN input (`IMC_Combat` + `IMC_REN_Default`, no key conflicts; E stays Interact).
2. If the attack doesn't fire because the REN controller lacks the donor IMC or bindings: add the donor IMC in `BP_REN_PlayerController` (priority 0; REN IMC stays priority 1).
3. Confirm the player has health and a life bar (A2). If not, use the fallback in the implementation doc §2.
4. **One simple chain is enough.** Don't add attacks.
5. Confirm the no-shadow still holds (Day-2 `ApplySheutState`) with any weapon mesh the donor attaches.

## 2. `BP_NamelessDead` — 45 min

1. Create `/Game/REN/Characters/Enemies/NamelessDead/BP_NamelessDead` as a **child or duplicate per D1**, from `BP_CombatEnemy`.
2. Placeholder visual:
   - a REN material instance `MI_REN_NamelessDead_TEMP` (warm-brown skin tone and linen off-white where the mannequin materials allow; no grey default, no emissive)
   - a TextRender component `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`, Hidden in Game
   - asset description with the same label
3. Tuning (in the REN class or a REN duplicate of the StateTree, **only** if the values live inside the tree), per implementation doc §8:
   - approach speed about 250
   - wind-up ≥ 0.5 s
   - cooldown about 1.5 s
   - health so it dies to 2–3 light chains
4. Behaviour check (spawn one manually in the court): approaches, telegraphs, hits, takes damage, dies (A3, A4). No teleporting, no rage.
5. If A3 is FALSE (the donor AI is unusable with REN classes): apply the minimal MoveTo/attack fallback from the implementation doc §2.

## 3. Death and restart — 45 min

Implement per the implementation doc §5:
- **Preferred:** a REN-owned donor checkpoint (child or duplicate).
- **Fallback:** `BP_REN_GameMode.RespawnPlayer()` + `LastCheckpoint` + `OnPlayerRespawned` + `BP_REN_Checkpoint`.

Wire up:
- `REN_INT_GW_Checkpoint_Approach` → `REN_GW_Trigger_Checkpoint_Approach` / `REN_GW_Respawn_Approach`
- `REN_INT_GW_Checkpoint_ArenaApproach` → `REN_GW_Trigger_Checkpoint_ArenaApproach` / `REN_GW_Respawn_ArenaApproach`
- The default checkpoint is `REN_PlayerStart` until the first checkpoint.

Player death → input off → 1.5 s → respawn at full health, facing +Y.

## 4. Encounter controller — 60 min

Create `/Game/REN/Gameplay/Combat/BP_EncounterController` exactly as in the implementation doc §4.
- Enum `E_EncounterState` (Idle, Active, Cleared) in `/Game/REN/Gameplay/Combat/`.
- Place it in `L_GateWest_Blockout` as `REN_INT_GW_Encounter01`, with:
  - `StartTrigger` = `REN_GW_Trigger_EncounterStart`
  - `SpawnMarkers` = `REN_GW_Marker_Enemy_01`, `_02`
  - `EnemyClass` = `BP_NamelessDead`
  - `GateSlab` = `REN_GW_CombatGate_Slab`
- **Dormant spawn:** if A9 is TRUE, spawn at BeginPlay with logic not started. Otherwise use the approach-trigger fallback. Record which one was used.
- Reset on `OnPlayerRespawned` (while not Cleared). When Cleared, the slab sinks 640 over 3 s.

## 5. Camera checks (no redesign) — 30 min

Run these in PIE and record PASS/FAIL, plus any values changed:

| Check | Where | PASS when |
|---|---|---|
| Tight compatibility | Tomb corridor (300 wide) and the shadow lane | No persistent clipping through walls or into Nefer; the path stays readable |
| Combat readability | Court, 2 enemies | Both enemies' wind-ups are visible during normal play |
| Enemy visibility | Enemy behind the player | The camera recovers view within about 1 s of turning |
| Wall collision | Back against a court wall and a pilaster | No violent snapping or pops |
| Distance | Everywhere | Comfortable 3–5 m feel (`ART_DIRECTION` gameplay mode) |

If the donor camera fails: make the **smallest** change (arm length, socket offset, probe size, camera lag) on `BP_NeferCharacter` only, and record the old and new values. No lock-on unless the donor already has one that works.

## 6. Dodge (only if needed) — ≤ 45 min

Fight the encounter 3 times with donor mobility.
- **If the hits are unavoidable/unfair:** implement a dodge exactly per the implementation doc §6 (dash 0.3 s, i-frames 0.25 s, cooldown 0.6 s, 1000 cm/s, no stamina, no root motion) and record the timing.
- **Otherwise:** skip it, record "deferred to Face-Eater prep", and move on.

## 7. Optional third enemy — 10 min (cut first)

Add `REN_GW_Marker_Enemy_03_Optional` to `SpawnMarkers` only if the 2-enemy fight is already fair and readable.

## 8. PIE acceptance (from `L_REN_Slice`) — PASS/FAIL each — 30 min

1. From the passage, the Nameless Dead are visible and not yet attacking (or the fallback pop-in is ≥ 10 m away).
2. Entering the court starts the encounter. Enemies approach with readable anticipation, and there's no rage behaviour.
3. Nefer's attack chain damages enemies. Enemies die (no instant despawn pop), and the slab sinks once they're all dead.
4. Enemies damage Nefer, and the life bar reflects it.
5. **Player death → restart** at `Respawn_Approach` at full health, with the encounter reset (the same 2 enemies, the slab closed). Repeat 3 times: no duplicate or leftover enemies, no errors.
6. After clearing: die later (e.g. force a kill in the corridor) → respawn at `Respawn_ArenaApproach`; the slab **stays open** and the enemies don't return.
7. Camera checks from §5 all PASS, or the smallest corrections are documented.
8. No-shadow still holds in the court lighting, including on any weapon mesh.
9. Git shows **no changes under `Content/Variant_Combat/`**.
10. No "Accessed None" or Blueprint errors across 3 full fights.
11. **Timing:** fight duration for 2 runs. Expected about 45–120 s.

## 9. World-lock and hand-back

1. Validate `L_GateWest_Blockout` standalone. Expected: only ADDED `REN_INT_GW_*`. No CHANGED lines; the slab must be back at its built transform outside PIE. Promote the candidate if it's clean.
2. Commit the assets (LFS), the audit file, the baseline and reports, and docs (CURRENT_PROJECT_STATE, TASK_BOARD, DEVLOG).
3. The report must include:
   - the A1–A10 results, the D1 decision, and the dormant-spawn method
   - the camera values
   - whether the dodge was added (with timing) or deferred
   - the §8 results and fight timings

## Cut order (Gate + combat, cut from the top)

1. Third enemy
2. Dodge (if not required for fairness)
3. Gate-opening sound and shake
4. Dormant-spawn polish (use the approach-trigger fallback)
5. Light-pass tuning beyond readability

**Never cut:**
- the Gate opening (deterministic)
- one encounter with 2 enemies
- damage both ways
- death → checkpoint restart with the encounter reset
- the combat gate unlocking on clear
- the camera checks
- no template modifications
