#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path

def find_root():
    p=Path.cwd().resolve()
    for root in [p,*p.parents]:
        if (root/"ProjectDocs"/"References"/"GENERATION_JOBS.jsonl").exists():
            return root
    raise SystemExit("Run from the REN repository root.")

ROOT=find_root()
REFS=ROOT/"ProjectDocs"/"References"
JOBS=REFS/"GENERATION_JOBS.jsonl"

def load_job(job_id):
    with JOBS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                j=json.loads(line)
                if j["id"]==job_id:
                    return j
    raise SystemExit(f"Job not found: {job_id}")

def choose_size(job):
    p=job.get("expected_file","").replace("\\","/")
    low=p.lower()
    if "/11_environments/" in "/"+low or "/17_cinematics/" in "/"+low:
        return "2048x1152"
    if "/14_materials/" in "/"+low or "scale" in low:
        return "2048x2048"
    return "1536x2048"

def versioned_target(expected_rel: str):
    target=REFS/expected_rel
    if not target.exists():
        return target
    stem=target.stem
    suffix=target.suffix
    m=1
    # If filename already has _vNN, increment it.
    import re
    match=re.search(r"_v(\d+)$", stem)
    if match:
        base=stem[:match.start()]
        m=int(match.group(1))+1
    else:
        base=stem
        m=2
    while True:
        cand=target.with_name(f"{base}_v{m:02d}{suffix}")
        if not cand.exists():
            return cand
        m+=1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--job-id",required=True)
    ap.add_argument("--model",default=os.getenv("REN_IMAGE_MODEL","gpt-image-2"))
    ap.add_argument("--quality",default=os.getenv("REN_IMAGE_QUALITY","high"))
    ap.add_argument("--size",default=None)
    ap.add_argument("--prompt-extra",default="")
    ap.add_argument("--dry-run",action="store_true")
    args=ap.parse_args()

    job=load_job(args.job_id)
    brief_path=REFS/job.get("required_canon_brief","")
    brief=brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
    prompt=job["prompt"]
    if brief:
        prompt += "\n\nCANON BRIEF — mandatory constraints:\n" + brief
    if args.prompt_extra:
        prompt += "\n\nTARGETED CORRECTION:\n" + args.prompt_extra

    size=args.size or choose_size(job)
    target=versioned_target(job["expected_file"])
    target.parent.mkdir(parents=True,exist_ok=True)

    identity_rel=job.get("input_identity_master")
    identity_path=(REFS/identity_rel) if identity_rel else None
    use_identity=bool(identity_path and identity_path.exists())

    print(f"Job: {job['id']}")
    print(f"Model: {args.model}")
    print(f"Quality: {args.quality}")
    print(f"Size: {size}")
    print(f"Mode: {'EDIT_WITH_IDENTITY_MASTER' if use_identity else 'GENERATE'}")
    print(f"Output: {target.relative_to(ROOT)}")

    if args.dry_run:
        print("\n--- PROMPT ---\n")
        print(prompt)
        return 0

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is missing. Set it locally; never commit or paste it into chat.")

    try:
        from openai import OpenAI
    except Exception:
        raise SystemExit("Python package 'openai' is missing. Run: python -m pip install -r Scripts/REN_Visual/requirements.txt")

    client=OpenAI()

    # Important: Nefer may be used as an identity master only when the job explicitly
    # declares input_identity_master. Style-only Nefer references are intentionally
    # not passed as edit inputs for unrelated subjects.
    if use_identity:
        with identity_path.open("rb") as img:
            result=client.images.edit(
                model=args.model,
                image=img,
                prompt=prompt,
                size=size,
                quality=args.quality,
            )
    else:
        result=client.images.generate(
            model=args.model,
            prompt=prompt,
            size=size,
            quality=args.quality,
        )

    if not result.data:
        raise SystemExit("Image API returned no image data.")
    b64=result.data[0].b64_json
    if not b64:
        raise SystemExit("Image API response did not contain b64_json.")
    target.write_bytes(base64.b64decode(b64))
    print(f"SAVED: {target}")
    print("STATUS: candidate only; visually inspect before record/approval.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
