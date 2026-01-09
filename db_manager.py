import psycopg2
from psycopg2 import extras
from datetime import date

class DBManager:
    def __init__(self):
        self.app_config = {}
        
        try:
            import os
            
            # .env dosyasını oku ve Environment Variables yükle
            base_dir = os.path.dirname(os.path.abspath(__file__))
            env_path = os.path.join(base_dir, '.env')
            
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                key, val = line.split('=', 1)
                                os.environ[key.strip()] = val.strip()
                            except ValueError:
                                continue # Hatalı satırları atla
            
            # Değişkenleri ortamdan al
            db_user = os.environ.get('DB_USER')
            db_pass = os.environ.get('DB_PASSWORD')
            db_host = os.environ.get('DB_HOST')
            db_name = os.environ.get('DB_NAME')
            
            if not all([db_user, db_pass, db_host, db_name]):
                 raise ValueError("Veritabanı bilgileri eksik! Lütfen proje ana dizininde '.env' dosyasının olduğundan ve gerekli bilgileri içerdiğinden emin olun.")

            self.config = {
                'user': db_user,
                'password': db_pass,
                'host': db_host,
                'dbname': db_name
            }
            self.app_config = {
                'app_admin_password': os.environ.get('APP_ADMIN_PASS', '1234'),
                'app_staff_password': os.environ.get('APP_STAFF_PASS', '1234')
            }
        except Exception as e:
            raise Exception(f"Yapılandırma hatası: {e}")

    def init_users(self):
        """Veritabanında admin ve gorevli kullanıcılarını kontrol eder, yoksa oluşturur."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Admin Kontrol
            cursor.execute("SELECT Count(*) FROM KULLANICI WHERE KullaniciAdi = 'admin'")
            if cursor.fetchone()[0] == 0:
                pwd = self.app_config.get('app_admin_password', '1234')
                cursor.execute("INSERT INTO KULLANICI (KullaniciAdi, Sifre, Rol) VALUES ('admin', %s, 'Admin')", (pwd,))
            
            # Görevli1 Kontrol
            cursor.execute("SELECT Count(*) FROM KULLANICI WHERE KullaniciAdi = 'gorevli1'")
            if cursor.fetchone()[0] == 0:
                pwd = self.app_config.get('app_staff_password', '1234')
                cursor.execute("INSERT INTO KULLANICI (KullaniciAdi, Sifre, Rol) VALUES ('gorevli1', %s, 'Gorevli')", (pwd,))

            # Görevli2 Kontrol
            cursor.execute("SELECT Count(*) FROM KULLANICI WHERE KullaniciAdi = 'gorevli2'")
            if cursor.fetchone()[0] == 0:
                pwd = self.app_config.get('app_staff_password', '1234')
                cursor.execute("INSERT INTO KULLANICI (KullaniciAdi, Sifre, Rol) VALUES ('gorevli2', %s, 'Gorevli')", (pwd,))
            
            conn.commit()
        except Exception as e:
            print(f"Kullanıcı başlatma hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_connection(self):
        return psycopg2.connect(**self.config)

    def login_kontrol(self, kullanici_adi, sifre):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM KULLANICI WHERE KullaniciAdi = %s AND Sifre = %s"
        cursor.execute(query, (kullanici_adi, sifre))
        user = cursor.fetchone()
        conn.close()
        return user

    def calistir_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return True, "İşlem Başarılı"
        except Exception as err:
            conn.rollback()
            return False, str(err)
        finally:
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    # Stored Procedure Çağırma
    def sp_yeni_odunc(self, uye_id, kitap_id, kul_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # PostgreSQL 'CALL' komutu
            cursor.execute("CALL sp_YeniOduncVer(%s, %s, %s)", (uye_id, kitap_id, kul_id))
            conn.commit()
            return True, "Ödünç işlemi başarılı."
        except Exception as err:
            conn.rollback()
            # Hata mesajını temizle (Postgres hatası uzun olabilir)
            msg = str(err).split('\n')[0] 
            return False, msg
        finally:
            conn.close()

    def ceza_ode(self, ceza_id):
        """Ceza ödeme işlemi - Ceza kaydını ödendi olarak işaretler"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE CEZA SET Odendi = TRUE WHERE CezaID = %s AND Odendi = FALSE", (ceza_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "Ceza başarıyla ödendi."
            else:
                return False, "Ceza bulunamadı veya zaten ödenmiş."
        except Exception as err:
            conn.rollback()
            return False, str(err)
        finally:
            conn.close()
    
    def sp_teslim_al(self, odunc_id, kul_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        bugun = date.today()
        try:
            cursor.execute("CALL sp_KitapTeslimAl(%s, %s, %s)", (odunc_id, bugun, kul_id))
            conn.commit()
            return True, "Kitap teslim alındı."
        except Exception as err:
            conn.rollback()
            msg = str(err).split('\n')[0]
            return False, msg
        finally:
            conn.close()

    # --- YENİ EKLENEN METOTLAR ---

    def sp_uye_ozet(self, uye_id):
        """sp_UyeOzetRapor fonksiyonunu çağırır ve sonucu döner."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # PostgreSQL function calls use SELECT
            cursor.execute("SELECT * FROM sp_UyeOzetRapor(%s)", (uye_id,))
            result = cursor.fetchone()
            return True, result
        except Exception as err:
            return False, str(err)
        finally:
            conn.close()

    def rapor_tarih_araligi(self, baslangic, bitis, kategori=None, uye_id=None):
        """İki tarih arasındaki ödünç işlemlerini detaylı getirir."""
        query = """
            SELECT 
                ODUNC.OduncID,
                UYE.UyeID,
                UYE.Ad || ' ' || UYE.Soyad as UyeAd,
                KITAP.KitapAdi,
                ODUNC.OduncTarihi,
                ODUNC.TeslimTarihi,
                KITAP.Kategori,
                CASE WHEN ODUNC.TeslimTarihi IS NULL THEN 'TESLİM EDİLMEDİ' ELSE 'TESLİM EDİLDİ' END as Durum,
                K1.KullaniciAdi as VerenPersonel,
                K2.KullaniciAdi as AlanPersonel
            FROM ODUNC
            JOIN UYE ON ODUNC.UyeID = UYE.UyeID
            JOIN KITAP ON ODUNC.KitapID = KITAP.KitapID
            LEFT JOIN KULLANICI K1 ON ODUNC.KullaniciID = K1.KullaniciID
            LEFT JOIN KULLANICI K2 ON ODUNC.TeslimAlanID = K2.KullaniciID
            WHERE ODUNC.OduncTarihi BETWEEN %s AND %s
        """
        params = [baslangic, bitis]
        
        if kategori and kategori != "Tümü":
            query += " AND KITAP.Kategori = %s"
            params.append(kategori)
        
        if uye_id and uye_id != "Tümü":
            query += " AND UYE.UyeID = %s"
            params.append(uye_id)
            
        query += " ORDER BY ODUNC.OduncTarihi DESC"
        return self.fetch_all(query, tuple(params))

    def rapor_en_cok_okunan(self, baslangic=None, bitis=None):
        """En çok ödünç alınan kitapları listeler. Tarih aralığı opsiyoneldir."""
        query = """
            SELECT 
                KITAP.KitapAdi,
                COUNT(ODUNC.OduncID) as OkunmaSayisi
            FROM ODUNC
            JOIN KITAP ON ODUNC.KitapID = KITAP.KitapID
            WHERE 1=1
        """
        params = []
        
        if baslangic and bitis:
            query += " AND ODUNC.OduncTarihi BETWEEN %s AND %s"
            params.extend([baslangic, bitis])
        
        query += """
            GROUP BY KITAP.KitapAdi
            ORDER BY OkunmaSayisi DESC
            LIMIT 10
        """
        return self.fetch_all(query, tuple(params) if params else None)
    
    def get_all_uyeler(self):
        """Tüm üyeleri listeler (raporlama için)."""
        return self.fetch_all("SELECT UyeID, Ad || ' ' || Soyad as AdSoyad FROM UYE ORDER BY Ad, Soyad")

    def get_categories(self):
        """Kitap tablosundaki benzersiz kategorileri getirir."""
        # Eğer KATEGORI tablosu varsa oradan, yoksa KITAP'tan (Geriye dönük uyumluluk ve geçiş için)
        try:
             # Önce tablo var mı kontrolü (basitçe select atarak)
             return [r['kategoriadi'] for r in self.fetch_all("SELECT KategoriAdi FROM KATEGORI ORDER BY KategoriAdi")]
        except:
             # Fallback
             query = "SELECT DISTINCT Kategori FROM KITAP WHERE Kategori IS NOT NULL ORDER BY Kategori"
             results = self.fetch_all(query)
             return [r['kategori'] for r in results]

   #Kategori, arama, raporlama

    def init_categories(self):
        """Kategori tablosunu oluşturur ve mevcut kitaplardan verileri aktarır."""
        sql_create = """
        CREATE TABLE IF NOT EXISTS KATEGORI (
            KategoriID SERIAL PRIMARY KEY,
            KategoriAdi VARCHAR(50) UNIQUE NOT NULL
        );
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql_create)
            conn.commit() # Create table first
            
            try:
                # Mevcut kitaplardaki kategorileri aktar (Eğer KITAP tablosunda Kategori sütunu varsa)
                cursor.execute("""
                    INSERT INTO KATEGORI (KategoriAdi)
                    SELECT DISTINCT Kategori FROM KITAP 
                    WHERE Kategori IS NOT NULL
                    ON CONFLICT (KategoriAdi) DO NOTHING;
                """)
                conn.commit()
            except Exception as e_mig:
                # Kolon yoksa veya başka hata varsa yoksay (Migration opsiyonel)
                print(f"Kategori migration uyarısı (Normal olabilir): {e_mig}")
                conn.rollback()
        except Exception as e:
            print(f"Kategori tablosu hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

    def kategori_ekle(self, ad):
        return self.calistir_query("INSERT INTO KATEGORI (KategoriAdi) VALUES (%s)", (ad,))

    def kategori_guncelle(self, eski_ad, yeni_ad):
        # Transaction: Hem KATEGORI tablosunu hem de KITAP tablosunu güncelle
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE KATEGORI SET KategoriAdi = %s WHERE KategoriAdi = %s", (yeni_ad, eski_ad))
            cursor.execute("UPDATE KITAP SET Kategori = %s WHERE Kategori = %s", (yeni_ad, eski_ad))
            conn.commit()
            return True, "Kategori güncellendi."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def kategori_sil(self, ad):
        # Kitaplarda kullanılıyor mu?
        cnt = self.fetch_all("SELECT Count(*) as c FROM KITAP WHERE Kategori = %s", (ad,))
        if cnt and cnt[0]['c'] > 0:
            return False, f"Bu kategoriye ait {cnt[0]['c']} kitap var. Önce onları düzenleyin."
        
        return self.calistir_query("DELETE FROM KATEGORI WHERE KategoriAdi = %s", (ad,))

    def arama_uye(self, keyword):
        query = """
            SELECT * FROM UYE 
            WHERE Ad ILIKE %s OR Soyad ILIKE %s OR Email ILIKE %s 
            ORDER BY UyeID DESC
        """
        kw = f"%{keyword}%"
        return self.fetch_all(query, (kw, kw, kw))

    def arama_kitap(self, keyword):
        query = """
            SELECT * FROM KITAP 
            WHERE KitapAdi ILIKE %s OR Yazar ILIKE %s 
            ORDER BY Kategori, KitapAdi
        """
        kw = f"%{keyword}%"
        return self.fetch_all(query, (kw, kw))
    
    

    def get_overdue_books(self):
        query = """
            SELECT 
                U.Ad || ' ' || U.Soyad as UyeAd,
                K.KitapAdi,
                O.OduncTarihi,
                O.SonTeslimTarihi,
                (CURRENT_DATE - O.SonTeslimTarihi) AS GecikmeGun
            FROM ODUNC O
            JOIN UYE U ON O.UyeID = U.UyeID
            JOIN KITAP K ON O.KitapID = K.KitapID
            WHERE O.TeslimTarihi IS NULL 
              AND O.SonTeslimTarihi < CURRENT_DATE
            ORDER BY GecikmeGun DESC
        """
        return self.fetch_all(query)
    
    def get_all_penalties_with_pending(self, uye_filter=""):
        """
        Hem gerçek cezaları (CEZA tablosundan) hem de geciken kitaplardan kaynaklanan bekleyen cezaları getirir
        Sadece ödenmemiş cezaları getirir (ödendiği için artık borç olarak sayılmayan cezalar hariç)
        """
        uye_condition = ""
        params = []
        if uye_filter:
            uye_condition = " AND (U.Ad ILIKE %s OR U.Soyad ILIKE %s)"
            kw = f"%{uye_filter}%"
            params = [kw, kw]
        
        query = """
            SELECT * FROM (
                -- Gerçek cezalar (CEZA tablosundan - sadece ödenmemiş olanlar)
                SELECT 
                    C.CezaID::text as CezaID,
                    U.Ad || ' ' || U.Soyad as UyeAd,
                    COALESCE(K.KitapAdi, '-') as KitapAd,
                    C.Tutar,
                    C.Aciklama,
                    C.Tarih::text as Tarih,
                    'Bekliyor' as Durum,
                    O.OduncID,
                    C.Tarih as TarihSira
                FROM CEZA C
                JOIN UYE U ON C.UyeID = U.UyeID
                LEFT JOIN ODUNC O ON C.OduncID = O.OduncID
                LEFT JOIN KITAP K ON O.KitapID = K.KitapID
                WHERE C.Odendi = FALSE
        """ + uye_condition + """
                
                UNION ALL
                
                -- Bekleyen cezalar (Geciken kitaplardan)
                SELECT 
                    'PENDING-' || O.OduncID::text as CezaID,
                    U.Ad || ' ' || U.Soyad as UyeAd,
                    K.KitapAdi as KitapAd,
                    (CURRENT_DATE - O.SonTeslimTarihi) * 5.00 as Tutar,
                    (CURRENT_DATE - O.SonTeslimTarihi)::text || ' gün gecikme cezası (Bekliyor)' as Aciklama,
                    'Bekliyor' as Tarih,
                    'Bekliyor' as Durum,
                    O.OduncID,
                    CURRENT_DATE as TarihSira
                FROM ODUNC O
                JOIN UYE U ON O.UyeID = U.UyeID
                JOIN KITAP K ON O.KitapID = K.KitapID
                LEFT JOIN CEZA C ON O.OduncID = C.OduncID
                WHERE O.TeslimTarihi IS NULL 
                  AND O.SonTeslimTarihi < CURRENT_DATE
                  AND C.CezaID IS NULL
        """ + uye_condition + """
            ) subquery
            ORDER BY CASE WHEN Durum = 'Bekliyor' THEN 0 ELSE 1 END, TarihSira DESC
        """
        
        # Parametreleri iki kez kullan (UNION ALL için)
        if params:
            params = params + params
        
        return self.fetch_all(query, tuple(params))