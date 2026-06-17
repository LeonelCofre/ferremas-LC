# FERREMAS — Solución de Comercio Electrónico (Entrega 2)

Evaluación Final Transversal — **ASY5131 Integración de Plataformas**.
Solución de comercio electrónico para la distribuidora FERREMAS, desarrollada en
**Python + Flask** con **arquitectura por capas** y separación entre el **frontend**
(web) y el **backend** (API), integrando pasarela de pago y conversión de divisas.

## Estructura del repositorio

```
ferremas-LC/
├─ backend/     → API REST (puerto 5001): api · services · repositories · models + SQLite
└─ frontend/    → Web Flask + Jinja (puerto 5000) que consume la API
```

Cada carpeta tiene su propio `README.md` con el detalle de su arquitectura,
endpoints, instalación y pruebas.

## Integraciones (3)

1. **API propia de productos** — catálogo en JSON consumido por el frontend.
2. **WEBPAY (Transbank Webpay Plus)** — pago con tarjeta (credenciales de integración/prueba).
3. **Banco Central de Chile** (`mindicador.cl`) — conversión de divisas en tiempo real.

## Puesta en marcha rápida

Abre **dos terminales** (requiere Python 3.10+).

**1) Backend (API) — puerto 5001**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python scripts/seed.py        # crea y puebla la base de datos
python app.py
```

**2) Frontend (Web) — puerto 5000**
```bash
cd frontend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python app.py
```

Luego abre http://localhost:5000 e ingresa con `cliente / cliente123`.

## Pruebas

```bash
cd backend  && python -m pytest -q     # 14 pruebas
cd frontend && python -m pytest -q     #  5 pruebas
```

## Integrantes

- Leonel Cofré
- [Integrante 2]
- [Integrante 3]
