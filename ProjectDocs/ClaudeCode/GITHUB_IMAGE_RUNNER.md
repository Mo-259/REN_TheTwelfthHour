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

Do not auto-LOCK.
Do not generate the entire queue before the first image is reviewed.
