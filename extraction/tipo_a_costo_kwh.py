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
        periodo_match = re.search(r'Periodo\s+(\d{1,2})\-(\d{4})', text)
        mes_actual = 12  # Por defecto diciembre
        
        if periodo_match:
            mes_actual = int(periodo_match.group(1))
        
        # Determinar los últimos 6 meses desde la fecha actual
        meses_esperados = self._get_last_6_months(mes_actual)
        
        historico = {}
        actual = None
        promedio = None
        
        # Buscar la línea que contiene "Actual" y "Promedio" (línea de leyenda)
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Buscar línea con "Actual" y "Promedio"
            if "Actual" in line and "Promedio" in line:
                # Esta es la línea de leyenda de meses
                # Buscar números en las líneas anteriores (pueden estar en múltiples líneas)
                todos_numeros = []
                
                # Buscar hacia atrás hasta 6 líneas
                for j in range(i - 1, max(0, i - 7), -1):
                    test_line = lines[j].strip()
                    # No debe contener texto, solo números
                    if test_line and not test_line.startswith('$') and "kWh" not in test_line:
                        # Extraer números, pero filtrar IDs muy largos (> 5 dígitos)
                        numeros = re.findall(r'\d+', test_line)
                        numeros = [int(n) for n in numeros if int(n) < 10000]
                        todos_numeros.extend(numeros)
                
                # Mapear los números encontrados a los meses esperados en orden
                # Sin importar si están etiquetados correctamente en el PDF
                if len(todos_numeros) >= 8:
                    # Últimos 8 números (6 meses + actual + promedio)
                    numeros_finales = todos_numeros[-8:]
                    for j, mes in enumerate(meses_esperados):
                        historico[mes] = numeros_finales[j]
                    actual = numeros_finales[-2]
                    promedio = numeros_finales[-1]
                elif len(todos_numeros) >= 6:
                    # Últimos 6 números (solo meses)
                    numeros_finales = todos_numeros[-6:]
                    for j, mes in enumerate(meses_esperados):
                        historico[mes] = numeros_finales[j]
                
                if historico:
                    break
        
        # Si no se encuentra el histórico con el método anterior, usar búsqueda individual por mes
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