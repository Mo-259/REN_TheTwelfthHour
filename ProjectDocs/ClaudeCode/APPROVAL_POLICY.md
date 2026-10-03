# REN Visual Approval Policy

## Status meanings

### LOCKED
Human-approved visual authority.
Never changed in place.

### APPROVED_BASE
Human-approved foundation for downstream exploration.
May still need technical sheets.

### NEEDS_REVIEW
Generated or revised candidate that passed basic mechanical validation but has not been human-approved.

### PROVISIONAL
A required slot exists in planning, but its visual is absent or insufficient.

### ARCHIVED
Not current authority.

## Automatic actions allowed

Claude may automatically:
- generate a new version,
- reject an obviously invalid candidate,
- archive a rejected generated candidate,
- mark a successfully written generated file `NEEDS_REVIEW`,
- record real dimensions,
- record generation model and prompt provenance,
- update completion counts.

Claude may not automatically:
- mark generated work `LOCKED`,
- replace a locked source,
- alter Nefer's face authority,
- delete historical candidates,
- promote an old conflicting design because it is prettier.

## Regeneration ceiling

At most 2 targeted regenerations for the same reference in one unattended pass.

After that:
- preserve the strongest candidate,
- mark `NEEDS_REVIEW`,
- document the unresolved issue,
- move to the next job.

This prevents endless API spend and style drift.
