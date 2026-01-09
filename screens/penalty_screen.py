"""Ceza ekranı modülü"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from constants import COLOR_CARD_BG, COLOR_DANGER, COLOR_SUCCESS
from ui_helpers import style_treeview


def create_penalty_screen(app):
    """Ceza ekranını oluşturur"""
    container = app.set_content_title("Ceza ve Borç Takibi")

    filter_frm = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG)
    filter_frm.pack(fill="x", pady=(0, 15), ipady=10)
    
    e_uye = ctk.CTkEntry(filter_frm, placeholder_text="Üye Adı Ara...", width=200)
    e_uye.pack(side="left", padx=10)
    
    style_treeview()
    tree = ttk.Treeview(container, columns=("ID", "Uye", "Kitap", "Tutar", "Aciklama", "Tarih", "Durum"), show="headings")
    tr_cols = ["ID", "Uye", "Kitap", "Tutar", "Aciklama", "Tarih", "Durum"]
    headers = ["ID", "Üye Adı", "Kitap Adı", "Tutar", "Açıklama", "Tarih", "Durum"]
    
    for c, h in zip(tr_cols, headers): 
        tree.heading(c, text=h)
        
    tree.column("ID", width=80)
    tree.column("Durum", width=80)
    tree.pack(fill="both", expand=True)

    lbl_total = ctk.CTkLabel(container, text="Toplam: 0.00 ₺", font=("Roboto", 20, "bold"), text_color=COLOR_DANGER)
    lbl_total.pack(pady=10, anchor="e")

    def filtrele(val=""):
        for i in tree.get_children(): tree.delete(i)
        
        rows = app.db.get_all_penalties_with_pending(val)
        
        total = 0
        for r in rows:
            durum = r.get('durum', 'Bekliyor')
            ceza_id = r.get('cezaid', '')
            tarih = r.get('tarih', 'Bekliyor')
            
            # PENDING- ile başlayan ID'ler bekleyen cezalardır (henüz CEZA tablosuna eklenmemiş)
            # Diğerleri gerçek ceza kayıtlarıdır
            is_pending = str(ceza_id).startswith('PENDING-')
            is_paid = durum == 'Ödendi'
            
            # Durum renklendirmesi için tag ekle
            if is_paid:
                tree.insert("", "end", values=(
                    ceza_id, r['uyead'], r['kitapad'], 
                    f"{float(r['tutar']):.2f} ₺", r['aciklama'], 
                    tarih, durum
                ), tags=('paid',))
            else:
                tree.insert("", "end", values=(
                    ceza_id, r['uyead'], r['kitapad'], 
                    f"{float(r['tutar']):.2f} ₺", r['aciklama'], 
                    tarih, durum
                ), tags=('pending',))
            
            # Sadece bekleyen cezaları toplam borca ekle
            if not is_paid:
                total += float(r['tutar'])
        
        # Tag renklendirmesi
        tree.tag_configure('pending', background='#fff3cd', foreground='#856404')
        tree.tag_configure('paid', background='#d4edda', foreground='#155724')
        
        lbl_total.configure(text=f"Toplam Bekleyen: {total:.2f} ₺")
    
    def ceza_ode_secilen():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen ödenecek bir ceza seçin.")
            return
        
        ceza_id_str = tree.item(sel[0])['values'][0]
        
        # PENDING- ile başlayan ID'ler henüz CEZA tablosuna eklenmemiş cezalardır
        if str(ceza_id_str).startswith('PENDING-'):
            messagebox.showinfo("Bilgi", "Bu ceza henüz kitap teslim edilmediği için ödenemez. Önce kitabı teslim alın.")
            return
        
        # Durum kontrolü
        durum = tree.item(sel[0])['values'][6]
        if durum == 'Ödendi':
            messagebox.showinfo("Bilgi", "Bu ceza zaten ödenmiş.")
            return
        
        # Onay al
        if not messagebox.askyesno("Onay", "Seçili cezayı ödendi olarak işaretlemek istediğinize emin misiniz?"):
            return
        
        # Ceza ödeme işlemi
        try:
            ceza_id = int(ceza_id_str)
            succ, msg = app.db.ceza_ode(ceza_id)
            if succ:
                messagebox.showinfo("Başarılı", msg)
                filtrele(e_uye.get())  # Listeyi yenile
            else:
                messagebox.showerror("Hata", msg)
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz ceza ID'si.")
    
    # Ödeme butonu
    btn_frm = ctk.CTkFrame(container, fg_color="transparent")
    btn_frm.pack(fill="x", pady=(10, 0))
    ctk.CTkButton(btn_frm, text="✅ Ceza Öde", command=ceza_ode_secilen, 
                 fg_color=COLOR_SUCCESS, width=150).pack(side="left", padx=5)

    ctk.CTkButton(filter_frm, text="Ara", command=lambda: filtrele(e_uye.get())).pack(side="left")
    e_uye.bind("<KeyRelease>", lambda e: filtrele(e_uye.get()))
    
    filtrele()

