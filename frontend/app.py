"""Frontend Web FERREMAS (puerto 5000). Sirve las páginas y consume el Backend API."""
import os
from flask import (Flask, render_template, request, session, redirect,
                   url_for, flash, jsonify)
from config import Config
from services import api_client as api

app = Flask(__name__)
app.config.from_object(Config)


# ─────────────────────────── helpers de sesión ───────────────────────────
def get_cart():
    return session.setdefault("cart", {})  # {producto_id: cantidad}


def cart_items_list():
    return [{"producto_id": int(pid), "cantidad": c} for pid, c in get_cart().items()]


def cart_count():
    return sum(get_cart().values())


@app.context_processor
def inject_globals():
    return {"cart_count": cart_count(), "usuario": session.get("user"),
            "desc_porc": app.config["DESCUENTO_PORC"],
            "desc_min": app.config["DESCUENTO_MIN_ITEMS"]}


# ─────────────────────────── catálogo / home ───────────────────────────
@app.route("/")
def index():
    cat = request.args.get("categoria_id", type=int)
    cats, _ = api.categorias()
    prods, err = api.productos(cat)
    return render_template("index.html", categorias=cats or [], productos=prods or [],
                           categoria_sel=cat, error=err)


@app.route("/producto/<int:pid>")
def detalle(pid):
    prod, err = api.producto(pid)
    if not prod:
        flash(err or "Producto no encontrado", "error")
        return redirect(url_for("index"))
    return render_template("detalle.html", p=prod)


