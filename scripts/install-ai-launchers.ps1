Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$source = Join-Path $PSScriptRoot 'ai-launch.ps1'
if (-not (Test-Path $source)) {
    throw "Missing source launcher: $source"
}

$installDir = Join-Path $env:USERPROFILE '.local\bin'
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

$targetLauncher = Join-Path $installDir 'ai-launch.ps1'
Copy-Item -Path $source -Destination $targetLauncher -Force

$wrappers = @{
    'claude-wsl.cmd' = "@echo off`r`npowershell -NoProfile -ExecutionPolicy Bypass -File ""%USERPROFILE%\.local\bin\ai-launch.ps1"" claude --dangerously-skip-permissions %*`r`n"
    'codex-wsl.cmd'  = "@echo off`r`npowershell -NoProfile -ExecutionPolicy Bypass -File ""%USERPROFILE%\.local\bin\ai-launch.ps1"" codex --yolo %*`r`n"
    'ai-shell.cmd'   = "@echo off`r`npowershell -NoProfile -ExecutionPolicy Bypass -File ""%USERPROFILE%\.local\bin\ai-launch.ps1"" shell`r`n"
}

foreach ($name in $wrappers.Keys) {
    $path = Join-Path $installDir $name
    Set-Content -Path $path -Value $wrappers[$name] -Encoding ASCII
}

$startMarker = '# >>> AI launchers >>>'
$endMarker = '# <<< AI launchers <<<'
$block = @(
    $startMarker,
    'function claude-wsl { & "$env:USERPROFILE\.local\bin\ai-launch.ps1" claude --dangerously-skip-permissions @args }',
    'function codex-wsl { & "$env:USERPROFILE\.local\bin\ai-launch.ps1" codex --yolo @args }',
    'function ai-shell { & "$env:USERPROFILE\.local\bin\ai-launch.ps1" shell @args }',
    'Set-Alias cw claude-wsl -Scope Global',
    'Set-Alias xw codex-wsl -Scope Global',
    $endMarker
)

$documentsPath = [Environment]::GetFolderPath('MyDocuments')
$profileTargets = @(
    (Join-Path $documentsPath 'PowerShell\Microsoft.PowerShell_profile.ps1'),
    (Join-Path $documentsPath 'WindowsPowerShell\Microsoft.PowerShell_profile.ps1')
) | Select-Object -Unique

$pattern = [regex]::Escape($startMarker) + '.*?' + [regex]::Escape($endMarker)
$replacement = ($block -join "`r`n")

foreach ($profilePath in $profileTargets) {
    $profileDir = Split-Path -Parent $profilePath
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
    }
    if (-not (Test-Path $profilePath)) {
        New-Item -ItemType File -Force -Path $profilePath | Out-Null
    }

    $profileTextRaw = Get-Content -Path $profilePath -Raw
    $profileText = if ($null -eq $profileTextRaw) { '' } else { [string]$profileTextRaw }

    $cleanProfileText = [regex]::Replace(
        $profileText,
        $pattern,
        '',
        [System.Text.RegularExpressions.RegexOptions]::Singleline
    ).TrimEnd()

    if ($cleanProfileText.Length -gt 0) {
        $newText = $cleanProfileText + "`r`n" + $replacement + "`r`n"
    }
    else {
        $newText = $replacement + "`r`n"
    }

    Set-Content -Path $profilePath -Value $newText -Encoding ASCII
}

Write-Host "Installed launcher: $targetLauncher"
Write-Host "Installed commands in PATH: claude-wsl.cmd, codex-wsl.cmd, ai-shell.cmd"
Write-Host "Updated PowerShell profiles:"
foreach ($profilePath in $profileTargets) {
    Write-Host "  $profilePath"
}
Write-Host "Use 'claude-wsl' or 'codex-wsl' in a new terminal session."
