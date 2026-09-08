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

# 画像デザイン完全再現CSS
st.markdown("""
    <style>
    /* 全体背景（パステルブルーのグラデーション） */
    .stApp {
        background: linear-gradient(180deg, #E2F2F8 0%, #F4F9FB 100%);
        font-family: 'Hiragino Maru Gothic ProN', 'Rounded Mplus 1c', 'Yu Gothic', sans-serif;
    }
    
    /* サイドバー背景 */
    [data-testid="stSidebar"] {
        background-color: #EAF4F8 !important;
        border-right: 1px solid #D5E6ED;
    }
    
    /* 左上ロゴエリア (大きな緑の走る人ピクトグラム) */
    .sidebar-logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .runner-logo-icon {
        width: 46px;
        height: 46px;
        background-color: #00A86B;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(0, 168, 107, 0.25);
    }
    .logo-text-main {
        font-size: 1.6rem;
        font-weight: 900;
        color: #1E293B;
        line-height: 1.1;
    }
    .logo-text-sub {
        font-size: 0.7rem;
        color: #64748B;
        margin-top: 3px;
        line-height: 1.2;
    }
    
    /* サイドバー吹き出し */
    .sidebar-msg-box {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 14px;
        text-align: center;
        border: 1.5px dashed #38BDF8;
        margin-top: 40px;
        font-size: 0.85rem;
        color: #0284C7;
        font-weight: bold;
        position: relative;
    }
    
    /* メインヘッダーバナー */
    .header-banner {
        background: #E0F2FE;
        border-radius: 18px;
        padding: 16px 20px;
        text-align: center;
        margin-bottom: 18px;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .header-title {
        color: #E11D48;
        font-size: 1.35rem;
        font-weight: 900;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    .header-subtitle {
        color: #334155;
        font-size: 0.95rem;
        font-weight: 800;
        margin-top: 4px;
    }
    
    /* メイン結果カード（ピンク枠） */
    .result-card {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
        border: 2.5px solid #FFD1DC;
        height: 100%;
    }
    .result-badge {
        color: #475569;
        font-size: 0.88rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .result-subhead {
        color: #94A3B8;
        font-size: 0.8rem;
        font-weight: bold;
        margin-top: 6px;
    }
    .destination-box {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 12px 0 16px 0;
    }
    .dest-icon {
        background-color: #00A86B;
        color: white;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        font-weight: bold;
        flex-shrink: 0;
    }
    .dest-title {
        font-size: 1.45rem;
        font-weight: 900;
        color: #1E293B;
        line-height: 1.2;
    }
    .dest-sub {
        font-size: 0.85rem;
        color: #00A86B;
        font-weight: bold;
    }
    .route-pill {
        background-color: #ECFDF5;
        color: #047857;
        padding: 6px 16px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.85rem;
        border: 1px solid #A7F3D0;
    }
    
    /* アドバイスカード（黄色枠） */
    .advice-card {
        background: #FFFBEB;
        border-radius: 20px;
        padding: 18px 20px;
        border: 2.5px solid #FDE68A;
        height: 100%;
    }
    .advice-header {
        color: #D97706;
        font-weight: 900;
        font-size: 1.05rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .advice-item {
        font-size: 0.85rem;
        margin-bottom: 10px;
        color: #451A03;
        line-height: 1.5;
        display: flex;
        align-items: baseline;
        gap: 6px;
    }
    
    /* 地図ヘッダー */
    .map-header {
        font-size: 1.2rem;
        font-weight: 900;
        color: #1E293B;
        margin: 20px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. サイドバー（緑の走る人ロゴ＆現在地入力）
# ---------------------------------------------------------
RUNNER_SVG = """
<svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M13.5 5.5C14.6046 5.5 15.5 4.60457 15.5 3.5C15.5 2.39543 14.6046 1.5 13.5 1.5C12.3954 1.5 11.5 2.39543 11.5 3.5C11.5 4.60457 12.3954 5.5 13.5 5.5Z" fill="white"/>
    <path d="M19.5 9.5L15 7.5L11.5 11L13.5 15L17.5 13.5V18.5H19.5V12.5L16.5 14L15 10.5L17 9.5H19.5V9.5Z" fill="white"/>
    <path d="M9.5 8.5L6.5 12.5H9.5L10.5 17.5L6.5 22.5H4.5L8 18L7 13.5L4 15.5V18.5H2V14.5L6.5 11.5L8 8.5H9.5Z" fill="white"/>
</svg>
"""

st.sidebar.markdown(f"""
<div class="sidebar-logo-container">
    <div class="runner-logo-icon">
        {RUNNER_SVG}
    </div>
    <div>
        <div class="logo-text-main">防災ナビ</div>
        <div class="logo-text-sub">いざという時に、<br>あなたのそばに</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("#### 📍 いまどこにいる？")
st.sidebar.caption("住所や建物名を入力してね")
user_address = st.sidebar.text_input("", value="八王子市丹木町1丁目", label_visibility="collapsed")

st.sidebar.markdown("""
<div class="sidebar-msg-box">
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
    {"name": "創価大学 グラウンド", "sub": "（構内一次避難場所）", "coords": [35.6870, 139.3285], "icon_label": "金"},
    {"name": "加住小・中学校", "sub": "（指定避難所）", "coords": [35.6828, 139.3361], "icon_label": "校"},
    {"name": "第一小学校", "sub": "（八王子駅北口側）", "coords": [35.6590, 139.3390], "icon_label": "校"},
    {"name": "第四小学校", "sub": "（明神町エリア）", "coords": [35.6552, 139.3465], "icon_label": "校"},
    {"name": "楢原小学校", "sub": "（楢原町エリア）", "coords": [35.6805, 139.3030], "icon_label": "校"}
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
# 4. メイン表示エリア（画像を完全に模倣）
# ---------------------------------------------------------
# ヘッダーバナー
st.markdown("""
<div class="header-banner">
    <div class="header-title">🌸 八王子市 避難ルートナビ 🥖</div>
    <div class="header-subtitle">〜 現在地を入れるだけ！一番近くて安全な避難所へ即案内 〜</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 0.8])

