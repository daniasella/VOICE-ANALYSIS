@echo off
:: Set clean environment and nice color (Cyan on Black)
color 0B
title VOICE-TO-VOICE SENTIMENT ANALYSIS SYSTEM

:: Determine target directory (always run inside FLASK2 if it exists)
set "CURRENT_DIR=%~dp0"
cd /d "%CURRENT_DIR%"

if exist "FLASK2" (
    cd "FLASK2"
)

cls
echo =======================================================================
echo          VOICE-TO-VOICE SENTIMENT ANALYSIS SYSTEM (INDONESIA)
echo =======================================================================
echo  Developed by: UMMU KHUZAIFAH (Universitas Wahid Hasyim Semarang)
echo =======================================================================
echo.

:: 1. Check Python installation
echo [STEP 1] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not added to your system PATH!
    echo Please install Python 3.12.10 and try again.
    pause
    exit /b
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [SUCCESS] Python %PY_VER% detected!
echo.

:: 2. Check or Create Virtual Environment
echo [STEP 2] Checking Virtual Environment...
if not exist "venv" (
    echo [INFO] Creating new virtual environment using Python %PY_VER%...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        color 0C
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b
    )
    echo [SUCCESS] Virtual environment created successfully.
) else (
    echo [SUCCESS] Virtual environment already exists.
)
echo.

:: 3. Activate Virtual Environment
echo [STEP 3] Activating Virtual Environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b
)
echo [SUCCESS] Virtual environment activated!
echo.

:: 4. Check requirements installation using a sentinel file
echo [STEP 4] Checking package requirements...
if not exist "venv\.requirements_installed" (
    echo [INFO] Installing required libraries from requirements.txt...
    echo This may take a few minutes depending on your internet connection.
    echo Please wait...
    echo.
    
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    if %ERRORLEVEL% neq 0 (
        color 0C
        echo.
        echo [ERROR] Package installation failed! 
        echo Please check your internet connection and try running again.
        pause
        exit /b
    )
    
    :: Create sentinel file to skip installation next time
    echo Installed on %date% at %time% > "venv\.requirements_installed"
    color 0B
    echo.
    echo [SUCCESS] All requirements installed successfully!
) else (
    echo [SUCCESS] Requirements are already installed. Skipping installation!
    echo [TIP] To force reinstall, delete the file 'venv\.requirements_installed'.
)
echo.

:: 5. Launch the Application and Web Browser
echo [STEP 5] Starting Flask Web Server...
echo.
echo =======================================================================
echo  SISTEM SEDANG BERJALAN!
echo  Aplikasi akan otomatis dibuka di Web Browser Anda.
echo  Jika tidak terbuka, silakan kunjungi: http://127.0.0.1:5000
echo =======================================================================
echo.

:: Start a background task to open the browser after 3 seconds using robust ping method
start /b cmd /c "ping -n 4 127.0.0.1 >nul && start http://127.0.0.1:5000"

:: Run the Flask app
python app.py

:: Deactivate virtual env on close (if it gets here)
call deactivate
pause
