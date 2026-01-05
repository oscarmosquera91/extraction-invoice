#!/usr/bin/env python3
import sys
import re
import pdfplumber

# Importar la función
sys.path.insert(0, '/Users/oscarmosquera/dev/projects/extraction-invoice')

from extraction.cliente_y_consumo import extract_cliente_y_consumo

# Test con TIPO_C
with pdfplumber.open('data/raw/1087010138.pdf') as pdf:
    text = pdf.pages[0].extract_text()
    
    # Ejecutar la función
    result = extract_cliente_y_consumo(text)
    
    print("TIPO_C (1087010138.pdf):")
    print(f"  direccion: {repr(result.get('direccion'))}")
    print(f"  barrio: {repr(result.get('barrio'))}")
    print(f"  ciudad: {repr(result.get('ciudad'))}")
