import requests
import pandas as pd
import ta
import time
import json
import os

DEFAULT_INTERVAL = "1hour"
SETTINGS_FILE = "ayarlar.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def get_klines(symbol='BTC-USDT', interval=DEFAULT_INTERVAL, limit=100):
    url = f"https://api.kucoin.com/api/v1/market/candles?type={interval}&symbol={symbol}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    if data['code'] != "200000":
        raise Exception("API Hatası:", data)
    df = pd.DataFrame(data['data'], columns=[
        'time', 'open', 'close', 'high', 'low', 'volume', 'turnover'
    ])
    df = df.iloc[::-1]
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['open'] = df['open'].astype(float)
    return df

def generate_signals(df):
    rsi = ta.momentum.RSIIndicator(close=df['close'], window=14)
    df['RSI'] = rsi.rsi()
    macd = ta.trend.MACD(close=df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    last = df.iloc[-1]
    if last['RSI'] < 30 and last['MACD'] > last['MACD_signal']:
        return 'AL'
    elif last['RSI'] > 70 and last['MACD'] < last['MACD_signal']:
        return 'SAT'
    else:
        return 'BEKLE'

def load_symbols(filepath='coinler.txt'):
    # Bu fonksiyon tablohazirla.py'den import edilmeli, burada tekrar bulunmamalı.
    from tablohazirla import load_symbols
    return load_symbols(filepath)

def load_interval():
    settings = load_settings()
    return settings.get("interval", DEFAULT_INTERVAL)

# Canlı Döngü
symbols = load_symbols()
interval = load_interval()
while True:
    try:
        for symbol in symbols:
            df = get_klines(symbol=symbol, interval=interval)
            sinyal = generate_signals(df)
            print(f"[{time.strftime('%H:%M:%S')}] {symbol} ({interval}) Sinyal: {sinyal}")
            time.sleep(1)
        time.sleep(60)
    except Exception as e:
        print("Hata:", e)
        time.sleep(10)
