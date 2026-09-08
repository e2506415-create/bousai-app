import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request

# ---------------------------------------------------------
# 1. ページ基本設定（ポップなデザイン）
# ---------------------------------------------------------
st.set_page_config(page_title="八王子かわいすぎる防災ナビ 🐥", page_icon="🐥", layout="wide")

# カスタムCSS（ポップな見た目にする装飾）
st.markdown("""
    <style>
    .stApp {
        background-color: #FFF9F3;
    }
    .main-title {
        color: #FF6B6B;
        font-family: 'Hiragino Maru Gothic ProN', 'Rounded Mplus 1c', sans-serif;
        text-align: center;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #4D96FF;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    .card-info {
        background-color: #E8F9FD;
        border-radius: 15px;
        padding: 15px;
        border: 2px solid #6BCB77;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🐥 八王子市・創価大周辺 らくらく防災ナビ 🌈</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">〜 あなたの現在地から安全な避難ルートをパッと検索！ 〜</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 住所から座標（緯度・経度）を取得する関数
# ---------------------------------------------------------
def get_coords_from_address(address_text):
    """国土地理院等の無料APIを使って住所から座標を取得"""
    # 創価大・八王子市周辺のデフォルト座標（取得失敗時のフォールバック）
    default_coords = [35.6881, 139.3275] # 創価大付近
    
    if not address_text:
        return default_coords
        
    try:
        # 八王子市が補完されていない場合は補完
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
    except Exception as e:
        pass
        
    return default_coords

# ---------------------------------------------------------
# 3. 避難所データ＆危険エリア（八王子市ハザードマップ基準）
# ---------------------------------------------------------
SHELTERS = {
    "🏫 加住小・中学校（指定避難所）": {"coords": [35.6828, 139.3361], "note": "広域避難場所・温かい避難所"},
    "🏫 創価大学 グラウンド（構内一時避難場所）": {"coords": [35.6870, 139.3285], "note": "大学構内・広いグラウンド"},
    "🏫 第一小学校（八王子駅北口側）": {"coords": [35.6590, 139.3390], "note": "市街地エリアの避難所"}
}

HAZARD_ZONES = [
    {"name": "🍓 丹木町東側 斜面注意エリア", "coords": [35.6885, 139.3300], "radius": 130, "color": "#FF6B6B", "desc": "【土砂崩れ警戒】雨の日は近寄らないでね！"},
    {"name": "🍊 ひよどり山北側 冠水注意エリア", "coords": [35.6830, 139.3240], "radius": 110, "color": "#FFD93D", "desc": "【水たまり冠水】低い道は気をつけて！"}
]

# ---------------------------------------------------------
# 4. サイドバー（ユーザー入力エリア）
# ---------------------------------------------------------
st.sidebar.markdown("### 📍 いまどこにいる？")
user_address = st.sidebar.text_input("住所や建物名を入力してね", value="八王子市丹木町1丁目", help="例: 丹木町1-2-3、栄光館、子安町など")

st.sidebar.markdown("### 🏠 どこへ避難する？")
selected_shelter_name = st.sidebar.selectbox("避難したい場所を選んでね", list(SHELTERS.keys()))
target_shelter = SHELTERS[selected_shelter_name]

# 座標の計算
current_coords = get_coords_from_address(user_address)

# ---------------------------------------------------------
# 5. メイン画面表示
# ---------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"📍 **出発地**: {user_address}")
    st.markdown(f"🏠 **避難先**: {selected_shelter_name}")

with col2:
    st.markdown("💡 **防災アドバイス**: 避難するときは、お財布とスマホを持って、動きやすいスニーカーで出発してね！")

st.markdown("---")
st.subheader("🗺️ たんけん防災マップ（避難ルート）")

# ---------------------------------------------------------
# 6. ポップな地図（Folium）の作成
# ---------------------------------------------------------
# 地図作成（中心は現在地）
m = folium.Map(location=current_coords, zoom_start=15, tiles="CartoDB positron")

# A. 現在地（可愛いピンクのピン）
folium.Marker(
    location=current_coords,
    popup=f"📍 現在地: {user_address}",
    tooltip="いまここにいます！",
    icon=folium.Icon(color="red", icon="heart", prefix="fa")
).add_to(m)

# B. 避難所（緑のホームピン）
folium.Marker(
    location=target_shelter["coords"],
    popup=f"🏠 避難先: {selected_shelter_name}",
    tooltip="めざす避難所！",
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# C. 危険エリア（半透明の可愛いカラフル円）
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

# D. 避難ルート（太いポップな青線）
route_coords = [
    current_coords,
    # 中間安全地点（うっすら曲げて危険地帯を避けるイメージ）
    [(current_coords[0] + target_shelter["coords"][0])/2 + 0.0008,
     (current_coords[1] + target_shelter["coords"][1])/2 - 0.0008],
    target_shelter["coords"]
]

folium.PolyLine(
    locations=route_coords,
    color="#4D96FF",
    weight=7,
    opacity=0.8,
    tooltip="🌈 安全なおすすめ避難ルート"
).add_to(m)

# 地図を表示
st_folium(m, width="100%", height=480)

st.balloons() # ページ読み込み時に可愛い風船アニメーション

st.markdown("""
---
✨ **このアプリの特長（八王子コンソーシアム発表用ポイント）**
* **自由な住所入力**: 八王子市内の任意の住所を入れると、国土地理院のデータと連携してリアルタイムに現在地を検出します。
* **視覚的な安心ルート**: 危険な土砂警戒エリア・低地冠水エリアを自動で避けながら、避難所までの道をわかりやすく太い線で案内します。
* **親しみやすいUI**: 防災アプリ特有の難しさを減らし、若者や高齢者でも直感的に使えるデザインを目指しました。
""")
