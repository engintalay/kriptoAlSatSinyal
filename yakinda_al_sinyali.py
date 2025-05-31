import requests
import pandas as pd
import ta
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os

APP_VERSION = "1.0.3"
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

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

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

def prepare_table_data(symbol, interval):
    try:
        # Bollinger için en az 44 veri (20 pencere + 24 mum) yükle
        df = get_klines(symbol=symbol, interval=interval, limit=44)
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
    # Grafik için son 100 mumu döndür (en fazla 44 veri olabilir)
    return tablo, df.iloc[-44:] if len(df) >= 44 else df

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

def manage_settings_window(parent, interval_var, update_callback):
    win = tk.Toplevel(parent)
    win.title("Ayarlar")
    win.geometry("300x150")
    win.resizable(False, False)

    tk.Label(win, text="Zaman Aralığı (interval):").pack(pady=10)
    interval_entry = ttk.Combobox(win, values=[
        "1min", "3min", "5min", "15min", "30min", "1hour", "2hour", "4hour", "6hour", "8hour", "12hour", "1day"
    ], state="readonly")
    interval_entry.set(interval_var.get())
    interval_entry.pack()

    def save_and_close():
        interval_var.set(interval_entry.get())
        # Ayarları dosyaya kaydet
        save_settings({"interval": interval_var.get()})
        update_callback()
        win.destroy()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="Kaydet ve Kapat", command=save_and_close).pack(side='left', padx=5)
    tk.Button(btn_frame, text="Vazgeç", command=win.destroy).pack(side='left', padx=5)

def show_about_window(parent):
    about = tk.Toplevel(parent)
    about.title("Hakkında")
    about.geometry("400x220")
    about.resizable(False, False)
    msg = (
        f"kriptoAlSatSinyal v{APP_VERSION}\n\n"
        "Kripto para piyasası için teknik analiz tabanlı sinyal üretimi ve görselleştirme sağlar.\n\n"
        "Geliştirici: Engin Talay\n"
        "Lisans: MIT\n"
        "github.com/engintalay/kriptoAlSatSinyal"
    )
    label = tk.Label(about, text=msg, justify="left", padx=10, pady=10, anchor="w", wraplength=380)
    label.pack(fill="both", expand=True)
    tk.Button(about, text="Kapat", command=about.destroy).pack(pady=10)

