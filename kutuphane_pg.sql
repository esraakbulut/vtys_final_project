-- Veritabanını oluştur
CREATE DATABASE "KutuphaneDB";

-- (Veritabanına bağlandıktan sonra çalıştırılacak scriptler)

-- 1. Tablolar


CREATE TABLE KULLANICI (
    KullaniciID SERIAL PRIMARY KEY,
    KullaniciAdi VARCHAR(50) UNIQUE NOT NULL,
    Sifre VARCHAR(50) NOT NULL,
    Rol VARCHAR(20) NOT NULL
);

CREATE TABLE UYE (
    UyeID SERIAL PRIMARY KEY,
    Ad VARCHAR(50) NOT NULL,
    Soyad VARCHAR(50) NOT NULL,
    Telefon VARCHAR(15),
    Email VARCHAR(100),
    ToplamBorc DECIMAL(10, 2) DEFAULT 0
);

CREATE TABLE KITAP (
    KitapID SERIAL PRIMARY KEY,
    KitapAdi VARCHAR(100) NOT NULL,
    Kategori VARCHAR(50),
    Yazar VARCHAR(50),
    Yayinevi VARCHAR(50),
    BasimYili INT,
    ToplamAdet INT DEFAULT 1,
    MevcutAdet INT DEFAULT 1
);
CREATE TABLE ODUNC (
    OduncID SERIAL PRIMARY KEY,
    UyeID INT REFERENCES UYE(UyeID),
    KitapID INT REFERENCES KITAP(KitapID),
    KullaniciID INT REFERENCES KULLANICI(KullaniciID),
    OduncTarihi DATE DEFAULT CURRENT_DATE,
    SonTeslimTarihi DATE,
    TeslimTarihi DATE NULL,
    TeslimAlanID INT REFERENCES KULLANICI(KullaniciID)
);

CREATE TABLE CEZA (
    CezaID SERIAL PRIMARY KEY,
    UyeID INT REFERENCES UYE(UyeID),
    OduncID INT REFERENCES ODUNC(OduncID),
    Tutar DECIMAL(10, 2),
    Aciklama VARCHAR(255),
    Tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Odendi BOOLEAN DEFAULT FALSE
);

CREATE TABLE LOG_ISLEM (
    LogID SERIAL PRIMARY KEY,
    TabloAdi VARCHAR(50), 
    IslemTuru VARCHAR(50),
    Tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Aciklama VARCHAR(255)
);

-- Başlangıç Verisi
-- Kullanıcılar artık uygulama tarafından otomatik oluşturuluyor.


-- 2. Stored Procedures (PostgreSQL'de Function veya Procedure)

-- SP 1: Yeni Ödünç Verme
CREATE OR REPLACE PROCEDURE sp_YeniOduncVer(p_UyeID INT, p_KitapID INT, p_KullaniciID INT)
LANGUAGE plpgsql AS $$
DECLARE 
    v_AktifOdunc INT;
    v_Stok INT;
BEGIN
    -- Kitap satırını işlem bitene kadar kilitle [cite: 31]
    SELECT MevcutAdet INTO v_Stok FROM KITAP WHERE KitapID = p_KitapID FOR UPDATE;
    
    -- Aktif ödünç sayısını kontrol et [cite: 30]
    SELECT COUNT(*) INTO v_AktifOdunc FROM ODUNC WHERE UyeID = p_UyeID AND TeslimTarihi IS NULL;
    
    IF v_AktifOdunc >= 5 THEN
        RAISE EXCEPTION 'Hata: Üye en fazla 5 kitap alabilir.';
    ELSIF v_Stok <= 0 THEN
        RAISE EXCEPTION 'Hata: Kitap stoğu tükenmiş.'; 
    ELSE
        -- Kayıt Ekle ve SonTeslimTarihi'ni 15 gün sonraya hesapla [cite: 33, 35]
        INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi)
        VALUES (p_UyeID, p_KitapID, p_KullaniciID, CURRENT_DATE, CURRENT_DATE + INTERVAL '15 days');
    END IF;
END;
$$;

