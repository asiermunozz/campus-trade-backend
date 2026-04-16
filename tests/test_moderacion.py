# tests/test_moderacion.py
from api.moderacion import validar_anuncio

def test_anuncio_valido():
    # Prueba un anuncio que debería pasar sin problemas
    resultado = validar_anuncio("Libro de Cálculo", "En perfecto estado", 20.0, "Libros")
    assert resultado["valido"] is True

def test_anuncio_con_palabra_prohibida():
    # Prueba que el filtro detecta palabras de la lista negra
    resultado = validar_anuncio("Vendo examen", "Es una estafa garantizada", 50.0, "Otros")
    assert resultado["valido"] is False
    assert "lenguaje no permitido" in resultado["motivo"]

def test_anuncio_precio_negativo():
    # Prueba que no permite precios negativos
    resultado = validar_anuncio("Calculadora", "Casi nueva", -5.0, "Electrónica")
    assert resultado["valido"] is False
    assert "negativo" in resultado["motivo"]