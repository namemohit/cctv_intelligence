# YOLOv8n CCTV/DVR Instance Detection and Logging System

A comprehensive Python system for detecting and logging object instances from CCTV/DVR feeds using YOLOv8n (nano) model. Perfect for security surveillance, monitoring, and analytics.

## Features

✅ **Real-time Detection**
- Process live RTSP streams from IP cameras
- Continuous monitoring with reconnection logic
- High-performance frame skipping for speed

✅ **Multiple Logging Formats**
- CSV files for spreadsheet analysis
- JSON for structured data and APIs
- SQLite database for queries and analytics
- Detailed file logs for debugging

✅ **Flexible Input Sources**
- Video files (MP4, AVI, MOV, etc.)
- RTSP streams from IP cameras
- Multiple simultaneous camera feeds
- DVR direct connections

✅ **Advanced Features**
- Configurable detection thresholds
- Bounding box visualization
- Output video annotation
- Detection statistics and summaries
- Class filtering
- Frame skipping for performance optimization

✅ **Production Ready**
- Comprehensive error handling
- Logging system for monitoring
- Database indexing for fast queries
- Batch processing capabilities
- 24/7 monitoring support

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 4GB+ RAM (8GB recommended for GPU)
- Optional: NVIDIA GPU with CUDA support

### Quick Setup

```bash
# 1. Clone or extract the project
cd yolo_dvr_detection

# 2. Run setup script (Linux/Mac)
chmod +x setup.sh
./setup.sh

# Or manual setup (all platforms):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Download YOLOv8n model (automatic or manual)
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Installation Options

**Option 1: Full Install (Recommended)**
```bash
pip install -r requirements.txt
```

**Option 2: Lightweight (CPU Only)**
```bash
pip install ultralytics opencv-python numpy torch torchvision
```

**Option 3: GPU Support**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

---

## Quick Start

### 1. Basic Video File Processing

```bash
python yolo_dvr_detector.py /path/to/video.mp4
```

### 2. Live RTSP Stream

```bash
python yolo_dvr_detector.py rtsp://192.168.1.100:554/stream1
```

### 3. With Visualization

```bash
python yolo_dvr_detector.py video.mp4 \
  --draw-boxes \
  --output-video output_annotated.mp4
```

### 4. Advanced Options

```bash
python yolo_dvr_detector.py rtsp://camera-ip:554/stream \
  --model yolov8n.pt \
  --conf 0.5 \
  --skip-frames 2 \
  --max-frames 1000 \
  --draw-boxes \
  --log-dir my_detections
```

---

## Configuration

### Via Command Line

```bash
python yolo_dvr_detector.py <video_source> [OPTIONS]

Options:
  --model MODEL              YOLO model (yolov8n.pt, yolov8s.pt, etc.)
  --conf THRESHOLD           Confidence threshold (0-1)
  --skip-frames N            Process every Nth frame
  --max-frames N             Maximum frames to process
  --draw-boxes               Draw detection boxes on frames
  --output-video PATH        Save annotated video
  --log-dir DIR              Log directory
```

### Via config.py

Edit `config.py` for persistent configuration:

```python
# Model and detection
YOLO_MODEL = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.5

# Video sources
VIDEO_SOURCES = [
    "rtsp://192.168.1.100:554/stream1",
    "rtsp://192.168.1.101:554/stream1",
]

# Processing
SKIP_FRAMES = 2
USE_GPU = True

# Logging
LOG_DIR = "detections_log"
ENABLE_CSV_LOG = True
ENABLE_JSON_LOG = True
ENABLE_DATABASE_LOG = True
```

### Camera Configuration

```python
# config.py
CAMERA_CONFIG = {
    "entrance": "rtsp://192.168.1.100:554/stream1",
    "parking_lot": "rtsp://192.168.1.101:554/stream1",
    "hallway": "rtsp://192.168.1.102:554/stream1",
}
```

---

## Usage Examples

### Example 1: Single Video File

```python
from yolo_dvr_detector import YOLODVRDetector, DetectionLogger

logger = DetectionLogger("my_logs")
detector = YOLODVRDetector("yolov8n.pt", conf_threshold=0.5)

stats = detector.process_video(
    video_source="/path/to/video.mp4",
    output_logger=logger,
    skip_frames=1
)

