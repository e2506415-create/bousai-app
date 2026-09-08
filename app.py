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
st.set_page_config(page_title="八王子市 避難ルートナビ", layout="wide")

# ポップデザインCSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;800;900&display=swap');

    .stApp {
        background: #F0F9FF;
        font-family: 'M PLUS Rounded 1c', 'Hiragino Maru Gothic ProN', "Yu Gothic UI", sans-serif;
    }
    
    /* サイドバー */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E0F2FE 0%, #BAE6FD 100%) !important;
        border-right: 3px solid #7DD3FC;
    }
    
    /* 左上ロゴエリア */
    .sidebar-logo-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        background: #FFFFFF;
        padding: 12px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
        border: 2px solid #38BDF8;
    }
    .sidebar-logo-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: #0F172A;
        line-height: 1.1;
    }
    .sidebar-logo-sub {
        font-size: 0.75rem;
        color: #0284C7;
        font-weight: 800;
        margin-top: 2px;
    }

    /* サイドバー吹き出し */
    .sidebar-msg-bubble {
        background-color: #FFFFFF;
        border: 2px dashed #38BDF8;
        border-radius: 20px;
        padding: 14px;
        color: #0284C7;
        font-size: 0.95rem;
        font-weight: 900;
        text-align: center;
        margin-top: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    /* メインヘッダーバナー */
    .header-banner {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 60%, #E0F2FE 100%);
        border-radius: 24px;
        padding: 24px 20px 20px 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.2);
        border: 3px solid #FFFFFF;
    }
    .banner-title-badge {
        display: inline-block;
        background: #FFFFFF;
        padding: 6px 20px;
        border-radius: 30px;
        color: #FF3B30;
        font-weight: 900;
        font-size: 1.25rem;
        box-shadow: 0 2px 8px rgba(255, 59, 48, 0.15);
        margin-bottom: 8px;
    }
    .banner-sub-text {
        color: #1E293B;
        font-size: 1.1rem;
        font-weight: 900;
        margin-bottom: 10px;
    }

    /* 水色バナー内に入れる入力欄の見出し */
    .banner-search-label {
        font-size: 1.1rem;
        font-weight: 900;
        color: #0284C7;
        margin-top: 10px;
        margin-bottom: 6px;
    }

    /* 入力フォームデザイン（角丸・白背景） */
    div[data-baseweb="input"] {
        border-radius: 18px !important;
        border: 2px solid #38BDF8 !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15) !important;
        background-color: #FFFFFF !important;
    }

    /* 最寄り避難所案内カード */
    .pink-card {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #FFD1DC;
        box-shadow: 0 8px 24px rgba(255, 182, 193, 0.25);
        height: 100%;
    }
    .pink-loc-tag {
        color: #334155;
        font-size: 0.95rem;
        font-weight: 900;
    }
    .pink-guide-tag {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 900;
        margin-top: 4px;
    }
    .dest-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #00A86B;
        margin: 10px 0 2px 0;
    }
    .dest-sub {
        font-size: 0.95rem;
        color: #00A86B;
        font-weight: 800;
        margin-bottom: 14px;
    }
    .pill-green-badge {
        background-color: #E6F4EA;
        color: #137333;
        padding: 8px 18px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #A7F3D0;
    }

    /* 移動ワンポイントカード */
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
        margin-bottom: 12px;
        border-bottom: 2px dashed #FDE68A;
        padding-bottom: 6px;
    }
    .yellow-card-item {
        font-size: 0.88rem;
        margin-bottom: 10px;
        color: #334155;
        font-weight: 800;
        line-height: 1.5;
    }

    /* 地図セクションタイトル */
    .map-title-bar {
        font-size: 1.3rem;
        font-weight: 900;
        color: #00A86B;
        margin: 24px 0 12px 0;
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
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
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
        font-weight: 800;
    }
    .contact-item-num {
        font-size: 1.35rem;
        font-weight: 900;
        color: #E11D48;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SVGイラスト素材
# ---------------------------------------------------------
SVG_LOGO_ICON = """<svg width="40" height="40" viewBox="0 0 100 100" fill="none"><rect width="100" height="100" rx="24" fill="#00A86B"/><circle cx="50" cy="30" r="10" fill="white"/><path d="M50 45 L35 65 H45 V85 H55 V65 H65 Z" fill="white"/></svg>"""

SVG_TOWN_LANDSCAPE = """
<svg width="100%" height="50" viewBox="0 0 600 70" preserveAspectRatio="none" fill="none">
    <path d="M0 70 L80 25 L160 70 Z" fill="#A7F3D0"/>
    <path d="M100 70 L200 10 L300 70 Z" fill="#6EE7B7"/>
    <path d="M400 70 L480 30 L560 70 Z" fill="#A7F3D0"/>
    <rect x="180" y="40" width="25" height="30" fill="#38BDF8" rx="2"/>
    <polygon points="180,40 192.5,28 205,40" fill="#F43F5E"/>
    <rect x="230" y="30" width="30" height="40" fill="#FBBF24" rx="3"/>
    <rect x="330" y="35" width="25" height="35" fill="#818CF8" rx="2"/>
    <polygon points="330,35 342.5,25 355,35" fill="#10B981"/>
    <circle cx="150" cy="50" r="12" fill="#34D399"/>
    <rect x="148" y="60" width="4" height="10" fill="#78350F"/>
    <circle cx="380" cy="48" r="14" fill="#10B981"/>
    <rect x="378" y="58" width="4" height="12" fill="#78350F"/>
</svg>
"""

# ---------------------------------------------------------
# 3. サイドバー
# ---------------------------------------------------------
st.sidebar.markdown(f"""
<div class="sidebar-logo-wrap">
    {SVG_LOGO_ICON}
    <div>
        <div class="sidebar-logo-title">防災ナビ</div>
        <div class="sidebar-logo-sub">いざという時に、あなたのそばに</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class="sidebar-msg-bubble">
    もしもの時も<br>一緒に考えよう！
</div>
<div style="margin-top: 20px;">
    {SVG_TOWN_LANDSCAPE}
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. メイン表示エリア（水色バナー内に現在地入力フォームを一体化）
# ---------------------------------------------------------
# 水色バナーの上半分を描画
st.markdown(f"""
<div class="header-banner">
    <div class="banner-title-badge">八王子市 避難ルートナビ</div>
    <div class="banner-sub-text">〜 現在地を入れるだけ！一番近くて安全な避難所へ即案内 〜</div>
    <div>
        {SVG_TOWN_LANDSCAPE}
    </div>
    <div class="banner-search-label">いまどこにいる？（住所や建物名を入力してね）</div>
</div>
""", unsafe_allow_html=True)

# 入力フォーム
user_address = st.text_input("現在地入力フォーム", value="八王子市丹木町1丁目", label_visibility="collapsed")

# ---------------------------------------------------------
# 5. 住所・距離計算ロジック
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
# 6. カード＆マップ表示エリア
# ---------------------------------------------------------
col1, col2 = st.columns([1.25, 0.75])

with col1:
    st.markdown(f"""
    <div class="pink-card">
        <div class="pink-loc-tag">現在地：{user_address}</div>
        <div class="pink-guide-tag">向かうべき最寄りの避難所はこちら！</div>
        <div class="dest-title">{nearest_shelter['name']}</div>
        <div class="dest-sub">{nearest_shelter['sub']}</div>
        <div>
            <span class="pill-green-badge">距離：約 {min_distance:.1f} km / 徒歩約 {walk_minutes} 分</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="yellow-card">
        <div class="yellow-card-title">移動時のワンポイント</div>
        <div class="yellow-card-item"><b>履物</b>：増水時の長靴は危険！スニーカーで。</div>
        <div class="yellow-card-item"><b>荷物</b>：両手が空くようにリュックで移動。</div>
        <div class="yellow-card-item"><b>移動</b>：水で隠れた側溝や傾斜地に注意！</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="map-title-bar">安全おすすめ避難ルートマップ</div>', unsafe_allow_html=True)

# 地図表示
m = folium.Map(location=current_coords, zoom_start=15, tiles="OpenStreetMap")

folium.Marker(
    location=current_coords,
    popup=f"現在地: {user_address}",
    tooltip="現在地",
    icon=folium.Icon(color="red")
).add_to(m)

folium.Marker(
    location=nearest_shelter["coords"],
    popup=nearest_shelter['name'],
    tooltip=nearest_shelter['name'],
    icon=folium.Icon(color="green")
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
# 7. 緊急連絡先エリア
# ---------------------------------------------------------
st.markdown("""
<div class="contact-card-box">
    <div class="contact-card-title">緊急連絡先＆通報ダイヤル</div>
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
