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

# ポップデザインCSS（絵文字不使用・配色・フォント・角丸・影でポップさを表現）
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;800;900&display=swap');

    /* 全体背景 */
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
        margin-bottom: 24px;
        background: #FFFFFF;
        padding: 12px 16px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
        border: 2px solid #38BDF8;
    }
    .sidebar-logo-icon {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF;
        width: 42px;
        height: 42px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 0.95rem;
        flex-shrink: 0;
        box-shadow: 0 3px 8px rgba(16, 185, 129, 0.3);
    }
    .sidebar-logo-title {
        font-size: 1.4rem;
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

    /* メインヘッダーバナー */
    .header-banner {
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
        border-radius: 24px;
        padding: 18px 24px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.25);
        border: 4px solid #FFFFFF;
    }
    .banner-title {
        color: #FFFFFF;
        font-weight: 900;
        font-size: 1.6rem;
        letter-spacing: 1px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 0;
    }

    /* 最寄り避難所案内カード */
    .shelter-card {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #F472B6;
        box-shadow: 0 8px 20px rgba(244, 114, 182, 0.15);
        height: 100%;
        position: relative;
    }
    .loc-badge {
        display: inline-block;
        background: #F1F5F9;
        color: #475569;
        font-size: 0.85rem;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 12px;
        margin-bottom: 8px;
    }
    .dest-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #059669;
        margin: 6px 0 2px 0;
    }
    .dest-sub {
        font-size: 0.9rem;
        color: #10B981;
        font-weight: 800;
        margin-bottom: 16px;
    }
    .pill-badge {
        background-color: #ECFDF5;
        color: #047857;
        border: 2px solid #A7F3D0;
        padding: 8px 18px;
        border-radius: 30px;
        font-weight: 900;
        font-size: 0.9rem;
        display: inline-block;
    }

    /* 移動ワンポイントカード */
    .point-card {
        background: #FFFBEB;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #FBBF24;
        box-shadow: 0 8px 20px rgba(251, 191, 36, 0.15);
        height: 100%;
    }
    .point-card-title {
        color: #D97706;
        font-weight: 900;
        font-size: 1.15rem;
        margin-bottom: 12px;
        border-bottom: 2px dashed #FDE68A;
        padding-bottom: 6px;
    }
    .point-card-item {
        font-size: 0.85rem;
        margin-bottom: 10px;
        color: #451A03;
        font-weight: 800;
        line-height: 1.6;
    }

    /* 地図セクションタイトル */
    .section-title {
        font-size: 1.25rem;
        font-weight: 900;
        color: #0F172A;
        margin: 24px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-title::before {
        content: "";
        display: inline-block;
        width: 10px;
        height: 22px;
        background: #10B981;
        border-radius: 6px;
    }

    /* 緊急電話番号エリア */
    .contact-card-box {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 20px;
        border: 3px solid #E2E8F0;
        box-shadow: 0 6px 16px rgba(0,0,0,0.03);
        margin-top: 24px;
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
        border: 2px solid #F1F5F9;
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
        <div class="loc-badge">現在地：{user_address}</div>
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