logger.print_summary()
```

### Example 2: Live RTSP Stream

```python
logger = DetectionLogger("surveillance_logs")
detector = YOLODVRDetector("yolov8n.pt", conf_threshold=0.5)

stats = detector.process_video(
    video_source="rtsp://192.168.1.100:554/stream1",
    output_logger=logger,
    skip_frames=2,  # Process every 2nd frame for speed
    max_frames=2000
)
```

### Example 3: Multiple Cameras

```python
logger = DetectionLogger("multi_camera_logs")
detector = YOLODVRDetector("yolov8n.pt")

cameras = {
    "entrance": "rtsp://192.168.1.100:554/stream1",
    "parking": "rtsp://192.168.1.101:554/stream1",
    "hallway": "rtsp://192.168.1.102:554/stream1",
}

for camera_name, rtsp_url in cameras.items():
    print(f"Processing {camera_name}...")
    stats = detector.process_video(rtsp_url, logger, skip_frames=3)
```

### Example 4: Continuous Monitoring

```python
detector = YOLODVRDetector("yolov8n.pt")
rtsp_url = "rtsp://192.168.1.100:554/stream1"

while True:
    logger = DetectionLogger("continuous_log")
    try:
        stats = detector.process_video(
            rtsp_url,
            logger,
            skip_frames=3,
            max_frames=500  # Process 500 frames per cycle
        )
        print(f"Detections: {stats['total_detections']}")
    except Exception as e:
        print(f"Error: {e}")
        # Reconnect logic here
```

### Example 5: Custom Detection with Alerts

```python
import cv2
from yolo_dvr_detector import YOLODVRDetector

detector = YOLODVRDetector("yolov8n.pt")
cap = cv2.VideoCapture("rtsp://192.168.1.100:554/stream1")

alert_classes = ["person", "car"]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    detections = detector.detect_frame(frame)

    # Alert on specific detections
    for detection in detections:
        if detection['class_name'] in alert_classes:
            print(f"🚨 ALERT: {detection['class_name']} detected!")
            # Send email, sound alarm, save frame, etc.
```

---

## Output Files

### Log Directory Structure

```
detections_log/
├── detections_20240313_120000.csv
├── detections_20240313_120000.json
├── detections_20240313_120000.db
└── yolo_detection_20240313_120000.log
```

### CSV Format

```csv
timestamp,source,frame_number,class_id,class_name,confidence,x_min,y_min,x_max,y_max,width,height
2024-03-13T12:00:00.123456,camera1,100,0,person,0.9234,100,50,300,400,200,350
2024-03-13T12:00:01.234567,camera1,105,2,car,0.8765,50,100,450,350,400,250
```

### JSON Format

```json
[
  {
    "timestamp": "2024-03-13T12:00:00.123456",
    "source": "camera1",
    "frame_number": 100,
    "class_id": 0,
    "class_name": "person",
    "confidence": 0.9234,
    "bbox": {
      "x_min": 100,
      "y_min": 50,
      "x_max": 300,
      "y_max": 400,
      "width": 200,
      "height": 350
    }
  }
]
```

### Database Schema

```sql
CREATE TABLE detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    source TEXT NOT NULL,
    frame_number INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    class_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    x_min INTEGER NOT NULL,
    y_min INTEGER NOT NULL,
    x_max INTEGER NOT NULL,
    y_max INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL
);

CREATE INDEX idx_timestamp ON detections(timestamp);
CREATE INDEX idx_class ON detections(class_name);
```

---

## Performance Optimization

### Speed Optimization

```python
# Use lighter model
detector = YOLODVRDetector("yolov8n.pt")  # Fastest

# Skip frames
detector.process_video(video, logger, skip_frames=5)

# Reduce resolution (in config)
# Lower confidence threshold
CONFIDENCE_THRESHOLD = 0.3
```

### Memory Optimization

```python
# In config.py
OPTIMIZE_MEMORY = True
USE_HALF_PRECISION = True
BATCH_SIZE = 1
```

### GPU Acceleration

```python
# In config.py
USE_GPU = True
NUM_THREADS = 4

# Or via command line
python yolo_dvr_detector.py video.mp4
```

---

## Querying Detections

### SQL Queries

```python
import sqlite3

conn = sqlite3.connect('detections_log/detections.db')
cursor = conn.cursor()

