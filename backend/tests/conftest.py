import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from src import create_app
from src.extensions import db
from src.models import Categoria, Producto, Usuario


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test"
    WEBPAY_COMMERCE_CODE = "597055555532"
    WEBPAY_API_KEY = "test"
    WEBPAY_INTEGRATION = "TEST"
    DESCUENTO_PORC = 5
    DESCUENTO_MIN_ITEMS = 4


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        cat = Categoria(nombre="Herramientas Manuales")
        db.session.add(cat); db.session.commit()
        db.session.add(Producto(codigo="FER-1", marca="Stanley", nombre="Martillo",
                                precio=10000, stock=50, categoria_id=cat.id))
        u = Usuario(nombre="Cliente Demo", usuario="cliente", correo="c@f.cl", rol="cliente")
        u.set_password("cliente123"); db.session.add(u); db.session.commit()
    return app


@pytest.fixture
def client(app):
    return app.test_client()
