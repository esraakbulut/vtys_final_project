"""Dinamik sorgu ekranı modülü"""
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from constants import COLOR_CARD_BG, COLOR_ACCENT
from ui_helpers import style_treeview, veriyi_csv_indir


def create_query_screen(app):
    """Dinamik sorgu ekranını oluşturur"""
    container = app.set_content_title("Detaylı Kitap Arama")

    frm = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG)
    frm.pack(fill="x", pady=10, ipady=10)
    
    # 1. Satır Filtreler
    row1 = ctk.CTkFrame(frm, fg_color="transparent")
    row1.pack(fill="x", padx=10, pady=5)

    ctk.CTkEntry(row1, placeholder_text="Kitap Adı (Kısmi)", width=200).pack(side="left", padx=5)
    e_ad = row1.winfo_children()[-1]
    
    ctk.CTkEntry(row1, placeholder_text="Yazar", width=200).pack(side="left", padx=5)
    e_yazar = row1.winfo_children()[-1]

    # Kategori ComboBox
    cats = ["Tümü"] + app.db.get_categories()
    cmb_kat = ctk.CTkComboBox(row1, values=cats, width=150)
    cmb_kat.set("Tümü")
    cmb_kat.pack(side="left", padx=5)

    # 2. Satır Filtreler (Yıl Aralığı ve Sıralama)
    row2 = ctk.CTkFrame(frm, fg_color="transparent")
    row2.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(row2, text="Yıl Aralığı:", font=("Roboto", 12)).pack(side="left", padx=5)
    e_yil_min = ctk.CTkEntry(row2, placeholder_text="Min", width=60)
    e_yil_min.pack(side="left", padx=2)
    e_yil_max = ctk.CTkEntry(row2, placeholder_text="Max", width=60)
    e_yil_max.pack(side="left", padx=2)
    
    var_stok = ctk.BooleanVar()
    ctk.CTkCheckBox(row2, text="Stokta Var", variable=var_stok).pack(side="left", padx=20)
    
    # BONUS: SIRALAMA
    ctk.CTkLabel(row2, text="Sırala:", font=("Roboto", 12)).pack(side="left", padx=(20, 5))
    cmb_sort = ctk.CTkComboBox(row2, values=["KitapAdi (A-Z)", "KitapAdi (Z-A)", "BasimYili (Artan)", "BasimYili (Azalan)"], width=150)
    cmb_sort.set("KitapAdi (A-Z)")
    cmb_sort.pack(side="left", padx=5)

    # Tablo
    style_treeview()
    tr_frame = ctk.CTkFrame(container, fg_color="transparent")
    tr_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    tr = ttk.Treeview(tr_frame, columns=("ID", "Ad", "Yazar", "Kategori", "Yil", "Stok"), show="headings")
    for c in ["ID", "Ad", "Yazar", "Kategori", "Yil", "Stok"]: tr.heading(c, text=c)
    tr.column("ID", width=50)
    tr.pack(fill="both", expand=True)

    app.sorgu_sonucu_cache = []

    def ara():
        # Dinamik SQL Oluşturma
        sql = "SELECT KitapID, KitapAdi, Yazar, Kategori, BasimYili, MevcutAdet FROM KITAP WHERE 1=1"
        params = []

        if e_ad.get():
            sql += " AND KitapAdi ILIKE %s"
            params.append(f"%{e_ad.get()}%")
        
        if e_yazar.get():
            sql += " AND Yazar ILIKE %s"
            params.append(f"%{e_yazar.get()}%")
        
        secilen_kat = cmb_kat.get()
        if secilen_kat and secilen_kat != "Tümü":
            sql += " AND Kategori = %s"
            params.append(secilen_kat)

        if e_yil_min.get() and e_yil_min.get().strip().isdigit():
            sql += " AND BasimYili >= %s"
            params.append(int(e_yil_min.get().strip()))
        
        if e_yil_max.get() and e_yil_max.get().strip().isdigit():
            sql += " AND BasimYili <= %s"
            params.append(int(e_yil_max.get().strip()))

        if var_stok.get():
            sql += " AND MevcutAdet > 0"
        
        # Sıralama - Daha gelişmiş sıralama seçenekleri
        sort_val = cmb_sort.get()
        if "KitapAdi (A-Z)" in sort_val: 
            sql += " ORDER BY KitapAdi ASC"
        elif "KitapAdi (Z-A)" in sort_val: 
            sql += " ORDER BY KitapAdi DESC"
        elif "BasimYili (Artan)" in sort_val: 
            sql += " ORDER BY BasimYili ASC"
        elif "BasimYili (Azalan)" in sort_val: 
            sql += " ORDER BY BasimYili DESC"
        else:
            sql += " ORDER BY KitapAdi ASC"  # Varsayılan

        app.sorgu_sonucu_cache = app.db.fetch_all(sql, tuple(params) if params else None)
        
        for i in tr.get_children(): tr.delete(i)
        for r in app.sorgu_sonucu_cache:
            tr.insert("", "end", values=(r['kitapid'], r['kitapadi'], r['yazar'], r['kategori'], r['basimyili'], r['mevcutadet']))
    
    def export_indir():
        if not app.sorgu_sonucu_cache:
            messagebox.showwarning("Uyarı", "Önce sorgu yapınız.")
            return
        
        # Export format seçimi
        format_sec = messagebox.askyesno("Format Seçimi", "CSV formatında kaydetmek için 'Evet'e, PDF formatında kaydetmek için 'Hayır'a basın.\n\nNot: CSV dosyaları Excel'de de açılabilir.")
        
        if format_sec:  # CSV
            cols = ["KitapID", "KitapAdi", "Yazar", "Kategori", "BasimYili", "MevcutAdet"]
            keys = ["kitapid", "kitapadi", "yazar", "kategori", "basimyili", "mevcutadet"]
            veriyi_csv_indir(cols, app.sorgu_sonucu_cache, "sorgu_sonucu.csv", keys=keys)
        else:  # PDF (basit HTML tablo olarak kaydet, PDF viewer ile açılabilir)
            try:
                dosya_yolu = filedialog.asksaveasfilename(
                    initialfile="sorgu_sonucu.html",
                    defaultextension=".html",
                    filetypes=[("HTML Dosyası", "*.html"), ("Tüm Dosyalar", "*.*")]
                )
                if not dosya_yolu:
                    return
                
                cols = ["KitapID", "KitapAdi", "Yazar", "Kategori", "BasimYili", "MevcutAdet"]
                keys = ["kitapid", "kitapadi", "yazar", "kategori", "basimyili", "mevcutadet"]
                
                html_content = "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Kitap Sorgu Sonuçları</title>"
                html_content += "<style>body{font-family:Arial;margin:20px;}table{border-collapse:collapse;width:100%;}th,td{border:1px solid #ddd;padding:8px;text-align:left;}th{background-color:#4CAF50;color:white;}</style></head><body>"
                html_content += "<h1>Kitap Sorgu Sonuçları</h1><table><tr>"
                for col in cols:
                    html_content += f"<th>{col}</th>"
                html_content += "</tr>"
                
                for row in app.sorgu_sonucu_cache:
                    html_content += "<tr>"
                    for key in keys:
                        val = str(row.get(key, ''))
                        html_content += f"<td>{val}</td>"
                    html_content += "</tr>"
                
                html_content += "</table></body></html>"
                
                with open(dosya_yolu, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                messagebox.showinfo("Başarılı", f"HTML dosyası kaydedildi:\n{dosya_yolu}\n\nNot: Bu dosya tarayıcıda açılabilir ve PDF olarak yazdırılabilir.")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilirken hata oluştu:\n{str(e)}")

    # Butonlar
    btn_frm = ctk.CTkFrame(frm, fg_color="transparent")
    btn_frm.pack(side="right", padx=10, pady=5)
    
    ctk.CTkButton(btn_frm, text="🔍 SORGULA", command=ara, width=140, fg_color=COLOR_ACCENT, font=("Roboto", 12, "bold")).pack(side="left", padx=5)
    ctk.CTkButton(btn_frm, text="📥 İndir (CSV/PDF)", command=export_indir, width=150, fg_color="#555").pack(side="left", padx=5)

