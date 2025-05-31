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

def save_coins(filepath, coins):
    with open(filepath, "a", encoding="utf-8") as f:
        for coin in coins:
            f.write(coin + "\n")

def main():
    try:
        n = int(input("Kaç adet en popüler USDT paritesi eklemek istersiniz? (örn: 10): ").strip())
    except Exception:
        print("Geçersiz sayı girdiniz.")
        return

    populer_coins = fetch_popular_usdt_pairs(n)
    mevcut_coins = load_existing_coins()
    yeni_eklenecekler = [coin for coin in populer_coins if coin not in mevcut_coins]

    if not yeni_eklenecekler:
        print("Eklenebilecek yeni coin yok. coinler.txt zaten güncel.")
        return

    save_coins("coinler.txt", yeni_eklenecekler)
    print(f"{len(yeni_eklenecekler)} yeni coin eklendi:")
    for coin in yeni_eklenecekler:
        print("-", coin)

if __name__ == "__main__":
    main()
