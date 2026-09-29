#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TTS Engine for Web Dubber: Edge-TTS synthesis and voice previewing.
"""
import os
import asyncio
import tempfile
import edge_tts

AVAILABLE_VOICES = [
    {
        "id": "km-KH-PisethNeural",
        "name": "ពិសិដ្ឋ (Piseth - ប្រុស / Male)",
        "lang": "km-KH",
        "gender": "Male",
        "default": True,
        "sample": "សួស្តី! នេះគឺជាសំឡេងពិសិដ្ឋ បង្កើតដោយបញ្ញាសិប្បនិម្មិត AI Dubber។"
    },
    {
        "id": "km-KH-SreymomNeural",
        "name": "ស្រីមុំ (Sreymom - ស្រី / Female)",
        "lang": "km-KH",
        "gender": "Female",
        "default": False,
        "sample": "សួស្តី! នេះគឺជាសំឡេងស្រីមុំ បង្កើតដោយបញ្ញាសិប្បនិម្មិត AI Dubber។"
    },
    {
        "id": "en-US-GuyNeural",
        "name": "Guy (English - Male)",
        "lang": "en-US",
        "gender": "Male",
        "default": False,
        "sample": "Hello! This is Guy, powered by Microsoft Neural AI Voice."
    },
    {
        "id": "en-US-JennyNeural",
        "name": "Jenny (English - Female)",
        "lang": "en-US",
        "gender": "Female",
        "default": False,
        "sample": "Hello! This is Jenny, speaking natural English speech."
    },
    {
        "id": "th-TH-NiwatNeural",
        "name": "Niwat (Thai - Male)",
        "lang": "th-TH",
        "gender": "Male",
        "default": False,
        "sample": "สวัสดีครับ นี่คือเสียงภาษาไทย"
    },
    {
        "id": "th-TH-PremwadeeNeural",
        "name": "Premwadee (Thai - Female)",
        "lang": "th-TH",
        "gender": "Female",
        "default": False,
        "sample": "สวัสดีค่ะ นี่คือเสียงภาษาไทย"
    },
    {
        "id": "zh-CN-YunxiNeural",
        "name": "Yunxi (Chinese - Male)",
        "lang": "zh-CN",
        "gender": "Male",
        "default": False,
        "sample": "你好！这是中文配音试听。"
    },
    {
        "id": "vi-VN-NamMinhNeural",
        "name": "Nam Minh (Vietnamese - Male)",
        "lang": "vi-VN",
        "gender": "Male",
        "default": False,
        "sample": "Xin chào! Đây là giọng đọc tiếng Việt."
    }
]

def format_rate(rate_val: int) -> str:
    """Format integer percentage (-50 to +50) to Edge-TTS rate string."""
    if rate_val >= 0:
        return f"+{rate_val}%"
    return f"{rate_val}%"

def format_pitch(pitch_val: int) -> str:
    """Format integer Hz to Edge-TTS pitch string."""
    if pitch_val >= 0:
        return f"+{pitch_val}Hz"
    return f"{pitch_val}Hz"

async def synthesize_speech(text: str, voice: str, output_path: str, rate: int = 0, pitch: int = 0, retries: int = 3) -> bool:
    """Generate audio file for a given text and voice."""
    clean_text = text.strip()
    if not clean_text:
        return False
    
    rate_str = format_rate(rate)
    pitch_str = format_pitch(pitch)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    for attempt in range(1, retries + 1):
        try:
            comm = edge_tts.Communicate(text=clean_text, voice=voice, rate=rate_str, pitch=pitch_str)
            await comm.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                return True
        except Exception as e:
            if attempt == retries:
                print(f"[TTS Error] Final attempt failed for text: {clean_text[:30]}... Err: {e}")
            await asyncio.sleep(0.3 * attempt)
            
    return os.path.exists(output_path) and os.path.getsize(output_path) > 100

async def generate_voice_preview(text: str, voice: str, rate: int = 0, pitch: int = 0) -> str:
    """Generate temporary audio file for preview and return path."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        out_path = tf.name
    
    success = await synthesize_speech(text, voice, out_path, rate=rate, pitch=pitch)
    if not success:
        if os.path.exists(out_path):
            os.remove(out_path)
        raise RuntimeError("Failed to generate voice preview via Edge-TTS.")
    return out_path
