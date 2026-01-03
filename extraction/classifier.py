import pdfplumber

def classify_receipt(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(
            page.extract_text() or "" for page in pdf.pages
        )

    if "$/kWh" in text:
        return "TIPO_A_COSTO_KWH"

    if "kWh" in text and "Promedio" in text:
        return "TIPO_B_CONSUMO_KWH"

    if "Historico Consumos:" in text:
        return "TIPO_C_SIN_HISTORICO"

    return "DESCONOCIDO"