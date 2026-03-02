import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# --- 1. PAGE SETUP & MEMORY ---
st.set_page_config(page_title="Pro Terminal | Dixit Capital", layout="wide", initial_sidebar_state="expanded")

# App ki memory (State) ban banana taaki wo yaad rakhe hum kahan hain
if 'current_view' not in st.session_state:
    st.session_state.current_view = "HOME"

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    hr { margin-top: 1rem; margin-bottom: 1.5rem; border-color: #333; }
    /* Making the link look exactly like text */
    a { text-decoration: none !important; color: inherit !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LEAD GENERATION (WHATSAPP) ---
@st.dialog("👑 Unlock Premium Access")
def premium_signup():
    st.markdown("Join **Dixit Capital Premium** to get the access code for our AI Quant Analyst.")
    YOUR_WHATSAPP_NUMBER = "917052360459" 
    name = st.text_input("Full Name")
    city = st.text_input("City")
    st.write("---")
    if name and city:
        raw_message = f"Hello Dixit Capital! 📈\n\nI want to purchase the Premium Access Code for the Quant Analyst tool.\nName: {name}\nCity: {city}"
        encoded_message = urllib.parse.quote(raw_message)
        whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={encoded_message}"
        st.link_button("📲 Chat with Team to get Code", whatsapp_url, type="primary", use_container_width=True)
    else:
        st.button("📲 Chat with Team to get Code", type="primary", disabled=True, use_container_width=True)

# --- 3. CLICKABLE BRANDING ---
# href="/" ka matlab hai ki click karte hi app refresh hokar Home par aayegi
st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <a href="/" target="_self">
            <h1 style='color: #1E88E5; font-family: "Arial Black", sans-serif; cursor: pointer;'>🏢 Dixit Capital & Wealth Management</h1>
        </a>
        <p style='font-style: italic; color: #888888; font-size: 18px;'>Advanced Quantitative Analysis & Portfolio Tracking</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# --- 4. TOP STOCKS LIST ---
TOP_STOCKS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "INFY.NS": "Infosys",
    "ZOMATO.NS": "Zomato",
    "TATAMOTORS.NS": "Tata Motors",
    "ITC.NS": "ITC Limited",
    "SBIN.NS": "State Bank of India"
}

# --- 5. SIDEBAR MENU ---
st.sidebar.header("⚙️ Main Menu")

if st.sidebar.button("🏠 Go to Home Dashboard", use_container_width=True):
    st.session_state.current_view = "HOME"
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)

if st.sidebar.button("👑 Upgrade to Premium", use_container_width=True):
    premium_signup()
    
st.sidebar.caption("Click 'DIXIT CAPITAL' at the top to return Home anytime.")

# Helper Functions
@st.cache_data(ttl=300)
def get_index_data(ticker):
    try: return yf.Ticker(ticker).history(period="2d")
    except: return None

@st.cache_data(ttl=1800)
def get_live_news(company_name):
    try:
        query = urllib.parse.quote(f"{company_name} share stock news India")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        news_items = []
        for item in root.findall('.//item')[:4]: 
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            if ' - ' in title: title, source = title.rsplit(' - ', 1)
            else: source = "Financial News"
            news_items.append({'title': title, 'link': link, 'source': source, 'date': pub_date[5:16]})
        return news_items
    except: return []

