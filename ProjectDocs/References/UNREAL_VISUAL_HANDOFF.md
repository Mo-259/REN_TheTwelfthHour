# REN — Unreal Visual Handoff (implementation authority)

Status: **P0 visual production FROZEN** (2026-10-04). All references are low-quality drafts, `NEEDS_REVIEW`, none LOCKED. Locking is owner-controlled. No further image generation, no P1 and no HIGH promotion without explicit owner instruction.

**Authority order:**
1. v3 Bible (`ProjectDocs/SourceOfTruth/REN_Complete_Game_Production_Bible_AR_v3.pdf`, mirrored in `References/Sources/REN_V3_*_AR.md`)
2. Unreal level actor transforms (spatial authority)
3. this document
4. generated images (visual reference only)

Generated images are **visual references, not canon**. They never define narrative, gameplay values, measurements or level layout. If an image conflicts with the v3 Bible, **the Bible wins**.

All paths below are relative to `ProjectDocs/References/`.

## A. Current primary bases

| Asset | Path | Authoritative for | NOT authoritative for |
|---|---|---|---|
| Nefer (locked identity master) | `01_Nefer/REF_CHR_Nefer_Hero_Locked_Original_v01.png` | face, facial structure, age, short dark curly hair, skin tone, tired expression, lean proportions, linen scribe costume (wrap, rope belt, faience pendant, arm wraps, sandals) | weapon size, combat poses, exact height in cm |
| Anubis | `02_Gods/Anubis/REF_GOD_Anubis_Hero_Master_v02.png` | tall narrow non-human funerary morphology, black funerary surfaces, restrained linen sash, **staff geometry** (ankh top, one lower crossbar with hanging linen, single straight shaft) | encounter staging, height in cm, abilities |
| Face-Eater (B01) | `05_Main_Bosses/B01_FaceEater/REF_BOSS_FaceEater_Hero_Master_v01.png` | identity: empty vertical cartouche head, long funerary limbs, two jaw masks on hafts, exposed rib, funerary linen/resin materials | arena layout (v3 §25: 24×20 m courtyard, three statues), phase timings, attack values |
| Kheft (B02) | `05_Main_Bosses/B02_Kheft/REF_BOSS_Kheft_Hero_Master_v02.png` | Egyptian shadow-guardian identity: shaved head, broad collar, pleated kilt, shears-headed bronze staff, oil lamp | arena layout (v3: 22 m Shadow City courtyard, three torches), mechanics |
| Sheut (C20) | `04_Soul_Parts/Sheut/REF_SOUL_Sheut_Hero_Master_v02.png` | flat-black, faceless cast-shadow form linked to Nefer at the feet | anything humanoid beyond Nefer's outline; Sheut is never a body, woman, face, ghost or smoke (cross-asset rule in `CONTINUITY_BASES.json`) |
| Thoth (C05) | `02_Gods/Thoth/REF_GOD_Thoth_Hero_Master_v02.png` | coherent non-human ibis morphology, backward-bending legs, wing-arm digits, reed and palette writing logic | height, abilities |
| Hori (C18) | `03_Humans/Hori/REF_CHR_Hori_Hero_Master_v01.png` | identity: face, shaved head, age, linen scribe clothing, writing board, bandaged injured hand | Black Hand form (separate base) |
| Hori / Black Hand (B03) | `05_Main_Bosses/B03_HoriBlackHand/REF_BOSS_HoriBlackHand_Hero_Master_v02.png` | separate matte-black ink / written-erasure parasite at the hand and forearm; Hori a protected witness | phase mechanics (v3 §25 governs), arena layout |
| Reed (W01) | `09_Weapons/Reed/REF_WEAPON_Reed_ThreeQuarter_v02.png` | design: single jointed reed stem, cut ink-darkened tip, leather and cord grip, proportions of its parts | **length**, which is **PROVISIONAL GAMEPLAY SCALE** (see note) |
| Djed (W02) | `09_Weapons/Djed/REF_WEAPON_Djed_ThreeQuarter_v04.png` | long staff, small Djed stacked-band stone head, wooden shaft, lashings, stone end cap | exact length (provisional gameplay scale) |
| Chaos Spear (W03) | `09_Weapons/ChaosSpear/REF_WEAPON_ChaosSpear_ThreeQuarter_v02.png` | one long spear: dark iron leaf head with red inlay, red-stone and dark shaft sections, bronze bands, butt cap | exact length (provisional gameplay scale) |
| Wedjat utility (U01) | `09_Weapons/WedjatUtility/REF_WEAPON_WedjatUtility_ThreeQuarter_v01.png` | compact Wedjat-eye tool, faience/lapis/bronze, wrapped grip, short point; a utility tool, not a fourth weapon | size in cm |
| Tomb sarcophagus | `11_Environments/Details/Tomb/Sarcophagus/REF_ENV_Sarcophagus_Gameplay_v01.png` | sarcophagus form, stone language, lid design family, weathering | placement, size and position in the level (the Unreal Tomb is the authority) |

