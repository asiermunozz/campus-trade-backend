from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from api.moderacion import validar_anuncio
from fastapi.middleware.cors import CORSMiddleware # <-- NUEVO: Importamos CORS

app = FastAPI(
    title="Campus Trade API",
    description="API REST para la gestión de anuncios de estudiantes",
    version="1.0"
)

# <-- NUEVO: Le damos permiso a la web para conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que cualquier web se conecte
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (El resto de tu código de las rutas sigue igual hacia abajo) ...

# Definimos el "molde" de los datos que el usuario nos tiene que enviar
class NuevoAnuncio(BaseModel):
    id_usuario: int
    titulo: str
    descripcion: str
    categoria: str
    precio: float

@app.get("/")
def ruta_principal():
    return {"mensaje": "¡El servidor de Campus Trade está funcionando perfectamente!"}

@app.get("/api/ping")
def ping():
    return {"status": "ok", "proyecto": "Campus Trade"}

# NUEVA RUTA: Recibir y guardar un anuncio
@app.post("/api/anuncios")
def publicar_anuncio(anuncio: NuevoAnuncio):
    # 1. Pasamos el anuncio por nuestro filtro de moderación
    resultado_filtro = validar_anuncio(anuncio.titulo, anuncio.descripcion, anuncio.precio, anuncio.categoria)
    
    if not resultado_filtro["valido"]:
        # Si el filtro lo rechaza (ej. tiene un insulto o precio negativo), devolvemos un Error 400
        raise HTTPException(status_code=400, detail=resultado_filtro["motivo"])
    
    # 2. Si es válido, abrimos la puerta de la base de datos y lo guardamos
    try:
        conexion = sqlite3.connect("campustrade.db")
        cursor = conexion.cursor()
        
        # Insertamos los datos en la tabla 'anuncios'
        cursor.execute('''
            INSERT INTO anuncios (id_usuario, titulo, descripcion, categoria, precio)
            VALUES (?, ?, ?, ?, ?)
        ''', (anuncio.id_usuario, anuncio.titulo, anuncio.descripcion, anuncio.categoria, anuncio.precio))
        
        conexion.commit() # Guardamos los cambios
        nuevo_id = cursor.lastrowid # Guardamos el ID que le ha tocado a este anuncio
        conexion.close()  # Cerramos la puerta
        
        return {"status": "éxito", "mensaje": "Anuncio publicado y guardado en la base de datos", "id_anuncio": nuevo_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")