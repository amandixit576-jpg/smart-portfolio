import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Financial Statements | DIG", page_icon="📚", layout="wide")

st.write("<br>", unsafe_allow_html=True)
st.markdown("<h1 style='color: #1E88E5;'>📚 Historical Financials & P&L</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888;'>Analyze the multi-year growth trajectory of Revenue and Profitability to find consistent compounding machines.</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 2])
with col1:
    ticker = st.text_input("Enter Company Symbol (e.g., RELIANCE, TCS)", "RELIANCE").upper().strip()

st.write("<br>", unsafe_allow_html=True)

if st.button("Extract Financial Records 📊", type="primary"):
    with st.spinner(f"Extracting 4-Year historical records for {ticker}..."):
        
        sym = f"{ticker}.NS" if not (ticker.endswith('.NS') or ticker.endswith('.BO')) else ticker
        stock = yf.Ticker(sym)
        
        try:
            # P&L Data Fetching
            financials = stock.financials
            
            if financials is None or financials.empty:
                st.error("🚨 No financial data found. The company might be delisted or the symbol is incorrect.")
            else:
                st.success(f"Audit Records Extracted Successfully for {sym}!")
                
                # Data ko sidha (Transpose) karna taaki dates rows ban jayein
                df = financials.T 
                
                # Revenue aur Net Income dhoondhna
                available_cols = df.columns
                revenue_col = 'Total Revenue' if 'Total Revenue' in available_cols else None
                net_income_col = 'Net Income' if 'Net Income' in available_cols else None
                
                if revenue_col and net_income_col:
                    # Chart ke liye clean dataframe banana (Crores mein convert karna)
                    chart_df = df[[revenue_col, net_income_col]].dropna()
                    chart_df = chart_df / 10000000 # Convert to ₹ Crores
                    
                    # Dates ko sirf Year mein convert karna (e.g., 2023, 2024)
                    chart_df.index = pd.to_datetime(chart_df.index).year 
                    chart_df = chart_df.sort_index(ascending=True) # Purane se naya (Left to Right)
                    
                    # --- DISPLAY CHART ---
                    st.markdown("### 📈 Revenue vs Net Profit Trend (₹ Crores)")
                    st.bar_chart(chart_df, height=350, use_container_width=True)
                    
                    # --- DISPLAY AUDIT TABLE ---
                    st.markdown("### 📋 Detailed Income Statement Extract (₹ Crores)")
                    # Dataframe ko sundar format mein dikhana
                    st.dataframe(chart_df.style.format("{:,.2f}"), use_container_width=True)
                    
                    st.info("💡 **Auditor's Tip:** Consistent Year-on-Year (YoY) growth in both Total Revenue and Net Income is the ultimate sign of a strong business moat.")
                else:
                    st.warning("Could not parse standard Revenue/Income columns from this stock's institutional feed.")
                    
        except Exception as e:
            st.error("Connection error. Please try again.")
