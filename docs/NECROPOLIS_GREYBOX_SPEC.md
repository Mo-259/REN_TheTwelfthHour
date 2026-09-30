# REN — Vertical Necropolis + Anubis Bridge: Greybox Spec v1

Status: designed in cloud on 2026-09-30. Builder: `Scripts/Editor/REN_Necropolis_Greybox_Builder_v1.py`. Layout data: `Scripts/Editor/REN_Necropolis_Layout.py` (the single source of numbers; this doc summarises it). Unreal execution and PIE traversal are **LOCAL_VALIDATION_REQUIRED**.

Sprint tier: **B** (a clean, readable route; placeholder art).
Sublevel: `/Game/REN/Worlds/Necropolis/L_Necropolis_Blockout`, always loaded in `L_REN_Slice`.

## 1. Coordinate convention (shared slice world)

- Units are cm. **+Y = forward** (Tomb → Duat → Gate of the West). **+Z = up.** Z 0 is the Tomb floor, which is also the Reveal Ledge top.
- Unreal is **left-handed**. When the player faces +Y (yaw 90), **player-right = −X** and **player-left = +X**.
- The builder-v3 labels `…Left…` and `…Right…` mean *map* −X and +X, which is the opposite of the player's view. For example, `REN_Reveal_LeftPier` (x −500) is on the player's **right**.
- New Necropolis labels therefore use axis tags: `_NX` for the −X side and `_PX` for the +X side.
- Every solid is an axis-aligned box made from the 100 cm Engine cube, so no rotated solids are needed and the Rotator-ordering risk is avoided.

## 2. Existing Tomb actors this layout depends on

These come from the builder-v3 source. **Live transforms are authoritative**; re-check them against the Tomb baseline once it's exported.

| Actor | AABB min → max (cm) | Role |
|---|---|---|
| `REN_RevealLedge` | (−375, 2525, −20) → (375, 2975, 0) | Start of the Necropolis route |
| `REN_Reveal_LeftPier` / `_RightPier` | x ∓530..∓470, y 2710..2850, z 0..360 | Reveal framing (player-right / player-left) |
| **`REN_DistantTower_A`** | (−1050, 3900, 0) → (−750, 4300, 1600) | **Skyline proxy.** Player-right, nearer, 16 m |
| **`REN_DistantTower_B`** | (650, 4350, 0) → (1050, 4850, 2300) | **Skyline proxy.** Player-left, farther, 23 m |
| **`REN_DistantGate`** | (−250, 5250, 0) → (250, 5350, 1100) | **Skyline proxy.** On the axis; the façade of the Gate of the West |

Skyline proxy rules:
- They stay where they are and remain Tomb-owned.
- The Necropolis builder never spawns geometry at their transforms and never overlaps them (enforced by `validate_layout()` and the tests).
- Replacing their mesh later is fine at the same transform. World-lock reports that as an *asset change*, not drift.
- The Necropolis **extends** them instead of duplicating them:
  - `REN_NEC_TowerA_Foundation` and `REN_NEC_TowerB_Foundation` continue both towers straight down from z 0 to −3000, with the same XY footprint. This makes them read as monumental shafts rising out of the void.
  - `REN_NEC_GatePlinth` is the gate's base.

## 3. Route overview (top view; +Y up the page, player-right = −X = page-left)

```
 y
5450 ┌──────── GatePlinth / plaza (z 0) ────────┐     beyond y 5450: L_GateWest_Blockout
5350 │ Wing_NX ▓▓[ REN_DistantGate ]▓▓ Wing_PX   │
5150 └────────┬──── Bridge_Deck (z 0) ───┬───────┘
              │   ▲ Anubis (0,4950)      │        ██ TowerB (+X, 650..1050)
              │   │  AnubisDialogue      │        ██ 4350..4850
 TowerA ██    │   │  AnubisSlow          │  S2 ▲ (x 320..620, climbs −Y to z 0)
 (−X) ██      │   │                      │  Landing (z −600) ← GlyphSeal slab
 3900..4300   │   │   COURT (z −600)  ║Glyph║
       Spur ◄─┤   │   x −700..250     ║Wall ║
  (z −600)    └ BridgeHead (z 0, y 3700..3880) ◄── S2 top arrives here
3695 ─────────── S1 bottom
2975  S1 ▼ (x −375..−75, descends +Y)   Ledge front (parapet + invisible wall)
2525 ┌──── REN_RevealLedge (Tomb, z 0) ────┐
```

