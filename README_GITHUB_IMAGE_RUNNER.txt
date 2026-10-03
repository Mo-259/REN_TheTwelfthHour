REN GitHub Image Runner PATCH v1

Extract directly into the REN_TheTwelfthHour repository root.

Adds:
- .github/workflows/ren-visual-generate.yml
- Scripts/REN_Visual/github_generate_batch.py
- ProjectDocs/ClaudeCode/GITHUB_IMAGE_RUNNER.md

Purpose:
Claude Code Cloud does not need direct access to OPENAI_API_KEY.
GitHub Actions reads the repository secret and performs image generation.

First test job:
C04.Hero_Master (Anubis Hero Master)

Safety:
- maximum 8 images per workflow run
- generated work is recorded NEEDS_REVIEW
- no automatic LOCKED promotion
