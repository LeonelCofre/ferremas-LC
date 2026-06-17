# FERREMAS — Backend API

API REST del sistema de comercio electrónico **FERREMAS** (Evaluación Final
Transversal — ASY5131, Integración de Plataformas). Provee los datos y las
integraciones que consume el frontend.

## Arquitectura por capas

```
app.py                      # punto de entrada (puerto 5001)
config.py                   # configuración
src/
 ├─ __init__.py             # application factory (wiring)
 ├─ extensions.py           # instancia SQLAlchemy
 ├─ api/                    # capa de presentación (controladores / blueprints)
 │   ├─ productos.py        # catálogo (JSON) + precio en divisa
 │   ├─ auth.py             # login, registro de clientes, suscripción
 │   ├─ divisa.py           # conversión de divisas (Banco Central)
 │   └─ pedidos.py          # cotizar, pedidos, pagos (Webpay/transferencia)
 ├─ services/               # capa de lógica de negocio e integraciones
 │   ├─ order_service.py    # totales, descuentos, estados, stock
 │   ├─ payment_service.py  # Integración Webpay/Transbank
 │   ├─ currency_service.py # Integración Banco Central (mindicador.cl)
 │   └─ notification_service.py # correo de suscripción (simulado/log)
 ├─ repositories/           # capa de acceso a datos
 └─ models/                 # capa de dominio (entidades SQLAlchemy)
scripts/seed.py             # carga de datos de ejemplo
tests/                      # pruebas con pytest
```

## Integraciones (3)

1. **API propia de productos** — `GET /api/productos` devuelve el catálogo en JSON
   (consumo interno del frontend y externo de terceros).
2. **WEBPAY (Transbank Webpay Plus)** — pago con tarjeta usando el SDK oficial con
   credenciales de **integración (prueba)**. Degrada a modo simulado si no hay red.
3. **Banco Central de Chile** — conversión de divisas vía `mindicador.cl`
   (USD/EUR/UF). Usa tasa referencial de respaldo si la API no responde.

## Requisitos e instalación

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python scripts/seed.py             # crea y puebla instance/ferremas.db
python app.py                      # API en http://localhost:5001
```

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET  | `/api/health` | Estado del servicio |
| GET  | `/api/categorias` | Lista de categorías |
| GET  | `/api/productos?categoria_id=&moneda=` | Catálogo (JSON), precio opcional en divisa |
| GET  | `/api/productos/<id>` | Detalle de producto |
| POST | `/api/auth/login` | Inicio de sesión |
| POST | `/api/clientes` | Registro de cliente (+ suscripción) |
| POST | `/api/suscripcion` | Suscripción al newsletter (correo de felicitaciones) |
| GET  | `/api/divisa?moneda=USD&monto=` | Tipo de cambio y conversión |
| POST | `/api/cotizar` | Total y descuento del carrito (>4 ítems = 5%) |
| POST | `/api/pedidos` | Crea un pedido |
| GET  | `/api/pedidos/<id>` | Detalle de pedido |
| PUT  | `/api/pedidos/<id>/estado` | Cambia el estado del pedido |
| POST | `/api/pagos/webpay/iniciar` | Inicia pago Webpay |
| POST | `/api/pagos/webpay/confirmar` | Confirma pago Webpay |
| POST | `/api/pagos/transferencia` | Datos para pago por transferencia |

## Usuarios de ejemplo (seed)

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| cliente | cliente123 | cliente |
| admin | admin123 | admin |
| vendedor | vend123 | vendedor |
| bodeguero | bod123 | bodeguero |
| contador | cont123 | contador |

## Pruebas

```bash
python -m pytest -q
```

## Base de datos

SQLite (`instance/ferremas.db`), gestionada con SQLAlchemy. El esquema se crea
automáticamente; `scripts/seed.py` carga categorías, productos y usuarios.
