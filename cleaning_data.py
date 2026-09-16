import json
import re
import pandas as pd

def extract_rov_matches_from_json(file_path):
    # 1. เปิดไฟล์ JSON
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data_list = json.load(f)

    dataset = []

    # 2. วนลูปอ่านข้อมูลทีละทัวร์นาเมนต์
    for tournament_data in raw_data_list:
        t_name = tournament_data['tournament']
        t_weight = tournament_data['time_weight']
        wikitext = tournament_data['wikitext']

        # 3. ใช้ลอจิกเดิมของคุณ Split text ของทัวร์นาเมนต์นั้นๆ
        games_raw = wikitext.split("{{Map|")[1:] 

        for game in games_raw:
            # Winner Match
            winner_match = re.search(r'\|winner=(\d)', game)
            if not winner_match:
                continue
            
            winner = int(winner_match.group(1))
            
            # Time Weight
            row_data = {
                'Tournament': t_name,
                'Time_Weight': t_weight,
                'Winner': winner
            }
            is_valid = True
            
            # Pick
            for team in [1, 2]:
                for pick_num in range(1, 6):
                    pattern = fr'\|t{team}h{pick_num}=([^|\n]+)'
                    match = re.search(pattern, game)
                    if match:
                        raw_name = match.group(1).strip().lower()
                        clean_name = raw_name.split(' (')[0]
                        row_data[f'T{team}_Pick{pick_num}'] = clean_name
                    else:
                        is_valid = False
            
            # Ban
            for team in [1, 2]:
                for ban_num in range(1, 5):
                    pattern = fr'\|t{team}b{ban_num}=([^|\n}}]+)'
                    match = re.search(pattern, game)
                    if match:
                        raw_name = match.group(1).strip().lower()
                        clean_name = raw_name.split(' (')[0]
                        row_data[f'T{team}_Ban{ban_num}'] = clean_name
                    else:
                        is_valid = False

            if is_valid:
                dataset.append(row_data)

    # Pandas
    df = pd.DataFrame(dataset)
    return df

if __name__ == "__main__":

    file_name = "all_tournaments_raw.json" 
    
    print("Loading and Cleaning Data...")
    df = extract_rov_matches_from_json(file_name)
    
    # ดูตัวอย่างคอลัมน์ว่ามาครบไหม
    print(df[['Tournament', 'Time_Weight', 'Winner', 'T1_Pick1']].head())
    print(f"\nComplete: {len(df)} matchs")
    
    # CSV
    output_name = "rov_dataset_cleaned.csv"
    df.to_csv(output_name, index=False)
    print(f"Saving '{output_name}' complete")