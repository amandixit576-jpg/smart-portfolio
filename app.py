import streamlit as st
from streamlit_supabase_auth import login_form
import os
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd
# 🔥 NAYE MODULAR IMPORTS 🔥
from services.stock_data import fetch_safe_info, fetch_stock_history, fetch_financials
from utils.formatters import format_inr, format_large_number, format_df_to_crores

# --- 1. PAGE SETUP & MEMORY ---
# Purana: page_icon="📈"
# Naya: page_icon="logo.png"

st.set_page_config(page_title="Dixit Investment Group | Screener", page_icon="logo.png", layout="wide")
# --- 1.5 SEO & META TAGS FOR GOOGLE/BING SEARCH ---
seo_meta_tags = """
<meta name="description" content="Dixit Investment Group (DIG) is a premium quantitative research and stock screener terminal. Analyze Indian NSE stocks, track mutual funds, plan SIPs, and use our AI-powered CA Audit tool for deep fundamental analysis.">
<meta name="keywords" content="Stock Screener, NSE Stocks, Fundamental Analysis, SIP Calculator, CA Audit, Dixit Investment Group, Financial Terminal">
<meta name="author" content="Aman Dixit">
<meta property="og:type" content="website">
<meta property="og:url" content="https://digscreener.in/">
<meta property="og:title" content="Dixit Investment Group | Premium Wealth Terminal">
<meta property="og:description" content="The Modern AI-Powered Screener & Quant Terminal for Indian Investors.">
<meta property="og:image" content="https://raw.githubusercontent.com/amandixit576-jpg/dig-screener-official/main/logo.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Dixit Investment Group | Premium Wealth Terminal">
<meta name="twitter:description" content="The Modern AI-Powered Screener & Quant Terminal for Indian Investors.">
<meta name="twitter:image" content="https://raw.githubusercontent.com/amandixit576-jpg/dig-screener-official/main/logo.png">
"""
st.markdown(seo_meta_tags, unsafe_allow_html=True)

if 'current_view' not in st.session_state: st.session_state.current_view = "HOME"
if 'portfolio' not in st.session_state: st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Price", "Quantity", "Hold Type"])
if 'watchlist' not in st.session_state: st.session_state.watchlist = ["RELIANCE.NS", "TCS.NS"]

