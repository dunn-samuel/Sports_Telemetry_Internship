import requests
import re
from datetime import datetime
import time
import os

os.environ['TZ'] = 'Europe/London'
time.tzset()

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def run_tennis_pipeline():
    current_hour = datetime.now().hour
    if current_hour < 10 or current_hour >= 22:
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    snapshot_dir = f"snapshots_tennis_{today_str}"
    if not os.path.exists(snapshot_dir): 
        os.makedirs(snapshot_dir)

    hub_url = "https://www.bbc.co.uk/sport/tennis"
    try:
        resp = requests.get(hub_url, headers=HEADERS, timeout=15)
        if resp.status_code != 200: 
            return

        live_links = re.findall(r'href="/sport/tennis/live/([a-z0-9]+)"', resp.text)

        if live_links:
            mega_page_id = live_links[0]
            live_url = f"https://www.bbc.co.uk/sport/tennis/live/{mega_page_id}"
            live_resp = requests.get(live_url, headers=HEADERS, timeout=15, allow_redirects=True)

            if live_resp.status_code == 200:
                timestamp = datetime.now().strftime('%H%M%S')
                filename = f"{snapshot_dir}/{timestamp}_Wimbledon_MegaPage.html"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(live_resp.text)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Tennis snapshot saved: {filename}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Tennis live page returned status code {live_resp.status_code}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No active live tennis links identified on hub.")

    except Exception as e:
        print(f"Error executing tennis pipeline: {e}")