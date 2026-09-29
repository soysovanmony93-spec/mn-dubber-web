#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Standalone Dubbing Pipeline Engine for Web & Mobile AI Dubber Studio.
"""
import os
import sys
try:
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import json
import time
import uuid
import shutil
import asyncio
import subprocess
import urllib.request
import urllib.parse
from typing import Callable, Optional, Dict, Any, List

from .tts_engine import synthesize_speech

def get_ffmpeg() -> str:
    """Find FFmpeg binary path."""
    # Check current environment or system PATH
    candidates = [
        "ffmpeg",
        os.path.join(os.getcwd(), "..", "bin", "ffmpeg.exe"),
        os.path.join(os.getcwd(), "bin", "ffmpeg.exe"),
        r"C:\ffmpeg\bin\ffmpeg.exe"
    ]
    for c in candidates:
        try:
            res = subprocess.run([c, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                return c
        except Exception:
            continue
    return "ffmpeg"

def get_ffprobe() -> str:
    """Find FFprobe binary path."""
    candidates = [
        "ffprobe",
        os.path.join(os.getcwd(), "..", "bin", "ffprobe.exe"),
        os.path.join(os.getcwd(), "bin", "ffprobe.exe"),
        r"C:\ffmpeg\bin\ffprobe.exe"
    ]
    for c in candidates:
        try:
            res = subprocess.run([c, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                return c
        except Exception:
            continue
    return "ffprobe"

def get_media_duration(file_path: str) -> float:
    """Get media duration in seconds using ffprobe or cv2."""
    try:
        import cv2
        cap = cv2.VideoCapture(file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        if fps > 0 and frames > 0:
            return float(frames / fps)
    except Exception:
        pass
    ffprobe_bin = get_ffprobe()
    cmd = [
        ffprobe_bin, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return float(res.stdout.strip())
    except Exception:
        return 0.0

def get_video_dimensions(file_path: str):
    """Retrieve video width and height."""
    try:
        import cv2
        cap = cv2.VideoCapture(file_path)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        if w > 0 and h > 0:
            return w, h
    except Exception:
        pass
    return 1920, 1080

def get_master_gemini_key() -> Optional[str]:
    """Retrieve local encrypted Gemini API Key from desktop app if available."""
    try:
        import base64
        import win32crypt
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        ls_path = os.path.join(os.environ.get('APPDATA', ''), 'mn-dubber-pro', 'Local State')
        cfg_path = os.path.join(os.environ.get('APPDATA', ''), 'mn-dubber-pro', 'gemini_config.json')
        if os.path.exists(ls_path) and os.path.exists(cfg_path):
            with open(ls_path, 'r', encoding='utf-8') as f:
                ls = json.load(f)
            enc_key = base64.b64decode(ls['os_crypt']['encrypted_key'])
            master_key = win32crypt.CryptUnprotectData(enc_key[5:], None, None, None, 0)[1]
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            raw = base64.b64decode(cfg['geminiApiKeyEncrypted'][4:])
            nonce = raw[3:15]
            ciphertext = raw[15:]
            aesgcm = AESGCM(master_key)
            return aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
    except Exception:
        pass
    return None

def parse_time_str(time_val) -> float:
    """Convert SRT timecode (HH:MM:SS,mmm or MM:SS,mmm or float) into seconds float."""
    if time_val is None:
        return 0.0
    if isinstance(time_val, (int, float)):
        return max(0.0, float(time_val))
    s = str(time_val).strip().replace(',', '.')
    if not s:
        return 0.0
    try:
        return max(0.0, float(s))
    except ValueError:
        pass
    parts = s.split(':')
    if len(parts) == 3:
        try:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        except Exception:
            return 0.0
    elif len(parts) == 2:
        try:
            return float(parts[0]) * 60 + float(parts[1])
        except Exception:
            return 0.0
    return 0.0

def translate_text_to_khmer(text: str, api_key: Optional[str] = None, retries: int = 3) -> str:
    """Translate text to Khmer supporting any AI API Key (Gemini, OpenAI, etc.) with automatic fallback."""
    clean = text.strip()
    if not clean:
        return ""
    
    # Try using provided API Key (Gemini or OpenAI)
    if api_key and api_key.strip():
        k = api_key.strip()
        # 1. Try Google GenAI SDK (Gemini 2.0 / 1.5 Flash)
        try:
            from google import genai
            client = genai.Client(api_key=k)
            prompt = f"Translate the following movie/video subtitle text accurately and naturally into spoken Khmer language. Output ONLY the Khmer translation without explanation:\n\n{clean}"
            resp = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            if resp.text and resp.text.strip():
                return resp.text.strip()
        except Exception:
            pass

        # 2. Try google.generativeai legacy SDK
        try:
            import google.generativeai as gai
            gai.configure(api_key=k)
            model = gai.GenerativeModel('gemini-1.5-flash')
            resp = model.generate_content(f"Translate into natural spoken Khmer language only: {clean}")
            if resp.text and resp.text.strip():
                return resp.text.strip()
        except Exception:
            pass

        # 3. Try OpenAI API if key starts with sk-
        if k.startswith("sk-"):
            try:
                import requests
                headers = {"Authorization": f"Bearer {k}", "Content-Type": "application/json"}
                body = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a professional video dubbing translator. Translate dialogue into natural spoken Khmer. Output only the Khmer translation."},
                        {"role": "user", "content": clean}
                    ],
                    "temperature": 0.3
                }
                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=10)
                if res.status_code == 200:
                    out = res.json()["choices"][0]["message"]["content"].strip()
                    if out:
                        return out
            except Exception:
                pass
    
    # Free Google Translate endpoint (automatic fallback)
    for attempt in range(retries):
        try:
            url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=km&dt=t&q=" + urllib.parse.quote(clean)
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode('utf-8'))
                parts = [p[0] for p in data[0] if p[0]]
                translated = "".join(parts).strip()
                if translated:
                    return translated
        except Exception:
            time.sleep(0.4)
            
    return clean

def format_srt_timestamp(seconds: float) -> str:
    """Format seconds into SubRip SRT timestamp 00:00:00,000."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

