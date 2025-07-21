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
    editor.geometry("600x520")

    # Área para mostrar patrones actuales
    area_patrones = scrolledtext.ScrolledText(editor, height=15, wrap=tk.WORD)
    area_patrones.pack(fill=tk.BOTH, padx=10, pady=5)

    def cargar_patrones_en_area():
        area_patrones.config(state='normal')
        area_patrones.delete("1.0", tk.END)
        if os.path.exists(ruta_csv):
            with open(ruta_csv, newline='', encoding='utf-8') as archivo:
                lector = csv.DictReader(archivo)
                area_patrones.insert(tk.END, f"Patrón | Tipo | Nivel\n")
                area_patrones.insert(tk.END, "-"*50 + "\n")
                for fila in lector:
                    area_patrones.insert(tk.END, f"{fila['Patron']} | {fila['Tipo']} | {fila['Nivel']}\n")
        area_patrones.config(state='disabled')

    cargar_patrones_en_area()

    frame_nuevo = tk.Frame(editor)
    frame_nuevo.pack(pady=10)

    tk.Label(frame_nuevo, text="Patrón:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
    entrada_patron = tk.Entry(frame_nuevo, width=30)
    entrada_patron.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(frame_nuevo, text="Tipo:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
    combo_tipo = ttk.Combobox(frame_nuevo, values=["Insulto", "Exclusion", "Amenaza"], state="readonly", width=28)
    combo_tipo.grid(row=1, column=1, padx=5, pady=2)
    combo_tipo.current(0)

    tk.Label(frame_nuevo, text="Nivel:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
    combo_nivel = ttk.Combobox(frame_nuevo, values=["media", "alta", "muy alta"], state="readonly", width=28)
    combo_nivel.grid(row=2, column=1, padx=5, pady=2)
    combo_nivel.current(0)

    def agregar_patron():
        patron = entrada_patron.get().strip()
        tipo = combo_tipo.get()
        nivel = combo_nivel.get()

        if not patron or not tipo or not nivel:
            messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
            return  # Quitamos el destroy para que el usuario corrija sin cerrar

        # Verificar si ya existe el patrón (ignorando mayúsculas)
        existe = False
        if os.path.exists(ruta_csv):
            with open(ruta_csv, newline='', encoding='utf-8') as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    if fila['Patron'].lower() == patron.lower():
                        existe = True
                        break

        if existe:
            messagebox.showwarning("Patrón existente", "El patrón ya existe en la lista.")
            return  # Igual que arriba, sin cerrar ventana

        escribir_header = not os.path.exists(ruta_csv) or os.stat(ruta_csv).st_size == 0

        with open(ruta_csv, mode='a', newline='', encoding='utf-8') as f:
            campos = ['Patron', 'Tipo', 'Nivel']
            escritor = csv.DictWriter(f, fieldnames=campos)
            if escribir_header:
                escritor.writeheader()
            escritor.writerow({'Patron': patron, 'Tipo': tipo, 'Nivel': nivel})

        cargar_patrones_en_area()
        entrada_patron.delete(0, tk.END)
        combo_tipo.current(0)
        combo_nivel.current(0)

        messagebox.showinfo("Patrón agregado", f"Se agregó el patrón:\n{patron}")

        if actualizar_callback:
            actualizar_callback()

        editor.destroy()

    # --- Área y botón para eliminar patrón ---
    tk.Label(editor, text="Patrón a eliminar:").pack(pady=(10,0))
    entrada_eliminar = tk.Entry(editor, width=30)
    entrada_eliminar.pack(pady=5)

    def eliminar_patron():
        patron_eliminar = entrada_eliminar.get().strip()
        if not patron_eliminar:
            messagebox.showwarning("Campo vacío", "Por favor, ingresa el patrón a eliminar.")
            return

        if not os.path.exists(ruta_csv):
            messagebox.showwarning("Archivo no encontrado", "No existe el archivo de patrones.")
            return

        with open(ruta_csv, newline='', encoding='utf-8') as archivo:
            lector = list(csv.DictReader(archivo))

        existe = any(fila['Patron'].lower() == patron_eliminar.lower() for fila in lector)
        if not existe:
            messagebox.showwarning("No encontrado", "No existe coincidencias encontradas.")
            return

        nuevos_patrones = [fila for fila in lector if fila['Patron'].lower() != patron_eliminar.lower()]

        with open(ruta_csv, mode='w', newline='', encoding='utf-8') as f:
            campos = ['Patron', 'Tipo', 'Nivel']
            escritor = csv.DictWriter(f, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(nuevos_patrones)

        cargar_patrones_en_area()
        entrada_eliminar.delete(0, tk.END)
        messagebox.showinfo("Patrón eliminado", f"Se eliminó el patrón:\n{patron_eliminar}")

        if actualizar_callback:
            actualizar_callback()

    tk.Button(editor, text="➕ Agregar Patrón", command=agregar_patron).pack(pady=5)
    tk.Button(editor, text="❌ Eliminar Patrón", command=eliminar_patron).pack(pady=5)

# --- GUI principal ---
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

        # Limpiar tags previos de resaltado
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

                # Resaltar coincidencias exactas (posiciones reportadas por KMP o BM)
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

                # Resaltar coincidencias parciales: buscamos subcadenas de tamaño 2 dentro del texto que no están resaltadas exactas
                if len(patron_lower) > 2:
                    fragmento = patron_lower[:2]
                    start_pos = 0
                    while True:
                        pos = texto_lower.find(fragmento, start_pos)
                        if pos == -1:
                            break
                        # Evitar superposición con exactas ya resaltadas
                        if not any(pos >= i and pos < i + len(patron_lower) for i in indices):
                            start_index = f"1.0 + {pos} chars"
                            end_index = f"1.0 + {pos + len(fragmento)} chars"
                            entrada.tag_add("resaltado_parcial", start_index, end_index)
                        start_pos = pos + 1

        salida.config(state='disabled')

        # Configurar colores para los tags
        entrada.tag_config("resaltado_exacto", background="orange")
        entrada.tag_config("resaltado_parcial", background="yellow")

        guardar_resultados_csv(ruta_csv_resultados, texto, resultados)

    ventana = tk.Tk()
    ventana.title("Detector de Bullying [EDA II]")
    ventana.geometry("800x500")

    tk.Label(ventana, text="📝 Ingrese el texto a analizar:").pack(pady=5)
    entrada = scrolledtext.ScrolledText(ventana, height=10, wrap=tk.WORD)
    entrada.pack(fill=tk.BOTH, padx=10, pady=5)

    btn_analizar = tk.Button(ventana, text="🔍 Analizar texto", command=analizar)
    btn_analizar.pack(pady=10)

    tk.Label(ventana, text="📋 Resultados:").pack(pady=5)
    salida = scrolledtext.ScrolledText(ventana, height=10, wrap=tk.WORD, state='disabled')
    salida.pack(fill=tk.BOTH, padx=10, pady=5)

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5, anchor='sw')

    btn_editar_patrones = tk.Button(frame_botones, text="🛠️ Editar patrones", command=lambda: abrir_editor_patrones(ruta_csv_patrones, actualizar_patrones))
    btn_editar_patrones.pack(side=tk.LEFT)

    # Botón limpiar para borrar entradas y salidas
    def limpiar_campos():
        entrada.delete("1.0", tk.END)
        salida.config(state='normal')
        salida.delete("1.0", tk.END)
        salida.config(state='disabled')

    btn_limpiar = tk.Button(frame_botones, text="🧹 Limpiar", command=limpiar_campos)
    btn_limpiar.pack(side=tk.LEFT, padx=10)

    ventana.mainloop()
