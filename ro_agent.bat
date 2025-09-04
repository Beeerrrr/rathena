@echo off
setlocal
REM Prefer venv Python if available, else fallback to system Python
set "ROOT_DIR=%~dp0"
set "AGENT_DIR=%ROOT_DIR%Ragnarok Online Agent"
set "VENV_PY=%AGENT_DIR%\ro_agent_env\Scripts\python.exe"

if exist "%VENV_PY%" (
  "%VENV_PY%" "%AGENT_DIR%\src\cli.py" %*
  goto :eof
) else (
  python "%AGENT_DIR%\src\cli.py" %*
)

endlocal
