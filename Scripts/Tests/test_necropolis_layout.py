"""
Offline tests for the Vertical Necropolis greybox layout + builder.

Run from the repo root:
    python -m unittest discover -s Scripts/Tests -v

Layout tests check geometry rules from docs/NECROPOLIS_GREYBOX_SPEC.md.
Builder tests run REN_Necropolis_Greybox_Builder_v1.py against a FAKE `unreal`
module: they prove guard/cleanup/spawn logic only. Real Unreal API behaviour and
PIE traversal are LOCAL_VALIDATION_REQUIRED.
"""

import os
import runpy
import shutil
import sys
import tempfile
import types
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EDITOR_DIR = os.path.join(REPO, "Scripts", "Editor")
sys.path.insert(0, EDITOR_DIR)

import REN_Necropolis_Layout as NL  # noqa: E402

UE_MAX_STEP_HEIGHT = 45
ASSUMED_JUMP_APEX_CM = 250      # template JumpZVelocity ~700, gravity 980 -> ~250 cm
CAPSULE_HEIGHT = 176
MIN_HEADROOM = 350


def by_label(items):
    return {it["label"]: it for it in items}


def steps(items, stair):
    out = [it for it in items if it["label"].startswith(f"REN_NEC_{stair}_Step_")]
    return sorted(out, key=lambda it: it["label"])


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = NL.build_layout()
        cls.L = by_label(cls.items)

    def test_valid_and_deterministic(self):
        self.assertEqual(NL.validate_layout(self.items), [])
        self.assertEqual(self.items, NL.build_layout())

    def test_prefix_and_no_proxy_duplication(self):
        for it in self.items:
            self.assertTrue(it["label"].startswith("REN_NEC_"), it["label"])
        proxy_boxes = {NL.TOMB_REFERENCE[p] for p in NL.SKYLINE_PROXIES}
        for it in self.items:
            if "min" in it:
                self.assertNotIn((it["min"], it["max"]), proxy_boxes, f"{it['label']} duplicates a proxy")
        for p in NL.SKYLINE_PROXIES:
            self.assertNotIn(p.replace("REN_", "REN_NEC_"), self.L)

    def test_foundations_extend_proxies_downward(self):
        for proxy, found in (("REN_DistantTower_A", "REN_NEC_TowerA_Foundation"),
                             ("REN_DistantTower_B", "REN_NEC_TowerB_Foundation")):
            pmin, pmax = NL.TOMB_REFERENCE[proxy]
            f = self.L[found]
            self.assertEqual(f["min"][:2], pmin[:2])
            self.assertEqual(f["max"][:2], pmax[:2])
            self.assertEqual(f["max"][2], pmin[2], "foundation must touch proxy base, not overlap")
        gmin, gmax = NL.TOMB_REFERENCE["REN_DistantGate"]
        plinth = self.L["REN_NEC_GatePlinth"]
        self.assertEqual(plinth["max"][2], gmin[2])
        self.assertLessEqual(plinth["min"][1], gmin[1])
        self.assertGreaterEqual(plinth["max"][1], gmax[1])

    def test_stair_rules(self):
        for name in ("S1", "S2"):
            st = steps(self.items, name)
            self.assertEqual(len(st), NL.STEP_COUNT)
            self.assertLessEqual(NL.STEP_RISE, UE_MAX_STEP_HEIGHT)
            tops = [s["max"][2] for s in st]
            for a, b in zip(tops, tops[1:]):
                self.assertLessEqual(abs(a - b), UE_MAX_STEP_HEIGHT)
            width = st[0]["max"][0] - st[0]["min"][0]
            self.assertGreaterEqual(width, 300)

    def test_route_connectivity(self):
        ledge_min, ledge_max = NL.TOMB_REFERENCE["REN_RevealLedge"]
        s1 = steps(self.items, "S1")
        # S1 starts at the ledge front edge, first step within step height of ledge top
        self.assertEqual(s1[0]["min"][1], ledge_max[1])
        self.assertLessEqual(ledge_max[2] - s1[0]["max"][2], UE_MAX_STEP_HEIGHT)
        self.assertGreaterEqual(s1[0]["min"][0], ledge_min[0])
        self.assertLessEqual(s1[0]["max"][0], ledge_max[0])
        # S1 ends on the court
        court = self.L["REN_NEC_Court_Floor"]
        self.assertEqual(s1[-1]["max"][2], court["max"][2])
        self.assertEqual(s1[-1]["max"][1], court["min"][1])
        # S2: landing -> bridge head
        s2 = steps(self.items, "S2")
        landing = self.L["REN_NEC_Landing_S2_Floor"]
        bh = self.L["REN_NEC_BridgeHead_Floor"]
        self.assertEqual(s2[0]["max"][1], landing["min"][1])
        self.assertLessEqual(s2[0]["max"][2] - landing["max"][2], UE_MAX_STEP_HEIGHT)
        self.assertEqual(s2[-1]["max"][2], bh["max"][2])
        self.assertEqual(s2[-1]["min"][1], bh["max"][1])
        # Bridge head -> bridge deck -> plinth, all at ledge height
        deck = self.L["REN_NEC_Bridge_Deck"]
        plinth = self.L["REN_NEC_GatePlinth"]
        self.assertEqual(deck["min"][1], bh["max"][1])
        self.assertEqual(deck["max"][1], plinth["min"][1])
        for it in (bh, deck, plinth):
            self.assertEqual(it["max"][2], NL.Z_LEDGE)

    def test_bridge_axis_and_width(self):
        deck = self.L["REN_NEC_Bridge_Deck"]
        self.assertEqual(deck["min"][0] + deck["max"][0], 0, "bridge centred on the Gate axis x=0")
        self.assertEqual(deck["max"][0] - deck["min"][0], 400)
        self.assertGreaterEqual(deck["max"][1] - deck["min"][1], 1200, "long threshold approach")
        anubis = self.L["REN_NEC_Marker_Anubis"]
        x, y, z = anubis["loc"]
        self.assertTrue(deck["min"][0] < x < deck["max"][0] and deck["min"][1] < y < deck["max"][1])
        self.assertEqual(z, deck["max"][2])
        self.assertEqual(anubis["rot"]["yaw"], -90.0)

    def test_headroom_over_court(self):
        court_top = self.L["REN_NEC_Court_Floor"]["max"][2]
        for name in ("REN_NEC_BridgeHead_Floor", "REN_NEC_Bridge_Deck"):
            self.assertGreaterEqual(self.L[name]["min"][2] - court_top, MIN_HEADROOM, name)

    def test_court_width(self):
        c = self.L["REN_NEC_Court_Floor"]
        self.assertGreaterEqual(c["max"][0] - c["min"][0], 900)

    def test_glyph_gate_blocks_court_to_landing(self):
        """Wall + slab + end pillar must seal the court's +X edge and be unjumpable."""
        court = self.L["REN_NEC_Court_Floor"]
        parts = [self.L[n] for n in ("REN_NEC_GlyphWall", "REN_NEC_GlyphSeal_Slab", "REN_NEC_GlyphWall_End")]
        spans = sorted((p["min"][1], p["max"][1]) for p in parts)
        self.assertLessEqual(spans[0][0], court["min"][1])
        for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
            self.assertEqual(a1, b0, "gap in glyph wall")
        self.assertGreaterEqual(spans[-1][1], court["max"][1])
        for p in parts:
            self.assertGreater(p["max"][2] - court["max"][2], ASSUMED_JUMP_APEX_CM + 100)
        slab = self.L["REN_NEC_GlyphSeal_Slab"]
        self.assertEqual(slab["kind"], "movable")
        self.assertGreaterEqual(slab["sink_cm"], slab["max"][2] - slab["min"][2], "slab must sink fully")
        self.assertGreaterEqual(slab["max"][1] - slab["min"][1], 250, "opening wide enough to pass")
        # Corner walls stop parapet-walking around the slab
        for n in ("REN_NEC_Court_CornerWall", "REN_NEC_Landing_S2_CornerWall"):
            self.assertGreater(self.L[n]["max"][2] - (court["max"][2] + NL.PARAPET_H), ASSUMED_JUMP_APEX_CM)

    def test_ledge_jump_blocker(self):
        inv = self.L["REN_NEC_Ledge_InvisWall_Front"]
        self.assertEqual(inv["kind"], "invis")
        self.assertGreaterEqual(inv["max"][2], NL.Z_LEDGE + ASSUMED_JUMP_APEX_CM + CAPSULE_HEIGHT)

    def test_fall_recovery_below_route(self):
        fall = self.L["REN_NEC_Trigger_FallRecovery"]
        walk_min = min(it["min"][2] for it in self.items if it["label"].endswith("_Floor"))
        self.assertLess(fall["max"][2], walk_min)
        self.assertGreater(fall["min"][2], NL.Z_VOID_BOTTOM)

    def test_rotations_explicit(self):
        spot = self.L["REN_NEC_Light_ShadowTease"]
        self.assertEqual(set(spot["rot"]), {"roll", "pitch", "yaw"})
        self.assertEqual(spot["rot"]["yaw"], 90.0)   # shines +Y onto Tower A's -Y face


