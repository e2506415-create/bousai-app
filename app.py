import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request
import math

# ---------------------------------------------------------
# 1. ページ基本設定
# ---------------------------------------------------------
st.set_page_config(page_title="防災ナビ 避難ルートマップ", page_icon="🏃‍♂️", layout="wide")

# 完全再現CSS
st.markdown("""
    <style>
    /* 全体背景（ペールブルーグラデーション） */
    .stApp {
        background: linear-gradient(180deg, #E6F3F9 0%, #F4F9FB 100%);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* サイドバー背景 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E8F4F8 0%, #E2F0F6 100%) !important;
        border-right: 1px solid #D1E5EE;
    }
    
    /* サイドバーヘッダー */
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }
    .sidebar-logo {
        background-color: #00A86B;
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 28px;
        box-shadow: 0 4px 10px rgba(0,168,107,0.2);
    }
    .sidebar-title-text {
        font-size: 1.7rem;
        font-weight: 900;
        color: #1E293B;
        line-height: 1.1;
    }
    .sidebar-sub-text {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 3px;
        font-weight: bold;
    }
    
    /* サイドバー吹き出し */
    .sidebar-footer-msg {
        margin-top: 60px;
        background-color: #FFFFFF;
        border: 2px dashed #7DD3FC;
        border-radius: 20px;
        padding: 16px;
        text-align: center;
        color: #0284C7;
        font-size: 0.85rem;
        font-weight: bold;
        line-height: 1.4;
    }
    
    /* メインヘッダーバナー */
    .main-header-banner {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 50%, #E0F2FE 100%);
        border-radius: 24px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        border: 2px solid #FFFFFF;
    }
    .main-header-title {
        color: #FF3B30;
        font-size: 1.4rem;
        font-weight: 900;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    .main-header-sub {
        color: #334155;
        font-size: 1.05rem;
        font-weight: 800;
    }
    
    /* メイン結果カード (ピンク枠グラデーション) */
    .result-card-container {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 24px;
        border: 3px solid #FFD1DC;
        box-shadow: 0 8px 20px rgba(255, 182, 193, 0.15);
        position: relative;
        height: 100%;
    }
    .result-loc-tag {
        color: #475569;
        font-size: 0.95rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .result-guide-text {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: bold;
        margin-top: 6px;
    }
    .result-target-box {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 16px 0;
    }
    .result-target-icon {
        background-color: #00A86B;
        color: white;
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        flex-shrink: 0;
    }
    .result-target-name {
        font-size: 1.6rem;
        font-weight: 900;
        color: #00A86B;
    }
    .result-target-sub {
        font-size: 1.0rem;
        color: #00A86B;
        font-weight: bold;
        margin-left: 6px;
    }
    .result-info-pill {
        background-color: #E6F4EA;
        color: #137333;
        padding: 8px 18px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    /* ワンポイントカード (黄色枠) */
    .advice-card-container {
        background: #FFFDF0;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #FDE68A;
        box-shadow: 0 8px 20px rgba(253, 230, 138, 0.2);
        height: 100%;
    }
    .advice-card-title {
        color: #D97706;
        font-weight: 900;
        font-size: 1.15rem;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .advice-card-item {
        font-size: 0.9rem;
        margin-bottom: 12px;
        color: #334155;
        line-height: 1.5;
        display: flex;
        align-items: baseline;
        gap: 8px;
    }
    
    /* 地図ヘッダー */
    .map-section-title {
        font-size: 1.3rem;
        font-weight: 900;
        color: #00A86B;
        margin: 24px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. サイドバー
# ---------------------------------------------------------
st.sidebar.markdown("""
<div class="sidebar-header">
    <div class="sidebar-logo">🏃‍♂️</div>
    <div>
        <div class="sidebar-title-text">防災ナビ</div>
        <div class="sidebar-sub-text">いざという時に、<br>あなたのそばに</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("#### 📍 いまどこにいる？")
st.sidebar.caption("住所や建物名を入力してね")
user_address = st.sidebar.text_input("現在地入力欄", value="八王子市丹木町1丁目", label_visibility="collapsed")

st.sidebar.markdown("""
<div class="sidebar-footer-msg">
    もしもの時も<br>一緒に考えよう！ ＼
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 座標計算ロジック
# ---------------------------------------------------------
def get_coords_from_address(address_text):
    default_coords = [35.6881, 139.3275]
    if not address_text:
        return default_coords
    try:
        search_query = address_text
        if "八王子" not in search_query:
            search_query = "東京都八王子市 " + search_query
        url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" + urllib.parse.quote(search_query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and len(data) > 0:
                lon, lat = data[0]['geometry']['coordinates']
                return [lat, lon]
    except Exception:
        pass
    return default_coords

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

current_coords = get_coords_from_address(user_address)

# 避難所データ
SHELTERS = [
    {"name": "創価大学 グラウンド", "sub": "(構内一次避難場所)", "coords": [35.6870, 139.3285]},
    {"name": "加住小・中学校", "sub": "(指定避難所)", "coords": [35.6828, 139.3361]},
    {"name": "第一小学校", "sub": "(八王子駅北口側)", "coords": [35.6590, 139.3390]},
    {"name": "第四小学校", "sub": "(明神町エリア)", "coords": [35.6552, 139.3465]},
    {"name": "楢原小学校", "sub": "(楢原町エリア)", "coords": [35.6805, 139.3030]}
]

nearest_shelter = None
min_distance = float('inf')

for shelter in SHELTERS:
    dist = calculate_distance(current_coords[0], current_coords[1], shelter["coords"][0], shelter["coords"][1])
    if dist < min_distance:
        min_distance = dist
        nearest_shelter = shelter

walk_minutes = math.ceil((min_distance / 4.0) * 60)

# ---------------------------------------------------------
# 4. メイン表示エリア
# ---------------------------------------------------------
st.markdown("""
<div class="main-header-banner">
    <div class="main-header-title">📢 八王子市 避難ルートナビ 🌈</div>
    <div class="main-header-sub">〜 現在地を入れるだけ！一番近くて安全な避難所へ即案内 〜</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.25, 0.75])

