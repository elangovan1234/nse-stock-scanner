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

async def send_telegram_message(message):
    """Send message to Telegram (async) - ONE MESSAGE ONLY"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        return True
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def format_results(smc_results, bajaj_results, rsi_results, engulfing_results, total_stocks):
    """Format all analysis results into ONE comprehensive message with requested formatting"""
    # Time in 12-hour AM/PM format
    current_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %I:%M %p')
    
    message = f"<b>📊 NSE STOCK ANALYSIS - {current_time}</b>\n"
    message += "═" * 50 + "\n\n"
    
    # 1. SMC DAILY ANALYSIS - Changed to "1D-LONG"
    if smc_results:
        message += "<b>🎯 1D-LONG (35% Discount + Swing Low):</b>\n"
        for stock in smc_results[:15]:  # Increased to 15
            signals = []
            if stock['order_block'] == 'Y': signals.append('OB')
            if stock['fvg'] == 'Y': signals.append('FVG')
            if stock['volume_spike'] == 'Y': signals.append('VOLx2')
            
            message += f"• {stock['symbol']}: {stock['confluence_score']}/3 → {', '.join(signals)}\n"
        if len(smc_results) > 15:
            message += f"... and {len(smc_results) - 15} more\n"
        message += f"<i>Total: {len(smc_results)}</i>\n\n"
    
    # 2. BAJAJ HOURLY ANALYSIS - Changed to "1HR-LONG"
    if bajaj_results:
        message += "<b>⏰ 1HR-LONG (15% Discount):</b>\n"
        for stock in bajaj_results[:15]:  # Increased to 15
            message += f"• {stock['symbol']}: OB={stock['ob']}, Score={stock['confluence_score']}\n"
        if len(bajaj_results) > 15:
            message += f"... and {len(bajaj_results) - 15} more\n"
        message += f"<i>Total: {len(bajaj_results)}</i>\n\n"
    
    # 3. RSI MULTI-TIMEFRAME - Simplified formatting
    if rsi_results:
        oversold = [r for r in rsi_results if 'OVERSOLD' in r.get('confluence', '')]
        overbought = [r for r in rsi_results if 'OVERBOUGHT' in r.get('confluence', '')]
        
        if oversold:
            message += "<b>🟢 TRIPLE OVERSOLD:</b>\n"
            for stock in oversold[:10]:  # Show more stocks
                # Format: symbol: 1D_RSI-4H_RSI-1H_RSI (no color balls, just numbers)
                rsi_values = f"{stock['1D_RSI']:.0f}-{stock['4H_RSI']:.0f}-{stock['1H_RSI']:.0f}"
                message += f"• {stock['symbol']}: {rsi_values}\n"
            if len(oversold) > 10:
                message += f"... and {len(oversold) - 10} more\n"
        
        if overbought:
            message += "<b>🔴 TRIPLE OVERBOUGHT:</b>\n"
            for stock in overbought[:10]:  # Show more stocks
                # Format: symbol: 1D_RSI-4H_RSI-1H_RSI (no color balls, just numbers)
                rsi_values = f"{stock['1D_RSI']:.0f}-{stock['4H_RSI']:.0f}-{stock['1H_RSI']:.0f}"
                message += f"• {stock['symbol']}: {rsi_values}\n"
            if len(overbought) > 10:
                message += f"... and {len(overbought) - 10} more\n"
        
        message += f"<i>Total triple alignments: {len(rsi_results)}</i>\n\n"
    
    # 4. 4H ENGULFING - Simplified formatting
    if engulfing_results:
        bullish = [r for r in engulfing_results if r['pattern'] == 'BULLISH']
        bearish = [r for r in engulfing_results if r['pattern'] == 'BEARISH']
        
        if bullish:
            message += "<b>📈 4H BULLISH ENGULFING:</b>\n"
            for stock in bullish[:10]:  # Show more stocks, no price/percentage
                message += f"• {stock['symbol']}\n"
            if len(bullish) > 10:
                message += f"... and {len(bullish) - 10} more\n"
        
        if bearish:
            message += "<b>📉 4H BEARISH ENGULFING:</b>\n"
            for stock in bearish[:10]:  # Show more stocks, no price/percentage
                message += f"• {stock['symbol']}\n"
            if len(bearish) > 10:
                message += f"... and {len(bearish) - 10} more\n"
        
        message += f"<i>Total engulfing patterns: {len(engulfing_results)}</i>\n\n"
    
    # 5. SIMPLE SUMMARY ONLY (removed executive summary and strong picks)
    message += "<b>📋 SUMMARY:</b>\n"
    message += f"• Total stocks: {total_stocks}\n"
    message += f"• 1D-LONG: {len(smc_results)}\n"
    message += f"• 1HR-LONG: {len(bajaj_results)}\n"
    message += f"• RSI Triple: {len(rsi_results)}\n"
    message += f"• 4H Engulfing: {len(engulfing_results)}\n"
    
    if not any([smc_results, bajaj_results, rsi_results, engulfing_results]):
        message += "\n<i>⚠️ No signals found</i>"
    
    return message

async def analyze_all_stocks():
    """Analyze ALL 209 stocks silently"""
    print(f"🔍 Analyzing ALL {len(STOCKS_LIST)} stocks...")
    
    smc_results = []
    bajaj_results = []
    rsi_results = []
    engulfing_results = []
    
    analyzed = 0
    errors = 0
    
    for i, symbol in enumerate(STOCKS_LIST, 1):
        if i % 20 == 0:
            print(f"   [{i:3d}/{len(STOCKS_LIST)}] stocks analyzed")
        
        try:
            # Run all analyses
            smc = analyze_smc_daily(symbol)
            if smc:
                smc_results.append(smc)
            
            bajaj = analyze_bajaj_hourly(symbol)
            if bajaj:
                bajaj_results.append(bajaj)
            
            rsi = analyze_rsi_mtf(symbol)
            if rsi:
                rsi_results.append(rsi)
            
            engulf = analyze_engulfing_4h(symbol)
            if engulf:
                engulfing_results.append(engulf)
            
            analyzed += 1
            time.sleep(0.25)  # Rate limiting
            
        except Exception as e:
            errors += 1
            continue
    
    print(f"✅ Analysis complete! Analyzed: {analyzed}, Errors: {errors}")
    return smc_results, bajaj_results, rsi_results, engulfing_results

async def main():
    """Main function - ONE MESSAGE ONLY"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram credentials missing!")
        return
    
    print("🚀 Starting NSE Stock Analysis...")
    print(f"📊 Total stocks: {len(STOCKS_LIST)}")
    
    # Analyze all stocks
    results = await analyze_all_stocks()
    
    # Create ONE comprehensive message
    message = format_results(*results, len(STOCKS_LIST))
    
    # Send ONE message only
    if await send_telegram_message(message):
        print("✅ Telegram message sent successfully!")
    else:
        print("❌ Failed to send Telegram message")

if __name__ == "__main__":
    asyncio.run(main())
