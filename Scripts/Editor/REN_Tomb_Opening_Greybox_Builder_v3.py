import unreal

# ============================================================
# REN — THE TWELFTH HOUR
# Tomb of No Name — Opening Greybox Builder v3
#
# Builds the FIRST 45–60 seconds of the opening as a playable
# authored greybox inside the CURRENT OPEN LEVEL.
#
# Flow:
#   Wake/Sarcophagus -> Blank Cartouche clue -> Corridor ->
#   Shadow-test zone -> Side clue chamber -> Exit door ->
#   Reveal ledge / beginning of the Duat.
#
# Re-running is safe: deletes only actors prefixed "REN_".
# ============================================================

PREFIX = "REN_"

# ------------------------------------------------------------
# Safety guards (added 2026-09-30, sprint plan)
# Cleanup below deletes EVERY "REN_" actor in all loaded levels, including
# interactables (REN_INT_*) and other sublevels' actors if run inside the
# persistent slice level. So:
#   1) only run with L_Tomb_Blockout opened standalone;
#   2) refuse once a world-lock baseline exists (layout locked), unless an
#      approved rebuild sets FORCE_REBUILD_AFTER_LOCK = True for one run.
# ------------------------------------------------------------
EXPECTED_WORLD = "L_Tomb_Blockout"
FORCE_REBUILD_AFTER_LOCK = False

_editor_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not _editor_world or _editor_world.get_name() != EXPECTED_WORLD:
    raise RuntimeError(
        f"Builder v3 must run with {EXPECTED_WORLD} opened standalone "
        f"(current: {_editor_world.get_name() if _editor_world else None}). Nothing was changed."
    )

import os as _os
_baseline = _os.path.join(
    unreal.Paths.project_dir(), "ProjectDocs", "WorldLocks", f"{EXPECTED_WORLD}.worldlock.json"
)
if _os.path.exists(_baseline) and not FORCE_REBUILD_AFTER_LOCK:
    raise RuntimeError(
        "World-lock baseline exists: the Tomb layout is locked. Re-running v3 would delete and "
        "respawn all REN_ actors (including REN_INT_* interactables). Nothing was changed. "
        "Set FORCE_REBUILD_AFTER_LOCK = True only with explicit approval."
    )

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
cylinder_mesh = unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")

if not cube_mesh:
    raise RuntimeError("Could not load Engine Cube mesh.")

# ------------------------------------------------------------
# Clean old generated actors
# ------------------------------------------------------------
for actor in actor_subsystem.get_all_level_actors():
    try:
        if actor.get_actor_label().startswith(PREFIX):
            actor_subsystem.destroy_actor(actor)
    except Exception:
        pass

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def spawn_mesh(label, mesh, location, scale, rotation=(0.0, 0.0, 0.0)):
    actor = actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*location),
        unreal.Rotator(rotation[1], rotation[2], rotation[0])
    )
    if not actor:
        raise RuntimeError(f"Failed to spawn {label}")

    actor.set_actor_label(label)
    actor.set_actor_scale3d(unreal.Vector(*scale))

    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    comp.set_static_mesh(mesh)
    return actor

def cube(label, location, scale, rotation=(0.0, 0.0, 0.0)):
    return spawn_mesh(label, cube_mesh, location, scale, rotation)

def cylinder(label, location, scale, rotation=(0.0, 0.0, 0.0)):
    if not cylinder_mesh:
        return None
    return spawn_mesh(label, cylinder_mesh, location, scale, rotation)

def point_light(label, location, intensity, radius):
    actor = actor_subsystem.spawn_actor_from_class(
        unreal.PointLight,
        unreal.Vector(*location),
        unreal.Rotator(0.0, 0.0, 0.0)
    )
    actor.set_actor_label(label)
    comp = actor.get_component_by_class(unreal.PointLightComponent)
    comp.set_editor_property("intensity", float(intensity))
    comp.set_editor_property("attenuation_radius", float(radius))
    return actor

def spot_light(label, location, rotation, intensity, radius, inner=18.0, outer=35.0):
    actor = actor_subsystem.spawn_actor_from_class(
        unreal.SpotLight,
        unreal.Vector(*location),
        unreal.Rotator(rotation[1], rotation[2], rotation[0])
    )
    actor.set_actor_label(label)
    comp = actor.get_component_by_class(unreal.SpotLightComponent)
    comp.set_editor_property("intensity", float(intensity))
    comp.set_editor_property("attenuation_radius", float(radius))
    comp.set_editor_property("inner_cone_angle", float(inner))
    comp.set_editor_property("outer_cone_angle", float(outer))
    return actor