with col1:
    st.markdown(f"""
    <div class="result-card-container">
        <div class="result-loc-tag">📍 現在地：{user_address}</div>
        <div class="result-guide-text">✨ 向かうべき最寄りの避難所はこちら！</div>
        <div class="result-target-box">
            <div class="result-target-icon">🏫</div>
            <div>
                <span class="result-target-name">{nearest_shelter['name']}</span>
                <span class="result-target-sub">{nearest_shelter['sub']}</span>
            </div>
        </div>
        <div>
            <span class="result-info-pill">🏃 距離：約 {min_distance:.1f} km / 徒歩約 {walk_minutes} 分</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="advice-card-container">
        <div class="advice-card-title">💡 移動時のワンポイント ✨</div>
        <div class="advice-card-item">👟 <span><b>履物</b>：増水時の長靴は危険！スニーカーで。</span></div>
        <div class="advice-card-item">🎒 <span><b>荷物</b>：両手が空くようにリュックで移動。</span></div>
        <div class="advice-card-item">⚠️ <span><b>移動</b>：水で隠れた側溝や傾斜地に注意！</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="map-section-title">🏛️ 安全おすすめ避難ルートマップ</div>', unsafe_allow_html=True)

# 地図表示
m = folium.Map(location=current_coords, zoom_start=15, tiles="OpenStreetMap")

# 現在地ピン（赤）
folium.Marker(
    location=current_coords,
    popup=f"📍 現在地: {user_address}",
    tooltip="現在地",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

# 避難所ピン（緑）
folium.Marker(
    location=nearest_shelter["coords"],
    popup=f"🏠 {nearest_shelter['name']}",
    tooltip=nearest_shelter['name'],
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# ルート点線（緑）
route_coords = [
    current_coords,
    [(current_coords[0] + nearest_shelter["coords"][0])/2 + 0.0005,
     (current_coords[1] + nearest_shelter["coords"][1])/2 - 0.0005],
    nearest_shelter["coords"]
]

folium.PolyLine(
    locations=route_coords,
    color="#00A86B",
    weight=5,
    opacity=0.8,
    dash_array="6, 6",
    tooltip="避難ルート"
).add_to(m)

st_folium(m, width="100%", height=430)
