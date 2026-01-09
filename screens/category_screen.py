"""Kategori yönetimi ekranı modülü"""
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from constants import COLOR_CARD_BG


def create_category_screen(app):
    """Kategori yönetimi ekranını oluşturur"""
    container = app.set_content_title("Kategori Yönetimi")
    
    # Grid Yapı (Sol form, Sağ liste)
    grid = ctk.CTkFrame(container, fg_color="transparent")
    grid.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Sol Taraf: İşlemler
    left = ctk.CTkFrame(grid, width=300, fg_color=COLOR_CARD_BG)
    left.pack(side="left", fill="y", padx=(0, 20))
    
    ctk.CTkLabel(left, text="Kategori İşlemleri", font=("Roboto", 16, "bold")).pack(pady=20)
    e_kat = ctk.CTkEntry(left, placeholder_text="Kategori Adı", width=250)
    e_kat.pack(pady=10)
    
    def temizle(): e_kat.delete(0, 'end')
    
    def listele():
        # Temizle
        for widget in right_scroll.winfo_children(): widget.destroy()
        cats = app.db.get_categories()
        
        for cat in cats:
            row = ctk.CTkFrame(right_scroll, fg_color="#333", height=50)
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=cat, font=("Roboto", 14), anchor="w").pack(side="left", padx=20)
            
            # Sil butonu
            def sil(c=cat):
                if messagebox.askyesno("Sil", f"'{c}' kategorisi silinsin mi?"):
                    succ, msg = app.db.kategori_sil(c)
                    if succ: listele(); messagebox.showinfo("Başarılı", "Silindi")
                    else: messagebox.showerror("Hata", msg)
            
            # Düzenle butonu
            def duzenle(c=cat):
                yeni = simpledialog.askstring("Düzenle", "Yeni Kategori Adı:", initialvalue=c)
                if yeni:
                    succ, msg = app.db.kategori_guncelle(c, yeni)
                    if succ: listele()
                    else: messagebox.showerror("Hata", msg)

            ctk.CTkButton(row, text="🗑️", width=40, height=30, fg_color="#c0392b", command=sil).pack(side="right", padx=10, pady=10)
            ctk.CTkButton(row, text="✏️", width=40, height=30, fg_color="#e67e22", command=duzenle).pack(side="right", padx=5)

    def ekle():
        ad = e_kat.get()
        if not ad: return
        succ, msg = app.db.kategori_ekle(ad)
        if succ: 
            temizle(); listele(); messagebox.showinfo("Başarılı", "Eklendi")
        else:
            messagebox.showerror("Hata", msg)

    ctk.CTkButton(left, text="EKLE", command=ekle, width=250, fg_color="green").pack(pady=10)

    # Sağ Taraf: Liste
    right = ctk.CTkFrame(grid, fg_color="transparent")
    right.pack(side="right", fill="both", expand=True)
    
    ctk.CTkLabel(right, text="Mevcut Kategoriler", font=("Roboto", 16, "bold")).pack(pady=(0, 10), anchor="w")
    
    right_scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
    right_scroll.pack(fill="both", expand=True)
    
    listele()

