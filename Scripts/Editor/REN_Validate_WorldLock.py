import unreal
from pathlib import Path
import json
import math

"""
REN — Validate World Lock
Run inside Unreal Editor.

Compares current REN_ Actor transforms against the exported baseline for the
current world. Does not modify the level.
"""

PREFIX = "REN_"
LOCATION_TOLERANCE_CM = 0.1
ROTATION_TOLERANCE_DEG = 0.1
SCALE_TOLERANCE = 0.0001

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

world = unreal_editor.get_editor_world()
if not world:
    raise RuntimeError("No editor world is open.")

world_name = world.get_name()
project_dir = Path(unreal.Paths.project_dir())
baseline_path = project_dir / "ProjectDocs" / "WorldLocks" / f"{world_name}.worldlock.json"

if not baseline_path.exists():
    raise RuntimeError(
        f"No baseline found at {baseline_path}. Run REN_Export_WorldLock.py first."
    )

baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
expected = {item["label"]: item for item in baseline.get("actors", [])}

current = {}
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

    current[label] = {
        "class": actor.get_class().get_name(),
        "location_cm": [loc.x, loc.y, loc.z],
        "rotation_deg": [rot.roll, rot.pitch, rot.yaw],
        "scale": [scale.x, scale.y, scale.z],
    }

def max_abs_diff(a, b):
    return max(abs(float(x) - float(y)) for x, y in zip(a, b))

missing = sorted(set(expected) - set(current))
added = sorted(set(current) - set(expected))
changed = []

for label in sorted(set(expected) & set(current)):
    e = expected[label]
    c = current[label]

    loc_diff = max_abs_diff(e["location_cm"], c["location_cm"])
    rot_diff = max_abs_diff(e["rotation_deg"], c["rotation_deg"])
    scale_diff = max_abs_diff(e["scale"], c["scale"])

    class_changed = e.get("class") != c.get("class")

    if (
        class_changed
        or loc_diff > LOCATION_TOLERANCE_CM
        or rot_diff > ROTATION_TOLERANCE_DEG
        or scale_diff > SCALE_TOLERANCE
    ):
        changed.append({
            "label": label,
            "class_changed": class_changed,
            "location_max_diff_cm": round(loc_diff, 4),
            "rotation_max_diff_deg": round(rot_diff, 4),
            "scale_max_diff": round(scale_diff, 6),
        })

unreal.log("===========================================================")
unreal.log("REN WORLD LOCK VALIDATION")
unreal.log(f"World: {world_name}")
unreal.log(f"Expected actors: {len(expected)}")
unreal.log(f"Current actors: {len(current)}")
unreal.log(f"Missing: {len(missing)}")
unreal.log(f"Added: {len(added)}")
unreal.log(f"Changed: {len(changed)}")

for label in missing:
    unreal.log_warning(f"MISSING: {label}")
for label in added:
    unreal.log_warning(f"ADDED: {label}")
for item in changed:
    unreal.log_warning(
        "CHANGED: "
        + item["label"]
        + f" | loc={item['location_max_diff_cm']}cm"
        + f" rot={item['rotation_max_diff_deg']}deg"
        + f" scale={item['scale_max_diff']}"
        + (" class_changed=True" if item["class_changed"] else "")
    )

if not missing and not added and not changed:
    unreal.log("RESULT: PASS — no unexplained REN spatial drift detected.")
else:
    unreal.log_warning("RESULT: REVIEW REQUIRED — world-lock differences detected.")

unreal.log("===========================================================")
