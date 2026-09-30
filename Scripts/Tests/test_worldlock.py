"""
Offline tests for REN world-lock tooling.

Run from the repo root:
    python -m unittest discover -s Scripts/Tests -v

These tests exercise the pure-Python comparison logic and run the two Unreal
editor scripts against a minimal FAKE `unreal` module. They prove script logic
and file handling only; real Unreal API behaviour is LOCAL_VALIDATION_REQUIRED.
"""

import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EDITOR_DIR = os.path.join(REPO, "Scripts", "Editor")
sys.path.insert(0, EDITOR_DIR)

import REN_WorldLock_Core as core  # noqa: E402


def rec(label, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), cls="StaticMeshActor", mesh=None,
        level=None):
    r = {
        "label": label,
        "class": cls,
        "location_cm": list(loc),
        "rotation_deg": list(rot),
        "scale": list(scale),
    }
    if mesh is not None:
        r["static_mesh"] = mesh
    if level is not None:
        r["level"] = level
    return r


def manifest(records, world="L_Test", map_path="/Game/Test/L_Test"):
    return core.build_manifest(records, world=world, map_path=map_path)


class AngleTests(unittest.TestCase):
    def test_wraparound(self):
        self.assertAlmostEqual(core.angle_delta_deg(179.95, -179.95), 0.1, places=6)
        self.assertAlmostEqual(core.angle_delta_deg(180, -180), 0.0)
        self.assertAlmostEqual(core.angle_delta_deg(0, 360), 0.0)
        self.assertAlmostEqual(core.angle_delta_deg(10, 350), 20.0)
        self.assertAlmostEqual(core.angle_delta_deg(0, 180), 180.0)


