import requests
import time
import json
import os

def fetch_tournament_stats():
    api_url = "https://liquipedia.net/honorofkings/api.php"
    
    headers = {
        'User-Agent': 'RoVDraftRecommender/1.0 (Contact: https://github.com/Aprilkung/RoV-Project)'
    }
    
    # Tournament Pages to Fetch
    tournaments = [
        "RoV_Pro_League/2026/Winter/Playoffs",      
        "RoV_Pro_League/2026/Winter/Group_Stage",   

        "Arena_of_Valor_Premier_League/2026/Playoffs",
        "Arena_of_Valor_Premier_League/2026/Swiss_Stage", 
        "Arena_of_Valor_Premier_League/2026/Wildcard",

        "RoV_Pro_League/2026/Summer/Playoffs",
        "RoV_Pro_League/2026/Summer/Group_Stage",
        
        "Arena_of_Valor_International_Championship/2025/Knockout_Stage",
        "Arena_of_Valor_International_Championship/2025/Group_Stage"
    ]
    
    all_raw_data = []
    total_tournaments = len(tournaments)
    
    print(f"Ready to fetch {total_tournaments} tournaments...\n")
    
    # loop fetch
    for index, page_name in enumerate(tournaments):
        weight = (total_tournaments - index) / total_tournaments
        
        params = {
            "action": "parse",
            "page": page_name,
            "prop": "wikitext",
            "format": "json"
        }
        
        print(f"[{index+1}/{total_tournaments}] Fetching data: {page_name}")
        print(f" -> Time Decay Weight: {weight:.2f}")
        
        response = requests.get(api_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'parse' in data and 'wikitext' in data['parse']:
                wikitext = data['parse']['wikitext']['*']
                print(f" -> Success: {len(wikitext)} characters\n")
                
                # (Name , Weight, Wikitext)
                all_raw_data.append({
                    "tournament": page_name,
                    "time_weight": round(weight, 2),
                    "wikitext": wikitext
                })
            else:
                print(" -> Fails: Cannot see wikitext in response\n")
        else:
            print(f" -> Fails Https: {response.status_code}\n")
            
        time.sleep(5)

    # --- ระบบค้นหา Path แบบฉลาด ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    filename = os.path.join(data_dir, "all_tournaments_raw.json")
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_raw_data, f, ensure_ascii=False, indent=4)
        
    print(f"Save '{filename}' Complete! {len(all_raw_data)} tournaments fetched.")

if __name__ == "__main__":
    fetch_tournament_stats()