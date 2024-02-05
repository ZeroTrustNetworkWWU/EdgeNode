@echo off

REM Check if venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    REM Activate existing venv
    call venv\Scripts\activate.bat
)

start cmd /k venv\Scripts\python.exe src\EdgeNode.py