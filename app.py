import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request
import math
import re

# ---------------------------------------------------------
# 1. ページ基本設定 (前のまま)
# ---------------------------------------------------------
st.set_page_config(page_title="ハチボー | 八王子市 防災ハザード＆避難ナビ", layout="wide")

# CSS設定 (前のまま + 新機能用の微調整)
css_style = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;800;900&display=swap');"
    ".stApp { background: #F0F9FF; font-family: 'M PLUS Rounded 1c', sans-serif; }"
    "[data-testid='stSidebar'] { background: linear-gradient(180deg, #E0F2FE 0%, #BAE6FD 100%) !important; border-right: 3px solid #7DD3FC; }"
    ".sidebar-logo-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; background: #FFFFFF; padding: 12px; border-radius: 20px; box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2); border: 2px solid #38BDF8; }"
    ".sidebar-logo-title { font-size: 1.5rem; font-weight: 900; color: #0F172A; line-height: 1.1; }"
    ".sidebar-logo-sub { font-size: 0.72rem; color: #0284C7; font-weight: 800; margin-top: 2px; }"
    ".sidebar-msg-bubble { background-color: #FFFFFF; border: 2px dashed #38BDF8; border-radius: 20px; padding: 14px; color: #0284C7; font-size: 0.95rem; font-weight: 900; text-align: center; margin-top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }"
    ".main-header-card { background: linear-gradient(180deg, #E0F2FE 0%, #FFFFFF 100%); border: 3px solid #BAE6FD; border-radius: 28px; padding: 24px 20px 16px 20px; text-align: center; box-shadow: 0 8px 24px rgba(56, 189, 248, 0.12); margin-bottom: 20px; }"
    ".banner-title-badge { display: inline-flex; align-items: center; gap: 12px; background: #FFFFFF; padding: 10px 28px; border-radius: 50px; color: #D97706; font-weight: 900; font-size: 2rem; box-shadow: 0 4px 16px rgba(217, 119, 6, 0.15); border: 2px solid #FDE68A; margin-bottom: 8px; }"
    ".banner-sub-title { font-size: 1rem; font-weight: 800; color: #0284C7; margin-bottom: 12px; letter-spacing: 0.05em; }"
    ".search-title-text { font-size: 1.05rem; font-weight: 900; color: #0284C7; text-align: center; margin-bottom: 10px; }"
    "div[data-baseweb='input'] { border-radius: 14px !important; border: 2px solid #38BDF8 !important; background-color: #F8FAFC !important; }"
    ".nav-card-box { background: #FFFFFF; border-radius: 24px; padding: 20px; border: 3px solid #38BDF8; box-shadow: 0 8px 20px rgba(56, 189, 248, 0.15); height: 100%; }"
    ".current-pos-badge { background: #E0F2FE; color: #0284C7; font-size: 0.85rem; font-weight: 900; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 6px; }"
    ".current-pos-name { font-size: 1.1rem; font-weight: 900; color: #1E293B; margin-bottom: 14px; border-bottom: 1px dashed #BAE6FD; padding-bottom: 8px; }"
    ".target-shelter-badge { background: #10B981; color: #FFFFFF; font-size: 0.85rem; font-weight: 900; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 6px; }"
    ".dest-shelter-title { font-size: 1.5rem; font-weight: 900; color: #047857; margin: 2px 0; }"
    ".dest-shelter-sub { font-size: 0.88rem; color: #475569; font-weight: 800; margin-bottom: 12px; }"
    ".route-info-pill { background-color: #ECFDF5; color: #065F46; padding: 8px 16px; border-radius: 50px; font-weight: 900; font-size: 0.9rem; display: inline-block; border: 1.5px solid #A7F3D0; }"
    ".yellow-card { background: #FFFDF0; border-radius: 24px; padding: 20px; border: 3px solid #FDE68A; box-shadow: 0 8px 20px rgba(253, 230, 138, 0.25); height: 100%; }"
    ".yellow-card-title { color: #D97706; font-weight: 900; font-size: 1.15rem; margin-bottom: 12px; border-bottom: 2px dashed #FDE68A; padding-bottom: 6px; }"
    ".yellow-card-item { font-size: 0.88rem; margin-bottom: 10px; color: #334155; font-weight: 800; line-height: 1.5; }"
    ".map-title-bar { font-size: 1.25rem; font-weight: 900; color: #E11D48; margin: 24px 0 12px 0; }"
    ".hazard-btn { display: block; background-color: #38BDF8; color: #FFFFFF !important; text-align: center; font-weight: 900; padding: 10px 14px; border-radius: 14px; text-decoration: none; box-shadow: 0 3px 8px rgba(56, 189, 248, 0.25); margin-top: 10px; font-size: 0.85rem; }"
    ".contact-card-box { background: #FFFFFF; border-radius: 24px; padding: 20px; border: 2px solid #E2E8F0; margin-top: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); }"
    ".contact-card-title { text-align: center; font-weight: 900; font-size: 1.05rem; color: #1E293B; margin-bottom: 14px; }"
    ".contact-grid-wrap { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; text-align: center; }"
    ".contact-item-box { background: #F8FAFC; padding: 12px 8px; border-radius: 16px; border: 1px solid #F1F5F9; }"
    ".contact-item-label { font-size: 0.75rem; color: #64748B; font-weight: 800; }"
    ".contact-item-num { font-size: 1.35rem; font-weight: 900; color: #E11D48; margin-top: 2px; }"
    
    /* 育成機能用の控えめなスタイル追加 */
    ".level-badge { background: #FFFFFF; color: #D97706; border: 2px solid #FDE68A; padding: 2px 8px; border-radius: 8px; font-weight: 900; font-size: 0.75rem; margin-left: 8px; vertical-align: middle; }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# 育成機能のロジック (前のデザインを崩さないよう控えめに)
