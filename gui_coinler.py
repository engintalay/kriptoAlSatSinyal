import tkinter as tk

def manage_coins_window(parent, symbols, update_callback):
    win = tk.Toplevel(parent)
    win.title("Coin Çiftlerini Yönet")
    win.geometry("400x420")
    win.resizable(False, False)

    tk.Label(win, text="coinler.txt içeriği (her satıra bir coin çifti):").pack(pady=5)
    text = tk.Text(win, width=35, height=14)
    text.pack(padx=10)
    text.insert('1.0', "\n".join(symbols))

    def save_and_close():
        new_symbols = [line.strip() for line in text.get('1.0', 'end').splitlines() if line.strip()]
        with open('coinler.txt', 'w', encoding='utf-8') as f:
            for sym in new_symbols:
                f.write(sym + '\n')
        update_callback(new_symbols)
        win.destroy()

    def add_popular_coins():
        from tablohazirla import fetch_popular_usdt_pairs
        import tkinter.messagebox as mbox
        try:
            n = int(entry_popular_count.get())
        except Exception:
            mbox.showerror("Hata", "Lütfen geçerli bir sayı girin.")
            return
        try:
            populer_coins = fetch_popular_usdt_pairs(n)
        except Exception as e:
            mbox.showerror("KuCoin API Hatası", str(e))
            return
        mevcut_coins = set([line.strip() for line in text.get('1.0', 'end').splitlines() if line.strip()])
        yeni_eklenecekler = [coin for coin in populer_coins if coin not in mevcut_coins]
        if not yeni_eklenecekler:
            mbox.showinfo("Bilgi", "Eklenebilecek yeni coin yok. coinler.txt zaten güncel.")
            return
        if mevcut_coins and not text.get('end-2c') == '\n':
            text.insert('end', '\n')
        for coin in yeni_eklenecekler:
            text.insert('end', coin + '\n')
        mbox.showinfo("Başarılı", f"{len(yeni_eklenecekler)} yeni coin eklendi.")

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Kaydet ve Kapat", command=save_and_close).pack(side='left', padx=5)
    tk.Button(btn_frame, text="Vazgeç", command=win.destroy).pack(side='left', padx=5)

    pop_frame = tk.LabelFrame(win, text="KuCoin'den Popüler USDT Coin Ekle", padx=8, pady=8)
    pop_frame.pack(padx=10, pady=10, fill='x')
    tk.Label(pop_frame, text="Kaç adet eklemek istersiniz?").pack(side='left')
    entry_popular_count = tk.Entry(pop_frame, width=5)
    entry_popular_count.insert(0, "10")
    entry_popular_count.pack(side='left', padx=5)
    tk.Button(pop_frame, text="Ekle", command=add_popular_coins).pack(side='left', padx=5)
