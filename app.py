import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd

# --- 1. PAGE SETUP & MEMORY ---
st.set_page_config(page_title="Dixit Investment Group | Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

if 'current_view' not in st.session_state: st.session_state.current_view = "HOME"
if 'portfolio' not in st.session_state: st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Price", "Quantity"])

# --- PREMIUM CSS (Finology & Institutional Look) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1300px; }
    
    /* Center aligning main content */
    .main-title { text-align: center; color: #1E88E5; font-size: 3.5rem; font-weight: 800; margin-bottom: 0px; font-family: sans-serif;}
    .sub-tagline { text-align: center; color: #555; font-size: 1.2rem; font-weight: 600; margin-top: 5px; margin-bottom: 30px; }

    /* FIX: Prevent Button Text Wrapping (Stops RELIANC E) */
    div[data-testid="stButton"] button {
        white-space: nowrap !important;
        border-radius: 8px !important;
        padding: 5px 15px !important;
    }
    
    a { text-decoration: none !important; color: inherit !important; }
    th { text-align: left !important; background-color: rgba(150, 150, 150, 0.1); }
    </style>
""", unsafe_allow_html=True)

# --- INDIAN NUMBER FORMATTING HELPERS ---
def format_inr(number):
    if pd.isna(number) or number is None: return "N/A"
    try:
        is_negative = number < 0
        number = abs(number)
        s, *d = str(round(float(number), 2)).partition(".")
        r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        formatted = "".join([r] + d) if r else s
        return f"-{formatted}" if is_negative else formatted
    except: return str(number)

def to_cr(number):
    if pd.isna(number) or number is None: return "N/A"
    return format_inr(round(float(number) / 10000000, 2))

# --- 2. LIVE INDEX TOP BAR (Stable Pulse) ---
@st.cache_data(ttl=300)
def get_market_indices():
    indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "BANKNIFTY": "^NSEBANK"}
    res = {}
    for name, tick in indices.items():
        try:
            d = yf.Ticker(tick).history(period="2d")
            curr, prev = d['Close'].iloc[-1], d['Close'].iloc[-2]
            res[name] = {"val": curr, "pct": ((curr-prev)/prev)*100}
        except: pass
    return res

pulse = get_market_indices()
if pulse:
    pcols = st.columns(len(pulse) + 2)
    for i, (name, val) in enumerate(pulse.items()):
        color = "#16A34A" if val['pct'] >= 0 else "#DC2626"
        pcols[i+1].markdown(f"**{name}**<br>₹{format_inr(val['val'])} <span style='color:{color}; font-weight:bold;'>({val['pct']:.2f}%)</span>", unsafe_allow_html=True)
st.divider()

# --- 3. TOOLS & SIDEBAR ---
TOP_STOCKS = {"RELIANCE.NS": "Reliance", "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC Bank", "INFY.NS": "Infosys", "ZOMATO.NS": "Zomato", "ITC.NS": "ITC"}

st.sidebar.markdown("<h2 style='color:#1E88E5;'>DIG Engine</h2>", unsafe_allow_html=True)
if st.sidebar.button("🏠 Home Dashboard", use_container_width=True): st.session_state.current_view = "HOME"; st.rerun()
if st.sidebar.button("⚖️ Peer Comparison", use_container_width=True): st.session_state.current_view = "COMPARE"; st.rerun()

# --- 4. HOME PAGE (Branding & Search) ---
if st.session_state.current_view == "HOME":
    st.markdown('<h1 class="main-title">Dixit Investment Group</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-tagline">(A Premium Wealth and Portfolio Management Company)</p>', unsafe_allow_html=True)
    
    sc1, sc2, sc3 = st.columns([1, 2, 1])
    with sc2:
        search = st.text_input("Search Asset", placeholder="Search Symbol (e.g. HDFCBANK)...", label_visibility="collapsed")
        if (st.button("Run Research", type="primary", use_container_width=True) or search) and search:
            st.session_state.current_view = search.upper() if search.upper().endswith(".NS") else f"{search.upper()}.NS"
            st.rerun()
        
        st.markdown("<p style='text-align:center;'><b>Quick Pulse Watchlist:</b></p>", unsafe_allow_html=True)
        t_cols = st.columns(len(TOP_STOCKS))
        for i, (tick, name) in enumerate(TOP_STOCKS.items()):
            if t_cols[i].button(name): st.session_state.current_view = tick; st.rerun()

    st.divider()
    t1, t2 = st.tabs(["💰 SIP Wealth Calculator", "💼 Managed Portfolio"])
    with t1:
        c1, c2 = st.columns([1, 2])
        sip = c1.number_input("Monthly SIP (₹)", 500, 1000000, 5000, 500)
        yrs = c1.slider("Tenure (Years)", 1, 30, 10)
        rate = c1.slider("Expected Return (%)", 5, 25, 12)
        m_r, m_d = rate/12/100, yrs*12
        fv = sip * (((1 + m_r)**m_d - 1) / m_r) * (1 + m_r)
        c2.success(f"### Projected Wealth: ₹{format_inr(round(fv, 0))}")
        c2.metric("Total Investment", f"₹{format_inr(sip*m_d)}")
        c2.metric("Wealth Gain", f"₹{format_inr(round(fv - (sip*m_d), 0))}")

# --- 5. STOCK ANALYSIS (STRONG RATIOS & FINANCIALS) ---
elif st.session_state.current_view == "COMPARE":
    st.header("⚖️ Peer Comparison Engine")
    if st.button("⬅️ Back"): st.session_state.current_view = "HOME"; st.rerun()
else:
    ticker = st.session_state.current_view
    if st.button("⬅️ Back to Terminal"): st.session_state.current_view = "HOME"; st.rerun()
    
    s_obj = yf.Ticker(ticker)
    info = s_obj.info
    hist = s_obj.history(period="1y")
    
    if not hist.empty:
        st.markdown(f"<h3 style='color:#1E88E5; margin-bottom:0px;'>Dixit Investment Group Research</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"# {info.get('shortName', ticker)}")
        price = hist['Close'].iloc[-1]
        c2.metric("LTP", f"₹{format_inr(price)}", f"{price - hist['Close'].iloc[-2]:.2f}")

        tabs = st.tabs(["📊 Charts", "📋 Strong Ratios", "📑 Financial Statements (Cr)", "📰 News Feed", "💎 AI Verdict"])
        
        with tabs[1]:
            st.markdown("### 📈 Deep Fundamental Ratios")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Market Cap", f"₹{to_cr(info.get('marketCap'))} Cr")
            col2.metric("Stock P/E", f"{round(info.get('trailingPE', 0), 2)}")
            col3.metric("ROE (%)", f"{round(info.get('returnOnEquity', 0)*100, 2)}%")
            col4.metric("Debt/Equity", f"{round(info.get('debtToEquity', 0), 2)}")
            
            st.write("")
            v1, v2, v3, v4 = st.columns(4)
            v1.metric("P/B Ratio", f"{round(info.get('priceToBook', 0), 2)}")
            v2.metric("Current Ratio", f"{round(info.get('currentRatio', 0), 2)}")
            v3.metric("Div. Yield (%)", f"{round(info.get('dividendYield', 0)*100, 2)}%")
            v4.metric("PEG Ratio", f"{round(info.get('pegRatio', 0), 2)}")

        with tabs[2]:
            st.markdown("### 📑 Annual Financials (In Crores)")
            pnl = s_obj.financials
            if not pnl.empty:
                st.dataframe(pnl.applymap(lambda x: to_cr(x)), use_container_width=True)

        with tabs[4]:
            st.markdown("### 💎 Institutional AI Verdict")
            pe = info.get('trailingPE', 100)
            roe = info.get('returnOnEquity', 0) * 100
            if pe < 25 and roe > 15:
                st.success("🎯 **STRONG BUY:** Undervalued with High Profitability.")
            elif pe > 40:
                st.warning("⚖️ **WATCH:** Overvalued. Wait for correction.")
            else:
                st.info("📊 **NEUTRAL:** Trading at fair market value.")

        with tabs[0]:
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
            fig.update_layout(template="plotly_white", xaxis_rangeslider_visible=False, height=550)
            st.plotly_chart(fig, use_container_width=True)
