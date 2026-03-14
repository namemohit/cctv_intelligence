# Project File Structure and Guide

## Overview

Complete YOLOv8n CCTV/DVR detection system with multi-format logging and real-time processing capabilities.

## File Directory

```
yolo_dvr_detection/
├── yolo_dvr_detector.py      ⭐ Main detection engine
├── config.py                 📋 Configuration settings
├── examples.py               📚 Usage examples
├── analyze_detections.py     📊 Analysis and querying tool
├── setup.sh                  🐧 Linux/Mac setup script
├── setup.bat                 🪟 Windows setup script
├── requirements.txt          📦 Python dependencies
├── README.md                 📖 Full documentation
├── QUICKSTART.md             ⚡ 5-minute quick start
├── FILE_STRUCTURE.md         📑 This file
└── detections_log/           📁 Output logs (created at runtime)
    ├── detections_*.csv
    ├── detections_*.json
    ├── detections_*.db
    └── yolo_detection_*.log
```

## File Descriptions

### Core Application Files

**yolo_dvr_detector.py** (800+ lines)
- Main detection engine
- `YOLODVRDetector` class: YOLO inference and frame processing
- `DetectionLogger` class: Multi-format logging (CSV, JSON, SQLite)
- Command-line interface for running detections
- Bounding box drawing and video annotation
- Frame-by-frame detection processing

**config.py** (200+ lines)
- Centralized configuration management
- Model selection and thresholds
- Video source configuration
- Processing parameters
- Logging options
- Camera setup for multi-camera systems
- Database and performance tuning

**examples.py** (500+ lines)
- 8 practical usage examples:
  1. Single video file processing
  2. Live RTSP stream from IP camera
  3. Multiple camera streams
  4. Video with visualization
  5. Batch video processing
  6. High-performance real-time
  7. Continuous 24/7 monitoring
  8. Detection with alert system
- Interactive menu to select and run examples

**analyze_detections.py** (400+ lines)
- Query and analyze detection results
- `DetectionAnalyzer` class with methods for:
  - Summary statistics
  - Detections by class
  - Detections by camera/source
  - Time-based analysis
  - High confidence filtering
  - Time range queries
  - CSV export
  - Report generation
- Command-line tool for database queries

### Setup and Configuration

**setup.sh** (Linux/Mac)
- Automated setup script
- Creates Python virtual environment
- Installs dependencies
- Downloads YOLOv8n model
- Validates installation
- Creates necessary directories

**setup.bat** (Windows)
- Windows equivalent of setup.sh
- PowerShell/CMD compatible
- Automatic model download
- Error checking at each step

**requirements.txt**
- Python package dependencies
- YOLO framework (ultralytics)
- OpenCV for video processing
- NumPy for numerical operations
- PyYAML, Pillow, matplotlib
- Optional: Flask for web UI, scikit-learn

### Documentation

**README.md** (Comprehensive, 600+ lines)
- Full feature overview
- Installation instructions for all platforms
- Quick start examples
- Detailed configuration guide
- Usage examples with code
- Output file formats (CSV, JSON, SQLite)
- Performance optimization tips
- SQL query examples
- Model selection guide
- CCTV/DVR integration instructions
- Troubleshooting section

**QUICKSTART.md** (Fast track, 150+ lines)
- 5-minute setup guide
- Installation for Windows/Linux/Mac
- 4 common scenarios with commands
- Performance tips
- Troubleshooting table
- Getting help resources

**FILE_STRUCTURE.md** (This file)
- Project organization
- File descriptions
- Usage workflow
- Key features per file

## Quick Start Workflow

### 1. Installation
```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh
./setup.sh
```

### 2. Configuration
Edit `config.py` to add your camera URLs:
```python
CAMERA_CONFIG = {
    "entrance": "rtsp://192.168.1.100:554/stream1",
}
```

### 3. Run Detection
```bash
# Option A: Use command line
python yolo_dvr_detector.py "rtsp://192.168.1.100:554/stream1"

# Option B: Use examples menu
python examples.py

# Option C: Custom Python script
from yolo_dvr_detector import YOLODVRDetector, DetectionLogger
```

