import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

TOP_6_PLAYERS = [
    "Sinner", "Zverev", "Auger-Aliassime", "Shelton", "Minaur", "Fritz",
    "Sabalenka", "Rybakina", "Swiatek", "Pegula", "Andreeva", "Anisimova",
    "Alcaraz", "Djokovic", "Medvedev", "Gauff", "Paolini"
]

UK_PLAYERS = [
    "Swan", "Chionski", "Choinski", "Fearnley", "Boulter", "Klugman", 
    "Dudeney", "Jones", "Xu", "Stojsavljevic", "Dart", "Wendelken", 
    "Harris", "Samuel", "Pinnington", "Gill", "Basing", "Tarvet", 
    "Norrie", "Fery", "Draper", "Raducanu", "Murray", "Evans"
]

MATCH_ODDS_DB = [
    {'winner': 'Andreeva', 'loser': 'Linette', 'uoh': 0.967741935},
    {'winner': 'Arevalo', 'loser': 'Krawietz', 'uoh': 0.777777778},
    {'winner': 'Auger-Aliassime', 'loser': 'Prizmic', 'uoh': 0.958333333},
    {'winner': 'Auger-Aliassime', 'loser': 'Zheng', 'uoh': 0.959488273},
    {'winner': 'Auger-Aliassime', 'loser': 'Fokina', 'uoh': 0.697560976},
    {'winner': 'Berrettini', 'loser': 'Wawrinka', 'uoh': 0.933333333},
    {'winner': 'Berrettini', 'loser': 'Fils', 'uoh': 0.791666667},
    {'winner': 'Bublik', 'loser': 'Tiafoe', 'uoh': 0.555555556},
    {'winner': 'Cobolli', 'loser': 'Minaur', 'uoh': 0.919889503},
    {'winner': 'Dimitrov', 'loser': 'Mensik', 'uoh': 0.738095238},
    {'winner': 'Dimitrov', 'loser': 'Berrettini', 'uoh': 0.67961165},
    {'winner': 'Djokovic', 'loser': 'Yibing', 'uoh': 0.994200497},
    {'winner': 'Djokovic', 'loser': 'Tsitsipas', 'uoh': 0.953488372},
    {'winner': 'Djokovic', 'loser': 'Rinderknech', 'uoh': 0.977198697},
    {'winner': 'Djokovic', 'loser': 'Safiullin', 'uoh': 0.955414013},
    {'winner': 'Djokovic', 'loser': 'Auger-Aliassime', 'uoh': 0.693069307},
    {'winner': 'Eala', 'loser': 'Swiatek', 'uoh': 0.932400932},
    {'winner': 'Fery', 'loser': 'Dimitrov', 'uoh': 0.839694656},
    {'winner': 'Fery', 'loser': 'Cobolli', 'uoh': 0.842490842},
    {'winner': 'Fritz', 'loser': 'Lajovic', 'uoh': 0.996015936},
    {'winner': 'Fritz', 'loser': 'Bublik', 'uoh': 0.81300813},
    {'winner': 'Gauff', 'loser': 'Sierra', 'uoh': 0.980392157},
    {'winner': 'Gauff', 'loser': 'Liu', 'uoh': 0.975177305},
    {'winner': 'Gauff', 'loser': 'Bencic', 'uoh': 0.523560209},
    {'winner': 'Gauff', 'loser': 'Pegula', 'uoh': 0.69124424},
    {'winner': 'Joint', 'loser': 'Williams', 'uoh': 0.558139535},
    {'winner': 'Keys', 'loser': 'Swan', 'uoh': 0.99009901},
    {'winner': 'Keys', 'loser': 'Anisimova', 'uoh': 0.70754717},
    {'winner': 'Kostyuk', 'loser': 'Paolini', 'uoh': 0.849056604},
    {'winner': 'Krejcikova', 'loser': 'Andreeva', 'uoh': 0.77092511},
    {'winner': 'Medvedev', 'loser': 'Cilic', 'uoh': 0.862068966},
    {'winner': 'Mertens', 'loser': 'Rybakina', 'uoh': 0.933333333},
    {'winner': 'Muchova', 'loser': 'Osaka', 'uoh': 0.641025641},
    {'winner': 'Muchova', 'loser': 'Gauff', 'uoh': 0.55},
    {'winner': 'Noskova', 'loser': 'Keys', 'uoh': 0.671361502},
    {'winner': 'Noskova', 'loser': 'Mertens', 'uoh': 0.697560976},
    {'winner': 'Noskova', 'loser': 'Kostyuk', 'uoh': 0.642857143},
    {'winner': 'Noskova', 'loser': 'Muchova', 'uoh': 0.639423077},
    {'winner': 'Osaka', 'loser': 'Kasatkina', 'uoh': 0.955414013},
    {'winner': 'Osaka', 'loser': 'Sabalenka', 'uoh': 0.795918367},
    {'winner': 'Ostapenko', 'loser': 'Dart', 'uoh': 0.892857143},
    {'winner': 'Paolini', 'loser': 'Eala', 'uoh': 0.676328502},
    {'winner': 'Patten', 'loser': 'Kokkinakis', 'uoh': 0.862068966},
    {'winner': 'Patten', 'loser': 'Arevalo', 'uoh': 0.578947368},
    {'winner': 'Pegula', 'loser': 'Jovic', 'uoh': 0.845864662},
    {'winner': 'Rybakina', 'loser': 'Boisson', 'uoh': 0.999394306},
    {'winner': 'Rybakina', 'loser': 'McNally', 'uoh': 0.943877551},
    {'winner': 'Sabalenka', 'loser': 'Kostovic', 'uoh': 0.998638221},
    {'winner': 'Sabalenka', 'loser': 'Kessler', 'uoh': 0.98400984},
    {'winner': 'Sabalenka', 'loser': 'Ostapenko', 'uoh': 0.914454277},
    {'winner': 'Sinner', 'loser': 'Kecmanovic', 'uoh': 0.999200639},
    {'winner': 'Sinner', 'loser': 'Borges', 'uoh': 0.998638221},
    {'winner': 'Sinner', 'loser': 'Brooksby', 'uoh': 0.99626401},
    {'winner': 'Sinner', 'loser': 'Mochizuki', 'uoh': 0.999091735},
    {'winner': 'Sinner', 'loser': 'Struff', 'uoh': 0.99626401},
    {'winner': 'Sinner', 'loser': 'Djokovic', 'uoh': 0.947867299},
    {'winner': 'Sinner', 'loser': 'Zverev', 'uoh': 0.947867299},
    {'winner': 'Swiatek', 'loser': 'Townsend', 'uoh': 0.964912281},
    {'winner': 'Swiatek', 'loser': 'Pliskova', 'uoh': 0.92348285},
    {'winner': 'Zverev', 'loser': 'Blockx', 'uoh': 0.985915493},
    {'winner': 'Zverev', 'loser': 'Royer', 'uoh': 0.996884735},
    {'winner': 'Zverev', 'loser': 'Giron', 'uoh': 0.993048659},
    {'winner': 'Zverev', 'loser': 'Lehecka', 'uoh': 0.995024876},
    {'winner': 'Zverev', 'loser': 'Fritz', 'uoh': 0.578947368},
    {'winner': 'Zverev', 'loser': 'Fery', 'uoh': 0.977198697}
]

