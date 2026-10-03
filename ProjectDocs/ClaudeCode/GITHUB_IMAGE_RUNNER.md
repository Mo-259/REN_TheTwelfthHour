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

Do not auto-LOCK.
Do not generate the entire queue before the first image is reviewed.
