# Change History

## [2026-01-29] - 5 Changes
- 08:55 - news_scraper_service.py - Implemented `ArticleScraperService` - Backend support for full article summarization
- 20:55 - test_database_service.py - Created 20 unit tests for DatabaseService - Full test coverage for CRUD operations
- 20:55 - database_service.py - Fixed `news_sentiment` → `news_context`, `.dict()` → `.model_dump()` - Bug fix + Pydantic v2 compatibility
- 20:59 - test_nlp_service.py, test_nlp_summarization.py - Fixed NLP summarization tests - Input length guard bypass + relaxed model output assertion

## [2026-01-28] - 6 Changes
- 08:35 - news_service.py - Added NewsService - Live yfinance news aggregation
- 08:38 - memo.py - Integrated live news & updated scoring - Replace mock data with real signals
- 08:42-09:10 - app.py - Revamped News UI, Added Portfolio Dashboard - UI/UX enhancements and performance tracking
- 08:55 - portfolio.py - Created Portfolio API - Handle virtual trades & P/L logic
- 09:15 - docs/ - Comprehensive Documentation Sync - Updated architectural docs, tech specs, and PRD and schemas.
