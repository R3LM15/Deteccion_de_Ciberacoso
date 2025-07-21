def boyer_moore(T, P):
    n, m = len(T), len(P)
    if m == 0:
        return []

    # Tabla de la última aparición
    last = {char: idx for idx, char in enumerate(P)}

    i = m - 1  # índice del texto
    k = m - 1  # índice del patrón
    resultados = []

    while i < n:
        if T[i] == P[k]:
            if k == 0:
                resultados.append(i)  # patrón encontrado desde i hasta i + m
                i += m  # saltamos al siguiente segmento
                k = m - 1
            else:
                i -= 1
                k -= 1
        else:
            j = last.get(T[i], -1)
            salto = m - min(k, j + 1)
            i += salto
            k = m - 1

    return resultados





def kmp_search(text, pattern):
    # Crear el arreglo LPS (longest prefix suffix)
    lps = [0] * len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j

    # Buscar patrón
    matches = []
    j = 0
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = lps[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == len(pattern):
            matches.append(i - j + 1)
            j = lps[j - 1]
    return matches

