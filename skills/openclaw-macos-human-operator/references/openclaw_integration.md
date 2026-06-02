# OpenClaw Integration Notes

## Install layout

Copy this skill directory into the OpenClaw/Codex skills location used by your OpenClaw runtime. Common patterns are:

- Project-local: `<openclaw-project>/skills/openclaw-macos-human-operator/`
- User-local: `~/.codex/skills/openclaw-macos-human-operator/`
- Container-mounted: mount this folder read-only and expose `SKILL.md` plus `scripts/` to the agent.

Keep `scripts/macos_human_operator.py` executable:

```bash
chmod +x scripts/macos_human_operator.py
```

## macOS permissions

The helper relies on normal macOS automation channels:

- Screen Recording: required for screenshots on modern macOS.
- Accessibility: required for System Events, UI tree inspection, keyboard, and mouse actions.
- Automation/Apple Events: required when controlling specific apps through AppleScript.

Grant permissions manually in System Settings. A skill should explain the requested permission and wait; it should not bypass TCC.

## OpenClaw agent prompt pattern

Use a prompt like:

```text
Use $openclaw-macos-human-operator to operate <App Name>. Goal: <desired end state>. Work in small observe-plan-act-verify steps, save screenshots under /tmp/openclaw-gui-<task>, and stop before submitting/deleting/sending anything unless I confirm.
```

## Calling the helper efficiently

Prefer one compact observation call:

```bash
python3 skills/openclaw-macos-human-operator/scripts/macos_human_operator.py observe --out /tmp/openclaw-gui-task/before.png --ui-depth 2 --format compact
```

Prefer one batch call for multiple actions:

```bash
cat >/tmp/openclaw-gui-task/actions.json <<'JSON'
[
  {"action":"activate","app":"Finder"},
  {"action":"hotkey","keys":["command","shift","g"]},
  {"action":"type","text":"~/Downloads","paste_threshold":60},
  {"action":"hotkey","keys":["return"]},
  {"action":"screenshot","out":"/tmp/openclaw-gui-task/after.png"}
]
JSON
python3 skills/openclaw-macos-human-operator/scripts/macos_human_operator.py batch --profile fast --file /tmp/openclaw-gui-task/actions.json
```

Use separate commands only for debugging or when you need full intermediate output.

## Recommended runtime policy

- Run on the user's logged-in Mac session, not as root.
- Restrict the agent to an allowlist of apps for the current task.
- Store screenshots in a temporary task directory and clean them up if they contain sensitive data.
- Log command invocations and high-level decisions for auditability.