# --- 2. CSS & ADAPTIVE THEME (UPTIMEROBOT SAAS THEME) ---
hide_st_style = """
    <style>
    /* 🔥 Hide Streamlit Branding 🔥 */
    #MainMenu, footer, header {visibility: hidden; height: 0px;}
    [data-testid="stToolbarActions"], [data-testid="collapsedControl"], section[data-testid="stSidebar"] {display: none !important;}
    [data-testid="stAppDeployButton"], .stAppDeployButton {display: none !important;}
    div[class^="viewerBadge_container"], .viewerBadge_container__1QSob {display: none !important;}
    [data-testid="stStatusWidget"], [data-testid="stDecoration"] {display: none !important;}

    /* 🟢 UPTIMEROBOT PREMIUM SAAS THEME 🟢 */
    /* Global Background (Deep Slate instead of pure black) */
    .stApp {
        background-color: #111827 !important;
        color: #F3F4F6 !important;
    }

    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 98% !important; }

    /* 🔥 SEARCH BAR FIX 🔥 */
    div[data-baseweb="input"] > div {
        background-color: #1F2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }
    input { color: #F3F4F6 !important; }

    /* 🔥 NORMAL BUTTONS (Nav, Trending) - Fix for White Boxes 🔥 */
    div[data-testid="stButton"] button[kind="secondary"] {
        background-color: #1F2937 !important; /* Soft Dark Grey */
        border: 1px solid #374151 !important;
        border-radius: 24px !important; /* Pill Shape like UptimeRobot */
        padding: 5px 20px !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stButton"] button[kind="secondary"] p {
        color: #9CA3AF !important; /* Slate Grey Text */
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: #00E570 !important; /* Modern SaaS Green */
        background-color: rgba(0, 229, 112, 0.05) !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover p {
        color: #00E570 !important;
    }

    /* 🔥 PRIMARY BUTTON (Search & Account) 🔥 */
    div[data-testid="stButton"] button[kind="primary"] { 
        background-color: #00E570 !important; /* Modern SaaS Green */
        border: none !important;
        border-radius: 24px !important; /* Pill Shape */
        box-shadow: 0 4px 14px 0 rgba(0, 229, 112, 0.2) !important;
    }
    div[data-testid="stButton"] button[kind="primary"] p {
        color: #111827 !important; /* Dark Text */
        font-weight: bold !important;
    }

    /* TEXT COLORS */
    .main-title { text-align: center; color: #00E570 !important; font-size: 3.5rem; font-weight: 800; margin-bottom: 0px; font-family: 'Segoe UI', sans-serif; letter-spacing: -1.5px;}
    .sub-title { text-align: center; color: #F3F4F6 !important; font-size: 1.2rem; font-weight: 600; margin-top: 0px; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.9;}
    .tag-line { text-align: center; color: #9CA3AF !important; font-size: 1rem; font-weight: 400; margin-top: 0px; margin-bottom: 30px; font-style: italic;}

    /* CARDS & METRICS (Sleek Dark Boxes) */
    .basket-card, div[data-testid="stMetric"] { 
        background-color: #1F2937 !important; 
        border: 1px solid #374151 !important; 
        border-radius: 12px !important; 
    }
    div[data-testid="stMetric"] { border-left: 4px solid #00E570 !important; padding: 15px; }
    .basket-card:hover { border-color: #00E570 !important; transform: translateY(-2px); }
    .basket-title, div[data-testid="stMetricValue"] > div { color: #00E570 !important; }
    .basket-card p { color: #9CA3AF !important; }

    /* TABS STYLING */
    button[data-baseweb="tab"] { color: #9CA3AF !important; }
    button[aria-selected="true"] { color: #00E570 !important; border-bottom-color: #00E570 !important; }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

import requests


# --- 4. LEAD GENERATION & SIDEBAR ---
TOP_STOCKS = {"RELIANCE.NS": "Reliance", "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC Bank", "INFY.NS": "Infosys", "ZOMATO.NS": "Zomato", "ITC.NS": "ITC", "SBIN.NS": "SBI"}

@st.dialog("👑 Unlock Premium Access")
def premium_signup():
    st.markdown("Join **Dixit Investment Group** for algorithmic access & fundamental models.")
    name, city = st.text_input("Full Name"), st.text_input("City")
    if name and city:
        st.link_button("📲 Chat to get Code", f"https://wa.me/917052360459?text={urllib.parse.quote(f'Hello Dixit Investment Group! I want to purchase the Premium Access Code. Name: {name}, City: {city}')}", type="primary", use_container_width=True)
    else:
        st.button("📲 Chat to get Code", type="primary", disabled=True, use_container_width=True)

# --- TOP NAVIGATION BAR (TICKER STYLE) ---
nav1, nav2, nav3, nav4, nav5, nav6, nav7, nav8 = st.columns([1.5, 1, 1, 1, 1, 1.5, 1.5, 1.2])

with nav1: st.markdown("<a href='/' target='_self' style='text-decoration: none;'><h4 style='color:#1E88E5; margin-top:5px; margin-bottom:0px;'>⚜️ DIG</h4></a>", unsafe_allow_html=True)
with nav2: 
    if st.button("Home", use_container_width=True): 
        st.session_state.current_view = "HOME"
        st.rerun()
with nav3: 
    if st.button("Compare", use_container_width=True): st.switch_page("pages/1_Compare.py")
with nav4: 
    if st.button("MFs", use_container_width=True): st.switch_page("pages/2_Mutual_Funds.py")
with nav5: 
    if st.button("Baskets", use_container_width=True): st.switch_page("pages/3_Baskets.py")
with nav6: st.empty() 
with nav7: 
    if st.button("👑 Premium", use_container_width=True): premium_signup()
with nav8: 
    if st.button("🔒 Account", type="primary", use_container_width=True): st.switch_page("pages/4_Premium_Account.py")

st.write("---")
@st.cache_data(ttl=1800)
def get_live_news(company_name):
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(f'{company_name} share stock news India')}&hl=en-IN&gl=IN&ceid=IN:en"
        root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read())
        return [{'title': i.find('title').text.rsplit(' - ', 1)[0] if ' - ' in i.find('title').text else i.find('title').text, 'link': i.find('link').text, 'date': i.find('pubDate').text[5:16]} for i in root.findall('.//item')[:4]]
    except: return []

# --- 5. APP SECTIONS ---

# ---> 🏠 HOME PAGE <---
if st.session_state.current_view == "HOME":
    
    # --- 🌟 THE DIG PREMIUM HERO SECTION ---
    st.write("<br><br>", unsafe_allow_html=True) 
    st.markdown("<h1 style='text-align: center; color: #1E88E5; font-size: 3.5rem;'>⚜️ Dixit Investment Group</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #888; font-weight: normal;'>The Modern Stock Screener that helps you pick better stocks.</h4>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)

    # 🔍 SINGLE BIG SEARCH BAR + GREEN BUTTON
    c1, search_col, c3 = st.columns([1, 2, 1])
    with search_col:
        search_input = st.text_input("Search", label_visibility="collapsed", placeholder="🔍 Type a Company Name or NSE Symbol (e.g., ITC)")
        
        # Ye 'type="primary"' aapke button ko wahi mast Green color dega!
        if st.button("Search & Analyze", type="primary", use_container_width=True):
            if search_input: 
                sym = search_input.upper().strip()
                if not (sym.endswith('.NS') or sym.endswith('.BO')): 
                    sym += '.NS'
                st.session_state.current_view = sym
                st.rerun()
            else:
                st.warning("Bhai, pehle company ka naam toh likho!")

    # 🔘 TRENDING BUTTONS (Ab click karne pe mast kaam karenge)
    st.write("<div style='text-align: center; margin-top: 15px; color: #888;'><b>What's Trending:</b></div>", unsafe_allow_html=True)
    t_spacer1, t_btn1, t_btn2, t_btn3, t_btn4, t_spacer2 = st.columns([2, 1, 1, 1, 1, 2])
    
    with t_btn1: 
        if st.button("ITC", use_container_width=True): 
            st.session_state.current_view = "ITC.NS"
            st.rerun()
    with t_btn2: 
        if st.button("RELIANCE", use_container_width=True): 
            st.session_state.current_view = "RELIANCE.NS"
            st.rerun()
    with t_btn3: 
        if st.button("HDFCBANK", use_container_width=True): 
            st.session_state.current_view = "HDFCBANK.NS"
            st.rerun()
    with t_btn4:
        if st.button("ZOMATO", use_container_width=True): 
            st.session_state.current_view = "ZOMATO.NS"
            st.rerun()
            
    st.write("<br><br><hr>", unsafe_allow_html=True)
    
    # 👇 Yahan se aapke SIP Planner aur Portfolio ke Tabs shuru honge
    
    ht1, ht2 = st.tabs(["🎯 Goal-Based SIP Planner", "💼 My Virtual Portfolio & Tax Audit"])
    with ht1:
        st.markdown("### Plan for your next lifestyle milestone")
        calc_col1, calc_col2 = st.columns([1, 2])
        with calc_col1:
            goal_type = st.selectbox("Select Financial Goal:", ["Custom Wealth Creation", "Himalayan Trek Fund (Nag Tibba - ₹25k)", "Luxury Watch Milestone (₹1.5L)", "Family Celebration Fund (₹10L)"])
            default_sip, default_years = 5000, 10
            if "Trek" in goal_type: default_sip, default_years = 2500, 1
            elif "Watch" in goal_type: default_sip, default_years = 6000, 2
            elif "Family" in goal_type: default_sip, default_years = 12000, 5
            
            sip_amount = st.number_input("Monthly SIP (₹)", min_value=500, value=default_sip, step=500)
            sip_years = st.slider("Investment Period (Years)", 1, 30, default_years)
            sip_rate = st.slider("Expected Annual Return (%)", 5, 25, 12)
        with calc_col2:
            monthly_rate = sip_rate / 12 / 100
            months = sip_years * 12
            invested = sip_amount * months
            fv = sip_amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
            st.success(f"### Estimated Goal Corpus: ₹{format_inr(round(fv, 0))}")
            w1, w2 = st.columns(2)
            w1.metric("Total Invested", f"₹{format_inr(round(invested, 0))}")
            w2.metric("Est. Wealth Gained", f"₹{format_inr(round(fv - invested, 0))}")

    with ht2:
        st.markdown("### Virtual Trade Book & Capital Gains Estimator")
        pc1, pc2, pc3, pc4, pc5 = st.columns(5)
        with pc1: p_tick = st.selectbox("Asset", list(TOP_STOCKS.keys()))
        with pc2: p_qty = st.number_input("Quantity", min_value=1, value=10)
        with pc3: p_buy = st.number_input("Buy Price (₹)", min_value=1.0, value=100.0)
        with pc4: p_type = st.selectbox("Holding Type", ["Short-Term (< 1 Yr)", "Long-Term (> 1 Yr)"])
        with pc5: 
            st.write("")
            if st.button("➕ Add Trade", use_container_width=True):
                st.session_state.portfolio = pd.concat([st.session_state.portfolio, pd.DataFrame({"Ticker": [p_tick], "Buy Price": [p_buy], "Quantity": [p_qty], "Hold Type": [p_type]})], ignore_index=True)
                st.success("Trade Added!")
        
        if not st.session_state.portfolio.empty:
            df_port = st.session_state.portfolio.copy()
            df_port["Live Price"] = [yf.Ticker(t).history(period="1d")['Close'].iloc[-1] if not yf.Ticker(t).history(period="1d").empty else 0 for t in df_port["Ticker"]]
            df_port["Total Invested"] = df_port["Buy Price"] * df_port["Quantity"]
            df_port["Current Value"] = df_port["Live Price"] * df_port["Quantity"]
            df_port["Gross P&L (₹)"] = df_port["Current Value"] - df_port["Total Invested"]
            
            def calc_tax(row):
                if row["Gross P&L (₹)"] <= 0: return 0
                if "Short-Term" in row["Hold Type"]: return row["Gross P&L (₹)"] * 0.20 
                else: return row["Gross P&L (₹)"] * 0.125 
                
            df_port["Est. Tax Liability"] = df_port.apply(calc_tax, axis=1)
            df_port["Net Post-Tax P&L"] = df_port["Gross P&L (₹)"] - df_port["Est. Tax Liability"]
            
            display_df = df_port.copy()
            for col in ["Buy Price", "Live Price", "Total Invested", "Current Value", "Gross P&L (₹)", "Est. Tax Liability", "Net Post-Tax P&L"]:
                display_df[col] = display_df[col].apply(lambda x: format_inr(round(x, 2)))
                
            st.dataframe(display_df, use_container_width=True)
            st.caption("ℹ️ *Tax estimator reflects new Indian Budget rules: 20% for STCG and 12.5% for LTCG.*")
# =====================================================================
# 🛑 ENGINE SHURU (Ye line ekdum LEFT WALL - 0 spaces par honi chahiye) 🛑
# =====================================================================
if st.session_state.current_view != "HOME":
    user_ticker = st.session_state.current_view

# 🛡️ BULLETPROOF DATA FETCHING (ANTI-BLOCK)
    with st.spinner(f"Fetching Institutional Data for {user_ticker}..."):
        import yfinance as yf
        
        # Yahoo ab khud anti-block handle karta hai, so simple Ticker call:
        tkr = yf.Ticker(user_ticker)
        
        try:
            data = tkr.history(period="1y")
        except:
            data = None
            
        try:
            info = tkr.info
        except:
            info = {}

    # 🟢 ASLI ENGINE YAHAN SE SHURU HOTA HAI
    if data is not None and not data.empty:
        
        # --- 🌟 FINOLOGY STYLE PREMIUM HEADER ---
        company_name = info.get('longName', info.get('shortName', user_ticker.replace('.NS', '')))
        display_name = company_name  # 👈 Isko aage khiskana hai
        sector = info.get('sector', 'N/A') # 👈 Isko bhi aage khiskana hai
        industry = info.get('industry', 'N/A') # 👈 Isko bhi aage khiskana hai
        
        st.markdown(f"<span style='color: #888; font-size: 14px;'>DIG Terminal > Company > <b style='color: #00E570;'>{user_ticker.replace('.NS', '')} Share Price</b></span>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='margin-top: -10px; margin-bottom: 5px; font-size: 2.8rem;'>{company_name}</h1>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='display: flex; gap: 12px; align-items: center; margin-bottom: 25px; flex-wrap: wrap;'>
            <span style='background-color: #1F2937; padding: 5px 10px; border-radius: 6px; font-size: 13px; color: #E5E7EB; border: 1px solid #374151;'>
                NSE: <b style='color: white;'>{user_ticker.replace('.NS', '')}</b>
            </span>
            <span style='background-color: #1F2937; padding: 5px 10px; border-radius: 6px; font-size: 13px; color: #E5E7EB; border: 1px solid #374151;'>
                SECTOR: <b style='color: #00E570;'>{sector}</b>
            </span>
            <span style='background-color: #1F2937; padding: 5px 10px; border-radius: 6px; font-size: 13px; color: #E5E7EB; border: 1px solid #374151;'>
                INDUSTRY: <b style='color: #00E570;'>{industry}</b>
            </span>
        </div>
        """, unsafe_allow_html=True)

        # --- PRICE CALCULATION ---
        curr_price, prev_price = data['Close'].iloc[-1], data['Close'].iloc[-2]
        chg = curr_price - prev_price
        pct = (chg/prev_price)*100
        color = "#16A34A" if chg >= 0 else "#DC2626"
        arrow = "▲" if chg >= 0 else "▼"

        # 2. Smart Fallback: History-based calculation for N/A values
        hist_1y = fetch_stock_history(user_ticker, period="1y")
        if not hist_1y.empty:
            if not info.get('fiftyTwoWeekHigh'): info['fiftyTwoWeekHigh'] = hist_1y['High'].max()
            if not info.get('fiftyTwoWeekLow'): info['fiftyTwoWeekLow'] = hist_1y['Low'].min()

        c1, c2 = st.columns([3, 1])
        
        # Left Side: Name and Sync Button
        
        
        if c1.button("🔄 Sync Live Data", help="Click to force refresh financial metrics and company info"):
            st.cache_data.clear()
            st.rerun()
        
        # Right Side: Price and Percentage (Intact as per your code)
        c2.markdown(f"<h2 style='text-align: right; margin-bottom: 0px;'>₹{format_inr(round(curr_price, 2))}</h2>", unsafe_allow_html=True)
        c2.markdown(f"<p style='text-align: right; color: {color}; font-weight: bold;'>{arrow} {format_inr(round(chg,2))} ({round(pct,2)}%)</p>", unsafe_allow_html=True)

        st.write("")
        
        # --- TICKER STYLE CARDS (Price Summary & Essentials) ---
        card_col1, card_col2 = st.columns([1, 1.5])
        
        with card_col1:
            with st.container(border=True):
                st.markdown("#### Price Summary")
                st.write("")
                p1, p2 = st.columns(2)
                p1.metric("TODAY'S HIGH", f"₹{format_inr(info.get('dayHigh', data['High'].iloc[-1]))}")
                p2.metric("TODAY'S LOW", f"₹{format_inr(info.get('dayLow', data['Low'].iloc[-1]))}")
                st.write("")
                p3, p4 = st.columns(2)
                p3.metric("52 WEEK HIGH", f"₹{format_inr(info.get('fiftyTwoWeekHigh', 0))}")
                p4.metric("52 WEEK LOW", f"₹{format_inr(info.get('fiftyTwoWeekLow', 0))}")

            with st.container(border=True):
                st.markdown("#### DIG Quant Rating 🤖")
                pe = info.get('trailingPE', 0)
                if pe > 0 and pe < 20: st.success("🌟 **Valuation:** Highly Attractive")
                elif pe >= 20 and pe < 40: st.info("⚖️ **Valuation:** Fairly Valued")
                else: st.warning("⚠️ **Valuation:** Expensive")
                
                sma_trend = data['Close'].rolling(50).mean().iloc[-1]
                if curr_price > sma_trend: st.success("📈 **Momentum:** Strong Bullish Breakout")
                else: st.error("📉 **Momentum:** Bearish Consolidation Phase")

        with card_col2:
            with st.container(border=True):
                st.markdown("#### Company Essentials")
                st.write("")
                e1, e2, e3 = st.columns(3)
            
            # Market Cap & EV ko seedha Crores (Cr) mein convert kiya taaki text na kate
            mcap = info.get('marketCap', 0)
            e1.metric("MARKET CAP", f"₹{mcap/10000000:,.0f} Cr" if mcap else "N/A")
            
            eval_val = info.get('enterpriseValue', 0)
            e2.metric("ENTERPRISE VAL", f"₹{eval_val/10000000:,.0f} Cr" if eval_val else "N/A")
            
            pe = info.get('trailingPE')
            e3.metric("P/E RATIO", round(pe, 2) if pe else "N/A")
            
            st.write("")
            e4, e5, e6 = st.columns(3)
            
            div_yield = info.get('dividendYield')
            e4.metric("DIV. YIELD", f"{round(div_yield * 100, 2)}%" if div_yield else "0.00%")
            
            bv = info.get('bookValue')
            e5.metric("BOOK VALUE", f"₹{round(bv, 2)}" if bv else "N/A")
            
            # Yahan asali galti thi! Face value hata kar ab hum EPS dikha rahe hain
            eps = info.get('trailingEPS')
            e6.metric("EPS (TTM)", f"₹{round(eps, 2)}" if eps else "N/A")
            
            st.write("")
            e7, e8, e9 = st.columns(3)
            
            # Debt ko bhi Crores (Cr) mein dikhayenge
            debt = info.get('totalDebt', 0)
            e7.metric("DEBT", f"₹{debt/10000000:,.0f} Cr" if debt else "N/A")
            
            roe = info.get('returnOnEquity')
            e8.metric("ROE", f"{round(roe * 100, 2)}%" if roe else "N/A")
            
            roce = info.get('returnOnCapitalEmployed')
            e9.metric("ROCE", f"{round(roce * 100, 2)}%" if roce else "N/A")

        st.write("---")
        data['SMA50'] = data['Close'].rolling(50).mean()
         # ISKE THEEK NICHE AAPKA PURANA 'tab1, tab2 = st.tabs(...)' WALA CODE HOGA
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📊 Price Chart", "📋 Pro Ratios", "📑 Financials", "🏢 Corp Actions", "📰 Live News", "💎 AI Quant", "📥 Export", "🧑‍💼 CA's Audit"])

        with tab1:
            st.markdown("### 📊 Advanced Technical Chart")
            data['SMA50'] = data['Close'].rolling(50).mean()
            t_obj = yf.Ticker(user_ticker)
            data['20SMA'] = data['Close'].rolling(20).mean()
            data['Upper_BB'] = data['20SMA'] + 2 * data['Close'].rolling(20).std()
            data['Lower_BB'] = data['20SMA'] - 2 * data['Close'].rolling(20).std()
            
            delta = data['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            data['RSI'] = 100 - (100 / (1 + (ema_up / ema_down)))
            
            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            data['MACD'] = exp1 - exp2
            data['Signal Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

            indicators = st.multiselect("Overlay Technical Indicators:", ["50 SMA", "200 SMA", "Bollinger Bands", "RSI (14)", "MACD"], default=["50 SMA"])

            has_rsi, has_macd = "RSI (14)" in indicators, "MACD" in indicators
            rows = 1 + int(has_rsi) + int(has_macd)
            row_heights = [0.6] + [0.2] * (rows - 1) if rows > 1 else [1]
            
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=row_heights)
            fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
            
            if "50 SMA" in indicators: fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='orange', width=1.5), name='50 SMA'), row=1, col=1)
            if "200 SMA" in indicators:
                data['SMA200'] = data['Close'].rolling(200).mean()
                fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], line=dict(color='blue', width=1.5), name='200 SMA'), row=1, col=1)
            if "Bollinger Bands" in indicators:
                fig.add_trace(go.Scatter(x=data.index, y=data['Upper_BB'], line=dict(color='gray', dash='dash'), name='Upper BB'), row=1, col=1)
                fig.add_trace(go.Scatter(x=data.index, y=data['Lower_BB'], line=dict(color='gray', dash='dash'), fill='tonexty', fillcolor='rgba(128,128,128,0.1)', name='Lower BB'), row=1, col=1)

            current_row = 2
            if has_rsi:
                fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='purple', width=1.5), name='RSI'), row=current_row, col=1)
                fig.add_hline(y=70, line_dash="dot", line_color="red", row=current_row, col=1) 
                fig.add_hline(y=30, line_dash="dot", line_color="green", row=current_row, col=1) 
                fig.update_yaxes(title_text="RSI", row=current_row, col=1, range=[0, 100])
                current_row += 1

            if has_macd:
                fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], line=dict(color='blue', width=1.5), name='MACD'), row=current_row, col=1)
                fig.add_trace(go.Scatter(x=data.index, y=data['Signal Line'], line=dict(color='orange', width=1.5), name='Signal'), row=current_row, col=1)
                colors = ['green' if val >= 0 else 'red' for val in (data['MACD'] - data['Signal Line'])]
                fig.add_trace(go.Bar(x=data.index, y=(data['MACD'] - data['Signal Line']), marker_color=colors, name='Histogram'), row=current_row, col=1)
                fig.update_yaxes(title_text="MACD", row=current_row, col=1)

            fig.update_layout(template="plotly_white", margin=dict(t=10, b=10, l=10, r=10), height=700 if rows > 1 else 500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### 📈 Comprehensive Financial Metrics")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Market Cap", f"₹{format_large_number(info.get('marketCap'))}")
            r2.metric("Current Price", f"₹{format_inr(info.get('currentPrice', 0))}")
            r3.metric("52 Week High", f"₹{format_inr(info.get('fiftyTwoWeekHigh', 0))}")
            r4.metric("52 Week Low", f"₹{format_inr(info.get('fiftyTwoWeekLow', 0))}")
            
            st.write("")
            r5, r6, r7, r8 = st.columns(4)
            r5.metric("Stock P/E", round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A")
            r6.metric("Book Value", f"₹{format_inr(round(info.get('bookValue', 0), 2))}" if info.get('bookValue') else "N/A")
            r7.metric("Dividend Yield", f"{round(info.get('dividendYield', 0)*100, 2)}%" if info.get('dividendYield') else "0.00%")
            r8.metric("ROCE", f"{round(info.get('returnOnCapitalEmployed', 0)*100, 2)}%" if info.get('returnOnCapitalEmployed') else "N/A") 
            
            st.write("")
            r9, r10, r11, r12 = st.columns(4)
            r9.metric("ROE", f"{round(info.get('returnOnEquity', 0)*100, 2)}%" if info.get('returnOnEquity') else "N/A")
            r10.metric("Face Value", f"₹{info.get('regularMarketPrice', 'N/A')}") 
            r11.metric("Debt to Equity", round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else "N/A")
            r12.metric("Price to Book", round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else "N/A")
            
            st.write("---")
            st.markdown("### 🐋 Shareholding Pattern")
            insider = round(info.get('heldPercentInsiders', 0) * 100, 2)
            inst = round(info.get('heldPercentInstitutions', 0) * 100, 2)
            st.write(f"**Promoters:** {insider}% | **Institutions (FII/DII):** {inst}% | **Public:** {round(100 - insider - inst, 2)}%")

        with tab3:
            st.markdown("### 📑 Annual Financial Statements (In Crores)")
            stmt1, stmt2 = st.tabs(["Income Statement", "Balance Sheet"])
            with stmt1:
                try:
                    fin_df = t_obj.financials
                    if not fin_df.empty: st.dataframe(format_df_to_crores(fin_df.dropna(how='all')), use_container_width=True)
                    else: st.warning("Income Statement data not available.")
                except: st.warning("Error fetching Income Statement.")
            with stmt2:
                try:
                    bs_df = t_obj.balance_sheet
                    if not bs_df.empty: st.dataframe(format_df_to_crores(bs_df.dropna(how='all')), use_container_width=True)
                    else: st.warning("Balance Sheet data not available.")
                except: st.warning("Error fetching Balance Sheet.")

        with tab4:
            st.markdown("### 📅 Recent Dividends & Corporate Actions")
            try:
                divs = t_obj.dividends.tail(5)
                if not divs.empty: st.write(divs)
                else: st.info("No recent dividend data found.")
            except: st.warning("Corporate action data unavailable.")

        with tab5:
            st.markdown("### 📰 Live Market News & AI Sentiment")
            sma_trend = data['SMA50'].iloc[-1]
            if curr_price > sma_trend:
                st.success("🤖 **AI Sentiment Radar:** The current market sentiment for this asset leans **BULLISH** based on prevailing momentum indices.")
            else:
                st.error("🤖 **AI Sentiment Radar:** The current market sentiment for this asset leans **BEARISH** indicating near-term consolidation or weakness.")
            
            st.write("---")
            live_news = get_live_news(display_name)
            if live_news:
                for n in live_news:
                    st.markdown(f"🔹 **[{n['title']}]({n['link']})**")
                    st.caption(f"🕒 {n['date']}")
                    st.divider()
            else: st.info("No recent news found.")

        with tab6:
            st.markdown("### 💎 AI Quant & Market Screener")
            entered_code = st.text_input("🔑 Enter Premium Access Code:", type="password")
            if entered_code == "AMANPRO":
                st.success("🔓 Premium Access Granted! Running Live Quant Models...")
                st.write("#### 🎯 Today's High-Probability Breakout Setups")
                if st.button("🔍 Scan Top Market Assets", type="primary"):
                    with st.spinner("Scanning real-time market data... This takes a few seconds."):
                        top_picks = []
                        SCAN_LIST = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS", "SBIN.NS", "ZOMATO.NS", "BHARTIARTL.NS"]
                        for sym in SCAN_LIST:
                            try:
                                scan_data = yf.Ticker(sym).history(period="3mo")
                                if len(scan_data) > 50:
                                    cp = scan_data['Close'].iloc[-1]
                                    sm = scan_data['Close'].rolling(50).mean().iloc[-1]
                                    d = scan_data['Close'].diff()
                                    rs = 100 - (100 / (1 + (d.clip(lower=0).ewm(com=13, adjust=False).mean() / (-1 * d.clip(upper=0)).ewm(com=13, adjust=False).mean())))
                                    cr = rs.iloc[-1]
                                    if cp > sm and cr >= 60:
                                        top_picks.append({"Asset": sym.replace('.NS', ''), "Price (₹)": round(cp, 2), "RSI Strength": round(cr, 2), "Signal": "Bullish 🚀"})
                            except: pass
                        if top_picks: st.table(pd.DataFrame(top_picks).sort_values(by="RSI Strength", ascending=False))
                        else: st.info("No strong momentum setups found right now.")
                
                st.write("---")
                st.write("#### 📊 Asset Valuation Model")
                pe = info.get('trailingPE', 0)
                if pe > 0 and pe < 20: st.success("✅ **Verdict: STRONG BUY** (Undervalued: Trading at discount).")
                elif pe >= 20 and pe < 40: st.info("⚖️ **Verdict: HOLD / SIP** (Fairly Valued: Normal pricing).")
                else: st.warning("⚠️ **Verdict: CAUTION** (Overpriced: High premium).")
            elif entered_code: st.error("❌ Invalid Code.")

        with tab7:
            st.markdown("### 📸 Influencer Content Dashboard")
            st.write("Generate ready-to-post scripts and branded reports for your social media audience.")
            
            pe_val = info.get('trailingPE', 0)
            trend_text = "bullish breakout territory" if curr_price > data['SMA50'].iloc[-1] else "a solid accumulation zone"
            val_text = "undervalued compared to historical peers" if (pe_val > 0 and pe_val < 25) else "trading at a premium, demanding caution"
            
            script = f"""**[HOOK]** Is {display_name} the next big wealth creator? 💸📉
            
**[BODY]**
Hey everyone, let's look at the data coming fresh from the DIG Screener terminal today. 
Currently trading at ₹{format_inr(round(curr_price, 2))}, {display_name} is sitting in {trend_text}. 

Looking at the fundamentals, it's {val_text}. If you hold this in your portfolio, keep an eye on these levels.

**[CTA]**
Want to see the deep-dive audit? Hit the link in my bio to use my custom screener! 🚀

#StockMarket #Investing #DixitInvestmentGroup #{display_name.replace(' ', '')}"""
            
            st.text_area("📝 Auto-Generated Reel/Post Script (Copy-Paste Ready):", script, height=250)
            
            st.write("---")
            report_df = pd.DataFrame({"Metric": ["Company", "Price", "P/E", "ROE", "Debt/Eq", "Analysis By"], "Value": [display_name, curr_price, info.get('trailingPE'), info.get('returnOnEquity'), info.get('debtToEquity'), "DIG Screener | 📸 @digscreener.in"]})
            st.download_button(label="📥 Download Branded CSV Report", data=report_df.to_csv(index=False).encode('utf-8'), file_name=f"{user_ticker}_AmanCreats_Report.csv", mime="text/csv", type="primary")

        with tab8:
            st.markdown("### 🧑‍💼 CA's Audit Desk (Advanced Risk Lens)")
            st.caption("Forensic level checks to identify working capital stress and governance red flags.")
            
            ocf = info.get('operatingCashflow')
            net_inc = info.get('netIncomeToCommon')
            
            st.markdown("#### 1. Earnings Quality Check")
            if pd.notna(ocf) and pd.notna(net_inc) and ocf != 0:
                if net_inc > 0 and ocf < 0: st.error("🚩 **Red Flag:** The company is reporting paper profits, but actual Operating Cash Flow is NEGATIVE.")
                elif ocf > net_inc: st.success("✅ **Clean:** Operating Cash Flow is higher than Net Income, indicating high-quality cash realization.")
                else: st.info("⚖️ **Standard:** Cash flow aligns relatively closely with reported income.")
            else: st.info("Detailed cash flow audit data is currently unavailable on free tier.")
                
            st.markdown("#### 2. Liquidity & Solvency Audit")
            cr = info.get('currentRatio')
            if pd.notna(cr):
                if cr < 1: st.warning(f"⚠️ **Caution:** Current Ratio is {round(cr, 2)}. Short-term liabilities exceed short-term assets.")
                else: st.success(f"✅ **Healthy:** Current Ratio is {round(cr, 2)}, indicating sufficient short-term liquidity.")
            else: st.write("Data not available.")

    else:
        st.warning("⚠️ Stock data unavailable right now. Try another NSE symbol like TCS, ITC, INFY.")

# --- 6. MEGA FOOTER ---
mega_footer = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
.premium-footer { background-color: var(--secondary-background-color); padding: 50px 20px 30px 20px; color: var(--text-color); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border-top: 1px solid rgba(128,128,128,0.2); margin-top: 60px; }
.footer-grid { display: flex; flex-wrap: wrap; justify-content: space-between; margin-bottom: 40px; max-width: 1200px; margin-left: auto; margin-right: auto; }
.footer-col { flex: 1; min-width: 200px; margin-bottom: 20px; }
.footer-brand { flex: 1.6; padding-right: 40px; }
.footer-col h4 { color: var(--text-color); font-size: 16px; margin-bottom: 18px; font-weight: 600; letter-spacing: 0.5px; opacity: 0.9;}
.footer-col a { display: block; color: var(--text-color); text-decoration: none; font-size: 14px; margin-bottom: 12px; transition: 0.3s; opacity: 0.7;}
.footer-col a:hover { color: #1E88E5; padding-left: 5px; opacity: 1;}
.social-icons { display: flex; gap: 15px; margin-top: 20px; }
.social-icons a { display: inline-flex !important; align-items: center; justify-content: center; width: 36px; height: 36px; background-color: rgba(128,128,128,0.2); border-radius: 50%; color: var(--text-color) !important; font-size: 16px; transition: 0.3s; padding: 0 !important; }
.social-icons a:hover { background-color: #1E88E5; color: white !important; transform: translateY(-3px); }
.footer-bottom { max-width: 1200px; margin: 0 auto; border-top: 1px solid rgba(128,128,128,0.2); padding-top: 25px; font-size: 11px; line-height: 1.6; color: var(--text-color); opacity: 0.6;}
.footer-bottom p { margin: 6px 0; }
.brand-title { color: #1E88E5; font-size: 22px; font-weight: bold; margin-bottom: 15px; letter-spacing: 1px; }
.block-container { padding-bottom: 0rem !important; }
</style>
<div class="premium-footer">
<div class="footer-grid">
<div class="footer-col footer-brand">
<div class="brand-title">⚜️ DIXIT INVESTMENT GROUP</div>
<p style="font-size: 13px; line-height: 1.7; text-align: justify;">Dixit Investment Group (DIG) is a premier quantitative research and portfolio management terminal designed for modern value investors and financial professionals. Built on the principles of deep fundamental analysis and data-driven investing, DIG provides institutional-grade market screeners, real-time SIP planning, and comprehensive tax audit tools. Our mission is to democratize elite financial analytics, empowering retail investors to make calculated, risk-adjusted decisions in the Indian equity markets.</p>
<div class="social-icons">
<a href="https://instagram.com/digscreener.in" target="_blank" title="Instagram"><i class="fab fa-instagram"></i></a>
<a href="https://www.linkedin.com/in/amandixit29" target="_blank" title="LinkedIn"><i class="fab fa-linkedin-in"></i></a>
<a href="#" target="_blank" title="Twitter/X"><i class="fab fa-x-twitter"></i></a>
<a href="#" target="_blank" title="YouTube"><i class="fab fa-youtube"></i></a>
</div>
</div>
<div class="footer-col">
  <h4>Company</h4>
  <a href="/About_Us" target="_self">About Us</a>
  <a href="/Our_Vision" target="_self">Our Vision</a>
  <a href="/Leadership" target="_self">Leadership</a>
  <a href="/Careers" target="_self">Careers</a>
</div>
<div class="footer-col">
  <h4>Terminal Tools</h4>
  <a href="/Custom_Screener" target="_self">Stock Screener 🎛️</a>
  <a href="/Financial_Statements" target="_self">5-Year Financials 📚</a>
  <a href="/Shareholding" target="_self">Shareholding 👥</a> <a href="/Compare" target="_self">Smart Peer Compare</a>
  <a href="/Intrinsic_Value" target="_self">DCF Calculator</a>
  <a href="/Forensic_Audit" target="_self">Forensic Audit 🕵️‍♂️</a>
  <a href="/Tax_Audit" target="_self">Tax Audit & Portfolio</a>
</div>
<div class="footer-col">
  <h4>Legal & Support</h4>
  <a href="/Help_Center" target="_self">Help Center</a>
  <a href="/Privacy_Policy" target="_self">Privacy Policy</a>
  <a href="/Terms_of_Use" target="_self">Terms of Use</a>
  <a href="/Regulatory_Disclaimer" target="_self">Regulatory Disclaimer</a>
</div>
</div>
<div class="footer-bottom">
<p><strong>SEBI Registration:</strong> INA000000000 (Dummy - For Educational Purposes Only) | <strong>Headquarters:</strong> Lucknow, Uttar Pradesh</p>
<p>Copyright © 2026 Dixit Investment Group. All Rights Reserved. | Data Feed provided by Third-Party APIs | Prices may be delayed by 15 minutes.</p>
<p><strong>Important Disclaimer:</strong> Though Dixit Investment Group is a highly advanced tool for financial analysis, it in no way recommends the fair value of any companies (since that is always subjective). Informed decision making and taking calculated risk is recommended for you to make the most out of equity investing. Therefore, the investors are hereby advised to use this terminal purely as an analytical research tool and apply their discretion while investing.</p>
</div>
</div>
"""
st.markdown(mega_footer, unsafe_allow_html=True)
# --- 7. FLOATING "GO TO TOP" BUTTON ---
go_to_top_html = """
    <a href="#" id="gototopBtn" title="Go to top">⬆</a>
    <style>
    #gototopBtn {
        position: fixed;
        bottom: 40px;
        right: 40px;
        z-index: 9999;
        background-color: #00E570; /* SaaS Mint Green */
        color: #111827 !important; /* Deep Slate */
        text-decoration: none;
        padding: 12px 18px;
        border-radius: 50%; /* Perfect Circle */
        font-size: 22px;
        font-weight: bold;
        box-shadow: 0 4px 14px 0 rgba(0, 229, 112, 0.4);
        transition: all 0.3s ease;
        text-align: center;
    }
    #gototopBtn:hover {
        background-color: #1F2937; /* Dark Grey on Hover */
        color: #00E570 !important;
        border: 2px solid #00E570;
        transform: scale(1.1); /* Halka sa bada hoga hover pe */
    }
    </style>
"""
st.markdown(go_to_top_html, unsafe_allow_html=True)





















































