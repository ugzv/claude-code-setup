[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-IsAdmin)) {
    $scriptPath = $PSCommandPath
    $argList = @(
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-File', ('"' + $scriptPath + '"')
    )
    Write-Host 'Requesting elevation to install WSL and Ubuntu...'
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList ($argList -join ' ')
    exit 0
}

Write-Host 'Enabling required Windows features...'
& dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
& dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

Write-Host 'Installing WSL runtime components...'
& wsl.exe --install --no-distribution
& wsl.exe --update
& wsl.exe --set-default-version 2

$distros = (& wsl.exe -l -q 2>$null) | ForEach-Object { $_.Trim() } | Where-Object { $_ }
if ($distros -notcontains 'Ubuntu') {
    Write-Host 'Installing Ubuntu distro...'
    & wsl.exe --install -d Ubuntu
}
else {
    Write-Host 'Ubuntu is already installed.'
}

Write-Host ''
Write-Host 'WSL bootstrap command completed.'
Write-Host 'If Windows asked for restart, reboot and run this script once more.'
Write-Host 'After Ubuntu first-launch account setup, run:'
Write-Host '  scripts\install-ai-launchers.ps1'
Write-Host 'Then use: claude-wsl / codex-wsl'
