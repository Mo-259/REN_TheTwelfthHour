---
paths:
  - "Content/**/*"
  - "Config/**/*"
---

# Unreal Asset / Config Rules

- `.uasset` and `.umap` are binary; do not infer Blueprint graph logic from raw bytes.
- Do not rewrite or mass-delete binary assets from cloud.
- Use live Unreal MCP or Unreal-generated reports for meaningful asset inspection.
- Preserve map/asset names and folder conventions.
- Do not modify Engine template content when a REN-owned duplicate is more appropriate.
- Avoid Level Blueprint for reusable gameplay systems.
