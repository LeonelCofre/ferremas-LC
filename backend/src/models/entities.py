"""Capa de dominio: entidades del modelo de datos de FERREMAS (SQLAlchemy)."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    productos = db.relationship("Producto", back_populates="categoria")

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre}


class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(40), unique=True, nullable=False)
    marca = db.Column(db.String(60))
    nombre = db.Column(db.String(140), nullable=False)
    precio = db.Column(db.Integer, nullable=False)          # CLP
    stock = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(200))
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"))
    categoria = db.relationship("Categoria", back_populates="productos")

    def to_dict(self):
        return {
            "id": self.id, "codigo": self.codigo, "marca": self.marca,
            "nombre": self.nombre, "precio": self.precio, "stock": self.stock,
            "imagen": self.imagen,
            "categoria": self.categoria.nombre if self.categoria else None,
            "categoria_id": self.categoria_id,
        }


class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(30))
    rol = db.Column(db.String(20), default="cliente")  # cliente, admin, vendedor, bodeguero, contador
    password_hash = db.Column(db.String(256), nullable=False)
    suscrito = db.Column(db.Boolean, default=False)
    debe_cambiar_pass = db.Column(db.Boolean, default=False)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    def to_dict(self):
        return {
            "id": self.id, "nombre": self.nombre, "usuario": self.usuario,
            "correo": self.correo, "telefono": self.telefono, "rol": self.rol,
            "suscrito": self.suscrito, "debe_cambiar_pass": self.debe_cambiar_pass,
        }


class Pedido(db.Model):
    __tablename__ = "pedidos"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(30), default="recibido")  # recibido, pagado, en_preparacion, despachado, entregado, cancelado
    tipo_entrega = db.Column(db.String(20), default="retiro")  # retiro / despacho
    total = db.Column(db.Integer, default=0)
    descuento = db.Column(db.Integer, default=0)
    detalles = db.relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")
    pago = db.relationship("Pago", back_populates="pedido", uselist=False)

    def to_dict(self):
        return {
            "id": self.id, "usuario_id": self.usuario_id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "estado": self.estado, "tipo_entrega": self.tipo_entrega,
            "total": self.total, "descuento": self.descuento,
            "detalles": [d.to_dict() for d in self.detalles],
        }


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedidos"
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"))
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"))
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Integer, default=0)
    pedido = db.relationship("Pedido", back_populates="detalles")
    producto = db.relationship("Producto")

    def to_dict(self):
        return {
            "producto_id": self.producto_id,
            "nombre": self.producto.nombre if self.producto else None,
            "cantidad": self.cantidad, "precio_unitario": self.precio_unitario,
            "subtotal": self.cantidad * self.precio_unitario,
        }


class Pago(db.Model):
    __tablename__ = "pagos"
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"))
    medio = db.Column(db.String(20))           # webpay / transferencia
    estado = db.Column(db.String(20), default="pendiente")  # pendiente, aprobado, rechazado
    token = db.Column(db.String(120))
    monto = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    pedido = db.relationship("Pedido", back_populates="pago")

    def to_dict(self):
        return {
            "id": self.id, "pedido_id": self.pedido_id, "medio": self.medio,
            "estado": self.estado, "token": self.token, "monto": self.monto,
            "fecha": self.fecha.isoformat() if self.fecha else None,
        }
