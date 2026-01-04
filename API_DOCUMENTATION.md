# API Documentation - Invoice Extraction

Documentación completa del endpoint de extracción de facturas.

## Información General

- **Base URL**: `http://localhost:8002`
- **Formato**: JSON
- **Método HTTP**: POST
- **Content-Type**: `application/json`

## Endpoints

### 1. Health Check

Verifica el estado del servicio.

**Endpoint**: `GET /health`

**Respuesta**:
```json
{
  "status": "healthy"
}
```

**Código de estado**: `200 OK`

---

### 2. Información de la API

Obtiene información básica sobre la API.

**Endpoint**: `GET /`

**Respuesta**:
```json
{
  "message": "Invoice Extraction API",
  "version": "1.0.0",
  "endpoints": {
    "POST /extract": "Extrae información de un PDF desde una URL"
  }
}
```

**Código de estado**: `200 OK`

---

### 3. Extraer Información de Factura

Extrae información estructurada de una factura en formato PDF desde una URL.

**Endpoint**: `POST /extract`

#### Request

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "pdf_url": "https://ejemplo.com/factura.pdf"
}
```

**Parámetros**:

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| pdf_url | string (URL) | Sí | URL pública del archivo PDF a procesar |

#### Response - Éxito

**Código de estado**: `200 OK`

**Body para TIPO_A_COSTO_KWH**:
```json
{
  "pdf_url": "https://admincens.cadenaportalgestion.com/PDF/Show?ID=1087010051",
  "tipo_recibo": "TIPO_A_COSTO_KWH",
  "cliente": {
    "documento": "668246",
    "nombre": "Luz Marina Rodriguez Molina",
    "direccion": "Kdx 23 1 b 2",
    "barrio": "Vda Agualasal",
    "ciudad": "El Zulia",
    "estrato": 2,
    "consumo_kwh": 110152.0,
    "total_facturado": 295
  },
  "historico": {
    "tipo": "costo_kwh",
    "unidad": "$/kWh",
    "meses": {
      "JUN": 141,
      "JUL": 129,
      "AGO": 145,
      "SEP": 145,
      "OCT": 143,
      "NOV": 128
    },
    "actual": 128,
    "promedio": 140
  }
}
```

**Body para TIPO_B_CONSUMO_KWH**:
```json
{
  "pdf_url": "https://admincens.cadenaportalgestion.com/PDF/Show?ID=1087010057",
  "tipo_recibo": "TIPO_B_CONSUMO_KWH",
  "cliente": {
    "documento": null,
    "nombre": "Mario Arciniegas Rodriguez",
    "direccion": "Kdx 23 1b 3 apt 2 1T08298 1T08298",
    "barrio": "Vda Agualasal 262.408",
    "ciudad": "El Zulia",
    "estrato": null,
    "consumo_kwh": 44749.0,
    "total_facturado": null
  },
  "historico": {
    "tipo": "consumo_kwh",
    "unidad": "kWh",
    "meses": {},
    "actual": null,
    "promedio": null
  }
}
```

**Body para TIPO_C_SIN_HISTORICO**:
```json
{
  "pdf_url": "https://admincens.cadenaportalgestion.com/PDF/Show?ID=1087010138",
  "tipo_recibo": "TIPO_C_SIN_HISTORICO",
  "cliente": {
    "documento": "1087010138",
    "nombre": "Zuleidy Medina Meneses",
    "direccion": "CLL 8 9-13 B SAN ROQUE - Aguachica - Cesar",
    "barrio": null,
    "ciudad": "El Presente Documento Equivalente Presta Mérito Ejecu(Cid:129)Vo En Virtud Del Ar(Cid:129)Culo 130 De La Ley 142 De 1994 Modificado Por El Ar(Cid:129)Culo 18 De",
    "estrato": 1,
    "consumo_kwh": null,
    "total_facturado": 36
  },
  "historico": {
    "tipo": "sin_historico",
    "consumo_activa_kwh": 42.59,
    "subsidio": "18.650",
    "historico": {
      "valores_historico": [
        "0.0",
        "0.0",
        "0.0",
        "0.0",
        "0.0",
        "0",
        "43"
      ],
      "descripcion": "Valores de consumo previos (si aplica)"
    },
    "observacion": "Recibo sin histórico gráfico disponible"
  }
}
```

**Campos de Respuesta**:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| pdf_url | string | URL del PDF procesado |
| tipo_recibo | string | Tipo de factura clasificada (TIPO_A_COSTO_KWH, TIPO_B_CONSUMO_KWH, TIPO_C_SIN_HISTORICO, DESCONOCIDO) |
| cliente | object | Información del cliente y consumo actual |
| cliente.documento | string/null | Documento de identidad del cliente |
| cliente.nombre | string | Nombre completo del cliente |
| cliente.direccion | string | Dirección del servicio |
| cliente.barrio | string/null | Barrio o vereda |
| cliente.ciudad | string | Ciudad del servicio |
| cliente.estrato | number/null | Estrato socioeconómico |
| cliente.consumo_kwh | number/null | Consumo en kWh del periodo |
| cliente.total_facturado | number/null | Valor total facturado |
| historico | object | Datos históricos según el tipo de recibo |
| historico.tipo | string | Tipo de histórico (costo_kwh, consumo_kwh, sin_historico) |
| historico.unidad | string | Unidad de medida ($/kWh, kWh) |
| historico.meses | object | Objeto con datos mensuales (varía según tipo) |
| historico.actual | number/null | Valor actual del periodo |
| historico.promedio | number/null | Valor promedio |

#### Response - Errores

**400 Bad Request** - URL inválida o no es un PDF:
```json
{
  "detail": "La URL no apunta a un archivo PDF válido"
}
```

**400 Bad Request** - Error al descargar:
```json
{
  "detail": "Error al descargar el PDF: Connection timeout"
}
```

**422 Unprocessable Entity** - Tipo de recibo no soportado:
```json
{
  "detail": "Tipo de recibo no soportado"
}
```

**500 Internal Server Error** - Error al procesar:
```json
{
  "detail": "Error al procesar el PDF: Invalid PDF structure"
}
```

## Ejemplos de Uso

### cURL

```bash
curl -X POST "http://localhost:8002/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://ejemplo.com/factura.pdf"
  }'
