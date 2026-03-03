import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd

# --- 1. PAGE SETUP & MEMORY ---
st.set_page_config(page_title="Dixit Investment Group | Premium Terminal", layout="wide", initial_sidebar_state="collapsed")

if 'current_view' not in st.session_state: st.session_state.current_view = "HOME"
if 'portfolio' not in st.session_state: st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Price", "Quantity"])

# --- PREMIUM CSS INJECTION (Navy Blue & Gold + Serif Fonts) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,700&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    hr { border-color: #E0E0E0; }
    
    /* Big Home Banner */
    .hero-banner {
        background-color: #0B1C2E; /* Deep Navy Blue */
        padding: 40px 20px;
        border-radius: 8px;
        border-bottom: 4px solid #D4AF37; /* Royal Gold */
        text-align: center;
        margin-bottom: 20px;
    }
    .brand-title {
        font-family: 'Playfair Display', serif;
        color: #D4AF37;
        font-size: 3.5rem;
        margin-bottom: 0px;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .brand-tagline {
        color: #FFFFFF;
        font-size: 1.2rem;
        font-weight: 300;
        margin-top: 5px;
        letter-spacing: 2px;
    }
    
    /* Small Top-Left Logo for other pages */
    .small-logo {
        font-family: 'Playfair Display', serif;
        color: #0B1C2E;
        font-size: 28px;
        font-weight: 700;
        border-bottom: 2px solid #D4AF37;
        display: inline-block;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    .small-logo span { color: #D4AF37; }
    
    /* Premium Button Styling */
    div.stButton > button {
        background-color: #0B1C2E;
        color: #D4AF37;
        border: 1px solid #D4AF37;
        border-radius: 4px;
        font-weight: 600;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #D4AF37;
        color: #0B1C2E;
        border: 1px solid #0B1C2E;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. LEAD GENERATION (WHATSAPP) ---
@st.dialog("Unlock Institutional Access")
def premium_signup():
    st.markdown("Join **Dixit Investment Group** for algorithmic access & deeper fundamental models.")
    YOUR_WHATSAPP_NUMBER = "917052360459" 
    name = st.text_input("Full Name")
    city = st.text_input("City")
    if name and city:
        raw_message = f"Hello Dixit Investment Group! 📈\n\nI want to purchase the Premium Access Code.\nName: {name}\nCity: {city}"
        whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={urllib.parse.quote(raw_message)}"
        st.link_button("📲 Connect with Advisor", whatsapp_url, type="primary", use_container_width=True)
    else:
        st.button("📲 Connect with Advisor", type="primary", disabled=True, use_container_width=True)

# --- 3. TOP MARKET BAR ---
@st.cache_data(ttl=300)
def get_index_data(ticker):
    try: return yf.Ticker(ticker).history(period="2d")
    except: return None

nifty, sensex, banknifty = get_index_data("^NSEI"), get_index_data("^BSESN"), get_index_data("^NSEBANK")

m1, m2, m3, m4, m5, m6 = st.columns(6)
def display_index(col, name, data):
    if data is not None and len(data) >= 2:
        curr, prev = data['Close'].iloc[-1], data['Close'].iloc[-2]
        chg, pct = curr - prev, ((curr - prev)/prev)*100
        color = "#2E7D32" if chg >= 0 else "#C62828" # Muted professional green/red
        col.markdown(f"**{name}**: {curr:.2f} <span style='color:{color};'>({pct:.2f}%)</span>", unsafe_allow_html=True)

display_index(m2, "SENSEX", sensex)
display_index(m3, "NIFTY 50", nifty)
display_index(m4, "BANKNIFTY", banknifty)
st.write("---")

TOP_STOCKS = {"RELIANCE.NS": "Reliance", "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC Bank", "INFY.NS": "Infosys", "ZOMATO.NS": "Zomato", "ITC.NS": "ITC", "SBIN.NS": "SBI"}

# --- 4. SIDEBAR MENU ---
st.sidebar.markdown("<h2 style='font-family: Playfair Display; color: #D4AF37;'>DIG Menu</h2>", unsafe_allow_html=True)
if st.sidebar.button("🏠 Home Dashboard", use_container_width=True): st.session_state.current_view = "HOME"; st.rerun()
if st.sidebar.button("⚖️ Peer Comparison", use_container_width=True): st.session_state.current_view = "COMPARE"; st.rerun()
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("👑 Upgrade to Premium", use_container_width=True): premium_signup()

# Helpers
@st.cache_data(ttl=1800)
def get_live_news(company_name):
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(f'{company_name} share stock news India')}&hl=en-IN&gl=IN&ceid=IN:en"
        root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read())
        return [{'title': i.find('title').text.rsplit(' - ', 1)[0] if ' - ' in i.find('title').text else i.find('title').text, 'link': i.find('link').text, 'date': i.find('pubDate').text[5:16]} for i in root.findall('.//item')[:4]]
    except: return []

# --- 5. PEER COMPARISON VIEW ---
if st.session_state.current_view == "COMPARE":
    st.markdown("<div class='small-logo'>Dixit <span>Investment Group</span></div>", unsafe_allow_html=True)
    st.markdown("### ⚖️ Peer-to-Peer Asset Comparison")
    if st.button("⬅️ Back to Terminal Hub"): st.session_state.current_view = "HOME"; st.rerun()
    st.write("---")
    
    c1, c2 = st.columns(2)
    with c1: t1 = st.selectbox("Select Asset 1:", list(TOP_STOCKS.keys()), index=0)
    with c2: t2 = st.selectbox("Select Asset 2:", list(TOP_STOCKS.keys()), index=2)
    
    if st.button("Run Institutional Comparison 🚀", type="primary"):
        i1, i2 = yf.Ticker(t1).info, yf.Ticker(t2).info
        comp_data = {
            "Metric": ["Price", "P/E Ratio", "ROE (%)", "Debt to Equity", "Market Cap (Cr)"],
            TOP_STOCKS[t1]: [f"₹{i1.get('currentPrice', 'N/A')}", i1.get('trailingPE', 'N/A'), round(i1.get('returnOnEquity', 0)*100, 2) if i1.get('returnOnEquity') else 'N/A', i1.get('debtToEquity', 'N/A'), round(i1.get('marketCap', 0)/10000000, 2) if i1.get('marketCap') else 'N/A'],
            TOP_STOCKS[t2]: [f"₹{i2.get('currentPrice', 'N/A')}", i2.get('trailingPE', 'N/A'), round(i2.get('returnOnEquity', 0)*100, 2) if i2.get('returnOnEquity') else 'N/A', i2.get('debtToEquity', 'N/A'), round(i2.get('marketCap', 0)/10000000, 2) if i2.get('marketCap') else 'N/A']
        }
        st.table(pd.DataFrame(comp_data).set_index("Metric"))

# --- 6. HOME PAGE (Massive Branding, Search, Calc, Portfolio) ---
elif st.session_state.current_view == "HOME":
    
    # BIG HOME BANNER
    st.markdown("""
        <div class="hero-banner">
            <h1 class="brand-title">Dixit Investment Group</h1>
            <p class="brand-tagline">A Premium Wealth & Portfolio Management Company</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        man_t = st.text_input("🔍 Type a Company Name or NSE Symbol (e.g., ITC)", placeholder="Search asset to analyze...")
        if st.button("Run Fundamental Audit", type="primary", use_container_width=True):
            if man_t:
                st.session_state.current_view = man_t.upper() if man_t.upper().endswith(".NS") else f"{man_t.upper()}.NS"
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #0B1C2E; font-weight: bold;'>Institutional Watchlist:</p>", unsafe_allow_html=True)
        t1, t2, t3, t4, t5 = st.columns(5)
        if t1.button("RELIANCE", use_container_width=True): st.session_state.current_view = "RELIANCE.NS"; st.rerun()
        if t2.button("HDFCBANK", use_container_width=True): st.session_state.current_view = "HDFCBANK.NS"; st.rerun()
        if t3.button("ZOMATO", use_container_width=True): st.session_state.current_view = "ZOMATO.NS"; st.rerun()
        if t4.button("TCS", use_container_width=True): st.session_state.current_view = "TCS.NS"; st.rerun()
        if t5.button("ITC", use_container_width=True): st.session_state.current_view = "ITC.NS"; st.rerun()

    st.write("---")
    
    ht1, ht2 = st.tabs(["💰 Wealth Calculator", "💼 Managed Portfolio (Virtual)"])
    with ht1:
        calc_col1, calc_col2 = st.columns([1, 2])
        with calc_col1:
            sip_amount = st.number_input("Monthly SIP (₹)", min_value=500, value=5000, step=500)
            sip_years = st.slider("Investment Period (Years)", 1, 30, 10)
            sip_rate = st.slider("Expected Annual Return (%)", 5, 25, 12)
        with calc_col2:
            monthly_rate = sip_rate / 12 / 100
            months = sip_years * 12
            invested = sip_amount * months
            fv = sip_amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
            st.success(f"### Estimated Value: ₹{fv:,.0f}")
            w1, w2 = st.columns(2)
            w1.metric("Capital Deployed", f"₹{invested:,.0f}")
            w2.metric("Projected Gains", f"₹{fv - invested:,.0f}")

    with ht2:
        pc1, pc2, pc3, pc4 = st.columns(4)
        with pc1: p_tick = st.selectbox("Asset", list(TOP_STOCKS.keys()))
        with pc2: p_qty = st.number_input("Quantity", min_value=1, value=10)
        with pc3: p_buy = st.number_input("Buy Price (₹)", min_value=1.0, value=100.0)
        with pc4: 
            st.write("")
            if st.button("➕ Execute Trade", use_container_width=True):
                st.session_state.portfolio = pd.concat([st.session_state.portfolio, pd.DataFrame({"Ticker": [p_tick], "Buy Price": [p_buy], "Quantity": [p_qty]})], ignore_index=True)
                st.success("Trade Recorded!")
        if not st.session_state.portfolio.empty:
            df_port = st.session_state.portfolio.copy()
            df_port["Live Price"] = [yf.Ticker(t).history(period="1d")['Close'].iloc[-1] if not yf.Ticker(t).history(period="1d").empty else 0 for t in df_port["Ticker"]]
            df_port["Total Invested"] = df_port["Buy Price"] * df_port["Quantity"]
            df_port["Current Value"] = df_port["Live Price"] * df_port["Quantity"]
            df_port["P&L (₹)"] = df_port["Current Value"] - df_port["Total Invested"]
            st.dataframe(df_port, use_container_width=True)

# --- 7. STOCK ANALYSIS ENGINE (All 7 Super Tabs) ---
else:
    user_ticker = st.session_state.current_view
    
    # Small Top-Left Branding
    st.markdown("<div class='small-logo'>Dixit <span>Investment Group</span></div>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Terminal Hub"): st.session_state.current_view = "HOME"; st.rerun()
    st.write("---")
    
    t_obj = yf.Ticker(user_ticker)
    data = t_obj.history(period="1y")
    info = t_obj.info
    display_name = info.get('shortName', user_ticker.replace('.NS', ''))

    if data is not None and not data.empty:
        curr_price, prev_price = data['Close'].iloc[-1], data['Close'].iloc[-2]
        
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"<h1 style='color:#0B1C2E; font-family: Playfair Display;'>{display_name}</h1>", unsafe_allow_html=True)
        c2.metric("Last Traded Price", f"₹{curr_price:.2f}", f"{(curr_price - prev_price):.2f} ({((curr_price - prev_price)/prev_price)*100:.2f}%)")

        data['SMA50'] = data['Close'].rolling(50).mean()
        
        # ALL 7 TABS
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Price Chart", "📋 Ratios & Whales", "📑 Financials", "🏢 Corp Actions", "📰 Live News", "💎 AI Quant", "📥 Export"])

        with tab1:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            # Chart colors updated to match the Gold/Navy premium theme
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='#D4AF37', width=2), name='50 SMA (Gold)'))
            fig.update_layout(template="plotly_white", margin=dict(t=10, b=10, l=10, r=10), height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("<h3 style='color: #0B1C2E;'>Key Metrics</h3>", unsafe_allow_html=True)
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Market Cap (Cr)", f"₹{round(info.get('marketCap', 0)/10000000, 2)}" if info.get('marketCap') else "N/A")
            f2.metric("P/E Ratio", round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A")
            f3.metric("ROE", f"{round(info.get('returnOnEquity', 0)*100, 2)}%" if info.get('returnOnEquity') else "N/A")
            f4.metric("Debt/Equity", round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else "N/A")
            
            st.write("---")
            st.markdown("<h3 style='color: #0B1C2E;'>🐋 Shareholding Pattern</h3>", unsafe_allow_html=True)
            insider = round(info.get('heldPercentInsiders', 0) * 100, 2)
            inst = round(info.get('heldPercentInstitutions', 0) * 100, 2)
            st.write(f"**Promoters:** {insider}% | **Institutions (FII/DII):** {inst}% | **Public:** {100 - insider - inst}%")

        with tab3:
            st.markdown("<h3 style='color: #0B1C2E;'>📑 Annual Financial Statements</h3>", unsafe_allow_html=True)
            stmt1, stmt2 = st.tabs(["Income Statement", "Balance Sheet"])
            with stmt1:
                try:
                    fin_df = t_obj.financials
                    if not fin_df.empty: st.dataframe(fin_df.dropna(how='all'), use_container_width=True)
                    else: st.warning("Income Statement data not available.")
                except: st.warning("Error fetching Income Statement.")
            with stmt2:
                try:
                    bs_df = t_obj.balance_sheet
                    if not bs_df.empty: st.dataframe(bs_df.dropna(how='all'), use_container_width=True)
                    else: st.warning("Balance Sheet data not available.")
                except: st.warning("Error fetching Balance Sheet.")

        with tab4:
            st.markdown("<h3 style='color: #0B1C2E;'>📅 Recent Corporate Actions</h3>", unsafe_allow_html=True)
            try:
                divs = t_obj.dividends.tail(5)
                if not divs.empty: st.write(divs)
                else: st.info("No recent dividend data found.")
            except: st.warning("Corporate action data unavailable.")

        with tab5:
            st.markdown("<h3 style='color: #0B1C2E;'>📰 Live Market News</h3>", unsafe_allow_html=True)
            live_news = get_live_news(display_name)
            if live_news:
                for n in live_news:
                    st.markdown(f"🔹 **[{n['title']}]({n['link']})**")
                    st.caption(f"🕒 {n['date']}")
                    st.divider()
            else: st.info("No recent news found.")

        with tab6:
            entered_code = st.text_input("🔑 Enter Premium Access Code:", type="password")
            if entered_code == "AMANPRO":
                st.success("🔓 Algorithm Running...")
                pe = info.get('trailingPE', 0)
                if pe > 0 and pe < 20: st.success("✅ **Verdict: STRONG BUY** (Undervalued: Trading at discount).")
                elif pe >= 20 and pe < 40: st.info("⚖️ **Verdict: HOLD / SIP** (Fairly Valued: Normal pricing).")
                else: st.warning("⚠️ **Verdict: CAUTION** (Overpriced: High premium).")
            elif entered_code: st.error("❌ Invalid Code.")

        with tab7:
            st.markdown("<h3 style='color: #0B1C2E;'>📥 Download Institutional Report</h3>", unsafe_allow_html=True)
            report_df = pd.DataFrame({"Metric": ["Company", "Price", "P/E", "ROE", "Debt/Eq"], "Value": [display_name, curr_price, info.get('trailingPE'), info.get('returnOnEquity'), info.get('debtToEquity')]})
            st.download_button(label="Download CSV", data=report_df.to_csv(index=False).encode('utf-8'), file_name=f"{user_ticker}_DIG_Report.csv", mime="text/csv", type="primary")

    else: st.error("⚠️ Invalid Asset Symbol. Try searching something like 'TCS'.")
