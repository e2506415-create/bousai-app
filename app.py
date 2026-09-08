import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request
import math

# ---------------------------------------------------------
# 1. ページ基本設定（ポップ・おしゃれ＆直感デザイン）
# ---------------------------------------------------------
st.set_page_config(page_title="八王子 避難ルートナビ 🐥", page_icon="🐥", layout="wide")

# カスタムCSS（見やすいフォント設定・パステルデザイン）
st.markdown("""
    <style>
    /* 全体背景と標準フォント */
    .stApp {
        background: linear-gradient(135deg, #FFF9F3 0%, #FAEDF0 100%);
        font-family: 'Hiragino Maru Gothic ProN', 'Rounded Mplus 1c', 'Yu Gothic', 'Meiryo', sans-serif;
    }
    
    /* メインタイトル */
    .main-title {
        color: #FF5D8F;
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 5px;
        text-shadow: 2px 2px 0px #FFF;
    }
    .sub-title {
        color: #577590;
        text-align: center;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 25px;
    }
    
    /* 一番大事なルート案内結果カード */
    .result-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 20px 25px;
        box-shadow: 0 8px 20px rgba(255, 93, 143, 0.2);
        border: 3px solid #FF5D8F;
        margin-bottom: 20px;
    }
    .result-header {
        font-size: 0.95rem;
        color: #8D99AE;
        font-weight: bold;
    }
    .result-destination {
        font-size: 1.55rem;
        color: #2A9D8F;
        font-weight: 800;
        margin: 6px 0 12px 0;
    }
    .result-route-info {
        font-size: 1.05rem;
        color: #2B2D42;
        background-color: #E8F5E9;
        padding: 10px 16px;
        border-radius: 12px;
        display: inline-block;
        font-weight: bold;
        border: 1px solid #C8E6C9;
    }
    
    /* 防災アドバイスカード */
    .advice-card {
        background-color: #FFF9A6;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(249, 199, 79, 0.2);
        border: 2.5px dashed #F9C74F;
        color: #432818;
    }
    .advice-title {
        font-size: 1.15rem;
        font-weight: bold;
        color: #E76F51;
        margin-bottom: 8px;
    }
    .advice-list {
        font-size: 0.95rem;
        line-height: 1.7;
        margin: 0;
        padding-left: 20px;
    }
    
    /* セクション見出し */
    .section-header {
        font-size: 1.35rem;
        font-weight: bold;
        color: #2A9D8F;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    
    /* 緊急連絡先ボックス */
    .contact-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 20px 25px;
        border: 2px solid #F4A261;
        box-shadow: 0 8px 20px rgba(244, 162, 97, 0.12);
        margin-top: 25px;
    }
    .contact-header {
        color: #E76F51;
        font-weight: bold;
        font-size: 1.25rem;
        margin-bottom: 15px;
        text-align: center;
    }
    .contact-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
    }
    .contact-item {
        background-color: #F8F9FA;
        border-radius: 12px;
        padding: 10px 15px;
        text-align: center;
    }
    .contact-num {
        font-size: 1.3rem;
        font-weight: bold;
        color: #E63946;
    }
    </style>
""", unsafe_allow_html=True)

