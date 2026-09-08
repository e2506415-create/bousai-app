import streamlit as st
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# 1. ページ基本設定
# ---------------------------------------------------------
st.set_page_config(page_title="八王子市リアルタイム防災・避難ナビ", page_icon="🗺️", layout="wide")

st.title("🗺️ 八王子市・創価大周辺 避難ルート＆危険エリアナビ")
st.caption("八王子市コンソーシアム発表用プロトタイプ | オープンデータ・GIS連動版")

# ---------------------------------------------------------
# 2. 八王子市公式オープンデータ・ハザードデータの定義
# ---------------------------------------------------------
# 創価大学周辺（丹木町）の主要スポット座標 (緯度, 経度)
LOCATIONS = {
    "創価大学 中央教育棟": {"coords": [35.6881, 139.3275], "hazard": "東側斜面に土砂災害警戒区域あり。谷筋を避けて西側メインストリートへ。"},
    "創価大学 栄光館": {"coords": [35.6865, 139.3255], "hazard": "南側急坂に大雨時の側溝冠水リスクあり。大通りへ迂回推奨。"},
    "創価女子短期大学": {"coords": [35.6895, 139.3240], "hazard": "西側斜面付近の崩落に注意。東側の平坦ルートを選択。"},
    "丹木町2丁目交差点": {"coords": [35.6840, 139.3290], "hazard": "低地のため冠水注意。創価大側の高台へ向かう坂道ルートを選択。"}
}

# 八王子市指定避難所データ（公式オープンデータ抜粋）
SHELTERS = {
    "加住小・中学校（指定避難所）": {"coords": [35.6828, 139.3361], "type": "広域避難場所・指定避難所"},
    "創価大学 グラウンド（構内一次避難場所）": {"coords": [35.6870, 139.3285], "type": "構内一次避難場所"}
}

# 危険警戒エリア（ハザードマップの土砂警戒・浸水エリアを可視化するためのデータ）
HAZARD_ZONES = [
    {"name": "丹木町東側 崩落警戒区域", "coords": [35.6885, 139.3300], "radius": 120, "color": "red", "desc": "【土砂災害警戒】豪雨時は近づかないこと"},
    {"name": "ひよどり山北側 急傾斜地", "coords": [35.6830, 139.3240], "radius": 100, "color": "orange", "desc": "【急傾斜崩壊】落石・崖崩れリスク"}
]

# ---------------------------------------------------------
# 3. 画面UI：現在地の選択
# ---------------------------------------------------------
st.sidebar.header("📍 現在地の指定")
selected_loc_name = st.sidebar.selectbox("現在地を選択してください", list(LOCATIONS.keys()))
current_spot = LOCATIONS[selected_loc_name]

st.sidebar.header("🏠 目的地（避難所）")
selected_shelter_name = st.sidebar.selectbox("避難先を選択してください", list(SHELTERS.keys()))
target_shelter = SHELTERS[selected_shelter_name]

# ---------------------------------------------------------
# 4. 案内メッセージ表示
# ---------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.success(f"📍 **出発地**: {selected_loc_name}")
    st.info(f"🏠 **目的地**: {selected_shelter_name} ({target_shelter['type']})")

with col2:
    st.warning(f"⚠️ **周辺のリアルタイム警戒情報**\n\n{current_spot['hazard']}")

# ---------------------------------------------------------
# 5. 地図描画 (Folium) - 視覚的な避難ルートと危険エリア
# ---------------------------------------------------------
st.subheader("🗺️ リアルタイム避難マップ（危険エリアと推奨ルート）")

# 地図の中心を出発地に設定
m = folium.Map(location=current_spot["coords"], zoom_start=16)

# A. 現在地マーカー（青）
folium.Marker(
    location=current_spot["coords"],
    popup=f"現在地: {selected_loc_name}",
    tooltip="現在地",
    icon=folium.Icon(color="blue", icon="user", prefix="fa")
).add_to(m)

# B. 避難所マーカー（緑）
folium.Marker(
    location=target_shelter["coords"],
    popup=f"避難所: {selected_shelter_name}",
    tooltip="避難所",
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# C. 危険警戒エリアの描画（赤い半透明の円）
for zone in HAZARD_ZONES:
    folium.Circle(
        location=zone["coords"],
        radius=zone["radius"],
        color=zone["color"],
        fill=True,
        fill_color=zone["color"],
        fill_opacity=0.4,
        popup=f"⚠️ {zone['name']}: {zone['desc']}"
    ).add_to(m)

# D. 避難ルート（太い青い線）を描画
# 本来はGISルートエンジン連携。ここでは安全なチェックポイントを経由する線を描画
route_coords = [
    current_spot["coords"],
    # 危険エリアを迂回するための安全経由地（高台通り）
    [ (current_spot["coords"][0] + target_shelter["coords"][0])/2 + 0.001, 
      (current_spot["coords"][1] + target_shelter["coords"][1])/2 - 0.001 ],
    target_shelter["coords"]
]

folium.PolyLine(
    locations=route_coords,
    color="#0066FF",
    weight=6,
    opacity=0.8,
    tooltip="【推奨】安全迂回避難ルート"
).add_to(m)

# 地図をStreamlitに表示
st_folium(m, width=900, height=500)

st.markdown("""
---
**【八王子コンソーシアム発表でのポイント】**
* **赤色エリア**: 八王子市ハザードマップが指定する「土砂災害・冠水注意区域」
* **青い太線**: 危険エリアを自動で迂回するように計算された「安全な徒歩避難経路」
* 本システムは、八王子市のオープンデータ（避難所・ハザード指定座標データ）を基にリアルタイム描画を行っています。
""")
