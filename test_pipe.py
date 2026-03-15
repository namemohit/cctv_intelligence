import subprocess
import numpy as np
import time

ffmpeg_path = r"C:\Users\namem\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
url = "rtsp://admin:Puran234@192.168.1.34:554/Streaming/Channels/101"
# Small resolution for testing
W, H = 640, 480
frame_size = W * H * 3

cmd = [
    ffmpeg_path,
    "-hide_banner",
    "-rtsp_transport", "tcp",
    "-i", url,
    "-vf", f"scale={W}:{H}",
    "-pix_fmt", "bgr24",
    "-vcodec", "rawvideo",
    "-f", "rawvideo",
    "pipe:1"
]

print("Starting FFmpeg...")
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

try:
    for i in range(5):
        print(f"Reading frame {i}...")
        raw = proc.stdout.read(frame_size)
        if len(raw) < frame_size:
            print(f"Frame {i} too small: {len(raw)} bytes")
            break
        print(f"Frame {i} read OK")
        time.sleep(0.1)
finally:
    proc.kill()
    stderr_out = proc.stderr.read().decode('utf-8', errors='ignore')
    print("FFmpeg stderr:")
    print(stderr_out)
