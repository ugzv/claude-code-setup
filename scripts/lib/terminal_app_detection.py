"""
Terminal app detection helpers for notifications.
"""

from __future__ import annotations

import os
import subprocess
from typing import Optional

from .platform_runtime import IS_MACOS, IS_WINDOWS, IS_WSL

if IS_WINDOWS:
    import ctypes
    import ctypes.wintypes


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


def get_terminal_app_macos() -> tuple[str, str, str]:
    """Detect which terminal or editor app is hosting the current process."""
    try:
        pid = os.getpid()
        for _ in range(10):
            result = subprocess.run(
                ["ps", "-o", "ppid=,comm=", "-p", str(pid)],
                capture_output=True,
                text=True,
                timeout=0.5,
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
            for app_key, app_info in MACOS_APP_INFO.items():
                if app_key in comm:
                    if app_key == "stable" and "warp" in comm:
                        continue
                    return app_info

            pid = int(ppid)
            if pid <= 1:
                break
    except Exception:
        pass

    return ("Terminal", "🖥️", "Terminal")


def _get_parent_process_names_windows() -> list[str]:
    """Walk the Windows process tree upward and return lowercase names."""
    names: list[str] = []
    try:
        kernel32 = ctypes.windll.kernel32

        th32cs_snprocess = 0x00000002
        snap = kernel32.CreateToolhelp32Snapshot(th32cs_snprocess, 0)
        if snap == ctypes.wintypes.HANDLE(-1).value:
            return names

        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.wintypes.DWORD),
                ("cntUsage", ctypes.wintypes.DWORD),
                ("th32ProcessID", ctypes.wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                ("th32ModuleID", ctypes.wintypes.DWORD),
                ("cntThreads", ctypes.wintypes.DWORD),
                ("th32ParentProcessID", ctypes.wintypes.DWORD),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", ctypes.wintypes.DWORD),
                ("szExeFile", ctypes.c_wchar * 260),
            ]

        try:
            pid_map = {}
            entry = PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)

            if kernel32.Process32FirstW(snap, ctypes.byref(entry)):
                while True:
                    exe = entry.szExeFile
                    if "." in exe:
                        exe = exe.rsplit(".", 1)[0]
                    pid_map[entry.th32ProcessID] = (
                        entry.th32ParentProcessID,
                        exe.lower(),
                    )
                    if not kernel32.Process32NextW(snap, ctypes.byref(entry)):
                        break
        finally:
            kernel32.CloseHandle(snap)

        current_pid = os.getpid()
        visited = set()
        while current_pid and current_pid not in visited:
            visited.add(current_pid)
            if current_pid not in pid_map:
                break
            parent_pid, exe_name = pid_map[current_pid]
            names.append(exe_name)
            current_pid = parent_pid
    except Exception:
        pass
    return names


def _detect_terminal_from_env() -> Optional[tuple[str, str, str]]:
    """Detect the hosting terminal/editor from inherited environment variables."""
    term_program = os.environ.get("TERM_PROGRAM", "").lower()
    wt_session = os.environ.get("WT_SESSION", "")

    if os.environ.get("CURSOR_TRACE_DIR"):
        return ("Cursor", "💠", "Cursor")

    if any(os.environ.get(var) for var in ("VSCODE_PID", "VSCODE_IPC_HOOK_CLI")):
        if "cursor" in term_program:
            return ("Cursor", "💠", "Cursor")
        return ("VSCode", "📟", "Code")

    for key, info in WINDOWS_APP_INFO.items():
        if key in term_program:
            return info

    if wt_session:
        return ("Windows Terminal", "💻", "WindowsTerminal")

    return None


def get_terminal_app_windows() -> tuple[str, str, str]:
    """Detect the hosting terminal/editor app on Windows."""
    env_result = _detect_terminal_from_env()
    if env_result:
        return env_result

    parent_names = _get_parent_process_names_windows()
    for name in parent_names:
        if "cursor" in name:
            return ("Cursor", "💠", "Cursor")
        if name == "code" or "visual studio code" in name:
            return ("VSCode", "📟", "Code")
        if "windsurf" in name:
            return ("Windsurf", "🌊", "Windsurf")
        if "antigravity" in name:
            return ("Antigravity", "🚀", "Antigravity")
        if "windowsterminal" in name:
            return ("Windows Terminal", "💻", "WindowsTerminal")
        if name in ("powershell", "pwsh"):
            return ("PowerShell", "🔷", "PowerShell")
        if name == "cmd":
            return ("CMD", "🖥️", "cmd")

    return ("Terminal", "🖥️", "cmd")


def get_terminal_app_wsl() -> tuple[str, str, str]:
    """Detect the hosting terminal/editor app when running inside WSL."""
    env_result = _detect_terminal_from_env()
    if env_result:
        return env_result
    return ("Terminal", "🖥️", "")


def get_terminal_app() -> tuple[str, str, str]:
    """Detect which terminal/editor app is hosting the current process."""
    if IS_MACOS:
        return get_terminal_app_macos()
    if IS_WSL:
        return get_terminal_app_wsl()
    if IS_WINDOWS:
        return get_terminal_app_windows()
    return ("Terminal", "🖥️", "")
