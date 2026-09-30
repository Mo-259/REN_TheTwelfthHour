"""
REN — Vertical Necropolis greybox layout v1 (pure data, no `unreal` import)

Consumed by Scripts/Editor/REN_Necropolis_Greybox_Builder_v1.py (Unreal) and by
Scripts/Tests/test_necropolis_layout.py (offline). Design doc:
docs/NECROPOLIS_GREYBOX_SPEC.md.

COORDINATES (shared slice world, cm):
  +Y = forward, toward the Duat / Gate of the West
  +Z = up; Z 0 = Tomb floor = Reveal Ledge top
  UE is left-handed: facing +Y, the PLAYER'S RIGHT is -X and PLAYER'S LEFT is +X.
  Labels here use axis tags (_NX = -X side, _PX = +X side) to avoid left/right ambiguity.

All solids are axis-aligned boxes given as (min, max) corners. The Engine cube
(/Engine/BasicShapes/Cube) is 100 cm and centred, so centre = (min+max)/2 and
scale = (max-min)/100. No rotated solids -> no Rotator-ordering risk.

Existing Tomb actors are NOT rebuilt here. TOMB_REFERENCE holds their design
AABBs from builder v3 source (live Unreal transforms are authoritative; re-check
against the Tomb world-lock baseline once exported).
"""

PREFIX = "REN_NEC_"
EXPECTED_WORLD = "L_Necropolis_Blockout"
LAYOUT_VERSION = 1

# Route elevations
Z_LEDGE = 0
Z_COURT = -600
Z_VOID_BOTTOM = -3000
SLAB = 40            # floor slab thickness

# Stairs
STEP_RISE = 25       # UE default MaxStepHeight is 45
STEP_RUN = 30
STEP_COUNT = 24      # 24 * 25 = 600 rise, 24 * 30 = 720 run

PARAPET_H = 100
PARAPET_T = 30

# ---------------------------------------------------------------------------
# Existing Tomb actors (from REN_Tomb_Opening_Greybox_Builder_v3.py source)
# ---------------------------------------------------------------------------
TOMB_REFERENCE = {
    # Reveal set piece (playable, Tomb-owned)
    "REN_RevealLedge":       ((-375, 2525, -20), (375, 2975, 0)),
    "REN_Reveal_LeftPier":   ((-530, 2710, 0), (-470, 2850, 360)),   # map-left = -X = PLAYER-RIGHT
    "REN_Reveal_RightPier":  ((470, 2710, 0), (530, 2850, 360)),     # map-right = +X = PLAYER-LEFT
    "REN_ExitTunnel_Floor":  ((-150, 2020, -20), (150, 2620, 0)),
    "REN_ExitTunnel_Left":   ((-170, 2020, 0), (-150, 2620, 400)),
    "REN_ExitTunnel_Right":  ((150, 2020, 0), (170, 2620, 400)),
    # Skyline / landmark PROXIES (keep transforms; mesh may be replaced later)
    "REN_DistantTower_A":    ((-1050, 3900, 0), (-750, 4300, 1600)),  # player-right, near
    "REN_DistantTower_B":    ((650, 4350, 0), (1050, 4850, 2300)),    # player-left, farther, taller
    "REN_DistantGate":       ((-250, 5250, 0), (250, 5350, 1100)),    # on axis: Gate of the West facade
}
SKYLINE_PROXIES = ("REN_DistantTower_A", "REN_DistantTower_B", "REN_DistantGate")


def _box(label, kind, mn, mx, **extra):
    d = {"label": PREFIX + label, "kind": kind, "min": tuple(mn), "max": tuple(mx)}
    d.update(extra)
    return d


def _point(label, loc, intensity, radius):
    return {"label": PREFIX + label, "kind": "point_light", "loc": tuple(loc),
            "intensity": float(intensity), "radius": float(radius)}


def _spot(label, loc, rot, intensity, radius, inner, outer):
    return {"label": PREFIX + label, "kind": "spot_light", "loc": tuple(loc), "rot": dict(rot),
            "intensity": float(intensity), "radius": float(radius),
            "inner": float(inner), "outer": float(outer)}


def _target(label, loc, yaw=0.0):
    return {"label": PREFIX + label, "kind": "target", "loc": tuple(loc),
            "rot": {"roll": 0.0, "pitch": 0.0, "yaw": float(yaw)}}