Sequence:
1. The Ledge.
2. **S1** descends 6 m on the player-right half of the ledge front.
3. **Lower Court.** This is the first route decision.
4. Optional **Spur** toward Tower A, with the shadow tease.
5. **Glyph** on the court's player-left wall.
6. The sealed **slab** sinks.
7. **S2** climbs 6 m beside Tower B, heading back toward −Y.
8. **Bridge Head.** The player arrives facing the Tomb, then turns 180° to face the axis.
9. **Anubis Bridge**, 12.7 m, flanked by both towers.
10. **Gate plaza.**

Layering is deliberate. The court sits 5.6 m below the Bridge Head and the bridge, so the player walks *under* the bridge they will later cross.

## 4. Elements (key numbers)

| Element | Box / location | Notes |
|---|---|---|
| Ledge safety | Front parapet x −45..375 (100 tall) + invisible wall to z 600; side parapets x ±(375..405); back-corner parapets | Stops a running jump straight to the Bridge Head (~7 m); prevents falls off the ledge sides and back |
| S1 descent | x −375..−75 (300 wide), 24 steps × 25 rise × 30 run, y 2975→3695, z 0→−600 | Per-step parapets both sides; invisible blocker on the +X side (x −45..−15) |
| Lower Court | x −700..250, y 3695..4850, z −600 (950 × 1155) | Parapets on the void edges; a bridge pier column stands in the court at x ±100, y 4400..4500 |
| Glyph wall | x 250..290, y 3695..4600, top z −150 (450 tall) | Seals the court's +X edge; can't be jumped (apex ~250) |
| **Glyph panel** | x 240..250, y 4430..4570, z −520..−280 | Faces −X into the court, lit by `Light_Glyph` |
| Glyph seal slab | x 250..290, y 4600..4850, z −600..−150, **Movable** | Sinks 460 cm when the Glyph is used; opening is 250 wide |
| Corner walls | court and landing corners at y 4850..4880, top −150 | Stop parapet-walking around the slab |
| Spur (optional) | x −1350..−700, y 3550..3850, z −600 | Dead end at a clue pedestal (−1250, 3650); about 12 m round trip |
| Landing S2 | x 290..620, y 4600..4850, z −600 | Behind the slab |
| S2 ascent | x 320..620 (300 wide), 24 steps, y 4600→3880, z −600→0 | Against Tower B's foundation face |
| Bridge Head | x −240..620, y 3700..3880, z 0 | Parapets on the void edges |
| Anubis Bridge | x −200..200 (**400 wide**), y 3880..5150, z 0; parapets x ±(200..240), 100 tall | Pier 1 (in court) and Pier 2 (y 4950..5050) |
| Gate plinth / plaza | x −500..500, y 5150..5450, z −3000..0 | Gate wings x ±(250..500), y 5250..5350, 7 m tall, seal the gate line |
| Foundations | Tower A / B footprints, z −3000..0 | Touch the proxy bases, no overlap |
| Void dressing | 3 suspended sarcophagus proxies, overhead `BlackRiver` slab at z 4000 | No collision; skyline only |

## 5. Beats and their locations

- **First route decision:** at the S1 bottom / court entry (about (−225, 3700, −600)).
  - To the player's right, the shadow on Tower A's face pulls toward the Spur.
  - Ahead-left, the warm Glyph light on the wall pulls toward the critical path.
  - Both are readable without UI.
- **Glyph interaction:** `REN_NEC_GlyphPanel` on the court's +X wall.
  - It uses the same `BPI_Interactable` pattern as the Tomb.
  - Carved grooves take ink, then `REN_NEC_GlyphSeal_Slab` sinks.
  - This is the **teaching moment** for the glyph mechanic that the Face-Eater fight tests later.
