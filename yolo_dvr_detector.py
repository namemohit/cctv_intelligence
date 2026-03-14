"""
YOLOv8n CCTV/DVR Instance Detection and Logging System

This module provides real-time and batch processing of CCTV/DVR feeds
using YOLOv8n object detection model with comprehensive logging capabilities.
"""

import cv2
import json
import csv
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import logging
import numpy as np
from ultralytics import YOLO
import argparse


class DetectionLogger:
    """Handles logging of detection instances to multiple formats."""

    def __init__(self, output_dir: str = "detections_log"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # Initialize log files
        self.csv_file = self.output_dir / f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.json_file = self.output_dir / f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.db_file = self.output_dir / f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

        # Initialize CSV
        self.csv_initialized = False

        # Initialize database
        self.init_database()

        # Statistics tracking
        self.detection_stats = defaultdict(int)
        self.total_detections = 0

    def setup_logging(self):
        """Setup Python logging to file."""
        log_file = self.output_dir / f"yolo_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def init_database(self):
        """Initialize SQLite database for detections."""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
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
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON detections(timestamp);
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_class ON detections(class_name);
        ''')

        conn.commit()
        conn.close()

    def log_detections(self, detections: List[Dict], frame_num: int, source: str = "CCTV"):
        """
        Log detected instances to all formats.

        Args:
            detections: List of detection dictionaries with keys:
                       - class_id, class_name, confidence, bbox (x1,y1,x2,y2)
            frame_num: Frame number from video
            source: Source identifier (camera name/ID)
        """
        timestamp = datetime.now().isoformat()

        for detection in detections:
            # Update statistics
            self.detection_stats[detection['class_name']] += 1
            self.total_detections += 1

            # Log to CSV
            self._log_to_csv(detection, frame_num, source, timestamp)

            # Log to JSON
            self._log_to_json(detection, frame_num, source, timestamp)

            # Log to database
            self._log_to_database(detection, frame_num, source, timestamp)

            # Console output
            self.logger.info(
                f"[{source}] Frame {frame_num} | {detection['class_name']} "
                f"(conf: {detection['confidence']:.2f}) | "
                f"BBox: {detection['bbox']}"
            )

    def _log_to_csv(self, detection: Dict, frame_num: int, source: str, timestamp: str):
        """Log detection to CSV file."""
        csv_data = {
            'timestamp': timestamp,
            'source': source,
            'frame_number': frame_num,
            'class_id': detection['class_id'],
            'class_name': detection['class_name'],
            'confidence': f"{detection['confidence']:.4f}",
            'x_min': int(detection['bbox'][0]),
            'y_min': int(detection['bbox'][1]),
            'x_max': int(detection['bbox'][2]),
            'y_max': int(detection['bbox'][3]),
            'width': int(detection['bbox'][2] - detection['bbox'][0]),
            'height': int(detection['bbox'][3] - detection['bbox'][1])
        }

        if not self.csv_initialized:
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=csv_data.keys())
                writer.writeheader()
                writer.writerow(csv_data)
            self.csv_initialized = True
        else:
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=csv_data.keys())
                writer.writerow(csv_data)

    def _log_to_json(self, detection: Dict, frame_num: int, source: str, timestamp: str):
        """Log detection to JSON file."""
        json_data = {
            'timestamp': timestamp,
            'source': source,
            'frame_number': frame_num,
            'class_id': detection['class_id'],
            'class_name': detection['class_name'],
            'confidence': float(f"{detection['confidence']:.4f}"),
            'bbox': {
                'x_min': int(detection['bbox'][0]),
                'y_min': int(detection['bbox'][1]),
                'x_max': int(detection['bbox'][2]),
                'y_max': int(detection['bbox'][3]),
                'width': int(detection['bbox'][2] - detection['bbox'][0]),
                'height': int(detection['bbox'][3] - detection['bbox'][1])
            }
        }

        # Append to JSON file
        existing_data = []
        if self.json_file.exists():
            try:
                with open(self.json_file, 'r') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []

        existing_data.append(json_data)

        with open(self.json_file, 'w') as f:
            json.dump(existing_data, f, indent=2)

    def _log_to_database(self, detection: Dict, frame_num: int, source: str, timestamp: str):
        """Log detection to SQLite database."""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO detections (
                timestamp, source, frame_number, class_id, class_name,
                confidence, x_min, y_min, x_max, y_max, width, height
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            source,
            frame_num,
            detection['class_id'],
            detection['class_name'],
            float(detection['confidence']),
            int(detection['bbox'][0]),
            int(detection['bbox'][1]),
            int(detection['bbox'][2]),
            int(detection['bbox'][3]),
            int(detection['bbox'][2] - detection['bbox'][0]),
            int(detection['bbox'][3] - detection['bbox'][1])
        ))

        conn.commit()
        conn.close()

    def get_statistics(self) -> Dict:
        """Get detection statistics."""
        return {
            'total_detections': self.total_detections,
            'classes_detected': dict(self.detection_stats),
            'timestamp': datetime.now().isoformat()
        }

    def print_summary(self):
        """Print detection summary."""
        stats = self.get_statistics()
        self.logger.info("\n" + "="*50)
        self.logger.info("DETECTION SUMMARY")
        self.logger.info("="*50)
        self.logger.info(f"Total Detections: {stats['total_detections']}")
        self.logger.info("Detections by Class:")
        for class_name, count in stats['classes_detected'].items():
            self.logger.info(f"  - {class_name}: {count}")
        self.logger.info(f"Log Files:")
        self.logger.info(f"  - CSV: {self.csv_file}")
        self.logger.info(f"  - JSON: {self.json_file}")
        self.logger.info(f"  - Database: {self.db_file}")
        self.logger.info("="*50 + "\n")


class YOLODVRDetector:
    """Main YOLO detector for CCTV/DVR streams."""

    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.5):
        """
        Initialize YOLO detector.

        Args:
            model_name: YOLO model to use (yolov8n, yolov8s, etc.)
            conf_threshold: Confidence threshold for detections
        """
        self.model = YOLO(model_name)
        self.conf_threshold = conf_threshold
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Loaded model: {model_name}")

    def detect_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in a frame.

        Args:
            frame: Input frame (BGR format from OpenCV)

        Returns:
            List of detection dictionaries
        """
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        detections = []

        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    detection = {
                        'class_id': int(box.cls),
                        'class_name': self.model.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'bbox': [
                            float(box.xyxy[0][0]),
                            float(box.xyxy[0][1]),
                            float(box.xyxy[0][2]),
                            float(box.xyxy[0][3])
                        ]
                    }
                    detections.append(detection)

        return detections

    def process_video(self, video_source: str, output_logger: DetectionLogger,
                     skip_frames: int = 1, max_frames: Optional[int] = None,
                     draw_boxes: bool = False, output_video: Optional[str] = None) -> Dict:
        """
        Process video from file or stream.

        Args:
            video_source: Path to video file or RTSP stream URL
            output_logger: DetectionLogger instance
            skip_frames: Process every nth frame (for performance)
            max_frames: Maximum frames to process (None = all)
            draw_boxes: Draw bounding boxes on output video
            output_video: Save annotated video to this path

        Returns:
            Processing statistics
        """
        cap = cv2.VideoCapture(video_source)

        if not cap.isOpened():
            self.logger.error(f"Failed to open video source: {video_source}")
            return {'success': False, 'error': 'Failed to open video source'}

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.logger.info(f"Video properties: {width}x{height}, {fps:.2f} FPS, {total_frames} frames")

        # Setup video writer if requested
        out = None
        if draw_boxes and output_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

        frame_count = 0
        processed_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1

                # Skip frames for performance
                if frame_count % skip_frames != 0:
                    continue

                processed_count += 1

                # Detect objects
                detections = self.detect_frame(frame)

                # Log detections
                if detections:
                    output_logger.log_detections(detections, frame_count,
                                                source=Path(video_source).stem)

                # Draw boxes if requested
                if draw_boxes and detections:
                    frame = self._draw_detections(frame, detections)

                # Write to output video
                if out:
                    out.write(frame)

                # Check max frames limit
                if max_frames and processed_count >= max_frames:
                    break

                # Progress logging
                if processed_count % 100 == 0:
                    self.logger.info(f"Processed {processed_count} frames ({frame_count} total)")

        finally:
            cap.release()
            if out:
                out.release()

        stats = {
            'success': True,
            'total_frames': frame_count,
            'processed_frames': processed_count,
            'total_detections': output_logger.total_detections,
            'video_source': video_source
        }

        return stats

    @staticmethod
    def _draw_detections(frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw bounding boxes and labels on frame."""
        for detection in detections:
            x1, y1, x2, y2 = [int(v) for v in detection['bbox']]

            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            label = f"{detection['class_name']} {detection['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='YOLOv8n CCTV/DVR Detection and Logging'
    )
    parser.add_argument('video_source',
                       help='Video file path or RTSP stream URL')
    parser.add_argument('--model', default='yolov8n.pt',
                       help='YOLO model name (default: yolov8n.pt)')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Confidence threshold (default: 0.5)')
    parser.add_argument('--skip-frames', type=int, default=1,
                       help='Process every nth frame (default: 1)')
    parser.add_argument('--max-frames', type=int, default=None,
                       help='Maximum frames to process')
    parser.add_argument('--draw-boxes', action='store_true',
                       help='Draw bounding boxes on frames')
    parser.add_argument('--output-video', type=str,
                       help='Save annotated video to this path')
    parser.add_argument('--log-dir', default='detections_log',
                       help='Directory for log files (default: detections_log)')

    args = parser.parse_args()

    # Initialize logger
    logger = DetectionLogger(args.log_dir)

    # Initialize detector
    detector = YOLODVRDetector(args.model, args.conf)

    # Process video
    print("\n" + "="*50)
    print("Starting CCTV/DVR Detection")
    print("="*50 + "\n")

    stats = detector.process_video(
        args.video_source,
        logger,
        skip_frames=args.skip_frames,
        max_frames=args.max_frames,
        draw_boxes=args.draw_boxes,
        output_video=args.output_video
    )

    # Print summary
    logger.print_summary()
    print(f"\nProcessing Statistics:")
    print(f"  Total frames: {stats['total_frames']}")
    print(f"  Processed frames: {stats['processed_frames']}")
    print(f"  Total detections: {stats['total_detections']}")


if __name__ == "__main__":
    main()
