import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request
import math
import re
import random

# ---------------------------------------------------------
# 1. ページ基本設定
# ---------------------------------------------------------
st.set_page_config(page_title="ハチボー | 八王子市 防災ハザード＆避難ナビ", layout="wide")

# CSS設定（Pythonの文字列結合で正しく記述）
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
    ".level-badge { background: #FFFFFF; color: #D97706; border: 2px solid #FDE68A; padding: 2px 8px; border-radius: 8px; font-weight: 900; font-size: 0.75rem; margin-left: 8px; vertical-align: middle; }"
    ".ar-viewport { position: relative; background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); border-radius: 24px; padding: 20px; color: white; border: 4px solid #38BDF8; text-align: center; overflow: hidden; font-family: sans-serif; }"
    ".ar-arrow { font-size: 3.5rem; animation: bounce 1.5s infinite; margin: 10px 0; display: inline-block; }"
    "@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }"
    ".ar-tag { background: rgba(16, 185, 129, 0.9); border: 2px solid #6EE7B7; border-radius: 12px; padding: 10px; margin-top: 10px; font-weight: bold; color: white; display: inline-block; }"
    ".board-card { background: #FFFFFF; border-radius: 16px; padding: 12px 16px; border-left: 5px solid #38BDF8; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }"
    ".board-time { font-size: 0.75rem; color: #94A3B8; font-weight: bold; }"
    ".board-user { font-weight: 900; color: #0284C7; font-size: 0.9rem; }"
    ".board-text { font-size: 0.95rem; color: #334155; margin-top: 4px; font-weight: 600; }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# セッション状態の初期化
# ---------------------------------------------------------
if 'exp' not in st.session_state:
    st.session_state.exp = 0
if 'visit_count' not in st.session_state:
    st.session_state.visit_count = 0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "こんにちは！ハチボーだよ！八王子市の避難や災害について何か気になることはあるかな？「創価大学までの行き方は？」「持っていくものは？」など聞いてね！"}
    ]
if 'board_messages' not in st.session_state:
    st.session_state.board_messages = [
        {"user": "八王子太郎", "time": "10分前", "text": "浅川沿いの歩道、一部泥が溜まって滑りやすくなっています。通行注意！", "type": "⚠️ 危険箇所"},
        {"user": "高尾ハナコ", "time": "25分前", "text": "加住小避難所、開設準備完了している模様です。", "type": "ℹ️ 避難所状況"},
        {"user": "防災ボランティア", "time": "1時間前", "text": "八王子駅北口のバス停、通常通り運行しています。", "type": "🚌 交通情報"}
    ]
if 'hachibo_mood' not in st.session_state:
    st.session_state.hachibo_mood = "normal"

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

if st.session_state.visit_count == 0:
    add_exp(5)
st.session_state.visit_count += 1

