import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request
import math
import re

# オプショナルインポート（自動GPS機能用）
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

# CSS設定
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
    ".search-title-text { font-size: 1.02rem; font-weight: 900; color: #0284C7; text-align: center; margin: 12px 0 6px 0; }"
    "div[data-baseweb='input'] { border-radius: 14px !important; border: 2px solid #38BDF8 !important; background-color: #FFFFFF !important; }"
    ".alert-card { border-radius: 20px; padding: 14px 18px; margin-bottom: 16px; text-align: center; color: white; font-weight: 900; box-shadow: 0 6px 18px rgba(0,0,0,0.1); }"
    ".alert-lvl-1 { background: linear-gradient(135deg, #0284C7 0%, #38BDF8 100%); border: 3px solid #7DD3FC; }"
    ".alert-lvl-2 { background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%); border: 3px solid #FDE68A; }"
    ".alert-lvl-3 { background: linear-gradient(135deg, #EA580C 0%, #F97316 100%); border: 3px solid #FFEDD5; }"
    ".alert-lvl-4 { background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%); border: 3px solid #FCA5A5; }"
    ".alert-lvl-5 { background: linear-gradient(135deg, #4C1D95 0%, #1E1B4B 100%); border: 3px solid #DDD6FE; }"
    ".alert-title { font-size: 1.25rem; letter-spacing: 0.04em; margin-bottom: 4px; }"
    ".alert-action { font-size: 0.92rem; background: rgba(255,255,255,0.22); padding: 5px 14px; border-radius: 50px; display: inline-block; margin-top: 4px; }"
    ".alert-raw-msg { font-size: 0.78rem; margin-top: 8px; opacity: 0.95; font-weight: 700; }"
    ".nav-card-box { background: #FFFFFF; border-radius: 24px; padding: 18px 20px; border: 3px solid #38BDF8; box-shadow: 0 8px 20px rgba(56, 189, 248, 0.15); height: 100%; }"
    ".current-pos-badge { background: #E0F2FE; color: #0284C7; font-size: 0.8rem; font-weight: 900; padding: 3px 10px; border-radius: 10px; display: inline-block; margin-bottom: 4px; }"
    ".current-pos-name { font-size: 1.0rem; font-weight: 900; color: #1E293B; margin-bottom: 10px; border-bottom: 1px dashed #BAE6FD; padding-bottom: 6px; }"
    ".target-shelter-badge { background: #059669; color: #FFFFFF; font-size: 0.8rem; font-weight: 900; padding: 3px 10px; border-radius: 10px; display: inline-block; margin-bottom: 4px; }"
    ".dest-shelter-title { font-size: 1.45rem; font-weight: 900; color: #047857; margin: 2px 0; }"
    ".dest-shelter-sub { font-size: 0.86rem; color: #475569; font-weight: 800; margin-bottom: 10px; }"
    ".route-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 8px; }"
    "@media (max-width: 640px) { .route-grid { grid-template-columns: 1fr; } }"
    ".route-card-1 { background: #ECFDF5; border: 2.5px solid #00A859; border-radius: 14px; padding: 10px; }"
    ".route-card-2 { background: #EFF6FF; border: 2.5px solid #0055FF; border-radius: 14px; padding: 10px; }"
    ".route-card-3 { background: #FFF1F2; border: 2.5px solid #E11D48; border-radius: 14px; padding: 10px; }"
    ".route-badge-1 { background: #00A859; color: white; font-size: 0.72rem; font-weight: 900; padding: 2px 8px; border-radius: 8px; display: inline-block; }"
    ".route-badge-2 { background: #0055FF; color: white; font-size: 0.72rem; font-weight: 900; padding: 2px 8px; border-radius: 8px; display: inline-block; }"
    ".route-badge-3 { background: #E11D48; color: white; font-size: 0.72rem; font-weight: 900; padding: 2px 8px; border-radius: 8px; display: inline-block; }"
    ".route-metric { font-size: 1.05rem; font-weight: 900; color: #0F172A; margin-top: 4px; }"
    ".route-desc { font-size: 0.75rem; color: #475569; font-weight: 700; margin-top: 2px; }"
    ".yellow-card { background: #FFFDF0; border-radius: 24px; padding: 18px 20px; border: 3px solid #FDE68A; box-shadow: 0 8px 20px rgba(253, 230, 138, 0.25); height: 100%; }"
    ".yellow-card-title { color: #D97706; font-weight: 900; font-size: 1.1rem; margin-bottom: 10px; border-bottom: 2px dashed #FDE68A; padding-bottom: 6px; }"
    ".yellow-card-item { font-size: 0.85rem; margin-bottom: 8px; color: #334155; font-weight: 800; line-height: 1.45; }"
    ".map-title-bar { font-size: 1.18rem; font-weight: 900; color: #E11D48; margin: 18px 0 8px 0; }"
    ".map-legend-bar { background: #FFFFFF; border: 2px solid #94A3B8; border-radius: 14px; padding: 10px 14px; font-size: 0.86rem; font-weight: 900; color: #0F172A; margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }"
    ".legend-line-1 { display: inline-block; width: 26px; height: 7px; background: #00A859; border: 1.5px solid #0F172A; border-radius: 4px; vertical-align: middle; margin-right: 4px; }"
    ".legend-line-2 { display: inline-block; width: 26px; height: 7px; background: #0055FF; border: 1.5px solid #0F172A; border-radius: 4px; vertical-align: middle; margin-right: 4px; }"
    ".legend-line-3 { display: inline-block; width: 26px; height: 7px; background: #E11D48; border: 1.5px solid #0F172A; border-radius: 4px; vertical-align: middle; margin-right: 4px; }"
    ".contact-card-box { background: #FFFFFF; border-radius: 24px; padding: 18px; border: 2px solid #E2E8F0; margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); }"
    ".contact-card-title { text-align: center; font-weight: 900; font-size: 1.02rem; color: #1E293B; margin-bottom: 12px; }"
    ".contact-grid-wrap { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; text-align: center; }"
    ".contact-item-box { background: #F8FAFC; padding: 10px 8px; border-radius: 16px; border: 1px solid #F1F5F9; }"
    ".contact-item-label { font-size: 0.74rem; color: #64748B; font-weight: 800; }"
    ".contact-item-num { font-size: 1.3rem; font-weight: 900; color: #E11D48; margin-top: 2px; }"
    ".footer-note { text-align: center; font-size: 0.76rem; color: #64748B; margin-top: 16px; padding-bottom: 16px; line-height: 1.5; }"
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
    '<svg width="100%" height="38" viewBox="0 0 600 70" preserveAspectRatio="none" fill="none">'
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
# 3. 八王子市全域 主要指定避難所・ランドマーク内蔵データベース
# ---------------------------------------------------------
LOCAL_LANDMARKS = {
    "八王子駅": [35.6558, 139.3389],
    "八王子": [35.6558, 139.3389],
    "京王八王子": [35.6580, 139.3435],
    "西八王子": [35.6565, 139.3125],
    "高尾駅": [35.6421, 139.2823],
    "高尾": [35.6421, 139.2823],
    "高尾山口": [35.6323, 139.2700],
    "南大沢": [35.6138, 139.3792],
    "北野": [35.6444, 139.3547],
    "片倉": [35.6353, 139.3411],
    "みなみ野": [35.6311, 139.3308],
    "八王子みなみ野": [35.6311, 139.3308],
    "長沼": [35.6478, 139.3658],
    "平山城址公園": [35.6475, 139.3800],
    "堀之内": [35.6236, 139.3933],
    "京王堀之内": [35.6236, 139.3933],
    "山田": [35.6422, 139.3278],
    "めじろ台": [35.6347, 139.3075],
    "狭間": [35.6350, 139.2933],
    "丹木町": [35.6881, 139.3275],
    "創価大学": [35.6870, 139.3285],
    "東京都立大学": [35.6195, 139.3810],
    "工学院大学": [35.6875, 139.3180],
    "中央大学": [35.6425, 139.4045],
    "帝京大学": [35.6350, 139.4125],
    "八王子市役所": [35.6663, 139.3160]
}

