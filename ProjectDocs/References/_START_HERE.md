# REN Visual Production Pack v3 — START HERE

This package is intentionally structured so it can be extracted **directly into the REN project root**.

Expected destination after extraction:

```text
<ProjectRoot>/
└── ProjectDocs/
    └── References/
```

Do **not** extract it inside `ProjectDocs/` itself, otherwise you will create:

```text
ProjectDocs/ProjectDocs/References/
```

## Current truth

This is a **design-progress / production-scaffold pack**, not a finished visual-art pack.

Current factual state:

- 45 canonical character entries.
- 18 main bosses.
- 2 additional non-boss major encounters.
- 12 optional bosses.
- 43 enemy labels.
- 6 canonical elites.
- 3 player weapons.
- 1 player utility.
- 4 transformations.
- 6 macroregions.
- 794 required visual-reference slots.
- 3 actual images currently present.
- 1 supplied Nefer identity source is `LOCKED`.
- Anubis v02 is `NEEDS_REVIEW`.
- 792 visual slots remain missing.
- No newly generated image currently meets the native >=2048 long-edge production requirement.

## Authority rule

Before any visual or Unreal implementation task, read:

1. `DESIGN_AUTHORITY.md`
2. `REFERENCE_MANIFEST.md`
3. `CHANGE_CONFLICTS.md`
4. the asset's own `ASSET_BRIEF.md`

Never treat a `PROVISIONAL` or `NEEDS_REVIEW` image as final visual authority.

## Immediate production priority

Do not expand late-game art yet.

Priority is the P0 visual queue:

1. Nefer missing production references.
2. Anubis redesign / review.
3. Face-Eater Combat v2.
4. Kheft.
5. Sheut.
6. Thoth.
7. Hori.
8. Black Hand.
9. Enemy set 01E–12E.
10. Required Shadow City references.
11. Required House of Life references.

## For Claude Code

Read `HANDOFF_TO_CLAUDE_CODE.md`.

## For ChatGPT Work

Read `WORK_CONTINUATION_PROMPT.md`.
