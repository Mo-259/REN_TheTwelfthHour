"""
REN — Gate of the West greybox layout v1 (pure data, no `unreal` import)

Consumed by Scripts/Editor/REN_GateWest_Greybox_Builder_v1.py (Unreal) and by
Scripts/Tests/test_gatewest_layout.py (offline). Design doc:
docs/GATE_WEST_GREYBOX_SPEC.md.

Shared slice coordinates (same as Tomb + Necropolis):
  +Y forward (toward the West), +Z up, Z 0 = walk level of ledge/bridge/plaza.
  Facing +Y, PLAYER-RIGHT = -X. Labels use _NX / _PX side tags.

Starts where the Necropolis gate plinth ends (y 5450) on the Gate axis x = 0.
REN_DistantGate (Tomb skyline proxy) is NOT rebuilt or duplicated here; it is
opened at runtime by a Blueprint (see spec §4). No Face-Eater logic here: the
arena is a spatial shell with markers only (plus the entry lock
slab + ArenaEnter trigger used by the boss encounter; no boss logic here).
"""

import REN_Necropolis_Layout as NL

PREFIX = "REN_GW_"
EXPECTED_WORLD = "L_GateWest_Blockout"
LAYOUT_VERSION = 1

Z0 = 0
SLAB = 40
Y_START = 5450          # Necropolis GatePlinth max Y

# Zone Y bounds (interior, walkable)
PASSAGE = (5450, 6250)      # compressed threshold, x -250..250
COURT = (6250, 7650)        # first combat, x -900..900
COURT_GATE = (7650, 7750)   # wall line with combat-gate slab, x -300..300
CORRIDOR = (7750, 8450)     # arena approach, x -300..300
ARENA_WALL_S = (8450, 8550)
ARENA = (8550, 10450)       # boss arena shell, x -1100..1100
RECESS = (10450, 10950)     # boss entrance recess, x -300..300

PASSAGE_HALF_W = 250
COURT_HALF_W = 900
CORRIDOR_HALF_W = 300
ARENA_HALF_W = 1100


def _box(label, kind, mn, mx, **extra):
    d = {"label": PREFIX + label, "kind": kind, "min": tuple(mn), "max": tuple(mx)}
    d.update(extra)
    return d


def _point(label, loc, intensity, radius):
    return {"label": PREFIX + label, "kind": "point_light", "loc": tuple(loc),
            "intensity": float(intensity), "radius": float(radius)}


def _target(label, loc, yaw=0.0):
    return {"label": PREFIX + label, "kind": "target", "loc": tuple(loc),
            "rot": {"roll": 0.0, "pitch": 0.0, "yaw": float(yaw)}}


