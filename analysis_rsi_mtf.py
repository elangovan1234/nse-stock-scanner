import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def get_multi_timeframe_data(symbol):
    """Get data for 1D, 4H, and 1H timeframes"""
    data_dict = {}
    
    try:
        # 1D data (60 days)
        daily_data = yf.download(symbol, period="60d", interval="1d", progress=False)
        if not daily_data.empty and len(daily_data) > 20:
            data_dict['1D'] = {
                'open': [float(x) for x in daily_data['Open'].values],
                'high': [float(x) for x in daily_data['High'].values],
                'low': [float(x) for x in daily_data['Low'].values],
                'close': [float(x) for x in daily_data['Close'].values]
            }
        
        # 4H data (30 days)
        four_hour_data = yf.download(symbol, period="30d", interval="4h", progress=False)
        if not four_hour_data.empty and len(four_hour_data) > 20:
            data_dict['4H'] = {
                'open': [float(x) for x in four_hour_data['Open'].values],
                'high': [float(x) for x in four_hour_data['High'].values],
                'low': [float(x) for x in four_hour_data['Low'].values],
                'close': [float(x) for x in four_hour_data['Close'].values]
            }
        
        # 1H data (10 days)
        hourly_data = yf.download(symbol, period="10d", interval="1h", progress=False)
        if not hourly_data.empty and len(hourly_data) > 20:
            data_dict['1H'] = {
                'open': [float(x) for x in hourly_data['Open'].values],
                'high': [float(x) for x in hourly_data['High'].values],
                'low': [float(x) for x in hourly_data['Low'].values],
                'close': [float(x) for x in hourly_data['Close'].values]
            }
        
        return data_dict if data_dict else None
    except:
        return None

def calculate_rsi(data, period=14):
    """Calculate RSI for given data"""
    try:
        close_prices = data['close']
        if len(close_prices) < period + 1:
            return None
        
        deltas = [close_prices[i] - close_prices[i-1] for i in range(1, len(close_prices))]
        
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi_values = []
        
        for i in range(period, len(deltas)):
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        return rsi_values[-1] if rsi_values else None
    except:
        return None

def analyze_rsi_mtf(symbol):
    """Analyze RSI in multiple timeframes"""
    try:
        data_dict = get_multi_timeframe_data(symbol)
        if data_dict is None:
            return None
        
        if not all(tf in data_dict for tf in ['1D', '4H', '1H']):
            return None
        
        results = {'symbol': symbol.replace('.NS', '')}
        
        rsi_values = {}
        rsi_status = {}
        rsi_signals = {}
        
        for timeframe in ['1D', '4H', '1H']:
            rsi_value = calculate_rsi(data_dict[timeframe])
            if rsi_value is None:
                return None
            
            if rsi_value >= 70:
                status = "OVERBOUGHT"
                signal = "🔴"
            elif rsi_value <= 30:
                status = "OVERSOLD"
                signal = "🟢"
            else:
                status = "NEUTRAL"
                signal = "⚪"
            
            rsi_values[timeframe] = round(rsi_value, 2)
            rsi_status[timeframe] = status
            rsi_signals[timeframe] = signal
        
        for timeframe in ['1D', '4H', '1H']:
            results[f'{timeframe}_RSI'] = rsi_values[timeframe]
            results[f'{timeframe}_SIGNAL'] = rsi_signals[timeframe]
        
        statuses = [rsi_status[timeframe] for timeframe in ['1D', '4H', '1H']]
        
        if all(status == "OVERBOUGHT" for status in statuses):
            results['confluence'] = "TRIPLE_OVERBOUGHT"
            results['signal'] = "🔴🔴🔴"
        elif all(status == "OVERSOLD" for status in statuses):
            results['confluence'] = "TRIPLE_OVERSOLD"
            results['signal'] = "🟢🟢🟢"
        else:
            return None
        
        return results
    except:
        return None
