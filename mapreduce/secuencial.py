
#!/usr/bin/env python3

import csv
import sys
import os
from datetime import datetime
from collections import defaultdict

dias = [
    "Lunes",
    "Martes",
    "Miercoles",
    "Jueves",
    "Viernes",
    "Sabado",
    "Domingo"
]

archivo = "/data/input/ventas_125053424.csv"

# Permitir indicar otro archivo como argumento
if len(sys.argv) > 1:
    archivo = sys.argv[1]

resultados = defaultdict(int)
registros_validos = 0
registros_invalidos = 0

print("Iniciando procesamiento secuencial...")

with open(archivo, "r", encoding="utf-8-sig", newline="") as f:

    lector = csv.reader(f)

    # Ignorar encabezado
    next(lector, None)

    for fila in lector:

        try:
            if len(fila) != 8:
                registros_invalidos += 1
                continue

            fecha = datetime.strptime(
                fila[1].strip(),
                "%Y-%m-%d %H:%M:%S"
            )

            cantidad = int(fila[5].strip())
            metodo_pago = fila[7].strip()

            if cantidad <= 0:
                registros_invalidos += 1
                continue

            if metodo_pago not in [
                "Efectivo",
                "Tarjeta",
                "Transferencia",
                "Vales"
            ]:
                registros_invalidos += 1
                continue

            dia = dias[fecha.weekday()]

            clave = f"{metodo_pago}|{dia}"

            resultados[clave] += cantidad
            registros_validos += 1

        except (ValueError, IndexError, csv.Error):
            registros_invalidos += 1
            continue

# Crear carpeta de resultados
os.makedirs("output", exist_ok=True)

# Guardar resultados ordenados
with open(
    "output/resultado_secuencial.txt",
    "w",
    encoding="utf-8"
) as salida:

    for clave in sorted(resultados):
        salida.write(f"{clave}\t{resultados[clave]}\n")

print("\nProcesamiento terminado.")
print(f"Registros validos: {registros_validos}")
print(f"Registros invalidos: {registros_invalidos}")
print(f"Combinaciones encontradas: {len(resultados)}")

print("\nResultados:")

for clave in sorted(resultados):
    print(f"{clave}\t{resultados[clave]}")

print("\nArchivo guardado en output/resultado_secuencial.txt")
