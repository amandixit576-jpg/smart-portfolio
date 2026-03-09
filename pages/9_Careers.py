import streamlit as st

st.set_page_config(page_title="Careers | DIG", page_icon="⚜️", layout="wide")

st.write("<br><br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #1E88E5; font-size: 3.5rem;'>⚜️ Careers</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>This section is currently being updated with institutional-grade content.</p>", unsafe_allow_html=True)
st.write("<hr>", unsafe_allow_html=True)

st.info("The detailed documentation for this section will be published here shortly.")

st.write("<br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    if st.button("⬅️ Back to Main Terminal", use_container_width=True, type="primary"):
        st.switch_page("app.py")