# ---------------------------------------------------------------------------
# Fake unreal for the builder
# ---------------------------------------------------------------------------

class _V:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = x, y, z


class _R:
    def __init__(self, roll=0.0, pitch=0.0, yaw=0.0):
        self.roll, self.pitch, self.yaw = roll, pitch, yaw


class _Comp:
    def __init__(self):
        self.props = {}

    def set_static_mesh(self, m):
        self.props["mesh"] = m

    def set_mobility(self, m):
        self.props["mobility"] = m

    def set_collision_profile_name(self, n):
        self.props["collision"] = n

    def set_box_extent(self, v):
        self.props["extent"] = (v.x, v.y, v.z)

    def set_editor_property(self, k, v):
        self.props[k] = v


class _FakeActor:
    def __init__(self, cls_name, loc, rot, label=None):
        self.cls_name, self.loc, self.rot = cls_name, loc, rot
        self.label = label or cls_name
        self.scale = None
        self.hidden = False
        self.folder = None
        self.comp = _Comp()

    def set_actor_label(self, l):
        self.label = l

    def get_actor_label(self):
        return self.label

    def set_actor_scale3d(self, v):
        self.scale = (v.x, v.y, v.z)

    def get_component_by_class(self, c):
        return self.comp

    def set_actor_hidden_in_game(self, h):
        self.hidden = h

    def set_folder_path(self, p):
        self.folder = p


