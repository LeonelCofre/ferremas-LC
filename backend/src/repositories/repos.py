"""Capa de acceso a datos (repositorios). Aísla las consultas de la BD."""
from ..extensions import db
from ..models import Categoria, Producto, Usuario, Pedido, DetallePedido, Pago


class ProductoRepository:
    @staticmethod
    def all(categoria_id=None):
        q = Producto.query
        if categoria_id:
            q = q.filter_by(categoria_id=categoria_id)
        return q.order_by(Producto.nombre).all()

    @staticmethod
    def get(pid):
        return Producto.query.get(pid)

    @staticmethod
    def get_by_codigo(codigo):
        return Producto.query.filter_by(codigo=codigo).first()

    @staticmethod
    def descontar_stock(producto, cantidad):
        producto.stock = max(0, producto.stock - cantidad)
        db.session.commit()


class CategoriaRepository:
    @staticmethod
    def all():
        return Categoria.query.order_by(Categoria.nombre).all()


class UsuarioRepository:
    @staticmethod
    def get(uid):
        return Usuario.query.get(uid)

    @staticmethod
    def by_usuario(usuario):
        return Usuario.query.filter_by(usuario=usuario).first()

    @staticmethod
    def by_correo(correo):
        return Usuario.query.filter_by(correo=correo).first()

    @staticmethod
    def add(usuario):
        db.session.add(usuario)
        db.session.commit()
        return usuario


class PedidoRepository:
    @staticmethod
    def get(pid):
        return Pedido.query.get(pid)

    @staticmethod
    def add(pedido):
        db.session.add(pedido)
        db.session.commit()
        return pedido

    @staticmethod
    def save():
        db.session.commit()