class CompareTests(unittest.TestCase):
    def test_identical_passes(self):
        m = manifest([rec("REN_A"), rec("REN_B", loc=(1, 2, 3))])
        r = core.compare_manifests(m, m)
        self.assertTrue(r["passed"])
        self.assertEqual(r["changed"], [])

    def test_within_tolerance_passes(self):
        b = manifest([rec("REN_A", loc=(100, 0, 0), rot=(0, 0, 90))])
        c = manifest([rec("REN_A", loc=(100.05, 0, 0), rot=(0, 0, 90.05))])
        self.assertTrue(core.compare_manifests(b, c)["passed"])

    def test_yaw_wrap_is_not_drift(self):
        b = manifest([rec("REN_A", rot=(0, 0, 180.0))])
        c = manifest([rec("REN_A", rot=(0, 0, -180.0))])
        self.assertTrue(core.compare_manifests(b, c)["passed"])

    def test_moved_actor_flagged(self):
        b = manifest([rec("REN_Door", loc=(0, 2015, 155))])
        c = manifest([rec("REN_Door", loc=(0, 2015, 170))])
        r = core.compare_manifests(b, c)
        self.assertFalse(r["passed"])
        self.assertEqual(r["changed"][0]["label"], "REN_Door")
        self.assertEqual(r["changed"][0]["location_max_diff_cm"], 15.0)

    def test_missing_and_added(self):
        b = manifest([rec("REN_A"), rec("REN_B")])
        c = manifest([rec("REN_A"), rec("REN_C")])
        r = core.compare_manifests(b, c)
        self.assertEqual(r["missing"], ["REN_B"])
        self.assertEqual(r["added"], ["REN_C"])
        self.assertFalse(r["passed"])

    def test_duplicates_fail(self):
        b = manifest([rec("REN_A")])
        c = manifest([rec("REN_A"), rec("REN_A", loc=(5, 5, 5))])
        r = core.compare_manifests(b, c)
        self.assertEqual(r["duplicate_labels_current"], ["REN_A"])
        self.assertFalse(r["passed"])
        self.assertEqual(c["duplicate_labels"], ["REN_A"])

    def test_class_change_fails(self):
        b = manifest([rec("REN_A", mesh="/Engine/BasicShapes/Cube.Cube")])
        c = manifest([rec("REN_A", cls="BP_ExitDoor_C", mesh="/Engine/BasicShapes/Cube.Cube")])
        r = core.compare_manifests(b, c)
        self.assertFalse(r["passed"])
        self.assertTrue(r["changed"][0]["class_changed"])
        self.assertEqual(r["asset_changes"], [])

    def test_mesh_swap_same_transform_is_warning_not_failure(self):
        """Art pass: Cube -> final mesh at identical transform must NOT be spatial drift."""
        b = manifest([rec("REN_Pillar", loc=(95, 860, 140), mesh="/Engine/BasicShapes/Cube.Cube")])
        c = manifest([rec("REN_Pillar", loc=(95, 860, 140), mesh="/Game/REN/Art/Architecture/SM_Pillar.SM_Pillar")])
        r = core.compare_manifests(b, c)
        self.assertTrue(r["passed"])
        self.assertTrue(r["spatial_passed"])
        self.assertEqual(r["changed"], [])
        self.assertEqual(len(r["asset_changes"]), 1)
        self.assertTrue(r["asset_changes"][0]["transform_unchanged"])
        _, warn, result = core.format_report(r)
        self.assertIn("PASS WITH ASSET CHANGES", result)
        self.assertTrue(any(w.startswith("ASSET CHANGE (review)") for w in warn))

    def test_mesh_swap_fails_in_strict_assets_mode(self):
        b = manifest([rec("REN_Pillar", mesh="/Engine/BasicShapes/Cube.Cube")])
        c = manifest([rec("REN_Pillar", mesh="/Game/REN/Art/SM_Pillar.SM_Pillar")])
        r = core.compare_manifests(b, c, strict_assets=True)
        self.assertFalse(r["passed"])
        self.assertTrue(r["spatial_passed"])
        self.assertIn("strict-assets", core.format_report(r)[2])

    def test_mesh_swap_does_not_mask_transform_change(self):
        """Replacing the mesh must never excuse a moved actor."""
        b = manifest([rec("REN_Door", loc=(0, 2015, 155), mesh="/Engine/BasicShapes/Cube.Cube")])
        c = manifest([rec("REN_Door", loc=(0, 2015, 160), mesh="/Game/REN/Art/SM_Door.SM_Door")])
        r = core.compare_manifests(b, c)
        self.assertFalse(r["passed"])
        self.assertEqual(r["changed"][0]["label"], "REN_Door")
        self.assertFalse(r["asset_changes"][0]["transform_unchanged"])

    def test_rotation_and_scale_changes_fail(self):
        b = manifest([rec("REN_A", rot=(0, 0, 90), scale=(1, 1, 1))])
        self.assertFalse(core.compare_manifests(b, manifest([rec("REN_A", rot=(0, 90, 0), scale=(1, 1, 1))]))["passed"])
        self.assertFalse(core.compare_manifests(b, manifest([rec("REN_A", rot=(0, 0, 90), scale=(1, 1, 1.01))]))["passed"])

    def test_level_ownership_change_fails(self):
        b = manifest([rec("REN_DistantGate", level="/Game/REN/Worlds/Tomb/L_Tomb_Blockout")])
        c = manifest([rec("REN_DistantGate", level="/Game/REN/Worlds/GateWest/L_GateWest_Blockout")])
        r = core.compare_manifests(b, c)
        self.assertFalse(r["passed"])
        self.assertTrue(r["changed"][0]["level_changed"])

    def test_level_ignored_when_baseline_lacks_it(self):
        b = manifest([rec("REN_A")])
        c = manifest([rec("REN_A", level="/Game/X/L_X")])
        self.assertTrue(core.compare_manifests(b, c)["passed"])

    def test_mesh_ignored_when_baseline_lacks_it(self):
        b = manifest([rec("REN_A")])
        c = manifest([rec("REN_A", mesh="/Engine/BasicShapes/Cube.Cube")])
        self.assertTrue(core.compare_manifests(b, c)["passed"])

    def test_map_mismatch_fails(self):
        b = manifest([rec("REN_A")], map_path="/Game/REN/Worlds/Tomb/L_Tomb_Blockout")
        c = manifest([rec("REN_A")], map_path="/Game/Other/L_Tomb_Blockout")
        r = core.compare_manifests(b, c)
        self.assertFalse(r["passed"])
        self.assertEqual(len(r["map_issues"]), 1)

    def test_schema1_baseline_readable(self):
        schema1 = {
            "schema": 1,
            "world": "L_Test",
            "actors": [rec("REN_A", loc=(1, 1, 1))],
        }
        r = core.compare_manifests(schema1, manifest([rec("REN_A", loc=(1, 1, 1), mesh="/x")]))
        self.assertTrue(r["passed"])

    def test_format_report(self):
        b = manifest([rec("REN_A")])
        c = manifest([rec("REN_A", loc=(9, 0, 0))])
        info, warn, result = core.format_report(core.compare_manifests(b, c))
        self.assertTrue(any(w.startswith("CHANGED: REN_A") for w in warn))
        self.assertIn("REVIEW REQUIRED", result)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _write(self, name, data):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, os.path.join(EDITOR_DIR, "REN_WorldLock_Core.py"), *args],
            capture_output=True, text=True,
        )

    def test_exit_codes(self):
        a = self._write("a.json", manifest([rec("REN_A")]))
        b = self._write("b.json", manifest([rec("REN_A", loc=(50, 0, 0))]))
        self.assertEqual(self._run(a, a).returncode, 0)
        report = os.path.join(self.tmp, "r.json")
        p = self._run(a, b, "--report", report)
        self.assertEqual(p.returncode, 1)
        with open(report, encoding="utf-8") as f:
            self.assertFalse(json.load(f)["passed"])
        self.assertEqual(self._run(a).returncode, 2)
        self.assertEqual(self._run(a, os.path.join(self.tmp, "nope.json")).returncode, 2)

    def test_strict_assets_flag(self):
        a = self._write("a.json", manifest([rec("REN_A", mesh="/Engine/BasicShapes/Cube.Cube")]))
        b = self._write("b.json", manifest([rec("REN_A", mesh="/Game/REN/Art/SM_A.SM_A")]))
        self.assertEqual(self._run(a, b).returncode, 0)
        self.assertEqual(self._run(a, b, "--strict-assets").returncode, 1)


