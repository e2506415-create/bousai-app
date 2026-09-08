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

# デザイン完全再現CSS
st.markdown("""
    <style>
    /* 全体背景 */
    .stApp {
        background: #F4F9FB;
        font-family: -apple-system, BlinkMacSystemFont, "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
    }
    
    /* サイドバー */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E6F3F7 0%, #DCEDF5 50%, #CDE3EE 100%) !important;
        border-right: 1px solid #C4DFEC;
    }
    
    /* 左上ロゴエリア */
    .sidebar-logo-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .runner-circle-icon {
        background-color: #00A86B;
        width: 58px;
        height: 58px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 14px rgba(0, 168, 107, 0.3);
        flex-shrink: 0;
    }
    .sidebar-logo-title {
        font-size: 1.7rem;
        font-weight: 900;
        color: #1E293B;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    .sidebar-logo-sub {
        font-size: 0.75rem;
        color: #64748B;
        font-weight: bold;
        margin-top: 2px;
        line-height: 1.2;
    }
    
    /* サイドバー下の街並みイラスト＆吹き出し */
    .sidebar-town-bg {
        margin-top: 40px;
        background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.6) 100%);
        border-radius: 20px;
        padding: 15px;
        text-align: center;
    }
    .sidebar-msg-bubble {
        background-color: #FFFFFF;
        border: 2px dashed #38BDF8;
        border-radius: 20px;
        padding: 12px;
        color: #0284C7;
        font-size: 0.88rem;
        font-weight: bold;
        line-height: 1.4;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .town-decor {
        font-size: 2rem;
        margin-top: 10px;
        letter-spacing: 4px;
    }

    /* メインヘッダーバナー（背景に山とイラスト風装飾） */
    .cute-banner {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 60%, #E0F2FE 100%);
        border-radius: 24px;
        padding: 24px 20px;
        text-align: center;
        margin-bottom: 20px;
        border: 3px solid #FFFFFF;
        box-shadow: 0 6px 16px rgba(0,0,0,0.03);
        position: relative;
        overflow: hidden;
    }
    .banner-title-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FFFFFF;
        padding: 6px 18px;
        border-radius: 30px;
        color: #FF3B30;
        font-weight: 900;
        font-size: 1.1rem;
        box-shadow: 0 2px 8px rgba(255, 59, 48, 0.15);
        margin-bottom: 8px;
    }
    .banner-sub-text {
        color: #1E293B;
        font-size: 1.2rem;
        font-weight: 900;
        letter-spacing: -0.2px;
    }

    /* 最寄り避難所案内カード (ピンク枠グラデーション) */
    .pink-card {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #FFD1DC;
        box-shadow: 0 8px 24px rgba(255, 182, 193, 0.25);
        position: relative;
        height: 100%;
    }
    .pink-loc-tag {
        color: #334155;
        font-size: 0.95rem;
        font-weight: bold;
    }
    .pink-guide-tag {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: bold;
        margin-top: 4px;
    }
    .dest-group {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 16px 0;
    }
    .dest-green-icon {
        background-color: #00A86B;
        color: white;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(0, 168, 107, 0.2);
    }
    .dest-green-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #00A86B;
    }
    .dest-green-sub {
        font-size: 0.95rem;
        color: #00A86B;
        font-weight: bold;
        margin-left: 6px;
    }
    .pink-arrow-btn {
        position: absolute;
        right: 20px;
        top: 42%;
        background-color: #FF477E;
        color: white;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(255, 71, 126, 0.3);
    }
    .pill-green-badge {
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

    /* 移動ワンポイントカード (黄色枠) */
    .yellow-card {
        background: #FFFDF0;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #FDE68A;
        box-shadow: 0 8px 24px rgba(253, 230, 138, 0.3);
        height: 100%;
    }
    .yellow-card-title {
        color: #D97706;
        font-weight: 900;
        font-size: 1.2rem;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .yellow-card-item {
        font-size: 0.9rem;
        margin-bottom: 12px;
        color: #334155;
        line-height: 1.5;
    }

    /* 地図セクションタイトル */
    .map-title-bar {
        font-size: 1.3rem;
        font-weight: 900;
        color: #00A86B;
        margin: 24px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* 緊急電話番号エリア */
    .contact-card-box {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 20px;
        border: 2px solid #E2E8F0;
        margin-top: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    .contact-card-title {
        text-align: center;
        font-weight: 900;
        font-size: 1.05rem;
        color: #1E293B;
        margin-bottom: 14px;
    }
    .contact-grid-wrap {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px;
        text-align: center;
    }
    .contact-item-box {
        background: #F8FAFC;
        padding: 12px 8px;
        border-radius: 16px;
        border: 1px solid #F1F5F9;
    }
    .contact-item-label {
        font-size: 0.75rem;
        color: #64748B;
        font-weight: bold;
    }
    .contact-item-num {
        font-size: 1.4rem;
        font-weight: 900;
        color: #E11D48;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. サイドバー（非常口風ピクトグラム＆イラスト再現）
# ---------------------------------------------------------
RUNNER_SVG = """<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.5 5.5C14.6046 5.5 15.5 4.60457 15.5 3.5C15.5 2.39543 14.6046 1.5 13.5 1.5C12.3954 1.5 11.5 2.39543 11.5 3.5C11.5 4.60457 12.3954 5.5 13.5 5.5Z" fill="white"/><path d="M19.5 9.5L15 7.5L11.5 11L13.5 15L17.5 13.5V18.5H19.5V12.5L16.5 14L15 10.5L17 9.5H19.5V9.5Z" fill="white"/><path d="M9.5 8.5L6.5 12.5H9.5L10.5 17.5L6.5 22.5H4.5L8 18L7 13.5L4 15.5V18.5H2V14.5L6.5 11.5L8 8.5H9.5Z" fill="white"/></svg>"""

st.sidebar.markdown(f"""
<div class="sidebar-logo-wrap">
    <div class="runner-circle-icon">
        {RUNNER_SVG}
    </div>
    <div>
        <div class="sidebar-logo-title">防災ナビ</div>
        <div class="sidebar-logo-sub">いざという時に、<br>あなたのそばに</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("#### 📍 いまどこにいる？")
st.sidebar.caption("住所や建物名を入力してね")
user_address = st.sidebar.text_input("現在地入力", value="八王子市丹木町1丁目", label_visibility="collapsed")

st.sidebar.markdown("""
<div class="sidebar-town-bg">
    <div class="sidebar-msg-bubble">
        もしもの時も<br>一緒に考えよう！ ＼
    </div>
    <div class="town-decor">⛰️ 🏡 🏫 🌳</div>
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
st.markdown("""
<div class="cute-banner">
    <div class="banner-title-badge">📢 八王子市 避難ルートナビ 🌈</div>
    <div class="banner-sub-text">〜 現在地を入れるだけ！一番近くて安全な避難所へ即案内 〜</div>
    <div style="font-size: 1.2rem; margin-top: 8px;">🏔️ 🏢 🏃‍♂️ 🏫 🌳</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.25, 0.75])

with col1:
    st.markdown(f"""
    <div class="pink-card">
        <div class="pink-loc-tag">📍 現在地：{user_address}</div>
        <div class="pink-guide-tag">✨ 向かうべき最寄りの避難所はこちら！</div>
        <div class="dest-group">
            <div class="dest-green-icon">🏫</div>
            <div>
                <span class="dest-green-title">{nearest_shelter['name']}</span>
                <span class="dest-green-sub">{nearest_shelter['sub']}</span>
            </div>
        </div>
        <div>
            <span class="pill-green-badge">🏃 距離：約 {min_distance:.1f} km / 徒歩約 {walk_minutes} 分</span>
        </div>
        <div class="pink-arrow-btn">❯</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="yellow-card">
        <div class="yellow-card-title">💡 移動時のワンポイント 🥖</div>
        <div class="yellow-card-item">👟 <b>履物</b>：増水時の長靴は危険！スニーカーで。</div>
        <div class="yellow-card-item">🎒 <b>荷物</b>：両手が空くようにリュックで移動。</div>
        <div class="yellow-card-item">⚠️ <b>移動</b>：水で隠れた側溝や傾斜地に注意！</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="map-title-bar">🏛️ 安全おすすめ避難ルートマップ</div>', unsafe_allow_html=True)

# 地図表示
m = folium.Map(location=current_coords, zoom_start=15, tiles="OpenStreetMap")

folium.Marker(
    location=current_coords,
    popup=f"📍 現在地: {user_address}",
    tooltip="現在地",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

folium.Marker(
    location=nearest_shelter["coords"],
    popup=f"🏠 {nearest_shelter['name']}",
    tooltip=nearest_shelter['name'],
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

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
# 5. 緊急連絡先エリア
# ---------------------------------------------------------
st.markdown("""
<div class="contact-card-box">
    <div class="contact-card-title">📞 緊急連絡先＆通報ダイヤル</div>
    <div class="contact-grid-wrap">
        <div class="contact-item-box">
            <div class="contact-item-label">火災・救急・救助</div>
            <div class="contact-item-num">119 番</div>
        </div>
        <div class="contact-item-box">
            <div class="contact-item-label">警察（事件・事故）</div>
            <div class="contact-item-num" style="color:#0284C7;">110 番</div>
        </div>
        <div class="contact-item-box">
            <div class="contact-item-label">災害用伝言ダイヤル</div>
            <div class="contact-item-num" style="color:#0D9488;">171 番</div>
        </div>
        <div class="contact-item-box">
            <div class="contact-item-label">八王子市役所 (代表)</div>
            <div style="font-weight:900; font-size:1.0rem; color:#334155; margin-top:4px;">042-620-7111</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