-- SP 2: Kitap Teslim Alma
CREATE OR REPLACE PROCEDURE sp_KitapTeslimAl(p_OduncID INT, p_TeslimTarihi DATE, p_TeslimAlanID INT)
LANGUAGE plpgsql
AS $$
DECLARE 
    v_SonTeslim DATE;
    v_UyeID INT;
    v_Gecikme INT;
    v_CezaTutar DECIMAL(10,2);
BEGIN
    SELECT SonTeslimTarihi, UyeID INTO v_SonTeslim, v_UyeID FROM ODUNC WHERE OduncID = p_OduncID;
    
    -- Teslim Tarihini ve Teslim Alanı Güncelle
    UPDATE ODUNC SET TeslimTarihi = p_TeslimTarihi, TeslimAlanID = p_TeslimAlanID WHERE OduncID = p_OduncID;
    
    -- Ceza Hesabı
    IF p_TeslimTarihi > v_SonTeslim THEN
        v_Gecikme := p_TeslimTarihi - v_SonTeslim;
        v_CezaTutar := v_Gecikme * 5.00;
        
        INSERT INTO CEZA (UyeID, OduncID, Tutar, Aciklama)
        VALUES (v_UyeID, p_OduncID, v_CezaTutar, v_Gecikme || ' gün gecikme cezası');
    END IF;
END;
$$;

-- SP 3: Üye Özet Raporu 
CREATE OR REPLACE FUNCTION sp_UyeOzetRapor(p_UyeID INT)
RETURNS TABLE (ToplamAlinan BIGINT, IadeEdilmeyen BIGINT, ToplamCeza DECIMAL) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY SELECT 
        (SELECT COUNT(*) FROM ODUNC WHERE UyeID = p_UyeID) as ToplamAlinan,
        (SELECT COUNT(*) FROM ODUNC WHERE UyeID = p_UyeID AND TeslimTarihi IS NULL) as IadeEdilmeyen,
        (SELECT COALESCE(SUM(Tutar), 0) FROM CEZA WHERE UyeID = p_UyeID) as ToplamCeza;
END;
$$;

-- 3. Triggers (Tetikleyici Fonksiyonları ve Tanımları)

-- Trigger Func 1: Stok Azalt
CREATE OR REPLACE FUNCTION func_tr_odunc_insert() RETURNS TRIGGER AS $$
BEGIN
    UPDATE KITAP SET MevcutAdet = MevcutAdet - 1 WHERE KitapID = NEW.KitapID;
    INSERT INTO LOG_ISLEM (TabloAdi, IslemTuru, Aciklama) VALUES ('ODUNC', 'INSERT', 'Odunc verildi. ID: ' || NEW.OduncID);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TR_ODUNC_INSERT AFTER INSERT ON ODUNC
FOR EACH ROW EXECUTE FUNCTION func_tr_odunc_insert();

-- Trigger Func 2: Stok Artır
CREATE OR REPLACE FUNCTION func_tr_odunc_update_teslim() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.TeslimTarihi IS NULL AND NEW.TeslimTarihi IS NOT NULL THEN
        UPDATE KITAP SET MevcutAdet = MevcutAdet + 1 WHERE KitapID = NEW.KitapID;
        INSERT INTO LOG_ISLEM (TabloAdi, IslemTuru, Aciklama) VALUES ('ODUNC', 'UPDATE', 'Kitap teslim alındı. ID: ' || NEW.OduncID);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TR_ODUNC_UPDATE_TESLIM AFTER UPDATE ON ODUNC
FOR EACH ROW EXECUTE FUNCTION func_tr_odunc_update_teslim();

-- Trigger Func 3: Borç Artır
CREATE OR REPLACE FUNCTION func_tr_ceza_insert() RETURNS TRIGGER AS $$
BEGIN
    UPDATE UYE SET ToplamBorc = ToplamBorc + NEW.Tutar WHERE UyeID = NEW.UyeID;
    INSERT INTO LOG_ISLEM (TabloAdi, IslemTuru, Aciklama) VALUES ('CEZA', 'INSERT', 'Ceza eklendi. UyeID: ' || NEW.UyeID);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TR_CEZA_INSERT AFTER INSERT ON CEZA
FOR EACH ROW EXECUTE FUNCTION func_tr_ceza_insert();

