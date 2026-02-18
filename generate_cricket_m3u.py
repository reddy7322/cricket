import requests
import json
import sys
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
JSON_URLS = [
    "https://pasteking.u0k.workers.dev/xzdzw.json",
    "https://sports.vodep39240327.workers.dev/sports.json"
]
OUTPUT_M3U = "cricket_pro.m3u"

DEFAULT_GROUP = "𝐂𝐫𝐢𝐜𝐤𝐞𝐭"
POWERED_BY = "Powered By @tvtelugu"
DEFAULT_LOGO = "https://tvtelugu.pages.dev/logo/TV%20Telugu%20Cricket.png"
DEFAULT_UA = "plaYtv/7.1.3 (Linux;Android 13) ExoPlayerLib/824.0"

def ist_timestamp():
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return now.strftime("%d %b %Y | %I:%M:%S %p")

def process_stream(stream, match_type):
    url_raw = stream.get("url", "").strip()
    if not url_raw:
        return None

    # Handle the pipe format used in some workers
    parts = url_raw.split('|')
    base_url = parts[0]
    
    # Extract params into a dictionary
    params = {}
    if len(parts) > 1:
        param_pairs = parts[1].split('&')
        for pair in param_pairs:
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k] = v

    language = stream.get("language", "Unknown").replace("✨", "").strip()
    channel_name = f"{match_type} - {language}"
    
    # 1. Start writing the entry
    entry = f'#EXTINF:-1 tvg-name="{channel_name}" tvg-logo="{DEFAULT_LOGO}" group-title="{DEFAULT_GROUP}",{channel_name}\n'
    
    # 2. Add DRM properties for TiviMate/OTT Navigator
    drm_license = params.get("drmLicense") or params.get("license_key")
    if drm_license:
        entry += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
        entry += f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n'
    
    # 3. Add Headers via #EXTHTTP (Best for TiviMate)
    headers = {
        "User-Agent": params.get("User-Agent") or params.get("user-agent") or DEFAULT_UA
    }
    if params.get("Cookie"): headers["Cookie"] = params.get("Cookie")
    if params.get("Origin"): headers["Origin"] = params.get("Origin")
    if params.get("Referer"): headers["Referer"] = params.get("Referer")
    
    entry += f'#EXTHTTP:{json.dumps(headers)}\n'
    
    # 4. Final URL
    entry += f'{base_url}\n'
    return entry

def main():
    print(">>> Starting Pro IPTV Generator")
    all_entries = []

    for url in JSON_URLS:
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()
            
            event = data.get("event", {})
            match_type = event.get("match_type", "LIVE")
            streams = data.get("streams", [])
            
            for s in streams:
                entry = process_stream(s, match_type)
                if entry:
                    all_entries.append(entry)
            print(f"✅ Fetched {len(streams)} streams from: {url}")
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")

    if not all_entries:
        print("❌ No streams found. Exiting.")
        sys.exit(1)

    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Generated: {ist_timestamp()}\n")
        f.write(f"# {POWERED_BY}\n\n")
        for entry in all_entries:
            f.write(entry + "\n")

    print(f"\n>>> Success! '{OUTPUT_M3U}' generated with {len(all_entries)} channels.")

if __name__ == "__main__":
    main()
