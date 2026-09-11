import requests
from datetime import datetime
import os
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
HUB_URL = "https://www.bbc.co.uk/sport/rugby-union" 
IGNORE_IDS = {"c87qn4g7wnwt"} 

def run_rugby_pipeline():
    today_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H%M%S")
    snapshot_dir = f"snapshots_rugby_{today_str}"
    
    if not os.path.exists(snapshot_dir): 
        os.makedirs(snapshot_dir)
        
    try:
        hub_resp = requests.get(HUB_URL, headers=HEADERS, timeout=15)
        if hub_resp.status_code == 200:
            found_ids = re.findall(r'(?:live|match)/([a-zA-Z0-9]{10,15})', hub_resp.text)
            for match_id in found_ids:
                if match_id not in IGNORE_IDS:
                    url = f"https://www.bbc.co.uk/sport/rugby-union/live/{match_id}"
                    filename = f"{snapshot_dir}/{timestamp}_Rugby_{match_id}.html"
                    resp = requests.get(url, headers=HEADERS, timeout=15)
                    if resp.status_code == 200:
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(resp.text)
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Saved Rugby snapshot: {match_id}")
    except Exception as e:
        print(f"Error executing Rugby pipeline: {e}")