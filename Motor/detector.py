import csv
from Motor.Algoritmos import kmp_search, boyer_moore

def cargar_patrones_csv(ruta_csv):
    patrones = []
    with open(ruta_csv, newline='', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        lector.fieldnames = [nombre.strip() for nombre in lector.fieldnames]
        for fila in lector:
            fila = {k.strip(): v for k, v in fila.items()}
            patrones.append({
                'patron': fila['Patron'].strip().lower(),
                'tipo': fila['Tipo'].strip(),
                'nivel': fila['Nivel'].strip()
            })
    return patrones

def distancia_levenshtein(s1, s2):
    if len(s1) < len(s2):
        return distancia_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]



def comentar_patron(texto, patron, indices_kmp, indices_bm):
    texto_lower = texto.lower()

    if not isinstance(indices_kmp, list):
        indices_kmp = [indices_kmp] if indices_kmp != -1 else []
    if not isinstance(indices_bm, list):
        indices_bm = [indices_bm] if indices_bm != -1 else []

    indices = indices_kmp + indices_bm
    if not indices:
        # No encontrado directamente: aplicar detección flexible
        len_patron = len(patron)
        ventana_min = max(3, len_patron - 2)
        ventana_max = len_patron + 6  # por sufijos largos

        for start in range(len(texto_lower) - ventana_min + 1):
            for ventana in range(ventana_min, ventana_max + 1):
                end = start + ventana
                if end > len(texto_lower):
                    continue
                fragmento = texto_lower[start:end]
                dist = distancia_levenshtein(patron, fragmento)

                # Regla 1: Levenshtein si patrón largo
                if len(patron) > 6 and dist == 1:
                    return "Variante gramatical no detectada (sinónimos)."

                # Regla 2: sufijos comunes ofensivos
                sufijos_validos = [
                    's', 'es', 'azo', 'aza', 'asas', 'asos', 'as', 'tas', 'itas', 'itos', 'otes',
                    'ísimo', 'ísima', 'isimo', 'isima', 'ísimos', 'ísimas', 'isimos', 'isimas',
                    'on', 'ona', 'ones', 'onas', 'uco', 'uca', 'otes', 'azas'
                ]
                if fragmento.startswith(patron):
                    resto = fragmento[len(patron):]
                    if resto in sufijos_validos:
                        return "Variante gramatical no detectada (sinónimos)."

                # Regla 3: contiene al menos 3 caracteres iniciales iguales y seguidos
                for k in range(len(patron), 2, -1):  # desde len hasta 3
                    if fragmento.startswith(patron[:k]):
                        return "Variante gramatical no detectada (sinónimos)."

        return "Patrón no está en el mensaje. Comprobación negativa."

    # Detección literal
    if 0 in indices:
        return "Detectado correctamente al inicio."

    # Contexto irónico
    for pos in indices:
        start = max(0, pos - 3)
        contexto = texto_lower[start:pos]
        if "no" in contexto or "sin" in contexto:
            return "Detección en contexto irónico."

    # No literal, pero parecido
    if patron not in texto_lower:
        return "Variante gramatical no detectada (sinónimos)."

    return "Patrón localizado en la posición correcta."



def analizar_texto_con_comentarios(texto, patrones):
    resultados = []
    texto_lower = texto.lower()

    for entrada in patrones:
        patron = entrada['patron']

        indice_kmp = kmp_search(texto_lower, patron)
        indice_bm = boyer_moore(texto_lower, patron)

        encontrado = bool(indice_kmp) or bool(indice_bm)

        if not encontrado:
            comentario = comentar_patron(texto, patron, [], [])
            if comentario == "Variante gramatical no detectada (sinónimos).":
                resultados.append({
                    'Patrón': patron,
                    'Categoría': entrada['tipo'],
                    'Nivel': entrada['nivel'],
                    'Índice KMP': [],
                    'Índice BM': [],
                    'Comentario': comentario,
                    'Algoritmo': 'Ninguno'
                })
        else:
            comentario = comentar_patron(texto, patron, indice_kmp, indice_bm)
            algoritmo_usado = 'Boyer-Moore' if len(patron) > 10 else 'KMP'
            resultados.append({
                'Patrón': patron,
                'Categoría': entrada['tipo'],
                'Nivel': entrada['nivel'],
                'Índice KMP': indice_kmp if algoritmo_usado == 'KMP' else [],
                'Índice BM': indice_bm if algoritmo_usado == 'Boyer-Moore' else [],
                'Comentario': comentario,
                'Algoritmo': algoritmo_usado
            })

    return resultados

def imprimir_resultados_con_comentarios(resultados):
    if not resultados:
        print("No se encontraron patrones detectados.")
        return

    print(f"{'Patrón':30} | {'Categoría':15} | {'Nivel':12} | {'Índice KMP':15} | {'Índice BM':15} | {'Algoritmo':12} | Comentario")
    print("-" * 120)
    for r in resultados:
        kmp_str = ", ".join(str(i) for i in r['Índice KMP']) if r['Índice KMP'] else ""
        bm_str = ", ".join(str(i) for i in r['Índice BM']) if r['Índice BM'] else ""
        print(f"{r['Patrón'][:30]:30} | {r['Categoría'][:15]:15} | {r['Nivel'][:12]:12} | "
              f"{kmp_str:15} | {bm_str:15} | {r['Algoritmo'][:12]:12} | {r['Comentario']}")
