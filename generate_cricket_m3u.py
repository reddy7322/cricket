import requests
import json
import sys
import os
import urllib3
from datetime import datetime, timedelta, timezone

# Disable SSL warnings for cleaner logs and better stream accessibility
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
JSON_URLS = [
    "https://pasteking.u0k.workers.dev/xzdzw.json",
    "https://sports.vodep39240327.workers.dev/sports.json"
]
OUTPUT_M3U = "cricket.m3u"

# Professional User-Agent used by TiviMate/ExoPlayer
DEFAULT_UA = "plaYtv/7.1.3 (Linux;Android 13) ygx/824.1 ExoPlayerLib/824.0"

# --- TELEGRAM CREDENTIALS ---
BOT_TOKEN = "8267675444:AAEchiYEjLOeSzxE47jKdbgj_qKJfOq7k2I"
CHAT_ID = "959113182"

def ist_timestamp():
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return now.strftime("%d %b %Y | %I:%M:%S %p")

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def is_working_pro(url):
    """
    Acts like a professional IPTV player.
    Checks if manifest/stream chunks are accessible with TV-grade headers.
    """
    headers = {
        "User-Agent": DEFAULT_UA,
        "Connection": "keep-alive",
        "Accept": "*/*",
        "Origin": "https://jiotv.com/",
        "Referer": "https://jiotv.com/"
    }
    try:
        # GET request with stream=True simulates a player opening the pipe
        with requests.get(url, headers=headers, timeout=10, stream=True, verify=False) as r:
            # 200/403/405 are considered 'Live' because DRM headers take over during playback
            return r.status_code in [200, 403, 405]
    except:
        return False

def main():
    print(f">>> Generator started. Bot: {BOT_TOKEN[:10]}... Chat: {CHAT_ID}")
    all_streams = []
    seen_urls = set()

    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_UA})

    for url in JSON_URLS:
        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()
            m_type = data.get("event", {}).get("match_type", "LIVE")
            streams = data.get("streams", [])
            for s in streams:
                s['m_label'] = m_type
                all_streams.append(s)
            print(f"✅ Loaded {len(streams)} potential streams from source.")
        except:
            print(f"⚠️ Source timeout/error: {url[:30]}...")

    working_count = 0
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# Updated: " + ist_timestamp() + "\n\n")

        for s in all_streams:
            url_raw = s.get("url", "").strip()
            if not url_raw:
                continue
            
            parts = url_raw.split('|')
            base_url = parts[0]

            # Duplicate prevention
            if base_url in seen_urls:
                continue
            
            # Validation using Pro Player logic
            if not is_working_pro(base_url):
                print(f"❌ Skipping Offline/Protected Stream: {s.get('language')}")
                continue

            seen_urls.add(base_url)
            lang = s.get("language", "Unknown").replace("✨", "").strip()
            name = f"{s['m_label']} - {lang}"
            
            f.write(f'#EXTINF:-1 tvg-logo="https://tvtelugu.pages.dev/logo/TV%20Telugu%20Cricket.png" group-title="Cricket",{name}\n')

            # DRM Clearkey Extraction
            params_str = url_raw.split('|')[1] if '|' in url_raw else ""
            if "drmLicense=" in params_str:
                key = params_str.split("drmLicense=")[1].split("&")[0]
                f.write("#KODIPROP:inputstream.adaptive.license_type=clearkey\n")
                f.write(f"#KODIPROP:inputstream.adaptive.license_key={key}\n")
            
            # Formatted headers for TiviMate / OTT Navigator compatibility
            f.write(f'#EXTHTTP:{{"User-Agent":"{DEFAULT_UA}","Connection":"keep-alive","Origin":"https://jiotv.com/"}}\n')
            f.write(f"{base_url}\n\n")
            working_count += 1

    # Telegram Notification Update
    msg = (
        f"<b>🏏 Cricket Playlist Updated!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Active Streams:</b> <code>{working_count}</code>\n"
        f"🕒 <b>Last Update:</b> <code>{ist_timestamp()}</code>\n\n"
        f"🔄 <b>Refresh or Reload your Playlist now!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 @tvtelugu"
    )
    
    send_telegram_msg(msg)
    print(f">>> Process finished. {working_count} streams added.")

if __name__ == "__main__":
    main()
    
