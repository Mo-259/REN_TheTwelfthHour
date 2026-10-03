# REN Visual Scripts

## Audit

```powershell
python Scripts/REN_Visual/ren_visual.py audit
```

## Show next P0 jobs

```powershell
python Scripts/REN_Visual/ren_visual.py next --priority P0 --limit 10
```

## Inspect one job

```powershell
python Scripts/REN_Visual/ren_visual.py show C04.Hero_Master
```

## Generate one candidate

```powershell
python Scripts/REN_Visual/openai_image_generate.py --job-id C04.Hero_Master
```

Targeted retry:

```powershell
python Scripts/REN_Visual/openai_image_generate.py `
  --job-id C04.Hero_Master `
  --prompt-extra "Reduce human torso anatomy; make cervical and thoracic morphology continuous with funerary jackal-derived organism."
```

The script never overwrites an existing file; it increments the version.

## Record a reviewed candidate

Use a path relative to `ProjectDocs/References/`:

```powershell
python Scripts/REN_Visual/ren_visual.py record C04.Hero_Master `
  --file 02_Gods/Anubis/REF_GOD_Anubis_Hero_Master_v03.png `
  --status NEEDS_REVIEW
```

`LOCKED` cannot be assigned by the helper.

## Security

Never commit an API key.
Never paste an API key into an LLM conversation.