### 4. Analyze Results
```bash
# View summary
python analyze_detections.py summary

# Query database
python analyze_detections.py classes

# Export to CSV
python analyze_detections.py export --output results.csv
```

## Key Features by File

### Detection (yolo_dvr_detector.py)
- ✅ Real-time RTSP streaming
- ✅ Video file processing
- ✅ Multi-format logging
- ✅ Bounding box visualization
- ✅ Frame skipping for performance
- ✅ Confidence filtering
- ✅ SQLite database with indexing

### Configuration (config.py)
- ✅ Model selection (n/s/m/l/x)
- ✅ Multi-camera setup
- ✅ Detection thresholds
- ✅ GPU/CPU selection
- ✅ Logging format options
- ✅ Performance tuning
- ✅ Alert configuration

### Examples (examples.py)
- ✅ Single camera
- ✅ RTSP streaming
- ✅ Multiple cameras
- ✅ Visualization
- ✅ Batch processing
- ✅ High-performance mode
- ✅ Continuous monitoring
- ✅ Alert system

### Analysis (analyze_detections.py)
- ✅ Summary statistics
- ✅ Class distribution
- ✅ Camera breakdown
- ✅ Time-based analysis
- ✅ High confidence queries
- ✅ Time range filtering
- ✅ CSV export
- ✅ Report generation

## Output Files Created

### Log Directory Structure
```
detections_log/
├── detections_20240313_120000.csv
│   └── timestamp, source, class, confidence, bbox coordinates
├── detections_20240313_120000.json
│   └── Structured detection data with metadata
├── detections_20240313_120000.db
│   └── SQLite database with indexed tables
└── yolo_detection_20240313_120000.log
    └── Detailed operation logs
```

### Database Schema
```
detections table:
- id (integer, primary key)
- timestamp (text)
- source (text) - camera name
- frame_number (integer)
- class_id (integer)
- class_name (text)
- confidence (real, 0-1)
- x_min, y_min, x_max, y_max (integer)
- width, height (integer)

Indexes:
- idx_timestamp ON timestamp
- idx_class ON class_name
```

## Common Use Cases

### Use Case 1: Single Security Camera
```
config.py → Configure RTSP URL → yolo_dvr_detector.py → analyze_detections.py
```

### Use Case 2: Multi-Camera DVR System
```
config.py → CAMERA_CONFIG → examples.py (option 3) → analyze_detections.py
```

### Use Case 3: Batch Video Processing
```
config.py → VIDEO_SOURCES → examples.py (option 5) → analyze_detections.py
```

### Use Case 4: Real-Time Alerts
```
examples.py (option 8) → Custom alert logic → analyze_detections.py
```

## System Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- 1GB disk space
- CPU: Any modern processor

### Recommended
- Python 3.9+
- 8GB+ RAM
- 10GB disk space (for logs)
- GPU: NVIDIA with CUDA

### Network
- For RTSP: Direct network access to cameras
- Bandwidth: 1-5 Mbps per camera stream

## Customization Points

### Modify Detection Logic
File: `yolo_dvr_detector.py`
- `detect_frame()` - Add custom post-processing
- `_draw_detections()` - Custom visualization

### Add Alert System
File: `examples.py`
- Example 8 shows basic alert structure
- Extend with email/SMS/webhook

### Custom Analysis
File: `analyze_detections.py`
- Add new query methods
- Create custom reports
- Integration with dashboards

### Performance Tuning
File: `config.py`
- Adjust SKIP_FRAMES
- Change model size
- Enable GPU acceleration
- Tune batch size

## Support and Help

1. **Quick Issues**: Check QUICKSTART.md troubleshooting
2. **Detailed Help**: Read README.md sections
3. **Examples**: Run examples.py for reference
4. **Analysis**: Use analyze_detections.py to query results
5. **Code**: Review docstrings in source files

## Version Information

- **YOLOv8n**: Object detection model
- **OpenCV**: Video processing
- **SQLite**: Database
- **Python**: 3.8+

---

**Ready to start? Begin with setup.sh/setup.bat, then read QUICKSTART.md!** 🎬🔍
