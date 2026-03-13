import yfinance as yf
import pandas as pd
import requests
import streamlit as st

# --- PRO DATA ENGINE (ANTI-BLOCK) ---
# Ek "Human-like" session banate hain taaki Yahoo block na kare
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
})

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_safe_info(ticker_symbol):
    import time # Local import taaki code smoothly chale
    
    # API ko 3 baar try karne ka chance denge (Smart Retry Logic)
    for attempt in range(3):
        try:
            t = yf.Ticker(ticker_symbol, session=session)
            inf = t.info
            
            # Agar data theek se aa gaya (कम से कम 10 values)
            if inf and len(inf) > 10:
                return inf
            else:
                time.sleep(0.5) # Agar Yahoo ne block kiya, toh 0.5 sec ruk kar dobara maangega
        except:
            time.sleep(1) # Error aane par 1 sec saans lega aur retry karega
            
    # Agar 3 baar mein bhi fail ho jaye tabhi khali return karega
    return {}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_history(ticker_symbol, period="1y"):
    try:
        t = yf.Ticker(ticker_symbol, session=session)
        df = t.history(period=period)
        if df.empty:
            df = t.history(period="1mo")
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_financials(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    try: return t.financials, t.balance_sheet
    except: return pd.DataFrame(), pd.DataFrame()
