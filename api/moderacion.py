# api/moderacion.py

# Lista negra de ejemplo (podéis añadir más)
PALABRAS_PROHIBIDAS = ["timo", "estafa", "falso", "insulto"]

def validar_anuncio(titulo, descripcion, precio, categoria):
    """
    Evalúa un anuncio basándose en las reglas de moderación.
    Devuelve un diccionario con el resultado.
    """
    
    # 1. Regla: Validar campos vacíos o nulos
    if not titulo or not descripcion or not categoria:
        return {"valido": False, "motivo": "Faltan campos obligatorios por rellenar."}
    
    # 2. Regla: Validar precios absurdos o negativos
    if precio < 0:
        return {"valido": False, "motivo": "El precio no puede ser negativo."}
    if precio > 10000:
        return {"valido": False, "motivo": "El precio excede el límite permitido para estudiantes."}
    
    # 3. Regla: Filtro de palabras prohibidas (Lista Negra)
    texto_completo = (titulo + " " + descripcion).lower()
    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in texto_completo:
            return {"valido": False, "motivo": f"El anuncio contiene lenguaje no permitido: '{palabra}'."}
            
    # (Aquí irían en el futuro las reglas de revisar el historial del usuario y la imagen)
    
    # Si sobrevive a todos los filtros, es válido
    return {"valido": True, "motivo": "Anuncio apto para publicación."}