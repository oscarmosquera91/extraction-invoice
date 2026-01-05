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
        
        lines = text.split('\n')
        
        # Estrategia 1: Buscar líneas con patrón "MES numero" (líneas individuales)
        for line in lines:
            # Verificar si esta línea contiene mes + número (ej: "JUN 210")
            match = re.match(r'^(JUN|JUL|AGO|SEP|OCT|NOV|ENE|FEB|MAR|ABR|MAY|DIC)\s+(\d+)$', line.strip())
            if match:
                mes = match.group(1)
                valor = int(match.group(2))
                historico[mes] = valor
        
        # Estrategia 2: Si no encontró histórico, buscar meses en líneas separadas
        # (cada mes en su propia línea) y extraer números de antes de ellos
        if not historico:
            # Busca la primera línea con un mes
            meses_lines_start = -1
            for i, line in enumerate(lines):
                if line.strip() in ['JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'DIC']:
                    meses_lines_start = i
                    break
            
            # Si encontró meses en líneas separadas, busca números anteriores
            # Pero solo si hay una línea que diga "Actual" o "Promedio" (que confirma que hay histórico)
            if meses_lines_start > 0:
                # Verifica que haya "Actual" y/o "Promedio" inmediatamente después de los meses
                tiene_actual_promedio = False
                for i in range(meses_lines_start + 6, min(meses_lines_start + 10, len(lines))):
                    if lines[i].strip() in ['Actual', 'Promedio']:
                        tiene_actual_promedio = True
                        break
                
                # Solo extraer si confirma que hay datos de histórico
                if tiene_actual_promedio:
                    todos_numeros = []
                    
                    # Buscar hacia atrás desde donde empiezan los meses
                    for j in range(meses_lines_start - 1, max(0, meses_lines_start - 10), -1):
                        test_line = lines[j].strip()
                        # No debe contener fechas, dinero o texto largo
                        if (test_line and not test_line.startswith('$') and "kWh" not in test_line and 
                            not re.match(r'\d{1,2}/\w{3}/\d{4}', test_line) and  # No fechas
                            not "PROMEDIO" in test_line and  # No la palabra PROMEDIO
                            len(test_line) < 30):
                            # Extraer números
                            numeros = re.findall(r'\b\d+\b', test_line)
                            numeros = [int(n) for n in numeros if 0 < int(n) < 10000]
                            if numeros:
                                todos_numeros.extend(numeros)
                    
                    # Mapear los números encontrados a los meses esperados en orden
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
        
        # Estrategia 3: Si aún no encontró, buscar línea con "Actual" y "Promedio"
        if not historico:
            for i, line in enumerate(lines):
                # Buscar línea con "Actual" y "Promedio"
                if "Actual" in line and "Promedio" in line:
                    # Buscar números en las líneas anteriores
                    todos_numeros = []
                    
                    # Buscar hacia atrás hasta 6 líneas
                    for j in range(i - 1, max(0, i - 7), -1):
                        test_line = lines[j].strip()
                        # No debe contener texto, solo números
                        if test_line and not test_line.startswith('$') and "kWh" not in test_line:
                            # Extraer números
                            numeros = re.findall(r'\d+', test_line)
                            numeros = [int(n) for n in numeros if int(n) < 10000]
                            todos_numeros.extend(numeros)
                    
                    # Mapear los números encontrados a los meses esperados
                    if len(todos_numeros) >= 8:
                        numeros_finales = todos_numeros[-8:]
                        for j, mes in enumerate(meses_esperados):
                            historico[mes] = numeros_finales[j]
                        actual = numeros_finales[-2]
                        promedio = numeros_finales[-1]
                    elif len(todos_numeros) >= 6:
                        numeros_finales = todos_numeros[-6:]
                        for j, mes in enumerate(meses_esperados):
                            historico[mes] = numeros_finales[j]
                    
                    if historico:
                        break
        
        # Buscar Actual y Promedio (si aún no se encontraron)
        if not actual:
            for line in lines:
                actual_match = re.match(r'^Actual\s+(\d+)$', line.strip())
                if actual_match:
                    actual = int(actual_match.group(1))
                    break
        
        if not promedio:
            for line in lines:
                promedio_match = re.match(r'^Promedio\s+(\d+)$', line.strip())
                if promedio_match:
                    promedio = int(promedio_match.group(1))
                    break
        
        # Si aún no encontró Actual y Promedio, buscar con regex flexible
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