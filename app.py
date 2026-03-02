import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

# --- 1. PAGE SETUP & MEMORY ---
st.set_page_config(page_title="Pro Terminal | Dixit Capital", layout="wide", initial_sidebar_state="expanded")

if 'current_view' not in st.session_state: st.session_state.current_view = "HOME"
if 'portfolio' not in st.session_state: st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Price", "Quantity"])

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    hr { margin-top: 1rem; margin-bottom: 1.5rem; border-color: #333; }
    a { text-decoration: none !important; color: inherit !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LEAD GENERATION (WHATSAPP) ---
@st.dialog("👑 Unlock Premium Access")
def premium_signup():
    st.markdown("Join **Dixit Capital Premium** for full algorithmic access.")
    YOUR_WHATSAPP_NUMBER = "917052360459" 
    name = st.text_input("Full Name")
    city = st.text_input("City")
    if name and city:
        raw_message = f"Hello Dixit Capital! 📈\n\nI want to purchase the Premium Access Code.\nName: {name}\nCity: {city}"
        whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={urllib.parse.quote(raw_message)}"
        st.link_button("📲 Chat to get Code", whatsapp_url, type="primary", use_container_width=True)
    else:
        st.button("📲 Chat to get Code", type="primary", disabled=True, use_container_width=True)

# --- 3. CLICKABLE BRANDING ---
st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <a href="/" target="_self">
            <h1 style='color: #1E88E5; font-family: "Arial Black", sans-serif; cursor: pointer;'>🏢 Dixit Capital & Wealth Management</h1>
        </a>
        <p style='font-style: italic; color: #888888; font-size: 18px;'>Advanced Quantitative Analysis & Portfolio Tracking</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

TOP_STOCKS = {
    "RELIANCE.NS": "Reliance Industries", "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank", "ICICIBANK.NS": "ICICI Bank",
    "INFY.NS": "Infosys", "ZOMATO.NS": "Zomato",
    "TATAMOTORS.NS": "Tata Motors", "ITC.NS": "ITC Limited"
}

# --- 4. SIDEBAR MENU ---
st.sidebar.header("⚙️ Main Menu")
if st.sidebar.button("🏠 Home Dashboard", use_container_width=True):
    st.session_state.current_view = "HOME"
    st.rerun()

if st.sidebar.button("⚖️ Peer Comparison", use_container_width=True):
    st.session_state.current_view = "COMPARE"
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("👑 Upgrade to Premium", use_container_width=True): premium_signup()

# Helpers
@st.cache_data(ttl=300)
def get_index_data(ticker):
    try: return yf.Ticker(ticker).history(period="2d")
    except: return None

@st.cache_data(ttl=1800)
def get_live_news(company_name):
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(f'{company_name} share stock news India')}&hl=en-IN&gl=IN&ceid=IN:en"
        root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read())
        return [{'title': i.find('title').text.rsplit(' - ', 1)[0] if ' - ' in i.find('title').text else i.find('title').text, 'link': i.find('link').text, 'date': i.find('pubDate').text[5:16]} for i in root.findall('.//item')[:4]]
    except: return []

# --- 5. PEER COMPARISON VIEW ---
if st.session_state.current_view == "COMPARE":
    st.markdown("<h3 style='text-align: center;'>⚖️ Peer-to-Peer Asset Comparison</h3>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"): st.session_state.current_view = "HOME"; st.rerun()
    
    c1, c2 = st.columns(2)
    with c1: t1 = st.selectbox("Select Asset 1:", list(TOP_STOCKS.keys()), index=0)
    with c2: t2 = st.selectbox("Select Asset 2:", list(TOP_STOCKS.keys()), index=2)
    
    if st.button("Run Comparison 🚀", type="primary"):
        i1, i2 = yf.Ticker(t1).info, yf.Ticker(t2).info
        st.markdown("### 📊 Fundamental Face-off")
        
        comp_data = {
            "Metric": ["Current Price", "P/E Ratio", "ROE (%)", "Debt to Equity", "Market Cap (Cr)"],
            TOP_STOCKS[t1]: [f"₹{i1.get('currentPrice', 'N/A')}", i1.get('trailingPE', 'N/A'), round(i1.get('returnOnEquity', 0)*100, 2), i1.get('debtToEquity', 'N/A'), round(i1.get('marketCap', 0)/10000000, 2)],
            TOP_STOCKS[t2]: [f"₹{i2.get('currentPrice', 'N/A')}", i2.get('trailingPE', 'N/A'), round(i2.get('returnOnEquity', 0)*100, 2), i2.get('debtToEquity', 'N/A'), round(i2.get('marketCap', 0)/10000000, 2)]
        }
        st.table(pd.DataFrame(comp_data).set_index("Metric"))

