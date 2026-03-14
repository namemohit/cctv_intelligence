from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import threading
import time
import json
import asyncio
import os
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict
from pydantic import BaseModel

# Import the existing YOLO detector
from yolo_dvr_detector import YOLODVRDetector, DetectionLogger

app = FastAPI(title="DVR YOLO Integration API")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Global variables to hold the current video source and stats
current_video_source = "rtsp://admin:Puran234@192.168.1.34:554/Streaming/Channels/102"
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
    detector = YOLODVRDetector("yolov8n.pt", conf_threshold=0.5)
    print("Detector initialized.")

    ffmpeg_proc = None
    frame_width = 0
    frame_height = 0
    last_source = None

    def test_tcp_connection(ip, port, timeout=3):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, int(port)))
            sock.close()
            return result == 0
        except Exception:
            return False


    # Fixed output dimensions — FFmpeg scales any codec/resolution to this
    FRAME_W, FRAME_H = 1280, 720

    def open_ffmpeg_pipe(url, width=FRAME_W, height=FRAME_H):
        """Open an FFmpeg subprocess that outputs raw BGR24 frames at fixed WxH.
        Uses ultra-compatible flags for non-standard DVR streams."""
        cmd = [
            "ffmpeg",
            "-loglevel", "error",
            # RTSP transport and timeout (5s in microseconds)
            "-rtsp_transport", "tcp",
            "-timeout", "5000000",
            # Give it more time to find headers
            "-analyzeduration", "20000000",
            "-probesize", "20000000",
            "-fflags", "+genpts+igndts",
            "-i", url,
            "-vf", f"scale={width}:{height}",
            "-pix_fmt", "bgr24",
            "-vcodec", "rawvideo",
            "-an",
            "-sn",
            "-f", "rawvideo",
            "pipe:1"
        ]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                bufsize=width * height * 3 * 10)

    import numpy as np
    while True:
        try:
            # If no source provided yet, wait
            if current_video_source is None:
                if latest_stats["status"] != "waiting_for_source":
                    print("Background thread: waiting for source...")
                latest_stats["status"] = "waiting_for_source"
                time.sleep(1)
                continue
            
            print(f"Background thread source check: {current_video_source}")

            # If source changed, kill existing ffmpeg process
            if current_video_source != last_source:
                if ffmpeg_proc:
                    ffmpeg_proc.kill()
                    ffmpeg_proc = None
                last_source = current_video_source

            # Open FFmpeg pipe if needed
            if ffmpeg_proc is None or ffmpeg_proc.poll() is not None:
                url = current_video_source
                print(f"Connecting to source via FFmpeg: {url}")
                latest_stats["status"] = "connecting"
                latest_stats["error_message"] = "Initializing connection..."

                # Test TCP port first if RTSP
                if url.startswith("rtsp://"):
                    try:
                        import urllib.parse
                        parsed = urllib.parse.urlparse(url)
                        ip_addr = parsed.hostname
                        port_num = parsed.port if parsed.port else 554
                        latest_stats["error_message"] = f"Testing TCP to {ip_addr}:{port_num}..."
                        if not test_tcp_connection(ip_addr, port_num):
                            latest_stats["status"] = "error"
                            latest_stats["error_message"] = f"Network Error: Cannot reach {ip_addr}:{port_num}"
                            time.sleep(5)
                            continue
                    except Exception:
                        pass

                latest_stats["error_message"] = "Starting FFmpeg decoder..."
                frame_width, frame_height = FRAME_W, FRAME_H
                ffmpeg_proc = open_ffmpeg_pipe(url)
                latest_stats["status"] = "connected"
                latest_stats["error_message"] = None

            # Read one raw BGR frame from FFmpeg stdout
            frame_size = FRAME_W * FRAME_H * 3
            t_start = time.time()
            raw = ffmpeg_proc.stdout.read(frame_size)

            if len(raw) < frame_size:
                err_out = ffmpeg_proc.stderr.read().decode('utf-8', errors='ignore')
                print(f"FFmpeg pipe ended or frame incomplete. Log:\n{err_out}")
                latest_stats["error_message"] = f"FFmpeg error: {err_out[:100]}"
                ffmpeg_proc.kill()
                ffmpeg_proc = None
                time.sleep(1)
                continue

            # import numpy as np  # moved up
            frame = np.frombuffer(raw, dtype=np.uint8).reshape((frame_height, frame_width, 3))
            
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

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
