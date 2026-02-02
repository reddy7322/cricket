import requests
import re
import sys

JSON_URL = "https://pasteking.u0k.workers.dev/3qsxt.json"
OUTPUT_M3U = "cricket.m3u"

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/143.0.0.0 Safari/537.36"
)

def parse_headers(url: str) -> str:
    """
    Converts Android-incompatible headers into:
    url|header=value|header=value
    """
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
    title = event.get("short_title", "Live Cricket")
    sport = event.get("sport", "Cricket")

    streams = data.get("streams", [])

    if not streams:
        print("❌ No streams found in JSON")
        sys.exit(1)

    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        for s in streams:
            language = s.get("language", "Unknown")
            provider = s.get("provider", "Live")
            url = s.get("url", "").strip()

            if not url:
                continue

            final_url = parse_headers(url)

            name = f"{title} [{language}]"
            group = f"{sport} | {provider}"

            f.write(
                f'#EXTINF:-1 tvg-name="{name}" '
                f'group-title="{group}",{name}\n'
            )
            f.write(final_url + "\n\n")

    print(">>> cricket.m3u generated successfully")


if __name__ == "__main__":
    main()
