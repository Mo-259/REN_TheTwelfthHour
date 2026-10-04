# REN — P0 to Unreal Execution Order

Master order: `docs/tasks/MASTER_LOCAL_EXECUTION_ORDER.md` (Phase A = Phase 1 below, Phase B = Phase 2 below).

Scope: the existing technical slice first, using frozen P0 references (`ProjectDocs/References/UNREAL_VISUAL_HANDOFF.md`). **Local Unreal + MCP only**; cloud sessions cannot change Editor state. Blueprint-first, no C++, no template edits, no final AAA assets yet.

**Workflow per task:** checkpoint commit → inspect → edit → compile → save → PIE → world-lock validate (if any level actor was touched) → update `docs/CURRENT_PROJECT_STATE.md`, `docs/TASK_BOARD.md` and `docs/DEVLOG.md`.

**Visual rule:** anything built from a reference stays `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY` until the owner LOCKS the reference. **Global must-not:** never move world-locked geometry to match an image (CAMERA MOVES, WORLD DOES NOT).

All reference paths below are relative to `ProjectDocs/References/`.

## Phase 1: Tomb technical prologue

| # | Task | Source references | Unreal deliverable | Acceptance criteria | Depends on | Must NOT change |
|---|---|---|---|---|---|---|
| 1 | Tomb material / lighting pass | `Tomb/BurialChamber_v02`, `Tomb/TransitionTunnel_v01`, `Tomb/SideClueChamber_v01`, `ShadowCity/ShadowLightMaterials_v01` (light logic) | `MI_` limestone/plaster/painted-band/floor material instances; lighting pass in `L_Tomb_Blockout` | Floor, path, doors and Nefer silhouette readable everywhere; no crushed blacks; stable exposure; world-lock report = no spatial failures | Existing Tomb blockout | Any actor transform; corridor order; trigger volumes |
| 2 | Sarcophagus visual pass | `Tomb/Sarcophagus_v01` (base) | Proxy mesh + material swap at the **identical transform** | Form, stone language and lid family match the base; world-lock = ASSET CHANGE only; lid/base Z unchanged | 1 | Position, rotation, scale, collision footprint |
| 3 | Blank Cartouche clue visual | `Tomb/BlankCartouche_v02` | Carved empty-ring material/decal on the existing cartouche panel (player-right) | Ring clearly readable from the approach path; **nothing written inside**; trigger `REN_Trigger_BlankCartouche` still fires | 1 | Panel position; trigger |
| 4 | No-Shadow test readability | `Tomb/NoShadowLane_v02`, `01_Nefer/…No_Shadow_State_v02` | One hard directional light setup in the no-shadow zone; props with clear cast shadows | In PIE, props cast obvious, consistent shadows and Nefer casts none, readable without UI | 1, 6 (character) | Zone layout; light positions beyond intensity/angle tuning (document any change) |
| 5 | Exit / transition / reveal treatment | `Tomb/ExitSlab_v01`, `Tomb/TransitionTunnel_v01`, `Tomb/RevealLedge_v02`, `Tomb/VerticalNecropolisVista_v01` | Materials and lighting on the exit door, tunnel and ledge; vista mood lighting | The exit reads as the way out; the ledge edge and drop read; the reveal composition holds | 1 | Door/tunnel/ledge transforms; reveal camera position (camera may be tuned, the world may not) |
| 6 | Nefer visual placeholder integration | `01_Nefer/REF_CHR_Nefer_Hero_Locked_Original_v01` + Body_Turnaround, Linen_Construction, Gameplay_Silhouette | Placeholder mesh/material set on the player character (`TEMP_PLACEHOLDER` label) | Silhouette reads as Nefer (curly head, linen wrap/kilt, lean); **no shadow** behaviour preserved; animations unaffected | — | Player capsule, movement values, camera rig defaults |
| 7 | Reed gameplay-scale placeholder | `09_Weapons/Reed/…ThreeQuarter_v02` (design), `01_Nefer/…Weapon_Sockets_v01`, `Reed/…Sockets_v01`, `…Attack_Use_v01` (relative carry) | Simple Reed proxy mesh attached to a hand socket + belt/back stow socket | Length set as **PROVISIONAL GAMEPLAY SCALE** and tuned in PIE for hand placement, animation clearance and camera readability; value logged in DEVLOG as provisional | 6 | Combat values; no canonical length recorded |
| 8 | Face-Eater production proxy | `B01/Hero_Master_v01`, `…Turnaround_v01`, `…Rig_Notes_Visual_v01`, `…Gameplay_Silhouette_v02`, `…Scale_Comparison_v01` | Proxy body (cartouche head, long limbs, two jaw masks on hafts, exposed rib) on the existing BP_FaceEater | Silhouette readable at gameplay distance; rib and both masks are separate, identifiable components; the boss reads clearly larger than Nefer | BP_FaceEater built per v3 §25 (see `docs/tasks/MASTER_LOCAL_EXECUTION_ORDER.md` Face-Eater authority; older P4/chest-seal specs are obsolete) | Arena geometry; v3 §25 mechanics |
| 9 | Face-Eater gameplay readability | `…Attack_Anticipation_v02`, `…Recovery_State_v02`, `…Weak_Point_or_Objective_v02`, Phase v03 (mechanic) + v04 (gate visual) | Readable tells, exposed-rib punish state, thrown-mask state, two thread targets toward an Egyptian pylon gate | Each tell is visible before damage; the rib punish window is unmistakable; at 30% the two threads are separately targetable and lead to the punish; the gate is Egyptian (no portcullis) | 8 | Phase thresholds/timings from v3 §25 |
| 10 | Anubis production proxy / encounter presentation | `02_Gods/Anubis/…Hero_Master_v02`, `…Turnaround_v01`, `…Gameplay_Silhouette_v01`, `…Scale_Comparison_v01` | Proxy with tall narrow funerary morphology and the correct staff (ankh, one lower crossbar with linen, single shaft); presentation lighting on the bridge | Reads as a non-human funerary organism (not jackal-head-on-man); staff geometry matches Hero v02; encounter framing per existing cinematic spec | 5 | Bridge/tower transforms; dialogue canon |

