import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def get_stock_data(symbol, period="1y", interval="1d"):
    """Get stock data from Yahoo Finance"""
    try:
        stock = yf.download(symbol, period=period, interval=interval, progress=False)
        if stock.empty or len(stock) < 100:
            return None

        data = {
            'open': [float(x) for x in stock['Open'].values],
            'high': [float(x) for x in stock['High'].values],
            'low': [float(x) for x in stock['Low'].values],
            'close': [float(x) for x in stock['Close'].values],
            'volume': [float(x) for x in stock['Volume'].values]
        }
        return data
    except:
        return None

def calculate_discount_zone(data):
    """Check if stock is 35% below 52-week high"""
    try:
        all_highs = data['high']
        all_lows = data['low']
        current_price = data['close'][-1]

        year_high = max(all_highs)
        year_low = min(all_lows)

        if year_high == year_low:
            return False

        discount_from_high = (year_high - current_price) / year_high
        return discount_from_high >= 0.35
    except:
        return False

def is_swing_low(data, window=5):
    """Check if current price is at swing low"""
    try:
        current_low = data['low'][-1]
        lookback_data = data['low'][-window-1:-1]
        lookforward_min = min(data['low'][-1:])

        if len(data['low']) >= window + 1:
            if current_low <= min(lookback_data) and current_low <= lookforward_min:
                return True
        return False
    except:
        return False

def detect_order_block(data):
    """Detect Order Blocks"""
    try:
        for i in range(len(data['close'])-6, max(len(data['close'])-25, 0), -1):
            if data['close'][i] < data['open'][i]:
                bullish_count = 0
                for j in range(i+1, min(i+6, len(data['close']))):
                    if data['close'][j] > data['open'][j]:
                        bullish_count += 1
                    else:
                        break

                if 3 <= bullish_count <= 5:
                    first_bullish_close = data['close'][i+1]
                    last_bullish_close = data['close'][i+bullish_count]
                    rally_pct = (last_bullish_close - first_bullish_close) / first_bullish_close
                    return rally_pct > 0.006
        return False
    except:
        return False

def detect_fair_value_gap(data):
    """Detect Fair Value Gap"""
    try:
        for i in range(len(data['close'])-7, max(len(data['close'])-15, 0), -1):
            bullish_count = 0
            end_index = min(i+6, len(data['close'])-1)
            for j in range(i, end_index):
                if data['close'][j] > data['open'][j]:
                    bullish_count += 1
                else:
                    break

            if 3 <= bullish_count <= 6:
                next_candle_idx = i + bullish_count
                if next_candle_idx < len(data['close']):
                    return data['close'][next_candle_idx] < data['open'][next_candle_idx]
        return False
    except:
        return False

def check_volume_spike(data):
    """Check if volume is 2x average volume"""
    try:
        if len(data['volume']) < 10:
            return False

        current_volume = data['volume'][-1]
        recent_volumes = data['volume'][-10:]
        avg_volume = sum(recent_volumes) / len(recent_volumes)

        if avg_volume == 0:
            return False

        return current_volume >= avg_volume * 2.0
    except:
        return False

def analyze_smc_daily(symbol):
    """Complete SMC analysis for daily timeframe"""
    try:
        data = get_stock_data(symbol, period="1y", interval="1d")
        if data is None:
            return None

        discount_zone = calculate_discount_zone(data)
        swing_low = is_swing_low(data)
        order_block = detect_order_block(data)
        fvg = detect_fair_value_gap(data)
        volume_spike = check_volume_spike(data)

        if discount_zone and swing_low:
            return {
                'symbol': symbol.replace('.NS', ''),
                'discount_zone': 'Y',
                'swing_low': 'Y',
                'order_block': 'Y' if order_block else 'N',
                'fvg': 'Y' if fvg else 'N',
                'volume_spike': 'Y' if volume_spike else 'N',
                'confluence_score': sum([1 for x in [order_block, fvg, volume_spike] if x])
            }
        return None
    except:
        return None