-- Trigger Func 4: Borç Azalt (Ceza Ödendiğinde)
CREATE OR REPLACE FUNCTION func_tr_ceza_update_odendi() RETURNS TRIGGER AS $$
BEGIN
    -- Ceza ödendi olarak işaretlendiğinde (FALSE -> TRUE)
    IF OLD.Odendi = FALSE AND NEW.Odendi = TRUE THEN
        UPDATE UYE SET ToplamBorc = ToplamBorc - NEW.Tutar WHERE UyeID = NEW.UyeID;
        INSERT INTO LOG_ISLEM (TabloAdi, IslemTuru, Aciklama) VALUES ('CEZA', 'UPDATE', 'Ceza ödendi. CezaID: ' || NEW.CezaID || ', UyeID: ' || NEW.UyeID);
    -- Ceza ödeme iptal edildiğinde (TRUE -> FALSE)
    ELSIF OLD.Odendi = TRUE AND NEW.Odendi = FALSE THEN
        UPDATE UYE SET ToplamBorc = ToplamBorc + NEW.Tutar WHERE UyeID = NEW.UyeID;
        INSERT INTO LOG_ISLEM (TabloAdi, IslemTuru, Aciklama) VALUES ('CEZA', 'UPDATE', 'Ceza ödeme iptal edildi. CezaID: ' || NEW.CezaID || ', UyeID: ' || NEW.UyeID);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TR_CEZA_UPDATE_ODENDI AFTER UPDATE OF Odendi ON CEZA
FOR EACH ROW EXECUTE FUNCTION func_tr_ceza_update_odendi();

-- Trigger Func 4: Silmeyi Engelle
CREATE OR REPLACE FUNCTION func_tr_uye_delete_block() RETURNS TRIGGER AS $$
DECLARE v_AktifOdunc INT;
BEGIN
    SELECT COUNT(*) INTO v_AktifOdunc FROM ODUNC WHERE UyeID = OLD.UyeID AND TeslimTarihi IS NULL;
    
    IF v_AktifOdunc > 0 OR OLD.ToplamBorc > 0 THEN
        RAISE EXCEPTION 'Hata: Üyenin üzerinde kitap veya borç var, silinemez!';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TR_UYE_DELETE_BLOCK BEFORE DELETE ON UYE
FOR EACH ROW EXECUTE FUNCTION func_tr_uye_delete_block();

-- ==========================================
-- TEST VERİLERİ (DUMMY DATA)
-- ==========================================

-- 1. Kitaplar (5 Farklı Kategori, 10 Kitap)
INSERT INTO KITAP (KitapAdi, Yazar, Kategori, Yayinevi, BasimYili, ToplamAdet, MevcutAdet) VALUES
('Sefiller', 'Victor Hugo', 'Klasik', 'İş Bankası', 1862, 5, 5),
('Suç ve Ceza', 'Dostoyevski', 'Klasik', 'Can Yayınları', 1866, 4, 4),
('1984', 'George Orwell', 'Bilim Kurgu', 'Can Yayınları', 1949, 10, 10),
('Cesur Yeni Dünya', 'Aldous Huxley', 'Bilim Kurgu', 'İthaki', 1932, 6, 6),
('Sapiens', 'Yuval Noah Harari', 'Tarih', 'Kolektif', 2011, 8, 8),
('Nutuk', 'Mustafa Kemal Atatürk', 'Tarih', 'Yapı Kredi', 1927, 20, 20),
('Simyacı', 'Paulo Coelho', 'Felsefe', 'Can Yayınları', 1988, 7, 7),
('Dönüşüm', 'Franz Kafka', 'Felsefe', 'İş Bankası', 1915, 6, 6),
('Python ile Veri Bilimi', 'Jake VanderPlas', 'Teknoloji', 'OReilly', 2016, 3, 3),
('Clean Code', 'Robert C. Martin', 'Teknoloji', 'Prentice Hall', 2008, 5, 5);

