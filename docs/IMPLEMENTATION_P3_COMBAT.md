# REN — P3 First Combat: Implementation Design

Status: cloud static specification, 2026-09-30. **Nothing here is PIE-validated.** It depends on the Day-1 donor audit (`docs/audits/VARIANT_COMBAT_DONOR_AUDIT.md`), which doesn't exist yet. Every donor fact below is an **assumption** until the audit confirms it.
Local execution: `docs/tasks/P3_FIRST_COMBAT.md`. Enemy direction: `docs/NAMELESS_DEAD_SPEC.md`. Space: `docs/GATE_WEST_GREYBOX_SPEC.md`.

## 1. Goal (and nothing more)

- Nefer attacks with **one simple chain** (the donor combo).
- Nameless Dead approach and attack with **one basic strike**, plus a second attack only if the donor already provides it cheaply.
- Damage works both ways. The player can die and an enemy can die.
- **Restart is reliable**: the player returns to the last checkpoint and the encounter resets cleanly.
- Dodge only if it's needed for fairness (§6).
- The fight reads well in the Gate court with the donor camera.

**Not built:** skill tree, inventory, stamina (unless the donor already requires it), combo editor, lock-on (unless the donor makes it free), status effects, equipment, loot, spawn waves.

## 2. Donor assumptions (VERIFY in the audit; each has a fallback)

| # | Assumption about Variant_Combat | If false |
|---|---|---|
| A1 | `BP_CombatCharacter` performs a light combo (`IA_ComboAttack` → `AM_ComboAttack`, with notifies `AN_AttackCombo` / `AN_AttackDamage`) and a charged attack | Use only whatever single attack exists. If there's none: one montage plus one sphere-trace damage notify in the REN class (still Blueprint) |
| A2 | Damage is applied through `BPI_Damageable` (the attacker calls it on the hit actor), and health lives on the character with `UI_LifeBar` | Add `Health` / `MaxHealth` and a `ReceiveDamage` path in the REN classes only |
| A3 | `BP_CombatEnemy` is run by `BP_CombatAIController` + StateTree `ST_CombatEnemy` (EQS evade/flank/fallback, ComboAttack/ChargedAttack tasks, SetCharacterSpeed) | Minimal fallback: AI MoveTo the player, attack in range, 1.5 s cooldown |
| A4 | The enemy has a death path (ragdoll or destroy) | Add: on Health ≤ 0 → stop logic, disable collision, ragdoll or play the death anim, no destroy for 5 s |
| A5 | The player has a death path, and `BP_Combat_CheckpointVolume` or the GameMode handles respawn | Use the REN minimal restart (§5) |
| A6 | There is **no dodge** in the template | §6 |
| A7 | The camera is a spring arm with a side-offset toggle (`IA_ToggleCameraSide`) | §7 |
| A8 | Donor StateTree tasks, notifies and UI **cast to `BP_CombatCharacter` / `BP_CombatEnemy`** or otherwise depend on those classes | Decision D1 |
| A9 | The StateTree AI component has a "start logic automatically" option that can be turned off | Encounter fallback (§4) |
| A10 | Combat relies on `IMC_Combat` bindings (attack, charged, camera side) | Check for key conflicts with E / Interact and with dodge |

## 3. Decisions

**D1 — Duplicate vs child Blueprint** (decided from the audit, per class):
- The rule is **never edit template assets**. Both options respect it.
- If donor tasks, notifies or UI **cast to or reference** the donor class (A8 true), make **child Blueprints**:
  - `BP_NeferCharacter` : `BP_CombatCharacter`
  - `BP_NamelessDead` : `BP_CombatEnemy`
  Casts keep working, and REN changes live in the child.
- If A8 is false, a **duplicate** is fine, but every hardcoded path must be retargeted.
- **Interfaces** (`BPI_Damageable`, `BPI_Attacker`, `BPI_Activatable`) are **referenced, never duplicated**; duplicating them would break donor notifies.
- The StateTree, AI controller, montages and notifies are **referenced as-is**. Duplicate one only when REN must change it (e.g. `ST_NamelessDead` if speed or wind-up tuning is stored inside the tree).
- A known temporary cost: REN keeps a dependency on `/Game/Variant_Combat/` for the slice.

**D2 — Enemies are spawned by an encounter controller, not hand-placed.** This gives deterministic resets on restart.

**D3 — Face-Eater is out of scope.** This file must not add boss logic. Later, the Face-Eater's phase authority will belong to a REN state machine, not the generic StateTree.

## 4. Encounter controller — `/Game/REN/Gameplay/Combat/BP_EncounterController`

Placed in `L_GateWest_Blockout` as `REN_INT_GW_Encounter01`.

| Variable | Type | Value |
|---|---|---|
| `StartTrigger` | Actor ref | `REN_GW_Trigger_EncounterStart` |
| `SpawnMarkers` | Actor array | `REN_GW_Marker_Enemy_01`, `_02` (add `_03_Optional` only if cut order allows) |
| `EnemyClass` | Class | `BP_NamelessDead` |
| `GateSlab` | Actor ref | `REN_GW_CombatGate_Slab` |
| `GateSinkDistance` / `GateDuration` | Float | 640 / 3.0 |
| `State` | Enum `E_EncounterState` | Idle, Active, Cleared |
| `LiveEnemies` | Actor array | |