def _stair(name, x0, x1, y_start, direction, z_bottom_top, going_up):
    """
    Build STEP_COUNT solid step blocks plus per-step parapets on both X sides.

    direction: +1 steps advance toward +Y, -1 toward -Y.
    going_up:  True  -> step tops rise from z_bottom_top+RISE to z_bottom_top+COUNT*RISE
               False -> step tops fall from -RISE (relative to z_bottom_top) downward
    Returns (items, step_tops) where step_tops[i] = (y0, y1, top_z).
    """
    items, tops = [], []
    for i in range(STEP_COUNT):
        a = y_start + direction * STEP_RUN * i
        b = y_start + direction * STEP_RUN * (i + 1)
        y0, y1 = min(a, b), max(a, b)
        if going_up:
            top = z_bottom_top + STEP_RISE * (i + 1)
        else:
            top = z_bottom_top - STEP_RISE * (i + 1)
        n = f"{i:02d}"
        items.append(_box(f"{name}_Step_{n}", "mesh", (x0, y0, Z_COURT - SLAB), (x1, y1, top)))
        items.append(_box(f"{name}_Parapet_NX_{n}", "mesh", (x0 - PARAPET_T, y0, top), (x0, y1, top + PARAPET_H)))
        items.append(_box(f"{name}_Parapet_PX_{n}", "mesh", (x1, y0, top), (x1 + PARAPET_T, y1, top + PARAPET_H)))
        tops.append((y0, y1, top))
    return items, tops


