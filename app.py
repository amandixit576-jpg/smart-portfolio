import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# --- 1. PAGE SETUP (Minimalist) ---
st.set_page_config(page_title="Pro Terminal | Dixit Capital", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    hr { margin-top: 1rem; margin-bottom: 2rem; border-color: #333; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LEAD GENERATION (WHATSAPP INTEGRATED) ---
@st.dialog("Request Premium Advisory")
def premium_signup():
    st.markdown("Join **Dixit Capital Premium** for institutional-grade audits, live alerts, and personalized portfolio management.")
    
    # Aapka WhatsApp number add kar diya gaya hai
    YOUR_WHATSAPP_NUMBER = "917052360459" 
    
    name = st.text_input("Full Name")
    city = st.text_input("City")
    
    st.write("---")
    
    if name and city:
        raw_message = f"Hello Dixit Capital.\n\nI am interested in the Premium Wealth Management services.\nName: {name}\nCity: {city}\n\nPlease share the details."
        encoded_message = urllib.parse.quote(raw_message)
        whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={encoded_message}"
        
        st.link_button("Continue to Secure Chat", whatsapp_url, type="primary", use_container_width=True)
    else:
        st.button("Continue to Secure Chat", type="primary", disabled=True, use_container_width=True)
        st.caption("Please enter your details to proceed.")

# --- 3. PREMIUM BRANDING (Luxury Feel) ---
st.markdown("<h1 style='text-align: center; font-weight: 300; letter-spacing: 3px; font-family: sans-serif;'>DIXIT CAPITAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 13px; letter-spacing: 2px;'>WEALTH MANAGEMENT & QUANTITATIVE ANALYSIS</p><hr>", unsafe_allow_html=True)

# --- 4. TOP STOCKS LIST ---
TOP_STOCKS = {
    "HOME": "Home Dashboard",
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

# --- 5. SIDEBAR & SEARCH ---
st.sidebar.markdown("### Main Menu")

if st.sidebar.button("Upgrade to Premium", use_container_width=True):
    premium_signup()

st.sidebar.markdown("---")
st.sidebar.markdown("**Equity Search**")

selected_ticker = st.sidebar.selectbox(
    "Select Asset:",
    options=list(TOP_STOCKS.keys()),
    format_func=lambda x: TOP_STOCKS[x] if x == "HOME" else f"{TOP_STOCKS[x]} ({x.replace('.NS', '')})"
)

manual_ticker = st.sidebar.text_input("Or enter NSE symbol (e.g., ITC):", "")

if manual_ticker:
    raw_ticker = manual_ticker.upper()
    user_ticker = raw_ticker if raw_ticker.endswith(".NS") else f"{raw_ticker}.NS"
else:
    user_ticker = selected_ticker

@st.cache_data(ttl=300)
def get_index_data(ticker):
    try: return yf.Ticker(ticker).history(period="2d")
    except: return None

# --- NEW LIVE NEWS ENGINE (Google News) ---
@st.cache_data(ttl=1800)
def get_live_news(company_name):
    try:
        query = urllib.parse.quote(f"{company_name} share stock news India")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        
        news_items = []
        for item in root.findall('.//item')[:4]: # Top 4 news dikhayega
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            
            # Formatting to make it clean
            if ' - ' in title:
                title, source = title.rsplit(' - ', 1)
            else:
                source = "Financial News"
                
            news_items.append({'title': title, 'link': link, 'source': source, 'date': pub_date[5:16]})
        return news_items
    except:
        return []

# --- 6. HOME DASHBOARD ---
if user_ticker == "HOME":
    st.markdown("<h3 style='text-align: center; font-weight: 400;'>Terminal Overview</h3>", unsafe_allow_html=True)
    
    nifty = get_index_data("^NSEI")
    banknifty = get_index_data("^NSEBANK")
    
    st.markdown("#### Market Pulse")
    col1, col2, col3 = st.columns(3)
    
    if nifty is not None and len(nifty) >= 2:
        n_curr, n_prev = nifty['Close'].iloc[-1], nifty['Close'].iloc[-2]
        col1.metric("NIFTY 50", f"{n_curr:.2f}", f"{n_curr - n_prev:.2f} ({(n_curr - n_prev)/n_prev * 100:.2f}%)")
    
    if banknifty is not None and len(banknifty) >= 2:
        bn_curr, bn_prev = banknifty['Close'].iloc[-1], banknifty['Close'].iloc[-2]
        col2.metric("NIFTY BANK", f"{bn_curr:.2f}", f"{bn_curr - bn_prev:.2f} ({(bn_curr - bn_prev)/bn_prev * 100:.2f}%)")
        
    col3.caption("Select an asset from the sidebar to begin technical and fundamental analysis.")
    st.divider()

    st.markdown("#### Wealth Projection")
    st.caption("Institutional-grade SIP modeling.")
    
    calc_col1, calc_col2 = st.columns([1, 2])
    with calc_col1:
        sip_amount = st.number_input("Monthly Investment (₹)", min_value=500, value=5000, step=500)
        sip_years = st.slider("Duration (Years)", 1, 30, 10)
        sip_rate = st.slider("Est. Annual Return (%)", 5, 25, 12)
    
    with calc_col2:
        monthly_rate = sip_rate / 12 / 100
        months = sip_years * 12
        invested_amount = sip_amount * months
        future_value = sip_amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
        wealth_gained = future_value - invested_amount
        
        st.markdown(f"### Projected Value: ₹{future_value:,.0f}")
        w_col1, w_col2 = st.columns(2)
        w_col1.metric("Capital Invested", f"₹{invested_amount:,.0f}")
        w_col2.metric("Estimated Returns", f"₹{wealth_gained:,.0f}")

# --- 7. STOCK ANALYSIS ENGINE ---
else:
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
        change = curr_price - prev_price
        pct = (change / prev_price) * 100

        st.markdown(f"## {display_name}")
        st.metric("Last Traded Price", f"₹{curr_price:.2f}", f"{change:.2f} ({pct:.2f}%)")

        # Premium Muted Chart
        data['SMA50'] = data['Close'].rolling(50).mean()
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
            name='Price',
            increasing_line_color='#2E7D32', decreasing_line_color='#C62828'
        ))
        
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='#BDBDBD', width=1.5), name='50-Day SMA'))
        
        fig.update_layout(
            template="plotly_dark", 
            margin=dict(t=10, b=10, l=10, r=10), 
            height=500, 
            xaxis_rangeslider_visible=False,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Fundamental Data"):
            if info:
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("P/E Ratio", round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A")
                f2.metric("ROE", f"{round(info.get('returnOnEquity', 0)*100, 2)}%" if info.get('returnOnEquity') else "N/A")
                f3.metric("Book Value", f"₹{round(info.get('bookValue', 0), 2)}" if info.get('bookValue') else "N/A")
                f4.metric("Debt/Equity", round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else "N/A")
                st.write("---")
                st.caption(f"{info.get('longBusinessSummary', 'N/A')[:400]}...")
            else:
                st.caption("Data unavailable.")

        with st.expander("Live Market News"):
            # Using the new Google News function here
            live_news = get_live_news(display_name)
            if live_news:
                for n in live_news:
                    st.markdown(f"**[{n['title']}]({n['link']})**")
                    st.caption(f"Source: {n['source']} | 🕒 {n['date']}")
                    st.write("")
            else:
                st.caption("No recent news found.")
    else:
        st.error("Invalid Stock Symbol. Please verify the ticker.")
