from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import cv2
import threading
import time
import json
import asyncio
import os
import sys
import socket
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict

# Path handling for PyInstaller standalone mode
def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(os.path.dirname(os.path.abspath(__file__)))

BASE_PATH = get_base_path()
DIST_PATH = BASE_PATH / "frontend" / "dist"

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|analyzeduration;50000000|probesize;50000000"
from pydantic import BaseModel

# Import the existing YOLO detector
from yolo_dvr_detector import YOLODVRDetector, DetectionLogger

app = FastAPI(title="DVR YOLO Integration API")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to hold the current video source and stats
current_video_source = None
latest_stats = {
    "person_count": 0,
    "last_update": time.time(),
    "status": "disconnected",
    "error_message": None,
    "latency_ms": 0
}

# The latest processed frame (JPEG format)
latest_frame = None
frame_lock = threading.Lock()

class VideoSource(BaseModel):
    url: str

@app.post("/api/set_source")
async def set_source(source: VideoSource):
    """Endpoint for the frontend to set the RTSP URL dynamically"""
    global current_video_source
    current_video_source = source.url
    # Reset stats
    latest_stats["status"] = "connecting"
    return {"message": "Source updated successfully", "source": current_video_source}

@app.get("/api/stats")
async def get_stats():
    """Endpoint to get real-time stats (person count, etc.)"""
    return latest_stats


def _get_local_subnet() -> str:
    """Return the local machine's subnet, e.g. '192.168.1' """
    try:
        # Connect to a public IP (no data sent) to find the outbound interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        # Return subnet prefix (first 3 octets)
        return ".".join(local_ip.split(".")[:3])
    except Exception:
        return "192.168.1"


