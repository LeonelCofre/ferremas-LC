"""Endpoint de conversión de divisas (Banco Central / mindicador.cl)."""
from flask import Blueprint, jsonify, request
from ..services.currency_service import obtener_tipo_cambio, convertir

bp = Blueprint("divisa", __name__, url_prefix="/api")


@bp.get("/divisa")
def divisa():
    moneda = request.args.get("moneda", "USD")
    monto = request.args.get("monto", type=float)
    tasa, fuente = obtener_tipo_cambio(moneda, con_fuente=True)
    if tasa is None:
        return jsonify({"error": "Moneda no soportada"}), 400
    out = {"moneda": moneda.upper(), "tasa_clp": tasa, "fuente": fuente}
    if monto is not None:
        out["monto_clp"] = monto
        out["monto_convertido"] = round(monto / tasa, 2)
    return jsonify(out)
