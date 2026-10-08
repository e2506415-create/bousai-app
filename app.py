import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request
import math

# --- ページ設定（サイトタイトル、アイコン） ---
st.set_page_config(page_title="ハチボー - 八王子市防災ナビ", page_icon="🚴‍♂️")

# ---------------------------------------------------------
# カスタムCSS（デザイン調整）
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&display=swap');
    body, * { font-family: 'Kosugi Maru', sans-serif !important; }
    .stApp { background-color: #f0fdf4; }
    .stButton>button { background-color: #16a34a; color: white; border-radius: 99px; }
    .stButton>button:hover { background-color: #15803d; color: white; }
    div[data-testid="stMetricValue"] { color: #16a34a; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    h1 { color: #15803d; border-bottom: 2px solid #16a34a; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# モーション・育成機能 (Session State)
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
        icon = "🥚"
    elif level < 10:
        title = "見習いハチボー"
        icon = "🐣"
    elif level < 20:
        title = "八王子マスター"
        icon = "🐤"
    else:
        title = "伝説の防災レジェンド"
        icon = "👑"
    return level, title, icon

# 訪問経験値（初回のみ）
if st.session_state.visit_count == 0:
    add_exp(5)
st.session_state.visit_count += 1

# ---------------------------------------------------------
# データ・API関連関数
# ---------------------------------------------------------

# 1. 八王子市の指定避難所データ（簡易版・位置情報付き）
# 最新情報は八王子市HPを確認してください。
SHELTERS = [
    {"name": "創価大学（広域）", "coords": [35.6870, 139.3285]},
    {"name": "工学院大学（広域）", "coords": [35.6892, 139.3134]},
    {"name": "都立八王子東高校", "coords": [35.6565, 139.3698]},
    {"name": "法政大学多摩キャンパス（広域）", "coords": [35.6095, 139.3790]},
    {"name": "エスフォルタアリーナ八王子（狭間）", "coords": [35.6416, 139.3005]},
    {"name": "中央大学多摩キャンパス（広域）", "coords": [35.6415, 139.4050]},
    {"name": "八王子市役所（本庁舎）", "coords": [35.6666, 139.3308]},
]

# 2. 住所 -> 座標変換API（国土地理院）
# 八王子市限定にするため、クエリに「八王子市」を自動付加
def get_coords_from_address(address_text):
    if not address_text:
        return None
    try:
        # クエリを八王子市に限定
        query = f"東京都八王子市 {address_text}"
        url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" + urllib.parse.quote(query)
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and len(data) > 0:
                lon, lat = data[0]['geometry']['coordinates']
                return [lat, lon]
    except Exception:
        pass
    return None

# 3. 2点間の直線距離計算 (ハバーサイン公式)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # 地球の半径 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# 4. ルート検索API (OSRM)
# profile: 'driving' (車), 'cycling' (自転車), 'foot' (徒歩)
def get_route_osrm(start_coords, end_coords, profile='foot'):
    try:
        url = f"http://router.project-osrm.org/route/v1/{profile}/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data['code'] == 'Ok':
                route = data['routes'][0]
                geometry = route['geometry']['coordinates']
                # Folium用に [lat, lon] のリストに変換
                route_coords = [[lat, lon] for lon, lat in geometry]
                distance_km = route['distance'] / 1000.0
                duration_min = route['duration'] / 60.0
                return route_coords, distance_km, duration_min
    except Exception:
        # APIエラー時はNoneを返す (直線距離フォールバック用)
        pass
    return None, None, None

# ---------------------------------------------------------
# メイン画面の実装
# ---------------------------------------------------------

# --- ヘッダー ---
st.title("🌱 コツコツハチボー - 八王子市防災ナビ")
st.markdown("八王子市限定の防災マップです。現在地を入力して、最寄りの避難所へのルートを確認しましょう。")

# --- 1. 育成機能 UI ---
lv, title, icon = get_level_info(st.session_state.exp)
col1, col2, col3 = st.columns([1, 2, 2])
with col1:
    st.markdown(f"<h1 style='text-align: center; border:none;'>{icon}</h1>", unsafe_allow_html=True)
with col2:
    st.metric(label="ハチボーLv", value=f"Lv.{lv}", help="コツコツ使うとレベルが上がるよ！")
    st.markdown(f"**称号**: {title}")
with col3:
    # 経験値ゲージ
    prog = st.session_state.exp % 10
    st.write("次のレベルまで...")
    st.progress(prog * 10)

st.markdown("---")

# --- 2. 住所入力・用途選択 ---
with st.sidebar:
    st.header("🔍 避難検索")
    address_input = st.text_input("現在地を入力 (八王子市内の町名・建物名)", placeholder="例: 八王子市役所")
    
    # 用途選択（自転車・徒歩・車）
    mode_opt = st.radio(
        "避難方法",
        ('徒歩 (推奨)', '自転車', '車 (緊急時のみ)'),
        index=0
    )
    
    search_button = st.button("避難所を探す")
    
    st.markdown("---")
    st.caption("※ルート検索・ハザードマップは目安です。実際の状況判断を優先してください。")

# --- 3. 検索ロジックと結果表示 ---
now_coords = None
nearest_shelter = None
route_polyline = None
dist_km = 0
time_min = 0

# OSRMプロファイルのマッピング
mode_map = {
    '徒歩 (推奨)': 'foot',
    '自転車': 'cycling',
    '車 (緊急時のみ)': 'driving'
}

if search_button and address_input:
    add_exp(2) # 検索で経験値+2
    with st.spinner('現在地を特定中...'):
        now_coords = get_coords_from_address(address_input)
        
    if now_coords:
        st.success(f"現在地を特定しました: (緯度:{now_coords[0]:.4f}, 経度:{now_coords[1]:.4f})")
        
        # 最寄りの避難所を特定（直線距離で計算）
        with st.spinner('最寄りの避難所を検索中...'):
            min_dist = float('inf')
            for shelter in SHELTERS:
                d = calculate_distance(now_coords[0], now_coords[1], shelter['coords'][0], shelter['coords'][1])
                if d < min_dist:
                    min_dist = d
                    nearest_shelter = shelter
            
            # OSRMで実際のルートと時間を取得
            mode_profile = mode_map[mode_opt]
            route_coords, route_dist, route_time = get_route_osrm(now_coords, nearest_shelter['coords'], mode_profile)
            
            # フォールバック処理（APIエラー時は直線距離から徒歩時間を推定）
            if route_coords:
                route_polyline = route_coords
                dist_km = route_dist
                time_min = route_time
                route_type = "道路優先"
            else:
                st.warning("ルート検索APIが混雑しています。直線距離での目安を表示します。")
                route_polyline = [now_coords, nearest_shelter['coords']]
                dist_km = min_dist
                # 徒歩の速度を時速4kmと仮定
                time_min = (dist_km / 4.0) * 60
                route_type = "直線距離 (目安)"

            # 結果表示
            add_exp(3) # 避難所特定で経験値+3
            st.subheader(f"🏃‍♂️ {mode_opt}での最寄り避難所")
            c1, c2, c3 = st.columns(3)
            c1.metric("避難所名", nearest_shelter['name'])
            c2.metric("距離", f"{dist_km:.2f} km", help=route_type)
            c3.metric("所要時間 (目安)", f"{time_min:.0f} 分")
            
    else:
        st.error("現在地を特定できませんでした。八王子市内の正確な住所を入力してください。")

# --- 4. 地図の表示 ---
st.markdown("### 🗺️ 防災マップ (八王子市)")

# 初期表示位置（八王子市役所）
map_center = [35.6666, 139.3308]
zoom_lv = 13

# 住所検索後は現在地をセンターに
if now_coords:
    map_center = now_coords
    zoom_lv = 15

# Folium地図の作成
m = folium.Map(location=map_center, zoom_start=zoom_lv, tiles="OpenStreetMap")

# --- ハザードマップ レイヤー追加 (ここが機能する部分) ---
# 国土地理院タイル

# 1. 洪水浸水想定区域 (全河川)
folium.TileLayer(
    tiles='https://disaportaldata.gsi.go.jp/raster/01_flood_l2_shinsuisai_data/{z}/{x}/{y}.png',
    attr='国土地理院ハザードマップ(洪水)',
    name='🌊 洪水浸水想定区域',
    opacity=0.7,
    overlay=True,
    control=True
).add_to(m)

# 2. 土砂災害警戒区域
folium.TileLayer(
    tiles='https://disaportaldata.gsi.go.jp/raster/05_sedimentdisaster_raster/{z}/{x}/{y}.png',
    attr='国土地理院ハザードマップ(土砂)',
    name='⛰️ 土砂災害警戒区域',
    opacity=0.7,
    overlay=True,
    control=True
).add_to(m)

# 避難所のマーカーを追加
for shelter in SHELTERS:
    folium.Marker(
        location=shelter['coords'],
        popup=shelter['name'],
        icon=folium.Icon(color='green', icon='home')
    ).add_to(m)

# 住所検索後の動的表示（現在地マーカー、ルート線）
if now_coords:
    # 現在地マーカー
    folium.Marker(
        location=now_coords,
        popup="現在地",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # 避難ルートの線（ポリライン）
    if route_polyline:
        folium.PolyLine(
            locations=route_polyline,
            color='#16a34a', # ハチボーグリーン
            weight=5,
            opacity=0.8,
            tooltip=f"{mode_opt}ルート"
        ).add_to(m)

# レイヤーコントロール（チェックボックス）を追加
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# 地図をStreamlitに描画
st_folium(m, width=700, height=500, returned_objects=[])

# --- フッター ---
st.markdown("---")
st.caption("コツコツハチボー v1.0 | 八王子市限定防災プロトタイプ")
st.caption("データ出典: 国土地理院ハザードマップタイル、OSRM API、OpenStreetMap")
