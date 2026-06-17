"""Integración 1: conversión de divisas en tiempo real.
Usa mindicador.cl (datos del Banco Central de Chile) para obtener el valor del
dólar/euro/UF en CLP. Si la API no es alcanzable, usa una tasa referencial de
respaldo (marcada como tal) para no interrumpir la operación.
"""
import requests

_ENDPOINTS = {
    "USD": "https://mindicador.cl/api/dolar",
    "EUR": "https://mindicador.cl/api/euro",
    "UF": "https://mindicador.cl/api/uf",
}
# Valores referenciales de respaldo (solo si la API no responde)
_FALLBACK = {"USD": 950.0, "EUR": 1030.0, "UF": 38000.0, "CLP": 1.0}


def obtener_tipo_cambio(moneda="USD", con_fuente=False):
    """Devuelve el valor en CLP de 1 unidad de la moneda. Si con_fuente=True
    devuelve (valor, fuente) donde fuente es 'banco_central' o 'referencial'."""
    moneda = (moneda or "USD").upper()
    if moneda == "CLP":
        return (1.0, "fija") if con_fuente else 1.0
    url = _ENDPOINTS.get(moneda)
    if url:
        try:
            r = requests.get(url, timeout=6)
            r.raise_for_status()
            val = float(r.json()["serie"][0]["valor"])
            return (val, "banco_central") if con_fuente else val
        except Exception as e:  # pragma: no cover - red externa
            print("currency_service (usando respaldo):", e)
    val = _FALLBACK.get(moneda)
    if val is None:
        return (None, None) if con_fuente else None
    return (val, "referencial") if con_fuente else val


def convertir(monto_clp, moneda="USD"):
    tasa = obtener_tipo_cambio(moneda)
    if not tasa:
        return None
    return round(monto_clp / tasa, 2)
