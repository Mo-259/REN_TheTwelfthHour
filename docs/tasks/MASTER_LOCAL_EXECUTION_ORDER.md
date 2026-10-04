# REN — Master Local Execution Order (current)

Rebuilt on main on 2026-10-04 from:
- the v3 Bible (`ProjectDocs/SourceOfTruth/REN_Complete_Game_Production_Bible_AR_v3.pdf`; text mirrors in `ProjectDocs/References/Sources/REN_V3_*_AR.md`)
- `ProjectDocs/References/UNREAL_VISUAL_HANDOFF.md`
- `ProjectDocs/Unreal/P0_TO_UNREAL_EXECUTION_ORDER.md`
- `docs/CURRENT_PROJECT_STATE.md`

It **replaces** the older planning version that lives only on branch `claude/festive-mendel-yqepmq`. That branch is **not merged** and must not be merged wholesale: its Face-Eater specifications predate v3 §25 and are obsolete.

Execution: **local Unreal + MCP only.** A cloud session never makes runtime work DONE. Blueprint-first; no C++ without approval; never edit template assets. **CAMERA MOVES. WORLD DOES NOT.**

## Authority

1. **v3 Bible.** Overrides every older doc and every generated image on gameplay, mechanics, values and narrative.
2. **Unreal actor transforms.** Spatial authority once an environment exists; validate with the world-lock tools in `ProjectDocs/WorldLocks/`.
3. **`UNREAL_VISUAL_HANDOFF.md`.** Visual authority for appearance (frozen P0 references; none LOCKED).
4. Repo planning docs in `docs/`. Older sections that conflict with v3 are superseded (see the Face-Eater section below).

## Current state (verified facts only, from `docs/CURRENT_PROJECT_STATE.md`)

**Verified locally:**
- `/Game/REN/Worlds/Tomb/L_Tomb_Blockout` greybox, built by the v3 opening builder: burial chamber, sarcophagus placeholder/lid/platform, blank cartouche panel (player-right), main corridor, no-shadow test zone, left side clue chamber, exit door, transition tunnel, reveal ledge, distant necropolis blockouts, temporary lights, player start;
- triggers `REN_Trigger_BlankCartouche`, `REN_Trigger_ShadowClue`, `REN_Trigger_SideClue`, `REN_Trigger_ExitReveal`.

**Not yet implemented or verified:**
- custom Nefer, Reed, interaction system, no-shadow runtime;
- prompts/UI, combat changes, Face-Eater boss, Anubis encounter;
- checkpoints/save, Sequencer.

**First step of every local session:** audit the live project. Do not assume anything beyond this list exists.

---

## PHASE A — Technical Prologue / Tomb

> Task numbers in this phase are **IMPLEMENTATION ORDER ONLY**, not playable order. The playable order follows the Hour 1 rule below (Face-Eater < Anubis).

Purpose: prove the pipeline (movement, interaction, no-shadow, a boss, readability) on the existing Tomb before the official slice.

Detailed tasks, sources, deliverables and acceptance criteria are in `ProjectDocs/Unreal/P0_TO_UNREAL_EXECUTION_ORDER.md` (Phase 1). Order:

1. Tomb material/lighting pass
2. Sarcophagus visual pass, at the identical transform
3. Blank Cartouche clue visual
4. No-Shadow test readability
5. Exit/transition/reveal treatment
6. Nefer placeholder integration
7. Reed gameplay-scale placeholder (**PROVISIONAL GAMEPLAY SCALE**; the v3 Bible gives no measurement)
8. Face-Eater production proxy
9. Face-Eater gameplay readability
10. Anubis production proxy and encounter presentation

**Required runtime systems** (build only as each task needs them):
- interaction input, trace and interface;
- Blank Cartouche and Exit Door interactions;
- no-shadow runtime;
- Reed base attacks, dodge, health/damage;
- checkpoint/retry.

**Phase A exit gate:**
- full PIE run of the prologue in **v3 runtime order** (Tomb → … → Face-Eater defeat → Anubis), the Face-Eater encounter strictly before Anubis;
- no BLOCKER/HIGH bugs;
- world-lock clean;
- owner visual sign-off on Tomb tasks 1–5.

**Hour 1 runtime order (RESOLVED in favour of v3, owner decision 2026-10-04):**

- **Hour 1 ordering rule (v3 §7, narrative/runtime authority):** in the playable game, the **Face-Eater (B01) encounter occurs BEFORE the Anubis encounter** (Face-Eater < Anubis). The v3 Hour-1 sequence is: wake in the tomb (CS01) → corridor with the guard → M01 memory → B01 Face-Eater (CS02; tomb courtyard 24×20 m, three statues) → Anubis sees the body seal. **Gate:** v3 §25 places a gate inside the B01 encounter (in phase 3 the masks gather around the gate), and v3 §33 puts the B01 entry 'at the door'. A separate 'Gate of the West' route beat and the exact position of the Vertical Necropolis reveal are **not established by v3** and stay flexible, provided Face-Eater < Anubis holds.
- **Authority:** narrative/runtime order = **v3 Bible**; spatial authority = the **existing Unreal level once validated**; implementation scheduling **may differ from narrative chronology but must be labelled IMPLEMENTATION ORDER ONLY** and never changes the runtime sequence.
- The Phase A task numbering above (Face-Eater tasks 8–9 before the Anubis task 10) is **IMPLEMENTATION ORDER ONLY**. Building or testing Anubis before the Face-Eater is allowed for technical convenience, but the shipped runtime sequence must keep Face-Eater < Anubis.

