"""Integración 2: pasarela de pago WEBPAY (Transbank Webpay Plus).
Usa el SDK oficial con credenciales de integración (ambiente de prueba).
Si el SDK no está disponible o el servicio no es alcanzable (red), opera en
modo simulado para no interrumpir el flujo de compra (degradación controlada).
"""
import uuid
from flask import current_app

try:
    from transbank.webpay.webpay_plus.transaction import Transaction
    from transbank.common.options import WebpayOptions
    from transbank.common.integration_type import IntegrationType
    _SDK = True
except Exception:  # pragma: no cover
    _SDK = False


def _transaction():
    options = WebpayOptions(
        commerce_code=current_app.config["WEBPAY_COMMERCE_CODE"],
        api_key=current_app.config["WEBPAY_API_KEY"],
        integration_type=IntegrationType.TEST,
    )
    return Transaction(options)


def iniciar_pago(orden_compra, sesion_id, monto, return_url):
    """Crea una transacción Webpay. Devuelve dict con token y url.
    Hace fallback a modo simulado si el SDK/red no están disponibles."""
    if _SDK:
        try:
            resp = _transaction().create(orden_compra, sesion_id, int(monto), return_url)
            return {"token": resp["token"], "url": resp["url"], "simulado": False}
        except Exception as e:  # red no disponible / error Transbank
            current_app.logger.warning("Webpay no disponible, modo simulado: %s", e)
    token = "SIM-" + uuid.uuid4().hex[:16]
    return {"token": token, "url": return_url, "simulado": True}


def confirmar_pago(token):
    """Confirma (commit) una transacción Webpay. Devuelve estado normalizado.
    En modo simulado aprueba la transacción para permitir continuar el flujo."""
    if _SDK and not str(token).startswith("SIM-"):
        try:
            resp = _transaction().commit(token)
            aprobado = resp.get("status") == "AUTHORIZED" and resp.get("response_code") == 0
            return {"estado": "aprobado" if aprobado else "rechazado", "detalle": resp}
        except Exception as e:
            current_app.logger.warning("Confirmación Webpay no disponible, simulado: %s", e)
    return {"estado": "aprobado", "detalle": {"status": "AUTHORIZED", "simulado": True}}
