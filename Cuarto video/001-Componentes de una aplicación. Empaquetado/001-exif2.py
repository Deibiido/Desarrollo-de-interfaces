import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image

class PhotoRenamerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Renombre fotos")
        self.geometry("400x350")
        
        # -- Folder path variable --
        self.folder_path = tk.StringVar()
        
        # -- Select Folder Button --
        self.select_folder_button = ttk.Button(
            self, 
            text="Seleccionar carpeta", 
            command=self.select_folder
        )
        self.select_folder_button.pack(pady=5)
        
        # -- Start Operation Button --
        self.start_button = ttk.Button(
            self, 
            text="Comenzar cambio de nombre", 
            command=self.start_renaming
        )
        self.start_button.pack(pady=5)
        
        # -- Progress Label --
        self.progress_label = tk.Label(self, text="Progreso:")
        self.progress_label.pack(pady=(20, 0))
        
        # -- Progress Bar --
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self, 
            orient="horizontal", 
            length=300, 
            mode="determinate", 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack()
        
    def select_folder(self):
        """Abre un popup que dice que selecciones la carpeta deseada."""
        selected_folder = filedialog.askdirectory()
        if selected_folder:
            self.folder_path.set(selected_folder)
            messagebox.showinfo("Carpeta seleccionada", f"Carpeta seleccionada:\n{selected_folder}")
        
    def start_renaming(self):
        """Empieza el proceso de cambo de nombre."""
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Ningún fichero seleccionado", "PSelecciona un fchero primero.")
            return
        
        base_name = simpledialog.askstring("Renombrar", "Inserta el nombre que quieras para los archivos:")
        if not base_name:
            messagebox.showwarning("No se ha puesto ningún nombre", "Inserta un nombre valido")
            return
        
        self.rename_photos(folder, base_name)
    
    def rename_photos(self, folder, base_name):
        """
        Renombra todos los formatos.jpg, .jpeg, .png de la carpeta
        """
        extensions = (".jpg", ".jpeg", ".png")
        all_files = os.listdir(folder)
        images = [f for f in all_files if f.lower().endswith(extensions)]
        
        total_images = len(images)
        if total_images == 0:
            messagebox.showinfo("No se encuentra ninguna imagen", "No hay ninguna imagen JPG/PNG en la carpeta seleccionada.")
            return
        
        for i, image_name in enumerate(images, start=1):
            old_path = os.path.join(folder, image_name)
            new_filename = f"{base_name}{i}{os.path.splitext(image_name)[1].lower()}"
            new_path = os.path.join(folder, new_filename)
            
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
            
            # Update progress bar
            progress_percent = (i / total_images) * 100
            self.progress_var.set(progress_percent)
            self.update_idletasks()
        
        messagebox.showinfo("Finalizado", "Ya se han renombrado todos los archvos.")

if __name__ == "__main__":
    app = PhotoRenamerApp()
    app.mainloop()
