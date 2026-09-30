# REN — Claude Code Development Kit

This kit is designed to be copied into the **root of the Unreal project**, next to the `.uproject` file.

Project target:
- Unreal Engine 5.8
- Third Person template
- Blueprint-first vertical-slice development
- Python for editor automation
- Unreal MCP for local agentic editor work when available
- Claude Code Cloud for repository work, planning, scripts, documentation, code review, and preparation

## Copy this structure into the project root

```text
REN_TheTwelfthHour/
├── REN_TheTwelfthHour.uproject
├── CLAUDE.md
├── MASTER_PROMPT_CLAUDE_CLOUD.md
├── .claude/
│   └── rules/
├── docs/
├── Scripts/
│   └── Editor/
└── ProjectDocs/
    └── WorldLocks/
```

## Important: Cloud vs Local

Claude Code Cloud runs on a remote machine. It cannot directly control the Unreal Editor running on your Windows PC through the local Unreal MCP server.

Therefore:

### While using Claude Code Cloud
Claude should:
- inspect and organize the repository
- create and edit text files
- create Unreal Python editor scripts
- prepare C++ only when explicitly approved
- write detailed Blueprint/MCP implementation plans
- create validation scripts
- maintain project state and task logs
- prepare commits / PRs
- never claim that an Unreal Editor action was executed unless it actually had editor access

### When Claude Code is local again
Use Unreal MCP to:
- inspect actors/assets/Blueprints
- create or edit Blueprint graphs
- run editor-side tools
- manipulate levels, materials, Sequencer, Niagara, Control Rig
- run automation tests

## First Cloud Session

Paste the entire contents of `MASTER_PROMPT_CLAUDE_CLOUD.md` as the first task.

## First Local MCP Session Later

Read `docs/LOCAL_MCP_HANDOFF.md`, start Unreal MCP, then tell Claude:

> Read CLAUDE.md, docs/CURRENT_PROJECT_STATE.md, docs/TECHNICAL_ARCHITECTURE.md, docs/VERTICAL_SLICE_SPEC.md, and docs/LOCAL_MCP_HANDOFF.md. Audit the live Unreal project through Unreal MCP before changing anything. Reconcile the documentation with the actual editor state, then continue from the first unfinished P0/P1 task.

## Source of Truth Priority

When documents disagree, use this order:

1. Explicit latest user decision
2. Actual live Unreal project state
3. `docs/CURRENT_PROJECT_STATE.md`
4. `docs/GAME_CANON.md`
5. Other design documents
6. Old prompts, screenshots, or exploratory assets

Never silently invent a missing decision.
