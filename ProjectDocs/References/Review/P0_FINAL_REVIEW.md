# REN — P0 Visual Production: Final Review

Date: 2026-10-03. All images are **low-quality drafts** with status **NEEDS_REVIEW**. Nothing is LOCKED; locking is owner-controlled.
Machine-readable QA verdicts: `AUTOPILOT_QA.json` (autopilot batches AP1–AP8). The verdicts for earlier batches come from the owner-facing batch reports and are summarised below.

## Coverage

| Metric | Value |
|---|---|
| P0 slots in `GENERATION_JOBS.jsonl` | **133** |
| Slots with an existing, valid PNG in the correct asset folder | **133 (100%)** |
| PASS | **121** |
| NEEDS_FIX (kept as usable drafts, minor issues) | **11** |
| BLOCKED_VISUAL_QA (draft kept, partially usable) | **1** |
| SAFETY_BLOCKED | **0** (the Face-Eater scale refusal was resolved with a low-detail retry) |
| Image API requests during autopilot | **62** (AP1–AP7: 8 each; AP8: 6) |
| Quality used | LOW only (every run's `LAST_GITHUB_GENERATION.json` reports `low`) |

Audit checks:
- no missing files, no duplicate slot files, no files in the wrong folder;
- every continuity, identity and multi-image job recorded the expected `sources` (image-token counts confirm each image was received);
- no text-only fallback (fail-closed);
- no HIGH quality used.

## Unresolved / limited slots

| Slot | Verdict | Note |
|---|---|---|
| W01.Physical_Dimensions | BLOCKED_VISUAL_QA | Two attempts. Both render the Reed about as tall as a man. The design is correct. The v3 Bible gives **no** weapon measurement, so Reed length is **PROVISIONAL GAMEPLAY SCALE**, tuned in Unreal; carry images (C01.Weapon_Sockets v01, W01.Sockets / Attack_Use) are relative guidance only. |
| B01.Phase_States | NEEDS_FIX | No more spend, by owner rule. Use **v03 for the mechanic** (threads from the body to the masks, masks at the gate) and **v04 for the Egyptian pylon gate**. |
| C04.Materials | NEEDS_FIX (owner) | Material reference only; the staff geometry comes from Hero Master v02. |
| E01, E02, E08 | NEEDS_FIX | Early sheets. E01/E02 have rendered text; E02 has a beam-like VFX; E08 is generic shadow-figure drift. |
| W01.Material_Closeups | NEEDS_FIX | Some panels show variant geometry; materials usable. |
| B02.Arena_Relationship | NEEDS_FIX | Minor crenellated wall tops; very dark. |
| W01.Hand_Scale, W02.Physical_Dimensions, W03.Gameplay_Silhouette, U01.Grip | NEEDS_FIX | Minor composition issues; their purpose is covered by sibling views. |

**Known global limitation (documented, not regenerated, per owner rule):** the enemy sheets E01–E10 were made before the no-text / neutral-scale policy. They contain model-rendered labels and **generic "Nefer" scale figures that are NOT the locked Nefer**. Do not use those figures as Nefer identity or scale. Every sheet made after the policy (E11–E12 onward) uses neutral silhouettes or the real Nefer master.

## Continuity bases (`CONTINUITY_BASES.json`, not locked)

| Asset | Base |
|---|---|
| Nefer (identity master) | locked original |
| Anubis | Hero Master v02 |
| Face-Eater | Hero v01 |
| Kheft | Hero v02 |
| Sheut | Hero v02 (plus the cross-asset Sheut rule) |
| Thoth | Hero v02 |
| Hori | v01 |
| Black Hand | Hero v02 |
| Reed | ThreeQuarter v02 |
| Djed | ThreeQuarter v04 |
| Chaos Spear | ThreeQuarter v02 |
| Wedjat | ThreeQuarter v01 |
| Tomb sarcophagus | Sarcophagus v01 (visual/material only) |

## Contact sheets (deterministic, no API)

**Optional review artifacts, not an Unreal implementation blocker. Not yet in the repository:** this folder is Git-LFS-tracked, and LFS uploads were refused (HTTP 403) from the cloud session. The sheets were delivered to the owner directly. They can be regenerated locally from this repo with `pip install pillow` and the contact-sheet script described in the owner report, then committed via Git LFS.


`P0_MASTER_CONTACT_SHEET.jpg`, `P0_NEFER_…`, `P0_GODS_…`, `P0_HUMANS_…`, `P0_SOUL_PARTS_…`, `P0_MAIN_BOSSES_…`, `P0_ENEMIES_…`, `P0_WEAPONS_UTILITY_…`, `P0_TOMB_…`, `P0_SHADOW_CITY_…`, `P0_HOUSE_OF_LIFE_…` (all `_CONTACT_SHEET.jpg` in this folder). The labels are drawn deterministically, not by the image model.

## Recommended for later HIGH finalization (owner: `FINALIZE <asset>`)

**Priority 1 (vertical slice):**
- Nefer Head_Master / Body_Turnaround
- Face-Eater Hero v01 + Turnaround + Gameplay_Silhouette
- Anubis Hero Master v02 + Turnaround
- Nameless Dead (E01, after a no-text regeneration)
- Tomb Sarcophagus v01, Blank Cartouche v02, No-Shadow Lane v02
- Reed ThreeQuarter v02

**Priority 2:**
- Kheft Hero v02 + Phase_States v02
- Sheut Hero v02 + Relationship_States v03
- Black Hand Hero v02 + Phase_States
- Thoth Hero v02
- House of Life Scribal Halls / Light Court
- Shadow City Entry / Kheft Arena

Everything else can stay as a draft reference.

## Next step for the Unreal vertical slice

1. Use these references to drive the Tomb prologue blockout-to-art pass (runtime order per v3 §7: **Face-Eater before Anubis**; any build order is implementation scheduling only), starting with Tomb materials (sarcophagus, cartouche, no-shadow lane lighting) per `docs/tasks/MASTER_LOCAL_EXECUTION_ORDER.md`. Unreal transforms stay the spatial authority; reference images never move world geometry.
2. Model the Face-Eater against the B01 set (Hero, Turnaround, Rig Notes, Silhouette, Weak Point v02, Phase v03 for the mechanic and v04 for the gate).
3. Model Nefer and the Reed (C01 set plus W01 set; Reed length = PROVISIONAL GAMEPLAY SCALE, tuned in Unreal).

This needs local Unreal; nothing here changes Editor state.
