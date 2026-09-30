import unreal
from pathlib import Path
import json
from datetime import datetime

"""
REN — Export World Lock
Run inside Unreal Editor.

Exports transforms for all Actors whose labels start with REN_ in the current
open level. The resulting JSON is a reviewable baseline for spatial continuity.
"""

PREFIX = "REN_"

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

world = unreal_editor.get_editor_world()
if not world:
    raise RuntimeError("No editor world is open.")

world_name = world.get_name()

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

    records.append({
        "label": label,
        "class": actor.get_class().get_name(),
        "location_cm": [round(loc.x, 4), round(loc.y, 4), round(loc.z, 4)],
        "rotation_deg": [round(rot.roll, 4), round(rot.pitch, 4), round(rot.yaw, 4)],
        "scale": [round(scale.x, 6), round(scale.y, 6), round(scale.z, 6)],
    })

records.sort(key=lambda x: x["label"])

payload = {
    "schema": 1,
    "project": "REN_TheTwelfthHour",
    "world": world_name,
    "actor_prefix": PREFIX,
    "exported_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "actor_count": len(records),
    "actors": records,
}

project_dir = Path(unreal.Paths.project_dir())
out_dir = project_dir / "ProjectDocs" / "WorldLocks"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / f"{world_name}.worldlock.json"
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

unreal.log("===========================================================")
unreal.log("REN WORLD LOCK EXPORT COMPLETE")
unreal.log(f"World: {world_name}")
unreal.log(f"Actors: {len(records)}")
unreal.log(f"Output: {out_path}")
unreal.log("===========================================================")
