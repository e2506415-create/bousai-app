import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.parse
import json
import urllib.request
import math
import re

# ---------------------------------------------------------
# 1. ページ基本設定
# ---------------------------------------------------------
st.set_page_config(page_title="ハチボー | 八王子市 防災ハザード＆避難ナビ", layout="wide")

# ポップデザインCSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;800;900&display=swap');

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
        margin-bottom: 20px;
        background: #FFFFFF;
        padding: 12px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
        border: 2px solid #38BDF8;
    }
    .sidebar-logo-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: #0F172A;
        line-height: 1.1;
    }
    .sidebar-logo-sub {
        font-size: 0.72rem;
        color: #0284C7;
        font-weight: 800;
        margin-top: 2px;
    }

    /* サイドバー吹き出し */
    .sidebar-msg-bubble {
        background-color: #FFFFFF;
        border: 2px dashed #38BDF8;
        border-radius: 20px;
        padding: 14px;
        color: #0284C7;
        font-size: 0.95rem;
        font-weight: 900;
        text-align: center;
        margin-top: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    /* メインヘッダーカード（リニューアル） */
    .main-header-card {
        background: linear-gradient(180deg, #E0F2FE 0%, #FFFFFF 100%);
        border: 3px solid #BAE6FD;
        border-radius: 28px;
        padding: 24px 20px 16px 20px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(56, 189, 248, 0.12);
        margin-bottom: 20px;
    }

    .banner-title-badge {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        background: #FFFFFF;
        padding: 10px 28px;
        border-radius: 50px;
        color: #D97706;
        font-weight: 900;
        font-size: 2rem;
        box-shadow: 0 4px 16px rgba(217, 119, 6, 0.15);
        border: 2px solid #FDE68A;
        margin-bottom: 8px;
    }
    .banner-sub-title {
        font-size: 1rem;
        font-weight: 800;
        color: #0284C7;
        margin-bottom: 12px;
        letter-spacing: 0.05em;
    }

    /* 検索カード */
    .search-card-wrap {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 18px 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        border: 2px solid #E0F2FE;
        margin-bottom: 24px;
    }

    .search-title-text {
        font-size: 1.05rem;
        font-weight: 900;
        color: #0284C7;
        text-align: center;
        margin-bottom: 10px;
    }

    /* 入力フォームの装飾 */
    div[data-baseweb="input"] {
        border-radius: 14px !important;
        border: 2px solid #38BDF8 !important;
        background-color: #F8FAFC !important;
    }

    /* 最寄り避難所案内カード */
    .pink-card {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #FFD1DC;
        box-shadow: 0 8px 24px rgba(255, 182, 193, 0.25);
        height: 100%;
    }
    .pink-loc-tag {
        color: #334155;
        font-size: 0.95rem;
        font-weight: 900;
    }
    .pink-guide-tag {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 900;
        margin-top: 4px;
    }
    .dest-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #00A86B;
        margin: 10px 0 2px 0;
    }
    .dest