# Global cache for Whisper model so it doesn't reload on every single video
_CACHED_WHISPER = None

def get_cached_whisper(model_name: str = "tiny"):
    global _CACHED_WHISPER
    if _CACHED_WHISPER is None:
        import whisper
        _CACHED_WHISPER = whisper.load_model(model_name)
    return _CACHED_WHISPER

class DubbingJob:
    def __init__(
        self,
        task_id: str,
        input_video_path: str,
        output_dir: str,
        voice_id: str = "km-KH-PisethNeural",
        voice_mode: str = "auto",  # 'auto', 'male', 'female', 'custom'
        vocal_cut_mode: str = "smart-duck",  # 'smart-duck', 'karaoke', 'clean-voice', 'normal'
        bg_music_volume: float = 0.15,
        dub_volume: float = 1.0,
        rate: int = 0,
        pitch: int = 0,
        gemini_api_key: Optional[str] = None,
        # Video Overlays
        logo_enabled: bool = False,
        logo_path: Optional[str] = None,
        logo_position: str = "top-right",
        logo_x: Optional[float] = None,
        logo_y: Optional[float] = None,
        logo_size: int = 14,
        logo_opacity: int = 90,
        logo_remove_bg: bool = False,
        logo_chroma_color: str = "#00FF00",
        blur_enabled: bool = False,
        blur_y: int = 83,
        blur_height: int = 13,
        blur_width: int = 95,
        blur_x: Optional[float] = None,
        blur_strength: int = 15,
        blur_darkness: int = 40,
        custom_text_enabled: bool = False,
        custom_text: str = "",
        custom_text_position: str = "top-center",
        custom_text_x: Optional[float] = None,
        custom_text_y: Optional[float] = None,
        custom_text_size: int = 26,
        custom_text_font_size_percent: Optional[float] = None,
        custom_text_color: str = "#ffffff",
        custom_text_bg: bool = True,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.task_id = task_id
        self.input_video_path = input_video_path
        self.output_dir = output_dir
        self.voice_id = voice_id
        self.voice_mode = voice_mode
        self.vocal_cut_mode = vocal_cut_mode
        self.bg_music_volume = bg_music_volume
        self.dub_volume = dub_volume
        self.rate = rate
        self.pitch = pitch
        self.gemini_api_key = gemini_api_key
        
        # Overlays
        self.logo_enabled = logo_enabled
        self.logo_path = logo_path
        self.logo_position = logo_position
        self.logo_x = logo_x
        self.logo_y = logo_y
        self.logo_size = logo_size
        self.logo_opacity = logo_opacity
        self.logo_remove_bg = logo_remove_bg
        self.logo_chroma_color = logo_chroma_color
        
        self.blur_enabled = blur_enabled
        self.blur_y = blur_y
        self.blur_height = blur_height
        self.blur_width = blur_width
        self.blur_x = blur_x
        self.blur_strength = blur_strength
        self.blur_darkness = blur_darkness
        
        self.custom_text_enabled = custom_text_enabled
        self.custom_text = custom_text
        self.custom_text_position = custom_text_position
        self.custom_text_x = custom_text_x
        self.custom_text_y = custom_text_y
        self.custom_text_size = custom_text_size
        self.custom_text_font_size_percent = custom_text_font_size_percent
        self.custom_text_color = custom_text_color
        self.custom_text_bg = custom_text_bg
        
        self.progress_callback = progress_callback
        
        self.work_dir = os.path.join(output_dir, f"work_{task_id}")
        os.makedirs(self.work_dir, exist_ok=True)
        
        self.ffmpeg_bin = get_ffmpeg()
        
    def notify(self, percent: int, step: str, details: str = ""):
        if self.progress_callback:
            self.progress_callback({
                "taskId": self.task_id,
                "percent": percent,
                "step": step,
                "details": details,
                "timestamp": time.time()
            })

    async def execute(self) -> Dict[str, str]:
        """Run full dubbing workflow."""
        try:
            self.notify(5, "កំពុងស្រង់សំឡេងដើម (Extracting Audio)", "Extracting pristine audio stream from video...")
            extracted_speech = os.path.join(self.work_dir, "speech_16k.wav")
            orig_stereo_audio = os.path.join(self.work_dir, "orig_stereo_44k.wav")
            
            # 1. 16kHz mono for speech recognition
            cmd_ext_speech = [
                self.ffmpeg_bin, "-y",
                "-i", self.input_video_path,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                extracted_speech
            ]
            await asyncio.to_thread(subprocess.run, cmd_ext_speech, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            # 2. 44.1kHz stereo for background music / effects
            cmd_ext_stereo = [
                self.ffmpeg_bin, "-y",
                "-i", self.input_video_path,
                "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
                orig_stereo_audio
            ]
            try:
                await asyncio.to_thread(subprocess.run, cmd_ext_stereo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except Exception:
                orig_stereo_audio = extracted_speech
            
            duration = await asyncio.to_thread(get_media_duration, self.input_video_path)
            
            # Step 2: Speech Recognition & Translation (Gemini SRT)
            self.notify(20, "Gemini AI កំពុងបង្កើត SRT និងបកប្រែ (Gemini SRT)", "Using Gemini AI for accurate timestamps and natural Khmer dubbing dialogue...")
            segments = await self._transcribe_and_translate(extracted_speech)
            
            if not segments:
                raise ValueError("មិនមានសំឡេងមនុស្សនិយាយនៅក្នុងវីដេអូនេះទេ (No speech detected in audio track). សូមជ្រើសរើសវីដេអូដែលមានការសន្ទនា ឬសំឡេងនិយាយ។")
            
            self.notify(50, f"បកប្រែរួចរាល់ ({len(segments)} ឃ្លា)", f"Generated {len(segments)} dialogue segments. Generating Khmer voices...")
            
            # Step 3: Generate TTS for each segment
            tts_segments = await self._generate_tts_clips(segments)
            
            # Step 4: Mix Dubbed Audio Track (Smart Vocal Removal & Studio Mixing)
            self.notify(75, "កំពុងកាត់សំឡេងដើម និងលាយសំឡេង (Smart Vocal Cut & Mix)", "Removing original spoken voice and balancing background audio with Khmer speech...")
            mixed_audio = await self._mix_audio_track(orig_stereo_audio, tts_segments, duration)
            
            # Step 5: Merge with Video (Video Overlays: Blur, Logo, Custom Text)
            self.notify(88, "កំពុង Render វីដេអូ HD (Rendering Video)", "Applying blur, logo and custom text overlays...")
            final_video = os.path.join(self.output_dir, f"dubbed_{self.task_id}.mp4")
            final_srt = os.path.join(self.output_dir, f"dubbed_{self.task_id}.srt")
            final_audio = os.path.join(self.output_dir, f"dubbed_{self.task_id}.mp3")
            
            # Write SRT file
            self._write_srt_file(segments, final_srt)
            
            # Export dubbed MP3 audio
            shutil.copyfile(mixed_audio, final_audio)
            
            # Get video dimensions
            video_w, video_h = get_video_dimensions(self.input_video_path)
            
            v_filters = []
            curr_v = "[0:v]"
            input_args = ["-i", self.input_video_path]
            input_idx = 1
            
            # 1. Blur Subtitle Box (To hide original Chinese/English subtitles)
            if self.blur_enabled:
                bx_ratio = max(0.0, min(1.0, float(self.blur_x if self.blur_x is not None else 5.0) / 100.0))
                by_ratio = max(0.0, min(1.0, float(self.blur_y if self.blur_y is not None else 83.0) / 100.0))
                bw_ratio = max(0.02, min(1.0, float(self.blur_width if self.blur_width is not None else 90.0) / 100.0))
                bh_ratio = max(0.01, min(1.0, float(self.blur_height if self.blur_height is not None else 13.0) / 100.0))
                
                crop_w = max(16, (int(video_w * bw_ratio) // 2) * 2)
                crop_h = max(16, (int(video_h * bh_ratio) // 2) * 2)
                crop_x = max(0, min(video_w - crop_w, (int(video_w * bx_ratio) // 2) * 2))
                crop_y = max(0, min(video_h - crop_h, (int(video_h * by_ratio) // 2) * 2))
                
                strength = max(4, min(40, int(self.blur_strength)))
                darkness = max(0.0, min(1.0, float(self.blur_darkness) / 100.0))
                
                v_filters.append(
                    f"{curr_v}split[main_b][crop_b];"
                    f"[crop_b]crop={crop_w}:{crop_h}:{crop_x}:{crop_y},"
                    f"boxblur={strength}:2,"
                    f"drawbox=x=0:y=0:w=iw:h=ih:color=black@{darkness:.2f}:t=fill[blur_box];"
                    f"[main_b][blur_box]overlay={crop_x}:{crop_y}[v_blur]"
                )
                curr_v = "[v_blur]"
            
            # 2. Logo Overlay with Background Removal
            if self.logo_enabled and self.logo_path and os.path.exists(self.logo_path):
                logo_in_idx = input_idx
                input_args.extend(["-i", self.logo_path])
                input_idx += 1
                
                logo_w_ratio = max(0.03, min(0.8, float(self.logo_size or 14) / 100.0))
                logo_alpha = max(0.1, min(1.0, float(self.logo_opacity or 90) / 100.0))
                target_logo_w = max(24, int(round(video_w * logo_w_ratio / 2.0)) * 2)
                
                chroma_filter = ""
                if self.logo_remove_bg:
                    raw_color = str(self.logo_chroma_color or "#00FF00").lstrip("#")
                    key_color = f"0x{raw_color}" if not raw_color.startswith("0x") else raw_color
                    chroma_filter = f",colorkey={key_color}:0.30:0.10"
                
                if self.logo_x is not None and self.logo_y is not None:
                    lx_ratio = max(0.0, min(1.0, float(self.logo_x) / 100.0))
                    ly_ratio = max(0.0, min(1.0, float(self.logo_y) / 100.0))
                    target_lx = max(0, min(video_w - target_logo_w, int(video_w * lx_ratio)))
                    target_ly = max(0, min(video_h - 20, int(video_h * ly_ratio)))
                    pos_expr = f"{target_lx}:{target_ly}"
                else:
                    pos = self.logo_position
                    if pos == "top-left":
                        pos_expr = "25:25"
                    elif pos == "bottom-right":
                        pos_expr = f"{video_w - target_logo_w - 25}:H-h-25"
                    elif pos == "bottom-left":
                        pos_expr = "25:H-h-25"
                    else:
                        pos_expr = f"{video_w - target_logo_w - 25}:25"
                
                v_filters.append(
                    f"[{logo_in_idx}:v]scale={target_logo_w}:-2,format=rgba{chroma_filter},colorchannelmixer=aa={logo_alpha:.2f}[logo_s];"
                    f"{curr_v}[logo_s]overlay={pos_expr}:eof_action=repeat[v_logo]"
                )
                curr_v = "[v_logo]"
            
            # 3. Custom Text Overlay (Title / Banner / Watermark)
            if self.custom_text_enabled and self.custom_text.strip():
                clean_text = self.custom_text.strip().replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")
                font_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "KantumruyPro-Bold.ttf"))
                if not os.path.exists(font_file):
                    font_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "fonts", "KantumruyPro-Bold.ttf"))
                
                # Proportional font size to video height (matches phone/browser preview proportion exactly)
                if getattr(self, "custom_text_font_size_percent", None) and float(self.custom_text_font_size_percent) > 0:
                    font_size = int(video_h * (float(self.custom_text_font_size_percent) / 100.0))
                else:
                    # Healthy HD scaling: default 26 slider corresponds to ~5.5% of video height
                    slider_val = float(self.custom_text_size or 26)
                    ratio = (slider_val / 26.0) * 0.055
                    font_size = int(video_h * ratio)
                
                # Clamp within healthy HD bounds
                font_size = max(28, min(240, font_size))
                
                if self.custom_text_x is not None and self.custom_text_y is not None:
                    tx_ratio = max(0.0, min(1.0, float(self.custom_text_x) / 100.0))
                    ty_ratio = max(0.0, min(1.0, float(self.custom_text_y) / 100.0))
                    target_tx = int(video_w * tx_ratio)
                    target_ty = int(video_h * ty_ratio)
                    pos_expr = f"x={target_tx}:y={target_ty}"
                else:
                    tpos = self.custom_text_position
                    if tpos == "top-left":
                        pos_expr = "x=30:y=25"
                    elif tpos == "top-right":
                        pos_expr = "x=w-text_w-30:y=25"
                    elif tpos == "bottom-center":
                        pos_expr = "x=(w-text_w)/2:y=h-text_h-30"
                    elif tpos == "bottom-left":
                        pos_expr = "x=30:y=h-text_h-30"
                    elif tpos == "bottom-right":
                        pos_expr = "x=w-text_w-30:y=h-text_h-30"
                    else:
                        pos_expr = "x=(w-text_w)/2:y=25"
                
                box_pad = max(10, int(font_size * 0.28))
                box_opt = f":box=1:boxcolor=black@0.70:boxborderw={box_pad}" if self.custom_text_bg else ":shadowcolor=black@0.85:shadowx=3:shadowy=3"
                escaped_font_path = font_file.replace(os.sep, '/').replace(':', r'\:')
                font_opt = f":fontfile='{escaped_font_path}'" if os.path.exists(font_file) else ""
                
                v_filters.append(
                    f"{curr_v}drawtext=text='{clean_text}'{font_opt}:fontcolor={self.custom_text_color}:fontsize={font_size}:{pos_expr}{box_opt}[v_txt]"
                )
                curr_v = "[v_txt]"
            
            # Execute merge with FFmpeg
            cmd_merge = [self.ffmpeg_bin, "-y"]
            cmd_merge.extend(input_args)
            cmd_merge.extend(["-i", mixed_audio])
            
            if v_filters:
                filter_complex_str = ";".join(v_filters)
                cmd_merge.extend([
                    "-filter_complex", filter_complex_str,
                    "-map", curr_v,
                    "-map", f"{input_idx}:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k",
                    "-shortest",
                    final_video
                ])
            else:
                cmd_merge.extend([
                    "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k",
                    "-map", "0:v:0",
                    "-map", f"{input_idx}:a",
                    "-shortest",
                    final_video
                ])
            
            res = await asyncio.to_thread(subprocess.run, cmd_merge, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0 or not os.path.exists(final_video):
                print(f"[FFmpeg Video Render Warning] Error rendering video with filters: {res.stderr}. Retrying fallback copy...")
                cmd_fallback = [
                    self.ffmpeg_bin, "-y",
                    "-i", self.input_video_path,
                    "-i", mixed_audio,
                    "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-shortest",
                    final_video
                ]
                await asyncio.to_thread(subprocess.run, cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            self.notify(100, "ជោគជ័យ ១០០% (Completed!)", "Dubbing completed successfully! Ready to play and download.")
            
            return {
                "video": final_video,
                "audio": final_audio,
                "srt": final_srt,
                "segmentsCount": len(segments),
                "duration": duration
            }
            
        finally:
            # Clean temporary work dir to save space
            try:
                if os.path.exists(self.work_dir):
                    shutil.rmtree(self.work_dir, ignore_errors=True)
            except Exception:
                pass

    async def _transcribe_and_translate(self, audio_wav: str) -> List[Dict[str, Any]]:
        """Transcribe and translate using ONLY Google Gemini API to produce high-precision Khmer SRT cues."""
        loop = asyncio.get_event_loop()
        
        # 1. Prepare compressed MP3 to send to Gemini fast
        gemini_mp3 = os.path.join(self.work_dir, "gemini_input.mp3")
        cmd_mp3 = [
            self.ffmpeg_bin, "-y",
            "-i", audio_wav,
            "-vn", "-ar", "16000", "-ac", "1", "-b:a", "64k",
            gemini_mp3
        ]
        await asyncio.to_thread(subprocess.run, cmd_mp3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not os.path.exists(gemini_mp3) or os.path.getsize(gemini_mp3) < 100:
            gemini_mp3 = audio_wav

        # 2. Get API Key
        effective_key = self.gemini_api_key or get_master_gemini_key()

        def _call_gemini():
            from google import genai
            from google.genai import types

            with open(gemini_mp3, "rb") as f:
                audio_bytes = f.read()

            audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")

            system_prompt = """You are an elite audiovisual subtitle translator and film dubbing director.
CRITICAL MANDATORY INSTRUCTIONS:
1. You must transcribe and translate EVERY SINGLE spoken dialogue, speech, conversation, reaction, and utterance from 00:00.000 to the very end of the audio track without skipping or omitting any line.
2. Ensure continuous, non-overlapping coverage: consecutive dialogues must never overlap.
3. Accurately detect timestamps for start and end times in SRT format (HH:MM:SS,mmm).
4. Translate each line into natural, fluent, cinematic Khmer dialogue suitable for dubbing.
5. Accurately detect speakerGender as 'male' or 'female' for each cue.
6. Absolutely DO NOT include tags or speaker notes like '(male)', '(female)', '(ស្រី)', or '(ប្រុស)' inside the spoken dialogue text.
7. Return a valid JSON object with the exact structure:
{
  "cues": [
    {
      "id": 1,
      "startTime": "00:00:01,200",
      "endTime": "00:00:03,800",
      "originalText": "Original spoken dialogue",
      "khmerText": "ឃ្លានិយាយបកប្រែជាភាសាខ្មែរ",
      "speakerGender": "male"
    }
  ]
}
Return raw JSON only."""

            client = genai.Client(api_key=effective_key)
            candidate_models = [
                "gemini-3.5-flash",
                "gemini-3.6-flash",
                "gemini-3.8-flash",
                "gemini-3-flash-preview",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-flash-latest"
            ]

            last_err = None
            for model_name in candidate_models:
                for attempt in range(2):
                    try:
                        # Try with system_instruction first
                        try:
                            resp = client.models.generate_content(
                                model=model_name,
                                contents=[audio_part, "Transcribe spoken audio and translate to natural Khmer dubbing dialogue."],
                                config=types.GenerateContentConfig(
                                    system_instruction=system_prompt,
                                    temperature=0.2,
                                    response_mime_type="application/json"
                                )
                            )
                        except Exception as sub_e:
                            if "Developer instruction" in str(sub_e) or "system_instruction" in str(sub_e).lower():
                                # Fallback without system_instruction parameter (embed in contents)
                                resp = client.models.generate_content(
                                    model=model_name,
                                    contents=[system_prompt, audio_part, "Transcribe spoken audio and translate to natural Khmer dubbing dialogue."],
                                    config=types.GenerateContentConfig(
                                        temperature=0.2,
                                        response_mime_type="application/json"
                                    )
                                )
                            else:
                                raise sub_e
                        if resp and resp.text:
                            clean_text = resp.text.strip()
                            if clean_text.startswith("```json"):
                                clean_text = clean_text[7:]
                            if clean_text.startswith("```"):
                                clean_text = clean_text[3:]
                            if clean_text.endswith("```"):
                                clean_text = clean_text[:-3]
                            data = json.loads(clean_text)
                            cues = data.get("cues", [])
                            if cues:
                                return cues
                    except Exception as e:
                        last_err = e
                        time.sleep(1.0)
                        continue

            if last_err:
                print(f"[Gemini SRT Error] All candidate models failed: {last_err}")
            return []

        cues = []
        if effective_key:
            cues = await loop.run_in_executor(None, _call_gemini)

        # Automatic fallback to local Whisper AI + translation if Gemini is unavailable or returns no cues
        if not cues:
            print("[Dubbing Engine] Gemini unavailable or busy. Falling back to local Whisper AI...")
            self.notify(30, "កំពុងប្រើ Whisper AI ក្នុងម៉ាស៊ីន (Local Whisper AI)", "Transcribing speech using local Whisper engine...")
            cues = await loop.run_in_executor(None, self._whisper_fallback, audio_wav)

        if not cues:
            raise ValueError("មិនបានរកឃើញសំឡេងមនុស្សនិយាយ ឬ API កំពុងមមាញឹក។ សូមសាកល្បងម្ដងទៀត!")

        # 3. Convert cues to segments and apply anti-overlap guarantee
        segments = []
        for idx, cue in enumerate(cues):
            st = parse_time_str(cue.get("startTime", 0))
            en = parse_time_str(cue.get("endTime", st + 2.0))
            khmer_txt = str(cue.get("khmerText", "")).strip()
            orig_txt = str(cue.get("originalText", "")).strip()
            if not khmer_txt:
                continue

            if en <= st:
                en = st + 1.5

            gender = str(cue.get("speakerGender", "male")).lower()
            if self.voice_mode == "female":
                v = "km-KH-SreymomNeural"
            elif self.voice_mode == "male":
                v = "km-KH-PisethNeural"
            else:
                v = "km-KH-SreymomNeural" if "female" in gender or "ស្រី" in gender else "km-KH-PisethNeural"

            segments.append({
                "id": idx + 1,
                "start": st,
                "end": en,
                "duration": max(0.5, en - st),
                "original_text": orig_txt,
                "khmer_text": khmer_txt,
                "gender": gender,
                "voice": v
            })

        # Anti-Overlap Enforcement: sentences must NEVER talk over each other
        segments.sort(key=lambda s: s["start"])
        for i in range(len(segments) - 1):
            if segments[i]["end"] > segments[i + 1]["start"]:
                segments[i]["end"] = max(segments[i]["start"] + 0.3, segments[i + 1]["start"] - 0.05)
                segments[i]["duration"] = max(0.3, segments[i]["end"] - segments[i]["start"])

        return segments

    def _whisper_fallback(self, audio_wav: str) -> List[Dict[str, Any]]:
        """Fallback transcription using local Whisper AI + translation when Gemini is unavailable."""
        try:
            print("[Dubbing Engine] Running local Whisper speech transcription...")
            model = get_cached_whisper("tiny")
            res = model.transcribe(audio_wav)
            raw_segs = res.get("segments", [])
            cues = []
            for seg in raw_segs:
                txt = seg.get("text", "").strip()
                if not txt:
                    continue
                kh_txt = translate_text_to_khmer(txt, self.gemini_api_key or get_master_gemini_key())
                cues.append({
                    "id": len(cues) + 1,
                    "startTime": format_srt_timestamp(seg.get("start", 0)),
                    "endTime": format_srt_timestamp(seg.get("end", 0)),
                    "originalText": txt,
                    "khmerText": kh_txt,
                    "speakerGender": "male"
                })
            return cues
        except Exception as e:
            print(f"[Whisper Fallback Error] {e}")
            return []

    async def _generate_tts_clips(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate audio clip for each segment and adjust speed if needed (8 workers)."""
        sem = asyncio.Semaphore(8)
        total_tts = len(segments)
        tts_done = 0
        
        async def process_single_seg(seg: Dict[str, Any]):
            nonlocal tts_done
            async with sem:
                seg_id = seg["id"]
                clip_raw = os.path.join(self.work_dir, f"seg_{seg_id}_raw.mp3")
                clip_fit = os.path.join(self.work_dir, f"seg_{seg_id}_fit.wav")
                
                # Synthesize Khmer voice
                await synthesize_speech(
                    text=seg["khmer_text"],
                    voice=seg["voice"],
                    output_path=clip_raw,
                    rate=self.rate,
                    pitch=self.pitch
                )
                
                # Check duration and adjust tempo
                target_dur = seg["duration"]
                clip_dur = await asyncio.to_thread(get_media_duration, clip_raw)
                
                if clip_dur > target_dur and target_dur > 0.3:
                    # Spoken text is longer than target slot -> speed up slightly (max 1.45x)
                    ratio = min(1.45, max(1.0, clip_dur / target_dur))
                    cmd_speed = [
                        self.ffmpeg_bin, "-y",
                        "-i", clip_raw,
                        "-filter:a", f"atempo={ratio:.3f}",
                        "-ar", "44100", "-ac", "2",
                        clip_fit
                    ]
                else:
                    cmd_speed = [
                        self.ffmpeg_bin, "-y",
                        "-i", clip_raw,
                        "-ar", "44100", "-ac", "2",
                        clip_fit
                    ]
                
                await asyncio.to_thread(subprocess.run, cmd_speed, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                seg["audio_clip"] = clip_fit

                tts_done += 1
                pct = 50 + int((tts_done / max(1, total_tts)) * 25)
                self.notify(pct, f"បញ្ចូលសំឡេង AI ({tts_done}/{total_tts} ឃ្លា)", f"Generated Khmer voice {tts_done}/{total_tts}...")
                return seg

        tasks = [process_single_seg(s) for s in segments]
        return await asyncio.gather(*tasks)

    async def _mix_audio_track(self, original_audio: str, segments: List[Dict[str, Any]], total_duration: float) -> str:
        """Combine background audio and dialogue clips into a unified studio track with crystal clear voice,
        completely removing the original spoken voice while preserving background music and sound effects."""
        loop = asyncio.get_event_loop()
        
        def _do_mix():
            import numpy as np
            import scipy.io.wavfile as wavfile
            from scipy import signal

            mixed_output = os.path.join(self.work_dir, "final_mix.wav")
            full_dub_wav = os.path.join(self.work_dir, "full_dubbed_khmer.wav")

            # 1. Assemble Full Khmer Dub Track with exact timestamps
            sr = 44100
            total_samples = int(max(2.0, total_duration + 5.0) * sr)
            dub_track = np.zeros((total_samples, 2), dtype=np.int16)

            # Sort segments by start time
            sorted_segs = sorted(segments, key=lambda s: float(s.get("start", 0.0)))
            
            for seg in sorted_segs:
                clip_path = seg.get("audio_clip")
                if not clip_path or not os.path.exists(clip_path) or os.path.getsize(clip_path) < 100:
                    continue
                try:
                    clip_sr, clip_data = wavfile.read(clip_path)
                    if len(clip_data.shape) == 1:
                        clip_data = np.column_stack((clip_data, clip_data))
                    
                    start_sec = max(0.0, float(seg.get("start", 0.0)))
                    start_sample = int(start_sec * sr)
                    clip_len = len(clip_data)

                    # Dynamically expand buffer if needed
                    needed = start_sample + clip_len
                    if needed > len(dub_track):
                        extra = np.zeros((needed - len(dub_track) + int(5 * sr), 2), dtype=np.int16)
                        dub_track = np.vstack((dub_track, extra))
                        total_samples = len(dub_track)

                    end_sample = min(total_samples, start_sample + clip_len)
                    actual_len = end_sample - start_sample
                    if actual_len > 0 and start_sample < total_samples:
                        dub_track[start_sample:end_sample] = np.clip(
                            dub_track[start_sample:end_sample].astype(np.int32) + clip_data[:actual_len].astype(np.int32),
                            -32768, 32767
                        ).astype(np.int16)
                except Exception as e:
                    print(f"[Audio Placement Warning] Error placing clip {clip_path}: {e}")

            # 2. Master Track Peak Normalization (broadcast loudness standard so speech is never quiet)
            max_peak = np.max(np.abs(dub_track))
            if max_peak > 300:
                norm_factor = min(4.0, 28000.0 / float(max_peak))
                dub_track = (dub_track.astype(np.float32) * norm_factor).astype(np.int16)

            wavfile.write(full_dub_wav, sr, dub_track)

            # 3. Check if pure dubbing requested or no background wanted
            bg_vol = max(0.0, min(1.0, float(self.bg_music_volume)))
            voice_mult = max(1.0, float(self.dub_volume) * 1.35)

            if self.vocal_cut_mode == "clean-voice" or bg_vol <= 0.005 or not os.path.exists(original_audio):
                print("[Audio Mix] Clean Voice / Pure Dub mode active (zero original voice).")
                if voice_mult > 1.35:
                    scaled_dub = np.clip(dub_track.astype(np.float32) * (voice_mult / 1.35), -32768, 32767).astype(np.int16)
                    wavfile.write(mixed_output, sr, scaled_dub)
                    return mixed_output
                return full_dub_wav

            # 4. Process original audio to remove/duck vocals while preserving background sound
            try:
                orig_sr, orig_data = wavfile.read(original_audio)
                if len(orig_data.shape) == 1:
                    orig_data = np.column_stack((orig_data, orig_data))

                # Align length with dub_track
                if len(orig_data) < total_samples:
                    pad = np.zeros((total_samples - len(orig_data), 2), dtype=orig_data.dtype)
                    orig_data = np.vstack((orig_data, pad))
                else:
                    orig_data = orig_data[:total_samples]

                orig_float = orig_data.astype(np.float32)

                # Vocal cancellation filter (Mid-Side subtraction to eliminate centered speech)
                if self.vocal_cut_mode in ["smart-duck", "karaoke"]:
                    diff = (orig_float[:, 0] - orig_float[:, 1]) * 0.5
                    # Preserve bass below 160Hz
                    try:
                        b, a = signal.butter(2, 160.0 / (sr / 2.0), btype='low')
                        center_bass = signal.lfilter(b, a, (orig_float[:, 0] + orig_float[:, 1]) * 0.5)
                        cut_l = diff + center_bass
                        cut_r = -diff + center_bass
                        orig_float = np.column_stack((cut_l, cut_r))
                    except Exception as fe:
                        print(f"[Vocal Filter Warning] Bass filter fallback: {fe}")
                        orig_float = np.column_stack((diff, -diff))

                # Segment-based Smart Ducking: Mute original audio completely during speech segments
                if self.vocal_cut_mode == "smart-duck":
                    bg_gain = np.full(total_samples, bg_vol, dtype=np.float32)
                    fade_len = int(0.04 * sr)  # 40ms smooth crossfade to eliminate clicks/pops

                    for seg in sorted_segs:
                        st_sec = max(0.0, float(seg.get("start", 0.0)))
                        en_sec = max(st_sec + 0.3, float(seg.get("end", 0.0)))
                        st_idx = max(0, int(st_sec * sr))
                        en_idx = min(total_samples, int(en_sec * sr))
                        if en_idx <= st_idx:
                            continue

                        # Fade out before speech starts
                        f_st = max(0, st_idx - fade_len)
                        if f_st < st_idx:
                            bg_gain[f_st:st_idx] = np.linspace(bg_vol, 0.0, st_idx - f_st)

                        # 100% MUTE during speech so original voice is completely eliminated
                        bg_gain[st_idx:en_idx] = 0.0

                        # Fade back in after speech ends
                        f_en = min(total_samples, en_idx + fade_len)
                        if en_idx < f_en:
                            bg_gain[en_idx:f_en] = np.linspace(0.0, bg_vol, f_en - en_idx)

                    bg_track = orig_float * bg_gain[:, None]
                else:
                    # Constant volume for karaoke or normal ducking
                    bg_track = orig_float * bg_vol

                # Mix processed background with Khmer dub voice
                dub_scaled = dub_track.astype(np.float32)
                if voice_mult > 1.35:
                    dub_scaled *= (voice_mult / 1.35)

                final_mix_data = np.clip(dub_scaled + bg_track, -32768, 32767).astype(np.int16)
                wavfile.write(mixed_output, sr, final_mix_data)
                return mixed_output

            except Exception as e:
                print(f"[Smart Audio Mix Fallback] Error in numpy mixing: {e}. Falling back to clean dub track.")
                return full_dub_wav

        return await loop.run_in_executor(None, _do_mix)

    def _write_srt_file(self, segments: List[Dict[str, Any]], srt_path: str):
        """Write SubRip .srt subtitle file."""
        with open(srt_path, "w", encoding="utf-8") as f:
            for idx, seg in enumerate(segments, 1):
                f.write(f"{idx}\n")
                f.write(f"{format_srt_timestamp(seg['start'])} --> {format_srt_timestamp(seg['end'])}\n")
                f.write(f"{seg['khmer_text']}\n\n")
