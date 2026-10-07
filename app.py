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

# CSS設定
css_style = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;800;900&display=swap');"
    ".stApp { background: #F0F9FF; font-family: 'M PLUS Rounded 1c', sans-serif; }"
    "[data-testid='stSidebar'] { background: linear-gradient(180deg, #E0F2FE 0%, #BAE6FD 100%) !important; border-right: 3px solid #7DD3FC; }"
    ".sidebar-logo-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; background: #FFFFFF; padding: 12px; border-radius: 20px; box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2); border: 2px solid #38BDF8; }"
    ".sidebar-logo-title { font-size: 1.5rem; font-weight: 900; color: #0F172A; line-height: 1.1; }"
    ".sidebar-logo-sub { font-size: 0.72rem; color: #0284C7; font-weight: 800; margin-top: 2px; }"
    ".sidebar-msg-bubble { background-color: #FFFFFF; border: 2px dashed #38BDF8; border-radius: 20px; padding: 14px; color: #0284C7; font-size: 0.95rem; font-weight: 900; text-align: center; margin-top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }"
    ".main-header-card { background: linear-gradient(180deg, #E0F2FE 0%, #FFFFFF 100%); border: 3px solid #BAE6FD; border-radius: 28px; padding: 24px 20px 16px 20px; text-align: center; box-shadow: 0 8px 24px rgba(56, 189, 248, 0.12); margin-bottom: 20px; }"
    ".banner-title-badge { display: inline-flex; align-items: center; gap: 12px; background: #FFFFFF; padding: 10px 28px; border-radius: 50px; color: #D97706; font-weight: 900; font-size: 2rem; box-shadow: 0 4px 16px rgba(217, 119, 6, 0.15); border: 2px solid #FDE68A; margin-bottom: 8px; }"
    ".banner-sub-title { font-size: 1rem; font-weight: 800; color: #0284C7; margin-bottom: 12px; letter-spacing: 0.05em; }"
    ".search-title-text { font-size: 1.05rem; font-weight: 900; color: #0284C7; text-align: center; margin-bottom: 10px; }"
    "div[data-baseweb='input'] { border-radius: 14px !important; border: 2px solid #38BDF8 !important; background-color: #F8FAFC !important; }"
    
    /* 避難ナビカード（改修） */
    ".nav-card-box { background: #FFFFFF; border-radius: 24px; padding: 20px; border: 3px solid #38BDF8; box-shadow: 0 8px 20px rgba(56, 189, 248, 0.15); height: 100%; }"
    ".current-pos-badge { background: #E0F2FE; color: #0284C7; font-size: 0.85rem; font-weight: 900; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 6px; }"
    ".current-pos-name { font-size: 1.1rem; font-weight: 900; color: #1E293B; margin-bottom: 14px; border-bottom: 1px dashed #BAE6FD; padding-bottom: 8px; }"
    ".target-shelter-badge { background: #10B981; color: #FFFFFF; font-size: 0.85rem; font-weight: 900; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 6px; }"
    ".dest-shelter-title { font-size: 1.5rem; font-weight: 900; color: #047857; margin: 2px 0; }"
    ".dest-shelter-sub { font-size: 0.88rem; color: #475569; font-weight: 800; margin-bottom: 12px; }"
    ".route-info-pill { background-color: #ECFDF5; color: #065F46; padding: 8px 16px; border-radius: 50px; font-weight: 900; font-size: 0.9rem; display: inline-block; border: 1.5px solid #A7F3D0; }"
    
    ".yellow-card { background: #FFFDF0; border-radius: 24px; padding: 20px; border: 3px solid #FDE68A; box-shadow: 0 8px 20px rgba(253, 230, 138, 0.25); height: 100%; }"
    ".yellow-card-title { color: #D97706; font-weight: 900; font-size: 1.15rem; margin-bottom: 12px; border-bottom: 2px dashed #FDE68A; padding-bottom: 6px; }"
    ".yellow-card-item { font-size: 0.88rem; margin-bottom: 10px; color: #334155; font-weight: 800; line-height: 1.5; }"
    ".map-title-bar { font-size: 1.25rem; font-weight: 900; color: #E11D48; margin: 24px 0 12px 0; }"
    ".hazard-btn { display: block; background-color: #38BDF8; color: #FFFFFF !important; text-align: center; font-weight: 900; padding: 10px 14px; border-radius: 14px; text-decoration: none; box-shadow: 0 3px 8px rgba(56, 189, 248, 0.25); margin-top: 10px; font-size: 0.85rem; }"
    ".contact-card-box { background: #FFFFFF; border-radius: 24px; padding: 20px; border: 2px solid #E2E8F0; margin-top: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); }"
    ".contact-card-title { text-align: center; font-weight: 900; font-size: 1.05rem; color: #1E293B; margin-bottom: 14px; }"
    ".contact-grid-wrap { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; text-align: center; }"
    ".contact-item-box { background: #F8FAFC; padding: 12px 8px; border-radius: 16px; border: 1px solid #F1F5F9; }"
    ".contact-item-label { font-size: 0.75rem; color: #64748B; font-weight: 800; }"
    ".contact-item-num
