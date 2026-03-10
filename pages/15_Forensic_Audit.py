import streamlit as st
import pandas as pd
from services.stock_data import fetch_safe_info

# Streamlit config
st.set_page_config(page_title="Forensic Audit | DIG", page_icon="🕵️‍♂️", layout="wide")
# --- HIDE DEFAULT STREAMLIT SIDEBAR MENU ---
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)
st.markdown("<h1 style='color: #1E88E5;'>🕵️‍♂️ Forensic Audit & Health Check</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888;'>Perform an institutional-grade fundamental health check, DuPont Analysis, and identify potential red flags.</p>", unsafe_allow_html=True)
st.write("---")

# --- INPUT SECTION ---
col1, col2 = st.columns([1, 2])
with col1:
    ticker = st.text_input("Enter Company Symbol (e.g., ITC, SUZLON)", "ITC").upper().strip()

st.write("<br>", unsafe_allow_html=True)

if st.button("Run Full Forensic Audit 🔍", type="primary"):
    with st.spinner(f"Auditing financial statements for {ticker}..."):
        
        # Smart symbol formatting
        sym = f"{ticker}.NS" if not (ticker.endswith('.NS') or ticker.endswith('.BO')) else ticker
        
        # Safe fetch using your existing service
        info = fetch_safe_info(sym)
        
        if not info or 'longName' not in info:
            st.error("Audit Failed! Could not fetch financial data. Please check the NSE symbol.")
        else:
            st.success(f"Audit Complete for {info.get('longName', ticker)}")
            
            # --- 🧮 DUPONT ANALYSIS SECTION ---
            st.markdown("### 🧮 DuPont Analysis Overview")
            st.info("ROE is driven by three engines: Profitability (Margin), Efficiency (Asset Turnover), and Leverage (Equity Multiplier).")
            
            roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
            npm = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
            roa = info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0
            
            d1, d2, d3 = st.columns(3)
            d1.metric("Return on Equity (ROE)", f"{round(roe, 2)}%" if roe else "N/A")
            d2.metric("Net Profit Margin", f"{round(npm, 2)}%" if npm else "N/A")
            d3.metric("Return on Assets (ROA)", f"{round(roa, 2)}%" if roa else "N/A")
            
            st.write("<hr>", unsafe_allow_html=True)
            
            # --- 🏥 LIQUIDITY & SOLVENCY HEALTH ---
            st.markdown("### 🏥 Financial Solvency Check")
            cr = info.get('currentRatio', 0)
            qr = info.get('quickRatio', 0)
            de = info.get('debtToEquity', 0)
            
            h1, h2, h3 = st.columns(3)
            
            # Current Ratio Check
            cr_status = "Ideal (> 1.5)" if cr and cr > 1.5 else ("Risky (< 1)" if cr and cr < 1 else "Average")
            cr_color = "normal" if cr and cr > 1 else "inverse"
            h1.metric("Current Ratio", round(cr, 2) if cr else "N/A", cr_status, delta_color=cr_color)
            
            # Quick Ratio Check
            qr_status = "Ideal (> 1.0)" if qr and qr > 1.0 else "Tight Liquidity"
            qr_color = "normal" if qr and qr > 1 else "inverse"
            h2.metric("Quick Ratio", round(qr, 2) if qr else "N/A", qr_status, delta_color=qr_color)
            
            # Debt to Equity Check
            h3.metric("Debt to Equity", round(de, 2) if de else "N/A", "Debt Level")
            
            st.write("<hr>", unsafe_allow_html=True)
            
            # --- 🚩 AUTOMATED CA RED FLAGS ---
            st.markdown("### 🚩 Automated Audit Flags")
            
            red_flags = []
            if cr and cr < 1.0: 
                red_flags.append("🚨 **Severe Liquidity Risk:** Current Ratio is strictly below 1.0. Company may struggle to pay short-term liabilities.")
            if de and de > 150: # Yahoo finance returns D/E in percentage usually (e.g., 150 = 1.5x)
                red_flags.append("🚨 **High Leverage Warning:** Debt to Equity ratio is dangerously high.")
            if roe and roe < 8.0: 
                red_flags.append("⚠️ **Low Profitability:** Return on Equity is below the standard risk-free rate (approx 7-8%).")
            if npm and npm < 0:
                red_flags.append("🚨 **Operational Loss:** The company is currently generating negative net profit margins.")
                
            if not red_flags:
                st.success("✅ **Clean Audit:** No major fundamental red flags detected in current operational metrics.")
            else:
                for flag in red_flags:
                    st.warning(flag)
