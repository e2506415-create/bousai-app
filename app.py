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

# CSS（画像のデザインをCSS/SVGで完全再現）
st.markdown("""
    <style>
    /* 全体背景 */
    .stApp {
        background-color: #F2F7F9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* サイドバー背景とイラスト演出 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E6F3F7 0%, #D8EBF2 60%, #CCE3ED 100%) !important;
        border-right: 1px solid #C5DFEC;
    }
    
    /* 左上ロゴエリア */
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    .sidebar-logo-icon {
        background-color: #00A86B;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 26px;
        box-shadow: 0 4px 10px rgba(0, 168, 107, 0.25);
    }
    .sidebar-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #1E293B;
        line-height: 1.1;
    }
    .sidebar-sub {
        font-size: 0.72rem;
        color: #64748B;
        font-weight: bold;
        margin-top: 2px;
    }
    
    /* サイドバー下の吹き出しメッセージ */
    .sidebar-msg-box {
        margin-top: 50px;
        background-color: #FFFFFF;
        border: 2px dashed #38BDF8;
        border-radius: 20px;
        padding: 14px;
        text-align: center;
        color: #0284C7;
        font-size: 0.85rem;
        font-weight: bold;
        line-height: 1.4;
        position: relative;
    }
    
    /* メインヘッダーバナー（水色背景・街並みイラスト装飾） */
    .main-banner {
        background: linear-gradient(180deg, #E0F2FE 0%, #BAE6FD 100%);
        border-radius: 24px;
        padding: 24px 20px;
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid #FFFFFF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        position: relative;
        overflow: hidden;
    }
    .main-banner-title {
        color: #E11D48;
        font-size: 1.35rem;
        font-weight: 900;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-bottom: 4px;
    }
    .main-banner-sub {
        color: #1E293B;
        font-size: 1.15rem;
        font-weight: 900;
    }
    
    /* メイン最寄りカード（ピンクグラデーション枠） */
    .pink-result-card {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #FFD1DC;
        box-shadow: 0 6px 18px rgba(255, 182, 193, 0.2);
        height: 100%;
        position: relative;
    }
    .pink-badge {
        color: #334155;
        font-size: 0.95rem;
        font-weight: bold;
    }
    .pink-guide {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: bold;
        margin-top: 4px;
    }
    .dest-flex {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 16px 0;
    }
    .dest-icon-green {
        background-color: #00A86B;
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .dest-name-green {
        font-size: 1.55rem;
        font-weight: 900;
        color: #00A86B;
    }
    .dest-sub-green {
        font-size: 0.95rem;
        color: #00A86B;
        font-weight: bold;
    }
    .green-pill-badge {
        background-color: #E6F4EA;
        color: #137333;
        padding: 8px 18px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 0.88rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .pink-circle-btn {
        position: absolute;
        right: 20px;
        top: 45%;
        background-color: #FF477E;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    
    /* アドバイスカード（黄色枠） */
    .yellow-advice-card {
        background: #FFFDF0;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #FDE68A;
        box-shadow: 0 6px 18px rgba(253, 230, 138, 0.25);
        height: 100%;
    }
    .yellow-title {
        color: #D97706;
        font-weight: 900;
        font-size: 1.15rem;
        margin-bottom: 14px;
    }
    .yellow-item {
        font-size: 0.88rem;
        margin-bottom: 10px;
        color: #334155;
        line-height: 1.5;
    }
    
    /* 地図タイトル */
    .map-title-green {
        font-size: 1.25rem;
        font-weight: 900;
        color: #00A86B;
        margin: 22px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* 緊急連絡先（電話番号エリア） */
    .contact-card {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 18px 22px;
        border: 2px solid #E2E8F0;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .contact-title {
        text-align: center;
        font-weight: 900;
        font-size: 1.05rem;
        color: #1E293B;
        margin-bottom: 12px;
    }
    .contact-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px;
        text-align: center;
    }
    .contact-box {
        background: #F8FAFC;
        padding: 10px 8px;
        border-radius: 14px;
        border: 1px solid #F1F5F9;
    }
    .contact-label {
        font-size: 0.75rem;
        color: #64748B;
        font-weight: bold;
    }
    .contact-number {
        font-size: 1.35rem;
        font-weight: 900;
        color: #E11D48;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. サイドバー表示（完全再現）
# ---------------------------------------------------------
st.sidebar.markdown("""
<div class="sidebar-header">
    <div class="sidebar-logo-icon">🏃‍♂️</div>
    <div>
        <div class="sidebar-title">防災ナビ</div>
        <div class="sidebar-sub">いざという時に、<br>あなたのそばに</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("#### 📍 いまどこにいる？")
st.sidebar.caption("住所や建物名を入力してね")
user_address = st.sidebar.text_input("現在地入力", value="八王子市丹木町1丁目", label_visibility="collapsed")

st.sidebar.markdown("""
<div class="sidebar-msg-box">
    もしもの時も<br>一緒に考えよう！ ＼
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 住所・距離計算ロジック
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

# 避難所リスト
SHELTERS = [
    {"name": "創価大学 グラウンド", "sub": "（構内一次避難場所）", "coords": [35.6870, 139.3285]},
    {"name": "加住小・中学校", "sub": "（指定避難所）", "coords": [35.6828, 139.3361]},
    {"name": "第一小学校", "sub": "（八王子駅北口側）", "coords": [35.6590, 139.3390]},
    {"name": "第四小学校", "sub": "（明神町エリア）", "coords": [35.6552, 139.3465]},
    {"name": "楢原小学校", "sub": "（楢原町エリア）", "coords": [35.6805, 139.3030]}
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
# 上部バナー
st.markdown("""
<div class="main-banner">
    <div class="main-banner-title">📢 八王子市 避難ルートナビ 🌈</div>
    <div class="main-banner-sub">〜 現在地を入れるだけ！一番近くて安全な避難所へ即案内 〜</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.25, 0.75])