# ---------------------------------------------------------
if 'exp' not in st.session_state:
    st.session_state.exp = 0
if 'visit_count' not in st.session_state:
    st.session_state.visit_count = 0

def add_exp(amount):
    st.session_state.exp += amount

def get_level_info(exp):
    level = exp // 10 + 1
    if level < 5:
        title = "ひよっこ防災士"
    elif level < 10:
        title = "見習いハチボー"
    else:
        title = "八王子マスター"
    return level, title

# 訪問経験値（初回のみ）
if st.session_state.visit_count == 0:
    add_exp(5)
st.session_state.visit_count += 1

# ---------------------------------------------------------
# 2. SVGパーツ (前のまま)
# ---------------------------------------------------------
SVG_HACHIBO_CHARACTER = (
    '<svg width="55" height="55" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M 68 65 C 88 62 96 38 82 22 C 72 12 62 24 66 38 C 70 48 64 65 Z" fill="#D97706" stroke="#B45309" stroke-width="2"/>'
    '<path d="M 28 50 C 15 58 12 72 22 80 C 30 75 32 68 32 60 Z" fill="#F59E0B" stroke="#B45309" stroke-width="1.8"/>'
    '<path d="M 72 50 C 85 58 88 72 78 80 C 70 75 68 68 68 60 Z" fill="#F59E0B" stroke="#B45309" stroke-width="1.8"/>'
    '<path d="M 33 50 C 33 50 30 76 38 82 C 45 86 55 86 62 82 C 70 76 67 50 67 50 Z" fill="#F59E0B" stroke="#B45309" stroke-width="2"/>'
    '<ellipse cx="50" cy="68" rx="12" ry="10" fill="#FEF3C7"/>'
    '<path d="M 35 56 Q 50 62 65 56 L 62 76 Q 50 80 38 76 Z" fill="#10B981" opacity="0.8"/>'
    '<ellipse cx="40" cy="83" rx="5" ry="3" fill="#78350F"/>'
    '<ellipse cx="60" cy="83" rx="5" ry="3" fill="#78350F"/>'
    '<circle cx="30" cy="58" r="3.5" fill="#F59E0B" stroke="#B45309" stroke-width="1.5"/>'
    '<circle cx="70" cy="58" r="3.5" fill="#F59E0B" stroke="#B45309" stroke-width="1.5"/>'
    '<ellipse cx="50" cy="38" rx="20" ry="16" fill="#F59E0B" stroke="#B45309" stroke-width="2"/>'
    '<ellipse cx="50" cy="41" rx="14" ry="10" fill="#FEF3C7"/>'
    '<circle cx="41" cy="37" r="3" fill="#1E293B"/>'
    '<circle cx="59" cy="37" r="3" fill="#1E293B"/>'
    '<circle cx="42" cy="35.5" r="1" fill="white"/>'
    '<circle cx="60" cy="35.5" r="1" fill="white"/>'
    '<polygon points="48,40 52,40 50,42" fill="#78350F"/>'
    '<path d="M 46 43 Q 50 46 54 43" stroke="#78350F" stroke-width="1.5" stroke-linecap="round" fill="none"/>'
    '<ellipse cx="35" cy="41" rx="3" ry="1.8" fill="#F43F5E" opacity="0.5"/>'
    '<ellipse cx="65" cy="41" rx="3" ry="1.8" fill="#F43F5E" opacity="0.5"/>'
    '<path d="M 28 28 C 28 10, 72 10, 72 28 Z" fill="#10B981"/>'
    '<rect x="24" y="26" width="52" height="4" rx="2" fill="#059669"/>'
    '<path d="M 50 14 L 51.2 17 L 54 15.8 L 52.3 18.7 L 55 20.8 L 51.2 20.4 L 50 23 L 48.8 20.4 L 45 20.8 L 47.7 18.7 L 46 15.8 L 48.8 17 Z" fill="#F59E0B"/>'
    '</svg>'
)

