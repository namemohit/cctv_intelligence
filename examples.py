"""
Example usage scripts for YOLOv8 CCTV/DVR Detection System

This module demonstrates different ways to use the detection system
for various CCTV/DVR scenarios.
"""

from yolo_dvr_detector import YOLODVRDetector, DetectionLogger
from config import *
import logging


def example_1_single_video_file():
    """Example 1: Process a single video file with basic logging."""
    print("\n" + "="*50)
    print("EXAMPLE 1: Single Video File Processing")
    print("="*50 + "\n")

    # Initialize
    logger = DetectionLogger(LOG_DIR)
    detector = YOLODVRDetector(YOLO_MODEL, CONFIDENCE_THRESHOLD)

    # Process video
    stats = detector.process_video(
        video_source="/path/to/your/video.mp4",
        output_logger=logger,
        skip_frames=1,
        max_frames=None,
        draw_boxes=False
    )

    logger.print_summary()
    print(f"\nStats: {stats}")


def example_2_rtsp_stream():
    """Example 2: Process live RTSP stream from CCTV camera."""
    print("\n" + "="*50)
    print("EXAMPLE 2: Live RTSP Stream Processing")
    print("="*50 + "\n")

    logger = DetectionLogger(LOG_DIR)
    detector = YOLODVRDetector(YOLO_MODEL, CONFIDENCE_THRESHOLD)

    # RTSP stream from IP camera
    rtsp_url = "rtsp://192.168.1.100:554/stream1"

    print(f"Connecting to RTSP stream: {rtsp_url}")

    stats = detector.process_video(
        video_source=rtsp_url,
        output_logger=logger,
        skip_frames=2,  # Skip every other frame for real-time performance
        max_frames=1000  # Process 1000 frames for demo
    )

    logger.print_summary()


def example_3_multiple_cameras():
    """Example 3: Process multiple camera streams sequentially."""
    print("\n" + "="*50)
    print("EXAMPLE 3: Multiple Camera Streams")
    print("="*50 + "\n")

    logger = DetectionLogger(LOG_DIR)
    detector = YOLODVRDetector(YOLO_MODEL, CONFIDENCE_THRESHOLD)

    cameras = {
        "entrance": "rtsp://192.168.1.100:554/stream1",
        "parking_lot": "rtsp://192.168.1.101:554/stream1",
        "hallway": "rtsp://192.168.1.102:554/stream1",
    }

    for camera_name, rtsp_url in cameras.items():
        print(f"\nProcessing camera: {camera_name}")
        print(f"RTSP URL: {rtsp_url}")

        try:
            stats = detector.process_video(
                video_source=rtsp_url,
                output_logger=logger,
                skip_frames=3,
                max_frames=500
            )
            print(f"✓ Processed {stats['processed_frames']} frames")
        except Exception as e:
            print(f"✗ Error processing {camera_name}: {e}")

    logger.print_summary()


def example_4_with_visualization():
    """Example 4: Process video with bounding box visualization."""
    print("\n" + "="*50)
    print("EXAMPLE 4: Video with Visualization")
    print("="*50 + "\n")

    logger = DetectionLogger(LOG_DIR)
    detector = YOLODVRDetector(YOLO_MODEL, CONFIDENCE_THRESHOLD)

    stats = detector.process_video(
        video_source="/path/to/your/video.mp4",
        output_logger=logger,
        skip_frames=1,
        draw_boxes=True,
        output_video="output_with_boxes.mp4"
    )

    logger.print_summary()
    print(f"\nAnnotated video saved: output_with_boxes.mp4")


def example_5_batch_processing():
    """Example 5: Batch process multiple video files."""
    print("\n" + "="*50)
    print("EXAMPLE 5: Batch Video Processing")
    print("="*50 + "\n")

    import os
    from pathlib import Path

    logger = DetectionLogger(LOG_DIR)
    detector = YOLODVRDetector(YOLO_MODEL, CONFIDENCE_THRESHOLD)

    video_directory = "/path/to/videos"
    video_files = list(Path(video_directory).glob("*.mp4"))

    print(f"Found {len(video_files)} video files")

    for i, video_file in enumerate(video_files, 1):
        print(f"\nProcessing video {i}/{len(video_files)}: {video_file.name}")

        try:
            stats = detector.process_video(
                video_source=str(video_file),
                output_logger=logger,
                skip_frames=2,
                max_frames=2000
            )
            print(f"✓ Detections: {stats['total_detections']}")
        except Exception as e:
            print(f"✗ Error: {e}")

    logger.print_summary()


