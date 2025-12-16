# NSE Stock Analysis Automation 🤖

Automated stock analysis system that runs on NSE market days at:
- 10:30 AM IST
- 2:00 PM IST  
- 5:00 PM IST

Sends analysis results directly to Telegram with NO Excel files needed.

## Features
✅ All 4 analysis methods integrated:
1. **SMC Daily Analysis** - 35% discount + swing low setups
2. **Bajaj-Style Hourly** - 15% discount + order blocks
3. **RSI Multi-Timeframe** - 1D/4H/1H triple alignments
4. **4H Engulfing Patterns** - Bullish/Bearish engulfing candles

✅ Automatic market day detection
✅ Telegram alerts only (no Excel output)
✅ Hardcoded 209 NSE F&O stocks
✅ Runs on GitHub Actions (free)

## Setup Instructions

### 1. Create GitHub Repository
1. Create new repository on GitHub
2. Name: `nse-stock-analysis`
3. Don't initialize with README

### 2. Create Files in Repository
Create these 9 files exactly as shown above:
1. `requirements.txt`
2. `stocks_list.py`
3. `analysis_smc_1d.py`
4. `analysis_bajaj_hourly.py`
5. `analysis_rsi_mtf.py`
6. `analysis_engulfing_4h.py`
7. `main.py`
8. `.github/workflows/nse_analysis.yml`
9. `README.md`

### 3. Set Up Telegram Bot
1. Message @BotFather on Telegram
2. Send `/newbot` and follow instructions
3. Get your bot token (format: `1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ`)
4. Message @userinfobot to get your chat ID

### 4. Set GitHub Secrets
Go to your repository → Settings → Secrets and variables → Actions → New repository secret:

Add these secrets:
- **Name**: `TELEGRAM_BOT_TOKEN`
  **Value**: Your bot token from @BotFather

- **Name**: `TELEGRAM_CHAT_ID`
  **Value**: Your chat ID from @userinfobot

### 5. Manual Test Run
1. Go to "Actions" tab
2. Click "NSE Stock Analysis"
3. Click "Run workflow" → "Run workflow"
4. Check Telegram for results

## Time Schedule (IST)
- Morning: 10:30 AM (05:00 UTC)
- Afternoon: 2:00 PM (08:30 UTC)
- Evening: 5:00 PM (11:30 UTC)

Only runs Monday-Friday on NSE market days.

## File Structure
