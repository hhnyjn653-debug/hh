#!/usr/bin/env python3
"""Human-like macOS desktop automation helper for OpenClaw skills.

The script intentionally uses only Python standard library plus optional macOS
frameworks (Quartz/AppKit) when available. On non-macOS hosts it still supports
--help and preflight diagnostics so the skill can be validated in CI.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import platform
import random
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

IS_MAC = platform.system() == "Darwin"

try:  # Optional: available when pyobjc-framework-Quartz is installed.
    import Quartz  # type: ignore
except Exception:  # pragma: no cover - import availability is host-specific.
    Quartz = None  # type: ignore

try:  # Optional: available when pyobjc-framework-AppKit is installed.
    import AppKit  # type: ignore
except Exception:  # pragma: no cover - import availability is host-specific.
    AppKit = None  # type: ignore


@dataclass(frozen=True)
class Point:
    x: float
    y: float


PROFILES = {
    "fast": {
        "click_duration": 0.16,
        "click_steps": 10,
        "click_pause": 0.08,
        "pre_click_pause": 0.05,
        "drag_duration": 0.35,
        "drag_steps": 16,
        "type_interval": 0.018,
        "type_pause": 0.06,
        "paste_threshold": 60,
    },
    "balanced": {
        "click_duration": 0.28,
        "click_steps": 18,
        "click_pause": 0.18,
        "pre_click_pause": 0.10,
        "drag_duration": 0.60,
        "drag_steps": 28,
        "type_interval": 0.035,
        "type_pause": 0.14,
        "paste_threshold": 100,
    },
    "careful": {
        "click_duration": 0.45,
        "click_steps": 32,
        "click_pause": 0.32,
        "pre_click_pause": 0.20,
        "drag_duration": 0.95,
        "drag_steps": 48,
        "type_interval": 0.055,
        "type_pause": 0.24,
        "paste_threshold": 160,
    },
}


KEY_ALIASES = {
    "cmd": "command",
    "command": "command",
    "control": "control",
    "ctrl": "control",
    "option": "option",
    "alt": "option",
    "shift": "shift",
    "return": "return",
    "enter": "return",
    "esc": "escape",
    "escape": "escape",
    "space": "space",
    "tab": "tab",
    "delete": "delete",
    "backspace": "delete",
    "up": "up arrow",
    "down": "down arrow",
    "left": "left arrow",
    "right": "right arrow",
}


def die(message: str, code: int = 2) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def run(cmd: Sequence[str], *, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(cmd),
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def osascript(script: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    if not IS_MAC:
        die("osascript actions require macOS")
    return run(["osascript", "-e", script, *args], check=check)


def require_mac(action: str) -> None:
    if not IS_MAC:
        die(f"{action} requires macOS; current platform is {platform.system()}")


def get_front_app() -> str:
    require_mac("front-app")
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = osascript(script, check=False)
    if result.returncode != 0:
        die(result.stderr.strip() or "could not query front app")
    return result.stdout.strip()


def capture_screenshot(out: str | None = None, *, window: bool = False) -> str:
    require_mac("screenshot")
    path = Path(out or tempfile.mkstemp(prefix="openclaw-screen-", suffix=".png")[1]).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["screencapture", "-x"]
    if window:
        cmd.append("-w")
    cmd.append(str(path))
    result = run(cmd, check=False)
    if result.returncode != 0:
        die(result.stderr.strip() or "screenshot failed; Screen Recording permission may be missing")
    return str(path)


def profile_name(args: argparse.Namespace) -> str:
    name = getattr(args, "profile", None) or "balanced"
    if name not in PROFILES:
        die(f"unknown profile {name!r}; choose fast, balanced, or careful")
    return name


def default_from_profile(args: argparse.Namespace, attr: str, key: str) -> None:
    if getattr(args, attr, None) is None:
        setattr(args, attr, PROFILES[profile_name(args)][key])


def preflight(_: argparse.Namespace) -> None:
    print(f"platform: {platform.platform()}")
    print(f"python: {sys.version.split()[0]}")
    print(f"macOS: {'yes' if IS_MAC else 'no'}")
    for binary in ("osascript", "screencapture", "cliclick"):
        found = shutil.which(binary)
        status = found if found else "not found"
        optional = " (optional)" if binary == "cliclick" else ""
        print(f"{binary}{optional}: {status}")
    print(f"Quartz/PyObjC: {'available' if Quartz is not None else 'not available'}")
    print(f"AppKit/PyObjC: {'available' if AppKit is not None else 'not available'}")
    if IS_MAC:
        front_app(argparse.Namespace())
        print("permissions: if screenshots, UI tree, or events fail, grant Screen Recording, Accessibility, and Automation in System Settings")
    else:
        print("note: action subcommands are disabled because this host is not macOS")


def front_app(_: argparse.Namespace) -> None:
    print(f"front_app: {get_front_app()}")


def screenshot(args: argparse.Namespace) -> None:
    print(capture_screenshot(args.out, window=args.window))


def activate(args: argparse.Namespace) -> None:
    require_mac("activate")
    if not args.app:
        die("--app is required")
    script = 'on run argv\n tell application (item 1 of argv) to activate\nend run'
    result = osascript(script, args.app, check=False)
    if result.returncode != 0:
        die(result.stderr.strip() or f"could not activate {args.app!r}")
    human_pause(args.pause)
    print(f"activated: {args.app}")


def normalize_key(key: str) -> str:
    lowered = key.lower()
    return KEY_ALIASES.get(lowered, lowered)


def hotkey(args: argparse.Namespace) -> None:
    require_mac("hotkey")
    if not args.keys:
        die("provide at least one key")
    keys = [normalize_key(k) for k in args.keys]
    modifiers = [k for k in keys[:-1] if k in {"command", "control", "option", "shift"}]
    key = keys[-1]
    using = ""
    if modifiers:
        using = " using {" + ", ".join(f"{m} down" for m in modifiers) + "}"
    key_expr = f'keystroke "{escape_applescript_string(key)}"'
    special = {"return", "escape", "space", "tab", "delete", "up arrow", "down arrow", "left arrow", "right arrow"}
    if key in special:
        key_expr = f"key code {special_key_code(key)}"
    script = f'tell application "System Events" to {key_expr}{using}'
    result = osascript(script, check=False)
    if result.returncode != 0:
        die(result.stderr.strip() or "hotkey failed; Accessibility permission may be missing")
    human_pause(args.pause)
    print("pressed: " + "+".join(keys))


def special_key_code(key: str) -> int:
    codes = {
        "return": 36,
        "tab": 48,
        "space": 49,
        "delete": 51,
        "escape": 53,
        "left arrow": 123,
        "right arrow": 124,
        "down arrow": 125,
        "up arrow": 126,
    }
    return codes[key]


def escape_applescript_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def type_text(args: argparse.Namespace) -> None:
    require_mac("type")
    default_from_profile(args, "interval", "type_interval")
    default_from_profile(args, "pause", "type_pause")
    default_from_profile(args, "paste_threshold", "paste_threshold")
    text = args.text if args.text is not None else sys.stdin.read()
    if args.paste or len(text) >= args.paste_threshold:
        paste_text(text)
    else:
        for char in text:
            if char == "\n":
                osascript('tell application "System Events" to key code 36', check=False)
            else:
                osascript(f'tell application "System Events" to keystroke "{escape_applescript_string(char)}"', check=False)
            time.sleep(max(0, random.gauss(args.interval, args.interval / 4)))
    human_pause(args.pause)
    print(f"typed_chars: {len(text)}")


def paste_text(text: str) -> None:
    require_mac("paste")
    if AppKit is not None:
        pasteboard = AppKit.NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        pasteboard.setString_forType_(text, AppKit.NSPasteboardTypeString)
    else:
        proc = subprocess.run(["pbcopy"], input=text, text=True, check=False)
        if proc.returncode != 0:
            die("pbcopy failed")
    osascript('tell application "System Events" to keystroke "v" using {command down}', check=False)


def current_mouse_location() -> Point:
    if Quartz is not None:
        event = Quartz.CGEventCreate(None)
        loc = Quartz.CGEventGetLocation(event)
        return Point(float(loc.x), float(loc.y))
    if shutil.which("cliclick"):
        result = run(["cliclick", "p:."])
        # cliclick prints e.g. "123,456"
        raw = result.stdout.strip().splitlines()[-1]
        x_str, y_str = raw.split(",", 1)
        return Point(float(x_str), float(y_str))
    return Point(0, 0)


def move_mouse(target: Point, *, duration: float, steps: int) -> None:
    require_mac("mouse movement")
    if Quartz is None and not shutil.which("cliclick"):
        die("mouse actions require PyObjC Quartz or the optional cliclick binary")
    start = current_mouse_location()
    steps = max(1, steps)
    for i in range(1, steps + 1):
        t = i / steps
        eased = 0.5 - math.cos(t * math.pi) / 2
        wobble = math.sin(t * math.pi) * random.uniform(-1.2, 1.2)
        x = start.x + (target.x - start.x) * eased + wobble
        y = start.y + (target.y - start.y) * eased - wobble
        set_mouse_position(Point(x, y))
        time.sleep(max(0, duration / steps))


def set_mouse_position(point: Point) -> None:
    if Quartz is not None:
        event = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventMouseMoved, (point.x, point.y), Quartz.kCGMouseButtonLeft)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
    else:
        run(["cliclick", f"m:{int(point.x)},{int(point.y)}"], check=True)


def post_mouse(kind: str, point: Point, button: str = "left") -> None:
    if Quartz is not None:
        quartz_button = Quartz.kCGMouseButtonLeft if button == "left" else Quartz.kCGMouseButtonRight
        event_types = {
            "down": Quartz.kCGEventLeftMouseDown if button == "left" else Quartz.kCGEventRightMouseDown,
            "up": Quartz.kCGEventLeftMouseUp if button == "left" else Quartz.kCGEventRightMouseUp,
        }
        event = Quartz.CGEventCreateMouseEvent(None, event_types[kind], (point.x, point.y), quartz_button)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
    else:
        action = "c" if button == "left" else "rc"
        if kind == "down":
            run(["cliclick", f"dd:{int(point.x)},{int(point.y)}"], check=True)
        elif kind == "up":
            run(["cliclick", f"du:{int(point.x)},{int(point.y)}"], check=True)
        else:
            run(["cliclick", f"{action}:{int(point.x)},{int(point.y)}"], check=True)


def click(args: argparse.Namespace) -> None:
    require_mac("click")
    default_from_profile(args, "duration", "click_duration")
    default_from_profile(args, "steps", "click_steps")
    default_from_profile(args, "pre_click_pause", "pre_click_pause")
    default_from_profile(args, "pause", "click_pause")
    target = jittered_point(args.x, args.y, args.jitter)
    move_mouse(target, duration=args.duration, steps=args.steps)
    human_pause(args.pre_click_pause)
    for index in range(args.count):
        post_mouse("down", target, args.button)
        time.sleep(random.uniform(0.045, 0.12))
        post_mouse("up", target, args.button)
        if index < args.count - 1:
            time.sleep(random.uniform(0.08, 0.18))
    human_pause(args.pause)
    print(f"clicked: {args.button} {target.x:.0f},{target.y:.0f} count={args.count}")


def drag(args: argparse.Namespace) -> None:
    require_mac("drag")
    default_from_profile(args, "duration", "drag_duration")
    default_from_profile(args, "steps", "drag_steps")
    default_from_profile(args, "pre_click_pause", "pre_click_pause")
    default_from_profile(args, "pause", "click_pause")
    start = jittered_point(args.x1, args.y1, args.jitter)
    end = jittered_point(args.x2, args.y2, args.jitter)
    move_mouse(start, duration=args.duration / 3, steps=max(3, args.steps // 3))
    human_pause(args.pre_click_pause)
    post_mouse("down", start, "left")
    move_mouse(end, duration=args.duration, steps=args.steps)
    post_mouse("up", end, "left")
    human_pause(args.pause)
    print(f"dragged: {start.x:.0f},{start.y:.0f} -> {end.x:.0f},{end.y:.0f}")


def jittered_point(x: float, y: float, jitter: float) -> Point:
    if jitter <= 0:
        return Point(x, y)
    return Point(x + random.uniform(-jitter, jitter), y + random.uniform(-jitter, jitter))


def scroll(args: argparse.Namespace) -> None:
    require_mac("scroll")
    if Quartz is not None:
        event = Quartz.CGEventCreateScrollWheelEvent(None, Quartz.kCGScrollEventUnitLine, 2, int(args.dy), int(args.dx))
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
    elif shutil.which("cliclick"):
        run(["cliclick", f"w:{int(args.dx)},{int(args.dy)}"], check=True)
    else:
        die("scroll requires PyObjC Quartz or cliclick")
    human_pause(args.pause)
    print(f"scrolled: dx={args.dx} dy={args.dy}")


def wait(args: argparse.Namespace) -> None:
    deadline = time.time() + args.seconds
    while time.time() < deadline:
        time.sleep(min(args.poll, max(0, deadline - time.time())))
    print(f"waited: {args.seconds:.2f}s")


def human_pause(base: float) -> None:
    if base > 0:
        time.sleep(max(0, random.gauss(base, base / 5)))


def ui_tree(args: argparse.Namespace) -> None:
    require_mac("ui-tree")
    app = args.app
    if not app:
        result = osascript('tell application "System Events" to get name of first application process whose frontmost is true', check=False)
        if result.returncode != 0:
            die(result.stderr.strip() or "could not find front app")
        app = result.stdout.strip()
    script = r'''
on describeElement(e, depth, maxDepth)
    tell application "System Events"
        set indent to ""
        repeat depth times
            set indent to indent & "  "
        end repeat
        set roleText to ""
        set titleText to ""
        set valueText to ""
        set posText to ""
        set sizeText to ""
        try
            set roleText to role of e as text
        end try
        try
            set titleText to name of e as text
        end try
        try
            set valueText to value of e as text
        end try
        try
            set p to position of e
            set posText to " @" & (item 1 of p as integer) & "," & (item 2 of p as integer)
        end try
        try
            set s to size of e
            set sizeText to " " & (item 1 of s as integer) & "x" & (item 2 of s as integer)
        end try
        set lineText to indent & roleText
        if titleText is not "" then set lineText to lineText & " | " & titleText
        if valueText is not "" then set lineText to lineText & " = " & valueText
        set lineText to lineText & posText & sizeText
        if depth < maxDepth then
            try
                repeat with child in UI elements of e
                    set lineText to lineText & linefeed & my describeElement(child, depth + 1, maxDepth)
                end repeat
            end try
        end if
        return lineText
    end tell
end describeElement

on run argv
    set appName to item 1 of argv
    set maxDepth to item 2 of argv as integer
    tell application "System Events"
        tell process appName
            return my describeElement(window 1, 0, maxDepth)
        end tell
    end tell
end run
'''
    result = osascript(script, app, str(args.depth), check=False)
    if result.returncode != 0:
        die(result.stderr.strip() or "ui-tree failed; Accessibility permission may be missing")
    print(result.stdout.rstrip())


def observe(args: argparse.Namespace) -> None:
    require_mac("observe")
    data = {"front_app": get_front_app(), "screenshot": capture_screenshot(args.out, window=args.window)}
    if args.ui_depth > 0:
        app = args.app or data["front_app"]
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            ui_tree(argparse.Namespace(app=app, depth=args.ui_depth))
        data["ui_tree"] = buffer.getvalue().strip()
    if args.format == "compact":
        compact = {k: v for k, v in data.items() if k != "ui_tree"}
        if "ui_tree" in data:
            compact["ui_tree_lines"] = len(data["ui_tree"].splitlines())
        print(json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def namespace_for_action(action: dict, inherited_profile: str) -> argparse.Namespace:
    name = action.get("action")
    if not name:
        die("batch action missing 'action'")
    common = {"profile": action.get("profile", inherited_profile)}
    if name == "activate":
        return argparse.Namespace(app=action.get("app"), pause=action.get("pause", 0.0), _func=activate)
    if name == "screenshot":
        return argparse.Namespace(out=action.get("out"), window=action.get("window", False), _func=screenshot)
    if name == "observe":
        return argparse.Namespace(out=action.get("out"), window=action.get("window", False), app=action.get("app"), ui_depth=action.get("ui_depth", 0), format=action.get("format", "compact"), _func=observe)
    if name == "hotkey":
        return argparse.Namespace(keys=action.get("keys", []), pause=action.get("pause", 0.0), _func=hotkey)
    if name == "type":
        return argparse.Namespace(text=action.get("text"), paste=action.get("paste", False), interval=action.get("interval"), paste_threshold=action.get("paste_threshold"), pause=action.get("pause"), _func=type_text, **common)
    if name == "click":
        return argparse.Namespace(x=action.get("x"), y=action.get("y"), button=action.get("button", "left"), count=action.get("count", 1), jitter=action.get("jitter", 3.0), duration=action.get("duration"), steps=action.get("steps"), pre_click_pause=action.get("pre_click_pause"), pause=action.get("pause"), _func=click, **common)
    if name == "drag":
        return argparse.Namespace(x1=action.get("x1"), y1=action.get("y1"), x2=action.get("x2"), y2=action.get("y2"), jitter=action.get("jitter", 2.0), duration=action.get("duration"), steps=action.get("steps"), pre_click_pause=action.get("pre_click_pause"), pause=action.get("pause"), _func=drag, **common)
    if name == "scroll":
        return argparse.Namespace(dx=action.get("dx", 0), dy=action.get("dy"), pause=action.get("pause", 0.0), _func=scroll)
    if name == "wait":
        return argparse.Namespace(seconds=action.get("seconds"), poll=action.get("poll", 0.1), _func=wait)
    die(f"unsupported batch action: {name}")


def batch(args: argparse.Namespace) -> None:
    source = Path(args.file).read_text() if args.file else sys.stdin.read()
    actions = json.loads(source)
    if not isinstance(actions, list):
        die("batch input must be a JSON array")
    completed = []
    for index, action in enumerate(actions, 1):
        if not isinstance(action, dict):
            die(f"batch item {index} is not an object")
        ns = namespace_for_action(action, args.profile)
        name = action.get("action")
        if args.compact:
            with contextlib.redirect_stdout(io.StringIO()):
                ns._func(ns)
        else:
            ns._func(ns)
        completed.append(name)
    if args.compact:
        print(json.dumps({"ok": True, "count": len(completed), "actions": completed}, separators=(",", ":")))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Human-like macOS GUI automation helper for OpenClaw agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              macos_human_operator.py preflight
              macos_human_operator.py observe --out /tmp/screen.png --ui-depth 2 --format compact
              macos_human_operator.py batch --profile fast --file /tmp/actions.json
              macos_human_operator.py click --profile careful --x 500 --y 300 --jitter 1
              macos_human_operator.py type --profile fast --text "Hello"
              macos_human_operator.py hotkey --keys command s
            """
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("preflight", help="print environment and permission guidance").set_defaults(func=preflight)
    sub.add_parser("front-app", help="print the frontmost app").set_defaults(func=front_app)

    p = sub.add_parser("observe", help="capture screenshot plus optional front app/UI tree in one compact call")
    p.add_argument("--out", help="output PNG path; default is a temporary file")
    p.add_argument("--window", action="store_true", help="interactive selected-window capture")
    p.add_argument("--app", help="app for UI tree; defaults to frontmost app")
    p.add_argument("--ui-depth", type=int, default=0, help="include Accessibility tree up to this depth")
    p.add_argument("--format", choices=["compact", "json"], default="compact")
    p.set_defaults(func=observe)

    p = sub.add_parser("batch", help="run JSON action array in one process to reduce shell calls/output")
    p.add_argument("--file", help="JSON file; stdin is used when omitted")
    p.add_argument("--profile", choices=["fast", "balanced", "careful"], default="balanced")
    p.add_argument("--verbose", action="store_false", dest="compact", default=True, help="show per-action output instead of one compact summary")
    p.set_defaults(func=batch)

    p = sub.add_parser("screenshot", help="capture a screenshot with screencapture")
    p.add_argument("--out", help="output PNG path; default is a temporary file")
    p.add_argument("--window", action="store_true", help="interactive selected-window capture")
    p.set_defaults(func=screenshot)

    p = sub.add_parser("activate", help="bring an app to the foreground")
    p.add_argument("--app", required=True, help="macOS application name")
    p.add_argument("--pause", type=float, default=0.35)
    p.set_defaults(func=activate)

    p = sub.add_parser("ui-tree", help="print Accessibility tree for the front window")
    p.add_argument("--app", help="application name; defaults to frontmost app")
    p.add_argument("--depth", type=int, default=3, help="maximum child depth")
    p.set_defaults(func=ui_tree)

    p = sub.add_parser("click", help="humanized mouse click")
    p.add_argument("--profile", choices=["fast", "balanced", "careful"], default="balanced")
    p.add_argument("--x", type=float, required=True)
    p.add_argument("--y", type=float, required=True)
    p.add_argument("--button", choices=["left", "right"], default="left")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--jitter", type=float, default=3.0)
    p.add_argument("--duration", type=float)
    p.add_argument("--steps", type=int)
    p.add_argument("--pre-click-pause", type=float)
    p.add_argument("--pause", type=float)
    p.set_defaults(func=click)

    p = sub.add_parser("drag", help="humanized mouse drag")
    p.add_argument("--profile", choices=["fast", "balanced", "careful"], default="balanced")
    p.add_argument("--x1", type=float, required=True)
    p.add_argument("--y1", type=float, required=True)
    p.add_argument("--x2", type=float, required=True)
    p.add_argument("--y2", type=float, required=True)
    p.add_argument("--jitter", type=float, default=2.0)
    p.add_argument("--duration", type=float)
    p.add_argument("--steps", type=int)
    p.add_argument("--pre-click-pause", type=float)
    p.add_argument("--pause", type=float)
    p.set_defaults(func=drag)

    p = sub.add_parser("scroll", help="scroll by line units")
    p.add_argument("--dx", type=int, default=0)
    p.add_argument("--dy", type=int, required=True, help="positive/negative line delta")
    p.add_argument("--pause", type=float, default=0.25)
    p.set_defaults(func=scroll)

    p = sub.add_parser("type", help="type or paste text into focused control")
    p.add_argument("--profile", choices=["fast", "balanced", "careful"], default="balanced")
    p.add_argument("--text", help="text to enter; stdin is used when omitted")
    p.add_argument("--interval", type=float, help="mean seconds between typed characters")
    p.add_argument("--paste", action="store_true", help="paste via clipboard instead of per-character typing")
    p.add_argument("--paste-threshold", type=int, help="auto-paste text at or above this length")
    p.add_argument("--pause", type=float)
    p.set_defaults(func=type_text)

    p = sub.add_parser("hotkey", help="press a keyboard shortcut")
    p.add_argument("--keys", nargs="+", required=True, help="e.g. command s or command shift g")
    p.add_argument("--pause", type=float, default=0.2)
    p.set_defaults(func=hotkey)

    p = sub.add_parser("wait", help="human-readable wait helper")
    p.add_argument("--seconds", type=float, required=True)
    p.add_argument("--poll", type=float, default=0.1)
    p.set_defaults(func=wait)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
