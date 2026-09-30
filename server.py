#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MN DUBBER WEB PRO - High-Performance Web & Mobile AI Dubbing Server.
Supports iOS (iPhone/iPad), Android, and Desktop browsers.
"""
import os
import sys
import uuid
import socket
import asyncio
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import requests
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.tts_engine import AVAILABLE_VOICES, generate_voice_preview
from services.dubbing_engine import DubbingJob
from services.tiktok_downloader import get_video_info, download_video_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

app = FastAPI(
    title="MN Dubber Web Pro",
    description="Next-Gen AI Video Dubbing Studio for iOS, Android & Web",
    version="1.0.0"
)

# Enable CORS for cross-device mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active tasks & connected WebSocket clients
TASKS: Dict[str, Dict[str, Any]] = {}
WS_CLIENTS: Dict[str, list] = {}
JOB_LOCK = asyncio.Lock()

async def auto_clean_temp_files():
    """Background task to clean up old temp and render files older than 3 hours for 24/7 rendering stability."""
    while True:
        try:
            await asyncio.sleep(1800)  # Every 30 minutes
            now = time.time()
            cutoff = now - (3 * 3600)
            for folder in [UPLOADS_DIR, OUTPUTS_DIR]:
                if not os.path.exists(folder):
                    continue
                for fname in os.listdir(folder):
                    fpath = os.path.join(folder, fname)
                    if os.path.isfile(fpath) and os.path.getmtime(fpath) < cutoff:
                        try:
                            os.remove(fpath)
                        except Exception:
                            pass
        except Exception:
            await asyncio.sleep(60)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(auto_clean_temp_files())

class VoicePreviewRequest(BaseModel):
    text: str
    voice: str
    rate: int = 0
    pitch: int = 0

class TikTokInfoRequest(BaseModel):
    url: str

class TikTokDownloadRequest(BaseModel):
    url: str

class DubRequest(BaseModel):
    fileId: str
    voiceId: str = "km-KH-PisethNeural"
    voiceMode: str = "auto"
    vocalCutMode: str = "smart-duck"  # 'smart-duck', 'karaoke', 'clean-voice', 'normal'
    bgMusicVolume: float = 0.15
    dubVolume: float = 1.0
    rate: int = 0
    pitch: int = 0
    geminiApiKey: Optional[str] = None
    # 1. Logo
    logoEnabled: bool = False
    logoFileId: Optional[str] = None
    logoPosition: str = "top-right"
    logoX: Optional[float] = None
    logoY: Optional[float] = None
    logoSize: int = 14
    logoOpacity: int = 90
    logoRemoveBg: bool = False
    logoChromaColor: str = "#00FF00"
    # 2. Blur Subtitle
    blurEnabled: bool = False
    blurY: float = 83.0
    blurHeight: float = 13.0
    blurWidth: float = 90.0
    blurX: Optional[float] = None
    blurStrength: int = 15
    blurDarkness: int = 40
    # 3. Custom Text (Title / Watermark / Social)
    customTextEnabled: bool = False
    customText: str = ""
    customTextPosition: str = "top-center"
    customTextX: Optional[float] = None
    customTextY: Optional[float] = None
    customTextSize: float = 26.0
    customTextFontSizePercent: Optional[float] = None
    customTextColor: str = "#ffffff"
    customTextBg: bool = True

GLOBAL_ONLINE_URL: Optional[str] = None

def start_cloudflare_tunnel(port: int = 8000):
    global GLOBAL_ONLINE_URL
    import subprocess
    import re
    import time
    
    candidates = [
        os.path.join(BASE_DIR, "..", "bin", "cloudflared.exe"),
        os.path.join(BASE_DIR, "bin", "cloudflared.exe"),
        "cloudflared.exe",
        "cloudflared"
    ]
    cf_bin = None
    for c in candidates:
        if os.path.exists(c):
            cf_bin = os.path.abspath(c)
            break
            
    if not cf_bin:
        print("[Cloudflare Tunnel] cloudflared.exe not found. Free online tunnel disabled.")
        return

    try:
        p = subprocess.Popen(
            [cf_bin, "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        start_t = time.time()
        while time.time() - start_t < 30:
            line = p.stderr.readline()
            if not line:
                continue
            m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if m:
                GLOBAL_ONLINE_URL = m.group(0)
                print("\n" + "="*70)
                print(">> 🌐 MN DUBBER PRO - ONLINE PUBLIC LINK (ឥតគិតថ្លៃ ១០០%)")
                print(">> 📱 ផ្ញើ Link នេះឱ្យអ្នកប្រើទូរស័ព្ទដៃ (iOS & Android):")
                print(f">>    {GLOBAL_ONLINE_URL}")
                print(">> (ដំណើរការពីគ្រប់ទីកន្លែងលើពិភពលោក មិនបាច់មានកុំព្យូទ័រឡើយ)")
                print("="*70 + "\n")
                break
    except Exception as e:
        print(f"[Cloudflare Tunnel Error] {e}")

def get_local_ip() -> str:
    """Retrieve LAN IP so mobile phones can connect."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

