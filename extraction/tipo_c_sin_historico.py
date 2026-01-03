import re
from extraction.base import BaseExtractor

class TipoCSinHistoricoExtractor(BaseExtractor):

    def extract(self, text: str) -> dict:
        """
        Extrae información del histórico para tipo C (Sin Histórico Gráfico).
        Este tipo no tiene gráfico de histórico sino una sección de "Historico Consumos:"
        """
        
        historico = {}
        observacion = "Recibo sin histórico gráfico disponible"
        
        # Buscar datos relevantes del consumo
        consumo_activa = None
        subsidio = None
        
        # Buscar consumo activa en la descripción
        consumo_match = re.search(r"CONSUMO\s+ACTIVA[^\d]*([\d\.]+)\s*(?:KWH|kWh)", text)
        if consumo_match:
            consumo_activa = float(consumo_match.group(1))
        
        # Buscar subsidio
        subsidio_match = re.search(r"SUBSIDIO\s*\$?\s*([\d\.]+)", text)
        if subsidio_match:
            subsidio = subsidio_match.group(1)
        
        # Buscar la sección de "Historico Consumos:"
        if "Historico Consumos:" in text:
            idx = text.find("Historico Consumos:")
            section = text[idx:idx+1000]
            
            # Buscar valores numéricos que representen el histórico
            # En este caso, buscar líneas con múltiples números decimales
            lineas = section.split('\n')
            
            for linea in lineas:
                # Buscar línea con múltiples valores decimales (patrón: 0.0 0.0 0.0...)
                if re.search(r'[\d\.]+ [\d\.]+ [\d\.]+', linea):
                    # Extraer todos los números de esta línea
                    numeros = re.findall(r'[\d.]+', linea)
                    if len(numeros) >= 3:
                        # Validar que sean valores razonables (no fechas)
                        try:
                            valores_float = [float(n) for n in numeros]
                            if all(0 <= v < 1000000 for v in valores_float):
                                historico = {
                                    "valores_historico": numeros,
                                    "descripcion": "Valores de consumo previos (si aplica)"
                                }
                                break
                        except:
                            pass
        
        return {
            "tipo": "sin_historico",
            "consumo_activa_kwh": consumo_activa,
            "subsidio": subsidio,
            "historico": historico,
            "observacion": observacion
        }