import os
import time
import psycopg2

from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "datamart"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "")
}


def conectar_db():
    return psycopg2.connect(**DB_CONFIG)


def inicializar_db():
    for intento in range(10):
        try:
            conexion = conectar_db()
            cursor = conexion.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resultados (
                    id SERIAL PRIMARY KEY,
                    clave VARCHAR(150) UNIQUE NOT NULL,
                    unidades_vendidas BIGINT NOT NULL
                );
            """)

            conexion.commit()
            cursor.close()
            conexion.close()

            print("Base de datos conectada y tabla lista.")
            return

        except psycopg2.OperationalError as error:
            print(f"Esperando PostgreSQL... intento {intento + 1}/10")
            time.sleep(3)

    raise RuntimeError("No fue posible conectar con PostgreSQL.")


@app.route("/health", methods=["GET"])
def health():
    try:
        conexion = conectar_db()
        conexion.close()
        return jsonify({"estado": "conectado", "base_datos": "datamart"})
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/resultados", methods=["GET"])
def obtener_resultados():
    conexion = conectar_db()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT clave, unidades_vendidas
        FROM resultados
        ORDER BY clave;
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(resultados)


@app.route("/resultados/<path:clave>", methods=["GET"])
def obtener_resultado(clave):
    conexion = conectar_db()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT clave, unidades_vendidas
        FROM resultados
        WHERE clave = %s;
    """, (clave,))

    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    if resultado is None:
        return jsonify({"mensaje": "Resultado no encontrado"}), 404

    return jsonify(resultado)


@app.route("/resultados", methods=["POST"])
def agregar_resultado():
    datos = request.get_json(silent=True) or {}

    clave = datos.get("clave")
    unidades = datos.get("unidades_vendidas")

    if not clave or not isinstance(unidades, int) or isinstance(unidades, bool) or unidades < 0:
        return jsonify({
            "error": "Envía una clave y unidades_vendidas como entero no negativo."
        }), 400

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO resultados (clave, unidades_vendidas)
        VALUES (%s, %s)
        ON CONFLICT (clave)
        DO UPDATE SET unidades_vendidas = EXCLUDED.unidades_vendidas;
    """, (clave, unidades))

    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Resultado guardado correctamente",
        "clave": clave,
        "unidades_vendidas": unidades
    }), 201


if __name__ == "__main__":
    inicializar_db()
    app.run(host="0.0.0.0", port=5000)