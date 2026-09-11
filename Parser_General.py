import os
import re
import json
from bs4 import BeautifulSoup
import pandas as pd

def extract_match_data(file_path, filename, folder_name):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')

        actual_clock = ""
        possible_classes = [
            'sp-c-fixture__status', 
            'sp-c-fixture__status gs-u-display-block',
            'fixture__status',
            'ssm-fixture__status',
            'gel-minion gs-u-display-block' 
        ]
        clock_element = soup.find(['span', 'div'], class_=possible_classes)
        
        if clock_element:
            actual_clock = clock_element.get_text(strip=True)
        else:
            fallback = soup.find(lambda tag: tag.name in ['span', 'div'] and tag.get('class') and 'status' in ' '.join(tag.get('class', [])).lower())
            if fallback:
                actual_clock = fallback.get_text(strip=True)

        time_str = filename[:4] + ":" + filename[4:6] if len(filename) >= 6 else None
        date_str = folder_name.split('_')[-1] if '_' in folder_name else None

        viewers = None
        viewing_element = soup.find('span', {'data-testid': 'viewer-count'})
        if viewing_element:
            raw_text = viewing_element.text
            viewers = int(raw_text.split(' ')[0].replace(',', ''))

        json_match = re.search(r'window\.__INITIAL_DATA__\s*=\s*"{?\\?"data\\?":({.*?})\\?\"}?";', html_content)

        sport, tournament, stage, home_entity, away_entity, venue = None, None, None, None, None, None
        is_uk_involved = 0

        if json_match:
            raw_json = json_match.group(1).replace('\\"', '"').replace('\\\\', '\\')
            try:
                data = json.loads(raw_json)
                for key, val in data.items():
                    if 'sportDataEvent' in val.get('data', {}):
                        event_data = val['data']['sportDataEvent']
                        sport = event_data.get('sportDiscipline')
                        tournament = event_data.get('tournament', {}).get('name')
                        stage = event_data.get('stage', {}).get('name')
                        venue = event_data.get('venue', {}).get('name')
                        home_team = event_data.get('home', {})
                        away_team = event_data.get('away', {})
                        home_entity = home_team.get('fullName')
                        away_entity = away_team.get('fullName')

                        uk_terms = ['England', 'Scotland', 'Wales', 'Northern Ireland', 'Great Britain', 'GBR']
                        if any(term in str(home_entity) for term in uk_terms) or \
                           any(term in str(away_entity) for term in uk_terms):
                            is_uk_involved = 1

                        if viewers is None and 'countingServiceDataAverage' in val['data']:
                            viewers = val['data']['countingServiceDataAverage']
                        break
            except json.JSONDecodeError:
                pass

        return {
            'Date': date_str, 'Time': time_str, 'Sport': sport, 'Competition': tournament,
            'Stage': stage, 'Actual_Clock': actual_clock, 'Home_Entity': home_entity,
            'Away_Entity': away_entity, 'Venue': venue, 'UK_Involved': is_uk_involved,
            'Viewers': viewers, 'Filename': filename
        }
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None

def extract_meta(filename):
    parts = filename.replace('.html', '').split('_')
    event = parts[1]
    sport, comp, home, away = "", "", "", ""
    if event == 'Wimbledon': sport, comp = 'Tennis', 'Wimbledon'
    elif event == 'F1': sport, comp = 'Motorsport', 'Formula 1'
    elif event == 'Golf': sport, comp = 'Golf', 'The Open'
    elif '-vs-' in event:
        sport, comp = 'Football', 'World Cup'
        teams = event.split('-vs-')
        if len(teams) == 2:
            home, away = teams[0].replace('-', ' '), teams[1].replace('-', ' ')
    stage = parts[2] if len(parts) > 2 else ""
    return pd.Series([sport, comp, stage, home, away])

