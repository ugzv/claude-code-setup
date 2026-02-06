#!/usr/bin/env python3
"""
Shared sound player module for Claude Code hooks.
Cross-platform: macOS (afplay) and Windows (winsound).
"""

import subprocess
from typing import Optional

from lib.platform_detection import IS_MACOS, IS_WINDOWS


# Sound definitions by type and platform
SOUNDS = {
    "completion": {
        "Darwin": "/System/Library/Sounds/Glass.aiff",
        "Windows": r"C:\Windows\Media\Windows Ding.wav",
    },
    "attention": {
        "Darwin": "/System/Library/Sounds/Frog.aiff",
        "Windows": r"C:\Windows\Media\Windows Exclamation.wav",
    },
}


def get_sound(sound_type: str) -> Optional[str]:
    """Get sound file path for the given type and current platform."""
    if IS_MACOS:
        return SOUNDS.get(sound_type, {}).get("Darwin")
    elif IS_WINDOWS:
        return SOUNDS.get(sound_type, {}).get("Windows")
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
    """Play a sound file using Windows winsound or PowerShell."""
    try:
        import winsound
        winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        try:
            subprocess.Popen(
                [
                    "powershell.exe", "-WindowStyle", "Hidden", "-Command",
                    f'(New-Object Media.SoundPlayer "{sound_file}").PlaySync()'
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception:
            pass


def play_sound(sound_file: str) -> None:
    """Play a sound file using platform-appropriate method."""
    if sound_file is None:
        return

    try:
        if IS_MACOS:
            play_sound_macos(sound_file)
        elif IS_WINDOWS:
            play_sound_windows(sound_file)
    except Exception:
        pass
