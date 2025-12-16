#!/usr/bin/env python3
# test_now.py - FIXED VERSION with async support

import os
import sys
import asyncio
import time
from datetime import datetime

# Add current directory to path
sys.path.append('.')

# Import your modules
try:
    from stocks_list import STOCKS_LIST
    from analysis_smc_1d import analyze_smc_daily
    from analysis_bajaj_hourly import analyze_bajaj_hourly
    from analysis_rsi_mtf import analyze_rsi_mtf
    from analysis_engulfing_4h import analyze_engulfing_4h
    print("✅ Modules imported successfully")
except Exception as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ ERROR: Telegram credentials not found in environment!")
    print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
    sys.exit(1)

# Import telegram AFTER checking credentials
from telegram import Bot

async def send_telegram_async(message):
    """Send message to Telegram (async version)"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        print("✅ Telegram message sent!")
        return True
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def send_telegram_sync(message):
    """Send message to Telegram (sync wrapper)"""
    return asyncio.run(send_telegram_async(message))

async def test_telegram_connection():
    """Test Telegram connection (async)"""
    print("\n🔗 Testing Telegram connection...")
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username}")
        return True
    except Exception as e:
        print(f"❌ Cannot connect to Telegram: {e}")
        return False

def run_quick_analysis():
    """Run quick analysis on 5 stocks (synchronous)"""
    print("\n📊 Running quick analysis...")
    
    # Use only 3 stocks for speed
    test_stocks = STOCKS_LIST[:3]
    print(f"Analyzing: {', '.join([s.replace('.NS', '') for s in test_stocks])}")
    
    results = {
        'smc': [], 'bajaj': [], 'rsi': [], 'engulfing': []
    }
    
    for symbol in test_stocks:
        stock_name = symbol.replace('.NS', '')
        print(f"  → {stock_name}: ", end="", flush=True)
        
        try:
            # Try each analysis
            signals = []
            
            # SMC
            smc = analyze_smc_daily(symbol)
            if smc:
                results['smc'].append(smc)
                signals.append("SMC")
            
            # Bajaj
            bajaj = analyze_bajaj_hourly(symbol)
            if bajaj:
                results['bajaj'].append(bajaj)
                signals.append("Bajaj")
            
            # RSI
            rsi = analyze_rsi_mtf(symbol)
            if rsi:
                results['rsi'].append(rsi)
                signals.append("RSI")
            
            # Engulfing
            engulf = analyze_engulfing_4h(symbol)
            if engulf:
                results['engulfing'].append(engulf)
                signals.append("Engulf")
            
            if signals:
                print(f"Found: {', '.join(signals)}")
            else:
                print("No signals")
                
        except Exception as e:
            print(f"Error: {str(e)[:50]}")
            continue
        
        # Small delay
        time.sleep(0.5)
    
    return results

def create_message(results):
    """Create Telegram message from results"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"<b>🚀 TEST RUN COMPLETE</b>\n"
    message += f"<i>Time: {current_time}</i>\n"
    message += "═" * 40 + "\n\n"
    
    message += "<b>📈 ANALYSIS RESULTS:</b>\n\n"
    
    # SMC Results
    if results['smc']:
        message += "🎯 <b>SMC Daily:</b>\n"
        for r in results['smc'][:3]:
            signals = []
            if r['order_block'] == 'Y': signals.append('OB')
            if r['fvg'] == 'Y': signals.append('FVG')
            if r['volume_spike'] == 'Y': signals.append('VOLx2')
            message += f"• {r['symbol']} (Score: {r['confluence_score']}/3)\n"
    else:
        message += "🎯 <b>SMC Daily:</b> No signals\n"
    
    # RSI Results
    if results['rsi']:
        message += "\n📊 <b>RSI MTF:</b>\n"
        for r in results['rsi'][:2]:
            signal = "🟢 OVERSOLD" if "OVERSOLD" in r.get('confluence', '') else "🔴 OVERBOUGHT"
            message += f"• {r['symbol']} {signal}\n"
    else:
        message += "\n📊 <b>RSI MTF:</b> No triple alignments\n"
    
    # Summary
    message += "\n<b>📋 SUMMARY:</b>\n"
    message += f"• Stocks analyzed: 3\n"
    message += f"• SMC signals: {len(results['smc'])}\n"
    message += f"• Bajaj signals: {len(results['bajaj'])}\n"
    message += f"• RSI signals: {len(results['rsi'])}\n"
    message += f"• Engulfing signals: {len(results['engulfing'])}\n"
    
    message += "\n<i>✅ Test completed successfully!</i>"
    
    return message

async def async_main():
    """Main async function"""
    print("=" * 60)
    print("🚀 NSE STOCK ANALYSIS - FORCE TEST RUN")
    print("=" * 60)
    
    # Test Telegram connection first
    if not await test_telegram_connection():
        # Try to send error message anyway
        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text="❌ <b>TEST ERROR</b>\n\nCould not connect to Telegram bot. Please check credentials.",
                parse_mode='HTML'
            )
        except:
            pass
        return
    
    # Send initial test message
    await send_telegram_async("🤖 <b>TEST STARTED</b>\nBeginning analysis now...")
    
    # Run analysis (synchronous, so run in thread)
    print("\n📊 Starting stock analysis...")
    results = run_quick_analysis()
    
    # Create and send results
    message = create_message(results)
    await send_telegram_async(message)
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE! Check Telegram for results.")
    print("=" * 60)

def main():
    """Main synchronous wrapper"""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