# --- 6. HOME PAGE (Search, Pulse, Calculator, Portfolio) ---
elif st.session_state.current_view == "HOME":
    ht1, ht2 = st.tabs(["🔍 Terminal Hub", "💼 My Virtual Portfolio"])
    
    with ht1:
        st.markdown("<h3 style='text-align: center;'>Search Asset for Analysis</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            sel_t = st.selectbox("Select from Top Companies:", ["-- Select --"] + list(TOP_STOCKS.keys()), format_func=lambda x: TOP_STOCKS.get(x, x))
            man_t = st.text_input("Or enter NSE symbol manually (e.g., ITC):")
            if st.button("📊 Run Technical Audit", type="primary", use_container_width=True):
                target = man_t.upper() if man_t else sel_t
                if target and target != "-- Select --":
                    st.session_state.current_view = target if target.endswith(".NS") else f"{target}.NS"
                    st.rerun()
        st.write("---")
        
        st.markdown("<h4 style='text-align: center;'>📡 Live Market Pulse</h4>", unsafe_allow_html=True)
        nifty, banknifty = get_index_data("^NSEI"), get_index_data("^NSEBANK")
        m1, m2, m3, m4 = st.columns([1, 2, 2, 1])
        if nifty is not None and len(nifty) >= 2: m2.metric("NIFTY 50", f"{nifty['Close'].iloc[-1]:.2f}", f"{nifty['Close'].iloc[-1] - nifty['Close'].iloc[-2]:.2f}")
        if banknifty is not None and len(banknifty) >= 2: m3.metric("NIFTY BANK", f"{banknifty['Close'].iloc[-1]:.2f}", f"{banknifty['Close'].iloc[-1] - banknifty['Close'].iloc[-2]:.2f}")
        
        st.write("---")
        
        # --- RETURN OF THE SIP CALCULATOR ---
        st.markdown("<h4 style='text-align: center;'>💰 SIP Wealth Calculator</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Plan your financial independence.</p>", unsafe_allow_html=True)
        
        calc_col1, calc_col2 = st.columns([1, 2])
        with calc_col1:
            sip_amount = st.number_input("Monthly SIP (₹)", min_value=500, value=5000, step=500)
            sip_years = st.slider("Investment Period (Years)", 1, 30, 10)
            sip_rate = st.slider("Expected Annual Return (%)", 5, 25, 12)
        with calc_col2:
            monthly_rate = sip_rate / 12 / 100
            months = sip_years * 12
            invested_amount = sip_amount * months
            future_value = sip_amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
            st.success(f"### Estimated Wealth: ₹{future_value:,.0f}")
            w_col1, w_col2 = st.columns(2)
            w_col1.metric("Total Invested", f"₹{invested_amount:,.0f}")
            w_col2.metric("Est. Wealth Gained", f"₹{future_value - invested_amount:,.0f}")
            st.progress(min(invested_amount / future_value, 1.0), text="Investment vs Growth Ratio")
        
    with ht2:
        st.markdown("### 💼 Paper Trading Portfolio")
        st.caption("Practice trading strategies without real money. (Note: Data resets on page refresh)")
        
        pc1, pc2, pc3, pc4 = st.columns(4)
        with pc1: p_tick = st.selectbox("Asset", list(TOP_STOCKS.keys()))
        with pc2: p_qty = st.number_input("Quantity", min_value=1, value=10)
        with pc3: p_buy = st.number_input("Buy Price (₹)", min_value=1.0, value=100.0)
        with pc4: 
            st.write("")
            if st.button("➕ Add Trade", use_container_width=True):
                new_trade = pd.DataFrame({"Ticker": [p_tick], "Buy Price": [p_buy], "Quantity": [p_qty]})
                st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_trade], ignore_index=True)
                st.success("Added!")
                
        if not st.session_state.portfolio.empty:
            df_port = st.session_state.portfolio.copy()
            live_prices, pnl_list = [], []
            for t in df_port["Ticker"]:
                try: live_prices.append(yf.Ticker(t).history(period="1d")['Close'].iloc[-1])
                except: live_prices.append(0)
            
            df_port["Live Price"] = live_prices
            df_port["Total Invested"] = df_port["Buy Price"] * df_port["Quantity"]
            df_port["Current Value"] = df_port["Live Price"] * df_port["Quantity"]
            df_port["P&L (₹)"] = df_port["Current Value"] - df_port["Total Invested"]
            
            st.dataframe(df_port, use_container_width=True)
            st.metric("Total Net P&L", f"₹{df_port['P&L (₹)'].sum():.2f}")

