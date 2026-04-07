from fastapi import FastAPI

# Inicializamos la aplicación. Esto generará la documentación automática.
app = FastAPI(
    title="Campus Trade API", 
    description="API REST para la gestión de anuncios de estudiantes",
    version="1.0"
)

# Creamos una "ruta" (endpoint). Cuando alguien entre a la raíz de la web (/), se ejecuta esto.
@app.get("/")
def ruta_principal():
    return {"mensaje": "¡El servidor de Campus Trade está funcionando perfectamente!"}

# Esta ruta la usaremos para comprobar que el servidor responde rápidamente (ping)
@app.get("/api/ping")
def ping():
    return {"status": "ok", "proyecto": "Campus Trade"}