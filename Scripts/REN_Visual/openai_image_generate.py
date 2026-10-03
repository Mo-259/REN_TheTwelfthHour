#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import contextlib
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
    check_image(path,"IDENTITY FAIL-CLOSED",job["id"])
    return path

CONTINUITY_BASES=REFS/"CONTINUITY_BASES.json"
CONTINUITY_INSTRUCTION=(
    "CONTINUITY: the supplied image is the current visual base for this asset (not a lock). Keep the identical "
    "subject: same anatomy, proportions, silhouette, costume, materials, colours and equipment. Produce only the "
    "requested view or sheet of this same asset; do not redesign it."
)

def strip_brief_sections(brief, headings):
    """Drop whole "## " sections whose heading line starts with one of `headings`, for prompt cost only.

    The brief file on disk is never changed; canon stays in the repository.
    """
    if not headings:
        return brief
    out=[]; skipping=False
    for line in brief.splitlines(keepends=True):
        if line.startswith("## "):
            skipping=any(line.startswith(h) for h in headings)
        if not skipping:
            out.append(line)
    return "".join(out)

# Shared no-copy rule for non-hero continuity jobs. Not applied to views whose purpose is to
# match the base (turnarounds, orthographic morphology, explicit matching views).
NO_COPY_RULE=(
    "The supplied continuity image defines identity, morphology, proportions and material language only. "
    "Never return its pose, framing, camera composition or background unchanged unless the requested view explicitly requires it."
)
MATCHING_VIEWS={"Turnaround_or_Morphology","Body_Turnaround","Front","Front_Side","Rear","Hero_Side","Identity_Comparison"}

def check_image(path, label, job_id):
    try:
        with path.open("rb") as f:
            head=f.read(64)
    except OSError as e:
        raise SystemExit(f"{label}: source image for {job_id} is unreadable ({type(e).__name__}).")
    if head.startswith(b"version https://git-lfs"):
        raise SystemExit(f"{label}: source image for {job_id} is a Git LFS pointer, not an image; run git lfs pull.")
    if not head.startswith(b"\x89PNG") and not head.startswith(b"\xff\xd8"):
        raise SystemExit(f"{label}: source image for {job_id} is not a PNG/JPEG image.")

def continuity_base_or_fail(job):
    """Follow-up views of an asset with an accepted continuity base are generated FROM that image.

    A base applies to the jobs of its own asset key, or to the assets listed in its "applies_to",
    never to a Hero_Master view or to its own "source_job". Never falls back to text-only
    generation: an unresolved or missing base fails the job before any API request.
    Using an image as a continuity base does not change its status.
    Returns (path, instruction) or None.
    """
    asset, _, view=job["id"].partition(".")
    if view=="Hero_Master" or not CONTINUITY_BASES.exists():
        return None
    bases=json.loads(CONTINUITY_BASES.read_text(encoding="utf-8")).get("bases",{})
    key=next((k for k,b in bases.items() if asset in b.get("applies_to",[k])),None)
    if key is None or job["id"]==bases[key].get("source_job"):
        return None
    base=bases[key]
    rel=base.get("file")
    if not rel:
        raise SystemExit(f"CONTINUITY FAIL-CLOSED: continuity base {key} is unresolved; refusing text-only follow-up view {job['id']}.")
    path=REFS/rel
    if not path.is_file():
        raise SystemExit(f"CONTINUITY FAIL-CLOSED: continuity base {key} missing ({rel}); refusing text-only follow-up view {job['id']}.")
    check_image(path,"CONTINUITY FAIL-CLOSED",job["id"])
    instruction=base.get("instruction") or CONTINUITY_INSTRUCTION
    if base.get("preserve"):
        instruction += " Preserve exactly: " + base["preserve"]
    if view not in MATCHING_VIEWS:
        instruction += " " + NO_COPY_RULE
    return path, instruction

def extra_references_or_fail(job):
    """Additional ordered reference images declared in the job's "input_references".

    Each entry is a path relative to ProjectDocs/References, or {"file": ..., "role": ...}.
    Every declared reference is required: missing, unreadable, LFS-pointer or non-image files
    fail the job before any API request. Nothing is silently dropped.
    Returns a list of (path, role).
    """
    refs=job.get("input_references") or []
    if not isinstance(refs, list):
        raise SystemExit(f"REFERENCE FAIL-CLOSED: input_references for {job['id']} must be a list.")
    out=[]
    for n, ref in enumerate(refs, 1):
        rel=ref.get("file") if isinstance(ref, dict) else ref
        role=(ref.get("role") if isinstance(ref, dict) else None) or f"reference {n}"
        if not rel:
            raise SystemExit(f"REFERENCE FAIL-CLOSED: reference {n} for {job['id']} is undeclared (empty path).")
        path=REFS/rel
        if not path.is_file():
            raise SystemExit(f"REFERENCE FAIL-CLOSED: required reference {n} for {job['id']} missing ({rel}); refusing generation without it.")
        check_image(path,"REFERENCE FAIL-CLOSED",job["id"])
        out.append((path, role))
    return out

