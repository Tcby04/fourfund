# FourFund

Simple, free Ramsey-style investment portfolio tool.

## What It Is

A tool that recommends the best funds for each category using the classic 25/25/25/25 split:
- 25% Large Cap Growth
- 25% Mid Cap
- 25% Small Cap  
- 25% International

## How It Works

- **Data Collection:** Python script fetches historical data from Yahoo Finance
- **Ranking Algorithm:** Scores funds based on:
  - Expense ratio (lower = better)
  - Long-term performance (10-year returns)
  - Consistency
- **Static Database:** Fund data is pre-calculated and stored in JSON

## Tech Stack

- **Frontend:** Plain HTML/CSS/JS (no frameworks)
- **Data:** yfinance for historical data
- **Hosting:** GitHub Pages

## Files

- `index.html` - Main website
- `fetch_funds.py` - Data collection script
- `fund_data.json` - Cached fund data

## URL

https://tcby04.github.io/fourfund/

## Status

MVP complete! Just needs to be pushed to GitHub.
