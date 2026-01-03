from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from extraction.orchestrator import process_pdf
import requests
import tempfile
import os
from typing import Dict, Any

app = FastAPI(
    title="Invoice Extraction API",
    description="API para extraer información de facturas en PDF",
    version="1.0.0"
)

class PDFRequest(BaseModel):
    pdf_url: HttpUrl

class ExtractionResponse(BaseModel):
    pdf_url: str
    tipo_recibo: str
    cliente: Dict[str, Any]
    historico: Dict[str, Any]

@app.get("/")
async def root():
    return {
        "message": "Invoice Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "POST /extract": "Extrae información de un PDF desde una URL"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/extract", response_model=ExtractionResponse)
async def extract_invoice(request: PDFRequest):
    """
    Extrae información de una factura en PDF desde una URL.

    - **pdf_url**: URL del PDF a procesar

    Retorna la extracción estructurada de la factura incluyendo:
    - tipo_recibo: Clasificación del tipo de factura
    - cliente: Información del cliente y consumo
    - historico: Datos históricos según el tipo de recibo
    """
    temp_file = None

    try:
        # Descargar el PDF desde la URL
        response = requests.get(str(request.pdf_url), timeout=30)
        response.raise_for_status()

        # Verificar que sea un PDF
        content_type = response.headers.get('content-type', '')
        if 'application/pdf' not in content_type.lower():
            # Intentar verificar por contenido
            if not response.content.startswith(b'%PDF'):
                raise HTTPException(
                    status_code=400,
                    detail="La URL no apunta a un archivo PDF válido"
                )

        # Guardar el PDF en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name

        # Procesar el PDF
        result = process_pdf(temp_path)

        # Verificar si hubo error en el procesamiento
        if "error" in result:
            raise HTTPException(
                status_code=422,
                detail=result["error"]
            )

        # Preparar respuesta
        return ExtractionResponse(
            pdf_url=str(request.pdf_url),
            tipo_recibo=result["tipo_recibo"],
            cliente=result["cliente"],
            historico=result["historico"]
        )

    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al descargar el PDF: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el PDF: {str(e)}"
        )
    finally:
        # Limpiar archivo temporal
        if temp_file and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
