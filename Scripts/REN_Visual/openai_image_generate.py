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
    return "1024x1536"

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

# Production policy appended to every prompt (policy only; canon unchanged).
# Labels, attack names, dimensions and notes are added later as deterministic
# overlay/document text, never rendered by the image model.
NO_TEXT_POLICY=(
    "PRODUCTION POLICY — NO RENDERED TEXT (overrides any instruction above, including requests for labels, "
    "names, notes, dimensions or Arabic): generate clean visual panels only. Render no Arabic, no English, "
    "no letters, numbers, titles, captions, labels, annotations, legends, callouts, arrows with text, "
    "pseudo-hieroglyphic explanatory text or fake material-map/texture-map panels anywhere in the image. "
    "Canon text in the brief is design information only and must not be reproduced as writing. "
    "Leave panel areas clean; text is added later outside the image model."
)
# Used whenever the locked Nefer identity master is NOT supplied as an image input.
NEUTRAL_SCALE_POLICY=(
    "PRODUCTION POLICY — SCALE FIGURE: the locked Nefer identity master is NOT supplied for this job, so do not "
    "depict Nefer and do not present any generated person as Nefer. Wherever a scale comparison or human "
    "reference is requested, use only a neutral, unlabeled, featureless human scale silhouette or a simple "
    "unlabeled metric scale bar."
)

def identity_master_or_fail(job):
    """Fail closed for identity-sensitive jobs (C01 Nefer, or any job declaring an identity master).

    Such a job must never silently fall back to text-only generation.
    Returns the identity image path, or None for jobs that are not identity-sensitive.
    """
    identity_rel=job.get("input_identity_master")
    sensitive=job["id"].startswith("C01.") or bool(identity_rel)
    if not sensitive:
        return None
    if not identity_rel:
        raise SystemExit(f"IDENTITY FAIL-CLOSED: {job['id']} is identity-sensitive but declares no input_identity_master; refusing text-only generation.")
    path=REFS/identity_rel
    if not path.is_file():
        raise SystemExit(f"IDENTITY FAIL-CLOSED: locked identity master missing for {job['id']} ({identity_rel}); refusing text-only generation.")
    with path.open("rb") as f:
        head=f.read(64)
    if head.startswith(b"version https://git-lfs"):
        raise SystemExit(f"IDENTITY FAIL-CLOSED: identity master for {job['id']} is a Git LFS pointer, not an image; run git lfs pull.")
    if not head.startswith(b"\x89PNG") and not head.startswith(b"\xff\xd8"):
        raise SystemExit(f"IDENTITY FAIL-CLOSED: identity master for {job['id']} is not a PNG/JPEG image; refusing text-only generation.")
    return path

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
    identity_path=identity_master_or_fail(job)
    use_identity=identity_path is not None
    brief_path=REFS/job.get("required_canon_brief","")
    brief=brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
    prompt=job["prompt"]
    if brief:
        prompt += "\n\nCANON BRIEF — mandatory constraints:\n" + brief
    if args.prompt_extra:
        prompt += "\n\nTARGETED CORRECTION:\n" + args.prompt_extra
    prompt += "\n\n" + NO_TEXT_POLICY
    if not use_identity:
        prompt += "\n\n" + NEUTRAL_SCALE_POLICY

    size=args.size or choose_size(job)
    target=versioned_target(job["expected_file"])
    target.parent.mkdir(parents=True,exist_ok=True)

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

    # Cost safety: exactly one API request per job. The SDK's default automatic
    # retries (max_retries=2) are disabled; failed jobs are retried only manually after review.
    client=OpenAI(max_retries=0)

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
