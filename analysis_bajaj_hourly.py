import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def get_hourly_data(symbol, period="2mo", interval="1h"):
    """Get hourly stock data"""
    try:
        hourly_data = yf.download(symbol, period=period, interval=interval, progress=False)
        if hourly_data.empty or len(hourly_data) < 100:
            return None

        data = {
            'open': [float(x) for x in hourly_data['Open'].values],
            'high': [float(x) for x in hourly_data['High'].values],
            'low': [float(x) for x in hourly_data['Low'].values],
            'close': [float(x) for x in hourly_data['Close'].values]
        }
        return data
    except:
        return None

def calculate_discount_hourly(data):
    """Check if stock is 15% below 2-month high"""
    try:
        all_highs = data['high']
        current_price = data['close'][-1]
        period_high = max(all_highs)
        discount_from_high = (period_high - current_price) / period_high
        return discount_from_high > 0.15
    except:
        return False

def is_swing_low_hourly(data):
    """Check if price is at swing low - hourly"""
    try:
        current_low = data['low'][-1]
        lookback = data['low'][-11:-1]
        if len(lookback) > 0 and current_low <= min(lookback):
            return True
        return False
    except:
        return False

def detect_order_block_hourly(data):
    """Detect Order Blocks - hourly"""
    try:
        for i in range(len(data['close'])-10, max(len(data['close'])-100, 0), -1):
            if data['close'][i] < data['open'][i]:
                bullish_count = 0
                for j in range(i+1, min(i+15, len(data['close']))):
                    if data['close'][j] > data['open'][j]:
                        bullish_count += 1
                    else:
                        break

                if 2 <= bullish_count <= 12:
                    first_bullish_close = data['close'][i+1]
                    last_bullish_close = data['close'][i+bullish_count]
                    rally_pct = (last_bullish_close - first_bullish_close) / first_bullish_close
                    return rally_pct > 0.003
        return False
    except:
        return False

def analyze_bajaj_hourly(symbol):
    """Analyze stock for Bajaj-style setup - HOURLY"""
    try:
        data = get_hourly_data(symbol)
        if data is None:
            return None

        discount_zone = calculate_discount_hourly(data)
        swing_low = is_swing_low_hourly(data)

        if not (discount_zone and swing_low):
            return None

        ob = detect_order_block_hourly(data)
        
        # Calculate confluence score
        confluence_factors = [ob]
        score = sum([1 for factor in confluence_factors if factor])
        
        # Priority score
        priority_score = 0
        if ob: priority_score += 2

        return {
            'symbol': symbol.replace('.NS', ''),
            'discount_zone': 'Y',
            'swing_low': 'Y',
            'ob': 'Y' if ob else 'N',
            'confluence_score': f'{score}/1',
            'priority_score': priority_score
        }
    except:
        return None
