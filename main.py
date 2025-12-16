import os
import time
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import pytz
from telegram import Bot

# Import analysis modules
from stocks_list import STOCKS_LIST
from analysis_smc_1d import analyze_smc_daily
from analysis_bajaj_hourly import analyze_bajaj_hourly
from analysis_rsi_mtf import analyze_rsi_mtf
from analysis_engulfing_4h import analyze_engulfing_4h

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# ⚠️ TEST MODE - DISABLE MARKET CHECK
TEST_MODE = True  # Set to False for production

def is_market_open():
    """Check if NSE is open today - DISABLED IN TEST MODE"""
    if TEST_MODE:
        print("⚠️ TEST MODE: Market check disabled")
        return True
    
    try:
        nse = mcal.get_calendar('NSE')
        today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
        
        schedule = nse.schedule(start_date=today, end_date=today)
        if schedule.empty:
            return False
        
        now_ist = datetime.now(pytz.timezone('Asia/Kolkata'))
        market_open = schedule.iloc[0]['market_open'].astimezone(pytz.timezone('Asia/Kolkata'))
        market_close = schedule.iloc[0]['market_close'].astimezone(pytz.timezone('Asia/Kolkata'))
        
        return market_open <= now_ist <= market_close
    except:
        return False

def send_telegram_message(message):
    """Send message to Telegram"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        print("✅ Message sent to Telegram")
        return True
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

def format_results(smc_results, bajaj_results, rsi_results, engulfing_results):
    """Format all analysis results into a single message"""
    current_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"<b>🧪 TEST RUN - NSE STOCK ANALYSIS</b>\n"
    message += f"<i>Time: {current_time}</i>\n"
    message += "═" * 50 + "\n\n"
    
    # 1. SMC DAILY ANALYSIS
    if smc_results:
        message += "<b>🎯 SMC DAILY (35% Discount + Swing Low):</b>\n"
        for stock in smc_results[:5]:  # Top 5
            signals = []
            if stock['order_block'] == 'Y': signals.append('OB')
            if stock['fvg'] == 'Y': signals.append('FVG')
            if stock['volume_spike'] == 'Y': signals.append('VOLx2')
            
            message += f"• {stock['symbol']}: {stock['confluence_score']}/3 → {', '.join(signals)}\n"
        message += f"Total qualified: {len(smc_results)}\n\n"
    else:
        message += "<b>❌ SMC DAILY:</b> No signals found\n\n"
    
    # 2. BAJAJ HOURLY ANALYSIS
    if bajaj_results:
        message += "<b>⏰ BAJAJ-STYLE HOURLY (15% Discount):</b>\n"
        for stock in bajaj_results[:5]:  # Top 5
            message += f"• {stock['symbol']}: OB={stock['ob']}, Score={stock['confluence_score']}\n"
        message += f"Total qualified: {len(bajaj_results)}\n\n"
    else:
        message += "<b>❌ BAJAJ HOURLY:</b> No signals found\n\n"
    
    # 3. RSI MULTI-TIMEFRAME
    if rsi_results:
        oversold = [r for r in rsi_results if r['confluence'] == "TRIPLE_OVERSOLD"]
        overbought = [r for r in rsi_results if r['confluence'] == "TRIPLE_OVERBOUGHT"]
        
        if oversold:
            message += "<b>🟢 TRIPLE OVERSOLD (1D+4H+1H):</b>\n"
            for stock in oversold[:3]:
                message += f"• {stock['symbol']}: 1D={stock['1D_RSI']}, 4H={stock['4H_RSI']}, 1H={stock['1H_RSI']}\n"
        
        if overbought:
            message += "<b>🔴 TRIPLE OVERBOUGHT (1D+4H+1H):</b>\n"
            for stock in overbought[:3]:
                message += f"• {stock['symbol']}: 1D={stock['1D_RSI']}, 4H={stock['4H_RSI']}, 1H={stock['1H_RSI']}\n"
        
        if oversold or overbought:
            message += f"Total triple alignments: {len(rsi_results)}\n\n"
    else:
        message += "<b>❌ RSI MTF:</b> No triple alignments found\n\n"
    
    # 4. 4H ENGULFING
    if engulfing_results:
        bullish = [r for r in engulfing_results if r['pattern'] == 'BULLISH']
        bearish = [r for r in engulfing_results if r['pattern'] == 'BEARISH']
        
        if bullish:
            message += "<b>📈 4H BULLISH ENGULFING:</b>\n"
            for stock in bullish[:3]:
                message += f"• {stock['symbol']}: ₹{stock['price']} ({stock['change_pct']:+.2f}%)\n"
        
        if bearish:
            message += "<b>📉 4H BEARISH ENGULFING:</b>\n"
            for stock in bearish[:3]:
                message += f"• {stock['symbol']}: ₹{stock['price']} ({stock['change_pct']:+.2f}%)\n"
        
        message += f"Total engulfing patterns: {len(engulfing_results)}\n\n"
    else:
        message += "<b>❌ 4H ENGULFING:</b> No patterns found\n\n"
    
    # SUMMARY
    message += "<b>📊 TEST SUMMARY:</b>\n"
    message += f"• Total stocks analyzed: {len(STOCKS_LIST)}\n"
    message += f"• SMC Daily signals: {len(smc_results) if smc_results else 0}\n"
    message += f"• Bajaj Hourly signals: {len(bajaj_results) if bajaj_results else 0}\n"
    message += f"• RSI Triple signals: {len(rsi_results) if rsi_results else 0}\n"
    message += f"• 4H Engulfing signals: {len(engulfing_results) if engulfing_results else 0}\n"
    
    message += f"\n<i>⚠️ This was a TEST RUN with market check disabled</i>"
    
    return message

def run_analysis():
    """Run all analyses"""
    print(f"🧪 TEST MODE: Starting analysis at {datetime.now()}")
    
    if not is_market_open():
        print("⚠️ Market is closed but running in TEST MODE")
    
    print(f"📊 Analyzing {len(STOCKS_LIST)} stocks...")
    
    # Run all analyses
    smc_results = []
    bajaj_results = []
    rsi_results = []
    engulfing_results = []
    
    # Analyze only 10 stocks for quick testing
    test_stocks = STOCKS_LIST[:10]  # Only first 10 for quick test
    
    for i, symbol in enumerate(test_stocks, 1):
        print(f"   [{i:3d}/{len(test_stocks)}] {symbol.replace('.NS', '')}")
        
        try:
            # Run SMC Daily
            smc_result = analyze_smc_daily(symbol)
            if smc_result:
                smc_results.append(smc_result)
            
            # Run Bajaj Hourly
            bajaj_result = analyze_bajaj_hourly(symbol)
            if bajaj_result:
                bajaj_results.append(bajaj_result)
            
            # Run RSI MTF
            rsi_result = analyze_rsi_mtf(symbol)
            if rsi_result:
                rsi_results.append(rsi_result)
            
            # Run 4H Engulfing
            engulfing_result = analyze_engulfing_4h(symbol)
            if engulfing_result:
                engulfing_results.append(engulfing_result)
            
            # Small delay to avoid rate limiting
            time.sleep(0.3)
            
        except Exception as e:
            print(f"      Error analyzing {symbol}: {e}")
            continue
    
    print(f"\n✅ Analysis completed!")
    print(f"   SMC Daily: {len(smc_results)} signals")
    print(f"   Bajaj Hourly: {len(bajaj_results)} signals")
    print(f"   RSI MTF: {len(rsi_results)} signals")
    print(f"   4H Engulfing: {len(engulfing_results)} signals")
    
    # Format and send results
    message = format_results(smc_results, bajaj_results, rsi_results, engulfing_results)
    
    if send_telegram_message(message):
        print("✅ Telegram message sent successfully!")
    else:
        print("❌ Failed to send Telegram message")

if __name__ == "__main__":
    # Validate Telegram credentials
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ ERROR: Telegram credentials not set!")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as environment variables")
        exit(1)
    
    print("🧪 STARTING TEST RUN...")
    print(f"📊 Stocks to analyze: {len(STOCKS_LIST)}")
    print(f"⚙️  TEST_MODE: {TEST_MODE}")
    
    # Run analysis
    run_analysis()
