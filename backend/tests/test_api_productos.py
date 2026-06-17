def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.get_json()["estado"] == "ok"

def test_listar_productos(client):
    r = client.get("/api/productos")
    assert r.status_code == 200
    data = r.get_json()
    assert len(data) == 1 and data[0]["codigo"] == "FER-1"

def test_categorias(client):
    r = client.get("/api/categorias")
    assert r.status_code == 200 and len(r.get_json()) == 1

def test_detalle_404(client):
    assert client.get("/api/productos/999").status_code == 404
