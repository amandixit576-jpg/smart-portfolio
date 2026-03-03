import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd

# --- 1. PAGE SETUP & MEMORY ---
st.set_page_config(page_title="Dixit Investment Group | Screener", layout="wide", initial_sidebar_state="collapsed")

if 'current_view' not in st.session_state: st.session_state.current_view = "HOME"
if 'portfolio' not in st.session_state: st.session_state.portfolio = pd.DataFrame(columns=["Ticker", "Buy Price", "Quantity"])

# --- PREMIUM CSS (Fixing Button Wrapping & Layouts) ---
st.markdown("""
    <style>
    /* Center aligning main content */
    .block-container { padding-top: 0rem; padding-bottom: 2rem; max-width: 1200px; }
    
    /* FIX: Prevent Button Text Wrapping (Stops RELIANC E) */
    div[data-testid="stButton"] button {
        white-space: nowrap !important;
        border-radius: 8px !important;
        padding-left: 5px !important;
        padding-right: 5px !important;
    }
    div[data-testid="stButton"] button p {
        font-size: 14px !important;
    }

    /* Screener Headers */
    .main-title { text-align: center; color: #1E88E5; font-size: 3.5rem; font-weight: 800; margin-bottom: 0px; font-family: sans-serif;}
    .sub-title { text-align: center; color: #555; font-size: 1.2rem; font-weight: 600; margin-top: 5px; margin-bottom: 30px; }
    
    a { text-decoration: none !important; color: inherit !important; }
    th { text-align: left !important; background-color: rgba(150, 150, 150, 0.1); }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS FOR INDIAN FORMATTING ---
def format_inr(number):
    """Formats a number using the Indian numbering system (e.g., 1,00,000.00)"""
    if pd.isna(number) or number is None: 
        return "N/A"
    try:
        is_negative = number < 0
        number = abs(number)
        s, *d = str(round(float(number), 2)).partition(".")
        r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        formatted_num = "".join([r] + d) if r else s
        return f"-{formatted_num}" if is_negative else formatted_num
    except: 
        return str(number)

def format_large_number(number):
    """Smartly formats large numbers to Hundreds, Thousands, or Crores."""
    if pd.isna(number) or number is None:
        return "N/A"
    try:
        num = float(number)
        if num >= 10000000:  # Crores
            return f"{format_inr(round(num / 10000000, 2))} Cr"
        elif num >= 100000:  # Lakhs
            return f"{format_inr(round(num / 100000, 2))} L"
        else:
            return format_inr(num)
    except:
        return str(number)

def format_df_to_crores(df):
    """Converts dataframe values to Crores for statements."""
    if df is None or df.empty: return df
    formatted = df.copy()
    for col in formatted.columns:
        formatted[col] = pd.to_numeric(formatted[col], errors='coerce')
        formatted[col] = formatted[col].apply(lambda x: f"{format_inr(round(x / 10000000, 2))}" if pd.notna(x) else "N/A")
    formatted.columns = [str(c).split(' ')[0] for c in formatted.columns]
    return formatted

# --- 2. TOP MARKET BAR (Native Stable Streamlit) ---
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

st.markdown("<br>", unsafe_allow_html=True) # Little breathing room
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
if st.sidebar.button("⚖️ Peer Comparison", use_container_width=True): st.session_state.current_view = "COMPARE"; st.rerun()
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
        i1, i2 = yf.Ticker(t1).info, yf.Ticker(t2).info
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

# --- 5. HOME PAGE (Screener + Finology UI) ---
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
    
    ht1, ht2 = st.tabs(["💰 SIP Wealth Calculator", "💼 My Virtual Portfolio"])
    with ht1:
        calc_col1, calc_col2 = st.columns([1, 2])
        with calc_col1:
            sip_amount = st.number_input("Monthly SIP (₹)", min_value=500, value=5000, step=500)
            sip_years = st.slider("Investment Period (Years)", 1, 30, 10)
            sip_rate = st.slider("Expected Annual Return (%)", 5, 25, 12)
        with calc_col2:
            monthly_rate = sip_rate / 12 / 100
            months = sip_years * 12
            invested = sip_amount * months
            fv = sip_amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
            st.success(f"### Estimated Wealth: ₹{format_inr(round(fv, 0))}")
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
            df_port["P&L (₹)"] = df_port["Current Value"] - df_port["Total Invested"]
            
            # Format Portfolio DF
            display_df = df_port.copy()
            for col in ["Buy Price", "Live Price", "Total Invested", "Current Value", "P&L (₹)"]:
                display_df[col] = display_df[col].apply(lambda x: format_inr(round(x, 2)))
                
            st.dataframe(display_df, use_container_width=True)

# --- 6. STOCK ANALYSIS ENGINE (Expanded Ratios) ---
else:
    user_ticker = st.session_state.current_view
    
    if st.button("⬅️ Back to Home Search"): st.session_state.current_view = "HOME"; st.rerun()
    st.write("---")
    
    t_obj = yf.Ticker(user_ticker)
    data = t_obj.history(period="1y")
    info = t_obj.info
    display_name = info.get('shortName', user_ticker.replace('.NS', ''))

    if data is not None and not data.empty:
        curr_price, prev_price = data['Close'].iloc[-1], data['Close'].iloc[-2]
        
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"<h1 style='color: #1E293B;'>{display_name}</h1>", unsafe_allow_html=True)
        c2.metric("Current Price", f"₹{format_inr(round(curr_price, 2))}", f"{(curr_price - prev_price):.2f} ({((curr_price - prev_price)/prev_price)*100:.2f}%)")

        data['SMA50'] = data['Close'].rolling(50).mean()
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Price Chart", "📋 Pro Ratios & Whales", "📑 Financials (In Cr)", "🏢 Corp Actions", "📰 Live News", "💎 AI Quant", "📥 Export"])

        with tab1:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='orange'), name='50 SMA'))
            fig.update_layout(template="plotly_white", margin=dict(t=10, b=10, l=10, r=10), height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### 📈 Comprehensive Financial Metrics")
            
            # Expanded Ratios
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
            r8.metric("ROCE", f"{round(info.get('returnOnCapitalEmployed', 0)*100, 2)}%" if info.get('returnOnCapitalEmployed') else "N/A") # Added ROCE if available
            
            st.write("")
            r9, r10, r11, r12 = st.columns(4)
            r9.metric("ROE", f"{round(info.get('returnOnEquity', 0)*100, 2)}%" if info.get('returnOnEquity') else "N/A")
            r10.metric("Face Value", f"₹{info.get('regularMarketPrice', 'N/A')}") # Approximation
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
            entered_code = st.text_input("🔑 Enter Premium Access Code:", type="password")
            if entered_code == "AMANPRO":
                st.success("🔓 Algorithm Running...")
                pe = info.get('trailingPE', 0)
                if pe > 0 and pe < 20: st.success("✅ **Verdict: STRONG BUY** (Undervalued: Trading at discount).")
                elif pe >= 20 and pe < 40: st.info("⚖️ **Verdict: HOLD / SIP** (Fairly Valued: Normal pricing).")
                else: st.warning("⚠️ **Verdict: CAUTION** (Overpriced: High premium).")
            elif entered_code: st.error("❌ Invalid Code.")

        with tab7:
            st.markdown("### 📥 Download Institutional Report")
            report_df = pd.DataFrame({"Metric": ["Company", "Price", "P/E", "ROE", "Debt/Eq"], "Value": [display_name, curr_price, info.get('trailingPE'), info.get('returnOnEquity'), info.get('debtToEquity')]})
            st.download_button(label="Download CSV", data=report_df.to_csv(index=False).encode('utf-8'), file_name=f"{user_ticker}_Report.csv", mime="text/csv", type="primary")

    else: st.error("⚠️ Invalid Asset Symbol. Try searching something like 'TCS'.")
