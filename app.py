import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Pro Terminal | Stock Screener", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM BRANDING & HEADER ---
# Yahan aap apni company ka naam aur tagline change kar sakte hain
st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <h1 style='color: #1E88E5; font-family: "Arial Black", sans-serif;'>🏢 Dixit Capital & Wealth Management</h1>
        <p style='font-style: italic; color: #888888; font-size: 18px;'>Advanced Quantitative Analysis & Portfolio Tracking</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("⚙️ Terminal Settings")

# Professional English Terminology
risk_profile = st.sidebar.selectbox(
    "Client Risk Appetite:", 
    ["Conservative (Low Risk)", "Moderate (Balanced)", "Aggressive (High Risk)"]
)

# Benchmark Suggestions
benchmark_ticker = "RELIANCE.NS"
if risk_profile == "Conservative (Low Risk)":
    benchmark_ticker = "LIQUIDBEES.NS"
elif risk_profile == "Moderate (Balanced)":
    benchmark_ticker = "NIFTYBEES.NS"

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Equity Search")
user_ticker = st.sidebar.text_input("Enter NSE Ticker Symbol:", benchmark_ticker)
st.sidebar.caption("Example: HDFCBANK.NS, TCS.NS, INFY.NS")

# --- DATA FETCHING ENGINE ---
@st.cache_data(ttl=300)
def fetch_market_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        # Fetching 1 year of data to calculate 200-Day Moving Average properly
        return stock.history(period="1y")
    except:
        return None

data = fetch_market_data(user_ticker)

# --- MAIN DASHBOARD ---
if data is not None and not data.empty:
    
    # Calculate Key Metrics
    curr_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2]
    price_change = curr_price - prev_price
    pct_change = (price_change / prev_price) * 100
    
    # Calculate Moving Averages
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    
    # Top Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"{user_ticker} - Last Traded Price", 
                  value=f"₹{curr_price:.2f}", 
                  delta=f"{price_change:.2f} ({pct_change:.2f}%)")
    with col2:
        st.metric(label="50-Day SMA", value=f"₹{data['SMA_50'].iloc[-1]:.2f}" if not data['SMA_50'].isna().iloc[-1] else "N/A")
    with col3:
        st.metric(label="200-Day SMA", value=f"₹{data['SMA_200'].iloc[-1]:.2f}" if not data['SMA_200'].isna().iloc[-1] else "N/A")
        
    st.markdown("### 📊 Interactive Technical Chart")
    
    # --- PLOTLY CANDLESTICK CHART ---
    fig = go.Figure()
    
    # 1. Candlestick Trace
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        name='Market Price',
        increasing_line_color='#26A69A', decreasing_line_color='#EF5350'
    ))
    
    # 2. 50-Day Moving Average Trace
    fig.add_trace(go.Scatter(
        x=data.index, y=data['SMA_50'],
        line=dict(color='orange', width=1.5),
        name='50-Day SMA'
    ))
    
    # 3. 200-Day Moving Average Trace
    fig.add_trace(go.Scatter(
        x=data.index, y=data['SMA_200'],
        line=dict(color='blue', width=1.5),
        name='200-Day SMA'
    ))
    
    # Chart Layout Formatting
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=10, r=10, t=30, b=10),
        height=600,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Footer Insight
    st.info(f"**System Note:** Based on the selected **{risk_profile}** profile, the recommended benchmark asset is **{benchmark_ticker}**.")

else:
    st.error("⚠️ Invalid Ticker Symbol. Please ensure you append '.NS' for National Stock Exchange securities (e.g., ZOMATO.NS).")

