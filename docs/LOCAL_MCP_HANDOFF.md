# REN — Local Unreal MCP Handoff

Use this when Claude Code is running on the same machine as Unreal.

## Unreal setup

Required Unreal plugins:
- Unreal MCP / ModelContextProtocol
- All Toolsets
- Toolset Registry (dependency)
- Python Editor Script Plugin

Restart Unreal after enabling plugins.

## Start MCP

Recommended:
Enable Auto Start Server in:
Editor Preferences → Model Context Protocol.

Default endpoint:
`http://127.0.0.1:8000/mcp`

Or start manually in Unreal console:

```text
ModelContextProtocol.StartServer
```

Generate Claude Code config:

```text
ModelContextProtocol.GenerateClientConfig ClaudeCode
```

This should write `.mcp.json` at the project root.

## Local Claude startup

Start Claude Code from the Unreal project root so it reads:
- `CLAUDE.md`
- project `.claude/rules/`
- `.mcp.json`

## Mandatory first local task

Before editing Unreal:

1. verify MCP connection
2. inspect current map
3. list REN actors
4. locate known triggers
5. inspect current player Blueprint / GameMode
6. inspect input assets
7. reconcile live state with `docs/CURRENT_PROJECT_STATE.md`
8. export world-lock baseline if one does not exist

Do not make edits before this audit.

## MCP discipline

Unreal executes MCP tool calls on the game thread.

Do not issue overlapping editor mutation calls.

Perform changes serially:
inspect → mutate → compile/save → inspect result.

## Recommended first local implementation

P1 Interaction foundation:
- create `IA_Interact`
- map to E
- create `BPI_Interactable`
- add 350cm camera-forward interaction logic
- create/test Blank Cartouche interaction
- create/test Exit Door interaction
- compile/save
- PIE test
- update docs

## Handoff back to cloud

After local implementation:
- update `CURRENT_PROJECT_STATE.md`
- export relevant reports/manifests
- commit
- push
- cloud sessions may then continue planning/scripts based on verified state
