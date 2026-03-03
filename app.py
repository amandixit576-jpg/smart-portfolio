import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd

# --- 1. PAGE SETUP & MEMORY ---
st.set_page_config(page_title="Dixit Investment Group | Screener", layout="wide", initial_sidebar_state="collapsed")

if 'current_view' not in st.session_state: st.session_state.current_view = "HOME"
if 'portfolio' not in st.session_state: st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Price", "Quantity"])

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    .block-container { padding-top: 0rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="stButton"] button {
        white-space: nowrap !important;
        border-radius: 8px !important;
        padding-left: 5px !important;
        padding-right: 5px !important;
    }
    div[data-testid="stButton"] button p { font-size: 14px !important; }
    .main-title { text-align: center; color: #1E88E5; font-size: 3.5rem; font-weight: 800; margin-bottom: 0px; font-family: sans-serif;}
    .sub-title { text-align: center; color: #555; font-size: 1.2rem; font-weight: 600; margin-top: 5px; margin-bottom: 30px; }
    a { text-decoration: none !important; color: inherit !important; }
    th { text-align: left !important; background-color: rgba(150, 150, 150, 0.1); }
    /* Thematic Basket Cards */
    .basket-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background: #f8f9fa; text-align: center; margin-bottom: 10px; height: 130px; }
    .basket-title { color: #1E88E5; font-weight: 700; font-size: 1.1rem; }
    .basket-card p { font-size: 0.9rem; color: #666; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def format_inr(number):
    if pd.isna(number) or number is None: return "N/A"
    try:
        is_negative = number < 0
        number = abs(number)
        s, *d = str(round(float(number), 2)).partition(".")
        r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        formatted_num = "".join([r] + d) if r else s
        return f"-{formatted_num}" if is_negative else formatted_num
    except: return str(number)

def format_large_number(number):
    if pd.isna(number) or number is None: return "N/A"
    try:
        num = float(number)
        if num >= 10000000: return f"{format_inr(round(num / 10000000, 2))} Cr"
        elif num >= 100000: return f"{format_inr(round(num / 100000, 2))} L"
        else: return format_inr(num)
    except: return str(number)

def format_df_to_crores(df):
    if df is None or df.empty: return df
    formatted = df.copy()
    for col in formatted.columns:
        formatted[col] = pd.to_numeric(formatted[col], errors='coerce')
        formatted[col] = formatted[col].apply(lambda x: f"{format_inr(round(x / 10000000, 2))}" if pd.notna(x) else "N/A")
    formatted.columns = [str(c).split(' ')[0] for c in formatted.columns]
    return formatted

# Anti-Crash function for Yahoo Finance data
@st.cache_data(ttl=3600)
def fetch_safe_info(ticker_symbol):
    try:
        return yf.Ticker(ticker_symbol).info
    except Exception:
        return {} 

# --- 2. TOP MARKET BAR ---
@st.cache_data(ttl=300)
def get_index_data(ticker):
    try: return yf.Ticker(ticker).history(period="2d")
    except: return None

nifty, sensex, banknifty = get_index_data("^NSEI"), get_index_data("^BSESN"), get_index_data("^NSEBANK")

def display_index(col, name, data):
    if data is not None and len(data) >= 2:
        curr, prev = data['Close'].iloc[-1], data['Close'].iloc[-2]
        chg, pct = curr - prev, ((curr - prev)/prev)*100
        color = "#16A34A" if chg >= 0 else "#DC2626"
        sign = "+" if chg >= 0 else ""
        col.markdown(f"**{name}**: ₹{format_inr(round(curr, 2))} <span style='color:{color}; font-weight:bold;'>({sign}{pct:.2f}%)</span>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) 
top1, top2, top3, top4 = st.columns([1, 2, 2, 2])
display_index(top2, "SENSEX", sensex)
display_index(top3, "NIFTY 50", nifty)
display_index(top4, "BANKNIFTY", banknifty)
st.write("---")

# --- 3. LEAD GENERATION & SIDEBAR ---
TOP_STOCKS = {"RELIANCE.NS": "Reliance", "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC Bank", "INFY.NS": "Infosys", "ZOMATO.NS": "Zomato", "ITC.NS": "ITC", "SBIN.NS": "SBI"}

@st.dialog("👑 Unlock Premium Access")
def premium_signup():
    st.markdown("Join **Dixit Investment Group** for algorithmic access & fundamental models.")
    name, city = st.text_input("Full Name"), st.text_input("City")
    if name and city:
        st.link_button("📲 Chat to get Code", f"https://wa.me/917052360459?text={urllib.parse.quote(f'Hello Dixit Investment Group! I want to purchase the Premium Access Code. Name: {name}, City: {city}')}", type="primary", use_container_width=True)
    else:
        st.button("📲 Chat to get Code", type="primary", disabled=True, use_container_width=True)

st.sidebar.markdown("<h3 style='color:#1E88E5;'>DIG Menu</h3>", unsafe_allow_html=True)
if st.sidebar.button("🏠 Home Dashboard", use_container_width=True): st.session_state.current_view = "HOME"; st.rerun()
if st.sidebar.button("🧺 Theme Baskets", use_container_width=True): st.session_state.current_view = "BASKETS"; st.rerun()
if st.sidebar.button("⚖️ Peer Comparison", use_container_width=True): st.session_state.current_view = "COMPARE"; st.rerun()
if st.sidebar.button("📈 Mutual Funds", use_container_width=True): st.session_state.current_view = "MUTUAL_FUNDS"; st.rerun()
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("👑 Upgrade to Premium", use_container_width=True): premium_signup()

@st.cache_data(ttl=1800)
def get_live_news(company_name):
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(f'{company_name} share stock news India')}&hl=en-IN&gl=IN&ceid=IN:en"
        root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read())
        return [{'title': i.find('title').text.rsplit(' - ', 1)[0] if ' - ' in i.find('title').text else i.find('title').text, 'link': i.find('link').text, 'date': i.find('pubDate').text[5:16]} for i in root.findall('.//item')[:4]]
    except: return []

# --- 4. PEER COMPARISON VIEW ---
if st.session_state.current_view == "COMPARE":
    st.markdown("<h2 style='color:#1E88E5;'>⚖️ Peer-to-Peer Asset Comparison</h2>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Home Engine"): st.session_state.current_view = "HOME"; st.rerun()
    st.write("---")
    
    c1, c2 = st.columns(2)
    with c1: t1 = st.selectbox("Select Asset 1:", list(TOP_STOCKS.keys()), index=0)
    with c2: t2 = st.selectbox("Select Asset 2:", list(TOP_STOCKS.keys()), index=2)
    
    if st.button("Run Comparison 🚀", type="primary"):
        i1, i2 = fetch_safe_info(t1), fetch_safe_info(t2)
        comp_data = {
            "Metric": ["Price (₹)", "P/E Ratio", "P/B Ratio", "ROE (%)", "Debt to Equity", "Market Cap"],
            TOP_STOCKS[t1]: [
                format_inr(i1.get('currentPrice')), 
                round(i1.get('trailingPE', 0), 2) if i1.get('trailingPE') else 'N/A', 
                round(i1.get('priceToBook', 0), 2) if i1.get('priceToBook') else 'N/A',
                round(i1.get('returnOnEquity', 0)*100, 2) if i1.get('returnOnEquity') else 'N/A', 
                round(i1.get('debtToEquity', 0), 2) if i1.get('debtToEquity') else 'N/A', 
                f"₹{format_large_number(i1.get('marketCap'))}"
            ],
            TOP_STOCKS[t2]: [
                format_inr(i2.get('currentPrice')), 
                round(i2.get('trailingPE', 0), 2) if i2.get('trailingPE') else 'N/A', 
                round(i2.get('priceToBook', 0), 2) if i2.get('priceToBook') else 'N/A',
                round(i2.get('returnOnEquity', 0)*100, 2) if i2.get('returnOnEquity') else 'N/A', 
                round(i2.get('debtToEquity', 0), 2) if i2.get('debtToEquity') else 'N/A', 
                f"₹{format_large_number(i2.get('marketCap'))}"
            ]
        }
        st.table(pd.DataFrame(comp_data).set_index("Metric"))

# --- 4.5 MUTUAL FUND TRACKER ---
elif st.session_state.current_view == "MUTUAL_FUNDS":
    st.markdown("<h2 style='color:#1E88E5;'>📈 Mutual Fund Tracker</h2>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Home Engine"): st.session_state.current_view = "HOME"; st.rerun()
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
            mf_data = yf.Ticker(mf_ticker)
            try:
                hist = mf_data.history(period="1y")
            except:
                hist = pd.DataFrame()

            if not hist.empty:
                current_nav = hist['Close'].iloc[-1]
                prev_nav = hist['Close'].iloc[-2]

                c1, c2 = st.columns([3, 1])
                c1.markdown(f"### {selected_mf}")
                c2.metric("Current NAV", f"₹{format_inr(round(current_nav, 2))}", f"{(current_nav - prev_nav):.2f} ({((current_nav - prev_nav)/prev_nav)*100:.2f}%)")

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', fill='tozeroy', line=dict(color='#1E88E5'), name='NAV'))
                fig.update_layout(template="plotly_white", margin=dict(t=10, b=10, l=10, r=10), height=400, yaxis_title="Net Asset Value (₹)")
                st.plotly_chart(fig, use_container_width=True)

                st.info("💡 **Pro Tip:** Mutual Fund NAVs are calculated only once a day at the end of the trading session (usually updated around 9 PM - 11 PM IST).")
            else:
                st.error("⚠️ Data not available for this Mutual Fund right now.")

# --- 4.6 THEME BASKETS (EXPANDED) ---
elif st.session_state.current_view == "BASKETS":
    st.markdown("<h2 style='color:#1E88E5;'>🧺 Ready-Made Theme Baskets</h2>", unsafe_allow_html=True)
    st.write("Invest in ideas, not just single stocks. Explore top sectors and themes driving the market.")
    if st.button("⬅️ Back to Home Engine"): st.session_state.current_view = "HOME"; st.rerun()
    st.write("---")

    # Row 1
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown('<div class="basket-card"><div class="basket-title">🌱 Green Energy & EV</div><p>Tata Power, Suzlon, Adani Green, Tata Motors</p></div>', unsafe_allow_html=True)
        if st.button("Analyze Green Energy", key="b_green", use_container_width=True):
            st.session_state.current_view = "TATAPOWER.NS"; st.rerun()
    with b2:
        st.markdown('<div class="basket-card"><div class="basket-title">👑 Monopoly Stocks</div><p>IRCTC, IEX, CDSL, HAL</p></div>', unsafe_allow_html=True)
        if st.button("Analyze Monopolies", key="b_mono", use_container_width=True):
            st.session_state.current_view = "IRCTC.NS"; st.rerun()
    with b3:
        st.markdown('<div class="basket-card"><div class="basket-title">🏦 PSU Banking</div><p>SBI, PNB, Bank of Baroda, Canara Bank</p></div>', unsafe_allow_html=True)
        if st.button("Analyze PSU Banks", key="b_psu", use_container_width=True):
            st.session_state.current_view = "SBIN.NS"; st.rerun()
            
    st.write("")
    
    # Row 2 (New Personalised Baskets)
    b4, b5, b6 = st.columns(3)
    with b4:
        st.markdown('<div class="basket-card"><div class="basket-title">🍃 Ethical & Cruelty-Free</div><p>Pure vegetarian FMCG & cruelty-free leaders (Tata Consumer, Dabur, Patanjali)</p></div>', unsafe_allow_html=True)
        if st.button("Analyze Ethical Basket", key="b_ethical", use_container_width=True):
            st.session_state.current_view = "TATACONSUM.NS"; st.rerun()
    with b5:
        st.markdown('<div class="basket-card"><div class="basket-title">💻 Tech & Innovation</div><p>IT Giants shaping the future (TCS, HCLTech, Infosys)</p></div>', unsafe_allow_html=True)
        if st.button("Analyze Tech Basket", key="b_tech", use_container_width=True):
            st.session_state.current_view = "HCLTECH.NS"; st.rerun()
    with b6:
        st.markdown('<div class="basket-card"><div class="basket-title">💰 Dividend Kings</div><p>Consistent high-yield cash generators (Coal India, ITC, Vedanta)</p></div>', unsafe_allow_html=True)
        if st.button("Analyze Dividend Kings", key="b_div", use_container_width=True):
            st.session_state.current_view = "COALINDIA.NS"; st.rerun()

# --- 5. HOME PAGE ---
elif st.session_state.current_view == "HOME":
    st.markdown('<h1 class="main-title">Dixit Investment Group</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">The Modern Stock Screener that helps you pick better stocks.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        man_t = st.text_input("Search", placeholder="🔍 Type a Company Name or NSE Symbol (e.g., ITC)", label_visibility="collapsed")
        if st.button("Search & Analyze", type="primary", use_container_width=True):
            if man_t:
                st.session_state.current_view = man_t.upper() if man_t.upper().endswith(".NS") else f"{man_t.upper()}.NS"
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_t1, col_t2 = st.columns([1, 4])
        col_t1.markdown("**What's Trending:**")
        with col_t2:
            t1, t2, t3, t4, t5 = st.columns(5)
            if t1.button("RELIANCE"): st.session_state.current_view = "RELIANCE.NS"; st.rerun()
            if t2.button("HDFCBANK"): st.session_state.current_view = "HDFCBANK.NS"; st.rerun()
            if t3.button("ZOMATO"): st.session_state.current_view = "ZOMATO.NS"; st.rerun()
            if t4.button("TCS"): st.session_state.current_view = "TCS.NS"; st.rerun()
            if t5.button("ITC"): st.session_state.current_view = "ITC.NS"; st.rerun()

    st.write("---")
    
    ht1, ht2 = st.tabs(["🎯 Goal-Based SIP Planner", "💼 My Virtual Portfolio & Taxes"])
    with ht1:
        st.markdown("### Plan for your next milestone")
        calc_col1, calc_col2 = st.columns([1, 2])
        with calc_col1:
            goal_type = st.selectbox("Select Financial Goal:", ["Custom Wealth Creation", "Himalayan Trek Fund (₹50k)", "Luxury Watch Fund (₹1.5L)", "Sibling's Setup Fund (₹10L)"])
            
            # Dynamic preset values based on goal
            default_sip = 5000
            default_years = 10
            if "Trek" in goal_type: default_sip, default_years = 4000, 1
            elif "Watch" in goal_type: default_sip, default_years = 6000, 2
            elif "Sibling" in goal_type: default_sip, default_years = 12000, 5
            
            sip_amount = st.number_input("Monthly SIP (₹)", min_value=500, value=default_sip, step=500)
            sip_years = st.slider("Investment Period (Years)", 1, 30, default_years)
            sip_rate = st.slider("Expected Annual Return (%)", 5, 25, 12)
        with calc_col2:
            monthly_rate = sip_rate / 12 / 100
            months = sip_years * 12
            invested = sip_amount * months
            fv = sip_amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
            st.success(f"### Estimated Goal Corpus: ₹{format_inr(round(fv, 0))}")
            w1, w2 = st.columns(2)
            w1.metric("Total Invested", f"₹{format_inr(round(invested, 0))}")
            w2.metric("Est. Wealth Gained", f"₹{format_inr(round(fv - invested, 0))}")

    with ht2:
        pc1, pc2, pc3, pc4 = st.columns(4)
        with pc1: p_tick = st.selectbox("Asset", list(TOP_STOCKS.keys()))
        with pc2: p_qty = st.number_input("Quantity", min_value=1, value=10)
        with pc3: p_buy = st.number_input("Buy Price (₹)", min_value=1.0, value=100.0)
        with pc4: 
            st.write("")
            if st.button("➕ Add Trade", use_container_width=True):
                st.session_state.portfolio = pd.concat([st.session_state.portfolio, pd.DataFrame({"Ticker": [p_tick], "Buy Price": [p_buy], "Quantity": [p_qty]})], ignore_index=True)
                st.success("Trade Added!")
        
        if not st.session_state.portfolio.empty:
            df_port = st.session_state.portfolio.copy()
            df_port["Live Price"] = [yf.Ticker(t).history(period="1d")['Close'].iloc[-1] if not yf.Ticker(t).history(period="1d").empty else 0 for t in df_port["Ticker"]]
            df_port["Total Invested"] = df_port["Buy Price"] * df_port["Quantity"]
            df_port["Current Value"] = df_port["Live Price"] * df_port["Quantity"]
            df_port["Gross P&L (₹)"] = df_port["Current Value"] - df_port["Total Invested"]
            
            df_port["Est. STCG Tax (20%)"] = df_port["Gross P&L (₹)"].apply(lambda x: x * 0.20 if x > 0 else 0)
            df_port["Net Post-Tax P&L"] = df_port["Gross P&L (₹)"] - df_port["Est. STCG Tax (20%)"]
            
            display_df = df_port.copy()
            for col in ["Buy Price", "Live Price", "Total Invested", "Current Value", "Gross P&L (₹)", "Est. STCG Tax (20%)", "Net Post-Tax P&L"]:
                display_df[col] = display_df[col].apply(lambda x: format_inr(round(x, 2)))
                
            st.dataframe(display_df, use_container_width=True)
            st.caption("ℹ️ *Tax estimator assumes Short-Term Capital Gains (STCG) at a flat 20% rate on profitable trades.*")

# --- 6. STOCK ANALYSIS ENGINE ---
else:
    user_ticker = st.session_state.current_view
    
    if st.button("⬅️ Back to Home Search"): st.session_state.current_view = "HOME"; st.rerun()
    st.write("---")
    
    t_obj = yf.Ticker(user_ticker)
    
    try:
        data = t_obj.history(period="1y")
    except:
        data = pd.DataFrame()
        
    info = fetch_safe_info(user_ticker)
    display_name = info.get('shortName', user_ticker.replace('.NS', ''))

    if data is not None and not data.empty:
        curr_price, prev_price = data['Close'].iloc[-1], data['Close'].iloc[-2]
        
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"<h1 style='color: #1E293B;'>{display_name}</h1>", unsafe_allow_html=True)
        c2.metric("Current Price", f"₹{format_inr(round(curr_price, 2))}", f"{(curr_price - prev_price):.2f} ({((curr_price - prev_price)/prev_price)*100:.2f}%)")

        data['SMA50'] = data['Close'].rolling(50).mean()
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📊 Price Chart", "📋 Pro Ratios & Whales", "📑 Financials (In Cr)", "🏢 Corp Actions", "📰 Live News", "💎 AI Quant", "📥 Export Mode", "🧑‍💼 CA's Audit Desk"])

        with tab1:
            st.markdown("### 📊 Advanced Technical Chart")
            data['20SMA'] = data['Close'].rolling(20).mean()
            data['Upper_BB'] = data['20SMA'] + 2 * data['Close'].rolling(20).std()
            data['Lower_BB'] = data['20SMA'] - 2 * data['Close'].rolling(20).std()
            
            delta = data['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            data['RSI'] = 100 - (100 / (1 + (ema_up / ema_down)))
            
            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            data['MACD'] = exp1 - exp2
            data['Signal Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

            indicators = st.multiselect("Overlay Technical Indicators:", ["50 SMA", "200 SMA", "Bollinger Bands", "RSI (14)", "MACD"], default=["50 SMA"])

            has_rsi = "RSI (14)" in indicators
            has_macd = "MACD" in indicators
            
            rows = 1 + int(has_rsi) + int(has_macd)
            row_heights = [0.6] + [0.2] * (rows - 1) if rows > 1 else [1]
            
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=row_heights)

            fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
            
            if "50 SMA" in indicators:
                fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='orange', width=1.5), name='50 SMA'), row=1, col=1)
            if "200 SMA" in indicators:
                data['SMA200'] = data['Close'].rolling(200).mean()
                fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], line=dict(color='blue', width=1.5), name='200 SMA'), row=1, col=1)
            if "Bollinger Bands" in indicators:
                fig.add_trace(go.Scatter(x=data.index, y=data['Upper_BB'], line=dict(color='gray', dash='dash'), name='Upper BB'), row=1, col=1)
                fig.add_trace(go.Scatter(x=data.index, y=data['Lower_BB'], line=dict(color='gray', dash='dash'), fill='tonexty', fillcolor='rgba(128,128,128,0.1)', name='Lower BB'), row=1, col=1)

            current_row = 2
            if has_rsi:
                fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='purple', width=1.5), name='RSI'), row=current_row, col=1)
                fig.add_hline(y=70, line_dash="dot", line_color="red", row=current_row, col=1) 
                fig.add_hline(y=30, line_dash="dot", line_color="green", row=current_row, col=1) 
                fig.update_yaxes(title_text="RSI", row=current_row, col=1, range=[0, 100])
                current_row += 1

            if has_macd:
                fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], line=dict(color='blue', width=1.5), name='MACD'), row=current_row, col=1)
                fig.add_trace(go.Scatter(x=data.index, y=data['Signal Line'], line=dict(color='orange', width=1.5), name='Signal'), row=current_row, col=1)
                colors = ['green' if val >= 0 else 'red' for val in (data['MACD'] - data['Signal Line'])]
                fig.add_trace(go.Bar(x=data.index, y=(data['MACD'] - data['Signal Line']), marker_color=colors, name='Histogram'), row=current_row, col=1)
                fig.update_yaxes(title_text="MACD", row=current_row, col=1)

            fig.update_layout(template="plotly_white", margin=dict(t=10, b=10, l=10, r=10), height=700 if rows > 1 else 500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### 📈 Comprehensive Financial Metrics")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Market Cap", f"₹{format_large_number(info.get('marketCap'))}")
            r2.metric("Current Price", f"₹{format_inr(info.get('currentPrice', 0))}")
            r3.metric("52 Week High", f"₹{format_inr(info.get('fiftyTwoWeekHigh', 0))}")
            r4.metric("52 Week Low", f"₹{format_inr(info.get('fiftyTwoWeekLow', 0))}")
            
            st.write("")
            r5, r6, r7, r8 = st.columns(4)
            r5.metric("Stock P/E", round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A")
            r6.metric("Book Value", f"₹{format_inr(round(info.get('bookValue', 0), 2))}" if info.get('bookValue') else "N/A")
            r7.metric("Dividend Yield", f"{round(info.get('dividendYield', 0)*100, 2)}%" if info.get('dividendYield') else "0.00%")
            r8.metric("ROCE", f"{round(info.get('returnOnCapitalEmployed', 0)*100, 2)}%" if info.get('returnOnCapitalEmployed') else "N/A") 
            
            st.write("")
            r9, r10, r11, r12 = st.columns(4)
            r9.metric("ROE", f"{round(info.get('returnOnEquity', 0)*100, 2)}%" if info.get('returnOnEquity') else "N/A")
            r10.metric("Face Value", f"₹{info.get('regularMarketPrice', 'N/A')}") 
            r11.metric("Debt to Equity", round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else "N/A")
            r12.metric("Price to Book", round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else "N/A")
            
            st.write("---")
            st.markdown("### 🐋 Shareholding Pattern")
            insider = round(info.get('heldPercentInsiders', 0) * 100, 2)
            inst = round(info.get('heldPercentInstitutions', 0) * 100, 2)
            st.write(f"**Promoters:** {insider}% | **Institutions (FII/DII):** {inst}% | **Public:** {round(100 - insider - inst, 2)}%")

        with tab3:
            st.markdown("### 📑 Annual Financial Statements (In Crores)")
            st.caption("Figures are represented in ₹ Crores (Cr).")
            stmt1, stmt2 = st.tabs(["Income Statement", "Balance Sheet"])
            with stmt1:
                try:
                    fin_df = t_obj.financials
                    if not fin_df.empty: st.dataframe(format_df_to_crores(fin_df.dropna(how='all')), use_container_width=True)
                    else: st.warning("Income Statement data not available.")
                except: st.warning("Error fetching Income Statement.")
            with stmt2:
                try:
                    bs_df = t_obj.balance_sheet
                    if not bs_df.empty: st.dataframe(format_df_to_crores(bs_df.dropna(how='all')), use_container_width=True)
                    else: st.warning("Balance Sheet data not available.")
                except: st.warning("Error fetching Balance Sheet.")

        with tab4:
            st.markdown("### 📅 Recent Dividends & Corporate Actions")
            try:
                divs = t_obj.dividends.tail(5)
                if not divs.empty: st.write(divs)
                else: st.info("No recent dividend data found.")
            except: st.warning("Corporate action data unavailable.")

        with tab5:
            st.markdown("### 📰 Live Market News")
            live_news = get_live_news(display_name)
            if live_news:
                for n in live_news:
                    st.markdown(f"🔹 **[{n['title']}]({n['link']})**")
                    st.caption(f"🕒 {n['date']}")
                    st.divider()
            else: st.info("No recent news found.")

        with tab6:
            st.markdown("### 💎 AI Quant & Market Screener")
            entered_code = st.text_input("🔑 Enter Premium Access Code:", type="password")
            
            if entered_code == "AMANPRO":
                st.success("🔓 Premium Access Granted! Running Live Quant Models...")
                
                # --- LIVE MOMENTUM SCANNER ---
                st.write("#### 🎯 Today's High-Probability Breakout Setups")
                st.caption("Disclaimer: These algorithms identify strong technical momentum (RSI > 60 & Price > 50 SMA). Always manage your risk.")
                
                if st.button("🔍 Scan Top Market Assets", type="primary"):
                    with st.spinner("Scanning real-time market data... This takes a few seconds."):
                        top_picks = []
                        SCAN_LIST = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS", "SBIN.NS", "ZOMATO.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "LT.NS"]
                        
                        for sym in SCAN_LIST:
                            try:
                                scan_data = yf.Ticker(sym).history(period="3mo")
                                if len(scan_data) > 50:
                                    close_price = scan_data['Close'].iloc[-1]
                                    sma50 = scan_data['Close'].rolling(50).mean().iloc[-1]
                                    
                                    delta = scan_data['Close'].diff()
                                    up = delta.clip(lower=0)
                                    down = -1 * delta.clip(upper=0)
                                    ema_up = up.ewm(com=13, adjust=False).mean()
                                    ema_down = down.ewm(com=13, adjust=False).mean()
                                    rsi = 100 - (100 / (1 + (ema_up / ema_down)))
                                    current_rsi = rsi.iloc[-1]
                                    
                                    if close_price > sma50 and current_rsi >= 60:
                                        top_picks.append({
                                            "Asset": sym.replace('.NS', ''),
                                            "Price (₹)": round(close_price, 2),
                                            "RSI Strength": round(current_rsi, 2),
                                            "Signal": "Bullish 🚀"
                                        })
                            except:
                                pass
                                
                        if top_picks:
                            result_df = pd.DataFrame(top_picks).sort_values(by="RSI Strength", ascending=False)
                            st.table(result_df)
                        else:
                            st.info("No strong momentum setups found right now. The broader market might be consolidating or bearish.")
                
                st.write("---")
                
                # --- VALUATION MODEL ---
                st.write("#### 📊 Asset Valuation Model (P/E Based)")
                pe = info.get('trailingPE', 0)
                if pe > 0 and pe < 20: st.success("✅ **Verdict: STRONG BUY** (Undervalued: Trading at discount).")
                elif pe >= 20 and pe < 40: st.info("⚖️ **Verdict: HOLD / SIP** (Fairly Valued: Normal pricing).")
                else: st.warning("⚠️ **Verdict: CAUTION** (Overpriced: High premium).")
                
            elif entered_code: 
                st.error("❌ Invalid Code.")

        with tab7:
            st.markdown("### 📥 Creator Export Mode")
            st.write("Generate a branded institutional report for your portfolio or audience.")
            report_df = pd.DataFrame({
                "Metric": ["Company", "Price", "P/E", "ROE", "Debt/Eq", "Analysis By"], 
                "Value": [display_name, curr_price, info.get('trailingPE'), info.get('returnOnEquity'), info.get('debtToEquity'), "DIG Screener | 📸 @aman_creats"]
            })
            st.download_button(label="Download Branded CSV", data=report_df.to_csv(index=False).encode('utf-8'), file_name=f"{user_ticker}_DIG_Report.csv", mime="text/csv", type="primary")

        with tab8:
            st.markdown("### 🧑‍💼 CA's Audit Desk (Advanced Risk Lens)")
            st.caption("Forensic level checks to identify working capital stress and governance red flags.")
            
            ocf = info.get('operatingCashflow')
            net_inc = info.get('netIncomeToCommon')
            
            # Cash Flow Check
            st.markdown("#### 1. Earnings Quality Check")
            if pd.notna(ocf) and pd.notna(net_inc) and ocf != 0:
                if net_inc > 0 and ocf < 0:
                    st.error("🚩 **Red Flag:** The company is reporting paper profits, but actual Operating Cash Flow is NEGATIVE.")
                elif ocf > net_inc:
                    st.success("✅ **Clean:** Operating Cash Flow is higher than Net Income, indicating high-quality cash realization.")
                else:
                    st.info("⚖️ **Standard:** Cash flow aligns relatively closely with reported income.")
            else:
                st.info("Detailed cash flow audit data is currently unavailable on free tier.")
                
            # Current Ratio Check
            st.markdown("#### 2. Liquidity Audit")
            cr = info.get('currentRatio')
            if pd.notna(cr):
                if cr < 1: st.warning(f"⚠️ **Caution:** Current Ratio is {round(cr, 2)}. Short-term liabilities exceed short-term assets.")
                else: st.success(f"✅ **Healthy:** Current Ratio is {round(cr, 2)}, indicating sufficient short-term liquidity.")
            else:
                st.write("Data not available.")

    else: st.error("⚠️ Invalid Asset Symbol. Try searching something like 'TCS'.")
