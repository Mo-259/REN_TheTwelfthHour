# Git Import Checklist

Run from the Unreal project root.

## 1. Verify destination

You should have:

```text
ProjectDocs/References/REFERENCE_MANIFEST.json
ProjectDocs/References/DESIGN_AUTHORITY.md
ProjectDocs/References/GENERATION_JOBS.jsonl
```

You should NOT have:

```text
ProjectDocs/ProjectDocs/References/
```

## 2. Inspect Git

```powershell
git status
```

Review the new `ProjectDocs/References/` files.

## 3. Add only the reference package

```powershell
git add ProjectDocs/References
```

## 4. Review staged files

```powershell
git status
git diff --cached --stat
```

## 5. Commit

Suggested message:

```text
art: add REN v3 visual reference production scaffold
```

## 6. Push

Push the current working branch according to the repository's normal branch workflow.

Do not claim the art pack is visually complete in the commit message.
