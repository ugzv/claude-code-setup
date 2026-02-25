"""
Platform detection utilities for Claude Code and Codex CLI hooks.
Handles terminal focus detection and terminal app identification.
Cross-platform: macOS, Windows, and WSL.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# =============================================================================
# Platform Constants
# =============================================================================

# Use sys.platform instead of platform.system() — the platform module calls
# uname() which makes WMI calls on Windows that can deadlock (Python 3.13+).
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

# WSL detection: /proc/version contains "microsoft" on both WSL1 and WSL2
IS_WSL = False
if sys.platform == "linux":
    try:
        IS_WSL = "microsoft" in Path("/proc/version").read_text().lower()
    except Exception:
        pass

# Gate for routing to Windows GUI code (toast notifications, sounds via powershell.exe)
USES_WINDOWS_GUI = IS_WINDOWS or IS_WSL

# Resolve powershell.exe — on WSL with appendWindowsPath=false it won't be on PATH
POWERSHELL_EXE = "powershell.exe"
if IS_WSL:
    _ps_candidates = [
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
        "/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe",
    ]
    for _p in _ps_candidates:
        if Path(_p).exists():
            POWERSHELL_EXE = _p
            break

if IS_WINDOWS:
    import ctypes
    import ctypes.wintypes

# Derive CLI home from script location: lib/ -> scripts/ -> ~/.claude/ or ~/.codex/
_LIB_DIR = Path(__file__).resolve().parent          # .../scripts/lib/
_SCRIPTS_DIR = _LIB_DIR.parent                       # .../scripts/
CLI_HOME = _SCRIPTS_DIR.parent                        # ~/.claude/ or ~/.codex/
CLI_NAME = "Codex CLI" if CLI_HOME.name == ".codex" else "Claude Code"

# Debug logging (off by default, enable with CLAUDE_HOOKS_DEBUG=1)
DEBUG_LOG_PATH = CLI_HOME / "notification_debug.log"
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


def get_windows_subprocess_kwargs() -> dict:
    """Return subprocess kwargs for hiding the console window.
    On native Windows: {creationflags: CREATE_NO_WINDOW}.
    On WSL: {} (Linux subprocess doesn't support creationflags)."""
    if IS_WINDOWS:
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


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


def _get_foreground_process_name_windows() -> str:
    """Get the process name of the foreground window using ctypes (~1ms).
    Returns lowercase process name without extension, or empty string on failure."""
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""

        # Get the process ID from the window handle
        pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return ""

        # Open the process and query its image name
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        if not handle:
            return ""

        try:
            buf = ctypes.create_unicode_buffer(260)
            buf_size = ctypes.wintypes.DWORD(260)
            success = kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(buf_size))
            if success:
                # Extract filename without extension
                path = buf.value
                name = path.rsplit("\\", 1)[-1]
                if "." in name:
                    name = name.rsplit(".", 1)[0]
                return name.lower()
        finally:
            kernel32.CloseHandle(handle)
    except Exception:
        pass
    return ""


# Process names that indicate a terminal/editor is focused
WINDOWS_TERMINAL_PROCESSES = {
    "windowsterminal", "cmd", "powershell", "pwsh",
    "code", "cursor", "windsurf", "antigravity",
    "conhost", "alacritty", "wezterm", "hyper",
}


def is_terminal_focused_windows() -> bool:
    """Check if terminal or editor is currently focused (Windows).
    Uses ctypes for ~1ms performance instead of PowerShell ~500ms."""
    process_name = _get_foreground_process_name_windows()
    if not process_name:
        return False
    return process_name in WINDOWS_TERMINAL_PROCESSES


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


def _get_parent_process_names_windows() -> list:
    """Walk the process tree upward using ctypes (~5ms).
    Returns list of lowercase process names from current PID to root."""
    names = []
    try:
        kernel32 = ctypes.windll.kernel32

        # Snapshot all processes
        TH32CS_SNAPPROCESS = 0x00000002
        snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
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
            # Build pid -> (parent_pid, exe_name) map
            pid_map = {}
            entry = PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)

            if kernel32.Process32FirstW(snap, ctypes.byref(entry)):
                while True:
                    exe = entry.szExeFile
                    if "." in exe:
                        exe = exe.rsplit(".", 1)[0]
                    pid_map[entry.th32ProcessID] = (entry.th32ParentProcessID, exe.lower())
                    if not kernel32.Process32NextW(snap, ctypes.byref(entry)):
                        break
        finally:
            kernel32.CloseHandle(snap)

        # Walk up from our PID
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


def _detect_terminal_from_env() -> Optional[tuple]:
    """Detect terminal app from environment variables (0ms, works on Windows and WSL).
    Returns (app_display_name, emoji, app_name) or None if not detected."""
    term_program = os.environ.get("TERM_PROGRAM", "").lower()
    wt_session = os.environ.get("WT_SESSION", "")

    # Editor-specific env vars
    if os.environ.get("CURSOR_TRACE_DIR"):
        return ("Cursor", "💠", "Cursor")
    if any(os.environ.get(v) for v in ("VSCODE_PID", "VSCODE_IPC_HOOK_CLI")):
        # Could be VSCode or Cursor — TERM_PROGRAM disambiguates
        if "cursor" in term_program:
            return ("Cursor", "💠", "Cursor")
        return ("VSCode", "📟", "Code")

    for key, info in WINDOWS_APP_INFO.items():
        if key in term_program:
            return info

    if wt_session:
        return ("Windows Terminal", "💻", "WindowsTerminal")

    return None


def get_terminal_app_windows() -> tuple:
    """Detect which terminal/editor app Claude Code is running in (Windows).
    Returns (app_display_name, emoji, app_name) tuple.
    Uses env vars first (0ms), then ctypes process tree (~5ms)."""

    # 1. Environment variable heuristics (instant, most reliable)
    env_result = _detect_terminal_from_env()
    if env_result:
        return env_result

    # 2. ctypes process tree walk (~5ms, no subprocess)
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


def get_terminal_app_wsl() -> tuple:
    """Detect which terminal/editor app Claude Code is running in (WSL).
    Returns (app_display_name, emoji, app_name) tuple.
    Uses env vars (inherited from host Windows terminal)."""
    env_result = _detect_terminal_from_env()
    if env_result:
        return env_result
    return ("Terminal", "🖥️", "")


def get_terminal_app() -> tuple:
    """Detect which terminal/editor app Claude Code is running in.
    Returns (app_display_name, emoji, app_name) tuple."""
    if IS_MACOS:
        return get_terminal_app_macos()
    elif IS_WSL:
        return get_terminal_app_wsl()
    elif IS_WINDOWS:
        return get_terminal_app_windows()
    return ("Terminal", "🖥️", "")
