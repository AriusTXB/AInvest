import streamlit as st
import requests

st.set_page_config(
    page_title="InvestAI Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("InvestAI Terminal 🚀")
st.markdown("### Automated Equity Research Platform")

# Sidebar
st.sidebar.header("Configuration")
api_status = "Unknown"

try:
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        api_status = "✅ Online"
    else:
        api_status = "❌ Error"
except:
    api_status = "🔴 Offline"

st.sidebar.metric("API Status", api_status)

# Main Dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader("Market Intelligence")
    st.info("Market Data Module not loaded.")

with col2:
    st.subheader("Social Signals")
    st.warning("Social Scraper Module not loaded.")