def build_layout():
    """Return the deterministic list of Necropolis greybox items."""
    L = []

    # -- N0 Reveal-ledge safety (adjacent to Tomb ledge, not modifying it) --------
    L.append(_box("Ledge_Parapet_Front", "mesh", (-45, 2975, 0), (375, 3005, PARAPET_H)))
    # Invisible blockers stop a running jump from the ledge / upper S1 steps
    # straight to the Bridge Head (~7 m), which would skip the Glyph gate.
    L.append(_box("Ledge_InvisWall_Front", "invis", (-45, 2975, PARAPET_H), (375, 3005, 600)))
    L.append(_box("Ledge_Parapet_NX", "mesh", (-405, 2525, 0), (-375, 2975, PARAPET_H)))
    L.append(_box("Ledge_Parapet_PX", "mesh", (375, 2525, 0), (405, 2975, PARAPET_H)))
    L.append(_box("Ledge_ParapetBack_NX", "mesh", (-375, 2495, 0), (-170, 2525, PARAPET_H)))
    L.append(_box("Ledge_ParapetBack_PX", "mesh", (170, 2495, 0), (375, 2525, PARAPET_H)))

    # -- N1 Descent stair S1 (player-right half of ledge front, going +Y, down) ---
    s1, _ = _stair("S1", -375, -75, 2975, +1, Z_LEDGE, going_up=False)
    L += s1   # bottom step top = -600 at y 3665..3695
    L.append(_box("S1_InvisWall_PX", "invis", (-45, 3005, Z_COURT), (-15, 3665, 600)))

    # -- N2 Lower Court T1 ---------------------------------------------------------
    L.append(_box("Court_Floor", "mesh", (-700, 3695, Z_COURT - SLAB), (250, 4850, Z_COURT)))
    L.append(_box("Court_Parapet_South_NX", "mesh", (-700, 3665, Z_COURT), (-405, 3695, Z_COURT + PARAPET_H)))
    L.append(_box("Court_Parapet_South_PX", "mesh", (-45, 3665, Z_COURT), (250, 3695, Z_COURT + PARAPET_H)))
    L.append(_box("Court_Parapet_NX", "mesh", (-730, 3850, Z_COURT), (-700, 4850, Z_COURT + PARAPET_H)))
    L.append(_box("Court_Parapet_North", "mesh", (-700, 4850, Z_COURT), (100, 4880, Z_COURT + PARAPET_H)))
    L.append(_box("Court_CornerWall", "mesh", (100, 4850, Z_COURT), (250, 4880, -150)))
    # Bridge support column standing in the court (under the bridge)
    L.append(_box("Bridge_Pier1_Column", "mesh", (-100, 4400, Z_COURT), (100, 4500, -SLAB)))
    L.append(_box("Bridge_Pier1_Lower", "mesh", (-100, 4400, Z_VOID_BOTTOM), (100, 4500, Z_COURT - SLAB)))

    # Glyph wall (+X edge of court) and the sealed slab the Glyph opens
    L.append(_box("GlyphWall", "mesh", (250, 3695, Z_COURT), (290, 4600, -150)))
    L.append(_box("GlyphSeal_Slab", "movable", (250, 4600, Z_COURT), (290, 4850, -150), sink_cm=460))
    L.append(_box("GlyphWall_End", "mesh", (250, 4850, Z_COURT), (290, 4880, -150)))
    L.append(_box("GlyphPanel", "mesh", (240, 4430, -520), (250, 4570, -280)))

    # -- Spur (player-right branch toward Tower A) + shadow tease -----------------
    L.append(_box("Spur_Floor", "mesh", (-1350, 3550, Z_COURT - SLAB), (-700, 3850, Z_COURT)))
    L.append(_box("Spur_Parapet_South", "mesh", (-1350, 3520, Z_COURT), (-700, 3550, Z_COURT + PARAPET_H)))
    L.append(_box("Spur_Parapet_End", "mesh", (-1380, 3520, Z_COURT), (-1350, 3880, Z_COURT + PARAPET_H)))
    L.append(_box("Spur_Parapet_North", "mesh", (-1350, 3850, Z_COURT), (-730, 3880, Z_COURT + PARAPET_H)))
    L.append(_box("Spur_CluePedestal", "mesh", (-1300, 3600, Z_COURT), (-1200, 3700, Z_COURT + 100)))

    # -- S2 ascent (player-left side of court, going -Y, up) -----------------------
    L.append(_box("Landing_S2_Floor", "mesh", (290, 4600, Z_COURT - SLAB), (620, 4850, Z_COURT)))
    L.append(_box("Landing_S2_Parapet_PX", "mesh", (620, 4600, Z_COURT), (650, 4850, Z_COURT + PARAPET_H)))
    L.append(_box("Landing_S2_CornerWall", "mesh", (290, 4850, Z_COURT), (440, 4880, -150)))
    L.append(_box("Landing_S2_Parapet_North", "mesh", (440, 4850, Z_COURT), (650, 4880, Z_COURT + PARAPET_H)))
    s2, _ = _stair("S2", 320, 620, 4600, -1, Z_COURT, going_up=True)
    L += s2   # top step top = 0 at y 3880..3910

    # -- Bridge head BH (arrival from S2; U-turn to face the Gate) ----------------
    L.append(_box("BridgeHead_Floor", "mesh", (-240, 3700, -SLAB), (620, 3880, Z_LEDGE)))
    L.append(_box("BridgeHead_Parapet_South", "mesh", (-270, 3670, -SLAB), (650, 3700, PARAPET_H)))
    L.append(_box("BridgeHead_Parapet_NX", "mesh", (-270, 3700, -SLAB), (-240, 3880, PARAPET_H)))
    L.append(_box("BridgeHead_Parapet_PX", "mesh", (620, 3700, -SLAB), (650, 3880, PARAPET_H)))
    L.append(_box("BridgeHead_Parapet_Gap", "mesh", (240, 3880, Z_LEDGE), (290, 3910, PARAPET_H)))

    # -- Anubis bridge ----------------------------------------------------------------
    L.append(_box("Bridge_Deck", "mesh", (-200, 3880, -SLAB), (200, 5150, Z_LEDGE)))
    L.append(_box("Bridge_Parapet_NX", "mesh", (-240, 3880, -SLAB), (-200, 5150, PARAPET_H)))
    L.append(_box("Bridge_Parapet_PX", "mesh", (200, 3880, -SLAB), (240, 5150, PARAPET_H)))
    L.append(_box("Bridge_Pier2", "mesh", (-100, 4950, Z_VOID_BOTTOM), (100, 5050, -SLAB)))

    # -- Gate plinth / plaza (base of REN_DistantGate; proxy itself untouched) ----
    L.append(_box("GatePlinth", "mesh", (-500, 5150, Z_VOID_BOTTOM), (500, 5450, Z_LEDGE)))
    L.append(_box("Plaza_Parapet_South_NX", "mesh", (-500, 5150, Z_LEDGE), (-240, 5180, PARAPET_H)))
    L.append(_box("Plaza_Parapet_South_PX", "mesh", (240, 5150, Z_LEDGE), (500, 5180, PARAPET_H)))
    L.append(_box("Plaza_Parapet_NX", "mesh", (-530, 5150, Z_LEDGE), (-500, 5450, PARAPET_H)))
    L.append(_box("Plaza_Parapet_PX", "mesh", (500, 5150, Z_LEDGE), (530, 5450, PARAPET_H)))
    L.append(_box("Gate_Wing_NX", "mesh", (-500, 5250, Z_LEDGE), (-250, 5350, 700)))
    L.append(_box("Gate_Wing_PX", "mesh", (250, 5250, Z_LEDGE), (500, 5350, 700)))

    # -- Foundations: extend skyline proxies DOWN into the void (no overlap) -------
    L.append(_box("TowerA_Foundation", "mesh", (-1050, 3900, Z_VOID_BOTTOM), (-750, 4300, Z_LEDGE)))
    L.append(_box("TowerB_Foundation", "mesh", (650, 4350, Z_VOID_BOTTOM), (1050, 4850, Z_LEDGE)))

    # -- Void dressing (no collision; skyline only) --------------------------------
    L.append(_box("Dressing_SuspendedSarc_01", "dressing", (-1920, 4650, -1040), (-1680, 4740, -960)))
    L.append(_box("Dressing_SuspendedSarc_02", "dressing", (1560, 3780, -740), (1650, 4020, -660)))
    L.append(_box("Dressing_SuspendedSarc_03", "dressing", (1780, 5150, -340), (2020, 5240, -260)))
    L.append(_box("Dressing_BlackRiver", "dressing", (-3000, 3200, 4000), (3000, 6500, 4050)))

    # -- Triggers (Blueprint logic added locally on Day 3) ------------------------
    L.append(_box("Trigger_ShadowTease", "trigger", (-400, 3400, -650), (-50, 3800, -250)))
    L.append(_box("Trigger_AnubisSlow", "trigger", (-200, 4300, 0), (200, 4450, 300)))
    L.append(_box("Trigger_AnubisDialogue", "trigger", (-200, 4650, 0), (200, 4750, 300)))
    L.append(_box("Trigger_FallRecovery", "trigger", (-3000, 2400, -1600), (3000, 6000, -1400)))

    # -- Markers (TargetPoints) --------------------------------------------------------
    L.append(_target("Marker_Anubis", (0, 4950, 0), yaw=-90))          # faces -Y, toward the player
    L.append(_target("Marker_ShadowWalk_Start", (-760, 3780, Z_COURT)))
    L.append(_target("Marker_ShadowWalk_End", (-1120, 3780, Z_COURT)))
    L.append(_target("Respawn_Ledge", (0, 2800, 100), yaw=90))
    L.append(_target("Respawn_Court", (-225, 3800, Z_COURT + 100), yaw=90))
    L.append(_target("Respawn_BridgeHead", (100, 3790, 100), yaw=90))

    # -- Lights (greybox; tune locally) -----------------------------------------------
    L.append(_point("Light_Court", (-250, 4200, -250), 4000, 1400))
    L.append(_point("Light_Glyph", (120, 4500, -350), 2500, 700))
    L.append(_point("Light_Stair2", (470, 4250, -200), 2500, 900))
    L.append(_point("Light_Bridge", (0, 4500, 350), 5000, 1600))
    L.append(_point("Light_Gate", (0, 5100, 500), 6000, 1600))
    L.append(_spot("Light_ShadowTease", (-900, 3600, -250),
                   {"roll": 0.0, "pitch": -10.0, "yaw": 90.0}, 8000, 1200, 20, 40))

    return L


