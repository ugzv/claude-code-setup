"""
Notification delivery utilities for Claude Code and Codex CLI hooks.
Cross-platform: macOS (terminal-notifier/osascript), Windows (toast), and WSL (toast via powershell.exe).
"""

from .platform_detection import (
    CLI_NAME, IS_MACOS, IS_WSL, USES_WINDOWS_GUI,
    log_debug, run_powershell, run_quiet,
)


# =============================================================================
# Shared Helpers
# =============================================================================

def _prepare_notification_args(title: str, message: str, subtitle: str = "") -> tuple[str, str]:
    """Build full title and escape both strings for PowerShell."""
    full_title = f"{title} - {subtitle}" if subtitle else title
    full_title = full_title.replace("'", "''").replace('"', '`"')
    message = message.replace("'", "''").replace('"', '`"')
    return full_title, message


# =============================================================================
# Windows PowerShell Helpers
# =============================================================================

def _build_windows_toast_script(full_title: str, message: str) -> str:
    """Build PowerShell script for Windows toast notification.
    Tries BurntToast module first, falls back to WinRT toast API.
    Uses CLI_NAME for the notifier identity so Claude/Codex notifications are distinct."""
    return f'''
    if (Get-Module -ListAvailable -Name BurntToast) {{
        Import-Module BurntToast
        New-BurntToastNotification -Text "{full_title}", "{message}"
    }} else {{
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

        $template = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">{full_title}</text>
            <text id="2">{message}</text>
        </binding>
    </visual>
</toast>
"@
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{CLI_NAME}").Show($toast)
    }}
    '''


def _build_balloon_script(full_title: str, message: str) -> str:
    """Build PowerShell script for a balloon (NotifyIcon) notification.
    Works reliably from WSL where WinRT toasts are silently dropped
    due to the PowerShell process lacking a registered AppUserModelID."""
    return f'''
    Add-Type -AssemblyName System.Windows.Forms
    $n = New-Object System.Windows.Forms.NotifyIcon
    $n.Icon = [System.Drawing.SystemIcons]::Information
    $n.BalloonTipTitle = "{full_title}"
    $n.BalloonTipText = "{message}"
    $n.Visible = $true
    $n.ShowBalloonTip(5000)
    Start-Sleep -Seconds 3
    $n.Dispose()
    '''


# =============================================================================
# macOS Notifications
# =============================================================================

def escape_for_applescript(text: str) -> str:
    """Escape text for use in AppleScript string literals."""
    return text.replace('\\', '\\\\').replace('"', '\\"')


def get_bundle_id_for_app(app_name: str) -> str:
    """Dynamically get bundle ID for an app (macOS)."""
    ok, stdout = run_quiet(["osascript", "-e", f'id of app "{app_name}"'])
    return stdout if ok else ""


def send_notification_macos(title: str, message: str, subtitle: str = "", app_name: str = "") -> None:
    """Send macOS notification using terminal-notifier (preferred) or osascript."""
    # Try terminal-notifier first
    found, terminal_notifier_path = run_quiet(["which", "terminal-notifier"])

    if found and terminal_notifier_path:
        try:
            cmd = [terminal_notifier_path, "-title", title, "-message", message]
            if subtitle:
                cmd.extend(["-subtitle", subtitle])

            if app_name:
                bundle_id = get_bundle_id_for_app(app_name)
                if bundle_id:
                    cmd.extend(["-activate", bundle_id])

            ok, _ = run_quiet(cmd, timeout=2)
            if ok:
                log_debug(f"  → terminal-notifier SUCCESS: {title}")
                return
            else:
                log_debug("  → terminal-notifier FAILED, falling back to osascript")

        except Exception as e:
            log_debug(f"  → terminal-notifier FAILED: {str(e)}, falling back to osascript")

    # Fallback to osascript
    try:
        safe_title = escape_for_applescript(title)
        safe_message = escape_for_applescript(message)
        safe_subtitle = escape_for_applescript(subtitle)

        script = f'display notification "{safe_message}" with title "{safe_title}"'
        if safe_subtitle:
            script += f' subtitle "{safe_subtitle}"'

        ok, _ = run_quiet(["osascript", "-e", script], timeout=2)
        if ok:
            log_debug(f"  → osascript SUCCESS: {title} | {subtitle} | {message[:50]}")
        else:
            log_debug("  → osascript FAILED")

    except Exception as e:
        log_debug(f"  → NOTIFICATION FAILED: {str(e)}")


# =============================================================================
# Windows Notifications
# =============================================================================

def _send_notification_windows(
    title: str, message: str, subtitle: str = "", app_name: str = "", *, blocking: bool = True,
) -> None:
    """Send Windows notification using PowerShell.
    On native Windows: WinRT toast (BurntToast → WinRT fallback).
    On WSL: balloon notification (WinRT toasts are silently dropped).
    When blocking=False, uses fire-and-forget Popen (~10ms)."""
    full_title, message = _prepare_notification_args(title, message, subtitle)

    if IS_WSL:
        ps_script = _build_balloon_script(full_title, message)
        timeout = 8
    else:
        ps_script = _build_windows_toast_script(full_title, message)
        timeout = 5

    label = "WSL balloon" if IS_WSL else "Windows toast"

    if blocking:
        try:
            result = run_powershell(ps_script, timeout=timeout)
            if result and result.returncode == 0:
                log_debug(f"  → {label} SUCCESS: {full_title}")
            else:
                stderr = (result.stderr[:100] if result and result.stderr else "no error")
                log_debug(f"  → {label} issue: {stderr}")
        except Exception as e:
            log_debug(f"  → {label} FAILED: {str(e)}")
    else:
        try:
            run_powershell(ps_script, fire_and_forget=True)
            log_debug(f"  → {label} ASYNC launched: {full_title}")
        except Exception as e:
            log_debug(f"  → {label} ASYNC failed: {str(e)}")


# =============================================================================
# Cross-Platform Interface
# =============================================================================

def send_notification(
    title: str, message: str, subtitle: str = "", app_name: str = "", *, blocking: bool = True,
) -> None:
    """Send desktop notification using platform-appropriate method.
    When blocking=False, uses fire-and-forget on Windows (macOS is already fast)."""
    if IS_MACOS:
        send_notification_macos(title, message, subtitle, app_name)
    elif USES_WINDOWS_GUI:
        _send_notification_windows(title, message, subtitle, app_name, blocking=blocking)


def send_notification_async(title: str, message: str, subtitle: str = "", app_name: str = "") -> None:
    """Backward-compatible alias."""
    send_notification(title, message, subtitle, app_name, blocking=False)
