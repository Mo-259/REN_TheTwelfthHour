---
paths:
  - "Scripts/Editor/**/*.py"
---

# Unreal Editor Python Rules

- These scripts run inside Unreal Editor, not as standalone runtime game code.
- Use the current UE 5.8 Python API where possible.
- Prefer `unreal.get_editor_subsystem(...)` APIs over deprecated editor libraries.
- Scope cleanup operations using `REN_` Actor labels; never delete unrelated Actors.
- Re-running a builder should be safe when practical.
- Never create/switch levels mid-script and then continue mutating stale world references.
- Log a clear completion marker and generated-actor count.
- Save the current level only after successful construction.
- Any destructive rebuild must be obvious in comments and limited to REN-generated Actors.
- Run normal Python syntax checks in cloud, but label Unreal API execution `LOCAL_VALIDATION_REQUIRED`.
