# REN — Git Workflow

## Track

Normally track:
- `.uproject`
- `Config/`
- `Content/` including `.uasset` / `.umap`
- `Scripts/`
- `Source/` if C++ is added
- `.claude/`
- `CLAUDE.md`
- project docs

## Ignore

Ignore generated/local folders:
- `.vs/`
- `Binaries/`
- `DerivedDataCache/`
- `Intermediate/`
- `Saved/`
- IDE/user files

## Commit policy

One coherent task per commit when practical.

Examples:
- `chore: add REN Claude project instructions`
- `tools: add tomb world-lock export`
- `feat: add interact input and base interface`
- `level: lock tomb opening layout`
- `boss: prototype Face-Eater exposed state`

## Before risky edits

1. `git status`
2. ensure unrelated work is not being overwritten
3. checkpoint current good state
4. make scoped change
5. validate
6. commit

## Prohibited without explicit approval

- force push
- history rewrite
- hard reset
- cleaning untracked project content
- mass binary asset deletion
