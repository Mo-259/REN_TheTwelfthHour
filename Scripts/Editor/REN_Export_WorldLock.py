import unreal
from pathlib import Path
import json
import os
import sys

"""
REN — Export World Lock
Run inside Unreal Editor (Tools > Execute Python Script, or `py "<path>"`).

Exports transforms for all Actors whose labels start with REN_ in the current
open level. The resulting JSON is a reviewable baseline for spatial continuity.

Read-only with respect to the level: this script never modifies or saves Actors.

Baseline safety:
- If no baseline exists, writes  ProjectDocs/WorldLocks/<World>.worldlock.json
- If a baseline already exists, writes
      ProjectDocs/WorldLocks/<World>.worldlock.candidate.json
  and leaves the baseline untouched. Review the candidate with
  REN_Validate_WorldLock.py (or the offline CLI in REN_WorldLock_Core.py),
  then promote it deliberately (rename over the baseline, or set
  ALLOW_BASELINE_OVERWRITE = True for one run) and log it in docs/DEVLOG.md.
"""

PREFIX = "REN_"

# Set True only for an approved, intentional baseline refresh. Reset afterwards.
ALLOW_BASELINE_OVERWRITE = False


def _import_core():
    candidates = []
    try:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    candidates.append(os.path.join(unreal.Paths.project_dir(), "Scripts", "Editor"))
    for path in candidates:
        path = os.path.normpath(path)
        if os.path.isfile(os.path.join(path, "REN_WorldLock_Core.py")) and path not in sys.path:
            sys.path.insert(0, path)
    import importlib
    import REN_WorldLock_Core
    # Unreal keeps modules loaded between script runs; reload to pick up edits.
    return importlib.reload(REN_WorldLock_Core)


core = _import_core()

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

world = unreal_editor.get_editor_world()
if not world:
    raise RuntimeError("No editor world is open.")

world_name = world.get_name()
# "/Game/REN/Worlds/Tomb/L_Tomb_Blockout.L_Tomb_Blockout" -> package path
map_path = world.get_path_name().split(".")[0]

records = []
for actor in actor_subsystem.get_all_level_actors():
    try:
        label = actor.get_actor_label()
    except Exception:
        continue

    if not label.startswith(PREFIX):
        continue

    loc = actor.get_actor_location()
    rot = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()

    record = {
        "label": label,
        "class": actor.get_class().get_name(),
        "location_cm": [round(loc.x, 4), round(loc.y, 4), round(loc.z, 4)],
        "rotation_deg": [round(rot.roll, 4), round(rot.pitch, 4), round(rot.yaw, 4)],
        "scale": [round(scale.x, 6), round(scale.y, 6), round(scale.z, 6)],
    }

    mesh_comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    if mesh_comp:
        mesh = mesh_comp.get_editor_property("static_mesh")
        record["static_mesh"] = mesh.get_path_name() if mesh else None

    records.append(record)

payload = core.build_manifest(records, world=world_name, map_path=map_path, prefix=PREFIX)

project_dir = Path(unreal.Paths.project_dir())
out_dir = project_dir / "ProjectDocs" / "WorldLocks"
out_dir.mkdir(parents=True, exist_ok=True)
baseline_path = out_dir / f"{world_name}.worldlock.json"
candidate_path = out_dir / f"{world_name}.worldlock.candidate.json"

if baseline_path.exists() and not ALLOW_BASELINE_OVERWRITE:
    out_path = candidate_path
    wrote_baseline = False
else:
    out_path = baseline_path
    wrote_baseline = True

out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

unreal.log("===========================================================")
unreal.log("REN WORLD LOCK EXPORT COMPLETE")
unreal.log(f"World: {world_name}")
unreal.log(f"Map: {map_path}")
unreal.log(f"Actors: {len(records)}")
unreal.log(f"Output: {out_path}")
if wrote_baseline:
    unreal.log("Wrote BASELINE.")
else:
    unreal.log_warning(
        "Baseline already exists; wrote CANDIDATE instead. "
        "Review differences before promoting it to baseline."
    )
for label in payload["duplicate_labels"]:
    unreal.log_warning(f"DUPLICATE LABEL: {label}")
unreal.log("===========================================================")
