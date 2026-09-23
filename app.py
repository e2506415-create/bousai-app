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
st.set_page_config(page_title="ハチボー | 八王子市 防災ハザード＆避難ナビ", layout="wide")

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
        font-size: 1.6rem;
        font-weight: 900;
        color: #0F172A;
        line-height: 1.1;
    }
    .sidebar-logo-sub {
        font-size: 0.72rem;
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

    /* 上部バナーエリア */
    [data-testid="stVerticalBlock"] > div:has(div.banner-marker) {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        border-radius: 24px;
        padding: 20px;
        border: 3px solid #FFFFFF;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.15);
        margin-bottom: 20px;
    }

    .banner-title-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: #FFFFFF;
        padding: 8px 24px;
        border-radius: 30px;
        color: #D97706;
        font-weight: 900;
        font-size: 1.8rem;
        box-shadow: 0 2px 8px rgba(217, 119, 6, 0.15);
        margin-bottom: 6px;
    }
    .banner-sub-title {
        font-size: 0.95rem;
        font-weight: 800;
        color: #0284C7;
        margin-bottom: 10px;
    }

    /* 内側の白い検索カード枠 */
    [data-testid="stVerticalBlock"] > div:has(div.search-card-marker) {
        background-color: #FFFFFF !important;
        border-radius: 18px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
        margin-top: 10px !important;
    }

    .search-title-text {
        font-size: 1.05rem;
        font-weight: 900;
        color: #0284C7;
        text-align: center;
        margin-bottom: 8px;
    }

    /* 入力フォームの装飾 */
    div[data-baseweb="input"] {
        border-radius: 14px !important;
        border: 2px solid #38BDF8 !important;
        background-color: #F8FAFC !important;
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
        color: #475569;
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
        color: #E11D48;
        margin: 24px 0 12px 0;
    }

    /* リンクボタン風スタイル */
    .hazard-btn {
        display: block;
        background-color: #38BDF8;
        color: #FFFFFF !important;
        text-align: center;
        font-weight: 900;
        padding: 10px 14px;
        border-radius: 14px;
        text-decoration: none;
        box-shadow: 0 3px 8px rgba(56, 189, 248, 0.25);
        margin-top: 10px;
        font-size: 0.85rem;
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
# 2. SVGイラスト素材（高尾山ムササビ「ハチボー」全身＆街並み）
# ---------------------------------------------------------
SVG_HACHIBO_CHARACTER = """
<svg width="55" height="55" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M 68 62 C 88 58 96 36 82 22 C 72 12 62 24 66 38 Q 70 48 64 62" fill="#D97706" stroke="#B45309" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M 28 55 C 18 62 16 75 24 82 C 32 78 35 70 34 62 Z" fill="#F59E0B" stroke="#B45309" stroke-width="2"/>
  <path d="M 72 55 C 82 62 84 75 76 82 C 68 78 65 70 66 62 Z" fill="#F59E0B" stroke="#B45309" stroke-width="2"/>
  <path d="M 33 52 C 33 52 30 78 36 84 C 42 88 58 88 64 84 C 70 78 67 52 67 52 Z" fill="#F59E0B" stroke="#B45309" stroke-width="2.5"/>
  <ellipse cx="50" cy="70" rx="13" ry="12" fill="#FEF3C7"/>
  <path d="M 34 60 C 34 60 40 76 50 76 C 60 76 66 60 66 60 C 66 60 58 56 50 56 C 42 56 34 60 34 60 Z" fill="#059669" opacity="0.15"/>
  <ellipse cx="38" cy="85" rx="6" ry="3.5" fill="#78350F"/>
  <ellipse cx="62" cy="85" rx="6" ry="3.5" fill="#78350F"/>
  <circle cx="30" cy="62" r="4" fill="#F59E0B" stroke="#B45309" stroke-width="1.5"/>
  <circle cx="70" cy="62" r="4" fill="#F59E0B" stroke="#B45309" stroke-width="1.5"/>
  <ellipse cx="50" cy="42" rx="22" ry="18" fill="#F59E0B" stroke="#B45309" stroke-width="2.5"/>
  <ellipse cx="50" cy="45" rx="16" ry="12" fill="#FEF3C7"/>
  <circle cx="40" cy="41" r="3.5" fill="#1E293B"/>
  <circle cx="60" cy="41" r="3.5" fill="#1E293B"/>
  <circle cx="41" cy="39.5" r="1.2" fill="white"/>
  <circle cx="61" cy="39.5" r="1.2" fill="white"/>
  <polygon points="48,44 52,44 50,46" fill="#78350F"/>
  <path d="M 45 47 Q 50 50 55 47" stroke="#78350F" stroke-width="1.8" stroke-linecap="round" fill="none"/>
  <ellipse cx="34" cy="45" rx="3.5" ry="2" fill="#F43F5E" opacity="0.5"/>
  <ellipse cx="66" cy="45" rx="3.5" ry="2" fill="#F43F5E" opacity="0.5"/>
  <path d="M 26 32 C 26 12, 74 12, 74 32 Z" fill="#10B981"/>
  <rect x="22" y="30" width="56" height="5" rx="2.5" fill="#059669"/>
  <path d="M 50 16 L 51.5 19.5 L 55 18 L 52.8 21.5 L 56 24 L 51.5 23.5 L 50 27 L 48.5 23.5 L 44 24 L 47.2 21.5 L 45 18 L 48.5 19.5 Z" fill="#F59E0B"/>
</svg>
"""

SVG_TOWN_LANDSCAPE = """
<svg width="100%" height="45" viewBox="0 0 600 70" preserveAspectRatio="none" fill="none">
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
    {SVG_HACHIBO_CHARACTER}
    <div>
        <div class="sidebar-logo-title">ハチボー</div>
        <div class="sidebar-logo-sub">八王子市 防災ハザード＆避難ナビ</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class="sidebar-msg-bubble">
    高尾山からみんなをナビするよ！<br>ハザードマップをチェック！
</div>

<a href="https://hachioji-city.github.io/hazardmap/" target="_blank" class="hazard-btn">
    🗺️ 八王子市WEBハザードマップ公式
</a>

<a href="https://hachioji.riskma.jp/#/mobile" target="_blank" class="hazard-btn" style="background-color:#0D9488;">
    📱 八王子市 Riskma（雨量・河川情報）
</a>

<a href="https://www.jma.go.jp/bosai/kaikotan/#zoom:11/lat:35.658000/lon:139.339000/colordepth:normal/elements:rasrf&slmcs" target="_blank" class="hazard-btn" style="background-color:#0284C7;">
    🌧️ 気象庁 雨雲の動き（八王子付近）
</a>

<div style="margin-top: 20px;">
    {SVG_TOWN_LANDSCAPE}
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. メイン表示エリア
# ---------------------------------------------------------
with st.container():
    st.markdown('<div class="banner-marker"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align: center;">
        <div class="banner-title-badge">
            {SVG_HACHIBO_CHARACTER}
            <span>ハチボー</span>
        </div>
        <div class="banner-sub-title">八王子市 防災ハザード＆避難ナビ</div>
        <div>{SVG_TOWN_LANDSCAPE}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="search-card-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="search-title-text">📍 いまどこにいる？（住所や建物名を入力してね）</div>', unsafe_allow_html=True)
        user_address = st.text_input("現在地入力フォーム", value="八王子市丹木町1丁目", label_visibility="collapsed")

# ---------------------------------------------------------
# 5. 住所ジオコーディング・道路ルート(OSRM)計算ロジック
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

def get_osrm_route(start_coords, end_coords):
    try:
        url = f"http://router.project-osrm.org/route/v1/foot/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('routes'):
                route = data['routes'][0]
                geometry = route['geometry']['coordinates']
                route_line = [[lat, lon] for lon, lat in geometry]
                distance_km = route['distance'] / 1000.0
                duration_min = math.ceil(route['duration'] / 60.0)
                return route_line, distance_km, duration_min
    except Exception:
        pass
    dist = calculate_distance(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
    walk_min = math.ceil((dist / 4.0) * 60)
    return [start_coords, end_coords], dist, walk_min

current_coords = get_coords_from_address(user_address)

# 八王子市公式避難所リスト
SHELTERS = [
    {
        "name": "創価大学", 
        "sub": "丹木町1-236 / 広域避難場所", 
        "coords": [35.6870, 139.3285],
        "cap": "屋外 192,000㎡"
    },
    {
        "name": "加住小・中学校", 
        "sub": "加住町1-191 / 指定避難所（最大1,931人収容）", 
        "coords": [35.6828, 139.3361],
        "cap": "屋内 2,172㎡"
    },
    {
        "name": "第一小学校", 
        "sub": "元横山町2-14-3 / 指定避難所（最大1,242人収容）", 
        "coords": [35.6590, 139.3390],
        "cap": "屋内 2,561㎡"
    },
    {
        "name": "第四小学校", 
        "sub": "明神町2-15-1 / 指定避難所（最大1,295人収容）", 
        "coords": [35.6552, 139.3465],
        "cap": "屋内 2,671㎡"
    },
    {
        "name": "楢原小学校", 
        "sub": "楢原町140-4 / 指定避難所（最大1,364人収容）", 
        "coords": [35.6805, 139.3030],
        "cap": "屋内 2,818㎡"
    }
]

nearest_shelter = None
min_distance = float('inf')

for shelter in SHELTERS:
    dist = calculate_distance(current_coords[0], current_coords[1], shelter["coords"][0], shelter["coords"][1])
    if dist < min_distance:
        min_distance = dist
        nearest_shelter = shelter

route_line, real_dist, real_minutes = get_osrm_route(current_coords, nearest_shelter["coords"])

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
        <div class="dest-sub">📍 {nearest_shelter['sub']}</div>
        <div>
            <span class="pill-green-badge">道路ルート距離：約 {real_dist:.1f} km / 徒歩約 {real_minutes} 分</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="yellow-card">
        <div class="yellow-card-title">移動時のワンポイント</div>
        <div class="yellow-card-item"><b>履物</b>：増水時の長靴は危険！スニーカーで。</div>
        <div class="yellow-card-item"><b>荷物</b>：両手が空くようにリュックで移動。</div>
        <div class="yellow-card-item"><b>ハザード</b>：浸水エリア（水色）や崖（赤）を回避！</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="map-title-bar">⚠️ 八王子市 防災ハザードマップ（道路避難ルート重ね合わせ）</div>', unsafe_allow_html=True)

# 地図初期化
m = folium.Map(location=current_coords, zoom_start=15, tiles="OpenStreetMap")

# 国土地理院 ハザードマップタイルレイヤーの追加
folium.TileLayer(
    tiles="https://disaportaldata.gsi.go.jp/raster/01_flood_l2_shinsuisai_data/{z}/{x}/{y}.png",
    attr="国土地理院 洪水浸水想定区域",
    name="🌊 洪水浸水想定区域",
    opacity=0.6,
    overlay=True
).add_to(m)

folium.TileLayer(
    tiles="https://disaportaldata.gsi.go.jp/raster/05_sedimentdisaster_raster/{z}/{x}/{y}.png",
    attr="国土地理院 土砂災害警戒区域",
    name="⛰️ 土砂災害警戒区域",
    opacity=0.6,
    overlay=True
).add_to(m)

# マーカー（現在地）
folium.Marker(
    location=current_coords,
    popup=f"現在地: {user_address}",
    tooltip="現在地",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

# マーカー（避難所）
folium.Marker(
    location=nearest_shelter["coords"],
    popup=f"{nearest_shelter['name']} ({nearest_shelter['cap']})",
    tooltip=nearest_shelter['name'],
    icon=folium.Icon(color="green", icon="home")
).add_to(m)

# 道路沿いの避難ルート
folium.PolyLine(
    locations=route_line,
    color="#00A86B",
    weight=6,
    opacity=0.85,
    dash_array="6, 6",
    tooltip="道路優先避難ルート"
).add_to(m)

# レイヤーコントロール（右上）
folium.LayerControl(position="topright", collapsed=False).add_to(m)

# 地図レンダリング
st_folium(m, width="100%", height=450)

# 外部公式リンク案内
st.markdown("""
<div style="margin-top: 15px; text-align: center;">
    <a href="https://hachioji-city.github.io/hazardmap/" target="_blank" style="color:#0284C7; font-weight:900; text-decoration:underline; font-size:1.05rem;">
        🔗 詳細な避難場所指定や最新情報は「八王子市 WEB防災ハザードマップ公式」で確認できます
    </a>
</div>
""", unsafe_allow_html=True)

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
