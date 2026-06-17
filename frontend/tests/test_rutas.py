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