SHELTERS = [
    {"name": "第一小学校", "sub": "元横山町2-14-3 / 指定避難所", "coords": [35.6590, 139.3390], "cap": "屋内 2,561㎡"},
    {"name": "第三小学校", "sub": "上野町31-1 / 指定避難所", "coords": [35.6510, 139.3320], "cap": "屋内 2,400㎡"},
    {"name": "第四小学校", "sub": "明神町2-15-1 / 指定避難所", "coords": [35.6552, 139.3465], "cap": "屋内 2,671㎡"},
    {"name": "第六小学校", "sub": "本町24-1 / 指定避難所", "coords": [35.6615, 139.3270], "cap": "屋内 2,310㎡"},
    {"name": "第七小学校", "sub": "台町3-25-1 / 指定避難所", "coords": [35.6515, 139.3175], "cap": "屋内 2,450㎡"},
    {"name": "富士森公園", "sub": "台町2-2 / 広域避難場所", "coords": [35.6518, 139.3228], "cap": "屋外 140,000㎡"},
    {"name": "創価大学", "sub": "丹木町1-236 / 広域避難場所", "coords": [35.6870, 139.3285], "cap": "屋外 192,000㎡"},
    {"name": "加住小・中学校", "sub": "加住町1-191 / 指定避難所", "coords": [35.6828, 139.3361], "cap": "屋内 2,172㎡"},
    {"name": "楢原小学校", "sub": "楢原町140-4 / 指定避難所", "coords": [35.6805, 139.3030], "cap": "屋内 2,818㎡"},
    {"name": "中野北小学校", "sub": "中野山王2-20-1 / 指定避難所", "coords": [35.6725, 139.3260], "cap": "屋内 2,510㎡"},
    {"name": "宇津木台小学校", "sub": "久保山町2-25 / 指定避難所", "coords": [35.6845, 139.3540], "cap": "屋内 2,480㎡"},
    {"name": "浅川小学校", "sub": "初沢町1232 / 指定避難所", "coords": [35.6395, 139.2810], "cap": "屋内 2,390㎡"},
    {"name": "東浅川小学校", "sub": "東浅川町535 / 指定避難所", "coords": [35.6455, 139.2935], "cap": "屋内 2,420㎡"},
    {"name": "長房小学校", "sub": "長房町454 / 指定避難所", "coords": [35.6610, 139.2940], "cap": "屋内 2,610㎡"},
    {"name": "横山第一小学校", "sub": "並木町15-1 / 指定避難所", "coords": [35.6540, 139.3025], "cap": "屋内 2,530㎡"},
    {"name": "館小・中学校", "sub": "館町1097 / 指定避難所", "coords": [35.6320, 139.2975], "cap": "屋内 2,750㎡"},
    {"name": "北野小学校", "sub": "北野町538-1 / 指定避難所", "coords": [35.6435, 139.3550], "cap": "屋内 2,490㎡"},
    {"name": "由井第一小学校", "sub": "打越町1192 / 指定避難所", "coords": [35.6400, 139.3455], "cap": "屋内 2,380㎡"},
    {"name": "片倉台小学校", "sub": "片倉町1405 / 指定避難所", "coords": [35.6295, 139.3390], "cap": "屋内 2,410㎡"},
    {"name": "みなみ野小学校", "sub": "みなみ野1-13-1 / 指定避難所", "coords": [35.6310, 139.3220], "cap": "屋内 2,890㎡"},
    {"name": "南大沢小学校", "sub": "南大沢3-18 / 指定避難所", "coords": [35.6165, 139.3765], "cap": "屋内 2,710㎡"},
    {"name": "東京都立大学（南大沢キャンパス）", "sub": "南大沢1-1 / 広域避難場所", "coords": [35.6195, 139.3810], "cap": "屋外 420,000㎡"},
    {"name": "松木小学校", "sub": "松木38-1 / 指定避難所", "coords": [35.6255, 139.3895], "cap": "屋内 2,520㎡"},
    {"name": "由木東小学校", "sub": "鹿島111-1 / 指定避難所", "coords": [35.6345, 139.4050], "cap": "屋内 2,460㎡"},
    {"name": "恩方第一小学校", "sub": "下恩方町1595 / 指定避難所", "coords": [35.6765, 139.2480], "cap": "屋内 2,150㎡"}
]