Logic:
1. **BeginPlay:** spawn one enemy at each marker (transform = marker). **Preferred (if A9):** AI logic is *not started*, so enemies stand still facing −Y and are visible from the passage (the readable approach). **Fallback:** spawn them when the player enters `REN_GW_Trigger_Checkpoint_Approach` (≥ 10 m away, accept distant pop-in).
2. **StartTrigger overlap** (State = Idle): State = Active; start the AI logic on every live enemy.
3. **Enemy death** (bind to the donor death event, or `OnDestroyed`): remove it from `LiveEnemies`. When the array is empty: State = **Cleared**, then Timeline `GateDuration` sinks `GateSlab` by `GateSinkDistance` (deterministic). Sound is nullable.
4. **Player respawn** (`BP_REN_GameMode.OnPlayerRespawned`), if State ≠ Cleared: destroy `LiveEnemies`, State = Idle, respawn at the markers (as in BeginPlay). The slab stays closed.
5. The **Cleared** state survives respawns, and the slab stays open.

## 5. Death and restart

**Preferred:** use the donor checkpoint/respawn, if the audit shows it works with REN classes.
- Place **REN-owned duplicates** (or children, per D1) of `BP_Combat_CheckpointVolume`.
- Never use template instances bound to template logic that we can't adapt.

**Fallback — minimal REN restart (Blueprint only):**
- `BP_REN_GameMode`:
  - `LastCheckpoint` (Transform), set by checkpoint volumes
  - event dispatcher `OnPlayerRespawned`
  - function `RespawnPlayer()`:
    1. Fade out (0.4 s).
    2. Destroy the dead pawn.
    3. `RestartPlayerAtTransform(PC, LastCheckpoint)`, restoring full health.
    4. Call `ApplySheutState` via BeginPlay (Day 2).
    5. Fade in.
    6. Broadcast `OnPlayerRespawned`.
- `BP_REN_Checkpoint` (`/Game/REN/Gameplay/Checkpoints/`): an instance-editable `TriggerActor` and `RespawnPoint` (TargetPoint). On player overlap → `GameMode.LastCheckpoint = RespawnPoint` transform.
- Player death: the donor death event (or Health ≤ 0) → disable input → 1.5 s → `RespawnPlayer()`.
- **Default checkpoint:** the slice start (`REN_PlayerStart`) until the first checkpoint is reached.
- **No save system.** A level reload is only a last-resort debug path.

## 6. Dodge (preferred, not mandatory)

- First test the fight with donor mobility only.
- **Add a dodge only if** enemy attacks can't be avoided fairly by movement.
- If added: `IA_Dodge` (key from the audit's free-key list; suggested Left Alt / gamepad B or Circle, checking `IMC_Combat` for conflicts) in `IMC_REN_Default`.
- `BP_NeferCharacter.Dodge()`:
  - blocked if falling, dodging, or in cooldown
  - direction = last movement input (or −ActorForward if there's none)
  - `LaunchCharacter(Direction × 1000, XYOverride = true, ZOverride = false)`, with ground friction/braking temporarily lowered for 0.3 s (or just rely on launch plus normal braking; tune)
  - `bInvulnerable = true` from 0.00 to 0.25 s. Damage receipt ignores hits while it's true (in the REN class's damage path).
  - cooldown 0.6 s
  - no stamina
  - no root motion (optionally play an existing montage for visuals only; none is required)
- If an attack montage is playing: allow the dodge to cancel after the damage notify, or block it. Pick whichever the donor supports; document it.
- **Timing, if added:** dash 0.3 s, i-frames 0.25 s, cooldown 0.6 s, speed 1000 cm/s.

## 7. Camera (no redesign)

- Start from the donor camera.
- Test these explicitly:
  - tight Tomb corridor, 300 wide
  - combat readability in the court
  - enemy visibility during attacks
  - wall collision (probe) behaviour
  - clipping into Nefer
  - distance
- If any fails, apply the **smallest** correction (arm length, socket offset, probe size, lag), record the values, and apply them to `BP_NeferCharacter` only.
- **No** lock-on unless the donor already has one that works. No cinematic combat camera.

## 8. Nameless Dead in combat (per `NAMELESS_DEAD_SPEC.md`)

- Human-sized, using the donor capsule. **`TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`**:
  - the mannequin mesh with a warm-brown/linen REN material instance (never the default grey, never glowing)
  - an editor-only TextRender with that label (Hidden in Game)
  - the same label in the asset description
- Readable anticipation: attack wind-up **≥ 0.5 s** (lower the montage play rate or add a pre-attack pause in the tree or the REN child).
- Walk speed lower than the donor's (target about 250 cm/s approach).
- No teleporting, no roars, no rage behaviour.
- Tuning targets (convert to donor units after the audit):

  | Parameter | Target |
  |---|---|
  | Enemy health | dies to 2–3 of the player's light chains |
  | Player health | survives about 5–6 enemy hits |
  | Attack cooldown | about 1.5 s |
  | Active enemies | at most 2 (3 only if Enemy_03 is kept) |

## 9. Acceptance (PASS/FAIL; local only)

See `docs/tasks/P3_FIRST_COMBAT.md` §8. Summary:
- attack, damage and death both ways
- the encounter clears and the slab sinks
- player death → checkpoint restart with the encounter reset (repeated 3 times, no leftovers)
- camera readable
- no soft-lock
- no template asset modified (Git shows no changes under `Content/Variant_Combat/`)
