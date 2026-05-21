@echo off
:: Enable local variable scope and UTF-8 output
setlocal enabledelayedexpansion
chcp 65001 >nul

:: Define terminal colors (using ANSI escape codes)
set "ESC="
set "GREEN=%ESC%[92m"
set "CYAN=%ESC%[96m"
set "YELLOW=%ESC%[93m"
set "RED=%ESC%[91m"
set "RESET=%ESC%[0m"

echo =======================================================
echo        GIT REPOSITORY INITIALIZER ^& PUSH TOOL
echo =======================================================
echo.

:: Step 1: Check if Git is installed
echo %CYAN%[1/6] Checking Git installation...%RESET%
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%Error: Git is not installed or not in your PATH. Please install Git first.%RESET%
    goto error
)
echo %GREEN%Git is installed.%RESET%
echo.

:: Step 2: Create a standard .gitignore if not present
echo %CYAN%[2/6] Checking for .gitignore...%RESET%
if not exist .gitignore (
    echo %YELLOW%No .gitignore file found. Creating a standard one to exclude 'venv', temporary, and IDE files...%RESET%
    (
        echo # Virtual Environment
        echo venv/
        echo .venv/
        echo env/
        echo */venv/
        echo */.venv/
        echo */env/
        echo.
        echo # Python Cache and compiled files
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo.
        echo # IDE and Editor settings
        echo .idea/
        echo .vscode/
        echo *.suo
        echo *.ntvs*
        echo *.njsproj
        echo *.sln
        echo *.sw?
        echo.
        echo # Operating System files
        echo Thumbs.db
        echo ehthumbs.db
        echo Desktop.ini
    ) > .gitignore
    echo %GREEN%.gitignore successfully created.%RESET%
) else (
    echo %GREEN%.gitignore already exists.%RESET%
)
echo.

:: Step 3: Initialize Git Repository
echo %CYAN%[3/6] Initializing Git repository...%RESET%
if not exist .git (
    git init
    if %errorlevel% neq 0 (
        echo %RED%Failed to initialize Git repository.%RESET%
        goto error
    )
    echo %GREEN%Git repository initialized successfully.%RESET%
) else (
    echo %GREEN%Git repository already initialized.%RESET%
)
echo.

:: Step 4: Configure Remote Origin URL
echo %CYAN%[4/6] Configuring remote origin to https://github.com/daniasella/VOICE-ANALYSIS ...%RESET%
git remote get-url origin >nul 2>nul
if %errorlevel% equ 0 (
    echo %YELLOW%Remote origin already exists. Updating its URL...%RESET%
    git remote set-url origin https://github.com/daniasella/VOICE-ANALYSIS
) else (
    echo %GREEN%Adding remote origin...%RESET%
    git remote add origin https://github.com/daniasella/VOICE-ANALYSIS
)
if %errorlevel% neq 0 (
    echo %RED%Failed to configure remote origin.%RESET%
    goto error
)
echo %GREEN%Remote origin configured successfully.%RESET%
echo.

:: Step 5: Rename branch to 'main'
echo %CYAN%[5/6] Renaming default branch to 'main'...%RESET%
git branch -M main
if %errorlevel% neq 0 (
    echo %RED%Failed to rename branch to main.%RESET%
    goto error
)
echo %GREEN%Branch successfully set to 'main'.%RESET%
echo.

:: Step 6: Stage, Commit, and Push
echo %CYAN%[6/6] Staging files, committing, and pushing to GitHub...%RESET%
echo Staging all files...
git add .
if %errorlevel% neq 0 (
    echo %RED%Failed to stage files.%RESET%
    goto error
)

echo Committing files...
git commit -m "Initial commit of Voice Analysis project"
:: It's fine if there is nothing new to commit, we can proceed
echo.
echo Pushing to remote 'main' branch on GitHub...
echo %YELLOW%Note: If this is your first time pushing, a GitHub authentication prompt may appear.%RESET%
git push -u origin main
if %errorlevel% neq 0 (
    echo %RED%Failed to push code to GitHub.%RESET%
    goto error
)

echo.
echo =======================================================
echo %GREEN%SUCCESS: Project initialized and pushed successfully!%RESET%
echo =======================================================
goto end

:error
echo.
echo =======================================================
echo %RED%ERROR: The process could not be completed.%RESET%
echo =======================================================

:end
echo.
pause
