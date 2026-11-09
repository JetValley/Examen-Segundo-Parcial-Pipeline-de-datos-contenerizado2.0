
#!/usr/bin/env python3

import sys

clave_actual = None
total = 0

for linea in sys.stdin:

    try:
        linea = linea.strip()

        if not linea:
            continue

        clave, valor = linea.split("\t", 1)

        valor = int(valor)

        if clave == clave_actual:
            total += valor

        else:
            # Imprimir el resultado anterior
            if clave_actual is not None:
                print(f"{clave_actual}\t{total}")

            # Iniciar nueva clave
            clave_actual = clave
            total = valor

    except (ValueError, IndexError):
        continue

# Imprimir la ultima agrupacion
if clave_actual is not None:
    print(f"{clave_actual}\t{total}")
