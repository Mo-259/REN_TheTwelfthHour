import unreal
from pathlib import Path
import json
import os
import sys

"""
REN — Validate World Lock
Run inside Unreal Editor (Tools > Execute Python Script, or `py "<path>"`).

Compares current REN_ Actor transforms against the exported baseline for the
current world. Does not modify the level.

Detects: missing / added / moved / rotated / rescaled Actors, class changes,
static-mesh swaps (schema 2 baselines), duplicate labels, and map mismatch.
Rotation compare is wrap-aware (179.95 vs -179.95 = 0.1 deg).

Writes a machine-readable report to:
    ProjectDocs/WorldLocks/Reports/<World>.validation.json
Commit that report when handing results back to a cloud session.
"""

PREFIX = "REN_"


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
map_path = world.get_path_name().split(".")[0]
project_dir = Path(unreal.Paths.project_dir())
lock_dir = project_dir / "ProjectDocs" / "WorldLocks"
baseline_path = lock_dir / f"{world_name}.worldlock.json"

if not baseline_path.exists():
    raise RuntimeError(
        f"No baseline found at {baseline_path}. Run REN_Export_WorldLock.py first."
    )

baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

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
        "location_cm": [loc.x, loc.y, loc.z],
        "rotation_deg": [rot.roll, rot.pitch, rot.yaw],
        "scale": [scale.x, scale.y, scale.z],
    }

    mesh_comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    if mesh_comp:
        mesh = mesh_comp.get_editor_property("static_mesh")
        record["static_mesh"] = mesh.get_path_name() if mesh else None

    records.append(record)

current = core.build_manifest(records, world=world_name, map_path=map_path, prefix=PREFIX)
report = core.compare_manifests(baseline, current)
report["baseline_file"] = baseline_path.name

report_dir = lock_dir / "Reports"
report_dir.mkdir(parents=True, exist_ok=True)
report_path = report_dir / f"{world_name}.validation.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

info, warn, result = core.format_report(report)
for line in info:
    unreal.log(line)
for line in warn:
    unreal.log_warning(line)
if report["passed"]:
    unreal.log(result)
else:
    unreal.log_warning(result)
unreal.log(f"Report: {report_path}")
unreal.log("===========================================================")
