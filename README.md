# Proyecto: Pipeline de Big Data Contenerizado

## 1. Descripción del proyecto

Este proyecto implementa un pipeline de procesamiento de datos utilizando Docker, Hadoop MapReduce, Python, PostgreSQL y Flask.

El objetivo es procesar un conjunto de datos de ventas de 5 millones de registros para responder la siguiente pregunta:

**¿Cuántas unidades se vendieron por método de pago y día de la semana?**

El procesamiento se realiza mediante dos métodos: un programa secuencial en Python y un trabajo distribuido con Hadoop Streaming. Posteriormente, los resultados se almacenan en PostgreSQL y se consultan mediante una API REST.

## 2. Tecnologías utilizadas

- **Docker y Docker Compose:** creación y administración de los contenedores.
- **Debian:** sistema operativo utilizado en el contenedor de Hadoop.
- **Hadoop 3.4.1:** procesamiento de datos mediante MapReduce.
- **Python 3:** desarrollo de los programas Mapper, Reducer y procesamiento secuencial.
- **PostgreSQL 16:** almacenamiento de los resultados.
- **Flask:** desarrollo de la API REST.
- **SSH:** comunicación entre contenedores mediante autenticación por llave pública.

## 3. Arquitectura del proyecto

El proyecto está compuesto por tres servicios principales:

| Servicio | Función |
|---|---|
| hadoop | Procesa el dataset mediante Hadoop Streaming y permite conexiones SSH. |
| db | Almacena los resultados procesados en PostgreSQL. |
| api | Expone los resultados mediante endpoints REST. |

Los servicios se comunican mediante una red interna de Docker Compose.

Se utiliza un volumen llamado `postgres_data` para conservar la información de la base de datos aunque los contenedores se detengan o se eliminen.

## 4. Estructura del proyecto

```text
examen_2do_parcial/
│
├── api/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
│
├── data/
│   └── ventas_125053424.csv
│
├── evidencias/
│   └── ev.jpg
│
├── hadoop/
│   ├── Dockerfile
│   ├── core-site.xml
│   ├── mapred-site.xml
│   └── entrypoint.sh
│
├── mapreduce/
│   ├── mapper.py
│   ├── reducer.py
│   └── secuencial.py
│
├── scripts/
│   └── cargar_resultados.py
│
├── output/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── generar_dataset.py
└── README.md
```

El dataset se genera localmente y no se incluye en el repositorio debido a su tamaño.

## 5. Generación del dataset

Se utilizó el generador proporcionado por el profesor, conservando su código original.

La matrícula utilizada fue `125053424`.

Para generar el archivo se ejecuta:

```powershell
python generar_dataset.py 125053424
```

El archivo generado es:

```text
ventas_125053424.csv
```

Este archivo contiene aproximadamente 5 millones de registros y se coloca dentro de la carpeta `data`.

## 6. Procesamiento con Hadoop MapReduce

El procesamiento utiliza Hadoop Streaming para ejecutar programas escritos en Python.

### Mapper

El Mapper realiza las siguientes operaciones:

1. Lee los registros del archivo CSV.
2. Ignora el encabezado.
3. Valida los registros.
4. Obtiene el método de pago.
5. Obtiene el día de la semana a partir de la fecha.
6. Emite una clave formada por método de pago y día, junto con las unidades vendidas.

Ejemplo:

```text
Efectivo|Lunes    5
Tarjeta|Martes    3
```

### Reducer

El Reducer recibe las claves agrupadas y suma las unidades vendidas correspondientes a cada combinación.

El resultado final contiene 28 combinaciones: cuatro métodos de pago por siete días de la semana.

### Ejecución de Hadoop

Primero se inicia el entorno:

```powershell
docker compose up -d --build
```

Después se ejecuta el trabajo dentro del contenedor Hadoop:

```powershell
docker compose exec hadoop bash
```

Dentro del contenedor:

```bash
cd /app/mapreduce

rm -rf /data/output/resultado_hadoop

hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar \
-files mapper.py,reducer.py \
-input /data/input/ventas_125053424.csv \
-output /data/output/resultado_hadoop \
-mapper "python3 mapper.py" \
-reducer "python3 reducer.py"
```

