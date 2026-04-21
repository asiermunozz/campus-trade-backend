# 🎓 CampusTrade - El Marketplace Universitario

CampusTrade es una plataforma de compraventa exclusiva para estudiantes universitarios. Diseñada como un Producto Mínimo Viable (MVP), permite a la comunidad universitaria anunciar, buscar y adquirir productos y servicios (desde apuntes y libros hasta material de facultad) de forma segura y estructurada.

## 🚀 Características Principales

* **Autenticación y Seguridad:** Sistema de registro y login estricto que solo admite correos institucionales (`@campus.uan`).
* **Roles de Usuario (RBAC):** Cuentas de estudiante estándar y cuentas de Administrador/Moderador con capacidades globales de edición y eliminación.
* **Gestión de Perfil:** Panel de usuario con pestañas dinámicas para gestionar artículos "En Venta", "Favoritos", "Comprados" y "Vendidos".
* **Motor de Búsqueda:** Filtrado en tiempo real por texto y 11 categorías diferentes sin necesidad de recargar la página.
* **Pasarela de Pago Simulada:** Flujo de checkout interactivo con opciones de entrega en el campus y métodos de pago simulados (Tarjeta y Bizum).
* **Protección de Concurrencia (Race Conditions):** El backend verifica cambios de precio o eliminaciones en el último milisegundo antes de procesar una compra.
* **Filtro de Moderación Automático:** Algoritmo basado en expresiones regulares (Regex) que bloquea instantáneamente la publicación de anuncios con contenido inapropiado o ilegal.
* **Gestión de Imágenes:** Almacenamiento de múltiples imágenes por anuncio codificadas en Base64 directamente en la base de datos.

## 🛠️ Tecnologías Utilizadas

**Frontend:**
* HTML5 / CSS3
* Vanilla JavaScript (ES6+)
* [Tailwind CSS](https://tailwindcss.com/) (Estilos)
* [FontAwesome](https://fontawesome.com/) (Iconografía)
* [Toastify JS](https://apvarun.github.io/toastify-js/) (Notificaciones no intrusivas)

**Backend:**
* [Python 3.x](https://www.python.org/)
* [FastAPI](https://fastapi.tiangolo.com/) (API RESTful)
* [SQLite3](https://www.sqlite.org/index.html) (Base de datos relacional)
* Uvicorn (Servidor ASGI)

---

## ⚙️ Instalación y Ejecución Local

Para probar el proyecto en un entorno local, sigue estos pasos:

### 1. Clonar el repositorio
\`\`\`bash
git clone https://github.com/TU_USUARIO/campustrade.git
cd campustrade
\`\`\`

### 2. Iniciar el Servidor Backend (Python)
Es necesario tener Python instalado. Se recomienda usar un entorno virtual.
\`\`\`bash
# Instalar dependencias
pip install fastapi uvicorn pydantic

# Iniciar el servidor
python -m uvicorn api.index:app --reload
\`\`\`
El servidor se ejecutará en `http://127.0.0.1:8000`. La base de datos SQLite (`campustrade.db`) se autoconfigurará al arrancar.

### 3. Iniciar el Frontend
Dado que es una Single Page Application (SPA) en Vanilla JS, no requiere servidor de Node. Simplemente abre el archivo `index.html` en cualquier navegador web moderno.

---

## 🧪 Guía de Pruebas para Evaluación

Para facilitar la corrección del proyecto, sugerimos probar los siguientes flujos:

### Flujo 1: Moderación y Roles (Perfil Administrador)
1. Iniciar sesión con las credenciales maestras:
   * **Email:** `admin@campus.uan`
   * **Contraseña:** `admin123`
2. Navegar por la tienda. Notará que los botones de "Comprar" se sustituyen por "Gestionar".
3. Al entrar en cualquier anuncio, el sistema alertará del "Modo Administrador", permitiendo editar o borrar publicaciones de otros usuarios.

### Flujo 2: Seguridad y Filtro Automático
1. Intentar registrar un usuario con un correo como `prueba@gmail.com`. El sistema lo rechazará (se requiere `@campus.uan`).
2. Una vez registrado correctamente, intentar anunciar un producto utilizando palabras prohibidas en el título o descripción (ej. "Netflix", "Pinganillo", "Arma"). El backend denegará la petición y mostrará el motivo.

### Flujo 3: Experiencia de Compra y Perfil
1. Dar "Me gusta" (Corazón) a un artículo y comprobar que aparece en la pestaña de Favoritos del perfil personal.
2. Iniciar el proceso de compra de un artículo.
3. Observar la validación del formulario de pago (ej. intentar introducir un número de tarjeta de menos de 16 dígitos o un formato de fecha incorrecto).
4. Tras completar la compra, verificar que el artículo desaparece de la tienda principal y se mueve a la pestaña de "Comprados", mostrando además la información de contacto del vendedor.

---

## 🏗️ Arquitectura de la Base de Datos

El sistema utiliza SQLite con las siguientes tablas principales:
* `usuarios`: Almacena credenciales (con hash), datos de contacto y rol (`estudiante` o `moderador`).
* `anuncios`: Relaciona cada artículo con su creador (`id_usuario`). Incluye estado (`activo`, `vendido`) y, en caso de venta, registra el `id_comprador` para mantener el historial.
* `favoritos`: Tabla relacional (Muchos a Muchos) con clave primaria compuesta `(id_usuario, id_anuncio)`.

## 👥 Autores
* [Tu Nombre / Asier] - Lead Developer (Full Stack)
* [Nombre Compañero 1 - Adrián] - QA Testing & Data Entry
* [Nombre Compañero 2 - Gila] - Documentación Técnica
* [Nombre Compañero 3 - Alonso] - Presentación y Diseño
