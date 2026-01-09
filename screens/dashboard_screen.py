"""Dashboard ekranı modülü"""
import customtkinter as ctk
from constants import (COLOR_CARD_BG, COLOR_ACCENT, COLOR_SUCCESS, 
                       COLOR_DANGER, COLOR_WARNING, COLOR_INFO)


def create_dashboard(app):
    """Dashboard ekranını oluşturur"""
    container = app.set_content_title("Genel Bakış")
    
    # İstatistikleri veritabanından çek
    kullanici_adi = app.aktif_kullanici.get('kullaniciadi', 'Kullanıcı') if app.aktif_kullanici else 'Misafir'
    
    # Hoş geldin mesajı
    welcome_frm = ctk.CTkFrame(container, fg_color="transparent")
    welcome_frm.pack(fill="x", pady=(0, 20))
    ctk.CTkLabel(welcome_frm, text=f"Hoş geldiniz, {kullanici_adi} 👋", 
                 font=("Roboto", 32, "bold"), text_color=COLOR_ACCENT).pack(anchor="w")
    ctk.CTkLabel(welcome_frm, text="Bugün kütüphanede neler yapmak istersiniz?", 
                 font=("Roboto", 16), text_color="gray").pack(anchor="w")

    try:
        uye_sayisi = len(app.db.fetch_all("SELECT UyeID FROM UYE"))
        kitap_sayisi = app.db.fetch_all("SELECT SUM(MevcutAdet) as t FROM KITAP")[0]['t'] or 0
        odunc_sayisi = len(app.db.fetch_all("SELECT OduncID FROM ODUNC WHERE TeslimTarihi IS NULL"))
    except:
        uye_sayisi, kitap_sayisi, odunc_sayisi = 0, 0, 0

    # Kartlar Grid
    grid_frm = ctk.CTkFrame(container, fg_color="transparent")
    grid_frm.pack(fill="x", pady=20)

    def create_card(parent, title, value, color, icon):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=15, height=150)
        card.pack(side="left", expand=True, fill="both", padx=10)
        
        ctk.CTkLabel(card, text=icon, font=("Arial", 40), text_color="white").pack(pady=(20, 5))
        ctk.CTkLabel(card, text=value, font=("Roboto", 36, "bold"), text_color="white").pack()
        ctk.CTkLabel(card, text=title, font=("Roboto", 14), text_color="#eeeeee").pack(pady=(0, 20))

    create_card(grid_frm, "Toplam Üye", str(uye_sayisi), COLOR_SUCCESS, "👥")
    create_card(grid_frm, "Raftaki Kitaplar", str(kitap_sayisi), COLOR_INFO, "📚")
    create_card(grid_frm, "Aktif Ödünçler", str(odunc_sayisi), COLOR_WARNING, "⏳")

    # Alt Kısım: Hızlı Erişim
    ctk.CTkLabel(container, text="Hızlı İşlemler", font=("Roboto", 20, "bold")).pack(anchor="w", pady=(30, 10))
    
    quick_frm = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG, corner_radius=15)
    quick_frm.pack(fill="x", ipady=20)

    ctk.CTkButton(quick_frm, text="Yeni Kitap Ekle", command=app.kitap_yonetimi, width=200, height=50, fg_color="#333", border_width=1, border_color="gray").pack(side="left", padx=20)
    ctk.CTkButton(quick_frm, text="Hemen Ödünç Ver", command=app.odunc_verme_ekrani, width=200, height=50, fg_color=COLOR_ACCENT).pack(side="left", padx=20)

