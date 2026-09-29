---
title: MN DUBBER PRO
emoji: 🎬
colorFrom: indigo
colorTo: cyan
sdk: docker
app_port: 7860
pinned: false
---

# 🚀 MN DUBBER WEB PRO (iOS & Android & Desktop)

> កម្មវិធីបកប្រែ និងបញ្ចូលសំឡេងវីដេអូជាភាសាខ្មែរដោយស្វ័យប្រវត្តិតាមរយៈ AI - ជំនាន់ Web Application ប្រើប្រាស់បានទាំងលើ **iOS (iPhone/iPad)**, **Android** និងកុំព្យូទ័រគ្រប់ប្រភេទ។

---

## 🌟 លក្ខណៈពិសេសចម្បង (Key Features)

1. **ដំណើរការលើគ្រប់ Device**:
   - ប្រើប្រាស់លើទូរស័ព្ទ **iPhone / iPad** (Safari)
   - ប្រើប្រាស់លើទូរស័ព្ទ **Android** (Chrome)
   - ប្រើប្រាស់លើ **Computer** (Windows, Mac, Linux)
2. **PWA (Progressive Web App)**:
   - អាចចុច **"Add to Home Screen"** លើ iPhone និង Android ដើម្បីដំឡើងជា App ពេញអេក្រង់ (Full-screen Mobile App) ដោយមិនបាច់ចូល App Store ឬ Play Store។
3. **AI Dubbing Pipeline**:
   - ស្រង់សំឡេងវីដេអូដោយស្វ័យប្រវត្តិ (FFmpeg HD)
   - ស្តាប់ និងបកប្រែជាភាសាខ្មែរតាមរយៈ AI (Whisper / Gemini AI)
   - បង្កើតសំឡេងខ្មែរធម្មជាតិ (Edge-TTS: ពិសិដ្ឋ / ស្រីមុំ)
   - Time-Stretching & Studio Audio Mixing (សម្រួលល្បឿននិយាយ និងលាយភ្លេង Background)
   - ទាញយកវីដេអូកម្រិតច្បាស់ (MP4 HD), សំឡេង (MP3) និងអក្សររត់ (SRT Subtitles)
4. **Voice Studio**:
   - អាចសាកល្បងសរសេរអត្ថបទ និងស្តាប់សំឡេង AI ផ្ទាល់ភ្លាមៗ (Instant Voice Audition)
   - កែសម្រួល Speed (-30% ទៅ +40%) និង Pitch (-30Hz ទៅ +30Hz)

---

## 📱 របៀបបើកប្រើនៅលើទូរស័ព្ទដៃ (iOS & Android)

### ជំហានទី ១: បើកដំណើរការ Server លើកុំព្យូទ័រ
ចុចពីរដង (Double click) លើឯកសារ **`start_web.bat`** នៅក្នុង folder នេះ (ឬវាយពាក្យ `python server.py` ក្នុង terminal)។

នៅពេលបើក Server វានឹងបង្ហាញអាសយដ្ឋាន IP ដូចជា៖
```text
============================================================
🚀 MN DUBBER WEB PRO - Server Running!
👉 Local Access:   http://localhost:8000
📱 Mobile Access:  http://192.168.1.XX:8000
   (Open this link on your iPhone or Android on the same Wi-Fi!)
============================================================
```

### ជំហានទី ២: បើកលើទូរស័ព្ទដៃ
1. ត្រូវប្រាកដថាទូរស័ព្ទរបស់អ្នកភ្ជាប់ **Wi-Fi តែមួយ** ជាមួយកុំព្យូទ័រ។
2. បើក Browser (Safari លើ iPhone ឬ Chrome លើ Android)។
3. វាយអាសយដ្ឋាន `http://192.168.1.XX:8000` (លេខ IP ដែល Server បង្ហាញ)។
4. **ដើម្បីដាក់ជា App លើទូរស័ព្ទ**:
   - **iPhone (Safari)**: ចុចប៊ូតុង **Share** (សញ្ញាព្រួញឡើងលើ) ➡️ ជ្រើសរើស **"Add to Home Screen"**
   - **Android (Chrome)**: ចុចសញ្ញាចុច ៣ នៅជ្រុងខាងស្តាំ ➡️ ជ្រើសរើស **"Install App"** ឬ **"Add to Home Screen"**

---

## ☁️ របៀបដាក់លើ Cloud Server (Deploy Online)

ប្រសិនបើអ្នកចង់ឱ្យអ្នកដទៃអាចចូលប្រើពីគ្រប់ទីកន្លែងតាមអ៊ីនធឺណិត (មិនបាច់នៅ Wi-Fi តែមួយ)៖

### វិធីទី ១: ប្រើ Cloudflare Tunnel ឬ Ngrok (ឥតគិតថ្លៃ ងាយស្រួលបំផុត)
1. ទាញយក [ngrok](https://ngrok.com/) ឬ `cloudflared`
2. វាយបញ្ជា៖
   ```bash
   ngrok http 8000
   ```
3. អ្នកនឹងទទួលបាន Public Link HTTPS ដូចជា `https://xxxx.ngrok-free.app` ដែលអាចបើកបានពីគ្រប់ទូរស័ព្ទលើពិភពលោក!

### វិធីទី ២: ដាក់លើ Cloud VPS (Docker / Ubuntu)
1. ជួល Cloud VPS (DigitalOcean, Linode, Hetzner, AWS) ដែលមាន Ubuntu
2. ដំណើរការជាមួយ Docker៖
   ```bash
   docker build -t mn-dubber-web .
   docker run -d -p 8000:8000 mn-dubber-web
   ```
3. កំណត់ Nginx Reverse Proxy និង Domain Name ជាមួយ SSL Certificate (Let's Encrypt HTTPS)។

---

## 🛠️ រចនាសម្ព័ន្ធឯកសារ (Project Structure)

```
ai-dubber-web/
├── server.py              # FastAPI Web Backend (REST API + WebSocket + Static Files)
├── services/
│   ├── __init__.py
│   ├── dubbing_engine.py  # Standalone Pipeline: Extraction, Translation, TTS, Mixing, Muxing
│   └── tts_engine.py      # Edge-TTS Khmer voices & Voice preview generator
├── public/
│   ├── index.html         # High-End Mobile-First Glassmorphic Interface
│   ├── styles.css         # Modern Neon Dark CSS (Responsive for iOS & Android)
│   ├── app.js             # Client state, XHR uploads, WebSocket live progress
│   ├── manifest.json      # PWA App Manifest
│   └── sw.js              # PWA Service Worker for caching & fast loading
├── uploads/               # Temporary uploaded videos
├── outputs/               # Rendered dubbed videos, audios & srt files
├── Dockerfile             # Docker container file for cloud deployment
├── requirements.txt       # Dependencies
└── start_web.bat          # 1-Click launcher for Windows
```
