import requests

def fetch_popular_usdt_pairs(top_n=10):
    url = "https://api.kucoin.com/api/v1/market/allTickers"
    resp = requests.get(url)
    data = resp.json()
    if data["code"] != "200000":
        raise Exception("KuCoin API Hatası:", data)
    tickers = data["data"]["ticker"]
    # Sadece USDT pariteleri ve hacme göre sırala
    usdt_pairs = [
        (t["symbolName"], float(t["volValue"])) for t in tickers if t["symbolName"].endswith("-USDT")
    ]
    usdt_pairs.sort(key=lambda x: x[1], reverse=True)
    return [pair for pair, _ in usdt_pairs[:top_n]]

def load_existing_coins(filepath="coinler.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_coins(filepath, coins, overwrite=False):
    mode = "w" if overwrite else "a"
    with open(filepath, mode, encoding="utf-8") as f:
        for coin in coins:
            f.write(coin + "\n")

def main():
    print("Popüler USDT coin listesini güncellemek için iki seçenek:")
    print("1) Sadece yeni coinleri mevcut coinler.txt dosyasına ekle (var olanları silmez)")
    print("2) coinler.txt dosyasını sıfırla ve sadece seçtiğiniz popüler coinleri ekle (tüm eski coinler silinir)")
    secim = input("Seçiminiz (1/2): ").strip()
    if secim not in ("1", "2"):
        print("Geçersiz seçim.")
        return

    try:
        n = int(input("Kaç adet en popüler USDT paritesi eklemek istersiniz? (örn: 10): ").strip())
    except Exception:
        print("Geçersiz sayı girdiniz.")
        return

    populer_coins = fetch_popular_usdt_pairs(n)

    if secim == "2":
        save_coins("coinler.txt", populer_coins, overwrite=True)
        print(f"coinler.txt sıfırlandı ve {len(populer_coins)} coin eklendi:")
        for coin in populer_coins:
            print("-", coin)
    else:
        mevcut_coins = load_existing_coins()
        yeni_eklenecekler = [coin for coin in populer_coins if coin not in mevcut_coins]
        if not yeni_eklenecekler:
            print("Eklenebilecek yeni coin yok. coinler.txt zaten güncel.")
            return
        save_coins("coinler.txt", yeni_eklenecekler, overwrite=False)
        print(f"{len(yeni_eklenecekler)} yeni coin eklendi:")
        for coin in yeni_eklenecekler:
            print("-", coin)

if __name__ == "__main__":
    main()
