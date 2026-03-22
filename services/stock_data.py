import yfinance as yf
import pandas as pd
import requests
import streamlit as st
import sqlite3

# --- PRO DATA ENGINE (ANTI-BLOCK) ---
# Ek "Human-like" session banate hain taaki Yahoo block na kare
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
})

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_safe_info(ticker_symbol):
    import time
    import requests
    
    # 1. Sabse badi galti ka ilaj: Agar naam ke aage .NS nahi laga hai, toh khud laga do
    if not ticker_symbol.endswith('.NS') and not ticker_symbol.endswith('.BO'):
        yahoo_symbol = f"{ticker_symbol}.NS"
    else:
        yahoo_symbol = ticker_symbol
        
    # 2. Smart Retry Logic (Agar Yahoo block kare toh naye bhes mein jayega)
    for attempt in range(3):
        try:
            # Har try mein naya aur strong "User-Agent" (Bhes badalna)
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            })
            
            t = yf.Ticker(yahoo_symbol, session=session)
            inf = t.info
            
            # 3. Check karna ki asli data aaya hai ya khali dabba (Market Cap check karke)
            if inf and ('marketCap' in inf or len(inf) > 10):
                return inf
            else:
                time.sleep(1) # 1 second ruk kar dobara try karega
                
        except Exception as e:
            time.sleep(1)
            
    # Agar 3 baar mein bhi fail ho jaye
    return {}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_history(ticker_symbol, period="1y"):
    import sqlite3
    import pandas as pd
    import yfinance as yf
    
    try:
        # 1. Godown (Database) check karega
        conn = sqlite3.connect('dig_master.db')
        table_name = ticker_symbol.replace('.NS', '')
        
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        conn.close()
        return df
        
    except Exception as e:
        # 2. Agar stock DB mein nahi hai, toh seedha Yahoo se layega (BUG FIXED)
        try:
            if not ticker_symbol.endswith('.NS') and not ticker_symbol.endswith('.BO'):
                yahoo_symbol = f"{ticker_symbol}.NS"
            else:
                yahoo_symbol = ticker_symbol
                
            t = yf.Ticker(yahoo_symbol) # Yahan se purana session logic hata diya jo crash kar raha tha
            df = t.history(period=period)
            if df.empty:
                df = t.history(period="1mo")
            return df
        except:
            return pd.DataFrame()

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_financials(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    try: return t.financials, t.balance_sheet
    except: return pd.DataFrame(), pd.DataFrame()
