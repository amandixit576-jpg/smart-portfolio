import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Shareholding | DIG", page_icon="👥", layout="wide")
# --- HIDE DEFAULT STREAMLIT SIDEBAR MENU ---
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)
st.markdown("<h1 style='color: #1E88E5;'>👥 Ownership & Smart Money Track</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888;'>Analyze Promoter conviction and track where Institutional Investors (FIIs/DIIs) are parking their capital.</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 2])
with col1:
    ticker = st.text_input("Enter Company Symbol (e.g., HDFCBANK, ITC)", "HDFCBANK").upper().strip()

st.write("<br>", unsafe_allow_html=True)

if st.button("Analyze Ownership Structure 🕵️‍♂️", type="primary"):
    with st.spinner(f"Extracting Shareholding Data for {ticker}..."):
        
        sym = f"{ticker}.NS" if not (ticker.endswith('.NS') or ticker.endswith('.BO')) else ticker
        stock = yf.Ticker(sym)
        
        try:
            # Fetch Major Holders
            holders = stock.major_holders
            
            if holders is None or holders.empty:
                st.warning("Shareholding data is currently unavailable for this stock via institutional feeds.")
            else:
                st.success(f"Shareholding Audit Complete for {sym}!")
                
                # Cleaning up the data table
                holders.columns = ['Percentage', 'Category']
                
                st.markdown("### 📊 Broad Ownership Breakdown")
                
                # Metrics Display
                r1, r2 = st.columns(2)
                r1.dataframe(holders.set_index('Category'), use_container_width=True)
                
                r2.info("💡 **Auditor's Tip:** \n\n1. **High Insider/Promoter Holding** indicates the founders have strong skin in the game. \n\n2. **High Institutional Holding** means Mutual Funds and FIIs have deeply audited and trusted this business model.")
                
                st.write("<hr>", unsafe_allow_html=True)
                
                # Fetch Institutional Holders (Mutual Funds, FIIs, etc.)
                inst_holders = stock.institutional_holders
                st.markdown("### 🏦 Top Institutional Investors (The 'Smart Money')")
                
                if inst_holders is not None and not inst_holders.empty:
                    # Rename columns for premium feel
                    if 'Holder' in inst_holders.columns:
                        st.dataframe(inst_holders.set_index('Holder'), use_container_width=True)
                    else:
                        st.dataframe(inst_holders, use_container_width=True)
                else:
                    st.info("No major institutional holders found or data not currently disclosed by the exchange.")
                    
        except Exception as e:
            st.error("Error fetching shareholding data. Please verify the NSE symbol and try again.")
