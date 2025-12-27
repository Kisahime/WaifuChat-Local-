@echo off
setlocal enabledelayedexpansion

TITLE WaifuChat Local - Installer

echo ===================================================
echo       WaifuChat Local - One-Click Installer
echo ===================================================
echo.

:: 1. Check for Python
echo [1/5] Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10 or newer from python.org and try again.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version
echo Python found!
echo.

:: 2. Create Virtual Environment
echo [2/5] Creating Virtual Environment (venv)...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo venv created.
) else (
    echo venv already exists.
)
echo.

:: 3. Activate venv and Upgrade Pip
echo [3/5] Activating venv and updating pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
echo.

:: 4. Install Dependencies (CUDA)
echo [4/5] Installing Dependencies with NVIDIA CUDA Support...
echo This may take a while depending on your internet speed.
echo.

:: Force reinstall llama-cpp-python with CUDA flags
set CMAKE_ARGS=-DGGML_CUDA=on
pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir

:: Install other requirements
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies.
    echo Ensure you have the NVIDIA CUDA Toolkit installed if you want GPU acceleration.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

:: 5. Download Model
echo [5/5] Downloading AI Model (Llama-3-8B-Stheno)...
echo This is a ~5GB download. Please be patient.
python download_model.py

echo.
echo ===================================================
echo           Installation Complete! 
echo ===================================================
echo.
echo You can now run the app using 'run.bat'
pause
