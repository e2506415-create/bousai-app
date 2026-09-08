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

# デザインCSS（絵文字排除・シンプルデザイン）
st.markdown("""
    <style>
    /* 全体背景 */
    .stApp {
        background: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
    }
    
    /* サイドバー */
    [data-testid="stSidebar"] {
        background-color: #E2E8F0 !important;
        border-right: 1px solid #CBD5E1;
    }
    
    /* 左上ロゴエリア */
    .sidebar-logo-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }
    .sidebar-logo-icon {
        background-color: #059669;
        color: #FFFFFF;
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .sidebar-logo-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: #0F172A;
        line-height: 1.1;
    }
    .sidebar-logo-sub {
        font-size: 0.75rem;
        color: #475569;
        font-weight: bold;
        margin-top: 2px;
    }

    /* メインヘッダーバナー */
    .header-banner {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .banner-title {
        color: #0F172A;
        font-weight: 900;
        font-size: 1.5rem;
        margin: 0;
    }

    /* 最寄り避難所案内カード */
    .shelter-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        border: 2px solid #FBCFE8;
        box-shadow: 0 4px 12px rgba(244, 114, 182, 0.08);
        height: 100%;
    }
    .loc-tag {
        color: #334155;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .dest-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: #059669;
        margin: 12px 0 4px 0;
    }
    .dest-sub {
        font-size: 0.85rem;
        color: #059669;
        font-weight: bold;
        margin-bottom: 16px;
    }
    .pill-badge {
        background-color: #ECFDF5;
        color: #047857;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
        display: inline-block;
    }

    /* 移動ワンポイントカード */
    .point-card {
        background: #FFFBEB;
        border-radius: 16px;
        padding: 20px;
        border: 2px solid #FDE68A;
        height: 100%;
    }
    .point-card-title {
        color: #D97706;
        font-weight: 900;
        font-size: 1.1rem;
        margin-bottom: 12px;
    }
    .point-card-item {
        font-size: 0.85rem;
        margin-bottom: 10px;
        color: #334155;
        line-height: 1.5;
    }

    /* 地図セクションタイトル */
    .section-title {
        font-size: 1.2rem;
        font-weight: 900;
        color: #0F172A;
        margin: 24px 0 12px 0;
    }

    /* 緊急電話番号エリア */
    .contact-card-box {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        margin-top: 24px;
    }
    .contact-card-title {
        text-align: center;
        font-weight: 900;
        font-size: 1.0rem;
        color: #0F172A;
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
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
    .contact-item-label {
        font-size: 0.75rem;
        color: #64748B;
        font-weight: bold;
    }
    .contact-item-num {
        font-size: 1.3rem;
        font-weight: 900;
        color: #E11D48;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. サイドバー
# ---------------------------------------------------------
st.sidebar.markdown("""
<div class="sidebar-logo-wrap">
    <div class="sidebar-logo-icon">避難</div>
    <div>
        <div class="sidebar-logo-title">防災ナビ</div>
        <div class="sidebar-logo-sub">八王子市 避難情報</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("##### 現在地の設定")
user_address = st.sidebar.text_input("現在地住所", value="八王子市丹木町1丁目")

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
    {"name": "創価大学 グラウンド", "sub": "構内一次避難場所", "coords": [35.6870, 139.3285]},
    {"name": "加住小・中学校", "sub": "指定避難所", "coords": [35.6828, 139.3361]},
    {"name": "第一小学校", "sub": "八王子駅北口エリア", "coords": [35.6590, 139.3390]},
    {"name": "第四小学校", "sub": "明神町エリア", "coords": [35.6552, 139.3465]},
    {"name": "楢原小学校", "sub": "楢原町エリア", "coords": [35.6805, 139.3030]}
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
<div class="header-banner">
    <div class="banner-title">八王子市 避難ルートナビ</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 0.8])

with col1:
    st.markdown(f"""
    <div class="shelter-card">
        <div class="loc-tag">現在地：{user_address}</div>
        <div class="dest-title">{nearest_shelter['name']}</div>
        <div class="dest-sub">（{nearest_shelter['sub']}）</div>
        <div>
            <span class="pill-badge">距離：約 {min_distance:.1f} km / 徒歩約 {walk_minutes} 分</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="point-card">
        <div class="point-card-title">移動時の注意事項</div>
        <div class="point-card-item"><b>履物</b>：増水時の長靴は危険なため、スニーカーを着用してください。</div>
        <div class="point-card-item"><b>荷物</b>：両手が自由に使えるようリュックサックで移動してください。</div>
        <div class="point-card-item"><b>足元</b>：冠水時は用水路や側溝の位置が見えなくなるため注意してください。</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-title">避難ルートマップ</div>', unsafe_allow_html=True)

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
    color="#059669",
    weight=4,
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
    <div class="contact-card-title">緊急連絡先・通報ダイヤル</div>
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
            <div class="contact-item-label">八王子市役所 代表</div>
            <div style="font-weight:900; font-size:1.0rem; color:#334155; margin-top:4px;">042-620-7111</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
