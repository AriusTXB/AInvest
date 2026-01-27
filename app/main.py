from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="InvestAI API",
    description="Backend for Automated Equity Research Platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "InvestAI API"}

@app.get("/")
def root():
    return {"message": "InvestAI API is running"}

# specialized routers
from app.api.endpoints import market
app.include_router(market.router, prefix="/api/market", tags=["Market"])
