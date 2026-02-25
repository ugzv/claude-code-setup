"""
Notification delivery utilities for Claude Code and Codex CLI hooks.
Cross-platform: macOS (terminal-notifier/osascript), Windows (toast), and WSL (toast via powershell.exe).
"""

import subprocess

from .platform_detection import (
    CLI_NAME, IS_MACOS, IS_WSL, POWERSHELL_EXE, USES_WINDOWS_GUI,
    get_windows_subprocess_kwargs, log_debug,
)


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
    try:
        result = subprocess.run(
            ["osascript", "-e", f'id of app "{app_name}"'],
            capture_output=True,
            text=True,
            timeout=0.5,
            stdin=subprocess.DEVNULL
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def send_notification_macos(title: str, message: str, subtitle: str = "", app_name: str = "") -> None:
    """Send macOS notification using terminal-notifier (preferred) or osascript."""
    # Try terminal-notifier first
    terminal_notifier_path = None
    try:
        result = subprocess.run(["which", "terminal-notifier"], capture_output=True, text=True)
        if result.returncode == 0:
            terminal_notifier_path = result.stdout.strip()
    except Exception:
        pass

    if terminal_notifier_path:
        try:
            cmd = [terminal_notifier_path, "-title", title, "-message", message]
            if subtitle:
                cmd.extend(["-subtitle", subtitle])

            if app_name:
                bundle_id = get_bundle_id_for_app(app_name)
                if bundle_id:
                    cmd.extend(["-activate", bundle_id])

            subprocess.run(cmd, check=True, timeout=2, capture_output=True)
            log_debug(f"  → terminal-notifier SUCCESS: {title}")
            return

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

        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            log_debug(f"  → osascript SUCCESS: {title} | {subtitle} | {message[:50]}")
        else:
            log_debug(f"  → osascript FAILED: {result.stderr}")

    except Exception as e:
        log_debug(f"  → NOTIFICATION FAILED: {str(e)}")


# =============================================================================
# Windows Notifications
# =============================================================================

def send_notification_windows(title: str, message: str, subtitle: str = "", app_name: str = "") -> None:
    """Send Windows notification using PowerShell.
    On native Windows: WinRT toast (BurntToast → WinRT fallback).
    On WSL: balloon notification (WinRT toasts are silently dropped)."""
    full_title = f"{title} - {subtitle}" if subtitle else title

    # Escape for PowerShell
    full_title = full_title.replace("'", "''").replace('"', '`"')
    message = message.replace("'", "''").replace('"', '`"')

    # WSL: use balloon notification (WinRT toasts lack AppUserModelID)
    if IS_WSL:
        try:
            ps_script = _build_balloon_script(full_title, message)
            result = subprocess.run(
                [POWERSHELL_EXE, "-WindowStyle", "Hidden", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=8,
                stdin=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                log_debug(f"  → WSL balloon SUCCESS: {full_title}")
            else:
                log_debug(f"  → WSL balloon issue: {result.stderr[:100] if result.stderr else 'no error'}")
        except Exception as e:
            log_debug(f"  → WSL balloon FAILED: {str(e)}")
        return

    # Native Windows: try toast notification
    try:
        ps_script = _build_windows_toast_script(full_title, message)
        result = subprocess.run(
            [POWERSHELL_EXE, "-WindowStyle", "Hidden", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=5,
            stdin=subprocess.DEVNULL,
            **get_windows_subprocess_kwargs()
        )
        if result.returncode == 0:
            log_debug(f"  → Windows toast SUCCESS: {full_title}")
        else:
            log_debug(f"  → Windows toast issue: {result.stderr[:100] if result.stderr else 'no error'}")
    except Exception as e:
        log_debug(f"  → Windows toast FAILED: {str(e)}")


# =============================================================================
# Cross-Platform Interface
# =============================================================================

def send_notification(title: str, message: str, subtitle: str = "", app_name: str = "") -> None:
    """Send desktop notification using platform-appropriate method."""
    if IS_MACOS:
        send_notification_macos(title, message, subtitle, app_name)
    elif USES_WINDOWS_GUI:
        send_notification_windows(title, message, subtitle, app_name)


def send_notification_windows_async(title: str, message: str, subtitle: str = "") -> None:
    """Send Windows notification via fire-and-forget Popen (~10ms).
    Does not wait for the PowerShell process to complete."""
    full_title = f"{title} - {subtitle}" if subtitle else title

    # Escape for PowerShell
    full_title = full_title.replace("'", "''").replace('"', '`"')
    message = message.replace("'", "''").replace('"', '`"')

    ps_script = (_build_balloon_script(full_title, message) if IS_WSL
                 else _build_windows_toast_script(full_title, message))

    try:
        subprocess.Popen(
            [POWERSHELL_EXE, "-WindowStyle", "Hidden", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            **get_windows_subprocess_kwargs(),
        )
        log_debug(f"  -> Windows notification ASYNC launched: {full_title}")
    except Exception as e:
        log_debug(f"  -> Windows notification ASYNC failed: {str(e)}")


def send_notification_async(title: str, message: str, subtitle: str = "", app_name: str = "") -> None:
    """Send desktop notification asynchronously (fire-and-forget).
    On macOS, falls back to sync send. On Windows, uses Popen."""
    if IS_MACOS:
        send_notification_macos(title, message, subtitle, app_name)
    elif USES_WINDOWS_GUI:
        send_notification_windows_async(title, message, subtitle)
