import streamlit as st

st.set_page_config(page_title="Our Vision | DIG", page_icon="⚜️", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E88E5;'>Our Vision</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>Democratizing Institutional-Grade Financial Data.</p>", unsafe_allow_html=True)
st.write("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### 🔭 The Future of Investing")
    st.write(
        "For decades, advanced quantitative analysis and deep portfolio management tools have been locked behind "
        "expensive paywalls, accessible only to elite hedge funds and large institutions. At Dixit Investment Group (DIG), "
        "we are actively tearing down those walls."
    )
    st.write(
        "Our vision is to build a completely automated, data-driven ecosystem where every retail investor, "
        "financial auditor, and market enthusiast has access to lightning-fast, unbiased, and mathematically sound equity research."
    )
    
    st.markdown("### ⚡ Core Pillars")
    st.info("**1. Radical Transparency:** Clean data directly from institutional APIs, no hidden agendas.")
    st.success("**2. Audit-Grade Accuracy:** Financial ratios calculated with the precision of strict auditing standards.")
    st.warning("**3. Seamless Automation:** Complex fundamental analysis simplified into one-click actionable insights.")

st.write("---")
