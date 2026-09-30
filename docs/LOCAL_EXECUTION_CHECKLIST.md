# REN — Local Execution Checklist

Use this when a cloud task produces scripts or a local-MCP plan.

## Before running editor automation

- Save current Unreal work.
- Confirm correct level is open.
- Check Git status / checkpoint important changes.
- Read the script header.
- Confirm cleanup is scoped to `REN_` labels or another explicit safe scope.
- Do not execute an unreviewed script against a production level.

## After running

- inspect Output Log for traceback/errors
- confirm completion marker
- inspect Actor count
- inspect Outliner
- press Play / PIE where relevant
- verify player spawn and collisions
- verify no duplicate Actors
- save only after result is acceptable
- update world-lock baseline if layout was intentionally changed

## For Blueprint/MCP changes

- compile affected Blueprints
- save
- PIE test
- test one success path
- test one failure/edge path
- update current state and task board
