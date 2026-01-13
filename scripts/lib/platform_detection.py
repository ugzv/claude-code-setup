"""
Platform detection utilities for Claude Code hooks.
Handles terminal focus detection and terminal app identification.
Cross-platform: macOS and Windows.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

# =============================================================================
# Platform Constants
# =============================================================================

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"

# Debug logging (off by default, enable with CLAUDE_HOOKS_DEBUG=1)
DEBUG_LOG_PATH = Path.home() / ".claude" / "notification_debug.log"
DEBUG_ENABLED = os.environ.get("CLAUDE_HOOKS_DEBUG", "").lower() in ("1", "true", "yes")


def log_debug(message: str, *, path: Optional[str] = None) -> None:
    """Silently append to debug log if DEBUG_ENABLED. Never raises."""
    if not DEBUG_ENABLED:
        return
    try:
        target = path or DEBUG_LOG_PATH
        with open(target, "a") as f:
            f.write(f"{message}\n")
    except Exception:
        pass


# =============================================================================
# Terminal Focus Detection
# =============================================================================

def is_terminal_focused_macos() -> bool:
    """Check if terminal or editor with terminal is currently focused (macOS)."""
    try:
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=0.5,
            stdin=subprocess.DEVNULL
        )

        if result.returncode == 0:
            frontmost_app = result.stdout.strip().lower()
            terminal_apps = [
                "terminal", "iterm", "iterm2", "cursor", "stable",
                "windsurf", "antigravity", "visual studio code", "code",
                "warp", "alacritty", "kitty", "hyper"
            ]
            return any(app in frontmost_app for app in terminal_apps)
    except Exception:
        pass
    return False


def is_terminal_focused_windows() -> bool:
    """Check if terminal or editor is currently focused (Windows)."""
    try:
        # Use PowerShell to get foreground window title
        result = subprocess.run(
            [
                "powershell.exe", "-WindowStyle", "Hidden", "-Command",
                "(Get-Process | Where-Object {$_.MainWindowHandle -eq "
                "(Add-Type -MemberDefinition '[DllImport(\"user32.dll\")] "
                "public static extern IntPtr GetForegroundWindow();' "
                "-Name Win32 -PassThru)::GetForegroundWindow()}).ProcessName"
            ],
            capture_output=True,
            text=True,
            timeout=1.0,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            process_name = result.stdout.strip().lower()
            terminal_apps = [
                "windowsterminal", "cmd", "powershell", "pwsh",
                "code", "cursor", "windsurf", "antigravity",
                "conhost", "alacritty", "wezterm", "hyper"
            ]
            return any(app in process_name for app in terminal_apps)
    except Exception:
        pass
    return False


def is_terminal_focused() -> bool:
    """Check if terminal or editor with terminal is currently focused."""
    if IS_MACOS:
        return is_terminal_focused_macos()
    elif IS_WINDOWS:
        return is_terminal_focused_windows()
    return False


# =============================================================================
# Terminal App Detection
# =============================================================================

# App info mapping: key -> (display_name, emoji, app_name_for_activation)
MACOS_APP_INFO = {
    "antigravity": ("Antigravity", "🚀", "Antigravity"),
    "cursor": ("Cursor", "💠", "Cursor"),
    "stable": ("Cursor", "💠", "Cursor"),
    "windsurf": ("Windsurf", "🌊", "Windsurf"),
    "codeium": ("Windsurf", "🌊", "Windsurf"),
    "warp": ("Warp", "💻", "Warp"),
    "iterm2": ("iTerm", "🔷", "iTerm"),
    "iterm": ("iTerm", "🔷", "iTerm"),
    "code": ("VSCode", "📟", "Visual Studio Code"),
    "visual studio code": ("VSCode", "📟", "Visual Studio Code"),
    "terminal": ("Terminal", "🖥️", "Terminal"),
}

WINDOWS_APP_INFO = {
    "vscode": ("VSCode", "📟", "Code"),
    "cursor": ("Cursor", "💠", "Cursor"),
    "windsurf": ("Windsurf", "🌊", "Windsurf"),
    "antigravity": ("Antigravity", "🚀", "Antigravity"),
}


def get_terminal_app_macos() -> tuple:
    """Detect which terminal/editor app Claude Code is running in (macOS).
    Returns (app_display_name, emoji, app_name_for_activation) tuple."""

    try:
        pid = os.getpid()
        for _ in range(10):
            result = subprocess.run(
                ["ps", "-o", "ppid=,comm=", "-p", str(pid)],
                capture_output=True,
                text=True,
                timeout=0.5
            )

            if result.returncode != 0:
                break

            output = result.stdout.strip()
            if not output:
                break

            parts = output.split(None, 1)
            if len(parts) < 2:
                break

            ppid, comm = parts[0], parts[1].lower()

            for app_key, (app_display_name, emoji, app_name) in MACOS_APP_INFO.items():
                if app_key in comm:
                    if app_key == "stable" and "warp" in comm:
                        continue
                    return (app_display_name, emoji, app_name)

            pid = int(ppid)
            if pid <= 1:
                break

    except Exception:
        pass

    return ("Terminal", "🖥️", "Terminal")


def get_terminal_app_windows() -> tuple:
    """Detect which terminal/editor app Claude Code is running in (Windows).
    Returns (app_display_name, emoji, app_name) tuple."""

    # Check environment variables first (most reliable)
    term_program = os.environ.get("TERM_PROGRAM", "").lower()
    wt_session = os.environ.get("WT_SESSION", "")  # Windows Terminal

    # Check TERM_PROGRAM
    for key, info in WINDOWS_APP_INFO.items():
        if key in term_program:
            return info

    # Windows Terminal detected
    if wt_session:
        return ("Windows Terminal", "💻", "WindowsTerminal")

    # Try to detect via process tree using PowerShell
    try:
        result = subprocess.run(
            [
                "powershell.exe", "-WindowStyle", "Hidden", "-Command",
                "$p = Get-Process -Id $PID; "
                "while ($p.Parent) { $p = $p.Parent; $p.ProcessName }"
            ],
            capture_output=True,
            text=True,
            timeout=1.0,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            process_names = result.stdout.lower()

            if "cursor" in process_names:
                return ("Cursor", "💠", "Cursor")
            elif "code" in process_names:
                return ("VSCode", "📟", "Code")
            elif "windsurf" in process_names:
                return ("Windsurf", "🌊", "Windsurf")
            elif "antigravity" in process_names:
                return ("Antigravity", "🚀", "Antigravity")
            elif "windowsterminal" in process_names:
                return ("Windows Terminal", "💻", "WindowsTerminal")
            elif "powershell" in process_names or "pwsh" in process_names:
                return ("PowerShell", "🔷", "PowerShell")
            elif "cmd" in process_names:
                return ("CMD", "🖥️", "cmd")

    except Exception:
        pass

    return ("Terminal", "🖥️", "cmd")


def get_terminal_app() -> tuple:
    """Detect which terminal/editor app Claude Code is running in.
    Returns (app_display_name, emoji, app_name) tuple."""
    if IS_MACOS:
        return get_terminal_app_macos()
    elif IS_WINDOWS:
        return get_terminal_app_windows()
    return ("Terminal", "🖥️", "")
