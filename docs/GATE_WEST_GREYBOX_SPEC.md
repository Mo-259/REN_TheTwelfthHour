# REN — Gate of the West: Greybox Spec v1

Status: designed in cloud on 2026-09-30. Builder: `Scripts/Editor/REN_GateWest_Greybox_Builder_v1.py`. Layout data (the single source of numbers): `Scripts/Editor/REN_GateWest_Layout.py`. Unreal execution and PIE are **LOCAL_VALIDATION_REQUIRED**.

- Sublevel: `/Game/REN/Worlds/GateWest/L_GateWest_Blockout`, always loaded in `L_REN_Slice`. Prefix `REN_GW_`.
- Sprint tiers: approach and first combat are **C**; the arena shell is **A later** (Face-Eater, Day 5; **no boss logic here**).
- Visuals: greybox only. No reference master exists yet, so all character and marker visuals are `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.

## 1. Coordinates and connection

- These are the shared slice coordinates: +Y forward (west), +Z up, Z 0 = walk level. Facing +Y, **player-right = −X**. Side tags are `_NX`/`_PX`.
- The area starts at **y 5450**, the north edge of `REN_NEC_GatePlinth`, on the Gate axis **x = 0**.
- The entrance is the Gate itself. `REN_DistantGate` is a Tomb skyline proxy at x ±250, y 5250..5350, z 0..1100, flanked by the Necropolis gate wings.
  - It is **not duplicated, moved in the editor, or reassigned to another level**.
  - At runtime it sinks 1100 cm into the plinth (§4), leaving a 500 cm opening that lines up exactly with the 500 cm passage.
- Validation checks: no overlap with any Tomb reference actor or any Necropolis solid; a continuous floor chain; an unobstructed walk along x = 0 (except the closed combat gate).

## 2. Layout (top view, +Y up the page, player-right = page-left)

```
 y
11050 ┌─RecessBack─┐
10450 │  RECESS    │  boss entrance (on axis, dark, lintel at 700)   ▲ FaceEater_Start_PLACEHOLDER (0,10700)
      ├────────────┴───────────────┐
      │ ARENA SHELL 2200 × 1900     │  4 Glyph-pillar shells (±650, 9150 / 9950), 120×120×600
      │     ▲ FaceEater_Center_PLACEHOLDER (0,9550)
 8550 ├──────┐  threshold  ┌───────┤  walls 900
 8450        │ CORRIDOR    │           600 wide, lintel at y 8250..8450 (600 clear)
 7750        │  (ckpt)     │
 7650 ═══════╪ CombatGate  ╪═══════   slab 600 wide × 600 tall, sinks 640 when cleared
      │ stela ▓            ▓ stela │  stelae 900 tall flank the exit = "go here"
      │ COURT 1800 × 1400 (pilasters at x ±750..900)  enemies E1(−300,6950) E2(300,7100) [E3(0,7350) optional]
 6250 └──────┐             ┌───────┘
             │ PASSAGE 500 │  basalt mass x ±250..530, walls 800, lintels at 600
 5450        │  (ckpt)     │
 ────────────┴── Gate (REN_DistantGate sinks) ── Necropolis plaza (Trigger_GateOpen)
