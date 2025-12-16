import os
import asyncio
import time
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import pytz

# Import analysis modules
from stocks_list import STOCKS_LIST
from analysis_smc_1d import analyze_smc_daily
from analysis_bajaj_hourly import analyze_bajaj_hourly
from analysis_rsi_mtf import analyze_rsi_mtf
from analysis_engulfing_4h import analyze_engulfing_4h

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Import telegram
from telegram import Bot

# ⚠️ FORCE ANALYSIS MODE
FORCE_ANALYSIS = True  # Set to True to always run analysis

async def send_telegram_message(message):
    """Send message to Telegram (async)"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        print("✅ Message sent to Telegram")
        return True
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

def format_results(smc_results, bajaj_results, rsi_results, engulfing_results, analyzed_count):
    """Format all analysis results into a single message"""
    current_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"<b>📊 NSE STOCK ANALYSIS - {current_time}</b>\n"
    message += "═" * 50 + "\n\n"
    
    # 1. SMC DAILY ANALYSIS
    if smc_results:
        message += "<b>🎯 SMC DAILY (35% Discount + Swing Low):</b>\n"
        for stock in smc_results[:10]:  # Top 10
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
        for stock in bajaj_results[:10]:  # Top 10
            message += f"• {stock['symbol']}: OB={stock['ob']}, Score={stock['confluence_score']}\n"
        message += f"Total qualified: {len(bajaj_results)}\n\n"
    else:
        message += "<b>❌ BAJAJ HOURLY:</b> No signals found\n\n"
    
    # 3. RSI MULTI-TIMEFRAME
    if rsi_results:
        oversold = [r for r in rsi_results if 'OVERSOLD' in r.get('confluence', '')]
        overbought = [r for r in rsi_results if 'OVERBOUGHT' in r.get('confluence', '')]
        
        if oversold:
            message += "<b>🟢 TRIPLE OVERSOLD (1D+4H+1H):</b>\n"
            for stock in oversold[:5]:
                message += f"• {stock['symbol']}: 1D={stock['1D_RSI']}, 4H={stock['4H_RSI']}, 1H={stock['1H_RSI']}\n"
        
        if overbought:
            message += "<b>🔴 TRIPLE OVERBOUGHT (1D+4H+1H):</b>\n"
            for stock in overbought[:5]:
                message += f"• {stock['symbol']}: 1D={stock['1D_RSI']}, 4H={stock['4H_RSI']}, 1H={stock['1H_RSI']}\n"
        
        message += f"Total triple alignments: {len(rsi_results)}\n\n"
    else:
        message += "<b>❌ RSI MTF:</b> No triple alignments found\n\n"
    
    # 4. 4H ENGULFING
    if engulfing_results:
        bullish = [r for r in engulfing_results if r['pattern'] == 'BULLISH']
        bearish = [r for r in engulfing_results if r['pattern'] == 'BEARISH']
        
        if bullish:
            message += "<b>📈 4H BULLISH ENGULFING:</b>\n"
            for stock in bullish[:5]:
                message += f"• {stock['symbol']}: ₹{stock['price']} ({stock['change_pct']:+.2f}%)\n"
        
        if bearish:
            message += "<b>📉 4H BEARISH ENGULFING:</b>\n"
            for stock in bearish[:5]:
                message += f"• {stock['symbol']}: ₹{stock['price']} ({stock['change_pct']:+.2f}%)\n"
        
        message += f"Total engulfing patterns: {len(engulfing_results)}\n\n"
    else:
        message += "<b>❌ 4H ENGULFING:</b> No patterns found\n\n"
    
    # SUMMARY
    message += "<b>📊 ANALYSIS SUMMARY:</b>\n"
    message += f"• Total stocks analyzed: {analyzed_count}\n"
    message += f"• SMC Daily signals: {len(smc_results)}\n"
    message += f"• Bajaj Hourly signals: {len(bajaj_results)}\n"
    message += f"• RSI Triple signals: {len(rsi_results)}\n"
    message += f"• 4H Engulfing signals: {len(engulfing_results)}\n"
    message += f"• Total time: {datetime.now().strftime('%H:%M:%S')}\n"
    
    return message

async def run_full_analysis():
    """Run full analysis on ALL stocks"""
    print(f"🚀 Starting FULL analysis at {datetime.now()}")
    print(f"📊 Analyzing ALL {len(STOCKS_LIST)} stocks...")
    
    # Run all analyses
    smc_results = []
    bajaj_results = []
    rsi_results = []
    engulfing_results = []
    
    analyzed_count = 0
    errors = 0
    
    # Send progress update
    await send_telegram_message(f"🔍 <b>ANALYSIS STARTED</b>\n\nAnalyzing {len(STOCKS_LIST)} stocks...")
    
    for i, symbol in enumerate(STOCKS_LIST, 1):
        stock_name = symbol.replace('.NS', '')
        
        if i % 20 == 0:  # Progress every 20 stocks
            print(f"   [{i:3d}/{len(STOCKS_LIST)}] {stock_name}")
            # Send progress update every 50 stocks
            if i % 50 == 0:
                progress_msg = f"📈 <b>Progress:</b> {i}/{len(STOCKS_LIST)} stocks analyzed\n"
                progress_msg += f"✅ SMC: {len(smc_results)}, Bajaj: {len(bajaj_results)}\n"
                progress_msg += f"✅ RSI: {len(rsi_results)}, Engulfing: {len(engulfing_results)}"
                await send_telegram_message(progress_msg)
        
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
            
            analyzed_count += 1
            
            # Rate limiting
            time.sleep(0.3)  # Reduced delay for faster analysis
            
        except Exception as e:
            errors += 1
            if errors <= 5:  # Log first 5 errors only
                print(f"      Error analyzing {stock_name}: {e}")
            continue
    
    print(f"\n✅ Analysis completed!")
    print(f"   Stocks analyzed: {analyzed_count}")
    print(f"   Errors: {errors}")
    print(f"   SMC Daily: {len(smc_results)} signals")
    print(f"   Bajaj Hourly: {len(bajaj_results)} signals")
    print(f"   RSI MTF: {len(rsi_results)} signals")
    print(f"   4H Engulfing: {len(engulfing_results)} signals")
    
    # Format and send results
    message = format_results(smc_results, bajaj_results, rsi_results, engulfing_results, analyzed_count)
    
    if await send_telegram_message(message):
        print("✅ Telegram message sent successfully!")
    else:
        print("❌ Failed to send Telegram message")
    
    return smc_results, bajaj_results, rsi_results, engulfing_results

async def main():
    """Main async function"""
    # Validate Telegram credentials
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ ERROR: Telegram credentials not set!")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as environment variables")
        return
    
    print("=" * 60)
    print("🚀 NSE STOCK ANALYSIS - FULL SCAN")
    print("=" * 60)
    print(f"📊 Total stocks: {len(STOCKS_LIST)}")
    print(f"⚙️  FORCE_ANALYSIS: {FORCE_ANALYSIS}")
    print("=" * 60)
    
    # Send startup message
    startup_msg = f"🤖 <b>NSE ANALYSIS BOT STARTED</b>\n\n"
    startup_msg += f"📊 Analyzing: {len(STOCKS_LIST)} stocks\n"
    startup_msg += f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    startup_msg += "═" * 30 + "\n\n"
    startup_msg += "<b>ANALYSIS MODULES:</b>\n"
    startup_msg += "• SMC Daily (35% discount + swing low)\n"
    startup_msg += "• Bajaj Hourly (15% discount)\n"
    startup_msg += "• RSI Multi-Timeframe\n"
    startup_msg += "• 4H Engulfing Patterns\n\n"
    startup_msg += "<i>Analysis in progress...</i>"
    
    await send_telegram_message(startup_msg)
    
    # Run analysis
    results = await run_full_analysis()
    
    # Send completion message
    completion_msg = f"✅ <b>ANALYSIS COMPLETED</b>\n\n"
    completion_msg += f"📊 Total stocks analyzed: {len(STOCKS_LIST)}\n"
    completion_msg += f"🕒 Finished: {datetime.now().strftime('%H:%M:%S')}\n\n"
    completion_msg += "<i>Check above for detailed results.</i>"
    
    await send_telegram_message(completion_msg)

if __name__ == "__main__":
    asyncio.run(main())