-- 2. Üyeler (5 Üye)
INSERT INTO UYE (Ad, Soyad, Telefon, Email) VALUES
('Ali', 'Yılmaz', '5551112233', 'ali@mail.com'),
('Ayşe', 'Kara', '5552223344', 'ayse@mail.com'),
('Mehmet', 'Demir', '5553334455', 'mehmet@mail.com'),
('Zeynep', 'Çelik', '5554445566', 'zeynep@mail.com'),
('Burak', 'Öz', '5555556677', 'burak@mail.com');

-- 2.1. Varsayılan Kullanıcılar (Foreign Key için gerekli)
-- Şifreler hashlenmemiş '1234' olarak eklendi, uygulama içinde tekrar güncellenebilir.
INSERT INTO KULLANICI (KullaniciID, KullaniciAdi, Sifre, Rol) VALUES
(1, 'admin', '1234', 'Admin'),
(2, 'gorevli1', '1234', 'Gorevli'),
(3, 'gorevli2', '1234', 'Gorevli')
ON CONFLICT (KullaniciID) DO NOTHING;
-- Sequence'i güncelle (Manuel ID verdiğimiz için)
SELECT setval('kullanici_kullaniciid_seq', (SELECT MAX(KullaniciID) FROM KULLANICI));

-- 3. Geçmiş Ödünç İşlemleri (Raporları Test Etmek İçin)
-- Not: Triggerlar stokları otomatik düşeceği için manuel stok ayarı yapmıyoruz.
-- Ancak geçmiş tarihli kayıtlar için CALL prosedürünü değil direkt INSERT kullanıp triggerın çalışmasını sağlayacağız.

-- Ali (1 numaralı üye), Sefiller (1 numaralı kitap) almış
INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi) 
VALUES (1, 1, 1, '2023-01-01', '2023-01-16');
-- Teslim etmiş (Gecikmesiz)
UPDATE ODUNC SET TeslimTarihi = '2023-01-10' WHERE UyeID=1 AND KitapID=1;

-- Ayşe (2), 1984 (3) almış
INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi) 
VALUES (2, 3, 1, '2023-02-01', '2023-02-16');
-- Teslim etmiş (Gecikmeli - Ceza oluşmalı) -- Manuel Ceza eklemiyoruz, SP çalıştırırsak oluşur ama burada manuel insert yapıyoruz.
-- Trigger sadece stok artırır. O yüzden manuel ceza ekleyelim test için.
UPDATE ODUNC SET TeslimTarihi = '2023-02-20' WHERE UyeID=2 AND KitapID=3;
INSERT INTO CEZA (UyeID, OduncID, Tutar, Aciklama) 
VALUES (2, (SELECT MAX(OduncID) FROM ODUNC), 20.00, '4 gün gecikme');

-- Popüler Kitap Testi: 1984 kitabı bir kez daha alınmış olsun
INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi) 
VALUES (3, 3, 1, '2023-03-01', '2023-03-16');
-- Hala elinde (Teslim tarihi NULL)

-- Geciken Kitaplar Test Verisi (Raporlar için)
-- Bu kayıtlar SonTeslimTarihi < CURRENT_DATE ve TeslimTarihi IS NULL olacak şekilde ayarlanmalı
-- MevcutAdet'i trigger otomatik azaltacak, bu yüzden önce stokları kontrol et

-- Mehmet (3), Sapiens (5) - 10 gün önce alınmış, 5 gün önce teslim etmesi gereken (5 gün gecikmiş)
INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi) 
VALUES (3, 5, 1, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '5 days');

-- Zeynep (4), Nutuk (6) - 7 gün önce alınmış, 2 gün önce teslim etmesi gereken (2 gün gecikmiş)
INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi) 
VALUES (4, 6, 1, CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '2 days');

-- Burak (5), Simyacı (7) - 20 gün önce alınmış, 5 gün önce teslim etmesi gereken (5 gün gecikmiş)
INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi) 
VALUES (5, 7, 1, CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE - INTERVAL '5 days');

-- Ali (1), Suç ve Ceza (2) - 12 gün önce alınmış, 3 gün önce teslim etmesi gereken (3 gün gecikmiş)
INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi) 
VALUES (1, 2, 1, CURRENT_DATE - INTERVAL '12 days', CURRENT_DATE - INTERVAL '3 days');