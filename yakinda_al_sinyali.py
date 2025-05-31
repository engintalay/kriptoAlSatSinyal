import requests
import pandas as pd
import ta
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

def prepare_table_data(symbol):
    try:
        df = get_klines(symbol=symbol)
    except Exception as e:
        # API hatası varsa boş tablo döndür
        tablo = pd.DataFrame([{
            'datetime': '',
            'OPEN': '',
            'CLOSE': '',
            'LOW': '',
            'HIGH': '',
            'MEAN': '',
            'RSI': '',
            'MACD': '',
            'MACD_signal': '',
            'SUPERTREND': '❌',
            'SIGNAL': '❌'
        }])
        tablo.columns = ['datetime', 'OPEN', 'CLOSE', 'LOW', 'HIGH', 'MEAN', 'RSI', 'MACD', 'MACD_signal', 'SUPERTREND', 'SIGNAL']
        tablo.iloc[0, 0] = f"{symbol} için veri yok"
        return tablo, None
    rsi = ta.momentum.RSIIndicator(close=df['close'], window=14)
    macd = ta.trend.MACD(close=df['close'])
    df['RSI'] = rsi.rsi()
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df = calculate_supertrend(df, atr_period=22, multiplier=3)
    df = df.dropna()
    df['signal'] = df.apply(generate_signal, axis=1)
    df['datetime'] = pd.to_datetime(df['time'].astype(int), unit='s', utc=True).dt.tz_convert('Europe/Istanbul')
    df['SUPERTREND_SYMBOL'] = df['SUPERTREND'].map({True: '🟢', False: '🔴'})
    signal_map = {'AL': '🟢', 'SAT': '🔴', 'BEKLE': '⚪'}
    df['SIGNAL_SYMBOL'] = df['signal'].map(signal_map)
    df['MEAN'] = (df['open'] + df['close'] + df['low'] + df['high']) / 4
    tablo = df[['datetime', 'open', 'close', 'low', 'high', 'MEAN', 'RSI', 'MACD', 'MACD_signal', 'SUPERTREND_SYMBOL', 'SIGNAL_SYMBOL']].iloc[-24:]
    tablo = tablo.rename(columns={
        'SUPERTREND_SYMBOL': 'SUPERTREND',
        'SIGNAL_SYMBOL': 'SIGNAL',
        'open': 'OPEN',
        'close': 'CLOSE',
        'low': 'LOW',
        'high': 'HIGH',
        'MEAN': 'MEAN'
    })
    # Grafik için son 100 mumu döndür
    return tablo, df.iloc[-100:] if len(df) >= 100 else df

def manage_coins_window(parent, symbols, update_callback):
    win = tk.Toplevel(parent)
    win.title("Coin Çiftlerini Yönet")
    win.geometry("350x350")
    win.resizable(False, False)

    tk.Label(win, text="coinler.txt içeriği (her satıra bir coin çifti):").pack(pady=5)
    text = tk.Text(win, width=30, height=12)
    text.pack(padx=10)
    text.insert('1.0', "\n".join(symbols))

    def save_and_close():
        new_symbols = [line.strip() for line in text.get('1.0', 'end').splitlines() if line.strip()]
        with open('coinler.txt', 'w', encoding='utf-8') as f:
            for sym in new_symbols:
                f.write(sym + '\n')
        update_callback(new_symbols)
        win.destroy()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Kaydet ve Kapat", command=save_and_close).pack(side='left', padx=5)
    tk.Button(btn_frame, text="Vazgeç", command=win.destroy).pack(side='left', padx=5)

def show_tables_in_tabs(symbols):
    root = tk.Tk()
    root.title("Kripto Son 5 Mum Sinyalleri")

    # Menü çubuğu ve coin yönetim ekranı
    def reload_and_refresh(new_symbols=None):
        root.destroy()
        # Uygulamayı yeniden başlat
        import sys, os
        os.execl(sys.executable, sys.executable, *sys.argv)

    menubar = tk.Menu(root)
    coin_menu = tk.Menu(menubar, tearoff=0)
    coin_menu.add_command(label="Coin Çiftlerini Yönet", command=lambda: manage_coins_window(root, symbols, reload_and_refresh))
    menubar.add_cascade(label="Ayarlar", menu=coin_menu)
    root.config(menu=menubar)

    # Progress bar ekle
    progress = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress, maximum=100)
    progress_bar.pack(fill='x', padx=10, pady=5)
    progress_label = tk.Label(root, text="Yükleniyor... %0")
    progress_label.pack()

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    style = ttk.Style()
    style.theme_use("default")
    style.map("Treeview", background=[('selected', '#ececec')])

    total = len(symbols)
    for idx, symbol in enumerate(symbols, 1):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=symbol)
        tablo, df_graph = prepare_table_data(symbol)
        cols = list(tablo.columns)
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
        tree.tag_configure('supertrend_green', background='#d4fcdc')
        tree.tag_configure('supertrend_red', background='#ffd6d6')
        for _, row in tablo.iterrows():
            tags = ()
            if row['SUPERTREND'] == '🟢':
                tags = ('supertrend_green',)
            elif row['SUPERTREND'] == '🔴':
                tags = ('supertrend_red',)
            tree.insert('', 'end', values=[row[col] for col in cols], tags=tags)
        tree.pack(fill='x', expand=False)

        # Mum grafik (candlestick) ekle
        if df_graph is not None and not df_graph.empty and 'datetime' in df_graph:
            import matplotlib.dates as mdates
            from matplotlib.patches import Rectangle

            fig, ax = plt.subplots(figsize=(10, 3))
            # Son 24 mum için
            df_candle = df_graph.iloc[-24:]
            x = df_candle['datetime']
            opens = df_candle['open']
            closes = df_candle['close']
            highs = df_candle['high']
            lows = df_candle['low']

            # X eksenini saat olarak ayarla
            saatler = df_candle['datetime'].dt.strftime('%H:%M').tolist()
            ax.set_xticks(list(range(len(saatler))))
            ax.set_xticklabels(saatler, rotation=45)

            width = 0.6
            for i in range(len(df_candle)):
                color = 'green' if closes.iloc[i] >= opens.iloc[i] else 'red'
                # Gövde
                ax.add_patch(Rectangle((i - width/2, min(opens.iloc[i], closes.iloc[i])),
                                       width, abs(opens.iloc[i] - closes.iloc[i]),
                                       color=color, alpha=0.7))
                # Fitil
                ax.plot([i, i], [lows.iloc[i], highs.iloc[i]], color='black', linewidth=1)

            ax.set_xlim(-1, len(df_candle))
            ax.set_title(f"{symbol} Son 24 Mum (Saatlik) Candlestick")
            ax.set_ylabel("Fiyat")
            ax.grid(True, axis='y')
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            plt.close(fig)

        # Progress bar güncelle
        percent = int((idx / total) * 100)
        progress.set(percent)
        progress_label.config(text=f"Yükleniyor... %{percent}")
        root.update_idletasks()

    progress_label.config(text="Yükleme tamamlandı.")
    progress_bar.pack_forget()
    progress_label.pack_forget()

    root.mainloop()

if __name__ == "__main__":
    symbols = load_symbols()
    show_tables_in_tabs(symbols)
