# REN Claude Code Visual Factory v1

This ZIP is designed to be extracted directly into the **REN_TheTwelfthHour repository root**.

It does not replace the existing Unreal project or existing root `CLAUDE.md`.
It adds:
- the full current Visual Production reference scaffold,
- the v3 Production Bible,
- Claude Code subagents,
- project slash commands,
- safe queue/manifest scripts,
- an optional OpenAI image-generation adapter,
- approval and anti-drift rules.

## After extraction

Open Claude Code in the repository root.

Preferred start:

```text
/ren-visual-start
```

If the command is not discovered, paste the entire contents of:

```text
ProjectDocs/ClaudeCode/ONE_TIME_START_PROMPT.txt
```

That is the only production prompt needed.

## External prerequisite for actual image generation

Claude Code needs access to an image generator.

This bundle includes an OpenAI Images API adapter.
If you use it, set `OPENAI_API_KEY` locally in your environment.
Never paste the key into chat or commit it.

Without an image-generation credential/tool, Claude can audit and manage the queue but cannot create photorealistic references.

## Safety

Generated art is never auto-LOCKED.
P0 is produced before late-game breadth.
No auto-push.
No destructive Git commands.
No Unreal world edits are part of this visual task.
