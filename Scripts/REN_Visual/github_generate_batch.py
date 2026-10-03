#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

def find_root() -> Path:
    p = Path.cwd().resolve()
    for root in [p, *p.parents]:
        if (root / "ProjectDocs" / "References" / "GENERATION_JOBS.jsonl").exists():
            return root
    raise SystemExit("Could not find REN repository root.")

ROOT = find_root()
REFS = ROOT / "ProjectDocs" / "References"
JOBS = REFS / "GENERATION_JOBS.jsonl"

def load_jobs():
    out = {}
    for line in JOBS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            j = json.loads(line)
            out[j["id"]] = j
    return out

def snapshot_for(expected_rel: str):
    p = REFS / expected_rel
    parent = p.parent
    parent.mkdir(parents=True, exist_ok=True)
    return {x.resolve() for x in parent.glob(p.stem.split("_v")[0] + "*") if x.is_file()}

def run(cmd):
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run([str(x) for x in cmd], cwd=ROOT, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-ids", required=True, help="Comma-separated job ids")
    ap.add_argument("--quality", default="high")
    args = ap.parse_args()

    jobs = load_jobs()
    ids = [x.strip() for x in args.job_ids.split(",") if x.strip()]
    if not ids:
        raise SystemExit("No job ids supplied.")
    if len(ids) > 8:
        raise SystemExit("Safety limit: maximum 8 generated images per workflow run.")

    report = []
    for job_id in ids:
        if job_id not in jobs:
            raise SystemExit(f"Unknown generation job: {job_id}")
        job = jobs[job_id]
        expected_rel = job["expected_file"]
        expected_path = REFS / expected_rel
        before = {x.resolve() for x in expected_path.parent.iterdir() if x.is_file()} if expected_path.parent.exists() else set()

        run([
            sys.executable,
            "Scripts/REN_Visual/openai_image_generate.py",
            "--job-id", job_id,
            "--quality", args.quality,
        ])

        after = {x.resolve() for x in expected_path.parent.iterdir() if x.is_file()}
        new_files = sorted(after - before, key=lambda p: p.stat().st_mtime_ns)

        pngs = [p for p in new_files if p.suffix.lower() == ".png"]
        if not pngs:
            raise SystemExit(f"No new PNG detected for {job_id}.")
        candidate = pngs[-1]
        rel = candidate.relative_to(REFS).as_posix()

        run([
            sys.executable,
            "Scripts/REN_Visual/ren_visual.py",
            "record", job_id,
            "--file", rel,
            "--status", "NEEDS_REVIEW",
        ])

        report.append({
            "job_id": job_id,
            "file": rel,
            "status": "NEEDS_REVIEW",
        })

    out = ROOT / "ProjectDocs" / "References" / "LAST_GITHUB_GENERATION.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\nGenerated candidates:")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
