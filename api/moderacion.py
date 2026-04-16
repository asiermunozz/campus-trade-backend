import re

# Tu lista negra de palabras y frases prohibidas (limpia de duplicados)
PALABRAS_PROHIBIDAS = [
    "marihuana", "maria", "porros", "hachis", "polen", "cocaína", "coca", "keta", "mdma", "cristal", "speed", "setas", "lsd", "xanax", "trankimazin", "adderall", "ritalin", "esteroides", "anabolizantes", "testosterona", "farmacia", "receta", "antibiótico",
    "porno", "erotico", "sexshop", "consolador", "vibrador", "escort", "masajes", "citas", "sugar daddy", "sugar baby", "onlyfans", "desnuda", "desnudo",
    "pistola", "revolver", "municion", "rifle", "escopeta", "navaja", "puñal", "puño americano", "taser", "spray pimienta", "petardos", "polvora",
    "hago examen", "hago tfg", "hago tfm", "hago deberes", "pinganillo", "chuleta", "examen filtrado",
    "billetes falsos", "dinero negro", "cripto", "inversion rapida",
    "netflix", "spotify", "hbo", "disney+", "dazn", "cuentas", "premium",
    "tabaco", "vaper", "cigarrillo", "alcohol", "vodka", "ron", "ginebra",
    "perro en venta", "gato en venta", "cachorro", "donar organos",
    "vender cuenta", "seguidores instagram",
    "joder", "gilipollas", "cabron", "cabrona", "mierda", "puta", "puto", "puton", "maricon", "mariconazo", "zorra", "zorro", "polla", "coño", "rabo", "nabo", "cojones", "pelotas", "jilipollas", "subnormal", "retrasado", "imbecil", "estupido", "capullo", "mamon", "mamona", "meada", "meado", "cagar", "cagada", "marica", "bollo", "bollera", "travelo", "sudaca", "panchi", "negrata", "moro", "guiri", "asqueroso", "malparido", "pendejo", "culiao", "concha", "chupa", "follar"
]

def validar_anuncio(titulo: str, descripcion: str, precio: float, categoria: str) -> dict:
    # 1. Filtro básico de precio
    if precio < 0:
        return {"valido": False, "motivo": "El precio no puede ser negativo."}
    
    # 2. Unimos el título y la descripción, y lo pasamos todo a minúsculas
    texto_completo = f"{titulo} {descripcion}".lower()

    # 3. Filtro de contenido prohibido
    for palabra in PALABRAS_PROHIBIDAS:
        # El \b asegura que busque la palabra completa, no trozos de otras palabras.
        # re.escape() asegura que si la frase tiene un "+", no rompa el código.
        patron = r'\b' + re.escape(palabra) + r'\b'
        
        if re.search(patron, texto_completo):
            # Si encuentra coincidencia, detiene la publicación instantáneamente
            return {"valido": False, "motivo": f"El anuncio contiene vocabulario no permitido ('{palabra}')."}

    # Si pasa todos los filtros, damos luz verde
    return {"valido": True, "motivo": "Anuncio correcto."}