@echo off
REM Claude Code Setup - Windows wrapper for install.py
REM Requires Python 3.8+

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is required
    echo Install from: https://python.org
    exit /b 1
)

python "%~dp0install.py" %*
