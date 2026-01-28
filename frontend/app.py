import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
import base64

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="InvestAI Terminal | Premium Equity Research",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling (Premium Glassmorphism) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
    }
    
    /* Glassmorphism containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        border-left: 4px solid #3d5afe;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
    }
    
    .recommendation-buy { color: #00e676; font-weight: 700; font-size: 28px; text-shadow: 0 0 10px rgba(0,230,118,0.3); }
    .recommendation-sell { color: #ff1744; font-weight: 700; font-size: 28px; text-shadow: 0 0 10px rgba(255,23,68,0.3); }
    .recommendation-hold { color: #ffea00; font-weight: 700; font-size: 28px; text-shadow: 0 0 10px rgba(255,234,0,0.3); }
    
    .stProgress > div > div > div > div {
        background-color: #3d5afe;
    }
    
    .social-post {
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding: 10px 0;
    }
    
    .sentiment-tag {
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 10px;
        text-transform: uppercase;
        font-weight: bold;
    }
    .tag-positive { background: rgba(0, 230, 118, 0.1); color: #00e676; border: 1px solid #00e676; }
    .tag-negative { background: rgba(255, 23, 68, 0.1); color: #ff1744; border: 1px solid #ff1744; }
    .tag-neutral { background: rgba(255, 255, 255, 0.1); color: #ccc; border: 1px solid #ccc; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.image("https://img.icons8.com/isometric/100/diamond.png", width=80)
st.sidebar.title("InvestAI 💎")
st.sidebar.caption("High-Fidelity Equity Intelligence")

ticker_input = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL").upper()
analyze_btn = st.sidebar.button("Run Intelligence Engine", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📄 Document Analysis")
uploaded_file = st.sidebar.file_uploader("Upload Financial Report (PDF)", type="pdf")
ocr_engine = st.sidebar.selectbox("OCR Engine", options=["Tesseract (Local)", "DeepSeek (AI)"])
engine_map = {"Tesseract (Local)": "tesseract", "DeepSeek (AI)": "deepseek"}

if uploaded_file and st.sidebar.button("Extract Data"):
    with st.sidebar:
        with st.spinner(f"Processing via {ocr_engine}..."):
            files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
            v_res = requests.post(
                f"{API_BASE_URL}/api/vision/extract", 
                files=files,
                params={"engine": engine_map[ocr_engine]}
            )
            if v_res.status_code == 200:
                st.session_state.ocr_data = v_res.json()["data"]
                st.success("Extracted successfully!")
            else:
                st.error("OCR Failed")

st.sidebar.markdown("---")
api_status = "Online"
try:
    if requests.get(f"{API_BASE_URL}/health", timeout=2).status_code != 200: api_status = "Error"
except: api_status = "Offline"
st.sidebar.caption(f"Backend Node: {api_status}")

# --- Helper Functions ---
def create_sparkline(val1, val2, label):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = val1,
        title = {'text': label, 'font': {'size': 14}},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#3d5afe"}}
    ))
    fig.update_layout(height=150, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    return fig

# --- Main App Logic ---

st.title(f"Market Analytics: {ticker_input}")

if analyze_btn or (ticker_input and "data" not in st.session_state):
    with st.spinner(f"Aggregating cross-service signals for {ticker_input}..."):
        try:
            response = requests.get(f"{API_BASE_URL}/api/memo/{ticker_input}")
            if response.status_code == 200:
                st.session_state.data = response.json()
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Link failed: {str(e)}")

if "data" in st.session_state:
    data = st.session_state.data
    market = data.get("market_data", {})
    indicators = market.get("indicators", {})
    social = data.get("social_context", {})
    news_context = data.get("news_context", {})
    rec = data.get("recommendation", "HOLD")

    # Header Stats
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'><div style='font-size:12px;color:#aaa'>PRICE</div><div style='font-size:24px;font-weight:600'>${market.get('price',0)}</div><div style='color:#00e676'>↑ {market.get('change_percent',0)}%</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><div style='font-size:12px;color:#aaa'>RSI (14)</div><div style='font-size:24px;font-weight:600'>{indicators.get('rsi',0)}</div><div style='color:#aaa;font-size:10px'>OVERSOLD < 30</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><div style='font-size:12px;color:#aaa'>MACD</div><div style='font-size:24px;font-weight:600'>{indicators.get('macd',0)}</div><div style='color:#aaa;font-size:10px'>TREND DIRECTION</div></div>", unsafe_allow_html=True)
    with c4:
        color_class = f"recommendation-{rec.lower()}"
        st.markdown(f"<div class='metric-card' style='border-left-color:var(--{rec.lower()})'><div style='font-size:12px;color:#aaa'>AI CONVICTION</div><div class='{color_class}'>{rec}</div></div>", unsafe_allow_html=True)
        if st.button("📈 Track Signal", type="secondary", use_container_width=True):
            payload = {
                "ticker": ticker_input,
                "entry_price": market.get("price", 0),
                "entry_date": datetime.now().strftime("%Y-%m-%d"),
                "recommendation": rec
            }
            try:
                p_res = requests.post(f"{API_BASE_URL}/api/portfolio/add", json=payload)
                if p_res.status_code == 200:
                    st.toast(f"Tracking {ticker_input} at ${payload['entry_price']}", icon="✅")
                else:
                    st.error("Tracking Failed")
            except:
                st.error("API Error")

    # Layout: Summary & Technicals / News & Social
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("💡 Intelligence Summary")
        st.write(data.get("analysis_summary"))
        
        # Dashboard Tabs
        tab_tech, tab_ocr, tab_portfolio = st.tabs(["📊 Technical Analysis", "📄 Document OCR Result", "💼 Portfolio Tracker"])
        
        with tab_tech:
            st.plotly_chart(create_sparkline(indicators.get('rsi', 0), 100, "Momentum Score"), use_container_width=True)
            st.markdown(f"**Company:** {market.get('company_name')} | **Sector:** {market.get('sector')}")
            st.info(market.get("summary"))
            
        with tab_ocr:
            if "ocr_data" in st.session_state:
                st.table(pd.DataFrame(st.session_state.ocr_data))
            else:
                st.write("Upload a PDF in the sidebar to populate this section with real financial data.")

        with tab_portfolio:
            try:
                port_res = requests.get(f"{API_BASE_URL}/api/portfolio/")
                if port_res.status_code == 200:
                    portfolio_items = port_res.json()
                    if portfolio_items:
                        df_p = pd.DataFrame(portfolio_items)
                        # Styling for P/L
                        def color_pl(val):
                            color = '#00e676' if val > 0 else '#ff1744'
                            return f'color: {color}; font-weight: bold'
                        
                        st.dataframe(
                            df_p[['ticker', 'recommendation', 'entry_price', 'current_price', 'p_l_percent']].style.applymap(color_pl, subset=['p_l_percent']),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("Your portfolio is currently empty. Track a signal to start monitoring performance.")
                else:
                    st.error("Failed to load portfolio")
            except Exception as e:
                st.error(f"Portfolio Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # News Tab
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📰 News Intelligence")
        if news_context:
            items = news_context.get("items", [])
            overall_sent = news_context.get("overall_sentiment", "neutral")
            
            st.markdown(f"**Overall Signal:** <span class='sentiment-tag tag-{overall_sent}'>{overall_sent}</span>", unsafe_allow_html=True)
            st.divider()
            
            for item in items:
                label = item.get("sentiment", {}).get("label", "neutral")
                st.markdown(f"""
                <div style='margin-bottom: 15px; border-left: 2px solid rgba(255,255,255,0.1); padding-left: 10px;'>
                    <a href='{item.get("link")}' target='_blank' style='text-decoration:none; color:#3d5afe; font-weight:600; font-size:14px;'>{item.get("title")}</a><br>
                    <span class='sentiment-tag tag-{label}' style='font-size:9px;'>{label}</span>
                    <span style='font-size:11px; color:#666;'> | {item.get("publisher")}</span>
                    <div style='font-size:12px; color:#aaa; margin-top:5px;'>{item.get("summary")[:120]}...</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Social Consensus Logic
            st.subheader("💬 Social Consensus")
            if social:
                social_posts = social.get("data", [])
                social_summary = social.get("summary", "")
                social_source = social.get("source", "")
                
                st.caption(f"Source: {social_source}")
                st.markdown(f"**Insight:** {social_summary}")
                
                if social_posts:
                    pos_count = len([p for p in social_posts if p.get('sentiment_label') == 'positive'])
                    consensus = round((pos_count / len(social_posts)) * 100) if social_posts else 50
                    st.write(f"Community Sentiment: {consensus}% Bullish")
                    st.progress(consensus / 100)
                    
                    for post in social_posts[:5]:
                        label = post.get('sentiment_label', 'neutral')
                        st.markdown(f"""
                        <div class='social-post'>
                            <span class='sentiment-tag tag-{label}'>{label}</span>
                            <span style='font-size:12px; color:#aaa; margin-left:10px'>@{post.get('handle')}</span>
                            <div style='font-size:13px; margin-top:5px'>{post.get('content')}</div>
                            <div style='font-size:10px; color:#666'>{post.get('source')} | {post.get('timestamp')[:16]}</div>
                        </div>
                        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center; padding-top:100px; opacity:0.6'>
        <img src='https://img.icons8.com/isometric/200/diamond.png' width='150'><br>
        <h1>Welcome to InvestAI Terminal</h1>
        <p>Enter a ticker symbol in the sidebar to begin institutional-grade research.</p>
    </div>
    """, unsafe_allow_html=True)
