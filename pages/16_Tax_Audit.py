import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tax Audit & Portfolio | DIG", page_icon="🧾", layout="wide")

st.write("<br>", unsafe_allow_html=True)
st.markdown("<h1 style='color: #1E88E5;'>🧾 Portfolio Tax Audit Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888;'>Estimate your Capital Gains Tax liability based on the latest Indian Budget equity taxation rules.</p>", unsafe_allow_html=True)
st.write("---")

# --- 📝 TAX AUDIT INPUTS ---
st.markdown("### 📊 Enter Trade Details")
c1, c2, c3 = st.columns(3)

with c1:
    asset = st.text_input("Asset / Stock Name", "Reliance")
    qty = st.number_input("Quantity", min_value=1, value=100, step=10)
    
with c2:
    buy_price = st.number_input("Buy Price (₹)", min_value=1.0, value=1000.0, step=10.0)
    sell_price = st.number_input("Current/Sell Price (₹)", min_value=1.0, value=1400.0, step=10.0)
    
with c3:
    st.write("Holding Period")
    holding_period = st.radio("Select duration to apply correct tax slab:", 
                              ["Short-Term (< 1 Year) [20% Tax]", "Long-Term (> 1 Year) [12.5% Tax]"], 
                              label_visibility="collapsed")

st.write("<br>", unsafe_allow_html=True)

# --- 🧮 CA LEVEL TAX CALCULATION ENGINE ---
if st.button("Calculate Tax Liability & Net Profit 🧮", type="primary", use_container_width=True):
    with st.spinner("Computing tax brackets..."):
        
        invested = buy_price * qty
        current_value = sell_price * qty
        gross_profit = current_value - invested
        
        # Latest Indian Budget Tax Rates
        tax_rate = 0.20 if "Short-Term" in holding_period else 0.125
        tax_name = "STCG (20%)" if "Short-Term" in holding_period else "LTCG (12.5%)"
        
        # Calculate Tax
        if gross_profit > 0:
            tax_amount = gross_profit * tax_rate
            net_profit = gross_profit - tax_amount
        else:
            tax_amount = 0.0
            net_profit = gross_profit # Loss case
            
        st.success(f"Tax Audit Complete for {asset.upper()}")
        
        # --- 📈 DISPLAY BALANCE SHEET ---
        r1, r2, r3, r4 = st.columns(4)
        
        r1.markdown(f"""
        <div style='background-color: #1F2937; padding: 15px; border-radius: 8px; border-left: 4px solid #888;'>
            <p style='color: #888; margin: 0px; font-size: 14px;'>Total Invested</p>
            <h3 style='color: white; margin: 5px 0px 0px 0px;'>₹{invested:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        profit_color = "#10B981" if gross_profit >= 0 else "#DC2626"
        r2.markdown(f"""
        <div style='background-color: #1F2937; padding: 15px; border-radius: 8px; border-left: 4px solid {profit_color};'>
            <p style='color: #888; margin: 0px; font-size: 14px;'>Gross P&L</p>
            <h3 style='color: {profit_color}; margin: 5px 0px 0px 0px;'>₹{gross_profit:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        r3.markdown(f"""
        <div style='background-color: #1F2937; padding: 15px; border-radius: 8px; border-left: 4px solid #F59E0B;'>
            <p style='color: #888; margin: 0px; font-size: 14px;'>Estimated Tax ({tax_name})</p>
            <h3 style='color: #F59E0B; margin: 5px 0px 0px 0px;'>₹{tax_amount:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        r4.markdown(f"""
        <div style='background-color: #1F2937; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6;'>
            <p style='color: #888; margin: 0px; font-size: 14px;'>Net Post-Tax Profit</p>
            <h3 style='color: #3B82F6; margin: 5px 0px 0px 0px;'>₹{net_profit:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)
        st.info("⚠️ **Statutory Audit Note:** This calculation uses flat rates (20% STCG, 12.5% LTCG) per the latest Indian Budget. It does not account for the ₹1.25 Lakh LTCG exemption limit, cess, surcharges, or brokerage fees. For educational purposes only.")
