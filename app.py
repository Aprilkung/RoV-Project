import streamlit as st
from predictor import RoVDraftRecommender
from hero_dictionary import hero_roles

# --- 1. ตั้งค่าและ CSS ---
st.set_page_config(page_title="RoV Draft Simulator", page_icon="🎮", layout="wide")

st.markdown("""
<style>
    /* ปุ่ม Primary (ปุ่มที่กำลังถูกเลือก/ไฮไลท์) จะเป็นสีเหลือง */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #FFD700 !important;
        color: #000000 !important;
        border-color: #FFD700 !important;
        font-weight: bold;
        border-radius: 8px;
    }
    
    /* สร้างปุ่ม Hero ให้เป็นทรงกล่องจัตุรัส */
    div[data-testid="stButton"] button {
        border-radius: 12px;
        padding: 5px;
        height: 65px; 
    }
    
    /* สไตล์กล่อง Pick/Ban */
    .hero-pick-box {
        background-color: #1E1E1E;
        border: 2px solid #555;
        border-radius: 12px;
        padding: 15px 5px;
        margin-bottom: 10px;
        text-align: center;
        color: white;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    .hero-pick-empty {
        background-color: #000000;
        border: 2px dashed #444;
        border-radius: 12px;
        padding: 15px 5px;
        margin-bottom: 10px;
        text-align: center;
        color: #555;
    }
    .hero-ban-box {
        background-color: #3b1c1c;
        border: 1px solid #ff4444;
        border-radius: 8px;
        padding: 5px;
        margin-bottom: 5px;
        text-align: center;
        color: #ffaaaa;
        font-size: 0.8em;
    }
    .hero-ban-empty {
        background-color: #000000;
        border: 1px dashed #555;
        border-radius: 8px;
        padding: 5px;
        margin-bottom: 5px;
        text-align: center;
        color: #333;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. โหลดข้อมูล & สร้างหน่วยความจำ ---
@st.cache_resource
def load_model():
    return RoVDraftRecommender()

recommender = load_model()
all_heroes = sorted(list(hero_roles.keys()))
roles = ["offlane", "jungle", "midlane", "carry", "roaming"]

if 'my_role' not in st.session_state: st.session_state.my_role = "roaming"
if 'active_zone' not in st.session_state: st.session_state.active_zone = "Pick A" # ค่าเริ่มต้น
if 'team_a_picks' not in st.session_state: st.session_state.team_a_picks = []
if 'team_b_picks' not in st.session_state: st.session_state.team_b_picks = []
if 'team_a_bans' not in st.session_state: st.session_state.team_a_bans = []
if 'team_b_bans' not in st.session_state: st.session_state.team_b_bans = []

def set_role(r): st.session_state.my_role = r
def set_zone(z): st.session_state.active_zone = z 

def add_hero_to_zone(hero):
    zone = st.session_state.active_zone
    if zone == "Ban A" and len(st.session_state.team_a_bans) < 5: st.session_state.team_a_bans.append(hero)
    elif zone == "Ban B" and len(st.session_state.team_b_bans) < 5: st.session_state.team_b_bans.append(hero)
    elif zone == "Pick A" and len(st.session_state.team_a_picks) < 5: st.session_state.team_a_picks.append(hero)
    elif zone == "Pick B" and len(st.session_state.team_b_picks) < 5: st.session_state.team_b_picks.append(hero)

def undo_last():
    zone = st.session_state.active_zone
    if zone == "Ban A" and st.session_state.team_a_bans: st.session_state.team_a_bans.pop()
    elif zone == "Ban B" and st.session_state.team_b_bans: st.session_state.team_b_bans.pop()
    elif zone == "Pick A" and st.session_state.team_a_picks: st.session_state.team_a_picks.pop()
    elif zone == "Pick B" and st.session_state.team_b_picks: st.session_state.team_b_picks.pop()

def reset_all():
    st.session_state.team_a_picks, st.session_state.team_b_picks = [], []
    st.session_state.team_a_bans, st.session_state.team_b_bans = [], []

def render_boxes(hero_list, max_slots, box_type="pick"):
    for i in range(max_slots):
        if i < len(hero_list):
            css = "hero-pick-box" if box_type == "pick" else "hero-ban-box"
            st.markdown(f'<div class="{css}">{hero_list[i].upper()}</div>', unsafe_allow_html=True)
        else:
            css = "hero-pick-empty" if box_type == "pick" else "hero-ban-empty"
            st.markdown(f'<div class="{css}">+</div>', unsafe_allow_html=True)

# --- ฟังก์ชันสำหรับสร้าง Pop-up Prediction ---
@st.dialog("🎯 Prediction Results")
def show_prediction_popup(top3):
    if not top3:
        st.error("ไม่พบข้อมูลฮีโร่ที่แนะนำ หรือโดนเลือกไปหมดแล้ว")
        return
        
    cols = st.columns(3)
    
    # จัดลำดับกล่อง: ซ้าย(อันดับ 2), กลาง(อันดับ 1), ขวา(อันดับ 3)
    if len(top3) >= 3:
        display_order = [top3[1], top3[0], top3[2]]
    elif len(top3) == 2:
        display_order = [top3[1], top3[0], None]
    else:
        display_order = [None, top3[0], None]
        
    for i in range(3):
        with cols[i]:
            if display_order[i]:
                hero = display_order[i]['Hero']
                score = display_order[i]['FinalScore']
                
                # ไฮไลท์สีทองเฉพาะตรงกลาง (อันดับ 1)
                color = "#FFD700" if i == 1 else "#AAAAAA" 
                
                # กล่องฮีโร่ (ใช้ aspect-ratio: 1/1 เพื่อให้เป็นจัตุรัสเสมอ)
                st.markdown(f"""
                    <div style="aspect-ratio: 1/1; background-color: #1E1E1E; border: 2px solid {color}; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.5);">
                        <span style="font-weight: bold; color: white; font-size: 1.1rem;">{hero.upper()[:5]}</span>
                    </div>
                    <p style="text-align: center; font-size: 13px; color: #ccc; margin: 8px 0 0 0;">{hero}</p>
                    <p style="text-align: center; font-weight: bold; font-size: 16px; color: {color}; margin: 0;">{score}%</p>
                """, unsafe_allow_html=True)


# --- 3. วาดหน้าจอ UI ---
st.write("##### เลือกตำแหน่ง")
role_cols = st.columns(5)
for i, r in enumerate(roles):
    btn_type = "primary" if st.session_state.my_role == r else "secondary"
    role_cols[i].button(r.replace("_", " ").upper(), type=btn_type, on_click=set_role, args=(r,), use_container_width=True)

st.divider()

col_left, col_center, col_right = st.columns([1, 2.5, 1], gap="small")

# --- ฝั่งซ้าย TEAM A ---
with col_left:
    st.markdown("<h4 style='text-align: center;'>🔵 My Team</h4>", unsafe_allow_html=True)
    
    st.button("🚫 BANS (คลิกเพื่อเลือก)", type="primary" if st.session_state.active_zone == "Ban A" else "secondary", on_click=set_zone, args=("Ban A",), key="btn_zone_ban_a", use_container_width=True)
    ban_cols = st.columns(5)
    for i in range(5):
        with ban_cols[i]:
            if i < len(st.session_state.team_a_bans):
                st.markdown(f'<div class="hero-ban-box">{st.session_state.team_a_bans[i][:3]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="hero-ban-empty">-</div>', unsafe_allow_html=True)
    
    st.write("") 
    
    st.button("PICKS (คลิกเพื่อเลือก)", type="primary" if st.session_state.active_zone == "Pick A" else "secondary", on_click=set_zone, args=("Pick A",), key="btn_zone_pick_a", use_container_width=True)
    render_boxes(st.session_state.team_a_picks, 5, "pick")

# --- ฝั่งขวา TEAM B ---
with col_right:
    st.markdown("<h4 style='text-align: center;'>🔴 Opponent Team</h4>", unsafe_allow_html=True)
    
    st.button("🚫 BANS (คลิกเพื่อเลือก)", type="primary" if st.session_state.active_zone == "Ban B" else "secondary", on_click=set_zone, args=("Ban B",), key="btn_zone_ban_b", use_container_width=True)
    ban_cols = st.columns(5)
    for i in range(5):
        with ban_cols[i]:
            if i < len(st.session_state.team_b_bans):
                st.markdown(f'<div class="hero-ban-box">{st.session_state.team_b_bans[i][:3]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="hero-ban-empty">-</div>', unsafe_allow_html=True)
                
    st.write("")
    
    st.button("PICKS (คลิกเพื่อเลือก)", type="primary" if st.session_state.active_zone == "Pick B" else "secondary", on_click=set_zone, args=("Pick B",), key="btn_zone_pick_b", use_container_width=True)
    render_boxes(st.session_state.team_b_picks, 5, "pick")

# --- ตรงกลาง HERO POOL ---
with col_center:
    search_q = st.text_input("Hero Pool", placeholder="Searching ...")
    used_heroes = set(st.session_state.team_a_picks + st.session_state.team_b_picks + st.session_state.team_a_bans + st.session_state.team_b_bans)
    filtered_heroes = [h for h in all_heroes if search_q.lower() in h.lower()]
    
    pool_container = st.container(height=450, border=True)
    with pool_container:
        pool_cols = st.columns(4)
        for idx, hero in enumerate(filtered_heroes):
            is_disabled = hero in used_heroes
            with pool_cols[idx % 4]:
                st.button(
                    hero.upper()[:5], 
                    key=f"btn_{hero}", 
                    disabled=is_disabled, 
                    on_click=add_hero_to_zone, 
                    args=(hero,),
                    use_container_width=True
                )
                st.markdown(f"<p style='text-align: center; font-size: 11px; margin-top: -15px; margin-bottom: 10px; color: #888;'>{hero}</p>", unsafe_allow_html=True)

st.divider()

# --- 4. แถบเครื่องมือด้านล่างสุด ---
sp1, btn1, btn2, btn3, sp2 = st.columns([1.5, 1, 1, 1, 1.5])

with btn1:
    st.button("Reset All", on_click=reset_all, use_container_width=True)
with btn2:
    run_predict = st.button("🔮 Predict", type="primary", use_container_width=True)
with btn3:
    st.button("Undo", on_click=undo_last, use_container_width=True)

# --- เรียกใช้ Pop-up ทำนาย ---
if run_predict:
    allies = st.session_state.team_a_picks
    enemies = st.session_state.team_b_picks
    bans = st.session_state.team_a_bans + st.session_state.team_b_bans
    
    with st.spinner('🤖 กำลังประมวลผล...'):
        top3 = recommender.recommend(st.session_state.my_role, allies, enemies, {}, bans)
        show_prediction_popup(top3)