with col1:
    st.markdown(f"""
    <div class="pink-result-card">
        <div class="pink-badge">📍 現在地：{user_address}</div>
        <div class="pink-guide">✨ 向かうべき最寄りの避難所はこちら！</div>
        <div class="dest-flex">
            <div class="dest-icon-green">🏫</div>
            <div>
                <span class="dest-name-green">{nearest_shelter['name']}</span>
                <span class="dest-sub-green">{nearest_shelter['sub']}</span>
            </div>
        </div>
        <div>
            <span class="green-pill-badge">🏃 距離：約 {min_distance:.1f} km / 徒歩約 {walk_minutes} 分</span>
        </div>
        <div class="pink-circle-btn">❯</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="yellow-advice-card">
        <div class="yellow-title">💡 移動時のワンポイント ✨</div>
        <div class="yellow-item">👟 <b>履物</b>：増水時の長靴は危険！スニーカーで。</div>
        <div class="yellow-item">🎒 <b>荷物</b>：両手が空くようにリュックで移動。</div>
        <div class="yellow-item">⚠️ <b>移動</b>：水で隠れた側溝や傾斜地に注意！</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="map-title-green">🏛️ 安全おすすめ避難ルートマップ</div>', unsafe_allow_html=True)

# 地図
m = folium.Map(location=current_coords, zoom_start=15, tiles="OpenStreetMap")

# 現在地ピン
folium.Marker(
    location=current_coords,
    popup=f"📍 現在地: {user_address}",
    tooltip="現在地",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

# 最寄り避難所ピン
folium.Marker(
    location=nearest_shelter["coords"],
    popup=f"🏠 {nearest_shelter['name']}",
    tooltip=nearest_shelter['name'],
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# 避難ルート破線（緑）
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

st_folium(m, width="100%", height=420)

# ---------------------------------------------------------
# 5. 緊急連絡先・ダイヤル（復元）
# ---------------------------------------------------------
st.markdown("""
<div class="contact-card">
    <div class="contact-title">📞 緊急連絡先＆通報ダイヤル</div>
    <div class="contact-grid">
        <div class="contact-box">
            <div class="contact-label">火災・救急・救助</div>
            <div class="contact-number">119 番</div>
        </div>
        <div class="contact-box">
            <div class="contact-label">警察（事件・事故）</div>
            <div class="contact-number" style="color:#0284C7;">110 番</div>
        </div>
        <div class="contact-box">
            <div class="contact-label">災害用伝言ダイヤル</div>
            <div class="contact-number" style="color:#0D9488;">171 番</div>
        </div>
        <div class="contact-box">
            <div class="contact-label">八王子市役所 (代表)</div>
            <div style="font-weight:900; font-size:1.0rem; color:#334155; margin-top:4px;">042-620-7111</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
