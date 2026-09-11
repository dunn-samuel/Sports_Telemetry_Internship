import requests
import json
import re
from datetime import datetime, timedelta
import pandas as pd
import time
import schedule
import os

os.environ['TZ'] = 'Europe/London'
time.tzset()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def take_html_snapshot(sport_name, match_id, interval_label, teams, scheduled_date):
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    if current_date_str != scheduled_date:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Skipped {teams} ({interval_label}): Scheduled for {scheduled_date}, current date is {current_date_str}.")
        return

    snapshot_dir = f"snapshots_{scheduled_date}"
    if not os.path.exists(snapshot_dir):
        os.makedirs(snapshot_dir)

    url = f"https://www.bbc.co.uk/sport/{sport_name.lower()}/live/{match_id}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        timestamp = datetime.now().strftime('%H%M%S')
        safe_teams = "".join(c for c in teams if c.isalnum() or c in (' ', '-')).replace(" ", "-")
        filename = f"{snapshot_dir}/{timestamp}_{safe_teams}_{interval_label}.html"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Snapshot saved: {filename}")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error taking snapshot for {teams}: {e}")

def is_target_match(sport, tourney_name, stage_name):
    tourney = (tourney_name or "").lower()
    stage = (stage_name or "").lower()
    if sport == "Football":
        return "world cup" in tourney or "world cup" in stage
    return False

def run_football_pipeline():
    schedule.clear('snapshots')

    dates_to_check = [
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    ]

    for target_date_str in dates_to_check:
        print(f"Initiating football schedule check for: {target_date_str}")
        daily_fixtures = []
        seen_match_ids = set()

        TARGET_URLS = {
            "Football": f"https://www.bbc.co.uk/sport/football/scores-fixtures/{target_date_str}"
        }

        for sport_name, index_url in TARGET_URLS.items():
            try:
                response = requests.get(index_url, headers=HEADERS)
                if response.status_code != 200:
                    print(f"Unable to retrieve {sport_name} schedule for {target_date_str}.")
                    continue

                match = re.search(r'window\.__INITIAL_DATA__\s*=\s*"(.*?)";', response.text)
                if not match: 
                    continue

                raw_json = match.group(1).encode().decode('unicode_escape')
                bbc_data = json.loads(raw_json)

                main_data = bbc_data.get('data', {})
                for key in main_data.keys():
                    if 'sport-data-scores-fixtures' in key:
                        events = main_data[key].get('data', {}).get('eventGroups', [])
                        for tourney_group in events:
                            tourney_name = tourney_group.get('displayLabel', 'Unknown')
                            for stage in tourney_group.get('secondaryGroups', []):
                                stage_name = stage.get('displayLabel', 'Unknown')
                                if not is_target_match(sport_name, tourney_name, stage_name): 
                                    continue

                                for game in stage.get('events', []):
                                    match_id = game.get('tipoTopicId', '')
                                    if not match_id or match_id in seen_match_ids: 
                                        continue

                                    home_team = game.get('home', {}).get('fullName', 'Unknown')
                                    away_team = game.get('away', {}).get('fullName', 'Unknown')
                                    ko_str = game.get('time', {}).get('displayTimeUK', '00:00')

                                    seen_match_ids.add(match_id)
                                    daily_fixtures.append({
                                        "sport": sport_name,
                                        "stage": f"{tourney_name} - {stage_name}",
                                        "teams": f"{home_team}-vs-{away_team}",
                                        "kick_off": ko_str,
                                        "match_id": match_id
                                    })

                                    try:
                                        ko_time = datetime.strptime(f"{target_date_str} {ko_str}", "%Y-%m-%d %H:%M")
                                        intervals = {
                                            "start": 5, "mid_h1": 24, "ht": 48,
                                            "mid_h2": 87, "end": 112, "et_start": 120,
                                            "et_ht": 137, "pens": 155
                                        }

                                        for label, min_offset in intervals.items():
                                            target_time = ko_time + timedelta(minutes=min_offset)
                                            if target_time > datetime.now():
                                                schedule.every().day.at(target_time.strftime("%H:%M")).do(
                                                    take_html_snapshot,
                                                    sport_name=sport_name,
                                                    match_id=match_id,
                                                    interval_label=label,
                                                    teams=f"{home_team}-vs-{away_team}",
                                                    scheduled_date=target_date_str
                                                ).tag('snapshots')
                                    except ValueError: 
                                        pass

            except Exception as e:
                print(f"Error processing {sport_name}: {e}")
            time.sleep(1)

        if daily_fixtures:
            pd.DataFrame(daily_fixtures).to_csv(f"Daily_Schedule_{target_date_str}.csv", index=False)
            print(f"Scheduled snapshots for {len(daily_fixtures)} matches on {target_date_str}.")
        else:
            print(f"No targeted football matches found for {target_date_str}.")