# ---------------------------------------------------------
# 4. 高耐久データ処理＆3系統避難ルート生成エンジン
# ---------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def fetch_hachioji_jma_warning():
    url = "https://www.jma.go.jp/bosai/warning/data/warning/130000.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.2) as response:
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

@st.cache_data(ttl=86400, show_spinner=False)
def get_coords_from_address(address_text):
    default_coords = [35.6558, 139.3389]
    if not address_text:
        return default_coords

    cleaned = address_text.strip()
    for key, coords in LOCAL_LANDMARKS.items():
        if key in cleaned:
            return coords

    try:
        cleaned_text = cleaned.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        cleaned_text = re.sub(r'[\d\-－丁目番号]+$', '', cleaned_text).strip()
        search_query = cleaned_text if cleaned_text else address_text
        if "八王子" not in search_query:
            search_query = "東京都八王子市 " + search_query

        url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" + urllib.parse.quote(search_query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.2) as response:
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

def _fetch_single_osrm(coords_list, profile):
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coords_list])
    url = f"http://router.project-osrm.org/route/v1/{profile}/{coord_str}?overview=full&geometries=geojson&alternatives=true"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=1.5) as response:
        return json.loads(response.read().decode('utf-8'))

@st.cache_data(ttl=3600, show_spinner=False)
def get_three_evacuation_routes(start_lat, start_lon, end_lat, end_lon, profile='foot'):
    speed = 4.0 if profile == 'foot' else (15.0 if profile == 'cycling' else 25.0)
    routes_result = []

    mid_lat = (start_lat + end_lat) / 2.0
    mid_lon = (start_lon + end_lon) / 2.0
    dlat = end_lat - start_lat
    dlon = end_lon - start_lon
    norm = math.sqrt(dlat**2 + dlon**2)
    if norm < 0.0005:
        norm = 0.0005
    offset = 0.0038
    perp_lat = (-dlon / norm) * offset
    perp_lon = (dlat / norm) * offset

    wp_left = [mid_lat + perp_lat, mid_lon + perp_lon]
    wp_right = [mid_lat - perp_lat, mid_lon - perp_lon]

    try:
        data_main = _fetch_single_osrm([[start_lat, start_lon], [end_lat, end_lon]], profile)
        if isinstance(data_main, dict) and data_main.get('routes'):
            r0 = data_main['routes'][0]
            line0 = [[lat, lon] for lon, lat in r0['geometry']['coordinates']]
            dist0 = r0['distance'] / 1000.0
            min0 = max(1, math.ceil(r0['duration'] / 60.0))
            routes_result.append({
                "name": "ルート① 最短メイン経路",
                "desc": "最も距離が短い基本ルート",
                "line": line0,
                "dist": dist0,
                "min": min0,
                "color": "#00A859"
            })

            if len(data_main['routes']) > 1:
                r1 = data_main['routes'][1]
                line1 = [[lat, lon] for lon, lat in r1['geometry']['coordinates']]
                dist1 = r1['distance'] / 1000.0
                min1 = max(1, math.ceil(r1['duration'] / 60.0))
                routes_result.append({
                    "name": "ルート② 別通り迂回経路",
                    "desc": "メイン通り通行止め時の別ルート",
                    "line": line1,
                    "dist": dist1,
                    "min": min1,
                    "color": "#0055FF"
                })
            else:
                data_left = _fetch_single_osrm([[start_lat, start_lon], wp_left, [end_lat, end_lon]], profile)
                if data_left.get('routes'):
                    rl = data_left['routes'][0]
                    routes_result.append({
                        "name": "ルート② 北・西側迂回経路",
                        "desc": "大通り・高台側へ大きく回る経路",
                        "line": [[lat, lon] for lon, lat in rl['geometry']['coordinates']],
                        "dist": rl['distance'] / 1000.0,
                        "min": max(1, math.ceil(rl['duration'] / 60.0)),
                        "color": "#0055FF"
                    })

            data_right = _fetch_single_osrm([[start_lat, start_lon], wp_right, [end_lat, end_lon]], profile)
            if data_right.get('routes'):
                rr = data_right['routes'][0]
                routes_result.append({
                    "name": "ルート③ 南・東側迂回経路",
                    "desc": "逆方向から安全に回り込む経路",
                    "line": [[lat, lon] for lon, lat in rr['geometry']['coordinates']],
                    "dist": rr['distance'] / 1000.0,
                    "min": max(1, math.ceil(rr['duration'] / 60.0)),
                    "color": "#E11D48"
                })
    except Exception:
        pass

    base_dist = calculate_distance(start_lat, start_lon, end_lat, end_lon) * 1.25
    if len(routes_result) < 1:
        routes_result.append({
            "name": "ルート① 最短メイン経路",
            "desc": "直線方向の最短基準ルート",
            "line": [[start_lat, start_lon], [end_lat, end_lon]],
            "dist": base_dist,
            "min": max(1, math.ceil((base_dist / speed) * 60)),
            "color": "#00A859"
        })
    if len(routes_result) < 2:
        d_left = (
            calculate_distance(start_lat, start_lon, wp_left[0], wp_left[1])
            + calculate_distance(wp_left[0], wp_left[1], end_lat, end_lon)
        ) * 1.2
        routes_result.append({
            "name": "ルート② 北・西側迂回経路",
            "desc": "冠水・倒壊箇所を避ける北西側迂回",
            "line": [[start_lat, start_lon], wp_left, [end_lat, end_lon]],
            "dist": d_left,
            "min": max(1, math.ceil((d_left / speed) * 60)),
            "color": "#0055FF"
        })
    if len(routes_result) < 3:
        d_right = (
            calculate_distance(start_lat, start_lon, wp_right[0], wp_right[1])
            + calculate_distance(wp_right[0], wp_right[1], end_lat, end_lon)
        ) * 1.2
        routes_result.append({
            "name": "ルート③ 南・東側迂回経路",
            "desc": "別方向から避難所へ入る南東側迂回",
            "line": [[start_lat, start_lon], wp_right, [end_lat, end_lon]],
            "dist": d_right,
            "min": max(1, math.ceil((d_right / speed) * 60)),
            "color": "#E11D48"
        })

    return routes_result[:3]

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
    '<div class="sidebar-msg-bubble">住所がわからなくても大丈夫！<br>3つの避難ルートから安全な道を選ぼう！</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏃‍♂️ 避難手段の選択")