# ヘッダーエリア
st.markdown('<p class="main-title">🐥 八王子市 避難ルートナビ 🌈</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">〜 現在地を入れるだけ！一番近くて安全な避難所へ即案内 〜</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 住所座標変換 & 2点間距離計算（最寄り判定用）
# ---------------------------------------------------------
def get_coords_from_address(address_text):
    """国土地理院等の無料APIを使って住所から座標を取得"""
    default_coords = [35.6881, 139.3275] # 創価大付近
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
    """2地点間の直線距離(km)を計算"""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------------------------------------------------
# 3. 八王子市内の主要避難所データ & 危険エリア
# ---------------------------------------------------------
SHELTERS = [
    {"name": "🏫 加住小・中学校（指定避難所）", "coords": [35.6828, 139.3361], "note": "広域避難場所・指定避難所"},
    {"name": "🏫 創価大学 グラウンド（構内一次避難場所）", "coords": [35.6870, 139.3285], "note": "大学構内・広いグラウンド"},
    {"name": "🏫 第一小学校（八王子駅北口側）", "coords": [35.6590, 139.3390], "note": "市街地エリアの避難所"},
    {"name": "🏫 第四小学校（明神町エリア）", "coords": [35.6552, 139.3465], "note": "東部エリアの指定避難所"},
    {"name": "🏫 楢原小学校（楢原町エリア）", "coords": [35.6805, 139.3030], "note": "西部エリアの指定避難所"}
]

HAZARD_ZONES = [
    {"name": "🍓 丹木町東側 斜面注意エリア", "coords": [35.6885, 139.3300], "radius": 130, "color": "#FF6B6B", "desc": "【土砂崩れ警戒】大雨時は近づかず、高台へ！"},
    {"name": "🍊 ひよどり山北側 冠水注意エリア", "coords": [35.6830, 139.3240], "radius": 110, "color": "#FFD93D", "desc": "【水たまり冠水】アンダーパスや低い道は避けて！"}
]

# ---------------------------------------------------------
# 4. サイドバー（現在地入力のみ）
# ---------------------------------------------------------
st.sidebar.markdown("### 📍 いまどこにいる？")
user_address = st.sidebar.text_input("住所や建物名を入力してね", value="八王子市丹木町1丁目", help="例: 丹木町1-2-3、栄光館、八王子駅など")

# 現在地の座標取得
current_coords = get_coords_from_address(user_address)

# ---------------------------------------------------------
# 5. 最寄り避難所・徒歩時間の自動判定
# ---------------------------------------------------------
nearest_shelter = None
min_distance = float('inf')

for shelter in SHELTERS:
    dist = calculate_distance(current_coords[0], current_coords[1], shelter["coords"][0], shelter["coords"][1])
    if dist < min_distance:
        min_distance = dist
        nearest_shelter = shelter

# 徒歩時間の目安（時速4kmとして計算）
walk_minutes = math.ceil((min_distance / 4.0) * 60)

# ---------------------------------------------------------
# 6. メイン画面：最寄り避難所＆ナビ結果のカード表示
# ---------------------------------------------------------
col1, col2 = st.columns([1.2, 0.8])

with col1:
    st.markdown(f"""
    <div class="result-card">
        <div class="result-header">📍 現在地：{user_address}</div>
        <div style="font-size:0.9rem; color:#8D99AE; margin-top:8px;">🏃‍♂️ 向かうべき最寄りの避難所はこちら！</div>
        <div class="result-destination">{nearest_shelter['name']}</div>
        <div class="result-route-info">
            🚶‍♂️ 距離: 約 <b>{min_distance:.1f} km</b> ／ 徒歩約 <b>{walk_minutes} 分</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="advice-card">
        <div class="advice-title">💡 移動時のワンポイント</div>
        <ul class="advice-list">
            <li><b>👟 履物</b>：増水時の長靴は危険！スニーカーで。</li>
            <li><b>🎒 荷物</b>：両手が空くようにリュックで移動。</li>
            <li><b>⚠️ 移動</b>：水で隠れた側溝や傾斜地に注意！</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<p class="section-header">🗺️ 安全おすすめ避難ルートマップ</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 地図描画
# ---------------------------------------------------------
m = folium.Map(location=current_coords, zoom_start=15)

# A. 現在地（赤ピン）
folium.Marker(
    location=current_coords,
    popup=f"📍 現在地: {user_address}",
    tooltip="いまここにいます！",
    icon=folium.Icon(color="red", icon="user", prefix="fa")
).add_to(m)

# B. 自動選出された最寄り避難所（緑のホームピン）
folium.Marker(
    location=nearest_shelter["coords"],
    popup=f"🏠 最寄り避難所: {nearest_shelter['name']}",
    tooltip="目指す避難所！",
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# C. その他の避難所（グレーピン）
for shelter in SHELTERS:
    if shelter["name"] != nearest_shelter["name"]:
        folium.Marker(
            location=shelter["coords"],
            popup=f"🏫 {shelter['name']}",
            tooltip="その他の避難所",
            icon=folium.Icon(color="gray", icon="info-sign")
        ).add_to(m)

# D. 危険エリア（警戒円）
for zone in HAZARD_ZONES:
    folium.Circle(
        location=zone["coords"],
        radius=zone["radius"],
        color=zone["color"],
        fill=True,
        fill_color=zone["color"],
        fill_opacity=0.4,
        popup=f"{zone['name']}\n{zone['desc']}"
    ).add_to(m)

# E. 最寄り避難所までのルート（太い青線）
route_coords = [
    current_coords,
    [(current_coords[0] + nearest_shelter["coords"][0])/2 + 0.0006,
     (current_coords[1] + nearest_shelter["coords"][1])/2 - 0.0006],
    nearest_shelter["coords"]
]

folium.PolyLine(
    locations=route_coords,
    color="#0066FF",
    weight=8,
    opacity=0.85,
    tooltip=f"🌈 {nearest_shelter['name']} への安全ルート"
).add_to(m)

# 地図を表示
st_folium(m, width="100%", height=480)

# ---------------------------------------------------------
# 8. 緊急連絡先カード
# ---------------------------------------------------------
st.markdown("""
<div class="contact-card">
    <div class="contact-header">📞 緊急連絡先＆安否確認ダイヤル</div>
    <div class="contact-grid">
        <div class="contact-item">
            <div style="font-size:0.85rem; color:#6C757D;">火災・救急・救助</div>
            <div class="contact-num">119 番</div>
        </div>
        <div class="contact-item">
            <div style="font-size:0.85rem; color:#6C757D;">警察（事件・事故）</div>
            <div class="contact-num" style="color:#0077B6;">110 番</div>
        </div>
        <div class="contact-item">
            <div style="font-size:0.85rem; color:#6C757D;">災害用伝言ダイヤル</div>
            <div class="contact-num" style="color:#2A9D8F;">171 番</div>
        </div>
        <div class="contact-item">
            <div style="font-size:0.85rem; color:#6C757D;">八王子市役所 (代表)</div>
            <div style="font-weight:bold; font-size:1.05rem; margin-top:3px;">042-620-7111</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
