import os
import re
import threading
from tkinter import Tk, Toplevel, Text, StringVar, filedialog, END
from ttkbootstrap import ttk, Style
from ttkbootstrap.constants import *

def filtrar_directorios(dirs):
    """
    Filtra y elimina los directorios que comienzan con un punto.

    Args:
        dirs (list): Lista de nombres de directorios.
    """
    dirs[:] = [d for d in dirs if not d.startswith('.')]

def listar_estructura_markdown(ruta, archivo_salida):
    """
    Genera la estructura del directorio en formato Markdown con listas desordenadas,
    excluyendo directorios ocultos.
    """
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("# Estructura del Proyecto\n\n")
        for root, dirs, files in os.walk(ruta):
            filtrar_directorios(dirs)
            relative_path = os.path.relpath(root, ruta)
            level = 0 if relative_path == '.' else relative_path.count(os.sep) + 1
            indent = '    ' * level
            carpeta = os.path.basename(root)
            if carpeta:
                f.write(f"{indent}- **🗀  {carpeta}/**\n")
            for file in files:
                if not file.startswith('.'):
                    file_indent = '    ' * (level + 1)
                    f.write(f"{file_indent}- 🗋  {file}\n")

def extraer_docstring(file_path):
    """
    Extrae el docstring o comentarios iniciales de un archivo según su tipo,
    excluyendo archivos en directorios ocultos.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    doc = ""
    partes = file_path.split(os.sep)
    if any(part.startswith('.') for part in partes):
        return doc
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if ext == '.py':
            match = re.match(r'^\s*(?:\'\'\'|\"\"\")([\s\S]*?)(?:\'\'\'|\"\"\")', content, re.DOTALL)
            if match:
                doc = match.group(1).strip()
            else:
                comments = []
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("#"):
                        comments.append(line.lstrip("#").strip())
                    elif not line:
                        continue
                    else:
                        break
                if comments:
                    doc = "\n".join(comments)
        elif ext in ['.js', '.php', '.css']:
            if ext == '.php':
                content = re.sub(r'<\?php\s*', '', content, flags=re.IGNORECASE)
            multiline_match = re.match(r'^\s*/\*([\s\S]*?)\*/', content, re.DOTALL)
            if multiline_match:
                doc = multiline_match.group(1).strip()
            else:
                comments = []
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("//"):
                        comments.append(line.lstrip("//").strip())
                    elif not line:
                        continue
                    else:
                        break
                if comments:
                    doc = "\n".join(comments)
        elif ext == '.html':
            match = re.match(r'^\s*<!--([\s\S]*?)-->', content, re.DOTALL)
            if match:
                doc = match.group(1).strip()
    except Exception as e:
        print(f"Error al procesar el archivo {file_path}: {e}")
    return doc

def agregar_docstrings_markdown(ruta, archivo_salida):
    """
    Agrega docstrings/comentarios de los archivos al documento Markdown,
    excluyendo directorios ocultos.
    """
    with open(archivo_salida, 'a', encoding='utf-8') as f:
        f.write("\n# Documentación de Archivos\n\n")
        for root, dirs, files in os.walk(ruta):
            filtrar_directorios(dirs)
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                doc = extraer_docstring(file_path)
                if doc:
                    relative_path = os.path.relpath(file_path, ruta)
                    f.write(f"## {relative_path}\n\n")
                    f.write(f"{doc}\n\n")

def agregar_codigo_markdown(ruta, archivo_salida):
    """
    Agrega el código de cada archivo al documento Markdown dentro de bloques de código,
    excluyendo directorios ocultos.
    """
    with open(archivo_salida, 'a', encoding='utf-8') as f:
        f.write("\n# Código de Archivos\n\n")
        for root, dirs, files in os.walk(ruta):
            filtrar_directorios(dirs)
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                ext = ext.lower().lstrip('.')
                lang_map = {
                    'py': 'python',
                    'js': 'javascript',
                    'php': 'php',
                    'css': 'css',
                    'html': 'html',
                    'htm': 'html',
                }
                lang = lang_map.get(ext, '')
                try:
                    with open(file_path, 'r', encoding='utf-8') as code_file:
                        code_content = code_file.read()
                    relative_path = os.path.relpath(file_path, ruta)
                    f.write(f"## {relative_path}\n\n")
                    f.write(f"```{lang}\n")
                    f.write(f"{code_content}\n")
                    f.write("```\n\n")
                except Exception as e:
                    print(f"Error al leer el archivo {file_path}: {e}")

def procesar(carpeta, archivo_md, actualizar_label):
    """
    Ejecuta las tres fases del procesamiento y actualiza la etiqueta de estado.
    """
    try:
        listar_estructura_markdown(carpeta, archivo_md)
        actualizar_label("Estructura del proyecto generada.")
        agregar_docstrings_markdown(carpeta, archivo_md)
        actualizar_label("Docstrings/comentarios agregados.")
        agregar_codigo_markdown(carpeta, archivo_md)
        actualizar_label("Código de archivos agregado.")
        actualizar_label(f"Proceso completado. Archivo generado: {archivo_md}")
    except Exception as e:
        actualizar_label(f"Error: {e}")

def iniciar_proceso(carpeta, archivo_md, actualizar_label):
    """
    Inicia el procesamiento en un hilo separado.
    """
    hilo = threading.Thread(target=procesar, args=(carpeta, archivo_md, actualizar_label))
    hilo.start()
    return hilo

def main():
    root = Tk()
    root.title("Generador de Estructura Markdown")
    root.geometry("700x350")
    style = Style(theme='cosmo')

    ruta_carpeta = StringVar()
    ruta_archivo = StringVar()

    def seleccionar_carpeta():
        carpeta = filedialog.askdirectory()
        if carpeta:
            ruta_carpeta.set(carpeta)

    def seleccionar_archivo():
        archivo = filedialog.asksaveasfilename(defaultextension=".md",
                                               filetypes=[("Markdown files", "*.md")])
        if archivo:
            ruta_archivo.set(archivo)

    def actualizar_label(texto):
        estado_var.set(texto)
        root.update_idletasks()

    # Función que muestra la ventana para ingresar anotaciones
    def solicitar_anotaciones(archivo_md):
        anot_win = Toplevel(root)
        anot_win.title("Añadir Anotaciones")
        anot_win.geometry("500x300")

        lbl = ttk.Label(anot_win, text="Ingresa tus anotaciones:")
        lbl.pack(pady=10)

        text_box = Text(anot_win, wrap='word', height=10)
        text_box.pack(expand=True, fill='both', padx=10)

        def guardar_anotaciones():
            anotaciones = text_box.get("1.0", END).strip()
            if anotaciones:
                try:
                    with open(archivo_md, 'a', encoding='utf-8') as f:
                        f.write("\n# Anotaciones\n\n")
                        f.write(f"{anotaciones}\n")
                    actualizar_label("Anotaciones agregadas al archivo.")
                except Exception as e:
                    actualizar_label(f"Error al guardar anotaciones: {e}")
            anot_win.destroy()

        guardar_btn = ttk.Button(anot_win, text="Guardar", command=guardar_anotaciones)
        guardar_btn.pack(pady=10)

    # Función para verificar cuando el hilo termina y luego solicitar anotaciones
    def check_thread(hilo, archivo_md):
        if hilo.is_alive():
            root.after(100, check_thread, hilo, archivo_md)
        else:
            solicitar_anotaciones(archivo_md)

    def iniciar_proceso_ui():
        if not ruta_carpeta.get() or not ruta_archivo.get():
            actualizar_label("Por favor, selecciona la carpeta y el archivo de salida.")
            return
        hilo = iniciar_proceso(ruta_carpeta.get(), ruta_archivo.get(), actualizar_label)
        # Una vez iniciado el proceso, se comprueba periódicamente si ya terminó para solicitar las anotaciones
        root.after(100, check_thread, hilo, ruta_archivo.get())

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=BOTH, expand=True)

    carpeta_label = ttk.Label(frame, text="Carpeta de Origen:")
    carpeta_label.grid(row=0, column=0, sticky=W, pady=5)

    carpeta_entry = ttk.Entry(frame, textvariable=ruta_carpeta, width=50)
    carpeta_entry.grid(row=0, column=1, pady=5, padx=5)

    carpeta_button = ttk.Button(frame, text="Seleccionar Carpeta", command=seleccionar_carpeta)
    carpeta_button.grid(row=0, column=2, pady=5)

    archivo_label = ttk.Label(frame, text="Archivo de Salida (.md):")
    archivo_label.grid(row=1, column=0, sticky=W, pady=5)

    archivo_entry = ttk.Entry(frame, textvariable=ruta_archivo, width=50)
    archivo_entry.grid(row=1, column=1, pady=5, padx=5)

    archivo_button = ttk.Button(frame, text="Seleccionar Archivo", command=seleccionar_archivo)
    archivo_button.grid(row=1, column=2, pady=5)

    procesar_button = ttk.Button(frame, text="Iniciar Proceso", command=iniciar_proceso_ui)
    procesar_button.grid(row=2, column=1, pady=20)

    estado_var = StringVar()
    estado_var.set("Esperando para iniciar...")
    estado_label = ttk.Label(frame, textvariable=estado_var, bootstyle="info")
    estado_label.grid(row=3, column=0, columnspan=3, pady=10)

    frame.columnconfigure(1, weight=1)
    root.mainloop()

if __name__ == "__main__":
    main()
