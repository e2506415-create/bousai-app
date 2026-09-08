import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request

# ---------------------------------------------------------
# 1. ページ基本設定（おしゃれ・ポップ＆見やすいデザイン）
# ---------------------------------------------------------
st.set_page_config(page_title="八王子 避難ルートナビ 🐥", page_icon="🐥", layout="wide")

# カスタムCSS（ポップ・おしゃれなUI装飾）
st.markdown("""
    <style>
    /* 全体背景 */
    .stApp {
        background: linear-gradient(135deg, #FFF9F3 0%, #FAEDF0 100%);
        font-family: 'Hiragino Maru Gothic ProN', 'Rounded Mplus 1c', 'メイリオ', sans-serif;
    }
    
    /* メインタイトル */
    .main-title {
        color: #FF5D8F;
        text-align: center;
        font-size: 2.3rem;
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
    
    /* 大事な情報カード (現在地・避難先) */
    .spot-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 18px 22px;
        box-shadow: 0 8px 20px rgba(255, 154, 162, 0.15);
        border: 2px solid #FFC6FF;
        margin-bottom: 15px;
    }
    .spot-label {
        font-size: 0.85rem;
        color: #8D99AE;
        font-weight: bold;
        margin-bottom: 4px;
    }
    .spot-value {
        font-size: 1.35rem;
        color: #2B2D42;
        font-weight: bold;
    }
    
    /* 防災アドバイスカード */
    .advice-card {
        background-color: #FFF9A6;
        border-radius: 20px;
        padding: 18px 22px;
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
        font-size: 1.4rem;
        font-weight: bold;
        color: #2A9D8F;
        margin-top: 10px;
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
st.markdown('<p class="main-title">🐥 八王子市・創価大周辺 避難ルートナビ 🌈</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">〜 あなたの現在地から安全な避難経路をすぐ案内！ 〜</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 住所から座標（緯度・経度）を取得する関数
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
    except Exception as e:
        pass
        
    return default_coords

# ---------------------------------------------------------
# 3. 避難所データ＆危険エリア（八王子市ハザードマップ基準）
# ---------------------------------------------------------
SHELTERS = {
    "🏫 加住小・中学校（指定避難所）": {"coords": [35.6828, 139.3361], "note": "広域避難場所・指定避難所"},
    "🏫 創価大学 グラウンド（構内一次避難場所）": {"coords": [35.6870, 139.3285], "note": "大学構内・広いグラウンド"},
    "🏫 第一小学校（八王子駅北口側）": {"coords": [35.6590, 139.3390], "note": "市街地エリアの避難所"}
}

HAZARD_ZONES = [
    {"name": "🍓 丹木町東側 斜面注意エリア", "coords": [35.6885, 139.3300], "radius": 130, "color": "#FF6B6B", "desc": "【土砂崩れ警戒】大雨時は近づかず、高台へ！"},
    {"name": "🍊 ひよどり山北側 冠水注意エリア", "coords": [35.6830, 139.3240], "radius": 110, "color": "#FFD93D", "desc": "【水たまり冠水】アンダーパスや低い道は避けて！"}
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
# 5. メイン画面：大事な情報の強調カード表示
# ---------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"""
    <div class="spot-card">
        <div class="spot-label">📍 現在地（出発ポイント）</div>
        <div class="spot-value">{user_address}</div>
        <div style="margin-top:12px;" class="spot-label">🏠 めざす避難先</div>
        <div class="spot-value" style="color:#2A9D8F;">{selected_shelter_name}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="advice-card">
        <div class="advice-title">💡 今すぐ確認！安全避難のアドバイス</div>
        <ul class="advice-list">
            <li><b>👟 履物</b>：増水時の長靴は危険！履き慣れたスニーカーで。</li>
            <li><b>🎒 荷物</b>：両手が空くようにリュックまとめ。</li>
            <li><b>⚠️ 移動</b>：谷筋や斜面近く、浸水で隠れた側溝に注意！</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<p class="section-header">🗺️ 避難ルート＆危険エリアマップ</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 日本語表示の地図描画
# ---------------------------------------------------------
m = folium.Map(location=current_coords, zoom_start=15)

# A. 現在地（赤ピン）
folium.Marker(
    location=current_coords,
    popup=f"📍 現在地: {user_address}",
    tooltip="いまここにいます！",
    icon=folium.Icon(color="red", icon="user", prefix="fa")
).add_to(m)

# B. 避難所（緑のホームピン）
folium.Marker(
    location=target_shelter["coords"],
    popup=f"🏠 避難先: {selected_shelter_name}",
    tooltip="めざす避難所！",
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# C. 危険エリア（半透明の警戒円）
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

# D. 避難ルート（太い青線）
route_coords = [
    current_coords,
    [(current_coords[0] + target_shelter["coords"][0])/2 + 0.0008,
     (current_coords[1] + target_shelter["coords"][1])/2 - 0.0008],
    target_shelter["coords"]
]

folium.PolyLine(
    locations=route_coords,
    color="#0066FF",
    weight=7,
    opacity=0.8,
    tooltip="🌈 安全なおすすめ避難ルート"
).add_to(m)

# 地図を表示
st_folium(m, width="100%", height=480)

# ---------------------------------------------------------
# 7. おしゃれな緊急連絡先カード
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