def example_6_high_performance():
    """Example 6: High-performance configuration for real-time processing."""
    print("\n" + "="*50)
    print("EXAMPLE 6: High-Performance Real-Time Processing")
    print("="*50 + "\n")

    logger = DetectionLogger(LOG_DIR)

    # Use lighter model and aggressive frame skipping
    detector = YOLODVRDetector("yolov8n.pt", CONFIDENCE_THRESHOLD)

    stats = detector.process_video(
        video_source="rtsp://192.168.1.100:554/stream1",
        output_logger=logger,
        skip_frames=5,  # Process every 5th frame for speed
        max_frames=2000
    )

    print(f"\nProcessing Speed: {stats['processed_frames']} frames/run")


def example_7_continuous_monitoring():
    """Example 7: Continuous monitoring with loop (for 24/7 surveillance)."""
    print("\n" + "="*50)
    print("EXAMPLE 7: Continuous Monitoring")
    print("="*50 + "\n")

    detector = YOLODVRDetector(YOLO_MODEL, CONFIDENCE_THRESHOLD)
    rtsp_url = "rtsp://192.168.1.100:554/stream1"

    max_iterations = 10  # Change to continuous monitoring
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Monitoring Cycle {iteration} ---")

        logger = DetectionLogger(LOG_DIR)

        try:
            stats = detector.process_video(
                video_source=rtsp_url,
                output_logger=logger,
                skip_frames=5,
                max_frames=500
            )
            print(f"Detections this cycle: {stats['total_detections']}")

        except Exception as e:
            print(f"Error in monitoring cycle: {e}")
            # Reconnect logic here

    print("\nMonitoring completed")


def example_8_with_alerts():
    """Example 8: Detection with alert system."""
    print("\n" + "="*50)
    print("EXAMPLE 8: Detection with Alerts")
    print("="*50 + "\n")

    logger = DetectionLogger(LOG_DIR)
    detector = YOLODVRDetector(YOLO_MODEL, CONFIDENCE_THRESHOLD)

    alert_classes = ["person", "car"]  # Trigger alerts for these
    alert_count = {cls: 0 for cls in alert_classes}

    import cv2
    cap = cv2.VideoCapture("/path/to/your/video.mp4")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        detections = detector.detect_frame(frame)

        # Check for alerts
        for detection in detections:
            if detection['class_name'] in alert_classes:
                alert_count[detection['class_name']] += 1

                # Trigger alert
                print(f"\n🚨 ALERT: {detection['class_name']} detected! "
                      f"(Confidence: {detection['confidence']:.2f})")

                # Here you could:
                # - Send email notification
                # - Sound alarm
                # - Save frame snapshot
                # - Log to database

        if frame_count >= 1000:  # Demo limit
            break

    cap.release()

    print(f"\nAlert Summary:")
    for cls, count in alert_count.items():
        print(f"  {cls}: {count} detections")


# ============================================
# Run Examples
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("YOLOv8 CCTV/DVR Detection System - Examples")
    print("="*60)

    print("\nAvailable Examples:")
    print("1. Single video file processing")
    print("2. Live RTSP stream processing")
    print("3. Multiple camera streams")
    print("4. Video with visualization")
    print("5. Batch video processing")
    print("6. High-performance real-time processing")
    print("7. Continuous monitoring (24/7)")
    print("8. Detection with alerts")

    choice = input("\nSelect example (1-8) or 'q' to quit: ").strip()

    examples = {
        '1': example_1_single_video_file,
        '2': example_2_rtsp_stream,
        '3': example_3_multiple_cameras,
        '4': example_4_with_visualization,
        '5': example_5_batch_processing,
        '6': example_6_high_performance,
        '7': example_7_continuous_monitoring,
        '8': example_8_with_alerts,
    }

    if choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            print(f"\nError running example: {e}")
            import traceback
            traceback.print_exc()
    elif choice.lower() != 'q':
        print("Invalid selection")
