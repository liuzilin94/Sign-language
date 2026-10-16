@echo off
setlocal
cd /d "%~dp0"

if exist "simple_frontend.html" (
    start "" "%~dp0simple_frontend.html"
    exit /b 0
)

echo Frontend page was not found.
echo Expected file: simple_frontend.html
pause
exit /b 1
