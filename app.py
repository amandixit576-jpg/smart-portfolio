import streamlit as st
import yfinance as yf
import plotly.graph_objects as go  # Naya Hatyar (Interactive Charts)

# Page Setup
st.set_page_config(page_title="Smart Portfolio", layout="wide")
st.title("📊 Smart Portfolio Pro-Terminal")

# --- SIDEBAR: Controls ---
st.sidebar.header("Terminal Settings")
risk = st.sidebar.selectbox("Risk Profile:", ["Low (Safe)", "Medium (Balanced)", "High (Aggressive)"])

# Logic
suggested = "RELIANCE.NS"
if risk == "Low (Safe)":
    suggested = "LIQUIDBEES.NS"
elif risk == "Medium (Balanced)":
    suggested = "NIFTYBEES.NS"

user_ticker = st.sidebar.text_input("Search NSE Stock (e.g. TCS.NS):", suggested)

# --- MAIN ENGINE ---
@st.cache_data(ttl=300)
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        # Candlestick ke liye 3 mahine ka data zyada acha dikhta hai
        return stock.history(period="3mo")
    except:
        return None

data = get_stock_data(user_ticker)

if data is not None and not data.empty:
    curr_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2]
    change = curr_price - prev_price
    pct_change = (change / prev_price) * 100
    
    # Header Metrics
    st.subheader(f"📈 {user_ticker} Live Status")
    st.metric(label="Current Market Price", 
              value=f"₹{curr_price:.2f}", 
              delta=f"{change:.2f} ({pct_change:.2f}%)")
    
    st.write("---")
    st.write("**Interactive Candlestick Chart (Last 3 Months)**")
    
    # --- TICKERTAPE STYLE CHART ---
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=user_ticker,
        increasing_line_color='green', 
        decreasing_line_color='red'
    )])
    
    # Chart ko sundar banane ki settings
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=550,
        xaxis_rangeslider_visible=False, # Niche ka extra slider hata diya clean look ke liye
        template="plotly_dark" # Streamlit dark mode mein ekdum premium lagega
    )
    
    # Chart ko screen par dikhana
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"💡 Based on your {risk} profile, we suggest tracking {suggested}.")

else:
    st.error("⚠️ Stock symbol galat hai. Kripya '.NS' lagana na bhoolein (Jaise: HDFCBANK.NS)")
