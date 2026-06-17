"""Lógica de negocio de pedidos: cálculo de totales y descuentos, creación de
pedidos, reserva de stock y transición de estados."""
from flask import current_app
from ..extensions import db
from ..models import Pedido, DetallePedido, Pago
from ..repositories.repos import ProductoRepository, PedidoRepository


def calcular_totales(items):
    """items: [{producto_id, cantidad}]. Devuelve (lineas, subtotal, descuento, total, n_items)."""
    lineas, subtotal, n_items = [], 0, 0
    for it in items:
        prod = ProductoRepository.get(it["producto_id"])
        if not prod:
            continue
        cant = int(it.get("cantidad", 1))
        n_items += cant
        sub = prod.precio * cant
        subtotal += sub
        lineas.append({"producto": prod, "cantidad": cant, "precio_unitario": prod.precio, "subtotal": sub})
    descuento = 0
    if n_items > current_app.config["DESCUENTO_MIN_ITEMS"]:
        descuento = round(subtotal * current_app.config["DESCUENTO_PORC"] / 100)
    total = subtotal - descuento
    return lineas, subtotal, descuento, total, n_items


def crear_pedido(usuario_id, items, tipo_entrega="retiro"):
    lineas, subtotal, descuento, total, _ = calcular_totales(items)
    pedido = Pedido(usuario_id=usuario_id, estado="recibido",
                    tipo_entrega=tipo_entrega, total=total, descuento=descuento)
    for ln in lineas:
        pedido.detalles.append(DetallePedido(
            producto_id=ln["producto"].id, cantidad=ln["cantidad"],
            precio_unitario=ln["precio_unitario"]))
    PedidoRepository.add(pedido)
    return pedido


def registrar_pago(pedido, medio, estado, token=None):
    pago = pedido.pago or Pago(pedido_id=pedido.id)
    pago.medio = medio
    pago.estado = estado
    pago.token = token
    pago.monto = pedido.total
    if not pedido.pago:
        db.session.add(pago)
    if estado == "aprobado":
        pedido.estado = "pagado"
        for d in pedido.detalles:           # actualización de inventario
            prod = d.producto
            if prod:
                ProductoRepository.descontar_stock(prod, d.cantidad)
    db.session.commit()
    return pago
