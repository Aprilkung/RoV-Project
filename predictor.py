import pandas as pd
from hero_dictionary import hero_roles

class RoVDraftRecommender:
    def __init__(self):
        print("Loading Recommender...")
        self.df_base = pd.read_csv("base_winrate.csv")
        self.df_syn = pd.read_csv("synergy.csv")
        self.df_ctr = pd.read_csv("counter.csv")

        # Total_Presence
        if 'Bans' in self.df_base.columns:
            self.df_base['Total_Presence'] = self.df_base['Matches'] + self.df_base['Bans']
        else:
            self.df_base['Total_Presence'] = self.df_base['Matches']

    def get_bayesian_base_wr(self, hero, C=20, m=0.45): 
        row = self.df_base[self.df_base['Hero'] == hero]
        if row.empty:
            return m, 0.0
            
        matches = row['Matches'].values[0]
        wr = row['WinRate'].values[0]
        presence = row['Total_Presence'].values[0] # ดึงค่าการมีส่วนร่วมรวม
        
        adjusted_wr = ((C * m) + (matches * wr)) / (C + matches)
        return adjusted_wr, float(presence)

    def get_pair_score(self, df, col_name, pair_name):
        row = df[df[col_name] == pair_name]
        if row.empty:
            return None 
            
        matches = row['Matches'].values[0]
        if matches < 10:
            return None 
            
        return row['WinRate'].values[0]

    def recommend(self, my_role, allies, enemies, mastery_dict=None, ban_list=None):
        if mastery_dict is None: mastery_dict = {}
        if ban_list is None: ban_list = []
        
        num_allies = len(allies)
        num_enemies = len(enemies)
        
        w_base = 0.20
        w_pop = 0.20
        w_syn = 0.20
        w_ctr = 0.20
        w_mas = 0.20
        
        max_presence = self.df_base['Total_Presence'].max() if not self.df_base.empty else 1.0

        results = []
        
        for hero, roles in hero_roles.items():
            if my_role not in roles: continue
            if hero in allies or hero in enemies or hero in ban_list: continue
            
            # 1. Base Score
            base_score, presence = self.get_bayesian_base_wr(hero)

            # 2. Pop Score
            pop_score = min(presence / max_presence, 1.0)
            
            # 3. Synergy Score
            syn_score = 0.0
            if num_allies > 0:
                total_syn = 0
                for ally in allies:
                    pair = "-".join(sorted([hero, ally]))
                    score = self.get_pair_score(self.df_syn, 'Hero_Pair', pair)
                    total_syn += score if score is not None else 0.46
                syn_score = total_syn / num_allies
                
            # 4. Counter Score
            ctr_score = 0.0
            if num_enemies > 0:
                total_ctr = 0
                for enemy in enemies:
                    if hero < enemy:
                        pair = f"{hero}_vs_{enemy}"
                        score = self.get_pair_score(self.df_ctr, 'Ally_vs_Enemy', pair)
                        total_ctr += score if score is not None else 0.46
                    else:
                        pair = f"{enemy}_vs_{hero}"
                        score = self.get_pair_score(self.df_ctr, 'Ally_vs_Enemy', pair)
                        total_ctr += (1.0 - score) if score is not None else 0.46
                ctr_score = total_ctr / num_enemies
                
            # 5. Mastery Score
            mas_score = mastery_dict.get(hero, 0.0)
            
            # Normalize Weights
            active_weight = w_base + w_pop  
            if num_allies > 0: active_weight += w_syn
            if num_enemies > 0: active_weight += w_ctr
            if mastery_dict: active_weight += w_mas 
            
            raw_score = (w_base * base_score) + (w_pop * pop_score) + (w_syn * syn_score) + (w_ctr * ctr_score) + (w_mas * mas_score)
            
            final_score = raw_score / active_weight if active_weight > 0 else 0.0
            
            results.append({
                "Hero": hero,
                "FinalScore": round(final_score * 100, 2),
                "Base": round(base_score, 2),
                "Pop": round(pop_score, 2),
                "Syn": round(syn_score, 2),
                "Ctr": round(ctr_score, 2)
            })
            
        # sorting
        results_sorted = sorted(results, key=lambda x: x["FinalScore"], reverse=True)
        return results_sorted[:3]

# Testing
if __name__ == "__main__":
    recommender = RoVDraftRecommender()
    
    my_role = "roaming"
    my_team = [] 
    enemy_team = []
    ban_list = ["kilgroth", "lubu", "omen","billow","tachi"]
    
    my_mastery = {}
    
    print(f"\n--- Top 3 Recommendations for {my_role} ---")
    top3 = recommender.recommend(my_role, my_team, enemy_team, my_mastery, ban_list)
    
    for i, data in enumerate(top3, 1):
        print(f"Rank {i}: {data['Hero'].upper()} | Recommendation: {data['FinalScore']}%")
        print(f"   (Stats: Winrate={data['Base']}, Pop={data['Pop']}, Synergy={data['Syn']}, Counter={data['Ctr']})")