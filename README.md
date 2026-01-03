# Invoice Extraction API

API para extraer información de facturas en PDF utilizando FastAPI.

## Características

- Recibe una URL de un archivo PDF
- Clasifica automáticamente el tipo de factura
- Extrae información del cliente y consumo
- Extrae datos históricos según el tipo de factura
- Retorna resultados estructurados en formato JSON

## Instalación y Despliegue

### Opción 1: Docker (Recomendado)

1. Construir y ejecutar con Docker Compose:
```bash
docker compose up -d
```

2. Verificar que el contenedor esté corriendo:
```bash
docker compose ps
```

3. Ver logs:
```bash
docker compose logs -f
```

4. Detener el servicio:
```bash
docker compose down
```

### Opción 2: Docker Build Manual

```bash
# Construir la imagen
docker build -t extraction-invoice-api .

# Ejecutar el contenedor
docker run -d -p 8000:8000 --name extraction-api extraction-invoice-api

# Ver logs
docker logs -f extraction-api

# Detener el contenedor
docker stop extraction-api
docker rm extraction-api
```

### Opción 3: Instalación Local

1. Crear y activar entorno virtual:
```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Iniciar el servidor:
```bash
python api.py
```

O usando uvicorn directamente:
```bash
uvicorn api:app --reload
```

El servidor estará disponible en `http://localhost:8000`

### Endpoints

#### GET /
Información básica de la API

#### GET /health
Verificación del estado del servidor

#### POST /extract
Extrae información de una factura desde una URL

**Request Body:**
```json
{
  "pdf_url": "https://ejemplo.com/factura.pdf"
}
```

**Response:**
```json
{
  "pdf_url": "https://ejemplo.com/factura.pdf",
  "tipo_recibo": "TIPO_A_COSTO_KWH",
  "cliente": {
    "nombre": "Juan Pérez",
    "consumo_kwh": 150.5
  },
  "historico": {
    "datos": [...]
  }
}
```

### Ejemplo con curl

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://ejemplo.com/factura.pdf"}'
```

### Ejemplo con Python

```python
import requests

response = requests.post(
    "http://localhost:8000/extract",
    json={"pdf_url": "https://ejemplo.com/factura.pdf"}
)

print(response.json())
```

## Documentación Interactiva

Una vez iniciado el servidor, puedes acceder a:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Tipos de Facturas Soportadas

- **TIPO_A_COSTO_KWH**: Facturas que contienen "$/kWh"
- **TIPO_B_CONSUMO_KWH**: Facturas que contienen "kWh" y "Promedio"
- **TIPO_C_SIN_HISTORICO**: Facturas que contienen "Historico Consumos:"

## Estructura del Proyecto

```
extraction-invoice/
├── extraction/
│   ├── base.py                    # Clase base para extractores
│   ├── classifier.py              # Clasificador de facturas
│   ├── orchestrator.py            # Orquestador principal
│   ├── cliente_y_consumo.py       # Extractor de datos del cliente
│   ├── tipo_a_costo_kwh.py        # Extractor tipo A
│   ├── tipo_b_consumo_kwh.py      # Extractor tipo B
│   └── tipo_c_sin_historico.py    # Extractor tipo C
├── api.py                         # API FastAPI
├── Dockerfile                     # Configuración Docker
├── docker-compose.yml             # Orquestación Docker
├── .dockerignore                  # Archivos excluidos de Docker
├── requirements.txt               # Dependencias del proyecto
├── run_batch.py                   # Script para procesamiento por lotes
└── README.md                      # Documentación
```

## Desarrollo

Para ejecutar en modo desarrollo con recarga automática:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## Notas

- La API descarga temporalmente el PDF de la URL proporcionada
- Los archivos temporales se eliminan automáticamente después del procesamiento
- Timeout de descarga: 30 segundos
- Se valida que la URL apunte a un archivo PDF válido
