# Quick Start Guide

## Installation (5 minutes)

### Windows
```batch
# Run setup from PowerShell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## Running Detection

### 1. Process a Video File
```bash
python yolo_dvr_detector.py "C:\path\to\video.mp4"
```

### 2. Connect to IP Camera (RTSP)
```bash
python yolo_dvr_detector.py "rtsp://192.168.1.100:554/stream1"
```

### 3. Save Annotated Video
```bash
python yolo_dvr_detector.py video.mp4 --draw-boxes --output-video output.mp4
```

### 4. View Results
Results are saved to `detections_log/` folder:
- **detections_*.csv** - Spreadsheet format
- **detections_*.json** - Structured data format
- **detections_*.db** - Database with all detections

## Configuration

Edit `config.py` to set:
- Your camera RTSP URLs
- Detection confidence level
- Which classes to detect
- Log directory location

## Common Scenarios

### Scenario 1: Single Security Camera
```bash
python yolo_dvr_detector.py "rtsp://192.168.1.100:554/stream1" --conf 0.6
```

### Scenario 2: DVR with Multiple Cameras
```python
# Edit config.py
CAMERA_CONFIG = {
    "entrance": "rtsp://192.168.1.100:554/ch1",
    "parking": "rtsp://192.168.1.100:554/ch2",
    "hallway": "rtsp://192.168.1.100:554/ch3",
}

# Then run examples.py and select option 3
python examples.py
```

### Scenario 3: Process Video Files in Folder
```python
# Run examples.py, select option 5
python examples.py
```

### Scenario 4: Real-Time Monitoring with Alerts
```python
# Run examples.py, select option 8
python examples.py
```

## Checking Results

### View CSV Results
Open `detections_log/detections_*.csv` in Excel

### Query Database
```bash
# Install SQLite browser
# https://sqlitebrowser.org/

# Or query from Python:
python -c "
import sqlite3
db = sqlite3.connect('detections_log/detections_*.db')
c = db.cursor()
c.execute('SELECT class_name, COUNT(*) FROM detections GROUP BY class_name')
for row in c:
    print(f'{row[0]}: {row[1]}')
"
```

### View JSON Results
Open `detections_log/detections_*.json` in any text editor

## Performance Tips

1. **For faster processing**, use skip frames:
   ```bash
   python yolo_dvr_detector.py video.mp4 --skip-frames 5
   ```

2. **For better detection**, increase max frames:
   ```bash
   python yolo_dvr_detector.py video.mp4 --max-frames 5000
   ```

3. **For GPU acceleration**, use NVIDIA GPU:
   - Install CUDA: https://developer.nvidia.com/cuda-downloads
   - GPU will be detected automatically

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Run `pip install -r requirements.txt` |
| RTSP won't connect | Check URL format: `rtsp://ip:port/stream` |
| Slow processing | Use `--skip-frames 3` or larger model |
| Out of memory | Reduce skip-frames or use yolov8n model |
| GPU not detected | Install CUDA and cuDNN |

## Next Steps

1. ✅ Install and test (this guide)
2. 📹 Configure your cameras in `config.py`
3. 🚀 Start detection with `python examples.py`
4. 📊 Analyze results in `detections_log/`
5. 🔔 Set up alerts if needed (see examples.py)

## Getting Help

- Check README.md for detailed documentation
- Review examples.py for different use cases
- See YOLO docs: https://docs.ultralytics.com

Happy monitoring! 🎥🔍
