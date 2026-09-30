"""
REN — World Lock Core

Purpose: protect SPATIAL CONTINUITY. "Camera moves. World does not."

Pure-Python comparison logic shared by:
- Scripts/Editor/REN_Export_WorldLock.py    (runs inside Unreal Editor)
- Scripts/Editor/REN_Validate_WorldLock.py  (runs inside Unreal Editor)
- this file as a standalone CLI             (runs anywhere, incl. cloud/CI)

This module must NOT import `unreal`. It only reads/writes manifest dicts.

Two finding categories:

SPATIAL FAILURES (always fail validation):
- location / rotation / scale change beyond tolerance
- missing actor, unexpected new actor
- duplicate label (baseline or current)
- actor class change (structural replacement; review, then re-baseline)
- actor moved to a different level/sublevel (schema 3+)
- baseline/current map mismatch

ASSET CHANGES (warning by default; fail only in strict-assets mode):
- static mesh replaced at the same transform (e.g. greybox Cube -> final
  Egyptian architecture mesh). This is expected during the art pass and is
  NOT spatial drift.

CLI usage (offline review of two manifests, e.g. baseline vs candidate):

    python Scripts/Editor/REN_WorldLock_Core.py BASELINE.json CURRENT.json [--strict-assets] [--report OUT.json]

Exit codes: 0 = PASS (possibly with asset-change warnings),
            1 = REVIEW REQUIRED (spatial failure, or asset change in strict mode),
            2 = usage/input error.
"""

import json
import sys
from datetime import datetime, timezone

SCHEMA_VERSION = 3
DEFAULT_PREFIX = "REN_"

LOCATION_TOLERANCE_CM = 0.1
ROTATION_TOLERANCE_DEG = 0.1
SCALE_TOLERANCE = 0.0001


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def angle_delta_deg(a, b):
    """Smallest absolute difference between two angles, in degrees (0..180)."""
    d = (float(a) - float(b)) % 360.0
    return min(d, 360.0 - d)


def max_abs_diff(a, b):
    return max(abs(float(x) - float(y)) for x, y in zip(a, b))


def max_angle_diff(a, b):
    return max(angle_delta_deg(x, y) for x, y in zip(a, b))


def find_duplicate_labels(records):
    seen = {}
    for rec in records:
        seen[rec["label"]] = seen.get(rec["label"], 0) + 1
    return sorted(label for label, n in seen.items() if n > 1)


def build_manifest(records, world, map_path, prefix=DEFAULT_PREFIX, project="REN_TheTwelfthHour"):
    """Build a manifest from actor records (list of dicts)."""
    records = sorted(records, key=lambda r: r["label"])
    return {
        "schema": SCHEMA_VERSION,
        "project": project,
        "world": world,
        "map_path": map_path,
        "actor_prefix": prefix,
        "exported_utc": utc_now_iso(),
        "actor_count": len(records),
        "duplicate_labels": find_duplicate_labels(records),
        "actors": records,
    }


def compare_manifests(
    baseline,
    current,
    strict_assets=False,
    location_tol=LOCATION_TOLERANCE_CM,
    rotation_tol=ROTATION_TOLERANCE_DEG,
    scale_tol=SCALE_TOLERANCE,
):
    """
    Compare two manifests (schema 1, 2 or 3). Returns a report dict.

    report["passed"] is False on any spatial failure. Asset changes (mesh
    swaps at an unchanged transform) are reported in report["asset_changes"]
    and only fail when strict_assets=True.
    """
    base_actors = baseline.get("actors", [])
    cur_actors = current.get("actors", [])

    base_dupes = find_duplicate_labels(base_actors)
    cur_dupes = find_duplicate_labels(cur_actors)

    # Duplicates are reported separately; for pairing, first record wins.
    expected = {}
    for rec in base_actors:
        expected.setdefault(rec["label"], rec)
    actual = {}
    for rec in cur_actors:
        actual.setdefault(rec["label"], rec)

    map_issues = []
    b_world, c_world = baseline.get("world"), current.get("world")
    if b_world and c_world and b_world != c_world:
        map_issues.append(f"world name differs: baseline={b_world} current={c_world}")
    b_map, c_map = baseline.get("map_path"), current.get("map_path")
    if b_map and c_map and b_map != c_map:
        map_issues.append(f"map path differs: baseline={b_map} current={c_map}")

    missing = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    changed = []        # spatial / structural failures
    asset_changes = []  # mesh swaps at the same transform

    for label in sorted(set(expected) & set(actual)):
        e, c = expected[label], actual[label]

        loc_diff = max_abs_diff(e["location_cm"], c["location_cm"])
        rot_diff = max_angle_diff(e["rotation_deg"], c["rotation_deg"])
        scale_diff = max_abs_diff(e["scale"], c["scale"])
        class_changed = e.get("class") != c.get("class")
        # Level ownership is only compared when both sides recorded it (schema 3+).
        level_changed = (
            e.get("level") is not None and c.get("level") is not None and e["level"] != c["level"]
        )
        # Mesh is only compared when both sides recorded it (schema 2+).
        mesh_changed = (
            "static_mesh" in e and "static_mesh" in c and e["static_mesh"] != c["static_mesh"]
        )

        spatial = (
            loc_diff > location_tol
            or rot_diff > rotation_tol
            or scale_diff > scale_tol
        )

        if spatial or class_changed or level_changed:
            item = {
                "label": label,
                "location_max_diff_cm": round(loc_diff, 4),
                "rotation_max_diff_deg": round(rot_diff, 4),
                "scale_max_diff": round(scale_diff, 6),
                "class_changed": class_changed,
                "level_changed": level_changed,
            }
            if class_changed:
                item["class"] = [e.get("class"), c.get("class")]
            if level_changed:
                item["level"] = [e.get("level"), c.get("level")]
            changed.append(item)

        if mesh_changed:
            asset_changes.append({
                "label": label,
                "static_mesh": [e.get("static_mesh"), c.get("static_mesh")],
                "transform_unchanged": not spatial,
            })

    spatial_passed = not (missing or added or changed or base_dupes or cur_dupes or map_issues)
    passed = spatial_passed and not (strict_assets and asset_changes)

    return {
        "schema": SCHEMA_VERSION,
        "generated_utc": utc_now_iso(),
        "world": c_world or b_world,
        "map_path": c_map or b_map,
        "baseline_schema": baseline.get("schema"),
        "baseline_exported_utc": baseline.get("exported_utc"),
        "strict_assets": bool(strict_assets),
        "tolerances": {
            "location_cm": location_tol,
            "rotation_deg": rotation_tol,
            "scale": scale_tol,
        },
        "expected_count": len(base_actors),
        "current_count": len(cur_actors),
        "map_issues": map_issues,
        "duplicate_labels_baseline": base_dupes,
        "duplicate_labels_current": cur_dupes,
        "missing": missing,
        "added": added,
        "changed": changed,
        "asset_changes": asset_changes,
        "spatial_passed": spatial_passed,
        "passed": passed,
    }


