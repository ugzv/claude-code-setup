"""Platform dependency installation (brew / apt-get helpers)."""

import subprocess

from .platform import IS_WINDOWS, IS_MACOS, IS_WSL


def _check_and_brew_install(package: str, dry_run: bool, required: bool = False) -> None:
    """Check if a package is installed, install via brew if not."""
    result = subprocess.run(["which", package], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  {package} already installed")
        return

    # Check if brew is available
    result = subprocess.run(["which", "brew"], capture_output=True, text=True)
    if result.returncode != 0:
        label = "required" if required else "optional"
        print(f"  {package} not found ({label})")
        print(f"  Install with: brew install {package}")
        return

    if dry_run:
        print(f"  Would install: {package} (via brew)")
    else:
        print(f"  Installing {package}...")
        result = subprocess.run(
            ["brew", "install", package],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  {package} installed")
        else:
            print(f"  Failed to install {package}")
            print(f"  Error: {result.stderr.strip()}")


def install_macos_deps(dry_run: bool = False) -> None:
    """Install macOS dependencies: jq (statusline) and terminal-notifier (notifications)."""
    if not IS_MACOS:
        return
    _check_and_brew_install("jq", dry_run, required=True)
    _check_and_brew_install("terminal-notifier", dry_run)


def install_wsl_deps(dry_run: bool = False) -> None:
    """Install jq on WSL/Linux if not present, with optional Linux desktop deps."""
    if IS_WINDOWS or IS_MACOS:
        return

    result = subprocess.run(["which", "jq"], capture_output=True, text=True)
    if result.returncode == 0:
        print("  jq already installed")
    else:
        if dry_run:
            print("  Would install: jq (via apt-get)")
        else:
            print("  Installing jq (required for statusline)...")
            result = subprocess.run(
                ["sudo", "apt-get", "install", "-y", "jq"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                print("  jq installed")
            else:
                print("  Failed to install jq (statusline won't work)")
                print("  Install manually: sudo apt-get install jq")

    if IS_WSL:
        return

    optional_linux_tools = (
        ("notify-send", "libnotify-bin", "desktop notifications"),
        ("paplay", "pulseaudio-utils", "sound playback"),
    )
    for binary, package, label in optional_linux_tools:
        result = subprocess.run(["which", binary], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  {binary} already installed")
            continue
        if dry_run:
            print(f"  Would install: {package} (optional for {label})")
            continue
        print(f"  {binary} not found (optional for {label})")
        print(f"  Install manually: sudo apt-get install {package}")
