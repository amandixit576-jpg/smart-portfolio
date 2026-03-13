import streamlit as st

st.set_page_config(page_title="Leadership | DIG", page_icon="⚜️", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E88E5;'>Leadership</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>The minds driving the next generation of financial technology.</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 2.5])

with col1:
    st.markdown("<h1 style='text-align: center; font-size: 120px;'>⚜️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'><b>Headquarters:</b> Lucknow, UP</p>", unsafe_allow_html=True)

with col2:
    st.markdown("### Aman Dixit")
    st.markdown("<h5 style='color: #888;'>Founder & Quantitative Researcher</h5>", unsafe_allow_html=True)
    
    st.write(
        "Aman brings a unique blend of core financial accounting and modern algorithmic analysis to the table. "
        "With a strong foundation in commerce and rigorous training in advanced auditing practices, he recognized a massive gap "
        "in how retail financial data is presented and verified."
    )
    st.write(
        "Operating at the intersection of traditional portfolio management and automated tech, Aman founded DIG to build "
        "a zero-friction screener. His focus remains on structuring high-end market data, automating complex firm operations, "
        "and designing systems that provide institutional-level clarity to every user."
    )
    
    st.markdown(
        """
        <br>
        <a href="https://www.linkedin.com/in/amandixit29" target="_blank" style="text-decoration: none;">
            <div style="background-color: #0A66C2; color: white; padding: 10px 20px; border-radius: 5px; width: 220px; text-align: center; font-weight: bold;">
                🔗 Connect on LinkedIn
            </div>
        </a>
        """, 
        unsafe_allow_html=True
    )