def clean_player_name(raw_string):
    return re.sub(r'\(.*', '', raw_string).strip()

def extract_stage(court_lines):
    stage_keywords = ["Round of 16", "Quarter-final", "Semi-final", "Final", 
                      "First Round", "Second Round", "Third Round", "Fourth Round"]
    for line in court_lines[:15]:
        for kw in stage_keywords:
            if kw.lower() in line.lower(): 
                return kw
    return "Group Stage"

def extract_live_marquee(court_lines):
    block_text = " ".join(court_lines)
    if "LIVE" not in block_text.upper(): 
        return None, None, None, None
    stage = extract_stage(court_lines)
    home_entity, away_entity = None, None
    for line in court_lines:
        if " vs " in line.lower():
            parts = re.split(r'(?i) vs ', line)
            if len(parts) == 2:
                home_entity = clean_player_name(parts[0])
                away_entity = clean_player_name(parts[1])
                break
                
    uoh_score = None
    if home_entity and away_entity:
        for match in MATCH_ODDS_DB:
            if re.search(r'\b' + re.escape(match['winner']) + r'\b', block_text, re.IGNORECASE) and \
               re.search(r'\b' + re.escape(match['loser']) + r'\b', block_text, re.IGNORECASE):
                uoh_score = match['uoh']
                home_entity = match['winner']
                away_entity = match['loser']
                break
    return home_entity, away_entity, stage, uoh_score

