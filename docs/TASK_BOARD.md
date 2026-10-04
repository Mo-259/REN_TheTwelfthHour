# REN — Task Board

Status values:
- TODO
- IN_PROGRESS
- BLOCKED
- LOCAL_VALIDATION_REQUIRED
- DONE

## P0 — Production foundation

| ID | Task | Status |
|---|---|---|
| P0-01 | Verify project root / `.uproject` / Git status | TODO |
| P0-02 | Install this Claude dev kit into repo | IN_PROGRESS |
| P0-03 | Verify Unreal `.gitignore` | TODO |
| P0-04 | Copy v3 Tomb builder into `Scripts/Editor/` | TODO |
| P0-05 | Export first world-lock manifest | LOCAL_VALIDATION_REQUIRED |
| P0-06 | Validate v3 map route in PIE | DONE (user confirmed script complete; traversal details still worth rechecking) |
| P0-07 | Configure local Unreal MCP | TODO |

## P1 — Interaction foundation

| ID | Task | Status |
|---|---|---|
| P1-01 | Create `IA_Interact` | TODO |
| P1-02 | Map Interact to E | TODO |
| P1-03 | Create `BPI_Interactable` | TODO |
| P1-04 | Implement 350cm camera trace | TODO |
| P1-05 | Blank Cartouche interactable | TODO |
| P1-06 | Exit Door interactable | TODO |
| P1-07 | Sarcophagus interaction placeholder | TODO |
| P1-08 | Interaction prompt UI | TODO |

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
| P3-02 | Light attack | TODO |
| P3-03 | Dodge | TODO |
| P3-04 | Player health/damage | TODO |
| P3-05 | Enemy health/damage | TODO |
| P3-06 | Combat camera decision | TODO |

## P4 — Face-Eater

> P-phase numbering is **IMPLEMENTATION ORDER ONLY**. Runtime order follows v3 §7: Face-Eater (B01) before Anubis. P4-04 hook sweep, P4-06 grab and P4-07 chest seal are **superseded** by the v3 §25 mechanics (two jaw masks, exposed rib, mask throw at 65%, gate threads at 30%). See `docs/tasks/MASTER_LOCAL_EXECUTION_ORDER.md`.

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
