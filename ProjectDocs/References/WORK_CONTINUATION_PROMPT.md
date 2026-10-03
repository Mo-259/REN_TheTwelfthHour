# ChatGPT Work — Continue Visual Production

Continue from the existing REN Visual Production Pack v3 Design Progress 01.

Do NOT rebuild the folder structure.
Do NOT rewrite the asset briefs.
Do NOT recreate the manifest.
Do NOT spend the session expanding planning documentation.

The planning/scaffolding phase already exists.

## Primary task

Produce actual INDIVIDUAL visual references, one asset at a time, using:

- `GENERATION_JOBS.jsonl`
- `DESIGN_AUTHORITY.md`
- `REFERENCE_MANIFEST.json`
- `QA_ACCEPTANCE.md`
- each asset's `ASSET_BRIEF.md`

## Immediate order

1. Anubis review/redesign.
2. Face-Eater Combat v2.
3. Kheft.
4. Sheut.
5. Thoth.
6. Hori.
7. Black Hand.
8. Nameless Dead.
9. Scribes Without Mouths.
10. Cemetery Jackals.
11. Face Leeches.
12. Shadowless.
13. Wall Crawlers.
14. Lamp Guards.
15. False Shadows.
16. Ink Ghosts.
17. Erased Scribes.
18. Papyrus Serpents.
19. Archive Guards.
20. required P0 Shadow City references.
21. required P0 House of Life references.

## Realism

Use the supplied Nefer master as the minimum realism benchmark.

References must look like believable high-end AAA 3D production assets:
- real anatomy,
- real material response,
- real linen/fiber/stone/bronze/fur/skin,
- neutral production lighting,
- no stylized fantasy illustration,
- no plastic skin,
- no generic Egyptian cosplay.

## Anubis correction

The rejected direction is:
`normal human body + jackal head`.

Anubis should be a complete funerary divine organism:
- very tall,
- narrow,
- vertical,
- long controlled limbs,
- precise grasping hands,
- black funerary surface transitioning through short fur / organic dark skin / resin / basalt-like material,
- integrated off-white funerary linen,
- restrained staff,
- stillness as power.

Anubis must not resemble Seth.

Seth = dry, asymmetric, desert, spear, motion.
Anubis = black, controlled, vertical, staff, stillness.

Existing Anubis v02 is only a candidate. Review it critically.

## Generation/QA loop

For each asset:

GENERATE
→ inspect
→ compare with canon
→ compare with realism benchmark
→ silhouette check
→ anatomy check
→ gameplay readability check
→ ACCEPT CANDIDATE or REJECT
→ version non-destructively
→ update manifest/QA

Do not automatically mark generated work `LOCKED`.

## Resolution handling

Do not fake native resolution through upscaling.

If built-in generation cannot meet >=2048 native long edge:
- keep producing strong design candidates,
- record actual dimensions,
- keep status below production-final,
- preserve prompt and candidate for later high-resolution regeneration,
- do not stop the whole art queue merely because native resolution is unavailable.

## Output

At session end:
- update manifest,
- update QA report,
- update completion report,
- update blockers,
- create the next progress ZIP with root beginning at `ProjectDocs/References/`.
