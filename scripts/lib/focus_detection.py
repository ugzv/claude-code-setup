"""
Terminal focus detection helpers.
"""

from __future__ import annotations

import subprocess

from .platform_runtime import IS_MACOS, IS_WINDOWS

if IS_WINDOWS:
    import ctypes
    import ctypes.wintypes


def is_terminal_focused_macos() -> bool:
    """Check if a terminal or editor-with-terminal is frontmost on macOS."""
    try:
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=0.5,
            stdin=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            frontmost_app = result.stdout.strip().lower()
            terminal_apps = [
                "terminal",
                "iterm",
                "iterm2",
                "cursor",
                "stable",
                "windsurf",
                "antigravity",
                "visual studio code",
                "code",
                "warp",
                "alacritty",
                "kitty",
                "hyper",
            ]
            return any(app in frontmost_app for app in terminal_apps)
    except Exception:
        pass
    return False


def _get_foreground_process_name_windows() -> str:
    """Return the lowercase name of the foreground Windows process."""
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""

        pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return ""

        process_query_limited_information = 0x1000
        handle = kernel32.OpenProcess(process_query_limited_information, False, pid.value)
        if not handle:
            return ""

        try:
            buf = ctypes.create_unicode_buffer(260)
            buf_size = ctypes.wintypes.DWORD(260)
            success = kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(buf_size))
            if success:
                name = buf.value.rsplit("\\", 1)[-1]
                if "." in name:
                    name = name.rsplit(".", 1)[0]
                return name.lower()
        finally:
            kernel32.CloseHandle(handle)
    except Exception:
        pass
    return ""


WINDOWS_TERMINAL_PROCESSES = {
    "windowsterminal",
    "cmd",
    "powershell",
    "pwsh",
    "code",
    "cursor",
    "windsurf",
    "antigravity",
    "conhost",
    "alacritty",
    "wezterm",
    "hyper",
}


def is_terminal_focused_windows() -> bool:
    """Check if a terminal or editor is frontmost on Windows."""
    process_name = _get_foreground_process_name_windows()
    return bool(process_name) and process_name in WINDOWS_TERMINAL_PROCESSES


def is_terminal_focused() -> bool:
    """Check if a terminal or editor with terminal is currently focused."""
    if IS_MACOS:
        return is_terminal_focused_macos()
    if IS_WINDOWS:
        return is_terminal_focused_windows()
    return False
