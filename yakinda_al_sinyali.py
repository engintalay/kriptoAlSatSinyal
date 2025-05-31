import requests
import pandas as pd
import ta

def get_klines(symbol='BTC-USDT', interval='1hour', limit=100):
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

def calculate_supertrend(df, atr_period=22, multiplier=3.0):
    hl2 = (df['high'] + df['low']) / 2
    atr = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=atr_period).average_true_range()
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=df.index, dtype='bool')
    in_uptrend = True

    for i in range(1, len(df)):
        if df['close'][i] > upper_band[i - 1]:
            in_uptrend = True
        elif df['close'][i] < lower_band[i - 1]:
            in_uptrend = False
        # devam ediyorsa önceki trendi koru
        supertrend.iloc[i] = in_uptrend

    df['SUPERTREND'] = supertrend.ffill().astype(bool)
    return df

def generate_signal(row):
    if row['RSI'] < 30 and row['MACD'] > row['MACD_signal'] and row['SUPERTREND'] == True:
        return 'AL'
    elif row['RSI'] > 70 and row['MACD'] < row['MACD_signal'] and row['SUPERTREND'] == False:
        return 'SAT'
    else:
        return 'BEKLE'

def load_symbols(filepath='coinler.txt'):
    with open(filepath, 'r', encoding='utf-8') as f:
        symbols = [line.strip() for line in f if line.strip()]
    return symbols

def check_recent_buy_signal(symbol='BTC-USDT'):
    df = get_klines(symbol=symbol)
    
    # RSI ve MACD
    rsi = ta.momentum.RSIIndicator(close=df['close'], window=14)
    macd = ta.trend.MACD(close=df['close'])
    df['RSI'] = rsi.rsi()
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    
    # Supertrend hesapla (TradingView ayarları: ATR period=22, multiplier=3)
    df = calculate_supertrend(df, atr_period=22, multiplier=3)

    df = df.dropna()
    df['signal'] = df.apply(generate_signal, axis=1)

    # Zaman bilgisini ekle ve yerel saat (Europe/Istanbul) olarak ayarla
    df['datetime'] = pd.to_datetime(df['time'].astype(int), unit='s', utc=True).dt.tz_convert('Europe/Istanbul')

    # SUPERTREND'i sembole çevir
    df['SUPERTREND_SYMBOL'] = df['SUPERTREND'].map({True: '🟢', False: '🔴'})
    # Sinyali sembole çevir
    signal_map = {'AL': '🟢', 'SAT': '🔴', 'BEKLE': '⚪'}
    df['SIGNAL_SYMBOL'] = df['signal'].map(signal_map)

    # Ortalama değeri ekle
    df['MEAN'] = (df['open'] + df['close'] + df['low'] + df['high']) / 4

    recent_signals = df['signal'].iloc[-5:]
    print(f"\n{symbol} için son 5 mum sinyali:")
    print(df[['datetime', 'open', 'close', 'low', 'high', 'MEAN', 'RSI', 'MACD', 'MACD_signal', 'SUPERTREND_SYMBOL', 'SIGNAL_SYMBOL']]
            .iloc[-5:]
            .rename(columns={
                'SUPERTREND_SYMBOL': 'SUPERTREND',
                'SIGNAL_SYMBOL': 'SIGNAL',
                'open': 'OPEN',
                'close': 'CLOSE',
                'low': 'LOW',
                'high': 'HIGH',
                'MEAN': 'MEAN'
            })
            .to_string(index=True))
    if 'AL' in recent_signals.values:
        print(f"✅ {symbol} için yakın zamanda AL sinyali üretildi.")
    else:
        print(f"❌ {symbol} için yakın zamanda AL sinyali yok.")

if __name__ == "__main__":
    symbols = load_symbols()
    for symbol in symbols:
        check_recent_buy_signal(symbol)
