"""Kitap yönetimi ekranı modülü"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from constants import COLOR_CARD_BG, COLOR_ACCENT, COLOR_SUCCESS
from ui_helpers import style_treeview, veriyi_csv_indir


def create_book_screen(app):
    """Kitap yönetimi ekranını oluşturur"""
    container = app.set_content_title("Kitap Envanteri")

    # --- ARAMA PANELİ ---
    search_frame = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG)
    search_frame.pack(fill="x", pady=(0, 10))
    
    ctk.CTkLabel(search_frame, text="🔍 Kitap Ara:", font=("Roboto", 14, "bold")).pack(side="left", padx=15, pady=15)
    e_search = ctk.CTkEntry(search_frame, placeholder_text="Kitap Adı veya Yazar...", width=250)
    e_search.pack(side="left", padx=5)

    def ara(*args):
        kw = e_search.get()
        if kw:
            app.kitap_listesi_cache = app.db.arama_kitap(kw)
        else:
            app.kitap_listesi_cache = app.db.fetch_all("SELECT * FROM KITAP ORDER BY KitapID ASC")
        update_tree()
        
    e_search.bind("<KeyRelease>", ara)
    
    def yeni_kitap_popup():
        top = ctk.CTkToplevel(app)
        top.title("Kitap Ekleme Sihirbazı")
        top.geometry("400x580")
        top.transient(app)
        
        ctk.CTkLabel(top, text="Yeni Kitap Bilgileri", font=("Roboto", 18, "bold")).pack(pady=20)
        
        entries = {}
        # Kategori için Combobox kullanalım
        cats = app.db.get_categories()
        
        for f in ["KitapAdi", "Yazar", "Kategori", "Yayinevi", "BasimYili", "ToplamAdet"]:
            if f == "Kategori":
                ctk.CTkComboBox(top, values=cats, width=300).pack(pady=8)
            else:
                ctk.CTkEntry(top, placeholder_text=f, width=300).pack(pady=8)
            entries[f] = top.winfo_children()[-1]
        
        def kaydet():
            try:
                # Validasyon: Stok Negatif Olamaz
                stok_str = entries["ToplamAdet"].get()
                try:
                    stok = int(stok_str)
                    if stok < 0:
                        messagebox.showerror("Hata", "Stok adedi negatif olamaz!")
                        return
                except ValueError:
                    messagebox.showerror("Hata", "Lütfen geçerli bir sayı giriniz.")
                    return

                vals = tuple(entries[f].get() for f in ["KitapAdi", "Yazar", "Kategori", "Yayinevi", "BasimYili", "ToplamAdet"])
                vals = vals + (vals[-1],) # Mevcut = Toplam
                sql = "INSERT INTO KITAP (KitapAdi, Yazar, Kategori, Yayinevi, BasimYili, ToplamAdet, MevcutAdet) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                succ, msg = app.db.calistir_query(sql, vals)
                if succ: top.destroy(); ara(); messagebox.showinfo("Başarılı", "Kitap Eklendi")
                else: messagebox.showerror("Hata", msg)
            except Exception as e: messagebox.showerror("Hata", str(e))

        ctk.CTkButton(top, text="Kaydet", command=kaydet, fg_color=COLOR_SUCCESS).pack(pady=20)

    ctk.CTkButton(search_frame, text="+ Yeni Kitap", command=yeni_kitap_popup, fg_color=COLOR_ACCENT).pack(side="right", padx=15)

    # Tablo
    style_treeview()
    tree = ttk.Treeview(container, columns=("ID", "Ad", "Yazar", "Kategori", "Stok", "Mevcut"), show="headings")
    for c in ["ID", "Ad", "Yazar", "Kategori", "Stok", "Mevcut"]: tree.heading(c, text=c)
    tree.pack(fill="both", expand=True)
    
    # Buton Barı (CSV için)
    btn_bar = ctk.CTkFrame(container, fg_color="transparent")
    btn_bar.pack(fill="x", pady=10)

    def update_tree():
        for i in tree.get_children(): tree.delete(i)
        # Cache zaten ara() ile doluyor
        if not hasattr(app, 'kitap_listesi_cache'): return
        for r in app.kitap_listesi_cache:
            tree.insert("", "end", values=(r['kitapid'], r['kitapadi'], r['yazar'], r['kategori'], r['toplamadet'], r['mevcutadet']))
    
    def csv_indir():
        if hasattr(app, 'kitap_listesi_cache'):
            cols = list(app.kitap_listesi_cache[0].keys()) if app.kitap_listesi_cache else []
            veriyi_csv_indir(cols, app.kitap_listesi_cache, "kitap_listesi.csv")

    ctk.CTkButton(btn_bar, text="📥 Listeyi İndir", command=csv_indir, fg_color="#555").pack(side="right")

    ara()

