"""
Low-level runtime environment helpers for hook scripts.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Use sys.platform instead of platform.system() because platform.system()
# can trigger WMI deadlocks on Windows with newer Python runtimes.
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

IS_WSL = False
if sys.platform == "linux":
    try:
        IS_WSL = "microsoft" in Path("/proc/version").read_text().lower()
    except Exception:
        pass

USES_WINDOWS_GUI = IS_WINDOWS or IS_WSL

POWERSHELL_EXE = "powershell.exe"
if IS_WSL:
    _ps_candidates = [
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
        "/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe",
    ]
    for _candidate in _ps_candidates:
        if Path(_candidate).exists():
            POWERSHELL_EXE = _candidate
            break

_LIB_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _LIB_DIR.parent
CLI_HOME = _SCRIPTS_DIR.parent
CLI_NAME = "Codex CLI" if CLI_HOME.name == ".codex" else "Claude Code"

DEBUG_LOG_PATH = CLI_HOME / "notification_debug.log"
DEBUG_ENABLED = os.environ.get("CLAUDE_HOOKS_DEBUG", "").lower() in ("1", "true", "yes")


def log_debug(message: str, *, path: Optional[str] = None) -> None:
    """Silently append to the debug log if debug logging is enabled."""
    if not DEBUG_ENABLED:
        return
    try:
        target = path or DEBUG_LOG_PATH
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(f"{message}\n")
    except Exception:
        pass


def get_windows_subprocess_kwargs() -> dict:
    """Return subprocess kwargs for hiding the console window on Windows."""
    if IS_WINDOWS:
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def run_powershell(
    script: str,
    *,
    timeout: int = 5,
    fire_and_forget: bool = False,
) -> subprocess.CompletedProcess[str] | None:
    """Run a PowerShell script hidden, returning a result unless detached."""
    cmd = [POWERSHELL_EXE, "-WindowStyle", "Hidden", "-Command", script]
    kwargs = get_windows_subprocess_kwargs()
    if fire_and_forget:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            **kwargs,
        )
        return None

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        stdin=subprocess.DEVNULL,
        **kwargs,
    )


def run_quiet(
    cmd: list[str],
    *,
    timeout: int | None = None,
) -> tuple[bool, str]:
    """Run a command quietly, returning (success, stripped_stdout)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception:
        return False, ""
