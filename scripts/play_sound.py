#!/usr/bin/env python3
"""
Play sound notifications for Claude Code hooks.

Usage:
    play_sound.py              # completion sound (Glass/Ding)
    play_sound.py attention    # attention sound (Frog/Exclamation)
    play_sound.py /path/to.wav # custom sound file
"""

import sys
from typing import Optional

from sound_player import IS_MACOS, IS_WINDOWS, play_sound

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


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "completion"

    # Check if it's a known sound type or a file path
    if arg in SOUNDS:
        sound_file = get_sound(arg)
    else:
        sound_file = arg  # Treat as custom file path

    play_sound(sound_file)
