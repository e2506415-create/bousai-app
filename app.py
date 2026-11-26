import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request
import math
import re

# オプショナルインポート（GPS機能用）
try:
    from streamlit_js_eval import get_geolocation
    HAS_GPS_LIB = True
except ImportError:
    HAS_GPS_LIB = False

# ---------------------------------------------------------
# 1. ページ基本設定
# ---------------------------------------------------------
st.set_page_config(
    page_title="はちまる | 八王子市 防災・避難ナビ",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto"
)

# CSS設定（スマホ・PC・HP埋め込み最適化）
css_style = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700;800;900&display=swap');"
    ".stApp { background: #F0F9FF; font-family: 'M PLUS Rounded 1c', sans-serif; }"
    "[data-testid='stSidebar'] { background: linear-gradient(180deg, #E0F2FE 0%, #BAE6FD 100%) !important; border-right: 3px solid #7DD3FC; }"
    ".sidebar-logo-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; background: #FFFFFF; padding: 12px; border-radius: 20px; box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2); border: 2px solid #38BDF8; }"
    ".sidebar-logo-title { font-size: 1.45rem; font-weight: 900; color: #0F172A; line-height: 1.1; }"
    ".sidebar-logo-sub { font-size: 0.72rem; color: #0284C7; font-weight: 800; margin-top: 2px; }"
    ".sidebar-msg-bubble { background-color: #FFFFFF; border: 2px dashed #38BDF8; border-radius: 18px; padding: 12px; color: #0284C7; font-size: 0.9rem; font-weight: 900; text-align: center; margin-top: 8px; }"
    ".main-header-card { background: linear-gradient(180deg, #E0F2FE 0%, #FFFFFF 100%); border: 3px solid #BAE6FD; border-radius: 24px; padding: 20px 16px 12px 16px; text-align: center; box-shadow: 0 8px 24px rgba(56, 189, 248, 0.12); margin-bottom: 14px; }"
    ".banner-title-badge { display: inline-flex; align-items: center; gap: 12px; background: #FFFFFF; padding: 8px 24px; border-radius: 50px; color: #D97706; font-weight: 900; font-size: 1.85rem; box-shadow: 0 4px 16px rgba(217, 119, 6, 0.15); border: 2px solid #FDE68A; margin-bottom: 6px; }"
    ".banner-sub-title { font-size: 0.95rem; font-weight: 800; color: #0284C7; margin-bottom: 8px; letter-spacing: 0.05em; }"
    ".search-title-text { font-size: 1.05rem; font-weight: 900; color: #0284C7; text-align: center; margin: 14px 0 8px 0; }"
    "div[data-baseweb='input'] { border-radius: 14px !important; border: 2px solid #38BDF8 !important; background-color: #FFFFFF !important; }"
    ".alert-card { border-radius: 20px; padding: 14px 18px; margin-bottom: 16px; text-align: center; color: white; font-weight: 900; box-shadow: 0 6px 18px rgba(0,0,0,0.1); }"
    ".alert-lvl-1 { background: linear-gradient(135deg, #0284C7 0%, #38BDF8 100%); border: 3px solid #7DD3FC; }"
    ".alert-lvl-2 { background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%); border: 3px solid #FDE68A; }"
    ".alert-lvl-3 { background: linear-gradient(135deg, #EA580C 0%, #F97316 100%); border: 3px solid #FFEDD5; }"
    ".alert-lvl-4 { background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%); border: 3px solid #FCA5A5; }"
    ".alert-lvl-5 { background: linear-gradient(135deg, #4C1D95 0%, #1E1B4B 100%); border: 3px solid #DDD6FE; }"
    ".alert-title { font-size: 1.3rem; letter-spacing: 0.04em; margin-bottom: 4px; }"
    ".alert-action { font-size: 0.95rem; background: rgba(255,255,255,0.22); padding: 5px 14px; border-radius: 50px; display: inline-block; margin-top: 4px; }"
    ".alert-raw-msg { font-size: 0.8rem; margin-top: 8px; opacity: 0.95; font-weight: 700; }"
    ".nav-card-box { background: #FFFFFF; border-radius: 24px; padding: 20px; border: 3px solid #38BDF8; box-shadow: 0 8px 20px rgba(56, 189, 248, 0.15); height: 100%; }"
    ".current-pos-badge { background: #E0F2FE; color: #0284C7; font-size: 0.82rem; font-weight: 900; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 6px; }"
    ".current-pos-name { font-size: 1.05rem; font-weight: 900; color: #1E293B; margin-bottom: 12px; border-bottom: 1px dashed #BAE6FD; padding-bottom: 8px; }"
    ".target-shelter-badge { background: #10B981; color: #FFFFFF; font-size: 0.82rem; font-weight: 900; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 6px; }"
    ".dest-shelter-title { font-size: 1.5rem; font-weight: 900; color: #047857; margin: 2px 0; }"
    ".dest-shelter-sub { font-size: 0.88rem; color: #475569; font-weight: 800; margin-bottom: 10px; }"
    ".route-info-pill { background-color: #ECFDF5; color: #065F46; padding: 7px 14px; border-radius: 50px; font-weight: 900; font-size: 0.9rem; display: inline-block; border: 1.5px solid #A7F3D0; margin-bottom: 12px; }"
    ".gmap-btn { display: block; width: 100%; background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: #FFFFFF !important; text-align: center; font-weight: 900; padding: 11px 16px; border-radius: 14px; text-decoration: none; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25); font-size: 0.95rem; margin-top: 6px; }"
    ".gmap-btn:hover { opacity: 0.92; }"
    ".yellow-card { background: #FFFDF0; border-radius: 24px; padding: 20px; border: 3px solid #FDE68A; box-shadow: 0 8px 20px rgba(253, 230, 138, 0.25); height: 100%; }"
    ".yellow-card-title { color: #D97706; font-weight: 900; font-size: 1.12rem; margin-bottom: 12px; border-bottom: 2px dashed #FDE68A; padding-bottom: 6px; }"
    ".yellow-card-item { font-size: 0.88rem; margin-bottom: 10px; color: #334155; font-weight: 800; line-height: 1.5; }"
    ".map-title-bar { font-size: 1.2rem; font-weight: 900; color: #E11D48; margin: 20px 0 10px 0; }"
    ".contact-card-box { background: #FFFFFF; border-radius: 24px; padding: 20px; border: 2px solid #E2E8F0; margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); }"
    ".contact-card-title { text-align: center; font-weight: 900; font-size: 1.05rem; color: #1E293B; margin-bottom: 14px; }"
    ".contact-grid-wrap { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; text-align: center; }"
    ".contact-item-box { background: #F8FAFC; padding: 12px 8px; border-radius: 16px; border: 1px solid #F1F5F9; }"
    ".contact-item-label { font-size: 0.75rem; color: #64748B; font-weight: 800; }"
    ".contact-item-num { font-size: 1.35rem; font-weight: 900; color: #E11D48; margin-top: 2px; }"
    ".footer-note { text-align: center; font-size: 0.78rem; color: #64748B; margin-top: 20px; padding-bottom: 16px; line-height: 1.6; }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SVGパーツ（はちまるキャラクター）