SVG_TOWN_LANDSCAPE = (
    '<svg width="100%" height="45" viewBox="0 0 600 70" preserveAspectRatio="none" fill="none">'
    '<path d="M0 70 L80 25 L160 70 Z" fill="#A7F3D0"/>'
    '<path d="M100 70 L200 10 L300 70 Z" fill="#6EE7B7"/>'
    '<path d="M400 70 L480 30 L560 70 Z" fill="#A7F3D0"/>'
    '<rect x="180" y="40" width="25" height="30" fill="#38BDF8" rx="2"/>'
    '<polygon points="180,40 192.5,28 205,40" fill="#F43F5E"/>'
    '<rect x="230" y="30" width="30" height="40" fill="#FBBF24" rx="3"/>'
    '<rect x="330" y="35" width="25" height="35" fill="#818CF8" rx="2"/>'
    '<polygon points="330,35 342.5,25 355,35" fill="#10B981"/>'
    '<circle cx="150" cy="50" r="12" fill="#34D399"/>'
    '<rect x="148" y="60" width="4" height="10" fill="#78350F"/>'
    '<circle cx="380" cy="48" r="14" fill="#10B981"/>'
    '<rect x="378" y="58" width="4" height="12" fill="#78350F"/>'
    '</svg>'
)

# ---------------------------------------------------------
# 3. サイドバー (前のまま + 新機能 用途選択)
# ---------------------------------------------------------
lv, title = get_level_info(st.session_state.exp)

# レベル情報をタイトル横に表示
sidebar_logo_html = (
    f'<div class="sidebar-logo-wrap">'
    f'{SVG_HACHIBO_CHARACTER}'
    f'<div><div class="sidebar-logo-title">ハチボー <span class="level-badge">Lv.{lv}</span></div>'
    f'<div class="sidebar-logo-sub">八王子市 防災ハザード＆避難ナビ / {title}</div></div>'
    f'</div>'
)
st.sidebar.markdown(sidebar_logo_html, unsafe_allow_html=True)

st.sidebar.markdown(
    f'<div class="sidebar-msg-bubble">高尾山からみんなをナビするよ！<br>ハザードマップをチェック！</div>',
    unsafe_allow_html=True
)

# 新機能: 用途選択（自転車・徒歩・車）を追加
st.sidebar.markdown("---")
st.sidebar.subheader("🏃‍♂️ 避難方法の選択")
mode_opt = st.sidebar.radio(
    "移動手段を選んでね",
    ('徒歩 (推奨)', '自転車', '車 (緊急時のみ)'),
    index=0
)