@app.get("/api/info")
def get_server_info():
    return {
        "appName": "MN Dubber Web Pro",
        "version": "1.0.0",
        "localIp": get_local_ip(),
        "publicUrl": GLOBAL_ONLINE_URL,
        "port": 8000
    }

@app.get("/api/voices")
def get_voices():
    return {"voices": AVAILABLE_VOICES}

@app.post("/api/preview-voice")
async def preview_voice(req: VoicePreviewRequest):
    try:
        temp_audio = await generate_voice_preview(
            text=req.text,
            voice=req.voice,
            rate=req.rate,
            pitch=req.pitch
        )
        return FileResponse(
            temp_audio,
            media_type="audio/mpeg",
            filename="voice_preview.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1].lower()
        if not ext:
            ext = ".mp4"
            
        saved_filename = f"{file_id}{ext}"
        saved_path = os.path.join(UPLOADS_DIR, saved_filename)
        
        # Save file in chunks to handle large video uploads smoothly
        with open(saved_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024 * 4):  # 4MB chunks
                buffer.write(chunk)
                
        file_size = os.path.getsize(saved_path)
        
        return {
            "success": True,
            "fileId": saved_filename,
            "originalName": file.filename,
            "size": file_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def broadcast_progress(task_id: str, data: Dict[str, Any]):
    """Send progress to all connected WebSockets for this task."""
    if task_id in TASKS:
        TASKS[task_id].update({
            "percent": data.get("percent", 0),
            "step": data.get("step", ""),
            "details": data.get("details", "")
        })
    
    clients = WS_CLIENTS.get(task_id, [])
    for ws in clients:
        try:
            await ws.send_json(data)
        except Exception:
            pass

async def run_dub_job_task(task_id: str, req: DubRequest):
    input_path = os.path.join(UPLOADS_DIR, req.fileId)
    if not os.path.exists(input_path):
        TASKS[task_id]["status"] = "failed"
        TASKS[task_id]["error"] = "Input file not found."
        await broadcast_progress(task_id, {"status": "failed", "error": "Input file not found."})
        return

    if JOB_LOCK.locked():
        await broadcast_progress(task_id, {
            "taskId": task_id,
            "percent": 2,
            "step": "កំពុងរង់ចាំក្នុងជួរ Render (Queued)",
            "details": "កំពុងរង់ចាំ Render វីដេអូមុនចប់។ វីដេអូរបស់អ្នកនឹងចាប់ផ្ដើមបន្ទាប់ដោយស្វ័យប្រវត្តិ...",
            "timestamp": time.time()
        })

    async with JOB_LOCK:
        def on_progress(p_data: Dict[str, Any]):
            asyncio.create_task(broadcast_progress(task_id, p_data))

        logo_path = os.path.join(UPLOADS_DIR, req.logoFileId) if (req.logoEnabled and req.logoFileId) else None
        if logo_path and not os.path.exists(logo_path):
            logo_path = None

        job = DubbingJob(
            task_id=task_id,
            input_video_path=input_path,
            output_dir=OUTPUTS_DIR,
            voice_id=req.voiceId,
            voice_mode=req.voiceMode,
            vocal_cut_mode=req.vocalCutMode,
            bg_music_volume=req.bgMusicVolume,
            dub_volume=req.dubVolume,
            rate=req.rate,
            pitch=req.pitch,
            gemini_api_key=req.geminiApiKey,
            # Video overlays
            logo_enabled=req.logoEnabled and bool(logo_path),
            logo_path=logo_path,
            logo_position=req.logoPosition,
            logo_x=req.logoX,
            logo_y=req.logoY,
            logo_size=req.logoSize,
            logo_opacity=req.logoOpacity,
            logo_remove_bg=req.logoRemoveBg,
            logo_chroma_color=req.logoChromaColor,
            blur_enabled=req.blurEnabled,
            blur_y=req.blurY,
            blur_height=req.blurHeight,
            blur_width=req.blurWidth,
            blur_x=req.blurX,
            blur_strength=req.blurStrength,
            blur_darkness=req.blurDarkness,
            custom_text_enabled=req.customTextEnabled and bool(req.customText.strip()),
            custom_text=req.customText.strip(),
            custom_text_position=req.customTextPosition,
            custom_text_x=req.customTextX,
            custom_text_y=req.customTextY,
            custom_text_size=req.customTextSize,
            custom_text_font_size_percent=req.customTextFontSizePercent,
            custom_text_color=req.customTextColor,
            custom_text_bg=req.customTextBg,
            progress_callback=on_progress
        )

        try:
            result = await job.execute()
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["percent"] = 100
            TASKS[task_id]["result"] = {
                "videoUrl": f"/api/download/{task_id}/video",
                "audioUrl": f"/api/download/{task_id}/audio",
                "srtUrl": f"/api/download/{task_id}/srt",
                "segmentsCount": result.get("segmentsCount", 0),
                "duration": result.get("duration", 0)
            }
            await broadcast_progress(task_id, {
                "status": "completed",
                "percent": 100,
                "step": "ជោគជ័យ ១០០% (Completed!)",
                "result": TASKS[task_id]["result"]
            })
        except Exception as e:
            TASKS[task_id]["status"] = "failed"
            TASKS[task_id]["error"] = str(e)
            await broadcast_progress(task_id, {
                "status": "failed",
                "percent": 0,
                "error": str(e)
            })

@app.post("/api/dub")
async def start_dubbing(req: DubRequest):
    task_id = str(uuid.uuid4())[:8]
    TASKS[task_id] = {
        "taskId": task_id,
        "status": "processing",
        "percent": 0,
        "step": "កំពុងចាប់ផ្តើម (Starting...)",
        "details": "Initializing task pipeline...",
        "result": None,
        "error": None
    }
    
    # Launch background processing task
    asyncio.create_task(run_dub_job_task(task_id, req))
    
    return {"success": True, "taskId": task_id}

@app.get("/api/task/{task_id}")
def get_task_status(task_id: str):
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/api/download/{task_id}/video")
def download_video(task_id: str):
    path = os.path.join(OUTPUTS_DIR, f"dubbed_{task_id}.mp4")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(path, media_type="video/mp4", filename=f"dubbed_{task_id}.mp4")

@app.get("/api/download/{task_id}/audio")
def download_audio(task_id: str):
    path = os.path.join(OUTPUTS_DIR, f"dubbed_{task_id}.mp3")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path, media_type="audio/mpeg", filename=f"dubbed_{task_id}.mp3")

@app.get("/api/download/{task_id}/srt")
def download_srt(task_id: str):
    path = os.path.join(OUTPUTS_DIR, f"dubbed_{task_id}.srt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Subtitle file not found")
    return FileResponse(path, media_type="application/x-subrip", filename=f"dubbed_{task_id}.srt")

@app.websocket("/ws/{task_id}")
async def websocket_progress(websocket: WebSocket, task_id: str):
    await websocket.accept()
    if task_id not in WS_CLIENTS:
        WS_CLIENTS[task_id] = []
    WS_CLIENTS[task_id].append(websocket)
    
    # Send current state immediately
    if task_id in TASKS:
        await websocket.send_json(TASKS[task_id])
        
    try:
        while True:
            # Keep socket alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        if task_id in WS_CLIENTS and websocket in WS_CLIENTS[task_id]:
            WS_CLIENTS[task_id].remove(websocket)

@app.post("/api/tiktok/info")
async def get_tiktok_video_info(req: TikTokInfoRequest):
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, get_video_info, req.url)
        return {"success": True, "info": info}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/tiktok/download")
