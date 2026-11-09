
#!/usr/bin/env python3

import sys
import csv
from datetime import datetime

# Traduccion de los dias de la semana
dias = [
    "Lunes",
    "Martes",
    "Miercoles",
    "Jueves",
    "Viernes",
    "Sabado",
    "Domingo"
]

for linea in sys.stdin:
    try:
        # Leer la linea como CSV
        fila = next(csv.reader([linea]))

        # Ignorar encabezado
        if not fila or fila[0].strip().lstrip("\ufeff").lower() == "id":
            continue

        # Verificar que tenga todas las columnas
        if len(fila) != 8:
            continue

        fecha = datetime.strptime(
            fila[1].strip(),
            "%Y-%m-%d %H:%M:%S"
        )

        cantidad = int(fila[5].strip())
        metodo_pago = fila[7].strip()

        # Validar cantidad y metodo de pago
        if cantidad <= 0:
            continue

        if metodo_pago not in [
            "Efectivo",
            "Tarjeta",
            "Transferencia",
            "Vales"
        ]:
            continue

        # Obtener el dia de la semana
        dia = dias[fecha.weekday()]

        # Crear clave y emitir cantidad
        clave = f"{metodo_pago}|{dia}"

        print(f"{clave}\t{cantidad}")

    except (ValueError, IndexError, csv.Error):
        # Ignorar registros incorrectos
        continue
