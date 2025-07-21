import os
import csv

from GUI.interfaz import lanzar_interfaz
from Motor.detector import (
    cargar_patrones_csv,
    analizar_texto_con_comentarios,
    imprimir_resultados_con_comentarios
)

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
        escritor = csv.DictWriter(f, fieldnames=campos)
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

if __name__ == "__main__":
    
    lanzar_interfaz()
    
    #----- desmarcar para impresion y analisis en la consola -----
    
    #ruta_csv_patrones = "patrones.csv"
    #ruta_csv_tabla_pruebas = "Tabla_Pruebas.csv"

    #texto_entrada = input("🔎 Escribe el mensaje a analizar:\n> ").strip()
    #patrones = cargar_patrones_csv(ruta_csv_patrones)

    #resultados = analizar_texto_con_comentarios(texto_entrada, patrones)
    #imprimir_resultados_con_comentarios(resultados)

    #guardar_resultados_csv(ruta_csv_tabla_pruebas, texto_entrada, resultados)