# Get all detections
cursor.execute('SELECT * FROM detections')

# Get by class
cursor.execute('SELECT * FROM detections WHERE class_name = "person"')

# Get by time range
cursor.execute('''
    SELECT * FROM detections
    WHERE timestamp BETWEEN '2024-03-13T10:00:00' AND '2024-03-13T12:00:00'
''')

# Count detections by class
cursor.execute('''
    SELECT class_name, COUNT(*) as count
    FROM detections
    GROUP BY class_name
    ORDER BY count DESC
''')

results = cursor.fetchall()
for row in results:
    print(f"{row[0]}: {row[1]}")
```

### Python Analysis

```python
import pandas as pd

# Load CSV
df = pd.read_csv('detections_log/detections.csv')

# Count by class
print(df['class_name'].value_counts())

# Filter by confidence
high_confidence = df[df['confidence'] > 0.9]

# Time-based analysis
df['timestamp'] = pd.to_datetime(df['timestamp'])
hourly_counts = df.set_index('timestamp').resample('1H').size()
```

---

## Troubleshooting

### Issue: CUDA not available

```python
# Use CPU instead
import torch
torch.cuda.is_available()  # Check if GPU available

# Force CPU in config.py
USE_GPU = False
```

### Issue: RTSP Connection Failed

```python
# Check RTSP URL format
rtsp://username:password@192.168.1.100:554/stream1

# Test with ffprobe
ffprobe rtsp://192.168.1.100:554/stream1

# Increase timeout in config.py
CONNECTION_TIMEOUT = 30
```

### Issue: Out of Memory

```python
# Reduce batch size
BATCH_SIZE = 1

# Use lighter model
YOLO_MODEL = "yolov8n.pt"

# Enable memory optimization
OPTIMIZE_MEMORY = True
```

### Issue: Slow Processing

```python
# Skip more frames
--skip-frames 5

# Reduce resolution
# Lower confidence threshold
--conf 0.3

# Use lighter model
--model yolov8n.pt
```

---

## Model Selection

| Model | Speed | Accuracy | Size | Recommended Use |
|-------|-------|----------|------|-----------------|
| yolov8n.pt | ⚡⚡⚡ | ⭐⭐⭐ | ~7MB | Real-time, low resources |
| yolov8s.pt | ⚡⚡ | ⭐⭐⭐⭐ | ~23MB | Balanced |
| yolov8m.pt | ⚡ | ⭐⭐⭐⭐⭐ | ~50MB | High accuracy needed |
| yolov8l.pt | -- | ⭐⭐⭐⭐⭐ | ~98MB | Maximum accuracy |
| yolov8x.pt | -- | ⭐⭐⭐⭐⭐ | ~157MB | Maximum accuracy |

---

## CCTV/DVR Integration

### IP Camera Integration

```bash
# Hikvision cameras
rtsp://username:password@192.168.1.100:554/Streaming/Channels/101

# Dahua cameras
rtsp://username:password@192.168.1.100:554/stream/main

# Generic RTSP
rtsp://192.168.1.100:554/stream1
```

### DVR Connection

```python
# Direct DVR access (if supported)
VIDEO_SOURCES = [
    "rtsp://dvr_ip:554/ch1",
    "rtsp://dvr_ip:554/ch2",
]
```

---

## Advanced Features

### Custom Classes

```python
# In examples.py
TARGET_CLASSES = ["person", "car", "dog"]

# Filter detections
for detection in detections:
    if detection['class_name'] in TARGET_CLASSES:
        logger.log_detections([detection], frame_num)
```

### Alerts and Notifications

```python
# Email alerts
import smtplib
from email.mime.text import MIMEText

def send_alert(detection):
    msg = MIMEText(f"Alert: {detection['class_name']} detected")
    # Send email logic
```

---

## Support

For issues, questions, or contributions:
1. Check the Troubleshooting section
2. Review examples.py for usage patterns
3. Check YOLO documentation: https://docs.ultralytics.com

---

## License

This project uses YOLOv8 which is licensed under the AGPL-3.0 License.

---

## Version History

- **v1.0** - Initial release with YOLOv8n support
  - Multi-format logging (CSV, JSON, SQLite)
  - RTSP stream support
  - Batch processing
  - Real-time monitoring

---

**Happy detecting! 🎬📹🔍**
