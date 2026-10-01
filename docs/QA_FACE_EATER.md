# REN — Face-Eater QA Matrix (local PIE; all LOCAL_VALIDATION_REQUIRED)

- Run from `L_REN_Slice` (or a GateWest test start with the checkpoint at `REN_GW_Respawn_ArenaApproach`). Record PASS/FAIL, the build/commit, and notes.
- Turn on `bDebugState` for state-transition checks. Use `bDebugTelegraphs` for hit-area checks.
- Spec: `docs/FACE_EATER_BOSS_SPEC.md`. Implementation: `docs/IMPLEMENTATION_P4_FACE_EATER.md`.

## States (S)

| ID | Test | Expected |
|---|---|---|
| S1 | Load the level; observe the boss from the corridor | Dormant: still, no AI, no attacks, bar hidden |
| S2 | Hit the boss while Dormant (reach it through the open entry) | No damage, no state change |
| S3 | Cross ArenaEnter | The slab rises (1.5 s) and the player is inside. Intro: the bar fades in; no attacks during the 2 s |
| S4 | Intro → Combat | Exactly one transition. The first attack is **Heavy Strike** |
| S5 | Combat → Exposed via a valid Glyph | Immediate transition; the remaining recovery is aborted |
| S6 | Exposed → Staggered after 4.0 s (±0.1) | The seal closes, no attacks, no damage |
| S7 | Staggered → Combat after 1.2 s | First attack ≥ 1.0 s later; all glyphs reset |
| S8 | Health ≤ 0 during Exposed | Defeated immediately; nothing runs afterwards |
| S9 | Attempt a state change after Defeated (die, re-enter, hit) | Stays Defeated; slab open |
| S10 | `CheckInvariants` log during a full fight | Zero invariant errors |

## Attacks (A)

| ID | Test | Expected |
|---|---|---|
| A1 | Heavy Strike timing | Anticipation ≈ 1.4 s (locked for the last 0.4 s), active 0.25 s, recovery 3.0 s |
| A2 | Heavy: move after the lock begins | The boss does not re-track (no snap) |
| A3 | Heavy hit area | Hits only inside the r 220 circle 400 ahead; 35% of player MaxHealth; knockback away |
| A4 | Hook Sweep timing | Anticipation ≈ 1.0 s (locked 0.3 s), active 0.35 s, recovery 1.6 s |
| A5 | Sweep hit area | Hits within r 420, ±80° only; behind the boss is safe; 20%; lateral knockback |
| A6 | Each attack hits at most once | Standing in two query samples → one hit |
| A7 | Grab (if kept) | Reach telegraph; ≤ 300 range only. On hit: 25% + push + 0.8 s input lock and **no** glyph window. On miss: 2.2 s recovery + window |
| A8 | Scheduler | A Heavy at least every 3rd attack; never 3 Sweeps in a row; beyond 650 the boss approaches instead of attacking |
| A9 | Dodge i-frames (if a dodge exists) | A hit during i-frames deals 0 |
| A10 | Watchdog | Force a stall (debug); within 6 s it recovers to Combat-idle with a logged error |

## Recovery window and Glyphs (G)

| ID | Test | Expected |
|---|---|---|
| G1 | After a Heavy Strike lands | `bGlyphWindowOpen` true for 2.8 s; the prompt appears on pillars in range |
| G2 | After a Sweep | Window 1.5 s |
| G3 | Valid Glyph during the window | Exposed. The glyph is marked used; the others become non-interactable (the window closed) |
| G4 | Glyph outside the window (Combat, no recovery) | No prompt; E does nothing; the interaction is **not consumed** |
| G5 | Glyph during Exposed, Staggered, Intro, Dormant or Defeated | No prompt, nothing happens |
| G6 | Press E twice quickly on a valid glyph | One Exposed only |
| G7 | Reachability | From the farthest arena point at window open, a pillar can be used before a Heavy window closes (static estimate ≈ 1.4 s) |
| G8 | Reset of glyphs | After Staggered → Combat, every pillar is usable in the next window (including the one used last) |
| G9 | Hint (if kept) | Appears once after 6 deflects or 2 wasted windows; never again |

