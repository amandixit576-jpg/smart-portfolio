import yfinance as yf
import pandas as pd
import streamlit as st
import sqlite3
import requests

# --- 🛡️ STEALTH MODE ENGINE (Yahoo Blocks ko bypass karne ke liye) ---
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
})

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_safe_info(ticker_symbol):
    # Auto .NS logic
    if not ticker_symbol.endswith('.NS') and not ticker_symbol.endswith('.BO'):
        ticker_symbol += '.NS'
        
    # 3 baar try karega stealth mode mein
    for _ in range(3):
        try:
            t = yf.Ticker(ticker_symbol, session=session)
            inf = t.info
            # Check karega ki asli data aaya ya nahi
            if inf and 'currentPrice' in inf: 
                return inf
        except:
            pass
    return {}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_history(ticker_symbol, period="1y"):
    if not ticker_symbol.endswith('.NS') and not ticker_symbol.endswith('.BO'):
        ticker_symbol += '.NS'
        
    try:
        # 1. Pehle local DB (Godown) check karega
        conn = sqlite3.connect('dig_master.db')
        table_name = ticker_symbol.replace('.NS', '')
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        conn.close()
        return df
    except:
        # 2. Agar DB mein nahi hai, toh Yahoo se Stealth mode mein layega
        try:
            t = yf.Ticker(ticker_symbol, session=session)
            df = t.history(period=period)
            if df.empty:
                df = t.history(period="1mo")
            return df
        except:
            return pd.DataFrame()

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_financials(ticker_symbol):
    if not ticker_symbol.endswith('.NS'):
        ticker_symbol += '.NS'
    try:
        t = yf.Ticker(ticker_symbol, session=session)
        return t.financials, t.balance_sheet
    except:
        return pd.DataFrame(), pd.DataFrame()
