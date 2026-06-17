# FERREMAS — Frontend Web

Aplicación web (Flask + Jinja) del sistema de comercio electrónico **FERREMAS**.
Consume el [Backend API](../ferremas-backend) y no accede directamente a la base
de datos, respetando la **separación de capas** (front ↔ API ↔ datos).

## Funcionalidades (según el mínimo de desarrollo)

- Página principal con catálogo por categorías, **login (perfil cliente)** y suscripción.
- Catálogo cuyos **precios provienen de la API** (que a su vez integra divisa del Banco Central).
- Registro / **Crear cuenta** y correo de **felicitaciones** al suscribirse.
- Carrito **“Mi compra”** con total y **% de descuento** (compras de más de 4 artículos).
- Al iniciar sesión se muestra el **nombre del cliente** y su **% de descuento** (perfil).
- Pago con **Webpay** (éxito/error que retornan al punto del flujo BPMN) y opción de
  **transferencia** que muestra los datos bancarios.

## Arquitectura

```
app.py                 # rutas / controladores (puerto 5000)
config.py              # configuración (BACKEND_URL, descuento)
services/api_client.py # capa de integración HTTP con el Backend API
templates/             # vistas Jinja (base, index, carrito, registro, perfil, ...)
static/estilo.css      # estilos
tests/                 # pruebas con pytest
```

## Instalación y ejecución

> Requiere el **Backend API** corriendo en `http://localhost:5001`
> (ver `../ferremas-backend`).

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
# opcional: export BACKEND_URL=http://localhost:5001
python app.py                        # web en http://localhost:5000
```

Inicia primero el backend (`python app.py` en `ferremas-backend`, puerto 5001) y
luego el frontend (puerto 5000). Ingresa con el usuario de ejemplo
`cliente / cliente123`.

## Pruebas

```bash
python -m pytest -q
```
