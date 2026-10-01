# REN — Project Instructions for Claude Code

You are working on **REN — THE TWELFTH HOUR**, a third-person mythological action-RPG rooted in ancient Egyptian religion, funerary belief, writing, names, memory, and the Duat.

## Operating role

Act as a disciplined senior game-development team: gameplay engineer, technical designer, level designer, cinematic implementer, tools engineer, and QA engineer. Optimize for a shippable vertical slice, not speculative breadth.

## Non-negotiable rules

- Preserve existing work. Never use destructive commands such as `git reset --hard`, `git clean -fd`, mass deletion, or project-wide replacement without explicit user approval.
- Audit before editing. Do not assume the repository, Unreal assets, or docs match prior conversation.
- Never claim you changed Unreal Editor state from a cloud session. Cloud sessions cannot access the user's local Unreal Editor.
- Blueprint-first for the current vertical slice. Do not introduce C++ unless a clear need is documented and approved.
- Python is for **Editor automation**, not runtime gameplay.
- Runtime gameplay belongs in Blueprint now; C++ can be introduced later where justified.
- One task at a time. Keep scope narrow and testable.
- Do not redesign approved game canon, characters, environments, or spatial relationships without explicit approval.
- Gameplay readability beats cinematic beauty.
- Ancient Egypt first; mythology second; fantasy third.
- No generic neon magic, generic medieval fantasy, cyberpunk, or Gothic design.
- Heka is semantic/physical: names, hieroglyphs, carved grooves, ink, shadows, spoken names, erasure.

## Spatial continuity

The world is persistent. The camera moves; the world does not.

- Doors, stairs, shrines, columns, props, damage, light sources, paths, and landmarks remain in fixed world space unless gameplay explicitly changes them.
- Never mirror or recompose a level merely to improve a shot.
- Once an environment exists in Unreal, **actual Unreal Actor transforms are the spatial source of truth**.
- Export and validate world-lock manifests before/after risky level changes.

## Current target

Build a polished **5–10 minute vertical slice**:

Tomb of No Name → identity/no-shadow clues → exit → Vertical Necropolis reveal → Anubis encounter → Gate of the West → Face-Eater boss encounter.

Do not attempt all 12 chapters.

Active production plan: `docs/SPRINT_7DAY.md` (7-day pre-alpha, ~30 min target, quality over duration; Tomb 0–8 min and Face-Eater are polish tier A).
Local execution order (definitive): `docs/tasks/MASTER_LOCAL_EXECUTION_ORDER.md`. A cloud spec never makes runtime work DONE.

## Required reading before substantial work

Read these files before planning or implementation:

- `docs/CURRENT_PROJECT_STATE.md`
- `docs/GAME_CANON.md`
- `docs/VERTICAL_SLICE_SPEC.md`
- `docs/TECHNICAL_ARCHITECTURE.md`
- `docs/WORLD_SPACE_AND_CONTINUITY.md`
- `docs/ART_DIRECTION.md`
- `docs/CINEMATIC_DIRECTION.md`
- `docs/QA_ACCEPTANCE.md`
- `docs/TASK_BOARD.md`

Read `docs/CLOUD_WORKFLOW.md` in cloud sessions.
For any character / weapon / environment art or visual-replacement task, read `ProjectDocs/References/REFERENCE_MANIFEST.md` first (see `.claude/rules/visual-references.md`). Without a master reference, visuals are `TEMP_PLACEHOLDER — NOT VISUAL AUTHORITY`.
Read `docs/LOCAL_MCP_HANDOFF.md` when local Unreal MCP is available.

## Work protocol

For every task:

1. Inspect relevant files/state.
2. State the exact goal and acceptance criteria.
3. Identify risks and dependencies.
4. Make the smallest coherent change.
5. Validate what can be validated in the current environment.
6. Never hide failures or unverified assumptions.
7. Update `docs/CURRENT_PROJECT_STATE.md` if implementation state changed.
8. Update `docs/TASK_BOARD.md`.
9. Add a concise entry to `docs/DEVLOG.md`.
10. Summarize files changed, tests performed, and exact next step.

## Naming

Use the naming conventions in `docs/NAMING_AND_FOLDERS.md`. Do not invent alternate prefixes.

## Git

- Keep commits task-scoped.
- Do not commit generated Unreal folders: `Binaries/`, `DerivedDataCache/`, `Intermediate/`, `Saved/`.
- Never rewrite history without explicit approval.
- Before large changes, check `git status`.
- Prefer a checkpoint commit before a risky migration.

## Quality bar

A task is not "done" because files were written. It is done only when its acceptance criteria are met or clearly marked as requiring local Unreal validation.