class _World:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


def make_fake_unreal(project_dir, world_name, actors, log):
    u = types.ModuleType("unreal")
    u.Vector, u.Rotator = _V, _R

    class _Cls:
        def __init__(self, name):
            self.name = name

    for n in ("StaticMeshActor", "TriggerBox", "TargetPoint", "PointLight", "SpotLight",
              "StaticMeshComponent", "BoxComponent", "PointLightComponent", "SpotLightComponent"):
        setattr(u, n, _Cls(n))
    u.ComponentMobility = types.SimpleNamespace(MOVABLE="MOVABLE")

    class EditorActorSubsystem:
        def get_all_level_actors(self):
            return list(actors)

        def destroy_actor(self, a):
            log["destroyed"].append(a.label)
            actors.remove(a)

        def spawn_actor_from_class(self, cls, loc, rot):
            a = _FakeActor(cls.name, (loc.x, loc.y, loc.z), rot)
            actors.append(a)
            log["spawned"] += 1
            return a

    class LevelEditorSubsystem:
        def save_current_level(self):
            log["saves"] += 1

    class UnrealEditorSubsystem:
        def get_editor_world(self):
            return _World(world_name)

    class Paths:
        @staticmethod
        def project_dir():
            return project_dir + os.sep

    subs = {"EditorActorSubsystem": EditorActorSubsystem(), "LevelEditorSubsystem": LevelEditorSubsystem(),
            "UnrealEditorSubsystem": UnrealEditorSubsystem()}
    u.EditorActorSubsystem, u.LevelEditorSubsystem, u.UnrealEditorSubsystem = (
        EditorActorSubsystem, LevelEditorSubsystem, UnrealEditorSubsystem)
    u.get_editor_subsystem = lambda cls: subs[cls.__name__]
    u.Paths = Paths
    u.load_asset = lambda path: "CUBE" if path == "/Engine/BasicShapes/Cube.Cube" else None
    u.log = lambda m: log["info"].append(m)
    u.log_warning = lambda m: log["warn"].append(m)
    return u


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.project = tempfile.mkdtemp()
        self.log = {"destroyed": [], "spawned": 0, "saves": 0, "info": [], "warn": []}
        self.unrelated = _FakeActor("StaticMeshActor", (0, 0, 0), _R(), label="Floor")
        self.actors = [self.unrelated]
        self._saved = sys.modules.get("unreal")
        self.n_items = len(NL.build_layout())

    def tearDown(self):
        if self._saved is None:
            sys.modules.pop("unreal", None)
        else:
            sys.modules["unreal"] = self._saved
        shutil.rmtree(self.project)

    def _run(self, world="L_Necropolis_Blockout"):
        sys.modules["unreal"] = make_fake_unreal(self.project, world, self.actors, self.log)
        runpy.run_path(os.path.join(EDITOR_DIR, "REN_Necropolis_Greybox_Builder_v1.py"), run_name="__main__")

    def _nec(self):
        return [a for a in self.actors if a.label.startswith("REN_NEC_")]

    def test_wrong_world_refused(self):
        with self.assertRaises(RuntimeError):
            self._run(world="L_Tomb_Blockout")
        self.assertEqual(self.log["spawned"], 0)
        self.assertEqual(self.log["destroyed"], [])

    def test_tomb_actors_loaded_refused(self):
        self.actors.append(_FakeActor("StaticMeshActor", (0, 0, 0), _R(), label="REN_DistantGate"))
        with self.assertRaises(RuntimeError) as ctx:
            self._run()
        self.assertIn("non-REN_NEC_", str(ctx.exception))
        self.assertEqual(self.log["destroyed"], [])
        self.assertEqual(self.log["spawned"], 0)

    def test_hand_placed_interactables_tolerated_and_preserved(self):
        glyph = _FakeActor("BP_GlyphMechanism_C", (245, 4500, -400), _R(), label="REN_INT_NEC_Glyph")
        cam = _FakeActor("CameraActor", (-160, 4520, 170), _R(), label="REN_CAM_NEC_Anubis")
        self.actors += [glyph, cam]
        self._run()
        self._run()
        self.assertIn(glyph, self.actors)
        self.assertIn(cam, self.actors)
        self.assertNotIn("REN_INT_NEC_Glyph", self.log["destroyed"])

    def test_locked_baseline_refused(self):
        d = os.path.join(self.project, "ProjectDocs", "WorldLocks")
        os.makedirs(d)
        with open(os.path.join(d, "L_Necropolis_Blockout.worldlock.json"), "w") as f:
            f.write("{}")
        with self.assertRaises(RuntimeError):
            self._run()
        self.assertEqual(self.log["spawned"], 0)

    def test_build_and_rerun_safe(self):
        self._run()
        self.assertEqual(len(self._nec()), self.n_items)
        self.assertEqual(self.log["saves"], 1)
        self._run()
        self.assertEqual(len(self._nec()), self.n_items, "re-run must not duplicate")
        self.assertEqual(len(self.log["destroyed"]), self.n_items)
        self.assertTrue(all(l.startswith("REN_NEC_") for l in self.log["destroyed"]))
        self.assertIn(self.unrelated, self.actors, "non-REN actor must survive")
        labels = [a.label for a in self._nec()]
        self.assertEqual(len(labels), len(set(labels)))
        self.assertFalse(self.log["warn"])

    def test_spawned_properties(self):
        self._run()
        A = {a.label: a for a in self._nec()}
        slab = A["REN_NEC_GlyphSeal_Slab"]
        self.assertEqual(slab.comp.props["mobility"], "MOVABLE")
        self.assertTrue(A["REN_NEC_Ledge_InvisWall_Front"].hidden)
        self.assertEqual(A["REN_NEC_Dressing_BlackRiver"].comp.props["collision"], "NoCollision")
        trig = A["REN_NEC_Trigger_AnubisDialogue"]
        self.assertEqual(trig.comp.props["extent"], (200.0, 50.0, 150.0))
        self.assertIsNone(trig.scale)
        anubis = A["REN_NEC_Marker_Anubis"]
        self.assertEqual((anubis.rot.roll, anubis.rot.pitch, anubis.rot.yaw), (0.0, 0.0, -90.0))
        spot = A["REN_NEC_Light_ShadowTease"]
        self.assertEqual((spot.rot.roll, spot.rot.pitch, spot.rot.yaw), (0.0, -10.0, 90.0))
        deck = A["REN_NEC_Bridge_Deck"]
        self.assertEqual(deck.loc, (0.0, 4515.0, -20.0))
        self.assertEqual(deck.scale, (4.0, 12.7, 0.4))
        for proxy in NL.SKYLINE_PROXIES:
            self.assertNotIn(proxy, A)


if __name__ == "__main__":
    unittest.main()
