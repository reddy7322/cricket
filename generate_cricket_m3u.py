import requests
import json
import sys
import os
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
JSON_URLS = [
    "https://pasteking.u0k.workers.dev/xzdzw.json",
    "https://sports.vodep39240327.workers.dev/sports.json"
]
OUTPUT_M3U = "cricket.m3u"
DEFAULT_UA = "plaYtv/7.1.3 (Linux;Android 13) ExoPlayerLib/824.0"

# --- TELEGRAM CREDENTIALS ---
BOT_TOKEN = "8599332115:AAEfXEqZ2B9KWr0OuksXCgDiLJFeD_TlJEg"
CHAT_ID = "-1002428994434" # Your group ID for @tvteluguchat

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
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def is_working(url):
    """Lenient check to ensure streams aren't wrongly skipped."""
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": DEFAULT_UA}, stream=True)
        return response.status_code in [200, 403, 405]
    except:
        return False

def main():
    print(">>> Generating Cricket Playlist for @tvteluguchat")
    all_streams = []
    seen_urls = set()
    source_status = []

    for url in JSON_URLS:
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()
            m_type = data.get("event", {}).get("match_type", "LIVE")
            streams = data.get("streams", [])
            for s in streams:
                s['m_label'] = m_type
                all_streams.append(s)
            source_status.append(f"✅ {url[:25]}...")
        except:
            source_status.append(f"❌ {url[:25]}...")

    working_count = 0
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# Updated: " + ist_timestamp() + "\n\n")

        for s in all_streams:
            url_raw = s.get("url", "").strip()
            if not url_raw: continue
            
            base_url = url_raw.split('|')[0]
            if base_url in seen_urls: continue
            if not is_working(base_url): continue

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
            
            f.write(f'#EXTHTTP:{{"User-Agent":"{DEFAULT_UA}"}}\n{base_url}\n\n')
            working_count += 1

    # Professional Message for the Group
    status_text = "\n".join(source_status)
    msg = (
        f"<b>🏏 Cricket Playlist Updated!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Active Streams:</b> <code>{working_count}</code>\n"
        f"🕒 <b>Last Update:</b> <code>{ist_timestamp()}</code>\n\n"
        f"📡 <b>Source Status:</b>\n{status_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <i>Optimized for TiviMate & OTT Navigator</i>\n"
        f"📢 @tvteluguchat"
    )
    
    send_telegram_msg(msg)
    print(f">>> Done! {working_count} streams verified.")

if __name__ == "__main__":
    main()
    
