import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import yfinance as yf

def ema(series, span):
    """Calculate Exponential Moving Average"""
    return series.ewm(span=span, adjust=False).mean()

def rsi(series, period=14):
    """Calculate Relative Strength Index"""
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    avg_gain = up.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = down.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def macd(series, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def stochastic(high, low, close, k_period=14, d_period=3):
    """Calculate Stochastic Oscillator"""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k_line = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d_line = k_line.rolling(window=d_period).mean()
    return k_line, d_line

def support_resistance(df, window=20):
    """Calculate Support and Resistance levels"""
    recent = df["Close"].tail(window)
    support = recent.min()
    resistance = recent.max()
    return float(support), float(resistance)

def bollinger_bands(series, window=20, num_std=2):
    """Calculate Bollinger Bands"""
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return lower_band, sma, upper_band

def atr(high, low, close, period=14):
    """Calculate Average True Range"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_val = tr.rolling(window=period).mean()
    return atr_val

def volume_analysis(df, window=20):
    """Analyze volume trends"""
    avg_volume = df["Volume"].rolling(window=window).mean()
    volume_ratio = df["Volume"].iloc[-1] / avg_volume.iloc[-1] if avg_volume.iloc[-1] > 0 else 1
    return float(volume_ratio)

def calculate_ai_score(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate AI confidence score based on multiple indicators
    Returns score 0-100 and detailed breakdown
    """
    if df is None or df.empty or len(df) < 50:
        return {
            "signal": "NO_DATA",
            "confidence": 0,
            "reason": "Insufficient data for analysis",
            "breakdown": {}
        }

    df = df.copy()
    
    # Calculate indicators
    df["EMA20"] = ema(df["Close"], 20)
    df["EMA50"] = ema(df["Close"], 50)
    df["EMA200"] = ema(df["Close"], 200)
    df["RSI14"] = rsi(df["Close"], 14)
    
    macd_line, signal_line, hist = macd(df["Close"])
    df["MACD"] = macd_line
    df["MACD_SIGNAL"] = signal_line
    df["MACD_HIST"] = hist
    
    k_line, d_line = stochastic(df["High"], df["Low"], df["Close"])
    df["STOCH_K"] = k_line
    df["STOCH_D"] = d_line
    
    lower_band, mid_band, upper_band = bollinger_bands(df["Close"])
    df["BB_LOWER"] = lower_band
    df["BB_MIDDLE"] = mid_band
    df["BB_UPPER"] = upper_band
    
    df["ATR"] = atr(df["High"], df["Low"], df["Close"])
    
    # Get latest values
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    
    # Calculate component scores (0-100 each)
    scores = {}
    
    # Trend Score (EMA alignment)
    if last["Close"] > last["EMA20"] > last["EMA50"] > last["EMA200"]:
        scores["trend"] = 100
    elif last["Close"] > last["EMA20"] > last["EMA50"]:
        scores["trend"] = 80
    elif last["Close"] > last["EMA20"]:
        scores["trend"] = 60
    elif last["Close"] < last["EMA20"] < last["EMA50"] < last["EMA200"]:
        scores["trend"] = 0
    elif last["Close"] < last["EMA20"] < last["EMA50"]:
        scores["trend"] = 20
    elif last["Close"] < last["EMA20"]:
        scores["trend"] = 40
    else:
        scores["trend"] = 50
    
    # RSI Score
    rsi_val = float(last["RSI14"])
    if 40 <= rsi_val <= 60:
        scores["rsi"] = 50
    elif 30 < rsi_val < 70:
        scores["rsi"] = 60
    elif rsi_val <= 30:
        scores["rsi"] = 80
    elif rsi_val >= 70:
        scores["rsi"] = 20
    else:
        scores["rsi"] = 40
    
    # MACD Score
    if last["MACD"] > last["MACD_SIGNAL"] and last["MACD_HIST"] > 0:
        scores["macd"] = 80
    elif last["MACD"] > last["MACD_SIGNAL"]:
        scores["macd"] = 60
    elif last["MACD"] < last["MACD_SIGNAL"] and last["MACD_HIST"] < 0:
        scores["macd"] = 20
    else:
        scores["macd"] = 40
    
    # Stochastic Score
    stoch_k = float(last["STOCH_K"]) if pd.notna(last["STOCH_K"]) else 50
    if stoch_k < 20:
        scores["stochastic"] = 80
    elif stoch_k > 80:
        scores["stochastic"] = 20
    else:
        scores["stochastic"] = 50 + (stoch_k - 50) / 3
    
    # Volume Score
    vol_ratio = volume_analysis(df)
    scores["volume"] = min(100, 50 + (vol_ratio - 1) * 25)
    
    # Price Action Score
    if last["Close"] > prev["Close"]:
        scores["price_action"] = 70
    elif last["Close"] < prev["Close"]:
        scores["price_action"] = 30
    else:
        scores["price_action"] = 50
    
    # Calculate weighted average
    weights = {
        "trend": 0.30,
        "rsi": 0.20,
        "macd": 0.20,
        "stochastic": 0.15,
        "volume": 0.10,
        "price_action": 0.05
    }
    
    weighted_score = sum(scores[key] * weights[key] for key in weights)
    
    # Determine signal
    if weighted_score >= 65:
        signal = "BUY"
    elif weighted_score <= 35:
        signal = "SELL"
    else:
        signal = "WAIT"
    
    # Confidence
    if signal == "BUY":
        confidence = min(95, 50 + (weighted_score - 65) * 3)
    elif signal == "SELL":
        confidence = min(95, 50 + (35 - weighted_score) * 3)
    else:
        confidence = max(20, 50 - abs(weighted_score - 50) / 2)
    
    support, resistance = support_resistance(df)
    
    # Generate reason
    reason_parts = []
    if scores["trend"] > 60:
        reason_parts.append("Strong uptrend")
    elif scores["trend"] < 40:
        reason_parts.append("Strong downtrend")
    else:
        reason_parts.append("Mixed trend")
    
    if scores["rsi"] >= 70:
        reason_parts.append("RSI oversold")
    elif scores["rsi"] <= 30:
        reason_parts.append("RSI overbought")
    
    if scores["macd"] > 60:
        reason_parts.append("MACD bullish")
    elif scores["macd"] < 40:
        reason_parts.append("MACD bearish")
    
    if vol_ratio > 1.5:
        reason_parts.append("Strong volume")
    
    reason = " | ".join(reason_parts)
    
    return {
        "signal": signal,
        "confidence": float(round(confidence, 2)),
        "reason": reason,
        "price": float(round(last["Close"], 4)),
        "ema20": float(round(last["EMA20"], 4)),
        "ema50": float(round(last["EMA50"], 4)),
        "ema200": float(round(last["EMA200"], 4)),
        "rsi14": float(round(last["RSI14"], 2)),
        "macd": float(round(last["MACD"], 4)),
        "macd_signal": float(round(last["MACD_SIGNAL"], 4)),
        "stoch_k": float(round(last["STOCH_K"], 2)) if pd.notna(last["STOCH_K"]) else None,
        "stoch_d": float(round(last["STOCH_D"], 2)) if pd.notna(last["STOCH_D"]) else None,
        "bb_upper": float(round(last["BB_UPPER"], 4)) if pd.notna(last["BB_UPPER"]) else None,
        "bb_middle": float(round(last["BB_MIDDLE"], 4)) if pd.notna(last["BB_MIDDLE"]) else None,
        "bb_lower": float(round(last["BB_LOWER"], 4)) if pd.notna(last["BB_LOWER"]) else None,
        "atr": float(round(last["ATR"], 4)) if pd.notna(last["ATR"]) else None,
        "support": support,
        "resistance": resistance,
        "trend": "Bullish" if scores["trend"] > 60 else "Bearish" if scores["trend"] < 40 else "Neutral",
        "volume_ratio": float(round(vol_ratio, 2)),
        "breakdown": {
            "trend_score": float(round(scores["trend"], 2)),
            "rsi_score": float(round(scores["rsi"], 2)),
            "macd_score": float(round(scores["macd"], 2)),
            "stochastic_score": float(round(scores["stochastic"], 2)),
            "volume_score": float(round(scores["volume"], 2)),
            "price_action_score": float(round(scores["price_action"], 2)),
            "weighted_score": float(round(weighted_score, 2))
        }
    }

def analyze_chart(symbol: str, interval: str = "1d", period: str = "1y") -> Dict[str, Any]:
    """Fetch data and analyze chart for given symbol"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            return {
                "signal": "NO_DATA",
                "confidence": 0,
                "reason": f"No data found for {symbol}"
            }
        
        data = data.reset_index()
        data = data.rename(columns={
            "Date": "Date",
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Volume": "Volume"
        })
        
        return calculate_ai_score(data)
        
    except Exception as e:
        return {
            "signal": "ERROR",
            "confidence": 0,
            "reason": f"Error analyzing {symbol}: {str(e)}"
        }