def _probe_host(ip: str, port: int = 554, timeout: float = 0.5) -> Optional[Dict]:
    """Try to open a TCP connection to ip:port. Returns info dict if open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            # Try reverse DNS
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = ip
            return {"ip": ip, "port": port, "hostname": hostname}
    except Exception:
        pass
    return None


@app.get("/api/scan_network")
async def scan_network():
    """Scan the local subnet for devices with port 554 (RTSP) open."""
    subnet = _get_local_subnet()
    hosts = [f"{subnet}.{i}" for i in range(1, 255)]
    found: List[dict] = []

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=60) as executor:
        futures = {executor.submit(_probe_host, ip): ip for ip in hosts}
        results = await loop.run_in_executor(
            None,
            lambda: [f.result() for f in as_completed(futures)]
        )

    found = [r for r in results if r is not None]
    found.sort(key=lambda x: int(x["ip"].split(".")[-1]))
    return {"subnet": subnet, "devices": found, "total_scanned": len(hosts)}

def generate_frames():
    """Background thread to capture and process frames via FFmpeg pipe (handles H.265/HEVC)."""
    import subprocess
    global latest_frame, latest_stats, current_video_source

    # Initialize YOLO detector (nano model for speed)
    print("Initializing YOLO detector...")
    detector = YOLODVRDetector(model_name=str(BASE_PATH / "yolov8n.pt"))
    print("Detector initialized.")

    ffmpeg_proc = None
    last_source = None
    FRAME_W, FRAME_H = 1280, 720
    frame_size = FRAME_W * FRAME_H * 3

    def open_ffmpeg_pipe(url):
        """Open an FFmpeg subprocess that outputs raw BGR24 frames at fixed WxH."""
        # Check for ffmpeg in BASE_PATH (bundled) or local dev path
        bundled_ffmpeg = BASE_PATH / "ffmpeg" / "bin" / "ffmpeg.exe"
        if bundled_ffmpeg.exists():
            ffmpeg_path = str(bundled_ffmpeg)
        else:
            ffmpeg_path = "ffmpeg"
            
        cmd = [
            ffmpeg_path,
            "-hide_banner",
            "-loglevel", "error",
            "-rtsp_transport", "tcp",
            "-timeout", "5000000",
            "-i", url,
            "-vf", f"scale={FRAME_W}:{FRAME_H}",
            "-pix_fmt", "bgr24",
            "-vcodec", "rawvideo",
            "-an", "-sn",
            "-f", "rawvideo",
            "pipe:1"
        ]
        import subprocess
        # Back to DEVNULL to keep things clean
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=frame_size * 5)
    import numpy as np

    while True:
        try:
            if current_video_source is None:
                if latest_stats["status"] != "waiting_for_source":
                    print("Background thread: waiting for source...")
                latest_stats["status"] = "waiting_for_source"
                time.sleep(1)
                continue
            
            if current_video_source != last_source:
                if ffmpeg_proc:
                    ffmpeg_proc.kill()
                    ffmpeg_proc = None
                last_source = current_video_source
                print(f"Background thread source changed to: {current_video_source}")

            if ffmpeg_proc is None or ffmpeg_proc.poll() is not None:
                url = current_video_source
                print(f"Connecting via FFmpeg pipe: {url}")
                latest_stats["status"] = "connecting"
                latest_stats["error_message"] = "Starting FFmpeg..."
                ffmpeg_proc = open_ffmpeg_pipe(url)
                latest_stats["status"] = "connected"
                latest_stats["error_message"] = None

            t_start = time.time()
            # Read frame
            raw = ffmpeg_proc.stdout.read(frame_size)
            
            if not raw or len(raw) < frame_size:
                print(f"FFmpeg stream ended or frame incomplete ({len(raw) if raw else 0}/{frame_size}).")
                latest_stats["error_message"] = "Stream ended or reconnecting"
                if ffmpeg_proc:
                    ffmpeg_proc.terminate()
                    try:
                        ffmpeg_proc.wait(timeout=2)
                    except:
                        ffmpeg_proc.kill()
                ffmpeg_proc = None
                time.sleep(1)
                continue
                
            frame = np.frombuffer(raw, dtype=np.uint8).reshape((FRAME_H, FRAME_W, 3)).copy()
            
            # DIAGNOSTIC OVERLAY
            cv2.putText(frame, "RECV OK", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Detect objects with YOLO
            t_detect = time.time()
            detections = detector.detect_frame(frame)

            # Count people and draw bounding boxes
            person_count = 0
            for detection in detections:
                if detection['class_name'] == 'person':
                    person_count += 1
                    x1, y1, x2, y2 = [int(v) for v in detection['bbox']]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"Person {detection['confidence']:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            t_end = time.time()
            latency = int((t_end - t_start) * 1000)

            # HUD overlay
            cv2.putText(frame, f"People: {person_count}  Lat: {latency}ms", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Update global stats
            latest_stats["person_count"] = person_count
            latest_stats["last_update"] = time.time()
            latest_stats["status"] = "connected"
            latest_stats["latency_ms"] = latency

            # Encode frame to JPEG for MJPEG stream
            ret_enc, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret_enc:
                with frame_lock:
                    latest_frame = buffer.tobytes()
            
            # Throttle loop to ~30 FPS max (0.033s) to save CPU
            elapsed = time.time() - t_start
            if elapsed < 0.033:
                time.sleep(0.033 - elapsed)

        except Exception as e:
            print(f"Error in frame generation: {e}")
            latest_stats["status"] = "error"
            latest_stats["error_message"] = str(e)
            if ffmpeg_proc:
                ffmpeg_proc.kill()
                ffmpeg_proc = None
            time.sleep(5)


@app.on_event("startup")
async def startup_event():
    """Start the background processing thread when the app starts"""
    # Start the video processing thread
    thread = threading.Thread(target=generate_frames, daemon=True)
    thread.start()

async def video_stream(request: Request):
    """Generator function for MJPEG streaming"""
    while True:
        if await request.is_disconnected():
            break
            
        with frame_lock:
            frame_bytes = latest_frame
            
        if frame_bytes is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Adjust streaming frame rate
        await asyncio.sleep(0.1)

@app.get("/video_feed")
async def video_feed(request: Request):
    """Endpoint to stream the processed video"""
    return StreamingResponse(video_stream(request), media_type="multipart/x-mixed-replace; boundary=frame")

# Serve the pre-built React frontend
if DIST_PATH.exists():
    app.mount("/", StaticFiles(directory=str(DIST_PATH), html=True), name="static")
else:
    @app.get("/")
    async def index():
        return {"message": "Development mode: Frontend not found at " + str(DIST_PATH)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