# ---------------------------------------------------------------------------
# Fake `unreal` module — just enough surface for the export/validate scripts.
# ---------------------------------------------------------------------------

class _Vec:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class _Rot:
    def __init__(self, roll, pitch, yaw):
        self.roll, self.pitch, self.yaw = roll, pitch, yaw


class _Named:
    def __init__(self, name, path=None):
        self._name, self._path = name, path or name

    def get_name(self):
        return self._name

    def get_path_name(self):
        return self._path


class _MeshComp:
    def __init__(self, mesh_path):
        self._mesh = _Named(mesh_path.split(".")[-1], mesh_path) if mesh_path else None

    def get_editor_property(self, name):
        assert name == "static_mesh"
        return self._mesh


class _Actor:
    def __init__(self, label, loc, rot=(0, 0, 0), scale=(1, 1, 1), cls="StaticMeshActor", mesh=None):
        self.label, self.loc, self.rot, self.scale, self.cls = label, loc, rot, scale, cls
        self.mesh_comp = _MeshComp(mesh) if cls == "StaticMeshActor" else None

    def get_actor_label(self):
        return self.label

    def get_actor_location(self):
        return _Vec(*self.loc)

    def get_actor_rotation(self):
        return _Rot(*self.rot)

    def get_actor_scale3d(self):
        return _Vec(*self.scale)

    def get_class(self):
        return _Named(self.cls)

    def get_component_by_class(self, klass):
        return self.mesh_comp

    def get_actor_bounds(self, only_colliding):
        ext = getattr(self, "bounds_extent", (50, 50, 50))
        return _Vec(*self.loc), _Vec(*ext)

    def get_level(self):
        level = _Named("PersistentLevel", "/Game/REN/Worlds/Tomb/L_Tomb_Blockout.L_Tomb_Blockout:PersistentLevel")
        level.get_outer = lambda: _Named("L_Tomb_Blockout", "/Game/REN/Worlds/Tomb/L_Tomb_Blockout.L_Tomb_Blockout")
        return level


def make_fake_unreal(project_dir, actors, logs, world_name="L_Tomb_Blockout"):
    u = types.ModuleType("unreal")

    class EditorActorSubsystem:
        def get_all_level_actors(self):
            return list(actors)

        def destroy_actor(self, actor):
            logs.append(("destroy", actor.label))
            actors.remove(actor)

    class UnrealEditorSubsystem:
        def get_editor_world(self):
            return _Named(world_name, f"/Game/REN/Worlds/Tomb/{world_name}.{world_name}")

    class StaticMeshComponent:
        pass

    class Paths:
        @staticmethod
        def project_dir():
            return project_dir + os.sep

    u.EditorActorSubsystem = EditorActorSubsystem
    u.UnrealEditorSubsystem = UnrealEditorSubsystem
    u.StaticMeshComponent = StaticMeshComponent
    u.Paths = Paths
    u.get_editor_subsystem = lambda cls: cls()
    u.log = lambda msg: logs.append(("info", msg))
    u.log_warning = lambda msg: logs.append(("warn", msg))
    return u


CUBE = "/Engine/BasicShapes/Cube.Cube"


