#  Kütüphane Yönetim Sistemi

Ondokuz Mayıs Üniversitesi Veritabanı Yönetim Sistemleri Güz Final Projesi.
 **CustomTkinter** arayüzü ve **PostgreSQL** veritabanı altyapısı ile Python kullanılarak geliştirilmiştir.

# Özellikler

### Güvenlik ve Giriş
*   **Rol Tabanlı Yetkilendirme:**
    *   **Yönetici (Admin):** Tüm yetkilere sahiptir.
    *   **Görevli (Personel):** Üye ve ödünç işlemlerini yönetir.
*   **Güvenli Giriş:** Kullanıcı bilgileri ve şifreler `.env` dosyasından okunur veya veritabanında saklanır.

### Üye Yönetimi
*   **Hızlı Kayıt:** Uygulama içinde yeni üye ekleme işlemi.
*   **Üye Takibi:** Üye bilgilerini güncelleme, silme ve borç durumunu görüntüleme.
*   **Detaylı Profil:** Üyenin elindeki kitaplar, toplam borcu ve geçmiş işlemleri.

### Kitap ve Stok Yönetimi
*   **Stok Takibi:** Kitapların toplam ve mevcut (rafta olan) adetlerinin anlık takibi.
*   **Akıllı Arama:** Kitap adı veya yazar adına göre anında filtreleme.
*   **Kategori Sistemi:** Kitapları kategorilerine göre düzenleme ve filtreleme.

### Ödünç ve İade (Core)
*   **Sorunsuz Ödünç Verme:**
    *   Üye ve kitap seçerek tek tıkla ödünç verme.
    *   Stok kontrolü (Stok 0 ise işlem engellenir).
    *   Üye limit kontrolü (Maksimum 5 kitap).
*   **Kolay İade ve Ceza:**
    *   Geciken kitaplar için otomatik ceza hesaplama (Gün başı 5.00 ₺).
    *   İade sırasında gecikme varsa sistem personeli uyarır.

### Raporlama ve Analiz
*   **Dashboard:** Aktif üye, kitap ve işlem sayıları.
*   **Özel Raporlar:**
    *   Geciken Kitaplar Listesi.
    *   Tarih Aralığına Göre İşlem Raporu.
    *   En Çok Okunan Kitaplar.
*   **Dışa Aktarma:** Verileri **CSV** formatında indirme imkanı.

---

## Kurulum Rehberi

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin.

### Gereksinimler
*   **Python 3.10+**: [python.org](https://www.python.org/)
*   **PostgreSQL**: [postgresql.org](https://www.postgresql.org/)

### 1. Hazırlık
Projeyi indirin ve terminali açarak proje klasörüne gidin:
```bash
cd vtys_final_project
```

Gerekli Python kütüphanelerini yükleyin:
```bash
pip install -r requirements.txt
```

### 2. Veritabanı Yapılandırması
Proje ana dizininde `.env` isimli bir dosya oluşturun ve veritabanı bilgilerinizi girin:

```env
# .env dosyası
DB_NAME=KutuphaneDB
DB_USER=postgres
DB_PASSWORD=sifreniz
DB_HOST=localhost

# Uygulama Kullanıcı Şifreleri (Varsayılan: 1234)
admin=1234
gorevli1=1234
gorevli2=1234
```

### 3. Veritabanını Kurun
Hazırladığımız script ile veritabanını ve tabloları tek komutla oluşturun:
```bash
python reset_db.py
```
*Bu komut veritabanını oluşturur, tabloları kurar ve test verilerini (kitaplar, üyeler) yükler.*

---

## Çalıştırma

Kurulum bittikten sonra uygulamayı başlatın:

```bash
python app.py
```

### Varsayılan Giriş Bilgileri

| Rol | Kullanıcı Adı | Şifre (Varsayılan) |
| :--- | :--- | :--- |
| **Yönetici** | `admin` | `1234` |
| **Personel 1** | `gorevli1` | `1234` |
| **Personel 2** | `gorevli2` | `1234` |

*Not: Şifreleri `.env` dosyasından değiştirebilirsiniz.*

---

## Proje Dosya Yapısı

```
vtys_final_projesi/
├── app.py                 # Ana uygulama başlatıcı
├── db_manager.py          # Veritabanı bağlantı ve işlem sınıfı
├── ui_helpers.py          # Yardımcı arayüz fonksiyonları
├── constants.py           # Renkler ve sabitler
├── reset_db.py            # Veritabanı kurulum scripti
├── kutuphane_pg.sql       # SQL şema ve prosedürleri
├── requirements.txt       # Kütüphane gereksinimleri
└── screens/               # Tüm ekran modülleri
    ├── login_screen.py    # Giriş ekranı
    ├── dashboard_screen.py# Ana kontrol paneli
    ├── member_screen.py   # Üye işlemleri
    ├── book_screen.py     # Kitap işlemleri
    ├── lending_screen.py  # Ödünç verme
    ├── return_screen.py   # İade alma
    └── report_screen.py   # Raporlar
```
