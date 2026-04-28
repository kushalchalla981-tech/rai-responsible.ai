@echo off
REM RAI Audit Platform - Quick Start Script for Windows

echo ========================================
echo RAI Audit Platform - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] Checking prerequisites... OK
echo.

REM Setup Backend
echo [2/4] Setting up backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing backend dependencies...
pip install -r requirements.txt

echo Starting backend server...
start "RAI Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

cd ..
echo Backend starting on http://localhost:8000
echo.

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Setup Frontend
echo [3/4] Setting up frontend...
cd frontend

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

echo Starting frontend server...
start "RAI Frontend" cmd /k "npm run dev"

cd ..
echo Frontend starting on http://localhost:3000
echo.

echo [4/4] Opening application...
echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to open the application in your browser...
pause >nul

start http://localhost:3000

echo.
echo The application is now running!
echo.
echo To stop the servers:
echo 1. Close the browser window
echo 2. Press Ctrl+C in the backend terminal
echo 3. Press Ctrl+C in the frontend terminal
echo.
pause