async def download_tiktok_video_endpoint(req: TikTokDownloadRequest):
    try:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, download_video_file, req.url, UPLOADS_DIR)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tiktok/download-file/{file_id}")
def download_tiktok_file(file_id: str, name: Optional[str] = "tiktok_video"):
    safe_name = os.path.basename(file_id)
    path = os.path.join(UPLOADS_DIR, safe_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video file not found")
    dl_filename = name if name and name.endswith(".mp4") else f"{name}.mp4"
    return FileResponse(path, media_type="video/mp4", filename=dl_filename)

@app.get("/api/tiktok/stream")
def stream_tiktok_video(url: str):
    """Proxy stream video for smooth in-browser preview without CORS or hotlink issues."""
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://ssstik.io/" if "tikcdn.io" in url else "https://www.tikwm.com/"
    }
    try:
        req = requests.get(url, headers=headers, stream=True, timeout=25)
        if req.status_code != 200:
            raise HTTPException(status_code=req.status_code, detail="Failed to fetch video stream")
            
        def iterfile():
            for chunk in req.iter_content(chunk_size=1024 * 512):
                if chunk:
                    yield chunk

        return StreamingResponse(iterfile(), media_type="video/mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount uploads directory so frontend can directly play / stream uploaded & TikTok videos
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Mount frontend public static files
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")

try:
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import threading

def run_port_80():
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=80, log_level="warning")
    except Exception as e:
        pass

