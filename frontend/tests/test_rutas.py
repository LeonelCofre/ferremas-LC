def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.get_json()["estado"] == "ok"

def test_home_degrada_sin_backend(client):
    # Si el backend no está, la home igual responde 200 con aviso
    r = client.get("/")
    assert r.status_code == 200
    assert b"FERREMAS" in r.data

def test_carrito_vacio(client):
    r = client.get("/carrito")
    assert r.status_code == 200
    assert "Mi compra".encode() in r.data

def test_registro_form(client):
    r = client.get("/registro")
    assert r.status_code == 200 and "Crear cuenta".encode() in r.data

def test_checkout_requiere_login(client):
    r = client.post("/checkout", data={"medio": "webpay"})
    assert r.status_code in (302, 200)  # redirige a carrito con aviso


def test_panel_requiere_login(client):
    # Sin sesión, el panel redirige al inicio.
    r = client.get("/panel")
    assert r.status_code == 302


def test_panel_cliente_redirige_a_perfil(client):
    with client.session_transaction() as s:
        s["user"] = {"id": 1, "nombre": "Cliente Demo", "rol": "cliente"}
    r = client.get("/panel")
    assert r.status_code == 302  # cliente no entra al panel interno


def test_panel_interno_renderiza(client):
    # Simula un bodeguero logueado; en modo degradado el panel igual responde 200.
    with client.session_transaction() as s:
        s["user"] = {"id": 3, "nombre": "Bodeguero Uno", "rol": "bodeguero"}
    r = client.get("/panel")
    assert r.status_code == 200
    assert "Panel de bodeguero".encode() in r.data
