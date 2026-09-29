import os
import re
import uuid
import requests
import yt_dlp
from typing import Dict, Any, Optional

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,km;q=0.8",
}

def extract_tiktok_url(text: str) -> Optional[str]:
    """Extract clean URL from raw text (handles text copied from TikTok share button)."""
    if not text:
        return None
    url_match = re.search(r'https?://[^\s]+', text.strip())
    if url_match:
        matched = url_match.group(0).strip()
        # Keep query parameters if shortlink (e.g. vt.tiktok.com)
        return matched
    return text.strip()

def resolve_canonical_url(url: str) -> str:
    """Resolve redirect for shortened links (vt.tiktok.com, vm.tiktok.com) to find canonical post URL."""
    if not url:
        return url
    if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
        try:
            res = requests.get(url, headers=DEFAULT_HEADERS, allow_redirects=True, timeout=8)
            if res.url and "tiktok.com" in res.url:
                # Strip excessive tracking query params but keep video ID
                return res.url.split('?')[0]
        except Exception as e:
            print(f"[TikTokDownloader] Redirect resolve error: {e}")
    return url

def fetch_via_ssstik(url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch video metadata and direct no-watermark download link using SSSTik.
    Works for TikTok Drama / Episode / Series videos as well as normal videos.
    """
    try:
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)
        
        # 1. Fetch homepage to get TT validation token
        home_res = session.get("https://ssstik.io/en", timeout=10)
        tt_match = re.search(r'data-tt=["\']([^"\']+)["\']', home_res.text)
        tt_token = tt_match.group(1) if tt_match else ""

        # 2. Query download links
        post_res = session.post(
            "https://ssstik.io/abc?url=dl",
            data={"id": url, "locale": "en", "tt": tt_token},
            headers={"HX-Request": "true"},
            timeout=15
        )
        
        if post_res.status_code == 200:
            html = post_res.text
            # Extract download link
            links = re.findall(r'href="([^"]+)"[^>]*class="[^"]*download[^"]*"', html)
            if not links:
                # Alternative regex for direct tikcdn links
                links = re.findall(r'href="(https?://[^"]*tikcdn\.io[^"]*)"', html)
            
            if links:
                play_url = links[0]
                
                # Title / caption
                title_m = re.search(r'<p class="maintext">([^<]+)</p>', html)
                title = title_m.group(1).strip() if title_m else "TikTok Video"
                
                # Author
                author_m = re.search(r'<h2>([^<]+)</h2>', html)
                author = author_m.group(1).strip() if author_m else "TikTok Creator"
                
                # Cover / avatar image
                cover = ""
                for img_src in re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', html):
                    if "tikcdn.io" in img_src or "tiktokcdn" in img_src:
                        cover = img_src
                        break

                return {
                    "source": "ssstik",
                    "title": title,
                    "author": author,
                    "avatar": cover,
                    "cover": cover,
                    "duration": 0,
                    "playUrl": play_url
                }
    except Exception as e:
        print(f"[TikTokDownloader] SSSTik fetch error: {e}")
    return None

def fetch_via_tikwm(url: str) -> Optional[Dict[str, Any]]:
    """Fetch video metadata and direct no-watermark link using TikWM API."""
    try:
        api_url = "https://www.tikwm.com/api/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        res = requests.post(api_url, data={"url": url, "hd": 1}, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 0 and "data" in data:
                d = data["data"]
                # Prefer HD no-watermark URL if available, else standard play
                play_url = d.get("hdplay") or d.get("play")
                if play_url and play_url.startswith("/"):
                    play_url = f"https://www.tikwm.com{play_url}"
                
                title = d.get("title") or "TikTok Video"
                author_name = d.get("author", {}).get("nickname") or d.get("author", {}).get("unique_id") or "TikTok Creator"
                avatar = d.get("author", {}).get("avatar") or ""
                cover = d.get("cover") or d.get("origin_cover") or ""
                duration = d.get("duration", 0)

                return {
                    "source": "tikwm",
                    "title": title,
                    "author": author_name,
                    "avatar": avatar,
                    "cover": cover,
                    "duration": duration,
                    "playUrl": play_url
                }
    except Exception as e:
        print(f"[TikTokDownloader] TikWM fetch error: {e}")
    return None

def fetch_via_ytdlp(url: str) -> Optional[Dict[str, Any]]:
    """Fallback fetch metadata using yt-dlp."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
            'http_headers': DEFAULT_HEADERS
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                title = info.get("title") or "Video"
                uploader = info.get("uploader") or info.get("creator") or "Creator"
                cover = info.get("thumbnail") or ""
                duration = info.get("duration", 0)
                url_direct = info.get("url")
                
                return {
                    "source": "ytdlp",
                    "title": title,
                    "author": uploader,
                    "avatar": "",
                    "cover": cover,
                    "duration": duration,
                    "playUrl": url_direct
                }
    except Exception as e:
        print(f"[TikTokDownloader] yt-dlp fetch error: {e}")
    return None

def get_video_info(raw_url: str) -> Dict[str, Any]:
    """Retrieve video info from TikTok or other supported video sites."""
    clean_url = extract_tiktok_url(raw_url)
    if not clean_url:
        raise ValueError("Invalid URL provided")

    canonical_url = resolve_canonical_url(clean_url)

    # 1. Try TikWM first (fastest for standard TikTok videos)
    info = fetch_via_tikwm(clean_url)
    if not info and canonical_url != clean_url:
        info = fetch_via_tikwm(canonical_url)

    # 2. Try SSSTik (specialized for TikTok Drama / Episode / Series & standard videos)
    if not info:
        info = fetch_via_ssstik(clean_url)
    if not info and canonical_url != clean_url:
        info = fetch_via_ssstik(canonical_url)

    # 3. Fallback to yt-dlp
    if not info:
        info = fetch_via_ytdlp(canonical_url)
    if not info and canonical_url != clean_url:
        info = fetch_via_ytdlp(clean_url)

    if not info:
        raise RuntimeError("មិនអាចទាញយកព័ត៌មានវីដេអូបានទេ។ សូមពិនិត្យ Link ម្តងទៀត (Failed to extract video info).")

    return info

def download_video_file(raw_url: str, output_dir: str) -> Dict[str, Any]:
    """Download video and save it into output_dir (e.g. uploads/). Returns file info."""
    clean_url = extract_tiktok_url(raw_url)
    if not clean_url:
        raise ValueError("Invalid URL provided")

    os.makedirs(output_dir, exist_ok=True)
    file_id = f"tiktok_{uuid.uuid4().hex[:12]}.mp4"
    dest_path = os.path.join(output_dir, file_id)

    # Get info & direct playUrl
    info = get_video_info(clean_url)
    downloaded = False
    
    if info and info.get("playUrl"):
        source = info.get("source", "tikwm")
        referer = "https://ssstik.io/" if source == "ssstik" else "https://www.tikwm.com/"
        stream_headers = {
            "User-Agent": DEFAULT_HEADERS["User-Agent"],
            "Referer": referer,
            "Accept": "*/*"
        }
        try:
            with requests.get(info["playUrl"], headers=stream_headers, stream=True, timeout=45) as r:
                r.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000:
                downloaded = True
        except Exception as e:
            print(f"[TikTokDownloader] Stream download from {source} failed: {e}")
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except Exception:
                    pass

    # If first stream failed, try alternative fetch method
    if not downloaded:
        alt_info = None
        if info and info.get("source") == "tikwm":
            alt_info = fetch_via_ssstik(clean_url)
        elif info and info.get("source") == "ssstik":
            alt_info = fetch_via_tikwm(clean_url)
            
        if alt_info and alt_info.get("playUrl"):
            try:
                alt_referer = "https://ssstik.io/" if alt_info.get("source") == "ssstik" else "https://www.tikwm.com/"
                headers = {"User-Agent": DEFAULT_HEADERS["User-Agent"], "Referer": alt_referer}
                with requests.get(alt_info["playUrl"], headers=headers, stream=True, timeout=45) as r:
                    r.raise_for_status()
                    with open(dest_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000:
                    downloaded = True
                    info = alt_info
            except Exception as e:
                print(f"[TikTokDownloader] Alt stream download failed: {e}")

    # Fallback to yt-dlp if direct streams didn't succeed
    if not downloaded:
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, f"tiktok_{uuid.uuid4().hex[:12]}.%(ext)s"),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'http_headers': DEFAULT_HEADERS
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            canonical_url = resolve_canonical_url(clean_url)
            extracted = ydl.extract_info(canonical_url or clean_url, download=True)
            actual_filename = ydl.prepare_filename(extracted)
            if not actual_filename.endswith(".mp4"):
                actual_filename = os.path.splitext(actual_filename)[0] + ".mp4"
            
            if os.path.exists(actual_filename):
                file_id = os.path.basename(actual_filename)
                dest_path = actual_filename
                downloaded = True
                if not info:
                    info = {
                        "title": extracted.get("title") or "TikTok Video",
                        "author": extracted.get("uploader") or "Creator",
                        "avatar": "",
                        "cover": extracted.get("thumbnail") or "",
                        "duration": extracted.get("duration", 0)
                    }

    if not downloaded or not os.path.exists(dest_path):
        raise RuntimeError("ការទាញយកវីដេអូបានបរាជ័យ (Video download failed). Please check the link.")

    file_size = os.path.getsize(dest_path)
    title = info.get("title", "tiktok_video") if info else "tiktok_video"
    # Clean title for filename (preserve Khmer and English characters, strip dangerous symbols)
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title)[:50].strip() or "tiktok_video"

    return {
        "success": True,
        "fileId": file_id,
        "filename": f"{clean_title}.mp4",
        "size": file_size,
        "title": title,
        "author": info.get("author") if info else "TikTok Creator",
        "avatar": info.get("avatar") if info else "",
        "cover": info.get("cover") if info else "",
        "duration": info.get("duration", 0) if info else 0,
        "localPath": dest_path
    }
