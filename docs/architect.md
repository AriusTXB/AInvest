# Architecture Documentation

## High-Level Overview
InvestAI is an automated equity research platform that aggregates market data, social sentiment, and news analysis to generate investment memos.
It follows a **Micro-Service style Monolith** architecture where a single FastAPI backend serves distinct modules (Market, Vision, NLP, Social) consumed by a Streamlit frontend.

## Components

### 1. Frontend (Streamlit)
- **Location**: `/frontend/app.py`
- **Role**: User Interface for displaying dashboards and reports.
- **Communication**: REST API calls to the Backend.

### 2. Backend (FastAPI)
- **Location**: `/app/main.py`
- **Role**: API Gateway and orchestrator.
- **Modules**:
  - `market`: Historical data & Technical Analysis (SMA, RSI, MACD).
  - `nlp`: Sentiment analysis on news headlines.
  - `social`: Social media signal simulation/scraping.
  - `memo`: Aggregation service that combines all inputs into a recommendation.
  - `vision`: (Planned/Stub) Document OCR/analysis.

### 3. Services Layer
- **Location**: `/app/services/`
- **Role**: Business logic and external integrations.
- **Key Services**:
  - `MarketService`: Wrapper around `yfinance` and `pandas` for calculation.
  - `NLPService`: Usage of `transformers` / `torch` for text analysis.
  - `SocialService`: Manages social feeds (currently simulated).

## Data Flow
1. **User Request**: User selects a ticker in Streamlit.
2. **Orchestration**: Streamlit calls `GET /api/memo/{ticker}`.
3. **Aggregation**: `Memo` endpoint calls `MarketService`, `SocialService`, and `NLPService` in parallel (conceptually).
4. **Processing**:
   - `MarketService` fetches `yfinance` data -> computes indicators.
   - `SocialService` retrieves recent posts.
   - `NLPService` analyzes simulated/real headlines.
5. **Synthesis**: Logic in `memo.py` combines scores (RSI + Sentiment) to output BUY/SELL/HOLD.
6. **Response**: JSON payload returned to Streamlit for rendering.

## Design Decisions
- **Streamlit for UI**: Rapid prototyping and data visualization capabilities out-of-the-box.
- **FastAPI**: High-performance async support for concurrent service execution.
- **On-the-fly Analysis**: No persistent database observed yet; data is fetched and analyzed in real-time.
