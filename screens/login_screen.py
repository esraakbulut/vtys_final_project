"""Giriş ekranı modülü"""
import customtkinter as ctk
from tkinter import messagebox
from constants import COLOR_MAIN_BG, COLOR_CARD_BG, COLOR_TEXT_MAIN, COLOR_TEXT_SUB, COLOR_ACCENT


def create_login_screen(app):
    """Giriş ekranını oluşturur"""
    app.temize_cek()
    
    # Arka plan görseli yerine şık bir gradient hissi için frame
    bg_frame = ctk.CTkFrame(app, fg_color=COLOR_MAIN_BG)
    bg_frame.pack(fill="both", expand=True)

    # Giriş Kartı
    card = ctk.CTkFrame(bg_frame, width=450, corner_radius=20, fg_color=COLOR_CARD_BG, border_width=2, border_color="#333")
    card.place(relx=0.5, rely=0.5, anchor="center")

    # Başlık ve İkon
    ctk.CTkLabel(card, text="📚", font=("Arial", 60)).pack(pady=(40, 10))
    ctk.CTkLabel(card, text="KÜTÜPHANE SİSTEMİ", font=("Roboto", 24, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(0, 5))
    ctk.CTkLabel(card, text="Personel Giriş Ekranı", font=("Roboto", 14), text_color=COLOR_TEXT_SUB).pack(pady=(0, 30))

    # Giriş Alanları
    e_user = ctk.CTkEntry(card, width=320, height=45, placeholder_text="Kullanıcı Adı", font=("Roboto", 14), corner_radius=10)
    e_user.pack(pady=10)
    
    e_pass = ctk.CTkEntry(card, width=320, height=45, show="●", placeholder_text="Şifre", font=("Roboto", 14), corner_radius=10)
    e_pass.pack(pady=10)

    def giris():
        user = app.db.login_kontrol(e_user.get(), e_pass.get())
        if user:
            app.aktif_kullanici = user
            app.ana_menu()
        else:
            e_pass.delete(0, 'end')
            e_user.focus()
            messagebox.showerror("Erişim Reddedildi", "Kullanıcı bilgileri doğrulanamadı.")

    ctk.CTkButton(card, text="GÜVENLİ GİRİŞ", command=giris, width=320, height=45, font=("Roboto", 14, "bold"), corner_radius=10, fg_color=COLOR_ACCENT, hover_color="#144d7a").pack(pady=40)
    
    # Alt Bilgi
    ctk.CTkLabel(card, text="Veritabanı Bağlantısı: Aktif ✅", font=("Arial", 10), text_color="gray").pack(pady=(0, 20))