**Weapon scale note:** the v3 Bible gives **no** physical measurement for any weapon. Reed, Djed, Chaos Spear and Wedjat lengths are **PROVISIONAL GAMEPLAY SCALE**. Tune them in Unreal against Nefer's proportions, hand placement, animation, combat readability and camera distance. Generated images may suggest relative scale only (for example, the Reed carried by Nefer in `01_Nefer/REF_CHR_Nefer_Weapon_Sockets_v01.png`). They never set a canonical number.

## B. Supporting references (strongest per priority asset)

| Asset | Turnaround | Materials | Silhouette | Gameplay states | Rig notes | Weak points | Scale |
|---|---|---|---|---|---|---|---|
| Nefer | `01_Nefer/REF_CHR_Nefer_Body_Turnaround_v01.png`, `…Head_Master_v01.png` | `…Linen_Construction_v01.png`, `…Skin_Closeups_v01.png`, `…Sandals_v01.png`, `…Hand_Anatomy_v01.png` | `…Gameplay_Silhouette_v01.png` | `…No_Shadow_State_v02.png`, `…Weapon_Sockets_v01.png` | — | — | `…Scale_Comparison_v01.png` |
| Face-Eater | `05_Main_Bosses/B01_FaceEater/REF_BOSS_FaceEater_Turnaround_or_Morphology_v01.png` | `…Materials_v01.png` | `…Gameplay_Silhouette_v02.png` | `…Attack_Anticipation_v02.png`, `…Recovery_State_v02.png`, Phase v03 + v04 (see C) | `…Rig_Notes_Visual_v01.png` | `…Weak_Point_or_Objective_v02.png` | `…Scale_Comparison_v01.png` (low-detail stand-in beside real Nefer), arena `…Arena_Relationship_v01.png` |
| Anubis | `02_Gods/Anubis/REF_GOD_Anubis_Turnaround_or_Morphology_v01.png` | `…Materials_v01.png` (limited, see C) | `…Gameplay_Silhouette_v01.png` | — | — | — | `…Scale_Comparison_v01.png` |
| Kheft | `05_Main_Bosses/B02_Kheft/REF_BOSS_Kheft_Turnaround_or_Morphology_v01.png` | `…Materials_v01.png` | `…Gameplay_Silhouette_v01.png` | `…Phase_States_v02.png`, `…Attack_Anticipation_v01.png`, `…Recovery_State_v01.png` | `…Rig_Notes_Visual_v01.png` | `…Weak_Point_or_Objective_v03.png` | `…Scale_Comparison_v01.png`, arena `…Arena_Relationship_v01.png` |
| Sheut | — | — | — | `04_Soul_Parts/Sheut/REF_SOUL_Sheut_Relationship_States_v03.png` | — | — | — |
| Hori / Black Hand | `05_Main_Bosses/B03_HoriBlackHand/REF_BOSS_HoriBlackHand_Turnaround_or_Morphology_v01.png` | `…Materials_v01.png` | `…Gameplay_Silhouette_v01.png` | `…Phase_States_v01.png`, `…Attack_Anticipation_v01.png`, `…Recovery_State_v01.png`; Hori alone `03_Humans/Hori/REF_CHR_Hori_Gameplay_v01.png` | `…Rig_Notes_Visual_v01.png` | `…Weak_Point_or_Objective_v02.png` | `…Scale_Comparison_v01.png`, arena `…Arena_Relationship_v02.png` |
| Thoth | `02_Gods/Thoth/REF_GOD_Thoth_Turnaround_or_Morphology_v01.png` | — | — | — | — | — | — |
| Reed | `09_Weapons/Reed/REF_WEAPON_Reed_Side_A_v01.png`, `…Side_B_v01.png`, `…Front_Thickness_v01.png` | `…Material_Closeups_v01.png` (limited) | `…Gameplay_Silhouette_v01.png` | `…Attack_Use_v01.png`, `…Sockets_v01.png` | — | — | `…Hand_Scale_v01.png` (relative only) |
| Djed / Chaos Spear / Wedjat | `Side_A`, `Side_B`, `Front_Thickness` in each `09_Weapons/<Weapon>/` folder | `Material_Closeups` | `Gameplay_Silhouette` | `Attack_Use`, `Sockets` | — | — | `Hand_Scale`, `Physical_Dimensions` (relative only) |

