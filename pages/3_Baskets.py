import streamlit as st

# Har page par Streamlit config sabse upar
st.set_page_config(page_title="Theme Baskets | DIG", page_icon="🧺", layout="wide")

st.markdown("<h2 style='color:#1E88E5;'>🧺 Ready-Made Theme Baskets</h2>", unsafe_allow_html=True)
st.write("Invest in ideas, not just single stocks. Explore top sectors and themes driving the market.")
st.write("---")

# --- BASKETS GRID ---
b1, b2, b3 = st.columns(3)

with b1:
    st.markdown('<div class="basket-card"><div class="basket-title">🌱 Green Energy & EV</div><p>Tata Power, Suzlon, Adani Green</p></div>', unsafe_allow_html=True)
    if st.button("Analyze Green Energy", key="b_green", use_container_width=True): 
        st.session_state.current_view = "TATAPOWER.NS"
        st.switch_page("app.py") # Ye main analysis engine par bhej dega

with b2:
    st.markdown('<div class="basket-card"><div class="basket-title">👑 Monopoly Stocks</div><p>IRCTC, IEX, CDSL, HAL</p></div>', unsafe_allow_html=True)
    if st.button("Analyze Monopolies", key="b_mono", use_container_width=True): 
        st.session_state.current_view = "IRCTC.NS"
        st.switch_page("app.py")

with b3:
    st.markdown('<div class="basket-card"><div class="basket-title">🏦 PSU Banking</div><p>SBI, PNB, Bank of Baroda</p></div>', unsafe_allow_html=True)
    if st.button("Analyze PSU Banks", key="b_psu", use_container_width=True): 
        st.session_state.current_view = "SBIN.NS"
        st.switch_page("app.py")

st.write("")
b4, b5, b6 = st.columns(3)

with b4:
    st.markdown('<div class="basket-card"><div class="basket-title">🍃 Ethical & Cruelty-Free</div><p>Pure vegetarian FMCG & mindful brands (Tata Consumer)</p></div>', unsafe_allow_html=True)
    if st.button("Analyze Ethical Basket", key="b_ethical", use_container_width=True): 
        st.session_state.current_view = "TATACONSUM.NS"
        st.switch_page("app.py")

with b5:
    st.markdown('<div class="basket-card"><div class="basket-title">💻 Tech & Innovation</div><p>IT Giants shaping the future (TCS, HCLTech)</p></div>', unsafe_allow_html=True)
    if st.button("Analyze Tech Basket", key="b_tech", use_container_width=True): 
        st.session_state.current_view = "HCLTECH.NS"
        st.switch_page("app.py")

with b6:
    st.markdown('<div class="basket-card"><div class="basket-title">💰 Dividend Kings</div><p>Consistent high-yield cash generators (Coal India, ITC)</p></div>', unsafe_allow_html=True)
    if st.button("Analyze Dividend Kings", key="b_div", use_container_width=True): 
        st.session_state.current_view = "COALINDIA.NS"
        st.switch_page("app.py")
