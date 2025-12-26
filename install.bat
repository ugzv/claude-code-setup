@echo off
setlocal

REM Claude Code Setup Installer
REM https://github.com/ugzv/claude-code-setup

echo Installing Claude Code Setup...
echo.

set "SCRIPT_DIR=%~dp0"

REM Create directories
if not exist "%USERPROFILE%\.claude\commands" mkdir "%USERPROFILE%\.claude\commands"
if not exist "%USERPROFILE%\.claude\templates" mkdir "%USERPROFILE%\.claude\templates"

REM Copy files
echo Installing commands...
copy /Y "%SCRIPT_DIR%commands\*.md" "%USERPROFILE%\.claude\commands\" >nul

echo Installing templates...
copy /Y "%SCRIPT_DIR%templates\*.md" "%USERPROFILE%\.claude\templates\" >nul

REM Configure settings (disable co-author in commits)
set "SETTINGS_FILE=%USERPROFILE%\.claude\settings.json"

if exist "%SETTINGS_FILE%" (
    findstr /C:"attribution" "%SETTINGS_FILE%" >nul
    if errorlevel 1 (
        echo Note: Add to %SETTINGS_FILE%: "attribution": { "commit": "" }
    ) else (
        echo Settings already configured
    )
) else (
    echo { > "%SETTINGS_FILE%"
    echo   "attribution": { >> "%SETTINGS_FILE%"
    echo     "commit": "" >> "%SETTINGS_FILE%"
    echo   } >> "%SETTINGS_FILE%"
    echo } >> "%SETTINGS_FILE%"
    echo Created settings.json
)

echo.
echo Done. Commands installed:
echo.
echo   /migrate        Set up tracking in a project
echo   /think          Plan approach before complex tasks
echo   /fix            Auto-fix linting and formatting
echo   /test           Run tests intelligently
echo   /commit         Commit changes with clean messages
echo   /push           Push and update state tracking
echo   /health         Check project health
echo   /analyze        Find code that resists change
echo   /backlog        Review and manage backlog
echo   /agent          Audit Agent SDK projects
echo   /mcp            Validate MCP server projects
echo   /prompt-guide   Load prompting philosophy
echo   /commands       List project commands
echo.
echo Next: Restart Claude Code, then run /migrate in a project
echo.

endlocal
