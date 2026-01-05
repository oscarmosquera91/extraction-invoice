import re

def extract_cliente_y_consumo(text: str) -> dict:
    def find(pattern):
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else None

    lines = text.split('\n')
    
    # Limpiar el texto: remover líneas vacías y caracteres corruptos (cid:XX)
    texto_limpio_lines = []
    for line in lines:
        # Remover caracteres corruptos (cid:...)
        line_limpia = re.sub(r'\(cid:\d+\)', '', line.strip())
        # Remover espacios extras
        line_limpia = ' '.join(line_limpia.split())
        # Agregar si no está vacía
        if line_limpia:
            texto_limpio_lines.append(line_limpia)
    texto_limpio = '\n'.join(texto_limpio_lines)
    
    # Extrae nombre - primero intenta con etiqueta "Nombre"
    nombre = find(r"Nombre\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s]+?)(?:\n|  )")
    
    # Si no lo encuentra, intenta buscar nombre después de "Cliente"
    if not nombre:
        nombre = find(r"Cliente\s+([A-ZÁÉÍÓÚÑ\s]+?)(?:\n|Correo)")
    
    # Si no lo encuentra, busca en línea con "Sujeto pasivo (Contribuyente):"
    # Permite incluir números y caracteres como espacios, ya que algunos nombres incluyen "Union Temporal" etc
    if not nombre:
        nombre = find(r"Sujeto pasivo \(Contribuyente\)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s0-9]+?)(?:\n|Norma|Tel|Acuerdo)")
        # Si encontró nombre, limpiar números al final (después de espacios)
        if nombre:
            nombre = re.sub(r'\s+\d+\s*$', '', nombre).strip()
    
    # Si aún no, intenta buscar iniciales después del documento (formato tipo B: "M Moreno")
    if not nombre:
        nombre = find(r"^([A-Z]\s[A-ZÁÉÍÓÚÑ]+)$")
    
    # Intenta encontrar documento con etiqueta explícita primero
    documento = find(r"(?:Número de )?[Dd]ocumento[:\-]?\s*(\d+)")
    # Si no lo encuentra, busca líneas que contengan solo números (5-8 dígitos)
    if not documento:
        for line in lines:
            line = line.strip()
            if line.isdigit() and 5 <= len(line) <= 8:
                documento = line
                break
    
    # Extrae dirección - busca patrón en línea completa que empieza con Kdx, Cll, Cra, etc
    direccion = find(r"Dirección\s*[:\-]?\s*(.+?)(?:\n|Correo|$)")
    
    # Si no la encuentra, busca en líneas individuales que empiezan con abreviaturas o patrones de dirección
    if not direccion:
        # Buscar líneas que contengan patrones típicos de direcciones
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # Busca direcciones que empiezan con prefijos típicos (Cra, Kdx, Cll, Av, etc) 
            # O que contengan números y palabras (patrón de dirección)
            if re.match(r"^(Kdx|Cll|Cra|Av|Avenida|Carrera|Calle|Noa)\s+", line_clean, re.IGNORECASE):
                # Verifica que no sea la dirección de la empresa (evita líneas con email después)
                has_email_after = False
                if i + 1 < len(lines) and "@" in lines[i + 1]:
                    has_email_after = True
                
                if not has_email_after:
                    direccion = line_clean
                    break
        
        # Si aún no encontró, busca líneas que empiezan en minúscula y tienen números (Noa mnz f casa...)
        if not direccion:
            for i, line in enumerate(lines):
                line_clean = line.strip()
                # Busca líneas que empiezan en minúscula pero contienen patrones de dirección
                if re.match(r"^[a-z]{2,}\s+[a-z]{1,4}\s+", line_clean, re.IGNORECASE):
                    # Verifica que no sea email o URL
                    if "@" not in line_clean and "www" not in line_clean.lower():
                        # Verifica que la siguiente línea sea un barrio (tipografía diferente)
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            # Si la siguiente línea es un nombre de lugar (barrio)
                            if re.match(r"^[A-Z][a-z]+", next_line) and len(next_line) < 40:
                                direccion = line_clean
                                break

    # Para TIPO_C, la dirección contiene la ciudad (ejemplo: "CLL 8 9-13 B SAN ROQUE - Aguachica - Cesar")
    # En este caso, barrio y ciudad deben extraerse de la dirección si es necesario, no de líneas separadas
    es_tipo_c = direccion and " - " in direccion and "Dirección:" in text[:500]
    
    # Extrae barrio - intenta etiqueta explícita primero, PERO solo en el contexto de la dirección encontrada
    barrio = None
    if direccion:
        # Buscar "Barrio:" etiquetado después de la dirección
        direccion_idx = text.lower().find(direccion.lower())
        if direccion_idx >= 0:
            # Buscar en los 500 caracteres después de la dirección
            text_after_direccion = text[direccion_idx:direccion_idx + 500]
            match = re.search(r"Barrio\s*[:\-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+?)(?:\n)", text_after_direccion, re.IGNORECASE)
            if match:
                barrio = match.group(1).strip()
    
    # Si aún no lo encuentra y NO es TIPO_C, busca líneas que comienzan con "Vda"
    if not barrio and not es_tipo_c:
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if re.match(r"^Vda\s+", line_clean, re.IGNORECASE):
                barrio = line_clean
                break
    
    # Si aún, busca la línea después de la dirección (si la dirección está en minúsculas)
    # pero solo si NO es TIPO_C
    if not barrio and direccion and not es_tipo_c:
        for i, line in enumerate(lines):
            if direccion.lower() in line.lower():
                # La siguiente línea probablemente sea el barrio
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # Verifica que sea un nombre de barrio
                    # Y que no sea texto de firma/documento
                    if (next_line and 
                        "Documento" not in next_line and "Presente" not in next_line and
                        "(" not in next_line and len(next_line) < 60 and
                        not next_line.isdigit()):
                        barrio = next_line
                break

    # Extrae ciudad - intenta múltiples estrategias
    # 1. Busca etiqueta explícita "Ciudad:" (puede estar después de barrio o en cualquier parte)
    ciudad = find(r"Ciudad\s*[:\-]?\s*([A-Z\s\w]+?)(?:\n|  )")
    
    # 2. Si no encontró, busca etiqueta "Municipio:" (común en primera página)
    if not ciudad:
        match = re.search(r"Municipio\s*[:\)]\s*([A-Z][A-Za-z\s]+?)(?:\n|$)", text, re.MULTILINE)
        if match:
            ciudad_candidate = match.group(1).strip()
            # Valida que no sea demasiado largo ni contenga palabras no esperadas
            if len(ciudad_candidate) < 80 and "Sujeto" not in ciudad_candidate and "Norma" not in ciudad_candidate:
                ciudad = ciudad_candidate
    
    # 3. Si no la encuentra y NO es TIPO_C, busca líneas que comienzan con "El" o "La"
    if not ciudad and not es_tipo_c:
        for line in lines:
            line_clean = line.strip()
            if re.match(r"^(El|La)\s+", line_clean, re.IGNORECASE):
                ciudad = line_clean
                break
    
    # 4. Si aún no, busca en líneas consecutivas después del barrio (pero solo si NO es TIPO_C)
    if not ciudad and barrio and not es_tipo_c:
        found_barrio = False
        for i, line in enumerate(lines):
            if barrio in line:
                found_barrio = True
                # Busca en las siguientes 3 líneas
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[j].strip()
                    # Verifica que sea un nombre de ciudad (no esté en mayúsculas sostenidas)
                    # Y que sea diferente al barrio y no sea texto de firma/documento
                    if (next_line and next_line != barrio and 
                        not all(c.isupper() or c.isspace() or c.isdigit() for c in next_line) and
                        not re.match(r"^(Residencial|Generica|\d+)", next_line) and
                        "Documento" not in next_line and "Presente" not in next_line and
                        "Equivalente" not in next_line and "(" not in next_line):
                        ciudad = next_line
                        break
                if ciudad:
                    break
    
    # Extrae estrato - busca un dígito después de etiqueta
    estrato = find(r"Estrato\s*[:\-]?\s*(\d)")
    
    # Si no la encuentra, busca el dígito al final de una línea (ej: "Residencial 461 04180590455 2")
    if not estrato:
        for i, line in enumerate(lines):
            if "Residencial" in line and re.search(r"\d{11}\s+(\d)$", line.strip()):
                match = re.search(r"\d{11}\s+(\d)$", line.strip())
                estrato = match.group(1) if match else None
                break
    
    # Si aún no, busca un dígito simple en una línea después de "Residencial"
    if not estrato:
        for i, line in enumerate(lines):
            if "Residencial" in line:
                # Busca la siguiente línea que contiene un dígito simple
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    # Busca un número simple (1-9) al inicio de línea
                    if re.match(r"^(\d)\s+", next_line):
                        match = re.match(r"^(\d)\s+", next_line)
                        estrato = match.group(1) if match else None
                        break
                if estrato:
                    break

    # Extrae consumo - busca diferentes formatos
    consumo = find(r"CONSUMO\s+ACTIVA\s*\$\s*([\d\.,]+)")
    
    # Si no lo encuentra, busca un patrón explícito de kWh (ej: "173 kWh")
    if not consumo:
        consumo = find(r"(\d+\.?\d*)\s*kWh")
    
    # Si no lo encuentra, busca formato alternativo
    if not consumo:
        consumo = find(r"Consumo\s*(?:Activa|ACTIVA)?\s*(?:[:\-]|-)?\s*\$?\s*([\d\.,]+)")
    
    # Si aún no, busca un número de 6 dígitos que pueda ser consumo (ej: "159,204")
    if not consumo:
        # Busca línea con formato de consumo (número con coma o punto como separador)
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # Busca patrones como "159,204" o "159.204"
            if re.match(r"^\d{2,3},\d{3}$", line_clean) or re.match(r"^\d{2,3}\.\d{3}$", line_clean):
                # Verifica que esté antes de información de cliente (tipo B pattern)
                if i + 1 < len(lines) and (
                    re.match(r"^[A-Z]\s[A-Z]", lines[i+1].strip()) or
                    "Tu energía fue subsidiada" in lines[i-1] if i > 0 else False
                ):
                    consumo = line_clean
                    break

    # Extrae total facturado
    total = find(r"Total\s*(?:Facturado|facturado)?[:\-]?\s*\$?\s*([\d\.,]+)")
    
    # Si no lo encuentra, busca en línea que comience con "Total"
    if not total:
        for line in lines:
            match = re.search(r"^Total[:\-]?\s*\$?\s*([\d\.,]+)", line.strip())
            if match:
                total = match.group(1)
                break

    # Si aún no lo encuentra, busca un número con coma/punto cerca del final del documento
    if not total:
        # Busca números con formato de dinero en el documento completo
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # Patrón específico para dinero (ej: "126,684")
            if re.match(r"^\d{2,3},\d{3}$", line_clean):
                # Verifica que esté después de "Por tus servicios pagas"
                found_context = False
                for j in range(max(0, i-5), i):
                    if "Por tus servicios" in lines[j] or "pagas" in lines[j]:
                        found_context = True
                        break
                
                if found_context and (not consumo or line_clean != consumo):
                    total = line_clean
                    break
    
    # Parsear consumo
    consumo_kwh = None
    if consumo:
        try:
            # Remover comas y convertir a float
            consumo_limpio = consumo.replace(",", "")
            consumo_kwh = float(consumo_limpio)
        except:
            consumo_kwh = None
    
    # Parsear total
    total_facturado = None
    if total:
        try:
            # Remover comas (separador de miles) y convertir
            total_limpio = total.replace(",", "")
            total_facturado = int(float(total_limpio))
        except:
            total_facturado = None

    # Extrae periodo facturado (ej: "14/NOV/2025 a 13/DIC/2025")
    periodo_facturado = find(r"[Pp]eriodo\s+facturado\s+(\d{2}/\w+/\d{4}\s+a\s+\d{2}/\w+/\d{4})")
    
    # Si no lo encuentra con "periodo facturado", busca el patrón de fechas directamente
    if not periodo_facturado:
        match = re.search(r"(\d{2}/\w+/\d{4})\s+a\s+(\d{2}/\w+/\d{4})", text, re.IGNORECASE)
        if match:
            periodo_facturado = f"{match.group(1)} a {match.group(2)}"

    # Extrae fecha y hora de generación o fecha de generación
    # Para TIPO_A y TIPO_B: busca "Fecha y hora de generación"
    fecha_hora_generacion = find(r"[Ff]echa\s+y\s+hora\s+de\s+generaci[óo]n\s*[:\-]?\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")
    
    # Si no la encuentra, busca formato alternativo sin "y hora"
    if not fecha_hora_generacion:
        fecha_hora_generacion = find(r"[Ff]echa\s+de\s+[Gg]eneraci[óo]n\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")
    
    # Si aún no, busca directamente el patrón de fecha y hora (YYYY-MM-DD HH:MM:SS)
    if not fecha_hora_generacion:
        match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", text)
        if match:
            fecha_hora_generacion = match.group(1)

    return {
        "documento": documento,
        "nombre": nombre.title() if nombre else None,
        "direccion": direccion,
        "barrio": barrio,
        "ciudad": ciudad.title() if ciudad else None,
        "estrato": int(estrato) if estrato else None,
        "consumo_kwh": consumo_kwh,
        "total_facturado": total_facturado,
        "periodo_facturado": periodo_facturado,
        "fecha_hora_generacion": fecha_hora_generacion,
        "texto_limpio": texto_limpio
    }