import streamlit as st

# ページの設定（タイトルやアイコン）
st.set_page_config(page_title="創価大学周辺 防災避難ナビ", page_icon="🚨", layout="centered")

st.title("🚨 創価大・丹木町エリア 避難ナビ")
st.caption("八王子市コンソーシアム発表用プロトタイプ")
st.write("現在地を選択するか入力すると、周辺の危険エリアと推奨避難ルートをご案内します。")

# 創価大学周辺の避難データ
soka_locations = {
    "中央教育棟": {
        "避難所": "加住小・中学校（指定避難所） / キャンパス内グラウンド",
        "危険エリア": "東側の谷筋・斜面方向は一部土砂災害警戒区域あり",
        "推奨ルート": "建物の西側メインストリートに出て、高低差の少ない中央通路を経由して避難してください。"
    },
    "栄光館": {
        "避難所": "加住小・中学校",
        "危険エリア": "周辺道路の勾配が急なため、大雨時の側溝溢水・冠水に注意",
        "推奨ルート": "大通り（ひよどり山トンネル方面へ抜ける主要道）に出て、北側の安全な平地へ誘導してください。"
    },
    "創価女子短期大学": {
        "避難所": "加住小・中学校",
        "危険エリア": "西側傾斜地の土砂崩れに注意",
        "推奨ルート": "構内の主要歩道を通って東側の高台へ移動してください。"
    },
    "丹木町2丁目": {
        "避難所": "加住小・中学校",
        "危険エリア": "谷地（やち）沿いの道路で局所的な冠水リスクあり",
        "推奨ルート": "低地を避け、創価大学側の高台へ上るルートを選択してください。"
    }
}

# 選択肢ボタン
selected_spot = st.selectbox(
    "現在地を選択してください",
    ["選択してください"] + list(soka_locations.keys())
)

# 直接入力欄（自由入力用）
custom_spot = st.text_input("または、詳しい現在地を直接入力（例: 中央教育棟の1階）")

location_to_check = custom_spot if custom_spot else selected_spot

if location_to_check and location_to_check != "選択してください":
    st.divider()
    
    # 検索ロジック
    matched_key = None
    for key in soka_locations:
        if key in location_to_check:
            matched_key = key
            break
            
    if matched_key:
        info = soka_locations[matched_key]
        st.success(f"📍 **現在地情報**: {location_to_check}")
        
        st.subheader("🏠 指定避難場所")
        st.info(info["避難所"])
        
        st.subheader("⚠️ 周辺ハザード警戒事項")
        st.warning(info["危険エリア"])
        
        st.subheader("🏃‍♂️ 推奨避難ルート")
        st.write(info["推奨ルート"])
        
        st.caption("※足元に十分注意し、隣近所や周りの人と声を掛け合いながら避難してください。")
    else:
        st.info(f"「{location_to_check}」周辺のデータを検索中です...")
        st.write("創価大学構内・丹木町周辺にいる場合は、土砂崩れが発生しやすい斜面から離れ、身の安全を確保した上でメインストリート（高台）を目指してください。")