# ---------------------------------------------------------
SVG_HACHIMARU_CHARACTER = (
    '<svg width="52" height="52" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
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
    '<ellipse cx="35" cy="41" rx="3" ry="1.8" fill="#F43F5E" opacity="0.6"/>'
    '<ellipse cx="65" cy="41" rx="3" ry="1.8" fill="#F43F5E" opacity="0.6"/>'
    '<path d="M 28 28 C 28 10, 72 10, 72 28 Z" fill="#10B981"/>'
    '<rect x="24" y="26" width="52" height="4" rx="2" fill="#059669"/>'
    '<path d="M 50 14 L 51.2 17 L 54 15.8 L 52.3 18.7 L 55 20.8 L 51.2 20.4 L 50 23 L 48.8 20.4 L 45 20.8 L 47.7 18.7 L 46 15.8 L 48.8 17 Z" fill="#F59E0B"/>'
    '</svg>'
)

SVG_TOWN_LANDSCAPE = (
    '<svg width="100%" height="40" viewBox="0 0 600 70" preserveAspectRatio="none" fill="none">'
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
# 3. 八王子市全域 主要指定避難所・広域避難場所マスターデータ (25箇所)
# ---------------------------------------------------------
SHELTERS = [
    # 中心部・駅周辺エリア
    {"name": "第一小学校", "sub": "元横山町2-14-3 / 指定避難所", "coords": [35.6590, 139.3390], "cap": "屋内 2,561㎡"},
    {"name": "第三小学校", "sub": "上野町31-1 / 指定避難所", "coords": [35.6510, 139.3320], "cap": "屋内 2,400㎡"},
    {"name": "第四小学校", "sub": "明神町2-15-1 / 指定避難所", "coords": [35.6552, 139.3465], "cap": "屋内 2,671㎡"},
    {"name": "第六小学校", "sub": "本町24-1 / 指定避難所", "coords": [35.6615, 139.3270], "cap": "屋内 2,310㎡"},
    {"name": "第七小学校", "sub": "台町3-25-1 / 指定避難所", "coords": [35.6515, 139.3175], "cap": "屋内 2,450㎡"},
    {"name": "富士森公園", "sub": "台町2-2 / 広域避難場所", "coords": [35.6518, 139.3228], "cap": "屋外 140,000㎡"},
    
    # 北部・加住・丹木・楢原エリア
    {"name": "創価大学", "sub": "丹木町1-236 / 広域避難場所", "coords": [35.6870, 139.3285], "cap": "屋外 192,000㎡"},
    {"name": "加住小・中学校", "sub": "加住町1-191 / 指定避難所", "coords": [35.6828, 139.3361], "cap": "屋内 2,172㎡"},
    {"name": "楢原小学校", "sub": "楢原町140-4 / 指定避難所", "coords": [35.6805, 139.3030], "cap": "屋内 2,818㎡"},
    {"name": "中野北小学校", "sub": "中野山王2-20-1 / 指定避難所", "coords": [35.6725, 139.3260], "cap": "屋内 2,510㎡"},
    {"name": "宇津木台小学校", "sub": "久保山町2-25 / 指定避難所", "coords": [35.6845, 139.3540], "cap": "屋内 2,480㎡"},
    
    # 西部・高尾・浅川・長房エリア
    {"name": "浅川小学校", "sub": "初沢町1232 / 指定避難所", "coords": [35.6395, 139.2810], "cap": "屋内 2,390㎡"},
    {"name": "東浅川小学校", "sub": "東浅川町535 / 指定避難所", "coords": [35.6455, 139.2935], "cap": "屋内 2,420㎡"},
    {"name": "長房小学校", "sub": "長房町454 / 指定避難所", "coords": [35.6610, 139.2940], "cap": "屋内 2,610㎡"},
    {"name": "横山第一小学校", "sub": "並木町15-1 / 指定避難所", "coords": [35.6540, 139.3025], "cap": "屋内 2,530㎡"},
    {"name": "館小・中学校", "sub": "館町1097 / 指定避難所", "coords": [35.6320, 139.2975], "cap": "屋内 2,750㎡"},
    
    # 南部・北野・片倉・みなみ野エリア
    {"name": "北野小学校", "sub": "北野町538-1 / 指定避難所", "coords": [35.6435, 139.3550], "cap": "屋内 2,490㎡"},
    {"name": "由井第一小学校", "sub": "打越町1192 / 指定避難所", "coords": [35.6400, 139.3455], "cap": "屋内 2,380㎡"},
    {"name": "片倉台小学校", "sub": "片倉町1405 / 指定避難所", "coords": [35.6295, 139.3390], "cap": "屋内 2,410㎡"},
    {"name": "みなみ野小学校", "sub": "みなみ野1-13-1 / 指定避難所", "coords": [35.6310, 139.3220], "cap": "屋内 2,890㎡"},
    
    # 南東部・南大沢・堀之内・由木エリア
    {"name": "南大沢小学校", "sub": "南大沢3-18 / 指定避難所", "coords": [35.6165, 139.3765], "cap": "屋内 2,710㎡"},
    {"name": "東京都立大学（南大沢キャンパス）", "sub": "南大沢1-1 / 広域避難場所", "coords": [35.6195, 139.3810], "cap": "屋外 420,000㎡"},
    {"name": "松木小学校", "sub": "松木38-1 / 指定避難所", "coords": [35.6255, 139.3895], "cap": "屋内 2,520㎡"},
    {"name": "由木東小学校", "sub": "鹿島111-1 / 指定避難所", "coords": [35.6345, 139.4050], "cap": "屋内 2,460㎡"},
    {"name": "恩方第一小学校", "sub": "下恩方町1595 / 指定避難所", "coords": [35.6765, 139.2480], "cap": "屋内 2,150㎡"}
]

# ---------------------------------------------------------
# 4. 高速キャッシュ付き API 取得関数群
# ---------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def fetch_hachioji_jma_warning():
    url = "https://www.jma.go.jp/bosai/warning/data/warning/130000.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            data = json.loads(response.read().decode('utf-8'))
            area_types = data.get("areaTypes", []) if isinstance(data, dict) else []
            for area_group in area_types:
                areas = area_group.get("areas", []) if isinstance(area_group, dict) else []
                for area in areas:
                    if isinstance(area, dict) and area.get("code") == "1320100":
                        warnings = area.get("warnings", [])
                        active_warnings = []
                        max_lvl = "レベル1"
                        for w in warnings:
                            if isinstance(w, dict):
                                status = w.get("status", "")
                                if status in ["発表", "継続"]:
                                    name = w.get("name", "")
                                    if name:
                                        active_warnings.append(name)
                                        if "特別警報" in name:
                                            max_lvl = "レベル5"
                                        elif "警報" in name and max_lvl not in ["レベル5"]:
                                            max_lvl = "レベル4"
                                        elif "注意報" in name and max_lvl in ["レベル1"]:
                                            max_lvl = "レベル2"
                        return max_lvl, active_warnings
    except Exception:
        pass
    return "レベル1", []

@st.cache_data(ttl=3600, show_spinner=False)
def get_coords_from_address(address_text):
    default_coords = [35.6558, 139.3389]  # デフォルト: 八王子駅周辺
    if not address_text or address_text == "八王子駅周辺":
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
        with urllib.request.urlopen(req, timeout=1.5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and isinstance(data, list) and len(data) > 0:
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

@st.cache_data(ttl=3600, show_spinner=False)
def get_route_osrm(start_lat, start_lon, end_lat, end_lon, profile='foot'):
    try:
        url = (
            'http://router.project-osrm.org/route/v1/' + profile + '/'
            + str(start_lon) + ',' + str(start_lat) + ';'
            + str(end_lon) + ',' + str(end_lat) + '?overview=full&geometries=geojson'
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, dict) and data.get('routes'):
                route = data['routes'][0]
                geometry = route['geometry']['coordinates']
                route_line = [[lat, lon] for lon, lat in geometry]
                distance_km = route['distance'] / 1000.0
                duration_min = math.ceil(route['duration'] / 60.0)
                return route_line, distance_km, duration_min, False
    except Exception:
        pass
    dist = calculate_distance(start_lat, start_lon, end_lat, end_lon)
    speed = 4.0 if profile == 'foot' else (15.0 if profile == 'cycling' else 30.0)
    walk_min = max(1, math.ceil((dist / speed) * 60))
    return [[start_lat, start_lon], [end_lat, end_lon]], dist, walk_min, True

# ---------------------------------------------------------
# 5. サイドバー
# ---------------------------------------------------------
sidebar_logo_html = (
    '<div class="sidebar-logo-wrap">'
    + SVG_HACHIMARU_CHARACTER +
    '<div><div class="sidebar-logo-title">はちまる</div>'
    '<div class="sidebar-logo-sub">八王子市 防災・避難ナビ</div></div>'
    '</div>'
)
st.sidebar.markdown(sidebar_logo_html, unsafe_allow_html=True)

st.sidebar.markdown(
    '<div class="sidebar-msg-bubble">高尾山からみんなをナビするよ！<br>落ち着いて行動しよう！</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏃‍♂️ 避難手段の選択")
mode_opt = st.sidebar.radio(
    "移動手段を選んでね",
    ('徒歩 (推奨)', '自転車', '車 (緊急時のみ)'),
    index=0
)

# 管理者・訓練用メニューは折りたたみ内に格納（本番公開時の誤操作防止）
with st.sidebar.expander("⚙️ 訓練・テスト表示設定"):
    use_realtime = st.toggle("📡 気象庁API リアルタイム連動", value=True)
    if not use_realtime:
        alert_level = st.selectbox(
            "訓練用 警戒レベル選択",
            [
                "レベル1：早期注意情報（平常）",
                "レベル2：注意報（避難行動確認）",
                "レベル3：高齢者等避難",
                "レベル4：避難指示（全員避難）",
                "レベル5：緊急安全確保"
            ],
            index=3
        )
        selected_lvl_key = alert_level.split("：")[0]
        active_warnings_list = ["訓練用シミュレーション表示中"]
    else:
        realtime_lvl, active_warnings_list = fetch_hachioji_jma_warning()
        selected_lvl_key = realtime_lvl

st.sidebar.markdown('<div style="margin-top: 24px;">' + SVG_TOWN_LANDSCAPE + '</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. ヘッダー＆リアルタイム警戒レベル表示
# ---------------------------------------------------------
header_html = (
    '<div class="main-header-card">'
    '<div class="banner-title-badge">' + SVG_HACHIMARU_CHARACTER + '<span>はちまる</span></div>'
    '<div class="banner-sub-title">八王子市 防災・避難ナビゲーション</div>'
    '<div>' + SVG_TOWN_LANDSCAPE + '</div>'
    '</div>'
)
st.markdown(header_html, unsafe_allow_html=True)

alert_info = {
    "レベル1": {
        "class": "alert-lvl-1",
        "title": "🔵 警戒レベル 1：現在、八王子市に大きな警戒発表はありません（平常）",
        "action": "最新の気象情報や、いざという時の避難経路を確認しておきましょう。"
    },
    "レベル2": {
        "class": "alert-lvl-2",
        "title": "🟡 警戒レベル 2：注意報が発表されています（避難行動確認）",
        "action": "ハザードマップで避難経路や非常持ち出し品を再確認してください。"
    },
    "レベル3": {
        "class": "alert-lvl-3",
        "title": "🟠 警戒レベル 3：高齢者等避難（警報発表中）",
        "action": "高齢者や移動に時間のかかる方は危険な場所から避難を開始してください！"
    },
    "レベル4": {
        "class": "alert-lvl-4",
        "title": "🔴 警戒レベル 4：避難指示（全員危険箇所から避難）",
        "action": "対象地域の方は速やかに全員指定避難所へ避難を開始してください！"
    },
    "レベル5": {
        "class": "alert-lvl-5",
        "title": "🟣 警戒レベル 5：緊急安全確保（特別警報発表中）",
        "action": "命の危険が迫っています！高い場所へ移動するなど直ちに安全を確保してください！"
    }
}

curr_alert = alert_info.get(selected_lvl_key, alert_info["レベル1"])
warning_detail_str = " / ".join(active_warnings_list) if active_warnings_list else "特記事項なし（発表なし）"

alert_card_html = (
    '<div class="alert-card ' + curr_alert["class"] + '">'
    '<div class="alert-title">' + curr_alert["title"] + '</div>'
    '<div class="alert-action">' + curr_alert["action"] + '</div>'
    '<div class="alert-raw-msg">📡 八王子市の現在の気象発表: ' + warning_detail_str + '</div>'
    '</div>'
)
st.markdown(alert_card_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 現在地取得（オンデマンドGPS）と住所検索エリア
# ---------------------------------------------------------
st.markdown('<div class="search-title-text">📍 いまどこにいる？（住所・駅名入力 または GPSボタン）</div>', unsafe_allow_html=True)

if "gps_active" not in st.session_state:
    st.session_state.gps_active = False

col_input, col_gps_btn = st.columns([3, 1])

with col_input:
    user_address_input = st.text_input(
        "現在地入力フォーム",
        value="",
        placeholder="例：八王子駅、丹木町1丁目、南大沢、高尾 など",
        label_visibility="collapsed"
    )
    if user_address_input.strip():
        st.session_state.gps_active = False

with col_gps_btn:
    if st.button("📡 GPSで現在地取得", use_container_width=True):
        st.session_state.gps_active = True

current_coords = None
display_address = ""

if st.session_state.gps_active and HAS_GPS_LIB:
    location = get_geolocation()
    if location and isinstance(location, dict) and 'coords' in location:
        lat = location['coords']['latitude']
        lon = location['coords']['longitude']
        current_coords = [lat, lon]
        display_address = "現在地（GPS自動取得）"
        st.success("📍 GPSで現在地を取得しました！")
    else:
        st.info("⏳ ブラウザの位置情報許可を待っています...（許可されない場合は左の欄に住所を入力してください）")

if current_coords is None:
    display_address = user_address_input if user_address_input.strip() else "八王子駅周辺"
    current_coords = get_coords_from_address(display_address)

# ---------------------------------------------------------
# 8. 最寄り避難所（上位3件）計算＆ルート検索
# ---------------------------------------------------------
shelters_with_dist = []
for shelter in SHELTERS:
    dist = calculate_distance(current_coords[0], current_coords[1], shelter["coords"][0], shelter["coords"][1])
    shelters_with_dist.append((dist, shelter))

shelters_with_dist.sort(key=lambda x: x[0])
top3_shelters = [item[1] for item in shelters_with_dist[:3]]

# 候補選択UI（第1候補が満員・通行止めの場合に備える）
shelter_options = [f"第{i+1}候補：{s['name']}（直線約{round(shelters_with_dist[i][0], 1)}km）" for i, s in enumerate(top3_shelters)]
selected_shelter_idx = st.selectbox(
    "避難先候補を選択（混雑や通行止め時は第2・第3候補へ切り替え可能）",
    range(len(top3_shelters)),
    format_func=lambda idx: shelter_options[idx]
)
target_shelter = top3_shelters[selected_shelter_idx]

mode_map = {'徒歩 (推奨)': 'foot', '自転車': 'cycling', '車 (緊急時のみ)': 'driving'}
gmap_mode_map = {'徒歩 (推奨)': 'walking', '自転車': 'bicycling', '車 (緊急時のみ)': 'driving'}
mode_profile = mode_map[mode_opt]

route_line, real_dist, real_minutes, is_fallback = get_route_osrm(
    current_coords[0], current_coords[1],
    target_shelter["coords"][0], target_shelter["coords"][1],
    mode_profile
)
mode_label = mode_opt.split(' ')[0]

# Googleマップ外部ナビ起動URL生成
gmap_url = (
    f"https://www.google.com/maps/dir/?api=1"
    f"&origin={current_coords[0]},{current_coords[1]}"
    f"&destination={target_shelter['coords'][0]},{target_shelter['coords'][1]}"
    f"&travelmode={gmap_mode_map[mode_opt]}"
)

col1, col2 = st.columns([1.3, 0.7])
with col1:
    nav_html = (
        '<div class="nav-card-box">'
        '<div class="current-pos-badge">📍 現在の検索位置</div>'
        '<div class="current-pos-name">' + display_address + '</div>'
        '<div class="target-shelter-badge">🏃‍♂️ 選択中の避難所（第' + str(selected_shelter_idx + 1) + '候補）</div>'
        '<div class="dest-shelter-title">' + target_shelter["name"] + '</div>'
        '<div class="dest-shelter-sub">所在地・区分：' + target_shelter["sub"] + '（' + target_shelter["cap"] + '）</div>'
        '<div><span class="route-info-pill">' + mode_label + 'ルート：約 ' + str(round(real_dist, 1)) + ' km / 約 ' + str(real_minutes) + ' 分</span></div>'
        '<a href="' + gmap_url + '" target="_blank" class="gmap-btn">🧭 スマホの地図アプリでナビを開始する</a>'
        '</div>'
    )
    st.markdown(nav_html, unsafe_allow_html=True)

with col2:
    yellow_html = (
        '<div class="yellow-card">'
        '<div class="yellow-card-title">避難時のワンポイント</div>'
        '<div class="yellow-card-item"><b>履物</b>：増水時の長靴は危険！履き慣れたスニーカーで。</div>'
        '<div class="yellow-card-item"><b>荷物</b>：両手が空くようにリュックで移動しよう。</div>'
        '<div class="yellow-card-item"><b>垂直避難</b>：外がすでに危険な場合は2階以上へ！</div>'
        '</div>'
    )
    st.markdown(yellow_html, unsafe_allow_html=True)

st.markdown('<div class="map-title-bar">🗺️ 八王子市 避難ルートマップ（周辺候補も表示）</div>', unsafe_allow_html=True)

m = folium.Map(location=current_coords, zoom_start=14, tiles="OpenStreetMap")

# 現在地マーカー
folium.Marker(
    location=current_coords,
    popup="現在地: " + display_address,
    tooltip="現在地",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

# 上位3避難所マーカー（選択中は緑、それ以外は青）
for idx, s in enumerate(top3_shelters):
    is_selected = (idx == selected_shelter_idx)
    folium.Marker(
        location=s["coords"],
        popup=f"第{idx+1}候補: {s['name']} ({s['cap']})",
        tooltip=f"第{idx+1}候補: {s['name']}",
        icon=folium.Icon(color="green" if is_selected else "blue", icon="home")
    ).add_to(m)

# ルート線描画
folium.PolyLine(
    locations=route_line,
    color="#00A86B",
    weight=6,
    opacity=0.85,
    dash_array="6, 6" if is_fallback else None,
    tooltip=mode_label + "避難ルート"
).add_to(m)

st_folium(m, width="100%", height=440, returned_objects=[])

# ---------------------------------------------------------
# 9. 緊急連絡先＆免責フッターエリア
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
    '<div class="footer-note">'
    '※本サービスは気象庁防災情報JSONおよびオープンデータをもとに避難行動を支援するものです。<br>'
    '※実際の災害発生時は、八王子市公式防災情報・防災行政無線の指示に従って安全に行動してください。'
    '</div>'
)
st.markdown(contact_html, unsafe_allow_html=True)
