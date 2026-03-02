import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import urllib.parse

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Pro Terminal | Dixit Capital", layout="wide", initial_sidebar_state="expanded")

# --- 2. LEAD GENERATION (SMART WHATSAPP BUTTON) ---
@st.dialog("👑 Unlock Premium Access")
def premium_signup():
    st.markdown("Join **Dixit Capital Premium** for advanced audits, live alerts, and portfolio management.")
    
    # YAHAN APNA ASLI WHATSAPP NUMBER DAALIYE (Country code 91 ke sath)
    YOUR_WHATSAPP_NUMBER = "919876543210" 
    
    name = st.text_input("Full Name")
    city = st.text_input("City")
    
    st.write("---")
    
    # Smart Logic: Button sirf tabhi chalega jab dono details bhari hon
    if name and city:
        raw_message = f"Hello Dixit Capital! 📈\n\nI want to join the Premium Membership.\nName: {name}\nCity: {city}\n\nPlease share the details."
        encoded_message = urllib.parse.quote(raw_message)
        whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={encoded_message}"
        
        # Streamlit ka official safe link button
        st.link_button("📲 Continue to WhatsApp", whatsapp_url, type="primary", use_container_width=True)
    else:
        # Jab tak naam nahi daala, button disabled rahega
        st.button("📲 Continue to WhatsApp", type="primary", disabled=True, use_container_width=True)
        st.caption("⚠️ Please enter your Name and City to unlock the button.")

# --- 3. BRANDING ---
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🏢 Dixit Capital & Wealth Management</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Advanced Quantitative Analysis & Portfolio Tracking</p><hr>", unsafe_allow_html=True)

# --- 4. TOP STOCKS LIST ---
TOP_STOCKS = {
    "HOME": "🏠 Home (Dashboard & Tools)",
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "INFY.NS": "Infosys",
    "ZOMATO.NS": "Zomato",
    "TATAMOTORS.NS": "Tata Motors",
    "ITC.NS": "ITC Limited",
    "SBIN.NS": "State Bank of India"
}

# --- 5. SIDEBAR & SEARCH ---
st.sidebar.header("⚙️ Main Menu")

if st.sidebar.button("👑 Upgrade to Premium", use_container_width=True):
    premium_signup()

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Equity Search")

selected_ticker = st.sidebar.selectbox(
    "Search or Select Stock:",
    options=list(TOP_STOCKS.keys()),
    format_func=lambda x: TOP_STOCKS[x] if x == "HOME" else f"{TOP_STOCKS[x]} ({x.replace('.NS', '')})"
)

manual_ticker = st.sidebar.text_input("Or type NSE symbol (e.g., ITC):", "")

if manual_ticker:
    raw_ticker = manual_ticker.upper()
    user_ticker = raw_ticker if raw_ticker.endswith(".NS") else f"{raw_ticker}.NS"
else:
    user_ticker = selected_ticker

# Helper function for fast indexing
@st.cache_data(ttl=300)
def get_index_data(ticker):
    try: return yf.Ticker(ticker).history(period="2d")
    except: return None

# --- 6. HOME DASHBOARD ---
if user_ticker == "HOME":
    st.markdown("<h3 style='text-align: center;'>Welcome to the Pro Terminal</h3>", unsafe_allow_html=True)
    
    # Market Pulse
    nifty = get_index_data("^NSEI")
    banknifty = get_index_data("^NSEBANK")
    
    st.markdown("#### 📡 Live Market Pulse")
    col1, col2, col3 = st.columns(3)
    
    if nifty is not None and len(nifty) >= 2:
        n_curr, n_prev = nifty['Close'].iloc[-1], nifty['Close'].iloc[-2]
        col1.metric("NIFTY 50", f"{n_curr:.2f}", f"{n_curr - n_prev:.2f} ({(n_curr - n_prev)/n_prev * 100:.2f}%)")
    
    if banknifty is not None and len(banknifty) >= 2:
        bn_curr, bn_prev = banknifty['Close'].iloc[-1], banknifty['Close'].iloc[-2]
        col2.metric("NIFTY BANK", f"{bn_curr:.2f}", f"{bn_curr - bn_prev:.2f} ({(bn_curr - bn_prev)/bn_prev * 100:.2f}%)")
        
    col3.info("👈 Select a stock from the sidebar to view technicals and fundamentals.")
    st.divider()

    # Wealth Calculator
    st.markdown("#### 💰 SIP Wealth Calculator")
    st.caption("Plan your financial independence with our institutional-grade calculator.")
    
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
        wealth_gained = future_value - invested_amount
        
        st.success(f"### Estimated Wealth: ₹{future_value:,.0f}")
        w_col1, w_col2 = st.columns(2)
        w_col1.metric("Total Invested", f"₹{invested_amount:,.0f}")
        w_col2.metric("Est. Wealth Gained", f"₹{wealth_gained:,.0f}")
        st.progress(min(invested_amount / future_value, 1.0), text="Investment vs Growth Ratio")

# --- 7. STOCK ANALYSIS ENGINE ---
else:
    @st.cache_data(ttl=300)
    def get_data(symbol):
        try: return yf.Ticker(symbol).history(period="1y")
        except: return None

    @st.cache_data(ttl=3600)
    def get_info(symbol):
        try: return yf.Ticker(symbol).info
        except: return {}

    data = get_data(user_ticker)
    info = get_info(user_ticker)

    if data is not None and not data.empty:
        curr_price, prev_price = data['Close'].iloc[-1], data['Close'].iloc[-2]
        change = curr_price - prev_price
        pct = (change / prev_price) * 100

        display_name = TOP_STOCKS.get(user_ticker, user_ticker.replace('.NS', ''))
        st.markdown(f"## {display_name}")
        st.metric("Last Traded Price", f"₹{curr_price:.2f}", f"{change:.2f} ({pct:.2f}%)")

        # Interactive Chart
        data['SMA50'] = data['Close'].rolling(50).mean()
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Price'))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='orange', width=1.5), name='50-Day SMA'))
        fig.update_layout(template="plotly_dark", margin=dict(t=10, b=10, l=10, r=10), height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # Expanders for clean UI
        with st.expander("📋 View Core Fundamentals & Valuation"):
            if info:
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("P/E Ratio", round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A")
                f2.metric("ROE", f"{round(info.get('returnOnEquity', 0)*100, 2)}%" if info.get('returnOnEquity') else "N/A")
                f3.metric("Book Value", f"₹{round(info.get('bookValue', 0), 2)}" if info.get('bookValue') else "N/A")
                f4.metric("Debt/Eq", round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else "N/A")
                st.caption(f"**Business Overview:** *{info.get('longBusinessSummary', 'N/A')[:300]}...*")
            else:
                st.warning("Fundamental data currently unavailable.")

        with st.expander("📰 View Latest Market News"):
            try:
                news = yf.Ticker(user_ticker).news
                if news:
                    for n in news[:3]:
                        st.write(f"🔹 [{n.get('title')}]({n.get('link')})")
                else:
                    st.write("No recent news found.")
            except:
                st.write("Could not load news at this time.")
    else:
        st.error("⚠️ Invalid Stock Symbol. Please check the spelling or enter a valid NSE ticker.")