```

## 3. Zones

| Zone | Interior (cm) | Purpose / notes |
|---|---|---|
| **Passage** | x ±250, y 5450..6250 | A compressed western threshold with walls 800 tall and **two lintels at 600**. Checkpoint `Respawn_Approach` (0, 5800). From here the player sees straight down the axis into the court, where the enemies stand. This is the readable pre-combat approach. |
| **Combat Court** | x ±900, y 6250..7650 (18 × 14 m; 15 m between pilasters) | Open top, walls 600. Pilasters sit against the side walls, out of the fight. Two stelae (900 tall) flank the exit. Enemy markers are at least 3 m from every wall. |
| **Combat Gate** | x ±300, y 7650..7750 | `REN_GW_CombatGate_Slab` (Movable, 600 tall, `sink_cm` 640) seals the exit until the encounter is cleared. It can't be jumped. |
| **Corridor** | x ±300, y 7750..8450 | Compression before the arena, with a lintel at 600. Checkpoint `Respawn_ArenaApproach` (0, 8000). |
| **Arena shell** | x ±1100, y 8550..10450 (22 × 19 m) | Walls 900, open top. Four **Glyph-pillar shells** are fixed landmarks now; Glyph Blueprints are layered on top later, the same pattern as the Cartouche. There is at least 6 m of clear radius around the boss centre marker for sweeps, and at least 3.3 m between each pillar and its side wall. **Entry lock** (added for C-05): `REN_GW_ArenaGate_Slab` rests below the threshold and rises 640 cm when the player crosses `REN_GW_Trigger_ArenaEnter` (y 8700..8900, full width). Arena requirements: `docs/FACE_EATER_BOSS_SPEC.md` §8. |
| **Boss recess** | x ±300, y 10450..10950 | This is the boss's entrance direction: dark, on axis, with a lintel at 700. |

Markers (TargetPoints):
- `Marker_Enemy_01`, `_02`, `_03_Optional`, all facing −Y
- `Marker_FaceEater_Start_PLACEHOLDER`, `Marker_FaceEater_Center_PLACEHOLDER`
- `Respawn_Approach`, `Respawn_ArenaApproach`, both facing +Y

Triggers:
- `Trigger_GateOpen` sits on the Necropolis plaza, y 5160..5245. It is GW-owned but spatially on the plaza.
- `Trigger_Checkpoint_Approach`
- `Trigger_EncounterStart` (y 6300..6500, full court width)
- `Trigger_Checkpoint_ArenaApproach`

## 4. Gate opening (no Tomb transform change)

- **Tomb actor property changes only:** set `REN_DistantGate` Mobility = **Movable** and add Actor Tag **`REN_GateWestLeaf`**. World-lock is unaffected: the transform, class, mesh and level stay the same.
- `BP_GateWestOpener` (GW level, label `REN_INT_GW_GateOpener`):
  - BeginPlay: `GetAllActorsWithTag(REN_GateWestLeaf)`. There must be exactly one; otherwise log an error and do nothing.
  - On the player overlapping `REN_GW_Trigger_GateOpen`, once: a Timeline of 6 s, ease-in, moves the gate's Z by **−1100**, so its top ends flush with the plaza.
  - Sound is nullable. A restrained shake is optional.
- The player can only reach the plaza by passing Anubis, and the dialogue trigger spans the full bridge width. So the gate always opens after the Anubis exchange.
- The gate stays open for the rest of the session (persistent world state).

## 5. Visual language (greybox now; art pass later reads the reference manifest)

- Monumental western threshold: pylon-like **mass** (thick walls), lintels, stelae and pilasters, a compress → open → compress → open rhythm, all on one axis toward the west.
- Materials later: basalt for the passage and arena walls, sandstone for the court.
- **Never:** Gothic arches, castle crenellations, spikes, demon architecture, skull décor, neon.

## 6. Camera and readability

- The camera is never roofed except under the lintels, which leave 600 cm of clearance.
- The court and arena are open-topped, so wall collision only matters at the edges.
- Main paths are at least 500 wide: passage 500, corridor 600.
- Lights are greybox point lights per zone (passage and corridor dim, court and arena brighter, recess very dim). Tune them locally.

## 7. Timing (honest)

| Beat | Time |
|---|---|
| Plaza → gate sinks (6 s) → passage | 15–20 s |
| First combat (2 Nameless Dead) | 45–120 s |
| Restarts | extra |
| Corridor → arena shell | 10–15 s |
| **Total (excluding the boss)** | **≈ 1.5–3 min** |

No padding.

## 8. Out of scope

Face-Eater logic and actor, Glyph pillar behaviour (Day 5; see `docs/FACE_EATER_BOSS_SPEC.md`), final art, additional encounters. The entry-lock geometry exists; its logic is Day 5.
