"""Configuración del frontend FERREMAS."""
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ferremas-frontend-dev")
    BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5001")
    DESCUENTO_PORC = float(os.environ.get("DESCUENTO_PORC", "5"))
    DESCUENTO_MIN_ITEMS = int(os.environ.get("DESCUENTO_MIN_ITEMS", "4"))