## Damage gating and health (D)

| ID | Test | Expected |
|---|---|---|
| D1 | Hit in Combat | 0 damage; hit-stop/shake (sound if assigned); the bar does not move; the boss doesn't flinch |
| D2 | Hit in Exposed | −7 per hit; the bar drops |
| D3 | Many hits in one Exposed window | Capped at −35 per cycle |
| D4 | Hit in Staggered, Intro or Dormant | 0 |
| D5 | Fight length | 3–5 Exposed cycles for a first-timer; record the actual number |
| D6 | Bar | Name + one bar only; no numbers, no phase markers |
| D7 | Exposed boss | No movement, no rotation, no attack for the full window |

## Defeat (F)

| ID | Test | Expected |
|---|---|---|
| F1 | Defeat | The bar fades; the slab lowers (exit open); `OnBossDefeated` fires once; TEMP subtitle |
| F2 | After defeat | The boss never attacks, rotates or moves again; glyphs are inert |

## Player death and restart (R) — non-negotiable

| ID | Test | Expected |
|---|---|---|
| R1 | Die in Combat | Respawn at `REN_GW_Respawn_ArenaApproach` facing +Y, full health. The boss is Dormant at Center with full health; the slab is open; the bar is hidden; the glyph window is closed |
| R2 | Re-enter after R1 | The encounter restarts normally (Intro → Combat → Heavy first) |
| R3 | **Restart ×3 in a row** | Identical result each time; no growth in bindings (one Intro per entry, one damage event per hit) |
| R4 | Die **mid-attack** (during anticipation and during active), ×3 | No attack continues after the respawn; no damage applied after death |
| R5 | Die **during Exposed** (force it with debug if needed), ×3 | The seal is closed after reset; the Exposed timer never fires later |
| R6 | Die during Staggered / Intro, ×3 | No stale transition fires after the reset |
| R7 | Duplicates | Outliner during PIE: exactly one `REN_INT_GW_FaceEater`, four glyphs, one boss bar widget |

## Camera and arena (C)

| ID | Test | Expected |
|---|---|---|
| C1 | Camera during the fight | The boss (3.8 m) and its telegraphs stay readable at normal distance; no lock-on needed |
| C2 | Camera between a pillar and a wall | No trapping or violent snapping |
| C3 | Camera at the arena walls and corners | Wall collision is stable; the player stays visible |
| C4 | Camera during Exposed | The seal is visible from the player's typical position |
| C5 | Pillar collision | Player and boss both move around all pillars; no snagging |
| C6 | Corners | Player in each corner: the boss can reach and hit (no safe spot) |
| C7 | Recess | The player in the recess can still be reached and hit |
| C8 | Arena escape | The entry is sealed during the fight; there's no other way out; the boss can't leave the arena |
| C9 | Boss out of bounds | Force the boss's Z < −500 (debug): the watchdog teleports it to Center |
| C10 | Player trapped by the gate | The slab never rises with the player in the threshold (stand at y ≈ 8500, then enter) |

## Hygiene (H)

| ID | Test | Expected |
|---|---|---|
| H1 | Output Log for a full fight + restart ×3 | No "Accessed None", no Blueprint runtime errors |
| H2 | Template assets | `git status` shows no changes under `Content/Variant_Combat/` |
| H3 | World-lock | Tomb, Necropolis and GateWest validate; only reviewed `REN_INT_GW_*` additions |
| H4 | Debug key removed | No debug Exposed key is left in the build |
| H5 | No-audio run | With all sounds unassigned, the fight plays with no errors |
| H6 | Placeholder labels | The boss asset description and the editor TextRender say `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY` |
