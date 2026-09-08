import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request
import math

# ---------------------------------------------------------
# 1. ページ基本設定（Webサイト風レイアウト）
# ---------------------------------------------------------
st.set_page_config(page_title="防災ナビ 避難ルートマップ", page_icon="🏃‍♂️", layout="wide")

# カスタムCSS（本格Webサイト/LP風デザイン）
st.markdown("""
    <style>
    /* 全体背景 */
    .stApp {
        background: linear-gradient(180deg, #EBF5F8 0%, #F7FAFC 100%);
        font-family: 'Hiragino Maru Gothic ProN', 'Rounded Mplus 1c', 'Yu Gothic', sans-serif;
    }
    
    /* サイドバーのWebサイト風カスタマイズ */
    [data-testid="stSidebar"] {
        background-color: #EBF5F8 !important;
        border-right: 1px solid #D0E3EA;
    }
    
    /* 画面上部 ヘッダーバナー */
    .site-header {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        border-radius: 24px;
        padding: 25px 30px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(186, 230, 253, 0.4);
        margin-bottom: 25px;
        position: relative;
        border: 2px solid #FFFFFF;
    }
    .site-title {
        color: #E11D48;
        font-size: 2.0rem;
        font-weight: 900;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    .site-subtitle {
        color: #334155;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 8px;
    }
    
    /* メイン結果カード (創価大学等) */
    .result-card {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        border: 2px solid #FFD1DC;
        margin-bottom: 20px;
    }
    .result-badge {
        color: #64748B;
        font-size: 0.9rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .destination-box {
        display: flex;
        align-items: center;
        gap: 15px;
        margin: 15px 0;
    }
    .dest-icon {
        background-color: #0D9488;
        color: white;
        width: 55px;
        height: 55px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        font-weight: bold;
        flex-shrink: 0;
    }
    .dest-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0F172A;
    }
    .route-pill {
        background-color: #ECFDF5;
        color: #047857;
        padding: 8px 18px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        font-size: 0.95rem;
        border: 1px solid #A7F3D0;
    }
    
    /* 右側：ワンポイントカード */
    .advice-card {
        background: #FFFBEB;
        border-radius: 24px;
        padding: 22px;
        border: 2px solid #FDE68A;
        box-shadow: 0 8px 20px rgba(251, 191, 36, 0.08);
    }
    .advice-header {
        color: #D97706;
        font-weight: 800;
        font-size: 1.15rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .advice-item {
        font-size: 0.92rem;
        margin-bottom: 10px;
        color: #451A03;
        line-height: 1.6;
    }
    
    /* 地図枠デザイン */
    .map-header {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F172A;
        margin: 20px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* 下部：緊急連絡先カード */
    .contact-card {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
        border: 1.5px solid #E2E8F0;
        margin-top: 30px;
    }
    .contact-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }
    .contact-item {
        background: #F8FAFC;
        padding: 15px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #F1F5F9;
    }
    .contact-num {
        font-size: 1.3rem;
        font-weight: 800;
        color: #E11D48;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Webサイト風トップヘッダー
st.markdown("""
<div class="site-header">
    <div class="site-title">📍 八王子市 避難ルートナビ 避難ルートマップ 🚩</div>
    <div class="site-subtitle">〜 現在地を入れるだけ！一番近くて安全な避難所へ即案内 〜</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 住所座標変換 & 2点間距離計算
# ---------------------------------------------------------
def get_coords_from_address(address_text):
    default_coords = [35.6881, 139.3275] # 創価大付近
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

# ---------------------------------------------------------
# 3. 避難所＆危険エリアデータ
# ---------------------------------------------------------
SHELTERS = [
    {"name": "創価大学 グラウンド（構内一次避難場所）", "coords": [35.6870, 139.3285], "icon": "🏫"},
    {"name": "加住小・中学校（指定避難所）", "coords": [35.6828, 139.3361], "icon": "🏫"},
    {"name": "第一小学校（八王子駅北口側）", "coords": [35.6590, 139.3390], "icon": "🏫"},
    {"name": "第四小学校（明神町エリア）", "coords": [35.6552, 139.3465], "icon": "🏫"},
    {"name": "楢原小学校（楢原町エリア）", "coords": [35.6805, 139.3030], "icon": "🏫"}
]

HAZARD_ZONES = [
    {"name": "🍓 丹木町東側 斜面注意エリア", "coords": [35.6885, 139.3300], "radius": 130, "color": "#FF6B6B", "desc": "【土砂崩れ警戒】大雨時は近づかず、高台へ！"},
    {"name": "🍊 ひよどり山北側 冠水注意エリア", "coords": [35.6830, 139.3240], "radius": 110, "color": "#FFD93D", "desc": "【水たまり冠水】アンダーパスや低い道は避けて！"}
]

# ---------------------------------------------------------
# 4. サイドバー
# ---------------------------------------------------------
st.sidebar.markdown("### 🏃‍♂️ 防災ナビ")
st.sidebar.markdown("<p style='font-size:0.85rem; color:#64748B;'>いざという時に、あなたのそばに</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📍 いまどこにいる？")
user_address = st.sidebar.text_input("住所や建物名を入力してね", value="八王子市丹木町1丁目")

current_coords = get_coords_from_address(user_address)

# ---------------------------------------------------------
# 5. 最寄り避難所の自動判別
# ---------------------------------------------------------
nearest_shelter = None
min_distance = float('inf')

for shelter in SHELTERS:
    dist = calculate_distance(current_coords[0], current_coords[1], shelter["coords"][0], shelter["coords"][1])
    if dist < min_distance:
        min_distance = dist
        nearest_shelter = shelter

walk_minutes = math.ceil((min_distance / 4.0) * 60)

# ---------------------------------------------------------
# 6. メインコンテンツ
# ---------------------------------------------------------
col1, col2 = st.columns([1.3, 0.7])

with col1:
    st.markdown(f"""
    <div class="result-card">
        <div class="result-badge">📍 現在地：{user_address}</div>
        <div style="font-size:0.85rem; color:#E11D48; font-weight:bold; margin-top:6px;">🏃 向かうべき最寄りの避難所はこちら！</div>
        <div class="destination-box">
            <div class="dest-icon">金</div>
            <div class="dest-title">{nearest_shelter['name']}</div>
        </div>
        <div>
            <span class="route-pill">🏃 距離：約 {min_distance:.1f} km ／ 徒歩約 {walk_minutes} 分</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="advice-card">
        <div class="advice-header">💡 移動時のワンポイント</div>
        <div class="advice-item"><b>👟 履物</b>：増水時の長靴は危険！スニーカーで。</div>
        <div class="advice-item"><b>🎒 荷物</b>：両手が空くようにリュックで移動。</div>
        <div class="advice-item"><b>⚠️ 移動</b>：水で隠れた側溝や傾斜地に注意！</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="map-header">🗺️ 安全おすすめ避難ルートマップ</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 地図描画
# ---------------------------------------------------------
m = folium.Map(location=current_coords, zoom_start=15)

# 現在地ピン
folium.Marker(
    location=current_coords,
    popup=f"📍 現在地: {user_address}",
    tooltip="いまここにいます！",
    icon=folium.Icon(color="red", icon="user", prefix="fa")
).add_to(m)

# 最寄り避難所ピン
folium.Marker(
    location=nearest_shelter["coords"],
    popup=f"🏠 最寄り避難所: {nearest_shelter['name']}",
    tooltip="目指す避難所！",
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# その他避難所ピン
for shelter in SHELTERS:
    if shelter["name"] != nearest_shelter["name"]:
        folium.Marker(
            location=shelter["coords"],
            popup=f"🏫 {shelter['name']}",
            tooltip="その他の避難所",
            icon=folium.Icon(color="gray", icon="info-sign")
        ).add_to(m)

# 危険エリア
for zone in HAZARD_ZONES:
    folium.Circle(
        location=zone["coords"],
        radius=zone["radius"],
        color=zone["color"],
        fill=True,
        fill_color=zone["color"],
        fill_opacity=0.35,
        popup=f"{zone['name']}\n{zone['desc']}"
    ).add_to(m)

# ルート線
route_coords = [
    current_coords,
    [(current_coords[0] + nearest_shelter["coords"][0])/2 + 0.0006,
     (current_coords[1] + nearest_shelter["coords"][1])/2 - 0.0006],
    nearest_shelter["coords"]
]

folium.PolyLine(
    locations=route_coords,
    color="#0284C7",
    weight=7,
    opacity=0.8,
    dash_array="10, 10",
    tooltip="安全ルート"
).add_to(m)

st_folium(m, width="100%", height=460)

# ---------------------------------------------------------
# 8. 緊急連絡先
# ---------------------------------------------------------
st.markdown("""
<div class="contact-card">
    <div style="text-align:center; font-weight:800; font-size:1.1rem; color:#0F172A;">📞 緊急連絡先＆ダイヤル</div>
    <div class="contact-grid">
        <div class="contact-item">
            <div style="font-size:0.8rem; color:#64748B;">火災・救急・救助</div>
            <div class="contact-num">119 番</div>
        </div>
        <div class="contact-item">
            <div style="font-size:0.8rem; color:#64748B;">警察（事件・事故）</div>
            <div class="contact-num" style="color:#0284C7;">110 番</div>
        </div>
        <div class="contact-item">
            <div style="font-size:0.8rem; color:#64748B;">災害用伝言ダイヤル</div>
            <div class="contact-num" style="color:#0D9488;">171 番</div>
        </div>
        <div class="contact-item">
            <div style="font-size:0.8rem; color:#64748B;">八王子市役所 (代表)</div>
            <div style="font-weight:800; font-size:1.0rem; margin-top:5px; color:#334155;">042-620-7111</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
