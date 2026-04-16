import sqlite3

# 1. Nos conectamos (esto crea el archivo 'campustrade.db' automáticamente)
conexion = sqlite3.connect("campustrade.db")
cursor = conexion.cursor()

# 2. Creamos las tablas según vuestro diseño
# TABLA USUARIOS
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    contrasena_hash TEXT NOT NULL,
    rol TEXT DEFAULT 'estudiante',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bloqueado BOOLEAN DEFAULT 0
)
''')

# TABLA ANUNCIOS
cursor.execute('''
CREATE TABLE IF NOT EXISTS anuncios (
    id_anuncio INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL,
    estado TEXT DEFAULT 'activo',
    url_imagen TEXT,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre TIMESTAMP,
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
)
''')

# TABLA FAVORITOS
cursor.execute('''
CREATE TABLE IF NOT EXISTS favoritos (
    id_usuario INTEGER,
    id_anuncio INTEGER,
    fecha_guardado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_anuncio),
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY(id_anuncio) REFERENCES anuncios(id_anuncio) ON DELETE CASCADE
)
''')

# TABLA COMPRAS (Simulación)
cursor.execute('''
CREATE TABLE IF NOT EXISTS compras (
    id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
    id_comprador INTEGER,
    id_vendedor INTEGER,
    id_anuncio INTEGER,
    precio_final REAL NOT NULL,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_pago TEXT DEFAULT 'pendiente',
    FOREIGN KEY(id_comprador) REFERENCES usuarios(id_usuario),
    FOREIGN KEY(id_vendedor) REFERENCES usuarios(id_usuario),
    FOREIGN KEY(id_anuncio) REFERENCES anuncios(id_anuncio)
)
''')

# TABLA MODERACIÓN
cursor.execute('''
CREATE TABLE IF NOT EXISTS moderacion (
    id_accion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_admin INTEGER,
    id_anuncio INTEGER,
    id_usuario_obj INTEGER,
    tipo_accion TEXT NOT NULL,
    motivo TEXT,
    fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(id_admin) REFERENCES usuarios(id_usuario),
    FOREIGN KEY(id_anuncio) REFERENCES anuncios(id_anuncio),
    FOREIGN KEY(id_usuario_obj) REFERENCES usuarios(id_usuario)
)
''')

# 3. Guardamos los cambios y cerramos
conexion.commit()
conexion.close()

print("¡Base de datos 'campustrade.db' creada con éxito!")