# ─────────────────────────── autenticación ───────────────────────────
@app.route("/login", methods=["POST"])
def login():
    data, err = api.login(request.form.get("usuario"), request.form.get("password"))
    if err:
        flash(err, "error")
        return redirect(request.referrer or url_for("index"))
    usuario = data["usuario"]
    session["user"] = usuario
    flash(f"¡Bienvenido, {usuario['nombre']}!", "ok")
    # Los perfiles internos (vendedor, bodeguero, contador, admin) acceden a su
    # panel de gestión; el cliente continúa en la tienda.
    if usuario["rol"] != "cliente":
        return redirect(url_for("panel"))
    return redirect(request.referrer or url_for("index"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Sesión cerrada.", "ok")
    return redirect(url_for("index"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        payload = {k: request.form.get(k) for k in
                   ("nombre", "usuario", "correo", "telefono", "password")}
        payload["suscrito"] = bool(request.form.get("suscrito"))
        data, err = api.registrar(payload)
        if err:
            flash(err, "error")
            return render_template("registro.html", form=payload)
        flash("Cuenta creada. Ya puedes iniciar sesión.", "ok")
        return redirect(url_for("index"))
    return render_template("registro.html", form={})


@app.route("/suscribir", methods=["POST"])
def suscribir():
    correo = request.form.get("correo")
    data, err = api.suscribir(correo)
    flash(err or "¡Felicitaciones! Te suscribiste a las ofertas de FERREMAS.",
          "error" if err else "ok")
    return redirect(request.referrer or url_for("index"))


# ─────────────────────────── carrito ───────────────────────────
@app.route("/carrito/agregar/<int:pid>", methods=["POST"])
def carrito_agregar(pid):
    cant = request.form.get("cantidad", 1, type=int)
    cart = get_cart()
    cart[str(pid)] = cart.get(str(pid), 0) + max(1, cant)
    session.modified = True
    flash("Producto agregado al carrito.", "ok")
    return redirect(request.referrer or url_for("index"))


@app.route("/carrito/eliminar/<int:pid>", methods=["POST"])
def carrito_eliminar(pid):
    get_cart().pop(str(pid), None)
    session.modified = True
    return redirect(url_for("carrito"))


@app.route("/carrito/vaciar", methods=["POST"])
def carrito_vaciar():
    session["cart"] = {}
    return redirect(url_for("carrito"))


@app.route("/carrito")
def carrito():
    items = cart_items_list()
    detalle, total_info = [], {"subtotal": 0, "descuento": 0, "total": 0, "items": 0}
    if items:
        cot, err = api.cotizar(items)
        if cot:
            total_info = cot
        for it in items:
            p, _ = api.producto(it["producto_id"])
            if p:
                detalle.append({"p": p, "cantidad": it["cantidad"],
                                "subtotal": p["precio"] * it["cantidad"]})
    return render_template("carrito.html", detalle=detalle, t=total_info)


# ─────────────────────────── checkout / pago ───────────────────────────
@app.route("/checkout", methods=["POST"])
def checkout():
    if not session.get("user"):
        flash("Debes iniciar sesión para comprar.", "error")
        return redirect(url_for("carrito"))
    items = cart_items_list()
    if not items:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for("carrito"))
    tipo_entrega = request.form.get("tipo_entrega", "retiro")
    medio = request.form.get("medio", "webpay")
    pedido, err = api.crear_pedido({"usuario_id": session["user"]["id"],
                                    "items": items, "tipo_entrega": tipo_entrega})
    if err:
        flash(err, "error")
        return redirect(url_for("carrito"))
    session["pedido_id"] = pedido["id"]

    if medio == "transferencia":
        data, err = api.transferencia({"pedido_id": pedido["id"]})
        return render_template("transferencia.html", datos=(data or {}).get("datos_transferencia", {}),
                               pedido=pedido)
    # Webpay
    ini, err = api.webpay_iniciar({"pedido_id": pedido["id"],
                                   "return_url": url_for("pago_retorno", _external=True)})
    if err:
        flash(err, "error")
        return redirect(url_for("carrito"))
    if ini.get("simulado"):
        # ambiente de prueba/sin red: vamos directo al retorno con el token
        return redirect(url_for("pago_retorno", token=ini["token"], pedido_id=pedido["id"]))
    # ambiente real: redirección a Webpay (token_ws)
    return redirect(f"{ini['url']}?token_ws={ini['token']}")


@app.route("/pago/retorno", methods=["GET", "POST"])
def pago_retorno():
    token = (request.values.get("token_ws") or request.values.get("token")
             or request.values.get("TBK_TOKEN"))
    pedido_id = request.values.get("pedido_id", session.get("pedido_id"), type=int) \
        or session.get("pedido_id")
    # cancelación del usuario en Webpay (TBK_TOKEN) -> error según BPMN
    if request.values.get("TBK_TOKEN") and not request.values.get("token_ws"):
        return render_template("confirmacion.html", ok=False,
                               mensaje="El pago fue cancelado o rechazado.")
    conf, err = api.webpay_confirmar({"pedido_id": pedido_id, "token": token})
    if err or not conf:
        return render_template("confirmacion.html", ok=False,
                               mensaje=err or "No se pudo confirmar el pago.")
    aprobado = conf.get("estado") == "aprobado"
    if aprobado:
        session["cart"] = {}  # vaciar carrito tras pago exitoso (punto del BPMN)
    return render_template("confirmacion.html", ok=aprobado, pedido=conf.get("pedido"),
                           mensaje=("¡Pago aprobado! Tu pedido fue confirmado."
                                    if aprobado else "El pago fue rechazado."))


# ─────────────────────────── perfil ───────────────────────────
@app.route("/perfil")
def perfil():
    if not session.get("user"):
        flash("Inicia sesión para ver tu perfil.", "error")
        return redirect(url_for("index"))
    return render_template("perfil.html")


# ─────────────────────────── panel interno por rol ───────────────────────────
@app.route("/panel")
def panel():
    """Panel de gestión para perfiles internos (vendedor, bodeguero, contador,
    admin). Toda la información proviene del Backend API (productos y divisa);
    el front no accede a la base de datos directamente."""
    user = session.get("user")
    if not user:
        flash("Inicia sesión con un perfil interno para acceder al panel.", "error")
        return redirect(url_for("index"))
    if user["rol"] == "cliente":
        return redirect(url_for("perfil"))

    productos, err = api.productos()
    productos = productos or []
    # Inventario valorizado (precio * stock) para vendedor / contador / admin.
    valor_inventario = sum((p.get("precio", 0) * (p.get("stock") or 0)) for p in productos)
    # Productos con stock bajo (< 20), foco del bodeguero.
    stock_bajo = [p for p in productos if (p.get("stock") or 0) < 20]
    # El contador ve el inventario también convertido a dólares (Banco Central).
    div, _ = api.divisa("USD", valor_inventario)
    return render_template("panel.html", rol=user["rol"], productos=productos,
                           valor_inventario=valor_inventario, stock_bajo=stock_bajo,
                           divisa=div, error=err)


@app.route("/health")
def health():
    return jsonify({"servicio": "FERREMAS Frontend", "estado": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
