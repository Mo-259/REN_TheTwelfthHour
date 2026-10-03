Continue the existing REN visual-production state without rebuilding planning.

Read:
- `ProjectDocs/ClaudeCode/REN_VISUAL_FACTORY_MASTER.md`
- `ProjectDocs/References/REFERENCE_MANIFEST.json`
- `ProjectDocs/References/GENERATION_JOBS.jsonl`

Run:
`python Scripts/REN_Visual/ren_visual.py audit`

Then process the next incomplete job in the current approved priority, respecting the batch limit, approval policy, and retry ceiling.