mode_opt = st.sidebar.radio(
    "移動手段を選んでね",
    ('徒歩 (推奨)', '自転車', '車 (緊急時のみ)'),
    index=0
)

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
        "action": "最新の気象情報や、3つの避難経路を事前に確認しておきましょう。"
    },
    "レベル2": {
        "class": "alert-lvl-2",
        "title": "🟡 警戒レベル 2：注意報が発表されています（避難行動確認）",
        "action": "複数の避難ルートを確認し、非常持ち出し品を準備してください。"
    },
    "レベル3": {
        "class": "alert-lvl-3",
        "title": "🟠 警戒レベル 3：高齢者等避難（警報発表中）",
        "action": "高齢者や移動に時間のかかる方は危険な場所から避難を開始してください！"
    },
    "レベル4": {
        "class": "alert-lvl-4",
        "title": "🔴 警戒レベル 4：避難指示（全員危険箇所から避難）",
        "action": "周囲の冠水・倒壊に注意し、安全なルートで速やかに避難してください！"
    },
    "レベル5": {
        "class": "alert-lvl-5",
        "title": "🟣 警戒レベル 5：緊急安全確保（特別警報発表中）",
        "action": "命の危険が迫っています！無理な移動を避け高い場所へ避難してください！"
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
# 7. 自動GPS測位 ＋ 地図タップ地点指定 ＋ 任意検索
# ---------------------------------------------------------
if "manual_pin" not in st.session_state:
    st.session_state.manual_pin = None

st.markdown('<div class="search-title-text">📍 住所がわからなくてもOK（現在地を自動表示／地図タップでも地点指定可能）</div>', unsafe_allow_html=True)

user_address_input = st.text_input(
    "出発地入力フォーム",
    value="",
    placeholder="別の場所を調べたい時だけ入力（例：八王子駅、高尾駅、南大沢 など）",
    label_visibility="collapsed"
)

if user_address_input.strip():
    st.session_state.manual_pin = None

current_coords = None
display_address = ""

if st.session_state.manual_pin is not None and not user_address_input.strip():
    current_coords = st.session_state.manual_pin
    display_address = f"地図上で指定した出発地点（緯度 {current_coords[0]:.4f}, 経度 {current_coords[1]:.4f}）"

if current_coords is None and not user_address_input.strip() and HAS_GPS_LIB:
    try:
        location = get_geolocation()
        if location and isinstance(location, dict) and 'coords' in location:
            lat = location['coords']['latitude']
            lon = location['coords']['longitude']
            current_coords = [lat, lon]
            display_address = f"現在地（自動測位：緯度 {lat:.4f}, 経度 {lon:.4f}）"
    except Exception:
        pass

if current_coords is None:
    if user_address_input.strip():
        display_address = user_address_input.strip()
        current_coords = get_coords_from_address(display_address)
    else:
        display_address = "八王子駅周辺（地図をタップするとその場所を出発地にできます）"
        current_coords = [35.6558, 139.3389]

# ---------------------------------------------------------
# 8. 最寄り避難所（上位3件）＆ 3系統マルチ避難ルート計算
# ---------------------------------------------------------
shelters_with_dist = []
for shelter in SHELTERS:
    dist = calculate_distance(current_coords[0], current_coords[1], shelter["coords"][0], shelter["coords"][1])
    shelters_with_dist.append((dist, shelter))

shelters_with_dist.sort(key=lambda x: x[0])
top3_shelters = [item[1] for item in shelters_with_dist[:3]]

col_sel1, col_sel2 = st.columns([1.2, 0.8])
with col_sel1:
    shelter_options = [f"避難先候補{i+1}：{s['name']}（約{round(shelters_with_dist[i][0] * 1.25, 1)}km）" for i, s in enumerate(top3_shelters)]
    selected_shelter_idx = st.selectbox(
        "避難先の避難所を選択（満員・通行止め時は別候補へ切替）",
        range(len(top3_shelters)),
        format_func=lambda idx: shelter_options[idx]
    )
target_shelter = top3_shelters[selected_shelter_idx]

mode_map = {'徒歩 (推奨)': 'foot', '自転車': 'cycling', '車 (緊急時のみ)': 'driving'}
mode_profile = mode_map[mode_opt]

three_routes = get_three_evacuation_routes(
    current_coords[0], current_coords[1],
    target_shelter["coords"][0], target_shelter["coords"][1],
    mode_profile
)

with col_sel2:
    route_choice_idx = st.selectbox(
        "強調表示するルートを選択",
        [0, 1, 2],
        format_func=lambda idx: f"{three_routes[idx]['name']}（約{three_routes[idx]['min']}分）"
    )

col1, col2 = st.columns([1.35, 0.65])
with col1:
    r0, r1, r2 = three_routes[0], three_routes[1], three_routes[2]
    nav_html = (
        '<div class="nav-card-box">'
        '<div class="current-pos-badge">📍 出発地点</div>'
        '<div class="current-pos-name">' + display_address + '</div>'
        '<div class="target-shelter-badge">🏃‍♂️ 避難先：' + target_shelter["name"] + '</div>'
        '<div class="dest-shelter-sub">' + target_shelter["sub"] + '（' + target_shelter["cap"] + '）</div>'
        '<div class="route-grid">'
        '<div class="route-card-1">'
        '<span class="route-badge-1">ルート① 最短</span>'
        '<div class="route-metric">約 ' + str(round(r0["dist"], 1)) + ' km / ' + str(r0["min"]) + '分</div>'
        '<div class="route-desc">' + r0["desc"] + '</div>'
        '</div>'
        '<div class="route-card-2">'
        '<span class="route-badge-2">ルート② 迂回A</span>'
        '<div class="route-metric">約 ' + str(round(r1["dist"], 1)) + ' km / ' + str(r1["min"]) + '分</div>'
        '<div class="route-desc">' + r1["desc"] + '</div>'
        '</div>'
        '<div class="route-card-3">'
        '<span class="route-badge-3">ルート③ 迂回B</span>'
        '<div class="route-metric">約 ' + str(round(r2["dist"], 1)) + ' km / ' + str(r2["min"]) + '分</div>'
        '<div class="route-desc">' + r2["desc"] + '</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(nav_html, unsafe_allow_html=True)

with col2:
    yellow_html = (
        '<div class="yellow-card">'
        '<div class="yellow-card-title">3つの道から安全に選ぶコツ</div>'
        '<div class="yellow-card-item"><b>冠水・川沿い回避</b>：低い道が水没していたら②か③の迂回ルートへ！</div>'
        '<div class="yellow-card-item"><b>単独ルート拡大</b>：線が重なって見づらい時は下のスイッチで1本だけ表示できます。</div>'
        '<div class="yellow-card-item"><b>地図タップ変更</b>：地図をタップするとその地点から3ルートを再計算します。</div>'
        '</div>'
    )
    st.markdown(yellow_html, unsafe_allow_html=True)

st.markdown('<div class="map-title-bar">🗺️ 避難ルートマップ</div>', unsafe_allow_html=True)

view_mode = st.radio(
    "地図のルート表示方法",
    ["3ルートすべて同時表示（比較用）", "選択中の1ルートのみくっきり表示（移動用）"],
    horizontal=True
)

legend_html = (
    '<div class="map-legend-bar">'
    '<span>🔴 出発地点</span>'
    '<span>🟢 避難所</span>'
    '<span><i class="legend-line-1"></i>ルート① 最短</span>'
    '<span><i class="legend-line-2"></i>ルート② 迂回A</span>'
    '<span><i class="legend-line-3"></i>ルート③ 迂回B</span>'
    '</div>'
)
st.markdown(legend_html, unsafe_allow_html=True)

center_lat = (current_coords[0] + target_shelter["coords"][0]) / 2.0
center_lon = (current_coords[1] + target_shelter["coords"][1]) / 2.0
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=15,
    tiles="CartoDB Voyager"
)

target_routes_for_bounds = [three_routes[route_choice_idx]] if "1ルートのみ" in view_mode else three_routes
all_lats = [current_coords[0], target_shelter["coords"][0]]
all_lons = [current_coords[1], target_shelter["coords"][1]]
for r in target_routes_for_bounds:
    for pt in r["line"]:
        all_lats.append(pt[0])
        all_lons.append(pt[1])
m.fit_bounds([[min(all_lats), min(all_lons)], [max(all_lats), max(all_lons)]], padding=(40, 40))

folium.Marker(
    location=current_coords,
    popup="出発地点: " + display_address,
    tooltip="出発地点（現在地）",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

for idx, s in enumerate(top3_shelters):
    is_selected = (idx == selected_shelter_idx)
    folium.Marker(
        location=s["coords"],
        popup=f"候補{idx+1}: {s['name']} ({s['cap']})",
        tooltip=f"候補{idx+1}: {s['name']}",
        icon=folium.Icon(color="green" if is_selected else "gray", icon="home")
    ).add_to(m)

if "1ルートのみ" in view_mode:
    indices_to_draw = [route_choice_idx]
else:
    indices_to_draw = [i for i in range(3) if i != route_choice_idx] + [route_choice_idx]

for idx in indices_to_draw:
    r = three_routes[idx]
    is_highlighted = (idx == route_choice_idx)

    folium.PolyLine(
        locations=r["line"],
        color="#0F172A",
        weight=16 if is_highlighted else 9,
        opacity=0.95 if is_highlighted else 0.55
    ).add_to(m)

    folium.PolyLine(
        locations=r["line"],
        color="#FFFFFF",
        weight=12 if is_highlighted else 6.5,
        opacity=1.0 if is_highlighted else 0.75
    ).add_to(m)

    folium.PolyLine(
        locations=r["line"],
        color=r["color"],
        weight=8 if is_highlighted else 4,
        opacity=1.0 if is_highlighted else 0.85,
        tooltip=f"【{r['name']}】約{round(r['dist'], 1)}km / 約{r['min']}分"
    ).add_to(m)

map_data = st_folium(m, width="100%", height=480, returned_objects=["last_clicked"])

if map_data and map_data.get("last_clicked"):
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lon = map_data["last_clicked"]["lng"]
    prev_pin = st.session_state.manual_pin
    if prev_pin is None or (abs(prev_pin[0] - clicked_lat) > 0.0001 or abs(prev_pin[1] - clicked_lon) > 0.0001):
        st.session_state.manual_pin = [clicked_lat, clicked_lon]
        st.rerun()

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
    '※本サービスは気象庁防災情報JSONおよびオープンデータをもとに避難経路を確認できる防災支援システムです。<br>'
    '※実際の災害発生時は、周囲の浸水・倒壊状況および八王子市公式防災情報の指示に従って安全に行動してください。'
    '</div>'
)
st.markdown(contact_html, unsafe_allow_html=True)
