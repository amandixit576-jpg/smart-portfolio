import streamlit as st
import pandas as pd
from services.stock_data import fetch_safe_info
from utils.formatters import format_inr, format_large_number

# Streamlit config (Har page pe zaroori hai)
st.set_page_config(page_title="Compare Assets | DIG", page_icon="⚖️", layout="wide")

st.markdown("<h2 style='color:#1E88E5;'>⚖️ Peer-to-Peer Asset Comparison</h2>", unsafe_allow_html=True)
st.write("---")

TOP_STOCKS = {"RELIANCE.NS": "Reliance", "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC Bank", "INFY.NS": "Infosys", "ZOMATO.NS": "Zomato", "ITC.NS": "ITC", "SBIN.NS": "SBI"}

c1, c2 = st.columns(2)
with c1: t1 = st.selectbox("Select Asset 1:", list(TOP_STOCKS.keys()), index=0)
with c2: t2 = st.selectbox("Select Asset 2:", list(TOP_STOCKS.keys()), index=2)

if st.button("Run Comparison 🚀", type="primary"):
    with st.spinner("Fetching data for comparison..."):
        i1, i2 = fetch_safe_info(t1), fetch_safe_info(t2)
        
        comp_data = {
            "Metric": ["Price (₹)", "P/E Ratio", "P/B Ratio", "ROE (%)", "Debt to Equity", "Market Cap"],
            TOP_STOCKS[t1]: [
                format_inr(i1.get('currentPrice')), 
                round(i1.get('trailingPE', 0), 2) if i1.get('trailingPE') else 'N/A', 
                round(i1.get('priceToBook', 0), 2) if i1.get('priceToBook') else 'N/A', 
                round(i1.get('returnOnEquity', 0)*100, 2) if i1.get('returnOnEquity') else 'N/A', 
                round(i1.get('debtToEquity', 0), 2) if i1.get('debtToEquity') else 'N/A', 
                f"₹{format_large_number(i1.get('marketCap'))}"
            ],
            TOP_STOCKS[t2]: [
                format_inr(i2.get('currentPrice')), 
                round(i2.get('trailingPE', 0), 2) if i2.get('trailingPE') else 'N/A', 
                round(i2.get('priceToBook', 0), 2) if i2.get('priceToBook') else 'N/A', 
                round(i2.get('returnOnEquity', 0)*100, 2) if i2.get('returnOnEquity') else 'N/A', 
                round(i2.get('debtToEquity', 0), 2) if i2.get('debtToEquity') else 'N/A', 
                f"₹{format_large_number(i2.get('marketCap'))}"
            ]
        }
        st.table(pd.DataFrame(comp_data).set_index("Metric"))