## Face-Eater implementation authority (applies to Phase A Tasks 8–9)

- **Mechanics: v3 §25 B01 only.**
  - Combat form: a hollow stone face over an exposed parasite; masks are attached to the body, not extra enemies.
  - Passive: it steals a voice, not a whole name; a mask blocks core hits until it cracks.
  - Weak point: the exposed side after the bite; the mask armour breaks to a Reed heavy attack, no advanced skill needed.
  - Attacks and tells: Calling Bite (inhale and carving widens; counter by side-exit, or parry then strike the neck); Mask Sweep (from phase 2); Face Spit (from phase 2); Hollow Scream (from phase 3).
  - Phase 1, "silent masks": horizontal then vertical slap. Parry the first, exit the second, strike the rib.
  - Phase 2 at 65%: it wears the guard's spear mask and throws a mask to the player's announced position. Strike the grounded mask to open the chest.
  - Phase 3 at 30%: the masks gather around the gate and it drags them by thread. Separate two threads during its lunge recovery, then punish up close.
  - Hour 1, scene CS02; arena: tomb courtyard 24×20 m with three statues.
- **Appearance:** the frozen P0 B01 set (`UNREAL_VISUAL_HANDOFF.md` §A–C). Identity is Hero v01. Phase States v03 supports the mechanic and v04 supports the Egyptian gate; neither is complete authority alone.
- Where the sheets disagree: **the Bible defines mechanics; the strongest approved references define appearance.**
- **Obsolete, never reintroduce:** chest seal exposed by Glyph interaction, Glyph pillars, hooked/extraction staff as the core mechanic, and any old "Exposed via glyph" state. These appear in older sections of `docs/VERTICAL_SLICE_SPEC.md` and `docs/GAMEPLAY_SYSTEMS.md` (now marked superseded) and in the unmerged branch's `FACE_EATER_BOSS_SPEC.md` / `IMPLEMENTATION_P4_FACE_EATER.md` / `QA_FACE_EATER.md`.
- **Useful, non-conflicting practices** (recreated here; the old docs are not merged):
  - one-shot hit windows synchronised to animation;
  - no hidden damage caps;
  - no softlocks;
  - the boss stays inside arena bounds;
  - retry resets the boss cleanly without duplicates;
  - every tell is readable before damage.

---

## PHASE B — Official Vertical Slice: City of Shadows + House of Life

Starts only after the Phase A exit gate passes. Source: **v3 §37**, a 45–60 minute test section.

**Required content (v3 §37):**
- rest quay; main path + shortcut; small daylight field; **M02** memory;
- six enemies from two families; one elite;
- **B02 Kheft complete with three phases**; **B03 Hori/Black Hand introduction**;
- **twelve nodes** from the first two skill trees;
- scene **CS03**.

**Pre-production gate (v3 §37):**
- controls work without effects; attacks readable in grey arenas;
- three builds achieve real wins; retry is close by;
- daylight does not break Sheut; **CS03 preserves the space**.
- Reject moving forward if understanding an attack requires memorising a video, or if B02 needs lighting that hides boundaries.

**Scene IDs (explicit; never abbreviate):**
- **CS03** (v3 §8, Hour 2, City of Shadows): the scene required by §37 for the slice.
- **CS04** (v3 §9, Hour 3, House of Life): the Hour-3 scene associated with B03. It is not part of the §37 required list, which asks only for a B03 *introduction*; build it only if the owner adds it.

**Order** (details in `P0_TO_UNREAL_EXECUTION_ORDER.md` Phase 2):
1. Gameplay-readable blockout. Shadow City: entry, main street, shortcut, rest quay, daylight field, Kheft arena (22 m, three torches). House of Life: archive entry, scribal halls, copying hall 18×24 m with tables and a fixed ink basin. Images are visual direction only.
2. Checkpoint/retry flow.
3. The slice's enemies: two families, six enemies plus one elite.
4. Sheut relationship states and shadow transfer (cross-asset Sheut rule).
5. B02 Kheft, three phases, per v3 §25.
6. Skill trees: the first two trees, 12 nodes, per v3 §22.
7. B03 Hori/Black Hand introduction, per v3 §25; Hori is never a damage target.
8. CS03 with spatial continuity validated by world-lock.

## PHASE C — Expansion (only after slice validation)

Locked until the Phase B gate passes and the owner approves. No full-game implementation planning now.

## Optional review artifacts (not blockers)

P0 contact sheets (`ProjectDocs/References/Review/P0_*_CONTACT_SHEET.jpg`) are **optional review artifacts**, not an Unreal implementation blocker. Claude Cloud cannot upload Git LFS (403). The owner can regenerate them locally and commit them with Git LFS whenever convenient. Do not retry an LFS upload from the cloud.