def run_master_parser():
    base_dir = './'
    parsed_data = []

    print("Step 1: Scanning snapshot directories and parsing metadata...")
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(folder_path) and folder_name.startswith("snapshots_"):
            for filename in os.listdir(folder_path):
                if filename.endswith(".html"):
                    row_data = extract_match_data(os.path.join(folder_path, filename), filename, folder_name)
                    if row_data: parsed_data.append(row_data)

    if not parsed_data:
        print("No valid snapshot files found to parse.")
        return

    df = pd.DataFrame(parsed_data)
    print(f"Parsing complete. Extracted data from {len(df)} snapshots.")

    print("Step 2: Cleaning and transforming dataset...")
    df['Time'] = df['Filename'].str[:2] + ':' + df['Filename'].str[2:4] + ':' + df['Filename'].str[4:6]
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day_of_Week'] = df['Date'].dt.day_name()
    df[['Sport', 'Competition', 'Stage', 'Home_Entity', 'Away_Entity']] = df['Filename'].apply(extract_meta)

    name_replacements = {'Congo DR': 'D.R. Congo', 'United States': 'USA', 'Bosnia Herzegovina': 'Bosnia and Herzegovina'}
    df['Home_Entity'] = df['Home_Entity'].replace(name_replacements)
    df['Away_Entity'] = df['Away_Entity'].replace(name_replacements)

    uk_terms = ['England', 'Scotland', 'Wales', 'Northern Ireland', 'Great Britain', 'GBR']
    df['UK_Involved'] = df.apply(lambda row: 1 if any(term in str(row['Home_Entity']) for term in uk_terms) or any(term in str(row['Away_Entity']) for term in uk_terms) else 0, axis=1)

    df['Is_Televised'] = df['Viewers'].notna().astype(int)
    df['Viewers'] = df['Viewers'].fillna(0)
    df = df[~df['Home_Entity'].str.contains('U19', na=False)]
    df = df.dropna(subset=['Competition'])
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    final_cols = ['Date', 'Day_of_Week', 'Time', 'Sport', 'Competition', 'Stage', 'Actual_Clock', 'Home_Entity', 'Away_Entity', 'Venue', 'UK_Involved', 'Is_Televised', 'Viewers', 'Filename']
    df = df[final_cols]

    print("Step 3: Merging with pre-match betting odds...")
    odds_file_path = os.path.join(base_dir, 'Betting_Odds.xlsx')
    if os.path.exists(odds_file_path):
        xls = pd.ExcelFile(odds_file_path)
        df_odds = pd.read_excel(xls, sheet_name='Master Odds')

        for col in ['Competition', 'Home_Entity', 'Away_Entity']:
            if df[col].dtype == 'object': df[col] = df[col].astype(str).str.strip().replace('nan', '')
            if df_odds[col].dtype == 'object': df_odds[col] = df_odds[col].astype(str).str.strip().replace('nan', '')

        mega_events = ['The Open', 'Wimbledon', 'Formula 1', 'Commonwealth Games']
        df_h2h = df[~df['Competition'].isin(mega_events)]
        odds_h2h = df_odds[~df_odds['Competition'].isin(mega_events)].drop_duplicates(subset=['Competition', 'Home_Entity', 'Away_Entity'])
        df_h2h = pd.merge(df_h2h, odds_h2h[['Competition', 'Home_Entity', 'Away_Entity', 'UOH_Score']], on=['Competition', 'Home_Entity', 'Away_Entity'], how='left')

        df_mega = df[df['Competition'].isin(mega_events)]
        odds_mega = df_odds[df_odds['Competition'].isin(mega_events)].drop_duplicates(subset=['Competition'])
        df_mega = pd.merge(df_mega, odds_mega[['Competition', 'UOH_Score']], on=['Competition'], how='left')

        df_final = pd.concat([df_h2h, df_mega], ignore_index=True)
    else:
        print("Betting_Odds.xlsx not found. Skipping merge step.")
        df_final = df

    output_path = os.path.join(base_dir, 'Final_Merged_Internship_Dataset.csv')
    df_final.to_csv(output_path, index=False)
    print(f"Dataset successfully processed and exported to {output_path}.")

if __name__ == "__main__":
    run_master_parser()