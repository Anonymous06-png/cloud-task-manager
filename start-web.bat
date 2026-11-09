@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-web.ps1" %*
set "exitCode=%ERRORLEVEL%"
if not "%exitCode%"=="0" (
    echo.
    echo Startup failed with exit code %exitCode%. Press any key to close.
    pause >nul
)
exit /b %exitCode%