class EditorScriptSmokeTests(unittest.TestCase):
    def setUp(self):
        self.project = tempfile.mkdtemp()
        self.logs = []
        self.actors = [
            _Actor("REN_ExitDoor", (0, 2015, 155), scale=(2.75, 0.3, 3.1), mesh=CUBE),
            _Actor("REN_PlayerStart", (0, -350, 110), rot=(0, 0, 90), cls="PlayerStart"),
            _Actor("Floor", (0, 0, 0), mesh=CUBE),  # non-REN: must be ignored
        ]
        self._saved = sys.modules.get("unreal")
        sys.modules["unreal"] = make_fake_unreal(self.project, self.actors, self.logs)
        self.lock_dir = os.path.join(self.project, "ProjectDocs", "WorldLocks")

    def tearDown(self):
        if self._saved is None:
            sys.modules.pop("unreal", None)
        else:
            sys.modules["unreal"] = self._saved
        shutil.rmtree(self.project)

    def _run(self, name):
        runpy.run_path(os.path.join(EDITOR_DIR, name), run_name="__main__")

    def _load(self, *parts):
        with open(os.path.join(self.lock_dir, *parts), encoding="utf-8") as f:
            return json.load(f)

    def test_export_then_validate_pass(self):
        self._run("REN_Export_WorldLock.py")
        base = self._load("L_Tomb_Blockout.worldlock.json")
        self.assertEqual(base["schema"], 3)
        self.assertEqual(base["actors"][0]["level"], "/Game/REN/Worlds/Tomb/L_Tomb_Blockout")
        self.assertEqual(base["map_path"], "/Game/REN/Worlds/Tomb/L_Tomb_Blockout")
        self.assertEqual(base["actor_count"], 2)
        labels = [a["label"] for a in base["actors"]]
        self.assertEqual(labels, ["REN_ExitDoor", "REN_PlayerStart"])
        self.assertEqual(base["actors"][0]["static_mesh"], CUBE)
        self.assertNotIn("static_mesh", base["actors"][1])

        self._run("REN_Validate_WorldLock.py")
        report = self._load("Reports", "L_Tomb_Blockout.validation.json")
        self.assertTrue(report["passed"])

    def test_second_export_writes_candidate_not_baseline(self):
        self._run("REN_Export_WorldLock.py")
        before = self._load("L_Tomb_Blockout.worldlock.json")
        self.actors[0].loc = (0, 2015, 300)
        self._run("REN_Export_WorldLock.py")
        after = self._load("L_Tomb_Blockout.worldlock.json")
        self.assertEqual(before["actors"], after["actors"])
        cand = self._load("L_Tomb_Blockout.worldlock.candidate.json")
        self.assertEqual(cand["actors"][0]["location_cm"], [0, 2015, 300])

    def test_validate_detects_drift_and_duplicates(self):
        self._run("REN_Export_WorldLock.py")
        self.actors[0].loc = (0, 2015, 170)
        self.actors.append(_Actor("REN_ExitDoor", (0, 0, 0), mesh=CUBE))
        self._run("REN_Validate_WorldLock.py")
        report = self._load("Reports", "L_Tomb_Blockout.validation.json")
        self.assertFalse(report["passed"])
        self.assertEqual(report["duplicate_labels_current"], ["REN_ExitDoor"])
        self.assertTrue(any("REVIEW REQUIRED" in m for _, m in self.logs))

    def test_validate_without_baseline_raises(self):
        with self.assertRaises(RuntimeError):
            self._run("REN_Validate_WorldLock.py")


class BuilderGuardTests(unittest.TestCase):
    """Builder v3 must refuse to run (before deleting anything) in unsafe situations."""

    def setUp(self):
        self.project = tempfile.mkdtemp()
        self.logs = []
        self.actors = [_Actor("REN_INT_ExitDoor", (0, 0, 0), cls="Actor")]
        self._saved = sys.modules.get("unreal")

    def tearDown(self):
        if self._saved is None:
            sys.modules.pop("unreal", None)
        else:
            sys.modules["unreal"] = self._saved
        shutil.rmtree(self.project)

    def _run_builder(self, world_name):
        sys.modules["unreal"] = make_fake_unreal(self.project, self.actors, self.logs, world_name)
        path = os.path.join(EDITOR_DIR, "REN_Tomb_Opening_Greybox_Builder_v3.py")
        with self.assertRaises(RuntimeError) as ctx:
            runpy.run_path(path, run_name="__main__")
        self.assertEqual(len(self.actors), 1, "builder deleted actors despite guard")
        self.assertFalse(any(kind == "destroy" for kind, _ in self.logs))
        return str(ctx.exception)

    def test_refuses_wrong_world(self):
        msg = self._run_builder("L_REN_Slice")
        self.assertIn("opened standalone", msg)

    def test_refuses_when_baseline_exists(self):
        lock = os.path.join(self.project, "ProjectDocs", "WorldLocks")
        os.makedirs(lock)
        with open(os.path.join(lock, "L_Tomb_Blockout.worldlock.json"), "w") as f:
            f.write("{}")
        msg = self._run_builder("L_Tomb_Blockout")
        self.assertIn("layout is locked", msg)


