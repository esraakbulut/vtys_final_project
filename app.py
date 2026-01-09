"""
Ana uygulama dosyası - Kütüphane Yönetim Sistemi
Modüler yapı: Tüm ekranlar screens/ klasöründe, yardımcı fonksiyonlar ui_helpers.py'de
"""
import customtkinter as ctk
from db_manager import DBManager
from constants import (COLOR_SIDEBAR, COLOR_MAIN_BG, COLOR_CARD_BG, COLOR_ACCENT, 
                       COLOR_TEXT_MAIN, COLOR_TEXT_SUB, COLOR_DANGER, COLOR_BTN_HOVER, 
                       COLOR_BTN_DANGER_HOVER)

# Ekranları import et
from screens.login_screen import create_login_screen
from screens.dashboard_screen import create_dashboard
from screens.member_screen import create_member_screen
from screens.book_screen import create_book_screen
from screens.category_screen import create_category_screen
from screens.lending_screen import create_lending_screen
from screens.return_screen import create_return_screen
from screens.penalty_screen import create_penalty_screen
from screens.report_screen import create_report_screen
from screens.query_screen import create_query_screen


class KutuphaneApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kütüphane Yönetim Sistemi | v2.0 Pro")
        self.geometry("1400x900")
        
        self.db = DBManager()
        self.db.init_users()  # Kullanıcıları oluştur/kontrol et
        self.db.init_categories()  # Kategorileri hazırla
        self.aktif_kullanici = None

        # Grid yapılandırması
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.giris_ekrani()

    def temize_cek(self):
        """Ekranda ne varsa temizler"""
        for widget in self.winfo_children():
            widget.destroy()

    def giris_ekrani(self):
        """Giriş ekranını gösterir"""
        create_login_screen(self)

    def ana_menu(self):
        """Ana menüyü oluşturur"""
        self.temize_cek()
        
        # --- SOL MENÜ (SIDEBAR) ---
        sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLOR_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)  # Genişliği sabitle

        # Logo Alanı
        logo_frm = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frm.pack(pady=40)
        ctk.CTkLabel(logo_frm, text="🎓 OMÜ", font=("Roboto", 30, "bold"), text_color=COLOR_ACCENT).pack()
        ctk.CTkLabel(logo_frm, text="Kütüphane Yönetimi", font=("Roboto", 12), text_color=COLOR_TEXT_SUB).pack()

        # Menü Butonları
        self.menu_buttons = []
        buttons = [
            ("📊  Genel Bakış", self.dashboard_goster),
            ("👥  Üye İşlemleri", self.uye_yonetimi),
            ("📚  Kitap İşlemleri", self.kitap_yonetimi),
            ("🏷️  Kategori Yönetimi", self.kategori_yonetimi),
            ("➡️  Ödünç Ver", self.odunc_verme_ekrani),
            ("⬅️  Teslim Al", self.teslim_alma_ekrani),
            ("⚖️  Cezalar", self.ceza_ekrani),
            ("📈  Raporlar", self.rapor_ekrani),
            ("🔍  Sorgulama", self.dinamik_sorgu_ekrani)
        ]

        for txt, cmd in buttons:
            btn = ctk.CTkButton(sidebar, text=txt, command=cmd,
                                fg_color="transparent", hover_color=COLOR_BTN_HOVER,
                                anchor="w", height=45, font=("Roboto", 14), corner_radius=8)
            btn.pack(fill="x", pady=2, padx=15)
            self.menu_buttons.append(btn)

        # Çıkış Butonu (En altta)
        ctk.CTkButton(sidebar, text="🚪 Çıkış Yap", command=self.giris_ekrani,
                      fg_color=COLOR_DANGER, hover_color=COLOR_BTN_DANGER_HOVER,
                      height=40, font=("Roboto", 14, "bold")).pack(side="bottom", fill="x", padx=20, pady=30)

        # --- SAĞ İÇERİK ALANI ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_MAIN_BG)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        
        # İlk açılışta Dashboard göster
        self.dashboard_goster()

    def set_content_title(self, title):
        """Sağ paneldeki başlığı ve eski içeriği temizler"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = ctk.CTkFrame(self.main_frame, height=80, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        
        ctk.CTkLabel(header, text=title, font=("Roboto", 32, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")
        
        # Kullanıcı rozeti
        user_badge = ctk.CTkFrame(header, fg_color=COLOR_CARD_BG, corner_radius=20)
        user_badge.pack(side="right")
        ctk.CTkLabel(user_badge, text=f"👤 {self.aktif_kullanici['kullaniciadi']} ({self.aktif_kullanici['rol']})",
                     font=("Roboto", 14), padx=20, pady=10).pack()

        # İçerik konteyner
        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        return content

    # Ekran metodları - screens modüllerinden import edilen fonksiyonları çağırır
    def dashboard_goster(self):
        """Dashboard ekranını gösterir"""
        create_dashboard(self)

    def uye_yonetimi(self):
        """Üye yönetimi ekranını gösterir"""
        create_member_screen(self)

    def kitap_yonetimi(self):
        """Kitap yönetimi ekranını gösterir"""
        create_book_screen(self)

    def kategori_yonetimi(self):
        """Kategori yönetimi ekranını gösterir"""
        create_category_screen(self)

    def odunc_verme_ekrani(self):
        """Ödünç verme ekranını gösterir"""
        create_lending_screen(self)

    def teslim_alma_ekrani(self):
        """Teslim alma ekranını gösterir"""
        create_return_screen(self)

    def ceza_ekrani(self):
        """Ceza ekranını gösterir"""
        create_penalty_screen(self)

    def rapor_ekrani(self):
        """Raporlar ekranını gösterir"""
        create_report_screen(self)

    def dinamik_sorgu_ekrani(self):
        """Dinamik sorgu ekranını gösterir"""
        create_query_screen(self)


if __name__ == "__main__":
    app = KutuphaneApp()
    app.mainloop()

