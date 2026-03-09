import streamlit as st

st.set_page_config(page_title="About Us | DIG", page_icon="⚜️", layout="wide")

st.write("<br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #1E88E5; font-size: 3.5rem;'>⚜️ About Dixit Investment Group</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>Democratizing elite financial analytics for the modern value investor.</p>", unsafe_allow_html=True)
st.write("<hr>", unsafe_allow_html=True)

col1, spacer, col2 = st.columns([2, 0.2, 1])

with col1:
    st.markdown("""
    ### 📌 Our Story
    Dixit Investment Group (DIG) was born out of a passion for deep fundamental analysis, quantitative research, and data-driven investing. 
    Rooted in the heart of **Lucknow**, our mission is to build tools that bring institutional-grade financial analytics to retail investors and financial professionals.
    
    ### 🎯 The Vision
    We believe in making calculated, risk-adjusted decisions in the Indian equity markets. Whether it's analyzing complex financial ratios, running CA-grade tax audits on your portfolio, or planning for a long-term lifestyle milestone, the DIG Terminal is engineered to be your ultimate financial command center.
    
    ### 💎 Core Values
    * **Precision:** Upholding the highest standards of data accuracy and accounting principles.
    * **Transparency:** Delivering clear, unbiased, and objective market insights.
    * **Growth:** Fostering continuous financial learning and long-term wealth creation.
    """)
    
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("**🏢 Headquarters:**\nLucknow, Uttar Pradesh")
    st.success("**🔬 Core Focus:**\nQuantitative Research, Tax Audits, Value Investing")
    st.warning("**📈 Coverage:**\nNSE Listed Equities & Mutual Funds")

st.write("<br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    if st.button("⬅️ Back to Main Terminal", use_container_width=True, type="primary"):
        st.switch_page("app.py")