class OrientationCheckTests(unittest.TestCase):
    """REN_Inspect_TombOrientation.py: read-only verdicts for the suspected v3 rotator bugs."""

    def setUp(self):
        self.project = tempfile.mkdtemp()
        self.logs = []
        self._saved = sys.modules.get("unreal")

    def tearDown(self):
        if self._saved is None:
            sys.modules.pop("unreal", None)
        else:
            sys.modules["unreal"] = self._saved
        shutil.rmtree(self.project)

    def _run(self, ps_rot, relief_rot, relief_extent, world="L_Tomb_Blockout"):
        ps = _Actor("REN_PlayerStart", (0, -350, 110), rot=ps_rot, cls="PlayerStart")
        rel = _Actor("REN_BlankCartouche_Relief", (370, 110, 225), rot=relief_rot,
                     scale=(0.08, 0.72, 1.45), mesh="/Engine/BasicShapes/Cylinder.Cylinder")
        rel.bounds_extent = relief_extent
        actors = [ps, rel]
        before = [(a.label, a.loc, a.rot, a.scale) for a in actors]
        sys.modules["unreal"] = make_fake_unreal(self.project, actors, self.logs, world)
        runpy.run_path(os.path.join(EDITOR_DIR, "REN_Inspect_TombOrientation.py"), run_name="__main__")
        self.assertEqual(before, [(a.label, a.loc, a.rot, a.scale) for a in actors], "inspection mutated actors")
        path = os.path.join(self.project, "ProjectDocs", "WorldLocks", "Reports",
                            "L_Tomb_Blockout.orientation_check.json")
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_predicted_builder_bug_is_reported_wrong(self):
        # Hypothesis from code reading: PlayerStart pitch 90; relief rolled 90 -> horizontal.
        rep = self._run(ps_rot=(0, 90, 0), relief_rot=(90, 0, 0), relief_extent=(4, 72.5, 36))
        self.assertEqual(rep["results"]["REN_PlayerStart"]["verdict"], "WRONG")
        self.assertEqual(rep["results"]["REN_BlankCartouche_Relief"]["verdict"], "WRONG_HORIZONTAL")
        self.assertFalse(rep["all_ok"])

    def test_correct_transforms_pass(self):
        rep = self._run(ps_rot=(0, 0, 90), relief_rot=(0, 0, 0), relief_extent=(4, 36, 72.5))
        self.assertTrue(rep["all_ok"])

    def test_yaw_wrap_accepted(self):
        rep = self._run(ps_rot=(0, 0, -270), relief_rot=(0, 0, 0), relief_extent=(4, 36, 72.5))
        self.assertEqual(rep["results"]["REN_PlayerStart"]["verdict"], "OK")

    def test_wrong_world_refused(self):
        with self.assertRaises(RuntimeError):
            self._run((0, 0, 90), (0, 0, 0), (4, 36, 72.5), world="L_REN_Slice")


class BuilderLabelTests(unittest.TestCase):
    """Static checks on the v3 builder: every generated label is REN_ and unique."""

    def test_builder_labels_unique_and_prefixed(self):
        path = os.path.join(EDITOR_DIR, "REN_Tomb_Opening_Greybox_Builder_v3.py")
        with open(path, encoding="utf-8") as f:
            src = f.read()
        labels = re.findall(r'(?:cube|cylinder|point_light|spot_light|trigger_box)\(\s*"([^"]+)"', src)
        labels += re.findall(r'set_actor_label\("([^"]+)"\)', src)
        self.assertEqual(len(labels), 58)
        self.assertEqual(len(labels), len(set(labels)), "duplicate builder labels")
        self.assertTrue(all(l.startswith("REN_") for l in labels))


if __name__ == "__main__":
    unittest.main()