# --- 7. STOCK ANALYSIS ENGINE (The Super Dashboard) ---
else:
    user_ticker = st.session_state.current_view
    if st.button("⬅️ Back to Home Search"): st.session_state.current_view = "HOME"; st.rerun()
    
    data = yf.Ticker(user_ticker).history(period="1y")
    t_obj = yf.Ticker(user_ticker)
    info = t_obj.info
    display_name = TOP_STOCKS.get(user_ticker, user_ticker.replace('.NS', ''))

    if data is not None and not data.empty:
        curr_price, prev_price = data['Close'].iloc[-1], data['Close'].iloc[-2]
        st.markdown(f"## {display_name}")
        st.metric("Last Traded Price", f"₹{curr_price:.2f}", f"{(curr_price - prev_price):.2f} ({((curr_price - prev_price)/prev_price)*100:.2f}%)")

        data['SMA50'] = data['Close'].rolling(50).mean()
        
        # Super Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Chart", "📋 Fundamentals & Whales", "🏢 CA Special (Corp Actions)", "💎 AI Quant", "📥 Export"])

        with tab1:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], increasing_line_color='#26A69A', decreasing_line_color='#EF5350')])
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='orange'), name='50 SMA'))
            fig.update_layout(template="plotly_dark", margin=dict(t=10, b=10, l=10, r=10), height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            f1, f2, f3 = st.columns(3)
            f1.metric("P/E Ratio", round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A")
            f2.metric("ROE", f"{round(info.get('returnOnEquity', 0)*100, 2)}%" if info.get('returnOnEquity') else "N/A")
            f3.metric("Debt/Equity", round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else "N/A")
            
            st.markdown("### 🐋 Whale Tracker (Shareholding)")
            insider = round(info.get('heldPercentInsiders', 0) * 100, 2)
            inst = round(info.get('heldPercentInstitutions', 0) * 100, 2)
            st.write(f"**Promoter Holding:** {insider}%")
            st.write(f"**Institutional Holding (FII/DII):** {inst}%")
            st.caption("High institutional holding usually indicates smart money trust.")

        with tab3:
            st.markdown("### 📅 Recent Dividends & Corporate Actions")
            try:
                divs = t_obj.dividends.tail(5)
                if not divs.empty: st.write(divs)
                else: st.info("No recent dividend data found.")
            except: st.warning("Corporate action data unavailable.")

        with tab4:
            entered_code = st.text_input("🔑 Enter Premium Access Code:", type="password")
            if entered_code == "AMANPRO":
                st.success("🔓 Algorithm Running...")
                pe = info.get('trailingPE', 0)
                if pe > 0 and pe < 20: st.success("✅ **Undervalued:** Trading at discount.")
                elif pe >= 20 and pe < 40: st.info("⚖️ **Fairly Valued:** Normal pricing.")
                else: st.warning("⚠️ **Overpriced:** High premium.")
            elif entered_code: st.error("❌ Invalid Code.")

        with tab5:
            st.markdown("### 📥 Download Institutional Report")
            st.write("Generate a CSV report containing core fundamentals to share with clients.")
            report_df = pd.DataFrame({"Metric": ["Company", "Price", "P/E", "ROE", "Debt/Eq"], "Value": [display_name, curr_price, info.get('trailingPE'), info.get('returnOnEquity'), info.get('debtToEquity')]})
            csv = report_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Report as CSV", data=csv, file_name=f"{user_ticker}_DixitCapital_Report.csv", mime="text/csv", type="primary")

    else: st.error("⚠️ Invalid Asset.")