def cross_asset_rules(job):
    """Reusable continuity rules (CONTINUITY_BASES.json "cross_asset_rules") for any job whose
    prompt mentions the subject, regardless of which asset the job belongs to."""
    if not CONTINUITY_BASES.exists():
        return []
    rules=json.loads(CONTINUITY_BASES.read_text(encoding="utf-8")).get("cross_asset_rules",[])
    text=job.get("prompt","")
    return [r["rule"] for r in rules
            if any(m in text for m in r.get("match",[])) and r.get("skip_if_contains","\0") not in text]

def usage_dict(result):
    u=getattr(result,"usage",None)
    if u is None:
        return None
    try:
        return u.model_dump()
    except Exception:
        return {k:getattr(u,k,None) for k in ("input_tokens","output_tokens","total_tokens")}

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
    continuity=None if identity_path else continuity_base_or_fail(job)
    continuity_path=continuity[0] if continuity else None
    # Ordered source images: identity master or continuity base first, then declared extra references.
    sources=[]
    if identity_path:
        sources.append((identity_path, "locked identity master"))
    elif continuity_path:
        sources.append((continuity_path, "continuity base"))
    sources+=extra_references_or_fail(job)
    required=int(job.get("required_reference_count",0) or 0)
    if len(sources) < required:
        raise SystemExit(f"REFERENCE FAIL-CLOSED: {job['id']} requires {required} source images but only {len(sources)} are declared; refusing generation.")
    # The locked Nefer master counts as supplied whether it is the identity master or an extra reference.
    nefer_supplied=any(pth.relative_to(REFS).as_posix().startswith("01_Nefer/") for pth, _ in sources)
    brief_path=REFS/job.get("required_canon_brief","")
    brief=brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
    brief=strip_brief_sections(brief, job.get("brief_exclude_headings",[]))
    prompt=job["prompt"]
    if brief:
        prompt += "\n\nCANON BRIEF — mandatory constraints:\n" + brief
    if args.prompt_extra:
        prompt += "\n\nTARGETED CORRECTION:\n" + args.prompt_extra
    if continuity:
        prompt += "\n\n" + continuity[1]
    if len(sources) > 1:
        prompt += "\n\nSOURCE IMAGES (in the order supplied): " + "; ".join(
            f"image {n}: {role}" for n, (_, role) in enumerate(sources, 1)) + ". Preserve each exactly; redesign none of them."
    for rule in cross_asset_rules(job):
        prompt += "\n\n" + rule
    prompt += "\n\n" + NO_TEXT_POLICY
    if not nefer_supplied:
        prompt += "\n\n" + NEUTRAL_SCALE_POLICY

    size=args.size or choose_size(job)
    target=versioned_target(job["expected_file"])
    target.parent.mkdir(parents=True,exist_ok=True)

    print(f"Job: {job['id']}")
    print(f"Model: {args.model}")
    print(f"Quality: {args.quality}")
    print(f"Size: {size}")
    mode="EDIT_WITH_IDENTITY_MASTER" if identity_path else ("EDIT_WITH_CONTINUITY_BASE" if continuity_path else ("EDIT_WITH_REFERENCES" if sources else "GENERATE"))
    print(f"Mode: {mode}")
    for n, (path, role) in enumerate(sources, 1):
        print(f"Source image {n}: {path.relative_to(REFS)} ({role})")
    print("SOURCES_JSON: "+json.dumps([str(pth.relative_to(REFS)) for pth, _ in sources]))
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
    # not passed as edit inputs for unrelated subjects. Continuity bases come only
    # from CONTINUITY_BASES.json.
    if sources:
        with contextlib.ExitStack() as stack:
            files=[stack.enter_context(pth.open("rb")) for pth, _ in sources]
            result=client.images.edit(
                model=args.model,
                image=files[0] if len(files)==1 else files,
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
    usage=usage_dict(result)
    if usage is not None:
        print("USAGE_JSON: "+json.dumps(usage,sort_keys=True,default=str))
    print("STATUS: candidate only; visually inspect before record/approval.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
