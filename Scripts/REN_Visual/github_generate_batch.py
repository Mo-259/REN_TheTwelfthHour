#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

# Hard cost-safety rule: at most this many image API requests per workflow run.
# Each requested job is attempted exactly once; there are NO automatic retries
# inside the runner (a refused/failed job gets at most one later targeted retry,
# requested manually after review).
MAX_REQUESTS_PER_RUN = 8

def find_root() -> Path:
    p = Path.cwd().resolve()
    for root in [p, *p.parents]:
        if (root / "ProjectDocs" / "References" / "GENERATION_JOBS.jsonl").exists():
            return root
    raise SystemExit("Could not find REN repository root.")

ROOT = find_root()
REFS = ROOT / "ProjectDocs" / "References"
JOBS = REFS / "GENERATION_JOBS.jsonl"
REPORT = REFS / "LAST_GITHUB_GENERATION.json"

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

def run_captured(cmd):
    """Run a child process, echo only its stdout, keep stderr private.

    stderr may contain raw API error payloads (request ids, full messages);
    it is parsed into a short sanitized reason and never printed.
    """
    print("+", " ".join(str(x) for x in cmd), flush=True)
    proc = subprocess.run([str(x) for x in cmd], cwd=ROOT, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n", flush=True)
    return proc

# Messages raised deliberately by openai_image_generate.py; safe to surface verbatim.
SAFE_GENERATOR_MESSAGES = (
    "Image API returned no image data.",
    "Image API response did not contain b64_json.",
    "OPENAI_API_KEY is missing",
    "Python package 'openai' is missing",
    "Job not found",
    "IDENTITY FAIL-CLOSED",
    "CONTINUITY FAIL-CLOSED",
)

def sanitize_failure(stderr: str, returncode: int):
    """Return (short_reason, charged) without exposing raw API responses."""
    text = stderr or ""
    if "moderation_blocked" in text or "rejected by the safety system" in text:
        stage_m = re.search(r"'moderation_stage':\s*'(\w+)'", text)
        cats_m = re.search(r"'categories':\s*\[([^\]]*)\]", text)
        stage = stage_m.group(1) if stage_m else "unknown"
        cats = ",".join(re.findall(r"'([\w\-/]+)'", cats_m.group(1))) if cats_m else "unspecified"
        if stage == "input":
            charged = "unknown (refused at input moderation; likely not charged)"
        elif stage == "output":
            charged = "unknown (refused at output moderation, after generation; billing not determinable from the response)"
        else:
            charged = "unknown"
        return f"REFUSED by image safety system (stage={stage}, categories={cats})", charged
    code_m = re.search(r"Error code: (\d{3})", text)
    if code_m:
        err_code = re.search(r"'code':\s*'([\w\-]+)'", text)
        reason = f"API error HTTP {code_m.group(1)}" + (f" ({err_code.group(1)})" if err_code else "")
        return reason, "unknown"
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in reversed(lines):
        for msg in SAFE_GENERATOR_MESSAGES:
            if line.startswith(msg):
                return line[:160], "unknown"
    exc = re.findall(r"^((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*(?:Error|Exception|Timeout))\b", text, re.M)
    if exc:
        return f"{exc[-1]} (details withheld)", "unknown"
    return f"generator failed (exit {returncode}, details withheld)", "unknown"

def png_dimensions(path: Path):
    try:
        with path.open("rb") as f:
            head = f.read(24)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", head[16:24])
            return f"{w}x{h}"
    except OSError:
        pass
    return "unknown"

def write_report(meta, success, failed, not_run):
    payload = {
        "schema": 2,
        **meta,
        "success": success,
        "failed": failed,
        "not_run": not_run,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def format_summary(success, failed, not_run):
    out = ["SUCCESS:"]
    out += [f"- {s['job_id']} | {s['file']} | {s['dimensions']} | {s['status']}" for s in success] or ["- (none)"]
    out.append("FAILED:")
    out += [f"- {f['job_id']} | {f['reason']} | charged: {f['charged']}" for f in failed] or ["- (none)"]
    out.append("NOT_RUN:")
    out += [f"- {j}" for j in not_run] or ["- (none)"]
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-ids", required=True, help="Comma-separated job ids")
    ap.add_argument("--quality", default="high")
    args = ap.parse_args()

    # --- Preflight (infrastructure/config errors fail the whole batch BEFORE any paid request) ---
    try:
        jobs = load_jobs()
    except (OSError, ValueError, KeyError) as e:
        raise SystemExit(f"Generation queue unreadable/corrupt: {type(e).__name__}")
    ids = []
    for x in args.job_ids.split(","):
        x = x.strip()
        if x and x not in ids:          # de-duplicate: never pay twice for one job in one run
            ids.append(x)
    if not ids:
        raise SystemExit("No job ids supplied.")
    if len(ids) > MAX_REQUESTS_PER_RUN:
        raise SystemExit(f"Safety limit: maximum {MAX_REQUESTS_PER_RUN} image API requests per workflow run.")
    unknown = [j for j in ids if j not in jobs]
    if unknown:
        raise SystemExit(f"Unknown generation job(s): {', '.join(unknown)}")

    meta = {"quality": args.quality, "requested": ids,
            "max_requests_per_run": MAX_REQUESTS_PER_RUN, "api_requests_made": 0}
    success, failed = [], []
    pending = list(ids)

    try:
        while pending:
            job_id = pending[0]
            if meta["api_requests_made"] >= MAX_REQUESTS_PER_RUN:
                break  # remaining jobs stay NOT_RUN
            job = jobs[job_id]
            expected_rel = job["expected_file"]
            expected_path = REFS / expected_rel
            before = {x.resolve() for x in expected_path.parent.iterdir() if x.is_file()} if expected_path.parent.exists() else set()

            meta["api_requests_made"] += 1   # count the attempt whether or not it succeeds
            pending.pop(0)
            proc = run_captured([
                sys.executable,
                "Scripts/REN_Visual/openai_image_generate.py",
                "--job-id", job_id,
                "--quality", args.quality,
            ])
            if proc.returncode != 0:
                reason, charged = sanitize_failure(proc.stderr, proc.returncode)
                print(f"FAILED {job_id}: {reason}", flush=True)
                failed.append({"job_id": job_id, "status": "FAILED", "reason": reason, "charged": charged})
                continue

            after = {x.resolve() for x in expected_path.parent.iterdir() if x.is_file()} if expected_path.parent.exists() else set()
            new_files = sorted(after - before, key=lambda p: p.stat().st_mtime_ns)
            pngs = [p for p in new_files if p.suffix.lower() == ".png"]
            if not pngs:
                print(f"FAILED {job_id}: no new PNG detected", flush=True)
                failed.append({"job_id": job_id, "status": "FAILED",
                               "reason": "generator reported success but no new PNG was detected",
                               "charged": "unknown (request completed; likely charged)"})
                continue
            candidate = pngs[-1]
            rel = candidate.relative_to(REFS).as_posix()

            rec = run_captured([
                sys.executable,
                "Scripts/REN_Visual/ren_visual.py",
                "record", job_id,
                "--file", rel,
                "--status", "NEEDS_REVIEW",
            ])
            if rec.returncode != 0:
                # The image exists and is kept (it will be committed); only the manifest record failed.
                print(f"FAILED {job_id}: image saved but manifest record failed ({rel})", flush=True)
                failed.append({"job_id": job_id, "status": "FAILED",
                               "reason": f"image saved at {rel} but manifest record failed",
                               "charged": "yes (image was produced)"})
                continue

            entry = {"job_id": job_id, "file": rel,
                     "dimensions": png_dimensions(candidate), "status": "NEEDS_REVIEW"}
            usage_m = re.search(r"^USAGE_JSON: (\{.*\})$", proc.stdout or "", re.M)
            if usage_m:
                try:
                    entry["usage"] = json.loads(usage_m.group(1))
                except ValueError:
                    pass
            success.append(entry)
    finally:
        # Always persist the report, even after an unexpected error, so successes are never lost.
        write_report(meta, success, failed, pending)
        summary = format_summary(success, failed, pending)
        print("\nBatch results:\n" + summary, flush=True)
        step_summary = os.getenv("GITHUB_STEP_SUMMARY")
        if step_summary:
            with open(step_summary, "a", encoding="utf-8") as f:
                f.write("## REN visual batch results\n\n```\n" + summary + "\n```\n")

    # Individual refusals/failures are NOT a batch failure: exit 0 so the persist step commits successes.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
