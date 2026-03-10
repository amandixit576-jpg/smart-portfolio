import streamlit as st
import plotly.graph_objects as go
from services.stock_data import fetch_stock_history
from utils.formatters import format_inr

# Har page par Streamlit config zaroori hai
st.set_page_config(page_title="Mutual Funds | DIG", page_icon="📈", layout="wide")
# --- HIDE DEFAULT STREAMLIT SIDEBAR MENU ---
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color:#1E88E5;'>📈 Mutual Fund Tracker</h2>", unsafe_allow_html=True)
st.write("---")

MF_DICT = {
    "Parag Parikh Flexi Cap Fund": "0P0000YWL1.BO", 
    "SBI Small Cap Fund": "0P0000XW8F.BO", 
    "Axis Bluechip Fund": "0P0000XVAA.BO",
    "HDFC Mid-Cap Opportunities": "0P0000XVU0.BO", 
    "ICICI Prudential Technology Fund": "0P0000XVYV.BO", 
    "Quant Small Cap Fund": "0P0001B61B.BO"
}

selected_mf = st.selectbox("Select a Mutual Fund to Analyze:", list(MF_DICT.keys()))
mf_ticker = MF_DICT[selected_mf]

if st.button("Fetch NAV & Chart 🚀", type="primary"):
    with st.spinner("Fetching latest NAV..."):
        # Yahan humne aapke naye 'Engine' ko call kiya hai
        hist = fetch_stock_history(mf_ticker, "1y")

        if hist is not None and not hist.empty and len(hist) >= 2:
            current_nav = hist['Close'].iloc[-1]
            prev_nav = hist['Close'].iloc[-2]
            
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"### {selected_mf}")
            
            # Nav metric with formatting
            c2.metric(
                "Current NAV", 
                f"₹{format_inr(round(current_nav, 2))}", 
                f"{(current_nav - prev_nav):.2f} ({((current_nav - prev_nav)/prev_nav)*100:.2f}%)"
            )

            # Plotly Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['Close'], 
                mode='lines', fill='tozeroy', 
                line=dict(color='#1E88E5'), name='NAV'
            ))
            fig.update_layout(
                template="plotly_white", 
                margin=dict(t=10, b=10, l=10, r=10), 
                height=400, yaxis_title="Net Asset Value (₹)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else: 
            st.error("⚠️ Data not available for this Mutual Fund right now.")
