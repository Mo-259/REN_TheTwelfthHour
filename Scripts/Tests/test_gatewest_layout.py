"""
Offline tests for the Gate of the West greybox layout + builder.

Run from the repo root:
    python -m unittest discover -s Scripts/Tests -v

Builder tests use the FAKE `unreal` module from test_necropolis_layout: they
prove guard / cleanup / spawn logic only. Real Unreal behaviour and PIE are
LOCAL_VALIDATION_REQUIRED.
"""

import os
import runpy
import shutil
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EDITOR_DIR = os.path.join(REPO, "Scripts", "Editor")
sys.path.insert(0, EDITOR_DIR)
sys.path.insert(0, os.path.dirname(__file__))

import REN_GateWest_Layout as GW  # noqa: E402
import REN_Necropolis_Layout as NL  # noqa: E402
from test_necropolis_layout import make_fake_unreal, _FakeActor, _R  # noqa: E402

CAPSULE_R = 42
MIN_MAIN_PATH_W = 500
MIN_CEILING_CLEARANCE = 550


def by_label(items):
    return {it["label"]: it for it in items}


def solids(items):
    return [it for it in items if it["kind"] in GW.SOLID_KINDS]


def point_in_solid(items, x, y, z=50):
    for it in solids(items):
        mn, mx = it["min"], it["max"]
        if mn[0] < x < mx[0] and mn[1] < y < mx[1] and mn[2] < z < mx[2]:
            return it["label"]
    return None


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = GW.build_layout()
        cls.L = by_label(cls.items)

    def test_valid_deterministic_prefixed(self):
        self.assertEqual(GW.validate_layout(self.items), [])
        self.assertEqual(self.items, GW.build_layout())
        for it in self.items:
            self.assertTrue(it["label"].startswith("REN_GW_"), it["label"])

    def test_no_overlap_with_tomb_or_necropolis(self):
        nec = [it for it in NL.build_layout() if it["kind"] in NL.SOLID_KINDS]
        for a in solids(self.items):
            for name, (mn, mx) in NL.TOMB_REFERENCE.items():
                self.assertEqual(GW.overlap_volume(a["min"], a["max"], mn, mx), 0, (a["label"], name))
            for b in nec:
                self.assertEqual(GW.overlap_volume(a["min"], a["max"], b["min"], b["max"]), 0,
                                 (a["label"], b["label"]))

    def test_no_skyline_proxy_duplication(self):
        proxy_boxes = {NL.TOMB_REFERENCE[p] for p in NL.SKYLINE_PROXIES}
        for it in self.items:
            if "min" in it:
                self.assertNotIn((it["min"], it["max"]), proxy_boxes)
        self.assertFalse(any("DistantGate" in it["label"] or "DistantTower" in it["label"] for it in self.items))

    def test_connects_to_necropolis_plinth_on_gate_axis(self):
        plinth = by_label(NL.build_layout())["REN_NEC_GatePlinth"]
        gate_min, gate_max = NL.TOMB_REFERENCE["REN_DistantGate"]
        floor = self.L["REN_GW_Passage_Floor"]
        self.assertEqual(floor["min"][1], plinth["max"][1])
        self.assertEqual(floor["max"][2], plinth["max"][2])
        # Passage opening equals the gate leaf width, centred on the axis
        self.assertEqual((floor["min"][0], floor["max"][0]), (gate_min[0], gate_max[0]))
        # Passage walls close the plinth's north edge out to the plaza parapets (no fall gap)
        self.assertLessEqual(self.L["REN_GW_Passage_Wall_NX"]["min"][0], -530)
        self.assertGreaterEqual(self.L["REN_GW_Passage_Wall_PX"]["max"][0], 530)

    def test_floor_chain_continuous(self):
        chain = ["REN_GW_Passage_Floor", "REN_GW_Court_Floor", "REN_GW_CombatGate_Threshold",
                 "REN_GW_Corridor_Floor", "REN_GW_Arena_Threshold", "REN_GW_Arena_Floor", "REN_GW_Recess_Floor"]
        for a, b in zip(chain, chain[1:]):
            self.assertEqual(self.L[a]["max"][1], self.L[b]["min"][1], f"gap between {a} and {b}")
            self.assertEqual(self.L[a]["max"][2], self.L[b]["max"][2])

    def test_path_widths(self):
        for name in ("REN_GW_Passage_Floor", "REN_GW_Corridor_Floor", "REN_GW_CombatGate_Threshold"):
            f = self.L[name]
            self.assertGreaterEqual(f["max"][0] - f["min"][0], MIN_MAIN_PATH_W, name)
        court = self.L["REN_GW_Court_Floor"]
        pil = self.L["REN_GW_Court_Pilaster_PX_01"]
        self.assertGreaterEqual(2 * pil["min"][0], 1500, "court width between pilasters")
        self.assertGreaterEqual(court["max"][1] - court["min"][1], 1200)
        arena = self.L["REN_GW_Arena_Floor"]
        self.assertGreaterEqual(arena["max"][0] - arena["min"][0], 2000)
        self.assertLessEqual(arena["max"][0] - arena["min"][0], 2600, "arena must not be oversized")

    def test_axis_walkable(self):
        """A straight walk up x=0 from the plaza to the recess hits no solid except the closed combat gate."""
        y = GW.Y_START + 10
        while y < GW.RECESS[1] - 10:
            hit = point_in_solid(self.items, 0, y)
            self.assertIn(hit, (None, "REN_GW_CombatGate_Slab"), f"blocked at y={y} by {hit}")
            y += 25

    def test_ceiling_clearance(self):
        for name in ("REN_GW_Passage_Lintel_South", "REN_GW_Passage_Lintel_North",
                     "REN_GW_Corridor_Lintel", "REN_GW_Recess_Lintel"):
            self.assertGreaterEqual(self.L[name]["min"][2], MIN_CEILING_CLEARANCE, name)

    def test_combat_gate_seals_and_sinks(self):
        slab = self.L["REN_GW_CombatGate_Slab"]
        self.assertEqual(slab["kind"], "movable")
        wall_nx = self.L["REN_GW_Court_WallNorth_NX"]
        wall_px = self.L["REN_GW_Court_WallNorth_PX"]
        self.assertEqual(slab["min"][0], wall_nx["max"][0])
        self.assertEqual(slab["max"][0], wall_px["min"][0])
        self.assertGreaterEqual(slab["max"][2], 450, "slab unjumpable")
        self.assertGreaterEqual(slab["sink_cm"], slab["max"][2] - slab["min"][2])

    def test_enemy_markers_inside_court_with_margin(self):
        court = self.L["REN_GW_Court_Floor"]
        for n in ("REN_GW_Marker_Enemy_01", "REN_GW_Marker_Enemy_02", "REN_GW_Marker_Enemy_03_Optional"):
            x, y, _ = self.L[n]["loc"]
            self.assertGreaterEqual(x - court["min"][0], 300)
            self.assertGreaterEqual(court["max"][0] - x, 300)
            self.assertGreaterEqual(y - court["min"][1], 300)
            self.assertGreaterEqual(court["max"][1] - y, 300)
            self.assertIsNone(point_in_solid(self.items, x, y))

    def test_arena_sweep_room_and_pillars(self):
        cx, cy, _ = self.L["REN_GW_Marker_FaceEater_Center_PLACEHOLDER"]["loc"]
        pillars = [it for it in self.items if "GlyphPillar" in it["label"]]
        self.assertEqual(len(pillars), 4)
        for p in pillars:
            px = (p["min"][0] + p["max"][0]) / 2
            py = (p["min"][1] + p["max"][1]) / 2
            self.assertGreaterEqual(((px - cx) ** 2 + (py - cy) ** 2) ** 0.5, 600, "sweep room around boss centre")
            # player can pass between pillar and side wall
            self.assertGreaterEqual(GW.ARENA_HALF_W - p["max"][0] if px > 0 else p["min"][0] + GW.ARENA_HALF_W,
                                    2 * CAPSULE_R + 150)
        self.assertEqual(self.L["REN_GW_Marker_FaceEater_Start_PLACEHOLDER"]["loc"][0], 0)
        self.assertTrue(all("PLACEHOLDER" in it["label"] for it in self.items if "FaceEater" in it["label"]))

    def test_no_face_eater_logic_objects(self):
        for it in self.items:
            if "FaceEater" in it["label"]:
                self.assertEqual(it["kind"], "target")

    def test_respawns_clear_and_facing_forward(self):
        for n in ("REN_GW_Respawn_Approach", "REN_GW_Respawn_ArenaApproach"):
            x, y, z = self.L[n]["loc"]
            self.assertIsNone(point_in_solid(self.items, x, y, z))
            self.assertEqual(self.L[n]["rot"]["yaw"], 90.0)


