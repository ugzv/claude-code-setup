Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$rawArgs = @($args)
if ($rawArgs.Count -lt 1) {
    throw "Usage: ai-launch.ps1 <claude|codex|shell> [args...]"
}

$Tool = [string]$rawArgs[0]
if ($Tool -notin @('claude', 'codex', 'shell')) {
    throw "Invalid tool '$Tool'. Expected one of: claude, codex, shell."
}

[string[]]$CommandArgs = @()
if ($rawArgs.Count -gt 1) {
    $CommandArgs = @($rawArgs[1..($rawArgs.Count - 1)] | ForEach-Object { [string]$_ })
}

function Should-SkipAutoUpdate {
    if ($env:AI_LAUNCH_SKIP_UPDATE -eq '1') {
        return $true
    }
    return $false
}

function Invoke-NativeAutoUpdate {
    param([Parameter(Mandatory = $true)][string]$ToolName)

    if (Should-SkipAutoUpdate) {
        return
    }

    if ($ToolName -eq 'claude') {
        $claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
        if ($null -ne $claudeCmd) {
            & $claudeCmd.Source update *> $null
        }
        return
    }

    if ($ToolName -eq 'codex') {
        $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
        if ($null -ne $npmCmd) {
            & $npmCmd.Source update -g @openai/codex *> $null
        }
    }
}

function Escape-BashArg {
    param([Parameter(Mandatory = $true)][string]$Value)

    if ($Value.Length -eq 0) {
        return "''"
    }

    $singleQuote = [char]39
    $doubleQuote = [char]34
    $replacement = "$singleQuote$doubleQuote$singleQuote$doubleQuote$singleQuote"
    return $singleQuote + ($Value -replace [regex]::Escape($singleQuote), $replacement) + $singleQuote
}

function Convert-WindowsPathToMsys {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ($Path -match '^([A-Za-z]):\\(.*)$') {
        $drive = $matches[1].ToLowerInvariant()
        $rest = $matches[2] -replace '\\', '/'
        if ($rest.Length -eq 0) {
            return "/$drive"
        }
        return "/$drive/$rest"
    }

    return ($Path -replace '\\', '/')
}

function Get-EnvValue {
    param([Parameter(Mandatory = $true)][string]$Name)
    $item = Get-Item "Env:$Name" -ErrorAction SilentlyContinue
    if ($null -eq $item) {
        return $null
    }
    return $item.Value
}

function Run-InWsl {
    param(
        [Parameter(Mandatory = $true)][string]$ToolName,
        [string[]]$ToolArgs
    )

    $distroOutput = (& wsl.exe -l -q 2>$null)
    if ($LASTEXITCODE -ne 0) {
        return $null
    }

    $distros = @($distroOutput | ForEach-Object { $_.Trim() } | Where-Object { $_ -and $_.Length -gt 0 })
    if ($distros.Count -eq 0) {
        return $null
    }

    $distro = if ($distros -contains 'Ubuntu') { 'Ubuntu' } else { $distros[0] }

    if ($ToolName -ne 'shell') {
        & wsl.exe -d $distro -- bash -lc ("command -v " + (Escape-BashArg -Value $ToolName) + " >/dev/null 2>&1")
        if ($LASTEXITCODE -ne 0) {
            return $null
        }
    }

    $winCwd = (Get-Location).Path
    $linuxCwd = (& wsl.exe -d $distro -- wslpath -a "$winCwd" 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($linuxCwd)) {
        $linuxCwd = '~'
    }
    else {
        $linuxCwd = $linuxCwd.Trim()
    }

    $exports = New-Object System.Collections.Generic.List[string]
    foreach ($name in @('ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'OPENAI_BASE_URL', 'CODEX_HOME', 'CLAUDE_CONFIG_DIR')) {
        $value = Get-EnvValue -Name $name
        if ($null -ne $value -and $value.Length -gt 0) {
            [void]$exports.Add("export $name=" + (Escape-BashArg -Value $value))
        }
    }

    $parts = New-Object System.Collections.Generic.List[string]
    if ($exports.Count -gt 0) {
        [void]$parts.Add(($exports -join '; '))
    }
    [void]$parts.Add('cd ' + (Escape-BashArg -Value $linuxCwd))

    if (-not (Should-SkipAutoUpdate)) {
        if ($ToolName -eq 'claude') {
            [void]$parts.Add('claude update >/dev/null 2>&1 || true')
        }
        elseif ($ToolName -eq 'codex') {
            [void]$parts.Add('npm update -g @openai/codex >/dev/null 2>&1 || true')
        }
    }

    if ($ToolName -eq 'shell') {
        [void]$parts.Add('exec ${SHELL:-bash} -l')
    }
    else {
        $escapedArgs = @($ToolArgs | ForEach-Object { Escape-BashArg -Value $_ })
        $invocation = if ($escapedArgs.Count -gt 0) {
            "$ToolName " + ($escapedArgs -join ' ')
        }
        else {
            $ToolName
        }
        [void]$parts.Add($invocation)
    }

    $bashCommand = $parts -join '; '
    & wsl.exe -d $distro -- bash -lc $bashCommand
    return [int]$LASTEXITCODE
}

function Run-InGitBash {
    param(
        [Parameter(Mandatory = $true)][string]$ToolName,
        [string[]]$ToolArgs
    )

    # Interactive Claude/Codex sessions are more reliable in native Windows terminals.
    # Keep Git Bash as the default only for shell mode, unless explicitly forced.
    if ($ToolName -ne 'shell' -and $env:AI_LAUNCH_PREFER_GIT_BASH -ne '1') {
        return $null
    }

    $gitBash = 'C:\Program Files\Git\bin\bash.exe'
    if (-not (Test-Path $gitBash)) {
        return $null
    }

    $msysCwd = Convert-WindowsPathToMsys -Path (Get-Location).Path
    $parts = New-Object System.Collections.Generic.List[string]
    [void]$parts.Add('cd ' + (Escape-BashArg -Value $msysCwd))

    if (-not (Should-SkipAutoUpdate)) {
        if ($ToolName -eq 'claude') {
            [void]$parts.Add('claude update >/dev/null 2>&1 || true')
        }
        elseif ($ToolName -eq 'codex') {
            [void]$parts.Add('npm update -g @openai/codex >/dev/null 2>&1 || true')
        }
    }

    if ($ToolName -eq 'shell') {
        [void]$parts.Add('exec bash -l')
    }
    else {
        $escapedArgs = @($ToolArgs | ForEach-Object { Escape-BashArg -Value $_ })
        $invocation = if ($escapedArgs.Count -gt 0) {
            "$ToolName " + ($escapedArgs -join ' ')
        }
        else {
            $ToolName
        }
        [void]$parts.Add($invocation)
    }

    $bashCommand = $parts -join '; '
    & $gitBash -lc $bashCommand
    return [int]$LASTEXITCODE
}

$exitCode = Run-InWsl -ToolName $Tool -ToolArgs $CommandArgs
if ($null -ne $exitCode) {
    exit $exitCode
}

Invoke-NativeAutoUpdate -ToolName $Tool

$native = Get-Command $Tool -ErrorAction SilentlyContinue
if ($null -eq $native) {
    $exitCode = Run-InGitBash -ToolName $Tool -ToolArgs $CommandArgs
    if ($null -ne $exitCode) {
        exit $exitCode
    }

    if ($Tool -eq 'shell') {
        Write-Error 'Neither WSL nor Git Bash is available.'
    }

    Write-Error "Command '$Tool' is not available on PATH."
}

& $native.Source @CommandArgs
exit $LASTEXITCODE