def parse_snapshot(file_path, filename):
    uk_time, date_str, dow_str, viewer_count = "", "", "", ""
    uk_active, stars_active = 0, 0
    home_entity, away_entity, stage, uoh_score = None, None, None, None
    time_match = re.match(r'^(\d{2})(\d{2})\d{2}_', filename)
    if time_match: 
        uk_time = f"{time_match.group(1)}:{time_match.group(2)}"

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f: 
            html_content = f.read()
        date_match = re.search(r'"startDate":"(\d{4}-\d{2}-\d{2})"', html_content) or re.search(r'"datePublished":"(\d{4}-\d{2}-\d{2})', html_content)
        if date_match:
            dt = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            date_str = dt.strftime("%d/%m/%Y")
            dow_str = dt.strftime("%A")

        viewer_match = re.search(r'(\d[\d,]*)\s+viewing', html_content, re.IGNORECASE)
        if viewer_match: 
            viewer_count = int(viewer_match.group(1).replace(',', ''))

        soup = BeautifulSoup(html_content, 'html.parser')
        lines = [line.strip() for line in soup.get_text(separator='\n').splitlines() if line.strip()]

        current_court = None
        court_blocks = {"Centre Court": [], "No.1 Court": []}
        for line in lines:
            line_lower = line.lower()
            if line_lower == "centre court": 
                current_court = "Centre Court"
                continue
            elif line_lower in ["no.1 court", "no. 1 court", "court 1", "court one"]: 
                current_court = "No.1 Court"
                continue
            elif any(c in line_lower for c in ["no.2 court", "court 2", "court 3", "court 4", "court 18"]): 
                current_court = "Other Court"
                continue
            if current_court in court_blocks: 
                court_blocks[current_court].append(line)

        combined_text = " ".join(court_blocks["Centre Court"]) + " " + " ".join(court_blocks["No.1 Court"])
        if "LIVE" in combined_text.upper():
            if any(re.search(r'\b' + re.escape(p) + r'\b', combined_text, re.IGNORECASE) for p in UK_PLAYERS): 
                uk_active = 1
            if any(re.search(r'\b' + re.escape(p) + r'\b', combined_text, re.IGNORECASE) for p in TOP_6_PLAYERS) or re.search(r'\([1-6]\)', combined_text): 
                stars_active = 1

        home_entity, away_entity, stage, uoh_score = extract_live_marquee(court_blocks["Centre Court"])
        if home_entity is None:
            home_entity, away_entity, stage, uoh_score = extract_live_marquee(court_blocks["No.1 Court"])

    except Exception as e: 
        print(f"Error reading {file_path}: {e}")

    return {
        'Date': date_str, 'Day_of_Week': dow_str, 'UK_Time': uk_time, 'Sport': 'Tennis',
        'Competition': 'Wimbledon', 'Stage': stage if stage else '', 'Venue': 'Wimbledon',
        'Country': 'United Kingdom', 'Home_Entity': home_entity if home_entity else '',
        'Away_Entity': away_entity if away_entity else '', 'UK_Involved': uk_active,
        'Top_6': stars_active, 'Is_Televised': 1, 'Viewer_Count': viewer_count,
        'Filename': filename, 'UOH_Score': round(uoh_score, 4) if uoh_score else ''
    }

def run_wimbledon_parser():
    base_dir = './' 
    results = []
    print("Executing Wimbledon extraction parser...")
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if filename.endswith(".html") and "Wimbledon" in filename:
                results.append(parse_snapshot(os.path.join(root, filename), filename))

    df = pd.DataFrame(results)
    output_cols = ['Date', 'Day_of_Week', 'UK_Time', 'Sport', 'Competition', 'Stage', 'Venue', 
                   'Country', 'Home_Entity', 'Away_Entity', 'UK_Involved', 'Top_6', 
                   'Is_Televised', 'Viewer_Count', 'Filename', 'UOH_Score']
    df[output_cols].to_csv('Master_Wimbledon_Dataset.csv', index=False)
    print(f"Processing complete. Snapshots processed: {len(df)}.")

if __name__ == "__main__": 
    run_wimbledon_parser()