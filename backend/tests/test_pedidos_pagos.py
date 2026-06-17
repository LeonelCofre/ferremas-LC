def test_cotizar_con_descuento(client):
    r = client.post("/api/cotizar", json={"items": [{"producto_id": 1, "cantidad": 5}]})
    d = r.get_json()
    assert d["items"] == 5 and d["descuento"] > 0 and d["total"] == d["subtotal"] - d["descuento"]

def test_cotizar_sin_descuento(client):
    r = client.post("/api/cotizar", json={"items": [{"producto_id": 1, "cantidad": 2}]})
    assert r.get_json()["descuento"] == 0

def test_flujo_pago_webpay(client):
    pid = client.post("/api/pedidos", json={"usuario_id": 1,
          "items": [{"producto_id": 1, "cantidad": 2}]}).get_json()["id"]
    ini = client.post("/api/pagos/webpay/iniciar",
          json={"pedido_id": pid, "return_url": "http://x/r"}).get_json()
    assert "token" in ini
    conf = client.post("/api/pagos/webpay/confirmar",
           json={"pedido_id": pid, "token": ini["token"]}).get_json()
    assert conf["estado"] == "aprobado" and conf["pedido"]["estado"] == "pagado"

def test_transferencia(client):
    pid = client.post("/api/pedidos", json={"usuario_id": 1,
          "items": [{"producto_id": 1, "cantidad": 1}]}).get_json()["id"]
    r = client.post("/api/pagos/transferencia", json={"pedido_id": pid})
    assert r.get_json()["datos_transferencia"]["monto"] == 10000
