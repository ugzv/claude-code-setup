@echo off
setlocal

REM Claude Code Setup Installer
REM https://github.com/ugzv/claude-code-setup

echo Installing Claude Code Setup...
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Create directories
echo Creating directories...
if not exist "%USERPROFILE%\.claude\commands" mkdir "%USERPROFILE%\.claude\commands"
if not exist "%USERPROFILE%\.claude\templates" mkdir "%USERPROFILE%\.claude\templates"

REM Copy commands
echo Installing commands...
copy /Y "%SCRIPT_DIR%commands\*.md" "%USERPROFILE%\.claude\commands\" >nul

REM Copy templates
echo Installing templates...
copy /Y "%SCRIPT_DIR%templates\*.md" "%USERPROFILE%\.claude\templates\" >nul

REM Configure settings (disable co-author in commits)
echo Configuring settings...
set "SETTINGS_FILE=%USERPROFILE%\.claude\settings.json"

if exist "%SETTINGS_FILE%" (
    findstr /C:"attribution" "%SETTINGS_FILE%" >nul
    if errorlevel 1 (
        echo   Note: Please manually add attribution settings to disable co-author
        echo   Add this to %SETTINGS_FILE%:
        echo   "attribution": { "commit": "" }
    ) else (
        echo   Attribution already configured, skipping...
    )
) else (
    echo { > "%SETTINGS_FILE%"
    echo   "attribution": { >> "%SETTINGS_FILE%"
    echo     "commit": "" >> "%SETTINGS_FILE%"
    echo   } >> "%SETTINGS_FILE%"
    echo } >> "%SETTINGS_FILE%"
    echo   Created settings.json
)

echo.
echo Installation complete!
echo.
echo Commands installed:
echo.
echo   Setup:
echo     /migrate       - Set up tracking (new or existing projects)
echo.
echo   Planning:
echo     /think         - Think through approach before complex tasks
echo.
echo   Development:
echo     /fix           - Auto-fix linting, formatting, unused imports
echo     /test          - Run tests
echo     /commit        - Clean commits (use --all for batch)
echo     /push          - Push + update state
echo.
echo   Analysis:
echo     /health        - Project health check (TODO, deps, security)
echo     /analyze       - Find refactoring opportunities (includes dead code)
echo     /agent         - Audit Agent SDK projects
echo     /mcp           - Test MCP server projects
echo.
echo   Prompting:
echo     /prompt-guide  - Load philosophy, apply to any prompt work
echo.
echo   Context:
echo     /backlog       - Manage backlog items
echo     /commands      - List project commands
echo.
echo Next steps:
echo   1. Restart Claude Code to pick up new commands
echo   2. In a project, run /migrate to set up tracking
echo.

endlocal
