"""Raporlar ekranı modülü"""
import customtkinter as ctk
from tkinter import messagebox
from constants import COLOR_CARD_BG, COLOR_ACCENT
from ui_helpers import style_treeview, create_treeview, create_button_frame, create_csv_button, veriyi_csv_indir


def create_overdue_tab(app, parent):
    """Geciken kitaplar raporu tab'ı"""
    style_treeview()
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    columns = ("Uye", "Kitap", "Tarih", "SonTarih", "Gecikme")
    headers = ("Üye", "Kitap", "Veriliş", "Son Teslim", "Gecikme (Gün)")
    tree = create_treeview(frame, columns, headers)
    tree.pack(fill="both", expand=True)
    
    app.gecikenler_data = []
    
    def yukle():
        for item in tree.get_children():
            tree.delete(item)
        app.gecikenler_data = app.db.get_overdue_books()
        for r in app.gecikenler_data:
            tree.insert("", "end", values=(
                r['uyead'], r['kitapadi'], r['odunctarihi'], 
                r['sonteslimtarihi'], f"{r['gecikmegun']} Gün"
            ))
    
    btn_frame = create_button_frame(parent)
    ctk.CTkButton(btn_frame, text="Yenile", command=yukle, 
                 width=100, fg_color=COLOR_ACCENT).pack(side="left", padx=5)
    create_csv_button(btn_frame, veriyi_csv_indir, app.gecikenler_data,
                     ["UyeAd", "KitapAdi", "OduncTarihi", "SonTeslimTarihi", "GecikmeGun"],
                     "geciken_kitaplar.csv", side="left", 
                     keys=["uyead", "kitapadi", "odunctarihi", "sonteslimtarihi", "gecikmegun"])
    yukle()


def create_date_range_tab(app, parent):
    """Tarih bazlı ödünç raporu tab'ı"""
    style_treeview()
    filter_frame = ctk.CTkFrame(parent, fg_color="transparent")
    filter_frame.pack(pady=10, fill="x", padx=10)
    
    # Tarih aralığı
    row1 = ctk.CTkFrame(filter_frame, fg_color="transparent")
    row1.pack(fill="x", pady=5)
    ctk.CTkLabel(row1, text="Başlangıç:", font=("Roboto", 12)).pack(side="left", padx=5)
    d1 = ctk.CTkEntry(row1, placeholder_text="YYYY-MM-DD", width=120)
    d1.pack(side="left", padx=5)
    ctk.CTkLabel(row1, text="Bitiş:", font=("Roboto", 12)).pack(side="left", padx=5)
    d2 = ctk.CTkEntry(row1, placeholder_text="YYYY-MM-DD", width=120)
    d2.pack(side="left", padx=5)
    
    # Filtreler
    row2 = ctk.CTkFrame(filter_frame, fg_color="transparent")
    row2.pack(fill="x", pady=5)
    ctk.CTkLabel(row2, text="Kategori:", font=("Roboto", 12)).pack(side="left", padx=5)
    cmb_kat = ctk.CTkComboBox(row2, values=["Tümü"] + app.db.get_categories(), width=150)
    cmb_kat.set("Tümü")
    cmb_kat.pack(side="left", padx=5)
    
    ctk.CTkLabel(row2, text="Üye:", font=("Roboto", 12)).pack(side="left", padx=5)
    uyeler = app.db.get_all_uyeler()
    uye_list = ["Tümü"] + [f"{u['uyeid']} - {u['adsoyad']}" for u in uyeler]
    cmb_uye = ctk.CTkComboBox(row2, values=uye_list, width=150)
    cmb_uye.set("Tümü")
    cmb_uye.pack(side="left", padx=5)

    # Treeview
    tree_frame = ctk.CTkFrame(parent, fg_color="transparent")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Admin kontrolü: Admin ise veren/alan personel sütunlarını ekle
    # Rol kontrolünü esnek yap (admin, Admin, ADMIN olabilir)
    user_role = str(app.aktif_kullanici.get('rol', '')).lower() if app.aktif_kullanici else ''
    is_admin = (user_role == 'admin')
    
    if is_admin:
        columns = ("Uye", "Kitap", "OduncTarihi", "TeslimTarihi", "Durum", "Veren", "Alan")
        headers = ("Üye", "Kitap", "Ödünç Tarihi", "Teslim Tarihi", "Durum", "Veren Prs.", "Alan Prs.")
    else:
        columns = ("Uye", "Kitap", "OduncTarihi", "TeslimTarihi", "Durum")
        headers = ("Üye", "Kitap", "Ödünç Tarihi", "Teslim Tarihi", "Durum")

    tree = create_treeview(tree_frame, columns, headers)
    tree.pack(fill="both", expand=True)
    
    app.tarih_raporu_data = []

    def ara():
        for item in tree.get_children():
            tree.delete(item)
        if not d1.get() or not d2.get(): 
            messagebox.showwarning("Uyarı", "Lütfen başlangıç ve bitiş tarihlerini giriniz.")
            return
        
        uye_id = None
        secilen_uye = cmb_uye.get()
        if secilen_uye and secilen_uye != "Tümü":
            uye_id = int(secilen_uye.split(" - ")[0])
        
        app.tarih_raporu_data = app.db.rapor_tarih_araligi(d1.get(), d2.get(), cmb_kat.get(), uye_id)
        for r in app.tarih_raporu_data:
            teslim_tarihi = str(r['teslimtarihi']) if r['teslimtarihi'] else "-"
            durum = r.get('durum', 'TESLİM EDİLMEDİ')
            
            vals = [r['uyead'], r['kitapadi'], r['odunctarihi'], teslim_tarihi, durum]
            if is_admin:
                vals.append(r.get('verenpersonel', '-'))
                vals.append(r.get('alanpersonel', '-'))
            
            tree.insert("", "end", values=tuple(vals))

    btn_frame = create_button_frame(filter_frame)
    ctk.CTkButton(btn_frame, text="Raporla", command=ara, fg_color=COLOR_ACCENT, width=100).pack(side="left", padx=5)
    
    export_cols = ["UyeAd", "KitapAdi", "OduncTarihi", "TeslimTarihi", "Kategori", "Durum"]
    export_keys = ["uyead", "kitapadi", "odunctarihi", "teslimtarihi", "kategori", "durum"]
    
    if is_admin:
        export_cols.extend(["VerenPersonel", "AlanPersonel"])
        export_keys.extend(["verenpersonel", "alanpersonel"])

    create_csv_button(btn_frame, veriyi_csv_indir, app.tarih_raporu_data,
                     export_cols,
                     "tarih_raporu.csv", side="left",
                     keys=export_keys)