# ---------------------------------------------------------------------------
# Face-Eater arena requirements (static). Constants MIRROR docs/FACE_EATER_BOSS_SPEC.md
# (§ "Arena requirements" and "Attack set"). Change both together.
# ---------------------------------------------------------------------------
BOSS_HEIGHT = 380
BOSS_CAPSULE_R = 90
PLAYER_CAPSULE_R = 42
SWEEP_REACH = 420                  # radius from boss centre
HEAVY_IMPACT_OFFSET, HEAVY_IMPACT_R = 400, 220
INTERACT_REACH = 300               # practical reach to a pillar face (P1 trace 350, minus margin)
PLAYER_RUN_SPEED = 500             # cm/s (template default; verify locally)
REACTION_TIME = 0.5                # s
HEAVY_GLYPH_WINDOW = 2.8           # s
SWEEP_GLYPH_WINDOW = 1.5           # s


class FaceEaterArenaRequirementsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = GW.build_layout()
        cls.L = by_label(cls.items)
        cls.pillars = [it for it in cls.items if "GlyphPillar" in it["label"]]

    def _dist_to_box_2d(self, x, y, box):
        dx = max(box["min"][0] - x, 0, x - box["max"][0])
        dy = max(box["min"][1] - y, 0, y - box["max"][1])
        return (dx * dx + dy * dy) ** 0.5

    def _arena_points(self, step=50):
        a0, a1 = GW.ARENA
        hw = GW.ARENA_HALF_W - PLAYER_CAPSULE_R
        x = -hw
        while x <= hw:
            y = a0 + PLAYER_CAPSULE_R
            while y <= a1 - PLAYER_CAPSULE_R:
                if not any(self._dist_to_box_2d(x, y, p) < PLAYER_CAPSULE_R for p in self.pillars):
                    yield x, y
                y += step
            x += step

    def test_max_distance_to_nearest_pillar(self):
        worst = max(min(self._dist_to_box_2d(x, y, p) for p in self.pillars) for x, y in self._arena_points())
        self.assertLessEqual(worst, 800, f"worst distance to a pillar = {worst:.0f} cm")
        # Heavy Strike window must be reachable from ANYWHERE in the arena.
        t = max(0.0, worst - INTERACT_REACH) / PLAYER_RUN_SPEED + REACTION_TIME
        self.assertLess(t, HEAVY_GLYPH_WINDOW, f"heavy window unreachable: needs {t:.2f}s")

    def test_sweep_window_reachable_when_fighting_near_a_pillar(self):
        # Sweep is the 'possible' opportunity: reachable if the player fights within ~5 m of a pillar.
        t = max(0.0, 500 - INTERACT_REACH) / PLAYER_RUN_SPEED + REACTION_TIME
        self.assertLess(t, SWEEP_GLYPH_WINDOW)

    def test_boss_can_follow_everywhere_no_safe_pockets(self):
        boss_d = 2 * BOSS_CAPSULE_R + 20
        hw = GW.ARENA_HALF_W
        for p in self.pillars:
            side_gap = hw - p["max"][0] if p["min"][0] > 0 else p["min"][0] + hw
            self.assertGreaterEqual(side_gap, boss_d, f"{p['label']} pillar-wall gap traps the boss")
        xs = sorted({(p["min"][0], p["max"][0]) for p in self.pillars})
        ys = sorted({(p["min"][1], p["max"][1]) for p in self.pillars})
        self.assertGreaterEqual(xs[1][0] - xs[0][1], boss_d)
        self.assertGreaterEqual(ys[1][0] - ys[0][1], boss_d)
        for p in self.pillars:   # pillar-to-end-wall gap
            self.assertGreaterEqual(min(p["min"][1] - GW.ARENA[0], GW.ARENA[1] - p["max"][1]), boss_d)
        # Corners: a player pressed into a corner is still inside sweep reach of a boss touching the walls.
        corner_gap = ((BOSS_CAPSULE_R + PLAYER_CAPSULE_R) * 2 ** 0.5)
        self.assertLess(corner_gap, SWEEP_REACH)

    def test_recess_fits_boss(self):
        lintel = self.L["REN_GW_Recess_Lintel"]
        recess = self.L["REN_GW_Recess_Floor"]
        self.assertGreater(lintel["min"][2], BOSS_HEIGHT + 50)
        self.assertGreaterEqual(recess["max"][0] - recess["min"][0], 2 * BOSS_CAPSULE_R + 100)

    def test_sweep_room_inside_arena(self):
        cx, cy, _ = self.L["REN_GW_Marker_FaceEater_Center_PLACEHOLDER"]["loc"]
        self.assertGreaterEqual(GW.ARENA_HALF_W - abs(cx), SWEEP_REACH + 200)
        self.assertGreaterEqual(min(cy - GW.ARENA[0], GW.ARENA[1] - cy), HEAVY_IMPACT_OFFSET + HEAVY_IMPACT_R)

    def test_entry_lock_and_trigger(self):
        slab = self.L["REN_GW_ArenaGate_Slab"]
        thr = self.L["REN_GW_Arena_Threshold"]
        trig = self.L["REN_GW_Trigger_ArenaEnter"]
        self.assertEqual(slab["kind"], "movable")
        self.assertLessEqual(slab["max"][2], thr["min"][2], "open (built) state must be below the threshold")
        self.assertEqual((slab["min"][0], slab["max"][0]), (thr["min"][0], thr["max"][0]))
        self.assertGreaterEqual(slab["max"][2] + slab["rise_cm"], 450, "raised slab must be unjumpable")
        self.assertGreaterEqual(slab["max"][2] + slab["rise_cm"] - (slab["max"][2] - slab["min"][2]), thr["min"][2],
                                "raised slab must reach down to the threshold (no crawl gap)")
        self.assertGreaterEqual(trig["min"][1] - slab["max"][1], 150, "player must be clear of the slab when it rises")
        self.assertGreaterEqual(trig["min"][1], GW.ARENA[0])
        self.assertEqual((trig["min"][0], trig["max"][0]), (-GW.ARENA_HALF_W, GW.ARENA_HALF_W), "full arena width")


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.project = tempfile.mkdtemp()
        self.log = {"destroyed": [], "spawned": 0, "saves": 0, "info": [], "warn": []}
        self.unrelated = _FakeActor("StaticMeshActor", (0, 0, 0), _R(), label="Floor")
        self.actors = [self.unrelated]
        self._saved = sys.modules.get("unreal")
        self.n = len(GW.build_layout())

    def tearDown(self):
        if self._saved is None:
            sys.modules.pop("unreal", None)
        else:
            sys.modules["unreal"] = self._saved
        shutil.rmtree(self.project)

    def _run(self, world="L_GateWest_Blockout"):
        sys.modules["unreal"] = make_fake_unreal(self.project, world, self.actors, self.log)
        runpy.run_path(os.path.join(EDITOR_DIR, "REN_GateWest_Greybox_Builder_v1.py"), run_name="__main__")

    def _gw(self):
        return [a for a in self.actors if a.label.startswith("REN_GW_")]

    def test_wrong_world_refused(self):
        for world in ("L_Necropolis_Blockout", "L_REN_Slice", "L_Tomb_Blockout"):
            with self.assertRaises(RuntimeError):
                self._run(world)
        self.assertEqual(self.log["spawned"], 0)

    def test_necropolis_or_tomb_actors_loaded_refused_nothing_deleted(self):
        nec = _FakeActor("StaticMeshActor", (0, 0, 0), _R(), label="REN_NEC_GatePlinth")
        tomb = _FakeActor("StaticMeshActor", (0, 0, 0), _R(), label="REN_DistantGate")
        self.actors += [nec, tomb]
        with self.assertRaises(RuntimeError):
            self._run()
        self.assertEqual(self.log["destroyed"], [])
        self.assertIn(nec, self.actors)
        self.assertIn(tomb, self.actors)

    def test_locked_baseline_refused(self):
        d = os.path.join(self.project, "ProjectDocs", "WorldLocks")
        os.makedirs(d)
        with open(os.path.join(d, "L_GateWest_Blockout.worldlock.json"), "w") as f:
            f.write("{}")
        with self.assertRaises(RuntimeError):
            self._run()
        self.assertEqual(self.log["spawned"], 0)

    def test_build_rerun_and_deletion_scope(self):
        interact = _FakeActor("BP_EncounterController_C", (0, 6400, 0), _R(), label="REN_INT_GW_Encounter01")
        cam = _FakeActor("CameraActor", (0, 0, 0), _R(), label="REN_CAM_GW_Test")
        self.actors += [interact, cam]
        self._run()
        self.assertEqual(len(self._gw()), self.n)
        self._run()
        self.assertEqual(len(self._gw()), self.n, "re-run must not duplicate")
        self.assertEqual(len(self.log["destroyed"]), self.n)
        self.assertTrue(all(l.startswith("REN_GW_") for l in self.log["destroyed"]))
        for keep in (self.unrelated, interact, cam):
            self.assertIn(keep, self.actors)
        self.assertEqual(self.log["saves"], 2)
        self.assertFalse(self.log["warn"])
        A = {a.label: a for a in self._gw()}
        self.assertEqual(A["REN_GW_CombatGate_Slab"].comp.props["mobility"], "MOVABLE")
        self.assertEqual(A["REN_GW_Marker_Enemy_01"].rot.yaw, -90.0)
        self.assertTrue(all(a.folder.startswith("REN_GW/") for a in self._gw()))


if __name__ == "__main__":
    unittest.main()
