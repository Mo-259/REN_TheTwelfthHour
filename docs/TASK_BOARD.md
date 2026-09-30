# REN — Task Board

Status values:
- TODO
- IN_PROGRESS
- BLOCKED
- LOCAL_VALIDATION_REQUIRED
- DONE

## 7-day sprint view (see `docs/SPRINT_7DAY.md`)

| Day | Local (Unreal/MCP) | Cloud prep for next day |
|---|---|---|
| 1 | P0-05, P0-06, P0-07, P0-09, P0-11, P1-00…P1-08 via `docs/tasks/P1_INTERACTION_FOUNDATION.md` | C-01 Necropolis builder, C-02 P2 Tomb-beats spec |
| 2 | P2-01…P2-04, P0-12 | C-03 GateWest/arena builder, C-04 P3 combat spec |
| 3 | P2-05, P5-01 (Anubis placeholder) | C-05 P4 Face-Eater spec |
| 4 | P3-01…P3-07, P4-01 | C-06 audio list + Tomb lighting spec |
| 5 | P4-02…P4-08 | C-07 bug triage / polish checklists |
| 6 | Tier A polish (Tomb + Face-Eater) | review hand-back reports |
| 7 | Freeze, playthroughs, package | release notes, state docs |

## Cloud prep tasks

| ID | Task | Status |
|---|---|---|
| C-00 | Sprint plan + P1 local task spec + v3 builder guard | DONE (cloud) |
| C-01 | `REN_Necropolis_Greybox_Builder_v1.py` (prefix `REN_NEC_`, standalone-map guard) | TODO |
| C-02 | `docs/tasks/P2_TOMB_BEATS.md` (no-shadow, side clue, wake, reveal camera, `L_REN_Slice`) | TODO |
| C-03 | `REN_GateWest_Greybox_Builder_v1.py` (prefix `REN_GW_`) | TODO |
| C-04 | `docs/tasks/P3_FIRST_COMBAT.md` | TODO |
| C-05 | `docs/tasks/P4_FACE_EATER.md` | TODO |
| C-06 | Audio placeholder list + Tomb lighting spec | TODO |
| C-07 | Bug triage / polish checklists | TODO |

## P0 — Production foundation

| ID | Task | Status |
|---|---|---|
| P0-01 | Verify project root / `.uproject` / Git status | DONE (cloud audit 2026-09-30) |
| P0-02 | Install this Claude dev kit into repo | DONE (repo files identical to DevKit zip) |
| P0-03 | Verify Unreal `.gitignore` | DONE (generated folders ignored; LFS decision open, see P0-10) |
| P0-04 | Copy v3 Tomb builder into `Scripts/Editor/` | DONE (labels match `L_Tomb_Blockout.umap`) |
| P0-05 | Export first world-lock manifest | LOCAL_VALIDATION_REQUIRED |
| P0-06 | Validate v3 map route in PIE | LOCAL_VALIDATION_REQUIRED (only script completion confirmed; also check PlayerStart pitch) |
| P0-07 | Configure local Unreal MCP | TODO |
| P0-08 | Harden world-lock export/validate + offline diff + tests | DONE in cloud; Unreal run LOCAL_VALIDATION_REQUIRED |
| P0-09 | Confirm Python Editor Script Plugin in `.uproject` | LOCAL_VALIDATION_REQUIRED |
| P0-10 | Decide Git LFS policy for `.uasset`/`.umap` | BLOCKED (user decision) |
| P0-11 | Set `L_Tomb_Blockout` as editor startup / game default map; clean stale DefaultEditor.ini map | TODO (local, via Project Settings; switch to `L_REN_Slice` once P0-12 exists) |
| P0-12 | Create persistent `L_REN_Slice` (non-WP) with always-loaded sublevels | TODO (Day 2) |
| P0-13 | Guard builder v3 against wrong world / locked layout | DONE in cloud (tested with fake `unreal`); Unreal run LOCAL_VALIDATION_REQUIRED |

## P1 — Interaction foundation

| ID | Task | Status |
|---|---|---|
| P1-00 | `BP_NeferCharacter` / `BP_REN_PlayerController` / `BP_REN_GameMode` from Variant_Combat duplicates | TODO (Day 1) |
| P1-01 | Create `IA_Interact` | LOCAL_VALIDATION_REQUIRED (asset exists at `/Game/REN/IA_Interact`, Boolean; unreferenced) |
| P1-02 | Map Interact to E | TODO |
| P1-03 | Create `BPI_Interactable` | TODO |
| P1-04 | Implement 350cm camera trace (start projected to pawn) | TODO |
| P1-05 | Blank Cartouche interactable | TODO |
| P1-06 | Exit Door interactable | TODO |
| P1-07 | Sarcophagus interaction placeholder | TODO |
| P1-08 | Interaction prompt UI + `WBP_Subtitle` | TODO |

## P2 — Opening mechanics

| ID | Task | Status |
|---|---|---|
| P2-01 | Implement no-shadow player state | TODO |
| P2-02 | Validate shadow clue lighting | TODO |
| P2-03 | Side clue trigger/content | TODO |
| P2-04 | Exit reveal transition | TODO |
| P2-05 | Build first Vertical Necropolis greybox | TODO |

## P3 — Combat foundation

| ID | Task | Status |
|---|---|---|
| P3-01 | Reed Blade prototype | TODO |
| P3-02 | Light attack (reuse template combo/charged attack) | TODO |
| P3-03 | Dodge | TODO |
| P3-04 | Player health/damage | TODO |
| P3-05 | Enemy health/damage | TODO |
| P3-06 | Combat camera decision | TODO |
| P3-07 | `BP_NamelessDead` encounter(s) + checkpoint + death/restart | TODO (Day 4) |

## P4 — Face-Eater

| ID | Task | Status |
|---|---|---|
| P4-01 | Gate of the West arena greybox | TODO |
| P4-02 | Face-Eater placeholder character | TODO |
| P4-03 | Boss state enum / state machine | TODO |
| P4-04 | Hook sweep | TODO |
| P4-05 | Heavy strike | TODO |
| P4-06 | Grab | TODO |
| P4-07 | Chest seal exposure mechanic | TODO |
| P4-08 | Boss completion/reward | TODO |

## P5 — Presentation

| ID | Task | Status |
|---|---|---|
| P5-01 | Anubis encounter blockout | TODO |
| P5-02 | Tomb art pass | TODO |
| P5-03 | Necropolis art pass | TODO |
| P5-04 | Face-Eater arena art pass | TODO |
| P5-05 | Audio pass | TODO |
| P5-06 | Sequencer passes | TODO |
| P5-07 | Trailer capture | TODO |
