import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

def read_config():
    config = {}
    try:
        # .env dosyasını oku
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        k, v = line.split('=', 1)
                        config[k.strip()] = v.strip()
                    except:
                        pass
        return config
    except FileNotFoundError:
        print("HATA: .env dosyası bulunamadı! Lütfen .env.example dosyasını .env olarak kopyalayıp düzenleyin.")
        sys.exit(1)

def reset_database():
    cfg = read_config()
    db_name = cfg.get('DB_NAME', 'kutuphane_db')
    
    # 1. Veritabanını oluştur (Eğer yoksa)
    print(f"[*] '{db_name}' veritabanı kontrol ediliyor...")
    try:
        # 'postgres' veritabanına bağlan
        conn = psycopg2.connect(
            host=cfg.get('DB_HOST', 'localhost'),
            user=cfg.get('DB_USER', 'postgres'),
            password=cfg.get('DB_PASSWORD', ''),
            dbname='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Veritabanı var mı kontrol et
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f"CREATE DATABASE \"{db_name}\"")
            print(f"[+] Veritabanı oluşturuldu: {db_name}")
        else:
            print(f"[i] Veritabanı zaten mevcut: {db_name}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"HATA: Veritabanı oluşturma başarısız: {e}")
        sys.exit(1)

    # 2. Şemayı Yükle
    print("[*] Tablolar ve veriler yükleniyor...")
    try:
        conn = psycopg2.connect(
            host=cfg.get('DB_HOST', 'localhost'),
            user=cfg.get('DB_USER', 'postgres'),
            password=cfg.get('DB_PASSWORD', ''),
            dbname=db_name
        )
        cur = conn.cursor()
        
        # Temiz Kurulum: Mevcut şemayı sıfırla
        print("[*] Mevcut tablolar temizleniyor...")
        cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        cur.execute("GRANT ALL ON SCHEMA public TO postgres;")
        cur.execute("GRANT ALL ON SCHEMA public TO public;")
        conn.commit()
        
        # SQL dosyasını oku ve CREATE DATABASE komutlarını temizle
        with open('kutuphane_pg.sql', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # CREATE DATABASE komutunu içeren satırları filtrele (Zaten adım 1'de oluşturduk)
        filtered_sql = []
        for line in lines:
            if line.strip().upper().startswith('CREATE DATABASE'):
                continue
            filtered_sql.append(line)
            
        sql_content = "".join(filtered_sql)
            
        # SQL'i çalıştır
        cur.execute(sql_content)
        conn.commit()
        
        print("[+] Şema ve test verileri başarıyla yüklendi!")
        print("\nKurulum Tamamlandı! 🚀")
        print("Uygulamayı başlatmak için: python app.py")
        
    except Exception as e:
        print(f"HATA: SQL scripti çalıştırılamadı: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    confirm = input("DİKKAT: Bu işlem mevcut veritabanını sıfırlayabilir veya üzerine yazabilir. Devam edilsin mi? (e/h): ")
    if confirm.lower() == 'e':
        reset_database()
    else:
        print("İşlem iptal edildi.")
