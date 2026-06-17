"""Integración 3 (API propia): catálogo de productos en formato JSON,
consumible interna y externamente. Incluye precio en divisa (Banco Central)."""
from flask import Blueprint, jsonify, request
from ..repositories.repos import ProductoRepository, CategoriaRepository
from ..services.currency_service import convertir

bp = Blueprint("productos", __name__, url_prefix="/api")


@bp.get("/productos")
def listar_productos():
    cat = request.args.get("categoria_id", type=int)
    moneda = request.args.get("moneda")  # opcional: USD/EUR/UF
    productos = ProductoRepository.all(categoria_id=cat)
    data = []
    for p in productos:
        d = p.to_dict()
        if moneda and moneda.upper() != "CLP":
            d["precio_divisa"] = convertir(p.precio, moneda)
            d["moneda"] = moneda.upper()
        data.append(d)
    return jsonify(data)


@bp.get("/productos/<int:pid>")
def detalle_producto(pid):
    p = ProductoRepository.get(pid)
    if not p:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(p.to_dict())


@bp.get("/categorias")
def listar_categorias():
    return jsonify([c.to_dict() for c in CategoriaRepository.all()])
