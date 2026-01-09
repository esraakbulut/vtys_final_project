"""Teslim alma ekranı modülü"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from constants import COLOR_CARD_BG, COLOR_DANGER, COLOR_SUCCESS
from ui_helpers import style_treeview


def create_return_screen(app):
    """Teslim alma ekranını oluşturur"""
    container = app.set_content_title("Teslim Alma İşlemleri")
    
    # Filtreleme Paneli
    filter_bar = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG)
    filter_bar.pack(fill="x", pady=(0, 10), padx=10)
    
    filter_row1 = ctk.CTkFrame(filter_bar, fg_color="transparent")
    filter_row1.pack(fill="x", padx=15, pady=10)
    ctk.CTkLabel(filter_row1, text="🔍 Filtrele:", font=("Roboto", 12, "bold")).pack(side="left", padx=5)
    e_filtre = ctk.CTkEntry(filter_row1, placeholder_text="Üye Adı, Kitap Adı...", width=250)
    e_filtre.pack(side="left", padx=5)
    
    filter_row2 = ctk.CTkFrame(filter_bar, fg_color="transparent")
    filter_row2.pack(fill="x", padx=15, pady=(0, 10))
    ctk.CTkLabel(filter_row2, text="Tarih Filtresi (Opsiyonel):", font=("Roboto", 12)).pack(side="left", padx=5)
    e_tarih_min = ctk.CTkEntry(filter_row2, placeholder_text="Başlangıç (YYYY-MM-DD)", width=150)
    e_tarih_min.pack(side="left", padx=5)
    e_tarih_max = ctk.CTkEntry(filter_row2, placeholder_text="Bitiş (YYYY-MM-DD)", width=150)
    e_tarih_max.pack(side="left", padx=5)
    
    # Ana Grid: Sol Liste, Sağ Detay
    main_grid = ctk.CTkFrame(container, fg_color="transparent")
    main_grid.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Sol: Liste
    left_frame = ctk.CTkFrame(main_grid, fg_color="transparent")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    style_treeview()
    tree = ttk.Treeview(left_frame, columns=("ID", "Uye", "Kitap", "Verilis", "SonTarih", "Gecikme"), show="headings")
    cols = ["ID", "Uye", "Kitap", "Verilis", "SonTarih", "Gecikme"]
    headers = ["ID", "Üye", "Kitap", "Veriliş", "Son Teslim", "Gecikme (Gün)"]
    
    for c, h in zip(cols, headers): tree.heading(c, text=h)
    tree.column("ID", width=50)
    tree.pack(fill="both", expand=True)

    def listele():
        for i in tree.get_children(): tree.delete(i)
        
        sql = """
            SELECT 
                O.OduncID, 
                U.Ad || ' ' || U.Soyad as UyeAd,
                K.KitapAdi, 
                O.OduncTarihi, 
                O.SonTeslimTarihi,
                CASE WHEN CURRENT_DATE > O.SonTeslimTarihi THEN (CURRENT_DATE - O.SonTeslimTarihi) ELSE 0 END as Gecikme
            FROM ODUNC O
            JOIN UYE U ON O.UyeID = U.UyeID
            JOIN KITAP K ON O.KitapID = K.KitapID
            WHERE O.TeslimTarihi IS NULL
        """
        params = []
        kw = e_filtre.get()
        if kw:
            sql += " AND (U.Ad ILIKE %s OR U.Soyad ILIKE %s OR K.KitapAdi ILIKE %s)"
            k = f"%{kw}%"
            params.extend([k, k, k])
        
        tarih_min = e_tarih_min.get()
        tarih_max = e_tarih_max.get()
        if tarih_min:
            sql += " AND O.OduncTarihi >= %s"
            params.append(tarih_min)
        if tarih_max:
            sql += " AND O.OduncTarihi <= %s"
            params.append(tarih_max)
        
        sql += " ORDER BY O.SonTeslimTarihi ASC"
        
        rows = app.db.fetch_all(sql, tuple(params) if params else None)
        for r in rows:
            gecikme = r['gecikme']
            g_str = f"{gecikme} Gün" if gecikme > 0 else "-"
            tree.insert("", "end", values=(r['oduncid'], r['uyead'], r['kitapadi'], r['odunctarihi'], r['sonteslimtarihi'], g_str))
    
    e_filtre.bind("<KeyRelease>", lambda e: listele())
    e_tarih_min.bind("<KeyRelease>", lambda e: listele())
    e_tarih_max.bind("<KeyRelease>", lambda e: listele())

    # Sağ: Detay Paneli
    detail_frame = ctk.CTkFrame(main_grid, width=350, fg_color=COLOR_CARD_BG)
    detail_frame.pack(side="right", fill="y", padx=(10, 0))
    detail_frame.pack_propagate(False)
    
    ctk.CTkLabel(detail_frame, text="Seçili Kayıt Detayları", font=("Roboto", 16, "bold")).pack(pady=15)
    
    detail_content = ctk.CTkFrame(detail_frame, fg_color="transparent")
    detail_content.pack(fill="both", expand=True, padx=15, pady=10)
    
    lbl_uye = ctk.CTkLabel(detail_content, text="Üye: -", font=("Roboto", 12), anchor="w")
    lbl_uye.pack(fill="x", pady=5)
    lbl_kitap = ctk.CTkLabel(detail_content, text="Kitap: -", font=("Roboto", 12), anchor="w")
    lbl_kitap.pack(fill="x", pady=5)
    lbl_odunc = ctk.CTkLabel(detail_content, text="Ödünç Tarihi: -", font=("Roboto", 12), anchor="w")
    lbl_odunc.pack(fill="x", pady=5)
    lbl_son = ctk.CTkLabel(detail_content, text="Son Teslim Tarihi: -", font=("Roboto", 12), anchor="w")
    lbl_son.pack(fill="x", pady=5)
    lbl_gecikme = ctk.CTkLabel(detail_content, text="Gecikme: -", font=("Roboto", 12, "bold"), anchor="w", text_color=COLOR_DANGER)
    lbl_gecikme.pack(fill="x", pady=5)
    
    def secim_degisti(e):
        sel = tree.selection()
        if sel:
            item = tree.item(sel[0])
            values = item['values']
            lbl_uye.configure(text=f"Üye: {values[1]}")
            lbl_kitap.configure(text=f"Kitap: {values[2]}")
            lbl_odunc.configure(text=f"Ödünç Tarihi: {values[3]}")
            lbl_son.configure(text=f"Son Teslim Tarihi: {values[4]}")
            gecikme_txt = values[5]
            if gecikme_txt != "-":
                lbl_gecikme.configure(text=f"Gecikme: {gecikme_txt}", text_color=COLOR_DANGER)
            else:
                lbl_gecikme.configure(text="Gecikme: Yok", text_color=COLOR_SUCCESS)
        else:
            lbl_uye.configure(text="Üye: -")
            lbl_kitap.configure(text="Kitap: -")
            lbl_odunc.configure(text="Ödünç Tarihi: -")
            lbl_son.configure(text="Son Teslim Tarihi: -")
            lbl_gecikme.configure(text="Gecikme: -", text_color=COLOR_DANGER)
    
    tree.bind("<<TreeviewSelect>>", secim_degisti)

    def teslim():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen bir kayıt seçiniz.")
            return
        
        item = tree.item(sel[0])
        oid = item['values'][0]
        uye_ad = item['values'][1]
        kitap_ad = item['values'][2]
        gecikme_txt = item['values'][5]
        
        # Gecikme bilgisini kontrol et
        gecikme_gun = 0
        if gecikme_txt != "-":
            try:
                gecikme_gun = int(gecikme_txt.split()[0])
            except:
                pass
        
        msg = f"{uye_ad} adlı üyenin '{kitap_ad}' kitabı teslim alınacak."
        if gecikme_gun > 0:
            tahmini_ceza = gecikme_gun * 5.0
            msg += f"\n\n⚠️ DİKKAT: {gecikme_gun} gün gecikme var!\nTahmini Ceza: {tahmini_ceza:.2f} ₺"
                
        if messagebox.askyesno("Onay", msg):
            # Teslim al (Giriş yapan personel ID'si ile)
            staff_id = app.aktif_kullanici['kullaniciid']
            succ_teslim, msg_teslim = app.db.sp_teslim_al(oid, staff_id)
            if succ_teslim:
                # Ceza kontrolü yap
                ceza_kontrol = app.db.fetch_all(
                    "SELECT Tutar, Aciklama FROM CEZA WHERE OduncID = %s ORDER BY Tarih DESC LIMIT 1",
                    (oid,)
                )
                final_msg = "Kitap teslim alındı."
                if ceza_kontrol and len(ceza_kontrol) > 0:
                    ceza = ceza_kontrol[0]
                    final_msg += f"\n\n{ceza['aciklama']} - {ceza['tutar']:.2f} ₺ ceza eklendi."
                
                messagebox.showinfo("Başarılı", final_msg)
                listele()
                # Detayları temizle
                tree.selection_set([])
                secim_degisti(None)
            else:
                messagebox.showerror("Hata", msg_teslim)
    
    # Buton
    btn_frame = ctk.CTkFrame(container, fg_color="transparent")
    btn_frame.pack(fill="x", padx=10, pady=10)
    ctk.CTkButton(btn_frame, text="✅ TESLİM AL", command=teslim, fg_color=COLOR_SUCCESS, height=50, font=("Roboto", 16, "bold")).pack(side="right")
    
    listele()

