from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json 
from api.moderacion import validar_anuncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Campus Trade API", version="6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def actualizar_base_datos():
    conexion = sqlite3.connect("campustrade.db")
    cursor = conexion.cursor()
    try: cursor.execute("ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT DEFAULT ''")
    except: pass
    try: cursor.execute("ALTER TABLE anuncios ADD COLUMN imagenes TEXT DEFAULT '[]'")
    except: pass
    try: cursor.execute("ALTER TABLE anuncios ADD COLUMN id_comprador INTEGER")
    except: pass
    cursor.execute('''CREATE TABLE IF NOT EXISTS favoritos (id_usuario INTEGER, id_anuncio INTEGER, PRIMARY KEY (id_usuario, id_anuncio))''')
    conexion.commit()
    conexion.close()

class NuevoAnuncio(BaseModel):
    id_usuario: int
    titulo: str
    descripcion: str
    categoria: str
    precio: float
    imagenes: list[str] = []

class EditarAnuncio(BaseModel):
    id_usuario: int 
    titulo: str
    descripcion: str
    categoria: str
    precio: float

class Credenciales(BaseModel):
    email: str
    contrasena: str

class NuevoUsuario(BaseModel):
    nombre: str
    email: str
    contrasena: str
    foto_perfil: str = ""

class FavoritoReq(BaseModel):
    id_usuario: int
    id_anuncio: int

@app.post("/api/anuncios")
def publicar_anuncio(anuncio: NuevoAnuncio):
    resultado_filtro = validar_anuncio(anuncio.titulo, anuncio.descripcion, anuncio.precio, anuncio.categoria)
    if not resultado_filtro["valido"]: raise HTTPException(status_code=400, detail=resultado_filtro["motivo"])
    try:
        conexion = sqlite3.connect("campustrade.db")
        cursor = conexion.cursor()
        imagenes_str = json.dumps(anuncio.imagenes)
        cursor.execute('''INSERT INTO anuncios (id_usuario, titulo, descripcion, categoria, precio, imagenes) VALUES (?, ?, ?, ?, ?, ?)''', 
                       (anuncio.id_usuario, anuncio.titulo, anuncio.descripcion, anuncio.categoria, anuncio.precio, imagenes_str))
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        return {"status": "éxito", "id_anuncio": nuevo_id}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/anuncios")
def obtener_anuncios():
    conexion = sqlite3.connect("campustrade.db")
    conexion.row_factory = sqlite3.Row 
    cursor = conexion.cursor()
    cursor.execute('''
        SELECT a.*, u.nombre as vendedor_nombre, u.email as vendedor_email, u.foto_perfil as vendedor_foto
        FROM anuncios a
        JOIN usuarios u ON a.id_usuario = u.id_usuario
        ORDER BY a.fecha_publicacion DESC
    ''')
    anuncios = []
    for row in cursor.fetchall():
        anuncio_dict = dict(row)
        try: anuncio_dict["imagenes"] = json.loads(anuncio_dict["imagenes"])
        except: anuncio_dict["imagenes"] = []
        anuncios.append(anuncio_dict)
    conexion.close()
    return anuncios

@app.put("/api/anuncios/{id_anuncio}")
def editar_anuncio(id_anuncio: int, datos: EditarAnuncio):
    resultado_filtro = validar_anuncio(datos.titulo, datos.descripcion, datos.precio, datos.categoria)
    if not resultado_filtro["valido"]: raise HTTPException(status_code=400, detail=resultado_filtro["motivo"])
    
    conexion = sqlite3.connect("campustrade.db")
    cursor = conexion.cursor()
    
    es_admin = False
    if datos.id_usuario == 1: 
        es_admin = True
    else:
        cursor.execute("SELECT rol FROM usuarios WHERE id_usuario = ?", (datos.id_usuario,))
        u = cursor.fetchone()
        if u and u[0] == 'moderador': es_admin = True

    if es_admin:
        cursor.execute('''UPDATE anuncios SET titulo = ?, descripcion = ?, precio = ?, categoria = ? WHERE id_anuncio = ?''',
                       (datos.titulo, datos.descripcion, datos.precio, datos.categoria, id_anuncio))
    else:
        cursor.execute('''UPDATE anuncios SET titulo = ?, descripcion = ?, precio = ?, categoria = ? WHERE id_anuncio = ? AND id_usuario = ?''',
                       (datos.titulo, datos.descripcion, datos.precio, datos.categoria, id_anuncio, datos.id_usuario))
    
    conexion.commit()
    cambios = cursor.rowcount
    conexion.close()
    if cambios == 0: raise HTTPException(status_code=403, detail="No tienes permiso para editar este anuncio")
    return {"status": "éxito"}