def show_tables_in_tabs(symbols):
    tablo_mum_sayilari = []  # tablo_mum_sayilari değişkenini başta tanımla
    root = tk.Tk()
    # Başlık: Her coin için tablo uzunluklarını göster
    tablo_mum_sayilari_str = 24
    root.title(f"Kripto Sinyalleri ({tablo_mum_sayilari_str} mum) v{APP_VERSION}")
    #root.title(f"Kripto Son 5 Mum Sinyalleri v{APP_VERSION}")

    # Ayarları yükle
    settings = load_settings()
    interval_val = settings.get("interval", DEFAULT_INTERVAL)
    interval_var = tk.StringVar(value=interval_val)

    # Menü çubuğu ve coin yönetim ekranı
    def reload_and_refresh(new_symbols=None):
        root.destroy()
        import sys, os
        os.execl(sys.executable, sys.executable, *sys.argv)

    def refresh_data():
        root.destroy()
        import sys, os
        os.execl(sys.executable, sys.executable, *sys.argv)

    def update_interval_and_refresh():
        root.destroy()
        import sys, os
        os.execl(sys.executable, sys.executable, *sys.argv)

    menubar = tk.Menu(root)
    coin_menu = tk.Menu(menubar, tearoff=0)
    coin_menu.add_command(label="Coin Çiftlerini Yönet", command=lambda: manage_coins_window(root, symbols, reload_and_refresh))
    menubar.add_cascade(label="Ayarlar", menu=coin_menu)
    menubar.add_command(label="Zaman Aralığı", command=lambda: manage_settings_window(root, interval_var, update_interval_and_refresh))
    menubar.add_command(label="Verileri Yenile", command=refresh_data)
    menubar.add_command(label="Hakkında", command=lambda: show_about_window(root))
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

    # tablo_mum_sayilari değişkenini başta tanımla
    tablo_mum_sayilari = []

    total = len(symbols)
    for idx, symbol in enumerate(symbols, 1):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=symbol)
        tablo, df_graph = prepare_table_data(symbol, interval_var.get())
        cols = list(tablo.columns)
        # Tabloyu tersten (yeni tarih üstte) göster
        tablo_display = tablo.iloc[::-1].reset_index(drop=True)
        tablo_mum_sayilari.append(len(tablo_display))
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
        tree.tag_configure('supertrend_green', background='#d4fcdc')
        tree.tag_configure('supertrend_red', background='#ffd6d6')
        for _, row in tablo_display.iterrows():
            tags = ()
            if row['SUPERTREND'] == '🟢':
                tags = ('supertrend_green',)
            elif row['SUPERTREND'] == '🔴':
                tags = ('supertrend_red',)
            tree.insert('', 'end', values=[row[col] for col in cols], tags=tags)
        tree.pack(fill='x', expand=False)

        # Mum grafik (candlestick) ekle
        canvas = None
        fig = None
        ax = None
        saatler = None  # <-- saatler değişkenini üst scope'ta tanımla
        if df_graph is not None and not df_graph.empty and 'datetime' in df_graph:
            import matplotlib.dates as mdates
            from matplotlib.patches import Rectangle

            df_candle = df_graph.iloc[-24:]
            bollinger_df = df_graph

            fig, ax = plt.subplots(figsize=(12, 4))
            x = df_candle['datetime']
            opens = df_candle['open']
            closes = df_candle['close']
            highs = df_candle['high']
            lows = df_candle['low']

            # Saat ve tarih bilgisini birleştir
            saatler = df_candle['datetime'].dt.strftime('%Y-%m-%d %H:%M').tolist()
            ax.set_xticks(list(range(len(saatler))))
            ax.set_xticklabels(saatler, rotation=45, fontsize=8)

            width = 0.6
            for i in range(len(df_candle)):
                color = 'green' if closes.iloc[i] >= opens.iloc[i] else 'red'
                ax.add_patch(Rectangle((i - width/2, min(opens.iloc[i], closes.iloc[i])),
                                       width, abs(opens.iloc[i] - closes.iloc[i]),
                                       color=color, alpha=0.7))
                ax.plot([i, i], [lows.iloc[i], highs.iloc[i]], color='black', linewidth=1)

            ax.set_xlim(-1, len(df_candle))
            ax.set_title(f"{symbol} Son 24 Mum (Saatlik) Candlestick")
            ax.set_ylabel("Fiyat")
            ax.grid(True, axis='y')
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill='both', expand=True)
            plt.close(fig)

        # Bollinger Bandı ve MA20 göster/gizle düğmesi
        def toggle_bollinger(ax=ax, fig=fig, canvas=canvas, df_candle=bollinger_df if df_graph is not None and not df_graph.empty else None, saatler=saatler):
            if ax is None or fig is None or canvas is None or df_candle is None or df_candle.empty or saatler is None:
                return
            # Önce eski Bollinger ve MA çizgilerini temizle
            for line in ax.get_lines():
                if hasattr(line, '_is_bollinger') and line._is_bollinger:
                    line.remove()
            for txt in getattr(ax, '_bollinger_texts', []):
                txt.remove()
            ax._bollinger_texts = []

            # Eğer zaten gösteriliyorsa tekrar çizme (toggle)
            if hasattr(ax, '_bollinger_visible') and ax._bollinger_visible:
                ax._bollinger_visible = False
                canvas.draw()
                return

            close = df_candle['close']
            window = 20 if len(close) >= 20 else len(close)
            if window < 2:
                return
            ma = close.rolling(window=window).mean()
            std = close.rolling(window=window).std()
            upper = ma + 2 * std
            lower = ma - 2 * std
            # Sadece son 24 mumun Bollinger ve MA20'sini çiz
            upper_last = upper.iloc[-24:]
            lower_last = lower.iloc[-24:]
            ma_last = ma.iloc[-24:]
            idxs = list(range(len(upper_last)))
            ln1, = ax.plot(idxs, upper_last, color='orange', linestyle='--', label='Bollinger Üst')
            ln2, = ax.plot(idxs, lower_last, color='purple', linestyle='--', label='Bollinger Alt')
            ln3, = ax.plot(idxs, ma_last, color='black', linestyle='-', label='MA20')
            ln1._is_bollinger = True
            ln2._is_bollinger = True
            ln3._is_bollinger = True

            # Saat ile kesişim noktalarındaki değerleri göster
            ax._bollinger_texts = []
            for i in idxs:
                saat = saatler[i]
                val_ma = ma_last.iloc[i]
                val_up = upper_last.iloc[i]
                val_lo = lower_last.iloc[i]
                # MA20
                txt_ma = ax.text(i, val_ma, f"{val_ma:.2f}", color='black', fontsize=7, ha='center', va='bottom', rotation=90)
                # Üst ve alt band
                txt_up = ax.text(i, val_up, f"{val_up:.2f}", color='orange', fontsize=7, ha='center', va='bottom', rotation=90)
                txt_lo = ax.text(i, val_lo, f"{val_lo:.2f}", color='purple', fontsize=7, ha='center', va='top', rotation=90)
                ax._bollinger_texts.extend([txt_ma, txt_up, txt_lo])

            ax._bollinger_visible = True
            ax.legend()
            canvas.draw()

        if canvas is not None:
            btn = tk.Button(frame, text="Bollinger Bandı ve MA20 Göster/Gizle", command=toggle_bollinger)
            btn.pack(pady=5)

        # Progress bar güncelle
        percent = int((idx / total) * 100)
        progress.set(percent)
        progress_label.config(text=f"Yükleniyor... %{percent}")
        root.update_idletasks()

    progress_label.config(text="Yükleme tamamlandı.")
    progress_bar.pack_forget()
    progress_label.pack_forget()

    # Başlık: Her coin için tablo uzunluklarını göster
 #   tablo_mum_sayilari_str = ", ".join([f"{sym}: {count} mum" for sym, count in zip(symbols, tablo_mum_sayilari)])
 #   root.title(f"Kripto Sinyalleri ({tablo_mum_sayilari_str} mum) v{APP_VERSION}")

    root.mainloop()

if __name__ == "__main__":
    symbols = load_symbols()
    show_tables_in_tabs(symbols)
