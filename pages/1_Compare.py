import streamlit as st
import pandas as pd
from services.stock_data import fetch_safe_info
from utils.formatters import format_inr, format_large_number

# Streamlit config (Har page pe zaroori hai)
st.set_page_config(page_title="Compare Assets | DIG", page_icon="⚖️", layout="wide")

st.markdown("<h2 style='color:#1E88E5;'>⚖️ Smart Peer Comparison Engine</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #888;'>Compare any fundamentally strong companies side-by-side to find the true sector leader.</p>", unsafe_allow_html=True)
st.write("---")

# --- DYNAMIC INPUT SECTION (Ab 5000+ stocks compare honge!) ---
c1, c2 = st.columns(2)
with c1: 
    t1 = st.text_input("Enter Asset 1 (e.g., TCS, ZOMATO)", "TCS").upper().strip()
with c2: 
    t2 = st.text_input("Enter Asset 2 (e.g., INFY, SWIGGY)", "INFY").upper().strip()

st.write("<br>", unsafe_allow_html=True)

if st.button("Run Comparison 🚀", type="primary", use_container_width=True):
    with st.spinner(f"Fetching institutional data for {t1} and {t2}..."):
        
        # NS lagane ka smart logic (Agar user NS lagana bhool jaye)
        sym1 = f"{t1}.NS" if not (t1.endswith('.NS') or t1.endswith('.BO')) else t1
        sym2 = f"{t2}.NS" if not (t2.endswith('.NS') or t2.endswith('.BO')) else t2
        
        # Aapka bulletproof fetch function 🛡️
        i1, i2 = fetch_safe_info(sym1), fetch_safe_info(sym2)
        
        # Asli company ka naam nikalna
        name1 = i1.get('shortName', t1)
        name2 = i2.get('shortName', t2)
        
        comp_data = {
            "Metric": [
                "Sector",
                "Price (₹)", 
                "Market Cap", 
                "P/E Ratio", 
                "P/B Ratio", 
                "ROE (%)", 
                "Debt to Equity",
                "Dividend Yield (%)"
            ],
            name1: [
                i1.get('sector', 'N/A'),
                format_inr(i1.get('currentPrice', 0)), 
                f"₹{format_large_number(i1.get('marketCap', 0))}" if i1.get('marketCap') else 'N/A',
                round(i1.get('trailingPE', 0), 2) if i1.get('trailingPE') else 'N/A', 
                round(i1.get('priceToBook', 0), 2) if i1.get('priceToBook') else 'N/A', 
                round(i1.get('returnOnEquity', 0)*100, 2) if i1.get('returnOnEquity') else 'N/A', 
                round(i1.get('debtToEquity', 0), 2) if i1.get('debtToEquity') else 'N/A',
                round(i1.get('dividendYield', 0)*100, 2) if i1.get('dividendYield') else 'N/A'
            ],
            name2: [
                i2.get('sector', 'N/A'),
                format_inr(i2.get('currentPrice', 0)), 
                f"₹{format_large_number(i2.get('marketCap', 0))}" if i2.get('marketCap') else 'N/A',
                round(i2.get('trailingPE', 0), 2) if i2.get('trailingPE') else 'N/A', 
                round(i2.get('priceToBook', 0), 2) if i2.get('priceToBook') else 'N/A', 
                round(i2.get('returnOnEquity', 0)*100, 2) if i2.get('returnOnEquity') else 'N/A', 
                round(i2.get('debtToEquity', 0), 2) if i2.get('debtToEquity') else 'N/A',
                round(i2.get('dividendYield', 0)*100, 2) if i2.get('dividendYield') else 'N/A'
            ]
        }
        
        # Dataframe ko mast style mein dikhana
        df = pd.DataFrame(comp_data).set_index("Metric")
        
        st.success("Comparison completed successfully!")
        st.dataframe(df, use_container_width=True, height=315)