with col1:
    st.markdown(f"""
    <div class="result-card">
        <div class="result-badge">📍 現在地：{user_address}</div>
        <div class="result-subhead">向かうべき最寄りの避難所はこちら！</div>
        <div class="destination-box">
            <div class="dest-icon">{nearest_shelter.get('icon_label', '金')}</div>
            <div>
                <span class="dest-title">{nearest_shelter['name']}</span>
                <span class="dest-sub">{nearest_shelter['sub']}</span>
            </div>
        </div>
        <div>
            <span class="route-pill">🏃 距離：約 {min_distance:.1f} km / 徒歩約 {walk_minutes} 分</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="advice-card">
        <div class="advice-header">🟡 移動時のワンポイント 🥖</div>
        <div class="advice-item">👟 <span><b>履物</b>：増水時の長靴は危険！スニーカーで。</span></div>
        <div class="advice-item">🎒 <span><b>荷物</b>：両手が空くようにリュックで移動。</span></div>
        <div class="advice-item">⚠️ <span><b>移動</b>：水で隠れた側溝や傾斜地に注意！</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="map-header">🏛️ 安全おすすめ避難ルートマップ</div>', unsafe_allow_html=True)

# Folium地図の作成
m = folium.Map(location=current_coords, zoom_start=15, tiles="OpenStreetMap")

# 現在地（赤ピン）
folium.Marker(
    location=current_coords,
    popup=f"📍 現在地: {user_address}",
    tooltip="現在地",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

# 最寄り避難所（緑ピン）
folium.Marker(
    location=nearest_shelter["coords"],
    popup=f"🏠 {nearest_shelter['name']}",
    tooltip=nearest_shelter['name'],
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# ルート点線（青）
route_coords = [
    current_coords,
    [(current_coords[0] + nearest_shelter["coords"][0])/2 + 0.0005,
     (current_coords[1] + nearest_shelter["coords"][1])/2 - 0.0005],
    nearest_shelter["coords"]
]

folium.PolyLine(
    locations=route_coords,
    color="#0284C7",
    weight=5,
    opacity=0.8,
    dash_array="6, 6",
    tooltip="安全避難ルート"
).add_to(m)

st_folium(m, width="100%", height=420)
