import unreal
from pathlib import Path
import json

"""
REN — Inspect Tomb Orientation (READ-ONLY)
Run inside Unreal Editor with /Game/REN/Worlds/Tomb/L_Tomb_Blockout open standalone.

Purpose: confirm or reject the suspected builder-v3 Rotator-ordering errors
BEFORE the first official Tomb world-lock baseline is exported, so a known-bad
transform is never locked.

Background: UE Python's constructor is unreal.Rotator(roll, pitch, yaw).
Builder v3 called Rotator(0.0, 90.0, 0.0) for REN_PlayerStart (-> pitch 90?)
and passed (0, 90, 0) through its helper for REN_BlankCartouche_Relief
(-> roll 90?). These are HYPOTHESES from reading code. This script measures
the live actors and reports:

  REN_PlayerStart            expected yaw 90 (faces +Y, toward the corridor), pitch 0, roll 0
  REN_BlankCartouche_Relief  expected a VERTICAL wall relief: world bounds thin on X,
                             taller (Z) than wide (Y)

It never modifies, moves, or saves anything. It writes:
  ProjectDocs/WorldLocks/Reports/<World>.orientation_check.json
"""

EXPECTED_WORLD = "L_Tomb_Blockout"
ANGLE_TOL_DEG = 1.0


def _angle_delta(a, b):
    d = (float(a) - float(b)) % 360.0
    return min(d, 360.0 - d)


actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world or world.get_name() != EXPECTED_WORLD:
    raise RuntimeError(
        f"Open {EXPECTED_WORLD} standalone first (current: {world.get_name() if world else None})."
    )

by_label = {}
for actor in actor_subsystem.get_all_level_actors():
    try:
        by_label.setdefault(actor.get_actor_label(), []).append(actor)
    except Exception:
        continue

results = {}


def _single(label):
    found = by_label.get(label, [])
    if len(found) != 1:
        results[label] = {"verdict": "NOT_FOUND" if not found else "DUPLICATE", "count": len(found)}
        return None
    return found[0]


# --- PlayerStart ------------------------------------------------------------
ps = _single("REN_PlayerStart")
if ps:
    r = ps.get_actor_rotation()
    rot = {"roll": round(r.roll, 4), "pitch": round(r.pitch, 4), "yaw": round(r.yaw, 4)}
    ok = (
        _angle_delta(r.yaw, 90.0) <= ANGLE_TOL_DEG
        and _angle_delta(r.pitch, 0.0) <= ANGLE_TOL_DEG
        and _angle_delta(r.roll, 0.0) <= ANGLE_TOL_DEG
    )
    results["REN_PlayerStart"] = {
        "rotation_deg": rot,
        "expected": {"roll": 0.0, "pitch": 0.0, "yaw": 90.0},
        "verdict": "OK" if ok else "WRONG",
        "fix_if_wrong": "Details > Transform > Rotation: X(roll)=0, Y(pitch)=0, Z(yaw)=90. Location unchanged.",
    }

# --- Blank Cartouche relief -------------------------------------------------
rel = _single("REN_BlankCartouche_Relief")
if rel:
    r = rel.get_actor_rotation()
    s = rel.get_actor_scale3d()
    _origin, ext = rel.get_actor_bounds(False)
    extent = {"x": round(ext.x, 2), "y": round(ext.y, 2), "z": round(ext.z, 2)}
    thin_on_x = ext.x < ext.y and ext.x < ext.z
    vertical = ext.z > ext.y
    if thin_on_x and vertical:
        verdict = "OK"
    elif thin_on_x and not vertical:
        verdict = "WRONG_HORIZONTAL"
    else:
        verdict = "UNEXPECTED"
    results["REN_BlankCartouche_Relief"] = {
        "rotation_deg": {"roll": round(r.roll, 4), "pitch": round(r.pitch, 4), "yaw": round(r.yaw, 4)},
        "scale": [round(s.x, 6), round(s.y, 6), round(s.z, 6)],
        "world_bounds_half_extent_cm": extent,
        "expected": "thin on X (wall normal), Z half-extent > Y half-extent (vertical cartouche)",
        "verdict": verdict,
        "fix_if_wrong": (
            "If WRONG_HORIZONTAL: set Rotation to X=0, Y=0, Z=0 (keep location and scale), "
            "re-run this script, expect OK. If UNEXPECTED: stop and report; do not improvise."
        ),
    }

all_ok = all(v.get("verdict") == "OK" for v in results.values()) and len(results) == 2
payload = {
    "world": world.get_name(),
    "results": results,
    "all_ok": all_ok,
    "note": "Read-only inspection. Export the official baseline only when all_ok is true.",
}

out_dir = Path(unreal.Paths.project_dir()) / "ProjectDocs" / "WorldLocks" / "Reports"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / f"{world.get_name()}.orientation_check.json"
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

unreal.log("===========================================================")
unreal.log("REN TOMB ORIENTATION CHECK (read-only)")
for label, res in results.items():
    line = f"{label}: {res['verdict']} | " + json.dumps({k: v for k, v in res.items() if k not in ('fix_if_wrong', 'expected')})
    if res["verdict"] == "OK":
        unreal.log(line)
    else:
        unreal.log_warning(line)
        if "fix_if_wrong" in res:
            unreal.log_warning(f"  FIX: {res['fix_if_wrong']}")
if all_ok:
    unreal.log("RESULT: ALL OK — safe to export the official Tomb baseline after traversal check.")
else:
    unreal.log_warning("RESULT: FIX REQUIRED — do NOT export the official baseline yet.")
unreal.log(f"Report: {out_path}")
unreal.log("===========================================================")
