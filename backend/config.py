"""Configuración del backend FERREMAS (capa de configuración)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ferremas-backend-dev")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'ferremas.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Transbank Webpay Plus - credenciales de INTEGRACIÓN (públicas, ambiente de prueba)
    WEBPAY_COMMERCE_CODE = os.environ.get("WEBPAY_COMMERCE_CODE", "597055555532")
    WEBPAY_API_KEY = os.environ.get(
        "WEBPAY_API_KEY",
        "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
    )
    WEBPAY_INTEGRATION = os.environ.get("WEBPAY_INTEGRATION", "TEST")
    # Descuento para compras de más de 4 artículos (caso FERREMAS)
    DESCUENTO_PORC = float(os.environ.get("DESCUENTO_PORC", "5"))
    DESCUENTO_MIN_ITEMS = int(os.environ.get("DESCUENTO_MIN_ITEMS", "4"))