def build_layout():
    L = []
    y0, y1 = PASSAGE
    # -- 1. Compressed threshold passage (basalt mass, two lintels) ---------------
    L.append(_box("Passage_Floor", "mesh", (-PASSAGE_HALF_W, y0, -SLAB), (PASSAGE_HALF_W, y1, Z0)))
    L.append(_box("Passage_Wall_NX", "mesh", (-530, y0, Z0), (-PASSAGE_HALF_W, y1, 800)))
    L.append(_box("Passage_Wall_PX", "mesh", (PASSAGE_HALF_W, y0, Z0), (530, y1, 800)))
    L.append(_box("Passage_Lintel_South", "mesh", (-PASSAGE_HALF_W, y0, 600), (PASSAGE_HALF_W, y0 + 200, 800)))
    L.append(_box("Passage_Lintel_North", "mesh", (-PASSAGE_HALF_W, y1 - 200, 600), (PASSAGE_HALF_W, y1, 800)))

    # -- 2. First combat court -----------------------------------------------------
    c0, c1 = COURT
    L.append(_box("Court_Floor", "mesh", (-COURT_HALF_W, c0, -SLAB), (COURT_HALF_W, c1, Z0)))
    L.append(_box("Court_WallSouth_NX", "mesh", (-1000, c0 - 100, Z0), (-530, c0, 600)))
    L.append(_box("Court_WallSouth_PX", "mesh", (530, c0 - 100, Z0), (1000, c0, 600)))
    L.append(_box("Court_Wall_NX", "mesh", (-1000, c0, Z0), (-COURT_HALF_W, c1 + 100, 600)))
    L.append(_box("Court_Wall_PX", "mesh", (COURT_HALF_W, c0, Z0), (1000, c1 + 100, 600)))
    L.append(_box("Court_WallNorth_NX", "mesh", (-COURT_HALF_W, c1, Z0), (-CORRIDOR_HALF_W, c1 + 100, 600)))
    L.append(_box("Court_WallNorth_PX", "mesh", (CORRIDOR_HALF_W, c1, Z0), (COURT_HALF_W, c1 + 100, 600)))
    # Perimeter pilasters (landmarks; against the side walls, out of the fight)
    for i, (py0, py1) in enumerate(((6700, 6850), (7150, 7300)), start=1):
        L.append(_box(f"Court_Pilaster_NX_{i:02d}", "mesh", (-COURT_HALF_W, py0, Z0), (-750, py1, 700)))
        L.append(_box(f"Court_Pilaster_PX_{i:02d}", "mesh", (750, py0, Z0), (COURT_HALF_W, py1, 700)))
    # Stelae flanking the exit: the "go here" landmark
    L.append(_box("Court_Stela_NX", "mesh", (-500, c1 - 100, Z0), (-350, c1, 900)))
    L.append(_box("Court_Stela_PX", "mesh", (350, c1 - 100, Z0), (500, c1, 900)))
    # Combat gate: threshold floor + slab that sinks when the encounter is cleared
    g0, g1 = COURT_GATE
    L.append(_box("CombatGate_Threshold", "mesh", (-CORRIDOR_HALF_W, g0, -SLAB), (CORRIDOR_HALF_W, g1, Z0)))
    L.append(_box("CombatGate_Slab", "movable", (-CORRIDOR_HALF_W, g0, Z0), (CORRIDOR_HALF_W, g1, 600), sink_cm=640))

    # -- 3. Arena approach corridor ------------------------------------------------
    r0, r1 = CORRIDOR
    L.append(_box("Corridor_Floor", "mesh", (-CORRIDOR_HALF_W, r0, -SLAB), (CORRIDOR_HALF_W, r1, Z0)))
    L.append(_box("Corridor_Wall_NX", "mesh", (-500, r0, Z0), (-CORRIDOR_HALF_W, r1, 800)))
    L.append(_box("Corridor_Wall_PX", "mesh", (CORRIDOR_HALF_W, r0, Z0), (500, r1, 800)))
    L.append(_box("Corridor_Lintel", "mesh", (-CORRIDOR_HALF_W, r1 - 200, 600), (CORRIDOR_HALF_W, r1, 800)))

    # -- 4. Face-Eater arena SHELL (no boss logic) ---------------------------------
    s0, s1 = ARENA_WALL_S
    a0, a1 = ARENA
    L.append(_box("Arena_Threshold", "mesh", (-CORRIDOR_HALF_W, s0, -SLAB), (CORRIDOR_HALF_W, s1, Z0)))
    # Arena entry lock (added for the C-05 boss spec): rests BELOW the threshold
    # (built/open state) and RISES 640 cm to seal the entry while the boss fight runs.
    L.append(_box("ArenaGate_Slab", "movable", (-CORRIDOR_HALF_W, s0, -SLAB - 600), (CORRIDOR_HALF_W, s1, -SLAB),
                  rise_cm=640))
    L.append(_box("Arena_WallSouth_NX", "mesh", (-1200, s0, Z0), (-CORRIDOR_HALF_W, s1, 900)))
    L.append(_box("Arena_WallSouth_PX", "mesh", (CORRIDOR_HALF_W, s0, Z0), (1200, s1, 900)))
    L.append(_box("Arena_Floor", "mesh", (-ARENA_HALF_W, a0, -SLAB), (ARENA_HALF_W, a1, Z0)))
    L.append(_box("Arena_Wall_NX", "mesh", (-1200, a0, Z0), (-ARENA_HALF_W, a1 + 100, 900)))
    L.append(_box("Arena_Wall_PX", "mesh", (ARENA_HALF_W, a0, Z0), (1200, a1 + 100, 900)))
    L.append(_box("Arena_WallNorth_NX", "mesh", (-ARENA_HALF_W, a1, Z0), (-CORRIDOR_HALF_W, a1 + 100, 900)))
    L.append(_box("Arena_WallNorth_PX", "mesh", (CORRIDOR_HALF_W, a1, Z0), (ARENA_HALF_W, a1 + 100, 900)))
    # Glyph pillar shells: fixed landmarks now; Glyph Blueprints are layered on later (Day 5)
    for i, (px, py) in enumerate(((-650, 9150), (650, 9150), (-650, 9950), (650, 9950)), start=1):
        L.append(_box(f"Arena_GlyphPillar_{i:02d}", "mesh", (px - 60, py - 60, Z0), (px + 60, py + 60, 600)))
    # Boss entrance recess (north, on axis)
    e0, e1 = RECESS
    L.append(_box("Recess_Floor", "mesh", (-CORRIDOR_HALF_W, a1, -SLAB), (CORRIDOR_HALF_W, e1, Z0)))
    L.append(_box("Recess_Wall_NX", "mesh", (-400, a1 + 100, Z0), (-CORRIDOR_HALF_W, e1, 900)))
    L.append(_box("Recess_Wall_PX", "mesh", (CORRIDOR_HALF_W, a1 + 100, Z0), (400, e1, 900)))
    L.append(_box("Recess_WallBack", "mesh", (-400, e1, Z0), (400, e1 + 100, 900)))
    L.append(_box("Recess_Lintel", "mesh", (-CORRIDOR_HALF_W, a1, 700), (CORRIDOR_HALF_W, a1 + 100, 900)))

    # -- Triggers (logic added locally) ---------------------------------------------
    # Gate opener sits on the Necropolis plaza (south of REN_DistantGate); GW-owned.
    L.append(_box("Trigger_GateOpen", "trigger", (-500, 5160, Z0), (500, 5245, 300)))
    L.append(_box("Trigger_Checkpoint_Approach", "trigger", (-PASSAGE_HALF_W, 5700, Z0), (PASSAGE_HALF_W, 5900, 300)))
    L.append(_box("Trigger_EncounterStart", "trigger", (-COURT_HALF_W, 6300, Z0), (COURT_HALF_W, 6500, 400)))
    L.append(_box("Trigger_Checkpoint_ArenaApproach", "trigger", (-CORRIDOR_HALF_W, 7850, Z0), (CORRIDOR_HALF_W, 8150, 300)))
    # Boss encounter start: deep inside the arena (>= 250 cm past the entry slab line) so normal
    # forward movement puts the whole player capsule well clear of the slab before it may rise.
    # The slab additionally runs a runtime closure-safety check (FACE_EATER_BOSS_SPEC §9).
    L.append(_box("Trigger_ArenaEnter", "trigger", (-ARENA_HALF_W, 8800, Z0), (ARENA_HALF_W, 9000, 400)))

    # -- Markers ------------------------------------------------------------------------
    L.append(_target("Respawn_Approach", (0, 5800, 100), yaw=90))
    L.append(_target("Respawn_ArenaApproach", (0, 8000, 100), yaw=90))
    L.append(_target("Marker_Enemy_01", (-300, 6950, 0), yaw=-90))
    L.append(_target("Marker_Enemy_02", (300, 7100, 0), yaw=-90))
    L.append(_target("Marker_Enemy_03_Optional", (0, 7350, 0), yaw=-90))
    L.append(_target("Marker_FaceEater_Start_PLACEHOLDER", (0, 10700, 0), yaw=-90))
    L.append(_target("Marker_FaceEater_Center_PLACEHOLDER", (0, 9550, 0), yaw=-90))

    # -- Lights (greybox; tune locally) ---------------------------------------------
    L.append(_point("Light_Passage", (0, 5850, 450), 2500, 1200))
    L.append(_point("Light_Court", (0, 6950, 700), 6000, 2200))
    L.append(_point("Light_Stelae", (0, 7450, 500), 2500, 900))
    L.append(_point("Light_Corridor", (0, 8100, 450), 2500, 1000))
    L.append(_point("Light_Arena_NX", (-500, 9550, 800), 6000, 2000))
    L.append(_point("Light_Arena_PX", (500, 9550, 800), 6000, 2000))
    L.append(_point("Light_Recess", (0, 10700, 400), 800, 600))
    return L


