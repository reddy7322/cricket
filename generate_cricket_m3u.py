import requests
import json
import sys
import os
import urllib3
from datetime import datetime, timedelta, timezone

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
JSON_URLS = [
    "https://pasteking.u0k.workers.dev/xzdzw.json",
    "https://sports.vodep39240327.workers.dev/sports.json"
]
OUTPUT_M3U = "cricket.m3u"
DEFAULT_UA = "plaYtv/7.1.3 (Linux;Android 13) ygx/824.1 ExoPlayerLib/824.0"

# --- TELEGRAM CREDENTIALS ---
BOT_TOKEN = "8267675444:AAEchiYEjLOeSzxE47jKdbgj_qKJfOq7k2I"
# Sending to both: Personal ID and Group ID
TARGET_IDS = ["959113182"]

def ist_timestamp():
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return now.strftime("%d %b %Y | %I:%M:%S %p")

def send_telegram_msg(message):
    for chat_id in TARGET_IDS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"❌ Telegram Error for {chat_id}: {e}")

def is_working_pro(url):
    headers = {
        "User-Agent": DEFAULT_UA,
        "Connection": "keep-alive",
        "Accept": "*/*",
        "Origin": "https://jiotv.com/",
        "Referer": "https://jiotv.com/"
    }
    try:
        with requests.get(url, headers=headers, timeout=10, stream=True, verify=False) as r:
            return r.status_code in [200, 403, 405]
    except:
        return False

def main():
    print(">>> Starting Update for Personal ID and @tvteluguchat...")
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
            
            parts = url_raw.split('|')
            base_url = parts[0]
            if base_url in seen_urls: continue
            if not is_working_pro(base_url): continue

            seen_urls.add(base_url)
            lang = s.get("language", "Unknown").replace("✨", "").strip()
            name = f"{s['m_label']} - {lang}"
            
            f.write(f'#EXTINF:-1 tvg-logo="https://tvtelugu.pages.dev/logo/TV%20Telugu%20Cricket.png" group-title="Cricket",{name}\n')

            params_str = url_raw.split('|')[1] if '|' in url_raw else ""
            if "drmLicense=" in params_str:
                key = params_str.split("drmLicense=")[1].split("&")[0]
                f.write("#KODIPROP:inputstream.adaptive.license_type=clearkey\n")
                f.write(f"#KODIPROP:inputstream.adaptive.license_key={key}\n")
            
            f.write(f'#EXTHTTP:{{"User-Agent":"{DEFAULT_UA}","Connection":"keep-alive","Origin":"https://jiotv.com/"}}\n')
            f.write(f"{base_url}\n\n")
            working_count += 1

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
    print(f">>> Done! Notification sent to all targets.")

if __name__ == "__main__":
    main()
    
