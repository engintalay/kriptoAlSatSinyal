# kriptoAlSatSinyal v1.0.3

## Overview
This project generates trading signals for multiple cryptocurrencies using technical indicators such as RSI, MACD, and SuperTrend. It supports both command-line and graphical (tabbed) viewing of recent signals and candlestick data. You can also manage the list of coin pairs and time interval from within the graphical application.

## Files
- **sinyalUretici.py**: Main logic for fetching market data, calculating indicators, and generating trading signals for multiple coins. Uses `ayarlar.json` for interval/timeframe.
- **yakinda_al_sinyali.py**: Shows the last 24 candles' indicator values and signals for all coins in a tabbed GUI, with candlestick charts, Bollinger Bands/MA20, coin pair management, and interval settings. The window title displays the number of rows for each coin.
    - **YENİ:** Coin çiftlerini yönet ekranına, KuCoin'den popüler USDT coinlerini doğrudan ekleyebileceğiniz bir arayüz eklendi. Artık coin ekleme işlemini uygulama içinden kolayca yapabilirsiniz.
- **kucoin_populer_usdt_ekle.py**: Adds the most popular USDT pairs from KuCoin to `coinler.txt`. You can choose to append only new coins or completely reset the list.
- **requirements.txt**: Lists the necessary Python libraries for the project.
- **install.sh**: Shell script to automate installation on Linux/macOS.
- **install.bat**: Batch script to automate installation on Windows.
- **run.sh**: Shell script to run the main signal generator.
- **run.bat**: Batch script to run the main signal generator on Windows.
- **coinler.txt**: List of coin pairs to monitor (one per line).
- **ayarlar.json**: Stores the selected time interval for the GUI and terminal applications.

## Installation Instructions

### 1. Clone the repository:
```sh
git clone <repository-url>
cd kriptoAlSatSinyal
```

### 2. Install dependencies

#### Linux/macOS:
```sh
bash install.sh
```

#### Windows:
```bat
install.bat
```

## Usage

### Terminal Sinyal Üretici (Tüm coinler için):
```sh
python sinyalUretici.py
```
- Tüm coinler için seçili zaman aralığında (interval) sinyal üretir.
- Zaman aralığı ayarı için önce GUI uygulamasından "Zaman Aralığı" menüsünü kullanarak ayar yapabilirsiniz.

### Grafiksel Tablo ve Mum Grafiği (Tüm coinler için):
```sh
python yakinda_al_sinyali.py
```
- Her coin için son 24 mum, teknik göstergeler ve sinyal tablosu sekmelerde gösterilir.
- Her sekmede ayrıca son 24 mum için candlestick grafik ve Bollinger Bantları/MA20 (düğme ile açılıp kapatılabilir) yer alır.
- Yükleme sırasında ilerleme çubuğu gösterilir.
- Menüden "Ayarlar > Coin Çiftlerini Yönet" ile coinler.txt dosyasını uygulama içinden düzenleyebilirsiniz.
- Menüden "Zaman Aralığı" ile mum verisi intervalini seçebilir ve ayarlar.json dosyasına kaydedebilirsiniz.
- Menüden "Verileri Yenile" ile verileri güncelleyebilirsiniz.
- Menüden "Hakkında" ile uygulama ve geliştirici hakkında bilgi alabilirsiniz.
- Uygulama başlığında her coin için tabloya eklenen mum sayısı gösterilir.
- **YENİ:** "Ayarlar > Coin Çiftlerini Yönet" ekranında, "KuCoin'den Popüler USDT Coin Ekle" bölümü ile popüler coinleri doğrudan ekleyebilirsiniz.

### KuCoin'den En Popüler USDT Coinlerini coinler.txt'ye Ekle:
```sh
python kucoin_populer_usdt_ekle.py
```
- Size kaç adet popüler USDT paritesi eklemek istediğinizi sorar.
- Ayrıca mevcut coinler.txt dosyasını sıfırlamak veya sadece yeni coinleri eklemek isteyip istemediğinizi seçebilirsiniz.
- coinler.txt dosyasına sadece yeni ve benzersiz coinleri ekler veya tamamen sıfırlar.

## Ekran Görüntüsü

Aşağıda uygulamanın örnek bir ekran görüntüsü yer almaktadır:

![Ekran Görüntüsü](docs/screenshot.png)

## coinler.txt Örneği
```
BTC-USDT
ETH-USDT
SOL-USDT
```

## Notlar
- Tüm coin çiftleri KuCoin borsasında desteklenmelidir.
- `requirements.txt` dosyasındaki tüm paketler kurulmalıdır.
- Grafiksel arayüz için `tkinter` ve `matplotlib` gereklidir.

## Hakkında
Bu uygulama, kripto para piyasası için teknik analiz tabanlı sinyal üretimi ve görselleştirme sağlar.  
Geliştirici: Engin Talay  
Sürüm: v1.0.3  
Lisans: MIT