# --- 6. HOME PAGE (Centralized Layout) ---
if st.session_state.current_view == "HOME":
    
    # 🔍 Center Search Bar
    st.markdown("<h3 style='text-align: center;'>🔍 Search Asset for Analysis</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1]) # Center alignment
    with col2:
        selected_ticker = st.selectbox("Select from Top Companies:", ["-- Select --"] + list(TOP_STOCKS.keys()), format_func=lambda x: TOP_STOCKS.get(x, x))
        manual_ticker = st.text_input("Or enter NSE symbol manually (e.g., ITC):", placeholder="Enter ticker symbol...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 Run Technical Audit", type="primary", use_container_width=True):
            target = manual_ticker.upper() if manual_ticker else selected_ticker
            if target and target != "-- Select --":
                final_ticker = target if target.endswith(".NS") else f"{target}.NS"
                st.session_state.current_view = final_ticker
                st.rerun()
            else:
                st.error("Please select or enter a valid stock symbol.")
                
    st.write("---")

    # 📡 Market Pulse
    st.markdown("<h4 style='text-align: center;'>📡 Live Market Pulse</h4>", unsafe_allow_html=True)
    nifty = get_index_data("^NSEI")
    banknifty = get_index_data("^NSEBANK")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns([1, 2, 2, 1])
    if nifty is not None and len(nifty) >= 2:
        n_curr, n_prev = nifty['Close'].iloc[-1], nifty['Close'].iloc[-2]
        m_col2.metric("NIFTY 50", f"{n_curr:.2f}", f"{n_curr - n_prev:.2f} ({(n_curr - n_prev)/n_prev * 100:.2f}%)")
    if banknifty is not None and len(banknifty) >= 2:
        bn_curr, bn_prev = banknifty['Close'].iloc[-1], banknifty['Close'].iloc[-2]
        m_col3.metric("NIFTY BANK", f"{bn_curr:.2f}", f"{bn_curr - bn_prev:.2f} ({(bn_curr - bn_prev)/bn_prev * 100:.2f}%)")
        
    st.write("---")

    # 💰 Wealth Calculator
    st.markdown("<h4 style='text-align: center;'>💰 SIP Wealth Calculator</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Plan your financial independence.</p>", unsafe_allow_html=True)
    
    calc_col1, calc_col2 = st.columns([1, 2])
    with calc_col1:
        sip_amount = st.number_input("Monthly SIP (₹)", min_value=500, value=5000, step=500)
        sip_years = st.slider("Investment Period (Years)", 1, 30, 10)
        sip_rate = st.slider("Expected Annual Return (%)", 5, 25, 12)
    with calc_col2:
        monthly_rate = sip_rate / 12 / 100
        months = sip_years * 12
        invested_amount = sip_amount * months
        future_value = sip_amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
        st.success(f"### Estimated Wealth: ₹{future_value:,.0f}")
        w_col1, w_col2 = st.columns(2)
        w_col1.metric("Total Invested", f"₹{invested_amount:,.0f}")
        w_col2.metric("Est. Wealth Gained", f"₹{future_value - invested_amount:,.0f}")
        st.progress(min(invested_amount / future_value, 1.0), text="Investment vs Growth Ratio")

# --- 7. STOCK ANALYSIS ENGINE ---
else:
    user_ticker = st.session_state.current_view
    
    if st.button("⬅️ Back to Home Search"):
        st.session_state.current_view = "HOME"
        st.rerun()
        
    @st.cache_data(ttl=300)
    def get_data(symbol):
        try: return yf.Ticker(symbol).history(period="1y")
        except: return None

    @st.cache_data(ttl=3600)
    def get_info(symbol):
        try: return yf.Ticker(symbol).info
        except: return {}

    data = get_data(user_ticker)
    info = get_info(user_ticker)
    display_name = TOP_STOCKS.get(user_ticker, user_ticker.replace('.NS', ''))

    if data is not None and not data.empty:
        curr_price, prev_price = data['Close'].iloc[-1], data['Close'].iloc[-2]
        change, pct = curr_price - prev_price, ((curr_price - prev_price) / prev_price) * 100

        st.markdown(f"## {display_name}")
        st.metric("Last Traded Price", f"₹{curr_price:.2f}", f"{change:.2f} ({pct:.2f}%)")

        data['SMA50'] = data['Close'].rolling(50).mean()
        data['SMA200'] = data['Close'].rolling(200).mean()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Technical Chart", "📋 Fundamental Audit", "📰 Live News", "💎 AI Quant Report"])

        with tab1:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Price', increasing_line_color='#26A69A', decreasing_line_color='#EF5350'))
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='orange', width=1.5), name='50-Day SMA'))
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], line=dict(color='dodgerblue', width=1.5), name='200-Day SMA'))
            fig.update_layout(template="plotly_dark", margin=dict(t=10, b=10, l=10, r=10), height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            if info:
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("P/E Ratio", round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A")
                f2.metric("ROE", f"{round(info.get('returnOnEquity', 0)*100, 2)}%" if info.get('returnOnEquity') else "N/A")
                f3.metric("Book Value", f"₹{round(info.get('bookValue', 0), 2)}" if info.get('bookValue') else "N/A")
                f4.metric("Debt/Eq", round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else "N/A")
                st.write("---")
                st.caption(f"**Business Overview:** *{info.get('longBusinessSummary', 'N/A')[:400]}...*")
            else: st.warning("Fundamental data currently unavailable.")

        with tab3:
            live_news = get_live_news(display_name)
            if live_news:
                for n in live_news:
                    st.markdown(f"🔹 **[{n['title']}]({n['link']})**")
                    st.caption(f"🗞️ Source: {n['source']} | 🕒 {n['date']}")
                    st.divider()
            else: st.info("No recent news found.")

        # --- CONTEXTUAL PREMIUM QUANT REPORT ---
        with tab4:
            st.markdown("### 🧠 Automated Quant Analyst")
            st.info("Unlock algorithmic analysis, valuation checks, and future movement insights.")
            
            col_a, col_b = st.columns([1, 2])
            with col_a:
                entered_code = st.text_input("🔑 Enter Premium Access Code:", type="password")
            
            if entered_code:
                if entered_code == "AMANPRO":
                    st.success("🔓 **Access Granted: Dixit Capital Quant Algorithm Running...**")
                    
                    # RSI Calculation
                    delta = data['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    current_rsi = (100 - (100 / (1 + rs))).iloc[-1]
                    
                    pe = info.get('trailingPE', 0)
                    roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
                    debt = info.get('debtToEquity', 0)
                    
                    score = 0
                    val_msg, tech_msg = "", ""
                    
                    if pe > 0 and pe < 20:
                        score += 2; val_msg = "✅ **Undervalued:** Trading at a discount compared to market averages."
                    elif pe >= 20 and pe < 40:
                        score += 1; val_msg = "⚖️ **Fairly Valued:** Priced reasonably for its growth expectations."
                    else:
                        score -= 1; val_msg = "⚠️ **Overpriced:** Trading at a high premium. High expectations are already baked into the price."

                    if current_rsi < 35:
                        score += 2; tech_msg = "📈 **Oversold:** The stock has seen heavy selling and might reverse upwards soon."
                    elif current_rsi > 65:
                        score -= 1; tech_msg = "📉 **Overbought:** The stock is running too hot. A short-term correction is highly likely."
                    else:
                        score += 1; tech_msg = "⚖️ **Neutral Momentum:** The stock is trading in a stable zone without extreme volatility."

                    st.markdown("---")
                    if score >= 3:
                        st.success("### Verdict: STRONG BUY (Accumulate)")
                        st.write("This asset shows strong fundamental valuation combined with favorable technical momentum. Good for immediate accumulation.")
                    elif score == 2:
                        st.info("### Verdict: HOLD / SIP")
                        st.write("A decent quality asset but current price points suggest staggered buying (SIP) rather than lumpsum investment.")
                    else:
                        st.warning("### Verdict: CAUTION / SELL")
                        st.write("Risk-reward ratio is currently unfavorable. It is either technically overbought or fundamentally overpriced. Wait for a correction.")
                    
                    st.markdown("### 📊 Detailed Justification")
                    st.markdown(val_msg)
                    st.markdown(tech_msg)
                    if roe > 15: st.markdown(f"✅ **Strong Management:** Generating excellent Return on Equity ({roe:.2f}%).")
                    if debt < 50: st.markdown("✅ **Safe Balance Sheet:** Low debt-to-equity ratio makes it fundamentally strong.")
                    st.caption("Disclaimer: This algorithmic report is based on current technical and fundamental data. Consult a registered financial advisor before trading.")
                else:
                    st.error("❌ Invalid Access Code. Please check the spelling or upgrade to Premium.")

    else:
        st.error("⚠️ Invalid Stock Symbol. Please verify the ticker.")
