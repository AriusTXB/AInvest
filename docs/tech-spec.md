# Technical Specifications

## Technology Stack
- **Language**: Python 3.9+
- **Web Framework**: FastAPI (`0.109.0`)
- **Server**: Uvicorn (`0.27.0`)
- **Frontend**: Streamlit (`1.31.0`)
- **Data Processing**: Pandas (`2.2.0`), Numpy (`1.26.3`)
- **Finance Data**: yfinance (`0.2.36`), pandas_ta (`0.3.14b0`)
- **ML/AI**:
  - Pytorch (`2.2.0`)
  - Transformers (`4.37.2`)
  - Scikit-learn (`1.4.0`)
- **Vision**: Pytesseract, pdf2image, OpenCV

## API Definition

### Base URL
`http://localhost:8000`

### Endpoints

#### Market
- `GET /api/market/{ticker}`: Returns raw market data and indicators.

#### Memo
- `GET /api/memo/{ticker}`: Returns full investment memo.
  - **Returns**: `InvestmentMemo` schema.

#### Social
- `GET /api/social/feed`: Returns mock social posts.

#### NLP
- `POST /api/nlp/analyze`: Analyzing text sentiment.

## Data Schemas (Pydantic)

### InvestmentMemo
```json
{
  "ticker": "string",
  "generated_at": "datetime",
  "market_data": {
    "price": "float",
    "indicators": {
      "rsi": "float",
      "macd": "float"
    }
  },
  "social_context": ["SocialPost"],
  "recommendation": "BUY|SELL|HOLD"
}
```

## Algorithms
- **Recommendation Logic**:
  - Score starts at 0.
  - RSI < 30 -> +1 (Oversold/Buy)
  - RSI > 70 -> -1 (Overbought/Sell)
  - Sentiment Positive -> +1
  - Sentiment Negative -> -1
  - Net Score >= 1 -> BUY, <= -1 -> SELL, else HOLD.
