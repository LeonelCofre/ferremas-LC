"""Pedidos y pagos (Webpay/transferencia)."""
from flask import Blueprint, jsonify, request, current_app
from ..repositories.repos import PedidoRepository
from ..services import order_service, payment_service

bp = Blueprint("pedidos", __name__, url_prefix="/api")


@bp.post("/cotizar")
def cotizar():
    """Calcula totales y descuento sin crear el pedido (para el carrito)."""
    body = request.get_json(force=True, silent=True) or {}
    items = body.get("items", [])
    _, subtotal, descuento, total, n = order_service.calcular_totales(items)
    return jsonify({"subtotal": subtotal, "descuento": descuento, "total": total, "items": n})


@bp.post("/pedidos")
def crear_pedido():
    body = request.get_json(force=True, silent=True) or {}
    pedido = order_service.crear_pedido(
        usuario_id=body.get("usuario_id"), items=body.get("items", []),
        tipo_entrega=body.get("tipo_entrega", "retiro"))
    return jsonify(pedido.to_dict()), 201


@bp.get("/pedidos/<int:pid>")
def ver_pedido(pid):
    p = PedidoRepository.get(pid)
    if not p:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify(p.to_dict())


@bp.put("/pedidos/<int:pid>/estado")
def cambiar_estado(pid):
    p = PedidoRepository.get(pid)
    if not p:
        return jsonify({"error": "Pedido no encontrado"}), 404
    body = request.get_json(force=True, silent=True) or {}
    p.estado = body.get("estado", p.estado)
    PedidoRepository.save()
    return jsonify(p.to_dict())


@bp.post("/pagos/webpay/iniciar")
def webpay_iniciar():
    body = request.get_json(force=True, silent=True) or {}
    pedido = PedidoRepository.get(body.get("pedido_id"))
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    res = payment_service.iniciar_pago(
        orden_compra=f"OC-{pedido.id}", sesion_id=f"S-{pedido.usuario_id or 0}",
        monto=pedido.total, return_url=body.get("return_url", ""))
    order_service.registrar_pago(pedido, "webpay", "pendiente", token=res["token"])
    return jsonify(res)


@bp.post("/pagos/webpay/confirmar")
def webpay_confirmar():
    body = request.get_json(force=True, silent=True) or {}
    token = body.get("token")
    res = payment_service.confirmar_pago(token)
    pedido = PedidoRepository.get(body.get("pedido_id"))
    if pedido:
        order_service.registrar_pago(pedido, "webpay", res["estado"], token=token)
    return jsonify({"estado": res["estado"], "pedido": pedido.to_dict() if pedido else None})


@bp.post("/pagos/transferencia")
def transferencia():
    """Devuelve los datos para realizar la transferencia (pago manual)."""
    body = request.get_json(force=True, silent=True) or {}
    pedido = PedidoRepository.get(body.get("pedido_id"))
    datos = {
        "banco": "Banco Estado", "tipo_cuenta": "Cuenta Corriente",
        "numero_cuenta": "123456789", "rut": "76.123.456-7",
        "titular": "FERREMAS SpA", "correo": "pagos@ferremas.cl",
        "monto": pedido.total if pedido else None,
    }
    if pedido:
        order_service.registrar_pago(pedido, "transferencia", "pendiente")
    return jsonify({"ok": True, "datos_transferencia": datos})
