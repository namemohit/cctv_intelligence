@echo off
REM YOLOv8 CCTV/DVR Detection System Setup Script for Windows

setlocal enabledelayedexpansion

echo.
echo ============================================
echo YOLOv8 CCTV/DVR Detection System Setup
echo ============================================
echo.

REM Check Python version
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK - Python version: %PYTHON_VERSION%
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv" (
    echo OK - Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo OK - Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo OK - Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not upgrade pip
) else (
    echo OK - Pip upgraded
)
echo.

REM Install requirements
echo Installing required packages...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo OK - Requirements installed
echo.

REM Create directories
echo Creating directories...
if not exist "detections_log" mkdir detections_log
if not exist "videos" mkdir videos
if not exist "output" mkdir output
echo OK - Directories created
echo.

REM Download YOLOv8n model
echo Downloading YOLOv8n model...
echo This may take a minute...
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not download model
) else (
    echo OK - YOLOv8n model downloaded
)
echo.

REM Test installation
echo Testing installation...
python -c "from ultralytics import YOLO; import cv2; import numpy; print('OK - All imports successful')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Installation test failed
    pause
    exit /b 1
)
echo OK - Installation test passed
echo.

echo ============================================
echo SETUP COMPLETED SUCCESSFULLY!
echo ============================================
echo.
echo Next steps:
echo.
echo 1. Configure your video sources:
echo    - Edit config.py and add your RTSP URLs
echo.
echo 2. Run detection on a video file:
echo    python yolo_dvr_detector.py "C:\path\to\video.mp4"
echo.
echo 3. Connect to RTSP camera:
echo    python yolo_dvr_detector.py "rtsp://192.168.1.100:554/stream1"
echo.
echo 4. View example usage:
echo    python examples.py
echo.
echo For more help, read:
echo - QUICKSTART.md (5-minute guide)
echo - README.md (full documentation)
echo.
pause
