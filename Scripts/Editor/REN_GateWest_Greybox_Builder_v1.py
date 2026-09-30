import unreal
import os
import sys

# ============================================================
# REN — THE TWELFTH HOUR
# Gate of the West (threshold + first combat court + arena SHELL)
# Greybox Builder v1
#
# Run inside Unreal Editor with /Game/REN/Worlds/GateWest/L_GateWest_Blockout
# opened STANDALONE (not inside L_REN_Slice).
#
# Layout data: Scripts/Editor/REN_GateWest_Layout.py (pure Python, unit-tested)
# Design doc:  docs/GATE_WEST_GREYBOX_SPEC.md
#
# Safety:
# - Refuses to run unless the open world is L_GateWest_Blockout.
# - Refuses if any other REN_ actor is loaded (Tomb / Necropolis sublevels),
#   except hand-placed REN_INT_* interactables and REN_CAM_* cameras, which are
#   allowed and NEVER deleted. Nothing is ever deleted outside the REN_GW_ prefix.
# - Refuses once a GateWest world-lock baseline exists (layout locked), unless
#   FORCE_REBUILD_AFTER_LOCK = True is set for one approved run.
# - Validates the whole layout (incl. no overlap with Tomb/Necropolis) BEFORE
#   deleting anything.
# - Re-run safe: deletes only REN_GW_ actors, then rebuilds deterministically.
# - Uses the single world reference captured at start; never switches levels.
# - Does NOT spawn or move REN_DistantGate (Tomb skyline proxy). It is opened
#   at runtime by a Blueprint (spec §4). No Face-Eater logic: markers only.
# ============================================================

FORCE_REBUILD_AFTER_LOCK = False

# Hand-placed actors that may live in this level; tolerated by the guard, never deleted.
ALLOWED_FOREIGN_PREFIXES = ("REN_INT_", "REN_CAM_")


def _import_layout():
    candidates = []
    try:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    candidates.append(os.path.join(unreal.Paths.project_dir(), "Scripts", "Editor"))
    for path in candidates:
        path = os.path.normpath(path)
        if os.path.isfile(os.path.join(path, "REN_GateWest_Layout.py")) and path not in sys.path:
            sys.path.insert(0, path)
    import importlib
    import REN_Necropolis_Layout
    import REN_GateWest_Layout
    # Unreal keeps modules loaded between script runs; reload to pick up edits
    # (Necropolis first: the GateWest layout validates against it).
    importlib.reload(REN_Necropolis_Layout)
    return importlib.reload(REN_GateWest_Layout)


layout_mod = _import_layout()
PREFIX = layout_mod.PREFIX
EXPECTED_WORLD = layout_mod.EXPECTED_WORLD

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

# ------------------------------------------------------------
# Guards (nothing is modified before all of these pass)
# ------------------------------------------------------------
if not editor_world or editor_world.get_name() != EXPECTED_WORLD:
    raise RuntimeError(
        f"GateWest builder must run with {EXPECTED_WORLD} opened standalone "
        f"(current: {editor_world.get_name() if editor_world else None}). Nothing was changed."
    )

foreign = []
for actor in actor_subsystem.get_all_level_actors():
    try:
        label = actor.get_actor_label()
    except Exception:
        continue
    if (label.startswith("REN_") and not label.startswith(PREFIX)
            and not label.startswith(ALLOWED_FOREIGN_PREFIXES)):
        foreign.append(label)
if foreign:
    raise RuntimeError(
        f"Found {len(foreign)} non-{PREFIX} REN actors (e.g. {foreign[:3]}). The Tomb or another "
        "sublevel is loaded. Open L_GateWest_Blockout standalone. Nothing was changed."
    )

baseline = os.path.join(
    unreal.Paths.project_dir(), "ProjectDocs", "WorldLocks", f"{EXPECTED_WORLD}.worldlock.json"
)
if os.path.exists(baseline) and not FORCE_REBUILD_AFTER_LOCK:
    raise RuntimeError(
        "GateWest world-lock baseline exists: layout is locked. Nothing was changed. "
        "Set FORCE_REBUILD_AFTER_LOCK = True only with explicit approval."
    )

items = layout_mod.build_layout()
errors = layout_mod.validate_layout(items)
if errors:
    raise RuntimeError("Layout validation failed; nothing was changed:\n  " + "\n  ".join(errors))

cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
if not cube_mesh:
    raise RuntimeError("Could not load /Engine/BasicShapes/Cube. Nothing was changed.")

# ------------------------------------------------------------
# Cleanup: ONLY REN_GW_ actors (PREFIX)
# ------------------------------------------------------------
removed = 0
for actor in actor_subsystem.get_all_level_actors():
    try:
        if actor.get_actor_label().startswith(PREFIX):
            actor_subsystem.destroy_actor(actor)
            removed += 1
    except Exception:
        pass