# ---------------------------------------------------------------------------
# Geometry helpers + validation (used by builder before spawning, and tests)
# ---------------------------------------------------------------------------
SOLID_KINDS = ("mesh", "movable", "invis")
BOX_KINDS = SOLID_KINDS + ("dressing", "trigger")


def center_and_scale(mn, mx):
    c = tuple((a + b) / 2.0 for a, b in zip(mn, mx))
    s = tuple((b - a) / 100.0 for a, b in zip(mn, mx))
    return c, s


def overlap_volume(a_min, a_max, b_min, b_max, eps=0.01):
    """Positive only for true interpenetration; touching faces return 0."""
    v = 1.0
    for i in range(3):
        d = min(a_max[i], b_max[i]) - max(a_min[i], b_min[i])
        if d <= eps:
            return 0.0
        v *= d
    return v


def validate_layout(items):
    """Return a list of error strings (empty = valid)."""
    errors = []
    labels = [it["label"] for it in items]
    if len(labels) != len(set(labels)):
        seen, dup = set(), set()
        for l in labels:
            (dup if l in seen else seen).add(l)
        errors.append(f"duplicate labels: {sorted(dup)}")
    for it in items:
        if not it["label"].startswith(PREFIX):
            errors.append(f"bad prefix: {it['label']}")
        if it["kind"] in BOX_KINDS:
            if any(b - a <= 0 for a, b in zip(it["min"], it["max"])):
                errors.append(f"non-positive size: {it['label']}")

    solids = [it for it in items if it["kind"] in SOLID_KINDS]
    for it in solids + [i for i in items if i["kind"] == "dressing"]:
        for name, (mn, mx) in TOMB_REFERENCE.items():
            if overlap_volume(it["min"], it["max"], mn, mx) > 0:
                errors.append(f"{it['label']} overlaps Tomb actor {name}")
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
    print(f"REN Necropolis layout v{LAYOUT_VERSION}: {len(layout)} items {kinds}")
    print("VALID" if not errs else "INVALID:\n  " + "\n  ".join(errs))