```

### Python (requests)

```python
import requests

url = "http://localhost:8002/extract"
payload = {
    "pdf_url": "https://ejemplo.com/factura.pdf"
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    print(f"Tipo de recibo: {data['tipo_recibo']}")
    print(f"Cliente: {data['cliente']['nombre']}")
    print(f"Consumo: {data['cliente']['consumo_kwh']} kWh")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### JavaScript (fetch)

```javascript
const url = "http://localhost:8002/extract";
const payload = {
  pdf_url: "https://ejemplo.com/factura.pdf"
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => {
    console.log('Tipo de recibo:', data.tipo_recibo);
    console.log('Cliente:', data.cliente.nombre);
    console.log('Consumo:', data.cliente.consumo_kwh, 'kWh');
  })
  .catch(error => console.error('Error:', error));
```

### Python (httpx - async)

```python
import httpx
import asyncio

async def extract_invoice():
    url = "http://localhost:8002/extract"
    payload = {
        "pdf_url": "https://ejemplo.com/factura.pdf"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        return response.json()

# Usar
result = asyncio.run(extract_invoice())
print(result)
```

## Tipos de Facturas Soportadas

### TIPO_A_COSTO_KWH
Facturas que contienen información de costo por kWh (identificadas por "$/kWh" en el texto).

**Características**:
- Incluye histórico de costo por kWh
- Contiene datos de consumo mensual
- Formato estructurado con costos detallados

### TIPO_B_CONSUMO_KWH
Facturas con información de consumo y promedio (identificadas por "kWh" y "Promedio" en el texto).

**Características**:
- Histórico de consumo en kWh
- Incluye promedios de consumo
- Datos comparativos mensuales

### TIPO_C_SIN_HISTORICO
Facturas con histórico de consumos (identificadas por "Historico Consumos:" en el texto).

**Características**:
- Lista de consumos históricos
- Formato simplificado
- Datos mensuales básicos

### DESCONOCIDO
Facturas que no coinciden con ninguno de los tipos anteriores.

**Nota**: Las facturas de tipo DESCONOCIDO no pueden ser procesadas y retornarán un error 422.

## Limitaciones y Consideraciones

### Timeouts
- **Descarga de PDF**: 30 segundos máximo
- **Procesamiento**: Sin límite definido (depende del tamaño del PDF)

### Tamaño de Archivo
- No hay límite estricto, pero archivos muy grandes pueden causar timeouts
- Recomendado: PDFs menores a 10 MB

### Seguridad
- La URL debe ser accesible públicamente
- Se valida que el contenido sea un PDF válido
- Los archivos temporales se eliminan automáticamente después del procesamiento

### Rate Limiting
- No implementado actualmente
- Considere implementar rate limiting en producción

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Extracción exitosa |
| 400 | Solicitud inválida (URL incorrecta, no es PDF, error de descarga) |
| 422 | Tipo de factura no soportado |
| 500 | Error interno del servidor |

## Documentación Interactiva

Para explorar la API de forma interactiva:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

Estas interfaces permiten:
- Probar endpoints directamente
- Ver esquemas de datos
- Descargar especificación OpenAPI
- Explorar modelos de respuesta

## Soporte y Contacto

Para reportar problemas o solicitar nuevas funcionalidades, por favor abre un issue en el repositorio del proyecto.
