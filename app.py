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
st.set_page_config(page_title="防災ナビ 避難ルートマップ", page_icon="🏃‍♂️", layout="wide")

# デザイン完全再現CSS
st.markdown("""
    <style>
    /* 全体背景 */
    .stApp {
        background: #F4F9FB;
        font-family: -apple-system, BlinkMacSystemFont, "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
    }
    
    /* サイドバー */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E6F3F7 0%, #DCEDF5 50%, #CDE3EE 100%) !important;
        border-right: 1px solid #C4DFEC;
    }
    
    /* 左上ロゴエリア */
    .sidebar-logo-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .runner-circle-icon {
        background-color: #00A86B;
        width: 58px;
        height: 58px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 14px rgba(0, 168, 107, 0.3);
        flex-shrink: 0;
    }
    .sidebar-logo-title {
        font-size: 1.7rem;
        font-weight: 900;
        color: #1E293B;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    .sidebar-logo-sub {
        font-size: 0.75rem;
        color: #64748B;
        font-weight: bold;
        margin-top: 2px;
        line-height: 1.2;
    }
    
    /* サイドバー下の街並みイラスト＆吹き出し */
    .sidebar-town-bg {
        margin-top: 40px;
        background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.6) 100%);
        border-radius: 20px;
        padding: 15px;
        text-align: center;
    }
    .sidebar-msg-bubble {
        background-color: #FFFFFF;
        border: 2px dashed #38BDF8;
        border-radius: 20px;
        padding:画面左側のサイドバーで、HTMLタグ（`title">防災ナビ</div>` や `sub">いざという時に...`）がそのままテキストとして表示されてしまっていますね。

Streamlitの `st.markdown` でHTMLレンダリングを有効にしていないか、書き方に誤りがある状態です。

**原因と修正方法**

`unsafe_allow_html=True` の指定が漏れているか、文字列の閉じタグ・引用符の記述が崩れている可能性が高いです。

**よくある原因1：`unsafe_allow_html=True` の不足**
```python
# ✕ 誤り（そのままテキスト出力される）
st.sidebar.markdown('<div class="title">防災ナビ</div>')

# ○ 修正
st.sidebar.markdown('<div class="title">防災ナビ</div>', unsafe_allow_html=True)
