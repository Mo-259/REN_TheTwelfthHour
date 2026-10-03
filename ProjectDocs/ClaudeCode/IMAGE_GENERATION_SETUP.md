# Image Generation Setup for Claude Code

The repository includes:
`Scripts/REN_Visual/openai_image_generate.py`

It is an optional external image-generation adapter.

## Prerequisite

Set `OPENAI_API_KEY` in the local environment.

Do not paste the key into Claude chat and do not save it in the repo.

PowerShell example for the current terminal session:

```powershell
$env:OPENAI_API_KEY="YOUR_KEY_SET_LOCALLY"
```

Permanent user-level environment setup can be done through Windows Environment Variables.

## Python packages

The helper needs:
- `openai`
- no image dependency for basic PNG dimension checks

Install through:

```powershell
python -m pip install -r Scripts/REN_Visual/requirements.txt
```

or use the provided setup script:

```powershell
powershell -ExecutionPolicy Bypass -File Scripts/REN_Visual/setup_windows.ps1
```

## Model behavior

The adapter defaults to `gpt-image-2` because the REN pipeline requires explicit 2K-class dimensions and this model supports arbitrary valid sizes.

Override only deliberately:

```powershell
$env:REN_IMAGE_MODEL="gpt-image-2"
```

Never silently downgrade models.

## Important

For non-Nefer assets, Nefer is a rendering-realism benchmark only.
The adapter does NOT feed Nefer as an edit/reference image unless a job explicitly has an identity master.

This avoids accidentally copying Nefer's anatomy/identity into unrelated gods and monsters.