# リンクボタン (前のまま)
st.sidebar.markdown("---")
st.sidebar.markdown(
    f'<a href="https://hachioji-city.github.io/hazardmap/" target="_blank" class="hazard-btn">🗺️ 八王子市WEBハザードマップ公式</a>'
    f'<a href="https://hachioji.riskma.jp/#/mobile" target="_blank" class="hazard-btn" style="background-color:#0D9488;">📱 八王子市 Riskma（雨量・河川情報）</a>'
    f'<a href="https://www.jma.go.jp/bosai/kaikotan/#zoom:11/lat:35.658000/lon:139.339000/colordepth:normal/elements:rasrf&slmcs" target="_blank" class="hazard-btn" style="background-color:#0284C7;">🌧️ 気象庁 雨雲の動き（八王子付近）</a>'
    f'<div style="margin-top: 20px;">{SVG_TOWN_LANDSCAPE}</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# データ・API関連関数 (新機能 八王子限定・用途別ルート検索・集中エラー対策)
# ---------------------------------------------------------

# 八王子市公式避難所リスト (前のまま)
SHELTERS = [
    {"name": "創価大学", "sub": "丹木町1-236 / 広域避難場所", "coords": [35.6870, 139.3285], "cap": "屋外 192,000㎡"},
    {"name": "加住小・中学校", "sub": "加住町1-191 / 指定避難所（最大1,931人収容）", "coords": [35.6828, 139.3361], "cap": "屋内 2,172㎡"},
    {"name": "第一小学校", "sub": "元横山町2-14-3 / 指定避難所（最大1,242人収容）", "coords": [35.6590, 139.3390], "cap": "屋内 2,561㎡"},
    {"name": "第四小学校", "sub": "明神町2-15-1 / 指定避難所（最大1,295人収容）", "coords": [35.6552, 139.3465], "cap": "屋内 2,671㎡"},
    {"name": "楢原小学校", "sub": "楢原町140-4 / 指定避難所（最大1,364人収容）", "coords": [35.6805, 139.3030], "cap": "屋内 2,818㎡"}
]

# 新機能: 八王子限定にするジオコーディング
def get_coords_from_address(address_text):
    default_coords = [35.6881, 139.3275]
    if not address_text:
        return default_coords
    
    try:
        # APIエラー防止クレンジング (前のまま)
        cleaned_text = address_text.strip()
        cleaned_text = cleaned_text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        cleaned_text = re.sub(r'[\d\-－丁目番号]+$', '', cleaned_text).strip()
        
        search_query = cleaned_text if cleaned_text else address_text
        # 新機能: 「八王子市」を自動付加
        if "八王子" not in search_query:
            search_query = "東京都八王子市 " + search_query
            
        url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" + urllib.parse.quote(search_query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=3) as response:
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

# 新機能: OSRM用途別ルート検索 & 集中エラー対策
def get_route_osrm(start_coords, end_coords, profile='foot'):
    try:
        url = f"http://router.project-osrm.org/route/v1/{profile}/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        # 集中対策: タイムアウトを厳しめに設定
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('routes'):
                route = data['routes'][0]
                geometry = route['geometry']['coordinates']
                route_line = [[lat, lon] for lon, lat in geometry]
                distance_km = route['distance'] / 1000.0
                duration_min = math.ceil(route['duration'] / 60.0)
                return route_line, distance_km, duration_min
    except Exception:
        # 集中エラー時のフォールバック (直線距離)
        pass
    
    # エラー時は直線距離から徒歩時間を推定
    dist = calculate_distance(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
    walk_min = math.ceil((dist / 4.0) * 60)
    return [start_coords, end_coords], dist, walk_min, True # 4つ目の戻り値はエラーフラグ

# ---------------------------------------------------------
# 4. メイン表示エリア (前のまま)
# ---------------------------------------------------------
header_html = (
    '<div class="main-header-card">'
    f'<div class="banner-title-badge">{SVG_HACHIBO_CHARACTER}<span>ハチボー</span></div>'
    '<div class="banner-sub-title">八王子市 防災ハザード＆避難ナビ</div>'
    f'<div>{SVG_TOWN_LANDSCAPE}</div>'
    '</div>'
)
st.markdown(header_html, unsafe_allow_html=True)

st.markdown('<div class="search-title-text">📍 いまどこにいる？（住所や建物名を入力してね）</div>', unsafe_allow_html=True)

user_address_input = st.text_input(
    "現在地入力フォーム", 
    value="", 
    placeholder="例：八王子市丹木町1丁目、八王子駅、創価大学 など", 
    label_visibility="collapsed"
)

display_address = user_address_input if user_address_input.strip() else "八王子市丹木町1丁目"

# --- ルート検索実行と育成経験値 ---
current_coords = get_coords_from_address(display_address)

if user_address_input.strip():
    add_exp(2) # 住所検索で経験値+2

SHELTERS = [
    {"name": "創価大学", "sub": "丹木町1-236 / 広域避難場所", "coords": [35.6870, 139.3285], "cap": "屋外 192,000㎡"},
    {"name": "加住小・中学校", "sub": "加住町1-191 / 指定避難所（最大1,931人収容）", "coords": [35.6828, 139.3361], "cap": "屋内 2,172㎡"},
    {"name": "第一小学校", "sub": "元横山町2-14-3 / 指定避難所（最大1,242人収容）", "coords": [35.6590, 139.3390], "cap": "屋内 2,561㎡"},
    {"name": "第四小学校", "sub": "明神町2-15-1 / 指定避難所（最大1,295人収容）", "coords": [35.6552, 139.3465], "cap": "屋内 2,671㎡"},
    {"name": "楢原小学校", "sub": "楢原町140-4 / 指定避難所（最大1,364人収容）", "coords": [35.6805, 139.3030], "cap": "屋内 2,818㎡"}
]

nearest_shelter = None
min_distance = float('inf')

for shelter in SHELTERS:
    dist = calculate_distance(current_coords[0], current_coords[1], shelter["coords"][0], shelter["coords"][1])
    if dist < min_distance:
        min_distance = dist
        nearest_shelter = shelter

# OSRMプロファイルのマッピング
mode_map = {
    '徒歩 (推奨)': 'foot',
    '自転車': 'cycling',
    '車 (緊急時のみ)': 'driving'
}
mode_profile = mode_map[mode_opt]

# 用途別ルート検索実行
result = get_route_osrm(current_coords, nearest_shelter["coords"], mode_profile)
route_line = result[0]
real_dist = result[1]
real_minutes = result[2]
is_fallback = result[3] if len(result) > 3 else False

# 用途別の日本語ラベル
mode_label = mode_opt.split(' ')[0]

if is_fallback:
    st.warning("⚠️ ルート検索APIが混雑しているため、直線距離での目安を表示しています。")

# ---------------------------------------------------------
# 6. カード＆マップ表示エリア (前のまま + 新機能 用途別ナビ表示)
# ---------------------------------------------------------
col1, col2 = st.columns([1.25, 0.75])

with col1:
    nav_html = (
        '<div class="nav-card-box">'
        '<div class="current-pos-badge">📍 現在の検索位置</div>'
        f'<div class="current-pos-name">{display_address}</div>'
        '<div class="target-shelter-badge">🏃‍♂️ おすすめの最寄り避難所</div>'
        f'<div class="dest-shelter-title">{nearest_shelter["name"]}</div>'
        f'<div class="dest-shelter-sub">所在地・区分：{nearest_shelter["sub"]}</div>'
        f'<div><span class="route-info-pill">{mode_label}ルート：約 {real_dist:.1f} km / 約 {real_minutes} 分</span></div>'
        '</div>'
    )
    st.markdown(nav_html, unsafe_allow_html=True)

with col2:
    yellow_html = (
        '<div class="yellow-card">'
        '<div class="yellow-card-title">移動時のワンポイント</div>'
        '<div class="yellow-card-item"><b>履物</b>：増水時の長靴は危険！スニーカーで。</div>'
        '<div class="yellow-card-item"><b>荷物</b>：両手が空くようにリュックで移動。</div>'
        '<div class="yellow-card-item"><b>ハザード</b>：浸水エリア（水色）や崖（赤）を回避！</div>'
        '</div>'
    )
    st.markdown(yellow_html, unsafe_allow_html=True)

st.markdown('<div class="map-title-bar">⚠️ 八王子市 防災ハザードマップ（用途別避難ルート重ね合わせ）</div>', unsafe_allow_html=True)

# 地図初期化 (前のまま)
m = folium.Map(location=current_coords, zoom_start=15, tiles="OpenStreetMap")

# 新機能: ハザードマップ レイヤー追加 (チェックボタンで意味を持たせる)
folium.TileLayer(
    tiles="https://disaportaldata.gsi.go.jp/raster/01_flood_l2_shinsuisai_data/{z}/{x}/{y}.png",
    attr="国土地理院 洪水浸水想定区域",
    name="🌊 洪水浸水想定区域",
    opacity=0.6,
    overlay=True,
    control=True
).add_to(m)

folium.TileLayer(
    tiles="
