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

# --- ADVANCED CSS (Clean & Professional) ---
st.markdown("""
    <style>
    .block-container { padding-top: 0rem; padding-bottom: 2rem; max-width: 1300px; }
    
    /* Live Index Bar Styling */
    .index-bar {
        background-color: #f8f9fa;
        padding: 10px;
        border-bottom: 1px solid #dee2e6;
        margin-bottom: 20px;
        display: flex;
        justify-content: center;
        gap: 30px;
    }

    /* Fixed Button Wrapping */
    div[data-testid="stButton"] button {
        white-space: nowrap !important;
        border-radius: 8px !important;
    }

    /* Header Styling */
    .main-title { text-align: center; color: #1E88E5; font-size: 3.5rem; font-weight: 800; margin-bottom: 0px; }
    .sub-tagline { text-align: center; color: #6c757d; font-size: 1.1rem; font-weight: 500; margin-bottom: 30px; }
    
    th { text-align: left !important; background-color: rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- INDIAN NUMBER FORMATTING HELPERS ---
def format_inr(number):
    if pd.isna(number) or number is None: return "N/A"
    try:
        s, *d = str(round(float(number), 2)).partition(".")
        r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        return "".join([r] + d) if r else s
    except: return str(number)

def get_cap_category(mcap):
    if mcap >= 200000000000: return "Large Cap" # > 20,000 Cr
    if mcap >= 50000000000: return "Mid Cap"   # > 5,000 Cr
    return "Small Cap"

# --- 2. LIVE INDEX BAR (Fixing the visibility) ---
@st.cache_data(ttl=120)
def get_market_indices():
    indices = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "BANKNIFTY": "^NSEBANK"}
    results = {}
    for name, ticker in indices.items():
        try:
            data = yf.Ticker(ticker).history(period="2d")
            if not data.empty:
                curr = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2]
                results[name] = {"price": curr, "change": curr - prev, "pct": ((curr - prev)/prev)*100}
        except: pass
    return results

idx_data = get_market_indices()
if idx_data:
    cols = st.columns(len(idx_data) + 2)
    for i, (name, val) in enumerate(idx_data.items()):
        color = "green" if val['change'] >= 0 else "red"
        cols[i+1].markdown(f"**{name}**<br><span style='font-size:1.1rem;'>{format_inr(val['price'])}</span> <span style='color:{color};'>({val['pct']:.2f}%)</span>", unsafe_allow_html=True)
st.divider()

# --- 3. SIDEBAR & TOOLS ---
TOP_STOCKS = {"RELIANCE.NS": "Reliance", "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC Bank", "INFY.NS": "Infosys", "ZOMATO.NS": "Zomato", "ITC.NS": "ITC", "SBIN.NS": "SBI"}

st.sidebar.markdown("<h3 style='color:#1E88E5;'>DIG Terminal</h3>", unsafe_allow_html=True)
if st.sidebar.button("🏠 Home Dashboard", use_container_width=True): st.session_state.current_view = "HOME"; st.rerun()
if st.sidebar.button("⚖️ Peer Comparison", use_container_width=True): st.session_state.current_view = "COMPARE"; st.rerun()

# --- 4. HOME PAGE ---
if st.session_state.current_view == "HOME":
    st.markdown('<h1 class="main-title">Dixit Investment Group</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-tagline">(A Premium Wealth and Portfolio Management Company)</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        search_q = st.text_input("Search Assets", placeholder="🔍 Enter Stock Symbol (e.g. RELIANCE)...", label_visibility="collapsed")
        if st.button("Analyze Now", type="primary", use_container_width=True):
            if search_q:
                st.session_state.current_view = search_q.upper() if search_q.upper().endswith(".NS") else f"{search_q.upper()}.NS"
                st.rerun()
        
        st.markdown("<br><p style='text-align:center;'><b>Quick Watchlist:</b></p>", unsafe_allow_html=True)
        t_cols = st.columns(len(TOP_STOCKS))
        for i, (tick, name) in enumerate(TOP_STOCKS.items()):
            if t_cols[i].button(name): st.session_state.current_view = tick; st.rerun()

    st.divider()
    
    t1, t2 = st.tabs(["💰 Wealth Planning", "💼 Virtual Portfolio"])
    with t1:
        calc_c1, calc_c2 = st.columns([1, 2])
        sip = calc_c1.number_input("Monthly SIP (₹)", 500, 1000000, 5000, 500)
        dur = calc_c1.slider("Years", 1, 30, 10)
        ret = calc_c1.slider("Returns (%)", 5, 25, 12)
        
        m_rate = ret/12/100
        m_dur = dur*12
        fv = sip * (((1 + m_rate)**m_dur - 1) / m_rate) * (1 + m_rate)
        calc_c2.success(f"### Target Wealth: ₹{format_inr(round(fv, 0))}")
        calc_c2.metric("Total Invested", f"₹{format_inr(sip*m_dur)}")
        calc_c2.metric("Wealth Gained", f"₹{format_inr(round(fv - (sip*m_dur), 0))}")

    with t2:
        st.markdown("### Portfolio Manager")
        pc1, pc2, pc3, pc4 = st.columns(4)
        p_t = pc1.selectbox("Asset", list(TOP_STOCKS.keys()))
        p_q = pc2.number_input("Qty", 1, 10000, 10)
        p_b = pc3.number_input("Price", 1.0, 100000.0, 100.0)
        if pc4.button("➕ Add", use_container_width=True):
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, pd.DataFrame({"Ticker": [p_t], "Buy Price": [p_b], "Quantity": [p_q]})], ignore_index=True)
            st.rerun()
        st.table(st.session_state.portfolio)

# --- 5. STOCK ANALYSIS (Extended) ---
elif st.session_state.current_view == "COMPARE":
    st.header("⚖️ Peer Comparison")
    if st.button("Back"): st.session_state.current_view = "HOME"; st.rerun()
else:
    ticker = st.session_state.current_view
    if st.button("⬅️ Back to Home"): st.session_state.current_view = "HOME"; st.rerun()
    
    s_obj = yf.Ticker(ticker)
    info = s_obj.info
    hist = s_obj.history(period="1y")
    
    if not hist.empty:
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"# {info.get('shortName', ticker)}")
        c1.markdown(f"**Sector:** {info.get('sector', 'N/A')} | **Category:** {get_cap_category(info.get('marketCap', 0))}")
        
        price = hist['Close'].iloc[-1]
        change = price - hist['Close'].iloc[-2]
        c2.metric("Current Price", f"₹{format_inr(price)}", f"{change:.2f} ({((change)/hist['Close'].iloc[-2])*100:.2f}%)")

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Technicals", "📑 Financial Audit", "📰 News", "💎 AI Quant"])
        
        with tab1:
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
            fig.update_layout(template="plotly_white", xaxis_rangeslider_visible=False, height=500)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.markdown("### Key Audit Metrics")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("P/E Ratio", round(info.get('trailingPE', 0), 2))
            m2.metric("Debt/Equity", round(info.get('debtToEquity', 0), 2))
            m3.metric("ROE (%)", f"{round(info.get('returnOnEquity', 0)*100, 2)}%")
            m4.metric("Market Cap (Cr)", f"{format_inr(round(info.get('marketCap', 0)/10000000, 2))} Cr")
            
            st.divider()
            st.markdown("#### Annual P&L (In Crores)")
            st.dataframe(s_obj.financials / 10000000)

        with tab3:
            news = s_obj.news
            for n in news[:4]:
                st.markdown(f"🔹 **[{n['title']}]({n['link']})**")
                st.caption(f"Source: {n['publisher']}")

        with tab4:
            st.info("Algorithmic Analysis Running...")
            # Simple AI logic
            pe = info.get('trailingPE', 100)
            if pe < 20: st.success("Verdict: UNDERVALUED (Strong Buy Opportunity)")
            else: st.warning("Verdict: OVERVALUED (Wait for correction)")
