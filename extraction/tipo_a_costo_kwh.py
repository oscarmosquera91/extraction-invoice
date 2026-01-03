import re
from extraction.base import BaseExtractor
from datetime import datetime

class TipoACostoKwhExtractor(BaseExtractor):
    
    # Mapeo de meses en español a número
    MESES_MAP = {
        "ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
        "JUL": 7, "AGO": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12
    }
    
    # Todos los meses posibles en orden
    TODAS_LOS_MESES = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

    def extract(self, text: str) -> dict:
        # Extraer la fecha de la factura para determinar qué meses incluir
        periodo_match = re.search(r'Periodo\s*[:\-]?\s*(\d{1,2})\-(\d{4})', text)
        mes_actual = 12  # Por defecto diciembre
        
        if periodo_match:
            mes_actual = int(periodo_match.group(1))
        
        # Determinar los últimos 6 meses desde la fecha actual
        meses_esperados = self._get_last_6_months(mes_actual)
        
        historico = {}
        actual = None
        promedio = None
        
        # Buscar la línea que contiene los meses esperados
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Verificar si esta línea contiene los meses esperados
            meses_en_linea = [mes for mes in meses_esperados if mes in line]
            
            if len(meses_en_linea) >= 4:  # Si encontramos al menos 4 de los 6 meses esperados
                tiene_actual_promedio = "Actual" in line and "Promedio" in line
                
                # Buscar la línea de valores anterior más adecuada
                # Preferir una línea que tenga exactamente 8 números si existe Actual y Promedio
                valores_line = None
                
                if tiene_actual_promedio:
                    # Buscar hacia atrás hasta 5 líneas
                    for j in range(i - 1, max(0, i - 6), -1):
                        test_line = lines[j].strip()
                        # No debe contener "kWh" y debe tener al menos 8 números
                        if "kWh" not in test_line and test_line and not test_line.startswith('$'):
                            numeros = re.findall(r'\d+', test_line)
                            if len(numeros) >= len(meses_en_linea) + 2:
                                valores_line = test_line
                                break
                
                if not valores_line and i > 0:
                    # Fallback: usar la línea anterior directa
                    valores_line = lines[i - 1].strip()
                
                if valores_line:
                    # Extraer todos los números de la línea de valores
                    numeros = re.findall(r'\d+', valores_line)
                    
                    if tiene_actual_promedio and len(numeros) >= len(meses_en_linea) + 2:
                        # Mapear valores a meses (los primeros 6)
                        for j, mes in enumerate(meses_en_linea):
                            historico[mes] = int(numeros[j])
                        # Actual y Promedio son los últimos dos números
                        actual = int(numeros[-2])
                        promedio = int(numeros[-1])
                    elif len(numeros) >= len(meses_en_linea):
                        # Solo mapear meses
                        for j, mes in enumerate(meses_en_linea):
                            historico[mes] = int(numeros[j])
                    break
        
        # Si no se encuentra el histórico con el método anterior, usar búsqueda individual
        if not historico:
            for mes in meses_esperados:
                match = re.search(rf"{mes}\s+(\d+)", text)
                if match:
                    historico[mes] = int(match.group(1))
        
        # Si aún no se encuentran Actual y Promedio, buscar patrones específicos
        if not actual:
            actual_match = re.search(r"Actual\s+(\d+)", text)
            actual = int(actual_match.group(1)) if actual_match else None
        
        if not promedio:
            promedio_match = re.search(r"Promedio\s+(\d+)", text)
            promedio = int(promedio_match.group(1)) if promedio_match else None

        return {
            "tipo": "costo_kwh",
            "unidad": "$/kWh",
            "meses": historico,
            "actual": actual,
            "promedio": promedio
        }
    
    def _get_last_6_months(self, mes_actual: int) -> list:
        """Retorna los últimos 6 meses antes del mes actual."""
        meses = []
        for i in range(6, 0, -1):
            mes_num = mes_actual - i
            if mes_num <= 0:
                mes_num += 12
            mes_nombre = [m for m, n in self.MESES_MAP.items() if n == mes_num][0]
            meses.append(mes_nombre)
        return meses