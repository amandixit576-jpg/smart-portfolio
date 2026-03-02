import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Pro Terminal | Stock Screener", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM BRANDING & HEADER ---
st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <h1 style='color: #1E88E5; font-family: "Arial Black", sans-serif;'>🏢 Dixit Capital & Wealth Management</h1>
        <p style='font-style: italic; color: #888888; font-size: 18px;'>Advanced Quantitative Analysis & Portfolio Tracking</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("⚙️ Terminal Settings")

risk_profile = st.sidebar.selectbox(
    "Client Risk Appetite:", 
    ["Conservative (Low Risk)", "Moderate (Balanced)", "Aggressive (High Risk)"]
)

benchmark_ticker = "RELIANCE.NS"
if risk_profile == "Conservative (Low Risk)":
    benchmark_ticker = "LIQUIDBEES.NS"
elif risk_profile == "Moderate (Balanced)":
    benchmark_ticker = "NIFTYBEES.NS"

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Equity Search")
raw_ticker = st.sidebar.text_input("Enter Company Name/Symbol:", "RELIANCE").upper()
user_ticker = raw_ticker if raw_ticker.endswith(".NS") else f"{raw_ticker}.NS"

st.sidebar.caption("Example: HDFCBANK, TCS, ZOMATO")

# --- DATA FETCHING ENGINE ---
@st.cache_data(ttl=300)
def fetch_market_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        return stock.history(period="1y")
    except:
        return None

@st.cache_data(ttl=3600)
def fetch_fundamentals(symbol):
    try:
        stock = yf.Ticker(symbol)
        return stock.info
    except:
        return {}

@st.cache_data(ttl=1800)
def fetch_news(symbol):
    try:
        stock = yf.Ticker(symbol)
        return stock.news
    except:
        return []

data = fetch_market_data(user_ticker)
info = fetch_fundamentals(user_ticker)
news_data = fetch_news(user_ticker)

# --- MAIN DASHBOARD ---
if data is not None and not data.empty:
    
    curr_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2]
    price_change = curr_price - prev_price
    pct_change = (price_change / prev_price) * 100
    
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    
    # Top Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"{raw_ticker} - Last Traded Price", 
                  value=f"₹{curr_price:.2f}", 
                  delta=f"{price_change:.2f} ({pct_change:.2f}%)")
    with col2:
        st.metric(label="50-Day SMA", value=f"₹{data['SMA_50'].iloc[-1]:.2f}" if not data['SMA_50'].isna().iloc[-1] else "N/A")
    with col3:
        st.metric(label="200-Day SMA", value=f"₹{data['SMA_200'].iloc[-1]:.2f}" if not data['SMA_200'].isna().iloc[-1] else "N/A")
        
    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["📈 Technical Analysis", "📋 Fundamental Audit", "📰 Latest News"])
    
    with tab1:
        st.markdown("### Interactive Technical Chart")
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
            name='Market Price',
            increasing_line_color='#26A69A', decreasing_line_color='#EF5350'
        ))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], line=dict(color='orange', width=1.5), name='50-Day SMA'))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_200'], line=dict(color='blue', width=1.5), name='200-Day SMA'))
        
        fig.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=30, b=10), height=550, xaxis_rangeslider_visible=False, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_
