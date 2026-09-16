import pandas as pd
from itertools import combinations

def calculate_heuristic_stats(input_file):
    print("Loading file...", input_file)
    df = pd.read_csv(input_file)
    
    # Dictionary
    base_stats = {}
    synergy_stats = {}
    counter_stats = {}
    
    # 1. แก้ไข stat func ให้รับค่า weight (Time Decay)
    def add_stat(stat_dict, key, is_win, weight):
        if key not in stat_dict:
            # เปลียนจาก 0 เป็น 0.0 เพื่อรองรับทศนิยม
            stat_dict[key] = {'match': 0.0, 'win': 0.0}
            
        # บวกด้วยค่า weight แทนการบวก 1
        stat_dict[key]['match'] += weight
        if is_win:
            stat_dict[key]['win'] += weight

    print("Calculating statistics, please wait...")
    
    for index, row in df.iterrows():
        winner = row['Winner']
        
        # 2. ดึงค่า Time_Weight ออกมาจากข้อมูลแต่ละแถว
        weight = float(row['Time_Weight'])
        
        t1_picks = [str(row[f'T1_Pick{i}']).strip() for i in range(1, 6)]
        t2_picks = [str(row[f'T2_Pick{i}']).strip() for i in range(1, 6)]
        
        t1_win = True if winner == 1 else False
        t2_win = True if winner == 2 else False

        # --- T1 Stats ---
        for hero in t1_picks:
            # 3. โยนค่า weight เข้าไปในทุกๆ การคำนวณ
            add_stat(base_stats, hero, t1_win, weight) 
            
            # Counter Stats
            for enemy in t2_picks:
                if hero < enemy:
                    add_stat(counter_stats, f"{hero}_vs_{enemy}", t1_win, weight)
                else:
                    add_stat(counter_stats, f"{enemy}_vs_{hero}", not t1_win, weight)
                
        for hero_a, hero_b in combinations(t1_picks, 2):
            pair_name = "-".join(sorted([hero_a, hero_b])) 
            add_stat(synergy_stats, pair_name, t1_win, weight)
            
        # --- T2 Stats ---
        for hero in t2_picks:
            add_stat(base_stats, hero, t2_win, weight)
                
        for hero_a, hero_b in combinations(t2_picks, 2):
            pair_name = "-".join(sorted([hero_a, hero_b]))
            add_stat(synergy_stats, pair_name, t2_win, weight)

    # --- ฟังก์ชันแปลง Dictionary เป็น DataFrame และคำนวณ Win Rate ---
    def make_dataframe(stat_dict, name_col):
        data_list = []
        for name, stats in stat_dict.items():
            # ปัดเศษทศนิยมให้ดูสวยงาม (Effective Matches/Wins)
            matches = round(stats['match'], 2)
            wins = round(stats['win'], 2)
            
            # ป้องกัน Error กรณี match เป็น 0 (แม้จะแทบเป็นไปไม่ได้)
            win_rate = round(wins / matches, 4) if matches > 0 else 0.0
            
            data_list.append({
                name_col: name,
                'Matches': matches,
                'Wins': wins,
                'WinRate': win_rate
            })
        return pd.DataFrame(data_list).sort_values(by='Matches', ascending=False)

    df_base = make_dataframe(base_stats, 'Hero')
    df_base.to_csv("base_winrate.csv", index=False)
    
    df_synergy = make_dataframe(synergy_stats, 'Hero_Pair')
    df_synergy.to_csv("synergy.csv", index=False)
    
    df_counter = make_dataframe(counter_stats, 'Ally_vs_Enemy')
    df_counter.to_csv("counter.csv", index=False)
    
    print("Complete 3 Files")

if __name__ == "__main__":
    calculate_heuristic_stats("rov_dataset_cleaned.csv")