def create_popular_tab(app, parent):
    """En çok ödünç alınan kitaplar raporu tab'ı"""
    style_treeview()
    filter_frame = ctk.CTkFrame(parent, fg_color="transparent")
    filter_frame.pack(fill="x", pady=10, padx=10)
    
    row = ctk.CTkFrame(filter_frame, fg_color="transparent")
    row.pack(fill="x", pady=5)
    ctk.CTkLabel(row, text="Başlangıç (Opsiyonel):", font=("Roboto", 12)).pack(side="left", padx=5)
    d1 = ctk.CTkEntry(row, placeholder_text="YYYY-MM-DD", width=120)
    d1.pack(side="left", padx=5)
    ctk.CTkLabel(row, text="Bitiş (Opsiyonel):", font=("Roboto", 12)).pack(side="left", padx=5)
    d2 = ctk.CTkEntry(row, placeholder_text="YYYY-MM-DD", width=120)
    d2.pack(side="left", padx=5)
    
    tree_frame = ctk.CTkFrame(parent, fg_color="transparent")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
    tree = create_treeview(tree_frame, ("Kitap", "Sayi"), ("Kitap Adı", "Ödünç Sayısı"))
    tree.pack(fill="both", expand=True)
    
    app.populer_data = []
    
    def yukle():
        for item in tree.get_children():
            tree.delete(item)
        baslangic = d1.get() if d1.get() else None
        bitis = d2.get() if d2.get() else None
        app.populer_data = app.db.rapor_en_cok_okunan(baslangic, bitis)
        for r in app.populer_data:
            tree.insert("", "end", values=(r['kitapadi'], r['okunmasayisi']))
    
    btn_frame = create_button_frame(parent)
    ctk.CTkButton(btn_frame, text="Raporla", command=yukle, fg_color=COLOR_ACCENT, width=100).pack(side="left", padx=5)
    create_csv_button(btn_frame, veriyi_csv_indir, app.populer_data,
                     ["KitapAdi", "OkunmaSayisi"],
                     "populer_kitaplar.csv", side="left",
                     keys=["kitapadi", "okunmasayisi"])
    yukle()


def create_report_screen(app):
    """Raporlar ekranını oluşturur"""
    container = app.set_content_title("Sistem Raporları")
    tab = ctk.CTkTabview(container, fg_color=COLOR_CARD_BG)
    tab.pack(fill="both", expand=True)
    
    tab1 = tab.add("⚠️ Gecikenler")
    tab2 = tab.add("📅 Tarih Bazlı")
    tab3 = tab.add("⭐ Popüler")
    
    create_overdue_tab(app, tab1)
    create_date_range_tab(app, tab2)
    create_popular_tab(app, tab3)