# ---------------------------------------------------------------------------
# Validation (shared geometry helpers from the Necropolis layout module)
# ---------------------------------------------------------------------------
center_and_scale = NL.center_and_scale
overlap_volume = NL.overlap_volume
SOLID_KINDS = NL.SOLID_KINDS
BOX_KINDS = NL.BOX_KINDS


def validate_layout(items):
    """Return a list of error strings (empty = valid)."""
    errors = []
    labels = [it["label"] for it in items]
    if len(labels) != len(set(labels)):
        errors.append("duplicate labels")
    for it in items:
        if not it["label"].startswith(PREFIX):
            errors.append(f"bad prefix: {it['label']}")
        if it["kind"] in BOX_KINDS and any(b - a <= 0 for a, b in zip(it["min"], it["max"])):
            errors.append(f"non-positive size: {it['label']}")

    solids = [it for it in items if it["kind"] in SOLID_KINDS]
    nec_solids = [it for it in NL.build_layout() if it["kind"] in SOLID_KINDS]
    for it in solids:
        for name, (mn, mx) in NL.TOMB_REFERENCE.items():
            if overlap_volume(it["min"], it["max"], mn, mx) > 0:
                errors.append(f"{it['label']} overlaps Tomb actor {name}")
        for n in nec_solids:
            if overlap_volume(it["min"], it["max"], n["min"], n["max"]) > 0:
                errors.append(f"{it['label']} overlaps Necropolis actor {n['label']}")
    for i, a in enumerate(solids):
        for b in solids[i + 1:]:
            if overlap_volume(a["min"], a["max"], b["min"], b["max"]) > 0:
                errors.append(f"{a['label']} overlaps {b['label']}")
    return errors


if __name__ == "__main__":
    layout = build_layout()
    errs = validate_layout(layout)
    kinds = {}
    for it in layout:
        kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    print(f"REN Gate of the West layout v{LAYOUT_VERSION}: {len(layout)} items {kinds}")
    print("VALID" if not errs else "INVALID:\n  " + "\n  ".join(errs))
