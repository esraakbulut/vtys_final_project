"""Üye yönetimi ekranı modülü"""
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
from constants import COLOR_CARD_BG, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER
from ui_helpers import style_treeview, veriyi_csv_indir


# ... (imports remain the same)
def create_member_screen(app):
    """Üye yönetimi ekranını oluşturur"""
    container = app.set_content_title("Üye Yönetimi")
    
    # Ana görünüm (Liste ve Arama)
    main_view = ctk.CTkFrame(container, fg_color="transparent")
    main_view.pack(fill="both", expand=True)

    # Yeni Üye Ekleme Görünümü
    add_member_view = ctk.CTkFrame(container, fg_color="transparent")

    def show_main_view():
        add_member_view.pack_forget()
        main_view.pack(fill="both", expand=True)
        ara() # Listeyi yenile

    def show_add_member_view():
        main_view.pack_forget()
        add_member_view.pack(fill="both", expand=True)
        # Formu temizle
        for entry in add_entries.values():
            entry.delete(0, "end")

    # --- ARAMA PANELİ (Main View) ---
    search_frame = ctk.CTkFrame(main_view, fg_color=COLOR_CARD_BG)
    search_frame.pack(fill="x", pady=(0, 10))
    
    ctk.CTkLabel(search_frame, text="🔍 Hızlı Arama:", font=("Roboto", 14, "bold")).pack(side="left", padx=15, pady=15)
    e_search = ctk.CTkEntry(search_frame, placeholder_text="Ad, Soyad veya Email...", width=250)
    e_search.pack(side="left", padx=5)

    def ara(*args):
         kw = e_search.get()
         if kw:
             app.uye_listesi_cache = app.db.arama_uye(kw)
         else:
             app.uye_listesi_cache = app.db.fetch_all("SELECT * FROM UYE ORDER BY UyeID DESC")
         update_tree()

    e_search.bind("<KeyRelease>", ara)

    # Yeni Üye Butonu (Main View)
    ctk.CTkButton(search_frame, text="+ Yeni Üye", command=show_add_member_view, fg_color=COLOR_SUCCESS, width=120).pack(side="right", padx=15)

    # --- YENİ ÜYE EKLEME FORMU (Add Member View) ---
    form_frame = ctk.CTkFrame(add_member_view, fg_color=COLOR_CARD_BG)
    form_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(form_frame, text="Yeni Üye Kaydı", font=("Roboto", 18, "bold")).pack(pady=20)

    add_entries = {}
    for f in ["Ad", "Soyad", "Telefon", "Email"]:
        row = ctk.CTkFrame(form_frame, fg_color="transparent")
        row.pack(pady=10)
        ctk.CTkLabel(row, text=f"{f}:", width=100, anchor="e").pack(side="left", padx=(0, 10))
        entry = ctk.CTkEntry(row, placeholder_text=f, width=300)
        entry.pack(side="left")
        add_entries[f] = entry
    
    def kaydet():
        if not add_entries["Ad"].get(): return
        app.db.calistir_query("INSERT INTO UYE (Ad, Soyad, Telefon, Email) VALUES (%s,%s,%s,%s)", 
                               (add_entries["Ad"].get(), add_entries["Soyad"].get(), add_entries["Telefon"].get(), add_entries["Email"].get()))
        messagebox.showinfo("Başarılı", "Yeni üye eklendi.")
        show_main_view()

    btn_row = ctk.CTkFrame(form_frame, fg_color="transparent")
    btn_row.pack(pady=30)
    ctk.CTkButton(btn_row, text="İptal", command=show_main_view, fg_color=COLOR_DANGER, width=120).pack(side="left", padx=10)
    ctk.CTkButton(btn_row, text="Kaydet", command=kaydet, fg_color=COLOR_SUCCESS, width=120).pack(side="left", padx=10)


    # --- TABLO (Main View) ---
    style_treeview()
    tree_frame = ctk.CTkFrame(main_view, fg_color="transparent")
    tree_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(tree_frame, columns=("ID", "Ad", "Soyad", "Tel", "Email", "Borc"), show="headings")
    for c in ["ID", "Ad", "Soyad", "Tel", "Email", "Borc"]: tree.heading(c, text=c)
    tree.column("ID", width=50, anchor="center")
    tree.pack(fill="both", expand=True)

    def update_tree():
        for i in tree.get_children(): tree.delete(i)
        for r in app.uye_listesi_cache:
            tree.insert("", "end", values=(r['uyeid'], r['ad'], r['soyad'], r['telefon'], r['email'], f"{r['toplamborc']} ₺"))

    # Butonlar (Main View)
    btn_frm = ctk.CTkFrame(main_view, fg_color="transparent")
    btn_frm.pack(fill="x", pady=10)
    
    def islem(tur):
        sel = tree.selection()
        if not sel: return
        uid = tree.item(sel[0])['values'][0]
        
        if tur == "sil":
            if messagebox.askyesno("Onay", "Silmek istediğine emin misin?"):
                succ, msg = app.db.calistir_query("DELETE FROM UYE WHERE UyeID = %s", (uid,))
                if not succ: messagebox.showerror("Hata", msg)
                else: ara()
        elif tur == "ozet":
            succ, res = app.db.sp_uye_ozet(uid)
            if succ: messagebox.showinfo("Özet", f"Aldığı: {res['toplamalinan']}\nElindeki: {res['iadeedilmeyen']}\nCeza: {res['toplamceza']} ₺")
        elif tur == "guncelle":
            yeni = simpledialog.askstring("Güncelle", "Yeni Telefon Numarası:")
            if yeni:
                app.db.calistir_query("UPDATE UYE SET Telefon = %s WHERE UyeID = %s", (yeni, uid))
                ara()

    ctk.CTkButton(btn_frm, text="Düzenle", command=lambda: islem("guncelle"), fg_color=COLOR_WARNING, width=100).pack(side="left", padx=5)
    ctk.CTkButton(btn_frm, text="Sil", command=lambda: islem("sil"), fg_color=COLOR_DANGER, width=100).pack(side="left", padx=5)
    ctk.CTkButton(btn_frm, text="Detaylı Rapor (SP)", command=lambda: islem("ozet"), fg_color=COLOR_SUCCESS).pack(side="right")
     
    # CSV İndir Butonu
    def csv_indir():
        if hasattr(app, 'uye_listesi_cache'):
            cols = ["UyeID", "Ad", "Soyad", "Telefon", "Email", "ToplamBorc"]
            veriyi_csv_indir(cols, app.uye_listesi_cache, "uye_listesi.csv")

    ctk.CTkButton(btn_frm, text="📥 Listeyi İndir", command=csv_indir, fg_color="#555").pack(side="right", padx=10)

    ara()