def trigger_box(label, location, scale):
    actor = actor_subsystem.spawn_actor_from_class(
        unreal.TriggerBox,
        unreal.Vector(*location),
        unreal.Rotator(0.0, 0.0, 0.0)
    )
    actor.set_actor_label(label)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    return actor

# ============================================================
# WORLD CONVENTION
# +Y = forward / toward the Duat
# 1 Unreal Unit = 1 cm
# ============================================================

# ============================================================
# 1) BURIAL CHAMBER
# ============================================================
# 8m x 10m x 4m
cube("REN_Tomb_Floor",      (0, 0, -10),   (8.0, 10.0, 0.20))
cube("REN_Tomb_Ceiling",    (0, 0, 410),   (8.0, 10.0, 0.20))
cube("REN_Tomb_LeftWall",   (-410, 0, 200), (0.20, 10.0, 4.0))
cube("REN_Tomb_RightWall",  (410, 0, 200),  (0.20, 10.0, 4.0))
cube("REN_Tomb_BackWall",   (0, -510, 200), (8.0, 0.20, 4.0))
cube("REN_Tomb_FrontLeft",  (-275, 510, 200), (2.5, 0.20, 4.0))
cube("REN_Tomb_FrontRight", (275, 510, 200),  (2.5, 0.20, 4.0))

# Sarcophagus composition: slightly rear of center.
cube("REN_Sarcophagus_Platform", (0, -130, 5),  (1.6, 2.9, 0.15))
cube("REN_Sarcophagus_Base",     (0, -130, 60), (1.15, 2.45, 0.70))
cube("REN_Sarcophagus_Lid",      (0, -130, 135), (1.20, 2.50, 0.18))

# Waking / camera staging markers (simple low blocks)
cube("REN_WakeMarker", (0, -315, 2), (0.4, 0.4, 0.04))

# Blank Cartouche clue wall on +X = PLAYER-LEFT when facing +Y
# (UE is left-handed; comment corrected 2026-09-30, geometry unchanged)
cube("REN_BlankCartouche_Panel", (385, 110, 205), (0.10, 2.2, 2.6))
# Greybox cartouche relief shape: tall oval cylinder flattened into wall
cylinder("REN_BlankCartouche_Relief", (370, 110, 225), (0.08, 0.72, 1.45), rotation=(0,90,0))

# Small funerary prop blocks around room
cube("REN_OfferingTable_Main", (-240, 100, 55), (1.25, 0.7, 0.60))
cube("REN_Canopic_01", (-285, 130, 45), (0.30, 0.30, 0.50))
cube("REN_Canopic_02", (-215, 135, 45), (0.30, 0.30, 0.50))
cube("REN_Canopic_03", (-250, 70, 45),  (0.30, 0.30, 0.50))

# ============================================================
# 2) CORRIDOR
# ============================================================
# 3m wide; long enough to pace the opening.
cube("REN_Corridor_Floor",   (0, 1250, -10), (3.0, 15.0, 0.20))
cube("REN_Corridor_Ceiling", (0, 1250, 410), (3.0, 15.0, 0.20))
cube("REN_Corridor_Right",   (160, 1250, 200), (0.20, 15.0, 4.0))

# Left side wall split for side chamber.
cube("REN_Corridor_Left_A", (-160, 760, 200),  (0.20, 5.2, 4.0))   # 500 -> 1020
# opening 1020 -> 1320
cube("REN_Corridor_Left_B", (-160, 1660, 200), (0.20, 6.8, 4.0))   # 1320 -> 2000

# Narrow columns / props in corridor for the future "no shadow" clue
cube("REN_ShadowTest_Column",   (95, 860, 140),  (0.45, 0.45, 2.8))
cube("REN_ShadowTest_Pedestal", (-70, 930, 55),  (0.8, 0.8, 0.6))
cube("REN_ShadowTest_JarA",     (-100, 1030, 38), (0.25, 0.25, 0.4))
cube("REN_ShadowTest_JarB",     (-35, 1045, 45),  (0.28, 0.28, 0.5))

# ============================================================
# 3) SIDE CLUE CHAMBER
# ============================================================
# Accessible on -X = PLAYER-RIGHT when facing +Y
# (comment corrected 2026-09-30, geometry unchanged).
cube("REN_Side_Floor",      (-525, 1170, -10), (7.1, 6.2, 0.20))
cube("REN_Side_Ceiling",    (-525, 1170, 410), (7.1, 6.2, 0.20))
cube("REN_Side_LeftWall",   (-890, 1170, 200), (0.20, 6.2, 4.0))
cube("REN_Side_FrontWall",  (-525, 850, 200),  (7.1, 0.20, 4.0))
cube("REN_Side_BackWall",   (-525, 1490, 200), (7.1, 0.20, 4.0))