## C. Do-not-use / limited-use references

- **Face-Eater Phase States:**
  - `…Phase_States_v03.png` = **mechanic support**: masks present, two threads from the body to the masks at the gate.
  - `…Phase_States_v04.png` = **Egyptian pylon gate visual support** only; its threads run from the hand, which is wrong.
  - **Neither is complete authority alone.** Phase rules come from v3 §25: two jaw masks + exposed rib; mask throw at 65%; masks gather at the gate and are dragged by thread at 30%; break two threads, then punish. Earlier v01/v02 are superseded.
- **Anubis Materials v01** (`02_Gods/Anubis/REF_GOD_Anubis_Materials_v01.png`): material reference only. Its staff (split shaft) is **not** staff geometry.
- **Reed Material Closeups** (`09_Weapons/Reed/REF_WEAPON_Reed_Material_Closeups_v01.png`): material reference only. The variant tips and curves are **not** alternate geometry.
- **Reed Physical Dimensions** (`09_Weapons/Reed/REF_WEAPON_Reed_Physical_Dimensions_v01.png`, `…_v02.png`): **BLOCKED and non-authoritative.**
- **Early enemy sheets E01–E10** (`07_Enemies/*/…Enemy_Gameplay_Sheet_v01/v02.png` generated before the no-text policy): their **"Nefer" scale figures are generic people, invalid for scale and identity**. All **generated labels and text** in those sheets are invalid. Use them only for creature design, tells and materials.
- **Superseded drafts:** any lower version where a higher `_vNN` exists for the same view, for example Kheft Hero v01, Sheut Hero v01, Thoth Hero v01, Djed ThreeQuarter v01–v03 and Chaos Spear ThreeQuarter v01. The archived Anubis `REF_GOD_Anubis_Hero_v02.png` is **not** the Anubis base.

## D. Environment authority

**Tomb:** the Unreal level (`L_Tomb_Blockout` within `L_REN_Slice`) is the spatial authority. **CAMERA MOVES. WORLD DOES NOT.**
- Generated Tomb images (`11_Environments/Details/Tomb/*`) control only **materials, lighting, ageing, atmosphere, prop treatment and visual language**.
- They never move doors, columns, clue positions or the sarcophagus, never change corridor order, and never resize rooms.
- Validate any level change with the world-lock tools (`ProjectDocs/WorldLocks/`).

**Shadow City and House of Life** (`11_Environments/Details/ShadowCity/*`, `…/HouseLife/*`):
- **visual direction only**: material logic, light and shadow readability, landmark style, buildability cues;
- **layout** comes from the v3 Bible (§8, §9, §25 arena sizes: Kheft 22 m with three torches; B03 copying hall 18×24 m with tables and a fixed ink basin) and from an approved Unreal blockout. A generated composition is never a floor plan.
