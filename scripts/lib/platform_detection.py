"""
Compatibility facade for runtime platform helpers.
"""

from .focus_detection import (
    WINDOWS_TERMINAL_PROCESSES,
    is_terminal_focused,
    is_terminal_focused_macos,
    is_terminal_focused_windows,
)
from .platform_runtime import (
    CLI_HOME,
    CLI_NAME,
    DEBUG_ENABLED,
    DEBUG_LOG_PATH,
    IS_MACOS,
    IS_WINDOWS,
    IS_WSL,
    POWERSHELL_EXE,
    USES_WINDOWS_GUI,
    get_windows_subprocess_kwargs,
    log_debug,
    run_powershell,
    run_quiet,
)
from .terminal_app_detection import (
    MACOS_APP_INFO,
    WINDOWS_APP_INFO,
    get_terminal_app,
    get_terminal_app_macos,
    get_terminal_app_windows,
    get_terminal_app_wsl,
)