# ---------------------------------------------------------
# 2. SVGパーツ (インタラクティブ表情チェンジ対応)
# ---------------------------------------------------------
def get_hachibo_svg(mood="normal"):
    eye_left = '<circle cx="41" cy="37" r="3" fill="#1E293B"/>'
    eye_right = '<circle cx="59" cy="37" r="3" fill="#1E293B"/>'
    mouth = '<path d="M 46 43 Q 50 46 54 43" stroke="#78350F" stroke-width="1.5" stroke-linecap="round" fill="none"/>'
    
    if mood == "happy":
        mouth = '<path d="M 44 42 Q 50 48 56 42 Z" fill="#78350F"/>'
    elif mood == "wink":
        eye_left = '<path d="M 38 37 Q 41 34 44 37" stroke="#1E293B" stroke-width="2" stroke-linecap="round" fill="none"/>'
        mouth = '<path d="M 45 42 Q 50 47 55 42" stroke="#78350F" stroke-width="2" stroke-linecap="round" fill="none"/>'

    return (
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
        + eye_left + eye_right +
        '<circle cx="42" cy="35.5" r="1" fill="white"/>'
        '<circle cx="60" cy="35.5" r="1" fill="white"/>'
        '<polygon points="48,40 52,40 50,42" fill="#78350F"/>'
        + mouth +
        '<ellipse cx="35" cy="41" rx="3" ry="1.8" fill="#F43F5E" opacity="0.6"/>'
        '<ellipse cx="65" cy="41" rx="3" ry="1.8" fill="#F43F5E" opacity="0.6"/>'
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
# 3. サイドバー (レベル＆ハチボーと遊ぶ)
# ---------------------------------------------------------
lv, title = get_level_info(st.session_state.exp)

sidebar_logo_html = (
    '<div class="sidebar-logo-wrap">'
    + get_hachibo_svg(st.session_state.hachibo_mood) +
    '<div><div class="sidebar-logo-title">ハチボー <span class="level-badge">Lv.' + str(lv) + '</span></div>'
    '<div class="sidebar-logo-sub">八王子市 防災ナビ / ' + title + '</div></div>'
    '</div>'
)
st.sidebar.markdown(sidebar_logo_html, unsafe_allow_html=True)

if st.sidebar.button("🖐️ ハチボーをつついてみる"):
    st.session_state.hachibo_mood = random.choice(["happy", "wink"])
    add_exp(1)
    st.rerun()

msg_text = "高尾山からみんなをナビするよ！<br>ハザードマップをチェック！"
if st.session_state.hachibo_mood == "happy":
    msg_text = "えへへ、つつかれた！<br>今日も防災の準備バッチリかな？"
elif st.session_state.hachibo_mood == "wink":
    msg_text = "ウインク！<br>八王子市の安全はボクが守るよ！"

st.sidebar.markdown(
    '<div class="sidebar-msg-bubble">' + msg_text + '</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏃‍♂️ 避難方法の選択")
mode_opt = st.sidebar.radio(
    "移動手段を選んでね",
    ('徒歩 (推奨)', '自転車', '車 (緊急時のみ)'),
    index=0
)

st.sidebar.markdown("---")
link_btns_html = (
    '<a href="https://hachioji-city.github.io/hazardmap/" target="_blank" class="hazard-btn">🗺️ 八王子市WEBハザードマップ公式</a>'
    '<a href="https://hachioji.riskma.jp/#/mobile" target="_blank" class="hazard-btn" style="background-color:#0D9488;">📱 八王子市 Riskma（雨量・河川情報）</a>'
    '<a href="https://www.jma.go.jp/bosai/kaikotan/#zoom:11/lat:35.658000/lon:139.339000/colordepth:normal/elements:rasrf&slmcs" target="_blank" class="hazard-btn" style="background-color:#0284C7;">🌧️ 気象庁 雨雲の動き（八王子付近）</a>'
    '<div style="margin-top: 20px;">' + SVG_TOWN_LANDSCAPE + '</div>'
)
st.sidebar.markdown(link_btns_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# データ・API関連関数
# ---------------------------------------------------------
def get_coords_from_address(address_text):
    default_coords = [35.6881, 139.3275]
    if not address_text:
        return default_coords
    try:
        cleaned_text = address_text.strip()
        cleaned_text = cleaned_text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        cleaned_text = re.sub(r'[\d\-－丁目番号]+$', '', cleaned_text).strip()
        search_query = cleaned_text if cleaned_text else address_text
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

def get_route_osrm(start_coords, end_coords, profile='foot'):
    try:
        url = 'http://router.project-osrm.org/route/v1/' + profile + '/' + str(start_coords[1]) + ',' + str(start_coords[0]) + ';' + str(end_coords[1]) + ',' + str(end_coords[0]) + '?overview=full&geometries=geojson'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('routes'):
                route = data['routes'][0]
                geometry = route['geometry']['coordinates']
                route_line = [[lat, lon] for lon, lat in geometry]
                distance_km = route['distance'] / 1000.0
                duration_min = math.ceil(route['duration'] / 60.0)
                return route_line, distance_km, duration_min, False
    except Exception:
        pass
    dist = calculate_distance(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
    walk_min = math.ceil((dist / 4.0) * 60)
    return [start_coords, end_coords], dist, walk_min, True

# ---------------------------------------------------------
# 4. ヘッダー＆メインナビ検索
# ---------------------------------------------------------
header_html = (
    '<div class="main-header-card">'
    '<div class="banner-title-badge">' + get_hachibo_svg("happy") + '<span>ハチボー</span></div>'
    '<div class="banner-sub-title">八王子市 防災ハザード＆避難インタラクティブナビ</div>'
    '<div>' + SVG_TOWN_LANDSCAPE + '</div>'
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
current_coords = get_coords_from_address(display_address)

if user_address_input.strip():
    add_exp(2)

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

mode_map = {'徒歩 (推奨)': 'foot', '自転車': 'cycling', '車 (緊急時のみ)': 'driving'}
mode_profile = mode_map[mode_opt]
route_line, real_dist, real_minutes, is_fallback = get_route_osrm(current_coords, nearest_shelter["coords"], mode_profile)
mode_label = mode_opt.split(' ')[0]

# ---------------------------------------------------------
# インパクト機能タブ構成
# ---------------------------------------------------------
tab_map, tab_ar, tab_ai, tab_board = st.tabs([
    "🗺️ 八王子ハザードマップ＆ルート", 
    "📱 AR避難ビジュアル案内", 
    "💬 ハチボー防災AIチャット", 
    "👥 地域防災コミュニティ掲示板"
])

# ---------------------------------------------------------
# TAB 1: マップ＋情報表示
# ---------------------------------------------------------
with tab_map:
    if is_fallback:
        st.warning("⚠️ ルート検索APIが混雑しているため、直線距離での目安を表示しています。")

    col1, col2 = st.columns([1.25, 0.75])
    with col1:
        nav_html = (
            '<div class="nav-card-box">'
            '<div class="current-pos-badge">📍 現在の検索位置</div>'
            '<div class="current-pos-name">' + display_address + '</div>'
            '<div class="target-shelter-badge">🏃‍♂️ おすすめの最寄り避難所</div>'
            '<div class="dest-shelter-title">' + nearest_shelter["name"] + '</div>'
            '<div class="dest-shelter-sub">所在地・区分：' + nearest_shelter["sub"] + '</div>'
            '<div><span class="route-info-pill">' + mode_label + 'ルート：約 ' + str(round(real_dist, 1)) + ' km / 約 ' + str(real_minutes) + ' 分</span></div>'
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

    st.markdown('<div class="map-title-bar">⚠️ 八王子市 防災ハザードマップ（重ね合わせ表示）</div>', unsafe_allow_html=True)

    m = folium.Map(location=current_coords, zoom_start=15, tiles="OpenStreetMap")
    folium.TileLayer(
        tiles="https://disaportaldata.gsi.go.jp/raster/01_flood_l2_shinsuisai_data/{z}/{x}/{y}.png",
        attr="国土地理院 洪水浸水想定区域", name="🌊 洪水浸水想定区域", opacity=0.6, overlay=True, control=True
    ).add_to(m)
    folium.TileLayer(
        tiles="https://disaportaldata.gsi.go.jp/raster/05_sedimentdisaster_raster/{z}/{x}/{y}.png",
        attr="国土地理院 土砂災害警戒区域", name="⛰️ 土砂災害警戒区域", opacity=0.6, overlay=True, control=True
    ).add_to(m)

    folium.Marker(location=current_coords, popup="現在地: " + display_address, tooltip="現在地", icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
    folium.Marker(location=nearest_shelter["coords"], popup=nearest_shelter['name'] + ' (' + nearest_shelter['cap'] + ')', tooltip=nearest_shelter['name'], icon=folium.Icon(color="green", icon="home")).add_to(m)

    folium.PolyLine(locations=route_line, color="#00A86B", weight=6, opacity=0.85, dash_array="6, 6" if is_fallback else None, tooltip=mode_label + "避難ルート").add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    st_folium(m, width="100%", height=450)

# ---------------------------------------------------------
# TAB 2: AR避難誘導風シミュレーター
# ---------------------------------------------------------
with tab_ar:
    st.subheader("📱 ARリアルタイム避難誘導ビュー（イメージ）")
    st.write("スマートフォンのカメラを通して、目の前にリアルタイムで避難方向とハザードが重なって表示されます！")
    
    ar_col1, ar_col2 = st.columns([1, 1])
    with ar_col1:
        ar_direction = "北東"
        ar_html = (
            '<div class="ar-viewport">'
            '<div style="font-size:0.8rem; color:#94A3B8;">[ 擬似カメラ画角 : 八王子市エリア ]</div>'
            '<div class="ar-arrow">⬆️</div>'
            '<div style="font-size:1.4rem; font-weight:900;">' + ar_direction + ' 方向へ進行</div>'
            '<div class="ar-tag">🏠 ' + nearest_shelter["name"] + ' まで あと ' + str(round(real_dist*1000)) + 'm</div>'
            '<div style="margin-top:15px; font-size:0.85rem; background:rgba(239, 68, 68, 0.2); border:1px solid #EF4444; padding:6px; border-radius:8px; color:#FCA5A5;">'
            '⚠️ 前方 150m 先: 浸水リスク有り（迂回推奨）</div>'
            '</div>'
        )
        st.markdown(ar_html, unsafe_allow_html=True)
    
    with ar_col2:
        st.markdown("### 🌟 AR機能の特徴")
        st.markdown("- **直感的な視界表示**: 地図を読まなくても画面の矢印に従うだけで安全な場所へ！")
        st.markdown("- **危険箇所のオーバーレイ**: 目の前の道路が冠水予定地の場合、赤くハイライト警告。")
        st.markdown("- **夜間モード対応**: 街灯の少ない避難路でも視界をサポート。")

# ---------------------------------------------------------
# TAB 3: ハチボー防災AIチャット
# ---------------------------------------------------------
with tab_ai:
    st.subheader("💬 ハチボー防災AIチャット")
    st.write("避難に関する疑問や気になることを何でも聞いてね！")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if user_prompt := st.chat_input("例: 「非常持ち出し袋には何を入れたらいい？」"):
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        bot_reply = "質問ありがとう！八王子の防災情報はボクにおまかせ！"
        if "創価大学" in user_prompt or "避難" in user_prompt:
            bot_reply = f"最寄りの避難所は【{nearest_shelter['name']}】（{nearest_shelter['sub']}）だよ！現在地から約{round(real_dist,1)}km、{mode_label}で約{real_minutes}分で着くよ！"
        elif "持ち物" in user_prompt or "袋" in user_prompt or "準備" in user_prompt:
            bot_reply = "持ち出し袋には【飲料水、非常食、懐中電灯、モバイルバッテリー、常備薬、現金、マスク】を準備しておくと安心だよ！リュックに入れて両手を空けておいてね！"
        elif "浅川" in user_prompt or "川" in user_prompt or "水" in user_prompt:
            bot_reply = "八王子市内の浅川や南浅川の様子は、サイドバーにある『八王子市 Riskma』からリアルタイム水位が確認できるよ！近づかないでね！"

        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)

# ---------------------------------------------------------
# TAB 4: 地域防災コミュニティ掲示板
# ---------------------------------------------------------
with tab_board:
    st.subheader("👥 地域の防災リアルタイム掲示板（共助機能）")
    st.write("近所の道路情報や避難所の混雑状況をみんなで投稿して共有しよう！")

    with st.expander("➕ 新しい投稿を追加する", expanded=False):
        post_user = st.text_input("お名前（ニックネーム）", value="八王子市民")
        post_type = st.selectbox("情報種別", ["⚠️ 危険箇所", "ℹ️ 避難所状況", "🚌 交通情報", "🤝 助け合い"])
        post_text = st.text_area("情報内容", placeholder="例：〇〇町交差点付近、倒木のため通行注意です。")
        if st.button("投稿する"):
            if post_text.strip():
                st.session_state.board_messages.insert(0, {
                    "user": post_user,
                    "time": "たった今",
                    "text": post_text,
                    "type": post_type
                })
                add_exp(3)
                st.success("投稿しました！ポイント獲得！")
                st.rerun()

    for msg in st.session_state.board_messages:
        board_html = (
            '<div class="board-card">'
            '<div style="display:flex; justify-content:space-between;">'
            '<span class="board-user">' + msg["user"] + ' <span style="font-size:0.75rem; color:#64748B;">(' + msg["type"] + ')</span></span>'
            '<span class="board-time">' + msg["time"] + '</span>'
            '</div>'
            '<div class="board-text">' + msg["text"] + '</div>'
            '</div>'
        )
        st.markdown(board_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. 緊急連絡先エリア
# ---------------------------------------------------------
contact_html = (
    '<div class="contact-card-box">'
    '<div class="contact-card-title">緊急連絡先＆通報ダイヤル</div>'
    '<div class="contact-grid-wrap">'
    '<div class="contact-item-box"><div class="contact-item-label">火災・救急・救助</div><div class="contact-item-num">119 番</div></div>'
    '<div class="contact-item-box"><div class="contact-item-label">警察（事件・事故）</div><div class="contact-item-num" style="color:#0284C7;">110 番</div></div>'
    '<div class="contact-item-box"><div class="contact-item-label">災害用伝言ダイヤル</div><div class="contact-item-num" style="color:#0D9488;">171 番</div></div>'
    '<div class="contact-item-box"><div class="contact-item-label">八王子市役所 (代表)</div><div style="font-weight:900; font-size:1.0rem; color:#334155; margin-top:4px;">042-620-7111</div></div>'
    '</div></div>'
)
st.markdown(contact_html, unsafe_allow_html=True)
