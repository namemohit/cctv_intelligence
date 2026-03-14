#!/bin/bash

# YOLOv8 CCTV/DVR Detection System Setup Script

echo "============================================"
echo "YOLOv8 CCTV/DVR Detection System Setup"
echo "============================================"
echo ""

# Check Python version
echo "Checking Python installation..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ Pip upgraded"
echo ""

# Install requirements
echo "Installing required packages..."
pip install -r requirements.txt
echo "✓ Requirements installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p detections_log
mkdir -p videos
mkdir -p output
echo "✓ Directories created"
echo ""

# Download YOLOv8n model
echo "Downloading YOLOv8n model..."
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
echo "✓ YOLOv8n model downloaded"
echo ""

# Test installation
echo "Testing installation..."
python3 -c "
from ultralytics import YOLO
import cv2
import numpy as np
print('✓ YOLO import successful')
print('✓ OpenCV import successful')
print('✓ NumPy import successful')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "✓ Setup completed successfully!"
    echo "============================================"
    echo ""
    echo "Next steps:"
    echo "1. Configure your video sources in config.py"
    echo "2. Run: python examples.py"
    echo "3. Or use: python yolo_dvr_detector.py <video_file>"
    echo ""
    echo "For real-time RTSP stream:"
    echo "  python yolo_dvr_detector.py 'rtsp://192.168.1.100:554/stream1'"
    echo ""
    echo "With visualization:"
    echo "  python yolo_dvr_detector.py 'video.mp4' --draw-boxes --output-video output.mp4"
    echo ""
else
    echo ""
    echo "✗ Setup failed. Please check the error messages above."
    exit 1
fi
