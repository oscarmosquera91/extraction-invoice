import re

def extract_cliente_y_consumo(text: str) -> dict:
    def find(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    lines = text.split('\n')
    
    # Extrae nombre - primero intenta con etiqueta "Nombre"
    nombre = find(r"Nombre\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s]+?)(?:\n|  )")
    
    # Si no lo encuentra, intenta buscar nombre después de "Cliente"
    if not nombre:
        nombre = find(r"Cliente\s+([A-ZÁÉÍÓÚÑ\s]+?)(?:\n|Correo)")
    
    # Si no lo encuentra, busca en línea con "Sujeto pasivo (Contribuyente):"
    if not nombre:
        nombre = find(r"Sujeto pasivo \(Contribuyente\)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s]+?)(?:\n|Norma)")
    
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
    direccion = find(r"Dirección\s*[:\-]?\s*([A-Z0-9\-\s]+?)(?:\n|  |Correo)")
    
    # Si no la encuentra, busca en líneas individuales que empiezan con abreviaturas
    if not direccion:
        for line in lines:
            line_clean = line.strip()
            if re.match(r"^(Kdx|Cll|Cra|Av|Avenida|Carrera|Calle)\s+", line_clean, re.IGNORECASE):
                direccion = line_clean
                break

    # Extrae barrio - intenta etiqueta explícita primero
    barrio = find(r"Barrio\s*[:\-]?\s*([A-Z\s]+?)(?:\n|  )")
    if not barrio:
        # Intenta búsqueda entre etiquetas
        barrio = find(r"Barrio\s*[:\-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+?)(?:\s+Ciudad)")
    
    # Si aún no lo encuentra, busca líneas que comienzan con "Vda"
    if not barrio:
        for line in lines:
            line_clean = line.strip()
            if re.match(r"^Vda\s+", line_clean, re.IGNORECASE):
                barrio = line_clean
                break

    # Extrae ciudad - intenta etiqueta explícita primero
    ciudad = find(r"Ciudad\s*[:\-]?\s*([A-Z\s]+?)(?:\n|  )")
    
    # Si no la encuentra, busca líneas que comienzan con "El" o "La"
    if not ciudad:
        for line in lines:
            line_clean = line.strip()
            if re.match(r"^(El|La)\s+", line_clean, re.IGNORECASE):
                ciudad = line_clean
                break
    
    # Extrae estrato - busca un dígito después de etiqueta
    estrato = find(r"Estrato\s*[:\-]?\s*(\d)")
    
    # Si no la encuentra, busca el dígito al final de una línea (ej: "Residencial 461 04180590455 2")
    if not estrato:
        for line in lines:
            if re.search(r"\d{11}\s+(\d)$", line.strip()):
                match = re.search(r"\d{11}\s+(\d)$", line.strip())
                estrato = match.group(1) if match else None
                break

    # Extrae consumo - busca diferentes formatos
    consumo = find(r"CONSUMO\s+ACTIVA\s*\$\s*([\d\.,]+)")
    
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

    return {
        "documento": documento,
        "nombre": nombre.title() if nombre else None,
        "direccion": direccion,
        "barrio": barrio,
        "ciudad": ciudad.title() if ciudad else None,
        "estrato": int(estrato) if estrato else None,
        "consumo_kwh": consumo_kwh,
        "total_facturado": total_facturado
    }