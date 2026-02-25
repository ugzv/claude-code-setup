#!/usr/bin/env python3
"""
Shared sound player module for Claude Code hooks.
Cross-platform: macOS (afplay), Windows (winsound), and WSL (powershell.exe).
"""

import subprocess
from typing import Optional

from lib.platform_detection import (
    IS_MACOS, IS_WINDOWS, USES_WINDOWS_GUI,
    run_powershell,
)


# Sound definitions by type and platform
SOUNDS = {
    "completion": {
        "macos": "/System/Library/Sounds/Glass.aiff",
        "windows": r"C:\Windows\Media\Windows Ding.wav",
    },
    "attention": {
        "macos": "/System/Library/Sounds/Frog.aiff",
        "windows": r"C:\Windows\Media\Windows Exclamation.wav",
    },
}


def get_sound(sound_type: str) -> Optional[str]:
    """Get sound file path for the given type and current platform."""
    if IS_MACOS:
        return SOUNDS.get(sound_type, {}).get("macos")
    elif USES_WINDOWS_GUI:
        # WSL uses Windows sound paths since powershell.exe plays them
        return SOUNDS.get(sound_type, {}).get("windows")
    return None


def play_sound_macos(sound_file: str) -> None:
    """Play a sound file using macOS afplay."""
    subprocess.Popen(
        ["afplay", sound_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True
    )


def play_sound_windows(sound_file: str) -> None:
    """Play a sound file using Windows winsound or PowerShell.
    On WSL, winsound is unavailable so we go straight to PowerShell."""
    if IS_WINDOWS:
        try:
            import winsound
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        except Exception:
            pass
    # PowerShell fallback (also the primary path on WSL)
    try:
        ps_script = f'(New-Object Media.SoundPlayer "{sound_file}").PlaySync()'
        run_powershell(ps_script, fire_and_forget=True)
    except Exception:
        pass


def play_sound(sound_file: str) -> None:
    """Play a sound file using platform-appropriate method."""
    if sound_file is None:
        return

    try:
        if IS_MACOS:
            play_sound_macos(sound_file)
        elif USES_WINDOWS_GUI:
            play_sound_windows(sound_file)
    except Exception:
        pass
