# tests/test_integracion.py
from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_obtener_lista_anuncios():
    # Prueba PI-02: Verificar que el GET a la BD funciona
    respuesta = client.get("/api/anuncios")
    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)

def test_registro_usuario_y_duplicado():
    # Prueba PI-01 del documento: Inserción en SQLite y control de errores
    correo_prueba = "test_integracion@campus.uan"
    usuario_datos = {
        "nombre": "Alumno Test",
        "email": correo_prueba,
        "password": "password123"
    }
    
    # 1. Primer registro (Debería funcionar o decir que ya existe de tests anteriores)
    respuesta_1 = client.post("/api/registro", json=usuario_datos)
    
    # 2. Intentamos registrar exactamente el mismo usuario otra vez
    respuesta_2 = client.post("/api/registro", json=usuario_datos)
    
    # Verificamos que el Backend protege la base de datos (HTTP 400 Bad Request)
    assert respuesta_2.status_code == 400
    assert "registrado" in respuesta_2.json()["detail"].lower()