Para consultar los resultados:

```bash
cat /data/output/resultado_hadoop/part-00000
```

## 7. Procesamiento secuencial

También se desarrolló un programa en Python que procesa el mismo dataset sin utilizar Hadoop.

Este programa agrupa las unidades vendidas utilizando el método de pago y el día de la semana.

Los resultados se guardan en:

```text
output/resultado_secuencial.txt
```

Se compararon los resultados del procesamiento secuencial con los obtenidos mediante Hadoop MapReduce.

Ambos archivos produjeron los mismos 28 resultados.

## 8. Base de datos PostgreSQL

Los resultados generados por Hadoop se insertan en PostgreSQL mediante el archivo:

```text
scripts/cargar_resultados.py
```

Para cargar los resultados:

```powershell
docker compose exec api python /scripts/cargar_resultados.py
```

La tabla utilizada se llama `resultados` y contiene:

| Campo | Descripción |
|---|---|
| id | Identificador del registro. |
| clave | Método de pago y día de la semana. |
| unidades_vendidas | Total de unidades vendidas. |

## 9. API REST con Flask

La API permite consultar y registrar resultados.

La dirección base es:

```text
http://localhost:5000
```

### Endpoints

| Método | Endpoint | Función |
|---|---|---|
| GET | `/health` | Verifica la conexión con PostgreSQL. |
| GET | `/resultados` | Consulta todos los resultados. |
| GET | `/resultados/<clave>` | Consulta un resultado específico. |
| POST | `/resultados` | Inserta o actualiza un resultado. |

Ejemplo de consulta:

```powershell
Invoke-RestMethod http://localhost:5000/resultados
```

Ejemplo de consulta individual:

```powershell
Invoke-RestMethod "http://localhost:5000/resultados/Efectivo%7CLunes"
```

## 10. Comunicación mediante SSH

Se configuró un servidor SSH en el contenedor Hadoop.

La autenticación se realiza mediante llaves SSH, sin necesidad de contraseña.

Se verificó la conexión local desde Hadoop y también la conexión desde el contenedor API hacia Hadoop utilizando el nombre del servicio:

```powershell
docker compose exec api ssh -i /shared-ssh/id_ed25519 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null hadoop@hadoop "whoami"
```

La conexión devolvió el usuario `hadoop`, confirmando que la comunicación funciona correctamente.

## 11. Persistencia de datos

Se configuró un volumen de Docker para PostgreSQL:

```yaml
volumes:
  postgres_data:
```

Se comprobó la persistencia ejecutando:

```powershell
docker compose down
docker compose up -d --build
```

Después del reinicio, la tabla `resultados` conservó sus 28 registros.

Es importante no utilizar `docker compose down -v`, ya que ese comando elimina también los volúmenes.

## 12. Ejecución general

Para iniciar los servicios del proyecto:

```powershell
docker compose up --build
```

Para revisar el estado de los contenedores:

```powershell
docker compose ps
```

Para detener los servicios:

```powershell
docker compose down
```

## 13. Resultados obtenidos

El trabajo de Hadoop procesó:

- 5,000,000 registros válidos.
- 5,000,000 registros emitidos por el Mapper.
- 28 grupos de resultados.
- 28 resultados finales generados por el Reducer.

También se verificó que los resultados del procesamiento secuencial y de Hadoop coinciden.

Finalmente, los 28 resultados se cargaron correctamente en PostgreSQL y se consultaron mediante la API REST.

## 14. Conclusión

Con este proyecto se implementó un pipeline de procesamiento de datos utilizando diferentes tecnologías dentro de contenedores Docker.

Se comprobó que Hadoop puede procesar millones de registros y agrupar información mediante MapReduce. También se comparó su resultado con un procesamiento secuencial en Python, obteniendo los mismos resultados.

La integración con PostgreSQL permitió almacenar la información y Flask facilitó su consulta mediante una API REST.

Además, se comprobó la comunicación SSH entre contenedores y la persistencia de los datos después de detener y volver a iniciar los servicios.