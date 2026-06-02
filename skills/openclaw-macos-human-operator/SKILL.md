---
name: openclaw-macos-human-operator
description: Efficient human-like macOS desktop application operation for OpenClaw agents. Use when Codex/OpenClaw must control a Mac GUI app with screenshots, Accessibility/UI scripting, cautious mouse/keyboard actions, visual verification, batched desktop actions, or app workflows that lack an API; especially for Finder, native macOS apps, Electron apps, browsers, and legacy desktop tools.
---

# OpenClaw macOS Human Operator

Operate macOS desktop apps with a token-efficient human loop: **observe → plan 1-3 actions → act → verify**. Prefer files/APIs/AppleScript before raw coordinates; use GUI control only when the visible app state matters.

## Fast Start

Use the helper first; load references only when needed.

```bash
python3 scripts/macos_human_operator.py preflight
python3 scripts/macos_human_operator.py observe --out /tmp/openclaw/before.png --ui-depth 2 --format compact
```

For multi-step work, avoid many shell calls. Put actions in JSON and run one process:

```bash
python3 scripts/macos_human_operator.py batch --profile fast --file /tmp/openclaw/actions.json
```

Example `actions.json`:

```json
[
  {"action":"activate","app":"Notes"},
  {"action":"hotkey","keys":["command","n"]},
  {"action":"type","text":"Draft text","paste_threshold":80},
  {"action":"screenshot","out":"/tmp/openclaw/after.png"}
]
```

## Runtime Rules

- Use **fast** profile for routine navigation, **balanced** for default work, **careful** for tiny/destructive targets.
- Read `references/human_gui_workflow.md` only for recovery, safety edge cases, or coordinate targeting details.
- Read `references/openclaw_integration.md` only for install/runtime setup.
- Stop for confirmation before credentials, purchases, sending/submitting, deletion/overwrite, security/privacy/billing changes, or permission grants.
- Do not use this for stealth, CAPTCHA bypass, anti-bot evasion, surveillance, or deception.

## Tool Priority

1. Native file/API edits.
2. AppleScript, Shortcuts, URL schemes.
3. Accessibility UI tree (`observe --ui-depth N` or `ui-tree`).
4. Screenshot/vision plus coordinates.
5. OCR/manual reading only when needed.

## Efficient Output

Report only: final state, verification evidence path(s), confirmations skipped/needed, and any uncertainty. Prefer compact command output (`observe --format compact`; `batch` is compact by default, use `--verbose` only for debugging) to save tokens.
