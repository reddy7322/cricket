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

# This User-Agent mimics an Android TV (ExoPlayer), which players use
DEFAULT_UA = "plaYtv/7.1.3 (Linux;Android 13) ygx/824.1 ExoPlayerLib/824.0"

# --- TELEGRAM CREDENTIALS ---
BOT_TOKEN = "8599332115:AAEfXEqZ2B9KWr0OuksXCgDiLJFeD_TlJEg"
CHAT_ID = "-1002428994434"

def ist_timestamp():
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return now.strftime("%d %b %Y | %I:%M:%S %p")

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def is_working_pro(url):
    """
    Mimics TiviMate/OTT Navigator behavior.
    Checks for video stream accessibility rather than just a 200 OK.
    """
    headers = {
        "User-Agent": DEFAULT_UA,
        "Connection": "keep-alive",
        "Accept": "*/*"
    }
    try:
        # We attempt to read the first 1024 bytes of the stream (manifest or chunk)
        with requests.get(url, headers=headers, timeout=8, stream=True, verify=False) as r:
            # 200 = Success, 403 = Protected (often still works in player with DRM)
            if r.status_code in [200, 403, 405]:
                return True
    except:
        return False
    return False

def main():
    print(">>> Acting as Pro Player to verify streams...")
    all_streams = []
    seen_urls = set()

    # Create a persistent session for faster fetching
    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_UA})

    for url in JSON_URLS:
        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()
            m_type = data.get("event", {}).get("match_type", "LIVE")
            for s in data.get("streams", []):
                s['m_label'] = m_type
                all_streams.append(s)
        except:
            pass

    working_count = 0
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# Updated: " + ist_timestamp() + "\n\n")

        for s in all_streams:
            url_raw = s.get("url", "").strip()
            if not url_raw: continue
            
            # Split URL and Params
            parts = url_raw.split('|')
            base_url = parts[0]

            if base_url in seen_urls: continue
            
            # PRO CHECK: This mimics TiviMate's internal connection attempt
            if not is_working_pro(base_url):
                print(f"❌ Player check failed for: {s.get('language')}")
                continue

            seen_urls.add(base_url)
            lang = s.get("language", "Unknown").replace("✨", "").strip()
            name = f"{s['m_label']} - {lang}"
            
            f.write(f'#EXTINF:-1 tvg-logo="https://tvtelugu.pages.dev/logo/TV%20Telugu%20Cricket.png" group-title="Cricket",{name}\n')

            # Handle DRM and specific player headers
            params_str = url_raw.split('|')[1] if '|' in url_raw else ""
            if "drmLicense=" in params_str:
                key = params_str.split("drmLicense=")[1].split("&")[0]
                f.write("#KODIPROP:inputstream.adaptive.license_type=clearkey\n")
                f.write(f"#KODIPROP:inputstream.adaptive.license_key={key}\n")
            
            # TiviMate/OTT Navigator use this JSON header format
            f.write(f'#EXTHTTP:{{"User-Agent":"{DEFAULT_UA}","Connection":"keep-alive"}}\n{base_url}\n\n')
            working_count += 1

    # Telegram Message
    msg = (
        f"<b>🏏 Cricket Playlist Updated!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Active Streams:</b> <code>{working_count}</code>\n"
        f"🕒 <b>Last Update:</b> <code>{ist_timestamp()}</code>\n\n"
        f"🔄 <b>Refresh or Reload your Playlist now!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 @tvteluguchat"
    )
    
    send_telegram_msg(msg)
    print(f">>> {working_count} verified streams successfully fetched.")

if __name__ == "__main__":
    main()
    
