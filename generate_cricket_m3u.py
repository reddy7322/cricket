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
CHAT_ID = "959113182"

def ist_timestamp():
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return now.strftime("%d %b %Y | %I:%M:%S %p")

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

def is_working(url):
    """
    Improved check. Many working streams return 403 or 405 to bots.
    We only skip if the connection is totally refused or 404.
    """
    try:
        # We use a GET request with a small chunk size to see if the server responds at all
        response = requests.get(url, timeout=5, headers={"User-Agent": DEFAULT_UA}, stream=True)
        # 200 is perfect, 403/405 often means the stream is live but protected
        return response.status_code in [200, 403, 405]
    except:
        return False

def main():
    print(">>> Starting Generator (Fixed Fetching Logic)")
    all_streams = []
    seen_urls = set()

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
            print(f"✅ Loaded {len(streams)} streams from {url}")
        except Exception as e:
            print(f"❌ Source Error: {e}")

    working_count = 0
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Updated: {ist_timestamp()}\n\n")

        for s in all_streams:
            url_raw = s.get("url", "").strip()
            if not url_raw:
                continue

            # Split the URL from the parameters
            parts = url_raw.split('|')
            base_url = parts[0]

            # Duplicate Check
            if base_url in seen_urls:
                continue

            # Validate Stream (Using the new lenient check)
            if not is_working(base_url):
                print(f"⚠️  Skipping likely dead stream: {s.get('language')}")
                continue

            seen_urls.add(base_url)

            # Parse DRM and Headers
            params = {}
            if len(parts) > 1:
                param_section = parts[1].replace('|', '&')
                pairs = param_section.split('&')
                for pair in pairs:
                    if '=' in pair:
                        k, v = pair.split('=', 1)
                        params[k.strip()] = v.strip()

            lang = s.get("language", "Unknown").replace("✨", "").strip()
            name = f"{s['m_label']} - {lang}"
            
            f.write(f'#EXTINF:-1 tvg-logo="https://tvtelugu.pages.dev/logo/TV%20Telugu%20Cricket.png" group-title="Cricket",{name}\n')

            # Correctly identify DRM keys
            drm = params.get("drmLicense") or params.get("license_key") or params.get("drm")
            if drm:
                f.write("#KODIPROP:inputstream.adaptive.license_type
                        
