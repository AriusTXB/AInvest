# Changelog

All notable changes to the InvestAI project will be documented in this file.

## [2026-01-28]

### Added
- **DeepSeek OCR Integration**: Added high-intelligence OCR engine choice (DeepSeek V3/R1) for superior financial table extraction.
- **Vision Service Enhancement**: 
  - Integrated image preprocessing (Otsu thresholding, Grayscale) for improved OCR accuracy.
  - Refined parsing heuristics for multi-currency and negative value support.
- **Social Service**: 
  - Integrated Stocktwits API for unified social sentiment aggregation.
  - Improved data deduplication and timestamp sorting for a cleaner live feed.
- **Frontend Refinement**: 
  - Added OCR Engine selector in the sidebar.
  - Revamped social consensus section with live insight summaries and BULL/BEAR tags.
- **Persistence**: Integrated Supabase for historical Investment Memo storage.

### Documentation
- Created Architecture documentation (`docs/architect.md`).
- Established Technical Specifications (`docs/tech-spec.md`).
- Drafted Product Requirements Document (`docs/prd.md`).