# Clue composition
cube("REN_Side_CluePedestal", (-610, 1210, 70), (1.0, 1.0, 0.75))
cube("REN_Side_Table",        (-430, 1320, 55), (1.6, 0.75, 0.60))
cube("REN_Side_WallTablet",   (-875, 1210, 210), (0.08, 1.25, 1.6))

# Trigger placeholders for later Blueprint logic
trigger_box("REN_Trigger_BlankCartouche", (300, 110, 120), (1.2, 2.0, 1.8))
trigger_box("REN_Trigger_ShadowClue",      (0, 940, 120),  (1.5, 2.0, 1.8))
trigger_box("REN_Trigger_SideClue",        (-470, 1180, 120), (2.0, 2.0, 1.8))

# ============================================================
# 4) EXIT / REVEAL THRESHOLD
# ============================================================
# A larger, more monumental door.
cube("REN_ExitDoor",       (0, 2015, 155), (2.75, 0.30, 3.10))
cube("REN_ExitLintel",     (0, 2040, 380), (3.2, 0.40, 0.70))
cube("REN_ExitSide_Left",  (-170, 2040, 205), (0.65, 0.40, 4.10))
cube("REN_ExitSide_Right", (170, 2040, 205),  (0.65, 0.40, 4.10))

# Small transition tunnel after door
cube("REN_ExitTunnel_Floor",   (0, 2320, -10), (3.0, 6.0, 0.20))
cube("REN_ExitTunnel_Ceiling", (0, 2320, 410), (3.0, 6.0, 0.20))
cube("REN_ExitTunnel_Left",    (-160, 2320, 200), (0.20, 6.0, 4.0))
cube("REN_ExitTunnel_Right",   (160, 2320, 200),  (0.20, 6.0, 4.0))

# ============================================================
# 5) REVEAL LEDGE — beginning of Vertical Necropolis
# ============================================================
# This is intentionally simple: a ledge over an empty void.
cube("REN_RevealLedge", (0, 2750, -10), (7.5, 4.5, 0.20))
cube("REN_Reveal_LeftPier",  (-500, 2780, 180), (0.6, 1.4, 3.6))
cube("REN_Reveal_RightPier", (500, 2780, 180),  (0.6, 1.4, 3.6))

# Fake distant architecture silhouettes for the first reveal.
cube("REN_DistantTower_A", (-900, 4100, 800), (3.0, 4.0, 16.0))
cube("REN_DistantTower_B", (850, 4600, 1150), (4.0, 5.0, 23.0))
cube("REN_DistantGate",    (0, 5300, 550), (5.0, 1.0, 11.0))

trigger_box("REN_Trigger_ExitReveal", (0, 2720, 140), (3.0, 2.0, 2.0))

# ============================================================
# 6) PLAYER START
# ============================================================
player_start = actor_subsystem.spawn_actor_from_class(
    unreal.PlayerStart,
    unreal.Vector(0, -350, 110),
    unreal.Rotator(0.0, 90.0, 0.0)
)
player_start.set_actor_label("REN_PlayerStart")

# ============================================================
# 7) GREYBOX LIGHTING
# ============================================================
# Burial chamber warm light
point_light("REN_Light_Burial", (0, -80, 300), 5200, 1350)

# Hard side light used later to demonstrate the missing shadow mechanic.
point_light("REN_Light_ShadowTest", (-130, 900, 250), 7000, 800)

# Side chamber
point_light("REN_Light_Side", (-540, 1180, 280), 3200, 850)

# Corridor / exit
point_light("REN_Light_Corridor", (0, 1500, 290), 2500, 1100)

# Cold reveal light beyond exit, intentionally stronger.
point_light("REN_Light_DuatReveal", (0, 2900, 500), 9000, 1800)

# ============================================================
# 8) SAVE + LOG
# ============================================================
level_subsystem.save_current_level()

ren_labels = []
for actor in actor_subsystem.get_all_level_actors():
    try:
        if actor.get_actor_label().startswith(PREFIX):
            ren_labels.append(actor.get_actor_label())
    except Exception:
        pass

unreal.log("===========================================================")
unreal.log("REN Tomb Opening Greybox Builder v3 COMPLETE")
unreal.log(f"Generated REN actors: {len(ren_labels)}")
unreal.log("Flow: Sarcophagus -> Cartouche -> Corridor -> Shadow clue ->")
unreal.log("      Side clue -> Exit door -> Reveal ledge.")
unreal.log("===========================================================")
