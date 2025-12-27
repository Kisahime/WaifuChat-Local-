@echo off
TITLE WaifuChat Local
echo Starting WaifuChat...

if not exist "venv" (
    echo [ERROR] Virtual environment not found. Please run 'install.bat' first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
streamlit run app.py
pause
