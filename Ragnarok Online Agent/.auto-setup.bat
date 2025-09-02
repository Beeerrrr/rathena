@echo off
REM Ragnarok Online Agent Auto-Setup Script (Windows)
REM This script automatically sets up the RO Agent for your project

echo 🗡️ Ragnarok Online Server Management Agent Setup
echo ==================================================

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PROJECT_DIR=%cd%"

echo 📍 Project Directory: %PROJECT_DIR%
echo 📍 Agent Directory: %SCRIPT_DIR%

REM Check if we're in a RO server directory
echo.
echo 🔍 Detecting RO server structure...

if exist "rathena" (
    echo ✅ Detected rAthena server structure
    set EMULATOR=rathena
) else if exist "npc" (
    if exist "db" (
        if exist "conf" (
            echo ✅ Detected rAthena server structure
            set EMULATOR=rathena
        )
    )
) else if exist "hercules" (
    echo ✅ Detected Hercules server structure
    set EMULATOR=hercules
) else if exist "openkore" (
    echo ✅ Detected OpenKore bot structure
    set EMULATOR=openkore
) else (
    echo ⚠️  No specific emulator detected - treating as generic RO project
    set EMULATOR=generic
)

REM Create necessary directories
echo.
echo 📁 Creating necessary directories...

if not exist "%PROJECT_DIR%\ANALYSIS_CACHE" mkdir "%PROJECT_DIR%\ANALYSIS_CACHE"
if not exist "%PROJECT_DIR%\ANALYSIS_CACHE\errors" mkdir "%PROJECT_DIR%\ANALYSIS_CACHE\errors"
if not exist "%PROJECT_DIR%\ANALYSIS_CACHE\patterns" mkdir "%PROJECT_DIR%\ANALYSIS_CACHE\patterns"
if not exist "%PROJECT_DIR%\ANALYSIS_CACHE\scripts" mkdir "%PROJECT_DIR%\ANALYSIS_CACHE\scripts"
if not exist "%PROJECT_DIR%\templates" mkdir "%PROJECT_DIR%\templates"
if not exist "%PROJECT_DIR%\docs" mkdir "%PROJECT_DIR%\docs"

echo ✅ Directories created

REM Check Python installation
echo.
echo 🐍 Checking Python installation...

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo ✅ Python found
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
        echo ✅ Python 3 found
    ) else (
        echo ❌ Python not found. Please install Python 3.8+
        pause
        exit /b 1
    )
)

REM Check Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 📊 Python Version: %PYTHON_VERSION%

REM Create virtual environment (optional)
echo.
set /p CREATE_VENV="🤔 Create virtual environment? (recommended) [Y/n]: "
if /i not "%CREATE_VENV%"=="n" (
    if /i not "%CREATE_VENV%"=="N" (
        echo 📦 Creating virtual environment...
        %PYTHON_CMD% -m venv ro_agent_env
        if exist "ro_agent_env" (
            echo ✅ Virtual environment created: ro_agent_env
            echo 💡 To activate: ro_agent_env\Scripts\activate
            set PYTHON_CMD=%PROJECT_DIR%\ro_agent_env\Scripts\python.exe
        )
    )
)

REM Install dependencies
echo.
echo 📦 Installing dependencies...

REM Create requirements.txt if it doesn't exist
if not exist "%SCRIPT_DIR%\requirements.txt" (
    echo click>=8.0.0> "%SCRIPT_DIR%\requirements.txt"
    echo requests>=2.25.0>> "%SCRIPT_DIR%\requirements.txt"
    echo pyyaml>=5.4.0>> "%SCRIPT_DIR%\requirements.txt"
    echo ✅ Created requirements.txt
)

REM Upgrade pip and install requirements
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r "%SCRIPT_DIR%\requirements.txt"

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ⚠️  Some dependencies may have failed to install
)

REM Create configuration file
echo.
echo ⚙️  Creating configuration...

