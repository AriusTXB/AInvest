import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="InvestAI Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
    }
    .recommendation-buy { color: #00ff00; font-weight: bold; font-size: 24px; }
    .recommendation-sell { color: #ff0000; font-weight: bold; font-size: 24px; }
    .recommendation-hold { color: #ffff00; font-weight: bold; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("InvestAI 🚀")
st.sidebar.markdown("---")

ticker_input = st.sidebar.text_input("Enter Ticker", value="AAPL").upper()
analyze_btn = st.sidebar.button("Analyze Ticker", type="primary")

st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")

api_status = "Unknown"
try:
    if requests.get(f"{API_BASE_URL}/health", timeout=2).status_code == 200:
        api_status = "✅ Online"
    else:
        api_status = "❌ Error"
except:
    api_status = "🔴 Offline"
st.sidebar.info(f"API: {api_status}")

# --- Main App Logic ---

st.title(f"Market Intelligence: {ticker_input}")

if analyze_btn or ticker_input:
    with st.spinner(f"Generating Investment Memo for {ticker_input}..."):
        try:
            response = requests.get(f"{API_BASE_URL}/api/memo/{ticker_input}")
            
            if response.status_code == 200:
                data = response.json()
                market = data.get("market_data", {})
                indicators = market.get("indicators", {})
                rec = data.get("recommendation", "HOLD")
                
                # Top Metrics Row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Price", f"${market.get('price', 0)}", f"{market.get('change_percent', 0)}%")
                
                with col2:
                    st.metric("RSI (14)", indicators.get("rsi", 0))
                
                with col3:
                    st.metric("MACD", indicators.get("macd", 0))
                    
                with col4:
                    color_class = f"recommendation-{rec.lower()}"
                    st.markdown(f"<div class='metric-card'><div style='font-size:14px'>AI Signal</div><div class='{color_class}'>{rec}</div></div>", unsafe_allow_html=True)
                
                # Summary
                st.markdown("### 📝 Analysis Summary")
                st.info(data.get("analysis_summary", "No summary available."))

                # Tabs for details
                tab1, tab2, tab3 = st.tabs(["📊 Technicals", "📰 News & Sentiment", "🐦 Social Signals"])
                
                with tab1:
                    st.subheader("Technical Indicators")
                    tech_df = pd.DataFrame([indicators])
                    st.dataframe(tech_df, use_container_width=True)
                    
                    st.markdown(f"**Sector:** {market.get('sector', 'N/A')}")
                    st.markdown(f"**Company:** {market.get('company_name', 'N/A')}")
                    st.text_area("Company Summary", market.get("summary", ""), height=100)

                with tab2:
                    st.subheader("AI News Analysis")
                    sentiment = data.get("news_sentiment", {})
                    st.markdown(f"**Headline Analyzed:** *{sentiment.get('headline_analyzed', 'N/A')}*")
                    
                    analysis = sentiment.get("analysis", {})
                    score = analysis.get("score", 0)
                    label = analysis.get("label", "Neutral")
                    
                    st.progress(score if label == "positive" else (1-score))
                    st.caption(f"Sentiment: {label.upper()} ({round(score*100, 1)}% Confidence)")

                with tab3:
                    st.subheader("Social Stream")
                    social_posts = data.get("social_context", [])
                    if social_posts:
                        for post in social_posts:
                            with st.chat_message("user"):
                                st.write(f"**@{post.get('handle')}**: {post.get('content')}")
                                st.caption(f"{post.get('timestamp')} | Sentiment: {post.get('sentiment_label')}")
                    else:
                        st.write("No recent social signals found.")

            elif response.status_code == 404:
                st.error(f"Ticker '{ticker_input}' not found. Please check the symbol.")
            else:
                st.error(f"API Error: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to connect to backend: {str(e)}")
else:
    st.info("👈 Enter a ticker and click 'Analyze' to start.")
