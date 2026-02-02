import requests
import re

JSON_URL = "https://pasteking.u0k.workers.dev/3qsxt.json"
OUTPUT_M3U = "cricket.m3u"

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"

def parse_headers(url):
    """
    Converts:
    https://url.m3u8|referer=xxx&origin=yyy&user-agent=zzz
    into:
    https://url.m3u8|referer=xxx|origin=yyy|user-agent=zzz
    """
    if "|" not in url:
        return url

    base, headers = url.split("|", 1)
    headers = headers.lstrip("?&")

    parts = re.split(r"[&|]", headers)
    clean_headers = []

    for part in parts:
        if "=" in part:
            k, v = part.split("=", 1)
            clean_headers.append(f"{k.strip()}={v.strip()}")

    # Ensure User-Agent exists (important for OTT/TiviMate)
    if not any(h.lower().startswith("user-agent=") for h in clean_headers):
        clean_headers.append(f"user-agent={DEFAULT_UA}")

    return base + "|" + "|".join(clean_headers)

def main():
    print("Fetching JSON...")
    r = requests.get(JSON_URL, timeout=15)
    r.raise_for_status()
    data = r.json()

    event = data.get("event", {})
    title = event.get("short_title", "Live Cricket")
    sport = event.get("sport", "Cricket")

    streams = data.get("streams", [])

    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for s in streams:
            language = s.get("language", "Unknown")
            quality = s.get("quality", "")
            provider = s.get("provider", "")
            url = s.get("url", "")

            final_url = parse_headers(url)

            name = f"{title} [{language}]"
            group = f"{sport} | {provider}"

            f.write(
                f'#EXTINF:-1 tvg-name="{name}" '
                f'group-title="{group}",{name}\n'
            )
            f.write(final_url + "\n\n")

    print(f"Done ✅ Output saved as: {OUTPUT_M3U}")

if __name__ == "__main__":
    main()
