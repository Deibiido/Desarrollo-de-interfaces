import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import zipfile
import os
import threading
import subprocess
import sys
import platform

# S quieres crear un acceso directo deberás de instalar winshell y pywin32
try:
    import winshell
    from win32com.client import Dispatch
    WINDOWS_SHORTCUT_AVAILABLE = True
except ImportError:
    WINDOWS_SHORTCUT_AVAILABLE = False

class Installer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Instalador")
        self.geometry("500x450")  # Increased height to accommodate additional UI elements
        self.resizable(False, False)
        
        # Guarda el fichero seleccionado por el ususario
        self.install_path = tk.StringVar(value=os.getcwd())  # Por defecto siempre estará en la carpeta en la que te encuentres
        
        # Prepare frames (screens)
        self.frames = {}
        
        for F in (WelcomeScreen, SelectFolderScreen, ProgressScreen, SuccessScreen):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show the Welcome screen first
        self.show_frame(WelcomeScreen)

    def show_frame(self, frame_class):
        """
        Bring the specified frame to the front.
        If the frame has an 'on_show' method, call it.
        """
        frame = self.frames[frame_class]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()

class WelcomeScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Title label
        title_label = tk.Label(self, text="Benvenido al instalador", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Description
        description_label = tk.Label(self, 
            text="Este instalador te guiará en el proceso \n"
                 "para instalar la aplicación en el sistema")
        description_label.pack(pady=10)
        
        # Next button
        next_button = ttk.Button(self, text="Next", command=self.go_next)
        next_button.pack(pady=20)
        
        self.parent = parent

    def go_next(self):
        self.parent.show_frame(SelectFolderScreen)

class SelectFolderScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Instruction label
        instruction_label = tk.Label(self, text="Selecciona la carpeta de instalación", font=("Arial", 12, "bold"))
        instruction_label.pack(pady=20)
        
        # Folder input frame
        folder_frame = tk.Frame(self)
        folder_frame.pack(pady=5)
        
        # Folder entry
        self.folder_entry = tk.Entry(folder_frame, textvariable=parent.install_path, width=40)
        self.folder_entry.pack(side="left", padx=(0, 10))
        
        # Browse button
        browse_button = ttk.Button(folder_frame, text="Explorar", command=self.browse_folder)
        browse_button.pack(side="left")
        
        # Error message label
        self.error_label = tk.Label(self, text="", fg="red", font=("Arial", 10))
        self.error_label.pack(pady=5)
        
        # Next button
        self.next_button = ttk.Button(self, text="Sguiente", command=self.go_next)
        self.next_button.pack(pady=20)
        self.next_button.config(state="disabled")  # Initially disabled
        
        self.parent = parent
        
        # Add trace to install_path
        self.parent.install_path.trace_add('write', self.on_path_change)
        
        # Initial check
        self.check_folder_empty()

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=os.getcwd(), title="Selecciona la carpeta de instalación")
        if folder:
            self.parent.install_path.set(folder)

    def on_path_change(self, *args):
        self.check_folder_empty()

    def check_folder_empty(self):
        path = self.parent.install_path.get()
        if os.path.isdir(path):
            try:
                if not os.listdir(path):  # Folder is empty
                    self.next_button.config(state="normal")
                    self.error_label.config(text="")
                else:
                    self.next_button.config(state="disabled")
                    self.error_label.config(text="La carpeta seleccionada no está vacia. Selecciona una carpeta vacia")
            except PermissionError:
                self.next_button.config(state="disabled")
                self.error_label.config(text="Permso denegado para acceder a la carpeta seleccionada.")
            except Exception as e:
                self.next_button.config(state="disabled")
                self.error_label.config(text=f"Error accediendo a la carpeta: {str(e)}")
        else:
            self.next_button.config(state="disabled")
            self.error_label.config(text="La ruta slecconada no es válida.")

    def go_next(self):
        self.parent.show_frame(ProgressScreen)

class ProgressScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Title
        title_label = tk.Label(self, text="Instalando", font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self, text="Preparando para instalar", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Next button (initially disabled)
        self.next_button = ttk.Button(self, text="Siguente", command=self.go_next)
        self.next_button.pack(pady=20)
        self.next_button.config(state="disabled")
        
        self.parent = parent
        self.installation_started = False  # Flag to prevent multiple starts

    def on_show(self):
        """
        Esta función es llamada cuando la pantalla de progreso se muestra
        Empieza la extracción si aún no se ha hecho
        """
        if not self.installation_started:
            self.installation_started = True
            threading.Thread(target=self.start_extraction, daemon=True).start()

    def start_extraction(self):
        archivo_original = "paquete.zip"
        salida = self.parent.install_path.get()
        
        # Determine the path of the zip file relative to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        zip_path = os.path.join(script_dir, archivo_original)
        
        if not os.path.isfile(zip_path):
            messagebox.showerror("Error", f"No se puede encontrar '{archivo_original}' en '{script_dir}'.")
            self.status_label.config(text="Instación fallida.")
            return

        try:
            with zipfile.ZipFile(zip_path, 'r') as zipped:
                # Get file list to compute progress
                file_list = zipped.namelist()
                total_files = len(file_list)
                
                for i, file in enumerate(file_list, start=1):
                    zipped.extract(file, salida)
                    
                    # Update progress
                    progress_value = int((i / total_files) * 100)
                    self.progress["value"] = progress_value
                    
                    # Update UI elements
                    self.status_label.config(text=f"Extrayendo {file} ({i}/{total_files})")
                    self.parent.update_idletasks()
            
            # Extraction successful
            self.status_label.config(text="Extracción completada.")
            self.next_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Un error ha surgdo en la extracción:\n{str(e)}")
            self.status_label.config(text="Instalación fallida.")

    def go_next(self):
        self.parent.show_frame(SuccessScreen)

class SuccessScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Title
        success_label = tk.Label(self, text="Instalación completada", font=("Arial", 14, "bold"))
        success_label.pack(pady=20)
        
        # Description
        detail_label = tk.Label(self, text="Tu instalacón se ha completado de forma satisfactoria", font=("Arial", 10))
        detail_label.pack(pady=10)
        
        # Checkbox variable
        self.launch_var = tk.BooleanVar(value=True)  # Default to checked
        self.shortcut_var = tk.BooleanVar(value=False)  # Default to checked
        self.open_folder_var = tk.BooleanVar(value=False)  # Default to unchecked
        
        # Checkbox
        self.launch_checkbox = tk.Checkbutton(self, text="Abrir la aplicación", variable=self.launch_var, font=("Arial", 10))
        self.launch_checkbox.pack(pady=5)
        
        self.shortcut_checkbox = tk.Checkbutton(self, text="Crear un acceso directo en el escritorio", variable=self.shortcut_var, font=("Arial", 10))
        self.shortcut_checkbox.pack(pady=5)
        
        # Checkbox para abrir la ruta de instalación
        self.open_folder_var = tk.BooleanVar(value=False)
        self.open_folder_checkbox = tk.Checkbutton(
            self,
            text="Abrir la carpeta de instalación",
            variable=self.open_folder_var,
            font=("Arial", 10)
        )
        self.open_folder_checkbox.pack(pady=5)
                
        # Exit button
        exit_button = ttk.Button(self, text="Finalizar", command=self.finish_installation)
        exit_button.pack(pady=20)
        
        self.parent = parent

    def finish_installation(self):
        # Crear acceso directo si la casilla está marcada
        if self.shortcut_var.get():
            threading.Thread(target=self.create_shortcut, daemon=True).start()
        
        # Iniciar la aplicación si la casilla está marcada
        if self.launch_var.get():
            self.launch_main_py()
        
        # Abrir la carpeta de instalación si la casilla está marcada
        if self.open_folder_var.get():
            self.open_installation_folder()

        # Cerrar el instalador
        self.parent.destroy()

    def create_shortcut(self):
        current_os = platform.system()
        target_path = os.path.join(self.parent.install_path.get(), "main.py")
        shortcut_name = "Aplicación"  # Podemos personalizar el nombre del acceso directo que se crea
        
        if not os.path.isfile(target_path):
            messagebox.showerror("Error", f"No se puede encontrar 'main.py' in '{self.parent.install_path.get()}'. No se puede crear el acceso directo.")
            return
        
        if current_os == "Windows":
            self.create_windows_shortcut(target_path, shortcut_name)
        elif current_os == "Darwin":
            self.create_macos_shortcut(target_path, shortcut_name)
        elif current_os == "Linux":
            self.create_linux_shortcut(target_path, shortcut_name)
        else:
            messagebox.showerror("Error", f"El sistema operativo actual no se soporta: {current_os}. No se puede crear el acceso directo.")
            
    def open_installation_folder(self):
        """
        Esto es para abrir la carpeta donde se realiza la instalación de la app
        """
    def create_windows_shortcut(self, target_path, shortcut_name):
        if not WINDOWS_SHORTCUT_AVAILABLE:
            messagebox.showerror("Error", "Los modulos winshell y pywin32 no estan instalados. No se puede crear el acceso directo.")
            return
        
        try:
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
            with winshell.shortcut(shortcut_path) as link:
                link.path = sys.executable
                link.arguments = f'"{target_path}"'
                link.description = "Ejecutar la aplicación"
                link.icon_location = (sys.executable, 0)
            messagebox.showinfo("Éxito", "Acceso directo creado")
        except Exception as e:
            messagebox.showerror("Error", f"Ha fallado la creación  del acceso directo:\n{str(e)}")

    def create_macos_shortcut(self, target_path, shortcut_name):
        try:
            # Path to the desktop
            desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
            alias_path = os.path.join(desktop, f"{shortcut_name}.app")
            
            # AppleScript to create alias
            applescript = f'''
            tell application "Finder"
                make alias file to POSIX file "{target_path}" at POSIX file "{desktop}"
                set name of result to "{shortcut_name}.app"
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript], check=True)
            messagebox.showinfo("Exito", "Desktop alias created successfully.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error al crear el alas en macOs:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Un error inesperado ha ocurrido:\n{str(e)}")

    def create_linux_shortcut(self, target_path, shortcut_name):
        try:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            shortcut_path = os.path.join(desktop, f"{shortcut_name}.desktop")
            
            # Content of the .desktop file
            desktop_entry = f"""[Desktop Entry]
Type=Application
Name={shortcut_name}
Exec={sys.executable} "{target_path}"
Icon=utilities-terminal
Terminal=false
"""
            with open(shortcut_path, 'w') as f:
                f.write(desktop_entry)
            
            # Make the .desktop file executable
            os.chmod(shortcut_path, 0o755)
            messagebox.showinfo("Success", "El acceso directo ha sido creado de forma satisfactoria")
        except Exception as e:
            messagebox.showerror("Error", f"Se ha fallado a la hora de crear un acceso directo en linux:\n{str(e)}")

    def launch_main_py(self):
        """
        nicia el main.py que se ha extraido.
        """
        main_py_path = os.path.join(self.parent.install_path.get(), "main.py")
        
        if not os.path.isfile(main_py_path):
            messagebox.showerror("Error", f"No se puede encontrar 'main.py' en '{self.parent.install_path.get()}'.")
            return
        
        try:
            # Launch main.py using the same Python interpreter
            subprocess.Popen([sys.executable, main_py_path], cwd=self.parent.install_path.get())
        except Exception as e:
            messagebox.showerror("Error", f"Se ha fallado a la hora de lanzar 'main.py':\n{str(e)}")
            return

if __name__ == "__main__":
    app = Installer()
    app.mainloop()
