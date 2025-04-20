@echo off
REM Script to launch Guts Discord bot versions and always launch guts.py in a new PowerShell tab

set "PATH=%PATH%;C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem"

echo ==============================================
echo        Guts Berserk 2 Discord Launcher
echo ==============================================
echo.
echo Please select which version to launch:
echo 1. CharacterAI Version (c.ai)
echo 2. LLM Version
echo Q. Quit
echo ===================================

set /p choice=Enter your choice (1, 2, or Q): 

REM Change to the directory of the batch file (current folder)
cd /d "%~dp0"

if /i "%choice%"=="1" (
    echo Launching CharacterAI Version...
    start powershell -NoExit -Command "cd '%~dp0' ; python '%~dp0guts_cai.py'"
) else if /i "%choice%"=="2" (
    echo Launching LLM Version...
    start powershell -NoExit -Command "cd '%~dp0' ; python '%~dp0guts_llm.py'"
) else if /i "%choice%"=="Q" (
    echo Quitting...
    exit
) else (
    echo Invalid choice, please try again.
    pause
    call :launch
)

REM Always launch guts.py after the selected version in a new PowerShell tab
echo Launching Guts...
start powershell -NoExit -Command "cd '%~dp0' ; python '%~dp0guts.py'"

exit
