import requests
import pandas as pd
import ta
import time

def get_klines(symbol='BTC-USDT', interval='1min', limit=100):
    url = f"https://api.kucoin.com/api/v1/market/candles?type={interval}&symbol={symbol}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    if data['code'] != "200000":
        raise Exception("API Hatası:", data)

    df = pd.DataFrame(data['data'], columns=[
        'time', 'open', 'close', 'high', 'low', 'volume', 'turnover'
    ])

    df = df.iloc[::-1]  # KuCoin ters sırada döner, düzelt
    df['close'] = df['close'].astype(float)
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
    with open(filepath, 'r', encoding='utf-8') as f:
        symbols = [line.strip() for line in f if line.strip()]
    return symbols

# Canlı Döngü
symbols = load_symbols()
while True:
    try:
        for symbol in symbols:
            df = get_klines(symbol=symbol)
            sinyal = generate_signals(df)
            print(f"[{time.strftime('%H:%M:%S')}] {symbol} Sinyal: {sinyal}")
            time.sleep(1)  # Her coin için kısa bekleme
        time.sleep(60)  # Tüm coinler tamamlanınca 1 dakika bekle
    except Exception as e:
        print("Hata:", e)
        time.sleep(10)
