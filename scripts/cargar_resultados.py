import os
import psycopg2

archivo = "/data/output/resultado_hadoop/part-00000"

conexion = psycopg2.connect(
    host=os.getenv("DB_HOST", "db"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "datamart"),
    user=os.getenv("DB_USER", "admin"),
    password=os.getenv("DB_PASSWORD", "")
)

cursor = conexion.cursor()

insertados = 0

with open(archivo, "r", encoding="utf-8") as f:
    for linea in f:
        linea = linea.strip()

        if not linea:
            continue

        clave, unidades = linea.split("\t", 1)

        cursor.execute("""
            INSERT INTO resultados (clave, unidades_vendidas)
            VALUES (%s, %s)
            ON CONFLICT (clave)
            DO UPDATE SET unidades_vendidas = EXCLUDED.unidades_vendidas;
        """, (clave, int(unidades)))

        insertados += 1

conexion.commit()
cursor.close()
conexion.close()

print(f"Se cargaron {insertados} resultados en PostgreSQL.")