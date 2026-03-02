import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Pro Terminal | Dixit Capital", layout="wide", initial_sidebar_state="expanded")

# --- 2. POPUP FORM ---
@st.dialog("👑 Unlock Premium Access")
def premium_signup():
    st.markdown("Join **Dixit Capital Premium** for advanced CA-level audits, real-time alerts, and personalized portfolio management.")
    with st.form("premium_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("WhatsApp Number")
        if st.form_submit_button("Request Access"):
            if name and phone:
                st.success(f"Thank you {name}! Our wealth management team will contact you shortly.")
            else:
                st.error("Please enter your name and phone number.")

# --- 3. BRANDING ---
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🏢 Dixit Capital & Wealth Management</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Advanced Quantitative Analysis & Portfolio Tracking</p><hr>", unsafe_allow_html=True)

# --- 4. TOP STOCKS DICT (Added 'HOME' option) ---
TOP_STOCKS = {
    "HOME": "🏠 Home (Dashboard)",
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "INFY.NS": "Infosys",
    "ZOMATO.NS": "Zomato",
    "TATAMOTORS.NS": "Tata Motors"
}

# --- 5. SIDEBAR ---
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

# Agar user ne manual type kiya hai toh wo use karo, warna dropdown wala
if manual_ticker:
    raw_ticker = manual_ticker.upper()
    user_ticker = raw_ticker if raw_ticker.endswith(".NS") else f"{raw_ticker}.NS"
else:
    user_ticker = selected_ticker

# --- 6. MAIN DASHBOARD LOGIC ---
if user_ticker == "HOME":
    # 🌟 WELCOME SCREEN (Clean & Simple)
    st.markdown("<h3 style='text-align: center;'>Welcome to the Pro Terminal</h3>", unsafe_allow_html=True)
    st.info("👈 Please search or select a stock from the sidebar menu to begin your analysis.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("**Why use Dixit Capital?**\n\n✅ Institutional Grade Candlestick Charts\n\n✅ Advanced Fundamental Audits\n\n✅ Clean & Ad-Free Interface")
    with col2:
        st.warning("**Market Notice:**\n\nAll financial data is delayed by approximately 15 minutes. Please trade responsibly and consult your financial advisor.")
        
else:
    # 📊 STOCK ANALYSIS SCREEN
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
        curr_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        change = curr_price - prev_price
        pct = (change / prev_price) * 100

        # Clean Title & Price
        display_name = TOP_STOCKS.get(user_ticker, user_ticker.replace('.NS', ''))
        st.markdown(f"## {display_name}")
        st.metric("Last Traded Price", f"₹{curr_price:.2f}", f"{change:.2f} ({pct:.2f}%)")

        # Technical Chart (Always Visible)
        data['SMA50'] = data['Close'].rolling(50).mean()
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Price'))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='orange', width=1.5), name='50-Day SMA'))
        fig.update_layout(template="plotly_dark", margin=dict(t=10, b=10, l=10, r=10), height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # 🧹 EXPANDERS (Hiding the complex stuff to keep UI clean)
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
