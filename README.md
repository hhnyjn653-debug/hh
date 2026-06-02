# hhwork

This repository contains a complete Codex/OpenClaw skill for human-like macOS desktop app operation.

## Skill

- `skills/openclaw-macos-human-operator/` — a token-efficient macOS GUI operation skill that teaches OpenClaw/Codex agents to observe, plan, batch actions, and verify like a careful human when controlling desktop applications.

## Validate

```bash
python /opt/codex/skills/.system/skill-creator/scripts/quick_validate.py skills/openclaw-macos-human-operator
python3 -m py_compile skills/openclaw-macos-human-operator/scripts/macos_human_operator.py
python3 skills/openclaw-macos-human-operator/scripts/macos_human_operator.py --help
python3 skills/openclaw-macos-human-operator/scripts/macos_human_operator.py preflight
```
