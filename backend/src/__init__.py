"""Application factory del backend FERREMAS (capa de presentación / wiring)."""
import os
from flask import Flask, jsonify
from .extensions import db


def create_app(config_object="config.Config"):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_object)
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "instance"), exist_ok=True)

    db.init_app(app)

    # Blueprints (controladores)
    from .api.productos import bp as productos_bp
    from .api.auth import bp as auth_bp
    from .api.divisa import bp as divisa_bp
    from .api.pedidos import bp as pedidos_bp
    for bp in (productos_bp, auth_bp, divisa_bp, pedidos_bp):
        app.register_blueprint(bp)

    @app.get("/")
    @app.get("/api/health")
    def health():
        return jsonify({"servicio": "FERREMAS Backend API", "estado": "ok",
                        "version": "1.0", "integraciones": ["productos", "webpay", "banco_central"]})

    with app.app_context():
        db.create_all()
    return app
