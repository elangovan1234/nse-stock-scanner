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
    """Format all analysis results into ONE comprehensive message"""
    current_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"<b>📊 NSE STOCK ANALYSIS - {current_time}</b>\n"
    message += "═" * 50 + "\n\n"
    
    # 1. SMC DAILY ANALYSIS
    if smc_results:
        message += "<b>🎯 SMC DAILY (35% Discount + Swing Low):</b>\n"
        for stock in smc_results[:10]:  # Show top 10
            signals = []
            if stock['order_block'] == 'Y': signals.append('OB')
            if stock['fvg'] == 'Y': signals.append('FVG')
            if stock['volume_spike'] == 'Y': signals.append('VOLx2')
            
            message += f"• {stock['symbol']}: {stock['confluence_score']}/3 → {', '.join(signals)}\n"
        if len(smc_results) > 10:
            message += f"... and {len(smc_results) - 10} more\n"
        message += f"<i>Total qualified: {len(smc_results)}</i>\n\n"
    
    # 2. BAJAJ HOURLY ANALYSIS
    if bajaj_results:
        message += "<b>⏰ BAJAJ-STYLE HOURLY (15% Discount):</b>\n"
        for stock in bajaj_results[:10]:  # Show top 10
            message += f"• {stock['symbol']}: OB={stock['ob']}, Score={stock['confluence_score']}\n"
        if len(bajaj_results) > 10:
            message += f"... and {len(bajaj_results) - 10} more\n"
        message += f"<i>Total qualified: {len(bajaj_results)}</i>\n\n"
    
    # 3. RSI MULTI-TIMEFRAME
    if rsi_results:
        oversold = [r for r in rsi_results if 'OVERSOLD' in r.get('confluence', '')]
        overbought = [r for r in rsi_results if 'OVERBOUGHT' in r.get('confluence', '')]
        
        if oversold:
            message += "<b>🟢 TRIPLE OVERSOLD (1D+4H+1H):</b>\n"
            for stock in oversold[:5]:
                message += f"• {stock['symbol']}: 1D={stock['1D_RSI']} {stock['1D_SIGNAL']}, "
                message += f"4H={stock['4H_RSI']} {stock['4H_SIGNAL']}, "
                message += f"1H={stock['1H_RSI']} {stock['1H_SIGNAL']}\n"
        
        if overbought:
            message += "<b>🔴 TRIPLE OVERBOUGHT (1D+4H+1H):</b>\n"
            for stock in overbought[:5]:
                message += f"• {stock['symbol']}: 1D={stock['1D_RSI']} {stock['1D_SIGNAL']}, "
                message += f"4H={stock['4H_RSI']} {stock['4H_SIGNAL']}, "
                message += f"1H={stock['1H_RSI']} {stock['1H_SIGNAL']}\n"
        
        message += f"<i>Total triple alignments: {len(rsi_results)}</i>\n\n"
    
    # 4. 4H ENGULFING
    if engulfing_results:
        bullish = [r for r in engulfing_results if r['pattern'] == 'BULLISH']
        bearish = [r for r in engulfing_results if r['pattern'] == 'BEARISH']
        
        if bullish:
            message += "<b>📈 4H BULLISH ENGULFING:</b>\n"
            for stock in bullish[:5]:
                change_emoji = "🟢" if stock['change_pct'] > 0 else "🔴"
                message += f"• {stock['symbol']}: ₹{stock['price']} ({change_emoji}{abs(stock['change_pct']):.2f}%)\n"
        
        if bearish:
            message += "<b>📉 4H BEARISH ENGULFING:</b>\n"
            for stock in bearish[:5]:
                change_emoji = "🔴" if stock['change_pct'] < 0 else "🟢"
                message += f"• {stock['symbol']}: ₹{stock['price']} ({change_emoji}{abs(stock['change_pct']):.2f}%)\n"
        
        message += f"<i>Total engulfing patterns: {len(engulfing_results)}</i>\n\n"
    
    # 5. TOP PICKS (Combined Signals)
    all_signals = {}
    for stock in smc_results + bajaj_results + rsi_results + engulfing_results:
        symbol = stock['symbol']
        if symbol not in all_signals:
            all_signals[symbol] = {'signals': [], 'count': 0}
        
        if 'symbol' in stock:
            all_signals[symbol]['count'] += 1
            if stock in smc_results and stock['confluence_score'] >= 2:
                all_signals[symbol]['signals'].append('SMC⭐')
            elif stock in bajaj_results and stock['ob'] == 'Y':
                all_signals[symbol]['signals'].append('Bajaj⭐')
            elif stock in rsi_results:
                all_signals[symbol]['signals'].append('RSI⭐')
            elif stock in engulfing_results:
                all_signals[symbol]['signals'].append('Engulf⭐')
    
    strong_picks = {k: v for k, v in all_signals.items() if v['count'] >= 2}
    if strong_picks:
        message += "<b>🎯 STRONG PICKS (Multiple Signals):</b>\n"
        for symbol, data in list(strong_picks.items())[:10]:
            message += f"• {symbol}: {', '.join(data['signals'])}\n"
        message += "\n"
    
    # 6. SUMMARY
    message += "<b>📋 EXECUTIVE SUMMARY:</b>\n"
    message += f"• Total stocks analyzed: {total_stocks}\n"
    message += f"• SMC Daily signals: {len(smc_results)}\n"
    message += f"• Bajaj Hourly signals: {len(bajaj_results)}\n"
    message += f"• RSI Triple signals: {len(rsi_results)}\n"
    message += f"• 4H Engulfing signals: {len(engulfing_results)}\n"
    message += f"• Strong multi-signal picks: {len(strong_picks)}\n"
    message += f"• Analysis time: {datetime.now().strftime('%H:%M')}\n"
    
    if not any([smc_results, bajaj_results, rsi_results, engulfing_results]):
        message += "\n<i>⚠️ No strong signals found. Market may be closed or in consolidation.</i>"
    
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
