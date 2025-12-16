import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def get_4h_data(symbol, period="2mo"):
    """Get 4-hour stock data"""
    try:
        stock = yf.download(symbol, period=period, interval="4h", progress=False)
        if stock.empty or len(stock) < 20:
            return None

        data = {
            'open': [float(x) for x in stock['Open'].values],
            'high': [float(x) for x in stock['High'].values],
            'low': [float(x) for x in stock['Low'].values],
            'close': [float(x) for x in stock['Close'].values]
        }
        return data
    except:
        return None

def is_engulfing_candle_4h(data):
    """Check for engulfing candle pattern in 4H"""
    try:
        if len(data['close']) < 3:
            return False, None

        prev_open = data['open'][-2]
        prev_high = data['high'][-2]
        prev_low = data['low'][-2]
        prev_close = data['close'][-2]

        before_prev_open = data['open'][-3]
        before_prev_high = data['high'][-3]
        before_prev_low = data['low'][-3]
        before_prev_close = data['close'][-3]

        engulfing_body_low = min(prev_open, prev_close)
        engulfing_body_high = max(prev_open, prev_close)
        engulfed_body_low = min(before_prev_open, before_prev_close)
        engulfed_body_high = max(before_prev_open, before_prev_close)

        # Bullish engulfing
        if (prev_close > prev_open and
            before_prev_close < before_prev_open and
            engulfing_body_low <= engulfed_body_low and
            engulfing_body_high >= engulfed_body_high and
            prev_low <= before_prev_low and
            prev_high >= before_prev_high):
            return True, 'BULLISH'

        # Bearish engulfing
        if (prev_close < prev_open and
            before_prev_close > before_prev_open and
            engulfing_body_low <= engulfed_body_low and
            engulfing_body_high >= engulfed_body_high and
            prev_low <= before_prev_low and
            prev_high >= before_prev_high):
            return True, 'BEARISH'

        return False, None
    except:
        return False, None

def analyze_engulfing_4h(symbol):
    """Analyze stock for 4H engulfing patterns"""
    try:
        data = get_4h_data(symbol)
        if data is None:
            return None

        has_engulfing, pattern_type = is_engulfing_candle_4h(data)

        if not has_engulfing:
            return None

        current_price = data['close'][-1]
        prev_close = data['close'][-2]
        price_change = ((current_price - prev_close) / prev_close) * 100

        return {
            'symbol': symbol.replace('.NS', ''),
            'pattern': pattern_type,
            'price': round(current_price, 2),
            'change_pct': round(price_change, 2)
        }
    except:
        return None
