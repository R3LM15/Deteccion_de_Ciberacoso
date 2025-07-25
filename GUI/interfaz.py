import tkinter as tk
from tkinter import messagebox, scrolledtext
import tkinter.ttk as ttk
import os
import csv

from Motor.detector import cargar_patrones_csv, analizar_texto_con_comentarios, imprimir_resultados_con_comentarios

# --- Lógica reutilizada del main.py ---
def obtener_ultimo_id_csv(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        return 0
    with open(nombre_archivo, newline='', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        filas = list(lector)
        if not filas:
            return 0
        ids = [int(fila['ID']) for fila in filas if fila['ID'].isdigit()]
        return max(ids) if ids else 0

def guardar_resultados_csv(nombre_archivo, mensaje, resultados):
    ultimo_id = obtener_ultimo_id_csv(nombre_archivo)
    escribir_header = not os.path.exists(nombre_archivo)

    with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as f:
        campos = ['ID', 'Mensaje de Entrada', 'Patrón Buscado', '¿Detectado?', 'Posición(es)', 'Algoritmo Usado', 'Comentario o Error']
        escritor = csv.DictWriter(f, fieldnames=campos, quoting=csv.QUOTE_MINIMAL)
        if escribir_header:
            escritor.writeheader()

        for r in resultados:
            patron = r['Patrón']
            algoritmo_usado = r['Algoritmo']

            posiciones = []
            if r.get('Índice KMP'):
                posiciones.extend(str(i) for i in r['Índice KMP'])
            if r.get('Índice BM'):
                posiciones.extend(str(i) for i in r['Índice BM'])
            posiciones_str = ', '.join(posiciones)

            fila = {
                'ID': ultimo_id + 1,
                'Mensaje de Entrada': mensaje,
                'Patrón Buscado': patron,
                '¿Detectado?': 'Sí' if posiciones else 'No',
                'Posición(es)': posiciones_str,
                'Algoritmo Usado': algoritmo_usado,
                'Comentario o Error': r.get('Comentario', '')
            }
            escritor.writerow(fila)
            ultimo_id += 1

# --- Ventana para editar/agregar patrones ---
def abrir_editor_patrones(ruta_csv, actualizar_callback=None):
    editor = tk.Toplevel()
    editor.title("🛠️ Editor de Patrones")
    editor.geometry("640x620")
    editor.configure(bg="#1a1a2e")  # Fondo oscuro intenso

    columnas = ("Patron", "Tipo", "Nivel")
    tree = ttk.Treeview(editor, columns=columnas, show="headings", height=15)
    tree.heading("Patron", text="📝 Patrón")
    tree.heading("Tipo", text="🏷️ Tipo")
    tree.heading("Nivel", text="⚠️ Nivel")
    tree.column("Patron", width=250, anchor="center")
    tree.column("Tipo", width=180, anchor="center")
    tree.column("Nivel", width=120, anchor="center")
    tree.pack(padx=15, pady=15, fill="both", expand=True)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#16213e", foreground="white")
    style.configure("Treeview", font=("Consolas", 10), background="#0f3460", fieldbackground="#0f3460", foreground="white", rowheight=25)
    style.map('Treeview', background=[('selected', '#e94560')], foreground=[('selected', 'white')])

    def cargar_patrones_en_tabla():
        for row in tree.get_children():
            tree.delete(row)
        if os.path.exists(ruta_csv):
            with open(ruta_csv, newline='', encoding='utf-8') as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    tree.insert("", tk.END, values=(fila['Patron'], fila['Tipo'], fila['Nivel']))

    cargar_patrones_en_tabla()

    frame_nuevo = tk.LabelFrame(editor, text="Agregar nuevo patrón", font=("Segoe UI", 10, "bold"), bg="#16213e", fg="white")
    frame_nuevo.pack(padx=10, pady=5, fill="x")

    tk.Label(frame_nuevo, text="Patrón:", bg="#16213e", fg="white").grid(row=0, column=0, padx=5, pady=2, sticky="e")
    entrada_patron = tk.Entry(frame_nuevo, width=30, bg="#0f3460", fg="white", insertbackground="white")
    entrada_patron.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(frame_nuevo, text="Tipo:", bg="#16213e", fg="white").grid(row=1, column=0, padx=5, pady=2, sticky="e")
    combo_tipo = ttk.Combobox(frame_nuevo, values=["Insulto", "Exclusion", "Amenaza"], state="readonly", width=28)
    combo_tipo.grid(row=1, column=1, padx=5, pady=2)
    combo_tipo.current(0)

    tk.Label(frame_nuevo, text="Nivel:", bg="#16213e", fg="white").grid(row=2, column=0, padx=5, pady=2, sticky="e")
    combo_nivel = ttk.Combobox(frame_nuevo, values=["media", "alta", "muy alta"], state="readonly", width=28)
    combo_nivel.grid(row=2, column=1, padx=5, pady=2)
    combo_nivel.current(0)

    boton_agregar = tk.Button(frame_nuevo, text="➕ Agregar Patrón", width=18, bg="#00b894", fg="white", activebackground="#019875", activeforeground="white",
                              command=lambda: agregar_patron())
    boton_agregar.grid(row=0, column=2, rowspan=3, padx=10, pady=2)

    def agregar_patron():
        patron = entrada_patron.get().strip()
        tipo = combo_tipo.get()
        nivel = combo_nivel.get()

        if not patron:
            messagebox.showwarning("Campos vacíos", "Por favor, ingresa un patrón.")
            return

        if os.path.exists(ruta_csv):
            with open(ruta_csv, newline='', encoding='utf-8') as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    if fila['Patron'].lower() == patron.lower():
                        messagebox.showwarning("Patrón existente", "Este patrón ya está registrado.")
                        return

        escribir_header = not os.path.exists(ruta_csv) or os.stat(ruta_csv).st_size == 0
        with open(ruta_csv, mode='a', newline='', encoding='utf-8') as f:
            campos = ['Patron', 'Tipo', 'Nivel']
            escritor = csv.DictWriter(f, fieldnames=campos)
            if escribir_header:
                escritor.writeheader()
            escritor.writerow({'Patron': patron, 'Tipo': tipo, 'Nivel': nivel})

        entrada_patron.delete(0, tk.END)
        combo_tipo.current(0)
        combo_nivel.current(0)

        cargar_patrones_en_tabla()
        messagebox.showinfo("Éxito", "Patrón agregado correctamente.")
        if actualizar_callback:
            actualizar_callback()

    frame_eliminar = tk.LabelFrame(editor, text="Eliminar patrón", font=("Segoe UI", 10, "bold"), bg="#16213e", fg="white")
    frame_eliminar.pack(padx=10, pady=5, fill="x")

    tk.Label(frame_eliminar, text="Patrón a eliminar:", bg="#16213e", fg="white").grid(row=0, column=0, padx=5, pady=5)
    entrada_eliminar = tk.Entry(frame_eliminar, width=30, bg="#0f3460", fg="white", insertbackground="white")
    entrada_eliminar.grid(row=0, column=1, padx=5, pady=5)

    boton_eliminar = tk.Button(frame_eliminar, text="❌ Eliminar Patrón", width=18, bg="#d63031", fg="white", activebackground="#b83227", activeforeground="white",
                               command=lambda: eliminar_patron())
    boton_eliminar.grid(row=0, column=2, padx=10, pady=5)

    def eliminar_patron():
        patron_eliminar = entrada_eliminar.get().strip()
        if not patron_eliminar:
            messagebox.showwarning("Campo vacío", "Ingresa el patrón a eliminar.")
            return

        if not os.path.exists(ruta_csv):
            messagebox.showwarning("No encontrado", "El archivo no existe.")
            return

        with open(ruta_csv, newline='', encoding='utf-8') as archivo:
            lector = list(csv.DictReader(archivo))

        nuevos_patrones = [f for f in lector if f['Patron'].lower() != patron_eliminar.lower()]

        if len(nuevos_patrones) == len(lector):
            messagebox.showinfo("No encontrado", "No se encontró el patrón especificado.")
            return

        with open(ruta_csv, mode='w', newline='', encoding='utf-8') as f:
            campos = ['Patron', 'Tipo', 'Nivel']
            escritor = csv.DictWriter(f, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(nuevos_patrones)

        entrada_eliminar.delete(0, tk.END)
        cargar_patrones_en_tabla()
        messagebox.showinfo("Éxito", "Patrón eliminado.")
        if actualizar_callback:
            actualizar_callback()

# ------------------- GUI PRINCIPAL -------------------
def lanzar_interfaz():
    ruta_csv_patrones = "patrones.csv"
    ruta_csv_resultados = "Tabla_Pruebas.csv"
    patrones = cargar_patrones_csv(ruta_csv_patrones)

    def actualizar_patrones():
        nonlocal patrones
        patrones = cargar_patrones_csv(ruta_csv_patrones)

    def analizar():
        texto = entrada.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Texto vacío", "Por favor, escribe un mensaje a analizar.")
            return

        resultados = analizar_texto_con_comentarios(texto, patrones)
        salida.config(state='normal')
        salida.delete("1.0", tk.END)

        entrada.tag_remove("resaltado_exacto", "1.0", tk.END)
        entrada.tag_remove("resaltado_parcial", "1.0", tk.END)

        if not resultados:
            salida.insert(tk.END, "✅ No se encontraron coincidencias.\n")
        else:
            for r in resultados:
                patron = r['Patrón']
                comentario = r['Comentario']
                tipo = r.get('Categoría', 'N/A')
                nivel = r.get('Nivel', 'N/A')
                salida.insert(tk.END, f"❗ Patrón: {patron}\nTipo: {tipo}\nNivel: {nivel}\nComentario: {comentario}\n\n")

                texto_lower = texto.lower()
                patron_lower = patron.lower()

                indices = []
                if r.get('Índice KMP'):
                    indices.extend(r['Índice KMP'])
                if r.get('Índice BM'):
                    indices.extend(r['Índice BM'])

                for inicio in indices:
                    fin = inicio + len(patron_lower)
                    start_index = f"1.0 + {inicio} chars"
                    end_index = f"1.0 + {fin} chars"
                    entrada.tag_add("resaltado_exacto", start_index, end_index)

                if len(patron_lower) > 2:
                    fragmento = patron_lower[:2]
                    start_pos = 0
                    while True:
                        pos = texto_lower.find(fragmento, start_pos)
                        if pos == -1:
                            break
                        if not any(pos >= i and pos < i + len(patron_lower) for i in indices):
                            start_index = f"1.0 + {pos} chars"
                            end_index = f"1.0 + {pos + len(fragmento)} chars"
                            entrada.tag_add("resaltado_parcial", start_index, end_index)
                        start_pos = pos + 1

        salida.config(state='disabled')
        entrada.tag_config("resaltado_exacto", background="#ff6f61")  # rojo coral vibrante
        entrada.tag_config("resaltado_parcial", background="#ffd166")  # amarillo fuerte

        guardar_resultados_csv(ruta_csv_resultados, texto, resultados)

    ventana = tk.Tk()
    ventana.title("Detector de Bullying [EDA II]")
    ventana.geometry("800x650")
    ventana.configure(bg="#16213e")  # fondo oscuro azul intenso

    tk.Label(ventana, text="📝 Ingrese el texto a analizar:", bg="#16213e", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=5)
    entrada = scrolledtext.ScrolledText(ventana, height=10, wrap=tk.WORD, font=("Consolas", 12), bg="#0f3460", fg="white", insertbackground="white")
    entrada.pack(fill=tk.BOTH, padx=10, pady=5)

    btn_analizar = tk.Button(ventana, text="🔍 Analizar texto", command=analizar, bg="#00cec9", fg="black", activebackground="#00b8b6", activeforeground="black", font=("Segoe UI", 10, "bold"))
    btn_analizar.pack(pady=10)

    tk.Label(ventana, text="📋 Resultados:", bg="#16213e", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=5)
    salida = scrolledtext.ScrolledText(ventana, height=10, wrap=tk.WORD, state='disabled', font=("Consolas", 12), bg="#0f3460", fg="white")
    salida.pack(fill=tk.BOTH, padx=10, pady=5)

    frame_botones = tk.Frame(ventana, bg="#16213e")
    frame_botones.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)

    btn_editar_patrones = tk.Button(frame_botones, text="🛠️ Editar patrones", bg="#0984e3", fg="white", activebackground="#0652DD", activeforeground="white", font=("Segoe UI", 10, "bold"),
                                    command=lambda: abrir_editor_patrones(ruta_csv_patrones, actualizar_patrones))
    btn_editar_patrones.pack(side=tk.LEFT)

    def limpiar_campos():
        entrada.delete("1.0", tk.END)
        salida.config(state='normal')
        salida.delete("1.0", tk.END)
        salida.config(state='disabled')

    btn_limpiar = tk.Button(frame_botones, text="🧹 Limpiar", command=limpiar_campos, bg="#6c5ce7", fg="white", activebackground="#4834d4", activeforeground="white", font=("Segoe UI", 10, "bold"))
    btn_limpiar.pack(side=tk.LEFT, padx=10)

    ventana.mainloop()
