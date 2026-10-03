#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from pathlib import Path
from collections import Counter

VALID_STATUSES = {"LOCKED","APPROVED_BASE","NEEDS_REVIEW","PROVISIONAL","ARCHIVED"}

P0_ASSET_ORDER = [
    "C01","C04","B01","B02","C20","C05","C18","B03",
    "E01","E02","E03","E04","E05","E06","E07","E08","E09","E10","E11","E12",
    "W01","W02","W03","W04",
]

def repo_root() -> Path:
    p = Path.cwd().resolve()
    for root in [p, *p.parents]:
        if (root/"ProjectDocs"/"References").exists():
            return root
    raise SystemExit("Could not find ProjectDocs/References. Run from the REN repository.")

ROOT = repo_root()
REFS = ROOT/"ProjectDocs"/"References"
MANIFEST = REFS/"REFERENCE_MANIFEST.json"
JOBS = REFS/"GENERATION_JOBS.jsonl"

def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))

def save_manifest(d):
    MANIFEST.write_text(json.dumps(d, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def load_jobs():
    rows=[]
    with JOBS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def save_jobs(rows):
    with JOBS.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False)+"\n")

def png_dimensions(path: Path):
    with path.open("rb") as f:
        sig=f.read(24)
    if len(sig)>=24 and sig[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", sig[16:24])
    return None

def priority_key(job):
    p = job.get("priority","P9")
    pid = int(p[1:]) if p.startswith("P") and p[1:].isdigit() else 99
    aid = job["id"].split(".",1)[0]
    try:
        aidx = P0_ASSET_ORDER.index(aid)
    except ValueError:
        aidx = 9999
    return (pid, aidx, job["id"])

def job_is_done(job):
    expected = REFS/job["expected_file"]
    status = job.get("status","")
    return expected.exists() or status in {"GENERATED","NEEDS_REVIEW","APPROVED_BASE","LOCKED","ARCHIVED"}

def audit():
    m=load_manifest()
    jobs=load_jobs()
    refs=m.get("references",[])
    statuses=Counter(r.get("status","UNKNOWN") for r in refs)
    prios=Counter(j.get("priority","UNKNOWN") for j in jobs)
    remaining=Counter()
    missing_expected=[]
    existing_generated=0
    for j in jobs:
        if not job_is_done(j):
            remaining[j.get("priority","UNKNOWN")]+=1
        if (REFS/j["expected_file"]).exists():
            existing_generated += 1
    for r in refs:
        fp=r.get("file")
        if fp and not (REFS/fp).exists():
            missing_expected.append((r["id"],fp))
    print("REN VISUAL FACTORY AUDIT")
    print(f"Repo: {ROOT}")
    print(f"Manifest refs: {len(refs)}")
    print(f"Generation jobs: {len(jobs)}")
    print(f"Job priorities: {dict(sorted(prios.items()))}")
    print(f"Remaining jobs: {dict(sorted(remaining.items()))}")
    print(f"Reference statuses: {dict(statuses)}")
    print(f"Expected generated job files present: {existing_generated}")
    print(f"Manifest file pointers missing on disk: {len(missing_expected)}")
    print(f"OPENAI_API_KEY: {'AVAILABLE' if os.getenv('OPENAI_API_KEY') else 'MISSING'}")
    source = ROOT/"ProjectDocs"/"SourceOfTruth"/"REN_Complete_Game_Production_Bible_AR_v3.pdf"
    print(f"V3 Production Bible: {'OK' if source.exists() else 'MISSING'}")
    if missing_expected:
        for rid, fp in missing_expected[:10]:
            print(f"  MISSING: {rid} -> {fp}")
    return 0 if source.exists() and not missing_expected else 2

def next_jobs(priority, limit):
    jobs=[j for j in load_jobs() if not job_is_done(j)]
    if priority:
        jobs=[j for j in jobs if j.get("priority")==priority]
    jobs.sort(key=priority_key)
    for j in jobs[:limit]:
        print(json.dumps({
            "id":j["id"],
            "priority":j.get("priority"),
            "expected_file":j["expected_file"],
            "brief":j.get("required_canon_brief"),
            "status":j.get("status"),
        }, ensure_ascii=False))
    return 0

def show_job(job_id):
    for j in load_jobs():
        if j["id"]==job_id:
            print(json.dumps(j, ensure_ascii=False, indent=2))
            return 0
    raise SystemExit(f"Job not found: {job_id}")

def record(job_id, file_rel, status):
    if status not in VALID_STATUSES:
        raise SystemExit(f"Invalid status {status}. Allowed: {sorted(VALID_STATUSES)}")
    if status=="LOCKED":
        raise SystemExit("Automatic LOCKED promotion is forbidden. Human approval must edit the manifest deliberately.")
    path=(REFS/file_rel).resolve()
    try:
        path.relative_to(REFS.resolve())
    except ValueError:
        raise SystemExit("File must be inside ProjectDocs/References.")
    if not path.exists():
        raise SystemExit(f"File does not exist: {path}")
    dims=png_dimensions(path)
    m=load_manifest()
    hit=None
    for r in m.get("references",[]):
        if r.get("id")==job_id:
            hit=r
            break
    if hit is None:
        raise SystemExit(f"Manifest reference not found: {job_id}")
    hit["file"]=file_rel.replace("\\","/")
    hit["status"]=status
    hit["visual_complete"]=True
    hit["visual_state"]="GENERATED_CANDIDATE_NEEDS_HUMAN_REVIEW" if status=="NEEDS_REVIEW" else f"RECORDED_{status}"
    if dims:
        w,h=dims
        hit["dimensions_px"]=[w,h]
        minimum=int(m.get("minimum_native_long_edge_px",2048))
        hit["resolution_compliant"]=max(w,h)>=minimum
    save_manifest(m)
    jobs=load_jobs()
    for j in jobs:
        if j["id"]==job_id:
            j["status"]=status
            j["actual_file"]=file_rel.replace("\\","/")
            if dims: j["dimensions_px"]=list(dims)
    save_jobs(jobs)
    print(f"Recorded {job_id} -> {file_rel} [{status}]")
    if dims:
        print(f"Dimensions: {dims[0]}x{dims[1]}")
    return 0

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("audit")
    n=sub.add_parser("next")
    n.add_argument("--priority")
    n.add_argument("--limit",type=int,default=10)
    s=sub.add_parser("show")
    s.add_argument("job_id")
    r=sub.add_parser("record")
    r.add_argument("job_id")
    r.add_argument("--file",required=True)
    r.add_argument("--status",default="NEEDS_REVIEW")
    a=ap.parse_args()
    if a.cmd=="audit": return audit()
    if a.cmd=="next": return next_jobs(a.priority,a.limit)
    if a.cmd=="show": return show_job(a.job_id)
    if a.cmd=="record": return record(a.job_id,a.file,a.status)

if __name__=="__main__":
    raise SystemExit(main())
