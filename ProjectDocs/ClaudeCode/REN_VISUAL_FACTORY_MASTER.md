# REN — Claude Code Visual Factory Master Rules

## Mission

Operate as the visual-production controller for **REN — THE TWELFTH HOUR**.

You are not allowed to improvise canon, silently replace approved identity, or call a generated image "final" because it looks attractive.

The system already contains:
- the v3 Production Bible,
- asset briefs,
- a reference manifest,
- a generation queue,
- current supplied/generated images,
- QA rules,
- conflict notes.

Use those. Do not rebuild the planning layer.

## Authority order

1. `ProjectDocs/SourceOfTruth/REN_Complete_Game_Production_Bible_AR_v3.pdf`
2. Current locked gameplay mechanic / encounter requirement
3. `ProjectDocs/References/DESIGN_AUTHORITY.md`
4. `ProjectDocs/References/CHANGE_CONFLICTS.md`
5. A `LOCKED` visual master
6. An `APPROVED_BASE` visual reference
7. Asset-specific `ASSET_BRIEF.md`
8. `NEEDS_REVIEW` candidate
9. `PROVISIONAL` specification
10. `ARCHIVED` work

A lower level never silently overrides a higher level.

## Hard visual direction

REN must look like a coherent photorealistic AAA game.

Use the supplied Nefer master as the rendering-realism benchmark:
- physically plausible anatomy,
- real skin and surface breakup,
- real linen fibers,
- real aged leather,
- real bronze/copper,
- real stone,
- restrained lighting,
- neutral production readability.

Avoid:
- generic Egyptian fantasy,
- cosplay,
- plastic skin,
- fashion-editorial posing,
- MMO armor,
- superhero anatomy,
- excessive gold,
- neon,
- cyberpunk,
- digital glitches,
- opaque fog hiding anatomy,
- random floating magical particles,
- fake unreadable hieroglyphic "translations",
- poster composition when a production reference was requested.

Ancient Egypt first. Mythology second. Fantasy third.

## Divine anatomy

Do not default to `human body + animal head`.

A god or monster may be:
- human-dominant,
- animal-derived,
- funerary-object-derived,
- stone/resin/sand/water-derived,
- architectural,
- shadow-derived,
- writing/symbol-derived,
- hybrid.

But it must remain:
- physically believable,
- readable from multiple gameplay angles,
- riggable in principle,
- capable of clear anticipation / active / recovery states,
- able to make real contact with the environment.

## Critical canon corrections

### Nefer
- Face/identity is locked to the supplied master.
- Human, lean, tired, observant former scribe.
- Never a warrior prince.
- No arbitrary face redesign across progression.

### Anubis
Rejected direction:
`muscular human male + jackal head`.

Required direction:
- complete funerary divine organism,
- extremely tall, narrow, vertical,
- long controlled limbs,
- dropped/slender shoulders,
- precise functional hands,
- black short fur flowing into dark organic skin / funerary resin / basalt-like material,
- integrated off-white funerary linen,
- restrained staff,
- stillness = power,
- must not read as Seth.

### Seth
- Set-animal identity; not jackal/wolf/dog/fox.
- dry desert morphology, motion, spear, asymmetry.
- must not read as Anubis.

### Face-Eater
Preserve the empty vertical cartouche identity when compatible, but current v3 combat rules win.
Combat v2 must visually support:
- two jaw-mask structures,
- exposed rib gameplay target,
- thrown-mask state,
- phase-3 visible threads/tethers,
- readable sweep/grab/recovery.
Do not use the obsolete chest-seal-only fight as current gameplay authority.

### Nameless Dead
Current v3 canon wins over the older "normal living human identity-erasure" direction.

### Meru
One person, three related visual states:
1. Teacher
2. Keeper of the Unname
3. Unwritten
Never generic dark wizard coding.

### Apep
A recurring visual system, not one normal snake boss.

### The Unname
Semantic erasure made physical.
No generic smoke demon, purple cosmic humanoid, AI glitch creature, or tentacle cliché.

## Production behavior

One distinct reference slot = one distinct generation job.

Technical multi-view sheets are allowed only when the slot explicitly calls for a turnaround/morphology/material/pose sheet.
Do not substitute giant collages for individual reference assets.

Never overwrite:
- `LOCKED`
- supplied originals
- approved candidates

Create a new version instead.

Generated image default status:
`NEEDS_REVIEW`

Only the human owner may promote a generated reference to:
`LOCKED`

Claude may recommend promotion to:
`APPROVED_BASE`
but must not silently do so.

## Image QA gate

Before accepting a candidate:
1. Canon match
2. Identity preservation where relevant
3. Photorealism
4. Anatomical plausibility
5. Silhouette readability
6. Gameplay facing / attack-source readability
7. Materials
8. Scale plausibility
9. Environment/prop continuity if relevant
10. No forbidden visual language
11. File dimensions
12. Naming/path correctness

If local image viewing is unavailable, do not self-approve visually.
Leave it `NEEDS_REVIEW`.

## World continuity

Absolute rule:
**CAMERA MOVES. WORLD DOES NOT.**

Never solve a reference frame by moving a door, column, light, resonator, platform, or arena landmark that is already spatially locked.

## Scope order

Do not start late-game breadth while P0 is incomplete.

P0 order:
1. Nefer missing production references
2. Anubis
3. Face-Eater Combat v2
4. Kheft
5. Sheut
6. Thoth
7. Hori
8. Black Hand
9. Enemies 01E–12E
10. Reed / Djed / Chaos Spear / Wedjat refs needed by the slice
11. Shadow City
12. House of Life
13. P0 props
14. P0 VFX

After P0 passes review:
- P1 Hours 4–6
- P2 Hours 7–9
- P3 Hours 10–12
- P4 optional/secondary breadth

## Git safety

- Never `git reset --hard`.
- Never delete user work to make the tree clean.
- Never edit `Content/Variant_Combat/` as part of the visual factory.
- Do not auto-push.
- Do not commit secrets.
- Never write `OPENAI_API_KEY` into the repository.
- If adding Git LFS rules, inspect existing `.gitattributes` first and merge rather than replace.

## Stop conditions

Stop and report instead of improvising if:
- source-of-truth files are missing,
- a supposedly locked identity image is referenced but absent,
- generated output contradicts canon after two targeted retries,
- image generation credentials are unavailable,
- an API/tool refuses requested generation,
- a file would overwrite locked work,
- there is an unresolved source conflict not covered by `CHANGE_CONFLICTS.md`.

Do not solve blockers by making up canon.