# ------------------------------------------------------------
# Spawn helpers (Rotators always built with keywords: roll/pitch/yaw)
# ------------------------------------------------------------
ZERO_ROT = unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0)


def _rot(d):
    return unreal.Rotator(roll=float(d["roll"]), pitch=float(d["pitch"]), yaw=float(d["yaw"]))


def _folder(actor, sub):
    try:
        actor.set_folder_path(f"REN_GW/{sub}")
    except Exception:
        pass


def spawn_box_mesh(it):
    center, scale = layout_mod.center_and_scale(it["min"], it["max"])
    actor = actor_subsystem.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*center), ZERO_ROT)
    if not actor:
        raise RuntimeError(f"Failed to spawn {it['label']}")
    actor.set_actor_label(it["label"])
    actor.set_actor_scale3d(unreal.Vector(*scale))
    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    comp.set_static_mesh(cube_mesh)
    kind = it["kind"]
    if kind == "movable":
        comp.set_mobility(unreal.ComponentMobility.MOVABLE)
        _folder(actor, "Mechanisms")
    elif kind == "invis":
        actor.set_actor_hidden_in_game(True)
        _folder(actor, "Blockers")
    elif kind == "dressing":
        comp.set_collision_profile_name("NoCollision")
        _folder(actor, "Dressing")
    else:
        _folder(actor, "Geometry")
    return actor


def spawn_trigger(it):
    center, _ = layout_mod.center_and_scale(it["min"], it["max"])
    half = [(b - a) / 2.0 for a, b in zip(it["min"], it["max"])]
    actor = actor_subsystem.spawn_actor_from_class(unreal.TriggerBox, unreal.Vector(*center), ZERO_ROT)
    actor.set_actor_label(it["label"])
    box = actor.get_component_by_class(unreal.BoxComponent)
    box.set_box_extent(unreal.Vector(*half))   # exact size; actor scale stays 1
    _folder(actor, "Triggers")
    return actor


def spawn_target(it):
    actor = actor_subsystem.spawn_actor_from_class(unreal.TargetPoint, unreal.Vector(*it["loc"]), _rot(it["rot"]))
    actor.set_actor_label(it["label"])
    _folder(actor, "Markers")
    return actor


def spawn_point_light(it):
    actor = actor_subsystem.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*it["loc"]), ZERO_ROT)
    actor.set_actor_label(it["label"])
    comp = actor.get_component_by_class(unreal.PointLightComponent)
    comp.set_editor_property("intensity", it["intensity"])
    comp.set_editor_property("attenuation_radius", it["radius"])
    _folder(actor, "Lights")
    return actor


def spawn_spot_light(it):
    actor = actor_subsystem.spawn_actor_from_class(unreal.SpotLight, unreal.Vector(*it["loc"]), _rot(it["rot"]))
    actor.set_actor_label(it["label"])
    comp = actor.get_component_by_class(unreal.SpotLightComponent)
    comp.set_editor_property("intensity", it["intensity"])
    comp.set_editor_property("attenuation_radius", it["radius"])
    comp.set_editor_property("inner_cone_angle", it["inner"])
    comp.set_editor_property("outer_cone_angle", it["outer"])
    _folder(actor, "Lights")
    return actor


SPAWNERS = {
    "mesh": spawn_box_mesh,
    "movable": spawn_box_mesh,
    "invis": spawn_box_mesh,
    "dressing": spawn_box_mesh,
    "trigger": spawn_trigger,
    "target": spawn_target,
    "point_light": spawn_point_light,
    "spot_light": spawn_spot_light,
}

spawned = 0
for it in items:
    SPAWNERS[it["kind"]](it)
    spawned += 1

# ------------------------------------------------------------
# Save + log
# ------------------------------------------------------------
level_subsystem.save_current_level()

count = 0
for actor in actor_subsystem.get_all_level_actors():
    try:
        if actor.get_actor_label().startswith(PREFIX):
            count += 1
    except Exception:
        pass

unreal.log("===========================================================")
unreal.log(f"REN Gate of the West Greybox Builder v{layout_mod.LAYOUT_VERSION} COMPLETE")
unreal.log(f"World: {editor_world.get_name()}")
unreal.log(f"Removed previous {PREFIX} actors: {removed}")
unreal.log(f"Spawned: {spawned} | {PREFIX} actors now in level: {count} (expected {len(items)})")
unreal.log("Route: Gate plaza -> Passage (checkpoint) -> Combat Court -> Combat Gate ->")
unreal.log("       Corridor (checkpoint) -> Arena SHELL (markers only, no boss logic).")
if count != len(items):
    unreal.log_warning("ACTOR COUNT MISMATCH — inspect Output Log before saving further work.")
unreal.log("===========================================================")
