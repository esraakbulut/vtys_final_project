"""Ödünç verme ekranı modülü"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from constants import COLOR_CARD_BG, COLOR_ACCENT, COLOR_WARNING


def create_lending_screen(app):
    """Ödünç verme ekranını oluşturur"""
    container = app.set_content_title("Ödünç Verme İşlemi")
    
    # Alt Panel (İşlem Butonu) - En alta sabitle
    bottom = ctk.CTkFrame(container, fg_color="transparent")
    bottom.pack(side="bottom", fill="x", pady=20)

    # Grid: Sol (Üye Seçimi), Sağ (Kitap Seçimi)
    grid = ctk.CTkFrame(container, fg_color="transparent")
    grid.pack(side="top", fill="both", expand=True, pady=10)
    
    app.secilen_uye_id = None
    app.secilen_kitap_id = None
    
    # --- SOL PANEL: ÜYE SEÇİMİ ---
    left = ctk.CTkFrame(grid, fg_color=COLOR_CARD_BG)
    left.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    ctk.CTkLabel(left, text="1. Adım: Üye Seçimi", font=("Roboto", 16, "bold")).pack(pady=10)
    e_uye_ara = ctk.CTkEntry(left, placeholder_text="Üye Ara (Ad/Soyad)...")
    e_uye_ara.pack(fill="x", padx=10, pady=(0, 10))
    
    tr_uye = ttk.Treeview(left, columns=("ID", "Ad", "Soyad", "Borc"), show="headings", height=10)
    for c in ["ID", "Ad", "Soyad", "Borc"]: tr_uye.heading(c, text=c)
    tr_uye.column("ID", width=30); tr_uye.column("Borc", width=60)
    tr_uye.pack(fill="both", expand=True, padx=10)
    
    lbl_secilen_uye = ctk.CTkLabel(left, text="Seçilen Üye: Yok", font=("Roboto", 14), text_color=COLOR_WARNING)
    lbl_secilen_uye.pack(pady=10)
    
    # Üye Listeleme
    def listele_uye(kw=""):
        for i in tr_uye.get_children(): tr_uye.delete(i)
        res = app.db.arama_uye(kw) if kw else app.db.fetch_all("SELECT * FROM UYE ORDER BY UyeID DESC LIMIT 50")
        for r in res:
            tr_uye.insert("", "end", values=(r['uyeid'], r['ad'], r['soyad'], f"{r['toplamborc']} ₺"))
    
    e_uye_ara.bind("<KeyRelease>", lambda e: listele_uye(e_uye_ara.get()))
    listele_uye()
    
    def uye_sec(e):
        sel = tr_uye.selection()
        if sel:
            vals = tr_uye.item(sel[0])['values']
            app.secilen_uye_id = vals[0]
            lbl_secilen_uye.configure(text=f"Seçilen: {vals[1]} {vals[2]} (ID: {vals[0]})")
            # Bonus: Aktif ödünçleri göster
            goster_aktif_odunc(app.secilen_uye_id)
    
    tr_uye.bind("<<TreeviewSelect>>", uye_sec)
    
    # --- BONUS: SEÇİLİ ÜYENİN AKTİF KİTAPLARI ---
    frame_aktif = ctk.CTkFrame(left, fg_color="#333", height=100)
    frame_aktif.pack(fill="x", padx=10, pady=10)
    ctk.CTkLabel(frame_aktif, text="Üyenin Elindeki Kitaplar:", font=("Arial", 11)).pack(anchor="w", padx=5)
    lbl_aktif_list = ctk.CTkLabel(frame_aktif, text="-", font=("Arial", 11), text_color="#ccc")
    lbl_aktif_list.pack(anchor="w", padx=5)
    
    def goster_aktif_odunc(uid):
        q = "SELECT KitapAdi FROM ODUNC JOIN KITAP ON ODUNC.KitapID = KITAP.KitapID WHERE UyeID=%s AND TeslimTarihi IS NULL"
        res = app.db.fetch_all(q, (uid,))
        if res:
            txt = "\n".join([f"• {r['kitapadi']}" for r in res])
            lbl_aktif_list.configure(text=txt)
        else:
            lbl_aktif_list.configure(text="Elinde kitap yok.")
    
    # --- SAĞ PANEL: KİTAP SEÇİMİ ---
    right = ctk.CTkFrame(grid, fg_color=COLOR_CARD_BG)
    right.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    ctk.CTkLabel(right, text="2. Adım: Kitap Seçimi", font=("Roboto", 16, "bold")).pack(pady=10)
    e_kitap_ara = ctk.CTkEntry(right, placeholder_text="Kitap Ara (Ad/Yazar)...")
    e_kitap_ara.pack(fill="x", padx=10, pady=(0, 10))
    
    tr_kitap = ttk.Treeview(right, columns=("ID", "Kitap", "Yazar", "Stok"), show="headings", height=15)
    for c in ["ID", "Kitap", "Yazar", "Stok"]: tr_kitap.heading(c, text=c)
    tr_kitap.column("ID", width=30); tr_kitap.column("Stok", width=40)
    tr_kitap.pack(fill="both", expand=True, padx=10)
    
    lbl_secilen_kitap = ctk.CTkLabel(right, text="Seçilen Kitap: Yok", font=("Roboto", 14), text_color=COLOR_WARNING)
    lbl_secilen_kitap.pack(pady=10)
    
    def listele_kitap(kw=""):
        for i in tr_kitap.get_children(): tr_kitap.delete(i)
        res = app.db.arama_kitap(kw) if kw else app.db.fetch_all("SELECT * FROM KITAP ORDER BY KitapID ASC LIMIT 50")
        for r in res:
            tr_kitap.insert("", "end", values=(r['kitapid'], r['kitapadi'], r['yazar'], r['mevcutadet']))
    
    e_kitap_ara.bind("<KeyRelease>", lambda e: listele_kitap(e_kitap_ara.get()))
    listele_kitap()
    
    def kitap_sec(e):
        sel = tr_kitap.selection()
        if sel:
            vals = tr_kitap.item(sel[0])['values']
            app.secilen_kitap_id = vals[0]
            stok = vals[3]
            lbl_secilen_kitap.configure(text=f"Seçilen: {vals[1]} (Stok: {stok})")
    
    tr_kitap.bind("<<TreeviewSelect>>", kitap_sec)
    
    # --- ALT PANEL: İŞLEM ---
    # bottom frame is created at the top
    
    def odunc_ver():
        if not app.secilen_uye_id or not app.secilen_kitap_id:
            messagebox.showwarning("Uyarı", "Lütfen hem üye hem kitap seçiniz.")
            return
        
        succ, msg = app.db.sp_yeni_odunc(app.secilen_uye_id, app.secilen_kitap_id, app.aktif_kullanici['kullaniciid'])
        if succ:
            messagebox.showinfo("Başarılı", msg)
            listele_kitap(e_kitap_ara.get()) # Stok güncelle
            listele_uye(e_uye_ara.get()) # Cache refresh
            goster_aktif_odunc(app.secilen_uye_id)
        else:
            messagebox.showerror("Hata", msg)
    
    ctk.CTkButton(bottom, text="✅ ÖDÜNÇ İŞLEMİNİ TAMAMLA", command=odunc_ver, height=50, width=300, font=("Roboto", 16, "bold"), fg_color=COLOR_ACCENT).pack(pady=10)

