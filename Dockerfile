# Usar imagen base de Python
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para pdfplumber y otras librerías
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY extraction/ ./extraction/
COPY api.py .

# Exponer puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