- **Independent-shadow tease:** Tower A foundation's −Y face (y 3900, x −1050..−750, z −600..0).
  - The face points back at the ledge, so it is visible from the ledge, S1, the court and the Spur.
  - The spot light `REN_NEC_Light_ShadowTease` sits at (−900, 3600, −250), aimed +Y.
  - `Trigger_ShadowTease` near the S1 bottom starts it.
  - A hidden-in-game mannequin with *Cast Hidden Shadow* walks from `Marker_ShadowWalk_Start` (−760, 3780) to `_End` (−1120, 3780), so a human shadow crosses the wall with nobody there and slips round the tower corner.
  - Nefer still casts no shadow himself.
- **Anubis bridge approach:**
  - The player arrives at the Bridge Head facing the Tomb, then turns to see the whole bridge axis: both towers, the Gate, and Anubis standing still at `Marker_Anubis` (0, 4950, 0), facing −Y.
  - `Trigger_AnubisSlow` (y 4300..4450) slows movement.
  - `Trigger_AnubisDialogue` (y 4650..4750, about 2–3 m from Anubis) starts the exchange.
  - There is 150 cm of clearance on each side of Anubis, so afterwards the player walks *past* him. Anubis does not move.

## 6. Safe widths, drops and recovery

- Main route at least 300 cm (stairs). Bridge 400. Court 950. Spur 300.
- Every edge above a drop of more than 3 m has a 100 cm parapet, except where the route intentionally connects.
- Stairs: 25 cm rise, which is under the UE default MaxStepHeight of 45.
- Headroom under the Bridge Head and bridge is 560 cm (at least 350 required).
- The void falls to −3000. `Trigger_FallRecovery` (z −1600..−1400, covering the whole area) is a Day-3 Blueprint that teleports the player to the last `REN_NEC_Respawn_*` point (Ledge, Court, BridgeHead).
- **Known residual risk:** a skilled diagonal jump from the court parapet around the corner wall into the landing may still be possible. This is a PIE check; if it reproduces, add an invisible blocker.

## 7. Camera sightlines (gameplay camera, ~3–5 m behind)

- **Ledge:** the Gate is dead ahead on the axis, framed by Tower A (right, near) and Tower B (left, far, taller). The Bridge Head is 7 m ahead across the gap. The court and S1 are visible below-right.
- **S1 descending:** Tower A's lit face is ahead-right, where the shadow tease plays.
- **Court:** looking up at the bridge underside and pier column; the Glyph panel is lit on the left wall.
- **Bridge Head arrival:** facing back toward the Tomb exit (showing where the player came from). The turn reveals the Anubis bridge composition.
- **Suggested Anubis camera** (a Day-3 CameraActor, placed locally): about (−160, 4520, 170), looking +Y at Anubis head height (0, 4950, ~220). It is on the player-right side of the bridge, still inside the parapet line.

## 8. Traversal time (honest)

| Beat | Time |
|---|---|
| Reveal pause on ledge | 10–20 s |
| S1 descent + shadow tease | 15–30 s |
| Spur detour (optional) | 20–40 s |
| Find and use the Glyph, slab sinks | 20–60 s |
| S2 ascent, Bridge Head turn | 15–20 s |
| Slowed bridge walk + Anubis exchange | 45–75 s |
| Pass Anubis to the plaza | 10 s |
| **Total** | **≈ 2.5–4.5 min** |

This is shorter than the 8-minute bracket (8–16). No padding has been added. If more time is wanted later, the candidates are meaningful additions such as a suspended-sarcophagus traversal or a second glyph use, not longer corridors.

## 9. Connection to Gate of the West

- The plaza ends at y 5450, and `L_GateWest_Blockout` starts beyond it.
- `REN_DistantGate` is Tomb-owned. How it opens is decided in the GateWest spec (task C-03). The preferred option is *Move Selected Actors to Level* into the GateWest sublevel at an identical transform. World-lock flags that as a level-ownership change, which gets reviewed and re-baselined.
- Until then, the gate and its wings seal the plaza.

## 10. Out of scope

Final art, Anubis animation, Sequencer, star openings below, the black-river material, and additional branches.