def format_report(report):
    """Return (info_lines, warning_lines, result_line) for logging."""
    info = [
        "===========================================================",
        "REN WORLD LOCK VALIDATION",
        f"World: {report['world']}",
        f"Map: {report['map_path']}",
        f"Mode: {'STRICT ASSETS' if report.get('strict_assets') else 'default (mesh swaps = warning)'}",
        f"Expected actors: {report['expected_count']}",
        f"Current actors: {report['current_count']}",
        f"Missing: {len(report['missing'])}",
        f"Added: {len(report['added'])}",
        f"Spatial/structural changes: {len(report['changed'])}",
        f"Asset changes (mesh swaps): {len(report['asset_changes'])}",
        f"Duplicate labels (baseline/current): "
        f"{len(report['duplicate_labels_baseline'])}/{len(report['duplicate_labels_current'])}",
    ]
    warn = []
    for msg in report["map_issues"]:
        warn.append(f"MAP MISMATCH: {msg}")
    for label in report["duplicate_labels_baseline"]:
        warn.append(f"DUPLICATE IN BASELINE: {label}")
    for label in report["duplicate_labels_current"]:
        warn.append(f"DUPLICATE IN LEVEL: {label}")
    for label in report["missing"]:
        warn.append(f"MISSING: {label}")
    for label in report["added"]:
        warn.append(f"ADDED: {label}")
    for item in report["changed"]:
        line = (
            f"CHANGED: {item['label']}"
            f" | loc={item['location_max_diff_cm']}cm"
            f" rot={item['rotation_max_diff_deg']}deg"
            f" scale={item['scale_max_diff']}"
        )
        if item["class_changed"]:
            line += f" class={item['class'][0]}->{item['class'][1]}"
        if item["level_changed"]:
            line += f" level={item['level'][0]}->{item['level'][1]}"
        warn.append(line)
    for item in report["asset_changes"]:
        tag = "ASSET CHANGE (strict: FAIL)" if report.get("strict_assets") else "ASSET CHANGE (review)"
        warn.append(
            f"{tag}: {item['label']} | mesh={item['static_mesh'][0]}->{item['static_mesh'][1]}"
            + ("" if item["transform_unchanged"] else " | transform ALSO changed (see CHANGED)")
        )

    if report["passed"] and not report["asset_changes"]:
        result = "RESULT: PASS — no unexplained REN spatial drift detected."
    elif report["passed"]:
        result = "RESULT: PASS WITH ASSET CHANGES — transforms intact; review mesh swaps."
    elif report["spatial_passed"]:
        result = "RESULT: REVIEW REQUIRED — asset changes in strict-assets mode."
    else:
        result = "RESULT: REVIEW REQUIRED — spatial/structural world-lock differences detected."
    return info, warn, result


def _main(argv):
    args = list(argv[1:])
    report_path = None
    strict_assets = False
    if "--strict-assets" in args:
        strict_assets = True
        args.remove("--strict-assets")
    if "--report" in args:
        i = args.index("--report")
        if i + 1 >= len(args):
            print("error: --report needs a path", file=sys.stderr)
            return 2
        report_path = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    try:
        with open(args[0], encoding="utf-8") as f:
            baseline = json.load(f)
        with open(args[1], encoding="utf-8") as f:
            current = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = compare_manifests(baseline, current, strict_assets=strict_assets)
    info, warn, result = format_report(report)
    for line in info:
        print(line)
    for line in warn:
        print(line)
    print(result)

    if report_path:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report: {report_path}")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
