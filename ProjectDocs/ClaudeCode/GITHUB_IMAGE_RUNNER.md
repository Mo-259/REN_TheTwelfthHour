# Claude Code Cloud — GitHub Image Runner

The OpenAI image credential is intentionally NOT available to Claude Code Cloud.

Image generation is executed by GitHub Actions using the repository secret:
`OPENAI_API_KEY`.

Workflow:
`.github/workflows/ren-visual-generate.yml`

Do not request or print the secret.

## To request an image

Prefer GitHub CLI if available:

```bash
gh workflow run ren-visual-generate.yml \
  --ref main \
  -f job_ids="C04.Hero_Master" \
  -f quality="high"
```

For the first validation run, generate **Anubis Hero Master only**.

Do not request multiple assets until that workflow completes successfully.

After the workflow commits the candidate:
1. refresh/fetch `main`,
2. inspect `ProjectDocs/References/LAST_GITHUB_GENERATION.json`,
3. visually review the generated file if image inspection is available,
4. keep it `NEEDS_REVIEW`,
5. report whether it passes the REN canon/realism/morphology gate.

## Batch resilience and cost safety

- Each requested job runs independently. A refused or failed image is recorded as `FAILED` (short, sanitized reason; raw API responses are never logged) and the batch continues. Successful outputs are always committed.
- `LAST_GITHUB_GENERATION.json` (schema 2) lists `success`, `failed` and `not_run`, plus `api_requests_made`. The same summary appears in the workflow run's step summary.
- Hard limit: **8 image API requests per workflow run**. There are no automatic retries inside the runner (SDK retries are disabled). A refused job gets at most **one** later targeted retry, after review.
- The whole batch fails only for infrastructure errors: checkout, missing `OPENAI_API_KEY`, Python/dependency setup, a corrupt queue or manifest, unknown job ids, or inability to write or persist output. If the commit/push fails, outputs are uploaded as a run artifact.

## Production prompt policy (generator-enforced)

`openai_image_generate.py` appends these to every prompt. They are production policy only and don't change canon.

- **No rendered text.** The image model renders no Arabic, no English, no captions or labels, no pseudo-hieroglyphic explanatory text and no fake material/texture-map panels. Gameplay, enemy, weapon and technical sheets are clean visual panels. Labels, attack names, dimensions and notes are added later as deterministic overlay or document text. Existing acceptable sheets are not regenerated just to remove text.
- **No fake Nefer.** When the locked Nefer identity master is not supplied as an image input, no person is depicted or labelled as Nefer. Scale comparisons use a neutral, unlabeled human silhouette or a plain metric scale bar. The real locked Nefer can be added later as a deterministic overlay.
- **Identity fail-closed.** Any `C01.*` job, or any job declaring `input_identity_master`, fails with `IDENTITY FAIL-CLOSED` if the master is undeclared, missing, an LFS pointer or not an image. It never falls back to text-only generation. The check runs before any API call, but the batch runner still counts the attempt against the 8-request cap (conservative).

## Continuity bases (follow-up view drift)

`ProjectDocs/References/CONTINUITY_BASES.json` lists the current visual base per asset. Every job of a listed asset except its `Hero_Master` (turnaround, morphology, materials, phase states, gameplay poses, detail and scale sheets) runs in `EDIT_WITH_CONTINUITY_BASE` mode from that image, with an instruction to keep the identical subject.

- Fail-closed: an unresolved (`"file": null`) or missing base fails the job with `CONTINUITY FAIL-CLOSED` before any API request. It never falls back to text-only generation.
- Listing an image as a base does **not** change its status and does **not** lock it.
- A job's `input_identity_master` (Nefer for C01/TR*, Hori for B03.Hero_Master) takes precedence over a continuity base.
- A base may set `applies_to` (asset keys it serves, instead of its own key), `source_job` (its own job, never edited from itself), a custom `instruction` and a `preserve` list.
- Current decisions: Anubis base = `REF_GOD_Anubis_Hero_Master_v02.png` (`REF_GOD_Anubis_Hero_v02.png` is not a base; kept on disk as historical reference). The Tomb sarcophagus base = `ENV_Tomb_02` Sarcophagus v01, **visual/material only, not spatial authority**; it currently serves `ENV_Tomb_01`. Other Tomb views are told not to depict the sarcophagus.

## Usage / cost metadata

When the image API returns token usage, the generator prints `USAGE_JSON` and the batch runner stores it as `usage` on each success entry in `LAST_GITHUB_GENERATION.json`. Money cost is not returned by the API; it is computed from tokens and the current price list.

Do not auto-LOCK.
Do not generate the entire queue before the first image is reviewed.
