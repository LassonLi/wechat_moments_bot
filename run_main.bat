@echo off
chcp 65001 >nul
rem Ensure Python uses UTF-8 on Windows
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set VENV_PY=%SCRIPT_DIR%\.venv\Scripts\python.exe
if exist "%VENV_PY%" (
	set PYTHON_PATH=%VENV_PY%
	goto :found_python
)

for /f "delims=" %%i in ('where python 2^>nul') do (
	set PYTHON_PATH=%%i
	goto :found_python
)

echo [ERROR] Python not found. Please install Python and add to PATH.
pause
exit /b 1

:found_python
if not exist "%SCRIPT_DIR%\logs" mkdir "%SCRIPT_DIR%\logs"
echo [%date% %time%] Running main.py using %PYTHON_PATH% >> "%SCRIPT_DIR%\logs\schtasks_run.log"
cd /d "%SCRIPT_DIR%"
"%PYTHON_PATH%" "%SCRIPT_DIR%\main.py" >> "%SCRIPT_DIR%\logs\schtasks_run.log" 2>&1
