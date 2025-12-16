#!/usr/bin/env python3
# test_run.py - Quick test without market check

import os
import time
from datetime import datetime
from telegram import Bot

from stocks_list import STOCKS_LIST
from analysis_smc_1d import analyze_smc_daily
from analysis_bajaj_hourly import analyze_bajaj_hourly
from analysis_rsi_mtf import analyze_rsi_mtf
from analysis_engulfing_4h import analyze_engulfing_4h

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_message(message):
    """Send message to Telegram"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        return True
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def quick_test():
    """Quick test with only 5 stocks"""
    print("🚀 QUICK TEST STARTING...")
    
    # Test with only 5 stocks for speed
    test_stocks = STOCKS_LIST[:5]
    print(f"Testing with {len(test_stocks)} stocks: {', '.join([s.replace('.NS', '') for s in test_stocks])}")
    
    results = {
        'smc': [], 'bajaj': [], 'rsi': [], 'engulfing': []
    }
    
    for symbol in test_stocks:
        stock_name = symbol.replace('.NS', '')
        print(f"  Analyzing {stock_name}...")
        
        try:
            # SMC Daily
            smc = analyze_smc_daily(symbol)
            if smc:
                results['smc'].append(smc)
            
            # Bajaj Hourly
            bajaj = analyze_bajaj_hourly(symbol)
            if bajaj:
                results['bajaj'].append(bajaj)
            
            # RSI MTF
            rsi = analyze_rsi_mtf(symbol)
            if rsi:
                results['rsi'].append(rsi)
            
            # 4H Engulfing
            engulf = analyze_engulfing_4h(symbol)
            if engulf:
                results['engulfing'].append(engulf)
                
        except Exception as e:
            print(f"    Error: {e}")
            continue
    
    # Create message
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"<b>🧪 QUICK TEST RESULTS</b>\n"
    message += f"<i>Time: {current_time}</i>\n"
    message += "═" * 40 + "\n\n"
    
    message += f"<b>Test Stocks:</b> {', '.join([s.replace('.NS', '') for s in test_stocks])}\n\n"
    
    if results['smc']:
        message += "<b>🎯 SMC Daily Found:</b>\n"
        for r in results['smc'][:3]:
            message += f"• {r['symbol']} (Score: {r['confluence_score']})\n"
    else:
        message += "<b>❌ No SMC Daily signals</b>\n"
    
    message += "\n"
    
    if results['rsi']:
        message += "<b>📊 RSI MTF Found:</b>\n"
        for r in results['rsi'][:3]:
            message += f"• {r['symbol']} ({r['confluence']})\n"
    else:
        message += "<b>❌ No RSI Triple alignments</b>\n"
    
    message += "\n<b>📈 Summary:</b>\n"
    message += f"• SMC Daily: {len(results['smc'])}\n"
    message += f"• Bajaj Hourly: {len(results['bajaj'])}\n"
    message += f"• RSI MTF: {len(results['rsi'])}\n"
    message += f"• 4H Engulfing: {len(results['engulfing'])}\n"
    
    message += "\n<i>⚠️ Quick test completed successfully!</i>"
    
    # Send to Telegram
    print("\n📨 Sending results to Telegram...")
    if send_telegram_message(message):
        print("✅ Telegram message sent!")
    else:
        print("❌ Failed to send to Telegram")
    
    return results

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ ERROR: Set Telegram credentials in GitHub Secrets!")
        exit(1)
    
    quick_test()