set CONFIG_FILE=%PROJECT_DIR%\ro_agent_config.yml
if not exist "%CONFIG_FILE%" (
    echo # Ragnarok Online Agent Configuration> "%CONFIG_FILE%"
    echo emulator: %EMULATOR%>> "%CONFIG_FILE%"
    echo project_path: %PROJECT_DIR%>> "%CONFIG_FILE%"
    echo agent_path: %SCRIPT_DIR%>> "%CONFIG_FILE%"
    echo.>> "%CONFIG_FILE%"
    echo # Cache settings>> "%CONFIG_FILE%"
    echo cache_enabled: true>> "%CONFIG_FILE%"
    echo cache_dir: ANALYSIS_CACHE>> "%CONFIG_FILE%"
    echo.>> "%CONFIG_FILE%"
    echo # Database settings ^(optional^)>> "%CONFIG_FILE%"
    echo database:>> "%CONFIG_FILE%"
    echo   host: localhost>> "%CONFIG_FILE%"
    echo   port: 3306>> "%CONFIG_FILE%"
    echo   name: ragnarok>> "%CONFIG_FILE%"
    echo   user: ragnarok>> "%CONFIG_FILE%"
    echo   password: ragnarok>> "%CONFIG_FILE%"
    echo.>> "%CONFIG_FILE%"
    echo # Translation settings>> "%CONFIG_FILE%"
    echo translation:>> "%CONFIG_FILE%"
    echo   default_source: english>> "%CONFIG_FILE%"
    echo   supported_languages: [thai, spanish, french, german]>> "%CONFIG_FILE%"
    echo.>> "%CONFIG_FILE%"
    echo # Backup settings>> "%CONFIG_FILE%"
    echo backup:>> "%CONFIG_FILE%"
    echo   enabled: true>> "%CONFIG_FILE%"
    echo   max_backups: 10>> "%CONFIG_FILE%"
    echo   compress: true>> "%CONFIG_FILE%"
    echo ✅ Configuration file created: ro_agent_config.yml
)

REM Create command alias (Windows)
echo.
echo 🔗 Setting up command alias...

REM Check if we can modify PATH or create a batch file
set ALIAS_FILE=%PROJECT_DIR%\ro_agent.bat
echo @echo off> "%ALIAS_FILE%"
echo "%PYTHON_CMD%" "%SCRIPT_DIR%\src\cli.py" %%*>> "%ALIAS_FILE%"

if exist "%ALIAS_FILE%" (
    echo ✅ Created alias script: ro_agent.bat
    echo 💡 You can now use: ro_agent --help
)

REM Final setup check
echo.
echo 🔍 Running setup verification...

REM Test import
%PYTHON_CMD% -c "import sys; sys.path.insert(0, '%SCRIPT_DIR%\src'); import cli; print('✅ CLI module imported successfully')" 2>nul

if %errorlevel% equ 0 (
    echo ✅ Setup verification passed
) else (
    echo ⚠️  Setup verification failed - some modules may not work correctly
)

REM Show completion message
echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo 🗡️  Ragnarok Online Agent is ready to use!
echo.
echo 📖 Quick Start:
echo    cd "%PROJECT_DIR%"
if exist "ro_agent_env" (
    echo    ro_agent_env\Scripts\activate
)
echo    "%PYTHON_CMD%" "%SCRIPT_DIR%\src\cli.py" --help
if exist "%ALIAS_FILE%" (
    echo    # Or use the alias: ro_agent --help
)
echo.
echo 📊 Detected Emulator: %EMULATOR%
echo 📁 Project Path: %PROJECT_DIR%
echo 📁 Agent Path: %SCRIPT_DIR%
echo.
echo 💡 Useful commands:
echo    ro_agent status              # Check server status
echo    ro_agent files organize      # Organize your files
echo    ro_agent script npc          # Generate NPC scripts
echo    ro_agent update items        # Update from kRO
echo    ro_agent ask "how to setup"  # Get help
echo.
echo 📚 For more information, see: %SCRIPT_DIR%\README.md
echo.
echo 🚀 Happy server managing!

pause