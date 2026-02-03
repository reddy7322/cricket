import requests
import re
import sys
from datetime import datetime, timedelta, timezone

JSON_URL = "https://pasteking.u0k.workers.dev/3qsxt.json"
OUTPUT_M3U = "cricket.m3u"

DEFAULT_GROUP = "𝐂𝐫𝐢𝐜𝐤𝐞𝐭"
POWERED_BY = "Powered By @tvtelugu"

DEFAULT_LOGO = "https://tvtelugu.pages.dev/logo/TV%20Telugu%20Cricket.png"
GROUP_LOGO = DEFAULT_LOGO

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/143.0.0.0 Safari/537.36"
)

def ordinal(n):
    if 11 <= n <= 13:
        return f"{n}th"
    return f"{n}{['th','st','nd','rd','th','th','th','th','th','th'][n % 10]}"

def ist_timestamp():
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return now.strftime(f"{ordinal(now.day)} %b %Y | %I:%M:%S %p")

def parse_headers(url: str) -> str:
    if "|" not in url:
        return url + f"|user-agent={DEFAULT_UA}"

    base, headers = url.split("|", 1)
    headers = headers.lstrip("?&")

    parts = re.split(r"[&|]", headers)
    clean_headers = []

    for part in parts:
        if "=" in part:
            k, v = part.split("=", 1)
            clean_headers.append(f"{k.strip()}={v.strip()}")

    if not any(h.lower().startswith("user-agent=") for h in clean_headers):
        clean_headers.append(f"user-agent={DEFAULT_UA}")

    return base + "|" + "|".join(clean_headers)

def main():
    print(">>> Generator started")

    try:
        r = requests.get(JSON_URL, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print("❌ JSON fetch failed:", e)
        sys.exit(1)

    data = r.json()

    event = data.get("event", {})
    match_type = event.get("match_type", "LIVE")

    streams = data.get("streams", [])
    if not streams:
        print("❌ No streams found")
        sys.exit(1)

    timestamp = ist_timestamp()

    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Last Updated : {timestamp}\n")
        f.write(f"# {POWERED_BY}\n\n")

        for s in streams:
            language = s.get("language", "Unknown").replace("✨", "").strip()
            url = s.get("url", "").strip()
            if not url:
                continue

            final_url = parse_headers(url)
            channel_name = f"{match_type} - {language}"

            f.write(
                f'#EXTINF:-1 '
                f'tvg-name="{channel_name}" '
                f'tvg-logo="{DEFAULT_LOGO}" '
                f'group-title="{DEFAULT_GROUP}" '
                f'group-logo="{GROUP_LOGO}",'
                f'{channel_name}\n'
            )
            f.write(final_url + "\n\n")

    print(">>> cricket.m3u generated successfully")

if __name__ == "__main__":
    main()
