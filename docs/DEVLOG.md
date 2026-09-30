# REN — Development Log

## 2026-09-30 — Unreal project bootstrap

- Unreal Engine 5.8 project created from Third Person template.
- Third-person movement/camera verified by user.
- Python Editor Script Plugin enabled.
- Python automation chosen for repetitive editor blockout work.
- `L_Tomb_Blockout` created under `/Game/REN/Worlds/Tomb/`.
- Early builder version exposed execution/world-switch issues.
- Builder workflow changed to operate inside the currently open level.
- Tomb Opening Greybox Builder v3 executed successfully.
- v3 includes burial chamber, sarcophagus, Blank Cartouche clue, corridor, no-shadow clue zone, side room, exit, transition tunnel, reveal ledge, triggers, and temporary lights.
- Decision: use Claude Code Cloud temporarily for repository preparation; use local Unreal MCP when local Claude access is available.
- Decision: Blueprint-first vertical slice; Python for editor automation; no premature C++ migration.

## Next

- Install Claude development kit in project root.
- Audit repo from cloud.
- Preserve v3 script in source control.
- Prepare interaction foundation package.
- Configure local Unreal MCP later.
