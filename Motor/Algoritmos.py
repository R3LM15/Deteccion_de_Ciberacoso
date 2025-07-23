def kmp_search(text, pattern):
    if not pattern:
        return []

    lps = [0] * len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j

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


def boyer_moore(texto, patron):
    n, m = len(texto), len(patron)
    if m == 0 or m > n:
        return []

    # Tabla de última aparición de cada carácter en el patrón
    last = {char: idx for idx, char in enumerate(patron)}

    resultados = []
    i = 0  # índice del texto

    while i <= n - m:
        j = m - 1  # índice del patrón
        while j >= 0 and patron[j] == texto[i + j]:
            j -= 1
        if j < 0:
            resultados.append(i)
            i += m  # salto completo si hubo coincidencia
        else:
            letra_actual = texto[i + j]
            salto = j - last.get(letra_actual, -1)
            i += max(1, salto)  # aseguramos al menos 1

    return resultados
