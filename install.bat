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

REM Clean up obsolete commands
for %%f in ("%USERPROFILE%\.claude\commands\*.md") do (
    if not exist "%SCRIPT_DIR%commands\%%~nxf" (
        del "%%f"
        echo Removed obsolete: %%~nxf
    )
)

REM Copy files
echo Installing commands...
copy /Y "%SCRIPT_DIR%commands\*.md" "%USERPROFILE%\.claude\commands\" >nul

echo Installing templates...
copy /Y "%SCRIPT_DIR%templates\*.md" "%USERPROFILE%\.claude\templates\" >nul

REM Install statusline
echo Installing statusline...
copy /Y "%SCRIPT_DIR%statusline.sh" "%USERPROFILE%\.claude\statusline.sh" >nul

REM Configure settings
set "SETTINGS_FILE=%USERPROFILE%\.claude\settings.json"

REM Create fresh settings (simpler than parsing JSON in batch)
echo { > "%SETTINGS_FILE%"
echo   "attribution": { >> "%SETTINGS_FILE%"
echo     "commit": "" >> "%SETTINGS_FILE%"
echo   }, >> "%SETTINGS_FILE%"
echo   "statusLine": { >> "%SETTINGS_FILE%"
echo     "type": "command", >> "%SETTINGS_FILE%"
echo     "command": "~/.claude/statusline.sh" >> "%SETTINGS_FILE%"
echo   } >> "%SETTINGS_FILE%"
echo } >> "%SETTINGS_FILE%"
echo Created settings.json

echo.
echo Done. Commands and statusline installed.
echo.
echo Commands:
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
echo   /mcp-guide      Validate MCP server projects
echo   /prompt-guide   Load prompting philosophy
echo   /commands       List project commands
echo.
echo Note: Statusline requires bash and jq (Git Bash or WSL)
echo.
echo Next: Restart Claude Code, then run /migrate in a project
echo.

endlocal