def open_browser(url: str):
    import time
    time.sleep(1.2)
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    is_hf_space = bool(os.environ.get("SPACE_ID") or os.environ.get("SPACE_AUTHOR_NAME"))
    default_port = 7860 if is_hf_space else 8000
    port = int(os.environ.get("PORT", default_port))

    # Only attempt port 80 listener on local Windows environments
    if not is_hf_space and sys.platform == "win32":
        t = threading.Thread(target=run_port_80, daemon=True)
        t.start()

    local_ip = get_local_ip()
    print("\n" + "="*60)
    print(">> MN DUBBER WEB PRO - Server Running!")
    print(f"-> Local Access:         http://localhost:{port}")
    if not is_hf_space:
        print(f"-> Mobile Link 1 (Easy): http://{local_ip}")
        print(f"-> Mobile Link 2:        http://{local_ip}:{port}")
    print("="*60 + "\n")
    
    # Auto-open web interface in default browser on local PC
    if not is_hf_space and sys.platform == "win32":
        threading.Thread(target=open_browser, args=(f"http://localhost:{port}",), daemon=True).start()
    
    # If --online or --tunnel requested, launch Cloudflare tunnel for free mobile access
    if "--online" in sys.argv or "--tunnel" in sys.argv or os.environ.get("MN_ONLINE_TUNNEL") == "1":
        threading.Thread(target=start_cloudflare_tunnel, args=(port,), daemon=True).start()

    uvicorn.run(app, host="0.0.0.0", port=port)