@app.delete("/api/anuncios/{id_anuncio}")
def borrar_anuncio(id_anuncio: int, id_usuario: int):
    conexion = sqlite3.connect("campustrade.db")
    cursor = conexion.cursor()
    
    es_admin = False
    if id_usuario == 1:
        es_admin = True
    else:
        cursor.execute("SELECT rol FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        u = cursor.fetchone()
        if u and u[0] == 'moderador': es_admin = True

    if es_admin:
        cursor.execute("DELETE FROM anuncios WHERE id_anuncio = ?", (id_anuncio,))
    else:
        cursor.execute("DELETE FROM anuncios WHERE id_anuncio = ? AND id_usuario = ?", (id_anuncio, id_usuario))
        
    conexion.commit()
    cambios = cursor.rowcount
    conexion.close()
    if cambios == 0: raise HTTPException(status_code=403, detail="No tienes permiso para borrar este anuncio")
    return {"status": "éxito"}

# --- RUTA MODIFICADA: COMPRA SEGURA Y CONTROL DE CONCURRENCIA ---
@app.put("/api/comprar/{id_anuncio}")
def comprar_anuncio(id_anuncio: int, id_comprador: int = 0, precio_esperado: float = None):
    conexion = sqlite3.connect("campustrade.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    # 1. Buscamos el anuncio justo antes de comprar
    cursor.execute("SELECT * FROM anuncios WHERE id_anuncio = ?", (id_anuncio,))
    anuncio = cursor.fetchone()
    
    # ¿Lo acaba de borrar el dueño o el admin?
    if not anuncio:
        conexion.close()
        raise HTTPException(status_code=404, detail="Operación cancelada: El anuncio acaba de ser eliminado.")
        
    # ¿Se te acaba de adelantar otro comprador?
    if anuncio["estado"] == "vendido":
        conexion.close()
        raise HTTPException(status_code=400, detail="¡Lo sentimos! Alguien se te acaba de adelantar y lo ha comprado.")
        
    # ¿El dueño ha cambiado el precio mientras rellenabas tu tarjeta?
    if precio_esperado is not None and float(anuncio["precio"]) != float(precio_esperado):
        conexion.close()
        raise HTTPException(status_code=409, detail=f"Operación cancelada: El vendedor acaba de cambiar el precio a {anuncio['precio']}€.")
        
    # Si pasa todas las pruebas, confirmamos la compra
    cursor.execute("UPDATE anuncios SET estado = 'vendido', id_comprador = ? WHERE id_anuncio = ?", (id_comprador, id_anuncio))
    conexion.commit()
    conexion.close()
    
    return {"status": "éxito"}

@app.get("/api/favoritos/{id_usuario}")
def ver_favoritos(id_usuario: int):
    conexion = sqlite3.connect("campustrade.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT id_anuncio FROM favoritos WHERE id_usuario = ?", (id_usuario,))
    favs = [row[0] for row in cursor.fetchall()]
    conexion.close()
    return favs

@app.post("/api/favoritos")
def toggle_favorito(req: FavoritoReq):
    conexion = sqlite3.connect("campustrade.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM favoritos WHERE id_usuario = ? AND id_anuncio = ?", (req.id_usuario, req.id_anuncio))
    if cursor.fetchone():
        cursor.execute("DELETE FROM favoritos WHERE id_usuario = ? AND id_anuncio = ?", (req.id_usuario, req.id_anuncio))
        accion = "eliminado"
    else:
        cursor.execute("INSERT INTO favoritos (id_usuario, id_anuncio) VALUES (?, ?)", (req.id_usuario, req.id_anuncio))
        accion = "añadido"
    conexion.commit()
    conexion.close()
    return {"status": "ok", "accion": accion}

@app.post("/api/login")
def hacer_login(cred: Credenciales):
    conexion = sqlite3.connect("campustrade.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND contrasena_hash = ?", (cred.email, cred.contrasena))
    usuario = cursor.fetchone()
    conexion.close()
    if usuario: return {"status": "ok", "id_usuario": usuario["id_usuario"], "rol": usuario["rol"], "usuario": usuario["nombre"], "foto_perfil": usuario["foto_perfil"]}
    
    if cred.email == "admin@campus.uan" and cred.contrasena == "admin123": 
        return {"status": "ok", "id_usuario": 1, "rol": "moderador", "usuario": "Admin", "foto_perfil": ""}
        
    raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

@app.post("/api/registro")
def registrar_usuario(usuario: NuevoUsuario):
    try:
        conexion = sqlite3.connect("campustrade.db")
        cursor = conexion.cursor()
        cursor.execute('''INSERT INTO usuarios (nombre, email, contrasena_hash, rol, foto_perfil) VALUES (?, ?, ?, 'estudiante', ?)''', (usuario.nombre, usuario.email, usuario.contrasena, usuario.foto_perfil))
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        return {"status": "éxito", "id_usuario": nuevo_id, "usuario": usuario.nombre, "rol": "estudiante", "foto_perfil": usuario.foto_perfil}
    except sqlite3.IntegrityError: raise HTTPException(status_code=400, detail="Este email ya está registrado")
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))