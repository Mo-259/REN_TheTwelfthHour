# REN — Claude Code Cloud Workflow

## What Cloud Claude can do well

- read repository files
- plan implementation
- write/edit Markdown
- create Unreal Python editor scripts
- create validation/reporting tools
- inspect text-based Config
- prepare code changes
- create task-scoped Git commits/PRs
- review architecture
- write local-MCP execution plans

## What it cannot directly do to the user's local Unreal Editor

A cloud environment is remote.

It cannot directly access the Unreal MCP server that runs inside the user's local Unreal Editor on `127.0.0.1`.

Therefore cloud Claude cannot truthfully:
- inspect live selected Actors
- inspect live Blueprint graphs
- move local level Actors through MCP
- compile Blueprints in the local Editor
- run local PIE
- render local Sequencer shots
- inspect local Output Log unless exported into repo/input

## Cloud-first task format

Every cloud task should end with:

### Cloud work completed
List actual repository changes.

### Static validation
List syntax/static checks actually run.

### LOCAL_VALIDATION_REQUIRED
Exact local Unreal checks still needed.

### Local execution prompt
A copy/paste prompt for local Claude + Unreal MCP.

## Repository handoff

Cloud work should be committed on a clear task branch or checkpoint.

When returning local:
1. pull/checkout cloud changes
2. start Unreal
3. start Unreal MCP
4. ask local Claude to audit first
5. perform local-only steps
6. update current state
7. commit validated result

## Binary Unreal assets

`.uasset` and `.umap` are binary.

Cloud Claude should not pretend to understand their internal graph/state from raw binary contents.

Use:
- documentation
- exported reports
- Unreal Python reports
- local MCP

to inspect them meaningfully.

## Parallel cloud sessions

Do not run multiple sessions that edit the same architectural files or same system at once.

Safe parallel examples:
- one session researches/updates art documentation
- one session writes a validation script
- one session audits naming

Unsafe:
- two sessions both redesign interaction architecture
- two sessions both edit the same builder script
