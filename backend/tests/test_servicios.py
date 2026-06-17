from src.services.currency_service import obtener_tipo_cambio
from src.services import payment_service

def test_divisa_clp():
    assert obtener_tipo_cambio("CLP") == 1.0

def test_divisa_fallback_o_real():
    # Con o sin red, debe devolver un valor numérico para USD
    val = obtener_tipo_cambio("USD")
    assert isinstance(val, float) and val > 0

def test_pago_simulado(app):
    with app.app_context():
        res = payment_service.iniciar_pago("OC-1", "S-1", 10000, "http://x/r")
        assert "token" in res
        conf = payment_service.confirmar_pago(res["token"])
        assert conf["estado"] in ("aprobado", "rechazado")