**Exit gate for Phase 1:** a full PIE run from the Tomb through the reveal to the Face-Eater defeat with no BLOCKER/HIGH bugs, world-lock clean for all three sublevels, and the owner's visual sign-off on tasks 1–5.

## Phase 2: official v3 vertical slice (after Phase 1 is validated locally)

Source: v3 Bible §37 (test section from City of Shadows + House of Life, target 45–60 min).

Required content:
- rest quay; main path + shortcut; small daylight field; M02 memory;
- six enemies from two families; one elite;
- full three-phase B02 Kheft; B03 introduction;
- twelve nodes available from the first two skill trees;
- CS03.

Production gate:
- controls work without effects; attacks readable in grey arenas;
- three builds achieve real wins; retry is close by;
- daylight does not break Sheut; CS03 preserves the space.

Order (do not expand beyond this):
1. **Gameplay-readable blockout:** Shadow City (entry, main street, shortcut, rest bank, Kheft arena 22 m with three torches) and House of Life (archive entry, scribal halls, copying hall 18×24 m). Use the `ShadowCity/*` and `HouseLife/*` references for visual direction only; the layout comes from the v3 Bible and blockout review.
2. **Checkpoint / retry flow:** rest anchor, close retry, save state.
3. **Enemies required by the slice:** two families, six enemies plus one elite, from `07_Enemies` sheets; creature design and tells only, ignoring the E01–E10 labels and scale figures.
4. **Sheut:** relationship states and shadow transfer, per `Sheut/Relationship_States_v03` and the cross-asset rule.
5. **Kheft (B02):** full three phases per v3 §25, using the B02 reference set.
6. **Skill trees:** the first two trees, 12 nodes, per v3 §22.
7. **Hori / Black Hand (B03) introduction:** per v3 §25 and the B03 set; Hori is never a damage target.
8. **CS03 and spatial continuity:** **CS03** (v3 §8, Hour 2, City of Shadows) is the scene required by v3 §37 and must preserve the established space (world-lock validated). **CS04** (v3 §9, Hour 3, House of Life) is the separate Hour-3 scene tied to B03; it is not in the §37 required list. B03 = Hori / Black Hand.

Do not expand into the rest of the game.
