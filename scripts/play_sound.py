#!/usr/bin/env python3
"""
Play sound notifications for Claude Code hooks.

Usage:
    play_sound.py              # completion sound (Glass/Ding)
    play_sound.py attention    # attention sound (Frog/Exclamation)
    play_sound.py /path/to.wav # custom sound file
"""

import sys

from sound_player import SOUNDS, get_sound, play_sound


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "completion"

    # Check if it's a known sound type or a file path
    if arg in SOUNDS:
        sound_file = get_sound(arg)
    else:
        sound_file = arg  # Treat as custom file path

    play_sound(sound_file)
