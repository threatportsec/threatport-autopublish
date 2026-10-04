# ThreatPort Auto-Publish

40 gun, her gun TR 12:00'da otomatik YouTube Shorts + Instagram Reels yayini.

GitHub Actions uzerinden calisir — PC kapaliyken bile calisir.

---

## Kurulum (tek seferlik)

### 1. GitHub reposu olustur

```bash
cd ~/Downloads/threatport-autopublish
git init
git add .
git commit -m "initial: ThreatPort autopublish"
gh repo create threatport-autopublish --private --source=. --push
```

### 2. YouTube Data API v3 kurulumu

1. [Google Cloud Console](https://console.cloud.google.com/) > yeni proje olustur
2. **APIs & Services > Library** > "YouTube Data API v3" arat > **Enable**
3. **APIs & Services > Credentials** > **Create Credentials > OAuth client ID**
   - Application type: **Desktop app**
   - Download JSON > `client_secret.json` olarak `scripts/` klasorune kaydet
4. **OAuth consent screen** > Test user olarak kendi Gmail adresini ekle

### 3. YouTube refresh token al (lokal, tek seferlik)

```bash
pip install -r requirements.txt
python scripts/get_youtube_token.py
```

Tarayicida Google ile giris yap, izin ver. Script sana 3 deger verecek:
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

### 4. GitHub Secrets ekle

Repo > **Settings > Secrets and variables > Actions** > su 5 secret'i ekle:

| Secret | Deger |
|--------|-------|
| `YOUTUBE_CLIENT_ID` | Google Cloud'dan |
| `YOUTUBE_CLIENT_SECRET` | Google Cloud'dan |
| `YOUTUBE_REFRESH_TOKEN` | Adim 3'ten |
| `IG_USERNAME` | Instagram kullanici adin |
| `IG_PASSWORD` | Instagram sifren |

Eger Instagram'da 2FA varsa:
| `IG_TOTP_CODE` | TOTP kodu (her workflow calistirmasinda guncellenmeli) |

> **Not:** Instagram 2FA icin `IG_TOTP_CODE` suresi gecer. 2FA'yi kapatmak veya
> Instagram'i Business/Creator hesabina cevirmek (Facebook Page baglayarak)
> bu sorunu ortadan kaldirir. Business hesaplar icin Meta Graph API kullanilabilir
> (bu script su an kisisel hesap icin `instagrapi` kullaniyor).

### 5. Baslangic tarihini ayarla

`.github/workflows/daily-publish.yml` icindeki `START_DATE` degerini ilk yayin
tarihine ayarla. Varsayilan: `2026-10-05` (yani ilk video 5 Ekim 2026'da yayinlanir).

```yaml
env:
  START_DATE: "2026-10-05"
```

### 6. Ilk testi calistir

GitHub'da repo > **Actions > Daily ThreatPort Publish > Run workflow**

Logs'dan her seyin calistigini dogrula.

---

## How it works

```
GitHub Actions cron (09:00 UTC = 12:00 TR)
  └─ scripts/publish.py
       ├─ calculates day number from START_DATE
       ├─ reads youtube-metadata.csv for title/description
       ├─ reads publish.md for Instagram caption
       ├─ youtube_upload.py  →  YouTube Data API v3
       └─ instagram_upload.py  →  instagrapi (personal account)
```

Her gun bir video. 40 günde tumu yayinlanir. Sonra workflow otomatik bostadir.

---

## Instagram uyarisi

Bu script kisisel Instagram hesaplari icin `instagrapi` (resmi olmayan) kutuphanesini
kullaniyor. Instagram bunu ToS ihlali olarak degerlendirebilir. Riskleri:
- Hesap gecici olarak kilitlanabilir
- 2FA her calistirmada guncelleme gerektirir

**Alternatif (onerilen):** Hesabini Business/Creator'a cevir (ucretsiz),
Facebook Page bagla. Bu durumda Meta Graph API ile resmi erisim mumkun olur.

---

## Manuel tetikleme

GitHub Actions'ta "Run workflow" ile manuel calistirabilirsin.
Belirli bir gunu zorlamak icin `day` parametresini doldur.

## Yerel test

```bash
cd ~/Downloads/threatport-autopublish
pip install -r requirements.txt
export YOUTUBE_CLIENT_ID="..."
export YOUTUBE_CLIENT_SECRET="..."
export YOUTUBE_REFRESH_TOKEN="..."
export IG_USERNAME="..."
export IG_PASSWORD="..."
python scripts/publish.py
```
