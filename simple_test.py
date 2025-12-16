#!/usr/bin/env python3
# simple_test.py - ONE MESSAGE ONLY

import os
import asyncio
import time
from datetime import datetime
from telegram import Bot

from stocks_list import STOCKS_LIST
from analysis_smc_1d import analyze_smc_daily
from analysis_bajaj_hourly import analyze_bajaj_hourly
from analysis_rsi_mtf import analyze_rsi_mtf
from analysis_engulfing_4h import analyze_engulfing_4h

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_one_message(message):
    """Send ONE message only"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        return True
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

async def quick_test():
    """Quick test - ONE MESSAGE ONLY"""
    print("🚀 Quick test starting...")
    
    # Test 10 stocks for speed
    test_stocks = STOCKS_LIST[:10]
    results = {'smc': [], 'bajaj': [], 'rsi': [], 'engulfing': []}
    
    for symbol in test_stocks:
        try:
            smc = analyze_smc_daily(symbol)
            if smc: results['smc'].append(smc)
            
            bajaj = analyze_bajaj_hourly(symbol)
            if bajaj: results['bajaj'].append(bajaj)
            
            rsi = analyze_rsi_mtf(symbol)
            if rsi: results['rsi'].append(rsi)
            
            engulf = analyze_engulfing_4h(symbol)
            if engulf: results['engulfing'].append(engulf)
            
            time.sleep(0.2)
        except:
            continue
    
    # Create ONE message
    current_time = datetime.now().strftime('%H:%M:%S')
    
    message = f"<b>🧪 QUICK TEST - {current_time}</b>\n"
    message += "═" * 40 + "\n\n"
    
    message += f"<b>Analyzed:</b> {len(test_stocks)} stocks\n\n"
    
    if results['smc']:
        message += "<b>SMC Daily:</b>\n"
        for r in results['smc'][:3]:
            message += f"• {r['symbol']} (Score: {r['confluence_score']})\n"
    
    if results['rsi']:
        message += "\n<b>RSI MTF:</b>\n"
        for r in results['rsi'][:2]:
            message += f"• {r['symbol']} ({r.get('confluence', 'N/A')})\n"
    
    message += f"\n<b>Signals found:</b> {sum(len(v) for v in results.values())}"
    message += f"\n<b>Time:</b> {current_time}"
    
    # Send ONE message
    await send_one_message(message)
    print("✅ Test complete! One message sent.")

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Set Telegram secrets!")
        exit(1)
    
    asyncio.run(quick_test())
