"""Pobla la base de datos con categorías, productos y usuarios de ejemplo."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import create_app
from src.extensions import db
from src.models import Categoria, Producto, Usuario

CATS = ["Herramientas Manuales", "Herramientas Eléctricas", "Materiales Básicos",
        "Equipos de Seguridad", "Tornillos y Anclajes", "Equipos de Medición"]

PRODUCTOS = [
    ("FER-1001", "Stanley", "Martillo carpintero 16oz", 8990, 40, "Herramientas Manuales"),
    ("FER-1002", "Bahco", "Juego destornilladores 6 pzas", 12990, 25, "Herramientas Manuales"),
    ("FER-1003", "Stanley", "Llave ajustable 10\"", 9990, 30, "Herramientas Manuales"),
    ("FER-2001", "Bosch", "Taladro percutor GSB 550W", 49990, 15, "Herramientas Eléctricas"),
    ("FER-2002", "Makita", "Sierra circular 1200W", 79990, 10, "Herramientas Eléctricas"),
    ("FER-2003", "Bosch", "Lijadora orbital 220W", 39990, 12, "Herramientas Eléctricas"),
    ("FER-3001", "Melón", "Cemento 25kg", 5990, 200, "Materiales Básicos"),
    ("FER-3002", "Sika", "Adhesivo estructural 300ml", 7990, 80, "Materiales Básicos"),
    ("FER-3003", "Sherwin", "Pintura látex blanco 1gl", 24990, 50, "Materiales Básicos"),
    ("FER-4001", "3M", "Casco de seguridad", 6990, 60, "Equipos de Seguridad"),
    ("FER-4002", "3M", "Guantes anticorte (par)", 4990, 100, "Equipos de Seguridad"),
    ("FER-4003", "3M", "Lentes de seguridad", 2990, 150, "Equipos de Seguridad"),
    ("FER-5001", "Hilti", "Tornillos autoperforantes (100u)", 3990, 120, "Tornillos y Anclajes"),
    ("FER-5002", "Hilti", "Anclajes expansivos (50u)", 8990, 70, "Tornillos y Anclajes"),
    ("FER-6001", "Bosch", "Nivel láser GLL", 59990, 8, "Equipos de Medición"),
    ("FER-6002", "Stanley", "Huincha de medir 5m", 4990, 90, "Equipos de Medición"),
]

USUARIOS = [
    ("Cliente Demo", "cliente", "cliente@ferremas.cl", "cliente123", "cliente", True),
    ("Administradora", "admin", "admin@ferremas.cl", "admin123", "admin", False),
    ("Vendedor Uno", "vendedor", "vendedor@ferremas.cl", "vend123", "vendedor", False),
    ("Bodeguero Uno", "bodeguero", "bodeguero@ferremas.cl", "bod123", "bodeguero", False),
    ("Contador Uno", "contador", "contador@ferremas.cl", "cont123", "contador", False),
]


def run():
    app = create_app()
    with app.app_context():
        db.drop_all(); db.create_all()
        cmap = {}
        for n in CATS:
            c = Categoria(nombre=n); db.session.add(c); cmap[n] = c
        db.session.commit()
        for cod, marca, nom, precio, stock, cat in PRODUCTOS:
            db.session.add(Producto(codigo=cod, marca=marca, nombre=nom, precio=precio,
                                    stock=stock, categoria_id=cmap[cat].id,
                                    imagen=f"{cod}.png"))
        for nombre, usr, correo, pw, rol, sus in USUARIOS:
            u = Usuario(nombre=nombre, usuario=usr, correo=correo, rol=rol, suscrito=sus)
            u.set_password(pw); db.session.add(u)
        db.session.commit()
        print("Seed OK:", Categoria.query.count(), "categorías,",
              Producto.query.count(), "productos,", Usuario.query.count(), "usuarios")


if __name__ == "__main__":
    run()
