"""Autenticación y registro de clientes."""
from flask import Blueprint, jsonify, request
from ..models import Usuario
from ..repositories.repos import UsuarioRepository
from ..services.notification_service import correo_bienvenida

bp = Blueprint("auth", __name__, url_prefix="/api")


@bp.post("/auth/login")
def login():
    body = request.get_json(force=True, silent=True) or {}
    u = UsuarioRepository.by_usuario(body.get("usuario", ""))
    if not u or not u.check_password(body.get("password", "")):
        return jsonify({"error": "Credenciales inválidas"}), 401
    return jsonify({"ok": True, "usuario": u.to_dict()})


@bp.post("/clientes")
def registrar_cliente():
    body = request.get_json(force=True, silent=True) or {}
    requeridos = ["nombre", "usuario", "correo", "password"]
    if any(not body.get(c) for c in requeridos):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    if UsuarioRepository.by_usuario(body["usuario"]) or UsuarioRepository.by_correo(body["correo"]):
        return jsonify({"error": "Usuario o correo ya registrado"}), 409
    u = Usuario(nombre=body["nombre"], usuario=body["usuario"], correo=body["correo"],
                telefono=body.get("telefono"), rol="cliente",
                suscrito=bool(body.get("suscrito")))
    u.set_password(body["password"])
    UsuarioRepository.add(u)
    if u.suscrito:
        correo_bienvenida(u.correo)
    return jsonify({"ok": True, "usuario": u.to_dict()}), 201


@bp.post("/suscripcion")
def suscripcion():
    body = request.get_json(force=True, silent=True) or {}
    correo = body.get("correo")
    if not correo:
        return jsonify({"error": "Correo requerido"}), 400
    msg = correo_bienvenida(correo)
    return jsonify({"ok": True, "mensaje": msg})
