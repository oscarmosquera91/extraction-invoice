import re
from extraction.base import BaseExtractor
from datetime import datetime

class TipoBConsumoKwhExtractor(BaseExtractor):
    
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
        
        # Buscar la línea que contiene los meses esperados (patrón: "MES \d+")
        lines = text.split('\n')
        
        # Buscar líneas con patrón "MES numero"
        for line in lines:
            # Verificar si esta línea contiene mes + número (ej: "JUN 210")
            match = re.match(r'^(JUN|JUL|AGO|SEP|OCT|NOV|ENE|FEB|MAR|ABR|MAY|DIC)\s+(\d+)$', line.strip())
            if match:
                mes = match.group(1)
                valor = int(match.group(2))
                historico[mes] = valor
        
        # Buscar Actual y Promedio
        for line in lines:
            actual_match = re.match(r'^Actual\s+(\d+)$', line.strip())
            if actual_match:
                actual = int(actual_match.group(1))
            
            promedio_match = re.match(r'^Promedio\s+(\d+)$', line.strip())
            if promedio_match:
                promedio = int(promedio_match.group(1))
        
        # Si no se encuentra Actual y Promedio con el patrón simple, buscar con regex flexible
        if not actual:
            actual_match = re.search(r"Actual\s+(\d+)", text)
            actual = int(actual_match.group(1)) if actual_match else None
        
        if not promedio:
            promedio_match = re.search(r"Promedio\s+(\d+)", text)
            promedio = int(promedio_match.group(1)) if promedio_match else None

        return {
            "tipo": "consumo_kwh",
            "unidad": "kWh",
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