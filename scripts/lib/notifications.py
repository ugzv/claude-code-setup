"""
Notification delivery utilities for Claude Code hooks.
Cross-platform: macOS (terminal-notifier/osascript) and Windows (toast notifications).
"""

import subprocess

from .platform_detection import IS_MACOS, IS_WINDOWS, log_debug


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
    """Send Windows toast notification using PowerShell."""
    # Combine title and subtitle for Windows
    full_title = f"{title} - {subtitle}" if subtitle else title

    # Escape for PowerShell
    full_title = full_title.replace("'", "''").replace('"', '`"')
    message = message.replace("'", "''").replace('"', '`"')

    # Try BurntToast first (better notifications if installed)
    try:
        ps_script = f'''
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
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Claude Code").Show($toast)
        }}
        '''

        result = subprocess.run(
            ["powershell.exe", "-WindowStyle", "Hidden", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=5,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            log_debug(f"  → Windows toast SUCCESS: {full_title}")
        else:
            log_debug(f"  → Windows toast issue: {result.stderr[:100] if result.stderr else 'no error'}")

    except Exception as e:
        # Fallback to basic balloon notification
        try:
            fallback_script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::Information
            $notification.BalloonTipTitle = "{full_title}"
            $notification.BalloonTipText = "{message}"
            $notification.Visible = $true
            $notification.ShowBalloonTip(5000)
            Start-Sleep -Milliseconds 100
            '''

            subprocess.run(
                ["powershell.exe", "-WindowStyle", "Hidden", "-Command", fallback_script],
                capture_output=True,
                timeout=3,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception:
            pass

        log_debug(f"  → Windows notification fallback used: {str(e)}")


# =============================================================================
# Cross-Platform Interface
# =============================================================================

def send_notification(title: str, message: str, subtitle: str = "", app_name: str = "") -> None:
    """Send desktop notification using platform-appropriate method."""
    if IS_MACOS:
        send_notification_macos(title, message, subtitle, app_name)
    elif IS_WINDOWS:
        send_notification_windows(title, message, subtitle, app_name)
