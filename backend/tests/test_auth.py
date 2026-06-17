def test_login_ok(client):
    r = client.post("/api/auth/login", json={"usuario": "cliente", "password": "cliente123"})
    assert r.status_code == 200 and r.get_json()["ok"] is True

def test_login_fail(client):
    r = client.post("/api/auth/login", json={"usuario": "cliente", "password": "mala"})
    assert r.status_code == 401

def test_registro_y_suscripcion(client):
    r = client.post("/api/clientes", json={"nombre": "Nuevo", "usuario": "nuevo",
                    "correo": "n@f.cl", "password": "x123", "suscrito": True})
    assert r.status_code == 201 and r.get_json()["usuario"]["rol"] == "cliente"
    # registro duplicado
    r2 = client.post("/api/clientes", json={"nombre": "Nuevo", "usuario": "nuevo",
                     "correo": "n@f.cl", "password": "x123"})
    assert r2.status_code == 409
