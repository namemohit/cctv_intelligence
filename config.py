"""
Configuration settings for YOLOv8 CCTV/DVR Detection System
"""

import os
from typing import Dict, List

# ============================================
# YOLO Model Configuration
# ============================================

# Model selection: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
YOLO_MODEL = "yolov8n.pt"  # Using nano for faster processing on DVR

# Confidence threshold (0-1)
CONFIDENCE_THRESHOLD = 0.5

# Classes to detect (None = all classes)
# Example: ["person", "car", "bus"]
TARGET_CLASSES = None

# ============================================
# Video Input Configuration
# ============================================

# Video sources can be:
# - File paths: "/path/to/video.mp4"
# - RTSP streams: "rtsp://192.168.1.100:554/stream1"
# - IP camera streams: "http://192.168.1.100/video"
# - Multiple sources in list format

VIDEO_SOURCES = [
    # "rtsp://192.168.1.100:554/stream1",  # Example RTSP stream
    # "rtsp://192.168.1.100:554/stream2",  # Multiple cameras
    # "/path/to/video.mp4",                 # Video file
]

# ============================================
# Processing Configuration
# ============================================

# Process every nth frame (1 = all frames, 5 = every 5th frame)
SKIP_FRAMES = 1

# Maximum frames to process (None = all)
MAX_FRAMES = None

# Enable GPU acceleration (requires CUDA)
USE_GPU = True

# Batch processing size (larger = faster but more memory)
BATCH_SIZE = 1

# ============================================
# Logging Configuration
# ============================================

# Directory to store detection logs
LOG_DIR = "detections_log"

# Log formats to enable
ENABLE_CSV_LOG = True
ENABLE_JSON_LOG = True
ENABLE_DATABASE_LOG = True
ENABLE_FILE_LOG = True

# ============================================
# Output Video Configuration
# ============================================

# Save annotated video with bounding boxes
SAVE_ANNOTATED_VIDEO = False
ANNOTATED_VIDEO_PATH = "output_annotated.mp4"

# Draw detections on frames
DRAW_BOXES = False

# Video codec (mp4v, MJPG, XVID)
VIDEO_CODEC = "mp4v"

# ============================================
# Advanced Processing Configuration
# ============================================

# Track objects across frames (requires additional setup)
ENABLE_TRACKING = False

# Minimum detection area in pixels (filter small detections)
MIN_DETECTION_AREA = 0

# Maximum detection area in pixels (filter large detections)
MAX_DETECTION_AREA = float('inf')

# ============================================
# Notification Configuration
# ============================================

# Alert on specific detections
ALERT_ENABLED = False
ALERT_CLASSES = ["person", "car", "dog"]  # Trigger alerts for these classes

# Email alerts (requires email configuration)
EMAIL_ALERTS = False
ALERT_EMAIL = "admin@example.com"

# ============================================
# Performance Tuning
# ============================================

# Number of threads for inference
NUM_THREADS = 4

# Memory optimization
OPTIMIZE_MEMORY = True

# Half precision (FP16) for faster inference on compatible GPUs
USE_HALF_PRECISION = True

# ============================================
# Database Configuration
# ============================================

# SQLite database location
DATABASE_PATH = "detections_log/detections.db"

# Enable automatic database cleanup (old entries)
AUTO_CLEANUP_DB = False
DB_RETENTION_DAYS = 30

# ============================================
# Streaming Configuration (if using network streams)
# ============================================

# Connection timeout in seconds
CONNECTION_TIMEOUT = 10

# Reconnection attempts
RECONNECT_ATTEMPTS = 3

# Buffer size for streaming
BUFFER_SIZE = 1024

# ============================================
# Multi-Camera Configuration
# ============================================

# Camera names/IDs for logging
CAMERA_CONFIG = {
    # "camera_1": "rtsp://192.168.1.100:554/stream1",
    # "camera_2": "rtsp://192.168.1.100:554/stream2",
    # "entrance": "/path/to/entrance.mp4",
}

# ============================================
# Helper Functions
# ============================================

def validate_config() -> bool:
    """Validate configuration settings."""
    if not VIDEO_SOURCES and not CAMERA_CONFIG:
        print("ERROR: No video sources configured!")
        return False

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
        print(f"Created log directory: {LOG_DIR}")

    return True


def get_video_sources() -> List[str]:
    """Get list of all configured video sources."""
    sources = list(VIDEO_SOURCES)
    sources.extend(CAMERA_CONFIG.values())
    return [s for s in sources if s]


if __name__ == "__main__":
    print("YOLOv8 CCTV/DVR Configuration")
    print("-" * 50)
    print(f"Model: {YOLO_MODEL}")
    print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}")
    print(f"Skip Frames: {SKIP_FRAMES}")
    print(f"Log Directory: {LOG_DIR}")
    print(f"Use GPU: {USE_GPU}")
    print(f"Draw Boxes: {DRAW_BOXES}")
    print("-" * 50)
