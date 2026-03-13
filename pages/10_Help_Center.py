import streamlit as st

st.set_page_config(page_title="Help Center | DIG", page_icon="⚜️", layout="wide")

# --- HIDE SIDEBAR MENU HACK ---
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E88E5;'>Help Center & FAQs</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Find answers to common questions about DIG Terminal.</p>", unsafe_allow_html=True)
st.write("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### 📌 Frequently Asked Questions")
    
    with st.expander("1. Where does DIG get its financial data?"):
        st.write("We use institutional-grade real-time feeds powered by the Yahoo Finance API. This ensures our stock prices and financial ratios are highly accurate and constantly updated.")
        
    with st.expander("2. Is the data really live?"):
        st.write("Yes! However, depending on network traffic and API rate limits, there might be a slight delay of a few seconds. We use an advanced caching system to ensure the site never crashes.")
        
    with st.expander("3. Does DIG provide stock tips or recommendations?"):
        st.write("Absolutely NOT. DIG is a purely analytical and educational tool. We provide the numbers, ratios, and raw data. The investment decision is entirely yours.")
        
    with st.expander("4. How are the financial ratios calculated?"):
        st.write("Our ratios are derived using strict, standard accounting practices. We cross-verify basic fundamental parameters (like PE, ROE, Debt) to give you an 'Audit-Ready' view of the company.")

    st.write("---")
    st.markdown("### 📩 Still need help?")
    st.info("Drop us an email at: **support@digscreener.in** (Response time: 24-48 hours)")
