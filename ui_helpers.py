"""
UI Helper fonksiyonları - Treeview, buton frame, CSV export vb.
"""

from tkinter import ttk, messagebox, filedialog
import csv
from constants import COLOR_CARD_BG, COLOR_TEXT_MAIN, COLOR_ACCENT


def style_treeview():
    """Tabloları modern ve karanlık moda uygun hale getirir"""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", 
                    background=COLOR_CARD_BG, 
                    foreground=COLOR_TEXT_MAIN, 
                    fieldbackground=COLOR_CARD_BG, 
                    rowheight=35,
                    font=("Roboto", 11))
    style.configure("Treeview.Heading", 
                    background="#1a1a1a", 
                    foreground=COLOR_TEXT_MAIN, 
                    font=("Roboto", 12, "bold"),
                    relief="flat")
    style.map("Treeview", background=[('selected', COLOR_ACCENT)])


def create_treeview(parent, columns, headers, column_widths=None):
    """Treeview oluşturur ve yapılandırır"""
    tree = ttk.Treeview(parent, columns=columns, show="headings")
    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
    if column_widths:
        for col, width in column_widths.items():
            tree.column(col, width=width)
    return tree


def create_button_frame(parent):
    """Butonlar için frame oluşturur"""
    import customtkinter as ctk
    btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
    btn_frame.pack(fill="x", pady=10, padx=10)
    return btn_frame


def create_csv_button(parent, csv_func, data, columns, filename, side="right", keys=None):
    """CSV export butonu oluşturur"""
    import customtkinter as ctk
    
    def export():
        if data:
            csv_func(columns, data, filename, keys=keys)
    
    btn = ctk.CTkButton(parent, text="📥 İndir", command=export, 
                       width=100, fg_color="#555")
    btn.pack(side=side, padx=5)
    return btn


def veriyi_csv_indir(columns, rows, default_name="rapor.csv", keys=None):
    """Verilen sütun ve satırları CSV olarak kaydeder."""
    try:
        dosya_yolu = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".csv",
            filetypes=[("CSV Dosyası", "*.csv"), ("Tüm Dosyalar", "*.*")]
        )
        
        if not dosya_yolu:
            return

        with open(dosya_yolu, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')  # Excel için noktalı virgül daha iyi
            writer.writerow(columns)
            
            # Rows dictionary listesi ise
            if rows and isinstance(rows[0], dict):
                data_keys = keys if keys else columns
                for row in rows:
                    # Columns sırasına göre değerleri al
                    values = [row.get(col, '') for col in data_keys]
                    writer.writerow(values)
            
            # Tuple veya list ise
            else: 
                writer.writerows(rows)

        messagebox.showinfo("Başarılı", f"Dosya kaydedildi:\n{dosya_yolu}")
    except Exception as e:
        messagebox.showerror("Hata", f"Dosya kaydedilirken hata oluştu:\n{str(e)}")

