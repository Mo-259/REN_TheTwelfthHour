# Handoff to Claude Code

## Purpose

This folder is now the repository-facing visual reference system for REN.

Claude Code must use it as **reference authority metadata**, not assume that all planned visual assets already exist.

## Read order

Before any task that touches art, visual identity, character proportions, boss appearance, environment design, materials, VFX, or cinematic composition:

1. `ProjectDocs/References/DESIGN_AUTHORITY.md`
2. `ProjectDocs/References/REFERENCE_MANIFEST.json`
3. `ProjectDocs/References/CHANGE_CONFLICTS.md`
4. the relevant `ASSET_BRIEF.md`
5. only then inspect any image candidate for that asset.

## Status handling

- `LOCKED` — may be used as authority unless the latest game bible explicitly supersedes it.
- `APPROVED_BASE` — safe foundation, but technical/gameplay sheets may still be missing.
- `NEEDS_REVIEW` — do not build final art from it.
- `PROVISIONAL` — specification exists, visual authority does not.
- `ARCHIVED` — never use as current authority.

## Important current facts

- Nefer supplied master remains the only locked identity source.
- Existing Anubis v02 is not locked.
- Face-Eater must follow current v3 combat mechanics, not the obsolete chest-seal-only concept.
- Current Nameless Dead authority is v3, not the earlier subtle-human-erasure direction.
- Seth must remain non-canine.
- Gods are not forced into a `human body + animal head` template.
- World continuity remains absolute: CAMERA MOVES; WORLD DOES NOT.

## What Claude Code may do now

Claude Code may:
- consume approved references,
- verify naming/manifest integrity,
- build greybox gameplay,
- implement Blueprint/C++ systems according to the active technical plan,
- create placeholder Unreal assets clearly marked temporary,
- update docs/manifest references when a visual is approved.

Claude Code must not:
- silently promote `PROVISIONAL` art to `LOCKED`,
- redesign a locked identity without explicit approval,
- claim final visual art exists when only an asset brief exists,
- infer exact model dimensions from AI images unless marked as provisional.

## P0 art dependency

For final character/boss art implementation, wait for approved P0 references.

For gameplay greybox, continue using placeholders and explicit labels:
`TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.
