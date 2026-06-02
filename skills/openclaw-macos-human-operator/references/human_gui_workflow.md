# Human GUI Workflow for macOS Desktop Apps

## Core loop

Use this loop for every GUI task:

1. **Observe**: use `observe` for one compact screenshot/front-app/UI-tree call; record visible dialogs and disabled controls.
2. **Intent**: write one sentence describing the next state, e.g. "The Save dialog should be open with filename filled."
3. **Act**: perform at most three low-risk UI actions.
4. **Verify**: screenshot or UI tree check confirms the intended state.
5. **Decide**: continue, recover, ask the user, or stop.

## Efficiency profile

Use the lowest-cost mode that is safe:

- `fast`: routine navigation, large targets, reversible actions.
- `balanced`: default profile.
- `careful`: tiny targets, unfamiliar windows, or near destructive controls.

Prefer `observe --format compact` and `batch --profile fast --file actions.json` to reduce shell calls and token output. Only request deep UI trees (`--ui-depth 4+`) after shallow observation fails.

## Human-like behavior rules

- Move the pointer along a path, not by teleporting unless the target app is insensitive to mouse behavior.
- Use jitter of 2-6 px for ordinary clicks; use 0-1 px for tiny controls.
- Pause 100-350 ms before clicking after a movement, and 150-600 ms after a click before observing.
- Type short natural text with 25-90 ms between characters. Paste long or structured text to avoid typos.
- Use keyboard shortcuts a human would use (`Command+L`, `Command+S`, `Command+Tab`) when safer than clicking.
- Scroll in moderate increments and re-observe; do not fling to unknown positions.

## Targeting hierarchy

1. Accessibility element by role/title/value.
2. Menu item by AppleScript/System Events.
3. Relative coordinate inside a known window.
4. Absolute coordinate from screenshot.
5. OCR-derived coordinate.

When using coordinates, record why the target is safe: visible label, known window bounds, or recent screenshot crop.

## Safety checkpoints

Stop for explicit user confirmation before:

- Submitting or sending anything to another person or external service.
- Deleting, archiving, overwriting, or bulk-moving user data.
- Installing software, granting permissions, changing privacy/security/billing settings.
- Entering passwords, MFA codes, recovery keys, private keys, or payment details.
- Accepting legal terms or making commitments on behalf of the user.

## Recovery playbooks

### App not focused

1. `activate --app "Name"`.
2. Verify with screenshot or `front-app`.
3. If still wrong, use Command+Tab or ask the user whether the app is installed/running.

### Permission denied

1. Run `preflight` to identify missing macOS permissions.
2. Explain the exact permission needed (Accessibility, Screen Recording, Automation).
3. Ask the user to grant it in System Settings. Do not attempt to bypass TCC.

### Unexpected modal/dialog

1. Read the dialog title/message from screenshot or UI tree.
2. If it is informational and has a safe cancel/close button, close it.
3. If it requests consent, credentials, payment, data deletion, or permissions, stop for user input.

### Click missed target

1. Do not repeat blindly.
2. Take a screenshot.
3. Recompute target using element bounds or a cropped screenshot.
4. Reduce jitter and move more slowly for the next attempt.

### UI changed after update/localization

1. Prefer roles and stable control positions over exact labels.
2. Search menus with likely synonyms.
3. Ask the user for a screenshot or app version if critical controls are missing.

## Evidence logging

Create a task directory such as `/tmp/openclaw-gui-YYYYmmdd-HHMMSS/` and save:

- `before.png`, `after-<step>.png`, and final screenshot.
- Any UI tree text used for targeting.
- A short notes file with decisions and confirmations.
