import pdfplumber
from extraction.classifier import classify_receipt
from extraction.tipo_a_costo_kwh import TipoACostoKwhExtractor
from extraction.tipo_b_consumo_kwh import TipoBConsumoKwhExtractor
from extraction.tipo_c_sin_historico import TipoCSinHistoricoExtractor
from extraction.cliente_y_consumo import extract_cliente_y_consumo


EXTRACTORS = {
    "TIPO_A_COSTO_KWH": TipoACostoKwhExtractor(),
    "TIPO_B_CONSUMO_KWH": TipoBConsumoKwhExtractor(),
    "TIPO_C_SIN_HISTORICO": TipoCSinHistoricoExtractor()
}

def process_pdf(pdf_path: str) -> dict:
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    receipt_type = classify_receipt(pdf_path)

    extractor = EXTRACTORS.get(receipt_type)
    if not extractor:
        return {"error": "Tipo de recibo no soportado"}

    cliente = extract_cliente_y_consumo(text)
    historico = extractor.extract(text)

    return {
        "pdf": pdf_path,
        "tipo_recibo": receipt_type,
        "cliente": cliente,
        "historico": historico
    }